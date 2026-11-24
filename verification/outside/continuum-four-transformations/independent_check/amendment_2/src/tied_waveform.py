"""B6 check (a): the tied waveform [0,0,1,2,2,1,0,0] x 512. Pattern counts at every lag used (2 tau <= n/4), equality with reversed counts,
Sigma_hat and a1, a2, a3 exactly 0 (exact rationals), identical counts under the three maps, and the must-fail ranking that breaks ties in
time order. Standard library only. No bare assert."""
import math
import sys
from fractions import Fraction
from itertools import product

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def dense(w):
    vals = sorted(set(w))
    return tuple(vals.index(v) for v in w)


def counts(x, tau):
    c = {}
    for t in range(len(x) - 2 * tau):
        p = dense((x[t], x[t + tau], x[t + 2 * tau]))
        c[p] = c.get(p, 0) + 1
    return c


PATS = sorted({dense(w) for w in product(range(3), repeat=3)})
assert_len = len(PATS)
print(f"INFO order-3 patterns: {len(PATS)} (plan: 13)")
rev = lambda p: dense(tuple(reversed(p)))
x = [0, 0, 1, 2, 2, 1, 0, 0] * 512
n = len(x)
lags = [2 ** j for j in range(10) if 2 * 2 ** j <= n // 4]
print(f"INFO n = {n}; lags used {lags}")


def midranks(v):
    srt = sorted(v)
    first = {}
    cnt = {}
    for i, a in enumerate(srt):
        first.setdefault(a, i)
        cnt[a] = cnt.get(a, 0) + 1
    return [Fraction(2 * first[a] + cnt[a] + 1, 2) for a in v]


# maps on y = x / max|x|: y^3 + y, exp(y), ranks. Ties must be preserved; compare counts as integers.
m = max(abs(a) for a in x)
y = [a / m for a in x]
maps = {"identity": x, "y^3+y": [a**3 + a for a in y], "exp(y)": [math.exp(a) for a in y], "mid-ranks": midranks(x)}
base = {t: counts(x, t) for t in lags}
ok_sym = True
ok_maps = True
for t in lags:
    c = base[t]
    for p in PATS:
        if c.get(p, 0) != c.get(rev(p), 0):
            ok_sym = False
    total = sum(c.values())
    tied = sum(v for p, v in c.items() if len(set(p)) < len(p) or max(p) < 2 and False)
for name, v in maps.items():
    for t in lags:
        if counts(v, t) != base[t]:
            ok_maps = False
print(f"CLAIM wave-sym | each pattern count equals its reversed pattern's count at every lag used | text=exact | mine={'exact' if ok_sym else 'NOT exact'} | {'REPRODUCED' if ok_sym else 'DIFFERS'}")
print(f"CLAIM wave-maps | every pattern count identical under the three maps (and the identity) | text=identical | mine={'identical' if ok_maps else 'NOT identical'} | {'REPRODUCED' if ok_maps else 'DIFFERS'}")
tied_total = sum(v for p, v in base[1].items() if len(set(p)) < 3)
print(f"INFO lag 1: {sum(base[1].values())} windows, {tied_total} tied")


def sigma_and_features(c):
    tot = sum(c.get(p, 0) for p in PATS)
    pr = {p: Fraction(2 * c.get(p, 0) + 1, 2) / (Fraction(tot) + Fraction(13, 2)) for p in PATS}
    # Sigma_hat = sum p ln(p/p_rev): zero exactly iff every ratio is exactly 1
    ratios = [pr[p] / pr[rev(p)] for p in PATS]
    exact0 = all(r == 1 for r in ratios)
    a = {}
    for name, (p, q) in {"a1": ((0, 1, 2), (2, 1, 0)), "a2": ((0, 2, 1), (1, 2, 0)), "a3": ((1, 0, 2), (2, 0, 1))}.items():
        a[name] = Fraction(2 * c.get(p, 0) + 1, 2 * c.get(q, 0) + 1)
    return exact0, a


allzero = True
for t in lags:
    e0, a = sigma_and_features(base[t])
    if not (e0 and all(v == 1 for v in a.values())):
        allzero = False
print(f"CLAIM wave-zero | Sigma_hat and a1, a2, a3 are exactly 0 (all ratios exactly 1) at every lag | text=exactly 0 | mine={'exactly 0' if allzero else 'non-zero'} | {'REPRODUCED' if allzero else 'DIFFERS'}")


def sigma_float(c):
    tot = sum(c.get(p, 0) for p in PATS)
    pr = {p: (c.get(p, 0) + 0.5) / (tot + 6.5) for p in PATS}
    return sum(pr[p] * math.log(pr[p] / pr[rev(p)]) for p in PATS)


# must-fail: ranking that breaks ties in time order (stable ranks) gives a non-zero Sigma_hat
order = sorted(range(n), key=lambda i: (x[i], i))
bypos = [0] * n
for r, i in enumerate(order):
    bypos[i] = r
nz = []
for t in lags:
    c = counts(bypos, t)
    nz.append((t, sigma_float(c)))
print("INFO Sigma_hat when ties are ranked in time order (no tied patterns remain):")
for t, v in nz:
    print(f"   lag {t}: {v:.6f}")
control("ranking ties in time order gives a non-zero Sigma_hat at some lag (so the new control can fail)", any(abs(v) > 1e-9 for _, v in nz))
print(f"INFO lags where the time-order ranking gives non-zero: {[t for t, v in nz if abs(v) > 1e-9]}")
# raw mid-rank statistic is zero in floating arithmetic too
control("floating Sigma_hat on the waveform is exactly 0.0 at every lag", all(sigma_float(base[t]) == 0.0 for t in lags))
control("a wrong waveform (not a palindrome) is not exactly symmetric", any(counts([0, 0, 1, 2, 2, 1, 1, 0] * 512, t) != base[t] for t in lags))
bad = [0, 1, 2, 0, 0, 0, 0, 0] * 512
okb = all(counts(bad, t).get(p, 0) == counts(bad, t).get(rev(p), 0) for t in lags for p in PATS)
control("a non-palindromic waveform fails the symmetry test", not okb)
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE tied_waveform")
