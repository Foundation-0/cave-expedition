#!/bin/bash
# Like run3.sh but one mode at a time (one process at once). Usage: ./run3seq.sh <python> <script> [arguments...]
set -u
py="$1"; script="$2"; shift 2
name=$(basename "$script" .py)
mkdir -p out
i=0
for modeflags in "-I -B" "-I -O -B" "-I -B -W error"; do
  i=$((i+1))
  err=$("$py" $modeflags "$script" "$@" 2>&1 >"out/$name.mode$i.txt")
  echo "rc=$? stderr_bytes=${#err}" > "out/$name.mode$i.status"
done
h1=$(md5 -q "out/$name.mode1.txt"); h2=$(md5 -q "out/$name.mode2.txt"); h3=$(md5 -q "out/$name.mode3.txt")
s1=$(cat "out/$name.mode1.status"); s2=$(cat "out/$name.mode2.status"); s3=$(cat "out/$name.mode3.status")
if [ "$h1" = "$h2" ] && [ "$h2" = "$h3" ] && [ "$s1" = "$s2" ] && [ "$s2" = "$s3" ]; then same=IDENTICAL; else same=DIFFERENT; fi
echo "$name: modes $same; $s1; md5 $h1"
