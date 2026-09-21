"""Tests for the LexiCore package.

Run with ``make test`` or ``python -m pytest``.  The suite is deliberately split:

* data-contract tests read the released CSV (they fail if data is corrupted);
* unit tests use tiny in-memory fixtures (they pin the library behaviour).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from lexicore import (
    DEFAULT_WEIGHTS,
    LEVELS,
    Candidate,
    Entry,
    load_entries,
    load_json_entries,
    score_candidates,
    select_by_level,
    validate_data,
    words_by_level,
)

DATA = Path(__file__).resolve().parents[1] / "data"


# --------------------------------------------------------------- data contract
def test_row_count_and_levels():
    entries = load_entries()
    assert len(entries) == 5000
    counts = {lv: sum(1 for e in entries if e.cefr_level == lv) for lv in LEVELS}
    assert counts == dict.fromkeys(LEVELS, 1000)


def test_headwords_unique_and_lowercase_ascii():
    words = [e.word for e in load_entries()]
    assert len(set(words)) == len(words)
    assert all(w == w.strip().lower() for w in words)
    assert all(w.replace("-", "").replace("'", "").isalpha() for w in words), "single-word headwords only"


def test_rank_columns_are_permutations():
    entries = load_entries()
    assert sorted(e.rank_global for e in entries) == list(range(1, 5001))
    for lv in LEVELS:
        assert sorted(e.rank_in_level for e in entries if e.cefr_level == lv) == list(range(1, 1001))


def test_known_top_words_are_a1():
    entries = {e.word: e for e in load_entries()}
    for w in ("the", "be", "from", "and"):
        assert entries[w].cefr_level == "A1"


def test_recency_columns_are_empty_in_1_0_0():
    """Release 1.0.0 ships the recency axis unpopulated (docs/KNOWN_ISSUES.md)."""
    entries = load_entries()
    assert not any(e.has_recency for e in entries)


def test_total_count_matches_the_released_aggregate():
    total = sum(e.total_count for e in load_entries())
    assert total == 9_705_062_231


def test_csv_round_trip_is_lossless(tmp_path):
    from lexicore.io import write_csv

    entries = load_entries()
    p = write_csv(entries, tmp_path / "out.csv")
    assert load_entries(p) == entries


def test_json_and_csv_agree_on_the_word_set():
    csv_words = {e.word for e in load_entries()}
    json_words = {e["word"] for e in load_json_entries()}
    assert csv_words == json_words


def test_manifest_declares_the_shipped_hashes():
    manifest = json.loads((DATA / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["validation"]["level_counts"] == dict.fromkeys(LEVELS, 1000)
    assert manifest["stats"]["total_words"] == 13_632_611_970
    assert set(manifest["sources"]) == {"fineweb", "fwedu", "wiki", "subs", "cc2026"}


def test_validate_data_passes():
    report = validate_data(DATA.parent)
    assert report.ok, report.summary()
    assert not report.drift, "expected-state checks drifted; update docs/KNOWN_ISSUES.md"


# --------------------------------------------------------------- unit behaviour
def test_entry_from_row_handles_empty_optionals():
    row = {
        "rank_global": "7", "rank_in_level": "3", "word": "test", "pos": "noun",
        "cefr_level": "A2", "cefr_source": "cefrj-v1.5", "confidence": "0.97",
        "n_sources": "5", "total_count": "123", "recent_share_2022plus": "",
        "newest_share_2025_2026": "", "wordfreq_zipf_2021_baseline": "4.1",
    }
    e = Entry.from_row(row)
    assert e.recent_share_2022plus is None and e.wordfreq_zipf_2021_baseline == 4.1
    assert e.model_labeled is False and not e.has_recency
    assert e.to_row()["confidence"] == "0.97"


def test_words_by_level_rejects_unknown_level():
    with pytest.raises(ValueError):
        words_by_level("C2")


def test_score_candidates_is_deterministic_and_weight_sensitive():
    pool = [
        Candidate("alpha", agg_lppm=9.0, disp=0.9, src_entropy=0.95, rng=1.0, df=0.8, util=1.0, level="A1", n_sources=5, total_f=100),
        Candidate("beta", agg_lppm=2.0, disp=0.2, src_entropy=0.30, rng=0.4, df=0.1, util=0.2, level="A1", n_sources=5, total_f=10),
        Candidate("gamma", agg_lppm=5.5, disp=0.6, src_entropy=0.70, rng=0.8, df=0.5, util=0.6, level="A1", n_sources=5, total_f=40),
    ]
    first = score_candidates(pool)
    assert all(isinstance(s, float) for _, s in first)
    assert [c.word for c, _ in first] == ["alpha", "gamma", "beta"]
    assert score_candidates(pool) == first, "scoring must be reproducible"
    single = score_candidates(pool, {"freq": 1.0, "disp": 0.0, "util": 0.0, "ent": 0.0,
                                    "rng": 0.0, "df": 0.0, "rec": 0.0})
    # ranking here is monotone in agg_lppm, so the order is unchanged ...
    assert [c.word for c, _ in single] == [c.word for c, _ in first]
    # ... but the scores are the freq-only z-scores, not the blended ones
    assert [s for _, s in single] != [s for _, s in first]
    import statistics

    vals = {"alpha": 9.0, "gamma": 5.5, "beta": 2.0}
    mean, sd = statistics.mean(list(vals.values())), statistics.pstdev(list(vals.values()))
    got = {c.word: s for c, s in single}
    assert got == pytest.approx({k: (v - mean) / sd for k, v in vals.items()}, abs=1e-4)
    with pytest.raises(ValueError):
        score_candidates(pool, {"bogus": 1.0})


def test_constant_feature_column_is_inert():
    """A column with zero variance (e.g. the missing recency axis) must not reorder."""
    pool = [
        Candidate("a", agg_lppm=1, disp=1, src_entropy=1, rng=1, df=1, util=1, recent_share=None, level="A1", n_sources=5),
        Candidate("b", agg_lppm=2, disp=2, src_entropy=2, rng=2, df=2, util=2, recent_share=None, level="A1", n_sources=5),
    ]
    scored = score_candidates(pool, {"rec": 0.06})
    assert [c.word for c, _ in scored] == ["b", "a"]


def test_select_by_level_respects_quota_and_min_sources():
    pool = [Candidate(f"w{i}", agg_lppm=i, disp=i / 10, src_entropy=0.5, rng=0.5, df=0.5,
                       util=0.5, level="A1", n_sources=5, total_f=10 * i) for i in range(5)]
    pool.append(Candidate("rare", agg_lppm=99, disp=9, src_entropy=9, rng=9, df=9, util=9,
                          level="A1", n_sources=2, total_f=1))
    picked = select_by_level(score_candidates(pool), per_level=3, min_sources=3)
    assert [c.word for c, _ in picked["A1"]] == ["w4", "w3", "w2"]
    assert all(o == 0 for lv, rows in picked.items() if lv != "A1" for _, o in rows)


def test_default_weights_sum_to_one():
    assert round(sum(DEFAULT_WEIGHTS.values()), 6) == 1.0
