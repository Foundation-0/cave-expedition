"""Join the part outputs of K2. usage: k2_combine.py smoke [epoch=0] <part files...> | full epoch=<k> <part files...>
The parts must be parts of K2 of the same size and key epoch as this run, from one clean code commit equal to this run's, covering every part
number once (kcommon.check_parts); otherwise nothing is joined and the exit status is 1."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from kcommon import header, summary, parse_cli, sizes, join_parts
import k2_nothing_in_noise as k2


def main():
    run = parse_cli(sys.argv, seeded=True, files=True)
    mode = run["mode"]
    commit = join_parts("K2", run)
    sz = sizes(mode)
    ns, nctrl = sz["K2_SEEDS"], (10 if mode == "smoke" else sz["K2_CTRL_SEEDS"])
    counts, tot = {}, {}
    for path in run["files"]:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("K2COUNT "):
                    _, cls, n, kind, c, t = line.split()
                    key = (cls, int(n), kind)
                    counts[key] = counts.get(key, 0) + int(c)
                    tot[key] = tot.get(key, 0) + int(t)
    bad = [k for k, t in tot.items() if t != (nctrl if k[2] == "raw" else ns)]
    if bad or len(counts) != 2 * len(k2.synth.K2_CLASSES) + 1:
        print("FAIL: parts do not cover every class and seed:", bad)
        raise SystemExit(1)
    header("K2", "nothing found in noise (parts joined)", run, commit)
    status, text = k2.evaluate(counts, ns, nctrl, mode)
    summary("K2", status, text, run)


if __name__ == "__main__":
    main()
