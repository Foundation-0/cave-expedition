"""Functions for the evaluator-side contact velocity and arc checks (not a check by itself).

project: exact Frobenius projection of a seed onto the bar-tangent strains.
neighbours: exact coset lookup of every contact. sweep: first-order velocity of every
contact in exact integers. gates: the three Lemma B gates. cayley_L: the rational arc.
Needs numpy.
"""
import math
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import det_frac, inv_frac, fail  # noqa: E402


def project(L, C, X0):
    """Frobenius-orthogonal projection of X0 onto {X: r_i X c_i^T = 0}, r_i rows of L, c_i rows of C."""
    n = len(L)
    # constraint matrices E_i = r_i^T c_i ; <E_i, X> = r_i X c_i^T
    rr = [[sum(L[i][k] * L[j][k] for k in range(n)) for j in range(n)] for i in range(n)]
    cc = [[sum(C[i][k] * C[j][k] for k in range(n)) for j in range(n)] for i in range(n)]
    G = [[rr[i][j] * cc[i][j] for j in range(n)] for i in range(n)]
    b = [sum(L[i][a] * X0[a][c] * C[i][c] for a in range(n) for c in range(n)) for i in range(n)]
    Gi = inv_frac(G)
    mu = [sum(Gi[i][j] * b[j] for j in range(n)) for i in range(n)]
    X = [[X0[a][c] - sum(mu[i] * L[i][a] * C[i][c] for i in range(n)) for c in range(n)] for a in range(n)]
    for i in range(n):
        if sum(L[i][a] * X[a][c] * C[i][c] for a in range(n) for c in range(n)) != 0:
            fail("projection failed")
    return X


def ldl_min_shift(Xs, lam):
    n = len(Xs)
    M = [[Xs[i][j] - (lam if i == j else 0) for j in range(n)] for i in range(n)]
    for k in range(n):
        if M[k][k] <= 0:
            return False
        for i in range(k + 1, n):
            f = M[i][k] / M[k][k]
            for j in range(k, n):
                M[i][j] -= f * M[k][j]
    return True


def neighbours(scale, L_x, W):
    """Exact: for int64 W (scale*w rows) and every motif ball pk, the neighbour index q and the
    integer cell vector m with p + w = q + m L.  Uses the integer adjugate N = D (scale L)^{-1}."""
    n = len(L_x)
    D = int(det_frac(L_x))
    Linv = inv_frac(L_x)
    Nfull = [[Linv[i][j] * D for j in range(n)] for i in range(n)]
    if any(v.denominator != 1 for r in Nfull for v in r):
        fail("adjugate not integral")
    N = np.array([[int(v) % D for v in r] for r in Nfull], dtype=np.int64)  # reduced mod D: keys only
    Lxi = np.array(L_x, dtype=np.int64)
    Linvf = np.array([[float(v) for v in r] for r in Linv])
    P = np.array([[s * scale if j == i else 0 for j in range(n)] for i in range(n) for s in (1, -1)], dtype=np.int64)
    keyW = (W @ N) % D
    keyP = (P @ N) % D
    def vview(K):
        K = np.ascontiguousarray(K)
        return K.view(np.dtype((np.void, K.dtype.itemsize * K.shape[1]))).ravel()
    motif = {vview(keyP[k:k + 1])[0].tobytes(): k for k in range(2 * n)}
    if len(motif) != 2 * n:
        fail("motif keys not distinct")
    out = []
    for pk in range(2 * n):
        kk = (keyW + keyP[pk]) % D
        uq, inv = np.unique(vview(kk), return_inverse=True)
        lut = np.array([motif.get(u.tobytes(), -1) for u in uq])
        if (lut < 0).any():
            fail("neighbour coset not in motif")
        qk = lut[inv.ravel()]
        if not (kk == keyP[qk]).all():
            fail("coset lookup failed (exact check)")
        num = (W + P[pk] - P[qk]) @ N
        if (num % D != 0).any():
            fail("m not integral")
        diff = W + P[pk] - P[qk]
        m = np.rint(diff.astype(float) @ Linvf).astype(np.int64)
        if not (m @ Lxi == diff).all():
            fail("m reconstruction not exact")
        out.append((qk, m))
    return P, out


def sweep(name, n, scale, L_x, minvecs_x, X):
    W = np.array(minvecs_x, dtype=np.int64)
    P, nb = neighbours(scale, L_x, W)
    den = 1
    for r in X:
        for v in r:
            den = math.lcm(den, v.denominator)
    Xi = np.array([[int(v * den) for v in r] for r in X], dtype=object)
    Wo = W.astype(object)
    Y = Wo.dot(Xi.T)            # rows: X w^T scaled by den*scale
    wXw = (Wo * Y).sum(axis=1)  # scaled by den*scale^2
    nW = len(W)
    counts = {"intra": 0, "inter": 0, "zero": 0, "neg": 0}
    minpos = None
    zero_list = []
    ar = np.arange(nW)
    for pk in range(2 * n):
        qk, m = nb[pk]
        intra = (m == 0).all(axis=1)
        ip, sp_ = divmod(pk, 2)
        sp_ = 1 if sp_ == 0 else -1
        iq = qk // 2
        sq = np.where(qk % 2 == 0, 1, -1).astype(object)
        vel = wXw - scale * (sq * Y[ar, iq] - sp_ * Y[:, ip])
        inter = ~intra
        counts["intra"] += int(intra.sum())
        counts["inter"] += int(inter.sum())
        vi = vel[inter]
        counts["neg"] += int(sum(1 for v in vi if v < 0))
        zidx = [k for k, v in zip(np.nonzero(inter)[0], vi) if v == 0]
        counts["zero"] += len(zidx)
        for k in zidx:
            zero_list.append((pk, [int(a) for a in W[k]]))
        pos = [v for v in vi if v > 0]
        if pos:
            mm = min(pos)
            minpos = mm if minpos is None or mm < minpos else minpos
    delta = Fraction(int(minpos), den * scale * scale)
    return counts, delta, zero_list


def gates(L, X, lam0, delta, tau):
    n = len(L)
    KX = sum(v * v for r in X for v in r)
    Li = inv_frac(L)
    Kinv = sum(v * v for r in Li for v in r)
    V = [[sum(L[i][k] * X[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    KR = Fraction(1, 8) * sum(sum(v * v for v in V[i]) ** 2 for i in range(n))
    KE = Kinv * KR
    g1 = KE * tau * tau <= lam0 * lam0 / 4
    g2 = KX * tau * tau <= Fraction(1, 144) and lam0 * tau / 2 <= Fraction(1, 24)
    g3 = 25 * KE * tau * tau < delta * delta
    return g1, g2, g3, KX, KE, V


def best_tau(L, X, lam0, delta):
    # largest tau = 1/N (N integer) passing all gates, by doubling then bisection
    lo, hi = 1, 1
    while not all(gates(L, X, lam0, delta, Fraction(1, hi))[:3]):
        hi *= 2
    lo = max(1, hi // 2)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if all(gates(L, X, lam0, delta, Fraction(1, mid))[:3]):
            hi = mid
        else:
            lo = mid
    return Fraction(1, hi)


def cayley_L(L, C, V, tau):
    n = len(L)
    out = []
    for i in range(n):
        vn = sum(v * v for v in V[i])
        den = 4 + vn * tau * tau / 2
        u = [((4 - vn * tau * tau / 2) * C[i][j] + 4 * tau * V[i][j]) / den for j in range(n)]
        out.append([(2 if i == j else 0) + u[j] for j in range(n)])
    return out
