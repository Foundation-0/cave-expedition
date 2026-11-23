"""Clean-room seed-key rebuild for the Amendment 3 draft (reading D14 as amended).
Standard library only. Each draw is an EVENT with an OWNER (the random start it is meant to use, named
from the plan's meaning, not from the key). A key is built from the owner by the D14 rule.
A family passes when owners and keys correspond one to one: no two owners share a key (collision)
and no owner has two keys. Events beyond the first on an owner are the 'shared by design' draws.
"""
import hashlib
import sys

M = "master"

def key(instr, split, net, seg, purpose, idx=0):
    return "|".join([M, str(instr), str(split), str(net), str(seg), str(purpose), str(idx)])

class Fam:
    def __init__(self, name):
        self.name = name
        self.ev = []          # (owner, key, tag)
    def add(self, owner, k, tag=""):
        self.ev.append((owner, k, tag))
    def stats(self):
        k2o, o2k = {}, {}
        for o, k, _ in self.ev:
            k2o.setdefault(k, set()).add(o)
            o2k.setdefault(o, set()).add(k)
        coll = [k for k, s in k2o.items() if len(s) > 1]
        split = [o for o, s in o2k.items() if len(s) > 1]
        return len(self.ev), len(k2o), len(o2k), coll, split

def seeds_hash(k):
    return int(hashlib.sha256(k.encode()).hexdigest()[:16], 16)

CLASSES = ["white", "ar05", "ar09", "ar099", "pl1", "pl2", "sines", "g2", "absh"]
NULL7 = CLASSES[:7]

# ---------------------------------------------------------------- K2
def fam_k2():
    f = Fam("K2")
    for c in CLASSES:
        for L in (4096, 2048):
            for s in range(1000):
                f.add(("K2", c, L, s, "data"), key(f"K2:{c}:{L}", "synthetic", "native", s, "data"))
                f.add(("K2", c, L, s, "pool"), key(f"K2:{c}:{L}", "synthetic", "native", s, "surrogates"))
    for s in range(200):  # must-fail control on exp of AR(1) 0.9 at 4096: map of the plain draw, plain pool key
        f.add(("K2", "ar09", 4096, s, "data"), key("K2:ar09:4096", "synthetic", "native", s, "data"), "mustfail")
        f.add(("K2", "ar09", 4096, s, "pool"), key("K2:ar09:4096", "synthetic", "native", s, "surrogates"), "mustfail")
    return f

# ---------------------------------------------------------------- K1
def fam_k1():
    f = Fam("K1")
    for c in CLASSES:
        for s in range(20):
            for _series in range(13):   # plain, 3 maps, negation, exp, cube, 3 maps each of exp and cube
                f.add(("K1", c, 1024, s, "data"), key(f"K1:{c}:1024", "synthetic", "native", s, "data"), "13")
                f.add(("K1", c, 1024, s, "pool"), key(f"K1:{c}:1024", "synthetic", "native", s, "surrogates"), "13")
            for L in (4096, 2048):      # normal scores of plain, exp, cube compared (seeds assumed 20)
                for _v in range(3):
                    f.add(("K1", c, L, s, "data"), key(f"K1:{c}:{L}", "synthetic", "native", s, "data"), "cmp")
    for c in NULL7:
        for s in range(20):
            for _series in range(4):    # integer-valued plain and its three maps
                f.add(("K1int", c, s, "data"), key(f"K1int:{c}:1024", "synthetic", "native", s, "data"), "int")
                f.add(("K1int", c, s, "pool"), key(f"K1int:{c}:1024", "synthetic", "native", s, "surrogates"), "int")
    for _m in range(4):                 # waveform and its three maps
        f.add(("K1wave", "pool"), key("K1wave:4096", "synthetic", "native", 0, "surrogates"), "wave")
    return f

# ---------------------------------------------------------------- K3
CASES3 = ["shots", "logistic", "saw", "saw_noisy"]
OWN = {"native4096": 4224, "native2048": 2176, "placement": 4224, "wlen2048": 2176}
USES3 = ["native4096", "native2048", "bm2", "sub2", "q12", "q8", "placement", "wlen2048"]
BASEUSE = {u: (u if u in OWN else "native4096") for u in USES3}

def fam_k3():
    f = Fam("K3")
    for c in CASES3:
        for s in range(200):
            for u in USES3:
                b = BASEUSE[u]
                f.add(("K3", c, b, s, "data"), key(f"K3:{c}:{OWN[b]}", "synthetic", b, s, "data"))
                f.add(("K3", c, u, s, "pool"), key(f"K3:{c}:{OWN[b]}", "synthetic", u, s, "surrogates"))
    for s in range(200):                # circular-shift control: shifts drawn from the native4096 pool key of the shots
        f.add(("K3", "shots", "native4096", s, "pool"), key(f"K3:shots:{OWN['native4096']}", "synthetic", "native4096", s, "surrogates"), "shift")
    return f

# ---------------------------------------------------------------- K4
KINDS4 = ["A", "B", "C", "S", "Sr"]
PAIRS4 = ["A>B", "A>C", "A>Aprime", "S>Sr", "Sr>S"]
RUNS4 = ["native", "placement"]

def k4_stream(f, kind, split, s, pools=True):
    if kind == "Aprime":
        f.add(("K4", "Aprime", split, s, "shuffle"), key(f"K4:Aprime:{split}", split, "native", s, "shuffle"))
        for j in range(33):
            f.add(("K4", "Aprime", split, s, "block", j), key(f"K4:Aprime:{split}", split, "native", s, "block-surrogate", j))
    else:
        f.add(("K4", kind, split, s, "data"), key(f"K4:{kind}", split, "native", s, "data"))
        if kind == "A" and False:
            pass
    if pools:
        for run in RUNS4:
            for seg in range(32):
                f.add(("K4", kind, split, s, run, seg, "pool"), key(f"K4:{kind}:s{s}", split, run, seg, "surrogates"))

def fam_k4(superset):
    f = Fam("K4 every kind, split, run" if superset else "K4 streams the criteria score")
    for s in range(10):
        if superset:
            streams = [(k, sp) for k in KINDS4 + ["Aprime"] for sp in ("fit", "verdict")]
        else:   # A fit; B, C verdict; A' fit and verdict (the control has its own fit stream); S and Sr both splits are reported only
            streams = [("A", "fit"), ("B", "verdict"), ("C", "verdict"), ("Aprime", "fit"), ("Aprime", "verdict")]
        for kind, sp in streams:
            k4_stream(f, kind, sp, s)
        if superset or True:
            # A' is made from the A stream of the same split and seed: an event on the A data owner
            for sp in (("fit", "verdict") if superset else ("fit", "verdict")):
                f.add(("K4", "A", sp, s, "data"), key("K4:A", sp, "native", s, "data"), "A'fromA")
        pairs = PAIRS4 if superset else PAIRS4[:3]
        for p in pairs:
            for run in RUNS4:
                for pur in ("detectors-arrow", "detectors-profile"):
                    f.add(("K4", "det", p, s, run, pur), key(f"K4:{p}", "verdict", run, s, pur))
    return f

# ---------------------------------------------------------------- K5
RUNS5 = ["native", "amp_scores", "amp_lognormal"]
def k5_pools(f, case, split, s, run):
    for lev, nu in enumerate((32, 32, 31, 15)):
        for q in range(nu):
            f.add(("K5", case, split, s, run, lev, q, "pool"),
                  key(f"K5b:{case}", split, run, f"s{s}-flow-L{lev}-q{q}", "surrogates"))

def fam_k5(superset):
    f = Fam("K5 every case, split, run" if superset else "K5 the 10 series sets of B9")
    for s in range(10):
        data = [("expo", "verdict"), ("cascade", "fit"), ("cascade", "verdict"), ("cascade_shuffled", "verdict"),
                ("y", "verdict"), ("yprime", "fit"), ("yprime", "verdict")]
        if superset:
            data = [(c, sp) for c in ("expo", "cascade", "cascade_shuffled", "y", "yprime") for sp in ("fit", "verdict")]
        for c, sp in data:
            f.add(("K5", c, sp, s, "data"), key(f"K5b:{c}", sp, "native", s, "data"))
        f.add(("K5", "iaaft", "fit", s, "whole"), key("K5b:cascade_iaaft", "fit", "native", s, "whole-surrogate"))
        f.add(("K5", "cascade", "fit", s, "data"), key("K5b:cascade", "fit", "native", s, "data"), "iaaft-from-cascade")
        f.add(("K5", "cascade", "verdict", s, "data"), key("K5b:cascade", "verdict", "native", s, "data"), "rank-map-of-cascade")
        sets = [("expo", "verdict", "native"), ("cascade", "fit", "native"), ("cascade", "verdict", "native"),
                ("cascade_shuffled", "verdict", "native"), ("y", "verdict", "native"), ("yprime", "verdict", "native"),
                ("cascade_iaaft", "fit", "native")] + [("cascade_rank", "verdict", r) for r in RUNS5]
        if superset:
            sets = [(c, sp, r) for c in ("expo", "cascade", "cascade_shuffled", "y", "yprime", "cascade_iaaft", "cascade_rank")
                    for sp in ("fit", "verdict") for r in RUNS5]
        for c, sp, r in sets:
            k5_pools(f, c, sp, s, r)
        # detectors: pools of cascade_rank use the cascade (verdict) series' instrument tag per D14? see note below
        crit = [("cascade>cascade_rank", r) for r in RUNS5] + [("cascade>yprime", "native"), ("cascade_iaaft>cascade", "native")]
        if superset:
            crit = [(c, r) for c in ("cascade>cascade_rank", "cascade>yprime", "cascade_iaaft>cascade") for r in RUNS5]
        for c, r in crit:
            f.add(("K5", "det", c, s, r), key(f"K5b:{c}", "verdict", r, s, "detectors-flow"))
    return f

if __name__ == "__main__":
    for f in (fam_k1(), fam_k2(), fam_k3(), fam_k4(False), fam_k4(True), fam_k5(False), fam_k5(True)):
        n, nk, no, coll, split = f.stats()
        print(f"{f.name}: events {n:,}, distinct keys {nk:,}, owners {no:,}, key collisions {len(coll)}, owner with two keys {len(split)}")
