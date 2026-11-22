"""Counts the seed keys that the K3, K4 and K5 code actually builds (PREREG section 11, D14). It runs the real seed-making code of
K4 and K5 with the surrogate pools and the transfer tests replaced by stubs, records every call of seeds.rng_for and every pool key
handed to the workers, and counts distinct keys against pools and detectors.
usage: key_count.py <package folder holding src/ and known_answer/> [seeds]     (default 10 seeds; prints the counts)"""
import os
import sys
from fractions import Fraction
PKG = os.path.abspath(sys.argv[1])
NS = int(sys.argv[2]) if len(sys.argv) > 2 else 10
sys.path.insert(0, os.path.join(PKG, "src")); sys.path.insert(0, os.path.join(PKG, "known_answer"))
import numpy as np
import seeds

CALLS = []
_orig = seeds.rng_for


def rec(*a):
    CALLS.append(a)
    return _orig(*a)


seeds.rng_for = rec
import par
JOBS = []


def stub_pmap(fn, items, workers=None):
    items = list(items)
    JOBS.extend((fn.__name__, it) for it in items)
    rng = np.random.default_rng(0)
    out = []
    for it in items:
        if fn.__name__ == "seg_task":
            L = 10
            out.append({"pn": 50, "den": 100, "reject": False, "T": 0.0, "js": list(range(L)), "zu": rng.standard_normal(L), "z1": rng.standard_normal(L),
                        "z23": rng.standard_normal(L), "iters": 0, "nconv": 0, "flag_zero_spread": False, "all_zero_spread": False})
        elif fn.__name__ == "unit_task":
            out.append({"z": rng.standard_normal(9), "S2": 1.0, "n_ge": 50, "departs": False})
        else:
            out.append(None)
    return out


par.pmap = stub_pmap
FAKE = {"p": Fraction(1), "adverse": False, "m": 9, "below_floor": False, "S_A": 0.0, "D": 1, "n_ge": 0}


def classify(calls):
    det = [c for c in calls if len(c) == 6 and str(c[4]).startswith("detectors")]
    return det


def report(name, pool_jobs, det_calls):
    pool_keys = [tuple(j[1]) for (_, j) in pool_jobs]
    seeds_ints = [seeds.seed_int(*k, "surrogates", 0) for k in pool_keys]
    print("%s: pools %d, distinct pool keys %d, distinct pool seeds %d, pools whose key contains the seed number: %s" % (
        name, len(pool_keys), len(set(pool_keys)), len(set(seeds_ints)), "yes" if any(("s%d" % s) in str(k[0]) for k in pool_keys for s in range(NS)) else "no"))
    print("%s: detectors %d, distinct detector keys %d" % (name, len(det_calls), len(set(det_calls))))
    print("%s: example pool key fields (instrument, split, net, segment): %r" % (name, pool_keys[0]))
    print("%s: example detector key: %r" % (name, det_calls[0] if det_calls else None))
    from collections import Counter
    per = Counter((k[0], k[1]) for k in pool_keys)
    print("%s: pools per (instrument, split) over all seeds: %s" % (name, "; ".join("%s %s %d (distinct keys %d)" % (a, b, n, len({k for k in pool_keys if (k[0], k[1]) == (a, b)})) for (a, b), n in sorted(per.items()))))
    inst = sorted({k[0] for k in pool_keys})
    print("%s: pool instruments: %s" % (name, ", ".join(inst)))
    print("%s: pool nets: %s" % (name, ", ".join(sorted({str(k[2]) for k in pool_keys}))))


def run(modname):
    CALLS.clear()
    JOBS.clear()
    mod = __import__(modname)
    if modname == "k5_scale_flow":
        import flow
        import nets
        flow.flow_transfer = lambda *a, **k: dict(FAKE)
        # STUB for counting only: the real exp of the standardised exp-mapped cascade overflows to infinity (see AMENDMENTS_NEEDED.md);
        # keys do not depend on the values, so a clipped exp lets the real seed-making code run on.
        def safe_exp_standardised(x):
            x = np.asarray(x, dtype=np.float64)
            return np.exp(np.clip((x - x.mean()) / x.std(), -50.0, 50.0))
        nets.amp_exp_standardised = safe_exp_standardised
        for s in range(NS):
            mod.one_seed(s)
    else:
        import pipeline
        pipeline.transfer_arrow_profile = lambda *a, **k: (dict(FAKE), dict(FAKE))
        for s in range(NS):
            mod.one_seed(s)
    det = [tuple(c) for c in classify(CALLS)]
    report(modname, JOBS, det)


if __name__ == "__main__":
    # K3: pool keys follow tasks.k3_task: (instrument K3:<case>, split synthetic, net the use, segment the seed number)
    import k3_planted_structure as k3
    items = k3.items(200)
    keys = [("K3:%s" % c, "synthetic", u, i) for (c, u, i, kind) in items]
    seeds_k3 = [seeds.seed_int(*k, "surrogates", 0) for k in keys]
    print("k3_planted_structure (full, 200 seeds): pools %d, distinct pool keys %d, distinct pool seeds %d; the 200 circular-shift control pools share the key of the shots native4096 pools by design" % (len(keys), len(set(keys)), len(set(seeds_k3))))
    print("k3 example pool key:", keys[0])
    run("k4_transfer")
    run("k5_scale_flow")
