"""Exact check that R_opt is sharp: explicit matrices of rank exactly max(1, ceil R_opt).

Audit: AUDIT-002. Backs, in VERDICTS.md: "Sharpness of R_opt (002): explicit matrices of rank
exactly max(1, ceil R_opt) built for 1,102 parameter sets in exact arithmetic".

Claim (THEOREMS.md A1.3 of Foundation-0/spectral-inertia): for every feasible (u, t, S, b) with
u > 0, the smallest possible rank of P is max(1, ceil R_opt(u, t, S, b)), matrix size free.
The lower side (rank P >= n+(H_perp) >= R_opt) is sampled in check_rank_envelope_and_moments.py.
This script checks the upper side. For each tuple it builds a diagonal P and Q of rank exactly r,
in exact arithmetic over Q(sqrt d) with SymPy, and verifies trace, trace of Q, Frobenius norm,
PSD, rank and the bound on positive eigenvalues of Q exactly. Boundary tuples are included.
It does not need any other repository.

Needs: Python 3 with SymPy.
Run (about 8 seconds for the default size, about 15 seconds for 800 777):
    python3 -I -B check_sharpness.py [n_random] [seed]
Defaults: n_random 400, seed 20261121 (552 tuples). "800 777" gives 1,102 tuples. The number of
tuples is printed.
Exit code 0 only if every tuple was realised exactly.
"""
import json
import math
import random
import sys
from fractions import Fraction as Fr

import sympy as sp

N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20261121
print("seed:", SEED, "n_random:", N)


def R(u, t, S, b):
    if u <= 0 or u + t <= 0:
        return Fr(0)
    if b > 0 and t > 0 and t * (u + t) >= b * S:
        return u * u / (S - t * t / b)
    return max(Fr(0), (u + t) ** 2 / S - b)


def Q_(x):
    return sp.Rational(x.numerator, x.denominator)


def smaller_root(a2, a1, a0):
    """smaller root of a2 y^2 + a1 y + a0 = 0 (a2 > 0)."""
    return (-a1 - sp.sqrt(a1 * a1 - 4 * a2 * a0)) / (2 * a2)


def larger_root(a2, a1, a0):
    return (-a1 + sp.sqrt(a1 * a1 - 4 * a2 * a0)) / (2 * a2)


def construct(u, t, S, b):
    """Return (P_diag, Q_diag) sympy lists, rank P == r."""
    r = max(1, math.ceil(R(u, t, S, b)))
    U, T, SS = Q_(u), Q_(t), Q_(S)
    if u + t <= 0:
        A = -(U + T)
        if SS <= A * A:
            if A == 0:
                return [U], [-U], r, "u+t=0,S=0"
            k = math.ceil(Fr(A.p, A.q) ** 2 / S)
            if k == 1:
                ns = [A]
            else:
                y = smaller_root(sp.Integer(k * (k - 1)), -2 * A * (k - 1), A * A - SS)
                ns = [y] * (k - 1) + [A - (k - 1) * y]
            return [U] + [0] * len(ns), [-U] + [-x for x in ns], r, "u+t<0,small S"
        if SS <= U * U + T * T:
            a = ((U - T) - sp.sqrt(2 * SS - (U + T) ** 2)) / 2
            return [U, 0], [-a, T + a], r, "u+t<=0,mid S"
        # b >= 1 needed
        x = sp.sqrt((SS - U * U - T * T) / 2)
        return [U, 0, 0, 0], [0, T, x, -x], r, "u+t<=0,large S"
    if b == 0:
        P = [U / r] * r
        if T == 0:
            S1 = U * U / r
        else:
            S1 = U * U / r + T * T
        if T != 0 and SS <= S1:
            # N on the r coords: -T(1-th)/r each, new coord N = -T th
            a2 = T * T / r + T * T
            a1 = -2 * (U + T) * T / r
            a0 = (U + T) ** 2 / r - SS
            th = larger_root(a2, a1, a0)
            return P + [0], [T * (1 - th) / r] * r + [T * th], r, "b=0,theta path"
        # P shaping with N (if any) on a separate coordinate
        target = SS - T * T
        if r == 1:
            ps = [U]
        else:
            y = smaller_root(sp.Integer(r * (r - 1)), -2 * U * (r - 1), U * U - target)
            ps = [y] * (r - 1) + [U - (r - 1) * y]
        return ps + [0], [0] * r + [T], r, "b=0,P shaping"
    caseB = t > 0 and r * t > b * u
    if caseB:
        q0 = T / b
        P = [0] * b + [U / r] * r
        Qd = [q0] * b + [0] * r
        tag = "caseB"
    else:
        h = (U + T) / (r + b)
        q0 = h
        P = [0] * b + [U / r] * r
        Qd = [h] * b + [-(b * h - T) / r] * r
        tag = "caseA"
    S0 = sum((p + q) ** 2 for p, q in zip(P, Qd))
    dS = SS - S0
    if dS == 0:
        return P, Qd, r, tag + ",min S"
    x = (-q0 + sp.sqrt(q0 * q0 + 2 * dS)) / 2
    Qd = [Qd[0] + x] + Qd[1:] + [-x]
    return P + [0], Qd, r, tag + ",x path"


def verify(u, t, S, b, P, Qd, r):
    P = [sp.nsimplify(p) if not isinstance(p, sp.Basic) else p for p in P]
    Qd = [sp.nsimplify(q) if not isinstance(q, sp.Basic) else q for q in Qd]
    ok = True
    why = []
    if not all(sp.simplify(p).is_nonnegative for p in P):
        ok = False; why.append("P not PSD")
    rk = sum(1 for p in P if not sp.simplify(p).is_zero)
    if rk != r:
        ok = False; why.append("rank %d != %d" % (rk, r))
    npos = sum(1 for q in Qd if sp.simplify(q).is_positive)
    if npos > b:
        ok = False; why.append("n_+(Q)=%d > b" % npos)
    for name, val, want in (("u", sum(P), Q_(u)), ("t", sum(Qd), Q_(t)),
                            ("S", sum((p + q) ** 2 for p, q in zip(P, Qd)), Q_(S))):
        d = sp.simplify(sp.expand(val - want))
        if not (d == 0 or d.equals(0)):
            ok = False; why.append("%s mismatch %s" % (name, d))
    return ok, why


def feasible_S(rng, u, t, b):
    """Random S in the feasible set for (u, t, b), dimension free."""
    if b == 0:
        top = u * u + t * t
        return top * Fr(rng.randint(1, 1000), 1000)
    lo = t * t / b if (t > 0 and u + t > 0) else Fr(0)
    return lo + Fr(rng.randint(1, 4000), rng.randint(1, 60))


def main():
    rng = random.Random(SEED)
    cases = []
    for _ in range(N):
        u = Fr(rng.randint(1, 30), rng.randint(1, 6))
        b = rng.choice([0, 0, 1, 1, 2, 3, 5])
        if b == 0:
            t = -Fr(rng.randint(0, 30), rng.randint(1, 6))
        else:
            t = Fr(rng.randint(-30, 30), rng.randint(1, 6))
        cases.append((u, t, feasible_S(rng, u, t, b), b))
    # boundary tuples: exactly the minimal S for a rank r, the b=0 maximum, the regime boundary
    for _ in range(N // 4):
        u = Fr(rng.randint(1, 30), rng.randint(1, 6))
        b = rng.choice([0, 1, 2, 3])
        t = -Fr(rng.randint(0, 20), rng.randint(1, 4)) if b == 0 else Fr(rng.randint(-20, 30), rng.randint(1, 4))
        r = rng.randint(1, 7)
        if u + t > 0:
            if b > 0 and t > 0 and r * t > b * u:
                cases.append((u, t, t * t / b + u * u / r, b))
            else:
                cases.append((u, t, (u + t) ** 2 / (r + b), b))
            if b > 0 and t > 0:
                cases.append((u, t, t * (u + t) / b, b))  # regime boundary t(u+t) = bS
        if b == 0:
            cases.append((u, t, u * u + t * t, b))
    cases.append((Fr(3), Fr(-3), Fr(0), 0))
    cases.append((Fr(3), Fr(-3), Fr(0), 2))
    stats = {"tuples": 0, "ok": 0, "fail": 0, "by_tag": {}, "max_r": 0, "fails": []}
    for (u, t, S, b) in cases:
        P, Qd, r, tag = construct(u, t, S, b)
        ok, why = verify(u, t, S, b, P, Qd, r)
        stats["tuples"] += 1
        stats["by_tag"][tag] = stats["by_tag"].get(tag, 0) + 1
        stats["max_r"] = max(stats["max_r"], r)
        # lower side sanity: R_opt > r - 1 exactly (so rank r - 1 is excluded by the theorem)
        if not (r == 1 or R(u, t, S, b) > r - 1):
            ok = False; why.append("ceil logic")
        if ok:
            stats["ok"] += 1
        else:
            stats["fail"] += 1
            if len(stats["fails"]) < 5:
                stats["fails"].append([str(u), str(t), str(S), b, r, tag, why])
    print(json.dumps(stats, indent=1))
    ok = stats["fail"] == 0
    print("RESULT check_sharpness: %s tuples=%d realised_exactly=%d failures=%d max_rank=%d"
          % ("PASS" if ok else "FAIL", stats["tuples"], stats["ok"], stats["fail"], stats["max_r"]))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
