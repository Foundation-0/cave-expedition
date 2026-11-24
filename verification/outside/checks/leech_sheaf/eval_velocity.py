"""Exact first-order velocity of every contact, and the Lemma B gates (evaluator check).

Checks, in exact integer and rational arithmetic and with no shared code with the target:
for BW16, with X the projection of the identity onto the bar-tangent strains, no contact
has negative velocity, the 32 zero-velocity contacts are exactly the bars, and the three
Lemma B gates hold at tau = 1/4000. For Leech, the natural seed (projection of the
identity) gives 28 negative contacts out of 9,432,672, while the target's tuned seed
gives 0 negative, 48 zero (all bars) and gates that hold at tau = 1e-10.
Backs: AUDIT-020R, VERDICTS.md section 1 (all contacts checked, repaired gate sufficient)
and the section 3 repair "Leech seed: the canonical choice fails on 28 contacts".
Needs: Python 3, numpy, a clone of the target at the head of draft PR 106
(first argument, or environment variable INCENTRE_LATTICES_PR106).
Run: python3 -I -B eval_velocity.py /path/to/incentre-lattices
Time: about 1 minute. No random numbers are used. Writes no files.
"""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import team_data, fail, bw16_minvecs, leech_minvecs  # noqa: E402
from eval_velocity_lib import project, sweep, gates, best_tau, ldl_min_shift  # noqa: E402

problems = []


def expect(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        problems.append(name)


# ---------------- BW16 ----------------
C16 = [[Fraction(x, 2) for x in r] for r in team_data("C2_16_WITNESS")]
L16 = [[(2 if i == j else 0) + C16[i][j] for j in range(16)] for i in range(16)]
I16 = [[Fraction(int(i == j)) for j in range(16)] for i in range(16)]
X16 = project(L16, C16, I16)
L16x, mv16 = bw16_minvecs()
c16, d16, z16 = sweep("BW16", 16, 2, L16x, mv16, X16)
Xs16 = [[(X16[i][j] + X16[j][i]) / 2 for j in range(16)] for i in range(16)]
bars = set()
for i in range(16):
    bars.add((2 * i, tuple(int(2 * x) for x in C16[i])))
    bars.add((2 * i + 1, tuple(int(-2 * x) for x in C16[i])))
print("BW16 counts", c16, "delta", d16, float(d16))
expect("BW16 contacts: 137280 inter-cell, 960 intra", c16["inter"] == 137280 and c16["intra"] == 960)
expect("BW16 no negative velocity", c16["neg"] == 0)
expect("BW16 32 zeros, exactly the bars", c16["zero"] == 32 and set((p, tuple(w)) for p, w in z16) == bars)
expect("BW16 delta > 1/7", d16 > Fraction(1, 7))
expect("BW16 symmetric part >= 1/5 I", ldl_min_shift(Xs16, Fraction(1, 5)))
g = gates(L16, X16, Fraction(1, 5), d16, Fraction(1, 4000))
expect("BW16 Lemma B gates hold at tau = 1/4000", all(bool(x) for x in g[:3]))
print("BW16 largest tau = 1/N passing the gates: 1/%d" % best_tau(L16, X16, Fraction(1, 5), d16).denominator)

# ---------------- Leech ----------------
U24 = team_data("U24_WITNESS")
C24 = [[Fraction(x, 4) for x in r] for r in U24]
L24 = [[(2 if i == j else 0) + C24[i][j] for j in range(24)] for i in range(24)]
I24 = [[Fraction(int(i == j)) for j in range(24)] for i in range(24)]
L24x, mv24 = leech_minvecs()
X24a = project(L24, C24, I24)
ca, da, za = sweep("Leech", 24, 4, L24x, mv24, X24a)
print("Leech seed = projection of identity: counts", ca, "smallest positive velocity", float(da))
expect("Leech natural seed: 28 negative contacts", ca["neg"] == 28 and ca["inter"] == 9432672)
X0 = [[Fraction(v, 256) for v in r] for r in team_data("X0_24_INT_256")]
X24b = project(L24, C24, X0)
cb, db, zb = sweep("Leech", 24, 4, L24x, mv24, X24b)
Xsb = [[(X24b[i][j] + X24b[j][i]) / 2 for j in range(24)] for i in range(24)]
print("Leech target seed projected: counts", cb, "delta", float(db))
expect("Leech target seed: 0 negative, 48 zero, 9432672 inter-cell, 2208 intra",
       cb["neg"] == 0 and cb["zero"] == 48 and cb["inter"] == 9432672 and cb["intra"] == 2208)
expect("Leech delta >= 2/25", db >= Fraction(2, 25))
expect("Leech symmetric part >= 1/5 I", ldl_min_shift(Xsb, Fraction(1, 5)))
gb = gates(L24, X24b, Fraction(1, 5), db, Fraction(1, 10**10))
expect("Leech Lemma B gates hold at tau = 1e-10", all(bool(x) for x in gb[:3]))
print("Leech largest tau = 1/N passing the gates: 1/%d" % best_tau(L24, X24b, Fraction(1, 5), db).denominator)

if problems:
    fail("; ".join(problems))
print("RESULT leech_sheaf/eval_velocity: PASS BW16 0 negative and 32 bar zeros of 137280; "
      "Leech target seed 0 negative and 48 bar zeros of 9432672; natural Leech seed 28 negative")
