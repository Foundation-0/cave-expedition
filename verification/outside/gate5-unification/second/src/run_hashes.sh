#!/bin/sh
# usage: TMPD=<scratch dir> sh src/run_hashes.sh   (run from the second/ directory)
# Optional: SCRIPTS="c4_thmA c5_thmB" runs only those scripts and appends their lines to out/hashes.txt.
# Runs every script under three interpreter flag sets inside the sandbox and records the exit status,
# the SHA-256 of stdout and the SHA-256 of the out/ file the script writes.
D="$(pwd)"
SB="(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$D\") (literal \"/dev/null\"))"
PY=/opt/homebrew/bin/python3.12
if [ -z "$SCRIPTS" ]; then
  SCRIPTS="c1_block c2_real c2_panel c2_anchor c3_trop c4_thmA c5_thmB"
  : > out/hashes.txt
else
  grep -v '^FINISHED$' out/hashes.txt > "$TMPD/h.txt"; cat "$TMPD/h.txt" > out/hashes.txt
fi
for s in $SCRIPTS; do
  for fl in "-I -B" "-I -O -B" "-I -B -W error"; do
    t0=$(date +%s)
    PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p "$SB" perl -e 'alarm 1800; exec @ARGV' $PY $fl src/$s.py > "$TMPD/o.txt" 2>"$TMPD/e.txt"
    rc=$?
    echo "$s [$fl] seconds=$(( $(date +%s) - t0 ))"
    h=$(shasum -a 256 "$TMPD/o.txt" | cut -d' ' -f1)
    f=$(shasum -a 256 out/$s.txt 2>/dev/null | cut -d' ' -f1)
    echo "$s [$fl] exit=$rc stdout=$h outfile=$f stderr_bytes=$(wc -c < "$TMPD/e.txt" | tr -d ' ')" >> out/hashes.txt
  done
done
echo FINISHED >> out/hashes.txt
