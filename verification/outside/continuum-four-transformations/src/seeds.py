"""Seed rule of PREREG section 11: first 16 hex digits of SHA-256 of
'master|instrument|split|net|segment|purpose|index', fed to numpy's default generator.

Key epoch (reading D14 as amended by Amendment 4): the master field is 20261121 in epoch 0 and 20261121e<k> in epoch k, for k from 1,
with every other field unchanged. The epoch is a required keyword at every function that makes a seed, so a call that forgets it
fails at once instead of drawing from epoch 0. Epoch 0 gives the strings of the seed rule byte for byte."""
import hashlib
import numpy as np

MASTER = 20261121


def check_epoch(epoch):
    """The key epoch as an int: an int (numpy integers allowed) of at least 0. A bool, a float, a string or None is refused."""
    if isinstance(epoch, (bool, np.bool_)) or not isinstance(epoch, (int, np.integer)):
        raise TypeError("the key epoch must be an int, got %s" % type(epoch).__name__)
    if epoch < 0:
        raise ValueError("the key epoch must be at least 0")
    return int(epoch)


def master_field(epoch):
    """The master field of the seed string: '20261121' in epoch 0 and '20261121e<k>' in epoch k from 1."""
    k = check_epoch(epoch)
    return str(MASTER) if k == 0 else "%de%d" % (MASTER, k)


def seed_string(instrument, split, net, segment, purpose, index, *, epoch):
    return "|".join([master_field(epoch)] + [str(v) for v in (instrument, split, net, segment, purpose, index)])


def seed_int(instrument, split, net, segment, purpose, index, *, epoch):
    h = hashlib.sha256(seed_string(instrument, split, net, segment, purpose, index, epoch=epoch).encode("utf-8"))
    return int(h.hexdigest()[:16], 16)


def rng_for(instrument, split, net, segment, purpose, index, *, epoch):
    return np.random.default_rng(seed_int(instrument, split, net, segment, purpose, index, epoch=epoch))
