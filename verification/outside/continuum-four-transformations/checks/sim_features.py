"""Sampled check on synthetic series only (no real data read).

Part 1: order-3 features of the K3 shot process. Part 2: share of tied order-3 windows at lag 1 after
8-bit quantization. Every series, length, start state, bin rule and seed is stated in the output.
"""
import sys
import numpy as np
from scipy.signal import lfilter

SEED = 20261122
N_SEG = 4096
out = []
w = out.append


def ar1(rng, n, phi):
    """x[0] drawn from the stationary law N(0, 1/(1-phi^2)); x[t] = phi x[t-1] + e[t], e ~ N(0, 1)."""
    e = rng.standard_normal(n)
    e[0] = e[0] / np.sqrt(1.0 - phi * phi)
    return lfilter([1.0], [1.0, -phi], e)


def shots(rng, n, rate=0.01, decay=10.0, height=3.0, phi=0.9):
    """K3 shots: AR(1) background scaled to unit SD, plus height * sum of instant-rise, exp-decay pulses."""
    bg = ar1(rng, n, phi)
    bg = bg / bg.std()
    kern = np.exp(-np.arange(int(10 * decay)) / decay)
    s = (rng.random(n) < rate).astype(float)
    return bg + height * np.convolve(s, kern)[:n]


CODES = {"012": 5, "021": 7, "102": 11, "120": 15, "201": 19, "210": 21}


def counts(x, tau):
    n = len(x) - 2 * tau
    a, b, c = x[:n], x[tau:tau + n], x[2 * tau:2 * tau + n]
    tie = (a == b) | (b == c) | (a == c)
    st = np.stack([a, b, c], axis=1)[~tie]
    r = np.argsort(np.argsort(st, axis=1, kind="stable"), axis=1, kind="stable")
    key = r[:, 0] * 9 + r[:, 1] * 3 + r[:, 2]
    return {k: int(np.sum(key == v)) for k, v in CODES.items()}, int(tie.sum()), n


def feats(cn):
    g = lambda k: cn[k] + 0.5
    a1 = np.log(g("012") / g("210"))
    a2 = np.log(g("021") / g("120"))
    a3 = np.log(g("102") / g("201"))
    return a1, a2 + a3, a2 - a3


LAGS = (1, 2, 4, 8, 16)
w("== Part 1. K3 shot process (rate 0.01, decay 10 samples, height 3, AR(1) 0.9 background) ==")
x = shots(np.random.default_rng(SEED), 2 ** 20)
w(f"one series of 2^20 samples, seed {SEED}:")
for label, y in (("A", x), ("C = A reversed", x[::-1]), ("-A", -x), ("-C", -x[::-1])):
    w("  " + label + ": " + "; ".join(
        "tau=%d a1=%+.4f s=%+.4f u=%+.4f" % ((t,) + tuple(feats(counts(y, t)[0]))) for t in LAGS))
n_rep = 200
w(f"u over {n_rep} independent segments of {N_SEG} samples, segment i uses seed {SEED} + 1 + i:")
us = {t: [] for t in LAGS}
for i in range(n_rep):
    y = shots(np.random.default_rng(SEED + 1 + i), N_SEG)
    for t in LAGS:
        us[t].append(feats(counts(y, t)[0])[2])
for t in LAGS:
    u = np.array(us[t])
    m, sd = u.mean(), u.std(ddof=1)
    w(f"  tau={t}: mean {m:+.4f}, per-segment SD {sd:.4f}, mean/SD {m / sd:+.2f}, "
      f"standard error {sd / np.sqrt(n_rep):.4f}, mean/SE {m / (sd / np.sqrt(n_rep)):+.1f}")

w("")
w("== Part 2. Tied order-3 windows at lag 1 after 8-bit quantization ==")
w(f"{n_rep} series per case, length {N_SEG}. AR(1) start state from its stationary law, innovations N(0, 1).")
w("Uniform bins: 256 equal-width bins over the series' own 0.1 to 99.9 percent quantile range, floor, then clipped to 0..255.")
w("Equal-count bins: floor(256 * (r - 1/2) / n) with r the 1-based rank (no ties in the unquantized series).")
w("Case k, series i uses seed 20261124 + 1000 k + i.")
cases = [("AR(1) 0.9", 0.9, False), ("AR(1) 0.99", 0.99, False), ("AR(1) 0.999", 0.999, False),
         ("AR(1) 0.9999", 0.9999, False), ("exp(3 z), z = AR(1) 0.9 scaled to unit SD", 0.9, True)]
for k, (label, phi, heavy) in enumerate(cases):
    fu, fq = [], []
    for i in range(n_rep):
        y = ar1(np.random.default_rng(20261124 + 1000 * k + i), N_SEG, phi)
        if heavy:
            y = np.exp(3.0 * y / y.std())
        lo, hi = np.quantile(y, [0.001, 0.999])
        qu = np.clip(np.floor((y - lo) / (hi - lo) * 256), 0, 255)
        r = np.argsort(np.argsort(y, kind="stable"), kind="stable") + 1
        qq = np.floor(256 * (r - 0.5) / len(y))
        fu.append(counts(qu, 1)[1] / (N_SEG - 2))
        fq.append(counts(qq, 1)[1] / (N_SEG - 2))
    fu, fq = np.array(fu), np.array(fq)
    w(f"  {label}: uniform bins mean {fu.mean():.3f} (SD {fu.std(ddof=1):.3f}); "
      f"equal-count bins mean {fq.mean():.3f} (SD {fq.std(ddof=1):.3f})")
sys.stdout.write("\n".join(out) + "\n")
