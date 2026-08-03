#!/usr/bin/env python
"""Park-and-skip queue (H2175 step 8, autonomy contract R4.2).

An automated lane that meets an UNCLASSIFIABLE item must never improvise a
classification and never block the whole lane on one item: it parks the item —
one JSON file per item under the parked/ dir with a one-line reason — and
continues with the remaining work. Parked items surface in the weekly review
packet (weekly_packet.py); a human (or a directed session) rules on them there.

Resolution of the parked dir: $PWG_PARKED_DIR (set by data_root.py to
<data-root>/parked) -> local src/pilot/parked/ fallback. Enabling the SEAMS that
call park() is a separate, deliberate act: gen_opt_harness2.py parks instead of
dying only when $PWG_PARK_AND_SKIP=1 — the historical fail-loud behavior stays
the default for every human-driven invocation.
"""
import json
import os
import re
import sys
import time

# Imported by pipeline code (gen_opt_harness2.build under perf_preflight's captured
# stdout): a StringIO has no reconfigure — guard, don't crash the importer.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

SCHEMA = 'pwg.parked_item.v1'

# the opt-in switch for park-instead-of-die seams (scheduler lanes set this)
ENABLE_VAR = 'PWG_PARK_AND_SKIP'


def enabled(env=None):
    return (env if env is not None else os.environ).get(ENABLE_VAR) == '1'


def parked_dir(env=None):
    env = env if env is not None else os.environ
    return env.get('PWG_PARKED_DIR') or os.path.join(HERE, 'parked')


def _safe(fragment):
    """Filesystem-safe filename fragment (SLP1 keys carry / and case; Windows-safe)."""
    return re.sub(r'[^A-Za-z0-9._-]', '_', fragment)[:80] or 'item'


def park(key, reason, source, lane=None, extra=None, env=None):
    """Write one parked-item record; return its path. Never raises on a duplicate —
    a re-parked key the same day appends a numeric suffix rather than overwriting
    the earlier evidence."""
    d = parked_dir(env)
    os.makedirs(d, exist_ok=True)
    day = time.strftime('%Y-%m-%d', time.gmtime())
    base = '%s_%s' % (day, _safe(str(key)))
    path = os.path.join(d, base + '.json')
    n = 1
    while os.path.exists(path):
        n += 1
        path = os.path.join(d, '%s.%d.json' % (base, n))
    record = {'schema': SCHEMA, 'parked_at': int(time.time()), 'date': day,
              'key': str(key), 'reason': str(reason).strip().splitlines()[0],
              'source': source, 'lane': lane or os.environ.get('PWG_LANE') or None}
    if extra:
        record['extra'] = extra
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(record, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, path)
    return path


def list_parked(env=None, since_epoch=None):
    """All parked records (optionally only those parked at/after since_epoch),
    oldest first. Unreadable files are reported as parse-error stubs, not dropped."""
    d = parked_dir(env)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if not name.endswith('.json'):
            continue
        p = os.path.join(d, name)
        try:
            rec = json.load(open(p, encoding='utf-8'))
        except (OSError, ValueError) as exc:
            rec = {'schema': SCHEMA, 'key': name, 'reason': 'UNREADABLE parked record: %s' % exc,
                   'source': 'parked_queue.list_parked', 'parked_at': None}
        rec['_path'] = p
        if since_epoch is not None and (rec.get('parked_at') or 0) < since_epoch:
            continue
        out.append(rec)
    return out


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        env = {'PWG_PARKED_DIR': d}
        # 1. a parked item lands as one JSON with a one-line reason
        p1 = park('aMSa/2', 'portrait missing\nsecond line ignored', 'selftest', env=env)
        rec = json.load(open(p1, encoding='utf-8'))
        assert rec['schema'] == SCHEMA and rec['key'] == 'aMSa/2'
        assert rec['reason'] == 'portrait missing', rec['reason']
        assert '\n' not in rec['reason']
        # 2. re-parking the same key the same day keeps BOTH records
        p2 = park('aMSa/2', 'still missing', 'selftest', env=env)
        assert p1 != p2 and os.path.exists(p1) and os.path.exists(p2)
        # 3. filenames are date-prefixed and filesystem-safe (no / from SLP1 keys)
        assert os.path.basename(p1).split('_')[0].count('-') == 2
        assert '/' not in os.path.basename(p1).replace('\\', '')
        # 4. list_parked returns oldest-first, tolerates junk
        with open(os.path.join(d, '2020-01-01_junk.json'), 'w', encoding='utf-8') as f:
            f.write('{not json')
        rows = list_parked(env=env)
        assert len(rows) == 3, rows
        assert any('UNREADABLE' in r['reason'] for r in rows)
        # 5. enabled() reads the opt-in switch, default off
        assert not enabled(env={})
        assert enabled(env={ENABLE_VAR: '1'})
    print('parked_queue selftest: PASS (one-line reason, no-overwrite dedupe, safe names, '
          'junk-tolerant listing, default-off switch)')
    return True


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--list', action='store_true', help='print parked records as JSON lines')
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.list:
        for rec in list_parked():
            print(json.dumps(rec, ensure_ascii=False))
    else:
        ap.print_help()
