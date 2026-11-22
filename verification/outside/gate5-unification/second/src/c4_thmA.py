# Independent exact check of "Theorem A" (algebraic Schur complement over Q[q] vs tropical elimination).
# Standard library only, integer arithmetic. No bare assert. Deterministic (seeded random.Random).
import sys, random

INF = 10 ** 9
FAILS = []           # unexpected results
def need(cond, msg):
    if not cond:
        FAILS.append(msg)

# ---------------- polynomial helpers (ascending integer coefficient lists) ----------------
def pstrip(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p
def padd(p, q):
    n = max(len(p), len(q))
    return pstrip([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)])
def pneg(p):
    return [-c for c in p]
def pmul(p, q, N=None):
    if not p or not q:
        return []
    L = len(p) + len(q) - 1
    if N is not None and L > N:
        L = N
    r = [0] * L
    for i, a in enumerate(p):
        if a == 0 or i >= L:
            continue
        for j, b in enumerate(q):
            if i + j >= L:
                break
            r[i + j] += a * b
    return pstrip(r)
def pval(p):
    for i, c in enumerate(p):
        if c:
            return i
    return INF
def plead(p):
    for c in p:
        if c:
            return c
    return 0
def pdeg(p):
    return len(p) - 1          # -1 for the zero polynomial
def pcoef(p, k):
    return p[k] if 0 <= k < len(p) else 0

def pdet(M):
    n = len(M)
    if n == 0:
        return [1]
    if n == 1:
        return M[0][0]
    tot = []
    for j in range(n):
        if not M[0][j]:
            continue
        minor = [[M[i][k] for k in range(n) if k != j] for i in range(1, n)]
        t = pmul(M[0][j], pdet(minor))
        tot = padd(tot, t if j % 2 == 0 else pneg(t))
    return tot
def padj(M):
    """adj(M)[a][b] = cofactor C_{b,a}"""
    n = len(M)
    if n == 1:
        return [[[1]]]
    A = [[[] for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            minor = [[M[i][k] for k in range(n) if k != c] for i in range(n) if i != r]
            d = pdet(minor)
            A[c][r] = d if (r + c) % 2 == 0 else pneg(d)
    return A

# ---------------- the objects ----------------
def maxdeg(K):
    return max([pdeg(K[i][j]) for i in range(len(K)) for j in range(len(K))] + [0])

def exact_P_Q(K, A, B):
    """S_ij = P_ij / Q, Q = det(I-K_BB); P_ij = K_ij Q + K_iB adj(I-K_BB) K_Bj  (exact polynomials)."""
    M = [[padd([1] if b == c else [], pneg(K[b][c])) for c in B] for b in B]
    Q = pdet(M)
    adj = padj(M)
    P = {}
    for i in A:
        for j in A:
            acc = pmul(K[i][j], Q)
            for x, b in enumerate(B):
                for y, c in enumerate(B):
                    if K[i][b] and adj[x][y] and K[c][j]:
                        acc = padd(acc, pmul(pmul(K[i][b], adj[x][y]), K[c][j]))
            P[(i, j)] = acc
    return P, Q

def series_S(K, A, B, N):
    """S = K_AA + sum_{m>=0} K_AB K_BB^m K_BA, truncated mod q^N (Neumann series, valid when val(K_BB)>=1)."""
    nb = len(B)
    cur = [[K[b][a][:N] for a in A] for b in B]       # K_BA
    cur = [[pstrip(x) for x in row] for row in cur]
    S = {}
    for i in A:
        for j in A:
            S[(i, j)] = pstrip(K[i][j][:N])
    for m in range(N + 2):
        if all(not x for row in cur for x in row):
            break
        for ia, i in enumerate(A):
            for ja, j in enumerate(A):
                acc = S[(i, j)]
                for x, b in enumerate(B):
                    if K[i][b] and cur[x][ja]:
                        acc = padd(acc, pmul(K[i][b], cur[x][ja], N))
                S[(i, j)] = pstrip(acc[:N])
        nxt = []
        for x, b in enumerate(B):
            row = []
            for ja in range(len(A)):
                acc = []
                for y, c in enumerate(B):
                    if K[b][c] and cur[y][ja]:
                        acc = padd(acc, pmul(K[b][c], cur[y][ja], N))
                row.append(pstrip(acc[:N]))
            nxt.append(row)
        cur = nxt
    return S

def tropical(K, A, B):
    n = len(K)
    t = [[pval(K[i][j]) for j in range(n)] for i in range(n)]
    # star over B by Bellman-Ford style relaxation (nonneg weights): star = min over walks (incl. empty walk, diag 0)
    st = {(b, c): (0 if b == c else INF) for b in B for c in B}
    for _ in range(len(B) + 1):
        ch = False
        for b in B:
            for c in B:
                for d in B:
                    if st[(b, d)] < INF and t[d][c] < INF and st[(b, d)] + t[d][c] < st[(b, c)]:
                        st[(b, c)] = st[(b, d)] + t[d][c]; ch = True
        if not ch:
            break
    T = {}
    for i in A:
        for j in A:
            best = t[i][j]
            for b in B:
                if t[i][b] >= INF:
                    continue
                for c in B:
                    if st[(b, c)] >= INF or t[c][j] >= INF:
                        continue
                    best = min(best, t[i][b] + st[(b, c)] + t[c][j])
            T[(i, j)] = best
    return t, st, T

def walks_L(K, A, B, t, i, j, Tij, absval=False, cap=2_000_000):
    """enumerate every walk i -> b1 -> ... -> bk -> j (k>=0 direct term counts as k=0, b in B, repeats allowed)
    whose total valuation equals Tij; return (sum of products of leading coefficients, number of such walks,
    number of partial walks explored). Terminates because every B->B edge has valuation >= 1 (pivot regularity)."""
    f = (lambda c: abs(c)) if absval else (lambda c: c)
    lead = lambda a, b: f(plead(K[a][b]))
    total = 0
    nw = 0
    if t[i][j] == Tij:
        total += lead(i, j); nw += 1
    explored = [0]
    stack = []
    for b in B:
        if t[i][b] < INF and t[i][b] <= Tij:
            stack.append((b, t[i][b], lead(i, b)))
    while stack:
        b, v, pr = stack.pop()
        explored[0] += 1
        if explored[0] > cap:
            return None, None, explored[0]
        if t[b][j] < INF and v + t[b][j] == Tij:
            total += pr * lead(b, j); nw += 1
        for c in B:
            w = t[b][c]
            if w < INF and v + w <= Tij:
                if w == 0:
                    return None, None, -1          # infinite family (only without pivot regularity)
                stack.append((c, v + w, pr * lead(b, c)))
    return total, nw, explored[0]

# ---------------- generators ----------------
def rpoly(r, vlo, D, signed=True, density=0.6):
    """random polynomial with valuation >= vlo, degree <= D (may be zero)"""
    c = [0] * (D + 1)
    for e in range(vlo, D + 1):
        if r.random() < density:
            x = r.randint(1, 3)
            c[e] = -x if (signed and r.random() < 0.5) else x
    return pstrip(c)

def gen_K(r, n, kb, D, regular=True, pos_lead=False, signed=True, pab=0.7, bb_val=1):
    idx = list(range(n)); r.shuffle(idx)
    B = sorted(idx[:kb]); A = sorted(idx[kb:]); Bs = set(B)
    K = [[[] for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if r.random() < pab:
                if i in Bs and j in Bs:
                    K[i][j] = rpoly(r, bb_val if regular else 0, max(D, bb_val if regular else 0), signed)
                else:
                    K[i][j] = rpoly(r, r.choice([0, 0, 1, 2]), D, signed)
    if pos_lead:
        for i in range(n):
            for j in range(n):
                if K[i][j] and plead(K[i][j]) < 0:
                    K[i][j] = pneg(K[i][j])      # whole polynomial flipped: lead > 0, tail random sign preserved relative
                    # re-randomise the tail signs so the tail is not forced
                    p = list(K[i][j]); v = pval(p)
                    for e in range(v + 1, len(p)):
                        if p[e] and r.random() < 0.5:
                            p[e] = -p[e]
                    K[i][j] = pstrip(p)
    return K, A, B

def force_cancel(r, K, A, B, npairs, gmax):
    """overwrite K_ij (i,j in A) by minus the truncation (mod q^g) of K_iB (I-K_BB)^-1 K_Bj, so L_ij = 0 on purpose
    (and S_ij has valuation >= g)."""
    pairs = [(i, j) for i in A for j in A]
    r.shuffle(pairs)
    g_list = []
    for (i, j) in pairs[:npairs]:
        g = r.randint(1, gmax)
        N = g
        Ksub = [row[:] for row in K]
        for b in B:
            Ksub[i][j] = []
        S = series_S(Ksub, [i, j] if i != j else [i], B, N)
        s0 = S[(i, j)]
        # series_S includes K_ij which we blanked, so s0 is the pure walk part
        K[i][j] = pneg(s0)
        g_list.append(g)
    return g_list

# ---------------- the checks ----------------
class Tally:
    def __init__(self):
        self.d = {}
    def add(self, k, n=1):
        self.d[k] = self.d.get(k, 0) + n
    def get(self, k):
        return self.d.get(k, 0)

def check_instance(K, A, B, tl, tag, controls, regular=True):
    n = len(K)
    D = maxdeg(K)
    nb = len(B)
    bound_val = (nb + 1) * D                       # claimed: val(S_ij) <= (|B|+1) D whenever S_ij != 0
    P, Q = exact_P_Q(K, A, B)
    need(Q and Q[0] == 1, "Q(0) != 1 in regular instance %s" % tag)
    N = bound_val + 2
    S = series_S(K, A, B, N)
    t, st, T = tropical(K, A, B)
    for i in A:
        for j in A:
            tl.add(tag + ":entries")
            Pij = P[(i, j)]
            # two ways to the valuation of S_ij: truncated Neumann series vs exact P (Q unit)
            vs = pval(S[(i, j)])
            vp = pval(Pij)
            if vs != vp and not (vs >= INF and vp >= N):
                need(False, "series/P valuation mismatch %s (%d,%d) %s %s" % (tag, i, j, vs, vp))
            val = vp
            Tij = T[(i, j)]
            if Tij >= INF:
                ok = (val >= INF)
                tl.add(tag + ":T_inf")
                if not ok:
                    need(False, "T infinite but S nonzero %s" % tag)
                continue
            L, nw, ex = walks_L(K, A, B, t, i, j, Tij)
            need(L is not None, "walk enumeration did not terminate in regular instance")
            ls = pcoef(S[(i, j)], Tij)       # coefficient of q^T in the series
            ls2 = pcoef(Pij, Tij)            # coefficient of q^T in P (Q(0)=1, val(S)>=T so same coefficient)
            lower = val >= Tij
            ident = (ls == L) and (ls2 == L)
            iff = ((val == Tij) == (L != 0))
            if not lower: need(False, "LOWER BOUND VIOLATED %s (%d,%d)" % (tag, i, j))
            if not ident: need(False, "LEAD IDENTITY VIOLATED %s (%d,%d) %s %s %s" % (tag, i, j, ls, ls2, L))
            if not iff: need(False, "IFF VIOLATED %s (%d,%d)" % (tag, i, j))
            tl.add("lower_ok", lower); tl.add("ident_ok", ident); tl.add("iff_ok", iff)
            if L != 0:
                tl.add("class_eq_Lnz")
            elif val >= INF:
                tl.add("class_L0_S0")
            else:
                gap = val - Tij
                tl.add("class_L0_Snz")
                tl.add("gap_ok", (1 <= gap <= bound_val - Tij))
                if not (1 <= gap <= bound_val - Tij):
                    need(False, "GAP BOUND VIOLATED %s (%d,%d) gap=%d bound=%d" % (tag, i, j, gap, bound_val - Tij))
                tl.add("gap_sum", gap)
                tl.add("gap_hist_%d" % min(gap, 9))
                if gap == bound_val - Tij:
                    tl.add("gap_tight")
                tl.add("gap_slack_min", 0)
            if val < INF:
                need(val <= bound_val, "val(S) > (|B|+1)D %s" % tag)
                tl.add("val_le_bound", val <= bound_val)
                tl.add("val_bound_tight", val == bound_val)
            # --- wrong versions (controls): each must be falsified somewhere ---
            ctl = controls
            if val == Tij: ctl["W1 val>=T+1"] += 1            # strict lower bound is wrong
            if val > Tij: ctl["W2 val<=T"] += 1               # reversed bound is wrong
            Lab, _, _ = walks_L(K, A, B, t, i, j, Tij, absval=True)
            if (val == Tij) != (Lab != 0): ctl["W3 sign-blind iff"] += 1
            if ls != L + 1: pass
            ctl["W5 lead = L+1"] += (1 if ls != L + 1 else 0)
            if val < INF and val - Tij > bound_val - Tij - 1: ctl["W4 gap<=(|B|+1)D-T-1"] += 1
            if val < INF and val - Tij > nb * D - Tij: ctl["W4b gap<=|B|D-T"] += 1
            tw = t[i][j]
            for b in B:
                if t[i][b] < INF and t[b][j] < INF:
                    tw = min(tw, t[i][b] + t[b][j])
            if val < tw: ctl["W6 single-hop T (no Kleene star)"] += 1
    return

def newctl():
    return {k: 0 for k in ["W1 val>=T+1", "W2 val<=T", "W3 sign-blind iff", "W5 lead = L+1",
                           "W4 gap<=(|B|+1)D-T-1", "W4b gap<=|B|D-T", "W6 single-hop T (no Kleene star)"]}

def main():
    P = print
    tl = Tally(); ctl = newctl()
    P("== Theorem A: exact checks (integers only) ==")
    # --- A1: random regular, mixed signs
    ninst = 0
    for seed in range(3000):
        r = random.Random(100000 + seed)
        n = r.choice([3, 4, 4, 5, 5, 6])
        kb = r.randint(1, n - 1)
        D = r.choice([1, 2, 2, 3, 4])
        K, A, B = gen_K(r, n, kb, D)
        check_instance(K, A, B, tl, "rand", ctl); ninst += 1
    P("A1 random mixed-sign regular instances: %d  (n in 3..6, |B| in 1..n-1, D in 1..4)" % ninst)
    # --- A2: forced cancellation
    ninst2 = 0
    for seed in range(2500):
        r = random.Random(200000 + seed)
        n = r.choice([3, 4, 4, 5, 5, 6])
        kb = r.randint(1, n - 1)
        D = r.choice([1, 2, 2, 3])
        K, A, B = gen_K(r, n, kb, D)
        force_cancel(r, K, A, B, r.randint(1, 3), r.choice([2, 3, 4, 6, 8]))
        check_instance(K, A, B, tl, "forced", ctl); ninst2 += 1
    P("A2 forced-cancellation instances: %d" % ninst2)
    # --- A2b: K_BB = 0 exact annihilation (S_ij = 0 on purpose)
    ninst2b = 0
    for seed in range(600):
        r = random.Random(250000 + seed)
        n = r.choice([3, 4, 5])
        kb = r.randint(1, n - 1)
        K, A, B = gen_K(r, n, kb, 2)
        for b in B:
            for c in B:
                K[b][c] = []
        i = r.choice(A); j = r.choice(A)
        acc = []
        for b in B:
            acc = padd(acc, pmul(K[i][b], K[b][j]))
        K[i][j] = pneg(acc)
        check_instance(K, A, B, tl, "annih", ctl); ninst2b += 1
    P("A2b exact annihilation (K_BB=0, K_ij = -K_iB K_Bj): %d" % ninst2b)
    # --- A3: positive leading coefficients, random tails
    ninst3 = 0
    pos_bad = 0
    pos_entries = 0
    for seed in range(1500):
        r = random.Random(300000 + seed)
        n = r.choice([3, 4, 5, 6])
        kb = r.randint(1, n - 1)
        D = r.choice([1, 2, 3, 4])
        K, A, B = gen_K(r, n, kb, D, pos_lead=True)
        tl2 = Tally(); c2 = newctl()
        check_instance(K, A, B, tl2, "pos", c2); ninst3 += 1
        pos_entries += tl2.get("pos:entries")
        pos_bad += tl2.get("class_L0_Snz") + tl2.get("class_L0_S0")
        for k, v in tl2.d.items():
            if k != "pos:entries":
                tl.add("pos_" + k, v)
    P("A3 positive-leading-coefficient instances: %d, entries %d, entries with L=0 (must be 0): %d" % (ninst3, pos_entries, pos_bad))
    need(pos_bad == 0, "positive-lead instance with L=0")
    # --- summary of A1..A3
    P("TOTAL instances (A1+A2+A2b+A3): %d" % (ninst + ninst2 + ninst2b + ninst3))
    for k in ["rand:entries", "forced:entries", "annih:entries", "pos:entries"]:
        P("  %s %d" % (k, tl.get(k)))
    P("entry checks passed: lower %d, lead-identity %d, iff %d (violations are listed under FAILURES)" % (tl.get("lower_ok"), tl.get("ident_ok"), tl.get("iff_ok")))
    P("entry classes: S has val=T with L!=0: %d;  L=0 and S!=0: %d;  L=0 and S=0: %d;  T=inf: %d" % (
        tl.get("class_eq_Lnz"), tl.get("class_L0_Snz"), tl.get("class_L0_S0"),
        sum(tl.get(k + ":T_inf") for k in ["rand", "forced", "annih", "pos"])))
    P("gap bound 1 <= gap <= (|B|+1)D - T held on %d of %d L=0,S!=0 entries; tight (gap==bound) on %d" % (tl.get("gap_ok"), tl.get("class_L0_Snz"), tl.get("gap_tight")))
    P("val(S)<=(|B|+1)D held on %d entries with S!=0; val==(|B|+1)D exactly on %d" % (tl.get("val_le_bound"), tl.get("val_bound_tight")))
    P("gap histogram (1..8, 9+): " + " ".join("%d" % tl.get("gap_hist_%d" % g) for g in range(1, 10)))

    # --- must-fail controls
    P("== must-fail controls: number of entries falsifying each deliberately wrong statement (all must be > 0) ==")
    for k in sorted(ctl):
        P("  %-36s falsified on %d entries" % (k, ctl[k]))
        if ctl[k] == 0:
            P("    NOTE: control not caught by sample")
    required = ["W1 val>=T+1", "W2 val<=T", "W3 sign-blind iff", "W5 lead = L+1", "W6 single-hop T (no Kleene star)", "W4b gap<=|B|D-T"]
    for k in required:
        need(ctl[k] > 0, "control not caught: " + k)

    # --- A4: tightness search for the gap bound, D=1 small
    best = None
    tight_found = 0
    for seed in range(20000):
        r = random.Random(400000 + seed)
        n = r.choice([3, 4]); kb = r.randint(1, n - 1)
        K, A, B = gen_K(r, n, kb, 1, pab=0.8)
        D = maxdeg(K)
        Pd, Q = exact_P_Q(K, A, B)
        t, st, T = tropical(K, A, B)
        for i in A:
            for j in A:
                if Pd[(i, j)] and T[(i, j)] < INF and pval(Pd[(i, j)]) == (len(B) + 1) * D:
                    tight_found += 1
    P("A4 tightness search D=1 (20000 instances): entries with val(S) == (|B|+1)D: %d" % tight_found)
    # --- explicit hand-built tight example |B|=1, D=1: K_02=q? val(S)=2?
    # A={0,1}, B={2}; K_BB = 0; K_01 = -1... val(S_01) = 0 only. Try K_01=0,K_02=1,K_21=1 -> S=1 (val 0). Tight needs val=(|B|+1)D=2:
    # K_02 = q, K_21 = q, K_01 = 0 gives S_01=q^2, val 2 = (|B|+1)D, but then L!=0 and gap is 0 (T=2).  For L=0 and val=bound see below.
    r = [[[], [], [0, 1]], [[], [], []], [[], [0, 1], []]]
    # K_00 etc zero. Check gap-class tightness by brute force below.
    # --- A5: brute-force exhaustive tiny family for the gap bound: |A|=2,|B|=1, D=2, K_BB in {0, q, -q, q^2...}
    import itertools
    polys2 = [[]] + [[a, b, c] for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1) if (a, b, c) != (0, 0, 0)]
    polys2 = [pstrip(p) for p in polys2]
    seen = set(); P2 = []
    for p in polys2:
        k = tuple(p)
        if k not in seen:
            seen.add(k); P2.append(p)
    # A={0,1}? need only K_01, K_0b, K_b1, K_bb (the rest do not enter S_01)
    tl5 = Tally(); maxgap_slack = None; cnt = 0
    for k01 in P2:
        for k0b in P2:
            for kb1 in P2:
                for kbb in P2:
                    if kbb and pval(kbb) < 1:
                        continue
                    K = [[[], k01, k0b], [[], [], []], [[], kb1, kbb]]
                    # indices: 0->0, 1->1 (A) , 2 -> B ; K[0][1]=k01, K[0][2]=k0b, K[2][1]=kb1, K[2][2]=kbb
                    D = max(pdeg(x) for x in (k01, k0b, kb1, kbb))
                    D = max(D, 0)
                    Pd, Q = exact_P_Q(K, [0, 1], [2])
                    t, st, T = tropical(K, [0, 1], [2])
                    p = Pd[(0, 1)]
                    cnt += 1
                    if p and T[(0, 1)] < INF:
                        v = pval(p)
                        bnd = 2 * D
                        need(v <= bnd, "A5 val bound violated")
                        L, nw, ex = walks_L(K, [0, 1], [2], t, 0, 1, T[(0, 1)])
                        need(v >= T[(0, 1)], "A5 lower bound violated")
                        need((v == T[(0, 1)]) == (L != 0), "A5 iff violated")
                        need(pcoef(p, T[(0, 1)]) == L, "A5 lead identity violated")
                        if L == 0:
                            tl5.add("gapcases")
                            if v == bnd: tl5.add("gap_tight")
                        if v == bnd and D >= 1: tl5.add("val_tight")
    P("A5 exhaustive |A|=2,|B|=1, entries in span{1,q,q^2} with coefficients in {-1,0,1}: %d systems; L=0&S!=0 cases %d; of these val(S)==2D (bound attained): %d; any case with val(S)==2D: %d" % (cnt, tl5.get("gapcases"), tl5.get("gap_tight"), tl5.get("val_tight")))

    # --- A6: without pivot regularity
    P("== without pivot regularity ==")
    # their witness
    K = [[[], [], [0, 1]], [[], [], []], [[], [0, 1], [1, -1]]]    # K_02=q, K_21=q, K_22=1-q
    Pd, Q = exact_P_Q(K, [0, 1], [2]); t, st, T = tropical(K, [0, 1], [2])
    v = pval(Pd[(0, 1)]) - pval(Q)
    P("witness K_22=1-q, K_02=K_21=q: Q=%s, P_01=%s, val(S_01)=val(P)-val(Q)=%d, T_01=%d, gap=%d" % (Q, Pd[(0, 1)], v, T[(0, 1)], v - T[(0, 1)]))
    need(v == 1 and T[(0, 1)] == 2, "witness reproduction")
    # random search: val(K_BB) may be 0.  Classify by Q(0).
    stat = Tally(); examples = []
    for seed in range(12000):
        r = random.Random(500000 + seed)
        n = r.choice([3, 4, 5]); kb = r.randint(1, 3)
        if kb >= n: kb = n - 1
        K, A, B = gen_K(r, n, kb, r.choice([1, 2]), regular=False, pab=0.75)
        Pd, Q = exact_P_Q(K, A, B)
        if not Q:
            stat.add("Q_zero"); continue
        vq = pval(Q)
        t, st, T = tropical(K, A, B)
        for i in A:
            for j in A:
                Tij = T[(i, j)]
                p = Pd[(i, j)]
                if not p or Tij >= INF:
                    continue
                v = pval(p) - vq
                key = "Q_unit" if vq == 0 else "Q_nonunit"
                stat.add(key + ":entries")
                if v < Tij:
                    stat.add(key + ":lower_violations")
                    if len(examples) < 3 and key == "Q_nonunit":
                        examples.append((seed, n, A, B, i, j, v, Tij, vq))
    P("random K, val(K_BB) allowed 0: entries with Q(0)!=0 (unit): %d, lower-bound violations: %d" % (stat.get("Q_unit:entries"), stat.get("Q_unit:lower_violations")))
    P("   entries with Q(0)=0 (non-unit): %d, lower-bound violations: %d; systems with Q==0 skipped: %d" % (stat.get("Q_nonunit:entries"), stat.get("Q_nonunit:lower_violations"), stat.get("Q_zero")))
    for e in examples:
        P("   example violation (seed,n,A,B,i,j,val(S),T,val(Q)): %s" % (e,))
    need(stat.get("Q_unit:lower_violations") == 0, "lower bound failed with Q(0) != 0 (new finding)")
    need(stat.get("Q_nonunit:lower_violations") > 0, "no failure found without regularity")
    # K_BB with val 0 but unit determinant: lower bound holds -> pivot regularity is sufficient, not necessary
    K = [[[], [], [0, 1], []], [[], [], [], []], [[], [], [], [1]], [[], [0, 1], [2], []]]
    # A={0,1}, B={2,3}: K_02=q, K_23? set K_BB=[[0,0? ]] build explicitly below instead
    K = [[[] for _ in range(4)] for _ in range(4)]
    K[0][2] = [0, 1]; K[3][1] = [0, 1]; K[2][3] = [1]; K[3][2] = [2]    # K_BB=[[0,1],[2,0]], det(I-K_BB)=-1, val(K_BB)=0
    Pd, Q = exact_P_Q(K, [0, 1], [2, 3]); t, st, T = tropical(K, [0, 1], [2, 3])
    P("val(K_BB)=0 but det(I-K_BB)=%s unit: S_01 has val %d, T_01=%d (bound holds; 'val(K_BB)>=1' is sufficient, not necessary; the L-walk set is infinite here)" % (Q, pval(Pd[(0, 1)]) - pval(Q), T[(0, 1)]))

    if FAILS:
        P("FAILURES: %d" % len(FAILS))
        for f in FAILS[:20]:
            P("  " + f)
        sys.exit(1)
    P("ALL CHECKS PASSED, ALL CONTROLS CAUGHT")
    sys.exit(0)

main()
