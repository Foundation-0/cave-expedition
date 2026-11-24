"""Sandboxed driver: loads the untouched upstream files by path and calls their own functions.
It never writes files. Run only via sbx.sh. Usage: up_driver.py <pr106 folds dir> <pr107 sheaf dir>
"""
import importlib.util
import hashlib
import json
import sys
from fractions import Fraction


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) != 3:
        print("usage: up_driver.py <folds dir> <sheaf dir>")
        return 2
    folds = load("e8fold", sys.argv[1] + "/verify_e8_spinor_fold.py")
    sheaf = load("sheaf", sys.argv[2] + "/fold_sheaf_collapse.py")

    # --- AUDIT-019 function at n = 8 (twisted cycle C_8), as called by upstream for n = 3..7
    C8 = sheaf.make_twisted_cycle_Cn(8)
    for (a, t) in [(Fraction(0), Fraction(1)), (Fraction(4, 3), Fraction(1, 3)), (Fraction(8, 9), Fraction(7, 9))]:
        r = sheaf.compute_fold_sheaf_elastic(C8, a, t)
        print("UP_D8_TWISTED", json.dumps(r, sort_keys=True))
    print("UP_D8_rk_M_rot", sheaf.rotational_locking_rank(C8))
    # --- same upstream function fed the Hadamard matrix (1/2) H_8 at (a, t) = (0, 1)
    H8 = [[1]]
    for _ in range(3):
        H8 = [r + r for r in H8] + [r + [-x for x in r] for r in H8]
    Chad = [[Fraction(x, 2) for x in r] for r in H8]
    r = sheaf.compute_fold_sheaf_elastic(Chad, Fraction(0), Fraction(1))
    print("UP_E8_HADAMARD_s1", json.dumps(r, sort_keys=True))

    # --- AUDIT-017 verifier: same calls as its main(), minus the certificate write
    H = folds.build_sylvester_H8()
    r14 = folds.verify_lemmas_1_to_4(H)
    r5 = folds.verify_lemma_5_bernstein_and_kissing(H, R2_cutoff=11)
    r6 = folds.verify_lemma_6_uniqueness()
    rg = folds.verify_b8_gauge_invariance(H)
    rc = folds.run_must_fail_controls(H)
    cert = {
        "theorem": "Canonical Sylvester-Hadamard Continuous Bar-Preserving Fold F_8 -> E_8 + E_6/E_7/D_n^+ Uniqueness",
        "status": "ALL_EXACT_CHECKS_PASS",
        "oracle": "exact",
        "arithmetic": "zero-float pure Python stdlib (int, Fraction, Z[sqrt(2)])",
        "sylvester_H8": H,
        "lemmas_1_to_4": r14,
        "lemma_5_bernstein_and_kissing": r5,
        "lemma_6_uniqueness_obstruction": r6,
        "b8_gauge_invariance": rg,
        "must_fail_controls": rc,
    }
    canon = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    print("UP_E8_CERT_SHA256", hashlib.sha256(canon.encode("utf-8")).hexdigest())
    print("UP_E8_PAIRS", r5["total_pairs"], r5["total_degree8_bernstein_coeffs"], r5["zero_coeffs_total"], r5["negative_pairs"])
    print("UP_E8_CONTROLS_REJECTED", len(rc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
