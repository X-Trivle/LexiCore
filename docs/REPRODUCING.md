# Reproducing and extending

## What is reproducible today

| task | status | how |
|---|---|---|
| Verify the artefacts are the released ones | ✅ now | `make checksums` (53-file ledger + 4 manifest hashes) |
| Verify the release contract (5,000 / 1,000 per level / ranks / ranges) | ✅ now | `make validate`, `make test` |
| Rebuild `data/derived/` from a release checkpoint | ✅ now, byte-identical | `make derived CHECKPOINT=/path/to/checkpoint/out` |
| Re-run **selection** with different weights over the released pool | ✅ now | `python -m lexicore reweight …` |
| Re-derive the CEFR **labels** | ❌ not from this repo | needs the anchor CSV/XLSX files (KI-12) |
| Re-run **counting** from the corpora | ❌ not from this repo | needs the pipeline code (KI-12) + ~66 GB of sources |

## What the checkpoint does *not* contain

The release was archived as `ckpt_lx5000v2_finalize_20260914T175041Z.tar.gz`
(SHA-256 `74aed1c2e249da6074dcc03ebbc00cfc4d1543efcbd8d080af0d8534acff26aa`, 374,861,085 bytes,
44 entries). It ships data, logs and flags — **no source code**. Extension census:
`pkl×9, log×12, json×7, flag×11, csv×2, md×1, txt×1`.

Runtime facts recoverable from the logs: driver at `/content/lexicore/pipeline/run.py`, 128 shards
per source, Python 3.13.15, numpy 2.1.3, pyarrow 25.0.1, scikit-learn 1.6.1,
`sklearn.linear_model.LogisticRegression` (multinomial) for the level model, NLTK for the gates.

### To make this a real build, ask for these paths

```
pipeline/run.py                    # driver: stages, retry, checkpoints, VERIFIED hashing
pipeline/env.py  collect.py  merge.py  label.py  select.py  finalize.py     # if split out
anchors/oxford-5k.csv
anchors/olp-en-cefrj/cefrj-vocabulary-profile-1.5.csv
anchors/olp-en-cefrj/octanove-vocabulary-profile-c1c2-1.0.csv
anchors/ngsl/NGSL-101-by-band-qq9o.xlsx   NGSL-101-with-SFI.xlsx   NGSL-Spoken-101.xlsx
anchors/nawl/NAWL_10_lemmatized_for_research.csv
anchors/misc/bsl.csv   anchors/misc/bnc_coca_25k.csv
requirements.txt  (or the pip freeze behind out/env.json)
```

Then a rebuild is: `python -m pipeline.run --stage all --corpus-root /data/lexicore`.

## Corpus inputs (public)

| source | fetch |
|---|---|
| fineweb | `HuggingFaceFW/fineweb` → `sample/10BT/00{0..4,…}_00000.parquet` (15 files, 30.6 GB) |
| fwedu | `HuggingFaceFW/fineweb-edu-score-2` → `data/CC-MAIN-2025-26/00{0..3}_00000.parquet` (5.8 GB) |
| wiki | `wikimedia/wikipedia` → `20231101.en/train-*-*-of-00041.parquet` (11.6 GB) |
| subs | `https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/mono/en.txt.gz` (9.5 GB) |
| cc2026 | `https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-34/segments/…/*.warc.wet.gz` (128 files, 8.2 GB) |

Exact URLs, per-file byte counts and SHA-256 are in `data/MANIFEST.json → sources[*].files`;
the `cc2026` records additionally carry `docs_seen`, `docs_en`, `docs_rejected_non_en` per file.

## The large pickles (not on GitHub)

`out/src_*.pkl` etc. total 743,006,691 bytes and several exceed GitHub's 100 MB per-file limit,
so they are **not** committed. Their sizes and SHA-256 are pinned in
[`docs/checkpoint_artifacts.json`](checkpoint_artifacts.json); fetch the tarball from the release
bucket and verify before use:

```bash
sha256sum ckpt_lx5000v2_finalize_20260914T175041Z.tar.gz
# expect 74aed1c2e249da6074dcc03ebbc00cfc4d1543efcbd8d080af0d8534acff26aa
tar -tzf ckpt_*.tar.gz            # 44 entries
python3 scripts/build_derived.py --checkpoint <extracted>/out --out /tmp/derived
diff <(zcat /tmp/derived/candidate_features.csv.gz | md5sum) <(zcat data/derived/candidate_features.csv.gz | md5sum)
```

## Data-quality work list (good first issues)

1. Recency: real year buckets from WARC `W-Date` → fill `recent_share_2022plus` /
   `newest_share_2025_2026`, then re-run `select` with `rec = 0.06` actually live
   ([KI-2](KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed)).
2. POS: UD-tag a stratified sample (≥200 occurrences per word) and publish `pos_senses`
   ([KI-3](KNOWN_ISSUES.md#ki-3-pos-is-a-dictionary-guess)).
3. `subs`: re-segment into ~500-word pseudo-documents, recompute `dfr`/`disp`
   ([KI-7](KNOWN_ISSUES.md#ki-7-dispersion-is-not-on-one-scale)).
4. Labels: replace the 437 model levels with an auditable interpolation over CEFR-J bands, and
   publish per-row CV error next to each model-labelled row
   ([KI-4](KNOWN_ISSUES.md#ki-4-437-words-are-levelled-by-a-weak-model)).
5. Add `rank_frequency` alongside `rank_in_level`
   ([KI-14](KNOWN_ISSUES.md#ki-14-ranks-inside-a-level-are-not-frequency-ranks)).
6. Add a `rejected_by_gate` breakdown to the funnel ([KI-13](KNOWN_ISSUES.md#ki-13-vocabulary-noise-survives-into-the-candidate-pool)).

Every item above has a machine-checkable expectation already wired into
`src/lexicore/validate.py` — fixing one flips its check to `DRIFT`, which is the reminder to
update this folder in the same PR.

## Licence hygiene for derived works

If you re-mix the list: the words and your annotations are yours (CC BY 4.0 applies to the
release's selection/ranking). The CEFR-J / NGSL / NAWL / BSL / Octanove *files* carry their own
terms and are not re-licensed here — see [NOTICE.md](../NOTICE.md).
