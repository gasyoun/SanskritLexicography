#!/usr/bin/env python
"""Append-only, credential-safe telemetry and bug census for headless runs."""
import collections
import datetime
import json
import math
import os
import sys

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gate_evidence as ge                                          # noqa: E402


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
    # H2079 (#945): the CLI envelope's own API time, and wall-minus-API. `elapsed_ms` remains the
    # gated wall reading — these exist so a reading can be DECOMPOSED after the fact into route
    # time vs time the CLI spent retrying internally (a rate-limited CLI hangs rather than
    # reporting 429, FINDINGS §270). Absent on any call that returned no envelope.
    'duration_api_ms', 'api_gap_ms',
    # H2095 (#946): the ceiling THAT ACTUALLY JUDGED this reading. Without it a probe row cannot
    # be read standalone — `PROBE_LATENCY_CEILING_MS` moved 30 000 -> 33 000 -> 65 000 in a single
    # day (31-07) while the `policy` token stayed 'production_v1'. H2118 then repaired the token
    # itself (one name per ceiling value, every gate deriving from `probe_log.POLICIES`), so
    # `policy` is sufficient provenance again — but this key stays: it records what judged a row
    # at the moment it was written, which no later reading of a policy table can reconstruct for
    # rows written before the repair.
    'latency_ceiling_ms',
    # H2326 (#1172): a non-success probe classification is otherwise unreadable after the fact.
    # `err_pattern` is WHICH alternative of the classifier regex matched (`429` vs `usage limit`
    # vs `rate limit` — an account weekly cap and a per-model capacity refusal are the same
    # `rate_limit` class but different decisions), and `raw_envelope_path` is the BASENAME of the
    # gitignored file under the probe's `output/` that holds the provider's own text. Both are
    # bounded: the pattern is a <=40-char slice matched by a fixed regex, the path a basename —
    # the envelope body itself never enters the event row.
    'err_pattern', 'raw_envelope_path',

    # H2878 (issue #1680): the no-output-progress reading for the spawn behind this row.
    # `elapsed_ms` says how long the call took; these say whether it was ALIVE for that long.
    # `bytes_seen` is result bytes on stdout, `quiet_ms` the LONGEST stretch in which none
    # arrived, and `killed_reason` distinguishes a stalled-output kill from the total-wall
    # backstop -- the distinction FINDINGS §378 named as missing and the 13-08 c1 reading
    # (300 198 ms, 0 output bytes, recorded as a bare `timeout`) needed and did not have.
    # Three bounded integers/enums; no payload, no path, no provider text.
    'bytes_seen', 'quiet_ms', 'killed_reason',

    # H2647: the BOX's state at the moment the reading was taken, so a row can tell its
    # SUBJECT (the account and route) from its ENVIRONMENT (this machine). Without these a
    # probe that died of local memory starvation is indistinguishable from one refused by
    # the provider -- on 13-08-2026 a c1 probe died in 7 754 ms on a JavaScriptCore
    # MemoryExhaustion assert at 97 % commit charge and was read as ACCOUNT CAPACITY.
    # Bounded by construction: eight scalars only, produced solely by host_state.capture()
    # (which pins this exact set in its own selftest) -- six small integers, one percentage,
    # two process counts. No hostname, no path, no user, no payload; nothing here can carry
    # provider text, so the leak this allowlist exists to prevent is not reachable through
    # them. Dropped by append_event when None, so a row from a host that cannot be measured
    # (or a non-Windows box) is byte-for-byte what it was before.
    'host_total_phys_mb', 'host_avail_phys_mb', 'host_commit_limit_mb',
    'host_commit_used_mb', 'host_commit_pct', 'host_memory_load_pct',
    'host_proc_node', 'host_proc_python',
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
    model_call_events = 0           # call-level events the dedup ran over (W1 accounting)
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
            model_call_events += 1
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
        # W1 (H3748, #1803 C8-7): `model_calls` is the DEDUPED count; this is how many
        # call-level events the dedup was actually applied to. The two being equal is the
        # evidence that no re-append was swallowed, and the gap is the evidence that some
        # were. Pre-W1 only the deduped side was reported, so a census over zero events
        # and a census over 900 printed the same shape.
        'model_call_events': model_call_events,
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


def write_census(events_path, output_path, evidence_path=None):
    """Write the bug census, and beside it the W1 gate-evidence sidecar.

    #1803 row C8-7: the census counters bypass the exactly-once dedup they document, so a
    re-appended event inflates cards/clean/calls -- and the census printed the same shape
    over an empty log as over a real run. The counting logic is unchanged; what is new is
    that the run now records how many events it read, how many call-level events the dedup
    ran over, and how many conflicted. A census over an EMPTY log is the one declared
    legitimate emptiness (a fresh box before the first run).
    """
    rows = read_events(events_path)
    payload = build_census(rows)
    tmp = output_path + '.tmp.%d' % os.getpid()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, output_path)

    ev = ge.GateEvidence('run_observability_census',
                         'exactly-once bug census over the append-only events log (C8-7)')
    ev.add_input('events', path=events_path, units=len(rows))
    ev.add_predicate('call_id_dedup', evaluations=payload['model_call_events'],
                     hits=len(payload['conflicting_call_ids']))
    ev.add_predicate('unaccounted_keys', evaluations=len(rows),
                     hits=len(payload['unaccounted_keys']))
    ev.note('model_calls_deduped', payload['model_calls'])
    ev.note('cards', payload['cards'])
    ev.set_verdict('pass' if not payload['conflicting_call_ids'] else 'fail')
    if not rows:
        ev.declare_expected_empty(
            'no_events_logged',
            'a fresh box before the first run: every census counter is honestly zero')
    ev.assert_nonvacuous()
    ev.emit(evidence_path or ge.sidecar_for(output_path))
    return payload
