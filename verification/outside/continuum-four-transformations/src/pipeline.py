"""Stream -> segments -> per-segment analysis -> instrument-level runs (PREREG sections 5, 7, 12).
These are the confirmatory-path building blocks. The listed transformation instances of section 12a are in a separate module that nothing here calls."""
from fractions import Fraction
import numpy as np
import controls
import flow
import keys
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
    """Apply the run's net to each native segment. None stays None. A segment whose values, after its offset and its net, are all
    equal is invalid (section 7, B7) and also becomes None: it stays in S as a non-rejecting segment."""
    net = RUN_NET[run]
    out = []
    for s in native_segs:
        if s is None:
            out.append(None)
            continue
        y = nets.apply(net, s)
        out.append(None if transfer.segments_constant(y) else y)
    return out


def analyse_list(series, key_of, kind="iaaft", workers=None, *, epoch):
    """series: list of series or None (invalid). key_of(q) gives the full pool key of entry q (keys.py, D14) and epoch the key epoch of
    the pools (required; the work item carries it to the worker). Returns a list of result dicts or None. Invalid blocks stay in the list
    (they count as non-rejecting segments)."""
    jobs, where = [], []
    for q, s in enumerate(series):
        if s is not None:
            jobs.append((s, key_of(q), kind, epoch))
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


def control_series(native_segs, run, channel):
    """C2 and C3 (one each per native segment, None stays None) for a run. They are made from the native segment, with the draws of
    keys.control_series, and are put through the run's net by the caller. The C2 and C3 series of an invalid segment are invalid and
    non-rejecting (None), section 7. C4 does not depend on any segment (controls.c4_generated_noise). Real-data draws keep epoch 0
    (keys.REAL_DATA_EPOCH)."""
    valid = [s is not None and not transfer.segments_constant(nets.apply(RUN_NET[run], s)) for s in native_segs]
    ep = keys.REAL_DATA_EPOCH
    c2 = [controls.c2_surrogate_as_data(s, keys.control_series("C2", channel, run, q), epoch=ep) if v else None for q, (s, v) in enumerate(zip(native_segs, valid))]
    c3 = [controls.c3_shuffle(s, keys.control_series("C3", channel, run, q), epoch=ep) if v else None for q, (s, v) in enumerate(zip(native_segs, valid))]
    return c2, c3


def presence_run(native_segs, run, channel, c4_native, kind="iaaft", workers=None):
    """One presence run: the real segments and the three controls through the same net. The pools use keys.real_pool for the real
    segments and the control pools of D14 (purposes C2-surrogates, C3-surrogates, C4-surrogates). Returns dict with K, S and the
    control counts, and run_passes needs the per-run level (levels.run_level). Real-data draws keep epoch 0 (keys.REAL_DATA_EPOCH)."""
    ep = keys.REAL_DATA_EPOCH
    net_series = run_series(native_segs, run)
    res = analyse_list(net_series, lambda q: keys.real_pool(channel, "verdict", run, q), kind, workers, epoch=ep)
    K, S = presence_counts(res)
    c2, c3 = control_series(native_segs, run, channel)
    r2 = analyse_list(run_series(c2, run), lambda q: keys.control_pool("C2", channel, run, q), kind, workers, epoch=ep)
    r3 = analyse_list(run_series(c3, run), lambda q: keys.control_pool("C3", channel, run, q), kind, workers, epoch=ep)
    r4 = analyse_list(run_series(c4_native, run), lambda q: keys.c4_pool(channel, run, q), kind, workers, epoch=ep)
    K2, S2 = presence_counts(r2)
    K3, S3 = presence_counts(r3)
    K4, S4 = presence_counts(r4)
    return {"K": K, "S": S, "C2": (K2, S2), "C3": (K3, S3), "C4": (K4, S4), "results": res}


def features(results, shift):
    """Arrow features (S_valid, 10), profile features (S_valid, 20) and the populated mask (10,) of the valid segments."""
    U, Pr = [], []
    pop = None
    for r in results:
        if r is None or r["all_zero_spread"]:
            continue   # an invalid segment, or one with zero spread at every lag, gives no transfer feature (sections 7 and 11a, D3)
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
