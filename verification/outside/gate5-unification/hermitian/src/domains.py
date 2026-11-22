"""Clean-room constructions of the three domains' matrices, in exact arithmetic.
Written from the mathematics (GKSL generator, AeST quadratic Hamiltonian, Hermitian rank bound), not from upstream code."""
from __future__ import annotations

from fractions import Fraction

from exactlib import *

ONE = Fraction(1)
ZERO = Fraction(0)
I_ = Qi(0, 1)

PAULI = {
    "I": [[Qi(1), Qi(0)], [Qi(0), Qi(1)]],
    "X": [[Qi(0), Qi(1)], [Qi(1), Qi(0)]],
    "Y": [[Qi(0), Qi(0, -1)], [Qi(0, 1), Qi(0)]],
    "Z": [[Qi(1), Qi(0)], [Qi(0), Qi(-1)]],
}


def kron(A, B):
    return [[A[i][j] * B[k][l] for j in range(len(A[0])) for l in range(len(B[0]))]
            for i in range(len(A)) for k in range(len(B))]


def pauli2(lbl):
    return kron(PAULI[lbl[0]], PAULI[lbl[1]])


# ---------------- Domain Q: open quantum (2-qubit GKSL generator in the Pauli basis) ----------------
ALL_LABELS = [a + b for a in "IXYZ" for b in "IXYZ"]


def anticommutes(l1, l2):
    """Pauli strings anticommute iff an odd number of positions differ and are both non-identity"""
    n = 0
    for a, b in zip(l1, l2):
        if a != "I" and b != "I" and a != b:
            n += 1
    return n % 2 == 1


def gksl_matrix(h_terms, jumps, cm_jump):
    """16x16 matrix L[a][b] = tr(E_a^dag L(E_b)), E_a = P_a/2, over Q.
    L(rho) = -i[H,rho] + sum_j rate_j D[J_j](rho),  H = sum coef*P(label),  jumps = [(rate, label)].
    The basis is ordered: invariant block first (Paulis commuting with cm_jump), then witness block (anticommuting)."""
    Hm = zeros(4, 4, Qi(0))
    for coef, lbl in h_terms:
        Hm = madd(Hm, mscale(Qi(fr(coef)), pauli2(lbl)))
    jl = [(fr(rate), pauli2(lbl)) for rate, lbl in jumps]
    inv_l = [l for l in ALL_LABELS if not anticommutes(l, cm_jump)]
    wit_l = [l for l in ALL_LABELS if anticommutes(l, cm_jump)]
    order = inv_l + wit_l
    E = [mscale(Qi(Fraction(1, 2)), pauli2(l)) for l in order]

    def act(rho):
        out = mscale(-I_, msub(mm(Hm, rho), mm(rho, Hm)))
        for rate, Lj in jl:
            if rate == 0:
                continue
            Ld = dag(Lj)
            LdL = mm(Ld, Lj)
            t1 = mm(mm(Lj, rho), Ld)
            an = madd(mm(LdL, rho), mm(rho, LdL))
            out = madd(out, mscale(Qi(rate), msub(t1, mscale(Qi(Fraction(1, 2)), an))))
        return out

    L = zeros(16, 16)
    for b in range(16):
        img = act(E[b])
        for a in range(16):
            M = mm(dag(E[a]), img)
            t = Qi(0) + M[0][0] + M[1][1] + M[2][2] + M[3][3]
            require(t.im == 0, "Liouvillian entry not real")
            L[a][b] = t.re
    return L, order, list(range(len(inv_l))), list(range(len(inv_l), 16))


def liouvillian(N, gamma1, g, gtid, omega=Fraction(0), cm_jump="ZI", ham="XZ", pair_jump="ZZ"):
    """the ledger's model: H = g*XZ + omega*IZ, jumps ZI at rate N^2 gamma1 and ZZ at rate gtid"""
    N = fr(N)
    gcm = N * N * fr(gamma1)
    return gksl_matrix([(g, ham), (omega, "IZ")], [(gcm, cm_jump), (gtid, pair_jump)], cm_jump)


# ---------------- Domain G: AeST quadratic Hamiltonian in (chi, p, P) ----------------
def aest_form(KB, lam, Kpp, r):
    """returns f(chi,p,P): the quadratic H2 at Q=1, built from the Legendre-transformed ADM Lagrangian."""
    KB, lam, Kpp, r = map(fr, (KB, lam, Kpp, r))
    b = 2 - KB

    def f(ch, p, P):
        ch, p, P = map(fr, (ch, p, P))
        gam = p / (2 * Kpp)
        Z = (p + P) / (2 * r)
        Phi = P / (4 * r)
        E = (Z - b * ch) / KB
        Lg = r * (-2 * Phi * Phi) + Kpp * gam * gam + r * (KB * E * E + 2 * b * E * ch - b * (1 + lam) * ch * ch)
        return p * (gam + Phi) + (p + P) * (E - Phi) - Lg

    return f


def hessian3(f):
    """exact Hessian of a homogeneous quadratic f on Q^3 by polarisation"""
    E = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    H = zeros(3, 3)
    for i in range(3):
        H[i][i] = f(*E[i]) * 2
    for i in range(3):
        for j in range(i + 1, 3):
            v = tuple(a + b for a, b in zip(E[i], E[j]))
            h = f(*v) - f(*E[i]) - f(*E[j])
            H[i][j] = h
            H[j][i] = h
    return H


def aest_hessian(KB, lam, Kpp, r):
    return hessian3(aest_form(KB, lam, Kpp, r))


def G_AA(KB, lam, Kpp, r):
    KB, lam, Kpp, r = map(fr, (KB, lam, Kpp, r))
    return (Kpp * (lam + 1) - (2 - KB) * lam * r) / (Kpp * (lam + 1) + (2 + KB * lam) * r)


# ---------------- Domain S: spectral inertia (Hermitian over Q(i)) ----------------
def householder(v):
    """exact unitary I - 2 v v^* / (v^* v) over Q(i)"""
    n = len(v)
    nn = sum((x.norm() for x in v), Fraction(0))
    require(nn != 0, "zero Householder vector")
    return [[(Qi(1) if i == j else Qi(0)) - Qi(2) * v[i] * cj(v[j]) / Qi(nn) for j in range(n)] for i in range(n)]


def rand_unitary(n, rng):
    U = None
    for _ in range(2):
        while True:
            v = [Qi(rng.randint(-3, 3), rng.randint(-3, 3)) for _ in range(n)]
            if any(not x.iszero() for x in v):
                break
        Hh = householder(v)
        U = Hh if U is None else mm(U, Hh)
    return U


def herm_from_spectrum(eigs, U):
    n = len(eigs)
    D = [[Qi(eigs[i]) if i == j else Qi(0) for j in range(n)] for i in range(n)]
    return mm(mm(U, D), dag(U))


def spectral_system(n, rank_p, bpos, rng, regime1=True):
    """P >= 0 of rank rank_p, Q Hermitian with bpos positive eigenvalues; returns dict with exact data"""
    UP = rand_unitary(n, rng)
    UQ = rand_unitary(n, rng)
    ep = [Fraction(rng.randint(1, 5), rng.randint(1, 3)) if not regime1 else Fraction(rng.randint(1, 4), rng.randint(2, 4)) for _ in range(rank_p)] + [Fraction(0)] * (n - rank_p)
    if regime1:
        eq = [Fraction(rng.randint(9, 11), 2) for _ in range(bpos)] + [-Fraction(rng.randint(0, 1), 10) for _ in range(n - bpos)]
    else:
        eq = [Fraction(rng.randint(1, 5), rng.randint(1, 3)) for _ in range(bpos)] + [-Fraction(rng.randint(0, 5), rng.randint(1, 3)) for _ in range(n - bpos)]
    P = herm_from_spectrum(ep, UP)
    Q = herm_from_spectrum(eq, UQ)
    M = madd(P, Q)
    return P, Q, M, UQ


def frob2(A):
    return sum((x.norm() for r in A for x in r), Fraction(0))


def spectral_scalars(P, Q, M, bpos):
    n = len(M)
    u = realpart(sum((P[i][i] for i in range(n)), Qi(0)))
    t = realpart(sum((Q[i][i] for i in range(n)), Qi(0)))
    S = frob2(M)
    return u, t, S, bpos


def R_opt(u, t, S, b):
    """regime-1 closed form u^2/(S - t^2/b); returns None outside regime 1 (t(u+t) >= bS, b>0, t>0, u>0)"""
    u, t, S = fr(u), fr(t), fr(S)
    if b > 0 and t > 0 and u > 0 and t * (u + t) >= b * S:
        den = S - t * t / b
        require(den > 0, "regime-1 denominator not positive")
        return u * u / den
    return None


def G2(S, t, b):
    return [[fr(S), fr(t)], [fr(t), fr(b)]]


def G2_bordered(S, t, b, u):
    """my lift: B = [[S,t,u],[t,b,0],[u,0,0]]; Schur complement of the 2x2 block G in B is -u^2 (G^{-1})_{11} = -R_opt"""
    return [[fr(S), fr(t), fr(u)], [fr(t), fr(b), ZERO], [fr(u), ZERO, ZERO]]
