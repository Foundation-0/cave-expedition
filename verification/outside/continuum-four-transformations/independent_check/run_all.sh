#!/bin/bash
# Rerun every check against the plan files in the folder above and record the results in out/.
# Usage: ./run_all.sh [frozen_plan_file]
#   PY_EXACT   Python 3.12 or later, standard library only (default: python3)
#   PY_NUMPY   Python 3.12 or later with numpy (default: python3)
#   The frozen plan (commit 24d7757) is needed by quote_check.py. Make it with:
#   git show 24d7757:verification/outside/continuum-four-transformations/PREREG.md > frozen_PREREG.md
set -u
cd "$(dirname "$0")"
PY_EXACT="${PY_EXACT:-python3}"
PY_NUMPY="${PY_NUMPY:-python3}"
FROZEN="${1:-frozen_PREREG.md}"
mkdir -p out
{
./run3.sh "$PY_EXACT" src/amendment_numbers.py
./run3.sh "$PY_EXACT" src/review_figures.py
./run3.sh "$PY_EXACT" src/symmetry_sawtooth.py
./run3.sh "$PY_EXACT" src/offset_rule.py
./run3.sh "$PY_EXACT" src/budget_and_channels.py ../PREREG.md
./run3.sh "$PY_EXACT" src/plan_numbers.py ../PREREG.md
./run3.sh "$PY_EXACT" src/manifest_check.py ..
./run3.sh "$PY_EXACT" src/quote_check.py "$FROZEN" ..
./run3.sh "$PY_EXACT" src/arrow_null.py
./run3.sh "$PY_EXACT" src/size_arithmetic.py
./run3.sh "$PY_EXACT" src/tess_size_consistency.py
./run3.sh "$PY_EXACT" src/outcomes.py
./run3.sh "$PY_NUMPY" src/pipeline_identity.py
./run3.sh "$PY_NUMPY" src/tie_rates.py
./run3.sh "$PY_NUMPY" src/shot_process.py
./run3.sh "$PY_NUMPY" src/k2_flag_rates.py
./run3.sh "$PY_NUMPY" src/k3_detection.py
} | tee out/SUMMARY.txt
