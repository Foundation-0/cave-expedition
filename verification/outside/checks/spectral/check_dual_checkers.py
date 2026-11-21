"""Two inertia-certificate checkers on the same fresh exact matrices.

Audit: AUDIT-016R. Backs, in VERDICTS.md: "Dual-oracle inertia checker (016R): agrees with our
checker on 400 fresh matrices and 800 tampered certificates, each rejects the other's must-fail
inputs" and the sentence for repair that the two checkers need a common string format.

In the code, "ours" means loom pull request 7 and "theirs" means spectral-inertia.
Ours:   siliconcordat/loom pull request 7, scripts/inertia_cert.py (checker) and the producer
        in scripts/verify_inertia.py.
Theirs: Foundation-0/spectral-inertia, dual_oracle.verify_inertia_dual_oracle (pldl and c_cert modes).
Truth:  exactlib_a.py (two inertia methods that agree).
For 400 matrices (singular, zero diagonal, repeated eigenvalues, entries near 1e12) it runs each
checker on its own certificate, on the other's certificate after mapping entries to the other's string
format, and counts wrong inertias, rejections of valid input and crashes. Then each certificate gets
one random tampering (800 in all) and both checkers must never accept a wrong inertia and must agree.
The raw format incompatibility (no mapping) is counted and printed, and is not a failure.

Needs: Python 3 with SymPy, clones in SPECTRAL_INERTIA_DIR and LOOM_SCRIPTS_DIR.
Run (about 8 seconds):
    SPECTRAL_INERTIA_DIR=/path/to/spectral-inertia LOOM_SCRIPTS_DIR=/path/to/loom/scripts \
        python3 -I -B check_dual_checkers.py [n_matrices] [seed]
Defaults: n_matrices 400, seed 20261121.
Exit code 0 only if no wrong inertia, no wrong acceptance, no crash and no disagreement was found.
"""
import copy
import importlib.util
import json
import os
import random
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

LOOM = common.loom_scripts_dir()
sys.path.insert(0, common.spectral_inertia_dir())
import exactlib_a as L  # noqa: E402
from spectral_inertia import dual_oracle as DO  # noqa: E402
from spectral_inertia import exact_qi as EQ  # noqa: E402

NAME = "check_dual_checkers"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


IC = load(os.path.join(LOOM, "inertia_cert.py"), "ours_checker")
VI = load(os.path.join(LOOM, "verify_inertia.py"), "ours_suite")


# ---------- format mapping ----------

def canon_s(s):
    f = Fr(s)
    return str(f.numerator) if f.denominator == 1 else "%d/%d" % (f.numerator, f.denominator)


def pq_s(s):
    f = Fr(s)
    return "%d/%d" % (f.numerator, f.denominator)


def map_entries(obj, fn):
    out = copy.deepcopy(obj)
    for key in ("M", "L", "D", "C", "C_inv"):
        if key in out:
            out[key] = [[fn(e) if isinstance(e, str) else [fn(e[0]), fn(e[1])] for e in row] for row in out[key]]
    return out


def to_qi(M):
    return [[EQ.Qi(x[0], x[1]) for x in r] for r in M]


# ---------- runners ----------

def run_ours(cert_or_text):
    text = cert_or_text if isinstance(cert_or_text, str) else json.dumps(cert_or_text)
    try:
        return ("ACCEPT", IC.check(text))
    except IC.CertError as e:
        return ("REJECT", str(e)[:60])
    except Exception as e:  # anything else is a crash, reported separately
        return ("CRASH", "%s: %s" % (type(e).__name__, str(e)[:60]))


def run_theirs(cert_or_text, mode="pldl"):
    text = cert_or_text if isinstance(cert_or_text, str) else json.dumps(cert_or_text)
    try:
        return ("ACCEPT", tuple(DO.verify_inertia_dual_oracle(text, mode=mode)["inertia"]))
    except EQ.CertError as e:
        return ("REJECT", e.code)
    except Exception as e:
        return ("CRASH", "%s: %s" % (type(e).__name__, str(e)[:60]))


# ---------- matrices ----------

def gen(rng, idx):
    n = rng.randint(1, 7)
    cplx = rng.random() < 0.6
    kind = rng.choice(["herm", "zerodiag", "lowrank", "repeat", "scalar", "zero", "blocks", "big", "psd_singular"])
    if kind == "herm":
        H = L.rand_herm(rng, n, cplx)
    elif kind == "zerodiag":
        H = L.rand_herm(rng, n, cplx)
        for i in range(n):
            H[i][i] = L.Z
    elif kind == "lowrank":
        H = L.madd(L.rand_psd(rng, n, rng.randint(0, 2), cplx), L.rand_psd(rng, n, rng.randint(0, 2), cplx), Fr(-1))
    elif kind == "repeat":
        U = L.rand_unitary(rng, n, cplx)
        v = Fr(rng.choice([-2, -1, 1, 3]), rng.choice([1, 2]))
        H = L.from_eig(U, [rng.choice([v, v, 0, -v]) for _ in range(n)])
    elif kind == "scalar":
        H = L.mscale(L.eye(n), Fr(rng.choice([-3, 1, 2]), 7))
    elif kind == "zero":
        H = L.zeros(n)
    elif kind == "blocks":
        H = L.zeros(n)
        for i in range(0, n - 1, 2):
            H[i][i + 1] = L.rcz(rng, cplx)
            if H[i][i + 1] == L.Z:
                H[i][i + 1] = L.O
            H[i + 1][i] = L.cc(H[i][i + 1])
    elif kind == "big":
        H = L.mscale(L.rand_herm(rng, n, cplx), Fr(10 ** 12 + 39, 7 ** 9))
    else:
        H = L.rand_psd(rng, n, rng.randint(0, n - 1) if n > 1 else 0, cplx)
    return kind, H


# ---------- tampering ----------

def tamper(rng, cert, fmt):
    """One random change to a certificate in its own string format (fmt: 'pq' or 'canon')."""
    c = copy.deepcopy(cert)
    n = len(c["M"])
    w = pq_s if fmt == "pq" else canon_s

    def bump(e, dv):
        if isinstance(e, str):
            return w(str(Fr(e) + dv))
        return [w(str(Fr(e[0]) + dv)), e[1]]

    op = rng.choice(["L", "D", "M", "P", "claim", "Lupper", "Doff", "Dimag"])
    i, j = rng.randrange(n), rng.randrange(n)
    if op == "L" and n > 1:
        i = rng.randrange(1, n); j = rng.randrange(0, i)
        c["L"][i][j] = bump(c["L"][i][j], 1)
    elif op == "D":
        c["D"][i][i] = bump(c["D"][i][i], rng.choice([1, -1]))
    elif op == "M":
        c["M"][i][i] = bump(c["M"][i][i], 1)
    elif op == "P" and n > 1:
        c["P"][0], c["P"][1] = c["P"][1], c["P"][0]
    elif op == "claim":
        cl = list(c.get("claim", [0, 0, 0]))
        cl[0] += 1; cl[2] -= 1
        c["claim"] = cl
    elif op == "Lupper" and n > 1:
        c["L"][0][n - 1] = w("1")
    elif op == "Doff" and n > 2:
        k = rng.randrange(0, n - 1)
        c["D"][k][k + 1] = w("1"); c["D"][k + 1][k] = w("1")
    elif op == "Dimag":
        c["D"][i][i] = [w(str(Fr(c["D"][i][i] if isinstance(c["D"][i][i], str) else c["D"][i][i][0]))), w("1")]
    return op, c


def truth_of(cert_M_entries):
    M = [[(Fr(e), Fr(0)) if isinstance(e, str) else (Fr(e[0]), Fr(e[1])) for e in row] for row in cert_M_entries]
    if not L.is_herm(M):
        return None
    return L.inertia(M, len(M) <= 6)


def main():
    ncase = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261121
    print("seed:", seed, "n_matrices:", ncase)
    rng = random.Random(seed)
    st = dict(matrices=0, kinds={}, ours_native_wrong=0, theirs_native_wrong=0, theirs_c_wrong=0,
              cross_ours_cert_in_theirs_wrong=0, cross_their_cert_in_ours_wrong=0,
              any_reject_on_valid=0, crashes=[], raw_format=dict(ours_cert_raw_into_theirs={},
                                                                 their_cert_raw_into_ours={}),
              fuzz=dict(total=0, ours_accept_wrong=0, theirs_accept_wrong=0, ours_acc=0, theirs_acc=0,
                        disagree=[]))
    for idx in range(ncase):
        kind, H = gen(rng, idx)
        st["matrices"] += 1
        st["kinds"][kind] = st["kinds"].get(kind, 0) + 1
        tru = L.inertia(H, len(H) <= 6)
        oc = VI.certify(H)
        tc = DO.produce_pldl_certificate(to_qi(H))
        C, Ci, D, _ = DO.produce_c_certificate(to_qi(H))
        tcc = {"M": EQ.matrix_to_json(to_qi(H)), "C": EQ.matrix_to_json(C), "C_inv": EQ.matrix_to_json(Ci),
               "D": EQ.matrix_to_json(D)}
        res = {
            "ours_native": run_ours(oc),
            "theirs_native": run_theirs(tc),
            "theirs_c": run_theirs(tcc, "c_cert"),
            "cross_ours_cert_in_theirs": run_theirs(map_entries(oc, canon_s)),
            "cross_their_cert_in_ours": run_ours(map_entries(tc, pq_s)),
        }
        for k, (verdict, val) in res.items():
            if verdict == "CRASH":
                st["crashes"].append([k, kind, val])
            elif verdict == "REJECT":
                st["any_reject_on_valid"] += 1
                st["crashes"].append([k, kind, "REJECT " + str(val)])
            elif val != tru:
                st[k + "_wrong"] += 1
        r1 = run_theirs(oc)
        r2 = run_ours(tc)
        d1 = st["raw_format"]["ours_cert_raw_into_theirs"]
        d2 = st["raw_format"]["their_cert_raw_into_ours"]
        d1[r1[0] + ":" + str(r1[1])] = d1.get(r1[0] + ":" + str(r1[1]), 0) + 1
        k2 = r2[0] + ":" + str(r2[1])[:30]
        d2[k2] = d2.get(k2, 0) + 1
        # differential fuzz: tamper each certificate in its own format, run its own checker and the other
        for fmt, base in (("pq", oc), ("canon", tc)):
            op, bad = tamper(rng, base, fmt)
            mine = run_ours(bad if fmt == "pq" else map_entries(bad, pq_s))
            theirs = run_theirs(bad if fmt == "canon" else map_entries(bad, canon_s))
            tr = truth_of(bad["M"])
            st["fuzz"]["total"] += 1
            for who, rr in (("ours", mine), ("theirs", theirs)):
                if rr[0] == "ACCEPT":
                    st["fuzz"][who + "_acc"] += 1
                    if rr[1] != tr:
                        st["fuzz"][who + "_accept_wrong"] += 1
                elif rr[0] == "CRASH":
                    st["crashes"].append(["fuzz-" + who, op, rr[1]])
            if (mine[0] == "ACCEPT") != (theirs[0] == "ACCEPT") and len(st["fuzz"]["disagree"]) < 8:
                st["fuzz"]["disagree"].append([fmt, op, mine[0], str(mine[1])[:40], theirs[0], str(theirs[1])])
    print(json.dumps(st, indent=1))
    fz = st["fuzz"]
    bad = (st["ours_native_wrong"] + st["theirs_native_wrong"] + st["theirs_c_wrong"]
           + st["cross_ours_cert_in_theirs_wrong"] + st["cross_their_cert_in_ours_wrong"]
           + st["any_reject_on_valid"] + len(st["crashes"]) + fz["ours_accept_wrong"]
           + fz["theirs_accept_wrong"] + len(fz["disagree"]))
    common.finish(NAME, bad == 0,
                  "matrices=%d tampered=%d wrong_inertia_or_wrong_accept_or_crash_or_disagreement=%d "
                  "(raw string formats rejected without mapping: %d of %d and %d of %d)" % (
                      st["matrices"], fz["total"], bad,
                      sum(v for k, v in st["raw_format"]["ours_cert_raw_into_theirs"].items() if k.startswith("REJECT")),
                      st["matrices"],
                      sum(v for k, v in st["raw_format"]["their_cert_raw_into_ours"].items() if k.startswith("REJECT")),
                      st["matrices"]))


if __name__ == "__main__":
    main()
