"""Sampled check (synthetic only, seeded): is the surrogate test itself unchanged by amplitude maps?
Pattern counts of the real series are unchanged by any strictly increasing map, but IAAFT surrogates
are built from amplitudes, so the surrogate pool, and hence the p-value, can change."""
import sys
import numpy as np

SEED = 20261123
out = []
w = out.append


def iaaft(x, rng, iters=200):
    amp = np.abs(np.fft.rfft(x))
    sorted_x = np.sort(x)
    s = rng.permutation(x)
    for _ in range(iters):
        ph = np.angle(np.fft.rfft(s))
        s = np.fft.irfft(amp * np.exp(1j * ph), n=len(x))
        s = sorted_x[np.argsort(np.argsort(s, kind="stable"), kind="stable")]
    return s


def sigma_hat(x, tau=1):
    n = len(x) - 2 * tau
    a, b, c = x[:n], x[tau:tau + n], x[2 * tau:2 * tau + n]
    st = np.stack([a, b, c], axis=1)
    r = np.argsort(np.argsort(st, axis=1, kind="stable"), axis=1, kind="stable")
    key = r[:, 0] * 9 + r[:, 1] * 3 + r[:, 2]
    codes = {"012": 5, "021": 7, "102": 11, "120": 15, "201": 19, "210": 21}
    cnt = {k: float(np.sum(key == v)) + 0.5 for k, v in codes.items()}
    tot = sum(cnt.values())
    pairs = [("012", "210"), ("021", "120"), ("102", "201")]
    val = 0.0
    for p, q in pairs:
        for i, j in ((p, q), (q, p)):
            val += cnt[i] / tot * np.log(cnt[i] / cnt[j])
    return val


def seg_p(x, seed, m=99):
    rng = np.random.default_rng(seed)
    real = sigma_hat(x)
    sur = np.array([sigma_hat(iaaft(x, rng)) for _ in range(m)])
    return (1 + int(np.sum(sur >= real))) / (m + 1), real, sur


rng = np.random.default_rng(SEED)
n = 1024
bg = np.zeros(n)
e = rng.standard_normal(n)
for t in range(1, n):
    bg[t] = 0.9 * bg[t - 1] + e[t]
k = np.exp(-np.arange(100) / 10.0)
x = bg / bg.std() + 3 * np.convolve((rng.random(n) < 0.01).astype(float), k)[:n]
z = (x - x.mean()) / x.std()
variants = {"x": z, "-x": -z, "exp(x)": np.exp(z), "x^3": z ** 3}
w(f"one synthetic shot segment, n={n}, 99 surrogates, same surrogate seed for every variant")
res = {}
for name, y in variants.items():
    p, real, sur = seg_p(y, SEED + 1)
    res[name] = (p, real, sur)
    w(f"{name}: real Sigma_hat {real:.6f}, surrogate mean {sur.mean():.6f}, segment p {p:.2f}")
w(f"real Sigma_hat identical across maps: {len({round(v[1], 12) for v in res.values()}) == 1}")
w(f"surrogate pool for -x equals that for x: {bool(np.allclose(res['x'][2], res['-x'][2], rtol=0, atol=1e-12))}")
w(f"surrogate pool for exp(x) equals that for x: {bool(np.allclose(res['x'][2], res['exp(x)'][2], rtol=0, atol=1e-12))}")
sys.stdout.write("\n".join(out) + "\n")
