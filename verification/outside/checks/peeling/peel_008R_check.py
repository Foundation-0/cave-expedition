#!/usr/bin/env python3
"""Independent statement-level check of AUDIT-008R (shares no code with the expedition). Backs VERDICTS.md
section 1 (008R identities hold) and section 4 item 2 (docs/09 Claim 9, Claim 10 transfer: parts a, b and the
energy split hold, part c fails on an exact cone example).

R1  Gauge shift = diagonal similarity: K_q(c + dH) = D^{-1} K_q(c) D, D = diag(q^H), symbolic in q.
    Also: whether D^{-1} K D is a Doob transform in the strict sense (stochastic) - it is not in general.
    Fixed seed 99, 40 random graphs.
R2  Accidental single-q lumpability: exact strong-lumpability defect of the 4-state unnormalised kernel
    and of the 5-state row-normalised Boltzmann kernel, as rational functions of q; roots in (0, 1);
    tropical (min-plus) defect of the same quotient.
R3  Cubic-Bregman Pythagoras: symbolic three-point identity; exact random tests on/off the e-flat family
    (negative control; fixed seed 4242); the two quoted cone numbers; and which parts of loom Claim 10
    transfer (a, b, energy split transfer; c fails, shown on an exact cone example).

Needs: Python 3, SymPy. No other input.
Run:   python3 -I -B peel_008R_check.py
Time:  about 5 seconds.
Last line: PEELING_008R_CHECK OK ... ; exit 0 only if every check held.
"""
from __future__ import annotations

import itertools
import json
import random
import sys
from fractions import Fraction as F

import sympy as sp

q = sp.Symbol("q", positive=True)
OUT: dict = {}


def need(c, m):
    if not c:
        raise RuntimeError("CHECK FAILED: " + m)


# ----------------------------------------------------------------- R1
def r1(seed=99, trials=40):
    rng = random.Random(seed)
    stoch_hits = 0
    for t in range(trials):
        n = rng.randint(3, 7)
        E = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 4)) for _ in range(rng.randint(n, 3 * n))]
        H = [rng.randint(-3, 5) for _ in range(n)]  # any integer potential, consistency not needed
        K = sp.zeros(n, n)
        Kr = sp.zeros(n, n)
        for u, v, c in E:
            K[u, v] += q ** c
            Kr[u, v] += q ** (c + H[v] - H[u])
        D = sp.diag(*[q ** h for h in H])
        need(sp.simplify(D.inv() * K * D - Kr) == sp.zeros(n, n), "diagonal similarity fails")
        for k in (1, 2, 3):
            need(sp.simplify((K ** k).trace() - (Kr ** k).trace()) == 0, "trace fails")
        # Doob in the strict sense needs row sums 1 for some q; test at q=1/2
        rs = [sum(Kr.subs(q, sp.Rational(1, 2))[i, j] for j in range(n)) for i in range(n)]
        if all(r == 1 for r in rs):
            stoch_hits += 1
    # fractional reduced costs break the "suboptimal entries <= q" convergence bound
    frac = {"c_red": "1/2", "q": "1/4", "entry": str(sp.Rational(1, 4) ** sp.Rational(1, 2)), "exceeds_q": True}
    need(sp.Rational(1, 4) ** sp.Rational(1, 2) > sp.Rational(1, 4), "frac check")
    return {"random_graphs": trials, "identity_holds_all": True, "stochastic_after_transform": stoch_hits,
            "fractional_reduced_cost_note": frac}


# ----------------------------------------------------------------- R2
def lump_defect(P, pi):
    """Sum over fibers X, target fibers Y, pairs u,w in X of (P(u->Y) - P(w->Y))^2 (zero iff strongly lumpable)."""
    n = P.shape[0]
    blocks = sorted(set(pi))
    tot = 0
    for X in blocks:
        mem = [s for s in range(n) if pi[s] == X]
        for Y in blocks:
            sums = [sum(P[u, v] for v in range(n) if pi[v] == Y) for u in mem]
            for a, b in itertools.combinations(sums, 2):
                tot += (a - b) ** 2
    return sp.factor(sp.simplify(tot))


def minplus_defect(n, goals, E, pi):
    import heapq
    qn = max(pi) + 1
    qe = {}
    for u, v, c in E:
        if pi[u] != pi[v]:
            k = (pi[u], pi[v])
            qe[k] = min(qe.get(k, c), c)
    h = [None] * qn
    pq = [(0, pi[g]) for g in goals]
    for _, a in pq:
        h[a] = 0
    heapq.heapify(pq)
    while pq:
        d, b = heapq.heappop(pq)
        if d != h[b]:
            continue
        for (a, bb), w in qe.items():
            if bb == b and (h[a] is None or d + w < h[a]):
                h[a] = d + w
                heapq.heappush(pq, (d + w, a))
    dfx = {}
    for s in range(n):
        if s in goals:
            continue
        dfx[s] = min(c + h[pi[v]] - h[pi[s]] for u, v, c in E if u == s)
    return dfx


def r2():
    res = {}
    # 4-state unnormalised
    E4 = [(0, 0, 1), (3, 3, 1), (1, 0, 1), (2, 0, 2), (2, 3, 2)]
    pi4 = [0, 1, 1, 0]
    K = sp.zeros(4, 4)
    for u, v, c in E4:
        K[u, v] += q ** c
    d4 = lump_defect(K, pi4)
    roots4 = [r for r in sp.solve(sp.numer(sp.together(d4)), q) if r.is_positive and r < 1]
    res["unnormalised_4state"] = {"defect": str(d4), "roots_in_(0,1)": [str(r) for r in roots4],
                                  "minplus_defect": minplus_defect(4, [0, 3], E4, pi4)}
    need(roots4 == [sp.Rational(1, 2)], "4-state root")
    # 5-state row-normalised
    E5 = [(0, 0, 1), (3, 3, 1), (4, 0, 3), (1, 0, 1), (1, 4, 1), (2, 0, 2), (2, 3, 2), (2, 4, 1)]
    pi5 = [0, 1, 1, 0, 2]
    K = sp.zeros(5, 5)
    for u, v, c in E5:
        K[u, v] += q ** c
    P = sp.Matrix(5, 5, lambda i, j: sp.simplify(K[i, j] / sum(K[i, :])))
    d5 = lump_defect(P, pi5)
    roots5 = [r for r in sp.solve(sp.numer(sp.together(d5)), q) if r.is_positive and r < 1]
    gap = sp.simplify(sum(P[1, v] for v in (0, 3)) - sum(P[2, v] for v in (0, 3)))
    md = minplus_defect(5, [0, 3], E5, pi5)
    res["boltzmann_5state"] = {"defect": str(d5), "gap_1_minus_2_to_Y": str(sp.factor(gap)),
                               "roots_in_(0,1)": [str(r) for r in roots5], "minplus_defect": md}
    need(roots5 == [sp.Rational(1, 2)], "5-state root")
    need(sp.simplify(gap - (1 - 2 * q) / (2 * (2 * q + 1))) == 0, "gap formula")
    need(max(md.values()) == 1, "min-plus defect 1")
    # limit q -> 0: P_q tends to the uniform choice among cheapest moves; is the limit chain lumpable?
    P0 = P.applyfunc(lambda e: sp.limit(e, q, 0))
    res["boltzmann_5state"]["limit_q0_defect"] = str(lump_defect(P0, pi5))
    res["boltzmann_5state"]["limit_q0_row1"] = [str(x) for x in P0.row(1)]
    res["boltzmann_5state"]["limit_q0_row2"] = [str(x) for x in P0.row(2)]
    return res


# ----------------------------------------------------------------- R3
def DF(p, r):
    return sum(F(1, 3) * (a - b) ** 2 * (a + 2 * b) for a, b in zip(p, r))


def r3(seed=4242):
    out = {}
    m = 4
    P = sp.symbols("p0:4")
    Qs = sp.symbols("q0:4")
    R = sp.symbols("r0:4")
    Fs = lambda x: sum(xi ** 3 for xi in x) / 3
    Ds = lambda a, b: Fs(a) - Fs(b) - sum(2 * 0 + bi ** 2 * (ai - bi) for ai, bi in zip(a, b))
    three = sp.expand(Ds(P, R) - Ds(P, Qs) - Ds(Qs, R) - sum((pi - qi) * (qi ** 2 - ri ** 2) for pi, qi, ri in zip(P, Qs, R)))
    need(three == 0, "three-point identity")
    out["three_point_identity_symbolic"] = "D(p||r) = D(p||q) + D(q||r) + <p-q, gradF(q)-gradF(r)>  (holds identically)"
    # closed-form check of D
    need(sp.expand(Ds(P, Qs) - sum(sp.Rational(1, 3) * (a - b) ** 2 * (a + 2 * b) for a, b in zip(P, Qs))) == 0, "D closed form")
    # quoted numbers
    c1 = (DF([4, 5, 4], [3, 4, 5]), DF([3, 4, 5], [5, 12, 13]), DF([4, 5, 4], [5, 12, 13]))
    need(c1 == (F(37, 3), F(1276), F(3865, 3)), "cone 1 numbers")
    # second cone: q*=[8,15,17], q_adapt=[7,24,25], p = q* + t[1,1,-1], find t with D(p||q*) = 369
    t = sp.Symbol("t")
    sols = [s for s in sp.solve(sp.Eq(sum(sp.Rational(1, 3) * (tt) ** 2 * (a + tt + 2 * a) for a, tt in zip([8, 15, 17], [t, t, -t])), 369), t) if s.is_real]
    found = []
    for s in sols:
        if s.is_rational:
            p = [F(str(8 + s)), F(str(15 + s)), F(str(17 - s))]
            if all(x > 0 for x in p):
                found.append(([str(x) for x in p], str(DF(p, [8, 15, 17])), str(DF([8, 15, 17], [7, 24, 25])), str(DF(p, [7, 24, 25]))))
    out["cone2_numbers"] = found
    need(any(f[1] == "369" and f[2] == "9413/3" and f[3] == "10520/3" for f in found), "cone 2 numbers")
    # random exact tests: q*, q' on cone family {q3^2 = q1^2+q2^2} via Pythagorean triples, p = q* + t[1,1,-1]
    rng = random.Random(seed)
    triples = []
    for a in range(1, 12):
        for b in range(a + 1, 12):
            if sp.gcd(a, b) == 1 and (a - b) % 2:
                triples.append((b * b - a * a, 2 * a * b, a * a + b * b))
    on_ok = off_fail = 0
    for _ in range(60):
        q1, q2 = rng.sample(triples, 2)
        k1, k2 = rng.randint(1, 3), rng.randint(1, 3)
        qs = [F(k1 * x) for x in q1]
        qa = [F(k2 * x) for x in q2]
        tt = F(rng.randint(-5, 5), rng.randint(1, 4))
        p = [qs[0] + tt, qs[1] + tt, qs[2] - tt]
        if min(p) <= 0:
            continue
        if DF(p, qa) == DF(p, qs) + DF(qs, qa):
            on_ok += 1
        else:
            raise RuntimeError("on-family Pythagoras failed")
        # off-family control: perturb q_adapt off the cone
        qo = [qa[0], qa[1], qa[2] + 1]
        if DF(p, qo) != DF(p, qs) + DF(qs, qo):
            off_fail += 1
    out["random_cone_tests"] = {"on_family_identity_holds": on_ok, "off_family_identity_fails": off_fail}
    # Claim 10 transfer: (c) fails. p and p' differ by a vector in col(Phi); outside reading changes.
    Phi = sp.Matrix([[1, 0], [0, 1], [1, 1]])
    qs, qs2 = [F(3), F(4), F(5)], [F(5), F(12), F(13)]
    p = [F(4), F(5), F(4)]
    p2 = [qs2[0] + F(1, 3), qs2[1] + F(1, 3), qs2[2] - F(1, 3)]
    diff = sp.Matrix([sp.Rational(str(a - b)) for a, b in zip(p2, p)])
    sol = Phi.solve_least_squares(diff)
    need(Phi * sol == diff, "p2 - p in col(Phi)")
    for pp, qq in ((p, qs), (p2, qs2)):
        need(Phi.T * sp.Matrix([sp.Rational(str(a - b)) for a, b in zip(pp, qq)]) == sp.zeros(2, 1), "stationarity")
    w = [1, 1, -1]
    read1 = sum(wi * (a - b) for wi, a, b in zip(w, p, qs))
    read2 = sum(wi * (a - b) for wi, a, b in zip(w, p2, qs2))
    out["claim10c_counterexample"] = {"p": [str(x) for x in p], "p_prime": [str(x) for x in p2],
                                      "p_prime_minus_p_in_colPhi_coeffs": [str(x) for x in sol],
                                      "outside_audit_reading_before": str(read1), "after": str(read2)}
    need(read1 != read2, "expected (c) to fail")
    return out


def main():
    print("seeds 99 (R1), 4242 (R3)")
    OUT["R1"] = r1()
    OUT["R2"] = r2()
    OUT["R3"] = r3()
    print(json.dumps(OUT, indent=1, default=str))
    r1o, r2o, r3o = OUT["R1"], OUT["R2"], OUT["R3"]
    need(r1o["identity_holds_all"] and r1o["stochastic_after_transform"] == 0, "R1 headline")
    need(r2o["unnormalised_4state"]["roots_in_(0,1)"] == ["1/2"], "R2 4-state root")
    need(r2o["boltzmann_5state"]["roots_in_(0,1)"] == ["1/2"], "R2 5-state root")
    tests = r3o["random_cone_tests"]
    need(tests["on_family_identity_holds"] > 0 and tests["off_family_identity_fails"] > 0, "R3 control")
    cx = r3o["claim10c_counterexample"]
    need((cx["outside_audit_reading_before"], cx["after"]) == ("3", "1"), "R3 claim 10c reading 3 -> 1")
    print(f"PEELING_008R_CHECK OK: R1 {r1o['random_graphs']} graphs 0 stochastic; R2 root only q = 1/2; "
          f"R3 identity on {tests['on_family_identity_holds']} on-family, fails on "
          f"{tests['off_family_identity_fails']} off-family; claim 10(c) 3 -> 1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
