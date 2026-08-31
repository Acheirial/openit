import os
import re
import yaml


class Quoted(str):
    pass


class ClashDumper(yaml.SafeDumper):
    pass


def _represent_quoted(dumper, data):
    text = str(data)
    if "'" in text and '"' not in text:
        return dumper.represent_scalar('tag:yaml.org,2002:str', text, style='"')
    return dumper.represent_scalar('tag:yaml.org,2002:str', text, style="'")


ClashDumper.add_representer(Quoted, _represent_quoted)
_SHORT_ID = re.compile(r'(?i)^(?:[0-9a-f]{2}){0,8}$')


def quote_strings(obj):
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if key == 'short-id' and value is not None:
                out[key] = Quoted(str(value))
            else:
                out[key] = quote_strings(value)
        return out
    if isinstance(obj, list):
        return [quote_strings(item) for item in obj]
    if isinstance(obj, str):
        return Quoted(obj)
    return obj


def dump_clash(data, stream):
    yaml.dump(quote_strings(data), stream, Dumper=ClashDumper, sort_keys=False, allow_unicode=True)


def dump_clash_file(data, path):
    tmp = str(path) + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as writer:
        dump_clash(data, writer)
    os.replace(tmp, path)


def reality_ok(proxy):
    opts = proxy.get('reality-opts')
    if not isinstance(opts, dict):
        return True
    sid = opts.get('short-id', '')
    if sid is None:
        sid = ''
    elif not isinstance(sid, str):
        sid = str(sid)
    sid = sid.strip()
    if not _SHORT_ID.fullmatch(sid):
        return False
    opts['short-id'] = sid
    return True


def sanitize_proxy(proxy):
    if not isinstance(proxy, dict):
        return proxy
    if proxy.get('network') == 'raw':
        proxy['network'] = 'tcp'
    return proxy
