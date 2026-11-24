import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import gates, segments
from kcommon import header, summary

N = 4096
BAD = {
    "GATE_NUMERIC": ["a", "b"],
    "GATE_SHAPE": np.ones((4200, 2)),
    "GATE_EMPTY": np.array([]),
    "GATE_SHORT": np.arange(100.0),
    "GATE_MISSING": np.where(np.arange(5000) == 17, np.nan, np.arange(5000.0)),
    "GATE_CONSTANT": np.full(5000, 3.0),
}


def code_of(f):
    try:
        f()
    except gates.GateError as e:
        return str(e).split(":")[0]
    except Exception as e:
        return "CRASH_" + type(e).__name__
    return "NO_ERROR"


def suite(disabled):
    """Failures of the gate suite. Empty means every refusal fires with its own code and a good input passes."""
    fails = []
    for code, bad in BAD.items():
        got = code_of(lambda: gates.validate_series(bad, N, disabled))
        if got != code:
            fails.append("%s: expected refusal, got %s" % (code, got))
    good = np.random.default_rng(1).standard_normal(5000)
    if code_of(lambda: gates.validate_series(good, N, disabled)) != "NO_ERROR":
        fails.append("good input refused")
    # the same gate guards the segment cutter
    got = code_of(lambda: segments.cut_segments(np.arange(100.0)))
    if got != "GATE_SHORT":
        fails.append("segment cutter does not refuse a short series (got %s)" % got)
    return fails


def main():
    header("K6", "gate checks: explicit refusals and must-fail inputs")
    f = suite(frozenset())
    print("all refusals active: %d failures" % len(f))
    for x in f:
        print("  FAIL", x)
    print("--- remove each refusal branch in turn; the suite must then fail")
    allflag = True
    for b in gates.BRANCHES:
        fb = suite(frozenset([b]))
        flagged = any(b in s for s in fb)
        allflag = allflag and flagged
        print("  without %-13s suite failures %d: %s" % (b, len(fb), "FLAGGED" if flagged else "NOT FLAGGED"))
    ok = (len(f) == 0) and allflag
    summary("K6", "PASS" if ok else "FAIL", "%d refusal branches, each refused its must-fail input; removal of each flagged: %s" % (len(gates.BRANCHES), "yes" if allflag else "NO"))


if __name__ == "__main__":
    main()
