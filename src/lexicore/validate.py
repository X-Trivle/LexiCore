"""Integrity checks that CI and contributors can run.

Two kinds of checks live here on purpose:

* ``hard`` — must always pass.  A failure means the file was damaged or an
  edit broke the release contract (row count, duplicate words, quotas,
  SHA-256 ledger).
* ``expected`` — encodes the *known* state of release 1.0.0 (empty recency
  columns, POS quality, label mix).  If one of these stops holding, the
  release changed shape and the docs must change with it.
"""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from .io import CSV_NAME, DATA_ROOT
from .models import CSV_COLUMNS, LEVELS

EXPECTED_ROWS = 5_000
EXPECTED_PER_LEVEL = 1_000
QUANTITIES = {"rows": EXPECTED_ROWS, "per_level": EXPECTED_PER_LEVEL}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    kind: str = "hard"  # hard | expected

    def as_dict(self) -> dict:
        return {"check": self.name, "ok": self.ok, "detail": self.detail, "kind": self.kind}


@dataclass
class ValidationReport:
    checks: list[Check] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def hard_failures(self) -> list[Check]:
        return [c for c in self.checks if c.kind == "hard" and not c.ok]

    @property
    def drift(self) -> list[Check]:
        """Expected-state checks that no longer match the data."""
        return [c for c in self.checks if c.kind == "expected" and not c.ok]

    @property
    def ok(self) -> bool:
        return not self.hard_failures

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "hard_failures": [c.as_dict() for c in self.hard_failures],
            "drift": [c.as_dict() for c in self.drift],
            "checks": [c.as_dict() for c in self.checks],
            "stats": self.stats,
        }

    def summary(self) -> str:
        lines = []
        for c in self.checks:
            mark = "PASS" if c.ok else ("FAIL" if c.kind == "hard" else "DRIFT")
            lines.append(f"[{mark:<5}] {c.name:<26} {c.detail}")
        return "\n".join(lines)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check_ledger(root: Path | None = None) -> Check:
    """Verify every hash in data/SHA256SUMS.txt against the file on disk."""
    root = root or DATA_ROOT.parent
    ledger = root / "data" / "SHA256SUMS.txt"
    if not ledger.exists():
        return Check("ledger", False, "data/SHA256SUMS.txt missing")
    bad, n = [], 0
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        n += 1
        target = root / rel
        if not target.exists():
            bad.append(f"{rel}: missing")
        elif _sha256(target) != digest:
            bad.append(f"{rel}: hash mismatch")
    return Check("ledger", not bad, f"{n} files verified" + (f"; {bad}" if bad else ""), "hard")


def check_columns(rows: list[dict]) -> Check:
    got = tuple(rows[0].keys()) if rows else ()
    return Check("columns", got == CSV_COLUMNS, f"expected {len(CSV_COLUMNS)} columns, got {len(got)}")


def check_counts(entries) -> Check:
    n = len(entries)
    return Check("row_count", n == EXPECTED_ROWS, f"{n} rows (expected {EXPECTED_ROWS})")


def check_unique(entries) -> Check:
    words = [e.word for e in entries]
    dupes = {w for w in words if words.count(w) > 1} if len(set(words)) != len(words) else set()
    return Check("unique_headwords", not dupes, f"{len(set(words))} distinct" + (f"; dupes {sorted(dupes)[:5]}" if dupes else ""))


def check_quotas(entries) -> Check:
    from collections import Counter

    c = Counter(e.cefr_level for e in entries)
    bad = {lv: c.get(lv, 0) for lv in LEVELS if c.get(lv, 0) != EXPECTED_PER_LEVEL}
    extra = set(c) - set(LEVELS)
    ok = not bad and not extra
    detail = ", ".join(f"{lv}={c.get(lv, 0)}" for lv in LEVELS)
    if not ok:
        detail += f" | deviations {bad} unknown-levels {sorted(extra)}"
    return Check("level_quotas", ok, detail)


def check_ranks(entries) -> Check:
    """rank_global is 1..5000 with no gaps and ranks inside each level are 1..1000."""
    problems = []
    if sorted(e.rank_global for e in entries) != list(range(1, EXPECTED_ROWS + 1)):
        problems.append("rank_global is not a permutation of 1..5000")
    from collections import defaultdict

    per: dict[str, list[int]] = defaultdict(list)
    for e in entries:
        per[e.cefr_level].append(e.rank_in_level)
    for lv, vals in per.items():
        if sorted(vals) != list(range(1, len(vals) + 1)):
            problems.append(f"{lv}: rank_in_level not 1..n")
    return Check("rank_integrity", not problems, "; ".join(problems) or "contiguous per level and global")


def check_ranges(entries) -> Check:
    problems = []
    for e in entries:
        if e.total_count <= 0:
            problems.append(f"{e.word}: non-positive total_count")
        if not 0.0 <= e.confidence <= 1.0:
            problems.append(f"{e.word}: confidence out of [0,1]")
        if not 3 <= e.n_sources <= 5:
            problems.append(f"{e.word}: n_sources {e.n_sources}")
    return Check("value_ranges", not problems, "; ".join(problems[:3]) or "counts>0, 0<=confidence<=1, 3<=n_sources<=5")


def check_expected_release_shape(entries) -> list[Check]:
    """The 1.0.0 release's documented quirks — see docs/KNOWN_ISSUES.md."""
    from collections import Counter

    out = []
    recency_filled = sum(1 for e in entries if e.has_recency)
    out.append(Check(
        "recency_columns_empty", recency_filled == 0,
        f"{recency_filled}/{len(entries)} rows carry recency values "
        f"(1.0.0 ships them empty; KI-2)", "expected"))
    srcs = Counter(e.cefr_source for e in entries)
    expected_srcs = {"cefrj-v1.5": 3898, "octanove-c1c2-v1.0": 665, "model:multinomial-logit-v1": 437}
    out.append(Check("label_mix", dict(srcs) == expected_srcs, f"{dict(srcs)}", "expected"))
    confs = Counter(e.confidence for e in entries)
    out.append(Check(
        "profile_confidence_constant",
        confs.get(0.97, 0) == 3898 and confs.get(0.95, 0) == 665,
        f"{len(confs)} distinct values; 0.97 x{confs.get(0.97, 0)} (CEFR-J cap), "
        f"0.95 x{confs.get(0.95, 0)} (Octanove cap) — KI-5", "expected"))
    noun = sum(1 for e in entries if e.pos == "noun")
    out.append(Check(
        "pos_is_unreliable", abs(noun - 3598) <= 40,
        f"noun={noun}/5000 ({100 * noun / len(entries):.1f}%) — heuristic POS, KI-3", "expected"))
    in_all = sum(1 for e in entries if e.n_sources == 5)
    out.append(Check("ubiquity", in_all == 4953, f"{in_all} words in all 5 sources (99.06%)", "expected"))
    return out


def validate_data(root: Path | str | None = None) -> ValidationReport:
    """Run every check against a checkout directory (defaults to this repo).

    ``root`` is the repository root (the folder that contains ``data/``), or the
    ``data/`` directory itself.
    """
    from collections import Counter

    from .io import load_entries

    root = Path(root) if root else DATA_ROOT.parent
    if (root / "data").is_dir():
        data_dir = root / "data"
    elif (root / CSV_NAME).exists():
        data_dir, root = root, root.parent
    else:
        raise FileNotFoundError(f"no data/ directory under {root}")

    entries = load_entries(data_dir / CSV_NAME)
    with (data_dir / CSV_NAME).open(encoding="utf-8", newline="") as fh:
        raw = list(csv.DictReader(fh))

    report = ValidationReport()
    report.checks.append(check_columns(raw))
    report.checks.append(check_counts(entries))
    report.checks.append(check_unique(entries))
    report.checks.append(check_quotas(entries))
    report.checks.append(check_ranks(entries))
    report.checks.append(check_ranges(entries))
    report.checks.extend(check_expected_release_shape(entries))
    if not (data_dir / "SHA256SUMS.txt").exists():
        report.checks.append(Check("ledger", False, "data/SHA256SUMS.txt missing", "hard"))
    else:
        report.checks.append(check_ledger(root))

    total = sum(e.total_count for e in entries)
    report.stats = {
        "rows": len(entries),
        "total_count_sum": total,
        "corpus_words": 13_632_611_970,
        "share_of_corpus_covered": round(100 * total / 13_632_611_970, 2),
        "levels": {lv: sum(1 for e in entries if e.cefr_level == lv) for lv in LEVELS},
        "label_sources": dict(Counter(e.cefr_source for e in entries)),
        "distinct_confidence": len({e.confidence for e in entries}),
    }
    return report
