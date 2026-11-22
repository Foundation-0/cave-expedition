"""Exact arithmetic of PREREG sections 5, 6, 9 and 12: binomial tails, control rule and ceiling, per-run levels,
the pass rule of a run, the combination over runs, Holm's step-down method and the status of a counting instrument.
Only int and fractions.Fraction. Every threshold below is taken from the plan text."""
from fractions import Fraction
from math import comb

ALPHA = Fraction(1, 20)          # per-segment level 0.05
FWER = Fraction(1, 20)
FAMILY = 40                      # confirmatory tests (section 9)
LAW2B_FAMILY = 102               # section 12a
MARGIN = Fraction(1, 4)          # signal margin in every run (section 5, 6)
MIN_VALID = 12                   # fewer valid segments: underpowered
CONTROL_LEVEL = Fraction(1, 100)  # 1 percent excess point
CEILING_CHECKS = 24              # three controls in each of 8 runs (section 6)


def binom_tail(S, K, q=ALPHA):
    """P(Binomial(S, q) >= K), exact."""
    if S < 0:
        raise ValueError("S must be non-negative")
    if K <= 0:
        return Fraction(1)
    q = Fraction(q)
    return sum(comb(S, k) * q ** k * (1 - q) ** (S - k) for k in range(K, S + 1))


def smallest_k(S, level, q=ALPHA):
    """Smallest K with P(Binomial(S, q) >= K) <= level."""
    level = Fraction(level)
    for K in range(S + 2):
        if binom_tail(S, K, q) <= level:
            return K
    raise RuntimeError("no such K")


def excess_point(S, level=CONTROL_LEVEL):
    """Smallest K with P(Binomial(S, 0.05) >= K) <= 0.01."""
    return smallest_k(S, level)


def control_absent(Kc, Sc):
    """C2, C3, C4 rule: K below the binomial 1 percent excess point (A1)."""
    return Kc < excess_point(Sc)


def c_max(S):
    """Control ceiling (k - 1) / S with k the smallest count whose tail is at most 0.01 / 24."""
    return Fraction(smallest_k(S, CONTROL_LEVEL / CEILING_CHECKS) - 1, S)


def presence_runs(N, has_second_channel):
    """Runs of a presence test: native, block mean by 2 and subsampling by 2 and the window length N/2 (only where the
    result has at least 2,048 samples), two quantizations, window placement, instrument (if a second channel)."""
    runs = ["native"]
    if N // 2 >= 2048:
        runs += ["bm2", "sub2"]
    runs += ["q12", "q8", "placement"]
    if N // 2 >= 2048:
        runs += ["wlen"]
    if has_second_channel:
        runs += ["instrument"]
    return runs


def transfer_runs(kind, has_second_channel):
    """Arrow and profile: primary, the instrument net and window placement. Scale flow: those and the two amplitude maps."""
    runs = ["native", "placement"] + (["instrument"] if has_second_channel else [])
    if kind == "flow":
        runs += ["amp_scores", "amp_exp"]
    return runs


def run_level(nruns, family=FAMILY, fwer=FWER):
    """Level of one run: the test's smallest Holm level split equally across its runs (Bonferroni)."""
    return Fraction(fwer) / family / nruns


def run_passes(K, S, level, controls):
    """A presence run passes only if (1) its binomial p is within the run's level, (2) its share K/S exceeds the share
    of each control (C2, C3, C4: list of (Kc, Sc)) by at least 1/4, and (3) each control share is at most c_max(S).
    Returns dict with the three conditions."""
    if S < 1 or K < 0 or K > S:
        raise ValueError("need 0 <= K <= S and S >= 1")
    p = binom_tail(S, K)
    share = Fraction(K, S)
    cm = c_max(S)
    margin_ok = all(share - Fraction(Kc, Sc) >= MARGIN for (Kc, Sc) in controls)
    ceil_ok = all(Fraction(Kc, Sc) <= cm for (Kc, Sc) in controls)
    ok = p <= level and margin_ok and ceil_ok
    return {"p": p, "p_ok": p <= level, "margin_ok": margin_ok, "ceiling_ok": ceil_ok, "pass": ok}


def presence_p(runs):
    """Instrument presence p-value: the largest p over the runs times the number of runs, capped at 1, and 1 if any
    run fails the margin or ceiling rule. runs: list of run_passes dicts."""
    if len(runs) == 0:
        raise ValueError("no runs to combine")
    if any((not r["margin_ok"]) or (not r["ceiling_ok"]) for r in runs):
        return Fraction(1)
    return min(Fraction(1), max(r["p"] for r in runs) * len(runs))


def transfer_p(run_ps, control_ps):
    """Transfer p-value: the largest p over the runs times the number of runs (capped at 1), and 1 if in any run the same
    transfer with B's C2 series or with B's C3 series reaches p <= 0.01. control_ps: list of Fractions (all runs, both
    controls)."""
    if len(run_ps) == 0:
        raise ValueError("no runs to combine")
    if any(Fraction(c) <= Fraction(1, 100) for c in control_ps):
        return Fraction(1)
    return min(Fraction(1), max(Fraction(p) for p in run_ps) * len(run_ps))


def transfer_run_floor_ok(floor, nruns, family=FAMILY):
    """A transfer run counts as not passing unless its smallest reachable p is within its per-run level."""
    return Fraction(floor) <= run_level(nruns, family)


def holm(tests, m=FAMILY, alpha=FWER):
    """tests: dict name -> p (Fraction or int ratio). The family has m tests; a test not in the dict counts as p = 1.
    Step-down: reject the i-th smallest while p_(i) <= alpha / (m - i). Returns dict name -> (rejected, threshold)."""
    if len(tests) > m:
        raise ValueError("more tests than the family size")
    order = sorted(tests.items(), key=lambda kv: (Fraction(kv[1]), kv[0]))
    out = {}
    alive = True
    for i, (name, p) in enumerate(order):
        thr = Fraction(alpha) / (m - i)
        ok = alive and Fraction(p) <= thr
        if not ok:
            alive = False
        out[name] = (ok, thr)
    return out


STATUSES = ("invalid", "underpowered", "present", "net-dependent", "absent")


def instrument_status(n_valid, n_selected, primary_controls_ok, holm_pass, net_underpowered, primary_run_pass):
    """Status of a counting instrument (section 12). Underpowered: the primary run has fewer than 12 valid segments or
    more than 25 percent of its selected blocks invalid. Invalid: C2, C3 or C4 fails in the primary run. Present: the
    presence test passes at its Holm step (which needs the primary run and every applicable net run to pass, no net
    underpowered). Net-dependent: the primary run alone passes at the test's per-run level but the presence test does
    not pass. Absent: otherwise. When both underpowered and invalid hold, 'underpowered' is reported (provisional, see
    AMENDMENTS_NEEDED.md)."""
    invalid_blocks = n_selected - n_valid
    if n_valid < MIN_VALID or invalid_blocks * 4 > n_selected:
        return "underpowered"
    if not primary_controls_ok:
        return "invalid"
    if holm_pass and not net_underpowered:
        return "present"
    if primary_run_pass:
        return "net-dependent"
    return "absent"
