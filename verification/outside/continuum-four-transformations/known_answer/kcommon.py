"""Shared helpers of the known-answer scripts: header, size labelling (SMOKE or FULL), checks without bare assert."""
import os
import sys
import numpy as np
import seeds

FULL = {"K1_SEEDS": 20, "K2_SEEDS": 1000, "K2_CTRL_SEEDS": 200, "K3_SEEDS": 200, "K4_SEEDS": 10, "K5_SEEDS": 10}
SMOKE_DIV = 20
SMOKE_MIN = 10


def sizes(mode):
    """mode 'full' or 'smoke'. Smoke is one twentieth of the plan's seeds, at least 10, the same seed rule."""
    if mode == "full":
        return dict(FULL)
    if mode == "smoke":
        return {k: max(SMOKE_MIN, v // SMOKE_DIV) for k, v in FULL.items()}
    raise ValueError("size must be 'smoke' or 'full'")


def parse_mode(argv):
    if len(argv) < 2 or argv[1] not in ("smoke", "full"):
        print("usage: <script> smoke|full [part nparts]")
        raise SystemExit(2)
    return argv[1]


def label(mode):
    return "SMOKE (one twentieth of the plan's seeds, at least 10; NOT a result)" if mode == "smoke" else "FULL"


def header(tid, title, mode):
    print("TEST", tid, "-", title)
    print("SIZE", label(mode))
    print("python", sys.version.split()[0], "numpy", np.__version__)
    print("master seed", seeds.MASTER, "| seed rule: first 16 hex digits of SHA-256 of", seeds.seed_string("<instrument>", "<split>", "<net>", "<segment>", "<purpose>", "<index>"))


def summary(tid, status, text, mode):
    print("SUMMARY", tid, ("SMOKE " if mode == "smoke" else "") + status, "|", text)


class Checker:
    """Collects checks. Never uses assert. fail() count decides the exit status."""

    def __init__(self):
        self.n = 0
        self.failed = []

    def check(self, name, cond):
        self.n += 1
        if not bool(cond):
            self.failed.append(name)
            print("  FAIL", name)
        return bool(cond)

    def eq(self, name, a, b):
        ok = (a == b)
        if isinstance(ok, np.ndarray):
            ok = bool(ok.all()) and np.shape(a) == np.shape(b)
        return self.check(name, ok)

    def done(self, tag):
        print("%s: %d checks, %d failed" % (tag, self.n, len(self.failed)))
        return len(self.failed) == 0
