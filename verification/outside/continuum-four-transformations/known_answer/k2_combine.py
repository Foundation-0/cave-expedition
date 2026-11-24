"""Join the part outputs of K2. usage: k2_combine.py smoke|full <part files...>"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from kcommon import header, summary, parse_mode, sizes
import k2_nothing_in_noise as k2


def main():
    mode = parse_mode(sys.argv)
    sz = sizes(mode)
    ns, nctrl = sz["K2_SEEDS"], (10 if mode == "smoke" else sz["K2_CTRL_SEEDS"])
    counts, tot = {}, {}
    for path in sys.argv[2:]:
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
    header("K2", "nothing found in noise (parts joined)", mode)
    status, text = k2.evaluate(counts, ns, nctrl, mode)
    summary("K2", status, text, mode)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
