"""K5 Scale flow (PREREG section 10, as amended by Amendments 2 and 3). Every series has 2^19 samples, cut by the segment rule at flow levels 0 to 3 (32, 32,
31 and 15 units). A unit departs if at most 4 of its 99 surrogates have a sum of squared standardised features at or above its own (equal sums count as
at or above); a level shows departure if the departing units are at or above the binomial 1 percent point for its units at rate 0.05. 10 seeds per case,
criteria required in at least 9 of 10.
- independent exponential values: no level shows departure. Cascade: departure at level 0 and level 3. Shuffled cascade: no level shows departure
  (must-fail control: the cascade criterion on the shuffled cascade must hold in at most 1 of 10 seeds). y_t = e_t^2 + e_(t-1)^2: departure at level 0.
- transfers: cascade (fit) to the rank-mapped cascade (the mid-ranks of the cascade, verdict) must give p at most 0.001 in the primary run and in both
  amplitude-map runs (amp_scores, amp_lognormal); a seed in which this map or a run's amplitude map fails the representability guard counts as failing the
  criterion. Cascade (fit) to y' = g^2 (verdict, g AR(1), c = 0.9859) and the IAAFT cascade (fit) to the cascade (verdict) must give p above 0.05 in the primary
  run. Every transfer must be evaluable (at least 8 features populated in both series) in at least 9 of 10 seeds, else K5 fails; a seed that is not evaluable
  counts as failing its criterion.
usage: k5_scale_flow.py smoke|full [part nparts] (parts split the seeds)"""
import os
import sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import flow, keys, levels, nets, par, segments, synth, tasks, transfer
from kcommon import header, summary, parse_mode, sizes

N = 4096


def stream_jobs(x, case, role, run, s):
    """Unit jobs of a stream cut into flow units. The pool key names the series the units are cut from (D14): case, split, run, seed, level, unit."""
    return flow.stream_units(x, lambda l, q: keys.k5_pool(case, role, run, s, l, q), N=N)


def one_seed(s):
    ser = {}
    ser[("expo", "verdict")] = synth.k5_series("expo", s, "verdict")
    for case in ("cascade", "yprime"):
        ser[(case, "fit")] = synth.k5_series(case, s, "fit")
        ser[(case, "verdict")] = synth.k5_series(case, s, "verdict")
    ser[("cascade_iaaft", "fit")] = synth.k5_series("cascade_iaaft", s, "fit")
    ser[("cascade_shuffled", "verdict")] = synth.k5_series("cascade_shuffled", s, "verdict")
    ser[("y", "verdict")] = synth.k5_series("y", s, "verdict")
    # the rank-mapped cascade (verdict): the mid-ranks of the cascade (SK8), in three runs. The amplitude nets act on the whole stream (D10).
    rank = nets.midranks(ser[("cascade", "verdict")])
    streams = {("native", "native"): rank, ("amp_scores", "amp_scores"): nets.amp_scores(rank), ("amp_lognormal", "amp_lognormal"): nets.amp_lognormal(rank)}
    guard = {}
    for (run, _), x in streams.items():
        inp = ser[("cascade", "verdict")] if run == "native" else rank
        guard[run] = bool(nets.map_guard_ok(inp, x))
    tau, shift = {}, {}
    for case in ("cascade", "yprime", "cascade_iaaft"):
        segs = [c["seg"] for c in segments.cut_segments(ser[(case, "fit")], N=N)]
        tau[case], shift[case] = transfer.level_shift(segs)
    shift["cascade_rank"] = shift["cascade"]       # the ranks of its fit series are the cascade's, so tau0 is the cascade's
    need = [("expo", "verdict", "native"), ("cascade", "fit", "native"), ("cascade", "verdict", "native"), ("cascade_shuffled", "verdict", "native"),
            ("y", "verdict", "native"), ("yprime", "verdict", "native"), ("cascade_iaaft", "fit", "native")]
    jobs, meta, owner = [], [], []
    for (case, role, run) in need:
        j, m = stream_jobs(ser[(case, role)], case, role, run, s)
        jobs += j
        meta += m
        owner += [(case, role, run)] * len(j)
    for run in ("native", "amp_scores", "amp_lognormal"):
        if guard[run]:
            j, m = stream_jobs(streams[(run, run)], "cascade_rank", "verdict", run, s)
            jobs += j
            meta += m
            owner += [("cascade_rank", "verdict", run)] * len(j)
    res = par.pmap(tasks.unit_task, jobs)
    U = {}
    for o, m, r in zip(owner, meta, res):
        U.setdefault(o, []).append(dict(l=m[0], q=m[1], **r))
    out = {"seed": s, "tau0": tau, "shift": shift, "guard": guard}
    dep = {}
    for case in ("expo", "cascade", "cascade_shuffled", "y"):
        d = flow.level_departure(U[(case, "verdict", "native")])
        dep[case] = {int(l): [int(v[0]), int(v[1]), int(levels.excess_point(v[0]))] for l, v in sorted(d.items())}
    out["departure"] = dep

    def tr(criterion, run, A, B, shA, shB):
        rng = keys.rng(keys.k5_detectors(criterion, run, s))
        r = flow.flow_transfer(U[A], shA, U[B], shB, rng)
        return {"p": "%d/%d" % (r["p"].numerator, r["p"].denominator), "m": int(r["m"]), "below_floor": bool(r["below_floor"]), "D": int(r["D"]),
                "adverse": bool(r["adverse"]), "S_A": float(r["S_A"]), "representable": True}

    for run in ("native", "amp_scores", "amp_lognormal"):
        if guard[run]:
            out["T1|" + run] = tr("cascade>cascade_rank", run, ("cascade", "fit", "native"), ("cascade_rank", "verdict", run), shift["cascade"], shift["cascade"])
        else:    # map not representable: the run does not pass and is never adverse (section 5)
            out["T1|" + run] = {"p": "1/1", "m": 0, "below_floor": True, "D": 1, "adverse": False, "S_A": 0.0, "representable": False}
    out["T2|native"] = tr("cascade>yprime", "native", ("cascade", "fit", "native"), ("yprime", "verdict", "native"), shift["cascade"], shift["yprime"])
    out["T3|native"] = tr("cascade_iaaft>cascade", "native", ("cascade_iaaft", "fit", "native"), ("cascade", "verdict", "native"), shift["cascade_iaaft"], shift["cascade"])
    return out


def frac(s):
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def shows(d, l):
    if l not in d:
        return False
    n, k, thr = d[l]
    return k >= thr


def evaluate(results, nseeds, mode):
    n = len(results)
    need = -(-9 * n // 10)
    names = ["expo none", "cascade L0 and top", "shuffled none", "y L0", "T1 positive (3 runs)", "T2 negative", "T3 negative",
             "T1 evaluable", "T2 evaluable", "T3 evaluable", "ctrl shuffled shows cascade criterion"]
    cnt = {k: 0 for k in names}
    print("seed  shifts(cascade, y', iaaft)  departing/units by level: expo | cascade | shuffled | y   transfers p (m): T1 native, amp_scores, amp_lognormal | T2 | T3")
    for r in sorted(results, key=lambda r: r["seed"]):
        D = r["departure"]
        top = max(D["cascade"])
        cnt["expo none"] += not any(shows(D["expo"], l) for l in D["expo"])
        cnt["cascade L0 and top"] += shows(D["cascade"], 0) and shows(D["cascade"], top)
        cnt["shuffled none"] += not any(shows(D["cascade_shuffled"], l) for l in D["cascade_shuffled"])
        ctop = max(D["cascade_shuffled"])
        cnt["ctrl shuffled shows cascade criterion"] += shows(D["cascade_shuffled"], 0) and shows(D["cascade_shuffled"], ctop)
        cnt["y L0"] += shows(D["y"], 0)
        t1 = [r["T1|" + k] for k in ("native", "amp_scores", "amp_lognormal")]
        t2, t3 = r["T2|native"], r["T3|native"]
        ev1 = all(x["m"] >= 8 for x in t1)
        ev2, ev3 = t2["m"] >= 8, t3["m"] >= 8
        cnt["T1 evaluable"] += ev1
        cnt["T2 evaluable"] += ev2
        cnt["T3 evaluable"] += ev3
        # a seed that is not evaluable counts as failing its criterion
        cnt["T1 positive (3 runs)"] += ev1 and all(x["representable"] and frac(x["p"]) <= Fraction(1, 1000) for x in t1)
        cnt["T2 negative"] += ev2 and frac(t2["p"]) > Fraction(1, 20)
        cnt["T3 negative"] += ev3 and frac(t3["p"]) > Fraction(1, 20)

        def fmt(d):
            return " ".join("L%d:%d/%d" % (l, d[l][1], d[l][0]) for l in sorted(d))
        print("%2d  %s/%s/%s  %s | %s | %s | %s   %s | %.2e(m%d) | %.2e(m%d)" % (
            r["seed"], r["shift"]["cascade"], r["shift"]["yprime"], r["shift"]["cascade_iaaft"], fmt(D["expo"]), fmt(D["cascade"]), fmt(D["cascade_shuffled"]), fmt(D["y"]),
            ", ".join("%.2e(m%d)" % (float(frac(x["p"])), x["m"]) for x in t1), float(frac(t2["p"])), t2["m"], float(frac(t3["p"])), t3["m"]))
    capc = 1 if n == 10 else n // 10
    for k in names:
        if k.startswith("ctrl"):
            print("must-fail control, %s: %d of %d seeds (allowed at most %d)" % (k, cnt[k], n, capc))
        else:
            print("criterion %-24s: %d of %d seeds (need %d)" % (k, cnt[k], n, need))
    crit = [k for k in names if not k.startswith("ctrl")]
    crit_ok = all(cnt[k] >= need for k in crit)
    ctrl_ok = cnt["ctrl shuffled shows cascade criterion"] <= capc
    return ("PASS" if crit_ok and ctrl_ok else "FAIL"), "criteria %s; shuffled-cascade control flagged: %s" % (dict(cnt), ctrl_ok)


def main():
    mode = parse_mode(sys.argv)
    ns = sizes(mode)["K5_SEEDS"]
    part = None
    if len(sys.argv) >= 5:
        part, nparts = int(sys.argv[3]), int(sys.argv[4])
    mine = [s for s in range(ns) if part is None or s % nparts == part]
    header("K5", "scale flow", mode)
    print("seeds: %s of %d (the plan has 10 seeds, so the smoke size equals the full seed count)" % (mine, ns))
    results = []
    for s in mine:
        r = one_seed(s)
        results.append(r)
        if part is not None:
            print("K5SEED", repr(r))
    par.close()
    if part is not None:
        return
    status, text = evaluate(results, ns, mode)
    summary("K5", status, text, mode)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
