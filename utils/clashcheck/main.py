import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from check import check
from tqdm import tqdm
from init import init, clean
from clash import push, checkenv, checkuse, pick_alive

if __name__ == '__main__':
    alive = []
    http_port, api_port, threads, source, timeout, outfile, proxyconfig, apiurl, testurl, config, secret = init()
    clashname, operating_system = checkenv()
    checkuse(clashname, operating_system)
    clash = subprocess.Popen([clashname, '-f', './temp/working.yaml', '-d', '.'])
    time.sleep(5)
    proxies = config.get('proxies') or []
    workers = max(1, int(threads))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(check, alive, proxy, apiurl, timeout, testurl, secret)
            for proxy in proxies
        ]
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Testing"):
            pass
    time.sleep(5)
    print("Alive proxies: " + str(len(alive)))
    alive = pick_alive(alive)
    print("Published proxies: " + str(len(alive)))
    push(alive,outfile)
    clean(clash)
