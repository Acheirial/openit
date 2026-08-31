import os
import secrets
import yaml
import shutil
import requests
from clash import filter, dump_clash
from yaml import SafeLoader

def init():
    if not os.path.exists('./temp'):
        os.mkdir('temp')

    config = 'config/config.yaml'
    # read from config file
    with open(config, 'r') as reader:
        config = yaml.load(reader, Loader=SafeLoader)
        http_port = config['http-port']
        api_port = config['api-port']
        threads = config['threads']
        source = str(config['source'])
        timeout = config['timeout']
        testurl = config['test-url']
        outfile = config['outfile']
    # get clash config file
    if source.startswith('http://'):
        proxyconfig = yaml.load(requests.get(source).text, Loader=SafeLoader)
    elif source.startswith('https://'):
        proxyconfig = yaml.load(requests.get(source).text, Loader=SafeLoader)
    else:
        with open(source, 'r') as reader:
            proxyconfig = yaml.load(reader, Loader=SafeLoader)

    # set clash api url
    baseurl = '127.0.0.1:' + str(api_port)
    apiurl = 'http://' + baseurl
    secret = secrets.token_urlsafe(24)

    # filter config files
    proxyconfig = filter(proxyconfig)

    config = {'port': http_port, 'external-controller': baseurl, 'secret': secret, 'mode': 'global',
              'log-level': 'silent', 'proxies': proxyconfig['proxies']}

    with open('./temp/working.yaml', 'w') as file:
        dump_clash(config, file)

    # return all variables
    return http_port, api_port, threads, source, timeout, outfile, proxyconfig, apiurl, testurl, config, secret

def clean(clash):
    if clash is not None:
        clash.terminate()
        try:
            clash.wait(timeout=5)
        except Exception:
            clash.kill()
    shutil.rmtree('./temp', ignore_errors=True)
