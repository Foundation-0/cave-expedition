"""Amendment 3: every seed key of section 11a, reading D14, built from the plan's counts.

A key is the string master|instrument|split|net|segment|purpose|index of section 11. Every draw below names the random
start it is meant to use (its owner), built from what the draw is (test, case, split, run, seed, segment, unit), never
from its key. Draws that share an owner do so by design, and each such sharing is printed with its reason.
A family passes when owners and keys correspond one to one: no two owners share a key (no unintended shared random
start) and no owner gets two keys (no broken pairing). The 64-bit seeds (first 16 hex digits of SHA-256) are counted too.

Two wordings are built: D14 as published at commit 1aa53fb, for the parts that Amendment 3 changes, and D14 as
Amendment 3 words it, for every family. The amended families use the run name amp_lognormal and the case cascade_rank of item
SK8, the published ones amp_exp and cascade_exp. The published wording must show the collisions that Amendment 3 corrects.
These are must-fail controls of this script, together with two planted faults.

Counts. Known-answer counts are the plan's (section 10). Where the plan does not say which streams a run scores (K4 runs,
K5 amplitude runs on the fit side), a superset is also built: keys distinct on a superset are distinct on any subset.
Real-data counts depend on the data, so the plan's upper bounds are used: 32 segments per run, and 7 levels of at most
32 flow units. The G1 null replicates are built on a reduced grid of segments (stated where printed), because every field
that the replicate rule adds is exercised there and the full grid only repeats it.

Standard library only. No bare assert. Usage: python3 -I -B seed_keys.py (same output under -I -O -B and -I -B -W error).
Exit status 0 when every amended family passes and every must-fail control is flagged, 1 otherwise.
"""
import hashlib
import sys

MASTER = 20261121


def seed_string(key):
    if not isinstance(key, tuple) or len(key) != 6:
        raise ValueError("a key has six fields after the master seed: %r" % (key,))
    inst, split, net, seg, purpose, index = key
    for f in (inst, split, net, purpose):
        if not isinstance(f, str) or f == "" or "|" in f:
            raise ValueError("bad text field in key %r" % (key,))
    if not isinstance(seg, (str, int)) or isinstance(seg, bool) or "|" in str(seg):
        raise ValueError("bad segment field in key %r" % (key,))
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        raise ValueError("bad index in key %r" % (key,))
    return "%d|%s|%s|%s|%s|%s|%d" % (MASTER, inst, split, net, seg, purpose, index)


def seed64(s):
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16)


class Family:
    def __init__(self, name):
        self.name = name
        self.n = 0
        self.owner_key = {}
        self.key_owner = {}
        self.collisions = 0
        self.splits = 0
        self.unstated = 0
        self.example = None
        self.shared = {}
        self.reasons = []

    def reason(self, label, text):
        self.reasons.append((label, text))
        self.shared[label] = 0

    def draw(self, owner, key, share=None):
        self.n += 1
        s = seed_string(key)
        if owner in self.owner_key:
            if share is None:
                self.unstated += 1
                if self.example is None:
                    self.example = "owner %r drawn twice with no stated sharing" % (owner,)
            else:
                if share not in self.shared:
                    raise ValueError("sharing label without a reason: " + share)
                self.shared[share] += 1
            if self.owner_key[owner] != s:
                self.splits += 1
                if self.example is None:
                    self.example = "owner %r gets two keys: %s and %s" % (owner, self.owner_key[owner], s)
            return
        if share is not None:
            raise ValueError("a shared draw must follow the draw it shares: %r" % (owner,))
        self.owner_key[owner] = s
        other = self.key_owner.get(s)
        if other is None:
            self.key_owner[s] = owner
        else:
            self.collisions += 1
            if self.example is None:
                self.example = "key %s used by %r and %r" % (s, other, owner)

    def ok(self):
        return self.collisions == 0 and self.splits == 0 and self.unstated == 0

    def nseeds(self):
        return len({seed64(s) for s in self.key_owner})

    def report(self, w):
        status = "OK, one key per independent random start" if self.ok() else (
            "FAULT: %d owners share another owner's key, %d owners get two keys, %d unstated reuses" % (
                self.collisions, self.splits, self.unstated))
        w("%s: draws %d, independent random starts %d, distinct keys %d, distinct 64-bit seeds %d | %s" % (
            self.name, self.n, len(self.owner_key), len(self.key_owner), self.nseeds(), status))
        if self.example is not None:
            w("    first fault: " + self.example)
        for label, text in self.reasons:
            w("    shared by design (%s): %d draws reuse a key. %s" % (label, self.shared[label], text))


# ---------------------------------------------------------------- plan counts (section 10)
K2_CLASSES = ("white", "ar1_0.5", "ar1_0.9", "ar1_0.99", "powerlaw1", "powerlaw2", "sines", "g2", "absh")
NULL_CLASSES = K2_CLASSES[:7]
K2_LENGTHS = (4096, 2048)
K2_SEEDS = 1000
K2_CONTROL_SEEDS = 200
K1_SEEDS = 20
K1_SERIES = ("plain", "plain:cube_map", "plain:exp_map", "plain:rank_map", "negation", "exp_version", "cube_version",
             "exp_version:cube_map", "exp_version:exp_map", "exp_version:rank_map",
             "cube_version:cube_map", "cube_version:exp_map", "cube_version:rank_map")
K1_INT_SERIES = ("integer", "integer:cube_map", "integer:exp_map", "integer:rank_map")
K3_CASES = ("shots", "logistic", "sawtooth", "sawtooth_noisy")
K3_GATING = ("shots", "logistic", "sawtooth")
K3_SEEDS = 200
K3_OWN = (("native4096", 4224), ("placement", 4224), ("native2048", 2176), ("wlen2048", 2176))
K3_ON_NATIVE4096 = ("bm2", "sub2", "q12", "q8")
K3_BLOCK = {"native4096": 4224, "placement": 4224, "native2048": 2176, "wlen2048": 2176,
            "bm2": 4224, "sub2": 4224, "q12": 4224, "q8": 4224}
K3_USES = ("native4096", "native2048", "bm2", "sub2", "q12", "q8", "placement", "wlen2048")
K4_KINDS = ("A", "B", "C", "S", "Sr")
K4_POOL_KINDS = ("A", "B", "C", "Aprime", "S", "Sr")
K4_SEEDS = 10
K4_RUNS = ("native", "placement")
K4_SEGMENTS = 32
K4_BLOCKS = 33
K4_PAIRS = ("A>B", "A>C", "A>Aprime", "S>Sr", "Sr>S")
SPLITS = ("fit", "verdict")
K5_SEEDS = 10
K5_UNITS = ((0, 32), (1, 32), (2, 31), (3, 15))
K5_RUNS = ("native", "amp_scores", "amp_lognormal")
K5_DATA = (("expo", "verdict"), ("cascade", "fit"), ("cascade", "verdict"), ("cascade_shuffled", "verdict"),
           ("y", "verdict"), ("yprime", "fit"), ("yprime", "verdict"))
K5_SETS = (("expo", "verdict", "native"), ("cascade", "fit", "native"), ("cascade", "verdict", "native"),
           ("cascade_shuffled", "verdict", "native"), ("y", "verdict", "native"), ("yprime", "verdict", "native"),
           ("cascade_iaaft", "fit", "native"), ("cascade_rank", "verdict", "native"),
           ("cascade_rank", "verdict", "amp_scores"), ("cascade_rank", "verdict", "amp_lognormal"))
K5_SETS_PUBLISHED = (("expo", "verdict", "native"), ("cascade", "fit", "native"), ("cascade", "verdict", "native"),
           ("cascade_shuffled", "verdict", "native"), ("y", "verdict", "native"), ("yprime", "verdict", "native"),
           ("cascade_iaaft", "fit", "native"), ("cascade_exp", "verdict", "native"),
           ("cascade_exp", "verdict", "amp_scores"), ("cascade_exp", "verdict", "amp_exp"))
K5_CASES_ALL = ("expo", "cascade", "cascade_shuffled", "y", "yprime", "cascade_iaaft", "cascade_rank")
K5_CRITERIA = (("cascade>cascade_rank", "cascade", K5_RUNS), ("cascade>yprime", "cascade", ("native",)),
               ("cascade_iaaft>cascade", "cascade_iaaft", ("native",)))
K5_CRITERIA_PUBLISHED = (("cascade>cascade_exp", "cascade", ("native", "amp_scores", "amp_exp")),
                         ("cascade>yprime", "cascade", ("native",)), ("cascade_iaaft>cascade", "cascade_iaaft", ("native",)))
L2B_PRESENCE = ("W", "Q", "H", "F", "M", "D", "O4", "E")
L2B_ARROW = ("W", "Q", "H", "F", "M", "D", "E")
L2B_FLOW = ("W", "H", "F", "B", "D", "R")
L2B_CHANGE_SEGMENT = ("W", "F", "D")
L2B_CHANGE_FLOW = ("W", "F", "D", "B", "R")
REPLICATES = range(1, 11)

PRIMARY = ("GW:H1", "SEIS:VBB", "WAVES:Z", "TESS:1")
SECOND = {"GW:H1": "GW:L1", "SEIS:VBB": "SEIS:SP", "WAVES:Z": "WAVES:S"}
INSTRUMENTS = {"GW:H1": "GW", "SEIS:VBB": "SEIS", "WAVES:Z": "WAVES", "TESS:1": "TESS"}
PRESENCE_RUNS = ("native", "bm2", "sub2", "q12", "q8", "placement", "wlen")
TRANSFER_RUNS = ("native", "instrument", "placement")
FLOW_RUNS = ("native", "instrument", "placement", "amp_scores", "amp_lognormal")
REAL_SEGMENTS = 32
REAL_UNITS = tuple((l, q) for l in range(7) for q in range(32))
C4_SERIES = 32


def units():
    for (l, n) in K5_UNITS:
        for q in range(n):
            yield l, q


def unit_seg(seed, l, q):
    return "s%d-flow-L%d-q%d" % (seed, l, q)


def l2b(inst, run):
    return "law2b-%s:%s" % (inst, run)


# ---------------------------------------------------------------- amended families
def fam_k1():
    f = Family("K1 (amended)")
    f.reason("K1 identity", "The 13 series of a class and seed (versions, maps, negation) are maps of the plain draw and "
             "use its data and pool keys, as do the 4 series of each integer-valued class and seed and the waveform with its "
             "3 maps. The identities of K1 need the same random start.")
    f.reason("K1 versions at 4096 and 2048", "The exp and cube versions are compared by their normal scores with the plain "
             "draw they are maps of.")
    for c in K2_CLASSES:
        for s in range(K1_SEEDS):
            dk = ("K1:%s:1024" % c, "synthetic", "native", s, "data", 0)
            pk = ("K1:%s:1024" % c, "synthetic", "native", s, "surrogates", 0)
            f.draw(("K1 data", c, 1024, s), dk)
            for i, name in enumerate(K1_SERIES):
                f.draw(("K1 pool", c, s), pk, None if i == 0 else "K1 identity")
                if i > 0:
                    f.draw(("K1 data", c, 1024, s), dk, "K1 identity")
        for n in (4096, 2048):
            for s in range(K1_SEEDS):
                dk = ("K1:%s:%d" % (c, n), "synthetic", "native", s, "data", 0)
                f.draw(("K1 data", c, n, s), dk)
                f.draw(("K1 data", c, n, s), dk, "K1 versions at 4096 and 2048")
                f.draw(("K1 data", c, n, s), dk, "K1 versions at 4096 and 2048")
    for c in NULL_CLASSES:
        for s in range(K1_SEEDS):
            dk = ("K1int:%s:1024" % c, "synthetic", "native", s, "data", 0)
            pk = ("K1int:%s:1024" % c, "synthetic", "native", s, "surrogates", 0)
            f.draw(("K1int data", c, s), dk)
            for i, name in enumerate(K1_INT_SERIES):
                f.draw(("K1int pool", c, s), pk, None if i == 0 else "K1 identity")
                if i > 0:
                    f.draw(("K1int data", c, s), dk, "K1 identity")
    for i in range(4):
        f.draw(("K1wave pool",), ("K1wave:4096", "synthetic", "native", 0, "surrogates", 0), None if i == 0 else "K1 identity")
    return f


def fam_k2():
    f = Family("K2 (amended, wording unchanged)")
    f.reason("K2 control", "The must-fail control (raw-value surrogates) runs on the exp version of the AR(1) 0.9 draw at "
             "4,096 samples, seeds 0 to 199, and draws from that draw's pool key, so that only the surrogate method differs.")
    for c in K2_CLASSES:
        for n in K2_LENGTHS:
            for s in range(K2_SEEDS):
                f.draw(("K2 data", c, n, s), ("K2:%s:%d" % (c, n), "synthetic", "native", s, "data", 0))
                f.draw(("K2 pool", c, n, s), ("K2:%s:%d" % (c, n), "synthetic", "native", s, "surrogates", 0))
    for s in range(K2_CONTROL_SEEDS):
        f.draw(("K2 data", "ar1_0.9", 4096, s), ("K2:ar1_0.9:4096", "synthetic", "native", s, "data", 0), "K2 control")
        f.draw(("K2 pool", "ar1_0.9", 4096, s), ("K2:ar1_0.9:4096", "synthetic", "native", s, "surrogates", 0), "K2 control")
    return f


def k3_pool_key(case, use, s, amended=True):
    inst = ("K3:%s:%d" % (case, K3_BLOCK[use])) if amended else ("K3:%s" % case)
    return (inst, "synthetic", use, s, "surrogates", 0)


def fam_k3(amended=True):
    f = Family("K3 (amended)" if amended else "K3 (published pool instrument K3:<case>)")
    f.reason("K3 nets", "The nets bm2, sub2, q12 and q8 are changes of observation of the native4096 draw and use it.")
    f.reason("K3 control", "The circular-shift control on the shots draws its shifts from the shots native4096 pool key, so "
             "that only the surrogate method differs.")
    for case in K3_CASES:
        for s in range(K3_SEEDS):
            for use, blk in K3_OWN:
                f.draw(("K3 data", case, use, s), ("K3:%s:%d" % (case, blk), "synthetic", use, s, "data", 0))
            for use in K3_ON_NATIVE4096:
                f.draw(("K3 data", case, "native4096", s), ("K3:%s:4224" % case, "synthetic", "native4096", s, "data", 0), "K3 nets")
            for use in K3_USES:
                f.draw(("K3 pool", case, use, s), k3_pool_key(case, use, s, amended))
    for s in range(K3_SEEDS):
        f.draw(("K3 pool", "shots", "native4096", s), k3_pool_key("shots", "native4096", s, amended), "K3 control")
    return f


def k4_det_key(pair, run, s, purpose, amended=True):
    if amended:
        return ("K4:" + pair, "verdict", run, s, purpose, 0)
    # published: purposes and net the run are stated, the instrument is that of the K4 line (the template's kind)
    return ("K4:" + pair.split(">")[0], "verdict", run, s, purpose, 0)


def fam_k4(superset):
    f = Family("K4 (amended, %s)" % ("superset: every kind, split and run" if superset else "the streams of D20 and its second reading"))
    f.reason("K4 Aprime", "A' is made from the A stream of the same split and seed, because the control removes structure "
             "from that stream.")
    if not superset:
        f.reason("K4 two readings", "Under D20's second reading the placement-run detectors of A>B, A>C and A>Aprime use D20's "
                 "keys, so that only the template differs between the readings.")
    for s in range(K4_SEEDS):
        for kind in K4_KINDS:
            for sp in SPLITS:
                f.draw(("K4 data", kind, sp, s), ("K4:" + kind, sp, "native", s, "data", 0))
        for sp in SPLITS:
            f.draw(("K4 data", "A", sp, s), ("K4:A", sp, "native", s, "data", 0), "K4 Aprime")
            f.draw(("K4 Aprime shuffle", sp, s), ("K4:Aprime:" + sp, sp, "native", s, "shuffle", 0))
            for q in range(K4_BLOCKS):
                f.draw(("K4 Aprime block", sp, s, q), ("K4:Aprime:" + sp, sp, "native", s, "block-surrogate", q))
        if superset:
            plan = [(k, sp, r) for k in K4_POOL_KINDS for sp in SPLITS for r in K4_RUNS]
            pairs = [(p, r) for p in K4_PAIRS for r in K4_RUNS]
        else:
            plan = [("A", "fit", "native")] + [(k, "verdict", r) for k in ("B", "C", "Aprime") for r in K4_RUNS]
            plan += [("S", "fit", "native"), ("Sr", "verdict", "native"), ("Sr", "fit", "native"), ("S", "verdict", "native")]
            pairs = [(p, r) for p in ("A>B", "A>C", "A>Aprime") for r in K4_RUNS] + [("S>Sr", "native"), ("Sr>S", "native")]
        for (k, sp, r) in plan:
            for q in range(K4_SEGMENTS):
                f.draw(("K4 pool", k, sp, r, s, q), ("K4:%s:s%d" % (k, s), sp, r, q, "surrogates", 0))
        for (p, r) in pairs:
            for purpose in ("detectors-arrow", "detectors-profile"):
                f.draw(("K4 detectors", p, r, purpose, s), k4_det_key(p, r, s, purpose))
        if not superset:
            # D20's second reading: templates and shifts from the fit streams cut in each run's own grid, blind spot in both runs
            for (k, sp) in (("A", "fit"), ("S", "fit"), ("Sr", "fit"), ("S", "verdict"), ("Sr", "verdict")):
                for q in range(K4_SEGMENTS):
                    f.draw(("K4 pool", k, sp, "placement", s, q), ("K4:%s:s%d" % (k, s), sp, "placement", q, "surrogates", 0))
            for p in ("S>Sr", "Sr>S"):
                for purpose in ("detectors-arrow", "detectors-profile"):
                    f.draw(("K4 detectors", p, "placement", purpose, s), k4_det_key(p, "placement", s, purpose))
            for p in ("A>B", "A>C", "A>Aprime"):
                for purpose in ("detectors-arrow", "detectors-profile"):
                    f.draw(("K4 detectors", p, "placement", purpose, s), k4_det_key(p, "placement", s, purpose), "K4 two readings")
    return f


def k5_pool_key(case, sp, run, s, l, q, wording):
    if wording == "amended":
        return ("K5b:" + case, sp, run, unit_seg(s, l, q), "surrogates", 0)
    if wording == "published":
        return ("K5b:" + case, sp, "native", "flow-L%d-q%d" % (l, q), "surrogates", 0)
    if wording == "seed only":
        return ("K5b:" + case, sp, "native", unit_seg(s, l, q), "surrogates", 0)
    if wording == "run only":
        return ("K5b:" + case, sp, run, "flow-L%d-q%d" % (l, q), "surrogates", 0)
    raise ValueError(wording)


def k5_det_key(crit, a_case, run, s, amended=True):
    if amended:
        return ("K5b:" + crit, "verdict", run, s, "detectors-flow", 0)
    # published: purpose detectors-flow in the K5 line (instrument K5b:<case>, net native), no pair and no run
    return ("K5b:" + a_case, "verdict", "native", s, "detectors-flow", 0)


def fam_k5(superset):
    f = Family("K5 (amended, %s)" % ("superset: every case, split and run" if superset else "the 10 series sets of B9"))
    f.reason("K5 maps", "The rank-mapped cascade is a map of the cascade (verdict) draw, and the IAAFT cascade is made from "
             "the cascade (fit) draw, as their criteria require.")
    for s in range(K5_SEEDS):
        data = [(c, sp) for c in ("expo", "cascade", "cascade_shuffled", "y", "yprime") for sp in SPLITS] if superset else K5_DATA
        for case, sp in data:
            f.draw(("K5 data", case, sp, s), ("K5b:" + case, sp, "native", s, "data", 0))
        f.draw(("K5 data", "cascade", "fit", s), ("K5b:cascade", "fit", "native", s, "data", 0), "K5 maps")
        f.draw(("K5 whole surrogate", s), ("K5b:cascade_iaaft", "fit", "native", s, "whole-surrogate", 0))
        f.draw(("K5 data", "cascade", "verdict", s), ("K5b:cascade", "verdict", "native", s, "data", 0), "K5 maps")
        sets = [(c, sp, r) for c in K5_CASES_ALL for sp in SPLITS for r in K5_RUNS] if superset else K5_SETS
        for (c, sp, r) in sets:
            for (l, q) in units():
                f.draw(("K5 pool", c, sp, r, s, l, q), k5_pool_key(c, sp, r, s, l, q, "amended"))
        for crit, a_case, runs in K5_CRITERIA:
            for r in (K5_RUNS if superset else runs):
                f.draw(("K5 detectors", crit, r, s), k5_det_key(crit, a_case, r, s))
    return f


def real_segments():
    """(channel, split, run, segment) of every real segment and flow unit at the plan's upper bounds."""
    out = []
    for ch in PRIMARY:
        for r in PRESENCE_RUNS:
            out += [(ch, "verdict", r, q) for q in range(REAL_SEGMENTS)]
        for r in ("native", "placement", "amp_scores", "amp_lognormal"):
            out += [(ch, "verdict", r, "flow-L%d-q%d" % u) for u in REAL_UNITS]
    for ch in SECOND.values():
        out += [(ch, "verdict", "instrument", q) for q in range(REAL_SEGMENTS)]
        out += [(ch, "verdict", "instrument", "flow-L%d-q%d" % u) for u in REAL_UNITS]
    for ch in list(PRIMARY) + list(SECOND.values()):
        out += [(ch, "fit", "native", q) for q in range(REAL_SEGMENTS)]
        out += [(ch, "fit", "native", "flow-L%d-q%d" % u) for u in REAL_UNITS]
    return out


def real_pairs():
    names = sorted(set(INSTRUMENTS.values()))
    return [(a, b) for a in names for b in names if a != b]


def fam_real():
    f = Family("Real data, segment and flow-unit pools and random detectors (amended)")
    f.reason("C5 substitution", "The same transfer with B's C2 or C3 series in place of B (section 5, control C5) uses the "
             "random detectors of the transfer it checks, so that only B changes.")
    for (ch, sp, r, seg) in real_segments():
        f.draw(("real pool", ch, sp, r, seg), (ch, sp, r, seg, "surrogates", 0))
    for (a, b) in real_pairs():
        for r in TRANSFER_RUNS:
            for purpose in ("detectors-arrow", "detectors-profile"):
                k = ("%s>%s" % (a, b), "verdict", r, 0, purpose, 0)
                f.draw(("real detectors", a, b, r, purpose), k)
                f.draw(("real detectors", a, b, r, purpose), k, "C5 substitution")
                f.draw(("real detectors", a, b, r, purpose), k, "C5 substitution")
        for r in FLOW_RUNS:
            k = ("%s>%s" % (a, b), "verdict", r, 0, "detectors-flow", 0)
            f.draw(("real detectors", a, b, r, "flow"), k)
            f.draw(("real detectors", a, b, r, "flow"), k, "C5 substitution")
            f.draw(("real detectors", a, b, r, "flow"), k, "C5 substitution")
    return f


def control_draws(f, amended=True, with_segment_pools=True):
    """C2 and C3 per verdict segment and flow unit, C4 per channel and presence run, and the pools of all three."""
    for (ch, sp, r, seg) in real_segments():
        if sp != "verdict":
            continue
        if with_segment_pools:
            f.draw(("real pool", ch, sp, r, seg), (ch, sp, r, seg, "surrogates", 0))
        for c in ("C2", "C3"):
            f.draw((c, ch, r, seg), (ch, "verdict", r, seg, c, 0))
            f.draw((c + " pool", ch, r, seg), (ch, "verdict", r, seg, (c + "-surrogates") if amended else "surrogates", 0))
    chan_runs = [(ch, r) for ch in PRIMARY for r in PRESENCE_RUNS] + [(ch, "instrument") for ch in SECOND.values()]
    for (ch, r) in chan_runs:
        for i in range(C4_SERIES):
            f.draw(("C4", ch, r, i), (ch, "verdict", r, i, "C4", 0))
            f.draw(("C4 pool", ch, r, i), (ch, "verdict", r, i, "C4-surrogates" if amended else "surrogates", 0))


def fam_controls(amended=True):
    f = Family("Controls C2, C3, C4 with the segment pools they sit beside (%s)" % (
        "amended" if amended else "published: a pool takes its segment's key with purpose surrogates"))
    control_draws(f, amended)
    return f


def fam_law2b_known_answer():
    f = Family("Law 2b pre-data checks on the known-answer draws (amended)")
    f.reason("Law 2b on known-answer data", "Each check applies the instance to the known-answer data draw (K2 seeds 0 to "
             "199 at 4,096 and K3 native4096 listed here, and the K4 and K5 streams likewise), so that only the instance differs.")
    for inst in L2B_CHANGE_SEGMENT:
        for c in K2_CLASSES:
            for s in range(200):
                if inst == L2B_CHANGE_SEGMENT[0]:
                    f.draw(("K2 data", c, 4096, s), ("K2:%s:4096" % c, "synthetic", "native", s, "data", 0))
                else:
                    f.draw(("K2 data", c, 4096, s), ("K2:%s:4096" % c, "synthetic", "native", s, "data", 0), "Law 2b on known-answer data")
                f.draw(("L2b K2 pool", inst, c, s), ("K2:%s:4096" % c, "synthetic", l2b(inst, "native"), s, "surrogates", 0))
                if inst == "F":
                    f.draw(("L2b K2 F noise", c, s), ("K2:%s:4096" % c, "synthetic", l2b("F", "native"), s, "law2b-F", 0))
        for case in K3_GATING:
            for s in range(200):
                if inst == L2B_CHANGE_SEGMENT[0]:
                    f.draw(("K3 data", case, "native4096", s), ("K3:%s:4224" % case, "synthetic", "native4096", s, "data", 0))
                else:
                    f.draw(("K3 data", case, "native4096", s), ("K3:%s:4224" % case, "synthetic", "native4096", s, "data", 0), "Law 2b on known-answer data")
                f.draw(("L2b K3 pool", inst, case, s), ("K3:%s:4224" % case, "synthetic", l2b(inst, "native4096"), s, "surrogates", 0))
                if inst == "F":
                    f.draw(("L2b K3 F noise", case, s), ("K3:%s:4224" % case, "synthetic", l2b("F", "native4096"), s, "law2b-F", 0))
    for s in range(K4_SEEDS):
        for inst in L2B_CHANGE_SEGMENT:
            for k in K4_POOL_KINDS:
                for sp in SPLITS:
                    for r in K4_RUNS:
                        for q in range(K4_SEGMENTS):
                            f.draw(("L2b K4 pool", inst, k, sp, r, s, q), ("K4:%s:s%d" % (k, s), sp, l2b(inst, r), q, "surrogates", 0))
                            if inst == "F":
                                f.draw(("L2b K4 F noise", k, sp, r, s, q), ("K4:%s:s%d" % (k, s), sp, l2b("F", r), q, "law2b-F", 0))
        for inst in L2B_ARROW:
            for p in K4_PAIRS:
                for r in K4_RUNS:
                    for purpose in ("detectors-arrow", "detectors-profile"):
                        f.draw(("L2b K4 detectors", inst, p, r, purpose, s), ("K4:" + p, "verdict", l2b(inst, r), s, purpose, 0))
        for inst in L2B_CHANGE_FLOW:
            for (c, sp, r) in K5_SETS:
                for (l, q) in units():
                    f.draw(("L2b K5 pool", inst, c, sp, r, s, l, q), ("K5b:" + c, sp, l2b(inst, r), unit_seg(s, l, q), "surrogates", 0))
                if inst == "F":
                    f.draw(("L2b K5 F noise", c, sp, r, s), ("K5b:" + c, sp, l2b("F", r), s, "law2b-F", 0))
        for inst in L2B_FLOW:
            for crit, a_case, runs in K5_CRITERIA:
                for r in runs:
                    f.draw(("L2b K5 detectors", inst, crit, r, s), ("K5b:" + crit, "verdict", l2b(inst, r), s, "detectors-flow", 0))
    return f


def fam_law2b_real_instances():
    f = Family("Law 2b instance tests on real data (amended)")
    segs = real_segments()
    for (ch, sp, r, seg) in segs:
        flow = isinstance(seg, str)
        for inst in (L2B_CHANGE_FLOW if flow else L2B_CHANGE_SEGMENT):
            f.draw(("L2b real pool", inst, ch, sp, r, seg), (ch, sp, l2b(inst, r), seg, "surrogates", 0))
            if sp == "verdict":
                for c in ("C2", "C3"):
                    f.draw(("L2b real control pool", inst, c, ch, r, seg), (ch, sp, l2b(inst, r), seg, c + "-surrogates", 0))
        if not flow:
            f.draw(("L2b real F noise", ch, sp, r, seg), (ch, sp, l2b("F", r), seg, "law2b-F", 0))
            if sp == "verdict":
                for c in ("C2", "C3"):
                    f.draw(("L2b real control F noise", c, ch, r, seg), (ch, sp, l2b("F", r), seg, c + "-law2b-F", 0))
    streams = sorted({(ch, sp, r) for (ch, sp, r, seg) in segs if isinstance(seg, str)})
    for (ch, sp, r) in streams:
        f.draw(("L2b real F noise stream", ch, sp, r), (ch, sp, l2b("F", r), "stream", "law2b-F", 0))
        if sp == "verdict":
            for c in ("C2", "C3"):
                f.draw(("L2b real control F noise stream", c, ch, r), (ch, sp, l2b("F", r), "stream", c + "-law2b-F", 0))
    chan_runs = [(ch, r) for ch in PRIMARY for r in PRESENCE_RUNS] + [(ch, "instrument") for ch in SECOND.values()]
    for (ch, r) in chan_runs:
        for i in range(C4_SERIES):
            for inst in L2B_CHANGE_SEGMENT:
                f.draw(("L2b real C4 pool", inst, ch, r, i), (ch, "verdict", l2b(inst, r), i, "C4-surrogates", 0))
            f.draw(("L2b real C4 F noise", ch, r, i), (ch, "verdict", l2b("F", r), i, "C4-law2b-F", 0))
    for (a, b) in real_pairs():
        for inst in L2B_ARROW:
            for r in TRANSFER_RUNS:
                for purpose in ("detectors-arrow", "detectors-profile"):
                    f.draw(("L2b real detectors", inst, a, b, r, purpose), ("%s>%s" % (a, b), "verdict", l2b(inst, r), 0, purpose, 0))
        for inst in L2B_FLOW:
            for r in FLOW_RUNS:
                f.draw(("L2b real detectors", inst, a, b, r, "flow"), ("%s>%s" % (a, b), "verdict", l2b(inst, r), 0, "detectors-flow", 0))
    return f


REP_SEGMENTS = 4
REP_UNITS = ((0, 0), (0, 1), (3, 0), (6, 31))


def replicate_segments():
    out = []
    for (ch, sp, r, seg) in real_segments():
        if sp != "verdict":
            continue
        if isinstance(seg, int) and seg < REP_SEGMENTS:
            out.append((ch, r, seg))
        if isinstance(seg, str) and seg in {"flow-L%d-q%d" % u for u in REP_UNITS}:
            out.append((ch, r, seg))
    return out


def fam_law2b_replicates(amended=True):
    f = Family("Law 2b G1 null replicates on real data (%s, segments 0 to %d and flow units %s of every channel and run)" % (
        "amended" if amended else "published: purpose law2b-null with the key of the segment",
        REP_SEGMENTS - 1, ", ".join("L%d-q%d" % u for u in REP_UNITS)))
    for (ch, r, seg) in replicate_segments():
        flow = isinstance(seg, str)
        for inst in (L2B_FLOW if flow else L2B_PRESENCE):
            for rep in REPLICATES:
                if not amended:
                    f.draw(("L2b null series", inst, ch, r, seg, rep), (ch, "verdict", r, seg, "law2b-null", 0))
                    continue
                net = l2b(inst, r)
                f.draw(("L2b null series", inst, ch, r, seg, rep), (ch, "verdict", net, seg, "law2b-null", rep))
                f.draw(("L2b null pool", inst, ch, r, seg, rep), (ch, "verdict", net, seg, "surrogates", rep))
                for c in ("C2", "C3"):
                    f.draw(("L2b null control", inst, c, ch, r, seg, rep), (ch, "verdict", net, seg, c, rep))
                    f.draw(("L2b null control pool", inst, c, ch, r, seg, rep), (ch, "verdict", net, seg, c + "-surrogates", rep))
                if inst == "F" and not flow:
                    f.draw(("L2b null F noise", ch, r, seg, rep), (ch, "verdict", net, seg, "law2b-F", rep))
                    for c in ("C2", "C3"):
                        f.draw(("L2b null control F noise", c, ch, r, seg, rep), (ch, "verdict", net, seg, c + "-law2b-F", rep))
    if amended:
        for (a, b) in real_pairs():
            for rep in REPLICATES:
                for inst in L2B_ARROW:
                    for r in TRANSFER_RUNS:
                        for purpose in ("detectors-arrow", "detectors-profile"):
                            f.draw(("L2b null detectors", inst, a, b, r, purpose, rep), ("%s>%s" % (a, b), "verdict", l2b(inst, r), 0, purpose, rep))
                for inst in L2B_FLOW:
                    for r in FLOW_RUNS:
                        f.draw(("L2b null detectors", inst, a, b, r, "flow", rep), ("%s>%s" % (a, b), "verdict", l2b(inst, r), 0, "detectors-flow", rep))
    return f


# ---------------------------------------------------------------- published wording (the parts Amendment 3 changes)
def pub_k5_pools(wording):
    f = Family("K5 flow-unit pools, %s" % {
        "published": "published (segment flow-L<level>-q<unit>, net native)",
        "seed only": "seed added, net still native",
        "run only": "run named in the net, seed still missing"}[wording])
    for s in range(K5_SEEDS):
        for (c, sp, r) in K5_SETS_PUBLISHED:
            for (l, q) in units():
                f.draw(("K5 pool", c, sp, r, s, l, q), k5_pool_key(c, sp, r, s, l, q, wording))
    return f


def misread_k5_source_instrument():
    f = Family("K5 flow-unit pools with a mapped series named by the draw it is made from (the reading that D14 now rules out)")
    src = {"cascade_rank": "cascade", "cascade_iaaft": "cascade"}
    for s in range(K5_SEEDS):
        for (c, sp, r) in K5_SETS:
            for (l, q) in units():
                f.draw(("K5 pool", c, sp, r, s, l, q), ("K5b:" + src.get(c, c), sp, r, unit_seg(s, l, q), "surrogates", 0))
    return f


def pub_k4_detectors():
    f = Family("K4 random detectors, published (purpose and run only, instrument of the template's kind)")
    for s in range(K4_SEEDS):
        for p in K4_PAIRS:
            for r in K4_RUNS:
                for purpose in ("detectors-arrow", "detectors-profile"):
                    f.draw(("K4 detectors", p, r, purpose, s), k4_det_key(p, r, s, purpose, amended=False))
    return f


def pub_k5_detectors():
    f = Family("K5 random detectors, published (purpose only, instrument of the template's case, net native)")
    for s in range(K5_SEEDS):
        for crit, a_case, runs in K5_CRITERIA_PUBLISHED:
            for r in runs:
                f.draw(("K5 detectors", crit, r, s), k5_det_key(crit, a_case, r, s, amended=False))
    return f


def pub_law2b_pools():
    f = Family("Law 2b W, F, D pools beside the confirmatory pools, published (a pool takes its segment's key)")
    for (ch, sp, r, seg) in real_segments():
        if isinstance(seg, str):
            continue
        f.draw(("real pool", ch, sp, r, seg), (ch, sp, r, seg, "surrogates", 0))
        for inst in L2B_CHANGE_SEGMENT:
            f.draw(("L2b real pool", inst, ch, sp, r, seg), (ch, sp, r, seg, "surrogates", 0))
    return f


# ---------------------------------------------------------------- planted faults
def planted_split():
    f = Family("Planted fault: K1 maps given their own pool keys")
    f.reason("K1 identity", "as in K1")
    for c in K2_CLASSES[:2]:
        for s in range(3):
            for i, name in enumerate(K1_SERIES):
                f.draw(("K1 pool", c, s), ("K1:%s:1024" % c, "synthetic", name, s, "surrogates", 0), None if i == 0 else "K1 identity")
    return f


def planted_unstated():
    f = Family("Planted fault: K2 control sharing the pool key with no stated reason")
    for s in range(5):
        k = ("K2:ar1_0.9:4096", "synthetic", "native", s, "surrogates", 0)
        f.draw(("K2 pool", "ar1_0.9", 4096, s), k)
        f.draw(("K2 pool", "ar1_0.9", 4096, s), k)
    return f


def main():
    out = []
    w = out.append
    w("Amendment 3: seed keys of section 11a (D14). Master seed %d. Seeds are numbered from 0." % MASTER)
    w("")
    w("== D14 as Amendment 3 words it ==")
    amended = [fam_k1(), fam_k2(), fam_k3(True), fam_k4(False), fam_k4(True), fam_k5(False), fam_k5(True), fam_real(),
               fam_controls(True), fam_law2b_known_answer(), fam_law2b_real_instances(), fam_law2b_replicates(True)]
    for f in amended:
        f.report(w)
    w("")
    w("== across families ==")
    # supersets contain their plan-count families, so the union is taken over the families that do not overlap
    union_names = ("K1 (amended)", "K2 (amended, wording unchanged)", "K3 (amended)",
                   "K4 (amended, superset: every kind, split and run)", "K5 (amended, superset: every case, split and run)",
                   "Controls C2, C3, C4 with the segment pools they sit beside (amended)",
                   "Law 2b pre-data checks on the known-answer draws (amended)", "Law 2b instance tests on real data (amended)")
    union_fams = [f for f in amended if f.name in union_names or f.name.startswith("Law 2b G1")]
    real_fam = [f for f in amended if f.name.startswith("Real data")][0]
    seen = {}
    cross = 0
    for f in union_fams + [real_fam]:
        for s, owner in f.key_owner.items():
            prev = seen.get(s)
            if prev is None:
                seen[s] = owner
            elif prev != owner:
                cross += 1   # a draw listed in two families carries the same owner in both, so this is a real collision
    seeds_all = {seed64(s) for s in seen}
    w("keys over all amended families: %d distinct keys, %d distinct 64-bit seeds, %d keys used by two different owners "
      "in different families" % (len(seen), len(seeds_all), cross))
    w("")
    w("== D14 as published at 1aa53fb, the parts Amendment 3 changes (must-fail controls: each must show a fault, except K3) ==")
    published = [misread_k5_source_instrument(), pub_k5_pools("published"), pub_k5_pools("seed only"), pub_k5_pools("run only"), pub_k4_detectors(),
                 pub_k5_detectors(), fam_controls(False), pub_law2b_pools(), fam_law2b_replicates(False)]
    for f in published:
        f.report(w)
    k3pub = fam_k3(False)
    k3pub.report(w)
    w("")
    w("== planted faults (must-fail controls) ==")
    planted = [planted_split(), planted_unstated()]
    for f in planted:
        f.report(w)
    w("")
    bad_amended = [f.name for f in amended if not f.ok()]
    unflagged = [f.name for f in published + planted if f.ok()]
    k3_ok = k3pub.ok()
    w("RESULT amended families with a fault: %s" % (bad_amended if bad_amended else "none"))
    w("RESULT must-fail controls not flagged: %s" % (unflagged if unflagged else "none"))
    w("RESULT published K3 pool keys distinct (wording only): %s" % ("yes" if k3_ok else "no"))
    w("RESULT keys shared across families without a stated reason: %d" % cross)
    good = (not bad_amended) and (not unflagged) and k3_ok and cross == 0 and len(seeds_all) == len(seen)
    w("DONE seed_keys: %s" % ("all checks hold" if good else "A CHECK FAILED"))
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
