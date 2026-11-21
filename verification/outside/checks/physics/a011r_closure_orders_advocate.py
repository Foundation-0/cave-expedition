#!/usr/bin/env python3
"""Advocate check of the AeST slow-mode closure residual (AUDIT-011R).

Backs: VERDICTS section 3, row "AUDIT-011R headline". Under the host protocol
the closure leaves 0.55 percent (H0) and 0.37 percent (H3). The 0.37 percent is
not a closure error. It equals the gap between two exact trajectories: the
protocol's slow preparation and the preparation placed on the H3 graph. Started
on its own manifold, H3 tracks to 0.00008 percent (k = 24). On fast-contaminated
preparations no closure that sees only (delta, theta) can pass the 1 percent gate.

Method: the host's slow-mode probe.py supplies only the four-state matrix M(a),
the protocol preparations and the observables. The closure chain
H_0 = -F^-1 C, H_(n+1) = F^-1 (dH_n/dt + H_n (A + B H_n) - C) is written here,
with the time derivative from a cubic spline. The k values are 6, 9, 12, 18, 24
at q_i = 0.01 and k = 6, 24 at q_i = 0.003, 0.03, 0.1. Nothing is random.

Needs: Python 3, numpy, scipy; a clone of Foundation-0/gravity (draft pull request 30).
Run:   python3 -I -B a011r_closure_orders_advocate.py /path/to/gravity
       (or set GRAVITY_REPO; add --verbose for the full table)
Time:  about 1 minute.
Exit:  0 only if every check holds.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

NAME = "a011r_closure_orders_advocate"
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
P = GRAV / "research/aest-response-gate-20261112/slow-mode/probe.py"
if not P.is_file():
    raise SystemExit("Missing " + str(P) + ". Is the clone at the commit listed in README.md?")
spec = importlib.util.spec_from_file_location("hostprobe", P)
hp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hp)


def need(c, m):
    if not c:
        raise SystemExit("CHECK FAILED: " + m)


def H_chain(k, nmax, a_grid):
    hp.KVAL = k
    Ms = np.array([hp.matrix(a) for a in a_grid])
    A, B, C, F = Ms[:, :2, :2], Ms[:, :2, 2:], Ms[:, 2:, :2], Ms[:, 2:, 2:]
    aH = np.array([a * hp.bg(a)[-1] for a in a_grid])
    Hs = [np.array([-np.linalg.solve(F[i], C[i]) for i in range(len(a_grid))])]
    defects = []
    for n in range(nmax + 1):
        Hn = Hs[-1]
        sp = CubicSpline(a_grid, Hn, axis=0)
        Hdot = sp(a_grid, 1) * aH[:, None, None]
        R = C + np.einsum("tij,tjk->tik", F, Hn) - Hdot - np.einsum("tij,tjk->tik", Hn, A + np.einsum("tij,tjk->tik", B, Hn))
        inner = slice(20, len(a_grid) - 20)
        defects.append(float(np.max(np.linalg.norm(np.linalg.solve(F[inner], R[inner]), axis=(1, 2))
                                    / np.linalg.norm(Hn[inner], axis=(1, 2)))))
        if n < nmax:
            rhs = Hdot + np.einsum("tij,tjk->tik", Hn, A + np.einsum("tij,tjk->tik", B, Hn)) - C
            Hs.append(np.linalg.solve(F, rhs))
    return [CubicSpline(a_grid, H, axis=0) for H in Hs], defects


def run_k(k, qi, nmax=3):
    hp.QI = qi
    hp.KVAL = k
    slow_state, contaminants, _ = hp.modes()
    grid = np.linspace(1, 2, 2001)
    fund = hp.fundamental(grid, tol=1e-11)
    zero = hp.fundamental(grid, "zero", 1e-11)
    x0 = hp.DELTA * slow_state
    ref0 = hp.observables(grid, np.einsum("tij,j->ti", zero, x0[:2]))
    scales = np.max(np.abs(ref0), axis=1)
    a_fine = np.linspace(0.97, 2.03, 3181)
    Hsp, defects = H_chain(k, nmax, a_fine)

    def reduced(Hn):
        def f(a, s):
            M = hp.matrix(a)
            return ((M[:2, :2] + M[:2, 2:] @ Hn(a)) @ s) / (a * hp.bg(a)[-1])
        sol = solve_ivp(f, (1, 2), x0[:2], t_eval=grid, method="DOP853", rtol=1e-11, atol=1e-22)
        need(sol.success, "reduced ode")
        return hp.observables(grid, sol.y.T)

    preps = [(0.0, 0.0, x0)] + [(eta, ph, x0 + hp.DELTA * eta * w) for eta in (0.001, 0.01, 0.1) for ph, w in contaminants]
    exact_obs = [(eta, ph, hp.observables(grid, np.einsum("tij,j->ti", fund, xx))) for eta, ph, xx in preps]
    out = {"k": k, "qi": qi, "invariance_defect_rel": defects, "orders": {}}
    for n, Hn in enumerate(Hsp):
        red = reduced(Hn)
        errs = {}
        for eta, ph, ob in exact_obs:
            e = float(np.max(np.max(np.abs(ob - red), axis=1) / scales))
            errs.setdefault(str(eta), []).append(e)
        xinv = np.concatenate([x0[:2], Hn(1.0) @ x0[:2]])
        obinv = hp.observables(grid, np.einsum("tij,j->ti", fund, xinv))
        out["orders"]["H%d" % n] = {
            "protocol_eta0": errs["0.0"][0],
            "own_invariant_ic": float(np.max(np.max(np.abs(obinv - red), axis=1) / scales)),
        }
    # Lower bound for any closure that sees only (delta, theta): phases 0 and pi give exact outputs
    # base + d and base - d from the same retained data, so one prediction has error >= max |d| / scale.
    base = exact_obs[0][2]
    lb = {}
    for eta, ph, ob in exact_obs[1:]:
        d = float(np.max(np.max(np.abs(ob - base), axis=1) / scales))
        lb[str(eta)] = max(lb.get(str(eta), 0.0), d)
    out["any_two_variable_closure_lower_bound"] = lb
    H3 = Hsp[-1](1.0)
    xinv3 = np.concatenate([x0[:2], H3 @ x0[:2]])
    ob3 = hp.observables(grid, np.einsum("tij,j->ti", fund, xinv3))
    out["exact_protocol_ic_vs_exact_H3_ic"] = float(np.max(np.max(np.abs(base - ob3), axis=1) / scales))
    return out


def main():
    res = []
    for k in (6.0, 9.0, 12.0, 18.0, 24.0):
        res.append(run_k(k, 0.01))
    for qi in (0.003, 0.03, 0.1):
        for k in (6.0, 24.0):
            try:
                res.append(run_k(k, qi))
            except (AssertionError, SystemExit, np.linalg.LinAlgError) as exc:
                res.append({"k": k, "qi": qi, "error": repr(exc)})

    for r in res:
        check("error" not in r, "run failed at q_i=%g k=%g" % (r["qi"], r["k"]))
    ok = [r for r in res if "error" not in r]
    base = [r for r in ok if r["qi"] == 0.01]
    check(len(base) == 5, "expected 5 runs at q_i = 0.01")
    for r in base:
        o = r["orders"]
        check(0.0054 <= o["H0"]["protocol_eta0"] <= 0.0060, "H0 not 0.55 to 0.59 percent at k=%g" % r["k"])
        check(0.00370 <= o["H3"]["protocol_eta0"] <= 0.00378, "H3 not 0.371 to 0.377 percent at k=%g" % r["k"])
        check(0.00372 <= r["exact_protocol_ic_vs_exact_H3_ic"] <= 0.00378, "IC gap not 0.372 to 0.377 percent at k=%g" % r["k"])
        check(abs(o["H3"]["protocol_eta0"] - r["exact_protocol_ic_vs_exact_H3_ic"]) < 0.00002,
              "H3 residual does not equal the IC gap at k=%g" % r["k"])
        check(o["H3"]["own_invariant_ic"] <= 0.000013, "H3 on its own manifold above 0.0013 percent at k=%g" % r["k"])
        d = r["invariance_defect_rel"]
        check(all(d[i] > d[i + 1] for i in range(len(d) - 1)), "invariance defect not decreasing with order at k=%g" % r["k"])
        check(r["any_two_variable_closure_lower_bound"]["0.001"] > 0.01,
              "lower bound for contaminated preparations not above the gate at k=%g" % r["k"])
    k24 = [r for r in base if r["k"] == 24.0][0]
    check(7e-7 <= k24["orders"]["H3"]["own_invariant_ic"] <= 9e-7, "H3 own-manifold error at k=24 is not 0.00008 percent")
    for r in ok:
        if r["qi"] == 0.03:
            check(0.0110 <= r["orders"]["H3"]["protocol_eta0"] <= 0.0115, "q_i=0.03 H3 not 1.11 to 1.14 percent")
            check(0.0111 <= r["exact_protocol_ic_vs_exact_H3_ic"] <= 0.0115, "q_i=0.03 IC gap not 1.12 to 1.14 percent")
        if r["qi"] == 0.1:
            check(0.0345 <= r["orders"]["H3"]["protocol_eta0"] <= 0.0390, "q_i=0.1 H3 not 3.46 to 3.85 percent")
            check(0.0360 <= r["exact_protocol_ic_vs_exact_H3_ic"] <= 0.0390, "q_i=0.1 IC gap not 3.63 to 3.86 percent")
            check(r["orders"]["H3"]["own_invariant_ic"] < 0.002, "q_i=0.1 H3 own-manifold error above 0.2 percent")

    if "--verbose" in sys.argv:
        print(json.dumps(res, indent=1, sort_keys=True))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    h3 = [r["orders"]["H3"]["protocol_eta0"] for r in base]
    gap = [r["exact_protocol_ic_vs_exact_H3_ic"] for r in base]
    print("RESULT %s: PASS %d of %d checks; q_i=0.01 H3 residual %.3f%% to %.3f%% equals the preparation gap %.3f%% to %.3f%%; "
          "H3 on its own manifold %.5f%% at k=24" % (NAME, COUNT[0], COUNT[0], 100 * min(h3), 100 * max(h3), 100 * min(gap), 100 * max(gap),
                                                    100 * k24["orders"]["H3"]["own_invariant_ic"]))


if __name__ == "__main__":
    main()
