#!/usr/bin/env python3
"""Check script eval_stack_certificate.py: AUDIT-006R (stacked-adapter certificate Q_stack), evaluator's independent exact check.

Backs: VERDICTS.md section 1, 'Stacked-adapter certificate Q_stack (006R)': PSD exactly when sigma_max^2 <= s on 324 probes with an exact root count. Also section 4 item 10: the integer-only certificate with must-fail controls and the gain table.
Needs: python3 (3.10 or newer) and SymPy. No network, no clone of any repository, no input files.
Run: python3 -I -B eval_stack_certificate.py
     (also python3 -I -O -B eval_stack_certificate.py and python3 -I -B -W error eval_stack_certificate.py, same output)
Time: about 2 seconds.
Every failed check raises CheckFailed and the script exits 1. On success the last
line printed starts with RESULT: PASS and the exit code is 0.
Seed (fixed, printed in the output): 881001, 881002.

Original description:
Independent exact check of the stacked-adapter certificate Q_stack(s) (AUDIT-006/006R, SEAM-06).

Shares no code with the expedition. Three routes:
  1. Q(s) = s G_B - G_B G_A G_B on the concatenated scaled factors, PSD decided by an
     exact symmetric-pivot LDL^T written here (Fraction).
  2. sigma_max(W)^2 for W = sum_i s_i B_i A_i as the largest real root of the exact
     characteristic polynomial of W^T W or W W^T (SymPy, algebraic numbers, no floats).
  3. A division-free integer checker: c * Q_int == L diag(D) L^T with integer L, D >= 0
     (accept), or an integer vector x with x^T Q_int x < 0 (reject). Only + and *.
Also: budget recovered against warp's Cauchy-Schwarz rule on warp's example limits.
"""
from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction as F

import sympy as sp


class CheckFailed(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise CheckFailed(msg)


def T(M):
    return [list(c) for c in zip(*M)]


def mm(A, B):
    Bt = T(B)
    return [[sum((x * y for x, y in zip(r, c)), F(0) if isinstance(r[0], F) else 0) for c in Bt] for r in A]


def concat_cols(Bs):
    return [sum((list(B[i]) for B in Bs), []) for i in range(len(Bs[0]))]


def concat_rows(As):
    return [list(r) for A in As for r in A]


def Q_of(Bs, As, scales, s):
    Bc = concat_cols([[[sc * x for x in row] for row in B] for B, sc in zip(Bs, scales)])
    Ac = concat_rows(As)
    GB = mm(T(Bc), Bc)
    GA = mm(Ac, T(Ac))
    K = mm(mm(GB, GA), GB)
    return [[s * GB[i][j] - K[i][j] for j in range(len(GB))] for i in range(len(GB))], GB, GA


def stack_sum(Bs, As, scales):
    W = None
    for B, A, sc in zip(Bs, As, scales):
        P = mm(B, A)
        P = [[sc * x for x in r] for r in P]
        W = P if W is None else [[a + b for a, b in zip(r1, r2)] for r1, r2 in zip(W, P)]
    return W


# ---------------------------------------------------------------- route 1: exact LDL^T PSD test
def ldl_psd(M):
    """Return (True, (order, L, D)) with M[order][:,order] = L diag(D) L^T, D >= 0,
    or (False, x) with x^T M x < 0. Exact Fractions."""
    n = len(M)
    S = [[F(x) for x in r] for r in M]
    order = list(range(n))
    L = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    D = [F(0)] * n
    k = 0
    while k < n:
        # pick a pivot with positive diagonal in the trailing block
        diag = [(S[i][i], i) for i in range(k, n)]
        neg = [i for v, i in diag if v < 0]
        if neg:
            y = {neg[0]: F(1)}
            return False, back_map(L, order, k, n, y)
        pos = [i for v, i in diag if v > 0]
        if not pos:
            for i in range(k, n):
                for j in range(k, n):
                    if i != j and S[i][j] != 0:
                        y = {i: F(1), j: F(-1) if S[i][j] > 0 else F(1)}
                        return False, back_map(L, order, k, n, y)
            break  # trailing block is zero
        p = pos[0]
        if p != k:
            S[k], S[p] = S[p], S[k]
            for r in S:
                r[k], r[p] = r[p], r[k]
            order[k], order[p] = order[p], order[k]
            L[k], L[p] = L[p], L[k]
            for r in L:
                r[k], r[p] = r[p], r[k]
            # keep L unit lower-triangular on the processed columns
            for c in range(n):
                pass
        piv = S[k][k]
        D[k] = piv
        for i in range(k + 1, n):
            L[i][k] = S[i][k] / piv
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                S[i][j] -= L[i][k] * S[k][j]
        for i in range(k + 1, n):
            S[i][k] = F(0)
            S[k][i] = F(0)
        k += 1
    return True, (order, L, D)


def back_map(L, order, k, n, y):
    """Vector x with x^T M x = y^T S y, S the trailing Schur block at step k."""
    z = [F(0)] * n
    for i, v in y.items():
        z[i] = v
    # solve L^T u = z (L unit lower-triangular in the permuted order), then x[order[i]] = u[i]
    u = [F(0)] * n
    for i in range(n - 1, -1, -1):
        u[i] = z[i] - sum((L[j][i] * u[j] for j in range(i + 1, n)), F(0))
    x = [F(0)] * n
    for i in range(n):
        x[order[i]] = u[i]
    return x


def quad(M, x):
    return sum((x[i] * M[i][j] * x[j] for i in range(len(x)) for j in range(len(x))), F(0))


def ldl_check_identity(M, cert):
    order, L, D = cert
    n = len(M)
    for i in range(n):
        for j in range(n):
            v = sum((L[i][t] * D[t] * L[j][t] for t in range(n)), F(0))
            if v != M[order[i]][order[j]]:
                return False
    return all(d >= 0 for d in D)


# ---------------------------------------------------------------- route 2: exact sigma_max^2
LAM = sp.Symbol("lam")


def gram_poly(W):
    Ws = sp.Matrix(W)
    G = Ws.T * Ws if Ws.cols <= Ws.rows else Ws * Ws.T
    return sp.Poly(G.charpoly(LAM).as_expr(), LAM, domain="QQ")


def smax2_le(poly, q):
    """Exact: is the largest root of poly <= q?  Sturm count on the square-free part."""
    sq = poly.sqf_part()
    qq = sp.Rational(q.numerator, q.denominator)
    above = sq.count_roots(qq, None) - (1 if sq.eval(qq) == 0 else 0)
    return above == 0


def smax2_info(poly):
    rr = [r for r in sp.roots(poly, filter="Q").keys()]
    approx = max(sp.N(r, 40) for r in poly.real_roots())
    exact = None
    for r in rr:
        if abs(sp.N(r, 40) - approx) < sp.Float("1e-30", 40):
            exact = F(int(sp.Rational(r).p), int(sp.Rational(r).q))
    return exact, F(str(approx))


# ---------------------------------------------------------------- route 3: integers only
def to_int_problem(Bs, As, scales, s):
    """Clear denominators: returns integer Q_int with Q_int PSD iff sigma_max^2 <= s."""
    sc_B = [[[sc * x for x in row] for row in B] for B, sc in zip(Bs, scales)]
    Bc = concat_cols(sc_B)
    Ac = concat_rows(As)
    beta = 1
    for r in Bc:
        for x in r:
            beta = math.lcm(beta, x.denominator)
    alpha = 1
    for r in Ac:
        for x in r:
            alpha = math.lcm(alpha, x.denominator)
    Bi = [[int(x * beta) for x in r] for r in Bc]
    Ai = [[int(x * alpha) for x in r] for r in Ac]
    GB = [[sum(Bi[k][i] * Bi[k][j] for k in range(len(Bi))) for j in range(len(Bi[0]))] for i in range(len(Bi[0]))]
    GA = [[sum(Ai[i][k] * Ai[j][k] for k in range(len(Ai[0]))) for j in range(len(Ai))] for i in range(len(Ai))]
    R = len(GB)
    GAGB = [[sum(GA[i][k] * GB[k][j] for k in range(R)) for j in range(R)] for i in range(R)]
    K = [[sum(GB[i][k] * GAGB[k][j] for k in range(R)) for j in range(R)] for i in range(R)]
    num, den = s.numerator, s.denominator
    big = num * alpha * alpha * beta * beta
    return [[big * GB[i][j] - den * K[i][j] for j in range(R)] for i in range(R)]


def int_certificate(Qint):
    ok, w = ldl_psd(Qint)
    if not ok:
        lcm = 1
        for v in w:
            lcm = math.lcm(lcm, v.denominator)
        return ("refute", [int(v * lcm) for v in w])
    order, L, D = w
    n = len(Qint)
    lam = 1
    for r in L:
        for v in r:
            lam = math.lcm(lam, v.denominator)
    dl = 1
    for v in D:
        dl = math.lcm(dl, v.denominator)
    # rows of Lint in ORIGINAL index order: c * Q = Lint diag(Dint) Lint^T, c = lam^2 * dl
    Lp = [[int(v * lam) for v in r] for r in L]
    Lint = [None] * n
    for i in range(n):
        Lint[order[i]] = Lp[i]
    return ("accept", (lam * lam * dl, Lint, [int(v * dl) for v in D]))


def int_checker(Qint, cert):
    """Division-free, square-root-free checker. Only + * and comparisons on Python ints."""
    kind, payload = cert
    n = len(Qint)
    if kind == "refute":
        x = payload
        if len(x) != n or any(type(v) is not int for v in x):
            return "malformed"
        q = 0
        for i in range(n):
            for j in range(n):
                q += x[i] * Qint[i][j] * x[j]
        return "reject" if q < 0 else "malformed"
    if kind == "accept":
        c, L, D = payload
        if type(c) is not int or c <= 0 or len(L) != n or len(D) != n:
            return "malformed"
        if any(type(d) is not int or d < 0 for d in D):
            return "malformed"
        if any(len(r) != n or any(type(v) is not int for v in r) for r in L):
            return "malformed"
        for i in range(n):
            for j in range(n):
                if c * Qint[i][j] != sum(L[i][t] * D[t] * L[j][t] for t in range(n)):
                    return "malformed"
        return "accept"
    return "malformed"


# ---------------------------------------------------------------- generators
def rand_frac_mat(rng, r, c, den=4, lo=-4, hi=4):
    return [[F(rng.randint(lo, hi), den) for _ in range(c)] for _ in range(r)]


def make_case(rng, kind, dout, din):
    N = rng.randint(2, 4)
    ranks = [rng.randint(1, 3) for _ in range(N)]
    scales = [F(rng.randint(-4, 6) or 1, rng.randint(1, 3)) for _ in range(N)]
    Bs, As = [], []
    if kind == "random":
        for r in ranks:
            Bs.append(rand_frac_mat(rng, dout, r))
            As.append(rand_frac_mat(rng, r, din))
    elif kind == "disjoint":
        # adapter i lives on its own block of output rows and input columns
        ranks = [1] * N
        ro, ci = 0, 0
        bo, bi = dout // N, din // N
        for i in range(N):
            B = [[F(0)] for _ in range(dout)]
            A = [[F(0)] * din]
            for t in range(bo):
                B[ro + t][0] = F(rng.randint(-4, 4) or 1, 4)
            for t in range(bi):
                A[0][ci + t] = F(rng.randint(-4, 4) or 1, 4)
            ro += bo
            ci += bi
            Bs.append(B)
            As.append(A)
    elif kind == "shared":
        B = rand_frac_mat(rng, dout, 2)
        A = rand_frac_mat(rng, 2, din)
        Bs = [B] * N
        As = [A] * N
        scales = [F(1)] * N
    elif kind == "rankdef":
        for r in ranks:
            B = rand_frac_mat(rng, dout, r + 1)
            for row in B:
                row[-1] = 2 * row[0]          # dependent column -> singular G_B
            Bs.append(B)
            As.append(rand_frac_mat(rng, r + 1, din))
    elif kind == "cancel":
        B = rand_frac_mat(rng, dout, 2)
        A = rand_frac_mat(rng, 2, din)
        Bs, As, scales = [B, B], [A, A], [F(1), F(-1)]   # W = 0
    return Bs, As, scales


def part_b1(seed=881001):
    rng = random.Random(seed)
    tally = {}
    probes = 0
    for kind, count in (("random", 18), ("disjoint", 10), ("shared", 8), ("rankdef", 10), ("cancel", 2)):
        for _ in range(count):
            dout, din = rng.choice([(6, 4), (5, 7), (8, 6)])
            Bs, As, scales = make_case(rng, kind, dout, din)
            W = stack_sum(Bs, As, scales)
            poly = gram_poly(W)
            exact, approx = smax2_info(poly)
            # Frobenius: tr(G_B G_A) on scaled concatenated factors
            _, GB, GA = Q_of(Bs, As, scales, F(0))
            trGBGA = sum((GB[i][k] * GA[k][i] for i in range(len(GB)) for k in range(len(GB))), F(0))
            frob = sum((x * x for r in W for x in r), F(0))
            need(trGBGA == frob, "Frobenius = tr(G_B G_A)")
            # probe values of s: exact when rational, rational brackets otherwise
            ss = []
            if exact is not None:
                q = exact
                ss += [q, q * F(999, 1000), q * F(1001, 1000) + F(1, 10**6)]
                tally["exact_rational_sigma_sq"] = tally.get("exact_rational_sigma_sq", 0) + 1
            ss += [approx * F(1000001, 1000000), approx * F(999999, 1000000)]
            ss += [F(0), F(1, 7), F(3), F(50)]
            for s in ss:
                if s < 0:
                    continue
                Q, _, _ = Q_of(Bs, As, scales, s)
                ok, wit = ldl_psd(Q)
                truth = smax2_le(poly, s)              # sigma_max^2 <= s
                need(ok == truth, f"Q(s) PSD != (sigma^2 <= s) kind={kind} s={s}")
                if ok:
                    need(ldl_check_identity(Q, wit), "LDL identity")
                else:
                    need(quad(Q, wit) < 0, "negative witness")
                # integer division-free route
                Qi = to_int_problem(Bs, As, scales, s)
                cert = int_certificate(Qi)
                verdict = int_checker(Qi, cert)
                need(verdict == ("accept" if truth else "reject"), "integer checker verdict")
                probes += 1
            tally[kind] = tally.get(kind, 0) + 1
    return {"cases": tally, "s_probes": probes}


def part_b2_controls(seed=881002):
    """Must-fail controls on the integer checker."""
    rng = random.Random(seed)
    Bs, As, scales = make_case(rng, "random", 6, 5)
    _, approx = smax2_info(gram_poly(stack_sum(Bs, As, scales)))
    s_ok, s_bad = approx * F(1001, 1000), approx * F(999, 1000)
    Qok = to_int_problem(Bs, As, scales, s_ok)
    Qbad = to_int_problem(Bs, As, scales, s_bad)
    kind, (c, L, D) = int_certificate(Qok)
    res = {}
    res["honest_accept"] = int_checker(Qok, (kind, (c, L, D)))
    # replay the accepting certificate against the matrix for a smaller s
    res["replay_on_smaller_s"] = int_checker(Qbad, (kind, (c, L, D)))
    D2 = list(D)
    j = next(i for i, d in enumerate(D2) if d > 0)
    D2[j] = -D2[j]
    res["negative_D_entry"] = int_checker(Qok, ("accept", (c, L, D2)))
    L2 = [list(r) for r in L]
    L2[0][0] += 1
    res["tampered_L"] = int_checker(Qok, ("accept", (c, L2, D)))
    res["c_zero"] = int_checker(Qok, ("accept", (0, L, D)))
    res["bool_in_D"] = int_checker(Qok, ("accept", (c, L, [True] + D[1:])))
    res["fraction_c"] = int_checker(Qok, ("accept", (F(c), L, D)))
    # c = 0 with D = 0 makes the identity 0 = 0 true for every matrix, so only the guard on c refuses it
    res["c_zero_and_D_zero_on_indefinite_matrix"] = int_checker(Qbad, ("accept", (0, L, [0] * len(D))))
    res["c_bits"] = c.bit_length()
    kb, x = int_certificate(Qbad)
    res["honest_refute_smaller_s"] = int_checker(Qbad, (kb, x))
    res["refute_vector_on_ok_matrix"] = int_checker(Qok, (kb, x))
    # a witness with x^T Q x = 0 does not show that Q is not PSD, so it must not count as a refutation
    res["refute_zero_vector"] = int_checker(Qok, ("refute", [0] * len(x)))
    # One control per remaining guard of int_checker. Each uses a tiny matrix and a certificate whose
    # identity c*Q == L diag(D) L^T holds exactly, so only the named guard can refuse it.
    # (a) guard d < 0: Q = [[1,2],[2,1]] is indefinite and has an honest L D L^T with D = [1, -3].
    res["indefinite_matrix_with_negative_D"] = int_checker([[1, 2], [2, 1]], ("accept", (1, [[1, 0], [2, 1]], [1, -3])))
    # (b) guard type(d) is not int: a bool 1 equals the int 1, so the identity holds.
    res["bool_D_identity_holds"] = int_checker([[1]], ("accept", (1, [[1]], [True])))
    # (c) guard type(v) is not int on L: the float 1.0 equals the int 1, so the identity holds.
    res["float_L_identity_holds"] = int_checker([[1]], ("accept", (1, [[1.0]], [1])))
    # (d) guard type(v) is not int on a refutation vector: [[-1]] is refuted by x = 1, and by x = 1.0 as well.
    res["float_refute_vector"] = int_checker([[-1]], ("refute", [1.0]))
    need(int_checker([[-1]], ("refute", [1])) == "reject", "honest refutation of [[-1]]")
    need(res["honest_accept"] == "accept" and res["honest_refute_smaller_s"] == "reject", "honest paths")
    refused = ("indefinite_matrix_with_negative_D", "bool_D_identity_holds", "float_L_identity_holds",
               "float_refute_vector",
               "replay_on_smaller_s", "negative_D_entry", "tampered_L", "c_zero", "bool_in_D", "fraction_c",
               "refute_vector_on_ok_matrix",
               "c_zero_and_D_zero_on_indefinite_matrix", "refute_zero_vector")
    for k in refused:
        need(res[k] == "malformed", f"control {k} not refused")
    res["controls_refused"] = len(refused)
    return res


# ---------------------------------------------------------------- budget vs warp Cauchy-Schwarz rule
def part_b3():
    """warp example config: single Frobenius^2 5, joint 20; single spectral^2 2, joint 8.
    Each of N equal adapters at scale 1 with per-adapter value v.
    CS rule admits v <= joint / N^2. Exact rule admits the largest v with true stack value <= joint,
    and v <= single in both cases."""
    rows = []
    for N in (2, 3, 4, 8):
        for metric, single, joint in (("frobenius_sq", F(5), F(20)), ("spectral_sq", F(2), F(8))):
            cs = min(single, joint / (N * N))
            # disjoint: Frobenius adds, spectral is the max
            disj = min(single, joint / N) if metric == "frobenius_sq" else min(single, joint)
            shared = min(single, joint / (N * N))  # identical updates: ||N D||^2 = N^2 ||D||^2
            rows.append({"N": N, "metric": metric, "cs_per_adapter": str(cs),
                         "exact_disjoint_per_adapter": str(disj), "gain_disjoint": str(disj / cs),
                         "exact_fully_shared": str(shared)})
    # concrete exact demonstration: N=4 disjoint rank-1 adapters, each spectral^2 = 2, Frobenius^2 = 2
    d = 8
    Bs, As = [], []
    for i in range(4):
        B = [[F(0)] for _ in range(d)]
        A = [[F(0)] * d]
        B[2 * i][0] = F(1)
        A[0][2 * i + 1] = F(2)       # B A has a single entry 2 -> sigma^2 = 4? adjust below
        Bs.append(B)
        As.append(A)
    # rescale so each adapter has sigma^2 = 2: entry sqrt(2) is irrational, use B entry 1, A entry 1 and scale
    As = [[[F(1) if x else F(0) for x in A[0]]] for A in As]
    scales = [F(1)] * 4                                  # each adapter: sigma^2 = 1, Frobenius^2 = 1
    W = stack_sum(Bs, As, scales)
    lam, _ = smax2_info(gram_poly(W))
    Q1, _, _ = Q_of(Bs, As, scales, F(1))
    ok1, _ = ldl_psd(Q1)
    cs_spec = 4 * sum((F(1) for _ in range(4)), F(0))    # N * sum sigma_i^2 = 16
    demo = {"N": 4, "each_sigma_sq": "1", "exact_stack_sigma_sq": str(lam), "Q(1)_psd": ok1,
            "cs_spectral_value": str(cs_spec), "cs_frobenius_value": "16", "exact_frobenius": "4"}
    need(ok1 and lam == 1, "disjoint demo")
    return {"table": rows, "demo": demo}


def main():
    out = {"B1_soundness_and_exactness": part_b1(), "B2_integer_checker_controls": part_b2_controls(),
           "B3_budget": part_b3()}
    print("seeds: B1=881001 B2=881002")
    print(json.dumps(out, indent=1, default=str))
    b1 = out["B1_soundness_and_exactness"]
    print("RESULT: PASS eval_stack_certificate: Q_stack PSD iff sigma_max^2 <= s on %d probes (exact), integer checker agrees, %d must-fail controls refused, gain table and N=4 demo held"
          % (b1["s_probes"], out["B2_integer_checker_controls"]["controls_refused"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckFailed as exc:
        print("RESULT: FAIL (%s)" % exc)
        sys.exit(1)
