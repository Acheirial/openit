#!/bin/bash
set -euo pipefail

git restore --source=HEAD --worktree --staged -- utils/subconverter/generate.ini 2>/dev/null || true

if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo -e "\033[32mnothing to commit, working tree clean.\033[0m"
  exit 0
fi

git status -s
git add -A
git restore --staged --worktree -- utils/subconverter/generate.ini 2>/dev/null || true
if git diff --cached --quiet; then
  echo -e "\033[32mnothing to commit after excluding generate.ini.\033[0m"
  exit 0
fi

git commit -m "$(date '+%Y.%m.%d %H:%M:%S') 订阅更新"
git pull --rebase origin main
git push origin main
