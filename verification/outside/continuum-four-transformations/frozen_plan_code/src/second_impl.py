"""Second implementation of the pattern count. Shares no code with patterns.py:
plain Python, rank of each value = number of window values below it."""


def pattern_counts(values, d, tau, step=1):
    """values: list of floats. Returns ({pattern string: count}, tied window count, window count)."""
    n = len(values)
    out = {}
    ties = 0
    nwin = 0
    t = 0
    while t + (d - 1) * tau <= n - 1:
        w = [values[t + k * tau] for k in range(d)]
        nwin += 1
        if len(set(w)) < d:
            ties += 1
        else:
            s = "".join(str(sum(1 for b in w if b < a)) for a in w)
            out[s] = out.get(s, 0) + 1
        t += step
    return out, ties, nwin
