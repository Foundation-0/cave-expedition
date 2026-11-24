"""Top-level task functions for the parallel map (must be importable by name). Results never depend on the worker count.
Every work item carries the key epoch of its draws as its last field (D14 as amended by Amendment 4). The parallel map starts its workers
with the spawn method, so a value set in the parent process would not reach them: the epoch travels with the item, and an item without
it fails to unpack."""
import numpy as np
import flow
import keys
import nets
import ranks
import segments
import seeds
import stats43
import synth


def seg_task(a):
    """a = (x (series after its net), pool key (six fields, keys.py), kind, epoch). Presence statistics and the standardised real-series
    features."""
    x, key, kind, epoch = a
    r = stats43.segment_test(x, key, 99, kind, epoch=epoch)
    zu, z1, z23 = stats43.arrow_profile_features(r["C3"])
    return {"pn": r["pn"], "den": r["den"], "reject": r["reject"], "T": r["T"], "js": r["js"],
            "zu": zu[0].copy(), "z1": z1[0].copy(), "z23": z23[0].copy(), "iters": r["iters"], "nconv": r["nconv"],
            "flag_zero_spread": r["flag_zero_spread"], "all_zero_spread": r["all_zero_spread"]}


def unit_task(a):
    """a = (segment, pool key, M, freq_map, epoch), as flow.stream_units makes it."""
    seg, key, M, freq_map, epoch = a
    return flow.analyse_unit(seg, key, M, freq_map, epoch=epoch)


def k2_task(a):
    """a = (cls, n, idx, kind, epoch): one K2 segment, native net, surrogate kind, key epoch of the K2 run."""
    cls, n, idx, kind, epoch = a
    x = synth.k2_series(cls, idx, n, epoch=epoch)
    # the pool key is that of the plain class draw, also for the must-fail control on the exp version (D14, K2)
    r = stats43.segment_test(x, keys.k2_pool(cls.partition("|")[0], n, idx), 99, kind, epoch=epoch)
    return {"pn": r["pn"], "reject": r["reject"], "iters": r["iters"], "nconv": r["nconv"],
            "zero": r["flag_zero_spread"]}


def k3_task(a):
    """a = (case, use, idx, kind, epoch). use: native4096, native2048, bm2, sub2, q12, q8, placement, wlen2048."""
    case, use, idx, kind, epoch = a
    N, pad = 4096, segments.PAD
    if use == "native2048":
        blk = synth.k3_series(case, use, idx, 2048 + pad, epoch=epoch)
        seg = blk[segments.best_offset(blk, 2048):][:2048]
        net = "native"
    elif use == "wlen2048":
        blk = synth.k3_series(case, use, idx, 2048 + pad, epoch=epoch)
        o = segments.best_offset(blk, 2048)
        seg, net = blk[o:o + 2048], "native"
    elif use == "placement":
        blk = synth.k3_series(case, use, idx, N + pad, epoch=epoch)
        o = segments.best_offset(blk, N)
        seg, net = blk[o:o + N], "native"
    else:
        blk = synth.k3_series(case, "native4096", idx, N + pad, epoch=epoch)
        o = segments.best_offset(blk, N)
        seg = blk[o:o + N]
        net = {"native4096": "native"}.get(use, use)
    y = nets.apply(net, seg)
    r = stats43.segment_test(y, keys.k3_pool(case, use, idx), 99, kind, epoch=epoch)
    return {"pn": r["pn"], "reject": r["reject"], "iters": r["iters"], "nconv": r["nconv"]}


def _digest(a):
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def k1_map(v, variant):
    """The K1 comparison maps (B5): y = v / max|v|, then y^3 + y and exp(y); the ranks of v; the negation."""
    if variant == "id":
        return v
    if variant == "neg":
        return -v
    if variant == "rank":
        return nets.increasing_maps()["rank"](v)
    y = v / np.max(np.abs(v))
    if variant == "cubic":
        return y ** 3 + y
    if variant == "exp":
        return np.exp(y)
    raise ValueError("unknown variant " + variant)


def k1_task(a):
    """a = (source, cls, idx, n, variant, kind, epoch). source 'class' (a class version of the plain draw under `K1`), 'int' (the
    integer-valued series of B6, `K1int`) or 'wave' (the tied waveform, `K1wave`). The series is the version of the plain draw
    mapped by `variant`. Returns the representability facts against the plain draw and digests of the surrogate rows (and their
    negation), the counts, the standardised features and the normal scores, and the p-value. epoch is the key epoch of the K1 run."""
    source, cls, idx, n, variant, kind, epoch = a
    base, _, ver = cls.partition("|")
    if source == "class":
        plain = synth.k1_series(base, idx, n, epoch=epoch)
        v = synth.k1_series(cls, idx, n, epoch=epoch)
        key = keys.k1_pool(base, n, idx)
    elif source == "int":
        plain = synth.k1_int_series(base, idx, n, epoch=epoch)
        v = plain
        key = keys.k1int_pool(base, idx, n)
    elif source == "wave":
        plain = synth.tied_waveform()
        v = plain
        key = keys.k1wave_pool()
    else:
        raise ValueError("unknown K1 source " + source)
    with np.errstate(all="ignore"):
        y = k1_map(v, variant)
    finite = bool(np.all(np.isfinite(y)))
    rep = finite and ranks.n_distinct(y) == ranks.n_distinct(plain)
    out = {"finite": finite, "representable": bool(rep)}
    if not rep:
        return out
    pool, _, _ = stats43.make_pool(y, key, 99, kind, epoch=epoch)
    js = nets.lag_js(n)
    C3, _ = stats43.counts3(pool, js)
    r = stats43.presence_stats(C3)
    out.update({"pn": r["pn"], "pool": _digest(pool[1:]), "negpool": _digest(-pool[1:]), "C3": _digest(C3),
                "Z": _digest(r["Z"]), "scores": _digest(ranks.normal_scores(y)), "T": r["T"]})
    return out
