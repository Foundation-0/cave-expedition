"""Emit one exact object file to stdout as canonical JSON.
usage: python3 -I -B make_objects.py {tower|cole_hopf|lp|farkas}
"""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tlib import (ZERO, build_tower, build_system, cole_hopf, dump, fstr, kmatrix_json, pjson, pval,
                  trop_matrix, witness_graphs, require, peel_layer, dijkstra_to_goals)
import lib8


def num(x):
    if x is None:
        return None
    x = Fraction(x)
    return int(x) if x.denominator == 1 else fstr(x)


def edge_list(es):
    return [[u, v, num(w)] for (u, v, w) in es]


def obj_tower():
    T = build_tower()
    sysd = T["sys"]
    layers = []
    for L in T["layers"]:
        n = sysd["n"]
        out_min = [None] * n
        for (u, v, c) in L["reduced_edges"]:
            if out_min[u] is None or c < out_min[u]:
                out_min[u] = c
        defects = [0 if (s in sysd["goals"] or out_min[s] is None) else out_min[s] for s in range(n)]
        layers.append({
            "name": L["name"], "quotient_map": L["pi"], "quotient_states": L["k"], "fiber_sizes": L["fiber"],
            "quotient_goals": L["qgoals"], "quotient_edges_min_residual_cost": edge_list(L["qedges"]),
            "potential_h_on_quotient": [num(x) for x in L["h"]],
            "sum_H_after_layer_concrete": num(L["sum_H_after"]),
            "layer_increment_concrete": num(L["sum_H_layer"]),
            "max_tropical_defect_after_layer": num(max(defects)),
            "nonzero_defect_states": sum(1 for s in range(n) if s not in sysd["goals"] and defects[s] > 0),
        })
    return {
        "object": "tropical_tower_32_state",
        "provenance": "clean-room rebuild from the docstring of tropical_quotient_sheaf_bridge.py (symmetric variant)",
        "n_states": sysd["n"], "state_index": "8x + 2y + m", "goals": sysd["goals"],
        "edges": edge_list(sysd["edges"]), "layers": layers,
        "H_total": [num(x) for x in T["H"]], "d_star": [num(x) for x in T["dstar"]],
        "sum_H_total": num(sum(T["H"], ZERO)), "sum_d_star": num(sum(T["dstar"], ZERO)),
        "H_equals_d_star": T["H"] == T["dstar"],
    }


def obj_cole_hopf():
    out = {"object": "cole_hopf_matrices_over_Q[q]", "convention": "K_uv = sum over edges u->v of q^cost; poly = coefficients low to high",
           "witnesses": {}}
    for name, g in sorted(witness_graphs().items()):
        K = cole_hopf(g["n"], g["edges"])
        out["witnesses"][name] = {"n": g["n"], "goals": g["goals"], "quotient_map": g["pi"],
                                  "edges": edge_list(g["edges"]), "K": kmatrix_json(K),
                                  "tropicalization": [[trop_matrix(K)[i][j] for j in range(g["n"])] for i in range(g["n"])]}
    T = build_tower()
    n = T["sys"]["n"]
    K = cole_hopf(n, T["sys"]["edges"])
    Kred = cole_hopf(n, T["final_edges"])
    for tag, M in (("K_32", K), ("K_32_doob_peeled", Kred)):
        tm = trop_matrix(M)
        out[tag] = {"n": n, "K": kmatrix_json(M),
                    "tropicalization_nonINF": [[i, j, tm[i][j]] for i in range(n) for j in range(n) if tm[i][j] is not None]}
    return out


def obj_lp():
    T = build_tower()
    sysd = T["sys"]
    out = {"object": "quotient_LP_behind_64_to_124",
           "lp_primal": "max sum_A mu_A h_A  s.t.  h_a - h_b <= w_ab on quotient edges, h = 0 on goals",
           "lp_dual": "min sum_e w_e y_e s.t. out(A) - in(A) >= mu_A on non-goal A, y >= 0",
           "layers": []}
    # single quotient LPs (first layer on the original costs)
    singles = []
    for name, pi in sysd["pis"]:
        L = peel_layer(sysd["n"], sysd["goals"], sysd["edges"], pi)
        singles.append({"quotient": name, "sum_H_concrete": num(L["sum_H_layer"]),
                        "lp_value_mu_one": num(L["primal_one"]), "lp_value_mu_fiber": num(L["primal_fiber"])})
    out["single_quotient_bounds_on_original_costs"] = singles
    for L in T["layers"]:
        out["layers"].append({
            "name": L["name"], "mu_one_value_primal": num(L["primal_one"]), "mu_one_value_dual": num(L["dual_one"]),
            "mu_fiber_value_primal": num(L["primal_fiber"]), "mu_fiber_value_dual": num(L["dual_fiber"]),
            "h": [num(x) for x in L["h"]], "quotient_edges": edge_list(L["qedges"]),
            "dual_flow_mu_one": [num(x) for x in L["dual_y_one"]],
            "dual_flow_mu_fiber": [num(x) for x in L["dual_y_fiber"]],
            "sum_H_after_layer": num(L["sum_H_after"])})
    out["bound_sequence_concrete_sum"] = [num(L["sum_H_after"]) for L in T["layers"]]
    out["true_sum_d_star"] = num(sum(T["dstar"], ZERO))
    return out


def obj_farkas():
    boxes = lib8.gen_boxes(500, 20261120)
    rows = []
    n_feas = 0
    n_nonlocal_only = 0
    for (L, U) in boxes:
        sig = {"%d,%d" % r: lib8.sigma(r, L, U) for r in lib8.RAYS}
        margin, harg = lib8.lp_margin((0, 0), L, U)
        feas = lib8.ledger_feasible(L, U)
        require(feas == (margin <= 0), "ledger rays disagree with exact LP")
        failed = [r for r in lib8.RAYS if lib8.sigma(r, L, U) < 0]
        row = {"L": L, "U": U, "sigma": sig, "exact_lp_margin_g0": fstr(margin), "feasible": feas}
        if feas:
            n_feas += 1
            row["primal_witness_h"] = [fstr(x) for x in harg]
        else:
            r0 = min(failed, key=lambda r: (lib8.sigma(r, L, U), r))
            row["farkas_dual_ray_u"] = list(r0)
            row["farkas_dual_value_sigma"] = lib8.sigma(r0, L, U)
            if all(r in ((2, 1), (1, 2)) for r in failed):
                n_nonlocal_only += 1
        rows.append(row)
    return {"object": "theorem_B_four_ray_farkas_boxes", "D": lib8.D, "rays": [list(r) for r in lib8.RAYS],
            "units": "log2 exponents; multiplicative box is [2^L_k, 2^U_k]; ray fails iff sigma < 0",
            "generator": "random.Random(20261120), randint(-6,6) x4 then randint(0,4) x4, 500 cases",
            "n_cases": len(rows), "n_feasible": n_feas, "n_nonlocal_only_obstructions": n_nonlocal_only, "boxes": rows}


def main(argv):
    require(len(argv) == 2, "usage: make_objects.py {tower|cole_hopf|lp|farkas}")
    fn = {"tower": obj_tower, "cole_hopf": obj_cole_hopf, "lp": obj_lp, "farkas": obj_farkas}.get(argv[1])
    require(fn is not None, "unknown object")
    sys.stdout.write(dump(fn()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
