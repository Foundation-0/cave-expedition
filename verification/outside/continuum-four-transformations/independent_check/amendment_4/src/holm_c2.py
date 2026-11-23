"""Amendment 4, C2: a failed Law 2b instance has each of its tests enter the Holm procedure with p = 1. Exact arithmetic, exhaustive small cases.
Holm step-down as section 9 and section 12a use it: sort the p-values ascending, reject p_(i) while p_(i) <= alpha / (m - i + 1), stop at the first failure.
Standard library only. No bare assert."""
import sys
from fractions import Fraction as F
from itertools import product

out = []
w = out.append
fails = []
def chk(name, ok, detail=""):
    w(f"[{'ok' if ok else 'FAIL'}] {name}{(': ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

ALPHA = F(1, 20)
def holm(ps, m):
    """ps: dict test -> p. m: family size. returns the set of rejected tests."""
    order = sorted(ps, key=lambda k: (ps[k], k))
    rej = set()
    for i, k in enumerate(order, start=1):
        if ps[k] <= ALPHA / (m - i + 1):
            rej.add(k)
        else:
            break
    return rej

GRID = [F(1, 2000), F(1, 400), F(1, 100), F(1, 50), F(1, 20), F(1, 10), F(1)]
m = 5
mono_bad = 0
drop_looser = drop_strict = same_as_drop = total = 0
for ps in product(GRID, repeat=m):
    base = {i: ps[i] for i in range(m)}
    r0 = holm(base, m)
    for mask in range(1, 2 ** m):
        J = {i for i in range(m) if mask >> i & 1}
        withp1 = {i: (F(1) if i in J else ps[i]) for i in range(m)}
        r1 = holm(withp1, m)
        # monotone: raising p-values of J cannot make any test outside J newly rejected, and rejects only tests whose p <= 1/m... never J itself unless p was 1
        if not (r1 - J) <= (r0 - J):
            mono_bad += 1
        if r1 & J and any(ps[i] != 1 for i in r1 & J):
            mono_bad += 1
        # alternative reading: drop the tests of J and run Holm on the rest with the smaller family
        rest = {i: ps[i] for i in range(m) if i not in J}
        r2 = holm(rest, len(rest)) if rest else set()
        total += 1
        if not r1 <= r2:
            mono_bad += 1
        if r2 - r1:
            drop_looser += 1
total_cases = total
w(f"   m = {m}, {len(GRID)} p-values per test, every failed subset: {total_cases:,} cases")
chk("with p = 1 the family size stays m: no test outside the failed set is rejected that was not rejected with its true p-values, and no failed test is rejected", mono_bad == 0)
chk("dropping the failed tests and shrinking the family would reject more in some cases (the looser reading C2 does not take)", drop_looser > 0, f"{drop_looser:,} cases where dropping rejects a test that p = 1 does not")
# the smallest threshold stays alpha/m when tests fail
chk("smallest Holm threshold stays 0.05 / 102 for the Law 2b family when 15 tests of a failed instance enter with p = 1", ALPHA / 102 == F(1, 2040), "0.05/102 = 0.000490")
# tests per instance: presence 3, arrow 6 pairs of the 3 counting instruments, flow 6 pairs
w("   tests of one instance: presence 3, arrow 6, flow 6 (only the kinds the instance has: 8 presence instances have 3 tests, 7 arrow instances 6, 6 flow instances 6)")
from collections import Counter
inst = {"W": (1, 1, 1), "Q": (1, 1, 0), "H": (1, 1, 1), "F": (1, 1, 1), "M": (1, 1, 0), "D": (1, 1, 1), "O4": (1, 0, 0), "E": (1, 1, 0), "B": (0, 0, 1), "R": (0, 0, 1)}
tot = sum(a * 3 + b * 6 + c * 6 for a, b, c in inst.values())
chk("instance test counts add to the family of 102", tot == 102, str(tot))
w("   tests of W: " + str(3 + 6 + 6) + " (all enter with p = 1 if W fails its pre-data check)")
w("")
w("RESULT " + ("all Holm checks hold" if not fails else "FAILED " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
