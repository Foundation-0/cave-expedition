"""Key uniqueness check (PREREG section 11a, reading D14 as amended by Amendment 3). Builds every seed key of every family at the plan's counts with the
functions of src/keys.py (the functions the code draws from), names for each draw the random start it is meant to use (its owner, built from what the draw
is, never from its key), and checks that no two owners share a key except the draws on the plan's "Shared by design" list. Prints draws and distinct keys per
family, and the totals of the plan: K4 6,180 draws on 6,100 keys, 417,545 distinct keys over all families. Exit status 1 on any fault or mismatch.
Real-data counts are the plan's upper bounds (32 segments per run, 7 levels of at most 32 flow units) and the null replicates use the plan's reduced grid.
Key epoch (reading D14 as amended by Amendment 4): the families are built in epoch 0. The check also shows that the epoch-0 strings are byte for byte
the strings of the seed rule before the epoch existed (a digest of every distinct string, pinned from the code before the change, and each string
against the old formula), and that the strings of epochs 1 to 3 never coincide with those of epoch 0 or of another epoch. Building a seed string
makes no draw.
usage: key_check.py"""
import hashlib
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import keys
import seeds
from kcommon import Checker

K2_CLASSES = ("white", "ar1_0.5", "ar1_0.9", "ar1_0.99", "powerlaw1", "powerlaw2", "sines", "g2", "absh")
NULL_CLASSES = K2_CLASSES[:7]
K1_SEEDS, K2_SEEDS, K2_CTRL, K3_SEEDS, K4_SEEDS, K5_SEEDS = 20, 1000, 200, 200, 10, 10
K1_SERIES = 13
K1_INT_SERIES = 4
K3_CASES = ("shots", "logistic", "sawtooth", "sawtooth_noisy")
K3_GATING = ("shots", "logistic", "sawtooth")
K3_USES = ("native4096", "native2048", "bm2", "sub2", "q12", "q8", "placement", "wlen2048")
K4_KINDS = ("A", "B", "C", "S", "Sr")
K4_POOL_KINDS = ("A", "B", "C", "Aprime", "S", "Sr")
K4_RUNS = ("native", "placement")
K4_PAIRS = ("A>B", "A>C", "A>Aprime", "S>Sr", "Sr>S")
SPLITS = ("fit", "verdict")
K5_UNITS = ((0, 32), (1, 32), (2, 31), (3, 15))
K5_RUNS = ("native", "amp_scores", "amp_lognormal")
K5_DATA = (("expo", "verdict"), ("cascade", "fit"), ("cascade", "verdict"), ("cascade_shuffled", "verdict"), ("y", "verdict"), ("yprime", "fit"), ("yprime", "verdict"))
K5_SETS = (("expo", "verdict", "native"), ("cascade", "fit", "native"), ("cascade", "verdict", "native"), ("cascade_shuffled", "verdict", "native"),
           ("y", "verdict", "native"), ("yprime", "verdict", "native"), ("cascade_iaaft", "fit", "native"), ("cascade_rank", "verdict", "native"),
           ("cascade_rank", "verdict", "amp_scores"), ("cascade_rank", "verdict", "amp_lognormal"))
K5_CASES_ALL = ("expo", "cascade", "cascade_shuffled", "y", "yprime", "cascade_iaaft", "cascade_rank")
K5_CRITERIA = (("cascade>cascade_rank", K5_RUNS), ("cascade>yprime", ("native",)), ("cascade_iaaft>cascade", ("native",)))
L2B_PRESENCE = ("W", "Q", "H", "F", "M", "D", "O4", "E")
L2B_ARROW = ("W", "Q", "H", "F", "M", "D", "E")
L2B_FLOW = ("W", "H", "F", "B", "D", "R")
L2B_CHANGE_SEGMENT = ("W", "F", "D")
L2B_CHANGE_FLOW = ("W", "F", "D", "B", "R")
# SHA-256 of the sorted distinct seed strings of the 12 families below, joined by newlines, computed with the code before Amendment 4 was carried out
# (src/seeds.py without the epoch, commit b2ef206), over 417,545 strings. Epoch 0 must reproduce it exactly.
EPOCH0_DIGEST = "3da7954bbaf21b3ce83629bb4c08e860677d9988c08f7aa49012563fb4a31585"
EPOCH0_STRINGS = 417545
OTHER_EPOCHS = (1, 2, 3)
PRIMARY = ("GW:H1", "SEIS:VBB", "WAVES:Z", "TESS:1")
SECOND = {"GW:H1": "GW:L1", "SEIS:VBB": "SEIS:SP", "WAVES:Z": "WAVES:S"}
INSTRUMENTS = {"GW:H1": "GW", "SEIS:VBB": "SEIS", "WAVES:Z": "WAVES", "TESS:1": "TESS"}
PRESENCE_RUNS = ("native", "bm2", "sub2", "q12", "q8", "placement", "wlen")
TRANSFER_RUNS = ("native", "instrument", "placement")
FLOW_RUNS = ("native", "instrument", "placement", "amp_scores", "amp_lognormal")
REAL_SEGMENTS = 32
REAL_UNITS = tuple((l, q) for l in range(7) for q in range(32))
C4_SERIES = 32


class Family:
    """Draws with owners. An owner is the random start a draw is meant to use. Sharing a key is allowed only for a draw that names a stated reason."""

    def __init__(self, name, expect_draws, expect_keys, epoch=0):
        self.name, self.expect = name, (expect_draws, expect_keys)
        self.epoch = epoch
        self.n = 0
        self.owner_key, self.key_owner = {}, {}
        self.keys = set()
        self.collisions = self.splits = self.unstated = 0
        self.shared = {}

    def reason(self, label):
        self.shared[label] = 0

    def draw(self, owner, key, share=None):
        self.n += 1
        self.keys.add(tuple(key))
        s = seeds.seed_string(*key, epoch=self.epoch)
        if owner in self.owner_key:
            if share is None:
                self.unstated += 1
            else:
                self.shared[share] += 1
            if self.owner_key[owner] != s:
                self.splits += 1
            return
        self.owner_key[owner] = s
        if s in self.key_owner:
            self.collisions += 1
        else:
            self.key_owner[s] = owner

    def ok(self):
        return self.collisions == 0 and self.splits == 0 and self.unstated == 0

    def line(self):
        return "%-46s draws %7d, distinct keys %7d, shared by design %s" % (self.name, self.n, len(self.key_owner), sum(self.shared.values()))


def with_net(key, net):
    inst, split, _, seg, purpose, idx = key
    return (inst, split, net, seg, purpose, idx)


def with_index(key, i):
    inst, split, net, seg, purpose, _ = key
    return (inst, split, net, seg, purpose, i)


def units():
    for (l, n) in K5_UNITS:
        for q in range(n):
            yield l, q


def fam_k1():
    f = Family("K1", 6884, 1001)
    for label in ("K1 identity", "K1 versions at 4096 and 2048"):
        f.reason(label)
    for c in K2_CLASSES:
        for s in range(K1_SEEDS):
            f.draw(("K1 data", c, 1024, s), keys.k1_data(c, 1024, s))
            for i in range(K1_SERIES):
                f.draw(("K1 pool", c, s), keys.k1_pool(c, 1024, s), None if i == 0 else "K1 identity")
                if i > 0:
                    f.draw(("K1 data", c, 1024, s), keys.k1_data(c, 1024, s), "K1 identity")
        for n in (4096, 2048):
            for s in range(K1_SEEDS):
                f.draw(("K1 data", c, n, s), keys.k1_data(c, n, s))
                for _ in range(2):
                    f.draw(("K1 data", c, n, s), keys.k1_data(c, n, s), "K1 versions at 4096 and 2048")
    for c in NULL_CLASSES:
        for s in range(K1_SEEDS):
            f.draw(("K1int data", c, s), keys.k1int_data(c, s))
            for i in range(K1_INT_SERIES):
                f.draw(("K1int pool", c, s), keys.k1int_pool(c, s), None if i == 0 else "K1 identity")
                if i > 0:
                    f.draw(("K1int data", c, s), keys.k1int_data(c, s), "K1 identity")
    for i in range(4):
        f.draw(("K1wave pool",), keys.k1wave_pool(), None if i == 0 else "K1 identity")
    return f


def fam_k2():
    f = Family("K2", 36400, 36000)
    f.reason("K2 control")
    for c in K2_CLASSES:
        for n in (4096, 2048):
            for s in range(K2_SEEDS):
                f.draw(("K2 data", c, n, s), keys.k2_data(c, n, s))
                f.draw(("K2 pool", c, n, s), keys.k2_pool(c, n, s))
    for s in range(K2_CTRL):
        f.draw(("K2 data", "ar1_0.9", 4096, s), keys.k2_data("ar1_0.9", 4096, s), "K2 control")
        f.draw(("K2 pool", "ar1_0.9", 4096, s), keys.k2_pool("ar1_0.9", 4096, s), "K2 control")
    return f


def fam_k3():
    f = Family("K3", 13000, 9600)
    f.reason("K3 nets")
    f.reason("K3 control")
    for case in K3_CASES:
        for s in range(K3_SEEDS):
            for use in ("native4096", "placement", "native2048", "wlen2048"):
                f.draw(("K3 data", case, use, s), keys.k3_data(case, use, s))
            for use in ("bm2", "sub2", "q12", "q8"):
                f.draw(("K3 data", case, "native4096", s), keys.k3_data(case, use, s), "K3 nets")
            for use in K3_USES:
                f.draw(("K3 pool", case, use, s), keys.k3_pool(case, use, s))
    for s in range(K3_SEEDS):
        f.draw(("K3 pool", "shots", "native4096", s), keys.k3_pool("shots", "native4096", s), "K3 control")
    return f


def fam_k4(superset):
    f = Family("K4 superset (every kind, split and run)" if superset else "K4 (D20 and its second reading)", 8680 if superset else 6180, 8660 if superset else 6100)
    f.reason("K4 Aprime")
    if not superset:
        f.reason("K4 two readings")
    for s in range(K4_SEEDS):
        for kind in K4_KINDS:
            for sp in SPLITS:
                f.draw(("K4 data", kind, sp, s), keys.k4_data(kind, sp, s))
        for sp in SPLITS:
            f.draw(("K4 data", "A", sp, s), keys.k4_data("A", sp, s), "K4 Aprime")
            f.draw(("K4 Aprime shuffle", sp, s), keys.k4_aprime_shuffle(sp, s))
            for pos in range(33):
                f.draw(("K4 Aprime block", sp, s, pos), keys.k4_aprime_block(sp, s, pos))
        if superset:
            plan = [(k, sp, r) for k in K4_POOL_KINDS for sp in SPLITS for r in K4_RUNS]
            pairs = [(p, r) for p in K4_PAIRS for r in K4_RUNS]
        else:
            plan = [("A", "fit", "native")] + [(k, "verdict", r) for k in ("B", "C", "Aprime") for r in K4_RUNS]
            plan += [("S", "fit", "native"), ("Sr", "verdict", "native"), ("Sr", "fit", "native"), ("S", "verdict", "native")]
            pairs = [(p, r) for p in ("A>B", "A>C", "A>Aprime") for r in K4_RUNS] + [("S>Sr", "native"), ("Sr>S", "native")]
        for (k, sp, r) in plan:
            for q in range(32):
                f.draw(("K4 pool", k, sp, r, s, q), keys.k4_pool(k, sp, r, s, q))
        for (p, r) in pairs:
            for purpose in ("detectors-arrow", "detectors-profile"):
                f.draw(("K4 detectors", p, r, purpose, s), keys.k4_detectors(p, r, s, purpose))
        if not superset:
            for (k, sp) in (("A", "fit"), ("S", "fit"), ("Sr", "fit"), ("S", "verdict"), ("Sr", "verdict")):
                for q in range(32):
                    f.draw(("K4 pool", k, sp, "placement", s, q), keys.k4_pool(k, sp, "placement", s, q))
            for p in ("S>Sr", "Sr>S"):
                for purpose in ("detectors-arrow", "detectors-profile"):
                    f.draw(("K4 detectors", p, "placement", purpose, s), keys.k4_detectors(p, "placement", s, purpose))
            for p in ("A>B", "A>C", "A>Aprime"):
                for purpose in ("detectors-arrow", "detectors-profile"):
                    f.draw(("K4 detectors", p, "placement", purpose, s), keys.k4_detectors(p, "placement", s, purpose), "K4 two readings")
    return f


def fam_k5(superset):
    f = Family("K5 superset (every case, split and run)" if superset else "K5 (the 10 series sets of B9)", 46420 if superset else 11150, 46400 if superset else 11130)
    f.reason("K5 maps")
    for s in range(K5_SEEDS):
        data = [(c, sp) for c in ("expo", "cascade", "cascade_shuffled", "y", "yprime") for sp in SPLITS] if superset else K5_DATA
        for case, sp in data:
            f.draw(("K5 data", case, sp, s), keys.k5_data(case, sp, s))
        f.draw(("K5 data", "cascade", "fit", s), keys.k5_data("cascade", "fit", s), "K5 maps")
        f.draw(("K5 whole surrogate", s), keys.k5_whole(s))
        f.draw(("K5 data", "cascade", "verdict", s), keys.k5_data("cascade", "verdict", s), "K5 maps")
        sets = [(c, sp, r) for c in K5_CASES_ALL for sp in SPLITS for r in K5_RUNS] if superset else K5_SETS
        for (c, sp, r) in sets:
            for (l, q) in units():
                f.draw(("K5 pool", c, sp, r, s, l, q), keys.k5_pool(c, sp, r, s, l, q))
        for crit, runs in K5_CRITERIA:
            for r in (K5_RUNS if superset else runs):
                f.draw(("K5 detectors", crit, r, s), keys.k5_detectors(crit, r, s))
    return f


def real_segments():
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
    f = Family("Real data pools and random detectors", 7436, 7172)
    f.reason("C5 substitution")
    for (ch, sp, r, seg) in real_segments():
        f.draw(("real pool", ch, sp, r, seg), keys.real_pool(ch, sp, r, seg))
    for (a, b) in real_pairs():
        for r in TRANSFER_RUNS:
            for purpose in ("detectors-arrow", "detectors-profile"):
                k = keys.real_detectors(a, b, r, purpose)
                f.draw(("real detectors", a, b, r, purpose), k)
                for _ in range(2):
                    f.draw(("real detectors", a, b, r, purpose), k, "C5 substitution")
        for r in FLOW_RUNS:
            k = keys.real_detectors(a, b, r, "detectors-flow")
            f.draw(("real detectors", a, b, r, "flow"), k)
            for _ in range(2):
                f.draw(("real detectors", a, b, r, "flow"), k, "C5 substitution")
    return f


def fam_controls():
    f = Family("Controls C2, C3, C4 with the segment pools", 28224, 28224)
    for (ch, sp, r, seg) in real_segments():
        if sp != "verdict":
            continue
        f.draw(("real pool", ch, sp, r, seg), keys.real_pool(ch, sp, r, seg))
        for c in ("C2", "C3"):
            f.draw((c, ch, r, seg), keys.control_series(c, ch, r, seg))
            f.draw((c + " pool", ch, r, seg), keys.control_pool(c, ch, r, seg))
    chan_runs = [(ch, r) for ch in PRIMARY for r in PRESENCE_RUNS] + [(ch, "instrument") for ch in SECOND.values()]
    for (ch, r) in chan_runs:
        for i in range(C4_SERIES):
            f.draw(("C4", ch, r, i), keys.c4_series(ch, r, i))
            f.draw(("C4 pool", ch, r, i), keys.c4_pool(ch, r, i))
    return f


def fam_law2b_known_answer():
    f = Family("Law 2b pre-data checks", 104320, 99520)
    f.reason("Law 2b on known-answer data")
    first = L2B_CHANGE_SEGMENT[0]
    for inst in L2B_CHANGE_SEGMENT:
        for c in K2_CLASSES:
            for s in range(200):
                f.draw(("K2 data", c, 4096, s), keys.k2_data(c, 4096, s), None if inst == first else "Law 2b on known-answer data")
                f.draw(("L2b K2 pool", inst, c, s), with_net(keys.k2_pool(c, 4096, s), keys.l2b_net(inst, "native")))
                if inst == "F":
                    f.draw(("L2b K2 F noise", c, s), keys.f_noise(keys.k2_pool(c, 4096, s), "native"))
        for case in K3_GATING:
            for s in range(200):
                f.draw(("K3 data", case, "native4096", s), keys.k3_data(case, "native4096", s), None if inst == first else "Law 2b on known-answer data")
                f.draw(("L2b K3 pool", inst, case, s), with_net(keys.k3_pool(case, "native4096", s), keys.l2b_net(inst, "native4096")))
                if inst == "F":
                    f.draw(("L2b K3 F noise", case, s), keys.f_noise(keys.k3_pool(case, "native4096", s), "native4096"))
    for s in range(K4_SEEDS):
        for inst in L2B_CHANGE_SEGMENT:
            for k in K4_POOL_KINDS:
                for sp in SPLITS:
                    for r in K4_RUNS:
                        for q in range(32):
                            f.draw(("L2b K4 pool", inst, k, sp, r, s, q), with_net(keys.k4_pool(k, sp, r, s, q), keys.l2b_net(inst, r)))
                            if inst == "F":
                                f.draw(("L2b K4 F noise", k, sp, r, s, q), keys.f_noise(keys.k4_pool(k, sp, r, s, q), r))
        for inst in L2B_ARROW:
            for p in K4_PAIRS:
                for r in K4_RUNS:
                    for purpose in ("detectors-arrow", "detectors-profile"):
                        f.draw(("L2b K4 detectors", inst, p, r, purpose, s), with_net(keys.k4_detectors(p, r, s, purpose), keys.l2b_net(inst, r)))
        for inst in L2B_CHANGE_FLOW:
            for (c, sp, r) in K5_SETS:
                for (l, q) in units():
                    f.draw(("L2b K5 pool", inst, c, sp, r, s, l, q), with_net(keys.k5_pool(c, sp, r, s, l, q), keys.l2b_net(inst, r)))
                if inst == "F":
                    f.draw(("L2b K5 F noise", c, sp, r, s), (("K5b:" + c), sp, keys.l2b_net("F", r), s, "law2b-F", 0))
        for inst in L2B_FLOW:
            for crit, runs in K5_CRITERIA:
                for r in runs:
                    f.draw(("L2b K5 detectors", inst, crit, r, s), with_net(keys.k5_detectors(crit, r, s), keys.l2b_net(inst, r)))
    return f


def fam_law2b_real():
    f = Family("Law 2b instance tests, real data", 89376, 89376)
    segs = real_segments()
    for (ch, sp, r, seg) in segs:
        flow = isinstance(seg, str)
        for inst in (L2B_CHANGE_FLOW if flow else L2B_CHANGE_SEGMENT):
            f.draw(("L2b real pool", inst, ch, sp, r, seg), with_net(keys.real_pool(ch, sp, r, seg), keys.l2b_net(inst, r)))
            if sp == "verdict":
                for c in ("C2", "C3"):
                    f.draw(("L2b real control pool", inst, c, ch, r, seg), with_net(keys.control_pool(c, ch, r, seg), keys.l2b_net(inst, r)))
        if not flow:
            f.draw(("L2b real F noise", ch, sp, r, seg), keys.f_noise(keys.real_pool(ch, sp, r, seg)))
            if sp == "verdict":
                for c in ("C2", "C3"):
                    f.draw(("L2b real control F noise", c, ch, r, seg), keys.f_noise(keys.control_pool(c, ch, r, seg), control=c))
    streams = sorted({(ch, sp, r) for (ch, sp, r, seg) in segs if isinstance(seg, str)})
    for (ch, sp, r) in streams:
        f.draw(("L2b real F noise stream", ch, sp, r), (ch, sp, keys.l2b_net("F", r), "stream", "law2b-F", 0))
        if sp == "verdict":
            for c in ("C2", "C3"):
                f.draw(("L2b real control F noise stream", c, ch, r), (ch, sp, keys.l2b_net("F", r), "stream", c + "-law2b-F", 0))
    chan_runs = [(ch, r) for ch in PRIMARY for r in PRESENCE_RUNS] + [(ch, "instrument") for ch in SECOND.values()]
    for (ch, r) in chan_runs:
        for i in range(C4_SERIES):
            for inst in L2B_CHANGE_SEGMENT:
                f.draw(("L2b real C4 pool", inst, ch, r, i), with_net(keys.c4_pool(ch, r, i), keys.l2b_net(inst, r)))
            f.draw(("L2b real C4 F noise", ch, r, i), (ch, "verdict", keys.l2b_net("F", r), i, "C4-law2b-F", 0))
    for (a, b) in real_pairs():
        for inst in L2B_ARROW:
            for r in TRANSFER_RUNS:
                for purpose in ("detectors-arrow", "detectors-profile"):
                    f.draw(("L2b real detectors", inst, a, b, r, purpose), with_net(keys.real_detectors(a, b, r, purpose), keys.l2b_net(inst, r)))
        for inst in L2B_FLOW:
            for r in FLOW_RUNS:
                f.draw(("L2b real detectors", inst, a, b, r, "flow"), with_net(keys.real_detectors(a, b, r, "detectors-flow"), keys.l2b_net(inst, r)))
    return f


def fam_replicates():
    f = Family("Law 2b G1 null replicates (reduced grid)", 99240, 99240)
    rep_units = {"flow-L%d-q%d" % u for u in ((0, 0), (0, 1), (3, 0), (6, 31))}
    segs = []
    for (ch, sp, r, seg) in real_segments():
        if sp == "verdict" and ((isinstance(seg, int) and seg < 4) or (isinstance(seg, str) and seg in rep_units)):
            segs.append((ch, r, seg))
    for (ch, r, seg) in segs:
        flow = isinstance(seg, str)
        for inst in (L2B_FLOW if flow else L2B_PRESENCE):
            net = keys.l2b_net(inst, r)
            for rep in range(1, 11):
                f.draw(("L2b null series", inst, ch, r, seg, rep), (ch, "verdict", net, seg, "law2b-null", rep))
                f.draw(("L2b null pool", inst, ch, r, seg, rep), with_index(with_net(keys.real_pool(ch, "verdict", r, seg), net), rep))
                for c in ("C2", "C3"):
                    f.draw(("L2b null control", inst, c, ch, r, seg, rep), with_index(with_net(keys.control_series(c, ch, r, seg), net), rep))
                    f.draw(("L2b null control pool", inst, c, ch, r, seg, rep), with_index(with_net(keys.control_pool(c, ch, r, seg), net), rep))
                if inst == "F" and not flow:
                    f.draw(("L2b null F noise", ch, r, seg, rep), with_index(keys.f_noise(keys.real_pool(ch, "verdict", r, seg)), rep))
                    for c in ("C2", "C3"):
                        f.draw(("L2b null control F noise", c, ch, r, seg, rep), with_index(keys.f_noise(keys.control_pool(c, ch, r, seg), control=c), rep))
    for (a, b) in real_pairs():
        for rep in range(1, 11):
            for inst in L2B_ARROW:
                for r in TRANSFER_RUNS:
                    for purpose in ("detectors-arrow", "detectors-profile"):
                        f.draw(("L2b null detectors", inst, a, b, r, purpose, rep), with_index(with_net(keys.real_detectors(a, b, r, purpose), keys.l2b_net(inst, r)), rep))
            for inst in L2B_FLOW:
                for r in FLOW_RUNS:
                    f.draw(("L2b null detectors", inst, a, b, r, "flow", rep), with_index(with_net(keys.real_detectors(a, b, r, "detectors-flow"), keys.l2b_net(inst, r)), rep))
    return f


def planted_split():
    f = Family("Planted fault: K1 maps given their own pool keys", 0, 0)
    f.reason("K1 identity")
    for c in K2_CLASSES[:2]:
        for s in range(3):
            for i in range(K1_SERIES):
                k = keys.k1_pool(c, 1024, s)
                f.draw(("K1 pool", c, s), k if i == 0 else (k[0], k[1], "map%d" % i, k[3], k[4], k[5]), None if i == 0 else "K1 identity")
    return f


def planted_unstated():
    f = Family("Planted fault: a K2 control sharing a pool key with no stated reason", 0, 0)
    for s in range(5):
        f.draw(("K2 pool", "ar1_0.9", 4096, s), keys.k2_pool("ar1_0.9", 4096, s))
        f.draw(("K2 pool", "ar1_0.9", 4096, s), keys.k2_pool("ar1_0.9", 4096, s))
    return f


def old_seed_string(key):
    """The seed string as the code made it before the key epoch existed: master 20261121 and the six fields, joined by '|'."""
    return "|".join(str(v) for v in (20261121,) + tuple(key))


def epoch_checks(C, fams):
    """Reading D14 as amended by Amendment 4: epoch 0 unchanged, epochs never coinciding. Builds strings only, never a generator."""
    keyset = set()
    for f in fams:
        keyset |= f.keys
    keylist = sorted(keyset, key=repr)
    s0 = [seeds.seed_string(*k, epoch=0) for k in keylist]
    C.eq("epoch 0: every key's string equals the old seed string (master 20261121, no epoch), byte for byte", sum(1 for k, s in zip(keylist, s0) if s != old_seed_string(k)), 0)
    distinct0 = sorted(set(s0))
    dig = hashlib.sha256("\n".join(distinct0).encode("utf-8")).hexdigest()
    print("epoch 0: %d distinct strings over %d distinct keys, SHA-256 of the sorted strings %s" % (len(distinct0), len(keylist), dig))
    C.eq("epoch 0: the sorted distinct strings reproduce the digest pinned from the code before the change (%d strings)" % EPOCH0_STRINGS, (len(distinct0), dig), (EPOCH0_STRINGS, EPOCH0_DIGEST))
    C.eq("no key field contains '|', so the master field is always the first field of a string", sum(1 for k in keylist for v in k if "|" in str(v)), 0)
    C.eq("master field of epoch 0 is 20261121 and of epoch 1 is 20261121e1", (seeds.master_field(0), seeds.master_field(1), seeds.master_field(12)), ("20261121", "20261121e1", "20261121e12"))
    mf = [seeds.master_field(k) for k in range(10001)]
    C.check("master fields of epochs 0 to 10,000 are distinct and contain no '|' (so no two epochs give one string, for any key)", len(set(mf)) == len(mf) and not any("|" in m for m in mf))
    per = {0: set(distinct0)}
    for e in OTHER_EPOCHS:
        per[e] = {seeds.seed_string(*k, epoch=e) for k in keylist}
        C.eq("epoch %d: every key gives its own string (%d)" % (e, len(keylist)), len(per[e]), len(keylist))
    overlaps = sum(len(per[a] & per[b]) for a in per for b in per if a < b)
    allstr = set().union(*per.values())
    print("epochs %s: %d strings, %d shared between two epochs" % (", ".join(str(e) for e in sorted(per)), len(allstr), overlaps))
    C.eq("the strings of epochs 0 to %d never coincide across epochs" % max(OTHER_EPOCHS), overlaps, 0)
    C.eq("distinct 64-bit seeds equal distinct strings over epochs 0 to %d" % max(OTHER_EPOCHS), len({int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16) for s in allstr}), len(allstr))
    planted = {old_seed_string(k) for k in keylist[:1000]}
    C.check("must-fail: epoch-1 strings built without the epoch are flagged as coinciding with epoch 0", len(planted & per[0]) > 0)


def main():
    C = Checker()
    print("KEY CHECK: every seed key of D14 (Amendment 3), built with src/keys.py at the plan's counts, in key epoch 0 (master field %s)." % seeds.master_field(0))
    fams = [fam_k1(), fam_k2(), fam_k3(), fam_k4(False), fam_k4(True), fam_k5(False), fam_k5(True), fam_real(), fam_controls(), fam_law2b_known_answer(), fam_law2b_real(), fam_replicates()]
    for f in fams:
        print(f.line())
        C.check("%s: no two draws share a key except those on the plan's shared-by-design list" % f.name, f.ok())
        C.eq("%s: draws match the plan (%d)" % (f.name, f.expect[0]), f.n, f.expect[0])
        C.eq("%s: distinct keys match the plan (%d)" % (f.name, f.expect[1]), len(f.key_owner), f.expect[1])
    union = {}
    cross = 0
    names = ("K1", "K2", "K3", "K4 superset (every kind, split and run)", "K5 superset (every case, split and run)", "Controls C2, C3, C4 with the segment pools",
             "Law 2b pre-data checks", "Law 2b instance tests, real data", "Law 2b G1 null replicates (reduced grid)", "Real data pools and random detectors")
    for f in fams:
        if f.name in names:
            for s, owner in f.key_owner.items():
                prev = union.get(s)
                if prev is None:
                    union[s] = owner
                elif prev != owner:
                    cross += 1
    # the controls family repeats the real-data pools it sits beside with the same owner, so those are not collisions
    print("all families together: %d distinct keys, %d keys used by two different owners in different families" % (len(union), cross))
    C.eq("distinct keys over all families (the plan's total)", len(union), 417545)
    C.eq("no key used by two different owners in different families", cross, 0)
    C.eq("distinct 64-bit seeds equal distinct keys", len({int(__import__("hashlib").sha256(s.encode("utf-8")).hexdigest()[:16], 16) for s in union}), len(union))
    for f in (planted_split(), planted_unstated()):
        C.check("must-fail: %s is flagged" % f.name, not f.ok())
    k4 = [f for f in fams if f.name.startswith("K4 (")][0]
    C.eq("K4 draws on keys (the plan's 6,180 on 6,100)", (k4.n, len(k4.key_owner)), (6180, 6100))
    epoch_checks(C, fams)
    ok = C.done("KEY CHECK")
    if not ok:
        print("FAIL")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
