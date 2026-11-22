#!/bin/sh
# usage: run_anchor.sh <hermitian_dir>   (absolute path of the work directory)
# Runs the three upstream scripts untouched under sandbox-exec, writes confined to <hermitian_dir>/out.
set -u
W="$1"
OUT="$W/out"
PY=/opt/homebrew/bin/python3.12
run() {  # run <logname> <script> [args...]
  name="$1"; shift
  PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p "(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$OUT\") (literal \"/dev/null\"))" perl -e 'alarm 600; exec @ARGV' $PY -I -B "$@" > "$OUT/$name.stdout" 2> "$OUT/$name.stderr"
  echo "$name exit=$?"
}
rm -rf "$OUT/anchor_fractals" "$OUT/anchor_gravity"
mkdir -p "$OUT/anchor_fractals" "$OUT/anchor_gravity"
cp "$W/upstream/fractals/studies/expedition-witness-zeno-schur/probe4_witness_zeno_schur.py" "$OUT/anchor_fractals/"
cp "$W/upstream/fractals/studies/expedition-witness-zeno-schur/probe4_witness_zeno_results.json" "$OUT/anchor_fractals/committed_results.json"
cp "$W/upstream/gravity/studies/expedition-aest-helmholtz-probes/probe1_aest_helmholtz_closure.py" "$OUT/anchor_gravity/"
( cd "$W" && shasum -a 256 out/anchor_fractals/probe4_witness_zeno_schur.py upstream/fractals/studies/expedition-witness-zeno-schur/probe4_witness_zeno_schur.py out/anchor_gravity/probe1_aest_helmholtz_closure.py upstream/gravity/studies/expedition-aest-helmholtz-probes/probe1_aest_helmholtz_closure.py upstream/ledger-pr1/check_003_seam01_ropt.py ) > "$OUT/anchor_input_hashes.txt"
run anchor_check003 "$W/upstream/ledger-pr1/check_003_seam01_ropt.py"
run anchor_probe4 "$OUT/anchor_fractals/probe4_witness_zeno_schur.py"
run anchor_probe1 "$OUT/anchor_gravity/probe1_aest_helmholtz_closure.py"
# raw output hashes first, then replace the absolute work directory by a placeholder in text logs
( cd "$OUT" && shasum -a 256 anchor_check003.stdout anchor_check003.stderr anchor_probe4.stdout anchor_probe4.stderr anchor_probe1.stdout anchor_probe1.stderr anchor_fractals/probe4_witness_zeno_results.json ) > "$OUT/anchor_output_hashes_raw.txt"
for f in anchor_check003.stdout anchor_check003.stderr anchor_probe4.stdout anchor_probe4.stderr anchor_probe1.stdout anchor_probe1.stderr; do
  sed "s#$W#<WORKDIR>#g" "$OUT/$f" > "$OUT/$f.tmp" && mv "$OUT/$f.tmp" "$OUT/$f"
done
( cd "$OUT" && shasum -a 256 anchor_check003.stdout anchor_check003.stderr anchor_probe4.stdout anchor_probe4.stderr anchor_probe1.stdout anchor_probe1.stderr anchor_fractals/probe4_witness_zeno_results.json ) > "$OUT/anchor_output_hashes_sanitized.txt"
