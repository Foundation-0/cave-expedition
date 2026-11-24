# What the check scripts need

This note records the software behind the committed outputs of `checks/amendment_2/` and `checks/amendment_3/`. It is not part of the plan.

- `recompute_k2b.py` and `compute_components.py` (Amendment 2), and `seed_keys.py` and `compute_k3.py` (Amendment 3), use the Python standard library only.
- `derive_yprime.py` needs numpy and scipy. Its only use of scipy is `scipy.special.erf`.
- `amp_maps.py` (Amendment 3) needs numpy.
- The three `checks/sim_*.py` scripts of Amendment 1 need numpy. The numpy version behind their committed outputs was not recorded when they were made.
- The scripts run under `python3 -I`, which ignores the user's own site-packages. numpy and scipy must therefore be installed in the interpreter's own site-packages, not with `pip install --user`.
- Part 1 of `derive_yprime.py` is deterministic (a trapezoid sum). Part 2 and `amp_maps.py` draw samples from numpy's generator, so their printed figures depend on the numpy version. Part 1's last digits can also depend on numpy and scipy.
- The committed outputs of both folders were made with Python 3.14.6, numpy 2.5.4 and scipy 1.18.1, and are identical in the three modes `-I -B`, `-I -O -B` and `-I -B -W error` (`status.txt` in each folder).

On 2026-11-22, a rerun of `derive_yprime.py` under `python3 -I -B` with those versions gave output byte-identical to the committed `out_derive_yprime.mode1.txt`. The committed outputs of Amendment 2 were not changed.
