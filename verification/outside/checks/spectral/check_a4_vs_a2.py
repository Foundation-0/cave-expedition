"""Does bound A4 (weighted quartic Weyl) certify a larger integer than A2 and R_opt? Exact check.

Audit: AUDIT-014 (A4 of spectral-inertia higher_moments.py). Backs, in VERDICTS.md: "Higher moments
A4 (014): N1. Beats every degree-4 moment-only bound on a structured class (6 to 10 percent of fresh
samples), never on 1,200 generic samples. Its gain comes from tr Q."

A4 is fully optimised over its five parameters in floating point (L-BFGS-B from several starts), then
rounded to rationals and evaluated exactly. Any rational parameters give a valid bound, so rounding
cannot break soundness. Every exact bound is compared with the exact n+(H_perp). It checks:
(a) the two explicit matrices of the sibling team, where A4 certifies 3 and ceil R_opt = ceil(R_H4 - b) = 2;
(b) 300 fresh matrices in each of three families (general, regime1, weak = one large isolated Q+ eigenvalue
with P weakly coupled): no bound ever exceeds n+(H_perp);
(c) A4 beats max(R_H4 - b, R_opt) in integer terms in 0 generic and 0 regime1 samples, and in some weak ones.
It does not import the sibling team's code.

Needs: Python 3 with numpy and SciPy, exactlib_b.py.
Run (about 3 minutes for the default size): python3 -I -B check_a4_vs_a2.py [seed] [count_per_family]
Defaults: seed 101, count 300. The seed is printed. Results move slightly with the SciPy version.
Exit code 0 only if there are no bound violations, no A4 win in the generic and regime1 families, and
A4 wins in at least one weak sample and on both explicit matrices.
"""
import json
import math
import os
import random
import sys
from fractions import Fraction as F

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import exactlib_b as L  # noqa: E402


def stats(P, Q, UQ, b):
    n = len(P)
    H = L.madd(P, Q)
    S = L.moments(H, 6)
    t = L.tr(Q)
    T3 = L.tr(L.mmul(L.mmul(Q, Q), Q))
    u = L.tr(P)
    if n - b > 0:
        Up = [[UQ[i][b + j] for j in range(n - b)] for i in range(n)]
        npHp = L.inertia(L.mmul(L.mmul(L.dag(Up), H), Up))[0]
    else:
        npHp = 0
    Hf = np.array([[complex(float(x[0]), float(x[1])) for x in r] for r in H])
    ev = np.linalg.eigvalsh(Hf)
    return dict(S=S, t=t, T3=T3, u=u, b=b, npHp=npHp, ev=ev, rkP=L.rank(P))


def a4_opt(st, rng):
    S, t, T3, b = st["S"], st["t"], st["T3"], st["b"]
    Sf = {k: float(v) for k, v in S.items()}
    tf, T3f = float(t), float(T3)
    scale = max(1.0, abs(Sf[2]) ** 0.5)

    def neg(x):
        s, p, g1, g3, lk = x
        kap = math.exp(lk)
        beta = s + g3 / p
        alpha = 1 - (beta * beta - s * s + kap) / (2 * p)
        lam0 = (s + g1 - alpha * beta) / kap
        M = alpha * alpha + kap * lam0 * lam0
        v = 2 * s * Sf[1] - (s * s + 2 * p) * Sf[2] + 2 * s * p * Sf[3] - p * p * Sf[4] + 2 * g1 * tf + 2 * g3 * T3f - b * M
        return -v

    starts = []
    h4v, a = L.hankel_best(S, 2)
    starts.append([float(a[0]), max(float(a[1]), 1e-6), 0.0, 0.0, math.log(1e-6)])
    pos = sorted([e for e in st["ev"] if e > 1e-9], reverse=True)
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            m1, m2 = pos[i], pos[j]
            s0, p0 = (m1 + m2) / (m1 * m2), 1 / (m1 * m2)
            for mu in (m1, 2 * m1, pos[0]):
                q = 1 - s0 * mu + p0 * mu * mu
                if mu > s0 / (2 * p0) and q > 0:
                    starts.append([s0, p0, q * (2 * p0 * mu - s0), 0.0, math.log(2 * p0 * q)])
    for _ in range(6):
        starts.append([rng.uniform(0, 3) / scale, rng.uniform(0.01, 2) / scale ** 2, rng.uniform(0, 5),
                       rng.uniform(0, 1) / scale ** 2, rng.uniform(-6, 4)])
    # exact limit candidate: H4 optimum with gamma = 0 and a tiny exact kappa (A4 -> H4 - b as kappa -> 0)
    # (when p* = 0 use p = 1e-12 and kappa = p^3 so that kappa * lam0^2 -> 0)
    sp = (a[0], a[1]) if a[1] > 0 else (a[0], F(1, 10 ** 12))
    best_exact = L.a4_value(S, t, T3, b, sp[0], sp[1], F(0), F(0), min(F(1, 10 ** 30), sp[1] ** 3))
    for x0 in starts:
        try:
            r = minimize(neg, x0, method="L-BFGS-B",
                         bounds=[(0, None), (1e-12, None), (0, None), (0, None), (-30, 30)])
            xs = [r.x] + ([np.array(x0)])
        except (ValueError, OverflowError, FloatingPointError, ZeroDivisionError):
            continue
        for x in xs:
            s, p, g1, g3, lk = x
            if not all(map(math.isfinite, x)):
                continue
            try:
                kap = math.exp(lk)
            except OverflowError:
                continue
            fr = [F(s).limit_denominator(10 ** 6), F(p).limit_denominator(10 ** 9), F(g1).limit_denominator(10 ** 6),
                  F(g3).limit_denominator(10 ** 9), F(kap).limit_denominator(10 ** 12)]
            if fr[1] <= 0 or fr[4] <= 0:
                continue
            v = L.a4_value(S, t, T3, b, *fr)
            if best_exact is None or v > best_exact:
                best_exact = v
    return best_exact


def gen(family, rng):
    n = rng.randint(3, 6)
    if family == "general":
        b = rng.randint(0, n - 1)
        r = rng.randint(1, n)
        UP, UQ = L.cayley(n, rng), L.cayley(n, rng)
        pe = [F(rng.randint(1, 6), rng.randint(1, 3)) for _ in range(r)] + [F(0)] * (n - r)
        qe = [F(rng.randint(1, 6), rng.randint(1, 3)) for _ in range(b)] + \
             [-F(rng.randint(0, 4), rng.randint(1, 3)) for _ in range(n - b)]
    elif family == "regime1":
        b = rng.randint(1, n - 1)
        r = rng.randint(1, n)
        UP, UQ = L.cayley(n, rng), L.cayley(n, rng)
        pe = [F(rng.randint(1, 3), rng.randint(2, 5)) for _ in range(r)] + [F(0)] * (n - r)
        qe = [F(rng.randint(8, 12), 2) for _ in range(b)] + [-F(rng.randint(0, 1), 10) for _ in range(n - b)]
    else:  # "weak": team-style -- Q_+ on its own coordinates, P spread, small complex rotation
        b = rng.randint(1, min(2, n - 2))
        r = n - b
        UQ = L.eye(n)
        eps = F(1, rng.choice([20, 50, 100, 200]))
        K = L.zeros(n)
        for i in range(n):
            for j in range(i + 1, n):
                a = (eps * rng.randint(-1, 1), eps * rng.randint(-1, 1))
                K[i][j] = a
                K[j][i] = (-a[0], a[1])
        I = L.eye(n)
        UP = L.mmul(L.msub(I, K), L.inv(L.madd(I, K)))
        big = F(rng.randint(2, 10))
        pe = [F(0)] * b + [F(1)] + [F(1, rng.randint(2, 10)) for _ in range(r - 1)]
        qe = [big] * b + [F(0)] * (n - b)
    P = L.from_eigs(UP, pe)
    Q = L.from_eigs(UQ, qe)
    return P, Q, UQ, b


def team_examples():
    out = {}
    # diagonal witness: Q = diag(10,0,0,0), P = diag(0,1,1/10,1/10), b = 1
    UQ = L.eye(4)
    P = L.from_eigs(UQ, [F(0), F(1), F(1, 10), F(1, 10)])
    Q = L.from_eigs(UQ, [F(10), F(0), F(0), F(0)])
    st = stats(P, Q, UQ, 1)
    out["diag"] = summarize(st, extra_a4=peak(st, F(11), F(10), F(10)))
    # non-commuting: P2 = diag(0,1,1/6,1/6) rotated by Cayley(K), eps = 1/200; Q2 = diag(3,0,0,0)
    eps = F(1, 200)
    K = L.zeros(4)
    K[0][1] = (eps, eps)
    K[1][0] = (-eps, eps)
    K[0][2] = (F(0), eps)
    K[2][0] = (F(0), eps)
    I = L.eye(4)
    U = L.mmul(L.msub(I, K), L.inv(L.madd(I, K)))
    P = L.mmul(L.mmul(U, L.from_eigs(I, [F(0), F(1), F(1, 6), F(1, 6)])), L.dag(U))
    Q = L.from_eigs(I, [F(3), F(0), F(0), F(0)])
    st = stats(P, Q, I, 1)
    out["noncommuting_eps_1_200"] = summarize(st, extra_a4=peak(st, F(7), F(6), F(3)))
    return out


def peak(st, s, p, mu):
    q = 1 - s * mu + p * mu * mu
    return L.a4_value(st["S"], st["t"], st["T3"], st["b"], s, p, q * (2 * p * mu - s), F(0), 2 * p * q)


def summarize(st, extra_a4=None, rng=None):
    S, b = st["S"], st["b"]
    h4 = L.hankel_best(S, 2)[0] - b
    h6 = L.hankel_best(S, 3)[0] - b
    R = L.ropt(st["u"], st["t"], S[2], b)
    a4 = a4_opt(st, rng or random.Random(1))
    if extra_a4 is not None and (a4 is None or extra_a4 > a4):
        a4 = extra_a4
    return dict(npHp=st["npHp"], rkP=st["rkP"], R_opt=float(R), H4mb=float(h4), H6mb=float(h6), A4=float(a4),
                cert=dict(R_opt=L.cert_int(R), H4=L.cert_int(h4), H6=L.cert_int(h6), A4=L.cert_int(a4)),
                viol=[k for k, v in (("R_opt", R), ("H4", h4), ("H6", h6), ("A4", a4)) if v > st["npHp"]])


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 101
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    print("seed:", seed, "count_per_family:", count, "(the optimiser restart rng is fixed: Random(1))")
    rng = random.Random(seed)
    res = {"team_examples": team_examples()}
    for fam in ("general", "regime1", "weak"):
        c = dict(cases=0, viol=0, a4_gt_h4=0, a4_gt_max_h4_ropt=0, a4_gt_h6=0, h6_gt_a4=0, h4_gt_ropt=0,
                 a4_lt_h4_real=0, room_left=0, examples=[])
        for _ in range(count):
            P, Q, UQ, b = gen(fam, rng)
            st = stats(P, Q, UQ, b)
            sm = summarize(st, rng=rng)
            ce = sm["cert"]
            c["cases"] += 1
            c["viol"] += len(sm["viol"]) > 0
            c["a4_gt_h4"] += ce["A4"] > ce["H4"]
            c["a4_gt_max_h4_ropt"] += ce["A4"] > max(ce["H4"], ce["R_opt"])
            c["a4_gt_h6"] += ce["A4"] > ce["H6"]
            c["h6_gt_a4"] += ce["H6"] > ce["A4"]
            c["h4_gt_ropt"] += ce["H4"] > ce["R_opt"]
            c["a4_lt_h4_real"] += sm["A4"] < sm["H4mb"] - 1e-9
            c["room_left"] += max(ce.values()) < st["npHp"]
            if ce["A4"] > max(ce["H4"], ce["R_opt"]) and len(c["examples"]) < 3:
                c["examples"].append(sm)
        res[fam] = c
    print(json.dumps(res, indent=1, default=str))
    team_ok = all(v["cert"]["A4"] > max(v["cert"]["H4"], v["cert"]["R_opt"]) and not v["viol"]
                  for v in res["team_examples"].values())
    viol = sum(res[f]["viol"] for f in ("general", "regime1", "weak"))
    gen_wins = res["general"]["a4_gt_max_h4_ropt"] + res["regime1"]["a4_gt_max_h4_ropt"]
    weak_wins = res["weak"]["a4_gt_max_h4_ropt"]
    ok = team_ok and viol == 0 and gen_wins == 0 and weak_wins > 0
    common.finish("check_a4_vs_a2", ok,
                  "violations=%d A4_beats_A2_and_R_opt: generic=%d of %d, weak=%d of %d, team_examples=%s"
                  % (viol, gen_wins, 2 * count, weak_wins, count, "both" if team_ok else "NOT both"))


if __name__ == "__main__":
    main()
