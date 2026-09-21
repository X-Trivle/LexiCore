# Notice

LexiCore-5000 © 2026 LexiCore maintainers.
The dataset files and the code in this repository are licensed under
**CC BY 4.0** (see [LICENSE](LICENSE)).

This file lists everything in this repository that is **not** ours to license, and what you must
do if you redistribute. It is engineering documentation, not legal advice.

## 1. What CC BY 4.0 covers here

* `data/` — the 5,000-word selection, its ordering, the released comparison sets, and the derived
  tables (`data/derived/`), i.e. the aggregate results of counting public corpora.
* `src/`, `tests/`, `scripts/`, `Makefile`, `pyproject.toml` — the reference code.
* `docs/`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` and the other prose, **except** the
  items in §3.

Required attribution (a reasonable form under CC BY 4.0 §3(a)):

> LexiCore-5000 (v1.0.0), https://github.com/X-Trivle/LexiCore — CC BY 4.0.
> Frequency evidence derived from FineWeb, FineWeb-Edu, Wikipedia (20231101.en),
> OPUS-OpenSubtitles 2024 and Common Crawl CC-MAIN-2026-34.

Indicate if you changed anything, and keep a link to this notice.

## 2. Upstream material — original terms apply

Nothing here transfers rights in the corpora or the anchor lists. If you redistribute the list
together with data from these sources, their terms follow you.

| material | owner / source | licence | used for |
|---|---|---|---|
| FineWeb `sample/10BT` | Hugging Face | ODC-By 1.0 | counting |
| FineWeb-Edu-score-2 | Hugging Face | ODC-By 1.0 | counting |
| Wikipedia 20231101.en | Wikimedia Foundation | CC BY-SA 3.0 / GFDL | counting |
| OPUS-OpenSubtitles v2024 | Tiedemann / OPUS, CSC | OpenSubtitles terms + attribution | counting |
| Common Crawl CC-MAIN-2026-34 | Common Crawl | Common Crawl Terms of Use | counting |
| CEFR-J Wordlist v1.5 | Tono Lab, TUFS ([cefr-j.org](http://www.cefr-j.org/download.html)) | free for research & commercial use **with citation** | 3,898 levels |
| Octanove Vocabulary Profile C1/C2 v1.0 | Open Language Profiles | CC BY-SA 4.0 | 665 levels |
| NGSL / NAWL / BSL 1.0x | Browne, Culligan, Phillips | CC BY-SA 4.0 | utility term, gates |
| BNC/COCA 25k bands | wordfrequency.info | free use with attribution | `bnc_band`, baseline |
| wordfreq v3.x | Rob Speer | Apache-2.0 code / CC BY-SA 4.0 data | 2021 Zipf baseline |
| Oxford 5000 reference | Oxford University Press (mirror: `nalgeon/words`) | **not licensed for redistribution** — comparison only | external comparison |
| Princeton WordNet 3.x, NLTK `words`/`words_alpha`, CMUdict 0.7b | Princeton / NLTK / CMU / dwyl | WordNet licence / public domain / BSD-like / MIT | validity gates |

**CC BY-SA interaction.** Wikipedia, Octanove, NGSL/NAWL/BSL are *share-alike*. Aggregated counts
and independently written documentation are not "adaptations" of those works, which is why the
release's CC BY 4.0 grant is offered over the selection and the code. If you instead publish a
derivative **of an anchor list itself** (e.g. a reformatted NGSL sheet), the BY-SA terms attach to
that derivative. Keep your artefacts separable.

**Not redistributed.** None of the files in the table above is copied into this repository — only
their numeric conclusions, cited by URL and by SHA-256 of the exact file the release read
(`data/MANIFEST.json → anchors_provenance`).

## 3. Excluded from the CC BY 4.0 grant

`ecosystem/lexideck-multilingual/assets/` — screenshots and other material belonging to the
companion product **LexiDeck Multilingual**. They are included for identification and illustration
of that product, and are **not** part of the open dataset release. Ask the product owner before
reusing them elsewhere. Nothing in §1 or §2 of this notice grants rights in that product, its
audio, its illustrations, its translations or its paid content.

## 4. Trademarks and CEFR

"CEFR" is a Council of Europe framework; level labels here are descriptive, not endorsements.
"Oxford 5000" belongs to Oxford University Press and is used only as an external comparison point.

## 5. How the numbers were produced

See [docs/METHODOLOGY.md](docs/METHODOLOGY.md) and
[docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) — including the two axes (recency, POS) that are
**not** trustworthy in 1.0.0.
