"""Join part outputs of K4. usage: k4_combine.py smoke [epoch=0] <part files...> | full epoch=<k> <part files...>
The parts must be parts of K4 of the same size and key epoch as this run, from one clean code commit equal to this run's, covering every part
number once (kcommon.check_parts); otherwise nothing is joined and the exit status is 1."""
import ast, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from kcommon import header, summary, parse_cli, sizes, join_parts
import k4_transfer as k4


def main():
    run = parse_cli(sys.argv, seeded=True, files=True)
    commit = join_parts("K4", run)
    ns = sizes(run["mode"])["K4_SEEDS"]
    res = []
    for path in run["files"]:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("K4SEED "):
                    res.append(ast.literal_eval(line[len("K4SEED "):]))
    if sorted(r["seed"] for r in res) != list(range(ns)):
        print("FAIL: parts do not cover seeds 0 to %d" % (ns - 1))
        raise SystemExit(1)
    header("K4", "transfer (parts joined)", run, commit)
    status, text = k4.evaluate(res, ns)
    summary("K4", status, text, run)


if __name__ == "__main__":
    main()
