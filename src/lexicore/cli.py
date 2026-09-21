"""Command line interface: ``python -m lexicore`` or ``lexicore`` after install.

Examples
--------
    lexicore words --level A1                 # 1,000 A1 words, release order
    lexicore words --level C1 --sort alpha    # alphabetical handout
    lexicore show --word agreement            # one entry, all columns
    lexicore validate --json                  # machine-readable CI output
    lexicore stats                              # headline numbers
    lexicore reweight --freq 0.5 --disp 0.3     # compare against the shipped weights
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .io import load_entries
from .models import CORPUS_WORDS, LEVELS
from .select import DEFAULT_WEIGHTS, load_candidates, score_candidates, select_by_level
from .validate import validate_data


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lexicore", description="Query and verify the LexiCore-5000 list.")
    p.add_argument("--version", action="version", version=f"lexicore {__version__}")
    p.add_argument("--data", type=Path, default=None, help="path to a data/ directory")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("words", help="print headwords")
    s.add_argument("--level", choices=LEVELS, default=None)
    s.add_argument("--sort", choices=["rank", "alpha", "freq"], default="rank")
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--out", type=Path, default=None)

    s = sub.add_parser("show", help="print one entry as JSON")
    s.add_argument("--word", required=True)

    sub.add_parser("stats", help="headline numbers for the release")
    sub.add_parser("validate", help="run integrity checks").add_argument("--json", action="store_true")

    s = sub.add_parser("reweight", help="re-score the released candidate table with new weights")
    for k in DEFAULT_WEIGHTS:
        s.add_argument(f"--{k}", type=float, default=None, dest=f"w_{k}")
    s.add_argument("--per-level", type=int, default=1_000)
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    entries = load_entries(args.data / "LexiCore_5000.csv") if args.data else load_entries()

    if args.cmd == "words":
        rows = [e for e in entries if args.level is None or e.cefr_level == args.level]
        if args.sort == "alpha":
            rows.sort(key=lambda e: e.word)
        elif args.sort == "freq":
            rows.sort(key=lambda e: -e.total_count)
        if args.limit:
            rows = rows[: args.limit]
        text = "".join(f"{e.word}\n" for e in rows)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {len(rows)} words -> {args.out}", file=sys.stderr)
        else:
            sys.stdout.write(text)
        return 0

    if args.cmd == "show":
        for e in entries:
            if e.word == args.word:
                print(json.dumps(e.as_dict(), indent=2, ensure_ascii=False))
                return 0
        print(f"not found: {args.word}", file=sys.stderr)
        return 1

    if args.cmd == "stats":
        report = validate_data(args.data) if args.data else None
        stats = report.stats if report else {}
        from collections import Counter

        stats = stats or {
            "rows": len(entries),
            "levels": dict(Counter(e.cefr_level for e in entries)),
            "label_sources": dict(Counter(e.cefr_source for e in entries)),
            "total_count_sum": sum(e.total_count for e in entries),
            "corpus_words": CORPUS_WORDS,
            "share_of_corpus_covered": round(100 * sum(e.total_count for e in entries) / CORPUS_WORDS, 2),
        }
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "validate":
        report = validate_data(args.data) if args.data else validate_data()
        if args.json:
            print(json.dumps(report.as_dict(), indent=2))
        else:
            print(report.summary())
        return 0 if report.ok else 2

    if args.cmd == "reweight":
        weights = {k: v for k, v in
                   ((k, getattr(args, f"w_{k}")) for k in DEFAULT_WEIGHTS) if v is not None}
        pool = load_candidates()
        baseline = select_by_level(score_candidates(pool))
        tweaked = select_by_level(score_candidates(pool, weights), per_level=args.per_level)
        from .select import compare_selection

        print(json.dumps({"weights_applied": weights, "pool": len(pool),
                          "note": "baseline is rebuilt with the shipped weights, not the released CSV",
                          "compare": compare_selection(baseline, tweaked)}, indent=2))
        return 0

    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
