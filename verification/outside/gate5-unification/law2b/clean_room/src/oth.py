"""Claims 23, 24 (clean-room, exact)."""
import os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ex import *
from common import *

R = Rec()


def mp_inverse(A):
    """exact Moore-Penrose inverse of a rational matrix via full-rank factorisation A = C Fm; A^+ = Fm^T (Fm Fm^T)^-1 (C^T C)^-1 C^T"""
    n, m = len(A), len(A[0])
    Rr, piv = rref(A)
    r = len(piv)
    if r == 0:
        return zeros(m, n)
    C = [[A[i][c] for c in piv] for i in range(n)]
    Fm = [list(Rr[k]) for k in range(r)]
    left = inv(mmul(Fm, tr(Fm)))
    right = inv(mmul(tr(C), C))
    return mmul(mmul(mmul(tr(Fm), left), right), tr(C))


def penrose_ok(A, P):
    AP = mmul(A, P); PA = mmul(P, A)
    return (mmul(AP, A) == A) and (mmul(PA, P) == P) and (AP == tr(AP)) and (PA == tr(PA))


def assemble(A, B, D):
    p, q = len(A), len(D)
    M = zeros(p + q, p + q)
    for i in range(p):
        for j in range(p):
            M[i][j] = A[i][j]
        for j in range(q):
            M[i][p + j] = B[i][j]
            M[p + j][i] = B[i][j]
    for i in range(q):
        for j in range(q):
            M[p + i][p + j] = D[i][j]
    return M


def analyse(A, B, D):
    Ap = mp_inverse(A)
    req(penrose_ok(A, Ap), 'Moore-Penrose equations')
    S = msub(D, mmul(mmul(tr(B), Ap), B))
    M = assemble(A, B, D)
    iM, iA, iS = inertia_cong(M), inertia_cong(A), inertia_cong(S)
    add = (iM == tuple(a + b for a, b in zip(iA, iS)))
    cond = (mmul(mmul(A, Ap), B) == B)
    return dict(Ap=Ap, S=S, M=M, iM=iM, iA=iA, iS=iS, add=add, cond=cond)


def show(tag, A, B, D, r):
    print('%s: A=%s B=%s D=%s' % (tag, A, B, D))
    print('   A^+ = %s (Penrose equations verified exactly)' % r['Ap'])
    print('   S = D - B^T A^+ B = %s ; In(M)=%s In(A)=%s In(S)=%s ; range condition A A^+ B = B: %s ; additivity In(M)=In(A)+In(S): %s' % (r['S'], r['iM'], r['iA'], r['iS'], r['cond'], r['add']))

# exhaustive small search over symmetric 2x2 singular A, B 2xq, D qxq, entries in a small range
cases = {'cond_true_add_true': None, 'cond_false_add_false': None, 'cond_false_add_true': None, 'cond_true_add_false': None}
cnt = {k: 0 for k in cases}
tot = 0
rng = [-1, 0, 1]
for a11, a12, a22 in itertools.product(rng, rng, rng):
    A = fm([[a11, a12], [a12, a22]])
    if det(A) != 0:
        continue
    for b in itertools.product(rng, repeat=2):
        B = fm([[b[0]], [b[1]]])
        for d in [-1, 0, 1]:
            D = fm([[d]])
            r = analyse(A, B, D)
            tot += 1
            key = ('cond_true' if r['cond'] else 'cond_false') + '_' + ('add_true' if r['add'] else 'add_false')
            cnt[key] += 1
            if cases[key] is None:
                cases[key] = (A, B, D, r)
# second exhaustive search: A = [0] (1x1), B 1x2 and D 2x2 symmetric, entries in {-1,0,1}
cnt2 = {k: 0 for k in cnt}
tot2 = 0
for b in itertools.product(rng, repeat=2):
    B = fm([[b[0], b[1]]])
    for d11, d12, d22 in itertools.product(rng, rng, rng):
        D = fm([[d11, d12], [d12, d22]])
        r = analyse(fm([[0]]), B, D)
        tot2 += 1
        key = ('cond_true' if r['cond'] else 'cond_false') + '_' + ('add_true' if r['add'] else 'add_false')
        cnt2[key] += 1
        if cases[key] is None:
            cases[key] = (fm([[0]]), B, D, r)
print('C23 search 1: singular 2x2 symmetric A in {-1,0,1}, B 2x1, D 1x1:', tot, 'systems; counts', cnt)
print('C23 search 2: A=[0], B 1x2, D 2x2 symmetric, entries in {-1,0,1}:', tot2, 'systems; counts', cnt2)
R.check('C23 whenever A A^+ B = B holds, additivity holds (no counterexample in either search)', cnt['cond_true_add_false'] == 0 and cnt2['cond_true_add_false'] == 0 and cnt['cond_true_add_true'] > 0)
R.check('C23 witness: condition fails and additivity fails exists', cases['cond_false_add_false'] is not None)
R.check('C23 witness: condition fails and additivity holds exists', cases['cond_false_add_true'] is not None)
for k in ('cond_true_add_true', 'cond_false_add_false', 'cond_false_add_true'):
    A, B, D, r = cases[k]
    show('C23 witness [%s]' % k, A, B, D, r)
# hand-chosen readable witnesses with 1x1 pivot
A = fm([[0]]); B = fm([[1]]); D = fm([[0]])
r = analyse(A, B, D); show('C23 readable (condition fails, additivity fails)', A, B, D, r)
R.check('C23 readable fail witness: A=[0], B=[1], D=[0]', (not r['cond']) and (not r['add']))
# control: a wrong pseudo-inverse (A^+ replaced by 0 when A != 0) must break the Penrose check
Aw = fm([[1, 0], [0, 0]])
R.check('CTRL a wrong "pseudo-inverse" (zero matrix) is rejected by the Penrose test', not penrose_ok(Aw, zeros(2, 2)))
R.check('CTRL a correct pseudo-inverse of diag(1,0) passes', penrose_ok(Aw, mp_inverse(Aw)))
Aw2 = fm([[2, 2], [2, 2]])
R.check('CTRL A=[[2,2],[2,2]]: A^+ = (1/8) [[1,1],[1,1]]', mp_inverse(Aw2) == msc(F(1, 8), fm([[1, 1], [1, 1]])))

# ---------------- claim 24
p = [F(1, 2), F(1, 4), F(1, 4)]
cols = [[F(3, 4), F(-3, 8), F(-3, 8)], [F(0), F(7, 4), F(-7, 4)], [F(0), F(0), F(0)]]
Wm = tr(cols)   # W has these as columns
Dinv = [[F(1) / p[i] if i == j else F(0) for j in range(3)] for i in range(3)]
G = mmul(mmul(tr(Wm), Dinv), Wm)
print('C24 W^T diag(1/p) W =', G)
R.check('C24 equals diag(9/4, 49/2, 0)', G == [[F(9, 4), 0, 0], [0, F(49, 2), 0], [0, 0, 0]])
# control: wrong p must not give it
p2 = [F(1, 3), F(1, 3), F(1, 3)]
Dinv2 = [[F(1) / p2[i] if i == j else F(0) for j in range(3)] for i in range(3)]
G2 = mmul(mmul(tr(Wm), Dinv2), Wm)
R.check('CTRL with p = (1/3,1/3,1/3) the matrix differs', G2 != [[F(9, 4), 0, 0], [0, F(49, 2), 0], [0, 0, 0]])
# the range-condition theorem itself: if A A^+ B = B then M = E^T diag(A,S) E with E = [[I, A^+ B],[0, I]]
okc = 0; totc = 0
for A_, B_, D_ in [(cases['cond_true_add_true'][0], cases['cond_true_add_true'][1], cases['cond_true_add_true'][2])]:
    r_ = analyse(A_, B_, D_)
    p_, q_ = len(A_), len(D_)
    E = eye(p_ + q_)
    AB = mmul(r_['Ap'], B_)
    for i in range(p_):
        for j in range(q_):
            E[i][p_ + j] = AB[i][j]
    Dg = zeros(p_ + q_, p_ + q_)
    for i in range(p_):
        for j in range(p_):
            Dg[i][j] = A_[i][j]
    for i in range(q_):
        for j in range(q_):
            Dg[p_ + i][p_ + j] = r_['S'][i][j]
    okc += (mmul(mmul(tr(E), Dg), E) == r_['M']); totc += 1
R.check('C23 congruence M = E^T diag(A,S) E with E=[[I,A^+B],[0,I]] verified exactly on the witness with the range condition', okc == totc == 1)
# hand witness for 'fails the condition yet additivity holds'
A = fm([[0]]); B = fm([[1, 0]]); D = fm([[0, 1], [1, 0]])
r = analyse(A, B, D); show('C23 readable (condition fails, additivity holds)', A, B, D, r)
R.check('C23 readable witness: A=[0], B=[[1,0]], D=[[0,1],[1,0]]: M is the path graph P3 (eigenvalues +-sqrt2, 0); In(M)=(1,1,1)=(0,0,1)+(1,1,0)', (not r['cond']) and r['add'] and r['iM'] == (1, 1, 1))
print('FAILS:', R.bad)
sys.exit(1 if R.bad else 0)
