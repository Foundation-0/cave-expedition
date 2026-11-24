"""Input refusals (PREREG K6). Each refusal is one guard that raises GateError whose message starts with its code.
There is no switch in this module that turns a guard off. K6 shows that every guard is needed by deleting each one
from a copy of this file's source and checking that the suite then fails."""
import numpy as np


class GateError(ValueError):
    pass


BRANCHES = ("GATE_NUMERIC", "GATE_SHAPE", "GATE_EMPTY", "GATE_SHORT", "GATE_MISSING", "GATE_CONSTANT")


def validate_series(x, N):
    """Return x as a float64 1-D array, or raise GateError whose message starts with the branch code.
    Only integer, unsigned and float dtypes are numeric: bool, complex, string and object arrays are refused before any
    conversion (a conversion could drop an imaginary part or turn text into numbers)."""
    if type(N) is not int or N < 1:
        raise TypeError("N must be an int of at least 1")
    try:
        raw = np.asarray(x)
    except (TypeError, ValueError):
        raise GateError("GATE_NUMERIC: input cannot be read as an array")
    if raw.dtype.kind not in "iuf":
        raise GateError("GATE_NUMERIC: input is not integer or float valued")
    a = raw.astype(np.float64)
    if a.ndim != 1:
        raise GateError("GATE_SHAPE: input is not a one-dimensional series")
    if a.size == 0:
        raise GateError("GATE_EMPTY: input is empty")
    if a.size < N:
        raise GateError("GATE_SHORT: series has %d samples, fewer than N = %d" % (a.size, N))
    if not np.all(np.isfinite(a)):
        raise GateError("GATE_MISSING: series has missing or non-finite values")
    if np.all(a == a.flat[0]):
        raise GateError("GATE_CONSTANT: series is constant")
    return a
