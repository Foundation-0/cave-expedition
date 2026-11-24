"""Exact recomputation of the figures printed in the outside review body (read as data) and of the amendment's
statements about them. Standard library only. No bare assert."""
import sys
from fractions import Fraction
from math import comb

FAILS = []
p = Fraction(1, 20)


def tail(n, pp, k):
    return sum(Fraction(comb(n, j)) * pp**j * (1 - pp)**(n - j) for j in range(k, n + 1))


def d(x, k=8):
    return f"{float(x):.{k}f}"


def check(tag, review, mine_str, ok):
    print(f"REVIEWFIG {tag} | review says {review} | mine {mine_str} | {'AGREES' if ok else 'DIFFERS'}")


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def old_inv(S):
    return sum(Fraction(comb(S, K)) * p**K * (1 - p)**(S - K) for K in range(S + 1) if not (K < (4 if S == 12 else 6) and 10 * K <= S))


def new_inv(S):
    kk = 4 if S == 12 else 6
    return tail(S, p, kk)


for S, single_old_rev, single_new_rev, ratio_rev, inst_rev, any3_rev in ((12, "0.118359", "0.002236", "52.92x", "31.47%", "67.82%"),
                                                                        (32, "0.073805", "0.004599", "16.05x", "20.55%", "49.84%")):
    o, n_ = old_inv(S), new_inv(S)
    print(f"-- S={S}: single control old {d(o)}, new {d(n_)}")
    check(f"S{S} old single", single_old_rev, d(o, 6), abs(float(o) - float(single_old_rev)) < 2e-6)
    check(f"S{S} new single", single_new_rev, d(n_, 6), abs(float(n_) - float(single_new_rev)) < 2e-6)
    check(f"S{S} ratio", ratio_rev, f"{float(o / n_):.2f}x", f"{float(o / n_):.2f}x" == ratio_rev)
    inst = 1 - (1 - o)**3
    check(f"S{S} instrument", inst_rev, f"{float(inst)*100:.2f}%", f"{float(inst)*100:.2f}%" == inst_rev)
    a3 = 1 - (1 - inst)**3
    check(f"S{S} >=1 of 3", any3_rev, f"{float(a3)*100:.2f}%", f"{float(a3)*100:.2f}%" == any3_rev)
i12 = 1 - (1 - old_inv(12))**3
check("S12 >=1 of 4", "77.95%", f"{float(1-(1-i12)**4)*100:.2f}%", f"{float(1-(1-i12)**4)*100:.2f}%" == "77.95%")
i32n = 1 - (1 - new_inv(32))**3
check("S32 new per instrument", "1.37%", f"{float(i32n)*100:.2f}%", f"{float(i32n)*100:.2f}%" == "1.37%")
check("S32 new across 4 instruments", "5.38%", f"{float(1-(1-i32n)**4)*100:.2f}%", f"{float(1-(1-i32n)**4)*100:.2f}%" == "5.38%")
t18, t19, t21 = tail(200, p, 18), tail(200, p, 19), tail(200, p, 21)
check("K2 tail >=18", "0.012089", d(t18, 6), d(t18, 6) == "0.012089")
check("K2 21-class FWER old", "22.54%", f"{float(1-(1-t18)**21)*100:.2f}%", f"{float(1-(1-t18)**21)*100:.2f}%" == "22.54%")
print(f"INFO exact tail at >=19 to 10 digits: {d(t19, 10)} (review prints 0.005823, amendment prints 0.005824)")
check("K2 'K<=18' tail", "0.005823", d(t19, 6), d(t19, 6) == "0.005823")
check("K2 21-class FWER at K<=20 (fail >=21)", "2.41%", f"{float(1-(1-t21)**21)*100:.2f}%", f"{float(1-(1-t21)**21)*100:.2f}%" == "2.41%")
print("K2 catch rates at true per-segment rate 0.08, 200 draws:")
p8 = Fraction(8, 100)
for lab, k in (("review option 1 (pass K<=18, fail >=19)", 19), ("review option 2 (pass K<=20, fail >=21)", 21), ("original plan (fail >=18)", 18)):
    print(f"   {lab}: P(Bin(200,0.08) >= {k}) = {d(tail(200, p8, k), 6)}")
check("TESS 27 d at 20 s", "116,640 samples", f"{27*86400//20:,}", 27 * 86400 // 20 == 116640)
check("TESS zero-padded share", "40/56 = 71.43%", f"{40/56*100:.2f}%", f"{40/56*100:.2f}%" == "71.43%")
check("Arm B 4320*50", "216,000", f"{4320*50:,}", 4320 * 50 == 216000)
control("wrong figure 0.118359 vs 0.19 flagged", abs(float(old_inv(12)) - 0.19) > 2e-6)
control("wrong tail 0.005823 vs 0.0074 flagged", d(t19, 6) != "0.0074")
if FAILS:
    print("FAILED:", FAILS); sys.exit(1)
print("DONE exact_review_numbers")
