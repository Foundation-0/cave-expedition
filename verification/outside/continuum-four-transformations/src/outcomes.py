"""Outcome decision procedure of PREREG section 12, as pure functions from a result vector to exactly one outcome.
Booleans, strings and integers only."""
from itertools import combinations

INSTR = (0, 1, 2)  # the counting instruments: GW, SEIS, Wind/WAVES
PAIRS = tuple(combinations(INSTR, 2))
ORDERED = tuple((i, j) for i in INSTR for j in INSTR if i != j)
STATUSES = ("invalid", "underpowered", "present", "net-dependent", "absent")
ARROW = ("pass", "adverse", "neither")
PROFILE = ("pass", "neither")
OUT_T3 = ("INVALID", "EVIDENCE AGAINST", "SUPPORTED", "NET-DEPENDENT", "PARTIAL", "DOES NOT DISCRIMINATE", "INCONCLUSIVE")
OUT_T1 = ("INVALID", "EVIDENCE AGAINST", "SUPPORTED", "PARTIAL", "DOES NOT DISCRIMINATE", "INCONCLUSIVE")


def _check_t3(kat_ok, status, arrow, profile):
    if not isinstance(kat_ok, bool):
        raise TypeError("kat_ok must be a bool")
    if len(status) != 3 or any(s not in STATUSES for s in status):
        raise ValueError("status must be three of " + str(STATUSES))
    if set(arrow) != set(ORDERED) or any(v not in ARROW for v in arrow.values()):
        raise ValueError("arrow needs a result in %s for each of the 6 ordered pairs" % (ARROW,))
    if set(profile) != set(ORDERED) or any(v not in PROFILE for v in profile.values()):
        raise ValueError("profile needs a result in %s for each of the 6 ordered pairs" % (PROFILE,))


def outcome_t3(kat_ok, status, arrow, profile):
    """status: tuple of 3 statuses for GW, SEIS, WAVES. arrow: dict (i, j) -> 'pass'|'adverse'|'neither' for each ordered
    pair (template from i, scored on j). profile: dict (i, j) -> 'pass'|'neither'. Returns exactly one of OUT_T3.
    The first rule that applies sets the outcome."""
    _check_t3(kat_ok, status, arrow, profile)
    P = {i for i in INSTR if status[i] == "present"}
    Q = {i for i in INSTR if status[i] in ("present", "net-dependent")}
    V = {i for i in INSTR if status[i] in ("present", "net-dependent", "absent")}
    n_absent = sum(1 for i in INSTR if status[i] == "absent")

    def both(d, v, pair):
        i, j = pair
        return d[(i, j)] == v and d[(j, i)] == v

    def adverse_any(pair):
        i, j = pair
        return arrow[(i, j)] == "adverse" or arrow[(j, i)] == "adverse"

    n_adverse_pairs = sum(1 for p in PAIRS if set(p) <= V and both(arrow, "adverse", p))
    all_arrow_pass = all(both(arrow, "pass", p) for p in PAIRS)
    # rule 5: a pair inside P passes both ways on the arrow, or both ways on the profile while its arrow is adverse in neither direction
    some_pair = any(set(p) <= P and (both(arrow, "pass", p) or (both(profile, "pass", p) and not adverse_any(p))) for p in PAIRS)
    if not kat_ok:
        return "INVALID"
    if n_absent >= 2 or n_adverse_pairs >= 2:
        return "EVIDENCE AGAINST"
    if len(P) == 3 and all_arrow_pass:
        return "SUPPORTED"
    if len(Q) == 3 and len(P) < 3 and all_arrow_pass:
        return "NET-DEPENDENT"
    if len(P) >= 2 and some_pair:
        return "PARTIAL"
    if len(P) >= 2:
        return "DOES NOT DISCRIMINATE"
    if len(P) <= 1 and n_absent <= 1 and n_adverse_pairs <= 1:
        return "INCONCLUSIVE"
    raise RuntimeError("no rule applies to this state (the procedure must cover every state)")


def outcome_t1(kat_ok, usable, transfer):
    """Scale-flow half of T1. usable: tuple of 3 bools. transfer: dict (i, j) -> 'pass'|'adverse'|'neither'.
    Returns exactly one of OUT_T1."""
    if not isinstance(kat_ok, bool):
        raise TypeError("kat_ok must be a bool")
    if len(usable) != 3 or any(not isinstance(u, bool) for u in usable):
        raise ValueError("usable must be three bools")
    if set(transfer) != set(ORDERED) or any(v not in ARROW for v in transfer.values()):
        raise ValueError("transfer needs a result in %s for each of the 6 ordered pairs" % (ARROW,))
    V = {i for i in INSTR if usable[i]}

    def both(v, pair):
        i, j = pair
        return transfer[(i, j)] == v and transfer[(j, i)] == v

    n_adv = sum(1 for p in PAIRS if set(p) <= V and both("adverse", p))
    n_pass = sum(1 for p in PAIRS if set(p) <= V and both("pass", p))
    if not kat_ok:
        return "INVALID"
    if n_adv >= 2:
        return "EVIDENCE AGAINST"
    if len(V) == 3 and n_pass == 3:
        return "SUPPORTED"
    if n_pass >= 1:
        return "PARTIAL"
    if len(V) >= 2:
        return "DOES NOT DISCRIMINATE"
    return "INCONCLUSIVE"
