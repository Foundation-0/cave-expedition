"""Exact checks of the amendment's binomial claims (control rule A1, K2 cutoffs A2).
Standard library only. Integers and fractions.Fraction only. No bare assert.
Output is a table of CLAIM lines (REPRODUCED / DIFFERS) plus CONTROL lines.
Exit status 1 if any must-fail control is not flagged, else 0.
"""
import sys
from fractions import Fraction
from math import comb, factorial

FAILS = []


def tail(n, p, k):
    """P(Binomial(n, p) >= k), p a Fraction, exact."""
    if k <= 0:
        return Fraction(1)
    q = 1 - p
    return sum(Fraction(comb(n, j)) * p**j * q**(n - j) for j in range(k, n + 1))


def smallest_k(n, p, level):
    """Smallest k with tail(n,p,k) <= level."""
    for k in range(0, n + 2):
        if tail(n, p, k) <= level:
            return k
    raise ValueError("no k")


def dec(x, d=6):
    return f"{float(x):.{d}f}"


def matches(claimed, exact, digits):
    """True when exact rounds (half-up-ish via Fraction) to the claimed decimal string."""
    scale = 10**digits
    r = Fraction(round(exact * scale), scale)
    return r == Fraction(claimed)


def claim(tag, desc, claimed, exact, digits):
    ok = matches(claimed, exact, digits)
    print(f"CLAIM {tag} | {desc} | amendment={claimed} | mine={dec(exact, max(digits, 6))} | "
          f"{'REPRODUCED' if ok else 'DIFFERS'}")
    return ok


def control(tag, flagged):
    """A must-fail control: flagged must be True (the checker caught the wrong input)."""
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


p05 = Fraction(5, 100)

# ---------------- PREREG-01a ----------------
print("# PREREG-01a: control rule")
kpt = {}
for S in (12, 24, 32):
    kpt[S] = smallest_k(S, p05, Fraction(1, 100))
    print(f"INFO S={S}: smallest k with tail<=0.01 is {kpt[S]} (tail {dec(tail(S, p05, kpt[S]), 6)}; "
          f"tail at k-1 {dec(tail(S, p05, kpt[S]-1), 6)})")
claim("01a-k12", "1% point at S=12", "4", Fraction(kpt[12]), 0)
claim("01a-k24", "1% point at S=24", "5", Fraction(kpt[24]), 0)
claim("01a-k32", "1% point at S=32", "6", Fraction(kpt[32]), 0)


def pass_old(S, K):
    return K < kpt[S] and 10 * K <= S


def pass_new(S, K):
    return K < kpt[S]


def inv_prob(S, passfn):
    q = Fraction(0)
    for K in range(S + 1):
        if not passfn(S, K):
            q += Fraction(comb(S, K)) * p05**K * (1 - p05)**(S - K)
    return q


for S, c_ctrl, c_inst3, c_any3, c_new_inst in (
        (12, "0.118360", "0.314711", "0.678173", "0.006694"),
        (32, "0.073805", "0.205477", "0.498444", "0.013736")):
    pc = inv_prob(S, pass_old)
    pi = 1 - (1 - pc)**3
    pa = 1 - (1 - pi)**3
    pn_c = inv_prob(S, pass_new)
    pn_i = 1 - (1 - pn_c)**3
    claim(f"01a-S{S}-ctrl", f"old rule, one control invalid, S={S}", c_ctrl, pc, 6)
    claim(f"01a-S{S}-inst", f"old rule, instrument (3 controls) invalid, S={S}", c_inst3, pi, 6)
    claim(f"01a-S{S}-any", f"old rule, >=1 of 3 instruments invalid, S={S}", c_any3, pa, 6)
    claim(f"01a-S{S}-new", f"binomial rule only, instrument invalid, S={S}", c_new_inst, pn_i, 6)
    print(f"INFO S={S} binomial-only single control invalid = {dec(pn_c, 6)}")
# which clause binds in the old rule
for S in (12, 24, 32):
    ratio_max = max(K for K in range(S + 1) if 10 * K <= S)
    binom_max = kpt[S] - 1
    print(f"INFO S={S}: old rule passes K<={min(ratio_max, binom_max)}; ratio clause allows K<={ratio_max}, "
          f"binomial clause allows K<={binom_max}; ratio binds = {ratio_max < binom_max}")
# must-fail: an off-by-0.01 claim and a wrong rule must be flagged
control("01a wrong number 0.324711", not matches("0.324711", 1 - (1 - inv_prob(12, pass_old))**3, 6))
control("01a rule with K<=3 at S=12 (wrong point) differs",
        inv_prob(12, lambda S, K: K < 3) != inv_prob(12, pass_new))

# ---------------- PREREG-01b ----------------
print("# PREREG-01b: K2 cutoff")
t17 = tail(200, p05, 17)
t18 = tail(200, p05, 18)
t19 = tail(200, p05, 19)
t20 = tail(200, p05, 20)
t21 = tail(200, p05, 21)
claim("01b-t18", "P(Bin(200,.05)>=18)", "0.012089", t18, 6)
claim("01b-t19", "P(Bin(200,.05)>=19)", "0.005824", t19, 6)
print(f"INFO tails n=200: >=17 {dec(t17, 6)}, >=18 {dec(t18, 6)}, >=19 {dec(t19, 6)}, >=20 {dec(t20, 6)}, >=21 {dec(t21, 6)}")
k200 = smallest_k(200, p05, Fraction(1, 100))
claim("01b-k200", "exact 1% point n=200", "19", Fraction(k200), 0)
# old text: rate at most 0.086 of 200 passes K up to floor(0.086*200)
old_pass_max = (86 * 200) // 1000
claim("01b-oldpass", "0.086 of 200 passes K up to", "17", Fraction(old_pass_max), 0)
# reviewers' looser cutoff: fail at 21 or more of 200; 21 classes
fam21 = 1 - (1 - t21)**21
print(f"INFO reviewers' cutoff (fail at >=21): per-class false-fail {dec(t21, 6)}, over 21 classes {dec(fam21, 6)}")
claim("01b-fam21", "reviewers' 21-class false-fail near 2.4 percent", "0.024", fam21, 3)
p08 = Fraction(8, 100)
claim("01b-pow200-19", "P(Bin(200,.08)>=19): 200 draws failing at 19 or more (first review cutoff)", "0.2506", tail(200, p08, 19), 4)
claim("01b-pow200-21", "P(Bin(200,.08)>=21): 200 draws failing at 21 or more (second review cutoff)", "0.1225", tail(200, p08, 21), 4)
print(f"INFO P(Bin(200,.08)>=18) = {dec(tail(200, p08, 18), 6)}, >=19 = {dec(tail(200, p08, 19), 6)}")
k1000 = smallest_k(1000, p05, Fraction(1, 100))
claim("01b-k1000", "1% point n=1000", "68", Fraction(k1000), 0)
t68 = tail(1000, p05, 68)
t67 = tail(1000, p05, 67)
claim("01b-t68", "P(Bin(1000,.05)>=68)", "0.0074", t68, 4)
print(f"INFO n=1000 tails: >=67 {dec(t67, 6)} (above 0.01 = {t67 > Fraction(1, 100)}), >=68 {dec(t68, 6)}")
claim("01b-pow1000-08", "P(Bin(1000,.08)>=68)", "0.9302", tail(1000, p08, 68), 4)
claim("01b-pow1000-07", "P(Bin(1000,.07)>=68)", "0.6155", tail(1000, Fraction(7, 100), 68), 4)
claim("01b-falsepres", "P(Bin(32,.08)>=7) false presence at rate .08, S=32", "0.0119", tail(32, p08, 7), 4)
print(f"INFO at true rate .08, S=12 P(K>=5)={dec(tail(12, p08, 5), 6)}, S=24 P(K>=6)={dec(tail(24, p08, 6), 6)}")
# false-flag chance on a calibrated class: old (1 window length) vs new (3 or 4 window lengths)
print(f"INFO calibrated-class false flag: old one length {dec(t18, 6)}; new per length {dec(t68, 6)}; "
      f"new over 3 lengths {dec(1 - (1 - t68)**3, 6)}; over 4 lengths {dec(1 - (1 - t68)**4, 6)}")
control("01b wrong 18->19 tail claimed 0.012089", not matches("0.012089", t19, 6))
control("01b wrong power claim 0.9902", not matches("0.9902", tail(1000, p08, 68), 4))


if FAILS:
    print("FAILED CONTROLS:", FAILS)
    sys.exit(1)
print("DONE amendment_numbers")
