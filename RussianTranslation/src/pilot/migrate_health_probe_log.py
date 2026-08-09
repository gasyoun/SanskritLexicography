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
DEFAULT_OUTPUT_DIR = os.path.join(HERE, 'output')


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


def source_files(output_dir, canonical):
    """Every legacy per-account probe events file, EXCLUDING the canonical file itself."""
    pats = ('*gate0*probe_events.jsonl', '*_probe_events.jsonl')
    seen = set()
    out = []
    for pat in pats:
        for path in sorted(glob.glob(os.path.join(output_dir, pat))):
            if os.path.abspath(path) == os.path.abspath(canonical) or path in seen:
                continue
            seen.add(path)
            out.append(path)
    return out


def migrate(dry_run=False, output_dir=None):
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    canonical = os.path.join(output_dir, 'health_probe_log.jsonl')
    existing_keys = set()
    if os.path.exists(canonical):
        for row in _read_rows(canonical):
            existing_keys.add(_dedupe_key(row))

    sources = source_files(output_dir, canonical)
    to_write = []
    for path in sources:
        for row in _read_rows(path):
            if row.get('event') != 'probe_call':
                continue
            key = _dedupe_key(row)
            if key in existing_keys:
                continue
            existing_keys.add(key)
            to_write.append(row)

    print('%d source file(s) scanned; %d new row(s) to migrate%s'
          % (len(sources), len(to_write), ' (dry-run)' if dry_run else ''))
    if dry_run or not to_write:
        return 0

    os.makedirs(output_dir, exist_ok=True)
    with open(canonical, 'a', encoding='utf-8') as fh:
        for row in to_write:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('wrote %d row(s) -> %s' % (len(to_write), canonical))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--dry-run', action='store_true')
    # H2269: allow pointing at another checkout's pilot/output (worktree dual-run,
    # or a frozen snapshot) without copying files into the script's sibling dir.
    ap.add_argument('--output-dir', default=None,
                    help='pilot/output directory (default: sibling output/ of this script)')
    a = ap.parse_args()
    return migrate(dry_run=a.dry_run, output_dir=a.output_dir)


if __name__ == '__main__':
    sys.exit(main())
