"""Exact false-presence chance of one presence run, at several Holm steps.
Rules taken from the plan text: a presence run passes if its binomial tail is within (Holm step threshold / runs) and the share of
rejecting segments K/S exceeds each control share by at least 1/4. Control shares: 0 (most favourable to presence) or 0.05 (margin share 0.30).
Domain: S = 12..32 segments, run counts 8 (GW, SEIS, Wind at N=4096), 7 (TESS), 5 (Wind at N=2048). Segment rate r.
Standard library only. No bare assert."""
import sys
from fractions import Fraction
from math import comb, ceil

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def tail(n, p, k):
    if k <= 0:
        return Fraction(1)
    return sum(Fraction(comb(n, j)) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))


def kmin(n, p, level):
    for k in range(n + 2):
        if tail(n, p, k) <= level:
            return k
    raise ValueError("none")


P05 = Fraction(1, 20)


def knee(S, level, ctrl):
    return max(kmin(S, P05, level), ceil(S * (Fraction(1, 4) + ctrl)))


def maximum(r, ctrl, step, runs_list, offset=0):
    best = (Fraction(0), None, [])
    for runs in runs_list:
        for S in range(12, 33):
            K = knee(S, step / runs, ctrl) + offset
            v = tail(S, r, K)
            if v > best[0]:
                best = (v, (runs, S, K), [(runs, S, K)])
            elif v == best[0]:
                best[2].append((runs, S, K))
    return best


steps = {"smallest Holm step 0.05/40": Fraction(5, 4000), "largest Holm step 0.05/1": Fraction(5, 100)}
RUNS = (8, 7, 5)
res = {}
for lab, step in steps.items():
    print(f"== {lab}")
    for r in (Fraction(1, 10), Fraction(129, 1000)):
        for ctrl in (Fraction(0), Fraction(5, 100)):
            b = maximum(r, ctrl, step, RUNS)
            res[(lab, r, ctrl)] = b
            print(f"  r={float(r):.3f} control {float(ctrl):.2f}: maximum {float(b[0]):.6f} at (runs, S, K) = {b[1]}; ties: {[t for t in b[2] if t != b[1]][:4]}")
# S = 32 value at control 0.05
s32 = tail(32, Fraction(1, 10), knee(32, steps["smallest Holm step 0.05/40"] / 8, Fraction(5, 100)))
print(f"  r=0.10 control 0.05 at S=32 (8 runs): {float(s32):.6f}; 7 runs: {float(tail(32, Fraction(1,10), knee(32, steps['smallest Holm step 0.05/40']/7, Fraction(5,100)))):.6f}; 5 runs: {float(tail(32, Fraction(1,10), knee(32, steps['smallest Holm step 0.05/40']/5, Fraction(5,100)))):.6f}")

# intermediate steps: the plan has 40 tests, so a step is 0.05/j for j = 1..40
print("== maxima over all 40 Holm steps (r = 0.10, control 0.05)")
allsteps = [(Fraction(5, 100 * j), j) for j in range(1, 41)]
for j in (40, 30, 20, 10, 5, 2, 1):
    b = maximum(Fraction(1, 10), Fraction(5, 100), Fraction(5, 100 * j), RUNS)
    print(f"  step 0.05/{j}: {float(b[0]):.5f} at {b[1]}")

def roundup_matches(v, text):
    """True when the text figure equals v rounded UP at the text's own number of decimals."""
    d = len(text.split(".")[1])
    scale = 10 ** d
    import math
    return Fraction(math.ceil(v * scale), scale) == Fraction(text)


def row(tag, text, key, tol=None):
    v = res[key][0]
    print(f"CLAIM {tag} | text={text} (rounded up) | mine={float(v):.6f} at {res[key][1]} | {'REPRODUCED' if roundup_matches(v, text) else 'DIFFERS'}")


L, Sm = "largest Holm step 0.05/1", "smallest Holm step 0.05/40"
row("step-large-0.10-c0", "0.069", (L, Fraction(1, 10), Fraction(0)), 0.0005)
row("step-large-0.10-c05", "0.035", (L, Fraction(1, 10), Fraction(5, 100)), 0.0005)
row("step-large-0.129-c0", "0.142", (L, Fraction(129, 1000), Fraction(0)), 0.005)
row("step-large-0.129-c05", "0.076", (L, Fraction(129, 1000), Fraction(5, 100)), 0.0005)
row("small-0.10-c0", "0.012", (Sm, Fraction(1, 10), Fraction(0)), 0.0005)
row("small-0.10-c05", "0.0086", (Sm, Fraction(1, 10), Fraction(5, 100)), 0.0001)
print(f"CLAIM small-0.10-S32 | text=0.00081 (rounded up) | mine={float(s32):.6f} | {'REPRODUCED' if roundup_matches(s32, '0.00081') else 'DIFFERS'}")
control("a wrong figure 0.0007 is not the round-up of the S=32 value", not roundup_matches(s32, "0.0007"))
row("small-0.129-c0", "0.047", (Sm, Fraction(129, 1000), Fraction(0)), 0.0005)
row("small-0.129-c05", "0.029", (Sm, Fraction(129, 1000), Fraction(5, 100)), 0.0005)
# must-fail control: an off-by-one threshold gives a strictly larger value
b0 = maximum(Fraction(1, 10), Fraction(0), steps[Sm], RUNS)
b1 = maximum(Fraction(1, 10), Fraction(0), steps[Sm], RUNS, offset=-1)
control("threshold one lower gives a strictly larger maximum", b1[0] > b0[0])
control("a wrong text value (0.012 as 0.0012) is not an upper bound-with-slack", not (float(b0[0]) <= 0.0012))
if FAILS:
    print("FAILED CONTROLS:", FAILS)
    sys.exit(1)
print("DONE holm_steps")
