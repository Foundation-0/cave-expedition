#!/usr/bin/env python3
"""Recompute the canonical SHA-256 of the three gravity probe result files (AUDIT-011R, 012, 013R).

Backs: VERDICTS section 3, row "Team checks", the part that says the pinned
hashes fa4d3a1b (probe 1) and 35e16732 (probe 3) are stale against the published
head, while the verdicts they back still reproduce. The canonical hash is the
SHA-256 of the JSON with sorted keys and compact separators, with the stored
"sha256_canonical" field removed. This script uses its own code for it.

Checks: for probes 1, 2 and 3 the recomputed hash equals the value recorded in
the file; the three recomputed hashes start with bcde4938, ed74a3a4 and
6d467347; the two stale prefixes above are not the hash of any current file.
Pure standard library, no random numbers, no network.

Needs: Python 3; a clone of Foundation-0/gravity (draft pull request 30).
Run:   python3 -I -B a011r_probe_hashes.py /path/to/gravity
       (or set GRAVITY_REPO)
Time:  under one second.
Exit:  0 only if every check holds.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

NAME = "a011r_probe_hashes"
FAILS = []
COUNT = [0]


def check(cond, msg):
    COUNT[0] += 1
    if not cond:
        FAILS.append(msg)


args = [a for a in sys.argv[1:] if not a.startswith("--")]
GRAV = args[0] if args else os.environ.get("GRAVITY_REPO", "")
if not GRAV or not Path(GRAV).is_dir():
    raise SystemExit("Pass the path of a Foundation-0/gravity clone as the first argument or set GRAVITY_REPO.")
D = Path(GRAV) / "studies/expedition-aest-helmholtz-probes"
FILES = [("probe1", "probe1_aest_results.json", "bcde4938"),
         ("probe2", "probe2_latch_chirp_results.json", "ed74a3a4"),
         ("probe3", "probe3_inertia_boxes_results.json", "6d467347")]
STALE = ("fa4d3a1b", "35e16732")

got = {}
for tag, name, prefix in FILES:
    path = D / name
    if not path.is_file():
        raise SystemExit("Missing " + str(path) + ". Is the clone at the commit listed in README.md?")
    data = json.loads(path.read_text(encoding="utf-8"))
    recorded = data.pop("sha256_canonical", None)
    recomputed = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    got[tag] = recomputed
    check(recorded is not None, "%s: no recorded sha256_canonical field" % tag)
    check(recorded == recomputed, "%s: recorded hash differs from the recomputed one" % tag)
    check(recomputed.startswith(prefix), "%s: recomputed hash does not start with %s" % (tag, prefix))
    check(not any(recomputed.startswith(s) for s in STALE), "%s: recomputed hash matches a stale pinned prefix" % tag)

if "--verbose" in sys.argv:
    print(json.dumps(got, indent=1))
if FAILS:
    print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
    sys.exit(1)
print("RESULT %s: PASS %d of %d checks; recomputed canonical hashes %s match the recorded values; stale prefixes %s are not current" % (
    NAME, COUNT[0], COUNT[0], ", ".join(got[t][:8] for t, _, _ in FILES), " and ".join(STALE)))
