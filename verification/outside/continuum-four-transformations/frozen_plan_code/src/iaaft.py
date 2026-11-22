"""IAAFT surrogates (Schreiber and Schmitz, PRL 77, 635, 1996) and the broken must-fail variants.
PROVISIONAL CHOICES (the plan names IAAFT but fixes none of these; see AMENDMENTS_NEEDED.md, item A1):
start from a random permutation of the series; alternate spectrum step and rank-remap step;
stop when the rank order no longer changes or after MAX_ITER rounds; end on the rank-remap step,
so the surrogate has exactly the values of the series."""
import numpy as np

MAX_ITER = 100


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
    x = np.asarray(x, dtype=np.float64)
    init = rng.permuted(np.tile(x, (M, 1)), axis=1)
    return iaaft_core(np.sort(x), np.abs(np.fft.rfft(x)), init, max_iter)


def leaky_surrogates(x, M, rng):
    """MUST-FAIL variant. Circular shifts of the series keep the spectrum, the values and the whole time arrow."""
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
    (quantiles at (k + 1/2)/n), made by the same IAAFT loop."""
    q = np.quantile(np.asarray(values, dtype=np.float64), (np.arange(n) + 0.5) / n)
    init = rng.permutation(q)[None, :]
    Y, _, _ = iaaft_core(q, np.sqrt(np.asarray(med_periodogram)), init, max_iter)
    return Y[0]
