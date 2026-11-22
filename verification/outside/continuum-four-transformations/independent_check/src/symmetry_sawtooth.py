"""Clean-room exact checks: ordinal pattern symmetries, tied-pattern counts, sawtooth counts.
Standard library only; integers and Fractions only. No bare assert.
Pattern notation (plan section 4): a pattern lists the rank (0 = smallest) of each window position,
so (a,b,c) with b < c < a is "201". Tied windows get dense ranks (equal values, equal rank).
"""
import random
import sys
from itertools import product
from fractions import Fraction

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def verdict(tag, desc, claimed, mine, ok):
    print(f"CLAIM {tag} | {desc} | amendment={claimed} | mine={mine} | {'REPRODUCED' if ok else 'DIFFERS'}")


def pat(w):
    """Dense-rank pattern string of a window of values."""
    vals = sorted(set(w))
    return "".join(str(vals.index(v)) for v in w)


def counts(x, tau, d=3):
    c = {}
    for t in range(len(x) - (d - 1) * tau):
        w = tuple(x[t + i * tau] for i in range(d))
        c[pat(w)] = c.get(pat(w), 0) + 1
    return c


def all_patterns(d):
    """All weak-ordering patterns of d positions: dense-rank strings."""
    out = set()
    for r in product(range(d), repeat=d):
        used = sorted(set(r))
        if used == list(range(len(used))):
            out.add("".join(map(str, r)))
    return sorted(out)


def rev(p):
    return pat(tuple(reversed([int(ch) for ch in p])))


def comp(p):
    return pat(tuple(-int(ch) for ch in p))


def n(c, p):
    return c.get(p, 0)


def feats_int(c):
    """Return (X1, X2, X3) with exp(a2)... as exact rationals: ratios (n+1/2)/(n'+1/2) for a1,a2,a3."""
    r1 = Fraction(2 * n(c, "012") + 1, 2 * n(c, "210") + 1)
    r2 = Fraction(2 * n(c, "021") + 1, 2 * n(c, "120") + 1)
    r3 = Fraction(2 * n(c, "102") + 1, 2 * n(c, "201") + 1)
    return r1, r2, r3


def u_zero(c):
    """u = a2 - a3 = 0 iff (2 n021 + 1)(2 n201 + 1) == (2 n120 + 1)(2 n102 + 1). Integer test."""
    return (2 * n(c, "021") + 1) * (2 * n(c, "201") + 1) == (2 * n(c, "120") + 1) * (2 * n(c, "102") + 1)


# ---- pattern census ----
P3 = all_patterns(3)
P4 = all_patterns(4)
verdict("pat13", "number of order-3 patterns with ties", 13, len(P3), len(P3) == 13)
verdict("pat75", "number of order-4 patterns with ties", 75, len(P4), len(P4) == 75)
pairs = sorted({tuple(sorted((p, rev(p)))) for p in P3})
selfrev = [p for p in P3 if rev(p) == p]
print(f"INFO order-3 reversal classes: {pairs}")
print(f"INFO self-reverse order-3 patterns: {selfrev}")
ok = (set(selfrev) == {"010", "101", "000"} and ("001", "100") in pairs and ("011", "110") in pairs)
verdict("pairs13", "001-100, 011-110 paired; 010,101,000 self-reverse", "as stated", "as stated" if ok else "differs", ok)
verdict("rev6", "strict pairs 012-210, 021-120, 102-201",
        "as stated", "as stated" if (rev("012") == "210" and rev("021") == "120" and rev("102") == "201") else "differs",
        rev("012") == "210" and rev("021") == "120" and rev("102") == "201")
# polarity bijection commutes with reversal on all 13 patterns
commute = all(comp(rev(p)) == rev(comp(p)) for p in P3) and all(comp(comp(p)) == p for p in P3)
verdict("commute", "polarity flip is a bijection commuting with reversal (13 patterns)", "yes", "yes" if commute else "no", commute)
commute4 = all(comp(rev(p)) == rev(comp(p)) for p in P4)
verdict("commute4", "same for the 75 order-4 patterns", "(implied)", "yes" if commute4 else "no", commute4)

# ---- symmetry maps on random integer sequences (with and without ties) ----
rng = random.Random(20261201)
ok_maps = True
ok_u = True
nonzero_u_seen = 0
for trial in range(300):
    L = rng.randint(40, 120)
    hi = rng.choice([3, 10, 10**6])
    x = [rng.randint(0, hi) for _ in range(L)]
    # make it irreversible-ish by random drift so u is usually nonzero
    x = [v + (i // 7) * rng.choice([0, 1]) for i, v in enumerate(x)]
    for tau in (1, 2, 3):
        cx = counts(x, tau)
        cn = counts([-v for v in x], tau)
        cr = counts(list(reversed(x)), tau)
        cnr = counts([-v for v in reversed(x)], tau)
        # untied counts only for features
        f = feats_int(cx)
        fn = feats_int(cn)
        fr = feats_int(cr)
        fnr = feats_int(cnr)
        inv = lambda t: tuple(1 / a for a in t)
        # polarity: (a1,a2,a3)->(-a1,-a3,-a2): ratios (r1,r2,r3)->(1/r1, 1/r3, 1/r2)
        if fn != (1 / f[0], 1 / f[2], 1 / f[1]):
            ok_maps = False
        # time reversal: -> (-a1,-a2,-a3)
        if fr != (1 / f[0], 1 / f[1], 1 / f[2]):
            ok_maps = False
        # both: (a1,a2,a3) -> (+a1, +a3, +a2)
        if fnr != (f[0], f[2], f[1]):
            ok_maps = False
        # u = a2 - a3: ratio r2/r3
        U = lambda t: t[1] / t[2]
        if U(fn) != U(f):           # polarity: u unchanged
            ok_u = False
        if U(fr) != 1 / U(f):       # reversal: u -> -u
            ok_u = False
        if U(fnr) != 1 / U(f):      # both: u -> -u
            ok_u = False
        if U(f) != 1:
            nonzero_u_seen += 1
        # counts-level relabelling checks (ties included)
        if any(n(cn, comp(p)) != n(cx, p) for p in P3):
            ok_maps = False
        if any(n(cr, rev(p)) != n(cx, p) for p in P3):
            ok_maps = False
print(f"INFO random-sequence trials: u nonzero in {nonzero_u_seen} of 900 (series, lag) cases")
verdict("maps", "polarity (a1,a2,a3)->(-a1,-a3,-a2); reversal -> (-a1,-a2,-a3); both -> (+a1,+a3,+a2)",
        "as stated", "as stated" if ok_maps else "differs", ok_maps)
verdict("u-signs", "u unchanged by polarity, negated by reversal, negated by both (s unchanged by both)",
        "as stated", "as stated" if ok_u else "differs", ok_u)
# s = a2 + a3 : ratio r2*r3. check s -> -s under polarity and reversal, +s under both
ok_s = True
for trial in range(200):
    x = [rng.randint(0, 50) for _ in range(rng.randint(30, 90))]
    f = feats_int(counts(x, 1))
    fn = feats_int(counts([-v for v in x], 1))
    fr = feats_int(counts(list(reversed(x)), 1))
    fnr = feats_int(counts([-v for v in reversed(x)], 1))
    S = lambda t: t[1] * t[2]
    if not (S(fn) == 1 / S(f) and S(fr) == 1 / S(f) and S(fnr) == S(f)):
        ok_s = False
verdict("s-signs", "s=a2+a3 -> -s under polarity and under reversal, +s under both", "as stated",
        "as stated" if ok_s else "differs", ok_s)
# magnitudes m1=|a1|, m23=|a2+a3| unchanged by reversal (ratio r -> 1/r keeps |ln r|)
verdict("m-rev", "m1, m23 unchanged by time reversal", "as stated", "as stated" if ok_s and ok_maps else "differs", ok_s and ok_maps)

# must-fail: the (wrong) claim that polarity maps (a1,a2,a3) to (-a1,-a2,-a3) must be refuted
bad = False
x = [0, 1, 3, 2, 5, 4, 6, 8, 7, 9, 12, 10, 11, 15, 13, 14]
f = feats_int(counts(x, 1))
fn = feats_int(counts([-v for v in x], 1))
bad = fn != (1 / f[0], 1 / f[1], 1 / f[2])
control("wrong polarity map (-a1,-a2,-a3) refuted on an example", bad)
control("wrong claim 'u unchanged by reversal' refuted", feats_int(counts(list(reversed(x)), 1))[1] / feats_int(counts(list(reversed(x)), 1))[2] != feats_int(counts(x, 1))[1] / feats_int(counts(x, 1))[2])

# ---- sawtooth ----
T = 4096
rise = [t % 64 for t in range(T)]
fall = [-(t % 64) for t in range(T)]
fall2 = [63 - (t % 64) for t in range(T)]
rev_rise = list(reversed(rise))
neg_rise = [-v for v in rise]
print("# sawtooth, period 64, 4096 samples, x_t = t mod 64 (rising ramp). Falling ramp also given.")
allok = True
for tau in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512):
    c = counts(rise, tau)
    cf = counts(fall, tau)
    row = {p: n(c, p) for p in ("012", "021", "102", "120", "201", "210")}
    tied = sum(v for p, v in c.items() if len(set(p)) < 3)
    z = u_zero(c)
    zf = u_zero(cf)
    same_rev_neg = counts(rev_rise, tau) == counts(neg_rise, tau)
    print(f"lag {tau:4d}: untied counts {row} tied={tied} total={sum(c.values())} u==0 rising: {z}, falling: {zf}; "
          f"reversed==negated counts: {same_rev_neg}")
    if tau in (1, 2, 4, 8, 16) and not (z and zf):
        allok = False
    if not same_rev_neg:
        allok = False
verdict("saw-u0", "u exactly 0 on the sawtooth at lags 1,2,4,8,16 (integer comparison)", "yes", "yes" if allok else "no", allok)
c1 = counts(rise, 1)
verdict("saw-n120", "n(120) at lag 1", 63, n(c1, "120"), n(c1, "120") == 63)
verdict("saw-n201", "n(201) at lag 1", 63, n(c1, "201"), n(c1, "201") == 63)
verdict("saw-n021", "n(021) at lag 1", 0, n(c1, "021"), n(c1, "021") == 0)
verdict("saw-n102", "n(102) at lag 1", 0, n(c1, "102"), n(c1, "102") == 0)
cf1 = counts(fall, 1)
print(f"INFO falling ramp lag 1: n021={n(cf1,'021')} n102={n(cf1,'102')} n120={n(cf1,'120')} n201={n(cf1,'201')} "
      f"(the amendment's 'n(120)=n(201)=63, n(021)=n(102)=0' holds for the rising ramp only; direction is not stated in the text)")
verdict("saw-fall-eq", "fall = 63 - (t mod 64) and -(t mod 64) give identical counts", "(implied)",
        "identical" if all(counts(fall, t) == counts(fall2, t) for t in (1, 2, 4, 8, 16)) else "differ",
        all(counts(fall, t) == counts(fall2, t) for t in (1, 2, 4, 8, 16)))
# non-integer view: the claim 'reversed sawtooth and negated sawtooth give identical counts'
rr = all(counts(rev_rise, t) == counts(neg_rise, t) for t in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512))
verdict("saw-rev-neg", "reversed sawtooth and negated sawtooth give identical counts (all ten lags)", "yes",
        "yes" if rr else "no", rr)
# derive: reviewers' count of 0 for n(120), n(201): what shorter/other construction gives 0?
print(f"INFO reviewers' claim n(120)=n(201)=0 contradicted: mine {n(c1,'120')}, {n(c1,'201')}")
# must-fail controls for the sawtooth checker
x2 = [(t % 64) for t in range(T)]
x2[100] = -1000
control("a sawtooth with one planted dip is not flagged u==0 (checker detects nonzero)", not u_zero(counts(x2, 1)))
control("a random-walk-like series has u != 0 detected", not u_zero(counts([i + (i * i) % 17 for i in range(500)], 1)))
control("wrong claim n(120)=0 refuted", n(c1, "120") != 0)
# the identity that is checked: product form equals u == 0
a = counts(rise, 1)
lhs = (2 * n(a, "021") + 1) * (2 * n(a, "201") + 1)
rhs = (2 * n(a, "120") + 1) * (2 * n(a, "102") + 1)
print(f"INFO lag 1 products: (2n021+1)(2n201+1) = {lhs}, (2n120+1)(2n102+1) = {rhs}")

if FAILS:
    print("FAILED CONTROLS:", FAILS)
    sys.exit(1)
print("DONE exact_symmetry")
