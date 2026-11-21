#!/usr/bin/env python3
"""Independent check of the AeST Schur identity and slow-mode closure (AUDIT-011R).

Backs: VERDICTS section 1 row "AeST Schur identity and slow-mode closure (011R)"
and the section 3 repair of the AUDIT-011R headline (0.55 and 0.37 percent under
the host protocol, not 0.00008 percent).

Part S (SymPy, exact): the Schur complement of the Minkowski H_2 written in the
host derivation, compared with the stated law, plus an inertia table by exact
Descartes sign counts. Part G: the host's own slow-mode probe.py (loaded
unmodified from the gravity clone) supplies the four-state system, the protocol
preparation and the gate metric. Two closures are written here from scratch:
quasi-static elimination (qsa) and the closed-form Helmholtz pressure (helm).
They are scored against the host's 1 percent gate at the protocol k values, at
k values not reported, at other background q_i, and on the fast-contaminated
preparations. Nothing is random.

Needs: Python 3, numpy, scipy, sympy; a clone of Foundation-0/gravity at the
commit in README.md (draft pull request 30).
Run:   python3 -I -B a011r_schur_closure_independent.py /path/to/gravity
       (or set GRAVITY_REPO instead of the argument; add --verbose for details)
Time:  about 1 to 2 minutes.
Exit:  0 only if every check holds.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

NAME = "a011r_schur_closure_independent"
GATE = 0.01
FAILS = []
COUNT = [0]


def check(cond, msg):
    COUNT[0] += 1
    if not cond:
        FAILS.append(msg)


def repo_path():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    value = args[0] if args else os.environ.get("GRAVITY_REPO", "")
    if not value or not Path(value).is_dir():
        raise SystemExit("Pass the path of a Foundation-0/gravity clone as the first argument or set GRAVITY_REPO.")
    return Path(value)


GRAV = repo_path()


def part_s():
    k = sp.symbols("k", positive=True)
    chi, p, P = sp.symbols("chi p P")
    H2 = p**2 / 16 + (p + P) ** 2 / (4 * k**2) - (p + P) * chi + 3 * k**2 * chi**2 - P**2 / (8 * k**2)
    v = [chi, p, P]
    M = sp.hessian(H2, v)  # H2 = 1/2 v^T M v
    Mff = M[:2, :2]
    MfP = M[:2, 2]
    S = sp.simplify(M[2, 2] - (MfP.T * Mff.inv() * MfP)[0, 0])
    sol = sp.solve([sp.diff(H2, chi), sp.diff(H2, p)], [chi, p], dict=True)[0]
    Hmin = sp.simplify(H2.subs(sol))
    KB, lam, Kpp, Q = 1, 1, 4, 1
    r = k**2
    GAA = (Kpp * Q**2 * (1 + lam) - (2 - KB) * lam * r) / (Kpp * Q**2 * (1 + lam) + (2 + KB * lam) * r)
    target = -GAA * P**2 / (8 * k**2)
    out = {
        "S_P": str(S),
        "Hmin_minus_target": str(sp.simplify(Hmin - target)),
        "Hmin_minus_half_S_P2": str(sp.simplify(Hmin - S * P**2 / 2)),
        "S_P_minus_expected": str(sp.simplify(S - (k**2 - 8) / (12 * k**4 + 32 * k**2))),
        "minors": [str(sp.factor(m)) for m in (M[:1, :1].det(), M[:2, :2].det(), M.det())],
        "Mff_pd_for_all_k": bool(sp.simplify(Mff.det()).is_positive) and bool(Mff[0, 0].is_positive),
        "inertia_pos_neg_zero": {},
    }
    for rv in (7, 8, 9, 2, 100):
        Mr = M.subs(k, sp.sqrt(rv))
        lam_ = sp.symbols("lam_")
        cp = sp.Poly(Mr.charpoly(lam_).as_expr(), lam_)
        zero = 0
        while cp.eval(0) == 0:
            cp = sp.Poly(sp.cancel(cp.as_expr() / lam_), lam_)
            zero += 1

        def sc(cs):
            cs = [c for c in cs if c != 0]
            return sum(1 for x, y in zip(cs, cs[1:]) if x * y < 0)

        pos = sc(cp.all_coeffs())  # all roots real (symmetric matrix): Descartes is exact
        neg = sc(cp.compose(sp.Poly(-lam_, lam_)).all_coeffs())
        out["inertia_pos_neg_zero"][rv] = [int(pos), int(neg), 3 - int(pos) - int(neg), str(GAA.subs(k, sp.sqrt(rv)))]
    return out


def load_host():
    path = GRAV / "research/aest-response-gate-20261112/slow-mode/probe.py"
    if not path.is_file():
        raise SystemExit("Missing " + str(path) + ". Is the clone at the commit listed in README.md?")
    spec = importlib.util.spec_from_file_location("host_slow_probe", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def reduced_rhs(h, a, x, kind):
    """Two-variable closure in the host coordinates (delta, theta)."""
    if kind == "qsa":
        M = h.matrix(a)  # host 4x4, coordinates (delta, theta, chi, Z)
        A, B, C, F = M[:2, :2], M[:2, 2:], M[2:, :2], M[2:, 2:]
        return (A - B @ np.linalg.solve(F, C)) @ x
    Q, Kp, R, W, H = h.bg(a)
    r = h.KVAL**2 / a**2
    ca = Kp / (4 * Q)
    w = 2 * (Q - 1) ** 2 / R
    M2 = 4.0 * Q * Q * 2.0 / 3.0
    delta, theta = x
    Phi = -(R * delta + 3 * H * W * theta) / (2 * r)
    pressure = ca * R * delta * M2 / (M2 + r)
    Phidot = -H * Phi + W * theta / 2
    dd = 3 * H * (w * delta - pressure / R) + 3 * W / R * Phidot - r * W / R * theta
    td = 3 * H * ca * theta + pressure / W + Phi
    return np.array([dd, td])


def gate_errors(h, k, qi=0.01, etas=(0.0,)):
    h.QI = qi
    h.KVAL = k
    slow_state, contaminants, _ = h.modes()
    grid = np.linspace(1, 2, 2001)
    fund = h.fundamental(grid, tol=1e-11)
    zero = h.fundamental(grid, "zero", 1e-11)
    init = h.DELTA * slow_state
    ref0 = h.observables(grid, np.einsum("tij,j->ti", zero, init[:2]))
    scales = np.max(abs(ref0), axis=1)
    res = {}
    preps = [(0.0, 0.0, init)]
    for eta in etas:
        if eta > 0:
            preps += [(eta, ph, init + h.DELTA * eta * wv) for ph, wv in contaminants]
    for kind in ("qsa", "helm"):
        sol = solve_ivp(lambda a, x: reduced_rhs(h, a, x, kind) / (a * h.bg(a)[-1]), (1, 2), init[:2],
                        t_eval=grid, method="DOP853", rtol=1e-11, atol=1e-22)
        pred = h.observables(grid, sol.y.T)
        worst = {}
        for eta, ph, x0 in preps:
            obs = h.observables(grid, np.einsum("tij,j->ti", fund, x0))
            e = np.max(abs(obs - pred), axis=1) / scales
            worst[eta] = max(worst.get(eta, 0.0), float(max(e)))
        res[kind] = worst
    return res


def main():
    out = {"part_S": part_s()}
    s = out["part_S"]
    check(s["S_P_minus_expected"] == "0", "Schur complement differs from (k^2-8)/(12k^4+32k^2)")
    check(s["Hmin_minus_target"] == "0", "direct minimum differs from the stated G_AA law")
    check(s["Hmin_minus_half_S_P2"] == "0", "direct minimum differs from S_P P^2/2")
    check(s["Mff_pd_for_all_k"], "fast block not positive definite")
    expected = {7: [2, 1, 0, "1/29"], 8: [2, 0, 1, "0"], 9: [3, 0, 0, "-1/35"], 2: [2, 1, 0, "3/7"], 100: [3, 0, 0, "-23/77"]}
    check(s["inertia_pos_neg_zero"] == expected, "inertia table at k^2 = 7, 8, 9, 2, 100 differs")

    h = load_host()
    rows = []
    for k in (6.0, 9.0, 12.0, 18.0, 24.0, 3.5, 4.5, 7.5, 15.0, 33.0, 48.0):
        etas = (0.0, 0.001, 0.01, 0.1) if k in (6.0, 24.0) else (0.0,)
        rows.append({"k": k, "qi": 0.01, "worst_err": gate_errors(h, k, 0.01, etas=etas)})
    for qi in (0.003, 0.03, 0.1):
        for k in (6.0, 24.0):
            try:
                rows.append({"k": k, "qi": qi, "worst_err": gate_errors(h, k, qi)})
            except AssertionError as exc:
                rows.append({"k": k, "qi": qi, "host_probe_refused": repr(exc)})
    out["part_G"] = rows

    base = [r for r in rows if r["qi"] == 0.01]
    q_worst = max(r["worst_err"]["qsa"][0.0] for r in base)
    q_best = min(r["worst_err"]["qsa"][0.0] for r in base)
    h_worst = max(r["worst_err"]["helm"][0.0] for r in base)
    h_best = min(r["worst_err"]["helm"][0.0] for r in base)
    check(len(base) == 11, "expected 11 k values at q_i = 0.01")
    check(q_worst < GATE and h_worst < GATE, "a closure fails the 1 percent gate on the protocol preparation")
    check(0.0045 <= q_best and q_worst <= 0.0060, "quasi-static error band is not about 0.46 to 0.59 percent")
    check(0.0018 <= h_best and h_worst <= 0.0048, "Helmholtz error band is not about 0.19 to 0.47 percent")
    for r in base:
        for eta in (0.001, 0.01, 0.1):
            if eta in r["worst_err"]["qsa"]:
                check(r["worst_err"]["qsa"][eta] > GATE and r["worst_err"]["helm"][eta] > GATE,
                      "closure passes on a fast-contaminated preparation at k=%g eta=%g" % (r["k"], eta))
    by = {(r["qi"], r["k"]): r for r in rows}
    for key, r in by.items():
        check("worst_err" in r, "host probe refused q_i=%g k=%g" % key)
    for k in (6.0, 24.0):
        if (0.003, k) in by and "worst_err" in by[(0.003, k)]:
            e = by[(0.003, k)]["worst_err"]
            check(e["qsa"][0.0] < GATE and e["helm"][0.0] < GATE, "q_i=0.003: a closure fails")
        if (0.03, k) in by and "worst_err" in by[(0.03, k)]:
            e = by[(0.03, k)]["worst_err"]
            check(e["qsa"][0.0] > GATE and e["helm"][0.0] < GATE, "q_i=0.03: expected quasi-static fail, Helmholtz pass")
        if (0.1, k) in by and "worst_err" in by[(0.1, k)]:
            e = by[(0.1, k)]["worst_err"]
            check(e["qsa"][0.0] > GATE and e["helm"][0.0] > GATE, "q_i=0.1: expected both to fail")

    if "--verbose" in sys.argv:
        print(json.dumps(out, indent=1, default=str))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    print("RESULT %s: PASS %d of %d checks; S_P=(k^2-8)/(12k^4+32k^2) exact; protocol-k worst error qsa %.3f%%, helm %.3f%% (gate 1%%); "
          "all fast-contaminated preparations fail" % (NAME, COUNT[0], COUNT[0], 100 * q_worst, 100 * h_worst))


if __name__ == "__main__":
    main()
