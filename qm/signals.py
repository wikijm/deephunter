from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Query
import requests
import json

# Params for requests API calls
S1_URL = settings.S1_URL
S1_TOKEN = settings.S1_TOKEN
PROXY = settings.PROXY

@receiver(pre_save, sender=Query)
def check_initial_value(sender, instance, **kwargs):
    # Check if the instance is being updated (i.e., it's not a new object)
    if instance.pk:
        # Retrieve the current value of the field from the database
        original_instance = Query.objects.get(pk=instance.pk)
        
        # Get the value of the STAR rule flag before threat hunting analytic is saved
        # and compare with updated value
        old_value = original_instance.star_rule
        new_value = instance.star_rule
        
        # If STAR rule flag was initially set, and has been removed with the update
        # we need to delete the STAR rule in S1
        if old_value and not new_value:
            body = {
                "filter": {
                    "name__contains": instance.name
                }
            }
            r = requests.delete(f'{S1_URL}/web/api/v2.1/cloud-detection/rules',
                json=body,
                headers={'Authorization': f'ApiToken:{S1_TOKEN}'},
                proxies=PROXY
                )

# This handler is triggered after an object is saved (created or updated)
@receiver(post_save, sender=Query)
def post_save_handler(sender, instance, created, **kwargs):
    # only apply if STAR_RULE flag set
    if instance.star_rule:

        # filter "tenant=true" is to apply rule to scope "global"
        body_new = {
            "data": {
                "queryLang": "2.0",
                "severity": "High",
                "description": "Rule Sync from DeepHunter",
                "s1ql": instance.query,
                "name": instance.name,
                "queryType": "events",
                "expirationMode": "Permanent",
                "status": "Active"
            },
            "filter": {
                "tenant": "true"
            }
        }
                
        # For newly created analytic
        if created:
            r = requests.post(f'{S1_URL}/web/api/v2.1/cloud-detection/rules',
                json=body_new,
                headers={'Authorization': f'ApiToken:{S1_TOKEN}'},
                proxies=PROXY
                )
                
        # When analytic is updated
        else:
            # check if STAR rule already exists (STAR rule flag was previously set)
            r = requests.get(f'{S1_URL}/web/api/v2.1/cloud-detection/rules?name__contains={instance.name}',
                headers={'Authorization': f'ApiToken:{S1_TOKEN}'},
                proxies=PROXY
                )
            if r.json()['data']:
                # if it exists, update it, but preserve severity and expiration              
                rule_id = r.json()['data'][0]['id']
                severity = r.json()['data'][0]['severity']
                expirationMode = r.json()['data'][0]['expirationMode']

                if expirationMode == 'Permanent':
                    body_update = {
                        "data": {
                            "queryLang": "2.0",
                            "severity": severity,
                            "s1ql": instance.query,
                            "name": instance.name,
                            "queryType": "events",
                            "expirationMode": "Permanent",
                            "status": "Active"
                        },
                        "filter": {
                            "tenant": "true"
                        }
                    }
                else:
                    body_update = {
                        "data": {
                            "queryLang": "2.0",
                            "severity": severity,
                            "s1ql": instance.query,
                            "name": instance.name,
                            "queryType": "events",
                            "expirationMode": "Temporary",
                            "expiration": r.json()['data'][0]['expiration'],
                            "status": "Active"
                        },
                        "filter": {
                            "tenant": "true"
                        }
                    }
                    
                r = requests.put(f'{S1_URL}/web/api/v2.1/cloud-detection/rules/{rule_id}',
                    json=body_update,
                    headers={'Authorization': f'ApiToken:{S1_TOKEN}'},
                    proxies=PROXY
                    )
            else:
                # if it does not exist (STAR rule flag was not set), create it
                r = requests.post(f'{S1_URL}/web/api/v2.1/cloud-detection/rules',
                    json=body_new,
                    headers={'Authorization': f'ApiToken:{S1_TOKEN}'},
                    proxies=PROXY
                    )

# This handler is triggered after an object is deleted
@receiver(post_delete, sender=Query)
def post_delete_handler(sender, instance, **kwargs):
    # only apply if STAR_RULE flag set
    if instance.star_rule:
        body = {
            "filter": {
                "name__contains": instance.name
            }
        }
        r = requests.delete(f'{S1_URL}/web/api/v2.1/cloud-detection/rules',
            json=body,
            headers={'Authorization': f'ApiToken:{S1_TOKEN}'},
            proxies=PROXY
            )
