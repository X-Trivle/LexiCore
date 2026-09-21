# Deck structure, measured

Everything on this page was read out of the **free 50-word sample** (`application.apkg`,
5,877,461 bytes, fetched 2026-09-21), not from marketing copy. Where a claim about the full deck
(5,700 words, 28,000 sentences, 38 hours of audio) cannot be seen in a 50-word sample, it is
marked *stated, not measured*.

## How to reproduce these numbers

```bash
curl -LO "https://assets-2-prod.whop.com/public/uploads/2026-09-20/305d9e95-7a9d-44b1-8471-76eb2b4f8748/application.apkg"
mkdir -p sample && cd sample && unzip -q ../application.apkg
python3 - <<'PY'
import sqlite3, json
c = sqlite3.connect("collection.anki2").cursor()
print(c.execute("select count(*) from notes").fetchone()[0], "notes")
m = list(json.loads(c.execute("select models from col").fetchone()[0]).values())[0]
print(m["name"], "-", len(m["flds"]), "fields")
print([f["name"] for f in m["flds"]])
print(len(json.load(open("media"))), "media files")
PY
```

## Container

| | |
|---|---|
| notes / cards | 50 / 50 (one card per word) |
| note type | `LexiCore Multilingual 12` |
| fields | 85 |
| card templates | 1 (`Card 1`) |
| media | 350 files = **7 per note**: 1 `webp` illustration + 1 `mp3` headword audio + 5 `opus` sentence audio |
| tags | `LexiCore`, `level-B1`, `cefr-B1`, `pos-noun`, `order-02148`, … |

## Field map (85)

| group | fields | count | populated in sample |
|---|---|---:|---|
| headword | `Word` (text + inline `<audio>`), `Image` (webp) | 2 | 50/50 |
| examples | `Ex1`…`Ex5` (each with `<audio>` and a `<span class="lx-hl">` highlight on the headword) | 5 | 50/50 |
| word translations | `tr_ar de es fr hi id ja ko pt ru ur zh` | 12 | 50/50 |
| example translations | `ex1t_*` … `ex5t_*` × 12 languages | 60 | 50/50 |
| metadata | `Level`, `cefr`, `pos`, `order`, `def`, `IPA` | 6 | 50/50 |

Measured invariants: `Level == cefr` in all 50 notes; every note has all 5 examples, all 12 word
translations and all 60 example translations; every note has an `<img>` and a non-empty `IPA` and
`def`. In the sample, `pos` carries multiple comma-separated tags (e.g. `adj,noun`,
`noun,prep,verb`) — 33/50 contain `noun`, 15/50 contain `adj`.

## Rotation engine

The card template embeds a script block the source calls
*"LexiCore — example rotation engine (v18)"*: **one example at a time**, with a per-word counter
held in `localStorage`, and two selectable modes in the card's settings gear —

* `rate` (default): the position advances when the card is **rated**, not when it is revealed,
  previewed or browsed;
* `each`: the position advances on every appearance, for clients that do not report the rating.

That matches the "5 examples, rotating during review" claim in the visible mechanism; the number
of distinct examples per word (5) is verified above. 2 script blocks, ~27.5 KB of template
JavaScript, no `Math.random` — the rotation is stateful, not random.

## Coverage of the sample against this list

| measure | value |
|---|---|
| sample notes matching a LexiCore headword | **44 / 50** |
| not in LexiCore | `asleep`, `deposited`, `employer`, `frighten`, `reduce`, `stakeholders` |
| of those, in Oxford's set but not LexiCore | `asleep`, `employer`, `frighten`, `reduce` (4) |
| `order` range in sample | 31 … 5,569 |
| notes whose `order` equals LexiCore `rank_global` | 1 / 44 |

`order` is therefore the **deck's** sequence over ~5,700 items (it exceeds 5,000), not the
dataset's rank. Example: `agreement` is `order = 02148` in the deck and `rank_global = 2104` here.

## Stated, not measurable from the sample

* 5,700+ words and 28,000+ sentences across the full deck (a 50-word sample can only confirm
  5 sentences per word, which it does).
* 38+ hours of human-recorded sentence audio and ~1.8 M characters of written content.
* Headword audio, IPA and an illustration "for every word" — true for all 50 sample notes.
