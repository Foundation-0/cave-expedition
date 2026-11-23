"""Uniqueness of the seed-rule keys that section 11a, reading D14, writes down. Keys are master|instrument|split|net|segment|purpose|index
with index 0 unless stated. This script builds every key for the known-answer tests as D14 words them and counts distinct keys against the
number of draws that should be independent. Standard library only. No bare assert."""
import sys

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def key(instr, split, net, seg, purpose, idx=0):
    return f"master|{instr}|{split}|{net}|{seg}|{purpose}|{idx}"


def report(name, keys, intended):
    d = len(set(keys))
    status = "all distinct" if d == intended == len(keys) else f"COLLISION: {len(keys)} draws, {d} distinct keys"
    print(f"KEYS {name}: draws {len(keys)}, distinct keys {d}, intended independent draws {intended} | {status}")
    return d == intended == len(keys)


SEEDS = 10
ok = {}
# K5 data keys (segment = seed number)
cases = ["exp", "cascade", "shuffled", "yt", "yprime", "iaaft_cascade", "cascade_exp"]
data_keys = [key(f"K5b:{c}", sp, "native", s, "data") for c in cases for sp in ("fit", "verdict") for s in range(SEEDS)]
ok["K5 data"] = report("K5 data", data_keys, len(cases) * 2 * SEEDS)
# K5 flow-unit pools as D14 words them: segment flow-L<level>-q<unit>, no seed in the key
pool_keys = [key(f"K5b:{c}", sp, "native", f"flow-L{l}-q{q}", "surrogates") for c in cases for sp in ("fit", "verdict") for s in range(SEEDS)
             for l, nu in enumerate((32, 32, 31, 15)) for q in range(nu)]
ok["K5 pools"] = report("K5 flow-unit pools (as written)", pool_keys, len(pool_keys))
# the same with the seed carried in the segment field
pool_keys_fix = [key(f"K5b:{c}", sp, "native", f"s{s}-flow-L{l}-q{q}", "surrogates") for c in cases for sp in ("fit", "verdict") for s in range(SEEDS)
                 for l, nu in enumerate((32, 32, 31, 15)) for q in range(nu)]
report("K5 flow-unit pools (seed added to the segment field)", pool_keys_fix, len(pool_keys_fix))
# K3: data keys per use and pools per use, seeds 0..199
K3C = ["shots", "logistic", "saw", "saw_noisy"]
uses_own = ["native4096", "native2048", "placement", "wlen2048"]
uses_all = uses_own + ["bm2", "sub2", "q12", "q8"]
length = {"native4096": 4096, "native2048": 2048, "placement": 4096, "wlen2048": 2048}
k3d = [key(f"K3:{c}:{length[u]}", "synthetic", u, s, "data") for c in K3C for u in uses_own for s in range(200)]
ok["K3 data"] = report("K3 data (four uses with their own draw)", k3d, len(k3d))
k3p = [key(f"K3:{c}", "synthetic", u, s, "surrogates") for c in K3C for u in uses_all for s in range(200)]
ok["K3 pools"] = report("K3 pools (one per use)", k3p, len(k3p))
both = set(k3d) & set(k3p)
print(f"INFO K3 data keys and pool keys share a key: {len(both)}")
# K4 pools as D14 words them
kinds = ["A", "B", "C", "S", "Sr"]
k4 = [key(f"K4:{k}:s{s}", sp, run, seg, "surrogates") for k in kinds for sp in ("fit", "verdict") for s in range(SEEDS) for run in ("primary", "shifted") for seg in range(32)]
ok["K4 pools"] = report("K4 pools", k4, len(k4))
# K2 control shares the pool key of its class and length (stated); K1 keys
k2 = [key(f"K2:{c}:{n}", "synthetic", "native", s, p) for c in ("ar1_0.9", "white") for n in (4096, 2048) for s in range(1000) for p in ("data", "surrogates")]
ok["K2"] = report("K2 data and pools", k2, len(k2))
k2ctl = [key("K2:ar1_0.9:4096", "synthetic", "native", s, "surrogates") for s in range(200)]
print(f"INFO K2 control keys equal the K2 ar1_0.9 / 4096 pool keys for seeds 0..199: {set(k2ctl) <= set(k2)} (stated: the control pairs with the same random start)")
# detectors: D14 gives purposes and net only
det = [key("?", "?", run, "?", "detectors-flow") for crit in ("cascade_to_yprime", "iaaft_to_cascade", "cascade_to_exp") for s in range(SEEDS) for run in ("primary",)]
print(f"INFO detectors-flow keys as D14 words them (instrument, split and segment not stated): {len(det)} draws, {len(set(det))} distinct strings")
control("a key with the seed missing collides across seeds (the K5 pool keys as written)", not ok["K5 pools"])
control("keys with the seed present are distinct", ok["K3 pools"] and ok["K4 pools"])
bad = [k for k, v in ok.items() if not v]
print(f"RESULT keys that collide as written: {bad}")
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE seed_keys")
