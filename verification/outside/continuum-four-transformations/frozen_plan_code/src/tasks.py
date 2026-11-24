"""Top-level task functions for the parallel map (must be importable by name)."""
import numpy as np
import iaaft
import nets
import seeds
import stats43
import synth
import flow
import transfer


def seg_task(a):
    """a = (x, key, js, kind, d4). Full result of stats43.analyse."""
    x, key, js, kind, d4 = a
    return stats43.analyse(x, key, js, kind=kind, d4=d4)


def k2_task(a):
    cls, idx = a
    x = synth.k2_series(cls, idx)
    r = stats43.analyse(x, ("K2:" + cls, "synthetic", "native", idx), nets.lag_js("native"))
    return {"pn": r["pn"], "reject": r["reject"], "lag_min_pn": r["lag_min_pn"], "tie": r["tie_excluded"],
            "deg": r["degenerate"], "iters": r["iters"], "nconv": r["nconv"], "pg": iaaft.periodogram(x)}


def k3_task(a):
    case, net, idx, kind = a
    x = synth.k3_series(case, idx)
    y = nets.apply(net, x)
    r = stats43.analyse(y, ("K3:" + case, "synthetic", net, idx), nets.lag_js(net), kind=kind)
    return {"pn": r["pn"], "reject": r["reject"], "tie": r["tie_excluded"], "iters": r["iters"], "nconv": r["nconv"]}


def flow_task(a):
    seg, key = a
    return flow.flow_segment(seg, key)


def sens_task(a):
    """IAAFT iteration-cap sensitivity (descriptive)."""
    cls, idx, cap = a
    x = synth.k2_series(cls, idx)
    r = stats43.analyse(x, ("K2:" + cls, "synthetic", "native", idx), nets.lag_js("native"), max_iter=cap)
    return {"reject": r["reject"], "iters": r["iters"], "nconv": r["nconv"]}
