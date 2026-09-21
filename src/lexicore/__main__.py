"""Allow ``python -m lexicore`` (same entry point as the ``lexicore`` script)."""
from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
