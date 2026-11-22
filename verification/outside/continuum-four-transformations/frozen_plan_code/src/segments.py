"""Segment rule of PREREG section 7. Block choice is a pure function of series length and parameters."""
import numpy as np
import gates


def select_blocks(n, N=4096, pad=128, nkeep=32, start=0):
    """Return (selected block starts in samples, J complete blocks, k)."""
    J = max(0, (n - start) // (N + pad))
    k = max(1, J // nkeep)
    idx = [i for i in range(J) if i % k == 0][:nkeep]
    return [start + i * (N + pad) for i in idx], J, k


def best_offset(block, N, pad=128):
    """Offset 0..pad that minimises (last - first)^2 + (last slope - first slope)^2; ties go to the smallest offset."""
    best, best_o = None, 0
    for o in range(pad + 1):
        s = block[o:o + N]
        cost = (s[-1] - s[0]) ** 2 + ((s[-1] - s[-2]) - (s[1] - s[0])) ** 2
        if best is None or cost < best:
            best, best_o = cost, o
    return best_o


def cut_segments(x, N=4096, pad=128, nkeep=32, start=0, valid=None):
    """valid: optional list of booleans for the selected blocks (decided from flags and sample times by a reader).
    Returns list of dicts with block start, offset, segment (None if invalid)."""
    x = gates.validate_series(x, N + pad)
    starts, J, k = select_blocks(len(x), N, pad, nkeep, start)
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


def underpowered(valid_flags, min_valid=12, max_invalid_frac=0.25):
    n = len(valid_flags)
    nv = sum(1 for v in valid_flags if v)
    return nv < min_valid or (n - nv) > max_invalid_frac * n
