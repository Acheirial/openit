#!/bin/sh
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
VER="${SUBCONVERTER_EXTENDED_VERSION:-v1.9.0}"
URL="https://github.com/Aethersailor/SubConverter-Extended/releases/download/${VER}/SubConverter-Extended-${VER}-linux-amd64.tar.gz"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl -fsSL -o "$TMP/sce.tar.gz" "$URL"
tar -xzf "$TMP/sce.tar.gz" -C "$TMP"
SRC="$TMP/SubConverter-Extended"

cp -f "$SRC/subconverter" "$ROOT/subconverter.bin"
chmod +x "$ROOT/subconverter.bin"
rm -rf "$ROOT/lib" "$ROOT/lib64"
cp -a "$SRC/lib" "$ROOT/lib"
cp -a "$SRC/lib64" "$ROOT/lib64"
mkdir -p "$ROOT/usr/lib"
cp -f "$SRC/usr/lib/libmihomo.so" "$ROOT/usr/lib/libmihomo.so"
chmod +x "$ROOT/usr/lib/libmihomo.so"
printf '%s\n' "$VER" > "$ROOT/EXTENDED-VERSION"
echo "Installed SubConverter-Extended $VER"
