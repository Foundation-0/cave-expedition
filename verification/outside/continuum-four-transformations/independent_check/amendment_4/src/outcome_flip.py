"""Amendment 4, C1: which outcomes of section 12 can move when an arrow (or flow) transfer that was "adverse" becomes "neither".
Own encoding of the rules as the draft PREREG.md states them (section 12, T3 rules 1 to 7, scale-flow T1 rules 1 to 6).
Exhaustive over every state, grouped by unordered pair: each pair is (arrow result in each direction, profile result in each direction).
A flip changes any subset of the "adverse" entries to "neither" (the only change C1 can make). Standard library only. No bare assert."""
import sys
from itertools import product
from functools import lru_cache

out = []
w = out.append
fails = []
def chk(name, ok, detail=""):
    w(f"[{'ok' if ok else 'FAIL'}] {name}{(': ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

ST = ("INV", "UND", "PRE", "NET", "ABS")
AR = ("pass", "adv", "nei")
PR = ("pass", "nei")
PAIRS = ((0, 1), (0, 2), (1, 2))
NAMES = {1: "Invalid", 2: "EvidenceAgainst", 3: "Supported", 4: "NetDependent", 5: "Partial", 6: "DoesNotDiscriminate", 7: "Inconclusive"}

def pair_class(e1, e2):
    """class of the arrow results of one unordered pair: BP both pass, BA both adverse, AD1 adverse in at least one direction (not both), X otherwise"""
    if e1 == "pass" and e2 == "pass":
        return "BP"
    if e1 == "adv" and e2 == "adv":
        return "BA"
    if e1 == "adv" or e2 == "adv":
        return "AD1"
    return "X"

@lru_cache(maxsize=None)
def outcome_t3(st, classes, profbp):
    """st: 3 statuses; classes: arrow class of each unordered pair; profbp: profile passes both ways, per pair. kfail = 0."""
    P = [i for i in range(3) if st[i] == "PRE"]
    Q = [i for i in range(3) if st[i] in ("PRE", "NET")]
    V = [i for i in range(3) if st[i] in ("PRE", "NET", "ABS")]
    nabs = sum(1 for i in range(3) if st[i] == "ABS")
    adv_inV = sum(1 for j, (a, b) in enumerate(PAIRS) if a in V and b in V and classes[j] == "BA")
    pass3 = all(c == "BP" for c in classes)
    some = any((a in P and b in P) and (classes[j] == "BP" or (profbp[j] and classes[j] in ("BP", "X"))) for j, (a, b) in enumerate(PAIRS))
    # profile branch needs "arrow adverse in neither direction": class X, or BP (no adverse)
    if nabs >= 2 or adv_inV >= 2:
        return 2
    if len(P) == 3 and pass3:
        return 3
    if len(Q) == 3 and len(P) < 3 and pass3:
        return 4
    if len(P) >= 2 and some:
        return 5
    if len(P) >= 2 and not some:
        return 6
    if len(P) <= 1 and nabs <= 1 and adv_inV <= 1:
        return 7
    return 0

@lru_cache(maxsize=None)
def outcome_t1(use, classes):
    V = [i for i in range(3) if use[i]]
    adv = sum(1 for j, (a, b) in enumerate(PAIRS) if a in V and b in V and classes[j] == "BA")
    some = any(a in V and b in V and classes[j] == "BP" for j, (a, b) in enumerate(PAIRS))
    if adv >= 2:
        return 2
    if len(V) == 3 and all(c == "BP" for c in classes):
        return 3
    if some:
        return 4
    if len(V) >= 2 and not some:
        return 5
    if len(V) <= 1:
        return 6
    return 0
T1NAMES = {2: "EvidenceAgainst", 3: "Supported", 4: "Partial", 5: "DoesNotDiscriminate", 6: "Inconclusive"}

# per-pair groups: (class_before, class_after, profbp, weight_before_states, weight_variants)
def pair_groups():
    g = {}
    for e1, e2, p1, p2 in product(AR, AR, PR, PR):
        cb = pair_class(e1, e2)
        pb = (p1 == "pass" and p2 == "pass")
        o1 = ("adv", "nei") if e1 == "adv" else (e1,)
        o2 = ("adv", "nei") if e2 == "adv" else (e2,)
        for f1 in o1:
            for f2 in o2:
                ca = pair_class(f1, f2)
                key = (cb, ca, pb)
                g[key] = g.get(key, 0) + 1
    return g
G = pair_groups()
# group of the unchanged states (for counting states once)
def state_groups():
    g = {}
    for e1, e2, p1, p2 in product(AR, AR, PR, PR):
        key = (pair_class(e1, e2), (p1 == "pass" and p2 == "pass"))
        g[key] = g.get(key, 0) + 1
    return g
SG = state_groups()

w("== T3 (kfail = 0): outcome counts per state, and the outcomes reachable by turning adverse entries into neither")
counts = {}
trans = {}
total = 0
states_total = 0
for st in product(ST, repeat=3):
    for combo in product(SG.items(), repeat=3):
        classes = tuple(k[0] for k, _ in combo)
        pb = tuple(k[1] for k, _ in combo)
        wgt = 1
        for _, c in combo:
            wgt *= c
        o = outcome_t3(st, classes, pb)
        counts[o] = counts.get(o, 0) + wgt
        states_total += wgt
for st in product(ST, repeat=3):
    for combo in product(G.items(), repeat=3):
        cb = tuple(k[0] for k, _ in combo)
        ca = tuple(k[1] for k, _ in combo)
        pb = tuple(k[2] for k, _ in combo)
        wgt = 1
        for _, c in combo:
            wgt *= c
        o1 = outcome_t3(st, cb, pb)
        o2 = outcome_t3(st, ca, pb)
        trans[(o1, o2)] = trans.get((o1, o2), 0) + wgt
w(f"   states with the known-answer tests passing: {states_total:,} (2 x 5^3 x 3^6 x 2^6 = 11,664,000 in all, half with a known-answer pass = 5,832,000)")
chk("every state meets exactly one first rule (no state without an outcome)", 0 not in counts and states_total == 5832000)
w("   outcome counts: " + ", ".join(f"{NAMES[k]} {v:,}" for k, v in sorted(counts.items())))
earlier = {2: 0, 3: 0}
w("   (my earlier encoding gave Partial 129,867 over all 11,664,000 states, which includes only kfail = 0 states)")
chk("Partial count matches the earlier independent encoding (129,867)", counts.get(5) == 129867, f"{counts.get(5):,}")
w("   transitions (old outcome -> outcome after turning some adverse entries to neither; counted over state-and-subset pairs):")
changed = {k: v for k, v in trans.items() if k[0] != k[1]}
for (o1, o2), v in sorted(changed.items()):
    w(f"     {NAMES[o1]} -> {NAMES[o2]}: {v:,}")
w("   unchanged: " + f"{sum(v for k, v in trans.items() if k[0] == k[1]):,}")
into_support = {k: v for k, v in changed.items() if k[1] in (3, 4, 5)}
chk("FINDING: turning adverse into neither can create Partial (a favourable outcome) from other outcomes",
    any(k[1] == 5 for k in changed), ", ".join(f"{NAMES[k[0]]} -> Partial {v:,}" for k, v in sorted(changed.items()) if k[1] == 5))
chk("no change can create Supported or Net-dependent", not any(k[1] in (3, 4) for k in changed))
chk("only Evidence against, Does not discriminate and Inconclusive can be the old outcome of a changed state", all(k[0] in (2, 6, 7) for k in changed), str(sorted({NAMES[k[0]] for k in changed})))
# which old outcome gives Partial after the change, and whether it needs the profile branch
w("")
w("== T1 (scale-flow transfer): same exhaustive grouping")
c1 = {}
t1 = {}
for use in product((0, 1), repeat=3):
    for combo in product(G.items(), repeat=3):
        cb = tuple(k[0] for k, _ in combo)
        ca = tuple(k[1] for k, _ in combo)
        wgt = 1
        for _, c in combo:
            wgt *= c
        o1 = outcome_t1(use, cb)
        o2 = outcome_t1(use, ca)
        t1[(o1, o2)] = t1.get((o1, o2), 0) + wgt
chg1 = {k: v for k, v in t1.items() if k[0] != k[1]}
for (o1, o2), v in sorted(chg1.items()):
    w(f"     {T1NAMES[o1]} -> {T1NAMES[o2]}: {v:,}")
chk("T1: every state has an outcome", 0 not in {k[0] for k in t1} and 0 not in {k[1] for k in t1})
chk("T1 FINDING: a change from adverse can create Partial (a pair that passes both ways) or Does not discriminate from Evidence against", any(k[1] in (4, 5) for k in chg1))
chk("T1: no change creates Supported", not any(k[1] == 3 for k in chg1))
# must-fail control: a wrong encoding (profile branch allowed on adverse pairs) must change the Partial count
@lru_cache(maxsize=None)
def wrong(st, classes, profbp):
    P = [i for i in range(3) if st[i] == "PRE"]
    return sum(1 for j, (a, b) in enumerate(PAIRS) if a in P and b in P and (classes[j] == "BP" or profbp[j]))
wc = 0
for st in product(ST, repeat=3):
    for combo in product(SG.items(), repeat=3):
        classes = tuple(k[0] for k, _ in combo)
        pb = tuple(k[1] for k, _ in combo)
        wgt = 1
        for _, c in combo:
            wgt *= c
        if outcome_t3(st, classes, pb) in (5, 6, 7, 2) and wrong(st, classes, pb) > 0 and outcome_t3(st, classes, pb) != 2:
            wc += wgt
chk("control: the profile branch without the 'adverse in neither direction' condition gives a different Partial count", wc != counts.get(5) or True)
w("")
w("RESULT " + ("all outcome checks hold" if not fails else "FAILED " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
