#!/bin/bash
# Reruns every check of the Amendment 2 independent check against the plan files two folders up, three modes at once.
# Usage, from inside the repository: independent_check/amendment_2/run_all.sh
#   PY_EXACT   Python 3.12 or later, standard library only (default: python3)
#   PY_NUMPY   Python 3.12 or later with numpy (default: python3)
# quotes.py and classify_diff.py read the base commit f584897 with git, so run this inside a clone that has that commit.
set -u
cd "$(dirname "$0")"
PY_EXACT="${PY_EXACT:-python3}"
PY_NUMPY="${PY_NUMPY:-python3}"
R=../run3.sh
PK=../..
mkdir -p out
{
$R "$PY_EXACT" src/published_files_check.py $PK/PREREG.md $PK/AMENDMENT_2.md $PK/README.md $PK/AMENDMENT_1.md
$R "$PY_EXACT" src/quotes.py $PK/AMENDMENT_2.md
$R "$PY_EXACT" src/classify_diff.py $PK/PREREG.md
$R "$PY_EXACT" src/test_counts.py $PK/PREREG.md
$R "$PY_EXACT" ../src/outcomes.py
$R "$PY_EXACT" src/holm_steps.py
$R "$PY_EXACT" src/compute_and_points.py
$R "$PY_EXACT" src/seed_keys.py
$R "$PY_EXACT" src/tied_waveform.py
$R "$PY_EXACT" src/constant_segments.py
$R "$PY_EXACT" src/tau0_integer_form.py
$R "$PY_EXACT" src/saw_noise.py
$R "$PY_NUMPY" src/k1_scope.py
$R "$PY_NUMPY" src/k1_normal_scores.py
$R "$PY_NUMPY" src/integer_identity.py
$R "$PY_NUMPY" src/yprime_const.py
$R "$PY_NUMPY" src/k5_series_checks.py
$R "$PY_NUMPY" src/cascade_tau0.py
} | tee out/SUMMARY.txt
