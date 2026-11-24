"""Third pass: epochs belong to one test. Keys of known-answer tests take the master field of their own test's epoch, real-data keys keep epoch 0.
Checks several mixed assignments (K1 to K5 on different epochs at once): all keys distinct within a run, 64-bit seeds distinct, and every
key of a test sits in that test's epoch only. Reuses the key builders of the earlier checks. Standard library only. No bare assert."""
import hashlib
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sk_keys as K
import sk_keys3b as S
import sk_keys4 as D4
import sk_keys5 as D5

out = []
w = out.append
fails = []
def chk(name, ok, detail=""):
    w(f"[{'ok' if ok else 'FAIL'}] {name}{(': ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

K.M = "20261121"
fams = [K.fam_k1(), K.fam_k2(), K.fam_k3(), K.fam_k4(True), K.fam_k5(True), S.real(), S.controls(), S.pre(), S.l2b_real(), S.null(), D4.fam_k4_d20(), D5.fam_k4_both(True)]
bodies = set()
for f in fams:
    for _o, k, _t in f.ev:
        bodies.add(k.split("|", 1)[1])
chk("epoch 0 keys, bodies without the master field", len(bodies) == 417545, f"{len(bodies):,}")
def test_of(body):
    inst = body.split("|", 1)[0]
    if inst.startswith("K1") :
        return "K1"
    if inst.startswith("K2:"):
        return "K2"
    if inst.startswith("K3:"):
        return "K3"
    if inst.startswith("K4:"):
        return "K4"
    if inst.startswith("K5b:"):
        return "K5"
    return "real"
by = {}
for b in bodies:
    by.setdefault(test_of(b), []).append(b)
w("   keys per test: " + ", ".join(f"{t} {len(v):,}" for t, v in sorted(by.items())))
chk("every instrument tag belongs to exactly one test or to real data", sum(len(v) for v in by.values()) == len(bodies))
def master(k):
    return "20261121" if k == 0 else "20261121e%d" % k
assignments = [dict(K1=1, K2=1, K3=1, K4=1, K5=1), dict(K1=1, K2=2, K3=1, K4=3, K5=1), dict(K1=2, K2=3, K3=2, K4=2, K5=3), dict(K1=0, K2=1, K3=0, K4=1, K5=0)]
for a in assignments:
    keys = []
    for t, v in by.items():
        m = master(a.get(t, 0))
        keys += [m + "|" + b for b in v]
    seeds = {int(hashlib.sha256(k.encode()).hexdigest()[:16], 16) for k in keys}
    chk(f"mixed epochs {a}: keys distinct, seeds distinct", len(set(keys)) == len(keys) == 417545 and len(seeds) == 417545)
# a Law 2b pre-data key follows the epoch of the test it reuses
pre_keys = [k for _o, k, _t in S.pre().ev]
tests_in_pre = {test_of(k.split("|", 1)[1]) for k in pre_keys}
chk("the Law 2b pre-data checks draw only from K2, K3, K4 and K5 instrument tags", tests_in_pre == {"K2", "K3", "K4", "K5"}, str(sorted(tests_in_pre)))
real_keys = [k for f in (S.real(), S.l2b_real(), S.null(), S.controls()) for _o, k, _t in f.ev]
chk("real-data keys, controls, Law 2b real-data tests and null replicates carry no known-answer tag", {test_of(k.split("|", 1)[1]) for k in real_keys} == {"real"})
# must-fail: if two tests shared an epoch field by mistake in the master of another test's tag, keys would still differ; the control is a wrong rule that drops the instrument from the key
bad = {k.split("|", 1)[0] + "|" + "|".join(k.split("|")[2:]) for _o, k, _t in K.fam_k2().ev}
chk("control: a rule that drops the instrument field collapses keys", len(bad) < 36000, f"{len(bad):,} of 36,000")
w("")
w("RESULT " + ("all mixed-epoch checks hold" if not fails else "FAILED " + "; ".join(fails)))
sys.stdout.write("\n".join(out) + "\n")
