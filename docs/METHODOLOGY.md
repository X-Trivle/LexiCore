# Methodology

Release 1.0.0 · built 2026-09-14 12:59–17:50 UTC · described from the release manifest and
the unmodified stage logs in [`reports/upstream/`](../reports/upstream).

Where this document states a number, that number is present in a file in this repository; the
two places it is *not* (the recency axes) are flagged and covered by
[KNOWN_ISSUES.md](KNOWN_ISSUES.md).

## 1. Goal

Produce a 5,000-word English core list, split into five equal 1,000-word CEFR bands, that:

1. is **counted**, not curated — evidence of use in five independent corpora types (web,
   educational web, encyclopaedic, subtitles/spoken, recent crawl);
2. prefers words that are **widely dispersed** over words that are merely frequent in one niche;
3. prefers words that are **useful** to learners (coverage of the NGSL/NAWL/BSL teaching lists);
4. carries a **CEFR level** traceable to a published profile wherever possible;
5. prefers **current** usage over historical usage.

Goals 1–4 are met and verifiable here. Goal 5 is **not** met in 1.0.0: the recency features
never reached the feature table ([KI-2](KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed)).

## 2. Pipeline

Ten stages, run by a single driver with resumable per-stage `done/*.flag` markers. Timings are
the ones printed by the runner (`make check` does not re-run this; see
[REPRODUCING.md](REPRODUCING.md)).

| # | Stage | What it does | Wall time | Output |
|---|---|---|---:|---|
| 1 | `env` | measure CPU/RAM/disk, probe accelerators, freeze package versions | 36 s | `env.json` |
| 2 | `fineweb` | stream 15 parquet shards of `HuggingFaceFW/fineweb` `sample/10BT`; language filter; count `freq`, `df`, per-shard counts, held-out sample | 4,569 s | `src_fineweb.pkl` |
| 3 | `fwedu` | same over 4 shards of `fineweb-edu-score-2` (CC-MAIN-2025-26) | 638 s | `src_fwedu.pkl` |
| 4 | `wiki` | same over the 41 shards of `wikimedia/wikipedia` 20231101.en | 1,280 s | `src_wiki.pkl` |
| 5 | `subs` | stream `OPUS-OpenSubtitles/v2024/mono/en.txt.gz`, capped at target | 1,175 s | `src_subs.pkl` |
| 6 | `cc2026` | 128 WET files from `CC-MAIN-2026-34`, per-file doc accept/reject log | 1,673 s | `src_cc2026.pkl` |
| 7 | `setup` | NLTK data for the validity gates (WordNet, `words`, `words_alpha`, CMUdict) | 2 s | – |
| 8 | `merge` | union 1,034,148 surface types → lemmatise → pool 215,416 candidate lemmas → build feature table | 805 s | `features.pkl`, `surface_to_lemma.pkl` |
| 9 | `label` | CEFR-J + Octanove direct profiles (7,662 candidates); multinomial logistic model for the rest; 5-fold CV against the direct labels | 29 s | `labels.pkl`, `cefr_label_report.json` |
| 10 | `select` | validity gates → eligibility (119,155) → weighted score → quota fill 1,000/level | 15 s | `selected.pkl`, `select_report.json` |
| 11 | `finalize` | contract checks, artefact writing, Oxford comparison, reports | 33 s | `deliverables/` |

Compute inside the run was parallel: `P = 128` shards per source (`psh` files-per-shard was
tuned per source: 3 for `wiki`, 32 for `fwedu`), on a 24-core / 50.5 GB host.

**Accounting note:** 2 h 51 m of stage time inside 4 h 51 m of wall time — the remainder was
checkpoint backup/restore traffic, including one failed restore (`runner.log` line 2) and four
restart cycles.

## 3. Counting and normalisation

* Token counts are **post-filter word counts**, not raw corpus sizes: each source keeps a
  surface vocabulary of 148 k–491 k types, and the reported `tokens` is essentially the sum over
  that vocabulary (e.g. `subs`: 1,099,782,261 counted of 1,103,261,872 claimed).
* Surface forms are mapped to lemmas before pooling: `merge` added 4,506,797 inflected-form
  records and resolved 283,502 of 1,034,148 surface types via a lemma step
  (`data/derived/surface_to_lemma.csv.gz` is that map).
* Per-document language filtering is logged for `cc2026` (e.g. 20,729 docs seen → 11,961
  English kept, 8,768 rejected) and for the HF sources by shard.
* A **held-out** 1/1000 document sample was counted separately (`held` per source; 13,674,353
  word occurrences in total) and is what the coverage figure in [VALIDATION.md](VALIDATION.md) uses.

## 4. Features (215,416 candidates × 22 fields)

| field | meaning |
|---|---|
| `ppm[source]` | occurrences per million words of that corpus |
| `dp[source]` | document prevalence in that corpus |
| `dfr[source]` | fraction of documents containing the word |
| `range[source]` | presence span across the corpus's shards |
| `agg_lppm` | pooled log-parts-per-million |
| `disp` | pooled dispersion score |
| `src_entropy` | balance across the five sources (1.0 = perfectly balanced) |
| `total_f` | pooled occurrences |
| `held_count` | occurrences in the held-out sample |
| `recent_share`, `newest_share` | *empty in 1.0.0* |
| `in_cefrj`, `in_oct` | level from CEFR-J v1.5 / Octanove C1–C2 profile |
| `ngsl_band`, `ngsl_rank`, `ngsl_spoken`, `nawl`, `bsl`, `bnc_band` | teaching-list anchors |
| `wf_zipf2021` | `wordfreq` 2021 Zipf baseline (external sanity check) |

`data/derived/candidate_features.csv.gz` is this table verbatim.

## 5. CEFR labelling

1. **Direct profiles first.** A lemma present in CEFR-J v1.5 (or the Octanove C1/C2 profile)
   takes that level, with a fixed confidence cap (0.97 / 0.95). This covers 7,662 of the
   215,416 candidates and 4,563 of the 5,000 selected words (91.3%).
2. **Model for the rest.** A multinomial logistic regression (`sklearn`,
   `cefr_source = model:multinomial-logit-v1`) trained on the direct-labelled candidates using
   the frequency/dispersion/anchor features. Cross-validated performance against the direct
   labels: **accuracy 0.3814, macro-F1 0.3829** (majority class would be ≈0.32), see the
   confusion matrix in [`reports/upstream/cefr_label_report.json`](../reports/upstream/cefr_label_report.json).
   It supplied the level for 437 selected words.
3. **No C2 band.** The release uses A1–C1 only; Octanove C2 words collapse into C1.

## 6. Gates, scoring, selection

```
215,416 candidates
   │  validity gates (WordNet / NLTK words / words_alpha / CMUdict) and minimum evidence
   ▼
119,155 eligible  (55.3%)
   │  score = Σ wᵢ · zᵢ
   ▼
1,000 per level, chosen as the top-scoring eligible words in that band
```

| weight | feature | value | note |
|---|---|---:|---|
| `freq` | `agg_lppm` | 0.34 | |
| `disp` | `disp` | 0.18 | |
| `util` | NGSL/NAWL/BSL utility | 0.18 | |
| `ent` | `src_entropy` | 0.10 | |
| `rng` | `range` | 0.08 | |
| `df` | `dfr` | 0.06 | |
| `rec` | `recent_share` | 0.06 | **inert in 1.0.0** (all-null input) |

Eligible pool by level: A1 2,234 · A2 1,912 · B1 3,238 · B2 13,808 · C1 97,963 — A1/A2/B1 are
*nearly exhausted* by the quota (the top ~45%/52%/31% of their pool), which is why the level
bands are not equally selective. See [KI-6](KNOWN_ISSUES.md#ki-6-c1-is-a-catch-all-band).

## 7. Comparison against Oxford 5000

Computed *outside* the construction path: Oxford never influenced which words were chosen.
On 4,928 single-word Oxford entries: 3,526 shared, Jaccard 0.5508, exact level agreement 0.466,
within-one-band 0.8659, quadratic weighted κ 0.7124. Full crosstab in
`data/MANIFEST.json → oxford_comparison`, word sets in `data/oxford_comparison_sets.csv`.

## 8. What the method does *not* do

* no human review of individual items;
* no lemma-sense splitting (a word carries one level even when its senses span bands);
* no frequency-normalised comparison between corpora of very different document granularity
  (see [KI-7](KNOWN_ISSUES.md#ki-7-dispersion-is-not-on-one-scale));
* no recency signal in 1.0.0 (see [KI-2](KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed)).
