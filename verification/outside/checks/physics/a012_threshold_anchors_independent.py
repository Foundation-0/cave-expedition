#!/usr/bin/env python3
"""Independent check of the galaxy hold-out and the outside anchors (AUDIT-012).

Backs: VERDICTS section 1 row "SPARC to KiDS-1000 outside anchor (012)", and the
section 3 repair of AUDIT-012 (the 185.59 km/s zero-parameter model is not
falsified; the trained threshold of 60.15 km/s is an optimiser artifact).

Data: the host repo's own catalog (wave7 build_catalog, 126 systems), the
SPARC and KiDS tables (wave3) and the Wave-9/10 threshold model, all loaded
unmodified from the gravity clone. Fits are written here: dense profile fits
under an effective-variance chi-squared and under a vectorised copy of wave7's
correlated errors-in-variables metric. Parts: leave-one-catalog-out Hill fits,
the one-parameter Jeans threshold, the zero-parameter sigma* = 185.59 per
catalog, the latch quantities (rank and a seeded permutation test, seed 777001),
and the SPARC to KiDS-1000 anchor.

Needs: Python 3, numpy, scipy; a clone of Foundation-0/gravity (draft pull request 30).
Run:   python3 -I -B a012_threshold_anchors_independent.py /path/to/gravity
       (or set GRAVITY_REPO; add --verbose for all numbers)
Time:  about 30 seconds.
Exit:  0 only if every check holds.
"""
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2_dist

NAME = "a012_threshold_anchors_independent"
FAILS = []
COUNT = [0]
SEED = 777001
print("seed", SEED)


def check(cond, msg):
    COUNT[0] += 1
    if not cond:
        FAILS.append(msg)


def repo_path():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    value = args[0] if args else os.environ.get("GRAVITY_REPO", "")
    if not value or not Path(value).is_dir():
        raise SystemExit("Pass the path of a Foundation-0/gravity clone as the first argument or set GRAVITY_REPO.")
    return Path(value)


GRAV = repo_path()


def load(name, rel):
    path = GRAV / rel
    if not path.is_file():
        raise SystemExit("Missing " + str(path) + ". Is the clone at the commit listed in README.md?")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


w7 = load("w7", "wave7_group_cluster_threshold_audit.py")
sys.modules["wave7_group_cluster_threshold_audit"] = w7
w3 = load("w3", "wave3_empirical_audit.py")
w9 = load("w9", "wave9_scale_convergence_audit.py")
w10 = load("w10", "wave10_covariant_jeans_unification.py")

ROWS = w7.build_catalog()
FAM = {
    "galaxies": ("SPARC_HSB", "Mistele2024_KiDS_WL"),
    "milgrom_opt": ("Milgrom2019_opt",),
    "milgrom_rich": ("Milgrom2019_rich",),
    "angus_xray": ("Angus2008_Xray",),
    "kettula_wl": ("Kettula2015_WL",),
}
SIG = np.array([r["sig"] for r in ROWS])
Y = np.array([r["logR"] for r in ROWS])
SX = np.array([r["sx"] for r in ROWS])
SY = np.array([r["sy"] for r in ROWS])
CV = np.array([r["cov"] for r in ROWS])
CAT = np.array([r["cat"] for r in ROWS])
FIDX = {f: np.flatnonzero(np.isin(CAT, c)) for f, c in FAM.items()}
VAR = SY**2 + (CV * SX) ** 2


def hill(s, sc, sh, rs):
    s = np.asarray(s, float)
    x3 = np.where(s > sc, np.clip(s * s - sc * sc, 0, None) ** 1.5, 0.0)
    return np.where(s > sc, np.log10(1.0 + (rs - 1.0) * x3 / (x3 + sh**3)), 0.0)


def chi2_diag(idx, pred):
    return float(np.sum((Y[idx] - pred) ** 2 / VAR[idx]))


KS = np.arange(-14, 15) / 4.0


def chi2_odr(idx, f):
    """Vectorised copy of wave7.odr_chi2 (cov_on=True), for any vectorised model f(sigma)."""
    xi = np.log10(SIG[idx])
    yi, sx, sy, a = Y[idx], SX[idx], SY[idx], CV[idx]
    u = xi[:, None] + KS[None, :] * sx[:, None]
    dx = xi[:, None] - u
    dy = (yi[:, None] - a[:, None] * dx) - f(10.0**u)
    q = (dx / sx[:, None]) ** 2 + (dy / sy[:, None]) ** 2
    return float(np.sum(np.min(q, axis=1)))


def fit_hill(idx, metric, sc_grid=np.arange(40.0, 601.0, 2.0)):
    best = None
    prof = []
    for sc in sc_grid:
        def obj(p):
            lsh, rs = p
            if not (1.0 <= lsh <= 3.2 and 1.05 <= rs <= 15):
                return 1e9
            f = lambda s: hill(s, sc, 10**lsh, rs)
            return chi2_diag(idx, f(SIG[idx])) if metric == "diag" else chi2_odr(idx, f)
        b = None
        for st in ([1.6, 3.5], [2.4, 4.0], [2.8, 6.0]):
            r = minimize(obj, st, method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-6, "maxiter": 600})
            if b is None or r.fun < b.fun:
                b = r
        prof.append((float(sc), float(b.fun)))
        if best is None or b.fun < best[0]:
            best = (float(b.fun), float(sc), float(10 ** b.x[0]), float(b.x[1]))
    ci = [sc for sc, c in prof if c <= best[0] + 4.0]
    return {"chi2": best[0], "sc": best[1], "sh": best[2], "rsat": best[3], "sc_dchi2_4_range": [min(ci), max(ci)]}


# Wave-9/10 threshold model, built from the host's constants and nu_rar
def jeans_logR(s, sj, dust):
    out = np.zeros_like(np.asarray(s, float))
    s = np.asarray(s, float)
    for i, sv in np.ndenumerate(s):
        if sv <= sj:
            continue
        f_trap = 1.0 - (sj / sv) ** 2
        g_tot = 2.0 * (sv * 1e3) ** 2 / (250.0 * w10.KPC)
        lo, hi = 1e-15, g_tot
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if mid * (w10.nu_rar(mid / w10.A0) + f_trap * dust) < g_tot:
                lo = mid
            else:
                hi = mid
        gb = 0.5 * (lo + hi)
        out[i] = math.log10(g_tot / (gb * w10.nu_rar(gb / w10.A0)))
    return out


def sigma_star():
    sR0, Dn = w10.build_eh98_power_spectrum()
    return w10.audit_c26_nonlinear_collapse_and_k0_test(sR0, Dn)["sigma_star_z0_kms"]


def part_threshold():
    allidx = np.arange(len(ROWS))
    out = {"n": len(ROWS), "families": {f: int(len(i)) for f, i in FIDX.items()},
           "sigma_ranges": {f: [float(SIG[i].min()), float(SIG[i].max())] for f, i in FIDX.items()}}
    # full-sample fits
    out["full_hill_diag"] = fit_hill(allidx, "diag")
    out["full_hill_odr"] = fit_hill(allidx, "odr", np.arange(40.0, 601.0, 5.0))
    # LOCO, both metrics
    loco = {}
    for f, hold in FIDX.items():
        train = np.setdiff1d(allidx, hold)
        row = {}
        for metric, grid in (("diag", np.arange(40.0, 601.0, 2.0)), ("odr", np.arange(40.0, 601.0, 5.0))):
            h = fit_hill(train, metric, grid)
            pred = lambda s, h=h: hill(s, h["sc"], h["sh"], h["rsat"])
            hold_c2 = chi2_diag(hold, pred(SIG[hold])) if metric == "diag" else chi2_odr(hold, pred)
            mond_c2 = chi2_diag(hold, np.zeros(len(hold))) if metric == "diag" else chi2_odr(hold, lambda s: np.zeros_like(s))
            row[metric] = {"train_sc": h["sc"], "train_sc_dchi2_4_range": h["sc_dchi2_4_range"],
                           "train_sh": h["sh"], "train_rsat": h["rsat"],
                           "holdout_chi2_hill": hold_c2, "holdout_chi2_mond": mond_c2}
        loco[f] = row
    out["loco_hill"] = loco
    # Wave-9 one-parameter threshold (R2500 dust ratio), LOCO on sigma_J, wave7 ODR metric
    dust = w9.DUST_TO_B_R2500
    sj_grid = np.arange(60.0, 401.0, 5.0)
    cache = {sj: jeans_logR(SIG, sj, dust) for sj in sj_grid}

    def odr_tab(idx, sj):
        # ODR needs f at shifted sigmas; evaluate exactly (slow path) only for chosen sj
        return chi2_odr(idx, lambda s: jeans_logR(s, sj, dust))

    w9loco = {}
    for f, hold in FIDX.items():
        train = np.setdiff1d(allidx, hold)
        c2s = [(chi2_diag(train, cache[sj][train]), sj) for sj in sj_grid]
        c_best, sj_best = min(c2s)
        ci = [sj for c, sj in c2s if c <= c_best + 4.0]
        w9loco[f] = {"train_sigJ_diag": float(sj_best), "train_sigJ_dchi2_4_range": [float(min(ci)), float(max(ci))],
                     "holdout_chi2_diag_at_train_sigJ": chi2_diag(hold, cache[sj_best][hold]),
                     "holdout_chi2_diag_mond": chi2_diag(hold, np.zeros(len(hold)))}
    out["loco_wave9_1param_diag"] = w9loco
    # Wave-10 zero-parameter sigma_* model, per catalog (nothing is trained: no LOCO needed)
    sst = sigma_star()
    p10 = jeans_logR(SIG, sst, w10.DUST_TO_B_R2500)
    out["wave10_k0"] = {"sigma_star": sst, "per_family_chi2_diag": {f: chi2_diag(i, p10[i]) for f, i in FIDX.items()},
                        "per_family_chi2_mond_diag": {f: chi2_diag(i, np.zeros(len(i))) for f, i in FIDX.items()},
                        "per_family_n": {f: int(len(i)) for f, i in FIDX.items()},
                        "clean60_odr": chi2_odr(np.flatnonzero(~np.isin(CAT, ["Milgrom2019_opt", "Milgrom2019_rich"])),
                                                lambda s: jeans_logR(s, sst, w10.DUST_TO_B_R2500))}
    return out


def part_latch(full):
    """Contract 4 quantities for the Hill fit on all 126 systems (effective-variance metric)."""
    sc, sh, rs = full["sc"], full["sh"], full["rsat"]
    Wh = 1 / np.sqrt(VAR)
    p0 = np.array([sc, sh, rs])
    J = np.zeros((len(ROWS), 3))
    for j in range(3):
        d = np.zeros(3)
        d[j] = 1e-4 * p0[j]
        J[:, j] = Wh * (hill(SIG, *(p0 + d)) - hill(SIG, *(p0 - d))) / (2 * d[j])
    sv = np.linalg.svd(J, compute_uv=False)
    rank = int(np.sum(sv > sv[0] * 1e-10))
    Qm, _ = np.linalg.qr(J)

    def sin2(v):
        return float(1 - np.linalg.norm(Qm.T @ v) ** 2 / np.linalg.norm(v) ** 2)

    r_star = Wh * (Y - hill(SIG, *p0))
    out = {"m": len(ROWS), "rank_Phi": rank, "m_minus_rank": len(ROWS) - rank,
           "surviving_fraction": (len(ROWS) - rank) / len(ROWS),
           "singular_values": sv.tolist(),
           "stationarity_|J^T r*|/(|J||r*|)": float(np.linalg.norm(J.T @ r_star) / (np.linalg.norm(J) * np.linalg.norm(r_star))),
           "sin2_threshold_shift_audit_dF_dsc": sin2(J[:, 0]),
           "sin2_audit_185_minus_fitted": sin2(Wh * (hill(SIG, 185.59, sh, rs) - hill(SIG, *p0))),
           "sin2_catalog_offsets": {f: sin2(Wh * np.isin(np.arange(len(ROWS)), i)) for f, i in FIDX.items()}}
    # post-fit catalog-offset statistic with a fresh-seed permutation null
    rng = np.random.default_rng(SEED)
    z = r_star

    def stat(zv):
        return sum((np.sum(Wh[i] * zv[i]) ** 2) / np.sum(Wh[i] ** 2) for i in FIDX.values())

    t0 = stat(z)
    ge = sum(stat(rng.permutation(z)) >= t0 for _ in range(4000))
    out["catalog_offset_stat"] = float(t0)
    out["catalog_offset_perm_p_seed777001"] = (ge + 1) / 4001
    out["post_fit_chi2_over_m_minus_rank"] = float(np.sum(z**2) / (len(ROWS) - rank))
    return out


def part_sparc_kids():
    def rar(lgb, ds, a0):
        gb = 10.0**lgb
        u = (gb / a0) ** (ds / (1 + ds))
        return math.log10(gb / (-math.expm1(-u)))

    def c2_sparc(ds, a0):
        return sum(((lo - rar(lb, ds, a0)) / (sd / math.sqrt(n))) ** 2 for lb, lo, sd, n in w3.SPARC_RAR_BINS)

    def c2_kids(ds, a0, table):
        r = 1000.0 * 3.085677581491367e19
        c = 0.0
        for lm, v, e in table:
            gb = 6.67430e-11 * 10**lm * 1.98847e30 / r**2
            vp = math.sqrt(10 ** rar(math.log10(gb), ds, a0) * r) / 1e3
            c += ((v - vp) / e) ** 2
        return c

    res = {}
    best = min((c2_sparc(ds, a0 * 1e-12), ds, a0 * 1e-12) for ds in np.arange(0.80, 1.101, 0.005) for a0 in range(80, 161))
    b1 = min((c2_sparc(1.0, a0 * 1e-12), 1.0, a0 * 1e-12) for a0 in range(80, 161))
    for tag, (c, ds, a0) in (("free_ds", best), ("ds_1", b1)):
        res[tag] = {"ds": round(float(ds), 3), "a0": a0, "sparc_chi2": c,
                    "kids_1mpc_chi2": c2_kids(ds, a0, w3.KIDS_WL_ALL_1000KPC)}
    # the dependence of the anchor on ds alone, a0 held at the ds=1 value
    res["kids_1mpc_vs_ds_at_fixed_a0"] = {f"{d:.2f}": c2_kids(d, b1[2], w3.KIDS_WL_ALL_1000KPC) for d in (0.90, 0.94, 0.97, 1.0, 1.03)}
    return res


def main():
    th = part_threshold()
    out = {"threshold": th, "latch": part_latch(th["full_hill_diag"]), "sparc_kids": part_sparc_kids()}
    L = th["loco_hill"]
    check(th["n"] == 126, "catalog size is not 126")
    check(th["families"] == {"galaxies": 6, "milgrom_opt": 56, "milgrom_rich": 10, "angus_xray": 26, "kettula_wl": 28},
          "catalog family sizes differ")
    # galaxy hold-out: the trained threshold and the hold-out misfit against pure MOND
    g = L["galaxies"]
    check(g["diag"]["train_sc"] == 74.0, "galaxy fold, diagonal metric: trained threshold is not 74 km/s")
    check(129.0 <= g["diag"]["holdout_chi2_hill"] <= 132.0, "galaxy fold hold-out chi2 is not about 130")
    check(0.33 <= g["diag"]["holdout_chi2_mond"] <= 0.35, "galaxy fold pure-MOND chi2 is not about 0.34")
    check(g["odr"]["train_sc"] == 145.0, "galaxy fold, correlated metric: trained threshold is not 145 km/s")
    check(g["odr"]["train_sc_dchi2_4_range"] == [140.0, 170.0], "galaxy fold, correlated metric: range is not 140 to 170")
    # the other four folds stay at 156 to 202 km/s
    for f in ("milgrom_opt", "milgrom_rich", "angus_xray", "kettula_wl"):
        for m in ("diag", "odr"):
            check(156.0 <= L[f][m]["train_sc"] <= 202.0, "fold %s %s: trained threshold outside 156 to 202" % (f, m))
    check(th["loco_wave9_1param_diag"]["galaxies"]["train_sigJ_diag"] == 75.0, "one-parameter Jeans galaxy fold is not 75 km/s")
    # zero-parameter sigma* = 185.59: acceptable on every catalog, nothing trained
    k0 = th["wave10_k0"]
    check(round(k0["sigma_star"], 2) == 185.59, "sigma* is not 185.59")
    for f, want in (("galaxies", 1.57), ("milgrom_opt", 62.5), ("milgrom_rich", 17.7), ("angus_xray", 39.2), ("kettula_wl", 19.2)):
        c, n = k0["per_family_chi2_diag"][f], k0["per_family_n"][f]
        check(abs(c - want) < 0.06, "sigma* chi2 for %s is %.2f, not %.2f" % (f, c, want))
        check(chi2_dist.sf(c, n) > 0.01, "sigma* chi2 for %s is not acceptable (p <= 0.01)" % f)
    # latch quantities of the Hill fit
    lt = out["latch"]
    check(lt["m"] == 126 and lt["rank_Phi"] == 3 and lt["m_minus_rank"] == 123, "latch counts are not m=126, rank 3, 123 surviving")
    check(lt["sin2_threshold_shift_audit_dF_dsc"] < 1e-12, "threshold-shift audit is not in the span of the fit")
    check(lt["catalog_offset_perm_p_seed777001"] <= 0.0005, "catalog offsets do not disagree at p <= 0.0005")
    # SPARC to KiDS-1000 anchor
    sk = out["sparc_kids"]
    check(sk["free_ds"]["ds"] == 0.945 and abs(sk["free_ds"]["a0"] - 1.25e-10) < 1e-13, "free fit is not ds 0.945, a0 1.25e-10")
    check(abs(sk["free_ds"]["sparc_chi2"] - 25.89) < 0.01 and abs(sk["ds_1"]["sparc_chi2"] - 30.49) < 0.01, "SPARC chi2 is not 30.49 to 25.89")
    check(abs(sk["ds_1"]["kids_1mpc_chi2"] - 31.5) < 0.1 and abs(sk["free_ds"]["kids_1mpc_chi2"] - 69.9) < 0.1, "KiDS chi2 is not 31.5 to 69.9")
    v = sk["kids_1mpc_vs_ds_at_fixed_a0"]
    check(abs(v["1.03"] - 13.8) < 0.1, "KiDS chi2 at ds 1.03 is not 13.8")
    check(v["0.90"] > v["0.94"] > v["0.97"] > v["1.00"] > v["1.03"], "KiDS chi2 does not fall as ds rises")

    if "--verbose" in sys.argv:
        print(json.dumps(out, indent=1))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    print("RESULT %s: PASS %d of %d checks; galaxy hold-out trained threshold %d km/s (diag) and %d km/s (correlated); sigma* 185.59 acceptable on all five catalogs; "
          "latch rank %d of %d; SPARC to KiDS-1000 chi2 %.1f to %.1f" % (
              NAME, COUNT[0], COUNT[0], g["diag"]["train_sc"], g["odr"]["train_sc"], lt["rank_Phi"], lt["m"],
              sk["ds_1"]["kids_1mpc_chi2"], sk["free_ds"]["kids_1mpc_chi2"]))


if __name__ == "__main__":
    main()
