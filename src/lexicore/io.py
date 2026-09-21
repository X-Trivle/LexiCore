"""Readers and writers for the released data files.

No third-party dependencies: the stdlib is enough for a 5,000-row list, and
keeping the loader dependency-free makes the data usable in notebooks, CI and
small tools.
"""
from __future__ import annotations

import csv
import gzip
import json
import os
from collections.abc import Iterator
from pathlib import Path

from .models import LEVELS, Entry

#: Override with ``LEXICORE_DATA=/path/to/data`` when the data lives elsewhere.
DATA_ROOT = Path(os.environ.get("LEXICORE_DATA", Path(__file__).resolve().parents[2] / "data"))

CSV_NAME = "LexiCore_5000.csv"
JSON_NAME = "LexiCore_5000.json"
TXT_NAME = "LexiCore_5000.txt"
MANIFEST_NAME = "MANIFEST.json"


def _csv_path(name: str) -> Path:
    p = DATA_ROOT / name
    if not p.exists():
        raise FileNotFoundError(
            f"{p} not found. Set LEXICORE_DATA to the directory containing "
            f"{CSV_NAME}, or clone the repository."
        )
    return p


def load_entries(path: Path | str | None = None) -> list[Entry]:
    """Load the 5,000 headwords in ``rank_global`` order."""
    p = Path(path) if path else _csv_path(CSV_NAME)
    if str(p).endswith(".gz"):
        with gzip.open(p, "rt", encoding="utf-8", newline="") as fh:
            return [Entry.from_row(r) for r in csv.DictReader(fh)]
    with p.open(encoding="utf-8", newline="") as fh:
        return [Entry.from_row(r) for r in csv.DictReader(fh)]


def load_json_entries(path: Path | str | None = None) -> list[dict]:
    """Load the JSON release (per-source ppm included) as plain dicts."""
    p = Path(path) if path else _csv_path(JSON_NAME)
    doc = json.loads(p.read_text(encoding="utf-8"))
    return doc["entries"] if isinstance(doc, dict) else doc


def load_manifest() -> dict:
    return json.loads(_csv_path(MANIFEST_NAME).read_text(encoding="utf-8"))


def iter_words(entries: Iterator[Entry] | list[Entry] | None = None) -> Iterator[str]:
    for e in entries if entries is not None else load_entries():
        yield e.word


def entry_for(word: str, entries: list[Entry] | None = None) -> Entry | None:
    """Look up a single headword (release order preserved elsewhere)."""
    entries = entries if entries is not None else load_entries()
    word = word.strip().lower()
    return next((e for e in entries if e.word == word), None)


def levels(entries: list[Entry] | None = None) -> dict[str, list[Entry]]:
    """Group entries by CEFR level, keeping the released order."""
    entries = entries if entries is not None else load_entries()
    grouped: dict[str, list[Entry]] = {lv: [] for lv in LEVELS}
    for e in entries:
        grouped.setdefault(e.cefr_level, []).append(e)
    return grouped


def words_by_level(level: str, alphabetical: bool = False) -> list[str]:
    if level not in LEVELS:
        raise ValueError(f"unknown level {level!r}; expected one of {', '.join(LEVELS)}")
    words = [e.word for e in load_entries() if e.cefr_level == level]
    return sorted(words) if alphabetical else words


def write_csv(entries: list[Entry], path: Path | str) -> Path:
    """Write entries back in the release CSV format (CRLF, header included)."""
    from .models import CSV_COLUMNS

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(CSV_COLUMNS), lineterminator="\r\n")
        w.writeheader()
        for e in entries:
            w.writerow(e.to_row())
    return path


def write_txt(entries: list[Entry], path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{e.word}\n" for e in entries), encoding="utf-8")
    return path
