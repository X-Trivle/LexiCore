# Ecosystem

Things built on `data/LexiCore_5000.csv`. Each subfolder documents one project: what it is, how it
relates to the list, and — where possible — what we could measure.

| project | what | relationship to the list |
|---|---|---|
| [lexideck-multilingual/](lexideck-multilingual/) | Anki deck: 5,700+ words A1–C1, 5 rotating examples per word, human audio, IPA, illustration, 12 languages | uses all 5,000 LexiCore headwords **plus ~700 additions**; notes are tagged `LexiCore` and carry the released CEFR level |

## Adding a project

Create `ecosystem/<name>/README.md` with:

1. what it is and where to get it;
2. exactly how it consumes the list (a file, a column, a level mapping);
3. one verifiable statement about that consumption — e.g. "N of M sample entries match a headword"
   — with the command to reproduce it, as
   [lexideck-multilingual/DECK_STRUCTURE.md](lexideck-multilingual/DECK_STRUCTURE.md) does;
4. a note on assets: material that belongs to the product (screenshots, audio, illustrations) is
   not part of the dataset's CC BY 4.0 grant — say so in the folder and list it in
   [NOTICE.md](../NOTICE.md).
