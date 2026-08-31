import os
import requests
import json
import yaml
import time

def get_file_list():
    try:
        start = time.time()
        headers = {}
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = 'Bearer ' + token
        rawdata = json.loads(requests.get('https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1', headers=headers, timeout=60).text)
        data = rawdata['tree']
        dirlist = []
        count = 0
        for x in data:
            dirlist.append(data[count]['path'])
            count = count +1
        end = time.time()
        return dirlist, count
    except Exception:
        return None
        #print("Failed to fetch proxies from changfengoss/pub")

def get_proxies(date, file):
    baseurl = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'
    working = yaml.safe_load(requests.get(url=baseurl+date+'/'+file,).text)
    data_out = []
    for x in working['proxies']:
        data_out.append(x)
    return data_out
