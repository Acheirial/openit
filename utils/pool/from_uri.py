import base64
import urllib.parse
import yaml
import requests

HEADERS = {'Accept': '*/*', 'User-Agent': 'Clash'}


def _b64(data):
    pad = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + pad).decode('utf-8', 'replace')


def parse_ss(url):
    body = url[5:].split('#', 1)[0]
    if '@' not in body:
        decoded = _b64(body)
        if '@' not in decoded:
            return None
        method_pass, hostport = decoded.rsplit('@', 1)
    else:
        userinfo, hostport = body.rsplit('@', 1)
        if ':' not in userinfo:
            method_pass = _b64(userinfo)
        else:
            method_pass = userinfo
    if ':' not in method_pass or ':' not in hostport:
        return None
    method, password = method_pass.split(':', 1)
    host, port = hostport.rsplit(':', 1)
    host = urllib.parse.unquote(host)
    return {
        'name': 'ss',
        'type': 'ss',
        'server': host.strip('[]'),
        'port': int(port.split('?')[0]),
        'cipher': method,
        'password': urllib.parse.unquote(password),
        'udp': True,
    }


def parse_trojan(url):
    body = url[9:].split('#', 1)[0]
    if '@' not in body:
        return None
    password, rest = body.split('@', 1)
    hostport, _, query = rest.partition('?')
    host, port = hostport.rsplit(':', 1)
    params = urllib.parse.parse_qs(query)
    node = {
        'name': 'trojan',
        'type': 'trojan',
        'server': urllib.parse.unquote(host).strip('[]'),
        'port': int(port),
        'password': urllib.parse.unquote(password),
        'udp': True,
        'skip-cert-verify': True,
    }
    sni = params.get('sni') or params.get('peer')
    if sni:
        node['sni'] = sni[0]
    if (params.get('type') or [''])[0] == 'ws':
        node['network'] = 'ws'
        node['ws-opts'] = {
            'path': (params.get('path') or ['/'])[0],
            'headers': {'Host': (params.get('host') or params.get('sni') or [node['server']])[0]},
        }
    return node


def parse_ssr(url):
    decoded = _b64(url[6:].split('#', 1)[0])
    main, _, query = decoded.partition('/?')
    parts = main.split(':')
    if len(parts) < 6:
        return None
    host, port, protocol, method, obfs, password_b64 = parts[0], parts[1], parts[2], parts[3], parts[4], ':'.join(parts[5:])
    params = urllib.parse.parse_qs(query)
    return {
        'name': 'ssr',
        'type': 'ssr',
        'server': host,
        'port': int(port),
        'protocol': protocol,
        'cipher': method,
        'obfs': obfs,
        'password': _b64(password_b64),
        'protocol-param': _b64(params['protoparam'][0]) if 'protoparam' in params else '',
        'obfs-param': _b64(params['obfsparam'][0]) if 'obfsparam' in params else '',
        'udp': True,
    }


PARSERS = {
    'ss': parse_ss,
    'trojan': parse_trojan,
    'ssr': parse_ssr,
}


def convert(text):
    proxies = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '://' not in line:
            continue
        if 'xxxxxxxxxx' in line or '@localhost:' in line:
            continue
        scheme = line.split('://', 1)[0].lower()
        parser = PARSERS.get(scheme)
        if not parser:
            continue
        try:
            node = parser(line)
        except Exception:
            continue
        if not node:
            continue
        node['name'] = f"{node['type']}-{len(proxies)+1}"
        proxies.append(node)
    return proxies


def fetch(url):
    return requests.get(url, timeout=120, headers=HEADERS).text


if __name__ == '__main__':
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else 'https://etoneya.baby/'
    out = sys.argv[2] if len(sys.argv) > 2 else 'etoneya.yaml'
    text = fetch(src) if src.startswith('http') else open(src, encoding='utf-8').read()
    proxies = convert(text)
    with open(out, 'w', encoding='utf-8') as writer:
        yaml.dump({'proxies': proxies}, writer, sort_keys=False, allow_unicode=True)
    print(f'Wrote {len(proxies)} proxies to {out}')
