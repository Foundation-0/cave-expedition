"""Ledger of the key epochs each known-answer test has used, and the rule a full-count run must meet (PREREG section 10, repair rule, and
reading D14 as amended by Amendment 4).

known_answer/EPOCHS.tsv has a header line and one row per run that used an epoch of a test, with six tab-separated fields:
    test        K1 to K5 (K6 has no random draws and is exempt from the epoch rule, so it has no rows)
    epoch       a whole number; 0 is the diagnostic epoch of smoke runs and of every run before Amendment 4 was carried out
    code_commit the full or short commit of the code that ran, or - when it is not known
    date        the start date of the run, YYYY-MM-DD
    kind        full-count (a run at the plan's full seed count, with its must-fail controls), diagnostic (only on epoch 0), law2b-check
                (a Law 2b pre-data check that reuses the test's draws on that epoch) or draws-seen (only from epoch 1: an outcome of some
                other run that used the same data draws as that epoch, even under other surrogate or detector keys, was seen)
    note        free text without tabs
Epochs belong to one test: a row uses that epoch for that test only. A test has used an epoch if any row names that test and epoch.
A full-count run of a test uses the lowest epoch from 1 that the test has not used, and every rerun after a full-count outcome uses a new
epoch. So a full-count run is refused on epoch 0, on an epoch the test has used, and on any epoch other than the lowest unused one from 1.
Several ledger files can be read as one: the rows of each are joined, a row that appears in more than one file counts once, and the
joined rows must meet every rule (so two different full-count rows for one test and epoch are refused).
usage: epochs.py next <test> [<ledger file> ...]              print the lowest epoch from 1 that the test has not used
       epochs.py check <test> <epoch> [<ledger file> ...]     exit status 0 if a full-count run of the test may use this epoch, else 1
                                                               with the reason
       (the ledger read is the EPOCHS.tsv beside this file, joined with each ledger file named, for example the ledger of the runs
       started from a build folder that run_full.sh keeps)"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "EPOCHS.tsv")
HEADER = ("test", "epoch", "code_commit", "date", "kind", "note")
SEEDED = ("K1", "K2", "K3", "K4", "K5")
KINDS = ("full-count", "diagnostic", "law2b-check", "draws-seen")
USAGE = "usage: epochs.py next <test> [<ledger file> ...] | epochs.py check <test> <epoch> [<ledger file> ...]"


class LedgerError(ValueError):
    pass


def _rows_of(text, where):
    """The rows of one ledger text as tuples of six strings, after the checks that need only one row."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines or tuple(lines[0].split("\t")) != HEADER:
        raise LedgerError("%sthe first line must be the header: %s" % (where, "\\t".join(HEADER)))
    out = []
    for no, line in enumerate(lines[1:], start=2):
        f = line.split("\t")
        if len(f) != len(HEADER):
            raise LedgerError("%sline %d: %d fields, need %d" % (where, no, len(f), len(HEADER)))
        test, epoch, commit, date, kind, note = f
        if test == "K6":
            raise LedgerError("%sline %d: K6 has no random draws and is exempt from the epoch rule" % (where, no))
        if test not in SEEDED:
            raise LedgerError("%sline %d: unknown test %r" % (where, no, test))
        if not re.fullmatch(r"0|[1-9][0-9]*", epoch):
            raise LedgerError("%sline %d: the epoch must be a whole number, got %r" % (where, no, epoch))
        e = int(epoch)
        if commit != "-" and not re.fullmatch(r"[0-9a-f]{7,40}", commit):
            raise LedgerError("%sline %d: the code commit must be a hex commit or -, got %r" % (where, no, commit))
        if not re.fullmatch(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", date):
            raise LedgerError("%sline %d: the date must be YYYY-MM-DD, got %r" % (where, no, date))
        if kind not in KINDS:
            raise LedgerError("%sline %d: kind must be one of %s" % (where, no, ", ".join(KINDS)))
        if e == 0 and kind != "diagnostic":
            raise LedgerError("%sline %d: a run on epoch 0 is a diagnostic and cannot be a %s row" % (where, no, kind))
        if e > 0 and kind == "diagnostic":
            raise LedgerError("%sline %d: a diagnostic (smoke) run uses epoch 0, not epoch %d" % (where, no, e))
        out.append((test, epoch, commit, date, kind, note))
    return out


def parse_ledgers(texts):
    """Rows of one or more ledger texts read as one ledger, as dicts with the epoch as an int. A row of one text that an earlier text
    already holds counts once; within one text every row counts. Refuses a ledger that breaks any rule of the module text, also across
    the texts."""
    rows, seen, full = [], set(), set()
    for k, text in enumerate(texts):
        where = "" if len(texts) == 1 else "ledger %d, " % (k + 1)
        mine = _rows_of(text, where)
        before = set(seen)
        seen.update(mine)
        for r in mine:
            if r in before:
                continue
            test, epoch, commit, date, kind, note = r
            e = int(epoch)
            if kind == "full-count":
                if (test, e) in full:
                    raise LedgerError("%s has two full-count runs on epoch %d; a rerun uses a new epoch" % (test, e))
                full.add((test, e))
            rows.append({"test": test, "epoch": e, "code_commit": commit, "date": date, "kind": kind, "note": note})
    return rows


def parse_ledger(text):
    """Rows of one ledger text (see parse_ledgers)."""
    return parse_ledgers([text])


def used_epochs(rows, test):
    """The epochs the test has used (any kind of row)."""
    return {r["epoch"] for r in rows if r["test"] == test}


def next_epoch(rows, test):
    """The lowest epoch from 1 that the test has not used."""
    if test not in SEEDED:
        raise LedgerError("%s is not a seeded known-answer test (K6 has no random draws and no epoch)" % (test,))
    used = used_epochs(rows, test)
    k = 1
    while k in used:
        k += 1
    return k


def check_full_run(rows, test, epoch):
    """The reason a full-count run of the test may not use this epoch, or None when it may."""
    if test == "K6":
        return "K6 has no random draws and is exempt from the epoch rule: run it without an epoch"
    if test not in SEEDED:
        return "unknown test %r" % (test,)
    if isinstance(epoch, bool) or not isinstance(epoch, int):
        return "the epoch must be an int"
    if epoch < 1:
        return "epoch %d is a diagnostic epoch: a full-count run uses an epoch from 1" % epoch
    if epoch in used_epochs(rows, test):
        return "%s has used epoch %d already: every rerun uses a new epoch" % (test, epoch)
    nxt = next_epoch(rows, test)
    if epoch != nxt:
        return "%s must use the lowest epoch from 1 it has not used, which is %d, not %d" % (test, nxt, epoch)
    return None


def read_ledger(path=LEDGER, extra=()):
    """The rows of the ledger file at path, joined with those of each file in extra (see parse_ledgers)."""
    texts = []
    for p in (path,) + tuple(extra):
        with open(p, "r", encoding="utf-8") as fh:
            texts.append(fh.read())
    return parse_ledgers(texts)


def main(argv):
    try:
        if len(argv) >= 3 and argv[1] == "next":
            rows = read_ledger(extra=argv[3:])
            print(next_epoch(rows, argv[2]))
            return 0
        if len(argv) >= 4 and argv[1] == "check":
            if not re.fullmatch(r"0|[1-9][0-9]*", argv[3]):
                print("REFUSED: the epoch must be a whole number written in digits, got %r" % argv[3])
                return 1
            rows = read_ledger(extra=argv[4:])
            why = check_full_run(rows, argv[2], int(argv[3]))
            if why is not None:
                print("REFUSED:", why)
                return 1
            print("ok: a full-count run of %s may use epoch %s" % (argv[2], argv[3]))
            return 0
    except (OSError, LedgerError) as e:
        print("REFUSED:", e)
        return 1
    print(USAGE)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
