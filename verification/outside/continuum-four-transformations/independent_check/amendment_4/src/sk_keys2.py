"""Real data, controls, Law 2b and null replicates. Reads the families of sk_keys.py. Standard library only."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk_keys import *

CH = {"GW": ("H1", "L1"), "SEIS": ("VBB", "SP"), "WW": ("Z", "S"), "TESS": ("SAP", None)}
INS = list(CH)
PRES_RUNS = ["native", "bm2", "sub2", "q12", "q8", "placement", "wlen", "instrument"]
TR_RUNS = ["native", "instrument", "placement"]
FLOW_RUNS = TR_RUNS + ["amp_scores", "amp_lognormal"]
COUNT3 = ["GW", "SEIS", "WW"]

def runs_for(ins, runs):
    return [r for r in runs if not (r == "instrument" and CH[ins][1] is None)]
def chan(ins, run):
    return CH[ins][1] if run == "instrument" else CH[ins][0]
def flow_unit_label(l, q):
    return f"flow-L{l}-q{q}"
UNITS = [(l, q) for l in range(7) for q in range(32)]

def real_units(ins):
    out = []
    for run in runs_for(ins, PRES_RUNS):
        for seg in range(32):
            out.append(("seg", ins, "verdict", run, seg))
    for run in runs_for(ins, TR_RUNS):
        for seg in range(32):
            out.append(("seg", ins, "fit", run, seg))
    for run in runs_for(ins, FLOW_RUNS):
        for sp in ("fit", "verdict"):
            for (l, q) in UNITS:
                out.append(("unit", ins, sp, run, (l, q)))
    return out

def ukey(u, net=None, purpose="surrogates", idx=0):
    kind, ins, sp, run, s = u
    seg = s if kind == "seg" else flow_unit_label(*s)
    return key(f"{ins}:{chan(ins, run)}", sp, net or run, seg, purpose, idx)

def fam_real():
    f = Fam("Real data pools and detectors")
    for ins in INS:
        for u in real_units(ins):
            f.add(("real",) + u, ukey(u))
    pairs = [(a, b) for a in INS for b in INS if a != b]
    for a, b in pairs:
        for r in TR_RUNS:
            for pur in ("detectors-arrow", "detectors-profile"):
                f.add(("real-det", a, b, r, pur), key(f"{a}>{b}", "verdict", r, 0, pur))
        for r in FLOW_RUNS:
            f.add(("real-det", a, b, r, "detectors-flow"), key(f"{a}>{b}", "verdict", r, 0, "detectors-flow"))
    for a, b in pairs:   # C5: B's C2 or C3 series reuse the detectors of the transfer they check
        for r in TR_RUNS:
            for pur in ("detectors-arrow", "detectors-profile"):
                for c in ("C2", "C3"):
                    f.add(("real-det", a, b, r, pur), key(f"{a}>{b}", "verdict", r, 0, pur), "C5")
        for r in FLOW_RUNS:
            for c in ("C2", "C3"):
                f.add(("real-det", a, b, r, "detectors-flow"), key(f"{a}>{b}", "verdict", r, 0, "detectors-flow"), "C5")
    return f

def fam_controls():
    f = Fam("Controls C2 to C4 with their pools")
    for ins in INS:
        for u in real_units(ins):
            if u[2] != "verdict":
                continue
            for c in ("C2", "C3"):
                f.add(("ctl", c, "series") + u, ukey(u, purpose=c))
                f.add(("ctl", c, "pool") + u, ukey(u, purpose=f"{c}-surrogates"))
        for run in runs_for(ins, PRES_RUNS):
            for i in range(32):
                f.add(("ctl", "C4", "series", ins, run, i), key(f"{ins}:{chan(ins, run)}", "verdict", run, i, "C4"))
                f.add(("ctl", "C4", "pool", ins, run, i), key(f"{ins}:{chan(ins, run)}", "verdict", run, i, "C4-surrogates"))
    return f

PRES_INST = ["W", "Q", "H", "F", "M", "D", "O4", "E"]
ARR_INST = ["W", "Q", "H", "F", "M", "D", "E"]
FLOW_INST = ["W", "H", "F", "B", "D", "R"]
CHG_PRES = {"W", "F", "D"}
CHG_FLOW = {"W", "F", "D", "B", "R"}

def l2net(i, run):
    return f"law2b-{i}:{run}"

def fam_l2b_real():
    f = Fam("Law 2b instance tests, real data")
    pairs3 = [(a, b) for a in COUNT3 for b in COUNT3 if a != b]
    def pools(units, inst, chg):
        for u in units:
            if inst in chg:
                f.add(("l2b",) + u + (inst,), ukey(u, net=l2net(inst, u[3])))
            else:
                f.add(("real",) + u, ukey(u), "shares-base-pool")
    for ins in COUNT3:
        for inst in PRES_INST:
            pools([u for u in real_units(ins) if u[0] == "seg" and u[2] == "verdict"], inst, CHG_PRES)
            if inst == "F":
                for run in runs_for(ins, PRES_RUNS):
                    for seg in range(32):
                        u = ("seg", ins, "verdict", run, seg)
                        f.add(("l2b-Fnoise", ins, "verdict", run, seg), ukey(u, net=l2net("F", run), purpose="law2b-F"))
    for inst in ARR_INST:
        for ins in COUNT3:
            pools([u for u in real_units(ins) if u[0] == "seg" and u[3] in TR_RUNS], inst, CHG_PRES)
            if inst == "F":
                for run in TR_RUNS:
                    for seg in range(32):
                        for sp in ("fit", "verdict"):
                            u = ("seg", ins, sp, run, seg)
                            f.add(("l2b-Fnoise", ins, sp, run, seg), ukey(u, net=l2net("F", run), purpose="law2b-F"))
        for a, b in pairs3:
            for r in TR_RUNS:
                f.add(("l2b-det", "arrow", inst, a, b, r), key(f"{a}>{b}", "verdict", l2net(inst, r), 0, "detectors-arrow"))
    for inst in FLOW_INST:
        for ins in COUNT3:
            pools([u for u in real_units(ins) if u[0] == "unit"], inst, CHG_FLOW)
            if inst == "F":
                for run in runs_for(ins, FLOW_RUNS):
                    for sp in ("fit", "verdict"):
                        f.add(("l2b-Fnoise-stream", ins, sp, run), key(f"{ins}:{chan(ins, run)}", sp, l2net("F", run), "stream", "law2b-F"))
        for a, b in pairs3:
            for r in FLOW_RUNS:
                f.add(("l2b-det", "flow", inst, a, b, r), key(f"{a}>{b}", "verdict", l2net(inst, r), 0, "detectors-flow"))
    return f

def fam_l2b_pre():
    f = Fam("Law 2b pre-data checks")
    def kn_pool(owner, instr, split, seg, inst, chg, run="native"):
        if inst in chg:
            f.add(owner + (inst,), key(instr, split, l2net(inst, run), seg, "surrogates"))
        else:
            f.add(owner, key(instr, split, run, seg, "surrogates"), "shares-base-pool")
    for inst in PRES_INST:
        for c in CLASSES:
            for s in range(200):
                f.add(("K2", c, 4096, s, "data"), key(f"K2:{c}:4096", "synthetic", "native", s, "data"), "reuse")
                kn_pool(("K2", c, 4096, s, "pool"), f"K2:{c}:4096", "synthetic", s, inst, CHG_PRES)
                if inst == "F":
                    f.add(("K2", c, 4096, s, "Fnoise"), key(f"K2:{c}:4096", "synthetic", l2net("F", "native"), s, "law2b-F"))
        for c in CASES3:
            for s in range(200):
                f.add(("K3", c, "native4096", s, "data"), key(f"K3:{c}:4224", "synthetic", "native4096", s, "data"), "reuse")
                kn_pool(("K3", c, "native4096", s, "pool"), f"K3:{c}:4224", "synthetic", s, inst, CHG_PRES, run="native4096")
                if inst == "F":
                    f.add(("K3", c, s, "Fnoise"), key(f"K3:{c}:4224", "synthetic", l2net("F", "native4096"), s, "law2b-F"))
    for inst in ARR_INST:
        for s in range(10):
            for kind, sp in (("A", "fit"), ("B", "verdict"), ("C", "verdict")):
                f.add(("K4", kind, sp, s, "data"), key(f"K4:{kind}", sp, "native", s, "data"), "reuse")
                for run in RUNS4:
                    for seg in range(32):
                        kn_pool(("K4", kind, sp, s, run, seg, "pool"), f"K4:{kind}:s{s}", sp, seg, inst, CHG_PRES, run=run)
            for p in PAIRS4[:2]:
                for run in RUNS4:
                    for pur in ("detectors-arrow", "detectors-profile"):
                        f.add(("K4", "det", inst, p, s, run, pur), key(f"K4:{p}", "verdict", l2net(inst, run), s, pur))
    for inst in FLOW_INST:
        for s in range(10):
            for case, sp in (("cascade", "fit"), ("cascade", "verdict"), ("yprime", "verdict"), ("cascade_iaaft", "fit"), ("cascade_rank", "verdict")):
                runs = RUNS5 if case == "cascade_rank" else ["native"]
                f.add(("K5", case, sp, s, "data"), key(f"K5b:{case}", sp, "native", s, "data"), "reuse")
                for r in runs:
                    for l, nu in enumerate((32, 32, 31, 15)):
                        for q in range(nu):
                            kn_pool(("K5", case, sp, s, r, l, q, "pool"), f"K5b:{case}", sp, f"s{s}-flow-L{l}-q{q}", inst, CHG_FLOW, run=r)
            for c, r in [("cascade>cascade_rank", x) for x in RUNS5] + [("cascade>yprime", "native"), ("cascade_iaaft>cascade", "native")]:
                f.add(("K5", "det", inst, c, s, r), key(f"K5b:{c}", "verdict", l2net(inst, r), s, "detectors-flow"))
    return f

def fam_null(reduced_segs=2, reduced_units=2, net_has_instance=True):
    f = Fam("Law 2b null replicates, reduced grid")
    pairs3 = [(a, b) for a in COUNT3 for b in COUNT3 if a != b]
    def rep(ins, sp, run, segname, inst, r):
        net = l2net(inst, run) if net_has_instance else run
        base = (ins, sp, run, segname)
        for nm, pur in (("c2", "law2b-null"), ("c2pool", "C2-surrogates"), ("c3", "C3"), ("c3pool", "C3-surrogates")) + ((("fnoise", "C2-law2b-F"),) if inst == "F" else ()):
            yield (nm, base, inst, r), key(f"{ins}:{chan(ins, run)}", sp, net, segname, pur, r)
    for r in range(1, 11):
        for inst in PRES_INST:
            for ins in COUNT3:
                for run in runs_for(ins, PRES_RUNS):
                    for seg in range(reduced_segs):
                        for o, k in rep(ins, "verdict", run, seg, inst, r):
                            f.add(("null",) + o, k)
        for inst in FLOW_INST:
            for ins in COUNT3:
                for run in runs_for(ins, FLOW_RUNS):
                    for (l, q) in UNITS[:reduced_units]:
                        for o, k in rep(ins, "verdict", run, flow_unit_label(l, q), inst, r):
                            f.add(("null",) + o, k)
        for inst in ARR_INST:
            for a, b in pairs3:
                for run in TR_RUNS:
                    f.add(("null-det", inst, a, b, run, r, "arrow"), key(f"{a}>{b}", "verdict", l2net(inst, run), 0, "detectors-arrow", r))
        for inst in FLOW_INST:
            for a, b in pairs3:
                for run in FLOW_RUNS:
                    f.add(("null-det", inst, a, b, run, r, "flow"), key(f"{a}>{b}", "verdict", l2net(inst, run), 0, "detectors-flow", r))
    return f

def cross_family(fams):
    k2own = {}
    for f in fams:
        for o, k, _ in f.ev:
            k2own.setdefault(k, set()).add(o)
    return [k for k, s in k2own.items() if len(s) > 1], len(k2own), len({seeds_hash(k) for k in k2own})

if __name__ == "__main__":
    fams = [fam_k1(), fam_k2(), fam_k3(), fam_k4(True), fam_k5(False), fam_real(), fam_controls(), fam_l2b_pre(), fam_l2b_real(), fam_null()]
    for f in fams:
        n, nk, no, coll, split = f.stats()
        print(f"{f.name}: events {n:,}, distinct keys {nk:,}, owners {no:,}, collisions {len(coll)}, owner-two-keys {len(split)}")
    cf, nk, nh = cross_family(fams)
    print(f"across these families: {nk:,} distinct keys, {nh:,} distinct 64-bit seeds, keys with two different owners {len(cf)}")
