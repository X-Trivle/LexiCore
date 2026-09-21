#!/usr/bin/env python3
"""Rebuild `data/derived/` from a release checkpoint.

The checkpoint ships three compact pickles that are far more useful as plain
CSV: the surface->lemma map, the scored candidate table and the CEFR labels.
This script converts them (streaming, no pandas, ~1.5 GB peak RAM for the
largest input) and writes a manifest describing what was produced.

    python scripts/build_derived.py --checkpoint ../checkpoint/out --out data/derived

Run `make checksums` afterwards to refresh data/SHA256SUMS.txt.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

FEATURE_COLUMNS = [
    "word", "n_sources", "agg_lppm", "disp", "src_entropy", "total_f", "held_count",
    "wf_zipf2021", "ngsl_band", "ngsl_rank", "recent_share", "newest_share",
    "in_cefrj", "in_oct", "ngsl_spoken", "nawl", "bsl", "bnc_band",
]
LEVELS = ["A1", "A2", "B1", "B2", "C1"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cell(v) -> str:
    if v is None:
        return ""
    if v is True:
        return "1"
    if v is False:
        return "0"
    return str(v)


def write_feature_table(rows: list[dict], srcs: list[str], fh) -> int:
    header = FEATURE_COLUMNS + [f"{k}_{s}" for k in ("ppm", "dfr", "dp", "range") for s in srcs]
    w = csv.writer(fh)
    w.writerow(header)
    for r in rows:
        flat = [cell(r.get(c)) for c in FEATURE_COLUMNS]
        for key in ("ppm", "dfr", "dp", "range"):
            d = r.get(key) or {}
            flat += [cell(d.get(s)) for s in srcs]
        w.writerow(flat)
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoint", required=True, help="directory containing the checkpoint's out/*.pkl")
    ap.add_argument("--out", required=True, help="target directory (usually data/derived)")
    args = ap.parse_args(argv)

    ckpt, out = Path(args.checkpoint), Path(args.out)
    if not ckpt.is_dir():
        sys.exit(f"checkpoint dir not found: {ckpt}")
    out.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict] = {}

    def emit(name: str, writer_rows) -> None:
        target = out / name
        buf = io.StringIO()
        n = writer_rows(buf)
        # mtime=0 -> byte-for-byte reproducible output (make derived is idempotent)
        target.write_bytes(gzip.compress(buf.getvalue().encode("utf-8"), 9, mtime=0))
        files[name] = {"rows": n, "bytes": target.stat().st_size, "sha256": sha256(target)}
        print(f"  {name}: {n:,} rows -> {files[name]['bytes']:,} bytes")

    print(f"building derived data from {ckpt}")

    surface = pickle.load((ckpt / "surface_to_lemma.pkl").open("rb"))

    def _surface(b):
        w = csv.writer(b)
        w.writerow(["surface", "lemma"])
        for k in sorted(surface):
            w.writerow([k, surface[k]])
        return len(surface)

    emit("surface_to_lemma.csv.gz", _surface)

    feat = pickle.load((ckpt / "features.pkl").open("rb"))
    srcs = sorted(feat["totals"])

    def _feat(b):
        return write_feature_table(feat["table"], srcs, b)

    emit("candidate_features.csv.gz", _feat)

    labels = pickle.load((ckpt / "labels.pkl").open("rb"))

    def _labels(b):
        w = csv.writer(b)
        w.writerow(["lemma", "level", "label_source", "confidence"] + LEVELS)
        for k, v in labels.items():
            mp = v.get("model_proba") or {}
            w.writerow([k, cell(v.get("level")), cell(v.get("source")), cell(v.get("confidence"))]
                       + [cell(mp.get(lv)) for lv in LEVELS])
        return len(labels)

    emit("candidate_labels.csv.gz", _labels)

    (out / "derived_manifest.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": str(ckpt),
        "feature_columns": FEATURE_COLUMNS,
        "per_source_columns": [f"{k}_{s}" for k in ("ppm", "dfr", "dp", "range") for s in srcs],
        "files": files,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out / 'derived_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
