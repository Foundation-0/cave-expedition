"""PREREG-04 sample budgets, exact integer and rational arithmetic."""
from fractions import Fraction as F
from math import factorial
import sys

out = []
w = out.append
N, PAD, MIN_SEG = 4096, 128, 12
B = N + PAD
w(f"block length {B}; {MIN_SEG} blocks need {MIN_SEG * B} samples; at coarse-graining level l: {MIN_SEG * B} * 2^l")

# TESS, 20 s cadence. Sector spans from the MAST observation records (t_max - t_min, days).
for name, span in (("sector 38", F(5936005602700231, 10 ** 11) - F(5933335740082176, 10 ** 11)),
                   ("sector 65", F(6009613228145833, 10 ** 11) - F(6006824191372685, 10 ** 11))):
    cad = int(span * 86400 / 20)
    w(f"TESS {name}: span {float(span):.3f} d, at most {cad} cadences before gaps and flags")
    for l in range(4):
        blocks = cad // (2 ** l) // B
        w(f"   level {l}: at most {blocks} blocks{' (>= 12)' if blocks >= MIN_SEG else ' (< 12)'}")
w(f"TESS at most level 1 -> of 7 aligned T1 levels at most 2 populated: {F(5, 7)} = {float(F(5, 7)):.4f} of features zero")

# Wind/WAVES, 8 days.
secs = 8 * 86400
w("Wind/WAVES, 8 days, cadence c seconds per channel:")
for c in (16, 30, 33, 45, 54, 55, 60, 120, 192):
    per = secs // c
    per_channel_blocks = per // B
    w(f"   c={c}: {per} samples per channel; original rule (4 channels, blocks per channel) {4 * per_channel_blocks} blocks; "
      f"concatenated channels {4 * per // B}; time-disjoint blocks of N=4096: {per // B}, "
      f"N=2048: {per // (2048 + PAD)}, N=1024: {per // (1024 + PAD)}, N=512: {per // (512 + PAD)}")
w(f"original rule reaches 12 blocks iff floor({secs}/(c*{B})) >= 3 iff c <= {F(secs, 3 * B)} = {float(F(secs, 3 * B)):.4f} s")
for n in (4096, 2048, 1024, 512):
    w(f"time-disjoint rule reaches 12 blocks of N={n} iff c <= {F(secs, 12 * (n + PAD))} = {float(F(secs, 12 * (n + PAD))):.3f} s")

# Window-length net 2N = 8192 against the other instruments
for name, total in (("GW 4096 s at 4096 Hz", 4096 * 4096), ("SEIS one day at 20 Hz", 86400 * 20)):
    w(f"{name}: blocks of 8192+128: {total // (8192 + PAD)}; of 4096+128: {total // B}; of 1024+128: {total // (1024 + PAD)}")

# Arm B capacity
for d in (4, 5, 6):
    w(f"Arm B: d={d}: {factorial(d)} patterns, 50 per pattern needs {50 * factorial(d)} windows (one segment has {N - (d - 1)}); "
      f"Markov transitions {factorial(d) * d} need {50 * factorial(d) * d}; 32 pooled segments give {32 * N}")
sys.stdout.write("\n".join(out) + "\n")
