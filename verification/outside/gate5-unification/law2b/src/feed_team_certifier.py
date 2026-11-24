#!/usr/bin/env python3
"""feed_team_certifier.py: feed the specs written by law2b_check.py to the team's certify_transformational_steelman (read-only import by path).
Usage: python3 -I -B feed_team_certifier.py <law2b_check stdout json> <path to transformational_steelman_certifier.py>
Prints one JSON object: for every spec the team's verdict, reasons, and my guard function's reasons; plus must-fail probes of the team's certifier."""
import importlib.util, json, sys
from fractions import Fraction

def load(path):
    spec = importlib.util.spec_from_file_location("team_cert", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def conv(s):
    out = {}
    for k, v in s.items():
        if k.startswith("_"): continue
        if k in ("max_null_false_pass_rate", "residual_gap", "max_residual_gap"): out[k] = Fraction(v)
        else: out[k] = v
    return out

def main():
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    team = load(sys.argv[2])
    res = {}
    for name, s in sorted(rep["specs"].items()):
        mine = s.get("_my_guard_reasons", [])
        try:
            r = team.certify_transformational_steelman(conv(s))
            res[name] = {"team_status": r["status"], "team_admitted": r["admitted"], "team_reasons": r["reasons"], "my_reasons": mine, "my_admitted": mine == []}
        except Exception as exc:   # schema refusal is itself a result
            res[name] = {"team_error": str(exc), "my_reasons": mine}
    # probes of the team's certifier with a spec whose claimed numbers are FALSE (the certifier takes counts on trust)
    base = conv(rep["specs"]["R4_lattice_basis_change_T1"])
    probes = {}
    p = dict(base); p["target_pass_count"] = p["target_total_count"]; p["null_false_pass_count"] = 0; p["literal_failure_witness"] = "invented"
    probes["admits_any_self_reported_numbers"] = team.certify_transformational_steelman(p)["admitted"]
    q = dict(conv(rep["specs"]["R3_equiv_IF"])); q["obstruction_invariant"] = "x"; q["obstruction_survives_all_searched"] = True
    probes["admits_unchecked_obstruction_string"] = team.certify_transformational_steelman(q)["admitted"]
    z = dict(conv(rep["specs"]["R3_equiv_IF"])); z["residual_gap"] = Fraction(0)
    probes["refuses_iF_with_zero_gap"] = not team.certify_transformational_steelman(z)["admitted"]
    res["_probes"] = probes
    sys.stdout.write(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
