"""A4 against the sharp degree-4 moment-only bound: does A4's gain come from tr Q?

Audit: AUDIT-014. Backs, in VERDICTS.md: "Higher moments A4 (014): N1. Beats every degree-4
moment-only bound on a structured class (6 to 10 percent of fresh samples) ... Its gain comes from tr Q."

A4 uses the moments S1..S4 together with tr Q and tr Q^3. The sharp classical one-sided degree-4 bound
uses S1..S4 only (a linear program, from check_moment_bounds_a2.py). This script compares the two on
the sibling team's two explicit matrices and on fresh "weak" family samples (check_a4_vs_a2.py). In the
cases where A4 beats max(R_H4 - b, R_opt) in integer terms, the sharp moment-only bound must not
reach A4's integer. The LP is float on a grid, so integers are read with a 1e-6 margin. The LP must never
exceed the exact n+(H_perp).

Needs: Python 3 with numpy and SciPy, exactlib_b.py, check_a4_vs_a2.py, check_moment_bounds_a2.py.
Run (about 3 minutes for the default size): python3 -I -B check_a4_vs_sharp_deg4.py [seed] [count]
Defaults: seed 303, count 300. The seed is printed.
Exit code 0 only if the LP never exceeds n+(H_perp), A4 beats the LP on at least one case, and
the LP reaches A4's integer in none of the cases where A4 beats the other bounds.
"""
import json
import math
import os
import random
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import exactlib_b as L  # noqa: E402
import check_a4_vs_a2 as T  # noqa: E402
from check_moment_bounds_a2 import lp_sharp  # noqa: E402


def lp_cert(ev, b):
    v = lp_sharp(list(ev))
    return v, max(0, math.ceil(v - b - 1e-6))


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 303
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    print("seed:", seed, "count:", count)
    out = {}
    UQ = L.eye(4)
    st = T.stats(L.from_eigs(UQ, [F(0), F(1), F(1, 10), F(1, 10)]), L.from_eigs(UQ, [F(10), F(0), F(0), F(0)]), UQ, 1)
    v, c = lp_cert(st["ev"], 1)
    out["team_diag"] = {"lp_minus_b": round(v - 1, 6), "lp_cert": c, "npHp": st["npHp"]}
    eps = F(1, 200)
    K = L.zeros(4)
    K[0][1] = (eps, eps); K[1][0] = (-eps, eps); K[0][2] = (F(0), eps); K[2][0] = (F(0), eps)
    I = L.eye(4)
    U = L.mmul(L.msub(I, K), L.inv(L.madd(I, K)))
    P = L.mmul(L.mmul(U, L.from_eigs(I, [F(0), F(1), F(1, 6), F(1, 6)])), L.dag(U))
    st = T.stats(P, L.from_eigs(I, [F(3), F(0), F(0), F(0)]), I, 1)
    v, c = lp_cert(st["ev"], 1)
    out["team_noncommuting"] = {"lp_minus_b": round(v - 1, 6), "lp_cert": c, "npHp": st["npHp"]}
    rng = random.Random(seed)
    cnt = dict(cases=0, a4_wins_over_h4_ropt=0, lp_ge_a4_on_those=0, a4_gt_lp=0, lp_gt_a4=0, lp_above_npHp=0)
    for _ in range(count):
        P, Q, UQ, b = T.gen("weak", rng)
        st = T.stats(P, Q, UQ, b)
        sm = T.summarize(st, rng=rng)
        v, c = lp_cert(st["ev"], b)
        ce = sm["cert"]
        cnt["cases"] += 1
        cnt["lp_above_npHp"] += (v - b) > st["npHp"] + 1e-6
        if ce["A4"] > max(ce["H4"], ce["R_opt"]):
            cnt["a4_wins_over_h4_ropt"] += 1
            cnt["lp_ge_a4_on_those"] += c >= ce["A4"]
        cnt["a4_gt_lp"] += ce["A4"] > c
        cnt["lp_gt_a4"] += c > ce["A4"]
    out["weak_family"] = cnt
    print(json.dumps(out, indent=1))
    w = out["weak_family"]
    ok = (w["lp_above_npHp"] == 0 and w["a4_gt_lp"] > 0 and w["lp_ge_a4_on_those"] == 0
          and w["a4_wins_over_h4_ropt"] > 0)
    common.finish("check_a4_vs_sharp_deg4", ok,
                  "A4 beats max(A2,R_opt) in %d of %d weak samples, sharp degree-4 LP reaches A4's integer in %d of them, "
                  "A4 above LP in %d, LP above n_plus in %d"
                  % (w["a4_wins_over_h4_ropt"], w["cases"], w["lp_ge_a4_on_those"], w["a4_gt_lp"], w["lp_above_npHp"]))


if __name__ == "__main__":
    main()
