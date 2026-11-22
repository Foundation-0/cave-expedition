"""Amendment 2: exact one-run chance that a series with segment rate r passes a presence run.

A presence run passes when K (rejecting segments out of S) reaches the binomial point of the run's level
and the share K/S exceeds every control share by at least 1/4. Exact rational arithmetic throughout.
Domain: S = 12 to 32, runs in {5, 7, 8}. Two control assumptions: every control share 0 (K/S >= 1/4)
and every control share exactly 0.05 (K/S >= 3/10). Level: the smallest Holm step, 0.05/40 divided by
the runs; also reported, the largest Holm step, 0.05 divided by the runs."""
from fractions import Fraction as F
from math import comb
import sys

P0 = F(1, 20)
out = []
w = out.append
_cache = {}


def tails(n, p):
    key = (n, p)
    if key not in _cache:
        pmf = [F(comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
        t = [F(0)] * (n + 2)
        acc = F(0)
        for i in range(n, -1, -1):
            acc += pmf[i]
            t[i] = acc
        if acc != 1:
            raise ValueError("pmf does not sum to 1")
        _cache[key] = t
    return _cache[key]


def tail(n, k, p):
    if k <= 0:
        return F(1)
    if k > n:
        return F(0)
    return tails(n, p)[k]


def k_binomial(S, level):
    t = tails(S, P0)
    for k in range(S + 2):
        if t[k] <= level:
            return k
    raise ValueError("no k")


def ceil_frac(x):
    return -((-x.numerator) // x.denominator)


def round_up(x, sig):
    # smallest decimal with `sig` significant digits that is >= x
    e = 0
    y = x
    while y < 1:
        y *= 10
        e += 1
    scale = F(10) ** (e + sig - 1)
    v = ceil_frac(x * scale)
    return f"{float(F(v, 1) / scale):.{e + sig - 1}f}"


def table(rate, ctrl_share, step):
    best = (F(-1), None, None, None)
    for runs in (5, 7, 8):
        level = (F(5, 100) / 40 if step == "smallest" else F(5, 100)) / runs
        for S in range(12, 33):
            margin = ctrl_share + F(1, 4)
            k = max(k_binomial(S, level), ceil_frac(margin * S))
            p = tail(S, k, rate)
            if p > best[0]:
                best = (p, runs, S, k)
    return best


rates = (("0.10", F(1, 10)), ("0.129", F(129, 1000)))
ctrls = (("control shares 0", F(0)), ("control shares 0.05", F(1, 20)))
for step in ("smallest", "largest"):
    w(f"== Holm step: {step} (per-run level = {'0.05/40' if step == 'smallest' else '0.05'} / runs) ==")
    for rl, r in rates:
        for cl, c in ctrls:
            p, runs, S, k = table(r, c, step)
            w(f"rate {rl}, {cl}: maximum {float(p):.6f} (exact {p.numerator}/{p.denominator} has {len(str(p.denominator))} digits) "
              f"at runs = {runs}, S = {S}, K >= {k}; rounded up: {round_up(p, 2)} (three decimals: {float(F(ceil_frac(p * 1000), 1000)):.3f})")
w("== where the largest-step maximum falls, for each run count (all S attaining it) ==")
for rl, r in rates:
    for cl, c in ctrls:
        cells = []
        for runs in (5, 7, 8):
            level = F(5, 100) / runs
            vals = []
            for S in range(12, 33):
                k = max(k_binomial(S, level), ceil_frac((c + F(1, 4)) * S))
                vals.append((tail(S, k, r), S, k))
            m = max(v[0] for v in vals)
            where = ", ".join(f"S = {S}, K >= {k}" for p, S, k in vals if p == m)
            cells.append(f"{runs} runs: {float(m):.6f} at {where}")
        w(f"rate {rl}, {cl}: " + "; ".join(cells))
w("== rate 0.10, controls 0.05, at S = 32 for each run count (smallest Holm step) ==")
for runs in (5, 7, 8):
    level = F(5, 100) / 40 / runs
    k = max(k_binomial(32, level), ceil_frac(F(3, 10) * 32))
    p = tail(32, k, F(1, 10))
    w(f"runs = {runs}: K >= {k}, chance {float(p):.6f}, rounded up {round_up(p, 2)}")
# second route, sharing no helper with the code above: direct sums with math.comb, no cache
def direct_tail(n, k, p):
    return sum(F(comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(max(k, 0), n + 1))


def direct_k(S, level):
    k = 0
    while direct_tail(S, k, P0) > level:
        k += 1
    return k


agree = True
for rl, r in rates:
    for cl, c in ctrls:
        p, runs, S, k = table(r, c, "smallest")
        level = F(5, 100) / 40 / runs
        k2 = max(direct_k(S, level), ceil_frac((c + F(1, 4)) * S))
        agree = agree and k2 == k and direct_tail(S, k2, r) == p
w(f"second route agrees exactly on all four maxima (smallest Holm step): {agree}")
# must-fail control: an off-by-one threshold (K - 1) must give a strictly larger maximum
p_ok, runs, S, k = table(F(1, 10), F(0), "smallest")
p_bad = tail(S, k - 1, F(1, 10))
w(f"control: threshold K - 1 at the same cell gives {float(p_bad):.6f}; flagged = {p_bad > p_ok}")
sys.stdout.write("\n".join(out) + "\n")
