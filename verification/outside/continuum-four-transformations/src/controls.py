"""Controls of PREREG section 6 that are series transformations. C1 is the pool inside every test.
C6 (instrument noise) needs real data and has no code here."""
import numpy as np
import iaaft
import seeds


def c2_surrogate_as_data(seg, key):
    """One fixed surrogate of the segment."""
    rng = seeds.rng_for(*key, "C2", 0)
    Y, _, _ = iaaft.iaaft_surrogates(seg, 1, rng)
    return Y[0]


def c3_shuffle(seg, key):
    return iaaft.shuffle_series(seg, seeds.rng_for(*key, "C3", 0))


def c4_generated_noise(fit_segments, instrument, split, n_series=32, N=4096):
    """32 series with the fit-set median periodogram and the fit-set value distribution."""
    med = np.median(np.stack([iaaft.periodogram(s) for s in fit_segments]), axis=0)
    vals = np.concatenate([np.asarray(s, dtype=np.float64) for s in fit_segments])
    return [iaaft.generated_noise(med, vals, N, seeds.rng_for(instrument, split, "native", i, "C4", 0)) for i in range(n_series)]
