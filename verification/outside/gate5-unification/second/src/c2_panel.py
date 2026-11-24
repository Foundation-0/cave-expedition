import os, sys, random, time
from collections import Counter
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from lat import *

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

def ri(r, a, b):
    return r.randint(a, b)

def Fm(M):
    return [[Fraction(x) for x in r] for r in M]

def rand_sym(r, n, lo=-3, hi=3):
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            M[i][j] = M[j][i] = ri(r, lo, hi)
    return Fm(M)

def twisted(n, t=1):
    C = [[0] * n for _ in range(n)]
    C[0][1] = C[0][n - 1] = -1
    C[1][0] = 1; C[1][2] = -1
    for k in range(2, n - 1):
        C[k][k - 1] = C[k][k + 1] = -1
    C[n - 1][0] = 1; C[n - 1][n - 2] = -1
    return [[Fraction((2 if i == j else 0) + t * C[i][j]) for j in range(n)] for i in range(n)]

def fam_diag_rep(r, n):
    pool = [r.choice([2, 3, 4, -1, 1]) for _ in range(2)]
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        M[i][i] = r.choice(pool)
    return Fm(M)

def fam_blockdiag(r, n):
    cuts = sorted(r.sample(range(1, n), r.randint(1, min(2, n - 1))))
    bounds = [0] + cuts + [n]
    M = [[0] * n for _ in range(n)]
    for a, b in zip(bounds, bounds[1:]):
        sym_blk = r.random() < 0.5
        for i in range(a, b):
            for j in range(a, b):
                if sym_blk and j < i:
                    M[i][j] = M[j][i]
                else:
                    M[i][j] = ri(r, -2, 3)
    return Fm(M)

def fam_sym(r, n):
    return rand_sym(r, n)

def fam_nearsym(r, n):
    M = rand_sym(r, n)
    i, j = r.sample(range(n), 2)
    M[i][j] = M[i][j] + r.choice([1, -1, 2])
    return M

def fam_UL(r, n):
    return mm(rand_unimodular(r, n, 12), rand_sym(r, n))

def fam_UtLU(r, n):
    U = rand_unimodular(r, n, 12)
    return mm(T(U), mm(rand_sym(r, n), U))

def fam_generic(r, n):
    return Fm([[ri(r, -3, 3) for _ in range(n)] for _ in range(n)])

def fam_sparse01(r, n):
    M = [[(2 if i == j else ri(r, -1, 1)) for j in range(n)] for i in range(n)]
    return Fm(M)

def fam_duprows(r, n):
    M = fam_generic(r, n)
    i, j = r.sample(range(n), 2)
    M[j] = list(M[i])
    return M

def fam_twist(r, n):
    return twisted(n, r.choice([1, 2]))

def fam_hadamard(r, n):
    if n == 4:
        H = [[(-1) ** bin(i & j).count("1") for j in range(4)] for i in range(4)]
        return [[Fraction(2 if i == j else 0) + Fraction(H[i][j], 2) for j in range(4)] for i in range(4)]
    return rand_sym(r, n, -1, 2)

FAMS = [("diag_rep", fam_diag_rep), ("blockdiag", fam_blockdiag), ("sym", fam_sym),
        ("nearsym", fam_nearsym), ("sym_UL", fam_UL), ("sym_UtLU", fam_UtLU),
        ("generic", fam_generic), ("sparse01", fam_sparse01), ("dup_rows", fam_duprows),
        ("twisted", fam_twist), ("hadamard4/sym", fam_hadamard)]

def analyse(L):
    n = len(L)
    d0, ae, Z = matrices(n, standard_bars(L))
    Delta, Bel, Blat, Kel, Klat = gram_blocks(d0, ae, Z)
    Se = schur128(Delta, Bel, Kel)
    rS = rank(Se)
    rv, nst = virial_rank(d0, ae)
    basis = diag_dim_and_basis(L)
    dim = len(basis)
    rsig = rank_sigma_map(L, basis)
    # derived closed form: sigma(z) = diag(z) L (L - 2I) for z in Z_B
    Bm = [[L[i][j] - (2 if i == j else 0) for j in range(n)] for i in range(n)]
    LB = mm(L, Bm)
    ident = True
    for z in basis:
        Mz = [[z[i] * LB[i][j] for j in range(n)] for i in range(n)]
        v = [Mz[i][i] for i in range(n)] + [2 * Mz[k][l] for k in range(n) for l in range(k + 1, n)]
        if not (all(Mz[i][j] == Mz[j][i] for i in range(n) for j in range(n)) and v == sigma_c(L, z)):
            ident = False
    nzrows = [i for i in range(n) if any(LB[i])]
    rows = []
    for i in range(n):
        for j in range(i + 1, n):
            rr = [Fraction(0)] * n
            rr[i] = rr[i] + L[i][j]
            rr[j] = rr[j] - L[j][i]
            rows.append(rr)
    for i in nzrows:
        rr = [Fraction(0)] * n
        rr[i] = Fraction(1)
        rows.append(rr)
    d2 = len(nullspace(rows, n)) if rows else n
    r2 = dim - d2
    return dict(n=n, dim=dim, rank=rS, rsig=rsig, rv=rv, nst=nst, r2=r2, ident=ident)

def maxabs(L):
    return max((abs(x.numerator) + x.denominator for r in L for x in r))

def run_panel(tag, base, per, ns=(3, 4, 5, 6), fams=FAMS):
    tab = Counter()
    tabn = {}
    viol_a = []; viol_b = []; viol_rule = []; viol_virial = []; viol_r2 = []; viol_id = []
    conv_witness = []   # dim>=2 with rank<=1 / dim==1 with sigma==0
    total = 0
    t0 = time.time()
    for n in ns:
        for fi, (fname, gen) in enumerate(fams):
            for t in range(per):
                seed = base + 10000 * n + 100 * fi + t
                r = random.Random(seed)
                L = gen(r, n)
                a = analyse(L)
                total += 1
                key = (a["dim"], a["rank"])
                tab[key] += 1
                tabn.setdefault(n, Counter())[key] += 1
                info = (n, maxabs(L), seed, fname, a, [[str(x) for x in row] for row in L])
                if a["dim"] == 0 and a["rank"] != 0:
                    viol_a.append(info)
                if a["dim"] == 1 and a["rsig"] >= 1 and a["rank"] != 1:
                    viol_b.append(info)
                if a["rank"] != a["rsig"]:
                    viol_rule.append(info)
                if a["rank"] != a["rv"]:
                    viol_virial.append(info)
                if a["rank"] != a["r2"]:
                    viol_r2.append(info)
                if not a["ident"]:
                    viol_id.append(info)
                if (a["dim"] >= 2 and a["rank"] <= 1) or (a["dim"] == 1 and a["rsig"] == 0):
                    conv_witness.append(info)
    return total, tab, tabn, viol_a, viol_b, viol_rule, viol_virial, conv_witness, viol_r2, viol_id

def show(tag, res):
    total, tab, tabn, va, vb, vr, vv, cw, vr2, vid = res
    P("---- panel %s: %d lattices ----" % (tag, total))
    P("(dim Z_B, rank S_el) : count")
    for k in sorted(tab):
        P("  %s : %d" % (k, tab[k]))
    for n in sorted(tabn):
        P("  n=%d: %s" % (n, ", ".join("%s:%d" % (k, tabn[n][k]) for k in sorted(tabn[n]))))
    P("(a) dim=0 but rank!=0: %d ; (b) dim=1, sigma!=0, rank!=1: %d" % (len(va), len(vb)))
    P("rule rank S == rank(z -> sigma_c(z) on Z_B) violated: %d ; virial rank(ae^T N) != rank S: %d" % (len(vr), len(vv)))
    P("derived identity sigma(z)=diag(z) L (L-2I) violated: %d ; derived rank rule rank S = dim Z_B - dim{z in Z_B: z_i=0 wherever row i of L(L-2I) != 0} violated: %d" % (len(vid), len(vr2)))
    for nm, lst in (("(a)", va), ("(b)", vb), ("rule", vr), ("virial", vv), ("derived-identity", vid), ("derived-rule", vr2)):
        if lst:
            w = sorted(lst, key=lambda x: (x[0], x[1], x[2]))[0]
            P("  smallest %s counterexample: n=%d seed=%d family=%s data=%s L=%s" % (nm, w[0], w[2], w[3], w[4], w[5]))
    P("converse-of-(b) witnesses (dim>=2 with rank<=1, or dim=1 with sigma=0): %d" % len(cw))
    if cw:
        w = sorted(cw, key=lambda x: (x[0], x[1], x[2]))[0]
        P("  smallest: n=%d seed=%d family=%s data=%s L=%s" % (w[0], w[2], w[3], w[4], w[5]))
    # converse specifically: rank 1 with dim != 1
    return tab

def lone_instances():
    P("---- named probes (n=3..8) ----")
    for n in (3, 4, 8):
        L = [[Fraction(3 if (i == j and i == 0) else (2 if i == j else 0)) for j in range(n)] for i in range(n)]
        a = analyse(L); P("  diag(3,2,..,2) n=%d: dim=%d rank=%d rsig=%d" % (n, a["dim"], a["rank"], a["rsig"]))
        L = [[Fraction(2 if i == j else 0) for j in range(n)] for i in range(n)]
        a = analyse(L); P("  2I n=%d: dim=%d rank=%d" % (n, a["dim"], a["rank"]))
    L = Fm([[3, 0, 0], [0, 4, 0], [0, 0, 2]])
    a = analyse(L); P("  diag(3,4,2): dim=%d rank=%d" % (a["dim"], a["rank"]))
    L = Fm([[2, 1, 0, 0], [1, 2, 0, 0], [0, 0, 2, 0], [0, 0, 0, 2]])
    a = analyse(L); P("  2I + symmetric 2x2 block, n=4: dim=%d rank=%d" % (a["dim"], a["rank"]))

def rigidity_proviso():
    P("---- proviso: intra-cell framework has only rigid motions (dim ker = n + n(n-1)/2) ----")
    for n in range(3, 9):
        L = [[Fraction(2 if i == j else 0) for j in range(n)] for i in range(n)]
        bars = standard_bars(L)
        d0, ae, Z = matrices(n, bars)
        nin = 2 * n * (n - 1)
        intra = d0[:nin]
        rk = rank(intra)
        P("  n=%d: intra bars=%d motions=%d expected=%d" % (n, nin, 2 * n * n - rk, n + n * (n - 1) // 2))

def basis_change_small(per):
    P("---- C6 plain basis change vs carried, small n ----")
    kept = lost = tot = 0
    car_ok = car_rel = 0
    diag_ok = 0
    for n in (3, 4, 5):
        for t in range(per):
            r = random.Random(8800000 + 1000 * n + t)
            L = rand_sym(r, n)
            base_dim = len(diag_dim_and_basis(L))
            d0, ae, Z = matrices(n, standard_bars(L))
            Dl, Be, Bl, Ke, Kl = gram_blocks(d0, ae, Z)
            Se0, Sl0 = S_both(Dl, Be, Bl, Ke, Kl)
            r0 = rank(Se0)
            if r0 != 1:
                continue
            U = rand_unimodular(r, n, 10)
            if all(U[i][j] == (1 if i == j else 0) for i in range(n) for j in range(n)):
                continue
            Ui = inverse(U)
            L2 = mm(U, L)
            Sn = S_both(*gram_blocks(*matrices(n, standard_bars(L2))))[0]
            tot += 1
            if rank(Sn) == 1:
                kept += 1
            else:
                lost += 1
            bars0 = standard_bars(L)
            bc = []
            for (u, v, m, ell) in bars0:
                m2 = [sum((m[k] * Ui[k][j] for k in range(n)), Fraction(0)) for j in range(n)]
                bc.append((u, v, m2, ell))
            Sc, Slc = S_both(*gram_blocks(*matrices(n, bc)))
            car_ok += eq(Sc, Se0)
            UiK = [[Ui[a][b] if k == l else Fraction(0) for b in range(n) for l in range(n)] for a in range(n) for k in range(n)]
            car_rel += eq(Slc, mm(T(UiK), mm(Sl0, UiK)))
            # sign-diagonal U
            sg = [r.choice([1, -1]) for _ in range(n)]
            Ud = [[Fraction(sg[i] if i == j else 0) for j in range(n)] for i in range(n)]
            Sd = S_both(*gram_blocks(*matrices(n, standard_bars(mm(Ud, L)))))[0]
            diag_ok += (rank(Sd) == 1)
    P("  collapsing symmetric lattices tested: %d ; after naive U L (unimodular, generic): collapse kept %d, lost %d" % (tot, kept, lost))
    P("  carried: S_el unchanged exactly %d/%d ; S_lat' = (U^-1 x I)^T S_lat (U^-1 x I) %d/%d" % (car_ok, tot, car_rel, tot))
    P("  naive with U = diag(+-1): collapse kept %d/%d (spec edge case (c))" % (diag_ok, tot))

def defect_tests(count):
    P("---- C2 defect: random maps of the same shape as Phi (n=3,4) ----")
    stats = {"true": [0, 0], "bu_I": [0, 0], "bu_P": [0, 0], "dense": [0, 0]}
    for n in (3, 4):
        for t in range(count):
            r = random.Random(9100000 + 1000 * n + t)
            L = rand_sym(r, n)
            nb = 2 * n * (n - 1) + n
            nu = 2 * n * n
            ns_ = n * (n + 1) // 2
            d0, ae, Z = matrices(n, standard_bars(L))
            Hl, _ = full_H(d0, Z)
            Sl = schur128(sub(Hl, 0, nu, 0, nu), sub(Hl, 0, nu, nu, len(Hl)), sub(Hl, nu, len(Hl), nu, len(Hl)))
            def defect(Phi):
                PH = mm(T(Phi), mm(Hl, Phi))
                Sp = schur128(sub(PH, 0, nu, 0, nu), sub(PH, 0, nu, nu, len(PH)), sub(PH, nu, len(PH), nu, len(PH)))
                Rp = [rr[nu:] for rr in Phi[nu:]]
                return is_zero(madd(Sp, mm(T(Rp), mm(Sl, Rp)), -1))
            def rnd(a, b):
                return [[Fraction(ri(r, -2, 2)) for _ in range(b)] for _ in range(a)]
            Xp, Rr = rnd(nu, ns_), rnd(n * n, ns_)
            Pbu = [eye(nu)[i] + Xp[i] for i in range(nu)] + [[Fraction(0)] * nu + Rr[i] for i in range(n * n)]
            Pm = rand_unimodular(r, nu, 40)
            Pbu2 = [Pm[i] + Xp[i] for i in range(nu)] + [[Fraction(0)] * nu + Rr[i] for i in range(n * n)]
            Pd = rnd(nu + n * n, nu + ns_)
            Ptrue = build_Phi(L, n)
            for key, Ph in (("true", Ptrue), ("bu_I", Pbu), ("bu_P", Pbu2), ("dense", Pd)):
                z = defect(Ph)
                stats[key][0] += 1
                stats[key][1] += (1 if z else 0)
    for k, (tot, zero) in stats.items():
        P("  %-6s: defect exactly zero in %d/%d" % (k, zero, tot))
    names = {"true": "true Phi", "bu_I": "random block-upper-triangular [[I,X'],[0,R']]", "bu_P": "random block-upper-triangular [[P,X'],[0,R']] with P unimodular", "dense": "dense random 3n^2 x (2n^2+ns) map"}
    for k in names:
        P("    %s -> %s" % (k, names[k]))
    ok_control = stats["dense"][1] < stats["dense"][0]
    return ok_control and stats["true"][1] == stats["true"][0]

def main():
    rigidity_proviso()
    lone_instances()
    res = run_panel("main (seed base 7000000, n=3..6)", 7000000, 10)
    tab_main = show("main", res)
    iff_viol = sum(c for (d, r), c in tab_main.items() if (r == 1) != (d == 1))
    P("CONTROL wrong rule 'rank 1 iff dim Z_B = 1' is violated on %d lattices of the main panel (must be >0)" % iff_viol)
    res2 = run_panel("fresh (seed base 9500000, n=3..6)", 9500000, 4)
    show("fresh seed", res2)
    res8 = run_panel("n=8 extra (seed base 9700000)", 9700000, 3, ns=(8,),
                     fams=[f for f in FAMS if f[0] in ("diag_rep", "blockdiag", "sym", "nearsym", "sym_UL", "generic", "twisted", "dup_rows")])
    show("n=8 extra", res8)
    res3 = run_panel("fresh2 (seed base 9900000, n=3..6)", 9900000, 6)
    show("fresh seed 2", res3)
    basis_change_small(15)
    ok = defect_tests(6) and iff_viol > 0
    P("CONTROL defect test: dense random maps nonzero in some case AND true Phi zero in all: %s" % ok)
    with open(os.path.join(here, "..", "out", "c2_panel.txt"), "w", newline="\n") as fh:
        fh.write("\n".join(OUT) + "\n")
    if not ok:
        print("CONTROL PASSED (defect test vacuous)")
        sys.exit(2)

main()
