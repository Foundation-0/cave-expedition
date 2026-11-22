import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import nets, par, seeds, stats43
from kcommon import header, summary

NSEED = 200
NOISE_SD = 0.5 / np.sqrt(12.0)  # half the standard deviation of the noiseless sawtooth (0.2887)


def task(a):
    net, idx = a
    rng = seeds.rng_for("X4:sawtooth_sd", "synthetic", "native", idx, "data", 0)
    ph = int(rng.integers(0, 64))
    x = ((np.arange(4096) + ph) % 64) / 64.0 + NOISE_SD * rng.standard_normal(4096)
    y = nets.apply(net, x)
    return stats43.analyse(y, ("X4:sawtooth_sd", "synthetic", net, idx), nets.lag_js(net))["reject"]


def main():
    header("X4", "extra, descriptive: K3 sawtooth with the other reading of 'noise of half its amplitude' (noise sd = half the sawtooth's standard deviation)")
    print("not a plan test; the K3 verdict for the sawtooth stays as K3 reports it with the first reading (AMENDMENTS_NEEDED.md, A6)")
    nl = ("native", "bm2", "whiten")
    res = par.pmap(task, [(n, i) for n in nl for i in range(NSEED)])
    par.close()
    parts = []
    for k, n in enumerate(nl):
        nd = sum(1 for r in res[k * NSEED:(k + 1) * NSEED] if r)
        print("sawtooth, noise sd %.4f, net %-7s detect %3d of %d, rate %.3f" % (NOISE_SD, n, nd, NSEED, nd / NSEED))
        parts.append("%s %.3f" % (n, nd / NSEED))
    summary("X4", "DESCRIPTIVE", "sawtooth rates, second reading: " + ", ".join(parts))


if __name__ == "__main__":
    main()
