"""Exact clean-room library for the tropical / LP rows audit.

Everything on a decision path is int, Fraction, a polynomial in q with Fraction
coefficients (tuple, lowest degree first, no trailing zeros) or a min-plus value
(int, or None for infinity).  No floats, no numpy, no bare assert.
"""
import heapq
import json
import sys
from fractions import Fraction


class AuditError(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise AuditError(msg)


def fr(x):
    if isinstance(x, bool):
        raise AuditError("bool is not a number")
    if isinstance(x, (int, Fraction)):
        return Fraction(x)
    if isinstance(x, str):
        return Fraction(x)
    raise AuditError("not exact: %r" % (type(x),))


def fstr(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def dump(obj):
    """Canonical deterministic JSON (LF, sorted keys)."""
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=True) + "\n"


# ---------------------------------------------------------------- polynomials
ZERO = Fraction(0)
ONE = Fraction(1)


def ptrim(c):
    c = list(c)
    while c and c[-1] == 0:
        c.pop()
    return tuple(c)


def pmono(c, e):
    c = fr(c)
    if c == 0:
        return ()
    return tuple([ZERO] * e + [c])


def padd(a, b):
    n = max(len(a), len(b))
    return ptrim([(a[i] if i < len(a) else ZERO) + (b[i] if i < len(b) else ZERO) for i in range(n)])


def pneg(a):
    return tuple(-x for x in a)


def psub(a, b):
    return padd(a, pneg(b))


def pmul(a, b):
    if not a or not b:
        return ()
    r = [ZERO] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    r[i + j] += x * y
    return ptrim(r)


def pval(a):
    """lowest exponent with a nonzero coefficient, None for the zero polynomial"""
    for i, x in enumerate(a):
        if x != 0:
            return i
    return None


def plead(a):
    v = pval(a)
    return None if v is None else (v, a[v])


def pjson(a):
    return [fstr(x) for x in a]


def pdet(M):
    n = len(M)
    if n == 0:
        return (ONE,)
    if n == 1:
        return M[0][0]
    tot = ()
    for j in range(n):
        if not M[0][j]:
            continue
        minor = [[M[i][k] for k in range(n) if k != j] for i in range(1, n)]
        term = pmul(M[0][j], pdet(minor))
        tot = padd(tot, term) if j % 2 == 0 else psub(tot, term)
    return tot


def padj(M):
    """adjugate: M * adj(M) = det(M) * I"""
    n = len(M)
    if n == 1:
        return [[(ONE,)]]
    adj = [[() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = [[M[r][c] for c in range(n) if c != j] for r in range(n) if r != i]
            d = pdet(minor)
            adj[j][i] = d if (i + j) % 2 == 0 else pneg(d)
    return adj


# ----------------------------------------------------------- min-plus helpers
def mp_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if a <= b else b


def mp_mul(a, b):
    if a is None or b is None:
        return None
    return a + b


def trop_matrix(K):
    return [[pval(e) for e in row] for row in K]


def minplus_schur(T, A, B):
    """A_AA (+) A_AB (x) A_BB^* (x) A_BA in (min,+); star by Floyd-Warshall (no negative cycles)."""
    R = {}
    for k in B:
        for l in B:
            R[(k, l)] = 0 if k == l else T[k][l]
            if k == l and T[k][k] is not None:
                require(T[k][k] >= 0, "negative cycle in min-plus block")
    for m in B:
        for k in B:
            for l in B:
                R[(k, l)] = mp_add(R[(k, l)], mp_mul(R[(k, m)], R[(m, l)]))
    out = {}
    for i in A:
        for j in A:
            best = T[i][j]
            for k in B:
                if T[i][k] is None:
                    continue
                for l in B:
                    if T[l][j] is None or R[(k, l)] is None:
                        continue
                    best = mp_add(best, T[i][k] + R[(k, l)] + T[l][j])
            out[(i, j)] = best
    return out


# ------------------------------------------ Schur complement of (I - K) over Q(q)
def schur_rational(K, A, B):
    """S = K_AA + K_AB (I-K_BB)^{-1} K_BA as entries (num, den) over Q[q]; None if I-K_BB singular."""
    nb = len(B)
    N = [[psub((ONE,) if k == l else (), K[k][l]) for l in B] for k in B]
    D = pdet(N)
    if not D:
        return None
    adj = padj(N)
    out = {}
    for i in A:
        for j in A:
            num = pmul(K[i][j], D)
            for a, k in enumerate(B):
                if not K[i][k]:
                    continue
                for b, l in enumerate(B):
                    if adj[a][b] and K[l][j]:
                        num = padd(num, pmul(pmul(K[i][k], adj[a][b]), K[l][j]))
            out[(i, j)] = (num, D)
    return out


def rat_val(nd):
    num, den = nd
    if not num:
        return None
    return pval(num) - pval(den)


# --------------------------- independent second checker: truncated power series
def series_schur_vals(K, A, B, M):
    """Valuation of S_ij by truncated Neumann series mod q^M.  Requires K_BB(0) = 0.
    Returns dict (i,j) -> int valuation if below M else None (meaning >= M or zero)."""
    def tr(p):
        return [p[e] if e < len(p) else ZERO for e in range(M)]

    Kt = {}
    for i in range(len(K)):
        for j in range(len(K)):
            if K[i][j]:
                Kt[(i, j)] = tr(K[i][j])
    for k in B:
        for l in B:
            if (k, l) in Kt:
                require(Kt[(k, l)][0] == 0, "series checker needs K_BB(0)=0")

    def smul(x, y):
        r = [ZERO] * M
        for a in range(M):
            if x[a]:
                for b in range(M - a):
                    if y[b]:
                        r[a + b] += x[a] * y[b]
        return r

    def sadd(x, y):
        return [x[e] + y[e] for e in range(M)]

    # Z = sum_k K_BB^k  as dict (k,l)->series, computed by fixed-point iteration Z <- I + K_BB Z
    zero = [ZERO] * M
    one = [ONE] + [ZERO] * (M - 1)
    Z = {(k, l): (one if k == l else zero) for k in B for l in B}
    for _ in range(M + len(B) + 1):
        newZ = {}
        for k in B:
            for l in B:
                acc = one if k == l else zero
                for m in B:
                    if (k, m) in Kt:
                        acc = sadd(acc, smul(Kt[(k, m)], Z[(m, l)]))
                newZ[(k, l)] = acc
        Z = newZ
    out = {}
    for i in A:
        for j in A:
            acc = Kt.get((i, j), zero)
            for k in B:
                if (i, k) not in Kt:
                    continue
                for l in B:
                    if (l, j) not in Kt:
                        continue
                    acc = sadd(acc, smul(smul(Kt[(i, k)], Z[(k, l)]), Kt[(l, j)]))
            v = None
            for e in range(M):
                if acc[e] != 0:
                    v = e
                    break
            out[(i, j)] = v
    return out


# ----------- leading-coefficient semiring: predicts exactly when valuation commutes
def _lead_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if a[0] < b[0]:
        return a
    if b[0] < a[0]:
        return b
    return (a[0], a[1] + b[1])


def _lead_mul(a, b):
    if a is None or b is None:
        return None
    return (a[0] + b[0], a[1] * b[1])


def lead_schur(K, A, B):
    """(valuation, leading coefficient at the tropical value) of S_ij, valid when val(K_BB) > 0.
    The sum over minimizing walks of the products of leading coefficients."""
    Lk = [[plead(e) for e in row] for row in K]
    for k in B:
        for l in B:
            if Lk[k][l] is not None:
                require(Lk[k][l][0] > 0, "lead_schur needs val(K_BB) > 0")
    X = {(k, l): ((0, ONE) if k == l else None) for k in B for l in B}
    for _ in range(len(B) + 1):
        newX = {}
        for k in B:
            for l in B:
                acc = (0, ONE) if k == l else None
                for m in B:
                    acc = _lead_add(acc, _lead_mul(Lk[k][m], X[(m, l)]))
                newX[(k, l)] = acc
        X = newX
    out = {}
    for i in A:
        for j in A:
            acc = Lk[i][j]
            for k in B:
                for l in B:
                    acc = _lead_add(acc, _lead_mul(_lead_mul(Lk[i][k], X[(k, l)]), Lk[l][j]))
            out[(i, j)] = acc
    return out


def mmatrix_nonneg_ok(K0):
    """exact: K0 >= 0 entrywise and I-K0 a nonsingular M-matrix (all leading principal minors > 0),
    equivalently spectral radius < 1."""
    n = len(K0)
    for r in K0:
        for x in r:
            if x < 0:
                return False
    for m in range(1, n + 1):
        sub = [[(ONE if i == j else ZERO) - K0[i][j] for j in range(m)] for i in range(m)]
        if frac_det(sub) <= 0:
            return False
    return True


def frac_det(M):
    n = len(M)
    A = [list(r) for r in M]
    det = ONE
    for c in range(n):
        p = None
        for r in range(c, n):
            if A[r][c] != 0:
                p = r
                break
        if p is None:
            return ZERO
        if p != c:
            A[c], A[p] = A[p], A[c]
            det = -det
        det *= A[c][c]
        for r in range(c + 1, n):
            if A[r][c] != 0:
                f = A[r][c] / A[c][c]
                for k in range(c, n):
                    A[r][k] -= f * A[c][k]
    return det


# ------------------------------------------------------- linear algebra over Q
def solve_exact(A, b):
    """Solve A x = b exactly (square, nonsingular); None if singular."""
    n = len(A)
    M = [list(map(Fraction, A[i])) + [Fraction(b[i])] for i in range(n)]
    for c in range(n):
        p = None
        for r in range(c, n):
            if M[r][c] != 0:
                p = r
                break
        if p is None:
            return None
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [M[r][k] - f * M[c][k] for k in range(n + 1)]
    return [M[i][n] for i in range(n)]


def mat_mul(A, B):
    return [[sum((A[i][k] * B[k][j] for k in range(len(B))), ZERO) for j in range(len(B[0]))] for i in range(len(A))]


def mat_vec(A, x):
    return [sum((A[i][k] * x[k] for k in range(len(x))), ZERO) for i in range(len(A))]


def transpose(A):
    return [list(r) for r in zip(*A)]


def sym_inertia(A):
    """exact (pos, neg, zero) of a symmetric rational matrix by symmetric Gaussian elimination
    with diagonal pivots (Bunch-Kaufman free: falls back to congruence by adding rows)."""
    n = len(A)
    M = [list(r) for r in A]
    for i in range(n):
        for j in range(n):
            require(M[i][j] == M[j][i], "inertia needs a symmetric matrix")
    pos = neg = 0
    idx = list(range(n))
    size = n
    while size > 0:
        # choose a nonzero diagonal pivot
        p = None
        for i in range(size):
            if M[i][i] != 0:
                p = i
                break
        if p is None:
            # all diagonal zero: find a nonzero off-diagonal, add row/col j to row/col i
            pair = None
            for i in range(size):
                for j in range(i + 1, size):
                    if M[i][j] != 0:
                        pair = (i, j)
                        break
                if pair:
                    break
            if pair is None:
                break  # zero block remains
            i, j = pair
            for k in range(size):
                M[i][k] += M[j][k]
            for k in range(size):
                M[k][i] += M[k][j]
            continue
        M[0], M[p] = M[p], M[0]
        for r in M:
            r[0], r[p] = r[p], r[0]
        pv = M[0][0]
        if pv > 0:
            pos += 1
        else:
            neg += 1
        for r in range(1, size):
            if M[r][0] != 0:
                f = M[r][0] / pv
                for k in range(size):
                    M[r][k] -= f * M[0][k]
        for r in range(1, size):
            M[r][0] = ZERO
        for k in range(1, size):
            M[0][k] = ZERO
        M = [row[1:] for row in M[1:]]
        size -= 1
    zero = n - pos - neg
    return (pos, neg, zero)


# ------------------------------------------------ shortest paths (clean room)
def dijkstra_to_goals(n, goals, edges):
    """distance to the goal set over directed edges (u, v, w), w >= 0, exact.
    Returns (dist list with None = unreachable, parent edge index list, finalize order)."""
    rev = [[] for _ in range(n)]
    for idx, (u, v, w) in enumerate(edges):
        require(w >= 0, "negative edge")
        rev[v].append((u, w, idx))
    dist = [None] * n
    parent = [-1] * n
    heap = []
    for g in sorted(set(goals)):
        dist[g] = Fraction(0)
        heapq.heappush(heap, (Fraction(0), g))
    order = []
    done = [False] * n
    while heap:
        d, v = heapq.heappop(heap)
        if done[v]:
            continue
        done[v] = True
        order.append(v)
        for u, w, idx in rev[v]:
            nd = d + w
            if dist[u] is None or nd < dist[u]:
                dist[u] = nd
                parent[u] = idx
                heapq.heappush(heap, (nd, u))
    return dist, parent, order


def bellman_ford_to_goals(n, goals, edges):
    """independent: plain Bellman-Ford relaxation to a fixpoint (no heap)."""
    dist = [None] * n
    for g in goals:
        dist[g] = Fraction(0)
    for _ in range(n + 1):
        changed = False
        for u, v, w in edges:
            if dist[v] is not None and (dist[u] is None or dist[v] + w < dist[u]):
                dist[u] = dist[v] + w
                changed = True
        if not changed:
            return dist
    raise AuditError("negative cycle")


# ---------------------------------------------------------------- the 32-state system
def build_system():
    """32 states (x,y,m), x,y in 0..3, m in {0,1}; goal (0,0,0); index = 8x + 2y + m.
    Rebuilt from the docstring of the ledger's script (symmetric variant)."""
    states = [(x, y, m) for x in range(4) for y in range(4) for m in (0, 1)]
    idx = {s: i for i, s in enumerate(states)}
    edges = []
    for (x, y, m) in states:
        u = idx[(x, y, m)]
        edges.append((u, idx[(x, y, 1 - m)], Fraction(1)))
        if m == 0:
            if x > 0:
                edges.append((u, idx[(x - 1, y, 0)], Fraction(1)))
            if x < 3:
                edges.append((u, idx[(x + 1, y, 0)], Fraction(1)))
            if x > 0 and y > 0:
                edges.append((u, idx[(x - 1, y - 1, 0)], Fraction(2)))
        else:
            if y > 0:
                edges.append((u, idx[(x, y - 1, 1)], Fraction(1)))
            if y < 3:
                edges.append((u, idx[(x, y + 1, 1)], Fraction(1)))
    pi_x = [2 * x + m for (x, y, m) in states]
    pi_y = [2 * y + m for (x, y, m) in states]
    pi_imb = [2 * (1 if y > x else 0) + m for (x, y, m) in states]
    return {"states": states, "n": len(states), "goals": [idx[(0, 0, 0)]], "edges": edges,
            "pis": [("pi_x", pi_x), ("pi_y", pi_y), ("pi_imbalance", pi_imb)]}


def validate_quotient(pi, n):
    require(len(pi) == n, "quotient map length")
    for c in pi:
        require(isinstance(c, int) and not isinstance(c, bool) and c >= 0, "quotient label")
    labels = sorted(set(pi))
    require(labels == list(range(len(labels))), "quotient map not onto 0..k-1")
    return len(labels)


def quotient_edges(edges, pi):
    best = {}
    for (u, v, w) in edges:
        a, b = pi[u], pi[v]
        if a == b:
            continue
        if (a, b) not in best or w < best[(a, b)]:
            best[(a, b)] = w
    return [(a, b, w) for (a, b), w in sorted(best.items())]


def peel_layer(n, goals, cur_edges, pi, mu=None):
    """one layer of the tower, clean room.  Returns a dict with exact objects."""
    k = validate_quotient(pi, n)
    qgoals = sorted({pi[g] for g in goals})
    qe = quotient_edges(cur_edges, pi)
    dist, parent, order = dijkstra_to_goals(k, qgoals, [(a, b, w) for (a, b, w) in qe])
    require(all(d is not None for d in dist), "unreachable quotient vertex")
    fiber = [0] * k
    for s in range(n):
        fiber[pi[s]] += 1
    mu_one = [ONE] * k
    mu_fib = [Fraction(c) for c in fiber]

    def dual_flow(weights):
        flow_at = [Fraction(w) for w in weights]
        for g in qgoals:
            flow_at[g] = ZERO
        y = [ZERO] * len(qe)
        for v in reversed(order):
            if v in qgoals:
                continue
            e = parent[v]
            y[e] += flow_at[v]
            flow_at[qe[e][1]] += flow_at[v]
        return y

    res = {"k": k, "qgoals": qgoals, "qedges": qe, "h": dist, "fiber": fiber, "parent": parent}
    for tag, mu_ in (("one", mu_one), ("fiber", mu_fib)):
        y = dual_flow(mu_)
        res["dual_y_" + tag] = y
        res["primal_" + tag] = sum((mu_[a] * dist[a] for a in range(k) if a not in qgoals), ZERO)
        res["dual_" + tag] = sum((qe[i][2] * y[i] for i in range(len(qe))), ZERO)
    red = []
    for (u, v, w) in cur_edges:
        c = w + dist[pi[v]] - dist[pi[u]]
        require(c >= 0, "negative reduced cost")
        red.append((u, v, c))
    res["reduced_edges"] = red
    res["sum_H_layer"] = sum((dist[pi[s]] for s in range(n)), ZERO)
    return res


def build_tower(sysd=None):
    sysd = sysd or build_system()
    n, goals, edges = sysd["n"], sysd["goals"], sysd["edges"]
    cur = list(edges)
    H = [ZERO] * n
    layers = []
    for name, pi in sysd["pis"]:
        L = peel_layer(n, goals, cur, pi)
        L["name"] = name
        L["pi"] = pi
        L["input_edges"] = cur
        for s in range(n):
            H[s] += L["h"][pi[s]]
        L["sum_H_after"] = sum(H, ZERO)
        layers.append(L)
        cur = L["reduced_edges"]
    dstar, _, _ = dijkstra_to_goals(n, goals, edges)
    return {"sys": sysd, "layers": layers, "H": H, "dstar": dstar, "final_edges": cur}


# ------------------------------------------------------- Cole-Hopf matrices
def cole_hopf(n, edges):
    """K_{uv} = sum over edges q^{c(e)} as polynomials in q; costs must be integers >= 0."""
    K = [[() for _ in range(n)] for _ in range(n)]
    for (u, v, w) in edges:
        w = fr(w)
        require(w.denominator == 1 and w >= 0, "Cole-Hopf needs integer cost >= 0")
        K[u][v] = padd(K[u][v], pmono(1, int(w)))
    return K


def witness_graphs():
    """the 4- and 5-state graphs of the ledger's Maslov-Doob section (clean-room copy of the cost tables)."""
    acc = {"n": 4, "goals": [0, 3], "pi": [0, 1, 1, 0],
           "edges": [(0, 0, 1), (3, 3, 1), (1, 0, 1), (2, 0, 2), (2, 3, 2)]}
    boltz = {"n": 5, "goals": [0, 3], "pi": [0, 1, 1, 0, 2],
             "edges": [(0, 0, 1), (3, 3, 1), (4, 0, 3), (1, 0, 1), (1, 4, 1), (2, 0, 2), (2, 3, 2), (2, 4, 1)]}
    rigid = {"n": 4, "goals": [0, 3], "pi": [0, 1, 1, 0],
             "edges": [(0, 0, 1), (3, 3, 1), (1, 0, 1), (1, 3, 2), (2, 0, 2), (2, 3, 1)]}
    out = {}
    for name, g in (("acc4", acc), ("boltz5", boltz), ("rigid4", rigid)):
        g = dict(g)
        g["edges"] = [(u, v, Fraction(w)) for (u, v, w) in g["edges"]]
        out[name] = g
    return out


def kmatrix_json(K):
    n = len(K)
    return [{"i": i, "j": j, "poly": pjson(K[i][j])} for i in range(n) for j in range(n) if K[i][j]]
