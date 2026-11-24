"""Epoch-0 diagnostic (DIAGNOSIS_EPOCH0.md): K4 A to B under both readings of D20, per seed, for more seeds than the 10 of the plan, and with only the pool key or only
the detector key changed. Changes no code under test. An alternative key differs from the real one only in its purpose field (prefix `diag-`).
usage: diag_k4.py <first seed> <last seed> <alt: 0 or 1>      alt=1 also runs the alternative pool key and three alternative detector keys"""
import os
import sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src")); sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, HERE)
import par, keys, pipeline, segments, synth, tasks, transfer
import diag_tasks as dt
import k4_transfer as k4


def rows_for_seed(s, pool_variant, det_variants):
    st = {(k, sp): synth.k4_stream(k, s, sp) for k in ("A", "B") for sp in ("fit", "verdict")}
    sh = {(k, r): transfer.level_shift(k4.cut(st[(k, "fit")], r)) for k in ("A", "B") for r in k4.RUNS}
    plan = [("A", "fit", "native"), ("A", "fit", "placement"), ("B", "verdict", "native"), ("B", "verdict", "placement")]
    jobs, meta = [], []
    for (k, sp, r) in plan:
        for q, sg in enumerate(k4.cut(st[(k, sp)], r)):
            key = keys.k4_pool(k, sp, r, s, q)
            if pool_variant == "alt":
                key = dt.alt_pool_key(key)
            jobs.append((sg, key, "iaaft"))
            meta.append((k, sp, r))
    res = par.pmap(tasks.seg_task, jobs)
    R = {}
    for m, r in zip(meta, res):
        R.setdefault(m, []).append(r)
    out = []
    for dv in det_variants:
        for reading in (1, 2):
            for run in k4.RUNS:
                tg = "native" if reading == 1 else run
                shA, shB = (sh[("A", "native")][1], sh[("B", "native")][1]) if reading == 1 else (sh[("A", run)][1], sh[("B", run)][1])
                ka = keys.k4_detectors("A>B", run, s, "detectors-arrow")
                kp = keys.k4_detectors("A>B", run, s, "detectors-profile")
                if dv != "default":
                    ka = ka[:4] + (dv + "-" + ka[4],) + ka[5:]
                    kp = kp[:4] + (dv + "-" + kp[4],) + kp[5:]
                a, p = pipeline.transfer_arrow_profile(R[("A", "fit", tg)], shA, R[("B", "verdict", run)], shB, keys.rng(ka), keys.rng(kp))
                out.append({"seed": s, "pool": pool_variant, "det": dv, "reading": reading, "run": run, "arrow_p": a["p"], "profile_p": p["p"], "arrow_m": a["m"], "profile_m": p["m"],
                            "shA": shA, "shB": shB, "tauA": sh[("A", tg)][0], "tauB": sh[("B", run if reading == 2 else "native")][0]})
    return out


def passes(rows, seed, pool, det, reading):
    rs = [r for r in rows if r["seed"] == seed and r["pool"] == pool and r["det"] == det and r["reading"] == reading]
    return all(r["arrow_p"] <= Fraction(1, 1000) and r["profile_p"] <= Fraction(1, 1000) for r in rs), rs


def main():
    a, b, alt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rows = []
    for s in range(a, b + 1):
        rows += rows_for_seed(s, "default", ("default", "diag1", "diag2", "diag3") if alt else ("default",))
        if alt:
            rows += rows_for_seed(s, "alt", ("default",))
    par.close()
    for r in rows:
        print("K4DIAG seed %d pool %s det %s reading %d run %s arrow_p %.3e profile_p %.3e m %d/%d shifts A %d B %d tau0 A %g B %g" % (
            r["seed"], r["pool"], r["det"], r["reading"], r["run"], float(r["arrow_p"]), float(r["profile_p"]), r["arrow_m"], r["profile_m"], r["shA"], r["shB"], r["tauA"], r["tauB"]))
    seeds_ = list(range(a, b + 1))
    for pool, det in ([("default", "default")] + ([("default", "diag1"), ("default", "diag2"), ("default", "diag3"), ("alt", "default")] if alt else [])):
        for reading in (1, 2):
            ok = [s for s in seeds_ if passes(rows, s, pool, det, reading)[0]]
            print("SUMMARY pool %s detectors %s reading %d: seeds passing %d of %d" % (pool, det, reading, len(ok), len(seeds_)))


if __name__ == "__main__":
    main()
