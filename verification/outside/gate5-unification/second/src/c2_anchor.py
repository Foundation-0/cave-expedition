import os, sys, time, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from lat import *

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

up = os.path.join(here, "..", "..", "lattice", "upstream", "pr107", "results", "expedition-fold-sheaf-collapse", "fold_sheaf_collapse.py")
spec = importlib.util.spec_from_file_location("fsc_upstream", up)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def mine(C, a, t):
    n = len(C)
    L = [[(2 + a if i == j else 0) + t * C[i][j] for j in range(n)] for i in range(n)]
    L = [[Fraction(x) for x in r] for r in L]
    d0, ae, Z = matrices(n, standard_bars(L))
    Delta, Bel, Blat, Kel, Klat = gram_blocks(d0, ae, Z)
    Se = schur128(Delta, Bel, Kel)
    rk = rank(d0)
    return L, Se, rk, len(d0)

def main():
    n = 8
    C8 = [[0] * n for _ in range(n)]
    C8[0][1] = C8[0][7] = -1
    C8[1][0] = 1; C8[1][2] = -1
    for k in range(2, 7):
        C8[k][k - 1] = C8[k][k + 1] = -1
    C8[7][0] = 1; C8[7][6] = -1
    Hm = [[(-1) ** bin(i & j).count("1") for j in range(8)] for i in range(8)]
    Hh = [[Fraction(Hm[i][j], 2) for j in range(8)] for i in range(8)]
    up_C8 = mod.make_twisted_cycle_Cn(8)
    P("upstream make_twisted_cycle_Cn(8) == my C_8 from SPEC: %s" % (up_C8 == C8))
    cases = [
        ("C_8 (a,t)=(0,1)", C8, Fraction(0), Fraction(1), dict(S00="1/8", tr="23/4")),
        ("C_8 (a,t)=(4/3,1/3)", C8, Fraction(4, 3), Fraction(1, 3), dict(S00="2527/2976", tr="17297/1488")),
        ("C_8 (a,t)=(8/9,7/9)", C8, Fraction(8, 9), Fraction(7, 9), dict(S00="1925/28296", tr="2149217/155628")),
        ("H/2 as C_mat (a,t)=(0,1)", Hh, Fraction(0), Fraction(1), dict(S00="27/92", tr="114/23")),
    ]
    allok = True
    for name, C, a, t, exp in cases:
        t0 = time.time()
        up_r = mod.compute_fold_sheaf_elastic(C, a, t)
        L, Se, rk, nb = mine(C, a, t)
        ns = len(Se)
        tr = sum((Se[i][i] for i in range(ns)), Fraction(0))
        p = next(i for i in range(ns) if Se[i][i])
        mode = [str(Se[p][j] / Se[p][p]) for j in range(ns)]
        ok = (str(Se[0][0]) == up_r["S_00"] and str(tr) == up_r["tr_S_cell"]
              and 2 * n * n - rk == up_r["H0"] and nb - rk == up_r["H1"]
              and mode == up_r["rank1_mode_normalized"]
              and up_r["S_cell_inertia"] == [1, 0, 35] and rank(Se) == 1
              and str(Se[0][0]) == exp["S00"] and str(tr) == exp["tr"])
        allok = allok and ok
        P("%s: mine S_00=%s tr=%s H0=%d H1=%d rank=%d | upstream S_00=%s tr=%s H0=%d H1=%d inertia=%s | spec S_00=%s tr=%s | mode row equal=%s | ALL MATCH: %s "
          % (name, Se[0][0], tr, 2 * n * n - rk, nb - rk, rank(Se), up_r["S_00"], up_r["tr_S_cell"], up_r["H0"], up_r["H1"], up_r["S_cell_inertia"], exp["S00"], exp["tr"], mode == up_r["rank1_mode_normalized"], ok))
    for name, C in (("C_8", C8), ("H/2", Hh)):
        try:
            ur = mod.rotational_locking_rank(C)
        except Exception as e:
            ur = "error:" + type(e).__name__
        L = [[Fraction((2 if i == j else 0) + C[i][j]) for j in range(8)] for i in range(8)]
        P("rotational_locking_rank(%s) upstream=%s ; mine n - dim Z_B = %d" % (name, ur, 8 - len(diag_dim_and_basis(L))))
    # negative control: upstream function must reject a^2+2t^2 != 2
    try:
        mod.compute_fold_sheaf_elastic(C8, Fraction(1), Fraction(1))
        rej = False
    except ValueError:
        rej = True
    P("CONTROL upstream rejects a^2+2t^2 != 2: %s" % rej)
    # negative control on my side: wrong expected value must not match
    L, Se, rk, nb = mine(C8, Fraction(0), Fraction(1))
    wrong_match = (str(Se[0][0]) == "1/7")
    P("CONTROL wrong expected S_00 (1/7) must not match: %s" % (not wrong_match))
    P("pr106 build_sylvester_H8 == my Sylvester H: skipped importing pr106 (its main writes a certificate; functions not needed for S values)")
    with open(os.path.join(here, "..", "out", "c2_anchor.txt"), "w", newline="\n") as fh:
        fh.write("\n".join(OUT) + "\n")
    if wrong_match or not rej:
        print("CONTROL PASSED")
        sys.exit(2)
    if not allok:
        print("ANCHOR MISMATCH")

main()
