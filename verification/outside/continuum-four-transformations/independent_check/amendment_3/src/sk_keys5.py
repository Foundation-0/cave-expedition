"""K4 under D20 and under its second reading, own key builder. Standard library only."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk_keys import *
import sk_keys2 as R
import sk_keys3b as S
import sk_keys4 as D

def fam_k4_both(second=True):
    f = D.fam_k4_d20()
    f.name = "K4 under D20 and its second reading" if second else "K4 under D20 alone"
    if not second:
        return f
    for s in range(10):
        # second reading, placement run: templates and level shifts from fit streams cut in the placement grid
        for k in ("A", "S", "Sr"):
            for seg in range(32):
                f.add(("K4", k, "fit", s, "placement", seg, "pool"), key(f"K4:{k}:s{s}", "fit", "placement", seg, "surrogates"))
        # blind spot scored in both runs: verdict S and Sr pools in the placement grid
        for k in ("S", "Sr"):
            for seg in range(32):
                f.add(("K4", k, "verdict", s, "placement", seg, "pool"), key(f"K4:{k}:s{s}", "verdict", "placement", seg, "surrogates"))
        # detectors of the placement run: A>B, A>C, A>Aprime keep D20's keys (shared); S>Sr and Sr>S are new
        for p in ("A>B", "A>C", "A>Aprime", "S>Sr", "Sr>S"):
            for pur in ("detectors-arrow", "detectors-profile"):
                f.add(("K4", "det", p, s, "placement", pur), key(f"K4:{p}", "verdict", "placement", s, pur), "second reading" if p in ("A>B", "A>C", "A>Aprime") else "")
    return f

if __name__ == "__main__":
    a = fam_k4_both(False); b = fam_k4_both(True)
    for f in (a, b):
        n, nk, no, coll, sp = f.stats()
        print(f"{f.name}: draws {n:,}, distinct keys {nk:,}, owners {no:,}, collisions {len(coll)}, owner-two-keys {len(sp)}")
    shared = sum(1 for o, k, t in b.ev if t == "second reading")
    print(f"second-reading draws on a key D20 already uses: {shared}; new pool draws {1600}; new detector sets {sum(1 for o,k,t in b.ev if o[1]=='det' and o[4]=='placement' and o[2] in ('S>Sr','Sr>S'))}")
    base = [fam_k1(), fam_k2(), fam_k3(), fam_k4(True), fam_k5(True), S.real(), S.controls(), S.pre(), S.l2b_real(), S.null()]
    cf0, n0, h0 = R.cross_family(base)
    cf1, n1, h1 = R.cross_family(base + [b])
    print(f"all families with the K4 superset: {n0:,} keys; adding the D20 and second-reading K4 family: {n1:,} keys, two-owner keys {len(cf1)}")
    # must-fail: a second reading keyed without the run (placement pools under the native net) collides with D20's primary pools
    bad = Fam("planted fault")
    for s in range(10):
        for k in ("A", "S", "Sr"):
            for seg in range(32):
                bad.add(("K4", k, "fit", s, "native", seg), key(f"K4:{k}:s{s}", "fit", "native", seg, "surrogates"))
                bad.add(("K4", k, "fit", s, "placement", seg), key(f"K4:{k}:s{s}", "fit", "native", seg, "surrogates"))
    n, nk, no, coll, sp = bad.stats()
    print(f"planted fault (second reading keyed with the primary net): {n} draws, {nk} keys, flagged {'YES' if coll else 'no'}")
