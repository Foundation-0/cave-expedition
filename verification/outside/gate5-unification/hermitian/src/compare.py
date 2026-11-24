"""Tasks 3a-3e and must-fail controls. Usage: python3 -I -B compare.py <objects_dir>
Prints a deterministic report; exits non-zero if any internal check fails or any must-fail control passes."""
from __future__ import annotations

import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from suite import *  # noqa: E402

FAILS = []


def note_fail(msg):
    FAILS.append(msg)
    print("FAIL:", msg)


def out(*a):
    print(*a)


# ---------------------------------------------------------------- carriers
def carriers():
    L, Gv, Sp, rej = all_objects()
    C = {"S_G": [], "S_B": [], "S_M": [], "L_A": [], "L_full": [], "G_H2": []}
    for rep, (M, G, Bm, R, RB, u, t, S, b, Ro) in Sp:
        C["S_G"].append((rep["label"], G, [1], [0]))
        C["S_B"].append((rep["label"], Bm, [0, 1], [2]))
        C["S_M"].append((rep["label"], M, list(range(b)), list(range(b, len(M)))))
    for rep, (Lm, pi, pw, R, order) in L:
        ix, xy = order.index("IX"), order.index("XY")
        A = [[Lm[ix][ix], Lm[ix][xy]], [Lm[xy][ix], Lm[xy][xy]]]
        C["L_A"].append((rep["label"], A, [1], [0]))
        C["L_full"].append((rep["label"], Lm, pw, pi))
    for rep, (Hm, pv, rs, R) in Gv:
        C["G_H2"].append((rep["label"], Hm, pv, rs))
    return C, (L, Gv, Sp, rej)


# ---------------------------------------------------------------- properties
def pivot_sign_of(App):
    pin = inertia_congruence(symm_part(App) if is_real_entries(App) else App)
    k = len(App)
    return 1 if pin[0] == k else (-1 if pin[1] == k else 0), pin


def coupling_class(X, piv, rest):
    Xpr = sub(X, piv, rest)
    Xrp = sub(X, rest, piv)
    T = tr(Xrp) if is_real_entries(Xrp) else dag(Xrp)
    if Xpr == T:
        return "sym"
    if is_real_entries(Xpr) and Xpr == mscale(Fraction(-1), tr(Xrp)):
        return "anti"
    return "other"


def offdiag_zero(A):
    return all(iz(A[i][j]) for i in range(len(A)) for j in range(len(A)) if i != j)


def props(X, piv, rest):
    App = sub(X, piv, piv)
    P = {}
    P["pivot_invertible"] = det(App) != 0
    if not P["pivot_invertible"]:
        for k in ("pivot_definite", "pivot_positive_definite", "pivot_negative_definite", "pivot_sign_normalised_full_semidefinite", "coupling_reciprocal_sym", "coupling_antisym",
                  "pivot_diagonal", "reduced_diagonal", "schur_lowers_diag_in_pivot_sign", "pivot_pd_and_schur_negative", "coupling_rank_le_1", "haynsworth_applies",
                  "reduced_sign_matches_pivot_sign"):
            P[k] = False
        P["full_singular"] = det(X) == 0
        return P
    s, pin = pivot_sign_of(App)
    P["pivot_definite"] = s != 0
    P["pivot_positive_definite"] = s > 0
    P["pivot_negative_definite"] = s < 0
    R = schur(X, piv, rest)
    Sx = symm_part(X)
    P["full_singular"] = det(X) == 0
    if s != 0:
        pf = inertia_congruence(Sx)
        P["pivot_sign_normalised_full_semidefinite"] = (pf[1] == 0) if s > 0 else (pf[0] == 0)
        P["schur_lowers_diag_in_pivot_sign"] = all(s * R[i][i] <= s * X[rest[i]][rest[i]] for i in range(len(rest)))
        Rs = symm_part(R)
        pr = inertia_congruence(Rs)
        P["reduced_sign_matches_pivot_sign"] = (pr[1] == 0) if s > 0 else (pr[0] == 0)
    else:
        P["pivot_sign_normalised_full_semidefinite"] = False
        P["schur_lowers_diag_in_pivot_sign"] = False
        P["reduced_sign_matches_pivot_sign"] = False
    cc = coupling_class(X, piv, rest)
    P["pivot_pd_and_schur_negative"] = (s > 0) and (inertia_congruence(symm_part(R))[1] == len(rest))
    P["coupling_reciprocal_sym"] = cc == "sym"
    P["coupling_antisym"] = cc == "anti"
    P["pivot_diagonal"] = offdiag_zero(App)
    P["reduced_diagonal"] = offdiag_zero(R)
    P["coupling_rank_le_1"] = rank(sub(X, piv, rest)) <= 1
    P["haynsworth_applies"] = is_hermitian(X) and (inertia_congruence(X) == tuple(a + b for a, b in zip(inertia_congruence(App), inertia_congruence(R))))
    return P


PROP_NAMES = ["pivot_invertible", "pivot_definite", "pivot_positive_definite", "pivot_negative_definite", "pivot_sign_normalised_full_semidefinite", "reduced_sign_matches_pivot_sign",
              "schur_lowers_diag_in_pivot_sign", "pivot_pd_and_schur_negative", "coupling_reciprocal_sym", "coupling_antisym", "pivot_diagonal", "reduced_diagonal",
              "coupling_rank_le_1", "full_singular", "haynsworth_applies"]


def rates(plist):
    n = len(plist)
    return {k: (sum(1 for p in plist if p[k]), n) for k in PROP_NAMES}


# ---------------------------------------------------------------- equivalence (Landherr over Q(i), partition respecting)
def landherr_invariants(X, piv, rest):
    App = sub(X, piv, piv)
    R = schur(X, piv, rest)
    inv_p = inertia_congruence(App)
    inv_r = inertia_congruence(R)
    dp, dr = realpart(det(App)), realpart(det(R))
    return {"n": len(X), "shape": (len(piv), len(rest)), "pin": inv_p, "rin": inv_r,
            "pcls": norm_class(dp) if dp != 0 else None, "rcls": norm_class(dr) if dr != 0 else None,
            "pcls_sq": sqfree_class(dp) if dp != 0 else None, "rcls_sq": sqfree_class(dr) if dr != 0 else None}


def equiv(A, B):
    """A, B = (X, piv, rest). Returns (equivalent, first_failing_condition)."""
    XA, pa, ra = A
    XB, pb, rb = B
    if len(XA) != len(XB):
        return False, "1_size"
    ka, kb = kind_of(XA), kind_of(XB)
    sa = ka in ("symmetric", "hermitian")
    sb = kb in ("symmetric", "hermitian")
    if not (sa and sb):
        if sa != sb or ka != kb:
            return False, "2_symmetry_type"
        return False, "2_symmetry_type_nonhermitian_both_not_decidable_here"
    if (len(pa), len(ra)) != (len(pb), len(rb)):
        return False, "3_partition_shape"
    ia, ib = landherr_invariants(*A), landherr_invariants(*B)
    for key, name in (("pin", "4_pivot_inertia"), ("rin", "5_reduced_inertia"), ("pcls", "6_pivot_det_class"), ("rcls", "7_reduced_det_class")):
        if ia[key] != ib[key]:
            return False, name
    return True, "equivalent_over_Q(i)"


def equiv_up_to_unit(A, B):
    """exists rational c>0 with c*A partition-equivalent to B ?  conditions 1-5 are unit-blind; 6-7 are solved for c."""
    ok, why = equiv(A, B)
    if ok or why[0] in "123":
        return ok, why
    ia, ib = landherr_invariants(*A), landherr_invariants(*B)
    if ia["pin"] != ib["pin"]:
        return False, "4_pivot_inertia"
    if ia["rin"] != ib["rin"]:
        return False, "5_reduced_inertia"
    XA, pa, ra = A
    XB, pb, rb = B
    k, m = len(pa), len(ra)
    dpa, dra = realpart(det(sub(XA, pa, pa))), realpart(det(schur(XA, pa, ra)))
    dpb, drb = realpart(det(sub(XB, pb, pb))), realpart(det(schur(XB, pb, rb)))
    if k % 2:
        c = dpb / dpa
    elif m % 2:
        c = drb / dra
    else:
        c = Fraction(1)
    if c <= 0:
        return False, "6_pivot_det_class_sign"
    if norm_class(c ** k * dpa) != norm_class(dpb):
        return False, "6_pivot_det_class"
    if norm_class(c ** m * dra) != norm_class(drb):
        return False, "7_reduced_det_class"
    return True, "equivalent_over_Q(i)_after_unit_rescale"


# ---------------------------------------------------------------- exact rational function fitting
def nullspace(rows, ncols):
    M = [list(r) for r in rows]
    piv_cols = []
    r = 0
    for c in range(ncols):
        p = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        piv_cols.append(c)
        r += 1
    free = [c for c in range(ncols) if c not in piv_cols]
    basis = []
    for fc in free:
        v = [Fraction(0)] * ncols
        v[fc] = Fraction(1)
        for i, pc in enumerate(piv_cols):
            v[pc] = -M[i][fc]
        basis.append(v)
    return basis


def min_rational_degree(samples, maxdeg=4):
    """smallest (dn, dd) (by dn+dd) such that f(s) = N(s)/D(s) fits every sample exactly; None if not found."""
    best = None
    for tot in range(0, 2 * maxdeg + 1):
        for dd in range(0, tot + 1):
            dn = tot - dd
            if dn > maxdeg or dd > maxdeg:
                continue
            rows = []
            for s, f in samples:
                rows.append([s ** i for i in range(dn + 1)] + [-f * s ** j for j in range(dd + 1)])
            ns = nullspace(rows, dn + dd + 2)
            for v in ns:
                if any(x != 0 for x in v[dn + 1:]):
                    return (dn, dd)
    return best


# ---------------------------------------------------------------- random systems for the matched null
def rand_mat_sym(n, rng, lo=-6, hi=6):
    A = zeros(n, n)
    for i in range(n):
        for j in range(i, n):
            A[i][j] = A[j][i] = Fraction(rng.randint(lo, hi))
    return A


def rand_mat_gen(n, rng, lo=-3, hi=3):
    return [[Fraction(rng.randint(lo, hi)) for _ in range(n)] for _ in range(n)]


LABELS_NONID = [l for l in ALL_LABELS if l != "II"]


def rand_gksl(rng):
    hterms = [(rng.randint(-3, 3), LABELS_NONID[rng.randint(0, 14)]) for _ in range(2)]
    j1 = LABELS_NONID[rng.randint(0, 14)]
    j2 = LABELS_NONID[rng.randint(0, 14)]
    Lm, order, pi, pw = gksl_matrix(hterms, [(rng.randint(1, 6), j1), (rng.randint(1, 3), j2)], j1)
    return Lm, pw, pi


def null_systems(kind, n, rng):
    out_ = []
    for _ in range(n):
        if kind == "sym2":
            out_.append((rand_mat_sym(2, rng), [1], [0]))
        elif kind == "gen2":
            out_.append((rand_mat_gen(2, rng, -6, 6), [1], [0]))
        elif kind == "sym3":
            out_.append((rand_mat_sym(3, rng), [0, 1], [2]))
        elif kind == "gen16":
            out_.append((rand_mat_gen(16, rng), list(range(8, 16)), list(range(8))))
        elif kind == "gksl16":
            out_.append(rand_gksl(rng))
    return out_


# ---------------------------------------------------------------- main
def main():
    C, (L, Gv, Sp, rej) = carriers()
    out("== objects: L points=%d G points=%d S points=%d (S candidate draws rejected outside regime 1: %d)" % (len(L), len(Gv), len(Sp), rej))

    # ---- 3a invariants table
    out("\n== 3a  invariants (inertia is (pos,neg,zero); classes are (sign, squarefree part) mod squares and (sign, primes 3 mod 4) mod norms of Q(i))")

    def tally(vals):
        d = {}
        for v in vals:
            k = repr(v)
            d[k] = d.get(k, 0) + 1
        return "; ".join("%s x%d" % (k, d[k]) for k in sorted(d))

    out("S  full G (2x2, pivot b | reduced S-t^2/b): kind", tally([r["G"]["full_inv"]["kind"] for r, _ in Sp]),
        "| rank", tally([r["G"]["full_inv"]["rank"] for r, _ in Sp]),
        "| inertia", tally([r["G"]["full_inv"]["inertia"] for r, _ in Sp]))
    out("S  pivot b inertia", tally([r["G"]["pivot_inertia_of_symmetric_part"] for r, _ in Sp]), "| reduced inertia", tally([r["G"]["reduced_inv"]["inertia"] for r, _ in Sp]))
    out("S  det G class mod squares", tally([r["G"]["full_inv"]["det_class"]["sq"] for r, _ in Sp]))
    out("S  det G class mod norms  ", tally([r["G"]["full_inv"]["det_class"]["norm"] for r, _ in Sp]))
    out("S  reduced class (S - t^2/b) mod squares", tally([classes(Fraction(r["G"]["reduced"][0][0]))["sq"] for r, _ in Sp]), "| mod norms", tally([classes(Fraction(r["G"]["reduced"][0][0]))["norm"] for r, _ in Sp]))
    out("S  bordered lift B (3x3, pivot G | corner): kind", tally([r["B"]["full_inv"]["kind"] for r, _ in Sp]), "| inertia", tally([r["B"]["full_inv"]["inertia"] for r, _ in Sp]),
        "| pivot inertia", tally([r["B"]["pivot_inertia_of_symmetric_part"] for r, _ in Sp]), "| reduced inertia", tally([r["B"]["reduced_inv"]["inertia"] for r, _ in Sp]))
    out("S  Hermitian carrier M (n x n over Q(i)): n", tally([r["n"] for r, _ in Sp]), "| kind", tally([r["M_kind"] for r, _ in Sp]),
        "| rank", tally([r["M_inv"]["rank"] for r, _ in Sp]), "| inertia", tally([r["M_inv"]["inertia"] for r, _ in Sp]))
    out("S  chain rank P >= rank P_perp >= n+(H_perp) >= R_opt holds:", tally([r["chain"]["ok"] for r, _ in Sp]),
        "| R_opt == u^2 (G^{-1})_11:", tally([r["Ropt_equals_u2_G11inv"] for r, _ in Sp]), "| R_opt == -Schur(B):", tally([r["Ropt_equals_minus_B_schur"] for r, _ in Sp]))
    out("L  full (16x16, pivot witness 8x8 | reduced invariant 8x8): kind", tally([r["full_inv"]["kind"] for r, _ in L]),
        "| rank", tally([r["full_inv"]["rank"] for r, _ in L]), "| det", tally([r["full_inv"]["det"] for r, _ in L]),
        "| inertia of symmetric part", tally([r["full_inv"]["inertia_of_symmetric_part"] for r, _ in L]))
    out("L  pivot kind", tally([r["pivot_kind"] for r, _ in L]), "| pivot inertia of symmetric part", tally([r["pivot_inertia_of_symmetric_part"] for r, _ in L]),
        "| reduced kind", tally([r["reduced_inv"]["kind"] for r, _ in L]), "| reduced rank", tally([r["reduced_inv"]["rank"] for r, _ in L]),
        "| reduced inertia (if symmetric)", tally([r["reduced_inv"]["inertia"] for r, _ in L]))
    out("L  pivot det class mod squares (anchor/omega=0 points)", tally([classes(realpart(Fraction(r["pivot_det"])))["sq"] for r, _ in L if r["params"]["omega"] == "0"][:12]))
    out("L  pseudo-determinant of the reduced 8x8 (product of nonzero diagonal entries) class mod squares / norms, omega=0 points:",
        tally([(lambda d: (classes(d)["sq"], classes(d)["norm"]))(__import__("functools").reduce(lambda a, b: a * b, [Fraction(r["reduced"][i][i]) for i in range(8) if Fraction(r["reduced"][i][i]) != 0], Fraction(1))) for r, _ in L if r["params"]["omega"] == "0"][:6]))
    out("G  full H2 (3x3, pivot (chi,p) | reduced P): kind", tally([r["full_inv"]["kind"] for r, _ in Gv]), "| rank", tally([r["full_inv"]["rank"] for r, _ in Gv]),
        "| inertia", tally([r["full_inv"]["inertia"] for r, _ in Gv]))
    out("G  pivot inertia", tally([r["pivot_inertia_of_symmetric_part"] for r, _ in Gv]), "| reduced S_P inertia", tally([r["reduced_inv"]["inertia"] for r, _ in Gv]))
    out("G  reduced S_P class mod squares", tally([classes(Fraction(r["reduced"][0][0]))["sq"] if Fraction(r["reduced"][0][0]) != 0 else None for r, _ in Gv]), "| mod norms", tally([classes(Fraction(r["reduced"][0][0]))["norm"] if Fraction(r["reduced"][0][0]) != 0 else None for r, _ in Gv]))
    out("G  det H2 class mod squares", tally([r["full_inv"]["det_class"]["sq"] if r["full_inv"]["det_class"] else None for r, _ in Gv]))
    out("G  S_P == -G_AA/(4 r) exactly:", tally([r["S_P_equals_minus_GAA_over_4r"] for r, _ in Gv]),
        "| sign(G_AA) vs inertia: (G_AA<0 <-> (3,0,0)), (=0 <-> (2,0,1)), (>0 <-> (2,1,0)):",
        tally([(("neg" if Fraction(r["G_AA"]) < 0 else ("zero" if Fraction(r["G_AA"]) == 0 else "pos")), tuple(r["full_inv"]["inertia"])) for r, _ in Gv]))
    for r, _ in Gv:
        ga = Fraction(r["G_AA"])
        want = (3, 0, 0) if ga < 0 else ((2, 0, 1) if ga == 0 else (2, 1, 0))
        if tuple(r["full_inv"]["inertia"]) != want:
            note_fail("gravity inertia/G_AA sign correlation broken at " + r["label"])
    for r, _ in L:
        if r["params"]["omega"] == "0":
            if Fraction(r["reduced_IX_entry"]) != -Fraction(r["Gamma_eff_formula"]):
                note_fail("Gamma_eff mismatch at " + r["label"])

    # ---- 3b function family
    out("\n== 3b  function family")
    # shared scalar form x - sigma*y^2/z, read off the entries
    sig = {}
    for (lab, X, pv, rs) in C["S_G"]:
        x, y, z = X[0][0], X[0][1], X[1][1]
        red = schur(X, pv, rs)[0][0]
        if red != x - y * y / z or X[1][0] != y:
            note_fail("S_G scalar form")
    sig["S"] = tally(["+" if (X[0][1] * X[1][0]) > 0 else "-" for (_, X, _, _) in C["S_G"]])
    for (lab, X, pv, rs) in C["L_A"]:
        x, c12, c21, z = X[0][0], X[0][1], X[1][0], X[1][1]
        red = schur(X, pv, rs)[0][0]
        if red != x - c12 * c21 / z:
            note_fail("L_A scalar form")
    sig["L"] = tally(["+" if (X[0][1] * X[1][0]) > 0 else "-" for (_, X, _, _) in C["L_A"]])
    # gravity: two nested eliminations
    gnest = []
    for (lab, X, pv, rs) in C["G_H2"]:
        m00 = X[0][0]
        S1 = [[X[i][j] - X[i][0] * X[0][j] / m00 for j in (1, 2)] for i in (1, 2)]
        red = S1[1][1] - S1[0][1] * S1[1][0] / S1[0][0]
        gnest.append(red == schur(X, pv, rs)[0][0])
    sig["G_nested_two_step_equals_one_step"] = tally(gnest)
    out("sign of the coupling cycle product x_12*x_21 of the pivot/rest pair: S", sig["S"], "| L (minimal 2x2 carrier of Gamma_eff)", sig["L"],
        "| G: coupling is symmetric by construction; the 2x2 pivot is eliminated in two nested steps:", sig["G_nested_two_step_equals_one_step"])
    # Gamma_eff identity with coupling
    for (lab, X, pv, rs), (rep, _) in zip(C["L_A"], L):
        if rep["params"]["omega"] == "0":
            g = Fraction(rep["params"]["g"])
            if X[0][1] * X[1][0] != -4 * g * g:
                note_fail("coupling product != -4 g^2 at " + lab)
    out("L  coupling product is exactly -4 g^2 at every omega=0 point (checked); S coupling product is t^2 >= 0")
    # one-parameter slices, exact minimal degree (dn, dd)
    sl = {}
    ss = []
    for S_ in (Fraction(7), Fraction(9), Fraction(11), Fraction(13), Fraction(17), Fraction(23), Fraction(29), Fraction(31), Fraction(37)):
        Gm = G2(S_, 3, 2)
        ss.append((S_, 5 * 5 * inv(Gm)[0][0]))
    sl["S: R_opt(S) = u^2 (G^-1)_11, u=5,t=3,b=2"] = min_rational_degree(ss)
    tt = []
    for t_ in (Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5), Fraction(6), Fraction(7), Fraction(8), Fraction(9)):
        tt.append((t_, 25 * inv(G2(50, t_, 2))[0][0]))
    sl["S: R_opt(t), u=5,S=50,b=2"] = min_rational_degree(tt)
    ll = []
    for g1_ in (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(1), Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(11)):
        Lm, order, pi, pw = liouvillian(1, g1_, Fraction(3, 2), Fraction(1, 100))
        R = schur(Lm, pw, pi)
        ix = order.index("IX")
        ll.append((g1_, -R[ix][ix]))
    sl["L: Gamma_eff(gamma1), N=1,g=3/2,gt=1/100"] = min_rational_degree(ll)
    lg = []
    for g_ in (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(1), Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(11)):
        Lm, order, pi, pw = liouvillian(2, Fraction(1, 4), g_, Fraction(1, 100))
        R = schur(Lm, pw, pi)
        ix = order.index("IX")
        lg.append((g_, -R[ix][ix]))
    sl["L: Gamma_eff(g), N=2,gamma1=1/4,gt=1/100"] = min_rational_degree(lg)
    gg = []
    for r_ in (Fraction(1), Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(11), Fraction(13), Fraction(17), Fraction(19), Fraction(23)):
        Hm = aest_hessian(1, 1, 4, r_)
        gg.append((r_, schur(Hm, [0, 1], [2])[0][0]))
    sl["G: S_P(r), KB=1,lam=1,Kpp=4"] = min_rational_degree(gg)
    gk = []
    for k_ in (Fraction(1), Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(11), Fraction(13), Fraction(17), Fraction(19), Fraction(23)):
        Hm = aest_hessian(1, 1, k_, 9)
        gk.append((k_, schur(Hm, [0, 1], [2])[0][0]))
    sl["G: S_P(Kpp), KB=1,lam=1,r=9"] = min_rational_degree(gk)
    for k in sorted(sl):
        out("  minimal (deg N, deg D):", sl[k], "<-", k)
    # gravity: structural coincidences among Hessian entries
    ent = [[Fraction(r["full"][i][j]) for (i, j) in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))] + [Fraction(1)] for r, _ in Gv]
    nsp = nullspace(ent, 7)
    out("G  linear relations (with constant) among the 6 Hessian entries across the %d points: %d independent; m01 == m02 at every point: %s" %
        (len(Gv), len(nsp), tally([Fraction(r["full"][0][1]) == Fraction(r["full"][0][2]) for r, _ in Gv])))
    # block determinant formula and reciprocal reading
    dets = []
    for nm in ("S_G", "G_H2", "L_full"):
        for (lab, X, pv, rs) in C[nm]:
            dets.append(det(X) == det(sub(X, pv, pv)) * det(schur(X, pv, rs)))
    out("Schur determinant formula det(X)=det(pivot) det(reduced) at all points of all three domains:", tally(dets), "(identity of block elimination, no domain content)")
    recip = []
    for (lab, X, pv, rs) in C["G_H2"]:
        recip.append(inv(X)[2][2] == 1 / schur(X, pv, rs)[0][0] if det(X) != 0 else None)
    out("G  (H2^-1)_PP == 1/S_P == -4r/G_AA where H2 is invertible:", tally(recip))

    # ---- 3c equivalence
    out("\n== 3c  equivalence verdicts, partition respecting, over Q(i) (Landherr: dimension, signature, determinant mod norms) for symmetric/Hermitian objects")
    names = ["S_G", "S_B", "L_A", "L_full", "G_H2"]
    pair_res = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            cnt = {}
            for (_, XA, pa, ra) in C[a]:
                for (_, XB, pb, rb) in C[b]:
                    ok, why = equiv((XA, pa, ra), (XB, pb, rb))
                    cnt[why] = cnt.get(why, 0) + 1
            pair_res[(a, b)] = cnt
            out("  %-7s vs %-7s : %s" % (a, b, "; ".join("%s x%d" % (k, cnt[k]) for k in sorted(cnt))))
    # same-domain control: instances of one carrier among themselves
    for a in ("S_B", "G_H2"):
        cnt = {}
        for ia_, (_, XA, pa, ra) in enumerate(C[a]):
            for ib_, (_, XB, pb, rb) in enumerate(C[a]):
                if ia_ < ib_:
                    ok, why = equiv((XA, pa, ra), (XB, pb, rb))
                    cnt[why] = cnt.get(why, 0) + 1
        out("  within %-7s (instance pairs): %s" % (a, "; ".join("%s x%d" % (k, cnt[k]) for k in sorted(cnt))))
    # the lift pair, after allowing a unit rescale
    cntu = {}
    for (_, XA, pa, ra) in C["S_B"]:
        for (_, XB, pb, rb) in C["G_H2"]:
            ok, why = equiv_up_to_unit((XA, pa, ra), (XB, pb, rb))
            cntu[why] = cntu.get(why, 0) + 1
    out("  S_B vs G_H2 allowing a rational unit rescale c>0: %s" % "; ".join("%s x%d" % (k, cntu[k]) for k in sorted(cntu)))
    # Liouvillian carrier versus Hermitian gauge: complex-symmetric but not Hermitian
    gauge = []
    for (_, A, pv, rs), (rep, _) in zip(C["L_A"], L):
        T = [[Qi(1), Qi(0)], [Qi(0), Qi(0, 1)]]
        Ac = mm(mm(inv(T), A), T)
        sym_c = Ac[0][1] == Ac[1][0] and Ac[0][1] != 0
        herm_c = is_hermitian(Ac)
        red_c = schur(Ac, pv, rs)[0][0]
        red_o = schur(A, pv, rs)[0][0]
        gauge.append((sym_c, herm_c, red_c == red_o) if rep["params"]["omega"] == "0" else None)
    out("  L_A under the Q(i) gauge diag(1,i): (complex-symmetric, Hermitian, Schur value unchanged) =", tally([g for g in gauge if g is not None]))
    # partition respecting similarity over R on L_A: rho=delta/alpha, need -rho = 1/rho
    out("  L_A real diagonal similarity can never make the coupling symmetric: needs rho^2 = -1; cycle product x12*x21 = -4g^2 < 0 is invariant")
    # similarity class: discriminant of the 2x2 block (EP2 criterion) as the only dynamical invariant
    disc_info = []
    for (lab, A, pv, rs), (rep, _) in zip(C["L_A"], L):
        if rep["params"]["omega"] != "0":
            continue
        trc = A[0][0] + A[1][1]
        dt = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        disc = trc * trc - 4 * dt
        disc_info.append("neg" if disc < 0 else ("zero" if disc == 0 else "pos"))
    out("  L_A discriminant sign (underdamped=neg / EP2=zero / overdamped=pos) over omega=0 points:", tally(disc_info), "; a real symmetric 2x2 always has disc >= 0")

    # ---- Schur value vs exact eigenvalue (sharpness)
    out("\n== sharpness / exactness of the reduced quantity")
    sh = []
    for (lab, A, pv, rs), (rep, _) in zip(C["L_A"], L):
        if rep["params"]["omega"] != "0":
            continue
        red = schur(A, pv, rs)[0][0]
        trc = A[0][0] + A[1][1]
        dt = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        resid = red * red - trc * red + dt   # char poly at the Schur value; zero iff Schur value is an eigenvalue
        sh.append(resid != 0)
    out("L  Schur value is NOT an exact eigenvalue of the 2x2 block (char poly residual != 0) at points:", tally(sh))
    # inertia of the Liouvillian does not see g
    sg = []
    for (lab, Xl, pv, rs), (rep, (Lm, pi, pw, R, order)) in zip(C["L_full"], L):
        Ss = symm_part(Xl)
        Rs_sym = schur(Ss, pv, rs)
        ix = order.index("IX")
        sg.append((Rs_sym[ix][ix] == Fraction(-2) * Fraction(rep["params"]["gamma_tid"]), R[ix][ix] != Rs_sym[ix][ix]))
    out("L  Schur complement of the symmetric part has IX entry -2*gamma_tid (no g), differs from the Schur entry of L itself: (no-g, differs) =", tally(sg))
    # gravity: stationarity is exact
    stat = []
    for (lab, X, pv, rs) in C["G_H2"]:
        A_ = sub(X, pv, pv)
        c_ = sub(X, pv, rs)
        w = mm(inv(A_), c_)
        # minimiser over (chi,p) at P=1 is x = -A^{-1} c P ; energy 1/2 (S_P)
        xs = [[-w[0][0]], [-w[1][0]]]
        e = Fraction(1, 2) * (mm(mm(tr(xs), A_), xs)[0][0] + 2 * mm(tr(xs), c_)[0][0] + X[2][2])
        stat.append(e == Fraction(1, 2) * schur(X, pv, rs)[0][0])
    out("G  min over (chi,p) of H2 at P=1 equals S_P/2 exactly:", tally(stat))
    sp_ = []
    for (rep, (M, G, Bm, R, RB, u, t, S, b, Ro)) in Sp:
        r_min = max(1, -((-Ro.numerator) // Ro.denominator))
        sp_.append((rep["chain"]["rank_P"] >= r_min, rep["chain"]["rank_P"] == r_min))
    out("S  rank P >= max(1, ceil R_opt) and equality (the bound is attained at the point) over instances: (bound held, attained) =", tally(sp_))

    # ---- 3d matched null
    out("\n== 3d  matched null (seeded)")
    real_sets = {"S(G 2x2)": [p for p in C["S_G"]], "G(H2 3x3)": [p for p in C["G_H2"]], "L(16x16)": [p for p in C["L_full"]], "L_A(2x2)": [p for p in C["L_A"]]}
    real_props = {k: [props(X, pv, rs) for (_, X, pv, rs) in v] for k, v in real_sets.items()}
    NN = 240
    nulls = {"sym2": null_systems("sym2", NN, Rng(7001)), "sym3": null_systems("sym3", NN, Rng(7002)), "gen16": null_systems("gen16", NN, Rng(7003)),
             "gksl16": null_systems("gksl16", NN, Rng(7004)), "gen2": null_systems("gen2", NN, Rng(7005))}
    null_props = {k: [props(X, pv, rs) for (X, pv, rs) in v] for k, v in nulls.items()}
    rr = {k: rates(v) for k, v in real_props.items()}
    nr = {k: rates(v) for k, v in null_props.items()}
    hdr = "property".ljust(44) + " | " + " | ".join(k.ljust(9) for k in rr) + " | shared(S,G,L) | " + " | ".join(("null_" + k).ljust(11) for k in nr)
    out(hdr)
    shared = []
    for p in PROP_NAMES:
        cells = []
        for k in rr:
            a, n = rr[k][p]
            cells.append(("%d/%d" % (a, n)).ljust(9))
        sh_ = all(rr[k][p][0] == rr[k][p][1] for k in ("S(G 2x2)", "G(H2 3x3)", "L(16x16)"))
        if sh_:
            shared.append(p)
        ncells = [("%d/%d" % nr[k][p]).ljust(11) for k in nr]
        out(p.ljust(44) + " | " + " | ".join(cells) + " | " + ("YES" if sh_ else "no ").ljust(14) + " | " + " | ".join(ncells))
    out("properties held by every sampled point of all three real sets:", shared)
    # joint rate: random triple (sym2, sym3, gen16 / gksl16) all having every shared property
    for lk in ("gen16", "gksl16"):
        joint = 0
        for i in range(NN):
            if all(null_props["sym2"][i][p] and null_props["sym3"][i][p] and null_props[lk][i][p] for p in shared):
                joint += 1
        out("joint null rate (matched triples sym2, sym3, %s each holding all shared properties): %d/%d" % (lk, joint, NN))
    # the two properties whose sign structure the three real sets are claimed to share
    sn = "pivot_sign_normalised_full_semidefinite"
    out("sign-normalised statement 'pivot definite and the whole symmetric part semidefinite with the pivot sign': S %d/%d, G %d/%d, L %d/%d" % (
        rr["S(G 2x2)"][sn] + rr["G(H2 3x3)"][sn] + rr["L(16x16)"][sn]))
    # equivalence null: B instances against random symmetric 3x3 (2|1), allowing a unit rescale
    eqn = 0
    tot = 0
    nrng = Rng(7010)
    for (_, XB, pb, rb) in C["S_B"]:
        for _ in range(120):
            Xr = rand_mat_sym(3, nrng)
            try:
                ok, why = equiv_up_to_unit((XB, pb, rb), (Xr, [0, 1], [2]))
            except CheckFailure:
                continue
            except ZeroDivisionError:
                continue
            tot += 1
            if ok:
                eqn += 1
    realn = sum(1 for (_, XB, pb, rb) in C["S_B"] for (_, XH, ph, rh) in C["G_H2"] if equiv_up_to_unit((XB, pb, rb), (XH, ph, rh))[0])
    out("equivalence (S_B ~ partition-respecting up to unit rescale) rate: real S_B vs G_H2 %d/%d; S_B vs random symmetric 3x3 (2|1) %d/%d" % (realn, len(C["S_B"]) * len(C["G_H2"]), eqn, tot))
    # keep the coincident pair, show it is not unit-rescale invariant
    for (la, XB, pb, rb) in C["S_B"]:
        for (lb, XH, ph, rh) in C["G_H2"]:
            if equiv_up_to_unit((XB, pb, rb), (XH, ph, rh))[0]:
                outs = []
                for c_ in (Fraction(1), Fraction(3, 7), Fraction(5), Fraction(2)):
                    outs.append("c=%s:%s" % (c_, equiv((mscale(c_, XB), pb, rb), (XH, ph, rh))[1]))
                out("coincident pair (%s, %s), strict verdict under unit rescale of the S_B side: %s" % (la, lb, "; ".join(outs)))
                dra = realpart(det(schur(XB, pb, rb)))
                drb = realpart(det(schur(XH, ph, rh)))
                c_star = drb / dra
                out("  the rescale that works is c* = %s; strict verdict at c*: %s (a unit choice for one pair, not a family-wide map)" % (c_star, equiv((mscale(c_star, XB), pb, rb), (XH, ph, rh))[1]))

    # ---- 3e invariance
    out("\n== 3e  invariance of the conclusions")
    rngT = Rng(9001)

    def rand_T(n_p, n_r, rng):
        n = n_p + n_r
        T = zeros(n, n)
        while True:
            for i in range(n_p):
                for j in range(n_p):
                    T[i][j] = Fraction(rng.randint(-2, 2))
            for i in range(n_r):
                for j in range(n_r):
                    T[n_p + i][n_p + j] = Fraction(rng.randint(-2, 2))
            for i in range(n_p):
                for j in range(n_r):
                    T[i][n_p + j] = Fraction(rng.randint(-2, 2))
            if det(T) != 0:
                return T

    def conclusions(X, piv, rest):
        # reorder so that pivot comes first (indices piv then rest), conclusions are index-order free
        s, pin = pivot_sign_of(sub(X, piv, piv))
        R = schur(X, piv, rest)
        Rs = symm_part(R)
        return {"kind": kind_of(X), "pivot_sign": s, "pivot_inertia": pin, "reduced_inertia_sym_part": inertia_congruence(Rs),
                "antisym_part_zero": is_zero_mat(antisymm_part(X)), "coupling_cycle_sign_1x1": None}

    inv_ok = {"basis_change(congruence, partition respecting)": [0, 0], "unit_rescale(c=3/7 and c=5)": [0, 0]}
    for nm in ("S_G", "G_H2", "L_A", "L_full"):
        for (lab, X, pv, rs) in C[nm]:
            # reorder to (pivot, rest)
            order_idx = list(pv) + list(rs)
            Xo = sub(X, order_idx, order_idx)
            npv, nrs = len(pv), len(rs)
            base = conclusions(Xo, list(range(npv)), list(range(npv, npv + nrs)))
            T = rand_T(npv, nrs, rngT)
            Xt = mm(mm(tr(T), Xo), T)
            ct = conclusions(Xt, list(range(npv)), list(range(npv, npv + nrs)))
            inv_ok["basis_change(congruence, partition respecting)"][1] += 1
            if ct == base:
                inv_ok["basis_change(congruence, partition respecting)"][0] += 1
            else:
                note_fail("basis change altered a conclusion for %s %s" % (nm, lab))
            for c in (Fraction(3, 7), Fraction(5)):
                Xc = mscale(c, Xo)
                cc_ = conclusions(Xc, list(range(npv)), list(range(npv, npv + nrs)))
                inv_ok["unit_rescale(c=3/7 and c=5)"][1] += 1
                if cc_ == base:
                    inv_ok["unit_rescale(c=3/7 and c=5)"][0] += 1
                else:
                    note_fail("unit rescale altered a conclusion for %s %s" % (nm, lab))
    for k in sorted(inv_ok):
        out("  structural conclusions (kind, pivot sign/inertia, reduced inertia, antisymmetric part) unchanged under %s: %d/%d" % (k, inv_ok[k][0], inv_ok[k][1]))
    # first failing condition under basis change and rescale, per pair
    stab = {}
    for (a, b) in (("S_G", "L_A"), ("S_B", "G_H2"), ("S_G", "G_H2"), ("L_A", "G_H2")):
        same = 0
        tot = 0
        for (_, XA, pa, ra) in C[a]:
            for (_, XB, pb, rb) in C[b]:
                v0 = equiv((XA, pa, ra), (XB, pb, rb))[1]
                for c in (Fraction(3, 7), Fraction(5)):
                    v1 = equiv((mscale(c, XA), pa, ra), (XB, pb, rb))[1]
                    tot += 1
                    if v1 == v0:
                        same += 1
        stab[(a, b)] = (same, tot)
    out("  verdict (first failing condition) unchanged when one object is unit-rescaled:", {"%s/%s" % k: "%d/%d" % v for k, v in sorted(stab.items())})
    out("  (a verdict that changes under rescale can only be a determinant-class condition, 6 or 7; structural conditions 1-5 never change)")
    # homogeneity of the three reduced quantities under their own unit changes
    hom = []
    for (rep, (M, G, Bm, R, RB, u, t, S, b, Ro)) in Sp[:6]:
        c = Fraction(3, 2)
        hom.append((c * u) ** 2 / schur(G2(c * c * S, c * t, b), [1], [0])[0][0] == u * u / R[0][0])
    out("  S: R_opt invariant under (u,t,S)->(cu,ct,c^2 S):", tally(hom))
    hom = []
    for (rep, (Lm, pi, pw, R, order)) in [(r, o) for r, o in L if r["params"]["omega"] == "0"][:6]:
        P_ = rep["params"]
        c = Fraction(3, 2)
        Lc, o2, pi2, pw2 = liouvillian(Fraction(P_["N"]), c * Fraction(P_["gamma1"]), c * Fraction(P_["g"]), c * Fraction(P_["gamma_tid"]))
        R2 = schur(Lc, pw2, pi2)
        ix = o2.index("IX")
        hom.append(R2[ix][ix] == c * R[ix][ix])
    out("  L: Gamma_eff scales with c under (gamma1,g,gamma_tid)->c(.) (time unit change), signs and inertia fixed:", tally(hom))
    hom = []
    for (rep, (Hm, pv, rs, R)) in Gv[:8]:
        P_ = rep["params"]
        c = Fraction(3, 2)
        H2c = aest_hessian(Fraction(P_["KB"]), Fraction(P_["lam"]), c * Fraction(P_["Kpp"]), c * Fraction(P_["r_eq_k2"]))
        hom.append((G_AA(Fraction(P_["KB"]), Fraction(P_["lam"]), c * Fraction(P_["Kpp"]), c * Fraction(P_["r_eq_k2"])) == G_AA(Fraction(P_["KB"]), Fraction(P_["lam"]), Fraction(P_["Kpp"]), Fraction(P_["r_eq_k2"])),
                    schur(H2c, [0, 1], [2])[0][0] * c == R[0][0]))
    out("  G: (G_AA invariant, S_P scales as 1/c) under (Kpp,r)->c(Kpp,r):", tally(hom))

    # ---- must-fail controls
    out("\n== must-fail controls")
    ctrl = []

    def control(name, passed_wrongly):
        ctrl.append((name, passed_wrongly))
        out("  control %-62s %s" % (name, "PASSED (BAD)" if passed_wrongly else "rejected (good)"))
        if passed_wrongly:
            note_fail("control passed: " + name)

    try:
        inertia_congruence([[Fraction(0), Fraction(1)], [Fraction(0), Fraction(0)]])
        control("inertia of a non-Hermitian matrix is refused", True)
    except CheckFailure:
        control("inertia of a non-Hermitian matrix is refused", False)
    # wrong formula for R_opt
    bad = 0
    for (rep, (M, G, Bm, R, RB, u, t, S, b, Ro)) in Sp:
        if u * u / (S + t * t / b) == Ro:
            bad += 1
    control("wrong R_opt = u^2/(S + t^2/b) matches no point", bad > 0)
    bad = 0
    for (rep, _) in L:
        if rep["params"]["omega"] == "0" and Fraction(rep["reduced_IX_entry"]) == -(2 * Fraction(rep["params"]["gamma_tid"]) - Fraction(rep["Gamma_eff_formula"]) + 2 * Fraction(rep["params"]["gamma_tid"])):
            bad += 1
    control("sign-flipped Gamma_eff = 2gt - 2g^2/gcm matches no point", bad > 0)
    bad = 0
    for (rep, _) in Gv:
        if Fraction(rep["G_AA"]) != 0 and Fraction(rep["min_H2_coeff_of_D2"]) == Fraction(rep["G_AA"]) / (2 * Fraction(rep["params"]["r_eq_k2"])):
            bad += 1
    control("sign-flipped min H2 = +G_AA D^2/2k^2 matches no point with G_AA != 0", bad > 0)
    # equivalence tester: must say NO for S_G vs L_A, YES for a congruent copy
    okx = equiv((C["S_G"][0][1], [1], [0]), (C["L_A"][0][1], [1], [0]))[0]
    control("equivalence tester accepts S_G ~ L_A", okx)
    X0 = C["S_B"][0][1]
    Tt = rand_T(2, 1, Rng(5))
    Xc = mm(mm(tr(Tt), X0), Tt)
    pos_ctl = equiv((X0, [0, 1], [2]), (Xc, [0, 1], [2]))[0]
    control("positive control: congruent copy of B is NOT recognised as equivalent (tester broken)", not pos_ctl)
    # tampered object file detection
    tam = canon_json({"a": 1}) != canon_json({"a": 2})
    control("canonical JSON hash does not distinguish tampered objects", not tam)
    # properties tester: a random general 16x16 must not be antisymmetric-coupled
    control("random 16x16 is not flagged antisymmetric-coupled in >5% of draws", sum(1 for p in null_props["gen16"] if p["coupling_antisym"]) > NN // 20)
    # objects on disk equal the regenerated canonical documents
    docs = object_documents()
    odir = sys.argv[1]
    for fn in sorted(docs):
        p = os.path.join(odir, fn)
        try:
            with open(p, "r", encoding="utf-8", newline="") as fh:
                disk = fh.read()
        except OSError:
            disk = None
        same = disk == docs[fn]
        out("  object file %s sha256=%s matches regenerated: %s" % (fn, sha(docs[fn]), same))
        if not same:
            note_fail("object file differs from regenerated: " + fn)
    first = sorted(docs)[0]
    control("tampered object text is not detected", sha(docs[first]) == sha(docs[first].replace("0", "1", 1)))

    out("\nRESULT compare: %s controls=%d failures=%d" % ("PASS" if not FAILS else "FAIL", len(ctrl), len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
