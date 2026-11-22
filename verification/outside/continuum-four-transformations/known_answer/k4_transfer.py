"""K4 Transfer (PREREG section 10). Synthetic A: the K3 shots. B: shots at twice the rate on 1/f noise, every second sample kept, sign flipped.
C: the time reverse of a fresh series of kind A. Each instrument has two independent streams per seed (fit, verdict) of 33 blocks, so the
primary grid and the grid shifted by half a block both give 32 segments. Templates and tau0 come from fit streams only; scores from verdict
streams only. 10 seeds (the plan's number; smoke uses all 10 because the smoke rule says at least 10).
Runs: the primary grid and the shifted grid (synthetic instruments have no second channel).
- A to B: arrow p and profile p at most 0.001 in every run, in at least 9 of 10 seeds.
- A to C: the arrow score S_B(w_A) below the 2.5th percentile of its random detectors in every run, in at least 9 of 10 seeds. The profile
  transfer A to C is reported.
- Must-fail controls: A to A' (A with its blocks shuffled in time order and each block replaced by an IAAFT surrogate of itself): neither the
  arrow nor the profile transfer may reach p at most 0.01 (largest p over the runs) in more than 1 of 10 seeds.
- Blind spot, reported: sawtooth and its time reverse, arrow transfer in both directions (primary run), expected not to reject.
usage: k4_transfer.py smoke|full [part nparts] (parts split the seeds)"""
import ast
import os
import sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import iaaft, par, pipeline, ranks, segments, seeds, synth, transfer
from kcommon import header, summary, parse_mode, sizes

N = 4096
BLK = N + segments.PAD
RUNS = ("native", "placement")


def surrogate_blocks_stream(stream, tag, seed_idx):
    """A': the stream cut into its 33 blocks, block order shuffled, each block replaced by an IAAFT surrogate of itself."""
    blocks = [stream[i * BLK:(i + 1) * BLK] for i in range(len(stream) // BLK)]
    rng = seeds.rng_for("K4:Aprime:" + tag, "verdict", "native", seed_idx, "shuffle", 0)
    order = rng.permutation(len(blocks))
    out = []
    for q, k in enumerate(order):
        Y, _, _ = iaaft.iaaft_surrogates(blocks[int(k)], 1, seeds.rng_for("K4:Aprime:" + tag, "verdict", "native", seed_idx, "block-surrogate", q))
        out.append(Y[0])
    return np.concatenate(out)


def cut(stream, run):
    start = (BLK // 2) if run == "placement" else 0
    return [c["seg"] for c in segments.cut_segments(stream, N=N, start=start)]


def shift_of(stream):
    t0, sh = transfer.level_shift(cut(stream, "native"))
    return t0, sh


def one_seed(s):
    """All K4 quantities for one seed. Returns a dict of literals."""
    st = {}
    for kind in ("A", "B", "C"):
        st[(kind, "fit")] = synth.k4_stream(kind, s, "fit")
        st[(kind, "verdict")] = synth.k4_stream(kind, s, "verdict")
    st[("Ap", "fit")] = surrogate_blocks_stream(st[("A", "fit")], "fit", s)
    st[("Ap", "verdict")] = surrogate_blocks_stream(st[("A", "verdict")], "verdict", s)
    for kind in ("S", "Sr"):
        st[(kind, "fit")] = synth.k4_stream(kind, s, "fit")
        st[(kind, "verdict")] = synth.k4_stream(kind, s, "verdict")
    shifts = {k: shift_of(st[(k, "fit")]) for k in ("A", "B", "C", "Ap", "S", "Sr")}
    # jobs: (stream key, split, run)
    plan = [("A", "fit", "native")]
    for k in ("B", "C", "Ap"):
        plan += [(k, "verdict", "native"), (k, "verdict", "placement")]
    plan += [("S", "fit", "native"), ("Sr", "verdict", "native"), ("Sr", "fit", "native"), ("S", "verdict", "native")]
    jobs, meta = [], []
    for (k, split, run) in plan:
        segs = cut(st[(k, split)], run)
        for q, sg in enumerate(segs):
            jobs.append((sg, ("K4:%s:s%d" % (k, s), split, run, q), "iaaft"))
            meta.append((k, split, run))
    import tasks
    res = par.pmap(tasks.seg_task, jobs)
    R = {}
    for m, r in zip(meta, res):
        R.setdefault(m, []).append(r)
    out = {"seed": s, "tau0": {k: shifts[k][0] for k in shifts}, "shift": {k: shifts[k][1] for k in shifts}}

    def tr(Akey, Bkey, run, tag):
        rng_a = seeds.rng_for("K4:" + tag, "verdict", run, s, "detectors-arrow", 0)
        rng_p = seeds.rng_for("K4:" + tag, "verdict", run, s, "detectors-profile", 0)
        a, p = pipeline.transfer_arrow_profile(R[(Akey, "fit", "native")], shifts[Akey][1], R[(Bkey, "verdict", run)], shifts[Bkey][1], rng_a, rng_p)
        return a, p

    def lit(r):
        return {"p": "%d/%d" % (r["p"].numerator, r["p"].denominator), "adverse": bool(r["adverse"]), "m": int(r["m"]),
                "below_floor": bool(r["below_floor"]), "S_A": float(r["S_A"]), "D": int(r["D"]), "n_ge": int(r["n_ge"])}

    for tag, Bk in (("A>B", "B"), ("A>C", "C"), ("A>Ap", "Ap")):
        for run in RUNS:
            a, p = tr("A", Bk, run, tag)
            out["%s|%s" % (tag, run)] = {"arrow": lit(a), "profile": lit(p)}
    # blind spot, primary run
    for tag, A_, B_ in (("S>Sr", "S", "Sr"), ("Sr>S", "Sr", "S")):
        rng_a = seeds.rng_for("K4:" + tag, "verdict", "native", s, "detectors-arrow", 0)
        rng_p = seeds.rng_for("K4:" + tag, "verdict", "native", s, "detectors-profile", 0)
        a, p = pipeline.transfer_arrow_profile(R[(A_, "fit", "native")], shifts[A_][1], R[(B_, "verdict", "native")], shifts[B_][1], rng_a, rng_p)
        out["%s|native" % tag] = {"arrow": lit(a), "profile": lit(p)}
    return out


def frac(s):
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def evaluate(seed_results, nseeds, mode):
    n = len(seed_results)
    ab_ok = ac_ok = 0
    ctrl_arrow = ctrl_prof = 0
    print("seed  tau0 A/B/C/A'/S/Sr   shifts   A>B p arrow (native, placement)   A>B p profile      A>C arrow adverse S_A (native, placement)   A>C profile p   A>Ap max p arrow/profile   blind S>Sr, Sr>S arrow p")
    for r in sorted(seed_results, key=lambda r: r["seed"]):
        ab = [r["A>B|%s" % run] for run in RUNS]
        ac = [r["A>C|%s" % run] for run in RUNS]
        ap = [r["A>Ap|%s" % run] for run in RUNS]
        ab_pass = all(frac(x["arrow"]["p"]) <= Fraction(1, 1000) and frac(x["profile"]["p"]) <= Fraction(1, 1000) for x in ab)
        ac_pass = all(x["arrow"]["adverse"] for x in ac)
        ap_arrow = max(frac(x["arrow"]["p"]) for x in ap) <= Fraction(1, 100)
        ap_prof = max(frac(x["profile"]["p"]) for x in ap) <= Fraction(1, 100)
        ab_ok += ab_pass
        ac_ok += ac_pass
        ctrl_arrow += ap_arrow
        ctrl_prof += ap_prof
        bl = [r["S>Sr|native"]["arrow"], r["Sr>S|native"]["arrow"]]
        print("%2d  %s  %s  AB %s %s | %s %s  AC %s %s | prof p %s %s  Ap %s/%s  blind %s %s  [m AB %s, floor %s]" % (
            r["seed"], "/".join("%g" % r["tau0"][k] for k in ("A", "B", "C", "Ap", "S", "Sr")), "/".join(str(r["shift"][k]) for k in ("A", "B", "C", "Ap", "S", "Sr")),
            "%.2e" % float(frac(ab[0]["arrow"]["p"])), "%.2e" % float(frac(ab[1]["arrow"]["p"])),
            "%.2e" % float(frac(ab[0]["profile"]["p"])), "%.2e" % float(frac(ab[1]["profile"]["p"])),
            ac[0]["arrow"]["adverse"], ac[1]["arrow"]["adverse"],
            "%.2e" % float(frac(ac[0]["profile"]["p"])), "%.2e" % float(frac(ac[1]["profile"]["p"])),
            "%.2e" % float(max(frac(x["arrow"]["p"]) for x in ap)), "%.2e" % float(max(frac(x["profile"]["p"]) for x in ap)),
            "%.3f" % float(frac(bl[0]["p"])), "%.3f" % float(frac(bl[1]["p"])),
            ab[0]["arrow"]["m"], ab[0]["arrow"]["below_floor"]))
    need = -(-9 * n // 10)
    print("A to B passes (arrow and profile p <= 0.001 in every run): %d of %d seeds (need %d)" % (ab_ok, n, need))
    print("A to C arrow adverse in every run: %d of %d seeds (need %d)" % (ac_ok, n, need))
    cap = (n + 9) // 10 if n < 20 else n // 10
    cap = 1 if n == 10 else n // 10
    print("must-fail control A to A' reaches p <= 0.01: arrow in %d, profile in %d of %d seeds (allowed at most %d each)" % (ctrl_arrow, ctrl_prof, n, cap))
    blind = sum(1 for r in seed_results for k in ("S>Sr|native", "Sr>S|native") if frac(r[k]["arrow"]["p"]) <= Fraction(1, 100))
    print("blind spot (reported): arrow transfer rejects (p <= 0.01) in %d of %d seed-directions" % (blind, 2 * n))
    ok = ab_ok >= need and ac_ok >= need and ctrl_arrow <= cap and ctrl_prof <= cap
    return ("PASS" if ok else "FAIL"), "A>B %d/%d, A>C %d/%d, control arrow %d profile %d (cap %d)" % (ab_ok, n, ac_ok, n, ctrl_arrow, ctrl_prof, cap)


def main():
    mode = parse_mode(sys.argv)
    ns = sizes(mode)["K4_SEEDS"]
    part = None
    if len(sys.argv) >= 5:
        part, nparts = int(sys.argv[3]), int(sys.argv[4])
    mine = [s for s in range(ns) if part is None or s % nparts == part]
    header("K4", "transfer", mode)
    print("seeds: %s of %d (the plan has 10 seeds, so the smoke size equals the full seed count)" % (mine, ns))
    results = []
    for s in mine:
        r = one_seed(s)
        results.append(r)
        if part is not None:
            print("K4SEED", repr(r))
    par.close()
    if part is not None:
        return
    status, text = evaluate(results, ns, mode)
    summary("K4", status, text, mode)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
