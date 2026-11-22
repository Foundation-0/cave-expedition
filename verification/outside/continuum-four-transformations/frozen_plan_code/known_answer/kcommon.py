import sys
import numpy as np
import seeds


def header(tid, title):
    print("TEST", tid, "-", title)
    print("python", sys.version.split()[0], "numpy", np.__version__)
    print("master seed", seeds.MASTER, "| seed rule: first 16 hex digits of SHA-256 of", seeds.seed_string("<instrument>", "<split>", "<net>", "<segment>", "<purpose>", "<index>"))


def summary(tid, status, text):
    print("SUMMARY", tid, status, "|", text)
