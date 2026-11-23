#!/usr/bin/env python3
"""Independent check of the peeling tower (AUDIT-004 Part A). Backs VERDICTS.md section 1 (peeling tower
64 / 112 / 124, optimality theorem), section 2 (labels N0) and section 3 (the baseline 64 is 84 fairly,
and the strict-dominance sentence over zeroSelfLoop is false on hardin: 114 against 237/2).

Shares no code with the expedition. Exact rationals only (fractions.Fraction, SymPy exact simplex).
Every check raises through need(); there is no bare assert.

Sections
  1. Tower + exact Dijkstra on the 32-state system of quotient-lp-bounds PR 5 (rebuilt from its
     docstring), the asymmetric variant, and three instances of the repo's certificate.json.
  2. Order dependence (all permutations) and the exact LP optimum over the same quotient features.
  3. Optimality theorem: brute force over all small graphs, minimal counterexamples per hypothesis.
  4. Rounding (ties to quotient-lp-bounds PR 4).
  5. Missing / overpriced abstract step (ties to loom docs/09 Claims 12, 13).
  6. Random graphs (fixed seed, printed): validity, identity, iff, order dependence, greedy vs LP gap.

Needs: Python 3, SymPy. A clone of Foundation-0/quotient-lp-bounds at PR 5 head (for certificate.json).
Run:   python3 -I -B peel_tower_check.py /path/to/quotient-lp-bounds     (or set QLB_CLONE)
Time:  about 5 seconds.
Last line: PEELING_TOWER_CHECK OK ... ; exit 0 only if every check held.
"""
from __future__ import annotations

import heapq
import itertools
import json
import math
import os
import random
import sys
from fractions import Fraction as F
from pathlib import Path

import sympy
from sympy.solvers.simplex import lpmax, lpmin

INF = None
RESULTS: dict = {}


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


def need(cond, msg):
    if not cond:
        raise RuntimeError("CHECK FAILED: " + msg)


# ---------------------------------------------------------------- graph primitives
def dist_to_goals(n, goals, edges):
    """Exact Dijkstra on reversed graph. edges: list of (u, v, w) with w >= 0. Returns list (None = inf)."""
    radj = [[] for _ in range(n)]
    for u, v, w in edges:
        need(w >= 0, "negative weight in dijkstra")
        radj[v].append((u, w))
    d = [None] * n
    pq = []
    for g in set(goals):
        d[g] = F(0)
        pq.append((F(0), g))
    heapq.heapify(pq)
    done = [False] * n
    while pq:
        dv, v = heapq.heappop(pq)
        if done[v]:
            continue
        done[v] = True
        for u, w in radj[v]:
            nd = dv + w
            if d[u] is None or nd < d[u]:
                d[u] = nd
                heapq.heappush(pq, (nd, u))
    return d


def bellman_ford(n, goals, edges):
    """Second, independent shortest-path routine (allows any sign; detects negative cycles)."""
    d = [None] * n
    for g in goals:
        d[g] = F(0)
    for _ in range(n + 1):
        changed = False
        for u, v, w in edges:
            if d[v] is not None and (d[u] is None or d[v] + w < d[u]):
                d[u] = d[v] + w
                changed = True
        if not changed:
            return d, False
    return d, True  # still changing after n+1 rounds: negative cycle reachable


def quotient_potential(n, goals, edges, pi):
    """Shortest-path potential of the induced quotient graph (every real step mapped, min weight)."""
    qn = max(pi) + 1
    qe = {}
    for u, v, w in edges:
        a, b = pi[u], pi[v]
        if a == b:
            continue
        if (a, b) not in qe or w < qe[(a, b)]:
            qe[(a, b)] = w
    qg = sorted({pi[g] for g in goals})
    h = dist_to_goals(qn, qg, [(a, b, w) for (a, b), w in qe.items()])
    return h


def tower(n, goals, edges, quotients, layer_rule="exact", D=None):
    """Peel quotients in order. Returns (H, residual_edges, per-layer h list, ok_flag, first_violation).

    layer_rule:
      exact          : h_j = quotient distance under residual c^(j-1)
      floor_pot      : h_j = floor_D(exact h_j) (potential floored after the fact)
      floor_input    : h_j = quotient distance under floor_D(c^(j-1)); residual shifted on exact c^(j-1)
    """
    res = [(u, v, F(w)) for u, v, w in edges]
    H = [F(0)] * n
    hs = []
    for pi in quotients:
        if layer_rule == "floor_input":
            inp = [(u, v, F(math.floor(w * D), D)) for u, v, w in res]
        else:
            inp = res
        h = quotient_potential(n, goals, inp, pi)
        imgs = {pi[s] for s in range(n)}
        if any(h[a] is None for a in imgs):
            return None, None, hs, False, "quotient dead end"
        if layer_rule == "floor_pot":
            h = [None if x is None else F(math.floor(x * D), D) for x in h]
        hs.append(h)
        new = []
        for u, v, w in res:
            r = w + h[pi[v]] - h[pi[u]]
            if r < 0:
                return None, None, hs, False, ("negative reduced cost", u, v, str(r))
            new.append((u, v, r))
        res = new
        for s in range(n):
            H[s] += h[pi[s]]
    return H, res, hs, True, None


def is_consistent(n, goals, edges, H):
    return all(H[u] - H[v] <= w for u, v, w in edges) and all(H[g] <= 0 for g in goals)


def lp_optimum_feature_span(n, goals, edges, quotients):
    """Exact max sum_s H(s) over H = sum_j pi_j^* h_j, consistent on every real edge, H(goal) <= 0.

    Solved with sympy's exact rational simplex, and the dual solved separately; both objectives must match.
    """
    vars_ = []
    feat = []  # feat[s] = list of variable indices
    for j, pi in enumerate(quotients):
        base = len(vars_)
        for a in range(max(pi) + 1):
            vars_.append(sympy.Symbol(f"h{j}_{a}"))
        feat.append([base + p for p in pi])
    Hs = [sum(vars_[feat[j][s]] for j in range(len(quotients))) for s in range(n)]
    cons = [Hs[u] - Hs[v] <= sympy.Rational(w.numerator, w.denominator) for u, v, w in edges if u != v]
    cons += [Hs[g] <= 0 for g in goals]
    obj = sum(Hs)
    val, sol = lpmax(obj, cons)
    # exact primal feasibility re-check
    Hval = [F(str(sympy.nsimplify(h.subs(sol)))) for h in Hs]
    need(is_consistent(n, goals, edges, Hval), "LP primal infeasible on re-check")
    # dual: variables y_e >= 0 for each constraint row; A^T y = gradient of objective
    rows = [(u, v, w) for u, v, w in edges if u != v] + [(g, None, F(0)) for g in goals]
    ys = [sympy.Symbol(f"y{i}") for i in range(len(rows))]
    nv = len(vars_)
    col = [0] * nv
    for i, (u, v, w) in enumerate(rows):
        for j in range(len(quotients)):
            col_u = feat[j][u]
            col[col_u] = col[col_u] + ys[i]
            if v is not None:
                col_v = feat[j][v]
                col[col_v] = col[col_v] - ys[i]
    target = [0] * nv
    for s in range(n):
        for j in range(len(quotients)):
            target[feat[j][s]] += 1
    # Dual certificate: HiGHS proposes a support; the support system is then solved exactly.
    import numpy as np
    from scipy.optimize import linprog
    A = np.zeros((len(rows), nv))
    b = np.zeros(len(rows))
    for i, (u, v, w) in enumerate(rows):
        for j in range(len(quotients)):
            A[i, feat[j][u]] += 1
            if v is not None:
                A[i, feat[j][v]] -= 1
        b[i] = float(w)
    cvec = -np.array(target, dtype=float)
    lp = linprog(cvec, A_ub=A, b_ub=b, bounds=[(None, None)] * nv, method="highs")
    need(lp.status == 0, "highs failed")
    yf = -lp.ineqlin.marginals
    supp = [i for i in range(len(rows)) if yf[i] > 1e-9]
    ysym = [ys[i] for i in supp]
    Aint = [[int(round(A[i, k])) for k in range(nv)] for i in range(len(rows))]
    eqs = [sympy.Eq(sum((Aint[i][k] * ys[i] for i in supp), sympy.Integer(0)), target[k]) for k in range(nv)]
    need(sympy.false not in eqs, "dual support row reads 0 = nonzero")
    eqs = [e for e in eqs if e is not sympy.true]
    dsol = sympy.linsolve(eqs, ysym)
    need(dsol != sympy.EmptySet, "dual support system inconsistent")
    (tup,) = list(dsol)
    free = sorted(set().union(*[sympy.sympify(x).free_symbols for x in tup]), key=str)
    if free:
        # pin free parameters by a small exact LP on the support only
        dobj = sum(sympy.Rational(rows[i][2].numerator, rows[i][2].denominator) * yv for i, yv in zip(supp, tup))
        dval, fs = lpmin(dobj, [yv >= 0 for yv in tup])
        tup = [sympy.sympify(yv).subs(fs) for yv in tup]
    need(all(sympy.sympify(yv) >= 0 for yv in tup), "dual negative")
    dval = sum(sympy.Rational(rows[i][2].numerator, rows[i][2].denominator) * yv for i, yv in zip(supp, tup))
    need(sympy.simplify(dval - val) == 0, f"LP primal {val} != exact dual {dval}")
    return F(str(val)), Hval


# ---------------------------------------------------------------- instances
def team_instance(asymmetric=False):
    """Rebuilt from the docstring of build_coupled_2agent_system (own code)."""
    st = [(x, y, m) for x in range(4) for y in range(4) for m in (0, 1)]
    ix = {s: i for i, s in enumerate(st)}
    E = []
    for (x, y, m) in st:
        u = ix[(x, y, m)]
        E.append((u, ix[(x, y, 1 - m)], F(1)))
        if m == 0:
            for dx in (-1, 1):
                if 0 <= x + dx <= 3:
                    E.append((u, ix[(x + dx, y, 0)], F(1)))
            if x >= 1 and y >= 1:
                E.append((u, ix[(x - 1, y - 1, 0)], F(3, 2) if asymmetric else F(2)))
        else:
            for dy in (-1, 1):
                if 0 <= y + dy <= 3:
                    E.append((u, ix[(x, y + dy, 1)], F(1)))
            if asymmetric and x >= 1:
                E.append((u, ix[(x - 1, y, 1)], F(2)))
    pix = [2 * x + m for (x, y, m) in st]
    piy = [2 * y + m for (x, y, m) in st]
    pimb = [2 * int(y > x) + m for (x, y, m) in st]
    return len(st), [ix[(0, 0, 0)]], E, {"pi_x": pix, "pi_y": piy, "pi_imb": pimb}


def load_cert(path, name):
    b = json.loads(Path(path).read_text())
    inst = next(i for i in b["instances"] if i["name"] == name)
    E = [(int(u), int(v), F(str(w))) for u, v, w in inst["edges"]]
    return inst["num_vertices"], [int(g) for g in inst["goals"]], E


def repo_instances(cert):
    out = {}
    # Instance 3: states (d1, d2, act), index ((d1*4)+d2)*2+act
    n, g, E = load_cert(cert, "multi_agent_cyclic_switch_partition")
    st = [(a, b, c) for a in range(4) for b in range(4) for c in (0, 1)]
    out["repo3_cyclic_switch"] = (n, g, E, {
        "pi_d1": [2 * a + c for a, b, c in st],
        "pi_d2": [2 * b + c for a, b, c in st],
        "pi_sum_parity": [((a + b) % 2) * 2 + c for a, b, c in st],
    })
    # Instance 1: states (c_miss 0..3, d_goal 0..4, ah), index (c*5+d)*2+ah
    n, g, E = load_cert(cert, "soko_iii14_transmutation_repair")
    st = [(c, d, a) for c in range(4) for d in range(5) for a in (0, 1)]
    out["repo1_soko"] = (n, g, E, {
        "pi_c": [2 * c + a for c, d, a in st],
        "pi_d": [2 * d + a for c, d, a in st],
    })
    # Instance 2: states (mask 0..15, used 0..2), index mask*3+used; half-integer costs
    n, g, E = load_cert(cert, "hardin_strip_w4_antidiag_edit_bound")
    st = [(m, u) for m in range(16) for u in range(3)]
    out["repo2_hardin"] = (n, g, E, {
        "pi_used": [u for m, u in st],
        "pi_pop": [bin(m).count("1") for m, u in st],
        "pi_low2": [m & 3 for m, u in st],
    })
    return out


def zero_self_loop_best(n, goals, edges, pi):
    """Pointwise-max deficit phi: phi(u)-phi(v) <= c on quotient self-loops, <= 0 otherwise."""
    return dist_to_goals(n, goals, [(u, v, (w if pi[u] == pi[v] else F(0))) for u, v, w in edges])


def sfmt(x):
    return None if x is None else str(x)


# ---------------------------------------------------------------- section 1-2
def section_tower(cert):
    rep = {}
    insts = {"team_sym": team_instance(False), "team_asym": team_instance(True)}
    insts.update(repo_instances(cert))
    for name, (n, goals, E, Q) in insts.items():
        d = dist_to_goals(n, goals, E)
        d2, negc = bellman_ford(n, goals, E)
        need(d == d2 and not negc, f"{name}: dijkstra != bellman-ford")
        need(all(x is not None for x in d), f"{name}: some state not co-reachable")
        r = {"n": n, "edges": len(E), "sum_dstar": str(sum(d))}
        names = list(Q)
        # single quotients and zero-self-loop baseline
        for qn in names:
            H, res, hs, ok, why = tower(n, goals, E, [Q[qn]])
            need(ok, f"{name}:{qn} single failed {why}")
            phi = zero_self_loop_best(n, goals, E, Q[qn])
            Hz = [H[s] + phi[s] for s in range(n)]
            need(is_consistent(n, goals, E, Hz), "zsl composition not consistent")
            r[f"single[{qn}]"] = str(sum(H))
            r[f"single+zsl[{qn}]"] = str(sum(Hz))
        # every ordered sequence of 2 and 3 distinct quotients
        seqs = {}
        for k in (2, 3):
            if len(names) < k:
                continue
            for perm in itertools.permutations(names, k):
                H, res, hs, ok, why = tower(n, goals, E, [Q[p] for p in perm])
                need(ok, f"{name}:{perm} failed {why}")
                need(is_consistent(n, goals, E, H), "tower not consistent")
                need(all(H[s] <= d[s] for s in range(n)), "tower exceeds d*")
                dres = dist_to_goals(n, goals, res)
                need(all(d[s] - H[s] == dres[s] for s in range(n)), "identity d*-H = d*_res fails")
                # iff (all costs > 0 here except check)
                defect0 = all(min(w for u, v, w in res if u == s) == 0 for s in range(n) if s not in goals)
                exact = H == d
                if all(w > 0 for _, _, w in E):
                    need(defect0 == exact, "iff fails on instance")
                seqs["->".join(perm)] = (str(sum(H)), exact)
        r["towers"] = seqs
        # pointwise max over all 2-orders
        # exact LP optimum in the span of the same features (2-set and full set)
        for k in sorted({2, len(names)}):
            for combo in itertools.combinations(names, k):
                val, Hlp = lp_optimum_feature_span(n, goals, E, [Q[c] for c in combo])
                need(all(Hlp[s] <= d[s] for s in range(n)), "LP bound exceeds d*")
                r[f"LP_opt{{{','.join(combo)}}}"] = str(val)
        rep[name] = r
    return rep


# ---------------------------------------------------------------- section 3: optimality theorem brute force
def defect(n, goals, edges, H, sink_inf):
    out = {}
    for s in range(n):
        if s in goals:
            continue
        rs = [w + H[v] - H[u] for u, v, w in edges if u == s]
        out[s] = (min(rs) if rs else (None if sink_inf else F(0)))  # None = +inf
    return out


def section_optimality():
    """All graphs on 2 and 3 states (state 0 = goal, goal has no out-edges), costs in {absent,0,1,2},
    self-loops allowed; all integer potentials H in {0..3} on non-goal states that are consistent.
    Classify failures of the iff under each hypothesis set and record smallest witnesses."""
    stats = {}
    witnesses = {}
    for n in (2, 3):
        pairs = [(u, v) for u in range(1, n) for v in range(n)]
        for costs in itertools.product((None, 0, 1, 2), repeat=len(pairs)):
            E = [(u, v, F(c)) for (u, v), c in zip(pairs, costs) if c is not None]
            d = dist_to_goals(n, [0], E)
            pos = all(w > 0 for _, _, w in E)
            # zero-cost cycle among non-goal states?  check via graph of zero edges
            zero_adj = {s: [v for u, v, w in E if u == s and w == 0 and v != 0] for s in range(1, n)}
            zc = False
            for s in range(1, n):
                stack, seen = [s], set()
                while stack:
                    x = stack.pop()
                    for y in zero_adj.get(x, []):
                        if y == s:
                            zc = True
                        if y not in seen:
                            seen.add(y)
                            stack.append(y)
            coreach = all(x is not None for x in d)
            sinks = any(not any(u == s for u, _, _ in E) for s in range(1, n))
            for Hv in itertools.product(range(4), repeat=n - 1):
                H = [F(0)] + [F(x) for x in Hv]
                if not all(H[u] - H[v] <= w for u, v, w in E):
                    continue
                exact = all(d[s] is not None and H[s] == d[s] for s in range(n))
                for conv in ("sink_zero", "sink_inf"):
                    df = defect(n, [0], E, H, conv == "sink_inf")
                    zero = all(x is not None and x == 0 for x in df.values())
                    key_hyp = []
                    if pos and coreach:
                        key_hyp.append("team: c>0 & coreachable")
                    if not zc and conv == "sink_inf":
                        key_hyp.append("repair: no zero cycle & delta(sink)=inf")
                    if not zc and conv == "sink_zero":
                        key_hyp.append("drop coreach (sink delta=0), keep no zero cycle")
                    if conv == "sink_inf" and zc:
                        key_hyp.append("drop no-zero-cycle (sink delta=inf)")
                    for kh in key_hyp:
                        st = stats.setdefault(kh, {"cases": 0, "iff_fail": 0})
                        st["cases"] += 1
                        if zero != exact:
                            st["iff_fail"] += 1
                            if kh not in witnesses or len(E) < len(witnesses[kh]["edges"]) or n < witnesses[kh]["n"]:
                                witnesses[kh] = {"n": n, "edges": [(u, v, str(w)) for u, v, w in E],
                                                 "H": [str(x) for x in H], "dstar": [sfmt(x) for x in d],
                                                 "defect": {k: sfmt(v) for k, v in df.items()}}
    need(stats["team: c>0 & coreachable"]["iff_fail"] == 0, "team-hypothesis iff fails")
    need(stats["repair: no zero cycle & delta(sink)=inf"]["iff_fail"] == 0, "repaired iff fails")
    need(stats["drop coreach (sink delta=0), keep no zero cycle"]["iff_fail"] > 0, "coreach not needed?")
    need(stats["drop no-zero-cycle (sink delta=inf)"]["iff_fail"] > 0, "zero-cycle hyp not needed?")
    return {"stats": stats, "smallest_witness": witnesses}


# ---------------------------------------------------------------- section 4: rounding
def section_rounding(cert):
    rep = {}
    # 4a smallest floor-potential failure: chain 2->1->0 cost 1/2 each, identity quotient, D=1
    E = [(2, 1, F(1, 2)), (1, 0, F(1, 2))]
    H, res, hs, ok, why = tower(3, [0], E, [[0, 1, 2]], "floor_pot", 1)
    need(not ok, "floor_pot should fail on 2-edge chain")
    rep["floor_potential_smallest_failure"] = {"edges": "2->1 (1/2), 1->0 (1/2), D=1", "exact_h": [str(x) for x in hs[0]] if hs else None, "violation": str(why)}
    # 4b signed-share flooring (PR 4 rule applied to tower shares): 2-cycle a<->b
    E = [(1, 2, F(1)), (2, 1, F(1)), (1, 0, F(3, 2)), (2, 0, F(1))]
    H, res, hs, ok, why = tower(3, [0], E, [[0, 1, 2]])
    need(ok, "exact single layer ok")
    shares = [(u, v, F(math.floor((hs[0][u] - hs[0][v]) * 1), 1)) for u, v, w in E]
    dshare, negcyc = bellman_ford(3, [0], shares)
    rep["signed_share_floor"] = {"h": [str(x) for x in hs[0]], "shares_floored_D1": [(u, v, str(w)) for u, v, w in shares],
                                 "negative_cycle_after_floor": negcyc}
    need(negcyc, "expected a negative cycle from floored signed shares")
    # 4c instances: on-grid -> potentials already on grid; off-grid -> compare rules
    insts = {"team_sym": team_instance(False), "team_asym": team_instance(True)}
    insts.update(repo_instances(cert))
    table = {}
    for name, (n, goals, E0, Q) in insts.items():
        names = list(Q)
        for D in (1, 2, 10):
            for perm in itertools.permutations(names, min(3, len(names))):
                qs = [Q[p] for p in perm]
                He, rese, hse, oke, _ = tower(n, goals, E0, qs, "exact")
                need(oke, "exact tower failed")
                ongrid_costs = all((w * D).denominator == 1 for _, _, w in E0)
                ongrid_pots = all(x is None or (x * D).denominator == 1 for h in hse for x in h)
                if ongrid_costs:
                    need(ongrid_pots, "on-grid costs but off-grid potentials")
                Hp, _, _, okp, whyp = tower(n, goals, E0, qs, "floor_pot", D)
                Hi, _, _, oki, whyi = tower(n, goals, E0, qs, "floor_input", D)
                need(oki and is_consistent(n, goals, E0, Hi), "floor_input must always be valid")
                Ef = [(u, v, F(math.floor(w * D), D)) for u, v, w in E0]
                Hc, _, _, okc, _ = tower(n, goals, Ef, qs, "exact")
                need(okc and is_consistent(n, goals, E0, Hc), "floor-costs-once must be valid")
                if okp:
                    need(is_consistent(n, goals, E0, Hp), "floor_pot accepted but inconsistent")
                key = f"{name}|D={D}|{'->'.join(perm)}"
                table[key] = {"ongrid_costs": ongrid_costs, "exact": str(sum(He)),
                              "floor_pot_valid": okp, "floor_pot_sum": str(sum(Hp)) if okp else str(whyp),
                              "floor_input_sum": str(sum(Hi)), "floor_costs_once_sum": str(sum(Hc)),
                              "max_state_loss_floor_input": str(max(He[s] - Hi[s] for s in range(n))),
                              "max_state_gain_floor_input": str(max(Hi[s] - He[s] for s in range(n)))}
    rep["instances"] = table
    return rep


# ---------------------------------------------------------------- section 5: missing step
def section_missing_step():
    rep = {}
    # states 0 goal, 1, 2, 3. Real steps: 3->2, 2->1, 1->0 (cost 1), shortcut 3->0 (cost 1).
    E = [(3, 2, F(1)), (2, 1, F(1)), (1, 0, F(1)), (3, 0, F(1))]
    pi = [0, 1, 2, 2]  # class {2,3}
    d = dist_to_goals(4, [0], E)
    # hand specification that omits the abstract step 2->0 (the image of the real step 3->0)
    spec = [(2, 1, F(1)), (1, 0, F(1))]
    h = dist_to_goals(3, [0], spec)
    H = [h[pi[s]] for s in range(4)]
    bad = [s for s in range(4) if H[s] > d[s]]
    neg = [(u, v, str(w + H[v] - H[u])) for u, v, w in E if w + H[v] - H[u] < 0]
    need(bad == [3] and neg == [(3, 0, "-1")], "missing-step example not as expected")
    # induced quotient (tower's rule) contains the step and is valid
    Ht, _, _, okt, _ = tower(4, [0], E, [pi])
    need(okt and all(Ht[s] <= d[s] for s in range(4)), "induced quotient must be valid")
    # overpriced abstract step: step present but priced 2 > real cost 1
    spec2 = [(2, 1, F(1)), (1, 0, F(1)), (2, 0, F(2))]
    h2 = dist_to_goals(3, [0], spec2)
    H2 = [h2[pi[s]] for s in range(4)]
    need(H2[3] > d[3], "overpriced step should over-bound")
    rep = {"dstar": [str(x) for x in d], "H_missing_spec": [str(x) for x in H], "states_overbound": bad,
           "negative_reduced_cost_edges": neg, "H_induced_tower": [str(x) for x in Ht],
           "H_overpriced_spec": [str(x) for x in H2]}
    return rep


# ---------------------------------------------------------------- section 6: random graphs
def random_graph(rng, n, rational):
    E = []
    # ensure co-reachability: random spanning in-tree to goal 0
    for s in range(1, n):
        p = rng.randrange(0, s)
        E.append((s, p, F(rng.randint(1, 4), rng.choice([1, 2, 3]) if rational else 1)))
    for _ in range(rng.randint(n, 3 * n)):
        u, v = rng.randrange(1, n), rng.randrange(0, n)
        if u != v:
            E.append((u, v, F(rng.randint(1, 4), rng.choice([1, 2, 3]) if rational else 1)))
    return E


def section_random(seed=777, trials=300):
    rng = random.Random(seed)
    cnt = {"trials": 0, "order_dependent": 0, "lp_strictly_better_than_best_order": 0, "tower_exact": 0,
           "floor_pot_invalid": 0, "floor_input_loss_gt_layers_over_D": 0, "floor_input_beats_exact": 0}
    worst_gap = (F(0), None)
    for t in range(trials):
        n = rng.randint(5, 9)
        rational = (t % 2 == 1)
        E = random_graph(rng, n, rational)
        Q = [[0] + [rng.randrange(1, 3) for _ in range(n - 1)] for _ in range(3)]  # goal alone in class 0
        d = dist_to_goals(n, [0], E)
        sums = []
        for perm in itertools.permutations(range(3)):
            H, res, hs, ok, why = tower(n, [0], E, [Q[p] for p in perm])
            need(ok, "random tower failed")
            need(is_consistent(n, [0], E, H) and all(H[s] <= d[s] for s in range(n)), "random tower invalid")
            dres = dist_to_goals(n, [0], res)
            need(all(d[s] - H[s] == dres[s] for s in range(n)), "random identity fails")
            zero = all(min(w for u, v, w in res if u == s) == 0 for s in range(1, n))
            need(zero == (H == d), "random iff fails")
            sums.append(sum(H))
            if H == d:
                cnt["tower_exact"] += 1
        cnt["trials"] += 1
        if len(set(sums)) > 1:
            cnt["order_dependent"] += 1
        if t < 80:  # exact LP is slower; cap
            val, _ = lp_optimum_feature_span(n, [0], E, Q)
            need(val >= max(sums), "LP below a feasible tower value")
            if val > max(sums):
                cnt["lp_strictly_better_than_best_order"] += 1
                if val - max(sums) > worst_gap[0]:
                    worst_gap = (val - max(sums), {"n": n, "lp": str(val), "best_tower": str(max(sums))})
        # rounding on rational graphs
        if rational:
            for D in (1, 2):
                Hp, _, _, okp, _ = tower(n, [0], E, Q, "floor_pot", D)
                if not okp:
                    cnt["floor_pot_invalid"] += 1
                He, _, _, _, _ = tower(n, [0], E, Q)
                Hi, _, _, oki, _ = tower(n, [0], E, Q, "floor_input", D)
                need(oki and is_consistent(n, [0], E, Hi), "floor_input invalid on random")
                if any(He[s] - Hi[s] > F(3 * (n - 1), D) for s in range(n)):
                    cnt["floor_input_loss_gt_layers_over_D"] += 1
                if any(Hi[s] > He[s] for s in range(n)):
                    cnt["floor_input_beats_exact"] += 1
    cnt["worst_lp_gap"] = (str(worst_gap[0]), worst_gap[1])
    return cnt


SEED = 777
TRIALS = 300


def headline(R):
    """Compare the headline numbers named in VERDICTS.md; any mismatch raises."""
    team = R["1_2_tower_instances"]["team_sym"]
    tw = team["towers"]
    need(team["sum_dstar"] == "124", "team instance optimum is not 124")
    need(team["single[pi_x]"] == "64" and team["single+zsl[pi_x]"] == "64", "baseline pi_x is not 64")
    need(team["single[pi_y]"] == "84", "baseline pi_y is not 84")
    need(tuple(tw["pi_x->pi_y"]) == ("112", False), "2-layer tower is not 112")
    need(tuple(tw["pi_x->pi_y->pi_imb"]) == ("124", True), "3-layer tower is not exact 124")
    sums = [int(v[0]) for v in tw.values()]
    need(len(sums) == 12, "expected 12 ordered towers")
    hard = R["1_2_tower_instances"]["repo2_hardin"]
    need(hard["towers"]["pi_used->pi_low2"][0] == "114", "hardin tower is not 114")
    need(hard["single+zsl[pi_used]"] == "237/2", "hardin zeroSelfLoop composition is not 237/2")
    need(F(114) < F(237, 2), "114 should be below 237/2")
    r3 = R["1_2_tower_instances"]["repo3_cyclic_switch"]
    r3_vals = [int(v[0]) for v in r3["towers"].values()]
    r3_max, r3_min = max(r3_vals), min(r3_vals)
    r3_lp = r3["LP_opt{pi_d1,pi_d2,pi_sum_parity}"]
    need(r3["sum_dstar"] == "80", "repo instance 3 truth is not 80")
    need(r3_max == 60, "repo instance 3 best tower is not 60")
    need(r3_lp == "68", "repo instance 3 LP over the same quotients is not 68")
    soko = R["1_2_tower_instances"]["repo1_soko"]
    need(soko["sum_dstar"] == "155" and all(v[1] for v in soko["towers"].values()), "soko not exact 155")
    opt = R["3_optimality_theorem"]["stats"]
    rep = opt["repair: no zero cycle & delta(sink)=inf"]
    need(dict(rep) == {"cases": 10272, "iff_fail": 0}, "optimality repair did not hold on 10272 cases")
    need(opt["team: c>0 & coreachable"]["iff_fail"] == 0, "team hypothesis set has a failure")
    need(R["6_random"]["trials"] == TRIALS, "random trial count")
    return (f"PR5 instance 64/112/124 (single quotients 64, 84), 12 orders {min(sums)} to {max(sums)}, "
            f"hardin 114 < 237/2, repo3 best {r3_max} (orders {r3_min} to {r3_max}) LP {r3_lp} truth "
            f"{r3['sum_dstar']}, optimality repair 0 failures in {rep['cases']}, seed {SEED}")


def main():
    cert = cert_path()
    print(f"seed {SEED}")
    RESULTS["1_2_tower_instances"] = section_tower(cert)
    RESULTS["3_optimality_theorem"] = section_optimality()
    RESULTS["4_rounding"] = section_rounding(cert)
    RESULTS["5_missing_step"] = section_missing_step()
    RESULTS["6_random"] = section_random(SEED, TRIALS)
    print(json.dumps(RESULTS, indent=1, default=str))
    print("PEELING_TOWER_CHECK OK: " + headline(RESULTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
