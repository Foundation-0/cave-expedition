"""Join part outputs of K5. usage: k5_combine.py smoke|full <part files...>"""
import ast, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from kcommon import header, summary, parse_mode, sizes
import k5_transfer as k5


def main():
    mode = parse_mode(sys.argv)
    ns = sizes(mode)["K5_SEEDS"]
    res = []
    for path in sys.argv[2:]:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("K5SEED "):
                    res.append(ast.literal_eval(line[len("K5SEED "):]))
    if sorted(r["seed"] for r in res) != list(range(ns)):
        print("FAIL: parts do not cover seeds 0 to %d" % (ns - 1))
        raise SystemExit(1)
    header("K5", "transfer (parts joined)", mode)
    status, text = k5.evaluate(res, ns, mode)
    summary("K5", status, text, mode)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
