#!/usr/bin/env python3
"""law2b_check.py: exact Law-2b (transform before dismissal) checker for the gate5-unification rulings.
Usage: python3 -I -B law2b_check.py <path to verification/outside/gate5-unification>
Python 3.12 standard library only; Fractions and ints only on every decision path; no bare assert.
Shares no code with the team certifier (symbiosis/round10/arm5-transformational-steelman)."""
from fractions import Fraction as F

# ---------- matrices (list of lists of Fraction) ----------
def mat(rows): return [[F(x) for x in r] for r in rows]
def zeros(n, m): return [[F(0)] * m for _ in range(n)]
def eye(n): return [[F(1) if i == j else F(0) for j in range(n)] for i in range(n)]
def tr(A): return [list(r) for r in zip(*A)] if A else []
def mm(A, B):
    Bt = tr(B)
    return [[sum((a * b for a, b in zip(r, c) if a and b), F(0)) for c in Bt] for r in A]
def madd(A, B): return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]
def msub(A, B): return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]
def msc(c, A): return [[c * a for a in r] for r in A]
def sub(A, rows, cols): return [[A[i][j] for j in cols] for i in rows]
def is_zero(A): return all(x == 0 for r in A for x in r)
def is_sym(A): return all(A[i][j] == A[j][i] for i in range(len(A)) for j in range(i))

def rref(A):
    """returns (R, pivots) exact"""
    M = [list(r) for r in A]; n = len(M); m = len(M[0]) if n else 0
    piv = []; r = 0
    for c in range(m):
        p = next((i for i in range(r, n) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        if pv != 1: M[r] = [x / pv for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                f = M[i][c]; Mr = M[r]
                M[i] = [x - f * y for x, y in zip(M[i], Mr)]
        piv.append(c); r += 1
        if r == n: break
    return M, piv
def rank(A): return len(rref(A)[1]) if A and A[0] else 0
def nullspace(A, m=None):
    """basis of {x : A x = 0}, list of vectors"""
    if not A: return [[F(int(i == j)) for j in range(m)] for i in range(m)]
    m = len(A[0]); R, piv = rref(A)
    free = [c for c in range(m) if c not in piv]; out = []
    for f in free:
        v = [F(0)] * m; v[f] = F(1)
        for i, pc in enumerate(piv): v[pc] = -R[i][f]
        out.append(v)
    return out
def det(A):
    M = [list(r) for r in A]; n = len(M); d = F(1)
    for c in range(n):
        p = next((i for i in range(c, n) if M[i][c] != 0), None)
        if p is None: return F(0)
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for i in range(c + 1, n):
            if M[i][c] != 0:
                f = M[i][c] / M[c][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[c])]
    return d
def inv(A):
    n = len(A); aug = [list(A[i]) + [F(int(i == j)) for j in range(n)] for i in range(n)]
    R, piv = rref(aug)
    if piv[:n] != list(range(n)) or len(piv) < n: return None
    return [r[n:] for r in R]
def solve_consistent(A, Bm):
    """one solution X (free vars 0) of A X = Bm, or None if inconsistent"""
    n = len(A); m = len(A[0]); k = len(Bm[0])
    aug = [list(A[i]) + list(Bm[i]) for i in range(n)]
    R, piv = rref(aug)
    if any(c >= m for c in piv): return None
    X = zeros(m, k)
    for i, pc in enumerate(piv): X[pc] = list(R[i][m:])
    return X
def schur(M, piv, rest):
    A = sub(M, piv, piv); B = sub(M, piv, rest); C = sub(M, rest, piv); D = sub(M, rest, rest)
    Ai = inv(A)
    if Ai is None: return None
    return msub(D, mm(mm(C, Ai), B))

# ---------- inertia of symmetric rational matrices: congruence elimination ----------
def inertia_sym(A):
    """(n+, n-, n0) by exact symmetric elimination with 2x2 pivots when needed"""
    M = [list(r) for r in A]; n = len(M); pos = neg = 0
    idx = list(range(n))
    def cong_add(i, j):  # row_i += row_j, col_i += col_j  (congruence by I + e_j e_i^T)
        M[i] = [a + b for a, b in zip(M[i], M[j])]
        for r in range(len(M)): M[r][i] = M[r][i] + M[r][j]
    size = n
    while size:
        k = next((i for i in range(size) if M[i][i] != 0), None)
        if k is None:
            pr = next(((i, j) for i in range(size) for j in range(i + 1, size) if M[i][j] != 0), None)
            if pr is None: break
            cong_add(pr[0], pr[1]); k = pr[0]
        # swap k to 0
        M[0], M[k] = M[k], M[0]
        for r in M: r[0], r[k] = r[k], r[0]
        p = M[0][0]
        if p > 0: pos += 1
        else: neg += 1
        for i in range(1, size):
            if M[i][0] != 0:
                f = M[i][0] / p
                M[i] = [x - f * y for x, y in zip(M[i], M[0])]
        for i in range(1, size):
            if M[0][i] != 0: M[0][i] = F(0)
        M = [r[1:] for r in M[1:]]; size -= 1
    return (pos, neg, size)

# ---------- polynomials (low->high coefficient lists of Fraction) ----------
def ptrim(p):
    p = list(p)
    while p and p[-1] == 0: p.pop()
    return p
def padd(p, q):
    n = max(len(p), len(q)); return ptrim([(p[i] if i < len(p) else F(0)) + (q[i] if i < len(q) else F(0)) for i in range(n)])
def pmul(p, q):
    if not p or not q: return []
    r = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q): r[i + j] += a * b
    return ptrim(r)
def pder(p): return ptrim([i * p[i] for i in range(1, len(p))])
def pdivmod(p, q):
    p = ptrim(p); q = ptrim(q); out = [F(0)] * max(len(p) - len(q) + 1, 0)
    while len(p) >= len(q) and p:
        c = p[-1] / q[-1]; d = len(p) - len(q); out[d] = c
        p = ptrim([a - (c * q[i - d] if 0 <= i - d < len(q) else 0) for i, a in enumerate(p)])
    return ptrim(out), p
from math import gcd as _igcd
def _prim_int(p):
    """scale a Fraction poly to a primitive integer poly (same roots)"""
    p = ptrim(p)
    if not p: return []
    den = 1
    for a in p: den = den * a.denominator // _igcd(den, a.denominator)
    ip = [int(a * den) for a in p]
    g = 0
    for a in ip: g = _igcd(g, abs(a))
    return [F(a // g) for a in ip]
def pgcd(p, q):
    p, q = _prim_int(p), _prim_int(q)
    while q:
        # pseudo-remainder keeps integers small; primitive part after each step
        r = ptrim(p)
        lc = q[-1]
        while len(r) >= len(q) and r:
            c = r[-1]; d = len(r) - len(q)
            r = ptrim([a * lc - (c * q[i - d] if 0 <= i - d < len(q) else 0) for i, a in enumerate(r)])
        p, q = q, _prim_int(r)
    return [x / p[-1] for x in p] if p else p
def peval(p, x):
    r = F(0)
    for a in reversed(p): r = r * x + a
    return r
def charpoly(A):
    """Faddeev-LeVerrier: returns monic coefficients low->high"""
    n = len(A); M = zeros(n, n); c = [F(0)] * (n + 1); c[n] = F(1)
    I = eye(n)
    for k in range(1, n + 1):
        M = madd(mm(A, M), msc(c[n - k + 1], I)) if k > 1 else I
        AM = mm(A, M)
        c[n - k] = -sum((AM[i][i] for i in range(n)), F(0)) / k
    return c
def squarefree(p):
    g = pgcd(p, pder(p)); return pdivmod(p, g)[0] if g and len(g) > 1 else ptrim(p)
def sturm_real_roots(p):
    """number of distinct real roots of p (any p): via squarefree part and Sturm chain"""
    p = squarefree(ptrim(p))
    if len(p) <= 1: return 0
    chain = [p, pder(p)]
    while chain[-1]:
        r = pdivmod(chain[-2], chain[-1])[1]
        if not r: break
        chain.append([-x for x in r])
    chain = [c for c in chain if c]
    def sgn_inf(c, plus): 
        v = c[-1]; 
        if not plus and (len(c) - 1) % 2: v = -v
        return 1 if v > 0 else -1
    def changes(signs): 
        s = [x for x in signs if x != 0]; return sum(1 for a, b in zip(s, s[1:]) if a != b)
    return changes([sgn_inf(c, False) for c in chain]) - changes([sgn_inf(c, True) for c in chain])
def mpoly_eval(p, A):
    n = len(A); R = zeros(n, n); I = eye(n)
    for a in reversed(p): R = madd(mm(R, A), msc(a, I))
    return R

# ================= common helpers (checker bookkeeping, rng, spectral inertia) =================
import json, sys, os
from math import isqrt

REPORT = {"checks": [], "numbers": {}, "tables": {}, "specs": {}, "controls": []}
FAILS = []

def check(cid, ok, detail=""):
    """record a check; failures are collected and make the exit code non-zero (no bare assert anywhere)"""
    ok = bool(ok)
    REPORT["checks"].append({"id": cid, "ok": ok, "detail": detail})
    if not ok: FAILS.append(cid)
    return ok

def control(cid, rejected, detail=""):
    """a must-fail control: `rejected` must be True (the checker refused the bad input). Else the run fails."""
    rejected = bool(rejected)
    REPORT["controls"].append({"id": cid, "rejected": rejected, "detail": detail})
    if not rejected: FAILS.append("CONTROL_PASSED_BUT_MUST_FAIL:" + cid)
    return rejected

def fs(x):
    if isinstance(x, F): return str(x)
    if isinstance(x, (list, tuple)): return [fs(y) for y in x]
    if isinstance(x, dict): return {str(k): fs(v) for k, v in x.items()}
    return x

class Rng:
    """splitmix64, deterministic"""
    def __init__(self, seed): self.s = seed & 0xFFFFFFFFFFFFFFFF
    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)
    def randint(self, lo, hi): return lo + self.next() % (hi - lo + 1)

def is_rat_square(r):
    r = F(r)
    if r < 0: return False
    return isqrt(r.numerator) ** 2 == r.numerator and isqrt(r.denominator) ** 2 == r.denominator

def sym_part(M): return msc(F(1, 2), madd(M, tr(M)))

def largest_inv_sub_in(M, W):
    """dimension of the largest M-invariant subspace contained in span(W) (rows of W are a basis); exact"""
    n = len(M)
    for _ in range(n + 2):
        k = len(W)
        if k == 0: return 0, []
        LN = nullspace(W)                       # vectors orthogonal to span W
        if not LN: return k, W
        MW = [[sum(M[i][l] * W[j][l] for l in range(n)) for i in range(n)] for j in range(k)]   # row j = M w_j
        cons = [[sum(c[i] * MW[j][i] for i in range(n)) for j in range(k)] for c in LN]
        ns = nullspace(cons)
        Wn = [[sum(a[j] * W[j][i] for j in range(k)) for i in range(n)] for a in ns]
        if len(Wn) == k: return k, W
        W = Wn
    return len(W), W

def spectral_inertia_dissipative(X):
    """(#Re>0, #Re<0, #Re=0) of a real square X whose symmetric part is negative semidefinite; None if it is not.
    Reason: Re(lam)|v|^2 = v^* sym(X) v <= 0, so Re lam <= 0; Re lam = 0 forces sym(X) v = 0 (so v lies in ker sym(X));
    purely imaginary eigenvalues of a dissipative matrix are semisimple (|exp(tX)| stays bounded), so their total
    algebraic multiplicity equals the dimension of the largest X-invariant subspace inside ker sym(X)."""
    H = sym_part(X)
    if inertia_sym(H)[0] != 0: return None
    n = len(X)
    m0, _ = largest_inv_sub_in(X, nullspace(H) if rank(H) < n else [])
    return (0, n - m0, m0)

def lyapunov_inertia(M):
    """(#Re>0, #Re<0) of real square M with no imaginary-axis eigenvalue, via M X + X M^T = -I (Taussky/Ostrowski-Schneider):
    n_+(X) = #Re<0 and n_-(X) = #Re>0.  Returns None when the Lyapunov system is singular (imaginary-axis eigenvalue)."""
    n = len(M)
    idx = [(i, j) for i in range(n) for j in range(i, n)]; pos = {p: k for k, p in enumerate(idx)}
    def var(i, j): return pos[(i, j)] if i <= j else pos[(j, i)]
    rows = []; rhs = []
    for (i, j) in idx:
        row = [F(0)] * len(idx)
        for k in range(n):
            if M[i][k] != 0: row[var(k, j)] += M[i][k]
            if M[j][k] != 0: row[var(i, k)] += M[j][k]
        rows.append(row); rhs.append([F(-1) if i == j else F(0)])
    sol = solve_consistent(rows, rhs)
    if sol is None: return None
    # solution may be non-unique when singular; require unique
    if rank(rows) != len(idx): return None
    X = [[sol[var(i, j)][0] for j in range(n)] for i in range(n)]
    p, m, z = inertia_sym(X)
    if z != 0: return None
    return (m, p)    # (#Re>0, #Re<0)

# ================= RULING G5-14 / G5-02 (row 6, open-quantum Liouvillian) =================
def load_json(path):
    with open(path, "r", encoding="utf-8") as fh: return json.load(fh)

def parse_mat(rows): return [[F(x) for x in r] for r in rows]

def pneg(p): return ptrim([a * (-1) ** i for i, a in enumerate(p)])
def ppowmod(q, k, m):
    r = [F(1)]; b = pdivmod(q, m)[1]
    while k:
        if k & 1: r = pdivmod(pmul(r, b), m)[1]
        b = pdivmod(pmul(b, b), m)[1]; k >>= 1
    return r

def row6(PK):
    d = load_json(os.path.join(PK, "hermitian", "objects", "open_quantum_liouvillian.json"))
    pts = d["points"]
    T = {"points": len(pts)}
    per = []
    n_nonsym = n_antic = n_realspec = n_nonreal = n_diag = 0
    n_dis = n_add = n_addA = 0
    n_SH_is_D = n_S_ne_SH = n_hnonscalar = 0
    n_Hsum_ne = 0
    coupling_ok = 0
    for p in pts:
        M = parse_mat(p["full"]); piv = p["pivot_indices"]; rest = p["rest_indices"]; n = len(M)
        A = sub(M, piv, piv); D = sub(M, rest, rest); Bm = sub(M, rest, piv); C = sub(M, piv, rest)
        row = {"label": p["label"]}
        # --- literal claim: M Hermitian (real symmetric) ?
        sym = is_sym(M); n_nonsym += (not sym)
        N = msub(M, tr(M)); row["rank_antisym_part"] = rank(N)
        # coupling antisymmetric ?
        anti = (C == msc(F(-1), tr(Bm))) and not is_zero(Bm); n_antic += anti
        # diagonal-gauge invariant: 2-cycle products m_ij m_ji (invariant under every D^-1 M D); Hermitian needs all >= 0
        prods = [M[i][j] * M[j][i] for i in range(n) for j in range(i + 1, n) if M[i][j] != 0 or M[j][i] != 0]
        row["min_two_cycle_product"] = min(prods)
        # similarity invariants
        cp = charpoly(M); sf = squarefree(cp); nd = len(sf) - 1; nr = sturm_real_roots(cp)
        diag = is_zero(mpoly_eval(sf, M))
        row["distinct_eigs"] = nd; row["distinct_real_eigs"] = nr; row["diagonalizable"] = diag
        similar_to_sym = diag and nr == nd
        row["similar_to_real_symmetric"] = similar_to_sym
        n_realspec += similar_to_sym; n_nonreal += (not similar_to_sym); n_diag += diag
        # T6 / T2 : symmetric part projection kills the coupling
        H = sym_part(M); SH = schur(H, piv, rest); S = schur(M, piv, rest)
        n_SH_is_D += (SH == sym_part(D)); n_S_ne_SH += (S != SH)
        inH = inertia_sym(H); inAH = inertia_sym(sub(H, piv, piv)); inSH = inertia_sym(SH)
        row["In(H)"] = inH; row["In(A_H)+In(S(H))"] = tuple(a + b for a, b in zip(inAH, inSH))
        inSsym = inertia_sym(sym_part(S)); row["In(sym A)+In(sym S(M))"] = tuple(a + b for a, b in zip(inAH, inSsym))
        # T4 : cM + lam I Hermitian iff antisym part vanishes and sym part scalar
        hdiag = {H[i][i] for i in range(n)}; n_hnonscalar += (len(hdiag) > 1 or not all(H[i][j] == 0 for i in range(n) for j in range(n) if i != j))
        # --- the transformed claim: spectral (Lyapunov) inertia additivity
        iM = spectral_inertia_dissipative(M); iA = spectral_inertia_dissipative(A); iS = spectral_inertia_dissipative(S)
        dis = iM is not None and iA is not None and iS is not None
        n_dis += dis
        row["dissipative_M_A_S"] = dis
        if dis:
            row["In_spec(M)"] = iM; row["In_spec(A)+In_spec(S)"] = tuple(a + b for a, b in zip(iA, iS))
            n_add += (iM == tuple(a + b for a, b in zip(iA, iS)))
        # sylvester sum on the unsymmetrised pieces (as the package did): In(sym M) vs In(A) + In(sym S)
        # cross-check of m0 for M by a second method: gcd(charpoly(x), charpoly(-x)^n)
        g = pgcd(cp, ppowmod(pneg(cp), n, cp)); row["m0_gcd_method"] = len(g) - 1
        if dis: check("row6.m0_two_methods." + p["label"], len(g) - 1 == iM[2], "gcd method %d vs invariant-subspace method %d" % (len(g) - 1, iM[2]))
        row["kernel_dim"] = n - rank(M)
        absB = sorted({abs(x) for r_ in Bm for x in r_ if x != 0})
        row["coupling_abs_values"] = absB
        if F(p["params"]["omega"]) == 0:
            coupling_ok += (absB == [2 * F(p["params"]["g"])])
        per.append(row)
    n_w0 = sum(1 for p_ in pts if F(p_["params"]["omega"]) == 0)
    T["coupling_entries_equal_2g_at_omega0"] = [coupling_ok, n_w0]
    check("row6.coupling_is_2g_at_omega0", coupling_ok == n_w0, "nonzero |coupling entries| == {2g} at %d/%d points with omega=0, so the coupling is exactly linear in g and vanishes only at g=0" % (coupling_ok, n_w0))
    T.update({"M_not_symmetric": n_nonsym, "coupling_antisymmetric": n_antic, "similar_to_real_symmetric": n_realspec,
              "has_nonreal_eigenvalue_pair": n_nonreal, "diagonalizable": n_diag, "S_of_symmetric_part_equals_D": n_SH_is_D,
              "S_ne_S_of_symmetric_part": n_S_ne_SH, "sym_part_nonscalar": n_hnonscalar, "dissipative": n_dis,
              "spectral_inertia_additive": n_add})
    check("row6.literal_fails_all", n_nonsym == len(pts) and n_antic == len(pts), "non-symmetric %d/%d, antisymmetric coupling %d/%d" % (n_nonsym, len(pts), n_antic, len(pts)))
    check("row6.all_two_cycle_products_negative_for_coupled_pairs", all(r["min_two_cycle_product"] < 0 for r in per), "min product %s" % min(r["min_two_cycle_product"] for r in per))
    check("row6.T6_sym_projection_decouples", n_SH_is_D == len(pts), "S(sym M) == sym(D) (no elimination effect) at %d/%d points" % (n_SH_is_D, len(pts)))
    check("row6.spectral_additivity_all_points", n_add == len(pts) and n_dis == len(pts), "dissipative %d/%d, additive %d/%d" % (n_dis, len(pts), n_add, len(pts)))
    # exhaustive coordinate-compression check at the first point (2^16 index subsets): compression is symmetric iff coupling inside is zero
    p0 = pts[0]; M0 = parse_mat(p0["full"]); piv0 = p0["pivot_indices"]; rest0 = p0["rest_indices"]
    Bm0 = sub(M0, rest0, piv0)
    ok_all = True; n_sub = 0; n_herm_nontrivial = 0
    nonzero_B = {(i, j) for i in range(len(rest0)) for j in range(len(piv0)) if Bm0[i][j] != 0}
    for mask in range(1, 1 << 16):
        J = [i for i in range(16) if mask >> i & 1]
        Jr = [i for i in J if i in rest0]; Jp = [i for i in J if i in piv0]
        if not Jr or not Jp: continue
        n_sub += 1
        sym_J = is_sym(sub(M0, J, J))
        coupled = any(M0[a][b] != 0 for a in Jr for b in Jp)
        if sym_J == coupled: ok_all = False; break
        if sym_J: n_herm_nontrivial += 1
    check("row6.T6_all_coordinate_compressions", ok_all, "%d partition-respecting coordinate subsets: compression symmetric iff the coupling inside it is zero; %d of them symmetric (all decoupled)" % (n_sub, n_herm_nontrivial))
    T["coordinate_subsets_checked"] = n_sub; T["coordinate_subsets_symmetric_decoupled"] = n_herm_nontrivial
    T["rows"] = per
    # --- null panel for G1: matched random 8x8 systems (4 rest + 4 pivot), same ring, A diagonal negative, D diagonal negative
    rng = Rng(20261122)
    def rand_sys(antisym):
        n = 8; r = list(range(4)); pv = list(range(4, 8))
        M = zeros(n, n)
        for i in r: M[i][i] = F(-rng.randint(1, 9), rng.randint(1, 5))
        for i in pv: M[i][i] = F(-rng.randint(1, 9), rng.randint(1, 5))
        for i in r:
            for j in pv:
                if rng.randint(0, 2) == 0:
                    v = F(rng.randint(-4, 4)); M[i][j] = v
                    M[j][i] = -v if antisym else F(rng.randint(-4, 4))
        return M, pv, r
    def spec_add(M, pv, r):
        S = schur(M, pv, r)
        if S is None: return None
        iM, iA, iS = lyapunov_inertia(M), lyapunov_inertia(sub(M, pv, pv)), lyapunov_inertia(S)
        if None in (iM, iA, iS): return None
        # (#Re>0, #Re<0) pairs; zero count is zero by the no-imaginary-eigenvalue requirement
        return iM == (iA[0] + iS[0], iA[1] + iS[1])
    for tag, anti in (("in_class_antisymmetric_coupling", True), ("out_of_class_independent_coupling", False)):
        n_try = n_ok = n_skip = 0
        while n_try + n_skip < 60:
            M, pv, r = rand_sys(anti)
            res = spec_add(M, pv, r)
            if res is None: n_skip += 1; continue
            n_try += 1; n_ok += res
        T["null_" + tag] = {"tested": n_try, "additive": n_ok, "skipped_singular": n_skip}
    # second panel (added after the clean-room recheck): dense independent coupling, every B and C entry random and nonzero, coupling scale varied
    def rand_sys_dense(scale):
        n = 8; r_ = list(range(4)); pv_ = list(range(4, 8)); M = zeros(n, n)
        for i in range(n): M[i][i] = F(-rng.randint(1, 9), rng.randint(1, 5))
        for i in r_:
            for j in pv_:
                M[i][j] = F((1 if rng.randint(0, 1) else -1) * rng.randint(1, 4)) * scale
                M[j][i] = F((1 if rng.randint(0, 1) else -1) * rng.randint(1, 4)) * scale
        return M, pv_, r_
    dn = dp = dskip = 0
    for scale in (F(1, 4), F(1, 2), F(1), F(2)):
        got = 0
        while got < 15:
            M_, pv_, r_ = rand_sys_dense(scale)
            res_ = spec_add(M_, pv_, r_)
            if res_ is None: dskip += 1; continue
            got += 1; dn += 1; dp += res_
    T["null_dense_independent_coupling"] = {"tested": dn, "additive": dp, "skipped_singular": dskip}
    # cross-check Lyapunov method against the invariant-subspace method on dissipative systems (small)
    agree = 0; tot = 0
    for _ in range(12):
        M, pv, r = rand_sys(True)
        a = lyapunov_inertia(M); b = spectral_inertia_dissipative(M)
        if a is None or b is None: continue
        tot += 1; agree += (a == (b[0], b[1]))
    check("row6.lyapunov_vs_invariant_subspace", tot > 0 and agree == tot, "agree %d/%d" % (agree, tot))
    REPORT["numbers"]["row6"] = T
    return T

# ================= RULING G5-14 / G5-02 (row 4, Q[q] Cole-Hopf lift of the (min,+) coarse-graining object) =================
INF = None
def series_mul(a, b, N):
    r = [F(0)] * (N + 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if i + j > N: break
                if y: r[i + j] += x * y
    return r
def series_add(a, b): return [x + y for x, y in zip(a, b)]
def series_val(a):
    for i, x in enumerate(a):
        if x != 0: return i
    return INF
def smat_mul(A, B, N):
    n, m, k = len(A), len(B), len(B[0])
    R = [[[F(0)] * (N + 1) for _ in range(k)] for _ in range(n)]
    for i in range(n):
        for l in range(m):
            for j in range(k):
                if any(A[i][l]) and any(B[l][j]):
                    R[i][j] = series_add(R[i][j], series_mul(A[i][l], B[l][j], N))
    return R
def smat_val(A): return [[series_val(x) for x in r] for r in A]
def tmin(a, b):
    if a is INF: return b
    if b is INF: return a
    return min(a, b)
def tplus(a, b): return INF if (a is INF or b is INF) else a + b
def trop_star(T):
    """Kleene star of a (min,+) matrix with non-negative entries: min over all walks incl. the empty one"""
    n = len(T); D = [[(0 if i == j else T[i][j]) for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                D[i][j] = tmin(D[i][j], tplus(D[i][k], D[k][j]))
    return D
def keff_series(Ks, B, A, N):
    """Ks: dict-free n x n matrix of truncated series; returns K_eff = K_AA + K_AB (sum_k K_BB^k) K_BA (series), needs val(K_BB)>=1"""
    sel = lambda R, C: [[Ks[i][j] for j in C] for i in R]
    KBB = sel(B, B); b = len(B)
    ident = [[([F(1)] + [F(0)] * N if i == j else [F(0)] * (N + 1)) for j in range(b)] for i in range(b)]
    star = ident; P = ident
    for _ in range(N):
        P = smat_mul(P, KBB, N)
        star = [[series_add(star[i][j], P[i][j]) for j in range(b)] for i in range(b)]
        if all(not any(x) for r in P for x in r): break
    inner = smat_mul(smat_mul(sel(A, B), star, N), sel(B, A), N)
    KAA = sel(A, A)
    return [[series_add(KAA[i][j], inner[i][j]) for j in range(len(A))] for i in range(len(A))]
def trop_eff(T, B, A):
    sel = lambda R, C: [[T[i][j] for j in C] for i in R]
    st = trop_star(sel(B, B)); TAB = sel(A, B); TBA = sel(B, A); TAA = sel(A, A)
    out = []
    for i in range(len(A)):
        row = []
        for j in range(len(A)):
            v = TAA[i][j]
            for b1 in range(len(B)):
                for b2 in range(len(B)):
                    v = tmin(v, tplus(tplus(TAB[i][b1], st[b1][b2]), TBA[b2][j]))
            row.append(v)
        out.append(row)
    return out
def load_K(entries, n, N):
    K = [[[F(0)] * (N + 1) for _ in range(n)] for _ in range(n)]
    for e in entries:
        poly = [F(x) for x in e["poly"]]
        for k, c in enumerate(poly):
            if k <= N: K[e["i"]][e["j"]][k] += c
    return K

def bridge_blocks(K, n, N, blocks):
    """for each block B: if val(K_BB) >= 1 compare val(K_eff) with the tropical elimination; returns (in_hyp, pass, fail_list)"""
    T = smat_val(K)
    inh = ok = 0; bad = []
    for B in blocks:
        A = [i for i in range(n) if i not in B]
        if any(series_val(K[i][j]) == 0 for i in B for j in B): continue   # hypothesis val(K_BB)>=1 violated
        inh += 1
        Ke = keff_series(K, B, A, N); V = smat_val(Ke); TE = trop_eff(T, B, A)
        if V == TE: ok += 1
        else: bad.append(B)
    return inh, ok, bad

def row4(PK):
    d = load_json(os.path.join(PK, "tropical", "objects", "cole_hopf.json"))
    tw = load_json(os.path.join(PK, "tropical", "objects", "tower.json"))
    n = d["K_32"]["n"]; N = 12
    T = {}
    K = load_K(d["K_32"]["K"], n, N); Kp = load_K(d["K_32_doob_peeled"]["K"], n, N)
    dstar = tw["d_star"]
    # --- T1: Doob gauge D^-1 K D with D = diag(q^{d*}) reproduces the stored peeled matrix exactly (entrywise exponent shift)
    exps = {(e["i"], e["j"]): [k for k, c in enumerate(e["poly"]) if F(c) != 0] for e in d["K_32"]["K"]}
    expp = {(e["i"], e["j"]): [k for k, c in enumerate(e["poly"]) if F(c) != 0] for e in d["K_32_doob_peeled"]["K"]}
    gauge_ok = set(exps) == set(expp) and all(
        len(exps[k]) == 1 and expp[k] == [exps[k][0] + dstar[k[1]] - dstar[k[0]]] and all(F(c) in (0, 1) for c in
        [c for e in d["K_32_doob_peeled"]["K"] if (e["i"], e["j"]) == k for c in e["poly"]]) for k in exps)
    check("row4.T1_doob_gauge_exact", gauge_ok, "K_peeled == D^-1 K D, D=diag(q^d*) on all %d entries" % len(exps))
    T["entries"] = len(exps)
    one_way = sorted(k for k in exps if (k[1], k[0]) not in exps)
    T["one_way_edges"] = one_way
    check("row4.support_asymmetric", len(one_way) == 9, "one-way edges: %s" % one_way)
    # gauge-invariant: support pattern. witness (10,0)
    # --- T1/T4: spectrum of K(q0) for rational q0 (exact char poly, squarefree part, Sturm count of distinct real roots)
    spec = {}
    for q0 in (F(1, 2), F(1, 10), F(1, 1000)):
        Kq0 = [[sum((c * q0 ** k for k, c in enumerate(x)), F(0)) for x in r] for r in K]
        cp = charpoly(Kq0); sf = squarefree(cp); nd = len(sf) - 1; nr = sturm_real_roots(cp)
        diag = is_zero(mpoly_eval(sf, Kq0))
        spec[str(q0)] = {"distinct_eigs": nd, "distinct_real_eigs": nr, "diagonalizable": diag}
    check("row4.spectrum_q_half_has_nonreal", 2 <= spec["1/2"]["distinct_real_eigs"] < spec["1/2"]["distinct_eigs"], "K(1/2): %(distinct_eigs)d distinct eigenvalues, %(distinct_real_eigs)d real" % spec["1/2"])
    check("row4.spectrum_small_q_real_diagonalizable", all(spec[k]["distinct_real_eigs"] == spec[k]["distinct_eigs"] == 32 and spec[k]["diagonalizable"] for k in ("1/10", "1/1000")), "at q=1/10 and q=1/1000 all 32 eigenvalues are real and distinct, so K(q) is similar to a real symmetric matrix by a NON-block-diagonal P")
    T["spectrum_by_q"] = spec
    A0 = zeros(n, n)
    for e in d["K_32"]["K"]: A0[e["i"]][e["j"]] = F(1)
    # block nilpotency at the 9 one-way pairs
    nil = 0
    for (i, j) in one_way:
        B = [i, j]; Kb = [[A0[a][b] for b in B] for a in B]
        nil += (not is_zero(Kb)) and is_zero(mm(Kb, Kb))
    T["one_way_pairs_with_nonzero_nilpotent_K_BB"] = nil
    # --- T5: valuation / Kleene-star bridge on all 528 blocks of size 1 and 2
    blocks = [[i] for i in range(n)] + [[i, j] for i in range(n) for j in range(i + 1, n)]
    inh, ok, bad = bridge_blocks(K, n, N, blocks)
    inhp, okp, badp = bridge_blocks(Kp, n, N, blocks)
    T.update({"blocks": len(blocks), "K32_in_hypothesis": inh, "K32_bridge_exact": ok, "peeled_in_hypothesis": inhp, "peeled_bridge_exact": okp})
    check("row4.T5_bridge_K32", inh == len(blocks) and ok == inh, "val(S_ij)==T_ij on %d/%d in-hypothesis blocks (of %d)" % (ok, inh, len(blocks)))
    check("row4.T5_bridge_peeled", okp == inhp and inhp > 0, "peeled matrix: %d/%d in-hypothesis blocks exact; %d blocks outside val(K_BB)>=1" % (okp, inhp, len(blocks) - inhp))
    # --- signed null (G1): random 4x4 matrices over Z[q], same hypothesis val(K_BB)>=1, signed coefficients
    rng = Rng(777001); nn = 4; Ns = 10
    n_s = pass_s = ent_tot = ent_bad = 0
    for _ in range(80):
        Ks = [[[F(0)] * (Ns + 1) for _ in range(nn)] for _ in range(nn)]
        for i in range(nn):
            for j in range(nn):
                if rng.randint(0, 2) < 2:
                    e = rng.randint(1, 2); c = rng.randint(-2, 2)
                    if c: Ks[i][j][e] = F(c)
        B = [0] if rng.randint(0, 1) == 0 else [0, 1]; A = [i for i in range(nn) if i not in B]
        Ke = keff_series(Ks, B, A, Ns); V = smat_val(Ke); TE = trop_eff(smat_val(Ks), B, A)
        n_s += 1; pass_s += (V == TE)
        for r1, r2 in zip(V, TE):
            for a, b in zip(r1, r2):
                ent_tot += 1; ent_bad += (a != b)
    T["signed_null"] = {"samples": n_s, "bridge_exact_on_all_entries": pass_s, "entries": ent_tot, "entries_with_cancellation_gap": ent_bad}
    # --- cancellation witness (T5 gap): K_00 = -q^2, K_01 = K_10 = q, K_11 = 0 :  K_eff_00 = -q^2 + q^2 = 0, so val = inf while T = 2
    Kw = [[[F(0)] * (Ns + 1) for _ in range(2)] for _ in range(2)]
    Kw[0][0][2] = F(-1); Kw[0][1][1] = F(1); Kw[1][0][1] = F(1)
    Vw = smat_val(keff_series(Kw, [1], [0], Ns)); TEw = trop_eff(smat_val(Kw), [1], [0])
    T["cancellation_witness"] = {"val_series": Vw, "tropical": TEw}
    check("row4.T5_cancellation_witness", Vw == [[INF]] and TEw == [[2]], "val(S)=%s vs T=%s: bridge only an inequality when signs cancel" % (Vw, TEw))
    # --- witness that is OUTSIDE the hypothesis val(K_BB) >= 1: K22 = 1 - q, K02 = K21 = q, B = {2}.  K_eff,01 = K01 + K02 (1 - K22)^-1 K21 = q q / q = q  (val 1) while T01 = 2
    okw = True
    for qq in (F(1, 3), F(1, 10), F(1, 100)):
        K22 = 1 - qq; K02 = qq; K21 = qq
        keff01 = K02 * (1 / (1 - K22)) * K21
        okw = okw and keff01 == qq
    T["outside_hypothesis_witness"] = {"K22": "1-q", "K02": "q", "K21": "q", "val_Keff01": 1, "T01": 2, "val_K_BB": 0}
    check("row4.outside_hypothesis_witness", okw, "K_eff,01 = q exactly at q = 1/3, 1/10, 1/100, so val = 1 < T01 = 2 with val(K_BB) = 0")
    # --- matched null MAPS (Gate-5 style): replace valuation by f o val, f random non-decreasing, test commutation with elimination
    rngf = Rng(99001); panel = [[i] for i in (0, 5, 9, 17, 31)] + [[0, 1], [2, 3], [10, 11], [20, 21], [30, 31]]
    def commutes(fmap):
        okc = 0
        for B in panel:
            A = [i for i in range(n) if i not in B]
            Ke = keff_series(K, B, A, N); V = smat_val(Ke)
            Tf = [[(None if x is None else fmap[x]) for x in r] for r in smat_val(K)]
            lhs = [[(None if x is None else fmap[x]) for x in r] for r in V]
            okc += (lhs == trop_eff(Tf, B, A))
        return okc == len(panel)
    true_maps = [{e: c * e for e in range(0, 3 * N + 1)} for c in (1, 2, 3)]
    T["true_homs_commute"] = [commutes(m) for m in true_maps]
    check("row4.T5_scalings_commute", all(T["true_homs_commute"]), "f(e)=c*e, c=1,2,3 commute with elimination on %d blocks" % len(panel))
    nullc = 0; nullt = 40
    for _ in range(nullt):
        f = {0: 0}; acc = 0
        for e in range(1, 3 * N + 1):
            acc += rngf.randint(0, 3); f[e] = acc
        nullc += commutes(f)
    T["null_maps"] = {"samples": nullt, "commuting": nullc}
    # --- T1-spectral rescue on the lift is vacuous: at q = 1/100 every I-K_eff, I-K_BB, I-K is strictly row-diagonally dominant
    q = F(1, 100)
    def at_q(Kser): return [[sum((c * q ** k for k, c in enumerate(x)), F(0)) for x in r] for r in Kser]
    def dominant(Mx): return all(Mx[i][i] > sum((abs(Mx[i][j]) for j in range(len(Mx)) if j != i), F(0)) for i in range(len(Mx)))
    Kq = at_q(K); okdom = 0
    for B in blocks:
        A = [i for i in range(n) if i not in B]
        Ke = at_q(keff_series(K, B, A, N))
        Seff = msub(eye(len(A)), Ke); Abb = msub(eye(len(B)), sub(Kq, B, B))
        okdom += dominant(Seff) and dominant(Abb)
    T["spectral_vacuous_dominant_blocks"] = okdom
    check("row4.spectral_inertia_vacuous_on_lift", okdom == len(blocks) and dominant(msub(eye(n), Kq)), "I-K, I-K_BB, I-K_eff strictly row-diagonally dominant at q=1/100 for %d/%d blocks => In_spec = (size,0,0) everywhere" % (okdom, len(blocks)))
    rngn = Rng(555); nullpass = 0; nulltot = 40
    for _ in range(nulltot):
        Mn = zeros(12, 12)
        for i in range(12):
            for j in range(12):
                if rngn.randint(0, 3) == 0: Mn[i][j] = q
        nullpass += dominant(msub(eye(12), Mn))
    T["spectral_null_all_positive"] = {"samples": nulltot, "all_positive_spectrum": nullpass}
    # tower (T6 quotient) exact facts
    T["tower_sum_d_star"] = sum(tw["d_star"]); T["tower_H_equals_d_star"] = tw["H_total"] == tw["d_star"]
    check("row4.tower_sum", T["tower_sum_d_star"] == 124 and T["tower_H_equals_d_star"], "sum d* = %d" % T["tower_sum_d_star"])
    REPORT["numbers"]["row4"] = T
    return T

# ================= RULING G5-04 (rows 1, 5, 6 are not partition-respecting equivalent) =================
def hermitian_to_real(Mc):
    """a Hermitian matrix with entries 'a+bi' strings -> real symmetric 2n x 2n embedding [[Re,-Im],[Im,Re]] (inertia doubles)"""
    def parse(s):
        s = s.replace(" ", "")
        if "i" not in s: return F(s), F(0)
        body = s[:-1]
        # find the split between real and imaginary part: last + or - that is not at index 0
        k = max(body.rfind("+"), body.rfind("-"))
        if k <= 0: return F(0), F(body if body not in ("", "+", "-") else body + "1")
        im = body[k:]
        if im in ("+", "-"): im += "1"
        return F(body[:k]), F(im)
    n = len(Mc); Re = zeros(n, n); Im = zeros(n, n)
    for i in range(n):
        for j in range(n):
            Re[i][j], Im[i][j] = parse(Mc[i][j])
    R = zeros(2 * n, 2 * n)
    for i in range(n):
        for j in range(n):
            R[i][j] = Re[i][j]; R[i][n + j] = -Im[i][j]; R[n + i][j] = Im[i][j]; R[n + i][n + j] = Re[i][j]
    return R

def equiv_data(M, piv, rest):
    A = sub(M, piv, piv); S = schur(M, piv, rest)
    return {"inA": inertia_sym(A), "inS": inertia_sym(S), "detA": det(A), "detS": det(S)}

def same_sq(x, y):
    """same square class over Q (both zero counts as equal, one zero does not)"""
    x = F(x); y = F(y)
    if x == 0 or y == 0: return x == y
    return is_rat_square(x / y)

def real_equiv(a, b): return a["inA"] == b["inA"] and a["inS"] == b["inS"]
def q_equiv_necessary(a, b):
    return real_equiv(a, b) and same_sq(a["detA"], b["detA"]) and same_sq(a["detS"], b["detS"])

def equiv_search(PK):
    sp = load_json(os.path.join(PK, "hermitian", "objects", "spectral_inertia_hermitian.json"))["points"]
    ae = load_json(os.path.join(PK, "hermitian", "objects", "aest_gravity_hamiltonian.json"))["points"]
    lq = load_json(os.path.join(PK, "hermitian", "objects", "open_quantum_liouvillian.json"))["points"]
    T = {}
    def Bm(p):
        S, t, u = [F(p["scalars"][k]) for k in "Stu"]; b = F(p["b"])
        return mat([[S, t, u], [t, b, 0], [u, 0, 0]])
    O1 = [(p["label"], Bm(p)) for p in sp]
    O5 = [(p["label"], parse_mat(p["full"])) for p in ae]
    D1 = [(l, equiv_data(M, [0, 1], [2])) for l, M in O1]; D5 = [(l, equiv_data(M, [0, 1], [2])) for l, M in O5]
    # cross-check one object's Schur complement against the Hermitian 4x4 object of the same point (R_opt identity): independent embedding check
    cascade = {"pivot_inertia": 0, "reduced_inertia": 0, "pivot_det_square_class": 0, "reduced_det_square_class": 0, "equivalent": 0}
    real_eq = 0
    for _, a in D1:
        for _, b in D5:
            if a["inA"] != b["inA"]: cascade["pivot_inertia"] += 1
            elif a["inS"] != b["inS"]: cascade["reduced_inertia"] += 1
            elif not same_sq(a["detA"], b["detA"]): cascade["pivot_det_square_class"] += 1; real_eq += 1
            elif not same_sq(a["detS"], b["detS"]): cascade["reduced_det_square_class"] += 1; real_eq += 1
            else: cascade["equivalent"] += 1; real_eq += 1
    T["pairs"] = len(D1) * len(D5); T["cascade"] = cascade; T["real_equivalent_pairs"] = real_eq
    check("equiv.literal_fails_all_pairs", cascade["equivalent"] == 0 and sum(cascade.values()) == len(D1) * len(D5), str(cascade))
    check("equiv.reproduces_package_108", cascade["reduced_inertia"] == 108, "pairs failing on the inertia of the reduced block: %d (package: 108)" % cascade["reduced_inertia"])
    # Hermitian M_full (rows 1) real-embedding inertia sanity: n+ doubles
    herm_ok = 0
    for p in sp:
        R = hermitian_to_real(p["M_full"]); i = inertia_sym(R); herm_ok += (i[0] % 2 == 0 and i[1] % 2 == 0 and i[2] % 2 == 0)
    check("equiv.hermitian_embedding_even", herm_ok == len(sp), "real embedding of the 4x4 Hermitian objects has even inertia at %d/%d points" % (herm_ok, len(sp)))
    # --- T1/T2/T3 class invariants: congruence-type maps keep (In A, In S). exact check on random partition-respecting congruences
    rng = Rng(424242); kept = tot = 0
    for l, M in O1 + O5:
        base = equiv_data(M, [0, 1], [2])
        for _ in range(6):
            # random partition-respecting congruence P = diag(P_A (2x2 invertible), p_S nonzero scalar) with rational entries
            while True:
                PA = [[F(rng.randint(-3, 3)) for _ in range(2)] for _ in range(2)]
                if det(PA) != 0: break
            ps = F(rng.randint(1, 5), rng.randint(1, 5)) * (1 if rng.randint(0, 1) else -1)
            P = zeros(3, 3); P[0][0], P[0][1], P[1][0], P[1][1] = PA[0][0], PA[0][1], PA[1][0], PA[1][1]; P[2][2] = ps
            M2 = mm(mm(tr(P), M), P)
            d2 = equiv_data(M2, [0, 1], [2]); tot += 1; kept += (d2["inA"] == base["inA"] and d2["inS"] == base["inS"])
    T["congruence_invariance"] = {"tested": tot, "inertia_pair_preserved": kept}
    check("equiv.congruence_preserves_inertia_pair", kept == tot, "%d/%d" % (kept, tot))
    # --- T4: one global shift M + lam*I with lam fixed by a data-independent bound: here lam0 = 1 + max over all objects of the max abs row sum
    bound = max(sum(abs(x) for x in r) for _, M in O1 + O5 for r in M)
    lam = bound + 1
    def shifted(M): return madd(M, msc(lam, eye(3)))
    Ds1 = [equiv_data(shifted(M), [0, 1], [2]) for _, M in O1]; Ds5 = [equiv_data(shifted(M), [0, 1], [2]) for _, M in O5]
    re_pairs = sum(1 for a in Ds1 for b in Ds5 if real_equiv(a, b))
    # null: random 3x3 symmetric integer matrices (matched size and partition), same global shift
    nn = 0; npass = 0
    nullm = []
    for _ in range(20):
        X = zeros(3, 3)
        for i in range(3):
            for j in range(i, 3):
                v = F(rng.randint(-(int(bound) // 3), int(bound) // 3)); X[i][j] = v; X[j][i] = v
        nullm.append(X)
    Dn = [equiv_data(shifted(X), [0, 1], [2]) for X in nullm]
    for i in range(0, len(Dn) - 1, 2):
        nn += 1; npass += real_equiv(Dn[i], Dn[i + 1])
    T["T4_global_shift"] = {"lambda": lam, "real_equivalent_pairs_after_shift": re_pairs, "of": len(Ds1) * len(Ds5), "null_pairs": nn, "null_real_equivalent": npass,
                           "all_positive_definite": all(d["inA"] == (2, 0, 0) and d["inS"] == (1, 0, 0) for d in Ds1 + Ds5 + Dn)}
    check("equiv.T4_global_shift_makes_everything_equal", re_pairs == len(Ds1) * len(Ds5) and npass == nn, "after M+%s*I: %d/%d real-equivalent, null %d/%d" % (lam, re_pairs, len(Ds1) * len(Ds5), npass, nn))
    # scope of lambda: the row 6 matrices have much larger row sums
    L6 = [parse_mat(p["full"]) for p in lq]
    maxrs6 = max(sum(abs(x) for x in r_) for M_ in L6 for r_ in M_)
    pd6 = sum(1 for M_ in L6 if inertia_sym(madd(sym_part(M_), msc(lam, eye(16)))) == (16, 0, 0))
    T["lambda_scope"] = {"lambda": lam, "row1_row5_max_row_sum": bound, "row6_max_row_sum": maxrs6, "row6_points": len(L6), "row6_points_with_sym_M_plus_lambda_I_positive_definite": pd6}
    check("equiv.lambda_scope_row6", pd6 < len(L6) and maxrs6 > lam, "lambda=%s is a bound for rows 1 and 5 only: row 6 max row sum %s, sym(M)+lambda I positive definite at %d of %d points" % (lam, maxrs6, pd6, len(L6)))
    # per-determinant square-class failures over all 168 pairs (separately from the cascade)
    badA = sum(1 for _, a in D1 for _, b in D5 if not same_sq(a["detA"], b["detA"]))
    badS = sum(1 for _, a in D1 for _, b in D5 if not same_sq(a["detS"], b["detS"]))
    T["square_class_failures_all_pairs"] = {"detA": badA, "detS": badS, "pairs": len(D1) * len(D5)}
    # --- T6: compression to the pivot block only: real equivalence of the two 2x2 pivot blocks; matched null = random positive-definite 2x2 pairs
    A1 = [inertia_sym(sub(M, [0, 1], [0, 1])) for _, M in O1]; A5 = [inertia_sym(sub(M, [0, 1], [0, 1])) for _, M in O5]
    pv_pass = sum(1 for a in A1 for b in A5 if a == b)
    nullA = 0; nullT = 60
    for _ in range(nullT):
        def rpd():
            while True:
                a, b, c = F(rng.randint(1, 9)), F(rng.randint(-3, 3)), F(rng.randint(1, 9))
                if a * c - b * b > 0: return [[a, b], [b, c]]
        nullA += (inertia_sym(rpd()) == inertia_sym(rpd()))
    T["T6_pivot_only"] = {"pairs_real_equivalent": pv_pass, "of": len(A1) * len(A5), "null_pd_pairs": nullT, "null_equivalent": nullA}
    # --- T7: domain split Omega_valid = {pairs whose (In A, In S) agree}: defined by the outcome, count
    T["T7_domain_split"] = {"omega_valid_pairs": real_eq, "of": len(D1) * len(D5)}
    # --- per-pair unit rescale (the package's near-match): needs one free scalar per pair
    unit = 0
    for _, a in D1:
        for _, b in D5:
            if a["inA"] == b["inA"] and a["inS"] == b["inS"]:
                # c>0 with c^2 detA_a ~ detA_b  (A is 2x2) and c detS_a ~ detS_b: both square-class conditions
                c = b["detS"] / a["detS"]
                if c > 0 and is_rat_square(c ** 2 * a["detA"] / b["detA"]): unit += 1
    T["per_pair_unit_rescale_matches"] = unit
    # --- row 6 versus rows 1 and 5: dimension and symmetry type
    L0 = parse_mat(lq[0]["full"])
    T["row6_vs_others"] = {"row6_size": len(L0), "rows_1_5_size": 3, "row6_symmetric": is_sym(L0), "rank_antisym_part": rank(msub(L0, tr(L0)))}
    check("equiv.row6_dimension_and_type", len(L0) != 3 and not is_sym(L0), "16x16 non-symmetric vs 3x3 symmetric")
    REPORT["numbers"]["equiv"] = T
    return T

# ================= LATTICE PAIR (G5-05 second half, G5-06, and the team's M1), built from lattice/SPEC.md sections 1-2 =================
def lattice_build(L, bridge_m=None):
    """L: n x n rows r_i. bridge_m: optional list of integer row vectors m_i (default e_i). Returns dict of exact objects."""
    n = len(L); nv = 2 * n
    def xv(v):
        x = [F(0)] * n; x[v // 2] = F(1) if v % 2 == 0 else F(-1); return x
    bars = []   # (u, v, m, ell)
    for i in range(n):
        for j in range(i + 1, n):
            for si in (0, 1):
                for sj in (0, 1):
                    v = 2 * i + si; u = 2 * j + sj
                    bars.append((u, v, [0] * n, [a - b for a, b in zip(xv(v), xv(u))]))
    for i in range(n):
        m = list(bridge_m[i]) if bridge_m is not None else [1 if k == i else 0 for k in range(n)]
        u = 2 * i; v = 2 * i + 1
        ell = [a - b + sum(m[k] * L[k][c] for k in range(n)) for c, (a, b) in enumerate(zip(xv(v), xv(u)))]
        bars.append((u, v, m, ell))
    nb = len(bars); ns = n * (n + 1) // 2
    d0 = zeros(nb, nv * n); ae = zeros(nb, ns); Z = zeros(nb, n * n)
    pairs = [(k, l) for k in range(n) for l in range(k + 1, n)]
    for b, (u, v, m, ell) in enumerate(bars):
        for k in range(n):
            d0[b][v * n + k] += ell[k]; d0[b][u * n + k] -= ell[k]
            ae[b][k] = ell[k] * ell[k]
            for l in range(n): Z[b][k * n + l] = F(m[k]) * ell[l]
        for c, (k, l) in enumerate(pairs): ae[b][n + c] = 2 * ell[k] * ell[l]
    W = F(1, 2)
    def schur_pinv(Bl, Kl):   # S = K + B^T X with Delta X = -B, free variables 0
        Delta = msc(W, mm(tr(d0), d0)); Bt = msc(W, mm(tr(d0), Bl))
        X = solve_consistent(Delta, msc(F(-1), Bt))
        if X is None: return None
        return madd(msc(W, mm(tr(Bl), Bl)), mm(tr(Bt), X))
    S_el = schur_pinv(ae, None); S_lat = schur_pinv(Z, None)
    # Phi
    X = zeros(nv * n, ns)
    for v in range(nv):
        x = xv(v)
        for k in range(n): X[v * n + k][k] = x[k]
        for c, (k, l) in enumerate(pairs):
            X[v * n + l][n + c] += x[k]; X[v * n + k][n + c] += x[l]
    RL = zeros(n * n, ns)
    for j in range(n):
        for k in range(n): RL[k * n + j][j] = F(L[k][j])
    for c, (j, l) in enumerate(pairs):
        for k in range(n):
            RL[k * n + l][n + c] += F(L[k][j]); RL[k * n + j][n + c] += F(L[k][l])
    return {"n": n, "bars": bars, "d0": d0, "ae": ae, "Z": Z, "S_el": S_el, "S_lat": S_lat, "Xphi": X, "RL": RL, "pairs": pairs}

def hcat(A, B): return [a + b for a, b in zip(A, B)]
def vcat(A, B): return [list(r) for r in A] + [list(r) for r in B]

def phi_matrix(o):
    nvn = len(o["Xphi"]); n2 = len(o["RL"]); ns = len(o["Xphi"][0])
    top = hcat(eye(nvn), o["Xphi"]); bot = hcat(zeros(n2, nvn), o["RL"])
    return vcat(top, bot)

def lattice_checks(L, tag):
    o = lattice_build([[F(x) for x in r] for r in L])
    n = o["n"]
    d0, ae, Z = o["d0"], o["ae"], o["Z"]
    Rel = hcat(d0, ae); Rlat = hcat(d0, Z); Phi = phi_matrix(o)
    ok_id = (mm(Rlat, Phi) == Rel)                                  # R_el = R_lat Phi
    W = F(1, 2)
    Hel = msc(W, mm(tr(Rel), Rel)); Hlat = msc(W, mm(tr(Rlat), Rlat))
    ok_cong = (mm(mm(tr(Phi), Hlat), Phi) == Hel)                      # H_el = Phi^T H_lat Phi
    ok_M1 = (o["S_el"] == mm(mm(tr(o["RL"]), o["S_lat"]), o["RL"]))     # S_el = R_L^T S_lat R_L
    return o, ok_id, ok_cong, ok_M1

def ZB_dim(L):
    n = len(L); rows = []
    for i in range(n):
        for j in range(i + 1, n):
            r = [F(0)] * n; r[i] = F(L[i][j]); r[j] = -F(L[j][i]); rows.append(r)
    return len(nullspace(rows)) if rows else n, nullspace(rows)

def sigma_rank(L, basis):
    n = len(L); cols = []
    B = [[F(L[i][j]) - (2 if i == j else 0) for j in range(n)] for i in range(n)]
    for z in basis:
        dz = [[z[i] * B[i][j] for j in range(n)] for i in range(n)]
        M = mm(tr([[F(x) for x in r] for r in L]), dz)
        sg = msc(F(1, 2), madd(M, tr(M)))
        col = [sg[i][i] for i in range(n)] + [2 * sg[i][j] for i in range(n) for j in range(i + 1, n)]
        cols.append(col)
    return rank(tr(cols)) if cols else 0

def lattice_section():
    T = {}
    rng = Rng(31415926)
    def unimod(n, steps=20):
        U = eye(n)
        for _ in range(steps):
            i = rng.randint(0, n - 1); j = rng.randint(0, n - 1)
            if i == j: continue
            E = eye(n); E[i][j] = F(rng.choice([1, -1]) if hasattr(rng, "choice") else (1 if rng.randint(0, 1) else -1))
            U = mm(E, U)
        return U
    # --- M1 and the identities on the n=3 and n=4 checks
    base = {}
    for n in (3, 4):
        L = [[2 if i == j else 0 for j in range(n)] for i in range(n)]
        # a symmetric non-trivial lattice: L = 2I + C with C a symmetric cycle-ish integer matrix
        for i in range(n):
            L[i][(i + 1) % n] += -1; L[(i + 1) % n][i] += -1
        o, ok_id, ok_cong, ok_M1 = lattice_checks(L, "sym%d" % n)
        T["M1_n%d" % n] = {"R_el_eq_R_lat_Phi": ok_id, "H_el_eq_PhiT_H_lat_Phi": ok_cong, "S_el_eq_RLT_S_lat_RL": ok_M1,
                           "rank_S_el": rank(o["S_el"]), "inertia_S_el": inertia_sym(o["S_el"]), "ZB_dim": ZB_dim(L)[0]}
        check("lattice.M1.n%d" % n, ok_id and ok_cong and ok_M1, str(T["M1_n%d" % n]))
        base[n] = (L, o)
    # --- G5-06: forward directions and converse witness on a panel
    panel = []
    for n in (3, 4):
        d2 = [[F(2) if i == j else F(0) for j in range(n)] for i in range(n)]
        dg = [[(3 if (i == j and i == 0) else (2 if i == j else 0)) for j in range(n)] for i in range(n)]
        panel.append(("diag(3,2..)", n, dg))
        panel.append(("2I", n, [[2 if i == j else 0 for j in range(n)] for i in range(n)]))
        Lb = [[2 if i == j else 0 for j in range(n)] for i in range(n)]; Lb[0][1] = Lb[1][0] = 1
        panel.append(("2I+sym2x2", n, Lb))
        for t in range(6):
            Ls = [[F(0)] * n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    v = F(rng.randint(-2, 2)); Ls[i][j] = v; Ls[j][i] = v
                Ls[i][i] += 2
            panel.append(("rand_sym%d" % t, n, Ls))
        for t in range(4):
            Ln = [[F(rng.randint(-2, 2)) for _ in range(n)] for _ in range(n)]
            for i in range(n): Ln[i][i] += 2
            panel.append(("rand_nonsym%d" % t, n, Ln))
    rows = []
    fwd_zero_ok = fwd_one_ok = C5_ok = lit_conv_fail = lit_conv_total = 0
    wit = None
    for name, n, L in panel:
        o = lattice_build([[F(x) for x in r] for r in L])
        r = rank(o["S_el"]); dz, basis = ZB_dim(L); sr = sigma_rank(L, basis)
        rows.append({"name": name, "n": n, "rank_S": r, "dim_ZB": dz, "rank_sigma_on_ZB": sr})
        if dz == 0: fwd_zero_ok += (r == 0)
        if dz == 1 and sr == 1: fwd_one_ok += (r == 1)
        C5_ok += (r == sr)
        lit_conv_total += 1
        if r == 1 and dz != 1:
            lit_conv_fail += 1
            if wit is None: wit = (name, n, L)
    T["converse"] = {"panel": len(panel), "rank_S_equals_rank_sigma_on_ZB": C5_ok, "dimZB0_implies_S0_failures": sum(1 for x in rows if x["dim_ZB"] == 0 and x["rank_S"] != 0),
                     "converse_counterexamples_rank1_but_dimZB_ne_1": lit_conv_fail, "first_counterexample": (wit[0], wit[1]) if wit else None, "rows": rows}
    check("lattice.C5_rank_formula_panel", C5_ok == len(panel), "rank S_el == rank of z -> sigma_c(z) on Z_B for %d/%d lattices (n=3,4)" % (C5_ok, len(panel)))
    check("lattice.forward_dimZB0", T["converse"]["dimZB0_implies_S0_failures"] == 0, "dim Z_B = 0 implies S_el = 0 on the panel")
    check("lattice.converse_counterexample_exists", lit_conv_fail >= 1, "rank-1 S with dim Z_B != 1: %d lattices, first %s" % (lit_conv_fail, T["converse"]["first_counterexample"]))
    # smallest witness diag(3,2,2)
    Ld = [[3, 0, 0], [0, 2, 0], [0, 0, 2]]
    od = lattice_build([[F(x) for x in r] for r in Ld]); dzd, bd = ZB_dim(Ld)
    T["diag322"] = {"rank_S_el": rank(od["S_el"]), "dim_ZB": dzd, "inertia": inertia_sym(od["S_el"]), "rank_sigma": sigma_rank(Ld, bd)}
    check("lattice.diag322_witness", T["diag322"]["rank_S_el"] == 1 and dzd == 3, str(T["diag322"]))
    # --- G5-06 basis change: naive vs carried, on symmetric (collapsing) lattices
    nn = nc = ns_ = carried_S_same = carried_cov = 0; collapsed_total = 0
    for n in (3, 4):
        L0, o0 = base[n]
        r0 = rank(o0["S_el"])
        for t in range(8):
            U = unimod(n)
            Lp = mm(U, [[F(x) for x in r] for r in L0])
            on = lattice_build(Lp)                                  # naive: bridges m = e_i, bars change
            nn += 1; ns_ += (rank(on["S_el"]) == r0)
            Uinv = inv(U)
            bm = [[sum(F(1 if k == i else 0) * Uinv[k][c] for k in range(n)) for c in range(n)] for i in range(n)]  # m'_i = e_i U^-1
            if not all(x.denominator == 1 for r in bm for x in r): continue
            oc = lattice_build(Lp, bridge_m=[[int(x) for x in r] for r in bm])    # carried: same bars
            nc += 1
            carried_S_same += (oc["S_el"] == o0["S_el"])
            # covariance S_lat' = (U^-1 kron I)^T S_lat (U^-1 kron I): dL' = U dL  =>  dL = U^-1 dL'
            Uk = zeros(n * n, n * n)
            for a in range(n):
                for b in range(n):
                    for c in range(n): Uk[a * n + c][b * n + c] = Uinv[a][b]
            carried_cov += (oc["S_lat"] == mm(mm(tr(Uk), o0["S_lat"]), Uk))
    T["basis_change"] = {"naive_changes": nn, "naive_keeps_rank": ns_, "carried_changes": nc, "carried_S_el_unchanged": carried_S_same, "carried_S_lat_covariant": carried_cov}
    check("lattice.carried_S_el_unchanged", nc > 0 and carried_S_same == nc and carried_cov == nc, str(T["basis_change"]))
    # --- G5-05 second half: commuting defect test, n = 3
    L3, o3 = base[3]
    Phi = phi_matrix(o3); Rel = hcat(o3["d0"], o3["ae"]); Rlat = hcat(o3["d0"], o3["Z"])
    Hlat = msc(F(1, 2), mm(tr(Rlat), Rlat))
    nvn = len(o3["Xphi"]); ns = len(o3["Xphi"][0]); n2 = len(o3["RL"])
    def schur_gen(H, k):   # Schur complement of leading k x k block with pseudo-inverse convention (free vars 0)
        A = [r[:k] for r in H[:k]]; Bb = [r[k:] for r in H[:k]]; Dd = [r[k:] for r in H[k:]]
        X = solve_consistent(A, msc(F(-1), Bb))
        return None if X is None else madd(Dd, mm(tr(Bb), X))
    S_lat = schur_gen(Hlat, nvn)
    check("lattice.S_lat_matches_builder", S_lat == o3["S_lat"], "pseudo-inverse Schur conventions agree")
    def defect_gen(X_, R_):
        Ph = vcat(hcat(eye(nvn), X_), hcat(zeros(n2, nvn), R_))
        lhs = schur_gen(mm(mm(tr(Ph), Hlat), Ph), nvn)
        return None if lhs is None else msub(lhs, mm(mm(tr(R_), S_lat), R_))
    zero_up = ident_up = 0; dense_zero = 0; ntest = 12
    rng2 = Rng(2718281)
    for _ in range(ntest):
        X_ = [[F(rng2.randint(-2, 2)) for _ in range(ns)] for _ in range(nvn)]
        R_ = [[F(rng2.randint(-2, 2)) for _ in range(ns)] for _ in range(n2)]
        d_ = defect_gen(X_, R_)
        zero_up += (d_ is not None and is_zero(d_))
        ident_up += (mm(Rlat, vcat(hcat(eye(nvn), X_), hcat(zeros(n2, nvn), R_))) == Rel)
        # dense: also random lower-left block
        Ph = vcat(hcat([[F(rng2.randint(-1, 1)) for _ in range(nvn)] for _ in range(nvn)], X_), hcat([[F(rng2.randint(-1, 1)) for _ in range(nvn)] for _ in range(n2)], R_))
        lhs = schur_gen(mm(mm(tr(Ph), Hlat), Ph), nvn)
        if lhs is not None: dense_zero += is_zero(msub(lhs, mm(mm(tr(R_), S_lat), R_)))
    T["commuting_test"] = {"random_block_upper_maps": ntest, "zero_defect": zero_up, "satisfy_R_el_eq_R_lat_Phi": ident_up, "dense_maps_zero_defect": dense_zero,
                           "true_Phi_defect_zero": is_zero(defect_gen(o3["Xphi"], o3["RL"])),
                           "free_entries_block_upper_class": nvn * ns + n2 * ns, "independent_defect_constraints": ns * (ns + 1) // 2}
    check("lattice.commuting_test_nondiscriminating", zero_up == ntest and T["commuting_test"]["true_Phi_defect_zero"] and dense_zero == 0 and ident_up == 0, str(T["commuting_test"]))
    REPORT["numbers"]["lattice"] = T
    return T

# ================= RULING G5-01 sub-claim: inertia additivity with the pseudo-inverse Schur complement =================
def mp_pinv(A):
    """exact Moore-Penrose inverse via full-rank factorisation A = Fm Gm"""
    R, piv = rref(A)
    r = len(piv)
    if r == 0: return zeros(len(A[0]), len(A))
    Fm = [[A[i][c] for c in piv] for i in range(len(A))]
    Gm = [R[i] for i in range(r)]
    GGt = mm(Gm, tr(Gm)); FtF = mm(tr(Fm), Fm)
    return mm(mm(mm(tr(Gm), inv(GGt)), inv(FtF)), tr(Fm))

def g501_range_condition():
    rng = Rng(1618033)
    tot = rng_hold = add_given_range = add_given_norange = norange = 0
    for _ in range(300):
        k = rng.randint(2, 3); m = rng.randint(1, 3); n = k + m
        # singular symmetric pivot block A of rank k-1 (or k-2), random symmetric rest, random coupling
        Vv = [[F(rng.randint(-2, 2)) for _ in range(rng.randint(1, k - 1))] for _ in range(k)]
        A = mm(Vv, tr(Vv))
        M = zeros(n, n)
        for i in range(k):
            for j in range(k): M[i][j] = A[i][j]
        for i in range(k, n):
            for j in range(i, n):
                v = F(rng.randint(-3, 3)); M[i][j] = v; M[j][i] = v
        if rng.randint(0, 1) == 0:
            Y = [[F(rng.randint(-2, 2)) for _ in range(m)] for _ in range(k)]
            Bc = mm(A, Y)                      # coupling inside range(A): range condition holds by construction
        else:
            Bc = [[F(rng.randint(-2, 2)) for _ in range(m)] for _ in range(k)]
        for i in range(k):
            for j in range(m):
                M[i][k + j] = Bc[i][j]; M[k + j][i] = Bc[i][j]
        piv = list(range(k)); rest = list(range(k, n))
        Ap = mp_pinv(A); B = sub(M, piv, rest); C = sub(M, rest, piv); D = sub(M, rest, rest)
        S = msub(D, mm(mm(C, Ap), B))
        rc = (mm(mm(A, Ap), B) == B)
        add = (tuple(inertia_sym(M)) == tuple(a + b for a, b in zip(inertia_sym(A), inertia_sym(S))))
        tot += 1
        if rc:
            rng_hold += 1; add_given_range += add
        else:
            norange += 1; add_given_norange += add
    out = {"samples": tot, "range_condition_holds": rng_hold, "additive_given_range_condition": add_given_range, "range_condition_fails": norange, "additive_given_range_fails": add_given_norange}
    check("g501.range_condition_is_sufficient", add_given_range == rng_hold, str(out))
    REPORT["numbers"]["g501"] = out
    return out

def g501_witnesses():
    """the three small symmetric witnesses for 'sufficient, not necessary' (clean-room second checker found the same three)"""
    cases = {
        "range_holds_additive": ([[-1, -1], [-1, -1]], [[-1], [-1]], [[-1]]),
        "range_fails_not_additive": ([[0]], [[1]], [[0]]),
        "range_fails_but_additive": ([[0]], [[1, 0]], [[0, 1], [1, 0]]),
    }
    out = {}
    for name, (A, B, D) in cases.items():
        A = mat(A); B = mat(B); D = mat(D); k = len(A); m = len(D)
        M = [A[i] + B[i] for i in range(k)] + [list(tr(B)[j]) + D[j] for j in range(m)]
        Ap = mp_pinv(A); S = msub(D, mm(mm(tr(B), Ap), B))
        rc = (mm(mm(A, Ap), B) == B)
        add = tuple(inertia_sym(M)) == tuple(a + b for a, b in zip(inertia_sym(A), inertia_sym(S)))
        out[name] = {"range_condition": rc, "additive": add, "In_M": inertia_sym(M), "In_A": inertia_sym(A), "In_S": inertia_sym(S)}
    ok = (out["range_holds_additive"]["range_condition"] and out["range_holds_additive"]["additive"]
          and not out["range_fails_not_additive"]["range_condition"] and not out["range_fails_not_additive"]["additive"]
          and not out["range_fails_but_additive"]["range_condition"] and out["range_fails_but_additive"]["additive"])
    check("g501.three_witnesses", ok, str(out))
    REPORT["numbers"]["g501_witnesses"] = out
    return out

# ================= CLAIM 18: block-diagonal symmetrisation of K(q) for the row 4 object (my own code; decided at fixed rational q) =================
def sparse_null(rows, ncols):
    """rows: list of dict col->Fraction. Returns a basis of the null space as list of dict col->Fraction (exact)."""
    piv = {}
    for r in rows:
        r = {c: v for c, v in r.items() if v != 0}
        while r:
            c = min(r)
            if c in piv:
                f = r[c]
                for cc, vv in piv[c].items():
                    nv = r.get(cc, F(0)) - f * vv
                    if nv == 0: r.pop(cc, None)
                    else: r[cc] = nv
            else:
                f = r[c]; piv[c] = {cc: vv / f for cc, vv in r.items()}; break
    for c in sorted(piv, reverse=True):
        row = piv[c]
        for j in sorted(k for k in row if k != c and k in piv):
            f = row.get(j)
            if not f: continue
            for cc, vv in piv[j].items():
                nv = row.get(cc, F(0)) - f * vv
                if nv == 0: row.pop(cc, None)
                else: row[cc] = nv
    free = [c for c in range(ncols) if c not in piv]
    out = []
    for fcol in free:
        v = {fcol: F(1)}
        for c, row in piv.items():
            if fcol in row: v[c] = -row[fcol]
        out.append(v)
    return out

def claim18(PK):
    d = load_json(os.path.join(PK, "tropical", "objects", "cole_hopf.json"))
    n = d["K_32"]["n"]
    polys = {(e["i"], e["j"]): [F(x) for x in e["poly"]] for e in d["K_32"]["K"]}
    idx = {}
    for i in range(n):
        for j in range(i, n): idx[(i, j)] = len(idx)
    inv_idx = {v: k for k, v in idx.items()}
    def uid(i, j): return idx[(min(i, j), max(i, j))]
    oneway = [(10, 0), (12, 2), (14, 4), (18, 8), (20, 10), (22, 12), (26, 16), (28, 18), (30, 20)]
    T = {}
    for (a, b) in ((1, 10), (1, 100), (1, 1000)):
        q = F(a, b)
        K = zeros(n, n)
        for (i, j), p in polys.items(): K[i][j] = sum((c * q ** k for k, c in enumerate(p)), F(0))
        rows = []
        for i in range(n):
            for j in range(i + 1, n):
                row = {}
                for k in range(n):
                    if K[i][k] != 0: row[uid(k, j)] = row.get(uid(k, j), F(0)) + K[i][k]
                    if K[j][k] != 0: row[uid(i, k)] = row.get(uid(i, k), F(0)) - K[j][k]
                rows.append(row)
        basis = sparse_null(rows, len(idx))
        Wm = []
        for bv in basis:
            X = zeros(n, n)
            for c, v in bv.items():
                i, j = inv_idx[c]; X[i][j] = v; X[j][i] = v
            Wm.append(X)
        okW = all((lambda KX: KX == tr(KX))(mm(K, X)) for X in Wm)
        res = {"dim_W": len(Wm), "W_basis_verified": okW}
        check("claim18.W_basis.q=%s" % q, okW and len(Wm) == 32, "dim %d" % len(Wm))
        # fully diagonal G
        drows = [[X[i][j] for X in Wm] for i in range(n) for j in range(i + 1, n)]
        res["diagonal_G_solution_dim"] = len(nullspace(drows, len(Wm)))
        nul0 = 0; one = []; other = []
        Pm = (1 << 61) - 1
        def modp(x):
            x = F(x)
            return (x.numerator % Pm) * pow(x.denominator % Pm, -1, Pm) % Pm
        def rank_modp(rows_):
            M_ = [list(r_) for r_ in rows_]; rk = 0
            for c_ in range(len(M_[0]) if M_ else 0):
                p_ = next((i_ for i_ in range(rk, len(M_)) if M_[i_][c_]), None)
                if p_ is None: continue
                M_[rk], M_[p_] = M_[p_], M_[rk]
                iv = pow(M_[rk][c_], -1, Pm)
                for i_ in range(rk + 1, len(M_)):
                    if M_[i_][c_]:
                        f_ = M_[i_][c_] * iv % Pm
                        M_[i_] = [(a_ - f_ * b_) % Pm for a_, b_ in zip(M_[i_], M_[rk])]
                rk += 1
            return rk
        Wp = [[[modp(x) for x in r_] for r_ in X] for X in Wm]
        for B in [[b] for b in range(n)] + [[b, c] for b in range(n) for c in range(b + 1, n)]:
            A = [i for i in range(n) if i not in B]
            # screen: true nullity <= nullity modulo a prime, so nullity 0 modulo p proves the exact solution space is {0}
            if len(Wm) - rank_modp([[X[x][y] for X in Wp] for x in A for y in B]) == 0:
                nul0 += 1; continue
            rr = [[X[x][y] for X in Wm] for x in A for y in B]
            co = nullspace(rr, len(Wm))
            if not co: nul0 += 1; continue
            if len(co) > 1: other.append(B); continue
            G = zeros(n, n)
            for k, ck in enumerate(co[0]):
                if ck != 0:
                    for i in range(n):
                        for j in range(n):
                            if Wm[k][i][j] != 0: G[i][j] += ck * Wm[k][i][j]
            ine = inertia_sym(G)
            pd = ine in ((n, 0, 0), (0, n, 0))
            blockdiag = all(G[x][y] == 0 for x in A for y in B) and (lambda KG: KG == tr(KG))(mm(K, G))
            one.append((B, ine, pd, blockdiag))
        pd_sing = [x[0][0] for x in one if len(x[0]) == 1 and x[2] and x[3]]
        pd_pairs = [x[0] for x in one if len(x[0]) == 2 and x[2] and x[3]]
        antip = [x for x in one if len(x[0]) == 2]
        res.update({"partitions_with_solution_space_zero": nul0, "one_dimensional": len(one), "more_than_one_dim": len(other),
                    "singletons_with_PD_solution": pd_sing, "pairs_with_PD_solution": pd_pairs,
                    "one_dim_pairs": len(antip), "one_dim_pairs_all_indefinite": all(not x[2] for x in antip),
                    "all_one_dim_solutions_verified_block_diagonal_and_KG_symmetric": all(x[3] for x in one)})
        # one-way pairs: necessary condition from the BB block alone
        ow_ok = 0
        for (i, j) in oneway:
            Bl = [i, j]; KB = sub(K, Bl, Bl)
            # unknown symmetric G_B = [[x,y],[y,z]] ; (KB G_B) symmetric
            Gu = lambda x, y, z: mat([[x, y], [y, z]])
            eqs = []
            cols = []
            for t in range(3):
                e = [F(0)] * 3; e[t] = F(1); Mx = mm(KB, Gu(*e)); cols.append(Mx[0][1] - Mx[1][0])
            sol = nullspace([cols], 3)
            # every solution must have a zero diagonal entry (x=0 or z=0) for all combinations => all basis vectors vanish in the same diagonal slot
            ow_ok += (all(v[0] == 0 for v in sol) or all(v[2] == 0 for v in sol))
        res["one_way_pairs_with_no_PD_possible"] = ow_ok
        check("claim18.one_way_pairs.q=%s" % q, ow_ok == 9 and not pd_pairs or ow_ok == 9, "%d of 9" % ow_ok)
        check("claim18.verified_block_diagonal.q=%s" % q, res["all_one_dim_solutions_verified_block_diagonal_and_KG_symmetric"], "")
        T["q=%s" % q] = res
    REPORT["numbers"]["claim18"] = T
    return T

# ================= M2, guards (my own reading of the specification lines 46-53), specs, controls =================
FAMS = ["T1_GAUGE_SIMILARITY", "T2_AFFINE_BREGMAN", "T3_METRIC_CHART", "T4_SPECTRAL_PSD_SHIFT", "T5_SEMIRING_TROPICAL", "T6_SUBSPACE_PROJECTION", "T7_ORDER_DOMAIN_RESIDUAL"]
CAP = F(1, 10)

def my_guards(s):
    """independent reading of 'Four Mandatory Law-3 Anti-Epicycle / Non-Degeneracy Guards (G1..G4)'. Returns the list of refusal reasons."""
    r = []
    v = s["proposed_verdict"]
    null_rate = F(s["null_false_pass_count"], s["null_total_count"])
    if s["relabelled_as_literal"]: r.append("G3_SILENT")
    if not s["fixed_globally_before_holdout"]: r.append("G2_POST_HOC")
    if null_rate > CAP: r.append("G1_VACUOUS")
    if F(s["max_null_false_pass_rate"]) > 0 and s["null_total_count"] * F(s["max_null_false_pass_rate"]) < 1: r.append("G1_NULL_RESOLUTION")
    if v == "FALSIFIED_RAW":
        r.append("G4_RAW")
    elif v == "INVARIANT_FALSIFIED":
        if len(set(s["families_searched"])) < 7: r.append("G4_SEARCH")
        if s["applied_family"] is not None: r.append("G4_RESCUE_APPLIED")
        if s["obstruction_invariant"] is None or not s["obstruction_survives_all_searched"]: r.append("G4_OBSTRUCTION")
        if s["target_pass_count"] >= s["target_total_count"]: r.append("G4_NO_FAILING_TARGET")
        if F(s["residual_gap"]) == 0: r.append("G4_ZERO_GAP")
        if s["transform_rank"] != 0 or s["transform_dof"] != 0 or s["preserved_invariant_core"] is not None or s["modified_hypotheses"] is not None: r.append("G4_RESCUE_FIELDS")
    else:
        if s["applied_family"] is None: r.append("G0_NO_FAMILY")
        if s["transform_rank"] < 1: r.append("G1_ZERO_RANK")
        if s["target_pass_count"] < s["target_total_count"]: r.append("G1_TARGET_FAILS")
        if s["transform_dof"] >= s["held_out_constraints"]: r.append("G2_DOF")
        if s["preserved_invariant_core"] is None or s["modified_hypotheses"] is None: r.append("G3_LEDGER")
        if v == "TRANSFORMED_EXACT" and (F(s["residual_gap"]) != 0 or F(s["max_residual_gap"]) != 0): r.append("G3_GAP")
        if v == "BOUNDED_TRANSFORM_CORE" and not (0 < F(s["residual_gap"]) <= F(s["max_residual_gap"])): r.append("G3_GAP")
    return r

def mkspec(claim_id, verdict, literal_witness, searched, applied, dof, held, tp, tt, nfp, nt, rank_, core, mod, gap, maxgap, relab=False, obs=None, surv=False, fixed=True):
    return {"claim_id": claim_id, "proposed_verdict": verdict, "literal_failed": True, "literal_failure_witness": literal_witness,
            "families_searched": list(searched), "applied_family": applied, "transform_dof": dof, "held_out_constraints": held,
            "fixed_globally_before_holdout": fixed, "target_pass_count": tp, "target_total_count": tt, "null_false_pass_count": nfp,
            "null_total_count": nt, "max_null_false_pass_rate": "1/10", "transform_rank": rank_, "preserved_invariant_core": core,
            "modified_hypotheses": mod, "residual_gap": str(gap), "max_residual_gap": str(maxgap), "relabelled_as_literal": relab,
            "obstruction_invariant": obs, "obstruction_survives_all_searched": surv}

def m2_check():
    p = [F(1, 2), F(1, 4), F(1, 4)]
    cols = [[F(3, 4), F(-3, 8), F(-3, 8)], [F(0), F(7, 4), F(-7, 4)], [F(0), F(0), F(0)]]    # tangent vectors w1, w2, w3 (zero-sum)
    Wm = tr(cols)                                                                            # rows = vectors? columns of Wm are the w's below
    Wm = [[cols[j][i] for j in range(3)] for i in range(3)]                                  # W[i][j] = w_j[i]
    G = mm(mm(tr(Wm), [[(1 / p[i]) if i == k else F(0) for k in range(3)] for i in range(3)]), Wm)
    exp = [[F(9, 4), 0, 0], [0, F(49, 2), 0], [0, 0, 0]]
    ok = G == mat(exp) and all(sum(cols[j]) == 0 for j in range(3))
    check("M2.fisher_pullback_exact", ok, "W^T diag(1/p) W = diag(9/4,49/2,0) at p=(1/2,1/4,1/4)")
    # null: random zero-sum tangent triples with entries on a small grid; how often is the pullback diagonal?
    rng = Rng(8675309); diag_n = 0; tot = 0
    for _ in range(200):
        cs = []
        for _ in range(3):
            a, b = F(rng.randint(-4, 4), 4), F(rng.randint(-4, 4), 4)
            cs.append([a, b, -a - b])
        Wr = [[cs[j][i] for j in range(3)] for i in range(3)]
        Gr = mm(mm(tr(Wr), [[(1 / p[i]) if i == k else F(0) for k in range(3)] for i in range(3)]), Wr)
        tot += 1; diag_n += all(Gr[i][j] == 0 for i in range(3) for j in range(3) if i != j)
    # free parameters: three zero-sum vectors in R^3 have 6 degrees of freedom; the property fixes 3 off-diagonal zeros
    REPORT["numbers"]["M2"] = {"exact": ok, "null_random_tangent_triples": tot, "null_pullback_diagonal": diag_n, "free_parameters": 6, "property_constraints": 3}
    return ok

def heavy_lattice_n8():
    out = {}
    H = [[(-1) ** bin(i & j).count("1") for j in range(8)] for i in range(8)]
    Le8 = [[(F(2) if i == j else F(0)) + F(H[i][j], 2) for j in range(8)] for i in range(8)]
    C = [[0] * 8 for _ in range(8)]
    C[0][1] = C[0][7] = -1; C[1][0] = 1; C[1][2] = -1
    for k in range(2, 7): C[k][k - 1] = C[k][k + 1] = -1
    C[7][0] = 1; C[7][6] = -1
    Ld8 = [[(F(2) if i == j else F(0)) + F(C[i][j]) for j in range(8)] for i in range(8)]
    for name, L, trace in (("E8_s1", Le8, F(114, 23)), ("D8_s1", Ld8, F(23, 4))):
        o, ok_id, ok_cong, ok_M1 = lattice_checks(L, name)
        t = sum(o["S_el"][i][i] for i in range(len(o["S_el"])))
        out[name] = {"R_el_eq_R_lat_Phi": ok_id, "H_el_eq_PhiT_H_lat_Phi": ok_cong, "S_el_eq_RLT_S_lat_RL": ok_M1, "rank_S_el": rank(o["S_el"]), "inertia_S_el": inertia_sym(o["S_el"]),
                     "trace_S_el": t, "SPEC_trace": trace, "dim_ZB": ZB_dim(L)[0]}
        check("lattice.M1.n8." + name, ok_id and ok_cong and ok_M1 and t == trace and rank(o["S_el"]) == 1, str(out[name]))
    REPORT["numbers"]["lattice_n8"] = out
    return out

def controls_and_specs():
    N = REPORT["numbers"]
    r6, r4, eq, lat = N["row6"], N["row4"], N["equiv"], N["lattice"]
    # ---------------- null counts for the obstruction (false positives of the obstruction invariants on Hermitian nulls)
    rng = Rng(60221023); fires = 0; nul = 0
    for _ in range(60):
        n = 8; M = zeros(n, n)
        for i in range(n): M[i][i] = F(-rng.randint(1, 9), rng.randint(1, 5))
        for i in range(4):
            for j in range(4, 8):
                if rng.randint(0, 2) == 0:
                    v = F(rng.randint(-4, 4)); M[i][j] = v; M[j][i] = v      # symmetric coupling: a genuine Hermitian system
        nul += 1; fires += (rank(msub(M, tr(M))) > 0)
    N["obstruction_false_positives_on_hermitian_nulls"] = {"samples": nul, "fired": fires}
    check("obstruction.no_false_positive_on_hermitian_nulls", fires == 0, "rank(M - M^T) > 0 fired on %d/%d symmetric systems" % (fires, nul))
    # ---------------- specs
    sp = REPORT["specs"]
    nl_in = r6["null_out_of_class_independent_coupling"]
    sp["R1a_row4_elimination_T5"] = mkspec("G5-02:row4:elimination-clause", "TRANSFORMED_EXACT",
        "no additive inverse in (min,+): D - C A^-1 B does not exist for the (min,+) object as worded", FAMS, "T5_SEMIRING_TROPICAL", 0, 528, 528, 528,
        r4["null_maps"]["commuting"], r4["null_maps"]["samples"], 89,
        "block elimination exists with quotient and determinant structure; valuation of the Schur complement of I-K equals the (min,+) Kleene-star elimination",
        "object is the Q[q] lift K of the (min,+) matrix with nonnegative coefficients and val(K_BB)>=1; inverse becomes Kleene star; inertia statement not included",
        F(0), F(0))
    sp["R1b_row4_inertia_incomplete"] = mkspec("G5-02:row4:inertia-clause", "INVARIANT_FALSIFIED",
        "K is not symmetric (9 one-way edges); (min,+) has no negation, so Sylvester inertia of the object as worded is undefined", FAMS, None, 0, 528, 0, 528, 0, 40, 0, None, None, F(9, 1), F(9, 1),
        obs="support asymmetry survives diagonal gauge, symmetric additive shifts and tropicalisation; block-diagonal conjugacy is decided only at q=1/10, 1/100, 1/1000 for blocks of size 1 and 2 (impossible for 480 of 528 blocks and every one-way pair, possible for some singletons where the form is positive definite and so vacuous); symbolic q and larger blocks undecided", surv=False)
    sp["R2_row6_inertia_IF"] = mkspec("G5-14:row6:hermitian-inertia", "INVARIANT_FALSIFIED",
        "M=Liouvillian is not Hermitian (antisymmetric coupling, rank(M-M^T)=8); In(M) undefined", FAMS, None, 0, 17, 0, 17, N["obstruction_false_positives_on_hermitian_nulls"]["fired"],
        N["obstruction_false_positives_on_hermitian_nulls"]["samples"], 0, None, None, F(8, 1), F(8, 1),
        obs="antisymmetric coupling B!=0 with C=-B^T: no block-diagonal similarity, congruence, complex affine map or partition-respecting compression makes M Hermitian; spectral-inertia rescue is vacuous (G1)", surv=True)
    sp["R2x_row6_spectral_rescue_rejected"] = mkspec("G5-14:row6:spectral-inertia", "TRANSFORMED_EXACT",
        "Sylvester inertia of M undefined", FAMS, "T1_GAUGE_SIMILARITY", 0, 17, 17, 17, nl_in["additive"], nl_in["tested"], 16,
        "number of eigenvalues by sign of real part is additive over the Schur split", "inertia of the Hermitian form replaced by spectral inertia of the operator; needs sym(M)<=0 and A invertible",
        F(0), F(0))
    sp["R3_equiv_IF"] = mkspec("G5-04:rows1-5:equivalence", "INVARIANT_FALSIFIED",
        "no partition-respecting congruence class agrees on any of the 168 (spectral inertia, AeST) pairs", FAMS, None, 0, 168, 0, 168,
        0, eq["congruence_invariance"]["tested"], 0, None, None, F(1, 1), F(1, 1),
        obs="(In A, In S) and the dimensions are invariants of congruence, linear charts, additive linear terms; global shift and compressions are vacuous (G1)", surv=True)
    t4 = eq["T4_global_shift"]
    sp["R3x_equiv_T4_shift_rejected"] = mkspec("G5-04:T4-global-shift", "TRANSFORMED_EXACT", "inertia pairs differ", FAMS, "T4_SPECTRAL_PSD_SHIFT", 1, 168, 168, 168,
        t4["null_real_equivalent"], max(t4["null_pairs"], 1), 3, "pivot and Schur block signs", "all objects replaced by M + lambda I with lambda above a row-sum bound", F(0), F(0))
    t6 = eq["T6_pivot_only"]
    sp["R3y_equiv_T6_pivot_only_rejected"] = mkspec("G5-04:T6-pivot-only", "TRANSFORMED_EXACT", "inertia pairs differ", FAMS, "T6_SUBSPACE_PROJECTION", 0, 168, 168, 168,
        t6["null_equivalent"], t6["null_pd_pairs"], 4, "pivot block inertia", "Schur block and coupling dropped; claim is about the 2x2 pivot blocks only", F(0), F(0))
    bc = lat["basis_change"]
    sp["R4_lattice_basis_change_T1"] = mkspec("G5-06:basis-change", "TRANSFORMED_EXACT",
        "naive basis change U L loses the rank-1 collapse", FAMS, "T1_GAUGE_SIMILARITY", 0, bc["carried_changes"], bc["carried_S_el_unchanged"], bc["carried_changes"],
        bc["naive_keeps_rank"], bc["naive_changes"], 9, "S_el unchanged and S_lat covariant: S_lat' = (U^-1 x I)^T S_lat (U^-1 x I)",
        "basis change carries the bridge translations m' = m U^-1 so that every bar vector is unchanged", F(0), F(0))
    ct = lat["commuting_test"]
    sp["R5_commuting_test_rejected"] = mkspec("G5-05:commuting-defect", "TRANSFORMED_EXACT",
        "zero commuting defect does not single out Phi", FAMS, "T6_SUBSPACE_PROJECTION", ct["free_entries_block_upper_class"], ct["independent_defect_constraints"], ct["zero_defect"] and ct["random_block_upper_maps"], ct["random_block_upper_maps"],
        ct["zero_defect"], ct["random_block_upper_maps"], 54, "naturality of the Schur complement under block-upper-triangular maps with identity leading block",
        "claim restricted to the block-upper-triangular class", F(0), F(0))
    # ---------------- must-fail controls
    # (c1) wrong transformation: symmetric-part Schur complement does not reproduce the ledger Schur complement (row 6)
    control("c1.S_of_symmetric_part_is_not_S", r6["S_ne_S_of_symmetric_part"] == r6["points"], "S(sym M) != S(M) at %d/%d points" % (r6["S_ne_S_of_symmetric_part"], r6["points"]))
    # (c2) wrong inertia notion: Sylvester inertia of sym(M) is not additive against In(A)+In(S(M))
    c2 = sum(1 for row in r6["rows"] if row["In(H)"] != row["In(sym A)+In(sym S(M))"])
    control("c2.sylvester_sum_with_ledger_schur_fails", c2 == r6["points"], "In(sym M) != In(A_sym)+In(sym S(M)) at %d/%d points (the package's own mismatch, recomputed)" % (c2, r6["points"]))
    # (c3) wrong tropical map: f(e)=e+1 as an 'exponent map' must not commute on blocks with paths through B; random monotone f must (almost) never commute
    control("c3.random_nonlinear_exponent_maps_rejected", r4["null_maps"]["commuting"] <= r4["null_maps"]["samples"] // 10, "%d/%d random monotone maps commute" % (r4["null_maps"]["commuting"], r4["null_maps"]["samples"]))
    # (c4) naive basis change must NOT leave S_el unchanged / collapse
    control("c4.naive_basis_change_loses_collapse", bc["naive_keeps_rank"] == 0, "naive changes keeping rank 1: %d/%d" % (bc["naive_keeps_rank"], bc["naive_changes"]))
    # (c5) spectral-inertia routine must refuse a non-dissipative matrix
    control("c5.dissipative_routine_refuses_nondissipative", spectral_inertia_dissipative(mat([[1, 0], [0, -1]])) is None and spectral_inertia_dissipative(mat([[0, 1], [1, 0]])) is None, "indefinite symmetric part rejected")
    # (c6) known-answer tests of the toolkit
    ok_in = inertia_sym(mat([[0, 1], [1, 0]])) == (1, 1, 0) and inertia_sym(mat([[1, 0], [0, 0]])) == (1, 0, 1) and inertia_sym(mat([[2, 1], [1, -3]])) == (1, 1, 0)
    cp = charpoly(mat([[2, 1], [0, 3]])); ok_cp = cp == [F(6), F(-5), F(1)]
    ok_st = sturm_real_roots([F(1), F(0), F(1)]) == 0 and sturm_real_roots([F(-1), F(0), F(1)]) == 2 and sturm_real_roots([F(0), F(0), F(0), F(1)]) == 1
    check("toolkit.known_answers", ok_in and ok_cp and ok_st, "inertia, charpoly, Sturm")
    ly = lyapunov_inertia(mat([[-1, 0], [0, 2]])); ly2 = lyapunov_inertia(mat([[0, 1], [-1, 0]]))
    check("toolkit.lyapunov_known", ly == (1, 1) and ly2 is None, "diag(-1,2) -> (#Re>0,#Re<0)=(1,1); rotation has imaginary eigenvalues -> None")
    # (c7) guards: must-fail specs for my guard function
    good = sp["R4_lattice_basis_change_T1"]
    g0 = my_guards(good)
    check("guards.good_spec_admitted", g0 == [], str(g0))
    bad = dict(good); bad["transform_dof"] = bad["held_out_constraints"]
    control("c7a.dof_equals_constraints_rejected", "G2_DOF" in my_guards(bad), str(my_guards(bad)))
    bad = dict(good); bad["null_false_pass_count"] = bad["null_total_count"]
    control("c7b.vacuous_null_rejected", "G1_VACUOUS" in my_guards(bad), str(my_guards(bad)))
    bad = dict(good); bad["transform_rank"] = 0
    control("c7c.zero_rank_rejected", "G1_ZERO_RANK" in my_guards(bad), str(my_guards(bad)))
    bad = dict(good); bad["relabelled_as_literal"] = True
    control("c7d.silent_relabel_rejected", "G3_SILENT" in my_guards(bad), str(my_guards(bad)))
    bad = dict(sp["R3_equiv_IF"]); bad["families_searched"] = FAMS[:1]
    control("c7e.falsified_with_one_family_rejected", "G4_SEARCH" in my_guards(bad), str(my_guards(bad)))
    bad = dict(sp["R3_equiv_IF"]); bad["proposed_verdict"] = "FALSIFIED_RAW"
    control("c7f.raw_falsification_rejected", "G4_RAW" in my_guards(bad), str(my_guards(bad)))
    bad = dict(good); bad["fixed_globally_before_holdout"] = False
    control("c7g.post_hoc_rejected", "G2_POST_HOC" in my_guards(bad), str(my_guards(bad)))
    # my own verdict for every spec
    for k, s in sp.items():
        s["_my_guard_reasons"] = my_guards(s)

def main():
    PK = sys.argv[1] if len(sys.argv) > 1 else None
    if PK is None or not os.path.isdir(PK):
        print("usage: law2b_check.py <path to verification/outside/gate5-unification>", file=sys.stderr); return 2
    row6(PK); row4(PK); equiv_search(PK); lattice_section(); m2_check(); heavy_lattice_n8(); g501_range_condition(); g501_witnesses(); claim18(PK)
    controls_and_specs()
    # normalise to JSON
    def conv(x):
        if isinstance(x, F): return str(x)
        if isinstance(x, dict): return {str(k): conv(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [conv(v) for v in x]
        return x
    REPORT["fails"] = FAILS
    REPORT["status"] = "ALL_CHECKS_PASSED" if not FAILS else "FAILED"
    sys.stdout.write(json.dumps(conv(REPORT), indent=1, sort_keys=True) + "\n")
    return 0 if not FAILS else 1

if __name__ == "__main__":
    sys.exit(main())
