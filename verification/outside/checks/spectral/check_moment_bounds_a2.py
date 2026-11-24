"""Classical moment bounds against the higher-moment bound A2: counterexample and gap check.

Audit: AUDIT-014 (bound A2 of spectral-inertia higher_moments.py). Backs, in VERDICTS.md: "Higher
moments A2 (014): N0 as a theorem, N1 for the closed form. Classical one-sided moment method. The
team's one-sided sign constraint is the correct form. The remark it would be reduced to is wrong for
indefinite matrices." It does not use the sibling team's code.

Part 1 (exact, Fractions). The bound 1 - Lambda_m(0), with Lambda_m the Christoffel function at 0,
is a lower bound for the nonzero-eigenvalue fraction, not for the positive one. Counterexamples:
G = -I_3 gives 1 - Lambda_1(0) = 1 with n+ = 0, and diag(1,-1) gives 1 - Lambda_2(0) = 1 with
n+/d = 1/2. So "the sharp version is a Christoffel function" is false for n+.
Part 2 (float linear program, comparison only). On 200 random mixed-sign spectra it compares the
single-square degree-4 bound A2 (R_H4) with the sharp degree-4 one-sided moment bound
max{ sum f(h_i) : deg f <= 4, f <= 0 on (-inf,0], f <= 1 on (0,inf) }. A2 is a restricted, explicitly
solvable case: the LP is never below it and never above n+.

Needs: Python 3 with numpy and SciPy (HiGHS linear programming).
Run (about 10 seconds): python3 -I -B check_moment_bounds_a2.py
Fixed seed 5. Exit code 0 only if both counterexamples hold, the LP is never below A2 (minus 1e-6),
never above n+ (plus 1e-6), and exceeds A2 by more than 0.1 in at least one case.
"""
import json
import os
import random
import sys
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import exactlib_b as L  # noqa: E402


def christoffel_bound(mom, m):
    """1 - min{ (1/d) tr q(G)^2 : deg q <= m, q(0) = 1 }, exact, from normalised moments mom[k]."""
    # q = 1 + sum_{k=1}^m c_k x^k ; minimise 1 + 2 sum c_k mom[k] + sum c_j c_k mom[j+k]
    A = [[mom[j + k] for k in range(1, m + 1)] for j in range(1, m + 1)]
    y = [-mom[j] for j in range(1, m + 1)]
    c = L._solve(A, y)
    if c is None:
        return "singular moment matrix (fewer atoms than m)"
    val = 1 + 2 * sum(c[k - 1] * mom[k] for k in range(1, m + 1)) + sum(
        c[j - 1] * c[k - 1] * mom[j + k] for j in range(1, m + 1) for k in range(1, m + 1))
    return 1 - val


def lp_sharp(ev, deg=4):
    X = max(10.0, 4 * max(abs(e) for e in ev))
    grid = np.concatenate([np.linspace(-X, 0, 4000), np.linspace(1e-9, X, 4000)])
    V = np.vstack([grid ** k for k in range(deg + 1)]).T
    ub = np.where(grid <= 0, 0.0, 1.0)
    # leading coefficient <= 0 so f -> -inf at both ends (needed for f <= 1 on all of R)
    A_ub = np.vstack([V, np.eye(deg + 1)[deg]])
    b_ub = np.concatenate([ub, [0.0]])
    mvec = np.array([sum(e ** k for e in ev) for k in range(deg + 1)])
    r = linprog(-mvec, A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * (deg + 1), method="highs")
    return -r.fun if r.status == 0 else None


def main():
    print("seed: 5")
    out = {}
    # (1) exact counterexamples to "n_+(G)/d >= 1 - Lambda_m(0)"
    for name, ev in (("G=-I_3", [F(-1)] * 3), ("G=diag(1,-1)", [F(1), F(-1)]), ("G=diag(2,-1,-1)", [F(2), F(-1), F(-1)])):
        d = len(ev)
        mom = {k: sum(e ** k for e in ev) / d for k in range(0, 7)}
        npos = sum(e > 0 for e in ev)
        out[name] = {"n_plus_over_d": str(F(npos, d)),
                     "1-Lambda_1(0)": str(christoffel_bound(mom, 1)),
                     "1-Lambda_2(0)": str(christoffel_bound(mom, 2)) if d >= 2 else None,
                     "team_A2_m2_value_over_d": str(L.hankel_best({k: mom[k] * d for k in range(1, 7)}, 2)[0] / d),
                     "rank_over_d": str(F(sum(e != 0 for e in ev), d))}
    # (2) single-square A2 (m=2) vs sharp degree-4 one-sided LP on random spectra
    rng = random.Random(5)
    gaps = []
    for _ in range(200):
        n = rng.randint(3, 8)
        ev = [rng.choice([-1, 1]) * rng.uniform(0.05, 4) for _ in range(n)]
        evF = [F(e).limit_denominator(1000) for e in ev]
        S = {k: sum(e ** k for e in evF) for k in range(1, 7)}
        h4 = float(L.hankel_best(S, 2)[0])
        lp = lp_sharp([float(e) for e in evF])
        npos = sum(e > 0 for e in evF)
        if lp is None:
            continue
        gaps.append((lp - h4, h4, lp, npos))
    gaps.sort(reverse=True)
    out["A2_vs_sharp_deg4_LP"] = {
        "cases": len(gaps),
        "lp_exceeds_h4_by_0.01": sum(g[0] > 0.01 for g in gaps),
        "lp_exceeds_h4_by_0.1": sum(g[0] > 0.1 for g in gaps),
        "lp_below_h4_minus_1e-6": sum(g[0] < -1e-6 for g in gaps),
        "lp_above_npos": sum(g[2] > g[3] + 1e-6 for g in gaps),
        "top3_(gap,h4,lp,npos)": [[round(x, 4) for x in g[:3]] + [g[3]] for g in gaps[:3]],
        "integer_gain_cases": sum(max(0, -int(-(g[2] - 1e-6) // 1)) > max(0, -int(-g[1] // 1)) for g in gaps),
    }
    print(json.dumps(out, indent=1))
    g = out["A2_vs_sharp_deg4_LP"]
    ce1 = F(out["G=-I_3"]["1-Lambda_1(0)"]) > F(out["G=-I_3"]["n_plus_over_d"])
    ce2 = F(out["G=diag(1,-1)"]["1-Lambda_2(0)"]) > F(out["G=diag(1,-1)"]["n_plus_over_d"])
    ok = (ce1 and ce2 and g["lp_below_h4_minus_1e-6"] == 0 and g["lp_above_npos"] == 0
          and g["lp_exceeds_h4_by_0.1"] > 0)
    common.finish("check_moment_bounds_a2", ok,
                  "christoffel_counterexamples=%s lp_exceeds_A2_by_0.1=%d of %d lp_below_A2=%d lp_above_n_plus=%d"
                  % ("hold" if (ce1 and ce2) else "FAIL", g["lp_exceeds_h4_by_0.1"], g["cases"],
                     g["lp_below_h4_minus_1e-6"], g["lp_above_npos"]))


if __name__ == "__main__":
    main()
