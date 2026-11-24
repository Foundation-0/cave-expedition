#!/bin/sh
# usage: run_all.sh <hermitian_dir>  -- runs every script under the three interpreter modes and checks identical output
set -u
W="$1"
OUT="$W/out"
PY=/opt/homebrew/bin/python3.12
SRC="$W/src"
rc=0
sh "$SRC/run_anchor.sh" "$W" > "$OUT/run_anchor.log" 2>&1
: > "$OUT/mode_hashes.txt"
for script in build_objects compare anchor_compare; do
  case $script in
    build_objects) arg="$W/objects" ;;
    compare) arg="$W/objects" ;;
    anchor_compare) arg="$W" ;;
  esac
  i=0
  for flags in "-I -B" "-I -O -B" "-I -B -W error"; do
    i=$((i+1))
    $PY $flags "$SRC/$script.py" "$arg" > "$OUT/$script.mode$i.log" 2> "$OUT/$script.mode$i.err"
    code=$?
    h=$(shasum -a 256 "$OUT/$script.mode$i.log" | cut -d' ' -f1)
    echo "$script mode$i flags='$flags' exit=$code sha256=$h" >> "$OUT/mode_hashes.txt"
    [ $code -eq 0 ] || rc=1
  done
  h1=$(shasum -a 256 "$OUT/$script.mode1.log" | cut -d' ' -f1)
  h2=$(shasum -a 256 "$OUT/$script.mode2.log" | cut -d' ' -f1)
  h3=$(shasum -a 256 "$OUT/$script.mode3.log" | cut -d' ' -f1)
  if [ "$h1" != "$h2" ] || [ "$h1" != "$h3" ]; then echo "$script: MODE OUTPUTS DIFFER" >> "$OUT/mode_hashes.txt"; rc=1; fi
done
echo "run_all exit=$rc" >> "$OUT/mode_hashes.txt"
exit $rc
