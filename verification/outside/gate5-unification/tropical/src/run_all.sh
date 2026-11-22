#!/bin/sh
# Run every section under the three interpreter modes, compare, and record SHA-256 hashes.
# usage: sh src/run_all.sh   (from anywhere; paths are relative to the tropical/ directory)
set -u
cd "$(dirname "$0")/.." || exit 1
PY=python3
HERM=../hermitian/objects
ANCHOR=out/anchor_tropical.stdout
rc=0
for mode in 1 2 3; do
  case $mode in
    1) flags="-I -B" ;;
    2) flags="-I -O -B" ;;
    3) flags="-I -B -W error" ;;
  esac
  d=out/mode$mode
  rm -rf "$d"; mkdir -p "$d"
  for o in tower cole_hopf lp farkas; do
    $PY $flags src/make_objects.py $o > "$d/obj_$o.json" 2> "$d/obj_$o.err" || { echo "FAIL make_objects $o mode$mode"; rc=1; }
  done
  $PY $flags src/tropical_audit.py s4row4 $ANCHOR > "$d/s4row4.json" 2> "$d/s4row4.err" || { echo "FAIL s4row4 mode$mode"; rc=1; }
  $PY $flags src/tropical_audit.py s4row8 > "$d/s4row8.json" 2> "$d/s4row8.err" || { echo "FAIL s4row8 mode$mode"; rc=1; }
  $PY $flags src/tropical_audit.py s4bridge $HERM > "$d/s4bridge.json" 2> "$d/s4bridge.err" || { echo "FAIL s4bridge mode$mode"; rc=1; }
  $PY $flags src/tropical_audit.py s4null > "$d/s4null.json" 2> "$d/s4null.err" || { echo "FAIL s4null mode$mode"; rc=1; }
  $PY $flags src/tropical_audit.py s5real > "$d/s5real.json" 2> "$d/s5real.err" || { echo "FAIL s5real mode$mode"; rc=1; }
  $PY $flags src/tropical_audit.py s5random > "$d/s5random.json" 2> "$d/s5random.err" || { echo "FAIL s5random mode$mode"; rc=1; }
  $PY $flags src/tropical_audit.py controls > "$d/controls.json" 2> "$d/controls.err"; crc=$?
  echo "controls exit code mode$mode: $crc" >> "$d/controls.exit"
  [ "$crc" -eq 0 ] || { echo "FAIL controls mode$mode (exit $crc)"; rc=1; }
done
# compare and hash
: > out/hashes.txt
for f in obj_tower obj_cole_hopf obj_lp obj_farkas s4row4 s4row8 s4bridge s4null s5real s5random controls; do
  h1=$(shasum -a 256 out/mode1/$f.json | cut -d' ' -f1)
  h2=$(shasum -a 256 out/mode2/$f.json | cut -d' ' -f1)
  h3=$(shasum -a 256 out/mode3/$f.json | cut -d' ' -f1)
  if [ "$h1" = "$h2" ] && [ "$h2" = "$h3" ]; then st=IDENTICAL; else st=DIFFERENT; rc=1; fi
  echo "$f $st mode1=$h1 mode2=$h2 mode3=$h3" >> out/hashes.txt
done
for f in obj_tower obj_cole_hopf obj_lp obj_farkas; do
  cp out/mode1/$f.json objects/${f#obj_}.json
done
cat out/hashes.txt
exit $rc
