"""Compares clean-room objects against the upstream stated quantities. Usage: python3 -I -B anchor_compare.py <hermitian_dir>
Reads: out/anchor_fractals/probe4_witness_zeno_results.json (produced by the untouched upstream run), the committed copy of it,
upstream gravity committed results JSON (probe not runnable here: numpy missing), out/anchor_check003.stdout."""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from suite import *  # noqa: E402

FAILS = []


def chk(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def sha_file(p):
    import hashlib
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    W = sys.argv[1]
    # ---------------- A. fractals PR 59, probe4 (anchor: upstream script run untouched)
    ran = os.path.join(W, "out", "anchor_fractals", "probe4_witness_zeno_results.json")
    com = os.path.join(W, "out", "anchor_fractals", "committed_results.json")
    chk(sha_file(ran) == sha_file(com), "A0 upstream rerun output is byte-identical to its committed results file")
    d = load(ran)
    rows = d["part_b_exact_16x16_lindblad_zeno"]["exact_16x16_schur_sweep"]
    g1, g, gt = Fraction(1, 4), Fraction(3, 2), Fraction(1, 100)
    nrow = 0
    for r in rows:
        N = r["N"]
        Lm, order, pi, pw = liouvillian(N, g1, g, gt)
        R = schur(Lm, pw, pi)
        ix, iy, izz, zi, zx = (order.index(k) for k in ("IX", "IY", "IZ", "ZI", "ZX"))
        gam = -R[ix][ix]
        okk = (gam == Fraction(r["Gamma_Schur_IX_IY_exact"]) and -R[iy][iy] == gam and -R[izz][izz] == Fraction(r["IZ_decay_exact"])
               and -R[zi][zi] == Fraction(r["ZI_decay_exact"]) and -R[zx][zx] == Fraction(r["ZX_decay_exact"]))
        # regime from the 2x2 block [IX | XY]
        xy = order.index("XY")
        A = [[Lm[ix][ix], Lm[ix][xy]], [Lm[xy][ix], Lm[xy][xy]]]
        disc = (A[0][0] + A[1][1]) ** 2 - 4 * (A[0][0] * A[1][1] - A[0][1] * A[1][0])
        reg = "underdamped" if disc < 0 else ("EP2" if disc == 0 else "overdamped_zeno")
        chk(okk and reg == r["regime"] and gam == 2 * gt + 2 * g * g / (fr(N) ** 2 * g1),
            "A1 N=%d: Gamma_eff, IZ, ZI, ZX decays and regime '%s' reproduce the upstream sweep row exactly" % (N, reg))
        nrow += 1
    chk(nrow == 8, "A2 eight sweep rows compared")

    # ---------------- B. gravity PR 30, probe1: upstream script cannot run (numpy missing); anchor is the committed results JSON
    gj = load(os.path.join(W, "upstream", "gravity", "studies", "expedition-aest-helmholtz-probes", "probe1_aest_results.json"))
    for row in gj["exact_rational_minkowski_pole_zero_inertia"]:
        KB, lam, Kpp, r = (Fraction(row[k]) for k in ("KB", "lam_s", "Kpp", "r_eq_k2"))
        Hm = aest_hessian(KB, lam, Kpp, r)
        # symmetric elimination pivots in the order chi, p, P
        d0 = Hm[0][0]
        S1 = [[Hm[i][j] - Hm[i][0] * Hm[0][j] / d0 for j in (1, 2)] for i in (1, 2)]
        d1 = S1[0][0]
        d2 = S1[1][1] - S1[0][1] * S1[1][0] / d1 if d1 != 0 else Fraction(0)
        piv = [str(d0), str(d1), str(d2)]
        ine = inertia_congruence(Hm)  # (pos, neg, zero)
        upi = row["exact_inertia_pos_zero_neg"]  # (pos, zero, neg)
        chk(piv == row["exact_D_pivots"] and (ine[0], ine[2], ine[1]) == tuple(upi) and str(G_AA(KB, lam, Kpp, r)) == row["exact_G_AA_over_Gtilde"],
            "B1 %s: pivots %s, inertia (pos,zero,neg)=%s and G_AA reproduce the committed exact values" % (row["case"], piv, (ine[0], ine[2], ine[1])))
    # committed symbolic S_P string, transcribed by hand here and compared as text, then evaluated at my points
    want_txt = "-(KB*lam*r + Kpp*lam + Kpp - 2*lam*r)/(4*r*(KB*lam*r + Kpp*lam + Kpp + 2*r))"
    chk(gj["symbolic_theorems"]["hamiltonian_schur_complement_S_P"] == want_txt, "B2 committed S_P text equals the transcription used below")

    def SP_txt(KB, lam, Kpp, r):
        return -(KB * lam * r + Kpp * lam + Kpp - 2 * lam * r) / (4 * r * (KB * lam * r + Kpp * lam + Kpp + 2 * r))

    L_, Gv, Sp, rej = all_objects()
    okall = all(SP_txt(*(Fraction(rep["params"][k]) for k in ("KB", "lam", "Kpp", "r_eq_k2"))) == Fraction(rep["reduced"][0][0]) for rep, _ in Gv)
    chk(okall, "B3 committed closed form S_P equals my exact Schur complement at all %d sampled points" % len(Gv))
    chk(gj["symbolic_theorems"]["lam0_schur_S_P"] == "-Kpp/(4*r*(Kpp + 2*r))", "B4 committed lam=0 closed form text read")
    lam0 = [rep for rep, _ in Gv if Fraction(rep["params"]["lam"]) == 0]
    chk(all(-Fraction(rep["params"]["Kpp"]) / (4 * Fraction(rep["params"]["r_eq_k2"]) * (Fraction(rep["params"]["Kpp"]) + 2 * Fraction(rep["params"]["r_eq_k2"]))) == Fraction(rep["reduced"][0][0]) for rep in lam0) and len(lam0) >= 1,
        "B5 lam=0 closed form reproduced at %d sampled lam=0 point(s)" % len(lam0))

    # ---------------- C. ledger check_003 (anchor: untouched run) and its constants
    c3 = load_text = None
    with open(os.path.join(W, "out", "anchor_check003.stdout"), "r", encoding="utf-8") as fh:
        c3 = json.load(fh)
    chk(c3["edge_cases_audit"]["edge2_raw_negative_else_branch"] == str(Fraction(1 + 1) ** 2 / Fraction(10) - 5), "C1 raw else-branch value at (u,t,S,b)=(1,1,10,5) is -23/5")
    chk(c3["complex_hermitian_audit"]["violations_strengthened_chain_n_pos_H_perp_ge_R_opt"] == 0, "C2 upstream run reports 0 chain violations (its own count, 420 instances)")
    # sharpness witnesses asserted in the script source (read statically): values of R_opt at four tuples
    def ropt_full(u, t, S, b):
        v = R_opt(u, t, S, b)
        if v is not None:
            return v, "regime1 (derived: u^2 (G^-1)_11)"
        if u <= 0 or u + t <= 0:
            return Fraction(0), "regime0"
        val = (u + t) ** 2 / S - b
        return (val if val > 0 else Fraction(0)), "regime2 (transcribed: outside the Schur form)"
    for tup, want in (((6, 5, 43, 1), 2), ((10, 1, Fraction(121, 10), 1), 9), ((10, -4, 12, 1), 2), ((6, -3, 3, 0), 3)):
        u, t, S, b = (Fraction(x) for x in tup)
        v, how = ropt_full(u, t, S, int(b))
        chk(v == want, "C3 R_opt%s = %s (script asserts %s) [%s]" % (tuple(str(x) for x in tup), v, want, how))
        if how.startswith("regime1"):
            Gm = G2(S, t, b)
            chk(u * u * inv(Gm)[0][0] == want, "C4 same value as u^2 (G^-1)_11 for G=[[S,t],[t,b]] built from the tuple")
    # must-fail controls: each wrong statement has to be rejected, otherwise the comparator is not discriminating
    r0 = rows[0]
    Lm, order, pi, pw = liouvillian(r0["N"], g1, g, gt)
    R = schur(Lm, pw, pi)
    ix = order.index("IX")
    chk(not (-R[ix][ix] == Fraction(r0["Gamma_Schur_IX_IY_exact"]) + Fraction(1, 1000)), "K1 control: perturbed Gamma_eff is rejected")
    chk(gj["symbolic_theorems"]["hamiltonian_schur_complement_S_P"] != want_txt.replace("-(", "+(", 1), "K2 control: sign-flipped S_P text is rejected")
    chk(ropt_full(Fraction(6), Fraction(5), Fraction(43), 1)[0] != 3, "K3 control: wrong R_opt witness value 3 is rejected")
    chk(not all(SP_txt(*(Fraction(rep["params"][k]) for k in ("KB", "lam", "Kpp", "r_eq_k2"))) == -Fraction(rep["reduced"][0][0]) for rep, _ in Gv), "K4 control: negated S_P is rejected")
    print("RESULT anchor_compare: %s failures=%d" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
