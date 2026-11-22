import os, sys, random
from fractions import Fraction
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from exact import *

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

class Refused(Exception):
    pass

def is_herm_type(M):
    return any(isinstance(x, Gq) and x.im for r in M for x in r)

def real_embed(M):
    n = len(M)
    R = [[Fraction(0)] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            x = Gq.c(M[i][j]) if not isinstance(M[i][j], Gq) else M[i][j]
            R[i][j] = x.re
            R[n + i][n + j] = x.re
            R[i][n + j] = -x.im
            R[n + i][j] = x.im
    return R

def inertia(M):
    """Inertia via characteristic polynomial and Descartes sign count."""
    n = len(M)
    if n == 0:
        return (0, 0, 0)
    if is_herm_type(M):
        p, q, z = inertia_charpoly(real_embed(M))
        if p % 2 or q % 2 or z % 2:
            raise ValueError("odd embedded inertia")
        return (p // 2, q // 2, z // 2)
    R = [[(x.re if isinstance(x, Gq) else x) for x in r] for r in M]
    return inertia_charpoly(R)

def is_hermitian(M):
    n = len(M)
    return all(M[i][j] == conj(M[j][i]) for i in range(n) for j in range(n))

def block(M, k):
    n = len(M)
    return (sub(M, 0, k, 0, k), sub(M, 0, k, k, n), sub(M, k, n, 0, k), sub(M, k, n, k, n))

def schur(M, k):
    A, B, C, D = block(M, k)
    if det(A) == 0:
        raise Refused("singular pivot block")
    return D - mm(C, mm(inverse(A), B)) if False else madd(D, mm(C, mm(inverse(A), B)), -1)

def Vmat(M, k):
    n = len(M)
    A, B, C, D = block(M, k)
    Ai = inverse(A)
    V = eye(n)
    X = mm(Ai, B)
    for i in range(k):
        for j in range(n - k):
            V[i][k + j] = -X[i][j]
    return V

def addi(a, b):
    return tuple(x + y for x, y in zip(a, b))

def checks(M, k, S):
    """returns (inertia_ok, det_ok, congruence_ok)"""
    A = sub(M, 0, k, 0, k)
    n = len(M)
    iM, iA, iS = inertia(M), inertia(A), inertia(S)
    ok_in = (iM == addi(iA, iS))
    ok_det = (det(M) == det(A) * det(S)) if S else (det(M) == det(A))
    V = Vmat(M, k)
    Dg = zeros(n, n)
    for i in range(k):
        for j in range(k):
            Dg[i][j] = A[i][j]
    for i in range(n - k):
        for j in range(n - k):
            Dg[k + i][k + j] = S[i][j]
    ok_cong = eq(mm(ct(V), mm(M, V)), Dg)
    return ok_in, ok_det, ok_cong

# ------------------------------------------------------------- families
def ri(r, a, b):
    return r.randint(a, b)

def fam_intsym(r, n):
    M = zeros(n, n)
    for i in range(n):
        for j in range(i, n):
            M[i][j] = M[j][i] = Fraction(ri(r, -3, 3))
    return M

def fam_banded(r, n):
    bw = r.choice([1, 2])
    M = zeros(n, n)
    for i in range(n):
        for j in range(i, min(n, i + bw + 1)):
            M[i][j] = M[j][i] = Fraction(ri(r, -4, 4))
    return M

def fam_circulant(r, n):
    c = [Fraction(ri(r, -3, 3)) for _ in range(n // 2 + 1)]
    M = zeros(n, n)
    for i in range(n):
        for j in range(n):
            d = (j - i) % n
            M[i][j] = c[min(d, n - d)]
    return M

def fam_hilbert(r, n):
    sh = r.choice([0, 0, 1, 2])
    cc = r.choice([Fraction(0), Fraction(1, 2), Fraction(1, 3), Fraction(1, 7)])
    M = zeros(n, n)
    for i in range(n):
        for j in range(n):
            M[i][j] = Fraction(1, i + j + 1 + sh) - (cc if i == j else 0)
            if r.random() < 0 :
                pass
    sgn = r.choice([1, 1, -1])
    if sgn < 0:  # signed Hilbert-type: D H D with D = diag(+-1)
        d = [r.choice([1, -1]) for _ in range(n)]
        M = [[M[i][j] * d[i] * d[j] for j in range(n)] for i in range(n)]
    return M

def fam_gram_psd(r, n):
    k = max(1, n - r.choice([1, 2, 3]))
    X = [[Fraction(ri(r, -2, 2)) for _ in range(n)] for _ in range(k)]
    return mm(T(X), X)

def fam_gram_indef(r, n):
    k = max(1, n - r.choice([0, 1, 2]))
    X = [[Fraction(ri(r, -2, 2)) for _ in range(n)] for _ in range(k)]
    J = zeros(k, k)
    for i in range(k):
        J[i][i] = Fraction(r.choice([1, -1]))
    return mm(T(X), mm(J, X))

def rg(r, a=2):
    return Gq(ri(r, -a, a), ri(r, -a, a))

def fam_herm(r, n):
    M = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        M[i][i] = Gq(ri(r, -3, 3), 0)
        for j in range(i + 1, n):
            g = rg(r, 2)
            M[i][j] = g
            M[j][i] = g.conj()
    return M

def fam_herm_gram(r, n):
    k = max(1, n - r.choice([1, 2, 3]))
    X = [[rg(r, 1) for _ in range(n)] for _ in range(k)]
    return mm(ct(X), X)

def fam_sparse0(r, n):
    """symmetric, sparse, zero diagonal (pivots often singular)"""
    M = zeros(n, n)
    for i in range(n):
        for j in range(i + 1, n):
            if r.random() < 0.35:
                M[i][j] = M[j][i] = Fraction(ri(r, -2, 2))
    return M

FAMS = [("intsym", fam_intsym), ("banded", fam_banded), ("circulant", fam_circulant),
        ("hilbert", fam_hilbert), ("gram_psd", fam_gram_psd), ("gram_indef", fam_gram_indef),
        ("herm_Qi", fam_herm), ("herm_gram_Qi", fam_herm_gram), ("sparse_zero_diag", fam_sparse0)]
PER = 64

def main():
    tot = 0
    inv_n = 0
    ref_n = 0
    ref_ok = 0
    sing_expected = 0
    allpass = 0
    fails = []
    wrong1_pass = 0
    wrong2_pass = 0
    P("C1 clean-room panel: families=%d per_family=%d total=%d sizes 2..10" % (len(FAMS), PER, len(FAMS) * PER))
    P("%-18s %5s %7s %7s %7s %7s %7s" % ("family", "sys", "invert", "refuse", "inertia", "det", "congr"))
    for fi, (name, gen) in enumerate(FAMS):
        c_sys = c_inv = c_ref = c_in = c_det = c_cg = 0
        for t in range(PER):
            seed = 4100000 + 1000 * fi + t
            r = random.Random(seed)
            n = 2 + (t % 9)
            M = gen(r, n)
            if not is_hermitian(M):
                raise ValueError("generator produced non-Hermitian matrix")
            k = r.randint(1, n - 1)
            c_sys += 1
            A = sub(M, 0, k, 0, k)
            singular = (det(A) == 0)
            if singular:
                sing_expected += 1
                try:
                    schur(M, k)
                    ref_ok += 0  # not refused: error
                    fails.append(("singular pivot NOT refused", name, n, k, seed))
                except Refused:
                    ref_ok += 1
                c_ref += 1
                continue
            S = schur(M, k)
            if not is_hermitian(S):
                fails.append(("S not Hermitian", name, n, k, seed))
            a, b, c = checks(M, k, S)
            c_inv += 1
            c_in += a; c_det += b; c_cg += c
            if not (a and b and c):
                fails.append(("identity failed", name, n, k, seed, (a, b, c)))
            else:
                allpass += 1
            # controls
            A_, B_, C_, D_ = block(M, k)
            Sw1 = madd(D_, mm(C_, mm(inverse(A_), B_)), 1)      # wrong sign
            Sw2 = madd(D_, mm(C_, mm(A_, B_)), -1)               # A instead of A^-1
            if all(checks(M, k, Sw1)):
                wrong1_pass += 1
            if all(checks(M, k, Sw2)):
                wrong2_pass += 1
        P("%-18s %5d %7d %7d %7d %7d %7d" % (name, c_sys, c_inv, c_ref, c_in, c_det, c_cg))
        tot += c_sys; inv_n += c_inv; ref_n += c_ref
    P("TOTAL systems=%d invertible_pivot=%d singular_pivot=%d" % (tot, inv_n, ref_n))
    P("PASS RATE (invertible pivot, all three identities): %d/%d" % (allpass, inv_n))
    P("SINGULAR PIVOTS refused: %d/%d" % (ref_ok, sing_expected))
    # handcrafted refusal example: [[0,1],[1,0]], k=1
    Mh = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    try:
        schur(Mh, 1)
        hand = False
    except Refused:
        hand = True
    P("handcrafted [[0,1],[1,0]] k=1 refused: %s ; inertia(M)=%s" % (hand, inertia(Mh)))
    # smallest counterexample
    if fails:
        P("FAILURES: %d" % len(fails))
        for f in sorted(fails, key=lambda f: (f[2], f[3]))[:5]:
            P("  ", f)
    else:
        P("FAILURES: 0 (no counterexample)")
    # sanity check of inertia routine on known matrices
    known = [([[1, 0, 0], [0, -1, 0], [0, 0, 0]], (1, 1, 1)),
             ([[2, 1], [1, 2]], (2, 0, 0)), ([[0, 1], [1, 0]], (1, 1, 0)),
             ([[1, 2], [2, 1]], (1, 1, 0))]
    okk = all(inertia([[Fraction(x) for x in r] for r in m]) == e for m, e in known)
    P("inertia routine known-answer checks: %s" % okk)
    herm = [[Gq(0, 0), Gq(0, 1)], [Gq(0, -1), Gq(0, 0)]]
    P("Hermitian [[0,i],[-i,0]] inertia: %s (expect (1,1,0))" % (inertia(herm),))
    P("CONTROL wrong Schur D + C A^-1 B passes all identities on %d/%d systems (must be < total)" % (wrong1_pass, inv_n))
    P("CONTROL wrong Schur D - C A B passes all identities on %d/%d systems (must be < total)" % (wrong2_pass, inv_n))
    bad = (wrong1_pass == inv_n) or (wrong2_pass == inv_n) or (not okk)
    with open(os.path.join(here, "..", "out", "c1_block.txt"), "w", newline="\n") as fh:
        fh.write("\n".join(OUT) + "\n")
    if bad:
        print("CONTROL PASSED: checker is vacuous")
        sys.exit(2)

main()
