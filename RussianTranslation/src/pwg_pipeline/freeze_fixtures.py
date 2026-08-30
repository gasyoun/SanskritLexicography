"""Mint the frozen ``expected.json`` for each replay campaign (step 8).

Run once when a fixture is added or deliberately re-baselined:

    python -m pwg_pipeline.freeze_fixtures --matrix tests/fixtures/pwg_pipeline

Re-baselining is a reviewable act: the diff of ``expected.json`` is the record
of what changed in the contract, which is exactly what the replay gate compares
against on every later run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

if __package__ in (None, ''):  # pragma: no cover - direct-script invocation
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'pwg_pipeline'

from . import replay  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='freeze replay expectations')
    parser.add_argument('--matrix', required=True)
    parser.add_argument('--campaign', action='append')
    args = parser.parse_args(argv)
    names = args.campaign or list(replay.CAMPAIGNS)
    written = []
    for name in names:
        directory = os.path.join(args.matrix, name)
        actual = replay.freeze(directory)
        written.append({'campaign': name,
                        'jobs': len(actual['jobs']),
                        'calls': actual['accounting']['calls'],
                        'store_rows': actual['store']['rows']})
    sys.stdout.write(json.dumps(
        {'frozen': written}, ensure_ascii=False, indent=2) + '\n')
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
