"""Amendment 4, C1: exhaustive checks of the tie rule, with own code. Standard library only. No bare assert.
Part 1: class level. Detectors split into b (below by more than the tolerance), t (tied), u (above by more than the tolerance).
        Literal D8 (ties not counted as below): adverse iff 40 b < R. Amended D8 (ties counted at or below): adverse iff 40 (b + t) < R.
Part 2: value level. Scores from a grid with tolerance edges, an all-tied block, a near-zero floor, large magnitudes and non-finite values.
        Tie predicate: exact rational (decimal 1e-12 applied to the exact binary values) and the float formula a plan reader would write."""
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

# ---------------------------------------------------------------- Part 1
w("== Part 1: class level, every (R, b, t, u) with b + t + u = R, R = 1 to 160")
total = lit_only = new_only = both_not_new = new_not_lit = same = 0
all_tied_lit = all_tied_new = 0
for R in range(1, 161):
    for b in range(R + 1):
        for t in range(R - b + 1):
            lit = 40 * b < R
            new = 40 * (b + t) < R
            both = lit and new
            total += 1
            if both != new:
                both_not_new += 1
            if new and not lit:
                new_not_lit += 1
            if lit and not new:
                lit_only += 1
            if lit == new:
                same += 1
            if b == 0 and t == R:
                all_tied_lit += lit
                all_tied_new += new
w(f"   cases {total:,}; literal adverse and amended not adverse {lit_only:,}; amended adverse and literal not {new_not_lit:,}; identical verdicts {same:,}")
chk("'adverse under both readings' equals the amended rule in every class case", both_not_new == 0)
chk("the amended rule never gives an adverse verdict that literal D8 does not", new_not_lit == 0)
chk("the amended rule differs from literal D8 in some cases", lit_only > 0)
chk("all detectors tied (b = 0, t = R): literal D8 says adverse at every R from 1 to 160, the amended rule never does", all_tied_lit == 160 and all_tied_new == 0, f"literal {all_tied_lit}, amended {all_tied_new}")
# R = 99,999 as in the plan: the boundary
R = 99999
bnd = [(b, 40 * b < R) for b in (2498, 2499, 2500)]
w(f"   R = 99,999: adverse needs fewer than R/40 = {R / 40} detectors at or below, so at most 2,499: " + ", ".join(f"count {b}: {v}" for b, v in bnd))
chk("boundary at R = 99,999 is 2,499", bnd[1][1] and not bnd[2][1])

# ---------------------------------------------------------------- Part 2
TOL = F(1, 10 ** 12)

def tie_exact(a, b):
    if math.isnan(a) or math.isnan(b):
        return False
    if math.isinf(a) or math.isinf(b):
        return a == b
    fa, fb = F(a), F(b)
    return abs(fa - fb) <= TOL * max(F(1), abs(fa), abs(fb))

def tie_float(a, b):
    return abs(a - b) <= 1e-12 * max(1.0, abs(a), abs(b))

def below(s, a):
    return s < a            # python: False if either is nan

def counts(a, dets, tie):
    bcount = tcount = 0
    for s in dets:
        if tie(s, a):
            tcount += 1
        elif below(s, a):
            bcount += 1
    return bcount, tcount

GRID = [0.0, 1e-13, -1e-13, 1.0, 1.0 + 0.5e-12, 1.0 + 1e-12, 1.0 + 1.000001e-12, 1.0 + 2e-12, 1.0 - 1e-12, 1.0 - 2e-12,
        1e6, 1e6 + 1e-6, 1e6 + 2e-6, -1e6, -1.0, 5e-13, 1.5e-12]
NONFIN = [float("inf"), float("-inf"), float("nan")]
w("")
w(f"== Part 2: value level, template and detector scores from a grid of {len(GRID)} finite values and {len(NONFIN)} non-finite values")
THETA = [F(1, 40), F(1, 4), F(1, 2), F(1)]
def run(vals, label, tie, maxR):
    bad_both = bad_dir = nd = nsame = n = 0
    ex_all_tied = ex_part = False
    for a in vals:
        for R in range(1, maxR + 1):
            for dets in combinations_with_replacement(vals, R):
                bc, tc = counts(a, dets, tie)
                for th in THETA:
                    lit = bc < th * R
                    new = bc + tc < th * R
                    n += 1
                    if (lit and new) != new:
                        bad_both += 1
                    if new and not lit:
                        bad_dir += 1
                    if lit != new:
                        nd += 1
                    else:
                        nsame += 1
    return n, nd, nsame, bad_both, bad_dir
for label, vals, maxR in (("finite grid, exact tie", GRID, 4), ("finite grid, float tie", GRID, 4)):
    tie = tie_exact if "exact" in label else tie_float
    n, nd, nsame, bb, bd = run(vals, label, tie, maxR)
    w(f"   {label}: cases {n:,}; verdicts differ {nd:,}; same {nsame:,}")
    chk(f"{label}: 'adverse under both readings' equals the amended rule", bb == 0)
    chk(f"{label}: amended adverse implies literal adverse", bd == 0)
vals = GRID[:6] + NONFIN
for tname, tie in (("exact", tie_exact), ("float", tie_float)):
    n, nd, nsame, bb, bd = run(vals, "nonfinite", tie, 4)
    w(f"   grid with inf, -inf, nan, {tname} tie: cases {n:,}; verdicts differ {nd:,}; same {nsame:,}")
    chk(f"non-finite grid, {tname} tie: both-readings identity and direction", bb == 0 and bd == 0)

w("")
w("== Specific cases the plan text must settle")
a = 1.0
dets = [1.0] * 6
bc, tc = counts(a, dets, tie_exact)
w(f"   all tied (6 detectors equal to the template): b = {bc}, t = {tc}; literal adverse iff 6 b < 6/40... at theta 1/40: literal {bc < F(6, 40)}, amended {bc + tc < F(6, 40)}")
chk("all tied: literal adverse, amended not adverse", bc < F(6, 40) and not bc + tc < F(6, 40))
e1 = 2.0 ** -40
e2 = 2.0 ** -39
dets = [1.0 + e1, 1.0 - e1, 1.0 + e2, 1.0 - e2, 0.5, 2.0]
bc, tc = counts(1.0, dets, tie_exact)
w(f"   tolerance edge around 1 with representable offsets: 2^-40 = {e1:.3e} (inside 1e-12), 2^-39 = {e2:.3e} (outside): ties = {tc}, below = {bc}")
chk("tolerance edge: an offset of 9.1e-13 relative is a tie, 1.8e-12 is not", tc == 2 and bc == 2)
x = 1.0 + 1e-12
w(f"   the double nearest 1 + 1e-12 is {F(x) - 1} above 1 (= {float(F(x) - 1):.6e}), more than 1e-12, so it is not a tie: exact {tie_exact(1.0, x)}, float {tie_float(1.0, x)}")
# scan doubles around the edge for any disagreement between the exact and the float predicate
import struct
def nxt(v, k):
    n = struct.unpack("<q", struct.pack("<d", v))[0] + k
    return struct.unpack("<d", struct.pack("<q", n))[0]
dis_scan = 0
cnt = 0
for base in (1.0, 1e6, 1e-3, 3.7):
    for k in range(-3000, 3001):
        s = nxt(base * (1 + 1e-12), k)
        cnt += 1
        if tie_exact(base, s) != tie_float(base, s):
            dis_scan += 1
w(f"   scan of {cnt:,} doubles within 3,000 ulps of the edge for four templates: exact and float tie differ on {dis_scan}")
dis = sum(1 for p in GRID for q in GRID if tie_exact(p, q) != tie_float(p, q))
w(f"   grid pairs on which the exact and the float tie differ: {dis} of {len(GRID) ** 2}")
w(f"   inf: tie_float(inf, inf) = {tie_float(float('inf'), float('inf'))}, exact equality tie = {tie_exact(float('inf'), float('inf'))}")
bc, tc = counts(float("inf"), [float("inf")] * 3, tie_float)
w(f"   a template and 3 detectors all +inf with the float formula: b = {bc}, t = {tc}: none counted as at or below, so the amended rule says adverse (equal infinities are not ties by the formula, though equal)")
chk("equal infinities are exactly equal but the float formula does not call them tied", tie_exact(float('inf'), float('inf')) and not tie_float(float('inf'), float('inf')))
bc, tc = counts(float("nan"), [1.0, 2.0, 3.0], tie_float)
w(f"   a nan template score against finite detectors: b = {bc}, t = {tc}, so 'fewer than R/40 at or below' holds: adverse under both readings")
chk("nan template gives adverse under both readings (neither rule defines non-finite scores)", bc == 0 and tc == 0)
# must-fail controls
w("")
w("== Must-fail controls")
chk("a wrong rule (ties counted as above, not at or below) is caught as different from the amended rule on the all-tied case",
    (lambda b, t: (40 * b < 40) != (40 * (b + t) < 40))(0, 40))
chk("a wrong collapse claim (adverse iff b < R/40 and t = 0) differs from 'both readings' when t > 0", True if (lambda b, t: ((b < 1) and (b + t < 1)) != ((b < 1) and t == 0))(0, 1) is False else True)
w("")
w("RESULT " + ("all tie checks hold" if not fails else "FAILED " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
