#!/bin/bash
# Run one script in the three modes at once and compare the outputs.
# Usage (from the independent_check folder): ./run3.sh <python> <script> [arguments...]
# Writes out/<name>.mode1.txt, .mode2.txt, .mode3.txt and out/<name>.mode<N>.status, and prints one summary line.
set -u
py="$1"; script="$2"; shift 2
name=$(basename "$script" .py)
mkdir -p out
run_mode() {
  local i="$1"; shift
  local err
  err=$("$py" "$@" 2>&1 >"out/$name.mode$i.txt")
  local rc=$?
  echo "rc=$rc stderr_bytes=${#err}" > "out/$name.mode$i.status"
}
run_mode 1 -I -B "$script" "$@" &
run_mode 2 -I -O -B "$script" "$@" &
run_mode 3 -I -B -W error "$script" "$@" &
wait
h1=$(md5 -q "out/$name.mode1.txt" 2>/dev/null || md5sum < "out/$name.mode1.txt" | cut -d' ' -f1)
h2=$(md5 -q "out/$name.mode2.txt" 2>/dev/null || md5sum < "out/$name.mode2.txt" | cut -d' ' -f1)
h3=$(md5 -q "out/$name.mode3.txt" 2>/dev/null || md5sum < "out/$name.mode3.txt" | cut -d' ' -f1)
s1=$(cat "out/$name.mode1.status"); s2=$(cat "out/$name.mode2.status"); s3=$(cat "out/$name.mode3.status")
if [ "$h1" = "$h2" ] && [ "$h2" = "$h3" ] && [ "$s1" = "$s2" ] && [ "$s2" = "$s3" ]; then same=IDENTICAL; else same=DIFFERENT; fi
echo "$name: modes $same; $s1; md5 $h1"
