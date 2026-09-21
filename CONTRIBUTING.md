# Contributing

Thanks for taking the list seriously enough to argue with it. This project is a dataset plus a
small stdlib-only library, so the bar is: **reproducible, reviewable, licensed**.

## Ground rules

1. `make validate`, `make test`, `make lint` must pass. CI runs them on Python 3.10 / 3.12 / 3.13.
2. Data changes are **proposed in an issue first** (`data-request` template), with the measurement
   that motivates them. A row that changes a level, a count or a rank is a release change.
3. Any edit under `data/` requires regenerating the ledger in the same PR:
   `make ledger` → commit `data/SHA256SUMS.txt`. CI fails on a mismatch, which is the point.
4. Do not add files > 100 MB (GitHub rejects them) and do not vendor third-party wordlists —
   cite them by URL and hash, as `docs/PROVENANCE.md` does.
5. Documentation must keep claims bounded by evidence. If a number is not in a file in this repo,
   say where it comes from — or don't write it. Known flaws stay documented
   ([docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)); a fix must flip its `expected` check to
   `DRIFT` and update that file in the same PR.

## Setup

```bash
git clone https://github.com/X-Trivle/LexiCore.git && cd LexiCore
python3 -m venv .venv && . .venv/bin/activate
make install            # pip install -e ".[dev]"
make validate && make test && make lint
```

Layout: `src/lexicore/` (library), `tests/` (pytest), `scripts/` (repo tooling), `data/`
(release + derived), `docs/` (prose), `reports/upstream/` (immutable originals),
`ecosystem/` (companion products).

## Making each kind of change

**Code / API.** Backward compatibility matters: `Entry`, `load_entries`, `validate_data` are the
public surface. Add tests for behaviour, not for implementation. Ruff config is in `pyproject.toml`
(line length 100, `E,F,I,UP,B,C4,SIM`).

**A new column in `data/LexiCore_5000.csv`.** Update `models.CSV_COLUMNS` and `Entry.to_row()`
(the round-trip test catches drift), document it in `docs/DATA_DICTIONARY.md`, bump the version in
`pyproject.toml` + `CITATION.cff` + `CHANGELOG.md`, and refresh the ledger.
Add the expectation to `validate.py` so the next edit is noticed.

**Re-deriving `data/derived/`.** `make derived CHECKPOINT=/path/to/checkpoint/out`. Output is
deterministic (`gzip mtime=0`), so a rebuild should be a no-op; if it isn't, that is a bug worth a
report.

**Research changes (weights, thresholds, gates).** Do them on the candidate table, not on the
released CSV:

```bash
python -m lexicore reweight --freq 0.5 --disp 0.25 --util 0.25   # prints Jaccard + samples
```

Open an issue with the diff and one concrete evaluation (e.g. held-out type coverage, or overlap
with a published syllabus). "It feels better" is not the bar.

**A fix for a documented flaw.** Best contributions in order of value right now:
real year buckets ([KI-2](docs/KNOWN_ISSUES.md#ki-2-the-recency-axis-was-never-computed)),
re-tagged POS ([KI-3](docs/KNOWN_ISSUES.md#ki-3-pos-is-a-dictionary-guess)),
re-segmented subtitles ([KI-7](docs/KNOWN_ISSUES.md#ki-7-dispersion-is-not-on-one-scale)),
honest confidence ([KI-5](docs/KNOWN_ISSUES.md#ki-5-confidence-is-a-cap-not-a-calibrated-probability)).

## Pull request flow

Use the template. Keep one logical change per PR; `feat(data):`, `fix(lib):`, `docs:`,
`test:`, `chore:`. If you touched data, paste the output of `make validate` and
`make checksums` into the PR description.

## Licensing your contribution

By opening a PR you offer your contribution under the project's CC BY 4.0 for data and docs and
the same terms as the code (see [LICENSE](LICENSE), [NOTICE.md](NOTICE.md)). State clearly if you
cannot (e.g. third-party encumbered data) — that part will be rejected rather than laundered.

## Conduct

Be precise and be kind. Disagreements happen about word levels, which are judgement calls; argue
with the evidence, not the person. [Code of Conduct](CODE_OF_CONDUCT.md).
