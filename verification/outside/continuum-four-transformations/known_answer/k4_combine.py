"""Join part outputs of K4. usage: k4_combine.py smoke|full <part files...>"""
import ast, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from kcommon import header, summary, parse_mode, sizes
import k4_transfer as k4


def main():
    mode = parse_mode(sys.argv)
    ns = sizes(mode)["K4_SEEDS"]
    res = []
    for path in sys.argv[2:]:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("K4SEED "):
                    res.append(ast.literal_eval(line[len("K4SEED "):]))
    if sorted(r["seed"] for r in res) != list(range(ns)):
        print("FAIL: parts do not cover seeds 0 to %d" % (ns - 1))
        raise SystemExit(1)
    header("K4", "transfer (parts joined)", mode)
    status, text = k4.evaluate(res, ns, mode)
    summary("K4", status, text, mode)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
