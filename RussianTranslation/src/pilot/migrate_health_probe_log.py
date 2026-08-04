#!/usr/bin/env python
"""One-time backfill: copy historical probe_call rows into the canonical
`output/health_probe_log.jsonl` (B3 residual, H2240).

Before H2240, `kitchen_slices.health_ribbon` glob-scraped every
`*_probe_events.jsonl` under `pilot/output` (one file per account, e.g.
`h963_c4_gate0_probe_events.jsonl`). Since H2240, `live_probe`'s `_emit`
writes every NEW probe reading straight into the canonical file, but a
checkout that already has history in the old per-account files would show a
truncated sparkline (canonical starts empty) until those old readings are
folded in once. This script does that fold — idempotent, so re-running it
is always safe.

    python src/pilot/migrate_health_probe_log.py           # writes
    python src/pilot/migrate_health_probe_log.py --dry-run # report only

Dedupe key: (run_id, purpose, account) — the same triple `live_probe`'s own
exact-run_id read discipline (#729) uses, so a row already present (e.g.
from a NEW post-H2240 probe whose run also happens to be re-scanned here)
is never duplicated.
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, 'output')
CANONICAL = os.path.join(OUTPUT_DIR, 'health_probe_log.jsonl')


def _dedupe_key(row):
    return (row.get('run_id'), row.get('purpose'), row.get('account'))


def _read_rows(path):
    rows = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def source_files():
    """Every legacy per-account probe events file, EXCLUDING the canonical file itself."""
    pats = ('*gate0*probe_events.jsonl', '*_probe_events.jsonl')
    seen = set()
    out = []
    for pat in pats:
        for path in sorted(glob.glob(os.path.join(OUTPUT_DIR, pat))):
            if path == CANONICAL or path in seen:
                continue
            seen.add(path)
            out.append(path)
    return out


def migrate(dry_run=False):
    existing_keys = set()
    if os.path.exists(CANONICAL):
        for row in _read_rows(CANONICAL):
            existing_keys.add(_dedupe_key(row))

    to_write = []
    for path in source_files():
        for row in _read_rows(path):
            if row.get('event') != 'probe_call':
                continue
            key = _dedupe_key(row)
            if key in existing_keys:
                continue
            existing_keys.add(key)
            to_write.append(row)

    print('%d source file(s) scanned; %d new row(s) to migrate%s'
          % (len(source_files()), len(to_write), ' (dry-run)' if dry_run else ''))
    if dry_run or not to_write:
        return 0

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CANONICAL, 'a', encoding='utf-8') as fh:
        for row in to_write:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('wrote %d row(s) -> %s' % (len(to_write), CANONICAL))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    return migrate(dry_run=a.dry_run)


if __name__ == '__main__':
    sys.exit(main())
