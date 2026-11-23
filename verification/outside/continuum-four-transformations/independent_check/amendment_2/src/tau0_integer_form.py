"""Plan 4.3 text: with doubled mid-ranks centred by their exact mean, numerator and denominator are integers, and 'below 1/2' means twice the numerator
is less than the denominator. Check equivalence with exact rational 'autocorrelation below 1/2' (biased estimate about the mean) on random tied series,
and find exact-equality cases (autocorrelation exactly 1/2), which the integer form must not count as below. Standard library only. No bare assert."""
import random
import sys
from fractions import Fraction
from itertools import product

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def midranks2(x):
    """doubled mid-ranks, integers: 2 * mean of the ranks (1-based) of the tied group"""
    srt = sorted(x)
    first, cnt = {}, {}
    for i, a in enumerate(srt):
        first.setdefault(a, i)
        cnt[a] = cnt.get(a, 0) + 1
    return [2 * first[a] + cnt[a] + 1 for a in x]      # = 2 * (first+1 + first+cnt)/2


def acf_fraction(x, k):
    r2 = midranks2(x)
    n = len(r2)
    mean = Fraction(sum(r2), n)
    d = [Fraction(v) - mean for v in r2]
    num = sum(d[t] * d[t + k] for t in range(n - k))
    den = sum(v * v for v in d)
    return num / den


def below_half_integer(x, k):
    r2 = midranks2(x)
    n = len(r2)
    s = sum(r2)
    c = [n * v - s for v in r2]                          # integers, = n (2 r - mean2)
    num = sum(c[t] * c[t + k] for t in range(n - k))
    den = sum(v * v for v in c)
    return 2 * num < den, num, den


rng = random.Random(20270001)
bad = 0
tot = 0
for _ in range(3000):
    n = rng.randint(6, 40)
    hi = rng.choice([2, 3, 6, 40, 1000])
    x = [rng.randint(0, hi) for _ in range(n)]
    if len(set(x)) == 1:
        continue
    for k in range(1, min(n - 1, 8) + 1):
        tot += 1
        exact = acf_fraction(x, k) < Fraction(1, 2)
        integer, num, den = below_half_integer(x, k)
        if exact != integer:
            bad += 1
print(f"CLAIM tau0-integer | the integer form (2 x numerator < denominator) equals exact rational 'autocorrelation below 1/2' | text=equivalent | mine={'equal in all ' + str(tot) + ' cases' if not bad else str(bad) + ' differences'} | {'REPRODUCED' if not bad else 'DIFFERS'}")
# exact-equality cases
eq = []
for n in range(4, 9):
    for x in product(range(3), repeat=n):
        if len(set(x)) == 1:
            continue
        for k in range(1, n - 1):
            if acf_fraction(list(x), k) == Fraction(1, 2):
                eq.append((x, k))
    if len(eq) >= 3:
        break
print(f"INFO exact-equality cases found (autocorrelation exactly 1/2): {len(eq)}; first: {eq[:2]}")
if eq:
    x, k = eq[0]
    integer, num, den = below_half_integer(list(x), k)
    float_ac = float(acf_fraction(list(x), k))
    print(f"   example {x}, lag {k}: integer form numerator {num}, denominator {den}, below-1/2 verdict {integer}; the float autocorrelation is {float_ac!r}")
    control("integer form does not count an exact one half as below", not integer)
else:
    print("   (no exact-equality case in the search range; equality is possible in principle: 2 num = den is an integer equation)")
    control("integer form is exact (equality is decided by integers)", True)
# denominator positive for non-constant series
x = [1, 1, 2, 3, 3]
integer, num, den = below_half_integer(x, 1)
control("denominator positive for a non-constant series", den > 0)
control("a constant series has denominator 0 (invalid by the B7 rule, never reaches tau0)", below_half_integer([4, 4, 4, 4], 1)[2] == 0)
if FAILS or bad:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE tau0_integer_form")
