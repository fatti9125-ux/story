#!/usr/bin/env bash
# Download the story asset library listed in assets_manifest.tsv into ./assets
# Skips files already present with the right size; retries; verifies byte size.
# Needs drive.usercontent.google.com allowed in the environment network.
set -u
cd "$(dirname "$0")"
OUT=assets; mkdir -p "$OUT"
JOBS=${JOBS:-4}
fetch() {
  id="$1"; size="$2"; path="$OUT/$3"
  mkdir -p "$(dirname "$path")"
  if [ -f "$path" ] && [ "$(stat -c %s "$path")" = "$size" ]; then echo "ok    $3"; return 0; fi
  for t in 1 2 3 4; do
    curl -sS -L --fail -o "$path.part" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" \
      && [ "$(stat -c %s "$path.part")" = "$size" ] && mv "$path.part" "$path" && { echo "got   $3"; return 0; }
    sleep $((t*5))
  done
  echo "FAIL  $3"; rm -f "$path.part"; return 1
}
export -f fetch; export OUT
grep -v '^#' assets_manifest.tsv | tr '\t' '\n' | xargs -d '\n' -n 3 -P "$JOBS" bash -c 'fetch "$0" "$1" "$2"'
echo "--- done"
