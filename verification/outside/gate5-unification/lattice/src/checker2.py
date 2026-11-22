"""Second checker for Gate 5: shares no code with g5lib / g5more.  Everything is recomputed modulo the prime
P = 2^31 - 1 (sqrt 2 = 2^((P+1)/4)) from the written definitions, and compared with the exact objects.
usage: checker2.py <objects dir> [stride]
A modular match is strong evidence, not a proof; the exact objects are the proof, this is the independent audit.
"""
import json
import os
import sys

P = 2147483647
R2 = pow(2, (P + 1) // 4, P)
HALF = pow(2, P - 2, P)
N = 8


def inv(a):
    return pow(a % P, P - 2, P)


def parse(s):
    def rat(t):
        if "/" in t:
            a, b = t.split("/")
            return int(a) * inv(int(b)) % P
        return int(t) % P

    if "sqrt2" in s:
        a, b = s.split("+", 1)
        return (rat(a) + rat(b.replace("*sqrt2", "")) * R2) % P
    return rat(s)


def motif(i, s):  # vertex index -> coordinates
    v = [0] * N
    v[i] = 1 if s == 0 else -1
    return v


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def bars_mod(L):
    """independent bar list from the packing definition: contacts inside cell 0 plus the 8 bridges."""
    pts = []
    for i in range(N):
        for s in (0, 1):
            pts.append((i, s, motif(i, s)))
    bars = []
    # intra-cell contacts: pairs of motif points at squared distance 2 (found by testing, not by index rules)
    for a in range(len(pts)):
        for b in range(len(pts)):
            if a == b:
                continue
            d = [x - y for x, y in zip(pts[a][2], pts[b][2])]
            if dot(d, d) == 2 and a > b:
                # a is the "v" endpoint, b the "u" endpoint
                bars.append((b, a, [x % P for x in d]))
    for i in range(N):
        u = 2 * i      # +e_i
        v = 2 * i + 1  # -e_i
        ell = [(motif(i, 1)[k] - motif(i, 0)[k] + L[i][k]) % P for k in range(N)]
        bars.append((u, v, ell))
    return bars


def pair_idx():
    return [(k, l) for k in range(N) for l in range(k + 1, N)]


def build_RW(bars):
    """rows of [d0 | ae] as dict (cols 0..127 vertex dofs, 128..163 strain)"""
    rows = []
    pr = pair_idx()
    for (u, v, ell) in bars:
        r = {}
        for k in range(N):
            if ell[k]:
                r[v * N + k] = ell[k]
                r[u * N + k] = (-ell[k]) % P
        for k in range(N):
            x = ell[k] * ell[k] % P
            if x:
                r[128 + k] = x
        for c, (k, l) in enumerate(pr):
            x = 2 * ell[k] * ell[l] % P
            if x:
                r[128 + N + c] = x
        rows.append(r)
    return rows


def gram(rows, ncol):
    G = [dict() for _ in range(ncol)]
    for r in rows:
        for i, a in r.items():
            gi = G[i]
            wa = a * HALF % P
            for j, b in r.items():
                gi[j] = (gi.get(j, 0) + wa * b) % P
    return G


def schur_mod(rows):
    """S = K - B^T Delta^+ B mod P, by Gauss-Jordan on the augmented system [Delta | -B]."""
    G = gram(rows, 164)
    aug = []
    for i in range(128):
        d = {j: v for j, v in G[i].items() if j < 128 and v}
        for j, v in G[i].items():
            if j >= 128 and v:
                d[j] = (-v) % P
        aug.append(d)
    piv = {}
    for row in aug:
        r = dict(row)
        for pc in [c for c in r if c in piv and c < 128]:
            f = r.get(pc, 0)
            if f:
                for c2, v2 in piv[pc].items():
                    nv = (r.get(c2, 0) - f * v2) % P
                    if nv:
                        r[c2] = nv
                    else:
                        r.pop(c2, None)
        cols = [c for c in r if c < 128]
        if not cols:
            if any(r.values()):
                raise ValueError("inconsistent")
            continue
        pc = min(cols)
        iv = inv(r[pc])
        r = {c: v * iv % P for c, v in r.items()}
        for opc, orow in piv.items():
            if pc in orow:
                f = orow[pc]
                for c2, v2 in r.items():
                    nv = (orow.get(c2, 0) - f * v2) % P
                    if nv:
                        orow[c2] = nv
                    else:
                        orow.pop(c2, None)
        piv[pc] = r
    X = {}
    for pc, r in piv.items():
        X[pc] = {c - 128: v for c, v in r.items() if c >= 128}
    S = [[0] * 36 for _ in range(36)]
    for i in range(36):
        for j in range(36):
            acc = G[128 + i].get(128 + j, 0)
            S[i][j] = acc
    for r_ in range(128):
        Bi = G[r_]
        if r_ not in X:
            continue
        xs = X[r_]
        for i in range(36):
            b = Bi.get(128 + i, 0)
            if b:
                for j, x in xs.items():
                    S[i][j] = (S[i][j] + b * x) % P
    return S


def rank_mod(M):
    A = [list(r) for r in M]
    rk = 0
    m, n = len(A), len(A[0])
    for c in range(n):
        p = next((r for r in range(rk, m) if A[r][c] % P), None)
        if p is None:
            continue
        A[rk], A[p] = A[p], A[rk]
        iv = inv(A[rk][c])
        A[rk] = [x * iv % P for x in A[rk]]
        for r in range(m):
            if r != rk and A[r][c] % P:
                f = A[r][c]
                A[r] = [(x - f * y) % P for x, y in zip(A[r], A[rk])]
        rk += 1
    return rk


def rank_rows(rows, ncol):
    return rank_mod([[r.get(c, 0) for c in range(ncol)] for r in rows])


def main():
    objd = sys.argv[1]
    stride = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    bad = []

    def chk(label, cond):
        print(("PASS " if cond else "FAIL ") + label)
        if not cond:
            bad.append(label)

    def ctl(label, detected):
        print(("CONTROL-DETECTED " if detected else "CONTROL-NOT-DETECTED ") + label)
        if not detected:
            bad.append("control " + label)

    # ---- the five real pairs
    for name in ("e8_s1", "d8_s1", "d8_k1", "e8_half", "d8_half"):
        with open(os.path.join(objd, "pair_%s.json" % name), encoding="utf-8") as f:
            o = json.load(f)
        L = [[parse(x) for x in r] for r in o["L"]]
        rows = build_RW(bars_mod(L))
        S = schur_mod(rows)
        Sj = [[parse(x) for x in r] for r in o["elasticity"]["S"]]
        chk("%s: S recomputed mod P equals exact S mod P (36x36)" % name, S == Sj)
        chk("%s: rank of S mod P is 1" % name, rank_mod(S) == 1)
        rk = rank_rows([{c: v for c, v in r.items() if c < 128} for r in rows], 128)
        chk("%s: rank d0 = 99 so H0=29, H1=21 (mod P)" % name, rk == 99 and 128 - rk == 29 and len(rows) - rk == 21)
        # exact objects K, B, Delta against mod-P gram
        G = gram(rows, 164)
        okK = all(G[128 + i].get(128 + j, 0) == v for i, j, v in [(a, b, parse(c)) for a, b, c in o["elasticity"]["K_sparse"]])
        cntK = sum(1 for i in range(36) for j in range(36) if G[128 + i].get(128 + j, 0))
        okB = all(G[i].get(128 + j, 0) == v for i, j, v in [(a, b, parse(c)) for a, b, c in o["elasticity"]["B_sparse"]])
        okD = all(G[i].get(j, 0) == v for i, j, v in [(a, b, parse(c)) for a, b, c in o["elasticity"]["Delta_sparse"]])
        chk("%s: K, B, Delta sparse entries equal the independent Gram blocks mod P" % name,
            okK and okB and okD and cntK == len(o["elasticity"]["K_sparse"]))
        # Phi identity R_el = R_lat Phi mod P (Phi from the JSON)
        Phi = {}
        for i, j, v in o["Phi_sparse"]:
            Phi.setdefault(i, {})[j] = parse(v)
        pr = pair_idx()
        okphi = True
        bars_o = o["bars"]
        rows_o = build_RW([(b["u"], b["v"], [parse(x) for x in b["ell"]]) for b in bars_o])
        for b, rrow in zip(bars_o, rows_o):
            u, v = b["u"], b["v"]
            ell = [parse(x) for x in b["ell"]]
            m = b["m"]
            lat = {}
            for k in range(N):
                if ell[k]:
                    lat[v * N + k] = ell[k]
                    lat[u * N + k] = (-ell[k]) % P
            for k in range(N):
                if m[k]:
                    for l in range(N):
                        if ell[l]:
                            lat[128 + k * N + l] = m[k] * ell[l] % P
            comp = {}
            for k, a in lat.items():
                for c, w in Phi.get(k, {}).items():
                    comp[c] = (comp.get(c, 0) + a * w) % P
            comp = {c: v_ for c, v_ in comp.items() if v_}
            if comp != rrow:
                okphi = False
                break
        chk("%s: R_lat Phi = R_el row by row mod P (Phi read from the object file)" % name, okphi)
        if name == "e8_s1":
            Sbad = [list(r) for r in Sj]
            Sbad[3][4] = (Sbad[3][4] + 1) % P
            ctl("a tampered S entry is detected", S != Sbad)
            Lp = [list(r) for r in L]
            Lp[0][1] = (Lp[0][1] + inv(7)) % P
            ctl("a perturbed lattice gives a different S", schur_mod(build_RW(bars_mod(Lp))) != Sj)
            ctl("a perturbed lattice loses rank 1", rank_mod(schur_mod(build_RW(bars_mod(Lp)))) != 1)
    # ---- null lattices
    for name in ("e8_s1", "d8_s1"):
        path = os.path.join(objd, "null_lattices_%s.json" % name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            o = json.load(f)
        checked = 0
        mism = 0
        for rec in o["lattices"][::stride]:
            L = [[parse(x) for x in r] for r in rec["L"]]
            S = schur_mod(build_RW(bars_mod(L)))
            rk = rank_mod(S)
            want = rec["S_inertia"][0] + rec["S_inertia"][1]
            if rk != want or ((rk == 1 and rec["S_inertia"] == [1, 0, 35]) != rec["collapse"]):
                mism += 1
            checked += 1
        chk("null lattices %s: independent mod-P rank of S matches the recorded rank on %d of %d lattices (stride %d)" % (name, checked, len(o["lattices"]), stride), mism == 0)
    print("FAILS", len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
