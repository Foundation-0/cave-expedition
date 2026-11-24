#!/usr/bin/env python3
"""Root-graph obstruction of Theorem 1 (advocate check).

Builds the graph on norm-2 vectors with edges |u.v| = 1 for D_16 and for E_8 (+) E_8.
D_16 has one component of 480 roots spanning rank 16, while E_8 (+) E_8 has two components
of 240. A connected root set lies in one orthogonal summand, so D_16 cannot sit inside
E_8 (+) E_8, and no cross-polytope packing P_16 + Z^16 L can equal a translate of it.
Exact arithmetic with fractions.
Backs: AUDIT-020R, VERDICTS.md section 1 and REPORTS.md (Theorem 1 holds and is
elementary; it needs only D_n inside Gamma and a connected D_n root graph).
Needs: Python 3 only.
Run: python3 -I -B adv_obstruction.py
Time: about 1 second. No random numbers are used. Writes no files.
"""
import hashlib
import itertools
import json
from fractions import Fraction as Fr


def need(c, m):
    if not c:
        raise SystemExit("CHECK FAILED: " + m)


def comps(vecs):
    n = len(vecs)
    seen = [False] * n
    sizes = []
    for s in range(n):
        if seen[s]:
            continue
        stack = [s]
        seen[s] = True
        size = 0
        while stack:
            a = stack.pop()
            size += 1
            for b in range(n):
                if not seen[b] and abs(sum(x * y for x, y in zip(vecs[a], vecs[b]))) == 1:
                    seen[b] = True
                    stack.append(b)
        sizes.append(size)
    return sorted(sizes)


def dn_roots(n):
    out = []
    for i, j in itertools.combinations(range(n), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * n
                v[i], v[j] = si, sj
                out.append(v)
    return out


def e8_roots():
    out = [list(map(Fr, v)) for v in dn_roots(8)]
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            out.append([Fr(s, 2) for s in signs])
    need(len(out) == 240, "E8 count")
    return out


def main():
    rep = {}
    rep["D16_components"] = comps(dn_roots(16))
    e8 = e8_roots()
    e8e8 = [v + [Fr(0)] * 8 for v in e8] + [[Fr(0)] * 8 + v for v in e8]
    rep["E8+E8_components"] = comps(e8e8)
    # all norm-2 vectors of E8+E8: (w1,w2) with |w1|^2+|w2|^2 = 2 and w_k in E8 (min 2) -> one part zero
    rep["E8+E8_norm2_count_from_lemma"] = len(e8e8)
    # D16 roots span R^16 (rank 16): check rank of the 480 vectors
    M = [list(map(Fr, v)) for v in dn_roots(16)]
    r = 0
    A = [row[:] for row in M]
    for c in range(16):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c] / A[r][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        r += 1
    rep["D16_rank"] = r
    txt = json.dumps(rep, sort_keys=True)
    print(txt)
    print("SHA256", hashlib.sha256(txt.encode()).hexdigest())
    need(rep["D16_components"] == [480], "D16 root graph is connected with 480 roots")
    need(rep["D16_rank"] == 16, "D16 roots span rank 16")
    need(rep["E8+E8_components"] == [240, 240], "E8+E8 root graph has two components of 240")
    need(rep["E8+E8_norm2_count_from_lemma"] == 480, "E8+E8 has 480 norm-2 vectors")
    print("RESULT leech_sheaf/adv_obstruction: PASS D16 roots form 1 component of 480 (rank 16), "
          "E8+E8 roots form 2 components of 240")


if __name__ == "__main__":
    main()
