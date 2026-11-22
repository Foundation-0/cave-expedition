#!/usr/bin/env python3
"""Recount every total of the second-pass rulings from rulings.json and compare with the text.

Backs: README.md and OUTSIDE_AUDIT.md (the counts of findings and rulings) and REVIEW-RESPONSE.md item 6.
Needs: python3 (3.8 or newer), standard library only. No network, no clone, no input other than the files
beside this script.
Run: python3 -I -B check_totals.py
Result: one line starting RESULT, exit code 0 only if every count agrees.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FAIL = []


def need(cond, msg):
    if not cond:
        FAIL.append(msg)
        print("FAIL:", msg)


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def main():
    data = json.loads(read("rulings.json"))
    rulings = [(a["area"], f) for a in data["areas"] for f in a["findings"]]
    kinds = Counter(f["ruling"] for _, f in rulings)
    need(set(kinds) <= {"stands", "stands_narrowed", "falls"}, "unknown ruling label %s" % sorted(kinds))
    ids = [(area, f["id"]) for area, f in rulings]
    need(len(ids) == len(set(ids)), "duplicate finding id")
    # a finding with two parts carries ids such as F1a and F1b; they count once as a first-pass finding
    findings = {(area, f["id"].rstrip("ab") if f.get("part") else f["id"]) for area, f in rulings}
    n_rulings, n_findings = len(rulings), len(findings)
    totals = {"stands": kinds["stands"], "stands_narrowed": kinds["stands_narrowed"], "falls": kinds["falls"]}
    print("recount from rulings.json: %d first-pass findings, %d rulings: %s" % (n_findings, n_rulings, totals))
    need(data["totals"] == totals, "totals in rulings.json %s differ from the recount %s" % (data["totals"], totals))
    need(data["first_pass_findings"] == n_findings, "first_pass_findings differs from the recount")
    need(data["rulings"] == n_rulings, "rulings differs from the recount")
    need(sum(totals.values()) == n_rulings, "the three totals do not add up to the number of rulings")
    sentence = ("%d first-pass findings carry %d rulings, because one finding (`folds-dn-e8` F1) had a label part and a "
                "wording part: %d stood as written, %d were narrowed and %d fell"
                % (n_findings, n_rulings, totals["stands"], totals["stands_narrowed"], totals["falls"]))
    for name in ("README.md", "OUTSIDE_AUDIT.md"):
        need(sentence in read(name), "%s does not state: %s" % (name, sentence))
    # the old totals must be gone from the text
    for name in ("README.md", "OUTSIDE_AUDIT.md", "REVIEW-RESPONSE.md"):
        text = read(name)
        stale = "13 stood as written, 22 were narrowed and 1 fell"
        need(stale not in text or name == "REVIEW-RESPONSE.md", "%s still states the old totals" % name)
    print("RESULT check_totals: %s (%d failed checks, %d findings, %d rulings)"
          % ("PASS" if not FAIL else "FAIL", len(FAIL), n_findings, n_rulings))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
