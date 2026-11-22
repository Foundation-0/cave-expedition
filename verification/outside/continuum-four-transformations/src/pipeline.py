"""Stream -> segments -> per-segment analysis -> instrument-level runs (PREREG sections 5, 7, 12).
These are the confirmatory-path building blocks. The listed transformation instances of section 12a are in a separate module that nothing here calls."""
from fractions import Fraction
import numpy as np
import controls
import flow
import levels
import nets
import par
import segments
import seeds
import tasks
import transfer

RUN_NET = {"native": "native", "bm2": "bm2", "sub2": "sub2", "q12": "q12", "q8": "q8", "placement": "native",
           "wlen": "native", "instrument": "native"}


def cut_run(stream, N, run, valid=None):
    """Native segments for one run of the nets table: list with None for invalid blocks, and the segment length used.
    Window placement shifts the block grid by half a block; the window length net uses N/2."""
    if run == "placement":
        return [c["seg"] for c in segments.cut_segments(stream, N=N, start=(N + segments.PAD) // 2, valid=valid)], N
    if run == "wlen":
        return [c["seg"] for c in segments.cut_segments(stream, N=N // 2, valid=valid)], N // 2
    return [c["seg"] for c in segments.cut_segments(stream, N=N, valid=valid)], N


def run_series(native_segs, run):
    """Apply the run's net to each native segment (None stays None)."""
    net = RUN_NET[run]
    return [None if s is None else nets.apply(net, s) for s in native_segs]


def analyse_list(series, prefix, kind="iaaft", workers=None):
    """series: list of series or None (invalid). prefix = (instrument, split, net). Returns list of result dicts or None.
    Invalid blocks stay in the list (they count as non-rejecting segments)."""
    jobs, where = [], []
    for q, s in enumerate(series):
        if s is not None:
            jobs.append((s, prefix + (q,), kind))
            where.append(q)
    res = par.pmap(tasks.seg_task, jobs, workers)
    full = [None] * len(series)
    for q, r in zip(where, res):
        full[q] = r
    return full


def presence_counts(results):
    """K of S segments with p <= 0.05; invalid blocks stay in S as non-rejecting."""
    S = len(results)
    K = sum(1 for r in results if r is not None and r["reject"])
    return K, S


def control_series(native_segs, run, instrument, split, fit_segments, N_native):
    """C2, C3 (one per native segment, None stays None) and C4 (32 series) for a run, each then put through the run's net."""
    c2 = [None if s is None else controls.c2_surrogate_as_data(s, (instrument, split, run, q)) for q, s in enumerate(native_segs)]
    c3 = [None if s is None else controls.c3_shuffle(s, (instrument, split, run, q)) for q, s in enumerate(native_segs)]
    return c2, c3


def presence_run(native_segs, run, prefix, c4_native, instrument, split, kind="iaaft", workers=None):
    """One presence run: the real segments and the three controls through the same net. Returns dict with K, S and the
    control counts, and run_passes needs the per-run level (levels.run_level)."""
    net_series = run_series(native_segs, run)
    res = analyse_list(net_series, prefix, kind, workers)
    K, S = presence_counts(res)
    c2, c3 = control_series(native_segs, run, instrument, split, None, None)
    r2 = analyse_list(run_series(c2, run), prefix + ("C2",), kind, workers)
    r3 = analyse_list(run_series(c3, run), prefix + ("C3",), kind, workers)
    r4 = analyse_list(run_series(c4_native, run), prefix + ("C4",), kind, workers)
    K2, S2 = presence_counts(r2)
    K3, S3 = presence_counts(r3)
    K4, S4 = presence_counts(r4)
    return {"K": K, "S": S, "C2": (K2, S2), "C3": (K3, S3), "C4": (K4, S4), "results": res}


def features(results, shift):
    """Arrow features (S_valid, 10), profile features (S_valid, 20) and the populated mask (10,) of the valid segments."""
    U, Pr = [], []
    pop = None
    for r in results:
        if r is None:
            continue
        u, p, m = transfer.level_vectors(r["zu"], r["z1"], r["z23"], r["js"], shift)
        U.append(u)
        Pr.append(p)
        pop = m if pop is None else (pop & m)
    if not U:
        raise ValueError("no valid segments")
    return np.stack(U), np.stack(Pr), pop


def transfer_arrow_profile(fitA, shiftA, verdB, shiftB, rng_arrow, rng_profile, R=transfer.R_DETECTORS):
    """Arrow and profile transfer of A (fit results) to B (verdict results). Returns (arrow dict, profile dict), each after
    the populated-feature floor."""
    UA, PA, popA = features(fitA, shiftA)
    UB, PB, popB = features(verdB, shiftB)
    wA_u = transfer.build_template(UA)
    wA_p = transfer.build_template(PA)
    arrow = transfer.transfer_test("arrow", wA_u, UB.mean(axis=0), transfer.pop_both(popA, popB, 1), rng_arrow, R)
    prof = transfer.transfer_test("profile", wA_p, PB.mean(axis=0), transfer.pop_both(popA, popB, 2), rng_profile, R)
    return transfer.apply_floor(arrow, "arrow"), transfer.apply_floor(prof, "profile")
