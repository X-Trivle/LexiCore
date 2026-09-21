"""Typed view over a LexiCore release row.

The dataclass mirrors `data/LexiCore_5000.csv` one-to-one so that
CSV -> object -> CSV round-trips are loss-free (see tests/test_io.py).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

LEVELS: tuple[str, ...] = ("A1", "A2", "B1", "B2", "C1")
CSV_COLUMNS: tuple[str, ...] = (
    "rank_global",
    "rank_in_level",
    "word",
    "pos",
    "cefr_level",
    "cefr_source",
    "confidence",
    "n_sources",
    "total_count",
    "recent_share_2022plus",
    "newest_share_2025_2026",
    "wordfreq_zipf_2021_baseline",
)


@dataclass(frozen=True)
class Entry:
    """One headword.

    Notes on fields that the reader should not over-trust:

    * ``pos`` comes from a lightweight dictionary lookup, not from tagging the
      corpora.  Function words are frequently wrong (e.g. ``at`` -> ``noun``).
      See docs/KNOWN_ISSUES.md#KI-3.
    * ``recent_share_2022plus`` / ``newest_share_2025_2026`` are empty in the
      1.0.0 release: the recency axis never reached the feature table.
      ``has_recency`` is provided so downstream code can degrade cleanly.
    * ``confidence`` is a constant 0.97 (CEFR-J) or 0.95 (Octanove) for
      profile-derived labels; only ``cefr_source`` starting with ``model:``
      carries a real posterior probability.
    """

    rank_global: int
    rank_in_level: int
    word: str
    pos: str
    cefr_level: str
    cefr_source: str
    confidence: float
    n_sources: int
    total_count: int
    recent_share_2022plus: float | None = None
    newest_share_2025_2026: float | None = None
    wordfreq_zipf_2021_baseline: float | None = None

    # ------------------------------------------------------------------ parsing
    @classmethod
    def from_row(cls, row: dict[str, str]) -> Entry:
        def num(key: str, cast):
            raw = (row.get(key) or "").strip()
            return cast(raw) if raw else None

        return cls(
            rank_global=int(row["rank_global"]),
            rank_in_level=int(row["rank_in_level"]),
            word=row["word"].strip(),
            pos=(row.get("pos") or "").strip(),
            cefr_level=row["cefr_level"].strip(),
            cefr_source=row["cefr_source"].strip(),
            confidence=num("confidence", float) or 0.0,
            n_sources=int(row["n_sources"]),
            total_count=int(row["total_count"]),
            recent_share_2022plus=num("recent_share_2022plus", float),
            newest_share_2025_2026=num("newest_share_2025_2026", float),
            wordfreq_zipf_2021_baseline=num("wordfreq_zipf_2021_baseline", float),
        )

    def to_row(self) -> dict[str, str]:
        """Serialise back to CSV text exactly as the release formats it."""

        def fmt(v: Any) -> str:
            if v is None:
                return ""
            if isinstance(v, float):
                # release uses repr-style floats for confidence/zipf, ints for counts
                s = f"{v:.10g}"
                return s
            return str(v)

        return {
            "rank_global": fmt(self.rank_global),
            "rank_in_level": fmt(self.rank_in_level),
            "word": self.word,
            "pos": self.pos,
            "cefr_level": self.cefr_level,
            "cefr_source": self.cefr_source,
            "confidence": fmt(self.confidence),
            "n_sources": fmt(self.n_sources),
            "total_count": fmt(self.total_count),
            "recent_share_2022plus": fmt(self.recent_share_2022plus),
            "newest_share_2025_2026": fmt(self.newest_share_2025_2026),
            "wordfreq_zipf_2021_baseline": fmt(self.wordfreq_zipf_2021_baseline),
        }

    # ------------------------------------------------------------------ helpers
    @property
    def model_labeled(self) -> bool:
        return self.cefr_source.startswith("model:")

    @property
    def has_recency(self) -> bool:
        return self.recent_share_2022plus is not None or self.newest_share_2025_2026 is not None

    @property
    def per_million(self) -> float:
        """Corpus-wide frequency in parts per million (13,632,611,970 words)."""
        return 1e6 * self.total_count / CORPUS_WORDS

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


CORPUS_WORDS = 13_632_611_970  # from data/MANIFEST.json -> stats.total_words


@dataclass
class CorpusStats:
    """Aggregate figures quoted by the release, kept in one place."""

    total_words: int = CORPUS_WORDS
    sources: dict = field(
        default_factory=lambda: {
            "fineweb": 7_545_397_544,
            "fwedu": 1_509_381_045,
            "wiki": 2_172_583_977,
            "subs": 1_103_261_872,
            "cc2026": 1_301_987_532,
        }
    )
