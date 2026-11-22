#!/usr/bin/env python3
"""AUDIT-099 Pure-Q Zero-Float Graph Topology & Compositional Grammar Oracle.

Parses and audits two staged compositional corpora strictly from raw files using
100% pure Python 3 stdlib (exact int / Fraction arithmetic; ZERO floats, ZERO bare asserts):
  1. Christopher Alexander's *A Pattern Language* (`apl-md`, 253 patterns, 1..253).
  2. *The Grammar of Simulation* (`simgrammar`, games / mechanics / techniques / opportunities / sources).

Applies strict Law-5 anti-smuggling discipline:
  - Compares the two extracted graphs ONLY on matched dimensionless graph observables
    (connected components, articulation points, bridges, Tarjan SCC giant-component
    fraction, hierarchy monotonicity, bipartite co-occurrence, and Rényi-2 specialization
    against B >= 100 degree-preserving / permutation multi-shuffle nulls with exact
    pure-Q empirical rank p-values).
  - Explicitly documents structural divergences and non-significant nulls without
    shared-vocabulary metaphors.
"""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction
import math
from pathlib import Path
import random
import re
from typing import Any


class GrammarAuditError(ValueError):
    """Fail-closed refusal raised on any malformed input, conservation breach, or gate failure."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GrammarAuditError(message)


def _require_exact_int(value: Any, name: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"exact-int:{name}")
    return value


def _require_exact_bool(value: Any, name: str) -> bool:
    _require(type(value) is bool, f"exact-bool:{name}")
    return value


def _require_exact_fraction(value: Any, name: str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value, 1)
    raise GrammarAuditError(f"exact-fraction:{name}")


def _require_clean_ascii(value: Any, name: str) -> str:
    _require(
        isinstance(value, str)
        and len(value) > 0
        and value == value.strip()
        and all(32 <= ord(ch) <= 126 for ch in value),
        f"clean-ascii:{name}",
    )
    return value


def frac_str(value: Fraction) -> str:
    v = _require_exact_fraction(value, "frac_str")
    return f"{v.numerator}/{v.denominator}"


def frac_dec(value: Fraction, digits: int = 6) -> str:
    """Truncate exact Fraction toward zero to `digits` decimals."""
    v = _require_exact_fraction(value, "frac_dec")
    d = _require_exact_int(digits, "digits")
    _require(d >= 1, "digits-pos")
    sign = "-" if v < 0 else ""
    av = abs(v)
    ten_pow = 10**d
    scaled = (av.numerator * ten_pow) // av.denominator
    whole, rem = divmod(scaled, ten_pow)
    return f"{sign}{whole}.{rem:0{d}d}"


def frac_dec_ceil(value: Fraction, digits: int = 6) -> str:
    """Round non-negative exact Fraction strictly UP to `digits` decimals."""
    v = _require_exact_fraction(value, "frac_dec_ceil")
    d = _require_exact_int(digits, "digits")
    _require(v >= 0 and d >= 1, "frac-dec-ceil-domain")
    ten_pow = 10**d
    scaled = (v.numerator * ten_pow + v.denominator - 1) // v.denominator
    whole, rem = divmod(scaled, ten_pow)
    return f"{whole}.{rem:0{d}d}"


# =============================================================================
# EXACT GRAPH & RANK PRIMITIVES (PURE INT / FRACTION, ZERO FLOATS)
# =============================================================================


def tarjan_sccs(adj: dict[Any, set[Any]]) -> list[list[Any]]:
    """Iterative Tarjan strongly connected components (deterministic sorted output)."""
    _require(isinstance(adj, dict) and len(adj) >= 1, "tarjan-adj-nonempty")
    index_counter = 0
    indices: dict[Any, int] = {}
    lowlink: dict[Any, int] = {}
    tarjan_stack: list[Any] = []
    on_stack: set[Any] = set()
    sccs: list[list[Any]] = []

    for root in sorted(adj):
        if root in indices:
            continue
        call_stack: list[tuple[Any, list[Any], int]] = [(root, sorted(adj[root]), 0)]
        indices[root] = lowlink[root] = index_counter
        index_counter += 1
        tarjan_stack.append(root)
        on_stack.add(root)

        while call_stack:
            v, nbrs, pos = call_stack[-1]
            if pos < len(nbrs):
                call_stack[-1] = (v, nbrs, pos + 1)
                w = nbrs[pos]
                if w not in indices:
                    indices[w] = lowlink[w] = index_counter
                    index_counter += 1
                    tarjan_stack.append(w)
                    on_stack.add(w)
                    call_stack.append((w, sorted(adj.get(w, set())), 0))
                elif w in on_stack:
                    if indices[w] < lowlink[v]:
                        lowlink[v] = indices[w]
            else:
                call_stack.pop()
                if call_stack:
                    parent = call_stack[-1][0]
                    if lowlink[v] < lowlink[parent]:
                        lowlink[parent] = lowlink[v]
                if lowlink[v] == indices[v]:
                    comp: list[Any] = []
                    while True:
                        w = tarjan_stack.pop()
                        on_stack.remove(w)
                        comp.append(w)
                        if w == v:
                            break
                    sccs.append(sorted(comp))

    sccs.sort(key=lambda c: (-len(c), c[0]))
    return sccs


def undirected_articulations_and_bridges(uadj: dict[Any, set[Any]]) -> tuple[int, list[Any], list[tuple[Any, Any]]]:
    """Iterative DFS computing (component_count, articulation_points, bridge_edges)."""
    _require(isinstance(uadj, dict) and len(uadj) >= 1, "uadj-nonempty")
    disc: dict[Any, int] = {}
    low: dict[Any, int] = {}
    parent: dict[Any, Any] = {}
    child_count: dict[Any, int] = {}
    arts: set[Any] = set()
    bridges: list[tuple[Any, Any]] = []
    timer = 0
    comps = 0

    for root in sorted(uadj):
        if root in disc:
            continue
        comps += 1
        disc[root] = low[root] = timer
        timer += 1
        parent[root] = None
        child_count[root] = 0
        stack: list[tuple[Any, list[Any], int]] = [(root, sorted(uadj[root]), 0)]

        while stack:
            u, nbrs, pos = stack[-1]
            if pos < len(nbrs):
                stack[-1] = (u, nbrs, pos + 1)
                v = nbrs[pos]
                if v not in disc:
                    parent[v] = u
                    child_count[u] += 1
                    child_count[v] = 0
                    disc[v] = low[v] = timer
                    timer += 1
                    stack.append((v, sorted(uadj.get(v, set())), 0))
                elif v != parent[u]:
                    if disc[v] < low[u]:
                        low[u] = disc[v]
            else:
                stack.pop()
                p = parent[u]
                if p is not None:
                    if low[u] < low[p]:
                        low[p] = low[u]
                    if parent[p] is not None and low[u] >= disc[p]:
                        arts.add(p)
                    if low[u] > disc[p]:
                        bridges.append((u, p) if u < p else (p, u))
                elif child_count[u] > 1:
                    arts.add(u)

    return comps, sorted(arts), sorted(bridges)


def _midranks_doubled(values: Sequence[int]) -> list[int]:
    """Return exact integer 2 * midrank for tie-adjusted Spearman without floats."""
    n = len(values)
    _require(n >= 2, "spearman-n-ge-2")
    order = sorted(range(n), key=lambda i: values[i])
    r2 = [0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        mr2 = (i + 1) + (j + 1)
        for k in range(i, j + 1):
            r2[order[k]] = mr2
        i = j + 1
    return r2


def exact_spearman_sq_and_sign(xs: Sequence[int], ys: Sequence[int]) -> tuple[int, Fraction, int]:
    """Return exact (sign, rho^2 as Fraction, cov_num) for integer vectors xs, ys."""
    _require(len(xs) == len(ys) and len(xs) >= 2, "spearman-len-match")
    n = len(xs)
    rx = _midranks_doubled(xs)
    ry = _midranks_doubled(ys)
    sum_r = n * (n + 1)
    cov_num = n * sum(a * b for a, b in zip(rx, ry)) - sum_r * sum_r
    vx_num = n * sum(a * a for a in rx) - sum_r * sum_r
    vy_num = n * sum(b * b for b in ry) - sum_r * sum_r
    _require(vx_num > 0 and vy_num > 0, "spearman-nonconstant")
    sgn = 1 if cov_num > 0 else (-1 if cov_num < 0 else 0)
    rho_sq = Fraction(cov_num * cov_num, vx_num * vy_num)
    return sgn, rho_sq, cov_num


def _isqrt_frac_dec(val: Fraction, digits: int = 6) -> str:
    """Truncated decimal string of sqrt(val) for non-negative Fraction val using math.isqrt."""
    v = _require_exact_fraction(val, "sqrt-val")
    d = _require_exact_int(digits, "sqrt-digits")
    _require(v >= 0 and d >= 1, "sqrt-domain")
    ten_pow = 10**d
    scaled = math.isqrt((v.numerator * ten_pow * ten_pow) // v.denominator)
    whole, rem = divmod(scaled, ten_pow)
    return f"{whole}.{rem:0{d}d}"


# =============================================================================
# RAW FILE PARSERS (APL-MD & SIMGRAMMAR — 100% STDLIB)
# =============================================================================

_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_PAT_NUM_RE = re.compile(r"\((\d+)\)")
_CONF_TAG_RE = re.compile(r"#APL/confidence/(\w+)")
_TIER_TAG_RE = re.compile(r"#APL/(Town-Patterns|Building-Patterns|Construction-Patterns)")


def parse_apl_corpus(patterns_dir: Path) -> dict[str, Any]:
    """Parse all pattern Markdown files from an apl-md Patterns/ directory."""
    _require(patterns_dir.is_dir(), f"apl-dir-missing:{patterns_dir.name}")
    files = sorted(patterns_dir.glob("*.md"))
    _require(len(files) >= 2, "apl-files-min")

    id_by_file: dict[Path, int] = {}
    for fp in files:
        m = re.search(r"\((\d+)\)$", fp.stem)
        _require(m is not None, f"apl-filename-id:{fp.name}")
        pid = int(m.group(1))
        _require(pid >= 1 and pid not in id_by_file.values(), f"apl-dup-id:{pid}")
        id_by_file[fp] = pid

    valid_ids = set(id_by_file.values())
    adj: dict[int, set[int]] = {pid: set() for pid in valid_ids}
    upper_edges: set[tuple[int, int]] = set()
    lower_edges: set[tuple[int, int]] = set()
    self_loops: list[int] = []
    raw_wikilinks = 0
    unresolved_links = 0
    conf_counts: dict[str, int] = {}
    tier_by_id: dict[int, int] = {}
    min_id = min(valid_ids)

    for fp in files:
        src = id_by_file[fp]
        txt = fp.read_text(encoding="utf-8")
        cm = _CONF_TAG_RE.search(txt)
        cval = cm.group(1) if cm else "none"
        conf_counts[cval] = conf_counts.get(cval, 0) + 1

        tm = _TIER_TAG_RE.search(txt)
        if tm:
            tname = tm.group(1)
            tier_by_id[src] = 0 if tname == "Town-Patterns" else (1 if tname == "Building-Patterns" else 2)
        else:
            tier_by_id[src] = 0 if src <= 94 else (1 if src <= 204 else 2)

        for raw_t in _WIKILINK_RE.findall(txt):
            raw_wikilinks += 1
            mm = _PAT_NUM_RE.search(raw_t)
            if mm is None:
                unresolved_links += 1
                continue
            dst = int(mm.group(1))
            if dst not in valid_ids:
                unresolved_links += 1
                continue
            if dst == src:
                self_loops.append(src)
            else:
                adj[src].add(dst)

        if "### Related Patterns" in txt:
            rp = txt.split("### Related Patterns", 1)[1].split("\n---", 1)[0].strip()
            paras = [p.strip() for p in re.split(r"\n\s*\n", rp) if p.strip()]
            if src == min_id and len(paras) == 1:
                for raw_t in _WIKILINK_RE.findall(paras[0]):
                    mm = _PAT_NUM_RE.search(raw_t)
                    if mm is not None:
                        dst = int(mm.group(1))
                        if dst in valid_ids and dst != src:
                            lower_edges.add((src, dst))
            elif paras:
                for raw_t in _WIKILINK_RE.findall(paras[0]):
                    mm = _PAT_NUM_RE.search(raw_t)
                    if mm is not None:
                        dst = int(mm.group(1))
                        if dst in valid_ids and dst != src:
                            upper_edges.add((src, dst))
                for p_rest in paras[1:]:
                    for raw_t in _WIKILINK_RE.findall(p_rest):
                        mm = _PAT_NUM_RE.search(raw_t)
                        if mm is not None:
                            dst = int(mm.group(1))
                            if dst in valid_ids and dst != src:
                                lower_edges.add((src, dst))

    return {
        "nodes": sorted(valid_ids),
        "adj": adj,
        "upper_edges": sorted(upper_edges),
        "lower_edges": sorted(lower_edges),
        "self_loops": sorted(set(self_loops)),
        "raw_wikilinks": raw_wikilinks,
        "unresolved_links": unresolved_links,
        "confidence_counts": conf_counts,
        "tier_by_id": tier_by_id,
    }


def _strip_yaml_scalar(raw: str) -> str:
    return raw.strip().strip("'\"")


def _parse_sg_game(text: str, fname: str) -> dict[str, Any]:
    m_id = re.search(r"^id:\s*(.+)$", text, re.M)
    m_yr = re.search(r"^year:\s*(\d+)$", text, re.M)
    _require(m_id is not None and m_yr is not None, f"sg-game-header:{fname}")
    gid = _strip_yaml_scalar(m_id.group(1))
    year = int(m_yr.group(1))
    deprecated = bool(re.search(r"^deprecated:", text, re.M))
    mechanics: list[dict[str, str]] = []
    in_m = False
    cur: dict[str, str] | None = None
    for line in text.splitlines():
        if line == "mechanics:":
            in_m = True
            continue
        if in_m:
            if line and not line[0].isspace() and not line.startswith("-"):
                in_m = False
                continue
            mi = re.match(r"^\s*-\s+id:\s*(.+)$", line)
            if mi:
                cur = {"id": _strip_yaml_scalar(mi.group(1)), "role": ""}
                mechanics.append(cur)
            else:
                mr = re.match(r"^\s+role:\s*(.+)$", line)
                if mr and cur is not None:
                    cur["role"] = _strip_yaml_scalar(mr.group(1))
    return {"id": gid, "year": year, "deprecated": deprecated, "mechanics": mechanics}


def _parse_sg_mechanic(text: str, fname: str) -> dict[str, Any]:
    m_id = re.search(r"^id:\s*(.+)$", text, re.M)
    m_fam = re.search(r"^family:\s*(.+)$", text, re.M)
    _require(m_id is not None and m_fam is not None, f"sg-mech-header:{fname}")
    mid = _strip_yaml_scalar(m_id.group(1))
    fam = _strip_yaml_scalar(m_fam.group(1))
    deprecated = bool(re.search(r"^deprecated:", text, re.M))
    scores: dict[str, int] = {}
    for k in ("legibility", "emergence_potential", "tuning_difficulty"):
        ms = re.search(rf"^{k}:\s*(\d+)$", text, re.M)
        _require(ms is not None, f"sg-mech-score:{fname}:{k}")
        scores[k] = int(ms.group(1))
    rels: dict[str, list[str]] = {"requires": [], "specializes": [], "synergy": [], "tension": []}
    for rk in ("requires", "specializes", "synergy", "tension"):
        ms = re.search(rf"^{rk}:\s+(\S+)\s*$", text, re.M)
        if ms and ms.group(1) != "[]":
            rels[rk].append(_strip_yaml_scalar(ms.group(1)))
            continue
        in_r = False
        for line in text.splitlines():
            if line == f"{rk}:":
                in_r = True
                continue
            if in_r:
                if line and not line[0].isspace() and not line.startswith("-"):
                    in_r = False
                    continue
                m1 = re.match(r"^\s*-\s+id:\s*(.+)$", line)
                m2 = re.match(r"^\s*-\s+([a-z0-9-]+)\s*$", line)
                if m1:
                    rels[rk].append(_strip_yaml_scalar(m1.group(1)))
                elif m2:
                    rels[rk].append(_strip_yaml_scalar(m2.group(1)))
    return {"id": mid, "family": fam, "deprecated": deprecated, "scores": scores, "rels": rels}


def _parse_sg_technique(text: str, fname: str) -> dict[str, Any]:
    m_id = re.search(r"^id:\s*(.+)$", text, re.M)
    _require(m_id is not None, f"sg-tech-header:{fname}")
    tid = _strip_yaml_scalar(m_id.group(1))
    deprecated = bool(re.search(r"^deprecated:", text, re.M))
    affects: list[dict[str, str]] = []
    in_a = False
    cur: dict[str, str] | None = None
    for line in text.splitlines():
        if line == "affects:":
            in_a = True
            continue
        if in_a:
            if line and not line[0].isspace() and not line.startswith("-"):
                in_a = False
                continue
            m1 = re.match(r"^\s*-\s+(?:mechanic|id):\s*(.+)$", line)
            if m1:
                cur = {"mechanic": _strip_yaml_scalar(m1.group(1)), "effect": ""}
                affects.append(cur)
            else:
                me = re.match(r"^\s+effect:\s*(.+)$", line)
                if me and cur is not None:
                    cur["effect"] = _strip_yaml_scalar(me.group(1))
    return {"id": tid, "deprecated": deprecated, "affects": affects}


def parse_simgrammar_corpus(data_dir: Path) -> dict[str, Any]:
    """Parse games, mechanics, techniques, opportunities, and sources from simgrammar/data/."""
    _require(data_dir.is_dir(), f"sg-data-dir-missing:{data_dir.name}")
    for sub in ("games", "mechanics", "techniques", "opportunities", "sources"):
        _require((data_dir / sub).is_dir(), f"sg-subdir-missing:{sub}")

    games_all = [_parse_sg_game(f.read_text(encoding="utf-8"), f.name) for f in sorted((data_dir / "games").glob("*.yaml"))]
    mechs_all = [_parse_sg_mechanic(f.read_text(encoding="utf-8"), f.name) for f in sorted((data_dir / "mechanics").glob("*.yaml"))]
    techs_all = [_parse_sg_technique(f.read_text(encoding="utf-8"), f.name) for f in sorted((data_dir / "techniques").glob("*.yaml"))]

    opp_files = sorted((data_dir / "opportunities").glob("*.yaml"))
    live_opps: list[str] = []
    deprecated_opps: list[dict[str, str]] = []
    for f in opp_files:
        txt = f.read_text(encoding="utf-8")
        m_id = re.search(r"^id:\s*(.+)$", txt, re.M)
        _require(m_id is not None, f"sg-opp-header:{f.name}")
        oid = _strip_yaml_scalar(m_id.group(1))
        if re.search(r"^deprecated:", txt, re.M):
            m_sup = re.search(r"^\s+superseded_by:\s*(.+)$", txt, re.M)
            deprecated_opps.append(
                {"id": oid, "superseded_by": _strip_yaml_scalar(m_sup.group(1)) if m_sup else "unspecified"}
            )
        else:
            live_opps.append(oid)

    source_files = sorted((data_dir / "sources").glob("*.yaml"))
    _require(len(games_all) >= 2 and len(mechs_all) >= 2 and len(techs_all) >= 1, "sg-corpus-nonempty")

    return {
        "games": [g for g in games_all if not g["deprecated"]],
        "mechanics": [m for m in mechs_all if not m["deprecated"]],
        "techniques": [t for t in techs_all if not t["deprecated"]],
        "total_opp_files": len(opp_files),
        "live_opportunities": live_opps,
        "deprecated_opportunities": deprecated_opps,
        "source_count": len(source_files),
    }


# =============================================================================
# BITMASK DEGREE-PRESERVING REWIRING & LIVE ANALYSIS ENGINES
# =============================================================================


def _rewire_directed_bitmask_null(
    n_nodes: int,
    edges_idx: Sequence[tuple[int, int]],
    tier_by_idx: Sequence[int],
    n_shuffles: int,
    seed: int,
    mode: str,
) -> dict[str, Any]:
    """Fast exact-int bitmask degree-preserving directed rewiring null."""
    rr = random.Random(seed).randrange
    m = len(edges_idx)
    swaps = 2 * m
    bits = [1 << idx for idx in range(n_nodes)]
    tier_masks = [0, 0, 0]
    for idx, t in enumerate(tier_by_idx):
        tier_masks[t] |= bits[idx]
    all_mask = (1 << n_nodes) - 1
    gt_masks = [all_mask ^ ((1 << (idx + 1)) - 1) for idx in range(n_nodes)]

    recip_vals: list[int] = []
    same_tier_vals: list[int] = []
    down_vals: list[int] = []

    for _ in range(n_shuffles):
        elist = list(edges_idx)
        out_m = [0] * n_nodes
        in_m = [0] * n_nodes
        for u, v in elist:
            out_m[u] |= bits[v]
            in_m[v] |= bits[u]
        for _s in range(swaps):
            i = rr(m)
            j = rr(m)
            if i == j:
                continue
            u1, v1 = elist[i]
            u2, v2 = elist[j]
            if u1 == v2 or u2 == v1 or u1 == u2 or v1 == v2:
                continue
            bv2 = bits[v2]
            bv1 = bits[v1]
            if (out_m[u1] & bv2) or (out_m[u2] & bv1):
                continue
            v_xor = bv1 | bv2
            u_xor = bits[u1] | bits[u2]
            out_m[u1] ^= v_xor
            out_m[u2] ^= v_xor
            in_m[v1] ^= u_xor
            in_m[v2] ^= u_xor
            elist[i] = (u1, v2)
            elist[j] = (u2, v1)

        if mode == "full":
            recip_vals.append(sum((out_m[u] & in_m[u]).bit_count() for u in range(n_nodes)))
            same_tier_vals.append(sum((out_m[u] & tier_masks[tier_by_idx[u]]).bit_count() for u in range(n_nodes)))
        else:
            down_vals.append(sum((out_m[u] & gt_masks[u]).bit_count() for u in range(n_nodes)))

    return {"recip": recip_vals, "same_tier": same_tier_vals, "down": down_vals}


def analyze_apl_graph_live(
    apl_data: dict[str, Any], n_shuffles: int = 200, seed: int = 20261122
) -> dict[str, Any]:
    """Compute exact pure-Q graph invariants and B-shuffle degree-preserving nulls on apl-md."""
    b_i = _require_exact_int(n_shuffles, "n_shuffles")
    s_i = _require_exact_int(seed, "seed")
    _require(b_i >= 100, "apl-shuffles-ge-100")

    nodes: list[int] = list(apl_data["nodes"])
    idx_of = {pid: i for i, pid in enumerate(nodes)}
    v_count = len(nodes)
    adj: dict[int, set[int]] = apl_data["adj"]
    tier_by_id: dict[int, int] = apl_data["tier_by_id"]

    edge_set = {(u, v) for u in adj for v in adj[u]}
    edges = sorted(edge_set)
    e_uniq = len(edges)
    recip_dir = sum(1 for u, v in edges if (v, u) in edge_set)
    oneway_dir = e_uniq - recip_dir
    down_e = sum(1 for u, v in edges if u < v)
    up_e = e_uniq - down_e

    tier_mat = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for u, v in edges:
        tier_mat[tier_by_id[u]][tier_by_id[v]] += 1
    same_tier_e = tier_mat[0][0] + tier_mat[1][1] + tier_mat[2][2]

    upper_set = set(apl_data["upper_edges"])
    lower_set = set(apl_data["lower_edges"])
    overlap_ul = len(upper_set & lower_set)
    lower_down = sum(1 for u, v in lower_set if u < v)
    lower_up = len(lower_set) - lower_down
    upper_up = sum(1 for u, v in upper_set if u > v)
    upper_down = len(upper_set) - upper_up

    lower_tier_mat = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for u, v in lower_set:
        lower_tier_mat[tier_by_id[u]][tier_by_id[v]] += 1

    sccs_full = tarjan_sccs(adj)
    lower_adj: dict[int, set[int]] = {pid: set() for pid in nodes}
    for u, v in lower_set:
        lower_adj[u].add(v)
    sccs_lower = tarjan_sccs(lower_adj)

    uadj: dict[int, set[int]] = {pid: set() for pid in nodes}
    for u, v in edges:
        uadj[u].add(v)
        uadj[v].add(u)
    undir_edges = sum(len(vs) for vs in uadj.values()) // 2
    u_comps, u_arts, u_bridges = undirected_articulations_and_bridges(uadj)

    # Degree-preserving multi-shuffle nulls (B shuffles)
    tier_by_idx = [tier_by_id[pid] for pid in nodes]
    full_idx_edges = [(idx_of[u], idx_of[v]) for u, v in edges]
    null_full = _rewire_directed_bitmask_null(v_count, full_idx_edges, tier_by_idx, b_i, s_i, "full")
    ge_recip = sum(1 for x in null_full["recip"] if x >= recip_dir)
    ge_same = sum(1 for x in null_full["same_tier"] if x >= same_tier_e)

    lower_idx_edges = [(idx_of[u], idx_of[v]) for u, v in sorted(lower_set)]
    null_lower = _rewire_directed_bitmask_null(v_count, lower_idx_edges, tier_by_idx, b_i, s_i + 1, "lower")
    ge_lower_down = sum(1 for x in null_lower["down"] if x >= lower_down)

    return {
        "v_count": v_count,
        "raw_wikilinks": apl_data["raw_wikilinks"],
        "unresolved_links": apl_data["unresolved_links"],
        "self_loops": list(apl_data["self_loops"]),
        "e_uniq": e_uniq,
        "undir_edges": undir_edges,
        "recip_directed_edges": recip_dir,
        "recip_pairs": recip_dir // 2,
        "oneway_directed_edges": oneway_dir,
        "reciprocity_ratio": frac_str(Fraction(recip_dir, e_uniq)),
        "reciprocity_dec6": frac_dec(Fraction(recip_dir, e_uniq), 6),
        "down_edges": down_e,
        "up_edges": up_e,
        "tier_matrix_full": tier_mat,
        "same_tier_edges": same_tier_e,
        "same_tier_ratio": frac_str(Fraction(same_tier_e, e_uniq)),
        "upper_e_count": len(upper_set),
        "upper_up": upper_up,
        "upper_down": upper_down,
        "lower_e_count": len(lower_set),
        "lower_down": lower_down,
        "lower_up": lower_up,
        "lower_down_ratio": frac_str(Fraction(lower_down, len(lower_set))) if lower_set else "0/1",
        "lower_tier_matrix": lower_tier_mat,
        "upper_lower_overlap": overlap_ul,
        "scc_count_full": len(sccs_full),
        "giant_scc_full": len(sccs_full[0]),
        "giant_scc_full_frac": frac_str(Fraction(len(sccs_full[0]), v_count)),
        "non_giant_sccs_full": [c for c in sccs_full[1:]],
        "scc_count_lower": len(sccs_lower),
        "giant_scc_lower": len(sccs_lower[0]),
        "giant_scc_lower_frac": frac_str(Fraction(len(sccs_lower[0]), v_count)),
        "undir_components": u_comps,
        "articulation_count": len(u_arts),
        "bridge_count": len(u_bridges),
        "biconnected_zero_cuts": (u_comps == 1 and len(u_arts) == 0 and len(u_bridges) == 0),
        "confidence_counts": dict(sorted(apl_data["confidence_counts"].items())),
        "nulls": {
            "n_shuffles": b_i,
            "seed": s_i,
            "recip_null_mean_dec4": frac_dec(Fraction(sum(null_full["recip"]), b_i), 4),
            "recip_ge_obs": ge_recip,
            "recip_p": frac_str(Fraction(1 + ge_recip, b_i + 1)),
            "recip_p_upper_dec6": frac_dec_ceil(Fraction(1 + ge_recip, b_i + 1), 6),
            "same_tier_null_mean_dec4": frac_dec(Fraction(sum(null_full["same_tier"]), b_i), 4),
            "same_tier_ge_obs": ge_same,
            "same_tier_p": frac_str(Fraction(1 + ge_same, b_i + 1)),
            "same_tier_p_upper_dec6": frac_dec_ceil(Fraction(1 + ge_same, b_i + 1), 6),
            "lower_down_null_mean_dec4": frac_dec(Fraction(sum(null_lower["down"]), b_i), 4),
            "lower_down_ge_obs": ge_lower_down,
            "lower_down_p": frac_str(Fraction(1 + ge_lower_down, b_i + 1)),
            "lower_down_p_upper_dec6": frac_dec_ceil(Fraction(1 + ge_lower_down, b_i + 1), 6),
        },
    }


def _rewire_bipartite_cooc_null(
    n_games: int,
    n_mechs: int,
    gm_idx_edges: Sequence[tuple[int, int]],
    n_shuffles: int,
    seed: int,
) -> list[int]:
    """Fast exact-int bitmask degree-preserving bipartite rewiring null for co-occurring pairs."""
    rr = random.Random(seed).randrange
    m = len(gm_idx_edges)
    swaps = 2 * m
    bits = [1 << k for k in range(n_mechs)]
    cooc_counts: list[int] = []

    for _ in range(n_shuffles):
        elist = list(gm_idx_edges)
        g_mask = [0] * n_games
        for g, mc in elist:
            g_mask[g] |= bits[mc]
        for _s in range(swaps):
            i = rr(m)
            j = rr(m)
            if i == j:
                continue
            g1, m1 = elist[i]
            g2, m2 = elist[j]
            if g1 == g2 or m1 == m2:
                continue
            bm2 = bits[m2]
            bm1 = bits[m1]
            if (g_mask[g1] & bm2) or (g_mask[g2] & bm1):
                continue
            m_xor = bm1 | bm2
            g_mask[g1] ^= m_xor
            g_mask[g2] ^= m_xor
            elist[i] = (g1, m2)
            elist[j] = (g2, m1)

        co_mask = [0] * n_mechs
        for gm in g_mask:
            rem = gm
            while rem:
                lsb = rem & -rem
                mi = lsb.bit_length() - 1
                co_mask[mi] |= gm
                rem ^= lsb
        total_deg = 0
        for mi in range(n_mechs):
            cm = co_mask[mi] & ~bits[mi]
            total_deg += cm.bit_count()
        cooc_counts.append(total_deg // 2)

    return cooc_counts


def analyze_simgrammar_live(
    sg_data: dict[str, Any], n_shuffles: int = 200, seed: int = 20261122
) -> dict[str, Any]:
    """Compute exact pure-Q recount, graph invariants, and B-shuffle nulls on simgrammar."""
    b_i = _require_exact_int(n_shuffles, "n_shuffles")
    s_i = _require_exact_int(seed, "seed")
    _require(b_i >= 100, "sg-shuffles-ge-100")

    games: list[dict[str, Any]] = sg_data["games"]
    mechs: list[dict[str, Any]] = sg_data["mechanics"]
    techs: list[dict[str, Any]] = sg_data["techniques"]
    n_games = len(games)
    n_mechs = len(mechs)
    n_techs = len(techs)
    mech_ids = sorted(m["id"] for m in mechs)
    mech_idx = {mid: i for i, mid in enumerate(mech_ids)}
    fam_by_m = {m["id"]: m["family"] for m in mechs}
    n_families = len(set(fam_by_m.values()))

    # Game-mechanic bipartite edges
    gm_edges = 0
    core_edges = 0
    supporting_edges = 0
    gm_idx_edges: list[tuple[int, int]] = []
    pre2000_set: set[str] = set()
    post2010_uses = 0
    post2010_from_pre2000 = 0
    cooc_pairs: set[tuple[str, str]] = set()

    for g in games:
        if g["year"] <= 2000:
            for item in g["mechanics"]:
                pre2000_set.add(item["id"])

    for gi, g in enumerate(games):
        mids_in_g: list[str] = []
        for item in g["mechanics"]:
            mid = item["id"]
            _require(mid in mech_idx, f"sg-unknown-game-mech:{g['id']}:{mid}")
            gm_edges += 1
            if item["role"] == "core":
                core_edges += 1
            elif item["role"] == "supporting":
                supporting_edges += 1
            gm_idx_edges.append((gi, mech_idx[mid]))
            mids_in_g.append(mid)
            if g["year"] >= 2010:
                post2010_uses += 1
                if mid in pre2000_set:
                    post2010_from_pre2000 += 1
        uniq_g = sorted(set(mids_in_g))
        for i in range(len(uniq_g)):
            for j in range(i + 1, len(uniq_g)):
                cooc_pairs.add((uniq_g[i], uniq_g[j]))

    total_possible_pairs = n_mechs * (n_mechs - 1) // 2

    # Technique-mechanic edges & family concentration
    tm_edges = 0
    touched_mechs: set[str] = set()
    global_fam_counts: dict[str, int] = {}
    tech_mech_lists: list[list[str]] = []
    for t in techs:
        t_mechs: list[str] = []
        for aff in t["affects"]:
            mid = aff["mechanic"]
            _require(mid in mech_idx, f"sg-unknown-tech-mech:{t['id']}:{mid}")
            tm_edges += 1
            touched_mechs.add(mid)
            t_mechs.append(mid)
            fm = fam_by_m[mid]
            global_fam_counts[fm] = global_fam_counts.get(fm, 0) + 1
        tech_mech_lists.append(t_mechs)

    unlinked_mechs = n_mechs - len(touched_mechs)
    unlinked_uses = sum(1 for g in games for item in g["mechanics"] if item["id"] not in touched_mechs)

    global_r2_num = sum(c * c for c in global_fam_counts.values())
    global_r2 = Fraction(global_r2_num, tm_edges * tm_edges)
    wt_num = 0
    wt_den = 0
    for t_mechs in tech_mech_lists:
        fc: dict[str, int] = {}
        for mid in t_mechs:
            fm = fam_by_m[mid]
            fc[fm] = fc.get(fm, 0) + 1
        wt_num += sum(c * c for c in fc.values())
        wt_den += len(t_mechs) * len(t_mechs)
    wt_r2 = Fraction(wt_num, wt_den)

    # Mechanic-mechanic relations
    rel_counts = {"requires": 0, "specializes": 0, "synergy": 0, "tension": 0}
    dep_adj: dict[str, set[str]] = {mid: set() for mid in mech_ids}
    all_uadj: dict[str, set[str]] = {mid: set() for mid in mech_ids}
    pair_rel_map: dict[tuple[str, str], list[str]] = {}
    for m in mechs:
        u = m["id"]
        for rk in ("requires", "specializes", "synergy", "tension"):
            for v in m["rels"][rk]:
                _require(v in mech_idx, f"sg-unknown-mech-rel:{u}:{rk}:{v}")
                rel_counts[rk] += 1
                if rk in ("requires", "specializes"):
                    dep_adj[u].add(v)
                all_uadj[u].add(v)
                all_uadj[v].add(u)
                pair = (u, v) if u < v else (v, u)
                pair_rel_map.setdefault(pair, []).append(rk)

    undir_mech_edges = sum(len(vs) for vs in all_uadj.values()) // 2
    overlap_mech_pairs = sorted([list(p) for p, rks in pair_rel_map.items() if len(rks) > 1])
    dep_sccs = tarjan_sccs(dep_adj)
    dep_nontriv_sccs = [c for c in dep_sccs if len(c) > 1]
    isolated_mechs = sum(1 for mid in mech_ids if len(all_uadj[mid]) == 0)
    m_comps, m_arts, m_bridges = undirected_articulations_and_bridges(all_uadj)

    # Exact pure-Q Spearman correlations across all mechanics
    em_vals = [m["scores"]["emergence_potential"] for m in mechs]
    lg_vals = [m["scores"]["legibility"] for m in mechs]
    tn_vals = [m["scores"]["tuning_difficulty"] for m in mechs]
    sgn_el, rho_sq_el, cov_el = exact_spearman_sq_and_sign(em_vals, lg_vals)
    sgn_et, rho_sq_et, cov_et = exact_spearman_sq_and_sign(em_vals, tn_vals)

    # Multi-shuffle nulls (B shuffles)
    cooc_nulls = _rewire_bipartite_cooc_null(n_games, n_mechs, gm_idx_edges, b_i, s_i)
    le_cooc = sum(1 for x in cooc_nulls if x <= len(cooc_pairs))

    rng = random.Random(s_i + 2)
    f_list = [fam_by_m[mid] for mid in mech_ids]
    all_aff_mechs = [mid for t_mechs in tech_mech_lists for mid in t_mechs]
    ge_global_r2 = 0
    ge_wt_r2 = 0
    null_gr2_nums: list[int] = []
    null_wtr2_nums: list[int] = []
    for _ in range(b_i):
        f_shuf = list(f_list)
        rng.shuffle(f_shuf)
        fmap = dict(zip(mech_ids, f_shuf))
        gfc: dict[str, int] = {}
        for mid in all_aff_mechs:
            fm = fmap[mid]
            gfc[fm] = gfc.get(fm, 0) + 1
        gn = sum(c * c for c in gfc.values())
        null_gr2_nums.append(gn)
        if gn >= global_r2_num:
            ge_global_r2 += 1

        wn = 0
        for t_mechs in tech_mech_lists:
            fc2: dict[str, int] = {}
            for mid in t_mechs:
                fm = fmap[mid]
                fc2[fm] = fc2.get(fm, 0) + 1
            wn += sum(c * c for c in fc2.values())
        null_wtr2_nums.append(wn)
        if wn >= wt_num:
            ge_wt_r2 += 1

    # Spearman exact integer permutation nulls (B shuffles)
    em_r = _midranks_doubled(em_vals)
    lg_r = _midranks_doubled(lg_vals)
    tn_r = _midranks_doubled(tn_vals)
    sum_r = n_mechs * (n_mechs + 1)
    le_el = 0
    ge_et = 0
    for _ in range(b_i):
        p_lg = list(lg_r)
        rng.shuffle(p_lg)
        if n_mechs * sum(a * b for a, b in zip(em_r, p_lg)) - sum_r * sum_r <= cov_el:
            le_el += 1
        p_tn = list(tn_r)
        rng.shuffle(p_tn)
        if n_mechs * sum(a * b for a, b in zip(em_r, p_tn)) - sum_r * sum_r >= cov_et:
            ge_et += 1

    p_global_r2 = Fraction(1 + ge_global_r2, b_i + 1)
    p_wt_r2 = Fraction(1 + ge_wt_r2, b_i + 1)

    return {
        "counts": {
            "games": n_games,
            "mechanics": n_mechs,
            "families": n_families,
            "techniques": n_techs,
            "total_opportunity_files": sg_data["total_opp_files"],
            "live_opportunities": len(sg_data["live_opportunities"]),
            "deprecated_opportunities": len(sg_data["deprecated_opportunities"]),
            "deprecated_opportunity_details": sg_data["deprecated_opportunities"],
            "sources": sg_data["source_count"],
        },
        "game_mechanic_bipartite": {
            "gm_edges": gm_edges,
            "core_edges": core_edges,
            "supporting_edges": supporting_edges,
            "pre2000_vocab_count": len(pre2000_set),
            "pre2000_vocab_share": frac_str(Fraction(len(pre2000_set), n_mechs)),
            "pre2000_vocab_dec4": frac_dec(Fraction(len(pre2000_set), n_mechs), 4),
            "post2010_uses": post2010_uses,
            "post2010_from_pre2000_uses": post2010_from_pre2000,
            "post2010_old_share": frac_str(Fraction(post2010_from_pre2000, post2010_uses)) if post2010_uses else "0/1",
            "post2010_old_dec4": frac_dec(Fraction(post2010_from_pre2000, post2010_uses), 4) if post2010_uses else "0.0000",
            "cooc_pairs": len(cooc_pairs),
            "total_possible_pairs": total_possible_pairs,
            "cooc_share": frac_str(Fraction(len(cooc_pairs), total_possible_pairs)),
            "cooc_dec4": frac_dec(Fraction(len(cooc_pairs), total_possible_pairs), 4),
        },
        "technique_mechanic_bipartite": {
            "tm_edges": tm_edges,
            "touched_mechs": len(touched_mechs),
            "unlinked_mechs": unlinked_mechs,
            "unlinked_uses": unlinked_uses,
            "unlinked_uses_share": frac_str(Fraction(unlinked_uses, gm_edges)),
            "unlinked_uses_dec4": frac_dec(Fraction(unlinked_uses, gm_edges), 4),
            "top_families": sorted(global_fam_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:6],
            "global_family_renyi2": frac_str(global_r2),
            "global_family_renyi2_dec6": frac_dec(global_r2, 6),
            "global_family_eff_diversity_d2_dec4": frac_dec(Fraction(1, 1) / global_r2, 4),
            "within_tech_family_renyi2": frac_str(wt_r2),
            "within_tech_family_renyi2_dec6": frac_dec(wt_r2, 6),
        },
        "mechanic_relation_graph": {
            "typed_edge_counts": rel_counts,
            "typed_edge_total": sum(rel_counts.values()),
            "undir_mech_edges": undir_mech_edges,
            "overlapping_multitype_pairs": overlap_mech_pairs,
            "dep_directed_edges": rel_counts["requires"] + rel_counts["specializes"],
            "dep_nontrivial_sccs": dep_nontriv_sccs,
            "dep_strict_dag": len(dep_nontriv_sccs) == 0,
            "isolated_mechs": isolated_mechs,
            "undir_components": m_comps,
            "articulation_count": len(m_arts),
            "bridge_count": len(m_bridges),
        },
        "spearman_rubric_correlations": {
            "emergence_vs_legibility_sign": sgn_el,
            "emergence_vs_legibility_rho_sq": frac_str(rho_sq_el),
            "emergence_vs_legibility_abs_rho_dec6": _isqrt_frac_dec(rho_sq_el, 6),
            "emergence_vs_tuning_sign": sgn_et,
            "emergence_vs_tuning_rho_sq": frac_str(rho_sq_et),
            "emergence_vs_tuning_abs_rho_dec6": _isqrt_frac_dec(rho_sq_et, 6),
        },
        "nulls": {
            "n_shuffles": b_i,
            "seed": s_i,
            "cooc_null_mean_pairs_dec2": frac_dec(Fraction(sum(cooc_nulls), b_i), 2),
            "cooc_null_mean_share_dec4": frac_dec(Fraction(sum(cooc_nulls), b_i * total_possible_pairs), 4),
            "cooc_le_obs": le_cooc,
            "cooc_p": frac_str(Fraction(1 + le_cooc, b_i + 1)),
            "cooc_p_upper_dec6": frac_dec_ceil(Fraction(1 + le_cooc, b_i + 1), 6),
            "global_family_r2_null_mean_dec6": frac_dec(Fraction(sum(null_gr2_nums), b_i * tm_edges * tm_edges), 6),
            "global_family_r2_ge_obs": ge_global_r2,
            "global_family_r2_p": frac_str(p_global_r2),
            "global_family_r2_p_upper_dec6": frac_dec_ceil(p_global_r2, 6),
            "global_family_r2_status": (
                "SIGNIFICANT_AT_ALPHA_005" if p_global_r2 <= Fraction(1, 20) else "NON_SIGNIFICANT_AT_ALPHA_005"
            ),
            "within_tech_r2_null_mean_dec6": frac_dec(Fraction(sum(null_wtr2_nums), b_i * wt_den), 6),
            "within_tech_r2_ge_obs": ge_wt_r2,
            "within_tech_r2_p": frac_str(p_wt_r2),
            "within_tech_r2_p_upper_dec6": frac_dec_ceil(p_wt_r2, 6),
            "spearman_em_lg_le_obs": le_el,
            "spearman_em_lg_p": frac_str(Fraction(1 + le_el, b_i + 1)),
            "spearman_em_lg_p_upper_dec6": frac_dec_ceil(Fraction(1 + le_el, b_i + 1), 6),
            "spearman_em_tn_ge_obs": ge_et,
            "spearman_em_tn_p": frac_str(Fraction(1 + ge_et, b_i + 1)),
            "spearman_em_tn_p_upper_dec6": frac_dec_ceil(Fraction(1 + ge_et, b_i + 1), 6),
        },
    }


def build_honest_structural_comparison(apl_res: dict[str, Any], sg_res: dict[str, Any]) -> dict[str, Any]:
    """Dimensionless graph comparison under strict Law 5 (documents divergences explicitly)."""
    mr = sg_res["mechanic_relation_graph"]
    n_mechs = sg_res["counts"]["mechanics"]
    apl_giant_lower = Fraction(apl_res["giant_scc_lower"], apl_res["v_count"])
    sg_art_frac = Fraction(mr["articulation_count"], n_mechs)
    sg_bridge_frac = Fraction(mr["bridge_count"], mr["undir_mech_edges"]) if mr["undir_mech_edges"] > 0 else Fraction(0, 1)

    return {
        "law5_anti_smuggling_note": (
            "Comparison restricted strictly to dimensionless graph observables computed from raw files; "
            "no shared-vocabulary unification is claimed between architectural patterns and game mechanics."
        ),
        "apl_giant_scc_lower_frac": frac_str(apl_giant_lower),
        "apl_biconnected_zero_cuts": apl_res["biconnected_zero_cuts"],
        "sg_dep_strict_dag": mr["dep_strict_dag"],
        "sg_mech_articulation_frac": frac_str(sg_art_frac),
        "sg_mech_bridge_frac": frac_str(sg_bridge_frac),
        "sg_global_tech_family_r2_status": sg_res["nulls"]["global_family_r2_status"],
        "topological_divergence_documented": (
            apl_giant_lower > Fraction(1, 2)
            and apl_res["biconnected_zero_cuts"]
            and mr["dep_strict_dag"]
            and mr["articulation_count"] > 0
            and mr["bridge_count"] > 0
        ),
    }


# =============================================================================
# FAIL-CLOSED CONSERVATION & AUDIT CERTIFIER (100% R5 MUTATION-HARDENED)
# =============================================================================


def _parse_frac_str(raw: Any, name: str) -> Fraction:
    s = _require_clean_ascii(raw, name)
    parts = s.split("/")
    _require(len(parts) == 2 and parts[0].lstrip("-").isdigit() and parts[1].isdigit(), f"frac-str:{name}")
    den = int(parts[1])
    _require(den > 0, f"frac-str-den:{name}")
    return Fraction(int(parts[0]), den)


def certify_pattern_sim_grammar_audit(
    apl_res: dict[str, Any], sg_res: dict[str, Any], comparison: dict[str, Any]
) -> dict[str, Any]:
    """Fail-closed exact conservation & Law-5 anti-smuggling audit gate for AUDIT-099."""
    _require(isinstance(apl_res, dict) and isinstance(sg_res, dict) and isinstance(comparison, dict), "audit-dicts")

    # 1. APL conservation invariants
    v = _require_exact_int(apl_res["v_count"], "apl.v_count")
    e = _require_exact_int(apl_res["e_uniq"], "apl.e_uniq")
    ue = _require_exact_int(apl_res["undir_edges"], "apl.undir_edges")
    rd = _require_exact_int(apl_res["recip_directed_edges"], "apl.recip_directed_edges")
    rp = _require_exact_int(apl_res["recip_pairs"], "apl.recip_pairs")
    ow = _require_exact_int(apl_res["oneway_directed_edges"], "apl.oneway_directed_edges")
    dn = _require_exact_int(apl_res["down_edges"], "apl.down_edges")
    up = _require_exact_int(apl_res["up_edges"], "apl.up_edges")
    st = _require_exact_int(apl_res["same_tier_edges"], "apl.same_tier_edges")
    tmat = apl_res["tier_matrix_full"]
    _require(isinstance(tmat, list) and len(tmat) == 3 and all(isinstance(r, list) and len(r) == 3 for r in tmat), "apl.tmat-shape")
    tmat_entries = [_require_exact_int(x, "apl.tmat") for row in tmat for x in row]
    _require(all(x >= 0 for x in tmat_entries), "apl.tmat-nonneg")
    tmat_sum = sum(tmat_entries)
    tmat_diag = tmat[0][0] + tmat[1][1] + tmat[2][2]

    le = _require_exact_int(apl_res["lower_e_count"], "apl.lower_e_count")
    ld = _require_exact_int(apl_res["lower_down"], "apl.lower_down")
    lu = _require_exact_int(apl_res["lower_up"], "apl.lower_up")
    scc_f = _require_exact_int(apl_res["scc_count_full"], "apl.scc_count_full")
    g_f = _require_exact_int(apl_res["giant_scc_full"], "apl.giant_scc_full")
    scc_l = _require_exact_int(apl_res["scc_count_lower"], "apl.scc_count_lower")
    g_l = _require_exact_int(apl_res["giant_scc_lower"], "apl.giant_scc_lower")
    u_c = _require_exact_int(apl_res["undir_components"], "apl.undir_components")
    arts = _require_exact_int(apl_res["articulation_count"], "apl.articulation_count")
    brdg = _require_exact_int(apl_res["bridge_count"], "apl.bridge_count")

    _require(v >= 2 and 0 <= e <= v * (v - 1), "apl-v-e-bounds")
    _require(dn >= 0 and up >= 0 and dn + up == e, "apl-down-up-sum")
    _require(rd >= 0 and ow >= 0 and rd % 2 == 0 and rp == rd // 2 and rd + ow == e, "apl-recip-sum")
    _require(ue == rp + ow, "apl-undir-edge-identity")
    _require(tmat_sum == e and tmat_diag == st, "apl-tier-matrix-conservation")
    _require(ld >= 0 and lu >= 0 and ld + lu == le and le <= e, "apl-lower-sum")
    _require(scc_f >= 1 and g_f + (scc_f - 1) <= v and scc_f * g_f >= v, "apl-scc-full-pigeonhole")
    _require(scc_l >= 1 and g_l + (scc_l - 1) <= v and scc_l * g_l >= v, "apl-scc-lower-pigeonhole")
    if g_f >= 2:
        _require(e >= g_f, "apl-scc-full-edge-min")
    if g_l >= 2:
        _require(le >= g_l, "apl-scc-lower-edge-min")
    _require(1 <= u_c <= v and 0 <= arts <= v - 2 and 0 <= brdg <= ue, "apl-cut-bounds")
    _require(v - u_c <= ue <= v * (v - 1) // 2, "apl-undir-edge-comp-bounds")
    if u_c == 1 and arts == 0 and brdg == 0:
        _require(ue >= v, "apl-biconnected-edge-min")
    apl_biconn = _require_exact_bool(apl_res.get("biconnected_zero_cuts"), "apl.biconnected_zero_cuts")
    _require(apl_biconn == (u_c == 1 and arts == 0 and brdg == 0), "apl-biconn-flag-match")

    apl_n = apl_res["nulls"]
    b_apl = _require_exact_int(apl_n["n_shuffles"], "apl.n_shuffles")
    _require(b_apl >= 100, "apl-shuffles-min")
    for ge_k, p_k in (("recip_ge_obs", "recip_p"), ("same_tier_ge_obs", "same_tier_p"), ("lower_down_ge_obs", "lower_down_p")):
        ge_v = _require_exact_int(apl_n[ge_k], f"apl.{ge_k}")
        _require(0 <= ge_v <= b_apl, f"apl-ge-range:{ge_k}")
        p_v = _parse_frac_str(apl_n[p_k], f"apl.{p_k}")
        _require(p_v == Fraction(1 + ge_v, b_apl + 1), f"apl-p-formula:{p_k}")

    # 2. SimGrammar conservation invariants
    cnt = sg_res["counts"]
    n_g = _require_exact_int(cnt["games"], "sg.games")
    n_m = _require_exact_int(cnt["mechanics"], "sg.mechanics")
    n_t = _require_exact_int(cnt["techniques"], "sg.techniques")
    tot_o = _require_exact_int(cnt["total_opportunity_files"], "sg.total_opps")
    live_o = _require_exact_int(cnt["live_opportunities"], "sg.live_opps")
    dep_o = _require_exact_int(cnt["deprecated_opportunities"], "sg.dep_opps")
    _require(n_g >= 2 and n_m >= 2 and n_t >= 1, "sg-entity-mins")
    _require(live_o >= 0 and dep_o >= 0 and live_o + dep_o == tot_o, "sg-opp-partition")

    gm = sg_res["game_mechanic_bipartite"]
    gm_e = _require_exact_int(gm["gm_edges"], "sg.gm_edges")
    c_e = _require_exact_int(gm["core_edges"], "sg.core_edges")
    s_e = _require_exact_int(gm["supporting_edges"], "sg.supporting_edges")
    pre2k = _require_exact_int(gm["pre2000_vocab_count"], "sg.pre2000")
    p2010 = _require_exact_int(gm["post2010_uses"], "sg.post2010_uses")
    p2010_o = _require_exact_int(gm["post2010_from_pre2000_uses"], "sg.post2010_old")
    cooc = _require_exact_int(gm["cooc_pairs"], "sg.cooc_pairs")
    tot_p = _require_exact_int(gm["total_possible_pairs"], "sg.total_possible_pairs")
    _require(c_e >= 0 and s_e >= 0 and c_e + s_e == gm_e and gm_e >= 1 and gm_e <= n_g * n_m, "sg-gm-role-sum")
    _require(0 <= pre2k <= n_m and 0 <= p2010_o <= p2010 <= gm_e, "sg-temporal-bounds")
    _require(tot_p == n_m * (n_m - 1) // 2 and 0 <= cooc <= tot_p, "sg-cooc-bounds")

    tm = sg_res["technique_mechanic_bipartite"]
    tm_e = _require_exact_int(tm["tm_edges"], "sg.tm_edges")
    tch = _require_exact_int(tm["touched_mechs"], "sg.touched_mechs")
    unl = _require_exact_int(tm["unlinked_mechs"], "sg.unlinked_mechs")
    unl_u = _require_exact_int(tm["unlinked_uses"], "sg.unlinked_uses")
    _require(tm_e >= 1 and tm_e <= n_t * n_m and tch >= 1 and unl >= 0 and tch + unl == n_m, "sg-tm-mech-partition")
    _require(0 <= unl_u <= gm_e, "sg-unlinked-uses-bounds")
    if unl == 0:
        _require(unl_u == 0, "sg-unlinked-zero-pigeonhole")
    gr2 = _parse_frac_str(tm["global_family_renyi2"], "sg.global_r2")
    wtr2 = _parse_frac_str(tm["within_tech_family_renyi2"], "sg.within_tech_r2")
    _require(Fraction(0, 1) < gr2 <= Fraction(1, 1), "sg-global-r2-range")
    _require(Fraction(0, 1) < wtr2 <= Fraction(1, 1), "sg-wt-r2-range")

    mr = sg_res["mechanic_relation_graph"]
    rc = mr["typed_edge_counts"]
    typed_tot = _require_exact_int(mr["typed_edge_total"], "sg.typed_edge_total")
    mr_ue = _require_exact_int(mr["undir_mech_edges"], "sg.undir_mech_edges")
    iso = _require_exact_int(mr["isolated_mechs"], "sg.isolated_mechs")
    mc = _require_exact_int(mr["undir_components"], "sg.undir_components")
    ma = _require_exact_int(mr["articulation_count"], "sg.mech_arts")
    mb = _require_exact_int(mr["bridge_count"], "sg.mech_bridges")
    rc_vals = [_require_exact_int(rc[k], f"sg.rc.{k}") for k in ("requires", "specializes", "synergy", "tension")]
    _require(all(x >= 0 for x in rc_vals) and sum(rc_vals) == typed_tot, "sg-typed-rel-sum")
    _require(0 <= mr_ue <= typed_tot and 0 <= iso <= n_m, "sg-mech-edge-bounds")
    _require(1 <= mc <= n_m and mc >= iso and 0 <= ma <= n_m - 2 and 0 <= mb <= mr_ue, "sg-mech-comp-bounds")
    non_iso = n_m - iso
    _require(
        mr_ue >= n_m - mc and mr_ue <= non_iso * (non_iso - 1) // 2 and 2 * mr_ue >= non_iso,
        "sg-mech-edge-comp-bounds",
    )
    if iso < n_m:
        _require(mc >= iso + 1, "sg-mech-noniso-comp-pigeonhole")
    mr_dag = _require_exact_bool(mr.get("dep_strict_dag"), "sg.dep_strict_dag")
    _require(
        isinstance(mr.get("dep_nontrivial_sccs"), list) and (len(mr["dep_nontrivial_sccs"]) == 0) == mr_dag,
        "sg-dep-dag-scc-match",
    )

    sp = sg_res["spearman_rubric_correlations"]
    s_el = _require_exact_int(sp["emergence_vs_legibility_sign"], "sg.s_el")
    s_et = _require_exact_int(sp["emergence_vs_tuning_sign"], "sg.s_et")
    rsq_el = _parse_frac_str(sp["emergence_vs_legibility_rho_sq"], "sg.rsq_el")
    rsq_et = _parse_frac_str(sp["emergence_vs_tuning_rho_sq"], "sg.rsq_et")
    _require(s_el in (-1, 0, 1) and s_et in (-1, 0, 1), "sg-spearman-signs")
    _require(Fraction(0, 1) <= rsq_el <= Fraction(1, 1) and Fraction(0, 1) <= rsq_et <= Fraction(1, 1), "sg-spearman-bounds")
    _require((s_el == 0) == (rsq_el == 0) and (s_et == 0) == (rsq_et == 0), "sg-spearman-sign-zero-match")

    sg_n = sg_res["nulls"]
    b_sg = _require_exact_int(sg_n["n_shuffles"], "sg.n_shuffles")
    _require(b_sg >= 100, "sg-shuffles-min")
    for ge_k, p_k in (
        ("cooc_le_obs", "cooc_p"),
        ("global_family_r2_ge_obs", "global_family_r2_p"),
        ("within_tech_r2_ge_obs", "within_tech_r2_p"),
        ("spearman_em_lg_le_obs", "spearman_em_lg_p"),
        ("spearman_em_tn_ge_obs", "spearman_em_tn_p"),
    ):
        ge_v = _require_exact_int(sg_n[ge_k], f"sg.{ge_k}")
        _require(0 <= ge_v <= b_sg, f"sg-ge-range:{ge_k}")
        p_v = _parse_frac_str(sg_n[p_k], f"sg.{p_k}")
        _require(p_v == Fraction(1 + ge_v, b_sg + 1), f"sg-p-formula:{p_k}")

    # 3. Honest significance & Law-5 anti-smuggling consistency
    p_gr2 = _parse_frac_str(sg_n["global_family_r2_p"], "sg.p_gr2")
    expected_gr2_status = (
        "SIGNIFICANT_AT_ALPHA_005" if p_gr2 <= Fraction(1, 20) else "NON_SIGNIFICANT_AT_ALPHA_005"
    )
    _require(sg_n["global_family_r2_status"] == expected_gr2_status, "sg-honest-r2-status")
    _require(comparison.get("sg_global_tech_family_r2_status") == expected_gr2_status, "comp-honest-r2-status")
    _require(comparison.get("apl_giant_scc_lower_frac") == frac_str(Fraction(g_l, v)), "comp-apl-scc-match")
    cmp_biconn = _require_exact_bool(comparison.get("apl_biconnected_zero_cuts"), "comp.apl_biconnected_zero_cuts")
    _require(cmp_biconn == apl_biconn, "comp-apl-biconn-match")
    cmp_dag = _require_exact_bool(comparison.get("sg_dep_strict_dag"), "comp.sg_dep_strict_dag")
    _require(cmp_dag == mr_dag, "comp-sg-dag-match")
    _require(comparison.get("sg_mech_articulation_frac") == frac_str(Fraction(ma, n_m)), "comp-sg-art-frac-match")
    expected_br_frac = frac_str(Fraction(mb, mr_ue)) if mr_ue > 0 else "0/1"
    _require(comparison.get("sg_mech_bridge_frac") == expected_br_frac, "comp-sg-bridge-frac-match")
    cmp_div = _require_exact_bool(
        comparison.get("topological_divergence_documented"), "comp.topological_divergence_documented"
    )
    expected_div = Fraction(g_l, v) > Fraction(1, 2) and apl_biconn and mr_dag and ma > 0 and mb > 0
    _require(cmp_div == expected_div, "comp-divergence-flag-match")

    violations: list[str] = []
    if not cmp_div:
        violations.append("LAW5_TOPOLOGICAL_DIVERGENCE_NOT_DOCUMENTED")

    return {
        "certified": len(violations) == 0,
        "violations": violations,
        "apl_conservation_ok": True,
        "simgrammar_conservation_ok": True,
        "global_tech_family_r2_honest_status": expected_gr2_status,
        "multi_shuffle_min_b_verified": min(b_apl, b_sg),
    }
