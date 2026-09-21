#!/usr/bin/env python3
"""Verify the integrity ledgers that ship with the release.

1. every hash in ``data/SHA256SUMS.txt``
2. the four artifact hashes declared inside ``data/MANIFEST.json``
3. sizes of the derived tables recorded in ``data/derived/derived_manifest.json``

Exit code is non-zero on any mismatch, so this is usable as a CI gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="data", help="path to the data/ directory")
    ap.add_argument("--root", default=None, help="repo root (defaults to --data/..)")
    args = ap.parse_args(argv)

    data = Path(args.data)
    root = Path(args.root) if args.root else data.parent
    failures: list[str] = []
    checked = 0

    ledger = data / "SHA256SUMS.txt"
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            target = root / rel
            checked += 1
            if not target.exists():
                failures.append(f"{rel}: missing")
            elif sha256(target) != digest:
                failures.append(f"{rel}: SHA-256 mismatch")
        print(f"SHA256SUMS.txt: {checked} files")
    else:
        failures.append(f"{ledger}: not found")

    manifest = data / "MANIFEST.json"
    if manifest.exists():
        doc = json.loads(manifest.read_text(encoding="utf-8"))
        for name, info in (doc.get("artifacts") or {}).items():
            target = data / name
            checked += 1
            if not target.exists():
                failures.append(f"artifact {name}: missing")
                continue
            if target.stat().st_size != info["bytes"]:
                failures.append(f"artifact {name}: size {target.stat().st_size} != {info['bytes']}")
            if sha256(target) != info["sha256"]:
                failures.append(f"artifact {name}: SHA-256 mismatch")
        print(f"MANIFEST artifacts: {len(doc.get('artifacts') or {})} files")

    dm = data / "derived" / "derived_manifest.json"
    if dm.exists():
        for name, info in json.loads(dm.read_text(encoding="utf-8"))["files"].items():
            target = data / "derived" / name
            checked += 1
            if not target.exists():
                failures.append(f"derived {name}: missing")
            elif target.stat().st_size != info["bytes"]:
                failures.append(f"derived {name}: size mismatch")
        print(f"derived manifest: {len(json.loads(dm.read_text())['files'])} files")

    if failures:
        print("\nFAIL:", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        return 1
    print(f"\nOK: {checked} files verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
