"""Ordered parallel map. Results do not depend on the worker count."""
import multiprocessing as mp
import os

_POOL = None
MAX_WORKERS = 6  # at most 6 worker processes at once (shared machine)


def pmap(fn, items, workers=None):
    global _POOL
    items = list(items)
    workers = MAX_WORKERS if workers is None else min(int(workers), MAX_WORKERS)
    if workers <= 1 or len(items) < 3:
        return [fn(i) for i in items]
    if _POOL is None:
        _POOL = mp.get_context("spawn").Pool(workers)
    return _POOL.map(fn, items, chunksize=1)


def close():
    global _POOL
    if _POOL is not None:
        _POOL.close()
        _POOL.join()
        _POOL = None
