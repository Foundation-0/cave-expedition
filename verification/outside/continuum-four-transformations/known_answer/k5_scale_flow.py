"""K5 Scale flow (PREREG section 10). Every series has 2^19 samples, cut by the segment rule at flow levels 0 to 3 (32, 32, 31 and 15 units).
Per level, a unit "departs" if the sum of its squared standardised features is exceeded or equalled by at most 4 of its 99 surrogates (p <= 0.05); a
level "shows departure" if the departing units are at or above the binomial 1 percent point for its number of units at rate 0.05. 10 seeds per case
(the plan's number), criteria required in at least 9 of 10.
- independent exponential values: no level shows departure.
- dyadic cascade (log-normal weights, mean 1, log sd 0.5): departure at level 0 and at the highest populated level (3).
- the same cascade shuffled in time: no level shows departure. Must-fail control: the cascade criterion (departure at level 0 and level 3) applied to the
  shuffled cascade must hold in at most 1 of 10 seeds.
- y_t = e_t^2 + e_(t-1)^2: departure at level 0 (higher levels reported).
- transfers (primary run, see AMENDMENTS_NEEDED.md): cascade to cascade after exp of the standardised series: p at most 0.001; cascade to y: p above 0.05; shuffled
  cascade to cascade: p above 0.05. Each case has a fit series (tau0 and template) and an independent verdict series (scored).
usage: k5_scale_flow.py smoke|full [part nparts] (parts split the seeds)"""
import os
import sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import flow, levels, nets, par, segments, seeds, synth, tasks, transfer
from kcommon import header, summary, parse_mode, sizes

N = 4096


def stream_jobs(x, instrument, role):
    jobs, meta = flow.stream_units(x, (instrument, role, "native"), N=N)
    return jobs, meta


def one_seed(s):
    ser = {}
    ser[("expo", "verdict")] = synth.k5_series("expo", s, "verdict")
    for case in ("cascade", "cascade_shuffled"):
        ser[(case, "fit")] = synth.k5_series(case, s, "fit")
        ser[(case, "verdict")] = synth.k5_series(case, s, "verdict")
    ser[("y", "fit")] = synth.k5_series("y", s, "fit")
    ser[("y", "verdict")] = synth.k5_series("y", s, "verdict")
    ser[("cascade_exp", "verdict")] = nets.amp_exp_standardised(ser[("cascade", "verdict")])
    tau = {}
    shift = {}
    for case in ("cascade", "cascade_shuffled", "y"):
        segs = [c["seg"] for c in segments.cut_segments(ser[(case, "fit")], N=N)]
        tau[case], shift[case] = transfer.level_shift(segs)
    shift["cascade_exp"] = shift["cascade"]   # the same fit ranks: the exp map does not change tau0
    shift["expo"] = 0
    need = [("expo", "verdict"), ("cascade", "fit"), ("cascade", "verdict"), ("cascade_exp", "verdict"), ("y", "verdict"),
            ("cascade_shuffled", "verdict"), ("cascade_shuffled", "fit")]
    jobs, meta, owner = [], [], []
    for (case, role) in need:
        j, m = stream_jobs(ser[(case, role)], "K5:%s:s%d" % (case, s), role)
        jobs += j
        meta += m
        owner += [(case, role)] * len(j)
    res = par.pmap(tasks.unit_task, jobs)
    U = {}
    for o, m, r in zip(owner, meta, res):
        U.setdefault(o, []).append(dict(l=m[0], q=m[1], **r))
    out = {"seed": s, "tau0": tau, "shift": shift}
    dep = {}
    for case in ("expo", "cascade", "cascade_shuffled", "y"):
        d = flow.level_departure(U[(case, "verdict")])
        dep[case] = {int(l): [int(v[0]), int(v[1]), int(levels.excess_point(v[0]))] for l, v in sorted(d.items())}
    out["departure"] = dep

    def tr(tag, Ac, Bc):
        rng = seeds.rng_for("K5:" + tag, "verdict", "native", s, "detectors-flow", 0)
        r = flow.flow_transfer(U[(Ac, "fit")], shift[Ac], U[(Bc, "verdict")], shift[Bc], rng)
        return {"p": "%d/%d" % (r["p"].numerator, r["p"].denominator), "m": int(r["m"]), "below_floor": bool(r["below_floor"]), "D": int(r["D"]),
                "adverse": bool(r["adverse"]), "S_A": float(r["S_A"])}

    out["T_cascade>cascade_exp"] = tr("cascade>cascade_exp", "cascade", "cascade_exp")
    out["T_cascade>y"] = tr("cascade>y", "cascade", "y")
    out["T_shuffled>cascade"] = tr("shuffled>cascade", "cascade_shuffled", "cascade")
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
    cnt = {"expo none": 0, "cascade L0 and top": 0, "shuffled none": 0, "y L0": 0, "T c>c_exp": 0, "T c>y": 0, "T s>c": 0, "ctrl shuffled shows cascade criterion": 0}
    print("seed  shifts(c,s,y)  departing/units by level: expo | cascade | shuffled | y   transfers p (m, floor): c>cexp | c>y | s>c")
    for r in sorted(results, key=lambda r: r["seed"]):
        D = r["departure"]
        top = max(D["cascade"])
        expo_none = not any(shows(D["expo"], l) for l in D["expo"])
        casc = shows(D["cascade"], 0) and shows(D["cascade"], top)
        shuf_none = not any(shows(D["cascade_shuffled"], l) for l in D["cascade_shuffled"])
        ctop = max(D["cascade_shuffled"])
        ctrl = shows(D["cascade_shuffled"], 0) and shows(D["cascade_shuffled"], ctop)
        yl0 = shows(D["y"], 0)
        t1, t2, t3 = r["T_cascade>cascade_exp"], r["T_cascade>y"], r["T_shuffled>cascade"]
        cnt["expo none"] += expo_none
        cnt["cascade L0 and top"] += casc
        cnt["shuffled none"] += shuf_none
        cnt["y L0"] += yl0
        cnt["T c>c_exp"] += frac(t1["p"]) <= Fraction(1, 1000)
        cnt["T c>y"] += frac(t2["p"]) > Fraction(1, 20)
        cnt["T s>c"] += frac(t3["p"]) > Fraction(1, 20)
        cnt["ctrl shuffled shows cascade criterion"] += ctrl

        def fmt(d):
            return " ".join("L%d:%d/%d" % (l, d[l][1], d[l][0]) for l in sorted(d))
        print("%2d  %s/%s/%s  %s | %s | %s | %s   %.2e(m%d%s) | %.2e(m%d%s) | %.2e(m%d%s)" % (
            r["seed"], r["shift"]["cascade"], r["shift"]["cascade_shuffled"], r["shift"]["y"], fmt(D["expo"]), fmt(D["cascade"]), fmt(D["cascade_shuffled"]), fmt(D["y"]),
            float(frac(t1["p"])), t1["m"], "F" if t1["below_floor"] else "", float(frac(t2["p"])), t2["m"], "F" if t2["below_floor"] else "",
            float(frac(t3["p"])), t3["m"], "F" if t3["below_floor"] else ""))
    print("(F marks a transfer below the populated-feature floor: it counts as not rejecting, p = 1)")
    for k, v in cnt.items():
        if k.startswith("ctrl"):
            print("must-fail control, %s: %d of %d seeds (allowed at most %d)" % (k, v, n, 1 if n == 10 else n // 10))
        else:
            print("criterion %-20s: %d of %d seeds (need %d)" % (k, v, n, need))
    capc = 1 if n == 10 else n // 10
    crit_ok = all(cnt[k] >= need for k in ("expo none", "cascade L0 and top", "shuffled none", "y L0", "T c>c_exp", "T c>y", "T s>c"))
    ctrl_ok = cnt["ctrl shuffled shows cascade criterion"] <= capc
    # vacuous passes: the two p > 0.05 criteria passed only because no feature was populated in both
    vac = sum(1 for r in results for k in ("T_cascade>y", "T_shuffled>cascade") if r[k]["below_floor"])
    print("p > 0.05 criteria that passed only through the populated-feature floor (m below 8): %d of %d seed-transfers" % (vac, 2 * n))
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
