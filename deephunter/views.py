from authlib.integrations.django_client import OAuth
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from authlib.integrations.django_client import token_update

oauth = OAuth()
oauth.register(
    name='pingid',
)

@receiver(token_update)
def on_token_update(sender, name, token, refresh_token=None, access_token=None, **kwargs):
    if refresh_token:
        item = OAuth2Token.find(name=name, refresh_token=refresh_token)
    elif access_token:
        item = OAuth2Token.find(name=name, access_token=access_token)
    else:
        return
    
    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']
    item.save()

def sso(request):
    # build a full authorize callback uri
    redirect_uri = request.build_absolute_uri('/authorize')
    # Redirect user to Auth website (PingID for instance)
    #  were login form may be shown, and eventually MFA
    return oauth.pingid.authorize_redirect(request, redirect_uri)  

def user_logout(request):
    logout(request)
    return redirect('/')

def authorize(request):
    token = oauth.pingid.authorize_access_token(request)
    
    if 'groups' in token['userinfo']:
        # Groups can be string or list. This makes sure that whatever type, we make it a list
        if type(token['userinfo']['groups']) == str:
            usergroups = [token['userinfo']['groups']]
        else:
            usergroups = token['userinfo']['groups']
        
        refgroup_viewer = "SG_{}_usr".format(settings.AUTHLIB_OAUTH_CLIENTS['pingid']['client_id'])
        refgroup_manager = "SG_{}_pr".format(settings.AUTHLIB_OAUTH_CLIENTS['pingid']['client_id'])

        # if user is member of 1 of the reference groups, access granted
        if refgroup_viewer in usergroups or refgroup_manager in usergroups:
            # we search if the user is already in the local DB
            user = User.objects.filter(username=token['userinfo']['sub'])

            if 'sub' in token['userinfo']:
                username = token['userinfo']['sub']
            else:
                username = ''
            
            if 'firstName' in token['userinfo']:
                first_name = token['userinfo']['firstName']
            else:
                first_name = ''
            
            if 'lastName' in token['userinfo']:
                last_name = token['userinfo']['lastName']
            else:
                last_name = ''
            
            if 'email' in token['userinfo']:
                email = token['userinfo']['email']
            else:
                email = ''
            
            if user:
                # If user already exists, profile updated
                user = get_object_or_404(User, username=username)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.is_active = True
                user.is_staff = True
                user.save()
            else:
                # User is granted access but does not exist yet
                user = User(
                    username = username,
                    first_name = first_name,
                    last_name = last_name,
                    email = email,
                    is_active = True,
                    is_staff = True
                )
                user.save()
                        
            # Add user to relevant group (viewer or manager)
            if refgroup_manager in usergroups:
                group = get_object_or_404(Group, name='manager')
            else:
                group = get_object_or_404(Group, name='viewer')            
            # apply group to user
            group.user_set.add(user)
            
            # login user
            login(request, user)
        return HttpResponseRedirect('/')    
    else:
        return HttpResponseRedirect('/')
