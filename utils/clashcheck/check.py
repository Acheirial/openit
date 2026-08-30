import requests
import json

def check(alive, proxy, apiurl, sema, timeout, testurl, secret=''):
    try:
        headers = {'Authorization': 'Bearer ' + secret} if secret else {}
        r = requests.get(url=apiurl + '/proxies/' + str(proxy['name']) + '/delay?url='+testurl+'&timeout=' + str(timeout), headers=headers, timeout=10)
        response = json.loads(r.text)
        delay = response.get('delay')
        if delay and delay > 0:
            node = dict(proxy)
            node['_delay'] = int(delay)
            alive.append(node)
    except:
        pass
    sema.release()
