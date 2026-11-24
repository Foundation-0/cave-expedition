#!/usr/bin/env python3
"""Advocate recheck of AUDIT-010 exact claims: Theorem A, Theorem B and the README witnesses.

Checks: with oracles written here (not taken from the sibling team), that
  A: the interval all-pairs test equals a simple-temporal-problem solution on a chain (Bellman-Ford in exact
     rationals on log data, with a witness built and verified) and a general-rational forward-propagation oracle;
     step-only checks can pass while the global test fails; the smallest example (x = 1, 2, 4, bracket [1,1],
     boxes [1,1], [3/2,5/2], [9/2,5]) gives steps pass, pairs fail;
  B: the four-ray test equals the lower convex hull oracle and the C(m,3) chord-triple test (m = 4), the four
     rays are the four chord triples, every chord triple is needed for m = 5, 6, 7, applying the four-ray test to
     sliding windows misdecides some boxes for m >= 5, and the README witness inequalities reject the feasible convex
     point y = (1, 1, 1, 1024) while the note's rays accept it.
Backs: VERDICTS.md section 1 (No-log theorems A, B, C), section 2 (label N0: Dechter, Meiri and Pearl 1991 for A;
Baron, Matkowski and Nikodem 1994 for B, statement read as quoted in arXiv 2009.13400) and section 3 (README witness
row). Rulings F1, F2, F3 in RECHECK-1.json.
Needs: Python 3 standard library only, and a clone of Foundation-0/fractals at draft PR 60. Give its location as the
first argument or in FRACTALS_REPO.
Run: python3 -I -B check_exact_advocate.py /path/to/fractals     (add --details to print the full JSON)
Time: about 2 seconds. Fixed seed: 4242 (printed). Exit 0 only if every check held.
"""
import importlib.util
import itertools
import json
import os
import random
import sys
from fractions import Fraction as Fr

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
    return cond


def load_team():
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.environ.get("FRACTALS_REPO")
    if not root:
        raise SystemExit("usage: check_exact_advocate.py <path to a clone of Foundation-0/fractals at PR 60> "
                         "(or set FRACTALS_REPO)")
    path = os.path.join(root, "studies", "expedition-mult-farkas-dsi", "verify_mult_farkas_dsi.py")
    if not os.path.isfile(path):
        raise SystemExit(f"missing {path}: is the clone at draft PR 60?")
    spec = importlib.util.spec_from_file_location("team_verifier", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------- Theorem A oracles ----------------
def stp_feasible_log(a, l, u, alo, ahi):
    """STP on log2 values. Nodes 0 (origin) and 1..n for h_i. Edge i->j weight w means X_j - X_i <= w.
    Bellman-Ford from origin in exact rationals; returns (feasible, witness h or None)."""
    n = len(a)
    edges = []
    for i in range(n):
        edges.append((0, i + 1, Fr(u[i])))      # h_i <= u_i
        edges.append((i + 1, 0, -Fr(l[i])))     # -h_i <= -l_i
    for i in range(n - 1):
        d = Fr(a[i + 1] - a[i])
        edges.append((i + 1, i + 2, ahi * d))   # h_{i+1} - h_i <= ahi d
        edges.append((i + 2, i + 1, -alo * d))  # h_i - h_{i+1} <= -alo d
    dist = [Fr(0)] + [None] * n
    for _ in range(n + 1):
        changed = False
        for s, t, w in edges:
            if dist[s] is not None and (dist[t] is None or dist[s] + w < dist[t]):
                dist[t] = dist[s] + w
                changed = True
        if not changed:
            break
    for s, t, w in edges:
        if dist[s] is not None and (dist[t] is None or dist[s] + w < dist[t]):
            return False, None
    h = dist[1:]
    return True, h


def witness_ok(a, l, u, alo, ahi, h):
    n = len(a)
    if any(not (l[i] <= h[i] <= u[i]) for i in range(n)):
        return False
    for i in range(n - 1):
        d = a[i + 1] - a[i]
        s = h[i + 1] - h[i]
        if not (alo * d <= s <= ahi * d):
            return False
    return True


def forward_feasible_mult(xs, lo, hi, alo, ahi):
    """General positive rationals. Raise every y to the common denominator q so slopes become integers,
    then propagate the feasible interval forward exactly. Returns (feasible, witness in y^q space)."""
    q = alo.denominator * ahi.denominator
    P1, P2 = int(alo * q), int(ahi * q)
    LO = [v ** q for v in lo]
    HI = [v ** q for v in hi]
    I = [(LO[0], HI[0])]
    for i in range(1, len(xs)):
        r = xs[i] / xs[i - 1]
        a0, b0 = I[-1]
        nlo, nhi = a0 * r ** P1, b0 * r ** P2
        c, d = max(nlo, LO[i]), min(nhi, HI[i])
        if c > d:
            return False, None
        I.append((c, d))
    # backward pass builds a witness z_i = y_i^q
    z = [None] * len(xs)
    z[-1] = I[-1][0]
    for i in range(len(xs) - 2, -1, -1):
        r = xs[i + 1] / xs[i]
        # need z_i with z_{i+1}/r^P2 <= z_i <= z_{i+1}/r^P1 and z_i in I[i]
        c = max(I[i][0], z[i + 1] / r ** P2)
        d = min(I[i][1], z[i + 1] / r ** P1)
        if c > d:
            return False, None
        z[i] = c
    for i in range(len(xs)):
        if not (LO[i] <= z[i] <= HI[i]):
            return False, None
    for i in range(len(xs) - 1):
        r = xs[i + 1] / xs[i]
        if not (z[i] * r ** P1 <= z[i + 1] <= z[i] * r ** P2):
            return False, None
    return True, z


def my_pairs_test(xs, lo, hi, alo, ahi, adjacent_only=False):
    """My own integer form of the all-pairs condition (cross-multiplied, no division)."""
    p1, q1, p2, q2 = alo.numerator, alo.denominator, ahi.numerator, ahi.denominator
    n = len(xs)

    def powfrac(f, e):
        return f ** e  # Fraction ** int is exact, including negative e
    for i in range(n):
        for j in range(i + 1, n):
            if adjacent_only and j != i + 1:
                continue
            rx = xs[j] / xs[i]
            if powfrac(hi[j] / lo[i], q1) < powfrac(rx, p1):
                return False
            if powfrac(lo[j] / hi[i], q2) > powfrac(rx, p2):
                return False
    return True


def theorem_a(team, rng, ncases):
    out = dict(stp_cases=0, stp_agree=0, stp_feasible=0, stp_local_yes_global_no=0, witness_ok=0,
               mult_cases=0, mult_agree=0, mult_local_yes_global_no=0, team_vs_mine_agree=0)
    for _ in range(ncases):
        n = rng.randint(2, 7)
        a = sorted(rng.sample(range(0, 20), n))
        l = [rng.randint(-12, 12) for _ in range(n)]
        u = [v + rng.randint(0, 6) for v in l]
        q = rng.choice([1, 2, 3, 4, 6])
        p1 = rng.randint(-3 * q, 3 * q)
        p2 = p1 + rng.randint(0, 2 * q)
        alo, ahi = Fr(p1, q), Fr(p2, q)
        feas, h = stp_feasible_log(a, l, u, alo, ahi)
        xs = [Fr(2) ** e for e in a]
        lo = [Fr(2) ** e for e in l]
        hi = [Fr(2) ** e for e in u]
        team_res = team.check_interval_scaling_global(xs, lo, hi, alo, ahi)
        out["stp_cases"] += 1
        out["stp_agree"] += check(team_res["global_ok"] == feas, f"STP mismatch a={a} l={l} u={u} {alo} {ahi}")
        if feas:
            out["stp_feasible"] += 1
            out["witness_ok"] += check(witness_ok(a, l, u, alo, ahi, h), "STP witness failed")
        if team_res["local_ok"] and not feas:
            out["stp_local_yes_global_no"] += 1
    for _ in range(ncases):
        n = rng.randint(2, 6)
        xs = [Fr(rng.randint(1, 9), rng.randint(1, 5))]
        for _ in range(n - 1):
            xs.append(xs[-1] * Fr(rng.randint(6, 30), 5))
        lo, hi = [], []
        for _ in range(n):
            v = Fr(rng.randint(1, 60), rng.randint(1, 12))
            lo.append(v)
            hi.append(v * Fr(rng.randint(10, 25), 10))
        q = rng.choice([1, 2, 3])
        p1 = rng.randint(-2 * q, 2 * q)
        p2 = p1 + rng.randint(0, q)
        alo, ahi = Fr(p1, q), Fr(p2, q)
        feas, _z = forward_feasible_mult(xs, lo, hi, alo, ahi)
        team_res = team.check_interval_scaling_global(xs, lo, hi, alo, ahi)
        mine = my_pairs_test(xs, lo, hi, alo, ahi)
        out["mult_cases"] += 1
        out["mult_agree"] += check(team_res["global_ok"] == feas == mine, f"mult mismatch {xs} {lo} {hi} {alo} {ahi}")
        out["team_vs_mine_agree"] += (team_res["global_ok"] == mine)
        if my_pairs_test(xs, lo, hi, alo, ahi, adjacent_only=True) and not feas:
            out["mult_local_yes_global_no"] += 1
    # evaluator's smallest example and team's toy example
    ex = dict(xs=[Fr(1), Fr(2), Fr(4)], lo=[Fr(1), Fr(3, 2), Fr(9, 2)], hi=[Fr(1), Fr(5, 2), Fr(5)])
    out["evaluator_minimal_example"] = dict(
        steps=my_pairs_test(ex["xs"], ex["lo"], ex["hi"], Fr(1), Fr(1), True),
        pairs=my_pairs_test(ex["xs"], ex["lo"], ex["hi"], Fr(1), Fr(1)),
        forward=forward_feasible_mult(ex["xs"], ex["lo"], ex["hi"], Fr(1), Fr(1))[0])
    return out


# ---------------- Theorem B oracles ----------------
def hull_feasible(L, U):
    """Equally spaced points k = 0..m-1, log values. Greatest convex minorant of the U points (lower hull),
    evaluated on the grid; a convex h with L <= h <= U exists iff hull >= L (the hull itself is a witness)."""
    m = len(U)
    pts = list(range(m))
    hull = []
    for k in pts:
        while len(hull) >= 2:
            i, j = hull[-2], hull[-1]
            # remove j if it lies on or above the segment i -> k
            if (U[j] - U[i]) * (k - i) >= (U[k] - U[i]) * (j - i):
                hull.pop()
            else:
                break
        hull.append(k)
    g = [None] * m
    for s in range(len(hull) - 1):
        i, k = hull[s], hull[s + 1]
        for j in range(i, k + 1):
            g[j] = U[i] + Fr(U[k] - U[i], 1) * Fr(j - i, k - i)
    ok = all(g[j] >= L[j] for j in range(m))
    return ok, g


def chord_triples_ok(L, U):
    m = len(U)
    bad = []
    for i, j, k in itertools.combinations(range(m), 3):
        # L_j <= ((k-j) U_i + (j-i) U_k)/(k-i)
        if (k - i) * L[j] > (k - j) * U[i] + (j - i) * U[k]:
            bad.append((i, j, k))
    return not bad, bad


def is_convex(g):
    return all(g[j - 1] - 2 * g[j] + g[j + 1] >= 0 for j in range(1, len(g) - 1))


def theorem_b(team, rng, ncases):
    out = {}
    agree4 = feasible4 = 0
    for _ in range(ncases):
        L = [rng.randint(-10, 10) for _ in range(4)]
        U = [v + rng.randint(0, 6) for v in L]
        ok, g = hull_feasible(L, U)
        if ok:
            check(is_convex(g) and all(L[k] <= g[k] <= U[k] for k in range(4)), "hull witness invalid")
        ct, _bad = chord_triples_ok(L, U)
        team_res = team.check_4pt_farkas_monotonicity([Fr(2) ** v for v in L], [Fr(2) ** v for v in U], "convex")
        agree4 += check(ok == ct == team_res["feasible"], f"B mismatch L={L} U={U}")
        feasible4 += ok
        # concave mode by sign flip: concave h in [L,U] <=> convex -h in [-U,-L]
        okc, _ = hull_feasible([-v for v in U], [-v for v in L])
        team_c = team.check_4pt_farkas_monotonicity([Fr(2) ** v for v in L], [Fr(2) ** v for v in U], "concave")
        check(okc == team_c["feasible"], f"B concave mismatch L={L} U={U}")
    out["m4"] = dict(cases=ncases, agree=agree4, feasible=feasible4)
    # team rays == chord triples for m = 4 (as integer vectors on log values)
    rays = {"(1,0)": (1, -2, 1, 0), "(0,1)": (0, 1, -2, 1), "(2,1)": (2, -3, 0, 1), "(1,2)": (1, 0, -3, 2)}
    tri = {}
    for i, j, k in itertools.combinations(range(4), 3):
        v = [0] * 4
        v[i] += k - j
        v[k] += j - i
        v[j] -= k - i
        tri[(i, j, k)] = tuple(v)
    out["m4_rays_equal_chord_triples"] = sorted(rays.values()) == sorted(tri.values())
    out["m4_triple_map"] = {str(t): [n for n, r in rays.items() if r == v] for t, v in tri.items()}
    # general m: chord triples vs hull, and irredundancy of every triple
    for m in (5, 6, 7):
        ag = 0
        for _ in range(ncases):
            L = [rng.randint(-10, 10) for _ in range(m)]
            U = [v + rng.randint(0, 6) for v in L]
            ag += check(hull_feasible(L, U)[0] == chord_triples_ok(L, U)[0], f"m={m} hull vs triples")
        irred = 0
        for i, j, k in itertools.combinations(range(m), 3):
            BIG = 10 ** 6
            U = [BIG] * m
            L = [-BIG] * m
            U[i] = 0
            U[k] = 0
            L[j] = 1
            ok, bad = chord_triples_ok(L, U)
            irred += (bad == [(i, j, k)]) and (hull_feasible(L, U)[0] is False)
        # does the team's 4-point ray family, applied to every 4-point window, decide m points?
        win_fail = 0
        example = None
        for _ in range(ncases):
            L = [rng.randint(-10, 10) for _ in range(m)]
            U = [v + rng.randint(0, 6) for v in L]
            wins = all(team.check_4pt_farkas_monotonicity([Fr(2) ** v for v in L[s:s + 4]], [Fr(2) ** v for v in U[s:s + 4]], "convex")["feasible"]
                       for s in range(m - 3))
            if wins != hull_feasible(L, U)[0]:
                win_fail += 1
                example = example or dict(L=L, U=U, bad=chord_triples_ok(L, U)[1])
        out[f"m{m}"] = dict(cases=ncases, hull_vs_triples_agree=ag, n_triples=len(list(itertools.combinations(range(m), 3))),
                            irredundant_triples=irred, sliding_4pt_windows_wrong=win_fail, sliding_example=example)
    # README witnesses vs y = (1,1,1,1024)
    y = [Fr(1), Fr(1), Fr(1), Fr(1024)]
    U0, L1, L2, U3 = y[0], y[1], y[2], y[3]
    out["F3_point"] = dict(
        log2y=[0, 0, 0, 10], second_diffs=[0, 10], convex=True,
        readme_w1_U0sq_L2cu_ge_L1pow4_U3=(U0 ** 2 * L2 ** 3 >= L1 ** 4 * U3),
        readme_w2_U0_L2pow4_ge_L1cu_U3sq=(U0 * L2 ** 4 >= L1 ** 3 * U3 ** 2),
        note_ray21_U0sq_U3_ge_L1cu=(U0 ** 2 * U3 >= L1 ** 3),
        note_ray12_U0_U3sq_ge_L2cu=(U0 * U3 ** 2 >= L2 ** 3),
        team_code_feasible=team.check_4pt_farkas_monotonicity(y, y, "convex")["feasible"],
        hull_feasible=hull_feasible([0, 0, 0, 10], [0, 0, 0, 10])[0])
    # what vectors do the README witnesses correspond to (exponent of U0,L1,L2,U3 on the >= side minus other side)
    out["F3_readme_vectors_log"] = {"w1": [2, -4, 3, -1], "w2": [1, -3, 4, -2],
                                    "w1_sum_coeffs": 2 - 4 + 3 - 1, "w2_sum_coeffs": 1 - 3 + 4 - 2,
                                    "w1_first_moment": 0 * 2 + 1 * -4 + 2 * 3 + 3 * -1, "w2_first_moment": 0 - 3 + 8 - 6}
    return out


def main():
    seed = 4242
    print(f"seed={seed}")
    team = load_team()
    rng = random.Random(seed)
    a = theorem_a(team, rng, 1500)
    b = theorem_b(team, rng, 1500)
    ex = a["evaluator_minimal_example"]
    check(ex["steps"] is True and ex["pairs"] is False and ex["forward"] is False, "minimal example not reproduced")
    check(b["m4_rays_equal_chord_triples"], "four rays are not the four chord triples")
    for m in (5, 6, 7):
        check(b[f"m{m}"]["irredundant_triples"] == b[f"m{m}"]["n_triples"], f"not every chord triple needed at m={m}")
        check(b[f"m{m}"]["sliding_4pt_windows_wrong"] > 0, f"sliding windows never wrong at m={m}")
    f3 = b["F3_point"]
    check(f3["convex"] and f3["team_code_feasible"] and f3["hull_feasible"] and f3["note_ray21_U0sq_U3_ge_L1cu"]
          and f3["note_ray12_U0_U3sq_ge_L2cu"] and not f3["readme_w1_U0sq_L2cu_ge_L1pow4_U3"]
          and not f3["readme_w2_U0_L2pow4_ge_L1cu_U3sq"], "README witness defect not reproduced")
    check(a["stp_agree"] == a["stp_cases"] and a["mult_agree"] == a["mult_cases"], "oracle disagreement in A")
    res = {"theorem_A": a, "theorem_B": b, "fails": FAILS[:10], "n_fails": len(FAILS)}
    if "--details" in sys.argv:
        print(json.dumps(res, indent=1, sort_keys=True))
    verdict = "OK" if not FAILS else "FAIL"
    print(f"ZEROLOG_EXACT_ADVOCATE {verdict}: A STP {a['stp_agree']}/{a['stp_cases']} ({a['stp_feasible']} feasible, "
          f"{a['witness_ok']} witnesses verified, {a['stp_local_yes_global_no']} step-pass global-fail), "
          f"rational {a['mult_agree']}/{a['mult_cases']} ({a['mult_local_yes_global_no']} step-pass global-fail); "
          f"B m=4 {b['m4']['agree']}/{b['m4']['cases']}, hull vs triples m=5,6,7 "
          f"{b['m5']['hull_vs_triples_agree']},{b['m6']['hull_vs_triples_agree']},{b['m7']['hull_vs_triples_agree']} of 1500, "
          f"sliding windows wrong m=5,6,7 {b['m5']['sliding_4pt_windows_wrong']},{b['m6']['sliding_4pt_windows_wrong']},"
          f"{b['m7']['sliding_4pt_windows_wrong']}; failures {len(FAILS)}")
    for f in FAILS[:10]:
        print("FAILED:", f)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
