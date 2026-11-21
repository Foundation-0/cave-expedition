"""Shared helpers for the outside checks: locate public repo clones, report results.

Clone locations come from environment variables. Nothing here touches the network.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def require_dir(var, marker, what):
    """Return the absolute path in environment variable `var`, or exit with a plain message."""
    path = os.environ.get(var)
    if not path:
        raise SystemExit(
            "%s is not set. Point it at a local clone of %s (see README.md)." % (var, what))
    path = os.path.abspath(path)
    if not os.path.exists(os.path.join(path, marker)):
        raise SystemExit(
            "%s does not look like a clone of %s (missing %s)." % (var, what, marker))
    return path


def spectral_inertia_dir():
    return require_dir("SPECTRAL_INERTIA_DIR", "spectral_inertia",
                       "Foundation-0/spectral-inertia")


def loom_scripts_dir():
    return require_dir("LOOM_SCRIPTS_DIR", "inertia_cert.py",
                       "the scripts folder of siliconcordat/loom pull request 7")


def finish(name, ok, detail):
    """Print the single result line and exit 0 only if ok."""
    print("RESULT %s: %s %s" % (name, "PASS" if ok else "FAIL", detail))
    sys.stdout.flush()
    raise SystemExit(0 if ok else 1)
