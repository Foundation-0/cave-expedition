"""Epoch-0 diagnostic (DIAGNOSIS_EPOCH0.md): the K2 must-fail control and the K3 circular-shift control, 200 seeds each, per seed. Changes no code under test.
Prints, per seed, the segment p numerators (p = pn / 100, a segment rejects when pn <= 5), and counts at 10, 20, 50, 100 and 200 seeds.
usage: diag_controls.py"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src")); sys.path.insert(0, HERE)
import par
import diag_tasks as dt

NS = 200


def counts(pns):
    return {n: sum(1 for p in pns[:n] if p <= 5) for n in (10, 20, 50, 100, 200)}


def main():
    jobs = []
    names = []
    for label, task, mk in (
        ("K2 control: raw-value surrogates, default pool key", dt.k2_control_task, lambda i: (i, "raw", "default")),
        ("K2 control: raw-value surrogates, alternative pool key", dt.k2_control_task, lambda i: (i, "raw", "alt")),
        ("K2 same series: normal-score surrogates (the plan's method), default pool key", dt.k2_control_task, lambda i: (i, "iaaft", "default")),
        ("K3 control: circular shifts on shots native4096, default pool key", dt.k3_task, lambda i: ("shots", "native4096", i, "leaky", "default")),
        ("K3 control: circular shifts on shots native4096, alternative pool key", dt.k3_task, lambda i: ("shots", "native4096", i, "leaky", "alt")),
        ("K3 same series: normal-score surrogates (detection of the planted shots), default pool key", dt.k3_task, lambda i: ("shots", "native4096", i, "iaaft", "default")),
    ):
        res = par.pmap(task, [mk(i) for i in range(NS)])
        pns = [r["pn"] for r in res]
        c = counts(pns)
        print("%s" % label)
        print("  rejecting segments (p <= 0.05) at 10, 20, 50, 100, 200 seeds: %s" % ", ".join("%d" % c[n] for n in (10, 20, 50, 100, 200)))
        print("  pn per seed 0 to 199: %s" % " ".join(str(p) for p in pns))
    par.close()


if __name__ == "__main__":
    main()
