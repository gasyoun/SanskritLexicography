"""``python -m pwg_pipeline`` -- the supported operator entry point."""
from __future__ import annotations

from .cli import main

if __name__ == '__main__':
    raise SystemExit(main())
