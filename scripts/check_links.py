#!/usr/bin/env python3
"""Fail if a relative markdown link points at a path that does not exist in the repo."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"\]\((?!https?:)([^)\s#]+)(#[^)]*)?\)")


def main() -> int:
    bad = []
    for p in sorted(ROOT.rglob("*.md")):
        if any(part in {".git", "node_modules"} for part in p.parts):
            continue
        for m in PATTERN.finditer(p.read_text(encoding="utf-8", errors="replace")):
            target = (p.parent / m.group(1)).resolve()
            if not target.exists():
                bad.append(f"{p.relative_to(ROOT)}: broken link -> {m.group(1)}")
    if bad:
        print("\n".join(bad))
        print(f"{len(bad)} broken relative link(s)")
        return 1
    n = sum(1 for _ in ROOT.rglob("*.md"))
    print(f"relative links OK across {n} markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
