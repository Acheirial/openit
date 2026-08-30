import json
import urllib.parse
import yaml
from yaml.loader import SafeLoader


def _q(value):
    return urllib.parse.quote(str(value), safe='')


def _host(node):
    server = str(node.get('server') or '')
    port = node.get('port')
    if ':' in server and not server.startswith('['):
        server = f'[{server}]'
    return f'{server}:{port}'


def _remark(node):
    name = node.get('name')
    return f'#{_q(name)}' if name else ''


def encode_ss(node):
    userinfo = f"{node.get('cipher')}:{node.get('password')}"
    b64 = __import__('base64').urlsafe_b64encode(userinfo.encode()).decode().rstrip('=')
    return f"ss://{b64}@{_host(node)}{_remark(node)}"


def encode_trojan(node):
    query = {}
    if node.get('sni'):
        query['sni'] = node['sni']
    if node.get('network') == 'ws':
        query['type'] = 'ws'
        opts = node.get('ws-opts') or {}
        query['path'] = opts.get('path') or '/'
        headers = opts.get('headers') or {}
        query['host'] = headers.get('Host') or headers.get('host') or node.get('sni') or node.get('server')
    q = urllib.parse.urlencode({k: v for k, v in query.items() if v})
    return f"trojan://{_q(node.get('password'))}@{_host(node)}{'?'+q if q else ''}{_remark(node)}"


def encode_vmess(node):
    payload = {
        'v': '2',
        'ps': node.get('name') or '',
        'add': node.get('server'),
        'port': str(node.get('port')),
        'id': node.get('uuid'),
        'aid': str(node.get('alterId') or 0),
        'net': node.get('network') or 'tcp',
        'type': 'none',
        'tls': 'tls' if node.get('tls') else '',
        'sni': node.get('servername') or node.get('sni') or '',
    }
    opts = node.get('ws-opts') or {}
    if payload['net'] == 'ws':
        payload['path'] = opts.get('path') or '/'
        headers = opts.get('headers') or {}
        payload['host'] = headers.get('Host') or headers.get('host') or ''
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    b64 = __import__('base64').b64encode(raw.encode()).decode()
    return f'vmess://{b64}'


def encode_vless(node):
    network = node.get('network') or 'tcp'
    if network in ('splithttp',):
        network = 'xhttp'
    query = {'type': network, 'encryption': 'none'}
    if node.get('tls') or node.get('reality-opts'):
        query['security'] = 'reality' if node.get('reality-opts') else 'tls'
    sni = node.get('servername') or node.get('sni')
    if sni:
        query['sni'] = sni
    if node.get('flow'):
        query['flow'] = node['flow']
    if network == 'ws':
        opts = node.get('ws-opts') or {}
        query['path'] = opts.get('path') or '/'
        headers = opts.get('headers') or {}
        query['host'] = headers.get('Host') or headers.get('host') or sni or node.get('server')
    elif network == 'grpc':
        opts = node.get('grpc-opts') or {}
        query['serviceName'] = opts.get('grpc-service-name') or ''
    elif network == 'xhttp':
        opts = node.get('xhttp-opts') or {}
        query['path'] = opts.get('path') or '/'
        query['mode'] = opts.get('mode') or 'auto'
        query['host'] = opts.get('host') or sni or node.get('server')
    reality = node.get('reality-opts') or {}
    if reality.get('public-key'):
        query['pbk'] = reality['public-key']
        query['sid'] = reality.get('short-id') or ''
    q = urllib.parse.urlencode({k: v for k, v in query.items() if v not in (None, '')})
    return f"vless://{_q(node.get('uuid'))}@{_host(node)}?{q}{_remark(node)}"


def encode_hysteria2(node):
    query = {}
    if node.get('sni'):
        query['sni'] = node['sni']
    if node.get('obfs'):
        query['obfs'] = node['obfs']
    if node.get('obfs-password'):
        query['obfs-password'] = node['obfs-password']
    q = urllib.parse.urlencode(query)
    return f"hysteria2://{_q(node.get('password'))}@{_host(node)}{'?'+q if q else ''}{_remark(node)}"


def encode_anytls(node):
    query = {}
    if node.get('sni'):
        query['sni'] = node['sni']
    q = urllib.parse.urlencode(query)
    return f"anytls://{_q(node.get('password'))}@{_host(node)}{'?'+q if q else ''}{_remark(node)}"


def encode_ssr(node):
    password = __import__('base64').urlsafe_b64encode(str(node.get('password') or '').encode()).decode().rstrip('=')
    main = ':'.join([
        str(node.get('server')),
        str(node.get('port')),
        str(node.get('protocol') or 'origin'),
        str(node.get('cipher')),
        str(node.get('obfs') or 'plain'),
        password,
    ])
    params = []
    remarks = __import__('base64').urlsafe_b64encode(str(node.get('name') or '').encode()).decode().rstrip('=')
    params.append(f'remarks={remarks}')
    if node.get('protocol-param'):
        params.append('protoparam=' + __import__('base64').urlsafe_b64encode(str(node['protocol-param']).encode()).decode().rstrip('='))
    if node.get('obfs-param'):
        params.append('obfsparam=' + __import__('base64').urlsafe_b64encode(str(node['obfs-param']).encode()).decode().rstrip('='))
    encoded = __import__('base64').urlsafe_b64encode((main + '/?' + '&'.join(params)).encode()).decode().rstrip('=')
    return f'ssr://{encoded}'


ENCODERS = {
    'ss': encode_ss,
    'ssr': encode_ssr,
    'trojan': encode_trojan,
    'vmess': encode_vmess,
    'vless': encode_vless,
    'hysteria2': encode_hysteria2,
    'hysteria': encode_hysteria2,
    'anytls': encode_anytls,
}


def proxies_from(path):
    data = yaml.load(open(path, encoding='utf-8').read(), Loader=SafeLoader)
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return [x for x in (data.get('proxies') or []) if isinstance(x, dict)]


def convert(path):
    urls = []
    for node in proxies_from(path):
        encoder = ENCODERS.get(node.get('type'))
        if not encoder:
            continue
        try:
            url = encoder(node)
        except Exception:
            continue
        if url:
            urls.append(url)
    return urls


if __name__ == '__main__':
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else 'output.yaml'
    out = sys.argv[2] if len(sys.argv) > 2 else 'nodes.txt'
    urls = convert(src)
    with open(out, 'w', encoding='utf-8') as writer:
        writer.write('\n'.join(urls))
        if urls:
            writer.write('\n')
    print(f'Wrote {len(urls)} URIs to {out}')
