"""Recompute the section 11 compute table of the Amendment 2 draft (after B5, B6, B9, B12), the K2 control flag point and the series counts of B5 and B9.
Unit cost 2.29 processor-seconds per 4,096-sample pool, cost proportional to length. Standard library only. No bare assert."""
import sys
from fractions import Fraction as F
from math import comb

FAILS = []
C = F(229, 100)


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def tail(n, p, k):
    return sum(F(comb(n, j)) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))


def kmin(n, p, level):
    for k in range(n + 2):
        if tail(n, p, k) <= level:
            return k


def row(tag, desc, mine, text):
    ok = f"{float(mine):.2f}" == text
    print(f"ROW {tag} | {desc} | mine={float(mine):,.2f} | text={text} | {'REPRODUCED' if ok else 'DIFFERS'}")
    return mine


print("== K2 control flag point")
k200 = kmin(200, F(1, 20), F(1, 1400))
print(f"CLAIM k2c-200 | smallest k with P(Bin(200, 0.05) >= k) <= 0.01/14 | text=22 | mine={k200} | {'REPRODUCED' if k200 == 22 else 'DIFFERS'}")
print(f"INFO tail at 22 {float(tail(200, F(1,20), 22)):.6f}, at 21 {float(tail(200, F(1,20), 21)):.6f}, limit {float(F(1,1400)):.6f}")
k10 = kmin(10, F(1, 20), F(1, 1400))
print(f"CLAIM k2c-10 | the same rule at 10 seeds | text=5 | mine={k10} | {'REPRODUCED' if k10 == 5 else 'DIFFERS'}")
print("== series counts")
per_class_seed = 1 + 3 + 1 + 2 + 6
print(f"CLAIM b5-13 | series per class and seed: plain, 3 maps, negation, exp and cube versions, 3 maps of each | text=13 | mine={per_class_seed} | {'REPRODUCED' if per_class_seed == 13 else 'DIFFERS'}")
print(f"INFO class versions: 9 classes x 3 versions = {9*3} (text 27); (class version, map) cells = {27*3}; with 20 seeds = {27*3*20} cases per length")
b9_series = 1 + 2 + 1 + 1 + 1 + 1 + 3
print(f"CLAIM b9-10 | K5 series per seed: exponential 1, cascade fit and verdict 2, shuffled 1, y_t 1, y' 1, IAAFT cascade 1, exp-mapped cascade in 3 runs 3 | text=10 | mine={b9_series} | {'REPRODUCED' if b9_series == 10 else 'DIFFERS'}")
print("== compute table")
k2 = row("K2", "9 x 1000 x 1.5", 9 * 1000 * F(3, 2) * C, "30915.00")
pools_k1 = 9 * 20 * 13 * F(1, 4) + 7 * 20 * 4 * F(1, 4) + 4
k1 = row("K1", f"(9 x 20 x 13 + 7 x 20 x 4) x 1/4 + 4 = {float(pools_k1)} pools", pools_k1 * C, "1669.41")
gw = 1 + F(1, 2) + F(1, 2) + 1 + 1 + 1 + F(1, 2) + 1
tess = gw - 1
k3 = row("K3", "(4 x 200 x 5.5 + 200) pools", (4 * 200 * (gw - 1) + 200) * C, "10534.00")
k4 = row("K4", "10 x 2 x 490 s (490 measured)", F(10 * 2 * 490), "9800.00")
k5 = row("K5", "10 series x 10 seeds x 110 units", 10 * 10 * 110 * C, "25190.00")
l2n = row("Law2b new pools", "3 x 12 x 200", 3 * 12 * 200 * C, "16488.00")
l2s = F(3600)
l2k4 = row("Law2b paired K4", "3 x K4", 3 * k4, "29400.00")
l2k5 = row("Law2b paired K5", "5 x K5", 5 * k5, "125950.00")
kt = row("known-answer total", "sum", k2 + k1 + k3 + k4 + k5 + l2n + l2s + l2k4 + l2k5, "253546.41")
fit = row("fit stage", "7 x (32 + 150) pools", 7 * (32 + 150) * C, "2917.46")
pres = row("presence", "(3 x 6.5 + 5.5) x 32 x 4", (3 * gw + tess) * 32 * 4 * C, "7328.00")
flow = row("scale flow", "4 x 5 x 150 x 3", 4 * 5 * 150 * 3 * C, "20610.00")
vt = row("verdict total", "sum", pres + flow, "27938.00")
mode = row("one mode", "sum", kt + fit + vt, "284401.87")
three = row("three modes (s)", "3 x", 3 * mode, "853205.61")
print(f"INFO hours: one mode {float(mode/3600):.2f} (text 79.0), three modes {float(three/3600):.2f} (text 237.0)")
w = row("Law2b worst", "(i) + (ii) + (iii)", 9 * gw * 32 * 4 * C + 5 * 3 * 150 * 5 * 3 * C + 10 * 102 * 64 * C, "243926.22")
print(f"INFO worst case hours: per mode {float(w/3600):.2f} (text 67.8), three modes {float(3*w/3600):.2f} (text 203.3)")
print("INFO each non-plan count and its label in the draft table: K4 490 s measured (source: the builder's timing file, named once for the unit cost); 150 flow units assumption; 3,600 s allowance assumption; 64 pools per null replicate assumption; K1 and K5 counts plan; fit stage 7 channels plan, 150 assumption")
control("a wrong total (K1 left at the old 641.20) is not the table's sum", f"{float(kt - k1 + F(64120, 100)):.2f}" != "253546.41")
control("the wrong channel count (8) changes the fit row", f"{float(8*(32+150)*C):.2f}" != "2917.46")
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE compute_and_points")
