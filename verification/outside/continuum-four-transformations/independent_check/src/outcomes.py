"""Independent encoding (rule 5 as revised: a profile pass counts only if the pair is arrow-adverse in neither direction) of the section 12 decision procedure (T3 and scale-flow T1), read from the revised text.
Enumerates every state. Standard library only. No bare assert.
State for T3: known-answer pass/fail (2) x status of each of 3 counting instruments in {INV, UND, PRE, NET, ABS} (5^3)
 x arrow result of each of 6 ordered pairs in {pass, adverse, neither} (3^6) x profile result in {pass, neither} (2^6).
State for T1: known-answer (2) x usable (2^3) x transfer of 6 ordered pairs in {pass, adverse, neither} (3^6)."""
import sys
from itertools import product, combinations

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


INS = (0, 1, 2)
ORD = [(a, b) for a in INS for b in INS if a != b]
UNO = list(combinations(INS, 2))
ST = ("INV", "UND", "PRE", "NET", "ABS")
AR = ("pass", "adverse", "neither")
PR = ("pass", "neither")


def conds_t3(kfail, st, arrow, prof, rule7_all_pairs):
    P = [i for i in INS if st[i] == "PRE"]
    Q = [i for i in INS if st[i] in ("PRE", "NET")]
    V = [i for i in INS if st[i] in ("PRE", "NET", "ABS")]
    nabs = sum(1 for i in INS if st[i] == "ABS")
    both = lambda t, a, b, v: t[(a, b)] == v and t[(b, a)] == v
    adv_in_V = sum(1 for a, b in UNO if a in V and b in V and both(arrow, a, b, "adverse"))
    adv_all = sum(1 for a, b in UNO if both(arrow, a, b, "adverse"))
    pass3 = all(both(arrow, a, b, "pass") for a, b in UNO)
    inside_P = [(a, b) for a, b in UNO if a in P and b in P]
    some_pass = any(both(arrow, a, b, "pass") or (both(prof, a, b, "pass") and arrow[(a, b)] != "adverse" and arrow[(b, a)] != "adverse") for a, b in inside_P)
    c = {}
    c[1] = bool(kfail)
    c[2] = nabs >= 2 or adv_in_V >= 2
    c[3] = len(P) == 3 and pass3
    c[4] = len(Q) == 3 and len(P) < 3 and pass3
    c[5] = len(P) >= 2 and some_pass
    c[6] = len(P) >= 2 and not some_pass
    adv7 = adv_all if rule7_all_pairs else adv_in_V
    c[7] = len(P) <= 1 and nabs <= 1 and adv7 <= 1
    return c


NAMES = {1: "Invalid", 2: "EvidenceAgainst", 3: "Supported", 4: "NetDependent", 5: "Partial", 6: "DoesNotDiscriminate", 7: "Inconclusive"}


def run_t3(rule7_all_pairs):
    total = 0
    uncovered = 0
    first = {}
    multi = {}
    ex_unc = None
    odd = {"partial_via_profile_on_adverse_pair": 0, "partial_with_one_adverse_pair": 0, "partial_with_absent": 0,
           "supported_without_all_present": 0, "favourable_with_kfail": 0, "evidence_against_with_2_present_and_a_pass_pair": 0,
           "inconclusive_with_adverse_pair_outside_V": 0}
    ex_odd = {}
    for kfail in (0, 1):
        for st in product(ST, repeat=3):
            for arrow in product(AR, repeat=6):
                at = dict(zip(ORD, arrow))
                for prof in product(PR, repeat=6):
                    pt = dict(zip(ORD, prof))
                    c = conds_t3(kfail, st, at, pt, rule7_all_pairs)
                    total += 1
                    hit = [r for r in range(1, 8) if c[r]]
                    if not hit:
                        uncovered += 1
                        ex_unc = ex_unc or (kfail, st, arrow, prof)
                        continue
                    o = hit[0]
                    first[o] = first.get(o, 0) + 1
                    if len(hit) > 1:
                        key = (o, kfail)
                        multi[key] = multi.get(key, 0) + 1
                    if kfail:
                        continue
                    both = lambda t, a, b, v: t[(a, b)] == v and t[(b, a)] == v
                    P = [i for i in INS if st[i] == "PRE"]
                    if o == 5:
                        # is the only way into Partial a pair that is arrow-adverse both ways?
                        ways = [(a, b) for a, b in UNO if a in P and b in P and (both(at, a, b, "pass") or (both(pt, a, b, "pass") and at[(a, b)] != "adverse" and at[(b, a)] != "adverse"))]
                        adv_either = lambda a, b: at[(a, b)] == "adverse" or at[(b, a)] == "adverse"
                        if (not ways) or any(adv_either(a, b) for a, b in ways):
                            odd["partial_via_profile_on_adverse_pair"] += 1
                            ex_odd.setdefault("partial_via_profile_on_adverse_pair", (st, arrow, prof))
                        if any(both(at, a, b, "adverse") for a, b in UNO):
                            odd["partial_with_one_adverse_pair"] += 1
                        if any(s == "ABS" for s in st):
                            odd["partial_with_absent"] += 1
                    if o == 7 and any(both(at, a, b, "adverse") for a, b in UNO):
                        odd["inconclusive_with_adverse_pair_outside_V"] += 1
                        ex_odd.setdefault("inconclusive_with_adverse_pair_outside_V", (st, arrow, prof))
    return total, uncovered, first, multi, ex_unc, odd, ex_odd


def conds_t1(kfail, use, tr):
    V = [i for i in INS if use[i]]
    both = lambda a, b, v: tr[(a, b)] == v and tr[(b, a)] == v
    adv = sum(1 for a, b in UNO if a in V and b in V and both(a, b, "adverse"))
    inV = [(a, b) for a, b in UNO if a in V and b in V]
    some = any(both(a, b, "pass") for a, b in inV)
    c = {1: bool(kfail), 2: adv >= 2, 3: len(V) == 3 and all(both(a, b, "pass") for a, b in UNO),
         4: some, 5: len(V) >= 2 and not some, 6: len(V) <= 1}
    return c


for rule7 in (False,):
    total, unc, first, multi, ex_unc, odd, ex_odd = run_t3(rule7)
    label = "rule 7 counts adverse pairs among all pairs" if rule7 else "rule 7 counts adverse pairs inside V"
    print(f"== T3, {label}")
    expect = 2 * 5**3 * 3**6 * 2**6
    print(f"states enumerated: {total} (text: 11,664,000; 2 x 5^3 x 3^6 x 2^6 = {expect}); states meeting no rule: {unc}")
    print("first-match outcome counts:", {NAMES[k]: v for k, v in sorted(first.items())})
    kp = {NAMES[o]: v for (o, k), v in sorted(multi.items()) if k == 0}
    print("states with known-answer pass whose outcome is also met by a lower-ranked rule:", kp)
    print("   text A9: 11,200 evidence against, all 64 supported, 448 net-dependent")
    if ex_unc:
        print("   example state meeting no rule:", ex_unc)
    print("odd states (known-answer pass):", odd)
    for k, v in ex_odd.items():
        print(f"   example {k}: status {v[0]} arrow {v[1]} profile {v[2]}")
    if rule7 is False:
        claim_ok = (total == 11664000 and unc == 0)
        print(f"CLAIM t3-states | 11,664,000 states, every state one outcome | mine {total}, uncovered {unc} | {'REPRODUCED' if claim_ok else 'DIFFERS'}")
        pc = first.get(5, 0)
        print(f"CLAIM t3-partial | partial states after the change | text=129,867 | mine={pc} | {'REPRODUCED' if pc == 129867 else 'DIFFERS'}")
        print(f"CLAIM t3-partial-moved | partial fell from 215,506 and the difference moved to does-not-discriminate | text=difference moves to DND | mine: partial {215506 - pc} fewer, DND {first.get(6, 0)} (was 379,566; change {first.get(6, 0) - 379566}) | {'REPRODUCED' if (215506 - pc) == (first.get(6, 0) - 379566) else 'DIFFERS'}")
        print(f"CLAIM t3-partial-adverse | partial states where the pair that carries partial is arrow-adverse in either direction | text=none | mine={odd['partial_via_profile_on_adverse_pair']} | {'REPRODUCED' if odd['partial_via_profile_on_adverse_pair'] == 0 else 'DIFFERS'}")


# T1
total = unc = 0
first = {}
multi = {}
for kfail in (0, 1):
    for use in product((0, 1), repeat=3):
        for tr in product(AR, repeat=6):
            t = dict(zip(ORD, tr))
            c = conds_t1(kfail, use, t)
            total += 1
            hit = [r for r in range(1, 7) if c[r]]
            if not hit:
                unc += 1
                continue
            first[hit[0]] = first.get(hit[0], 0) + 1
            if len(hit) > 1 and not kfail:
                multi[hit[0]] = multi.get(hit[0], 0) + 1
N1 = {1: "Invalid", 2: "EvidenceAgainst", 3: "Supported", 4: "Partial", 5: "DoesNotDiscriminate", 6: "Inconclusive"}
print("== T1 scale flow")
print(f"states enumerated: {total} (text 11,664 = 2 x 2^3 x 3^6 = {2*8*729}); uncovered {unc}")
print("first-match counts:", {N1[k]: v for k, v in sorted(first.items())})
print("known-answer pass, also met by a lower-ranked rule:", {N1[k]: v for k, v in sorted(multi.items())}, "(text: 25 evidence against, 1 supported)")
ok1 = total == 11664 and unc == 0 and multi.get(2) == 25 and multi.get(3) == 1
print(f"CLAIM t1-states | text 11,664 states, exactly one outcome, 25 and 1 | mine as above | {'REPRODUCED' if ok1 else 'DIFFERS'}")
# T1 oddity: Partial without any presence evidence
print("INFO T1 has no presence test: 'Partial' and 'Supported' need only transfer passes between usable instruments; "
      "usable means not invalid for T3 and >= 12 segments at some level.")

# must-fail controls: a broken precedence (Supported before Evidence against) must give a state with two outcomes of different class
def broken_first(c):
    order = (1, 5, 2, 3, 4, 6, 7)
    for r in order:
        if c[r]:
            return r
st = ("PRE", "PRE", "PRE")
arrow = {o: "pass" for o in ORD}
for o in ((0, 1), (1, 0), (0, 2), (2, 0)):
    arrow[o] = "adverse"          # pairs {0,1} and {0,2} adverse both ways; pair {1,2} passes both ways
prof = {o: "neither" for o in ORD}
c = conds_t3(0, st, arrow, prof, False)
control("broken precedence (Partial ranked above Evidence against) changes the outcome on a constructed state",
        broken_first(c) != [r for r in range(1, 8) if c[r]][0])
control("an all-pass all-present state is Supported", [r for r in range(1, 8) if conds_t3(0, st, {o: 'pass' for o in ORD}, prof, False)[r]][0] == 3)
control("a known-answer failure is Invalid whatever else", [r for r in range(1, 8) if conds_t3(1, st, {o: 'pass' for o in ORD}, prof, False)[r]][0] == 1)
if FAILS:
    print("FAILED CONTROLS:", FAILS); sys.exit(1)
print("DONE outcomes")
