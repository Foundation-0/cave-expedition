#!/usr/bin/env python3
"""Supplement to peel_tower_check.py (own code only). AUDIT-004 Part A. Backs VERDICTS.md section 3
(the dominance sentence over zeroSelfLoop is a statement about the chosen second quotient, not a general
law) and section 4 item 9 (quotient-lp-bounds 4 PROOF.md: with rounding, floor each layer's input costs).

S1  Smallest witnesses for each hypothesis of the optimality theorem where the failing state IS co-reachable.
S2  Per-layer rounding bound (PR 4, 4.3 applied to one quotient graph): with floored layer input,
    h_exact(a) - h_floor(a) <= hops(a)/D on every layer, hops = fewest edges on a floored shortest path.
    Random graphs use the fixed seed 31337 (printed).
S3  zeroSelfLoop deficit is a feasible second layer on the residual of the first.

Needs: Python 3, SymPy, peel_tower_check.py in the same folder. A clone of Foundation-0/quotient-lp-bounds
at PR 5 head (for certificate.json).
Run:   python3 -I -B peel_tower_supplement.py /path/to/quotient-lp-bounds     (or set QLB_CLONE)
Time:  about 5 seconds.
Last line: PEELING_SUPPLEMENT_CHECK OK ... ; exit 0 only if every check held.
"""
from __future__ import annotations

import itertools
import json
import importlib.util
import math
import os
import random
import sys
from fractions import Fraction as F
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "peel_tower_check", Path(os.path.abspath(__file__)).with_name("peel_tower_check.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)
SEED = 31337


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


def need(c, m):
    if not c:
        raise RuntimeError("CHECK FAILED: " + m)


def s1():
    best = {}
    for n in (2, 3):
        pairs = [(u, v) for u in range(1, n) for v in range(n)]
        for costs in itertools.product((None, 0, 1, 2), repeat=len(pairs)):
            E = [(u, v, F(c)) for (u, v), c in zip(pairs, costs) if c is not None]
            d = P.dist_to_goals(n, [0], E)
            for Hv in itertools.product(range(4), repeat=n - 1):
                H = [F(0)] + [F(x) for x in Hv]
                if not all(H[u] - H[v] <= w for u, v, w in E):
                    continue
                for conv in (False, True):
                    df = P.defect(n, [0], E, H, conv)
                    zero = all(x is not None and x == 0 for x in df.values())
                    for s in range(1, n):
                        if d[s] is None or not zero or H[s] == d[s]:
                            continue
                        # failing state s is co-reachable, delta == 0 everywhere, H(s) != d*(s)
                        tag = ("sink_delta_inf" if conv else "sink_delta_0")
                        haszero = any(w == 0 for _, _, w in E)
                        key = tag + ("|has zero-cost edge" if haszero else "|all costs > 0")
                        cand = (n, len(E))
                        if key not in best or cand < best[key][0]:
                            best[key] = (cand, {"n": n, "edges": [(u, v, str(w)) for u, v, w in E],
                                                "H": [str(x) for x in H], "dstar": [P.sfmt(x) for x in d],
                                                "failing_state": s})
    need(len(best) == 3, "expected three witness classes")
    return {k: v[1] for k, v in best.items()}


def hops_on_shortest(n, goals, edges, dist):
    """Fewest edges among shortest paths (dist exact) via BFS on tight edges."""
    hop = [None] * n
    for g in goals:
        hop[g] = 0
    changed = True
    while changed:
        changed = False
        for u, v, w in edges:
            if dist[u] is not None and dist[v] is not None and hop[v] is not None and dist[u] == dist[v] + w:
                if hop[u] is None or hop[v] + 1 < hop[u]:
                    hop[u] = hop[v] + 1
                    changed = True
    return hop


def s2(cert):
    insts = {"team_asym": P.team_instance(True)}
    insts.update(P.repo_instances(cert))
    rng = random.Random(SEED)
    for t in range(120):
        n = rng.randint(5, 9)
        E = P.random_graph(rng, n, True)
        insts[f"rand{t}"] = (n, [0], E, {f"q{j}": [0] + [rng.randrange(1, 3) for _ in range(n - 1)] for j in range(3)})
    checked = worst = 0
    worst_ratio = F(0)
    for name, (n, goals, E0, Q) in insts.items():
        for D in (1, 2, 10):
            res = [(u, v, F(w)) for u, v, w in E0]
            for qn, pi in Q.items():
                qn_ = max(pi) + 1
                qe, qf = {}, {}
                for u, v, w in res:
                    a, b = pi[u], pi[v]
                    if a != b:
                        wf = F(math.floor(w * D), D)
                        qe[(a, b)] = min(qe.get((a, b), w), w)
                        qf[(a, b)] = min(qf.get((a, b), wf), wf)
                qg = sorted({pi[g] for g in goals})
                he = P.dist_to_goals(qn_, qg, [(a, b, w) for (a, b), w in qe.items()])
                hf = P.dist_to_goals(qn_, qg, [(a, b, w) for (a, b), w in qf.items()])
                hops = hops_on_shortest(qn_, qg, [(a, b, w) for (a, b), w in qf.items()], hf)
                for a in set(pi):
                    loss = he[a] - hf[a]
                    need(loss >= 0, "floored quotient distance above exact")
                    need(loss <= F(hops[a], D), f"per-layer loss bound fails {name} {qn} D={D}")
                    if hops[a]:
                        worst_ratio = max(worst_ratio, loss / F(hops[a], D))
                    checked += 1
                # advance residual with the floored-input potential (tower rule 'floor_input')
                res = [(u, v, w + hf[pi[v]] - hf[pi[u]]) for u, v, w in res]
                need(all(w >= 0 for _, _, w in res), "floor_input residual negative")
    return {"quotient_vertex_checks": checked, "max_loss_over_hops_per_D": str(worst_ratio)}


def s3(cert):
    insts = {"team_sym": P.team_instance(False), "team_asym": P.team_instance(True)}
    insts.update(P.repo_instances(cert))
    out = {}
    for name, (n, goals, E, Q) in insts.items():
        for qn, pi in Q.items():
            H, res, hs, ok, _ = P.tower(n, goals, E, [pi])
            phi = P.zero_self_loop_best(n, goals, E, pi)
            need(all(phi[u] - phi[v] <= w for u, v, w in res), "zsl not feasible on residual")
            dres = P.dist_to_goals(n, goals, res)
            out[f"{name}|{qn}"] = {"sum_zsl_phi": str(sum(phi)), "sum_best_second_layer_full_state": str(sum(dres))}
    return out


def main():
    cert = cert_path()
    print(f"seed {SEED}")
    r1, r2, r3 = s1(), s2(cert), s3(cert)
    print(json.dumps({"S1_smallest_coreachable_witnesses": r1, "S2_per_layer_rounding": r2,
                      "S3_zsl_as_layer": r3}, indent=1))
    need(F(r2["max_loss_over_hops_per_D"]) <= 1, "loss ratio above 1")
    print(f"PEELING_SUPPLEMENT_CHECK OK: {len(r1)} witness classes, {r2['quotient_vertex_checks']} rounding "
          f"checks (max ratio {r2['max_loss_over_hops_per_D']}), {len(r3)} zsl layers feasible, seed {SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
