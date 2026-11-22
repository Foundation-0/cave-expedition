"""Input refusals (PREREG K6). Each branch has a code. A branch can be switched off
through `disabled`, only so that the known-answer suite can show it notices the removal."""
import numpy as np


class GateError(ValueError):
    pass


BRANCHES = ("GATE_NUMERIC", "GATE_SHAPE", "GATE_EMPTY", "GATE_SHORT", "GATE_MISSING", "GATE_CONSTANT")


def validate_series(x, N, disabled=frozenset()):
    """Return x as a float64 1-D array, or raise GateError whose message starts with the branch code."""
    a = None
    try:
        a = np.asarray(x, dtype=np.float64)
    except (TypeError, ValueError):
        if "GATE_NUMERIC" not in disabled:
            raise GateError("GATE_NUMERIC: input is not numeric")
    if a is None:
        return None
    if a.ndim != 1 and "GATE_SHAPE" not in disabled:
        raise GateError("GATE_SHAPE: input is not a one-dimensional series")
    if a.size == 0 and "GATE_EMPTY" not in disabled:
        raise GateError("GATE_EMPTY: input is empty")
    if a.size < N and "GATE_SHORT" not in disabled:
        raise GateError("GATE_SHORT: series has %d samples, fewer than N = %d" % (a.size, N))
    if a.size > 0 and not np.all(np.isfinite(a)) and "GATE_MISSING" not in disabled:
        raise GateError("GATE_MISSING: series has missing or non-finite values")
    if a.size > 0 and np.all(a == a.flat[0]) and "GATE_CONSTANT" not in disabled:
        raise GateError("GATE_CONSTANT: series is constant")
    return a
