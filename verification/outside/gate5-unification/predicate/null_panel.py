"""Seeded generator of block systems unrelated to the ledger's eight domains.

Exact arithmetic only: int, fractions.Fraction, and the pair type QI for Q(i).
No floats, no numpy. Every random draw is an integer draw from random.Random
seeded with a string, so output is identical on every run and Python mode.

A system is a dict: id, family, mode ("native" or "scrambled"), ring ("Q" or
"Q(i)"), n, k, seed, perm, M. The pivot block (the block to be eliminated) is
the leading k x k block of M. Schur complement = D - C A^-1 B on the rest.

Run: python3 -I -B null_panel.py [master_seed] [per_cell]   (prints a JSON log)
"""
import hashlib
import json
import random
import sys
from fractions import Fraction

DEFAULT_MASTER = 20261121
DEFAULT_PER_CELL = 30
FAMILIES = (
    "pd_rational",
    "indefinite_symmetric",
    "grounded_laplacian_kron",
    "gaussian_conditioning",
    "normal_equations_nuisance",
    "hermitian_qi",
)
MODES = ("native", "scrambled")


class QI:
    """Element a + b*i of Q(i), with a and b Fractions."""

    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = Fraction(re)
        self.im = Fraction(im)

    @staticmethod
    def _c(x):
        if isinstance(x, QI):
            return x
        if isinstance(x, (int, Fraction)):
            return QI(x, 0)
        return None

    def __add__(self, o):
        o = QI._c(o)
        if o is None:
            return NotImplemented
        return QI(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __sub__(self, o):
        o = QI._c(o)
        if o is None:
            return NotImplemented
        return QI(self.re - o.re, self.im - o.im)

    def __rsub__(self, o):
        o = QI._c(o)
        if o is None:
            return NotImplemented
        return o - self

    def __mul__(self, o):
        o = QI._c(o)
        if o is None:
            return NotImplemented
        return QI(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __neg__(self):
        return QI(-self.re, -self.im)

    def norm(self):
        return self.re * self.re + self.im * self.im

    def conjugate(self):
        return QI(self.re, -self.im)

    def __truediv__(self, o):
        o = QI._c(o)
        if o is None:
            return NotImplemented
        n = o.norm()
        if n == 0:
            raise ZeroDivisionError("QI division by zero")
        num = self * o.conjugate()
        return QI(num.re / n, num.im / n)

    def __rtruediv__(self, o):
        o = QI._c(o)
        if o is None:
            return NotImplemented
        return o / self

    def __eq__(self, o):
        o = QI._c(o)
        if o is None:
            return NotImplemented
        return self.re == o.re and self.im == o.im

    def __ne__(self, o):
        r = self.__eq__(o)
        return r if r is NotImplemented else not r

    def __hash__(self):
        return hash((self.re, self.im))

    def __bool__(self):
        return self.re != 0 or self.im != 0

    def __str__(self):
        return "%s%s%si" % (self.re, "+" if self.im >= 0 else "-", abs(self.im))

    __repr__ = __str__


def elem_str(x):
    return str(x)


def mat_hash(M):
    s = ";".join(",".join(elem_str(x) for x in row) for row in M)
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def _rat(rng, a, q):
    return Fraction(rng.randint(-a, a), rng.randint(1, q))


def _mm(A, B):
    n, m, p = len(A), len(B), len(B[0])
    out = []
    for i in range(n):
        row = []
        for j in range(p):
            acc = Fraction(0)
            for t in range(m):
                acc += A[i][t] * B[t][j]
            row.append(acc)
        out.append(row)
    return out


def _tr(A):
    return [list(r) for r in zip(*A)]


def _gram(X):
    return _mm(_tr(X), X)


def _perm_apply(M, perm):
    n = len(M)
    return [[M[perm[i]][perm[j]] for j in range(n)] for i in range(n)]


def _build_pd_rational(rng, n):
    m = n + rng.randint(0, 2)
    W = [[Fraction(rng.randint(-3, 3)) for _ in range(n)] for _ in range(m)]
    G = _gram(W)
    for i in range(n):
        G[i][i] += 1
    s = Fraction(rng.randint(1, 5), rng.randint(1, 5))
    return [[s * x for x in row] for row in G], rng.randint(1, n - 1), "Q"


def _build_indefinite(rng, n):
    M = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            v = _rat(rng, 4, 3)
            M[i][j] = v
            M[j][i] = v
    return M, rng.randint(1, n - 1), "Q"


def _build_laplacian(rng, n):
    # Nodes 0..k-1 interior (eliminated), k..n-1 boundary; no boundary-boundary
    # edges; every boundary node touches an interior node; graph connected.
    k = rng.randint(1, n - 1)
    w = {}
    for i in range(1, k):
        j = rng.randint(0, i - 1)
        w[(j, i)] = rng.randint(1, 5)
    for b in range(k, n):
        i = rng.randint(0, k - 1)
        w[(i, b)] = rng.randint(1, 5)
    for i in range(k):
        for j in range(i + 1, n):
            if (i, j) not in w and rng.randint(0, 2) == 0:
                w[(i, j)] = rng.randint(1, 5)
    L = [[Fraction(0)] * n for _ in range(n)]
    for (i, j), c in sorted(w.items()):
        L[i][j] -= c
        L[j][i] -= c
        L[i][i] += c
        L[j][j] += c
    return L, k, "Q"


def _build_gaussian(rng, n):
    r = rng.choice((Fraction(1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(3, 4)))
    d = [Fraction(rng.randint(1, 4), rng.randint(1, 3)) for _ in range(n)]
    S = [[d[i] * d[j] * r ** abs(i - j) for j in range(n)] for i in range(n)]
    return S, rng.randint(1, n - 1), "Q"


def _build_normal_eq(rng, n):
    m = n + rng.randint(0, 4)
    X = [[Fraction(rng.randint(-3, 3)) for _ in range(n)] for _ in range(m)]
    return _gram(X), rng.randint(1, n - 1), "Q"


def _build_hermitian_qi(rng, n):
    M = [[QI(0, 0)] * n for _ in range(n)]
    for i in range(n):
        M[i][i] = QI(_rat(rng, 4, 2), 0)
        for j in range(i + 1, n):
            z = QI(_rat(rng, 3, 2), _rat(rng, 3, 2))
            M[i][j] = z
            M[j][i] = z.conjugate()
    return M, rng.randint(1, n - 1), "Q(i)"


BUILDERS = {
    "pd_rational": _build_pd_rational,
    "indefinite_symmetric": _build_indefinite,
    "grounded_laplacian_kron": _build_laplacian,
    "gaussian_conditioning": _build_gaussian,
    "normal_equations_nuisance": _build_normal_eq,
    "hermitian_qi": _build_hermitian_qi,
}


def generate_panel(master=DEFAULT_MASTER, per_cell=DEFAULT_PER_CELL):
    """Return the list of systems: for each family and index, a native system
    and a paired scrambled system (same matrix, uniformly random index
    permutation, same pivot size k)."""
    out = []
    for fam in FAMILIES:
        for idx in range(per_cell):
            seed = "%s|%s|%d" % (master, fam, idx)
            rng = random.Random(seed)
            n = rng.randint(2, 12)
            M, k, ring = BUILDERS[fam](rng, n)
            perm = list(range(n))
            rng.shuffle(perm)
            ident = list(range(n))
            for mode, p in (("native", ident), ("scrambled", perm)):
                MM = M if mode == "native" else _perm_apply(M, p)
                out.append(
                    {
                        "id": "%s/%s/%03d/%s" % (fam, mode, idx, master),
                        "family": fam,
                        "mode": mode,
                        "ring": ring,
                        "n": n,
                        "k": k,
                        "seed": seed,
                        "perm": p,
                        "M": MM,
                    }
                )
    return out


def panel_log(master, per_cell):
    systems = generate_panel(master, per_cell)
    sizes = {}
    for s in systems:
        sizes[s["n"]] = sizes.get(s["n"], 0) + 1
    return {
        "master_seed": master,
        "per_cell": per_cell,
        "families": list(FAMILIES),
        "modes": list(MODES),
        "count": len(systems),
        "size_histogram": {str(k): sizes[k] for k in sorted(sizes)},
        "systems": [
            {
                "id": s["id"],
                "family": s["family"],
                "mode": s["mode"],
                "ring": s["ring"],
                "n": s["n"],
                "k": s["k"],
                "seed": s["seed"],
                "perm": s["perm"],
                "sha256": mat_hash(s["M"]),
            }
            for s in systems
        ],
    }


def main(argv):
    master = int(argv[1]) if len(argv) > 1 else DEFAULT_MASTER
    per_cell = int(argv[2]) if len(argv) > 2 else DEFAULT_PER_CELL
    if per_cell < 1 or per_cell > 1000:
        sys.stderr.write("per_cell out of range\n")
        return 2
    sys.stdout.write(json.dumps(panel_log(master, per_cell), indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
