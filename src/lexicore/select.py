"""Re-implementation of the release's selection score, for tinkering.

This is **not** upstream pipeline code — the pipeline that built release 1.0.0
lives outside this repository (see docs/REPRODUCING.md).  What this module does
is restate the published formula from ``MANIFEST.json`` + ``select_report.json``
so that maintainers can:

* re-run the quota fill on the released candidate table
  (``data/derived/candidate_features.csv.gz``);
* experiment with a different weight vector and diff the resulting word lists;
* reproduce the *shape* of the selection (not a bit-for-bit rebuild of it).

Formula (from the release metadata)
-----------------------------------
``score = Σ wᵢ · zᵢ`` over, per candidate:

===========  =============================================  ======
weight key   feature                                        weight
===========  =============================================  ======
``freq``     ``agg_lppm`` (log parts-per-million, pooled)   0.34
``disp``     ``disp`` (document dispersion, pooled)         0.18
``util``     utility from NGSL/NAWL/BSL membership          0.18
``ent``      ``src_entropy`` (balance across the 5 sources) 0.10
``rng``      ``range`` (span of per-source frequency)       0.08
``df``       ``dfr`` (fraction of documents containing it)  0.06
``rec``      ``recent_share`` — **absent in 1.0.0**         0.06
===========  =============================================  ======
"""
from __future__ import annotations

import csv
import gzip
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .io import DATA_ROOT
from .models import LEVELS

DEFAULT_WEIGHTS: dict[str, float] = {
    "freq": 0.34,
    "disp": 0.18,
    "util": 0.18,
    "ent": 0.10,
    "rng": 0.08,
    "df": 0.06,
    "rec": 0.06,
}


@dataclass(frozen=True)
class Candidate:
    """A row of the released candidate table, reduced to scoreable features."""

    word: str
    agg_lppm: float = 0.0
    disp: float = 0.0
    src_entropy: float = 0.0
    rng: float = 0.0
    df: float = 0.0
    recent_share: float | None = None
    util: float = 0.0
    level: str = ""
    label_source: str = ""
    total_f: int = 0
    n_sources: int = 0


def _f(row: dict, key: str, default: float = 0.0) -> float:
    raw = (row.get(key) or "").strip()
    if raw in ("", "None", "nan"):
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _opt_f(row: dict, key: str) -> float | None:
    raw = (row.get(key) or "").strip()
    if raw in ("", "None", "nan"):
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def util_from_lists(row: dict) -> float:
    """Utility signal: NGSL band membership, rank depth, NAWL/BSL flags.

    The release documented a 0.18 "util" weight without publishing its exact
    internals; this is a transparent reconstruction: band-1 NGSL = 1.0,
    band-2 = 0.6, band-3 = 0.35, outside = 0.0, +0.15 for NAWL, +0.10 for BSL,
    +0.05 for NGSL-Spoken, and a small rank-depth term (max 0.15).
    """
    band = row.get("ngsl_band") or ""
    base = {"1": 1.0, "2": 0.6, "3": 0.35}.get(band.strip(), 0.0)
    bonus = 0.0
    bonus += 0.15 if str(row.get("nawl", "")).lower() in ("1", "true") else 0.0
    bonus += 0.10 if str(row.get("bsl", "")).lower() in ("1", "true") else 0.0
    bonus += 0.05 if str(row.get("ngsl_spoken", "")).lower() in ("1", "true") else 0.0
    rank = _f(row, "ngsl_rank", 0.0)
    depth = 0.0 if rank <= 0 else 0.15 / (1.0 + math.log10(rank))
    return min(1.0, base + bonus + depth)


def _mean_of(row: dict, prefix: str) -> float:
    """Average a per-source column family (``dfr_fineweb``, ``dfr_wiki``, …).

    The released feature table stores ``dfr``/``range`` per source only; the
    scalar used for scoring is their unweighted mean, which is what the
    release's own ``disp``/``src_entropy`` aggregates are built from.
    """
    vals = [_f(row, k) for k in row if k.startswith(prefix + "_")]
    return sum(vals) / len(vals) if vals else 0.0


def load_candidates(path: Path | str | None = None) -> list[Candidate]:
    """Read ``data/derived/candidate_features.csv.gz`` into Candidates."""
    path = Path(path) if path else DATA_ROOT / "derived" / "candidate_features.csv.gz"
    opener = gzip.open if str(path).endswith(".gz") else open
    out: list[Candidate] = []
    with opener(path, "rt", encoding="utf-8", newline="") as fh:  # type: ignore[operator]
        for row in csv.DictReader(fh):
            out.append(
                Candidate(
                    word=row["word"],
                    agg_lppm=_f(row, "agg_lppm"),
                    disp=_f(row, "disp"),
                    src_entropy=_f(row, "src_entropy"),
                    rng=_f(row, "range") or _mean_of(row, "range"),
                    df=_f(row, "dfr") or _mean_of(row, "dfr"),
                    recent_share=_opt_f(row, "recent_share"),
                    util=util_from_lists(row),
                    level=row.get("in_cefrj") or row.get("in_oct") or "C1",
                    total_f=int(_f(row, "total_f")),
                    n_sources=int(_f(row, "n_sources")),
                )
            )
    return out


def _zscores(values: list[float]) -> list[float]:
    """Standardise; a constant column collapses to 0.0 (no ranking signal)."""
    n = len(values)
    if n == 0:
        return []
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    sd = math.sqrt(var)
    if sd == 0:
        return [0.0] * n
    return [(v - mean) / sd for v in values]


def score_candidates(cands: list[Candidate], weights: dict[str, float] | None = None) -> list[tuple[Candidate, float]]:
    """Return ``(candidate, score)`` using z-scores over the given pool."""
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        unknown = set(weights) - set(DEFAULT_WEIGHTS)
        if unknown:
            raise ValueError(f"unknown weight keys: {sorted(unknown)}")
        w.update(weights)
    keys = ["agg_lppm", "disp", "util", "src_entropy", "rng", "df"]
    cols = {k: _zscores([getattr(c, k) for c in cands]) for k in keys}
    # rec: absent in 1.0.0 -> constant 0.0, i.e. its 0.06 weight is inert
    rec = _zscores([(c.recent_share or 0.0) for c in cands])
    weight_for = {"agg_lppm": "freq", "disp": "disp", "util": "util",
                  "src_entropy": "ent", "rng": "rng", "df": "df"}
    scored: list[tuple[Candidate, float]] = []
    for i, c in enumerate(cands):
        s = sum(w[weight_for[k]] * cols[k][i] for k in keys) + w["rec"] * rec[i]
        scored.append((c, round(s, 5)))
    scored.sort(key=lambda t: (-t[1], t[0].word))
    return scored


def select_by_level(scored: list[tuple[Candidate, float]], per_level: int = 1_000,
                    min_sources: int = 3) -> dict[str, list[tuple[Candidate, float]]]:
    """Greedy quota fill: top ``per_level`` eligible candidates in each level."""
    buckets: dict[str, list[tuple[Candidate, float]]] = defaultdict(list)
    for item in scored:
        c, _ = item
        if c.n_sources < min_sources:
            continue
        lv = c.level if c.level in LEVELS else "C1"
        if len(buckets[lv]) < per_level:
            buckets[lv].append(item)
    return {lv: buckets.get(lv, []) for lv in LEVELS}


def compare_selection(a: dict[str, list[tuple[Candidate, float]]],
                      b: dict[str, list[tuple[Candidate, float]]]) -> dict:
    """Overlap statistics between two selections (e.g. baseline vs. tweaked)."""
    aw = {c.word for rows in a.values() for c, _ in rows}
    bw = {c.word for rows in b.values() for c, _ in rows}
    inter = aw & bw
    union = aw | bw
    return {
        "n_a": len(aw),
        "n_b": len(bw),
        "shared": len(inter),
        "jaccard": round(len(inter) / len(union), 4) if union else 0.0,
        "only_a": sorted(aw - bw)[:20],
        "only_b": sorted(bw - aw)[:20],
    }
