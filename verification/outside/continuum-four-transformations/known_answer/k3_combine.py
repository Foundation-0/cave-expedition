"""Join the part outputs of K3. usage: k3_combine.py smoke [epoch=0] <part files...> | full epoch=<k> <part files...>
The parts must be parts of K3 of the same size and key epoch as this run, from one clean code commit equal to this run's, covering every part
number once (kcommon.check_parts); otherwise nothing is joined and the exit status is 1."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from kcommon import header, summary, parse_cli, sizes, join_parts
import k3_planted_structure as k3


def main():
    run = parse_cli(sys.argv, seeded=True, files=True)
    commit = join_parts("K3", run)
    ns = sizes(run["mode"])["K3_SEEDS"]
    counts, tot = {}, {}
    for path in run["files"]:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("K3COUNT "):
                    _, case, use, kind, c, t = line.split()
                    key = (case, use, kind)
                    counts[key] = counts.get(key, 0) + int(c)
                    tot[key] = tot.get(key, 0) + int(t)
    bad = [k for k, t in tot.items() if t != ns]
    if bad or len(counts) != len(k3.synth.K3_CASES) * len(k3.USES) + 1:
        print("FAIL: parts do not cover every cell and seed:", bad)
        raise SystemExit(1)
    header("K3", "planted structure found (parts joined)", run, commit)
    status, text = k3.evaluate(counts, ns)
    summary("K3", status, text, run)


if __name__ == "__main__":
    main()
