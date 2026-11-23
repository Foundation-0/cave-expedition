"""Second pass: the new reading D8 as the second draft words it, against the old literal D8.
New D8: in each run, adverse iff 40 x (number of detectors at or below S_B(w_A)) < R, where at or below means below, equal, or tied under
|a - b| <= 1e-12 x max(1, |a|, |b|); a run with a non-finite S_B(w_A) or detector score is neither adverse nor passing.
Old D8 (literal): adverse iff 40 x (number of detectors below S_B(w_A) by more than the tolerance) < R. Standard library only. No bare assert."""
import math
import sys
from fractions import Fraction as F
from itertools import combinations_with_replacement

out = []
w = out.append
fails = []
def chk(name, ok, detail=""):
    w(f"[{'ok' if ok else 'FAIL'}] {name}{(': ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)
TOL = F(1, 10 ** 12)
def finite(x):
    return not (math.isnan(x) or math.isinf(x))
def tie(a, b):
    fa, fb = F(a), F(b)
    return abs(fa - fb) <= TOL * max(F(1), abs(fa), abs(fb))
def new_adverse(a, dets, theta_den=40):
    if not finite(a) or not all(finite(s) for s in dets):
        return False
    at_or_below = sum(1 for s in dets if s < a or s == a or tie(s, a))
    return theta_den * at_or_below < len(dets) * (theta_den // 40 if theta_den == 40 else 1)
def old_adverse(a, dets):
    # literal D8 with float comparisons, tolerance as the plan states it; non-finite scores are not covered by the old text
    def tied(s):
        if not (finite(s) and finite(a)):
            return s == a
        return tie(s, a)
    below = sum(1 for s in dets if s < a and not tied(s))
    return 40 * below < len(dets)
GRID = [0.0, 1.0, 1.0 + 2.0 ** -40, 1.0 + 2.0 ** -39, 1.0 - 2.0 ** -40, 1.0 - 2.0 ** -39, -1.0, 1e6, 1e6 + 1e-6, 1e-13, 2.0, 0.5]
BAD = [float("nan"), float("inf"), float("-inf")]
# the checks need R >= 41 to make "fewer than R/40" mean more than "none", so use R = 41 to 44 by repeating values
n = nd = viol = idn = 0
for a in GRID + BAD:
    for R in (41, 42, 80, 81):
        for k in range(0, 4):
            pass
import random
rnd = random.Random(20261123)
cases = 0
for a in GRID + BAD:
    for R in (1, 2, 40, 41, 80, 81):
        for rep in range(3000):
            dets = [rnd.choice(GRID + (BAD if rep % 5 == 0 else [])) for _ in range(R)]
            # bias towards ties and near ties
            if rep % 3 == 0:
                dets = [a if (finite(a) and rnd.random() < 0.7) else d for d in dets]
            na, oa = new_adverse(a, dets), old_adverse(a, dets)
            cases += 1
            if na and not oa:
                viol += 1
            if na != oa:
                nd += 1
chk("the new rule never gives an adverse verdict that the old literal rule does not", viol == 0, f"{cases:,} sampled cases (seed 20261123), {nd:,} where they differ")
# exhaustive on the finite grid, small R, with the threshold scaled so that counts above zero matter
exh = bad = 0
for a in GRID:
    for R in range(1, 6):
        for dets in combinations_with_replacement(GRID, R):
            at_or_below = sum(1 for s in dets if s < a or s == a or tie(s, a))
            below = sum(1 for s in dets if s < a and not tie(s, a))
            for den in (1, 2, 4):
                new = den * at_or_below < R
                old = den * below < R
                both = new and old
                exh += 1
                if both != new:
                    bad += 1
chk("exhaustive finite grid, R = 1 to 5, thresholds 1, 1/2, 1/4: 'both readings' equals the new rule", bad == 0, f"{exh:,} cases")
chk("a nan template, an inf template or any non-finite detector score: the new rule is not adverse", not new_adverse(float("nan"), [1.0] * 41) and not new_adverse(1.0, [float("inf")] * 41) and not new_adverse(float("inf"), [float("inf")] * 41))
chk("the old text gave adverse for a nan template (so the new text removes that)", old_adverse(float("nan"), [1.0] * 41))
R = 99999
chk("boundary R = 99,999: 2,499 at or below is adverse, 2,500 is not", 40 * 2499 < R and not 40 * 2500 < R)
chk("all tied (R = 99,999 detectors equal to the template): not adverse", not (40 * 99999 < R))
# must-fail control: a variant that counts a tie as not at or below equals the old rule, so it breaks the 'new rule is stricter' property
def wrong_new(a, dets):
    return 40 * sum(1 for s in dets if s < a and not tie(s, a)) < len(dets)
dif = sum(1 for dets in combinations_with_replacement(GRID, 3) if wrong_new(1.0, dets) != new_adverse(1.0, dets))
chk("control: a rule that leaves ties out of 'at or below' is different from the new rule", dif > 0, f"{dif} of the 3-detector multisets at template 1.0")
w("")
w("RESULT " + ("all D8 checks hold" if not fails else "FAILED " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
