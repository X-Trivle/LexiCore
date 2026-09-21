# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the dataset version follows
semver-as-applied-to-data: **major** = words added/removed or levels changed,
**minor** = new columns/derived tables, **patch** = docs, tooling, errata.

## [1.0.0] - 2026-09-14

### Added
- `LexiCore_5000` — 5,000 single-token English headwords, 1,000 each in A1/A2/B1/B2/C1,
  ranked by a weighted score over frequency (0.34), dispersion (0.18), teaching-list utility
  (0.18), source entropy (0.10), range (0.08), document frequency (0.06) and recency (0.06).
- Counting evidence over five corpora totalling 13,632,611,970 words:
  FineWeb `sample/10BT`, FineWeb-Edu-score-2, Wikipedia `20231101.en`,
  OPUS-OpenSubtitles v2024, Common Crawl `CC-MAIN-2026-34`.
- CEFR levels from CEFR-J v1.5 (3,898) and Octanove C1/C2 (665), with a multinomial logistic
  model for the remaining 437 (CV accuracy 0.3814, macro-F1 0.3829).
- External comparison against Oxford 5000 (never used in construction): 3,526 shared,
  Jaccard 0.5508, exact level agreement 0.466, quadratic-weighted κ 0.7124.
- Release manifest with per-file URLs, byte sizes and SHA-256 for every input.

### Known in this release (documented, not hidden)
- `recent_share_2022plus` and `newest_share_2025_2026` are empty for all 5,000 rows: the recency
  axis never reached the feature table, so its 0.06 weight was inert
  ([KI-2](docs/KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed)).
- `pos` is a dictionary lookup, not corpus tagging ([KI-3](docs/KNOWN_ISSUES.md#ki-3-pos-is-a-dictionary-guess)).
- `confidence` for profile-derived labels is a constant cap, not a posterior
  ([KI-5](docs/KNOWN_ISSUES.md#ki-5-confidence-is-a-cap-not-a-calibrated-probability)).
- The upstream `REPORT.md` "modern additions, ranked by 2025-26 evidence" section is alphabetical
  ([KI-1](docs/KNOWN_ISSUES.md#ki-1-a-ranked-list-that-is-not-ranked)).
- Pipeline source code and the anchor wordlist files are not in the release checkpoint
  ([KI-12](docs/KNOWN_ISSUES.md#ki-12-the-pipeline-code-is-not-in-the-release)).

## [1.0.0+repo] - 2026-09-21

### Added
- Public repository packaging of the release: data, docs, tooling.
- `data/SHA256SUMS.txt` integrity ledger over every data, docs, ecosystem and report file, plus
  `make checksums` / `make ledger`.
- `data/lists/` per-level handouts (rank order and alphabetical).
- `data/derived/`: `candidate_features.csv.gz` (215,416 candidates × the full feature vector),
  `candidate_labels.csv.gz` (levels, sources, confidences, class probabilities),
  `surface_to_lemma.csv.gz` (283,502 forms) — deterministic rebuild via `make derived`.
- `lexicore` Python package: `Entry` model, CSV/JSON/TXT loaders, `validate_data()`,
  a re-scoring harness for the published formula, and a CLI (`words`, `show`, `stats`,
  `validate`, `reweight`).
- 16 pytest cases: release contract + library behaviour, including loss-free CSV round-trip.
- `docs/`: methodology, provenance (with live re-verification of source URLs/hashes), data
  dictionary, validation, known issues, reproduction guide, artefact ledger.
- CI (GitHub Actions) running validate / ledger / test / lint / link-check on Python 3.10, 3.12, 3.13.
- GitHub Release [`v1.0.0`](https://github.com/X-Trivle/LexiCore/releases/tag/v1.0.0) carrying the
  374,861,085-byte release checkpoint as an asset (round-trip SHA-256 verified), so the payloads
  excluded by GitHub's 100 MB file limit are still obtainable.
- `ecosystem/lexideck-multilingual/`: the companion Anki deck (≈5,700 words = this list plus
  ~700 additions), its card model schema as measured from the free sample, and screenshots.

### Changed
- Upstream artefacts kept unmodified under `reports/upstream/`; only the files in `data/` are
  renamed/documented by this repository.

### Not changed (on purpose)
- No word was added, removed or re-levelled. 1.0.0's content is exactly the released content.

[1.0.0]: https://github.com/X-Trivle/LexiCore/releases/tag/v1.0.0
