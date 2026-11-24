"""Task 1: clean-room builders.  Emits canonical JSON objects for each real pair.
usage: build_objects.py <objects dir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g5lib import *
from g5more import *

CONVENTIONS = {
    "cell": "16 vertices +-e_i (vertex index 2*axis+sign, sign 0 = +); u-dofs: 8 coordinates per vertex, index vertex*8+coord (128 total)",
    "bars": "112 intra-cell bars (+-e_i to +-e_j, i<j) with m=0, then 8 bridge bars i: from +e_i in cell 0 to -e_i in cell e_i, m=e_i, ell = r_i - 2e_i = b_i (row i of B = L - 2I)",
    "bar_vector": "ell = x_v - x_u + m.L ; elongation row of u-dofs: ell at vertex v, -ell at vertex u; weight W = 1/2 on every bar",
    "strain_coordinates": "36 = 8 diagonal eps_kk then 28 off-diagonal eps_kl (k<l, lexicographic), eps symmetric with eps_kl=eps_lk=coordinate; strain row of a bar: (ell_k^2 | 2 ell_k ell_l)",
    "dL_coordinates": "64 = entries (k,l) of a lattice deformation dL, index k*8+l; Z-row of a bar: m_k ell_l",
    "Phi": "Phi : (u, eps) -> (dx, dL) = (u + X eps, L eps).  X eps = affine displacement x_v eps of every vertex; L eps = lattice basis deformed by eps.  Domain = elasticity coordinates (u in R^128, eps in R^36), codomain = lattice-side deformation coordinates (dx in R^128, dL in R^64).  Block upper triangular for the partitions (internal | macro): [[I, X],[0, R]]",
    "H_lat": "H_lat = R_lat^T W R_lat on (dx | dL), R_lat rows = [d0 row | Z row]; H_el = R_el^T W R_el on (u | eps), R_el rows = [d0 row | strain row].  Identity R_el = R_lat Phi, hence H_el = Phi^T H_lat Phi",
    "elasticity": "K = ae^T W ae, B = d0^T W ae, Delta = d0^T W d0 ; S = K - B^T Delta^+ B (Delta^+ : consistent solve, free variables 0) ; C = S / det L (volume normalisation)",
}


def sparse_of(M):
    out = []
    for i, r in enumerate(M):
        for j, v in enumerate(r):
            if v != 0:
                out.append([i, j, enc(v)])
    return out


def build(name, spec):
    L = spec["L"]
    n = len(L)
    F = Framework(L)
    B = bridge_of(L)
    G = gram(L)
    P = spec["part"]
    G11 = submat(G, P[0], P[0])
    G12 = submat(G, P[0], P[1])
    G22 = submat(G, P[1], P[1])
    X = solve_dense(G11, G12)
    schurG = madd(G22, matmul(transpose(G12), X), -1)
    detL = det_small(L)
    S, (K, Bm, Delta) = F.schur_direct()
    Sl, (Kl, Bl, Dl) = F.schur_lat_direct()
    Phi = matrix_Phi(L)
    obj = {
        "instance": name,
        "ring": spec["ring"],
        "note": spec["note"],
        "n": n,
        "conventions": CONVENTIONS,
        "L": encmat(L),
        "bridge_B": encmat(B),
        "det_L": enc(detL),
        "lattice_side": {
            "gram_G": encmat(G),
            "partition": P,
            "det_G": enc(det_small(G)),
            "det_G11": enc(det_small(G11)),
            "schur_G_over_G11": encmat(schurG),
            "det_schur": enc(det_small(schurG)),
        },
        "dimensions": {"bars": F.nb, "u": F.nu, "eps": F.ne, "dL": F.ndl, "Phi_shape": [F.nu + F.ndl, F.nu + F.ne]},
        "bars": [{"u": b[0], "v": b[1], "m": b[2], "ell": [enc(x) for x in b[3]]} for b in F.bars],
        "Phi_sparse": sparse_of(Phi),
        "elasticity": {
            "K_sparse": sparse_of(K),
            "B_sparse": sparse_of(Bm),
            "Delta_sparse": sparse_of(Delta),
            "S": encmat(S),
            "C_over_detL": encmat([[x / detL for x in r] for r in S]),
        },
        "lattice_side_schur": {"S_lat_sparse": sparse_of(Sl)},
    }
    return obj, S, Sl


def main():
    if len(sys.argv) != 2:
        print("usage: build_objects.py <objects dir>")
        return 2
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    for name, spec in instances().items():
        obj, S, Sl = build(name, spec)
        text = canon(obj)
        with open(os.path.join(outdir, "pair_" + name + ".json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("OBJECT", name, "ring", spec["ring"], "det_L", obj["det_L"], "S_inertia", inertia(S), "S_trace", enc(tr(S)),
              "S_lat_inertia", inertia(Sl), "sha256", sha(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
