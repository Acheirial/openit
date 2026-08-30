#!/bin/sh
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
GOOS="${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
GOARCH="${2:-$(uname -m)}"
API="https://api.github.com/repos/MetaCubeX/mihomo/releases"

case "$GOOS" in
  linux|darwin|windows) ;;
  mingw*|msys*|cygwin*) GOOS=windows ;;
  *)
    echo "unsupported os: $GOOS" >&2
    exit 1
    ;;
esac

case "$GOARCH" in
  x86_64|amd64) GOARCH=amd64 ;;
  aarch64|arm64) GOARCH=arm64 ;;
  *)
    echo "unsupported arch: $GOARCH" >&2
    exit 1
    ;;
esac

github_get() {
  if [ -n "$GITHUB_TOKEN" ]; then
    curl -fsSL -H "Authorization: Bearer ${GITHUB_TOKEN}" -H "Accept: application/vnd.github+json" "$@"
  else
    curl -fsSL -H "Accept: application/vnd.github+json" "$@"
  fi
}

if [ -n "$MIHOMO_VERSION" ]; then
  RELEASE_URL="$API/tags/${MIHOMO_VERSION}"
else
  RELEASE_URL="$API/latest"
fi

VER="$(github_get "$RELEASE_URL" | python3 -c '
import json, sys
r = json.load(sys.stdin)
if r.get("draft") or r.get("prerelease"):
    raise SystemExit("refusing non-release: %s" % r.get("tag_name"))
tag = r.get("tag_name") or ""
if not tag:
    raise SystemExit("missing tag_name")
print(tag)
')"

if [ "$GOOS" = windows ]; then
  NAME="mihomo-windows-${GOARCH}-${VER}.zip"
  DEST="$ROOT/clash-windows-${GOARCH}.exe"
else
  NAME="mihomo-${GOOS}-${GOARCH}-${VER}.gz"
  DEST="$ROOT/clash-${GOOS}-${GOARCH}"
fi

URL="https://github.com/MetaCubeX/mihomo/releases/download/${VER}/${NAME}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

github_get -o "$TMP/$NAME" "$URL"
if [ "$GOOS" = windows ]; then
  unzip -qo "$TMP/$NAME" -d "$TMP"
  BIN="$(find "$TMP" -type f -name 'mihomo*.exe' | head -n 1)"
  test -n "$BIN"
  cp -f "$BIN" "$DEST"
else
  gzip -dc "$TMP/$NAME" > "$DEST"
  chmod +x "$DEST"
fi

printf '%s\n' "$VER" > "$ROOT/MIHOMO-VERSION"
echo "Installed Mihomo $VER -> $DEST"
