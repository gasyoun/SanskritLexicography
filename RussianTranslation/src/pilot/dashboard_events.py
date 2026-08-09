#!/usr/bin/env python
"""Append-only dashboard event helpers.

Event writes are best-effort by design: operational scripts must not fail merely
because the local observability log is unavailable.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
# H1386 P3f: PWG_EVENTS_PATH lets a hermetic harness (h1339_offline_bench) redirect the
# events ledger into its sandbox -- a bench audit must never append to the LIVE
# dashboard_events.jsonl. Unset (production) resolves exactly as before.
EVENT_LOG = os.environ.get('PWG_EVENTS_PATH') or os.path.join(OUT, 'dashboard_events.jsonl')

# OPT-8 / H2229 — second paid window is already aborted by guards; these types make
# the abort visible on the public kitchen (not only console stderr).
COLLISION_EVENT_TYPES = frozenset({
    'lease_collision',
    'store_hit',
    'occupied_keys_unreadable',
    'key_overlap',
})

OPERATOR_ONE_LINER_COLLISION = (
    'If the kitchen collision banner is red (or collision_guard.blocked=true): '
    'DO NOT start a second paid window on those keys/root — a live job or recent '
    'store-hit / lease collision already holds them. Wait for the live job to '
    'finish or requeue that lease; only then import another window.'
)

_KIND_TO_TYPE = {
    'occupied_keys_overlap': 'lease_collision',
    'requeue_key_overlap': 'lease_collision',
    'nominal_keys_active': 'lease_collision',
    'occupied_keys_unreadable': 'occupied_keys_unreadable',
    'store_hit': 'store_hit',
    'key_overlap': 'key_overlap',
}


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def append_event(source, event_type, level='info', root=None, state=None,
                 summary='', data=None, log_path=EVENT_LOG):
    rec = {
        'ts': utc_now(),
        'source': source,
        'type': event_type,
        'level': level,
        'root': root,
        'state': state,
        'summary': summary or '',
        'data': data or {},
    }
    try:
        parent = os.path.dirname(os.path.abspath(log_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    except Exception as e:
        print('warning: dashboard event append failed: %s' % e, file=sys.stderr)
    return rec


def emit_collision(kind, *, root=None, summary='', data=None, source=None,
                   log_path=EVENT_LOG):
    """OPT-8 / H2229 — record a store-hit / lease-collision abort for the kitchen.

    Best-effort like append_event. Does not change spend behaviour — callers still
    SystemExit after this. Kind maps to a stable event type for kitchen_slices.
    """
    payload = dict(data or {})
    payload.setdefault('kind', kind)
    payload.setdefault('operator_one_liner', OPERATOR_ONE_LINER_COLLISION)
    etype = _KIND_TO_TYPE.get(kind, 'lease_collision')
    banner = 'DO NOT START A SECOND PAID WINDOW'
    sum_text = summary or ('%s — %s' % (banner, kind))
    if banner not in sum_text:
        sum_text = '%s — %s' % (banner, sum_text)
    return append_event(
        source or 'collision_guard', etype, level='error', root=root,
        state='blocked_second_window', summary=sum_text, data=payload,
        log_path=log_path)


def emit_stage_boundary(stage, window_tag=None, root=None, ts=None, data=None,
                        log_path=EVENT_LOG):
    """Append a stage_boundary event (H1403 A2 / H1553).

    Marks a pipeline phase edge (audit_start / audit_end today) so wall-clock
    auto-derive can later separate generation wall from operator idle. Best-effort
    like append_event — never raises into the caller.
    """
    payload = dict(data or {})
    if window_tag is not None:
        payload.setdefault('window_tag', window_tag)
    if ts is not None:
        payload.setdefault('boundary_ts', ts)
    rec = append_event(
        'audit_window', 'stage_boundary', level='info', root=root,
        state=stage, summary='stage_boundary:%s' % stage, data=payload,
        log_path=log_path)
    if ts is not None:
        rec['ts'] = ts
    return rec


def read_events(limit=100, log_path=EVENT_LOG):
    if not os.path.exists(log_path):
        return []
    out = []
    try:
        with open(log_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    out.append({'ts': None, 'source': 'dashboard_events',
                                'type': 'malformed_line', 'level': 'warn',
                                'root': None, 'state': 'malformed',
                                'summary': line[:200], 'data': {}})
    except Exception as e:
        return [{'ts': utc_now(), 'source': 'dashboard_events',
                 'type': 'read_failed', 'level': 'warn', 'root': None,
                 'state': 'unavailable', 'summary': str(e), 'data': {}}]
    return out[-limit:]
