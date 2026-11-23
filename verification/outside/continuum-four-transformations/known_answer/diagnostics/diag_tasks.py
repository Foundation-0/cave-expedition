"""Tasks for the epoch-0 diagnosis (DIAGNOSIS_EPOCH0.md). Diagnostic only: nothing here is a known-answer run and nothing may pass a test.
They import the code under test and change none of it. An alternative pool key differs from the real one only in its purpose field
(`diag-surrogates`), so the draw is independent of the real pool's draw."""
import numpy as np
import keys
import nets
import segments
import stats43
import synth


def alt_pool_key(key):
    inst, split, net, seg, purpose, idx = key
    return (inst, split, net, seg, "diag-" + purpose, idx)


def k2_control_task(a):
    """a = (idx, kind, key variant). The K2 must-fail control series (AR(1) 0.9 after exp, 4,096 samples)."""
    idx, kind, variant = a
    x = synth.k2_series("ar1_0.9|exp", idx, 4096)
    key = keys.k2_pool("ar1_0.9", 4096, idx)
    if variant == "alt":
        key = alt_pool_key(key)
    r = stats43.segment_test(x, key, 99, kind)
    return {"pn": r["pn"], "T": r["T"]}


def k3_task(a):
    """a = (case, use, idx, kind, key variant): one K3 segment exactly as tasks.k3_task makes it, with an optional alternative pool key."""
    case, use, idx, kind, variant = a
    N, pad = 4096, segments.PAD
    if use == "native2048":
        blk = synth.k3_series(case, use, idx, 2048 + pad)
        seg, net = blk[segments.best_offset(blk, 2048):][:2048], "native"
    elif use == "wlen2048":
        blk = synth.k3_series(case, use, idx, 2048 + pad)
        o = segments.best_offset(blk, 2048)
        seg, net = blk[o:o + 2048], "native"
    elif use == "placement":
        blk = synth.k3_series(case, use, idx, N + pad)
        o = segments.best_offset(blk, N)
        seg, net = blk[o:o + N], "native"
    else:
        blk = synth.k3_series(case, "native4096", idx, N + pad)
        o = segments.best_offset(blk, N)
        seg = blk[o:o + N]
        net = {"native4096": "native"}.get(use, use)
    y = nets.apply(net, seg)
    key = keys.k3_pool(case, use, idx)
    if variant == "alt":
        key = alt_pool_key(key)
    r = stats43.segment_test(y, key, 99, kind)
    return {"pn": r["pn"], "T": r["T"]}
