#!/usr/bin/env python3
"""Independent soundness test of the Probe 3 inertia box certifier (AUDIT-013R).

Backs: VERDICTS section 1 row "Inertia box certifier (013R)": certified boxes
are sound, including indefinite inertias, and no box that straddles an inertia
change or the singular line L1 + L2 = 2 is certified.

The certifier from the gravity clone (probe3_nonaffine_inertia_box_certifier.py)
is the object under test and is imported. Everything that judges it is written
here: an exact inertia oracle (Faddeev-LeVerrier characteristic polynomial over
Fractions plus Descartes sign counts, exact for real symmetric matrices), the
two-bar truss Hessian re-derived with SymPy from the energy in the host docs,
120 random non-affine matrix families with random boxes, and hand-built near
misses. The random generator is random.Random(90210), seed printed below.

Needs: Python 3, sympy; a clone of Foundation-0/gravity (draft pull request 30).
Run:   python3 -I -B a013r_box_certifier_independent.py /path/to/gravity
       (or set GRAVITY_REPO; add --verbose for all numbers)
Time:  about 1 to 2 minutes.
Exit:  0 only if every check holds.
"""
import importlib.util
import json
import os
import random
import sys
from fractions import Fraction as F
from pathlib import Path

import sympy as sp

NAME = "a013r_box_certifier_independent"
SEED = 90210
FAILS = []
COUNT = [0]


def check(cond, msg):
    COUNT[0] += 1
    if not cond:
        FAILS.append(msg)


def repo_path():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    value = args[0] if args else os.environ.get("GRAVITY_REPO", "")
    if not value or not Path(value).is_dir():
        raise SystemExit("Pass the path of a Foundation-0/gravity clone as the first argument or set GRAVITY_REPO.")
    return Path(value)


P3 = repo_path() / "studies/expedition-aest-helmholtz-probes/probe3_nonaffine_inertia_box_certifier.py"
if not P3.is_file():
    raise SystemExit("Missing " + str(P3) + ". Is the clone at the commit listed in README.md?")
spec = importlib.util.spec_from_file_location("p3", P3)
p3 = importlib.util.module_from_spec(spec)
sys.modules["p3"] = p3
spec.loader.exec_module(p3)


QI = p3.QI


# ---------- exact oracle ----------
def charpoly(M):
    n = len(M)
    I = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    Mk = [[F(0)] * n for _ in range(n)]
    c = [F(1)]
    for k in range(1, n + 1):
        Mk = [[sum(M[i][t] * Mk[t][j] for t in range(n)) + c[-1] * I[i][j] for j in range(n)] for i in range(n)]
        AM = [[sum(M[i][t] * Mk[t][j] for t in range(n)) for j in range(n)] for i in range(n)]
        c.append(-sum(AM[i][i] for i in range(n)) / k)
    return c  # x^n + c1 x^(n-1) + ... + cn


def inertia(M):
    c = charpoly(M)
    z = 0
    while c and c[-1] == 0:
        c.pop()
        z += 1

    def sc(cs):
        cs = [x for x in cs if x != 0]
        return sum(1 for a, b in zip(cs, cs[1:]) if a * b < 0)

    pos = sc(c)
    neg = sc([x * (-1) ** (len(c) - 1 - i) for i, x in enumerate(c)])
    return (pos, z, neg)  # same (pos, zero, neg) order as the certifier


# ---------- truss: my own derivation ----------
L1s, L2s, xs, ys = sp.symbols("L1 L2 x y", real=True)
V = sum((1 / (2 * L)) * (sp.sqrt((xs - px) ** 2 + ys**2) - L) ** 2 for L, px in ((L1s, -1), (L2s, 1)))
HV = sp.hessian(V, (xs, ys))


def truss_stable_hessian_inertia(L1, L2):
    """Inertia of the Hessian at the stable equilibrium branch used in docs/10 (exact, algebraic)."""
    L1, L2 = sp.Rational(L1), sp.Rational(L2)
    if L1 + L2 <= 2:
        x0, y0 = (L1 - L2) / (L1 + L2), sp.Integer(0)
        if L1 + L2 == 2:
            x0 = (L1 - L2) / 2
    else:
        x0 = (L1**2 - L2**2) / 4
        y0 = sp.sqrt(L1**2 - (x0 + 1) ** 2)
    Hn = sp.simplify(HV.subs({L1s: L1, L2s: L2, xs: x0, ys: y0}))
    g = [sp.simplify(sp.diff(V, v).subs({L1s: L1, L2s: L2, xs: x0, ys: y0})) for v in (xs, ys)]
    if any(gi != 0 for gi in g):
        raise RuntimeError(f"not an equilibrium at {(L1, L2)}: {g}")
    tr, det = sp.nsimplify(Hn.trace()), sp.simplify(Hn.det())
    if det == 0:
        return (1 if tr > 0 else 0, 1, 1 if tr < 0 else 0)
    if det < 0:
        return (1, 0, 1)
    return (2, 0, 0) if tr > 0 else (0, 0, 2)


def rand_in(iv, rng, den=997):
    return iv.lo + (iv.hi - iv.lo) * F(rng.randrange(den + 1), den)


def boxes_grid(lo, hi, nsplit):
    out = []
    for i in range(nsplit):
        for j in range(nsplit):
            out.append((QI(lo[0] + (hi[0] - lo[0]) * F(i, nsplit), lo[0] + (hi[0] - lo[0]) * F(i + 1, nsplit)),
                        QI(lo[1] + (hi[1] - lo[1]) * F(j, nsplit), lo[1] + (hi[1] - lo[1]) * F(j + 1, nsplit))))
    return out


def main():
    rng = random.Random(SEED)
    print("seed", SEED)
    out = {}
    # ---- 1. truss: compare the certifier's pieces with my Hessian over the docs/10 box ----
    # Rebuild the certifier's evaluators by calling its system function's closures is not possible,
    # so reconstruct them from the module source via a small shim: call system1 for its JSON and
    # separately test certify_single_box on my own exact-rational evaluator families.
    s1 = p3.system1_fibral_rigidity_truss()
    out["team_system1_summary"] = {k: (v.get("certified_inertia"), v.get("uniformly_certified"), v.get("boxes_evaluated"))
                                   for k, v in s1.items() if isinstance(v, dict) and "boxes_evaluated" in v}
    # my own on-line Hessian enclosure written as a single analytic expression (no branch on L1+L2):
    def M_online(pt):
        L1, L2 = pt
        hxx = L1.inv() + L2.inv()
        return [[hxx, QI.pt(0)], [QI.pt(0), hxx * (QI.pt(1) - (L1 + L2) * QI.pt(F(1, 2)))]]

    # pointwise agreement of my Hessian inertia with the on-line formula at sampled points, and the line
    agree = 0
    line_pts = [(F(7, 10), F(13, 10)), (F(1), F(1)), (F(23, 20), F(17, 20)), (F(3, 4), F(5, 4))]
    for L1, L2 in line_pts:
        if truss_stable_hessian_inertia(L1, L2) != (1, 1, 0):
            raise SystemExit(f"line point not singular {(L1, L2)}")
    # straddling boxes for the analytic on-line expression must never certify
    straddle_certified = 0
    straddle_tried = 0
    for _ in range(300):
        c1 = F(rng.randrange(700, 1300), 1000)
        c2 = 2 - c1 + F(rng.randrange(-20, 21), 1000)
        w1, w2 = F(rng.randrange(1, 60), 1000), F(rng.randrange(1, 60), 1000)
        box = (QI(c1 - w1, c1 + w1), QI(c2 - w2, c2 + w2))
        s = (box[0].lo + box[1].lo, box[0].hi + box[1].hi)
        if not (s[0] < 2 < s[1]):
            continue
        straddle_tried += 1
        ok, _, _ = p3.certify_single_box(M_online, box)
        straddle_certified += int(ok)
    out["truss_online_expr_straddling_line"] = {"boxes_tried": straddle_tried, "certified": straddle_certified}
    # certified sub-boxes of the docs/10 box: sample points, compare with MY Hessian (both branches)
    def M_off(pt):  # the certifier's congruent off-line form, re-entered from docs/10 algebra
        L1, L2 = pt
        x = (L1.sqr() - L2.sqr()) * QI.pt(F(1, 4))
        i1 = L1.inv() * L1.inv() * L1.inv()
        i2 = L2.inv() * L2.inv() * L2.inv()
        A = (x + 1).sqr() * i1 + (x - 1).sqr() * i2
        B = (x + 1) * i1 + (x - 1) * i2
        return [[A, B], [B, i1 + i2]]

    n_cert = n_pts = mism = 0
    refused = 0
    for box in boxes_grid((F(7, 10), F(9, 10)), (F(13, 10), F(15, 10)), 12):
        s_lo, s_hi = box[0].lo + box[1].lo, box[0].hi + box[1].hi
        if s_hi < 2:
            ev = M_online
        elif s_lo > 2:
            ev = M_off
        else:
            continue
        ok, inn, _ = p3.certify_single_box(ev, box)
        if not ok:
            refused += 1
            continue
        n_cert += 1
        for _ in range(4):
            L1, L2 = rand_in(box[0], rng), rand_in(box[1], rng)
            n_pts += 1
            if truss_stable_hessian_inertia(L1, L2) != tuple(inn):
                mism += 1
    out["truss_certified_subboxes_sampled"] = {"boxes_certified": n_cert, "boxes_refused": refused,
                                               "points_checked_against_my_hessian": n_pts, "mismatches": mism}
    # pointwise-only check of the full corner set used by docs/10 (reproduces table)
    out["docs10_points"] = {f"{a},{b}": truss_stable_hessian_inertia(a, b) for a, b in
                            ((F(7, 10), F(9, 10)), (F(7, 10), F(3, 2)), (F(13, 10), F(9, 10)), (F(13, 10), F(3, 2)), (F(9, 10), F(11, 10)))}

    # ---- 2. adversarial random polynomial families ----
    def rand_poly_family(n, rng):
        # symmetric M(t1,t2) = A0 + t1 A1 + t2 A2 + t1*t2 A3 + t1^2 A4 (non-affine), small integers
        mats = []
        for _ in range(5):
            A = [[F(0)] * n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    A[i][j] = A[j][i] = F(rng.randint(-4, 4))
            mats.append(A)
        def at_pt(t1, t2):
            co = [1, t1, t2, t1 * t2, t1 * t1]
            return [[sum(co[k] * mats[k][i][j] for k in range(5)) for j in range(n)] for i in range(n)]
        def ev(pt):
            t1, t2 = pt
            co = [QI.pt(1), t1, t2, t1 * t2, t1.sqr()]
            return [[sum((co[k] * mats[k][i][j] for k in range(5)), QI.pt(0)) for j in range(n)] for i in range(n)]
        return at_pt, ev

    adv = {"families": 0, "boxes_tried": 0, "certified": 0, "sample_points": 0, "unsound": 0,
           "certified_boxes_with_sign_change_found": 0, "straddle_attempts": 0, "straddle_certified": 0}
    for fam in range(120):
        n = rng.choice([2, 3, 4])
        at_pt, ev = rand_poly_family(n, rng)
        adv["families"] += 1
        for _ in range(12):
            c1, c2 = F(rng.randint(-200, 200), 100), F(rng.randint(-200, 200), 100)
            w = F(rng.choice([1, 2, 5, 10, 25, 50]), 100)
            box = (QI(c1 - w, c1 + w), QI(c2 - w, c2 + w))
            adv["boxes_tried"] += 1
            try:
                ok, inn, _ = p3.certify_single_box(ev, box)
            except (ZeroDivisionError, ValueError):
                continue
            # find whether the inertia actually changes inside the box on a fine rational grid
            seen = set()
            for i in range(9):
                for j in range(9):
                    t1 = box[0].lo + (box[0].hi - box[0].lo) * F(i, 8)
                    t2 = box[1].lo + (box[1].hi - box[1].lo) * F(j, 8)
                    seen.add(inertia(at_pt(t1, t2)))
            if len(seen) > 1:
                adv["straddle_attempts"] += 1
                adv["straddle_certified"] += int(bool(ok))
            if ok:
                adv["certified"] += 1
                for _ in range(10):
                    t1, t2 = rand_in(box[0], rng), rand_in(box[1], rng)
                    adv["sample_points"] += 1
                    if inertia(at_pt(t1, t2)) != tuple(inn):
                        adv["unsound"] += 1
                if len(seen) > 1:
                    adv["certified_boxes_with_sign_change_found"] += 1
    out["adversarial_random_families"] = adv

    # ---- 3. hand-built near-misses ----
    near = {}
    cases = {
        "tangent_zero_t^2": (lambda pt: [[QI.pt(1), QI.pt(0)], [QI.pt(0), pt[0].sqr()]], (QI(F(-1, 10), F(1, 7)),)),
        "tangent_zero_offcentre": (lambda pt: [[QI.pt(1), QI.pt(0)], [QI.pt(0), (pt[0] - QI.pt(F(1, 3))).sqr()]], (QI(F(0), F(1, 2)),)),
        "eigen_crossing_2x2": (lambda pt: [[pt[0], QI.pt(1)], [QI.pt(1), pt[0]]], (QI(F(9, 10), F(11, 10)),)),
        "tiny_box_on_crossing": (lambda pt: [[pt[0] - QI.pt(1), QI.pt(0)], [QI.pt(0), QI.pt(1)]], (QI(F(1) - F(1, 10**12), F(1) + F(1, 10**13)),)),
        "skew_blackbox_scope_note": (lambda pt: [[QI.pt(1), pt[0]], [-pt[0], QI.pt(1)]], (QI(F(-1, 2), F(1, 2)),)),
    }
    for name, (ev, box) in cases.items():
        try:
            ok, inn, mg = p3.certify_single_box(ev, box)
            near[name] = {"certified": bool(ok), "inertia": inn}
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            near[name] = {"raised": type(exc).__name__}
    out["near_misses"] = near
    out_ = out
    s1 = out_["team_system1_summary"]
    check(s1["full_box_piecewise_isolates_L1_plus_L2_eq_2"][1] is False, "full box straddling the singular line was certified uniformly")
    for key in ("online_subbox_7_10_to_8_10_x_9_10_to_1_certified_PD", "offline_subbox_congruent_certified_PD", "offline_subbox_raw_isqrt_certified_PD"):
        check(s1[key][1] is True and tuple(s1[key][0]) == (2, 0, 0), "truss sub-box %s is not certified positive definite" % key)
    st = out_["truss_online_expr_straddling_line"]
    check(st["boxes_tried"] >= 100 and st["certified"] == 0, "a box straddling L1 + L2 = 2 was certified (tried %d)" % st["boxes_tried"])
    sub = out_["truss_certified_subboxes_sampled"]
    check(sub["boxes_certified"] >= 100 and sub["points_checked_against_my_hessian"] >= 400 and sub["mismatches"] == 0,
          "certified truss sub-boxes disagree with the independent Hessian")
    d = out_["docs10_points"]
    check(d["9/10,11/10"] == (1, 1, 0), "the on-line point is not singular with inertia (1,1,0)")
    check(all(v == (2, 0, 0) for k, v in d.items() if k != "9/10,11/10"), "a stable-branch corner is not positive definite")
    adv = out_["adversarial_random_families"]
    check(adv["families"] == 120 and adv["certified"] >= 100 and adv["sample_points"] >= 1000, "too few certified boxes were sampled")
    check(adv["unsound"] == 0, "a certified box holds a sampled point of different inertia")
    check(adv["certified_boxes_with_sign_change_found"] == 0 and adv["straddle_attempts"] >= 100 and adv["straddle_certified"] == 0,
          "a box with a sampled inertia change was certified")
    nm = out_["near_misses"]
    for name in ("tangent_zero_t^2", "tangent_zero_offcentre", "eigen_crossing_2x2", "tiny_box_on_crossing"):
        check(nm[name].get("certified") is False, "near miss %s was certified" % name)
    check(nm["skew_blackbox_scope_note"].get("certified") is True, "scope note case (skew-symmetric entry) changed behaviour")

    if "--verbose" in sys.argv:
        print(json.dumps(out, indent=1, default=str))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    print("RESULT %s: PASS %d of %d checks; %d random boxes certified, %d sample points, 0 unsound; %d boxes with an inertia change, 0 certified; "
          "%d boxes straddling L1+L2=2, 0 certified" % (NAME, COUNT[0], COUNT[0], adv["certified"], adv["sample_points"], adv["straddle_attempts"], st["boxes_tried"]))


if __name__ == "__main__":
    main()
