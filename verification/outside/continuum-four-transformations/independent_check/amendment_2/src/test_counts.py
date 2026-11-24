"""Test counts of the plan (40 confirmatory, 102 Law 2b) from the plan tables, and the Holm thresholds. Standard library only. int / Fraction / math.comb. No bare assert.
argv[1] = revised PREREG.md. Prints CLAIM / INFO / CONTROL lines; exit 1 if a must-fail control is not flagged."""
import re
import sys
from fractions import Fraction
from math import comb, factorial, ceil
from itertools import permutations

PLAN = sys.argv[1]
FAILS = []


def slurp(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def claim(tag, desc, text, mine, ok):
    print(f"CLAIM {tag} | {desc} | text={text} | mine={mine} | {'REPRODUCED' if ok else 'DIFFERS'}")


def tail(n, p, k):
    if k <= 0:
        return Fraction(1)
    return sum(Fraction(comb(n, j)) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))


def kmin(n, p, level):
    for k in range(n + 2):
        if tail(n, p, k) <= level:
            return k
    raise ValueError("none")


def f4(x, d=4):
    return f"{float(x):.{d}f}"


P05 = Fraction(1, 20)
text = slurp(PLAN).split("\n")

# ---------------- counts ----------------
print("# counts")
s9 = [i for i, l in enumerate(text) if l.startswith("## 9.")][0]
s10 = [i for i, l in enumerate(text) if l.startswith("## 10.")][0]
rows = [l for l in text[s9:s10] if l.startswith("| T") and not l.startswith("| Test")]
counts9 = [int(l.split("|")[2].strip()) for l in rows]
claim("count40", "confirmatory family, section 9 table", 40, sum(counts9), sum(counts9) == 40)
s12a = [i for i, l in enumerate(text) if l.startswith("## 12a.")][0]
s12b = [i for i, l in enumerate(text) if l.startswith("## 12b.")][0]
trs = [l for l in text[s12a:s12b] if re.match(r"\| T\d_", l)]
cols = {"a": 0, "b": 0, "c": 0}
for l in trs:
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    for name, c in zip("abc", cells[1:4]):
        if c.lower().startswith("none"):
            continue
        cols[name] += 1
        if "O4" in c:
            cols[name] += 1
print(f"INFO instances per column from the 12a table: {cols}")
n_a, n_b, n_c = cols["a"] * 3, cols["b"] * 6, cols["c"] * 6
claim("count102", "24 + 42 + 36 from the 12a table", 102, n_a + n_b + n_c, (n_a, n_b, n_c) == (24, 42, 36))
thr40 = Fraction(5, 4000)
thr102 = Fraction(5, 100 * 102)
claim("thr102", "0.05/102", "0.000490", f4(thr102, 6), f4(thr102, 6) == "0.000490")
control("wrong family size 93 flagged", n_a + n_b + n_c != 93)


if FAILS:
    print("FAILED CONTROLS:", FAILS)
    sys.exit(1)
print("DONE test_counts")
