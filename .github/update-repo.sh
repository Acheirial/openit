#!/bin/bash
set -euo pipefail

products=(
  url
  https
  long
  Clash.yaml
  .github/log
  utils/pool/check
  utils/pool/output.yaml
  utils/clashcheck/data/check.yaml
)

git restore --source=HEAD --worktree --staged -- utils/subconverter/generate.ini 2>/dev/null || true

changed=0
existing=()
for path in "${products[@]}"; do
  if [ ! -e "$path" ]; then
    continue
  fi
  existing+=("$path")
  if ! git diff --quiet -- "$path" || [ -z "$(git ls-files -- "$path")" ]; then
    changed=1
  fi
done
if [ "$changed" -eq 0 ]; then
  echo -e "\033[32mnothing to commit, subscription products unchanged.\033[0m"
  exit 0
fi

git status -s -- "${existing[@]}"
git add -- "${existing[@]}"
if git diff --cached --quiet; then
  echo -e "\033[32mnothing to commit after excluding generate.ini.\033[0m"
  exit 0
fi

git commit -m "$(date '+%Y.%m.%d %H:%M:%S') 订阅更新"
for i in 1 2 3; do
  if git pull --rebase origin main && git push origin main; then
    exit 0
  fi
  git rebase --abort >/dev/null 2>&1 || true
  sleep 5
done
echo "rebase/push failed after 3 attempts" >&2
exit 1
