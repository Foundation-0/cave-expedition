"""Top-level task functions for the parallel map (must be importable by name). Results never depend on the worker count."""
import numpy as np
import flow
import nets
import ranks
import segments
import seeds
import stats43
import synth


def seg_task(a):
    """a = (x (series after its net), key, kind). Presence statistics and the standardised real-series features."""
    x, key, kind = a
    r = stats43.segment_test(x, key, 99, kind)
    zu, z1, z23 = stats43.arrow_profile_features(r["C3"])
    return {"pn": r["pn"], "den": r["den"], "reject": r["reject"], "T": r["T"], "js": r["js"],
            "zu": zu[0].copy(), "z1": z1[0].copy(), "z23": z23[0].copy(), "iters": r["iters"], "nconv": r["nconv"],
            "flag_zero_spread": r["flag_zero_spread"], "all_zero_spread": r["all_zero_spread"]}


def unit_task(a):
    seg, key, M, freq_map = a
    return flow.analyse_unit(seg, key, M, freq_map)


def k2_task(a):
    """a = (cls, n, idx, kind): one K2 segment, native net, surrogate kind."""
    cls, n, idx, kind = a
    x = synth.k2_series(cls, idx, n)
    r = stats43.segment_test(x, ("K2:%s:%d" % (cls, n), "synthetic", "native", idx), 99, kind)
    return {"pn": r["pn"], "reject": r["reject"], "iters": r["iters"], "nconv": r["nconv"],
            "zero": r["flag_zero_spread"]}


def k3_task(a):
    """a = (case, use, idx, kind). use: native4096, native2048, bm2, sub2, q12, q8, placement, wlen2048."""
    case, use, idx, kind = a
    N, pad = 4096, segments.PAD
    if use == "native2048":
        blk = synth.k3_series(case, use, idx, 2048 + pad)
        seg = blk[segments.best_offset(blk, 2048):][:2048]
        net = "native"
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
    r = stats43.segment_test(y, ("K3:%s" % case, "synthetic", use, idx), 99, kind)
    return {"pn": r["pn"], "reject": r["reject"], "iters": r["iters"], "nconv": r["nconv"]}


def _digest(a):
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def k1_task(a):
    """a = (cls, idx, n, variant, kind). Full pipeline of one segment under a variant of the plain class series x:
    id, cubic (x^3 + x), exp, rank, neg (-x), classexp and classcube (the exp and cube versions of the class).
    Digests of the surrogate rows (and their negation), of the counts and of the standardised features."""
    cls, idx, n, variant, kind = a
    x = synth.k2_series(cls, idx, n)
    if variant == "id":
        y = x
    elif variant == "cubic":
        y = x ** 3 + x
    elif variant == "exp":
        y = np.exp(x)
    elif variant == "rank":
        y = nets.increasing_maps()["rank"](x)
    elif variant == "neg":
        y = -x
    elif variant == "classexp":
        y = synth.k2_series(cls + "|exp", idx, n)
    elif variant == "classcube":
        y = synth.k2_series(cls + "|cube", idx, n)
    else:
        raise ValueError("unknown variant " + variant)
    key = ("K1:%s:%d" % (cls, n), "synthetic", "native", idx)
    pool, _, _ = stats43.make_pool(y, key, 99, kind)
    js = nets.lag_js(n)
    C3, _ = stats43.counts3(pool, js)
    r = stats43.presence_stats(C3)
    return {"guard": nets.map_guard_ok(x, y), "pn": r["pn"], "pool": _digest(pool[1:]), "negpool": _digest(-pool[1:]),
            "C3": _digest(C3), "Z": _digest(r["Z"]), "scores": _digest(ranks.normal_scores(y)),
            "T": r["T"]}
