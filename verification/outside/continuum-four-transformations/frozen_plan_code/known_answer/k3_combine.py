"""Joins the three K3 part outputs (k3_part0.txt to k3_part2.txt) into the K3 verdict. Usage: k3_combine.py <folder>."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import synth
from kcommon import header, summary

NSEED = 200


def main():
    folder = sys.argv[1]
    header("K3", "planted structure found: joined from 3 part outputs, 200 seeds per case")
    rows = {}
    for p in range(3):
        with open(os.path.join(folder, "k3_part%d.txt" % p), encoding="utf-8") as f:
            for line in f:
                if line.startswith("ROW|"):
                    _, c, n, nd, need = line.strip().split("|")
                    rows[(c, n)] = (int(nd), float(need))
    allpass = True
    flagged_all = True
    print("%-10s %-8s %7s %7s %6s %8s" % ("case", "net", "detect", "rate", "need", "result"))
    for c in synth.K3_CASES:
        for n in ("native", "bm2", "whiten"):
            nd, need = rows[(c, n)]
            ok = nd / NSEED >= need
            allpass = allpass and ok
            print("%-10s %-8s %7d %7.3f %6.2f %8s" % (c, n, nd, nd / NSEED, need, "PASS" if ok else "FAIL"))
    print("--- must-fail control: surrogate generator that leaks the time arrow, native net")
    for c in synth.K3_CASES:
        nd, need = rows[(c, "leaky")]
        fl = nd / NSEED < need
        flagged_all = flagged_all and fl
        print("%-10s leaky    %7d %7.3f  need>=%.2f -> %s" % (c, nd, nd / NSEED, need, "FLAGGED (below criterion)" if fl else "NOT FLAGGED"))
    summary("K3", "PASS" if (allpass and flagged_all) else "FAIL", "detection criteria %s; leaky-surrogate control %s" % ("all met" if allpass else "NOT all met", "flagged in all cases" if flagged_all else "NOT flagged in all cases"))


if __name__ == "__main__":
    main()
