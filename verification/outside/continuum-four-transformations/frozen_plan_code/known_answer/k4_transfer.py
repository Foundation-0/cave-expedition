import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from fractions import Fraction
import numpy as np
import controls, nets, par, pipeline, presence, seeds, synth, transfer
from kcommon import header, summary

N = 4096
NBLK = 33
LEN = NBLK * (N + 128)
SHIFT_START = (N + 128) // 2
JS = nets.lag_js("native")


def stream(name, split):
    rng = seeds.rng_for("K4:" + name, split, "native", 0, "data", 0)
    if name == "A":
        return synth.shots_ar(LEN, rng)
    if name == "B":
        return synth.shots_B(LEN, rng)
    if name == "C":
        return synth.shots_ar(LEN, rng)[::-1].copy()
    raise ValueError(name)


def fmt(p):
    return "%.5f" % float(p)


def main():
    header("K4", "transfer: A = shots in AR(1) 0.9; B = shots in 1/f background, half rate, polarity flipped; C = time-reversed shots")
    print("streams of %d samples (%d blocks); runs: primary grid and grid shifted by half a block (start %d); p = largest over runs" % (LEN, NBLK, SHIFT_START))
    print("seed example, A fit data:", seeds.seed_int("K4:A", "fit", "native", 0, "data", 0))
    fitA = stream("A", "fit")
    targets = {"A'": stream("A", "verdict"), "B": stream("B", "verdict"), "C": stream("C", "verdict")}
    runs = (("native", 0), ("shift", SHIFT_START))
    out = {}
    pres = {t: [] for t in targets}
    diagnostics = []
    c5 = None
    for label, start in runs:
        cutA, resA = pipeline.analyse_stream(fitA, "K4:A", "fit", label, JS, N=N, start=start)
        segsA = [c["seg"] for c in cutA]
        t0A, shA = transfer.level_shift(segsA)
        FA = pipeline.t3_features_of(resA, shA)
        FAb = pipeline.t3_features_of(resA, shA, arrow_blind=True)
        w = transfer.build_template(FA[:, 0, :])
        wb = transfer.build_template(FAb[:, 0, :])
        print("run %-6s A fit: %d segments, tau0 %.1f, level shift %d" % (label, len(segsA), t0A, shA))
        for tname, x in targets.items():
            inst = "K4:" + tname.replace("'", "p")
            cut, res = pipeline.analyse_stream(x, inst, "verdict", label, JS, N=N, start=start)
            K, S, pp = pipeline.presence_of(res)
            pres[tname].append(pp)
            t0, sh = transfer.level_shift([c["seg"] for c in cut])
            F = pipeline.t3_features_of(res, sh)
            Fb = pipeline.t3_features_of(res, sh, arrow_blind=True)
            tr = transfer.transfer_test(w, F, seeds.rng_for(inst, "verdict", label, 0, "perm", 0))
            trb = transfer.transfer_test(wb, Fb, seeds.rng_for(inst, "verdict", label, 0, "permblind", 0))
            out[(label, tname)] = (tr, trb)
            # descriptive diagnostic, not scored: template restricted to the u entries, and to the m entries
            mask_u = np.array([1.0 if i % 3 == 0 else 0.0 for i in range(30)])
            diag = []
            for dn, mk in (("u-only", mask_u), ("m-only", 1.0 - mask_u)):
                wd = w * mk
                wd = wd / np.sqrt(wd @ wd)
                td = transfer.transfer_test(wd, F, seeds.rng_for(inst, "verdict", label, 0, "permdiag" + dn, 0), R=2000)
                diag.append("%s AUC %.4f (2.5th pct %.4f, p=%s)" % (dn, td["auc"], td["q025"], fmt(td["p"])))
            diagnostics.append("  diagnostic run %-6s A -> %-2s: %s" % (label, tname, "; ".join(diag)))
            print("  A -> %-2s: presence K=%d of S=%d, p=%.3g | tau0 %.1f shift %d | AUC %.4f, permuted 2.5th pct %.4f, permuted mean %.4f, p=%s (n>=%d)" %
                  (tname, K, S, float(pp), t0, sh, tr["auc"], tr["q025"], tr["perm_mean"], fmt(tr["p"]), tr["n_ge"]))
            if label == "native" and tname == "B":
                # C5: transfer on surrogates, B's C2 series in place of B
                c2 = []
                for q, c in enumerate(cut):
                    c2.append(controls.c2_surrogate_as_data(c["seg"], (inst, "verdict", label, q)))
                import tasks
                res5 = par.pmap(tasks.seg_task, [(s2, ("K4:B-C2", "verdict", label, q), JS, "iaaft", False) for q, s2 in enumerate(c2)])
                cut5 = [{"seg": s2} for s2 in c2]
                K5, S5, pp5 = pipeline.presence_of(res5)
                t05, sh5 = transfer.level_shift([c["seg"] for c in cut5])
                F5 = pipeline.t3_features_of(res5, sh5)
                tr5 = transfer.transfer_test(w, F5, seeds.rng_for("K4:B-C2", "verdict", label, 0, "perm", 0))
                c5 = (K5, S5, tr5)
    par.close()
    pB = presence.combine_runs([out[(l, "B")][0]["p"] for l, _ in runs])
    print("--- criteria")
    ok1 = pB <= Fraction(1, 1000)
    print("A -> B transfer p (largest over runs) = %s, need <= 0.001: %s" % (fmt(pB), "PASS" if ok1 else "FAIL"))
    ok2 = all(out[(l, "C")][0]["auc"] < out[(l, "C")][0]["q025"] for l, _ in runs)
    print("A -> C AUC below 2.5th percentile of permuted templates in every run: %s (%s)" % ("PASS" if ok2 else "FAIL", "; ".join("%s %.4f vs %.4f" % (l, out[(l, "C")][0]["auc"], out[(l, "C")][0]["q025"]) for l, _ in runs)))
    print("--- extras from the plan's controls (descriptive, not in section 10)")
    print("A -> A' (same kind, new data) p (largest over runs) = %s" % fmt(presence.combine_runs([out[(l, "A'")][0]["p"] for l, _ in runs])))
    print("presence on verdict-like streams, instrument p = largest over the two runs: " + ", ".join("%s %.3g" % (t, float(presence.combine_runs(v))) for t, v in pres.items()))
    print("C5 transfer on surrogates (B's C2 series in place of B, primary run): K=%d of S=%d, p=%s, need > 0.01: %s" % (c5[0], c5[1], fmt(c5[2]["p"]), "PASS" if c5[2]["p"] > Fraction(1, 100) else "FAIL"))
    print("--- descriptive diagnostic (not scored, 2,000 permutations): the template cut to its u entries or to its m entries")
    for dl in diagnostics:
        print(dl)
    print("--- must-fail control: arrow-blind template (u replaced by |u|); the A -> C criterion must fail")
    okb = [out[(l, "C")][1]["auc"] < out[(l, "C")][1]["q025"] for l, _ in runs]
    print("arrow-blind A -> C AUC vs 2.5th percentile, per run: " + "; ".join("%s %.4f vs %.4f" % (l, out[(l, "C")][1]["auc"], out[(l, "C")][1]["q025"]) for l, _ in runs))
    flagged = not all(okb)
    print("control %s" % ("FLAGGED (criterion fails for the broken detector)" if flagged else "NOT FLAGGED (the suite cannot tell the broken detector from the real one)"))
    status = "PASS" if (ok1 and ok2 and flagged) else "FAIL"
    summary("K4", status, "A->B p=%s, A->C AUC<q025 %s, arrow-blind control %s" % (fmt(pB), "yes" if ok2 else "no", "flagged" if flagged else "NOT flagged"))


if __name__ == "__main__":
    main()
