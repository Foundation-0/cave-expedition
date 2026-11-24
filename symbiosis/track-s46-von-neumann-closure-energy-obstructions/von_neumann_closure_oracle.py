"""Track S46 (Portal 46): Exact Pure-Z/Q Oracle for Planetary-Scale Energy-Hierarchy
Obstructions, Von Neumann/Leontief Industrial Closure, Schur Vitamin Bottleneck,
Radiative Heat-Rejection Ceiling, and Eigen Metrology Error-Threshold.

Certifies four exact pure-Z/Q pillars with zero IEEE-754 floating-point arithmetic:
  1. Mars 1-bar atmospheric mass, gravitational binding energy U_grav, chemical/orbital
     specific-energy hierarchy, and the >76x..>615x nuclear-transmutation obstruction.
  2. Exact Q^{4x4} Von Neumann / Leontief Hawkins-Simon industrial closure (productive
     self-compounding A_good with rho(A_good) <= 3/5 < 1 and positive inverse (I-A)^{-1} > 0
     vs non-productive deficit control A_bad with rho(A_bad) = 23/20 > 1).
  3. Exact Q^{5x5} Schur-complement vitamin import-leverage bottleneck S_VV = (1 - A_VV)
     - A_VL (I - A_LL)^{-1} A_LV: proving autonomous closure fails when S_VV < 0 despite
     locally productive bulk, and resumes under design-for-closure (S_VV' > 0 or V -> empty).
  4. Exact pi-free Stefan-Boltzmann O(R^3)/O(R^2) radiative bifurcation (with k^3 swarm
     restoration) and discrete Eigen quasispecies error-catastrophe recursion proving
     fail-closed physical metrology (sigma > 1/Q) is necessary for self-copying stability.

100% pure Python 3 stdlib (int, fractions.Fraction).
Zero IEEE-754 floats, zero float() calls, zero bare asserts, zero .isdigit(), zero RNG.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Sequence

TRACK_ID = "TRACK-S46-VON-NEUMANN-CLOSURE-ENERGY"
SCHEMA_VERSION = "aletheia.von_neumann_closure_energy.v1"
MAX_INT_BITS = 3_321
MAX_INT_DIGITS = 1_000
MAX_RATIONAL_BITS = 3_321


class VonNeumannClosureError(ValueError):
    """Typed fail-closed error for all Track S46 oracle, linear-algebra, and Zone-B checks."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.detail = message


# ============================================================================
# 1. Strict Fail-Closed Primitives (Binding 3,321-bit Cap, Zero Floats)
# ============================================================================

def require_ok(cond: bool, code: str, message: str) -> None:
    if type(cond) is not bool:
        raise VonNeumannClosureError("INVALID_CONDITION_TYPE", f"{code}: exact bool required")
    if not cond:
        raise VonNeumannClosureError(code, message)


def require_exact_bool(val: Any, label: str = "bool") -> bool:
    if type(val) is not bool:
        raise VonNeumannClosureError("INVALID_BOOL_TYPE", f"{label} must be exact bool")
    return val


def require_exact_int(
    val: Any,
    label: str = "int",
    *,
    lo: int | None = None,
    hi: int | None = None,
) -> int:
    if type(val) is not int:
        raise VonNeumannClosureError("INVALID_INT_TYPE", f"{label} must be exact int")
    if val.bit_length() > MAX_INT_BITS:
        raise VonNeumannClosureError("INT_BIT_LIMIT", f"{label} exceeds {MAX_INT_BITS}-bit cap")
    if lo is not None:
        if type(lo) is not int:
            raise VonNeumannClosureError("INVALID_BOUND_TYPE", f"{label}.lo must be exact int")
        if val < lo:
            raise VonNeumannClosureError("INT_OUT_OF_RANGE", f"{label} must be >= {lo}")
    if hi is not None:
        if type(hi) is not int:
            raise VonNeumannClosureError("INVALID_BOUND_TYPE", f"{label}.hi must be exact int")
        if val > hi:
            raise VonNeumannClosureError("INT_OUT_OF_RANGE", f"{label} must be <= {hi}")
    return val


def require_exact_fraction(val: Any, label: str = "rational") -> Fraction:
    if type(val) is not Fraction:
        raise VonNeumannClosureError("INVALID_FRACTION_TYPE", f"{label} must be exact Fraction")
    if val.numerator.bit_length() > MAX_RATIONAL_BITS:
        raise VonNeumannClosureError("RATIONAL_BIT_LIMIT", f"{label} numerator exceeds {MAX_RATIONAL_BITS}-bit cap")
    if val.denominator.bit_length() > MAX_RATIONAL_BITS:
        raise VonNeumannClosureError("RATIONAL_BIT_LIMIT", f"{label} denominator exceeds {MAX_RATIONAL_BITS}-bit cap")
    return val


def format_rational(q: Fraction, label: str = "rational") -> str:
    val = require_exact_fraction(q, label)
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"


def format_decimal(q: Fraction, places: int = 6) -> str:
    """Exact pure-integer half-up decimal rounding (zero floats, suppresses '-0.00...')."""
    val = require_exact_fraction(q, "decimal_val")
    p = require_exact_int(places, "places", lo=0, hi=12)
    neg = val < 0
    aq = -val if neg else val
    scale = 10**p
    scaled = aq * scale
    quot, rem = divmod(scaled.numerator, scaled.denominator)
    if rem * 2 >= scaled.denominator:
        quot += 1
    if quot == 0:
        neg = False
    sign = "-" if neg else ""
    if p == 0:
        return f"{sign}{quot}"
    whole, frac = divmod(quot, scale)
    return f"{sign}{whole}.{str(frac).rjust(p, '0')}"


def format_sci(q: Fraction, sig_digits: int = 4) -> str:
    """Exact pure-integer scientific notation for positive rationals (e.g. '3.880e+18', zero floats)."""
    val = require_exact_fraction(q, "sci_val")
    require_ok(val > 0, "SCI_NONPOSITIVE", "scientific format requires strictly positive rational")
    sd = require_exact_int(sig_digits, "sig_digits", lo=2, hi=8)
    # Find integer exponent e such that 10^e <= val < 10^(e+1)
    num, den = val.numerator, val.denominator
    exp = len(str(num)) - len(str(den))
    if exp >= 0:
        pow10 = 10**exp
        if num < den * pow10:
            exp -= 1
    else:
        pow10 = 10 ** (-exp)
        if num * pow10 < den:
            exp -= 1
    shift = (sd - 1) - exp
    if shift >= 0:
        scaled = val * (10**shift)
    else:
        scaled = val / (10 ** (-shift))
    quot, rem = divmod(scaled.numerator, scaled.denominator)
    if rem * 2 >= scaled.denominator:
        quot += 1
    if quot >= 10**sd:
        quot //= 10
        exp += 1
    s = str(quot)
    exp_sign = "+" if exp >= 0 else "-"
    return f"{s[0]}.{s[1:]}e{exp_sign}{abs(exp):02d}"


# ============================================================================
# 2. Exact Pure-Q Linear Algebra (Bareiss / Gauss-Jordan Determinant & Inverse)
# ============================================================================

def require_square_q_matrix(mat: Any, label: str = "matrix") -> list[list[Fraction]]:
    require_ok(type(mat) in (list, tuple) and len(mat) >= 1, "INVALID_MATRIX", f"{label} must be non-empty matrix")
    n = len(mat)
    out: list[list[Fraction]] = []
    for i, row in enumerate(mat):
        require_ok(type(row) in (list, tuple) and len(row) == n, "NON_SQUARE_MATRIX", f"{label}[{i}] length != {n}")
        out.append([require_exact_fraction(x, f"{label}[{i}][{j}]") for j, x in enumerate(row)])
    return out


def mat_mul_q(a: Sequence[Sequence[Fraction]], b: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    ma = require_square_q_matrix(a, "A")
    mb = require_square_q_matrix(b, "B")
    require_ok(len(ma) == len(mb), "DIM_MISMATCH", "matrix dimensions must match")
    n = len(ma)
    return [[sum((ma[i][k] * mb[k][j] for k in range(n)), Fraction(0)) for j in range(n)] for i in range(n)]


def mat_vec_q(a: Sequence[Sequence[Fraction]], v: Sequence[Fraction]) -> list[Fraction]:
    ma = require_square_q_matrix(a, "A")
    n = len(ma)
    require_ok(type(v) in (list, tuple) and len(v) == n, "VEC_DIM_MISMATCH", f"vector len must be {n}")
    vec = [require_exact_fraction(x, f"v[{i}]") for i, x in enumerate(v)]
    return [sum((ma[i][j] * vec[j] for j in range(n)), Fraction(0)) for i in range(n)]


def exact_det_and_inv_q(mat: Sequence[Sequence[Fraction]]) -> tuple[Fraction, list[list[Fraction]]]:
    """Exact Gauss-Jordan determinant & inverse over Q (zero floats, fail-closed on singular)."""
    m = require_square_q_matrix(mat, "M")
    n = len(m)
    aug = [list(m[i]) + [Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
    det = Fraction(1)
    for col in range(n):
        piv = -1
        for r in range(col, n):
            if aug[r][col] != 0:
                piv = r
                break
        require_ok(piv >= 0, "SINGULAR_MATRIX", f"matrix is singular at pivot column {col}")
        if piv != col:
            aug[col], aug[piv] = aug[piv], aug[col]
            det = -det
        pv = aug[col][col]
        det *= pv
        aug[col] = [x / pv for x in aug[col]]
        for r in range(n):
            if r != col:
                fac = aug[r][col]
                aug[r] = [aug[r][c] - fac * aug[col][c] for c in range(2 * n)]
    return det, [row[n:] for row in aug]


def leading_principal_minors_q(mat: Sequence[Sequence[Fraction]]) -> list[Fraction]:
    m = require_square_q_matrix(mat, "M")
    n = len(m)
    minors: list[Fraction] = []
    for k in range(1, n + 1):
        sub = [[m[i][j] for j in range(k)] for i in range(k)]
        det_k, _ = exact_det_and_inv_q(sub)
        minors.append(det_k)
    return minors


def identity_minus_q(a: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    ma = require_square_q_matrix(a, "A")
    n = len(ma)
    return [[Fraction(1 if i == j else 0) - ma[i][j] for j in range(n)] for i in range(n)]


def check_collatz_wielandt_bounds(
    a: Sequence[Sequence[Fraction]],
    v: Sequence[Fraction],
) -> tuple[Fraction, Fraction]:
    """For non-negative A and strictly positive v, certify min_i (Av)_i/v_i <= rho(A) <= max_i (Av)_i/v_i."""
    ma = require_square_q_matrix(a, "A")
    for i, row in enumerate(ma):
        for j, x in enumerate(row):
            require_ok(x >= 0, "NEGATIVE_MATRIX_ENTRY", f"A[{i}][{j}] must be >= 0")
    av = mat_vec_q(ma, v)
    ratios: list[Fraction] = []
    for i, vi in enumerate(v):
        require_ok(vi > 0, "NONPOSITIVE_WITNESS", f"witness v[{i}] must be > 0")
        ratios.append(av[i] / vi)
    return min(ratios), max(ratios)


# ============================================================================
# 3. Four Exact Pure-Z/Q Pillars
# ============================================================================

def certify_pillar1_mars_energy_hierarchy() -> dict[str, Any]:
    """Exact rational Mars 1-bar mass, gravitational binding energy, and >76x..>615x nuclear obstruction."""
    m_mars = Fraction(64_171 * 10**19)
    r_mars = Fraction(3_389_500)
    g_mars = Fraction(37_208, 10_000)
    big_g = Fraction(66_743, 10**15)
    p_1bar = Fraction(10**5)
    m_atm_now = Fraction(25 * 10**15)
    l_sun = Fraction(3_828 * 10**23)
    yr_s = Fraction(31_557_600)
    pi_lo = Fraction(333, 106)
    pi_hi = Fraction(355, 113)

    a_lo = 4 * pi_lo * r_mars * r_mars
    a_hi = 4 * pi_hi * r_mars * r_mars
    m_atm_lo = p_1bar * a_lo / g_mars
    m_atm_hi = p_1bar * a_hi / g_mars
    atm_ratio_lo = m_atm_lo / m_atm_now

    u_grav = Fraction(3, 5) * big_g * m_mars * m_mars / r_mars

    e_charge = Fraction(1_602_176_634, 10**28)
    u_kg = Fraction(16_605_390_666, 10**37)
    e_chem_spec = 5 * e_charge / (28 * u_kg)
    e_orb_spec = Fraction(1, 2) * Fraction(10_000) * Fraction(10_000)
    e_nuc1_spec = 10**6 * e_charge / u_kg
    e_nuc8_spec = 8 * e_nuc1_spec

    e_chem_hi = e_chem_spec * m_atm_hi
    e_orb_hi = e_orb_spec * m_atm_hi
    e_nuc1_lo = e_nuc1_spec * m_atm_lo
    e_nuc8_lo = e_nuc8_spec * m_atm_lo

    nuc1_over_ugrav_lo = e_nuc1_lo / u_grav
    nuc8_over_ugrav_lo = e_nuc8_lo / u_grav
    nuc1_over_orb_lo = e_nuc1_lo / e_orb_hi
    nuc1_over_lsun_yr_lo = e_nuc1_lo / (l_sun * yr_s)
    nuc8_over_lsun_yr_lo = e_nuc8_lo / (l_sun * yr_s)

    checks = {
        "m_atm_1bar_in_3p87e18_to_3p89e18_kg": all(
            (m_atm_lo > Fraction(387 * 10**16), m_atm_hi < Fraction(389 * 10**16))
        ),
        "m_atm_1bar_gt_150x_current": atm_ratio_lo > 150,
        "u_grav_in_4p86e30_to_4p87e30_J": all(
            (u_grav > Fraction(486 * 10**28), u_grav < Fraction(487 * 10**28))
        ),
        "chemical_bond_energy_lt_1e26_J": e_chem_hi < Fraction(10**26),
        "orbital_import_10kms_lt_2e26_J": e_orb_hi < Fraction(2 * 10**26),
        "nuclear_1MeV_exceeds_70x_u_grav": nuc1_over_ugrav_lo > 70,
        "nuclear_1MeV_exceeds_76x_u_grav": nuc1_over_ugrav_lo > 76,
        "nuclear_8MeV_exceeds_615x_u_grav": nuc8_over_ugrav_lo > 615,
        "nuclear_1MeV_exceeds_1e6x_orbital_import": nuc1_over_orb_lo > Fraction(10**6),
    }
    return {
        "pi_enclosure_q": [format_rational(pi_lo), format_rational(pi_hi)],
        "m_atm_1bar_kg_sci": [format_sci(m_atm_lo), format_sci(m_atm_hi)],
        "m_atm_over_current_lo_dec6": format_decimal(atm_ratio_lo, 6),
        "u_grav_mars_J_sci": format_sci(u_grav),
        "e_chem_5eV_28u_hi_J_sci": format_sci(e_chem_hi),
        "e_orb_10kms_hi_J_sci": format_sci(e_orb_hi),
        "e_nuc_1MeV_lo_J_sci": format_sci(e_nuc1_lo),
        "e_nuc_8MeV_lo_J_sci": format_sci(e_nuc8_lo),
        "nuc_1MeV_over_u_grav_lo_dec6": format_decimal(nuc1_over_ugrav_lo, 6),
        "nuc_8MeV_over_u_grav_lo_dec6": format_decimal(nuc8_over_ugrav_lo, 6),
        "nuc_1MeV_over_orbital_lo_sci": format_sci(nuc1_over_orb_lo),
        "nuc_1MeV_solar_years_lo_dec6": format_decimal(nuc1_over_lsun_yr_lo, 6),
        "nuc_8MeV_solar_years_lo_dec6": format_decimal(nuc8_over_lsun_yr_lo, 6),
        "inequality_checks": checks,
        "all_verified": all(checks.values()),
    }


def _canonical_4x4_matrices() -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    a_good = [
        [Fraction(1, 10), Fraction(1, 5), Fraction(3, 20), Fraction(1, 10)],
        [Fraction(3, 20), Fraction(1, 10), Fraction(1, 5), Fraction(3, 20)],
        [Fraction(1, 10), Fraction(3, 20), Fraction(1, 10), Fraction(1, 5)],
        [Fraction(3, 20), Fraction(1, 10), Fraction(3, 20), Fraction(1, 10)],
    ]
    a_bad = [
        [Fraction(3, 10), Fraction(3, 10), Fraction(3, 10), Fraction(1, 4)],
        [Fraction(3, 10), Fraction(3, 10), Fraction(1, 4), Fraction(3, 10)],
        [Fraction(1, 4), Fraction(3, 10), Fraction(3, 10), Fraction(3, 10)],
        [Fraction(3, 10), Fraction(1, 4), Fraction(3, 10), Fraction(3, 10)],
    ]
    return a_good, a_bad


def certify_pillar2_leontief_hawkins_simon() -> dict[str, Any]:
    """Exact Q^{4x4} Von Neumann / Leontief Hawkins-Simon closure vs deficit control."""
    sectors = ["power", "refining", "fabrication", "robotics"]
    a_good, a_bad = _canonical_4x4_matrices()
    ones4 = [Fraction(1), Fraction(1), Fraction(1), Fraction(1)]

    im_good = identity_minus_q(a_good)
    minors_good = leading_principal_minors_q(im_good)
    det_good, inv_good = exact_det_and_inv_q(im_good)
    prod_right = mat_mul_q(im_good, inv_good)
    prod_left = mat_mul_q(inv_good, im_good)
    id4 = [[Fraction(1 if i == j else 0) for j in range(4)] for i in range(4)]
    cw_lo_g, cw_hi_g = check_collatz_wielandt_bounds(a_good, ones4)
    gamma_lb = (Fraction(1) / cw_hi_g) - Fraction(1)

    good_rec = {
        "matrix_q": [[format_rational(x) for x in row] for row in a_good],
        "leading_principal_minors_q": [format_rational(m) for m in minors_good],
        "all_leading_minors_positive": all(m > 0 for m in minors_good),
        "det_I_minus_A_q": format_rational(det_good),
        "leontief_inverse_exact_identity": all((prod_right == id4, prod_left == id4)),
        "leontief_inverse_all_positive": all(inv_good[i][j] > 0 for i in range(4) for j in range(4)),
        "collatz_wielandt_rho_bounds_q": [format_rational(cw_lo_g), format_rational(cw_hi_g)],
        "rho_strictly_lt_1": cw_hi_g < 1,
        "balanced_growth_surplus_lb_q": format_rational(gamma_lb),
        "verified": all((
            all(m > 0 for m in minors_good),
            det_good > 0,
            prod_right == id4,
            prod_left == id4,
            all(inv_good[i][j] > 0 for i in range(4) for j in range(4)),
            cw_hi_g < 1,
            gamma_lb > 0,
        )),
    }

    im_bad = identity_minus_q(a_bad)
    minors_bad = leading_principal_minors_q(im_bad)
    det_bad, _ = exact_det_and_inv_q(im_bad)
    cw_lo_b, cw_hi_b = check_collatz_wielandt_bounds(a_bad, ones4)
    bad_rec = {
        "matrix_q": [[format_rational(x) for x in row] for row in a_bad],
        "leading_principal_minors_q": [format_rational(m) for m in minors_bad],
        "hawkins_simon_violated": any(m <= 0 for m in minors_bad),
        "det_I_minus_A_q": format_rational(det_bad),
        "collatz_wielandt_rho_bounds_q": [format_rational(cw_lo_b), format_rational(cw_hi_b)],
        "rho_strictly_gt_1": cw_lo_b > 1,
        "verified": all((det_bad < 0, any(m <= 0 for m in minors_bad), cw_lo_b > 1)),
    }
    return {
        "sectors": sectors,
        "productive_closure": good_rec,
        "deficit_negative_control": bad_rec,
        "all_verified": all((good_rec["verified"], bad_rec["verified"])),
    }


def _canonical_5x5_vitamin_specs() -> tuple[list[Fraction], list[Fraction], Fraction, list[Fraction], Fraction]:
    a_lv = [Fraction(1, 20), Fraction(1, 20), Fraction(1, 10), Fraction(1, 10)]
    a_vl_blocked = [Fraction(3, 2), Fraction(3, 2), Fraction(2), Fraction(2)]
    a_vv_blocked = Fraction(1, 5)
    a_vl_closed = [Fraction(1, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)]
    a_vv_closed = Fraction(1, 10)
    return a_lv, a_vl_blocked, a_vv_blocked, a_vl_closed, a_vv_closed


def certify_pillar3_schur_vitamin_bottleneck() -> dict[str, Any]:
    """Exact Q^{5x5} Schur-complement vitamin bottleneck vs design-for-closure restoration."""
    a_ll, _ = _canonical_4x4_matrices()
    im_ll = identity_minus_q(a_ll)
    det_ll, inv_ll = exact_det_and_inv_q(im_ll)
    a_lv, a_vl_b, a_vv_b, a_vl_c, a_vv_c = _canonical_5x5_vitamin_specs()

    # Exact vector (I_4 - A_LL)^{-1} A_LV
    inv_ll_alv = mat_vec_q(inv_ll, a_lv)

    # Case A: Unclosed high-complexity vitamin sector (S_VV < 0 -> closure algebraically blocked)
    s_vv_blocked = (Fraction(1) - a_vv_b) - sum((a_vl_b[i] * inv_ll_alv[i] for i in range(4)), Fraction(0))
    a5_blocked = [a_ll[i] + [a_lv[i]] for i in range(4)] + [a_vl_b + [a_vv_b]]
    im5_blocked = identity_minus_q(a5_blocked)
    det5_blocked, inv5_blocked = exact_det_and_inv_q(im5_blocked)
    ones5 = [Fraction(1)] * 5
    x_unit_blocked = mat_vec_q(inv5_blocked, ones5)
    # Import-leverage vector L_VL = A_VL (I_4 - A_LL)^{-1}
    import_leverage_b = [sum((a_vl_b[k] * inv_ll[k][j] for k in range(4)), Fraction(0)) for j in range(4)]

    blocked_rec = {
        "a_lv_q": [format_rational(x) for x in a_lv],
        "a_vl_q": [format_rational(x) for x in a_vl_b],
        "a_vv_q": format_rational(a_vv_b),
        "bulk_det_I_minus_ALL_q": format_rational(det_ll),
        "schur_complement_S_VV_q": format_rational(s_vv_blocked),
        "det_I_minus_A5_q": format_rational(det5_blocked),
        "block_det_identity_exact": det5_blocked == det_ll * s_vv_blocked,
        "schur_strictly_nonpositive": s_vv_blocked <= 0,
        "unit_demand_solution_q": [format_rational(x) for x in x_unit_blocked],
        "autonomous_fixed_point_infeasible": all(x < 0 for x in x_unit_blocked),
        "import_leverage_bulk_to_vitamin_q": [format_rational(x) for x in import_leverage_b],
        "verified": all((
            det_ll > 0,
            s_vv_blocked < 0,
            det5_blocked == det_ll * s_vv_blocked,
            det5_blocked < 0,
            all(x < 0 for x in x_unit_blocked),
            all(x > 0 for x in import_leverage_b),
        )),
    }

    # Case B: Design-for-closure restored (coarse local vitamin -> S_VV' > 0, rho(A5') < 1)
    s_vv_closed = (Fraction(1) - a_vv_c) - sum((a_vl_c[i] * inv_ll_alv[i] for i in range(4)), Fraction(0))
    a5_closed = [a_ll[i] + [a_lv[i]] for i in range(4)] + [a_vl_c + [a_vv_c]]
    im5_closed = identity_minus_q(a5_closed)
    det5_closed, inv5_closed = exact_det_and_inv_q(im5_closed)
    cw_lo_c, cw_hi_c = check_collatz_wielandt_bounds(a5_closed, ones5)
    cw_lo_ll, cw_hi_ll = check_collatz_wielandt_bounds(a_ll, [Fraction(1)] * 4)

    restored_rec = {
        "a_lv_q": [format_rational(x) for x in a_lv],
        "a_vl_q": [format_rational(x) for x in a_vl_c],
        "a_vv_q": format_rational(a_vv_c),
        "schur_complement_S_VV_q": format_rational(s_vv_closed),
        "det_I_minus_A5_q": format_rational(det5_closed),
        "block_det_identity_exact": det5_closed == det_ll * s_vv_closed,
        "schur_strictly_positive": s_vv_closed > 0,
        "coupled_inverse_all_positive": all(inv5_closed[i][j] > 0 for i in range(5) for j in range(5)),
        "collatz_wielandt_rho_bounds_q": [format_rational(cw_lo_c), format_rational(cw_hi_c)],
        "rho_strictly_lt_1": cw_hi_c < 1,
        "vitamin_removed_bulk_rho_ub_q": format_rational(cw_hi_ll),
        "verified": all((
            s_vv_closed > 0,
            det5_closed == det_ll * s_vv_closed,
            det5_closed > 0,
            all(inv5_closed[i][j] > 0 for i in range(5) for j in range(5)),
            cw_hi_c < 1,
            cw_hi_ll < 1,
        )),
    }
    return {
        "bulk_sectors": ["power", "refining", "fabrication", "robotics"],
        "vitamin_sector": "euv_lithography_vitamin",
        "unclosed_vitamin_blocked": blocked_rec,
        "design_for_closure_restored": restored_rec,
        "all_verified": all((blocked_rec["verified"], restored_rec["verified"])),
    }


def step_eigen_quasispecies(p0: Fraction, q_fidelity: Fraction, length_l: int, sigma_adv: Fraction, steps: int) -> dict[str, Any]:
    """Exact discrete Eigen quasispecies recursion over Q with closed-form odds cross-check."""
    p0v = require_exact_fraction(p0, "p0")
    qv = require_exact_fraction(q_fidelity, "q_fidelity")
    lv = require_exact_int(length_l, "length_l", lo=1, hi=32)
    sv = require_exact_fraction(sigma_adv, "sigma_adv")
    nv = require_exact_int(steps, "steps", lo=1, hi=20)
    require_ok(0 < p0v < 1, "INVALID_P0", "p0 must lie strictly in (0, 1)")
    require_ok(0 < qv < 1, "INVALID_Q_FIDELITY", "q_fidelity must lie strictly in (0, 1)")
    require_ok(sv >= 1, "INVALID_SIGMA", "sigma_adv must be >= 1")

    q_pow = qv**lv
    alpha = Fraction(1) / sv
    growth_factor = q_pow * sv
    p = p0v
    odds0 = p0v / (Fraction(1) - p0v)
    traj: list[Fraction] = [p]
    odds_exact = True
    for t in range(1, nv + 1):
        p = (q_pow * p) / (q_pow * p + alpha * (Fraction(1) - p))
        traj.append(p)
        lhs_odds = p / (Fraction(1) - p)
        rhs_odds = (growth_factor**t) * odds0
        if lhs_odds != rhs_odds:
            odds_exact = False
    return {
        "q_fidelity_q": format_rational(qv),
        "length_L": lv,
        "sigma_advantage_q": format_rational(sv),
        "Q_master_copy_prob_q": format_rational(q_pow),
        "Q_crit_q": format_rational(alpha),
        "Q_times_sigma_q": format_rational(growth_factor),
        "p0_q": format_rational(p0v),
        "p_final_q": format_rational(traj[-1]),
        "p_final_dec6": format_decimal(traj[-1], 6),
        "strictly_increasing": all(traj[i + 1] > traj[i] for i in range(nv)),
        "strictly_decreasing": all(traj[i + 1] < traj[i] for i in range(nv)),
        "stationary": all(traj[i] == p0v for i in range(nv + 1)),
        "closed_form_odds_identity_exact": odds_exact,
    }


def certify_pillar4_radiative_and_eigen() -> dict[str, Any]:
    """Certify exact pi-free Stefan-Boltzmann O(R^3)/O(R^2) ceiling & Eigen metrology gate."""
    sig_lo = Fraction(5_670_374, 10**14)
    sig_hi = Fraction(5_670_375, 10**14)
    eps = Fraction(9, 10)
    temp_k = Fraction(400)
    q_vol = Fraction(1_000)

    t4 = temp_k**4
    r_crit_lo = 3 * eps * sig_lo * t4 / q_vol
    r_crit_hi = 3 * eps * sig_hi * t4 / q_vol

    radii_specs = (
        ("subcritical_compact_3m", Fraction(3), 1, True),
        ("supercritical_8m_swarm_k3", Fraction(8), 3, False),
        ("supercritical_40m_swarm_k11", Fraction(40), 11, False),
        ("supercritical_400m_swarm_k103", Fraction(400), 103, False),
    )
    rad_rows: list[dict[str, Any]] = []
    for name, radius_m, k_split, exp_compact_ok in radii_specs:
        # P_gen / P_rad = R / R_crit -> lo uses r_crit_hi, hi uses r_crit_lo
        ratio_lo = radius_m / r_crit_hi
        ratio_hi = radius_m / r_crit_lo
        swarm_ratio_hi = ratio_hi / Fraction(k_split)
        compact_passes = ratio_hi < 1
        swarm_passes = swarm_ratio_hi < 1
        rad_rows.append({
            "name": name,
            "radius_m_q": format_rational(radius_m),
            "compact_heat_to_rad_lo_dec6": format_decimal(ratio_lo, 6),
            "compact_heat_to_rad_hi_dec6": format_decimal(ratio_hi, 6),
            "compact_cooling_feasible": compact_passes,
            "swarm_split_k": k_split,
            "swarm_unit_count_k3": k_split**3,
            "swarm_area_gain_factor": k_split,
            "swarm_heat_to_rad_hi_dec6": format_decimal(swarm_ratio_hi, 6),
            "swarm_cooling_feasible": swarm_passes,
            "verified": all((compact_passes is exp_compact_ok, swarm_passes)),
        })

    eigen_specs = (
        ("above_threshold_metrology_gate", Fraction(1, 2), Fraction(9, 10), 8, Fraction(4), 10, "increasing"),
        ("below_threshold_error_catastrophe", Fraction(1, 2), Fraction(4, 5), 8, Fraction(4), 10, "decreasing"),
        ("no_metrology_filter_sigma_1", Fraction(1, 2), Fraction(9, 10), 8, Fraction(1), 10, "decreasing"),
        ("exact_critical_threshold_stationary", Fraction(1, 2), Fraction(1, 2), 2, Fraction(4), 10, "stationary"),
    )
    eigen_rows: list[dict[str, Any]] = []
    for name, p0, qf, lv, sig, steps, exp_regime in eigen_specs:
        rec = step_eigen_quasispecies(p0, qf, lv, sig, steps)
        regime_ok = (
            rec["strictly_increasing"]
            if exp_regime == "increasing"
            else (rec["strictly_decreasing"] if exp_regime == "decreasing" else rec["stationary"])
        )
        rec["name"] = name
        rec["expected_regime"] = exp_regime
        rec["verified"] = all((regime_ok, rec["closed_form_odds_identity_exact"]))
        eigen_rows.append(rec)

    return {
        "radiative_ceiling": {
            "sigma_sb_enclosure_q": [format_rational(sig_lo), format_rational(sig_hi)],
            "emissivity_q": format_rational(eps),
            "temperature_K": 400,
            "volumetric_heat_W_per_m3": 1000,
            "r_crit_m_enclosure_dec6": [format_decimal(r_crit_lo, 6), format_decimal(r_crit_hi, 6)],
            "pi_cancels_identically": True,
            "cases": rad_rows,
            "all_verified": all(r["verified"] for r in rad_rows),
        },
        "eigen_metrology_threshold": {
            "cases": eigen_rows,
            "metrology_necessary_for_imperfect_fidelity": all(r["verified"] for r in eigen_rows),
            "all_verified": all(r["verified"] for r in eigen_rows),
        },
        "all_verified": all((all(r["verified"] for r in rad_rows), all(r["verified"] for r in eigen_rows))),
    }


def build_payload() -> dict[str, Any]:
    p1 = certify_pillar1_mars_energy_hierarchy()
    p2 = certify_pillar2_leontief_hawkins_simon()
    p3 = certify_pillar3_schur_vitamin_bottleneck()
    p4 = certify_pillar4_radiative_and_eigen()
    all_ok = all((p1["all_verified"], p2["all_verified"], p3["all_verified"], p4["all_verified"]))
    return {
        "track_id": TRACK_ID,
        "portal_ref": "Portal 46",
        "novelty_class": "N1",
        "prior_literature_n0": [
            "Leontief (1941) / Hawkins-Simon (1949): Input-Output Productivity Condition",
            "von Neumann (1945) / Collatz-Wielandt: Balanced Expanding Economy & Perron Bounds",
            "Schur (1917): Block-Matrix Schur Complement Reduction",
            "Eigen (1971): Quasispecies Self-Organization & Error-Catastrophe Threshold",
            "Jakosky & Edwards (Nature Astronomy 2018): Mars CO2 Inventory",
        ],
        "pillar1_mars_energy_hierarchy": p1,
        "pillar2_leontief_hawkins_simon": p2,
        "pillar3_schur_vitamin_bottleneck": p3,
        "pillar4_radiative_and_eigen": p4,
        "summary": {
            "pillar_count": 4,
            "all_four_pillars_verified": all_ok,
            "float_count_on_trust_path": 0,
            "bare_assert_count": 0,
            "rng_calls": 0,
        },
    }
