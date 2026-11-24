"""The two inputs that show the tension between reading D8 and item B8 (see AMENDMENTS_NEEDED.md). Prints what the code returns. Run with python3 -I -B."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, transfer
rng=lambda: np.random.default_rng(3)
def show(label, w, g):
    r=transfer.transfer_test("profile", np.asarray(w,float), np.asarray(g,float), np.ones(len(w),dtype=bool), rng(), R=100)
    print(label, "D=%d p=%s n_ge=%d n_lt=%d adverse=%s" % (r["D"], r["p"], r["n_ge"], r["n_lt"], r["adverse"]))
show("all tied (w = ones/sqrt(10), g = ones(10)):", np.ones(10)/np.sqrt(10), np.ones(10))
w=np.array([1,3,3,3,3,3,3,3.0]); w=w/np.sqrt(w@w)
show("partly tied (w = (1,3,3,3,3,3,3,3)/norm, g = (1,0,0,0,0,0,0,0)):", w, [1,0,0,0,0,0,0,0])
