def parse(data_in):
    dtp = []
    for x in data_in or []:
        dtp.append(x.replace('data/', '', 1))
    dtpr1 = [ x for x in dtp if "/" in x]
    dtpr2 = [ x for x in dtpr1 if ".yaml" in x]
    textdict = {}
    for x in dtpr2:
        parts = x.split('/')
        if len(parts) != 2:
            continue
        date, filename = parts
        if date in textdict:
            textdict[date].append(filename)
        else:
            textdict[date] = [filename]
    return textdict

def _fingerprint(node):
    if not isinstance(node, dict):
        return None
    kind = node.get('type')
    if not kind:
        return None
    return (
        kind,
        str(node.get('server') or ''),
        str(node.get('port') or ''),
        str(node.get('uuid') or node.get('password') or node.get('psk') or ''),
        str(node.get('cipher') or ''),
        str(node.get('network') or ''),
    )


def makeclash(dictin):
    seen = set()
    proxies = []
    for x in dictin:
        for y in x:
            try:
                key = _fingerprint(y)
                if not key or key in seen:
                    continue
                seen.add(key)
                proxies.append(y)
            except Exception:
                continue
    return proxies
