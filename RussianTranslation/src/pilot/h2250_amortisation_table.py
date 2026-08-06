#!/usr/bin/env python
"""H2250 -- read the committed h2250 raw envelopes and emit the amortisation table.

This is an ANALYSIS reader, not a third probe: the paid calls are issued by
`h2189_profile_ab.py` (the rig H2250 is required to reuse). What this adds is the one
thing that rig cannot report -- the `--max-turns 1` trivial phase comes back as
`subtype=error_max_turns`, so `summarise()` drops every trivial row as a failure and
prints `{}`. Those rows are not failures: they are billed calls with a complete `usage`
block, and their `cache_creation` / `cache_read` split IS the quantity under test.

Reads every `*.json` envelope under --root (recursing one level into per-batch dirs),
orders calls by file mtime within a batch, and prints per-call create/read/total plus the
amortisation verdict for each call after the first in its batch:

    AMORTISED   create == 0 and read == previous(create + read)
    PARTIAL     create > 0 but read >= previous read
    RE-CREATED  create ~= previous create (the v1.127.0 behaviour truth #1 records)

`--chrono` is the reading the memo uses. Per-batch grouping is an artefact of how the
paid calls had to be issued (one rig invocation per gap size); the cache does not know
about batches, so a call that opens a batch is NOT a cold baseline -- it is simply the
next call in one continuous sequence, and scoring it as `BASELINE` hides the very
comparison under test. `--chrono` merges every batch of one phase into one time-ordered
run and scores each call against the call that actually preceded it in wall time.

    python src/pilot/h2250_amortisation_table.py --root pwg_ru/h2250/raw
    python src/pilot/h2250_amortisation_table.py --root pwg_ru/h2250/raw --chrono
    python src/pilot/h2250_amortisation_table.py --root pwg_ru/h2250/raw --json

Model: authored by Opus 5 (`claude-opus-5[1m]`) for handoff H2250.
"""
import argparse
import datetime
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def load_envelope(path):
    with open(path, encoding='utf-8') as fh:
        raw = json.load(fh)
    usage = raw.get('usage') or {}
    creation = usage.get('cache_creation') or {}
    return {
        'file': os.path.basename(path),
        'mtime': os.path.getmtime(path),
        'subtype': raw.get('subtype'),
        'is_error': raw.get('is_error'),
        'num_turns': raw.get('num_turns'),
        'api_ms': raw.get('duration_api_ms'),
        'wall_ms': raw.get('duration_ms'),
        'create': usage.get('cache_creation_input_tokens') or 0,
        'read': usage.get('cache_read_input_tokens') or 0,
        'input': usage.get('input_tokens') or 0,
        'output': usage.get('output_tokens') or 0,
        'ttl_1h': creation.get('ephemeral_1h_input_tokens'),
        'ttl_5m': creation.get('ephemeral_5m_input_tokens'),
        'envelope_cost_usd': raw.get('total_cost_usd'),
    }


def phase_of(row):
    """`h2189_<phase>_<arm>_<key>_<n>.json` -- the phase is what makes two calls
    comparable at all, so it is what a chronological merge groups by."""
    parts = row['file'].split('_')
    return parts[1] if len(parts) > 1 else 'unknown'


def utc_hms(mtime):
    return datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).strftime('%H:%M:%S')


def verdict(prev, cur):
    """Classify one call against its predecessor in the same batch."""
    if prev is None:
        return 'BASELINE'
    prev_total = prev['create'] + prev['read']
    if cur['create'] == 0 and cur['read'] == prev_total:
        return 'AMORTISED'
    if cur['create'] == 0:
        return 'AMORTISED*'          # created nothing, but read != prev total
    if cur['read'] >= prev['read'] and cur['create'] < prev['create']:
        return 'PARTIAL'
    return 'RE-CREATED'


def batches(root):
    """{batch name: [rows ordered by mtime]}. A flat --root is one batch called '.'."""
    out = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        rows = [load_envelope(os.path.join(dirpath, f)) for f in filenames
                if f.endswith('.json') and not f.endswith('_rows.json')]
        if not rows:
            continue
        name = os.path.relpath(dirpath, root).replace('\\', '/')
        out[name] = sorted(rows, key=lambda r: r['mtime'])
    return dict(sorted(out.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--root', default=os.path.join(
        os.path.dirname(os.path.dirname(here)), 'pwg_ru', 'h2250', 'raw'))
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--chrono', action='store_true',
                    help='one time-ordered sequence per phase instead of per-batch groups')
    args = ap.parse_args()

    found = batches(args.root)
    if not found:
        print('no envelopes under %s' % args.root, file=sys.stderr)
        return 2

    for name, rows in found.items():
        for row in rows:
            row['batch'] = name

    if args.chrono:
        merged = {}
        for rows in found.values():
            for row in rows:
                merged.setdefault(phase_of(row), []).append(row)
        found = {ph: sorted(rows, key=lambda r: r['mtime'])
                 for ph, rows in sorted(merged.items())}

    for rows in found.values():
        prev = None
        for row in rows:
            row['verdict'] = verdict(prev, row)
            row['gap_s'] = None if prev is None else int(row['mtime'] - prev['mtime'])
            prev = row

    if args.json:
        print(json.dumps(found, ensure_ascii=False, indent=2, default=str))
        return 0

    print('%-22s %2s %8s %6s %9s %9s %9s %8s %7s  %-11s'
          % ('group', '#', 'utc', 'gap_s', 'create', 'read', 'total', 'api_ms',
             'out', 'verdict'))
    for name, rows in found.items():
        for i, r in enumerate(rows, 1):
            print('%-22s %2d %8s %6s %9d %9d %9d %8s %7d  %-11s'
                  % (name[:22], i, utc_hms(r['mtime']),
                     '-' if r['gap_s'] is None else r['gap_s'],
                     r['create'], r['read'], r['create'] + r['read'],
                     r['api_ms'], r['output'], r['verdict']))
    print('\nsubtypes seen: %s'
          % sorted({r['subtype'] for rows in found.values() for r in rows}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
