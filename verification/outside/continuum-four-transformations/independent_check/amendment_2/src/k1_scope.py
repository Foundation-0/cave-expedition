"""B5 check: representability guard on all 9 K2 classes in 3 versions at 4,096, 2,048 and 1,024 samples, 20 seeds, three comparison maps
on y = x / max|x| (y^3 + y, exp(y), ranks of x). Also the old unrescaled maps, and whether the rescaling itself can merge values.
Classes from the plan text (section 10). numpy only. No bare assert. Seeds are printed."""
import sys
import numpy as np

FAILS = []
SEEDS = 20
LENGTHS = (4096, 2048, 1024)


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def ar1(rng, n, c):
    e = rng.standard_normal(n) * np.sqrt(1 - c * c)
    x = np.empty(n)
    x[0] = rng.standard_normal()
    for t in range(1, n):
        x[t] = c * x[t - 1] + e[t]
    return x


def powerlaw(rng, n, slope):
    f = np.fft.rfftfreq(n)[1:]
    amp = f ** (-slope / 2.0)
    ph = rng.uniform(0, 2 * np.pi, len(f))
    sp = np.concatenate(([0.0], amp * np.exp(1j * ph)))
    return np.fft.irfft(sp, n=n)


def sines(rng, n):
    t = np.arange(n)
    x = rng.standard_normal(n)
    for f in (0.0137, 0.0781, 0.2113):
        x = x + np.cos(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))
    return x


def std(x):
    return (x - x.mean()) / x.std()


CLASSES = {
    "white": lambda r, n: r.standard_normal(n),
    "ar1_0.5": lambda r, n: ar1(r, n, 0.5),
    "ar1_0.9": lambda r, n: ar1(r, n, 0.9),
    "ar1_0.99": lambda r, n: ar1(r, n, 0.99),
    "pl_1": lambda r, n: powerlaw(r, n, 1),
    "pl_2": lambda r, n: powerlaw(r, n, 2),
    "sines3": sines,
    "g2": lambda r, n: ar1(r, n, 0.9) ** 2,
    "absh": lambda r, n: np.abs(ar1(r, n, 0.99)),
}


def ndistinct(x):
    return len(np.unique(x))


def midranks(x):
    n = len(x)
    order = np.argsort(x, kind="stable")
    xs = x[order]
    r = np.empty(n)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return r


def maps_new(x):
    y = x / np.max(np.abs(x))
    return {"y^3+y": y ** 3 + y, "exp(y)": np.exp(y), "ranks": midranks(x)}


def maps_old(x):
    with np.errstate(over="ignore", invalid="ignore"):
        return {"x^3+x": x ** 3 + x, "exp(x)": np.exp(x), "ranks": midranks(x)}


def versions(z):
    with np.errstate(over="ignore"):
        return {"plain": z, "exp": np.exp(z), "cube": z ** 3}


fail_new = {}
fail_old = {}
ver_bad = []
cases = 0
for n in LENGTHS:
    for cname, gen in CLASSES.items():
        for s in range(SEEDS):
            rng = np.random.default_rng(20262000 + 1000 * n + 100 * list(CLASSES).index(cname) + s)
            z = std(gen(rng, n))
            vs = versions(z)
            for vname, x in vs.items():
                if not np.all(np.isfinite(x)) or ndistinct(x) != ndistinct(z):
                    ver_bad.append((n, cname, vname, s))
                for mname, m in maps_new(x).items():
                    cases += 1
                    bad = (not np.all(np.isfinite(m))) or ndistinct(m) != ndistinct(x)
                    if bad:
                        fail_new[(n, cname, vname, mname)] = fail_new.get((n, cname, vname, mname), 0) + 1
                for mname, m in maps_old(x).items():
                    bad = (not np.all(np.isfinite(m))) or ndistinct(m) != ndistinct(x)
                    if bad:
                        fail_old[(n, cname, vname, mname)] = fail_old.get((n, cname, vname, mname), 0) + 1
print(f"seeds: series seed = 20262000 + 1000*n + 100*class_index + seed, seed 0..{SEEDS-1}; lengths {LENGTHS}")
print(f"INFO cases tested with the rescaled maps: {cases} (9 classes x 3 versions x 3 maps x {SEEDS} seeds x {len(LENGTHS)} lengths = {9*3*3*SEEDS*len(LENGTHS)})")
print(f"INFO version series (exp(z), z^3) that overflow or lose distinct values relative to z: {len(ver_bad)}")
print(f"RESULT rescaled maps: cells (length, class, version, map) with any failure: {len(fail_new)}; total failing cases {sum(fail_new.values())}")
for k, v in sorted(fail_new.items())[:10]:
    print(f"   {k}: {v} of {SEEDS}")
min_cov = min([SEEDS - fail_new.get((n, c, v, m), 0) for n in LENGTHS for c in CLASSES for v in ("plain", "exp", "cube") for m in ("y^3+y", "exp(y)", "ranks")])
print(f"RESULT smallest representable-seed count over all (length, class, version, map) cells: {min_cov} of {SEEDS}; the 18-of-20 rule is met: {min_cov >= 18}")
print(f"RESULT old unrescaled maps (x^3 + x, exp(x) on the version series): cells with any failure: {len(fail_old)}; total failing cases {sum(fail_old.values())}")
by = {}
for (n, c, v, m), k in fail_old.items():
    by.setdefault((c, v, m), 0)
    by[(c, v, m)] += k
for k, v in sorted(by.items(), key=lambda kv: -kv[1])[:8]:
    print(f"   old maps, {k}: {v} failing cases over the three lengths (of {SEEDS*len(LENGTHS)})")
g2e = [(n, v) for (n, c, vv, m), v in fail_old.items() if c == "g2" and vv == "exp" and m == "exp(x)"]
print(f"INFO squared-Gaussian class, exp version, old exp map: failing seeds per length {sorted(g2e)}")
g2c = [(n, v) for (n, c, vv, m), v in fail_old.items() if c == "g2" and vv == "cube"]
print(f"INFO squared-Gaussian class, cube version, old maps: failing seeds {sorted(g2c)}")

# does the rescaling itself merge values?
rng = np.random.default_rng(20262999)
print("RESCALING: share of adjacent-double pairs merged by x -> x / m")
for lo, hi in ((0.3, 0.99), (1.01, 10.0), (10.0, 1000.0)):
    m = rng.uniform(lo, hi, 200000)
    x1 = rng.uniform(lo, hi, 200000) * 0.999
    x2 = np.nextafter(x1, np.inf)
    merged = np.mean((x1 / m) == (x2 / m))
    print(f"   m in ({lo}, {hi}), inputs near m: merged share {merged:.4f}")
# in the actual classes the maximum is the divisor; is the max itself merged with its neighbour?
mx_lt1 = 0
for n in LENGTHS:
    for cname, gen in CLASSES.items():
        for s in range(SEEDS):
            rng2 = np.random.default_rng(20262000 + 1000 * n + 100 * list(CLASSES).index(cname) + s)
            z = std(gen(rng2, n))
            if np.max(np.abs(z)) < 1:
                mx_lt1 += 1
print(f"INFO standardised class series with max|z| < 1 (where division by max|x| could merge adjacent doubles): {mx_lt1}")
# integer-valued null classes, part (b)
ib = 0
for n in (1024,):
    for cname in list(CLASSES)[:7]:
        for s in range(SEEDS):
            rng3 = np.random.default_rng(20263000 + 100 * list(CLASSES).index(cname) + s)
            z = std(CLASSES[cname](rng3, n))
            x = np.round(8 * z)
            for mname, m in maps_new(x).items():
                if (not np.all(np.isfinite(m))) or ndistinct(m) != ndistinct(x):
                    ib += 1
print(f"RESULT integer-valued series round(8 z), 7 null classes x {SEEDS} seeds x 3 maps: guard failures {ib}")
# must-fail controls
xe = 1e-17 * np.arange(1, 9)
control("guard fires on exp of values spaced 1e-17 apart", ndistinct(np.exp(xe)) != ndistinct(xe))
big = np.array([1.0, 800.0])
with np.errstate(over="ignore"):
    control("guard fires on exp(800) overflow", not np.all(np.isfinite(np.exp(big))))
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE k1_scope")
