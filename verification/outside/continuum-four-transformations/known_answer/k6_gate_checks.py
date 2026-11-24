"""K6 Gate checks (PREREG section 10): empty input, missing values, a constant series and a series shorter than N are rejected with
explicit errors, plus the numeric and shape refusals. Each refusal has a must-fail input that trips it. Removing any refusal branch
must make the test suite fail. usage: k6_gate_checks.py smoke|full (no size effect)"""
import os, sys, types
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import gates, segments
from kcommon import header, summary, parse_mode

N = 4096
BAD = {
    "GATE_NUMERIC": ["a", "b"],
    "GATE_NUMERIC ragged": [[1.0, 2.0], [3.0]],
    "GATE_NUMERIC bool": [True, False] * 2500,
    "GATE_NUMERIC complex": np.array([1 + 2j, 2 + 3j] * 2500),
    "GATE_SHAPE": np.ones((4200, 2)),
    "GATE_EMPTY": np.array([]),
    "GATE_SHORT": np.arange(100.0),
    "GATE_MISSING": np.where(np.arange(5000) == 17, np.nan, np.arange(5000.0)),
    "GATE_CONSTANT": np.full(5000, 3.0),
}


def code_of(f):
    try:
        f()
    except Exception as e:
        if type(e).__name__ == "GateError":   # by name, so that a mutant module's own GateError class is recognised
            return str(e).split(":")[0]
        return "CRASH_" + type(e).__name__
    return "NO_ERROR"


def suite(mod):
    """Failures of the gate suite run on the module `mod`. Empty means every refusal fires with its own code, a good input
    (float or integer counts) passes, and a bad N is refused."""
    fails = []
    for label, bad in BAD.items():
        code = label.split()[0]
        got = code_of(lambda: mod.validate_series(bad, N))
        if got != code:
            fails.append("%s: expected refusal, got %s" % (label, got))
    good = np.random.default_rng(1).standard_normal(5000)
    if code_of(lambda: mod.validate_series(good, N)) != "NO_ERROR":
        fails.append("good input refused")
    if code_of(lambda: mod.validate_series(np.arange(5000) % 7 + 1, N)) != "NO_ERROR":
        fails.append("integer counts refused")
    for badN in (True, 0, 4096.0):
        if code_of(lambda: mod.validate_series(good, badN)) != "CRASH_TypeError":
            fails.append("N = %r not refused with a TypeError" % (badN,))
    return fails


def mutants():
    """Source mutants of src/gates.py: each `raise GateError(...)` statement replaced by `pass` in turn (the guard is deleted).
    Returns list of (description, module built from the mutated source)."""
    path = os.path.join(HERE, "..", "src", "gates.py")
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    out = []
    for i, ln in enumerate(lines):
        st = ln.strip()
        if st.startswith("raise GateError("):
            code = st.split('"')[1].split(":")[0]
            m = list(lines)
            m[i] = ln[:len(ln) - len(ln.lstrip())] + "pass"
            mod = types.ModuleType("gates_mutant")
            exec(compile("\n".join(m), "gates_mutant_%d" % i, "exec"), mod.__dict__)
            out.append(("line %d (%s)" % (i + 1, code), code, mod))
    return out


def main():
    mode = parse_mode(sys.argv)
    header("K6", "gate checks: explicit refusals and must-fail inputs", mode)
    f = suite(gates)
    if code_of(lambda: segments.cut_segments(np.arange(100.0))) != "GATE_SHORT":
        f.append("segment cutter does not refuse a short series")
    print("all refusals active: %d failures" % len(f))
    for x in f:
        print("  FAIL", x)
    ms = mutants()
    codes = {m[1] for m in ms}
    print("--- delete each refusal from a copy of the source in turn; the suite must then fail (%d mutants, %d codes)" % (len(ms), len(codes)))
    allflag = len(codes) == len(gates.BRANCHES)
    for desc, code, mod in ms:
        fb = suite(mod)
        flagged = len(fb) > 0
        allflag = allflag and flagged
        print("  without the refusal at %-24s suite failures %d: %s" % (desc, len(fb), "FLAGGED" if flagged else "NOT FLAGGED"))
    ok = (len(f) == 0) and allflag
    summary("K6", "PASS" if ok else "FAIL", "%d refusal codes, %d deletion mutants; each refusal fired on its must-fail input; every deletion flagged: %s" % (len(codes), len(ms), "yes" if allflag else "NO"), mode)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
