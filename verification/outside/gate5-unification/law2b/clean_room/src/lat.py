"""Lattice pair: claims 21, 22 (clean-room, exact).  Construction from lattice/SPEC.md sections 1-2."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ex import *
from common import *

R = Rec()


def bars_for(n, L, Mtr):
    """list of (u, v, ell) with ell = x_v - x_u + m L ; Mtr[i] = bridge translation of bridge i; also mvec per bar"""
    def x(v):
        a, s = divmod(v, 2)
        vec = [F(0)] * n
        vec[a] = F(1) if s == 0 else F(-1)
        return vec
    bars = []
    for i in range(n):
        for j in range(i + 1, n):
            for si in (0, 1):
                for sj in (0, 1):
                    v = 2 * i + si; u = 2 * j + sj
                    ell = [a - b for a, b in zip(x(v), x(u))]
                    bars.append((u, v, ell, [F(0)] * n))
    for i in range(n):
        u, v = 2 * i, 2 * i + 1
        m = Mtr[i]
        ell = [a - b for a, b in zip(x(v), x(u))]
        for k in range(n):
            for l in range(n):
                ell[l] += m[k] * L[k][l]
        bars.append((u, v, ell, list(m)))
    return bars


def rigidity(n, L, Mtr):
    bars = bars_for(n, L, Mtr)
    nb = len(bars)
    nv = 2 * n
    d0 = zeros(nb, nv * n)
    ae = zeros(nb, n * (n + 1) // 2)
    Z = zeros(nb, n * n)
    for r, (u, v, ell, m) in enumerate(bars):
        for k in range(n):
            d0[r][v * n + k] += ell[k]
            d0[r][u * n + k] -= ell[k]
        c = 0
        for k in range(n):
            ae[r][c] = ell[k] * ell[k]; c += 1
        for k in range(n):
            for l in range(k + 1, n):
                ae[r][c] = 2 * ell[k] * ell[l]; c += 1
        for k in range(n):
            for l in range(n):
                Z[r][k * n + l] = m[k] * ell[l]
    return d0, ae, Z


def schur_S(d0, X):
    """S = K + B^T Xs with Delta Xs = -B, W = 1/2.  X is ae or Z"""
    half = F(1, 2)
    d0t = tr(d0)
    Delta = msc(half, mmul(d0t, d0))
    Bm = msc(half, mmul(d0t, X))
    K = msc(half, mmul(tr(X), X))
    Xs = solve(Delta, msc(-1, Bm))
    req(Xs is not None, 'consistent system (H positive semidefinite)')
    return madd(K, mmul(tr(Bm), Xs))


def schur_S_projector(d0, X):
    """second construction: S = (1/2) X^T Pi X with Pi the orthogonal projector onto ker(d0^T) (self-stress space)"""
    N = nullspace(tr(d0), len(d0))     # vectors y in Q^nb with d0^T y = 0
    if not N:
        return zeros(len(X[0]), len(X[0]))
    Nm = tr(N)                          # nb x s
    G = mmul(tr(Nm), Nm)
    Gi = inv(G)
    Pi = mmul(mmul(Nm, Gi), tr(Nm))
    return msc(F(1, 2), mmul(mmul(tr(X), Pi), X))


def ZB_dim(n, L):
    B = [[L[i][j] - (2 if i == j else 0) for j in range(n)] for i in range(n)]
    rows = []
    for i in range(n):
        for j in range(i + 1, n):
            row = [F(0)] * n
            row[i] = B[i][j]
            row[j] = -B[j][i]
            rows.append(row)
    return len(nullspace(rows, n)) if rows else n


def default_M(n):
    return [[F(1) if k == i else F(0) for k in range(n)] for i in range(n)]


# ---------------- claim 21
for Lrows, name in [([[3, 0, 0], [0, 2, 0], [0, 0, 2]], 'diag(3,2,2)'), ([[2, 0, 0], [0, 2, 0], [0, 0, 2]], '2I')]:
    n = 3
    L = fm(Lrows)
    d0, ae, Z = rigidity(n, L, default_M(n))
    S = schur_S(d0, ae)
    S2 = schur_S_projector(d0, ae)
    rkS = rank(S)
    z = ZB_dim(n, L)
    print('C21 L=%s: bars %d, rank d0 %d, rank S_el %d (projector method gives %d, S equal: %s), dim Z_B = %d' % (name, len(d0), rank(d0), rkS, rank(S2), S == S2, z))
    if name == 'diag(3,2,2)':
        R.check('C21 L=diag(3,2,2): rank S_el = 1 and dim Z_B = 3, so "rank 1 iff dim Z_B = 1" fails as worded', rkS == 1 and z == 3 and S == S2)
        sig = inertia_cong(S)
        print('   inertia S_el:', sig)
    else:
        R.check('C21 (extra) L=2I: S_el = 0 while dim Z_B = 3', rkS == 0 and z == 3)

# generic sanity: a symmetric non-diagonal L with dim Z_B = 1
def rand_sym_L(n, rnd):
    L = [[F(0)] * n for _ in range(n)]
    for i in range(n):
        L[i][i] = F(rnd.randint(2, 4))
        for j in range(i + 1, n):
            L[i][j] = L[j][i] = F(rnd.randint(-1, 1))
    return L

rnd = random.Random(2222)
# control: non-symmetrizable L -> S = 0
Lns = fm([[2, 1, 0], [0, 2, 1], [1, 0, 2]])
d0, ae, Z = rigidity(3, Lns, default_M(3))
R.check('CTRL generic non-symmetrizable L (dim Z_B = 0): S_el = 0', ZB_dim(3, Lns) == 0 and rank(schur_S(d0, ae)) == 0)

# ---------------- claim 22
def rand_unimodular(n, rnd, steps=14):
    U = eye(n)
    while True:
        U = eye(n)
        for _ in range(steps):
            i, j = rnd.sample(range(n), 2)
            c = F(rnd.choice([-2, -1, 1, 2]))
            E = eye(n)
            E[i][j] = c
            U = mmul(E, U)
        # reject signed permutations
        nz = sum(1 for r in U for x in r if x != 0)
        if nz > n and abs(det(U)) == 1:
            return U

def kron_I(U, n):
    """(U kron I_n) acting on index k*n + l"""
    N = n * n
    K_ = zeros(N, N)
    for k in range(n):
        for k2 in range(n):
            if U[k][k2] != 0:
                for l in range(n):
                    K_[k * n + l][k2 * n + l] = U[k][k2]
    return K_

def find_base(n, rnd):
    while True:
        L = rand_sym_L(n, rnd)
        if ZB_dim(n, L) != 1:
            continue
        d0, ae, Z = rigidity(n, L, default_M(n))
        S = schur_S(d0, ae)
        if rank(S) == 1:
            return L, S, d0, ae, Z

res = {}
for n, count in [(3, 8), (4, 8)]:
    carried_ok = 0; slat_ok = 0; naive_collapse = 0; naive_ranks = []
    ctrl_wrong_slat = 0; ctrl_notcarried_changed = 0
    for t in range(count):
        L, S0, d0, ae, Z = find_base(n, rnd)
        Slat0 = schur_S(d0, Z)
        U = rand_unimodular(n, rnd)
        Ui = inv(U)
        Lp = mmul(U, L)
        # carried: m' = m U^-1 = row i of U^-1 ; bars unchanged
        Mc = [list(Ui[i]) for i in range(n)]
        d0c, aec, Zc = rigidity(n, Lp, Mc)
        Sc = schur_S(d0c, aec)
        carried_ok += (Sc == S0)
        Slatc = schur_S(d0c, Zc)
        P = kron_I(Ui, n)
        pred = mmul(mmul(tr(P), Slat0), P)
        slat_ok += (Slatc == pred)
        # control: wrong transformation (U instead of U^-1) must disagree
        P2 = kron_I(U, n)
        pred2 = mmul(mmul(tr(P2), Slat0), P2)
        ctrl_wrong_slat += (Slatc != pred2)
        # naive: bridges m = e_i with L' = U L
        d0n, aen, Zn = rigidity(n, Lp, default_M(n))
        Sn = schur_S(d0n, aen)
        rn = rank(Sn)
        naive_ranks.append(rn)
        naive_collapse += (rn == 1)
        ctrl_notcarried_changed += (Sn != S0)
    print('C22 n=%d: carried change leaves S_el exactly unchanged: %d/%d; S_lat\' = (U^-1 x I)^T S_lat (U^-1 x I): %d/%d; naive change keeps rank-1 collapse: %d/%d (naive ranks %s)' % (n, carried_ok, count, slat_ok, count, naive_collapse, count, naive_ranks))
    res[n] = (carried_ok, slat_ok, naive_collapse, count, ctrl_wrong_slat, ctrl_notcarried_changed)
tc = sum(v[0] for v in res.values()); ts = sum(v[1] for v in res.values()); tn = sum(v[2] for v in res.values()); tt = sum(v[3] for v in res.values())
R.check('C22 carried: S_el unchanged in %d of %d' % (tc, tt), tc == tt)
R.check('C22 carried: S_lat transformation law in %d of %d' % (ts, tt), ts == tt)
R.check('C22 naive: rank-1 collapse retained in %d of %d (claim: 0 of 16)' % (tn, tt), tn == 0)
R.check('CTRL wrong law (U instead of U^-1) for S_lat is flagged on all instances', sum(v[4] for v in res.values()) == tt)
R.check('CTRL naive S_el differs from the original on all instances (the "unchanged" test can say no)', sum(v[5] for v in res.values()) == tt)
# control: signed permutation U keeps the collapse even when naive (SPEC 5(c))
L, S0, d0, ae, Z = find_base(3, rnd)
Up = fm([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
d0n, aen, Zn = rigidity(3, mmul(Up, L), default_M(3))
print('   (info) naive change with a signed permutation: rank S_el =', rank(schur_S(d0n, aen)))
print('FAILS:', R.bad)
sys.exit(1 if R.bad else 0)
