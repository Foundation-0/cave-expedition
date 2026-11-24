"""Exact versus float contact distances on the Leech arc at tau = 1e-10 (evaluator check).

The target's Leech basis is extremely ill-conditioned. For the twelve smallest float
contact excesses (squared distance minus 2) along the arc at tau = 1e-10, this script
recomputes the same contacts in exact rationals. Float shows negative excesses, exact
shows positive ones. So any check of the Leech arc must be exact.
Also prints the squared Frobenius norm of the inverse period matrix and the size of the
largest cell vector among all contacts.
Backs: AUDIT-020R, VERDICTS.md and REPORTS.md (Leech basis ill-conditioned, float
distances negative while exact distances positive).
Needs: Python 3, numpy, a clone of the target at the head of draft PR 106
(first argument, or environment variable INCENTRE_LATTICES_PR106).
Run: python3 -I -B eval_leech_arc_probe.py /path/to/incentre-lattices
Time: about 30 seconds. No random numbers are used. Writes no files.
"""
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import team_data, fail, inv_frac, leech_minvecs  # noqa: E402
from eval_velocity_lib import project, gates, neighbours, cayley_L  # noqa: E402

U24 = team_data("U24_WITNESS")
C24 = [[Fraction(x, 4) for x in r] for r in U24]
L24 = [[(2 if i == j else 0) + C24[i][j] for j in range(24)] for i in range(24)]
X0 = [[Fraction(v, 256) for v in r] for r in team_data("X0_24_INT_256")]
X = project(L24, C24, X0)
g1, g2, g3, KX, KE, V = gates(L24, X, Fraction(1, 5), Fraction(2, 25), Fraction(1, 10**10))
Linv = inv_frac(L24)
print("squared Frobenius norm of L^-1: %.3g" % float(sum(x * x for r in Linv for x in r)))
L24x, mv = leech_minvecs()
W = np.array(mv, dtype=np.int64)
P, nb = neighbours(4, L24x, W)
print("largest cell vector entry over all contacts:", max(int(np.abs(m).max()) for _, m in nb))
tau = Fraction(1, 10**10)
Lt = cayley_L(L24, C24, V, tau)
Ltf = np.array([[float(x) for x in r] for r in Lt])
Pf = P.astype(float) / 4
cands = []
for pk in range(48):
    qk, m = nb[pk]
    inter = ~(m == 0).all(axis=1)
    d2 = ((m.astype(float) @ Ltf + Pf[qk] - Pf[pk]) ** 2).sum(axis=1)
    for k in np.argsort(np.where(inter, d2, np.inf))[:3]:
        cands.append((d2[k], pk, int(qk[k]), [int(a) for a in m[k]]))
cands.sort()
rows = []
for d2f, pk, qk, m in cands[:12]:
    p = [Fraction(int(a), 4) for a in P[pk]]
    q = [Fraction(int(a), 4) for a in P[qk]]
    vec = [sum(m[i] * Lt[i][j] for i in range(24)) + q[j] - p[j] for j in range(24)]
    ex = sum(x * x for x in vec) - 2
    rows.append((d2f - 2, ex))
    print("float excess %.4g, exact excess %.4g" % (d2f - 2, float(ex)))

problems = []
if not all(ex > 0 for _, ex in rows):
    problems.append("an exact excess is not positive")
n_float_neg = sum(1 for f, _ in rows if f < 0)
if n_float_neg == 0:
    problems.append("float shows no negative excess, so the contrast is not reproduced")
if problems:
    fail("; ".join(problems))
print("RESULT leech_sheaf/eval_leech_arc_probe: PASS at tau 1e-10 all %d worst contacts are positive in exact "
      "arithmetic (min %.3g), %d of them are negative in float (min %.3g)"
      % (len(rows), float(min(e for _, e in rows)), n_float_neg, min(f for f, _ in rows)))
