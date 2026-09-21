---
name: Data change proposal
about: Add/remove/re-level words, fix a documented flaw, add a column
labels: data, proposal
---

> Data changes are proposals first. A PR that edits `data/` without an accepted issue here will be
> closed, because the ledger hash is what everyone else cites.

**Proposal** (one sentence)

**Which documented issue does it fix?** Link a `KI-n` from `docs/KNOWN_ISSUES.md` if applicable.

**Measurement**
How was it measured? Corpora, sample size, script, and the resulting numbers.

**Blast radius**
Rows changed: ____ | levels changed: ____ | does it move `rank_global`? ____

**Reproduction recipe**
What should a reviewer run to see it for themselves?
