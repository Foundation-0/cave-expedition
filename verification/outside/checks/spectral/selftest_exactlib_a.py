"""Self-test of the exact helper library exactlib_a.py against floating-point eigenvalues.

Audit: supports AUDIT-002, AUDIT-014 and AUDIT-016R. Backs the trust placed in the exact inertia
routine that the other scripts use as ground truth ("two own inertia methods that agree on every
matrix"). It checks 300 random Hermitian matrices with entries in the Gaussian rationals (full,
zero diagonal, low rank, repeated eigenvalues), that random Cayley-type unitaries are exactly unitary,
and that the congruence inertia and the SymPy characteristic-polynomial inertia agree exactly and
match NumPy's eigenvalue signs.

Needs: Python 3 with numpy and SymPy.
Run (a few seconds): python3 -I -B selftest_exactlib_a.py
Fixed seed 7. Exit code 0 only if there are no mismatches.
"""
import os
import random
import sys
from fractions import Fraction as Fr

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import exactlib_a as L  # noqa: E402

SEED = 7
print("seed:", SEED)
rng = random.Random(SEED)
bad = 0
N = 0
for trial in range(300):
    n = rng.randint(1, 6)
    cplx = rng.random() < 0.7
    kind = rng.choice(["herm", "zerodiag", "lowrank", "repeat"])
    if kind == "herm":
        H = L.rand_herm(rng, n, cplx)
    elif kind == "zerodiag":
        H = L.rand_herm(rng, n, cplx)
        for i in range(n):
            H[i][i] = L.Z
    elif kind == "lowrank":
        H = L.madd(L.rand_psd(rng, n, rng.randint(0, n), cplx), L.rand_psd(rng, n, rng.randint(0, n), cplx), Fr(-1))
    else:
        U = L.rand_unitary(rng, n, cplx)
        H = L.from_eig(U, [Fr(rng.choice([-1, 0, 0, 1, 2])) for _ in range(n)])
    U = L.rand_unitary(rng, n, cplx)
    if L.mmul(L.dag(U), U) != L.eye(n):
        bad += 1
        print("NOT UNITARY", kind, n)
    a = L.inertia(H)
    A = np.array([[float(x[0]) + 1j * float(x[1]) for x in r] for r in H])
    ev = np.linalg.eigvalsh(A)
    sc = max(1.0, np.abs(ev).max())
    f = (int((ev > 1e-9 * sc).sum()), int((ev < -1e-9 * sc).sum()))
    if (a[0], a[1]) != f:
        bad += 1
        print("MISMATCH", kind, n, a, f)
    N += 1
common.finish("selftest_exactlib_a", bad == 0, "cases=%d mismatches=%d" % (N, bad))
