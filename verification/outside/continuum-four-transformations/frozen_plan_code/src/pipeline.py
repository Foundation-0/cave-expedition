"""Stream -> segments -> per-segment analysis -> instrument-level results."""
import numpy as np
import nets
import par
import segments
import tasks
import transfer
import presence


def analyse_stream(x, instrument, split, net_label, js, N=4096, start=0, kind="iaaft", d4=False, valid=None):
    """Cut the stream by the segment rule and analyse every valid segment. Invalid blocks are kept
    in the list with result None (they count as non-rejecting segments)."""
    cut = segments.cut_segments(x, N=N, start=start, valid=valid)
    jobs, where = [], []
    for q, c in enumerate(cut):
        if c["seg"] is not None:
            jobs.append((c["seg"], (instrument, split, net_label, q), js, kind, d4))
            where.append(q)
    res = par.pmap(tasks.seg_task, jobs)
    full = [None] * len(cut)
    for q, r in zip(where, res):
        full[q] = r
    return cut, full


def presence_of(results):
    """K of S segments with p <= 0.05; invalid blocks stay in S as non-rejecting."""
    S = len(results)
    K = sum(1 for r in results if r is not None and r["reject"])
    return K, S, presence.presence_p(K, S)


def t3_features_of(results, shift, arrow_blind=False):
    """(S_valid, P, 30) features of the valid segments."""
    F = [transfer.t3_features(r["C3"], r["js"], shift, arrow_blind) for r in results if r is not None]
    return np.stack(F)
