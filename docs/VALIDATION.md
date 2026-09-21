# Validation

Two separate things live here: the checks the **release** ran on itself, and the checks **we**
ran against the files in this repository. They are deliberately kept apart.

## 1. Automated gate in this repo

```bash
make validate      # or: python -m lexicore validate   (--json for machines)
make checksums     # ledger + manifest + derived hashes
make test          # 16 pytest cases
```

`python -m lexicore validate` on the committed data:

```
[PASS ] columns                    expected 12 columns, got 12
[PASS ] row_count                  5000 rows (expected 5000)
[PASS ] unique_headwords           5000 distinct
[PASS ] level_quotas               A1=1000, A2=1000, B1=1000, B2=1000, C1=1000
[PASS ] rank_integrity             contiguous per level and global
[PASS ] value_ranges               counts>0, 0<=confidence<=1, 3<=n_sources<=5
[PASS ] recency_columns_empty      0/5000 rows carry recency values (1.0.0 ships them empty; KI-2)
[PASS ] label_mix                  {'cefrj-v1.5': 3898, 'model:multinomial-logit-v1': 437, 'octanove-c1c2-v1.0': 665}
[PASS ] profile_confidence_constant 411 distinct values; 0.97 x3898 (CEFR-J cap), 0.95 x665 (Octanove cap) — KI-5
[PASS ] pos_is_unreliable          noun=3598/5000 (72.0%) — heuristic POS, KI-3
[PASS ] ubiquity                   4953 words in all 5 sources (99.06%)
[PASS ] ledger                     67 files verified
```

The last four "expected" checks are **drift detectors**: they pass while the release still has
the known gaps. When someone fixes recency or POS, the check flips to `DRIFT` and the docs must
be updated in the same pull request. Hard checks fail CI; drift checks report, CI annotates.

## 2. What the upstream release reported (`reports/upstream/`)

| claim | value | file |
|---|---|---|
| exactly 5,000 unique headwords, one level each | true, `problems: []` | `finalize.stage.log` |
| every headword in a validity dictionary | true | same |
| label mix | 3,898 / 665 / 437 | same |
| mean CEFR confidence | 0.9205 | same |
| present in all 5 / ≥4 sources | 99.06% / 99.98% | same |
| mean 2022+ and 2025-26 share | `NaN` / `NaN` | same — with `RuntimeWarning: Mean of empty slice` in the log |
| held-out coverage (overall) | 0.7251 | same |
| Oxford overlap / Jaccard | 3,526 / 0.5508 | same |
| level agreement exact / ±1 / κ | 0.466 / 0.8659 / 0.7124 | same |
| classifier CV accuracy / macro-F1 | 0.3814 / 0.3829 | `cefr_label_report.json` |

## 3. What we independently re-checked

| check | result |
|---|---|
| SHA-256 of the four release artefacts vs `MANIFEST.artifacts` | **4/4 match** (sizes too) |
| SHA-256 ledger over every file under `data/`, `docs/`, `ecosystem/`, `reports/` | **OK** |
| row count, uniqueness, per-level quota, rank permutations | 5,000 / 5,000 unique / 1,000 each / contiguous |
| `Σ total_count` over the list | 9,705,062,231 = 71.2% of the claimed corpus |
| `Σ total_f` over the 215,416 candidates vs claimed corpus | 13,327,211,431 = **97.75%** ✔ internally consistent |
| recency columns | empty in 5,000/5,000 CSV rows, 0/215,416 candidates, 2,876/2,876 comparison rows |
| source file records | 15 real files for `fineweb` (verified against the live HF tree), sizes and LFS oids match; `wiki` 41; `cc2026` 128 |
| `the`'s arithmetic | `Σ ppm × tokens` = 691,175,993 = released `total_count` ✔ |
| `make derived` reproducibility | rebuilding `data/derived/*.csv.gz` from the checkpoint yields **byte-identical** files |
| pipeline source code | **absent from the checkpoint** — see [REPRODUCING.md](REPRODUCING.md) |

## 4. Held-out coverage — what it does and does not show

`stats.held_out_coverage` compares a 1/1000 document sample per source (13,674,353 word
occurrences in total) against the final list:

| source | held-out words | covered | coverage |
|---|---:|---:|---:|
| fineweb | 7,565,444 | 5,719,128 | 0.756 |
| fwedu | 1,517,451 | 1,121,024 | 0.7388 |
| wiki | 2,283,599 | 1,504,095 | 0.6587 |
| subs | 1,102,508 | 913,927 | 0.829 |
| cc2026 | 1,216,026 | 664,997 | 0.5469 |
| **overall** | **13,685,028** | **9,923,171** | **0.7251** |

Two honest qualifications, because the number is easy to over-read:

1. `covered / held_words` is a **token** coverage: the share of held-out *occurrences* whose word
   is in the list. Any top-5,000 frequency list of English lands near 0.7–0.8, so this confirms
   the list is broad and common — it does **not** validate the CEFR levels or the ranking.
2. The sample is drawn from the same corpora as the counts, and `MANIFEST` labels it
   "independent documents" only in the sense of *not used for counting*.

A genuinely falsifiable version of this test would be: predict held-out **type** coverage of a
held list versus an equal-size random-frequency-matched list, per domain. `data/derived/` makes
that experiment a few lines of code — contributions welcome.
