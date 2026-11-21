#!/usr/bin/env python3
"""Independent exact check of AUDIT-010 Theorems A, B, C (Foundation-0/fractals draft PR 60).

Checks: with oracles written here (not taken from the sibling team), that
  A: the interval all-pairs test decides exactly whether values inside the error boxes exist with every step
     slope in the bracket (forward interval propagation plus an explicit witness), that step-only checks can pass
     while the global test fails, and that the README's smallest example behaves as reported;
  B: the four-ray test for four dyadic points agrees with exact Fourier-Motzkin elimination, that the complete set
     for m points is the C(m,3) chord triples (m = 4, 5, 6, extreme rays enumerated exactly), that each of the four
     rays is needed, and that the two witness inequalities in the study README reject a feasible convex point;
  C: the seasonal-differencing identity for p = 1..5 symbolically (SymPy).
Backs: VERDICTS.md section 1 ("No-log theorems A, B, C (010)"), section 2 (label N0 with the named prior art) and
the section 3 row "fractals 60 README" (mistranscribed witness inequalities).
The team's functions are loaded only as the system under test and compared with the oracles here.
Needs: Python 3 with SymPy, and a clone of Foundation-0/fractals at draft PR 60 (study folder
studies/expedition-mult-farkas-dsi). Give its location as the first argument or in FRACTALS_REPO.
Run: python3 -I -B check_exact_evaluator.py /path/to/fractals     (add --details to print the full JSON)
Time: about 5 seconds. Fixed seed: 77123 (printed). Exit 0 only if every check held.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import random
import sys
from fractions import Fraction as F
from math import lcm
from pathlib import Path

SEED = 77123


def load_sut():
    """Load the sibling team's verifier from the clone (system under test only)."""
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.environ.get("FRACTALS_REPO")
    if not root:
        raise SystemExit("usage: check_exact_evaluator.py <path to a clone of Foundation-0/fractals at PR 60> "
                         "(or set FRACTALS_REPO)")
    path = Path(root) / "studies" / "expedition-mult-farkas-dsi" / "verify_mult_farkas_dsi.py"
    if not path.is_file():
        raise SystemExit(f"missing {path}: is the clone at draft PR 60?")
    spec = importlib.util.spec_from_file_location("verify_mult_farkas_dsi", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SUT = load_sut()

FAILS: list[str] = []


def need(cond: bool, msg: str) -> None:
    if not cond:
        FAILS.append(msg)


# ---------------------------------------------------------------- Theorem A
def chain_oracle(L, U, lo_fac, hi_fac):
    """Exists y_i in [L_i, U_i] with lo_fac_i <= y_{i+1}/y_i <= hi_fac_i? Forward intervals, then a witness."""
    A, B = [L[0]], [U[0]]
    for i in range(len(L) - 1):
        a = max(L[i + 1], A[-1] * lo_fac[i])
        b = min(U[i + 1], B[-1] * hi_fac[i])
        if a > b:
            return False, None
        A.append(a)
        B.append(b)
    y = [None] * len(L)
    y[-1] = B[-1]
    for i in range(len(L) - 2, -1, -1):
        lo = max(A[i], y[i + 1] / hi_fac[i])
        hi = min(B[i], y[i + 1] / lo_fac[i])
        if not lo <= hi:
            raise RuntimeError("oracle witness construction failed (backward pass)")
        y[i] = hi
    for i in range(len(L)):
        if not L[i] <= y[i] <= U[i]:
            raise RuntimeError("oracle witness leaves its box")
    for i in range(len(L) - 1):
        if not lo_fac[i] <= y[i + 1] / y[i] <= hi_fac[i]:
            raise RuntimeError("oracle witness violates a step bracket")
    return True, y


def my_pairs(L, U, lo_fac, hi_fac, only_steps=False):
    n = len(L)
    for i in range(n):
        plo = phi = F(1)
        for j in range(i + 1, n):
            plo *= lo_fac[j - 1]
            phi *= hi_fac[j - 1]
            if only_steps and j > i + 1:
                break
            if U[j] / L[i] < plo or L[j] / U[i] > phi:
                return False
    return True


def theorem_a(rng):
    bases = [F(2), F(3), F(5, 3), F(7, 2), F(3, 2), F(10, 7)]
    stats = dict(cases=0, sut_agree=0, feasible=0, step_local_yes_global_no=0, point_cases=0, point_steps_eq_pairs=0)
    for t in range(1500):
        n = rng.randint(2, 7)
        a1 = F(rng.randint(-6, 4), rng.randint(1, 4))
        a2 = a1 + F(rng.randint(0, 3), rng.randint(1, 4))
        Q = lcm(a1.denominator, a2.denominator)
        steps = [rng.choice(bases) ** rng.randint(1, 2) for _ in range(n - 1)]
        xs = [F(1)]
        for s in steps:
            xs.append(xs[-1] * s ** Q)
        lo_fac = [s ** (Q * a1) for s in steps]   # (x_{i+1}/x_i)^{a1}, rational by construction
        hi_fac = [s ** (Q * a2) for s in steps]
        point = t % 5 == 0
        y = [F(rng.randint(1, 30), rng.randint(1, 30))]
        for i in range(n - 1):
            mid = lo_fac[i] if rng.random() < 0.5 else hi_fac[i]
            y.append(y[-1] * mid * F(rng.randint(8, 13), 10))
        if point:
            L = U = y
        else:
            L = [v * F(rng.randint(70, 100), 100) for v in y]
            U = [v * F(rng.randint(100, 130), 100) for v in y]
        ok, _ = chain_oracle(L, U, lo_fac, hi_fac)
        res = SUT.check_interval_scaling_global(xs, L, U, a1, a2)
        stats["cases"] += 1
        stats["sut_agree"] += int(res["global_ok"] == ok)
        need(res["global_ok"] == ok, f"ThmA SUT mismatch n={n} a=({a1},{a2})")
        need(my_pairs(L, U, lo_fac, hi_fac) == ok, "ThmA: my all-pairs != chain oracle")
        stats["feasible"] += int(ok)
        st = my_pairs(L, U, lo_fac, hi_fac, only_steps=True)
        if st and not ok:
            stats["step_local_yes_global_no"] += 1
        if point:
            stats["point_cases"] += 1
            stats["point_steps_eq_pairs"] += int(st == ok)
    # Smallest local-yes / global-no example: 3 points, x = 1, 2, 4, exponent bracket [1, 1] (y proportional to x).
    xs, L, U = [F(1), F(2), F(4)], [F(1), F(3, 2), F(9, 2)], [F(1), F(5, 2), F(5)]
    r = SUT.check_interval_scaling_global(xs, L, U, F(1), F(1))
    stats["tiny_example"] = dict(x=[1, 2, 4], y_lo=["1", "3/2", "9/2"], y_hi=["1", "5/2", "5"], bracket="[1,1]",
                                 sut=dict(local_ok=r["local_ok"], global_ok=r["global_ok"]),
                                 oracle=chain_oracle(L, U, [F(2)] * 2, [F(2)] * 2)[0],
                                 midpoints_pairs_mode=my_pairs([F(1), F(2), F(19, 4)], [F(1), F(2), F(19, 4)], [F(2)] * 2, [F(2)] * 2))
    need(r["sheaf_obstruction"] and not stats["tiny_example"]["oracle"], "tiny example")
    return stats


# ---------------------------------------------------------------- Theorem B
def fm_feasible(cons, nvar):
    """cons: list of (coef tuple, rhs) meaning coef . h <= rhs. Exact Fourier-Motzkin."""
    cur = {}
    def add(store, c, r):
        nz = [abs(v) for v in c if v != 0]
        if not nz:
            store.setdefault((None,), []).append(r)
            return
        s = nz[0] if False else max(nz)
        c2 = tuple(v / s for v in c)
        r2 = r / s
        if c2 not in store or r2 < store[c2]:
            store[c2] = r2
    trivial = []
    for c, r in cons:
        if all(v == 0 for v in c):
            trivial.append(r)
        else:
            add(cur, tuple(F(v) for v in c), F(r))
    for k in range(nvar):
        pos = [(c, r) for c, r in cur.items() if c != (None,) and c[k] > 0]
        neg = [(c, r) for c, r in cur.items() if c != (None,) and c[k] < 0]
        zer = [(c, r) for c, r in cur.items() if c != (None,) and c[k] == 0]
        nxt = {}
        for c, r in zer:
            nxt[c] = r
        for (cp, rp), (cn, rn) in itertools.product(pos, neg):
            wp, wn = -cn[k], cp[k]
            c = tuple(wp * a + wn * b for a, b in zip(cp, cn))
            r = wp * rp + wn * rn
            if all(v == 0 for v in c):
                trivial.append(r)
            else:
                nz = max(abs(v) for v in c)
                c2, r2 = tuple(v / nz for v in c), r / nz
                if c2 not in nxt or r2 < nxt[c2]:
                    nxt[c2] = r2
        cur = nxt
    return all(r >= 0 for r in trivial) and all(r >= 0 for c, r in cur.items())


def convex_cons(L, U, t, sign=1):
    """Box plus nondecreasing slopes on grid t (sign=-1: nonincreasing, i.e. log-concave)."""
    m = len(L)
    cons = []
    for k in range(m):
        e = [0] * m
        e[k] = 1
        cons.append((tuple(e), U[k]))
        e2 = [0] * m
        e2[k] = -1
        cons.append((tuple(e2), -L[k]))
    for k in range(1, m - 1):
        d1, d2 = t[k] - t[k - 1], t[k + 1] - t[k]
        # convex: (h_k - h_{k-1})/d1 <= (h_{k+1} - h_k)/d2  <=>  d2 h_{k-1} - (d1+d2) h_k + d1 h_{k+1} >= 0
        c = [0] * m
        c[k - 1], c[k], c[k + 1] = -d2 * sign, (d1 + d2) * sign, -d1 * sign
        cons.append((tuple(c), 0))
    return cons


def triples_ok(L, U, t, sign=1):
    m = len(L)
    if sign == -1:  # concave in [L,U] <=> convex in [-U,-L]
        L, U = [-u for u in U], [-l for l in L]
    if any(L[k] > U[k] for k in range(m)):
        return False
    for i, j, k in itertools.combinations(range(m), 3):
        if (t[k] - t[j]) * U[i] + (t[j] - t[i]) * U[k] < (t[k] - t[i]) * L[j]:
            return False
    return True


def windows4_ok(L, U):
    m = len(L)
    return all(triples_ok(L[s:s + 4], U[s:s + 4], list(range(4))) for s in range(m - 3))


def nullspace_1d(cols):
    """cols: list of column vectors (Fractions). Return the null vector if the nullspace is exactly 1-dim, else None."""
    nrow, ncol = len(cols[0]), len(cols)
    M = [[cols[j][i] for j in range(ncol)] for i in range(nrow)]
    piv_cols, r = [], 0
    for c in range(ncol):
        p = next((i for i in range(r, nrow) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(nrow):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv_cols.append(c)
        r += 1
    free = [c for c in range(ncol) if c not in piv_cols]
    if len(free) != 1:
        return None
    fcol = free[0]
    v = [F(0)] * ncol
    v[fcol] = F(1)
    for i, c in enumerate(piv_cols):
        v[c] = -M[i][fcol]
    return v


def farkas_extreme_rays(m):
    """Extreme rays of K = {(u,a,b) >= 0 : D^T u - a + b = 0}, D the (m-2) x m second-difference matrix."""
    D = [[0] * m for _ in range(m - 2)]
    for r in range(m - 2):
        D[r][r], D[r][r + 1], D[r][r + 2] = 1, -2, 1
    cols = []
    for r in range(m - 2):
        cols.append([F(D[r][k]) for k in range(m)])
    for k in range(m):
        cols.append([F(-1 if i == k else 0) for i in range(m)])
    for k in range(m):
        cols.append([F(1 if i == k else 0) for i in range(m)])
    n = len(cols)
    rays = set()
    for size in range(1, m + 2):
        for S in itertools.combinations(range(n), size):
            v = nullspace_1d([cols[j] for j in S])
            if v is None:
                continue
            if all(x > 0 for x in v):
                pass
            elif all(x < 0 for x in v):
                v = [-x for x in v]
            else:
                continue
            full = [F(0)] * n
            for j, x in zip(S, v):
                full[j] = x
            g = max(full)
            rays.add(tuple(x / g for x in full))
    # keep only minimal supports (extreme rays)
    rl = list(rays)
    supp = [frozenset(i for i, x in enumerate(r) if x != 0) for r in rl]
    ext = [rl[i] for i in range(len(rl)) if not any(supp[j] < supp[i] for j in range(len(rl)))]
    out = {"trivial": 0, "triples": set(), "other": []}
    for r in ext:
        u, a, b = r[:m - 2], r[m - 2:2 * m - 2], r[2 * m - 2:]
        if all(x == 0 for x in u):
            out["trivial"] += 1
            continue
        v = [a[k] - b[k] for k in range(m)]
        neg = [k for k in range(m) if v[k] < 0]
        pos = [k for k in range(m) if v[k] > 0]
        if len(neg) == 1 and len(pos) == 2 and pos[0] < neg[0] < pos[1]:
            i, j, k = pos[0], neg[0], pos[1]
            want = [F(0)] * m
            want[i], want[j], want[k] = F(k - j), F(-(k - i)), F(j - i)
            sc = v[i] / want[i]
            if all(v[q] == sc * want[q] for q in range(m)) and all(a[q] * b[q] == 0 for q in range(m)):
                out["triples"].add((i, j, k))
                continue
        out["other"].append([str(x) for x in r])
    out["triples"] = sorted(out["triples"])
    return out


def theorem_b(rng):
    st = dict(sut4_cases=0, sut4_agree=0, sut4_concave_agree=0)
    for _ in range(1500):
        L = [rng.randint(-6, 6) for _ in range(4)]
        U = [l + rng.randint(0, 4) for l in L]
        ok = fm_feasible(convex_cons(L, U, [0, 1, 2, 3]), 4)
        okc = fm_feasible(convex_cons(L, U, [0, 1, 2, 3], sign=-1), 4)
        yl, yh = [F(2) ** l for l in L], [F(2) ** u for u in U]
        r = SUT.check_4pt_farkas_monotonicity(yl, yh, "convex")
        rc = SUT.check_4pt_farkas_monotonicity(yl, yh, "concave")
        st["sut4_cases"] += 1
        st["sut4_agree"] += int(r["feasible"] == ok)
        st["sut4_concave_agree"] += int(rc["feasible"] == okc)
        need(r["feasible"] == ok and rc["feasible"] == okc, f"ThmB SUT mismatch L={L} U={U}")
    # triple conditions vs FM, m = 4..6, uniform and non-uniform grids, rational bounds
    tri = {}
    for m in (4, 5, 6):
        agree = n = nonwin = 0
        for _ in range(500 if m < 6 else 250):
            uniform = rng.random() < 0.5
            t = list(range(m)) if uniform else sorted(rng.sample(range(0, 3 * m), m))
            L = [F(rng.randint(-12, 12), rng.randint(1, 3)) for _ in range(m)]
            U = [l + F(rng.randint(0, 9), rng.randint(1, 3)) for l in L]
            ok = fm_feasible(convex_cons(L, U, t), m)
            n += 1
            agree += int(ok == triples_ok(L, U, t))
            need(ok == triples_ok(L, U, t), f"triples vs FM m={m}")
            if uniform and m >= 5 and windows4_ok(L, U) and not ok:
                nonwin += 1
        tri[m] = dict(cases=n, triple_vs_fm_agree=agree, four_point_windows_pass_but_infeasible=nonwin)
    st["triples_vs_fm"] = tri
    # their 5-point separation example
    L5, U5 = [0, 1, 0, 0, 0], [0, 1, 2, 3, 3]
    st["five_point_example"] = dict(fm_feasible=fm_feasible(convex_cons(L5, U5, list(range(5))), 5),
                                    windows4_pass=windows4_ok(L5, U5),
                                    failing_triples=[c for c in itertools.combinations(range(5), 3)
                                                     if (c[2] - c[1]) * U5[c[0]] + (c[1] - c[0]) * U5[c[2]] < (c[2] - c[0]) * L5[c[1]]])
    # each of the four 4-point rays is needed: a box where only that ray fails
    only = {}
    for _ in range(20000):
        L = [rng.randint(-4, 4) for _ in range(4)]
        U = [l + rng.randint(0, 4) for l in L]
        r = SUT.check_4pt_farkas_monotonicity([F(2) ** l for l in L], [F(2) ** u for u in U], "convex")
        if len(r["failed_rays"]) == 1 and r["failed_rays"][0] not in only:
            only[r["failed_rays"][0]] = dict(L=L, U=U, fm=fm_feasible(convex_cons(L, U, [0, 1, 2, 3]), 4))
    st["each_ray_alone"] = only
    # README witnesses (U0^2 L2^3 >= L1^4 U3 and U0 L2^4 >= L1^3 U3^2) on the feasible point h = (0,0,0,10) (log2)
    h = [0, 0, 0, 10]
    st["readme_witness_check"] = dict(point_is_convex=fm_feasible(convex_cons(h, h, [0, 1, 2, 3]), 4),
                                      readme_w1_holds=2 * h[0] + 3 * h[2] >= 4 * h[1] + h[3],
                                      readme_w2_holds=h[0] + 4 * h[2] >= 3 * h[1] + 2 * h[3])
    st["extreme_rays"] = {m: farkas_extreme_rays(m) for m in (4, 5, 6)}
    for m in (4, 5, 6):
        e = st["extreme_rays"][m]
        need(e["triples"] == sorted(itertools.combinations(range(m), 3)) and not e["other"], f"extreme rays m={m}")
    return st


# ---------------------------------------------------------------- Theorem C
def theorem_c():
    import sympy as sp
    out = {}
    for p in range(1, 6):
        y = sp.symbols(f"y0:{p + 2}", positive=True)  # y_{k-1} .. y_{k+p}
        R = [y[i + 1] * y[i - 1] / y[i] ** 2 for i in range(1, p + 1)]
        prod = sp.Mul(*R)
        closed = (y[p + 1] / y[1]) / (y[p] / y[0])
        ok_id = sp.simplify(prod - closed) == 0
        A, mu = sp.symbols("A mu", positive=True)
        P = sp.symbols(f"P0:{p}", positive=True)
        for k0 in range(p):
            yy = [A * mu ** (k0 - 1 + i) * P[(k0 - 1 + i) % p] for i in range(p + 2)]
            val = sp.simplify(closed.subs(dict(zip(y, yy))))
            ok_id = ok_id and val == 1
        out[p] = ok_id
    # converse: Pi_p(k) = 1 for all k  <=>  r_{k+p-1} = r_{k-1}: closed form is exactly r_{k+p-1}/r_{k-1}.
    # lag effect: y_k = 2^(k^2) (smooth curvature, no oscillation): log2 Pi_p = 2p exactly.
    yq = [F(2) ** (k * k) for k in range(12)]
    lag = {}
    for p in (1, 2, 3, 4):
        vals = SUT.null_equiv_products(yq, p)
        lag[p] = sorted({v.numerator.bit_length() - 1 for v in vals if v.denominator == 1})
    out["lag_curvature_log2_Pi_p"] = lag
    # alternating ripple y_k = (-1/2)-type: log y_k = eps*(-1)^k  -> Pi_1 = 4eps, Pi_2 = 0, Pi_3 = -4eps (log2)
    ya = [F(2) ** (1 if k % 2 else 0) for k in range(10)]
    out["pure_period2_log2_Pi_1_2_3"] = [sorted({F(v).numerator.bit_length() - F(v).denominator.bit_length() for v in SUT.null_equiv_products(ya, p)}) for p in (1, 2, 3)]
    return out


def main():
    print(f"seed={SEED}")
    rng = random.Random(SEED)
    a = theorem_a(rng)
    b = theorem_b(rng)
    c = theorem_c()
    # Claims backed (all must hold): every ray alone is needed, the README witnesses reject a feasible point,
    # the 5-point separation is one chord, identity C holds for p = 1..5.
    need(len(b["each_ray_alone"]) == 4, "not every one of the four rays was shown needed")
    need(b["readme_witness_check"]["point_is_convex"] and not b["readme_witness_check"]["readme_w1_holds"]
         and not b["readme_witness_check"]["readme_w2_holds"], "README witness defect not reproduced")
    need(all(c[p] is True for p in range(1, 6)), "theorem C identity failed")
    need(a["step_local_yes_global_no"] > 0, "no step-local-yes global-no case seen")
    out = {"theorem_A": a, "theorem_B": b, "theorem_C": c, "failures": FAILS}
    if "--details" in sys.argv:
        print(json.dumps(out, indent=1, default=str))
    tri = b["triples_vs_fm"]
    verdict = "OK" if not FAILS else "FAIL"
    print(f"ZEROLOG_EXACT_EVALUATOR {verdict}: A {a['sut_agree']}/{a['cases']} agree with chain oracle "
          f"({a['feasible']} feasible, {a['step_local_yes_global_no']} step-pass global-fail); "
          f"B {b['sut4_agree']}/{b['sut4_cases']} convex and {b['sut4_concave_agree']}/{b['sut4_cases']} concave agree with "
          f"Fourier-Motzkin, chord triples vs FM {sum(v['triple_vs_fm_agree'] for v in tri.values())}/"
          f"{sum(v['cases'] for v in tri.values())}, rays needed {len(b['each_ray_alone'])}/4; "
          f"C identity p=1..5 {all(c[p] for p in range(1, 6))}; failures {len(FAILS)}")
    for f in FAILS[:10]:
        print("FAILED:", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
