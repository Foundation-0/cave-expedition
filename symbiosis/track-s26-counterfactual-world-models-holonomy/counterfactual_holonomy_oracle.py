"""Track S26: Exact Pure-Z/Q Counterfactual World-Model Holonomy & Tomography Oracle.

Zero external dependencies, zero floats on trust paths, zero bare asserts, zero RNG.
Certifies exact rational algebraic identities auditing and breaking the O(h^4) minimax
wall of arXiv:2611.24778v1 (Balestriero, LeCun & Varaku, Nov 2026, Eq. 56 / Thm 3.6):

  - Theorem 1: Exact time-h chiral flow, Lie bracket [X_a, X_eps] = 2*theta*C*a*J*eps,
    Cayley SO(2, Q) factual gauge invariance, Eq. (56) residual-reuse risk 4*C^2*h^4 vs
    exact Bayes/minimax midpoint 4*C^2*h^4/(1+k^2) (strict 1+k^2 gap), and exact
    Pythagorean variance-matched transport improvement at q_0 != 0.
  - Theorem 2: Gauge-stabilizer anisotropy theorem breaking Thm 3.6 on strictly unpaired
    1-step factual covariances (both diagonal Sigma_12 and coordinate-free general PSD
    commutator/trace invariant), plus exact isotropic negative control.
  - Theorem 3: Exact rational 2-step signed-area recovery (general q_0 norm-difference
    formula AND universal q_0-free difference-norm formula) breaking Thm 3.6 even for
    100% isotropic eps, exact degenerate-action boundary controls, smooth nonlinear
    cross-channel O(h^4) -> O(h^6) MSE commutator elimination + self-advection Dg.g != 0
    obstruction (resolved at 3 steps), and exact curved-encoder D^2 E obstruction.
  - Theorem 4: Appendix E.4 multiplicative ratio reuse (0 error vs O(h^2) additive
    failure) and mixed additive+multiplicative 2-step 2x2 exact inversion + singular
    negative control (a_0 == a_1).
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import hmac
import json
import math
from typing import Any

SCHEMA_VERSION = "aletheia.track_s26.counterfactual_holonomy.v1"
TRACK_ID = "TRACK-S26-COUNTERFACTUAL-WORLD-MODELS-HOLONOMY"
MAX_JSON_BYTES = 1_048_576
MAX_JSON_DEPTH = 64
MAX_INT_DIGITS = 1000
MAX_RATIONAL_BITS = 4000

_TEN_POW_INT_LIMIT = 10**MAX_INT_DIGITS
_HEX_LOWER = frozenset("0123456789abcdef")
_ASCII_DIGITS = frozenset("0123456789")
_CERT_KEYS = frozenset({"schema", "track_id", "payload_sha256", "certificate_sha256", "payload"})

Vec2 = tuple[Fraction, Fraction]
Mat2 = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]

J_MAT: Mat2 = (
    (Fraction(0), Fraction(-1)),
    (Fraction(1), Fraction(0)),
)
JT_MAT: Mat2 = (
    (Fraction(0), Fraction(1)),
    (Fraction(-1), Fraction(0)),
)
I2_MAT: Mat2 = (
    (Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(1)),
)
K_SHEAR_MAT: Mat2 = (
    (Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(-1)),
)


class CounterfactualHolonomyError(ValueError):
    """Typed fail-closed error raised on any invalid input, control breach, or tamper."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# ---------------------------------------------------------------------------
# Strict Zone-B Primitive Validators & Canonical Zero-Float JSON
# ---------------------------------------------------------------------------

def require_bool(val: Any, label: str = "bool") -> bool:
    if type(val) is not bool:
        raise CounterfactualHolonomyError("INVALID_BOOL", f"{label} must be exact bool")
    return val


def require_int(val: Any, label: str = "int") -> int:
    if type(val) is not int:
        raise CounterfactualHolonomyError("INVALID_INT", f"{label} must be exact int")
    if val >= _TEN_POW_INT_LIMIT or val <= -_TEN_POW_INT_LIMIT:
        raise CounterfactualHolonomyError("INT_DIGIT_LIMIT", f"{label} exceeds {MAX_INT_DIGITS} digits")
    return val


def require_str(val: Any, label: str = "str") -> str:
    if type(val) is not str:
        raise CounterfactualHolonomyError("INVALID_STR", f"{label} must be exact str")
    try:
        val.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CounterfactualHolonomyError("INVALID_UTF8_SURROGATE", f"{label} contains lone surrogate") from exc
    return val


def require_sha256_hex(val: Any, label: str = "sha256") -> str:
    s = require_str(val, label)
    if len(s) != 64:
        raise CounterfactualHolonomyError("INVALID_SHA256", f"{label} must be 64-char lowercase hex")
    for ch in s:
        if ch not in _HEX_LOWER:
            raise CounterfactualHolonomyError("INVALID_SHA256", f"{label} contains non-hex char")
    return s


def require_fraction(val: Any, label: str = "rational") -> Fraction:
    if type(val) is not Fraction:
        raise CounterfactualHolonomyError("INVALID_RATIONAL", f"{label} must be exact Fraction")
    if val.numerator.bit_length() > MAX_RATIONAL_BITS or val.denominator.bit_length() > MAX_RATIONAL_BITS:
        raise CounterfactualHolonomyError("RATIONAL_BIT_LIMIT", f"{label} exceeds {MAX_RATIONAL_BITS} bits")
    return val


def parse_exact_int_str(raw: Any, label: str = "int_str") -> int:
    s = require_str(raw, label)
    if not s:
        raise CounterfactualHolonomyError("INVALID_INT_STR", f"{label} is empty")
    body = s[1:] if s[0] == "-" else s
    if not body:
        raise CounterfactualHolonomyError("INVALID_INT_STR", f"{label} missing digits")
    if len(body) > 1 and body[0] == "0":
        raise CounterfactualHolonomyError("INVALID_INT_STR", f"{label} has leading zero")
    if len(body) > MAX_INT_DIGITS:
        raise CounterfactualHolonomyError("INT_DIGIT_LIMIT", f"{label} exceeds {MAX_INT_DIGITS} digits")
    for ch in body:
        if ch not in _ASCII_DIGITS:
            raise CounterfactualHolonomyError("INVALID_INT_STR", f"{label} contains non-ASCII digit")
    val = int(s)
    if val == 0 and s[0] == "-":
        raise CounterfactualHolonomyError("INVALID_INT_STR", f"{label} negative zero forbidden")
    return val


def format_rational(val: Fraction, label: str = "rational") -> str:
    q = require_fraction(val, label)
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def parse_exact_rational(raw: Any, label: str = "rational") -> Fraction:
    s = require_str(raw, label)
    if "/" not in s:
        num = parse_exact_int_str(s, label)
        return require_fraction(Fraction(num, 1), label)
    parts = s.split("/")
    if len(parts) != 2:
        raise CounterfactualHolonomyError("INVALID_RATIONAL_STR", f"{label} must have at most one '/'")
    num = parse_exact_int_str(parts[0], f"{label}.num")
    den = parse_exact_int_str(parts[1], f"{label}.den")
    if den <= 1:
        raise CounterfactualHolonomyError("INVALID_RATIONAL_STR", f"{label} denominator must be > 1")
    if math.gcd(abs(num), den) != 1:
        raise CounterfactualHolonomyError("NON_CANONICAL_RATIONAL", f"{label} is not in lowest terms")
    return require_fraction(Fraction(num, den), label)


def _validate_json_tree_iterative(root: Any) -> None:
    stack: list[tuple[Any, int]] = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise CounterfactualHolonomyError("JSON_DEPTH_LIMIT", f"JSON nesting exceeds {MAX_JSON_DEPTH}")
        t = type(node)
        if node is None or t is bool:
            continue
        if t is int:
            require_int(node, "json_int")
            continue
        if t is str:
            require_str(node, "json_str")
            continue
        if t is list:
            nxt = depth + 1
            for item in node:
                stack.append((item, nxt))
            continue
        if t is dict:
            nxt = depth + 1
            for k, v in node.items():
                require_str(k, "json_key")
                stack.append((v, nxt))
            continue
        raise CounterfactualHolonomyError("FORBIDDEN_JSON_TYPE", f"unsupported JSON type {t.__name__}")


def _reject_json_float(token: str) -> Any:
    raise CounterfactualHolonomyError("FLOAT_LITERAL_FORBIDDEN", f"float literal forbidden: {token}")


def _reject_json_constant(token: str) -> Any:
    raise CounterfactualHolonomyError("NONFINITE_LITERAL_FORBIDDEN", f"JSON constant forbidden: {token}")


def _parse_json_int_bounded(token: str) -> int:
    return parse_exact_int_str(token, "json_int")


def _strict_pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        require_str(k, "json_key")
        if k in out:
            raise CounterfactualHolonomyError("DUPLICATE_JSON_KEY", f"duplicate key {k!r}")
        out[k] = v
    return out


def parse_strict_json_text(text: Any, *, require_object: bool = True) -> Any:
    s = require_str(text, "json_text")
    require_bool(require_object, "require_object")
    if len(s.encode("utf-8")) > MAX_JSON_BYTES:
        raise CounterfactualHolonomyError("JSON_TOO_LARGE", f"JSON text exceeds {MAX_JSON_BYTES} bytes")
    try:
        parsed = json.loads(
            s,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_constant,
            parse_int=_parse_json_int_bounded,
            object_pairs_hook=_strict_pairs_hook,
        )
    except CounterfactualHolonomyError:
        raise
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise CounterfactualHolonomyError("JSON_PARSE_ERROR", f"invalid JSON: {type(exc).__name__}") from exc
    _validate_json_tree_iterative(parsed)
    if require_object and type(parsed) is not dict:
        raise CounterfactualHolonomyError("JSON_ROOT_NOT_OBJECT", "JSON root must be an object")
    return parsed


def canonical_json_bytes(obj: Any) -> bytes:
    _validate_json_tree_iterative(obj)
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def sha256_canonical(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


# ---------------------------------------------------------------------------
# Pure-Q 2D Linear Algebra & Chiral Hard-Pair Flow (Eq. 56)
# ---------------------------------------------------------------------------

def mat_mul(a: Mat2, b: Mat2) -> Mat2:
    return (
        (a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]),
        (a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]),
    )


def mat_vec(m: Mat2, v: Vec2) -> Vec2:
    return (m[0][0] * v[0] + m[0][1] * v[1], m[1][0] * v[0] + m[1][1] * v[1])


def mat_transpose(m: Mat2) -> Mat2:
    return ((m[0][0], m[1][0]), (m[0][1], m[1][1]))


def mat_sub(a: Mat2, b: Mat2) -> Mat2:
    return (
        (a[0][0] - b[0][0], a[0][1] - b[0][1]),
        (a[1][0] - b[1][0], a[1][1] - b[1][1]),
    )


def mat_scale(s: Fraction, m: Mat2) -> Mat2:
    return (
        (s * m[0][0], s * m[0][1]),
        (s * m[1][0], s * m[1][1]),
    )


def mat_trace(m: Mat2) -> Fraction:
    return m[0][0] + m[1][1]


def mat_det(m: Mat2) -> Fraction:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def mat_commutator(a: Mat2, b: Mat2) -> Mat2:
    return mat_sub(mat_mul(a, b), mat_mul(b, a))


def vec_add(u: Vec2, v: Vec2) -> Vec2:
    return (u[0] + v[0], u[1] + v[1])


def vec_sub(u: Vec2, v: Vec2) -> Vec2:
    return (u[0] - v[0], u[1] - v[1])


def vec_scale(s: Fraction, v: Vec2) -> Vec2:
    return (s * v[0], s * v[1])


def vec_norm_sq(v: Vec2) -> Fraction:
    return v[0] * v[0] + v[1] * v[1]


def vec_det(u: Vec2, v: Vec2) -> Fraction:
    return u[0] * v[1] - u[1] * v[0]


def _require_theta(theta: Any) -> int:
    val = require_int(theta, "theta")
    if val not in (-1, 1):
        raise CounterfactualHolonomyError("INVALID_THETA", "theta must be -1 or +1")
    return val


def _require_pos_fraction(val: Any, label: str) -> Fraction:
    q = require_fraction(val, label)
    if q <= 0:
        raise CounterfactualHolonomyError("NON_POSITIVE_PARAM", f"{label} must be > 0")
    return q


def _require_vec2(v: Any, label: str) -> Vec2:
    if type(v) is not tuple or len(v) != 2:
        raise CounterfactualHolonomyError("INVALID_VEC2", f"{label} must be 2-tuple of Fraction")
    return (require_fraction(v[0], f"{label}[0]"), require_fraction(v[1], f"{label}[1]"))


def _require_sym_psd_mat2(m: Any, label: str) -> Mat2:
    if type(m) is not tuple or len(m) != 2:
        raise CounterfactualHolonomyError("INVALID_MAT2", f"{label} must be 2x2 tuple of Fraction")
    r0 = _require_vec2(m[0], f"{label}[0]")
    r1 = _require_vec2(m[1], f"{label}[1]")
    mat: Mat2 = (r0, r1)
    if mat[0][1] != mat[1][0]:
        raise CounterfactualHolonomyError("NON_SYMMETRIC_COV", f"{label} must be symmetric")
    if mat_trace(mat) < 0 or mat_det(mat) < 0:
        raise CounterfactualHolonomyError("NON_PSD_COV", f"{label} must be positive semidefinite")
    return mat


def chiral_flow_matrix(theta: int, coupling_c: Fraction, q0: Fraction, action: Fraction, h: Fraction) -> Mat2:
    """Exact time-h flow matrix M_theta = h*(I_2 + theta*C*(2*q0 + a*h)*J) of Eq. (56)."""
    th = _require_theta(theta)
    c = _require_pos_fraction(coupling_c, "coupling_c")
    q0_f = require_fraction(q0, "q0")
    a_f = require_fraction(action, "action")
    h_f = _require_pos_fraction(h, "h")
    u = Fraction(th) * c * (Fraction(2) * q0_f + a_f * h_f)
    return (
        (h_f, -h_f * u),
        (h_f * u, h_f),
    )


def chiral_flow_step(
    theta: int,
    coupling_c: Fraction,
    q0: Fraction,
    x0: Vec2,
    action: Fraction,
    h: Fraction,
    eps: Vec2,
) -> tuple[Fraction, Vec2, Vec2]:
    """Exact closed-form time-h integration of Eq. (56): (q1, x1, dx)."""
    x0_v = _require_vec2(x0, "x0")
    eps_v = _require_vec2(eps, "eps")
    m = chiral_flow_matrix(theta, coupling_c, q0, action, h)
    q1 = q0 + action * h
    dx = mat_vec(m, eps_v)
    x1 = vec_add(x0_v, dx)
    return q1, x1, dx


def chiral_inverse_eps(theta_c: Fraction, q0: Fraction, action: Fraction, h: Fraction, dx: Vec2) -> Vec2:
    """Exact rational inverse eps = (h*(I_2 + theta_c*(2*q0 + a*h)*J))^{-1} dx."""
    tc = require_fraction(theta_c, "theta_c")
    q0_f = require_fraction(q0, "q0")
    a_f = require_fraction(action, "action")
    h_f = _require_pos_fraction(h, "h")
    dx_v = _require_vec2(dx, "dx")
    u = tc * (Fraction(2) * q0_f + a_f * h_f)
    denom = h_f * (Fraction(1) + u * u)
    return (
        (dx_v[0] + u * dx_v[1]) / denom,
        (-u * dx_v[0] + dx_v[1]) / denom,
    )


def cayley_gauge_rotation(u: Fraction) -> Mat2:
    """Exact rational SO(2, Q) gauge matrix R(u) = (I - uJ)^{-1}(I + uJ)."""
    u_f = require_fraction(u, "u")
    denom = Fraction(1) + u_f * u_f
    c_val = (Fraction(1) - u_f * u_f) / denom
    s_val = (Fraction(2) * u_f) / denom
    return ((c_val, -s_val), (s_val, c_val))


def recover_theta_c_from_anisotropic_cov(
    sigma_dx: Mat2,
    sigma_eps: Mat2,
    q0: Fraction,
    action: Fraction,
    h: Fraction,
) -> Fraction:
    """Coordinate-free 1-step recovery of theta*C from unpaired factual covariance."""
    s_dx = _require_sym_psd_mat2(sigma_dx, "sigma_dx")
    s_eps = _require_sym_psd_mat2(sigma_eps, "sigma_eps")
    q0_f = require_fraction(q0, "q0")
    a_f = require_fraction(action, "action")
    h_f = _require_pos_fraction(h, "h")
    w = Fraction(2) * q0_f + a_f * h_f
    if w == 0:
        raise CounterfactualHolonomyError("ZERO_DRIFT_MOMENT", "2*q0 + a*h == 0 gives zero twist")
    disc = mat_trace(s_eps) ** 2 - Fraction(4) * mat_det(s_eps)
    if disc == 0:
        raise CounterfactualHolonomyError("ISOTROPIC_UNIDENTIFIABLE", "isotropic covariance (lambda_1 == lambda_2)")
    num = mat_trace(mat_mul(mat_mul(JT_MAT, s_dx), s_eps))
    return num / (h_f * h_f * w * disc)


def recover_theta_c_two_step_norm_diff(
    dx1: Vec2,
    dx2: Vec2,
    q0: Fraction,
    a0: Fraction,
    a1: Fraction,
    h: Fraction,
) -> Fraction:
    """General-q0 2-step norm-difference signed-area formula for theta*C."""
    v1 = _require_vec2(dx1, "dx1")
    v2 = _require_vec2(dx2, "dx2")
    q0_f = require_fraction(q0, "q0")
    a0_f = require_fraction(a0, "a0")
    a1_f = require_fraction(a1, "a1")
    h_f = _require_pos_fraction(h, "h")
    if a0_f + a1_f == 0:
        raise CounterfactualHolonomyError("DEGENERATE_ACTION_SUM", "a0 + a1 == 0 collapses 2-step area")
    w_sum = Fraction(4) * q0_f + (Fraction(3) * a0_f + a1_f) * h_f
    if w_sum == 0:
        raise CounterfactualHolonomyError("SYMMETRIC_NORM_DEGENERACY", "4*q0 + (3*a0 + a1)*h == 0 zeroes norm diff")
    det12 = vec_det(v1, v2)
    if det12 == 0:
        raise CounterfactualHolonomyError("ZERO_SIGNED_AREA", "det[dx1, dx2] == 0 (zero disturbance)")
    return (vec_norm_sq(v2) - vec_norm_sq(v1)) / (w_sum * det12)


def recover_theta_c_two_step_universal(
    dx1: Vec2,
    dx2: Vec2,
    a0: Fraction,
    a1: Fraction,
    h: Fraction,
) -> Fraction:
    """Universal q0-free 2-step formula theta*C = ||dx2 - dx1||^2 / (h*(a0+a1)*det[dx1, dx2])."""
    v1 = _require_vec2(dx1, "dx1")
    v2 = _require_vec2(dx2, "dx2")
    a0_f = require_fraction(a0, "a0")
    a1_f = require_fraction(a1, "a1")
    h_f = _require_pos_fraction(h, "h")
    a_sum = a0_f + a1_f
    if a_sum == 0:
        raise CounterfactualHolonomyError("DEGENERATE_ACTION_SUM", "a0 + a1 == 0 collapses 2-step area")
    det12 = vec_det(v1, v2)
    if det12 == 0:
        raise CounterfactualHolonomyError("ZERO_SIGNED_AREA", "det[dx1, dx2] == 0 (zero disturbance)")
    return vec_norm_sq(vec_sub(v2, v1)) / (h_f * a_sum * det12)


def predict_cf_two_step_extrapolation(
    x0: Vec2,
    dx1: Vec2,
    dx2: Vec2,
    a0: Fraction,
    a1: Fraction,
    a_prime: Fraction,
) -> Vec2:
    """1-line 2-step commutator extrapolation: x0 + dx1 + ((a'-a0)/(a0+a1))*(dx2 - dx1)."""
    x0_v = _require_vec2(x0, "x0")
    v1 = _require_vec2(dx1, "dx1")
    v2 = _require_vec2(dx2, "dx2")
    a0_f = require_fraction(a0, "a0")
    a1_f = require_fraction(a1, "a1")
    ap_f = require_fraction(a_prime, "a_prime")
    a_sum = a0_f + a1_f
    if a_sum == 0:
        raise CounterfactualHolonomyError("DEGENERATE_ACTION_SUM", "a0 + a1 == 0 forbids commutator extrapolation")
    scale = (ap_f - a0_f) / a_sum
    return vec_add(x0_v, vec_add(v1, vec_scale(scale, vec_sub(v2, v1))))


def recover_multiplicative_ratio(s0: Fraction, s_h: Fraction, a: Fraction, a_prime: Fraction) -> Fraction:
    """Exact Appendix E.4 multiplicative ratio reuse s0 + (a'/a)*(s_h - s0)."""
    s0_f = require_fraction(s0, "s0")
    sh_f = require_fraction(s_h, "s_h")
    a_f = require_fraction(a, "a")
    ap_f = require_fraction(a_prime, "a_prime")
    if a_f == 0:
        raise CounterfactualHolonomyError("ZERO_FACTUAL_ACTION", "a == 0 unidentifiable in multiplicative channel")
    return s0_f + (ap_f / a_f) * (sh_f - s0_f)


def recover_mixed_add_mult_two_step(
    r1: Fraction,
    r2: Fraction,
    a0: Fraction,
    a1: Fraction,
    h: Fraction,
) -> tuple[Fraction, Fraction]:
    """Exact 2x2 inversion for mixed channel r_k = h*(eps_add + a_k*eps_mult)."""
    r1_f = require_fraction(r1, "r1")
    r2_f = require_fraction(r2, "r2")
    a0_f = require_fraction(a0, "a0")
    a1_f = require_fraction(a1, "a1")
    h_f = _require_pos_fraction(h, "h")
    da = a1_f - a0_f
    if da == 0:
        raise CounterfactualHolonomyError("SINGULAR_ACTION_PAIR", "a0 == a1 yields singular 2x2 system")
    eps_mult = (r2_f - r1_f) / (h_f * da)
    eps_add = (a1_f * r1_f - a0_f * r2_f) / (h_f * da)
    return eps_add, eps_mult


# ---------------------------------------------------------------------------
# Theorem 1: Exact Reproduction & Algebraic Audit of arXiv:2611.24778v1
# ---------------------------------------------------------------------------

def _xeps_vector_field(theta: int, c_val: Fraction, q: Fraction, _x: Vec2, eps: Vec2) -> Vec2:
    """Disturbance vector field X_eps(q, x) = (I_2 + 2*theta*C*q*J)*eps of Eq. (56)."""
    return vec_add(eps, vec_scale(Fraction(2 * theta) * c_val * q, mat_vec(J_MAT, eps)))


def certify_theorem1_paper_reproduction() -> dict[str, Any]:
    # 1. Exact time-h flow integration residual (degree-1 integrand => midpoint rule is exact)
    #    plus Lie bracket [X_a, X_eps] = (0, 2*theta*C*a*J*eps), explicit step-2 nilpotency,
    #    and Cayley SO(2,Q) gauge invariance.
    flow_cases: list[dict[str, Any]] = []
    eps_ref: Vec2 = (Fraction(3), Fraction(-5))
    x_zero: Vec2 = (Fraction(0), Fraction(0))
    for theta, c_val, q0_val, a_val, h_val in (
        (1, Fraction(1), Fraction(0), Fraction(-1), Fraction(1, 2)),
        (-1, Fraction(3, 2), Fraction(2, 5), Fraction(7, 3), Fraction(1, 4)),
        (1, Fraction(5, 3), Fraction(-3, 4), Fraction(2), Fraction(1, 3)),
    ):
        _, _, dx = chiral_flow_step(theta, c_val, q0_val, x_zero, a_val, h_val, eps_ref)
        # Exact polynomial integral via midpoint t = h/2: q(h/2) = q0 + a*h/2
        q_mid = q0_val + a_val * h_val / Fraction(2)
        v_mid = _xeps_vector_field(theta, c_val, q_mid, x_zero, eps_ref)
        dx_quad = vec_scale(h_val, v_mid)
        ode_residual_zero = dx == dx_quad

        # Lie bracket [X_a, X_eps] = D(X_eps)*X_a - D(X_a)*X_eps = (0, 2*theta*C*a*J*eps)
        bracket = vec_scale(Fraction(2 * theta) * c_val * a_val, mat_vec(J_MAT, eps_ref))
        xeps_0 = _xeps_vector_field(theta, c_val, q0_val, x_zero, eps_ref)
        xeps_1 = _xeps_vector_field(theta, c_val, q0_val + a_val, x_zero, eps_ref)
        xeps_2 = _xeps_vector_field(theta, c_val, q0_val + Fraction(2) * a_val, x_zero, eps_ref)
        b_q0 = vec_sub(xeps_1, xeps_0)
        b_q1 = vec_sub(xeps_2, xeps_1)
        bracket_exact = b_q0 == bracket
        # Explicit nested brackets: [[X_a, X_eps], X_a] == 0 and [[X_a, X_eps], X_eps] == 0
        nested_xa = vec_sub(b_q1, b_q0)
        nested_xeps = vec_sub(_xeps_vector_field(theta, c_val, q0_val, b_q0, eps_ref), xeps_0)
        step2_nilpotent_exact = all((nested_xa == x_zero, nested_xeps == x_zero))

        # Cayley SO(2, Q) gauge equivalence between theta = +1 and theta = -1
        u_mag = c_val * (Fraction(2) * q0_val + a_val * h_val)
        m_plus = chiral_flow_matrix(1, c_val, q0_val, a_val, h_val)
        m_minus = chiral_flow_matrix(-1, c_val, q0_val, a_val, h_val)
        r_mat = cayley_gauge_rotation(u_mag)
        cov_plus = mat_mul(m_plus, mat_transpose(m_plus))
        cov_minus = mat_mul(m_minus, mat_transpose(m_minus))
        cov_iso_expected = mat_scale(h_val * h_val * (Fraction(1) + u_mag * u_mag), I2_MAT)
        gauge_ok = all(
            (
                mat_mul(mat_transpose(r_mat), r_mat) == I2_MAT,
                mat_det(r_mat) == Fraction(1),
                mat_mul(m_minus, r_mat) == m_plus,
                cov_plus == cov_minus,
                cov_plus == cov_iso_expected,
            )
        )
        flow_cases.append(
            {
                "theta": theta,
                "C": format_rational(c_val),
                "q0": format_rational(q0_val),
                "a": format_rational(a_val),
                "h": format_rational(h_val),
                "ode_residual_zero": ode_residual_zero,
                "lie_bracket_exact": bracket_exact,
                "step2_nilpotent_exact": step2_nilpotent_exact,
                "cayley_so2_gauge_exact": gauge_ok,
                "isotropic_variance_factor": format_rational(Fraction(1) + u_mag * u_mag),
            }
        )

    # 2. Eq. (56) q0=0, a=-1, a'=+1 exact risk audit: T_R = 4*C^2*h^4 vs Bayes = 4*C^2*h^4/(1+k^2)
    minimax_cases: list[dict[str, Any]] = []
    eps_sq = vec_norm_sq(eps_ref)
    for c_val, h_val in (
        (Fraction(1), Fraction(1, 2)),
        (Fraction(1), Fraction(1, 4)),
        (Fraction(1), Fraction(1, 8)),
        (Fraction(3, 2), Fraction(1, 4)),
    ):
        k = c_val * h_val
        k2 = k * k
        shrink = (Fraction(1) - k2) / (Fraction(1) + k2)
        exp_rr = Fraction(4) * c_val * c_val * (h_val**4)
        exp_bayes = exp_rr / (Fraction(1) + k2)
        theta_checks: list[bool] = []
        for theta in (-1, 1):
            _, _, x_obs = chiral_flow_step(theta, c_val, Fraction(0), (Fraction(0), Fraction(0)), Fraction(-1), h_val, eps_ref)
            _, _, y_cf = chiral_flow_step(theta, c_val, Fraction(0), (Fraction(0), Fraction(0)), Fraction(1), h_val, eps_ref)
            err_rr_norm = vec_norm_sq(vec_sub(y_cf, x_obs)) / eps_sq
            g_bar = vec_scale(shrink, x_obs)
            err_bayes_norm = vec_norm_sq(vec_sub(y_cf, g_bar)) / eps_sq
            theta_checks.append(err_rr_norm == exp_rr)
            theta_checks.append(err_bayes_norm == exp_bayes)
        minimax_cases.append(
            {
                "C": format_rational(c_val),
                "h": format_rational(h_val),
                "k": format_rational(k),
                "shrinkage_factor": format_rational(shrink),
                "mse_residual_reuse": format_rational(exp_rr),
                "mse_bayes_midpoint": format_rational(exp_bayes),
                "strict_gap_ratio": format_rational(exp_rr / exp_bayes),
                "expected_one_plus_k2": format_rational(Fraction(1) + k2),
                "both_thetas_exact": all(theta_checks),
            }
        )

    # 3. Exact Pythagorean variance-matched residual transport improvement at q0 != 0 vs q0 == 0 tie
    vm_cases: list[dict[str, Any]] = []
    for label, q0_val, a_val, ap_val, rho_vm in (
        ("pythagorean_3_4_to_4_3", Fraction(1, 2), Fraction(-1, 4), Fraction(1, 3), Fraction(4, 3)),
        ("pythagorean_5_12_to_12_5", Fraction(1), Fraction(-19, 12), Fraction(2, 5), Fraction(12, 5)),
        ("symmetric_q0_zero_control", Fraction(0), Fraction(-1), Fraction(1), Fraction(1)),
    ):
        c_val = Fraction(1)
        h_val = Fraction(1)
        u = c_val * (Fraction(2) * q0_val + a_val * h_val)
        up = c_val * (Fraction(2) * q0_val + ap_val * h_val)
        rho_exact_sq = (rho_vm * rho_vm) == (Fraction(1) + up * up) / (Fraction(1) + u * u)
        alpha_bayes = (Fraction(1) + u * up) / (Fraction(1) + u * u)
        _, _, x_obs = chiral_flow_step(1, c_val, q0_val, (Fraction(0), Fraction(0)), a_val, h_val, eps_ref)
        _, _, y_cf = chiral_flow_step(1, c_val, q0_val, (Fraction(0), Fraction(0)), ap_val, h_val, eps_ref)
        mse_rr = vec_norm_sq(vec_sub(y_cf, x_obs)) / eps_sq
        mse_vm = vec_norm_sq(vec_sub(y_cf, vec_scale(rho_vm, x_obs))) / eps_sq
        mse_b = vec_norm_sq(vec_sub(y_cf, vec_scale(alpha_bayes, x_obs))) / eps_sq
        vm_cases.append(
            {
                "label": label,
                "q0": format_rational(q0_val),
                "u": format_rational(u),
                "u_prime": format_rational(up),
                "rho_vm": format_rational(rho_vm),
                "rho_vm_sq_exact": rho_exact_sq,
                "alpha_bayes": format_rational(alpha_bayes),
                "mse_bayes": format_rational(mse_b),
                "mse_vm": format_rational(mse_vm),
                "mse_rr": format_rational(mse_rr),
                "vm_strictly_beats_rr": mse_vm < mse_rr,
                "bayes_le_vm": mse_b <= mse_vm,
            }
        )

    t1_flags = (
        all(c["ode_residual_zero"] for c in flow_cases),
        all(c["lie_bracket_exact"] for c in flow_cases),
        all(c["step2_nilpotent_exact"] for c in flow_cases),
        all(c["cayley_so2_gauge_exact"] for c in flow_cases),
        all(c["both_thetas_exact"] for c in minimax_cases),
        all(c["rho_vm_sq_exact"] for c in vm_cases),
        all(c["bayes_le_vm"] for c in vm_cases),
        vm_cases[0]["vm_strictly_beats_rr"],
        vm_cases[1]["vm_strictly_beats_rr"],
        not vm_cases[2]["vm_strictly_beats_rr"],
    )
    return {
        "flow_and_gauge_cases": flow_cases,
        "minimax_gap_cases": minimax_cases,
        "variance_matched_transport_cases": vm_cases,
        "all_verified": all(t1_flags),
    }


# ---------------------------------------------------------------------------
# Theorem 2: Gauge-Stabilizer Anisotropy Theorem (Unpaired 1-Step Data)
# ---------------------------------------------------------------------------

def certify_theorem2_gauge_anisotropy() -> dict[str, Any]:
    eps_sample: Vec2 = (Fraction(7, 3), Fraction(-2, 5))
    diag_cases: list[dict[str, Any]] = []
    for theta, c_val, q0_val, a_val, ap_val, h_val, s1_sq, s2_sq in (
        (1, Fraction(1), Fraction(0), Fraction(-1), Fraction(1), Fraction(1, 2), Fraction(3), Fraction(1)),
        (-1, Fraction(5, 2), Fraction(1, 3), Fraction(-2), Fraction(3), Fraction(1, 4), Fraction(2, 5), Fraction(7, 4)),
        (1, Fraction(3, 4), Fraction(-1, 2), Fraction(5, 3), Fraction(-4, 3), Fraction(1, 3), Fraction(9), Fraction(2)),
    ):
        sig_eps: Mat2 = ((s1_sq, Fraction(0)), (Fraction(0), s2_sq))
        m_mat = chiral_flow_matrix(theta, c_val, q0_val, a_val, h_val)
        sig_dx = mat_mul(mat_mul(m_mat, sig_eps), mat_transpose(m_mat))
        w = Fraction(2) * q0_val + a_val * h_val
        expected_s12 = h_val * h_val * Fraction(theta) * c_val * w * (s1_sq - s2_sq)
        rec_diag = sig_dx[0][1] / (h_val * h_val * w * (s1_sq - s2_sq))
        rec_general = recover_theta_c_from_anisotropic_cov(sig_dx, sig_eps, q0_val, a_val, h_val)

        # Stabilizer collapse check: R(u) Sigma_eps R(u)^T != Sigma_eps
        r_mat = cayley_gauge_rotation(c_val * w)
        rot_sig = mat_mul(mat_mul(r_mat, sig_eps), mat_transpose(r_mat))
        stabilizer_broken = rot_sig != sig_eps

        # Zero-error counterfactual recovery vs nonzero T_R error
        _, _, dx_obs = chiral_flow_step(theta, c_val, q0_val, (Fraction(0), Fraction(0)), a_val, h_val, eps_sample)
        _, _, y_true = chiral_flow_step(theta, c_val, q0_val, (Fraction(0), Fraction(0)), ap_val, h_val, eps_sample)
        eps_hat = chiral_inverse_eps(rec_general, q0_val, a_val, h_val, dx_obs)
        rec_th = 1 if rec_general > 0 else -1
        _, _, y_hat = chiral_flow_step(rec_th, abs(rec_general), q0_val, (Fraction(0), Fraction(0)), ap_val, h_val, eps_hat)
        cf_err_sq = vec_norm_sq(vec_sub(y_true, y_hat))
        rr_err_sq = vec_norm_sq(vec_sub(y_true, dx_obs))

        diag_cases.append(
            {
                "theta": theta,
                "C": format_rational(c_val),
                "q0": format_rational(q0_val),
                "a": format_rational(a_val),
                "a_prime": format_rational(ap_val),
                "h": format_rational(h_val),
                "sigma1_sq": format_rational(s1_sq),
                "sigma2_sq": format_rational(s2_sq),
                "sigma12_observed": format_rational(sig_dx[0][1]),
                "sigma12_matches_formula": sig_dx[0][1] == expected_s12,
                "recovered_theta_c_diag": format_rational(rec_diag),
                "recovered_theta_c_trace": format_rational(rec_general),
                "exact_recovery": all((rec_diag == Fraction(theta) * c_val, rec_general == Fraction(theta) * c_val)),
                "stabilizer_broken": stabilizer_broken,
                "eps_recovered_exact": eps_hat == eps_sample,
                "cf_err_sq": format_rational(cf_err_sq),
                "rr_err_sq": format_rational(rr_err_sq),
            }
        )

    # Coordinate-free general non-diagonal SPD covariance matrices
    general_psd_cases: list[dict[str, Any]] = []
    for label, theta, c_val, q0_val, a_val, h_val, sig_eps in (
        (
            "rotated_spd_5_2_3",
            1,
            Fraction(7, 3),
            Fraction(-3, 5),
            Fraction(5, 3),
            Fraction(1, 4),
            ((Fraction(5), Fraction(2)), (Fraction(2), Fraction(3))),
        ),
        (
            "rotated_spd_7_m3_4",
            -1,
            Fraction(4, 5),
            Fraction(2, 7),
            Fraction(-3, 2),
            Fraction(1, 5),
            ((Fraction(7), Fraction(-3)), (Fraction(-3), Fraction(4))),
        ),
    ):
        m_mat = chiral_flow_matrix(theta, c_val, q0_val, a_val, h_val)
        sig_dx = mat_mul(mat_mul(m_mat, sig_eps), mat_transpose(m_mat))
        w = Fraction(2) * q0_val + a_val * h_val
        disc = mat_trace(sig_eps) ** 2 - Fraction(4) * mat_det(sig_eps)
        comm = mat_commutator(sig_dx, sig_eps)
        expected_comm = mat_scale(h_val * h_val * Fraction(theta) * c_val * w * disc, J_MAT)
        rec = recover_theta_c_from_anisotropic_cov(sig_dx, sig_eps, q0_val, a_val, h_val)
        general_psd_cases.append(
            {
                "label": label,
                "theta": theta,
                "C": format_rational(c_val),
                "discriminant_delta_lambda_sq": format_rational(disc),
                "commutator_identity_exact": comm == expected_comm,
                "recovered_theta_c": format_rational(rec),
                "exact_recovery": rec == Fraction(theta) * c_val,
            }
        )

    # Exact negative control: isotropic Sigma_eps = sigma^2 * I_2
    iso_sig: Mat2 = ((Fraction(4), Fraction(0)), (Fraction(0), Fraction(4)))
    m_iso = chiral_flow_matrix(1, Fraction(2), Fraction(1, 3), Fraction(1), Fraction(1, 2))
    sig_dx_iso = mat_mul(mat_mul(m_iso, iso_sig), mat_transpose(m_iso))
    r_iso = cayley_gauge_rotation(Fraction(2) * (Fraction(2, 3) + Fraction(1, 2)))
    iso_rejected = False
    try:
        recover_theta_c_from_anisotropic_cov(sig_dx_iso, iso_sig, Fraction(1, 3), Fraction(1), Fraction(1, 2))
    except CounterfactualHolonomyError as exc:
        iso_rejected = exc.code == "ISOTROPIC_UNIDENTIFIABLE"
    iso_control = {
        "sigma12_zero": sig_dx_iso[0][1] == 0,
        "commutator_zero": mat_commutator(sig_dx_iso, iso_sig) == ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))),
        "stabilizer_preserves_cov": mat_mul(mat_mul(r_iso, iso_sig), mat_transpose(r_iso)) == iso_sig,
        "recovery_rejected_cleanly": iso_rejected,
    }

    t2_flags = (
        all(c["sigma12_matches_formula"] for c in diag_cases),
        all(c["exact_recovery"] for c in diag_cases),
        all(c["stabilizer_broken"] for c in diag_cases),
        all(c["eps_recovered_exact"] for c in diag_cases),
        all(c["cf_err_sq"] == "0" for c in diag_cases),
        all(c["rr_err_sq"] != "0" for c in diag_cases),
        all(c["commutator_identity_exact"] for c in general_psd_cases),
        all(c["exact_recovery"] for c in general_psd_cases),
        iso_control["sigma12_zero"],
        iso_control["commutator_zero"],
        iso_control["stabilizer_preserves_cov"],
        iso_control["recovery_rejected_cleanly"],
    )
    return {
        "diagonal_anisotropy_cases": diag_cases,
        "general_psd_coordinate_free_cases": general_psd_cases,
        "isotropic_negative_control": iso_control,
        "all_verified": all(t2_flags),
    }


# ---------------------------------------------------------------------------
# Theorem 3: 2-Step Signed-Area Recovery, Nonlinear O(h^6) & Curved Encoder
# ---------------------------------------------------------------------------

def _nonlinear_cross_channel_step(
    theta: int,
    c_val: Fraction,
    d_val: Fraction,
    q0: Fraction,
    a: Fraction,
    h: Fraction,
    eps: Vec2,
) -> Vec2:
    """Exact time-h integral of dq/dt=a, dx/dt=(I + 2*theta*C*q*J + 3*D*q^2*K)*eps."""
    i1 = h * (Fraction(2) * q0 + a * h)
    i2 = h * (Fraction(3) * q0 * q0 + Fraction(3) * q0 * a * h + a * a * h * h)
    je = mat_vec(J_MAT, eps)
    ke = mat_vec(K_SHEAR_MAT, eps)
    return vec_add(
        vec_scale(h, eps),
        vec_add(vec_scale(Fraction(theta) * c_val * i1, je), vec_scale(d_val * i2, ke)),
    )


def _self_advecting_step(
    theta: int,
    c_val: Fraction,
    beta: Fraction,
    q0: Fraction,
    x0: Vec2,
    a: Fraction,
    h: Fraction,
    eps: Vec2,
) -> tuple[Fraction, Vec2, Vec2]:
    """Exact integrable ODE with Dg.g != 0: dq=a, dx1=e1, dx2=e2 + 2*theta*C*q*e1 + 2*beta*x1*e1."""
    dx1 = h * eps[0]
    dx2 = (
        h * eps[1]
        + Fraction(theta) * c_val * h * (Fraction(2) * q0 + a * h) * eps[0]
        + beta * h * (Fraction(2) * x0[0] + h * eps[0]) * eps[0]
    )
    dx = (dx1, dx2)
    return q0 + a * h, vec_add(x0, dx), dx


def certify_theorem3_two_step_holonomy() -> dict[str, Any]:
    # Part A: Exact 2-step rational signed-area recovery (general q0 + universal q0-free)
    two_step_cases: list[dict[str, Any]] = []
    eps_grid: tuple[Vec2, ...] = ((Fraction(3), Fraction(-5)), (Fraction(-2, 3), Fraction(7, 4)))
    for idx, (theta, c_val, q0_val, a0_val, a1_val, ap_val, h_val) in enumerate(
        (
            (1, Fraction(1), Fraction(0), Fraction(1), Fraction(2), Fraction(-1), Fraction(1, 2)),
            (-1, Fraction(3, 2), Fraction(0), Fraction(-1), Fraction(4), Fraction(2), Fraction(1, 4)),
            (1, Fraction(5, 3), Fraction(-2, 3), Fraction(2), Fraction(-1), Fraction(7, 3), Fraction(1, 5)),
            (-1, Fraction(7, 4), Fraction(4, 5), Fraction(-3, 2), Fraction(5, 2), Fraction(-5, 2), Fraction(1, 3)),
        )
    ):
        eps = eps_grid[idx % len(eps_grid)]
        x0: Vec2 = (Fraction(1, 7), Fraction(-3, 5))
        q1, x1, dx1 = chiral_flow_step(theta, c_val, q0_val, x0, a0_val, h_val, eps)
        _, _, dx2 = chiral_flow_step(theta, c_val, q1, x1, a1_val, h_val, eps)
        _, y_true, _ = chiral_flow_step(theta, c_val, q0_val, x0, ap_val, h_val, eps)

        det12 = vec_det(dx1, dx2)
        exp_det12 = Fraction(theta) * c_val * (h_val**3) * (a0_val + a1_val) * vec_norm_sq(eps)
        ndiff_sq_norms = vec_norm_sq(dx2) - vec_norm_sq(dx1)
        w_sum = Fraction(4) * q0_val + (Fraction(3) * a0_val + a1_val) * h_val
        exp_ndiff_sq_norms = c_val * c_val * (h_val**3) * (a0_val + a1_val) * w_sum * vec_norm_sq(eps)

        rec_nd = recover_theta_c_two_step_norm_diff(dx1, dx2, q0_val, a0_val, a1_val, h_val)
        rec_univ = recover_theta_c_two_step_universal(dx1, dx2, a0_val, a1_val, h_val)
        eps_hat = chiral_inverse_eps(rec_univ, q0_val, a0_val, h_val, dx1)
        rec_th = 1 if rec_univ > 0 else -1
        _, y_hat_inv, _ = chiral_flow_step(rec_th, abs(rec_univ), q0_val, x0, ap_val, h_val, eps_hat)
        y_hat_ext = predict_cf_two_step_extrapolation(x0, dx1, dx2, a0_val, a1_val, ap_val)

        two_step_cases.append(
            {
                "theta": theta,
                "C": format_rational(c_val),
                "q0": format_rational(q0_val),
                "a0": format_rational(a0_val),
                "a1": format_rational(a1_val),
                "a_prime": format_rational(ap_val),
                "h": format_rational(h_val),
                "det12_identity_exact": det12 == exp_det12,
                "norm_diff_identity_exact": ndiff_sq_norms == exp_ndiff_sq_norms,
                "recovered_theta_c_norm_diff": format_rational(rec_nd),
                "recovered_theta_c_universal": format_rational(rec_univ),
                "exact_recovery": all((rec_nd == Fraction(theta) * c_val, rec_univ == Fraction(theta) * c_val)),
                "eps_recovered_exact": eps_hat == eps,
                "cf_err_sq_inversion": format_rational(vec_norm_sq(vec_sub(y_true, y_hat_inv))),
                "cf_err_sq_extrapolation": format_rational(vec_norm_sq(vec_sub(y_true, y_hat_ext))),
            }
        )

    # Part B: Exact degenerate-action boundary controls
    eps_b: Vec2 = (Fraction(3), Fraction(-5))
    # B1: a0 + a1 == 0
    q1_b1, x1_b1, dx1_b1 = chiral_flow_step(1, Fraction(2), Fraction(1, 2), (Fraction(0), Fraction(0)), Fraction(2), Fraction(1, 2), eps_b)
    _, _, dx2_b1 = chiral_flow_step(1, Fraction(2), q1_b1, x1_b1, Fraction(-2), Fraction(1, 2), eps_b)
    b1_nd_rej = False
    try:
        recover_theta_c_two_step_norm_diff(dx1_b1, dx2_b1, Fraction(1, 2), Fraction(2), Fraction(-2), Fraction(1, 2))
    except CounterfactualHolonomyError as exc:
        b1_nd_rej = exc.code == "DEGENERATE_ACTION_SUM"
    b1_univ_rej = False
    try:
        recover_theta_c_two_step_universal(dx1_b1, dx2_b1, Fraction(2), Fraction(-2), Fraction(1, 2))
    except CounterfactualHolonomyError as exc:
        b1_univ_rej = exc.code == "DEGENERATE_ACTION_SUM"

    # B2: 4*q0 + (3*a0 + a1)*h == 0 with a0 + a1 != 0 (symmetric reflection across q=0)
    # q0 = -1, h = 1, a0 = 1, a1 = 1, theta = -1, C = 3/2
    q1_b2, x1_b2, dx1_b2 = chiral_flow_step(-1, Fraction(3, 2), Fraction(-1), (Fraction(0), Fraction(0)), Fraction(1), Fraction(1), eps_b)
    _, _, dx2_b2 = chiral_flow_step(-1, Fraction(3, 2), q1_b2, x1_b2, Fraction(1), Fraction(1), eps_b)
    det12_b2 = vec_det(dx1_b2, dx2_b2)
    b2_norm_diff_zero = (vec_norm_sq(dx2_b2) - vec_norm_sq(dx1_b2)) == 0
    b2_theta_sign_recovered = (1 if (Fraction(2) * det12_b2) > 0 else -1) == -1
    b2_nd_rej = False
    try:
        recover_theta_c_two_step_norm_diff(dx1_b2, dx2_b2, Fraction(-1), Fraction(1), Fraction(1), Fraction(1))
    except CounterfactualHolonomyError as exc:
        b2_nd_rej = exc.code == "SYMMETRIC_NORM_DEGENERACY"
    b2_univ_rec = recover_theta_c_two_step_universal(dx1_b2, dx2_b2, Fraction(1), Fraction(1), Fraction(1))

    boundary_controls = {
        "a0_plus_a1_zero": {
            "dx2_equals_dx1": dx2_b1 == dx1_b1,
            "det12_zero": vec_det(dx1_b1, dx2_b1) == 0,
            "norm_diff_rejected": b1_nd_rej,
            "universal_rejected": b1_univ_rej,
        },
        "symmetric_reflection_4q0_plus_3a0_plus_a1_h_zero": {
            "norm_diff_identically_zero": b2_norm_diff_zero,
            "theta_sign_still_identified": b2_theta_sign_recovered,
            "norm_diff_formula_rejected": b2_nd_rej,
            "universal_formula_recovers_exact_theta_c": b2_univ_rec == Fraction(-3, 2),
            "recovered_theta_c_universal": format_rational(b2_univ_rec),
        },
    }

    # Part C: Smooth nonlinear cross-channel O(h^4) -> O(h^6) MSE + Dg.g != 0 obstruction
    nl_q0 = Fraction(1, 3)
    nl_a0, nl_a1, nl_ap = Fraction(1), Fraction(2), Fraction(-2)
    nl_c, nl_d = Fraction(3, 2), Fraction(1, 2)
    nl_scaling: list[dict[str, Any]] = []
    for h_val in (Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(1, 16)):
        dx1_nl = _nonlinear_cross_channel_step(1, nl_c, nl_d, nl_q0, nl_a0, h_val, eps_b)
        dx2_nl = _nonlinear_cross_channel_step(1, nl_c, nl_d, nl_q0 + nl_a0 * h_val, nl_a1, h_val, eps_b)
        y_nl_true = _nonlinear_cross_channel_step(1, nl_c, nl_d, nl_q0, nl_ap, h_val, eps_b)
        y_nl_2step = predict_cf_two_step_extrapolation((Fraction(0), Fraction(0)), dx1_nl, dx2_nl, nl_a0, nl_a1, nl_ap)
        err_rr_sq = vec_norm_sq(vec_sub(y_nl_true, dx1_nl))
        err_2step = vec_sub(y_nl_true, y_nl_2step)
        err_2step_sq = vec_norm_sq(err_2step)
        expected_rem = vec_scale(nl_d * (h_val**3) * (nl_ap - nl_a0) * (nl_ap - nl_a0 - nl_a1), mat_vec(K_SHEAR_MAT, eps_b))
        nl_scaling.append(
            {
                "h": format_rational(h_val),
                "rr_err_sq_div_h4": format_rational(err_rr_sq / (h_val**4)),
                "two_step_err_sq_div_h6": format_rational(err_2step_sq / (h_val**6)),
                "exact_h3_remainder_identity": err_2step == expected_rem,
            }
        )
    # Resonance cancellation at a' = a0 + a1 => exact 0 error even for quadratic coupling!
    h_res = Fraction(1, 4)
    dx1_res = _nonlinear_cross_channel_step(1, nl_c, nl_d, nl_q0, nl_a0, h_res, eps_b)
    dx2_res = _nonlinear_cross_channel_step(1, nl_c, nl_d, nl_q0 + nl_a0 * h_res, nl_a1, h_res, eps_b)
    y_res_true = _nonlinear_cross_channel_step(1, nl_c, nl_d, nl_q0, nl_a0 + nl_a1, h_res, eps_b)
    y_res_2step = predict_cf_two_step_extrapolation((Fraction(0), Fraction(0)), dx1_res, dx2_res, nl_a0, nl_a1, nl_a0 + nl_a1)
    nl_h6_const = len({row["two_step_err_sq_div_h6"] for row in nl_scaling}) == 1

    # Self-advection obstruction Dg.g != 0 (beta != 0) & 3-step exact cancellation
    sa_h = Fraction(1, 4)
    sa_beta = Fraction(3, 5)
    sa_c = Fraction(2)
    sa_q0 = Fraction(1, 2)
    sa_x0: Vec2 = (Fraction(1), Fraction(-1))
    sa_a0, sa_a1, sa_a2, sa_ap = Fraction(1), Fraction(2), Fraction(4), Fraction(-1)
    q1_sa, x1_sa, dx1_sa = _self_advecting_step(1, sa_c, sa_beta, sa_q0, sa_x0, sa_a0, sa_h, eps_b)
    q2_sa, x2_sa, dx2_sa = _self_advecting_step(1, sa_c, sa_beta, q1_sa, x1_sa, sa_a1, sa_h, eps_b)
    _, _, dx3_sa = _self_advecting_step(1, sa_c, sa_beta, q2_sa, x2_sa, sa_a2, sa_h, eps_b)
    _, y_sa_true, _ = _self_advecting_step(1, sa_c, sa_beta, sa_q0, sa_x0, sa_ap, sa_h, eps_b)
    y_sa_2step = predict_cf_two_step_extrapolation(sa_x0, dx1_sa, dx2_sa, sa_a0, sa_a1, sa_ap)
    sa_2step_err_x2 = y_sa_true[1] - y_sa_2step[1]
    sa_expected_obstruction = -((sa_ap - sa_a0) / (sa_a0 + sa_a1)) * Fraction(2) * sa_beta * sa_h * sa_h * eps_b[0] * eps_b[0]
    # 3-step second difference eliminates 2*beta*h^2*e1^2 identically:
    # (dx3_2 - dx2_2) - (dx2_2 - dx1_2) = theta*C*h^2*(a2 - a0)*e1
    d2_x2 = (dx3_sa[1] - dx2_sa[1]) - (dx2_sa[1] - dx1_sa[1])
    slope_3step = d2_x2 / (sa_a2 - sa_a0)
    y_sa_3step = (sa_x0[0] + dx1_sa[0], sa_x0[1] + dx1_sa[1] + (sa_ap - sa_a0) * slope_3step)

    # Part D: Exact curved-encoder D^2 E obstruction in JEPA latent space
    s0_e = Fraction(2, 3)
    a_e, ap_e, h_e = Fraction(1), Fraction(-2), Fraction(1, 4)
    eps_e = Fraction(5, 7)
    sig_sq_e = Fraction(9, 4)
    kappa = Fraction(3, 5)
    # Strictly additive physics: s_h(a, eps) = s0 + h*a + h*eps
    s_obs = s0_e + h_e * a_e + h_e * eps_e
    s_cf = s0_e + h_e * ap_e + h_e * eps_e
    state_rr_err = s_cf - (s_obs + h_e * (ap_e - a_e))
    # Curved encoder E(s) = (s, kappa * s^2), E[E_2(s_h(a))] = kappa*(s0+h*a)^2 + kappa*h^2*sig_sq_e
    z2_obs = kappa * s_obs * s_obs
    z2_cf = kappa * s_cf * s_cf
    mu_z2_obs = kappa * (s0_e + h_e * a_e) ** 2 + kappa * h_e * h_e * sig_sq_e
    mu_z2_cf = kappa * (s0_e + h_e * ap_e) ** 2 + kappa * h_e * h_e * sig_sq_e
    z2_rr = z2_obs + mu_z2_cf - mu_z2_obs
    latent_err = z2_cf - z2_rr
    expected_d2e_err = Fraction(2) * kappa * h_e * h_e * (ap_e - a_e) * eps_e
    latent_mse = Fraction(4) * kappa * kappa * (h_e**4) * ((ap_e - a_e) ** 2) * sig_sq_e
    # Flat/affine encoder control computed explicitly at kappa_flat = 0
    kappa_flat = Fraction(0)
    z2_flat_obs = kappa_flat * s_obs * s_obs
    z2_flat_cf = kappa_flat * s_cf * s_cf
    mu_z2_flat_obs = kappa_flat * (s0_e + h_e * a_e) ** 2 + kappa_flat * h_e * h_e * sig_sq_e
    mu_z2_flat_cf = kappa_flat * (s0_e + h_e * ap_e) ** 2 + kappa_flat * h_e * h_e * sig_sq_e
    flat_latent_err = z2_flat_cf - (z2_flat_obs + mu_z2_flat_cf - mu_z2_flat_obs)

    curved_encoder = {
        "kappa": format_rational(kappa),
        "state_space_rr_err": format_rational(state_rr_err),
        "latent_rr_err": format_rational(latent_err),
        "expected_h2_d2e_err": format_rational(expected_d2e_err),
        "d2e_identity_exact": all((latent_err == expected_d2e_err, latent_err != 0)),
        "latent_mse_h4": format_rational(latent_mse),
        "flat_encoder_control_zero": flat_latent_err == 0,
    }

    t3_flags = (
        all(c["det12_identity_exact"] for c in two_step_cases),
        all(c["norm_diff_identity_exact"] for c in two_step_cases),
        all(c["exact_recovery"] for c in two_step_cases),
        all(c["eps_recovered_exact"] for c in two_step_cases),
        all(c["cf_err_sq_inversion"] == "0" for c in two_step_cases),
        all(c["cf_err_sq_extrapolation"] == "0" for c in two_step_cases),
        boundary_controls["a0_plus_a1_zero"]["dx2_equals_dx1"],
        boundary_controls["a0_plus_a1_zero"]["det12_zero"],
        boundary_controls["a0_plus_a1_zero"]["norm_diff_rejected"],
        boundary_controls["a0_plus_a1_zero"]["universal_rejected"],
        boundary_controls["symmetric_reflection_4q0_plus_3a0_plus_a1_h_zero"]["norm_diff_identically_zero"],
        boundary_controls["symmetric_reflection_4q0_plus_3a0_plus_a1_h_zero"]["theta_sign_still_identified"],
        boundary_controls["symmetric_reflection_4q0_plus_3a0_plus_a1_h_zero"]["norm_diff_formula_rejected"],
        boundary_controls["symmetric_reflection_4q0_plus_3a0_plus_a1_h_zero"]["universal_formula_recovers_exact_theta_c"],
        nl_h6_const,
        all(r["exact_h3_remainder_identity"] for r in nl_scaling),
        y_res_true == y_res_2step,
        sa_2step_err_x2 == sa_expected_obstruction,
        sa_2step_err_x2 != 0,
        y_sa_3step == y_sa_true,
        curved_encoder["d2e_identity_exact"],
        state_rr_err == 0,
    )
    return {
        "two_step_isotropic_cases": two_step_cases,
        "degenerate_boundary_controls": boundary_controls,
        "nonlinear_commutator_h6_scaling": {
            "rows": nl_scaling,
            "h6_coefficient_constant_exact": nl_h6_const,
            "resonance_ap_eq_a0_plus_a1_zero_error": y_res_true == y_res_2step,
        },
        "self_advection_dg_g_obstruction": {
            "two_step_err_x2": format_rational(sa_2step_err_x2),
            "expected_obstruction": format_rational(sa_expected_obstruction),
            "obstruction_identity_exact": all((sa_2step_err_x2 == sa_expected_obstruction, sa_2step_err_x2 != 0)),
            "three_step_exact_cancellation": y_sa_3step == y_sa_true,
        },
        "curved_encoder_d2e_obstruction": curved_encoder,
        "all_verified": all(t3_flags),
    }


# ---------------------------------------------------------------------------
# Theorem 4: Multiplicative & Mixed Additive-Multiplicative Steelman (App E.4)
# ---------------------------------------------------------------------------

def certify_theorem4_multiplicative_steelman() -> dict[str, Any]:
    # 1. Pure multiplicative channel ds/dt = a * eps
    pure_cases: list[dict[str, Any]] = []
    for s0_val, a_val, ap_val, h_val, eps_val in (
        (Fraction(2), Fraction(3, 2), Fraction(-5, 4), Fraction(1, 4), Fraction(7, 3)),
        (Fraction(-1, 3), Fraction(-2), Fraction(3), Fraction(1, 8), Fraction(-5, 2)),
    ):
        s_obs = s0_val + h_val * a_val * eps_val
        s_cf = s0_val + h_val * ap_val * eps_val
        # Additive RR (mu(a) = s0 for zero-mean eps) -> s_hat_add = s_obs
        add_err = s_cf - s_obs
        expected_add_err = h_val * (ap_val - a_val) * eps_val
        mult_hat = recover_multiplicative_ratio(s0_val, s_obs, a_val, ap_val)
        pure_cases.append(
            {
                "s0": format_rational(s0_val),
                "a": format_rational(a_val),
                "a_prime": format_rational(ap_val),
                "h": format_rational(h_val),
                "additive_rr_err": format_rational(add_err),
                "additive_rr_h1_error_exact": all((add_err == expected_add_err, add_err != 0)),
                "multiplicative_ratio_err": format_rational(s_cf - mult_hat),
                "multiplicative_exact_zero": s_cf == mult_hat,
            }
        )

    zero_a_rejected = False
    try:
        recover_multiplicative_ratio(Fraction(1), Fraction(1), Fraction(0), Fraction(2))
    except CounterfactualHolonomyError as exc:
        zero_a_rejected = exc.code == "ZERO_FACTUAL_ACTION"

    # 2. Mixed additive + multiplicative channel ds/dt = v0*a + eps_add + a*eps_mult
    mixed_cases: list[dict[str, Any]] = []
    for s0_val, v0_val, a0_val, a1_val, ap_val, h_val, e_add, e_mult in (
        (Fraction(1), Fraction(3), Fraction(1), Fraction(-2), Fraction(5, 2), Fraction(1, 4), Fraction(7, 5), Fraction(-3, 2)),
        (Fraction(-2, 5), Fraction(-1, 2), Fraction(2, 3), Fraction(5, 3), Fraction(-1), Fraction(1, 5), Fraction(-4, 3), Fraction(9, 4)),
    ):
        ds1 = h_val * (v0_val * a0_val + e_add + a0_val * e_mult)
        ds2 = h_val * (v0_val * a1_val + e_add + a1_val * e_mult)
        r1 = ds1 - h_val * v0_val * a0_val
        r2 = ds2 - h_val * v0_val * a1_val
        s_cf = s0_val + h_val * (v0_val * ap_val + e_add + ap_val * e_mult)
        # 1-step additive reuse fails & 1-step multiplicative ratio fails
        s1_add_hat = s0_val + ds1 + h_val * v0_val * (ap_val - a0_val)
        s1_mult_hat = s0_val + h_val * v0_val * ap_val + (ap_val / a0_val) * r1
        # 2-step 2x2 exact inversion
        hat_add, hat_mult = recover_mixed_add_mult_two_step(r1, r2, a0_val, a1_val, h_val)
        s_hat_2step = s0_val + h_val * (v0_val * ap_val + hat_add + ap_val * hat_mult)
        mixed_cases.append(
            {
                "a0": format_rational(a0_val),
                "a1": format_rational(a1_val),
                "a_prime": format_rational(ap_val),
                "h": format_rational(h_val),
                "det_2x2": format_rational(h_val * h_val * (a1_val - a0_val)),
                "one_step_add_err": format_rational(s_cf - s1_add_hat),
                "one_step_mult_err": format_rational(s_cf - s1_mult_hat),
                "recovered_eps_add": format_rational(hat_add),
                "recovered_eps_mult": format_rational(hat_mult),
                "exact_recovery": all((hat_add == e_add, hat_mult == e_mult)),
                "two_step_cf_err": format_rational(s_cf - s_hat_2step),
            }
        )

    # 3. Exact singular negative control (a0 == a1) with explicit non-identifiable witness
    sing_a, sing_ap, sing_h = Fraction(2), Fraction(-3), Fraction(1, 2)
    e_add_1, e_mult_1 = Fraction(5), Fraction(3)
    delta = Fraction(7)
    e_add_2, e_mult_2 = e_add_1 + delta * sing_a, e_mult_1 - delta
    r_sing_1 = sing_h * (e_add_1 + sing_a * e_mult_1)
    r_sing_2 = sing_h * (e_add_2 + sing_a * e_mult_2)
    cf_div = sing_h * (e_add_2 + sing_ap * e_mult_2) - sing_h * (e_add_1 + sing_ap * e_mult_1)
    sing_rejected = False
    try:
        recover_mixed_add_mult_two_step(r_sing_1, r_sing_1, sing_a, sing_a, sing_h)
    except CounterfactualHolonomyError as exc:
        sing_rejected = exc.code == "SINGULAR_ACTION_PAIR"

    singular_control = {
        "factual_residuals_identical": r_sing_1 == r_sing_2,
        "counterfactual_divergence": format_rational(cf_div),
        "expected_divergence": format_rational(sing_h * (sing_a - sing_ap) * delta),
        "divergence_exact_nonzero": all((cf_div == sing_h * (sing_a - sing_ap) * delta, cf_div != 0)),
        "inversion_rejected_cleanly": sing_rejected,
    }

    t4_flags = (
        all(c["additive_rr_h1_error_exact"] for c in pure_cases),
        all(c["multiplicative_exact_zero"] for c in pure_cases),
        zero_a_rejected,
        all(c["exact_recovery"] for c in mixed_cases),
        all(c["two_step_cf_err"] == "0" for c in mixed_cases),
        all(c["one_step_add_err"] != "0" for c in mixed_cases),
        all(c["one_step_mult_err"] != "0" for c in mixed_cases),
        singular_control["factual_residuals_identical"],
        singular_control["divergence_exact_nonzero"],
        singular_control["inversion_rejected_cleanly"],
    )
    return {
        "pure_multiplicative_cases": pure_cases,
        "zero_action_control_rejected": zero_a_rejected,
        "mixed_two_step_cases": mixed_cases,
        "singular_a0_eq_a1_control": singular_control,
        "all_verified": all(t4_flags),
    }


# ---------------------------------------------------------------------------
# Canonical Certificate Builder & Validator
# ---------------------------------------------------------------------------

def build_standalone_certificate() -> dict[str, Any]:
    t1 = certify_theorem1_paper_reproduction()
    t2 = certify_theorem2_gauge_anisotropy()
    t3 = certify_theorem3_two_step_holonomy()
    t4 = certify_theorem4_multiplicative_steelman()
    payload: dict[str, Any] = {
        "source_paper": "arXiv:2611.24778v1",
        "theorem1_paper_reproduction": t1,
        "theorem2_gauge_anisotropy": t2,
        "theorem3_two_step_holonomy": t3,
        "theorem4_multiplicative_steelman": t4,
        "summary": {
            "all_theorems_verified": all(
                (t1["all_verified"], t2["all_verified"], t3["all_verified"], t4["all_verified"])
            ),
            "float_count_on_trust_path": 0,
            "bare_assert_count": 0,
            "rng_calls": 0,
        },
    }
    payload_sha = sha256_canonical(payload)
    outer_no_cert_sha = {
        "schema": SCHEMA_VERSION,
        "track_id": TRACK_ID,
        "payload_sha256": payload_sha,
        "payload": payload,
    }
    cert_sha = sha256_canonical(outer_no_cert_sha)
    return {
        "schema": SCHEMA_VERSION,
        "track_id": TRACK_ID,
        "payload_sha256": payload_sha,
        "certificate_sha256": cert_sha,
        "payload": payload,
    }


def validate_certificate_payload(cert: Any, *, full_replay: bool = True) -> dict[str, Any]:
    require_bool(full_replay, "full_replay")
    if type(cert) is not dict:
        raise CounterfactualHolonomyError("INVALID_CERT_TYPE", "certificate must be exact dict")
    _validate_json_tree_iterative(cert)
    if frozenset(cert.keys()) != _CERT_KEYS:
        raise CounterfactualHolonomyError("INVALID_CERT_KEYS", "certificate top-level keys mismatch")
    if cert["schema"] != SCHEMA_VERSION:
        raise CounterfactualHolonomyError("INVALID_SCHEMA", "certificate schema mismatch")
    if cert["track_id"] != TRACK_ID:
        raise CounterfactualHolonomyError("INVALID_TRACK_ID", "certificate track_id mismatch")
    if type(cert["payload"]) is not dict:
        raise CounterfactualHolonomyError("INVALID_PAYLOAD_TYPE", "certificate payload must be exact dict")

    claimed_p_sha = require_sha256_hex(cert["payload_sha256"], "payload_sha256")
    claimed_c_sha = require_sha256_hex(cert["certificate_sha256"], "certificate_sha256")

    actual_p_sha = sha256_canonical(cert["payload"])
    if not hmac.compare_digest(claimed_p_sha, actual_p_sha):
        raise CounterfactualHolonomyError("PAYLOAD_SHA256_MISMATCH", "payload_sha256 digest mismatch")

    outer_no_cert_sha = {
        "schema": cert["schema"],
        "track_id": cert["track_id"],
        "payload_sha256": claimed_p_sha,
        "payload": cert["payload"],
    }
    actual_c_sha = sha256_canonical(outer_no_cert_sha)
    if not hmac.compare_digest(claimed_c_sha, actual_c_sha):
        raise CounterfactualHolonomyError("CERT_SHA256_MISMATCH", "certificate_sha256 digest mismatch")

    if full_replay:
        ref = build_standalone_certificate()
        if not hmac.compare_digest(actual_p_sha, ref["payload_sha256"]):
            raise CounterfactualHolonomyError("REPLAY_MISMATCH", "certificate payload disagrees with deterministic replay")

    return {
        "valid": True,
        "schema": SCHEMA_VERSION,
        "track_id": TRACK_ID,
        "payload_sha256": actual_p_sha,
        "certificate_sha256": actual_c_sha,
        "full_replay": full_replay,
    }
