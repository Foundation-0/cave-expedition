#!/bin/sh
# Full known-answer runs at the plan's full seed counts, in three Python modes, one mode after another.
# usage: run_full.sh <results dir> <build folder> <epoch> [test ...]
#   <epoch>  the key epoch of this full-count run, a whole number from 1 (reading D14 as amended by Amendment 4). Epoch 0 is a diagnostic
#            epoch and is refused here, and so is a missing epoch. Every seeded test named must be allowed to use this epoch by the ledger
#            known_answer/EPOCHS.tsv of this checkout joined with <build folder>/EPOCHS_started.tsv (epochs.py check): the lowest epoch
#            from 1 that the test has not used.
#   [test]   any of K1 K2 K3 K4 K5 K6 (default: all six). K6 has no random draws and runs without an epoch. Epochs belong to one test, so
#            tests whose next epochs differ are run in separate calls.
# Run from a clean checkout of the code commit: the run is refused if a tracked file of the package differs from the commit. Long tests are
# split into parts with the same seeds and joined afterwards (K2 in 8 parts, K3 in 4, K4 and K5 by seed in 10 parts); every part gets
# epoch=<epoch> and part=<p>/<n>, and the join refuses parts that disagree on epoch or code commit. At most 4 worker processes run at once.
# Each run is timed (wall and processor seconds) and its exit status goes to <results dir>/status.txt; outputs go to <results dir>/mode<N>/.
# The rows this run adds to the ledger are written to <results dir>/EPOCHS_rows.tsv; commit them to known_answer/EPOCHS.tsv (FULL_RUN.md).
# The checkout's own ledger cannot hold the rows of a run of its own commit, so before any test starts the rows are also appended to
# <build folder>/EPOCHS_started.tsv, which every later call with that build folder checks: a second run of a test on the same epoch from
# the same build folder is refused. The results folder must be new or empty, so that no earlier run's record is overwritten.
# Every write that records the run is checked, and after the append the build folder's ledger is read back: unless it now gives each
# seeded test a next epoch above this one, the run stops before any test starts (a run is never started unrecorded).
if [ $# -lt 3 ]; then
  echo "usage: run_full.sh <results dir> <build folder> <epoch> [test ...]"
  echo "refused: the key epoch is missing (a full-count run names its epoch, from 1)"
  exit 2
fi
RES="$1"
BUILD="$2"
EPOCH="$3"
shift 3
TESTS="$*"
[ -n "$TESTS" ] || TESTS="K1 K2 K3 K4 K5 K6"
case "$EPOCH" in
  ''|*[!0-9]*|0*) echo "refused: the epoch must be a whole number from 1 without a leading zero (epoch 0 is a diagnostic and cannot pass a test), got '$EPOCH'"; exit 2;;
esac
if [ "${#EPOCH}" -gt 9 ]; then
  echo "refused: the epoch must have at most 9 digits (epochs.py EPOCH_RE)"; exit 2
fi
for t in $TESTS; do
  case "$t" in
    K1|K2|K3|K4|K5|K6) ;;
    *) echo "refused: unknown test '$t' (use K1 to K6)"; exit 2;;
  esac
done
want() { case " $TESTS " in *" $1 "*) return 0;; esac; return 1; }
PKG="$(cd "$(dirname "$0")/.." && pwd)"
HERE="$PKG/known_answer"
cd "$PKG" || exit 1
COMMIT="$(git rev-parse HEAD)" || { echo "refused: not a git checkout"; exit 2; }
if [ -n "$(GIT_OPTIONAL_LOCKS=0 git status --porcelain --untracked-files=no -- .)" ]; then
  echo "refused: a tracked file of the package differs from commit $COMMIT; run from a clean checkout"
  exit 2
fi
if [ -e "$RES" ]; then
  if [ ! -d "$RES" ] || [ -n "$(ls -A "$RES")" ]; then
    echo "refused: the results folder '$RES' exists and is not an empty folder; every run gets a new results folder (and a rerun after an outcome a new epoch)"
    exit 2
  fi
fi
if [ ! -d "$BUILD" ] || [ ! -w "$BUILD" ]; then
  echo "refused: the build folder '$BUILD' is not a writable folder; it holds the checkout, the outputs and the ledger of started runs"
  exit 2
fi
STARTED="$BUILD/EPOCHS_started.tsv"
for t in K1 K2 K3 K4 K5; do
  if want "$t"; then
    if [ -f "$STARTED" ]; then
      "$HERE/sbpy.sh" "$BUILD" 600 -I -B "$HERE/epochs.py" check "$t" "$EPOCH" "$STARTED" || { echo "refused by the ledger for $t (see above)"; exit 2; }
    else
      "$HERE/sbpy.sh" "$BUILD" 600 -I -B "$HERE/epochs.py" check "$t" "$EPOCH" || { echo "refused by the ledger for $t (see above)"; exit 2; }
    fi
  fi
done
norec() { echo "refused: $1; no test was started"; exit 2; }
mkdir -p "$RES" || norec "cannot make the results folder '$RES'"
START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "code commit: $COMMIT"
  echo "key epoch: $EPOCH (master field 20261121e$EPOCH; K6 has no random draws and uses no epoch)"
  echo "tests: $TESTS"
  echo "python: $(/usr/local/bin/python3.14 --version 2>&1)"
  echo "numpy: $(/usr/local/bin/python3.14 -c 'import numpy; print(numpy.__version__)')"
  echo "start: $START"
} > "$RES/run_info.txt" || norec "cannot write $RES/run_info.txt"
: > "$RES/EPOCHS_rows.tsv" || norec "cannot write $RES/EPOCHS_rows.tsv"
for t in K1 K2 K3 K4 K5; do
  if want "$t"; then
    printf '%s\t%s\t%s\t%s\tfull-count\trun_full.sh, three modes, results folder %s\n' "$t" "$EPOCH" "$COMMIT" "$(echo "$START" | cut -c1-10)" "$(basename "$RES")" >> "$RES/EPOCHS_rows.tsv" \
      || norec "cannot write the ledger row of $t to $RES/EPOCHS_rows.tsv"
  fi
done
if [ ! -f "$STARTED" ]; then
  printf 'test\tepoch\tcode_commit\tdate\tkind\tnote\n' > "$STARTED" || norec "cannot make the build folder's ledger $STARTED"
fi
cat "$RES/EPOCHS_rows.tsv" >> "$STARTED" || norec "cannot append the run's rows to the build folder's ledger $STARTED"
for t in K1 K2 K3 K4 K5; do
  if want "$t"; then
    nxt="$("$HERE/sbpy.sh" "$BUILD" 600 -I -B "$HERE/epochs.py" next "$t" "$STARTED")"
    case "$nxt" in
      ''|*[!0-9]*) norec "the build folder's ledger $STARTED cannot be read back for $t (got '$nxt')";;
    esac
    [ "$nxt" -gt "$EPOCH" ] || norec "the build folder's ledger $STARTED does not show $t on epoch $EPOCH after the append"
  fi
done
: > "$RES/status.txt" || norec "cannot write $RES/status.txt"
: > "$RES/timing.txt" || norec "cannot write $RES/timing.txt"
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
parts_run() {  # parts_run <mode> <test script> <nparts> <combine script>
  m="$1"; t="$2"; np="$3"; comb="$4"
  out="$RES/mode$m"
  p=0
  files=""
  while [ "$p" -lt "$np" ]; do
    timed "mode$m $t part $p of $np" "$out/parts/$t.part$p.txt" "$out/parts/$t.part$p.err" "$m" "$HERE/$t.py" full "epoch=$EPOCH" "part=$p/$np"
    files="$files $out/parts/$t.part$p.txt"
    p=$((p + 1))
  done
  timed "mode$m $t combined" "$out/$t.txt" "$out/$t.err" "$m" "$HERE/$comb" full "epoch=$EPOCH" $files
}
for m in 1 2 3; do
  mkdir -p "$RES/mode$m/parts"
  if want K6; then timed "mode$m k6_gate_checks" "$RES/mode$m/k6_gate_checks.txt" "$RES/mode$m/k6_gate_checks.err" "$m" "$HERE/k6_gate_checks.py" full; fi
  timed "mode$m units_check" "$RES/mode$m/units_check.txt" "$RES/mode$m/units_check.err" "$m" "$HERE/units_check.py"
  timed "mode$m review_witnesses" "$RES/mode$m/review_witnesses.txt" "$RES/mode$m/review_witnesses.err" "$m" "$HERE/review_witnesses.py"
  if want K1; then timed "mode$m k1_exact_checks" "$RES/mode$m/k1_exact_checks.txt" "$RES/mode$m/k1_exact_checks.err" "$m" "$HERE/k1_exact_checks.py" full "epoch=$EPOCH"; fi
  if want K3; then parts_run "$m" k3_planted_structure 4 k3_combine.py; fi
  if want K2; then parts_run "$m" k2_nothing_in_noise 8 k2_combine.py; fi
  if want K4; then parts_run "$m" k4_transfer 10 k4_combine.py; fi
  if want K5; then parts_run "$m" k5_scale_flow 10 k5_combine.py; fi
  echo "mode$m done: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RES/run_info.txt"
done
echo "end: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RES/run_info.txt"
touch "$RES/ALLDONE"
