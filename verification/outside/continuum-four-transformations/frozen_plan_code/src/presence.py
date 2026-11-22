"""Instrument presence, control rule, combination rule and Holm step (PREREG 4.3, 5, 6, 9). Exact rational arithmetic."""
from fractions import Fraction
from math import comb

ALPHA = Fraction(1, 20)
FAMILY = 28
FWER = Fraction(1, 20)


def binom_tail(S, K, q=ALPHA):
    """P(Binomial(S, q) >= K), exact."""
    if K <= 0:
        return Fraction(1)
    return sum(comb(S, k) * q ** k * (1 - q) ** (S - k) for k in range(K, S + 1))


def presence_p(K, S):
    if S < 1 or K < 0 or K > S:
        raise ValueError("need 0 <= K <= S and S >= 1")
    return binom_tail(S, K)


def excess_point(S, level=Fraction(1, 100)):
    """Smallest K with P(Binomial(S, 0.05) >= K) <= level."""
    for K in range(S + 2):
        if binom_tail(S, K) <= level:
            return K
    raise RuntimeError("no excess point")


def control_absent(K, S):
    """C2, C3, C4 rule: K below the 1 percent excess point and K / S at most 0.10."""
    return K < excess_point(S) and Fraction(K, S) <= Fraction(1, 10)


def combine_runs(pvalues):
    """Presence and transfer: the p-value of an instrument is the largest over the primary run and its net runs."""
    if len(pvalues) == 0:
        raise ValueError("no runs to combine")
    return max(Fraction(p) for p in pvalues)


def holm(tests, m=FAMILY, alpha=FWER):
    """tests: dict name -> p-value (rational or int ratio). The family has m tests; missing tests count as p = 1.
    Returns dict name -> (rejected, threshold used). Step-down: reject while p_(i) <= alpha / (m - i + 1)."""
    if len(tests) > m:
        raise ValueError("more tests than the family size")
    order = sorted(tests.items(), key=lambda kv: (Fraction(kv[1]), kv[0]))
    out = {}
    alive = True
    for i, (name, p) in enumerate(order):
        thr = Fraction(alpha) / (m - i)
        ok = alive and Fraction(p) <= thr
        if not ok:
            alive = False
        out[name] = (ok, thr)
    return out
