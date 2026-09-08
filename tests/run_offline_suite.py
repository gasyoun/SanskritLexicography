#!/usr/bin/env python3
"""Runner for the offline contract-pin suite (H4353).

Runs, in one pytest session:

* ``tests/`` — the HeadwordLists / data / scripts / tools / dashboard pins
  (``conftest.py`` disables the network and points every external data root
  at a non-existent directory before a single module is imported);
* ``HeadwordLists/works_catalogue/test_parse_ncc.py`` — the pre-existing
  NCC key-repair pin (H1671);
* ``docs_site/test_docs_site.py`` — skips itself without ``zettelkastenwiki``.

The seven ``progress_dashboard/*_selftest.py`` scripts are invoked from
``tests/test_dashboard_generators.py`` as subprocesses, so they are part of
the same green/red verdict.

Usage::

    python tests/run_offline_suite.py            # full suite, quiet
    python tests/run_offline_suite.py -k union   # any pytest args pass through

Exit code is pytest's. Needs ``pytest`` and ``sanskrit-util``
(``pip install "sanskrit-util @ git+https://github.com/sanskrit-lexicon/sanskrit-util#subdirectory=py"``).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
TARGETS = [
    "tests",
    "HeadwordLists/works_catalogue/test_parse_ncc.py",
    "docs_site/test_docs_site.py",
]


def main(argv: list[str]) -> int:
    import pytest  # noqa: E402  (imported late so the missing-dep message is readable)

    # Belt and braces: the same env hardening conftest.py applies, set here too so
    # that modules imported by the pre-existing tests see it as well.
    nowhere = str(REPO / "tests" / "_nonexistent_external_root")
    for var in ("CSL_ORIG_V02", "PWG_INPUT_DIR", "DCS_LEMMA_SUMMARY", "SSC_DIR",
                "KOSHA_FREQ", "HERITAGE_MIRROR_DATA", "PWG_DATA_ROOT"):
        os.environ[var] = nowhere
    os.environ.setdefault("PYTHONUTF8", "1")

    args = [str(REPO / t) for t in TARGETS] + ["-q", "-p", "no:cacheprovider"] + argv
    t0 = time.monotonic()
    rc = pytest.main(args)
    print(f"offline suite: exit {rc} · elapsed {time.monotonic() - t0:.1f}s · "
          f"network disabled · external roots → {nowhere}")
    return int(rc)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
