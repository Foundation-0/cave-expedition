"""Second implementation of the pattern count. Shares no code with patterns.py: plain Python, the pattern of a window is the
string of dense ranks (the number of distinct window values below each value)."""


def pattern_counts(values, d, tau, step=1):
    """values: list of floats. Returns ({pattern string: count}, window count). Tied windows are patterns of their own."""
    n = len(values)
    out = {}
    nwin = 0
    t = 0
    while t + (d - 1) * tau <= n - 1:
        w = [values[t + k * tau] for k in range(d)]
        nwin += 1
        s = "".join(str(len(set(b for b in w if b < a))) for a in w)
        out[s] = out.get(s, 0) + 1
        t += step
    return out, nwin
