import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import controls, nets, par, pipeline, presence, seeds, synth, tasks
from kcommon import header, summary

N = 4096
LEN = 33 * (N + 128)
JS = nets.lag_js("native")


def run_series(series_list, inst, label="native", d4=False):
    jobs = [(s, (inst, "verdict", label, q), JS, "iaaft", d4) for q, s in enumerate(series_list)]
    res = par.pmap(tasks.seg_task, jobs)
    K = sum(1 for r in res if r["reject"])
    return K, len(res), res


def main():
    header("X2", "extra: controls C2, C3, C4 on synthetic shots data, order-4 statistic, and a must-fail control (not a section 10 test)")
    fit = synth.shots_ar(LEN, seeds.rng_for("X2:A", "fit", "native", 0, "data", 0))
    ver = synth.shots_ar(LEN, seeds.rng_for("X2:A", "verdict", "native", 0, "data", 0))
    cutF, _ = pipeline.analyse_stream(fit, "X2:A", "fit", "native", JS[:1], N=N)  # only to cut; one lag keeps this cheap
    fit_segs = [c["seg"] for c in cutF]
    cutV, resV = pipeline.analyse_stream(ver, "X2:A", "verdict", "native", JS, N=N, d4=True)
    K, S, p = pipeline.presence_of(resV)
    print("real verdict-like segments: K=%d of S=%d, presence p=%.3g" % (K, S, float(p)))
    print("order 4 (reported, not part of the verdict): mean standardised T4 %.2f, mean standardised T3 %.2f" % (np.mean([r["T4"] for r in resV]), np.mean([r["T"] for r in resV])))
    vsegs = [c["seg"] for c in cutV]
    rows = []
    c2 = [controls.c2_surrogate_as_data(s, ("X2:A", "verdict", "native", q)) for q, s in enumerate(vsegs)]
    rows.append(("C2 surrogate as data",) + run_series(c2, "X2:C2")[:2])
    c3 = [controls.c3_shuffle(s, ("X2:A", "verdict", "native", q)) for q, s in enumerate(vsegs)]
    rows.append(("C3 shuffle",) + run_series(c3, "X2:C3")[:2])
    c4 = controls.c4_generated_noise(fit_segs, "X2:A", "fit", 32, N)
    rows.append(("C4 generated noise",) + run_series(c4, "X2:C4")[:2])
    ok = True
    for name, K, S in rows:
        absent = presence.control_absent(K, S)
        ok = ok and absent
        print("%-22s K=%d of S=%d, excess point %d, K/S=%.3f: %s" % (name, K, S, presence.excess_point(S), K / S, "ABSENT (pass)" if absent else "PRESENT (fail)"))
    print("--- must-fail control: 'C2' made with a time-arrow-keeping generator (circular shifts) must be flagged as present")
    rng = seeds.rng_for("X2:leaky", "verdict", "native", 0, "data", 0)
    leak = [np.roll(s, int(rng.integers(1, N))) for s in vsegs]
    K, S, _ = run_series(leak, "X2:leakC2")
    absent = presence.control_absent(K, S)
    print("leaky C2: K=%d of S=%d: %s" % (K, S, "NOT FLAGGED (control rule is blind)" if absent else "FLAGGED (present)"))
    status = "PASS" if (ok and not absent) else "FAIL"
    par.close()
    summary("X2", status, "controls C2, C3, C4 absent: %s; leaky control %s" % ("yes" if ok else "NO", "flagged" if not absent else "NOT flagged"))


if __name__ == "__main__":
    main()
