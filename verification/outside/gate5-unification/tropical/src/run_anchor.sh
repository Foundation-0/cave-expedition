#!/bin/sh
# Run the three upstream scripts untouched, in the sandbox, writes confined to out/.
# usage: sh src/run_anchor.sh   (needs /opt/homebrew/bin/python3.12 and sandbox-exec)
set -u
cd "$(dirname "$0")/.." || exit 1
O=$(pwd)/out
U=$(pwd)/upstream
run() {
  name=$1; shift
  PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p "(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$O\") (literal \"/dev/null\"))" perl -e 'alarm 600; exec @ARGV' /opt/homebrew/bin/python3.12 -I -B "$@" > "$O/anchor_$name.stdout" 2> "$O/anchor_$name.stderr"
  echo "$name exit $?"
}
run tropical "$U/qlb/studies/expedition-farkas-peeling/tropical_quotient_sheaf_bridge.py" --json
run portal78 "$U/qlb/studies/expedition-farkas-peeling/portal78_homotopy_bregman_bridge.py" --json
run verifier "$U/fr/studies/expedition-mult-farkas-dsi/verify_mult_farkas_dsi.py"
