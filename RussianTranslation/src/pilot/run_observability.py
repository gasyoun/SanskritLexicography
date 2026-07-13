#!/usr/bin/env python
"""Append-only, credential-safe telemetry and bug census for headless runs."""
import collections
import datetime
import json
import math
import os


SCHEMA = 'pwg.run_event.v1'
ALLOWED = {
    'run_id', 'lease_id', 'window_id', 'key', 'attempt', 'account',
    'manifest_hash', 'result_hash', 'stage', 'event', 'classification',
    'elapsed_ms', 'calls', 'retries', 'reset_at', 'cards', 'clean',
    'fidelity_rejects', 'unaccounted_keys', 'store_before', 'store_after',
    'tm_before', 'tm_after', 'note',
}


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='milliseconds').replace('+00:00', 'Z')


def append_event(path, **values):
    """Append one bounded event. Unknown fields are refused to prevent payload leaks."""
    unknown = set(values) - ALLOWED
    if unknown:
        raise ValueError('unsafe/unknown event fields: %s' % ','.join(sorted(unknown)))
    row = {'schema': SCHEMA, 'ts': utc_now()}
    row.update({k: v for k, v in values.items() if v is not None})
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
    return row


def read_events(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding='utf-8') as f:
        for number, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get('schema') != SCHEMA:
                raise ValueError('%s:%d: unsupported event schema' % (path, number))
            rows.append(row)
    return rows


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(math.ceil(p * len(ordered))) - 1)]


def build_census(rows):
    classes = collections.Counter(r.get('classification') for r in rows
                                  if r.get('classification'))
    by_key = collections.defaultdict(collections.Counter)
    for row in rows:
        if row.get('key') and row.get('classification') not in (None, 'success'):
            by_key[row['key']][row['classification']] += 1
    latencies = [int(r['elapsed_ms']) for r in rows if r.get('elapsed_ms') is not None]
    unaccounted = sorted({key for r in rows for key in (r.get('unaccounted_keys') or [])})
    calls = sum(int(r.get('calls') or 0) for r in rows)
    retries = sum(int(r.get('retries') or 0) for r in rows)
    clean = sum(int(r.get('clean') or 0) for r in rows if r.get('event') == 'run_summary')
    cards = sum(int(r.get('cards') or 0) for r in rows if r.get('event') == 'run_summary')
    fidelity = sum(int(r.get('fidelity_rejects') or 0) for r in rows
                   if r.get('event') == 'run_summary')
    quota = [r for r in rows if r.get('classification') == 'rate_limit']
    return {
        'schema': 'pwg.bug_census.v1', 'generated_at': utc_now(),
        'events': len(rows), 'classification_counts': dict(sorted(classes.items())),
        'repeated_by_key': {k: dict(v) for k, v in sorted(by_key.items()) if sum(v.values()) > 1},
        'latency_ms': {'p50': percentile(latencies, .50), 'p95': percentile(latencies, .95),
                       'max': max(latencies) if latencies else None},
        'calls': calls, 'retries': retries, 'cards': cards, 'audit_clean': clean,
        'clean_rate': clean / cards if cards else None,
        'fidelity_rejects': fidelity, 'fidelity_rate': fidelity / cards if cards else None,
        'quota_incidents': len(quota),
        'quota_resets': sorted({r.get('reset_at') for r in quota if r.get('reset_at')}),
        'unaccounted_keys': unaccounted,
    }


def write_census(events_path, output_path):
    payload = build_census(read_events(events_path))
    tmp = output_path + '.tmp.%d' % os.getpid()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, output_path)
    return payload
