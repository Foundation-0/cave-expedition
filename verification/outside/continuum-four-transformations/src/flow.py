"""Scale flow of PREREG 4.1: block averaging by 2, order-4 pattern classes at lag 1.
The transfer step on the 56 flow features is NOT implemented (AMENDMENTS_NEEDED.md, item B1)."""
import numpy as np
import patterns
import stats43
import segments

MIN_SEG = 12


def orbit_classes():
    """The 8 classes of order-4 patterns that map to each other under time reversal and polarity flip."""
    perms, codes, rev, comp, names = patterns.tables(4)
    seen = {}
    for k in range(len(perms)):
        orb = tuple(sorted({k, int(rev[k]), int(comp[k]), int(rev[int(comp[k])])}))
        seen[orb] = True
    cls = sorted(seen.keys())
    if len(cls) != 8:
        raise RuntimeError("expected 8 classes of order-4 patterns, got %d" % len(cls))
    return [list(c) for c in cls]


def coarse_levels(x, N=4096, pad=128, nkeep=32):
    """Levels l = 0, 1, ... of block averaging by 2 over the whole stretch, while a level gives >= 12 segments."""
    x = np.asarray(x, dtype=np.float64)
    out = []
    l = 0
    cur = x
    while True:
        starts, J, k = segments.select_blocks(len(cur), N, pad, nkeep)
        if len(starts) < MIN_SEG:
            break
        out.append((l, cur))
        m = (len(cur) // 2) * 2
        cur = cur[:m].reshape(-1, 2).mean(axis=1)
        l += 1
    return out


def flow_pool_features(C4_lag1):
    """C4_lag1: (P, 24) order-4 counts at lag 1, row 0 real. Returns standardised class frequencies (P, 8)."""
    cls = orbit_classes()
    tot = C4_lag1.sum(axis=1).astype(np.float64)
    fr = np.stack([C4_lag1[:, c].sum(axis=1) / tot for c in cls], axis=1)
    return stats43.loo_standardise(fr)[0]


def flow_segment(seg, key, M=99):
    """Flow features of one segment (real row 0 plus M surrogate rows)."""
    import seeds
    rng = seeds.rng_for(*key, "surrogates", 0)
    pool, _, _ = stats43.make_pool(seg, M, rng, "iaaft")
    c = patterns.counts_batch(pool, 4, 1)[0]
    return flow_pool_features(c)
