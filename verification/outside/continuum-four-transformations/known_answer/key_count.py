"""Counts the seed keys that the K3, K4 and K5 code actually builds (PREREG section 11, D14). It runs the real seed-making code of
K4 and K5 with the surrogate pools and the transfer tests replaced by stubs, records every call of seeds.rng_for and every pool key
handed to the workers, and counts distinct keys against pools and detectors.
It runs on key epoch 0 only. The epoch handed to one_seed is a numpy integer 0 (EPOCH below), and the count checks that this very object reaches
every call of seeds.rng_for and the last field of every work item, so a draw that took its epoch from anywhere but the run (a literal 0, a default)
would be found (reading D14 as amended by Amendment 4).
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
EPOCHS = []
EPOCH = np.int64(0)
_orig = seeds.rng_for


def rec(*a, epoch):
    CALLS.append(a)
    EPOCHS.append(epoch)
    return _orig(*a, epoch=epoch)


seeds.rng_for = rec
import par
JOBS = []
_orig_pmap = par.pmap


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
FAKE = {"p": Fraction(1), "adverse": False, "m": 9, "below_floor": False, "S_A": 0.0, "D": 1, "n_ge": 0, "n_lt": 0, "n_tie": 0, "n_le": 0, "n_nonfinite": 0,
        "nonfinite": False}


def classify(calls):
    det = [c for c in calls if len(c) == 6 and str(c[4]).startswith("detectors")]
    return det


def report(name, pool_jobs, det_calls):
    pool_keys = [tuple(j[1]) for (_, j) in pool_jobs]
    seeds_ints = [seeds.seed_int(*k, epoch=0) for k in pool_keys]
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


def compare_with_plan_keys(modname, pool_jobs, calls):
    """The keys the real K4 or K5 code built, against the keys that key_check.py builds from src/keys.py at the plan's counts."""
    import key_check
    fam = key_check.fam_k4(False) if modname == "k4_transfer" else key_check.fam_k5(False)
    want = set(fam.key_owner)
    got = {seeds.seed_string(*tuple(j[1]), epoch=0) for (_, j) in pool_jobs}
    for c in calls:
        if len(c) == 6 and (str(c[4]) in ("data", "shuffle", "block-surrogate", "whole-surrogate") or str(c[4]).startswith("detectors")):
            got.add(seeds.seed_string(*c, epoch=0))
    print("%s: keys the code built %d, keys of the plan's check %d, code keys not in the plan's list %d, plan keys the code did not build %d" % (
        modname, len(got), len(want), len(got - want), len(want - got)))
    print("%s: the code builds exactly the plan's keys: %s" % (modname, "yes" if got == want else "NO"))


def run(modname):
    CALLS.clear()
    EPOCHS.clear()
    JOBS.clear()
    mod = __import__(modname)
    if modname == "k5_scale_flow":
        import flow
        flow.flow_transfer = lambda *a, **k: dict(FAKE)
    else:
        import pipeline
        pipeline.transfer_arrow_profile = lambda *a, **k: (dict(FAKE), dict(FAKE))
    for s in range(NS):
        mod.one_seed(s, EPOCH)
    det = [tuple(c) for c in classify(CALLS)]
    report(modname, JOBS, det)
    compare_with_plan_keys(modname, JOBS, [tuple(c) for c in CALLS])
    own = sum(1 for e in EPOCHS if e is EPOCH) + sum(1 for (_, j) in JOBS if j[-1] is EPOCH)
    print("%s: draws made %d and work items %d; each received the run's epoch object: %s" % (
        modname, len(EPOCHS), len(JOBS), "yes" if own == len(EPOCHS) + len(JOBS) else "NO (%d of %d)" % (own, len(EPOCHS) + len(JOBS))))


def spawn_check():
    """Worker processes that par.pmap starts with the spawn method draw in the epoch their work items carry. A key of no test (instrument
    unit-epoch) on epoch 1, 3 workers, against the same tasks run in this process on epochs 1 and 0."""
    import synth
    import tasks
    jobs = [(synth.standardise(synth.ar1(0.7, 256, np.random.default_rng(20 + q))), ("unit-epoch", "synthetic", "native", q, "surrogates", 0), "iaaft", 1) for q in range(3)]
    try:
        spawned = _orig_pmap(tasks.seg_task, jobs, 3)
    finally:
        par.close()
    same = all(a["pn"] == b["pn"] and np.array_equal(a["zu"], b["zu"]) for a, b in zip(spawned, [tasks.seg_task(j) for j in jobs]))
    other = any(not np.array_equal(a["zu"], b["zu"]) for a, b in zip(spawned, [tasks.seg_task(j[:3] + (0,)) for j in jobs]))
    print("spawned workers (3) draw in the epoch of their work items: %s (same as in this process on epoch 1: %s; differ from epoch 0: %s)" % (
        "yes" if same and other else "NO", same, other))


if __name__ == "__main__":
    # K3: pool keys follow keys.k3_pool (instrument K3:<case>:<length>, split synthetic, net the use, segment the seed number)
    import keys as keymod
    import k3_planted_structure as k3
    items = k3.items(200, EPOCH)
    k3keys = [keymod.k3_pool(c, u, i) for (c, u, i, kind, _) in items]
    seeds_k3 = [seeds.seed_int(*k, epoch=0) for k in k3keys]
    print("k3_planted_structure: every work item carries the run's epoch object: %s" % ("yes" if all(it[-1] is EPOCH for it in items) else "NO"))
    print("k3_planted_structure (full, 200 seeds): pools %d, distinct pool keys %d, distinct pool seeds %d; the 200 circular-shift control pools share the key of the shots native4096 pools by design" % (len(k3keys), len(set(k3keys)), len(set(seeds_k3))))
    print("k3 example pool key:", k3keys[0])
    run("k4_transfer")
    run("k5_scale_flow")
    spawn_check()
