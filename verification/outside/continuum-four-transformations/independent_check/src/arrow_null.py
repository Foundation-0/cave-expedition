"""Exact enumeration: permutation-only null versus permutation-plus-random-sign null for the arrow transfer.
Score of a detector d on B's mean arrow profile f is d . f (surrogates average zero after standardisation, so the
comparison reduces to the dot product). p = fraction of ALL distinct detectors with score >= score(w_A) (exact).
Standard library only. No bare assert."""
import sys
from itertools import permutations, product
from fractions import Fraction

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def p_perm(w, f):
    s0 = dot(w, f)
    perms = list(permutations(w))
    return Fraction(sum(1 for d in perms if dot(d, f) >= s0), len(perms))


def p_sign(w, f):
    s0 = dot(w, f)
    n = 0
    tot = 0
    for d in set(permutations(w)):   # distinct permutations
        for sg in product((1, -1), repeat=len(w)):
            tot += 1
            if dot([a * b for a, b in zip(d, sg)], f) >= s0:
                n += 1
    return Fraction(n, tot)


print("Case 1: A's arrow template all one sign, B's arrow profile flat across levels")
for m in (4, 5, 6):
    w = list(range(1, m + 1))      # same-sign weights, distinct magnitudes
    f = [1] * m                    # flat B profile, same direction
    pp, ps = p_perm(w, f), p_sign(w, f)
    print(f"  m={m}: permutation-only p = {pp} ; permutation+sign p = {ps} = {float(ps):.5f} (expected 1/2^m = {Fraction(1, 2**m)})")
    if pp != 1 or ps != Fraction(1, 2 ** m):
        FAILS.append(f"case1 m={m}")
print("Case 2: same-sign template, B's profile has the same arrangement (levels ordered alike)")
for m in (4, 5, 6):
    w = list(range(1, m + 1)); f = list(range(1, m + 1))
    print(f"  m={m}: permutation-only p = {p_perm(w, f)} ; permutation+sign p = {p_sign(w, f)}")
print("Case 3: same-sign template, B's profile arranged in the opposite order")
for m in (4, 5, 6):
    w = list(range(1, m + 1)); f = list(range(m, 0, -1))
    print(f"  m={m}: permutation-only p = {p_perm(w, f)} ; permutation+sign p = {p_sign(w, f)}")
print("Reading: 'every permuted template scores as well as w_A' (AMENDMENT_1.md line 105) holds only for a level-flat B profile.")
print("In case 1 the sign-aware null is easier to beat than the permutation-only null (p drops from 1 to 1/2^m).")
# must-fail controls
control("claim p_perm < 1 for flat profile refuted", p_perm([1, 2, 3, 4], [1, 1, 1, 1]) == 1)
control("claim p_sign == 1 for flat profile refuted", p_sign([1, 2, 3, 4], [1, 1, 1, 1]) != 1)
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE exact_signnull")
