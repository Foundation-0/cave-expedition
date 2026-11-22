"""Writes the canonical object documents. Usage: python3 -I -B build_objects.py <objects_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from suite import object_documents, sha  # noqa: E402


def main():
    odir = sys.argv[1]
    docs = object_documents()
    for fn in sorted(docs):
        with open(os.path.join(odir, fn), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(docs[fn])
        print("wrote %s sha256=%s bytes=%d" % (fn, sha(docs[fn]), len(docs[fn].encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
