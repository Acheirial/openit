#!/bin/sh

echo -e "proxypool\n"
echo "download proxypool..."
wget https://github.com/Sansui233/proxypool/releases/download/v0.6.1/proxypool-linux-amd64 -O proxypool
echo "done"
echo "chmod 授予777权限..."
chmod +777 proxypool
echo "done"
echo "静默执行程序，默认配置..."
nohup ./proxypool -c ./config.yaml > /dev/null 2>&1 &
echo "done"
ps -e | grep proxypool
echo "这个进程的PID是..."
