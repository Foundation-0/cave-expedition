"""Does the sharpness of R_opt also hold when the matrix size n is held fixed? Numerical probe.

Audit: AUDIT-002. Backs, in VERDICTS.md: "Sharpness of R_opt (002)" as narrowed by the second pass:
the statement is about every feasible (u, t, S, b) with the matrix size free, and in a fixed-n probe
no counterexample was found (41 tested sources, n = 2 to 4). This is evidence, not a proof, and most
tested cases have target rank 1.

For random n x n complex sources with rank P above the target max(1, ceil R_opt), it tries to realise
the same (u, t, S, b) at the same n with rank P equal to the target, by many BFGS restarts on a residual
(normalised so S = 1). A residual that stays above 1e-13 counts as a candidate failure. R_opt of each
tuple is evaluated exactly with Fractions.

Needs: Python 3 with numpy and SciPy, exactlib_b.py.
Run (about 10 seconds for the default size): python3 -I -B check_fixed_n_sharpness.py [seed] [sources_per_case]
Defaults: seed 7, sources_per_case 10. The seed is printed. Counts move slightly with the SciPy version.
Exit code 0 only if at least one source was tested and no candidate failure was found.
"""
import json
import math
import os
import sys
from fractions import Fraction as F

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import exactlib_b as L  # noqa: E402


def unitary(x, n):
    A = x[: n * n].reshape(n, n) + 1j * x[n * n: 2 * n * n].reshape(n, n)
    Qm, R = np.linalg.qr(A)
    return Qm


def realise(n, r, b, u, t, S, rng, restarts=25):
    nb = 2 * n * n
    best = (np.inf, None)

    def build(x):
        B = x[:n * r].reshape(n, r) + 1j * x[n * r: 2 * n * r].reshape(n, r)
        off = 2 * n * r
        U = unitary(x[off: off + nb], n)
        off += nb
        qpos = x[off: off + b]
        qneg = -x[off + b: off + n] ** 2
        q = np.concatenate([qpos, qneg])
        P = B @ B.conj().T
        Q = U @ np.diag(q) @ U.conj().T
        return P, Q

    def res(x):
        P, Q = build(x)
        H = P + Q
        return ((np.trace(P).real - u) ** 2 + (np.trace(Q).real - t) ** 2
                + (np.sum(np.abs(H) ** 2) - S) ** 2)

    dim = 2 * n * r + nb + n
    for _ in range(restarts):
        x0 = rng.normal(size=dim)
        r_ = minimize(res, x0, method="BFGS", options={"gtol": 1e-14, "maxiter": 4000})
        if r_.fun < best[0]:
            best = (r_.fun, r_.x)
        if best[0] < 1e-14:
            break
    return best[0]


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    print("seed:", seed, "sources_per_case:", per)
    rng = np.random.default_rng(seed)
    out = {}
    for n in (2, 3, 4):
        for b in range(1, n):
            c = dict(sources=0, tested=0, realised=0, candidate_fail=0, fails=[])
            for _ in range(per):
                r_src = int(rng.integers(1, n + 1))
                # source: rational entries so that R_opt can be evaluated exactly
                Bm = rng.integers(-3, 4, size=(n, r_src)) + 1j * rng.integers(-3, 4, size=(n, r_src))
                P = Bm @ Bm.conj().T
                b_src = int(rng.integers(0, b + 1))
                Cm = rng.integers(-3, 4, size=(n, n)) + 1j * rng.integers(-3, 4, size=(n, n))
                Cm = Cm + Cm.conj().T
                w, V = np.linalg.eigh(Cm)
                # force n_+(Q) <= b by shifting: Q = Cm - shift I with shift = (b_src+1)-th largest eigenvalue
                shift = sorted(w, reverse=True)[b_src] if b_src < n else min(w) - 1
                Qn = Cm - shift * np.eye(n) * 1.0
                if int((np.linalg.eigvalsh(Qn) > 1e-9).sum()) > b:
                    continue
                if np.linalg.matrix_rank(P) == 0:
                    continue
                c["sources"] += 1
                Hn = P + Qn
                u = float(np.trace(P).real)
                t = float(np.trace(Qn).real)
                S = float(np.sum(np.abs(Hn) ** 2))
                sc = S ** 0.5  # normalise: (u, t, S) -> (u/sc, t/sc, 1); R_opt and ranks are unchanged
                u, t, S = u / sc, t / sc, 1.0
                Rf = L.ropt(F(u), F(t), F(S), b)
                target = max(1, math.ceil(Rf - F(1, 10 ** 9)))
                rk = int(np.linalg.matrix_rank(P))
                if rk <= target:
                    continue
                c["tested"] += 1
                best = realise(n, target, b, u, t, S, rng)
                if best < 1e-13:
                    c["realised"] += 1
                else:
                    c["candidate_fail"] += 1
                    if len(c["fails"]) < 3:
                        c["fails"].append(dict(u=u, t=t, S=S, b=b, R_opt=float(Rf), target=target, src_rank=rk,
                                               best_residual=best))
            out[f"n={n},b={b}"] = c
    print(json.dumps(out, indent=1))
    tested = sum(v["tested"] for v in out.values())
    realised = sum(v["realised"] for v in out.values())
    fails = sum(v["candidate_fail"] for v in out.values())
    common.finish("check_fixed_n_sharpness", tested > 0 and fails == 0,
                  "tested=%d realised_at_same_n=%d candidate_failures=%d" % (tested, realised, fails))


if __name__ == "__main__":
    main()
