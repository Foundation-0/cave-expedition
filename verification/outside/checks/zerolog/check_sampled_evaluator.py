#!/usr/bin/env python3
"""Independent sampled check of AUDIT-010's measured claims on fresh seeds of the live models.

Checks, on fresh seeds of the live Sabra shell model and the live percolation model in Foundation-0/fractals (the
node dump scripts next to this file run the models and print per-block data; nothing from the sibling team's
Python is used):
  K41: exact interval test on shells 3..8 at 5 standard errors, 16 seeds. F2 (exponent -2/3) and F6 (-2) pass the
       step test but fail the all-pairs test on 16 of 16 seeds; the F3 control (-1) passes on 16 of 16.
  Ripple: plain S2 carries a period-2 ripple (alternating part about 0.30 in log2, significant against a
       smooth-spectrum null on 400 draws); "p=2 beats p=3" is not diagnostic (it holds in about 67 percent of
       ripple-free surrogates); at b = -0.7 the same statistic prefers period 3 on 8 of 8 seeds.
  Percolation: effective dimension per octave over 20 fresh seeds rises at the first octave change (about 6 sigma),
       the second change is not resolved, and the four-ray test refutes log-concavity only through its own noise.
Backs: VERDICTS.md section 1 ("Sabra K41 failure at 5 SE, period-2 ripple, percolation falling refuted (010)",
sampled) and the section 3 row "AUDIT-010 note" (refutes period 3).
Needs: Python 3 standard library, node (any recent version), and a clone of Foundation-0/fractals at draft PR 60
(files turbulence/model.js and critical/model.js). Give its location as the first argument or in FRACTALS_REPO.
Run: python3 -I -B check_sampled_evaluator.py /path/to/fractals     (add --details to print the full JSON)
Time: about 3 minutes (most of it model runs and nulls). Fixed seed: 4242 (printed, used for the nulls;
the model seeds are fixed in the dump calls). Exit 0 only if every check held.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import random
import shutil
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path
from statistics import mean, stdev

HERE = Path(__file__).resolve().parent
SEED = 4242
rng = random.Random(SEED)
DATA: dict = {}


def run_node(script, *args):
    node = shutil.which("node")
    if node is None:
        raise SystemExit("node is required (it runs the live models); not found on PATH")
    done = subprocess.run([node, str(HERE / script), *args], capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise SystemExit(f"node {script} failed: {done.stderr.strip()[:300]}")
    return json.loads(done.stdout)


def make_data(repo):
    turb = str(Path(repo) / "turbulence" / "model.js")
    crit = str(Path(repo) / "critical" / "model.js")
    for f in (turb, crit):
        if not os.path.isfile(f):
            raise SystemExit(f"missing {f}: is the clone at draft PR 60?")

    def cfgs(seeds, lam=None, **run):
        out = []
        for sd in seeds:
            c = {"run": {**run, "seed": sd}}
            if lam is not None:
                c["lambda"] = lam
            out.append(c)
        return json.dumps(out)

    DATA["sabra_base.json"] = run_node("sabra_dump.js", turb, cfgs(range(101, 117)))
    DATA["sabra_lam16.json"] = run_node("sabra_dump.js", turb, cfgs(range(101, 109), lam=1.6, N=26))
    DATA["sabra_b03.json"] = run_node("sabra_dump.js", turb, cfgs(range(101, 109), b=-0.3, c=-0.7))
    DATA["sabra_b07.json"] = run_node("sabra_dump.js", turb, cfgs(range(101, 109), b=-0.7, c=-0.3))
    DATA["perc_fresh.json"] = run_node("perc_dump.js", crit, json.dumps(list(range(8010, 8201, 10))))


def load(name):
    return DATA[name]


def colstats(blocks, n):
    v = [b[n] for b in blocks]
    return mean(v), stdev(v) / math.sqrt(len(v))


# ---------- exact pure-power-law interval test (Theorem A with bracket [alpha, alpha]) ----------
def pl_pass(xs, lo, hi, alpha: Fr, only_steps=False):
    """Exists y_i in [lo_i, hi_i] with y_j/y_i = (x_j/x_i)^alpha for x_i = 2^n_i (n integer): compare in log2-free form
    (y-ratio)^q vs 2^(p dn)."""
    p, q = alpha.numerator, alpha.denominator
    for i, j in itertools.combinations(range(len(xs)), 2):
        if only_steps and j != i + 1:
            continue
        dn = xs[j] - xs[i]
        target = Fr(2) ** (p * dn)
        if (hi[j] / lo[i]) ** q < target or (lo[j] / hi[i]) ** q > target:
            return False
    return True


def alpha_window(xs, lo, hi):
    """Float report only: the set of exponents a pure power law through all boxes can have (empty if lo > hi)."""
    lo_a = max(math.log2(lo[j] / hi[i]) / (xs[j] - xs[i]) for i, j in itertools.combinations(range(len(xs)), 2))
    hi_a = min(math.log2(hi[j] / lo[i]) / (xs[j] - xs[i]) for i, j in itertools.combinations(range(len(xs)), 2))
    return lo_a, hi_a


def boxes(blocks, shells, k):
    lo, hi = [], []
    for n in shells:
        m, se = colstats(blocks, n)
        lo.append(Fr(m - k * se))
        hi.append(Fr(m + k * se))
    return lo, hi


def k41_section(runs):
    shells = list(range(3, 9))
    rows = []
    for r in runs:
        res = {"seed": r["cfg"]["run"]["seed"]}
        for key, ex in (("F2", Fr(-2, 3)), ("F6", Fr(-2)), ("F3", Fr(-1))):
            lo, hi = boxes(r[key], shells, 5)
            res[key] = dict(steps=pl_pass(shells, lo, hi, ex, True), pairs=pl_pass(shells, lo, hi, ex),
                            window=[round(v, 4) for v in alpha_window(shells, [float(x) for x in lo], [float(x) for x in hi])])
        rows.append(res)
    summ = {}
    for key in ("F2", "F6", "F3"):
        summ[key] = dict(steps_pass=sum(r[key]["steps"] for r in rows), pairs_pass=sum(r[key]["pairs"] for r in rows),
                         any_power_law_fits=sum(r[key]["window"][0] <= r[key]["window"][1] for r in rows),
                         windows=[r[key]["window"] for r in rows])
    return dict(n_seeds=len(rows), summary=summ)


# ---------- ripple ----------
def logs(r, key, shells):
    return [math.log2(mean(b[n] for b in r[key])) for n in shells]


def pi_dev(ly, p):
    """Team statistic max |Pi_p - 1| (symmetric in log), computed from log2 values: log2 Pi_p(k) = d_{k+p-1} - d_{k-1}."""
    d = [ly[i + 1] - ly[i] for i in range(len(ly) - 1)]  # log2 step ratios
    vals = [d[k + p - 1] - d[k - 1] for k in range(1, len(d) - p + 1)]
    return max(2 ** abs(v) - 1 for v in vals)


def alt_comp(ly):
    """Alternating part of the second differences of log2 y: mean of (-1)^i dd_i."""
    dd = [ly[i + 1] - 2 * ly[i] + ly[i - 1] for i in range(1, len(ly) - 1)]
    return mean((-1) ** i * v for i, v in enumerate(dd)), dd


def polyfit_eval(xs, ys, deg):
    # least squares via normal equations (small, well-conditioned after centering)
    xm = mean(xs)
    X = [[(x - xm) ** k for k in range(deg + 1)] for x in xs]
    A = [[sum(X[r][i] * X[r][j] for r in range(len(xs))) for j in range(deg + 1)] for i in range(deg + 1)]
    b = [sum(X[r][i] * ys[r] for r in range(len(xs))) for i in range(deg + 1)]
    n = deg + 1
    for c in range(n):
        piv = max(range(c, n), key=lambda i: abs(A[i][c]))
        A[c], A[piv], b[c], b[piv] = A[piv], A[c], b[piv], b[c]
        for i in range(n):
            if i != c:
                f = A[i][c] / A[c][c]
                A[i] = [a - f * cc for a, cc in zip(A[i], A[c])]
                b[i] -= f * b[c]
    coef = [b[i] / A[i][i] for i in range(n)]
    return [sum(coef[k] * (x - xm) ** k for k in range(n)) for x in xs]


def ripple_section(runs, shells, label):
    rows = []
    for r in runs:
        ly = logs(r, "S2", shells)
        lf = logs(r, "F2", shells)
        d1, d2, d3 = (pi_dev(ly, p) for p in (1, 2, 3))
        a, dd = alt_comp(ly)
        # matched null 1: same smooth spectrum (cubic fit to this seed's log2 S2) + per-shell noise at the seed's block SE
        smooth = polyfit_eval(shells, ly, 3)
        se = [colstats(r["S2"], n)[1] / mean(b[n] for b in r["S2"]) / math.log(2) for n in shells]
        null_a, null_p2lt3, null_ratio12 = [], 0, []
        for _ in range(400):
            sy = [s + rng.gauss(0, e) for s, e in zip(smooth, se)]
            null_a.append(abs(alt_comp(sy)[0]))
            n1, n2, n3 = (pi_dev(sy, p) for p in (1, 2, 3))
            null_p2lt3 += n2 < n3
            null_ratio12.append(n1 / n2)
        # matched null 2: shuffle the log2 step ratios (team's kind of null), statistic max_dev at p = 3 and p = 2
        steps = [ly[i + 1] - ly[i] for i in range(len(ly) - 1)]
        ge3 = ge2 = 0
        for _ in range(400):
            s = steps[:]
            rng.shuffle(s)
            yy = [0.0]
            for v in s:
                yy.append(yy[-1] + v)
            ge3 += pi_dev(yy, 3) <= d3   # small max_dev = evidence for period 3
            ge2 += pi_dev(yy, 2) <= d2
        rows.append(dict(seed=r["cfg"]["run"]["seed"], dev=[d1, d2, d3], flux_dev1=pi_dev(lf, 1),
                         alt=a, alt_null_p=(sum(x >= abs(a) for x in null_a) + 1) / 401,
                         smooth_null_frac_p2_lt_p3=null_p2lt3 / 400, smooth_null_ratio12_median=sorted(null_ratio12)[200],
                         shuffle_p_period3=(ge3 + 1) / 401, shuffle_p_period2=(ge2 + 1) / 401,
                         dd=[round(v, 3) for v in dd]))
    alts = [x["alt"] for x in rows]
    return dict(label=label, n=len(rows), shells=[shells[0], shells[-1]],
                mean_dev_p123=[round(mean(x["dev"][i] for x in rows), 3) for i in range(3)],
                frac_p2_lt_p3=sum(x["dev"][1] < x["dev"][2] for x in rows) / len(rows),
                smooth_null_frac_p2_lt_p3=round(mean(x["smooth_null_frac_p2_lt_p3"] for x in rows), 3),
                ratio12_obs_mean=round(mean(x["dev"][0] / x["dev"][1] for x in rows), 2),
                ratio12_smooth_null_median=round(mean(x["smooth_null_ratio12_median"] for x in rows), 2),
                alt_mean=round(mean(alts), 4), alt_se_across_seeds=round(stdev(alts) / math.sqrt(len(alts)), 4),
                alt_null_p_median=round(sorted(x["alt_null_p"] for x in rows)[len(rows) // 2], 4),
                shuffle_p3_values=[round(x["shuffle_p_period3"], 3) for x in rows],
                shuffle_p2_values=[round(x["shuffle_p_period2"], 3) for x in rows],
                flux_flattening=[round(x["dev"][0] / x["flux_dev1"], 1) for x in rows],
                dd_mean=[round(mean(x["dd"][i] for x in rows), 3) for i in range(len(rows[0]["dd"]))])


def sigma_relation(runs):
    """2 (a - c) k_n <Sigma_n> / eps against 1 - (c/a)^n (exact 4/5-law analogue with helicity flux delta = eps)."""
    r0 = runs[0]
    a, c = r0["a"], r0["c"]
    N = r0["N"]
    out = []
    for n in range(1, 10):
        vals = [2 * (a - c) * r["k"][n] * mean(b[n] for b in r["Sig"]) / mean(r["inj"]) for r in runs]
        out.append((n, round(mean(vals), 4), round(stdev(vals) / math.sqrt(len(vals)), 4), round(1 - (c / a) ** n, 4)))
    return dict(a=a, c=c, lam=r0["lambda"], rows=out)


# ---------- percolation ----------
def perc_section():
    data = load("perc_fresh.json")
    Ls = data[0]["Ls"]

    def four_ray(lo, hi, concave):
        # exact: chord conditions on log, written multiplicatively with integer exponents (uniform dyadic grid)
        if concave:
            lo, hi = [1 / h for h in hi], [1 / l for l in lo]
        fails = []
        for i, j, k in itertools.combinations(range(4), 3):
            if hi[i] ** (k - j) * hi[k] ** (j - i) < lo[j] ** (k - i):
                fails.append((i, j, k))
        return fails

    batches = []
    for b in range(4):
        grp = data[5 * b:5 * b + 5]
        lo, hi = [], []
        for i in range(4):
            v = [g["span"][i][0] for g in grp]
            m, se = mean(v), stdev(v) / math.sqrt(5)
            lo.append(Fr(m - 2 * se))
            hi.append(Fr(m + 2 * se))
        batches.append(dict(seeds=[g["seed"] for g in grp], convex_fails=four_ray(lo, hi, False),
                            concave_fails=four_ray(lo, hi, True)))
    # direct estimate from all 20 seeds: effective dimension per octave and its change
    hs = [[math.log2(g["span"][i][0]) for i in range(4)] for g in data]
    deff = [[h[i + 1] - h[i] for i in range(3)] for h in hs]
    dmean = [mean(d[i] for d in deff) for i in range(3)]
    dse = [stdev(d[i] for d in deff) / math.sqrt(len(deff)) for i in range(3)]
    dd = [[d[i + 1] - d[i] for i in range(2)] for d in deff]
    ddm = [mean(x[i] for x in dd) for i in range(2)]
    dds = [stdev(x[i] for x in dd) / math.sqrt(len(dd)) for i in range(2)]
    # false-positive rate of the team's test (5 seeds, +-2 SE, concave refuted) when the truth is an exact power law
    sd_seed = [stdev(g["span"][i][0] for g in data) for i in range(4)]
    mu = [mean(g["span"][i][0] for g in data) for i in range(4)]
    D = (math.log2(mu[3]) - math.log2(mu[0])) / 3
    truth = [mu[0] * 2 ** (D * i) for i in range(4)]
    fp = 0
    for _ in range(2000):
        lo, hi = [], []
        for i in range(4):
            v = [truth[i] + rng.gauss(0, sd_seed[i]) for _ in range(5)]
            m, se = mean(v), stdev(v) / math.sqrt(5)
            lo.append(Fr(max(m - 2 * se, 1e-9)))
            hi.append(Fr(m + 2 * se))
        fp += bool(four_ray(lo, hi, True))
    return dict(Ls=Ls, batches=batches, D_eff_per_octave=[round(x, 4) for x in dmean], D_eff_se=[round(x, 4) for x in dse],
                dD_eff=[round(x, 4) for x in ddm], dD_eff_se=[round(x, 4) for x in dds], target_D=round(91 / 48, 4),
                false_refutation_rate_if_pure_power_law=fp / 2000)


def main():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        repo = sys.argv[1]
    else:
        repo = os.environ.get("FRACTALS_REPO")
    if not repo:
        raise SystemExit("usage: check_sampled_evaluator.py <path to a clone of Foundation-0/fractals at PR 60> "
                         "(or set FRACTALS_REPO)")
    print(f"seed={SEED}")
    make_data(repo)
    base = load("sabra_base.json")
    out = {
        "k41_interval_test_fresh_seeds": k41_section(base),
        "ripple": [ripple_section(base, list(range(2, 10)), "lambda=2 b=-0.5 (team setting), shells 2..9"),
                   ripple_section(load("sabra_lam16.json"), list(range(2, 10)), "lambda=1.6 b=-0.5, shells 2..9"),
                   ripple_section(load("sabra_lam16.json"), list(range(2, 14)), "lambda=1.6 b=-0.5, shells 2..13"),
                   ripple_section(load("sabra_b03.json"), list(range(2, 10)), "lambda=2 b=-0.3 (c/a=-0.7)"),
                   ripple_section(load("sabra_b07.json"), list(range(2, 10)), "lambda=2 b=-0.7 (c/a=-0.3)")],
        "sigma_relation": [sigma_relation(base), sigma_relation(load("sabra_lam16.json")),
                           sigma_relation(load("sabra_b03.json")), sigma_relation(load("sabra_b07.json"))],
        "percolation": perc_section(),
    }
    fails = []

    def need(cond, msg):
        if not cond:
            fails.append(msg)

    k = out["k41_interval_test_fresh_seeds"]["summary"]
    need(k["F2"]["steps_pass"] == 16 and k["F2"]["pairs_pass"] == 0, "F2: expected steps pass and pairs fail on 16 of 16")
    need(k["F6"]["steps_pass"] == 16 and k["F6"]["pairs_pass"] == 0, "F6: expected steps pass and pairs fail on 16 of 16")
    need(k["F3"]["pairs_pass"] == 16, "F3 control: expected pairs pass on 16 of 16")
    rp = out["ripple"][0]
    need(rp["frac_p2_lt_p3"] == 1.0, "team setting: expected p2 < p3 on every seed")
    need(abs(rp["alt_mean"] - 0.30) < 0.01 and rp["alt_null_p_median"] <= 0.0025 + 1e-12,
         "team setting: alternating part not about 0.30 or not significant")
    need(0.6 < rp["smooth_null_frac_p2_lt_p3"] < 0.75, "p2 < p3 in ripple-free surrogates not about two thirds")
    need(out["ripple"][4]["frac_p2_lt_p3"] == 0.0, "b = -0.7: expected period 3 preferred on every seed")
    pc = out["percolation"]
    need(pc["dD_eff"][0] / pc["dD_eff_se"][0] > 5, "percolation: first octave change not above 5 sigma")
    need(abs(pc["dD_eff"][1] / pc["dD_eff_se"][1]) < 2, "percolation: second octave change unexpectedly resolved")
    need(all(b["convex_fails"] == [] for b in pc["batches"]), "percolation: log-convexity refuted in a batch")
    out["failures"] = fails
    if "--details" in sys.argv:
        print(json.dumps(out, indent=1))
    verdict = "OK" if not fails else "FAIL"
    print(f"ZEROLOG_SAMPLED_EVALUATOR {verdict}: K41 all-pairs pass F2 {k['F2']['pairs_pass']}/16 F6 {k['F6']['pairs_pass']}/16 "
          f"F3 {k['F3']['pairs_pass']}/16; period-2 alternating part {rp['alt_mean']} +- {rp['alt_se_across_seeds']}, "
          f"p2<p3 {rp['frac_p2_lt_p3']} observed vs {rp['smooth_null_frac_p2_lt_p3']} in smooth surrogates; "
          f"b=-0.7 p2<p3 {out['ripple'][4]['frac_p2_lt_p3']}; percolation dD_eff {pc['dD_eff'][0]} +- {pc['dD_eff_se'][0]}, "
          f"{pc['dD_eff'][1]} +- {pc['dD_eff_se'][1]}; failures {len(fails)}")
    for f in fails:
        print("FAILED:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
