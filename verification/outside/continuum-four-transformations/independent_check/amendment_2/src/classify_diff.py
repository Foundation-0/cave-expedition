"""Classify every changed line of the draft PREREG.md against the base. Prints hunks with a word-level diff for replaced lines.
The base is commit f584897, read with git, so run it from inside the repository. Argument: path of the PREREG.md to compare.
Standard library only. No bare assert."""
import subprocess
import difflib
import re
import sys


def slurp(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read().split("\n")


a = subprocess.run(["git", "show", "f584897:verification/outside/continuum-four-transformations/PREREG.md"], capture_output=True, text=True, check=True).stdout.split("\n")
b = slurp(sys.argv[1])
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
n_ins = n_del = n_rep = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    print(f"== {tag}: base lines {i1+1}-{i2}, draft lines {j1+1}-{j2}")
    if tag == "replace" and (i2 - i1) == (j2 - j1) == 1:
        wa = re.findall(r"\S+", a[i1])
        wb = re.findall(r"\S+", b[j1])
        s2 = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
        for t2, x1, x2, y1, y2 in s2.get_opcodes():
            if t2 == "equal":
                continue
            print(f"   {t2}: base words [{' '.join(wa[x1:x2])[:300]}] -> draft words [{' '.join(wb[y1:y2])[:300]}]")
        n_rep += 1
    else:
        for l in a[i1:i2]:
            print("   - " + l[:140])
        for l in b[j1:j2]:
            print("   + " + l[:140])
        n_del += i2 - i1
        n_ins += j2 - j1
print(f"INFO lines deleted {n_del}, inserted {n_ins}, one-line replacements {n_rep}")
# numbers appearing in the changed regions of the base that are thresholds elsewhere must survive: list sections intact
for pat in ("K >= 6", "0.00125", "74 or more", "129 or more", "99,999", "R = 99,999", "1/4 over", "0.30"):
    ca = sum(l.count(pat) for l in a)
    cb = sum(l.count(pat) for l in b)
    print(f"INFO occurrences of '{pat}': base {ca}, draft {cb}")
print("DONE classify_diff")
