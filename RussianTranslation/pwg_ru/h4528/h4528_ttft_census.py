#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4528_ttft_census.py — silence-bound census over COMMITTED Claude CLI result envelopes (H4528).

Why: arming the H2878 no-output-progress watchdog on the headless worker needs a window sized
from the longest silence a HEALTHY call can have on a token-streaming format. On
`--output-format stream-json --include-partial-messages` that silence is the per-request wait
for the first streamed token, which the CLI itself reports in every result envelope as
`ttft_stream_ms` (time to first streamed event) alongside `ttft_ms` (time to the first
COMPLETE message), `duration_ms` (wall) and `duration_api_ms`.

Every paid lane so far ran `--output-format json`, so no stdout-gap series exists; these
envelope fields are the only committed measurement of the quantity the window bounds.

Zero network, zero model calls: it only reads JSON files already in the tree.

Usage:
  python h4528_ttft_census.py [ROOT ...] [--json OUT]
Default ROOT: the RussianTranslation directory this file lives under.
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.dirname(os.path.dirname(HERE))
FIELDS = ('ttft_stream_ms', 'ttft_ms', 'time_to_request_ms', 'duration_ms', 'duration_api_ms',
          'num_turns')


def _objects(path):
    """Yield every JSON object in a .json (one doc) or .jsonl (one per line) file."""
    try:
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return
    if path.endswith('.jsonl'):
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('{'):
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
        return
    try:
        doc = json.loads(text)
    except ValueError:
        return
    stack = [doc]
    while stack:                                   # envelopes may be nested in a wrapper doc
        cur = stack.pop()
        if isinstance(cur, dict):
            yield cur
            stack.extend(v for v in cur.values() if isinstance(v, (dict, list)))
        elif isinstance(cur, list):
            stack.extend(v for v in cur if isinstance(v, (dict, list)))


def census(roots):
    rows, seen = [], set()
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '__pycache__')
                           and 'stenogrammy' not in d]
            for name in sorted(filenames):
                if not name.endswith(('.json', '.jsonl')):
                    continue
                path = os.path.join(dirpath, name)
                for obj in _objects(path):
                    if obj.get('type') != 'result' or 'ttft_stream_ms' not in obj:
                        continue
                    sid = obj.get('session_id') or obj.get('uuid')
                    if sid in seen:                # the same envelope copied into two files
                        continue
                    seen.add(sid)
                    row = {'file': os.path.relpath(path, RT_ROOT).replace(os.sep, '/'),
                           'subtype': obj.get('subtype'), 'is_error': obj.get('is_error')}
                    row.update({f: obj.get(f) for f in FIELDS})
                    if isinstance(row['duration_ms'], int) and isinstance(row['duration_api_ms'], int):
                        row['api_gap_ms'] = row['duration_ms'] - row['duration_api_ms']
                    rows.append(row)
    return rows


def _summ(values):
    vals = sorted(v for v in values if isinstance(v, (int, float)))
    if not vals:
        return None
    pick = lambda q: vals[min(len(vals) - 1, int(round(q * (len(vals) - 1))))]
    return {'n': len(vals), 'min': vals[0], 'p50': pick(0.5), 'p90': pick(0.9), 'max': vals[-1]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('roots', nargs='*', default=[RT_ROOT])
    ap.add_argument('--json', dest='json_out')
    args = ap.parse_args(argv)
    rows = census(args.roots)
    ok = [r for r in rows if r['subtype'] == 'success' and not r['is_error']]
    summary = {f: _summ(r.get(f) for r in ok) for f in FIELDS + ('api_gap_ms',)}
    print('envelopes with ttft_stream_ms: %d (success %d)' % (len(rows), len(ok)))
    print('%-40s %8s %8s %8s %8s %8s %5s' % ('file', 'ttft_st', 'ttft', 'wall', 'api', 'gap', 'turn'))
    for r in sorted(rows, key=lambda r: -(r.get('ttft_stream_ms') or 0)):
        print('%-40s %8s %8s %8s %8s %8s %5s' % (
            r['file'][-40:], r.get('ttft_stream_ms'), r.get('ttft_ms'), r.get('duration_ms'),
            r.get('duration_api_ms'), r.get('api_gap_ms'), r.get('num_turns')))
    print(json.dumps(summary, indent=1))
    if args.json_out:
        with open(args.json_out, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'rows': rows, 'success_summary': summary}, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
