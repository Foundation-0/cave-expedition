"""Recount of the 420-matrix R_opt comparison, rebuilt from scratch with independent exact code.

Audit: AUDIT-002. Backs, in VERDICTS.md: the chain "rank P >= ... >= R_opt" holding with 0 violations,
and the second-pass ruling that "R_opt >= docs/10 best member" holds on every instance, strictly on 417
of 420, with the integer-certificate gain smaller than the real-number count (202 of 420).

It regenerates 420 matrices with the same random call order as the sibling team's check_003 audit
(seed 20261120), without importing any of that team's code. Ranks and inertia of H_perp are exact
(exactlib_b.py). For each instance it compares R_opt with the best member of the docs/10 family, counts
strict wins, ties and losses, checks n+(H_perp) >= R_opt, and checks the generator's ranks and b.
Exit code 0 only if there are no chain violations, no instance where the docs/10 member exceeds R_opt,
no rank or b mismatch, and only if the counts that ruling spectral/F4 rests on come out as stated:
strict 417, ties 3, integer gain 202, docs/10 positive 15, strict wins with the docs/10 bound negative
402 (203 of them with R_opt = 0), and 7 integer gains over docs/10 combined with the trivial bound 1.

Needs: Python 3 (standard library only). No other repository.
Run (about 2 seconds): python3 -I -B check_recount_420.py
Fixed seed 20261120.
"""
import json
import os
import random
import sys
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import exactlib_b as L  # noqa: E402


def main():
    print("seed: 20261120")
    rng = random.Random(20261120)
    c = dict(total=0, strict=0, ties=0, below=0, strict_ours_neg_ropt0=0, strict_ours_neg=0,
             ours_pos=0, ceil_ropt_gt_ceil_ours=0, ceil_ropt_gt_ceil_ours_with_trivial1=0,
             ropt_pos=0, regime={0: 0, 1: 0, 2: 0}, chain_viol=0, rank_mismatch=0)
    for mode in ("general", "regime1_targeted"):
        for n in (2, 3, 4):
            for _ in range(70):
                if mode == "regime1_targeted":
                    b_true = rng.randint(1, n - 1)
                    r_true = rng.randint(1, n)
                else:
                    r_true = rng.randint(0, n)
                    b_true = rng.randint(0, n)
                UP = L.cayley(n, rng, -2, 2, 2)
                UQ = L.cayley(n, rng, -2, 2, 2)
                pe = []
                for k in range(r_true):
                    pe.append(F(rng.randint(1, 3), rng.randint(2, 5)) if mode == "regime1_targeted"
                              else F(rng.randint(1, 5), rng.randint(1, 3)))
                qe = []
                for k in range(b_true):
                    qe.append(F(rng.randint(8, 12), 2) if mode == "regime1_targeted"
                              else F(rng.randint(1, 5), rng.randint(1, 3)))
                for k in range(b_true, n):
                    qe.append(-F(rng.randint(0, 1), 10) if mode == "regime1_targeted"
                              else -F(rng.randint(0, 5), rng.randint(1, 3)))
                alpha = F(rng.randint(1, 7), rng.randint(1, 4))
                P = L.scal(alpha, L.from_eigs(UP, pe + [F(0)] * (n - r_true)))
                Q = L.scal(alpha, L.from_eigs(UQ, qe))
                H = L.madd(P, Q)
                if L.rank(P) != r_true:
                    c["rank_mismatch"] += 1
                b = L.inertia(Q)[0]
                L.need(b == b_true, "b mismatch")
                u, t, S = L.tr(P), L.tr(Q), L.frob2(H)
                R = L.ropt(u, t, S, b)
                G = L.docs10_best(u, t, S, b)
                # true n_+(H_perp) on W^perp = span of columns b..n-1 of UQ
                if n - b > 0:
                    Up = [[UQ[i][b + j] for j in range(n - b)] for i in range(n)]
                    Hp = L.mmul(L.mmul(L.dag(Up), H), Up)
                    npHp = L.inertia(Hp)[0]
                else:
                    npHp = 0
                if F(npHp) < R:
                    c["chain_viol"] += 1
                c["total"] += 1
                if R > G:
                    c["strict"] += 1
                    if G < 0:
                        c["strict_ours_neg"] += 1
                        if R == 0:
                            c["strict_ours_neg_ropt0"] += 1
                elif R == G:
                    c["ties"] += 1
                else:
                    c["below"] += 1
                c["ours_pos"] += G > 0
                c["ropt_pos"] += R > 0
                if L.cert_int(R) > L.cert_int(G):
                    c["ceil_ropt_gt_ceil_ours"] += 1
                triv = 1 if u > 0 else 0
                if max(triv, L.cert_int(R)) > max(triv, L.cert_int(G)):
                    c["ceil_ropt_gt_ceil_ours_with_trivial1"] += 1
                if u <= 0 or u + t <= 0:
                    c["regime"][0] += 1
                elif b > 0 and t > 0 and t * (u + t) >= b * S:
                    c["regime"][1] += 1
                else:
                    c["regime"][2] += 1
    print(json.dumps(c, indent=1))
    ok = (c["total"] == 420 and c["chain_viol"] == 0 and c["below"] == 0 and c["rank_mismatch"] == 0
          and c["strict"] == 417 and c["ties"] == 3 and c["ceil_ropt_gt_ceil_ours"] == 202
          and c["ours_pos"] == 15 and c["strict_ours_neg"] == 402 and c["strict_ours_neg_ropt0"] == 203
          and c["ceil_ropt_gt_ceil_ours_with_trivial1"] == 7)
    common.finish("check_recount_420", ok,
                  "total=%d strict=%d ties=%d below=%d chain_violations=%d ceil_gain=%d docs10_positive=%d"
                  % (c["total"], c["strict"], c["ties"], c["below"], c["chain_viol"],
                     c["ceil_ropt_gt_ceil_ours"], c["ours_pos"]))


if __name__ == "__main__":
    main()
