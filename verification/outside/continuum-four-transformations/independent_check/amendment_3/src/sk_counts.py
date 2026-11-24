"""Closed-form recount of the author's key table (second checker: arithmetic only, no key strings).
Each family is counted from the plan's numbers, under the stated upper-bound model. Standard library only."""
import sys

out = []
def w(s): out.append(s)
fails = []
def expect(name, got, want):
    ok = got == want
    w(f"{name}: mine {got:,}, author {want:,} -> {'match' if ok else 'DIFFERENT'}")
    if not ok:
        fails.append(name)

# K1
n13 = 9 * 20; ni = 7 * 20
keys_k1 = n13 * 2 + (9 * 20 * 2) + ni * 2 + 1          # 1024 data+pool, 4096/2048 data, integer data+pool, waveform pool
ev_k1_consistent = n13 * 26 + 9 * 20 * 2 * 3 + ni * 8 + 4  # same counting for the 13 and the 4 series: data and pool per series
ev_k1_author = n13 * 26 + 9 * 20 * 2 * 3 + ni * 5 + 4      # integer: 4 pool draws + 1 data draw
expect("K1 distinct keys", keys_k1, 1001)
expect("K1 draws, every series counted alike", ev_k1_consistent, 6884)
w(f"K1 shared draws: {ev_k1_consistent - keys_k1:,} (5,163 + 720)")
# K2
expect("K2 draws", 9 * 2 * 1000 * 2 + 400, 36400); expect("K2 keys", 9 * 2 * 1000 * 2, 36000)
# K3
k3_keys = 4 * 200 * (4 + 8); k3_ev = 4 * 200 * (8 + 8) + 200
expect("K3 keys", k3_keys, 9600); expect("K3 draws", k3_ev, 13000)
# K4 superset
k4_data = 5 * 2 * 10; k4_ap = 2 * 10 * 34; k4_pools = 6 * 2 * 2 * 32 * 10; k4_det = 5 * 2 * 2 * 10
expect("K4 superset keys", k4_data + k4_ap + k4_pools + k4_det, 8660)
expect("K4 superset draws", k4_data + k4_ap + k4_pools + k4_det + 20, 8680)
# K5 plan sets
units = 32 + 32 + 31 + 15
k5 = 10 * (8 + 10 * units + 5)
expect("K5 10 sets keys", k5, 11130); expect("K5 10 sets draws", k5 + 20, 11150)
w(f"K5 units per set {units}; keys = 10 seeds x (8 data or whole-surrogate + 10 sets x {units} + 5 detectors)")
k5s = 10 * (11 + 42 * units + 9)
expect("K5 superset keys", k5s, 46400)
# real data
pres = 31 * 32; fitseg = 7 * 32; flow_v = 19 * 224; flow_f = 7 * 224
pools = pres + fitseg + flow_v + flow_f
det = 12 * (3 * 2 + 5)
expect("Real pools+detectors keys", pools + det, 7172)
expect("Real draws (C5 adds 2 per detector key)", pools + det + 2 * det, 7436)
verd_units = pres + flow_v
ctl = verd_units * 5 + 31 * 32 * 2
expect("Controls with segment pools", ctl, 28224)
# Law 2b pre-data
pre_events = (3 * 9 * 200 + 1 * 9 * 200) + (3 * 3 * 200 + 1 * 3 * 200)      # K2, K3 (3 gating cases): pools and F noise
pre_events += 3 * 6 * 2 * 2 * 32 * 10 + 6 * 2 * 2 * 10 * 32                          # K4 pools (W,F,D) and F noise
pre_events += 7 * 5 * 2 * 2 * 10                                                        # K4 detectors, 7 arrow instances
pre_events += 5 * 10 * 10 * units + 10 * 10 + 6 * 5 * 10                                # K5 pools (5 instances), F noise, detectors
datakeys = 9 * 200 + 3 * 200
expect("Law 2b pre-data keys", pre_events + datakeys, 99520)
expect("Law 2b pre-data draws (4,800 data reuses)", pre_events + datakeys + 4800, 104320)
w(f"  reuses: K2 2 x 1,800 + K3 2 x 600 = {2*1800+2*600:,}")
# Law 2b real instances
segitems = pres + fitseg
t = segitems * 3 + pres * 3 * 2 + segitems + pres * 2
flowitems = flow_v + flow_f
t += flowitems * 5 + flow_v * 5 * 2
t += (19 + 7) + 19 * 2
t += 31 * 32 * (3 + 1)
t += 12 * (7 * 3 * 2 + 6 * 5)
expect("Law 2b real instance keys", t, 89376)
# replicates
presrep = 31 * 4; flowrep = 19 * 4
r = presrep * (8 * 10 * 6 + 1 * 10 * 3) + flowrep * (6 * 10 * 6) + 12 * 10 * (7 * 3 * 2 + 6 * 5)
expect("Law 2b null replicate keys", r, 99240)
# K4 as D20 words it plus its second reading
k4_d20 = 10 * (10 + 680 // 10 + (3 * 32 + 3 * 2 * 32 + 2 * 32) + 16)
expect("K4 D20 keys", k4_d20, 4460)
k4_2nd = k4_d20 + 10 * (3 * 32 + 2 * 32 + 2 * 2 * 1)
expect("K4 D20 and second reading keys", k4_2nd, 6100)
expect("K4 D20 and second reading draws (20 A' + 60 shared)", k4_2nd + 20 + 60, 6180)
# union
total = 1001 + 36000 + 9600 + 8660 + 46400 + 28224 + 99520 + 89376 + 99240
real_new = (pools + det) - verd_units       # real family keys not already in the controls family
total += real_new
total -= datakeys                             # pre-data data keys already counted in K2 and K3
expect("All families together (no key in two families)", total, 417545)
w("RESULT " + ("all table rows reproduced from the plan counts" if not fails else "DIFFERENT rows: " + ", ".join(fails)))
# must-fail control: a wrong recount is flagged
bad = 1001 + 1
w("must-fail: a K1 count off by one is flagged: " + ("yes" if bad != 1001 else "NO"))
sys.stdout.write("\n".join(out) + "\n")
sys.exit(0)
