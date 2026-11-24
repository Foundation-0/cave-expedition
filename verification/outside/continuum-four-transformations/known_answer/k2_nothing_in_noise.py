"""K2 Nothing found in noise (PREREG section 10). 9 classes at 4,096 and 2,048 samples, 1,000 seeds per class (smoke: one
twentieth, at least 10). K2a: the 7 null classes, flagged at the binomial point for the check level 0.01 / 14.
K2b: the 2 reversible non-Gaussian classes, flagged where P(Binomial(n, 0.10) >= k) <= 0.01 / 4, reported with Clopper-Pearson
99 percent intervals. Must-fail control: raw-value surrogates on AR(1) 0.9 after exp at 4,096 samples (200 seeds; smoke: 10).
usage: k2_nothing_in_noise.py smoke|full [part nparts]. With part and nparts the script prints counts only (join with k2_combine.py)."""
import os
import sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import levels, par, synth, tasks
from kcommon import header, summary, parse_mode, sizes

LENGTHS = (4096, 2048)
CTRL_CLASS = "ar1_0.9|exp"


def items(ns, nctrl):
    out = []
    for n in LENGTHS:
        for cls in synth.K2_CLASSES:
            for idx in range(ns):
                out.append((cls, n, idx, "iaaft"))
    for idx in range(nctrl):
        out.append((CTRL_CLASS, 4096, idx, "raw"))
    return out


def _tail_ge(n, k, p):
    """P(Binomial(n, p) >= k) in floating point (log-space terms). For the reported intervals only."""
    import math
    if k <= 0:
        return 1.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    lp, lq = math.log(p), math.log1p(-p)
    t = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq for i in range(k, n + 1)]
    m = max(t)
    return min(1.0, math.exp(m) * sum(math.exp(v - m) for v in t))


def clopper_pearson(k, n, conf=0.99):
    """Exact (Clopper-Pearson) interval by bisection on the binomial tails; floats, reported only (no decision uses it)."""
    a = (1.0 - conf) / 2.0
    lo, hi = 0.0, 1.0
    if k > 0:
        l, h = 0.0, 1.0
        for _ in range(60):
            m = (l + h) / 2
            if _tail_ge(n, k, m) < a:
                l = m
            else:
                h = m
        lo = h
    if k < n:
        l, h = 0.0, 1.0
        for _ in range(60):
            m = (l + h) / 2
            if 1.0 - _tail_ge(n, k + 1, m) > a:
                l = m
            else:
                h = m
        hi = l
    return lo, hi


def evaluate(counts, ns, nctrl, mode):
    """counts: dict (cls, n, kind) -> rejections. Prints the table and returns (status, text)."""
    fa = levels.smallest_k(ns, Fraction(1, 100) / 14)
    fb = levels.smallest_k(ns, Fraction(1, 100) / 4, Fraction(1, 10))
    fc = levels.smallest_k(nctrl, Fraction(1, 100) / 14)
    print("seeds per class %d (plan 1000); K2a flag point %d of %d (plan 74 of 1000); K2b flag point %d of %d (plan 129 of 1000)" % (ns, fa, ns, fb, ns))
    print("class                 n      rejections  rate    flagged   99 percent CP interval")
    flagged_any_a = flagged_any_b = False
    for n in LENGTHS:
        for cls in synth.K2_CLASSES:
            k = counts[(cls, n, "iaaft")]
            isb = cls in synth.K2B_CLASSES
            fl = k >= (fb if isb else fa)
            lo, hi = clopper_pearson(k, ns)
            flagged_any_b = flagged_any_b or (fl and isb)
            flagged_any_a = flagged_any_a or (fl and not isb)
            print("%-20s %5d  %6d/%-5d %.4f  %-8s  [%.4f, %.4f]  %s" % (cls, n, k, ns, k / ns, "FLAG" if fl else "no", lo, hi, "K2b (reported; flag stops the run)" if isb else "K2a"))
    kc = counts[(CTRL_CLASS, 4096, "raw")]
    ctrl_flag = kc >= fc
    print("must-fail control (raw-value surrogates, %s, 4096): %d of %d reject; flag point %d of %d (K2a rule at this n): %s" % (CTRL_CLASS, kc, nctrl, fc, nctrl, "FLAGGED" if ctrl_flag else "NOT FLAGGED"))
    ok = (not flagged_any_a) and (not flagged_any_b) and ctrl_flag
    return ("PASS" if ok else "FAIL"), "K2a flagged: %s; K2b flagged: %s; control flagged: %s" % (flagged_any_a, flagged_any_b, ctrl_flag)


def main():
    mode = parse_mode(sys.argv)
    sz = sizes(mode)
    ns, nctrl = sz["K2_SEEDS"], sz["K2_CTRL_SEEDS"]
    if mode == "smoke":
        nctrl = 10
    part = None
    if len(sys.argv) >= 5:
        part, nparts = int(sys.argv[3]), int(sys.argv[4])
    allitems = items(ns, nctrl)
    mine = allitems if part is None else [it for i, it in enumerate(allitems) if i % nparts == part]
    header("K2", "nothing found in noise", mode)
    print("segments in this run: %d of %d%s" % (len(mine), len(allitems), "" if part is None else " (part %d of %d)" % (part, nparts)))
    res = par.pmap(tasks.k2_task, mine)
    counts = {}
    tot = {}
    zero = 0
    for (cls, n, idx, kind), r in zip(mine, res):
        key = (cls, n, kind)
        counts[key] = counts.get(key, 0) + (1 if r["reject"] else 0)
        tot[key] = tot.get(key, 0) + 1
        zero += 1 if r["zero"] else 0
    print("segments with a zero-spread lag: %d" % zero)
    if part is not None:
        for key in sorted(counts):
            print("K2COUNT %s %d %s %d %d" % (key[0], key[1], key[2], counts[key], tot[key]))
        par.close()
        return
    status, text = evaluate(counts, ns, nctrl, mode)
    par.close()
    summary("K2", status, text, mode)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
