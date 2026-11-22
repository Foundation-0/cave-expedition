"""Gate 5, task 3c: keep the real Phi construction, replace the lattice by seeded random integral lattices
of the same rank and determinant.  Exact.   usage: gate5_null_lattices.py <instance> <objects dir> [trials]
Families (per instance):
  c1  random lattice, same determinant and same Smith form as the real one, nonsymmetric basis (U1 D U2)
  c2  random lattice, same determinant and Smith form, symmetric basis matrix (U^T D U)
  c3  random basis of the SAME lattice, rows re-indexed naively (U L), bars keep their index set
  c4  isometric copy of the real lattice with a symmetric basis: Q L Q^T, Q a random signed permutation
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


def one(Lp, Rreal, ne, cross):
    F = Framework(Lp)
    Y, _ = F.self_stress()
    S = F.schur_selfstress(F.ae, F.ne, Y)
    Sl = F.schur_selfstress(F.Z, F.ndl, Y)
    R = matrix_R(Lp)
    d1 = madd(S, lattice_pullback(Sl, R), -1)          # D1: Phi rebuilt from L'
    d2 = madd(S, lattice_pullback(Sl, Rreal), -1)      # D2: the REAL Phi carries S_lat(L') to S_el(L')
    basis, rk = rotational_locking(bridge_of(Lp))
    res = {
        "dimSigma": len(Y),
        "dim_ker_Mrot": len(basis),
        "S_inertia": inertia(S),
        "S_lat_inertia": inertia(Sl),
        "D1_zero": is_zero_mat(d1),
        "D2_zero": is_zero_mat(d2),
        "S_zero": is_zero_mat(S),
        "collapse": inertia(S) == [1, 0, ne - 1],
    }
    if cross:
        Sd, _ = F.schur_direct()
        res["cross_direct_equal"] = Sd == S
    return res


def main():
    name = sys.argv[1]
    objd = sys.argv[2]
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    spec = instances()[name]
    L = spec["L"]
    n = len(L)
    ne = n * (n + 1) // 2
    Rreal = matrix_R(L)
    real = one(L, Rreal, ne, True)
    print("REAL", name, canon(real).strip())
    check("real lattice: collapse and D1 zero and D2 zero", real["collapse"] and real["D1_zero"] and real["D2_zero"] and real["cross_direct_equal"])
    out = {"instance": name, "trials": trials, "families": {}, "lattices": []}
    for fam, base in (("c1", 100000), ("c2", 200000), ("c3", 300000), ("c4", 700000)):
        rows = []
        for t in range(trials):
            rng = Rng(base + t)
            if fam == "c1":
                Lp = same_snf_lattice(rng, L, False)
            elif fam == "c2":
                Lp = same_snf_lattice(rng, L, True)
            elif fam == "c3":
                U, Ui = rand_unimodular(rng, n)
                Lp = matmul(U, L)
            else:
                perm = list(range(n))
                for i in range(n - 1, 0, -1):
                    j = rng.below(i + 1)
                    perm[i], perm[j] = perm[j], perm[i]
                Q = [[0] * n for _ in range(n)]
                for i in range(n):
                    Q[i][perm[i]] = 1 if rng.below(2) == 0 else -1
                Lp = matmul(Q, matmul(L, transpose(Q)))
            res = one(Lp, Rreal, ne, t < 8)
            rows.append(res)
            out["lattices"].append({"family": fam, "index": t, "L": encmat(Lp), "S_inertia": res["S_inertia"], "dimSigma": res["dimSigma"],
                                    "D1_zero": res["D1_zero"], "collapse": res["collapse"]})
        n_d1 = sum(1 for r in rows if r["D1_zero"])
        n_d2 = sum(1 for r in rows if r["D2_zero"])
        n_col = sum(1 for r in rows if r["collapse"])
        cross = [r["cross_direct_equal"] for r in rows if "cross_direct_equal" in r]
        det_ok = True
        out["families"][fam] = {
            "n": trials, "D1_zero": n_d1, "D2_zero": n_d2, "collapse": n_col,
            "S_zero": sum(1 for r in rows if r["S_zero"]),
            "D2_zero_among_nonzero_S": sum(1 for r in rows if r["D2_zero"] and not r["S_zero"]),
            "nonzero_S": sum(1 for r in rows if not r["S_zero"]),
            "S_rank_hist": sorted_hist([r["S_inertia"][0] + r["S_inertia"][1] for r in rows]),
            "dim_ker_Mrot_hist": sorted_hist([r["dim_ker_Mrot"] for r in rows]),
            "dimSigma_hist": sorted_hist([r["dimSigma"] for r in rows]),
            "cross_direct_equal": cross,
        }
        print("FAMILY", fam, canon(out["families"][fam]).strip())
        check("%s: self-stress engine equals direct Schur on the cross-checked trials" % fam, all(cross))
    # same determinant / Smith form of every c1, c2 lattice (exact)
    den0, M0 = clear_denominators(L)
    snf0 = snf_diag(M0)
    ok = True
    for rec in out["lattices"]:
        if rec["family"] in ("c1", "c2", "c3", "c4"):
            Lp = [[dec(x) for x in r] for r in rec["L"]]
            den, Mi = clear_denominators(Lp)
            if abs(det_small(Lp)) != abs(det_small(L)):
                ok = False
            if rec["index"] < 20 and (den, snf_diag(Mi)) != (den0, snf0):
                ok = False
    check("every sampled lattice has |det| equal to the real one; first 20 per family have the same Smith form (scale %d)" % den0, ok)
    # must-fail controls
    c2first = [dec(x) for x in out["lattices"][trials]["L"][0]] and [[dec(x) for x in r] for r in out["lattices"][trials]["L"]]
    Fc = Framework(c2first)
    Yc, _ = Fc.self_stress()
    Sc = Fc.schur_selfstress(Fc.ae, Fc.ne, Yc)
    Slc = Fc.schur_selfstress(Fc.Z, Fc.ndl, Yc)
    wrongR = [list(r) for r in matrix_R(c2first)]
    wrongR[3][1] = wrongR[3][1] + 1
    control("a wrong pullback R makes the D1 defect nonzero on a collapsing random lattice", not is_zero_mat(madd(Sc, lattice_pullback(Slc, wrongR), -1)))
    pert = [list(r) for r in c2first]
    pert[0][1] = pert[0][1] + Fraction(1, 5)
    Fp = Framework(pert)
    Sp = Fp.schur_selfstress(Fp.ae, Fp.ne)
    control("breaking the symmetry of a symmetric random lattice destroys the collapse", inertia(Sp) != [1, 0, ne - 1] and inertia(Sc) == [1, 0, ne - 1])
    text = canon(out)
    path = os.path.join(objd, "null_lattices_%s.json" % name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    summ = {"instance": name, "real": real, "families": out["families"]}
    st = canon(summ)
    print("OBJECT_SHA256 null_lattices_%s.json %s" % (name, sha(text)))
    print("SUMMARY_SHA256 " + sha(st))
    print("FAILS", len(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
