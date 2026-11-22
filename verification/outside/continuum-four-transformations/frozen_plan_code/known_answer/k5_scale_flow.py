import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import flow, par, segments, seeds, synth, tasks
from kcommon import header, summary

N = 4096
LEN = 33 * (N + 128)


def make(kind, idx):
    rng = seeds.rng_for("K5:" + kind, "synthetic", "native", idx, "data", 0)
    if kind == "iid_exponential":
        return rng.exponential(1.0, LEN)
    if kind == "cascade":
        return synth.cascade(LEN, rng)
    if kind == "cascade_shuffled":
        return rng.permutation(synth.cascade(LEN, rng))
    if kind == "exp_ar1_0.5":
        return np.exp(synth.standardise(synth.ar1(0.5, LEN, rng)))
    raise ValueError(kind)


def flow_norms(kind, idx):
    x = make(kind, idx)
    norms = []
    for l, xl in flow.coarse_levels(x, N):
        cut = segments.cut_segments(xl, N=N)
        jobs = [(c["seg"], ("K5:" + kind, "synthetic", "L%d" % l, q)) for q, c in enumerate(cut)]
        feats = par.pmap(tasks.flow_task, jobs)
        mean = np.mean(np.stack([f[0] for f in feats]), axis=0)
        norms.append((l, len(cut), float(np.sqrt(mean @ mean))))
    return norms


def line(kind, idx, norms):
    r = norms[-1][2] / norms[0][2]
    return "%-17s seed idx %d: levels %s | norm level 0 = %.4f, top level (%d) = %.4f, ratio %.3f" % (
        kind, idx, " ".join("L%d:%dseg" % (l, s) for l, s, _ in norms), norms[0][2], norms[-1][0], norms[-1][2], r), r


def main():
    header("K5", "scale flow: decay of the mean flow feature under block averaging by 2")
    print("streams of %d samples; level l has the segments of the section 7 rule on the l-times averaged series; at least 12 segments to count as a level" % LEN)
    print("number of seeds per case is not fixed by the plan: the scored result is seed idx 0 of each case; other seeds are descriptive")
    print("seed example, iid_exponential idx 0:", seeds.seed_int("K5:iid_exponential", "synthetic", "native", 0, "data", 0))
    L1, r_iid = line("iid_exponential", 0, flow_norms("iid_exponential", 0))
    print(L1)
    ok_iid = r_iid < 0.5
    print("criterion: independent exponential values, top-level norm below half the level-0 norm: %s" % ("PASS" if ok_iid else "FAIL"))
    L2, r_cas = line("cascade", 0, flow_norms("cascade", 0))
    print(L2)
    ok_cas = r_cas >= 0.5
    print("criterion: random multiplicative cascade, top-level norm at least half the level-0 norm: %s" % ("PASS" if ok_cas else "FAIL"))
    print("criterion: cascade -> cascade after a monotone map, transfer p <= 0.001: NOT RUN (see AMENDMENTS_NEEDED.md, B1)")
    print("criterion: cascade -> shots, transfer p > 0.05: NOT RUN (see AMENDMENTS_NEEDED.md, B1)")
    print("--- descriptive (not scored)")
    for i in range(1, 6):
        t, r = line("iid_exponential", i, flow_norms("iid_exponential", i))
        print(t + ("  [below half]" if r < 0.5 else "  [not below half]"))
    t, r = line("exp_ar1_0.5", 0, flow_norms("exp_ar1_0.5", 0))
    print(t)
    print("--- must-fail control: the cascade criterion applied to the shuffled cascade (structure destroyed); a useful criterion must fail here")
    Ls, r_sh = line("cascade_shuffled", 0, flow_norms("cascade_shuffled", 0))
    print(Ls)
    flagged = r_sh < 0.5
    print("shuffled cascade passes the 'stays at least half' criterion: %s -> control %s" % ("no" if flagged else "yes", "FLAGGED" if flagged else "NOT FLAGGED (the criterion cannot tell structure from noise)"))
    par.close()
    status = "FAIL" if (not ok_iid or not ok_cas or not flagged) else "INCOMPLETE"
    summary("K5", status, "decay criterion iid %s (ratio %.3f), cascade criterion %s (ratio %.3f), transfer parts NOT RUN, shuffled-cascade control %s" % (
        "PASS" if ok_iid else "FAIL", r_iid, "PASS" if ok_cas else "FAIL", r_cas, "flagged" if flagged else "NOT flagged"))


if __name__ == "__main__":
    main()
