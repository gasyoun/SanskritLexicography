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
EVENT_LOG = os.path.join(OUT, 'dashboard_events.jsonl')


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
