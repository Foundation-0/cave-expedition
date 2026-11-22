"""Seed rule of PREREG section 11: first 16 hex digits of SHA-256 of
'master|instrument|split|net|segment|purpose|index', fed to numpy's default generator."""
import hashlib
import numpy as np

MASTER = 20261121


def seed_string(instrument, split, net, segment, purpose, index):
    return "|".join(str(v) for v in (MASTER, instrument, split, net, segment, purpose, index))


def seed_int(instrument, split, net, segment, purpose, index):
    h = hashlib.sha256(seed_string(instrument, split, net, segment, purpose, index).encode("utf-8"))
    return int(h.hexdigest()[:16], 16)


def rng_for(instrument, split, net, segment, purpose, index):
    return np.random.default_rng(seed_int(instrument, split, net, segment, purpose, index))
