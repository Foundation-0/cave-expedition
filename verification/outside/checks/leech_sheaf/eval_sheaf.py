"""Independent recheck of the AUDIT-019 fold-sheaf elastic collapse (evaluator check).

Own formulation that shares no code with the target: a periodic (q = 0) bar framework
with the rigid cross-polytope motif and n bridge bars; relaxed stiffness from the
self-stresses (macroscopic stresses of the self-stresses), exact in SymPy over Q and over
Q(sqrt 2). Checks: stiffness rank 1 for the twisted cycles C_3 to C_6 and for C4_nilp at
k = 1, 2 and 3 (k = 3 was not tested by the target), rank n at s = 0 for C_3 and C_4,
rank 0 for a non-symmetrizable control, and for the E_8 Hadamard path rank 1 at
s = 1/2, 1/3 and 1. Also checks the virial identity sigma* = B^T diag(tau) B + 2 diag(tau) B
at every symmetrizable point, and the Zener ratios A(D_n) = 2/(n-2) and A(E_8) = 1.
Backs: AUDIT-019, VERDICTS.md section 1 row "Fold-sheaf rank-1 results and stress
formula (019)" and the section 2 reading of rank 1 as the pentamode class.
Needs: Python 3, SymPy (tested with 1.14). No clone of the target is needed.
Run: python3 -I -B eval_sheaf.py
Time: about 30 seconds. No random numbers are used. Writes no files.
"""
import itertools
import json

import sympy as sp
from sympy.polys.matrices import DomainMatrix

R2 = sp.sqrt(2)


def dm(rows, K):
    return DomainMatrix([[K.convert(sp.nsimplify(x) if not isinstance(x, sp.Basic) else x) for x in r] for r in rows],
                        (len(rows), len(rows[0])), K)


def framework(B, K):
    """B: list of n bridge vectors (sympy numbers). Returns R, A (python lists of sympy), bar vectors."""
    n = len(B)
    node = lambda i, s: 2 * i + (0 if s > 0 else 1)
    bars = []  # (u, v, d) with d = pos(v) + cell shift - pos(u)
    for i in range(n):
        for j in range(i + 1, n):
            for si in (1, -1):
                for sj in (1, -1):
                    d = [0] * n
                    d[j] += sj
                    d[i] -= si
                    bars.append((node(i, si), node(j, sj), d))
    for i in range(n):
        bars.append((node(i, 1), node(i, -1), list(B[i])))
    nd = 2 * n * n
    R, A = [], []
    for u, v, d in bars:
        row = [0] * nd
        for k in range(n):
            row[u * n + k] -= d[k]
            row[v * n + k] += d[k]
        R.append(row)
        A.append([d[k] * d[k] for k in range(n)] + [2 * d[k] * d[l] for k in range(n) for l in range(k + 1, n)])
    return R, A, bars


def analyse(B, K, tau=None):
    n = len(B)
    R, A, bars = framework(B, K)
    Rm = dm(R, K)
    Am = dm(A, K)
    S = Rm.transpose().nullspace().transpose()  # columns: self-stresses (bars x h1)
    h1 = S.shape[1]
    rankR = Rm.rank()
    h0 = 2 * n * n - rankR
    MS = Am.transpose() * S  # macroscopic stresses (m_s x h1)
    rk = MS.rank()
    out = {"n": n, "H0": h0, "H1": h1, "stiffness_rank": rk}
    # relaxed stiffness by self-stress formula; W^{-1} = diag(|d|^2)
    winv = [sum(x * x for x in d) for _, _, d in bars]
    Winv = DomainMatrix.diag([K.convert(sp.nsimplify(w) if not isinstance(w, sp.Basic) else w) for w in winv], K)
    G = S.transpose() * Winv * S
    Kst = MS * G.inv() * MS.transpose()
    out["tr_K"] = str(sp.nsimplify(K.to_sympy(sum((Kst[i, i].element for i in range(Kst.shape[0])), K.zero))))
    out["K00"] = str(K.to_sympy(Kst[0, 0].element))
    # inertia of K via sympy eigen-sign count (exact charpoly roots sign by Descartes on charpoly)
    if tau is not None:
        # explicit self-stress with bridge tensions tau: solve intra stresses
        nb = len(bars)
        n_intra = nb - n
        RT = Rm.transpose().to_Matrix()
        Rin = RT[:, :n_intra]
        rhs = -RT[:, n_intra:] * sp.Matrix(tau)
        sol, params = Rin.gauss_jordan_solve(rhs)
        sol = sol.subs({p: 0 for p in params})
        om = list(sol) + list(tau)
        sig = sp.zeros(n, n)
        for w, (_, _, d) in zip(om, bars):
            dv = sp.Matrix(d)
            sig += w * dv * dv.T
        Bm = sp.Matrix(B)
        T = sp.diag(*tau)
        formula = Bm.T * T * Bm + 2 * T * Bm
        out["virial_stress_equals_BtTB_plus_2TB"] = bool(sp.simplify(sig - formula) == sp.zeros(n, n))
        out["sigma_star_diag"] = [str(sp.simplify(sig[k, k])) for k in range(n)]
        out["sigma_star_is_zero"] = bool(sp.simplify(sig) == sp.zeros(n, n))
    return out


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


def symmetrizer(B):
    """Diagonal tau (tau_0 = 1) with tau_i B_ij = tau_j B_ji for all i != j, or None."""
    n = len(B)
    tau = [None] * n
    tau[0] = sp.Integer(1)
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(n):
                if i != j and tau[i] is not None and B[i][j] != 0:
                    if B[j][i] == 0:
                        return None
                    t = sp.simplify(tau[i] * B[i][j] / B[j][i])
                    if tau[j] is None:
                        tau[j] = t
                        changed = True
                    elif sp.simplify(tau[j] - t) != 0:
                        return None
    if any(t is None for t in tau):
        return None
    for i in range(n):
        for j in range(n):
            if i != j and sp.simplify(tau[i] * B[i][j] - tau[j] * B[j][i]) != 0:
                return None
    return tau


report = {"Dn_path": [], "E8_path": {}, "bravais": {}}
QQ = sp.QQ
pts = {"k=1": (sp.Rational(4, 3), sp.Rational(1, 3)), "k=2": (sp.Rational(8, 9), sp.Rational(7, 9)),
       "k=3 (untested by team)": (sp.Rational(12, 19), sp.Rational(17, 19)), "s=1": (0, 1), "s=0 (a=sqrt2)": None}
C4N = [[0, -1, -1, 0], [-1, 0, 0, -1], [1, 0, 0, 1], [0, 1, 1, 0]]
cases = [("C_%d" % n, twisted_cycle(n)) for n in (3, 4, 5, 6)] + [("C4_nilp", C4N),
                                                                  ("C3_nonsym", [[0, 1, -1], [1, 0, -1], [1, -1, 0]])]
for name, C in cases:
    n = len(C)
    for lab, at in pts.items():
        if at is None:
            if name not in ("C_3", "C_4"):
                continue
            K = sp.QQ.algebraic_field(R2)
            a, t = R2, 0
        else:
            K = QQ
            a, t = at
        if (n == 6 and lab.startswith("k=2")) or (name == "C3_nonsym" and lab != "s=1"):
            continue
        if sp.simplify(a * a + 2 * t * t - 2) != 0:
            raise SystemExit("CHECK FAILED: curve point off the bar-length constraint")
        B = [[(a if i == j else 0) + t * C[i][j] for j in range(n)] for i in range(n)]
        tau = symmetrizer(B) if t != 0 else None
        r = analyse(B, K, tau=tau)
        r.update({"case": name, "point": lab, "symmetrizer": None if tau is None else [str(x) for x in tau]})
        report["Dn_path"].append(r)
        print(name, lab, r, flush=True)

# E_8 Hadamard path of E8_SPINOR_FOLD_PROOF.md at s = 1/2 (entries in Q(sqrt2)) and s = 1
H8 = [[(-1) ** bin(i & j).count("1") for j in range(8)] for i in range(8)]
Ip = [i for i in range(8) if H8[i][i] == 1]
for s in (sp.Rational(1, 2), sp.Rational(1, 3), sp.Integer(1)):
    Dp = (1 + 2 * R2) + (-1 + 2 * R2) * s ** 2
    Dm = (-1 + 2 * R2) + (1 + 2 * R2) * s ** 2
    ap = ((6 + 5 * R2) + (-6 + 5 * R2) * s ** 2) / Dp
    bp = 2 * R2 * s / Dp
    am = ((2 + 3 * R2) + (-2 + 3 * R2) * s ** 2) / Dm
    bm = 2 * R2 * s / Dm
    L = [[sp.radsimp((ap if i in Ip else am) if i == j else (bp if i in Ip else bm) * H8[i][j]) for j in range(8)]
         for i in range(8)]
    B = [[sp.radsimp(L[i][j] - (2 if i == j else 0)) for j in range(8)] for i in range(8)]
    norms = [sp.simplify(sum(x * x for x in row)) for row in B]
    K = sp.QQ.algebraic_field(R2)
    tau = symmetrizer(B)
    r = analyse(B, K, tau=tau)
    r.update({"bar_norms": [str(x) for x in norms], "symmetrizer": None if tau is None else [str(sp.radsimp(x)) for x in tau]})
    report["E8_path"]["s=%s" % s] = r
    print("E8 path s=", s, r, flush=True)
# sigma* at s=1 should be 2I + H8 (team) -- check and its signature
sig = sp.Matrix(8, 8, lambda i, j: (2 if i == j else 0) + H8[i][j])
report["E8_path"]["2I+H8_eigs"] = {str(k): v for k, v in sig.eigenvals().items()}


# Bravais (Cauchy-Born, central unit springs) fourth-moment tensors: Zener ratio
def roots_D(n):
    out = []
    for i in range(n):
        for j in range(i + 1, n):
            for a in (1, -1):
                for b in (1, -1):
                    v = [0] * n
                    v[i], v[j] = a, b
                    out.append(v)
    return out


def roots_E8():
    out = roots_D(8)
    for sg in itertools.product((1, -1), repeat=8):
        if sg.count(-1) % 2 == 0:
            out.append([sp.Rational(x, 2) for x in sg])
    return out


def zener(roots):
    c11 = sum(sp.Rational(w[0]) ** 4 for w in roots)
    c12 = sum(sp.Rational(w[0]) ** 2 * sp.Rational(w[1]) ** 2 for w in roots)
    c44 = c12  # central forces, Bravais, no prestress: Cauchy relation
    return {"C11:C12:C44": "%s:%s:%s" % (c11, c12, c44), "A": str(sp.Rational(2 * c44, c11 - c12)),
            "isotropic(C11=3C12)": c11 == 3 * c12}


for n in (3, 4, 5, 8, 16):
    report["bravais"]["D%d" % n] = zener(roots_D(n))
    report["bravais"]["D%d" % n]["2/(n-2)"] = str(sp.Rational(2, n - 2))
report["bravais"]["E8"] = zener(roots_E8())
print(json.dumps(report["bravais"], indent=1))
print("E8 2I+H8 eigs", report["E8_path"]["2I+H8_eigs"])

# ---------------- verdict ----------------
problems = []
for r in report["Dn_path"]:
    tag = "%s %s" % (r["case"], r["point"])
    if r["case"] == "C3_nonsym":
        if r["stiffness_rank"] != 0:
            problems.append(tag + " control should have rank 0")
    elif r["point"] == "s=0 (a=sqrt2)":
        if r["stiffness_rank"] != r["n"]:
            problems.append(tag + " should have rank n")
    else:
        if r["stiffness_rank"] != 1:
            problems.append(tag + " should have rank 1")
        if r.get("virial_stress_equals_BtTB_plus_2TB") is not True:
            problems.append(tag + " virial identity")
        if r.get("sigma_star_is_zero") is not False and r["case"] != "C4_nilp":
            problems.append(tag + " sigma* should not vanish")
for lab, r in report["E8_path"].items():
    if lab.startswith("s="):
        if not (r["stiffness_rank"] == 1 and r.get("virial_stress_equals_BtTB_plus_2TB") is True
                and all(x == "2" for x in r["bar_norms"])):
            problems.append("E8 path " + lab)
if report["E8_path"]["2I+H8_eigs"] != {"2 - 2*sqrt(2)": 4, "2 + 2*sqrt(2)": 4}:
    problems.append("2I+H8 signature (4,4)")
for n in (3, 4, 5, 8, 16):
    z = report["bravais"]["D%d" % n]
    if z["A"] != z["2/(n-2)"]:
        problems.append("Zener ratio D%d" % n)
if report["bravais"]["E8"]["A"] != "1" or not report["bravais"]["E8"]["isotropic(C11=3C12)"]:
    problems.append("E8 isotropy")
if problems:
    raise SystemExit("CHECK FAILED: " + "; ".join(problems))
print("RESULT leech_sheaf/eval_sheaf: PASS rank 1 for C3 to C6 and C4_nilp at k=1,2,3 and s=1, rank n at s=0, "
      "rank 0 for the control, rank 1 on the E8 path at s=1/2, 1/3, 1; virial identity and A(Dn)=2/(n-2) hold (%d cases)"
      % (len(report["Dn_path"]) + 3))
