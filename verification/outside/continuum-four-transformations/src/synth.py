"""Synthetic series for the known-answer tests (PREREG section 10). Seeds follow the rule of section 11
(seeds.rng_for). Readings that the plan leaves open are marked READING and listed in AMENDMENTS_NEEDED.md."""
import math
import numpy as np
import seeds


def standardise(x):
    x = np.asarray(x, dtype=np.float64)
    return (x - x.mean()) / x.std()


def white(n, rng):
    return rng.standard_normal(n)


def ar1(phi, n, rng, unit_variance=False):
    """Stationary AR(1): start drawn from the stationary law. With unit_variance the innovations have standard
    deviation sqrt(1 - phi^2), so the stationary variance is exactly 1 (used for g and h of K2b)."""
    e = rng.standard_normal(n)
    if unit_variance:
        e = e * math.sqrt(1.0 - phi * phi)
    x = np.empty(n)
    x[0] = e[0] / math.sqrt(1.0 - phi * phi)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return x


def powerlaw(beta, n, rng):
    """Fourier synthesis, power proportional to f^-beta, random phases (complex Gaussian coefficients)."""
    m = n // 2 + 1
    amp = np.zeros(m)
    amp[1:] = np.arange(1, m, dtype=np.float64) ** (-beta / 2.0)
    spec = amp * (rng.standard_normal(m) + 1j * rng.standard_normal(m))
    spec[0] = 0.0
    return np.fft.irfft(spec, n=n)


SINE_FREQS = (0.0137, 0.0781, 0.2113)  # cycles per sample, unit amplitude, random phases, in white noise of sd 1


def sines(n, rng):
    t = np.arange(n, dtype=np.float64)
    x = rng.standard_normal(n)
    for f in SINE_FREQS:
        x = x + np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi))
    return x


K2A_CLASSES = ("white", "ar1_0.5", "ar1_0.9", "ar1_0.99", "pl_1", "pl_2", "sines3")  # the 7 null classes
K2B_CLASSES = ("g2", "absh")  # g^2 with g AR(1) 0.9, |h| with h AR(1) 0.99
K2_CLASSES = K2A_CLASSES + K2B_CLASSES
K2_MAPS = ("id", "exp", "cube")


def _plain(base, n, rng):
    """The plain draw of a class: the 7 null classes standardised to mean 0 and sd 1, g^2 and |h| as defined."""
    if base == "white":
        return standardise(white(n, rng))
    if base.startswith("ar1_"):
        return standardise(ar1(float(base[4:]), n, rng))
    if base.startswith("pl_"):
        return standardise(powerlaw(float(base[3:]), n, rng))
    if base == "sines3":
        return standardise(sines(n, rng))
    if base == "g2":
        return ar1(0.9, n, rng, True) ** 2
    if base == "absh":
        return np.abs(ar1(0.99, n, rng, True))
    raise ValueError("unknown class " + base)


def class_series(cls, idx, n=4096, prefix="K2"):
    """One series of class cls, optionally 'cls|exp' or 'cls|cube', seed index idx. The seed depends on the plain class only
    (instrument `<prefix>:<class>:<length>`), so the exp and cube versions are the same draw, mapped. For the exp and cube
    versions, exp and cube act on the standardised series (for the 7 null classes it is the plain series already; for g^2 and |h|
    the versions exist for K1 only, B5)."""
    base, _, m = cls.partition("|")
    rng = seeds.rng_for("%s:%s:%d" % (prefix, base, n), "synthetic", "native", idx, "data", 0)
    x = _plain(base, n, rng)
    if m in ("", "id"):
        return x
    xs = standardise(x)
    if m == "exp":
        return np.exp(xs)
    if m == "cube":
        return xs ** 3
    raise ValueError("unknown map " + m)


def k2_series(cls, idx, n=4096):
    return class_series(cls, idx, n, "K2")


def k1_series(cls, idx, n=1024):
    return class_series(cls, idx, n, "K1")


def k1_int_series(cls, idx, n=1024):
    """K1 tied input (b): a null class made integer-valued as round(8 z), z the standardised plain series; draws under `K1int`."""
    base = cls.partition("|")[0]
    rng = seeds.rng_for("K1int:%s:%d" % (base, n), "synthetic", "native", idx, "data", 0)
    return np.round(8.0 * standardise(_plain(base, n, rng)))


def tied_waveform():
    """K1 tied input (a): [0, 0, 1, 2, 2, 1, 0, 0] repeated 512 times (4,096 samples), exactly time-symmetric."""
    return np.array([0, 0, 1, 2, 2, 1, 0, 0] * 512, dtype=np.float64)


SHOT_RATE = 0.01
SHOT_DECAY = 10.0
SHOT_HEIGHT_SD = 3.0
SHOT_KERNEL_LEN = 100


def shots_on(bg, bg_sd, rng, n, rate=SHOT_RATE):
    """Exponential shots: a shot starts at each sample with probability `rate`, rises at once to 3 times the exact
    standard deviation of the background and decays over 10 samples (kernel cut at 100 samples)."""
    pre = SHOT_KERNEL_LEN
    ev = (rng.random(n + pre) < rate).astype(np.float64)
    kern = SHOT_HEIGHT_SD * bg_sd * np.exp(-np.arange(SHOT_KERNEL_LEN) / SHOT_DECAY)
    sh = np.convolve(ev, kern)[pre:pre + n]
    return bg + sh


def shots_ar(n, rng, phi=0.9):
    """K3 shots and K4 instrument A: AR(1) background (coefficient 0.9), exact background sd 1 / sqrt(1 - phi^2)."""
    return shots_on(ar1(phi, n, rng), 1.0 / math.sqrt(1.0 - phi * phi), rng, n)


def shots_B(n, rng):
    """K4 instrument B: shots at twice the rate (decay over 10 fine samples) on power-law noise of slope 1 (unit
    standard deviation), then every second sample kept and the sign flipped. READING: the shot rate is 0.01 per fine
    sample, which is 0.02 per kept sample (twice the rate of A), the builder's construction."""
    fine = shots_on(standardise(powerlaw(1.0, 2 * n, rng)), 1.0, rng, 2 * n)
    return -fine[::2].copy()


def logistic(n, rng):
    x = rng.uniform(0.05, 0.95)
    for _ in range(1000):
        x = 4.0 * x * (1.0 - x)
    v = np.empty(n)
    for t in range(n):
        x = 4.0 * x * (1.0 - x)
        v[t] = x
    return v + 0.1 * v.std() * rng.standard_normal(n)


SAW_SD = 0.5 * math.sqrt((64 * 64 - 1) / 12.0) / 64.0  # half the standard deviation of the ramp k/64, k = 0..63 (0.1443)
SAW_SD_NOISY = 0.5  # the other reading ("half its amplitude"): reported, does not gate


def sawtooth(n, rng, noise_sd=SAW_SD):
    """Period 64, peak to peak (almost) 1, rising in ramps, random phase, white noise of standard deviation noise_sd."""
    ph = int(rng.integers(0, 64))
    t = np.arange(n)
    return ((t + ph) % 64) / 64.0 + noise_sd * rng.standard_normal(n)


K3_CASES = ("shots", "logistic", "sawtooth", "sawtooth_noisy")


def k3_series(case, tag, idx, n):
    """One K3 series of length n. tag names the use (native, placement, ...) so that each use is an independent draw."""
    rng = seeds.rng_for("K3:%s:%d" % (case, n), "synthetic", tag, idx, "data", 0)
    if case == "shots":
        return shots_ar(n, rng)
    if case == "logistic":
        return logistic(n, rng)
    if case == "sawtooth":
        return sawtooth(n, rng, SAW_SD)
    if case == "sawtooth_noisy":
        return sawtooth(n, rng, SAW_SD_NOISY)
    raise ValueError("unknown case " + case)


CASCADE_SIGMA = 0.5


def cascade(n, rng, sigma=CASCADE_SIGMA):
    """Dyadic random cascade with log-normal weights of mean 1 and log standard deviation 0.5, depth log2 n."""
    depth = int(math.ceil(math.log2(n)))
    x = np.ones(1)
    for lev in range(depth):
        w = np.exp(sigma * rng.standard_normal(2 ** (lev + 1)) - sigma * sigma / 2.0)
        x = np.repeat(x, 2) * w
    return x[:n]


def exponential_values(n, rng):
    return rng.exponential(1.0, n)


def y_series(n, rng):
    e = rng.standard_normal(n + 1)
    return e[1:] ** 2 + e[:-1] ** 2


K4_BLOCKS = 33
K4_LEN = K4_BLOCKS * (4096 + 128)


def k4_stream(kind, seed_idx, role):
    """K4 instruments: 'A' shots, 'B' shots at twice the rate on 1/f noise, half rate, flipped, 'C' time reverse of a fresh
    A, 'S' and 'Sr' the sawtooth and its time reverse (blind spot). role 'fit' or 'verdict': independent streams made
    with different seed purposes."""
    n = K4_LEN
    rng = seeds.rng_for("K4:" + kind, role, "native", seed_idx, "data", 0)
    if kind == "A":
        return shots_ar(n, rng)
    if kind == "B":
        return shots_B(n, rng)
    if kind == "C":
        return shots_ar(n, rng)[::-1].copy()
    if kind == "S":
        return sawtooth(n, rng, SAW_SD)
    if kind == "Sr":
        return sawtooth(n, rng, SAW_SD)[::-1].copy()
    raise ValueError("unknown K4 kind " + kind)


K5_N = 2 ** 19
K5_CASES = ("expo", "cascade", "cascade_shuffled", "y", "yprime", "cascade_iaaft")
YPRIME_C = 0.9859   # B9: the coefficient at which the population mid-rank autocorrelation of g^2 first falls below 1/2 at lag 16


def k5_series(case, seed_idx, role):
    """K5 draws (Amendment 2, B9) use the seed-rule instrument tag `K5b:<case>`, split `fit` or `verdict`, net `native`,
    segment the seed number, purpose `data`. cascade_iaaft is an IAAFT surrogate of the whole cascade fit series, started from
    the generator of `K5b:cascade_iaaft` (split fit, purpose `whole-surrogate`); it exists as a fit series only."""
    if case == "cascade_iaaft":
        if role != "fit":
            raise ValueError("cascade_iaaft exists as a fit series only")
        import iaaft
        src = k5_series("cascade", seed_idx, "fit")
        Y, _, _ = iaaft.iaaft_surrogates(src, 1, seeds.rng_for("K5b:cascade_iaaft", "fit", "native", seed_idx, "whole-surrogate", 0))
        return Y[0]
    rng = seeds.rng_for("K5b:" + case, role, "native", seed_idx, "data", 0)
    if case == "expo":
        return exponential_values(K5_N, rng)
    if case == "cascade":
        return cascade(K5_N, rng)
    if case == "cascade_shuffled":
        return rng.permutation(cascade(K5_N, rng))
    if case == "y":
        return y_series(K5_N, rng)
    if case == "yprime":
        return ar1(YPRIME_C, K5_N, rng, True) ** 2
    raise ValueError("unknown K5 case " + case)
