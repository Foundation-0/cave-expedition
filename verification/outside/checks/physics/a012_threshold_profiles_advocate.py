#!/usr/bin/env python3
"""Advocate check of the AUDIT-012 threshold claim (own fits, own metrics).

Backs: VERDICTS section 3, row "AUDIT-012". (1) "Decisively falsifies" the 185 km/s
threshold is false as worded: the zero-parameter sigma* = 185.59 is acceptable
on every catalog. (2) The sharper statement: the 120 groups and clusters alone
disfavour an onset at 185 (delta chi-squared 11.6 to 17.1), the 6 galaxies alone
need at least about 173, so the two disagree. (3) The trained threshold of
60.15 km/s is an optimiser artifact; the profile puts it near 150 under the
host's correlated metric.

Data source only: build_catalog() of the gravity clone's wave7 module (126
systems). The chi-squared metrics, the Hill model, the Jeans threshold model and
the profiles are written here. Part B asks which catalogs pull the one-parameter
Jeans threshold below 185. Nothing is random.

Needs: Python 3, numpy, scipy; a clone of Foundation-0/gravity (draft pull request 30).
Run:   python3 -I -B a012_threshold_profiles_advocate.py /path/to/gravity
       (or set GRAVITY_REPO; add --verbose for all numbers)
Time:  about 1 to 2 minutes.
Exit:  0 only if every check holds.
"""
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.stats import chi2 as chi2_dist

NAME = "a012_threshold_profiles_advocate"
FAILS = []
COUNT = [0]


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


def need(cond, msg):
    if not cond:
        raise SystemExit("CHECK FAILED: " + msg)


W7 = GRAV / "wave7_group_cluster_threshold_audit.py"
if not W7.is_file():
    raise SystemExit("Missing " + str(W7) + ". Is the clone at the commit listed in README.md?")
spec = importlib.util.spec_from_file_location("w7data", W7)
w7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w7)
ROWS = w7.build_catalog()
need(len(ROWS) == 126, "catalog size")

SIG = np.array([r["sig"] for r in ROWS], float)
Y = np.array([r["logR"] for r in ROWS], float)
SX = np.array([r["sx"] for r in ROWS], float)
SY = np.array([r["sy"] for r in ROWS], float)
CV = np.array([r["cov"] for r in ROWS], float)
CAT = np.array([r["cat"] for r in ROWS])
FAMS = {
    "galaxies": ["SPARC_HSB", "Mistele2024_KiDS_WL"],
    "milgrom_opt": ["Milgrom2019_opt"],
    "milgrom_rich": ["Milgrom2019_rich"],
    "angus_xray": ["Angus2008_Xray"],
    "kettula_wl": ["Kettula2015_WL"],
}
IDX = {f: np.flatnonzero(np.isin(CAT, c)) for f, c in FAMS.items()}
ALL = np.arange(126)
NONGAL = np.setdiff1d(ALL, IDX["galaxies"])

# ---- metrics -------------------------------------------------------------
def chi2_eff(idx, f):
    var = SY[idx] ** 2 + (CV[idx] * SX[idx]) ** 2
    return float(np.sum((Y[idx] - f(SIG[idx])) ** 2 / var))


KGRID = np.arange(-14, 15) / 4.0


def chi2_corr(idx, f):
    """Correlated errors-in-variables metric written from the formula in wave7's docstring-free odr_chi2:
    min over a 29-point latent grid u = x + k sx/4 of (dx/sx)^2 + ((y - a dx) - f(10^u))^2/sy^2."""
    x = np.log10(SIG[idx])
    u = x[:, None] + KGRID[None, :] * SX[idx][:, None]
    dx = x[:, None] - u
    resid = (Y[idx][:, None] - CV[idx][:, None] * dx) - f(10.0 ** u)
    q = (dx / SX[idx][:, None]) ** 2 + (resid / SY[idx][:, None]) ** 2
    return float(np.sum(q.min(axis=1)))


# ---- models --------------------------------------------------------------
def hill(s, sc, sh, rs):
    s = np.asarray(s, float)
    d = np.clip(s * s - sc * sc, 0.0, None) ** 1.5
    return np.where(s > sc, np.log10(1.0 + (rs - 1.0) * d / (d + sh ** 3)), 0.0)


A0 = 1.20e-10
KPC = 3.085677581491367e19
DUST = (1.0 - 0.105) / 0.105  # Vikhlinin f_b,2500 = 0.105, as stated in gravity CLAIMS C-23/C-26


def nu(y):
    sy = np.sqrt(np.clip(y, 0.0, None))
    out = np.ones_like(sy)
    m = (sy > 0) & (sy <= 40.0)
    out[m] = 1.0 / (1.0 - np.exp(-sy[m]))
    return out


def jeans(s, sj, dust=DUST):
    """log10 boost at 250 kpc: solve g_b (nu(g_b/a0) + f_trap dust) = g_tot by bisection (vectorised)."""
    s = np.asarray(s, float)
    shape = s.shape
    s = s.ravel()
    out = np.zeros_like(s)
    m = s > sj
    if np.any(m):
        sv = s[m]
        ft = 1.0 - (sj / sv) ** 2
        gt = 2.0 * (sv * 1e3) ** 2 / (250.0 * KPC)
        lo = np.full_like(sv, 1e-15)
        hi = gt.copy()
        for _ in range(70):
            mid = 0.5 * (lo + hi)
            go = mid * (nu(mid / A0) + ft * dust) < gt
            lo = np.where(go, mid, lo)
            hi = np.where(go, hi, mid)
        gb = 0.5 * (lo + hi)
        out[m] = np.log10(gt / (gb * nu(gb / A0)))
    return out.reshape(shape)


# ---- profiles ------------------------------------------------------------
LSH = np.linspace(1.0, 3.0, 41)       # log10 sigma_half 10..1000 km/s
RS = np.linspace(1.2, 8.0, 69)


def hill_profile(idx, metric, sc_grid):
    prof = []
    for sc in sc_grid:
        best = None
        for lsh in LSH:
            for rs in RS[::2]:
                f = lambda s, sc=sc, sh=10 ** lsh, rs=rs: hill(s, sc, sh, rs)
                c = chi2_eff(idx, f) if metric == "eff" else chi2_corr(idx, f)
                if best is None or c < best[0]:
                    best = (c, lsh, rs)
        # local refinement on rs around best
        c0, l0, r0 = best
        for lsh in np.linspace(l0 - 0.05, l0 + 0.05, 5):
            for rs in np.linspace(max(1.2, r0 - 0.1), r0 + 0.1, 5):
                f = lambda s, sc=sc, sh=10 ** lsh, rs=rs: hill(s, sc, sh, rs)
                c = chi2_eff(idx, f) if metric == "eff" else chi2_corr(idx, f)
                if c < best[0]:
                    best = (c, lsh, rs)
        prof.append((float(sc), best[0], float(10 ** best[1]), float(best[2])))
    return prof


def summarise(prof, at=185.0):
    cmin = min(p[1] for p in prof)
    b = min(prof, key=lambda p: p[1])
    near = min(prof, key=lambda p: abs(p[0] - at))
    ci = [p[0] for p in prof if p[1] <= cmin + 4.0]
    return {"best_sc": b[0], "best_sh": b[2], "best_rsat": b[3], "chi2_min": cmin,
            "dchi2_at_%g" % at: near[1] - cmin, "sc_dchi2le4": [min(ci), max(ci)]}


def compute():
    out = {}
    hold = IDX["galaxies"]
    # 1. Hill trained on the 120 non-galaxy systems, two metrics
    for metric, grid in (("eff", np.arange(40.0, 402.0, 5.0)), ("corr", np.arange(40.0, 402.0, 5.0))):
        prof = hill_profile(NONGAL, metric, grid)
        s = summarise(prof)
        c, sh, rs = s["best_sc"], s["best_sh"], s["best_rsat"]
        f = lambda x: hill(x, c, sh, rs)
        z = lambda x: np.zeros_like(np.asarray(x, float))
        s["holdout_gal_chi2_hill"] = chi2_eff(hold, f) if metric == "eff" else chi2_corr(hold, f)
        s["holdout_gal_chi2_mond"] = chi2_eff(hold, z) if metric == "eff" else chi2_corr(hold, z)
        # restricted to wave7's own sigma_crit search range (150..520)
        sub = [p for p in prof if p[0] >= 150.0]
        s["restricted_150_best_sc"] = min(sub, key=lambda p: p[1])[0]
        out["hill_train_nongal_" + metric] = s
    # 2. Wave-9/10 one-parameter Jeans threshold: profile sigma_J per training set
    sj_grid = np.arange(50.0, 302.0, 2.5)
    for name, idx in (("train_nongal", NONGAL), ("galaxies_only", hold), ("all126", ALL)):
        for metric in ("eff", "corr"):
            prof = []
            for sj in sj_grid:
                f = lambda x, sj=sj: jeans(x, sj)
                prof.append((float(sj), chi2_eff(idx, f) if metric == "eff" else chi2_corr(idx, f), 0, 0))
            s = summarise(prof, at=185.59)
            out["jeans1p_%s_%s" % (name, metric)] = {k: s[k] for k in ("best_sc", "chi2_min", "dchi2_at_185.59", "sc_dchi2le4")}
            if name == "train_nongal":
                bj = s["best_sc"]
                f = lambda x: jeans(x, bj)
                out["jeans1p_%s_%s" % (name, metric)]["holdout_gal_chi2"] = (
                    chi2_eff(hold, f) if metric == "eff" else chi2_corr(hold, f))
    # 3. Zero-parameter sigma* = 185.59 per catalog, both metrics, and MOND
    k0 = {}
    for fam, idx in IDX.items():
        f = lambda x: jeans(x, 185.59)
        z = lambda x: np.zeros_like(np.asarray(x, float))
        k0[fam] = {"n": int(len(idx)), "eff": chi2_eff(idx, f), "corr": chi2_corr(idx, f),
                   "mond_eff": chi2_eff(idx, z), "mond_corr": chi2_corr(idx, z)}
    out["k0_sigma185.59_per_catalog"] = k0
    return out




def which_catalog():
    grid = np.arange(50.0, 302.0, 2.5)
    sets = {"milgrom_opt": IDX["milgrom_opt"], "milgrom_rich": IDX["milgrom_rich"],
            "milgrom_both": np.concatenate([IDX["milgrom_opt"], IDX["milgrom_rich"]]),
            "xray_plus_wl": np.concatenate([IDX["angus_xray"], IDX["kettula_wl"]])}
    out = {}
    for k, idx in sets.items():
        for name, m in (("eff", chi2_eff), ("corr", chi2_corr)):
            prof = [(float(s), m(idx, lambda x, s=s: jeans(x, s))) for s in grid]
            cmin = min(p[1] for p in prof)
            b = min(prof, key=lambda p: p[1])[0]
            at = min(prof, key=lambda p: abs(p[0] - 185.59))[1]
            ci = [p[0] for p in prof if p[1] <= cmin + 4]
            out[k + "_" + name] = {"best": b, "dchi2_185.59": at - cmin, "ci4": [min(ci), max(ci)]}
    return out


def main():
    out = compute()
    pb = which_catalog()
    hc, he = out["hill_train_nongal_corr"], out["hill_train_nongal_eff"]
    # (3) the 60.15 km/s value is not where the profile sits
    check(abs(hc["best_sc"] - 150.0) <= 5.0, "correlated-metric Hill threshold is not near 150 km/s")
    check(hc["sc_dchi2le4"] == [140.0, 170.0], "correlated-metric Hill range is not 140 to 170")
    check(abs(hc["best_sc"] - 60.15) > 50.0, "profile threshold is near the reported 60.15")
    check(he["best_sc"] == 75.0 and he["sc_dchi2le4"] == [40.0, 140.0], "diagonal-metric Hill threshold is not 75 (range 40 to 140)")
    check(hc["holdout_gal_chi2_hill"] > 100 and he["holdout_gal_chi2_hill"] > 100, "trained Hill does not fail on the galaxy hold-out")
    check(hc["holdout_gal_chi2_mond"] < 1 and he["holdout_gal_chi2_mond"] < 1, "pure MOND does not fit the galaxies")
    # (2) 120 groups and clusters alone disfavour 185
    d185 = [hc["dchi2_at_185"], he["dchi2_at_185"], out["jeans1p_train_nongal_eff"]["dchi2_at_185.59"],
            out["jeans1p_train_nongal_corr"]["dchi2_at_185.59"]]
    check(min(d185) >= 11.5 and max(d185) <= 17.2, "delta chi-squared at 185 on the 120 is outside 11.6 to 17.1")
    check(abs(min(d185) - 11.55) < 0.05 and abs(max(d185) - 17.13) < 0.05, "delta chi-squared extremes are not 11.55 and 17.13")
    for m in ("eff", "corr"):
        ga = out["jeans1p_galaxies_only_" + m]
        check(ga["sc_dchi2le4"][0] >= 172.0, "galaxies-only lower bound is below 172 (%s)" % m)
        check(ga["dchi2_at_185.59"] < 4.0, "185.59 is outside the galaxies-only range (%s)" % m)
        check(out["jeans1p_train_nongal_" + m]["sc_dchi2le4"][1] < 185.59, "120-system range reaches 185.59 (%s)" % m)
        check(out["jeans1p_all126_" + m]["dchi2_at_185.59"] < 0.2, "185.59 is not near the all-126 optimum (%s)" % m)
    # (1) zero-parameter sigma* = 185.59 is acceptable on every catalog, both metrics
    bands = {"galaxies": (1.34, 1.57), "milgrom_opt": (62.4, 65.3), "milgrom_rich": (17.6, 22.8),
             "angus_xray": (39.1, 41.3), "kettula_wl": (17.7, 19.2)}
    for fam, (lo, hi) in bands.items():
        row = out["k0_sigma185.59_per_catalog"][fam]
        for m in ("eff", "corr"):
            check(lo - 0.06 <= row[m] <= hi + 0.06, "%s %s chi2 %.2f outside %.2f to %.2f" % (fam, m, row[m], lo, hi))
        check(chi2_dist.sf(row["eff"], row["n"]) > 0.01, "%s chi2 not acceptable at p > 0.01" % fam)
    # part B: the catalogs that pull the threshold below 185
    for key in ("milgrom_both_eff", "milgrom_both_corr", "xray_plus_wl_eff", "xray_plus_wl_corr"):
        check(pb[key]["best"] < 185.59 and pb[key]["dchi2_185.59"] > 5.0, "%s does not pull below 185.59" % key)
    for key in ("milgrom_opt_eff", "milgrom_opt_corr", "milgrom_rich_eff", "milgrom_rich_corr"):
        check(pb[key]["best"] < 185.59, "%s best is not below 185.59" % key)

    if "--verbose" in sys.argv:
        print(json.dumps({"main": out, "which_catalog": pb}, indent=1, sort_keys=True))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    print("RESULT %s: PASS %d of %d checks; trained Hill threshold %d km/s (correlated) and %d km/s (diagonal), not 60.15; "
          "delta chi-squared at 185 on the 120 systems %.1f to %.1f; galaxies alone need >= %.1f km/s; sigma* 185.59 acceptable on all five catalogs" % (
              NAME, COUNT[0], COUNT[0], hc["best_sc"], he["best_sc"], min(d185), max(d185),
              min(out["jeans1p_galaxies_only_eff"]["sc_dchi2le4"][0], out["jeans1p_galaxies_only_corr"]["sc_dchi2le4"][0])))


if __name__ == "__main__":
    main()
