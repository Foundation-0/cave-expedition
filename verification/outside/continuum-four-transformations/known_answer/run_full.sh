#!/bin/sh
# Full known-answer runs, K1 to K6, at the plan's full seed counts, in three Python modes, one mode after another.
# usage: run_full.sh <results dir> <build folder>
# Run from a clean checkout of the code commit. Long tests are split into parts with the same seeds and joined afterwards
# (K2 in 8 parts, K3 in 4, K4 and K5 by seed in 10 parts). At most 4 worker processes run at once. Each run is timed (wall and
# processor seconds) and its exit status goes to <results dir>/status.txt; outputs go to <results dir>/mode<N>/.
RES="$1"
BUILD="$2"
PKG="$(cd "$(dirname "$0")/.." && pwd)"
HERE="$PKG/known_answer"
mkdir -p "$RES"
cd "$PKG" || exit 1
{
  echo "code commit: $(git rev-parse HEAD)"
  echo "python: $(/usr/local/bin/python3.14 --version 2>&1)"
  echo "numpy: $(/usr/local/bin/python3.14 -c 'import numpy; print(numpy.__version__)')"
  echo "start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$RES/run_info.txt"
: > "$RES/status.txt"
: > "$RES/timing.txt"
flags() { case "$1" in 1) echo "-I -B";; 2) echo "-I -O -B";; 3) echo "-I -B -W error";; esac; }
timed() {  # timed <label> <out file> <err file> <mode> <script and args...>
  label="$1"; of="$2"; ef="$3"; m="$4"; shift 4
  fl=$(flags "$m")
  /usr/bin/time -p nice -n 10 "$HERE/sbpy.sh" "$BUILD" 172800 $fl "$@" > "$of" 2> "$ef"
  rc=$?
  echo "$label exit $rc" >> "$RES/status.txt"
  echo "$label: $(tr '\n' ' ' < "$ef")" >> "$RES/timing.txt"
  return $rc
}
parts_run() {  # parts_run <mode> <test> <nparts> <combine script>
  m="$1"; t="$2"; np="$3"; comb="$4"
  out="$RES/mode$m"
  p=0
  files=""
  while [ "$p" -lt "$np" ]; do
    timed "mode$m $t part $p of $np" "$out/parts/$t.part$p.txt" "$out/parts/$t.part$p.err" "$m" "$HERE/$t.py" full "$p" "$np"
    files="$files $out/parts/$t.part$p.txt"
    p=$((p + 1))
  done
  timed "mode$m $t combined" "$out/$t.txt" "$out/$t.err" "$m" "$HERE/$comb" full $files
}
for m in 1 2 3; do
  mkdir -p "$RES/mode$m/parts"
  timed "mode$m k6_gate_checks" "$RES/mode$m/k6_gate_checks.txt" "$RES/mode$m/k6_gate_checks.err" "$m" "$HERE/k6_gate_checks.py" full
  timed "mode$m units_check" "$RES/mode$m/units_check.txt" "$RES/mode$m/units_check.err" "$m" "$HERE/units_check.py"
  timed "mode$m review_witnesses" "$RES/mode$m/review_witnesses.txt" "$RES/mode$m/review_witnesses.err" "$m" "$HERE/review_witnesses.py"
  timed "mode$m k1_exact_checks" "$RES/mode$m/k1_exact_checks.txt" "$RES/mode$m/k1_exact_checks.err" "$m" "$HERE/k1_exact_checks.py" full
  parts_run "$m" k3_planted_structure 4 k3_combine.py
  parts_run "$m" k2_nothing_in_noise 8 k2_combine.py
  parts_run "$m" k4_transfer 10 k4_combine.py
  parts_run "$m" k5_scale_flow 10 k5_combine.py
  echo "mode$m done: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RES/run_info.txt"
done
echo "end: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RES/run_info.txt"
touch "$RES/ALLDONE"
