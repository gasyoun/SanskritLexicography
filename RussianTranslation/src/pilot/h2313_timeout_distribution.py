#!/usr/bin/env python
"""H2313: wall-clock distribution reader over every committed pwg_ru card-phase spawn.

Reads every ``*_card_rows.json`` under ``pwg_ru/h2189``, ``pwg_ru/h2250``, and
``pwg_ru/h2251`` (the only card-phase batches on disk that carry a harness-measured
``wall_ms`` per spawn) and prints one table: completed spawns as durations, killed
spawns marked censored (the harness's own kill ceiling for that batch, not a duration).
No probes issued -- this is a reader over already-committed envelopes, per H2313's
"do not generate a fresh distribution from scratch when a committed one exists."
"""
import glob
import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PWG_RU = os.path.join(ROOT, 'pwg_ru')


def find_rows_files():
    pattern = os.path.join(PWG_RU, '*', 'raw*', '**', '*_card_rows.json')
    files = glob.glob(pattern, recursive=True)
    pattern2 = os.path.join(PWG_RU, '*', 'raw*', '*_card_rows.json')
    files += glob.glob(pattern2)
    return sorted(set(files))


def load_spawns():
    spawns = []
    for path in find_rows_files():
        rel = os.path.relpath(path, PWG_RU)
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        for row in data.get('rows', []):
            spawns.append({
                'batch': rel,
                'key': row.get('key'),
                'wall_ms': row.get('wall_ms'),
                'failure_class': row.get('failure_class'),
                'num_turns': row.get('num_turns'),
                'schema_compliant': row.get('schema_compliant'),
            })
    return spawns


def percentile(values, pct):
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def main():
    spawns = load_spawns()
    completed = [sp for sp in spawns if sp['failure_class'] != 'timeout']
    censored = [sp for sp in spawns if sp['failure_class'] == 'timeout']

    print('| batch | key | wall_ms | status |')
    print('|---|---|--:|---|')
    for sp in sorted(spawns, key=lambda r: r['wall_ms']):
        status = 'CENSORED (killed)' if sp['failure_class'] == 'timeout' else 'completed'
        print('| %s | %s | %d | %s |' % (sp['batch'], sp['key'], sp['wall_ms'], status))

    print()
    print('n completed = %d, n censored (killed) = %d, n total = %d' %
          (len(completed), len(censored), len(spawns)))
    vals = [sp['wall_ms'] for sp in completed]
    print('completed wall_ms: min=%d max=%d p50=%d p90=%d p95=%d p99=%d' % (
        min(vals), max(vals), percentile(vals, 50), percentile(vals, 90),
        percentile(vals, 95), percentile(vals, 99)))
    print('censored wall_ms (kill ceilings hit, NOT durations): %s' %
          sorted(sp['wall_ms'] for sp in censored))


if __name__ == '__main__':
    sys.exit(main())
