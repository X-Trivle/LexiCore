# Security policy

LexiCore-5000 is a static dataset plus a stdlib-only reader, so the realistic attack surface is
small but not zero.

## Supported versions

| version | supported |
|---|---|
| 1.0.x | yes |
| < 1.0 | no (rebuild from 1.0.x) |

## What we treat as a security issue

* Any file under `data/` being replaced or silently edited without a commit and without a ledger
  entry — `make checksums` is the detection; a bypass is a bug.
* A parser crash or unbounded memory growth from a malformed CSV/JSON in `src/lexicore/io.py`
  (the readers must stay safe on untrusted copies of the file).
* Credential leakage: a token, bucket key or internal URL committed anywhere in the tree. The
  release checkpoint was published to a third-party file host; the repository must never contain
  host credentials. `reports/upstream/done/*.flag` is kept only as a record of the runner's
  resume behaviour, and contains no secrets.

## What we do not treat as a security issue

Data-quality defects (wrong POS, weak levels, missing recency). Those are documented in
[docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) and handled as ordinary issues.

## Reporting

Open a **private** security advisory:
<https://github.com/X-Trivle/LexiCore/security/advisories/new>.
We aim to acknowledge within 5 working days. Please do not open a public issue first.
