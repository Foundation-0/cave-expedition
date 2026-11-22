"""Amendment 2: component list of the compute estimate, exact decimal arithmetic.
Unit cost C = 2.29 processor-seconds per 4,096-sample pool (the builder's measured rate); a pool on n
samples costs C * n / 4096. Counts are those stated in the plan; nothing here changes a design choice."""
from fractions import Fraction as F
import sys

C = F(229, 100)
rows = [
    ("K2", "9 classes x 1,000 seeds x (1 + 1/2) pools", 9 * 1000 * F(3, 2) * C),
    ("K1 identity check (B5, B6)", "(9 classes x 20 seeds x 13 series + 7 classes x 20 seeds x 4 integer series) x 1/4 pool at 1,024 samples, + 4 pools for the tied waveform", ((9 * 20 * 13 + 7 * 20 * 4) * F(1, 4) + 4) * C),
    ("K3", "(4 cases x 200 seeds x 11/2 pools) + 200 control pools", (4 * 200 * F(11, 2) + 200) * C),
    ("K4", "10 seeds x 2 streams x 490 s (builder's measured cost per set of streams)", F(10 * 2 * 490)),
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
k_total = sum(r[2] for r in rows)
v_total = sum(r[2] for r in verdict)
for name, what, s in rows:
    w(f"{name}: {what}: {fmt(s)}")
w(f"known-answer tests, one mode: {fmt(k_total)}")
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
