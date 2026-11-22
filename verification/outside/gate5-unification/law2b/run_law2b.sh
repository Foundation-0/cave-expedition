#!/bin/sh
# usage: sh run_law2b.sh [<path to transformational_steelman_certifier.py>]      (run from the law2b/ folder)
# Runs the Law 2b checker, the certifier feed and the clean-room scripts, each in three interpreter modes (side by side) inside the sandbox
# (no network, writes only inside law2b/). Writes <name>.mode{1,2,3}.{out,err,rc,sec} next to each script's out/ folder and
# one line per run in out/hashes.txt and clean_room/out/hashes.txt (exit status, SHA-256 of stdout, stderr bytes, seconds).
# The team certifier is not in this repository. It is Foundation-0/cave-expedition PR 1 at 80606f1,
# symbiosis/round10/arm5-transformational-steelman/transformational_steelman_certifier.py. Without the argument
# the feed step and clean_room/src/cert.py are skipped.
D="$(pwd)"
PKG="$(cd .. && pwd)"
TC="$1"
SB="(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$D\") (literal \"/dev/null\"))"
PY=/opt/homebrew/bin/python3.12
# ONLY=feed reruns just the certifier feed (after law2b_check has run) and replaces its lines in out/hashes.txt.
# ONLY=cert reruns just clean_room/src/cert.py and replaces its lines in clean_room/out/hashes.txt.
if [ "$ONLY" = feed ]; then
  grep -v -e '^out/feed' -e '^FINISHED' out/hashes.txt > out/hashes.tmp; cat out/hashes.tmp > out/hashes.txt; : > out/hashes.tmp
elif [ "$ONLY" = cert ]; then
  grep -v -e '^clean_room/out/cert' clean_room/out/hashes.txt > out/hashes.tmp; cat out/hashes.tmp > clean_room/out/hashes.txt; : > out/hashes.tmp
else
  : > out/hashes.txt
  : > clean_room/out/hashes.txt
fi
run3() {  # run3 <hashfile> <outprefix> <script> [args...]   the three modes run side by side
  hf="$1"; pre="$2"; shift 2
  i=0
  for fl in "-I -B" "-I -O -B" "-I -B -W error"; do
    i=$((i+1))
    (
      t0=$(date +%s)
      PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p "$SB" perl -e 'alarm 3600; exec @ARGV' $PY $fl "$@" > "$pre.mode$i.out" 2> "$pre.mode$i.err"
      echo $? > "$pre.mode$i.rc"
      echo $(( $(date +%s) - t0 )) > "$pre.mode$i.sec"
    ) &
  done
  wait
  i=0
  for fl in "-I -B" "-I -O -B" "-I -B -W error"; do
    i=$((i+1))
    echo "$pre [$fl] exit=$(cat "$pre.mode$i.rc") stdout=$(shasum -a 256 "$pre.mode$i.out" | cut -d' ' -f1) stderr_bytes=$(wc -c < "$pre.mode$i.err" | tr -d ' ') seconds=$(cat "$pre.mode$i.sec")" | tee -a "$hf"
  done
  if cmp -s "$pre.mode1.out" "$pre.mode2.out" && cmp -s "$pre.mode1.out" "$pre.mode3.out"; then echo "$pre IDENTICAL_ACROSS_MODES" | tee -a "$hf"; else echo "$pre DIFFERS_ACROSS_MODES" | tee -a "$hf"; fi
}
if [ "$ONLY" = cert ]; then
  run3 clean_room/out/hashes.txt clean_room/out/cert clean_room/src/cert.py "$TC"
  exit 0
fi
[ "$ONLY" = feed ] || run3 out/hashes.txt out/law2b_check src/law2b_check.py "$PKG"
if [ -n "$TC" ]; then
  run3 out/hashes.txt out/feed src/feed_team_certifier.py out/law2b_check.mode1.out "$TC"
fi
[ "$ONLY" = feed ] && { echo FINISHED | tee -a out/hashes.txt; exit 0; }
for s in r6 r4 r4b r156 lat oth; do
  run3 clean_room/out/hashes.txt clean_room/out/$s clean_room/src/$s.py
done
if [ -n "$TC" ]; then
  run3 clean_room/out/hashes.txt clean_room/out/cert clean_room/src/cert.py "$TC"
fi
echo FINISHED | tee -a out/hashes.txt
