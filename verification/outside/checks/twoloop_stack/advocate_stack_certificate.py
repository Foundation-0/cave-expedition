#!/usr/bin/env python3
"""Check script advocate_stack_certificate.py: AUDIT-006R (Q_stack), advocate's re-check with its own code.

Backs: VERDICTS.md section 2, 'Q_stack (006R): N1 to N0': the concatenated test is the existing section 5.1 test applied to stacked factors (B_stack A_stack equals the sum of B_k A_k exactly, PSD of Q_stack equals PSD of sI - K on 240 probes), plus the worked example (four disjoint adapters pass at s = 1, a shared carrier is rejected at s = 1 with inertia (0,1,3) and accepted at s = 4).
Needs: python3 (3.10 or newer). No network, no clone of any repository, no input files.
Run: python3 -I -B advocate_stack_certificate.py
     (also python3 -I -O -B advocate_stack_certificate.py and python3 -I -B -W error advocate_stack_certificate.py, same output)
Time: about 1 second.
Every failed check raises CheckFailed and the script exits 1. On success the last
line printed starts with RESULT: PASS and the exit code is 0.
Seed (fixed, printed in the output): 5150.

Original description:
Advocate re-check of F4 (team Check 9: Q_stack(s) = s G_B - G_B G_A G_B with concatenated factors).

Own exact code: Faddeev-LeVerrier characteristic polynomial over Fractions + Descartes' rule (exact for
real-rooted polynomials, which symmetric matrices have) gives the inertia (n_plus, n_minus, n_zero).
1. B_stack A_stack == sum_k B_k A_k exactly, so Q_stack(s) is docs/10 section 5.1's Q(s) for B = B_stack, A = A_stack.
2. inertia test: Q_stack(s) PSD  <=>  s I - K PSD with K = (sum B_k A_k)(sum B_k A_k)^T, on random rectangular stacks.
3. team's example rebuilt with my own orthonormal basis (permutation-signed identity scaled, not the team's Householder):
   4 disjoint rank-2 projector adapters: PSD at s = 1, not at s = 99/100; shared carrier bio + astro: (0,1,3) at s = 1,
   PSD at s = 4; worst-case stack rule value N * sum sigma_k^2 = 16 vs exact 1.
Every failed check raises CheckFailed.
"""
import json
import random
import sys
from fractions import Fraction as Fr


class CheckFailed(Exception):
    pass


def need(c, msg):
    if not c:
        raise CheckFailed(msg)


def mm(A, B):
    return [[sum((A[i][k] * B[k][j] for k in range(len(B))), Fr(0)) for j in range(len(B[0]))] for i in range(len(A))]


def T(A):
    return [list(r) for r in zip(*A)]


def add(A, B):
    return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]


def scal(c, A):
    return [[c * a for a in r] for r in A]


def eye(n):
    return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]


def charpoly(A):
    """Faddeev-LeVerrier: returns c[0..n] with p(x) = sum c[i] x^(n-i), c[0] = 1."""
    n = len(A)
    c = [Fr(1)]
    Mk = [[Fr(0)] * n for _ in range(n)]
    for k in range(1, n + 1):
        Mk = add(mm(A, Mk), scal(c[-1], eye(n)))
        AM = mm(A, Mk)
        ck = -sum((AM[i][i] for i in range(n)), Fr(0)) / k
        c.append(ck)
    return c


def sign_changes(seq):
    s = [x for x in seq if x != 0]
    return sum(1 for a, b in zip(s, s[1:]) if (a > 0) != (b > 0))


def inertia(A):
    n = len(A)
    c = charpoly(A)   # coefficients of x^n ... x^0
    nz = 0
    while nz < n and c[n - nz] == 0:
        nz += 1
    core = c[: n + 1 - nz]
    pos = sign_changes(core)
    neg_coeffs = [core[i] * (-1) ** (len(core) - 1 - i) for i in range(len(core))]
    neg = sign_changes(neg_coeffs)
    need(pos + neg + nz == n, "Descartes count mismatch (should not happen for symmetric)")
    return (pos, neg, nz)


def concat(Bs, As):
    Bst = [sum((Bk[r] for Bk in Bs), []) for r in range(len(Bs[0]))]
    Ast = [row for Ak in As for row in Ak]
    return Bst, Ast


def Q_stack(Bst, Ast, s):
    GB = mm(T(Bst), Bst)
    GA = mm(Ast, T(Ast))
    return add(scal(s, GB), scal(Fr(-1), mm(mm(GB, GA), GB)))


def part12(seed=5150, trials=60):
    rng = random.Random(seed)
    agree = 0
    for _ in range(trials):
        d_out, d_in = rng.randint(3, 5), rng.randint(3, 5)
        N = rng.randint(2, 3)
        Bs, As = [], []
        for _ in range(N):
            rk = rng.randint(1, 2)
            Bs.append([[Fr(rng.randint(-2, 2), 2) for _ in range(rk)] for _ in range(d_out)])
            As.append([[Fr(rng.randint(-2, 2), 2) for _ in range(d_in)] for _ in range(rk)])
        Bst, Ast = concat(Bs, As)
        W = mm(Bst, Ast)
        Wsum = [[Fr(0)] * d_in for _ in range(d_out)]
        for Bk, Ak in zip(Bs, As):
            Wsum = add(Wsum, mm(Bk, Ak))
        need(W == Wsum, "B_stack A_stack != sum B_k A_k")
        K = mm(W, T(W))
        for s in (Fr(1, 2), Fr(2), Fr(5), Fr(12)):
            iq = inertia(Q_stack(Bst, Ast, s))
            ik = inertia(add(scal(s, eye(d_out)), scal(Fr(-1), K)))
            need((iq[1] == 0) == (ik[1] == 0), "PSD equivalence failed")
            agree += 1
    return {"probes": agree, "psd_equivalence_agrees": agree}


def part3():
    d = 8
    # my own orthonormal basis: columns of a signed permutation of the identity
    perm = [3, 6, 0, 7, 1, 4, 2, 5]
    sign = [1, -1, 1, 1, -1, 1, -1, 1]
    U = [[Fr(sign[c]) if r == perm[c] else Fr(0) for c in range(d)] for r in range(d)]
    col = lambda c: [[U[r][c]] for r in range(d)]
    Bs = []
    for k in range(4):
        Bs.append([[U[r][2 * k], U[r][2 * k + 1]] for r in range(d)])
    As = [T(Bk) for Bk in Bs]
    Bst, Ast = concat(Bs, As)
    i1 = inertia(Q_stack(Bst, Ast, Fr(1)))
    i99 = inertia(Q_stack(Bst, Ast, Fr(99, 100)))
    need(i1[1] == 0 and i99[1] > 0, "disjoint: PSD at 1, not at 99/100")
    B_astro = [[U[r][0], U[r][7]] for r in range(d)]
    Bst2, Ast2 = concat([Bs[0], B_astro], [As[0], T(B_astro)])
    j1 = inertia(Q_stack(Bst2, Ast2, Fr(1)))
    j4 = inertia(Q_stack(Bst2, Ast2, Fr(4)))
    jb = inertia(Q_stack(Bs[0], As[0], Fr(1)))
    need(j1 == (0, 1, 3) and j4[1] == 0 and jb[1] == 0, "shared-carrier inertias")
    return {"disjoint_s1": i1, "disjoint_s_99_100": i99, "shared_s1": j1, "shared_s4": j4, "bio_only_s1": jb,
            "worst_case_rule_N_sum_sigma2": 4 * 4, "exact_sigma_max2": 1}


def main():
    out = {"part12_random_stacks": part12(), "part3_team_example_rebuilt": part3()}
    print("seed: part12=5150")
    print(json.dumps(out, indent=1, default=str))
    print("RESULT: PASS advocate_stack_certificate: B_stack A_stack = sum B_k A_k and PSD equivalence agree on %d probes, worked example inertias match"
          % out["part12_random_stacks"]["probes"])
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckFailed as exc:
        print("RESULT: FAIL (%s)" % exc)
        sys.exit(1)
