"""Exact check of the rank envelope R_opt, the docs/10 family and the higher-moment bounds A2 to A4.

Audits: AUDIT-002 (rank envelope R_opt and the chain rank P >= rank of the compression
>= n+(H_perp) >= R_opt) and AUDIT-014 (higher-moment bounds A2, A3, A4).
Backs, in VERDICTS.md: "Rank envelope R_opt and the chain ... 0 violations on 1,600 fresh exact
matrices, null controls fire" and "Higher-moment bounds A2, A3, A4 ... 0 violations (12,240 witnesses)".

For each random exact matrix pair (P PSD, Q with at most b positive eigenvalues) it checks the
chain, R_opt <= n+(H_perp), the six-term slack identity as an exact equality, R_opt as the supremum
over scale and weight, and that A2, A3, A4 never exceed n+(H_perp). Null controls (a bound with a
negative coefficient, b one too small) must fire, otherwise the harness is blind and the run fails.
Ranks and inertias use only exactlib_a.py. The spectral-inertia package is imported only to compare
its R_opt and its witness searches with the exact truth.

Needs: Python 3 with numpy, a clone of Foundation-0/spectral-inertia in SPECTRAL_INERTIA_DIR.
Run (about 45 seconds for the default size):
    SPECTRAL_INERTIA_DIR=/path/to/spectral-inertia python3 -I -B check_rank_envelope_and_moments.py [n_cases] [seed]
Defaults: n_cases 800, seed 20261121 (the first 800 matrices). Seed 777 gives the second 800.
Exit code 0 only if every hard check held and the null controls fired.
"""
import json
import math
import os
import random
import sys
from fractions import Fraction as Fr

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

sys.path.insert(0, common.spectral_inertia_dir())
import exactlib_a as L  # noqa: E402
from spectral_inertia import higher_moments as HM  # noqa: E402

NAME = "check_rank_envelope_and_moments"
N_CASES = int(sys.argv[1]) if len(sys.argv) > 1 else 800
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20261121
print("seed:", SEED, "n_cases:", N_CASES)


def need(ok, msg):
    if not ok:
        common.finish(NAME, False, "check failed: " + msg)


# ---------------- my own formulas ----------------

def ropt_mine(u, t, S, b):
    """R_opt written from the statement in THEOREMS.md, then clamped at 0."""
    if u <= 0 or u + t <= 0:
        return Fr(0)
    if b > 0 and t > 0 and t * (u + t) >= b * S:
        return u * u / (S - t * t / b)
    return max(Fr(0), (u + t) ** 2 / S - b)


def F_scaled(u, t, S, b, s, c):
    """Unscaled slack bound applied to (sP, sQ) with weight c >= 1: 2su + 2cst - s^2 S - c^2 b."""
    return 2 * s * u + 2 * c * s * t - s * s * S - c * c * b


def ours_family(u, t, S, b, c):
    """docs/10 sec 3.2: r >= 2 tr M - ||M||^2 + c tr Q - (1 + c/2)^2 b, c >= 0."""
    return 2 * (u + t) - S + c * t - (1 + c / 2) ** 2 * b


def ours_best(u, t, S, b):
    if b > 0 and t >= b:
        return 2 * u + t * t / b - S
    return 2 * (u + t) - S - b


def ceil0(x):
    return max(0, math.ceil(x))


# ---------------- matrix polynomial traces (my route: evaluate the matrix polynomial) ----------

def mpoly(H, coeffs):
    """sum_k coeffs[k] H^k as a matrix (coeffs[0] is the constant)."""
    n = len(H)
    out = L.zeros(n)
    Hk = L.eye(n)
    for k, ck in enumerate(coeffs):
        if k > 0:
            Hk = L.mmul(Hk, H)
        if ck != 0:
            out = L.madd(out, Hk, ck)
    return out


def tr_phi_a(H, a):
    """tr(1 - q_a(H)^2) = n - ||q_a(H)||_F^2, q_a(x) = 1 + sum (-1)^k a_k x^k."""
    q = [Fr(1)] + [(-1) ** k * ak for k, ak in enumerate(a, start=1)]
    Qm = mpoly(H, q)
    return Fr(len(H)) - L.fro2(Qm)


def tr_A3(H, x0, tau):
    d = 3 * x0 + tau
    Lc = 2 * x0 * (2 * x0 + tau) / d
    M = x0 * x0 * (x0 + tau) ** 3 / d
    n = len(H)
    # lam (L - lam) (lam + tau)^2 as a matrix product
    Hs = L.madd(H, L.eye(n), tau)
    A = L.mmul(L.mmul(H, L.madd(L.mscale(L.eye(n), Lc), H, Fr(-1))), L.mmul(Hs, Hs))
    return L.tr(A) / M


def a4_params(s, p, g1, g3, kap):
    beta = s + g3 / p
    alpha = 1 - (beta * beta - s * s + kap) / (2 * p)
    lam0 = (s + g1 - alpha * beta) / kap
    M = alpha * alpha + kap * lam0 * lam0
    return M


def a4_bound(H, Q, b, s, p, g1, g3, kap):
    n = len(H)
    phi = Fr(n) - L.fro2(mpoly(H, [Fr(1), -s, p]))
    Q3 = L.mmul(L.mmul(Q, Q), Q)
    return phi + 2 * g1 * L.tr(Q) + 2 * g3 * L.tr(Q3) - b * a4_params(s, p, g1, g3, kap)


# ---------------- instance generator ----------------

def instance(rng, idx):
    n = rng.randint(1, 6)
    cplx = rng.random() < 0.75
    U = L.rand_unitary(rng, n, cplx)
    mode = rng.choice(["general", "general", "regime1", "commuting", "inW", "inWperp", "zerorows",
                       "repeat", "zeroP", "smallnoise", "regime1", "regime1w", "regime1w"])
    if n == 1 and mode == "regime1w":
        mode = "regime1"
    b_true = rng.randint(0, n)
    if mode == "regime1w":
        b_true = rng.randint(1, n - 1)
    if mode == "regime1":
        b_true = rng.randint(1, n)
    qpos = [Fr(5) + (Fr(rng.randint(0, 1), 20) if rng.random() < 0.3 else 0) if mode in ("regime1", "regime1w")
            else L.rq(rng, 1, 6, (1, 2, 3)) for _ in range(b_true)]
    if mode == "repeat" and qpos:
        qpos = [qpos[0]] * b_true
    qneg = [-Fr(rng.randint(0, 1), 10) if mode in ("regime1", "regime1w", "smallnoise") else -L.rq(rng, 0, 5, (1, 2, 3))
            for _ in range(n - b_true)]
    if mode == "repeat" and qneg:
        qneg = [qneg[0]] * len(qneg)
    Q = L.from_eig(U, qpos + qneg)
    Wp = [[U[i][j] for j in range(b_true, n)] for i in range(n)]
    W = [[U[i][j] for j in range(b_true)] for i in range(n)]
    r = rng.randint(0, n)
    if mode in ("general", "regime1", "smallnoise"):
        P = L.rand_psd(rng, n, r, cplx)
        if mode == "regime1":
            P = L.mscale(P, Fr(1, rng.choice([10, 30, 60])))
    elif mode == "regime1w":
        kk = rng.randint(1, n - b_true)
        Y = [[L.rcz(rng, cplx) for _ in range(kk)] for _ in range(n - b_true)]
        Y2 = [[L.mscale([[L.rcz(rng, cplx)]], Fr(1, rng.choice([5, 20, 100])))[0][0] for _ in range(kk)]
              for _ in range(b_true)]
        X = L.madd(L.mmul(Wp, Y), L.mmul(W, Y2))
        P = L.mscale(L.mmul(X, L.dag(X)), Fr(1, rng.choice([10, 30, 60])))
    elif mode == "commuting":
        P = L.from_eig(U, [Fr(rng.randint(0, 3), rng.choice([1, 2])) for _ in range(n)])
    elif mode == "inW":
        if b_true == 0:
            P = L.zeros(n)
        else:
            kk = rng.randint(1, b_true)
            Y = [[L.rcz(rng, cplx) for _ in range(kk)] for _ in range(b_true)]
            X = L.mmul(W, Y)
            P = L.mmul(X, L.dag(X))
    elif mode == "inWperp":
        if b_true == n:
            P = L.zeros(n)
        else:
            kk = rng.randint(1, n - b_true)
            Y = [[L.rcz(rng, cplx) for _ in range(kk)] for _ in range(n - b_true)]
            X = L.mmul(Wp, Y)
            P = L.mmul(X, L.dag(X))
    elif mode == "zerorows":
        X = [[L.rcz(rng, cplx) for _ in range(max(1, r))] for _ in range(n)]
        for i in range(n):
            if rng.random() < 0.5:
                X[i] = [L.Z] * len(X[i])
        P = L.mmul(X, L.dag(X))
    elif mode == "repeat":
        V = L.rand_unitary(rng, n, cplx)
        P = L.from_eig(V, [Fr(2)] * r + [Fr(0)] * (n - r))
    else:  # zeroP
        P = L.zeros(n)
    alpha = Fr(rng.randint(1, 9), rng.randint(1, 5))
    P, Q = L.mscale(P, alpha), L.mscale(Q, alpha)
    b_decl = b_true + (0 if mode in ("regime1", "regime1w") else rng.choice([0, 0, 0, 0, 1, 2]))
    return dict(n=n, mode=mode, cplx=cplx, U=U, W=W, Wp=Wp, P=P, Q=Q, b_true=b_true, b=b_decl)


def truth(inst):
    P, Q, Wp = inst["P"], inst["Q"], inst["Wp"]
    H = L.madd(P, Q)
    n = inst["n"]
    full = n <= 5
    iP = L.inertia(P, full)
    iQ = L.inertia(Q, full)
    need(iP[1] == 0, "generator: P not PSD")
    need(iQ[0] == inst["b_true"], "generator: n_+(Q) wrong")
    rkP = L.rank(P)
    need(rkP == iP[0], "rank vs inertia of PSD P")
    if Wp and Wp[0]:
        Pp = L.mmul(L.mmul(L.dag(Wp), P), Wp)
        Hp = L.mmul(L.mmul(L.dag(Wp), H), Wp)
        rkPp = L.rank(Pp)
        npHp = L.inertia(Hp, full)[0]
    else:
        rkPp, npHp, Hp = 0, 0, None
    npH = L.inertia(H, full)[0]
    return dict(H=H, rkP=rkP, rkPp=rkPp, npHp=npHp, npH=npH, Hp=Hp)


def slack_identity(inst, T, c):
    """Check 2u + 2ct - S == c^2 b+ - 2(c-1) tr(P11+Q-) - ||A - cI||^2 - 2||P12||^2 + (2 tr Hp - ||Hp||^2)."""
    U, P, Q = inst["U"], inst["P"], inst["Q"]
    bp = inst["b_true"]
    n = inst["n"]
    Pb = L.mmul(L.mmul(L.dag(U), P), U)
    Qb = L.mmul(L.mmul(L.dag(U), Q), U)
    u, t, S = L.tr(P), L.tr(Q), L.fro2(T["H"])
    P11tr = sum((Pb[i][i][0] for i in range(bp)), Fr(0))
    Qm_tr = sum((-Qb[i][i][0] for i in range(bp, n)), Fr(0))
    P12 = sum((L.cabs2(Pb[i][j]) for i in range(bp) for j in range(bp, n)), Fr(0))
    Aerr = sum((L.cabs2(L.cs(L.ca(Pb[i][j], Qb[i][j]), (c, Fr(0)) if i == j else L.Z))
                for i in range(bp) for j in range(bp)), Fr(0))
    if T["Hp"] is not None:
        hp = 2 * L.tr(T["Hp"]) - L.fro2(T["Hp"])
    else:
        hp = Fr(0)
    lhs = 2 * u + 2 * c * t - S
    rhs = c * c * bp - 2 * (c - 1) * (P11tr + Qm_tr) - Aerr - 2 * P12 + hp
    return lhs == rhs, (P11tr + Qm_tr) >= 0, hp <= T["npHp"]


def main():
    rng = random.Random(SEED)
    cnt = dict(cases=0, noncommuting=0, complex=0, b_gt_btrue=0, regimes={"0": 0, "1": 0, "2": 0},
               chain_viol=0, ropt_viol=0, ropt_vs_theirs_mismatch=0, ropt_lt_ours=0,
               slack_identity_fail=0, sup_check_fail=0, scale_fail=0,
               ropt_gt_ours_strict=0, ropt_tie_ours=0, ropt_gt_ours_only_because_ours_negative=0,
               ceil_ropt_gt_ceil_ours=0, ceil_equal=0, ceil_ropt_gt_ceil_c2=0,
               a2_checks=0, a2_viol=0, a3_checks=0, a3_viol=0, a4_checks=0, a4_viol=0,
               their_h4_viol=0, their_h6_viol=0, their_a3_viol=0, their_a4_viol=0,
               their_h4_moment_mismatch=0,
               a2_beats_ceil_ropt=0, a4_beats_ceil_ropt=0, best_hm_beats_ceil_ropt=0,
               null_a2_negcoef_viol=0, null_a4_btoo_small_viol=0, null_ropt_btoo_small_viol=0,
               max_gap_examples=[])
    for idx in range(N_CASES):
        inst = instance(rng, idx)
        T = truth(inst)
        P, Q, H, b = inst["P"], inst["Q"], T["H"], inst["b"]
        u, t, S = L.tr(P), L.tr(Q), L.fro2(H)
        cnt["cases"] += 1
        if L.fro2(L.madd(L.mmul(P, Q), L.mmul(Q, P), Fr(-1))) != 0:
            cnt["noncommuting"] += 1
        if any(x[1] != 0 for r in H for x in r):
            cnt["complex"] += 1
        if b > inst["b_true"]:
            cnt["b_gt_btrue"] += 1
        # Lemma 0 chain
        if not (T["rkP"] >= T["rkPp"] >= T["npHp"] >= T["npH"] - b):
            cnt["chain_viol"] += 1
        R = ropt_mine(u, t, S, b)
        reg = "0" if (u <= 0 or u + t <= 0) else ("1" if (b > 0 and t > 0 and t * (u + t) >= b * S) else "2")
        cnt["regimes"][reg] += 1
        if R > T["npHp"]:
            cnt["ropt_viol"] += 1
        try:
            Rt = HM.R_opt(u, t, S, b)
        except Exception as e:  # report, do not hide
            Rt = "EXC %s" % e
        if Rt != R:
            cnt["ropt_vs_theirs_mismatch"] += 1
        # sup over (s, c): the claimed optimizer attains R (when R > 0), random points never exceed R
        if R > 0:
            if reg == "1":
                s_star = u / (S - t * t / b)
                c_star = s_star * t / b
            else:
                s_star, c_star = (u + t) / S, Fr(1)
            if not (c_star >= 1 and F_scaled(u, t, S, b, s_star, c_star) == R):
                cnt["sup_check_fail"] += 1
        for _ in range(6):
            s_r = Fr(rng.randint(1, 40), rng.randint(1, 20))
            c_r = 1 + Fr(rng.randint(0, 40), rng.randint(1, 10))
            if F_scaled(u, t, S, b, s_r, c_r) > max(R, Fr(0)):
                cnt["sup_check_fail"] += 1
        sc = Fr(rng.randint(1, 30), rng.randint(1, 30))
        if ropt_mine(sc * u, sc * t, sc * sc * S, b) != R:
            cnt["scale_fail"] += 1
        # slack identity at random c (identity holds for any real c)
        for c in (Fr(1), Fr(rng.randint(1, 30), rng.randint(1, 7)) + 1, Fr(-3, 2)):
            ok_id, _, ok_hp = slack_identity(inst, T, c)
            if not (ok_id and ok_hp):
                cnt["slack_identity_fail"] += 1
        # docs/10 comparisons
        ob = ours_best(u, t, S, b)
        fam = [ours_family(u, t, S, b, Fr(c)) for c in (0, 1, 2, 3, 4, 6, 10)]
        if any(R < f for f in fam + [ob]):
            cnt["ropt_lt_ours"] += 1
        if any(f > T["rkP"] for f in fam + [ob]):
            need(False, "docs/10 bound exceeded rank P (should never happen)")
        if R > ob:
            cnt["ropt_gt_ours_strict"] += 1
            if ob < 0 and R == 0:
                cnt["ropt_gt_ours_only_because_ours_negative"] += 1
        elif R == ob:
            cnt["ropt_tie_ours"] += 1
        if ceil0(R) > ceil0(ob):
            cnt["ceil_ropt_gt_ceil_ours"] += 1
        else:
            cnt["ceil_equal"] += 1
        c2 = HM.R_lemma32_fixed_c(u, t, S, b, Fr(2))
        if ceil0(R) > ceil0(c2):
            cnt["ceil_ropt_gt_ceil_c2"] += 1
        # ---------------- A2 ----------------
        best_a2 = Fr(-10**9)
        a_list = []
        for _ in range(4):
            m = rng.randint(1, 3)
            a_list.append([Fr(rng.randint(0, 6), rng.randint(1, 8)) for _ in range(m)])
        # sharp choice from rounded positive eigenvalues of H (q* = prod (1 - x/mu))
        A = np.array([[float(x[0]) + 1j * float(x[1]) for x in r] for r in H])
        ev = sorted(np.linalg.eigvalsh(A), reverse=True)
        posv = [Fr(e).limit_denominator(1000) for e in ev if e > 1e-6]
        for m in (1, 2, 3):
            mus = posv[:m]
            if mus and all(mu > 0 for mu in mus):
                coef = [Fr(1)]
                for mu in mus:
                    coef = [x - (coef[i - 1] / mu if i > 0 else 0) for i, x in enumerate(coef + [Fr(0)])]
                a_list.append([abs(cf) for cf in coef[1:]])
        for a in a_list:
            val = tr_phi_a(H, a)
            cnt["a2_checks"] += 1
            if val - b > T["npHp"] or val > T["npH"]:
                cnt["a2_viol"] += 1
            best_a2 = max(best_a2, val - b)
        mom = {k: L.tr(mpoly(H, [Fr(0)] * k + [Fr(1)])) for k in range(1, 7)}
        h4 = HM.R_hankel4_exact(mom[1], mom[2], mom[3], mom[4], b)
        h6 = HM.R_hankel6_exact(mom, b)
        if h4["exact_bound"] > T["npHp"]:
            cnt["their_h4_viol"] += 1
        if h6["exact_bound"] > T["npHp"]:
            cnt["their_h6_viol"] += 1
        # recompute their H4 witness through my matrix route
        a_w = [Fr(x) for x in h4["witness_a"]]
        mine_h4 = max(Fr(0), tr_phi_a(H, a_w) - b)
        if mine_h4 != h4["exact_bound"]:
            cnt["their_h4_moment_mismatch"] += 1
        if max(best_a2, h6["exact_bound"]) > ceil0(R):
            cnt["a2_beats_ceil_ropt"] += 1
        # null: a negative coefficient breaks phi <= 0 on lam <= 0
        val = tr_phi_a(H, [Fr(-1), Fr(0)])
        if val > T["npH"]:
            cnt["null_a2_negcoef_viol"] += 1
        # ---------------- A3 ----------------
        for _ in range(3):
            x0 = Fr(rng.randint(1, 40), rng.randint(1, 8))
            tau = Fr(rng.randint(0, 10), rng.randint(1, 8))
            val = tr_A3(H, x0, tau)
            cnt["a3_checks"] += 1
            if val - b > T["npHp"] or val > T["npH"]:
                cnt["a3_viol"] += 1
        for x0 in posv[:2]:
            val = tr_A3(H, x0, Fr(0))
            cnt["a3_checks"] += 1
            if val - b > T["npHp"] or val > T["npH"]:
                cnt["a3_viol"] += 1
        a3t = HM.find_noise_quartic_witness(mom, b, Fr(0))
        if a3t["exact_bound"] > T["npHp"]:
            cnt["their_a3_viol"] += 1
        # ---------------- A4 ----------------
        best_a4 = Fr(-10**9)
        for _ in range(4):
            s = Fr(rng.randint(0, 6), rng.randint(1, 4))
            p = Fr(rng.randint(1, 6), rng.randint(1, 8))
            g1 = Fr(rng.randint(0, 6), rng.randint(1, 4))
            g3 = Fr(rng.randint(0, 3), rng.randint(1, 8))
            kap = Fr(rng.randint(1, 8), rng.randint(1, 8))
            val = a4_bound(H, Q, b, s, p, g1, g3, kap)
            cnt["a4_checks"] += 1
            if val > T["npHp"]:
                cnt["a4_viol"] += 1
            best_a4 = max(best_a4, val)
            nb = inst["b_true"] - 1
            if nb >= 0 and a4_bound(H, Q, nb, s, p, g1, g3, kap) > T["npHp"]:
                cnt["null_a4_btoo_small_viol"] += 1
        hints = []
        for i in range(min(2, len(posv))):
            for j in range(i + 1, min(3, len(posv))):
                mu1, mu2 = posv[i], posv[j]
                s_h, p_h = (mu1 + mu2) / (mu1 * mu2), 1 / (mu1 * mu2)
                hints.append((s_h, p_h, mu1 * 2))
                hints.append((s_h, p_h, mu1))
        Q3 = L.tr(L.mmul(L.mmul(Q, Q), Q))
        a4t = HM.find_weighted_quartic_witness(mom, t, Q3, b, peak_hints=hints or None)
        if a4t["exact_bound"] > T["npHp"]:
            cnt["their_a4_viol"] += 1
        if "witness" in a4t:
            w = a4t["witness"]
            mine = max(Fr(0), a4_bound(H, Q, b, Fr(w["s"]), Fr(w["p"]), Fr(w["gamma1"]), Fr(w["gamma3"]),
                                       Fr(w["kappa"])))
            need(mine == a4t["exact_bound"], "their A4 value differs from my matrix route")
        if max(best_a4, a4t["exact_bound"]) > ceil0(R):
            cnt["a4_beats_ceil_ropt"] += 1
        best_hm = max(best_a2, h6["exact_bound"], a3t["exact_bound"], best_a4, a4t["exact_bound"])
        if best_hm > ceil0(R):
            cnt["best_hm_beats_ceil_ropt"] += 1
        # null: declare b one too small for R_opt
        nb = inst["b_true"] - 1
        if nb >= 0 and ropt_mine(u, t, S, nb) > T["npHp"]:
            cnt["null_ropt_btoo_small_viol"] += 1
        gap = T["npHp"] - R
        if len(cnt["max_gap_examples"]) < 3 and gap >= 2 and inst["n"] <= 4:
            cnt["max_gap_examples"].append(dict(n=inst["n"], mode=inst["mode"], rkP=T["rkP"], npHp=T["npHp"],
                                                R_opt=str(R)))
    print(json.dumps(cnt, indent=1))
    hard = ["chain_viol", "ropt_viol", "ropt_vs_theirs_mismatch", "ropt_lt_ours", "slack_identity_fail",
            "sup_check_fail", "scale_fail", "a2_viol", "a3_viol", "a4_viol", "their_h4_viol", "their_h6_viol",
            "their_a3_viol", "their_a4_viol", "their_h4_moment_mismatch"]
    bad = {k: cnt[k] for k in hard if cnt[k]}
    need(not bad, "violations %r" % bad)
    need(cnt["null_a2_negcoef_viol"] > 0 and cnt["null_a4_btoo_small_viol"] > 0
         and cnt["null_ropt_btoo_small_viol"] > 0,
         "null controls never fired; harness may be blind")
    common.finish(NAME, True, "cases=%d complex=%d noncommuting=%d A2=%d A3=%d A4=%d witnesses, 0 violations, "
                  "null controls fired (A2 %d, A4 %d, R_opt %d)" % (
                      cnt["cases"], cnt["complex"], cnt["noncommuting"], cnt["a2_checks"], cnt["a3_checks"],
                      cnt["a4_checks"], cnt["null_a2_negcoef_viol"], cnt["null_a4_btoo_small_viol"],
                      cnt["null_ropt_btoo_small_viol"]))


if __name__ == "__main__":
    main()
