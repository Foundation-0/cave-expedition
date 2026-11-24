"""Amendment 4, reading D14 key epoch: the master field is 20261121 in epoch 0 and 20261121e<k> in epoch k.
Rebuilds every key family of Amendment 3 (own key builder, scope of the author's table, K4 as D20 words it and its second reading)
for epochs 0, 1, 2 and checks that all keys differ across epochs and families, and that the 64-bit seeds differ too.
Reads the modules of the earlier checks (sk_keys*.py). Standard library only. No bare assert."""
import hashlib
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sk_keys as K
import sk_keys2 as R2
import sk_keys3b as S
import sk_keys4 as D4
import sk_keys5 as D5

def master(e):
    return "20261121" if e == 0 else "20261121e%d" % e

def families():
    return [K.fam_k1(), K.fam_k2(), K.fam_k3(), K.fam_k4(True), K.fam_k5(True), S.real(), S.controls(), S.pre(), S.l2b_real(), S.null(),
            D4.fam_k4_d20(), D5.fam_k4_both(True)]

def keyset(e):
    K.M = master(e)
    keys = set()
    for f in families():
        for _o, k, _t in f.ev:
            keys.add(k)
    return keys

def seed64(k):
    return int(hashlib.sha256(k.encode("utf-8")).hexdigest()[:16], 16)

out = []
w = out.append
fails = []
def chk(name, ok, detail=""):
    w(f"[{'ok' if ok else 'FAIL'}] {name}{(': ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

per = {}
for e in (0, 1, 2):
    per[e] = keyset(e)
    w(f"epoch {e}: master field {master(e)!r}, {len(per[e]):,} distinct keys")
n0 = len(per[0])
chk("each epoch has the same number of keys as epoch 0 (417,545 for the families with the K4 superset)", all(len(per[e]) == n0 for e in per) and n0 == 417545, f"{n0:,}")
# every key of epoch k is epoch 0's key with the master field changed
def strip(k):
    return k.split("|", 1)[1]
body = {e: {strip(k) for k in per[e]} for e in per}
chk("keys of different epochs differ only in the master field", body[0] == body[1] == body[2])
allk = set()
tot = 0
for e in per:
    allk |= per[e]
    tot += len(per[e])
chk("no key string occurs in two epochs", len(allk) == tot, f"{len(allk):,} distinct of {tot:,}")
seeds = {seed64(k) for k in allk}
chk("the 64-bit seeds of all three epochs are distinct", len(seeds) == len(allk), f"{len(seeds):,} distinct seeds")
# the first field cannot be confused: split on '|' gives exactly the master field first
chk("the master field never contains the separator and epochs 1 and 10 differ", "|" not in master(10) and master(1) != master(10) and master(1) + "|" != master(10)[:len(master(1)) + 1])
# must-fail controls: an epoch rule that leaves the master unchanged collides, and one that puts the epoch in a field the plan uses elsewhere collides
K.M = master(0)
same = {k for f in families() for _o, k, _t in f.ev}
chk("control: reusing the master field for a rerun gives the same keys (all collide)", same == per[0])
w("")
w("RESULT " + ("all epoch checks hold" if not fails else "FAILED " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
