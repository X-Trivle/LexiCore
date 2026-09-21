"""LexiCore-5000 — a small, dependency-free reference implementation.

Public API
----------
load_entries, load_json_entries, iter_words, levels, entry_for
validate_data, ValidationReport
score_candidates, select_by_level, DEFAULT_WEIGHTS
"""
from __future__ import annotations

from .io import (
    DATA_ROOT,
    entry_for,
    iter_words,
    levels,
    load_entries,
    load_json_entries,
    words_by_level,
)
from .models import LEVELS, Entry
from .select import DEFAULT_WEIGHTS, Candidate, score_candidates, select_by_level
from .validate import Check, ValidationReport, validate_data

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "DATA_ROOT",
    "Entry",
    "LEVELS",
    "Check",
    "ValidationReport",
    "DEFAULT_WEIGHTS",
    "Candidate",
    "score_candidates",
    "select_by_level",
    "validate_data",
    "load_entries",
    "load_json_entries",
    "entry_for",
    "iter_words",
    "levels",
    "words_by_level",
]
