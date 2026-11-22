#!/bin/sh
# usage: TMPD=<scratch dir> sh src/run_hashes.sh   (run from the second/ directory)
# Runs every script under three interpreter flag sets inside the sandbox and records the exit status,
# the SHA-256 of stdout and the SHA-256 of the out/ file the script writes.
D="$(pwd)"
SB="(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$D\") (literal \"/dev/null\"))"
PY=/opt/homebrew/bin/python3.12
: > out/hashes.txt
for s in c1_block c2_real c2_panel c2_anchor c3_trop; do
  for fl in "-I -B" "-I -O -B" "-I -B -W error"; do
    PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p "$SB" perl -e 'alarm 1800; exec @ARGV' $PY $fl src/$s.py > "$TMPD/o.txt" 2>"$TMPD/e.txt"
    rc=$?
    h=$(shasum -a 256 "$TMPD/o.txt" | cut -d' ' -f1)
    f=$(shasum -a 256 out/$s.txt 2>/dev/null | cut -d' ' -f1)
    echo "$s [$fl] exit=$rc stdout=$h outfile=$f stderr_bytes=$(wc -c < "$TMPD/e.txt" | tr -d ' ')" >> out/hashes.txt
  done
done
echo FINISHED >> out/hashes.txt
