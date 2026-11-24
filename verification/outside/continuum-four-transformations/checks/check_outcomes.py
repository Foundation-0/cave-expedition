"""Exhaustive check that the outcome procedure of PREREG section 12 maps every result state to exactly one
outcome, for T3 and for the scale-flow half of T1, and a check of the Wind/WAVES channel-cycling rule.
Integers and booleans only."""
from itertools import product, combinations
from collections import Counter
import sys

out = []
w = out.append
INSTR = ("GW", "SEIS", "WAVES")            # the instruments that can count toward support
PAIRS = list(combinations(range(3), 2))     # unordered pairs
ORDERED = [(i, j) for i in range(3) for j in range(3) if i != j]
STATUS = ("invalid", "underpowered", "present", "net-dependent", "absent")
ORDER_T3 = ("INVALID", "EVIDENCE AGAINST", "SUPPORTED", "NET-DEPENDENT", "PARTIAL", "DOES NOT DISCRIMINATE", "INCONCLUSIVE")
ORDER_T1 = ("INVALID", "EVIDENCE AGAINST", "SUPPORTED", "PARTIAL", "DOES NOT DISCRIMINATE", "INCONCLUSIVE")


def t3_predicates(kat_ok, status, sig):
    """sig[p] = (arrow passes both ways, arrow adverse both ways, profile passes both ways,
    arrow adverse in at least one direction) for unordered pair p."""
    V = {i for i in range(3) if status[i] in ("present", "net-dependent", "absent")}
    P = {i for i in range(3) if status[i] == "present"}
    Q = {i for i in range(3) if status[i] in ("present", "net-dependent")}
    nA = sum(1 for i in range(3) if status[i] == "absent")
    nadv = sum(1 for k, p in enumerate(PAIRS) if set(p) <= V and sig[k][1])
    all_arrow = all(sig[k][0] for k in range(3))
    # rule 5: the arrow passes both ways, or the profile passes both ways while the arrow is adverse in neither direction
    some_pair = any(set(p) <= P and (sig[k][0] or (sig[k][2] and not sig[k][3])) for k, p in enumerate(PAIRS))
    return {
        "INVALID": not kat_ok,
        "EVIDENCE AGAINST": kat_ok and (nA >= 2 or nadv >= 2),
        "SUPPORTED": kat_ok and len(P) == 3 and all_arrow,
        "NET-DEPENDENT": kat_ok and len(Q) == 3 and len(P) < 3 and all_arrow,
        "PARTIAL": kat_ok and len(P) >= 2 and some_pair,
        "DOES NOT DISCRIMINATE": kat_ok and len(P) >= 2 and not some_pair,
        "INCONCLUSIVE": kat_ok and len(P) <= 1 and nA <= 1 and nadv <= 1,
    }


def t1_predicates(k_ok, valid, sig):
    """sig[p] = (transfer passes both ways, transfer adverse both ways) for unordered pair p."""
    V = {i for i in range(3) if valid[i]}
    nadv = sum(1 for k, p in enumerate(PAIRS) if set(p) <= V and sig[k][1])
    npass = sum(1 for k, p in enumerate(PAIRS) if set(p) <= V and sig[k][0])
    return {
        "INVALID": not k_ok,
        "EVIDENCE AGAINST": k_ok and nadv >= 2,
        "SUPPORTED": k_ok and len(V) == 3 and npass == 3,
        "PARTIAL": k_ok and npass >= 1,
        "DOES NOT DISCRIMINATE": k_ok and len(V) >= 2 and npass == 0,
        "INCONCLUSIVE": k_ok and len(V) <= 1,
    }


def resolve(preds, order):
    hits = [o for o in order if preds[o]]
    if not hits:
        raise ValueError("state matches no outcome")
    return hits[0], len(hits)


# T3: enumerate every ordered-pair result (arrow in {pass, adverse, neither}, profile in {pass, neither}),
# reduce to the per-unordered-pair signature with exact multiplicities, then enumerate all states.
sig_mult = Counter()
cells = list(product(("pass", "adverse", "neither"), ("pass", "neither")))
for combo in product(cells, repeat=len(ORDERED)):
    r = dict(zip(ORDERED, combo))
    sig = tuple((r[(i, j)][0] == "pass" and r[(j, i)][0] == "pass",
                 r[(i, j)][0] == "adverse" and r[(j, i)][0] == "adverse",
                 r[(i, j)][1] == "pass" and r[(j, i)][1] == "pass",
                 r[(i, j)][0] == "adverse" or r[(j, i)][0] == "adverse") for i, j in PAIRS)
    sig_mult[sig] += 1
total = 0
outcome_count = Counter()
multi = Counter()
for kat_ok in (True, False):
    for status in product(STATUS, repeat=3):
        for sig, m in sig_mult.items():
            o, nh = resolve(t3_predicates(kat_ok, status, sig), ORDER_T3)
            total += m
            outcome_count[o] += m
            if nh > 1:
                multi[o] += m
w("== T3 outcome procedure (rule 5: a profile pass counts only if the arrow is adverse in neither direction; rule 7 counts adverse pairs inside V) ==")
w(f"states enumerated: {total} = 2 (known-answer tests) x 5^3 (instrument status) x 6^6 (ordered-pair results)")
w(f"states matching no outcome: 0 (resolve() raises on any such state)")
for o in ORDER_T3:
    w(f"  {o}: {outcome_count[o]} states, of which {multi[o]} also matched a lower-precedence outcome")
if sum(outcome_count.values()) != total or total != 2 * 125 * 6 ** 6:
    raise SystemExit("count mismatch")

total = 0
outcome_count = Counter()
multi = Counter()
for k_ok in (True, False):
    for valid in product((True, False), repeat=3):
        for combo in product(("pass", "adverse", "neither"), repeat=len(ORDERED)):
            r = dict(zip(ORDERED, combo))
            sig = tuple((r[(i, j)] == "pass" and r[(j, i)] == "pass",
                         r[(i, j)] == "adverse" and r[(j, i)] == "adverse") for i, j in PAIRS)
            o, nh = resolve(t1_predicates(k_ok, valid, sig), ORDER_T1)
            total += 1
            outcome_count[o] += 1
            if nh > 1:
                multi[o] += 1
w("== T1 (scale flow) outcome procedure ==")
w(f"states enumerated: {total} = 2 x 2^3 (instrument valid) x 3^6 (ordered-pair results)")
for o in ORDER_T1:
    w(f"  {o}: {outcome_count[o]} states, of which {multi[o]} also matched a lower-precedence outcome")

# Wind/WAVES channel assignment under every-k thinning.
w("== Wind/WAVES channels under the every-k rule (J complete blocks, k = max(1, J // 32), first 32 selected) ==")
old_bad_single, old_bad_two, new_bad = [], [], []
for J in range(32, 720):
    k = max(1, J // 32)
    sel = [b for b in range(J) if b % k == 0][:32]
    old = {b % 4 for b in sel}
    new = Counter(i % 4 for i in range(len(sel)))
    if len(old) == 1:
        old_bad_single.append(J)
    elif len(old) < 4:
        old_bad_two.append(J)
    if len(new) != 4 or max(new.values()) - min(new.values()) > 1:
        new_bad.append(J)
w(f"J from 32 to 719 ({720 - 32} values). Old rule, block b from channel b mod 4: one channel only for "
  f"{len(old_bad_single)} values, two or three channels for {len(old_bad_two)} values.")
w(f"New rule, the i-th selected block from channel i mod 4: values of J where some channel is missing or counts "
  f"differ by more than one: {len(new_bad)}.")
sys.stdout.write("\n".join(out) + "\n")
