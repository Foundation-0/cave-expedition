#!/usr/bin/env python3
"""Check script advocate_trace_law_general.py: AUDIT-006 Check 4 (trace-slack law), symbolic part.

Question: is the threshold T*tau = w^2/q sufficient for R_opt > 1 against the worst
admissible noise N = tau v v^T (noise aligned with the known component), for general
q, w > 0 and dimension n? F(N) = (m - t)^2 - (S - t^2), and R_opt > 1 in branch 1
exactly when F > 0. Setting: T = n, Q = q v v^T, P = w I_2.

Backs: VERDICTS.md section 3, 'continuum 3, trace-slack: exact law -> a certified
sufficient condition'. The check shows F at the law is a positive-coefficient
polynomial over a positive denominator for n = 3, 4, 5, 8, 20, so the law is
sufficient there whenever the branch-1 condition holds. The branch-1 expression is
printed for reference and is not claimed positive for all q, w.
Needs: python3 (3.10 or newer) and SymPy. No network, no files, no random numbers.
Run: python3 -I -B advocate_trace_law_general.py
     (also python3 -I -O -B and python3 -I -B -W error, same output)
Time: about 1 second.
Every failed check exits 1. On success the last line starts with RESULT: PASS.
"""
import sys

import sympy as sp

q, w, tau = sp.symbols("q w tau", positive=True)


def main():
    print("seeds: none (no random numbers)")
    bad = []
    dims = (3, 4, 5, 8, 20)
    for n in dims:
        eig = [q, w - tau, w - tau] + [-tau] * (n - 3)   # worst case: N = tau v v^T cancels the shift on Q's direction
        m = sum(eig)
        S = sum(e**2 for e in eig)
        t = q - n * tau
        F = sp.expand((m - t)**2 - (S - t**2))
        Fl = sp.factor(sp.simplify(F.subs(tau, w**2 / (q * n))))
        print(n, "F at law =", Fl)
        B1 = sp.factor(sp.simplify((t * m - S).subs(tau, w**2 / (q * n))))
        print("   branch1 t*m - S at law =", B1)
        num, den = sp.fraction(sp.together(Fl))
        coeffs = sp.Poly(sp.expand(num), q, w).coeffs()
        den_ok = sp.Poly(sp.expand(den), q, w).coeffs()
        if not (all(c > 0 for c in coeffs) and all(c > 0 for c in den_ok)):
            bad.append(n)
    if bad:
        print("RESULT: FAIL F at the law is not manifestly positive for n in %s" % bad)
        return 1
    print("RESULT: PASS advocate_trace_law_general: F at the law has all-positive coefficients over a positive denominator for n in %s"
          % ", ".join(str(n) for n in dims))
    return 0


if __name__ == "__main__":
    sys.exit(main())
