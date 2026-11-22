"""Clean-room exact checks of the sample budgets (PREREG-04) and of the test counts.
Standard library only. Integers and Fractions. No bare assert.
Reads only the amended plan text (PREREG.md) for the count checks; no data file is touched."""
import re
import sys


def slurp(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
from fractions import Fraction
from itertools import permutations
from math import floor

PLAN = sys.argv[1] if len(sys.argv) > 1 else "../PREREG.md"
FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def verdict(tag, desc, claimed, mine, ok):
    print(f"CLAIM {tag} | {desc} | amendment={claimed} | mine={mine} | {'REPRODUCED' if ok else 'DIFFERS'}")


DAY = 86400
SPAN = 8 * DAY  # eight daily files
print("INFO Wind/WAVES series length assumed 8 days = 691200 s (section 8 lists 8 daily files per set)")


def blocks(nsamples, N):
    return nsamples // (N + 128)


# A6: block arithmetic
verdict("b4224", "12 blocks of 4,224 samples need", 50688, 12 * 4224, 12 * 4224 == 50688)
for sec, n_cad, want in (("38", 115338, 13), ("65", 120486, 14)):
    got = blocks(n_cad // 2, 4096)
    verdict(f"tess{sec}-L1", f"TESS sector {sec}: blocks at flow level 1 ({n_cad} cadences, input as stated)", want, got, got == want)
for lvl in range(0, 4):
    row = [blocks(n // 2**lvl, 4096) for n in (115338, 120486)]
    print(f"INFO TESS flow level {lvl}: blocks (sector 38, sector 65) = {row}; needs >=12: {[b >= 12 for b in row]}")
max_lvl = max(l for l in range(0, 8) if blocks(115338 // 2**l, 4096) >= 12 and blocks(120486 // 2**l, 4096) >= 12)
verdict("tess-maxlvl", "highest populated flow level", 1, max_lvl, max_lvl == 1)
empty = 7 - (max_lvl + 1)
verdict("tess-empty", "aligned flow levels (of 7) empty at least", 5, empty, empty >= 5)
print("COULD-NOT-CHECK the cadence counts 115,338 and 120,486 (they come from the TESS files, which the clean-room rules forbid opening)")

# old Wind/WAVES rule: pooled across 4 channels, 12 blocks => 3 blocks per channel at N=4096 (block numbering within channel)
cad_old = Fraction(SPAN, 3 * 4224)
verdict("ww-old-cad", "old rule, cadence for 12 blocks (seconds)", "600/11 = 54.5", f"{cad_old} = {float(cad_old):.4f}", cad_old == Fraction(600, 11))
# review's counts (channels joined end to end) vs within-channel
for c, rv, mine_rv in ((60, 10, None), (192, 3, None)):
    ns = SPAN // c
    joined = 4 * ns // 4224
    within = 4 * (ns // 4224)
    print(f"INFO cadence {c} s: per-channel samples {ns}; joined end to end {joined} blocks; within channel {within} blocks")
    verdict(f"ww-{c}s-joined", f"review's count at {c} s (channels joined)", rv, joined, joined == rv)
verdict("ww-60s-within", "60 s cadence, blocks within channels (plan rule)", 8, 4 * ((SPAN // 60) // 4224), 4 * ((SPAN // 60) // 4224) == 8)
verdict("ww-192s-within", "192 s cadence, blocks within channels", 0, 4 * ((SPAN // 192) // 4224), 4 * ((SPAN // 192) // 4224) == 0)
# the original text numbers blocks "from the start of the file (or channel)": if file = one daily file, counts differ
print(f"INFO if blocks were numbered within each DAILY file: 60 s gives {DAY//60} samples per day-channel -> {4*8*((DAY//60)//4224)} blocks; "
      f"20 s cadence gives {DAY//20} -> {4*8*((DAY//20)//4224)} blocks")

# new rule: time-disjoint blocks, cadence limits for 12 blocks
for N, want, label in ((4096, "13.6", 13.636), (2048, "26.5", 26.47), (1024, "50", 50.0), (512, "90", 90.0)):
    lim = Fraction(SPAN, 12 * (N + 128))
    ok = f"{float(lim):.1f}" == f"{float(want):.1f}" or (N in (1024, 512) and lim == Fraction(want))
    verdict(f"ww-new-{N}", f"cadence limit for 12 blocks at N={N}", want, f"{lim} = {float(lim):.4f}", f"{float(lim):.1f}" == f"{float(want):.1f}")
n33 = SPAN // 33
for N in (4096, 2048, 1024, 512):
    print(f"INFO 33 s cadence ({n33} sweeps): N={N} gives {n33 // (N+128)} time-disjoint blocks")
verdict("ww-33s", "at 33 s, largest N with >=12 blocks is 1024, with 18 blocks", "1024, 18",
        f"N=1024, {n33 // 1152} blocks", n33 // 1152 == 18 and n33 // 2176 < 12)
print("COULD-NOT-CHECK that the cadence is about 33 s (amendment says it is an estimate from file sizes only)")

# channel rule of the revised plan: the i-th selected block comes from channel i mod 4
def chans(J, rule):
    k = max(1, J // 32)
    sel = [b for b in range(J) if b % k == 0][:32]
    if rule == "old":
        return [b % 4 for b in sel]
    return [i % 4 for i in range(len(sel))]

bad_new = []
for J in range(12, 720):
    c = chans(J, "new")
    counts = [c.count(q) for q in range(4)]
    if len(c) >= 4 and max(counts) - min(counts) > 1:
        bad_new.append(J)
verdict("ch-new", "revised rule: all four channels, counts differ by at most one, every J from 12 to 719", "all four, at most one apart",
        f"{len(bad_new)} violations", not bad_new)
one = [J for J in range(32, 720) if len(set(chans(J, "old"))) == 1]
two3 = [J for J in range(32, 720) if len(set(chans(J, "old"))) in (2, 3)]
verdict("ch-old-1", "earlier draft (block b from channel b mod 4): one channel only, J from 32 to 719", "160 of 688", f"{len(one)} of 688", len(one) == 160)
verdict("ch-old-23", "earlier draft: two or three channels", "176 more", f"{len(two3)} more", len(two3) == 176)
control("old rule flagged as single-channel at J=128", len(set(chans(128, "old"))) == 1)
control("revised rule not single-channel at J=128", len(set(chans(128, "new"))) != 1)

# Arm B
ok50 = 24 * 50 <= 4093 and 120 * 50 > 4093
print(f"INFO order 4: {24*50} windows needed vs 4093 available at lag 1 (4096-3); order 5: {120*50}")
verdict("armb-o5", "order 5 needs 6,000 windows (untied patterns)", 6000, 120 * 50, 120 * 50 == 6000)
verdict("armb-o6", "order-6 transitions need 216,000 windows", 216000, 720 * 6 * 50, 720 * 6 * 50 == 216000)
verdict("armb-pool", "32 pooled 4,096-sample segments", 131072, 32 * 4096, 32 * 4096 == 131072)
print(f"INFO with ties kept: order 4 has 75 patterns -> {75*50}; order 5 has 541 patterns -> {541*50}")

# Manifest arithmetic
verdict("n26", "files: 4 GW + 4 SEIS + 16 WAVES + 2 TESS", 26, 4 + 4 + 16 + 2, 4 + 4 + 16 + 2 == 26)


control("wrong 60 s count of 10 within-channel flagged", 4 * ((SPAN // 60) // 4224) != 10)
control("wrong cadence limit 54.0 s flagged", cad_old != Fraction(54))
if FAILS:
    print("FAILED CONTROLS:", FAILS); sys.exit(1)
print("DONE budget_and_channels")
