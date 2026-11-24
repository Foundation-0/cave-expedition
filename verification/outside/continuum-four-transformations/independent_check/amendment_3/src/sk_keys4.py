"""Final pass: K4 as reading D20 words it, K5 pool instrument readings, null replicate net. Own key builder. Standard library only."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk_keys import *
import sk_keys2 as R
import sk_keys3b as S

def fam_k4_d20():
    f = Fam("K4 as D20 words it")
    for s in range(10):
        for kind in KINDS4:
            for sp in ("fit", "verdict"):
                f.add(("K4", kind, sp, s, "data"), key(f"K4:{kind}", sp, "native", s, "data"))
        for sp in ("fit", "verdict"):
            f.add(("K4", "A", sp, s, "data"), key("K4:A", sp, "native", s, "data"), "A'fromA")
            f.add(("K4", "Aprime", sp, s, "shuffle"), key(f"K4:Aprime:{sp}", sp, "native", s, "shuffle"))
            for j in range(33):
                f.add(("K4", "Aprime", sp, s, "block", j), key(f"K4:Aprime:{sp}", sp, "native", s, "block-surrogate", j))
        pools = [(k, "fit", ["native"]) for k in ("A", "S", "Sr")]
        pools += [(k, "verdict", ["native", "placement"]) for k in ("B", "C", "Aprime")]
        pools += [(k, "verdict", ["native"]) for k in ("Sr", "S")]
        for k, sp, runs in pools:
            for run in runs:
                for seg in range(32):
                    f.add(("K4", k, sp, s, run, seg, "pool"), key(f"K4:{k}:s{s}", sp, run, seg, "surrogates"))
        dets = [(p, r) for p in ("A>B", "A>C", "A>Aprime") for r in RUNS4] + [("S>Sr", "native"), ("Sr>S", "native")]
        for p, r in dets:
            for pur in ("detectors-arrow", "detectors-profile"):
                f.add(("K4", "det", p, s, r, pur), key(f"K4:{p}", "verdict", r, s, pur))
    return f

def alt_k5_pools():
    """Other reading: pools named by the draw the series is made from."""
    f = Fam("K5 pools, other reading (instrument of the source draw)")
    sets = [("expo", "verdict", "native", "expo"), ("cascade", "fit", "native", "cascade"), ("cascade", "verdict", "native", "cascade"),
            ("cascade_shuffled", "verdict", "native", "cascade_shuffled"), ("y", "verdict", "native", "y"), ("yprime", "verdict", "native", "yprime"),
            ("cascade_iaaft", "fit", "native", "cascade"), ("cascade_rank", "verdict", "native", "cascade"),
            ("cascade_rank", "verdict", "amp_scores", "cascade"), ("cascade_rank", "verdict", "amp_lognormal", "cascade")]
    for s in range(10):
        for c, sp, r, inst in sets:
            for l, nu in enumerate((32, 32, 31, 15)):
                for q in range(nu):
                    f.add(("K5", c, sp, r, s, l, q), key(f"K5b:{inst}", sp, r, f"s{s}-flow-L{l}-q{q}", "surrogates"))
    return f

def show(f):
    n, nk, no, coll, split = f.stats()
    print(f"{f.name}: events {n:,}, distinct keys {nk:,}, owners {no:,}, collisions {len(coll):,}")

if __name__ == "__main__":
    show(fam_k4_d20())
    show(fam_k5(False))
    show(alt_k5_pools())
    show(R.fam_null(net_has_instance=True))
    show(R.fam_null(net_has_instance=False))
    fams = [fam_k1(), fam_k2(), fam_k3(), fam_k4_d20(), fam_k4(True), fam_k5(True), S.real(), S.controls(), S.pre(), S.l2b_real(), S.null()]
    for f in fams[:3] + fams[5:]:
        pass
    cf, nk, nh = R.cross_family(fams)
    print(f"all families with K4 per D20 and the K4 superset: {nk:,} distinct keys, {nh:,} distinct 64-bit seeds, keys with two owners {len(cf)}")
