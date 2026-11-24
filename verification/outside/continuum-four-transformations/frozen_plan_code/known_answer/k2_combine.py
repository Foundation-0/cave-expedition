"""Joins the seven K2 part outputs (known_answer/out/k2_part0.txt to k2_part6.txt) into the K2 verdict.
Usage: k2_combine.py <folder with the part files>. No heavy computation."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import calibration, synth
from kcommon import header, summary

NSEED = 200
BOUND = 0.086


def main():
    folder = sys.argv[1]
    header("K2", "nothing found in noise: joined from 7 part outputs, 200 seeds per class")
    rows = {}
    for p in range(7):
        with open(os.path.join(folder, "k2_part%d.txt" % p), encoding="utf-8") as f:
            for line in f:
                if line.startswith("ROW|"):
                    tok = line.strip().split("|")  # class names contain a bar (for example white|exp)
                    c, nrej, nb, nd, sl = "|".join(tok[1:-4]), tok[-4], tok[-3], tok[-2], tok[-1]
                    rows[c] = (int(nrej), int(nb), int(nd), float(sl))
    names = synth.k2_class_names()
    missing = [c for c in names if c not in rows]
    if missing:
        raise SystemExit("missing classes: " + ", ".join(missing))
    print("%-18s %6s %7s %8s %7s" % ("class", "reject", "rate", "flagged", "slope"))
    nflag = 0
    for c in names:
        nrej, nb, nd, sl = rows[c]
        fl = nrej / NSEED > BOUND
        nflag += int(fl)
        print("%-18s %6d %7.3f %8s %7.2f" % (c, nrej, nrej / NSEED, "FLAGGED" if fl else "ok", sl))
    print("classes flagged (rate > %.3f): %d of %d" % (BOUND, nflag, len(names)))
    print("flagged classes:", ", ".join(c for c in names if rows[c][0] / NSEED > BOUND))
    slopes = {c: rows[c][3] for c in names}
    print("slope matching, nearest class by slope among all 21: " + ", ".join("%s -> %s" % (c, calibration.match_class(slopes[c], {k: v for k, v in slopes.items() if k != c})) for c in ("ar1_0.9", "pl_1", "white")) + " (each class matched against the other 20)")
    bw = rows["white"][1] / NSEED
    nbroken = sum(1 for c in names if rows[c][1] / NSEED > BOUND)
    print("--- must-fail control: detector with no correction for the ten lags")
    print("  white class rate %.3f (bound %.3f): %s; classes above the bound: %d of %d" % (bw, BOUND, "FLAGGED" if bw > BOUND else "NOT FLAGGED", nbroken, len(names)))
    ok = (nflag == 0) and bw > BOUND
    summary("K2", "PASS" if ok else "FAIL", "%d of %d classes above the 0.086 bound; must-fail control %s" % (nflag, len(names), "flagged" if bw > BOUND else "NOT flagged"))


if __name__ == "__main__":
    main()
