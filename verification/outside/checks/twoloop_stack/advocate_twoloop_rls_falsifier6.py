#!/usr/bin/env python3
"""Check script advocate_twoloop_rls_falsifier6.py: AUDIT-005 (two_loop_omitted_variable.py), advocate's re-check with its own code.

Backs: VERDICTS.md section 2, 'Two-loop law (005): N0 identity, N1 application' (identity 1 equals textbook restricted least squares); section 3, 'continuum 3, two-loop' (exact tie at x = 0 and x = 2, does not settle Claim 9: a partial revision hurts a fresh anchor, a wrong revision lowers the in-sample residual and raises the error against the truth); section 4 item 1 (Falsifier 6 miscalibrated: the outside part of the residual is unchanged while same-kind fresh anchors still improve).
Needs: python3 (3.10 or newer). No network, no clone of any repository, no input files.
Run: python3 -I -B advocate_twoloop_rls_falsifier6.py
     (also python3 -I -O -B advocate_twoloop_rls_falsifier6.py and python3 -I -B -W error advocate_twoloop_rls_falsifier6.py, same output)
Time: about 1 second.
Every failed check raises CheckFailed and the script exits 1. On success the last
line printed starts with RESULT: PASS and the exit code is 0.
Seeds (fixed, printed in the output): 4242 (part 1), 9191 (part 4).

Original description:
Advocate re-check of AUDIT-005 (two_loop_omitted_variable.py). Own code, no imports from team or evaluator.

Part 1 (F1): the team's absorption step against the textbook restricted least squares (RLS) route, term by term:
    X = Phi, Y = y, R = a1^T Phi (1 x k), r = a1^T y,
    beta_r = beta_hat - (X'X)^-1 R' [R (X'X)^-1 R']^-1 (R beta_hat - r),
    RSS_r = RSS_ur + (R beta_hat - r)' [R (X'X)^-1 R']^-1 (R beta_hat - r).
Part 2 (F3): the boundary points x = 0 and x = 2 are ties.
Part 3 (F2): the team's own noiseless revision statement, then per-anchor and noisy counterpoints.
Part 4 (missed): in the team's noiseless model, absorption passes same-kind fresh anchors while the outside gap
    (I - P) r is exactly unchanged and the total residual grows; so Falsifier 6's inference
    "then absorbing the anchor closed the real gap" is false in the model.
Every failed check raises CheckFailed. Run: python3 -I -B check_twoloop.py (also -O, -W error).
"""
import json
import random
import sys
from fractions import Fraction as Fr


class CheckFailed(Exception):
    pass


def need(c, msg):
    if not c:
        raise CheckFailed(msg)


def dot(u, v):
    return sum((a * b for a, b in zip(u, v)), Fr(0))


def mv(M, x):
    return [dot(row, x) for row in M]


def tr(M):
    return [list(c) for c in zip(*M)]


def mm(A, B):
    Bt = tr(B)
    return [[dot(r, c) for c in Bt] for r in A]


def sub(u, v):
    return [a - b for a, b in zip(u, v)]


def sc(c, u):
    return [c * a for a in u]


def inv(A):
    n = len(A)
    M = [list(A[i]) + [Fr(int(i == j)) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            raise CheckFailed("singular")
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def proj(X, v):
    XtX_inv = inv(mm(tr(X), X))
    return mv(X, mv(XtX_inv, mv(tr(X), v)))


def full_rank_instance(rng, m, k, d):
    while True:
        X = [[Fr(rng.randint(-3, 3)) for _ in range(k)] for _ in range(m)]
        try:
            inv(mm(tr(X), X))
            break
        except CheckFailed:
            continue
    Psi = [[Fr(rng.randint(-3, 3)) for _ in range(d)] for _ in range(m)]
    return X, Psi


def part1(seed, trials=150):
    rng = random.Random(seed)
    n = 0
    for _ in range(trials):
        m = rng.randint(5, 8)
        k = rng.randint(1, min(4, m - 2))
        X, Psi = full_rank_instance(rng, m, k, rng.randint(1, 3))
        th = [Fr(rng.randint(-3, 3)) for _ in range(k)]
        be = [Fr(rng.randint(-3, 3)) for _ in range(len(Psi[0]))]
        y = [a + b for a, b in zip(mv(X, th), mv(Psi, be))]
        if rng.random() < 0.5:
            y = [v + Fr(rng.randint(-4, 4), 3) for v in y]
        a1 = [Fr(rng.randint(-3, 3)) for _ in range(m)]
        XtX_inv = inv(mm(tr(X), X))
        bhat = mv(XtX_inv, mv(tr(X), y))
        rstar = sub(y, mv(X, bhat))
        p1 = proj(X, a1)
        e1 = dot(a1, rstar)
        pp = dot(p1, p1)
        if pp == 0 or e1 == 0:
            continue
        # team route
        r_adapt = sub(rstar, sc(e1 / pp, p1))
        # textbook RLS route, independent of the team's formula
        R = mv(tr(X), a1)               # R' as a k-vector (R = a1^T X)
        r_rhs = dot(a1, y)
        viol = dot(R, bhat) - r_rhs      # R beta_hat - r
        RXR = dot(R, mv(XtX_inv, R))     # R (X'X)^-1 R'
        b_r = sub(bhat, sc(viol / RXR, mv(XtX_inv, R)))
        e_r = sub(y, mv(X, b_r))
        RSS_r_formula = dot(rstar, rstar) + viol * viol / RXR
        need(viol == -e1, "R beta_hat - r must equal -e1")
        need(RXR == pp, "R (X'X)^-1 R' must equal |p1|^2")
        need(e_r == r_adapt, "restricted residual must equal r_adapt")
        need(dot(e_r, e_r) == RSS_r_formula, "RSS_r formula")
        need(dot(r_adapt, r_adapt) == dot(rstar, rstar) + e1 * e1 / pp, "team identity 1")
        need(dot(a1, e_r) == 0, "constraint holds")
        n += 1
    need(n >= 60, "too few instances")
    return {"instances": n, "with_noise_or_not": "mixed", "rls_equals_team_route": True}


def part2():
    # orthonormal toy: col(Phi) = span(u0, u1), r* = 5 u2, a1 = u0 + u2
    def u(i, m=5):
        return [Fr(int(i == j)) for j in range(m)]
    r = sc(Fr(5), u(2))
    a1 = [x + y for x, y in zip(u(0), u(2))]
    p1 = u(0)
    e1, pp = dot(a1, r), dot(p1, p1)
    ra = sub(r, sc(e1 / pp, p1))
    rows = []
    for alpha in (Fr(-1), Fr(0), Fr(1, 2), Fr(1), Fr(2), Fr(3)):
        a2 = [alpha * x + y for x, y in zip(u(0), u(2))]
        e2, post = dot(a2, r), dot(a2, ra)
        x = (dot(p1, a2) / pp) / (e2 / e1)
        need(post == e2 * (1 - x), "identity 2")
        rows.append({"x": str(x), "before_sq": str(e2 * e2), "after_sq": str(post * post),
                     "verdict": "helps" if post * post < e2 * e2 else ("tie" if post * post == e2 * e2 else "hurts")})
    need([r_["verdict"] for r_ in rows if r_["x"] in ("0", "2")] == ["tie", "tie"], "ties at 0 and 2")
    return rows


def part3():
    def u(i, m=5):
        return [Fr(int(i == j)) for j in range(m)]
    r = sc(Fr(5), u(2))
    # team's noiseless revision: adding v_part = 3/5 u2 + 4/5 u3 (already orthogonal to col Phi)
    v = [Fr(3, 5) * a + Fr(4, 5) * b for a, b in zip(u(2), u(3))]
    r_rev = sub(r, sc(dot(r, v), v))
    out = {"norm2_r_star": str(dot(r, r)), "norm2_r_rev_partial": str(dot(r_rev, r_rev))}
    need(dot(r_rev, r_rev) == 16, "team's 25 -> 16")
    a2 = sub(u(2), u(3))
    out["fresh_anchor_u2_minus_u3_before_after"] = [str(dot(a2, r) ** 2), str(dot(a2, r_rev) ** 2)]
    need(dot(a2, r_rev) ** 2 > dot(a2, r) ** 2, "partial revision hurts this fresh anchor (noiseless)")
    # wrong revision, noiseless: direction orthogonal to r*: r_rev == r*, no change
    w = u(3)
    r_wrong = sub(r, sc(dot(r, w), w))
    need(r_wrong == r, "noiseless wrong revision leaves residual unchanged")
    out["noiseless_wrong_revision_changes_residual"] = False
    # noisy: y = g + eps, Phi = [1,1,0,0]^T, truth g = 2 e2, wrong revision adds e3
    Phi = [[Fr(1)], [Fr(1)], [Fr(0)], [Fr(0)]]
    g = [Fr(0), Fr(0), Fr(2), Fr(0)]
    eps = [Fr(1, 3), Fr(-1, 2), Fr(1, 5), Fr(3, 4)]
    y = [a + b for a, b in zip(g, eps)]
    fit1 = proj(Phi, y)
    Phi2 = [row + [Fr(int(i == 3))] for i, row in enumerate(Phi)]
    fit2 = proj(Phi2, y)
    err1, err2 = sub(g, fit1), sub(g, fit2)
    res1, res2 = sub(y, fit1), sub(y, fit2)
    need(dot(res2, res2) < dot(res1, res1), "in-sample residual falls")
    need(dot(err2, err2) > dot(err1, err1), "error against truth rises")
    out["noisy_wrong_revision"] = {"in_sample": [str(dot(res1, res1)), str(dot(res2, res2))],
                                   "vs_truth": [str(dot(err1, err1)), str(dot(err2, err2))]}
    return out


def part4(seed, trials=200):
    """Falsifier 6 miscalibration in the team's own noiseless model."""
    rng = random.Random(seed)
    n = 0
    fires = 0
    for _ in range(trials):
        m = rng.randint(5, 8)
        k = rng.randint(1, min(3, m - 2))
        X, Psi = full_rank_instance(rng, m, k, rng.randint(1, 2))
        th = [Fr(rng.randint(-3, 3)) for _ in range(k)]
        be = [Fr(rng.randint(-3, 3)) for _ in range(len(Psi[0]))]
        y = [a + b for a, b in zip(mv(X, th), mv(Psi, be))]
        rstar = sub(y, proj(X, y))
        a1 = [Fr(rng.randint(-3, 3)) for _ in range(m)]
        p1 = proj(X, a1)
        e1, pp = dot(a1, rstar), dot(p1, p1)
        if pp == 0 or e1 == 0:
            continue
        ra = sub(rstar, sc(e1 / pp, p1))
        # the part of the error outside col(Phi) (the "real gap") is exactly unchanged
        outside_after = sub(ra, proj(X, ra))
        need(outside_after == rstar, "outside gap unchanged by absorption")
        need(dot(ra, ra) > dot(rstar, rstar), "total residual strictly grows")
        # fresh anchors of the same kind: small integer perturbations of a1
        same = [[a + Fr(rng.randint(-1, 1), 4) for a in a1] for _ in range(12)]
        before = sum((dot(a, rstar) ** 2 for a in same), Fr(0))
        after = sum((dot(a, ra) ** 2 for a in same), Fr(0))
        if after < before:
            fires += 1
        n += 1
    need(n >= 80, "too few")
    need(fires >= n // 2, "same-kind anchors should improve in most instances here")
    return {"instances": n, "same_kind_ensemble_improves_after_absorption": fires,
            "outside_gap_unchanged_in_all": True, "total_residual_grew_in_all": True}


def main():
    out = {"part1_rls": part1(4242), "part2_boundary": part2(), "part3_revision": part3(),
           "part4_falsifier6": part4(9191)}
    print("seeds: part1=4242 part4=9191")
    print(json.dumps(out, indent=1))
    print("RESULT: PASS advocate_twoloop_rls_falsifier6: %d instances match textbook restricted least squares, ties at x=0 and x=2, partial and wrong revisions behave as stated, outside gap unchanged in all %d Falsifier 6 instances (%d of them show same-kind anchors improving)"
          % (out["part1_rls"]["instances"], out["part4_falsifier6"]["instances"], out["part4_falsifier6"]["same_kind_ensemble_improves_after_absorption"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckFailed as exc:
        print("RESULT: FAIL (%s)" % exc)
        sys.exit(1)
