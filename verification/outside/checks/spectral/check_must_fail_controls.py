"""Must-fail controls swapped between the two inertia-certificate checkers, plus encoding probes.

Audit: AUDIT-016R. Backs, in VERDICTS.md: "each rejects the other's must-fail inputs" (016R, section 1)
and the sentence for repair about loom 10 (docs/11): the two formats do not interoperate without
a conversion.

In the code, "ours" means loom pull request 7 and "theirs" means spectral-inertia.
Ours:   siliconcordat/loom pull request 7, scripts/verify_inertia.py (its must-fail controls, raw
        text controls and a known-good certificate) and scripts/inertia_cert.py (checker).
Theirs: Foundation-0/spectral-inertia, dual_oracle (its structural controls from tests/test_track_c).
Our controls go to their checker with entries mapped to lowest terms. Their controls go to ours with
entries mapped to p/q. Raw-text controls (floats, NaN, duplicate keys, zero denominator, digit limits)
are rebuilt for their checker. Encoding probes and the size limit at n = 65 are printed. Every control
must be rejected by both checkers, and each known-good certificate must be accepted by both, with equal
inertia on random matrices at n = 8, 16, 24. The encoding probes are printed for information only.

Needs: Python 3 with SymPy, clones in SPECTRAL_INERTIA_DIR and LOOM_SCRIPTS_DIR.
Run (about 8 seconds):
    SPECTRAL_INERTIA_DIR=/path/to/spectral-inertia LOOM_SCRIPTS_DIR=/path/to/loom/scripts \
        python3 -I -B check_must_fail_controls.py
Fixed seed 5 for the random matrices. Exit code 0 only if every control was rejected by both.
"""
import json
import os
import random
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import check_dual_checkers as CO  # noqa: E402  (reuses loaders and format maps only)

print("seed: 5")
IC, VI, DO, EQ, L = CO.IC, CO.VI, CO.DO, CO.EQ, CO.L
out = {}

# 1. our controls -> their checker (mapped to canonical strings)
ours_ctrl = VI.controls()
r = {}
for name, cert in ours_ctrl.items():
    a = CO.run_ours(cert)
    b = CO.run_theirs(CO.map_entries(cert, CO.canon_s))
    r[name] = [a[0], b[0], str(b[1])]
out["our_controls"] = r

# 2. our raw-text controls rebuilt on a canonical GOOD for their checker
good_c = CO.map_entries(VI.GOOD, CO.canon_s)
gtext = json.dumps(good_c)
LONG = "1" * 5000
raw_theirs = {
    "float_in_json": gtext.replace('"1"', "1.0", 1),
    "decimal_string": gtext.replace('"1"', '"0.5"', 1),
    "duplicate_key": gtext[:-1] + ', "P": %s}' % json.dumps(good_c["P"]),
    "nan_constant": gtext.replace('"1"', "NaN", 1),
    "truncated": gtext[:50],
    "zero_denominator": gtext.replace('"1"', '"1/0"', 1),
    "entry_past_digit_limit": gtext.replace('"1"', '"%s"' % LONG, 1),
    "json_integer_past_digit_limit": gtext.replace('"P": [', '"P": [%s, ' % LONG, 1),
}
out["raw_controls"] = {k: [CO.run_ours(VI.RAW[k])[0], CO.run_theirs(v)[0], str(CO.run_theirs(v)[1])]
                       for k, v in raw_theirs.items()}
out["good_both"] = [CO.run_ours(VI.GOOD), CO.run_theirs(good_c)]

# 3. their structural controls (tests/test_track_c test_04) -> our checker (mapped to p/q)
I2 = [["1", "0"], ["0", "1"]]
I3 = [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]]
M_ov = [["1", "1", "0"], ["1", "1", "1"], ["0", "1", "1"]]
theirs_ctrl = {
    "overlap": {"M": M_ov, "P": [0, 1, 2], "L": I3, "D": M_ov},
    "repeated_P": {"M": [["1", "0"], ["0", "-1"]], "P": [0, 0], "L": I2, "D": [["1", "0"], ["0", "1"]]},
    "L_upper": {"M": [["2", "2"], ["2", "2"]], "P": [0, 1], "L": [["1", "1"], ["1", "1"]], "D": I2},
    "L_nonunit": {"M": [["4", "0"], ["0", "1"]], "P": [0, 1], "L": [["2", "0"], ["0", "1"]], "D": I2},
    "missing_D": {"M": I2, "P": [0, 1], "L": I2},
    "extra_key": {"M": I2, "P": [0, 1], "L": I2, "D": I2, "note": "x"},
    "bool_in_P": {"M": I2, "P": [False, True], "L": I2, "D": I2},
    "bool_claim": {"M": I2, "P": [0, 1], "L": I2, "D": I2, "claim": [2, False, False]},
    "D_complex_diag": {"M": I2, "P": [0, 1], "L": I2, "D": [[["1", "1"], "0"], ["0", "1"]]},
    "nonsquare_L": {"M": I2, "P": [0, 1], "L": [["1", "0"]], "D": I2},
    "empty": {},
}
r = {}
for name, cert in theirs_ctrl.items():
    a = CO.run_theirs(cert)
    try:
        mapped = CO.map_entries(cert, CO.pq_s)
    except Exception as e:
        mapped = cert
    b = CO.run_ours(mapped)
    r[name] = [a[0], str(a[1]), b[0], str(b[1])[:50]]
out["their_controls"] = r

# 4. encoding probes on ours (value-preserving re-spellings and junk) and the same idea on theirs
probes_ours = {"unreduced 2/2 for 1": "2/2", "neg zero -0/1": "-0/1", "leading zero 01/1": "01/1",
               "plain int 1": "1", "den leading zero 1/01": "1/01", "trailing newline": "1/1\n",
               "plus sign +1/1": "+1/1", "arabic digit": "١/1", "space": " 1/1"}
probes_theirs = {"unreduced 2/2": "2/2", "neg zero -0": "-0", "leading zero 01": "01", "p/1 form 1/1": "1/1",
                 "trailing newline": "1\n", "plus sign": "+1", "arabic digit": "١", "space": " 1"}
base_o = json.loads(json.dumps(VI.GOOD))
base_t = json.loads(json.dumps(good_c))
po, pt = {}, {}
# entry D[0][0] of GOOD is -? find an L diagonal entry ("1/1" / "1") and replace it
for name, s in probes_ours.items():
    c = json.loads(json.dumps(base_o)); c["L"][0][0] = s
    po[name] = CO.run_ours(c)[0]
for name, s in probes_theirs.items():
    c = json.loads(json.dumps(base_t)); c["L"][0][0] = s
    pt[name] = CO.run_theirs(c)[0]
out["encoding_probes_ours"] = po
out["encoding_probes_theirs"] = pt

# 5. size limit and timing (one process, modest sizes)
rng = random.Random(5)
sizes = {}
for n in (65,):
    H = L.zeros(n)
    for i in range(n):
        H[i][i] = (Fr(1), Fr(0))
    sizes["n65_ours"] = CO.run_ours(VI.certify(H))[0]
    sizes["n65_theirs"] = CO.run_theirs(DO.produce_pldl_certificate(CO.to_qi(H)))[0]
for n in (8, 16, 24):
    H = L.rand_herm(rng, n, True)
    oc = VI.certify(H)
    tc = DO.produce_pldl_certificate(CO.to_qi(H))
    a = CO.run_ours(oc)
    b = CO.run_theirs(tc)
    c = CO.run_theirs(CO.map_entries(oc, CO.canon_s))
    sizes["n%d" % n] = dict(ours=[a[0], len(json.dumps(oc))], theirs=[b[0], len(json.dumps(tc))],
                           theirs_on_our_cert=[c[0]], same=(a[1] == b[1] == c[1]))
out["size_limits"] = sizes
print(json.dumps(out, indent=1))

# ---- verdict ----
problems = []
for name, row in out["our_controls"].items():
    if row[0] != "REJECT" or row[1] != "REJECT":
        problems.append("our control %s: %s" % (name, row[:2]))
for name, row in out["raw_controls"].items():
    if row[0] != "REJECT" or row[1] != "REJECT":
        problems.append("raw control %s: %s" % (name, row[:2]))
for name, row in out["their_controls"].items():
    if row[0] != "REJECT" or row[2] != "REJECT":
        problems.append("their control %s: %s" % (name, [row[0], row[2]]))
if [x[0] for x in out["good_both"]] != ["ACCEPT", "ACCEPT"] or out["good_both"][0][1] != out["good_both"][1][1]:
    problems.append("known-good certificate not accepted by both with equal inertia")
if sizes["n65_ours"] != "REJECT" or sizes["n65_theirs"] != "REJECT":
    problems.append("n = 65 was not rejected by both")
for key in ("n8", "n16", "n24"):
    v = sizes[key]
    if not (v["ours"][0] == v["theirs"][0] == v["theirs_on_our_cert"][0] == "ACCEPT" and v["same"]):
        problems.append("%s: checkers disagree" % key)
n_ctrl = len(out["our_controls"]) + len(out["raw_controls"]) + len(out["their_controls"])
common.finish("check_must_fail_controls", not problems,
              ("%d controls rejected by both checkers, known-good accepted by both, n=8,16,24 agree"
               % n_ctrl) if not problems else "problems: %s" % problems[:3])
