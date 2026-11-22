"""From-scratch implementation of the bar-framework construction in SPEC (math only)."""
import random
from fractions import Fraction
from exact import *

HALF = Fraction(1, 2)

def xv(n, v, lam=1):
    a, s = divmod(v, 2)
    x = [Fraction(0)] * n
    x[a] = Fraction(lam) if s == 0 else -Fraction(lam)
    return x

def standard_bars(L, lam=1):
    """list of (u, v, m, ell); ell = lam*(x_v - x_u) + m L  (vertices scaled by lam, L as given)."""
    n = len(L)
    bars = []
    for i in range(n):
        for j in range(i + 1, n):
            for si in (0, 1):
                for sj in (0, 1):
                    v = 2 * i + si
                    u = 2 * j + sj
                    xvv, xuu = xv(n, v), xv(n, u)
                    ell = [lam * (xvv[k] - xuu[k]) for k in range(n)]
                    bars.append((u, v, [0] * n, ell))
    for i in range(n):
        u, v = 2 * i, 2 * i + 1
        m = [0] * n
        m[i] = 1
        xvv, xuu = xv(n, v), xv(n, u)
        ell = [lam * (xvv[k] - xuu[k]) + L[i][k] for k in range(n)]
        bars.append((u, v, m, ell))
    return bars

def strain_index(n):
    idx = {}
    c = n
    for k in range(n):
        for l in range(k + 1, n):
            idx[(k, l)] = c
            c += 1
    return idx

def matrices(n, bars):
    nb = len(bars)
    nu = 2 * n * n
    ns = n * (n + 1) // 2
    si = strain_index(n)
    d0 = zeros(nb, nu)
    ae = zeros(nb, ns)
    Z = zeros(nb, n * n)
    for r, (u, v, m, ell) in enumerate(bars):
        for k in range(n):
            d0[r][v * n + k] = d0[r][v * n + k] + ell[k]
            d0[r][u * n + k] = d0[r][u * n + k] - ell[k]
            ae[r][k] = ell[k] * ell[k]
            for l in range(n):
                if m[k]:
                    Z[r][k * n + l] = m[k] * ell[l]
        for (k, l), c in si.items():
            ae[r][c] = 2 * ell[k] * ell[l]
    return d0, ae, Z

def gram_blocks(d0, ae, Z):
    d0t = T(d0)
    Delta = msc(HALF, mm(d0t, d0))
    Bel = msc(HALF, mm(d0t, ae))
    Blat = msc(HALF, mm(d0t, Z))
    Kel = msc(HALF, mm(T(ae), ae))
    Klat = msc(HALF, mm(T(Z), Z))
    return Delta, Bel, Blat, Kel, Klat

def schur128(Delta, B, K):
    """K + B^T X with Delta X = -B (free variables 0)."""
    negB = [[-x for x in r] for r in B]
    X = solve_consistent(Delta, negB)
    return madd(K, mm(T(B), X))

def S_both(Delta, Bel, Blat, Kel, Klat):
    nel = len(Bel[0])
    rhs = [[-x for x in (re + rl)] for re, rl in zip(Bel, Blat)]
    X = solve_consistent(Delta, rhs)
    Xe = [r[:nel] for r in X]
    Xl = [r[nel:] for r in X]
    return madd(Kel, mm(T(Bel), Xe)), madd(Klat, mm(T(Blat), Xl))

def full_H(d0, ext, W=HALF):
    R = [r0 + r1 for r0, r1 in zip(d0, ext)]
    return msc(W, mm(T(R), R)), R

def build_Phi(L, n):
    nu = 2 * n * n
    ns = n * (n + 1) // 2
    si = strain_index(n)
    Phi = zeros(nu + n * n, nu + ns)
    for i in range(nu):
        Phi[i][i] = Fraction(1)
    for v in range(2 * n):
        x = xv(n, v)
        for k in range(n):
            Phi[v * n + k][nu + k] = x[k]
        for (k, l), c in si.items():
            Phi[v * n + l][nu + c] = Phi[v * n + l][nu + c] + x[k]
            Phi[v * n + k][nu + c] = Phi[v * n + k][nu + c] + x[l]
    for k in range(n):
        for j in range(n):
            Phi[nu + k * n + j][nu + j] = Phi[nu + k * n + j][nu + j] + L[k][j]
        for (j, l), c in si.items():
            Phi[nu + k * n + l][nu + c] = Phi[nu + k * n + l][nu + c] + L[k][j]
            Phi[nu + k * n + j][nu + c] = Phi[nu + k * n + j][nu + c] + L[k][l]
    return Phi

def RL_block(Phi, n):
    nu = 2 * n * n
    return [r[nu:] for r in Phi[nu:]]

def diag_dim_and_basis(L):
    """Z_B = {z : z_i L_ij = z_j L_ji, i<j}"""
    n = len(L)
    rows = []
    for i in range(n):
        for j in range(i + 1, n):
            r = [Fraction(0)] * n
            r[i] = r[i] + L[i][j]
            r[j] = r[j] - L[j][i]
            rows.append(r)
    return nullspace(rows, n) if rows else [[Fraction(int(k == i)) for k in range(n)] for i in range(n)]

def sigma_c(L, z):
    n = len(L)
    B = [[L[i][j] - (2 if i == j else 0) for j in range(n)] for i in range(n)]
    DB = [[z[i] * B[i][j] for j in range(n)] for i in range(n)]
    M = mm(T(L), DB)
    sg = [[HALF * (M[i][j] + M[j][i]) for j in range(n)] for i in range(n)]
    out = [sg[i][i] for i in range(n)]
    for k in range(n):
        for l in range(k + 1, n):
            out.append(2 * sg[k][l])
    return out

def rank_sigma_map(L, basis):
    if not basis:
        return 0
    return rank([sigma_c(L, z) for z in basis])

def virial_rank(d0, ae):
    """independent route: rank of ae^T N with N a basis of ker d0^T (self-stresses)"""
    N = nullspace(T(d0), len(d0))
    if not N:
        return 0, 0
    V = [[sum((ae[r][c] * vec[r] for r in range(len(d0)) if vec[r]), Fraction(0)) for vec in N]
         for c in range(len(ae[0]))]
    return rank(V), len(N)

def S_rank_only(L):
    n = len(L)
    bars = standard_bars(L)
    d0, ae, Z = matrices(n, bars)
    Delta, Bel, Blat, Kel, Klat = gram_blocks(d0, ae, Z)
    Se = schur128(Delta, Bel, Kel)
    return Se, d0, ae

# ------------------------------------------------ unimodular matrices
def rand_unimodular(r, n, steps=12):
    U = eye(n)
    for _ in range(steps):
        i = r.randrange(n)
        j = r.randrange(n)
        if i == j:
            continue
        s = r.choice([1, -1])
        # row_i += s * row_j
        U[i] = [a + s * b for a, b in zip(U[i], U[j])]
    return U

def instance_L_int(M):
    return [[Fraction(x) for x in r] for r in M]
