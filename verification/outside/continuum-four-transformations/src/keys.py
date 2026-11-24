"""The seed keys of PREREG section 11a, reading D14 as amended by Amendment 3. One function per kind of draw. A key is the tuple
(instrument, split, net, segment, purpose, index) that follows the master seed in the string of section 11 (see seeds.py).
Every random draw of the code takes its key from here. Two draws that the plan treats as independent never share a key. The keys
that more than one draw uses are listed in the plan under "Shared by design", and `known_answer/key_check.py` builds every key at the
plan's counts and checks both statements. Seeds are numbered from 0 and the index is 0 unless a function says otherwise.

Key epoch (reading D14 as amended by Amendment 4): a draw is made from a key and a key epoch. The epoch is a required argument of
rng(), and every function of src/ that draws takes it as a required keyword and hands it on, so the epoch reaches the draw explicitly
(also inside the worker processes of par.pmap, which get it with each work item). A known-answer test uses its own epoch for every draw,
its must-fail controls included. Real-data draws keep epoch 0 (REAL_DATA_EPOCH)."""
import seeds

K3_BLOCK = {"native4096": 4224, "placement": 4224, "native2048": 2176, "wlen2048": 2176,
            "bm2": 4224, "sub2": 4224, "q12": 4224, "q8": 4224}
K3_OWN_DRAW = ("native4096", "native2048", "placement", "wlen2048")
REAL_DATA_EPOCH = 0


def rng(key, epoch):
    """The numpy generator of a key in a key epoch. The epoch has no default: a call that forgets it fails."""
    return seeds.rng_for(*key, epoch=epoch)


def l2b_net(instance, run):
    """Net field of every draw made after a Law 2b instance is applied (D14, Law 2b)."""
    return "law2b-%s:%s" % (instance, run)


# K1 and K2 ------------------------------------------------------------------------------------------------------------
def k2_data(cls, n, seed):
    return ("K2:%s:%d" % (cls, n), "synthetic", "native", seed, "data", 0)


def k2_pool(cls, n, seed):
    return ("K2:%s:%d" % (cls, n), "synthetic", "native", seed, "surrogates", 0)


def k1_data(cls, n, seed):
    return ("K1:%s:%d" % (cls, n), "synthetic", "native", seed, "data", 0)


def k1_pool(cls, n, seed):
    return ("K1:%s:%d" % (cls, n), "synthetic", "native", seed, "surrogates", 0)


def k1int_data(cls, seed, n=1024):
    return ("K1int:%s:%d" % (cls, n), "synthetic", "native", seed, "data", 0)


def k1int_pool(cls, seed, n=1024):
    return ("K1int:%s:%d" % (cls, n), "synthetic", "native", seed, "surrogates", 0)


def k1wave_pool():
    return ("K1wave:4096", "synthetic", "native", 0, "surrogates", 0)


# K3 -------------------------------------------------------------------------------------------------------------------
def k3_data(case, use, seed):
    """The data draw of a use. The nets bm2, sub2, q12 and q8 use the native4096 draw."""
    d = use if use in K3_OWN_DRAW else "native4096"
    return ("K3:%s:%d" % (case, K3_BLOCK[d]), "synthetic", d, seed, "data", 0)


def k3_pool(case, use, seed):
    """Each pool uses the instrument of the data draw its segment comes from, net the use."""
    d = use if use in K3_OWN_DRAW else "native4096"
    return ("K3:%s:%d" % (case, K3_BLOCK[d]), "synthetic", use, seed, "surrogates", 0)


# K4 -------------------------------------------------------------------------------------------------------------------
def k4_data(kind, split, seed):
    return ("K4:" + kind, split, "native", seed, "data", 0)


def k4_aprime_shuffle(split, seed):
    return ("K4:Aprime:" + split, split, "native", seed, "shuffle", 0)


def k4_aprime_block(split, seed, position):
    """The index is the block's position in the shuffled order, 0 to 32."""
    return ("K4:Aprime:" + split, split, "native", seed, "block-surrogate", position)


def k4_pool(kind, split, run, seed, segment):
    return ("K4:%s:s%d" % (kind, seed), split, run, segment, "surrogates", 0)


def k4_detectors(pair, run, seed, purpose):
    """pair is 'A>B', 'A>C', 'A>Aprime', 'S>Sr' or 'Sr>S'; purpose 'detectors-arrow' or 'detectors-profile'."""
    return ("K4:" + pair, "verdict", run, seed, purpose, 0)


# K5 -------------------------------------------------------------------------------------------------------------------
def k5_data(case, split, seed):
    return ("K5b:" + case, split, "native", seed, "data", 0)


def k5_whole(seed):
    return ("K5b:cascade_iaaft", "fit", "native", seed, "whole-surrogate", 0)


def k5_unit_segment(seed, level, unit):
    return "s%d-flow-L%d-q%d" % (seed, level, unit)


def k5_pool(case, split, run, seed, level, unit):
    """case names the series the units are cut from (cascade_rank, cascade_iaaft, ...), not the draw it is made from."""
    return ("K5b:" + case, split, run, k5_unit_segment(seed, level, unit), "surrogates", 0)


def k5_detectors(criterion, run, seed):
    """criterion is 'cascade>cascade_rank', 'cascade>yprime' or 'cascade_iaaft>cascade'."""
    return ("K5b:" + criterion, "verdict", run, seed, "detectors-flow", 0)


# real data and controls -----------------------------------------------------------------------------------------------
def real_pool(channel, split, run, segment):
    return (channel, split, run, segment, "surrogates", 0)


def real_detectors(a, b, run, purpose):
    """a and b name the instruments of the ordered pair. Segment 0."""
    return ("%s>%s" % (a, b), "verdict", run, 0, purpose, 0)


def control_series(control, channel, run, segment):
    """C2 or C3 of a verdict segment or flow unit."""
    if control not in ("C2", "C3"):
        raise ValueError("control must be C2 or C3")
    return (channel, "verdict", run, segment, control, 0)


def control_pool(control, channel, run, segment):
    """The pool of a control series: the control's name and a hyphen before the purpose it would have on a segment."""
    return (channel, "verdict", run, segment, control + "-surrogates", 0)


def c4_series(channel, run, i):
    return (channel, "verdict", run, i, "C4", 0)


def c4_pool(channel, run, i):
    return (channel, "verdict", run, i, "C4-surrogates", 0)


def f_noise(base_key, instance_run=None, control=None):
    """Instance F's noise: the key the same draw has without the instance (purpose law2b-F), net law2b-F:<run> (D14, Law 2b), and for
    a control series the control's name and a hyphen before the purpose."""
    inst, split, net, seg, _, idx = base_key
    purpose = "law2b-F" if control is None else control + "-law2b-F"
    return (inst, split, l2b_net("F", net if instance_run is None else instance_run), seg, purpose, idx)
