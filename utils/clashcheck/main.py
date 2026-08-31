import os
import sys
import time
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from check import check
from tqdm import tqdm
from init import init, clean
from clash import push, checkenv, checkuse, pick_alive


def wait_mihomo(clash, apiurl, secret, timeout=30):
    headers = {'Authorization': 'Bearer ' + secret} if secret else {}
    deadline = time.time() + timeout
    while time.time() < deadline:
        if clash.poll() is not None:
            return False
        try:
            r = requests.get(apiurl + '/version', headers=headers, timeout=2)
            if r.ok:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


if __name__ == '__main__':
    alive = []
    clash = None
    http_port, api_port, threads, source, timeout, outfile, proxyconfig, apiurl, testurl, config, secret = init()
    clashname, operating_system = checkenv()
    checkuse(clashname, operating_system)
    tested = subprocess.run([clashname, '-t', '-f', './temp/working.yaml', '-d', '.'], capture_output=True, text=True)
    if tested.returncode != 0:
        sys.stderr.write(tested.stderr or tested.stdout or 'mihomo -t failed\n')
        if os.path.exists(outfile):
            print('Mihomo config test failed; keeping previous ' + outfile)
            sys.exit(0)
        raise SystemExit('Mihomo config test failed')
    clash = subprocess.Popen([clashname, '-f', './temp/working.yaml', '-d', '.'])
    if not wait_mihomo(clash, apiurl, secret):
        clean(clash)
        if os.path.exists(outfile):
            print('Mihomo failed to start; keeping previous ' + outfile)
            sys.exit(0)
        raise SystemExit('Mihomo failed to start')
    proxies = config.get('proxies') or []
    if not proxies:
        clean(clash)
        if os.path.exists(outfile):
            print('no proxies after filter; keeping previous ' + outfile)
            sys.exit(0)
        raise SystemExit('no proxies after filter')
    workers = max(1, int(threads))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(check, alive, proxy, apiurl, timeout, testurl, secret)
            for proxy in proxies
        ]
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Testing"):
            pass
    print("Alive proxies: " + str(len(alive)))
    alive = pick_alive(alive)
    print("Published proxies: " + str(len(alive)))
    if not alive:
        clean(clash)
        if os.path.exists(outfile):
            print('no alive proxies; keeping previous ' + outfile)
            sys.exit(0)
        raise SystemExit('no alive proxies')
    push(alive,outfile)
    clean(clash)
