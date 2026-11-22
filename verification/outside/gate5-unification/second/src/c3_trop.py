import os, sys, random
here = os.path.dirname(os.path.abspath(__file__))
OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

INF = 10 ** 9

# ---- polynomials: ascending integer coefficient lists, trailing zeros stripped
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
    if N is not None:
        L = min(L, N)
    r = [0] * L
    for i, a in enumerate(p):
        if a == 0 or i >= L:
            continue
        for j, b in enumerate(q):
            if i + j >= L:
                break
            if b:
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
    return len(p) - 1

# exact determinant / adjugate of small polynomial matrices
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
        term = pmul(M[0][j], pdet(minor))
        tot = padd(tot, term if j % 2 == 0 else pneg(term))
    return tot

def padj(M):
    n = len(M)
    A = [[[] for _ in range(n)] for _ in range(n)]
    if n == 1:
        A[0][0] = [1]
        return A
    for i in range(n):
        for j in range(n):
            minor = [[M[r][c] for c in range(n) if c != j] for r in range(n) if r != i]
            d = pdet(minor)
            A[j][i] = d if (i + j) % 2 == 0 else pneg(d)
    return A

# ---- instance generation
def rand_poly(r, vlo, vhi, dmax, signed):
    """polynomial with valuation v in [vlo,vhi]; coefficients up to degree dmax"""
    v = r.randint(vlo, vhi)
    coefs = [0] * (dmax + 1)
    for e in range(v, dmax + 1):
        if e == v or r.random() < 0.5:
            c = r.randint(1, 3)
            if signed and r.random() < 0.5:
                c = -c
            coefs[e] = c
    return pstrip(coefs)

def gen(seed, n, mode):
    r = random.Random(seed)
    kb = r.randint(1, n - 2)
    idx = list(range(n))
    r.shuffle(idx)
    B = sorted(idx[:kb])
    A = sorted(idx[kb:])
    Bs = set(B)
    signed = (mode != "pos")
    K = [[[] for _ in range(n)] for _ in range(n)]
    dmax = 3
    for i in range(n):
        for j in range(n):
            if r.random() < 0.65:
                if i in Bs and j in Bs:
                    K[i][j] = rand_poly(r, 1, 2, dmax, signed)
                elif i in Bs or j in Bs:
                    K[i][j] = rand_poly(r, 0, 1, dmax, signed)
                else:
                    K[i][j] = rand_poly(r, 0, 2, dmax, signed)
    if mode == "tie":
        for _ in range(r.randint(1, 4)):
            b = r.choice(B)
            i = r.choice(A)
            j = r.choice(A)
            K[i][b] = rand_poly(r, 0, 1, 2, True) or [1]
            K[b][j] = rand_poly(r, 0, 1, 2, True) or [1]
            w = pval(K[i][b]) + pval(K[b][j])
            lc = -plead(K[i][b]) * plead(K[b][j])
            tail = rand_poly(r, w + 1, w + 2, w + 2, True) if r.random() < 0.7 else []
            K[i][j] = padd([0] * w + [lc], tail)
    if mode == "annih":
        for b in B:
            for b2 in B:
                K[b][b2] = []
        pairs = [(i, j) for i in A for j in A]
        r.shuffle(pairs)
        for (i, j) in pairs[: r.randint(1, 3)]:
            acc = []
            for b in B:
                if not K[i][b]:
                    K[i][b] = rand_poly(r, 0, 1, 2, True)
                if not K[b][j]:
                    K[b][j] = rand_poly(r, 0, 1, 2, True)
                acc = padd(acc, pmul(K[i][b], K[b][j]))
            K[i][j] = pneg(acc)
    for b in B:
        for b2 in B:
            if K[b][b2] and K[b][b2][0] != 0:
                raise ValueError("K_BB constant term nonzero")
    return K, A, B

# ---- exact side: truncated series
def series_S(K, A, B, N):
    """S = K_AA + K_AB (I-K_BB)^-1 K_BA mod q^N, via W = K_BA + K_BB W iteration."""
    KBA = [[K[b][a] for a in A] for b in B]
    W = [[list(x) for x in row] for row in KBA]
    for _ in range(N):
        W2 = []
        for bi, b in enumerate(B):
            row = []
            for ai in range(len(A)):
                acc = list(KBA[bi][ai])
                for bj, b2 in enumerate(B):
                    if K[b][b2] and W[bj][ai]:
                        acc = padd(acc, pmul(K[b][b2], W[bj][ai], N))
                row.append([c for c in acc[:N]])
            W2.append(row)
        W = [[pstrip(x) for x in row] for row in W2]
    S = {}
    for ai, i in enumerate(A):
        for aj, j in enumerate(A):
            acc = list(K[i][j][:N])
            for bi, b in enumerate(B):
                if K[i][b] and W[bi][aj]:
                    acc = padd(acc, pmul(K[i][b], W[bi][aj], N))
            S[(i, j)] = pstrip(acc[:N])
    return S

def exact_P(K, A, B):
    """P_ij = K_ij det(I-K_BB) + K_iB adj(I-K_BB) K_Bj ; val(S_ij)=val(P_ij) exactly,
    since det(I-K_BB) has constant term 1 (a unit in Q[[q]])."""
    M = [[padd([1] if b == b2 else [], pneg(K[b][b2])) for b2 in B] for b in B]
    d = pdet(M)
    if not d or d[0] != 1:
        raise ValueError("det(I-K_BB) not a unit")
    adj = padj(M)
    P = {}
    for i in A:
        for j in A:
            acc = pmul(K[i][j], d)
            for bi, b in enumerate(B):
                for bj, b2 in enumerate(B):
                    if K[i][b] and adj[bi][bj] and K[b2][j]:
                        acc = padd(acc, pmul(pmul(K[i][b], adj[bi][bj]), K[b2][j]))
            P[(i, j)] = acc
    return P

# ---- tropical side
def tropical_T(K, A, B):
    t = [[pval(K[i][j]) for j in range(len(K))] for i in range(len(K))]
    # Kleene star over B (min,+): Floyd-Warshall with 0 diagonal
    st = {(b, c): (0 if b == c else t[b][c]) for b in B for c in B}
    for m in B:
        for b in B:
            for c in B:
                if st[(b, m)] < INF and st[(m, c)] < INF and st[(b, m)] + st[(m, c)] < st[(b, c)]:
                    st[(b, c)] = st[(b, m)] + st[(m, c)]
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
                    v = t[i][b] + st[(b, c)] + t[c][j]
                    if v < best:
                        best = v
            T[(i, j)] = best
    return t, T

def lead_sum(K, A, B, t, i, j, Tij, absval=False):
    """sum over walks i -> b1 -> ... -> bk -> j (k>=1, b's in B, repeats allowed) and the
    direct entry, with total valuation == Tij, of the product of leading coefficients."""
    f = (lambda c: abs(c)) if absval else (lambda c: c)
    tot = 0
    if t[i][j] == Tij:
        tot += f(plead(K[i][j]))
    G = [dict() for _ in range(Tij + 1)]
    for v in range(Tij + 1):
        for b in B:
            s = 0
            if t[i][b] == v:
                s += f(plead(K[i][b]))
            for b2 in B:
                w = t[b2][b]
                if w < INF and 1 <= w <= v:
                    g = G[v - w].get(b2, 0)
                    if g:
                        s += g * f(plead(K[b2][b]))
            if s:
                G[v][b] = s
    for b in B:
        if t[b][j] <= Tij:
            g = G[Tij - t[b][j]].get(b, 0)
            if g:
                tot += g * f(plead(K[b][j]))
    return tot

def main():
    modes = ["pos", "mixed", "tie", "annih"]
    per = 300
    tot_inst = 0
    cnt = {}
    viol_ge = []
    viol_iff = []
    trunc_disagree = 0
    order_stats = []
    ctrl_naive = ctrl_rev = ctrl_nostar = ctrl_abs = 0
    flagged_cancel_inst = 0
    cancel_inst_total = 0
    entries = 0
    ents = {"eq_leadnz": 0, "strict_leadzero": 0, "strict_to_inf": 0, "both_inf": 0}
    P("C3 panel: modes=%s n in {4,5} per (mode,n)=%d total=%d" % (modes, per, len(modes) * 2 * per))
    P("%-6s %2s %5s %9s %11s %9s %9s" % ("mode", "n", "inst", "entries", "equal&lead!=0", "strict&lead=0", "viol"))
    for mi, mode in enumerate(modes):
        for n in (4, 5):
            c_inst = c_ent = c_eq = c_st = c_viol = 0
            for t_ in range(per):
                seed = 5200000 + 100000 * mi + 10000 * (n - 4) + t_
                K, A, B = gen(seed, n, mode)
                D = max((pdeg(K[i][j]) for i in range(n) for j in range(n) if K[i][j]), default=0)
                N = (len(B) + 1) * D + 1
                order_stats.append(N)
                S = series_S(K, A, B, N)
                Pp = exact_P(K, A, B)
                t, Tm = tropical_T(K, A, B)
                inst_cancel = False
                for i in A:
                    for j in A:
                        entries += 1; c_ent += 1
                        vs = pval(S[(i, j)])           # INF if no nonzero below N
                        vp = pval(Pp[(i, j)])
                        # truncation consistency: nonzero P has degree < N so truncated val == exact val
                        if vs != vp:
                            trunc_disagree += 1
                        val = vp
                        Tij = Tm[(i, j)]
                        if Tij >= INF:
                            ls = 0
                        else:
                            ls = lead_sum(K, A, B, t, i, j, Tij)
                        ok_ge = val >= Tij
                        eqv = (val == Tij)
                        ok_iff = (eqv == (ls != 0)) if Tij < INF else (val >= INF)
                        if not ok_ge:
                            viol_ge.append((seed, i, j, val, Tij))
                        if not ok_iff:
                            viol_iff.append((seed, i, j, val, Tij, ls))
                        if not ok_ge or not ok_iff:
                            c_viol += 1
                        if Tij >= INF:
                            ents["both_inf"] += (1 if val >= INF else 0)
                        elif eqv:
                            c_eq += 1; ents["eq_leadnz"] += 1
                        else:
                            c_st += 1
                            inst_cancel = True
                            if val >= INF:
                                ents["strict_to_inf"] += 1
                            else:
                                ents["strict_leadzero"] += 1
                        # controls
                        if Tij < INF and val != Tij:
                            ctrl_naive += 1          # naive "val==T always" is falsified here
                        if val > Tij and Tij < INF:
                            pass
                        if val < Tij:
                            pass
                        if Tij < INF and val > Tij:
                            ctrl_rev += 1            # claim "val <= T" falsified here
                        # wrong T: single hop only
                        tw = t[i][j]
                        for b in B:
                            if t[i][b] < INF and t[b][j] < INF:
                                tw = min(tw, t[i][b] + t[b][j])
                        if val < tw:
                            ctrl_nostar += 1         # claim val >= Tw falsified here
                        # sign-blind leading sum
                        if Tij < INF:
                            la = lead_sum(K, A, B, t, i, j, Tij, absval=True)
                            if ((val == Tij) != (la != 0)):
                                ctrl_abs += 1        # sign-blind criterion falsified here
                c_inst += 1
                if mode in ("tie", "annih"):
                    cancel_inst_total += 1
                    flagged_cancel_inst += 1 if inst_cancel else 0
            P("%-6s %2d %5d %9d %11d %9d %9d" % (mode, n, c_inst, c_ent, c_eq, c_st, c_viol))
            tot_inst += c_inst
    P("TOTAL instances=%d entries=%d" % (tot_inst, entries))
    P("entry classes: equal_with_nonzero_lead=%d  strict_with_zero_lead_finite=%d  strict_to_exact_zero(S_ij=0,T finite)=%d  both_infinite=%d"
      % (ents["eq_leadnz"], ents["strict_leadzero"], ents["strict_to_inf"], ents["both_inf"]))
    P("violations of val>=T: %d" % len(viol_ge))
    P("violations of 'equal iff lead sum != 0': %d" % len(viol_iff))
    if viol_ge:
        P("  smallest witness (>=):", sorted(viol_ge)[0])
    if viol_iff:
        P("  smallest witness (iff):", sorted(viol_iff)[0])
    P("truncated-series valuation vs exact-polynomial valuation disagreements: %d" % trunc_disagree)
    P("series order N=(|B|+1)*D+1, D=max entry degree; min/max N used: %d/%d" % (min(order_stats), max(order_stats)))
    P("  reason: S=P/det(I-K_BB), det has constant term 1, P polynomial of degree <= (|B|+1)D, so val(S)=val(P)<N or S=0")
    P("cancelling-mode instances with at least one entry strictly above T: %d/%d" % (flagged_cancel_inst, cancel_inst_total))
    P("CONTROL naive 'val==T always' falsified on %d entries (must be >0)" % ctrl_naive)
    P("CONTROL reversed 'val<=T' falsified on %d entries (must be >0)" % ctrl_rev)
    P("CONTROL single-hop (no Kleene star) lower bound falsified on %d entries (must be >0)" % ctrl_nostar)
    P("CONTROL sign-blind leading sum falsified on %d entries (must be >0)" % ctrl_abs)
    bad = (ctrl_naive == 0 or ctrl_rev == 0 or ctrl_nostar == 0 or ctrl_abs == 0 or flagged_cancel_inst == 0)
    with open(os.path.join(here, "..", "out", "c3_trop.txt"), "w", newline="\n") as fh:
        fh.write("\n".join(OUT) + "\n")
    if bad:
        print("CONTROL PASSED: checker cannot see cancellation")
        sys.exit(2)

main()
