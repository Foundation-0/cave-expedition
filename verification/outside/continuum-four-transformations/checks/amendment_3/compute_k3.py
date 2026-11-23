"""Amendment 3, item SK9: the compute estimate with the K3 row following section 10's eight uses, exact arithmetic.
K3 uses and their pool sizes (a pool on n samples costs n/4096 of a 4,096-sample pool): native4096 1, native2048 1/2,
bm2 1/2 (block mean by 2 of 4,096 samples), sub2 1/2, q12 1, q8 1, placement 1, wlen2048 1/2, in all 6 pools per case
and seed. Amendment 2 priced 11/2 pools for 7 runs, leaving out native2048. A row is added for the second reading of
D20 (K4), 1,600 pools at 4,096 samples. Every other row is Amendment 2's.
Unit cost C = 2.29 processor-seconds per 4,096-sample pool (the builder's measured rate); a pool on n
samples costs C * n / 4096. Counts are those stated in the plan; nothing here changes a design choice."""
from fractions import Fraction as F
import sys

C = F(229, 100)
K3_USES = (("native4096", F(1)), ("native2048", F(1, 2)), ("bm2", F(1, 2)), ("sub2", F(1, 2)), ("q12", F(1)), ("q8", F(1)),
           ("placement", F(1)), ("wlen2048", F(1, 2)))
K3_POOLS = sum(p for _, p in K3_USES)
if K3_POOLS != 6 or len(K3_USES) != 8:
    raise SystemExit("K3 uses do not sum to 6 pools over 8 uses")
rows = [
    ("K2", "9 classes x 1,000 seeds x (1 + 1/2) pools", 9 * 1000 * F(3, 2) * C),
    ("K1 identity check (B5, B6)", "(9 classes x 20 seeds x 13 series + 7 classes x 20 seeds x 4 integer series) x 1/4 pool at 1,024 samples, + 4 pools for the tied waveform", ((9 * 20 * 13 + 7 * 20 * 4) * F(1, 4) + 4) * C),
    ("K3", "(4 cases x 200 seeds x 6 pools (8 uses)) + 200 control pools", (4 * 200 * K3_POOLS + 200) * C),
    ("K4", "10 seeds x 2 streams x 490 s (builder's measured cost per set of streams)", F(10 * 2 * 490)),
    ("K4, second reading of D20", "10 seeds x 160 pools (fit streams of A, S, Sr and verdict streams of S, Sr, 32 segments each, placement grid)", 10 * 160 * C),
    ("K5 (B9)", "10 series x 10 seeds x 110 units x 1 pool", 10 * 10 * 110 * C),
    ("Law 2b instance tests, new pools (W, F, D)", "3 instances x 12 cases x 200 seeds x 1 pool", 3 * 12 * 200 * C),
    ("Law 2b instance tests, saved pools", "allowance (assumption)", F(3600)),
    ("Law 2b instances, paired K4 on new pools (W, F, D)", "3 instances x the K4 cost above", 3 * F(10 * 2 * 490)),
    ("Law 2b instances, paired K5 on new pools (W, F, D, B, R)", "5 instances x the K5 cost above", 5 * 10 * 10 * 110 * C),
]
fit = ("Fit stage", "7 channels x (32 segments + 150 flow units, an assumption) x 1 pool", 7 * (32 + 150) * C)
verdict = [
    ("Presence", "(3 x 13/2 + 11/2) pools x 32 segments x 4", (3 * F(13, 2) + F(11, 2)) * 32 * 4 * C),
    ("Arrow and profile transfers", "reuse presence pools", F(0)),
    ("Scale flow", "4 instruments x 5 runs x 150 units x 3 pools", 4 * 5 * 150 * 3 * C),
]
law = [
    ("Law 2b worst case: new presence pools (W, F, D)", "3 instances x 3 instruments x 13/2 x 32 x 4", 3 * 3 * F(13, 2) * 32 * 4 * C),
    ("Law 2b worst case: new flow pools (W, F, D, B, R)", "5 x 3 instruments x 5 runs x 150 units x 3", 5 * 3 * 5 * 150 * 3 * C),
    ("Law 2b worst case: G1 null replicates", "102 tests x 10 x 32 segments x 2 pools", 102 * 10 * 32 * 2 * C),
]


def fmt(sec):
    return f"{float(sec):,.2f} s ({float(sec / 3600):.3f} h)"


out = []
w = out.append
w("K3 uses: " + ", ".join("%s %s" % (u, p) for u, p in K3_USES) + "; pools per case and seed: %s" % K3_POOLS)
old_k3 = (4 * 200 * F(11, 2) + 200) * C
k_total = sum(r[2] for r in rows)
v_total = sum(r[2] for r in verdict)
for name, what, s in rows:
    w(f"{name}: {what}: {fmt(s)}")
w(f"known-answer tests, one mode: {fmt(k_total)}")
w(f"K3 change against Amendment 2: {fmt((4 * 200 * K3_POOLS + 200) * C - old_k3)}")
w(f"{fit[0]}: {fit[1]}: {fmt(fit[2])}")
for name, what, s in verdict:
    w(f"{name}: {what}: {fmt(s)}")
w(f"confirmatory verdict run, one mode: {fmt(v_total)}")
per_mode = k_total + fit[2] + v_total
w(f"one mode without an adverse outcome: {fmt(per_mode)}")
w(f"three modes without an adverse outcome: {fmt(3 * per_mode)}")
l_total = sum(r[2] for r in law)
for name, what, s in law:
    w(f"{name}: {what}: {fmt(s)}")
w(f"Law 2b worst case, one mode: {fmt(l_total)}; three modes: {fmt(3 * l_total)}")
sys.stdout.write("\n".join(out) + "\n")
