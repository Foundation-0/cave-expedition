"""SK8: how often does the old exp map lose values on the K5 cascade? 200 fresh seeds. numpy, standard library."""
import hashlib, math, sys
import numpy as np
def rng(i):
    h = int(hashlib.sha256(f"A3verify|rate|{i}".encode()).hexdigest()[:16], 16)
    return np.random.default_rng(h)
def cascade(rg):
    a = np.array([1.0])
    for j in range(19):
        a = np.repeat(a, 2) * np.exp(0.5 * rg.standard_normal(2 ** (j + 1)) - 0.125)
    return a
N = 200
lose = over_z = domin = lose_c = 0
zmaxes = []
for i in range(N):
    x = cascade(rng(i))
    z = (x - x.mean()) / x.std()
    zmaxes.append(float(z.max()))
    with np.errstate(over="ignore"):
        m = np.exp(z)
    if not np.isfinite(m).all() or len(np.unique(m)) < len(np.unique(x)):
        lose += 1
    with np.errstate(all="ignore"):
        z2 = (m - m.mean()) / m.std() if np.isfinite(m).all() else None
        if z2 is not None:
            e2 = np.exp(z2)
            if not np.isfinite(e2).all():
                over_z += 1
    cen = np.exp(z - (z.max() + z.min()) / 2.0)
    if len(np.unique(cen)) < len(np.unique(x)):
        lose_c += 1
zs = np.array(zmaxes)
print(f"{N} cascades (seeds sha256 'A3verify|rate|i'): exp-mapped cascade (exp of the standardised cascade) lost distinct values or overflowed in {lose} ({lose/N:.3f}); "
      f"exp(z) overflowed or merged where max z above 709.78: {(zs > 709.78).sum()}; max z quantiles 5/50/95%: {np.percentile(zs,5):.0f}/{np.percentile(zs,50):.0f}/{np.percentile(zs,95):.0f}, largest {zs.max():.0f}")
print(f"exp of the re-standardised exp-mapped cascade overflowed in {over_z} of {N} ({over_z/N:.3f})")
print(f"centred form exp(z - (max z + min z)/2) lost distinct values in {lose_c} of {N} ({lose_c/N:.3f})")
# Wilson interval for the author's 2 of 10 against mine
k = lose_c; p = k / N; z = 1.96
c = (p + z*z/(2*N)) / (1 + z*z/N); h = z * math.sqrt(p*(1-p)/N + z*z/(4*N*N)) / (1 + z*z/N)
print(f"rate of the loss in the centred form {p:.3f}, 95% Wilson interval {max(0,c-h):.3f} to {c+h:.3f}; the author's 2 of 10 is {'inside' if (max(0,c-h)) <= 0.2 <= c+h else 'outside'} it")
