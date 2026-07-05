#!/usr/bin/env python
"""Best-effort auto-capture of live audit failures into the failure gallery.

The curated post-mortems in `failures/failures.jsonl` (ids `F1`..) carry
human-written root_cause / fix / lesson. These auto-captured records are LIVE
incidents from the kill-gate / audit: `source='auto'`, `status='open'`, id
`AUTO-<n>`, de-duplicated on `(mode, root, date)` so a recurring failure is
logged at most once per root per day and cannot flood the gallery. A human later
promotes a recurring AUTO record into a full curated post-mortem.

Writes are best-effort (never raise) — observability must not break an audit.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
# Auto-captured incidents go to a SEPARATE, git-ignored log so the curated,
# tracked post-mortems in failures/failures.jsonl stay pristine (human-authored
# only). The dashboard reads both.
FAILURES = os.path.join(REPO, 'failures', 'auto_failures.jsonl')


def _today():
    return datetime.datetime.now(datetime.timezone.utc).date().isoformat()


def _existing(path):
    """Return (set of (mode, root, date) signatures, max AUTO-<n> seen)."""
    sigs = set()
    maxn = 0
    if not os.path.exists(path):
        return sigs, maxn
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                sigs.add((r.get('mode'), r.get('root'), r.get('date')))
                rid = str(r.get('id') or '')
                if rid.startswith('AUTO-'):
                    try:
                        maxn = max(maxn, int(rid[5:]))
                    except ValueError:
                        pass
    except Exception:
        pass
    return sigs, maxn


def append_failure(mode, symptom, severity='high', root=None, data=None,
                   path=FAILURES):
    """Append one auto-captured failure incident; de-dupe on (mode, root, today).

    Returns the written record, None if de-duplicated, or None on any error.
    """
    try:
        sigs, maxn = _existing(path)
        date = _today()
        mode = mode or 'audit-failure'
        if (mode, root, date) in sigs:
            return None
        rec = {
            'id': 'AUTO-%d' % (maxn + 1),
            'date': date,
            'mode': mode,
            'severity': severity,
            'symptom': (symptom or mode)[:300],
            'root': root,
            'source': 'auto',
            'status': 'open',
            'data': data or {},
        }
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        return rec
    except Exception as e:
        print('warning: failure auto-capture failed: %s' % e, file=sys.stderr)
        return None
