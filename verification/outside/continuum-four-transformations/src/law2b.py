"""Listed transformation instances of PREREG section 12a (Law 2b), as separate named functions.

NOT called by the confirmatory path: no other module imports this one (units_check.py verifies it). The instances are
fixed here so that they are available to the fixed rule of section 12a; their statistics are checked against hand-made
counts only. Window names: W whitening, Q Bregman (quadratic generator), H Hellinger, F white floor, M max-plus,
D first differences, O4 order 4, E event-rich domain, B block maxima, R normal scores before block averaging.

Also here: the minimal state of the Law 2b search that Amendment 4 (item C2) needs, for an instance whose pre-data check failed. Such an
instance is "not tested": it cannot rescue, each of its tests enters the Holm procedure with p = 1, and an adverse outcome that lists it
cannot be recorded as final. The instance checks themselves and the verdict stage that would call these functions are not built."""
import math
import numpy as np
import levels
import patterns
import keys
import ranks


# T1 gauge: W ------------------------------------------------------------------------------------------------
def running_median_reflect(v, width=33):
    """Running median over `width` neighbouring values; the window is reflected at both ends (READING: numpy 'reflect',
    which does not repeat the edge value; see AMENDMENTS_NEEDED.md)."""
    h = width // 2
    padded = np.pad(np.asarray(v, dtype=np.float64), h, mode="reflect")
    win = np.lib.stride_tricks.sliding_window_view(padded, width)
    return np.median(win, axis=1)


def whiten_W(x):
    """Zero-phase whitening: divide the Fourier transform by the square root of the running median of |X(f)|^2 over 33
    neighbouring frequencies, set the zero frequency to 0, transform back."""
    x = np.asarray(x, dtype=np.float64)
    X = np.fft.rfft(x)
    med = running_median_reflect(np.abs(X) ** 2, 33)
    if not np.all(med > 0):
        raise ValueError("whitening needs a positive running median at every frequency")
    Y = X / np.sqrt(med)
    Y[0] = 0.0
    return np.fft.irfft(Y, n=len(x))


# T4 spectral shift: F -----------------------------------------------------------------------------------------
def white_floor_F(x, key, *, epoch):
    """Independent Gaussian noise with standard deviation 1/1000 of the segment's standard deviation, added first. key is the full key of
    the noise draw, keys.f_noise(...): the key the draw has without the instance, with net law2b-F:<run> and purpose law2b-F (D14), and
    epoch its key epoch (required): the epoch of the known-answer test whose draws a pre-data check reuses, or 0 on real data."""
    x = np.asarray(x, dtype=np.float64)
    if not (isinstance(key, tuple) and len(key) == 6):
        raise ValueError("a noise key has six fields")
    rng = keys.rng(key, epoch)
    return x + (x.std() / 1000.0) * rng.standard_normal(len(x))


# T6 projection: D and O4 ---------------------------------------------------------------------------------------
def differences_D(x):
    """First differences of the segment (lag 1)."""
    x = np.asarray(x, dtype=np.float64)
    return x[1:] - x[:-1]


def o4_lag_js(n):
    """Order-4 lags 2^j, j = 0 .. 9, with 3 tau at most n/4 (exact: 12 tau <= n)."""
    return [j for j in range(10) if 12 * (1 << j) <= n]


def sigma_O4(counts4):
    """Sigma_hat at order 4: 75 patterns, pseudocount 1/2 each, denominator count + 75/2."""
    return patterns.sigma_hat(counts4, 4)


# T2 Bregman, T3 Hellinger, T5 max-plus ----------------------------------------------------------------------
def sigma_Q(counts3):
    """Sum over patterns of (p(pi) - p(rev pi))^2."""
    p = patterns.probs(counts3, 3)
    rev = patterns.tables(3)["rev"]
    return ((p - p[..., rev]) ** 2).sum(axis=-1)


def sigma_H(counts3):
    """Sum over patterns of (sqrt p(pi) - sqrt p(rev pi))^2."""
    p = np.sqrt(patterns.probs(counts3, 3))
    rev = patterns.tables(3)["rev"]
    return ((p - p[..., rev]) ** 2).sum(axis=-1)


def sigma_M(counts3):
    """Largest absolute log ratio over pattern pairs (max-plus limit of the log ratios)."""
    p = patterns.probs(counts3, 3)
    rev = patterns.tables(3)["rev"]
    return np.abs(np.log(p) - np.log(p[..., rev])).max(axis=-1)


def _pair_ix():
    ix = patterns.tables(3)["index"]
    return [(ix[(0, 1, 2)], ix[(2, 1, 0)]), (ix[(0, 2, 1)], ix[(1, 2, 0)]), (ix[(1, 0, 2)], ix[(2, 0, 1)])]


def a_features_Q(counts3):
    """a_k replaced by p(pi_k) - p(rev pi_k). Transforms like a_k under reversal and polarity flip."""
    p = patterns.probs(counts3, 3)
    return tuple(p[..., a] - p[..., b] for a, b in _pair_ix())


def a_features_H(counts3):
    """a_k replaced by sqrt p(pi_k) - sqrt p(rev pi_k)."""
    p = np.sqrt(patterns.probs(counts3, 3))
    return tuple(p[..., a] - p[..., b] for a, b in _pair_ix())


def max_plus_score(w, f):
    """Max-plus form of the score w . f: the largest of w_k f_k."""
    return (np.asarray(w, dtype=np.float64) * np.asarray(f, dtype=np.float64)).max(axis=-1)


# T7 domain and residual: E and R -------------------------------------------------------------------------------
def _order_stat(sorted_vals, p_num, p_den):
    """The order statistic of rank ceil(p n), no interpolation (section 12a, instance E). p = p_num / p_den exactly."""
    n = len(sorted_vals)
    k = -(-p_num * n // p_den)          # ceil(p n) in integers
    return sorted_vals[max(1, k) - 1]


def tail_spread(x):
    """(q99.9 - q0.1) / (q75 - q25) as an exact rational. A quantile q_p is the order statistic of rank ceil(p n), with no
    interpolation (section 12a). Values are floats, converted exactly to rationals."""
    from fractions import Fraction
    v = sorted(float(t) for t in np.asarray(x, dtype=np.float64))
    q = [Fraction(_order_stat(v, a, b)) for (a, b) in ((999, 1000), (1, 1000), (3, 4), (1, 4))]
    den = q[2] - q[3]
    if not den > 0:
        raise ValueError("interquartile range is zero")
    return (q[0] - q[1]) / den


def event_rich_threshold(fit_segments):
    """Median over the instrument's fit segments of the tail spread, as an exact rational (the mean of the two middle values when
    their number is even). Fitted on fit data only."""
    from fractions import Fraction
    t = sorted(tail_spread(s) for s in fit_segments)
    m = len(t)
    if m == 0:
        raise ValueError("no fit segments")
    return t[m // 2] if m % 2 == 1 else (t[m // 2 - 1] + t[m // 2]) / 2


def event_rich(seg, threshold):
    """A verdict segment is event-rich if its tail spread exceeds the threshold (exact comparison)."""
    return tail_spread(seg) > threshold


def flow_normal_scores_R(x):
    """R: normal scores of the ranks before block averaging."""
    return ranks.normal_scores(x)


FLOW_BLOCK_OP_B = "max"             # B: block maxima of 2 replace block means (flow.block_average op)
flow_freq_map_H = np.sqrt           # H: square roots of the class frequencies before standardisation


# Law 2b search state with untested instances (section 12a as amended by Amendment 4, item C2) --------------------------
ADVERSE_KINDS = ("a", "b", "c")      # (a) presence, per absent counting instrument; (b) arrow, per adverse pair; (c) scale flow, per adverse pair
INSTANCES = {"a": ("W", "Q", "H", "F", "M", "D", "O4", "E"), "b": ("W", "Q", "H", "F", "M", "D", "E"), "c": ("W", "H", "F", "B", "D", "R")}
FAMILY_OF = {"W": "T1_GAUGE_SIMILARITY", "Q": "T2_AFFINE_BREGMAN", "H": "T3_METRIC_CHART", "F": "T4_SPECTRAL_PSD_SHIFT", "M": "T5_SEMIRING_TROPICAL",
             "B": "T5_SEMIRING_TROPICAL", "D": "T6_SUBSPACE_PROJECTION", "O4": "T6_SUBSPACE_PROJECTION", "E": "T7_ORDER_DOMAIN_RESIDUAL",
             "R": "T7_ORDER_DOMAIN_RESIDUAL"}
KIND_NAME = {"a": "presence (a)", "b": "arrow transfer (b)", "c": "scale-flow transfer (c)"}
STATE_WORDING = {"transformed core": "evidence against at the confirmatory level, transformed core passed under instance %s",
                 "final": "evidence against, final",
                 "unresolved": "evidence against at the confirmatory level, Law 2b search unresolved"}


def untested_instances(checks):
    """The instances that are not tested (C2): those that failed any of their pre-data checks. checks: dict instance -> dict check name ->
    bool (True when the check passed). Every instance named must have at least one recorded check, since the list of untested instances
    is fixed before any data file is opened. Returns a frozenset of instance names."""
    out = set()
    for inst, res in checks.items():
        if inst not in FAMILY_OF:
            raise ValueError("unknown Law 2b instance %r" % (inst,))
        if not res:
            raise ValueError("instance %s has no recorded pre-data check" % inst)
        for name, ok in res.items():
            if not isinstance(ok, (bool, np.bool_)):
                raise TypeError("check %s of instance %s must be a bool" % (name, inst))
        if not all(res.values()):
            out.add(inst)
    return frozenset(out)


def test_name(kind, instance, item):
    """Name of one test of the 102-test Law 2b family: kind, instance and triggering item."""
    return "law2b:%s:%s:%s" % (kind, instance, item)


def holm_family(computed, untested):
    """Holm over the Law 2b family (levels.holm, m = 102). computed: dict test name -> p of the tests computed. A test of an untested
    instance must not be computed: it stays out of the dict, so levels.holm counts it with p = 1, as a test that is not computed.
    untested: the untested instances; a computed test of one of them is refused."""
    for name in computed:
        parts = name.split(":")
        if len(parts) != 4 or parts[0] != "law2b" or parts[1] not in ADVERSE_KINDS or parts[2] not in INSTANCES[parts[1]]:
            raise ValueError("not a Law 2b test name: %r" % (name,))
        if parts[2] in untested:
            raise ValueError("instance %s is not tested, so its test %s enters Holm with p = 1 and has no computed p" % (parts[2], name))
    return levels.holm(computed, m=levels.LAW2B_FAMILY)


def untested_routes(kind, untested):
    """The rescue routes of one kind that could not be tested, in the order of the table of section 12a, named for the report."""
    return ["instance %s (%s) for %s: not tested" % (i, FAMILY_OF[i], KIND_NAME[kind]) for i in INSTANCES[kind] if i in untested]


def search_state(kind, items, untested, passes, vacuous, obstruction):
    """State of one triggered kind of "evidence against" (section 12a, Recording, with Amendment 4, item C2).
    kind: 'a', 'b' or 'c'. items: the triggering items (the absent counting instruments for (a), the adverse pairs for (b) and (c)).
    untested: instances whose pre-data check failed (untested_instances). passes: dict (instance, item) -> bool, for every tested instance
    of the kind and every item, True when the instance's test passes for that item. vacuous: tested instances found vacuous under G1.
    obstruction: bool, whether the obstruction of G4 holds under the confirmatory run and every tested instance.
    Returns dict(state, rescued_by, untested_routes, wording). Transformed core: a tested instance that is not vacuous passes for every
    item. Otherwise an untested instance leaves the search incomplete, so the state is unresolved and never final. Otherwise final if no
    instance passes for any item and the obstruction holds, and unresolved if not."""
    if kind not in ADVERSE_KINDS:
        raise ValueError("kind must be one of %s" % (ADVERSE_KINDS,))
    items = list(items)
    if not items or len(set(items)) != len(items):
        raise ValueError("need at least one triggering item, each named once")
    listed = INSTANCES[kind]
    untested = frozenset(i for i in untested if i in listed)
    tested = [i for i in listed if i not in untested]
    if not set(vacuous) <= set(tested):
        raise ValueError("only a tested instance of this kind can be vacuous")
    if not isinstance(obstruction, (bool, np.bool_)):
        raise TypeError("obstruction must be a bool")
    want = {(i, it) for i in tested for it in items}
    if set(passes) != want:
        raise ValueError("passes needs a result for every tested instance and item, and none for an untested instance")
    if any(not isinstance(v, (bool, np.bool_)) for v in passes.values()):
        raise TypeError("each pass result must be a bool")
    rescued = [i for i in tested if i not in vacuous and all(passes[(i, it)] for it in items)]
    if rescued:
        state = "transformed core"
        wording = STATE_WORDING[state] % ", ".join(rescued)
    elif untested:
        state = "unresolved"
        wording = STATE_WORDING[state]
    elif obstruction and not any(passes.values()):
        state = "final"
        wording = STATE_WORDING[state]
    else:
        state = "unresolved"
        wording = STATE_WORDING[state]
    routes = untested_routes(kind, untested)
    if routes:
        wording += "; rescue routes not tested: " + "; ".join(routes)
    return {"state": state, "rescued_by": rescued, "untested_routes": routes, "wording": wording}
