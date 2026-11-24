"""Row 8 objects: the 4-point dyadic log-convexity problem of AUDIT-010 Theorem B, in exact log2 units.

A box is integer exponent vectors L <= U (the multiplicative box is [2^L_k, 2^U_k]).
Feasible means: some h with L <= h <= U and (D h)_j >= 0, D = [[1,-2,1,0],[0,1,-2,1]].
"""
import itertools
import random
from fractions import Fraction

from tlib import ZERO, ONE, require, solve_exact

D = [[1, -2, 1, 0], [0, 1, -2, 1]]
RAYS = [(1, 0), (0, 1), (2, 1), (1, 2)]


def dual_vec(r):
    return [sum(r[j] * D[j][k] for j in range(2)) for k in range(4)]


def sigma(r, L, U):
    """support function of the box in direction v = D^T r (exact integer)."""
    v = dual_vec(r)
    return sum((v[k] * U[k] if v[k] > 0 else v[k] * L[k]) for k in range(4))


def ledger_feasible(L, U, rays=RAYS):
    """the ledger's rule: every ray inequality sigma(r) >= 0 (multiplicative lhs >= rhs)."""
    return all(sigma(r, L, U) >= 0 for r in rays)


def ledger_G(d, L, U, rays=RAYS):
    """the ledger-derived reduced object: max over rays of (r.d - sigma(r)) / (r0 + r1)."""
    best = None
    for r in rays:
        val = Fraction(r[0] * d[0] + r[1] * d[1] - sigma(r, L, U), r[0] + r[1])
        if best is None or val > best:
            best = val
    return best


def lp_margin(d, L, U):
    """g(d) = min over h in the box of max_j (d_j - (D h)_j), by exact vertex enumeration of
    {min t : t >= d_j - D_j h, L <= h <= U}.  Independent of the ray formula."""
    rows = []
    for j in range(2):
        rows.append(([-D[j][k] for k in range(4)] + [-1], -Fraction(d[j])))
    for k in range(4):
        e = [0, 0, 0, 0, 0]
        e[k] = 1
        rows.append((e, Fraction(U[k])))
        e2 = [0, 0, 0, 0, 0]
        e2[k] = -1
        rows.append((e2, -Fraction(L[k])))
    best = None
    arg = None
    for S in itertools.combinations(range(len(rows)), 5):
        z = solve_exact([rows[i][0] for i in S], [rows[i][1] for i in S])
        if z is None:
            continue
        ok = True
        for a, b in rows:
            if sum((a[k] * z[k] for k in range(5)), ZERO) > b:
                ok = False
                break
        if ok and (best is None or z[4] < best):
            best = z[4]
            arg = z[:4]
    require(best is not None, "LP has no vertex")
    return best, arg


def gen_boxes(n_cases, seed):
    """same generator as the ledger's verifier (random.Random(seed): randint(-6,6) then randint(0,4))."""
    rng = random.Random(seed)
    out = []
    for _ in range(n_cases):
        L = [rng.randint(-6, 6) for _ in range(4)]
        U = [L[k] + rng.randint(0, 4) for k in range(4)]
        out.append((L, U))
    return out
