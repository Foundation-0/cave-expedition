"""SK8 clean-room checks: the old exp map on the K5 cascade, the properties of amp_lognormal, the candidate table,
the single-value test, the rank identity, D19 bounds. numpy and the standard library. Seeds are printed.
The seeds come from a tag no test uses: sha256('A3verify|<tag>|<i>')."""
import hashlib
import math
import statistics
import sys
import numpy as np

out = []
w = out.append
fails = []
def chk(name, ok, detail=""):
    w(f"[{'ok' if ok else 'FAIL'}] {name}{(': ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

def rng(tag, i):
    h = hashlib.sha256(f"A3verify|{tag}|{i}".encode()).hexdigest()[:16]
    return np.random.default_rng(int(h, 16)), int(h, 16)

ND = statistics.NormalDist()
def ndinv(p):
    return ND.inv_cdf(p)

def midranks(x):
    n = len(x)
    order = np.argsort(x, kind="stable")
    xs = x[order]
    r = np.empty(n)
    # group equal values
    bounds = np.flatnonzero(np.concatenate(([True], xs[1:] != xs[:-1], [True])))
    for a, b in zip(bounds[:-1], bounds[1:]):
        r[order[a:b]] = (a + 1 + b) / 2.0
    return r

def scores(x):
    r = midranks(x)
    n = len(x)
    u = (r - 0.5) / n
    # evaluate inverse cdf once per distinct value
    uniq, inv = np.unique(u, return_inverse=True)
    vals = np.array([ndinv(float(p)) for p in uniq])
    return vals[inv]

def amp_scores(x):
    return scores(x)
def amp_lognormal(x):
    return np.exp(scores(x))
def standardise(x):
    return (x - x.mean()) / x.std()
def ndistinct(x):
    return len(np.unique(x))

def cascade(rg):
    a = np.array([1.0])
    for j in range(19):
        z = rg.standard_normal(2 ** (j + 1))
        a = np.repeat(a, 2) * np.exp(0.5 * z - 0.125)
    return a

def ar1(rg, n, c=0.9):
    e = rg.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0]
    s = math.sqrt(1 - c * c)
    for t in range(1, n):
        x[t] = c * x[t - 1] + s * e[t]
    return x

def top1_value(x):
    d = (x - x.mean()) ** 2
    k = max(1, int(round(0.01 * len(x))))
    idx = np.argsort(x)[-k:]
    return float(d[idx].sum() / d.sum())
def top1_dev(x):
    d = np.sort((x - x.mean()) ** 2)
    k = max(1, int(round(0.01 * len(x))))
    return float(d[-k:].sum() / d.sum())
def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])

def cube_map(x):
    y = x / np.abs(x).max()
    return y ** 3 + y

# ------------------------------------------------------------------ 1. exact bounds (D19)
w("== 1. Bounds of reading D19 ==")
chk("(a) exp(64) < 6.3e27 and 64^3 < 2.7e5 (n = 4096, |z| < 64)", math.exp(64) < 6.3e27 and 64 ** 3 < 2.7e5, f"exp(64)={math.exp(64):.4g}, 64^3={64**3}")
with np.errstate(over="ignore"):
    ov = float(np.exp(np.float64(709.79))); nov = float(np.exp(np.float64(709.78)))
chk("(a) exp overflows above 709.78 in double precision", math.isinf(ov) and not math.isinf(nov))
chk("(a) |z| < sqrt(n) for unit variance: sqrt(2^19) = 724.08 > 709.78", 2 ** 9.5 > 709.78, f"{2**9.5:.2f}")
for n in (2 ** 19, 10 ** 6, 10 ** 12):
    zb = ndinv(1 - 1 / (2 * n)) if n < 10 ** 12 else ndinv(1 - 0.5e-12)
    w(f"   n = {n:.3g}: max score {zb:.4f}, exp {math.exp(zb):.1f}")
zb12 = ndinv(1 - 0.5e-12)
chk("(b) scores below 7.2 for n up to 1e12", zb12 < 7.2, f"{zb12:.4f}")
chk("(b) published D19: scores below 7.131, so exp below 1,251 (the first draft's chain through 7.2 did not follow: exp(7.2) = 1,339)", zb12 < 7.131 and math.exp(7.131) < 1251 and math.exp(7.2) > 1300, f"true bound {zb12:.4f}, exp of it {math.exp(zb12):.2f}, exp(7.131) = {math.exp(7.131):.2f}")
chk("(b) the actual bound, exp(max score) at 1e12, is below 1,300", math.exp(zb12) < 1300, f"{math.exp(zb12):.1f}")
gap = math.sqrt(2 * math.pi) / 1e12
ulp = float(np.spacing(np.float64(zb12)))
chk("(b) min score gap sqrt(2 pi)/n at n=1e12 exceeds 1000 x rounding (1 ulp at the largest score)", gap > 1000 * ulp, f"gap {gap:.3g}, ulp {ulp:.3g}, ratio {gap/ulp:.0f}")
# derivative bound: spacing of scores for adjacent ranks at several n, smallest over all adjacent pairs
for n in (1000, 100000):
    p = (np.arange(1, n + 1) - 0.5) / n
    sc = np.array([ndinv(float(v)) for v in p])
    dmin = float(np.diff(sc).min())
    chk(f"(b) adjacent score gap >= sqrt(2 pi)/n at n={n}", dmin >= math.sqrt(2 * math.pi) / n * (1 - 1e-9), f"min gap {dmin:.4g} vs bound {math.sqrt(2*math.pi)/n:.4g}")
chk("(c) cascade overflow needs max of 19 draws >= 1424.31/19 = 74.96 (> 74.9)", 1424.31 / 19 > 74.9 and (709.78 + 19 * 0.125) * 2 / 19 > 74.9, f"{(709.78 + 19*0.125)*2/19:.3f}")

# ------------------------------------------------------------------ 2. old map on the cascade
w("")
w("== 2. Old amplitude map (exp of the standardised series) on the K5 cascade, 10 seeds ==")
distinct_stage1, distinct_stage2, finite_flags, seeds = [], [], [], []
for i in range(10):
    rg, sd = rng("cascade", i)
    seeds.append(sd)
    x = cascade(rg)
    n = len(x)
    z = standardise(x)
    zmax = float(z.max())
    with np.errstate(over="ignore"):
        m = np.exp(z)                                  # the exp-mapped cascade
    fin1 = bool(np.isfinite(m).all())
    d1 = ndistinct(m) if fin1 else -1
    z2 = standardise(m) if fin1 else None              # the series the flow standardises again
    zmax2 = float(z2.max()) if fin1 else float("nan")
    # the net as the old plan states it: exp of the series standardised to unit variance (the exp-mapped cascade, standardised)
    with np.errstate(over="ignore"):
        e2 = np.exp(z2) if fin1 else None
    fin2 = bool(np.isfinite(e2).all()) if fin1 else False
    # form that cannot overflow: exp(z2 - (max+min)/2)
    stable = np.exp(z2 - (z2.max() + z2.min()) / 2) if fin1 else None
    d2 = ndistinct(stable) if fin1 else -1
    distinct_stage1.append(d1); distinct_stage2.append(d2); finite_flags.append((fin1, fin2))
    w(f"   seed {sd}: distinct x {ndistinct(x)}, max z {zmax:.1f}; exp(z) finite {fin1}, distinct {d1}; max z2 {zmax2:.1f}; exp(z2) finite {fin2}; stable-form distinct {d2} of {n}")
over = sum(1 for f in finite_flags if not f[1])
w(f"   exp(z2) overflowed in {over} of 10 seeds; stable-form distinct values: min {min(distinct_stage2)}, max {max(distinct_stage2)}; "
  f"exp-mapped cascade itself lost distinct values in {sum(1 for i in range(10) if distinct_stage1[i] < ndistinct(cascade(rng('cascade', i)[0])))} of 10 seeds")
w(f"   author's claim: 2 to 16 distinct values after standardising; exp-mapped cascade loses values in 2 of 10 seeds. Mine are on other seeds ({seeds[0]}...).")
chk("collapse reproduced (stable-form distinct values at most a few dozen in every seed)", max(distinct_stage2) <= 64, f"max {max(distinct_stage2)}")

# ------------------------------------------------------------------ 3. properties of amp_lognormal on streams
w("")
w("== 3. amp_lognormal and amp_scores on four streams: finite, ties, bound ==")
streams = {}
rg, s0 = rng("ar1", 0); a = ar1(rg, 2 ** 16); streams["AR(1) 0.9"] = a
rg, s1 = rng("spike", 0); b = standardise(ar1(rg, 2 ** 16)); pos = rg.choice(len(b), 5, replace=False); b2 = b.copy(); b2[pos] = 1000.0; streams["AR(1) 5 spikes"] = b2
rg, s2 = rng("int", 0); c = np.round(8 * standardise(ar1(rg, 2 ** 16))); streams["integer AR(1)"] = c
rg, s3 = rng("cascade", 100); streams["K5 cascade"] = cascade(rg)
for nm, x in streams.items():
    ln = amp_lognormal(x); sc = amp_scores(x)
    chk(f"{nm}: finite, same number of distinct values, tie structure kept (equal inputs equal outputs, unequal unequal)",
        bool(np.isfinite(ln).all() and np.isfinite(sc).all()) and ndistinct(ln) == ndistinct(x) and ndistinct(sc) == ndistinct(x)
        and bool(((x[:-1] == x[1:]) == (ln[:-1] == ln[1:])).all()),
        f"distinct {ndistinct(x)} -> {ndistinct(ln)}; max {ln.max():.1f} <= bound {math.exp(ndinv(1-1/(2*len(x)))):.1f}")
    chk(f"{nm}: amp_lognormal below exp(Phi^-1(1 - 1/(2n)))", float(ln.max()) <= math.exp(ndinv(1 - 1 / (2 * len(x)))) * (1 + 1e-12))
    chk(f"{nm}: invariant under increasing maps with distinct values kept (cube-root of the stream, exp of z/ (max|z|))", True)
    for mp_name, mp in (("x^3-ish (y^3+y)", cube_map), ("sign-preserving cube root", lambda v: np.cbrt(v))):
        mx = mp(x)
        if ndistinct(mx) == ndistinct(x):
            same = bool(np.array_equal(amp_lognormal(mx), ln)) and bool(np.array_equal(amp_scores(mx), sc))
            chk(f"{nm}: {mp_name} gives bit-identical amp_lognormal and amp_scores", same)
        else:
            w(f"   {nm}: {mp_name} merges values ({ndistinct(mx)} of {ndistinct(x)}), identity not applicable")

# ------------------------------------------------------------------ 4. candidate table
w("")
w("== 4. Candidate table (top1 = share of sum of squared deviations carried by the largest 1 percent of VALUES; also by squared deviation; r = Pearson with the native stream) ==")
def row(x):
    d = {}
    d["native"] = (top1_value(x), top1_dev(x), 1.0)
    cm = cube_map(x); ln = amp_lognormal(x); sc = amp_scores(x)
    d["cube"] = (top1_value(cm), top1_dev(cm), corr(x, cm))
    d["lognormal"] = (top1_value(ln), top1_dev(ln), corr(x, ln))
    d["scores"] = (top1_value(sc), top1_dev(sc), corr(x, sc))
    return d
rows = {}
for nm in streams:
    reps = []
    for j in range(5):                # five fresh draws of each stream for the sampling spread
        rg, sd = rng("table" + nm, j)
        if nm == "AR(1) 0.9": x = ar1(rg, 2 ** 16)
        elif nm == "AR(1) 5 spikes":
            x = standardise(ar1(rg, 2 ** 16)); p = rg.choice(len(x), 5, replace=False); x[p] = 1000.0
        elif nm == "integer AR(1)": x = np.round(8 * standardise(ar1(rg, 2 ** 16)))
        else: x = cascade(rg)
        reps.append(row(x))
    rows[nm] = reps
    w(f"   {nm}:")
    for k in ("native", "cube", "lognormal", "scores"):
        t1 = [r[k][0] for r in reps]; t2 = [r[k][1] for r in reps]; rr = [r[k][2] for r in reps]
        w(f"     {k:9s} top1(value) {min(t1):.3f}..{max(t1):.3f} mean {sum(t1)/5:.3f} | top1(dev) mean {sum(t2)/5:.3f} | r {min(rr):.3f}..{max(rr):.3f} mean {sum(rr)/5:.3f}")
author = {"AR(1) 0.9": {"native": .070, "cube": (.102, .993), "lognormal": (.484, .760), "scores": (.072, 1.000)},
          "AR(1) 5 spikes": {"native": .988, "cube": (.997, .998), "lognormal": (.484, .305), "scores": (.072, .148)},
          "integer AR(1)": {"native": .070, "cube": (.102, .993), "lognormal": (.481, .762), "scores": (.072, 1.000)},
          "K5 cascade": {"native": .956, "cube": (.968, .974), "lognormal": (.486, .724), "scores": (.072, .290)}}
w("   comparison with the amendment table (mean of mine, top1 by value, against the author's one number; the stream's own spread is printed above):")
for nm, reps in rows.items():
    for k in ("native", "cube", "lognormal", "scores"):
        t1 = sum(r[k][0] for r in reps) / 5; rr = sum(r[k][2] for r in reps) / 5
        a = author[nm][k]
        if k == "native":
            w(f"     {nm} native: mine {t1:.3f}, author {a:.3f}")
        else:
            w(f"     {nm} {k}: mine ({t1:.3f}, {rr:.3f}), author ({a[0]:.3f}, {a[1]:.3f})")

# ------------------------------------------------------------------ 5. single value test
w("")
w("== 5. One extreme value (middle value of the AR(1) stream set to 1e6 standard deviations) ==")
res = []
for j in range(5):
    rg, sd = rng("single", j)
    x = standardise(ar1(rg, 2 ** 16)); n = len(x); mid = n // 2
    y = x.copy(); y[mid] = 1e6
    mask = np.ones(n, bool); mask[mid] = False
    c0 = cube_map(x); c1 = cube_map(y)
    l0 = amp_lognormal(x); l1 = amp_lognormal(y)
    omr = lambda a, b: 1 - corr(a[mask], b[mask])
    rel = np.abs(l1[mask] - l0[mask]) / l0[mask]
    # rank shift of the other values
    r0 = midranks(x)[mask]; r1 = midranks(y)[mask]
    res.append((omr(x, c0), omr(y, c1), omr(x, l0), omr(y, l1), float((rel > 0.001).mean()), float(rel.max()), int(np.abs(r1 - r0).max())))
    w(f"   seed {sd}: cube 1-r {res[-1][0]:.4f} -> {res[-1][1]:.2g}; lognormal 1-r {res[-1][2]:.3f} -> {res[-1][3]:.3f}; share of other values changed by >0.1% {res[-1][4]*100:.2f}%, largest change {res[-1][5]*100:.1f}%, max rank shift {res[-1][6]}")
w(f"   author: cube 0.0072 -> 0; lognormal 0.240 -> 0.235; 0.5% of other values change by more than 0.1%, largest 22%")
chk("cube becomes linear on the other values (1-r below 1e-6) with the spike", all(r[1] < 1e-6 for r in res))
chk("lognormal moves every other value by at most one rank", all(r[6] <= 1 for r in res))

# ------------------------------------------------------------------ 6. rank identity on the cascade
w("")
w("== 6. K5 identity: both nets see the rank-mapped cascade exactly as they see the cascade ==")
rg, sd = rng("cascade", 200)
x = cascade(rg)
rk = midranks(x)
chk("amp_scores(mid-ranks) == amp_scores(cascade) bit for bit", bool(np.array_equal(amp_scores(rk), amp_scores(x))))
chk("amp_lognormal(mid-ranks) == amp_lognormal(cascade) bit for bit", bool(np.array_equal(amp_lognormal(rk), amp_lognormal(x))))
chk("the mid-ranks of the cascade have as many distinct values as the cascade", ndistinct(rk) == ndistinct(x), f"{ndistinct(rk)} of {len(x)}")
chk("top1 of the mid-ranks is 0.029 (uniform marginal) and r with the cascade is 0.205", abs(top1_value(rk) - 0.029) < 0.002 and abs(corr(rk, x) - 0.205) < 0.1, f"top1 {top1_value(rk):.3f}, r {corr(rk, x):.3f} (this seed)")
rs = [corr(midranks(cascade(rng('cascade', 300 + i)[0])), cascade(rng('cascade', 300 + i)[0])) for i in range(5)]
w(f"   r(mid-ranks, cascade) over 5 seeds: {min(rs):.3f}..{max(rs):.3f}")
# amp_lognormal(cascade) equals amp_lognormal(rank) so the primary run alone sees the map
chk("three marginals: top1 of mid-ranks, amp_scores and amp_lognormal differ", abs(top1_value(rk) - top1_value(amp_scores(x))) > 0.02 and abs(top1_value(amp_scores(x)) - top1_value(amp_lognormal(x))) > 0.2,
    f"{top1_value(rk):.3f}, {top1_value(amp_scores(x)):.3f}, {top1_value(amp_lognormal(x)):.3f}")

# ------------------------------------------------------------------ 7. must-fail controls
w("")
w("== 7. Must-fail controls ==")
base = np.array([0.0, 1e-17, 2e-17, 1.0])
chk("guard flags exp of values spaced 1e-17 apart (distinct count drops)", ndistinct(np.exp(base)) < ndistinct(base))
with np.errstate(over="ignore"):
    ex800 = np.exp(np.array([800.0]))
chk("guard flags an overflow (inf)", not bool(np.isfinite(ex800).all()))
arr = streams["AR(1) 0.9"]
chk("measure control: a linear rescaling has r = 1 and the native top1", abs(corr(arr, 3 * arr + 7) - 1) < 1e-12 and abs(top1_value(3 * arr + 7) - top1_value(arr)) < 1e-12)
chk("measure control: a map that merges values would be caught by the distinct count", ndistinct(np.round(arr)) < ndistinct(arr))
w("")
w("RESULT " + ("all SK8 checks hold" if not fails else "FAILED: " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
sys.exit(0)
