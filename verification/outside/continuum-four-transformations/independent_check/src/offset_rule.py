"""Clean-room exact check of the segment-offset rule (plan section 7) and the PREREG-03 counterexample.
Standard library only. Integers and Fractions. No bare assert."""
import random
import sys
from fractions import Fraction

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def verdict(tag, desc, claimed, mine, ok):
    print(f"CLAIM {tag} | {desc} | amendment={claimed} | mine={mine} | {'REPRODUCED' if ok else 'DIFFERS'}")


def cost(seg):
    """squared jump first->last value + squared jump between first slope and last slope."""
    j = seg[-1] - seg[0]
    s0 = seg[1] - seg[0]
    s1 = seg[-1] - seg[-2]
    return j * j + (s1 - s0) * (s1 - s0)


def costs(block, N):
    return [cost(block[o:o + N]) for o in range(len(block) - N + 1)]


def argmin_first(c):
    best = 0
    for i, v in enumerate(c):
        if v < c[best]:
            best = i
    return best


def midranks(block):
    srt = sorted(block)
    out = []
    for v in block:
        lo = srt.index(v)               # 0-based first position
        cnt = srt.count(v)
        out.append(Fraction(2 * lo + cnt + 1, 2))  # mean of ranks lo+1 .. lo+cnt
    return out


block = [10, 10, 0, 1, 11, 11, 2, 2]
N = 6
raw = costs(block, N)
verdict("raw", "raw costs, block [10,10,0,1,11,11,2,2], N=6", "[1, 65, 5]", raw, raw == [1, 65, 5])
verdict("raw-off", "raw offset chosen", 0, argmin_first(raw), argmin_first(raw) == 0)
cube = [v ** 3 + v for v in block]
c3 = costs(cube, N)
verdict("cube", "costs after x -> x^3 + x", "[110224, 1103684, 104]", c3, c3 == [110224, 1103684, 104])
verdict("cube-off", "offset after x^3+x", 2, argmin_first(c3), argmin_first(c3) == 2)
ex = [2 ** v for v in block]
c2 = costs(ex, N)
verdict("pow2", "costs after x -> 2^x", "[1048576, 2082841, 10]", c2, c2 == [1048576, 2082841, 10])
verdict("pow2-off", "offset after 2^x", 2, argmin_first(c2), argmin_first(c2) == 2)
neg = [-v for v in block]
cn = costs(neg, N)
verdict("polarity-raw", "raw costs unchanged by polarity flip", "unchanged", "unchanged" if cn == raw else cn, cn == raw)
# midranks
expect = [Fraction(4), Fraction(17, 4), Fraction(29, 4)]
for name, b in (("identity", block), ("x^3+x", cube), ("2^x", ex), ("polarity", neg)):
    r = midranks(b)
    cr = costs(r, N)
    ok = cr == expect and argmin_first(cr) == 0
    verdict(f"rank-{name}", f"mid-rank costs under {name}", "[4, 17/4, 29/4], offset 0",
            f"{[str(v) for v in cr]}, offset {argmin_first(cr)}", ok)
print(f"INFO mid-ranks of the block: {[str(v) for v in midranks(block)]}")

# random invariance: mid-rank offset invariant under increasing maps and polarity; raw offset is not
rng = random.Random(20261202)
raw_changes = 0
rank_changes = 0
trials = 2000
for _ in range(trials):
    L = rng.randint(10, 24)
    Nn = rng.randint(6, L - 1)
    b = [rng.randint(0, 12) for _ in range(L)]
    maps = [lambda v: v ** 3 + v, lambda v: 2 ** v, lambda v: 7 * v + 3]
    base_r = argmin_first(costs(midranks(b), Nn))
    base_raw = argmin_first(costs(b, Nn))
    for m in maps:
        if argmin_first(costs(midranks([m(v) for v in b]), Nn)) != base_r:
            rank_changes += 1
        if argmin_first(costs([m(v) for v in b], Nn)) != base_raw:
            raw_changes += 1
    if argmin_first(costs(midranks([-v for v in b]), Nn)) != base_r:
        rank_changes += 1
verdict("rank-inv", f"mid-rank offset invariant under 3 increasing maps and polarity ({trials} random blocks with ties)",
        "invariant", f"{rank_changes} changes", rank_changes == 0)
print(f"INFO raw-value offset changed in {raw_changes} of {3*trials} (block, map) cases")
control("raw rule is not invariant (must change somewhere)", raw_changes > 0)
control("claimed costs [1,65,6] flagged", raw != [1, 65, 6])
control("claimed offset 1 after cube flagged", argmin_first(c3) != 1)

# Tie-break: smallest offset among equal costs
tb = argmin_first([5, 3, 3, 9])
verdict("tiebreak", "smallest offset among equal costs (helper)", 1, tb, tb == 1)
control("last-offset tie-break would give 2 (wrong) flagged", tb != 2)

if FAILS:
    print("FAILED CONTROLS:", FAILS)
    sys.exit(1)
print("DONE exact_endmatch")
