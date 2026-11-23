"""The one tie rule for floating values (PREREG sections 4.3 and 11a, D4 as replaced by Amendment 2, B8).

Two floating values a and b count as tied when |a - b| <= 1e-12 x max(1, |a|, |b|). Exact quantities (pattern counts, ranks,
binomial tails, levels, thresholds) are compared exactly and never use this rule. A tie never creates a verdict in either
direction: it counts against the real series in the segment p-value, against w_A in the transfer p-value, against departure
for a K5 unit, and not as "below" when deciding an adverse transfer."""
import numpy as np

REL = 1e-12


def tied(a, b):
    """Elementwise tie test. Non-finite entries never tie (an infinity ties with nothing, not even itself)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ok = np.isfinite(a) & np.isfinite(b)
    aa = np.where(ok, a, 0.0)
    bb = np.where(ok, b, 0.0)
    scale = np.maximum(1.0, np.maximum(np.abs(aa), np.abs(bb)))
    return ok & (np.abs(aa - bb) <= REL * scale)


def at_or_above(a, b):
    """a >= b, or a ties with b. Used wherever a tie must count against a finding. False if either value is not finite: a non-finite
    value never gives a verdict, so an infinity does not count against anything (and -inf, a surrogate with no lag kept, is never at
    or above)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ok = np.isfinite(a) & np.isfinite(b)
    return ok & ((a >= b) | tied(a, b))


def below(a, b):
    """a < b and not tied with b. False if either value is not finite."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ok = np.isfinite(a) & np.isfinite(b)
    return ok & (a < b) & ~tied(a, b)
