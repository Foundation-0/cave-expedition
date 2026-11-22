"""Helpers shared by the Gate 5 scripts (instances, sampling, block Schur, rotational locking)."""
from fractions import Fraction
from g5lib import *

# -------------------------------------------------------------- instances
def instances():
    """name -> (builder returning L, ring, curve note, partition of the Gram)."""
    H = sylvester(3)
    Ip = [i for i in range(8) if H[i][i] == 1]
    Im = [i for i in range(8) if H[i][i] == -1]
    return {
        "e8_s1": dict(L=L_E8_s1(), ring="Q", note="AUDIT-017 curve at s=1: L=2I+H8/2 (sqrt2*E8 basis)", part=[Ip, Im]),
        "d8_s1": dict(L=lattice_from_bridge(twisted_cycle(8)), ring="Q", note="AUDIT-009 curve at s=1: L=2I+C_8", part=[[0], list(range(1, 8))]),
        "d8_k1": dict(L=L_Dn_rational_point(8, Fraction(4, 3), Fraction(1, 3)), ring="Q", note="D_8 fold, rational conic point (a,t)=(4/3,1/3)", part=[[0], list(range(1, 8))]),
        "e8_half": dict(L=L8_of_s(Fraction(1, 2))[0], ring="Q(sqrt2)", note="AUDIT-017 curve at s=1/2", part=[Ip, Im]),
        "d8_half": dict(L=Ln_of_s(8, Fraction(1, 2)), ring="Q(sqrt2)", note="AUDIT-009 curve at s=1/2", part=[[0], list(range(1, 8))]),
    }


# -------------------------------------------------------------- matrices
def submat(M, rows, cols):
    return [[M[i][j] for j in cols] for i in rows]


def block_schur(M, p):
    """Schur complement of the leading p x p block of symmetric M (possibly singular, PSD-consistent):
    S = M22 - M21 X, M11 X = M12 (free variables 0, verified)."""
    n = len(M)
    P = list(range(p))
    Q = list(range(p, n))
    M11 = submat(M, P, P)
    M12 = submat(M, P, Q)
    M21 = submat(M, Q, P)
    M22 = submat(M, Q, Q)
    X = solve_consistent(M11, M12)
    return madd(M22, matmul(M21, X), -1)


def block_schur_invertible(M, p):
    """Classical Schur complement requiring M11 invertible (rank checked)."""
    P = list(range(p))
    M11 = submat(M, P, P)
    rows = [{j: v for j, v in enumerate(r) if v != 0} for r in M11]
    require(rank_sparse(rows, p) == p, "M11 not invertible")
    return block_schur(M, p)


def gram(L):
    return matmul(L, transpose(L))


def H_lat_from(F):
    """Dense 192 x 192 Hessian of the lattice-side bar-length form: R_lat^T W R_lat on (dx | dL)."""
    nu, nl = F.nu, F.ndl
    rows = [{**d0, **{nu + k: v for k, v in Z.items()}} for d0, Z in zip(F.d0, F.Z)]
    return gram_w(rows, rows, nu + nl, nu + nl)


def H_el_from(F):
    nu, ne = F.nu, F.ne
    rows = [{**d0, **{nu + k: v for k, v in a.items()}} for d0, a in zip(F.d0, F.ae)]
    return gram_w(rows, rows, nu + ne, nu + ne)


def rlat_rows(F):
    return [{**d0, **{F.nu + k: v for k, v in Z.items()}} for d0, Z in zip(F.d0, F.Z)]


def rotational_locking(Bm):
    """Kernel of z -> antisym(diag(z) B) : the diagonal symmetrizers.  Returns (basis, rank)."""
    n = len(Bm)
    pairs = off_pairs(n)
    # equations (i<j): z_i B_ij - z_j B_ji = 0, unknowns z_0..z_{n-1}
    rows = []
    for (i, j) in pairs:
        d = {}
        if Bm[i][j] != 0:
            d[i] = Bm[i][j]
        if Bm[j][i] != 0:
            d[j] = d.get(j, 0) - Bm[j][i]
        if d:
            rows.append(d)
    return nullspace_sparse(rows, n)


def sigma_star(L, Bm, z):
    """Candidate stress direction sigma = sym(L^T D B) in strain-inner-product coordinates [s_ii, 2 s_ij]."""
    n = len(L)
    DB = [[z[i] * Bm[i][j] for j in range(n)] for i in range(n)]
    M = matmul(transpose(L), DB)
    Ms = [[Fraction(1, 2) * (M[i][j] + M[j][i]) for j in range(n)] for i in range(n)]
    vec = [Ms[i][i] for i in range(n)] + [2 * Ms[i][j] for (i, j) in off_pairs(n)]
    return vec


def bridge_of(L):
    n = len(L)
    return [[L[i][j] - (2 if i == j else 0) for j in range(n)] for i in range(n)]


def proportional_rank1(S, v):
    """Return c with S = c v v^T exactly, or None."""
    ne = len(S)
    k = next((i for i in range(ne) if v[i] != 0), None)
    if k is None:
        return None
    c = S[k][k] / (v[k] * v[k])
    for i in range(ne):
        for j in range(ne):
            if S[i][j] != c * v[i] * v[j]:
                return None
    return c


def det_gen(M):
    return det_small(M)


# -------------------------------------------------------------- sampling
def rand_unimodular(rng, n, ops=40):
    U = eye(n)
    Ui = eye(n)
    for _ in range(ops):
        i = rng.below(n)
        j = rng.below(n)
        if i == j:
            continue
        k = rng.rng(-1, 1)
        if k == 0:
            k = 1
        # U <- E U where E = I + k e_i e_j^T ; Uinv <- Uinv E^{-1}, E^{-1} = I - k e_i e_j^T
        U[i] = [a + k * b for a, b in zip(U[i], U[j])]
        for r in range(n):
            Ui[r][j] = Ui[r][j] - k * Ui[r][i]
    return U, Ui


def same_snf_lattice(rng, L, symmetric):
    """Random lattice with the same determinant and the same Smith form as L (cleared by 2 or 1)."""
    n = len(L)
    den, M0 = clear_denominators(L)
    d = snf_diag(M0)
    D = [[d[i] if i == j else 0 for j in range(n)] for i in range(n)]
    U1, _ = rand_unimodular(rng, n)
    if symmetric:
        M = matmul(transpose(U1), matmul(D, U1))
    else:
        U2, _ = rand_unimodular(rng, n)
        M = matmul(U1, matmul(D, U2))
    return [[Fraction(x, den) for x in r] for r in M]


def inertia_label(S):
    return inertia(S)


def sorted_hist(items):
    h = {}
    for x in items:
        h[x] = h.get(x, 0) + 1
    return {k: h[k] for k in sorted(h)}


def collapse_flag(S, ne):
    return inertia(S) == [1, 0, ne - 1]


def rank_of(S):
    i = inertia(S)
    return i[0] + i[1]
