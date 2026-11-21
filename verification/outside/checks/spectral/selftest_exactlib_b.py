"""Self-test of the exact helper library exactlib_b.py against floating-point eigenvalues.

Audit: supports AUDIT-014 and the 420-case recount of AUDIT-002. Backs the trust placed in the exact
LDL* inertia routine used as ground truth by the second-pass scripts. It builds 300 random Hermitian
matrices from random exact unitaries and prescribed rational eigenvalues, with and without a zeroed
diagonal, and checks the exact inertia against the prescribed signs (full matrix) and against NumPy
eigenvalue signs (zero-diagonal matrix).

Needs: Python 3 with numpy.
Run (a few seconds): python3 -I -B selftest_exactlib_b.py
Fixed seed 7. Exit code 0 only if there are no mismatches.
"""
import os
import random
import sys
from fractions import Fraction as F

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import exactlib_b as L  # noqa: E402

SEED = 7
print("seed:", SEED)
rng = random.Random(SEED)
bad = 0
for trial in range(300):
    n = rng.randint(1, 6)
    U = L.cayley(n, rng)
    ev = [F(rng.randint(-3, 3), rng.randint(1, 3)) for _ in range(n)]
    A = L.from_eigs(U, ev)
    want = (sum(e > 0 for e in ev), sum(e < 0 for e in ev), sum(e == 0 for e in ev))
    got = L.inertia(A)
    # zero-diagonal case
    B = [[A[i][j] if i != j else L.Z for j in range(n)] for i in range(n)]
    w = np.linalg.eigvalsh(np.array([[complex(float(x[0]), float(x[1])) for x in r] for r in B]))
    gotB = L.inertia(B)
    numB = (int((w > 1e-9).sum()), int((w < -1e-9).sum()))
    if got != want or gotB[:2] != numB:
        bad += 1
        print("MISMATCH", n, ev, got, want, gotB, numB)
common.finish("selftest_exactlib_b", bad == 0, "cases=300 mismatches=%d" % bad)
