#!/usr/bin/env python3
"""Advocate recheck of AUDIT-010 sampled Sabra claims: the period-3 statement and the seed-7 number.

Checks, with own statistics on the live Sabra model run through sabra_dump_seeds.js (seeds 1, 7 and 101..114 at
b = -0.5, a replay of seeds 1 and 7, and seeds 201..206 at b = -0.7):
  - two node runs of seeds 1 and 7 are bit identical;
  - the shipped statistic max|Pi_p - 1| on S2 over shells 2..9 gives 0.5639 for seed 7 at p = 3 (the study note says
    0.659; no shell window tried gives 0.659) and 0.4848 for seed 1;
  - p=2 beats p=1 and p=3 on 16 of 16 seeds, but "p=2 beats p=3" also holds in two thirds of ripple-free surrogates,
    and an injected period-3 modulation of 5 and 10 percent leaves it true on 16 of 16 seeds (no power against
    period 3, so "refutes period 3" must be reworded);
  - the ratio-shuffle null the note describes (never shipped) gives 0.443 for seed 1 and 1.000 for seed 7;
  - at b = -0.7 the same statistic prefers period 3 on 6 of 6 fresh seeds.
Backs: VERDICTS.md section 3 rows "AUDIT-010 note" (refutes period 3) and "fractals 60 note" (seed 7 value 0.659,
shuffle p-values); section 1 period-2 ripple row. Rulings F4 and F5 in RECHECK-1.json.
Needs: Python 3 standard library, node (any recent version), and a clone of Foundation-0/fractals at draft PR 60.
Give its location as the first argument or in FRACTALS_REPO.
Run: python3 -I -B check_sampled_advocate.py /path/to/fractals     (add --details to print the full JSON)
Time: about 1 minute. Fixed seeds: 777 for the nulls (printed); model seeds are fixed in the dump calls.
Exit 0 only if every check held.
"""
import json
import math
import os
import random
import shutil
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
    return cond


def run_node(script, *args):
    node = shutil.which("node")
    if node is None:
        raise SystemExit("node is required (it runs the live model); not found on PATH")
    done = subprocess.run([node, str(HERE / script), *args], capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise SystemExit(f"node {script} failed: {done.stderr.strip()[:300]}")
    return json.loads(done.stdout)


def mean(v):
    return sum(v) / len(v)


def sd(v):
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


# ---- the team's statistic, own implementation (exact rationals, as the team does) ----
def dec(v, sig=10):
    e = max(6, -math.floor(math.log10(v)) + sig)
    G = 10 ** e
    return Fr(round(v * G), G)


def max_dev_exact(ys, p):
    ys = [dec(v) for v in ys]
    R = [ys[k + 1] * ys[k - 1] / (ys[k] * ys[k]) for k in range(1, len(ys) - 1)]
    best = Fr(0)
    for i in range(len(R) - p + 1):
        pr = Fr(1)
        for j in range(p):
            pr *= R[i + j]
        d = pr - 1 if pr >= 1 else 1 / pr - 1
        best = max(best, d)
    return float(best)


def max_dev_log(ly, p):
    """Same statistic from natural-log values: log Pi_p(k) = d_{k+p-1} - d_{k-1}, d = steps of log y."""
    d = [ly[i + 1] - ly[i] for i in range(len(ly) - 1)]
    return max(math.exp(abs(d[k + p - 1] - d[k - 1])) - 1 for k in range(1, len(d) - p + 1))


def polyfit(xs, ys, deg):
    xm = mean(xs)
    X = [[(x - xm) ** k for k in range(deg + 1)] for x in xs]
    n = deg + 1
    A = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]
    b = [sum(X[r][i] * ys[r] for r in range(len(xs))) for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda i: abs(A[i][c]))
        A[c], A[piv], b[c], b[piv] = A[piv], A[c], b[piv], b[c]
        for i in range(n):
            if i != c:
                f = A[i][c] / A[c][c]
                A[i] = [a - f * cc for a, cc in zip(A[i], A[c])]
                b[i] -= f * b[c]
    co = [b[i] / A[i][i] for i in range(n)]
    return [sum(co[k] * (x - xm) ** k for k in range(n)) for x in xs]


def lstsq(X, y):
    n = len(X[0])
    A = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]
    b = [sum(X[r][i] * y[r] for r in range(len(X))) for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda i: abs(A[i][c]))
        A[c], A[piv], b[c], b[piv] = A[piv], A[c], b[piv], b[c]
        for i in range(n):
            if i != c:
                f = A[i][c] / A[c][c]
                A[i] = [a - f * cc for a, cc in zip(A[i], A[c])]
                b[i] -= f * b[c]
    return [b[i] / A[i][i] for i in range(n)]


SHELLS = list(range(2, 10))


def per_seed(run):
    S2 = [run["S2"][n] for n in SHELLS]
    nb = run["nb"]
    se_rel = [sd([blk[n] for blk in run["S2b"]]) / math.sqrt(nb) / run["S2"][n] for n in SHELLS]
    return S2, se_rel


def shuffle_p(ly, p, rng, nnull, mode):
    """Team-style ratio-shuffle null. mode 'steps': permute the log step ratios; mode 'cross': permute the
    cross-ratios R_k (log second differences) and rebuild. Returns (P(null <= obs), P(null >= obs))."""
    obs = max_dev_log(ly, p)
    d = [ly[i + 1] - ly[i] for i in range(len(ly) - 1)]
    dd = [d[i + 1] - d[i] for i in range(len(d) - 1)]
    le = ge = 0
    for _ in range(nnull):
        if mode == "steps":
            s = d[:]
            rng.shuffle(s)
        else:
            t = dd[:]
            rng.shuffle(t)
            s = [d[0]]
            for v in t:
                s.append(s[-1] + v)
        yy = [0.0]
        for v in s:
            yy.append(yy[-1] + v)
        m = max_dev_log(yy, p)
        le += m <= obs
        ge += m >= obs
    return (le + 1) / (nnull + 1), (ge + 1) / (nnull + 1)


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.environ.get("FRACTALS_REPO")
    if not repo:
        raise SystemExit("usage: check_sampled_advocate.py <path to a clone of Foundation-0/fractals at PR 60> "
                         "(or set FRACTALS_REPO)")
    model = os.path.join(repo, "turbulence", "model.js")
    if not os.path.isfile(model):
        raise SystemExit(f"missing {model}: is the clone at draft PR 60?")
    print("seed=777")
    runA = run_node("sabra_dump_seeds.js", model, ",".join(["1", "7"] + [str(v) for v in range(101, 115)]))
    runB = run_node("sabra_dump_seeds.js", model, "1,7")
    b07 = run_node("sabra_dump_seeds.js", model, ",".join(str(v) for v in range(201, 207)), "-0.7")
    out = {}
    # determinism: seeds 1 and 7 identical across two independent node invocations
    out["replay_bit_identical_seed1_seed7"] = all(runA[s]["S2"] == runB[s]["S2"] and runA[s]["F2"] == runB[s]["F2"] for s in ("1", "7"))
    check(out["replay_bit_identical_seed1_seed7"], "node replay differs")

    # F5: the numbers for seeds 1 and 7
    f5 = {}
    for s in ("1", "7"):
        S2 = [runA[s]["S2"][n] for n in SHELLS]
        F2 = [runA[s]["F2"][n] for n in SHELLS]
        f5[s] = dict(S2_max_dev_p123=[round(max_dev_exact(S2, p), 6) for p in (1, 2, 3)],
                     F2_max_dev_p1=round(max_dev_exact(F2, 1), 6))
        # look for any nearby window/statistic that gives 0.659 (seed 7) or 0.485 (seed 1)
        alts = {}
        for lo in (1, 2, 3):
            for hi in (8, 9, 10, 11):
                ys = [runA[s]["S2"][n] for n in range(lo, hi + 1)]
                alts[f"S2 shells {lo}..{hi}"] = round(max_dev_exact(ys, 3), 4)
                ysf = [runA[s]["F2"][n] for n in range(lo, hi + 1)]
                alts[f"F2 shells {lo}..{hi}"] = round(max_dev_exact(ysf, 3), 4)
        f5[s]["p3_variants"] = alts
    out["F5"] = f5

    # F4: diagnostics over 16 seeds of the team's own setting
    rng = random.Random(777)
    seeds = sorted(runA, key=int)
    rows = []
    for s in seeds:
        S2, se = per_seed(runA[s])
        ly = [math.log(v) for v in S2]
        d1, d2, d3 = (max_dev_log(ly, p) for p in (1, 2, 3))
        # smooth ripple-free surrogates: fitted polynomial of degree 1, 2, 3 in n, plus Gaussian noise at block SE
        frac = {}
        for deg in (1, 2, 3):
            sm = polyfit(SHELLS, ly, deg)
            hits = 0
            for _ in range(400):
                sy = [m + rng.gauss(0, e) for m, e in zip(sm, se)]
                hits += max_dev_log(sy, 2) < max_dev_log(sy, 3)
            frac[deg] = hits / 400
        # injected period-3 modulation: does p=2 < p=3 still hold? (power of the team's diagnostic)
        inj = {}
        for A in (0.05, 0.10, 0.20):
            pat = [1, -0.5, -0.5]
            ly3 = [v + math.log(1 + A * pat[i % 3]) for i, v in enumerate(ly)]
            inj[A] = max_dev_log(ly3, 2) < max_dev_log(ly3, 3)
        ps_steps = shuffle_p(ly, 3, rng, 200, "steps")
        ps_cross = shuffle_p(ly, 3, rng, 200, "cross")
        # period components of the second differences of log S2 (6 values): fit const + linear + (-1)^j + cos/sin(2 pi j/3)
        d = [ly[i + 1] - ly[i] for i in range(len(ly) - 1)]
        dd = [d[i + 1] - d[i] for i in range(len(d) - 1)]
        X = [[1.0, j, (-1) ** j, math.cos(2 * math.pi * j / 3), math.sin(2 * math.pi * j / 3)] for j in range(len(dd))]
        co = lstsq(X, dd)
        rows.append(dict(seed=int(s), dev=[d1, d2, d3], p2_lt_p3=d2 < d3, p2_lt_p1=d2 < d1,
                         null_frac_p2_lt_p3=frac, injected_p3_still_p2_lt_p3=inj,
                         shuffle_p3_steps=ps_steps, shuffle_p3_cross=ps_cross,
                         alt=co[2], p3amp=math.hypot(co[3], co[4]), p3c=co[3], p3s=co[4],
                         se_rel=se))
    n = len(rows)
    alt = [r["alt"] for r in rows]
    c3 = [r["p3c"] for r in rows]
    s3 = [r["p3s"] for r in rows]
    out["F4"] = dict(
        n_seeds=n, shells=[SHELLS[0], SHELLS[-1]],
        mean_dev_p123=[round(mean([r["dev"][i] for r in rows]), 4) for i in range(3)],
        seeds_p2_lt_p3=sum(r["p2_lt_p3"] for r in rows), seeds_p2_lt_p1=sum(r["p2_lt_p1"] for r in rows),
        smooth_null_frac_p2_lt_p3_by_degree={deg: round(mean([r["null_frac_p2_lt_p3"][deg] for r in rows]), 3) for deg in (1, 2, 3)},
        injected_period3_seeds_still_p2_lt_p3={A: sum(r["injected_p3_still_p2_lt_p3"][A] for r in rows) for A in (0.05, 0.10, 0.20)},
        shuffle_p3_steps_le=[round(r["shuffle_p3_steps"][0], 3) for r in rows],
        shuffle_p3_cross_le=[round(r["shuffle_p3_cross"][0], 3) for r in rows],
        shuffle_p3_steps_ge=[round(r["shuffle_p3_steps"][1], 3) for r in rows],
        median_rel_block_SE=round(sorted(x for r in rows for x in r["se_rel"])[len(rows) * 4], 5),
        alt_coef_mean_se=[round(mean(alt), 4), round(sd(alt) / math.sqrt(n), 4)],
        period3_cos_mean_se=[round(mean(c3), 4), round(sd(c3) / math.sqrt(n), 4)],
        period3_sin_mean_se=[round(mean(s3), 4), round(sd(s3) / math.sqrt(n), 4)],
        seed1=dict(dev=[round(v, 4) for v in rows[0]["dev"]], shuffle_steps=rows[0]["shuffle_p3_steps"], shuffle_cross=rows[0]["shuffle_p3_cross"]),
    )
    # b = -0.7 (c/a = -0.3): a Sabra variant with no period-3 mechanism
    r7 = []
    for s in sorted(b07, key=int):
        S2 = [b07[s]["S2"][n] for n in SHELLS]
        ly = [math.log(v) for v in S2]
        r7.append([max_dev_log(ly, p) for p in (1, 2, 3)])
    out["b_minus_0p7"] = dict(n_seeds=len(r7), seeds_p3_lt_p2=sum(r[2] < r[1] for r in r7),
                              mean_dev_p123=[round(mean([r[i] for r in r7]), 4) for i in range(3)])
    f5, f4, b7 = out["F5"], out["F4"], out["b_minus_0p7"]
    check(f5["7"]["S2_max_dev_p123"][2] == 0.563938, "seed 7 p=3 value is not 0.563938")
    check(round(f5["1"]["S2_max_dev_p123"][2], 4) == 0.4848, "seed 1 p=3 value is not 0.4848")
    check(not any(abs(v - 0.659) < 0.0005 for v in f5["7"]["p3_variants"].values()), "a window gives 0.659 for seed 7")
    check(f4["seeds_p2_lt_p3"] == 16 and f4["seeds_p2_lt_p1"] == 16, "p=2 not best on 16 of 16 seeds")
    check(f4["injected_period3_seeds_still_p2_lt_p3"][0.05] == 16 and f4["injected_period3_seeds_still_p2_lt_p3"][0.1] == 16,
          "injected period 3 changed the verdict at 5 or 10 percent")
    check(0.6 < f4["smooth_null_frac_p2_lt_p3_by_degree"][2] < 0.75, "surrogate fraction not about two thirds")
    check(b7["seeds_p3_lt_p2"] == b7["n_seeds"] == 6, "b = -0.7 does not prefer period 3 on 6 of 6")
    out["fails"] = FAILS
    if "--details" in sys.argv:
        print(json.dumps(out, indent=1, sort_keys=True))
    verdict = "OK" if not FAILS else "FAIL"
    print(f"ZEROLOG_SAMPLED_ADVOCATE {verdict}: replay identical {out['replay_bit_identical_seed1_seed7']}; "
          f"seed 7 p=3 dev {f5['7']['S2_max_dev_p123'][2]} (note says 0.659), seed 1 {f5['1']['S2_max_dev_p123'][2]}; "
          f"p2<p3 on {f4['seeds_p2_lt_p3']}/16, surrogates {f4['smooth_null_frac_p2_lt_p3_by_degree']}, injected 5%/10%/20% "
          f"{f4['injected_period3_seeds_still_p2_lt_p3']}; shuffle p seed 1 {f4['seed1']['shuffle_steps'][0]:.3f}; "
          f"b=-0.7 period 3 preferred {b7['seeds_p3_lt_p2']}/{b7['n_seeds']}; failures {len(FAILS)}")
    for f in FAILS[:10]:
        print("FAILED:", f)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
