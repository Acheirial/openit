#!/bin/sh
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
VER="${MIHOMO_VERSION:-v1.19.30}"
GOOS="${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
GOARCH="${2:-$(uname -m)}"

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

curl -fsSL -o "$TMP/$NAME" "$URL"
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
