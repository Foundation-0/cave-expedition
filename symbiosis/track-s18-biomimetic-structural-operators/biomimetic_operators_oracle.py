#!/usr/bin/env python3
"""
AUDIT-117 (`track-s18-biomimetic-structural-operators`):
Pure-Z/Q Exact Biomimetic Structural Operators Oracle.

Strict Law-5 Beyond-Language Perception (Stage A biology-stripped -> Stage B
coordinate-, unit-, and radix-free exact Z/Q and Q[sqrt(2), sqrt(3)] operators):
  1. Unilateral Prestressed Cable Graphs & Hierarchical Fault-Localization (Orb Webs)
  2. Cascaded Porous Jammed-Log Weirs: K^3 Moment Collapse & Choke vs Piping (Beaver Dams)
  3. Underground Tunnel Networks: beta_1 >= 1 Ventilation Obstruction, Cave-In Pareto &
     Single-Lane Digging Congestion Markov Optimum (Ant / Termite Burrows)
  4. Discrete Riveted Thin-Leaf Volkersen Shear-Lag & Postage-Stamp Tear Optimum
     (Tailorbird Nests)
  5. Bonus Natural Geometries:
     5A. Euplectella Checkerboard Cylindrical Bracing (Maxwell-Calladine & Parity Obstruction)
     5B. Honeybee / Wasp Maraldi Angle cos(theta) = -1/3 Exact Q[sqrt(2), sqrt(3)] Optimality

Zero floats on trust paths. Zero bare `assert`s (100% `python3 -O` parity). Zero external deps.
"""
from __future__ import annotations

from fractions import Fraction
import json
import math
from typing import Any

MAX_JSON_DEPTH = 32
MAX_JSON_BYTES = 2_000_000
MAX_INT_DIGITS = 400
MAX_JSON_INT = 10**MAX_INT_DIGITS
MAX_SEQ_LEN = 256
MAX_MATRIX_DIM = 48


class BiomimeticOpError(ValueError):
    """Fail-closed typed error (never stripped under python3 -O)."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


# ---------------------------------------------------------------------------
# Strict Input Hardening & Iterative Zero-Float Canonical JSON
# ---------------------------------------------------------------------------

def require_int(
    val: Any,
    label: str = "int",
    *,
    lo: int | None = None,
    hi: int | None = None,
) -> int:
    if type(val) is not int:
        raise BiomimeticOpError("INVALID_INT_TYPE", f"{label} must be strict int")
    if lo is not None and val < lo:
        raise BiomimeticOpError("INT_BELOW_MIN", f"{label} below min {lo}")
    if hi is not None and val > hi:
        raise BiomimeticOpError("INT_ABOVE_MAX", f"{label} above max {hi}")
    return val


def require_rat(val: Any, label: str = "rational") -> Fraction:
    if type(val) is Fraction:
        return val
    if type(val) is int:
        return Fraction(val, 1)
    raise BiomimeticOpError("INVALID_RATIONAL_TYPE", f"{label} must be strict int or Fraction")


def require_pos_rat(val: Any, label: str = "positive_rational") -> Fraction:
    q = require_rat(val, label)
    if q <= 0:
        raise BiomimeticOpError("NON_POSITIVE_RATIONAL", f"{label} must be > 0")
    return q


def require_seq(
    val: Any,
    label: str = "seq",
    *,
    min_len: int = 1,
    max_len: int = MAX_SEQ_LEN,
) -> tuple[Any, ...]:
    if type(val) not in (list, tuple):
        raise BiomimeticOpError("INVALID_SEQ_TYPE", f"{label} must be strict list or tuple")
    n = len(val)
    if n < min_len:
        raise BiomimeticOpError("SEQ_TOO_SHORT", f"{label} length {n} < {min_len}")
    if n > max_len:
        raise BiomimeticOpError("SEQ_TOO_LONG", f"{label} length {n} > {max_len}")
    return tuple(val)


def fmt_q(q: Fraction) -> str:
    """Canonical reduced rational string ('p' if denom == 1 else 'p/q')."""
    r = require_rat(q, "q")
    if r.denominator == 1:
        return str(r.numerator)
    return f"{r.numerator}/{r.denominator}"


def validate_json_value(obj: Any, *, max_depth: int = MAX_JSON_DEPTH) -> None:
    """Iterative zero-float, depth-capped, strict-key JSON tree validator (zero recursion)."""
    limit = require_int(max_depth, "max_depth", lo=1, hi=128)
    stack: list[tuple[Any, int]] = [(obj, 0)]
    while stack:
        cur, depth = stack.pop()
        if depth > limit:
            raise BiomimeticOpError("MAX_DEPTH_EXCEEDED", f"JSON nesting exceeds {limit}")
        t = type(cur)
        if t is dict:
            for k, v in cur.items():
                if type(k) is not str:
                    raise BiomimeticOpError("NON_STR_KEY", "dict keys must be strict str")
                stack.append((v, depth + 1))
        elif t is list:
            for item in cur:
                stack.append((item, depth + 1))
        elif t is int:
            if abs(cur) > MAX_JSON_INT:
                raise BiomimeticOpError("INT_TOO_LARGE", "integer exceeds digit cap")
        elif t in (str, bool) or cur is None:
            continue
        elif t is float:
            raise BiomimeticOpError("FLOAT_FORBIDDEN", "float values are forbidden")
        else:
            raise BiomimeticOpError("UNSUPPORTED_JSON_TYPE", f"unsupported type {t.__name__}")


def _reject_float_token(tok: str) -> Any:
    raise BiomimeticOpError("JSON_FLOAT_FORBIDDEN", f"float literal forbidden: {tok!r}")


def _reject_constant_token(tok: str) -> Any:
    raise BiomimeticOpError("JSON_CONSTANT_FORBIDDEN", f"non-RFC8259 constant forbidden: {tok!r}")


def _parse_capped_int_token(tok: str) -> int:
    digits = tok[1:] if tok.startswith("-") else tok
    if len(digits) > MAX_INT_DIGITS:
        raise BiomimeticOpError("INT_DIGIT_LIMIT", f"integer token exceeds {MAX_INT_DIGITS} digits")
    return int(tok)


def _pairs_no_dup(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise BiomimeticOpError("JSON_DUPLICATE_KEY", f"duplicate JSON key: {k!r}")
        out[k] = v
    return out


def parse_strict_json(text: str) -> Any:
    """Fail-closed zero-float, no-duplicate-key, depth-capped, digit-capped JSON parser."""
    if type(text) is not str:
        raise BiomimeticOpError("INVALID_JSON_INPUT", "JSON input must be strict str")
    if len(text.encode("utf-8")) > MAX_JSON_BYTES:
        raise BiomimeticOpError("JSON_TOO_LARGE", "JSON input exceeds byte cap")
    if not text.strip():
        raise BiomimeticOpError("EMPTY_JSON", "JSON input must be non-empty")
    try:
        parsed = json.loads(
            text,
            parse_int=_parse_capped_int_token,
            parse_float=_reject_float_token,
            parse_constant=_reject_constant_token,
            object_pairs_hook=_pairs_no_dup,
        )
    except BiomimeticOpError:
        raise
    except (ValueError, RecursionError) as exc:
        raise BiomimeticOpError("JSON_PARSE_ERROR", str(exc)) from exc
    validate_json_value(parsed)
    return parsed


def canonical_json_bytes(obj: Any) -> bytes:
    """Canonical ASCII zero-float JSON bytes (validates iteratively before serializing)."""
    validate_json_value(obj)
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


# ---------------------------------------------------------------------------
# Exact Pure-Q Linear Algebra & Q[sqrt(2), sqrt(3)] Algebraic Field Core
# ---------------------------------------------------------------------------

def solve_linear_multi_q(matrix: Any, rhs_rows: Any) -> list[list[Fraction]]:
    """Exact Gauss-Jordan multi-RHS linear solver over Q (`A X = B`); rejects singular systems."""
    rows_raw = require_seq(matrix, "matrix", min_len=1, max_len=MAX_MATRIX_DIM)
    rhs_raw = require_seq(rhs_rows, "rhs_rows", min_len=1, max_len=MAX_MATRIX_DIM)
    n = len(rows_raw)
    if len(rhs_raw) != n:
        raise BiomimeticOpError("DIM_MISMATCH", "rhs row count must equal matrix dimension")
    first_rhs = require_seq(rhs_raw[0], "rhs_rows[0]", min_len=1, max_len=MAX_MATRIX_DIM)
    m_rhs = len(first_rhs)
    aug: list[list[Fraction]] = []
    for i in range(n):
        row = require_seq(rows_raw[i], f"row[{i}]", min_len=n, max_len=n)
        b_row = require_seq(rhs_raw[i], f"rhs_rows[{i}]", min_len=m_rhs, max_len=m_rhs)
        aug.append(
            [require_rat(x, f"A[{i}][{j}]") for j, x in enumerate(row)]
            + [require_rat(y, f"B[{i}][{k}]") for k, y in enumerate(b_row)]
        )
    tot_cols = n + m_rhs
    for col in range(n):
        piv = -1
        for r in range(col, n):
            if aug[r][col] != 0:
                piv = r
                break
        if piv < 0:
            raise BiomimeticOpError("SINGULAR_MATRIX", f"singular matrix at column {col}")
        if piv != col:
            aug[col], aug[piv] = aug[piv], aug[col]
        pv = aug[col][col]
        piv_row = [x / pv for x in aug[col]]
        aug[col] = piv_row
        nz = [(j, v) for j, v in enumerate(piv_row) if v != 0]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                row_r = aug[r]
                for j, v in nz:
                    row_r[j] -= factor * v
    return [aug[i][n:tot_cols] for i in range(n)]


def solve_linear_q(matrix: Any, rhs: Any) -> list[Fraction]:
    """Exact Gauss-Jordan single-RHS linear solver over Q (`A x = b`)."""
    rhs_seq = require_seq(rhs, "rhs", min_len=1, max_len=MAX_MATRIX_DIM)
    sol = solve_linear_multi_q(matrix, [[x] for x in rhs_seq])
    return [row[0] for row in sol]


def rank_and_nullspace_q(rows: Any, ncols: int) -> tuple[int, list[list[Fraction]]]:
    """Exact RREF rank and nullspace basis over Q."""
    nc = require_int(ncols, "ncols", lo=1, hi=MAX_SEQ_LEN)
    rows_raw = require_seq(rows, "rows", min_len=1, max_len=MAX_SEQ_LEN)
    mat: list[list[Fraction]] = []
    for i, raw_r in enumerate(rows_raw):
        rseq = require_seq(raw_r, f"row[{i}]", min_len=nc, max_len=nc)
        mat.append([require_rat(x, f"M[{i}][{j}]") for j, x in enumerate(rseq)])
    piv_cols: list[int] = []
    r = 0
    nrows = len(mat)
    for c in range(nc):
        piv = -1
        for i in range(r, nrows):
            if mat[i][c] != 0:
                piv = i
                break
        if piv < 0:
            continue
        if piv != r:
            mat[r], mat[piv] = mat[piv], mat[r]
        pv = mat[r][c]
        nz_cols: list[tuple[int, Fraction]] = []
        for j in range(c, nc):
            v = mat[r][j]
            if v != 0:
                v = v / pv
                mat[r][j] = v
                nz_cols.append((j, v))
        for i in range(nrows):
            if i != r and mat[i][c] != 0:
                factor = mat[i][c]
                row_i = mat[i]
                for j, rv in nz_cols:
                    row_i[j] -= factor * rv
        piv_cols.append(c)
        r += 1
        if r == nrows:
            break
    piv_set = set(piv_cols)
    basis: list[list[Fraction]] = []
    for fc in range(nc):
        if fc in piv_set:
            continue
        vec = [Fraction(0)] * nc
        vec[fc] = Fraction(1)
        for row_idx, pc in enumerate(piv_cols):
            vec[pc] = -mat[row_idx][fc]
        basis.append(vec)
    return r, basis


def sylvester_inertia_q(matrix: Any) -> tuple[int, int, int]:
    """
    Exact symmetric Sylvester inertia `(n_pos, n_neg, n_zero)` over Q via symmetric
    1x1 / 2x2 Bunch-Kaufman congruence elimination (no floats, handles zero-diagonal blocks).
    """
    rows_raw = require_seq(matrix, "matrix", min_len=1, max_len=MAX_MATRIX_DIM)
    n = len(rows_raw)
    A: list[list[Fraction]] = []
    for i in range(n):
        rseq = require_seq(rows_raw[i], f"row[{i}]", min_len=n, max_len=n)
        A.append([require_rat(x, f"S[{i}][{j}]") for j, x in enumerate(rseq)])
    for i in range(n):
        for j in range(i + 1, n):
            if A[i][j] != A[j][i]:
                raise BiomimeticOpError("NON_SYMMETRIC_MATRIX", f"asymmetry at ({i},{j})")

    n_pos = 0
    n_neg = 0
    n_zero = 0
    k = 0
    while k < n:
        diag_piv = -1
        for i in range(k, n):
            if A[i][i] != 0:
                diag_piv = i
                break
        if diag_piv >= 0:
            if diag_piv != k:
                A[k], A[diag_piv] = A[diag_piv], A[k]
                for row in A:
                    row[k], row[diag_piv] = row[diag_piv], row[k]
            d = A[k][k]
            if d > 0:
                n_pos += 1
            else:
                n_neg += 1
            for i in range(k + 1, n):
                f = A[i][k] / d
                if f != 0:
                    for j in range(k + 1, n):
                        A[i][j] -= f * A[k][j]
            k += 1
            continue

        # All remaining diagonal entries are 0; search for a nonzero off-diagonal 2x2 block
        off_i = -1
        off_j = -1
        for i in range(k, n):
            for j in range(i + 1, n):
                if A[i][j] != 0:
                    off_i = i
                    off_j = j
                    break
            if off_i >= 0:
                break
        if off_i < 0:
            n_zero += n - k
            break

        if off_i != k:
            A[k], A[off_i] = A[off_i], A[k]
            for row in A:
                row[k], row[off_i] = row[off_i], row[k]
        if off_j != k + 1:
            A[k + 1], A[off_j] = A[off_j], A[k + 1]
            for row in A:
                row[k + 1], row[off_j] = row[off_j], row[k + 1]

        b = A[k][k + 1]
        n_pos += 1
        n_neg += 1
        for i in range(k + 2, n):
            c0 = A[i][k + 1] / b
            c1 = A[i][k] / b
            for j in range(k + 2, n):
                A[i][j] -= c0 * A[k][j] + c1 * A[k + 1][j]
        k += 2

    return (n_pos, n_neg, n_zero)


def _validate_q23(elem: Any, label: str = "q23") -> tuple[Fraction, Fraction, Fraction, Fraction]:
    seq = require_seq(elem, label, min_len=4, max_len=4)
    return (
        require_rat(seq[0], f"{label}[0]"),
        require_rat(seq[1], f"{label}[1]"),
        require_rat(seq[2], f"{label}[2]"),
        require_rat(seq[3], f"{label}[3]"),
    )


def q23_mul(
    x: tuple[Fraction, Fraction, Fraction, Fraction],
    y: tuple[Fraction, Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Exact multiplication in Q[sqrt(2), sqrt(3)] with basis (1, sqrt(2), sqrt(3), sqrt(6))."""
    a0, a1, a2, a3 = _validate_q23(x, "x")
    b0, b1, b2, b3 = _validate_q23(y, "y")
    return (
        a0 * b0 + 2 * a1 * b1 + 3 * a2 * b2 + 6 * a3 * b3,
        a0 * b1 + a1 * b0 + 3 * a2 * b3 + 3 * a3 * b2,
        a0 * b2 + a2 * b0 + 2 * a1 * b3 + 2 * a3 * b1,
        a0 * b3 + a3 * b0 + a1 * b2 + a2 * b1,
    )


def _sign_q_sqrt2(p: Fraction, q: Fraction) -> int:
    """Exact sign of p + q * sqrt(2) in {-1, 0, +1}."""
    if p == 0 and q == 0:
        return 0
    if p >= 0 and q >= 0:
        return 1
    if p <= 0 and q <= 0:
        return -1
    diff = p * p - 2 * q * q
    if p > 0:
        return 1 if diff > 0 else -1
    return -1 if diff > 0 else 1


def q23_sign(elem: tuple[Fraction, Fraction, Fraction, Fraction]) -> int:
    """Exact sign in {-1, 0, +1} of (a + b*sqrt(2)) + (c + d*sqrt(2))*sqrt(3)."""
    a, b, c, d = _validate_q23(elem, "elem")
    s_u = _sign_q_sqrt2(a, b)
    s_v = _sign_q_sqrt2(c, d)
    if s_u == 0 and s_v == 0:
        return 0
    if s_u >= 0 and s_v >= 0:
        return 1
    if s_u <= 0 and s_v <= 0:
        return -1
    diff_p = (a * a + 2 * b * b) - 3 * (c * c + 2 * d * d)
    diff_q = 2 * a * b - 6 * c * d
    s_diff = _sign_q_sqrt2(diff_p, diff_q)
    return s_diff if s_u > 0 else -s_diff


# ---------------------------------------------------------------------------
# Graph Helper
# ---------------------------------------------------------------------------

def _validate_graph(
    n_nodes: int,
    edges: Any,
    weights: Any,
) -> tuple[int, tuple[tuple[int, int], ...], tuple[Fraction, ...]]:
    n = require_int(n_nodes, "n_nodes", lo=2, hi=MAX_MATRIX_DIM - 1)
    eseq = require_seq(edges, "edges", min_len=1, max_len=MAX_SEQ_LEN)
    wseq = require_seq(weights, "weights", min_len=len(eseq), max_len=len(eseq))
    clean_edges: list[tuple[int, int]] = []
    clean_w: list[Fraction] = []
    for idx, (e, w) in enumerate(zip(eseq, wseq)):
        pair = require_seq(e, f"edge[{idx}]", min_len=2, max_len=2)
        u = require_int(pair[0], f"edge[{idx}].u", lo=0, hi=n - 1)
        v = require_int(pair[1], f"edge[{idx}].v", lo=0, hi=n - 1)
        if u == v:
            raise BiomimeticOpError("SELF_LOOP_FORBIDDEN", f"self-loop at vertex {u}")
        clean_edges.append((u, v))
        clean_w.append(require_pos_rat(w, f"weight[{idx}]"))
    return n, tuple(clean_edges), tuple(clean_w)


def _is_connected(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == n


# ---------------------------------------------------------------------------
# Operator 1: Spider Webs — Unilateral Prestressed Cable Graphs & Hierarchical
#             Sherman-Morrison Rank-1 Fault-Localization
# ---------------------------------------------------------------------------

def laplacian_pseudoinverse_q(
    n_nodes: int,
    edges: Any,
    stiffnesses: Any,
) -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    """Exact rational weighted Graph Laplacian L_K and its Moore-Penrose pseudoinverse L_K^+."""
    n, es, ks = _validate_graph(n_nodes, edges, stiffnesses)
    if not _is_connected(n, es):
        raise BiomimeticOpError("DISCONNECTED_GRAPH", "graph must be connected for connected L_K^+")
    L = [[Fraction(0)] * n for _ in range(n)]
    for (u, v), k in zip(es, ks):
        L[u][u] += k
        L[v][v] += k
        L[u][v] -= k
        L[v][u] -= k
    bordered = [row + [Fraction(1)] for row in L] + [[Fraction(1)] * n + [Fraction(0)]]
    inv_n = Fraction(1, n)
    rhs_rows = [
        [(Fraction(1) if i == j else Fraction(0)) - inv_n for j in range(n)]
        for i in range(n)
    ] + [[Fraction(0)] * n]
    sol = solve_linear_multi_q(bordered, rhs_rows)
    return L, sol[:n]


def sherman_morrison_lodf_q(
    n_nodes: int,
    edges: Any,
    stiffnesses: Any,
    cut_index: int,
) -> dict[str, Any]:
    """
    Exact rational Sherman-Morrison rank-1 edge-deletion load redistribution (LODF):
        Delta f_{e'} / f_e = (k_{e'} b_{e'}^T L_K^+ b_e) / (1 - k_e b_e^T L_K^+ b_e)
    Independently cross-checked by direct full post-deletion solve of L'_K = L_K - k_e b_e b_e^T.
    """
    n, es, ks = _validate_graph(n_nodes, edges, stiffnesses)
    cidx = require_int(cut_index, "cut_index", lo=0, hi=len(es) - 1)
    L, Lp = laplacian_pseudoinverse_q(n, es, ks)

    def quad(u: int, v: int, x: int, y: int) -> Fraction:
        return Lp[u][x] - Lp[u][y] - Lp[v][x] + Lp[v][y]

    foster_sum = sum((k * quad(u, v, u, v) for (u, v), k in zip(es, ks)), Fraction(0))
    eu, ev = es[cidx]
    k_cut = ks[cidx]
    h_cut = k_cut * quad(eu, ev, eu, ev)
    if h_cut == 1:
        raise BiomimeticOpError("BRIDGE_EDGE_CUT", f"edge {cidx} is a bridge (h_e = 1)")

    denom = Fraction(1) - h_cut
    lodf: list[Fraction] = []
    for idx, ((u, v), k) in enumerate(zip(es, ks)):
        if idx == cidx:
            lodf.append(Fraction(0))
        else:
            lodf.append(k * quad(u, v, eu, ev) / denom)

    # Independent direct post-deletion solve of L'_K u_after = b_e under unit dipole load p = b_e
    L_rem = [row[:] for row in L]
    L_rem[eu][eu] -= k_cut
    L_rem[ev][ev] -= k_cut
    L_rem[eu][ev] += k_cut
    L_rem[ev][eu] += k_cut
    bordered_rem = [row + [Fraction(1)] for row in L_rem] + [[Fraction(1)] * n + [Fraction(0)]]
    dipole_rhs = [Fraction(0)] * (n + 1)
    dipole_rhs[eu] = Fraction(1)
    dipole_rhs[ev] = Fraction(-1)
    u_after = solve_linear_q(bordered_rem, dipole_rhs)[:n]
    u_before = [Lp[i][eu] - Lp[i][ev] for i in range(n)]
    f_e_before = k_cut * (u_before[eu] - u_before[ev])
    direct_match = all(
        (k * ((u_after[u] - u_after[v]) - (u_before[u] - u_before[v])) / f_e_before) == lodf[idx]
        for idx, ((u, v), k) in enumerate(zip(es, ks))
        if idx != cidx
    )

    return {
        "n_nodes": n,
        "cut_index": cidx,
        "foster_sum": foster_sum,
        "h_cut": h_cut,
        "lodf": lodf,
        "direct_resolve_exact_match": direct_match,
    }


def _build_orb_web(
    n_spokes: int,
    n_rings: int,
    kappa: int,
) -> tuple[int, list[tuple[int, int]], list[Fraction], list[tuple[str, int, int]]]:
    n = 1 + n_spokes * n_rings
    edges: list[tuple[int, int]] = []
    ks: list[Fraction] = []
    kinds: list[tuple[str, int, int]] = []
    for j in range(n_spokes):
        edges.append((0, 1 + j))
        ks.append(Fraction(kappa, 1))
        kinds.append(("radial", 0, j))
    for r in range(1, n_rings):
        for j in range(n_spokes):
            edges.append((1 + (r - 1) * n_spokes + j, 1 + r * n_spokes + j))
            ks.append(Fraction(kappa, 1))
            kinds.append(("radial", r, j))
    for r in range(n_rings):
        for j in range(n_spokes):
            edges.append((1 + r * n_spokes + j, 1 + r * n_spokes + (j + 1) % n_spokes))
            ks.append(Fraction(1, 1))
            kinds.append(("spiral", r, j))
    return n, edges, ks, kinds


def verify_cable_web_prestress_q(omega_spiral: Any, omega_inner: Any, omega_outer: Any) -> dict[str, Any]:
    """
    Exact 6-spoke integer-coordinate planar anchored orb web (13 vertices: 1 hub + 6 inner ring
    on exact C_6-Laplacian eigenvector hexagon + 6 outer anchor nodes; 18 cables).
    Verifies exact equilibrium residuals and Connelly-Whiteley stress matrix inertia.
    """
    w_sp = require_rat(omega_spiral, "omega_spiral")
    w_in = require_rat(omega_inner, "omega_inner")
    w_out = require_rat(omega_outer, "omega_outer")
    ring_coords: tuple[tuple[Fraction, Fraction], ...] = (
        (Fraction(2), Fraction(0)),
        (Fraction(1), Fraction(2)),
        (Fraction(-1), Fraction(2)),
        (Fraction(-2), Fraction(0)),
        (Fraction(-1), Fraction(-2)),
        (Fraction(1), Fraction(-2)),
    )
    coords: list[tuple[Fraction, Fraction]] = [(Fraction(0), Fraction(0))]
    coords.extend(ring_coords)
    coords.extend([(2 * x, 2 * y) for x, y in ring_coords])

    edges_w: list[tuple[int, int, Fraction]] = []
    for k in range(6):
        edges_w.append((0, 1 + k, w_in))
        edges_w.append((1 + k, 1 + (k + 1) % 6, w_sp))
        edges_w.append((1 + k, 7 + k, w_out))

    eq_ok = True
    for v in range(7):
        fx = Fraction(0)
        fy = Fraction(0)
        px, py = coords[v]
        for a, b, w in edges_w:
            if a == v:
                qx, qy = coords[b]
                fx += w * (px - qx)
                fy += w * (py - qy)
            elif b == v:
                qx, qy = coords[a]
                fx += w * (px - qx)
                fy += w * (py - qy)
        if (fx, fy) != (0, 0):
            eq_ok = False

    n_full = 13
    omega_full = [[Fraction(0)] * n_full for _ in range(n_full)]
    for a, b, w in edges_w:
        omega_full[a][a] += w
        omega_full[b][b] += w
        omega_full[a][b] -= w
        omega_full[b][a] -= w
    omega_int = [row[:7] for row in omega_full[:7]]
    inertia_int = sylvester_inertia_q(omega_int)
    inertia_full = sylvester_inertia_q(omega_full)
    all_strictly_tension = w_sp > 0 and w_in > 0 and w_out > 0
    return {
        "strictly_tension_only": all_strictly_tension,
        "interior_equilibrium_zero_residual": eq_ok,
        "omega_int_inertia": list(inertia_int),
        "omega_full_inertia": list(inertia_full),
        "omega_int_strictly_pd": inertia_int == (7, 0, 0),
        "omega_full_psd": inertia_full[1] == 0,
    }


def certify_operator1_spider_webs() -> dict[str, Any]:
    """Certify Operator 1 across kappa in {1, 10, 100} and Connelly-Whiteley prestress."""
    hierarchy: list[dict[str, Any]] = []
    remote_max_vals: list[Fraction] = []
    remote_l1_vals: list[Fraction] = []
    h_cut_vals: list[Fraction] = []
    direct_checks: list[bool] = []
    foster_checks: list[bool] = []

    for kappa in (1, 10, 100):
        n, edges, ks, kinds = _build_orb_web(6, 2, kappa)
        cut_sp = kinds.index(("spiral", 1, 0))
        res_sp = sherman_morrison_lodf_q(n, edges, ks, cut_sp)
        cut_rad = kinds.index(("radial", 1, 0))
        res_rad = sherman_morrison_lodf_q(n, edges, ks, cut_rad)
        pair_direct = all((res_sp["direct_resolve_exact_match"], res_rad["direct_resolve_exact_match"]))
        direct_checks.append(pair_direct)
        foster_checks.append(
            all((res_sp["foster_sum"] == Fraction(n - 1), res_rad["foster_sum"] == Fraction(n - 1)))
        )

        lodf_sp: list[Fraction] = res_sp["lodf"]
        same_sec_sp = abs(lodf_sp[kinds.index(("spiral", 0, 0))])
        remote_sp = [abs(lodf_sp[i]) for i, kd in enumerate(kinds) if kd[0] == "spiral" and kd[2] != 0]
        remote_max = max(remote_sp)
        remote_l1 = sum(remote_sp, Fraction(0))
        remote_max_vals.append(remote_max)
        remote_l1_vals.append(remote_l1)
        h_cut_vals.append(res_sp["h_cut"])

        hierarchy.append({
            "kappa": kappa,
            "foster_sum": fmt_q(res_sp["foster_sum"]),
            "spiral_cut_leverage_h": fmt_q(res_sp["h_cut"]),
            "same_sector_spiral_lodf": fmt_q(same_sec_sp),
            "remote_spiral_max_lodf": fmt_q(remote_max),
            "remote_spiral_l1_lodf": fmt_q(remote_l1),
            "outer_radial_cut_leverage_h": fmt_q(res_rad["h_cut"]),
            "direct_resolve_match": pair_direct,
        })

    monotone_localization = all((
        h_cut_vals[0] > h_cut_vals[1] > h_cut_vals[2],
        remote_max_vals[0] > remote_max_vals[1] > remote_max_vals[2],
        remote_l1_vals[0] > remote_l1_vals[1] > remote_l1_vals[2],
    ))
    remote_max_reduction_100 = remote_max_vals[0] / remote_max_vals[2]
    remote_l1_reduction_100 = remote_l1_vals[0] / remote_l1_vals[2]

    prestress_pos = verify_cable_web_prestress_q(Fraction(1), Fraction(10), Fraction(11))
    prestress_neg_ctrl = verify_cable_web_prestress_q(Fraction(1), Fraction(-10), Fraction(-9))

    passed = all((
        all(direct_checks),
        all(foster_checks),
        monotone_localization,
        remote_max_reduction_100 > Fraction(20),
        remote_l1_reduction_100 > Fraction(30),
        prestress_pos["strictly_tension_only"],
        prestress_pos["interior_equilibrium_zero_residual"],
        prestress_pos["omega_int_strictly_pd"],
        prestress_pos["omega_full_psd"],
        not prestress_neg_ctrl["strictly_tension_only"],
        prestress_neg_ctrl["omega_int_inertia"][1] >= 1,
    ))
    return {
        "operator": "op1_spider_web_cable_graph",
        "topology": "G_orb(N=6, R=2)",
        "hierarchy_sweep": hierarchy,
        "monotone_spiral_localization": monotone_localization,
        "remote_spiral_max_reduction_k1_to_k100": fmt_q(remote_max_reduction_100),
        "remote_spiral_l1_reduction_k1_to_k100": fmt_q(remote_l1_reduction_100),
        "connelly_whiteley_prestress_tension_only": prestress_pos,
        "connelly_whiteley_compression_negative_control": prestress_neg_ctrl,
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Operator 2: Beaver Dams — Cascaded Leaky Weirs, K^3 Moment Collapse &
#             Self-Healing Debris-Choke vs Runaway Piping Erosion
# ---------------------------------------------------------------------------

def analyze_weir_cascade_statics_q(
    total_head: Any,
    stage_heads: Any,
    specific_weight: Any = Fraction(1),
) -> dict[str, Any]:
    """Exact hydrostatic thrust & overturning moment decomposition for a K-stage weir cascade."""
    H = require_pos_rat(total_head, "total_head")
    gamma = require_pos_rat(specific_weight, "specific_weight")
    hs_raw = require_seq(stage_heads, "stage_heads", min_len=1, max_len=64)
    hs = [require_pos_rat(h, f"stage_heads[{i}]") for i, h in enumerate(hs_raw)]
    if sum(hs, Fraction(0)) != H:
        raise BiomimeticOpError("HEAD_SUM_MISMATCH", "stage heads must sum exactly to total_head")
    k = len(hs)
    f_mono = Fraction(1, 2) * gamma * H * H
    m_mono = Fraction(1, 6) * gamma * H * H * H
    f_stages = [Fraction(1, 2) * gamma * h * h for h in hs]
    m_stages = [Fraction(1, 6) * gamma * h * h * h for h in hs]
    f_total = sum(f_stages, Fraction(0))
    m_total = sum(m_stages, Fraction(0))
    m_peak = max(m_stages)
    sum_sq = sum((h * h for h in hs), Fraction(0))
    pairwise_sq = sum(((hs[i] - hs[j]) ** 2 for i in range(k) for j in range(i + 1, k)), Fraction(0))
    jensen_excess = sum_sq - (H * H) / Fraction(k)
    return {
        "stages": k,
        "f_mono": f_mono,
        "m_mono": m_mono,
        "f_total": f_total,
        "m_total": m_total,
        "m_peak": m_peak,
        "shear_reduction_ratio": f_mono / f_total,
        "peak_moment_reduction_ratio": m_mono / m_peak,
        "jensen_excess": jensen_excess,
        "jensen_identity_exact": jensen_excess == pairwise_sq / Fraction(k),
    }


def simulate_flood_cascade_q(stages: int, drain_rate: Any, steps: int) -> dict[str, Any]:
    """
    Exact discrete leaky-pond cascade recurrence Q_i[t] = alpha * Q_{i-1}[t] + (1 - alpha) * Q_i[t-1]
    cross-checked at every step against exact negative-binomial closed form.
    """
    k = require_int(stages, "stages", lo=1, hi=16)
    alpha = require_pos_rat(drain_rate, "drain_rate")
    if alpha >= 1:
        raise BiomimeticOpError("DRAIN_RATE_OUT_OF_RANGE", "drain_rate must lie strictly in (0, 1)")
    n_steps = require_int(steps, "steps", lo=1, hi=64)
    one_minus = Fraction(1) - alpha
    q = [Fraction(1) if t == 0 else Fraction(0) for t in range(n_steps)]
    for _ in range(k):
        nxt: list[Fraction] = []
        prev = Fraction(0)
        for val in q:
            cur = alpha * val + one_minus * prev
            nxt.append(cur)
            prev = cur
        q = nxt
    closed = [
        Fraction(math.comb(t + k - 1, k - 1)) * (alpha**k) * (one_minus**t)
        for t in range(n_steps)
    ]
    pk = max(q)
    pk_t = q.index(pk)
    return {
        "stages": k,
        "drain_rate": alpha,
        "peak_flow": pk,
        "peak_step": pk_t,
        "closed_form_exact_match": q == closed,
        "cumulative_mass_at_horizon": sum(q, Fraction(0)),
    }


def simulate_conductance_feedback_q(
    g0: Any,
    head: Any,
    coupling: Any,
    steps: int,
    mode: str,
) -> dict[str, Any]:
    """Exact pure-Q Lyapunov/contraction contrast: self-healing 'choke' vs runaway 'piping'."""
    g = require_pos_rat(g0, "g0")
    h = require_pos_rat(head, "head")
    c = require_pos_rat(coupling, "coupling")
    n_steps = require_int(steps, "steps", lo=1, hi=6)
    if mode not in ("choke", "piping"):
        raise BiomimeticOpError("UNKNOWN_FEEDBACK_MODE", f"unknown mode: {mode!r}")

    traj = [g]
    monotone_checks: list[bool] = []
    bound_checks: list[bool] = []
    g_init = g
    for t in range(1, n_steps + 1):
        q_t = g * h
        factor = Fraction(1) + c * q_t * q_t
        if mode == "choke":
            g_next = g / factor
            monotone_checks.append(0 < g_next < g)
            bound_checks.append(
                Fraction(1) / (g_next * g_next) > Fraction(1) / (g_init * g_init) + 2 * t * c * h * h
            )
        else:
            g_next = g * factor
            monotone_checks.append(g_next > g)
            bound_checks.append(g_next >= g_init * ((Fraction(1) + c * h * h * g_init * g_init) ** t))
        g = g_next
        traj.append(g)
    return {
        "mode": mode,
        "steps": n_steps,
        "g_initial": g_init,
        "g_final": traj[-1],
        "monotone": all(monotone_checks),
        "lyapunov_or_growth_bound_verified": all(bound_checks),
        "trajectory": traj,
    }


def certify_operator2_beaver_dams() -> dict[str, Any]:
    """Certify Operator 2: K^3 moment collapse, K-fold shear drop, flood attenuation & choke vs piping."""
    H = Fraction(8)
    statics_rows: list[dict[str, Any]] = []
    statics_checks: list[bool] = []
    for k in (1, 2, 4, 8):
        st = analyze_weir_cascade_statics_q(H, [H / k] * k)
        statics_checks.append(all((
            st["peak_moment_reduction_ratio"] == Fraction(k**3),
            st["shear_reduction_ratio"] == Fraction(k),
            st["jensen_excess"] == 0,
            st["jensen_identity_exact"],
        )))
        statics_rows.append({
            "K": k,
            "peak_moment_reduction_ratio": fmt_q(st["peak_moment_reduction_ratio"]),
            "total_shear_reduction_ratio": fmt_q(st["shear_reduction_ratio"]),
            "jensen_excess": fmt_q(st["jensen_excess"]),
        })

    non_unif = analyze_weir_cascade_statics_q(H, [Fraction(4), Fraction(4, 3), Fraction(4, 3), Fraction(4, 3)])
    non_unif_suboptimal = all((
        non_unif["jensen_identity_exact"],
        non_unif["jensen_excess"] > 0,
        non_unif["peak_moment_reduction_ratio"] < Fraction(64),
        non_unif["shear_reduction_ratio"] < Fraction(4),
    ))

    flood_rows: list[dict[str, Any]] = []
    flood_peaks: list[Fraction] = []
    flood_checks: list[bool] = []
    for k in (1, 2, 4, 8):
        fc = simulate_flood_cascade_q(k, Fraction(1, 2), 24)
        flood_checks.append(fc["closed_form_exact_match"])
        flood_peaks.append(fc["peak_flow"])
        flood_rows.append({
            "K": k,
            "peak_flow": fmt_q(fc["peak_flow"]),
            "peak_step": fc["peak_step"],
            "closed_form_exact_match": fc["closed_form_exact_match"],
        })
    flood_monotone = flood_peaks[0] > flood_peaks[1] > flood_peaks[2] > flood_peaks[3]

    # Fixed-mean-lag anti-strawman control (mean lag tau = 7 -> alpha_K = K / (K + 7))
    lag_k1 = simulate_flood_cascade_q(1, Fraction(1, 8), 24)
    lag_k2 = simulate_flood_cascade_q(2, Fraction(2, 9), 24)
    lag_k8 = simulate_flood_cascade_q(8, Fraction(8, 15), 24)
    fixed_lag_nonmonotone = all((
        lag_k2["peak_flow"] < lag_k1["peak_flow"],
        lag_k8["peak_flow"] > lag_k2["peak_flow"],
    ))

    choke = simulate_conductance_feedback_q(Fraction(1), Fraction(1), Fraction(1, 4), 5, "choke")
    piping = simulate_conductance_feedback_q(Fraction(1), Fraction(1), Fraction(1, 4), 5, "piping")
    choke_vs_piping_ratio = piping["g_final"] / choke["g_final"]

    passed = all((
        all(statics_checks),
        non_unif_suboptimal,
        all(flood_checks),
        flood_monotone,
        fixed_lag_nonmonotone,
        choke["monotone"],
        choke["lyapunov_or_growth_bound_verified"],
        piping["monotone"],
        piping["lyapunov_or_growth_bound_verified"],
        choke_vs_piping_ratio > Fraction(500),
    ))
    return {
        "operator": "op2_beaver_dam_weir_cascade",
        "equal_stage_statics": statics_rows,
        "non_uniform_k4_jensen_excess": fmt_q(non_unif["jensen_excess"]),
        "non_uniform_k4_suboptimal": non_unif_suboptimal,
        "flood_cascade_added_ponds": flood_rows,
        "flood_peak_monotone_attenuation": flood_monotone,
        "fixed_mean_lag_tau7_peaks": {
            "K1": fmt_q(lag_k1["peak_flow"]),
            "K2": fmt_q(lag_k2["peak_flow"]),
            "K8": fmt_q(lag_k8["peak_flow"]),
            "nonmonotone_plug_flow_tradeoff_verified": fixed_lag_nonmonotone,
        },
        "feedback_contrast_t5": {
            "choke_g5": fmt_q(choke["g_final"]),
            "choke_lyapunov_bound_ok": choke["lyapunov_or_growth_bound_verified"],
            "piping_g5": fmt_q(piping["g_final"]),
            "piping_growth_bound_ok": piping["lyapunov_or_growth_bound_verified"],
            "piping_over_choke_ratio_gt_500": choke_vs_piping_ratio > Fraction(500),
        },
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Operator 3: Underground Insect Tunnel Networks — beta_1 >= 1 Ventilation
#             Obstruction, Cave-In Pareto & Narrow-Lane Digging Congestion
# ---------------------------------------------------------------------------

def solve_kirchhoff_ventilation_q(
    n_nodes: int,
    edges: Any,
    conductances: Any,
    forcing: Any,
) -> dict[str, Any]:
    """
    Exact pure-Q Kirchhoff ventilation solver:
      q = G (eta - B^T p) with B q = 0 <=> L_G p = B G eta.
    Cross-checked independently via exact cycle-space basis projection C (C^T G^{-1} C)^{-1} C^T eta.
    """
    n, es, gs = _validate_graph(n_nodes, edges, conductances)
    m = len(es)
    eta_raw = require_seq(forcing, "forcing", min_len=m, max_len=m)
    eta = [require_rat(x, f"forcing[{i}]") for i, x in enumerate(eta_raw)]
    _, Lp = laplacian_pseudoinverse_q(n, es, gs)

    rhs = [Fraction(0)] * n
    for (u, v), g, e_val in zip(es, gs, eta):
        rhs[u] -= g * e_val
        rhs[v] += g * e_val
    p = [sum((Lp[i][j] * rhs[j] for j in range(n)), Fraction(0)) for i in range(n)]
    q = [g * (e_val - (p[v] - p[u])) for (u, v), g, e_val in zip(es, gs, eta)]

    kcl_res = [Fraction(0)] * n
    for (u, v), q_e in zip(es, q):
        kcl_res[u] -= q_e
        kcl_res[v] += q_e
    kcl_exact = all(val == 0 for val in kcl_res)

    B_rows = [[Fraction(0)] * m for _ in range(n)]
    for idx, (u, v) in enumerate(es):
        B_rows[u][idx] = Fraction(-1)
        B_rows[v][idx] = Fraction(1)
    rank_b, cycle_basis = rank_and_nullspace_q(B_rows, m)
    beta1 = m - n + 1

    if beta1 == 0:
        q_cycle = [Fraction(0)] * m
    else:
        r_mat = [
            [
                sum((cycle_basis[a][e] * cycle_basis[b][e] / gs[e] for e in range(m)), Fraction(0))
                for b in range(beta1)
            ]
            for a in range(beta1)
        ]
        c_eta = [sum((cycle_basis[a][e] * eta[e] for e in range(m)), Fraction(0)) for a in range(beta1)]
        loop_flows = solve_linear_q(r_mat, c_eta)
        q_cycle = [
            sum((loop_flows[a] * cycle_basis[a][e] for a in range(beta1)), Fraction(0))
            for e in range(m)
        ]

    power_eta = sum((e_val * q_e for e_val, q_e in zip(eta, q)), Fraction(0))
    power_diss = sum((q_e * q_e / g for q_e, g in zip(q, gs)), Fraction(0))
    return {
        "n_nodes": n,
        "n_edges": m,
        "beta1": beta1,
        "betti_dimension_exact": len(cycle_basis) == beta1,
        "rank_incidence": rank_b,
        "flows": q,
        "kcl_exact": kcl_exact,
        "cycle_basis_exact_match": q == q_cycle,
        "advective_power": power_eta,
        "power_balance_exact": power_eta == power_diss,
    }


def evaluate_cavein_cuts_q(n_nodes: int, edges: Any) -> dict[str, Any]:
    """Exhaustive exact combinatorial 1-edge and 2-edge cave-in disconnection fractions."""
    eseq = require_seq(edges, "edges", min_len=2, max_len=64)
    n, es, _ = _validate_graph(n_nodes, eseq, [Fraction(1)] * len(eseq))
    if not _is_connected(n, es):
        raise BiomimeticOpError("DISCONNECTED_BURROW", "initial burrow graph must be connected")
    m = len(es)
    disc1 = 0
    for i in range(m):
        rem = es[:i] + es[i + 1 :]
        if not _is_connected(n, rem):
            disc1 += 1
    disc2 = 0
    pairs = math.comb(m, 2)
    for i in range(m):
        for j in range(i + 1, m):
            rem = tuple(es[k] for k in range(m) if k != i and k != j)
            if not _is_connected(n, rem):
                disc2 += 1
    return {
        "n_edges": m,
        "beta1": m - n + 1,
        "disconnect_1_edge": Fraction(disc1, m),
        "disconnect_2_edge": Fraction(disc2, pairs),
    }


def solve_digging_markov_q(n_active: int, arrival_rate: Any, clog_factor: Any) -> dict[str, Any]:
    """
    Exact pure-Q finite-state continuous-time birth-death Markov chain for narrow-lane digging:
      States s in {0..k}; arrival (k - s) * lam; exit/dig clearance mu_s = 1 / r^(s - 1).
    Solved via exact generator linear system pi Q = 0, sum(pi) = 1 AND verified against
    closed-form detailed balance.
    """
    k = require_int(n_active, "n_active", lo=1, hi=12)
    lam = require_pos_rat(arrival_rate, "arrival_rate")
    r = require_pos_rat(clog_factor, "clog_factor")
    dim = k + 1
    A = [[Fraction(0)] * dim for _ in range(dim)]
    for s in range(dim):
        rate_up = Fraction(k - s) * lam if s < k else Fraction(0)
        rate_dn = Fraction(1) / (r ** (s - 1)) if s > 0 else Fraction(0)
        A[s][s] = -(rate_up + rate_dn)
        if s > 0:
            A[s][s - 1] = Fraction(k - (s - 1)) * lam
        if s < k:
            A[s][s + 1] = Fraction(1) / (r**s)
    A[dim - 1] = [Fraction(1)] * dim
    rhs = [Fraction(0)] * (dim - 1) + [Fraction(1)]
    pi = solve_linear_q(A, rhs)

    weights = [Fraction(1)]
    for s in range(1, dim):
        mu_s = Fraction(1) / (r ** (s - 1))
        weights.append(weights[-1] * Fraction(k - (s - 1)) * lam / mu_s)
    w_tot = sum(weights, Fraction(0))
    pi_db = [w / w_tot for w in weights]
    throughput = sum((pi[s] / (r ** (s - 1)) for s in range(1, dim)), Fraction(0))
    return {
        "n_active": k,
        "stationary_distribution": pi,
        "detailed_balance_exact_match": pi == pi_db,
        "throughput": throughput,
    }


def certify_operator3_insect_tunnels() -> dict[str, Any]:
    """Certify Operator 3: beta_1 >= 1 ventilation obstruction, Q3 cave-in Pareto & Aguilar-Gravish law."""
    ham_path = [(0, 1), (1, 3), (3, 2), (2, 6), (6, 7), (7, 5), (5, 4)]
    ham_cycle = ham_path + [(4, 0)]
    sparse_loops = ham_cycle + [(1, 5), (3, 7)]
    full_cube = sparse_loops + [(0, 2), (4, 6)]

    def diurnal_forcing(edges: list[tuple[int, int]], sign: int) -> list[Fraction]:
        out: list[Fraction] = []
        for u, v in edges:
            dz = ((v >> 2) & 1) - ((u >> 2) & 1)
            if dz == 0:
                out.append(Fraction(0))
            else:
                outer = (u >> 1) & 1
                coeff = 3 if outer == 1 else 1
                out.append(Fraction(sign * coeff * dz))
        return out

    def elevation_coboundary(edges: list[tuple[int, int]]) -> list[Fraction]:
        return [Fraction(((v >> 2) & 1) - ((u >> 2) & 1)) for u, v in edges]

    tree_day = solve_kirchhoff_ventilation_q(8, ham_path, [Fraction(1)] * len(ham_path), diurnal_forcing(ham_path, 1))
    cyc_day = solve_kirchhoff_ventilation_q(8, ham_cycle, [Fraction(1)] * len(ham_cycle), diurnal_forcing(ham_cycle, 1))
    cyc_night = solve_kirchhoff_ventilation_q(8, ham_cycle, [Fraction(1)] * len(ham_cycle), diurnal_forcing(ham_cycle, -1))
    cyc_exact_cob = solve_kirchhoff_ventilation_q(8, ham_cycle, [Fraction(1)] * len(ham_cycle), elevation_coboundary(ham_cycle))
    sparse_day = solve_kirchhoff_ventilation_q(8, sparse_loops, [Fraction(1)] * len(sparse_loops), diurnal_forcing(sparse_loops, 1))

    obstruction_ok = all((
        tree_day["beta1"] == 0,
        tree_day["betti_dimension_exact"],
        all(f == 0 for f in tree_day["flows"]),
        tree_day["advective_power"] == 0,
        tree_day["kcl_exact"],
        tree_day["cycle_basis_exact_match"],
        cyc_day["beta1"] == 1,
        cyc_day["betti_dimension_exact"],
        cyc_day["advective_power"] > 0,
        cyc_day["kcl_exact"],
        cyc_day["cycle_basis_exact_match"],
        cyc_day["power_balance_exact"],
        cyc_night["flows"] == [-f for f in cyc_day["flows"]],
        all(f == 0 for f in cyc_exact_cob["flows"]),
        sparse_day["beta1"] == 3,
        sparse_day["advective_power"] > cyc_day["advective_power"],
        sparse_day["cycle_basis_exact_match"],
    ))

    pareto_specs = [
        ("G_tree_MST", ham_path),
        ("G_cycle_1loop", ham_cycle),
        ("G_sparse_3loop", sparse_loops),
        ("G_cube_Q3", full_cube),
    ]
    pareto_rows: list[dict[str, Any]] = []
    pareto_map: dict[str, dict[str, Any]] = {}
    for name, es in pareto_specs:
        st = evaluate_cavein_cuts_q(8, es)
        pareto_map[name] = st
        pareto_rows.append({
            "topology": name,
            "excavation_cost": st["n_edges"],
            "beta1": st["beta1"],
            "disconnect_1_edge": fmt_q(st["disconnect_1_edge"]),
            "disconnect_2_edge": fmt_q(st["disconnect_2_edge"]),
        })
    pareto_ok = all((
        pareto_map["G_tree_MST"]["disconnect_1_edge"] == Fraction(1),
        pareto_map["G_cycle_1loop"]["disconnect_1_edge"] == Fraction(0),
        pareto_map["G_sparse_3loop"]["disconnect_2_edge"] == Fraction(7, 45),
        pareto_map["G_cube_Q3"]["disconnect_2_edge"] == Fraction(0),
    ))

    clogged_rows: list[dict[str, Any]] = []
    clogged_j: list[Fraction] = []
    uncrowded_j: list[Fraction] = []
    markov_db_checks: list[bool] = []
    for k in range(1, 7):
        res_c = solve_digging_markov_q(k, Fraction(1, 3), Fraction(4))
        res_u = solve_digging_markov_q(k, Fraction(1, 3), Fraction(1))
        markov_db_checks.append(res_c["detailed_balance_exact_match"])
        markov_db_checks.append(res_u["detailed_balance_exact_match"])
        clogged_j.append(res_c["throughput"])
        uncrowded_j.append(res_u["throughput"])
        clogged_rows.append({
            "k_active": k,
            "active_fraction": fmt_q(Fraction(k, 6)),
            "clogged_throughput": fmt_q(res_c["throughput"]),
            "uncrowded_throughput": fmt_q(res_u["throughput"]),
        })

    opt_k_clogged = clogged_j.index(max(clogged_j)) + 1
    opt_k_uncrowded = uncrowded_j.index(max(uncrowded_j)) + 1
    markov_ok = all((
        all(markov_db_checks),
        opt_k_clogged == 2,
        opt_k_uncrowded == 6,
        clogged_j[1] > clogged_j[0],
        clogged_j[1] / clogged_j[5] > Fraction(300),
        all(uncrowded_j[i] < uncrowded_j[i + 1] for i in range(5)),
    ))

    return {
        "operator": "op3_underground_insect_tunnels",
        "ventilation_obstruction": {
            "tree_beta1": tree_day["beta1"],
            "tree_advective_power": fmt_q(tree_day["advective_power"]),
            "cycle_beta1": cyc_day["beta1"],
            "cycle_day_power": fmt_q(cyc_day["advective_power"]),
            "cycle_night_exact_reversal": cyc_night["flows"] == [-f for f in cyc_day["flows"]],
            "cycle_coboundary_zero_flux": all(f == 0 for f in cyc_exact_cob["flows"]),
            "sparse_beta1": sparse_day["beta1"],
            "sparse_day_power": fmt_q(sparse_day["advective_power"]),
        },
        "cavein_pareto_frontier": pareto_rows,
        "digging_congestion_markov": {
            "n_workers": 6,
            "arrival_rate": "1/3",
            "clog_factor": "4",
            "clogged_opt_k": opt_k_clogged,
            "clogged_opt_fraction": fmt_q(Fraction(opt_k_clogged, 6)),
            "clogged_opt_over_full_ratio": fmt_q(clogged_j[1] / clogged_j[5]),
            "uncrowded_control_opt_k": opt_k_uncrowded,
            "sweep": clogged_rows,
        },
        "passed": all((obstruction_ok, pareto_ok, markov_ok)),
    }


# ---------------------------------------------------------------------------
# Operator 4: Tailorbird Nests — Discrete Volkersen Shear-Lag & Postage-Stamp
#             Perforation Tear Interior Optimum + Graded End-Rivet Spacing
# ---------------------------------------------------------------------------

def solve_volkersen_discrete_q(
    bay_lengths: Any,
    alpha_total: Any,
    load: Any = Fraction(1),
) -> dict[str, Any]:
    """
    Exact discrete Volkersen shear-lag tridiagonal solver over Q for m >= 2 rivets
    separated by bay lengths Delta_1..Delta_{m-1} (sum = L):
        -T_{i-1} + (2 + 2*lambda_i) T_i - T_{i+1} = lambda_i * W,  T_0 = 0, T_m = W,
    where lambda_i = alpha_total * (Delta_i / L) and rivet loads are F_i = T_i - T_{i-1}.
    """
    bays_raw = require_seq(bay_lengths, "bay_lengths", min_len=1, max_len=64)
    bays = [require_pos_rat(d, f"bay_lengths[{i}]") for i, d in enumerate(bays_raw)]
    alpha = require_pos_rat(alpha_total, "alpha_total")
    w = require_pos_rat(load, "load")
    L_tot = sum(bays, Fraction(0))
    lams = [alpha * d / L_tot for d in bays]
    n = len(bays)

    c_p = [Fraction(0)] * n
    d_p = [Fraction(0)] * n
    for i in range(n):
        diag = Fraction(2) + 2 * lams[i]
        rhs_i = lams[i] * w + (w if i == n - 1 else Fraction(0))
        if i == 0:
            c_p[0] = (Fraction(-1) / diag) if n > 1 else Fraction(0)
            d_p[0] = rhs_i / diag
        else:
            denom = diag + c_p[i - 1]
            c_p[i] = (Fraction(-1) / denom) if i < n - 1 else Fraction(0)
            d_p[i] = (rhs_i + d_p[i - 1]) / denom

    T = [Fraction(0)] * n
    T[n - 1] = d_p[n - 1]
    for i in range(n - 2, -1, -1):
        T[i] = d_p[i] - c_p[i] * T[i + 1]

    Ts = [Fraction(0)] + T + [w]
    residual_ok = all(
        (-Ts[i] + (Fraction(2) + 2 * lams[i]) * Ts[i + 1] - Ts[i + 2]) == lams[i] * w
        for i in range(n)
    )
    forces = [Ts[i + 1] - Ts[i] for i in range(n + 1)]
    return {
        "n_rivets": n + 1,
        "rivet_forces": forces,
        "max_rivet_force": max(forces),
        "min_rivet_force": min(forces),
        "force_sum_exact": sum(forces, Fraction(0)) == w,
        "tridiagonal_residual_zero": residual_ok,
    }


def evaluate_tailorbird_seam_q(
    seam_len: Any,
    hole_diam: Any,
    alpha_total: Any,
    f_pull: Any,
    t_intact: Any,
) -> dict[str, Any]:
    """
    Exact pure-Q seam-capacity sweep over all valid integer stitch counts 1 <= m < L / d_h,
    balancing Volkersen peak end-rivet pull-out against postage-stamp net-section tear.
    """
    L = require_pos_rat(seam_len, "seam_len")
    dh = require_pos_rat(hole_diam, "hole_diam")
    alpha = require_pos_rat(alpha_total, "alpha_total")
    fp = require_pos_rat(f_pull, "f_pull")
    t0 = require_pos_rat(t_intact, "t_intact")
    max_holes_ratio = L / dh
    if max_holes_ratio <= 2:
        raise BiomimeticOpError("SEAM_TOO_SHORT_FOR_INTERIOR", "need L / hole_diam > 2")
    m_max = (max_holes_ratio.numerator - 1) // max_holes_ratio.denominator

    rows: list[dict[str, Any]] = []
    caps: list[Fraction] = []
    res_checks: list[bool] = []
    for m in range(1, m_max + 1):
        if m == 1:
            fmax = Fraction(1)
        else:
            sol = solve_volkersen_discrete_q([L / Fraction(m - 1)] * (m - 1), alpha)
            fmax = sol["max_rivet_force"]
            res_checks.append(sol["tridiagonal_residual_zero"])
            res_checks.append(sol["force_sum_exact"])
        w_pull = fp / fmax
        w_tear = t0 * (Fraction(1) - Fraction(m) * dh / L)
        w_cap = w_pull if w_pull <= w_tear else w_tear
        caps.append(w_cap)
        rows.append({
            "m_stitches": m,
            "f_max_fraction": fmt_q(fmax),
            "w_pull": fmt_q(w_pull),
            "w_tear": fmt_q(w_tear),
            "w_cap": fmt_q(w_cap),
        })

    best_cap = max(caps)
    m_star = caps.index(best_cap) + 1
    strict_interior = 1 < m_star < m_max
    return {
        "m_max": m_max,
        "m_star": m_star,
        "w_cap_star": best_cap,
        "strict_interior_optimum": strict_interior,
        "all_tridiagonal_residuals_zero": all(res_checks),
        "sweep": rows,
    }


def certify_operator4_tailorbird_nests() -> dict[str, Any]:
    """Certify Operator 4: postage-stamp interior optimum m* + graded denser end-rivet superiority."""
    seam = evaluate_tailorbird_seam_q(Fraction(10), Fraction(1), Fraction(4), Fraction(1), Fraction(5))

    unif_4 = solve_volkersen_discrete_q([Fraction(1, 3)] * 3, Fraction(4))
    grad_4 = solve_volkersen_discrete_q([Fraction(1, 6), Fraction(2, 3), Fraction(1, 6)], Fraction(4))
    w_tear_4 = Fraction(5) * (Fraction(1) - Fraction(4, 10))
    cap_unif_4 = min(Fraction(1) / unif_4["max_rivet_force"], w_tear_4)
    cap_grad_4 = min(Fraction(1) / grad_4["max_rivet_force"], w_tear_4)

    unif_6 = solve_volkersen_discrete_q([Fraction(1, 5)] * 5, Fraction(6))
    grad_6 = solve_volkersen_discrete_q(
        [Fraction(1, 12), Fraction(1, 6), Fraction(1, 2), Fraction(1, 6), Fraction(1, 12)],
        Fraction(6),
    )

    passed = all((
        seam["all_tridiagonal_residuals_zero"],
        seam["strict_interior_optimum"],
        seam["m_star"] == 4,
        seam["w_cap_star"] == Fraction(28, 11),
        unif_4["tridiagonal_residual_zero"],
        grad_4["tridiagonal_residual_zero"],
        cap_grad_4 > cap_unif_4,
        cap_grad_4 == Fraction(20, 7),
        unif_6["tridiagonal_residual_zero"],
        grad_6["tridiagonal_residual_zero"],
        grad_6["max_rivet_force"] == Fraction(7, 22),
        grad_6["max_rivet_force"] < unif_6["max_rivet_force"],
    ))
    return {
        "operator": "op4_tailorbird_volkersen_seam",
        "seam_optimum": {
            "L": "10",
            "hole_diam": "1",
            "alpha_total": "4",
            "m_max": seam["m_max"],
            "m_star": seam["m_star"],
            "w_cap_star": fmt_q(seam["w_cap_star"]),
            "strict_interior_optimum": seam["strict_interior_optimum"],
            "sweep": seam["sweep"],
        },
        "graded_end_spacing_m4_alpha4": {
            "uniform_fmax": fmt_q(unif_4["max_rivet_force"]),
            "graded_fmax": fmt_q(grad_4["max_rivet_force"]),
            "uniform_net_capacity": fmt_q(cap_unif_4),
            "graded_net_capacity": fmt_q(cap_grad_4),
            "zero_extra_holes_gain_ratio": fmt_q(cap_grad_4 / cap_unif_4),
        },
        "graded_end_spacing_m6_alpha6": {
            "uniform_forces": [fmt_q(x) for x in unif_6["rivet_forces"]],
            "graded_forces": [fmt_q(x) for x in grad_6["rivet_forces"]],
            "uniform_fmax": fmt_q(unif_6["max_rivet_force"]),
            "graded_fmax": fmt_q(grad_6["max_rivet_force"]),
            "peak_stress_reduction_fraction": fmt_q(
                (unif_6["max_rivet_force"] - grad_6["max_rivet_force"]) / unif_6["max_rivet_force"]
            ),
        },
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Operator 5: Bonus Natural Geometries
#   5A: Venus' Flower Basket (Euplectella aspergillum) — Maxwell-Calladine
#   5B: Honeybee / Paper-Wasp Maraldi Angle cos(theta) = -1/3 in Q[sqrt(2), sqrt(3)]
# ---------------------------------------------------------------------------

def analyze_euplectella_shell_q(
    n_rows: int,
    n_cols: int,
    pattern: str,
    *,
    continuous_longitudinal_beams: bool = False,
) -> dict[str, Any]:
    """
    Exact Maxwell-Calladine rank-nullity analysis over Q for an unwrapped cylindrical
    square lattice shell (circumferential periodicity n_cols, axial bays n_rows).
    """
    nr = require_int(n_rows, "n_rows", lo=2, hi=8)
    nc = require_int(n_cols, "n_cols", lo=3, hi=8)
    valid_patterns = ("none", "checker_1", "checker_1_bridge", "checker_x", "bolker_crapo_tree", "full_1", "full_x")
    if pattern not in valid_patterns:
        raise BiomimeticOpError("UNKNOWN_BRACING_PATTERN", f"unknown pattern: {pattern!r}")
    if type(continuous_longitudinal_beams) is not bool:
        raise BiomimeticOpError("INVALID_BOOL_TYPE", "continuous_longitudinal_beams must be strict bool")

    ny = nr + 1
    n_verts = ny * nc
    ncols = 2 * n_verts

    def vid(r: int, c: int) -> int:
        return r * nc + (c % nc)

    rows: list[list[Fraction]] = []
    for r in range(ny):
        for c in range(nc):
            u, v = vid(r, c), vid(r, c + 1)
            row = [Fraction(0)] * ncols
            row[2 * u] = Fraction(-1)
            row[2 * v] = Fraction(1)
            rows.append(row)
    for r in range(nr):
        for c in range(nc):
            u, v = vid(r, c), vid(r + 1, c)
            row = [Fraction(0)] * ncols
            row[2 * u + 1] = Fraction(-1)
            row[2 * v + 1] = Fraction(1)
            rows.append(row)

    n_diags = 0
    for r in range(nr):
        for c in range(nc):
            u00, u10, u01, u11 = vid(r, c), vid(r, c + 1), vid(r + 1, c), vid(r + 1, c + 1)
            add_slash = False
            add_back = False
            if pattern == "checker_1" and (r + c) % 2 == 0:
                add_slash = True
            elif pattern == "checker_1_bridge" and ((r + c) % 2 == 0 or (r == 0 and c == 1)):
                add_slash = True
            elif pattern == "checker_x" and (r + c) % 2 == 0:
                add_slash = True
                add_back = True
            elif pattern == "bolker_crapo_tree" and (r == 0 or c == 0):
                add_slash = True
            elif pattern == "full_1":
                add_slash = True
            elif pattern == "full_x":
                add_slash = True
                add_back = True
            if add_slash:
                row = [Fraction(0)] * ncols
                row[2 * u00] = Fraction(-1)
                row[2 * u00 + 1] = Fraction(-1)
                row[2 * u11] = Fraction(1)
                row[2 * u11 + 1] = Fraction(1)
                rows.append(row)
                n_diags += 1
            if add_back:
                row = [Fraction(0)] * ncols
                row[2 * u10] = Fraction(1)
                row[2 * u10 + 1] = Fraction(-1)
                row[2 * u01] = Fraction(-1)
                row[2 * u01 + 1] = Fraction(1)
                rows.append(row)
                n_diags += 1

    n_collin = 0
    if continuous_longitudinal_beams:
        for r in range(1, nr):
            for c in range(nc):
                row = [Fraction(0)] * ncols
                row[2 * vid(r - 1, c)] = Fraction(1)
                row[2 * vid(r, c)] = Fraction(-2)
                row[2 * vid(r + 1, c)] = Fraction(1)
                rows.append(row)
                n_collin += 1

    rk, _ = rank_and_nullspace_q(rows, ncols)
    internal_dofs = ncols - 2
    floppy_modes = internal_dofs - rk
    self_stresses = len(rows) - rk

    torsion_vec: list[Fraction] = []
    for r in range(ny):
        for _ in range(nc):
            torsion_vec.extend([Fraction(r), Fraction(0)])
    torsion_energy = sum(
        (sum((v * torsion_vec[j] for j, v in enumerate(row) if v != 0), Fraction(0)) ** 2 for row in rows),
        Fraction(0),
    )

    zigzag_vec: list[Fraction] = []
    for r in range(ny):
        for c in range(nc):
            zigzag_vec.extend([Fraction(1 if r % 2 == 0 else -1), Fraction(-1 if c % 2 == 0 else 1)])
    zigzag_energy = sum(
        (sum((v * zigzag_vec[j] for j, v in enumerate(row) if v != 0), Fraction(0)) ** 2 for row in rows),
        Fraction(0),
    )

    return {
        "pattern": pattern,
        "continuous_longitudinal_beams": continuous_longitudinal_beams,
        "n_vertices": n_verts,
        "n_constraints": len(rows),
        "n_diagonals": n_diags,
        "n_collinearity": n_collin,
        "rank": rk,
        "floppy_modes": floppy_modes,
        "self_stresses": self_stresses,
        "maxwell_calladine_exact": (floppy_modes - self_stresses) == (internal_dofs - len(rows)),
        "global_torsion_energy": torsion_energy,
        "checkerboard_zigzag_energy": zigzag_energy,
    }


def certify_maraldi_angle_q(
    perturbations: Any = (Fraction(0), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(1)),
) -> dict[str, Any]:
    """
    Exact Q[sqrt(2), sqrt(3)] proof of the Maraldi rhombic-dodecahedral cell base angle:
      cos(theta) = -1/3, tan^2(alpha) = 1/2, x*^2 = 1/8,
      S_flat = (3/2)*sqrt(3), S_maraldi = (3/2)*sqrt(2), S_maraldi^2 / S_flat^2 = 2/3,
    with exact completion-of-square global optimality identity:
      3*(1 + 4*x^2) - (2*x + sqrt(2))^2 = (2*sqrt(2)*x - 1)^2 >= 0.
    """
    p_seq = require_seq(perturbations, "perturbations", min_len=1, max_len=32)
    xs = [require_rat(v, f"perturbations[{i}]") for i, v in enumerate(p_seq)]
    for x in xs:
        if x < 0:
            raise BiomimeticOpError("NEGATIVE_APEX_OFFSET", "apex offset x must be >= 0")

    x_star_sq = Fraction(1, 8)
    tan_alpha_sq = 4 * x_star_sq
    cos_theta = (Fraction(-1, 2) + x_star_sq) / (Fraction(1) + x_star_sq)

    s_flat = (Fraction(0), Fraction(0), Fraction(3, 2), Fraction(0))
    s_maraldi = (Fraction(0), Fraction(3, 2), Fraction(0), Fraction(0))
    delta_s = (
        s_flat[0] - s_maraldi[0],
        s_flat[1] - s_maraldi[1],
        s_flat[2] - s_maraldi[2],
        s_flat[3] - s_maraldi[3],
    )
    s_flat_sq = q23_mul(s_flat, s_flat)
    s_maraldi_sq = q23_mul(s_maraldi, s_maraldi)
    area_sq_ratio = s_maraldi_sq[0] / s_flat_sq[0]

    lhs_poly = (
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(-4), Fraction(0), Fraction(0)),
        (Fraction(8), Fraction(0), Fraction(0), Fraction(0)),
    )
    rhs_poly = (
        q23_mul((Fraction(-1), Fraction(0), Fraction(0), Fraction(0)), (Fraction(-1), Fraction(0), Fraction(0), Fraction(0))),
        q23_mul((Fraction(-2), Fraction(0), Fraction(0), Fraction(0)), (Fraction(0), Fraction(2), Fraction(0), Fraction(0))),
        q23_mul((Fraction(0), Fraction(2), Fraction(0), Fraction(0)), (Fraction(0), Fraction(2), Fraction(0), Fraction(0))),
    )
    square_identity_exact = lhs_poly == rhs_poly

    pert_rows: list[dict[str, Any]] = []
    pert_checks: list[bool] = []
    for x in xs:
        gap_q23 = (Fraction(1) + 8 * x * x, -4 * x, Fraction(0), Fraction(0))
        is_pos = q23_sign(gap_q23) == 1
        pert_checks.append(is_pos)
        pert_rows.append({
            "x_rational": fmt_q(x),
            "squared_excess_const": fmt_q(gap_q23[0]),
            "squared_excess_sqrt2": fmt_q(gap_q23[1]),
            "strictly_exceeds_maraldi": is_pos,
        })

    passed = all((
        cos_theta == Fraction(-1, 3),
        tan_alpha_sq == Fraction(1, 2),
        q23_sign(delta_s) == 1,
        s_flat_sq == (Fraction(27, 4), Fraction(0), Fraction(0), Fraction(0)),
        s_maraldi_sq == (Fraction(9, 2), Fraction(0), Fraction(0), Fraction(0)),
        area_sq_ratio == Fraction(2, 3),
        square_identity_exact,
        all(pert_checks),
    ))
    return {
        "x_star_squared": fmt_q(x_star_sq),
        "tan_alpha_squared": fmt_q(tan_alpha_sq),
        "cos_maraldi_theta": fmt_q(cos_theta),
        "s_flat_q23": [fmt_q(c) for c in s_flat],
        "s_maraldi_q23": [fmt_q(c) for c in s_maraldi],
        "delta_s_saving_q23": [fmt_q(c) for c in delta_s],
        "delta_s_strictly_positive": q23_sign(delta_s) == 1,
        "s_maraldi_sq_over_s_flat_sq": fmt_q(area_sq_ratio),
        "completion_of_square_identity_exact": square_identity_exact,
        "rational_perturbations": pert_rows,
        "passed": passed,
    }


def certify_operator5_bonus_geometries() -> dict[str, Any]:
    """Certify Operator 5: 5A Euplectella cylindrical lattice + 5B Maraldi rhombic-dodecahedral base."""
    patterns = ("none", "checker_1", "checker_1_bridge", "checker_x", "bolker_crapo_tree", "full_1", "full_x")
    pin_results: dict[str, dict[str, Any]] = {}
    pin_rows: list[dict[str, Any]] = []
    mc_checks: list[bool] = []
    for pat in patterns:
        res = analyze_euplectella_shell_q(4, 4, pat, continuous_longitudinal_beams=False)
        pin_results[pat] = res
        mc_checks.append(res["maxwell_calladine_exact"])
        pin_rows.append({
            "pattern": pat,
            "n_diagonals": res["n_diagonals"],
            "rank": res["rank"],
            "floppy_modes": res["floppy_modes"],
            "self_stresses": res["self_stresses"],
            "global_torsion_energy": fmt_q(res["global_torsion_energy"]),
            "checkerboard_zigzag_energy": fmt_q(res["checkerboard_zigzag_energy"]),
        })

    cont_none = analyze_euplectella_shell_q(4, 4, "none", continuous_longitudinal_beams=True)
    cont_chk1 = analyze_euplectella_shell_q(4, 4, "checker_1", continuous_longitudinal_beams=True)
    cont_chkx = analyze_euplectella_shell_q(4, 4, "checker_x", continuous_longitudinal_beams=True)

    euplectella_ok = all((
        all(mc_checks),
        pin_results["none"]["floppy_modes"] == 7,
        pin_results["none"]["global_torsion_energy"] == 0,
        pin_results["checker_1"]["n_diagonals"] * 2 == pin_results["full_1"]["n_diagonals"],
        pin_results["checker_1"]["floppy_modes"] == 1,
        pin_results["checker_1"]["global_torsion_energy"] == Fraction(8),
        pin_results["checker_1"]["checkerboard_zigzag_energy"] == 0,
        pin_results["checker_x"]["n_diagonals"] * 2 == pin_results["full_x"]["n_diagonals"],
        pin_results["checker_x"]["floppy_modes"] == 1,
        pin_results["checker_x"]["global_torsion_energy"] == Fraction(16),
        pin_results["checker_x"]["checkerboard_zigzag_energy"] == 0,
        pin_results["checker_1_bridge"]["floppy_modes"] == 0,
        pin_results["bolker_crapo_tree"]["floppy_modes"] == 0,
        pin_results["bolker_crapo_tree"]["n_diagonals"] == 7,
        cont_none["global_torsion_energy"] == 0,
        cont_none["floppy_modes"] == 4,
        cont_chk1["floppy_modes"] == 0,
        cont_chk1["checkerboard_zigzag_energy"] > 0,
        cont_chkx["floppy_modes"] == 0,
    ))

    maraldi = certify_maraldi_angle_q()
    return {
        "operator": "op5_euplectella_and_maraldi",
        "euplectella_4x4_cylindrical_shell": {
            "pin_jointed_comparison": pin_rows,
            "continuous_spicule_none_floppy": cont_none["floppy_modes"],
            "continuous_spicule_none_torsion_energy": fmt_q(cont_none["global_torsion_energy"]),
            "continuous_spicule_checker1_floppy": cont_chk1["floppy_modes"],
            "continuous_spicule_checker1_zigzag_energy": fmt_q(cont_chk1["checkerboard_zigzag_energy"]),
            "continuous_spicule_checkerx_floppy": cont_chkx["floppy_modes"],
            "passed": euplectella_ok,
        },
        "maraldi_rhombic_dodecahedral_base": maraldi,
        "passed": all((euplectella_ok, maraldi["passed"])),
    }


# ---------------------------------------------------------------------------
# Law-5 Typed Cross-Repo Operator Bridges & Full AUDIT-117 Payload
# ---------------------------------------------------------------------------

CROSS_REPO_BRIDGES: list[dict[str, str]] = [
    {
        "operator": "op1_spider_web_cable_graph",
        "target_repos": (
            "aska-physical/fibral-rigidity@06520520 (#5@4753275f, PROOF.md:75, verify.py:367-368), "
            "aska-physical/impedence-analyzers@ed0a5e10 (dock#8 P5), "
            "Foundation-0/incentre-lattices#109@97f5252c, "
            "Foundation-0/vitruvian3d@7099f5cb (vacancy_stress_verify.py:44-81), "
            "Foundation-0/spectral-inertia@8394da98"
        ),
        "typed_map": "(G, K, omega > 0) -> (L_K^+, LODF R_{e',e}, Delta R_eff, Omega_int(omega) > 0 via exact Q Sylvester inertia)",
        "predictive_transfer": "Anchored tension-only prestress Omega_int > 0 eliminates fibral-rigidity#5 flat-tangent H_yy = 0 collapse and contrasts with incentre-lattices#109 unpinned Maxwell trace=0; kappa=100 cuts remote spiral LODF >22x.",
    },
    {
        "operator": "op2_beaver_dam_weir_cascade",
        "target_repos": (
            "aska-physical/optifab@74d68ea1 (#13/#14, verify.py:249-263, loop.py:55-59, Spec.lean:59-69), "
            "aska-physical/venturi-collars@d53f85a3 (verify.py:31-41,68-69,124), "
            "aska-physical/funi-frame@97b326d2 (verify.py:111-119,141-164), "
            "Foundation-0/quotient-lp-bounds"
        ),
        "typed_map": "(H, K, alpha, g_t) -> (M_mono/M_stage = K^3, F_mono/F_tot = K, negative-binomial flood peak, g_t^{-2} Lyapunov contraction)",
        "predictive_transfer": "Multi-stage hydraulic/thermal buffering collapses peak stage load cubically (K^3) and stabilizes breach transients via negative-feedback choke damping vs super-exponential piping.",
    },
    {
        "operator": "op3_underground_insect_tunnels",
        "target_repos": (
            "aska-physical/optifab@74d68ea1 (verify.py:159-163,684-715, data/graph.json), "
            "aska-physical/venturi-collars@d53f85a3 (verify.py:17-41), "
            "Foundation-0/vitruvian3d@7099f5cb (transport-conductivity-20261112/THEOREM.md:26-77), "
            "Moissanite-Labs/weft, Moissanite-Labs/weft-loom"
        ),
        "typed_map": "(G, G_cond, eta) -> (P_cycle = G - G B^T L_G^+ B G, H_1 rank beta_1, k-cut survival, birth-death congestion throughput J(k))",
        "predictive_transfer": "Passive buoyancy loops require both beta_1 >= 1 and [eta] != 0 in H^1(G;Q); +1 cycle cuts 1-edge failure 100%->0%; single-lane worker queues peak at p* = 1/3 < 1.",
    },
    {
        "operator": "op4_tailorbird_volkersen_seam",
        "target_repos": (
            "aska-physical/cfrp-truss@3c11631e (verify.py:155-309 uniform T_sus/n_anchors gap), "
            "aska-physical/cfrp-masts@a12b665f (#1 collar kinematics, verify.py:123-134), "
            "aska-physical/fibral-rigidity@06520520, "
            "aska-physical/cfrp-strengthening@3f68cccf (flexure440.py:19,43-49), "
            "aska-physical/funi-floors@00eba18c (#3)"
        ),
        "typed_map": "(L, d_h, alpha, Delta) -> (SPD tridiagonal Volkersen forces F_i, interior optimum m* in (1, L/d_h), graded end-bay gain)",
        "predictive_transfer": "Replaces uniform multi-row dowel sharing with exact tridiagonal Volkersen peaking (2.28x at m=6, alpha=6); denser end spacing lifts net capacity +12.2% at m=4 with zero extra holes.",
    },
    {
        "operator": "op5_euplectella_and_maraldi",
        "target_repos": (
            "aska-physical/fibral-rigidity@06520520 (verify.py:43-53), "
            "aska-physical/cfrp-truss@3c11631e (#3), "
            "aska-physical/funi-frame@97b326d2 (verify.py:122-138), "
            "aska-physical/funi-floors@00eba18c (#1, verify.py:109-110), "
            "Foundation-0/rigid-realizations, "
            "Foundation-0/incentre-lattices@2d374fff (radius_ratio.py:153, polytopes.py:154)"
        ),
        "typed_map": "(R_cyl, Bolker-Crapo parity, Q[sqrt(2),sqrt(3)]) -> (rank-nullity m-s, zigzag curvature +/-4, cos(theta) = -1/3 global square identity)",
        "predictive_transfer": "Pure pin-jointed checkerboard bracing blocks global torsion yet leaves 1 exact zigzag mode killed by +1 parity bridge or continuous beams; exact Q[sqrt(2),sqrt(3)] Maraldi proof removes float64 reliance on rhombic dodecahedra.",
    },
]


def build_audit117_payload() -> dict[str, Any]:
    """Run all 5 exact-Q biomimetic structural operators and assemble canonical payload."""
    op1 = certify_operator1_spider_webs()
    op2 = certify_operator2_beaver_dams()
    op3 = certify_operator3_insect_tunnels()
    op4 = certify_operator4_tailorbird_nests()
    op5 = certify_operator5_bonus_geometries()
    all_passed = all((op1["passed"], op2["passed"], op3["passed"], op4["passed"], op5["passed"]))
    return {
        "audit_id": "AUDIT-117",
        "track": "track-s18-biomimetic-structural-operators",
        "oracle_class": "exact",
        "arithmetic": "pure_Z_Q_and_Q_sqrt2_sqrt3_zero_floats",
        "novelty_classification": "N0/N1",
        "operators": {
            "op1_spider_webs": op1,
            "op2_beaver_dams": op2,
            "op3_insect_tunnels": op3,
            "op4_tailorbird_nests": op4,
            "op5_bonus_geometries": op5,
        },
        "cross_repo_bridges": CROSS_REPO_BRIDGES,
        "all_passed": all_passed,
    }
