#!/bin/bash
# Reruns the clean-room checks of Amendment 4, three Python modes each, one process at a time.
# Usage, from inside the repository: independent_check/amendment_4/run_all.sh
#   PY        Python 3.12 or later (default: python3). Standard library only.
#   PK        folder that holds the published AMENDMENT_4.md and PREREG.md (default: ../..)
#   BASE_DIR  folder that holds base_PREREG.md and base_AMENDMENT_2.md, the files at commit 4c6ecd1.
#             If unset they are read with git from commit 4c6ecd1, so run inside a clone that has it.
set -u
cd "$(dirname "$0")"
PY="${PY:-python3}"
PK="${PK:-../..}"
mkdir -p out
if [ -z "${BASE_DIR:-}" ]; then
  git show 4c6ecd1:verification/outside/continuum-four-transformations/PREREG.md > out/base_PREREG.md
  git show 4c6ecd1:verification/outside/continuum-four-transformations/AMENDMENT_2.md > out/base_AMENDMENT_2.md
  BASE_DIR=out
fi
R=./run3seq.sh
{
$R "$PY" src/quotes_a4d.py "$PK/AMENDMENT_4.md" "$BASE_DIR/base_PREREG.md" "$BASE_DIR/base_AMENDMENT_2.md"
$R "$PY" src/tie_enum2.py
$R "$PY" src/d8_new2.py
$R "$PY" src/outcome_flip.py
$R "$PY" src/holm_c2.py
$R "$PY" src/epoch_keys.py
$R "$PY" src/epoch_mixed.py
} | tee out/SUMMARY.txt
