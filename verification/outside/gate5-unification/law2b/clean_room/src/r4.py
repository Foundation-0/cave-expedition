"""Row 4: Cole-Hopf claims 13-17 (clean-room, exact)."""
import os, sys, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ex import *
from common import *

R = Rec()
INF = None
doc = jload('tropical/objects/cole_hopf.json')


def load(key):
    Kd = {}
    for e in doc[key]['K']:
        p = pstrip([F(x) for x in e['poly']])
        Kd[(e['i'], e['j'])] = p
    return Kd, doc[key]['n']

K1, n = load('K_32')
K2, n2 = load('K_32_doob_peeled')
req(n == 32 and n2 == 32, 'size 32')
print('K_32 entries', len(K1), ' peeled entries', len(K2), ' diagonal entries in K:', sum(1 for (i, j) in K1 if i == j), ' in peeled:', sum(1 for (i, j) in K2 if i == j))


def val(p):
    p = pstrip(p)
    if not p:
        return INF
    for i, c in enumerate(p):
        if c != 0:
            return i


def pg(Kd, i, j):
    return Kd.get((i, j), [])


def pm(*ps):
    r = [F(1)]
    for p in ps:
        r = pmul(r, p)
    return r


def eff_vals(Kd, B):
    """exact valuations of K_eff = K_AA + K_AB (I-K_BB)^-1 K_BA over Q(q).  returns dict (i,j)->val (None=inf) or None if I-K_BB singular"""
    A = [i for i in range(n) if i not in B]
    one = [F(1)]
    if len(B) == 1:
        b = B[0]
        Dn = psub(one, pg(Kd, b, b))
        adj = {(b, b): one}
    else:
        b, c = B
        Dn = psub(pmul(psub(one, pg(Kd, b, b)), psub(one, pg(Kd, c, c))), pmul(pg(Kd, b, c), pg(Kd, c, b)))
        adj = {(b, b): psub(one, pg(Kd, c, c)), (b, c): pg(Kd, b, c), (c, b): pg(Kd, c, b), (c, c): psub(one, pg(Kd, b, b))}
    if not Dn:
        return None
    vD = val(Dn)
    out = {}
    for i in A:
        us = [u for u in B if pg(Kd, i, u)]
        for j in A:
            N = pmul(pg(Kd, i, j), Dn)
            if us:
                for u in us:
                    for v in B:
                        if pg(Kd, v, j) and adj.get((u, v)):
                            N = padd(N, pm(pg(Kd, i, u), adj[(u, v)], pg(Kd, v, j)))
            vN = val(N)
            out[(i, j)] = INF if vN is INF else vN - vD
    return out


def trop_eff(Kd, B):
    A = [i for i in range(n) if i not in B]
    T = lambda i, j: val(pg(Kd, i, j))
    big = 10 ** 9
    t = lambda i, j: big if T(i, j) is INF else T(i, j)
    # Kleene star on B (min,+), diagonal 0
    star = {(u, v): (0 if u == v else t(u, v)) for u in B for v in B}
    for w in B:
        for u in B:
            for v in B:
                if star[(u, w)] + star[(w, v)] < star[(u, v)]:
                    star[(u, v)] = star[(u, w)] + star[(w, v)]
    out = {}
    for i in A:
        for j in A:
            best = t(i, j)
            for u in B:
                tu = t(i, u)
                if tu >= big:
                    continue
                for v in B:
                    tv = t(v, j)
                    if tv >= big:
                        continue
                    best = min(best, tu + star[(u, v)] + tv)
            out[(i, j)] = INF if best >= big else best
    return out


blocks_all = [[b] for b in range(n)] + [[b, c] for b in range(n) for c in range(b + 1, n)]
req(len(blocks_all) == 528, '528 blocks')

# ---------------- claim 13
oneway = sorted((i, j) for (i, j) in K1 if i != j and (j, i) not in K1)
print('C13 one-way edges in K:', oneway)
R.check('C13 exactly the 9 listed one-way edges', oneway == [(10, 0), (12, 2), (14, 4), (18, 8), (20, 10), (22, 12), (26, 16), (28, 18), (30, 20)] and len(oneway) == 9)
nil_ok = 0
for (i, j) in oneway:
    Kbb = [[pg(K1, i, i), pg(K1, i, j)], [pg(K1, j, i), pg(K1, j, j)]]
    sq = [[padd(pmul(Kbb[a][0], Kbb[0][b]), pmul(Kbb[a][1], Kbb[1][b])) for b in range(2)] for a in range(2)]
    nonzero = any(Kbb[a][b] for a in range(2) for b in range(2))
    nilp = all(not sq[a][b] for a in range(2) for b in range(2))
    nil_ok += (nonzero and nilp)
R.check('C13 each of the 9 blocks K_BB is nonzero and nilpotent (K_BB^2 = 0)', nil_ok == 9, '%d/9' % nil_ok)
# control: a two-way pair is not nilpotent
two = sorted((i, j) for (i, j) in K1 if i < j and (j, i) in K1)[0]
i, j = two
Kbb = [[pg(K1, i, i), pg(K1, i, j)], [pg(K1, j, i), pg(K1, j, j)]]
sq = [[padd(pmul(Kbb[a][0], Kbb[0][b]), pmul(Kbb[a][1], Kbb[1][b])) for b in range(2)] for a in range(2)]
R.check('CTRL a two-way pair %s is NOT nilpotent (test can say no)' % (two,), any(sq[a][b] for a in range(2) for b in range(2)))

# ---------------- claim 14
def series_check(Kd, B, N=10):
    """second method: truncated Neumann series mod q^N for blocks with val(K_BB)>=1; returns (equal valuations capped at N?)"""
    A = [i for i in range(n) if i not in B]
    def tmul(a, b):
        return pstrip(pmul(a, b)[:N])
    def tadd(a, b):
        return pstrip(padd(a, b)[:N])
    m = len(B)
    KBB = [[pg(Kd, u, v) for v in B] for u in B]
    I_ = [[[F(1)] if a == b else [] for b in range(m)] for a in range(m)]
    inv_ = [[list(x) for x in r] for r in I_]
    P = [[list(x) for x in r] for r in I_]
    for _ in range(N):
        P = [[pstrip(sum_poly([tmul(P[a][c], KBB[c][b]) for c in range(m)], N)) for b in range(m)] for a in range(m)]
        inv_ = [[tadd(inv_[a][b], P[a][b]) for b in range(m)] for a in range(m)]
    out = {}
    for i in A:
        for j in A:
            e = list(pg(Kd, i, j))
            for u in range(m):
                for v in range(m):
                    t1 = pg(Kd, i, B[u]); t2 = pg(Kd, B[v], j)
                    if t1 and t2 and inv_[u][v]:
                        e = tadd(e, tmul(tmul(t1, inv_[u][v]), t2))
            e = pstrip(e[:N])
            out[(i, j)] = val(e)   # None means >= N
    return out

def sum_poly(lst, N):
    r = []
    for p in lst:
        r = padd(r, p)
    return pstrip(r[:N])

def run_trop(Kd, name, series=True):
    eq_blocks = 0; hyp_blocks = 0; eq_hyp = 0; ent = 0; mism_ent = 0; sing = 0
    hyp_mismatch_blocks = []; out_mismatch_blocks = 0; out_blocks = 0
    lower_ok = 0; lower_tot = 0
    ser_ok = 0; ser_tot = 0
    for B in blocks_all:
        ev = eff_vals(Kd, B)
        if ev is None:
            sing += 1
            continue
        te = trop_eff(Kd, B)
        hyp = all((val(pg(Kd, u, v)) is INF or val(pg(Kd, u, v)) >= 1) for u in B for v in B)
        same = True
        for key in ev:
            ent += 1
            a, b = ev[key], te[key]
            if a != b:
                same = False
                mism_ent += 1
            # lower bound val >= T (when T finite) -- count
            if b is not INF:
                lower_tot += 1
                lower_ok += (a is not INF and a >= b)
        eq_blocks += same
        if hyp:
            hyp_blocks += 1
            eq_hyp += same
            if not same:
                hyp_mismatch_blocks.append(B)
            if series:
                N = 10
                sv = series_check(Kd, B, N)
                ok = True
                for key in ev:
                    a = ev[key]
                    s_ = sv[key]
                    if (a is INF or a >= N):
                        ok = ok and (s_ is INF)
                    else:
                        ok = ok and (s_ == a)
                ser_tot += 1; ser_ok += ok
        else:
            out_blocks += 1
            out_mismatch_blocks += (not same)
    print('%s: blocks %d (singular I-K_BB: %d), entries compared %d, entry mismatches %d' % (name, len(blocks_all), sing, ent, mism_ent))
    print('   equal on %d blocks; blocks with val(K_BB)>=1: %d, equal on %d of them (mismatching blocks %s); blocks outside hypothesis: %d, equal-fail on %d of them' % (eq_blocks, hyp_blocks, eq_hyp, hyp_mismatch_blocks[:5], out_blocks, out_mismatch_blocks))
    print('   lower bound val(K_eff) >= T_eff on entries with finite T: %d of %d' % (lower_ok, lower_tot))
    if series:
        print('   independent truncated-series (order 10) valuation check on blocks with val(K_BB)>=1: %d of %d agree with exact' % (ser_ok, ser_tot))
    return dict(eq_blocks=eq_blocks, hyp_blocks=hyp_blocks, eq_hyp=eq_hyp, out_blocks=out_blocks, out_mismatch=out_mismatch_blocks, sing=sing, lower_ok=lower_ok, lower_tot=lower_tot, ser_ok=ser_ok, ser_tot=ser_tot)

r1 = run_trop(K1, 'C14 K')
R.check('C14 K: valuation = (min,+) elimination on 528 of 528 blocks', r1['eq_blocks'] == 528 and r1['hyp_blocks'] == 528)
R.check('C14 K: series method agrees on all blocks', r1['ser_ok'] == r1['ser_tot'] == 528)
r2 = run_trop(K2, "C14 K' (peeled)")
R.check("C14 K': 479 blocks satisfy val(K_BB)>=1 and valuation = (min,+) on all 479; 49 blocks outside", r2['hyp_blocks'] == 479 and r2['eq_hyp'] == 479 and r2['out_blocks'] == 49)
print("   (info) among the 49 blocks outside the hypothesis, valuation != (min,+) on", r2['out_mismatch'])

# control: wrong tropical rule must be flagged: use max instead of min in a perturbed T on one block
Bt = [3]
ev = eff_vals(K1, Bt); te = trop_eff(K1, Bt)
te_bad = dict(te)
k0 = next(k for k, v in te.items() if v is not INF)
te_bad[k0] = te[k0] + 1
R.check('CTRL perturbed tropical value is flagged as different from the exact valuation', any(ev[k] != te_bad[k] for k in ev))

# ---------------- claim 15 and the refuted-lower-bound witness
def eff_poly_2(K00, K01, K10, K11, B):
    """3-state helper not needed; direct two-state computations"""
    pass

q = [F(0), F(1)]
mq2 = [F(0), F(0), F(-1)]
W = {(0, 0): mq2, (0, 1): q, (1, 0): q}
one = [F(1)]
# B={1}: S_00 = K00 + K01 K10 / (1 - K11)
S00 = padd(W[(0, 0)], pmul(pmul(W[(0, 1)], W[(1, 0)]), one))
print('C15 witness K00=-q^2, K01=K10=q, K11=0.  Eliminating B={1}: S_00 =', S00, '(empty list = identically 0); val(K_BB)=val(K11)=inf (>=1 holds); tropical T_00 = min(2, 1+1) = 2')
R.check('C15 B={1}: Schur entry vanishes identically, tropical value 2', S00 == [] and min(2, 1 + 1) == 2)
# B={0}: S_11 = K11 + K10 K01/(1-K00) = q^2/(1+q^2)
N = pmul(W[(1, 0)], W[(0, 1)])
Dn = psub(one, W[(0, 0)])
print('C15 B={0}: S_11 = N/Dn with N =', N, ' Dn =', Dn, ' val(S_11) =', val(N) - val(Dn), ' T_11 = 2; val(K_BB)=val(K00)=2 >= 1')
print('C15 reading: this witness SATISFIES val(K_BB) >= 1 for both choices of B; it breaks equality through cancellation of coefficients (-q^2 + q^2), not through the valuation hypothesis. The lower bound val >= T still holds (inf >= 2).')
# genuinely outside val(K_BB)>=1: the README witness K22 = 1-q, K02=K21=q
K22 = [F(1), F(-1)]; K02 = q; K21 = q
S01 = pmul(K02, pmul(K21, [F(1)]))  # K01=0: S01 = K02 K21/(1-K22), 1-K22 = q
vS = val(pmul(K02, K21)) - val(psub(one, K22))
print('C15b outside hypothesis (val(K22)=0): K22=1-q, K02=K21=q, K01=0: val(S01) = 2 - 1 =', vS, ' T_01 = 2 ->', 'lower bound val>=T violated' if vS < 2 else 'ok')
R.check('C15b witness with val(K_BB)=0 violates the lower bound (val 1 < T 2)', vS == 1)

# ---------------- claim 16 / 17: evaluations at rational q
def Kint(Kd, a, b):
    """integer matrix b^E * K(a/b), E = max degree"""
    E = max(len(p) - 1 for p in Kd.values())
    M = [[0] * n for _ in range(n)]
    for (i, j), p in Kd.items():
        s = F(0)
        for e, c in enumerate(p):
            req(c.denominator == 1, 'integer coefficients')
            s += c * F(a) ** e * F(b) ** (E - e)
        req(s.denominator == 1, 'integer scaled entry')
        M[i][j] = int(s)
    return M

def count_real(Kd, a, b):
    Mi = Kint(Kd, a, b)
    p = charpoly_int(Mi)
    p = [F(x) for x in p]
    return n_real_distinct(p), n_real_with_mult(p), len(p) - 1

for (a, b) in [(1, 10), (1, 1000), (1, 100), (1, 2)]:
    dr, mr, dg = count_real(K1, a, b)
    print('C16 K(q=%d/%d): distinct real eigenvalues %d, real with multiplicity %d, of %d' % (a, b, dr, mr, dg))
    if (a, b) in [(1, 10), (1, 1000)]:
        R.check('C16 q=%d/%d: 32 distinct real eigenvalues' % (a, b), dr == 32 and mr == 32)
    if (a, b) == (1, 2):
        R.check('C16 q=1/2: only 24 of 32 real', mr == 24, '(distinct real %d)' % dr)
# controls
cd = [[0] * 32 for _ in range(32)]
for i in range(32):
    cd[i][i] = i + 1
pc = [F(x) for x in charpoly_int(cd)]
R.check('CTRL diag(1..32): 32 distinct real', n_real_distinct(pc) == 32)
cr = [[0] * 32 for _ in range(32)]
for i in range(32):
    cr[i][i] = i + 1
cr[0][0] = 0; cr[1][1] = 0; cr[0][1] = 1; cr[1][0] = -1
cr[2][2] = 0; cr[3][3] = 0; cr[2][3] = 2; cr[3][2] = -2
pc = [F(x) for x in charpoly_int(cr)]
R.check('CTRL two rotation blocks: 28 real, 4 non-real', n_real_with_mult(pc) == 28)
cdup = [[0] * 32 for _ in range(32)]
for i in range(32):
    cdup[i][i] = (i % 31) + 1
pc = [F(x) for x in charpoly_int(cdup)]
R.check('CTRL repeated eigenvalue: 31 distinct real, 32 with multiplicity', n_real_distinct(pc) == 31 and n_real_with_mult(pc) == 32)

def dd_strict(Mx):
    m = len(Mx)
    return all(abs(Mx[i][i]) > sum(abs(Mx[i][j]) for j in range(m) if j != i) for i in range(m))

def Kq(Kd, qv):
    M = zeros(n, n)
    for (i, j), p in Kd.items():
        M[i][j] = peval(p, qv)
    return M

def run17(qv):
    Kn = Kq(K1, qv)
    ImK = msub(eye(n), Kn)
    ok_full = dd_strict(ImK)
    okB = 0; okE = 0
    for B in blocks_all:
        A = [i for i in range(n) if i not in B]
        IB = msub(eye(len(B)), sub(Kn, B, B))
        okB += dd_strict(IB)
        X = solve(IB, sub(Kn, B, A))
        if X is None:
            continue
        Ke = madd(sub(Kn, A, A), mmul(sub(Kn, A, B), X))
        okE += dd_strict(msub(eye(len(A)), Ke))
    return ok_full, okB, okE

ok_full, okB, okE = run17(F(1, 100))
print('C17 q=1/100: I-K strictly row diag dominant:', ok_full, '; I-K_BB:', okB, 'of 528; I-K_eff:', okE, 'of 528')
R.check('C17 all three at q=1/100', ok_full and okB == 528 and okE == 528)
ok_full2, okB2, okE2 = run17(F(1, 2))
print('CTRL q=1/2: I-K dominant:', ok_full2, '; I-K_BB:', okB2, '; I-K_eff:', okE2)
R.check('CTRL at q=1/2 the dominance test fails somewhere (it can say no)', (not ok_full2) or okE2 < 528)

print('FAILS:', R.bad)
sys.exit(1 if R.bad else 0)
