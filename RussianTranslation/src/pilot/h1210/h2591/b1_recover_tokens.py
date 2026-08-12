#!/usr/bin/env python
"""Recover the TRUE per-call token totals from the CLI transcripts and re-run the compare.

The H2591 result envelopes under-reported: two calls that really spent 14 322 and 11 594
output tokens reported all zeros. The CLI's own transcripts are a second, independent
record of the same calls, so the token axis the receipt had to void can be rebuilt from
them — and the arms re-compared on evidence that exists.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

TDIR = r'D:\ClaudeTools\profiles\claude1\.claude\projects\D--pwg-ru-cli-cwd'
BASE = (r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation'
        r'\src\pilot\h1210\h2591')
FIELDS = ('input_tokens', 'output_tokens', 'cache_creation_input_tokens',
          'cache_read_input_tokens')


def parse(stamp):
    try:
        return dt.datetime.fromisoformat(str(stamp).replace('Z', '+00:00'))
    except Exception:                                          # noqa: BLE001
        return None


# --- transcripts -> (start, totals, api_errors) ------------------------------------
sessions = []
for path in glob.glob(os.path.join(TDIR, '*.jsonl')):
    stamps, totals, errs = [], {f: 0 for f in FIELDS}, []
    with open(path, encoding='utf-8', errors='replace') as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except Exception:                                  # noqa: BLE001
                continue
            when = parse(row.get('timestamp'))
            if when:
                stamps.append(when)
            msg = row.get('message') or {}
            if row.get('type') == 'assistant' and isinstance(msg.get('usage'), dict):
                for f in FIELDS:
                    totals[f] += int(msg['usage'].get(f) or 0)
            if row.get('isApiErrorMessage'):
                text = json.dumps(msg.get('content'), ensure_ascii=False)
                errs.append('529 Overloaded' if '529' in text else
                            'stream_stopped' if 'stopped arriving' in text else
                            'connection_lost' if 'Connection lost' in text else 'other')
    if stamps:
        sessions.append({'start': min(stamps), 'totals': totals, 'errors': errs,
                         'file': os.path.basename(path)[:8]})

# --- envelopes + ledger reservation times ------------------------------------------
ledger = json.load(open(os.path.join(BASE, 'call_reservation.json'), encoding='utf-8'))
res = {r['ordinal']: r for r in ledger['runs']['h2591']['reservations']}
env = {}
for p in glob.glob(os.path.join(BASE, 'envelopes', '*.json')):
    e = json.load(open(p, encoding='utf-8'))
    env[e['ordinal']] = e

used = set()
print('%-4s %-3s %-10s %-4s %10s %10s  %-18s %s'
      % ('ord', 'arm', 'key', 'rc', 'env_out', 'real_out', 'api_error', 'src'))
recovered = {}
for ordinal in sorted(env):
    e, r = env[ordinal], res[ordinal]
    reserved = dt.datetime.fromtimestamp(r['reserved_at_ns'] / 1e9, dt.timezone.utc)
    best = min((s for s in sessions if s['file'] not in used),
               key=lambda s: abs((s['start'] - reserved).total_seconds()), default=None)
    if best is None or abs((best['start'] - reserved).total_seconds()) > 90:
        print('%-4d ?? no transcript within 90 s' % ordinal)
        continue
    used.add(best['file'])
    recovered[ordinal] = best['totals']
    print('%-4d %-3s %-10s %-4s %10d %10d  %-18s %s'
          % (ordinal, e['arm'], e['key1'], str(e.get('returncode')),
             int((e['telemetry'] or {}).get('output_tokens') or 0),
             best['totals']['output_tokens'],
             ','.join(sorted(set(best['errors']))) or '-', best['file']))


def totals(arm, key):
    return sum(recovered[o][key] for o in recovered if env[o]['arm'] == arm)


print('\n--- token totals: ENVELOPE (what the receipt used) vs TRANSCRIPT (truth) ---')
for arm in ('A', 'B'):
    env_out = sum(int((env[o]['telemetry'] or {}).get('output_tokens') or 0)
                  for o in env if env[o]['arm'] == arm)
    env_in = sum(int((env[o]['telemetry'] or {}).get('input_tokens') or 0)
                 for o in env if env[o]['arm'] == arm)
    print('arm %s  envelope non-cache=%7d   transcript non-cache=%7d   '
          'transcript cache_create=%8d'
          % (arm, env_in + env_out,
             totals(arm, 'input_tokens') + totals(arm, 'output_tokens'),
             totals(arm, 'cache_creation_input_tokens')))

a = totals('A', 'input_tokens') + totals('A', 'output_tokens')
b = totals('B', 'input_tokens') + totals('B', 'output_tokens')
print('\nPREP non-cache token gain (transcript truth): %+.1f%%' % ((a - b) / a * 100))

print('\n--- like-for-like: only the 4 cards BOTH arms returned schema for ---')
pairs = {}
for o in env:
    pairs.setdefault(env[o]['key1'], {})[env[o]['arm']] = o
ta = tb = 0
for key, arms in pairs.items():
    if len(arms) != 2:
        continue
    oa, ob = arms['A'], arms['B']
    if env[oa].get('failure_class') or env[ob].get('failure_class'):
        continue
    va = recovered[oa]['input_tokens'] + recovered[oa]['output_tokens']
    vb = recovered[ob]['input_tokens'] + recovered[ob]['output_tokens']
    ta += va
    tb += vb
    print('  %-10s A %6d   B %6d   delta %+6d' % (key, va, vb, vb - va))
print('  TOTAL      A %6d   B %6d' % (ta, tb))
if ta:
    print('  paired PREP token gain: %+.1f%%' % ((ta - tb) / ta * 100))
