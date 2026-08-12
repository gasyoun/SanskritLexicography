#!/usr/bin/env python3
"""B1 residual item (1): was the account inside a provider limit window during H2591?

H2598 blocker B1 owes one check before any call is reserved — whether the account was
under a limit window during the H2591 run — and names the `rc=1` cluster as "the strongest
available proxy". This script makes that proxy explicit instead of eyeballed: it rebuilds
the per-call wall-clock timeline from the sealed reservation ledger, joins it to each
envelope's exit code and model attestation, and reports whether the refusals form a
CONTIGUOUS interval in time (a limit window) or are scattered across the run (which would
point at per-call causes instead).

Read-only. Makes no call, spends nothing, writes nothing unless --out is given.

    python b1_limit_window_probe.py [--run-dir <h2591 dir>] [--out timeline.json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RUN_DIR = os.path.normpath(os.path.join(HERE, '..', 'h2591'))


def _utc(ns: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(ns / 1e9, tz=dt.timezone.utc)


def load_rows(run_dir: str) -> list[dict]:
    with open(os.path.join(run_dir, 'call_reservation.json'), encoding='utf-8') as handle:
        ledger = json.load(handle)
    reservations = {}
    for run in (ledger.get('runs') or {}).values():
        for item in run.get('reservations') or []:
            reservations[item['ordinal']] = item

    rows = []
    for path in sorted(glob.glob(os.path.join(run_dir, 'envelopes', '*.json'))):
        with open(path, encoding='utf-8') as handle:
            envelope = json.load(handle)
        book = reservations.get(envelope['ordinal']) or {}
        started, ended = book.get('reserved_at_ns'), book.get('finalized_at_ns')
        rows.append({
            'ordinal': envelope['ordinal'],
            'arm': envelope['arm'],
            'key1': envelope['key1'],
            'returncode': envelope.get('returncode'),
            'failure_class': envelope.get('failure_class'),
            'returned_model': envelope.get('returned_model'),
            'usage_total': sum(int((envelope.get('telemetry') or {}).get(name) or 0)
                               for name in ('input_tokens', 'output_tokens',
                                            'cache_read_tokens', 'cache_creation_tokens')),
            'started_utc': _utc(started).isoformat() if started else None,
            'ended_utc': _utc(ended).isoformat() if ended else None,
            'wall_s': round((envelope.get('wall_ms') or 0) / 1000, 1),
        })
    return sorted(rows, key=lambda row: row['ordinal'])


def verdict(rows: list[dict]) -> dict:
    refused = [row for row in rows if row['returncode']]
    clean = [row for row in rows if not row['returncode']]
    ordinals = [row['ordinal'] for row in refused]
    contiguous = bool(ordinals) and ordinals == list(range(min(ordinals), max(ordinals) + 1))

    # Time-contiguity is the real test: a limit window refuses everything inside it, so no
    # clean call may fall between the first and last refusal. Ordinal-contiguity alone is
    # weaker — the run is serial, so ordinals and time only ever agree here, but a caller
    # that ever parallelizes would break that identity and the check must not silently rely
    # on it.
    span = None
    interlopers = []
    if refused:
        first = min(row['started_utc'] for row in refused if row['started_utc'])
        last = max(row['ended_utc'] for row in refused if row['ended_utc'])
        span = {'from_utc': first, 'to_utc': last}
        interlopers = [row['ordinal'] for row in clean
                       if row['started_utc'] and first <= row['started_utc'] <= last]

    return {
        'calls': len(rows),
        'refused_rc1': len(refused),
        'refused_ordinals': ordinals,
        'ordinal_contiguous': contiguous,
        'refusal_span_utc': span,
        'clean_calls_inside_the_span': interlopers,
        'unattested_calls': [row['ordinal'] for row in rows if not row['returned_model']],
        'zero_usage_calls': [row['ordinal'] for row in rows if row['usage_total'] == 0],
        'zero_usage_rc0_calls': [row['ordinal'] for row in rows
                                 if row['usage_total'] == 0 and not row['returncode']],
        'consistent_with_a_limit_window': bool(refused) and contiguous and not interlopers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', default=DEFAULT_RUN_DIR)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    rows = load_rows(args.run_dir)
    report = verdict(rows)

    print('%-3s %-3s %-9s %-4s %-19s %-19s %8s %7s %s'
          % ('#', 'arm', 'key', 'rc', 'started (UTC)', 'ended (UTC)', 'wall', 'tokens',
             'model'))
    for row in rows:
        print('%-3d %-3s %-9s %-4s %-19s %-19s %7.1fs %7d %s'
              % (row['ordinal'], row['arm'], row['key1'][:9], row['returncode'],
                 (row['started_utc'] or '')[:19], (row['ended_utc'] or '')[:19],
                 row['wall_s'], row['usage_total'], row['returned_model'] or 'UNATTESTED'))

    print('\nrefusals (rc=1): %s  ordinal-contiguous=%s'
          % (report['refused_ordinals'], report['ordinal_contiguous']))
    if report['refusal_span_utc']:
        print('refusal span:    %s .. %s' % (report['refusal_span_utc']['from_utc'][:19],
                                             report['refusal_span_utc']['to_utc'][:19]))
    print('clean calls inside that span: %s' % (report['clean_calls_inside_the_span'] or 'none'))
    print('zero-usage: all=%s  rc=0 only=%s' % (report['zero_usage_calls'],
                                                report['zero_usage_rc0_calls']))
    print('unattested: %s' % (report['unattested_calls'] or 'none'))
    print('\nconsistent with ONE provider limit window: %s'
          % report['consistent_with_a_limit_window'])
    print('NOTE: consistency is not proof. The provider exposes no queryable limit history,'
          '\n      and `claude auth status --json` reports subscription only, so this'
          '\n      remains a proxy — it can refute a window, never confirm one.')

    if args.out:
        with open(args.out, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump({'schema': 'pwg.b1_limit_window_probe.v1',
                       'run_dir': os.path.basename(args.run_dir),
                       'calls': rows, 'report': report}, handle,
                      ensure_ascii=False, indent=1)
            handle.write('\n')
        print('wrote %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
