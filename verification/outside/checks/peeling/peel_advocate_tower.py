#!/usr/bin/env python3
"""Advocate recheck of AUDIT-004 Part A (own code, shares nothing with the expedition or the first-pass
check). Backs VERDICTS.md section 2 (the tower is saturated cost partitioning, label N0) and section 3 (the
sentence "the tower strictly dominates zeroSelfLoop whenever non-self-loop edges carry slack" is false:
hardin gives 114 against 237/2, and the headline baseline 64 is 84 for the best single quotient plus deficit).

Everything is exact (fractions.Fraction). LP values use HiGHS (SciPy) only to propose a primal point and a
dual multiplier vector; both are rationalised and then checked exactly (primal feasibility, dual
feasibility A^T y = objective, nonnegativity, equal objectives). A failed check exits non-zero.
No random numbers are used, so there is no seed.

Needs: Python 3, NumPy, SciPy. A clone of Foundation-0/quotient-lp-bounds at PR 5 head (certificate.json).
Run:   python3 -I -B peel_advocate_tower.py /path/to/quotient-lp-bounds     (or set QLB_CLONE)
Time:  about 5 seconds.
Last line: PEELING_ADVOCATE_TOWER OK ... ; exit 0 only if every check held.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from pathlib import Path
from fractions import Fraction as Q


def cert_path():
    """certificate.json inside a clone of quotient-lp-bounds. The clone (or the file itself) comes from
    the first command-line argument or the environment variable QLB_CLONE."""
    arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QLB_CLONE")
    if not arg:
        raise SystemExit("missing input: pass the path of a quotient-lp-bounds clone as the first argument "
                         "or set QLB_CLONE")
    p = Path(arg)
    if p.is_dir():
        p = p / "certificate.json"
    if not p.is_file():
        raise SystemExit("certificate.json not found in the given quotient-lp-bounds clone")
    return str(p)


def fail_unless(ok, msg):
    if not ok:
        raise SystemExit("CHECK FAILED: " + msg)


# ----------------------------------------------------------------- shortest paths (Bellman-Ford, exact)
def goal_dist(n, goals, edges):
    d = [None] * n
    for g in goals:
        d[g] = Q(0)
    for _ in range(n + 2):
        changed = False
        for u, v, w in edges:
            if d[v] is not None and (d[u] is None or d[v] + w < d[u]):
                d[u] = d[v] + w
                changed = True
        if not changed:
            return d
    raise SystemExit("negative cycle")


def quotient_h(n, goals, edges, pi):
    """Goal distances of the induced quotient (every concrete step mapped, parallel steps -> min)."""
    m = max(pi) + 1
    best = {}
    for u, v, w in edges:
        a, b = pi[u], pi[v]
        if a != b and ((a, b) not in best or w < best[(a, b)]):
            best[(a, b)] = w
    return goal_dist(m, sorted({pi[g] for g in goals}), [(a, b, w) for (a, b), w in best.items()])


def tower(n, goals, edges, pis):
    res = list(edges)
    H = [Q(0)] * n
    for pi in pis:
        h = quotient_h(n, goals, res, pi)
        fail_unless(all(h[pi[s]] is not None for s in range(n)), "quotient dead end")
        new = []
        for u, v, w in res:
            r = w + h[pi[v]] - h[pi[u]]
            fail_unless(r >= 0, "negative reduced cost")
            new.append((u, v, r))
        res = new
        H = [H[s] + h[pi[s]] for s in range(n)]
    return H, res


def consistent(goals, edges, H):
    return all(H[u] - H[v] <= w for u, v, w in edges) and all(H[g] <= 0 for g in goals)


def zsl_phi(n, goals, edges, pi):
    """Pointwise-largest deficit allowed by the repo's PROOF.md section 3 (self-loop: <= c, else <= 0)."""
    d = goal_dist(n, goals, [(u, v, w if pi[u] == pi[v] else Q(0)) for u, v, w in edges])
    return [Q(0) if x is None else x for x in d]


# ----------------------------------------------------------------- exact-checked LP over the feature span
def span_lp(n, goals, edges, pis):
    import numpy as np
    from scipy.optimize import linprog
    offs, nv = [], 0
    for pi in pis:
        offs.append(nv)
        nv += max(pi) + 1
    def row(s):
        return [offs[j] + pis[j][s] for j in range(len(pis))]
    rows = []
    for u, v, w in edges:
        if u == v:
            continue
        coef = {}
        for k in row(u):
            coef[k] = coef.get(k, 0) + 1
        for k in row(v):
            coef[k] = coef.get(k, 0) - 1
        rows.append((coef, w))
    for g in goals:
        coef = {}
        for k in row(g):
            coef[k] = coef.get(k, 0) + 1
        rows.append((coef, Q(0)))
    obj = [0] * nv
    for s in range(n):
        for k in row(s):
            obj[k] += 1
    A = np.zeros((len(rows), nv))
    b = np.zeros(len(rows))
    for i, (coef, w) in enumerate(rows):
        for k, c in coef.items():
            A[i, k] = c
        b[i] = float(w)
    lp = linprog(-np.array(obj, float), A_ub=A, b_ub=b, bounds=[(None, None)] * nv, method="highs")
    fail_unless(lp.status == 0, "highs failed")
    x = [Q(float(t)).limit_denominator(1000) for t in lp.x]
    y = [Q(float(max(t, 0.0))).limit_denominator(1000) for t in -lp.ineqlin.marginals]
    # exact primal feasibility
    for coef, w in rows:
        fail_unless(sum(c * x[k] for k, c in coef.items()) <= w, "rationalised primal infeasible")
    pval = sum(obj[k] * x[k] for k in range(nv))
    # exact dual feasibility: A^T y == obj, y >= 0
    col = [Q(0)] * nv
    for (coef, w), yi in zip(rows, y):
        for k, c in coef.items():
            col[k] += c * yi
    fail_unless(all(yi >= 0 for yi in y) and col == [Q(o) for o in obj], "rationalised dual infeasible")
    dval = sum(w * yi for (coef, w), yi in zip(rows, y))
    fail_unless(pval == dval, f"primal {pval} != dual {dval}")
    return pval


# ----------------------------------------------------------------- instances
def team_instance():
    """The 32-state system of build_coupled_2agent_system(asymmetric=False), rebuilt from its docstring."""
    st = [(x, y, m) for x in range(4) for y in range(4) for m in (0, 1)]
    ix = {s: i for i, s in enumerate(st)}
    E = []
    for x, y, m in st:
        u = ix[(x, y, m)]
        E.append((u, ix[(x, y, 1 - m)], Q(1)))
        if m == 0:
            if x > 0:
                E.append((u, ix[(x - 1, y, 0)], Q(1)))
            if x < 3:
                E.append((u, ix[(x + 1, y, 0)], Q(1)))
            if x > 0 and y > 0:
                E.append((u, ix[(x - 1, y - 1, 0)], Q(2)))
        else:
            if y > 0:
                E.append((u, ix[(x, y - 1, 1)], Q(1)))
            if y < 3:
                E.append((u, ix[(x, y + 1, 1)], Q(1)))
    pis = {"pi_x": [2 * x + m for x, y, m in st], "pi_y": [2 * y + m for x, y, m in st],
           "pi_imb": [2 * int(y > x) + m for x, y, m in st]}
    return len(st), [ix[(0, 0, 0)]], E, pis


def cert_instance(cert, name):
    inst = next(i for i in cert["instances"] if i["name"] == name)
    E = [(int(u), int(v), Q(str(w))) for u, v, w in inst["edges"]]
    return inst["num_vertices"], [int(g) for g in inst["goals"]], E


def repo_instances(path):
    cert = json.loads(Path(path).read_text())
    out = {}
    n, g, E = cert_instance(cert, "soko_iii14_transmutation_repair")
    st = [(c, d, a) for c in range(4) for d in range(5) for a in (0, 1)]  # verify.py loop order
    out["soko"] = (n, g, E, {"pi_c": [2 * c + a for c, d, a in st], "pi_d": [2 * d + a for c, d, a in st]})
    n, g, E = cert_instance(cert, "hardin_strip_w4_antidiag_edit_bound")
    st = [(m, u) for m in range(16) for u in range(3)]
    out["hardin"] = (n, g, E, {"pi_used": [u for m, u in st], "pi_pop": [bin(m).count("1") for m, u in st],
                               "pi_low2": [m & 3 for m, u in st]})
    n, g, E = cert_instance(cert, "multi_agent_cyclic_switch_partition")
    st = [(a, b, c) for a in range(4) for b in range(4) for c in (0, 1)]
    out["cyclic"] = (n, g, E, {"pi_d1": [2 * a + c for a, b, c in st], "pi_d2": [2 * b + c for a, b, c in st],
                               "pi_sum_parity": [((a + b) % 2) * 2 + c for a, b, c in st]})
    return out


def analyse(name, n, goals, E, pis):
    d = goal_dist(n, goals, E)
    fail_unless(all(x is not None for x in d), f"{name}: not co-reachable")
    rep = {"n": n, "edges": len(E), "sum_dstar": str(sum(d))}
    singles = {}
    for k, pi in pis.items():
        H, _ = tower(n, goals, E, [pi])
        phi = zsl_phi(n, goals, E, pi)
        Hz = [H[s] + phi[s] for s in range(n)]
        fail_unless(consistent(goals, E, Hz), "zsl composition inconsistent")
        singles[k] = (H, Hz)
        rep[f"single[{k}]"] = str(sum(H))
        rep[f"single+zsl[{k}]"] = str(sum(Hz))
    towers = {}
    for r in (2, 3):
        for perm in itertools.permutations(pis, r):
            H, res = tower(n, goals, E, [pis[p] for p in perm])
            fail_unless(consistent(goals, E, H) and all(H[s] <= d[s] for s in range(n)), "tower invalid")
            first = perm[0]
            base = singles[first][1]
            # docstring reading 1: compare with first quotient + its best zero-self-loop deficit
            pointwise_ge = all(H[s] >= base[s] for s in range(n))
            # slack on non-self-loop edges of the first quotient after the first layer
            _, res1 = tower(n, goals, E, [pis[first]])
            nsl = [w for (u, v, w) in res1 if pis[first][u] != pis[first][v]]
            towers["->".join(perm)] = {
                "sum": str(sum(H)), "exact": H == d,
                "vs_first+zsl": str(sum(H) - sum(base)),
                "pointwise_ge_first+zsl": pointwise_ge,
                "first_layer_nonselfloop_slack_pos_count": sum(1 for w in nsl if w > 0),
                "first_layer_nonselfloop_count": len(nsl),
            }
    rep["towers"] = towers
    names = list(pis)
    rep["LP_span_all"] = str(span_lp(n, goals, E, [pis[k] for k in names]))
    return rep


def main():
    cert = cert_path()
    out = {"team32": analyse("team32", *team_instance())}
    for k, v in repo_instances(cert).items():
        out[k] = analyse(k, *v)
    print(json.dumps(out, indent=1))
    team, hard, cyc = out["team32"], out["hardin"], out["cyclic"]
    fail_unless(team["sum_dstar"] == "124" and team["towers"]["pi_x->pi_y->pi_imb"]["sum"] == "124"
                and team["towers"]["pi_x->pi_y->pi_imb"]["exact"], "team 3-layer tower is not exact 124")
    fail_unless(team["towers"]["pi_x->pi_y"]["sum"] == "112", "team 2-layer tower is not 112")
    fail_unless(team["single[pi_x]"] == "64" and team["single[pi_y]"] == "84", "single quotients 64 and 84")
    fail_unless(team["LP_span_all"] == "124", "team LP over the three quotients is not 124")
    bad = hard["towers"]["pi_used->pi_low2"]
    fail_unless(bad["sum"] == "114" and hard["single+zsl[pi_used]"] == "237/2", "hardin 114 against 237/2")
    fail_unless(bad["first_layer_nonselfloop_slack_pos_count"] == 72
                and bad["first_layer_nonselfloop_count"] == 104, "hardin slack count 72 of 104")
    fail_unless(not bad["pointwise_ge_first+zsl"], "hardin tower should lose pointwise")
    fail_unless(team["towers"]["pi_imb->pi_y"]["vs_first+zsl"] == "-4", "team pi_imb->pi_y should lose by 4")
    fail_unless(team["towers"]["pi_y->pi_x"]["vs_first+zsl"] == "0"
                and team["towers"]["pi_y->pi_x"]["first_layer_nonselfloop_slack_pos_count"] == 35,
                "team pi_y->pi_x should tie with positive slack on 35 edges")
    fail_unless(cyc["sum_dstar"] == "80" and cyc["LP_span_all"] == "68", "cyclic instance LP 68, truth 80")
    print("PEELING_ADVOCATE_TOWER OK: PR5 instance 64/84 -> 112 -> 124 (LP 124); hardin 114 < 237/2 "
          "(72 of 104 edges slack); imb->y 52 < 56; y->x ties 84; repo3 LP 68, truth 80")
    return 0


if __name__ == "__main__":
    sys.exit(main())
