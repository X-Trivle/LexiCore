# LexiDeck Multilingual

**A companion learning product built on LexiCore.** The deck's vocabulary is this list — the
5,000 LexiCore headwords — **plus about 700 additional high-utility words**, for a total of
**5,700+ words spanning A1 to C1**. Its notes are tagged `LexiCore`, `level-*`, `cefr-*`, `pos-*`
and `order-*`, which is how the relationship can be checked rather than asserted
(see [DECK_STRUCTURE.md](DECK_STRUCTURE.md)).

| | |
|---|---|
| Product page | <https://whop.com/lexideck/lexideck-multilingual/> |
| Free 50-word sample (`.apkg`, 5,877,461 bytes) | [application.apkg](https://assets-2-prod.whop.com/public/uploads/2026-09-20/305d9e95-7a9d-44b1-8471-76eb2b4f8748/application.apkg) |
| Sample mirror (release asset, link-stable) | [LexiDeck-Multilingual-free-sample-50-words.apkg](https://github.com/X-Trivle/LexiCore/releases/download/v1.0.0/LexiDeck-Multilingual-free-sample-50-words.apkg) · SHA-256 `8338bafb1118d9fb98facdff3c6761a4675692365cfb1f786acac7a6e388fed1` |
| Vocabulary base | [`data/LexiCore_5000.csv`](../../data/LexiCore_5000.csv) + ~700 additions ([ADDITIONS.md](ADDITIONS.md)) |

This folder documents the deck inside the dataset repository because the deck is the main thing
built on top of the list. It is *about* the product; it is not part of the dataset's data or
tooling (see [`assets/README.md`](assets/README.md)).

## What it is

LexiDeck Multilingual is an Anki-based English vocabulary system designed around context,
repetition, audio, images, pronunciation, and varied examples rather than isolated word
memorization.

It contains more than **5,700 English words from A1 to C1**, with **5 different example sentences
for every word**, giving you more than **28,000 example sentences** in total. The examples rotate
during reviews, so you repeatedly encounter the same vocabulary in different contexts instead of
seeing one sentence every time.

The deck also contains more than **38 hours of human-recorded sentence audio**, plus audio for the
headwords, IPA pronunciation, and a visual illustration for every word. The sentence collection
contains roughly **1.8 million characters of written content**, providing a substantial amount of
contextual English practice.

### Included

- 5,700+ English words, covering A1–C1
- 28,000+ example sentences
- 5 different examples for each word
- Rotating examples during reviews
- 38+ hours of human-recorded sentence audio
- Human-recorded audio for the example sentences
- Headword pronunciation audio
- IPA pronunciation
- An illustration for every word
- Translations in 12 languages
- Anki spaced-repetition system
- Context-based learning rather than isolated vocabulary
- Examples covering different ways words are naturally used

### 12 supported languages

中文 · हिन्दी · Español · العربية · Português · 한국어 · 日本語 · Bahasa Indonesia · Русский · اردو · Français · Deutsch

### About the totals

The amount of written example material is roughly comparable to **several full-length books**,
while the 38+ hours of recorded sentence audio represents dozens of hours of listening practice.
The exact book or video equivalent depends on the average length of the books or videos being
compared, so these figures are best understood as a rough indication of the amount of material
rather than a fixed conversion.

The goal is straightforward: give you enough vocabulary, repeated exposure, context, listening,
pronunciation, and visual information to make Anki reviews more useful than simply memorizing a
list of translations.

## In review

<p align="center">
  <img src="assets/ankidroid-review-01.png" alt="LexiDeck Multilingual review screen in AnkiDroid" width="255"/>
  &nbsp;
  <img src="assets/ankidroid-review-02.png" alt="LexiDeck Multilingual review screen in AnkiDroid, example sentence with audio and translations" width="255"/>
  &nbsp;
  <img src="assets/ankidroid-review-03.png" alt="LexiDeck Multilingual review screen in AnkiDroid, answer side" width="255"/>
</p>

Screenshots of the deck running in AnkiDroid, supplied by the product owner (2026-09-21).
The first two are the same card before and after reveal; the third is another card.

## Relationship to the list, honestly stated

* **Overlap.** In the free sample, 44 of 50 notes correspond to a LexiCore headword; 6 do not
  (`asleep`, `deposited`, `employer`, `frighten`, `reduce`, `stakeholders`) — four of them are
  words that appear in Oxford's list and not in LexiCore
  ([`data/oxford_comparison_sets.csv`](../../data/oxford_comparison_sets.csv)), i.e. the
  additions deliberately recover pedagogically common items that a frequency-plus-gate pipeline
  drops. Details: [ADDITIONS.md](ADDITIONS.md).
* **Ordering.** The deck's `order` field (sample range 31–5,569) is the deck's own sequence over
  ~5,700 words. It is **not** LexiCore's `rank_global`; do not treat one as the other.
* **Levels.** The deck carries the list's CEFR band (`Level` == `cefr` in all 50 sample notes), so
  the same caution applies: 8.7% of LexiCore levels come from a model with CV accuracy 0.38
  ([KI-4](../../docs/KNOWN_ISSUES.md#ki-4-437-words-are-levelled-by-a-weak-model)).
* **POS.** The deck's `pos` field holds multi-value tags (e.g. `adj,noun`) and is richer than the
  list's single guessed tag ([KI-3](../../docs/KNOWN_ISSUES.md#ki-3-pos-is-a-dictionary-guess)).

## Requirements to use it

Anki 23.10+ (the sample ships a v18 card template using modern field/media syntax) and enough disk
for the media package; `.apkg` files are plain ZIP archives, so they are inspectable by design.
