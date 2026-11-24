#!/bin/sh
# Hygiene checks to run before every push. usage: hygiene.sh <plan branch ref, for example origin/outside/continuum-four-transformations-prereg> [origin code branch ref]
# 1. every plan file on this branch is byte-identical to the plan branch tip (the diff must print nothing);
# 2. no local path or person name in the package, no CRLF, no __pycache__, no bare assert in code;
# 3. check-prose exits 0 on every markdown file of the package that differs from the remote code branch.
# Exit status 1 if any check fails.
PLAN="${1:?plan branch ref}"
REMOTE="${2:-origin/outside/continuum-four-transformations-code}"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 1
P=verification/outside/continuum-four-transformations
rc=0
d=$(git diff --stat "$PLAN" HEAD -- $P/PREREG.md $P/README.md $P/AMENDMENT_1.md $P/AMENDMENT_2.md $P/AMENDMENT_3.md $P/checks $P/independent_check $P/DATA_REQUEST.md $P/ARM_B_OUTLINE.md $P/FETCH_MANIFEST.tsv)
if [ -n "$d" ]; then echo "FAIL plan files differ from $PLAN:"; echo "$d"; rc=1; else echo "ok   plan files byte-identical to $PLAN ($(git rev-parse --short "$PLAN"))"; fi
if ! git merge-base --is-ancestor "$PLAN" HEAD; then echo "FAIL the branch does not contain $PLAN"; rc=1; fi
hits=$(grep -rIl "/Users/\|kethuda" $P --exclude-dir=.git --exclude-dir=checks --exclude-dir=independent_check --exclude-dir=frozen_plan_code --exclude-dir=out_frozen_plan --exclude=hygiene.sh 2>/dev/null)
if [ -n "$hits" ]; then echo "FAIL local path or name in:"; echo "$hits"; rc=1; else echo "ok   no local path or name"; fi
crlf=$(grep -rIl $'\r' $P/src $P/known_answer --include='*.py' --include='*.md' --include='*.sh' 2>/dev/null)
if [ -n "$crlf" ]; then echo "FAIL CRLF in: $crlf"; rc=1; else echo "ok   LF endings"; fi
pyc=$(find $P -name __pycache__ 2>/dev/null | head -1)
if [ -n "$pyc" ]; then echo "FAIL __pycache__ present"; rc=1; else echo "ok   no __pycache__"; fi
as=$(grep -rn "^[[:space:]]*assert " $P/src $P/known_answer --include='*.py' 2>/dev/null | grep -v "frozen_plan" | head -3)
if [ -n "$as" ]; then echo "FAIL bare assert: $as"; rc=1; else echo "ok   no bare assert"; fi
for f in $(git diff --name-only "$REMOTE" -- $P 2>/dev/null | grep '\.md$' | grep -v "PREREG.md\|AMENDMENT_[123].md\|DATA_REQUEST\|ARM_B\|independent_check\|/checks/\|^$P/README.md"); do
  if [ -f "$f" ]; then
    python3 "$HOME/.hermes/team-skills/scripts/check-prose.py" "$f" > /dev/null 2>&1 || { echo "FAIL check-prose on $f"; rc=1; }
  fi
done
[ "$rc" = 0 ] && echo "ok   check-prose exit 0 on changed markdown files"
[ "$rc" = 0 ] && echo "HYGIENE PASS" || echo "HYGIENE FAIL"
exit $rc
