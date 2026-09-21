PY ?= python3
DATA ?= data
CHECKPOINT ?= ../checkpoint/out   # directory holding the release checkpoint's out/*.pkl

.PHONY: help install validate test lint derived checksums ledger clean dist

help:
	@echo "make install    - editable install with dev extras (pip install -e '.[dev]')"
	@echo "make validate   - integrity + release-contract checks on $(DATA)/"
	@echo "make checksums  - verify data/SHA256SUMS.txt and the manifest artifact hashes"
	@echo "make ledger     - regenerate data/SHA256SUMS.txt after a deliberate data/docs change"
	@echo "make test       - pytest"
	@echo "make lint       - ruff check"
	@echo "make derived CHECKPOINT=/path/to/out - rebuild data/derived/ from a checkpoint"
	@echo "make dist       - sdist + wheel into dist/"

install:
	$(PY) -m pip install -e ".[dev]"

validate:
	$(PY) -m lexicore validate

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests scripts

derived:
	$(PY) scripts/build_derived.py --checkpoint $(CHECKPOINT) --out $(DATA)/derived

checksums:
	$(PY) scripts/verify_checksums.py --data $(DATA)

ledger:
	$(PY) scripts/build_checksums.py --root .

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

dist:
	$(PY) -m build
