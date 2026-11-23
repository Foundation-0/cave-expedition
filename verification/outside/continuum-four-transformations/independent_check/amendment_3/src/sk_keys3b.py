"""Second rebuild at the scope of the author's table (upper bounds: all 4 instruments, 12 ordered pairs, fit side on the native net),
with my own key builder and my own owner naming. Standard library only. Read sk_keys.py and sk_keys2.py first."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk_keys import *
import sk_keys2 as R

CH = R.CH
INS = R.INS
def inst_chan(ins, run):
    return CH[ins][1] if run == "instrument" else CH[ins][0]
UNITS = R.UNITS
def units_list():
    """(kind, ins, channel, split, net, segment_label) at the upper bounds."""
    out = []
    for ins in INS:
        for run in R.runs_for(ins, R.PRES_RUNS):
            for q in range(32):
                out.append(("seg", ins, inst_chan(ins, run), "verdict", run, q))
        for run in R.runs_for(ins, R.FLOW_RUNS):
            for (l, q) in UNITS:
                out.append(("unit", ins, inst_chan(ins, run), "verdict", run, f"flow-L{l}-q{q}"))
        for ch in [c for c in CH[ins] if c]:
            for q in range(32):
                out.append(("seg", ins, ch, "fit", "native", q))
            for (l, q) in UNITS:
                out.append(("unit", ins, ch, "fit", "native", f"flow-L{l}-q{q}"))
    return out
U = units_list()
def K(u, net=None, purpose="surrogates", idx=0):
    kind, ins, ch, sp, net0, seg = u
    return key(f"{ins}:{ch}", sp, net or net0, seg, purpose, idx)
PAIRS = [(a, b) for a in INS for b in INS if a != b]
PRES_I, ARR_I, FLOW_I = R.PRES_INST, R.ARR_INST, R.FLOW_INST
CHG_P, CHG_F = R.CHG_PRES, R.CHG_FLOW
l2 = R.l2net

def real():
    f = Fam("Real data pools and detectors")
    for u in U:
        f.add(("pool",) + u, K(u))
    for a, b in PAIRS:
        for r in R.TR_RUNS:
            for pur in ("detectors-arrow", "detectors-profile"):
                for rep in range(3):
                    f.add(("det", a, b, r, pur), key(f"{a}>{b}", "verdict", r, 0, pur), "C5" if rep else "")
        for r in R.FLOW_RUNS:
            for rep in range(3):
                f.add(("det", a, b, r, "flow"), key(f"{a}>{b}", "verdict", r, 0, "detectors-flow"), "C5" if rep else "")
    return f

def controls():
    f = Fam("Controls with pools")
    for u in U:
        if u[3] != "verdict":
            continue
        f.add(("pool",) + u, K(u))
        for c in ("C2", "C3"):
            f.add((c, "series") + u, K(u, purpose=c))
            f.add((c, "pool") + u, K(u, purpose=c + "-surrogates"))
    for ins in INS:
        for run in R.runs_for(ins, R.PRES_RUNS):
            ch = inst_chan(ins, run)
            for i in range(32):
                f.add(("C4", ins, ch, run, i), key(f"{ins}:{ch}", "verdict", run, i, "C4"))
                f.add(("C4pool", ins, ch, run, i), key(f"{ins}:{ch}", "verdict", run, i, "C4-surrogates"))
    return f

def l2b_real():
    f = Fam("Law 2b instance tests, real data")
    for u in U:
        flow = u[0] == "unit"
        for inst in (CHG_F if flow else CHG_P):
            net = l2(inst, u[4])
            f.add(("l2b-pool", inst) + u, K(u, net=net))
            if u[3] == "verdict":
                for c in ("C2", "C3"):
                    f.add(("l2b-ctlpool", inst, c) + u, K(u, net=net, purpose=c + "-surrogates"))
        if not flow:
            f.add(("l2b-F", ) + u, K(u, net=l2("F", u[4]), purpose="law2b-F"))
            if u[3] == "verdict":
                for c in ("C2", "C3"):
                    f.add(("l2b-ctlF", c) + u, K(u, net=l2("F", u[4]), purpose=c + "-law2b-F"))
    streams = sorted({(u[1], u[2], u[3], u[4]) for u in U if u[0] == "unit"})
    for (ins, ch, sp, net) in streams:
        f.add(("l2b-Fstream", ins, ch, sp, net), key(f"{ins}:{ch}", sp, l2("F", net), "stream", "law2b-F"))
        if sp == "verdict":
            for c in ("C2", "C3"):
                f.add(("l2b-ctlFstream", c, ins, ch, net), key(f"{ins}:{ch}", sp, l2("F", net), "stream", c + "-law2b-F"))
    for ins in INS:
        for run in R.runs_for(ins, R.PRES_RUNS):
            ch = inst_chan(ins, run)
            for i in range(32):
                for inst in CHG_P:
                    f.add(("l2b-C4pool", inst, ins, ch, run, i), key(f"{ins}:{ch}", "verdict", l2(inst, run), i, "C4-surrogates"))
                f.add(("l2b-C4F", ins, ch, run, i), key(f"{ins}:{ch}", "verdict", l2("F", run), i, "C4-law2b-F"))
    for a, b in PAIRS:
        for inst in ARR_I:
            for r in R.TR_RUNS:
                for pur in ("detectors-arrow", "detectors-profile"):
                    f.add(("l2b-det", inst, a, b, r, pur), key(f"{a}>{b}", "verdict", l2(inst, r), 0, pur))
        for inst in FLOW_I:
            for r in R.FLOW_RUNS:
                f.add(("l2b-det", inst, a, b, r, "flow"), key(f"{a}>{b}", "verdict", l2(inst, r), 0, "detectors-flow"))
    return f

def null():
    f = Fam("Law 2b null replicates, author's grid (segments 0-3, units L0q0 L0q1 L3q0 L6q31)")
    sel = {f"flow-L{l}-q{q}" for (l, q) in ((0, 0), (0, 1), (3, 0), (6, 31))}
    items = [u for u in U if u[3] == "verdict" and ((u[0] == "seg" and u[5] < 4) or (u[0] == "unit" and u[5] in sel))]
    for u in items:
        flow = u[0] == "unit"
        for inst in (FLOW_I if flow else PRES_I):
            net = l2(inst, u[4])
            for r in range(1, 11):
                own = ("null",) + u + (inst, r)
                f.add(own + ("series",), K(u, net=net, purpose="law2b-null", idx=r))
                f.add(own + ("pool",), K(u, net=net, purpose="surrogates", idx=r))
                for c in ("C2", "C3"):
                    f.add(own + (c,), K(u, net=net, purpose=c, idx=r))
                    f.add(own + (c, "pool"), K(u, net=net, purpose=c + "-surrogates", idx=r))
                if inst == "F" and not flow:
                    f.add(own + ("F",), K(u, net=net, purpose="law2b-F", idx=r))
                    for c in ("C2", "C3"):
                        f.add(own + (c, "F"), K(u, net=net, purpose=c + "-law2b-F", idx=r))
    for a, b in PAIRS:
        for r in range(1, 11):
            for inst in ARR_I:
                for run in R.TR_RUNS:
                    for pur in ("detectors-arrow", "detectors-profile"):
                        f.add(("null-det", inst, a, b, run, pur, r), key(f"{a}>{b}", "verdict", l2(inst, run), 0, pur, r))
            for inst in FLOW_I:
                for run in R.FLOW_RUNS:
                    f.add(("null-det", inst, a, b, run, "flow", r), key(f"{a}>{b}", "verdict", l2(inst, run), 0, "detectors-flow", r))
    return f

def pre():
    f = Fam("Law 2b pre-data checks, all kinds, splits and sets")
    def pool(owner, instr, split, seg, inst, chg, run):
        if inst in chg:
            f.add(owner + (inst,), key(instr, split, l2(inst, run), seg, "surrogates"))
    for inst in CHG_F | set(PRES_I) | set(ARR_I) | set(FLOW_I):
        pass
    for inst in R.CHG_PRES:
        for c in CLASSES:
            for s in range(200):
                f.add(("K2", c, 4096, s, "data"), key(f"K2:{c}:4096", "synthetic", "native", s, "data"), "reuse")
                pool(("K2", c, s, "pool"), f"K2:{c}:4096", "synthetic", s, inst, R.CHG_PRES, "native")
                if inst == "F":
                    f.add(("K2", c, s, "F"), key(f"K2:{c}:4096", "synthetic", l2("F", "native"), s, "law2b-F"))
        for c in ("shots", "logistic", "saw"):
            for s in range(200):
                f.add(("K3", c, "native4096", s, "data"), key(f"K3:{c}:4224", "synthetic", "native4096", s, "data"), "reuse")
                pool(("K3", c, s, "pool"), f"K3:{c}:4224", "synthetic", s, inst, R.CHG_PRES, "native4096")
                if inst == "F":
                    f.add(("K3", c, s, "F"), key(f"K3:{c}:4224", "synthetic", l2("F", "native4096"), s, "law2b-F"))
        for s in range(10):
            for k in ("A", "B", "C", "Aprime", "S", "Sr"):
                for sp in ("fit", "verdict"):
                    for run in RUNS4:
                        for seg in range(32):
                            pool(("K4", k, sp, run, s, seg, "pool"), f"K4:{k}:s{s}", sp, seg, inst, R.CHG_PRES, run)
                            if inst == "F":
                                f.add(("K4", k, sp, run, s, seg, "F"), key(f"K4:{k}:s{s}", sp, l2("F", run), seg, "law2b-F"))
    # the data draws of K4 and K5 are reused too; they appear once in their own families
    for inst in ARR_I:
        for s in range(10):
            for p in PAIRS4:
                for run in RUNS4:
                    for pur in ("detectors-arrow", "detectors-profile"):
                        f.add(("K4", "det", inst, p, run, pur, s), key(f"K4:{p}", "verdict", l2(inst, run), s, pur))
    sets = [("expo", "verdict", "native"), ("cascade", "fit", "native"), ("cascade", "verdict", "native"), ("cascade_shuffled", "verdict", "native"),
            ("y", "verdict", "native"), ("yprime", "verdict", "native"), ("cascade_iaaft", "fit", "native")] + [("cascade_rank", "verdict", r) for r in RUNS5]
    for inst in R.CHG_FLOW:
        for s in range(10):
            for (c, sp, r) in sets:
                for l, nu in enumerate((32, 32, 31, 15)):
                    for q in range(nu):
                        pool(("K5", c, sp, r, s, l, q), f"K5b:{c}", sp, f"s{s}-flow-L{l}-q{q}", inst, R.CHG_FLOW, r)
                if inst == "F":
                    f.add(("K5", c, sp, r, s, "F"), key(f"K5b:{c}", sp, l2("F", r), s, "law2b-F"))
    for inst in FLOW_I:
        for s in range(10):
            for crit, r in [("cascade>cascade_rank", x) for x in RUNS5] + [("cascade>yprime", "native"), ("cascade_iaaft>cascade", "native")]:
                f.add(("K5", "det", inst, crit, r, s), key(f"K5b:{crit}", "verdict", l2(inst, r), s, "detectors-flow"))
    return f

if __name__ == "__main__":
    fams = [fam_k1(), fam_k2(), fam_k3(), fam_k4(True), fam_k5(True), real(), controls(), pre(), l2b_real(), null()]
    want = {"K1": 1001, "K2": 36000, "K3": 9600, "K4 every kind, split, run": 8660, "K5 every case, split, run": None}
    tot = {}
    for f in fams:
        n, nk, no, coll, split = f.stats()
        print(f"{f.name}: events {n:,}, distinct keys {nk:,}, owners {no:,}, collisions {len(coll)}, owner-two-keys {len(split)}")
    cf, nk, nh = R.cross_family(fams)
    print(f"all together: {nk:,} distinct keys, {nh:,} distinct 64-bit seeds, keys with two different owners {len(cf)}")
