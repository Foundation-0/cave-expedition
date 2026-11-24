"""SK9: the K3 row and every total, exact rational arithmetic. Standard library only."""
from fractions import Fraction as F
import sys
out = []; w = out.append; fails = []
def chk(n, ok, d=""):
    w(f"[{'ok' if ok else 'FAIL'}] {n}{(': ' + d) if d else ''}")
    if not ok: fails.append(n)
unit = F(229, 100)
uses = {"native4096": F(4096, 4096), "native2048": F(2048, 4096), "bm2 (4096 -> 2048)": F(2048, 4096), "sub2 (4096 -> 2048)": F(2048, 4096),
        "q12": F(1), "q8": F(1), "placement": F(1), "wlen2048": F(2048, 4096)}
per = sum(uses.values())
chk("eight uses price 6 pools per case and seed", per == 6, str(per))
k3 = (4 * 200 * per + 200) * unit
chk("K3 row 11,450.00", k3 == F(11450), f"{float(k3):,.2f}")
old = (4 * 200 * F(11, 2) + 200) * unit
chk("old K3 row 10,534.00 (7 runs at 5.5 pools, native2048 left out)", old == F(10534), f"{float(old):,.2f}")
chk("difference 916.00", k3 - old == 916)
rows = [F("30915.00"), F("1669.41"), k3, F("9800.00"), 10 * 160 * unit, F("25190.00"), F("16488.00"), F("3600.00"), F("29400.00"), F("125950.00")]
tot = sum(rows)
chk("K4 second-reading row 3,664.00", 10 * 160 * unit == F(3664))
chk("known-answer total 258,126.41 (sum of the ten rows)", tot == F("258126.41"), f"{float(tot):,.2f}")
chk("old total 253,546.41 without the K3 correction and the new row", tot - 916 - 3664 == F("253546.41"))
fit, pres, flow = F("2917.46"), F("7328.00"), F("20610.00")
conf = pres + flow
chk("confirmatory total 27,938.00", conf == F("27938.00"))
one = tot + fit + conf
chk("one mode 288,981.87", one == F("288981.87"), f"{float(one):,.2f}")
chk("hours 80.3", round(float(one / 3600), 1) == 80.3, f"{float(one/3600):.3f}")
chk("three modes 866,945.61", 3 * one == F("866945.61"))
chk("three-mode hours 240.8", round(float(3 * one / 3600), 1) == 240.8, f"{float(3*one/3600):.3f}")
law = F("17147.52") + F("77287.50") + F("149491.20")
chk("Law 2b paired K4 row 29,400.00 = 3 x 9,800 (D20 alone)", 3 * F("9800.00") == F("29400.00"))
chk("Law 2b worst case 243,926.22 unchanged", law == F("243926.22"))
chk("Law 2b worst hours 67.8 and 203.3 (three modes)", round(float(law / 3600), 1) == 67.8 and round(float(3 * law / 3600), 1) == 203.3, f"{float(law/3600):.3f}, {float(3*law/3600):.3f}")
chk("Law 2b K2 and K3 row unchanged: 12 cases x 200 seeds x 3 instances x 2.29 = 16,488.00", 12 * 200 * 3 * unit == F(16488))
chk("must-fail: pricing the old 5.5 pools gives a different row", old != k3)
w("RESULT " + ("all SK9 figures reproduced" if not fails else "FAILED " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
