#!/usr/bin/env python
r"""30-minute weekly review packet (H2175 step 12, ruling R4.4).

Renders telemetry/weekly_packet_<ISO-week>.md from the durable ledgers:
per-lane throughput / cost / defect table, parked items awaiting a ruling,
experiment verdicts (E1-E3, when their verdict.json files exist), and the STAGED
DECISIONS DUE — auto-promote trial renewal (contract §5: authority expires 7 days
after first use) and the week-1 account-map judgment (R3.1).

Pure ledger read; no model calls, no store reads.
"""
import argparse
import glob
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

import data_root as dr          # noqa: E402
import parked_queue             # noqa: E402


def iso_week(ts):
    t = time.gmtime(ts)
    y, w, _ = time.strftime('%G %V %u', t).split()
    return '%s-W%s' % (y, w)


def week_rows(telemetry_dir, week):
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
                if rec.get('week') == week:
                    rows.append(rec)
        if rows:
            lanes[lane] = rows
    return lanes


def week_defects(telemetry_dir, week):
    """sev-3/total defects from the week's spotcheck_*.json reports."""
    sev3 = total = 0
    for path in sorted(glob.glob(os.path.join(telemetry_dir, 'spotcheck_*.json'))):
        try:
            rep = json.load(open(path, encoding='utf-8'))
        except (OSError, ValueError):
            continue
        ts = rep.get('generated_at') or 0
        if iso_week(ts) != week:
            continue
        total += len(rep.get('defects') or [])
        sev3 += rep.get('sev3_count') or 0
    return sev3, total


def first_auto_promotion(manifests_dir):
    """Epoch of the FIRST pwg.auto_promotion.v1 record anywhere — the trial clock
    (contract §5: authority expires 7 days after first use)."""
    first = None
    for path in glob.glob(os.path.join(manifests_dir, '**', '*.PROMOTED.json'),
                          recursive=True):
        try:
            rec = json.load(open(path, encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if rec.get('schema') != 'pwg.auto_promotion.v1':
            continue
        ts = rec.get('promoted_at')
        if ts and (first is None or ts < first):
            first = ts
    return first


def experiment_verdicts(root):
    out = []
    for path in sorted(glob.glob(os.path.join(root, 'experiments', '*', 'verdict.json'))):
        name = os.path.basename(os.path.dirname(path))
        try:
            v = json.load(open(path, encoding='utf-8'))
            out.append('%s: %s' % (name, v.get('verdict') or json.dumps(v)[:120]))
        except (OSError, ValueError):
            out.append('%s: UNREADABLE verdict.json' % name)
    return out


def build_packet(root, week, now=None):
    now = now or time.time()
    telemetry = dr.resolve(root, 'telemetry_dir')
    lanes = week_rows(telemetry, week)
    sev3, defects = week_defects(telemetry, week)
    parked = parked_queue.list_parked(env={'PWG_PARKED_DIR':
                                           dr.resolve(root, 'parked_dir')})
    first_promo = first_auto_promotion(dr.resolve(root, 'manifests_dir'))

    lines = ['# Nonstop lanes — weekly packet %s' % week, '',
             '| lane | ticks | windows | failed | skips | cost USD |',
             '|---|---|---|---|---|---|']
    for lane, rows in sorted(lanes.items()):
        windows = sum(1 for r in rows if r.get('verdict') == 'window')
        failed = sum(1 for r in rows if r.get('verdict') == 'window_failed')
        skips = sum(1 for r in rows if r.get('verdict') == 'skip')
        cost = sum(float(r.get('window_cost_usd') or 0) for r in rows)
        lines.append('| %s | %d | %d | %d | %d | %.2f |'
                     % (lane, len(rows), windows, failed, skips, cost))
    if not lanes:
        lines.append('| _no lane ticked this week_ | | | | | |')
    lines += ['', '## Defects (spot-checks this week)',
              '- sev-3: %d · all severities: %d' % (sev3, defects), '',
              '## Parked items awaiting a ruling (%d)' % len(parked)]
    for r in parked[:20]:
        lines.append('- `%s` — %s (%s)' % (r.get('key'), r.get('reason'),
                                           r.get('date')))
    if len(parked) > 20:
        lines.append('- … +%d more' % (len(parked) - 20))
    lines += ['', '## Experiment verdicts']
    verdicts = experiment_verdicts(root)
    lines += ['- ' + v for v in verdicts] or []
    if not verdicts:
        lines.append('- none yet (E1 staged behind the Wave-0 key; E2/E3 wave 3)')
    lines += ['', '## Staged decisions DUE']
    if first_promo:
        expiry = first_promo + 7 * 86400
        status = ('EXPIRED %s — auto-promote is OFF until explicitly renewed'
                  % time.strftime('%Y-%m-%d', time.gmtime(expiry))
                  if now > expiry else
                  'expires %s' % time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(expiry)))
        lines.append('- **Auto-promote trial renewal (contract §5):** first use %s; %s. '
                     'Renew / stage down to auto-launch-only / return to human review.'
                     % (time.strftime('%Y-%m-%d', time.gmtime(first_promo)), status))
    else:
        lines.append('- Auto-promote trial: not started yet (no auto-promotion on record).')
    lines.append('- **Account map (R3.1):** judge the 1 PC + 1 prod + 1 routines + 1 '
                 'interactive split against this week\'s numbers — possibly 3 '
                 'production accounts on the prod box.')
    lines.append('')
    lines.append('_Generated %s UTC by weekly_packet.py (H2175 R4.4)._'
                 % time.strftime('%Y-%m-%d %H:%M', time.gmtime(now)))
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-root')
    ap.add_argument('--week', default=iso_week(time.time()),
                    help='ISO week, e.g. 2026-W32 (default: current)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.data_root:
        ap.error('--data-root is required')
    text = build_packet(args.data_root, args.week)
    out = os.path.join(dr.resolve(args.data_root, 'telemetry_dir'),
                       'weekly_packet_%s.md' % args.week)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('weekly packet -> %s' % out)
    return 0


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for sub in dr.SUBDIRS:
            os.makedirs(os.path.join(td, sub), exist_ok=True)
        now = int(time.time())
        week = iso_week(now)
        with open(os.path.join(td, 'telemetry', 'scheduler_ticks_prod.jsonl'), 'w',
                  encoding='utf-8', newline='\n') as f:
            f.write(json.dumps({'week': week, 'verdict': 'window',
                                'window_cost_usd': 3.0}) + '\n')
            f.write(json.dumps({'week': '2026-W01', 'verdict': 'window',
                                'window_cost_usd': 50.0}) + '\n')
        with open(os.path.join(td, 'telemetry', 'spotcheck_x.json'), 'w',
                  encoding='utf-8', newline='\n') as f:
            json.dump({'generated_at': now, 'sev3_count': 1,
                       'defects': [{'severity': 3}, {'severity': 1}]}, f)
        # auto-promotion record 8 days old -> trial EXPIRED must be flagged
        os.makedirs(os.path.join(td, 'manifests', 'w'), exist_ok=True)
        with open(os.path.join(td, 'manifests', 'w', 'x.PROMOTED.json'), 'w',
                  encoding='utf-8', newline='\n') as f:
            json.dump({'schema': 'pwg.auto_promotion.v1',
                       'promoted_at': now - 8 * 86400}, f)
        os.makedirs(os.path.join(td, 'experiments', 'E1_deepseek_vs_c4'),
                    exist_ok=True)
        with open(os.path.join(td, 'experiments', 'E1_deepseek_vs_c4',
                               'verdict.json'), 'w', encoding='utf-8') as f:
            json.dump({'verdict': 'pending — sample frozen'}, f)
        parked_queue.park('odd~~2', 'no classification', 'selftest',
                          env={'PWG_PARKED_DIR': os.path.join(td, 'parked')})
        text = build_packet(td, week, now=now)
        assert '| prod | 1 | 1 | 0 | 0 | 3.00 |' in text, text
        assert '50.0' not in text, 'other weeks leaked in'
        assert 'sev-3: 1' in text
        assert 'odd~~2' in text
        assert 'E1_deepseek_vs_c4: pending' in text
        assert 'EXPIRED' in text, 'an 8-day-old trial must read as expired'
    print('weekly_packet selftest: PASS (week scoping, lane table, defects, parked, '
          'experiment verdicts, trial-expiry decision row)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
