"""PREREG-03: end-matching offset choice under strictly increasing maps and polarity flip. Exact."""
from fractions import Fraction as F
import sys

out = []
w = out.append


def cost(seg):
    """PREREG.md section 7: squared jump between first and last value plus squared jump between first and last slope."""
    return (seg[-1] - seg[0]) ** 2 + ((seg[1] - seg[0]) - (seg[-1] - seg[-2])) ** 2


def best(block, n):
    costs = [cost(block[o:o + n]) for o in range(len(block) - n + 1)]
    m = min(costs)
    return costs, [o for o, c in enumerate(costs) if c == m]


def midranks(block):
    """Exact mid-ranks (ties share the mean rank), as Fractions."""
    order = sorted(range(len(block)), key=lambda i: block[i])
    r = [F(0)] * len(block)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and block[order[j + 1]] == block[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = F(i + j, 2)
        i = j + 1
    return r


block = [10, 10, 0, 1, 11, 11, 2, 2]
n = 6
maps = {
    "identity": lambda v: v,
    "x^3 + x": lambda v: v ** 3 + v,
    "polarity -x": lambda v: -v,
    "2^x": lambda v: F(2) ** v,
}
w(f"block {block}, segment length {n}, offsets 0..{len(block) - n}")
for name, g in maps.items():
    mb = [g(F(v)) for v in block]
    c, o = best(mb, n)
    w(f"raw-value cost, map {name}: costs {[str(v) for v in c]} -> chosen offset(s) {o}")
for name, g in maps.items():
    mb = [g(F(v)) for v in block]
    c, o = best(midranks(mb), n)
    w(f"mid-rank cost, map {name}: costs {[str(v) for v in c]} -> chosen offset(s) {o}")
w("Note: mid-ranks are computed once on the whole block, then the cost is taken on each candidate segment.")
sys.stdout.write("\n".join(out) + "\n")
