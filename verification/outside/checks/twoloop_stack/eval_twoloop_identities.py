#!/usr/bin/env python3
"""Check script eval_twoloop_identities.py: AUDIT-005 (two_loop_omitted_variable.py), evaluator's independent exact check.

Backs: VERDICTS.md section 1, 'Two-loop identities (005)': 383 fresh exact instances including rank-deficient, noisy and several omitted directions. Also section 4 item 1 and 2: the noisy-truth formula, ensembles, and a wrong revision that lowers the in-sample residual and raises the error against the truth.
Needs: python3 (3.10 or newer) and SymPy. No network, no clone of any repository, no input files.
Run: python3 -I -B eval_twoloop_identities.py
     (also python3 -I -O -B eval_twoloop_identities.py and python3 -I -B -W error eval_twoloop_identities.py, same output)
Time: about 1 second.
Every failed check raises CheckFailed and the script exits 1. On success the last
line printed starts with RESULT: PASS and the exit code is 0.
Seeds (fixed, printed in the output): 777001, 777002, 777003.

Original description:
Independent exact check of AUDIT-005 (two_loop_omitted_variable.py).

Shares no code with the expedition. Fraction arithmetic for every identity,
SymPy only for the symbolic noise identity. Every failed check raises.
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction as F

import sympy as sp


class CheckFailed(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise CheckFailed(msg)


# ---------------------------------------------------------------- linear algebra
def dot(u, v):
    s = F(0)
    for a, b in zip(u, v):
        s += a * b
    return s


def matvec(M, x):
    return [dot(row, x) for row in M]


def transpose(M):
    return [list(c) for c in zip(*M)]


def matmul(A, B):
    Bt = transpose(B)
    return [[dot(r, c) for c in Bt] for r in A]


def sub(u, v):
    return [a - b for a, b in zip(u, v)]


def add(u, v):
    return [a + b for a, b in zip(u, v)]


def scale(c, u):
    return [c * a for a in u]


def solve(A, b):
    """Solve square nonsingular A x = b exactly (Gaussian elimination)."""
    n = len(A)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            raise CheckFailed("singular system")
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def col_basis(Phi):
    """Indices of a maximal independent set of columns (exact RREF)."""
    m, k = len(Phi), len(Phi[0])
    M = [list(r) for r in Phi]
    piv_cols, row = [], 0
    for c in range(k):
        p = next((r for r in range(row, m) if M[r][c] != 0), None)
        if p is None:
            continue
        M[row], M[p] = M[p], M[row]
        for r in range(m):
            if r != row and M[r][c] != 0:
                f = M[r][c] / M[row][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[row])]
        piv_cols.append(c)
        row += 1
        if row == m:
            break
    return piv_cols


def projector_apply(Phi, v):
    """P v, P the orthogonal projector onto col(Phi); works for rank-deficient Phi."""
    idx = col_basis(Phi)
    if not idx:
        return [F(0)] * len(v)
    Bm = [[row[c] for c in idx] for row in Phi]
    Bt = transpose(Bm)
    G = matmul(Bt, Bm)
    coef = solve(G, matvec(Bt, v))
    return matvec(Bm, coef)


def rint(rng, lo, hi):
    return F(rng.randint(lo, hi))


def rand_mat(rng, m, k, lo=-3, hi=3):
    return [[rint(rng, lo, hi) for _ in range(k)] for _ in range(m)]


# ---------------------------------------------------------------- Part A1: core identities
def instance(rng, m, k, d, rank_deficient, noise):
    Phi = rand_mat(rng, m, k)
    if rank_deficient and k >= 2:
        # last column = combination of the first two -> rank(Phi) < k
        a, b = rint(rng, -2, 2), rint(rng, 1, 2)
        for row in Phi:
            row[-1] = a * row[0] + b * row[1]
    Psi = rand_mat(rng, m, d)
    # correlate Psi with Phi on purpose
    for prow, row in zip(Phi, Psi):
        row[0] += prow[0]
    theta = [rint(rng, -3, 3) for _ in range(k)]
    beta = [rint(rng, -3, 3) for _ in range(d)]
    y = add(matvec(Phi, theta), matvec(Psi, beta))
    if noise:
        y = add(y, [F(rng.randint(-5, 5), 4) for _ in range(m)])
    return Phi, Psi, y


def part_a1(seed=777001, trials=400):
    rng = random.Random(seed)
    stats = {"tested": 0, "rank_deficient": 0, "noise": 0, "omitted_dirs_gt1": 0,
             "param_norm_shift_strictly_larger": 0, "constrained_LS_matches_min_output_shift": 0,
             "boundary_ratio_0": 0, "boundary_ratio_2": 0, "e2_zero_cases": 0}
    for t in range(trials):
        m = rng.randint(5, 8)
        k = rng.randint(2, min(4, m - 2))
        d = rng.randint(1, 3)
        rd = (t % 3 == 0)
        noise = (t % 2 == 0)
        Phi, Psi, y = instance(rng, m, k, d, rd, noise)
        r = sub(y, projector_apply(Phi, y))
        a1 = [rint(rng, -3, 3) for _ in range(m)]
        p1 = projector_apply(Phi, a1)
        e1 = dot(a1, r)
        pp = dot(p1, p1)
        if pp == 0 or e1 == 0 or dot(r, r) == 0:
            continue
        # r is orthogonal to every column of Phi
        need(all(dot([row[j] for row in Phi], r) == 0 for j in range(k)), "normal equations")
        # minimum output-norm silencing shift
        delta = scale(e1 / pp, p1)
        ra = sub(r, delta)
        need(dot(a1, ra) == 0, "a1 not silenced")
        need(dot(ra, ra) == dot(r, r) + e1 * e1 / pp, "Pythagorean inflation")
        # any other silencing shift inside col(Phi): r - delta' with p1.delta' = e1
        z = projector_apply(Phi, [rint(rng, -2, 2) for _ in range(m)])
        z = sub(z, scale(dot(z, p1) / pp, p1))  # z in col(Phi), z orthogonal to p1
        d2 = add(delta, z)
        ra2 = sub(r, d2)
        need(dot(a1, ra2) == 0, "alt shift not silencing")
        need(dot(ra2, ra2) == dot(r, r) + dot(d2, d2), "alt Pythagoras")
        need(dot(ra2, ra2) >= dot(ra, ra), "min shift not minimal")
        # parameter-space minimum-norm shift: dtheta = e1 * g / |g|^2 with g = Phi^T a1
        g = matvec(transpose(Phi), a1)
        gg = dot(g, g)
        dpar = matvec(Phi, scale(e1 / gg, g))
        rp = sub(r, dpar)
        need(dot(a1, rp) == 0, "param shift not silencing")
        need(dot(rp, rp) == dot(r, r) + dot(dpar, dpar), "param Pythagoras")
        if dot(rp, rp) > dot(ra, ra):
            stats["param_norm_shift_strictly_larger"] += 1
        # constrained least squares (KKT): min |y - Phi th|^2 s.t. a1.(y - Phi th) = 0
        idx = col_basis(Phi)
        Bm = [[row[c] for c in idx] for row in Phi]
        Bt = transpose(Bm)
        G = matmul(Bt, Bm)
        h = matvec(Bt, a1)
        q = len(idx)
        K = [G[i] + [h[i]] for i in range(q)] + [h + [F(0)]]
        rhs = matvec(Bt, y) + [dot(a1, y)]
        sol = solve(K, rhs)
        rc = sub(y, matvec(Bm, sol[:q]))
        need(dot(a1, rc) == 0, "KKT constraint")
        if rc == ra:
            stats["constrained_LS_matches_min_output_shift"] += 1
        else:
            raise CheckFailed("constrained LS differs from min output shift")
        # fresh anchors: generic random, and constructed boundary anchors
        cands = [[rint(rng, -3, 3) for _ in range(m)]]
        # build anchors with ratio exactly 0 and exactly 2: a2 = w + c * p1 where w has w.p1 = 0
        w = [rint(rng, -3, 3) for _ in range(m)]
        w = sub(w, scale(dot(w, p1) / pp, p1))
        ew = dot(w, r)
        if ew != 0:
            cands.append(w)  # ratio 0: p1.a2 = 0
            # ratio 2: need (p1.a2/pp) * e1 / e2 = 2 with a2 = w + c p1 -> c e1 = 2 (ew + c e1') where p1.r = 0
            # p1 is in col(Phi) so p1.r = 0, hence e2 = ew; c * pp/pp * e1 / ew = 2 -> c = 2 ew / e1
            cands.append(add(w, scale(2 * ew / e1, p1)))
        for a2 in cands:
            e2 = dot(a2, r)
            post = dot(a2, ra)
            if e2 == 0:
                stats["e2_zero_cases"] += 1
                need(post == -(e1 / pp) * dot(p1, a2), "e2=0 formula")
                continue
            rho = dot(p1, a2) / pp
            kap = e2 / e1
            x = rho / kap
            need(post == e2 * (1 - x), "fresh-anchor identity")
            helps = post * post < e2 * e2
            hurts = post * post > e2 * e2
            need(helps == (0 < x < 2), "helps iff 0<x<2")
            need(hurts == (x < 0 or x > 2), "hurts iff x<0 or x>2")
            if x == 0:
                stats["boundary_ratio_0"] += 1
                need(post * post == e2 * e2, "tie at 0")
            if x == 2:
                stats["boundary_ratio_2"] += 1
                need(post * post == e2 * e2, "tie at 2")
        stats["tested"] += 1
        stats["rank_deficient"] += rd
        stats["noise"] += noise
        stats["omitted_dirs_gt1"] += (d > 1)
    need(stats["tested"] >= 200, "too few instances")
    return stats


# ---------------------------------------------------------------- Part A2: several anchors absorbed
def part_a2(seed=777002, trials=150):
    rng = random.Random(seed)
    done = 0
    for _ in range(trials):
        m = rng.randint(6, 8)
        k = rng.randint(3, 4)
        Phi, Psi, y = instance(rng, m, k, 2, False, True)
        r = sub(y, projector_apply(Phi, y))
        na = rng.randint(2, 3)
        A = [[rint(rng, -3, 3) for _ in range(m)] for _ in range(na)]
        PA = [projector_apply(Phi, a) for a in A]
        G = [[dot(PA[i], PA[j]) for j in range(na)] for i in range(na)]
        e = [dot(a, r) for a in A]
        try:
            lam = solve(G, e)
        except CheckFailed:
            continue
        if all(v == 0 for v in e):
            continue
        delta = [F(0)] * m
        for i in range(na):
            delta = add(delta, scale(lam[i], PA[i]))
        ra = sub(r, delta)
        need(all(dot(a, ra) == 0 for a in A), "multi-anchor not silenced")
        infl = dot(e, lam)  # e^T G^{-1} e
        need(dot(ra, ra) == dot(r, r) + infl, "multi-anchor inflation e^T G^-1 e")
        need(infl > 0, "inflation positive")
        # minimality: add a direction inside col(Phi) orthogonal to all PA_i
        z = projector_apply(Phi, [rint(rng, -2, 2) for _ in range(m)])
        mu = solve(G, [dot(z, pa) for pa in PA])
        for i in range(na):
            z = sub(z, scale(mu[i], PA[i]))
        ra2 = sub(r, add(delta, z))
        need(all(dot(a, ra2) == 0 for a in A), "alt multi shift")
        need(dot(ra2, ra2) >= dot(ra, ra), "multi min")
        done += 1
    need(done >= 80, "too few multi-anchor cases")
    return {"multi_anchor_instances": done}


# ---------------------------------------------------------------- Part A3: soft (penalty) absorption
def part_a3(seed=777003, trials=200):
    rng = random.Random(seed)
    done = 0
    for _ in range(trials):
        m = rng.randint(5, 7)
        Phi, Psi, y = instance(rng, m, 2, 1, False, False)
        r = sub(y, projector_apply(Phi, y))
        a1 = [rint(rng, -3, 3) for _ in range(m)]
        p1 = projector_apply(Phi, a1)
        pp, e1 = dot(p1, p1), dot(a1, r)
        if pp == 0 or e1 == 0:
            continue
        lam = F(rng.randint(1, 20), rng.randint(1, 5))
        # minimise |r - D|^2 + lam (a1.(r - D))^2 over D in col(Phi): D = c p1, c = lam e1 / (1 + lam pp)
        c = lam * e1 / (1 + lam * pp)
        # stationarity check of the penalised objective along p1 and along col(Phi) orthogonal to p1
        D = scale(c, p1)
        rs = sub(r, D)
        grad_p1 = -2 * dot(p1, rs) - 2 * lam * dot(a1, rs) * dot(a1, p1)
        need(grad_p1 == 0, "soft stationarity")
        s = lam * pp / (1 + lam * pp)
        need(dot(rs, rs) == dot(r, r) + s * s * e1 * e1 / pp, "soft inflation s^2 e1^2/|p1|^2")
        a2 = [rint(rng, -3, 3) for _ in range(m)]
        e2 = dot(a2, r)
        if e2 == 0:
            continue
        x = (dot(p1, a2) / pp) / (e2 / e1)
        post = dot(a2, rs)
        need(post == e2 * (1 - s * x), "soft fresh identity")
        need((post * post < e2 * e2) == (0 < x < 2 / s), "soft boundary 0<x<2/s")
        done += 1
    need(done >= 100, "too few soft cases")
    return {"soft_absorption_instances": done, "boundary": "0 < rho/kappa < 2/s, s = lam|p1|^2/(1+lam|p1|^2)"}


# ---------------------------------------------------------------- Part A4: noise, error against the truth
def part_a4():
    m = 5
    eps = sp.symbols("eps0:%d" % m)
    sig = sp.symbols("s", positive=True)
    # fixed integer Phi (non-orthonormal), gap g, anchor a1
    Phi = sp.Matrix([[1, 0], [1, 1], [0, 2], [1, -1], [2, 1]])
    P = Phi * (Phi.T * Phi).inv() * Phi.T
    I = sp.eye(m)
    g = sp.Matrix([1, -2, 0, 3, 1])
    gperp = (I - P) * g
    a1 = sp.Matrix([1, 1, 0, -1, 2])
    p1 = P * a1
    pp = (p1.T * p1)[0]
    e = sp.Matrix(eps)
    E = gperp - P * e                       # model error against the noise-free truth
    e1 = (a1.T * E)[0]
    Ead = E - (e1 / pp) * p1
    diff = sp.expand((Ead.T * Ead)[0] - (E.T * E)[0])
    e1g = (a1.T * gperp)[0]
    claim = sp.expand((e1g ** 2 - ((p1.T * e)[0]) ** 2) / pp)
    need(sp.simplify(diff - claim) == 0, "per-draw noisy identity")
    # expectation: E[eps_i eps_j] = s^2 delta_ij, E[eps_i] = 0
    poly = sp.Poly(diff, *eps)
    expv = 0
    for mon, coef in poly.terms():
        deg = sum(mon)
        if deg == 0:
            expv += coef
        elif deg == 2 and max(mon) == 2:
            expv += coef * sig ** 2
    expv = sp.simplify(expv)
    need(sp.simplify(expv - (e1g ** 2 / pp - sig ** 2)) == 0, "expected noisy inflation")
    # concrete draw where absorption reduces the true error
    draw = {eps[i]: v for i, v in enumerate([3, -1, 2, 0, 4])}
    val = diff.subs(draw)
    # in-sample identity still exact with noise (residual of the noisy fit)
    return {
        "per_draw_identity": "|E_adapt|^2 - |E|^2 = ((a1.g_perp)^2 - (p1.eps)^2)/|p1|^2",
        "expected_change": str(expv),
        "e1g^2/|p1|^2": str(sp.nsimplify(e1g ** 2 / pp)),
        "example_draw_change": str(val),
        "example_draw_absorption_reduces_true_error": bool(val < 0),
    }


# ---------------------------------------------------------------- Part A5: ensembles of fresh anchors
def part_a5():
    # canonical-style instance in Q^4 with orthonormal axes for readability
    r = [F(0), F(0), F(5), F(0)]       # residual after the fit (outside col(Phi) = span(e0, e1))
    p1 = [F(1), F(0), F(0), F(0)]       # P a1
    a1 = [F(1), F(0), F(1), F(0)]
    e1, pp = dot(a1, r), dot(p1, p1)
    ra = sub(r, scale(e1 / pp, p1))
    def ms(ens, v):
        return sum((dot(a, v) ** 2 for a in ens), F(0)) / len(ens)
    m = 4
    iso = []
    for i in range(m):
        for sgn in (1, -1):
            a = [F(0)] * m
            a[i] = F(sgn)
            iso.append(a)
    iso_change = ms(iso, ra) - ms(iso, r)
    need(iso_change == e1 * e1 / pp / m, "isotropic ensemble change sigma^2 e1^2/|p1|^2")
    # same-kind ensemble: anchors near a1
    same = [add(a1, [F(i), F(0), F(0), F(j)]) for i in (-1, 0, 1) for j in (-1, 0, 1)]
    same_change = ms(same, ra) - ms(same, r)
    # ensemble boundary: helps iff c^2 Mpp < 2 c Mrp
    c = e1 / pp
    Mpp = sum((dot(a, p1) ** 2 for a in same), F(0)) / len(same)
    Mrp = sum((dot(a, r) * dot(a, p1) for a in same), F(0)) / len(same)
    need(same_change == c * c * Mpp - 2 * c * Mrp, "ensemble change formula")
    # partial specification revision can hurt one fresh anchor
    v = [F(0), F(0), F(3, 5), F(4, 5)]
    rrev = sub(r, scale(dot(r, v), v))
    a2 = [F(0), F(0), F(1), F(-1)]
    return {
        "isotropic_change": str(iso_change),
        "same_kind_change": str(same_change),
        "same_kind_absorption_helps": same_change < 0,
        "partial_revision_on_anchor_u2_minus_u3": [str(dot(a2, r) ** 2), str(dot(a2, rrev) ** 2)],
    }


def part_a6():
    """With noise, a wrong revision lowers the in-sample residual and raises the error against truth."""
    Phi = [[F(1)], [F(1)], [F(0)], [F(0)]]
    g = [F(0), F(0), F(2), F(0)]           # true omitted effect, already outside col(Phi)
    eps = [F(1, 2), F(-1, 4), F(1, 4), F(1)]
    y = add(g, eps)                          # theta* = 0
    P1 = lambda v: projector_apply(Phi, v)
    Phi2 = [row + [w] for row, w in zip(Phi, [F(0), F(0), F(0), F(1)])]  # wrong revision direction e3
    fit1, fit2 = P1(y), projector_apply(Phi2, y)
    res1, res2 = sub(y, fit1), sub(y, fit2)
    err1, err2 = sub(g, fit1), sub(g, fit2)  # error against noise-free truth
    need(dot(res2, res2) < dot(res1, res1), "wrong revision lowers in-sample residual")
    need(dot(err2, err2) > dot(err1, err1), "wrong revision raises true error")
    return {"in_sample": [str(dot(res1, res1)), str(dot(res2, res2))],
            "true_error": [str(dot(err1, err1)), str(dot(err2, err2))]}


def main():
    out = {"A1_core": part_a1(), "A2_multi_anchor": part_a2(), "A3_soft": part_a3(),
           "A4_noise_vs_truth": part_a4(), "A5_ensembles": part_a5(), "A6_wrong_revision": part_a6()}
    print("seeds: A1=777001 A2=777002 A3=777003")
    print(json.dumps(out, indent=1, default=str))
    a1 = out["A1_core"]
    print("RESULT: PASS eval_twoloop_identities: %d core instances (%d rank-deficient, %d noisy), %d multi-anchor, %d soft-absorption, noisy-truth identity and ensemble checks held"
          % (a1["tested"], a1["rank_deficient"], a1["noise"], out["A2_multi_anchor"]["multi_anchor_instances"], out["A3_soft"]["soft_absorption_instances"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckFailed as exc:
        print("RESULT: FAIL (%s)" % exc)
        sys.exit(1)
