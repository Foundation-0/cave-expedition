#!/bin/sh
s="$1"; b="${s%.py}"
python3 -I -B "$s" > "out_${b}.mode1.txt" 2> "out_${b}.mode1.err"; r1=$?
python3 -I -O -B "$s" > "out_${b}.mode2.txt" 2> "out_${b}.mode2.err"; r2=$?
python3 -I -B -W error "$s" > "out_${b}.mode3.txt" 2> "out_${b}.mode3.err"; r3=$?
echo "$s exit codes: $r1 $r2 $r3"
if cmp -s "out_${b}.mode1.txt" "out_${b}.mode2.txt" && cmp -s "out_${b}.mode1.txt" "out_${b}.mode3.txt"; then echo "identical output in all three modes"; else echo "OUTPUTS DIFFER"; fi
