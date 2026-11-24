"""Exact checks of the plan numbers (counts, per-run levels, floors, K2 gate, false presence, K3 and K5 numbers, compute). Standard library only. int / Fraction / math.comb. No bare assert.
argv[1] = revised PREREG.md. Prints CLAIM / INFO / CONTROL lines; exit 1 if a must-fail control is not flagged."""
import re
import sys
from fractions import Fraction
from math import comb, factorial, ceil
from itertools import permutations

PLAN = sys.argv[1]
FAILS = []


def slurp(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def claim(tag, desc, text, mine, ok):
    print(f"CLAIM {tag} | {desc} | text={text} | mine={mine} | {'REPRODUCED' if ok else 'DIFFERS'}")


def tail(n, p, k):
    if k <= 0:
        return Fraction(1)
    return sum(Fraction(comb(n, j)) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))


def kmin(n, p, level):
    for k in range(n + 2):
        if tail(n, p, k) <= level:
            return k
    raise ValueError("none")


def f4(x, d=4):
    return f"{float(x):.{d}f}"


P05 = Fraction(1, 20)
text = slurp(PLAN).split("\n")

# ---------------- counts ----------------
print("# counts")
s9 = [i for i, l in enumerate(text) if l.startswith("## 9.")][0]
s10 = [i for i, l in enumerate(text) if l.startswith("## 10.")][0]
rows = [l for l in text[s9:s10] if l.startswith("| T") and not l.startswith("| Test")]
counts9 = [int(l.split("|")[2].strip()) for l in rows]
claim("count40", "confirmatory family, section 9 table", 40, sum(counts9), sum(counts9) == 40)
s12a = [i for i, l in enumerate(text) if l.startswith("## 12a.")][0]
s12b = [i for i, l in enumerate(text) if l.startswith("## 12b.")][0]
trs = [l for l in text[s12a:s12b] if re.match(r"\| T\d_", l)]
cols = {"a": 0, "b": 0, "c": 0}
for l in trs:
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    for name, c in zip("abc", cells[1:4]):
        if c.lower().startswith("none"):
            continue
        cols[name] += 1
        if "O4" in c:
            cols[name] += 1
print(f"INFO instances per column from the 12a table: {cols}")
n_a, n_b, n_c = cols["a"] * 3, cols["b"] * 6, cols["c"] * 6
claim("count102", "24 + 42 + 36 from the 12a table", 102, n_a + n_b + n_c, (n_a, n_b, n_c) == (24, 42, 36))
thr40 = Fraction(5, 4000)
thr102 = Fraction(5, 100 * 102)
claim("thr102", "0.05/102", "0.000490", f4(thr102, 6), f4(thr102, 6) == "0.000490")
control("wrong family size 93 flagged", n_a + n_b + n_c != 93)

# ---------------- per-run levels ----------------
print("# per-run levels")
for lab, thr, runs in (("confirmatory presence 8 runs", thr40, 8), ("confirmatory TESS 7 runs", thr40, 7),
                       ("confirmatory Wind at N=2048, 5 runs (native, 2 quantizations, placement, instrument)", thr40, 5),
                       ("12a presence 8 runs", thr102, 8)):
    lvl = thr / runs
    row = [f"S={S}: K>={kmin(S, P05, lvl)}" for S in (12, 16, 24, 32)]
    print(f"INFO {lab}: per-run level {float(lvl):.3e}; " + "; ".join(row))
for S, want in ((12, 6), (24, 7), (32, 8)):
    got = kmin(S, P05, thr40 / 8)
    claim(f"K8-{S}", f"K needed at 0.00125/8, S={S}", want, got, got == want)
for S, want in ((12, 6), (16, 7), (24, 8), (32, 9)):
    got = kmin(S, P05, thr102 / 8)
    claim(f"K102-{S}", f"K needed at 0.05/102/8, S={S}", want, got, got == want)
for lab, thr, runs, txt in (("arrow 12a", thr102, 3, "1.6e-4"), ("scale flow 12a", thr102, 5, "9.8e-5"), ("presence 12a", thr102, 8, "6.1e-5")):
    v = float(thr / runs)
    claim(f"lvl-{lab}", f"per-run level {lab}", txt, f"{v:.2e}", abs(v - float(txt)) / float(txt) < 0.03)

# ---------------- floors ----------------
print("# floors")
R = 99999


def pmin(D):
    return (1 + Fraction(R, D)) / (R + 1)


for lab, D, lvl_conf, lvl_12a in (("arrow, signs", None, thr40 / 3, thr102 / 3), ("profile, permutations", None, thr40 / 3, None),
                                  ("scale flow, permutations", None, thr40 / 5, thr102 / 5)):
    pass
for m in (5, 6):
    v = pmin(factorial(m) * 2**m)
    print(f"INFO arrow {m} levels with signs: smallest p {float(v):.2e}; confirmatory per-run 4.17e-4 reaches: {v <= thr40/3}; 12a per-run {float(thr102/3):.2e} reaches: {v <= thr102/3}")
for m in (7, 8):
    v = pmin(factorial(m))
    print(f"INFO {m} features permutations: smallest p {float(v):.2e}; scale flow confirmatory reaches: {v <= thr40/5}; 12a scale flow reaches: {v <= thr102/5}")
claim("floor-6lev", "5 levels too large for 12a, 6 reach", "2.7e-4 too large; 3.2e-5", f"{float(pmin(3840)):.1e}; {float(pmin(46080)):.1e}", pmin(3840) > thr102 / 3 >= pmin(46080))
claim("floor-8feat", "7 features too large for 12a scale flow, 8 reach", "2.1e-4 too large; 3.5e-5", f"{float(pmin(5040)):.1e}; {float(pmin(40320)):.1e}", pmin(5040) > thr102 / 5 >= pmin(40320))
control("floor 7 claimed reaching 12a scale flow flagged", not (pmin(5040) <= thr102 / 5))
# every test reaches
for lab, p_, lvl in (("arrow", pmin(46080), thr40 / 3), ("profile", pmin(40320), thr40 / 3), ("scale flow", pmin(40320), thr40 / 5),
                     ("12a arrow", pmin(46080), thr102 / 3), ("12a scale flow", pmin(40320), thr102 / 5)):
    print(f"INFO {lab}: smallest p {float(p_):.2e} <= per-run level {float(lvl):.2e}: {p_ <= lvl}; adjusted (x runs) fits Holm: {p_ * (3 if 'scale' not in lab else 5) <= (thr40 if '12a' not in lab else thr102)}")

# ---------------- ceiling ----------------
print("# control ceiling, 24 checks")
for S in (12, 16, 24, 32):
    k = kmin(S, P05, Fraction(1, 2400))
    print(f"INFO S={S}: c_max={(k-1)}/{S}; breach bound 24 x tail = {float(24 * tail(S, P05, k)):.5f}")
w = max(24 * tail(S, P05, kmin(S, P05, Fraction(1, 2400))) for S in (12, 16, 24, 32))
claim("ceil24", "bound over 24 checks", "0.0045 (0.00441 at S=12)", f"{float(w):.5f}", abs(float(w) - 0.00441) < 5e-6 and float(w) <= 0.0045)

# ---------------- K2 gate ----------------
print("# K2 gate")
t05 = lambda k: tail(1000, P05, k)
k74 = kmin(1000, P05, Fraction(1, 1400))
claim("k2a-k", "smallest k with tail <= 0.01/14", 74, k74, k74 == 74)
any14 = 1 - (1 - t05(74))**14
claim("k2a-any", "calibrated set flagged anywhere (14 checks), at most", "0.0090", f"{float(any14):.5f} (union bound {float(14*t05(74)):.5f})", f"{float(14*t05(74)):.4f}" == "0.0090" or f"{float(any14):.4f}" == "0.0090")
old68 = 1 - (1 - t05(68))**14
claim("k2a-old68", "same 14 checks with the old point 68", "0.099", f"{float(old68):.4f}", f"{float(old68):.3f}" == "0.099" or f"{float(old68):.3f}" == "0.098")
for r, txt in ((50, "0.009"), (52, "0.025"), (55, "0.091"), (60, "0.43"), (70, ">0.99")):
    v = 1 - (1 - tail(1000, Fraction(r, 1000), 74))**14
    ok = (f"{float(v):.3f}" == txt) if txt != ">0.99" else float(v) > 0.99
    if txt == "0.43":
        ok = f"{float(v):.2f}" == "0.43"
    claim(f"k2a-fs-{r}", f"false-stop chance, all 7 classes at true rate {r/10:.1f}%", txt, f"{float(v):.4f}", ok)
c07_74 = tail(1000, Fraction(7, 100), 74)
c07_68 = tail(1000, Fraction(7, 100), 68)
claim("k2a-catch", "class at true rate 0.07 caught per check: new point 74 vs old 68", "0.33 vs 0.62", f"{float(c07_74):.3f} vs {float(c07_68):.3f}", f"{float(c07_74):.2f}" == "0.33" and f"{float(c07_68):.2f}" == "0.62")
k129 = kmin(1000, Fraction(1, 10), Fraction(1, 400))
claim("k2b-k", "smallest k with P(Bin(1000,0.10) >= k) <= 0.01/4", 129, k129, k129 == 129)
print(f"INFO K2b: tail at 129 under a true rate of 0.10 = {float(tail(1000, Fraction(1,10), 129)):.5f}; flag probability at true 0.11 = {float(tail(1000, Fraction(11,100), 129)):.4f}, 0.12 = {float(tail(1000, Fraction(12,100), 129)):.4f}, 0.129 = {float(tail(1000, Fraction(129,1000), 129)):.4f}")
print("INFO K2b: the plan's measured rates for the two classes in the clean-room check were 0.05 to 0.09; flag probability at 0.09 = "
      f"{float(tail(1000, Fraction(9,100), 129)):.2e}")

# false presence of one presence run when every segment rejects at rate r (exact; maximum over S = 12..32 and over the run counts the plan allows)
print("# false presence of one presence run when every segment rejects at rate r (A14 item 1; plan section 10, K2b)")


def kneed(S, runs, ctrl):
    kb = kmin(S, P05, thr40 / runs)
    km = ceil(S * (Fraction(1, 4) + ctrl))   # margin 1/4 over a control share ctrl
    return max(kb, km)


def best_over(r, ctrl, run_counts):
    best = (Fraction(0), None)
    for runs in run_counts:
        for S in range(12, 33):
            K = kneed(S, runs, ctrl)
            v = tail(S, r, K)
            if v > best[0]:
                best = (v, (S, runs, K))
    return best


rows_fp = []
for r in (Fraction(1, 10), Fraction(129, 1000)):
    for ctrl, lab in ((Fraction(0), "control shares 0"), (Fraction(5, 100), "control shares near 0.05 (margin share 0.30)")):
        b8 = best_over(r, ctrl, (8, 7))
        b5 = best_over(r, ctrl, (5,))
        print(f"INFO rate {float(r):.3f}, {lab}: largest one-run chance over S = 12..32: 8 or 7 runs {float(b8[0]):.5f} at (S, runs, K) = {b8[1]}; Wind/WAVES at N = 2,048 (5 runs) {float(b5[0]):.5f} at {b5[1]}")
        rows_fp.append((r, ctrl, b8, b5))
v32 = tail(32, Fraction(1, 10), kneed(32, 8, Fraction(0)))
claim("fp-0117", "rate 0.10, control shares 0: largest one-run chance (text: 0.0117 at S = 32)", "0.0117",
      f"{float(v32):.5f} at S=32 (8 runs); {float(rows_fp[0][3][0]):.5f} for Wind/WAVES with 5 runs at {rows_fp[0][3][1]}",
      f"{float(v32):.4f}" == "0.0117" and float(rows_fp[0][3][0]) <= 0.0117)
mx = max(rows_fp[1][2][0], rows_fp[1][3][0])
claim("fp-0043", "rate 0.10, control shares near 0.05: 'at most 0.0043'", "0.0043", f"largest {float(mx):.5f}", float(mx) <= 0.0043)
v32b = tail(32, Fraction(1, 10), kneed(32, 8, Fraction(5, 100)))
claim("fp-0008", "rate 0.10, control near 0.05, S = 32", "0.0008", f"{float(v32b):.5f}", f"{float(v32b):.4f}" == "0.0008")
claim("fp-046", "rate 0.129, control shares 0: largest one-run chance", "0.046", f"{float(rows_fp[2][2][0]):.5f}", f"{float(rows_fp[2][2][0]):.3f}" == "0.046")
mx2 = max(rows_fp[3][2][0], rows_fp[3][3][0])
claim("fp-013", "rate 0.129, control shares near 0.05: 'at most 0.013'", "0.013", f"largest {float(mx2):.5f}", float(mx2) <= 0.013)
s12 = (tail(12, Fraction(1, 10), kneed(12, 5, Fraction(5, 100))), tail(12, Fraction(129, 1000), kneed(12, 5, Fraction(5, 100))))
print(f"INFO the published 0.0043 and 0.013 equal the S = 12, 5-run values ({float(s12[0]):.5f}, {float(s12[1]):.5f}), not the maxima over S")
print(f"INFO across runs: with 8 independent runs at S = 32 the chance would be {float(v32**8):.1e} (rate 0.10); the runs are not independent")
control("wrong bound 0.0033 flagged", f"{float(v32):.4f}" != "0.0033")
control("wrong bound 0.0003 for S=32 flagged", f"{float(v32b):.4f}" != "0.0003")
control("wrong K2b point 120 flagged", k129 != 120)

# ---------------- Law 2b K2/G1 numbers ----------------
print("# Law 2b instance tests (P:407-409)")
k24 = kmin(200, P05, Fraction(1, 5600))
claim("g1-k24", "null class flagged at k with tail <= 0.01/56", 24, k24, k24 == 24)
claim("g1-t24", "P(Bin(200,.05) >= 24)", "7.2e-5", f"{float(tail(200, P05, 24)):.2e}", abs(float(tail(200, P05, 24)) - 7.2e-5) / 7.2e-5 < 0.03)
claim("g1-any", "calibrated set flagged anywhere, at most", "0.004", f"{float(56*tail(200, P05, 24)):.4f}", f"{float(56*tail(200, P05, 24)):.3f}" == "0.004")
k36 = kmin(200, Fraction(1, 10), Fraction(1, 1600))
claim("g1-k36", "reversible class point, tail <= 0.01/16", 36, k36, k36 == 36)
claim("g1-t36", "P(Bin(200,.10) >= 36)", "3.9e-4", f"{float(tail(200, Fraction(1,10), 36)):.2e}", abs(float(tail(200, Fraction(1,10), 36)) - 3.9e-4) / 3.9e-4 < 0.03)
claim("g1-catch", "a null rate of 0.10 is caught per check at 24 of 200", "0.20", f"{float(tail(200, Fraction(1,10), 24)):.3f}", f"{float(tail(200, Fraction(1,10), 24)):.2f}" == "0.20")

# ---------------- K3 control and criteria ----------------
print("# K3")
print("INFO circular-shift control passes if at most 20 of 200 segments are detected; a correct pipeline fails it if >= 21 are:")
for r in (50, 60, 75, 100):
    print(f"   true detection rate {r/1000:.3f}: P(>= 21 of 200) = {float(tail(200, Fraction(r, 1000), 21)):.4f}")
print(f"INFO builder's circular-shift detections were 12, 27 and 11 of 200 (0.060, 0.135, 0.055); at 0.135 the control would fail with probability {float(tail(200, Fraction(135,1000), 21)):.3f}")
print(f"INFO with 32 segments and true detection 0.5: P(K >= 10) = {float(tail(32, Fraction(1,2), 10)):.4f} (text: about 0.99)")
claim("k3-099", "32 segments at rate 0.5 give K >= 10 with probability about 0.99", "about 0.99", f"{float(tail(32, Fraction(1,2), 10)):.4f}", abs(float(tail(32, Fraction(1,2), 10)) - 0.99) < 0.002)
for r in (545, 520, 500):
    print(f"INFO K3 50-percent line: true rate {r/1000:.3f} fails with probability {float(1 - tail(200, Fraction(r,1000), 100)):.4f}")
for r in (700, 600):
    print(f"INFO K3 at 2,048 samples (published rule: 50 percent): true rate {r/1000:.3f} fails with probability {float(1 - tail(200, Fraction(r,1000), 100)):.5f}; an 80 percent rule would pass with probability {float(tail(200, Fraction(r,1000), 160)):.4f}")

# ---------------- K5 units ----------------
print("# K5")
for u in (32, 32, 31, 15):
    k = kmin(u, P05, Fraction(1, 100))
    print(f"INFO units={u}: 1% point k={k}, false departure {float(tail(u, P05, k)):.4f}")
fd = [tail(u, P05, kmin(u, P05, Fraction(1, 100))) for u in (32, 32, 31, 15)]
prod = Fraction(1)
for f in fd:
    prod *= (1 - f)
per_seed = 1 - prod
print(f"INFO null case, four levels: per-seed false departure {float(per_seed):.4f}; case fails if >= 2 of 10 seeds: {float(tail(10, per_seed, 2)):.4f}")
# unit counts from the segment rule
for lvl, n in ((0, 2**19), (1, 2**18), (2, 2**17), (3, 2**16), (4, 2**15)):
    J = n // 4224
    k = max(1, J // 32)
    sel = len([b for b in range(J) if b % k == 0][:32])
    print(f"INFO K5 level {lvl}: {n} samples, J={J}, k={k}, units={sel}")
claim("k5-units", "units at levels 0 to 3 are 32, 32, 31, 15 (level 4: 7)", "32, 32, 31, 15", ", ".join(str(len([b for b in range(n // 4224) if b % max(1, (n // 4224) // 32) == 0][:32])) for n in (2**19, 2**18, 2**17, 2**16)),
      [len([b for b in range(n // 4224) if b % max(1, (n // 4224) // 32) == 0][:32]) for n in (2**19, 2**18, 2**17, 2**16)] == [32, 32, 31, 15])

# ---------------- Wind cadence ----------------
print("# Wind/WAVES")
span = 8 * 86400
lim = Fraction(span, 12 * (2048 + 128))
claim("wind-26.5", "cadence limit for 12 blocks of 2,048 + 128 in 8 days", "26.5 s", f"{float(lim):.3f}", f"{float(lim):.1f}" == "26.5")

# ---------------- compute ----------------
print("# compute")
c = Fraction(23, 10)
u = {4096: Fraction(1), 2048: Fraction(1, 2)}
k2 = 9 * 1000 * c * (u[4096] + u[2048])
print(f"INFO amended K2 at two lengths: {float(k2/3600):.2f} h (before: 10.06)")
units = 4 * u[4096] + 3 * u[2048]
print(f"INFO K3 per seed-case with the six nets: {float(units):.2f} length-units; 3 cases {float(600*units*c/3600):.2f} h; with the noisy sawtooth {float(800*units*c/3600):.2f} h")
print(f"INFO published compute: known-answer 26 per mode, fit 1, verdict 8 (23 for three): 26 x 3 + 3 + 23 = {26*3+3+23}, or {26*3+3+24} with 8 h per mode; text says about 103. The K4 and K5 stream doubling cannot be recomputed from the text (no component list)")
print(f"INFO the Law 2b search adds 68 x 3 = {68*3} h (text 203)")

if FAILS:
    print("FAILED CONTROLS:", FAILS)
    sys.exit(1)
print("DONE plan_numbers")
