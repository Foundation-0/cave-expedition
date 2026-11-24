#!/bin/sh
# usage: run_up.sh <A|B|C> <tag> <script> [args...]  : runs an upstream script (or my driver) in the sandbox
M="$1"; TAG="$2"; shift 2
HERE="$(pwd)"
case "$M" in
  A) FL="-I -B" ;;
  B) FL="-I -O -B" ;;
  C) FL="-I -B -W error" ;;
esac
"$HERE/src/sbx.sh" "$HERE/out" $FL "$@" > "$HERE/out/${TAG}_$M.txt" 2> "$HERE/out/${TAG}_$M.err"
echo $? > "$HERE/out/${TAG}_$M.rc"
