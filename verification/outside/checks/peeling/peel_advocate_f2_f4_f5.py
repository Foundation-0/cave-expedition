#!/usr/bin/env python3
"""Advocate recheck of the narrowed dominance theorem (F2), the Doob reading (F4) and the optimality theorem
(F5), AUDIT-004 Part A and AUDIT-008R. Backs VERDICTS.md section 3 (the true form of the dominance claim: if
the second quotient is constant on the deficit's level sets, the 2-layer tower is at least the single
quotient plus deficit at every state, 0 failures in 822 checks) and section 1 (optimality theorem holds).

F2  tower(pi1, pi2) >= pi1*h1 + phi pointwise when phi factors through pi2: 22 instance cases and 800 random
    cases (fixed seed 20261120, printed).
F4  D^-1 K D is never row-stochastic (not a Doob transform) but is max-stochastic when H = d*.
F5  Bellman iff, brute force over all small co-reachable graphs with positive costs.

Own code. Imports peel_advocate_tower.py from the same folder.
Needs: Python 3, NumPy, SciPy (through peel_advocate_tower.py). A clone of Foundation-0/quotient-lp-bounds
at PR 5 head (certificate.json).
Run:   python3 -I -B peel_advocate_f2_f4_f5.py /path/to/quotient-lp-bounds     (or set QLB_CLONE)
Time:  about 20 seconds.
Last line: PEELING_ADVOCATE_F2_F4_F5 OK ... ; exit 0 only if every check held.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import random
import sys
from fractions import Fraction as Q

_spec = importlib.util.spec_from_file_location(
    "rt", os.path.join(os.path.dirname(os.path.abspath(__file__)), "peel_advocate_tower.py"))
rt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rt)
fail_unless, goal_dist, tower, zsl_phi, consistent = rt.fail_unless, rt.goal_dist, rt.tower, rt.zsl_phi, rt.consistent


def level_sets(vals):
    keys = {}
    return [keys.setdefault(v, len(keys)) for v in vals]


def refine(p1, p2):
    return level_sets(list(zip(p1, p2)))


# ------------------------------------------------------------- F2 narrowed: tower(pi1, pi2) >= h1 + phi1 if phi1 factors through pi2
def f2_theorem(instances, rng):
    out = {"instance_checks": 0, "instance_fail": 0, "random_checks": 0, "random_fail": 0,
           "random_strict_gain": 0, "random_equal": 0}

    def check(n, goals, E, p1, p2):
        phi = zsl_phi(n, goals, E, p1)
        H1, _ = tower(n, goals, E, [p1])
        base = [H1[s] + phi[s] for s in range(n)]
        # pi2 must resolve phi: phi constant on pi2 fibres
        fib = {}
        for s in range(n):
            fib.setdefault(p2[s], set()).add(phi[s])
        if any(len(v) > 1 for v in fib.values()):
            return None
        H, _ = tower(n, goals, E, [p1, p2])
        return all(H[s] >= base[s] for s in range(n)), sum(H) > sum(base)

    for name, (n, goals, E, pis) in instances.items():
        for k, p1 in pis.items():
            phi = zsl_phi(n, goals, E, p1)
            for p2 in (level_sets(phi), refine(level_sets(phi), p1)):
                r = check(n, goals, E, p1, p2)
                fail_unless(r is not None, "construction should resolve phi")
                out["instance_checks"] += 1
                out["instance_fail"] += (not r[0])
    for t in range(400):
        n = rng.randint(4, 9)
        E = []
        for s in range(1, n):
            E.append((s, rng.randrange(0, s), Q(rng.randint(1, 4), rng.choice([1, 2]))))
        for _ in range(rng.randint(n, 3 * n)):
            u, v = rng.randrange(1, n), rng.randrange(0, n)
            if u != v:
                E.append((u, v, Q(rng.randint(0, 4), rng.choice([1, 2]))))
        p1 = [0] + [rng.randrange(1, 4) for _ in range(n - 1)]
        phi = zsl_phi(n, [0], E, p1)
        for p2 in (level_sets(phi), refine(level_sets(phi), [rng.randrange(0, 3) for _ in range(n)])):
            r = check(n, [0], E, p1, p2)
            if r is None:
                continue
            out["random_checks"] += 1
            out["random_fail"] += (not r[0])
            out["random_strict_gain"] += r[1]
            out["random_equal"] += (r[0] and not r[1])
    fail_unless(out["instance_fail"] == 0 and out["random_fail"] == 0, "narrowed F2 theorem failed")
    return out


# ------------------------------------------------------------- F4: ordinary vs max-times stochasticity of D^-1 K D
def f4_doob(n, goals, E, Hlayers):
    rep = {}
    d = goal_dist(n, goals, E)
    for label, H in Hlayers.items():
        delta = {s: min(w + H[v] - H[u] for u, v, w in E if u == s) for s in range(n) if s not in goals}
        rows = []
        for q in (Q(1, 2), Q(1, 4), Q(1, 8), Q(1, 16)):
            K = [[Q(0)] * n for _ in range(n)]
            for u, v, w in E:
                K[u][v] += q ** int(w)
            Dg = [q ** int(H[s]) for s in range(n)]
            Kp = [[Dg[v] * K[u][v] / Dg[u] for v in range(n)] for u in range(n)]
            Kr = [[Q(0)] * n for _ in range(n)]
            for u, v, w in E:
                Kr[u][v] += q ** int(w + H[v] - H[u])
            fail_unless(Kp == Kr, "diagonal similarity identity fails")
            nongoal = [s for s in range(n) if s not in goals]
            plus_stoch = sum(1 for s in nongoal if sum(Kp[s]) == 1)
            max_row_is_q_delta = all(max(Kp[s]) == q ** int(delta[s]) for s in nongoal)
            max_stoch = sum(1 for s in nongoal if max(Kp[s]) == 1)
            rows.append({"q": str(q), "nongoal_rows": len(nongoal), "rows_sum_to_1": plus_stoch,
                         "rows_max_eq_1": max_stoch, "row_max_equals_q^delta": max_row_is_q_delta})
            fail_unless(max_row_is_q_delta, "row max != q^delta")
        rep[label] = {"H_equals_dstar": H == d, "states_with_positive_delta": sum(1 for x in delta.values() if x > 0),
                      "rows": rows}
    return rep


# ------------------------------------------------------------- F5: Bellman uniqueness brute force
def f5_bruteforce():
    stats = {"graphs": 0, "H_tested": 0, "iff_fail": 0}
    for n in (2, 3, 4):
        pairs = [(u, v) for u in range(1, n) for v in range(n) if u != v]
        choices = (None, 1, 2) if n == 4 else (None, 1, 2, 3)
        for costs in itertools.product(choices, repeat=len(pairs)):
            E = [(u, v, Q(c)) for (u, v), c in zip(pairs, costs) if c is not None]
            d = goal_dist(n, [0], E)
            if any(x is None for x in d):
                continue  # team hypothesis: co-reachable
            stats["graphs"] += 1
            top = 5 if n == 4 else 3 * n
            for Hv in itertools.product(range(top + 1), repeat=n - 1):
                H = [Q(0)] + [Q(x) for x in Hv]
                delta_zero = all(min(w + H[v] - H[u] for u, v, w in E if u == s) == 0 for s in range(1, n))
                stats["H_tested"] += 1
                if delta_zero != (H == d):
                    stats["iff_fail"] += 1
    fail_unless(stats["iff_fail"] == 0, "Bellman iff failed under c>0 & co-reachable")
    return stats


SEED = 20261120


def main():
    print(f"seed {SEED}")
    rng = random.Random(SEED)
    inst = {"team32": rt.team_instance()}
    inst.update(rt.repo_instances(rt.cert_path()))
    out = {"F2_narrowed": f2_theorem(inst, rng)}
    n, goals, E, pis = inst["team32"]
    H3, _ = tower(n, goals, E, [pis["pi_x"], pis["pi_y"], pis["pi_imb"]])
    H2, _ = tower(n, goals, E, [pis["pi_x"], pis["pi_y"]])
    out["F4_doob"] = f4_doob(n, goals, E, {"3-layer (exact)": H3, "2-layer (not exact)": H2})
    out["F5_bellman"] = f5_bruteforce()
    print(json.dumps(out, indent=1))
    f2, f5 = out["F2_narrowed"], out["F5_bellman"]
    d3, d2 = out["F4_doob"]["3-layer (exact)"], out["F4_doob"]["2-layer (not exact)"]
    fail_unless(f2["instance_checks"] == 22 and f2["random_checks"] == 800, "F2 case counts")
    fail_unless(all(r["rows_sum_to_1"] == 0 for r in d3["rows"] + d2["rows"]), "F4 some row is stochastic")
    fail_unless(d3["H_equals_dstar"] and not d2["H_equals_dstar"], "F4 layer exactness")
    fail_unless(f5["iff_fail"] == 0, "F5 failure")
    print(f"PEELING_ADVOCATE_F2_F4_F5 OK: F2 0 failures in {f2['instance_checks'] + f2['random_checks']}, "
          f"F4 0 stochastic rows, F5 0 failures on {f5['graphs']} graphs, seed {SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
