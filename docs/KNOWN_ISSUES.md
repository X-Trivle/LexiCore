# Known issues

Everything here was measured on the files in this repository, not inherited from the upstream
report. Each item shows the evidence, the practical consequence, and what a fix looks like.
The CI "expected" checks in `src/lexicore/validate.py` pin items KI-2, KI-3, KI-5 and KI-14 so
that a future fix is visible as an intentional change.

---

## KI-1 A ranked list that is not ranked

`reports/upstream/REPORT.md` has a section *"Notable modern additions (LexiCore, ranked by
2025-26 evidence)"*. The list reads
`abandoned, abdominal, aboard, abound, abruptly, absorption, abstraction, …` — which is exactly
alphabetical (`lst == sorted(lst)` → `True`), and `newest_share_2025_2026` is empty for every
word in it (and for all 2,876 rows of `oxford_comparison_sets.csv`).

**Consequence:** the sentence is a formatting artifact, not a measurement. Do not quote it as
evidence of modernity.
**Fix:** compute the field (KI-2) and re-render the section, or delete the "ranked by" wording.

## KI-2 The recency axis was never computed

| measured | value |
|---|---|
| `recent_share_2022plus` / `newest_share_2025_2026` filled in `data/LexiCore_5000.csv` | **0 / 5,000** |
| `recent_share` / `newest_share` non-null in `data/derived/candidate_features.csv.gz` | **0 / 215,416** |
| recency weight in the published score | **0.06** (inert) |
| `stats.mean_recent_share`, `stats.mean_newest_2025_26_share` | `NaN` |
| log evidence | `numpy … RuntimeWarning: Mean of empty slice` and `invalid value encountered in scalar divide` in `reports/upstream/finalize.stage.log` |

Deeper cause: each source's `year_freq` holds **one bucket only** — `fineweb: 2022-2024`,
`wiki: 2022-2024`, `fwedu: 2025-2026`, `cc2026: 2025-2026`, `subs: none`. So even with the
plumbing fixed, "recency share" would be a per-source proxy, and `fineweb`'s label is
inconsistent with its own description (2013–2024 corpus tagged 2022–2024).

**Consequence:** this release must not be marketed as recency-aware. The claim "modern additions"
has no measured support in 1.0.0.
**Fix:** extract real WARC `W-Date` / CC snapshot years per source, re-run `merge`+`select`, and
publish the year distribution per word. Until then, `wordfreq_zipf_2021_baseline` is the only
time-referenced signal in the file.

## KI-3 POS is a dictionary guess

`pos` values: noun 3,598 · adjective 545 · verb 526 · adverb 241 · other 90. Function words are
mislabeled in plain sight: `at → noun`, `be → noun`, `a → noun`, `or → noun`, `of → other`,
`by → adverb`. The field therefore cannot come from tagging the corpora.

**Consequence:** do not use `pos` in teaching material or in any "word class" analysis.
**Fix:** re-tag with a real parser (UDPipe / Stanza / spaCy) *on corpus samples*, take the modal
tag per sense, and emit `pos_senses` as a list rather than one label.

## KI-4 437 words are levelled by a weak model

`cefr_label_cv`: accuracy **0.3814**, macro-F1 **0.3829** over 5 classes; the majority class alone
would score ≈ 2,453 / 7,662 = **0.32**. The confusion matrix shows the failure is structural:
true B2 is scattered (145/184/438/799/887), and 189,058 of 215,416 candidates get predicted C1.
437 of the 5,000 selected words (8.7%) carry a model-derived level.

**Consequence:** those 437 levels are weak evidence, not profiles. `VALIDATION_REPORT.json`
reports `problems: []` because it only checks shape, not label validity.
**Fix:** restrict model labelling to words where a graded-wordlist interpolation is possible,
otherwise publish the word with `cefr_level = ""` and `cefr_source = "unlabeled"`; or replace the
linear model with a contextual/embedding-based difficulty estimator and report its CV numbers next
to every affected row.

## KI-5 Confidence is a cap, not a calibrated probability

411 distinct `confidence` values, but 3,898 rows are exactly `0.97` and 665 exactly `0.95`; only
the 437 model rows are real posteriors (min 0.231). The published "mean CEFR confidence 0.9205"
is thus dominated by two constants.

**Consequence:** the number is not a probability and must not be compared across lists.
**Fix:** either propagate the CEFR-J profile's own per-word evidence, or output calibrated
posteriors (Platt/isotonic on the CV folds) for *all* rows, and drop the caps.

## KI-6 C1 is a catch-all band

Eligible pool by level: A1 2,234 · A2 1,912 · B1 3,238 · B2 13,808 · **C1 97,963**. Selecting
1,000 from 97,963 is a different exercise from selecting 1,000 from 2,234 (A1 consumes 45% of
its pool). The rarest C1 words have 3,299–8,755 occurrences over 13.6 B words (`paywall`,
`paternalistic`, `splatter`, `linearly`) and the 2021 Zipf baseline goes down to 2.35.

**Consequence:** the "C1" band is not comparable to A1–B2 bands, nor to Oxford's C1.
**Fix:** publish an explicit rarity/utility interval per band, or split C1 into C1/C2 and set a
minimum-evidence floor per band (e.g. `total_count ≥ 20,000`).

## KI-7 Dispersion is not on one scale

`dfr` is "fraction of documents containing the word", but a `subs` "document" is a subtitle
*line*: `subs` has 198,800,294 docs for 1,103,261,872 words (5.5 words/doc), versus ~508
words/doc for `fineweb`. Measured directly: `the` has `dfr = 0.150` in `subs` and `0.980` in
`fineweb`. Since `disp` (0.18) + `ent` (0.10) + `df` (0.06) = 34% of the score are built on these,
the mix of granularities leaks into the ranking.

**Consequence:** cross-source dispersion favours sources with coarse documents; `n_sources ≥ 3`
is a weaker ubiquity test than it looks.
**Fix:** re-segment `subs` into fixed-size pseudo-documents (e.g. 30 consecutive lines /
per-title windows) and recompute.

## KI-8 "Files" counts include compute chunks

`REPORT.md` prints `files: 115 / 18 / 110 / 1 / 128`; the records are 15 + 100, 4 + 14, 41 + 69,
1, and 128 (downloaded files + per-shard bookkeeping rows).

**Consequence:** corpus-scale claims look inflated by the file column.
**Fix:** report `source_files` and `chunks` separately, as [PROVENANCE.md](PROVENANCE.md) does.

## KI-9 The subs source has no integrity record

`sources.subs.files[0]` is `{"kind": "source_stream", "url": …, "words": …, "note": "capped at target"}`
— no `bytes`, no `sha256`. We fetched the live `Content-Length` (9,508,584,209) as a substitute.
`target_words` is recorded for the other sources; for `subs` the cap is stated only in prose.
Related: `fineweb`'s recorded `target_words` is 7,300,000,000 while `tokens` is 7,545,397,544
(**above** the stated cap), so the cap was not the binding constraint for all sources.

**Fix:** stream-hash the file (`sha256` of the exact gzip) and record the cap that was applied.

## KI-10 Counted words are filtered words

Per-source `freq` tables hold 148 k–491 k surface types whose sum is within 0.3–2% of the
reported token total — i.e. the reported "words" are the words that survived the
type/validity filter, not the corpus's token count. For a raw web crawl, a ~98% first-pass
acceptance rate is not plausible; the denominator and the vocabulary were produced by the same
filter.

**Consequence:** "13.6 billion words analysed" is accurate as *counted words*, but it is not the
size of the corpora, and near-perfect vocabulary coverage is a property of the pipeline, not of
English.
**Fix:** publish both numbers: `tokens_raw` (all whitespace tokens) and `tokens_counted`.

## KI-11 Held-out coverage is token coverage

0.7251 overall means "72.5% of occurrences in a 1/1000 document sample are among the 5,000
words". Verified: `Σ held_count` over all 215,416 candidates = 13,674,353, matching the reported
denominators (13,685,028).

**Consequence:** expected for any large frequency list; it validates breadth, not the levels.
**Fix:** add the type-level, frequency-matched comparison described in
[VALIDATION.md](VALIDATION.md#4-held-out-coverage--what-it-does-and-does-not-show).

## KI-12 The pipeline code is not in the release

The checkpoint contains outputs and logs only. Extension census of the archive:
`pkl×9, log×12, json×7, flag×11, csv×2, md×1, txt×1` — zero `.py`/`.sh`/`.ipynb`. The only traces
of code are `/content/lexicore/pipeline/run.py:18` (with `dev=xm.xla_device(); tpu_cores=8`) and
six `sklearn/linear_model/_logistic.py` warnings in `label.stage.log`. The anchor files
(`anchors/oxford-5k.csv`, CEFR-J CSV, NGSL XLSX, …) are also absent, so labels cannot be
re-derived from this repository alone.

**Consequence:** this is an auditable artefact set, not a reproducible build.
**Fix:** see [REPRODUCING.md](REPRODUCING.md) for the exact list of files to request and what the
`data/derived/` tables already let you re-do in the meantime.

## KI-13 Vocabulary noise survives into the candidate pool

`data/derived/candidate_features.csv.gz` and the source tables contain web artifacts and
non-English/typo forms (`nbsp`, `div`, `var`, `https`, `www`, `href`, `utf`, `phychology`,
`numericals`, `parece`, `bambaataa`). The validity gates keep them out of the final 5,000, but
they inflate the 215,416 pool, its totals, and the dispersion denominators.

**Fix:** publish `rejected_by_gate` counts per category (spell-error, non-en, code, markup) so
the funnel is interpretable.

## KI-14 Ranks inside a level are not frequency ranks

Spearman between `total_count` and `rank_in_level`: **0.42 (A1), 0.38 (B1), 0.61 (C1)**. The top
A1 word is `at`, not `the`, because the blended score rewards dispersion/utility balance.

**Consequence:** `rank_in_level` is an "overall usefulness" ordering; label it as such in
downstream UIs, or emit `rank_frequency` alongside it (trivial: sort by `total_count`).
**Fix in this repo:** `python -m lexicore words --level A1 --sort freq` gives the frequency order.

## KI-15 Words absent by design that teachers may expect

Oxford includes, and LexiCore excludes, items such as `cannot`, `email`, `blog`, `goodbye`,
`menu`, `thirsty`, `waiter`, `sweater`, `policeman` (all in `oxford_only`). The gate is lemma- and
evidence-based, so contracted forms and low-dispersion everyday nouns drop out.

**Consequence:** for a pedagogical syllabus, review the `oxford_only` set before adopting the
list. This is precisely why companion products add words on top — see
[`ecosystem/`](../ecosystem/lexideck-multilingual/ADDITIONS.md).
