"""Ordered parallel map. Results do not depend on the worker count."""
import multiprocessing as mp
import os

_POOL = None


def pmap(fn, items, workers=None):
    global _POOL
    items = list(items)
    if workers is None:
        workers = min(12, (os.cpu_count() or 1) + 2)
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
