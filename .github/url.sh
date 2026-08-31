#!/bin/bash
set -euo pipefail
name=Openit
if [ ! -s url ]; then
  echo "empty url" >&2
  exit 1
fi
line=$(grep -cve '^$' url)
time=$(date '+%Y.%m.%d %H:%M:%S')

echo "$time >>> $line" >> .github/log && sed -i '2d' .github/log
echo -e "REMARKS=$name \nSTATUS=节点数量: $line.♥.更新时间: $time"
