"""PREREG-02: action of polarity flip P, time reversal R and R o P on order-3 pattern features.

Exact, integers only. Patterns are rank tuples: pattern (r0, r1, r2) means value i has rank r_i.
"""
from itertools import permutations
import sys

out = []
w = out.append


def rev(p):
    return tuple(reversed(p))


def comp(p):
    return tuple(len(p) - 1 - r for r in p)


def name(p):
    return "".join(str(r) for r in p)


def pat(window):
    order = sorted(range(len(window)), key=lambda i: (window[i], i))
    ranks = [0] * len(window)
    for pos, i in enumerate(order):
        ranks[i] = pos
    return tuple(ranks)


def counts(x, tau, d=3):
    c = {p: 0 for p in permutations(range(d))}
    ties = 0
    for t in range(len(x) - (d - 1) * tau):
        win = [x[t + j * tau] for j in range(d)]
        if len(set(win)) < d:
            ties += 1
            continue
        c[pat(win)] += 1
    return c, ties


# 1. Group action on the six patterns
P3 = sorted(permutations(range(3)))
w("== action on patterns (d = 3) ==")
for p in P3:
    w(f"{name(p)}: P -> {name(comp(p))}, R -> {name(rev(p))}, RP -> {name(rev(comp(p)))}")

# 2. Action on (a1, a2, a3) as signed index maps. a_i = ln n(num_i) / n(den_i).
pairs = {"a1": ((0, 1, 2), (2, 1, 0)), "a2": ((0, 2, 1), (1, 2, 0)), "a3": ((1, 0, 2), (2, 0, 1))}


def image(g):
    """For each feature, which feature (and sign) it becomes when counts are relabelled by g."""
    res = {}
    for k, (num, den) in pairs.items():
        gn, gd = g(num), g(den)
        hit = None
        for k2, (n2, d2) in pairs.items():
            if (gn, gd) == (n2, d2):
                hit = (+1, k2)
            elif (gn, gd) == (d2, n2):
                hit = (-1, k2)
        if hit is None:
            raise ValueError("map not closed")
        res[k] = hit
    return res


for label, g in (("P", comp), ("R", rev), ("RP", lambda p: rev(comp(p)))):
    im = image(g)
    w(f"{label}: " + ", ".join(f"{k} -> {'+' if s > 0 else '-'}{k2}" for k, (s, k2) in im.items()))
w("so with s = a2 + a3 and u = a2 - a3:")
w("  P : (a1, s, u) -> (-a1, -s, +u)")
w("  R : (a1, s, u) -> (-a1, -s, -u)")
w("  RP: (a1, s, u) -> (+a1, +s, -u)")
w("On (a1, s), P and R act the same way. Any polarity-invariant function of (a1, s) is therefore also")
w("time-reversal invariant: it cannot carry a time arrow. The only polarity-free arrow is u, and u is odd")
w("under RP, so its expectation is 0 for any process whose law is unchanged by RP.")
w("If law(x) = law(-x reversed), then law(x reversed) = law(-x): reversing time and flipping polarity are")
w("the same operation, so no polarity-invariant statistic can tell a series from its time reverse.")

# 3. Concrete series: noiseless sawtooth (slow linear rise over 64 samples, instant drop), RP-symmetric.
saw = [i % 64 for i in range(64 * 64)]
w("== noiseless sawtooth, period 64, 4096 samples ==")
for tau in (1, 2, 4, 8, 16):
    c, ties = counts(saw, tau)
    n = {name(p): c[p] for p in P3}
    # u == 0 exactly iff (2n021+1)(2n201+1) == (2n120+1)(2n102+1)  (counts + 1/2)
    lhs = (2 * n["021"] + 1) * (2 * n["201"] + 1)
    rhs = (2 * n["120"] + 1) * (2 * n["102"] + 1)
    w(f"tau={tau}: counts {n}, tied windows {ties}; n021==n102: {n['021'] == n['102']}, "
      f"n120==n201: {n['120'] == n['201']}; u == 0 exactly: {lhs == rhs}")

# 4. The same sawtooth reversed in time: a1 and s change sign, u stays 0.
rsaw = list(reversed(saw))
c, _ = counts(rsaw, 1)
w("reversed sawtooth, tau=1: " + str({name(p): c[p] for p in P3}))
w("negated sawtooth, tau=1: " + str({name(p): v for p, v in counts([-v for v in saw], 1)[0].items()}))

sys.stdout.write("\n".join(out) + "\n")
