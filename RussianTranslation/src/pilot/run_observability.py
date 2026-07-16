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
    # D-I: a real model call emits ONE call-level 'model_call' event carrying call_id +
    # key_count (+ elapsed_ms) and, separately, one 'model_call_key' relation event per key.
    # The per-key events carry no elapsed_ms and are excluded from the latency/classification
    # census, so a 5-key call yields exactly one latency sample and one classification count.
    'call_id', 'key_count',
    # D-K: the two-phase probe records each call separately with its purpose (warmup / measured),
    # model, and output_bytes. The warm-up latency is EXCLUDED from the acceptance census.
    'purpose', 'output_bytes', 'model',
    # H1080 launch-control follow-up: typed probe policy/lane and measured schema verdict.
    'policy', 'executor_lane', 'schema_valid',
}

# per-key relation events: kept for key<->call provenance / repeated-failure tracking, but
# NEVER counted as a latency sample or a classification tally (that is the call-level event's job).
KEY_RELATION_EVENT = 'model_call_key'
# D-K: a warm-up probe call is telemetry-only — its latency/classification never enter the census.
WARMUP_PURPOSE = 'warmup'


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
    # D-I exactly-once accounting. A crash/restart can re-append an event to the append-only log,
    # so call-level 'model_call' events are DEDUPED by call_id (first occurrence wins). A repeat
    # carrying a DIFFERENT (elapsed_ms, classification) is a *conflicting duplicate* and is
    # surfaced in `conflicting_call_ids`. Per-key 'model_call_key' relation events NEVER count
    # toward calls, latency, or classification — they feed only the per-key repeated-failure map.
    seen_calls = {}                 # call_id -> (elapsed_ms, classification) of the first event
    conflicting = set()
    census_rows = []                # deduped call rows + measured probe + other (latency+classification)
    probe = {'warmup': [], 'measured': []}   # D-K: probe calls broken out, distinguishable from translation
    quota = []                      # rate-limit observations incl. the WARM-UP probe (total quota)
    seen_quota_calls = set()
    for r in rows:
        ev = r.get('event')
        if ev == KEY_RELATION_EVENT:
            continue                # key relations mirror the call -> never counted anywhere
        purpose = r.get('purpose')
        if purpose in ('warmup', 'measured'):          # D-K: record every probe call, distinguishably
            probe[purpose].append({'latency_ms': r.get('elapsed_ms'), 'classification': r.get('classification'),
                                   'output_bytes': r.get('output_bytes'), 'model': r.get('model')})
        if r.get('classification') == 'rate_limit':    # total quota observations: warm-up INCLUDED
            cid = r.get('call_id')
            if ev == 'model_call' and cid is not None:
                if cid not in seen_quota_calls:
                    seen_quota_calls.add(cid)
                    quota.append(r)
            else:
                quota.append(r)
        if purpose == WARMUP_PURPOSE:                  # D-K: warm-up EXCLUDED from latency + classification
            continue
        if ev == 'model_call' and r.get('call_id') is not None:
            cid = r['call_id']
            sig = (r.get('elapsed_ms'), r.get('classification'))
            if cid not in seen_calls:
                seen_calls[cid] = sig
                census_rows.append(r)
            elif seen_calls[cid] != sig:
                conflicting.add(cid)       # same call_id, different data -> real conflict
            # exact re-append of an already-seen call_id is idempotent -> silently dropped
            continue
        census_rows.append(r)
    classes = collections.Counter(r.get('classification') for r in census_rows if r.get('classification'))
    by_key = collections.defaultdict(collections.Counter)
    for row in rows:                # by_key scans ALL rows, incl. key-relation events (they carry key+class)
        if row.get('key') and row.get('classification') not in (None, 'success'):
            by_key[row['key']][row['classification']] += 1
    # one latency sample per unique call (key-relation + warm-up excluded; dupes deduped)
    latencies = [int(r['elapsed_ms']) for r in census_rows if r.get('elapsed_ms') is not None]
    unaccounted = sorted({key for r in rows for key in (r.get('unaccounted_keys') or [])})
    calls = sum(int(r.get('calls') or 0) for r in rows)
    retries = sum(int(r.get('retries') or 0) for r in rows)
    clean = sum(int(r.get('clean') or 0) for r in rows if r.get('event') == 'run_summary')
    cards = sum(int(r.get('cards') or 0) for r in rows if r.get('event') == 'run_summary')
    fidelity = sum(int(r.get('fidelity_rejects') or 0) for r in rows
                   if r.get('event') == 'run_summary')
    return {
        'schema': 'pwg.bug_census.v1', 'generated_at': utc_now(),
        'events': len(rows), 'classification_counts': dict(sorted(classes.items())),
        'model_calls': len(seen_calls), 'conflicting_call_ids': sorted(conflicting),
        'probe': probe,                 # D-K: warm-up + measured probe calls, distinct from translation
        'quota_observations': len(quota),   # total rate-limit observations incl. the warm-up probe
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
