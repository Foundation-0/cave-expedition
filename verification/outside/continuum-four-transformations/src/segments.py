"""Segment rule of PREREG section 7. Block choice is a pure function of series length and parameters."""
import numpy as np
import gates
import ranks

PAD = 128


def select_blocks(n, N=4096, pad=PAD, nkeep=32, start=0):
    """Return (selected block starts in samples, J complete blocks, k). A block is N + pad samples, numbered from
    `start`. With J complete blocks, k = max(1, floor(J / 32)); blocks with index divisible by k are selected and the
    first 32 are kept."""
    J = max(0, (n - start) // (N + pad))
    k = max(1, J // nkeep)
    idx = [i for i in range(J) if i % k == 0][:nkeep]
    return [start + i * (N + pad) for i in idx], J, k


def offset_costs(block, N, pad=PAD):
    """Cost of every offset 0..pad in units of 1/4, as exact integers, on the exact mid-ranks of the whole block:
    (jump between first and last value)^2 + (jump between first and last slope)^2 for the N-sample segment."""
    t = ranks.twice_midrank(block)
    o = np.arange(pad + 1)
    first, second = t[o], t[o + 1]
    last, pen = t[o + N - 1], t[o + N - 2]
    jump = last - first
    sl = (last - pen) - (second - first)
    return [int(v) for v in (jump * jump + sl * sl)]


def best_offset(block, N, pad=PAD):
    """Offset 0..pad with the smallest cost; the smallest offset among equal costs."""
    costs = offset_costs(np.asarray(block), N, pad)
    best = min(costs)
    return costs.index(best)


def cut_segments(x, N=4096, pad=PAD, nkeep=32, start=0, valid=None):
    """valid: optional list of booleans for the selected blocks (decided from flags, sample times and missing-value
    markers by a reader). Returns a list of dicts: block start, offset, seg (None if the block is invalid)."""
    x = gates.validate_series(x, N + pad)
    starts, J, k = select_blocks(len(x), N, pad, nkeep, start)
    if valid is not None and len(valid) != len(starts):
        raise ValueError("validity flags: %d given for %d selected blocks" % (len(valid), len(starts)))
    out = []
    for q, s in enumerate(starts):
        ok = True if valid is None else bool(valid[q])
        if not ok:
            out.append({"block": s, "offset": None, "seg": None})
            continue
        blk = x[s:s + N + pad]
        o = best_offset(blk, N, pad)
        out.append({"block": s, "offset": o, "seg": blk[o:o + N].copy()})
    return out


def underpowered(valid_flags, min_valid=12, max_invalid_frac_num=1, max_invalid_frac_den=4):
    """Underpowered: fewer than 12 valid segments, or more than 25 percent of the selected blocks invalid (exact)."""
    n = len(valid_flags)
    nv = sum(1 for v in valid_flags if v)
    return nv < min_valid or (n - nv) * max_invalid_frac_den > max_invalid_frac_num * n
