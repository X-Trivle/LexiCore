#!/usr/bin/env python3
"""Regenerate ``data/SHA256SUMS.txt`` (the repository's integrity ledger).

Run this after any deliberate change to `data/`, `docs/` or `ecosystem/`, then
commit the updated ledger together with the change — CI verifies it.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

SKIP_NAMES = {"SHA256SUMS.txt", "build_facts.json"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="repository root")
    ap.add_argument("--include", default="data,docs,ecosystem,reports",
                    help="comma-separated top-level dirs to hash")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    lines = []
    for top in [t.strip() for t in args.include.split(",") if t.strip()]:
        base = root / top
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.name not in SKIP_NAMES:
                lines.append(f"{sha256(p)}  {p.relative_to(root).as_posix()}")
    out = root / "data" / "SHA256SUMS.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(root)}: {len(lines)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
