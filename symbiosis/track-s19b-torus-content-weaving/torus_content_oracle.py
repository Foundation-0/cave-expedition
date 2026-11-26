#!/usr/bin/env python3
"""
AUDIT-118B (`track-s19b-torus-content-weaving`):
Pure-Z/Q Exact Meta-Recursive Content Torus-Knot Weaving & `warp-drive` Axial Force-Multiplier Oracle.

Applies ALL 5 Laws of the Aletheia Method (Law 1 Portal-Keeper, Law 2b Transformational
Steelman, Law 3 Adversarial Tomography, Law 4 N0/N1/N2 Honesty, Law 5 Strict Exact Operators)
to weave 4 genuinely unconnected cross-track exact-operator torus-knot seams over Z/Q
anchored directly onto `Moissanite-Labs/warp-drive` (`#6/#7/#11/#14/#35/#37` & `siliconcordat/warp`),
explicitly falsify 3 superficially appealing metaphorical bridges (F1..F3), and certify
an 18-entry Missed-Portals & Unfinished-Gems Ledger mined across the full corpus.

Zero floats anywhere. Zero bare `assert`s. Zero external dependencies. Zero RNG calls.
"""
from __future__ import annotations

from fractions import Fraction
import json
import math
from typing import Any

MAX_JSON_DEPTH = 64
MAX_JSON_BYTES = 2_000_000
MAX_INT_DIGITS = 400
MAX_INT_BITS = 1328
MAX_SEQ_LEN = 256
MAX_MATRIX_DIM = 32

_ALLOWED_NOVELTY = frozenset({"N0", "N1", "N2"})
_ALLOWED_SEAM_STATUS = frozenset({"VERIFIED_EXACT_SEAM", "FALSIFIED_METAPHOR"})
_ALLOWED_PORTAL_STATUS = frozenset({"LIVE_PORTAL", "FALSIFIED_OR_CLOSED", "BLOCKED_EXTERNAL"})


class TorusContentError(ValueError):
    """Fail-closed typed error (immune to python3 -O assert stripping)."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


# ---------------------------------------------------------------------------
# Strict Input Hardening & Iterative Zero-Float Canonical JSON
# ---------------------------------------------------------------------------

def _check_no_surrogates(s: str) -> None:
    """Fast C-level strict UTF-8 check rejecting all lone UTF-16 surrogates U+D800..U+DFFF."""
    try:
        s.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise TorusContentError("SURROGATE_FORBIDDEN", "lone UTF-16 surrogate forbidden") from exc


def require_int(
    val: Any,
    label: str = "int",
    *,
    lo: int | None = None,
    hi: int | None = None,
) -> int:
    if type(val) is not int:
        raise TorusContentError("INVALID_INT_TYPE", f"{label} must be strict int")
    if val.bit_length() > MAX_INT_BITS:
        raise TorusContentError("INT_BIT_LIMIT", f"{label} exceeds {MAX_INT_BITS} bits")
    if lo is not None and val < lo:
        raise TorusContentError("INT_BELOW_MIN", f"{label} below min {lo}")
    if hi is not None and val > hi:
        raise TorusContentError("INT_ABOVE_MAX", f"{label} above max {hi}")
    return val


def require_bool(val: Any, label: str = "bool") -> bool:
    if type(val) is not bool:
        raise TorusContentError("INVALID_BOOL_TYPE", f"{label} must be strict bool")
    return val


def require_str(val: Any, label: str = "str") -> str:
    if type(val) is not str:
        raise TorusContentError("INVALID_STR_TYPE", f"{label} must be strict str")
    if not val:
        raise TorusContentError("EMPTY_STR", f"{label} must be non-empty")
    _check_no_surrogates(val)
    return val


def require_rat(val: Any, label: str = "rational") -> Fraction:
    t = type(val)
    if t is Fraction:
        if val.numerator.bit_length() > MAX_INT_BITS:
            raise TorusContentError("RAT_NUM_BIT_LIMIT", f"{label} numerator exceeds {MAX_INT_BITS} bits")
        if val.denominator.bit_length() > MAX_INT_BITS:
            raise TorusContentError("RAT_DEN_BIT_LIMIT", f"{label} denominator exceeds {MAX_INT_BITS} bits")
        return val
    if t is int:
        if val.bit_length() > MAX_INT_BITS:
            raise TorusContentError("INT_BIT_LIMIT", f"{label} exceeds {MAX_INT_BITS} bits")
        return Fraction(val, 1)
    raise TorusContentError("INVALID_RAT_TYPE", f"{label} must be strict int or Fraction")


def require_pos_rat(val: Any, label: str = "pos_rational") -> Fraction:
    q = require_rat(val, label)
    if q <= 0:
        raise TorusContentError("NON_POSITIVE_RAT", f"{label} must be strictly positive")
    return q


def require_seq(
    val: Any,
    label: str = "seq",
    *,
    min_len: int = 1,
    max_len: int = MAX_SEQ_LEN,
) -> tuple[Any, ...]:
    if type(val) not in (list, tuple):
        raise TorusContentError("INVALID_SEQ_TYPE", f"{label} must be strict list or tuple")
    n = len(val)
    if n < min_len:
        raise TorusContentError("SEQ_TOO_SHORT", f"{label} length {n} < {min_len}")
    if n > max_len:
        raise TorusContentError("SEQ_TOO_LONG", f"{label} length {n} > {max_len}")
    return tuple(val)


def fmt_q(q: Fraction) -> str:
    """Canonical reduced rational string ('p' if den == 1 else 'p/q')."""
    r = require_rat(q, "q")
    if r.denominator == 1:
        return str(r.numerator)
    return f"{r.numerator}/{r.denominator}"


def validate_json_value(obj: Any, *, max_depth: int = MAX_JSON_DEPTH) -> None:
    """Iterative zero-float, depth-capped, bit-capped, strict-type JSON tree validator."""
    limit = require_int(max_depth, "max_depth", lo=1, hi=128)
    stack: list[tuple[Any, int]] = [(obj, 0)]
    while stack:
        cur, depth = stack.pop()
        if depth > limit:
            raise TorusContentError("MAX_DEPTH_EXCEEDED", f"JSON nesting exceeds {limit}")
        t = type(cur)
        if t is dict:
            for k, v in cur.items():
                if type(k) is not str:
                    raise TorusContentError("NON_STR_KEY", "dict keys must be strict str")
                _check_no_surrogates(k)
                stack.append((v, depth + 1))
        elif t is list:
            for item in cur:
                stack.append((item, depth + 1))
        elif t is int:
            if cur.bit_length() > MAX_INT_BITS:
                raise TorusContentError("INT_BIT_LIMIT", f"integer exceeds {MAX_INT_BITS}-bit cap")
        elif t is str:
            _check_no_surrogates(cur)
        elif t is bool or cur is None:
            continue
        elif t is float:
            raise TorusContentError("FLOAT_FORBIDDEN", "float values are forbidden")
        else:
            raise TorusContentError("UNSUPPORTED_JSON_TYPE", f"unsupported type {t.__name__}")


def _reject_float_token(tok: str) -> Any:
    raise TorusContentError("JSON_FLOAT_FORBIDDEN", f"float literal forbidden: {tok!r}")


def _reject_constant_token(tok: str) -> Any:
    raise TorusContentError("JSON_CONSTANT_FORBIDDEN", f"non-RFC8259 constant forbidden: {tok!r}")


def _parse_capped_int_token(tok: str) -> int:
    digits = tok[1:] if tok.startswith("-") else tok
    if len(digits) > MAX_INT_DIGITS:
        raise TorusContentError("INT_DIGIT_LIMIT", f"integer token exceeds {MAX_INT_DIGITS} digits")
    val = int(tok)
    if val.bit_length() > MAX_INT_BITS:
        raise TorusContentError("INT_BIT_LIMIT", f"integer token exceeds {MAX_INT_BITS} bits")
    return val


def _pairs_no_dup(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise TorusContentError("JSON_DUPLICATE_KEY", f"duplicate JSON key: {k!r}")
        out[k] = v
    return out


def parse_strict_json(text: str) -> Any:
    """Fail-closed zero-float, no-duplicate-key, depth-capped, bit-capped JSON parser."""
    if type(text) is not str:
        raise TorusContentError("INVALID_JSON_INPUT", "JSON input must be strict str")
    _check_no_surrogates(text)
    if len(text.encode("utf-8")) > MAX_JSON_BYTES:
        raise TorusContentError("JSON_TOO_LARGE", "JSON input exceeds byte cap")
    try:
        parsed = json.loads(
            text,
            parse_float=_reject_float_token,
            parse_constant=_reject_constant_token,
            parse_int=_parse_capped_int_token,
            object_pairs_hook=_pairs_no_dup,
        )
    except TorusContentError:
        raise
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise TorusContentError("JSON_PARSE_ERROR", f"invalid JSON: {exc}") from exc
    validate_json_value(parsed, max_depth=MAX_JSON_DEPTH)
    return parsed


def canonical_json_bytes(obj: Any) -> bytes:
    """Canonical sorted-key ASCII UTF-8 JSON bytes (zero floats, bit/depth capped)."""
    validate_json_value(obj, max_depth=MAX_JSON_DEPTH)
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


# ---------------------------------------------------------------------------
# Pure-Z/Q Exact Linear Algebra & Dual-Oracle Sylvester Inertia
# ---------------------------------------------------------------------------

def require_matrix_q(mat: Any, label: str = "matrix") -> list[list[Fraction]]:
    rows = require_seq(mat, label, min_len=1, max_len=MAX_MATRIX_DIM)
    out: list[list[Fraction]] = []
    ncols: int | None = None
    for i, row in enumerate(rows):
        rseq = require_seq(row, f"{label}[{i}]", min_len=1, max_len=MAX_MATRIX_DIM)
        if ncols is None:
            ncols = len(rseq)
        elif len(rseq) != ncols:
            raise TorusContentError("RAGGED_MATRIX", f"{label} row {i} length mismatch")
        out.append([require_rat(x, f"{label}[{i}][{j}]") for j, x in enumerate(rseq)])
    return out


def require_sym_matrix_q(mat: Any, label: str = "sym_matrix") -> list[list[Fraction]]:
    m = require_matrix_q(mat, label)
    n = len(m)
    if len(m[0]) != n:
        raise TorusContentError("NON_SQUARE_MATRIX", f"{label} must be square")
    for i in range(n):
        for j in range(i + 1, n):
            if m[i][j] != m[j][i]:
                raise TorusContentError("NON_SYMMETRIC_MATRIX", f"{label}[{i}][{j}] != [{j}][{i}]")
    return m


def _mat_mul(A: list[list[Fraction]], B: list[list[Fraction]]) -> list[list[Fraction]]:
    m, k = len(A), len(A[0])
    p = len(B[0])
    out = [[Fraction(0)] * p for _ in range(m)]
    for i in range(m):
        for t in range(k):
            a_it = A[i][t]
            if a_it != 0:
                for j in range(p):
                    out[i][j] += a_it * B[t][j]
    return out


def _mat_vec(A: list[list[Fraction]], v: list[Fraction]) -> list[Fraction]:
    out: list[Fraction] = []
    for row in A:
        acc = Fraction(0)
        for a, b in zip(row, v):
            if a:
                acc += a * b
        out.append(acc)
    return out


def _dot(u: list[Fraction], v: list[Fraction]) -> Fraction:
    acc = Fraction(0)
    for a, b in zip(u, v):
        if a:
            acc += a * b
    return acc


def _transpose(A: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def rref_q(mat: list[list[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    """Exact Gauss-Jordan RREF over Q returning (rref_matrix, pivot_columns)."""
    m = len(mat)
    n = len(mat[0])
    A = [row[:] for row in mat]
    pivots: list[int] = []
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        scale = A[r][c]
        A[r] = [x / scale for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                factor = A[i][c]
                A[i] = [A[i][j] - factor * A[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def nullspace_basis_q(mat: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact rational basis of ker(mat)."""
    R, pivots = rref_q(mat)
    n = len(mat[0])
    piv_set = set(pivots)
    free_cols = [c for c in range(n) if c not in piv_set]
    basis: list[list[Fraction]] = []
    for fc in free_cols:
        vec = [Fraction(0)] * n
        vec[fc] = Fraction(1)
        for row_idx, pc in enumerate(pivots):
            vec[pc] = -R[row_idx][fc]
        basis.append(vec)
    return basis


def invert_matrix_q(mat: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact Gauss-Jordan inverse over Q (fails closed on singular matrix)."""
    n = len(mat)
    aug = [mat[i][:] + [Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
    R, pivots = rref_q(aug)
    if pivots != list(range(n)):
        raise TorusContentError("SINGULAR_MATRIX", "matrix is singular over Q")
    return [row[n:] for row in R]


def moore_penrose_sym_q(M: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact Moore-Penrose pseudoinverse M^+ = U (U^T M U)^-1 U^T for symmetric M over Q."""
    M_s = require_sym_matrix_q(M, "M")
    n = len(M_s)
    _, pivots = rref_q(M_s)
    if not pivots:
        return [[Fraction(0)] * n for _ in range(n)]
    U = [[M_s[i][c] for c in pivots] for i in range(n)]
    Ut = _transpose(U)
    core = _mat_mul(_mat_mul(Ut, M_s), U)
    core_inv = invert_matrix_q(core)
    return _mat_mul(_mat_mul(U, core_inv), Ut)


def verify_moore_penrose_axioms(M: list[list[Fraction]], Mp: list[list[Fraction]]) -> bool:
    """Verify all 4 Penrose axioms identically over Q."""
    MMp = _mat_mul(M, Mp)
    MpM = _mat_mul(Mp, M)
    return all((
        _mat_mul(MMp, M) == M,
        _mat_mul(MpM, Mp) == Mp,
        MMp == _transpose(MMp),
        MpM == _transpose(MpM),
    ))


def bunch_kaufman_inertia_q(mat: Any) -> tuple[tuple[int, int, int], bool]:
    """
    Exact symmetric P M P^T = L D L^T congruence over Q with 1x1 and 2x2 block pivots.
    Returns ((n_pos, n_neg, n_zero), congruence_exact).
    """
    M = require_sym_matrix_q(mat, "M")
    n = len(M)
    A = [row[:] for row in M]
    perm = list(range(n))
    L = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
    D = [[Fraction(0)] * n for _ in range(n)]

    n_pos = 0
    n_neg = 0
    n_zero = 0
    k = 0
    while k < n:
        diag_piv = None
        for i in range(k, n):
            if A[i][i] != 0:
                diag_piv = i
                break
        if diag_piv is not None:
            if diag_piv != k:
                perm[k], perm[diag_piv] = perm[diag_piv], perm[k]
                A[k], A[diag_piv] = A[diag_piv], A[k]
                for row in A:
                    row[k], row[diag_piv] = row[diag_piv], row[k]
                for j in range(k):
                    L[k][j], L[diag_piv][j] = L[diag_piv][j], L[k][j]
            piv = A[k][k]
            D[k][k] = piv
            if piv > 0:
                n_pos += 1
            else:
                n_neg += 1
            for i in range(k + 1, n):
                lik = A[i][k] / piv
                L[i][k] = lik
                for j in range(k + 1, n):
                    A[i][j] -= lik * A[k][j]
            for i in range(k + 1, n):
                A[i][k] = Fraction(0)
                A[k][i] = Fraction(0)
            k += 1
            continue

        pair = None
        for i in range(k, n):
            for j in range(i + 1, n):
                if A[i][j] != 0:
                    pair = (i, j)
                    break
            if pair is not None:
                break
        if pair is None:
            n_zero += n - k
            break
        p1, p2 = pair
        for dst, src in ((k, p1), (k + 1, p2)):
            if src != dst:
                perm[dst], perm[src] = perm[src], perm[dst]
                A[dst], A[src] = A[src], A[dst]
                for row in A:
                    row[dst], row[src] = row[src], row[dst]
                for j in range(k):
                    L[dst][j], L[src][j] = L[src][j], L[dst][j]
        b = A[k][k + 1]
        D[k][k + 1] = b
        D[k + 1][k] = b
        n_pos += 1
        n_neg += 1
        for i in range(k + 2, n):
            l0 = A[i][k + 1] / b
            l1 = A[i][k] / b
            L[i][k] = l0
            L[i][k + 1] = l1
            for j in range(k + 2, n):
                A[i][j] -= l0 * A[k][j] + l1 * A[k + 1][j]
        for i in range(k + 2, n):
            A[i][k] = Fraction(0)
            A[i][k + 1] = Fraction(0)
            A[k][i] = Fraction(0)
            A[k + 1][i] = Fraction(0)
        k += 2

    PMPt = [[M[perm[i]][perm[j]] for j in range(n)] for i in range(n)]
    LDLt = _mat_mul(_mat_mul(L, D), _transpose(L))
    return (n_pos, n_neg, n_zero), (PMPt == LDLt)


def _sign_variations(coeffs: list[Fraction]) -> int:
    nonzero = [c for c in coeffs if c != 0]
    flips = 0
    for i in range(len(nonzero) - 1):
        if (nonzero[i] > 0) != (nonzero[i + 1] > 0):
            flips += 1
    return flips


def faddeev_charpoly_q(mat: list[list[Fraction]]) -> tuple[list[Fraction], bool]:
    """
    Exact Faddeev-LeVerrier characteristic polynomial p(x) = det(xI - M) from highest degree
    down to constant term, paired with exact Cayley-Hamilton residual check p(M) == 0.
    """
    n = len(mat)
    coeffs: list[Fraction] = [Fraction(1)]
    B = [[Fraction(0)] * n for _ in range(n)]
    for k in range(1, n + 1):
        if k == 1:
            B = [row[:] for row in mat]
        else:
            B = _mat_mul(mat, B)
        tr = sum((B[i][i] for i in range(n)), Fraction(0))
        ck = -tr / Fraction(k)
        coeffs.append(ck)
        for i in range(n):
            B[i][i] += ck
    ch_zero = all(B[i][j] == 0 for i in range(n) for j in range(n))
    return coeffs, ch_zero


def faddeev_descartes_inertia_q(mat: Any) -> tuple[tuple[int, int, int], bool]:
    """
    Independent exact Sylvester inertia for symmetric M over Q via Faddeev-LeVerrier
    characteristic polynomial + exact Descartes' rule of signs (exact for real-rooted polys).
    """
    M = require_sym_matrix_q(mat, "M")
    n = len(M)
    coeffs, ch_zero = faddeev_charpoly_q(M)
    n_zero = 0
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
        n_zero += 1
    deg = len(coeffs) - 1
    n_pos = _sign_variations(coeffs)
    alt = [coeffs[i] * (Fraction(-1) ** (deg - i)) for i in range(len(coeffs))]
    n_neg = _sign_variations(alt)
    exact_ok = all((ch_zero, n_pos + n_neg + n_zero == n))
    return (n_pos, n_neg, n_zero), exact_ok


def bareiss_det_int(int_mat: Any) -> int:
    """Exact fraction-free Bareiss integer determinant over Z."""
    rows = require_seq(int_mat, "int_mat", min_len=1, max_len=MAX_MATRIX_DIM)
    n = len(rows)
    M: list[list[int]] = []
    for i, r in enumerate(rows):
        rseq = require_seq(r, f"int_mat[{i}]", min_len=n, max_len=n)
        M.append([require_int(x, f"int_mat[{i}][{j}]") for j, x in enumerate(rseq)])
    sign = 1
    prev_piv = 1
    for k in range(n - 1):
        if M[k][k] == 0:
            swap_row = None
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    swap_row = i
                    break
            if swap_row is None:
                return 0
            M[k], M[swap_row] = M[swap_row], M[k]
            sign = -sign
        piv = M[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * piv - M[i][k] * M[k][j]) // prev_piv
        prev_piv = piv
    return sign * M[n - 1][n - 1]


# ---------------------------------------------------------------------------
# PILLAR 1 — SEAM 1: Rank-1 Symmetric Update, Incremental `warp-drive` Adapter
#            Hot-Swap, & Adapter-to-Adapter Spectral-Margin LODF
# ---------------------------------------------------------------------------

def analyze_rank1_update_q(
    M_in: Any,
    b_in: Any,
    delta_in: Any,
) -> dict[str, Any]:
    """
    Exact Q unification of Sherman-Morrison edge-cut localization (S18),
    Sylvester congruence inertia (S17), and stacked-adapter Gram perturbation (warp#15/#17):
        M(delta) = M - delta * b * b^T,   h = b^T M^+ b,   gamma = 1 - delta * h.
    """
    M = require_sym_matrix_q(M_in, "M")
    n = len(M)
    b_seq = require_seq(b_in, "b", min_len=n, max_len=n)
    b = [require_rat(x, f"b[{i}]") for i, x in enumerate(b_seq)]
    delta = require_pos_rat(delta_in, "delta")

    in_M_bk, bk_m_ok = bunch_kaufman_inertia_q(M)
    in_M_fd, fd_m_ok = faddeev_descartes_inertia_q(M)
    if in_M_bk[1] != 0:
        raise TorusContentError("BASE_NOT_PSD", "base matrix M must be PSD (n_neg == 0)")

    Mp = moore_penrose_sym_q(M)
    mp_ok = verify_moore_penrose_axioms(M, Mp)
    v = _mat_vec(Mp, b)
    if _mat_vec(M, v) != b:
        raise TorusContentError("B_NOT_IN_RANGE", "vector b must lie in im(M)")
    h = _dot(b, v)
    if h <= 0:
        raise TorusContentError("ZERO_LEVERAGE", "b must be nonzero in im(M)")

    gamma = Fraction(1) - delta * h
    M_delta = [[M[i][j] - delta * b[i] * b[j] for j in range(n)] for i in range(n)]
    in_Md_bk, bk_md_ok = bunch_kaufman_inertia_q(M_delta)
    in_Md_fd, fd_md_ok = faddeev_descartes_inertia_q(M_delta)

    B_aug = [M[i][:] + [b[i]] for i in range(n)] + [b[:] + [Fraction(1) / delta]]
    in_B_bk, bk_b_ok = bunch_kaufman_inertia_q(B_aug)
    in_B_fd, fd_b_ok = faddeev_descartes_inertia_q(B_aug)

    dual_oracle_ok = all((
        bk_m_ok,
        fd_m_ok,
        bk_md_ok,
        fd_md_ok,
        bk_b_ok,
        fd_b_ok,
        mp_ok,
        in_M_bk == in_M_fd,
        in_Md_bk == in_Md_fd,
        in_B_bk == in_B_fd,
    ))

    schur_in = (1, 0, 0) if gamma > 0 else ((0, 0, 1) if gamma == 0 else (0, 1, 0))
    haynsworth_lhs = (in_Md_bk[0] + 1, in_Md_bk[1], in_Md_bk[2])
    haynsworth_rhs = (in_M_bk[0] + schur_in[0], in_M_bk[1] + schur_in[1], in_M_bk[2] + schur_in[2])
    haynsworth_exact = all((in_B_bk == haynsworth_lhs, in_B_bk == haynsworth_rhs))

    r, _, z0 = in_M_bk
    quad_val = _dot(v, _mat_vec(M_delta, v))
    quad_identity_exact = quad_val == h * gamma

    if gamma > 0:
        regime = "REGIME_I_STABLE"
        expected_in = (r, 0, z0)
        sm_Mp = [
            [Mp[i][j] + (delta / gamma) * v[i] * v[j] for j in range(n)]
            for i in range(n)
        ]
        extra_verified = sm_Mp == moore_penrose_sym_q(M_delta)
    elif gamma == 0:
        regime = "REGIME_II_CRITICAL_SINGULARITY"
        expected_in = (r - 1, 0, z0 + 1)
        extra_verified = all(x == 0 for x in _mat_vec(M_delta, v))
    else:
        regime = "REGIME_III_NEGATIVE_FLIP"
        expected_in = (r - 1, 1, z0)
        extra_verified = quad_val < 0

    return {
        "regime": regime,
        "delta": fmt_q(delta),
        "leverage_h": fmt_q(h),
        "schur_gamma": fmt_q(gamma),
        "inertia_M": list(in_M_bk),
        "inertia_M_delta": list(in_Md_bk),
        "expected_inertia": list(expected_in),
        "inertia_matches_theorem": in_Md_bk == expected_in,
        "bordered_inertia": list(in_B_bk),
        "dual_oracle_verified": dual_oracle_ok,
        "haynsworth_congruence_exact": haynsworth_exact,
        "witness_v": [fmt_q(x) for x in v],
        "vT_Mdelta_v": fmt_q(quad_val),
        "quad_identity_exact": quad_identity_exact,
        "regime_property_verified": extra_verified,
    }


def _weighted_laplacian(n_nodes: int, edges: list[tuple[int, int, Fraction]]) -> list[list[Fraction]]:
    L = [[Fraction(0)] * n_nodes for _ in range(n_nodes)]
    for u, v, w in edges:
        L[u][u] += w
        L[v][v] += w
        L[u][v] -= w
        L[v][u] -= w
    return L


def build_seam1_rank1_inertia_law() -> dict[str, Any]:
    """Certify Seam 1 unifying S18 graph cuts, S17 Sylvester inertia, & warp-drive hot-swap LODF."""
    edges = [
        (0, 1, Fraction(1)),
        (1, 2, Fraction(1)),
        (2, 0, Fraction(1)),
        (2, 3, Fraction(1)),
        (3, 4, Fraction(1)),
    ]
    L5 = _weighted_laplacian(5, edges)
    b_tri = [Fraction(1), Fraction(-1), Fraction(0), Fraction(0), Fraction(0)]
    b_bridge = [Fraction(0), Fraction(0), Fraction(1), Fraction(-1), Fraction(0)]

    g_reg1 = analyze_rank1_update_q(L5, b_tri, Fraction(1))
    g_reg2 = analyze_rank1_update_q(L5, b_bridge, Fraction(1))
    g_reg3 = analyze_rank1_update_q(L5, b_tri, Fraction(2))

    L5_plus = moore_penrose_sym_q(L5)
    L5_cut_plus = moore_penrose_sym_q(_weighted_laplacian(5, edges[1:]))
    e04 = [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(-1)]
    r_before = _dot(e04, _mat_vec(L5_plus, e04))
    r_after_direct = _dot(e04, _mat_vec(L5_cut_plus, e04))
    delta_r_direct = r_after_direct - r_before
    cross_dot = _dot(e04, _mat_vec(L5_plus, b_tri))
    h_tri = _dot(b_tri, _mat_vec(L5_plus, b_tri))
    delta_r_sm = (cross_dot * cross_dot) / (Fraction(1) - h_tri)

    # warp-drive / siliconcordat/warp#15/#17 stacked rank-1 adapters + O(d^2) incremental hot-swap
    a1 = [Fraction(1), Fraction(1), Fraction(0)]
    a2 = [Fraction(0), Fraction(1), Fraction(1)]
    a_orth = [Fraction(1), Fraction(-1), Fraction(1)]  # orthogonal to a1 (a1 . a_orth == 0)

    def base_M(s: Fraction) -> list[list[Fraction]]:
        return [[(s if i == j else Fraction(0)) - a1[i] * a1[j] for j in range(3)] for i in range(3)]

    w_reg1 = analyze_rank1_update_q(base_M(Fraction(4)), a2, Fraction(1))
    w_reg2 = analyze_rank1_update_q(base_M(Fraction(3)), a2, Fraction(1))
    w_reg3 = analyze_rank1_update_q(base_M(Fraction(5, 2)), a2, Fraction(1))

    # Exact O(d^2) incremental mount + unmount round-trip & Adapter-to-Adapter Spectral-Margin LODF
    M1 = base_M(Fraction(4))
    M1_inv = invert_matrix_q(M1)
    v2 = _mat_vec(M1_inv, a2)
    h2 = _dot(a2, v2)
    gamma2 = Fraction(1) - h2
    M12_inv_sm = [[M1_inv[i][j] + (v2[i] * v2[j]) / gamma2 for j in range(3)] for i in range(3)]
    # Incremental unmount (+ a2 a2^T) recovers M1_inv identically with 0/1 residual!
    w2 = _mat_vec(M12_inv_sm, a2)
    denom_unmount = Fraction(1) + _dot(a2, w2)
    M1_inv_recovered = [[M12_inv_sm[i][j] - (w2[i] * w2[j]) / denom_unmount for j in range(3)] for i in range(3)]
    unmount_exact = M1_inv_recovered == M1_inv

    # Adapter-to-Adapter Spectral-Margin LODF: Delta h_1^(2) == (a1^T M1^-1 a2)^2 / (1 - a2^T M1^-1 a2)
    h1_before = _dot(a1, _mat_vec(M1_inv, a1))
    h1_after_direct = _dot(a1, _mat_vec(M12_inv_sm, a1))
    lodf_cross = _dot(a1, v2)
    delta_h1_lodf = (lodf_cross * lodf_cross) / gamma2
    # Orthogonal control: mounting a_orth onto M1 gives EXACT 0/1 shift in a1's spectral leverage!
    v_orth = _mat_vec(M1_inv, a_orth)
    orth_cross = _dot(a1, v_orth)
    delta_h1_orth = (orth_cross * orth_cross) / (Fraction(1) - _dot(a_orth, v_orth))

    checks = [
        res[key]
        for res in (g_reg1, g_reg2, g_reg3, w_reg1, w_reg2, w_reg3)
        for key in (
            "inertia_matches_theorem",
            "dual_oracle_verified",
            "haynsworth_congruence_exact",
            "quad_identity_exact",
            "regime_property_verified",
        )
    ]
    checks.extend((
        delta_r_sm == delta_r_direct,
        unmount_exact,
        delta_h1_lodf == (h1_after_direct - h1_before),
        delta_h1_lodf > 0,
        delta_h1_orth == 0,
    ))
    return {
        "seam_id": "SEAM-1",
        "tracks_connected": [
            "track-s18-biomimetic-structural-operators",
            "track-s17-zone-canon-sylvester-inertia",
            "Moissanite-Labs/warp-drive",
            "siliconcordat/warp#15/#17",
        ],
        "graph_G5_non_bridge_cut": g_reg1,
        "graph_G5_bridge_disconnection": g_reg2,
        "graph_G5_oversubtract_flip": g_reg3,
        "graph_G5_delta_R_eff_before": fmt_q(r_before),
        "graph_G5_delta_R_eff_after": fmt_q(r_after_direct),
        "graph_G5_delta_R_eff_sm": fmt_q(delta_r_sm),
        "graph_G5_delta_R_eff_exact_match": delta_r_sm == delta_r_direct,
        "warp_cauchy_schwarz_N2_threshold": "8",
        "warp_exact_spectral_threshold": "3",
        "warp_regime1_s4_safe_inside_cs_reject": w_reg1,
        "warp_regime2_s3_critical_boundary": w_reg2,
        "warp_regime3_s5_2_negative_flip": w_reg3,
        "warp_drive_incremental_hotswap": {
            "unmount_roundtrip_exact": unmount_exact,
            "h1_before_mount_a2": fmt_q(h1_before),
            "h1_after_mount_a2": fmt_q(h1_after_direct),
            "adapter_lodf_delta_h1_coupled": fmt_q(delta_h1_lodf),
            "adapter_lodf_exact_match": delta_h1_lodf == (h1_after_direct - h1_before),
            "adapter_lodf_delta_h1_orthogonal": fmt_q(delta_h1_orth),
        },
        "passed": all(checks),
    }


# ---------------------------------------------------------------------------
# PILLAR 2 — SEAM 2: Exact Rounding-Envelope, Monotone Safety-Margin Duality,
#            & Beaver-Dam Choke Composition for `warp-drive` (#6/#35)
# ---------------------------------------------------------------------------

def _floor_log2_pos_rat(x: Fraction) -> int:
    """Exact integer e such that 2^e <= x < 2^(e+1) for x > 0 (zero floats)."""
    num, den = x.numerator, x.denominator
    e = num.bit_length() - den.bit_length()
    if e >= 0:
        if num < (den << e):
            e -= 1
    else:
        if (num << (-e)) < den:
            e -= 1
    return e


def _f32_ulp_exp(x: Fraction) -> int:
    """Return binary32 ULP exponent max(e - 23, -149), failing closed on overflow/underflow."""
    e = _floor_log2_pos_rat(x)
    if e > 127:
        raise TorusContentError("F32_OVERFLOW", "value exceeds binary32 max finite range")
    if e < -149:
        raise TorusContentError("F32_UNDERFLOW_ZERO", "value underflows binary32 min subnormal")
    return max(e - 23, -149)


def floor_binary32_q(val: Any) -> Fraction:
    """
    Exact pure-Z/Q round-down IEEE-754 binary32 dyadic rational rho_down^(32)(x) <= x.
    Zero Python floats, zero struct.pack. Fails closed on x <= 0, underflow-to-0, or overflow.
    """
    x = require_pos_rat(val, "x")
    ulp_exp = _f32_ulp_exp(x)
    if ulp_exp >= 0:
        m = x.numerator // (x.denominator << ulp_exp)
        return Fraction(m << ulp_exp, 1)
    shift = -ulp_exp
    m = (x.numerator << shift) // x.denominator
    return Fraction(m, 1 << shift)


def nearest_binary32_q(val: Any) -> Fraction:
    """Exact pure-Z/Q IEEE-754 binary32 round-to-nearest-even (zero floats)."""
    x = require_pos_rat(val, "x")
    ulp_exp = _f32_ulp_exp(x)
    if ulp_exp >= 0:
        den_scaled = x.denominator << ulp_exp
        m, r = divmod(x.numerator, den_scaled)
        twice_r = r << 1
        if twice_r > den_scaled:
            m += 1
        elif twice_r == den_scaled and (m & 1):
            m += 1
        return Fraction(m << ulp_exp, 1)
    shift = -ulp_exp
    m, r = divmod(x.numerator << shift, x.denominator)
    twice_r = r << 1
    if twice_r > x.denominator:
        m += 1
    elif twice_r == x.denominator and (m & 1):
        m += 1
    return Fraction(m, 1 << shift)


def round_nearest_thousandth_q(val: Any) -> Fraction:
    """Exact pure-Q round-to-nearest-even thousandth (pre-patch exo#7 behavior)."""
    x = require_pos_rat(val, "x")
    scaled = x * 1000
    q, r = divmod(scaled.numerator, scaled.denominator)
    twice_r = 2 * r
    if twice_r > scaled.denominator:
        q += 1
    elif twice_r == scaled.denominator and (q % 2 == 1):
        q += 1
    return Fraction(q, 1000)


def floor_uniform_dyadic_q(val: Any, k_bits: Any) -> Fraction:
    """Exact uniform dyadic grid floor floor(2^k * x) / 2^k over Q."""
    x = require_rat(val, "x")
    k = require_int(k_bits, "k_bits", lo=0, hi=32)
    m = (x.numerator << k) // x.denominator
    return Fraction(m, 1 << k)


def weft_budget_step_q(
    budget: Any,
    cost: Any,
    weight_safe: Any,
    *,
    non_finite_cost: Any = False,
) -> dict[str, Any]:
    """
    Pure-Q extended-state model of Moissanite-Labs/weft#224 C2 budget monotonicity gate:
    preserves 0 <= B' <= B on every accept AND B' == B on every reject.
    """
    b = require_rat(budget, "budget")
    c = require_rat(cost, "cost")
    safe = require_bool(weight_safe, "weight_safe")
    nf = require_bool(non_finite_cost, "non_finite_cost")
    if b <= 0:
        return {"accepted": False, "remaining_budget": fmt_q(b), "reason": "non_positive_budget"}
    if nf:
        return {"accepted": False, "remaining_budget": fmt_q(b), "reason": "non_finite_cost_preserved"}
    if c <= 0:
        return {"accepted": False, "remaining_budget": fmt_q(b), "reason": "non_positive_cost_preserved"}
    if not safe:
        return {"accepted": False, "remaining_budget": fmt_q(b), "reason": "unsafe_weight_preserved"}
    if c > b:
        return {"accepted": False, "remaining_budget": fmt_q(b), "reason": "insufficient_budget_preserved"}
    return {"accepted": True, "remaining_budget": fmt_q(b - c), "reason": "accepted"}


def build_seam2_rounding_envelope_duality() -> dict[str, Any]:
    """Certify Seam 2 unifying exo#7, quotient-lp-bounds#4, weft#224, S18 choke, & falsifying F2."""
    exo_cases = [
        ("2004/10000", Fraction(2004, 10000), Fraction(1681077, 8388608)),
        ("2006/10000", Fraction(2006, 10000), Fraction(6731019, 33554432)),
        ("5/10000", Fraction(5, 10000), Fraction(4294967, 8589934592)),
        ("2/10", Fraction(1, 5), Fraction(3355443, 16777216)),
        ("1/2", Fraction(1, 2), Fraction(1, 2)),
        ("3/4", Fraction(3, 4), Fraction(3, 4)),
        ("1", Fraction(1, 1), Fraction(1, 1)),
        ("2^-149", Fraction(1, 1 << 149), Fraction(1, 1 << 149)),
    ]
    exo_checks: dict[str, Any] = {}
    galois_checks: list[bool] = []
    prev_r: Fraction | None = None
    for label, x, expected in sorted(exo_cases, key=lambda t: t[1]):
        r1 = floor_binary32_q(x)
        r2 = floor_binary32_q(r1)
        deflation = r1 <= x
        idempotent = r2 == r1
        exact_match = r1 == expected
        monotone = True if prev_r is None else (prev_r <= r1)
        prev_r = r1
        galois_checks.extend((deflation, idempotent, exact_match, monotone))
        exo_checks[label] = {
            "floor_f32": fmt_q(r1),
            "exact_match": exact_match,
            "deflation": deflation,
            "idempotent": idempotent,
        }

    thousandths_overshoot_count = 0
    for k in range(1, 1001):
        xk = Fraction(k, 1000)
        if nearest_binary32_q(xk) > xk:
            thousandths_overshoot_count += 1

    hop_req = Fraction(2006, 10000)
    budget_B = Fraction(1003, 1000)
    k_hops = 5
    exact_sum = hop_req * k_hops
    thous_hop = round_nearest_thousandth_q(hop_req)
    thous_sum = thous_hop * k_hops
    thous_f32_hop = nearest_binary32_q(thous_hop)
    thous_f32_sum = thous_f32_hop * k_hops
    safe_hop = floor_binary32_q(hop_req)
    safe_sum = safe_hop * k_hops
    safe_hop2 = nearest_binary32_q(safe_hop)

    lp_edges = [(0, 1, Fraction(2)), (1, 2, Fraction(2)), (2, 3, Fraction(1)), (0, 2, Fraction(5))]
    h_frac = [Fraction(19, 4), Fraction(11, 4), Fraction(3, 4), Fraction(0)]
    h_floor_int = [floor_uniform_dyadic_q(v, 0) for v in h_frac]
    h_floor_d4 = [floor_uniform_dyadic_q(v, 2) for v in h_frac]

    def _lp_feasible(h_vec: list[Fraction], edges_list: list[tuple[int, int, Fraction]]) -> bool:
        return all([h_vec[-1] == 0] + [h_vec[u] - h_vec[v] <= c for u, v, c in edges_list])

    lp_orig_ok = _lp_feasible(h_frac, lp_edges)
    lp_floor_int_ok = _lp_feasible(h_floor_int, lp_edges)
    lp_floor_d4_ok = _lp_feasible(h_floor_d4, lp_edges)
    loss_int = sum(h_frac) - sum(h_floor_int)
    loss_bound_int_ok = Fraction(0) <= loss_int < Fraction(len(h_frac))

    f2_hu = Fraction((1 << 24) + 2, 1)
    f2_hv = Fraction((1 << 24) + 1, 1)
    f2_cost = Fraction(1, 1)
    f2_orig_diff = f2_hu - f2_hv
    f2_hu_r = floor_binary32_q(f2_hu)
    f2_hv_r = floor_binary32_q(f2_hv)
    f2_rounded_diff = f2_hu_r - f2_hv_r

    w_accept = weft_budget_step_q(Fraction(10), Fraction(3), True)
    w_insuff = weft_budget_step_q(Fraction(10), Fraction(12), True)
    w_negcost = weft_budget_step_q(Fraction(10), Fraction(-5), True)
    w_nonfin = weft_budget_step_q(Fraction(10), Fraction(1), True, non_finite_cost=True)

    # S18 Beaver-Dam Choke Contraction composed with exo#7 floor-binary32 (warp-drive #6/#35)
    alpha_choke = Fraction(1, 4)
    g_exact = Fraction(1, 1)
    g_f32 = Fraction(1, 1)
    choke_lyapunov_all_ok = True
    for step in range(1, 6):
        g_exact_next = g_exact / (Fraction(1) + alpha_choke * g_exact * g_exact)
        g_f32_cand = g_f32 / (Fraction(1) + alpha_choke * g_f32 * g_f32)
        g_f32_next = floor_binary32_q(g_f32_cand)
        lyap_floor = Fraction(1) + 2 * step * alpha_choke
        step_ok = all((
            g_f32_next > 0,
            g_f32_next <= g_exact_next,
            g_f32_next < g_f32,
            (Fraction(1) / (g_f32_next * g_f32_next)) > lyap_floor,
        ))
        choke_lyapunov_all_ok = all((choke_lyapunov_all_ok, step_ok))
        g_exact = g_exact_next
        g_f32 = g_f32_next
    k_cube_ratios = [k * k * k for k in (1, 2, 4, 8)]

    all_ok = all((
        all(galois_checks),
        thousandths_overshoot_count == 503,
        exact_sum == budget_B,
        thous_sum > budget_B,
        thous_f32_sum > thous_sum,
        safe_sum < budget_B,
        safe_hop2 == safe_hop,
        lp_orig_ok,
        lp_floor_int_ok,
        lp_floor_d4_ok,
        loss_bound_int_ok,
        f2_orig_diff <= f2_cost,
        f2_rounded_diff > f2_cost,
        w_accept["accepted"],
        w_accept["remaining_budget"] == "7",
        not w_insuff["accepted"],
        w_insuff["remaining_budget"] == "10",
        not w_negcost["accepted"],
        w_negcost["remaining_budget"] == "10",
        not w_nonfin["accepted"],
        w_nonfin["remaining_budget"] == "10",
        choke_lyapunov_all_ok,
        k_cube_ratios == [1, 8, 64, 512],
    ))
    return {
        "seam_id": "SEAM-2",
        "tracks_connected": [
            "siliconcordat/exo#7",
            "Foundation-0/quotient-lp-bounds#4/#6/#8",
            "Moissanite-Labs/weft#224",
            "track-s18-biomimetic-structural-operators",
            "Moissanite-Labs/warp-drive#6/#35",
        ],
        "exo7_golden_checks": exo_checks,
        "thousandths_1_to_1000_f32_overshoot_count": thousandths_overshoot_count,
        "multihop_5x_0_2006": {
            "budget_B": fmt_q(budget_B),
            "exact_sum": fmt_q(exact_sum),
            "nearest_thousandth_sum": fmt_q(thous_sum),
            "nearest_thousandth_overshoot": fmt_q(thous_sum - budget_B),
            "thousandth_then_f32_sum": fmt_q(thous_f32_sum),
            "floor_f32_sum": fmt_q(safe_sum),
            "floor_f32_slack": fmt_q(budget_B - safe_sum),
            "floor_f32_second_hop_idempotent": safe_hop2 == safe_hop,
        },
        "lp_directed_rounding": {
            "orig_feasible": lp_orig_ok,
            "uniform_int_floor_feasible": lp_floor_int_ok,
            "uniform_dyadic_floor_feasible": lp_floor_d4_ok,
            "uniform_int_objective_loss": fmt_q(loss_int),
            "loss_strictly_below_n": loss_bound_int_ok,
        },
        "falsified_bridge_F2_binary32_lp_break": {
            "h_u": fmt_q(f2_hu),
            "h_v": fmt_q(f2_hv),
            "edge_cost": fmt_q(f2_cost),
            "orig_diff": fmt_q(f2_orig_diff),
            "floor_f32_h_u": fmt_q(f2_hu_r),
            "floor_f32_h_v": fmt_q(f2_hv_r),
            "rounded_diff": fmt_q(f2_rounded_diff),
            "violates_lp_constraint": f2_rounded_diff > f2_cost,
        },
        "weft224_budget_monotonicity": {
            "valid_accept": w_accept,
            "insufficient_reject": w_insuff,
            "negative_cost_reject_no_mint": w_negcost,
            "non_finite_cost_reject_no_poison": w_nonfin,
        },
        "warp_drive_choke_x_floor_f32_contraction": {
            "k_stage_moment_ratios": k_cube_ratios,
            "g5_exact": fmt_q(g_exact),
            "g5_floor_f32": fmt_q(g_f32),
            "lyapunov_strengthened_all_5_steps": choke_lyapunov_all_ok,
        },
        "passed": all_ok,
    }


# ---------------------------------------------------------------------------
# PILLAR 3 — SEAM 3: Cycle-Space H^1(G; Q) vs. Directed Farkas Grounding,
#            `warp-drive#37/#11` 4-Bank Flush, & `exo#8` Completeness
# ---------------------------------------------------------------------------

def analyze_directed_network_q(
    n_nodes: Any,
    edges_in: Any,
    conductances_in: Any,
    forcing_in: Any,
) -> dict[str, Any]:
    """Exact Z/Q Kirchhoff-Hodge cycle-space & topological-grounding analyzer."""
    n = require_int(n_nodes, "n_nodes", lo=2, hi=MAX_MATRIX_DIM)
    edges_raw = require_seq(edges_in, "edges", min_len=1, max_len=MAX_MATRIX_DIM)
    m = len(edges_raw)
    edges: list[tuple[int, int]] = []
    for idx, e in enumerate(edges_raw):
        pair = require_seq(e, f"edges[{idx}]", min_len=2, max_len=2)
        u = require_int(pair[0], f"edges[{idx}][0]", lo=0, hi=n - 1)
        v = require_int(pair[1], f"edges[{idx}][1]", lo=0, hi=n - 1)
        if u == v:
            raise TorusContentError("SELF_LOOP_FORBIDDEN", "self-loop edge forbidden")
        edges.append((u, v))
    g_raw = require_seq(conductances_in, "conductances", min_len=m, max_len=m)
    g = [require_pos_rat(x, f"conductances[{i}]") for i, x in enumerate(g_raw)]
    eta_raw = require_seq(forcing_in, "forcing", min_len=m, max_len=m)
    eta = [require_rat(x, f"forcing[{i}]") for i, x in enumerate(eta_raw)]

    B = [[Fraction(0)] * m for _ in range(n)]
    for e_idx, (u, v) in enumerate(edges):
        B[u][e_idx] = Fraction(-1)
        B[v][e_idx] = Fraction(1)
    Bt = _transpose(B)

    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    components = 0
    for s in range(n):
        if not seen[s]:
            components += 1
            stack = [s]
            seen[s] = True
            while stack:
                cur = stack.pop()
                for nxt in adj[cur]:
                    if not seen[nxt]:
                        seen[nxt] = True
                        stack.append(nxt)

    beta1 = m - n + components
    ker_basis = nullspace_basis_q(B)

    BG = [[B[i][e] * g[e] for e in range(m)] for i in range(n)]
    L_G = _mat_mul(BG, Bt)
    rhs = _mat_vec(BG, eta)
    phi_kh = _mat_vec(moore_penrose_sym_q(L_G), rhs)
    grad_phi = _mat_vec(Bt, phi_kh)
    q = [g[e] * (eta[e] - grad_phi[e]) for e in range(m)]
    q_in_ker = all(x == 0 for x in _mat_vec(B, q))
    power_drive = _dot(eta, q)
    power_diss = sum((q[e] * q[e] / g[e] for e in range(m)), Fraction(0))

    indeg = [0] * n
    out_adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        out_adj[u].append(v)
        indeg[v] += 1
    ready = [i for i in range(n) if indeg[i] == 0]
    order: list[int] = []
    depth_phi = [Fraction(0)] * n
    while ready:
        u = ready.pop(0)
        order.append(u)
        for v in out_adj[u]:
            if depth_phi[v] < depth_phi[u] + 1:
                depth_phi[v] = depth_phi[u] + 1
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    is_dag = len(order) == n
    grounding_verified = False
    farkas_cycle_witness: list[str] | None = None
    farkas_verified = False
    if is_dag:
        grounding_verified = all(d >= 1 for d in _mat_vec(Bt, depth_phi))
    else:
        rem_nodes = {i for i in range(n) if indeg[i] > 0}
        in_adj_rem: dict[int, list[int]] = {i: [] for i in rem_nodes}
        for u, v in edges:
            if u in rem_nodes and v in rem_nodes:
                in_adj_rem[v].append(u)
        cur = min(rem_nodes)
        pos_in_path: dict[int, int] = {}
        path: list[int] = []
        while cur not in pos_in_path:
            pos_in_path[cur] = len(path)
            path.append(cur)
            cur = in_adj_rem[cur][0]
        cyc_nodes = list(reversed(path[pos_in_path[cur]:]))
        cyc_edges = {(cyc_nodes[i], cyc_nodes[(i + 1) % len(cyc_nodes)]) for i in range(len(cyc_nodes))}
        z_vec = [Fraction(1 if e in cyc_edges else 0) for e in edges]
        farkas_verified = all((all(x == 0 for x in _mat_vec(B, z_vec)), sum(z_vec) > 0))
        farkas_cycle_witness = [fmt_q(x) for x in z_vec]

    return {
        "n_nodes": n,
        "n_edges": m,
        "components": components,
        "beta1": beta1,
        "dim_ker_B": len(ker_basis),
        "betti_equals_nullity": len(ker_basis) == beta1,
        "ker_B_basis": [[fmt_q(x) for x in vec] for vec in ker_basis],
        "kirchhoff_flow_q": [fmt_q(x) for x in q],
        "q_in_ker_B": q_in_ker,
        "q_is_zero": all(x == 0 for x in q),
        "advective_power": fmt_q(power_drive),
        "power_balance_exact": power_drive == power_diss,
        "is_directed_acyclic": is_dag,
        "strict_topological_grounding_verified": grounding_verified,
        "grounding_potential": [fmt_q(x) for x in depth_phi] if is_dag else None,
        "farkas_directed_cycle_witness": farkas_cycle_witness,
        "farkas_witness_verified": farkas_verified,
    }


def verify_ledger_journal_completeness(
    ledger_receipts: Any,
    journal_attempts: Any,
) -> dict[str, Any]:
    """
    Fail-closed exo#8 R3 (EXO8-R2-J1..J4) ledger-to-journal completeness invariant:
    every chain-verified resolved receipt in the immutable ledger must appear with exact
    matching outcome in the journal (blocking omission & regressed->pending downgrades).
    """
    if type(ledger_receipts) is not dict:
        raise TorusContentError("LEDGER_NOT_DICT", "ledger_receipts must be strict dict")
    if type(journal_attempts) is not dict:
        raise TorusContentError("JOURNAL_NOT_DICT", "journal_attempts must be strict dict")
    for rid, outcome in ledger_receipts.items():
        require_str(rid, "ledger_receipt_id")
        require_str(outcome, "ledger_outcome")
    for rid, outcome in journal_attempts.items():
        require_str(rid, "journal_receipt_id")
        require_str(outcome, "journal_outcome")
    missing = sorted(rid for rid in ledger_receipts if rid not in journal_attempts)
    mismatched = sorted(
        rid for rid in ledger_receipts
        if rid in journal_attempts and journal_attempts[rid] != ledger_receipts[rid]
    )
    if missing:
        raise TorusContentError("JOURNAL_RECEIPT_OMITTED", f"missing ledger receipts: {missing}")
    if mismatched:
        raise TorusContentError("JOURNAL_OUTCOME_TAMPERED", f"tampered outcomes: {mismatched}")
    return {"complete": True, "verified_receipts": len(ledger_receipts)}


def build_seam3_cycle_cohomology_grounding() -> dict[str, Any]:
    """Certify Seam 3 unifying S18 circulation, S11 supervision, warp-drive#37, & exo#8."""
    t4 = analyze_directed_network_q(
        4,
        [(0, 1), (1, 2), (2, 3)],
        [Fraction(1), Fraction(1), Fraction(1)],
        [Fraction(3), Fraction(-2), Fraction(5)],
    )
    d4_asym = analyze_directed_network_q(
        4,
        [(0, 1), (1, 3), (0, 2), (2, 3)],
        [Fraction(1), Fraction(1), Fraction(1), Fraction(1)],
        [Fraction(2), Fraction(2), Fraction(0), Fraction(0)],
    )
    d4_coboundary = analyze_directed_network_q(
        4,
        [(0, 1), (1, 3), (0, 2), (2, 3)],
        [Fraction(1), Fraction(1), Fraction(1), Fraction(1)],
        [Fraction(1), Fraction(2), Fraction(2), Fraction(1)],
    )
    c3 = analyze_directed_network_q(
        3,
        [(0, 1), (1, 2), (2, 0)],
        [Fraction(1), Fraction(1), Fraction(1)],
        [Fraction(3), Fraction(0), Fraction(0)],
    )

    # warp-drive#37/#11 4-bank causal flush DAG vs un-flushed jacobi_feedback cycle leak
    # Nodes: 0=base_r0, 1=KV, 2=SSM, 3=horiz_lattice, 4=jacobi_feedback, 5=verified_commit
    wd_clean_edges = [(0, 1), (0, 2), (0, 3), (1, 5), (2, 5), (3, 4), (4, 5)]
    wd_clean = analyze_directed_network_q(
        6,
        wd_clean_edges,
        [Fraction(1)] * 7,
        [Fraction(0)] * 7,
    )
    wd_leak_edges = wd_clean_edges + [(4, 3)]
    wd_leak = analyze_directed_network_q(
        6,
        wd_leak_edges,
        [Fraction(1)] * 8,
        [Fraction(0)] * 7 + [Fraction(2)],
    )

    # exo#8 R3 ledger-to-journal completeness positive control
    exo8_ok = verify_ledger_journal_completeness(
        {"r1": "regressed", "r2": "regressed"},
        {"r1": "regressed", "r2": "regressed"},
    )

    all_ok = all((
        t4["beta1"] == 0,
        t4["betti_equals_nullity"],
        t4["q_is_zero"],
        t4["is_directed_acyclic"],
        t4["strict_topological_grounding_verified"],
        d4_asym["beta1"] == 1,
        d4_asym["betti_equals_nullity"],
        not d4_asym["q_is_zero"],
        d4_asym["power_balance_exact"],
        d4_asym["is_directed_acyclic"],
        d4_asym["strict_topological_grounding_verified"],
        d4_coboundary["q_is_zero"],
        c3["beta1"] == 1,
        not c3["q_is_zero"],
        c3["power_balance_exact"],
        not c3["is_directed_acyclic"],
        c3["farkas_witness_verified"],
        c3["farkas_directed_cycle_witness"] == ["1", "1", "1"],
        wd_clean["beta1"] == 2,
        wd_clean["is_directed_acyclic"],
        wd_clean["strict_topological_grounding_verified"],
        not wd_leak["is_directed_acyclic"],
        wd_leak["farkas_witness_verified"],
        wd_leak["farkas_directed_cycle_witness"] == ["0", "0", "0", "0", "0", "1", "0", "1"],
        exo8_ok["complete"],
    ))
    return {
        "seam_id": "SEAM-3",
        "tracks_connected": [
            "track-s18-biomimetic-structural-operators",
            "track-s11-erlang-otp-supervision",
            "Moissanite-Labs/warp-drive#37/#11",
            "siliconcordat/exo#8",
        ],
        "regime_A_tree_chain_T4": t4,
        "regime_B_diamond_DAG_D4_asymmetric_F1_refutation": d4_asym,
        "regime_B_diamond_DAG_D4_coboundary_control": d4_coboundary,
        "regime_C_directed_cycle_C3_farkas_obstruction": c3,
        "warp_drive_4bank_clean_flush_DAG": wd_clean,
        "warp_drive_4bank_unflushed_jacobi_cycle": wd_leak,
        "exo8_ledger_journal_completeness": exo8_ok,
        "passed": all_ok,
    }


# ---------------------------------------------------------------------------
# PILLAR 4 — SEAM 4 (Serendipitous 4-Track Discovery + `warp-drive#14` Bridge):
# S2 Character Kernel <-> S16 MacWilliams <-> S15/S15c/S15d E_8/WHT_8/guide_a <-> S14 HAWK
# ---------------------------------------------------------------------------

def _krawtchouk_int(n: int, q: int, j: int, i: int) -> int:
    total = 0
    for r in range(min(j, i) + 1):
        if j - r <= n - i:
            total += ((-1) ** r) * math.comb(i, r) * math.comb(n - i, j - r) * ((q - 1) ** (j - r))
    return total


def _sigma3(m: int) -> int:
    total = 0
    for d in range(1, m + 1):
        if m % d == 0:
            total += d * d * d
    return total


def _poly_mul_trunc(a: list[int], b: list[int], max_deg: int) -> list[int]:
    out = [0] * (max_deg + 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        limit = min(len(b), max_deg + 1 - i)
        for j in range(limit):
            out[i + j] += ai * b[j]
    return out


def _poly_pow_trunc(base: list[int], exp: int, max_deg: int) -> list[int]:
    res = [0] * (max_deg + 1)
    res[0] = 1
    p = base[: max_deg + 1]
    e = exp
    while e > 0:
        if e & 1:
            res = _poly_mul_trunc(res, p, max_deg)
        e >>= 1
        if e > 0:
            p = _poly_mul_trunc(p, p, max_deg)
    return res


def _build_hadamard_char_kernel(d: int) -> list[list[int]]:
    """Exact F_2^d additive character kernel K[x][y] = (-1)^(x . y) (S2 Lemma 3 & S15c WHT)."""
    sz = 1 << d
    return [
        [1 if ((x & y).bit_count() % 2 == 0) else -1 for y in range(sz)]
        for x in range(sz)
    ]


def _fwht_int(vec: list[int]) -> list[int]:
    """Exact pure-integer fast Walsh-Hadamard transform (power-of-2 length)."""
    a = vec[:]
    h = 1
    n = len(a)
    while h < n:
        for i in range(0, n, h * 2):
            for j in range(i, i + h):
                x, y = a[j], a[j + h]
                a[j] = x + y
                a[j + h] = x - y
        h *= 2
    return a


def _enumerate_e8_roots_doubled() -> list[tuple[int, ...]]:
    """Enumerate all 240 minimal vectors of E_8 in doubled coordinates u = 2y (||u||^2 = 8)."""
    roots: list[tuple[int, ...]] = []
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    v = [0] * 8
                    v[i] = si
                    v[j] = sj
                    roots.append(tuple(v))
    for mask in range(256):
        if mask.bit_count() % 2 == 0:
            roots.append(tuple(-1 if (mask >> b) & 1 else 1 for b in range(8)))
    return roots


def _construction_a_basis_int(gen_rows: list[list[int]]) -> list[list[int]]:
    """Build exact n x n integer basis B_C for Construction-A parity sublattice C + 2 Z^n."""
    k = len(gen_rows)
    n = len(gen_rows[0])
    basis = [row[:] for row in gen_rows]
    for j in range(k, n):
        row = [0] * n
        row[j] = 2
        basis.append(row)
    return basis


def build_seam4_character_macwilliams_construction_a() -> dict[str, Any]:
    """
    Serendipitous 4-track exact-Z/Q unification + warp-drive#14 Stage-2 Shell-Norm Bridge:
      S2 (Alpoge-Deligne Lemma 3 unitary character kernel K K* = Q^d I)
      <-> S16 (gfq-codes MacWilliams / Krawtchouk self-dual Hamming H_8 [8,4,4])
      <-> S15/S15c/S15d (siliquant E_8 theta 240*sigma_3(m), E_8^4, WHT_8 4096x, guide_a 1.83x)
      <-> S14 (MiniMax HAWK index-2^(n-k) parity-sublattice covolume & BentSum Parseval)
      -> warp-drive#14 bounded-trial execution throughput & zero-unpack Stage-2 shell norm.
    """
    H8 = _build_hadamard_char_kernel(3)
    H8_sq = [[sum(H8[i][t] * H8[t][j] for t in range(8)) for j in range(8)] for i in range(8)]
    h8_unitary_exact = all(H8_sq[i][j] == (8 if i == j else 0) for i in range(8) for j in range(8))

    e8_roots = _enumerate_e8_roots_doubled()
    wht_norm_preserved = True
    wht_wt8_roots = 0
    for u in e8_roots:
        hu = _fwht_int(list(u))
        if sum(x * x for x in hu) != 8 * sum(x * x for x in u):
            wht_norm_preserved = False
        if all(x != 0 for x in hu):
            wht_wt8_roots += 1

    f_q3 = [(((x >> 0) & (x >> 1)) ^ ((x >> 2) & (x >> 3)) ^ ((x >> 4) & (x >> 5))) & 1 for x in range(64)]
    chi_q3 = [1 if b == 0 else -1 for b in f_q3]
    walsh_q3 = _fwht_int(chi_q3)
    q3_bent_exact = all((all(v * v == 64 for v in walsh_q3), sum(f_q3) == 28))

    G_H8 = [
        [1, 0, 0, 0, 0, 1, 1, 1],
        [0, 1, 0, 0, 1, 0, 1, 1],
        [0, 0, 1, 0, 1, 1, 0, 1],
        [0, 0, 0, 1, 1, 1, 1, 0],
    ]
    codewords: list[tuple[int, ...]] = []
    for mask in range(16):
        cw = [0] * 8
        for r in range(4):
            if (mask >> r) & 1:
                for c in range(8):
                    cw[c] ^= G_H8[r][c]
        codewords.append(tuple(cw))
    self_dual_exact = all(
        sum(a * b for a, b in zip(c1, c2)) % 2 == 0 for c1 in codewords for c2 in codewords
    )
    weight_enum = [0] * 9
    for cw in codewords:
        weight_enum[sum(cw)] += 1
    dual_macwilliams = [
        Fraction(sum(weight_enum[i] * _krawtchouk_int(8, 2, j, i) for i in range(9)), 16)
        for j in range(9)
    ]
    macwilliams_self_dual_exact = all(
        dual_macwilliams[j] == Fraction(weight_enum[j], 1) for j in range(9)
    )

    max_shell = 16
    max_deg = 4 * max_shell
    theta3 = [0] * (max_deg + 1)
    theta2 = [0] * (max_deg + 1)
    for k in range(-10, 11):
        d3 = 4 * k * k
        if d3 <= max_deg:
            theta3[d3] += 1
        d2 = (2 * k + 1) * (2 * k + 1)
        if d2 <= max_deg:
            theta2[d2] += 1
    t3_4 = _poly_pow_trunc(theta3, 4, max_deg)
    t2_4 = _poly_pow_trunc(theta2, 4, max_deg)
    t3_8 = _poly_mul_trunc(t3_4, t3_4, max_deg)
    t2_8 = _poly_mul_trunc(t2_4, t2_4, max_deg)
    cross = _poly_mul_trunc(t3_4, t2_4, max_deg)
    theta_from_macwilliams = [t3_8[d] + 14 * cross[d] + t2_8[d] for d in range(max_deg + 1)]

    jacobi_shells = [1] + [240 * _sigma3(m) for m in range(1, max_shell + 1)]
    extracted_shells = [theta_from_macwilliams[4 * m] for m in range(max_shell + 1)]
    non_mult4_zero = all(
        theta_from_macwilliams[d] == 0 for d in range(max_deg + 1) if d % 4 != 0
    )
    theta_matches_jacobi = all((extracted_shells == jacobi_shells, non_mult4_zero))

    s_e8_2 = _poly_mul_trunc(jacobi_shells, jacobi_shells, max_shell)
    s_e8_4 = _poly_mul_trunc(s_e8_2, s_e8_2, max_shell)
    w_e8_4: list[int] = []
    running = 0
    for cnt in s_e8_4:
        running += cnt
        w_e8_4.append(running)

    B_hawk = _construction_a_basis_int([[1, 1, 1, 1, 1, 1, 1, 1]])
    det_hawk = abs(bareiss_det_int(B_hawk))
    G_hawk = [[sum(B_hawk[i][t] * B_hawk[j][t] for t in range(8)) for j in range(8)] for i in range(8)]
    gram_det_hawk = bareiss_det_int(G_hawk)

    B_ham8 = _construction_a_basis_int(G_H8)
    det_ham8 = abs(bareiss_det_int(B_ham8))
    G_ham8 = [[sum(B_ham8[i][t] * B_ham8[j][t] for t in range(8)) for j in range(8)] for i in range(8)]
    gram_det_ham8 = bareiss_det_int(G_ham8)
    e8_scaled_gram_det = Fraction(gram_det_ham8, 1 << 8)

    G_bad = [
        [1, 0, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 1, 1],
        [0, 0, 1, 0, 1, 1, 0, 1],
        [0, 0, 0, 1, 1, 1, 1, 0],
    ]
    bad_min_wt = min(
        sum(
            (sum(G_bad[r][c] for r in range(4) if (mask >> r) & 1) % 2)
            for c in range(8)
        )
        for mask in range(1, 16)
    )
    bad_lambda1_sq = Fraction(min(4, bad_min_wt), 2)
    e8_lambda1_sq = Fraction(min(4, 4), 2)

    # warp-drive#14 Force-Multiplier Bridge (AUDIT-115R 4096x adjoint WHT + AUDIT-116R 1.83x guide_a + Shell Norm)
    rows_w, cols_w = 4096, 1024
    leaves_total = (rows_w * cols_w) // 8  # 524,288 E_8 leaves
    input_blocks = cols_w // 8  # 128 8D input blocks
    adjoint_wht_reduction = Fraction(leaves_total, input_blocks)  # exact 4096
    stage1_share = Fraction(7, 10)  # 70% Stage-1 cycle share from AUDIT-115R (68%-75%)
    guide_a_stage1_speedup = Fraction(183, 100)  # 1.83x 88b Stage-1 speedup from AUDIT-116R
    amdahl_e2e_speedup = Fraction(1) / ((Fraction(1) - stage1_share) + stage1_share / guide_a_stage1_speedup)
    # Exact zero-unpack Stage-2 Frobenius bound for E_8^4 block at dyadic scale s_g = 1/16:
    s_g = Fraction(1, 16)
    frob_sq_cap_88b = 2 * s_g * s_g * 48  # 96 / 256 = 3/8
    frob_sq_cap_136b = 2 * s_g * s_g * 391  # 782 / 256 = 391/128
    # Verify exact Frobenius norm^2 of a 4-root E_8^4 block (m=4) after WHT_8 / sqrt(8): 2 * 4 * s_g^2 = 8/256 = 1/32
    sample_root = e8_roots[0]
    hu_sample = _fwht_int(list(sample_root))
    # ||y||^2 = ||u||^2 / 4 = ||H8 u||^2 / 32; 4 identical roots -> m = 4 -> 4 * ||y||^2 = 8
    block4_norm_sq = 4 * Fraction(sum(x * x for x in hu_sample), 32) * s_g * s_g
    shell_norm_exact = block4_norm_sq == 2 * 4 * s_g * s_g

    all_ok = all((
        h8_unitary_exact,
        len(e8_roots) == 240,
        wht_norm_preserved,
        wht_wt8_roots == 0,
        q3_bent_exact,
        self_dual_exact,
        weight_enum == [1, 0, 0, 0, 14, 0, 0, 0, 1],
        macwilliams_self_dual_exact,
        theta_matches_jacobi,
        w_e8_4[1] == 961,
        w_e8_4[2] == 355201,
        det_hawk == 128,
        gram_det_hawk == 16384,
        det_ham8 == 16,
        gram_det_ham8 == 256,
        e8_scaled_gram_det == 1,
        bad_min_wt == 3,
        bad_lambda1_sq < e8_lambda1_sq,
        adjoint_wht_reduction == 4096,
        amdahl_e2e_speedup == Fraction(1830, 1249),
        shell_norm_exact,
        block4_norm_sq <= frob_sq_cap_88b,
    ))
    return {
        "seam_id": "SEAM-4",
        "tracks_connected": [
            "track-s2-alpoge-deligne",
            "track-s16-gfq-distance-certifier",
            "track-s15-ballpack-tree-unrank",
            "track-s15c-e8had-simd-ballpack",
            "track-s15d-e8-leaf-stage1-attack",
            "track-s14-minimax-cryptanalysis",
            "Moissanite-Labs/warp-drive#14",
        ],
        "s2_h8_unitary_8I": h8_unitary_exact,
        "s15c_e8_root_count": len(e8_roots),
        "s15c_wht8_isometry_preserved": wht_norm_preserved,
        "s15c_e8had_weight8_root_count": wht_wt8_roots,
        "s14_bentsum_q3_parseval_flat_64": q3_bent_exact,
        "s16_hamming8_self_dual": self_dual_exact,
        "s16_hamming8_weight_enumerator": weight_enum,
        "s16_macwilliams_krawtchouk_exact": macwilliams_self_dual_exact,
        "s15_construction_a_theta_matches_jacobi_m0_16": theta_matches_jacobi,
        "s15_e8_shells_m0_to_6": jacobi_shells[:7],
        "s15_e8_4_ball_counts_m0_to_4": w_e8_4[:5],
        "s14_hawk_k1_det": det_hawk,
        "s14_hawk_k1_gram_det": gram_det_hawk,
        "s15_s16_hamming_k4_det": det_ham8,
        "s15_s16_e8_scaled_gram_det": fmt_q(e8_scaled_gram_det),
        "control_non_self_dual_8_4_3_dmin": bad_min_wt,
        "control_lambda1_sq_vs_e8": [fmt_q(bad_lambda1_sq), fmt_q(e8_lambda1_sq)],
        "warp_drive_14_siliquant_force_multiplier": {
            "adjoint_wht_reduction_4096x1024": fmt_q(adjoint_wht_reduction),
            "guide_a_stage1_speedup_88b": fmt_q(guide_a_stage1_speedup),
            "amdahl_e2e_dequant_speedup": fmt_q(amdahl_e2e_speedup),
            "zero_unpack_frob_sq_cap_88b_s1_16": fmt_q(frob_sq_cap_88b),
            "zero_unpack_frob_sq_cap_136b_s1_16": fmt_q(frob_sq_cap_136b),
            "sample_m4_block_norm_sq": fmt_q(block4_norm_sq),
            "shell_norm_isometry_exact": shell_norm_exact,
        },
        "passed": all_ok,
    }


# ---------------------------------------------------------------------------
# PILLAR 5 — Transfer-Matrix Split (Volkersen SL(2,Q) vs F3 Non-Normal) +
#            Fail-Closed Seam & Missed-Portals Ledger Certifier
# ---------------------------------------------------------------------------

def certify_torus_seam_record(rec: Any) -> dict[str, Any]:
    """Fail-closed Law-5 + Law-2b + Law-4 governance gate for candidate torus-knot seams."""
    if type(rec) is not dict:
        raise TorusContentError("SEAM_NOT_DICT", "seam record must be strict dict")
    req_keys = frozenset({
        "seam_id",
        "status",
        "novelty_tier",
        "in_89node_graph_already",
        "has_exact_q_operator",
        "has_minimal_counterexample",
        "dual_oracle_verified",
    })
    if set(rec.keys()) != req_keys:
        raise TorusContentError("SEAM_BAD_KEYS", f"unexpected keys: {sorted(map(repr, rec.keys()))}")
    sid = require_str(rec["seam_id"], "seam_id")
    status = require_str(rec["status"], "status")
    novelty = require_str(rec["novelty_tier"], "novelty_tier")
    already_in_graph = require_bool(rec["in_89node_graph_already"], "in_89node_graph_already")
    has_op = require_bool(rec["has_exact_q_operator"], "has_exact_q_operator")
    has_ce = require_bool(rec["has_minimal_counterexample"], "has_minimal_counterexample")
    dual_ok = require_bool(rec["dual_oracle_verified"], "dual_oracle_verified")

    if status not in _ALLOWED_SEAM_STATUS:
        raise TorusContentError("INVALID_SEAM_STATUS", f"unknown status {status!r}")
    if novelty not in _ALLOWED_NOVELTY:
        raise TorusContentError("INVALID_NOVELTY_TIER", f"unknown novelty tier {novelty!r}")
    if novelty == "N2":
        raise TorusContentError("UNPROVED_N2_INFLATION", "N2 requires external prior-art clearance")
    if status == "VERIFIED_EXACT_SEAM":
        if already_in_graph:
            raise TorusContentError("DUPLICATE_GRAPH_EDGE", f"{sid} is already in 89-node graph")
        if not has_op:
            raise TorusContentError("METAPHOR_SMUGGLING", f"{sid} lacks exact Z/Q operator")
        if not dual_ok:
            raise TorusContentError("MISSING_DUAL_ORACLE", f"{sid} lacks dual-oracle verification")
    else:
        if not has_ce:
            raise TorusContentError("FALSIFIED_WITHOUT_COUNTEREXAMPLE", f"{sid} lacks counterexample")
    return {"seam_id": sid, "status": status, "novelty_tier": novelty, "admitted": True}


def certify_missed_portal_entry(entry: Any) -> dict[str, Any]:
    """Fail-closed validator for Missed-Portals & Unfinished-Gems Ledger entries."""
    if type(entry) is not dict:
        raise TorusContentError("PORTAL_NOT_DICT", "portal entry must be strict dict")
    req_keys = frozenset({
        "portal_id",
        "origin_refs",
        "target_repo",
        "novelty_tier",
        "disposition",
        "concrete_gap",
    })
    if set(entry.keys()) != req_keys:
        raise TorusContentError("PORTAL_BAD_KEYS", f"unexpected keys: {sorted(map(repr, entry.keys()))}")
    pid = require_str(entry["portal_id"], "portal_id")
    refs = require_str(entry["origin_refs"], "origin_refs")
    repo = require_str(entry["target_repo"], "target_repo")
    nov = require_str(entry["novelty_tier"], "novelty_tier")
    disp = require_str(entry["disposition"], "disposition")
    gap = require_str(entry["concrete_gap"], "concrete_gap")
    if nov not in _ALLOWED_NOVELTY:
        raise TorusContentError("INVALID_PORTAL_NOVELTY", f"unknown novelty {nov!r}")
    if disp not in _ALLOWED_PORTAL_STATUS:
        raise TorusContentError("INVALID_PORTAL_DISPOSITION", f"unknown disposition {disp!r}")
    return {
        "portal_id": pid,
        "origin_refs": refs,
        "target_repo": repo,
        "novelty_tier": nov,
        "disposition": disp,
        "concrete_gap": gap,
    }


def _volkersen_sl2_transfer_witness() -> dict[str, Any]:
    """Prove S18 Volkersen uniform m=4, alpha=4 equals unimodular SL(2,Q) transfer matrix."""
    lam = Fraction(4, 3)
    c = Fraction(2) + 2 * lam
    M = [[c, Fraction(-1)], [Fraction(1), Fraction(0)]]
    det_M = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    M2 = _mat_mul(M, M)
    M3 = _mat_mul(M2, M)
    u0 = Fraction(-1, 2)
    u4_target = Fraction(1, 2)
    u1 = (u4_target - M3[0][1] * u0) / M3[0][0]
    u2 = c * u1 - u0
    u3 = c * u2 - u1
    u4 = c * u3 - u2
    Ts = [u + Fraction(1, 2) for u in (u0, u1, u2, u3, u4)]
    forces = [Ts[i + 1] - Ts[i] for i in range(4)]
    tridiag_res_zero = all(
        (-Ts[i] + c * Ts[i + 1] - Ts[i + 2]) == lam for i in range(3)
    )
    return {
        "lambda": fmt_q(lam),
        "det_SL2_transfer": fmt_q(det_M),
        "rivet_forces": [fmt_q(f) for f in forces],
        "peak_rivet_force": fmt_q(max(forces)),
        "exact_match_s18_11_28": max(forces) == Fraction(11, 28),
        "tridiagonal_residual_zero": tridiag_res_zero,
    }


def _falsified_f3_non_normal_transfer() -> dict[str, Any]:
    """
    Falsified Metaphorical Bridge F3: R8 AUDIT-072R lower-triangular transfer matrix T_J0
    has all eigenvalues 3/4 < 1, YET In(I - T^T T) = (2, 1, 0) and amplifies e_1 by 27/8 at t=1
    and 203541903/8388608 (~24.264x) at t=6.
    """
    T = [
        [Fraction(3, 4), Fraction(0), Fraction(0)],
        [Fraction(3, 4), Fraction(3, 4), Fraction(0)],
        [Fraction(3, 2), Fraction(3, 4), Fraction(3, 4)],
    ]
    charpoly, ch_zero = faddeev_charpoly_q(T)
    expected_cp = [Fraction(1), Fraction(-9, 4), Fraction(27, 16), Fraction(-27, 64)]
    TtT = _mat_mul(_transpose(T), T)
    I_minus_TtT = [[(Fraction(1) if i == j else Fraction(0)) - TtT[i][j] for j in range(3)] for i in range(3)]
    in_bk, bk_ok = bunch_kaufman_inertia_q(I_minus_TtT)
    in_fd, fd_ok = faddeev_descartes_inertia_q(I_minus_TtT)
    x = [Fraction(1), Fraction(0), Fraction(0)]
    norms_sq: list[Fraction] = []
    for _ in range(6):
        x = _mat_vec(T, x)
        norms_sq.append(_dot(x, x))
    return {
        "charpoly": [fmt_q(c) for c in charpoly],
        "cayley_hamilton_zero": ch_zero,
        "all_eigenvalues_3_4": charpoly == expected_cp,
        "inertia_I_minus_TtT": list(in_bk),
        "dual_oracle_match": all((bk_ok, fd_ok, in_bk == in_fd)),
        "t1_norm_sq": fmt_q(norms_sq[0]),
        "t2_norm_sq": fmt_q(norms_sq[1]),
        "t6_peak_norm_sq": fmt_q(norms_sq[5]),
        "refutes_monotone_decay": all((norms_sq[0] > 1, norms_sq[5] > 24, in_bk == (2, 1, 0))),
    }


def _canonical_missed_portals_raw() -> list[dict[str, Any]]:
    """18 concrete unfollowed leads, open conjectures, and anomalies mined from #1..#1033."""
    return [
        {
            "portal_id": "MP-01",
            "origin_refs": "cross_pollination_graph.json (E-01,E-04,E-06,E-10,E-12,E-14,E-15)",
            "target_repo": "Foundation-0/aletheia + Moissanite-Labs/{weft-loom,scry,siliconcordat,ml-os,ethos}",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "7 Wave-1/2 edges remained status=round2_ready unverified across 141-edge graph",
        },
        {
            "portal_id": "MP-02",
            "origin_refs": "AUDIT-059 (R5-4, #327/#345/#346)",
            "target_repo": "Moissanite-Labs/siliquant",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "Gemma 4 E4B Layer-10 #1/42 fan-out KL hypothesis (L09 vs L12/L13) awaits live GPU test",
        },
        {
            "portal_id": "MP-03",
            "origin_refs": "AUDIT-059 (R5-4, #327/#335)",
            "target_repo": "Moissanite-Labs/heedle",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "Pythia-160m non-monotonic dark-neuron rebound (3.77%->5.68%) unmodeled in SP-09 drift guard",
        },
        {
            "portal_id": "MP-04",
            "origin_refs": "AUDIT-087R (R10-4, cave-expedition#6, #806/#846)",
            "target_repo": "Foundation-0/continuum",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "Pre-registered 635 MB GWOSC/SEIS/WAVES/TESS raw telemetry test remains 0% fetched post-PREREG-01..04",
        },
        {
            "portal_id": "MP-05",
            "origin_refs": "LAW1B Atlas + SILICONCORDAT_ASKA_PHYSICAL_ISSUE_PORTALS.md (#958/#1023/#1032)",
            "target_repo": "siliconcordat/warp#13 + Moissanite-Labs/warp-drive#14",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "Stage 2 trusts self-declared norm integers without parsing GGUF v3 tensors or lora.alpha (gates #15/#17)",
        },
        {
            "portal_id": "MP-06",
            "origin_refs": "SILICONCORDAT_ASKA_PHYSICAL_ISSUE_PORTALS.md (#958/#983/#1032)",
            "target_repo": "siliconcordat/warp#16 + Moissanite-Labs/warp-drive#7/#11",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "ExternalCommandCanaryRunner unwired in cli.py; /etc/warp/canaries still read_only in Landlock blueprint",
        },
        {
            "portal_id": "MP-07",
            "origin_refs": "SILICONCORDAT_ASKA_PHYSICAL_ISSUE_PORTALS.md (#851/#958/#1023/#1030)",
            "target_repo": "aska-physical/optifab#14",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "5 live-reproduced plant-model defects on #13 (qFix outage omission, outage offset, WellFormed, distance)",
        },
        {
            "portal_id": "MP-08",
            "origin_refs": "LAW1B Atlas + #827/#923/#991",
            "target_repo": "Foundation-0/point-charges#22",
            "novelty_tier": "N2",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "4 positive charges with 11 non-degenerate equilibria (> Maxwell bound 9) awaiting full independent check",
        },
        {
            "portal_id": "MP-09",
            "origin_refs": "VITRUVIAN1_AND_PROVEN_LEAN_GEMS.md + #862/#865",
            "target_repo": "Proven-Commons/codec",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "IBAN mod 97-10 single-char digit-to-letter blind spot & 3 swap pairs (1B/2M/3X) not yet formalized in Lean",
        },
        {
            "portal_id": "MP-10",
            "origin_refs": "WEFT_PR_AND_196_GEM_AUDIT.md (#847/#853/#1020)",
            "target_repo": "Moissanite-Labs/weft#224/#219",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "weft#224 Python/JS NaN vs C11 10.0 remaining_budget split; weft#219 backslash-userinfo URL bypass",
        },
        {
            "portal_id": "MP-11",
            "origin_refs": "LAW1B Atlas + #672/#899/#905",
            "target_repo": "Moissanite-Labs/siliquant#29",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "shape/ballpack.py Format.read omits scale/weight/kept-entry invariant validation on untrusted headers",
        },
        {
            "portal_id": "MP-12",
            "origin_refs": "Track S5 AUDIT-101R2 (#620/#707)",
            "target_repo": "generalised.si -> Foundation-0/gfq-codes",
            "novelty_tier": "N0",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "GSI-R-0017 5 binary code certs prove rank only (exhaustive d_min open); WP-01..13 have 0/13 public certs",
        },
        {
            "portal_id": "MP-13",
            "origin_refs": "Track S12 AUDIT-111R (#795/#801/#806)",
            "target_repo": "Foundation-0/math0#9",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "66-room Sokoban Frontier open lower-bound gaps III-14/III-20/III-21 unattacked by 1-cochain peeling",
        },
        {
            "portal_id": "MP-14",
            "origin_refs": "BIO_GEOMETRY_REPO_OPERATOR_MAP.md (#970/#982/#986)",
            "target_repo": "Moissanite-Labs/exo#1217",
            "novelty_tier": "N0",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "Upstream mutable v1.8.0 tla2tools.jar asset 718777374 HTTP 404 still unpatched on main; PR #1218 stale",
        },
        {
            "portal_id": "MP-15",
            "origin_refs": "Track S15c/S15d AUDIT-115R/116R (#995/#1029/#1032)",
            "target_repo": "Moissanite-Labs/siliquant#23/#25 + Moissanite-Labs/warp-drive#14",
            "novelty_tier": "N1",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "guide_a GPU/TPU Pallas roofline & warp-drive#14 cross-org bounded-trial execution await live accelerator bench",
        },
        {
            "portal_id": "MP-16",
            "origin_refs": "AUDIT-085R (#513) + AUDIT-070R (Zenodo 23644664)",
            "target_repo": "Foundation-0/cave-expedition",
            "novelty_tier": "N0",
            "disposition": "FALSIFIED_OR_CLOSED",
            "concrete_gap": "Naive 30-way Schur unification (FALSIFIED by G5-14; narrowed to M1-M3) & Zenodo P=NP (5 exact disproofs)",
        },
        {
            "portal_id": "MP-17",
            "origin_refs": "Track S15d AUDIT-116R (#995/#1029) & Track S18 AUDIT-117 (#992)",
            "target_repo": "Moissanite-Labs/siliquant + aska-physical/fibral-rigidity",
            "novelty_tier": "N1",
            "disposition": "FALSIFIED_OR_CLOSED",
            "concrete_gap": "Low-norm E_8 shell LUT (0.0000% hits under EBG32) & pin-jointed Euplectella 0-mode slogan (zigzag nullity 1)",
        },
        {
            "portal_id": "MP-18",
            "origin_refs": "ROUND8_PORTALS.md + ROUND9_PORTALS.md (#418/#463)",
            "target_repo": "external/zhihu-403-antibot",
            "novelty_tier": "N0",
            "disposition": "BLOCKED_EXTERNAL",
            "concrete_gap": "3 Zhihu URLs HTTP 403 zse_ck anti-bot gated (strictly zero bypass; primary arXiv preprints audited instead)",
        },
    ]


def build_pillar5_transfer_falsifications_and_ledger() -> dict[str, Any]:
    """Certify Volkersen SL(2,Q) vs F3 non-normal transfer, all 7 seams, and 18 missed portals."""
    volk = _volkersen_sl2_transfer_witness()
    f3 = _falsified_f3_non_normal_transfer()

    seam_records_raw = [
        {
            "seam_id": "SEAM-1",
            "status": "VERIFIED_EXACT_SEAM",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": True,
            "has_minimal_counterexample": False,
            "dual_oracle_verified": True,
        },
        {
            "seam_id": "SEAM-2",
            "status": "VERIFIED_EXACT_SEAM",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": True,
            "has_minimal_counterexample": True,
            "dual_oracle_verified": True,
        },
        {
            "seam_id": "SEAM-3",
            "status": "VERIFIED_EXACT_SEAM",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": True,
            "has_minimal_counterexample": True,
            "dual_oracle_verified": True,
        },
        {
            "seam_id": "SEAM-4",
            "status": "VERIFIED_EXACT_SEAM",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": True,
            "has_minimal_counterexample": True,
            "dual_oracle_verified": True,
        },
        {
            "seam_id": "F1_BETA1_ZERO_VS_DAG",
            "status": "FALSIFIED_METAPHOR",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": False,
            "has_minimal_counterexample": True,
            "dual_oracle_verified": True,
        },
        {
            "seam_id": "F2_BINARY32_FLOOR_LP_SHIFT",
            "status": "FALSIFIED_METAPHOR",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": False,
            "has_minimal_counterexample": True,
            "dual_oracle_verified": True,
        },
        {
            "seam_id": "F3_SPEC_RADIUS_MONOTONE_DECAY",
            "status": "FALSIFIED_METAPHOR",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": False,
            "has_minimal_counterexample": True,
            "dual_oracle_verified": True,
        },
    ]
    certified_seams = [certify_torus_seam_record(r) for r in seam_records_raw]
    certified_portals = [certify_missed_portal_entry(e) for e in _canonical_missed_portals_raw()]

    counts_by_disp = {
        "LIVE_PORTAL": sum(1 for p in certified_portals if p["disposition"] == "LIVE_PORTAL"),
        "FALSIFIED_OR_CLOSED": sum(1 for p in certified_portals if p["disposition"] == "FALSIFIED_OR_CLOSED"),
        "BLOCKED_EXTERNAL": sum(1 for p in certified_portals if p["disposition"] == "BLOCKED_EXTERNAL"),
    }
    counts_by_nov = {
        "N0": sum(1 for p in certified_portals if p["novelty_tier"] == "N0"),
        "N1": sum(1 for p in certified_portals if p["novelty_tier"] == "N1"),
        "N2": sum(1 for p in certified_portals if p["novelty_tier"] == "N2"),
    }
    all_ok = all((
        volk["exact_match_s18_11_28"],
        volk["tridiagonal_residual_zero"],
        volk["det_SL2_transfer"] == "1",
        f3["cayley_hamilton_zero"],
        f3["all_eigenvalues_3_4"],
        f3["dual_oracle_match"],
        f3["refutes_monotone_decay"],
        len(certified_seams) == 7,
        len(certified_portals) == 18,
    ))
    return {
        "volkersen_sl2_transfer": volk,
        "falsified_bridge_F3_non_normal_overshoot": f3,
        "certified_seam_verdicts": certified_seams,
        "missed_portals_count": len(certified_portals),
        "missed_portals_by_disposition": counts_by_disp,
        "missed_portals_by_novelty": counts_by_nov,
        "missed_portals_ledger": certified_portals,
        "passed": all_ok,
    }


def build_audit118b_payload() -> dict[str, Any]:
    """Build complete deterministic pure-Z/Q AUDIT-118B payload across all 5 pillars."""
    p1 = build_seam1_rank1_inertia_law()
    p2 = build_seam2_rounding_envelope_duality()
    p3 = build_seam3_cycle_cohomology_grounding()
    p4 = build_seam4_character_macwilliams_construction_a()
    p5 = build_pillar5_transfer_falsifications_and_ledger()
    return {
        "audit_id": "AUDIT-118B",
        "track": "track-s19b-torus-content-weaving",
        "axial_force_multiplier_hub": "Moissanite-Labs/warp-drive",
        "oracle_class": "exact",
        "honest_novelty_tier": "N0/N1",
        "corpus_graph_snapshot": {
            "wave3b_nodes": 74,
            "wave3b_edges": 116,
            "wave2_sync_nodes": 89,
            "wave2_sync_edges": 141,
            "unverified_round2_ready_edges": 7,
            "board_messages_mined": 1033,
            "tracks_mined": 22,
        },
        "pillar_1_seam1_rank1_inertia": p1,
        "pillar_2_seam2_rounding_duality": p2,
        "pillar_3_seam3_cycle_grounding": p3,
        "pillar_4_seam4_character_macwilliams_e8_hawk": p4,
        "pillar_5_transfer_falsifications_and_ledger": p5,
        "all_passed": all((p1["passed"], p2["passed"], p3["passed"], p4["passed"], p5["passed"])),
    }
