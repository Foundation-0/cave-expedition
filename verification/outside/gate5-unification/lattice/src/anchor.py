"""Task 2: compare the clean-room objects with what the untouched upstream scripts print.
usage: anchor.py <objects dir> <out dir>
Reads: objects/pair_*.json, out/up_driver.txt, out/up_sheaf_json.txt (written earlier under the sandbox).
Exit code 1 if a check fails or a must-fail control passes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g5lib import *
from g5more import *

FAILS = []
PASSES = []
CONTROL_FAILS = []


def check(label, cond):
    if cond:
        PASSES.append(label)
        print("PASS", label)
    else:
        FAILS.append(label)
        print("FAIL", label)


def control(label, detected):
    if detected:
        print("CONTROL-DETECTED", label)
    else:
        CONTROL_FAILS.append(label)
        print("CONTROL-NOT-DETECTED", label)


def load_obj(d, name):
    with open(os.path.join(d, "pair_" + name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def decmat(M):
    return [[dec(x) for x in r] for r in M]


def summarize(S, F):
    d0 = [dict(r) for r in F.d0]
    rk = rank_sparse(d0, F.nu)
    iner = inertia(S)
    k = next((i for i in range(len(S)) if S[i][i] != 0), None)
    mode = None
    if iner[0] == 1 and k is not None:
        mode = [enc(S[k][j] / S[k][k]) for j in range(len(S))]
    return {"H0": F.nu - rk, "H1": F.nb - rk, "inertia": iner, "tr": enc(tr(S)), "S00": enc(S[0][0]), "mode": mode}


def up_fields(r):
    return {"H0": r["H0"], "H1": r["H1"], "inertia": r["S_cell_inertia"], "tr": r["tr_S_cell"], "S00": r["S_00"], "mode": r["rank1_mode_normalized"]}


def main():
    objd, outd = sys.argv[1], sys.argv[2]
    lines = open(os.path.join(outd, "up_driver_A.txt"), encoding="utf-8").read().splitlines()
    up = {}
    for ln in lines:
        if ln.startswith("UP_D8_TWISTED "):
            r = json.loads(ln[len("UP_D8_TWISTED "):])
            up[("d8", r["a"], r["t"])] = r
        elif ln.startswith("UP_E8_HADAMARD_s1 "):
            up["e8"] = json.loads(ln[len("UP_E8_HADAMARD_s1 "):])
        elif ln.startswith("UP_E8_CERT_SHA256 "):
            up["cert"] = ln.split()[1]
        elif ln.startswith("UP_D8_rk_M_rot "):
            up["rk_rot8"] = int(ln.split()[1])
    # ---- n = 8 anchors (upstream functions fed n = 8 by the driver, plus Hadamard fed to the same function)
    pairs = [("d8_s1", ("d8", "0", "1")), ("d8_k1", ("d8", "4/3", "1/3"))]
    for name, key in pairs:
        o = load_obj(objd, name)
        L = decmat(o["L"])
        F = Framework(L)
        S = decmat(o["elasticity"]["S"])
        mine = summarize(S, F)
        theirs = up_fields(up[key])
        check("anchor %s all fields equal upstream %s" % (name, key[0]), mine == theirs)
        check("anchor %s inertia [1,0,35]" % name, mine["inertia"] == [1, 0, 35])
    # third D_8 point (8/9, 7/9), built on the fly
    L3 = L_Dn_rational_point(8, Fraction(8, 9), Fraction(7, 9))
    F3 = Framework(L3)
    S3, _ = F3.schur_direct()
    check("anchor d8 (8/9,7/9) all fields equal upstream", summarize(S3, F3) == up_fields(up[("d8", "8/9", "7/9")]))
    o = load_obj(objd, "e8_s1")
    L = decmat(o["L"])
    F = Framework(L)
    S = decmat(o["elasticity"]["S"])
    mine = summarize(S, F)
    check("anchor e8_s1 all fields equal upstream function fed H8/2", mine == up_fields(up["e8"]))
    check("anchor e8_s1 inertia [1,0,35], H0=29, H1=21", mine["inertia"] == [1, 0, 35] and mine["H0"] == 29 and mine["H1"] == 21)
    # sigma* = 2 I + H8 (upstream strain-inner-product coordinates [S_ii, 2 S_ij])
    H = sylvester(3)
    sig = [H[i][i] + 2 for i in range(8)] + [2 * H[i][j] for (i, j) in off_pairs(8)]
    c = proportional_rank1(S, [Fraction(x) for x in sig])
    check("anchor e8_s1 S = c * sigma sigma^T with sigma = 2I+H8 (c=%s)" % (enc(c) if c is not None else "none"), c is not None)
    sig8 = [[H[i][j] + (2 if i == j else 0) for j in range(8)] for i in range(8)]
    check("anchor 2I+H8 inertia (4,4,0)", inertia(sig8) == [4, 4, 0])
    # rotational locking rank 7 (upstream rk(M_rot) = 7 for C_8 and for H8)
    basis_d, rk_d = rotational_locking(bridge_of(lattice_from_bridge(twisted_cycle(8))))
    basis_e, rk_e = rotational_locking(bridge_of(L_E8_s1()))
    check("anchor rk(M_rot)=7 for C_8 (upstream %s) and for H8/2" % up.get("rk_rot8"), rk_d == 7 and rk_e == 7 and up.get("rk_rot8") == 7)
    # ---- n = 3..7 against the upstream --json report
    with open(os.path.join(outd, "up_sheaf_json_A.txt"), encoding="utf-8") as f:
        rep = json.load(f)
    allok = True
    npts = 0
    for row in rep["universal_Cn_rank1_collapse"]:
        n = row["n"]
        for pt in row["points"]:
            a, t = Fraction(pt["a"]), Fraction(pt["t"])
            Ln = L_Dn_rational_point(n, a, t)
            Fn = Framework(Ln)
            Sn, _ = Fn.schur_direct()
            m = summarize(Sn, Fn)
            u = up_fields(pt)
            u["mode"] = pt["rank1_mode_normalized"]
            if m != u:
                allok = False
            npts += 1
    check("anchor twisted cycles n=3..7 (%d points) equal upstream --json" % npts, allok)
    # nonsymmetrizable negative control (upstream: rk(M_rot)=3, H0=3, H1=0, inertia [0,0,6])
    C3 = [[0, 1, -1], [1, 0, -1], [1, -1, 0]]
    F3n = Framework(lattice_from_bridge(C3))
    S3n, _ = F3n.schur_direct()
    nn = rep["negative_control_nonsymmetrizable_C3"]
    mm = summarize(S3n, F3n)
    check("anchor non-symmetrizable C3 control equals upstream", mm["H0"] == nn["H0"] and mm["H1"] == nn["H1"] and mm["inertia"] == nn["S_cell_inertia"])
    # ---- lattice side: L8(s) over Z[sqrt 2]
    L0, Ip = L8_of_s(0)
    check("L8(0) = (2+sqrt2) I", all(L0[i][j] == (Q2(2, 1) if i == j else 0) for i in range(8) for j in range(8)))
    L1, _ = L8_of_s(1)
    check("L8(1) = 2I + H8/2", all(L1[i][j] == L_E8_s1()[i][j] for i in range(8) for j in range(8)))
    check("det L8(1) = 16", det_small(L_E8_s1()) == 16)
    ok = True
    for s in (Fraction(1, 7), Fraction(1, 2), Fraction(3, 5), Fraction(9, 10)):
        Ls, _ = L8_of_s(s)
        for i in range(8):
            r = Ls[i]
            ell2 = sum(((r[j] - (2 if i == j else 0)) ** 2 if False else (r[j] - (2 if i == j else 0)) * (r[j] - (2 if i == j else 0)) for j in range(8)), Q2(0, 0))
            if ell2 != 2:
                ok = False
        G = gram(Ls)
        G1 = gram(L_E8_s1())
        diff = madd(G, G1, -1)
        iv = inertia(diff)
        if iv[1] != 0:
            ok = False
    check("bar identity |b_i|^2=2 exactly and G(s)-G(1) positive semidefinite at 4 rational s", ok)
    check("upstream certificate hash recomputed by sandboxed driver = %s" % up["cert"][:8], up["cert"] == "e4f14b928a3b08897e562ed56e334c6471ccf12e6bd55f52b6273f2577b0ef31")
    # ---- must-fail controls
    # (1) a wrong Phi (one sign flipped in X) must break H_el = Phi^T H_lat Phi
    Fe = Framework(L_E8_s1())
    Hl, He = H_lat_from(Fe), H_el_from(Fe)
    Phi = matrix_Phi(L_E8_s1())
    good = matmul(transpose(Phi), matmul(Hl, Phi)) == He
    check("H_el = Phi^T H_lat Phi for the real Phi (e8_s1)", good)
    bad = [list(r) for r in Phi]
    bad[1 * 8 + 0][128 + 0 + 0] = -bad[1 * 8 + 0][128 + 0]  # flip one X entry (vertex 1, coord 0, eps_00)
    control("wrong Phi (X sign flipped) breaks the congruence", matmul(transpose(bad), matmul(Hl, bad)) != He)
    # (2) perturbed lattice: collapse must be lost and upstream numbers must not match
    Lp = [list(r) for r in L_E8_s1()]
    Lp[0][1] = Lp[0][1] + Fraction(1, 7)
    Fp = Framework(Lp)
    Sp, _ = Fp.schur_direct()
    control("perturbed lattice loses the rank-1 collapse", inertia(Sp) != [1, 0, 35])
    control("perturbed lattice does not match upstream S fields", summarize(Sp, Fp) != up_fields(up["e8"]))
    # (3) deliberately wrong upstream value must be rejected
    wrong = dict(up_fields(up["e8"]))
    wrong["inertia"] = [1, 0, 34]
    control("comparison rejects a wrong inertia [1,0,34]", summarize(S, F) != wrong)
    # (4) wrong L8 (swap a_+ and a_-) breaks bar identity
    Ls, Ip = L8_of_s(Fraction(1, 2))
    Ls2 = [list(r) for r in Ls]
    Ls2[0][0], Ls2[1][1] = Ls2[1][1], Ls2[0][0]
    r0 = Ls2[0]
    ell2 = sum(((r0[j] - (2 if j == 0 else 0)) * (r0[j] - (2 if j == 0 else 0)) for j in range(8)), Q2(0, 0))
    control("swapped diagonal entries break |b_0|^2 = 2", ell2 != 2)
    print("SUMMARY passes=%d fails=%d control_fails=%d" % (len(PASSES), len(FAILS), len(CONTROL_FAILS)))
    return 1 if (FAILS or CONTROL_FAILS) else 0


if __name__ == "__main__":
    sys.exit(main())
