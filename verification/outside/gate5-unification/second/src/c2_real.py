import os, sys, random, time
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from lat import *

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

CONTROL_FAIL = []

def sgn(x):
    """sign of a + b sqrt2 or Fraction"""
    if isinstance(x, QS2):
        a, b = x.a, x.b
        if not b:
            return (a > 0) - (a < 0)
        if not a:
            return (b > 0) - (b < 0)
        if a > 0 and b > 0: return 1
        if a < 0 and b < 0: return -1
        # opposite signs: compare a^2 with 2 b^2
        if a > 0:
            return 1 if a * a > 2 * b * b else -1
        return 1 if 2 * b * b > a * a else -1
    return (x > 0) - (x < 0)

def sym(M):
    return all(M[i][j] == M[j][i] for i in range(len(M)) for j in range(len(M)))

def sstr(x):
    return str(x)

def sylvester_H(n=8):
    return [[(-1) ** bin(i & j).count("1") for j in range(n)] for i in range(n)]

def C8():
    n = 8
    C = [[0] * n for _ in range(n)]
    C[0][1] = C[0][7] = -1
    C[1][0] = 1; C[1][2] = -1
    for k in range(2, 7):
        C[k][k - 1] = C[k][k + 1] = -1
    C[7][0] = 1; C[7][6] = -1
    return C

def L_E8_1():
    H = sylvester_H()
    return [[Fraction(2 if i == j else 0) + Fraction(H[i][j], 2) for j in range(8)] for i in range(8)]

def L_D8(a, t):
    C = C8()
    return [[(2 + a if i == j else 0) + t * C[i][j] for j in range(8)] for i in range(8)]

def L_E8_s(s):
    """fold curve over Q(sqrt2); s Fraction"""
    r2 = QS2(0, 1)
    s2 = Fraction(s) * Fraction(s)
    one = QS2(1, 0)
    Dp = (1 + 2 * r2) + (-1 + 2 * r2) * s2
    Dm = (-1 + 2 * r2) + (1 + 2 * r2) * s2
    ap = ((6 + 5 * r2) + (-6 + 5 * r2) * s2) / Dp
    am = ((2 + 3 * r2) + (-2 + 3 * r2) * s2) / Dm
    bp = 2 * r2 * Fraction(s) / Dp
    bm = 2 * r2 * Fraction(s) / Dm
    H = sylvester_H()
    plus = {0, 3, 5, 6}
    L = []
    for i in range(8):
        row = []
        for j in range(8):
            if i == j:
                row.append(ap if i in plus else am)
            else:
                row.append((bp if i in plus else bm) * H[i][j])
        L.append(row)
    return L

def L_D8_s(s):
    s = Fraction(s)
    r2 = QS2(0, 1)
    t = 2 * s / (1 + s * s)
    a = r2 * ((1 - s * s) / (1 + s * s))
    return L_D8(a, t), a, t

def toQ(M):
    return [[F(x) for x in r] for r in M]

def rowsq(L):
    n = len(L)
    out = []
    for i in range(n):
        b = [L[i][k] - (2 if i == k else 0) for k in range(n)]
        out.append(sum((x * x for x in b), Fraction(0)))
    return out

def inertia_rank1(S):
    n = len(S)
    r = rank(S)
    if r == 0:
        return (0, 0, n)
    if r == 1 and sym(S):
        tr = sum((S[i][i] for i in range(n)), Fraction(0))
        return ((1, 0, n - 1) if sgn(tr) > 0 else (0, 1, n - 1))
    return None

def rank1_form(S, vec_pos=None):
    """returns (c, v) with S = c v v^T for rank-1 symmetric S, using v = column p"""
    n = len(S)
    p = next(i for i in range(n) if S[i][i])
    return p

def analyze(name, L, deep=True):
    t0 = time.time()
    n = len(L)
    res = {}
    P("== instance %s ==" % name)
    P("det L = %s ; |b_i|^2 = %s" % (det(L), sorted(set(str(x) for x in rowsq(L)))))
    bars = standard_bars(L)
    d0, ae, Z = matrices(n, bars)
    nb = len(bars)
    rk = rank(d0)
    P("bars=%d rank d0=%d H0=%d H1=%d" % (nb, rk, 2 * n * n - rk, nb - rk))
    Delta, Bel, Blat, Kel, Klat = gram_blocks(d0, ae, Z)
    Hlat, Rlat = full_H(d0, Z)
    Hel, Rel = full_H(d0, ae)
    Phi = build_Phi(L, n)
    RL = RL_block(Phi, n)
    c1a = eq(Rel, mm(Rlat, Phi))
    PhiT_H_Phi = mm(T(Phi), mm(Hlat, Phi))
    c1b = eq(Hel, PhiT_H_Phi)
    P("C1 R_el == R_lat Phi: %s ; H_el == Phi^T H_lat Phi: %s" % (c1a, c1b))
    nu = 2 * n * n
    Se, Sl = S_both(Delta, Bel, Blat, Kel, Klat)
    S_Hlat = schur128(sub(Hlat, 0, nu, 0, nu), sub(Hlat, 0, nu, nu, Hlat.__len__()), sub(Hlat, nu, len(Hlat), nu, len(Hlat)))
    S_prod = schur128(sub(PhiT_H_Phi, 0, nu, 0, nu), sub(PhiT_H_Phi, 0, nu, nu, len(PhiT_H_Phi)), sub(PhiT_H_Phi, nu, len(PhiT_H_Phi), nu, len(PhiT_H_Phi)))
    defect = madd(S_prod, mm(T(RL), mm(S_Hlat, RL)), -1)
    P("C2 defect zero: %s ; Schur(Phi^T H_lat Phi) == S_el direct: %s ; Schur(H_lat) == S_lat direct: %s" % (is_zero(defect), eq(S_prod, Se), eq(S_Hlat, Sl)))
    # pseudo-inverse independent form
    Nst = nullspace(T(d0), nb)
    G = [[sum((a[r] * b[r] for r in range(nb) if a[r]), Fraction(0)) for b in Nst] for a in Nst]
    Gi = inverse(G)
    AeN = mm(T(ae), T(Nst))  # (ns x nb)(nb x s)
    S_pi = msc(HALF, mm(AeN, mm(Gi, T(AeN))))
    P("S_el == (1/2) ae^T Pi ae (Pi = N G^-1 N^T): %s ; self-stress dim=%d (expected nb-rank = %d)" % (eq(S_pi, Se), len(Nst), nb - rk))
    ns = len(Se)
    r_e, r_l = rank(Se), rank(Sl)
    in_e, in_l = inertia_rank1(Se), inertia_rank1(Sl)
    tr = sum((Se[i][i] for i in range(ns)), Fraction(0))
    P("C3 rank S_el=%d inertia=%s ; rank S_lat=%d inertia=%s ; sym S_el=%s S_lat=%s" % (r_e, in_e, r_l, in_l, sym(Se), sym(Sl)))
    P("   trace S_el=%s ; S_00=%s ; det L=%s" % (sstr(tr), sstr(Se[0][0]), det(L)))
    # C4
    basis = diag_dim_and_basis(L)
    P("C5 dim Z_B = %d ; rank of z->sigma_c map = %d ; virial-route rank(ae^T N) = %d" % (len(basis), rank_sigma_map(L, basis), virial_rank(d0, ae)[0]))
    if len(basis) == 1:
        z = basis[0]
        z = [x / z[1] for x in z]
        # confirm diag(z) L symmetric
        DL = [[z[i] * L[i][j] for j in range(n)] for i in range(n)]
        P("C4 z =", [sstr(x) for x in z], "diag(z)L symmetric:", sym(DL))
        Bm = [[L[i][j] - (2 if i == j else 0) for j in range(n)] for i in range(n)]
        sg = sigma_c(L, z)
        p = next(i for i in range(len(sg)) if sg[i])
        c_el = Se[p][p] / (sg[p] * sg[p])
        ok_el = all(Se[i][j] == c_el * sg[i] * sg[j] for i in range(ns) for j in range(ns))
        w = [z[k] * Bm[k][l] for k in range(n) for l in range(n)]
        q = next(i for i in range(len(w)) if w[i])
        c_lat = Sl[q][q] / (w[q] * w[q])
        ok_lat = all(Sl[i][j] == c_lat * w[i] * w[j] for i in range(n * n) for j in range(n * n))
        P("C4 S_el = c sigma sigma^T: %s (c=%s) ; S_lat = c w w^T: %s (c=%s) ; c_el==c_lat: %s" % (ok_el, sstr(c_el), ok_lat, sstr(c_lat), c_el == c_lat))
        if name == "E8 s=1":
            H = sylvester_H()
            full = [[(2 if i == j else 0) + H[i][j] for j in range(n)] for i in range(n)]
            exp = [full[i][i] for i in range(n)] + [2 * full[k][l] for k in range(n) for l in range(k + 1, n)]
            P("   sigma == 2I+H (coordinates): %s ; c == 3/92: %s" % (all(sg[i] == exp[i] for i in range(len(exp))), c_el == Fraction(3, 92)))
        if name == "D8 s=1":
            P("   z == (-1,1,..,1): %s ; c == 1/32: %s" % (z == [Fraction(-1)] + [Fraction(1)] * 7, c_el == Fraction(1, 32)))
        for lam in (Fraction(2), Fraction(-3), Fraction(1, 5)):
            zl = [lam * x for x in z]
            sgl = sigma_c(L, zl)
            pl = next(i for i in range(len(sgl)) if sgl[i])
            cl = Se[pl][pl] / (sgl[pl] * sgl[pl])
            okl = all(Se[i][j] == cl * sgl[i] * sgl[j] for i in range(ns) for j in range(ns))
            P("   z scaled by %s: c' = c/lam^2: %s (S_el still = c' sigma' sigma'^T: %s)" % (lam, cl == c_el / (lam * lam), okl))
    # controls
    wrong_schur = madd(Kel, mm(T(Bel), solve_consistent(Delta, [[-x for x in r] for r in Bel])), -1) if False else None
    Xe = solve_consistent(Delta, [[-x for x in r] for r in Bel])
    S_wrong = madd(Kel, mm(T(Bel), Xe), -1)          # wrong sign: K - B^T X
    ctrl1 = not eq(S_wrong, Se)
    Lw = [list(r) for r in L]
    Lw[0][1] = Lw[0][1] + 1
    Phi_w = build_Phi(Lw, n)
    ctrl2 = not eq(Rel, mm(Rlat, Phi_w))
    Phi_p = [list(r) for r in Phi]
    Phi_p[0][nu] = Phi_p[0][nu] + 1
    ctrl3 = not eq(Hel, mm(T(Phi_p), mm(Hlat, Phi_p)))
    P("CONTROLS (each must be flagged as failing): wrong Schur sign differs from S_el: %s ; wrong Phi (L[0][1] shifted by 1) breaks R_el=R_lat Phi: %s ; perturbed Phi breaks congruence: %s" % (ctrl1, ctrl2, ctrl3))
    if not (ctrl1 and ctrl2 and ctrl3):
        CONTROL_FAIL.append(name)
    return dict(L=L, bars=bars, Se=Se, Sl=Sl)

def collapse_summary(S):
    r = rank(S)
    return r

def basis_change_tests(name, L, seeds):
    n = len(L)
    P("-- C6 basis change on %s --" % name)
    bars0 = standard_bars(L)
    d0, ae, Z = matrices(n, bars0)
    Delta, Bel, Blat, Kel, Klat = gram_blocks(d0, ae, Z)
    Se0, Sl0 = S_both(Delta, Bel, Blat, Kel, Klat)
    for sd in seeds:
        r = random.Random(sd)
        U = rand_unimodular(r, n, 14)
        Ui = inverse(U)
        L2 = mm(U, L)
        # naive: standard bars on the changed basis
        bn = standard_bars(L2)
        d0n, aen, Zn = matrices(n, bn)
        Dn, Ben, Bln, Ken, Kln = gram_blocks(d0n, aen, Zn)
        Sen, Sln = S_both(Dn, Ben, Bln, Ken, Kln)
        rn = rank(Sen)
        # carried: keep every ell
        bc = []
        for (u, v, m, ell) in bars0:
            m2 = [sum((m[k] * Ui[k][j] for k in range(n)), Fraction(0)) for j in range(n)]
            xvv, xuu = xv(n, v), xv(n, u)
            ell2 = [xvv[k] - xuu[k] + sum((m2[j] * L2[j][k] for j in range(n)), Fraction(0)) for k in range(n)]
            if ell2 != ell:
                raise ValueError("carried bar vector changed")
            bc.append((u, v, m2, ell2))
        d0c, aec, Zc = matrices(n, bc)
        Dc, Bec, Blc, Kec, Klc = gram_blocks(d0c, aec, Zc)
        Sec, Slc = S_both(Dc, Bec, Blc, Kec, Klc)
        UiK = [[Ui[a][b] if k == l else Fraction(0) for b in range(n) for l in range(n)] for a in range(n) for k in range(n)]
        pred = mm(T(UiK), mm(Sl0, UiK))
        P("  U seed %d: naive rank S_el=%d (collapse kept: %s) ; carried: S_el unchanged=%s, S_lat' = (U^-1 x I)^T S_lat (U^-1 x I): %s" % (sd, rn, rn == 1, eq(Sec, Se0), eq(Slc, pred)))
        # carried defect zero
        Hl, Rl = full_H(d0c, Zc)
        Phi2 = build_Phi(L2, n)
        RL2 = RL_block(Phi2, n)
        nu = 2 * n * n
        Sh = schur128(sub(Hl, 0, nu, 0, nu), sub(Hl, 0, nu, nu, len(Hl)), sub(Hl, nu, len(Hl), nu, len(Hl)))
        PH = mm(T(Phi2), mm(Hl, Phi2))
        Sp = schur128(sub(PH, 0, nu, 0, nu), sub(PH, 0, nu, nu, len(PH)), sub(PH, nu, len(PH), nu, len(PH)))
        dd = madd(Sp, mm(T(RL2), mm(Sh, RL2)), -1)
        P("     carried: defect zero=%s ; carried H_el == Phi'^T H_lat' Phi'=%s" % (is_zero(dd), eq(full_H(d0c, aec)[0], PH)))

def scaling_tests(name, L):
    n = len(L)
    P("-- C7 scaling on %s --" % name)
    d0, ae, Z = matrices(n, standard_bars(L))
    Se0 = S_both(*gram_blocks(d0, ae, Z))[0]
    for lam in (Fraction(2), Fraction(1, 3), Fraction(5, 2), Fraction(-1)):
        Ls = [[lam * x for x in r] for r in L]
        d0s, aes, Zs = matrices(n, standard_bars(Ls, lam))
        Ses = S_both(*gram_blocks(d0s, aes, Zs))[0]
        lam4 = lam ** 4
        ok = eq(Ses, msc(lam4, Se0))
        # L-only scaling
        d0l, ael, Zl = matrices(n, standard_bars(Ls))
        Sel = S_both(*gram_blocks(d0l, ael, Zl))[0]
        P("  lam=%s: global scale S -> lam^4 S exactly: %s ; L-only scale: rank S=%d inertia=%s" % (lam, ok, rank(Sel), inertia_charpoly(Sel) if not any(isinstance(x, QS2) for r in Sel for x in r) else inertia_rank1(Sel)))

def main():
    # check fold-curve consistency
    P("fold-curve checks over Q(sqrt2):")
    L0 = L_E8_s(Fraction(0))
    two_r2 = [[(QS2(2, 1) if i == j else QS2(0, 0)) for j in range(8)] for i in range(8)]
    P("  L8(0) == (2+sqrt2) I: %s" % all(L0[i][j] == two_r2[i][j] for i in range(8) for j in range(8)))
    L1 = L_E8_s(Fraction(1))
    E = L_E8_1()
    P("  L8(1) == 2I + H/2: %s" % all(L1[i][j] == E[i][j] for i in range(8) for j in range(8)))
    for s in (Fraction(1, 2), Fraction(1, 3)):
        P("  s=%s: |b_i|^2 all == 2: %s" % (s, all(x == 2 for x in rowsq(L_E8_s(s)))))
    Ld, a, t = L_D8_s(Fraction(1, 2))
    P("  D8 s=1/2: a^2+2t^2 == 2: %s" % ((a * a + 2 * t * t) == 2))
    insts = [
        ("E8 s=1", L_E8_1()),
        ("E8 s=1/2", L_E8_s(Fraction(1, 2))),
        ("D8 s=1", L_D8(Fraction(0), Fraction(1))),
        ("D8 s=1/2", Ld),
        ("D8 (a,t)=(4/3,1/3)", L_D8(Fraction(4, 3), Fraction(1, 3))),
    ]
    store = {}
    for name, L in insts:
        store[name] = analyze(name, [[x for x in r] for r in L])
    # expected exact values
    P("== expected-value comparison ==")
    exp_tr = {"E8 s=1": Fraction(114, 23), "D8 s=1": Fraction(23, 4), "D8 (a,t)=(4/3,1/3)": Fraction(17297, 1488)}
    for nm, v in exp_tr.items():
        S = store[nm]["Se"]
        tr = sum((S[i][i] for i in range(36)), Fraction(0))
        P("  trace %s: %s expected %s -> %s" % (nm, tr, v, tr == v))
    P("  S_00 E8 s=1 == 27/92: %s ; S_00 D8 s=1 == 1/8: %s" % (store["E8 s=1"]["Se"][0][0] == Fraction(27, 92), store["D8 s=1"]["Se"][0][0] == Fraction(1, 8)))
    Hm = sylvester_H()
    Mx = [[Fraction((2 if i == j else 0) + Hm[i][j]) for j in range(8)] for i in range(8)]
    P("  inertia(2I+H) = %s (upstream says (4,4,0))" % (inertia_charpoly(Mx),))
    # basis change and scaling
    basis_change_tests("E8 s=1", toQ(store["E8 s=1"]["L"]), [1101, 1102])
    basis_change_tests("D8 s=1", toQ(store["D8 s=1"]["L"]), [1201, 1202])
    scaling_tests("E8 s=1", toQ(store["E8 s=1"]["L"]))
    scaling_tests("D8 s=1", toQ(store["D8 s=1"]["L"]))
    with open(os.path.join(here, "..", "out", "c2_real.txt"), "w", newline="\n") as fh:
        fh.write("\n".join(OUT) + "\n")
    if CONTROL_FAIL:
        print("CONTROL PASSED (check is vacuous) on:", CONTROL_FAIL)
        sys.exit(2)

main()
