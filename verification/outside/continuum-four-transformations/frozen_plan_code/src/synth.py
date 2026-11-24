"""Synthetic series for the known-answer tests. Free parameters the plan leaves open are marked PROVISIONAL
and listed in AMENDMENTS_NEEDED.md (items A5 to A9)."""
import math
import numpy as np
import seeds


def standardise(x):
    x = np.asarray(x, dtype=np.float64)
    return (x - x.mean()) / x.std()


def white(n, rng):
    return rng.standard_normal(n)


def ar1(phi, n, rng):
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0] / math.sqrt(1.0 - phi * phi)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return x


def powerlaw(beta, n, rng):
    """Fourier synthesis, power proportional to f^-beta, random phases, unit standard deviation."""
    m = n // 2 + 1
    amp = np.zeros(m)
    amp[1:] = np.arange(1, m, dtype=np.float64) ** (-beta / 2.0)
    spec = amp * (rng.standard_normal(m) + 1j * rng.standard_normal(m))
    spec[0] = 0.0
    return standardise(np.fft.irfft(spec, n=n))


SINE_FREQS = (0.0137, 0.0781, 0.2113)  # PROVISIONAL (A5): cycles per sample, unit amplitude, unit-variance white noise


def sines(n, rng):
    t = np.arange(n, dtype=np.float64)
    x = rng.standard_normal(n)
    for f in SINE_FREQS:
        x = x + np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi))
    return x


K2_BASES = ("white", "ar1_0.5", "ar1_0.9", "ar1_0.99", "pl_1", "pl_2", "sines3")
K2_MAPS = ("id", "exp", "cube")


def k2_class_names():
    return [b + ("" if m == "id" else "|" + m) for b in K2_BASES for m in K2_MAPS]


def k2_series(cls, idx, n=4096):
    base, _, m = cls.partition("|")
    rng = seeds.rng_for("K2:" + cls, "synthetic", "native", idx, "data", 0)
    if base == "white":
        x = white(n, rng)
    elif base.startswith("ar1_"):
        x = ar1(float(base[4:]), n, rng)
    elif base.startswith("pl_"):
        x = powerlaw(float(base[3:]), n, rng)
    elif base == "sines3":
        x = sines(n, rng)
    else:
        raise ValueError("unknown class " + cls)
    if m == "exp":
        x = np.exp(standardise(x))
    elif m == "cube":
        x = standardise(x) ** 3
    return x


SHOT_RATE = 0.01
SHOT_DECAY = 10.0
SHOT_HEIGHT_SD = 3.0
SHOT_KERNEL_LEN = 100  # PROVISIONAL (A6): kernel cut at 10 decay times


def shots_on(bg, bg_sd, rng, n):
    """Exponential shots: instant rise, decay over 10 samples, rate 0.01 per sample, height 3 background sd."""
    pre = SHOT_KERNEL_LEN
    ev = (rng.random(n + pre) < SHOT_RATE).astype(np.float64)
    kern = SHOT_HEIGHT_SD * bg_sd * np.exp(-np.arange(SHOT_KERNEL_LEN) / SHOT_DECAY)
    sh = np.convolve(ev, kern)[pre:pre + n]
    return bg + sh


def shots_ar(n, rng, phi=0.9):
    return shots_on(ar1(phi, n, rng), 1.0 / math.sqrt(1.0 - phi * phi), rng, n)


def shots_B(n, rng):
    """K4 instrument B: shots in power-law (slope 1) background, sampled at half the rate (every second
    sample of a series twice as long), polarity flipped. PROVISIONAL reading (A7)."""
    fine = shots_on(powerlaw(1.0, 2 * n, rng), 1.0, rng, 2 * n)
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


def sawtooth(n, rng):
    """Period 64, peak-to-peak amplitude 1, white noise with standard deviation 0.5 (PROVISIONAL reading of 'half its amplitude', A8)."""
    ph = int(rng.integers(0, 64))
    t = np.arange(n)
    return ((t + ph) % 64) / 64.0 + 0.5 * rng.standard_normal(n)


K3_CASES = ("shots", "logistic", "sawtooth")


def k3_series(case, idx, n=4096):
    rng = seeds.rng_for("K3:" + case, "synthetic", "native", idx, "data", 0)
    if case == "shots":
        return shots_ar(n, rng)
    if case == "logistic":
        return logistic(n, rng)
    if case == "sawtooth":
        return sawtooth(n, rng)
    raise ValueError("unknown case " + case)


CASCADE_SIGMA = 0.5  # PROVISIONAL (A9): dyadic cascade, log-normal weights with mean 1


def cascade(n, rng, sigma=CASCADE_SIGMA):
    depth = int(math.ceil(math.log2(n)))
    x = np.ones(1)
    for lev in range(depth):
        w = np.exp(sigma * rng.standard_normal(2 ** (lev + 1)) - sigma * sigma / 2.0)
        x = np.repeat(x, 2) * w
    return x[:n]
