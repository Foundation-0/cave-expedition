"""Compute estimate for the amended plan, exact rational arithmetic on stated counts.

Unit cost: one pool (a 4,096-sample segment, its normal scores and 99 surrogates, and the statistics) costs
C processor-seconds. C = 229/100 is the builder's measured rate for the frozen plan's K2 (about 9,600
processor-seconds for 4,200 segments per mode). A pool on n samples is costed at C * n / 4096. These are
estimates; the real figures depend on IAAFT convergence and machine load."""
from fractions import Fraction as F
import sys

C = F(229, 100)
out = []
w = out.append


def h(sec):
    return f"{float(sec / 3600):.1f} h"


# relative pool costs of the presence runs (native 1, block mean by 2, subsample by 2, two quantizations,
# window placement, window length N/2, instrument); lengths below 2,048 are no longer confirmatory
presence_runs = [1, F(1, 2), F(1, 2), 1, 1, 1, F(1, 2), 1]
rel_presence = sum(presence_runs)           # 13/2
rel_presence_tess = rel_presence - 1        # no instrument net
kat = {}
kat["K2, 9 classes x 1,000 seeds at 4,096 and 2,048"] = 9 * 1000 * (1 + F(1, 2)) * C
kat["K1 identity of plain, exp and cube pipelines, 14 classes x 20 seeds"] = 14 * 20 * C
kat["K3, 4 cases x 200 seeds over 7 runs, plus the must-fail control at native"] = (4 * 200 * (rel_presence - 1) + 200) * C
kat["K4, 10 seeds, fit and verdict streams (builder: 490 s per seed for one set of streams)"] = 10 * 2 * F(490)
kat["K5, 4 cases x 10 seeds x 2 series (fit and verdict) x 110 units (2^19 samples, levels 0 to 3)"] = 4 * 10 * 2 * 110 * C
kat["Law 2b instance tests needing new pools (W, F, D): 12 cases x 200 seeds at N"] = 3 * 12 * 200 * C
kat["Law 2b instance tests on saved pools (Q, H, M, O4, E, B, R), allowance"] = F(3600)
k_total = sum(kat.values())
w("== known-answer tests, one mode ==")
for k, v in kat.items():
    w(f"{k}: {h(v)}")
w(f"total one mode {h(k_total)}; three modes {h(3 * k_total)}")

fit = 8 * 32 * C + 8 * 150 * C
w(f"== fit stage, one mode: {h(fit)} ==")

conf = {}
conf["presence: 3 instruments x 13/2 + TESS x 11/2 relative, 32 segments, 4 pools (real, C2, C3, C4)"] = (3 * rel_presence + rel_presence_tess) * 32 * 4 * C
conf["arrow and profile transfer: reuse presence pools"] = F(0)
conf["scale flow: 4 instruments x 5 runs x about 150 units x 3 pools (real, C2, C3)"] = 4 * 5 * 150 * 3 * C
c_total = sum(conf.values())
w("== confirmatory verdict run, one mode ==")
for k, v in conf.items():
    w(f"{k}: {h(v)}")
w(f"total one mode {h(c_total)}; three modes {h(3 * c_total)}")

law = {}
law["(a) and (b): new pools for W, F, D on 3 counting instruments, presence runs, 4 pools"] = 3 * 3 * rel_presence * 32 * 4 * C
law["(c): new flow pools for W, F, D, B, R on 3 instruments x 5 runs x 150 units x 3 pools"] = 5 * 3 * 5 * 150 * 3 * C
law["G1 null replicates: 102 tests x 10 (only instances that pass), stop at first failing run, about 2 pools x 32 segments"] = 102 * 10 * 32 * 2 * C
l_total = sum(law.values())
w("== Law 2b search, one mode, worst case (all three adverse types occur) ==")
for k, v in law.items():
    w(f"{k}: {h(v)}")
w(f"total one mode {h(l_total)}; three modes {h(3 * l_total)}")

base = 3 * k_total + 3 * fit + 3 * c_total
w("== totals, processor-hours ==")
w(f"without any adverse outcome: {h(base)}")
w(f"worst case: {h(base + 3 * l_total)}")
w(f"frozen plan, K2 alone, three modes as the builder ran it: {h(3 * 9600)}")
sys.stdout.write("\n".join(out) + "\n")
