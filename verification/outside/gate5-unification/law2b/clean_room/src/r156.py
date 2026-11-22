"""Rows 1, 5, 6 equivalence: claims 19, 20 (clean-room, exact)."""
import os, sys, re, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ex import *
from common import *

R = Rec()
sp = jload('hermitian/objects/spectral_inertia_hermitian.json')['points']
ae = jload('hermitian/objects/aest_gravity_hamiltonian.json')['points']
lq = jload('hermitian/objects/open_quantum_liouvillian.json')['points']
print('row1 points', len(sp), ' row5 points', len(ae), ' pairs', len(sp) * len(ae))

# Row 1 object: the 3x3 real symmetric bordered matrix B = [[S,t,u],[t,b,0],[u,0,0]] (pivot = indices 0,1; rest = index 2).
# The package stores B only through invariants, so B is rebuilt from the stored scalars and checked against the stored invariants.
def rowB(p):
    S, t, u = F(p['scalars']['S']), F(p['scalars']['t']), F(p['scalars']['u'])
    b = F(p['b'])
    return [[S, t, u], [t, b, F(0)], [u, F(0), F(0)]]

def parse_det(s):
    return F(s)

objs1 = []
for p in sp:
    Bm = rowB(p)
    A2 = sub(Bm, [0, 1], [0, 1])
    Sc = schur(Bm, [2], [0, 1])
    # cross-check against the stored invariants of the package
    stored_pdet = F(p['B']['pivot_det'])
    stored_red = F(p['B']['reduced'][0][0])
    req(det(A2) == stored_pdet, 'rebuilt B pivot det matches stored for ' + p['label'])
    req(Sc[0][0] == stored_red, 'rebuilt B Schur matches stored for ' + p['label'])
    objs1.append((p['label'], Bm, A2, Sc))
objs5 = []
for p in ae:
    H = fmat(p['full'])
    A2 = sub(H, [0, 1], [0, 1])
    Sc = schur(H, [2], [0, 1])
    req(det(A2) == F(p['pivot_det']), 'aest pivot det matches stored ' + p['label'])
    req(Sc[0][0] == F(p['reduced'][0][0]), 'aest Schur matches stored ' + p['label'])
    objs5.append((p['label'], H, A2, Sc))
print('rebuilt objects match the stored pivot determinants and Schur entries: 12 + 14')

def inv_of(o):
    label, X, A2, Sc = o
    return dict(n=len(X), inA=inertia_cong(A2), inS=inertia_cong(Sc), dA=det(A2), dS=det(Sc))

I1 = [inv_of(o) for o in objs1]
I5 = [inv_of(o) for o in objs5]

def compare(a, b):
    """returns name of first failing criterion or None"""
    if a['n'] != b['n']:
        return 'dimension'
    if a['inA'] != b['inA']:
        return 'inertia_A'
    if a['inS'] != b['inS']:
        return 'inertia_S'
    if not same_square_class(a['dA'], b['dA']):
        return 'sqclass_detA'
    if not same_square_class(a['dS'], b['dS']):
        return 'sqclass_detS'
    return None

from collections import Counter
first = Counter(); agree = 0
any_inS = any_inA = any_sqA = any_sqS = 0
for a in I1:
    for b in I5:
        f = compare(a, b)
        first[f] += 1
        agree += (f is None)
        any_inA += (a['inA'] != b['inA'])
        any_inS += (a['inS'] != b['inS'])
        any_sqA += (not same_square_class(a['dA'], b['dA']))
        any_sqS += (not same_square_class(a['dS'], b['dS']))
print('C19 first failing criterion (order: dimension, inertia A, inertia S, sqclass detA, sqclass detS):', dict(first))
print('C19 pairs failing each criterion independently: inertia_A %d, inertia_S %d, sqclass_detA %d, sqclass_detS %d (of 168)' % (any_inA, any_inS, any_sqA, any_sqS))
R.check('C19 no pair agrees on all invariants: 0 of 168', agree == 0, 'agree=%d' % agree)
print('   pairs failing on inertia of the reduced block S: %d; failing first on sqclass(detA) after inertia agrees: %d' % (first['inertia_S'], first['sqclass_detA']))
R.check('C19 108 fail on inertia of reduced block, 60 on square class of det A', first['inertia_S'] == 108 and first['sqclass_detA'] == 60, str(dict(first)))
print('   inertia(A) values (row1):', sorted(set(a['inA'] for a in I1)), ' (row5):', sorted(set(a['inA'] for a in I5)))
print('   inertia(S) values (row1):', Counter(a['inS'] for a in I1), ' (row5):', Counter(a['inS'] for a in I5))
# second method for the square-class failures: small-prime / sign witness
def val_p(x, pr):
    x = F(x)
    v = 0
    nn, dd = x.numerator, x.denominator
    while nn % pr == 0:
        nn //= pr; v += 1
    while dd % pr == 0:
        dd //= pr; v -= 1
    return v
small_primes = [pr for pr in range(2, 20000) if all(pr % d for d in range(2, int(pr ** 0.5) + 1))]
witnessed = 0; sqfail = 0
for a in I1:
    for b in I5:
        if not same_square_class(a['dA'], b['dA']):
            sqfail += 1
            ratio = a['dA'] / b['dA']
            if ratio < 0 or any(val_p(ratio, pr) % 2 for pr in small_primes):
                witnessed += 1
print('C19 second method: of %d det-A square-class mismatches, %d have an explicit witness (sign or odd p-adic valuation at a prime < 20000); the exact isqrt test decides all of them' % (sqfail, witnessed))
# controls
selfagree = sum(1 for a in I1 for b in I1 if a is b and compare(a, b) is None)
R.check('CTRL each object agrees with itself (test can say yes): 12/12 and 14/14', selfagree == 12 and sum(1 for a in I5 for b in I5 if a is b and compare(a, b) is None) == 14)
a0 = dict(I5[0]); a1 = dict(I5[0]); a1['dA'] = a0['dA'] * F(9, 4); a1['dS'] = a0['dS'] * F(25, 49)
R.check('CTRL rescaling det by rational squares keeps agreement', compare(a0, a1) is None)
a2 = dict(a0); a2['dA'] = a0['dA'] * 2
R.check('CTRL rescaling det A by 2 breaks the square class', compare(a0, a2) == 'sqclass_detA')

# ---------------- claim 20
def rowsum_max(X):
    return max(sum(abs(x) for x in r) for r in X)
rs = {}
rs['row1 B (3x3)'] = max(rowsum_max(o[1]) for o in objs1)
rs['row5 aest (3x3)'] = max(rowsum_max(o[1]) for o in objs5)
Ml = [fmat(p['full']) for p in lq]
rs['row6 Liouvillian M'] = max(rowsum_max(M) for M in Ml)
rs['row6 sym(M)'] = max(rowsum_max(sym_part(M)) for M in Ml)
# row 1 Hermitian M_full over Q(i): parse
def parse_qi(s):
    m = re.fullmatch(r'(-?\d+(?:/\d+)?)(?:([+-]\d+(?:/\d+)?)i)?', s)
    req(m is not None, 'parse Q(i) entry ' + s)
    return F(m.group(1)), F(m.group(2) if m.group(2) else 0)
Mf = []
for p in sp:
    Mf.append([[parse_qi(x) for x in r] for r in p['M_full']])
ub = max(max(sum(abs(re_) + abs(im_) for re_, im_ in r) for r in X) for X in Mf)
lb = max(max(sum(max(abs(re_), abs(im_)) for re_, im_ in r) for r in X) for X in Mf)
rs['row1 M_full (Q(i), upper bound sum|re|+|im|)'] = ub
rs['row1 M_full (Q(i), lower bound sum max(|re|,|im|))'] = lb
for k, v in rs.items():
    print('C20 largest absolute row sum, %s: %s (= %s)' % (k, v, str(float(v)) if False else v))
overall = max(rs['row1 B (3x3)'], rs['row5 aest (3x3)'])
print('C20 largest absolute row sum over the objects of the 168 pairs (row 1 B, row 5 aest):', overall, '; the row-1 Hermitian M_full lies in [%s, %s] (below it)' % (lb, ub))
print('C20 the row-6 Liouvillian objects have larger row sums (up to %s), so 871 is NOT one more than the largest row sum if row 6 is counted' % rs['row6 Liouvillian M'])
lam = math.floor(max(overall, ub)) + 1
print('C20 lambda = floor(max row sum) + 1 over rows 1 and 5 =', lam)
R.check('C20 lambda = 871 for the row 1 and row 5 objects', lam == 871 and overall == 870)
lam = F(871)
def pd_shift_sym(X):
    n_ = len(X)
    Y = [[X[i][j] + (lam if i == j else 0) for j in range(n_)] for i in range(n_)]
    return inertia_cong(sym_part(Y)) == (n_, 0, 0)
okc = 0; tot = 0
for o in objs1: okc += pd_shift_sym(o[1]); tot += 1
for o in objs5: okc += pd_shift_sym(o[1]); tot += 1
for X in Mf:
    n_ = len(X)
    E = zeros(2 * n_, 2 * n_)
    for i in range(n_):
        for j in range(n_):
            re_, im_ = X[i][j]
            E[i][j] = re_; E[n_ + i][n_ + j] = re_
            E[i][n_ + j] = -im_; E[n_ + i][j] = im_
    okc += pd_shift_sym(E); tot += 1
R.check('C20 every row-1 object (B and Hermitian M_full via real embedding) and row-5 object plus 871 I is positive definite: %d objects' % tot, okc == tot, '%d/%d' % (okc, tot))
okl = sum(1 for M in Ml if pd_shift_sym(M))
print('C20 row-6 Liouvillian: sym(M)+871 I positive definite at %d of 17 points (so row 6 needs a larger shift; 871 was only claimed for the 168-pair objects)' % okl)
# after the shift: agree in (dim, inertia of A, inertia of S)?
def shifted_inv(o):
    label, X, A2, Sc = o
    Y = [[X[i][j] + (lam if i == j else 0) for j in range(3)] for i in range(3)]
    A2s = sub(Y, [0, 1], [0, 1]); Ss = schur(Y, [2], [0, 1])
    return (3, inertia_cong(A2s), inertia_cong(Ss))
sh1 = [shifted_inv(o) for o in objs1]; sh5 = [shifted_inv(o) for o in objs5]
ag = sum(1 for a in sh1 for b in sh5 if a == b)
R.check('C20 after the shift all 168 pairs agree in (dim, inertia A, inertia S)', ag == 168, '%d/168' % ag)
rnd = random.Random(200200)
def rsym3():
    X = [[F(0)] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(i, 3):
            X[i][j] = X[j][i] = F(rnd.randint(-20, 20), rnd.randint(1, 5))
    return X
agr = 0
for t in range(200):
    X, Y = rsym3(), rsym3()
    sx, sy = shifted_inv(('x', X, None, None)), shifted_inv(('y', Y, None, None))
    agr += (sx == sy)
R.check('C20 same for 200 random symmetric 3x3 pairs (entries up to 20): they all agree after the shift too, so the shift proves nothing', agr == 200, '%d/200' % agr)
# control: without the shift random pairs do NOT all agree
dis = 0
for t in range(200):
    X, Y = rsym3(), rsym3()
    dis += (inertia_cong(X) != inertia_cong(Y))
R.check('CTRL without the shift random symmetric pairs often differ in inertia (test can say no)', dis > 0, '%d/200 differ' % dis)
print('FAILS:', R.bad)
sys.exit(1 if R.bad else 0)
