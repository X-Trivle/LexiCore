# Data dictionary

Three layers of files: the **release** (what you should use), the **derived** views (what you
need to change it), and the **upstream reports** (what it was built from).

---

## `data/LexiCore_5000.csv` — canonical release

Delimited by `,`, CRLF line endings, UTF-8, one header row, 5,000 data rows.
Empty string = value absent (never `NA`/`null`).

| column | type | definition | caveats |
|---|---|---|---|
| `rank_global` | int 1–5000 | position in the whole list, by selection score | **not** a frequency rank; A1's rank 1 is `at`, ahead of `the` |
| `rank_in_level` | int 1–1000 | same score, within the CEFR band | Spearman vs `total_count`: A1 0.42, B1 0.38, C1 0.61 |
| `word` | str | lower-case, single-token headword (lemma) | no multiword units, no `cannot`/`email`-style exclusions by design |
| `pos` | enum: `noun, adjective, verb, adverb, other` | dictionary-lookup guess | **unreliable**, see [KI-3](KNOWN_ISSUES.md#ki-3-pos-is-a-dictionary-guess) — counts: noun 3,598 · adjective 545 · verb 526 · adverb 241 · other 90 |
| `cefr_level` | enum A1–C1 | difficulty band | exactly 1,000 each; no C2 band |
| `cefr_source` | enum `cefrj-v1.5`, `octanove-c1c2-v1.0`, `model:multinomial-logit-v1` | who decided the level | 3,898 / 665 / 437 |
| `confidence` | float 0.231–0.97 | label confidence | 0.97 and 0.95 are *caps* for profile labels, only model rows are posteriors — [KI-5](KNOWN_ISSUES.md#ki-5-confidence-is-a-cap-not-a-calibrated-probability) |
| `n_sources` | int 3–5 | how many of the five corpora contain the word | 5 → 4,953 · 4 → 46 · 3 → 1 |
| `total_count` | int | pooled lemma occurrences over 13,632,611,970 words | min 3,299 · median 292,252 · max 691,175,993 (`the`) |
| `recent_share_2022plus` | float \| empty | share of occurrences from 2022+ | **empty in all 5,000 rows** — [KI-2](KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed) |
| `newest_share_2025_2026` | float \| empty | share from the newest window | **empty in all 5,000 rows** |
| `wordfreq_zipf_2021_baseline` | float | external Zipf (2021) for the same lemma | 2.35–7.73, mean 4.333; use for cross-list comparisons |

Derived quantity provided by the loader: `Entry.per_million = 1e6 · total_count / 13,632,611,970`.

## `data/LexiCore_5000.json`

```
{ name, version, generated, n, cefr_levels, level_quota,
  entries: [ { word, pos, cefr, cefr_source, confidence, rank_in_level, n_sources, ppm: {…} } ] }
```

Same words and levels, plus `ppm` per source (fineweb / fwedu / wiki / subs / cc2026). No
`total_count` here — use `Σ ppmᵢ · tokensᵢ / 1e6` if you need it, or read the CSV.

## `data/LexiCore_5000.txt`

5,000 lines, word only, in `rank_global` order. For drop-into-everything use.
`data/lists/{A1..C1}.txt` are the same words per level, and `*.alphabetical.txt` is sorted.

## `data/oxford_comparison_sets.csv`

2,876 rows: `word, set (lexicore_only|oxford_only), lexicore_level, oxford_level, newest_share, recent_share`.
The last two columns are empty in every row (same root cause as KI-2).

## `data/MANIFEST.json` (release manifest, unmodified)

`method`, `environment`, `sources` (per-file URL/bytes/sha256 + chunk records),
`anchors_provenance`, `cefr_label_cv`, `validation`, `stats`, `oxford_comparison`, `artifacts`.
Note the key spelling `stats.mean_recent_share: NaN` — JSON writers that reject `NaN`
(`json.loads` accepts it, strict parsers do not) may choke; `scripts/` in this repo reads it
with `json.loads` defaults.

## `data/derived/` — the candidate pool (regenerate with `make derived`)

| file | rows | columns |
|---|---:|---|
| `candidate_features.csv.gz` | 215,416 | `word, n_sources, agg_lppm, disp, src_entropy, total_f, held_count, wf_zipf2021, ngsl_band, ngsl_rank, recent_share, newest_share, in_cefrj, in_oct, ngsl_spoken, nawl, bsl, bnc_band` + `ppm_*`, `dfr_*`, `dp_*`, `range_*` for each of the 5 sources |
| `candidate_labels.csv.gz` | 215,416 | `lemma, level, label_source, confidence, A1..C1` (class probabilities) |
| `surface_to_lemma.csv.gz` | 283,502 | `surface, lemma` |
| `derived_manifest.json` | – | row counts, bytes, sha256 (machine-readable) |

Booleans are written as `1`/`0`, empties as `""`. This is the **whole** scored pool, so you can
study rejected words (`215,416 − 119,155` ineligible, `119,155 − 5,000` eligible-but-not-selected).

## `reports/upstream/`

`REPORT.md` and `VALIDATION_REPORT.json` as shipped, plus every `*.stage.log`, `runner.log`,
`env.json`, `merge_summary.json`, `select_report.json`, `cefr_label_report.json` and the
`done/*.flag` markers. They are kept byte-identical so that any claim in the docs can be traced;
`REPORT.md` contains one claim we could not reproduce — see [KI-1](KNOWN_ISSUES.md#ki-1-a-ranked-list-that-is-not-ranked).
