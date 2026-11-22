#!/bin/sh
# usage: run_mode.sh <A|B|C> <tag> <script> [args...]   (run from the lattice/ directory; objects dir is chosen per mode)
M="$1"; TAG="$2"; SCRIPT="$3"; shift 3
HERE="$(pwd)"
case "$M" in
  A) FL="-I -B"; OBJ="$HERE/objects" ;;
  B) FL="-I -O -B"; OBJ="$HERE/out/objB" ;;
  C) FL="-I -B -W error"; OBJ="$HERE/out/objC" ;;
esac
mkdir -p "$OBJ"
# a literal OBJDIR argument is replaced by the mode specific objects directory
ARGS=""
for a in "$@"; do if [ "$a" = "OBJDIR" ]; then ARGS="$ARGS $OBJ"; else ARGS="$ARGS $a"; fi; done
/opt/homebrew/bin/python3.12 $FL "$HERE/src/$SCRIPT" $ARGS > "$HERE/out/${TAG}_$M.txt" 2> "$HERE/out/${TAG}_$M.err"
echo $? > "$HERE/out/${TAG}_$M.rc"
