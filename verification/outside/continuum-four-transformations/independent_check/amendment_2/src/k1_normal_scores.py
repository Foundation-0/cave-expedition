"""B5 check (normal scores of the exp and cube versions against the plain version, exact, 4,096 and 2,048 samples, 10 seeds): representability guard on all 9 K2 classes in 3 versions at 4,096, 2,048 and 1,024 samples, 20 seeds, three comparison maps
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



from statistics import NormalDist

ND = NormalDist()


def normal_scores(x):
    n = len(x)
    r = midranks(x)
    return np.array([ND.inv_cdf((float(v) - 0.5) / n) for v in r])


bad = []
tot = 0
for n in (4096, 2048):
    for ci, (cname, gen) in enumerate(CLASSES.items()):
        for s in range(10):
            rng = np.random.default_rng(20267000 + 1000 * n + 100 * ci + s)
            z = std(gen(rng, n))
            base = normal_scores(z)
            for vname, x in versions(z).items():
                tot += 1
                if not np.array_equal(base, normal_scores(x)):
                    bad.append((n, cname, vname, s))
            if not np.array_equal(normal_scores(-z), -base):
                bad.append((n, cname, "negation", s))
print(f"seeds: 20267000 + 1000*n + 100*class_index + seed (seed 0..9); lengths 4096, 2048; {tot} version comparisons, 9 classes")
print(f"CLAIM b5-ns | normal scores of exp and cube versions equal those of the plain version exactly (and -z gives the negated scores) | text=exact | mine={'exact in all cases' if not bad else str(len(bad)) + ' differences'} | {'REPRODUCED' if not bad else 'DIFFERS'}")
for b in bad[:5]:
    print("   ", b)
x = np.array([1.0, 2.0, 3.0])
control("the check detects a version that merges values", not np.array_equal(normal_scores(x), normal_scores(np.array([1.0, 1.0, 3.0]))))
if FAILS or bad:
    sys.exit(1)
print("DONE k1_normal_scores")
