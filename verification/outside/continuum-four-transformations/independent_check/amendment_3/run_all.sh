#!/bin/bash
# Reruns the clean-room checks of Amendment 3, three Python modes each, against the plan files two folders up.
# Usage, from inside the repository: independent_check/amendment_3/run_all.sh
#   PY   Python 3.12 or later with numpy (default: python3). The committed outputs were made with Python 3.14.6 and numpy 2.5.4.
# base_PREREG.md is read with git from commit 1aa53fb, so run this inside a clone that has that commit.
set -u
cd "$(dirname "$0")"
PY="${PY:-python3}"
R=../run3.sh
PK=../..
mkdir -p out
git show 1aa53fb:verification/outside/continuum-four-transformations/PREREG.md > out/base_PREREG.md
{
$R "$PY" src/sk_keys.py
$R "$PY" src/sk_keys2.py
$R "$PY" src/sk_keys3b.py
$R "$PY" src/sk_keys4.py
$R "$PY" src/sk_keys5.py
$R "$PY" src/sk_mustfail.py
$R "$PY" src/sk_counts.py
$R "$PY" src/sk8_maps.py
$R "$PY" src/sk8_rates2.py
$R "$PY" src/sk8_proxy2.py
$R "$PY" src/sk9_compute.py
$R "$PY" src/sk_quotes.py $PK/AMENDMENT_3.md out/base_PREREG.md
$R "$PY" ../amendment_2/src/test_counts.py $PK/PREREG.md
$R "$PY" ../src/outcomes.py
# the author's own scripts, rerun for comparison with their committed outputs
for s in seed_keys compute_k3 amp_maps; do
  $R "$PY" $PK/checks/amendment_3/$s.py
  for m in 1 2 3; do
    if cmp -s out/$s.mode$m.txt $PK/checks/amendment_3/out_$s.mode$m.txt; then echo "  $s mode$m equals the committed output"; else echo "  $s mode$m DIFFERS from the committed output"; fi
  done
done
./check_published.sh
} | tee out/SUMMARY.txt
