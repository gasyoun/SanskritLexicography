#!/usr/bin/env python3
"""H5403: the cards/hour figure of one PWG-RU volume wave, derived, never hand-typed.

H4342 (b) asked for "the first honest cards/hour figure"; H5403 makes it a tool so
every later wave reports it the same way instead of a prose estimate. Input is the
pair of artifacts a `bounded_staged_run.py` window already writes:

    volume.report.json    -- pwg.bounded_staged_run.v1 (summary.accepted_order, calls_spent)
    volume.events.jsonl   -- pwg.run_event.v1 rows (probe_call / attempt_* / model_call)

Three denominators, all reported, because they answer different questions:

  wall_clock_s        first event -> last event (probe legs included; what a slot costs)
  dispatch_s          first attempt_start -> last attempt_end (cards only, probes excluded)
  paid_calls          probe legs + card calls (the ration/quota unit actually spent)

"Cards" = leases whose cards were promoted into the store (summary.accepted_order),
never leases attempted: a defect card that lands in `requeue_backlog_keys` cost a
paid call and produced no store row, and a rate that hid that would flatter the lane.

Usage:
    python cards_per_hour.py --report ../../pwg_ru/h5403/volume.report.json \
                             --events ../../pwg_ru/h5403/volume.events.jsonl \
                             [--json out.json]
Exit 0 on a computed figure, 2 when the artifacts cannot support one.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def parse_ts(value):
    text = (value or '').replace('Z', '+00:00')
    return dt.datetime.fromisoformat(text)


def load_events(path):
    rows = []
    with open(path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def measure(report, events):
    summary = report.get('summary') or {}
    promoted_leases = list(summary.get('accepted_order') or [])
    wave = summary.get('wave') or {}
    receipt = wave.get('receipt') or {}
    stamps = sorted(parse_ts(row['ts']) for row in events if row.get('ts'))
    if not stamps:
        raise SystemExit(2)
    attempt_stamps = sorted(parse_ts(row['ts']) for row in events
                            if row.get('event') in ('attempt_start', 'attempt_end') and row.get('ts'))
    probe_calls = sum(1 for row in events if row.get('event') == 'probe_call')
    card_calls = int(summary.get('calls_spent') or 0)
    wall_s = (stamps[-1] - stamps[0]).total_seconds()
    dispatch_s = ((attempt_stamps[-1] - attempt_stamps[0]).total_seconds()
                  if len(attempt_stamps) > 1 else None)
    cards = len(promoted_leases)
    paid_calls = probe_calls + card_calls
    out = {
        'schema': 'pwg.cards_per_hour.v1',
        'run_id': report.get('run_id'),
        'cards_promoted': cards,
        'leases_attempted': len(promoted_leases) + len(summary.get('requeue_backlog_keys') or []),
        'requeue_backlog_keys': list(summary.get('requeue_backlog_keys') or []),
        'sense_rows_promoted': None,
        'paid_calls_total': paid_calls,
        'paid_calls_probe_legs': probe_calls,
        'paid_calls_cards': card_calls,
        'calls_reserved': summary.get('calls_reserved'),
        'window_start_utc': stamps[0].isoformat().replace('+00:00', 'Z'),
        'window_end_utc': stamps[-1].isoformat().replace('+00:00', 'Z'),
        'wall_clock_s': round(wall_s, 3),
        'dispatch_s': round(dispatch_s, 3) if dispatch_s is not None else None,
        'cards_per_hour_wall': round(cards * 3600.0 / wall_s, 2) if wall_s > 0 else None,
        'cards_per_hour_dispatch': (round(cards * 3600.0 / dispatch_s, 2)
                                    if dispatch_s else None),
        'cards_per_paid_call': round(cards / paid_calls, 4) if paid_calls else None,
        'gen_model_version': receipt.get('gen_model_version'),
    }
    tail = receipt.get('stdout_tail') or ''
    for token in tail.split('\n'):
        if 'sense rows' in token:
            for word in token.replace(';', ' ').split():
                if word.isdigit() and 'sense rows' in token.split(word, 1)[1][:20]:
                    out['sense_rows_promoted'] = int(word)
                    break
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--report', required=True)
    ap.add_argument('--events', required=True)
    ap.add_argument('--json', help='also write the measurement to this path')
    args = ap.parse_args(argv)
    with open(args.report, encoding='utf-8') as handle:
        report = json.load(handle)
    out = measure(report, load_events(args.events))
    if args.json:
        with open(args.json, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(out, handle, ensure_ascii=False, indent=1, sort_keys=True)
            handle.write('\n')
    print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    if out['cards_per_hour_wall'] is None:
        return 2
    print('\n%s: %d card(s) promoted in %.1f s wall -> %.1f cards/hour '
          '(dispatch-only %.1f cards/hour), %.2f cards per paid call (%d call(s))'
          % (out['run_id'], out['cards_promoted'], out['wall_clock_s'],
             out['cards_per_hour_wall'],
             out['cards_per_hour_dispatch'] or float('nan'),
             out['cards_per_paid_call'], out['paid_calls_total']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
