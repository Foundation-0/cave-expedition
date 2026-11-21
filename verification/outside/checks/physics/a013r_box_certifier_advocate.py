#!/usr/bin/env python3
"""Advocate soundness test of the Probe 3 box certifier (AUDIT-013R).

Backs: VERDICTS section 1 row "Inertia box certifier (013R)": 2,795 certified
boxes, 22,360 exact sample points, 0 unsound, including indefinite inertias.
Also the check that the oracle itself fires on known inputs (must-fail controls).

The certifier from the gravity clone is imported and is the object under test.
The oracle shares no code with it: an exact characteristic polynomial
(Faddeev-LeVerrier over Fraction) with Descartes sign counts, exact for real
symmetric matrices. Families: 40 random symmetric 3x3 and 4x4 non-affine
matrices in 2 parameters on a 1/4-wide root box,
M(t) = A0 + t1 A1 + t2 A2 + t1^2 A3 + t1 t2 A4 + t2^3 A5, integer entries in
[-3, 3]. For every certified leaf box, 4 corners, the midpoint and 3 seeded
interior rational points are compared with the certified inertia.
Seeds: 4242 and 777 by default (printed); give others as a comma list after the path.

Needs: Python 3 (standard library only); a clone of Foundation-0/gravity (draft pull request 30).
Run:   python3 -I -B a013r_box_certifier_advocate.py /path/to/gravity [4242,777]
       (or set GRAVITY_REPO; add --verbose for all counts)
Time:  about 1 minute.
Exit:  0 only if every check holds.
"""
import importlib.util
import json
import os
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

NAME = "a013r_box_certifier_advocate"
FAILS = []
COUNT = [0]


def check(cond, msg):
    COUNT[0] += 1
    if not cond:
        FAILS.append(msg)


ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
GRAV = ARGS[0] if ARGS else os.environ.get("GRAVITY_REPO", "")
if not GRAV or not Path(GRAV).is_dir():
    raise SystemExit("Pass the path of a Foundation-0/gravity clone as the first argument or set GRAVITY_REPO.")
try:
    SEEDS = [int(x) for x in (ARGS[1] if len(ARGS) > 1 else "4242,777").split(",")]
except ValueError:
    raise SystemExit("The seeds must be a comma list of integers, for example 4242,777.")
P3 = Path(GRAV) / "studies/expedition-aest-helmholtz-probes/probe3_nonaffine_inertia_box_certifier.py"
if not P3.is_file():
    raise SystemExit("Missing " + str(P3) + ". Is the clone at the commit listed in README.md?")
spec = importlib.util.spec_from_file_location("p3", P3)
p3 = importlib.util.module_from_spec(spec)
sys.modules["p3"] = p3
spec.loader.exec_module(p3)
QI = p3.QI


def charpoly(M):
    n = len(M)
    I = [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
    c = [Fr(1)]
    Mk = [row[:] for row in I]
    for k in range(1, n + 1):
        AM = [[sum(M[i][t] * Mk[t][j] for t in range(n)) for j in range(n)] for i in range(n)]
        ck = -sum(AM[i][i] for i in range(n)) / k
        c.append(ck)
        Mk = [[AM[i][j] + (ck if i == j else 0) for j in range(n)] for i in range(n)]
    return c  # lambda^n + c1 lambda^(n-1) + ... + cn


def inertia(M):
    c = charpoly(M)
    n = len(M)
    nz = 0
    while nz < n and c[n - nz] == 0:
        nz += 1
    coeffs = c[: n + 1 - nz]  # polynomial with zero roots removed, highest first
    def changes(seq):
        s = [x for x in seq if x != 0]
        return sum(1 for a, b in zip(s, s[1:]) if (a > 0) != (b > 0))
    pos = changes(coeffs)
    m = len(coeffs) - 1
    neg = changes([x * (-1) ** (m - i) for i, x in enumerate(coeffs)])
    return (pos, nz, neg)


def make_family(rng, n):
    def sym():
        A = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                A[i][j] = A[j][i] = rng.randint(-3, 3)
        return A
    As = [sym() for _ in range(6)]
    def ev_exact(t1, t2):
        terms = [Fr(1), t1, t2, t1 * t1, t1 * t2, t2 * t2 * t2]
        return [[sum(Fr(As[k][i][j]) * terms[k] for k in range(6)) for j in range(n)] for i in range(n)]
    def ev_qi(pt):
        t1, t2 = pt
        terms = [QI.pt(1), t1, t2, t1.sqr(), t1 * t2, t2.sqr() * t2]
        return [[sum((terms[k] * Fr(As[k][i][j]) for k in range(6)), QI.pt(0)) for j in range(n)] for i in range(n)]
    return ev_exact, ev_qi


def leaves(ev_qi, box, depth=0, out=None, maxd=6):
    out = [] if out is None else out
    ok, inert, _ = p3.certify_single_box(ev_qi, box)
    if ok:
        out.append((box, tuple(inert)))
        return out
    if depth >= maxd:
        return out
    ax = max(range(2), key=lambda i: box[i].width())
    m = box[ax].mid()
    for lo, hi in ((box[ax].lo, m), (m, box[ax].hi)):
        b = list(box)
        b[ax] = QI(lo, hi)
        leaves(ev_qi, tuple(b), depth + 1, out, maxd)
    return out


def run_seed(SEED):
    rng = random.Random(SEED)
    stats = {"families": 0, "certified_boxes": 0, "points_checked": 0, "violations": 0,
             "inertia_classes_seen": {}, "boxes_with_inertia_change_found_by_sampling_but_not_certified": 0}
    for fam in range(40):
        n = 3 if fam % 2 == 0 else 4
        ev_exact, ev_qi = make_family(rng, n)
        stats["families"] += 1
        c1, c2 = Fr(rng.randint(-8, 8), 8), Fr(rng.randint(-8, 8), 8)
        root = (QI(c1 - Fr(1, 8), c1 + Fr(1, 8)), QI(c2 - Fr(1, 8), c2 + Fr(1, 8)))
        for box, cert in leaves(ev_qi, root, maxd=7):
            stats["certified_boxes"] += 1
            stats["inertia_classes_seen"][str(cert)] = stats["inertia_classes_seen"].get(str(cert), 0) + 1
            pts = [(box[0].lo, box[1].lo), (box[0].lo, box[1].hi), (box[0].hi, box[1].lo), (box[0].hi, box[1].hi),
                   (box[0].mid(), box[1].mid())]
            for _ in range(3):
                u, v = Fr(rng.randint(0, 997), 997), Fr(rng.randint(0, 991), 991)
                pts.append((box[0].lo + u * box[0].width(), box[1].lo + v * box[1].width()))
            for t1, t2 in pts:
                stats["points_checked"] += 1
                if inertia(ev_exact(t1, t2)) != cert:
                    stats["violations"] += 1
    # Must-fail control: the oracle itself on a known singular and a known indefinite matrix
    ctrl = {"singular_diag(1,0,-1)": inertia([[Fr(1), 0, 0], [0, Fr(0), 0], [0, 0, Fr(-1)]]),
            "[[0,1],[1,0]]": inertia([[Fr(0), Fr(1)], [Fr(1), Fr(0)]])}
    check(ctrl["singular_diag(1,0,-1)"] == (1, 1, 1) and ctrl["[[0,1],[1,0]]"] == (1, 0, 1), "oracle control failed")
    stats["oracle_controls"] = {k: list(v) for k, v in ctrl.items()}
    return stats


def main():
    tot = {"certified_boxes": 0, "points_checked": 0, "violations": 0}
    allstats = {}
    indefinite = set()
    for seed in SEEDS:
        print("seed", seed)
        st = run_seed(seed)
        allstats[seed] = st
        check(st["families"] == 40, "seed %d: expected 40 families" % seed)
        check(st["certified_boxes"] >= 500 and st["points_checked"] >= 4000, "seed %d: too few certified boxes sampled" % seed)
        check(st["violations"] == 0, "seed %d: %d sample points disagree with the certified inertia" % (seed, st["violations"]))
        check(st["boxes_with_inertia_change_found_by_sampling_but_not_certified"] == 0, "seed %d: unexpected counter value" % seed)
        for k in tot:
            tot[k] += st[k]
        for cls in st["inertia_classes_seen"]:
            pos, zero, neg = [int(x) for x in cls.strip("()").split(",")]
            if pos > 0 and neg > 0:
                indefinite.add(cls)
    check(len(indefinite) >= 3, "fewer than 3 indefinite inertia classes were certified")
    if "--verbose" in sys.argv:
        print(json.dumps(allstats, indent=1, sort_keys=True))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    print("RESULT %s: PASS %d of %d checks; seeds %s: %d certified boxes, %d exact sample points, %d violations, %d indefinite inertia classes certified" % (
        NAME, COUNT[0], COUNT[0], ",".join(str(s) for s in SEEDS), tot["certified_boxes"], tot["points_checked"], tot["violations"], len(indefinite)))




if __name__ == "__main__":
    main()
