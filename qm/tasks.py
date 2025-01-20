from celery import shared_task
from django.shortcuts import get_object_or_404
from django.conf import settings
from time import sleep
from datetime import datetime, timedelta
import requests
import json
import numpy as np
from scipy import stats
from math import isnan
from qm.models import Query, Campaign, Snapshot, Endpoint, CeleryStatus
import logging

S1_URL = settings.S1_URL
S1_TOKEN = settings.S1_TOKEN
PROXY = settings.PROXY
DB_DATA_RETENTION = settings.DB_DATA_RETENTION
CAMPAIGN_MAX_HOSTS_THRESHOLD = settings.CAMPAIGN_MAX_HOSTS_THRESHOLD
CUSTOM_FIELDS = settings.CUSTOM_FIELDS

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task()
def regenerate_stats(query_id):
    query = get_object_or_404(Query, pk=query_id)
    
    # Create Campaign
    # Date of campaign is when the script runs (today) while snapshot date is the day before (detection date)
    campaign = Campaign(
        name='regenerate_stats_{}_{}'.format(query.name, datetime.now().strftime("%Y-%m-%d-%H-%M")),
        description='Regenerate stats for {}'.format(query.name),
        date_start=datetime.now(),
        nb_queries=1
        )
    campaign.save()

    # Create task in CeleryStatus object
    celery_status = CeleryStatus(
        query=query,
        progress=0
        )
    celery_status.save()
    
    # Delete all snapshots for this query
    # (related Endpoint object will automatically cascade delete)
    Snapshot.objects.filter(query=query).delete()
    
    # Rebuild campaigns for last DB_DATA_RETENTION (90 days by default) for the query
    for days in reversed(range(DB_DATA_RETENTION)):
        
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
        todate = datetime.combine((datetime.now() - timedelta(days=days)), datetime.min.time())
        body = {
            'fromDate': (todate - timedelta(days=1)).isoformat(),
            'query': q,
            'toDate': todate.isoformat(),
            'limit': CAMPAIGN_MAX_HOSTS_THRESHOLD
        }
        
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
                
                sleep(1)

            # store current time (used to update snapshot runtime)
            end_runtime = datetime.now()
            
            # Create snapshot. Necessary to have the object to link the detected assets.
            # Stats will be updated later to the snaptshot
            # the date of the snapshot is the day before the campaign (detection date)
            snapshot = Snapshot(
                campaign=campaign,
                query=query,
                date=todate - timedelta(days=1),
                runtime = (end_runtime-start_runtime).total_seconds()
                )
            snapshot.save()
                    
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
                hits_count = 0
                hits_endpoints = 0
                hits_c1 = 0
                hits_c2 = 0
                hits_c3 = 0
            
            # Now that stats have been collected, snapshot is updated.
            snapshot.hits_count = hits_count
            snapshot.hits_endpoints = hits_endpoints
            snapshot.hits_c1 = hits_c1
            snapshot.hits_c2 = hits_c2
            snapshot.hits_c3 = hits_c3
            snapshot.save()
            
            # Anomaly detection for hits_count (compute zscore against all snapshots available in DB)
            snapshots = Snapshot.objects.filter(query = query)
            a = np.array([c.hits_count for c in snapshots])
            z = stats.zscore(a)
            zscore_count = z[-1]
            if isnan(zscore_count):
                zscore_count = -9999
            if zscore_count > query.anomaly_threshold_count:
                anomaly_alert_count = True
            else:
                anomaly_alert_count = False
            
            # Anomaly detection for hits_endpoints (compute zscore against all snapshots available in DB)
            a = np.array([c.hits_endpoints for c in snapshots])
            z = stats.zscore(a)
            zscore_endpoints = z[-1]
            if isnan(zscore_endpoints):
                zscore_endpoints = -9999
            if zscore_endpoints > query.anomaly_threshold_endpoints:
                anomaly_alert_endpoints = True
            else:
                anomaly_alert_endpoints = False
            
            # Final update of snpashots with stats for the last snapshot (just created above)            
            snapshot.zscore_count = zscore_count
            snapshot.zscore_endpoints = zscore_endpoints
            snapshot.anomaly_alert_count = anomaly_alert_count
            snapshot.anomaly_alert_endpoints = anomaly_alert_endpoints
            snapshot.save()
            
        except:
            logger.error("[ ERROR ]")
            logger.error('RUNNING QUERY {}: {}'.format(query.name, query.query))
            logger.error(r.json())
            logger.error("================================")

        # Update Celery task progress
        celery_status.progress = (DB_DATA_RETENTION-days)*100/DB_DATA_RETENTION
        celery_status.save()

    # Close Campaign
    campaign.date_end = datetime.now()
    campaign.save()

    # Delete Celery task
    celery_status.delete()
