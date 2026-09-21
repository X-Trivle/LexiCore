# The ~700 additional words

The deck is **LexiCore-5000 plus roughly 700 more words** (≈5,700 total, A1–C1). This page records
what can be verified about those additions today, and the exact format needed to publish them
alongside the list.

## Verified so far (from the 50-word sample)

| observation | value |
|---|---|
| sample notes that are *not* LexiCore headwords | 6 of 50 (12%) |
| which ones | `asleep`, `deposited`, `employer`, `frighten`, `reduce`, `stakeholders` |
| of those, in Oxford-5000 but not in LexiCore | 4: `asleep`, `employer`, `frighten`, `reduce` |
| highest deck `order` seen in the sample | 5,569 (> 5,000, consistent with ≈5,700 items) |

Read against [`data/oxford_comparison_sets.csv`](../../data/oxford_comparison_sets.csv), the
pattern is coherent and useful: the additions are **everyday words that a frequency + validity-gate
pipeline drops** — contracted forms (`cannot`), high-frequency learner nouns
(`menu`, `goodbye`, `sweater`, `thirsty`, `waiter`), role words with a gendered second element
(`policeman`, `businessman`), and derived agent nouns (`employer`)
— see [KI-15](../../docs/KNOWN_ISSUES.md#ki-15-words-absent-by-design-that-teachers-may-expect).

**Not yet published anywhere:** the actual list of ~700 words, the rule that selected them, or
their levels. Until they exist as a file, "built on LexiCore + 700 words" is a design statement
we can only confirm partially (12% of the sample is outside the list).

## Publishing format

Add the file as `data/ecosystem/lexideck/additions_700.csv` (or ship it with the deck and link it)
using exactly this schema — the same column names as the release CSV, so the two files concatenate:

```csv
rank_global,rank_in_level,word,pos,cefr_level,cefr_source,confidence,n_sources,total_count,recent_share_2022plus,newest_share_2025_2026,wordfreq_zipf_2021_baseline
```

Rules a reviewer will check:

1. `word` must be a single lower-case token and **disjoint** from `LexiCore_5000.csv`;
2. `cefr_level` ∈ {A1,A2,B1,B2,C1} (add C2 only with a documented band change);
3. `cefr_source` must name a real provenance (`cefrj-v1.5`, `octanove-c1c2-v1.0`, a model id, or
   `manual` + a one-line rationale); never copy a level from Oxford without saying so;
4. `total_count` / `n_sources` are required so additions can be plotted on the same frequency
   scale as the list (or left empty **only** if `wordfreq_zipf_2021_baseline` is filled);
5. leave `recent_share_2022plus` and `newest_share_2025_2026` empty until
   [KI-2](../../docs/KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed) is fixed — an
   estimate here would be worse than a gap;
6. add `additions_source.csv.gz`-style provenance if the words come from an external list, and
   record its licence in [`NOTICE.md`](../../NOTICE.md).

A template with the two verifiable sample rows is in
[`additions_700.template.csv`](additions_700.template.csv) — rows are **placeholders illustrating
the format**, not a proposed list.

## Why this file matters more than the deck

Once the ~700 words exist as data, three things become possible that are impossible today:
measuring whether the additions improve coverage of A1/A2 (where LexiCore's pool is thin,
[KI-6](../../docs/KNOWN_ISSUES.md#ki-6-c1-is-a-catch-all-band)); checking whether they should be
**folded back** into the list as `LexiCore-5700`; and comparing the combined list against
Oxford/PIL/NAT-MEZ instead of against Oxford alone.
