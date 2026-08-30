import os
import yaml
import flag
import socket
import maxminddb
import platform
import psutil
import requests
from tqdm import tqdm
from pathlib import Path


PROTOCOL_RANK = {
    'hysteria2': 0,
    'hysteria': 1,
    'anytls': 2,
    'tuic': 3,
    'vless': 4,
    'trojan': 5,
    'wireguard': 6,
    'ss': 7,
    'vmess': 8,
    'ssr': 9,
    'snell': 10,
}


def _server_key(proxy):
    server = str(proxy.get('server') or '')
    try:
        return socket.gethostbyname(server)
    except Exception:
        return server


def _bare_http_socks(proxy):
    return proxy.get('type') in ('http', 'socks5', 'socks')


def pick_alive(alive, max_delay=1500):
    best = {}
    dropped_bare = 0
    dropped_slow = 0
    dropped_dup = 0
    kept = []
    for proxy in alive:
        if not isinstance(proxy, dict):
            continue
        if _bare_http_socks(proxy):
            dropped_bare += 1
            continue
        delay = proxy.get('_delay')
        try:
            delay = int(delay)
        except (TypeError, ValueError):
            delay = max_delay
        if delay <= 0 or delay > max_delay:
            dropped_slow += 1
            continue
        rank = PROTOCOL_RANK.get(proxy.get('type'), 99)
        key = _server_key(proxy)
        current = best.get(key)
        score = (rank, delay)
        if current is None or score < current[0]:
            if current is not None:
                dropped_dup += 1
            best[key] = (score, proxy)
        else:
            dropped_dup += 1
    for _, proxy in sorted(best.values(), key=lambda item: item[0]):
        node = dict(proxy)
        node.pop('_delay', None)
        kept.append(node)
    print(
        'Quality filter: kept %d, drop bare http/socks %d, slow %d, same-ip %d'
        % (len(kept), dropped_bare, dropped_slow, dropped_dup)
    )
    return kept


def push(list, outfile):
    country_count = {}
    count = 1
    clash = {'proxies': [], 'proxy-groups': [
            {'name': 'automatic', 'type': 'url-test', 'proxies': [], 'url': 'https://www.google.com/favicon.ico',
             'interval': 300}, {'name': '🌐 Proxy', 'type': 'select', 'proxies': ['automatic']}],
             'rules': ['MATCH,🌐 Proxy']}
    with maxminddb.open_database('Country.mmdb') as countrify:
        for i in tqdm(range(int(len(list))), desc="Parse"):
            x = list[i]
            try:
                try:
                    ip = str(socket.gethostbyname(x["server"]))
                except:
                    ip = str(x["server"])
                try:
                    country = str(countrify.get(ip)['country']['iso_code'])
                except:
                    country = 'UN'
                flagcountry = country
                try:
                    country_count[country] = country_count[country] + 1
                    x['name'] = str(flag.flag(flagcountry)) + " " + country + " " + str(count)
                except:
                    country_count[country] = 1
                    x['name'] = str(flag.flag(flagcountry)) + " " + country + " " + str(count)
                clash['proxies'].append(x)
                clash['proxy-groups'][0]['proxies'].append(x['name'])
                clash['proxy-groups'][1]['proxies'].append(x['name'])
                count = count + 1
            except:
                continue

    with open(outfile, 'w') as writer:
        yaml.dump(clash, writer, sort_keys=False)



def checkenv():
    operating_system = str(platform.system() + '/' +  platform.machine() + ' with ' + platform.node())
    print('Try to run Clash-compatible core on '+ operating_system)
    if operating_system.startswith('Darwin'):
        if 'arm64' in operating_system:
            clashname='./clash-darwin-arm64'
        elif 'x86_64' in operating_system:
            clashname='./clash-darwin-amd64'
        else:
            print('System is supported(Darwin) but Architecture is not supported.')
            exit(1)
    elif operating_system.startswith('Linux'):
        if 'x86_64' in operating_system:
            clashname='./clash-linux-amd64'
        elif 'aarch64' in operating_system:
            clashname='./clash-linux-arm64'
        else:
            print('System is supported(Linux) but Architecture is not supported.')
            exit(1)
    elif operating_system.startswith('Windows'):
        if 'AMD64' in operating_system:
            clashname='clash-windows-amd64.exe'
        else:
            print('System is supported(Windows) but Architecture is not supported.')
            exit(1)
    else:
        print('System is not supported.')
        exit(1)
    if not os.path.exists(clashname):
        print(clashname + ' missing. Run ./fetch-mihomo.sh first.')
        exit(1)

    return clashname, operating_system


def checkuse(clashname, operating_system):
    pids = psutil.process_iter()
    for pid in pids:
        if(pid.name() == clashname):
            if operating_system.startswith('Darwin'):
                os.kill(pid.pid,9)
            elif operating_system.startswith('Linux'):
                os.kill(pid.pid,9)
            elif operating_system.startswith('Windows'):
                os.popen('taskkill.exe /pid:'+str(pid.pid))
            else:
                print(clashname, str(pid.pid) + " ← kill to continue")
                exit(1)


def filter(config):
    list = config.get("proxies") or []
    ss_supported_ciphers = ['aes-128-gcm', 'aes-192-gcm', 'aes-256-gcm', 'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb', 'aes-128-ctr', 'aes-192-ctr', 'aes-256-ctr', 'rc4-md5', 'chacha20', 'chacha20-ietf', 'xchacha20', 'chacha20-ietf-poly1305', 'xchacha20-ietf-poly1305']
    ssr_supported_obfs = ['plain', 'http_simple', 'http_post', 'random_head', 'tls1.2_ticket_fastauth', 'tls1.2_ticket_auth']
    ssr_supported_protocol = ['origin', 'auth_sha1_v4', 'auth_aes128_md5', 'auth_aes128_sha1', 'auth_chain_a', 'auth_chain_b']
    vmess_supported_ciphers = ['auto', 'aes-128-gcm', 'chacha20-poly1305', 'none']
    iplist = {}
    passlist = []
    count = 1
    clash = {'proxies': [], 'proxy-groups': [
            {'name': 'automatic', 'type': 'url-test', 'proxies': [], 'url': 'https://www.google.com/favicon.ico',
             'interval': 300}, {'name': '🌐 Proxy', 'type': 'select', 'proxies': ['automatic']}],
             'rules': ['MATCH,🌐 Proxy']}
    with maxminddb.open_database('Country.mmdb') as countrify:
        for i in tqdm(range(int(len(list))), desc="Parse"):
            try:
                x = list[i]
                authentication = ''
                x['port'] = int(x['port'])
                try:
                    ip = str(socket.gethostbyname(x["server"]))
                except:
                    ip = x['server']
                try:
                    country = str(countrify.get(ip)['country']['iso_code'])
                except:
                    country = 'UN'
                if x['type'] == 'ss':
                    try:
                        if x['cipher'] not in ss_supported_ciphers:
                            continue
                        x['name'] = str(flag.flag(country)) + ' ' + str(country) + ' ' + str(count) + ' ' + 'SSS'
                        authentication = 'password'
                    except:
                        continue
                elif x['type'] == 'ssr':
                    try:
                        if x['cipher'] not in ss_supported_ciphers:
                            continue
                        if x['obfs'] not in ssr_supported_obfs:
                            continue
                        if x['protocol'] not in ssr_supported_protocol:
                            continue
                        authentication = 'password'
                        x['name'] = str(flag.flag(country)) + ' ' + str(country) + ' ' + str(count) + ' ' + 'SSR'
                    except:
                        continue
                elif x['type'] == 'vmess':
                    try:
                        if 'udp' in x:
                            if x['udp'] not in [False, True]:
                                continue
                        if 'tls' in x:
                            if x['tls'] not in [False, True]:
                                continue
                        if 'skip-cert-verify' in x:
                            if x['skip-cert-verify'] not in [False, True]:
                                continue
                        if x['cipher'] not in vmess_supported_ciphers:
                            continue
                        x['name'] = str(flag.flag(country)) + ' ' + str(country) + ' ' + str(count) + ' ' + 'VMS'
                        authentication = 'uuid'
                    except:
                        continue
                elif x['type'] == 'trojan':
                    try:
                        if 'udp' in x:
                            if x['udp'] not in [False, True]:
                                continue
                        if 'skip-cert-verify' in x:
                            if x['skip-cert-verify'] not in [False, True]:
                                continue
                        x['name'] = str(flag.flag(country)) + ' ' + str(country) + ' ' + str(count) + ' ' + 'TJN'
                        authentication = 'password'
                    except:
                        continue
                elif x['type'] == 'snell':
                    try:
                        if 'udp' in x:
                            if x['udp'] not in [False, True]:
                                continue
                        if 'skip-cert-verify' in x:
                            if x['skip-cert-verify'] not in [False, True]:
                                continue
                        x['name'] = str(flag.flag(country)) + ' ' + str(country) + ' ' + str(count) + ' ' + 'SNL'
                        authentication = 'psk'
                    except:
                        continue
                elif x['type'] in ('http', 'socks5', 'socks'):
                    continue
                elif x['type'] in ('vless', 'hysteria', 'hysteria2', 'anytls', 'tuic', 'wireguard'):
                    tags = {
                        'vless': 'VLS',
                        'hysteria': 'HY1',
                        'hysteria2': 'HY2',
                        'anytls': 'ATL',
                        'tuic': 'TIC',
                        'wireguard': 'WGD',
                    }
                    x['name'] = str(flag.flag(country)) + ' ' + str(country) + ' ' + str(count) + ' ' + tags[x['type']]
                    authentication = 'uuid' if x['type'] == 'vless' else 'password'
                else:
                    continue

                if authentication and ip in iplist and x['port'] in iplist[ip]:
                    if x.get(authentication) in passlist:
                        continue
                    else:
                        passlist.append(x[authentication])
                else:
                    try:
                        iplist[ip].append(x['port'])
                    except:
                        iplist[ip] = []
                        iplist[ip].append(x['port'])

                clash['proxies'].append(x)
                clash['proxy-groups'][0]['proxies'].append(x['name'])
                clash['proxy-groups'][1]['proxies'].append(x['name'])
                count = count + 1

            except:
                #print('shitwentwrong' + str(x))
                continue

    return clash
