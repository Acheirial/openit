import time
import yaml
import requests
from crawl import get_file_list, get_proxies
from parse import parse, makeclash
from clash import push
from multiprocessing import Process, Manager
from yaml.loader import SafeLoader

headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip', 'Connection': 'Keep-Alive', 'User-Agent': 'Clash'}

def local(proxy_list, file):
    try:
        with open(file, 'r') as reader:
            working = yaml.safe_load(reader)
        data_out = []
        for x in working['proxies']:
            data_out.append(x)
        proxy_list.append(data_out)
    except:
        print(file + ": No such file")

def url(proxy_list, link):
    try:
        working = yaml.safe_load(requests.get(url=link, timeout=240, headers=headers).text)
        data_out = []
        for x in working['proxies']:
            data_out.append(x)
        proxy_list.append(data_out)
    except:
        print("Error in Collecting " + link )
        #pass

def fetch(proxy_list, filename):
    current_date = time.strftime("%Y_%m_%d", time.localtime())
    baseurl = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'
    working = yaml.safe_load(requests.get(url=baseurl + current_date + '/' + filename, timeout=240).text)
    data_out = []
    for x in working['proxies']:
        data_out.append(x)
    proxy_list.append(data_out)

proxy_list=[]
if __name__ == '__main__':
    with Manager() as manager:
        proxy_list = manager.list()
        current_date = time.strftime("%Y_%m_%d", time.localtime())
        start = time.time()
        with open('config.yaml', 'r') as reader:
            config = yaml.load(reader, Loader=SafeLoader)
            subscribe_links = config.get('sub') or []
            subscribe_files = config.get('local') or []
        tree = get_file_list()
        filenames = []
        if tree:
            directories, total = tree
            data = parse(directories) or {}
            filenames = data.get(current_date) or []
        print("Success: find " + str(len(subscribe_links) + len(subscribe_files) + len(filenames)) + " Clash link")

        processes=[]
        try:
            for i in subscribe_files:
                p = Process(target=local, args=(proxy_list, i))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
            processes=[]
            for i in subscribe_links:
                p = Process(target=url, args=(proxy_list, i))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
            processes=[]
            for i in filenames:
                p = Process(target=fetch, args=(proxy_list, i))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
            end = time.time()
            print("Collecting in " + "{:.2f}".format(end-start) + " seconds")
        except Exception as e:
            end = time.time()
            print("Collecting in " + "{:.2f}".format(end-start) + " seconds: " + str(e))

        proxy_list=list(proxy_list)
        proxies = makeclash(proxy_list)
        print("Merged proxies: " + str(len(proxies)))
        if not proxies:
            raise SystemExit('no proxies collected')
        push(proxies)
