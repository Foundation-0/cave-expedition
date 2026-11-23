#!/usr/bin/env python3
"""Recheck of the AUDIT-019 mechanics claims, written from scratch (advocate check).

Framework: rigid cross-polytope motif {+-e_i} (2n nodes per cell, all edges of length
sqrt 2) plus n bridge bars from +e_i in cell 0 to -e_i in cell e_i, as springs with
stiffness 1/|b|^2, periodic at q = 0. For each case, in exact rationals:
  (a) the relaxed Cauchy-Born tensor (Schur complement) and its rank;
  (b) the periodic self-stresses and the span of their virial stresses;
  (c) the diagonal symmetrizers tau of the bridge matrix and the closed form
      sigma(tau) = B^T diag(tau) B + 2 diag(tau) B;
  (d) Lubensky et al. (2015) eq. (A4): the Schur complement equals E^T G^-1 E over the
      self-stresses.
In every case rank S = rank of the virial span = number of diagonal symmetrizers = rank of
the formula span, and the spans coincide. Cases: C_3 to C_6 at two pure-Q points, C_3 to
C_7 at s = 1, C4_nilp, the Sylvester-Hadamard E_8 endpoint, a non-symmetrizable control
(rank 0), and a two-block C_3 + C_3 case (rank 2).
Backs: AUDIT-019, VERDICTS.md section 1 row "Fold-sheaf rank-1 results and stress formula
(019)" and section 2 (the object is the relaxed Cauchy-Born tensor, equal to Lubensky et
al. 2015 eq. A4; rank = dimension of the diagonal symmetrizers).
Needs: Python 3 only (fractions). No clone of the target is needed.
Run: python3 -I -B adv_sheaf.py
Time: about 10 seconds. No random numbers are used. Writes no files.
"""
import hashlib
import json
from fractions import Fraction as Fr


def need(c, m):
    if not c:
        raise SystemExit("CHECK FAILED: " + m)


def rref(M):
    A = [row[:] for row in M]
    rows, cols = len(A), len(A[0]) if A else 0
    piv = []
    r = 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        piv.append(c)
        r += 1
        if r == rows:
            break
    return A[:r], piv


def rank(M):
    return len(rref(M)[0]) if M else 0


def nullspace(M, ncols):
    R, piv = rref(M) if M else ([], [])
    free = [c for c in range(ncols) if c not in piv]
    basis = []
    for f in free:
        v = [Fr(0)] * ncols
        v[f] = Fr(1)
        for i, c in enumerate(piv):
            v[c] = -R[i][f]
        basis.append(v)
    return basis


def T(M):
    return [list(r) for r in zip(*M)]


def mm(A, B):
    Bt = T(B)
    return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]


def sym_index(n):
    return [(i, j) for i in range(n) for j in range(i, n)]


def framework(Bm):
    n = len(Bm)
    nodes = []
    for i in range(n):
        for s in (1, -1):
            v = [Fr(0)] * n
            v[i] = Fr(s)
            nodes.append(v)
    N = len(nodes)
    bars = []  # (node_a, node_b, vector b = pos_b' - pos_a)
    for a in range(N):
        for b in range(a + 1, N):
            d = [y - x for x, y in zip(nodes[a], nodes[b])]
            if sum(x * x for x in d) == 2:
                bars.append((a, b, d))
    for i in range(n):
        bars.append((2 * i, 2 * i + 1, [Fr(x) for x in Bm[i]]))
    return nodes, bars


def analyse(Bm):
    n = len(Bm)
    nodes, bars = framework(Bm)
    N = len(nodes)
    for (_, _, b) in bars:
        need(sum(x * x for x in b) == 2, "bar length")
    S_idx = sym_index(n)
    # compatibility matrix Cm: bars x (N*n); affine elongation matrix A: bars x sym (strain eps_ij, i<=j)
    Cm, A = [], []
    for (a, b, d) in bars:
        row = [Fr(0)] * (N * n)
        for k in range(n):
            row[b * n + k] += d[k]
            row[a * n + k] -= d[k]
        Cm.append(row)
        A.append([d[i] * d[j] * (1 if i == j else 2) for (i, j) in S_idx])
    kw = [Fr(1, 2)] * len(bars)  # stiffness 1/|b|^2
    # (a) Schur complement S = A^T k A - A^T k Cm (Cm^T k Cm)^+ Cm^T k A  computed via solving
    kA = [[kw[r] * x for x in A[r]] for r in range(len(bars))]
    kC = [[kw[r] * x for x in Cm[r]] for r in range(len(bars))]
    Kaa = mm(T(A), kA)
    Bca = mm(T(Cm), kA)           # dofs x sym
    Dcc = mm(T(Cm), kC)           # dofs x dofs
    # solve Dcc U = Bca (consistent); use rref on augmented
    m = len(S_idx)
    aug = [Dcc[i] + Bca[i] for i in range(len(Dcc))]
    R, piv = rref(aug)
    ndof = len(Dcc)
    need(all(p < ndof for p in piv), "inconsistent relaxation system")
    U = [[Fr(0)] * m for _ in range(ndof)]
    for i, c in enumerate(piv):
        for j in range(m):
            U[c][j] = R[i][ndof + j]
    BU = mm(T(Bca), U)
    S = [[Kaa[i][j] - BU[i][j] for j in range(m)] for i in range(m)]
    rk_S = rank(S)
    # (b) self-stresses: t with Cm^T t = 0
    SS = nullspace(T(Cm), len(bars))
    sig = []
    for t in SS:
        s = [[sum(t[r] * bars[r][2][i] * bars[r][2][j] for r in range(len(bars))) for j in range(n)] for i in range(n)]
        sig.append(s)
    flat = [[s[i][j] for (i, j) in S_idx] for s in sig]
    rk_sig = rank(flat) if flat else 0
    # (d) Lubensky (A4): S = Sigma_s^T [(k^-1)_ss]^-1 Sigma_s with Sigma_s rows = macro stress (Voigt-weighted) of basis t
    lub_equal = None
    if SS:
        G = [[sum(t1[r] * t2[r] / kw[r] for r in range(len(bars))) for t2 in SS] for t1 in SS]  # t^T k^-1 t
        E = [[sum(t[r] * A[r][c] for r in range(len(bars))) for c in range(m)] for t in SS]    # (E_aff . t) per strain
        # S_lub = E^T G^{-1} E
        aug2 = [G[i] + E[i] for i in range(len(G))]
        R2, piv2 = rref(aug2)
        need(len(piv2) == len(G) and all(p < len(G) for p in piv2), "G singular")
        GiE = [[R2[i][len(G) + j] for j in range(m)] for i in range(len(G))]
        S_lub = mm(T(E), GiE)
        lub_equal = all(S_lub[i][j] == S[i][j] for i in range(m) for j in range(m))
    # (c) diagonal symmetrizers of Bm
    eqs = []
    for i in range(n):
        for j in range(i + 1, n):
            row = [Fr(0)] * n
            row[i] = Fr(Bm[i][j])
            row[j] = -Fr(Bm[j][i])
            eqs.append(row)
    taus = nullspace([r for r in eqs if any(r)], n)
    formula_sig = []
    for tau in taus:
        s = [[sum(Bm[k][i] * tau[k] * Bm[k][j] for k in range(n)) + 2 * tau[i] * Bm[i][j] for j in range(n)] for i in range(n)]
        formula_sig.append(s)
    fflat = [[s[i][j] for (i, j) in S_idx] for s in formula_sig]
    rk_formula = rank(fflat) if fflat else 0
    # do the formula stresses span the same space as the self-stress virials?
    same_span = (rank(flat + fflat) == rk_sig == rk_formula) if (flat or fflat) else True
    trS = sum(S[k][k] for k in range(m))
    return {
        "n": n, "bars": len(bars), "dofs": N * n,
        "zero_modes_H0": N * n - rank(Cm), "self_stresses_H1": len(SS),
        "rank_S_cell": rk_S, "rank_virial_span": rk_sig,
        "dim_diag_symmetrizers": len(taus), "rank_formula_span": rk_formula,
        "formula_span_equals_virial_span": same_span,
        "lubensky_A4_equals_schur": lub_equal,
        "trace_S_tensor_coords": str(trS),
        "formula_stress_if_unique": [[str(x) for x in r] for r in formula_sig[0]] if len(formula_sig) == 1 else None,
    }


def twisted_cycle(n):
    C = [[0] * n for _ in range(n)]
    C[0][1] = -1
    C[0][n - 1] = -1
    C[1][0] = 1
    C[1][2] = -1
    for k in range(2, n - 1):
        C[k][k - 1] = -1
        C[k][k + 1] = -1
    C[n - 1][0] = 1
    C[n - 1][n - 2] = -1
    return C


def bars_from(C, a, t):
    n = len(C)
    return [[(a if i == j else 0) + t * C[i][j] for j in range(n)] for i in range(n)]


def main():
    out = {}
    k = Fr(1)  # team's pure-Q curve point a = 4k/(2k^2+1), t = (2k^2-1)/(2k^2+1)
    for kk in (Fr(1), Fr(3, 2)):
        a = 4 * kk / (2 * kk * kk + 1)
        t = (2 * kk * kk - 1) / (2 * kk * kk + 1)
        need(a * a + 2 * t * t == 2, "curve")
        for n in (3, 4, 5, 6):
            out[f"C{n}_k={kk}"] = analyse(bars_from(twisted_cycle(n), a, t))
    # s = 0 (t = 0): a = sqrt2 not rational -> use the s=1 endpoint and interior points only
    for n in (3, 4, 5, 6, 7):
        out[f"C{n}_s=1"] = analyse(bars_from(twisted_cycle(n), 0, 1))
    nil = [[0, -1, -1, 0], [-1, 0, 0, -1], [1, 0, 0, 1], [0, 1, 1, 0]]
    out["C4nilp_k=1"] = analyse(bars_from(nil, Fr(4, 3), Fr(1, 3)))
    out["C4nilp_s=1"] = analyse(bars_from(nil, 0, 1))
    # E8 Sylvester-Hadamard endpoint: C = H8/2, bars = rows of C (|row|^2 = 2)
    H2 = [[1, 1], [1, -1]]
    H = H2
    for _ in range(2):
        H = [[H[i // 2][j // 2] * H2[i % 2][j % 2] for j in range(2 * len(H))] for i in range(2 * len(H))]
    out["H8_s=1"] = analyse([[Fr(x, 2) for x in r] for r in H])
    # negative control: non-symmetrizable 3-cycle
    C3bad = twisted_cycle(3)
    C3bad[0][1] = 1
    out["C3_nonsymmetrizable_s=1"] = analyse(bars_from(C3bad, 0, 1))
    # beyond the team: block bridge matrix with a 2-dim symmetrizer space (two disjoint twisted 3-cycles, n=6)
    blk = [[0] * 6 for _ in range(6)]
    c3 = twisted_cycle(3)
    for i in range(3):
        for j in range(3):
            blk[i][j] = c3[i][j]
            blk[3 + i][3 + j] = c3[i][j]
    out["two_blocks_C3+C3_n6_s=1"] = analyse(bars_from(blk, 0, 1))
    txt = json.dumps(out, sort_keys=True, indent=1)
    print(txt)
    print("SHA256", hashlib.sha256(txt.encode()).hexdigest())
    problems = []
    for name, r in out.items():
        if not (r["rank_S_cell"] == r["rank_virial_span"] == r["dim_diag_symmetrizers"] == r["rank_formula_span"]):
            problems.append(name + ": ranks disagree")
        if r["formula_span_equals_virial_span"] is not True:
            problems.append(name + ": spans differ")
        if r["self_stresses_H1"] and r["lubensky_A4_equals_schur"] is not True:
            problems.append(name + ": Lubensky A4 differs from the Schur complement")
        want = 0 if "nonsymmetrizable" in name else 2 if "two_blocks" in name else 1
        if r["rank_S_cell"] != want:
            problems.append("%s: rank %d, expected %d" % (name, r["rank_S_cell"], want))
    if problems:
        raise SystemExit("CHECK FAILED: " + "; ".join(problems))
    print("RESULT leech_sheaf/adv_sheaf: PASS %d cases, rank S = virial span = diagonal symmetrizers = formula span "
          "(rank 1 for twisted cycles, C4_nilp and H8; 0 for the control; 2 for two blocks), Lubensky A4 equals the Schur complement"
          % len(out))


if __name__ == "__main__":
    main()
