"""Shared helpers: locate the public target clone and read witness tables from it.

The target is a clone of Foundation-0/incentre-lattices at the head of draft pull
request 106. Give its folder as the first non-flag command-line argument or in the
environment variable INCENTRE_LATTICES_PR106. The clone is only read, and only as
data: the verifier file is parsed with ast and never executed.
"""
import ast
import os
import sys

VERIFIER_REL = os.path.join("results", "expedition-dn-e8-folds", "verify_bw16_leech24.py")
ENV_NAME = "INCENTRE_LATTICES_PR106"


def need(cond, msg):
    """Explicit check that exits non-zero (never a bare assert)."""
    if not cond:
        raise SystemExit("CHECK FAILED: " + msg)


def clone_dir():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = args[0] if args else os.environ.get(ENV_NAME)
    if not d:
        raise SystemExit("Missing target clone. Pass the folder of a clone of Foundation-0/incentre-lattices "
                         "at the head of draft PR 106 as the first argument, or set " + ENV_NAME + ".")
    return d


def verifier_path():
    p = os.path.join(clone_dir(), VERIFIER_REL)
    if not os.path.isfile(p):
        raise SystemExit("Cannot find " + VERIFIER_REL + " under the given clone folder.")
    return p


_CACHE = {}


def team_data(name):
    """Literal value assigned to a top-level name in the target's verifier (data only)."""
    if "tree" not in _CACHE:
        with open(verifier_path(), encoding="utf-8") as fh:
            _CACHE["tree"] = ast.parse(fh.read())
    for node in _CACHE["tree"].body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name):
            return ast.literal_eval(node.value)
    raise SystemExit("Table " + name + " not found in the target verifier.")
