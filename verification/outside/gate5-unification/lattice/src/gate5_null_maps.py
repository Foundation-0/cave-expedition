"""Gate 5, task 3b: keep the real lattice, replace Phi by seeded random integer maps of the same shape (192 x 164)
and rank (164).  Exact.   usage: gate5_null_maps.py <instance> <objects dir> [trials]
Families:
  m1  block upper triangular [[P,Q],[0,R]], P unimodular (128x128), Q sparse, R (64x36) of rank 36   (same structure as the real Phi)
  m2  fully random sparse map of rank 164 (no block structure)
  m3  block lower triangular [[P,0],[T,R]]  (macro coordinates feed the internal block)
Defect of a map Phi' : Schur(Phi'^T H_lat Phi')  -  R'^T Schur(H_lat) R'   with R' the lower-right 64x36 block.
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


def sparse_block(rng, r, c, dens_num, dens_den, lo=-1, hi=1):
    M = [[0] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            if rng.below(dens_den) < dens_num:
                v = rng.rng(lo, hi)
                M[i][j] = v
    return M


def rank_dense(M):
    rows = [{j: Fraction(v) for j, v in enumerate(r) if v != 0} for r in M]
    return rank_sparse(rows, len(M[0]))


def make_map(fam, rng, nu, ndl, ne):
    N, Mc = nu + ndl, nu + ne
    while True:
        if fam == "m1":
            P, _ = rand_unimodular(rng, nu, 60)
            Q = sparse_block(rng, nu, ne, 1, 12)
            R = sparse_block(rng, ndl, ne, 1, 3, -2, 2)
            Phi = [P[i] + Q[i] for i in range(nu)] + [[0] * nu + R[i] for i in range(ndl)]
        elif fam == "m3":
            P, _ = rand_unimodular(rng, nu, 60)
            T = sparse_block(rng, ndl, nu, 1, 24)
            R = sparse_block(rng, ndl, ne, 1, 3, -2, 2)
            Phi = [P[i] + [0] * ne for i in range(nu)] + [T[i] + R[i] for i in range(ndl)]
        else:
            Phi = sparse_block(rng, N, Mc, 1, 16)
        if rank_dense([list(r) for r in Phi]) == Mc:
            return Phi


def apply_map(F, Phi):
    """rows of R_lat Phi : 120 x 164 as (u-part rows, eps-part rows) sparse dicts."""
    rl = rlat_rows(F)
    nu = F.nu
    ur, er = [], []
    for row in rl:
        acc = {}
        for k, v in row.items():
            pk = Phi[k]
            for c, w in enumerate(pk):
                if w != 0:
                    acc[c] = acc.get(c, 0) + v * w
        ur.append({c: v for c, v in acc.items() if c < nu and v != 0})
        er.append({c - nu: v for c, v in acc.items() if c >= nu and v != 0})
    return ur, er


def schur_map(F, Phi):
    ur, er = apply_map(F, Phi)
    rows = {}
    for e, d in enumerate(ur):
        for c, v in d.items():
            rows.setdefault(c, {})[e] = v
    Y, _ = nullspace_sparse([rows[k] for k in sorted(rows)], F.nb)
    return F.schur_selfstress(er, F.ne, Y), len(Y)


def main():
    name = sys.argv[1]
    objd = sys.argv[2]
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    L = instances()[name]["L"]
    F = Framework(L)
    nu, ndl, ne = F.nu, F.ndl, F.ne
    Y0, _ = F.self_stress()
    S_lat = F.schur_selfstress(F.Z, ndl, Y0)
    S_el = F.schur_selfstress(F.ae, ne, Y0)
    # the real Phi itself, same pipeline
    Phi0 = matrix_Phi(L)
    S0, _ = schur_map(F, Phi0)
    R0 = [row[nu:] for row in Phi0[nu:]]
    real_def = madd(S0, lattice_pullback(S_lat, R0), -1)
    check("real Phi through the random-map pipeline: defect zero, S equals S_el", is_zero_mat(real_def) and S0 == S_el)
    out = {"instance": name, "trials": trials, "families": {}}
    first_m3_defect_nonzero = None
    wrong_ok = None
    for fam, base in (("m1", 400000), ("m2", 500000), ("m3", 600000)):
        rows = []
        for t in range(trials):
            rng = Rng(base + t)
            Phi = make_map(fam, rng, nu, ndl, ne)
            Sp, dsig = schur_map(F, Phi)
            Rmm = [row[nu:] for row in Phi[nu:]]
            d = madd(Sp, lattice_pullback(S_lat, Rmm), -1)
            r = {"defect_zero": is_zero_mat(d), "S_zero": is_zero_mat(Sp), "collapse": inertia(Sp) == [1, 0, ne - 1],
                 "S_rank": rank_of(Sp), "dimSigma": dsig}
            if t < 3:
                Hl = H_lat_from(F)
                Mp = matmul(transpose(Phi), matmul(Hl, Phi))
                r["cross_direct_equal"] = block_schur(Mp, nu) == Sp
            if fam == "m3" and t == 0:
                first_m3_defect_nonzero = not r["defect_zero"]
            if fam == "m1" and t == 0:
                Rw = [list(x) for x in Rmm]
                r0 = next(i for i in range(ndl) if S_lat[i][i] != 0)  # a coordinate on which the lattice-side stress lives
                Rw[r0][0] = Rw[r0][0] + 1
                wrong_ok = not is_zero_mat(madd(Sp, lattice_pullback(S_lat, Rw), -1))
            rows.append(r)
        cross = [r["cross_direct_equal"] for r in rows if "cross_direct_equal" in r]
        out["families"][fam] = {
            "n": trials,
            "defect_zero": sum(1 for r in rows if r["defect_zero"]),
            "defect_zero_with_S_nonzero": sum(1 for r in rows if r["defect_zero"] and not r["S_zero"]),
            "collapse": sum(1 for r in rows if r["collapse"]),
            "S_zero": sum(1 for r in rows if r["S_zero"]),
            "S_rank_hist": sorted_hist([r["S_rank"] for r in rows]),
            "dimSigma_hist": sorted_hist([r["dimSigma"] for r in rows]),
            "cross_direct_equal": cross,
        }
        print("FAMILY", fam, canon(out["families"][fam]).strip())
        check("%s: self-stress pipeline equals the direct dense Schur on cross-checked trials" % fam, all(cross))
    control("a tampered R' makes the defect nonzero on a triangular map", wrong_ok is True)
    control("the first block-lower-triangular map has a nonzero defect", first_m3_defect_nonzero is True)
    text = canon(out)
    with open(os.path.join(objd, "null_maps_%s.json" % name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("OBJECT_SHA256 null_maps_%s.json %s" % (name, sha(text)))
    print("FAILS", len(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
