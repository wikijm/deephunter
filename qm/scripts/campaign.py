from django.shortcuts import get_object_or_404
from django.conf import settings
from time import sleep
from datetime import datetime, timedelta
import requests
import json
import numpy as np
from scipy import stats
from math import isnan
from qm.models import Query, Snapshot, Campaign, Endpoint
import logging

S1_URL = settings.S1_URL
S1_TOKEN = settings.S1_TOKEN
PROXY = settings.PROXY
DB_DATA_RETENTION = settings.DB_DATA_RETENTION
CAMPAIGN_MAX_HOSTS_THRESHOLD = settings.CAMPAIGN_MAX_HOSTS_THRESHOLD
CUSTOM_FIELDS = settings.CUSTOM_FIELDS
ON_MAXHOSTS_REACHED = settings.ON_MAXHOSTS_REACHED

DEBUG = False

# Get an instance of a logger
logger = logging.getLogger(__name__)

def run():
    
    # Cleanup all campaigns older than DB_DATA_RETENTION (90 days by default). Will automatically cascade delete snapshots and endpoints
    # Date of campaign is when the script runs (today) while snapshot date is the day before (detection date)
    Campaign.objects.filter(date_start__lt=datetime.today()-timedelta(days=DB_DATA_RETENTION)).delete()
    # Make sure remaining old Snapshots/Endpoitns are also deleted (when regen stats is used, campaign date is today, while 1st stats are 3 months old)
    Snapshot.objects.filter(date__lt=datetime.today()-timedelta(days=DB_DATA_RETENTION)).delete()

    # Create Campaign
    campaign = Campaign(
        name='daily_cron_{}'.format(datetime.now().strftime("%Y-%m-%d")),
        description='Daily cron job, run all analytics',
        date_start=datetime.now()
        )
    campaign.save()
    
    # Filter query with the "run_daily" flag set
    for query in Query.objects.filter(run_daily=True):
        
        # Run query with filter for the last 24 hours, as the script is run every day
        # hacklist is used instead of array_agg_distinct to get list of storylineid because
        # array_agg_distinct prevents the powerquery from executing without error
        q = "{} | group nb=count(), storylineid=hacklist(src.process.storyline.id)".format(query.query)
        if CUSTOM_FIELDS['c1']:
            q += ", c1=count({})".format(CUSTOM_FIELDS['c1']['filter'])
        if CUSTOM_FIELDS['c2']:
            q += ", c2=count({})".format(CUSTOM_FIELDS['c2']['filter'])
        if CUSTOM_FIELDS['c3']:
            q += ", c3=count({})".format(CUSTOM_FIELDS['c3']['filter'])
        q += " by endpoint.name, site.name"
        todate = datetime.combine(datetime.today(), datetime.min.time())
        body = {
            'fromDate': (todate - timedelta(hours=24)).isoformat(),
            'query': q,
            'toDate': todate.isoformat(),
            'limit': CAMPAIGN_MAX_HOSTS_THRESHOLD
        }
        
        if DEBUG:
            print('*** RUNNING QUERY {}: {}'.format(query.name, query.query))
        
        # store current time (used to update snapshot runtime)
        start_runtime = datetime.now()
        
        r = requests.post('{}/web/api/v2.1/dv/events/pq'.format(S1_URL),
            json=body,
            headers={'Authorization': 'ApiToken:{}'.format(S1_TOKEN)},
            proxies=PROXY)
        
        try:
            query_id = r.json()['data']['queryId']
            status = r.json()['data']['status']
        
            # Ping PowerQuery every second, until it is complete (unless you do that, the PQ will be cancelled)
            while status == 'RUNNING':
                r = requests.get('{}/web/api/v2.1/dv/events/pq-ping'.format(S1_URL),
                    params = {"queryId": query_id},
                    headers={'Authorization': 'ApiToken:{}'.format(S1_TOKEN)},
                    proxies=PROXY)
                    
                status = r.json()['data']['status']
                progress = r.json()['data']['progress']
                
                if DEBUG:
                    print('PROGRESS: {}'.format(progress))
                
                sleep(1)

            # store current time (used to update snapshot runtime)
            end_runtime = datetime.now()

            # Create snapshot. Necessary to have the object to link the detected assets.
            # Stats will be updated later to the snapshot
            # the date of the snapshot is the day before the campaign (detection date)
            snapshot = Snapshot(
                campaign=campaign,
                query=query,
                date=datetime.now()-timedelta(days=1),
                runtime = (end_runtime-start_runtime).total_seconds()
                )
            snapshot.save()
                    
            if DEBUG:
                print('***DATA (JSON): {}'.format(r.json()))
            
            if len(r.json()['data']['data']) != 0:
                data = r.json()['data']['data']
                
                hits_endpoints = len(data)
                hits_count = 0
                hits_c1 = 0
                hits_c2 = 0
                hits_c3 = 0
                
                for i in data:
                    
                    # The storylineid field has 255 chars max
                    if len(i[3]) < 255:
                        storylineid = i[3][1:][:-1]
                    else:
                        storylineid = ''
                    
                    # update detected endpoints and link it with current snapshot
                    endpoint = Endpoint(
                        hostname = i[0],
                        site = i[1],
                        snapshot = snapshot,
                        storylineid = storylineid
                    )
                    endpoint.save()
                    # count nb of hits
                    hits_count += int(float(i[2]))
                    # count nb of 1st custom field (C1)
                    if CUSTOM_FIELDS['c1']:
                        if int(float(i[4])) > 0:
                            hits_c1 += 1
                    # count nb of 2nd custom field (C2)
                    if CUSTOM_FIELDS['c2']:
                        if int(float(i[5])) > 0:
                            hits_c2 += 1
                    # count nb of 3rd custom field (C3)
                    if CUSTOM_FIELDS['c3']:
                        if int(float(i[6])) > 0:
                            hits_c3 += 1
                # if hits_count too big, set to -1
                #if hits_count > 2000000000:
                #    hits_count = -1
            else:
                if DEBUG:
                    print('NO DATA!')
                hits_count = 0
                hits_endpoints = 0
                hits_c1 = 0
                hits_c2 = 0
                hits_c3 = 0
            
            if DEBUG:
                print("*** HITS_COUNT = {}".format(hits_count))
                print("*** HITS_ENDPOINTS = {}".format(hits_endpoints))
                print("*** HITS_C1 = {}".format(hits_c1))
                print("*** HITS_C2 = {}".format(hits_c2))
                print("*** HITS_C3 = {}".format(hits_c3))
            
            # Now that stats have been collected, snapshot is updated.
            snapshot.hits_count = hits_count
            snapshot.hits_endpoints = hits_endpoints
            snapshot.hits_c1 = hits_c1
            snapshot.hits_c2 = hits_c2
            snapshot.hits_c3 = hits_c3
            snapshot.save()
            if DEBUG:
                print("Snapshot created")
            
            # When the max_hosts threshold is reached (by default 1000)
            if hits_count >= CAMPAIGN_MAX_HOSTS_THRESHOLD:
                # Update the maxhost counter if reached
                query.maxhosts_count += 1
                # if threshold is reached
                if query.maxhosts_count >= ON_MAXHOSTS_REACHED['THRESHOLD']:
                    # If DISABLE_RUN_DAILY is set, we disable the run_daily flag for the query
                    if ON_MAXHOSTS_REACHED['DISABLE_RUN_DAILY']:
                        query.run_daily = False
                    # If DELETE_STATS is set, we delete all stats for the query
                    if ON_MAXHOSTS_REACHED['DELETE_STATS']:
                        Snapshot.objects.filter(query=query).delete()
                # we update the query (counter updated, and flags updated)
                query.save()
                if DEBUG:
                    print("Max hosts threshold reached. Counter updated")            
            
            # Anomaly detection for hits_count (compute zscore against all snapshots available in DB)
            if DEBUG:
                print("Anomaly detection for hits_count")
            snapshots = Snapshot.objects.filter(query = query)
            a = np.array([c.hits_count for c in snapshots])
            z = stats.zscore(a)
            if DEBUG:
                for i,v in enumerate(a):
                    print( '{},{}'.format(v,z[i]) )
            zscore_count = z[-1]
            if isnan(zscore_count):
                zscore_count = -9999
            if zscore_count > query.anomaly_threshold_count:
                anomaly_alert_count = True
            else:
                anomaly_alert_count = False
            
            # Anomaly detection for hits_endpoints (compute zscore against all snapshots available in DB)
            if DEBUG:
                print("Anomaly detection for hits_endpoints")
            a = np.array([c.hits_endpoints for c in snapshots])
            z = stats.zscore(a)
            if DEBUG:
                for i,v in enumerate(a):
                    print( '{},{}'.format(v,z[i]) )
            zscore_endpoints = z[-1]
            if isnan(zscore_endpoints):
                zscore_endpoints = -9999
            if zscore_endpoints > query.anomaly_threshold_endpoints:
                anomaly_alert_endpoints = True
            else:
                anomaly_alert_endpoints = False
            
            # Final update of snapshots with stats for the last snapshot (just created above)
            if DEBUG:
                print("***Final update for new snapshot")
                print("snapshot.zscore_count = {}".format(zscore_count))
                print("snapshot.zscore_endpoints = {}".format(zscore_endpoints))
                print("snapshot.anomaly_alert_count = {}".format(anomaly_alert_count))
                print("snapshot.anomaly_alert_endpoints = {}".format(anomaly_alert_endpoints))
            
            snapshot.zscore_count = zscore_count
            snapshot.zscore_endpoints = zscore_endpoints
            snapshot.anomaly_alert_count = anomaly_alert_count
            snapshot.anomaly_alert_endpoints = anomaly_alert_endpoints
            snapshot.save()
            
        except:
            print("***ERROR. See campaigns.log for more information")
            logger.error("[ ERROR ]")
            logger.error('RUNNING QUERY {}: {}'.format(query.name, query.query))
            logger.error(r.json())
            logger.error("================================")
        
        if DEBUG:
            print("================================")

    # Close Campaign
    campaign.date_end = datetime.now()
    campaign.nb_queries = Query.objects.filter(run_daily=True).count()
    campaign.save()
