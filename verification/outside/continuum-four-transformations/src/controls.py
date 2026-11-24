"""Controls of PREREG section 6 that are series transformations (C1 is the pool inside every test; C5 is a transfer with
B's C2 or C3 series in place of B, see pipeline.py; C6 needs real data and has no code here). Keys follow D14 (keys.py). Each function
takes the key epoch of its draws as a required keyword; the real-data path passes keys.REAL_DATA_EPOCH (D14 as amended by Amendment 4)."""
import numpy as np
import iaaft
import keys


def c2_surrogate_as_data(seg, key, *, epoch):
    """C2: one fixed surrogate of the segment (made from its normal scores). key = keys.control_series("C2", ...)."""
    Y, _, _ = iaaft.iaaft_surrogates(seg, 1, keys.rng(key, epoch))
    return Y[0]


def c3_shuffle(seg, key, *, epoch):
    """C3: random permutation of the segment. key = keys.control_series("C3", ...)."""
    return iaaft.shuffle_series(seg, keys.rng(key, epoch))


def c4_generated_noise(fit_segments, channel, run, N, n_series=32, *, epoch):
    """C4: 32 series per instrument with the fit-set median periodogram and the fit-set value distribution. Series i uses
    keys.c4_series(channel, run, i)."""
    segs = [np.asarray(s, dtype=np.float64) for s in fit_segments]
    n = min(len(s) for s in segs)
    med = np.median(np.stack([iaaft.periodogram(s[:n]) for s in segs]), axis=0)
    vals = np.concatenate(segs)
    return [iaaft.generated_noise(med, vals, N, keys.rng(keys.c4_series(channel, run, i), epoch)) for i in range(n_series)]
