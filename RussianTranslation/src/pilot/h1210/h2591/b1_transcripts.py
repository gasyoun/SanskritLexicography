#!/usr/bin/env python
"""Recover what the H2591 child calls actually returned, from the CLI's own transcripts.

The driver discarded the raw wrappers, but the CLI wrote a session transcript per call
under the claude1 profile. For every rc=1 / zero-usage call this recovers the thing that
could not be inspected before: the assistant text, the stop reason, and the per-turn usage.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DIR = r'D:\ClaudeTools\profiles\claude1\.claude\projects\D--pwg-ru-cli-cwd'
RUN = (dt.datetime(2026, 8, 12, 13, 25, 0, tzinfo=dt.timezone.utc),
       dt.datetime(2026, 8, 12, 14, 27, 0, tzinfo=dt.timezone.utc))


def parse(stamp):
    try:
        return dt.datetime.fromisoformat(str(stamp).replace('Z', '+00:00'))
    except Exception:                                          # noqa: BLE001
        return None


sessions = []
for path in glob.glob(os.path.join(DIR, '*.jsonl')):
    rows = []
    with open(path, encoding='utf-8', errors='replace') as handle:
        for line in handle:
            try:
                rows.append(json.loads(line))
            except Exception:                                  # noqa: BLE001
                pass
    stamps = [parse(r.get('timestamp')) for r in rows]
    stamps = [s for s in stamps if s]
    if not stamps:
        continue
    first, last = min(stamps), max(stamps)
    if not (RUN[0] <= first <= RUN[1]):
        continue
    sessions.append((first, last, path, rows))

sessions.sort()
print('transcripts inside the H2591 run window: %d\n' % len(sessions))

for first, last, path, rows in sessions:
    texts, usages, stops, errors = [], [], [], []
    for r in rows:
        msg = r.get('message') or {}
        if r.get('type') == 'assistant':
            if msg.get('usage'):
                usages.append(msg['usage'])
            if msg.get('stop_reason'):
                stops.append(msg['stop_reason'])
            content = msg.get('content')
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        texts.append(block.get('text') or '')
            elif isinstance(content, str):
                texts.append(content)
        if r.get('isApiErrorMessage'):
            errors.append(str(msg.get('content'))[:300])

    out = sum(int(u.get('output_tokens') or 0) for u in usages)
    inp = sum(int(u.get('input_tokens') or 0) for u in usages)
    cc = sum(int(u.get('cache_creation_input_tokens') or 0) for u in usages)
    joined = ' '.join(texts).strip()

    print('%s -> %s  (%.0fs)  %s' % (first.strftime('%H:%M:%S'), last.strftime('%H:%M:%S'),
                                     (last - first).total_seconds(),
                                     os.path.basename(path)[:8]))
    print('   turns=%d assistant_usage_blocks=%d in=%d out=%d cache_create=%d'
          % (len(rows), len(usages), inp, out, cc))
    print('   stop_reasons=%s  api_error_msgs=%d' % (stops or None, len(errors)))
    if errors:
        for e in errors[:2]:
            print('   !! API ERROR: %s' % e.replace('\n', ' ')[:220])
    if joined:
        print('   text head: %s' % joined.replace('\n', ' ')[:200])
    else:
        print('   text head: <no assistant text>')
    print()
