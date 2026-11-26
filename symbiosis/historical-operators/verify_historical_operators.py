#!/usr/bin/env python3
"""Historical Exact-Operator Applications & Gate-5 Congruence Boundaries for Cave Expedition.

Standalone pure Python 3 standard-library verifier (int, fractions.Fraction,
math.gcd; zero AST float literals, zero float() calls, zero math.log, zero bare
asserts, CPU-only).

Certifies three exact theorem families over Z, Q, and Q(sqrt(2)) extending
AUDIT-002, AUDIT-004, AUDIT-009, AUDIT-010, AUDIT-014, AUDIT-017, AUDIT-018,
AUDIT-019, and AUDIT-020R while honoring and sharpening the outside Gate-5 ruling
in README.md section 1 (distinguishing true Sylvester congruence from shared block
elimination, without modifying verification/checks/check_003_seam01_ropt.py):

  1. Physical Schur Pushforwards & Machine-Checked Gate-5 Congruence Theorem:
     - Petra Siq 6-stage terracotta conduit vented surge attenuation (1/3 -> 64/1365).
     - Roman Lyon Gier 9-pipe inverted siphon fault tolerance (conductances 9/1, 8/1, 7/1; ratios 8/9, 7/9).
     - Amazonian Casarabe radial-ring canal graph C_{2,6} (13 nodes, 24 edges,
       betti_1 = 12): hub-to-rim Schur conductance 2755/1806 > 13/42 (ring C_13)
       > 1/12 (tree T_13), retaining 427248/498655 after primary spoke cut.
     - Ibn al-Nafis readable-record 3x3 -> 2x2 covariance Schur pushforward
       (det: 34/625 -> 688/15625, trace drop 81/1250, extending AUDIT-018).
     - Self-certifying GL_n(Q) congruence P^T M P = diag(d) proving exact [4, 4, 0]
       Sylvester congruence between AUDIT-019's H_8 fold-sheaf stress operator
       2*I_8 + H_8 and AUDIT-017's shifted Gram operator 2*(G(1) - 2*I_8), alongside
       provable Gate-5 non-congruence against passive PSD hydraulic M-matrix
       Laplacians (n_neg == 0, matched-dimension 8x8 conduit [7, 0, 1]).

  2. Discrete Parity, Chokwe Sona Sheaf Nullity & Al-Biruni Stereographic Folds:
     - Pingala nasta(3, k) character table reproduces Sylvester-Hadamard H_8 (64/64).
     - The 128 even-parity Yoruba Ifa 8-bit words map bijectively onto the 128
       spinor roots of E_8 (128 + 112 = 240 kissing roots in AUDIT-017).
     - All 32 affine Boolean functions on Bamana GF(2)^4 (RM(1, 4), Barnes-Wall
       Lambda_16 spinor layer in AUDIT-020R) are GF(2)^16-orthogonal across all 5
       extended Hamming [16, 11, 4] parity-check rows.
     - Exact Q coboundary rank on Chokwe Sona mirror curves across all 16 grids
       1 <= m, n <= 4 proves dim ker Delta_F == gcd(m, n) ([2 -> 1] internal wall
       merge on 2x2; [1 -> 2] internal wall split on 2x3, extending AUDIT-004/019).
     - Exact Q(sqrt(2)) identity proving both AUDIT-009 (F_n -> D_n, kappa^2 = 1)
       and AUDIT-017 (F_8 -> E_8, kappa_pm^2 = (9 -+ 4*sqrt(2))/7) bar-preserving
       folds are Al-Biruni stereographic meridian lifts preserving ||b_i(s)||^2 == 2.

  3. Zero-Log Multiplicative Farkas & Madhava-Hankel Spectral Tightening:
     - Al-Farabi 53-TET pairwise multiplicative Farkas sheaf obstruction (local
       steps pass 31/53; global span fails via 3^53 > 2^84, extending AUDIT-010).
     - Zu Chongzhi 355/113 4-ray Farkas log-concavity refutation (local 3-pt rays
       (1,0),(0,1) pass while non-local 4-pt rays (2,1),(1,2) refute, verified
       against an independent Q Fourier-Motzkin elimination oracle).
     - Madhava (R_2(n), R_3(n)) rational tail closure tightening AUDIT-014's 4th-
       moment Stieltjes-Hankel bound R_{H,4} on P(sigma) = diag(2, 1, 4/5 - sigma)
       (sigma = pi/4): at n = 2 terms, 2-moment ceil(R_opt) == 2 and raw Leibniz
       ceil(R_{H,4}^raw) == 2, whereas Madhava certifies ceil(R_{H,4}^Madhava) == 3
       == rank(P) and narrows the R_{H,4} enclosure width at n = 20 by 1,314,575x.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import hmac
import itertools
import json
import math
from pathlib import Path
import sys
from typing import Any


SCHEMA_VERSION = "cave-expedition.historical-operators-gate5.v2"
ARITHMETIC_DOMAIN = "exact_Z_Q_Qs2_stdlib_zero_floats_zero_logs"
GATE5_SCOPE_STATEMENT = (
    "Eight frontiers each use block elimination; AUDIT-017 and AUDIT-019 share an "
    "exact Sylvester congruence [4,4,0], whereas passive hydraulic M-matrix "
    "Laplacians have n_neg == 0 and share block elimination only."
)
EXTERNAL_REFERENCES_STATUS = "CITED_EXTERNAL_NOT_REHASHED_HERE"

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_CERT_PATH = SCRIPT_DIR / "historical_operators_certificate.json"

HEX_LOWER = frozenset("0123456789abcdef")

OUTSIDE_ANCHOR_KEY = "outside_anchor_check_003_seam01_ropt_py"
OUTSIDE_ANCHOR_RELPATH = "verification/checks/check_003_seam01_ropt.py"
OUTSIDE_ANCHOR_SHA256 = "ae239507fecea4fdd9d5d0ef2e298483ddf040067b5987dffdeb684873feac86"
ON_DISK_ANCHOR_SPECS: dict[str, tuple[str, str]] = {
    OUTSIDE_ANCHOR_KEY: (OUTSIDE_ANCHOR_RELPATH, OUTSIDE_ANCHOR_SHA256),
}


# ---------------------------------------------------------------------------
# Fail-Closed Primitives & Boolean Predicates
# ---------------------------------------------------------------------------


def require_ok(cond: bool, msg: str) -> None:
    """Fail-closed runtime invariant check preserved under python3 -O."""
    if not cond:
        raise ValueError(msg)


def require_fraction(val: Any, name: str) -> Fraction:
    """Require an exact fractions.Fraction instance."""
    require_ok(isinstance(val, Fraction), f"{name} must be Fraction")
    return val


def is_exact_int(val: Any) -> bool:
    """Return True iff val is an int and not a bool."""
    return isinstance(val, int) and not isinstance(val, bool)


def is_hex64(val: Any) -> bool:
    """Return True iff val is a 64-character lowercase hexadecimal string."""
    return isinstance(val, str) and len(val) == 64 and set(val) <= HEX_LOWER


def is_strict_open_bracket_q(lo: Fraction, val: Fraction, hi: Fraction) -> bool:
    """Return True iff lo < val < hi in exact Q."""
    require_fraction(lo, "lo")
    require_fraction(val, "val")
    require_fraction(hi, "hi")
    return lo < val and val < hi


def require_inertia_triple(val: Any, name: str) -> tuple[int, int, int]:
    """Validate an exact non-negative 3-tuple (n_pos, n_neg, n_zero)."""
    require_ok(isinstance(val, tuple), f"{name} must be tuple")
    require_ok(len(val) == 3, f"{name} must have length 3")
    for idx, entry in enumerate(val):
        require_ok(is_exact_int(entry), f"{name}[{idx}] must be int")
        require_ok(entry >= 0, f"{name}[{idx}] must be >= 0")
    return val


def are_inertias_congruence_compatible(
    in_x: tuple[int, int, int], in_y: tuple[int, int, int]
) -> bool:
    """Sylvester's Law of Inertia necessary & sufficient signature match."""
    rx = require_inertia_triple(in_x, "in_x")
    ry = require_inertia_triple(in_y, "in_y")
    return rx[0] == ry[0] and rx[1] == ry[1] and rx[2] == ry[2]


def require_4boxes_q(
    boxes: Any, positive_only: bool
) -> tuple[
    tuple[Fraction, Fraction],
    tuple[Fraction, Fraction],
    tuple[Fraction, Fraction],
    tuple[Fraction, Fraction],
]:
    """Validate 4 rational interval boxes [lo_k, hi_k] (requiring lo_k > 0 if positive_only)."""
    require_ok(isinstance(boxes, tuple), "boxes must be tuple")
    require_ok(len(boxes) == 4, "boxes must have length 4")
    for idx, pair in enumerate(boxes):
        require_ok(isinstance(pair, tuple), f"boxes[{idx}] must be tuple")
        require_ok(len(pair) == 2, f"boxes[{idx}] must have length 2")
        require_fraction(pair[0], f"boxes[{idx}][0]")
        require_fraction(pair[1], f"boxes[{idx}][1]")
        if positive_only:
            require_ok(pair[0] > Fraction(0, 1), f"boxes[{idx}][0] must be > 0")
        require_ok(pair[0] <= pair[1], f"boxes[{idx}] must satisfy lo <= hi")
    return boxes


def farkas_4ray_log_concave_status_q(
    boxes: tuple[
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
    ],
) -> dict[str, bool]:
    """Evaluate all 4 integer Farkas log-concavity rays on 4 interval boxes [y_k^-, y_k^+]."""
    checked = require_4boxes_q(boxes, positive_only=True)
    (y0_lo, _), (y1_lo, y1_hi), (y2_lo, y2_hi), (y3_lo, _) = checked
    ray_10 = y0_lo * y2_lo <= y1_hi * y1_hi
    ray_01 = y1_lo * y3_lo <= y2_hi * y2_hi
    ray_21 = (y0_lo ** 2) * y3_lo <= y1_hi ** 3
    ray_12 = y0_lo * (y3_lo ** 2) <= y2_hi ** 3

    local_3pt_ok = ray_10 and ray_01
    nonlocal_4pt_ok = ray_21 and ray_12
    global_4ray_ok = local_3pt_ok and nonlocal_4pt_ok
    return {
        "ray_10": ray_10,
        "ray_01": ray_01,
        "ray_21": ray_21,
        "ray_12": ray_12,
        "local_3pt_ok": local_3pt_ok,
        "nonlocal_4pt_ok": nonlocal_4pt_ok,
        "global_4ray_ok": global_4ray_ok,
    }


def all_three_theorems_certified(t1_ok: bool, t2_ok: bool, t3_ok: bool) -> bool:
    """Return True iff all three theorem families T1, T2, T3 hold."""
    return bool(t1_ok) and bool(t2_ok) and bool(t3_ok)


def q_to_str(val: Fraction) -> str:
    """Serialize Fraction canonically as 'num/den'."""
    require_fraction(val, "val")
    return f"{val.numerator}/{val.denominator}"


def str_to_q(text: Any, name: str) -> Fraction:
    """Parse canonical 'num/den' string into exact reduced Fraction."""
    require_ok(isinstance(text, str), f"{name} must be str")
    num_s, _, den_s = text.partition("/")
    num = int(num_s, 10)
    den = int(den_s, 10)
    require_ok(den > 0, f"{name} denominator must be positive")
    frac = Fraction(num, den)
    require_ok(q_to_str(frac) == text, f"{name} must be in canonical reduced form")
    return frac


def ceil_q(val: Fraction) -> int:
    """Exact integer ceiling of a Fraction without floating-point arithmetic."""
    require_fraction(val, "val")
    return -((-val.numerator) // val.denominator)


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic UTF-8 canonical JSON serialization."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    """Lowercase SHA-256 hex digest."""
    return hashlib.sha256(data).hexdigest()


def sha256_file_raw(path: Path) -> str:
    """Compute lowercase SHA-256 hex digest over exact raw bytes of an on-disk file."""
    require_ok(isinstance(path, Path), "path must be Path")
    require_ok(path.is_file(), f"file not found: {path.name}")
    return sha256_bytes(path.read_bytes())


def compute_on_disk_anchor_digests(repo_root: Path = REPO_ROOT) -> dict[str, str]:
    """Hash every pinned in-repo anchor file on disk and verify against its expected SHA-256."""
    require_ok(isinstance(repo_root, Path), "repo_root must be Path")
    digests: dict[str, str] = {}
    for key, (rel_path, expected_sha) in ON_DISK_ANCHOR_SPECS.items():
        actual_sha = sha256_file_raw(repo_root / rel_path)
        require_ok(
            hmac.compare_digest(actual_sha, expected_sha),
            f"on-disk anchor digest mismatch for {rel_path}",
        )
        digests[key] = actual_sha
    return digests


def _no_duplicate_keys_object_pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Strict JSON object hook rejecting duplicate keys."""
    out: dict[str, Any] = {}
    for key, value in pairs:
        require_ok(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _reject_json_constant(token: str) -> Any:
    """Strict JSON parse_constant hook rejecting NaN/Infinity/-Infinity."""
    raise ValueError(f"forbidden non-finite JSON constant: {token}")


def _reject_json_float(token: str) -> Any:
    """Strict JSON parse_float hook rejecting floating-point JSON literals."""
    raise ValueError(f"forbidden JSON float literal: {token}")


def loads_strict_json(raw_text: str) -> Any:
    """Parse JSON text while rejecting duplicate keys, floats, and non-finite constants."""
    require_ok(isinstance(raw_text, str), "raw_text must be str")
    return json.loads(
        raw_text,
        object_pairs_hook=_no_duplicate_keys_object_pairs_hook,
        parse_constant=_reject_json_constant,
        parse_float=_reject_json_float,
    )


# ---------------------------------------------------------------------------
# Exact Q(sqrt(2)) Field Arithmetic (Zero Floats, Zero math.sqrt)
# ---------------------------------------------------------------------------


class Qs2:
    """Exact element a + b*sqrt(2) in Q(sqrt(2)) represented by Fraction pair (a, b)."""

    __slots__ = ("a", "b")

    def __init__(self, a: Fraction, b: Fraction = Fraction(0, 1)) -> None:
        require_fraction(a, "Qs2.a")
        require_fraction(b, "Qs2.b")
        self.a = a
        self.b = b

    def __add__(self, other: Qs2) -> Qs2:
        require_ok(isinstance(other, Qs2), "addend must be Qs2")
        return Qs2(self.a + other.a, self.b + other.b)

    def __sub__(self, other: Qs2) -> Qs2:
        require_ok(isinstance(other, Qs2), "subtrahend must be Qs2")
        return Qs2(self.a - other.a, self.b - other.b)

    def __mul__(self, other: Qs2) -> Qs2:
        require_ok(isinstance(other, Qs2), "multiplier must be Qs2")
        return Qs2(
            self.a * other.a + Fraction(2, 1) * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Qs2) and self.a == other.a and self.b == other.b

    def inv(self) -> Qs2:
        norm = self.a * self.a - Fraction(2, 1) * self.b * self.b
        require_ok(norm != Fraction(0, 1), "division by zero in Q(sqrt(2))")
        return Qs2(self.a / norm, (-self.b) / norm)

    def div(self, other: Qs2) -> Qs2:
        require_ok(isinstance(other, Qs2), "divisor must be Qs2")
        return self * other.inv()

    def is_strictly_positive(self) -> bool:
        """Exact sign > 0 check for a + b*sqrt(2) without floats."""
        zero = Fraction(0, 1)
        if self.a <= zero and self.b <= zero:
            return False
        if self.a >= zero and self.b >= zero:
            return True
        diff = self.a * self.a - Fraction(2, 1) * self.b * self.b
        if self.a > zero:
            return diff > zero
        return diff < zero

    def to_pair_str(self) -> list[str]:
        return [q_to_str(self.a), q_to_str(self.b)]


# ---------------------------------------------------------------------------
# Exact Linear Algebra, Schur Pushforward, & Self-Certifying Congruence
# ---------------------------------------------------------------------------


def require_rect_matrix_q(mat: Any, name: str) -> tuple[int, int]:
    """Validate non-empty rectangular matrix of Fractions and return (rows, cols)."""
    require_ok(isinstance(mat, list), f"{name} must be list")
    require_ok(len(mat) >= 1, f"{name} must be non-empty")
    for r_idx, row in enumerate(mat):
        require_ok(isinstance(row, list), f"{name}[{r_idx}] must be list")
        if r_idx == 0:
            require_ok(len(row) >= 1, f"{name} must have >= 1 column")
        else:
            require_ok(len(row) == len(mat[0]), f"{name} must be rectangular")
        for val in row:
            require_fraction(val, f"{name} entry")
    return len(mat), len(mat[0])


def mat_mul_q(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact matrix multiplication A * B over Q with shape guard."""
    m, k_a = require_rect_matrix_q(a, "a")
    k_b, n = require_rect_matrix_q(b, "b")
    require_ok(k_a == k_b, "inner matrix dimensions must match")
    return [
        [sum((a[i][t] * b[t][j] for t in range(k_a)), Fraction(0, 1)) for j in range(n)]
        for i in range(m)
    ]


def mat_transpose_q(a: list[list[Fraction]]) -> list[list[Fraction]]:
    """Matrix transpose over Q."""
    m, n = require_rect_matrix_q(a, "a")
    return [[a[i][j] for i in range(m)] for j in range(n)]


def exact_solve_q(a_mat: list[list[Fraction]], b_mat: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact Gauss-Jordan linear solver A * X = B over Q."""
    m, m_cols = require_rect_matrix_q(a_mat, "a_mat")
    require_ok(m == m_cols, "a_mat must be square")
    b_rows, n_rhs = require_rect_matrix_q(b_mat, "b_mat")
    require_ok(b_rows == m, "rhs row count mismatch")
    aug = [list(a_mat[i]) + list(b_mat[i]) for i in range(m)]

    for col in range(m):
        piv = -1
        for r in range(col, m):
            if aug[r][col] != Fraction(0, 1):
                piv = r
                break
        require_ok(piv != -1, "singular interior block in linear solve")
        if piv != col:
            aug[col], aug[piv] = aug[piv], aug[col]
        pv = aug[col][col]
        for j in range(col, m + n_rhs):
            aug[col][j] = aug[col][j] / pv
        for r in range(m):
            if r != col and aug[r][col] != Fraction(0, 1):
                fac = aug[r][col]
                for j in range(col, m + n_rhs):
                    aug[r][j] = aug[r][j] - fac * aug[col][j]
    return [aug[i][m:] for i in range(m)]


def exact_rank_q(mat: list[list[Fraction]]) -> int:
    """Exact row-echelon rank of an m x n matrix over Q."""
    m, n = require_rect_matrix_q(mat, "mat")
    work = [list(row) for row in mat]
    rank = 0
    for col in range(n):
        piv = -1
        for r in range(rank, m):
            if work[r][col] != Fraction(0, 1):
                piv = r
                break
        if piv == -1:
            continue
        if piv != rank:
            work[rank], work[piv] = work[piv], work[rank]
        pv = work[rank][col]
        for j in range(col, n):
            work[rank][j] = work[rank][j] / pv
        for r in range(m):
            if r != rank and work[r][col] != Fraction(0, 1):
                fac = work[r][col]
                for j in range(col, n):
                    work[r][j] = work[r][j] - fac * work[rank][j]
        rank += 1
    return rank


def build_conductance_laplacian_q(
    n_nodes: int,
    edges: list[tuple[int, int, Fraction]],
    shunts: list[tuple[int, Fraction]] | None = None,
) -> list[list[Fraction]]:
    """Construct symmetric grounded conductance Laplacian over Q."""
    require_ok(is_exact_int(n_nodes), "n_nodes must be int")
    require_ok(n_nodes >= 2, "n_nodes must be >= 2")
    require_ok(n_nodes <= 128, "n_nodes exceeds bounded limit 128")
    require_ok(isinstance(edges, list), "edges must be list")
    require_ok(len(edges) >= 1, "edges must be non-empty")
    lap = [[Fraction(0, 1) for _ in range(n_nodes)] for _ in range(n_nodes)]
    for edge in edges:
        require_ok(isinstance(edge, tuple), "edge must be tuple")
        require_ok(len(edge) == 3, "edge must have length 3")
        u, v, g = edge[0], edge[1], edge[2]
        require_ok(is_exact_int(u), "edge u must be int")
        require_ok(is_exact_int(v), "edge v must be int")
        require_fraction(g, "edge_g")
        require_ok(g > Fraction(0, 1), "edge conductance must be > 0")
        require_ok(0 <= u, "u < 0")
        require_ok(u < n_nodes, "u >= n_nodes")
        require_ok(0 <= v, "v < 0")
        require_ok(v < n_nodes, "v >= n_nodes")
        require_ok(u != v, "self-loop forbidden")
        lap[u][u] += g
        lap[v][v] += g
        lap[u][v] -= g
        lap[v][u] -= g
    if shunts is not None:
        require_ok(isinstance(shunts, list), "shunts must be list")
        for sh in shunts:
            require_ok(isinstance(sh, tuple), "shunt must be tuple")
            require_ok(len(sh) == 2, "shunt must have length 2")
            node, gs = sh[0], sh[1]
            require_ok(is_exact_int(node), "shunt node must be int")
            require_fraction(gs, "shunt_g")
            require_ok(gs >= Fraction(0, 1), "shunt conductance must be >= 0")
            require_ok(0 <= node, "shunt node < 0")
            require_ok(node < n_nodes, "shunt node >= n_nodes")
            lap[node][node] += gs
    return lap


def schur_pushforward_with_congruence_q(
    mat: list[list[Fraction]], boundary: tuple[int, ...]
) -> dict[str, Any]:
    """Compute Schur complement M / M_II and explicit unitriangular congruence U^T M U."""
    n, n_cols = require_rect_matrix_q(mat, "mat")
    require_ok(n == n_cols, "mat must be square")
    require_ok(n >= 2, "matrix dim must be >= 2")
    require_ok(isinstance(boundary, tuple), "boundary must be tuple")
    require_ok(len(boundary) >= 1, "boundary must be non-empty")
    require_ok(len(boundary) < n, "interior must be non-empty")
    for b in boundary:
        require_ok(is_exact_int(b), "boundary index must be int")
        require_ok(0 <= b, "boundary index < 0")
        require_ok(b < n, "boundary index >= n")
    b_set = set(boundary)
    require_ok(len(b_set) == len(boundary), "duplicate boundary index")

    b_idx = list(boundary)
    i_idx = [k for k in range(n) if k not in b_set]
    order = b_idx + i_idx
    m_perm = [[mat[u][v] for v in order] for u in order]

    nb = len(b_idx)
    ni = len(i_idx)
    m_bb = [row[:nb] for row in m_perm[:nb]]
    m_bi = [row[nb:] for row in m_perm[:nb]]
    m_ib = [row[:nb] for row in m_perm[nb:]]
    m_ii = [row[nb:] for row in m_perm[nb:]]

    inv_ii_ib = exact_solve_q(m_ii, m_ib)
    prod = mat_mul_q(m_bi, inv_ii_ib)
    schur = [[m_bb[r][c] - prod[r][c] for c in range(nb)] for r in range(nb)]

    u_mat = [[Fraction(1 if r == c else 0, 1) for c in range(n)] for r in range(n)]
    for r in range(ni):
        for c in range(nb):
            u_mat[nb + r][c] = -inv_ii_ib[r][c]

    ut_m_u = mat_mul_q(mat_transpose_q(u_mat), mat_mul_q(m_perm, u_mat))
    expected_blk = [[Fraction(0, 1) for _ in range(n)] for _ in range(n)]
    for r in range(nb):
        for c in range(nb):
            expected_blk[r][c] = schur[r][c]
    for r in range(ni):
        for c in range(ni):
            expected_blk[nb + r][nb + c] = m_ii[r][c]

    return {
        "schur": schur,
        "interior": m_ii,
        "permuted_full": m_perm,
        "unitriangular_u": u_mat,
        "block_congruence_exact": ut_m_u == expected_blk,
    }


def verify_congruence_certificate_q(
    mat: list[list[Fraction]], p_mat: list[list[Fraction]], diag: list[Fraction]
) -> None:
    """Verify invertible P in GL_n(Q) satisfies P^T M P == diag(d) identically."""
    n, m_cols = require_rect_matrix_q(mat, "mat")
    require_ok(n == m_cols, "mat must be square")
    p_rows, p_cols = require_rect_matrix_q(p_mat, "p_mat")
    require_ok(p_rows == n, "p_mat row mismatch")
    require_ok(p_cols == n, "p_mat col mismatch")
    require_ok(isinstance(diag, list), "diag must be list")
    require_ok(len(diag) == n, "diag length mismatch")
    for d_val in diag:
        require_fraction(d_val, "diag entry")
    reconstructed = mat_mul_q(mat_transpose_q(p_mat), mat_mul_q(mat, p_mat))
    expected_diag = [
        [diag[i] if i == j else Fraction(0, 1) for j in range(n)] for i in range(n)
    ]
    require_ok(reconstructed == expected_diag, "self-certifying P^T M P == diag(d) check failed")
    require_ok(exact_rank_q(p_mat) == n, "congruence matrix P must be invertible")


def certified_symmetric_congruence_inertia_q(mat: list[list[Fraction]]) -> dict[str, Any]:
    """Construct invertible P in GL_n(Q) with P^T M P = diag(d) and return certified inertia."""
    n, n_cols = require_rect_matrix_q(mat, "mat")
    require_ok(n == n_cols, "matrix must be square")
    for i in range(n):
        for j in range(i + 1, n):
            require_ok(mat[i][j] == mat[j][i], "matrix must be symmetric")

    work = [list(row) for row in mat]
    p_mat = [[Fraction(1 if i == j else 0, 1) for j in range(n)] for i in range(n)]

    def swap_rc(i: int, j: int) -> None:
        if i == j:
            return
        work[i], work[j] = work[j], work[i]
        for row in work:
            row[i], row[j] = row[j], row[i]
        for row in p_mat:
            row[i], row[j] = row[j], row[i]

    def add_col_row(target: int, src: int, scale: Fraction) -> None:
        if scale == Fraction(0, 1):
            return
        for r in range(n):
            p_mat[r][target] = p_mat[r][target] + scale * p_mat[r][src]
            work[r][target] = work[r][target] + scale * work[r][src]
        for c in range(n):
            work[target][c] = work[target][c] + scale * work[src][c]

    k = 0
    while k < n:
        piv1 = -1
        for r in range(k, n):
            if work[r][r] != Fraction(0, 1):
                piv1 = r
                break
        if piv1 != -1:
            swap_rc(k, piv1)
            d_piv = work[k][k]
            for r in range(k + 1, n):
                if work[k][r] != Fraction(0, 1):
                    add_col_row(r, k, -work[k][r] / d_piv)
            k += 1
            continue

        pair: tuple[int, int] | None = None
        for r in range(k, n):
            for c in range(r + 1, n):
                if work[r][c] != Fraction(0, 1):
                    pair = (r, c)
                    break
            if pair is not None:
                break
        if pair is None:
            break

        r_idx, c_idx = pair
        swap_rc(k, r_idx)
        if c_idx == k:
            c_idx = r_idx
        swap_rc(k + 1, c_idx)
        add_col_row(k, k + 1, Fraction(1, 1))

    diag = [work[i][i] for i in range(n)]
    verify_congruence_certificate_q(mat, p_mat, diag)

    n_pos = sum(1 for d in diag if d > Fraction(0, 1))
    n_neg = sum(1 for d in diag if d < Fraction(0, 1))
    n_zero = sum(1 for d in diag if d == Fraction(0, 1))
    return {
        "inertia": (n_pos, n_neg, n_zero),
        "diag": diag,
        "p_mat": p_mat,
        "certified_congruence_ok": True,
    }


# ---------------------------------------------------------------------------
# Theorem 1: Physical Schur Pushforwards & Exact Gate-5 Congruence Theorem
# ---------------------------------------------------------------------------


def build_sylvester_h8() -> list[list[int]]:
    """Construct canonical 8x8 Sylvester-Hadamard matrix H_8 = H_2^{x3}."""
    mat = [[1]]
    for _ in range(3):
        mat = [r + r for r in mat] + [r + [-x for x in r] for r in mat]
    return mat


def run_theorem_t1() -> dict[str, Any]:
    """Certify four physical Schur pushforwards and exact Gate-5 inertia classification."""
    petra_edges = [(k, k + 1, Fraction(2, 1)) for k in range(6)]
    lap_petra_unvented = build_conductance_laplacian_q(7, petra_edges)
    lap_petra_vented = build_conductance_laplacian_q(
        7, petra_edges, [(k, Fraction(1, 1)) for k in range(1, 6)]
    )
    sp_petra_unv = schur_pushforward_with_congruence_q(lap_petra_unvented, (0, 6))
    sp_petra_ven = schur_pushforward_with_congruence_q(lap_petra_vented, (0, 6))
    petra_surge_unv = -sp_petra_unv["schur"][0][1]
    petra_surge_ven = -sp_petra_ven["schur"][0][1]

    def gier_schur_conductance(n_pipes: int) -> tuple[Fraction, dict[str, Any], list[list[Fraction]]]:
        end_node = n_pipes + 1
        edges = [(0, p, Fraction(2, 1)) for p in range(1, n_pipes + 1)] + [
            (p, end_node, Fraction(2, 1)) for p in range(1, n_pipes + 1)
        ]
        lap = build_conductance_laplacian_q(end_node + 1, edges)
        sp = schur_pushforward_with_congruence_q(lap, (0, end_node))
        return sp["schur"][0][0], sp, lap

    g_gier_9, sp_gier_9, lap_gier_9 = gier_schur_conductance(9)
    g_gier_8, _, _ = gier_schur_conductance(8)
    g_gier_7, _, _ = gier_schur_conductance(7)

    casarabe_edges = (
        [(0, 1 + k, Fraction(1, 1)) for k in range(6)]
        + [(1 + k, 1 + ((k + 1) % 6), Fraction(1, 1)) for k in range(6)]
        + [(1 + k, 7 + k, Fraction(1, 1)) for k in range(6)]
        + [(7 + k, 7 + ((k + 1) % 6), Fraction(1, 1)) for k in range(6)]
    )
    ring_edges = [(k, (k + 1) % 13, Fraction(1, 1)) for k in range(13)]
    tree_edges = [(k, k + 1, Fraction(1, 1)) for k in range(12)]

    lap_casarabe = build_conductance_laplacian_q(13, casarabe_edges)
    sp_casarabe = schur_pushforward_with_congruence_q(lap_casarabe, (0, 7))
    g_casarabe = sp_casarabe["schur"][0][0]
    g_casarabe_cut = schur_pushforward_with_congruence_q(
        build_conductance_laplacian_q(13, casarabe_edges[1:]), (0, 7)
    )["schur"][0][0]

    g_ring = schur_pushforward_with_congruence_q(
        build_conductance_laplacian_q(13, ring_edges), (0, 7)
    )["schur"][0][0]
    g_ring_cut = schur_pushforward_with_congruence_q(
        build_conductance_laplacian_q(13, ring_edges[1:]), (0, 7)
    )["schur"][0][0]
    g_tree = schur_pushforward_with_congruence_q(
        build_conductance_laplacian_q(13, tree_edges), (0, 12)
    )["schur"][0][0]

    cov_3x3 = [
        [Fraction(1, 4), Fraction(9, 100), Fraction(9, 100)],
        [Fraction(9, 100), Fraction(1, 4), Fraction(9, 100)],
        [Fraction(9, 100), Fraction(9, 100), Fraction(1, 4)],
    ]
    sp_nafis = schur_pushforward_with_congruence_q(cov_3x3, (0, 1))
    s_nafis = sp_nafis["schur"]
    det_prior = cov_3x3[0][0] * cov_3x3[1][1] - cov_3x3[0][1] * cov_3x3[1][0]
    det_readable = s_nafis[0][0] * s_nafis[1][1] - s_nafis[0][1] * s_nafis[1][0]
    tr_drop_readable = (cov_3x3[0][0] - s_nafis[0][0]) + (cov_3x3[1][1] - s_nafis[1][1])

    h8 = build_sylvester_h8()
    c_half_h8 = [[Fraction(h8[i][j], 2) for j in range(8)] for i in range(8)]
    ct_c = mat_mul_q(mat_transpose_q(c_half_h8), c_half_h8)
    sigma_star_019 = [
        [ct_c[i][j] + Fraction(2, 1) * c_half_h8[i][j] for j in range(8)] for i in range(8)
    ]
    l8_at_1 = [
        [Fraction(2 if i == j else 0, 1) + Fraction(h8[i][j], 2) for j in range(8)]
        for i in range(8)
    ]
    g_017_at_1 = mat_mul_q(l8_at_1, mat_transpose_q(l8_at_1))
    shifted_g_017_scaled = [
        [Fraction(2, 1) * (g_017_at_1[i][j] - Fraction(2 if i == j else 0, 1)) for j in range(8)]
        for i in range(8)
    ]
    p_scale_2 = [[Fraction(2 if i == j else 0, 1) for j in range(8)] for i in range(8)]
    congruent_019_to_017 = (
        mat_mul_q(mat_transpose_q(p_scale_2), mat_mul_q(sigma_star_019, p_scale_2))
        == shifted_g_017_scaled
    )

    cert_sigma_019 = certified_symmetric_congruence_inertia_q(sigma_star_019)
    cert_shifted_017 = certified_symmetric_congruence_inertia_q(shifted_g_017_scaled)
    cert_g017_pd = certified_symmetric_congruence_inertia_q(g_017_at_1)

    cert_petra_v = certified_symmetric_congruence_inertia_q(lap_petra_vented)
    cert_gier_full = certified_symmetric_congruence_inertia_q(lap_gier_9)
    cert_gier_ii = certified_symmetric_congruence_inertia_q(sp_gier_9["interior"])
    cert_gier_schur = certified_symmetric_congruence_inertia_q(sp_gier_9["schur"])
    cert_casarabe = certified_symmetric_congruence_inertia_q(lap_casarabe)
    cert_nafis = certified_symmetric_congruence_inertia_q(s_nafis)

    lap_hyd_8 = build_conductance_laplacian_q(
        8, [(k, k + 1, Fraction(1, 1)) for k in range(7)]
    )
    cert_hyd_8 = certified_symmetric_congruence_inertia_q(lap_hyd_8)

    haynsworth_gier_ok = all(
        (
            sp_gier_9["block_congruence_exact"],
            cert_gier_full["inertia"][0] == cert_gier_ii["inertia"][0] + cert_gier_schur["inertia"][0],
            cert_gier_full["inertia"][1] == cert_gier_ii["inertia"][1] + cert_gier_schur["inertia"][1],
            cert_gier_full["inertia"][2] == cert_gier_ii["inertia"][2] + cert_gier_schur["inertia"][2],
        )
    )
    true_congruence_pair_ok = all(
        (
            congruent_019_to_017,
            are_inertias_congruence_compatible(
                cert_sigma_019["inertia"], cert_shifted_017["inertia"]
            ),
            cert_sigma_019["inertia"] == (4, 4, 0),
            cert_g017_pd["inertia"] == (8, 0, 0),
        )
    )
    non_congruence_gate5_ok = all(
        (
            cert_petra_v["inertia"] == (7, 0, 0),
            cert_gier_full["inertia"] == (10, 0, 1),
            cert_casarabe["inertia"] == (12, 0, 1),
            cert_nafis["inertia"] == (2, 0, 0),
            cert_hyd_8["inertia"] == (7, 0, 1),
            not are_inertias_congruence_compatible(
                cert_hyd_8["inertia"], cert_sigma_019["inertia"]
            ),
        )
    )
    physical_witnesses_ok = all(
        (
            sp_petra_unv["block_congruence_exact"],
            sp_petra_ven["block_congruence_exact"],
            sp_casarabe["block_congruence_exact"],
            sp_nafis["block_congruence_exact"],
            petra_surge_unv == Fraction(1, 3),
            petra_surge_ven == Fraction(64, 1365),
            g_gier_9 == Fraction(9, 1),
            g_gier_8 / g_gier_9 == Fraction(8, 9),
            g_gier_7 / g_gier_9 == Fraction(7, 9),
            g_casarabe == Fraction(2755, 1806),
            g_casarabe_cut == Fraction(1656, 1267),
            g_casarabe_cut / g_casarabe == Fraction(427248, 498655),
            g_ring == Fraction(13, 42),
            g_ring_cut == Fraction(1, 6),
            g_tree == Fraction(1, 12),
            g_casarabe > g_ring,
            g_ring > g_tree,
            det_prior == Fraction(34, 625),
            det_readable == Fraction(688, 15625),
            tr_drop_readable == Fraction(81, 1250),
        )
    )

    passed = all(
        (
            physical_witnesses_ok,
            haynsworth_gier_ok,
            true_congruence_pair_ok,
            non_congruence_gate5_ok,
        )
    )
    return {
        "novelty_class": "N1_exact_gate5_congruence_boundary_classification",
        "related_audits": ["AUDIT-002", "AUDIT-004", "AUDIT-017", "AUDIT-018", "AUDIT-019"],
        "petra_surge_unvented": q_to_str(petra_surge_unv),
        "petra_surge_vented": q_to_str(petra_surge_ven),
        "gier_conductances_9_8_7": [q_to_str(g_gier_9), q_to_str(g_gier_8), q_to_str(g_gier_7)],
        "casarabe_conductance": q_to_str(g_casarabe),
        "casarabe_single_cut_conductance": q_to_str(g_casarabe_cut),
        "casarabe_single_cut_retention": q_to_str(g_casarabe_cut / g_casarabe),
        "ring_c13_conductance": q_to_str(g_ring),
        "tree_t13_conductance": q_to_str(g_tree),
        "ibn_al_nafis_schur_det_prior": q_to_str(det_prior),
        "ibn_al_nafis_schur_det_readable": q_to_str(det_readable),
        "ibn_al_nafis_schur_trace_drop": q_to_str(tr_drop_readable),
        "inertias_pos_neg_zero": {
            "sigma_star_h8_fold_sheaf": list(cert_sigma_019["inertia"]),
            "shifted_gram_h8_packing": list(cert_shifted_017["inertia"]),
            "gram_g1_e8_endpoint": list(cert_g017_pd["inertia"]),
            "petra_vented_7x7": list(cert_petra_v["inertia"]),
            "gier_9pipe_11x11": list(cert_gier_full["inertia"]),
            "casarabe_13x13": list(cert_casarabe["inertia"]),
            "hydraulic_conduit_8x8": list(cert_hyd_8["inertia"]),
            "ibn_al_nafis_2x2": list(cert_nafis["inertia"]),
        },
        "haynsworth_unitriangular_additivity_verified": haynsworth_gier_ok,
        "true_sylvester_congruence_h8_pair_verified": true_congruence_pair_ok,
        "gate5_passive_hydraulic_non_congruence_verified": non_congruence_gate5_ok,
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Theorem 2: Discrete Parity, Chokwe Sona Sheaf Nullity & Stereographic Folds
# ---------------------------------------------------------------------------


def pingala_nasta_bits(n_syllables: int, k_one_based: int) -> tuple[int, ...]:
    """Pingala nasta recursion mapping 1-based meter index k in [1, 2^n] to {0, 1}^n."""
    require_ok(is_exact_int(n_syllables), "n_syllables must be int")
    require_ok(n_syllables >= 1, "n_syllables must be >= 1")
    require_ok(n_syllables <= 32, "n_syllables exceeds bounded limit 32")
    require_ok(is_exact_int(k_one_based), "k_one_based must be int")
    require_ok(1 <= k_one_based, "k_one_based < 1")
    require_ok(k_one_based <= (1 << n_syllables), "k_one_based > 2^n")
    cur = k_one_based
    bits: list[int] = []
    for _ in range(n_syllables):
        if (cur & 1) == 1:
            bits.append(0)
            cur = (cur + 1) // 2
        else:
            bits.append(1)
            cur = cur // 2
    return tuple(bits)


def sona_sheaf_laplacian_nullity_q(
    m_rows: int,
    n_cols: int,
    vertical_mirrors: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    """Build explicit cellular sheaf coboundary d0 over Q on Sona 4mn-segment graph & compute dim ker."""
    require_ok(is_exact_int(m_rows), "m_rows must be int")
    require_ok(is_exact_int(n_cols), "n_cols must be int")
    require_ok(m_rows >= 1, "m_rows must be >= 1")
    require_ok(n_cols >= 1, "n_cols must be >= 1")
    require_ok(m_rows <= 8, "m_rows exceeds bounded Sona grid limit 8")
    require_ok(n_cols <= 8, "n_cols exceeds bounded Sona grid limit 8")
    require_ok(isinstance(vertical_mirrors, tuple), "vertical_mirrors must be tuple")
    v_set: set[tuple[int, int]] = set()
    for vm in vertical_mirrors:
        require_ok(isinstance(vm, tuple), "mirror entry must be tuple")
        require_ok(len(vm) == 2, "mirror entry must have length 2")
        require_ok(is_exact_int(vm[0]), "mirror x must be int")
        require_ok(is_exact_int(vm[1]), "mirror y must be int")
        v_set.add((vm[0], vm[1]))

    two_m = 2 * m_rows
    two_n = 2 * n_cols
    n_segs = 4 * m_rows * n_cols
    visited = bytearray(n_segs)
    edges: list[tuple[int, int]] = []
    loop_count = 0

    for seg_id in range(n_segs):
        if visited[seg_id]:
            continue
        loop_count += 1
        x_min = seg_id // two_n
        y_min = seg_id % two_n
        if ((x_min + y_min) & 1) == 1:
            x, y, dx, dy = x_min, y_min, 1, 1
        else:
            x, y, dx, dy = x_min, y_min + 1, 1, -1

        cycle_ids: list[int] = []
        while True:
            c_xmin = x if dx == 1 else x - 1
            c_ymin = y if dy == 1 else y - 1
            cur_id = c_xmin * two_n + c_ymin
            if visited[cur_id]:
                break
            visited[cur_id] = 1
            cycle_ids.append(cur_id)
            nx = x + dx
            ny = y + dy
            ndx = -dx if (nx == 0 or nx == two_m or (nx, ny) in v_set) else dx
            ndy = -dy if (ny == 0 or ny == two_n) else dy
            x, y, dx, dy = nx, ny, ndx, ndy

        c_len = len(cycle_ids)
        for idx in range(c_len):
            edges.append((cycle_ids[idx], cycle_ids[(idx + 1) % c_len]))

    d0_mat: list[list[Fraction]] = []
    for u_seg, v_seg in edges:
        row = [Fraction(0, 1)] * n_segs
        row[u_seg] = Fraction(1, 1)
        row[v_seg] = Fraction(-1, 1)
        d0_mat.append(row)

    rk_d0 = exact_rank_q(d0_mat)
    ker_dim = n_segs - rk_d0
    return {
        "n_segments": n_segs,
        "loop_count": loop_count,
        "coboundary_rank": rk_d0,
        "sheaf_ker_dim": ker_dim,
        "internal_floppy_modes": ker_dim - 1,
    }


def biruni_stereographic_meridian_qs2(kappa_sq: Qs2, s_param: Fraction) -> tuple[Qs2, Qs2]:
    """Evaluate (-Z_Biruni, X_Biruni^2) = ((1 - k^2 s^2)/(1 + k^2 s^2), 4 k^2 s^2 / (1 + k^2 s^2)^2)."""
    require_ok(isinstance(kappa_sq, Qs2), "kappa_sq must be Qs2")
    require_fraction(s_param, "s_param")
    one = Qs2(Fraction(1, 1), Fraction(0, 1))
    s_sq = Qs2(s_param * s_param, Fraction(0, 1))
    u_sq = kappa_sq * s_sq
    denom = one + u_sq
    neg_z = (one - u_sq).div(denom)
    four_u_sq = Qs2(Fraction(4, 1), Fraction(0, 1)) * u_sq
    x_sq = four_u_sq.div(denom * denom)
    return neg_z, x_sq


def run_theorem_t2() -> dict[str, Any]:
    """Certify Pingala/Ifa/Bamana parity bridges, Sona sheaf nullity, & Biruni folds."""
    h8 = build_sylvester_h8()
    nasta_3 = [pingala_nasta_bits(3, k) for k in range(1, 9)]
    h8_from_pingala = [
        [
            1 if (sum(nasta_3[a][t] * nasta_3[b][t] for t in range(3)) & 1) == 0 else -1
            for b in range(8)
        ]
        for a in range(8)
    ]
    pingala_h8_match = h8_from_pingala == h8

    even_ifa_spinors: list[tuple[Fraction, ...]] = []
    for k in range(1, 257):
        bits8 = pingala_nasta_bits(8, k)
        if (sum(bits8) & 1) == 0:
            vec = tuple(Fraction(1, 2) if b == 0 else Fraction(-1, 2) for b in bits8)
            even_ifa_spinors.append(vec)
    d8_roots_count = 28 * 4
    ifa_e8_spinor_ok = all(
        (
            len(even_ifa_spinors) == 128,
            len(set(even_ifa_spinors)) == 128,
            all(sum(c * c for c in v) == Fraction(2, 1) for v in even_ifa_spinors),
            len(even_ifa_spinors) + d8_roots_count == 240,
        )
    )

    pts_f2_4 = [pingala_nasta_bits(4, k) for k in range(1, 17)]
    parity_rows_a16 = [
        tuple(1 for _ in range(16)),
        tuple(pt[0] for pt in pts_f2_4),
        tuple(pt[1] for pt in pts_f2_4),
        tuple(pt[2] for pt in pts_f2_4),
        tuple(pt[3] for pt in pts_f2_4),
    ]
    rm14_codewords: list[tuple[int, ...]] = []
    for c0 in (0, 1):
        for coeffs in itertools.product((0, 1), repeat=4):
            cw = tuple(
                (c0 ^ sum(coeffs[j] * pt[j] for j in range(4))) & 1 for pt in pts_f2_4
            )
            rm14_codewords.append(cw)

    rm14_weights = [sum(cw) for cw in rm14_codewords]
    rm14_self_orth = all(
        (sum(cw[idx] * prow[idx] for idx in range(16)) & 1) == 0
        for cw in rm14_codewords
        for prow in parity_rows_a16
    )
    rm14_bw16_ok = all(
        (
            len(set(rm14_codewords)) == 32,
            rm14_weights.count(0) == 1,
            rm14_weights.count(16) == 1,
            rm14_weights.count(8) == 30,
            rm14_self_orth,
        )
    )

    sona_grid_checks: list[bool] = []
    for m_r in range(1, 5):
        for n_c in range(1, 5):
            g_mn = math.gcd(m_r, n_c)
            sr = sona_sheaf_laplacian_nullity_q(m_r, n_c)
            sona_grid_checks.extend(
                (
                    sr["sheaf_ker_dim"] == g_mn,
                    sr["loop_count"] == g_mn,
                    (sr["internal_floppy_modes"] == 0) == (g_mn == 1),
                )
            )
    sona_2x2_raw = sona_sheaf_laplacian_nullity_q(2, 2)
    sona_2x2_merged = sona_sheaf_laplacian_nullity_q(2, 2, vertical_mirrors=((2, 1),))
    sona_2x3_raw = sona_sheaf_laplacian_nullity_q(2, 3)
    sona_2x3_split = sona_sheaf_laplacian_nullity_q(2, 3, vertical_mirrors=((2, 1),))
    sona_sheaf_ok = all(
        tuple(sona_grid_checks)
        + (
            sona_2x2_raw["sheaf_ker_dim"] == 2,
            sona_2x2_merged["sheaf_ker_dim"] == 1,
            sona_2x3_raw["sheaf_ker_dim"] == 1,
            sona_2x3_split["sheaf_ker_dim"] == 2,
        )
    )

    s_samples = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(1, 1))
    sqrt2 = Qs2(Fraction(0, 1), Fraction(1, 1))
    two_qs2 = Qs2(Fraction(2, 1), Fraction(0, 1))
    kp_sq = Qs2(Fraction(-1, 1), Fraction(2, 1)).div(Qs2(Fraction(1, 1), Fraction(2, 1)))
    km_sq = Qs2(Fraction(1, 1), Fraction(2, 1)).div(Qs2(Fraction(-1, 1), Fraction(2, 1)))

    biruni_fold_checks: list[bool] = [
        kp_sq == Qs2(Fraction(9, 7), Fraction(-4, 7)),
        km_sq == Qs2(Fraction(9, 7), Fraction(4, 7)),
    ]
    for s_val in s_samples:
        nz_dn, x2_dn = biruni_stereographic_meridian_qs2(Qs2(Fraction(1, 1)), s_val)
        bar_sq_dn = two_qs2 * (nz_dn * nz_dn + x2_dn)
        biruni_fold_checks.append(bar_sq_dn == two_qs2)

        s2_q = Qs2(s_val * s_val, Fraction(0, 1))
        dp = Qs2(Fraction(1, 1), Fraction(2, 1)) + Qs2(Fraction(-1, 1), Fraction(2, 1)) * s2_q
        dm = Qs2(Fraction(-1, 1), Fraction(2, 1)) + Qs2(Fraction(1, 1), Fraction(2, 1)) * s2_q
        ap = (Qs2(Fraction(6, 1), Fraction(5, 1)) + Qs2(Fraction(-6, 1), Fraction(5, 1)) * s2_q).div(dp)
        bp = Qs2(Fraction(0, 1), Fraction(2, 1) * s_val).div(dp)
        am = (Qs2(Fraction(2, 1), Fraction(3, 1)) + Qs2(Fraction(-2, 1), Fraction(3, 1)) * s2_q).div(dm)
        bm = Qs2(Fraction(0, 1), Fraction(2, 1) * s_val).div(dm)

        nz_p, x2_p = biruni_stereographic_meridian_qs2(kp_sq, s_val)
        nz_m, x2_m = biruni_stereographic_meridian_qs2(km_sq, s_val)

        ap_minus_2 = ap - two_qs2
        am_minus_2 = am - two_qs2
        seven = Qs2(Fraction(7, 1), Fraction(0, 1))
        biruni_fold_checks.extend(
            (
                ap_minus_2 == sqrt2 * nz_p,
                am_minus_2 == sqrt2 * nz_m,
                seven * bp * bp == two_qs2 * x2_p,
                seven * bm * bm == two_qs2 * x2_m,
                ap_minus_2 * ap_minus_2 + seven * bp * bp == two_qs2,
                am_minus_2 * am_minus_2 + seven * bm * bm == two_qs2,
            )
        )

        if is_strict_open_bracket_q(Fraction(0, 1), s_val, Fraction(1, 1)):
            m00, m01 = ap + bp, two_qs2 * bp
            m10, m11 = two_qs2 * bm, am - bm
            d00 = (m00 * m00 + m01 * m01) - two_qs2
            d01 = (m00 * m10 + m01 * m11) - Qs2(Fraction(1, 1))
            d11 = (m10 * m10 + m11 * m11) - Qs2(Fraction(1, 1))
            det_diff = d00 * d11 - d01 * d01
            biruni_fold_checks.extend((d00.is_strictly_positive(), det_diff.is_strictly_positive()))

    biruni_folds_ok = all(biruni_fold_checks)
    passed = all((pingala_h8_match, ifa_e8_spinor_ok, rm14_bw16_ok, sona_sheaf_ok, biruni_folds_ok))
    return {
        "novelty_class": "N1_pingala_ifa_sona_biruni_lattice_sheaf_bridges",
        "related_audits": ["AUDIT-004", "AUDIT-009", "AUDIT-017", "AUDIT-019", "AUDIT-020R"],
        "pingala_nasta3_equals_sylvester_h8": pingala_h8_match,
        "ifa_even_parity_e8_spinor_roots": len(even_ifa_spinors),
        "e8_total_kissing_roots": len(even_ifa_spinors) + d8_roots_count,
        "bamana_rm14_codewords": len(rm14_codewords),
        "bamana_rm14_orth_a16_verified": rm14_bw16_ok,
        "sona_16_grids_gcd_ker_verified": sona_sheaf_ok,
        "sona_2x2_ker_raw_to_walled": [
            sona_2x2_raw["sheaf_ker_dim"],
            sona_2x2_merged["sheaf_ker_dim"],
        ],
        "sona_2x3_ker_raw_to_walled": [
            sona_2x3_raw["sheaf_ker_dim"],
            sona_2x3_split["sheaf_ker_dim"],
        ],
        "biruni_kappa_plus_sq_qs2": kp_sq.to_pair_str(),
        "biruni_kappa_minus_sq_qs2": km_sq.to_pair_str(),
        "biruni_stereographic_f8_e8_identity_verified": biruni_folds_ok,
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Theorem 3: Multiplicative Farkas & Madhava-Hankel Spectral Bounds
# ---------------------------------------------------------------------------


def fourier_motzkin_log_concave_additive_q(
    h_boxes: tuple[
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
    ],
) -> bool:
    """Independent additive Q Fourier-Motzkin oracle for h0 - 2*h1 + h2 <= 0 & h1 - 2*h2 + h3 <= 0."""
    checked = require_4boxes_q(h_boxes, positive_only=False)
    (a0, _), (a1, b1), (a2, b2), (a3, _) = checked
    h1_lo = max(a1, (a0 + a2) / Fraction(2, 1), (Fraction(2, 1) * a0 + a3) / Fraction(3, 1))
    h1_hi = min(b1, Fraction(2, 1) * b2 - a3)
    return h1_lo <= h1_hi


def stieltjes_hankel_rh4_interval_q(
    eig1: Fraction, eig2: Fraction, eig3_lo: Fraction, eig3_hi: Fraction
) -> dict[str, Fraction]:
    """Sound rational [lo, hi] enclosure of R_{H,4} & R_opt^(2) for diag(eig1, eig2, eig3)."""
    require_fraction(eig1, "eig1")
    require_fraction(eig2, "eig2")
    require_fraction(eig3_lo, "eig3_lo")
    require_fraction(eig3_hi, "eig3_hi")
    require_ok(eig1 > Fraction(0, 1), "eig1 must be > 0")
    require_ok(eig2 > Fraction(0, 1), "eig2 must be > 0")
    require_ok(eig3_lo >= Fraction(0, 1), "eig3_lo must be >= 0")
    require_ok(eig3_lo <= eig3_hi, "eig3_lo must be <= eig3_hi")

    s1_lo = eig1 + eig2 + eig3_lo
    s1_hi = eig1 + eig2 + eig3_hi
    s2_lo = eig1 ** 2 + eig2 ** 2 + eig3_lo ** 2
    s2_hi = eig1 ** 2 + eig2 ** 2 + eig3_hi ** 2
    s3_lo = eig1 ** 3 + eig2 ** 3 + eig3_lo ** 3
    s3_hi = eig1 ** 3 + eig2 ** 3 + eig3_hi ** 3
    s4_lo = eig1 ** 4 + eig2 ** 4 + eig3_lo ** 4
    s4_hi = eig1 ** 4 + eig2 ** 4 + eig3_hi ** 4

    num_lo = max(Fraction(0, 1), s1_lo * s3_lo - s2_hi ** 2)
    num_hi = s1_hi * s3_hi - s2_lo ** 2
    det_lo = s2_lo * s4_lo - s3_hi ** 2
    det_hi = s2_hi * s4_hi - s3_lo ** 2
    require_ok(det_lo > Fraction(0, 1), "Hankel determinant lower bound must be > 0")

    ropt_hi = (s1_hi ** 2) / s2_lo
    rh4_lo = (s1_lo ** 2) / s2_hi + (num_lo ** 2) / (s2_hi * det_hi)
    rh4_hi = (s1_hi ** 2) / s2_lo + (num_hi ** 2) / (s2_lo * det_lo)
    return {
        "ropt_hi": ropt_hi,
        "rh4_lo": rh4_lo,
        "rh4_hi": rh4_hi,
        "width": rh4_hi - rh4_lo,
    }


def madhava_sigma_enclosures_even_n_q(n_even: int) -> dict[str, Fraction]:
    """Return raw [S0(n), S0(n-1)] and Madhava [S0(n)+R2(n), S0(n)+R3(n)] enclosures of pi/4."""
    require_ok(is_exact_int(n_even), "n_even must be int")
    require_ok(n_even >= 2, "n_even must be >= 2")
    require_ok(n_even <= 128, "n_even exceeds bounded limit 128")
    require_ok((n_even & 1) == 0, "n_even must be even for lower-sum S0(n)")

    s0 = Fraction(0, 1)
    for k in range(1, n_even + 1):
        term = Fraction(1, 2 * k - 1)
        s0 = s0 + term if (k & 1) == 1 else s0 - term

    raw_lo = s0
    raw_hi = s0 + Fraction(1, 2 * n_even - 1)
    r2 = Fraction(n_even, 4 * n_even * n_even + 1)
    r3 = Fraction(n_even * n_even + 1, 4 * (n_even ** 3) + 5 * n_even)
    return {
        "raw_lo": raw_lo,
        "raw_hi": raw_hi,
        "madhava_lo": s0 + r2,
        "madhava_hi": s0 + r3,
    }


def run_theorem_t3() -> dict[str, Any]:
    """Certify Al-Farabi/Zu Chongzhi Farkas obstructions & Madhava-Hankel tightening."""
    holder_num = 3 ** 53
    holder_den = 2 ** 84
    zalzal_lhs = 12 ** 53
    zalzal_rhs = (11 ** 53) * (2 ** 7)

    steps_m = (0, 18, 36, 53)
    tol = Fraction(1, 1200)
    y_boxes_farabi = [
        (
            (Fraction(3, 2) ** m) * (Fraction(1, 1) - tol),
            (Fraction(3, 2) ** m) * (Fraction(1, 1) + tol),
        )
        for m in steps_m
    ]

    def slope_31_53_feasible(i_idx: int, j_idx: int) -> bool:
        dm = steps_m[j_idx] - steps_m[i_idx]
        ylo_i, yhi_i = y_boxes_farabi[i_idx]
        ylo_j, yhi_j = y_boxes_farabi[j_idx]
        target_pow = Fraction(2, 1) ** (31 * dm)
        return ((yhi_j / ylo_i) ** 53 >= target_pow) and ((ylo_j / yhi_i) ** 53 <= target_pow)

    farabi_local_ok = all(
        (slope_31_53_feasible(0, 1), slope_31_53_feasible(1, 2), slope_31_53_feasible(2, 3))
    )
    farabi_global_03 = slope_31_53_feasible(0, 3)

    zu_milu = Fraction(355, 113)
    zu_boxes = (
        (zu_milu, Fraction(4, 1)),
        (Fraction(2, 1), Fraction(3, 1)),
        (Fraction(2, 1), Fraction(3, 1)),
        (zu_milu, Fraction(4, 1)),
    )
    zu_4ray = farkas_4ray_log_concave_status_q(zu_boxes)

    fm_check_exponents = (
        (
            (Fraction(4, 1), Fraction(5, 1)),
            (Fraction(1, 1), Fraction(3, 1)),
            (Fraction(1, 1), Fraction(3, 1)),
            (Fraction(4, 1), Fraction(5, 1)),
        ),
        (
            (Fraction(2, 1), Fraction(4, 1)),
            (Fraction(2, 1), Fraction(3, 1)),
            (Fraction(2, 1), Fraction(3, 1)),
            (Fraction(2, 1), Fraction(4, 1)),
        ),
    )
    fm_matches: list[bool] = []
    for h_box in fm_check_exponents:
        pow2_box = tuple(
            (Fraction(2, 1) ** int(lo), Fraction(2, 1) ** int(hi)) for lo, hi in h_box
        )
        r4 = farkas_4ray_log_concave_status_q(pow2_box)  # type: ignore[arg-type]
        fm_ok = fourier_motzkin_log_concave_additive_q(h_box)
        fm_matches.append(r4["global_4ray_ok"] == fm_ok)

    farkas_ok = all(
        (
            holder_num == 19383245667680019896796723,
            holder_den == 19342813113834066795298816,
            holder_num > holder_den,
            zalzal_lhs != zalzal_rhs,
            farabi_local_ok,
            not farabi_global_03,
            zu_4ray["local_3pt_ok"],
            not zu_4ray["nonlocal_4pt_ok"],
            not zu_4ray["global_4ray_ok"],
            all(fm_matches),
        )
    )

    four_fifths = Fraction(4, 5)
    enc_n2 = madhava_sigma_enclosures_even_n_q(2)
    raw_n2_eig3_lo = Fraction(0, 1)
    raw_n2_eig3_hi = max(four_fifths - enc_n2["raw_lo"], enc_n2["raw_hi"] - four_fifths)
    mad_n2_eig3_lo = four_fifths - enc_n2["madhava_hi"]
    mad_n2_eig3_hi = four_fifths - enc_n2["madhava_lo"]

    hankel_raw_n2 = stieltjes_hankel_rh4_interval_q(
        Fraction(2, 1), Fraction(1, 1), raw_n2_eig3_lo, raw_n2_eig3_hi
    )
    hankel_mad_n2 = stieltjes_hankel_rh4_interval_q(
        Fraction(2, 1), Fraction(1, 1), mad_n2_eig3_lo, mad_n2_eig3_hi
    )
    hankel_rank2_boundary = stieltjes_hankel_rh4_interval_q(
        Fraction(2, 1), Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)
    )

    enc_n20 = madhava_sigma_enclosures_even_n_q(20)
    raw_n20_eig3_lo = four_fifths - enc_n20["raw_hi"]
    raw_n20_eig3_hi = four_fifths - enc_n20["raw_lo"]
    mad_n20_eig3_lo = four_fifths - enc_n20["madhava_hi"]
    mad_n20_eig3_hi = four_fifths - enc_n20["madhava_lo"]

    hankel_raw_n20 = stieltjes_hankel_rh4_interval_q(
        Fraction(2, 1), Fraction(1, 1), raw_n20_eig3_lo, raw_n20_eig3_hi
    )
    hankel_mad_n20 = stieltjes_hankel_rh4_interval_q(
        Fraction(2, 1), Fraction(1, 1), mad_n20_eig3_lo, mad_n20_eig3_hi
    )
    width_tightening_n20_floor = int(hankel_raw_n20["width"] // hankel_mad_n20["width"])

    ceil_ropt_mad_n2 = ceil_q(hankel_mad_n2["ropt_hi"])
    ceil_rh4_raw_n2 = ceil_q(hankel_raw_n2["rh4_lo"])
    ceil_rh4_mad_n2 = ceil_q(hankel_mad_n2["rh4_lo"])

    madhava_hankel_ok = all(
        (
            enc_n2["madhava_lo"] == Fraction(40, 51),
            enc_n2["madhava_hi"] == Fraction(11, 14),
            mad_n2_eig3_lo == Fraction(1, 70),
            mad_n2_eig3_hi == Fraction(4, 255),
            hankel_rank2_boundary["rh4_lo"] == Fraction(2, 1),
            hankel_raw_n2["rh4_lo"] < Fraction(2, 1),
            hankel_mad_n2["rh4_lo"] > Fraction(2, 1),
            ceil_ropt_mad_n2 == 2,
            ceil_rh4_raw_n2 == 2,
            ceil_rh4_mad_n2 == 3,
            width_tightening_n20_floor >= 1314575,
        )
    )

    passed = all((farkas_ok, madhava_hankel_ok))
    return {
        "novelty_class": "N1_diophantine_farkas_and_madhava_hankel_closure",
        "related_audits": ["AUDIT-002", "AUDIT-010", "AUDIT-014"],
        "farabi_holder_53_comma": f"{holder_num}/{holder_den}",
        "farabi_local_steps_pass_31_53": farabi_local_ok,
        "farabi_global_span_pass_31_53": farabi_global_03,
        "zu_chongzhi_4ray_local_3pt_ok": zu_4ray["local_3pt_ok"],
        "zu_chongzhi_4ray_nonlocal_4pt_ok": zu_4ray["nonlocal_4pt_ok"],
        "fourier_motzkin_equivalence_verified": all(fm_matches),
        "madhava_n2_eig3_bracket": [q_to_str(mad_n2_eig3_lo), q_to_str(mad_n2_eig3_hi)],
        "n2_ceil_ropt_2moment": ceil_ropt_mad_n2,
        "n2_ceil_rh4_raw_leibniz": ceil_rh4_raw_n2,
        "n2_ceil_rh4_madhava_r2_r3": ceil_rh4_mad_n2,
        "n2_rh4_madhava_lower": q_to_str(hankel_mad_n2["rh4_lo"]),
        "n20_rh4_width_tightening_floor": width_tightening_n20_floor,
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Certificate Builder & Hardened Fail-Closed Validators
# ---------------------------------------------------------------------------


def verify_core_invariants(core: Any, repo_root: Path = REPO_ROOT) -> None:
    """Validate structural, live on-disk anchor SHA-256, and mathematical invariants of unsigned core."""
    require_ok(isinstance(core, dict), "certificate core must be dict")
    require_ok(core.get("schema_version") == SCHEMA_VERSION, "schema_version mismatch")
    require_ok(core.get("arithmetic_domain") == ARITHMETIC_DOMAIN, "arithmetic_domain mismatch")
    require_ok(core.get("gate5_scope_statement") == GATE5_SCOPE_STATEMENT, "gate5_scope mismatch")
    require_ok(
        core.get("external_references_status") == EXTERNAL_REFERENCES_STATUS,
        "external_references_status mismatch",
    )

    anchors = core.get("on_disk_anchor_digests")
    require_ok(isinstance(anchors, dict), "on_disk_anchor_digests must be dict")
    live_anchors = compute_on_disk_anchor_digests(repo_root=repo_root)
    require_ok(
        set(anchors.keys()) == set(live_anchors.keys()),
        "on_disk_anchor_digests keys mismatch",
    )
    for key, val in anchors.items():
        require_ok(is_hex64(val), f"on-disk anchor digest {key} must be 64-hex")
        require_ok(
            hmac.compare_digest(val, live_anchors[key]),
            f"on-disk anchor digest {key} mismatch",
        )

    thms = core.get("theorems")
    require_ok(isinstance(thms, dict), "theorems must be dict")

    t1 = thms.get("t1_schur_and_gate5")
    require_ok(isinstance(t1, dict), "t1 must be dict")
    require_ok(t1.get("passed") is True, "t1 passed must be True")
    require_ok(t1.get("haynsworth_unitriangular_additivity_verified") is True, "t1 haynsworth flag")
    require_ok(t1.get("true_sylvester_congruence_h8_pair_verified") is True, "t1 congruence flag")
    require_ok(t1.get("gate5_passive_hydraulic_non_congruence_verified") is True, "t1 gate5 flag")
    require_ok(str_to_q(t1.get("petra_surge_unvented"), "petra_unv") == Fraction(1, 3), "petra 1/3")
    require_ok(str_to_q(t1.get("petra_surge_vented"), "petra_ven") == Fraction(64, 1365), "petra 64/1365")
    require_ok(str_to_q(t1.get("casarabe_conductance"), "casarabe") == Fraction(2755, 1806), "casarabe g")
    inert = t1.get("inertias_pos_neg_zero")
    require_ok(isinstance(inert, dict), "inertias must be dict")
    require_ok(inert.get("sigma_star_h8_fold_sheaf") == [4, 4, 0], "sigma_star inertia != [4,4,0]")
    require_ok(inert.get("hydraulic_conduit_8x8") == [7, 0, 1], "hydraulic_8x8 inertia != [7,0,1]")

    t2 = thms.get("t2_parity_sona_biruni")
    require_ok(isinstance(t2, dict), "t2 must be dict")
    require_ok(t2.get("passed") is True, "t2 passed must be True")
    require_ok(t2.get("pingala_nasta3_equals_sylvester_h8") is True, "t2 pingala h8 flag")
    require_ok(t2.get("ifa_even_parity_e8_spinor_roots") == 128, "t2 ifa 128 spinor roots")
    require_ok(t2.get("e8_total_kissing_roots") == 240, "t2 e8 240 roots")
    require_ok(t2.get("bamana_rm14_orth_a16_verified") is True, "t2 rm14 orth flag")
    require_ok(t2.get("sona_16_grids_gcd_ker_verified") is True, "t2 sona gcd flag")
    require_ok(t2.get("sona_2x2_ker_raw_to_walled") == [2, 1], "t2 sona 2x2 merge")
    require_ok(t2.get("sona_2x3_ker_raw_to_walled") == [1, 2], "t2 sona 2x3 split")
    require_ok(t2.get("biruni_stereographic_f8_e8_identity_verified") is True, "t2 biruni fold flag")

    t3 = thms.get("t3_farkas_and_madhava_hankel")
    require_ok(isinstance(t3, dict), "t3 must be dict")
    require_ok(t3.get("passed") is True, "t3 passed must be True")
    require_ok(t3.get("farabi_local_steps_pass_31_53") is True, "t3 farabi local")
    require_ok(t3.get("farabi_global_span_pass_31_53") is False, "t3 farabi global must be False")
    require_ok(t3.get("zu_chongzhi_4ray_local_3pt_ok") is True, "t3 zu local")
    require_ok(t3.get("zu_chongzhi_4ray_nonlocal_4pt_ok") is False, "t3 zu nonlocal must be False")
    require_ok(t3.get("fourier_motzkin_equivalence_verified") is True, "t3 fm flag")
    require_ok(t3.get("n2_ceil_ropt_2moment") == 2, "t3 ceil ropt == 2")
    require_ok(t3.get("n2_ceil_rh4_raw_leibniz") == 2, "t3 ceil rh4 raw == 2")
    require_ok(t3.get("n2_ceil_rh4_madhava_r2_r3") == 3, "t3 ceil rh4 madhava == 3")
    require_ok(str_to_q(t3.get("n2_rh4_madhava_lower"), "rh4_lo") > Fraction(2, 1), "t3 rh4_lo > 2")
    tight_fl = t3.get("n20_rh4_width_tightening_floor")
    require_ok(is_exact_int(tight_fl), "tightening floor must be int")
    require_ok(tight_fl >= 1314575, "tightening floor must be >= 1314575")

    require_ok(core.get("overall_passed") is True, "overall_passed must be True")


def build_certificate(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Execute T1, T2, T3, hash on-disk anchors, verify invariants, and seal canonical certificate."""
    anchors = compute_on_disk_anchor_digests(repo_root=repo_root)
    t1 = run_theorem_t1()
    t2 = run_theorem_t2()
    t3 = run_theorem_t3()
    overall = all_three_theorems_certified(t1["passed"], t2["passed"], t3["passed"])

    core: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "arithmetic_domain": ARITHMETIC_DOMAIN,
        "gate5_scope_statement": GATE5_SCOPE_STATEMENT,
        "external_references_status": EXTERNAL_REFERENCES_STATUS,
        "on_disk_anchor_digests": anchors,
        "theorems": {
            "t1_schur_and_gate5": t1,
            "t2_parity_sona_biruni": t2,
            "t3_farkas_and_madhava_hankel": t3,
        },
        "overall_passed": overall,
    }
    verify_core_invariants(core, repo_root=repo_root)
    payload_sha = sha256_bytes(canonical_json_bytes(core))
    sealed = dict(core)
    sealed["payload_sha256"] = payload_sha
    sealed["certificate_sha256"] = sha256_bytes(canonical_json_bytes(sealed))
    return sealed


def validate_certificate(cert: Any, repo_root: Path = REPO_ROOT) -> None:
    """Hardened public validator checking invariants, on-disk anchors, 64-hex digests, & live-oracle equality."""
    verify_core_invariants(cert, repo_root=repo_root)
    payload_sha = cert.get("payload_sha256")
    cert_sha = cert.get("certificate_sha256")
    require_ok(is_hex64(payload_sha), "payload_sha256 must be 64-hex")
    require_ok(is_hex64(cert_sha), "certificate_sha256 must be 64-hex")

    unsigned = {
        k: v for k, v in cert.items() if k not in ("payload_sha256", "certificate_sha256")
    }
    require_ok(
        hmac.compare_digest(payload_sha, sha256_bytes(canonical_json_bytes(unsigned))),
        "payload_sha256 digest mismatch",
    )
    with_payload = dict(unsigned)
    with_payload["payload_sha256"] = payload_sha
    require_ok(
        hmac.compare_digest(cert_sha, sha256_bytes(canonical_json_bytes(with_payload))),
        "certificate_sha256 digest mismatch",
    )
    recomputed = build_certificate(repo_root=repo_root)
    require_ok(
        canonical_json_bytes(cert) == canonical_json_bytes(recomputed),
        "certificate diverges from freshly recomputed pure-Q oracle",
    )


def format_canonical_certificate_json(cert: dict[str, Any], repo_root: Path = REPO_ROOT) -> str:
    """Format validated certificate deterministically with 2-space indent."""
    validate_certificate(cert, repo_root=repo_root)
    return json.dumps(cert, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def check_certificate_file(cert_path: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Validate on-disk certificate JSON (strict duplicate-key parse & raw-bytes SHA-256 binding)."""
    require_ok(isinstance(cert_path, Path), "cert_path must be Path")
    require_ok(cert_path.is_file(), f"certificate file not found: {cert_path.name}")
    raw_bytes = cert_path.read_bytes()
    raw_text = raw_bytes.decode("utf-8")
    loaded = loads_strict_json(raw_text)
    validate_certificate(loaded, repo_root=repo_root)
    expected_bytes = format_canonical_certificate_json(loaded, repo_root=repo_root).encode("utf-8")
    require_ok(
        hmac.compare_digest(sha256_bytes(raw_bytes), sha256_bytes(expected_bytes)),
        "on-disk certificate raw-bytes SHA-256 does not match canonical certificate",
    )
    return loaded


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint supporting default check, --check, --write, and --json."""
    parser = argparse.ArgumentParser(
        description="Verify historical exact-operator applications & Gate-5 congruence boundaries."
    )
    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument("--check", action="store_true", help="Validate existing certificate JSON.")
    mode.add_argument("--write", action="store_true", help="Write canonical certificate JSON.")
    mode.add_argument("--json", action="store_true", help="Print canonical certificate JSON to stdout.")
    parser.add_argument("--cert-path", type=Path, default=DEFAULT_CERT_PATH, help="Certificate path.")
    args = parser.parse_args(argv)

    if args.write:
        cert = build_certificate()
        args.cert_path.write_text(format_canonical_certificate_json(cert), encoding="utf-8")
        print(f"WROTE {args.cert_path.name} certificate_sha256={cert['certificate_sha256']}")
        return 0
    if args.json:
        cert = build_certificate()
        sys.stdout.write(format_canonical_certificate_json(cert))
        return 0
    cert = check_certificate_file(args.cert_path)
    print(f"PASS {args.cert_path.name} certificate_sha256={cert['certificate_sha256']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
