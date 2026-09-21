## What and why

<!-- One paragraph. If this closes an issue, link it. -->

Closes #

## Type of change

- [ ] docs only
- [ ] library / tooling code
- [ ] tests
- [ ] data change (any byte under `data/`) - **requires an accepted issue**
- [ ] derived data rebuild (`make derived`)

## Evidence

<!-- For data changes: the measurement that motivates it, and how to reproduce it. -->

## Checks

Paste real output:

```text
$ make validate
$ make checksums
$ make test
$ make lint
```

- [ ] I re-generated `data/SHA256SUMS.txt` (`make ledger`) if I touched `data/`
- [ ] I updated `docs/DATA_DICTIONARY.md` / `docs/KNOWN_ISSUES.md` if behaviour or schema changed
- [ ] No file I added is a third-party wordlist, corpus dump, or larger than 100 MB
- [ ] My contribution is offered under the project's licence (see `NOTICE.md`)
