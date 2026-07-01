#!/usr/bin/env bash
# Snapshot the current renders into the dated evolution log.
# usage:  NOTE=short-note bash snap.sh
set -euo pipefail
MACHINE="${MACHINE:-einhander}"
NOTE="${NOTE:?set NOTE=short-note}"
HERE="$(cd "$(dirname "$0")" && pwd)"
dir="$HERE/renders/$MACHINE"
mkdir -p "$dir"
n=$(printf '%04d' $(( $(ls "$dir"/*-iso.png 2>/dev/null | wc -l) + 1 )))
for v in iso thumb top; do
  src="$HERE/build/${MACHINE}_${v}.png"
  [ -f "$src" ] && cp "$src" "$dir/${n}-${NOTE}-${v}.png"
done
echo "- ${n}-${NOTE} — $(date -I) — ${NOTE}" >> "$dir/INDEX.md"
echo "logged frame ${n}: ${NOTE}"
