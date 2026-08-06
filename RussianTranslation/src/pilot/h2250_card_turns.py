#!/usr/bin/env python
"""H2250 -- why the `card` phase cannot settle prefix amortisation on its own.

The trivial phase pins `--max-turns 1`, so one envelope == one model turn and its
`cache_creation`/`cache_read` pair is a clean read of the prefix. The card phase does
not: it is an agentic call that runs to completion, so the envelope's usage is a SUM
over however many turns the loop happened to take. Two identical card prompts that take
different turn counts therefore produce incomparable totals -- which is exactly what the
two H2250 card calls did.

This prints the per-call turn count next to the usage so the memo can say that with
numbers instead of asserting it.

    python src/pilot/h2250_card_turns.py

Model: authored by Opus 5 (`claude-opus-5[1m]`) for handoff H2250.
"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'pwg_ru', 'h2250', 'raw')


def main():
    paths = sorted(glob.glob(os.path.join(ROOT, '*', '*card*nakzatra*.json')),
                   key=os.path.getmtime)
    if not paths:
        print('no card envelopes under %s' % ROOT, file=sys.stderr)
        return 2
    print('%-26s %6s %8s %9s %9s %9s %8s %8s'
          % ('batch', 'turns', 'api_ms', 'create', 'read', 'total', 'out', 'usd'))
    for path in paths:
        with open(path, encoding='utf-8') as fh:
            raw = json.load(fh)
        usage = raw.get('usage') or {}
        create = usage.get('cache_creation_input_tokens') or 0
        read = usage.get('cache_read_input_tokens') or 0
        print('%-26s %6s %8s %9d %9d %9d %8s %8.4f'
              % (os.path.basename(os.path.dirname(path))[:26],
                 raw.get('num_turns'), raw.get('duration_api_ms'), create, read,
                 create + read, usage.get('output_tokens'),
                 raw.get('total_cost_usd') or 0.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
