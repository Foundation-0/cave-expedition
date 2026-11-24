"""Object suite: seeded rational points for the three domains, with exact invariants."""
from __future__ import annotations

from fractions import Fraction

from domains import *

SEED_Q = 20261121101
SEED_G = 20261121202
SEED_S = 20261121303

LIOUV_ANCHOR_NS = (1, 2, 3, 5, 10, 20, 50, 100)
GRAV_ANCHOR = [  # (label, KB, lam, Kpp, r) read from the committed results of the gravity probe
    ("UV_stable", 1, 1, 4, 9), ("CRITICAL", 1, 1, 4, 8), ("IR_clustering", 1, 1, 4, 7), ("lam0", 1, 0, 4, 4)]


def kind_of(X):
    if not is_real_entries(X):
        return "hermitian" if is_hermitian(X) else "neither"
    if is_symmetric(X):
        return "symmetric"
    if is_antisymmetric(X):
        return "antisymmetric"
    return "neither"


def classes(d):
    if d == 0:
        return None
    return {"sq": list(sqfree_class(d)), "norm": list(norm_class(d))}


def invariants(X):
    """exact invariants of a square matrix over Q or Q(i); inertia only if Hermitian"""
    k = kind_of(X)
    d = det(X)
    out = {"size": len(X), "kind": k, "rank": rank(X), "det": enc(d)}
    out["det_class"] = classes(realpart(d)) if (d != 0 and (k in ("hermitian", "symmetric") or is_real_entries(X))) else None
    if k in ("hermitian", "symmetric"):
        out["inertia"] = list(inertia(X))
    else:
        out["inertia"] = None
        S = symm_part(X)
        out["inertia_of_symmetric_part"] = list(inertia(S)) if is_real_entries(X) else None
    return out


def block_report(X, piv, rest):
    App = sub(X, piv, piv)
    R = schur(X, piv, rest)
    sp = symm_part(App) if is_real_entries(App) else App
    pin = inertia(sp)
    return {
        "pivot_indices": piv, "rest_indices": rest,
        "pivot_kind": kind_of(App), "pivot_inertia_of_symmetric_part": list(pin),
        "pivot_definite": pin[0] == len(piv) or pin[1] == len(piv),
        "pivot_sign": (1 if pin[0] == len(piv) else (-1 if pin[1] == len(piv) else 0)),
        "pivot_det": enc(det(App)),
        "reduced": matstr(R), "reduced_inv": invariants(R),
        "full_inv": invariants(X),
    }, R


def liouv_params():
    rng = Rng(SEED_Q)
    pts = []
    for N in LIOUV_ANCHOR_NS:
        pts.append(("anchor_N%d" % N, N, Fraction(1, 4), Fraction(3, 2), Fraction(1, 100), Fraction(0)))
    for i in range(7):
        pts.append(("seeded_%d" % i, rng.randint(1, 6), Fraction(rng.randint(1, 5), rng.randint(1, 4)),
                    Fraction(rng.randint(1, 6), rng.randint(1, 3)), Fraction(rng.randint(1, 5), rng.randint(10, 60)), Fraction(0)))
    for i in range(2):
        pts.append(("seeded_omega_%d" % i, rng.randint(1, 4), Fraction(rng.randint(1, 5), rng.randint(1, 4)),
                    Fraction(rng.randint(1, 6), rng.randint(1, 3)), Fraction(rng.randint(1, 5), rng.randint(10, 60)),
                    Fraction(rng.randint(1, 5), rng.randint(1, 3))))
    return pts


def grav_params():
    rng = Rng(SEED_G)
    pts = [(l, Fraction(a), Fraction(b), Fraction(c), Fraction(d)) for (l, a, b, c, d) in GRAV_ANCHOR]
    for i in range(10):
        pts.append(("seeded_%d" % i, Fraction(rng.randint(1, 7), 4), Fraction(rng.randint(0, 6), rng.randint(1, 3)),
                    Fraction(rng.randint(1, 8), rng.randint(1, 3)), Fraction(rng.randint(1, 40), rng.randint(1, 4))))
    return pts


def spec_params():
    rng = Rng(SEED_S)
    pts = []
    rejected = 0
    while len(pts) < 12:
        n = rng.randint(3, 4)
        rp = rng.randint(1, n)
        bp = rng.randint(1, n - 1) if len(pts) % 3 != 2 else 2
        P, Q, M, UQ = spectral_system(n, rp, bp, rng, regime1=True)
        u, t, S, b = spectral_scalars(P, Q, M, bp)
        Ro = R_opt(u, t, S, b)
        if Ro is None:
            rejected += 1
            continue
        pts.append({"label": "seeded_%d" % len(pts), "n": n, "rank_P": rp, "b": bp, "P": P, "Q": Q, "M": M, "UQ": UQ,
                    "u": u, "t": t, "S": S, "Ropt": Ro})
    return pts, rejected


def build_liouv(pt):
    label, N, g1, g, gt, om = pt
    L, order, pi, pw = liouvillian(N, g1, g, gt, om)
    rep, R = block_report(L, pw, pi)
    gcm = fr(N) * fr(N) * g1
    rep.update({"domain": "open_quantum", "label": label, "params": {"N": str(N), "gamma1": str(g1), "g": str(g), "gamma_tid": str(gt), "omega": str(om)},
                "basis": order, "full": matstr(L), "base_ring": "Q",
                "Gamma_eff_formula": enc(2 * gt + 2 * g * g / gcm)})
    ix = order.index("IX")
    rep["reduced_IX_entry"] = enc(R[ix][ix])
    return rep, (L, pi, pw, R, order)


def build_grav(pt):
    label, KB, lam, Kpp, r = pt
    Hm = aest_hessian(KB, lam, Kpp, r)
    rep, R = block_report(Hm, [0, 1], [2])
    ga = G_AA(KB, lam, Kpp, r)
    rep.update({"domain": "aest_gravity", "label": label, "params": {"KB": str(KB), "lam": str(lam), "Kpp": str(Kpp), "r_eq_k2": str(r)},
                "basis": ["chi", "p", "P"], "full": matstr(Hm), "base_ring": "Q",
                "G_AA": enc(ga), "S_P_equals_minus_GAA_over_4r": R[0][0] == -ga / (4 * r),
                "min_H2_coeff_of_D2": enc(R[0][0] * 2)})  # P=-2D: S_P*P^2/2 = 2 S_P D^2
    return rep, (Hm, [0, 1], [2], R)


def build_spec(pt):
    P, Q, M, UQ = pt["P"], pt["Q"], pt["M"], pt["UQ"]
    n, b = pt["n"], pt["b"]
    u, t, S, Ro = pt["u"], pt["t"], pt["S"], pt["Ropt"]
    perp = list(range(b, n))
    Up = [[UQ[i][j] for j in perp] for i in range(n)]
    Hp = mm(mm(dag(Up), M), Up)
    Pp = mm(mm(dag(Up), P), Up)
    pos_Hp = inertia(Hp)[0]
    chain = {"rank_P": rank(P), "rank_P_perp": rank(Pp), "n_plus_H_perp": pos_Hp, "R_opt": enc(Ro),
             "ok": rank(P) >= rank(Pp) >= pos_Hp and fr(pos_Hp) >= Ro}
    G = G2(S, t, b)
    rep, R = block_report(G, [1], [0])
    Bm = G2_bordered(S, t, b, u)
    repB, RB = block_report(Bm, [0, 1], [2])
    out = {"domain": "spectral_inertia", "label": pt["label"], "n": n, "b": b,
           "scalars": {"u": enc(u), "t": enc(t), "S": enc(S)},
           "M_full": matstr(M), "M_kind": kind_of(M), "M_inv": invariants(M), "chain": chain,
           "G": rep, "B": repB, "base_ring": "Q(i) for M, Q for G and B",
           "Ropt_from_G": enc(u * u / R[0][0]), "Ropt_equals_minus_B_schur": RB[0][0] == -Ro, "Ropt_equals_u2_G11inv": u * u * inv(G)[0][0] == Ro}
    return out, (M, G, Bm, R, RB, u, t, S, b, Ro)


def all_objects():
    L = [build_liouv(p) for p in liouv_params()]
    Gv = [build_grav(p) for p in grav_params()]
    sp_pts, rej = spec_params()
    Sp = [build_spec(p) for p in sp_pts]
    return L, Gv, Sp, rej


def object_documents():
    """filename -> canonical JSON text of the objects (what build_objects.py writes and compare.py re-checks)"""
    L, Gv, Sp, rej = all_objects()
    docs = {
        "open_quantum_liouvillian.json": {"domain": "open_quantum", "seed": SEED_Q, "convention": "inertia is (positive, negative, zero); matrices are exact rationals as strings",
                                           "points": [r for r, _ in L]},
        "aest_gravity_hamiltonian.json": {"domain": "aest_gravity", "seed": SEED_G, "convention": "inertia is (positive, negative, zero); matrices are exact rationals as strings",
                                           "points": [r for r, _ in Gv]},
        "spectral_inertia_hermitian.json": {"domain": "spectral_inertia", "seed": SEED_S, "draws_rejected_outside_regime_1": rej,
                                             "convention": "inertia is (positive, negative, zero); Q(i) entries as re+imi",
                                             "points": [r for r, _ in Sp]},
    }
    return {k: canon_json(v) for k, v in docs.items()}
