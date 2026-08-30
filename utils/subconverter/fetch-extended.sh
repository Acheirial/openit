#!/bin/sh
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
API="https://api.github.com/repos/Aethersailor/SubConverter-Extended/releases"

github_get() {
  if [ -n "$GITHUB_TOKEN" ]; then
    curl -fsSL -H "Authorization: Bearer ${GITHUB_TOKEN}" -H "Accept: application/vnd.github+json" "$@"
  else
    curl -fsSL -H "Accept: application/vnd.github+json" "$@"
  fi
}

if [ -n "$SUBCONVERTER_EXTENDED_VERSION" ]; then
  RELEASE_URL="$API/tags/${SUBCONVERTER_EXTENDED_VERSION}"
else
  RELEASE_URL="$API/latest"
fi

META="$(github_get "$RELEASE_URL")"
VER="$(printf '%s' "$META" | python3 -c '
import json, sys
r = json.load(sys.stdin)
if r.get("draft") or r.get("prerelease"):
    raise SystemExit("refusing non-release: %s" % r.get("tag_name"))
tag = r.get("tag_name") or ""
if not tag:
    raise SystemExit("missing tag_name")
print(tag)
')"
NAME="SubConverter-Extended-${VER}-linux-amd64.tar.gz"
DIGEST="$(printf '%s' "$META" | NAME="$NAME" python3 -c '
import json, os, sys
r = json.load(sys.stdin)
name = os.environ["NAME"]
for asset in r.get("assets") or []:
    if asset.get("name") == name:
        digest = asset.get("digest") or ""
        if digest.startswith("sha256:"):
            print(digest.split(":", 1)[1])
            break
        raise SystemExit("missing sha256 digest for %s" % name)
else:
    raise SystemExit("asset not found: %s" % name)
')"
URL="https://github.com/Aethersailor/SubConverter-Extended/releases/download/${VER}/${NAME}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

github_get -o "$TMP/sce.tar.gz" "$URL"
GOT="$(sha256sum "$TMP/sce.tar.gz" | awk '{print $1}')"
if [ "$GOT" != "$DIGEST" ]; then
  echo "digest mismatch for $NAME" >&2
  echo "expected $DIGEST" >&2
  echo "got $GOT" >&2
  exit 1
fi
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
