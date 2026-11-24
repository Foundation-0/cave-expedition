# Independent exact check of "Theorem B" (rank of S_el for the cross-polytope lattice framework).
# Built from lattice/SPEC.md section 1 only. Fractions only. No bare assert. Deterministic.
import sys, random
from fractions import Fraction as F

FAILS = []
def need(c, m):
    if not c:
        FAILS.append(m)

# ---------------- linear algebra over Q (dense, lists of lists of Fractions) ----------------
def rref(M, ncols=None):
    """return (R, pivots) reduced row echelon form of a copy of M (rows list of lists)."""
    R = [list(r) for r in M]
    if not R:
        return R, []
    nc = len(R[0]) if ncols is None else ncols
    piv = []
    r = 0
    for c in range(nc):
        p = None
        for i in range(r, len(R)):
            if R[i][c] != 0:
                p = i; break
        if p is None:
            continue
        R[r], R[p] = R[p], R[r]
        inv = 1 / R[r][c]
        R[r] = [x * inv for x in R[r]]
        for i in range(len(R)):
            if i != r and R[i][c] != 0:
                f = R[i][c]
                R[i] = [a - f * b for a, b in zip(R[i], R[r])]
        piv.append(c)
        r += 1
        if r == len(R):
            break
    return R, piv

def rank(M):
    if not M or not M[0]:
        return 0
    return len(rref(M)[1])

def nullspace(M, nc):
    """basis of {x : M x = 0}"""
    if not M:
        return [[F(1) if i == j else F(0) for i in range(nc)] for j in range(nc)]
    R, piv = rref(M, nc)
    free = [c for c in range(nc) if c not in piv]
    basis = []
    for f in free:
        v = [F(0)] * nc
        v[f] = F(1)
        for k, c in enumerate(piv):
            v[c] = -R[k][f]
        basis.append(v)
    return basis

def matmul(A, B):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col) if a != 0 and b != 0) for col in Bt] for row in A]

def transpose(A):
    return [list(r) for r in zip(*A)]

# ---------------- the construction (SPEC section 1) ----------------
def build(L):
    n = len(L)
    def x(v):
        a, s = divmod(v, 2)
        e = [F(0)] * n
        e[a] = F(1) if s == 0 else F(-1)
        return e
    bars = []     # (v, u, ell)
    for i in range(n):
        for j in range(i + 1, n):
            for si in (0, 1):
                for sj in (0, 1):
                    v = 2 * i + si; u = 2 * j + sj
                    ell = [a - b for a, b in zip(x(v), x(u))]
                    bars.append((v, u, ell, False))
    for i in range(n):
        u = 2 * i; v = 2 * i + 1
        # ell = x_v - x_u + m L with m = e_i: = -2 e_i + r_i
        ell = [a - b + L[i][k] for k, (a, b) in enumerate(zip(x(v), x(u)))]
        bars.append((v, u, ell, True))
    nstrain = n * (n + 1) // 2
    d0 = []; ae = []
    for (v, u, ell, br) in bars:
        row = [F(0)] * (2 * n * n)
        for k in range(n):
            row[v * n + k] += ell[k]
            row[u * n + k] -= ell[k]
        d0.append(row)
        a = [ell[k] * ell[k] for k in range(n)]
        for k in range(n):
            for l in range(k + 1, n):
                a.append(2 * ell[k] * ell[l])
        ae.append(a)
    return bars, d0, ae

def S_spec(L):
    """S = K + B^T X with Delta X = -B  (free variables 0); W = 1/2."""
    bars, d0, ae = build(L)
    nu = len(d0[0]); ns = len(ae[0])
    half = F(1, 2)
    Dl = [[F(0)] * nu for _ in range(nu)]
    Bm = [[F(0)] * ns for _ in range(nu)]
    Km = [[F(0)] * ns for _ in range(ns)]
    for r, a in zip(d0, ae):
        nzr = [(i, x) for i, x in enumerate(r) if x != 0]
        nza = [(i, x) for i, x in enumerate(a) if x != 0]
        for i, x in nzr:
            for j, y in nzr:
                Dl[i][j] += half * x * y
            for j, y in nza:
                Bm[i][j] += half * x * y
        for i, x in nza:
            for j, y in nza:
                Km[i][j] += half * x * y
    aug = [Dl[i] + [-b for b in Bm[i]] for i in range(nu)]
    R, piv = rref(aug, nu)
    # consistency: rows beyond the pivots must have zero RHS
    cons = all(all(x == 0 for x in R[k][nu:]) for k in range(len(piv), len(R)))
    X = [[F(0)] * ns for _ in range(nu)]
    for k, c in enumerate(piv):
        X[c] = R[k][nu:]
    S = [[Km[i][j] + sum(Bm[t][i] * X[t][j] for t in range(nu) if Bm[t][i] != 0 and X[t][j] != 0) for j in range(ns)] for i in range(ns)]
    return S, cons

def left_kernel(d0):
    """basis of self-stresses: y with d0^T y = 0"""
    return nullspace(transpose(d0), len(d0))

def rank_via_stress(L):
    bars, d0, ae = build(L)
    N = left_kernel(d0)
    ns = len(ae[0])
    M = [[sum(y[e] * ae[e][c] for e in range(len(ae)) if y[e] != 0) for c in range(ns)] for y in N]
    return rank(M) if M else 0, len(N), rank(d0)

def S_projector(L):
    """S = (1/2) ae^T Pi ae, Pi orthogonal projector onto self-stress space (second construction, same SPEC)"""
    bars, d0, ae = build(L)
    N = left_kernel(d0)
    ns = len(ae[0])
    if not N:
        return [[F(0)] * ns for _ in range(ns)]
    M = [[sum(y[e] * ae[e][c] for e in range(len(ae)) if y[e] != 0) for c in range(ns)] for y in N]
    G = [[sum(a * b for a, b in zip(y1, y2)) for y2 in N] for y1 in N]
    # G^{-1} M by solving G Z = M
    aug = [G[i] + M[i] for i in range(len(N))]
    R, piv = rref(aug, len(N))
    Z = [R[k][len(N):] for k in range(len(N))]       # G invertible: pivots on all columns
    S = [[F(1, 2) * sum(M[k][i] * Z[k][j] for k in range(len(N))) for j in range(ns)] for i in range(ns)]
    return S

# ---------------- the formula ----------------
def matL2(L):
    n = len(L)
    Bm = [[L[i][j] - (2 if i == j else 0) for j in range(n)] for i in range(n)]
    return matmul(L, Bm), Bm

def dimZ_and_second(L, Bvariant=False):
    n = len(L)
    rows = []
    for i in range(n):
        for j in range(i + 1, n):
            r = [F(0)] * n
            r[i] += L[i][j]
            r[j] -= L[j][i]
            rows.append(r)
    dimZ = n - (rank(rows) if rows else 0)
    LB, Bm = matL2(L)
    ref = Bm if Bvariant else LB
    extra = []
    for i in range(n):
        if any(x != 0 for x in ref[i]):
            e = [F(0)] * n; e[i] = F(1); extra.append(e)
    dim2 = n - rank(rows + extra)
    return dimZ, dim2

def formula(L):
    dz, d2 = dimZ_and_second(L)
    return dz - d2

# ---------------- matrix families ----------------
def rint(r, lo=-3, hi=3):
    return r.randint(lo, hi)
def mat(n, f):
    return [[F(f(i, j)) for j in range(n)] for i in range(n)]
def rand_int(r, n):
    return mat(n, lambda i, j: rint(r))
def rand_rat(r, n):
    return mat(n, lambda i, j: F(rint(r, -4, 4), r.choice([1, 2, 3, 4])))
def rand_diag(r, n):
    return mat(n, lambda i, j: (rint(r, -2, 4) if i == j else 0))
def rand_sym(r, n):
    A = rand_int(r, n)
    return [[A[min(i, j)][max(i, j)] for j in range(n)] for i in range(n)]
def rand_symmetrizable(r, n):
    S = rand_sym(r, n)
    d = [F(r.choice([-3, -2, -1, 1, 2, 3, 1, 1])) for _ in range(n)]
    return [[S[i][j] / d[i] for j in range(n)] for i in range(n)]
def block_diag(blocks):
    n = sum(len(b) for b in blocks)
    L = [[F(0)] * n for _ in range(n)]
    o = 0
    for b in blocks:
        for i in range(len(b)):
            for j in range(len(b)):
                L[o + i][o + j] = b[i][j]
        o += len(b)
    return L
def rand_blocks_symmetrizable(r, n):
    sizes = []
    left = n
    while left > 0:
        s = r.randint(1, left); sizes.append(s); left -= s
    return block_diag([rand_symmetrizable(r, s) for s in sizes])
def unimod(r, n, steps=12):
    U = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    Ui = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    for _ in range(steps):
        i = r.randrange(n); j = r.randrange(n)
        if i == j:
            continue
        c = r.choice([-1, 1, 2, -2])
        # U <- (I + c e_i e_j^T) U   ; Ui <- Ui (I - c e_i e_j^T)
        U[i] = [a + c * b for a, b in zip(U[i], U[j])]
        for k in range(n):
            Ui[k][j] -= c * Ui[k][i]
    return U, Ui
def conj(U, Ui, J):
    return matmul(matmul(U, J), Ui)
def rand_2proj(r, n):
    k = r.randint(0, n)
    U, Ui = unimod(r, n)
    J = mat(n, lambda i, j: (2 if (i == j and i < k) else 0))
    return conj(U, Ui, J)                 # L = 2 P, P idempotent  => L(L-2I)=0
def rand_sym_2proj(r, n):
    v = [F(rint(r, -2, 2)) for _ in range(n)]
    if all(x == 0 for x in v):
        v[0] = F(1)
    vv = sum(x * x for x in v)
    return [[2 * v[i] * v[j] / vv for j in range(n)] for i in range(n)]
def rand_nilpotent(r, n):
    N = mat(n, lambda i, j: (rint(r) if j > i else 0))
    U, Ui = unimod(r, n, 8)
    return conj(U, Ui, N)
def rand_scalar_plus_nil(r, n):
    c = r.choice([0, 1, 2, 3, F(1, 2), -1])
    N = rand_nilpotent(r, n)
    return [[N[i][j] + (c if i == j else 0) for j in range(n)] for i in range(n)]
def rand_jordan(r, n):
    c = r.choice([0, 1, 2, 3])
    J = mat(n, lambda i, j: (c if i == j else (1 if (j == i + 1 and r.random() < 0.7) else 0)))
    U, Ui = unimod(r, n, 8)
    return conj(U, Ui, J)
def rand_scalar(r, n):
    c = r.choice([0, 1, 2, 3, -1, F(5, 2)])
    return mat(n, lambda i, j: c if i == j else 0)
def two_plus_sym_block(r, n):
    L = mat(n, lambda i, j: 2 if i == j else 0)
    k = r.randint(2, n)
    S = rand_sym(r, k)
    for i in range(k):
        for j in range(k):
            if i != j:
                L[i][j] = S[i][j]
    return L
def rand_sparse(r, n):
    return mat(n, lambda i, j: (rint(r) if r.random() < 0.35 else 0))
def rand_zero_rows(r, n):
    L = rand_int(r, n)
    for i in range(n):
        if r.random() < 0.3:
            L[i] = [F(0)] * n
    return L

FAMILIES = [("random int", rand_int), ("random rational", rand_rat), ("diagonal", rand_diag), ("symmetric", rand_sym),
            ("symmetrizable, generic D", rand_symmetrizable), ("symmetrizable, several D (blocks)", rand_blocks_symmetrizable),
            ("L(L-2I)=0, nonsymmetric 2P", rand_2proj), ("L(L-2I)=0, symmetric 2P", rand_sym_2proj),
            ("nilpotent (conjugated)", rand_nilpotent), ("c I + nilpotent", rand_scalar_plus_nil), ("Jordan-type repeated eigenvalue", rand_jordan),
            ("scalar c I", rand_scalar), ("2I + symmetric block", two_plus_sym_block), ("sparse random", rand_sparse), ("zero rows", rand_zero_rows)]

def show(L):
    return "[" + "; ".join(" ".join(str(x) for x in row) for row in L) + "]"

WRONG = {
    "F1 drop second term (rank=dim Z_B)": lambda L: dimZ_and_second(L)[0],
    "F2 off by one (formula+1)": lambda L: formula(L) + 1,
    "F3 row test uses L-2I instead of L(L-2I)": lambda L: (lambda a: a[0] - a[1])(dimZ_and_second(L, True)),
    "F4 rank = min(dim Z_B,1)": lambda L: min(dimZ_and_second(L)[0], 1),
}

def main():
    P = print
    # --- step checks and the two constructions agree
    P("== B0: two constructions of S_el (SPEC Schur with free vars 0 vs (1/2) ae^T Pi ae) agree exactly ==")
    r = random.Random(777)
    agree = 0; tot = 0
    for t in range(40):
        n = r.choice([3, 3, 4])
        fam = FAMILIES[t % len(FAMILIES)]
        L = fam[1](r, n)
        S1, cons = S_spec(L); S2 = S_projector(L)
        tot += 1
        need(cons, "inconsistent system")
        if S1 == S2: agree += 1
        else: need(False, "constructions disagree " + show(L))
    P("   %d of %d agree (n=3,4, all 15 families rotated)" % (agree, tot))

    # --- main panel
    P("== B1: rank(S_el) vs formula ==")
    counts = {3: 60, 4: 40, 5: 12, 6: 3}
    total = 0; mism = 0; wrongc = {k: 0 for k in WRONG}
    famstat = {}
    cx = []
    rankhist = {}
    for n in (3, 4, 5, 6):
        for fi, (fname, f) in enumerate(FAMILIES):
            for t in range(counts[n]):
                r = random.Random(1000000 * n + 1000 * fi + t)
                L = f(r, n)
                S, cons = S_spec(L) if n <= 5 else (None, True)
                need(cons, "inconsistent")
                if n <= 5:
                    rk = rank(S)
                    rk2 = rank_via_stress(L)[0]
                    need(rk == rk2, "S rank vs stress-map rank differ " + show(L))
                else:
                    rk = rank_via_stress(L)[0]
                fm = formula(L)
                total += 1
                key = (fname, n)
                st = famstat.setdefault(fname, [0, 0])
                st[0] += 1
                if rk != fm:
                    mism += 1; st[1] += 1
                    if len(cx) < 5: cx.append((n, show(L), rk, fm))
                for k, w in WRONG.items():
                    if w(L) != rk:
                        wrongc[k] += 1
                dz = dimZ_and_second(L)[0]
                rankhist[(dz, rk)] = rankhist.get((dz, rk), 0) + 1
    P("   instances: %d (n=3: %d, n=4: %d, n=5: %d, n=6: %d per family x 15 families)" % (total, counts[3], counts[4], counts[5], counts[6]))
    P("   mismatches between actual rank and formula: %d" % mism)
    for c in cx:
        P("   COUNTEREXAMPLE n=%d L=%s actual=%d formula=%d" % c)
    for fname in [f[0] for f in FAMILIES]:
        P("   family %-36s %4d instances, %d mismatches" % (fname, famstat[fname][0], famstat[fname][1]))
    P("   (dim Z_B, actual rank) -> count: " + ", ".join("%s:%d" % (k, v) for k, v in sorted(rankhist.items())))
    P("== must-fail controls (wrong formulas; must disagree with the actual rank somewhere) ==")
    for k in sorted(wrongc):
        P("   %-45s disagrees on %d of %d" % (k, wrongc[k], total))
        need(wrongc[k] > 0, "wrong formula not caught: " + k)
    need(mism == 0, "formula mismatch for n>=3")

    # --- n = 2
    P("== B2: n = 2 ==")
    for name, L in (("diag(3,2)", [[F(3), F(0)], [F(0), F(2)]]), ("3 I", [[F(3), F(0)], [F(0), F(3)]])):
        S, cons = S_spec(L)
        P("   L=%s: actual rank %d, stress-map rank %d, formula %d" % (name, rank(S), rank_via_stress(L)[0], formula(L)))
        need(cons, "inconsistent n=2")
    n2m = 0; n2t = 0
    for t in range(400):
        r = random.Random(9000000 + t)
        fam = FAMILIES[t % len(FAMILIES)]
        L = fam[1](r, 2)
        S, cons = S_spec(L)
        n2t += 1
        if rank(S) != formula(L): n2m += 1
    P("   random n=2 instances: %d, formula wrong on %d" % (n2t, n2m))
    need(n2m > 0, "n=2 should show failures")
    wit = [[F(3), F(0)], [F(0), F(2)]]
    S, _ = S_spec(wit)
    need(rank(S) == 0 and formula(wit) == 1, "n=2 witness diag(3,2)")
    wit = [[F(3), F(0)], [F(0), F(3)]]
    S, _ = S_spec(wit)
    need(rank(S) == 1 and formula(wit) == 2, "n=2 witness 3I")

    # --- B3: step checks of the proof
    P("== B3: proof-step checks ==")
    # step 2: dimension of the infinitesimal flexes of the intra-cell framework (bars only, no bridges)
    for n in (2, 3, 4, 5, 6):
        L = [[F(0)] * n for _ in range(n)]
        bars, d0, ae = build(L)
        intra = [row for row, b in zip(d0, bars) if not b[3]]
        dimker = 2 * n * n - rank(intra)
        P("   n=%d: dim ker(d0 intra) = %d; translations+rotations = %d" % (n, dimker, n + n * (n - 1) // 2))
        if n >= 3:
            need(dimker == n + n * (n - 1) // 2, "flex dimension n=%d" % n)
        else:
            need(dimker == n + n * (n - 1) // 2 + 1, "n=2 extra flex")
    # steps 3-5: z lifts to a self-stress iff z in Z_B ; virial of the lift equals sigma_c(z) = (sigma_ii | 2 sigma_ij), sigma = diag(z) L (L-2I) on Z_B
    ok_lift = 0; bad_lift = 0; ok_nolift = 0; tested_nolift = 0; ok_vir = 0; tested_vir = 0
    for t in range(60):
        r = random.Random(4000000 + t)
        n = r.choice([3, 4, 5])
        fam = FAMILIES[[4, 5, 6, 7, 2, 12, 3][t % 7]]
        L = fam[1](r, n)
        bars, d0, ae = build(L)
        nb = n * (n - 1) * 2
        # equations: for stress w = (y, z): d0^T w = 0.  Solve for y given z by RREF on [d0_intra^T | d0_bridge^T z]
        d0t = transpose(d0)
        # Z_B basis
        rows = []
        for i in range(n):
            for j in range(i + 1, n):
                row = [F(0)] * n; row[i] += L[i][j]; row[j] -= L[j][i]; rows.append(row)
        ZB = nullspace(rows, n)
        # a random z not in Z_B (when Z_B != all)
        def lift(z):
            nbar = len(bars)
            cols = [c for c in range(nbar) if not bars[c][3]]
            A = [[d0t[rw][c] for c in cols] + [-sum(d0t[rw][nb + i] * z[i] for i in range(n))] for rw in range(len(d0t))]
            R, piv = rref(A, len(cols))
            if any(R[k][len(cols)] != 0 for k in range(len(piv), len(R))):
                return None
            y = [F(0)] * len(cols)
            for k, c in enumerate(piv):
                y[c] = R[k][len(cols)]
            w = [F(0)] * nbar
            for k, c in enumerate(cols):
                w[c] = y[k]
            for i in range(n):
                w[nb + i] = z[i]
            return w
        for z in ZB:
            w = lift(z)
            if w is None:
                bad_lift += 1; need(False, "z in Z_B did not lift " + show(L)); continue
            ok_lift += 1
            vir = [sum(w[e] * ae[e][c] for e in range(len(ae))) for c in range(len(ae[0]))]
            # sigma = diag(z) L (L-2I)
            LB, Bm = matL2(L)
            sig = [[z[i] * LB[i][j] for j in range(n)] for i in range(n)]
            sc = [sig[i][i] for i in range(n)] + [2 * sig[i][j] for i in range(n) for j in range(i + 1, n)]
            tested_vir += 1
            if vir == sc: ok_vir += 1
            else: need(False, "virial != sigma_c " + show(L))
        z = [F(r.randint(-3, 3)) for _ in range(n)]
        inZ = all(sum(rows[k][i] * z[i] for i in range(n)) == 0 for k in range(len(rows)))
        w = lift(z)
        tested_nolift += 1
        if (w is not None) == inZ: ok_nolift += 1
        else: need(False, "lift exists iff z in Z_B violated " + show(L))
    P("   z in Z_B basis vectors lifted to self-stresses: %d (failures %d); virial of lift == diag(z)L(L-2I) in strain coordinates: %d of %d" % (ok_lift, bad_lift, ok_vir, tested_vir))
    P("   random z: 'lift exists iff z in Z_B' held on %d of %d" % (ok_nolift, tested_nolift))
    if FAILS:
        P("FAILURES: %d" % len(FAILS))
        for f in FAILS[:20]:
            P("  " + f)
        sys.exit(1)
    P("ALL CHECKS PASSED, ALL CONTROLS CAUGHT")
    sys.exit(0)

main()
