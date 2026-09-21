# Provenance

Every corpus and every anchor list that the release consumed, with the recorded file list, and
what we independently re-checked on 2026-09-21.

Source of truth: `data/MANIFEST.json` (`sources`, `anchors_provenance`, `artifacts`).

## 1. Corpora

| id | what | window | licence | words counted | docs | real files | bytes |
|---|---|---|---|---:|---:|---:|---:|
| `fineweb` | `HuggingFaceFW/fineweb` → `sample/10BT` | 2013–2024 web | ODC-By 1.0 | 7,545,397,544 | 14,853,888 | **15** | 30.64 GB |
| `fwedu` | `HuggingFaceFW/fineweb-edu-score-2` → `data/CC-MAIN-2025-26` | educational web | ODC-By 1.0 | 1,509,381,045 | 2,020,431 | 4 | 5.83 GB |
| `wiki` | `wikimedia/wikipedia` → `20231101.en` | encyclopaedic | CC BY-SA 3.0 / GFDL | 2,172,583,977 | 5,428,305 | 41 | 11.63 GB |
| `subs` | `OPUS-OpenSubtitles/v2024/mono/en.txt.gz` | spoken (film/TV) | OPUS/OpenSubtitles attribution | 1,103,261,872 | 198,800,294 lines | 1 stream | 9.51 GB¹ |
| `cc2026` | `data.commoncrawl.org/crawl-data/CC-MAIN-2026-34/…wet.gz` | recent web | Common Crawl Terms of Use | 1,301,987,532 | 1,549,435 | 128 | 8.21 GB |
| | | | **total** | **13,632,611,970** | 219,656,353 | 192 | ~65.8 GB |

¹ size read from the live server, not recorded by the release — the only source without a
recorded byte count or hash ([KI-9](KNOWN_ISSUES.md#ki-9-the-subs-source-has-no-integrity-record)).

`MANIFEST.json → sources[*].files` carries a `url` + `bytes` + `sha256` record for each downloaded
file, plus one `chunk` record per compute shard (with its own `words` / `docs_en`). Summing the
chunk records reproduces the per-source word totals exactly.

> ⚠️ The upstream `REPORT.md` prints `Files: 115 / 18 / 110 / 1 / 128`; those are
> *file + chunk* record counts (fineweb = 15 real files + 100 chunks). Use the table above.

## 2. Independent re-verification (2026-09-21)

| check | method | result |
|---|---|---|
| shard exists & size as recorded | `curl -sIL …/sample/10BT/000_00000.parquet` | `content-length: 2,147,292,183` = manifest ✔ |
| `sample/10BT` really has 15 shards, all used | `GET /api/datasets/HuggingFaceFW/fineweb/tree/main/sample/10BT` | 15 files, 30.6 GB ✔ |
| recorded hash is the real file hash | compare manifest `sha256` vs HF git-LFS `oid` | `6b552ea48424648d…` identical ✔ |
| wikipedia shard size | `HEAD …/20231101.en/train-00000-of-00041.parquet` | 420,296,449 = manifest ✔ |
| commoncrawl WET file | `HEAD …CC-MAIN-20260807101845-…-00719.warc.wet.gz` | 62,456,581 = manifest ✔ |
| OpenSubtitles stream | `HEAD …/v2024/mono/en.txt.gz` | 9,508,584,209 bytes (consistent with 1.1 B words, "capped at target") ✔ |
| counts agree with the candidate table | Σ `total_f` over 215,416 candidates = 13,327,211,431 | 97.75% of the 13,632,611,970 claimed ✔ |
| per-word counts self-consistent | `the`: Σ over sources of `ppm × tokens` | 691,175,993 = `total_count` ✔ |
| release artefacts unmodified | SHA-256 of the 4 files vs `MANIFEST.artifacts` | all 4 match ✔ (`make checksums`) |

Not reproduced here: the corpora themselves (≈66 GB) and the original run.
Not verifiable from the checkpoint: the `subs` stream (no hash) and the *year* attribution used
for recency ([KI-2](KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed)).

## 3. Anchors and gates

These files drove labelling and validity. They are **not redistributed** in this repository; the
provenance records below are the release's own, including the exact files it used.

| anchor | file / id | licence | role |
|---|---|---|---|
| CEFR-J v1.5 (Tono, TUFS) | `olp-en-cefrj/cefrj-vocabulary-profile-1.5.csv` · [cefr-j.org/download.html](http://www.cefr-j.org/download.html) · sha256 `b0dd3c63…` | free for research & commercial use with citation | 3,898 levels (78%) |
| Octanove C1/C2 v1.0 | `olp-en-cefrj/octanove-vocabulary-profile-c1c2-1.0.csv` · [github.com/openlanguageprofiles/olp-en-cefrj](https://github.com/openlanguageprofiles/olp-en-cefrj) · sha256 `18c33a40…` | CC BY-SA 4.0 | 665 levels |
| NGSL 1.01 (+ bands, SFI, Spoken) | `ngsl/NGSL-101-by-band-qq9o.xlsx`, `ngsl/NGSL-101-with-SFI.xlsx`, `ngsl/NGSL-Spoken-101.xlsx` · [newgeneralservicelist.com](https://www.newgeneralservicelist.com/) | CC BY-SA 4.0 | `util` term, gating |
| NAWL 1.0 | `nawl/NAWL_10_lemmatized_for_research.csv` | CC BY-SA 4.0 | `util` term |
| BSL 1.01 | `misc/bsl.csv` | CC BY-SA 4.0 | `util` term |
| BNC/COCA 25k bands | `misc/bnc_coca_25k.csv` · [wordfrequency.info](https://www.wordfrequency.info/) (mirror `antdurrant/word.lists`) | free use with attribution | `bnc_band` |
| wordfreq v3.x | `en` top-200k, Zipf 2021 · [github.com/rspeer/wordfreq](https://github.com/rspeer/wordfreq) | Apache-2.0 code / CC BY-SA 4.0 data | external baseline column |
| validity gates | Princeton WordNet 3.x (NLTK), NLTK `words`, `dwyl/english-words` (MIT, sha256 `3ed0c946…`), CMUdict 0.7b (BSD-like, sha256 `b6b3efc0…`) | per project | `all_valid_words` |
| Oxford 5000 | `anchors/oxford-5k.csv` (mirror `nalgeon/words`) | reference only | comparison, **never** used in construction |

See [NOTICE.md](../NOTICE.md) for the CC BY-SA interaction with this repository's CC BY 4.0 grant.
