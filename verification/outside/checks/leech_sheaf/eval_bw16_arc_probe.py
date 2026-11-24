"""Exact check of the BW16 Cayley arc beyond the certified radius (evaluator check).

For the target's BW16 framework and the seed X = projection of the identity, computes in
exact rationals the smallest non-bar inter-cell contact excess (squared distance minus 2)
at tau = 1/4000 (the certified radius), 1/30 and 1/10. The arc stays separated at 1/4000
and 1/30 and overlaps at 1/10, so 1/4000 is safe and conservative.
Backs: AUDIT-020R, VERDICTS.md section 1 row "Barnes-Wall and Leech realizations and arcs"
(arc beyond the certified radius).
Needs: Python 3, numpy, a clone of the target at the head of draft PR 106
(first argument, or environment variable INCENTRE_LATTICES_PR106).
Run: python3 -I -B eval_bw16_arc_probe.py /path/to/incentre-lattices
Time: about 30 seconds. No random numbers are used. Writes no files.
"""
import math
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import team_data, fail, bw16_minvecs  # noqa: E402
from eval_velocity_lib import project, gates, neighbours, cayley_L  # noqa: E402

C16 = [[Fraction(x, 2) for x in r] for r in team_data("C2_16_WITNESS")]
L16 = [[(2 if i == j else 0) + C16[i][j] for j in range(16)] for i in range(16)]
I16 = [[Fraction(int(i == j)) for j in range(16)] for i in range(16)]
X = project(L16, C16, I16)
V = gates(L16, X, Fraction(1, 5), Fraction(1, 7), Fraction(1, 4000))[5]
L16x, mv = bw16_minvecs()
W = np.array(mv, dtype=np.int64)
P, nb = neighbours(2, L16x, W)
best = {}
for tau in (Fraction(1, 4000), Fraction(1, 30), Fraction(1, 10)):
    Lt = cayley_L(L16, C16, V, tau)
    # common integer scaling: vec = (m . LtD + (q - p) * den) / (2 den), all in exact Python integers
    den = 1
    for row in Lt:
        for v in row:
            den = den * v.denominator // math.gcd(den, v.denominator)
    LtD = np.array([[int(2 * v * den) for v in row] for row in Lt], dtype=object)
    two_den_sq = (2 * den) ** 2
    worst = None  # smallest nonzero d2 - 2, times (2 den)^2
    for pk in range(32):
        qk, m = nb[pk]
        keep = m.any(axis=1)
        mk = m[keep].astype(object)
        off = (P[qk[keep]] - P[pk]).astype(object) * den
        num = mk.dot(LtD) + off
        d = (num * num).sum(axis=1) - 2 * two_den_sq
        for v in d:
            if v != 0 and (worst is None or v < worst):
                worst = v
    best[tau] = Fraction(worst, two_den_sq)
    print("tau = %s: smallest non-bar inter-cell excess d2 - 2 = %.6g (exact rational)" % (tau, float(best[tau])))

problems = []
if not best[Fraction(1, 4000)] > 0:
    problems.append("not separated at 1/4000")
if not best[Fraction(1, 30)] > 0:
    problems.append("not separated at 1/30")
if not best[Fraction(1, 10)] < 0:
    problems.append("no overlap at 1/10")
if problems:
    fail("; ".join(problems))
print("RESULT leech_sheaf/eval_bw16_arc_probe: PASS BW16 arc separated at tau 1/4000 and 1/30, overlaps at 1/10 "
      "(min excess %.4g, %.4g, %.4g)" % tuple(float(best[t]) for t in (Fraction(1, 4000), Fraction(1, 30), Fraction(1, 10))))
