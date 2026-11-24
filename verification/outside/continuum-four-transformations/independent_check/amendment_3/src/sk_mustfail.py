"""Must-fail controls and alternative readings for the Amendment 3 seed keys. Standard library only."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk_keys import *
import sk_keys2 as R

def show(name, f):
    n, nk, no, coll, split = f.stats()
    print(f"{name}: events {n:,}, distinct keys {nk:,}, owners {no:,}, collisions {len(coll):,}, flagged {'YES' if coll else 'no'}")
    return len(coll)

res = {}
# 1. old published D14 for K5 flow-unit pools: segment flow-L-q without seed or run, 10 sets of 110 units, 10 seeds
f = Fam("old K5 pools (10 sets)")
sets = [("expo", "verdict"), ("cascade", "fit"), ("cascade", "verdict"), ("cascade_shuffled", "verdict"), ("y", "verdict"),
        ("yprime", "verdict"), ("cascade_iaaft", "fit"), ("cascade_exp", "verdict"), ("cascade_exp", "verdict@amp_exp"), ("cascade_exp", "verdict@amp_scores")]
for s in range(10):
    for i, (c, sp) in enumerate(sets):
        for l, nu in enumerate((32, 32, 31, 15)):
            for q in range(nu):
                owner = ("K5", c, sp, s, l, q, i)
                f.add(owner, key(f"K5b:{c}", sp.split("@")[0], "native", f"flow-L{l}-q{q}", "surrogates"))
res["old K5 pools"] = show("must-fail: published D14, K5 flow-unit pools", f)
# 1b. the same with 14 series per seed, as the independent check counted (adds fit series of four more cases)
f = Fam("old K5 pools (14 sets)")
sets14 = sets + [("expo", "fit"), ("cascade_shuffled", "fit"), ("y", "fit"), ("yprime", "fit")]
for s in range(10):
    for i, (c, sp) in enumerate(sets14):
        for l, nu in enumerate((32, 32, 31, 15)):
            for q in range(nu):
                f.add(("K5", c, sp, s, l, q, i), key(f"K5b:{c}", sp.split("@")[0], "native", f"flow-L{l}-q{q}", "surrogates"))
res["old K5 pools 14"] = show("must-fail: same, 14 series sets per seed (my first count)", f)
# 2. old detectors-flow: key without pair, seed or run
f = Fam("old detectors")
for s in range(10):
    for c, r in [("cascade>cascade_rank", x) for x in R.RUNS5] + [("cascade>yprime", "native"), ("cascade_iaaft>cascade", "native")]:
        f.add(("K5", "det", c, s, r), key("K5b:detectors", "verdict", "native", "0", "detectors-flow"))
res["old K5 det"] = show("must-fail: old detectors-flow (K5, 5 per seed x 10 seeds)", f)
f = Fam("old K4 detectors")
for s in range(10):
    for p in PAIRS4[:3]:
        for run in RUNS4:
            for pur in ("detectors-arrow", "detectors-profile"):
                f.add(("K4", "det", p, s, run, pur), key("K4:detectors", "verdict", "native", s, pur))
res["old K4 det"] = show("must-fail: old K4 detectors without pair and run", f)
# 3. planted fault in the amended rules: drop the run from the Law 2b net, drop the seed from K5 pools, drop the split from K4 pools
orig = R.l2net
R.l2net = lambda i, run: f"law2b-{i}"
res["fault no run in l2b net"] = show("planted fault: Law 2b net without the run (real-data instance tests)", R.fam_l2b_real())
R.l2net = orig
f = Fam("planted K4 pool no split")
for s in range(10):
    for kind in ("A", "B"):
        for sp in ("fit", "verdict"):
            for run in RUNS4:
                for seg in range(32):
                    f.add(("K4", kind, sp, s, run, seg), key(f"K4:{kind}:s{s}", "x", run, seg, "surrogates"))
res["fault no split"] = show("planted fault: K4 pools without the split", f)
# 4. alternative readings of the draft text
f = R.fam_null(net_has_instance=False)
res["null net no instance"] = show("alternative reading: null replicate keys without net law2b-<instance>", f)
f = R.fam_null(net_has_instance=True)
res["null net instance"] = show("draft with net law2b-<instance>:<run> in every replicate draw", f)
# 5. K5 pools of cascade_rank taking the instrument of the series it is cut from = the cascade draw
f = Fam("K5 rank pools by cascade instrument")
for s in range(10):
    for r in R.RUNS5:
        for l, nu in enumerate((32, 32, 31, 15)):
            for q in range(nu):
                f.add(("K5", "cascade_rank", "verdict", s, r, l, q), key("K5b:cascade", "verdict", r, f"s{s}-flow-L{l}-q{q}", "surrogates"))
    for l, nu in enumerate((32, 32, 31, 15)):
        for q in range(nu):
            f.add(("K5", "cascade", "verdict", s, "native", l, q), key("K5b:cascade", "verdict", "native", f"s{s}-flow-L{l}-q{q}", "surrogates"))
res["rank pool reading"] = show("alternative reading: rank-mapped cascade pools use instrument K5b:cascade", f)
# 6. C2 pool without control prefix collides with the segment pool
f = Fam("control pools no prefix")
for ins in R.INS:
    for u in R.real_units(ins):
        if u[2] != "verdict":
            continue
        f.add(("real",) + u, R.ukey(u))
        f.add(("ctl", "C2", "pool") + u, R.ukey(u))
res["control pool"] = show("planted fault: control pools keyed like segment pools (the SK5 fault)", f)
# 7. Which real-data flow-unit F noise segment field without 'stream'
print("Seeds in the rule: first 16 hex digits of SHA-256 as a 64-bit seed; collisions among all distinct keys of the checked families: 0 (see sk_keys2.py)")
need = ["old K5 pools", "old K5 pools 14", "old K5 det", "old K4 det", "fault no run in l2b net", "fault no split", "control pool"]
bad = [k for k in need if not res[k]]
print("must-fail controls all flagged:", "yes" if not bad else "NO: " + ",".join(bad))
