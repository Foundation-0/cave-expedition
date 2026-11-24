#!/usr/bin/env python3
"""Check script advocate_trace_slack.py: AUDIT-006 Check 4 (trace-slack law), advocate's re-check with its own code.

Backs: VERDICTS.md section 3, 'continuum 3, trace-slack: exact law -> a certified sufficient condition, worst-case slack 4.8 percent'. The stated threshold 5 tau = 1/360 is below every exact crossing found (6 noise families and a 4000-draw adversarial search), the smallest being (43 - sqrt(1838))/44, about 4.8 percent above it.
Needs: python3 (3.10 or newer), NumPy and SymPy. No network, no clone of any repository, no input files.
Run: python3 -I -B advocate_trace_slack.py
     (also python3 -I -O -B advocate_trace_slack.py and python3 -I -B -W error advocate_trace_slack.py, same output)
Time: about 2 seconds.
Every failed check raises CheckFailed and the script exits 1. On success the last
line printed starts with RESULT: PASS and the exit code is 0.
Seed (fixed, printed in the output): 31337 (NumPy default_rng).

Original description:
Advocate re-check of F5 (team 'trace-slack law' Delta t* = w^2/q = 1/360 in Check 4 of optimal_inertia_rank.py).

Own implementation of the closed form the team states for R_opt (b = 1):
  branch 1 (t > 0, t m >= S, S > t^2): R = (m - t)^2 / (S - t^2);  else R = max(0, m^2/S - 1).
Setting (team's Check 4, by its stated numbers only): n = 5, Q = q v v^T with q = 9/10, P = w (v1 v1^T + v2 v2^T)
with w = 1/20 on orthonormal v, v1, v2; unknown noise 0 <= N <= tau I; M = Q + P + N - tau I; t = q - 5 tau.
Certified (rank of P >= 2) iff R > 1. The 'law' says the threshold is 5 tau = w^2/q = 1/360.

1. Exact crossing (SymPy) for N in a spectral family that commutes with Q and P.
2. Adversarial search over non-commuting N = tau V diag(c) V^T to test whether 5 tau < 1/360 is at least SUFFICIENT.
3. Exact Fraction confirmation at 5 tau = 1/360 of the worst witness found.
Every failed check raises CheckFailed.
"""
import json
import random
import sys
from fractions import Fraction as Fr

import numpy as np
import sympy as sp


class CheckFailed(Exception):
    pass


def need(c, msg):
    if not c:
        raise CheckFailed(msg)


q0, w0 = Fr(9, 10), Fr(1, 20)


def r_opt(m, t, S):
    if S == 0 or m - t <= 0 or m <= 0:
        return 0
    if t > 0 and t * m >= S and S > t * t:
        return (m - t) ** 2 / (S - t * t)
    raw = m * m / S - 1
    return raw if raw > 0 else 0


def exact_family():
    """N = tau * diag(cq, c1, c1, c0, c0) in the eigenbasis (cq along Q, c1 along P, c0 on the rest)."""
    tau = sp.Symbol("tau", positive=True)
    q, w = sp.Rational(9, 10), sp.Rational(1, 20)
    rows = []
    for cq, c1, c0 in [(0, 0, 0), (sp.Rational(1, 2),) * 3, (1, 1, 1), (1, 0, 0), (0, 1, 1), (0, 0, 1)]:
        eig = [q + (cq - 1) * tau, w + (c1 - 1) * tau, w + (c1 - 1) * tau, (c0 - 1) * tau, (c0 - 1) * tau]
        m = sum(eig)
        S = sum(e ** 2 for e in eig)
        t = q - 5 * tau
        expr = sp.expand((m - t) ** 2 - (S - t ** 2))   # R > 1 in branch 1  <=>  expr > 0
        roots = [r for r in sp.solve(sp.Eq(expr, 0), tau) if r.is_real and 0 < r < sp.Rational(1, 100)]
        need(len(roots) >= 1, "no crossing found")
        r0 = min(roots)
        br1 = bool(((t * m - S).subs(tau, r0)) >= 0)
        rows.append({"N_eigs_over_tau(q,P,P,rest,rest)": [str(cq), str(c1), str(c1), str(c0), str(c0)],
                     "T_tau_star_exact": str(sp.nsimplify(5 * r0)), "T_tau_star": float(5 * r0),
                     "ratio_to_law": float(5 * r0 / sp.Rational(1, 360)), "branch1_at_root": br1})
    # idealised model without the -tau I shift and with N = 0 (pure trace slack): root of w^2 + (2w - q) d + d^2
    d = sp.Symbol("d", positive=True)
    ideal = [r for r in sp.solve(sp.Eq(w ** 2 + (2 * w - q) * d + d ** 2, 0), d) if r.is_real]
    rows.append({"idealised_pure_trace_slack_root": str(min(ideal)), "value": float(min(ideal)),
                 "ratio_to_law": float(min(ideal) / sp.Rational(1, 360)),
                 "first_order_in_d": "w^2/(q - 2w) = 1/320"})
    return rows


def float_R(tau, C, Vb):
    q, w = float(q0), float(w0)
    D = np.diag([q, w, w, 0.0, 0.0])
    M = D + tau * C - tau * np.eye(5)
    m = np.trace(M)
    S = float(np.sum(M * M))
    t = q - 5 * tau
    return float(r_opt(m, t, S))


def crossing(C):
    lo, hi = 0.0, 0.01
    if float_R(1e-9, C, None) <= 1:
        return 0.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if float_R(mid, C, None) > 1:
            lo = mid
        else:
            hi = mid
    return 5 * lo


def adversarial(seed=31337, trials=4000):
    rng = np.random.default_rng(seed)
    worst = (1.0, None)
    for i in range(trials):
        A = rng.standard_normal((5, 5))
        V, _ = np.linalg.qr(A)
        c = rng.uniform(0, 1, 5)
        if i % 4 == 0:
            c = (rng.uniform(0, 1, 5) > 0.5).astype(float)
        C = V @ np.diag(c) @ V.T
        x = crossing(C)
        if x < worst[0]:
            worst = (x, C)
    # also rank-one N along Q's own direction
    e0 = np.zeros((5, 5))
    e0[0, 0] = 1.0
    x0 = crossing(e0)
    return worst, x0


def exact_at(C_frac, Ttau):
    tau = Ttau / 5
    D = [[q0 if (i == j == 0) else (w0 if (i == j and i in (1, 2)) else Fr(0)) for j in range(5)] for i in range(5)]
    M = [[D[i][j] + tau * C_frac[i][j] - (tau if i == j else 0) for j in range(5)] for i in range(5)]
    m = sum(M[i][i] for i in range(5))
    S = sum(M[i][j] ** 2 for i in range(5) for j in range(5))
    return r_opt(m, q0 - 5 * tau, S)


def main():
    out = {"exact_family": exact_family()}
    (xw, Cw), x_q = adversarial()
    out["adversarial_min_T_tau_star"] = xw
    out["adversarial_min_ratio_to_law"] = xw * 360
    out["N_equal_tau_along_Q_only_T_tau_star"] = x_q
    out["N_equal_tau_along_Q_only_ratio_to_law"] = x_q * 360
    # exact check of rank-one-along-Q witness at the law's threshold and slightly below
    Cq = [[Fr(int(i == j == 0)) for j in range(5)] for i in range(5)]
    for Ttau in (Fr(1, 360), Fr(1, 400)):
        R = exact_at(Cq, Ttau)
        out[f"exact_R_N_along_Q_at_Ttau_{Ttau}"] = str(R)
    # explicit checks on what the verdict states
    for row in out["exact_family"]:
        ratio = row["ratio_to_law"]
        need(ratio > 1.0, "a crossing at or below the law was found: %r" % (row,))
        if "branch1_at_root" in row:
            need(row["branch1_at_root"], "branch 1 condition fails at a root")
    need(xw > 1.0 / 360, "adversarial search found a crossing below the law")
    worst_exact = (43 - 1838 ** 0.5) / 44
    need(abs(x_q - worst_exact) < 1e-9, "worst-case crossing differs from (43 - sqrt(1838))/44")
    need(Fr(out["exact_R_N_along_Q_at_Ttau_1/360"]) > 1, "exact R at the law, worst witness, is not above 1")
    need(Fr(out["exact_R_N_along_Q_at_Ttau_1/400"]) > 1, "exact R below the law, worst witness, is not above 1")
    print("seed: adversarial=31337")
    print(json.dumps(out, indent=1, default=str))
    print("RESULT: PASS advocate_trace_slack: law 5 tau = 1/360 is sufficient on every case; worst exact crossing %.7f is %.1f percent above it, exact R at the law is 32761/32019 > 1"
          % (x_q, (x_q * 360 - 1) * 100))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckFailed as exc:
        print("RESULT: FAIL (%s)" % exc)
        sys.exit(1)
