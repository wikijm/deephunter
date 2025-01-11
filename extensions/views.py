from django.conf import settings
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, JsonResponse
from bs4 import BeautifulSoup
import requests
import re
import vt

PROXY = settings.PROXY
VT_API_KEY = settings.VT_API_KEY

def is_valid_md5(hash: str) -> bool:
    pattern = r'^[a-z-A-Z0-9]{32}$'
    return re.match(pattern, hash) is not None
    
def is_valid_sha1(hash: str) -> bool:
    pattern = r'^[a-z-A-Z0-9]{40}$'
    return re.match(pattern, hash) is not None
    
def is_valid_sha256(hash: str) -> bool:
    pattern = r'^[a-z-A-Z0-9]{64}$'
    return re.match(pattern, hash) is not None

def is_valid_ip(ip: str) -> bool:
    pattern = r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'
    return re.match(pattern, ip) is not None

@login_required
def loldriverhashchecker(request):

    hashes = ''
    found_hashes = ''
    
    if request.method == "POST":
        lol_hashes = []
        found_hashes = []
        hashes = request.POST['hashes']
        
        response = requests.get(
            'https://www.loldrivers.io/',
            proxies=PROXY
            )
        soup = BeautifulSoup(response.text, "lxml")
        #Created a list of lol driver SHA256 hashes
        for link in soup.find_all("a", href=True):
            if len(link.text) == 64:
                lol_hashes.append(str(link.text))
        
        # search if any matching hash
        for hash in hashes.split('\r\n'):
            hash = hash.strip()
            if is_valid_sha256(hash):
                if hash in lol_hashes:
                    found_hashes.append(hash)
    
    context = {
        'hashes': hashes,
        'output': found_hashes
    }
    return render(request, 'loldriverhashchecker.html', context)

@login_required
def whois(request):

    ip = ''
    whois = ''

    if request.method == "POST":
        ip = request.POST['ip']
        if is_valid_ip(ip):
            response = requests.get(
                'https://www.whois.com/whois/{}/'.format(ip),
                proxies=PROXY
                )
            soup = BeautifulSoup(response.text, features="lxml")
            elements = soup.find_all('pre', attrs={'id': 'registryData'})
            whois = elements[0].text
        else:
            whois = 'Invalid IP format'
    else:
        whois = 'Provide an IP address in the form above'
        
    context = {
        'ip': ip,
        'output': whois
    }
    return render(request, 'whois.html', context)

@login_required
def vthashchecker(request):

    hashes = ''
    output = ''
    
    if request.method == "POST":
        output = []
        hashes = request.POST['hashes']

        client = vt.Client(
            VT_API_KEY,
            proxy=PROXY['https']
        )

        for hash in hashes.split('\r\n'):
            hash = hash.strip()
            if is_valid_md5(hash) or is_valid_sha1(hash) or is_valid_sha256(hash):        
                try:
                    file = client.get_object("/files/{}".format(hash))
                    output.append({
                        'hash': hash,
                        'foundinvt': 'Y',
                        'malicious': file.last_analysis_stats['malicious'],
                        'suspicious': file.last_analysis_stats['suspicious']
                    })        
                except:
                    output.append({
                        'hash': hash,
                        'foundinvt': 'N',
                        'malicious': '',
                        'suspicious': ''
                    })        
                        
    context = {
        'hashes': hashes,
        'output': output
    }
    return render(request, 'vthashchecker.html', context)
