#!/usr/bin/env python
r"""5-minute daily digest of the nonstop lanes (H2175 step 12, ruling R4.4).

Reads ONLY the durable ledgers in a pwg-ru-data checkout — scheduler tick ledgers,
the day's spot-check report, lane freeze/pause files, parked items, auto-promotion
records — and renders telemetry/digest_<date>.md. Optionally pings a GitHub issue
(--issue/--repo, via gh) so the human loop is one notification, not a hunt.

No model calls, no store reads beyond the ledgers: the digest must stay cheap
enough to run unconditionally from every lane's timer.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

import data_root as dr        # noqa: E402
import parked_queue           # noqa: E402
import spot_check_daily as scd  # noqa: E402


def utc_date(ts):
    return time.strftime('%Y-%m-%d', time.gmtime(ts))


def day_ticks(telemetry_dir, date):
    """lane -> that day's tick records, from scheduler_ticks_<lane>.jsonl."""
    lanes = {}
    for path in sorted(glob.glob(os.path.join(telemetry_dir, 'scheduler_ticks_*.jsonl'))):
        lane = os.path.basename(path)[len('scheduler_ticks_'):-len('.jsonl')]
        rows = []
        with open(path, encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if utc_date(rec.get('ts') or 0) == date:
                    rows.append(rec)
        if rows:
            lanes[lane] = rows
    return lanes


def lane_summary(rows):
    windows = [r for r in rows if r.get('verdict') == 'window']
    failed = [r for r in rows if r.get('verdict') == 'window_failed']
    skips = {}
    for r in rows:
        if r.get('verdict') == 'skip':
            skips[r.get('reason') or '?'] = skips.get(r.get('reason') or '?', 0) + 1
    cost = sum(float(r.get('window_cost_usd') or 0) for r in rows)
    explained = len(windows) + len(failed) + sum(skips.values())
    return {'ticks': len(rows), 'windows': len(windows), 'failed': len(failed),
            'skips': skips, 'cost_usd': round(cost, 4),
            'unexplained': len(rows) - explained}


def build_digest(root, date):
    telemetry = dr.resolve(root, 'telemetry_dir')
    gatelogs = dr.resolve(root, 'gatelogs_dir')
    lanes = day_ticks(telemetry, date)
    spot = None
    spot_path = os.path.join(telemetry, 'spotcheck_%s.json' % date)
    if os.path.exists(spot_path):
        spot = json.load(open(spot_path, encoding='utf-8'))
    freezes = sorted(os.path.basename(p) for p in
                     glob.glob(os.path.join(gatelogs, 'lane_freeze_*.json')))
    pauses = sorted(os.path.basename(p) for p in
                    glob.glob(os.path.join(gatelogs, 'lane_pause_*.json')))
    day_start = time.mktime(time.strptime(date, '%Y-%m-%d')) - time.timezone
    parked_today = [r for r in parked_queue.list_parked(
        env={'PWG_PARKED_DIR': dr.resolve(root, 'parked_dir')})
        if r.get('date') == date]
    promoted = scd.day_promotion_records(dr.resolve(root, 'manifests_dir'), date)

    lines = ['# Nonstop lanes — daily digest %s' % date, '']
    if not lanes:
        lines.append('**No lane ticked today.** If lanes were expected, the timers '
                     'are the first suspect (this line IS the alarm).')
    for lane, rows in sorted(lanes.items()):
        s = lane_summary(rows)
        lines.append('## Lane `%s` — %d ticks, %d windows, $%.2f' %
                     (lane, s['ticks'], s['windows'], s['cost_usd']))
        if s['failed']:
            lines.append('- ⚠ %d failed windows' % s['failed'])
        for reason, n in sorted(s['skips'].items()):
            lines.append('- skip ×%d: %s' % (n, reason))
        if s['unexplained']:
            lines.append('- 🔴 %d UNEXPLAINED tick records (bug: every branch must '
                         'record a reason)' % s['unexplained'])
        lines.append('')
    lines.append('## Controls')
    lines.append('- auto-promotions today: %d' % len(promoted))
    if spot:
        lines.append('- spot-check: sampled %d/%d, sev-3 defects %d, SAN-LOSS in '
                     'store: %s' % (len(spot.get('sampled') or []),
                                    spot.get('population') or 0,
                                    spot.get('sev3_count') or 0,
                                    spot.get('san_loss_in_store')))
    else:
        lines.append('- spot-check: **MISSING for %s** (INCONCLUSIVE, not clean)' % date)
    lines.append('- freezes: %s' % (', '.join(freezes) or 'none'))
    lines.append('- pauses: %s' % (', '.join(pauses) or 'none'))
    lines.append('- parked today: %d%s' % (len(parked_today),
                 (' — ' + '; '.join('%s (%s)' % (r.get('key'), r.get('reason'))
                                    for r in parked_today[:5])) if parked_today else ''))
    lines.append('')
    lines.append('_Generated %s UTC by digest_daily.py (H2175 R4.4)._'
                 % time.strftime('%H:%M', time.gmtime()))
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-root')
    ap.add_argument('--date', default=utc_date(time.time()))
    ap.add_argument('--issue', type=int, default=None,
                    help='GitHub issue number to comment the digest on (gh CLI)')
    ap.add_argument('--repo', default='gasyoun/pwg-ru-data')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.data_root:
        ap.error('--data-root is required')
    text = build_digest(args.data_root, args.date)
    out = os.path.join(dr.resolve(args.data_root, 'telemetry_dir'),
                       'digest_%s.md' % args.date)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('digest -> %s' % out)
    if args.issue:
        proc = subprocess.run(['gh', 'issue', 'comment', str(args.issue),
                               '--repo', args.repo, '--body-file', out],
                              capture_output=True, text=True, encoding='utf-8')
        print('issue ping: %s' % ('ok' if proc.returncode == 0
                                  else (proc.stderr or '')[-200:]))
    return 0


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for sub in dr.SUBDIRS:
            os.makedirs(os.path.join(td, sub), exist_ok=True)
        tdir = os.path.join(td, 'telemetry')
        now = int(time.time())
        date = utc_date(now)
        with open(os.path.join(tdir, 'scheduler_ticks_pc.jsonl'), 'w',
                  encoding='utf-8', newline='\n') as f:
            f.write(json.dumps({'ts': now, 'verdict': 'window',
                                'window_cost_usd': 2.5}) + '\n')
            f.write(json.dumps({'ts': now, 'verdict': 'skip',
                                'reason': 'live_gate_no_go_all_roster'}) + '\n')
            f.write(json.dumps({'ts': now - 86400 * 3, 'verdict': 'window',
                                'window_cost_usd': 9.9}) + '\n')   # old, excluded
        with open(os.path.join(tdir, 'spotcheck_%s.json' % date), 'w',
                  encoding='utf-8', newline='\n') as f:
            json.dump({'sampled': ['a'], 'population': 10, 'sev3_count': 1,
                       'san_loss_in_store': False}, f)
        parked_queue.park('weird~~1', 'unclassifiable', 'selftest',
                          env={'PWG_PARKED_DIR': os.path.join(td, 'parked')})
        text = build_digest(td, date)
        assert 'Lane `pc` — 2 ticks, 1 windows, $2.50' in text, text
        assert 'skip ×1: live_gate_no_go_all_roster' in text
        assert 'sev-3 defects 1' in text
        assert 'parked today: 1' in text and 'weird~~1' in text
        assert '$9.9' not in text, 'old ticks leaked into the day digest'
        # missing spot-check is called out as INCONCLUSIVE, never silently clean
        os.remove(os.path.join(tdir, 'spotcheck_%s.json' % date))
        text2 = build_digest(td, date)
        assert 'MISSING for %s' % date in text2
    print('digest_daily selftest: PASS (day scoping, lane summary, spot-check '
          'inconclusive-when-missing, parked surfacing)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
