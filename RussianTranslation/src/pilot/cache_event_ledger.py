#!/usr/bin/env python
"""Sealed run manifests + append-only JSONL events (H2702).

Layout of one run directory:

    run.manifest.json
    events.jsonl
    requests/<request_sha256>.json
    responses/<request_sha256>.<attempt>.json
    summary.json
    tm/                  # experimental only

A torn last line or a garbage interleaved write fails closed. Terminal events
are fsynced. Missing usage is null plus a reason, never zero. Resume skips
requests that already have a terminal event.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import cache_identity as ident  # noqa: E402

TERMINAL_KINDS = frozenset({
    'terminal_response', 'park', 'stop', 'completion', 'tm_short_circuit',
})
USAGE_ZERO_KEYS = (
    'input_tokens', 'output_tokens', 'cache_hit_tokens', 'cache_miss_tokens',
    'prompt_tokens', 'completion_tokens',
)


class LedgerError(ValueError):
    pass


def _utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def normalize_usage(usage, reason=None):
    """Missing usage stays null + reason. Never coerce absent counters to 0."""
    if usage is None:
        return None, reason or 'usage_absent'
    if not isinstance(usage, dict):
        return None, reason or 'usage_malformed'
    if all((usage.get(key) in (0, None) for key in USAGE_ZERO_KEYS)):
        if all(usage.get(key) is None for key in USAGE_ZERO_KEYS):
            return None, reason or 'usage_absent'
        # All-zero usage is unevaluable (H2591), not a free call.
        return None, reason or 'usage_all_zero'
    cleaned = {}
    for key, value in usage.items():
        cleaned[key] = value
    return cleaned, None


def read_events(path):
    if not os.path.isfile(path):
        return []
    events = []
    with open(path, 'rb') as handle:
        raw = handle.read()
    if not raw:
        return []
    if raw.endswith(b'\r\n') or (b'\r' in raw and b'\n' not in raw.split(b'\r')[-1:]):
        # Mixed or CR-only is treated as torn/interleaved.
        raise LedgerError('ledger line endings are not LF')
    text = raw.decode('utf-8')
    if text.startswith('\ufeff'):
        raise LedgerError('ledger has a UTF-8 BOM')
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    else:
        raise LedgerError('torn ledger: last line has no terminating LF')
    prev_seq = 0
    for index, line in enumerate(lines, 1):
        if not line:
            raise LedgerError('empty ledger line at %d' % index)
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError('torn/interleaved ledger at line %d: %s' % (index, exc))
        if not isinstance(event, dict):
            raise LedgerError('ledger line %d is not an object' % index)
        seq = event.get('seq')
        if not isinstance(seq, int) or seq != prev_seq + 1:
            raise LedgerError('ledger seq gap at line %d (prev=%s got=%s)' % (
                index, prev_seq, seq))
        prev_seq = seq
        events.append(event)
    return events


def completed_request_ids(events):
    done = set()
    for event in events:
        if event.get('kind') in TERMINAL_KINDS and event.get('request_id'):
            done.add(event['request_id'])
    return done


SLOT_TERMINAL_KINDS = frozenset({
    'terminal_response', 'park', 'stop', 'tm_short_circuit',
})


def completed_pair_slots(events):
    """Slots keyed by (request_id, cold_warm). Cold and warm share request_id."""
    done = set()
    for event in events:
        if event.get('kind') not in SLOT_TERMINAL_KINDS:
            continue
        rid = event.get('request_id')
        cw = event.get('cold_warm')
        if rid and cw in ('cold', 'warm'):
            done.add((rid, cw))
    return done


class EventLedger:
    def __init__(self, run_dir):
        self.run_dir = os.path.abspath(run_dir)
        self.manifest_path = os.path.join(self.run_dir, 'run.manifest.json')
        self.events_path = os.path.join(self.run_dir, 'events.jsonl')
        self.lock = threading.Lock()
        self._seq = 0
        self.manifest = None

    def seal(self, spec):
        os.makedirs(os.path.join(self.run_dir, 'requests'), exist_ok=True)
        os.makedirs(os.path.join(self.run_dir, 'responses'), exist_ok=True)
        os.makedirs(os.path.join(self.run_dir, 'tm'), exist_ok=True)
        namespaces = spec.get('namespaces') or {}
        experimental = namespaces.get('experimental_tm') or os.path.join(self.run_dir, 'tm')
        experimental = os.path.abspath(experimental)
        if os.path.commonpath([self.run_dir, experimental]) != self.run_dir:
            raise LedgerError('experimental TM root must live under the run directory')
        body = {
            'schema': ident.RUN_MANIFEST_SCHEMA,
            'run_id': spec['run_id'],
            'sealed': True,
            'sealed_at': spec.get('sealed_at') or _utc(),
            'source_commit': spec['source_commit'],
            'baseline_manifest_sha256': spec.get('baseline_manifest_sha256'),
            'cohort_sha256': spec['cohort_sha256'],
            'pricing_version': spec.get('pricing_version') or 'unpriced-offline',
            'n': int(spec['n']),
            'call_ceiling': int(spec.get('call_ceiling') or spec['n']),
            'cost_ceiling_usd': float(spec.get('cost_ceiling_usd') or 0),
            'schedule_window': spec.get('schedule_window'),
            'requested_model': spec['requested_model'],
            'provider': spec['provider'],
            'retry_ladder': list(spec.get('retry_ladder') or [
                'v0', 'v1-compact', 'v2-cap', 'v3-partition',
            ]),
            'acceptance': spec.get('acceptance') or {},
            'namespaces': {
                'experimental_tm': experimental,
                'canonical_tm': namespaces.get('canonical_tm') or 'canonical-tm',
                'canonical_store': namespaces.get('canonical_store') or 'canonical-store',
            },
            'schedule': list(spec.get('schedule') or []),
            'promotable': False,
        }
        hashed = dict(body)
        hashed.pop('manifest_sha256', None)
        body['manifest_sha256'] = ident.sha256_bytes(ident.canonical_bytes(hashed))
        tmp = self.manifest_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(ident.canonical_dumps(body))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, self.manifest_path)
        if not os.path.isfile(self.events_path):
            open(self.events_path, 'ab').close()
        self.manifest = body
        self._seq = 0
        self.append({
            'kind': 'seal',
            'run_id': body['run_id'],
            'request_id': None,
            'detail': {'manifest_sha256': body['manifest_sha256']},
        }, terminal=True)
        return body

    def load(self):
        if not os.path.isfile(self.manifest_path):
            raise LedgerError('run is not sealed')
        with open(self.manifest_path, encoding='utf-8') as handle:
            self.manifest = json.loads(handle.read())
        events = read_events(self.events_path)
        self._seq = events[-1]['seq'] if events else 0
        return events

    def append(self, event, terminal=False):
        with self.lock:
            usage, usage_reason = normalize_usage(
                event.get('usage'), event.get('usage_reason'))
            if usage is None:
                cost_evaluable = False
                observed = None
            else:
                cost_evaluable = bool(event.get('cost_evaluable', True))
                observed = event.get('observed_cost_usd')
            self._seq += 1
            row = {
                'schema': ident.EVENT_SCHEMA,
                'event_id': event.get('event_id') or uuid.uuid4().hex,
                'seq': self._seq,
                'kind': event['kind'],
                'run_id': event.get('run_id') or (self.manifest or {}).get('run_id'),
                'request_id': event.get('request_id'),
                'prefix_group_id': event.get('prefix_group_id'),
                'cold_warm': event.get('cold_warm'),
                'source_ordinal': event.get('source_ordinal'),
                'attempt': event.get('attempt'),
                'parent_request_id': event.get('parent_request_id'),
                'repair_variant': event.get('repair_variant'),
                'ts': event.get('ts') or _utc(),
                'transport_outcome': event.get('transport_outcome'),
                'requested_model': event.get('requested_model'),
                'served_model': event.get('served_model'),
                'usage': usage,
                'usage_reason': usage_reason,
                'pricing_table': event.get('pricing_table'),
                'pricing_version': event.get('pricing_version'),
                'cost_evaluable': cost_evaluable,
                'observed_cost_usd': observed,
                'latency_ms': event.get('latency_ms'),
                'output_termination': event.get('output_termination'),
                'audit_verdict': event.get('audit_verdict'),
                'accepted_artifact': event.get('accepted_artifact'),
                'detail': event.get('detail') or {},
            }
            line = ident.canonical_dumps(row).encode('utf-8')
            flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
            if hasattr(os, 'O_BINARY'):
                flags |= os.O_BINARY
            fd = os.open(self.events_path, flags)
            try:
                os.write(fd, line)
                if terminal or row['kind'] in TERMINAL_KINDS:
                    os.fsync(fd)
            finally:
                os.close(fd)
            return row

    def write_request(self, request):
        path = os.path.join(self.run_dir, 'requests', request['request_id'] + '.json')
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(ident.canonical_dumps(request))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        return path

    def resume_pending(self, request_ids):
        events = self.load()
        done = completed_request_ids(events)
        return [rid for rid in request_ids if rid not in done]


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        led = EventLedger(os.path.join(tmp, 'run'))
        man = led.seal({
            'run_id': 'offline-test',
            'source_commit': '0' * 40,
            'cohort_sha256': ident.sha256_bytes('cohort'),
            'n': 2,
            'requested_model': 'deepseek-v4-pro',
            'provider': 'deepseek',
            'cost_ceiling_usd': 0,
        })
        if man['promotable'] is not False:
            raise AssertionError('manifest must be non-promotable')
        rid = ident.sha256_bytes('req')
        led.append({
            'kind': 'compile', 'request_id': rid, 'usage': None,
        })
        led.append({
            'kind': 'dispatch', 'request_id': rid, 'attempt': 1,
            'usage': {'input_tokens': None, 'output_tokens': None},
        })
        term = led.append({
            'kind': 'completion', 'request_id': rid, 'attempt': 1,
            'usage': {'input_tokens': 10, 'output_tokens': 4},
            'cost_evaluable': True, 'observed_cost_usd': 0.01,
        }, terminal=True)
        if term['usage']['input_tokens'] != 10:
            raise AssertionError('present usage was dropped')
        zero = led.append({
            'kind': 'dispatch', 'request_id': ident.sha256_bytes('other'),
            'usage': {'input_tokens': 0, 'output_tokens': 0,
                      'cache_hit_tokens': 0, 'cache_miss_tokens': 0,
                      'prompt_tokens': 0, 'completion_tokens': 0},
        })
        if zero['usage'] is not None or zero['usage_reason'] != 'usage_all_zero':
            raise AssertionError('all-zero usage must be unevaluable, not zero')
        pending = led.resume_pending([rid, ident.sha256_bytes('other')])
        if rid in pending:
            raise AssertionError('completed request re-dispatched on resume')
        if ident.sha256_bytes('other') not in pending:
            raise AssertionError('open request dropped on resume')
        # Torn last line fails closed.
        with open(led.events_path, 'ab') as handle:
            handle.write(b'{"seq":')
        try:
            read_events(led.events_path)
            raise AssertionError('torn ledger was accepted')
        except LedgerError:
            pass
    print('cache_event_ledger selftest: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(selftest())
