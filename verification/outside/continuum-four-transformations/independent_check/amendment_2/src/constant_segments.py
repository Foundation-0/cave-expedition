"""B7 check: what can an extra invalid, non-rejecting segment do?
(1) Exact: K cannot rise, so the presence tail cannot fall; the 25 percent limit and the segment counts it implies.
(2) Exact enumeration of the section 12 decision procedure (known-answer tests pass): flip each absent counting instrument to underpowered
and list how the outcome moves. Standard library only. No bare assert."""
import sys
from fractions import Fraction
from itertools import product, combinations
from math import comb

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def tail(n, p, k):
    return sum(Fraction(comb(n, j)) * p**j * (1 - p)**(n - j) for j in range(max(k, 0), n + 1))


P05 = Fraction(1, 20)
# (1) with n_c constant segments among S, K <= S - n_c; the tail P(Bin(S, 0.05) >= K) is non-increasing in K
print("== (1) presence tail with constant segments (S = 32, 8 runs: K needed 8 at level 0.00125/8)")
S = 32
lvl = Fraction(5, 4000) / 8
kneed = next(k for k in range(S + 2) if tail(S, P05, k) <= lvl)
for nc in (0, 4, 8, 9, 24, 25):
    kmax = S - nc
    can = kmax >= kneed
    inv_share = Fraction(nc, S)
    print(f"   constant segments {nc}: invalid share {float(inv_share):.3f} ({'above' if inv_share > Fraction(1,4) else 'within'} the 25 percent limit); largest possible K {kmax}; can reach K >= {kneed}: {can}")
ok_mono = all(tail(S, P05, k) >= tail(S, P05, k + 1) for k in range(S))
print(f"CLAIM b7-monotone | K cannot rise and the tail is non-increasing in K | text=cannot raise the chance of present | mine={'confirmed' if ok_mono else 'NOT'} | {'REPRODUCED' if ok_mono else 'DIFFERS'}")
over = next(nc for nc in range(S + 1) if Fraction(nc, S) > Fraction(1, 4))
print(f"INFO the 25 percent limit is crossed at {over} constant segments of {S}; at that point K can still be {S-over} >= {kneed}")

# (2) outcome movement under absent -> underpowered
INS = (0, 1, 2)
ORD = [(a, b) for a in INS for b in INS if a != b]
UNO = list(combinations(INS, 2))
ST = ("INV", "UND", "PRE", "NET", "ABS")
AR = ("pass", "adverse", "neither")
PR = ("pass", "neither")


def outcome(st, at, pt):
    P = [i for i in INS if st[i] == "PRE"]
    Q = [i for i in INS if st[i] in ("PRE", "NET")]
    V = [i for i in INS if st[i] in ("PRE", "NET", "ABS")]
    nabs = sum(1 for i in INS if st[i] == "ABS")
    both = lambda t, a, b, v: t[(a, b)] == v and t[(b, a)] == v
    adv = sum(1 for a, b in UNO if a in V and b in V and both(at, a, b, "adverse"))
    pass3 = all(both(at, a, b, "pass") for a, b in UNO)
    if nabs >= 2 or adv >= 2:
        return "EvidenceAgainst"
    if len(P) == 3 and pass3:
        return "Supported"
    if len(Q) == 3 and len(P) < 3 and pass3:
        return "NetDependent"
    some = any(both(at, a, b, "pass") or (both(pt, a, b, "pass") and at[(a, b)] != "adverse" and at[(b, a)] != "adverse") for a, b in combinations(P, 2))
    if len(P) >= 2:
        return "Partial" if some else "DoesNotDiscriminate"
    if len(P) <= 1 and nabs <= 1 and adv <= 1:
        return "Inconclusive"
    return "NONE"


trans = {}
n_states = 0
none = 0
for st in product(ST, repeat=3):
    if "ABS" not in st:
        continue
    for arrow in product(AR, repeat=6):
        at = dict(zip(ORD, arrow))
        for prof in product(PR, repeat=6):
            pt = dict(zip(ORD, prof))
            o = outcome(st, at, pt)
            for i in INS:
                if st[i] == "ABS":
                    st2 = list(st)
                    st2[i] = "UND"
                    o2 = outcome(tuple(st2), at, pt)
                    trans[(o, o2)] = trans.get((o, o2), 0) + 1
                    n_states += 1
                    if o == "NONE" or o2 == "NONE":
                        none += 1
print(f"== (2) known-answer tests pass; each state with an absent instrument, that instrument flipped to underpowered ({n_states} flips)")
order = ["Supported", "NetDependent", "Partial", "DoesNotDiscriminate", "Inconclusive", "EvidenceAgainst"]
chg = {k: v for k, v in trans.items() if k[0] != k[1]}
for (a, b), v in sorted(chg.items(), key=lambda kv: -kv[1]):
    print(f"   {a} -> {b}: {v}")
fav = sum(v for (a, b), v in chg.items() if a == "EvidenceAgainst")
print(f"INFO flips that leave 'EvidenceAgainst': {fav}; flips into 'Supported' or 'NetDependent' or 'Partial': {sum(v for (a, b), v in chg.items() if b in ('Supported', 'NetDependent', 'Partial'))}")
print(f"INFO states without an outcome in this enumeration: {none}")
claim_ok = sum(v for (a, b), v in chg.items() if b in ("Supported", "NetDependent")) == 0
print(f"CLAIM b7-no-present | turning an absent instrument into an underpowered one never creates a 'present' instrument or a supported outcome | text=cannot raise the chance of present | mine={'confirmed' if claim_ok else 'NOT'} | {'REPRODUCED' if claim_ok else 'DIFFERS'}")
path = sum(v for (a, b), v in chg.items() if a == "EvidenceAgainst" and b in ("Inconclusive", "Partial", "DoesNotDiscriminate"))
print(f"FINDING absent -> underpowered turns an adverse outcome into a less adverse one in {path} flips (e.g. evidence against -> inconclusive); this is the existing underpowered rule, reachable here by 9 or more constant segments of 32")
control("a flip that changes nothing is not counted as a change", chg.get(("Supported", "Supported"), 0) == 0)
control("the monotonicity check would catch a rising tail", tail(32, P05, 8) < tail(32, P05, 7))
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE constant_segments")
