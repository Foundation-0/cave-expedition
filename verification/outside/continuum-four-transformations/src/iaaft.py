"""IAAFT surrogates (Schreiber and Schmitz, PRL 77, 635, 1996) made from normal scores (PREREG section 4).

Rule of the plan: every series is replaced by its normal scores Phi^-1((r - 1/2)/n) (mid-ranks, see ranks.py);
each surrogate starts from a seeded random permutation of the scores and alternates two steps: impose the Fourier
amplitudes of the scores, then replace values by the sorted scores in the current rank order. It stops when the
rank order is unchanged between two successive iterations, or after MAX_ITER = 1,000 iterations, and ends on the
rank step, so a surrogate has exactly the scores as its values.

Reading used for 'the rank order is unchanged between two successive iterations': the array produced by the rank
step equals the array that entered the iteration (the values are the sorted scores, so equal arrays mean an
unchanged assignment of scores to positions). The start (the random permutation) counts as the first iterate.

Also here: the MUST-FAIL variants used by the known-answer controls (raw-value surrogates, circular shifts)."""
import numpy as np
import ranks

MAX_ITER = 1000
RAW_MAX_ITER = 100  # only for the frozen plan's raw-value variant (must-fail control of K2)


def iaaft_core(sorted_vals, amp, init, max_iter=MAX_ITER):
    Y = np.array(init, dtype=np.float64, copy=True)
    M, n = Y.shape
    active = np.arange(M)
    iters = np.zeros(M, dtype=np.int64)
    conv = np.zeros(M, dtype=bool)
    for _ in range(max_iter):
        cur = Y[active]
        F = np.fft.rfft(cur, axis=1)
        mag = np.abs(F)
        pos = mag > 0
        unit = np.where(pos, F / np.where(pos, mag, 1.0), 1.0)
        Z = np.fft.irfft(unit * amp, n=n, axis=1)
        order = np.argsort(Z, axis=1)
        new = np.empty_like(Z)
        np.put_along_axis(new, order, np.broadcast_to(sorted_vals, Z.shape), axis=1)
        same = np.all(new == cur, axis=1)
        Y[active] = new
        iters[active] += 1
        conv[active[same]] = True
        active = active[~same]
        if active.size == 0:
            break
    return Y, iters, conv


def iaaft_surrogates(x, M, rng, max_iter=MAX_ITER):
    """M surrogates made from the normal scores of x. Returns (Y (M, n), iterations (M,), converged (M,))."""
    z = ranks.normal_scores(x)
    init = rng.permuted(np.tile(z, (M, 1)), axis=1)
    return iaaft_core(np.sort(z), np.abs(np.fft.rfft(z)), init, max_iter)


def raw_surrogates(x, M, rng, max_iter=RAW_MAX_ITER):
    """MUST-FAIL variant (K1, K2): surrogates made from the raw values, as in the frozen plan."""
    x = np.asarray(x, dtype=np.float64)
    init = rng.permuted(np.tile(x, (M, 1)), axis=1)
    return iaaft_core(np.sort(x), np.abs(np.fft.rfft(x)), init, max_iter)


def leaky_surrogates(x, M, rng):
    """MUST-FAIL variant (K3): circular shifts keep the spectrum, the values and the whole time arrow."""
    x = np.asarray(x, dtype=np.float64)
    shifts = rng.integers(1, len(x), size=M)
    Y = np.stack([np.roll(x, int(s)) for s in shifts])
    return Y, np.zeros(M, dtype=np.int64), np.ones(M, dtype=bool)


def shuffle_series(x, rng):
    return rng.permutation(np.asarray(x, dtype=np.float64))


def periodogram(x):
    return np.abs(np.fft.rfft(np.asarray(x, dtype=np.float64))) ** 2


def generated_noise(med_periodogram, values, n, rng, max_iter=MAX_ITER):
    """C4: one series with the given median periodogram and the value distribution of `values`
    (quantiles at (k + 1/2)/n), made by the same IAAFT loop (spectrum step on the median amplitude,
    rank step onto the quantiles)."""
    q = np.quantile(np.asarray(values, dtype=np.float64), (np.arange(n) + 0.5) / n)
    init = rng.permutation(q)[None, :]
    Y, _, _ = iaaft_core(q, np.sqrt(np.asarray(med_periodogram, dtype=np.float64)), init, max_iter)
    return Y[0]
