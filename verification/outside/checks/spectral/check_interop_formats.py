"""Do loom pull request 7 certificates and the dual-oracle checker interoperate, in both directions?

Audit: AUDIT-016R. Backs, in VERDICTS.md, the sentence for repair "loom 10 (docs/11): supports loom#7
certificates ... False at head since the team's own hardening (rejects "1/1" and "0/1"). One-line fix
or a converter." It uses each side's own producer and own checker, unchanged, on four matrices
(two truss matrices, a complex 3x3, a zero-diagonal 2x2). It prints, for each matrix, what each checker
does with the other's raw certificate and with the same certificate converted to the other's string
format (lowest terms "1", or p/q "1/1").

Run it against two commits of Foundation-0/spectral-inertia to see the change: the default branch head
(raw loom certificates are rejected, the hardening) and commit 1dc18e4, the parent of the hardening
(raw loom certificates were accepted). The raw outcomes are printed as measurements. The script fails
only if a converted certificate is rejected, or if the checkers give different inertia on a converted one.

Needs: Python 3 (standard library only), clones in SPECTRAL_INERTIA_DIR and LOOM_SCRIPTS_DIR.
Run (about 1 second):
    SPECTRAL_INERTIA_DIR=/path/to/spectral-inertia LOOM_SCRIPTS_DIR=/path/to/loom/scripts \
        python3 -I -B check_interop_formats.py
Deterministic, no random numbers. Exit code 0 only if every converted certificate is accepted by
the other checker with the same inertia.
"""
import importlib.util
import json
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

sys.path.insert(0, common.spectral_inertia_dir())
import spectral_inertia.dual_oracle as dora  # noqa: E402
import spectral_inertia.exact_qi as eqi  # noqa: E402

spec = importlib.util.spec_from_file_location("loom7_verify", os.path.join(common.loom_scripts_dir(), "verify_inertia.py"))
vi = importlib.util.module_from_spec(spec); spec.loader.exec_module(vi)
ic = vi.ic

mats = {
    "truss_interior_diag(200/99,0)": [[F(200, 99), F(0)], [F(0), F(0)]],
    "truss_corner": [[F(6688, 4375), F(4432, 3675)], [F(4432, 3675), F(29744, 9261)]],
    "complex_3x3": [[F(2), (F(1), F(1)), F(0)], [(F(1), F(-1)), F(-1), F(1, 2)], [F(0), F(1, 2), F(3)]],
    "zero_diag_2x2": [[F(0), F(1)], [F(1), F(0)]],
}


def lowest_terms(x):
    if isinstance(x, list):
        return [lowest_terms(v) for v in x]
    if isinstance(x, str) and "/" in x:
        f = F(x)
        return str(f.numerator) if f.denominator == 1 else "%d/%d" % (f.numerator, f.denominator)
    return x


def p_over_q(x):
    if isinstance(x, list):
        return [p_over_q(v) for v in x]
    if isinstance(x, str):
        f = F(x)
        return "%d/%d" % (f.numerator, f.denominator)
    return x


out = {}
problems = []
raw_loom_into_team = 0
raw_team_into_loom = 0
for name, M in mats.items():
    row = {}
    cert = vi.certify(M)
    text = json.dumps(cert)
    row["loom7_checker_on_loom7_cert"] = list(ic.check(text))
    for strict in (True, False):
        try:
            row[f"team_pldl_on_loom7_cert_strict={strict}"] = list(dora.verify_congruence_pldl_cert(text, strict_string_entries=strict))
        except eqi.CertError as e:
            row[f"team_pldl_on_loom7_cert_strict={strict}"] = "REJECT " + e.code + ": " + e.message[:60]
    conv = {k: (lowest_terms(v) if k != "P" else v) for k, v in cert.items()}
    try:
        row["team_dual_oracle_on_converted_loom7_cert"] = list(dora.verify_inertia_dual_oracle(json.dumps(conv))["inertia"])
    except eqi.CertError as e:
        row["team_dual_oracle_on_converted_loom7_cert"] = "REJECT " + e.code
    # reverse direction: team's own producer -> loom#7 checker
    Mq = [[eqi.Qi(x[0], x[1]) if isinstance(x, tuple) else eqi.Qi(F(x)) for x in r] for r in M]
    tcert = dora.produce_pldl_certificate(Mq)
    ttext = json.dumps({k: tcert[k] for k in ("M", "P", "L", "D")})
    try:
        row["loom7_checker_on_team_cert"] = list(ic.check(ttext))
    except ic.CertError as e:
        row["loom7_checker_on_team_cert"] = "REJECT " + str(e)[:70]
    tconv = {k: (p_over_q(v) if k != "P" else v) for k, v in json.loads(ttext).items()}
    row["loom7_checker_on_converted_team_cert"] = list(ic.check(json.dumps(tconv)))
    native = row["loom7_checker_on_loom7_cert"]
    if row["team_dual_oracle_on_converted_loom7_cert"] != native:
        problems.append(name + ": converted loom certificate")
    if row["loom7_checker_on_converted_team_cert"] != native:
        problems.append(name + ": converted team certificate")
    if not isinstance(row["team_pldl_on_loom7_cert_strict=True"], list):
        raw_loom_into_team += 1
    if not isinstance(row["loom7_checker_on_team_cert"], list):
        raw_team_into_loom += 1
    out[name] = row
print(json.dumps(out, indent=1))
common.finish("check_interop_formats", not problems,
              "matrices=%d converted certificates accepted with equal inertia by both checkers=%s; "
              "raw loom certificates rejected by the dual oracle: %d of %d; raw dual-oracle certificates "
              "rejected by the loom checker: %d of %d"
              % (len(mats), "yes" if not problems else "NO " + str(problems), raw_loom_into_team, len(mats),
                 raw_team_into_loom, len(mats)))
