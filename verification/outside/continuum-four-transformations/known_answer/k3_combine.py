"""Join the part outputs of K3. usage: k3_combine.py smoke|full <part files...>"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from kcommon import header, summary, parse_mode, sizes
import k3_planted_structure as k3


def main():
    mode = parse_mode(sys.argv)
    ns = sizes(mode)["K3_SEEDS"]
    counts, tot = {}, {}
    for path in sys.argv[2:]:
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
    header("K3", "planted structure found (parts joined)", mode)
    status, text = k3.evaluate(counts, ns)
    summary("K3", status, text, mode)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
