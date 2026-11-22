#!/usr/bin/env python3
"""Mutation check for the guards of int_checker in eval_stack_certificate.py (review item 1).

Backs: REVIEW-RESPONSE.md item 1. Each guard of the integer checker is disabled in turn on a scratch
copy of eval_stack_certificate.py, and the copy must then FAIL, naming the control that guard isolates.
Needs: python3 (3.10 or newer) and SymPy. No network, no input files. The original file is not changed.
Run: python3 -I -B mutate_stack_guards.py
Time: about 20 seconds.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "eval_stack_certificate.py")

# (name, text to find, replacement, control that must turn red)
MUTANTS = [
    ("guard d < 0", "d < 0 for d in D", "d < -10**100 for d in D", "indefinite_matrix_with_negative_D"),
    ("guard type(d) is not int", "type(d) is not int or d < 0", "d < 0", "bool_D_identity_holds"),
    ("guard type(v) is not int on L", "any(type(v) is not int for v in r) for r in L", "False for r in L",
     "float_L_identity_holds"),
    ("guard type(v) is not int on x", "any(type(v) is not int for v in x)", "False", "float_refute_vector"),
    ("guard c <= 0", "or c <= 0 or", "or c < -10**100 or", "c_zero_and_D_zero_on_indefinite_matrix"),
    ("guard type(c) is not int", "type(c) is not int or c <= 0", "c <= 0", "fraction_c"),
]


def main():
    with open(SRC, encoding="utf-8") as fh:
        text = fh.read()
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, old, new, control in MUTANTS:
            if text.count(old) != 1:
                failures.append("%s: pattern found %d times, expected once" % (name, text.count(old)))
                continue
            path = os.path.join(tmp, "mutant.py")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text.replace(old, new))
            run = subprocess.run([sys.executable, "-I", "-B", path], capture_output=True, text=True, cwd=tmp)
            last = run.stdout.strip().splitlines()[-1] if run.stdout.strip() else ""
            red = run.returncode == 1 and ("control %s not refused" % control) in last
            print("%-34s -> exit %d, %s" % (name, run.returncode, last[:90]))
            if not red:
                failures.append("%s: expected control %s to turn red" % (name, control))
    if failures:
        print("RESULT: FAIL mutate_stack_guards: " + "; ".join(failures))
        return 1
    print("RESULT: PASS mutate_stack_guards: %d guards disabled one at a time, each turned its own control red" % len(MUTANTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
