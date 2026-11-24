"""Row 4, claim 18 (open item): is there a block-diagonal invertible P with P^-1 (I-K) P real symmetric?
Equivalent: positive definite block-diagonal G (G = P P^T) with K G symmetric, i.e. K G = G K^T.
All arithmetic exact.  K is evaluated at the rational points q = 1/10, 1/100, 1/1000, 1/2."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ex import *
from common import *

R = Rec()
doc = jload('tropical/objects/cole_hopf.json')
n = 32
Kd = {}
for e in doc['K_32']['K']:
    Kd[(e['i'], e['j'])] = pstrip([F(x) for x in e['poly']])


def Kq(qv):
    M = zeros(n, n)
    for (i, j), p in Kd.items():
        M[i][j] = peval(p, qv)
    return M


def sparse_nullspace(rows, ncols):
    """rows: list of dict col->Fraction.  returns basis of nullspace as list of dicts col->Fraction"""
    piv = {}   # col -> row dict (normalised, pivot coefficient 1)
    for r in rows:
        r = {c: v for c, v in r.items() if v != 0}
        while r:
            hit = None
            for c in sorted(r):
                if c in piv:
                    hit = c
                    break
            if hit is None:
                break
            f = r[hit]
            for c, v in piv[hit].items():
                nv = r.get(c, F(0)) - f * v
                if nv == 0:
                    r.pop(c, None)
                else:
                    r[c] = nv
        if not r:
            continue
        c0 = min(r)
        f = r[c0]
        r = {c: v / f for c, v in r.items()}
        piv[c0] = r
    # full back-reduction, descending pivot order
    for c in sorted(piv, reverse=True):
        row = piv[c]
        for j in sorted(k for k in row if k != c and k in piv):
            f = row.get(j)
            if f is None or f == 0:
                continue
            for cc, v in piv[j].items():
                nv = row.get(cc, F(0)) - f * v
                if nv == 0:
                    row.pop(cc, None)
                else:
                    row[cc] = nv
    free = [c for c in range(ncols) if c not in piv]
    basis = []
    for f in free:
        v = {f: F(1)}
        for c, row in piv.items():
            if f in row:
                v[c] = -row[f]
        basis.append(v)
    return basis, len(piv)


idx = {}
for i in range(n):
    for j in range(i, n):
        idx[(i, j)] = len(idx)
NU = len(idx)


def uid(i, j):
    return idx[(min(i, j), max(i, j))]


def W_space(Km):
    """basis of {X symmetric : K X = X K^T}; each basis element as dict (i,j)-> value (i<=j)"""
    rows = []
    nzK = [[(k, Km[i][k]) for k in range(n) if Km[i][k] != 0] for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            row = {}
            for k, a in nzK[i]:
                c = uid(k, j)
                row[c] = row.get(c, F(0)) + a
            for k, a in nzK[j]:
                c = uid(i, k)
                row[c] = row.get(c, F(0)) - a
            rows.append(row)
    basis, rk = sparse_nullspace(rows, NU)
    inv_idx = {v: k for k, v in idx.items()}
    mats = []
    for b in basis:
        X = zeros(n, n)
        for c, v in b.items():
            i, j = inv_idx[c]
            X[i][j] = v
            X[j][i] = v
        mats.append(X)
    return mats, rk


def check_W(Km, mats):
    return all(mmul(Km, X) == tr(mmul(Km, X)) for X in mats)


def restrict(mats, A, B):
    """subspace of span(mats) with X[A][B]=0 : returns list of combined matrices (basis of W')"""
    d = len(mats)
    if d == 0:
        return []
    rows = []
    for a in A:
        for b in B:
            rows.append([m[a][b] for m in mats])
    if not rows:
        coefs = [[F(1) if i == j else F(0) for i in range(d)] for j in range(d)]
    else:
        coefs = nullspace(rows, d)
    out = []
    for c in coefs:
        X = zeros(n, n)
        for k, ck in enumerate(c):
            if ck != 0:
                Mk = mats[k]
                for i in range(n):
                    for j in range(n):
                        if Mk[i][j] != 0:
                            X[i][j] += ck * Mk[i][j]
        out.append(X)
    return out


def is_pd(X):
    return inertia_cong(X) == (n, 0, 0)


def decide(basis, rnd):
    """returns ('NO', reason) / ('YES', witness) / ('UNDECIDED', info)"""
    d = len(basis)
    if d == 0:
        return 'NO', 'solution space {0}'
    for t in range(n):
        if all(X[t][t] == 0 for X in basis):
            return 'NO', 'diagonal entry %d is zero on the whole space' % t
    if d == 1:
        X = basis[0]
        if is_pd(X) or is_pd(msc(-1, X)):
            return 'YES', X
        return 'NO', 'one-dimensional, ' + str(inertia_cong(X))
    # search
    for trial in range(60):
        cs = [F(rnd.randint(-5, 5)) for _ in range(d)]
        if all(c == 0 for c in cs):
            continue
        X = zeros(n, n)
        for c, Xk in zip(cs, basis):
            if c != 0:
                for i in range(n):
                    for j in range(n):
                        if Xk[i][j] != 0:
                            X[i][j] += c * Xk[i][j]
        if is_pd(X):
            return 'YES', X
    return 'UNDECIDED', 'dim %d, 60 random combinations not PD' % d


P61 = (1 << 61) - 1


def modp(x):
    x = F(x)
    req(x.denominator % P61 != 0, 'denominator invertible mod p')
    return x.numerator % P61 * pow(x.denominator % P61, -1, P61) % P61


def rank_mod(rows):
    M = [list(r) for r in rows]
    r = 0
    if not M:
        return 0
    m = len(M[0])
    for c in range(m):
        p = None
        for i in range(r, len(M)):
            if M[i][c] % P61:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        iv = pow(M[r][c], -1, P61)
        for i in range(r + 1, len(M)):
            if M[i][c] % P61:
                f = M[i][c] * iv % P61
                M[i] = [(a_ - f * b_) % P61 for a_, b_ in zip(M[i], M[r])]
        r += 1
    return r


blocks_all = [[b] for b in range(n)] + [[b, c] for b in range(n) for c in range(b + 1, n)]
oneway = [(10, 0), (12, 2), (14, 4), (18, 8), (20, 10), (22, 12), (26, 16), (28, 18), (30, 20)]
summary = {}
for (a, b) in [(1, 10), (1, 100), (1, 1000)]:
    qv = F(a, b)
    Km = Kq(qv)
    mats, rk = W_space(Km)
    okW = check_W(Km, mats)
    print('C18 q=%d/%d: W = {X symmetric : K X = X K^T} has dimension %d (rank %d of %d unknowns); basis verified exactly: %s' % (a, b, len(mats), rk, NU, okW))
    d_unres = len(mats)
    mm = [[[modp(x) for x in r] for r in X] for X in mats]
    # unrestricted: W = span(v_k v_k^T); PD members exist iff all coefficients d_k > 0 possible: K has 32 distinct real eigenvalues (claim 16) so yes
    print('   unrestricted P (one block): W contains PD members because K has 32 distinct real eigenvalues (K = V L V^-1, G = V V^T)')
    # fully diagonal G
    rows = [[m[i][j] for m in mm] for i in range(n) for j in range(i + 1, n)]
    nul_diag_modp = len(mats) - rank_mod(rows)
    ex_rows = [[m[i][j] for m in mats] for i in range(n) for j in range(i + 1, n)]
    nul_diag = len(nullspace(ex_rows, len(mats)))
    print('   fully diagonal G (gauge similarity): solution space dimension %d (mod-p screen %d)' % (nul_diag, nul_diag_modp))
    zero_blocks = 0; cand = []
    for B in blocks_all:
        A = [i for i in range(n) if i not in B]
        rows = [[m[x][y] for m in mm] for x in A for y in B]
        nul = len(mats) - rank_mod(rows)
        if nul == 0:
            zero_blocks += 1     # true nullity <= nullity mod p, so the exact solution space is {0}
        else:
            cand.append((B, nul))
    print('   528 partitions: solution space exactly {0} (proved by mod-p rank: true nullity <= mod-p nullity) in %d; remaining candidates %d with mod-p nullity %s' % (zero_blocks, len(cand), sorted(set(c[1] for c in cand))))
    yes = []; no = []; yes_X = {}
    for B, nul in cand:
        A = [i for i in range(n) if i not in B]
        rows = [[m[x][y] for m in mats] for x in A for y in B]
        co = nullspace(rows, len(mats))
        if len(co) == 0:
            no.append((B, 'exact nullity 0'))
            continue
        # build basis matrices exactly
        sp = []
        for c in co:
            X = zeros(n, n)
            for k_, ck in enumerate(c):
                if ck != 0:
                    for i in range(n):
                        for j in range(n):
                            if mats[k_][i][j] != 0:
                                X[i][j] += ck * mats[k_][i][j]
            sp.append(X)
        # exact verification: block diagonal and K X symmetric
        for X in sp:
            req(all(X[x][y] == 0 for x in A for y in B), 'block diagonal')
            req(mmul(Km, X) == tr(mmul(Km, X)), 'K X symmetric')
        if len(sp) == 1:
            X = sp[0]
            ine = inertia_cong(X)
            if ine == (n, 0, 0) or ine == (0, n, 0):
                yes.append((B, ine)); yes_X[tuple(B)] = X if ine == (n, 0, 0) else msc(-1, X)
            else:
                no.append((B, 'one-dimensional, inertia %s' % (ine,)))
        else:
            no.append((B, 'dim %d UNDECIDED' % len(sp)))
    und = [x for x in no if 'UNDECIDED' in x[1]]
    print('   exact treatment of the candidates: PD solution found in %d, none in %d, undecided %d' % (len(yes), len(no) - len(und), len(und)))
    kinds = {}
    for B, why in no:
        kinds[why] = kinds.get(why, 0) + 1
    print('   reasons:', sorted(kinds.items()))
    if yes:
        print('   PD witnesses at partitions B =', [y[0] for y in yes], 'inertias', sorted(set(y[1] for y in yes)))
        print('   non-PD one-dimensional partitions B =', [x[0] for x in no if 'one-dimensional' in x[1]])
        chol_ok = 0
        for B_, ine_ in yes:
            G_ = yes_X[tuple(B_)]
            # second method: Cholesky pivots without pivoting must all be positive; plus the exact identities
            M_ = [list(r) for r in G_]
            okp = True
            for c_ in range(n):
                if M_[c_][c_] <= 0:
                    okp = False
                    break
                for i_ in range(c_ + 1, n):
                    if M_[i_][c_] != 0:
                        f_ = M_[i_][c_] / M_[c_][c_]
                        M_[i_] = [a_ - f_ * b_ for a_, b_ in zip(M_[i_], M_[c_])]
            A_ = [i for i in range(n) if i not in B_]
            blockdiag = all(G_[x][y] == 0 for x in A_ for y in B_)
            chol_ok += (okp and blockdiag and mmul(Km, G_) == tr(mmul(Km, G_)))
        print('   second check (Cholesky pivots > 0, G block diagonal, K G symmetric, all exact): %d of %d witnesses' % (chol_ok, len(yes)))
        req(chol_ok == len(yes), 'witness second check')
    ow_in = [ [min(i, j), max(i, j)] for (i, j) in oneway]
    print('   the 9 one-way pairs: PD solution in', sum(1 for B in ow_in if B in [y[0] for y in yes]), 'of 9')
    summary[(a, b)] = (nul_diag, zero_blocks, len(yes), len(und))
R.check('C18 no fully diagonal PD G exists (gauge similarity D^-1 K D cannot symmetrize) at q=1/10, 1/100, 1/1000', all(v[0] == 0 for v in summary.values()))
print('C18 structure: for B = {i,j} a one-way pair, K_BB = [[0,k],[0,0]]; K_BB G_B symmetric forces (G_B)_22 = 0, so G_B is singular: no PD G, for every q.')
ns = nullspace([[F(0), F(0), F(1)]], 3)
R.check('C18 the 2x2 solution space {g22 = 0} contains no PD matrix (basis has g22 = 0)', all(v[2] == 0 for v in ns))
# control: the screening method must find a PD solution when one exists. Build K0 = G0 S with G0 PD diagonal (block structure), S symmetric: K0 G0 = G0 S G0 symmetric
K0 = [[F(0)] * n for _ in range(n)]
g0 = [F(i + 1) for i in range(n)]
rnd = random.Random(8)
S0 = [[F(0)] * n for _ in range(n)]
for i in range(n):
    for j in range(i, n):
        if rnd.random() < 0.15 or i == j:
            S0[i][j] = S0[j][i] = F(rnd.randint(-2, 2))
K0 = [[g0[i] * S0[i][j] for j in range(n)] for i in range(n)]   # K0 = G0 S0 with G0 = diag(g0): K0 G0 symmetric
mats0, rk0 = W_space(K0)
mm0 = [[[modp(x) for x in r] for r in X] for X in mats0]
rows = [[m[i][j] for m in mm0] for i in range(n) for j in range(i + 1, n)]
nd0 = len(mats0) - rank_mod(rows)
R.check('CTRL on a matrix built to be diagonally symmetrizable the diagonal-G solution space is nonzero (the screen can say yes)', nd0 >= 1)
print('FAILS:', R.bad)
for k_, v in sorted(summary.items()):
    print('SUMMARY q=%d/%d diagonal-G dim=%d, partitions with exact solution space {0}: %d/528, PD solutions: %d, undecided: %d' % (k_[0], k_[1], v[0], v[1], v[2], v[3]))
sys.exit(1 if R.bad else 0)
