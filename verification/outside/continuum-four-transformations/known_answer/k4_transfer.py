"""K4 Transfer (PREREG section 10, reading D20 of Amendment 3). Synthetic A: the K3 shots. B: shots at twice the rate on 1/f noise, every second
sample kept, sign flipped. C: the time reverse of a fresh series of kind A. Each instrument has two independent streams per seed (fit, verdict) of
33 blocks, so the primary grid and the grid shifted by half a block both give 32 segments. 10 seeds.
K4 passes only if it passes under both readings of its stream set (D20):
  reading 1 (D20): templates from the fit streams of A, S and Sr cut in the primary grid, reused by the placement run; level shifts from the fit
    streams of every kind (A' included) in the primary grid; pools for the verdict streams of B, C and A' in both runs and for S and Sr in the
    primary run; detectors for A>B, A>C and A>Aprime in both runs and for S>Sr and Sr>S in the primary run.
  reading 2: each run takes its templates and level shifts from the fit streams cut in that run's own grid, and the blind spot is scored in both runs.
Criteria within each reading: A to B arrow p and profile p at most 0.001 in every run, in at least 9 of 10 seeds. A to C arrow adverse in every run, in
at least 9 of 10 seeds (the profile transfer A to C is reported), where a run is adverse as reading D8 defines it after Amendment 4 (fewer than R/40
of the detectors at or below S_B(w_A), ties counted as at or below). Must-fail control A to A' (A cut into its 33 blocks, the block order shuffled and each
block replaced by an IAAFT surrogate of itself, with its own fit stream made the same way): neither the arrow nor the profile transfer may reach p at
most 0.01 in more than 1 of 10 seeds, where a seed reaches it if p is at most 0.01 in any run, judged within each reading. Blind spot, reported: sawtooth
and its time reverse, arrow and profile transfer in both directions.
Every draw uses the run's key epoch (reading D14 as amended by Amendment 4). A run with a non-finite score is neither adverse nor passing (D8); READING
(AMENDMENTS_NEEDED.md): such a run counts as failing the criterion it enters, and in the control as reaching p at most 0.01, so it can never help K4 pass.
usage: k4_transfer.py smoke [epoch=0] [part=<p>/<n>] | full epoch=<k> [part=<p>/<n>] (parts split the seeds; join them with k4_combine.py)"""
import ast
import os
import sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import iaaft, keys, par, pipeline, ranks, segments, synth, tasks, transfer
from kcommon import header, summary, parse_cli, sizes

N = 4096
BLK = N + segments.PAD
RUNS = ("native", "placement")
KINDS = ("A", "B", "C", "Aprime", "S", "Sr")


def surrogate_blocks_stream(stream, split, seed_idx, epoch):
    """A': the A stream of the same split cut into its 33 blocks, block order shuffled and each block replaced by an IAAFT surrogate of itself.
    The draws use keys.k4_aprime_shuffle and keys.k4_aprime_block (index the block's position in the shuffled order), in the run's key epoch."""
    blocks = [stream[i * BLK:(i + 1) * BLK] for i in range(len(stream) // BLK)]
    order = keys.rng(keys.k4_aprime_shuffle(split, seed_idx), epoch).permutation(len(blocks))
    out = []
    for pos, k in enumerate(order):
        Y, _, _ = iaaft.iaaft_surrogates(blocks[int(k)], 1, keys.rng(keys.k4_aprime_block(split, seed_idx, pos), epoch))
        out.append(Y[0])
    return np.concatenate(out)


def cut(stream, run):
    start = (BLK // 2) if run == "placement" else 0
    return [c["seg"] for c in segments.cut_segments(stream, N=N, start=start)]


def one_seed(s, epoch):
    """All K4 quantities for one seed, under both readings, with every draw in the key epoch `epoch`. Returns a dict of literals."""
    st = {}
    for kind in ("A", "B", "C", "S", "Sr"):
        for split in ("fit", "verdict"):
            st[(kind, split)] = synth.k4_stream(kind, s, split, epoch=epoch)
    for split in ("fit", "verdict"):
        st[("Aprime", split)] = surrogate_blocks_stream(st[("A", split)], split, s, epoch)
    # level shifts from the fit streams cut in each grid (no pools); reading 1 uses the primary grid for every run
    shifts = {}
    for kind in KINDS:
        for run in RUNS:
            shifts[(kind, run)] = transfer.level_shift(cut(st[(kind, "fit")], run))
    # pools: reading 1 (D20), then the extra pools of reading 2
    plan = [("A", "fit", "native")]
    for k in ("B", "C", "Aprime"):
        plan += [(k, "verdict", "native"), (k, "verdict", "placement")]
    plan += [("S", "fit", "native"), ("Sr", "verdict", "native"), ("Sr", "fit", "native"), ("S", "verdict", "native")]
    plan += [("A", "fit", "placement"), ("S", "fit", "placement"), ("Sr", "fit", "placement"), ("S", "verdict", "placement"), ("Sr", "verdict", "placement")]
    jobs, meta = [], []
    for (k, split, run) in plan:
        for q, sg in enumerate(cut(st[(k, split)], run)):
            jobs.append((sg, keys.k4_pool(k, split, run, s, q), "iaaft", epoch))
            meta.append((k, split, run))
    res = par.pmap(tasks.seg_task, jobs)
    R = {}
    for m, r in zip(meta, res):
        R.setdefault(m, []).append(r)
    out = {"seed": s, "tau0": {"%s|%s" % (k, r): shifts[(k, r)][0] for (k, r) in shifts}, "shift": {"%s|%s" % (k, r): shifts[(k, r)][1] for (k, r) in shifts}}

    def lit(r):
        return {"p": "%d/%d" % (r["p"].numerator, r["p"].denominator), "adverse": bool(r["adverse"]), "m": int(r["m"]),
                "below_floor": bool(r["below_floor"]), "S_A": float(r["S_A"]), "D": int(r["D"]), "n_ge": int(r["n_ge"]),
                "n_le": int(r["n_le"]), "nonfinite": bool(r["nonfinite"])}

    def tr(pair, run, reading):
        Ak, Bk = pair.split(">")
        if reading == 1:
            tmpl_grid, shA, shB = "native", shifts[(Ak, "native")][1], shifts[(Bk, "native")][1]
        else:
            tmpl_grid, shA, shB = run, shifts[(Ak, run)][1], shifts[(Bk, run)][1]
        rng_a = keys.rng(keys.k4_detectors(pair, run, s, "detectors-arrow"), epoch)
        rng_p = keys.rng(keys.k4_detectors(pair, run, s, "detectors-profile"), epoch)
        a, p = pipeline.transfer_arrow_profile(R[(Ak, "fit", tmpl_grid)], shA, R[(Bk, "verdict", run)], shB, rng_a, rng_p)
        return {"arrow": lit(a), "profile": lit(p)}

    for reading in (1, 2):
        pairs = [(p_, r) for p_ in ("A>B", "A>C", "A>Aprime") for r in RUNS]
        pairs += [(p_, "native") for p_ in ("S>Sr", "Sr>S")] if reading == 1 else [(p_, r) for p_ in ("S>Sr", "Sr>S") for r in RUNS]
        for (p_, r) in pairs:
            out["r%d:%s|%s" % (reading, p_, r)] = tr(p_, r, reading)
    return out


def frac(s):
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def evaluate_reading(results, nseeds, reading):
    """Criteria of one reading. Returns (ok, counts dict, lines)."""
    n = len(results)
    need = -(-9 * n // 10)
    cap = 1 if n == 10 else n // 10
    ab_ok = ac_ok = ctrl_arrow = ctrl_prof = 0
    blind_arrow = blind_prof = blind_tot = 0
    n_nonfinite = 0
    lines = []
    for r in sorted(results, key=lambda r: r["seed"]):
        g = lambda pair, run: r["r%d:%s|%s" % (reading, pair, run)]
        ab = [g("A>B", run) for run in RUNS]
        ac = [g("A>C", run) for run in RUNS]
        ap = [g("A>Aprime", run) for run in RUNS]
        # a run with a non-finite score is neither adverse nor passing (D8); it counts as failing its criterion (READING)
        ab_pass = all(frac(x["arrow"]["p"]) <= Fraction(1, 1000) and frac(x["profile"]["p"]) <= Fraction(1, 1000)
                      and not x["arrow"]["nonfinite"] and not x["profile"]["nonfinite"] for x in ab)
        ac_pass = all(x["arrow"]["adverse"] and not x["arrow"]["nonfinite"] for x in ac)
        # any run, within this reading (D17, D20); a non-finite run counts against the control (READING)
        ap_arrow = min(frac(x["arrow"]["p"]) for x in ap) <= Fraction(1, 100) or any(x["arrow"]["nonfinite"] for x in ap)
        ap_prof = min(frac(x["profile"]["p"]) for x in ap) <= Fraction(1, 100) or any(x["profile"]["nonfinite"] for x in ap)
        n_nonfinite += sum(int(x[t]["nonfinite"]) for x in ab + ac + ap for t in ("arrow", "profile"))
        ab_ok += ab_pass
        ac_ok += ac_pass
        ctrl_arrow += ap_arrow
        ctrl_prof += ap_prof
        bl = []
        for pair in ("S>Sr", "Sr>S"):
            for run in (RUNS if reading == 2 else ("native",)):
                x = g(pair, run)
                bl.append("%s %s arrow %.3f profile %.3f" % (pair, run, float(frac(x["arrow"]["p"])), float(frac(x["profile"]["p"]))))
                blind_tot += 1
                blind_arrow += frac(x["arrow"]["p"]) <= Fraction(1, 100)
                blind_prof += frac(x["profile"]["p"]) <= Fraction(1, 100)
        lines.append("%2d  AB arrow %s profile %s | AC adverse %s %s, profile p %s | A>Aprime min p arrow %.2e profile %.2e | blind: %s | m AB %s floor %s" % (
            r["seed"], " ".join("%.2e" % float(frac(x["arrow"]["p"])) for x in ab), " ".join("%.2e" % float(frac(x["profile"]["p"])) for x in ab),
            ac[0]["arrow"]["adverse"], ac[1]["arrow"]["adverse"], " ".join("%.2e" % float(frac(x["profile"]["p"])) for x in ac),
            float(min(frac(x["arrow"]["p"]) for x in ap)), float(min(frac(x["profile"]["p"]) for x in ap)), "; ".join(bl), ab[0]["arrow"]["m"], ab[0]["arrow"]["below_floor"]))
    ok = ab_ok >= need and ac_ok >= need and ctrl_arrow <= cap and ctrl_prof <= cap
    lines.append("reading %d: A to B passes in %d of %d seeds (need %d). A to C arrow adverse in every run in %d of %d (need %d)." % (reading, ab_ok, n, need, ac_ok, n, need))
    lines.append("reading %d: must-fail control A to A' reaches p <= 0.01 in any run: arrow in %d, profile in %d of %d seeds (allowed at most %d each)" % (reading, ctrl_arrow, ctrl_prof, n, cap))
    lines.append("reading %d: blind spot (reported): arrow rejects (p <= 0.01) in %d and profile in %d of %d seed-direction-runs" % (reading, blind_arrow, blind_prof, blind_tot * 1))
    lines.append("reading %d: transfer runs of A to B, A to C and A to A' with a non-finite score: %d (each counts as failing its criterion)" % (reading, n_nonfinite))
    lines.append("reading %d: %s" % (reading, "PASS" if ok else "FAIL"))
    return ok, {"ab": ab_ok, "ac": ac_ok, "ctrl_arrow": ctrl_arrow, "ctrl_prof": ctrl_prof}, lines


def evaluate(seed_results, nseeds):
    oks, texts = [], []
    for reading in (1, 2):
        ok, counts, lines = evaluate_reading(seed_results, nseeds, reading)
        print("--- reading %d (%s)" % (reading, "D20: templates and shifts from the primary-grid fit streams" if reading == 1 else "each run uses the fit streams of its own grid"))
        for ln in lines:
            print(ln)
        oks.append(ok)
        texts.append("reading %d A>B %d/%d, A>C %d/%d, control arrow %d profile %d" % (reading, counts["ab"], len(seed_results), counts["ac"], len(seed_results), counts["ctrl_arrow"], counts["ctrl_prof"]))
    return ("PASS" if all(oks) else "FAIL"), "; ".join(texts) + "; K4 passes only if both readings pass"


def main():
    run = parse_cli(sys.argv, seeded=True, parts=True, test="K4")
    ns = sizes(run["mode"])["K4_SEEDS"]
    part, nparts = run["part"], run["nparts"]
    mine = [s for s in range(ns) if part is None or s % nparts == part]
    header("K4", "transfer", run)
    print("seeds: %s of %d (the plan has 10 seeds, so the smoke size equals the full seed count)" % (mine, ns))
    results = []
    for s in mine:
        r = one_seed(s, run["epoch"])
        results.append(r)
        if part is not None:
            print("K4SEED", repr(r))
    par.close()
    if part is not None:
        return
    status, text = evaluate(results, ns)
    summary("K4", status, text, run)


if __name__ == "__main__":
    main()
