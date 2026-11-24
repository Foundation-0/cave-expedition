#!/usr/bin/env python3
"""R5 must-fail controls for verification/checks/check_003_seam01_ropt.py (AUDIT-002).

PROTOCOL.md R5 asks for a must-fail control for every named check, so that deleting any
refusal branch turns the suite red. check_003 itself is not edited: its bytes and its
stdout are pinned by the outside Gate-5 anchor (verification/outside/gate5-unification),
check_recount_420 copies its random call order and check_012 imports from it. This file
therefore loads it with importlib and drives each guard by patching the helper that feeds
it (for example R_opt + 1000, R_G = 10**9, a rank off by one), never by changing the file.

Each refusal is matched on its full message. A loose fragment such as "Hermitian" also
matches a different guard, which would let a deleted guard pass unnoticed.

The baseline runs at the top of each class are positive controls: the unpatched audit must
pass and return the counts recorded in the anchored stdout.

Run (all three R4 modes):
  python3 -I -B verification/tests/test_check_003_r5.py
  python3 -I -O -B verification/tests/test_check_003_r5.py
  python3 -I -B -W error verification/tests/test_check_003_r5.py
Needs: Python 3 standard library only. Takes about 7 seconds.
"""
from __future__ import annotations

import importlib.util
import math
import re
import sys
import types
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

CHECK = Path(__file__).resolve().parents[1] / "checks" / "check_003_seam01_ropt.py"
MODULE_NAME = "cave_check_003_under_test"


def _load_check_003() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(MODULE_NAME, CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CHECK}")
    module = importlib.util.module_from_spec(spec)
    # The Qi dataclass resolves its string annotations through sys.modules, so the
    # module must be registered before it runs.
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


C3 = _load_check_003()


def q(re_part, im_part=0):
    return C3.Qi(Fraction(re_part), Fraction(im_part))


def mat(rows):
    return [[v if isinstance(v, C3.Qi) else q(v) for v in row] for row in rows]


def caller_binds(name: str, obj) -> bool:
    """True when the audit function that called a patched helper holds obj under name.

    Frame 0 is this function, frame 1 the patched helper, frame 2 its caller.
    """
    return sys._getframe(2).f_locals.get(name) is obj


class RefusalCase(unittest.TestCase):
    def assertRefused(self, fn, expected):
        """fn must raise RuntimeError whose text equals expected (str) or fully matches it (Pattern)."""
        with self.assertRaises(RuntimeError) as ctx:
            fn()
        text = str(ctx.exception)
        if isinstance(expected, re.Pattern):
            self.assertIsNotNone(expected.fullmatch(text), f"refusal text {text!r} does not match {expected.pattern!r}")
        else:
            self.assertEqual(text, expected)
        return text


class PrimitiveGuards(RefusalCase):
    def test_require(self):
        self.assertIsNone(C3.require(True, "never shown"))
        self.assertRefused(lambda: C3.require(False, "control"), "CHECK FAILED: control")

    def test_qi_division(self):
        self.assertEqual(q(1) / q(2), q(Fraction(1, 2)))
        self.assertEqual(q(1, 1) / q(1, -1), q(0, 1))
        self.assertRefused(lambda: q(1) / q(0), "CHECK FAILED: division by zero in Q(i)")

    def test_cmul_dimension(self):
        x = mat([[1, 2], [3, 4]])
        self.assertEqual(C3.cmul(C3.ceye(2), x), x)
        self.assertRefused(lambda: C3.cmul(x, mat([[1, 0], [0, 1], [1, 1]])), "CHECK FAILED: cmul dimension mismatch")

    def test_is_hermitian(self):
        self.assertTrue(C3.is_hermitian(mat([[2, q(1, 1)], [q(1, -1), 3]])))
        self.assertFalse(C3.is_hermitian([]), "empty matrix")
        self.assertFalse(C3.is_hermitian(mat([[1, 2], [2]])), "ragged rows")
        self.assertFalse(C3.is_hermitian(mat([[1, 2, 3], [2, 1, 0]])), "rows longer than the row count")
        self.assertFalse(C3.is_hermitian(mat([[q(1, 1)]])), "complex diagonal")
        self.assertFalse(C3.is_hermitian(mat([[1, q(1, 1)], [q(1, 1), 1]])), "off-diagonal not conjugate")

    def test_ctrace_real(self):
        self.assertEqual(C3.ctrace_real(mat([[2, 0], [0, 3]])), Fraction(5))
        self.assertRefused(lambda: C3.ctrace_real(mat([[q(1, 1)]])), "CHECK FAILED: Hermitian trace has nonzero imaginary part")

    def test_cmat_inv(self):
        self.assertEqual(C3.cmat_inv(mat([[2, 0], [0, 4]])), mat([[Fraction(1, 2), 0], [0, Fraction(1, 4)]]))
        self.assertRefused(lambda: C3.cmat_inv(mat([[0, 0], [0, 0]])), "CHECK FAILED: singular matrix in cmat_inv")


class DescartesOracleGuards(RefusalCase):
    def test_inertia_positive_controls(self):
        self.assertEqual(C3.hermitian_inertia_descartes(mat([[2, 0, 0], [0, -3, 0], [0, 0, 0]])), (1, 1, 1))
        self.assertEqual(C3.hermitian_inertia_descartes(mat([[2, q(1, 1)], [q(1, -1), 3]])), (2, 0, 0))

    def test_hermitian_guard(self):
        self.assertRefused(
            lambda: C3.hermitian_inertia_descartes(mat([[1, q(1, 1)], [q(1, 1), 1]])),
            "CHECK FAILED: matrix must be Hermitian",
        )

    def test_cayley_hamilton_guard(self):
        real_cmul = C3.cmul

        def off_diagonal_drift(a, b):
            out = real_cmul(a, b)
            out[0][1] = out[0][1] + q(1)
            return out

        with mock.patch.object(C3, "cmul", off_diagonal_drift):
            self.assertRefused(
                lambda: C3.hermitian_inertia_descartes(mat([[1, 0], [0, 2]])),
                "CHECK FAILED: Faddeev-LeVerrier Cayley-Hamilton check failed",
            )

    def test_sign_count_guard(self):
        # A rotation has no real eigenvalues; with the Hermitian guard bypassed the
        # sign counts cannot add up to n.
        with mock.patch.object(C3, "is_hermitian", lambda a: True):
            self.assertRefused(
                lambda: C3.hermitian_inertia_descartes(mat([[0, -1], [1, 0]])),
                "CHECK FAILED: Descartes sum mismatch: (0, 0, 0) vs 2",
            )


class ROptGuards(RefusalCase):
    def test_positive_controls(self):
        self.assertEqual(C3.R_opt_guarded(Fraction(6), Fraction(5), Fraction(43), 1), Fraction(2))
        self.assertEqual(C3.R_opt_guarded(Fraction(0), Fraction(1), Fraction(1), 1), Fraction(0))
        self.assertEqual(C3.R_opt_guarded(Fraction(1), Fraction(1), Fraction(10), 5), Fraction(0))

    def test_S_must_be_positive(self):
        self.assertRefused(
            lambda: C3.R_opt_guarded(Fraction(1), Fraction(0), Fraction(0), 0),
            "CHECK FAILED: S must be > 0 when u + t > 0",
        )

    def test_regime1_denominator_must_be_positive(self):
        # u=1, t=2, b=1, S=4: t(u+t)=6 >= bS=4 and S - t^2/b = 0.
        self.assertRefused(
            lambda: C3.R_opt_guarded(Fraction(1), Fraction(2), Fraction(4), 1),
            "CHECK FAILED: S > t^2/b violated for feasible u > 0, t > 0",
        )


class EdgeCaseAuditGuards(RefusalCase):
    def test_baseline(self):
        out = C3.audit_edge_cases()
        self.assertTrue(out["edge1_u0_t1_S1_b1_raw_peer_weaver"].startswith("ZeroDivisionError: "))
        self.assertEqual(out["edge1_guarded_R_opt"], "0")
        self.assertEqual(out["edge2_raw_negative_else_branch"], "-23/5")
        self.assertEqual(out["edge2_guarded_clamped"], "0")

    def test_raw_formula_that_never_divides_by_zero(self):
        with mock.patch.object(C3, "R_opt_raw_peer_weaver", lambda u, t, S, b: Fraction(-1)):
            self.assertRefused(
                C3.audit_edge_cases,
                "CHECK FAILED: expected raw #17 formula to hit ZeroDivisionError at u=0, t=b=S=1",
            )

    def test_guarded_value_nonzero_at_u0(self):
        with mock.patch.object(C3, "R_opt_guarded", lambda u, t, S, b: Fraction(7)):
            self.assertRefused(C3.audit_edge_cases, "CHECK FAILED: guarded R_opt must return 0 when u=0")

    def test_raw_else_branch_not_negative(self):
        def raw(u, t, S, b):
            if u == 0:
                raise ZeroDivisionError("control")
            return Fraction(0)

        with mock.patch.object(C3, "R_opt_raw_peer_weaver", raw):
            self.assertRefused(C3.audit_edge_cases, "CHECK FAILED: expected raw #17 formula to return negative value")

    def test_guarded_value_not_clamped(self):
        with mock.patch.object(C3, "R_opt_guarded", lambda u, t, S, b: Fraction(0) if u == 0 else Fraction(1)):
            self.assertRefused(C3.audit_edge_cases, "CHECK FAILED: guarded R_opt must clamp negative branch to 0")


class ComplexHermitianAuditGuards(RefusalCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = C3.audit_complex_hermitian()

    def test_baseline_counts(self):
        out = self.baseline
        self.assertEqual(out["complex_hermitian_instances_Q_i"], 420)
        self.assertEqual(out["strictly_noncommuting"], 356)
        self.assertEqual(out["strictly_complex_nonzero_imag"], 413)
        self.assertEqual(out["violations_strengthened_chain_n_pos_H_perp_ge_R_opt"], 0)
        self.assertEqual(out["instances_with_rank_P_perp_strictly_lt_rank_P"], 190)
        self.assertEqual(out["instances_with_n_pos_H_perp_strictly_lt_rank_P_perp"], 71)
        self.assertEqual(out["R_opt_strictly_beats_Fable_RG"], 417)
        self.assertEqual(out["R_opt_ties_Fable_RG"], 3)
        self.assertEqual(out["R_opt_strictly_beats_fixed_c2"], 214)
        self.assertEqual(
            out["regime_counts"],
            {"regime1_u2_over_S_minus_t2_b": 51, "regime2_u_plus_t_sq_over_S_minus_b": 279, "regime0_zero": 90},
        )
        self.assertIs(out["scan23848_mode_b_comparison"]["rho=0.0"]["R_opt_exact_is_1"], True)

    def test_rank_of_P1_off_by_one(self):
        real_crank = C3.crank

        def crank(a):
            r = real_crank(a)
            return r + 1 if caller_binds("P1", a) else r

        with mock.patch.object(C3, "crank", crank):
            self.assertRefused(C3.audit_complex_hermitian, "CHECK FAILED: exact rank mismatch")

    def test_inertia_of_Q_off_by_one(self):
        real = C3.hermitian_inertia_descartes
        seen = []

        def descartes(h):
            p, n, z = real(h)
            if caller_binds("Q", h) and not seen:
                seen.append(p)
                return (p + 1, n, z)
            return (p, n, z)

        with mock.patch.object(C3, "hermitian_inertia_descartes", descartes):
            text = self.assertRefused(
                C3.audit_complex_hermitian,
                re.compile(r"CHECK FAILED: independent Descartes inertia mismatch: \d+ vs \d+"),
            )
        self.assertEqual(text, f"CHECK FAILED: independent Descartes inertia mismatch: {seen[0] + 1} vs {seen[0]}")

    def test_P1_reported_with_negative_eigenvalue(self):
        real = C3.hermitian_inertia_descartes

        def descartes(h):
            p, n, z = real(h)
            return (p, 1, z) if caller_binds("P1", h) else (p, n, z)

        with mock.patch.object(C3, "hermitian_inertia_descartes", descartes):
            self.assertRefused(C3.audit_complex_hermitian, "CHECK FAILED: P1 PSD verification failed")

    def test_portal1_slack_bound(self):
        real = C3.cfrob_sq

        def cfrob_sq(a):
            s = real(a)
            return s - 10**6 if caller_binds("M", a) else s

        with mock.patch.object(C3, "cfrob_sq", cfrob_sq):
            self.assertRefused(
                C3.audit_complex_hermitian,
                re.compile(r"CHECK FAILED: Portal 1 slack bound violated: -\d+(/\d+)? < \d+(/\d+)?"),
            )

    def test_projected_rank_above_rank(self):
        real_crank = C3.crank

        def crank(a):
            r = real_crank(a)
            return r + 1000 if caller_binds("P22", a) else r

        with mock.patch.object(C3, "crank", crank):
            self.assertRefused(C3.audit_complex_hermitian, "CHECK FAILED: projected rank/inertia chain violated")

    def test_R_opt_above_projected_inertia(self):
        real = C3.R_opt_guarded

        with mock.patch.object(C3, "R_opt_guarded", lambda u, t, S, b: real(u, t, S, b) + 1000):
            self.assertRefused(
                C3.audit_complex_hermitian,
                re.compile(r"CHECK FAILED: STRENGTHENED R_opt VIOLATED: n_\+\(H_perp\)=\d+ < \d+(/\d+)?"),
            )

    def _first_ropt_refusal(self, helper_name):
        real = C3.R_opt_guarded
        values = []

        def recording(u, t, S, b):
            values.append(real(u, t, S, b))
            return values[-1]

        with mock.patch.object(C3, "R_opt_guarded", recording), mock.patch.object(
            C3, helper_name, lambda u, t, S, b: Fraction(10**9)
        ):
            with self.assertRaises(RuntimeError) as ctx:
                C3.audit_complex_hermitian()
        return str(ctx.exception), values[0]

    def test_R_opt_below_R_G(self):
        text, ropt = self._first_ropt_refusal("R_G_fable")
        self.assertEqual(text, f"CHECK FAILED: R_opt < R_G violated: {ropt} < 1000000000")

    def test_R_opt_below_R_c2(self):
        text, ropt = self._first_ropt_refusal("R_lemma32_c2")
        self.assertEqual(text, f"CHECK FAILED: R_opt < R_c2 violated: {ropt} < 1000000000")

    def test_scale_invariance(self):
        real = C3.R_opt_guarded
        calls = []

        def second_call_drifts(u, t, S, b):
            calls.append(1)
            value = real(u, t, S, b)
            return value + 1 if len(calls) == 2 else value

        with mock.patch.object(C3, "R_opt_guarded", second_call_drifts):
            self.assertRefused(C3.audit_complex_hermitian, "CHECK FAILED: R_opt not scale-invariant!")

    def _run_with_S_scaled(self, factor: Fraction):
        real = C3.cfrob_sq
        with mock.patch.object(C3, "cfrob_sq", lambda a: real(a) * factor):
            return C3.audit_complex_hermitian()

    def test_regime1_count_49_is_refused(self):
        # Scaling every S by 1002/1000 moves the two regime-1 instances with
        # t(u+t)/(bS) below 1.002 into regime 2, leaving 49.
        self.assertRefused(
            lambda: self._run_with_S_scaled(Fraction(1002, 1000)),
            "CHECK FAILED: expected >= 50 Regime 1 instances, got 49",
        )

    def test_regime1_count_50_is_accepted(self):
        # Scaling by 10012/10000 moves only the instance with the smallest ratio.
        out = self._run_with_S_scaled(Fraction(10012, 10000))
        self.assertEqual(out["regime_counts"]["regime1_u2_over_S_minus_t2_b"], 50)


class SharpnessAuditGuards(RefusalCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = C3.audit_sharpness()

    def test_baseline(self):
        out = self.baseline
        self.assertEqual(out["exact_rational_equality_witnesses_verified"], 4)
        self.assertEqual(out["constructive_integer_sharpness_tuples_verified"], 200)
        self.assertLess(out["max_construction_error"], 1e-9)
        self.assertEqual(out["subcases_covered"], {"R1": 50, "R2_caseA": 104, "R2_caseB": 7, "u_plus_t_le_0": 39})

    def _witness_drift(self, call_number):
        real = C3.R_opt_guarded
        calls = []

        def drift(u, t, S, b):
            calls.append(1)
            value = real(u, t, S, b)
            return value + 1 if len(calls) == call_number else value

        return mock.patch.object(C3, "R_opt_guarded", drift)

    def test_exact_witnesses(self):
        expected = {
            1: "CHECK FAILED: exact Regime 1 tightness failed: 3",
            2: "CHECK FAILED: exact Regime 2 (t>0) tightness failed: 10",
            3: "CHECK FAILED: exact Regime 2 (t<0) tightness failed: 3",
            4: "CHECK FAILED: exact Regime 2 (b=0) tightness failed: 4",
        }
        for call_number, message in expected.items():
            with self.subTest(witness=call_number), self._witness_drift(call_number):
                self.assertRefused(C3.audit_sharpness, message)

    def test_construction_requires_positive_u(self):
        self.assertRefused(lambda: C3.construct_sharp_diagonal(0.0, 1.0, 1.0, 1), "CHECK FAILED: requires u > 0")

    def test_case_a_delta_guard(self):
        # b=0 with t>0 is infeasible (Q has no positive eigenvalue), so delta = -t.
        self.assertRefused(lambda: C3.construct_sharp_diagonal(1.0, 1.0, 4.0, 0), "CHECK FAILED: Case A delta < 0: -1.0")
        # delta exactly at the declared tolerance -1e-10 is accepted.
        # After the guard, delta is clamped to 0, so the construction is P1 = [u + t], Q = [0].
        p_diag, q_diag = C3.construct_sharp_diagonal(1.0, 1e-10, (1.0 + 1e-10) ** 2, 0)
        self.assertEqual(p_diag, [1.0 + 1e-10])
        self.assertEqual(q_diag, [0.0])

    def test_case_a_rank_one_guard(self):
        # With ceil returning one more than it should, the S > (u+t)^2 branch sees r = 2.
        fake_math = types.SimpleNamespace(ceil=lambda x: math.ceil(x) + 1, sqrt=math.sqrt)
        with mock.patch.object(C3, "math", fake_math):
            self.assertRefused(
                lambda: C3.construct_sharp_diagonal(1.0, 1.0, 5.0, 0),
                "CHECK FAILED: expected r==1 when S > (u+t)^2, got r=2",
            )

    def _patched_construction(self, change):
        real = C3.construct_sharp_diagonal
        built = []

        def construct(u, t, S, b):
            p_diag, q_diag = real(u, t, S, b)
            if not built:
                p_diag, q_diag = change(list(p_diag), list(q_diag))
                built.append(p_diag)
            return p_diag, q_diag

        return mock.patch.object(C3, "construct_sharp_diagonal", construct), built

    def test_built_P1_not_psd(self):
        patch, built = self._patched_construction(lambda p, q_: (p + [-1.0], q_ + [0.0]))
        with patch:
            text = self.assertRefused(C3.audit_sharpness, re.compile(r"CHECK FAILED: built P1 not PSD: \[.*\]"))
        self.assertEqual(text, f"CHECK FAILED: built P1 not PSD: {built[0]}")

    def test_built_rank_above_target(self):
        patch, _ = self._patched_construction(lambda p, q_: (p + [1.0] * 10, q_ + [-1.0] * 10))
        with patch:
            self.assertRefused(C3.audit_sharpness, re.compile(r"CHECK FAILED: built rank 1\d > target \d"))

    def test_built_positive_count_above_b(self):
        patch, _ = self._patched_construction(lambda p, q_: (p + [0.0] * 10, q_ + [1.0] * 10))
        with patch:
            self.assertRefused(C3.audit_sharpness, re.compile(r"CHECK FAILED: built n_\+\(Q\) 1\d > b=\d"))

    def test_built_tuple_mismatch(self):
        def nudge(p, q_):
            i = max(range(len(p)), key=lambda k: p[k])
            p[i] += 1e-6
            return p, q_

        patch, _ = self._patched_construction(nudge)
        with patch:
            self.assertRefused(C3.audit_sharpness, re.compile(r"CHECK FAILED: constructed tuple mismatch err=\S+"))

    def test_tuple_error_at_the_tolerance_is_refused(self):
        # The guard is err < 1e-9, so an error of exactly 1e-9 must be refused. abs is
        # shadowed in the module namespace; line 710 is its only use in check_003.
        with mock.patch.object(C3, "abs", lambda x: 1e-9, create=True):
            self.assertRefused(C3.audit_sharpness, "CHECK FAILED: constructed tuple mismatch err=1e-09")


if __name__ == "__main__":
    unittest.main()
