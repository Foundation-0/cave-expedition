"""Exact binomial checks for PREREG-01a, PREREG-01b and related cutoffs. Fractions only."""
from fractions import Fraction as F
from math import comb, factorial
import sys

P0 = F(1, 20)


_CACHE = {}


def _upper_tails(n, p):
    """List T with T[k] = P(Bin(n, p) >= k) for k = 0..n+1, exact, cached."""
    key = (n, p)
    if key not in _CACHE:
        pmf = [F(comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
        tails = [F(0)] * (n + 2)
        acc = F(0)
        for i in range(n, -1, -1):
            acc += pmf[i]
            tails[i] = acc
        if acc != 1:
            raise ValueError("pmf does not sum to 1")
        _CACHE[key] = tails
    return _CACHE[key]


def tail(n, k, p=P0):
    """P(Bin(n, p) >= k), exact."""
    if k <= 0:
        return F(1)
    if k > n:
        return F(0)
    return _upper_tails(n, p)[k]


def first_k_at_or_below(n, level, p=P0):
    tails = _upper_tails(n, p)
    for k in range(n + 2):
        if tails[k] <= level:
            return k
    raise ValueError("no k")


def f(x, nd=6):
    return f"{float(x):.{nd}f}"


out = []
w = out.append
w("== PREREG-01a: control rule at PREREG.md line 150 ==")
for S in (12, 16, 24, 32):
    k1 = first_k_at_or_below(S, F(1, 100))
    # original rule: absent iff K < k1 AND K/S <= 1/10 ; fail iff K >= k1 OR K > S/10
    kmax_ratio = max(k for k in range(S + 1) if F(k, S) <= F(1, 10))
    fail_orig = tail(S, min(k1, kmax_ratio + 1))
    fail_fix = tail(S, k1)
    bind = "ratio clause binds" if kmax_ratio + 1 < k1 else "binomial clause binds"
    w(f"S={S}: 1% excess point K>={k1} (tail {f(tail(S, k1))}); ratio clause allows K<={kmax_ratio}; {bind}")
    for name, pf in (("original", fail_orig), ("binomial only", fail_fix)):
        inst = 1 - (1 - pf) ** 3
        w(f"   {name}: one control fails {f(pf)}; one instrument (3 controls, independent) {f(inst)}; "
          f">=1 of 3 instruments {f(1 - (1 - inst) ** 3)}; >=1 of 4 {f(1 - (1 - inst) ** 4)}")

w("== PREREG-01b: K2 cutoff at PREREG.md line 211 ==")
n = 200
kpass_orig = max(k for k in range(n + 1) if F(k, n) <= F(86, 1000))
w(f"rate <= 0.086 of 200 passes K <= {kpass_orig}; tail P(K >= {kpass_orig + 1}) = {f(tail(n, kpass_orig + 1))}")
k99 = first_k_at_or_below(n, F(1, 100))
w(f"exact 1% point for n=200: fail at K >= {k99} (tail {f(tail(n, k99))}); P(K >= {k99 - 1}) = {f(tail(n, k99 - 1))}")
for k in (k99, 21):
    t = tail(n, k)
    w(f"   fail at K >= {k}: per class {f(t)}; 21 classes at least one false flag {f(1 - (1 - t) ** 21)}")
n2 = 1000
k99b = first_k_at_or_below(n2, F(1, 100))
w(f"exact 1% point for n=1000: fail at K >= {k99b} (tail {f(tail(n2, k99b))})")
w("power of K2 to flag a miscalibrated class (true per-segment rate r):")
for r in (F(6, 100), F(7, 100), F(8, 100), F(10, 100)):
    w(f"   r={f(r, 2)}: n=200 fail at K>={k99} flags with prob {f(tail(200, k99, r), 4)}; "
      f"n=200 fail at K>=21 flags with prob {f(tail(200, 21, r), 4)}; "
      f"n=1000 fail at K>={k99b} flags with prob {f(tail(1000, k99b, r), 4)}")
w("false presence from an undetected miscalibration (needs K >= 7 of 32, or K >= 5 of 12):")
for r in (F(6, 100), F(7, 100), F(8, 100), F(10, 100)):
    w(f"   r={f(r, 2)}: S=32 {f(tail(32, 7, r), 4)}; S=12 {f(tail(12, 5, r), 4)}")

w("== Holm family ==")
for m in (28, 40):
    thr = F(5, 100) / m
    w(f"{m} tests: smallest Holm threshold {thr} = {f(thr)}")
    for S in (12, 16, 24, 32):
        kmin = first_k_at_or_below(S, thr)
        w(f"   presence S={S}: needs K >= {kmin} (tail {f(tail(S, kmin))}); p_min 0.05^S = {float(P0 ** S):.3e}")

w("== smallest p of a template test with m jointly populated features ==")
for m in range(3, 11):
    perm = factorial(m)
    signperm = factorial(m) * 2 ** m
    pp = max(F(1, perm), F(1, 10000))
    ps = max(F(1, signperm), F(1, 10000))
    w(f"m={m}: permutations {perm} -> p_min {f(pp)}; permutations with sign flips {signperm} -> p_min {f(ps)}")

sys.stdout.write("\n".join(out) + "\n")

# ---- Section added for the reconciliation with Aletheia v2.0.0 (Bonferroni across net runs) ----
out2 = []
v = out2.append
v("== Bonferroni split across net runs inside each test (Aletheia v2.0.0, OTF-TIGHT-01) ==")
for fam, m in (("confirmatory", 40), ("listed transformations", 99)):
    thr = F(5, 100) / m
    v(f"{fam} family: {m} tests, smallest Holm threshold {thr} = {f(thr, 7)}")
    for runs, label in ((13, "presence, 13 runs"), (12, "presence TESS, 12 runs"), (5, "transfer, 5 runs")):
        per = thr / runs
        v(f"   {label}: smallest per-run level {per} = {float(per):.3e}")
        if label.startswith("presence"):
            for S in (12, 16, 24, 32):
                kmin = first_k_at_or_below(S, per)
                v(f"      S={S}: needs K >= {kmin} (tail {float(tail(S, kmin)):.3e})")
        else:
            perm = next(mm for mm in range(1, 20) if F(1, factorial(mm)) <= per)
            sign = next(mm for mm in range(1, 20) if F(1, factorial(mm) * 2 ** mm) <= per)
            v(f"      smallest m with 1/m! within it: {perm}; with signs, 1/(m! 2^m): {sign}")
            for R in (9999, 99999):
                v(f"      R = {R}: smallest p 1/{R + 1} {'within' if F(1, R + 1) <= per else 'NOT within'} the level")
v("== control ceiling c_max(S) for signal-over-control dominance (Rule 5), Bonferroni over 3 controls x 13 runs ==")
lev = F(1, 100) / (3 * 13)
for S in (12, 16, 24, 32):
    ks = first_k_at_or_below(S, lev)
    v(f"S={S}: level {float(lev):.3e}, smallest k with tail within it {ks} (tail {float(tail(S, ks)):.3e}); "
      f"c_max = {ks - 1}/{S} = {float(F(ks - 1, S)):.4f}; chance a calibrated control exceeds it in one run {float(tail(S, ks)):.2e}, "
      f"in any of 39 checks at most {float(1 - (1 - tail(S, ks)) ** 39):.4f}")
v("== null resolution for Law 2b guard G1 ==")
for n in (10, 20):
    v(f"null replicates {n}: n * 1/10 = {F(n, 10)} (needs >= 1); false passes allowed at rate <= 1/10: {n // 10}")
sys.stdout.write("\n".join(out2) + "\n")

# ---- Practical floor of sampled random-detector tests, and K2 false flags of a calibrated instrument ----
out3 = []
x = out3.append
x("== practical smallest p with R sampled detectors: (1 + R/D)/(R + 1), D distinct detectors ==")
for R in (9999, 99999):
    for label, D in (("signs+perm m=5", factorial(5) * 2 ** 5), ("signs+perm m=6", factorial(6) * 2 ** 6),
                     ("perm m=7", factorial(7)), ("perm m=8", factorial(8)), ("perm m=9", factorial(9))):
        val = (1 + F(R, D)) / (R + 1)
        x(f"R={R}, {label}, D={D}: {float(val):.3e}; within 0.00025: {val <= F(1, 4000)}; within 1/9900: {val <= F(1, 9900)}")
x("== K2: chance a calibrated instrument is marked not calibrated (each check flags at 68 of 1,000, tail t) ==")
t68 = tail(1000, 68)
for checks in (1, 3, 4, 9, 12):
    x(f"{checks} independent checks: {float(1 - (1 - t68) ** checks):.4f}")
sys.stdout.write("\n".join(out3) + "\n")

# ---- Final thresholds after the known-answer results (normal scores before surrogates; whitening and
# ---- amplitude maps out of the presence and arrow/profile runs) ----
out4 = []
y = out4.append
y("== final per-run levels ==")
for fam, m in (("confirmatory", 40), ("Law 2b family", 93)):
    thr = F(5, 100) / m
    y(f"{fam}: {m} tests, smallest Holm threshold {float(thr):.4e}")
    for label, runs, kind in (("presence, 10 runs", 10, "p"), ("presence TESS, 9 runs", 9, "p"),
                              ("arrow/profile transfer, 3 runs", 3, "t"), ("scale-flow transfer, 5 runs", 5, "t")):
        per = thr / runs
        if kind == "p":
            ks = ", ".join(f"S={S}: K>={first_k_at_or_below(S, per)}" for S in (12, 16, 24, 32))
            y(f"   {label}: per-run level {float(per):.3e}; {ks}")
        else:
            R = 99999
            ok6 = (1 + F(R, factorial(6) * 2 ** 6)) / (R + 1) <= per
            ok8 = (1 + F(R, factorial(8))) / (R + 1) <= per
            y(f"   {label}: per-run level {float(per):.3e}; R={R}: 6 levels with signs within it {ok6}; 8 features with permutations within it {ok8}")
y("== control ceiling c_max(S), 1 percent split over 3 controls x 10 runs ==")
lev = F(1, 100) / 30
for S in (12, 16, 24, 32):
    ks = first_k_at_or_below(S, lev)
    y(f"S={S}: c_max = {ks - 1}/{S}; any of 30 checks exceeded by a calibrated pipeline with probability at most {float(1 - (1 - tail(S, ks)) ** 30):.4f}")
y("== K2 after the change: one base class per instrument, checked at 3 or 4 window lengths ==")
for checks in (3, 4):
    y(f"{checks} checks at tail {float(t68):.4f}: {float(1 - (1 - t68) ** checks):.4f}")
y("== Law 2b instance known-answer tests: 200 seeds per class, exact 1 percent point ==")
y(f"fail at K >= {k99} of 200 (tail {float(tail(200, k99)):.4f})")
sys.stdout.write("\n".join(out4) + "\n")

# ---- Numbers for the second clean-room pass: 8 presence runs, 102-test Law 2b family, K2 gate rule ----
out5 = []
z = out5.append
z("== per-run levels with 8 presence runs (7 for TESS) ==")
for fam, m in (("confirmatory", 40), ("Law 2b family", 102)):
    thr = F(5, 100) / m
    z(f"{fam}: {m} tests, smallest Holm threshold {float(thr):.4e}")
    for label, runs, kind in (("presence, 8 runs", 8, "p"), ("presence TESS, 7 runs", 7, "p"),
                              ("arrow/profile transfer, 3 runs", 3, "t"), ("scale-flow transfer, 5 runs", 5, "t")):
        per = thr / runs
        if kind == "p":
            ks = ", ".join(f"S={S}: K>={first_k_at_or_below(S, per)}" for S in (12, 16, 24, 32))
            z(f"   {label}: per-run level {float(per):.3e}; {ks}")
        else:
            R = 99999
            v6 = (1 + F(R, factorial(6) * 2 ** 6)) / (R + 1)
            v5 = (1 + F(R, factorial(5) * 2 ** 5)) / (R + 1)
            v8 = (1 + F(R, factorial(8))) / (R + 1)
            v7 = (1 + F(R, factorial(7))) / (R + 1)
            z(f"   {label}: per-run level {float(per):.3e}; signs: 6 levels {v6 <= per}, 5 levels {v5 <= per}; "
              f"permutations: 8 features {v8 <= per}, 7 features {v7 <= per}")
z("== control ceiling over 3 controls x 8 runs = 24 checks ==")
lev = F(1, 100) / 24
for S in (12, 16, 24, 32):
    ks = first_k_at_or_below(S, lev)
    bound = 1 - (1 - tail(S, ks)) ** 24
    z(f"S={S}: c_max = {ks - 1}/{S}; probability any of 24 checks is breached by a calibrated pipeline {float(bound):.5f}")
z("== K2 gate: 7 null classes x 2 window lengths (4,096 and 2,048) = 14 checks; 2 reversible classes x 2 = 4 checks ==")
ka = first_k_at_or_below(1000, F(1, 100) / 14)
z(f"K2a flag: k_a = {ka} of 1,000 (rate {ka / 1000}); per-check tail at 0.05 {float(tail(1000, ka)):.3e}; "
  f"chance any of 14 calibrated checks flags {float(1 - (1 - tail(1000, ka)) ** 14):.4f}")
for r in (F(52, 1000), F(55, 1000), F(60, 1000), F(70, 1000), F(80, 1000), F(100, 1000)):
    pc = tail(1000, ka, r)
    z(f"   true null rate {float(r):.3f}: per check {float(pc):.4f}; any of 14 checks {float(1 - (1 - pc) ** 14):.4f}")
p10 = F(1, 10)
kb = first_k_at_or_below(1000, F(1, 100) / 4, p10)
z(f"K2b flag (rate clearly above 0.10): k_b = {kb} of 1,000, the smallest k with P(Bin(1000, 0.10) >= k) <= 0.01/4 (tail {float(tail(1000, kb, p10)):.3e})")
for r in (F(7, 100), F(9, 100), F(10, 100), F(12, 100), F(15, 100)):
    z(f"   true rate {float(r):.2f}: flagged at one length with probability {float(tail(1000, kb, r)):.4f}")
z("why a reversible series at rate <= 0.10 cannot alone produce presence in one run:")
for S in (12, 16, 24, 32):
    kneed = first_k_at_or_below(S, F(5, 100) / 40 / 8)
    kmargin = -(-(S * 3) // 10)   # share at least 0.30 = 0.05 + 1/4, if the control share were exactly 0.05
    k = max(kneed, kmargin)
    z(f"   S={S}: needs K >= {k}; P(Bin(S, 0.10) >= {k}) = {float(tail(S, k, p10)):.2e}")
z("== old instrument-level false-flag figures (superseded), for the record ==")
for checks in (3, 4, 9):
    z(f"   {checks} checks: {float(1 - (1 - t68) ** checks):.4f}")
z(f"   three instruments, 3 checks each: {float(1 - (1 - t68) ** 9):.4f}")
for r in (F(52, 1000), F(55, 1000), F(60, 1000)):
    pc = tail(1000, 68, r)
    z(f"   true rate {float(r):.3f}: per check {float(pc):.4f}; over 3 checks {float(1 - (1 - pc) ** 3):.4f}")
z(f"K3 must-fail and Law 2b instance tests: 200 seeds; K3 pass needs at least 100 of 200 per net")
sys.stdout.write("\n".join(out5) + "\n")

# ---- One-run chance that a reversible series at segment rate r passes a presence run (third pass) ----
out6 = []
q = out6.append
q("== one presence run passed by a series whose segment rate is r (binomial level 0.00125 / runs, margin 1/4 over the controls) ==")
for runs in (8, 5):
    per = F(5, 100) / 40 / runs
    for r in (F(1, 10), F(129, 1000)):
        worst0, worst5 = (F(0), None), (F(0), None)
        cells = []
        for S in range(12, 33, 4):
            kb = first_k_at_or_below(S, per)
            k0 = max(kb, -(-S // 4))                 # control shares 0: K/S >= 1/4
            k5 = max(kb, -(-(S * 3) // 10))          # control shares 0.05: K/S >= 0.30
            p0, p5 = tail(S, k0, r), tail(S, k5, r)
            cells.append(f"S={S}: {float(p0):.4f} / {float(p5):.4f}")
            if p0 > worst0[0]:
                worst0 = (p0, S)
            if worst5[1] is None or p5 > worst5[0]:
                worst5 = (p5, S)
        q(f"{runs} runs, r = {float(r):.3f} (controls at 0 / controls at 0.05): " + "; ".join(cells))
        q(f"   largest with controls at 0: {float(worst0[0]):.4f} at S = {worst0[1]}; with controls at 0.05: {float(worst5[0]):.4f} at S = {worst5[1]}")
sys.stdout.write("\n".join(out6) + "\n")
