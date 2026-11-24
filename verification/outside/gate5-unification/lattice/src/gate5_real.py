"""Gate 5, tasks 3a, 3d, 3e, 3f on the real pairs (all exact).  Deterministic output, exit 1 on any failed
check or any must-fail control that is not detected.   usage: gate5_real.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g5lib import *
from g5more import *

FAIL = []


def check(label, cond):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAIL.append(label)


def control(label, detected):
    print(("CONTROL-DETECTED " if detected else "CONTROL-NOT-DETECTED ") + label)
    if not detected:
        FAIL.append("control " + label)


def disc_info(M, ring_q2=False):
    d = congruence_diagonal(M)
    n = len(M)
    if not d:
        return {"rank": 0, "disc_nondeg_part": None}
    prod = 1
    for x in d:
        prod = prod * x
    if isinstance(prod, Q2):
        return {"rank": len(d), "disc_nondeg_part": enc(prod), "square_in_Q(sqrt2)": q2_is_square(prod)}
    cls = squarefree_class(prod)
    return {"rank": len(d), "disc_nondeg_part": enc(prod), "class_mod_squares": cls}


def invariants(M, label):
    n = len(M)
    out = {"label": label, "size": n, "inertia": inertia(M)}
    out.update(disc_info(M))
    out["det"] = enc(det_small(M))
    try:
        den, Mi = clear_denominators(M)
        out["snf_of_cleared"] = {"scale_den": den, "diag": snf_diag(Mi)}
    except Exception:  # Q(sqrt 2) entries cannot be cleared over Z
        out["snf_of_cleared"] = "n/a (entries in Q(sqrt2))"
    return out


def vec_DB(z, Bm):
    n = len(Bm)
    return [z[i] * Bm[i][j] for i in range(n) for j in range(n)]


def kron_I(U, n):
    """(U kron I_n) acting on dL index k*n + l."""
    N = n * n
    out = [[0] * N for _ in range(N)]
    for k in range(n):
        for j in range(n):
            if U[k][j] != 0:
                for l in range(n):
                    out[k * n + l][j * n + l] = U[k][j]
    return out


def strain_T(g):
    """Coordinate matrix T_g (36 x 36) of eps -> g^T eps g, in coordinates (eps_kk | eps_kl, k<l)."""
    n = len(g)
    pairs = off_pairs(n)
    ne = n + len(pairs)
    T = [[0] * ne for _ in range(ne)]
    gT = transpose(g)
    for c in range(ne):
        E = [[0] * n for _ in range(n)]
        if c < n:
            E[c][c] = 1
        else:
            k, l = pairs[c - n]
            E[k][l] = 1
            E[l][k] = 1
        Mx = matmul(gT, matmul(E, g))
        for k in range(n):
            T[k][c] = Mx[k][k]
        for idx, (k, l) in enumerate(pairs):
            T[n + idx][c] = Mx[k][l]
    return T


def real_pair(name, spec, rep):
    L = spec["L"]
    n = len(L)
    F = Framework(L)
    Hl, He = H_lat_from(F), H_el_from(F)
    Phi = matrix_Phi(L)
    R = matrix_R(L)
    PhiT = transpose(Phi)
    Mp = matmul(PhiT, matmul(Hl, Phi))
    check("%s: H_el = Phi^T H_lat Phi (exact, 164x164)" % name, Mp == He)
    # --- 3a: eliminate then map  vs  map then eliminate
    S_map_then_elim = block_schur(Mp, F.nu)
    S_lat = block_schur(Hl, F.nu)
    pulled = lattice_pullback(S_lat, R)
    defect = madd(S_map_then_elim, pulled, -1)
    S_el, _ = F.schur_direct()
    nz = sum(1 for r in defect for x in r if x != 0)
    check("%s: defect (map-then-eliminate) - (eliminate-then-map) is exactly zero" % name, nz == 0)
    check("%s: Schur(Phi^T H_lat Phi) equals the direct elasticity S = K - B^T Delta^+ B" % name, S_map_then_elim == S_el)
    # --- what depends on the lattice
    Bm = bridge_of(L)
    basis, rkrot = rotational_locking(Bm)
    check("%s: dim ker M_rot (diagonal symmetrizers of L-2I) = 1, rank %d" % (name, rkrot), len(basis) == 1 and rkrot == 7)
    z = basis[0]
    sig = sigma_star(L, Bm, z)
    c_el = proportional_rank1(S_el, sig)
    vdb = vec_DB(z, Bm)
    c_lat = proportional_rank1(S_lat, vdb)
    check("%s: S_el = c sigma sigma^T with sigma = sym(L^T D B) (closed form)" % name, c_el is not None)
    check("%s: S_lat = c' (DB)(DB)^T (closed form)" % name, c_lat is not None)
    # sigma = R^T vec(DB) up to symmetrisation convention: pullback of v through R
    pv = [sum((R[r][c] * vdb[r] for r in range(n * n)), 0) for c in range(F.ne)]
    check("%s: R^T vec(DB) is proportional to sigma (pullback of the lattice-side stress)" % name,
          proportional_rank1([[pv[i] * pv[j] for j in range(F.ne)] for i in range(F.ne)], sig) is not None)
    # --- 3e invariants
    G = gram(L)
    P = spec["part"]
    G11 = submat(G, P[0], P[0])
    G12 = submat(G, P[0], P[1])
    G22 = submat(G, P[1], P[1])
    schurG = madd(G22, matmul(transpose(G12), solve_dense(G11, G12)), -1)
    inv = [invariants(G, "Gram G=L L^T (8x8)"), invariants(schurG, "block Schur G/G11"),
           invariants(S_lat, "S_lat (64x64)"), invariants(S_el, "S_el (36x36)")]
    detL = det_small(L)
    r_pullback_nonzero = any(x != 0 for x in pv)
    cls_equal = None
    if inv[2].get("class_mod_squares") is not None and inv[3].get("class_mod_squares") is not None:
        cls_equal = inv[2]["class_mod_squares"] == inv[3]["class_mod_squares"]
    elif inv[2].get("disc_nondeg_part") is not None:
        cls_equal = None
    # relation between the two discriminants and the pullback
    # --- 3f (basis change, scale): done only on the rational instances
    f_res = {}
    if spec["ring"] == "Q":
        Y, _ = F.self_stress()
        carried = []
        for seed in (11, 12, 13):
            U, Ui = rand_unimodular(Rng(seed), n)
            Lnew = matmul(U, L)
            Fc = Framework(L, U=(U, Ui))
            Fc.L = Lnew
            Yc, _ = Fc.self_stress()
            Sc = Fc.schur_selfstress(Fc.ae, Fc.ne, Yc)
            Slc = Fc.schur_selfstress(Fc.Z, Fc.ndl, Yc)
            Rc = matrix_R(Lnew)
            Uti = kron_I(Ui, n)
            expect = matmul(transpose(Uti), matmul(S_lat, Uti))
            carried.append({
                "seed": seed,
                "S_el_unchanged": Sc == S_el,
                "defect_zero": madd(Sc, lattice_pullback(Slc, Rc), -1) == [[0] * F.ne for _ in range(F.ne)],
                "S_lat_congruent": Slc == expect,
                "S_lat_inertia": inertia(Slc),
                "S_lat_class": disc_info(Slc).get("class_mod_squares"),
                "rank1_collapse": inertia(Sc) == [1, 0, F.ne - 1],
            })
        naive = []
        for seed in range(21, 31):
            U, Ui = rand_unimodular(Rng(seed), n)
            Fn = Framework(matmul(U, L))
            Sn = Fn.schur_selfstress(Fn.ae, Fn.ne)
            naive.append(inertia(Sn) == [1, 0, F.ne - 1])
        strain = []
        for seed in (41, 42, 43):
            g, gi = rand_unimodular(Rng(seed), n)
            Tinv = strain_T(gi)
            S2 = matmul(transpose(Tinv), matmul(S_el, Tinv))
            d1, M1 = clear_denominators(S_el)
            d2, M2 = clear_denominators(S2)
            strain.append({"seed": seed, "inertia_same": inertia(S2) == inertia(S_el),
                           "class_same": disc_info(S2).get("class_mod_squares") == disc_info(S_el).get("class_mod_squares"),
                           "snf_same_after_unimodular": snf_diag(M1)[:1] == snf_diag(M2)[:1] and d1 == d2 if False else (snf_diag(M1), d1) == (snf_diag(M2), d2),
                           "S_changed": S2 != S_el})
        gscale = []
        for lam in (Fraction(2), Fraction(1, 3), Fraction(5, 2)):
            Fs = Framework([[lam * x for x in r] for r in L], lam=lam)
            Ss = Fs.schur_selfstress(Fs.ae, Fs.ne)
            Sls = Fs.schur_selfstress(Fs.Z, Fs.ndl)
            Rs = matrix_R([[lam * x for x in r] for r in L])
            gscale.append({"lam": enc(lam), "S_scales_by_lam4": Ss == mscale(lam ** 4, S_el),
                           "defect_zero": madd(Ss, lattice_pullback(Sls, Rs), -1) == [[0] * F.ne for _ in range(F.ne)],
                           "inertia": inertia(Ss)})
        lscale = []
        for mu in (Fraction(2), Fraction(1, 3), Fraction(5, 2), Fraction(-1)):
            Fl = Framework([[mu * x for x in r] for r in L])
            Sl_ = Fl.schur_selfstress(Fl.ae, Fl.ne)
            lscale.append({"mu": enc(mu), "inertia": inertia(Sl_), "S_ratio_const": proportional_rank1(Sl_, sig) is not None})
        f_res = {"carried_basis_change": carried, "naive_basis_change_collapse_flags": naive, "strain_unimodular": strain,
                 "global_scale": gscale, "lattice_only_scale": lscale}
        check("%s: carried basis change leaves S_el exactly unchanged, defect zero, S_lat congruent (3 seeds)" % name,
              all(c["S_el_unchanged"] and c["defect_zero"] and c["S_lat_congruent"] and c["rank1_collapse"] for c in carried))
        check("%s: strain-side unimodular change preserves inertia, class, Smith form (3 seeds)" % name,
              all(s["inertia_same"] and s["class_same"] and s["snf_same_after_unimodular"] and s["S_changed"] for s in strain))
        check("%s: global scale: S -> lam^4 S exactly, collapse and zero defect persist" % name,
              all(g["S_scales_by_lam4"] and g["defect_zero"] for g in gscale))
    rep[name] = {
        "ring": spec["ring"], "det_L": enc(detL), "dim_ker_Mrot": len(basis), "rank_Mrot": rkrot,
        "symmetrizer_z": [enc(x) for x in z],
        "defect_nonzero_entries": nz, "c_el": enc(c_el), "c_lat": enc(c_lat),
        "pullback_R_T_v_nonzero": r_pullback_nonzero,
        "S_el_class_equals_S_lat_class": cls_equal,
        "invariants": inv, "f": f_res,
    }
    return F, Hl, Phi, R, S_lat


def arbitrary_matrix_tests(rep):
    """3d: for arbitrary symmetric M (not from any lattice) the defect vanishes under the real block-triangular Phi."""
    L = L_E8_s1()
    F = Framework(L)
    Phi = matrix_Phi(L)
    R = matrix_R(L)
    N = F.nu + F.ndl
    res = []
    zero_good = 0
    zero_bad = 0
    trials = 12
    for t in range(trials):
        rng = Rng(7000 + t)
        M = [[0] * N for _ in range(N)]
        for i in range(F.nu):
            M[i][i] = rng.rng(5, 9)
        for i in range(F.nu, N):
            M[i][i] = rng.rng(-3, 3)
        dens = 3 * N
        for _ in range(dens):
            i, j = rng.below(N), rng.below(N)
            v = rng.rng(-2, 2)
            if i != j:
                M[i][j] = v
                M[j][i] = v
        Mp = matmul(transpose(Phi), matmul(M, Phi))
        lhs = block_schur_invertible(Mp, F.nu)
        rhs = lattice_pullback(block_schur_invertible(M, F.nu), R)
        d0 = madd(lhs, rhs, -1)
        z_ok = is_zero_mat(d0)
        # contrast: Phi_bad has the macro block feeding the internal block the other way (lower triangular)
        Pb = [list(r) for r in Phi]
        for k in range(F.ndl):
            for c in range(F.nu):
                Pb[F.nu + k][c] = 0
        Pbad = [list(r) for r in Phi]
        for c in range(F.ne):  # remove X, add a T block (dL <- u) instead
            for i in range(F.nu):
                Pbad[i][F.nu + c] = 0
        for k in range(F.ndl):
            Pbad[F.nu + k][k % F.nu] = 1
        Mpb = matmul(transpose(Pbad), matmul(M, Pbad))
        try:
            lb = block_schur_invertible(Mpb, F.nu)
            bad_zero = madd(lb, rhs, -1)
            bz = is_zero_mat(bad_zero)
        except LibError:
            bz = False
        zero_good += 1 if z_ok else 0
        zero_bad += 1 if bz else 0
        res.append([z_ok, bz])
    rep["arbitrary_M_under_real_Phi"] = {"trials": trials, "defect_zero_count": zero_good, "lower_triangular_Phi_defect_zero_count": zero_bad}
    check("3d: arbitrary symmetric M (12 seeded, indefinite, M11 invertible): defect is zero for every M under the real Phi", zero_good == trials)
    control("3d control: a non-block-triangular Phi (macro feeds internal) gives nonzero defect on arbitrary M", zero_bad < trials)


def controls_real(F, Hl, Phi, R, S_lat, L):
    # wrong Phi: flip one entry of X
    He = H_el_from(F)
    bad = [list(r) for r in Phi]
    bad[8][F.nu + 0] = -bad[8][F.nu + 0] if bad[8][F.nu + 0] != 0 else 1
    control("wrong Phi breaks H_el = Phi^T H_lat Phi", matmul(transpose(bad), matmul(Hl, bad)) != He)
    # wrong pullback R (taken from a perturbed lattice) gives a nonzero defect
    Lp = [list(r) for r in L]
    Lp[2][5] = Lp[2][5] + Fraction(1, 3)
    Rp = matrix_R(Lp)
    S_el, _ = F.schur_direct()
    control("pullback through R of a perturbed lattice gives a nonzero defect", madd(S_el, lattice_pullback(S_lat, Rp), -1) != [[0] * F.ne for _ in range(F.ne)])
    # perturbed lattice breaks the closed form and the collapse
    Fp = Framework(Lp)
    Sp = Fp.schur_selfstress(Fp.ae, Fp.ne)
    control("perturbed lattice loses the rank-1 collapse", inertia(Sp) != [1, 0, F.ne - 1])
    # a symmetric perturbation keeps a symmetrizer: collapse survives (positive control for the closed form)
    Ls = [list(r) for r in L]
    Ls[2][5] = Ls[2][5] + Fraction(1, 3)
    Ls[5][2] = Ls[5][2] + Fraction(1, 3)
    Fs = Framework(Ls)
    Ss = Fs.schur_selfstress(Fs.ae, Fs.ne)
    check("positive control: symmetric perturbation of L keeps the rank-1 collapse", inertia(Ss) == [1, 0, F.ne - 1])


def main():
    rep = {}
    insts = instances()
    keep = None
    for name, spec in insts.items():
        res = real_pair(name, spec, rep)
        if name == "e8_s1":
            keep = (spec["L"],) + res
    L, F, Hl, Phi, R, S_lat = keep
    controls_real(F, Hl, Phi, R, S_lat, L)
    arbitrary_matrix_tests(rep)
    text = canon(rep)
    print("REPORT_JSON " + text.rstrip())
    print("REPORT_SHA256 " + sha(text))
    print("FAILS", len(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
