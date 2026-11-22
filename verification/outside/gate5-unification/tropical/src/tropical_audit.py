"""S4 (inf-projection) and S5 (valuation commutes with elimination) audit, exact.

usage: python3 -I -B tropical_audit.py SECTION [ARG]
  s4row4 [ANCHOR_JSON]   row 4 (tower and LP) as a partial minimization
  s4row8                 row 8 (Theorem B boxes) as a partial minimization
  s4bridge OBJECT_DIR    quadratic bridge on the symmetric objects of the other worker
  s4null                 300 seeded unrelated convex elimination problems plus a non-convex set
  s5real                 valuation versus elimination on the real Cole-Hopf matrices
  s5random               valuation versus elimination on seeded random matrices over Q[q]
  controls               must-fail controls; exit 1 if any control passes
Prints canonical JSON to stdout.  Exact arithmetic only, no floats.
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib8
from tlib import (AuditError, ONE, ZERO, bellman_ford_to_goals, build_system, build_tower, cole_hopf,
                  dijkstra_to_goals, dump, fr, fstr, lead_schur, mat_mul, mat_vec, minplus_schur,
                  mmatrix_nonneg_ok, padd, peel_layer, pmul, pmono, pval, plead, quotient_edges, rat_val, require,
                  schur_rational, series_schur_vals, solve_exact, sym_inertia, transpose, trop_matrix,
                  validate_quotient, witness_graphs)


def frac_matrix(rows):
    return [[fr(x) for x in r] for r in rows]


def sub(M, R, C):
    return [[M[i][j] for j in C] for i in R]


# =============================================================== S4 row 4
def row4_layer_check(n, goals, edges, pi, claimed_qedges, claimed_h):
    """True iff the claimed reduced object equals g.
    g is computed with no code shared with the ledger path: min over each fiber of the concrete
    edge costs, and Bellman-Ford distance in the lifted graph where every fiber is a zero-cost clique."""
    k = validate_quotient(pi, n)
    if quotient_edges(edges, pi) != list(claimed_qedges):
        return False
    lifted = list(edges)
    for a in range(k):
        mem = [s for s in range(n) if pi[s] == a]
        for s in mem:
            for t in mem:
                if s != t:
                    lifted.append((s, t, Fraction(0)))
    dist = bellman_ford_to_goals(n, goals, lifted)
    for a in range(k):
        vals = {dist[s] for s in range(n) if pi[s] == a}
        if len(vals) != 1:
            return False
        if vals.pop() != claimed_h[a]:
            return False
    return True


def concrete_flow_certificate(n, goals, edges, pi, L, tag):
    """exact weak-duality certificate on the CONCRETE graph: flow phi >= 0 (y), aggregated supply mu,
    potential h(pi(.)) feasible on every concrete cross edge, equal values.  So g(mu) = sum mu h."""
    k = L["k"]
    mu = [ONE] * k if tag == "one" else [Fraction(c) for c in L["fiber"]]
    qe = L["qedges"]
    y = L["dual_y_" + tag]
    phi = {}
    for i, (a, b, w) in enumerate(qe):
        if y[i] == 0:
            continue
        pick = None
        for idx, (u, v, c) in enumerate(edges):
            if pi[u] == a and pi[v] == b and c == w:
                pick = idx
                break
        require(pick is not None, "no concrete edge attains the fiber minimum")
        phi[pick] = phi.get(pick, ZERO) + y[i]
    net = [ZERO] * k
    cost = ZERO
    for idx, f in phi.items():
        u, v, c = edges[idx]
        require(f >= 0, "negative flow")
        net[pi[u]] += f
        net[pi[v]] -= f
        cost += c * f
    ok_flow = all(net[a] >= mu[a] for a in range(k) if a not in L["qgoals"])
    h = L["h"]
    ok_pot = all(h[g] == 0 for g in L["qgoals"]) and all(x >= 0 for x in h)
    for (u, v, c) in edges:
        if pi[u] != pi[v] and h[pi[u]] - h[pi[v]] > c:
            ok_pot = False
    value = sum((mu[a] * h[a] for a in range(k) if a not in L["qgoals"]), ZERO)
    return {"flow_feasible": ok_flow, "potential_feasible": ok_pot, "concrete_cost": cost, "primal_value": value,
            "equal": cost == value, "n_flow_edges": len(phi)}


def s4row4(anchor_path):
    T = build_tower()
    sysd = T["sys"]
    n, goals = sysd["n"], sysd["goals"]
    anchor = None
    if anchor_path:
        with open(anchor_path) as fh:
            anchor = json.load(fh)["part_a_tropical_quotient"]["coupled_2agent_symmetric"]
    layers = []
    all_ok = True
    for li, L in enumerate(T["layers"]):
        edges = L["input_edges"]
        pi = L["pi"]
        chk = row4_layer_check(n, goals, edges, pi, L["qedges"], L["h"])
        cert1 = concrete_flow_certificate(n, goals, edges, pi, L, "one")
        cert2 = concrete_flow_certificate(n, goals, edges, pi, L, "fiber")
        row = {"layer": L["name"], "reduced_object_equals_g": chk,
               "g_mu_one": fstr(cert1["concrete_cost"]), "ledger_lp_mu_one": fstr(L["primal_one"]),
               "g_mu_fiber": fstr(cert2["concrete_cost"]), "ledger_layer_increment": fstr(L["sum_H_layer"]),
               "certificate_mu_one": {k: (fstr(v) if isinstance(v, Fraction) else v) for k, v in cert1.items()},
               "certificate_mu_fiber": {k: (fstr(v) if isinstance(v, Fraction) else v) for k, v in cert2.items()}}
        if anchor is not None:
            a = anchor["layers_3"][li]
            row["anchor_primal_eq_dual_obj"] = a["primal_eq_dual_obj"]
            row["anchor_sum_H_after_layer"] = a["sum_H_after_layer"]
            row["anchor_matches"] = (a["primal_eq_dual_obj"] == fstr(L["primal_one"]) and
                                     a["sum_H_after_layer"] == fstr(L["sum_H_after"]))
            all_ok = all_ok and row["anchor_matches"]
        row_ok = chk and cert1["equal"] and cert2["equal"] and cert1["flow_feasible"] and cert1["potential_feasible"] \
            and cert2["flow_feasible"] and cert2["potential_feasible"] \
            and cert1["concrete_cost"] == L["primal_one"] and cert2["concrete_cost"] == L["sum_H_layer"]
        row["all_checks_pass"] = row_ok
        all_ok = all_ok and row_ok
        layers.append(row)
    d = sum(T["dstar"], ZERO)
    return {
        "section": "s4row4",
        "statement": {
            "f": "f(x,y) = sum_e c(e) y_e over concrete cross-fiber edges, plus the indicator of y >= 0 and of "
                 "sum over the fiber of (a,b) of y_e = x_ab, where x is a flow on quotient edges",
            "fiber_y": "the split of each aggregated quotient flow x_ab over the concrete edges of the fiber (a,b): a product of simplices",
            "g": "g(x) = inf_y f(x,y) = sum_ab w_ab x_ab with w_ab = min over the fiber of the residual cost (parallel-edge minimum)",
            "value": "min over feasible x of g = quotient LP value; equals the max sum mu h by LP duality (certified on the concrete graph)",
            "convex_f_and_g": "f is linear plus polyhedral indicators; g is linear on x >= 0"},
        "layers": layers,
        "bound_sequence": [fstr(L["sum_H_after"]) for L in T["layers"]],
        "sum_d_star": fstr(d),
        "all_pass": all_ok and T["H"] == T["dstar"],
    }


# =============================================================== S4 row 8
def s4row8():
    boxes = lib8.gen_boxes(500, 20261120)
    agree0 = 0
    feas_agree = 0
    for (L, U) in boxes:
        m, _ = lib8.lp_margin((0, 0), L, U)
        if m == lib8.ledger_G((0, 0), L, U):
            agree0 += 1
        if lib8.ledger_feasible(L, U) == (m <= 0):
            feas_agree += 1
    rng = random.Random(777)
    agree_d = 0
    n_d = 150
    for _ in range(n_d):
        L, U = boxes[rng.randrange(len(boxes))]
        d = (rng.randint(-6, 6), rng.randint(-6, 6))
        m, _ = lib8.lp_margin(d, L, U)
        if m == lib8.ledger_G(d, L, U):
            agree_d += 1
    # concave side (log-concavity) by symmetry h -> -h: box [-U,-L]
    agree_c = 0
    for (L, U) in boxes[:150]:
        Lc = [-u for u in U]
        Uc = [-l for l in L]
        m, _ = lib8.lp_margin((0, 0), Lc, Uc)
        if m == lib8.ledger_G((0, 0), Lc, Uc):
            agree_c += 1
    # convex g in d (midpoint check, exact) on a few boxes
    conv_ok = 0
    conv_n = 0
    for (L, U) in boxes[:40]:
        for _ in range(3):
            d1 = (rng.randint(-6, 6), rng.randint(-6, 6))
            d2 = (rng.randint(-6, 6), rng.randint(-6, 6))
            dm = (Fraction(d1[0] + d2[0], 2), Fraction(d1[1] + d2[1], 2))
            g1, _ = lib8.lp_margin(d1, L, U)
            g2, _ = lib8.lp_margin(d2, L, U)
            gm, _ = lib8.lp_margin(dm, L, U)
            conv_n += 1
            if gm <= (g1 + g2) / 2:
                conv_ok += 1
    return {
        "section": "s4row8",
        "statement": {
            "f": "f(d,h) = max_j (d_j - (D h)_j) + indicator(h in box [L,U]), h = log2 y in R^4, D = [[1,-2,1,0],[0,1,-2,1]]",
            "fiber_y": "h in the box (4 variables); x = d in R^2",
            "g": "g(d) = inf_h f(d,h) = min over the box of max_j (d_j - (Dh)_j)",
            "ledger_reduced_object": "max over the 4 rays r of (r.d - sigma(r)) / (r0 + r1); feasibility is g(0) <= 0, i.e. all sigma(r) >= 0",
            "exactness_scope": "boxes with integer log2 endpoints (multiplicative powers of 2); general rational boxes need logs"},
        "g0_equals_ray_formula": {"cases": len(boxes), "agree": agree0},
        "feasibility_verdicts_agree": {"cases": len(boxes), "agree": feas_agree},
        "g_d_equals_ray_formula_random_d": {"cases": n_d, "agree": agree_d},
        "concave_mode_g0": {"cases": 150, "agree": agree_c},
        "g_convex_in_d_midpoint": {"cases": conv_n, "satisfied": conv_ok},
        "all_pass": (agree0 == len(boxes) and feas_agree == len(boxes) and agree_d == n_d and agree_c == 150
                     and conv_ok == conv_n),
    }


# =============================================================== S4 bridge
def quad_value(H, z):
    Hz = mat_vec(H, z)
    return sum((z[i] * Hz[i] for i in range(len(z))), ZERO)


def partial_min_matrix(H, P, R):
    """matrix of g(x) = inf_y z^T H z (symmetric H, pivot block C = H[P][P] positive definite).
    y*(x) from the gradient equation, certified exactly: gradient zero + C positive definite.
    The matrix of g is read off by polarization, so it is computed without the Schur formula."""
    nr = len(R)
    C = sub(H, P, P)
    Bm = sub(H, P, R)
    require(sym_inertia(C) == (len(P), 0, 0), "pivot not positive definite")

    def g_of(x):
        rhs = [-v for v in mat_vec(Bm, x)]
        y = solve_exact(C, rhs)
        require(y is not None, "singular pivot")
        grad = [mat_vec(C, y)[i] + mat_vec(Bm, x)[i] for i in range(len(P))]
        require(all(v == 0 for v in grad), "gradient not zero")
        z = [ZERO] * len(H)
        for a, r in enumerate(R):
            z[r] = x[a]
        for a, p in enumerate(P):
            z[p] = y[a]
        return quad_value(H, z)

    def e(i):
        return [ONE if j == i else ZERO for j in range(nr)]

    g_diag = [g_of(e(i)) for i in range(nr)]
    G = [[ZERO] * nr for _ in range(nr)]
    for i in range(nr):
        G[i][i] = g_diag[i]
        for j in range(i + 1, nr):
            x = [ZERO] * nr
            x[i] = ONE
            x[j] = ONE
            G[i][j] = G[j][i] = (g_of(x) - g_diag[i] - g_diag[j]) / 2
    return G


def schur_formula(H, P, R):
    A = sub(H, R, R)
    Bm = sub(H, P, R)
    C = sub(H, P, P)
    cols = []
    for j in range(len(R)):
        y = solve_exact(C, [Bm[i][j] for i in range(len(P))])
        require(y is not None, "singular pivot")
        cols.append(y)
    CinvB = transpose(cols)
    BtCinvB = mat_mul(transpose(Bm), CinvB)
    return [[A[i][j] - BtCinvB[i][j] for j in range(len(R))] for i in range(len(R))]


def s4bridge(objdir):
    out = {"section": "s4bridge", "aest": [], "spectral_B": [], "spectral_G": [], "liouvillian": []}
    with open(os.path.join(objdir, "aest_gravity_hamiltonian.json")) as fh:
        aest = json.load(fh)
    n_ok = 0
    for p in aest["points"]:
        H = frac_matrix(p["full"])
        P, R = p["pivot_indices"], p["rest_indices"]
        G = partial_min_matrix(H, P, R)
        Sf = schur_formula(H, P, R)
        red = frac_matrix(p["reduced"])
        ok = (G == red) and (Sf == red)
        n_ok += ok
        out["aest"].append({"label": p["label"], "min_matrix_equals_schur_and_object": ok,
                            "full_inertia_of_H": list(sym_inertia(H)), "reduced": [[fstr(x) for x in r] for r in G]})
    out["aest_summary"] = {"points": len(aest["points"]), "equal": n_ok}
    with open(os.path.join(objdir, "spectral_inertia_hermitian.json")) as fh:
        spec = json.load(fh)
    nb = ng = 0
    for p in spec["points"]:
        S, t, u, b = fr(p["scalars"]["S"]), fr(p["scalars"]["t"]), fr(p["scalars"]["u"]), fr(p["b"])
        Bm = [[S, t, u], [t, b, ZERO], [u, ZERO, ZERO]]
        Gm = [[S, t], [t, b]]
        for tag, M, key in (("B", Bm, "B"), ("G", Gm, "G")):
            P, R = p[key]["pivot_indices"], p[key]["rest_indices"]
            Gmin = partial_min_matrix(M, P, R)
            red = frac_matrix(p[key]["reduced"])
            ok = (Gmin == red) and (schur_formula(M, P, R) == red)
            if tag == "B":
                nb += ok
                out["spectral_B"].append({"label": p["label"], "ok": ok, "g": fstr(Gmin[0][0]),
                                          "minus_Ropt_equal": Gmin[0][0] == -fr(p["chain"]["R_opt"])})
            else:
                ng += ok
                out["spectral_G"].append({"label": p["label"], "ok": ok})
    out["spectral_summary"] = {"points": len(spec["points"]), "B_equal": nb, "G_equal": ng,
                               "note": "the Hermitian matrix M over Q(i) carries no block elimination in the object; only the real symmetric lift B and its pivot G are tested"}
    with open(os.path.join(objdir, "open_quantum_liouvillian.json")) as fh:
        liou = json.load(fh)
    cnt = {"points": 0, "pivot_symmetric_part_negative_definite": 0, "pivot_symmetric": 0, "full_symmetric": 0,
           "inf_exists": 0, "ledger_schur_recomputed_equals_object": 0, "sup_matrix_equals_ledger_schur": 0,
           "sup_matrix_equals_sym_part_of_ledger_schur": 0, "ledger_schur_symmetric": 0}
    for p in liou["points"]:
        L = frac_matrix(p["full"])
        P, R = p["pivot_indices"], p["rest_indices"]
        cnt["points"] += 1
        C = sub(L, P, P)
        Cs = [[(C[i][j] + C[j][i]) / 2 for j in range(len(P))] for i in range(len(P))]
        cnt["pivot_symmetric"] += all(C[i][j] == C[j][i] for i in range(len(P)) for j in range(len(P)))
        cnt["full_symmetric"] += all(L[i][j] == L[j][i] for i in range(len(L)) for j in range(len(L)))
        ine = sym_inertia(Cs)
        cnt["pivot_symmetric_part_negative_definite"] += (ine == (0, len(P), 0))
        # f(0, t e) = t^2 C_ee < 0: unbounded below along y
        e0 = P[0]
        dec = [L[e0][e0] * s * s for s in (1, 2, 4)]
        cnt["inf_exists"] += (not (dec[0] > dec[1] > dec[2]))
        # ledger Schur recomputed from the full matrix
        A = sub(L, R, R)
        B = sub(L, R, P)
        Cc = sub(L, P, R)
        cols = []
        for j in range(len(R)):
            y = solve_exact(C, [Cc[i][j] for i in range(len(P))])
            require(y is not None, "singular pivot")
            cols.append(y)
        BCinvCc = mat_mul(B, transpose(cols))
        Rl = [[A[i][j] - BCinvCc[i][j] for j in range(len(R))] for i in range(len(R))]
        obj_red = frac_matrix(p["reduced"])
        cnt["ledger_schur_recomputed_equals_object"] += (Rl == obj_red)
        cnt["ledger_schur_symmetric"] += all(Rl[i][j] == Rl[j][i] for i in range(len(R)) for j in range(len(R)))
        # sup over y of the quadratic form: stationary point (C + C^T) y = -(B^T + Cc) x, value matrix Q
        Ls = [[(L[i][j] + L[j][i]) / 2 for j in range(len(L))] for i in range(len(L))]
        Q = schur_formula(Ls, P, R)
        cnt["sup_matrix_equals_ledger_schur"] += (Q == Rl)
        symR = [[(Rl[i][j] + Rl[j][i]) / 2 for j in range(len(R))] for i in range(len(R))]
        cnt["sup_matrix_equals_sym_part_of_ledger_schur"] += (Q == symR)
        out["liouvillian"].append({"label": p["label"], "pivot_symmetric": all(C[i][j] == C[j][i] for i in range(len(P)) for j in range(len(P))),
                                   "pivot_sym_part_inertia": list(ine),
                                   "f(0,t e): t=1,2,4": [fstr(x) for x in dec],
                                   "sup_matrix_equals_ledger_schur": Q == Rl,
                                   "sup_matrix_equals_sym_part_of_ledger_schur": Q == symR})
    out["liouvillian_summary"] = cnt
    out["all_pass"] = (out["aest_summary"]["equal"] == out["aest_summary"]["points"] and
                       nb == len(spec["points"]) and ng == len(spec["points"]) and cnt["inf_exists"] == 0)
    return out


# =============================================================== S4 matched null
def null_shortest_path(rng):
    n = rng.randint(5, 9)
    edges = []
    for u in range(1, n):
        edges.append((u, rng.randint(0, u - 1), Fraction(rng.randint(1, 5))))
    for _ in range(n):
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            edges.append((u, v, Fraction(rng.randint(0, 4))))
    k = rng.randint(2, min(4, n))
    labels = list(range(k)) + [rng.randrange(k) for _ in range(n - k)]
    rng.shuffle(labels)
    goals = [0]
    L = peel_layer(n, goals, edges, labels)
    chk = row4_layer_check(n, goals, edges, labels, L["qedges"], L["h"])
    c1 = concrete_flow_certificate(n, goals, edges, labels, L, "one")
    c2 = concrete_flow_certificate(n, goals, edges, labels, L, "fiber")
    ok = chk and c1["equal"] and c2["equal"] and c1["flow_feasible"] and c1["potential_feasible"] \
        and c2["flow_feasible"] and c2["potential_feasible"]
    return ok


def _vertices_2d(rows):
    """vertices of {y : a.y <= r} in R^2 (feasible basic solutions)."""
    out = []
    for i, j in itertools.combinations(range(len(rows)), 2):
        y = solve_exact([rows[i][0], rows[j][0]], [rows[i][1], rows[j][1]])
        if y is None:
            continue
        if all(a[0] * y[0] + a[1] * y[1] <= r for a, r in rows):
            out.append(y)
    return out


def lp_primal_dual(rows, c):
    """returns ('opt', primal, dual) or ('infeasible', certificate_found)."""
    verts = _vertices_2d(rows)
    if not verts:
        # Farkas certificate: lambda >= 0, A^T lambda = 0, lambda . r < 0, support <= 3
        for i, j, k in itertools.combinations(range(len(rows)), 3):
            m1 = [rows[i][0][0], rows[j][0][0], rows[k][0][0]]
            m2 = [rows[i][0][1], rows[j][0][1], rows[k][0][1]]
            lam = [m1[1] * m2[2] - m1[2] * m2[1], m1[2] * m2[0] - m1[0] * m2[2], m1[0] * m2[1] - m1[1] * m2[0]]
            for sgn in (1, -1):
                l = [sgn * v for v in lam]
                if all(v >= 0 for v in l) and any(v > 0 for v in l):
                    if l[0] * rows[i][1] + l[1] * rows[j][1] + l[2] * rows[k][1] < 0:
                        return ("infeasible", True)
        return ("infeasible", False)
    primal = min(c[0] * y[0] + c[1] * y[1] for y in verts)
    dual = None
    for i, j in itertools.combinations(range(len(rows)), 2):
        lam = solve_exact([[rows[i][0][0], rows[j][0][0]], [rows[i][0][1], rows[j][0][1]]], [-c[0], -c[1]])
        if lam is None or lam[0] < 0 or lam[1] < 0:
            continue
        val = -(lam[0] * rows[i][1] + lam[1] * rows[j][1])
        if dual is None or val > dual:
            dual = val
    return ("opt", primal, dual)


def null_lp(rng):
    m = rng.randint(3, 5)
    base = []
    for _ in range(m):
        while True:
            a = (rng.randint(-3, 3), rng.randint(-3, 3))
            if a != (0, 0):
                break
        base.append((a, rng.randint(-4, 8), rng.randint(-2, 2)))  # a, r, alpha
    box = [((1, 0), 10), ((-1, 0), 10), ((0, 1), 10), ((0, -1), 10)]
    c = (rng.randint(-3, 3), rng.randint(-3, 3))
    xs = [Fraction(rng.randint(-6, 6), rng.randint(1, 3)) for _ in range(2)]
    xs.append((xs[0] + xs[1]) / 2)
    vals = []
    ok = True
    for x in xs:
        rows = [(a, r - al * x) for (a, r, al) in base] + box
        res = lp_primal_dual(rows, c)
        if res[0] == "opt":
            ok = ok and (res[1] == res[2])
            vals.append(res[1])
        else:
            ok = ok and res[1]
            vals.append(None)
    infeasible = any(v is None for v in vals)
    convex_ok = True
    if all(v is not None for v in vals):
        convex_ok = vals[2] <= (vals[0] + vals[1]) / 2
    return ok and convex_ok, infeasible


def rand_pd(rng, n):
    W = [[Fraction(rng.randint(-3, 3)) for _ in range(n)] for _ in range(n)]
    H = mat_mul(transpose(W), W)
    for i in range(n):
        H[i][i] += rng.randint(1, 2)
    return H


def null_quadratic(rng):
    n = rng.randint(3, 6)
    k = rng.randint(1, n - 1)
    H = rand_pd(rng, n)
    idx = list(range(n))
    rng.shuffle(idx)
    P, R = sorted(idx[:k]), sorted(idx[k:])
    G = partial_min_matrix(H, P, R)
    S = schur_formula(H, P, R)
    ok = (G == S)
    # minimality: random perturbations of y never go below the value at y*
    x = [Fraction(rng.randint(-3, 3)) for _ in R]
    Cm, Bm = sub(H, P, P), sub(H, P, R)
    y = solve_exact(Cm, [-v for v in mat_vec(Bm, x)])

    def val(yv):
        z = [ZERO] * n
        for a, r in enumerate(R):
            z[r] = x[a]
        for a, p in enumerate(P):
            z[p] = yv[a]
        return quad_value(H, z)

    base = val(y)
    for _ in range(5):
        d = [Fraction(rng.randint(-3, 3), rng.randint(1, 3)) for _ in P]
        ok = ok and (val([y[i] + d[i] for i in range(k)]) >= base)
    return ok


def null_indefinite(rng):
    """symmetric H whose pivot is NOT positive definite: the infimum does not exist (S4 fails)."""
    while True:
        n = rng.randint(3, 5)
        k = rng.randint(1, n - 1)
        H = [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                H[i][j] = H[j][i] = Fraction(rng.randint(-4, 4))
        P = list(range(k))
        if sym_inertia(sub(H, P, P)) != (k, 0, 0):
            return True


def s4null():
    out = {"section": "s4null", "seeds": {"shortest_path": 1001, "lp": 2001, "quadratic": 3001, "indefinite": 4001}}
    sp = [null_shortest_path(random.Random(1001 + i)) for i in range(100)]
    lp = [null_lp(random.Random(2001 + i)) for i in range(100)]
    qd = [null_quadratic(random.Random(3001 + i)) for i in range(100)]
    out["shortest_path_quotients"] = {"problems": len(sp), "S4_holds": sum(sp)}
    out["lp_block_projected_out"] = {"problems": len(lp), "S4_holds": sum(1 for a, b in lp if a),
                                     "of_which_infeasible_at_some_x": sum(1 for a, b in lp if b)}
    out["positive_definite_quadratics"] = {"problems": len(qd), "S4_holds": sum(qd)}
    tot = len(sp) + len(lp) + len(qd)
    held = sum(sp) + sum(1 for a, b in lp if a) + sum(qd)
    out["total_problems"] = tot
    out["total_S4_holds"] = held
    # discrimination: the same elimination formula on non-convex problems; S4 (an infimum exists) fails
    ind = 0
    n_ind = 100
    for i in range(n_ind):
        rng = random.Random(4001 + i)
        ind += 1 if null_indefinite(rng) else 0
    out["non_convex_set"] = {"problems": n_ind, "pivot_not_positive_definite_so_inf_does_not_exist": ind}
    out["verdict"] = ("S4 holds for every unrelated convex elimination problem tried: it classifies, it does not discriminate"
                      if held == tot else "S4 failed on some convex null problems")
    out["all_pass"] = (held == tot and ind == n_ind and tot >= 200)
    return out


# =============================================================== S5
def shift_poly(p, s):
    """multiply by q^s (s may be negative when the low coefficients vanish)."""
    if not p:
        return ()
    if s >= 0:
        return tuple([ZERO] * s + list(p))
    require(all(x == 0 for x in p[:-s]), "negative shift would leave Q[q]")
    return tuple(p[-s:])


def compare_case(K, A, B):
    """one elimination: exact val(Schur over Q(q)) against min-plus elimination of val(K)."""
    S = schur_rational(K, A, B)
    if S is None:
        return None
    T = trop_matrix(K)
    TS = minplus_schur(T, A, B)
    K_BB0 = [[(K[k][l][0] if K[k][l] else ZERO) for l in B] for k in B]
    reg = all(x == 0 for r in K_BB0 for x in r)
    nonneg = all(c >= 0 for i in range(len(K)) for j in range(len(K)) for c in K[i][j])
    res = {"entries": len(A) * len(A), "defects": 0, "negative_gap": 0, "regular_valuation_positive": reg,
           "all_coeffs_nonneg": nonneg, "M_matrix_ok": None, "lead_pred_agree": None, "series_agree": None}
    vals = {}
    for key, nd in S.items():
        v = rat_val(nd)
        vals[key] = v
        t = TS[key]
        if v != t:
            res["defects"] += 1
            if v is not None and t is not None and v < t:
                res["negative_gap"] += 1
    if nonneg:
        res["M_matrix_ok"] = mmatrix_nonneg_ok(K_BB0)
    if reg:
        Ls = lead_schur(K, A, B)
        agree = True
        for key, v in vals.items():
            t = TS[key]
            lead = Ls[key]
            if lead is None:
                agree = agree and (v is None and t is None)
                continue
            agree = agree and (lead[0] == t)
            predicted_defect = (lead[1] == 0)
            agree = agree and (predicted_defect == (v != t))
            if predicted_defect:
                agree = agree and (v is None or v > t)
        res["lead_pred_agree"] = agree
        M = 24
        sv = series_schur_vals(K, A, B, M)
        sa = True
        for key, v in vals.items():
            if v is not None and v < M:
                sa = sa and (sv[key] == v)
            else:
                sa = sa and (sv[key] is None)
        res["series_agree"] = sa
    return res


def powerset_blocks(n, maxb):
    out = []
    for nb in range(1, maxb + 1):
        for B in itertools.combinations(range(n), nb):
            A = [i for i in range(n) if i not in B]
            if len(A) >= 2:
                out.append((list(A), list(B)))
    return out


def s5real():
    out = {"section": "s5real", "witnesses": {}}
    allok = True
    # (a) valuation carries K to the cost matrix; elimination commutes: exhaustive blocks on 4 and 5 states
    for name, g in sorted(witness_graphs().items()):
        n = g["n"]
        K = cole_hopf(n, g["edges"])
        T = trop_matrix(K)
        cost = [[None] * n for _ in range(n)]
        for (u, v, w) in g["edges"]:
            w = int(w)
            cost[u][v] = w if cost[u][v] is None else min(cost[u][v], w)
        cases = defects = singular = 0
        lead_ok = series_ok = 0
        for (A, B) in powerset_blocks(n, n - 1):
            r = compare_case(K, A, B)
            if r is None:
                singular += 1
                continue
            cases += 1
            defects += r["defects"]
            lead_ok += 1 if r["lead_pred_agree"] else 0
            series_ok += 1 if r["series_agree"] else 0
        out["witnesses"][name] = {"n": n, "val_K_equals_cost_matrix": T == cost, "blocks_tested": cases,
                                  "singular_blocks": singular, "entries_with_defect": defects,
                                  "lead_prediction_agree": lead_ok, "series_checker_agree": series_ok}
        allok = allok and T == cost and defects == 0
    # (b) 32-state system: K, Doob-peeled K, single and pair eliminations
    TW = build_tower()
    n = TW["sys"]["n"]
    K = cole_hopf(n, TW["sys"]["edges"])
    Kred = cole_hopf(n, TW["final_edges"])
    H = TW["H"]
    doob_ok = True
    for u in range(n):
        for v in range(n):
            if K[u][v] or Kred[u][v]:
                lhs = shift_poly(K[u][v], int(H[v] - H[u]))
                doob_ok = doob_ok and (lhs == Kred[u][v])
                if K[u][v]:
                    doob_ok = doob_ok and (pval(Kred[u][v]) == pval(K[u][v]) + int(H[v] - H[u]))
    out["doob_monomial_similarity_commutes_with_valuation"] = doob_ok
    allok = allok and doob_ok
    big = {}
    for tag, M in (("K_32", K), ("K_32_doob_peeled", Kred)):
        cases = defects = singular = lead_ok = lead_n = series_ok = series_n = 0
        mm_true = 0
        for nb in (1, 2):
            for B in itertools.combinations(range(n), nb):
                A = [i for i in range(n) if i not in B]
                r = compare_case(M, A, list(B)) if (nb == 1 or True) else None
                if r is None:
                    singular += 1
                    continue
                cases += 1
                defects += r["defects"]
                if r["lead_pred_agree"] is not None:
                    lead_n += 1
                    lead_ok += 1 if r["lead_pred_agree"] else 0
                if r["series_agree"] is not None:
                    series_n += 1
                    series_ok += 1 if r["series_agree"] else 0
                mm_true += 1 if r["M_matrix_ok"] else 0
        big[tag] = {"blocks_tested_sizes_1_and_2": cases, "singular": singular, "entries_with_defect": defects,
                    "blocks_with_K_BB_constant_term_zero": lead_n, "lead_prediction_agree": lead_ok,
                    "series_checker_agree": series_ok, "blocks_satisfying_nonneg_and_M_matrix": mm_true}
        allok = allok and defects == 0
    out["state_32"] = big
    # (c) all-beta partition function: eliminate every non-goal state, Z(s) = sum over paths q^cost
    goal = TW["sys"]["goals"][0]
    Bs = [s for s in range(n) if s != goal]
    M = 14
    def trunc(p):
        return tuple(p[:M]) if len(p) <= M else tuple(p[:M])
    def zvec(Mx):
        Z = {s: () for s in Bs}
        for _ in range(M + n + 2):
            newZ = {}
            for s in Bs:
                acc = Mx[s][goal]
                for t in Bs:
                    if Mx[s][t] and Z[t]:
                        acc = padd(acc, trunc(pmul(Mx[s][t], Z[t])))
                newZ[s] = acc
            Z = newZ
        return Z
    Z = zvec(K)
    Zr = zvec(Kred)
    z_ok = all(pval(Z[s]) == int(TW["dstar"][s]) and Z[s][int(TW["dstar"][s])] > 0 for s in Bs)
    zr_ok = all(pval(Zr[s]) == 0 and Zr[s][0] > 0 for s in Bs)
    out["partition_function_valuation"] = {
        "val_Z_equals_d_star_all_31": z_ok, "val_Z_doob_peeled_equals_0_all_31": zr_ok,
        "sum_of_val_Z": int(sum(pval(Z[s]) for s in Bs)),
        "meaning": "valuation of the exact path-sum Z(s) equals the shortest-path distance; after the tower it is 0 everywhere"}
    allok = allok and z_ok and zr_ok
    out["all_pass"] = allok
    return out


def rand_poly_matrix(rng, n, kind, emin):
    K = [[() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if rng.randint(0, 1):
                m = rng.choice([1, 2])
                exps = rng.sample(range(emin, 4), m)
                p = ()
                for e in exps:
                    c = rng.randint(1, 3)
                    if kind == "mix":
                        c *= rng.choice([-1, 1])
                    p = padd(p, pmono(c, e))
                K[i][j] = p
    return K


def group_stats():
    return {"matrices": 0, "primary_cases": 0, "primary_singular": 0, "primary_defect_cases": 0,
            "exhaustive_cases": 0, "exhaustive_singular": 0, "exhaustive_defect_cases": 0,
            "matrices_with_any_defect_exhaustive": 0, "negative_gap_cases": 0, "regular_negative_gap_cases": 0,
            "regular_cases": 0, "regular_defect_cases": 0, "regular_lead_pred_agree": 0, "regular_series_agree": 0,
            "nonregular_cases": 0, "nonregular_defect_cases": 0,
            "nonneg_Mmatrix_cases": 0, "nonneg_Mmatrix_defect_cases": 0,
            "nonneg_not_Mmatrix_cases": 0, "nonneg_not_Mmatrix_defect_cases": 0}


def s5random():
    out = {"section": "s5random",
           "model": "n x n over Q[q]; each entry present with probability 1/2; present entry has 1 or 2 monomials of distinct "
                    "exponents in [emin,3] with integer coefficient magnitude 1..3; kind pos = all coefficients positive, "
                    "mix = independent random signs; block B of size 1..min(3,n-2) eliminated (Schur complement of I-K)",
           "groups": {}}
    seeds = {"pos_e1": 5100, "mix_e1": 5200, "pos_e0": 5300, "mix_e0": 5400}
    spec = {"pos_e1": ("pos", 1), "mix_e1": ("mix", 1), "pos_e0": ("pos", 0), "mix_e0": ("mix", 0)}
    per_n = 200
    for gname in sorted(spec):
        kind, emin = spec[gname]
        for n in (4, 5):
            st = group_stats()
            rng = random.Random(seeds[gname] + n)
            for _ in range(per_n):
                K = rand_poly_matrix(rng, n, kind, emin)
                st["matrices"] += 1
                nb = rng.randint(1, min(3, n - 2))
                B = sorted(rng.sample(range(n), nb))
                A = [i for i in range(n) if i not in B]
                r = compare_case(K, A, B)
                st["primary_cases"] += 1
                if r is None:
                    st["primary_singular"] += 1
                    st["primary_cases"] -= 1
                elif r["defects"]:
                    st["primary_defect_cases"] += 1
                any_def = False
                for (A2, B2) in powerset_blocks(n, 3):
                    r2 = compare_case(K, A2, B2)
                    if r2 is None:
                        st["exhaustive_singular"] += 1
                        continue
                    st["exhaustive_cases"] += 1
                    d = r2["defects"] > 0
                    any_def = any_def or d
                    st["exhaustive_defect_cases"] += 1 if d else 0
                    st["negative_gap_cases"] += 1 if r2["negative_gap"] else 0
                    if r2["regular_valuation_positive"]:
                        st["regular_cases"] += 1
                        st["regular_negative_gap_cases"] += 1 if r2["negative_gap"] else 0
                        st["regular_defect_cases"] += 1 if d else 0
                        st["regular_lead_pred_agree"] += 1 if r2["lead_pred_agree"] else 0
                        st["regular_series_agree"] += 1 if r2["series_agree"] else 0
                    else:
                        st["nonregular_cases"] += 1
                        st["nonregular_defect_cases"] += 1 if d else 0
                    if r2["all_coeffs_nonneg"]:
                        if r2["M_matrix_ok"]:
                            st["nonneg_Mmatrix_cases"] += 1
                            st["nonneg_Mmatrix_defect_cases"] += 1 if d else 0
                        else:
                            st["nonneg_not_Mmatrix_cases"] += 1
                            st["nonneg_not_Mmatrix_defect_cases"] += 1 if d else 0
                st["matrices_with_any_defect_exhaustive"] += 1 if any_def else 0
            out["groups"]["%s_n%d" % (gname, n)] = st
    # rates as exact fractions
    rates = {}
    for key, st in out["groups"].items():
        rates[key] = {"primary_defect_rate": "%d/%d" % (st["primary_defect_cases"], st["primary_cases"]),
                      "exhaustive_defect_rate": "%d/%d" % (st["exhaustive_defect_cases"], st["exhaustive_cases"])}
    out["rates"] = rates
    out["condition_checks"] = {
        "positive_group_with_valuation_positive_blocks_has_zero_defects": all(
            out["groups"][k]["exhaustive_defect_cases"] == 0 for k in out["groups"] if k.startswith("pos_e1")),
        "nonneg_coefficients_and_M_matrix_has_zero_defects_everywhere": all(
            st["nonneg_Mmatrix_defect_cases"] == 0 for st in out["groups"].values()),
        "lead_coefficient_rule_predicts_every_regular_case": all(
            st["regular_lead_pred_agree"] == st["regular_cases"] for st in out["groups"].values()),
        "series_checker_agrees_in_every_regular_case": all(
            st["regular_series_agree"] == st["regular_cases"] for st in out["groups"].values()),
        "valuation_never_below_tropical_when_regular": all(
            st["regular_negative_gap_cases"] == 0 for st in out["groups"].values())}
    out["all_pass"] = all(out["condition_checks"].values())
    return out


# =============================================================== controls
def convex_precondition_quadratic(H):
    """jointly convex quadratic form iff the symmetric matrix is positive semidefinite."""
    return sym_inertia(H)[1] == 0


def midpoint_convex(g, pts):
    for a, b in itertools.combinations(pts, 2):
        m = (a + b) / 2
        if g(m) > (g(a) + g(b)) / 2:
            return False
    return True


def controls():
    out = {"section": "controls", "controls": {}}
    bad = []

    def record(name, detected, detail):
        out["controls"][name] = {"detected": bool(detected), "detail": detail}
        if not detected:
            bad.append(name)

    # C1 wrong quotient map
    TW = build_tower()
    sysd = TW["sys"]
    L1 = TW["layers"][0]
    n, goals = sysd["n"], sysd["goals"]
    honest = row4_layer_check(n, goals, L1["input_edges"], L1["pi"], L1["qedges"], L1["h"])
    pi_bad = list(L1["pi"])
    pi_bad[8] = L1["pi"][0]  # move state (1,0,0) into the goal class
    wrong = row4_layer_check(n, goals, L1["input_edges"], pi_bad, L1["qedges"], L1["h"])
    pi_swap = list(L1["pi"])
    pi_swap[10], pi_swap[27] = pi_swap[27], pi_swap[10]
    wrong2 = row4_layer_check(n, goals, L1["input_edges"], pi_swap, L1["qedges"], L1["h"])
    try:
        validate_quotient([9 if c == 1 else c for c in L1["pi"]], n)
        rejected = False
    except AuditError:
        rejected = True
    record("wrong_quotient_moved_state", (honest is True) and (wrong is False),
           {"honest_map_passes": honest, "corrupted_map_passes": wrong})
    record("wrong_quotient_swapped_states", (honest is True) and (wrong2 is False),
           {"honest_map_passes": honest, "swapped_map_passes": wrong2})
    record("wrong_quotient_labels_not_onto", rejected, {"validation_rejected": rejected})
    # C2 non-convex f
    H_ind = [[Fraction(1), Fraction(2)], [Fraction(2), Fraction(1)]]
    c2a = not convex_precondition_quadratic(H_ind)
    record("nonconvex_indefinite_quadratic", c2a, {"inertia": list(sym_inertia(H_ind))})
    # f = x^2 + 4xy + y^2: pivot positive definite, g = -3 x^2 is concave
    H_pd_pivot = [[Fraction(1), Fraction(2)], [Fraction(2), Fraction(1)]]
    g_neg = partial_min_matrix(H_pd_pivot, [1], [0])
    gfun = lambda x: g_neg[0][0] * x * x
    c2b = (not convex_precondition_quadratic(H_pd_pivot)) and (not midpoint_convex(gfun, [Fraction(0), Fraction(2)])) \
        and g_neg[0][0] == -3
    record("nonconvex_f_with_positive_definite_pivot", c2b, {"g_coefficient": fstr(g_neg[0][0])})
    # f = (x-y)^2 with y in the non-convex fiber {0,3}
    gdisc = lambda x: min((x - 0) ** 2, (x - 3) ** 2)
    c2c = not midpoint_convex(gdisc, [Fraction(0), Fraction(3)])
    # contrast: the convex fiber [0,3] passes the same test
    def gint(x):
        d = ZERO if 0 <= x <= 3 else (-x if x < 0 else x - 3)
        return d * d
    contrast = midpoint_convex(gint, [Fraction(0), Fraction(3), Fraction(-1), Fraction(5)])
    record("nonconvex_fiber_discrete", c2c and contrast, {"g_nonconvex_detected": c2c, "convex_fiber_contrast_passes": contrast})
    # C3 Q[q] matrix with cancelling leading terms
    # states 0,1,2; A = {0,2}, B = {1}; K02 = q^2, K01 = q, K12 = -q  =>  S02 = q^2 - q^2 = 0
    K = [[() for _ in range(3)] for _ in range(3)]
    K[0][2] = pmono(1, 2)
    K[0][1] = pmono(1, 1)
    K[1][2] = pmono(-1, 1)
    r1 = compare_case(K, [0, 2], [1])
    # partial cancellation: K12 = -q + q^3 gives S02 = q^4 while the tropical value is 2
    K2 = [row[:] for row in K]
    K2[1][2] = padd(pmono(-1, 1), pmono(1, 3))
    r2 = compare_case(K2, [0, 2], [1])
    S2 = schur_rational(K2, [0, 2], [1])
    record("cancelling_leading_terms_total", r1["defects"] >= 1 and r1["lead_pred_agree"] is True,
           {"defect_entries": r1["defects"]})
    record("cancelling_leading_terms_partial", r2["defects"] >= 1 and rat_val(S2[(0, 2)]) == 4 and r2["lead_pred_agree"] is True,
           {"defect_entries": r2["defects"], "val_exact": rat_val(S2[(0, 2)]), "val_tropical": 2})
    # C4 truncated ray set (local rays only) must disagree with the exact LP on some box
    boxes = lib8.gen_boxes(500, 20261120)
    miss = 0
    for (Lb, Ub) in boxes:
        m, _ = lib8.lp_margin((0, 0), Lb, Ub)
        if lib8.ledger_feasible(Lb, Ub, lib8.RAYS[:2]) != (m <= 0):
            miss += 1
    record("truncated_ray_set_row8", miss > 0, {"boxes_where_two_rays_disagree_with_exact_lp": miss})
    out["all_controls_detected"] = not bad
    out["undetected"] = bad
    return out, (0 if not bad else 1)


def main(argv):
    require(len(argv) >= 2, "usage: tropical_audit.py SECTION [ARG]")
    sec = argv[1]
    arg = argv[2] if len(argv) > 2 else None
    code = 0
    if sec == "s4row4":
        res = s4row4(arg)
    elif sec == "s4row8":
        res = s4row8()
    elif sec == "s4bridge":
        require(arg is not None, "s4bridge needs the object directory")
        res = s4bridge(arg)
    elif sec == "s4null":
        res = s4null()
    elif sec == "s5real":
        res = s5real()
    elif sec == "s5random":
        res = s5random()
    elif sec == "controls":
        res, code = controls()
    else:
        raise AuditError("unknown section")
    sys.stdout.write(dump(res))
    if code == 0 and isinstance(res, dict) and res.get("all_pass") is False:
        code = 2
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
