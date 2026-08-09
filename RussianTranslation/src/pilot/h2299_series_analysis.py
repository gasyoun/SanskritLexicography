"""H2299 -- the tables behind the c4 measured-leg hang classification, recomputed.

Reads ONLY the two ledgers the gate already writes. Spends nothing, fires no call,
writes nothing. Every figure in
`pwg_ru/h2299/C4_MEASURED_LEG_KILL_CEILING_HANG_CLASSIFICATION_06-08-2026.md`
comes from this script, so a future session checks the write-up by re-running it
rather than by trusting a restated number.

    python src/pilot/h2299_series_analysis.py [--root <RussianTranslation>]

`--root` defaults to the MAIN checkout, not to this file's own tree: both ledgers
are gitignored local-only telemetry and exist only where the gate actually ran, so
running this from a worktree still reads the real series.

Model: Opus 5 1M (`claude-opus-5[1m]`) for handoff H2299.
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_ROOT = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation'


def _require(path):
    if not os.path.exists(path):
        raise SystemExit(
            'ledger not found: %s\n'
            'Both ledgers are gitignored local-only telemetry written where the gate ran.\n'
            'Pass --root <the checkout that actually ran the gate>.' % path)
    return path


def load_events(path):
    rows = []
    with open(_require(path), encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_calls(path):
    with open(_require(path), encoding='utf-8') as fh:
        return json.load(fh)


def fmt(v, width=9):
    return ('%*s' % (width, '—' if v is None else v))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default=DEFAULT_ROOT)
    args = ap.parse_args()
    out = os.path.join(args.root, 'src', 'pilot', 'output')
    events = load_events(os.path.join(out, 'h963_c4_gate0_probe_events.jsonl'))
    calls = load_calls(os.path.join(out, 'h963_c4_gate0_calls.json'))

    print('=' * 100)
    print('H2299 -- c4 gate-0 probe series: purpose x classification x duration_api_ms')
    print('=' * 100)
    print('events rows: %d   call-ledger runs: %d' % (len(events), len(calls.get('runs', {}))))
    print()

    # --- Table 1: every probe_call row, in file order -----------------------------------
    hdr = ('%-22s %-8s %-11s %10s %10s %10s %8s %-14s %s'
           % ('ts (UTC)', 'purpose', 'class', 'wall_ms', 'api_ms', 'gap_ms', 'out_B',
              'policy', 'run tail'))
    print(hdr)
    print('-' * len(hdr))
    for r in events:
        if r.get('event') != 'probe_call':
            continue
        run = r.get('run_id', '')
        tail = run.split('/')[-1] if '/' in run else '(campaign-only)'
        print('%-22s %-8s %-11s %10s %10s %10s %8s %-14s %s'
              % (r['ts'][:19].replace('T', ' '), r.get('purpose'), r.get('classification'),
                 fmt(r.get('elapsed_ms'), 10), fmt(r.get('duration_api_ms'), 10),
                 fmt(r.get('api_gap_ms'), 10), fmt(r.get('output_bytes'), 8),
                 r.get('policy'), tail))
    print()

    # --- Table 2: purpose x classification cross-tab -------------------------------------
    cross = Counter()
    purposes, classes = set(), set()
    for r in events:
        if r.get('event') != 'probe_call':
            continue
        p, c = r.get('purpose'), r.get('classification')
        cross[(p, c)] += 1
        purposes.add(p)
        classes.add(c)
    classes = sorted(classes)
    print('purpose x classification')
    print('%-10s %s  | %s' % ('', ' '.join('%10s' % c for c in classes), 'total'))
    for p in sorted(purposes):
        row = [cross[(p, c)] for c in classes]
        print('%-10s %s  | %5d' % (p, ' '.join('%10d' % n for n in row), sum(row)))
    print()

    # --- Table 3: per policy, measured-leg outcome ---------------------------------------
    print('measured-leg outcome by policy version')
    by_policy = {}
    for r in events:
        if r.get('event') != 'probe_call' or r.get('purpose') != 'measured':
            continue
        by_policy.setdefault(r.get('policy'), []).append(r)
    print('%-16s %6s %6s %6s   %s' % ('policy', 'n', 'ok', 'fail', 'failing classifications'))
    for pol in sorted(by_policy):
        rows = by_policy[pol]
        ok = sum(1 for r in rows if r.get('classification') == 'success')
        bad = [r.get('classification') for r in rows if r.get('classification') != 'success']
        print('%-16s %6d %6d %6d   %s' % (pol, len(rows), ok, len(rows) - ok,
                                          ', '.join(bad) or '-'))
    print()

    # --- Table 4: warm-up leg outcome by policy ------------------------------------------
    print('warm-up-leg outcome by policy version')
    by_policy_w = {}
    for r in events:
        if r.get('event') != 'probe_call' or r.get('purpose') != 'warmup':
            continue
        by_policy_w.setdefault(r.get('policy'), []).append(r)
    print('%-16s %6s %6s %6s   %s' % ('policy', 'n', 'ok', 'fail', 'failing classifications'))
    for pol in sorted(by_policy_w):
        rows = by_policy_w[pol]
        ok = sum(1 for r in rows if r.get('classification') == 'success')
        bad = [r.get('classification') for r in rows if r.get('classification') != 'success']
        print('%-16s %6d %6d %6d   %s' % (pol, len(rows), ok, len(rows) - ok,
                                          ', '.join(bad) or '-'))
    print()

    # --- Table 5: sitting-level pairing (does 'warm-up passes, measured fails' hold?) -----
    print('sitting-level pairing (only runs carrying a per-invocation run id)')
    sittings = {}
    order = []
    for r in events:
        if r.get('event') != 'probe_call':
            continue
        run = r.get('run_id', '')
        key = run.split('/')[-1] if '/' in run else 'campaign-only:' + r['ts'][:10]
        if key not in sittings:
            sittings[key] = {}
            order.append(key)
        sittings[key][r.get('purpose')] = r
    print('%-28s %-18s %-18s %s' % ('sitting', 'warmup', 'measured', 'verdict'))
    print('-' * 92)
    n_both, n_wpass_mfail = 0, 0
    for key in order:
        s = sittings[key]
        w, m = s.get('warmup'), s.get('measured')
        wc = w.get('classification') if w else '(absent)'
        mc = m.get('classification') if m else '(absent)'
        verdict = '-'
        if w is not None and m is not None:
            n_both += 1
            if wc == 'success' and mc != 'success':
                verdict = 'WARMUP PASS / MEASURED FAIL'
                n_wpass_mfail += 1
            elif wc == 'success' and mc == 'success':
                verdict = 'both pass'
            else:
                verdict = 'warm-up already bad'
        print('%-28s %-18s %-18s %s' % (key[:28], wc, mc, verdict))
    print()
    print('sittings with BOTH legs: %d ; of those warm-up-pass/measured-fail: %d (%.0f%%)'
          % (n_both, n_wpass_mfail, 100.0 * n_wpass_mfail / n_both if n_both else 0))
    print()

    # --- Table 6: api_gap_ms trend (candidate 3: local scaffolding overhead) --------------
    print('local scaffolding overhead (api_gap_ms = wall - duration_api_ms), chronological')
    print('%-22s %-8s %10s %10s %10s %7s' % ('ts (UTC)', 'purpose', 'wall_ms', 'api_ms',
                                             'gap_ms', 'gap/wall'))
    for r in events:
        if r.get('event') != 'probe_call' or r.get('api_gap_ms') is None:
            continue
        share = r['api_gap_ms'] / float(r['elapsed_ms']) if r.get('elapsed_ms') else 0
        print('%-22s %-8s %10d %10d %10d %6.0f%%'
              % (r['ts'][:19].replace('T', ' '), r.get('purpose'), r['elapsed_ms'],
                 r['duration_api_ms'], r['api_gap_ms'], 100 * share))
    print()

    # --- Table 7: call-ledger telemetry (candidate 2: cache/prompt-state dependence) ------
    print('call-ledger telemetry per reservation (cache state, cost, CLI duration)')
    hdr7 = ('%-26s %-16s %6s %7s %11s %13s %11s %10s %9s'
            % ('sitting', 'purpose', 'ord', 'out_tok', 'cache_read', 'cache_create',
               'subagent', 'cost_usd', 'cli_ms'))
    print(hdr7)
    print('-' * len(hdr7))
    for run_id, run in calls.get('runs', {}).items():
        tail = run_id.split('/')[-1] if '/' in run_id else run_id
        for res in run.get('reservations', []):
            t = res.get('telemetry') or {}
            print('%-26s %-16s %6s %7s %11s %13s %11s %10s %9s'
                  % (tail[:26], res.get('purpose'), res.get('ordinal'),
                     fmt(t.get('output_tokens'), 7), fmt(t.get('cache_read_tokens'), 11),
                     fmt(t.get('cache_creation_tokens'), 13),
                     fmt(t.get('subagent_tokens'), 11),
                     ('%.4f' % t['observed_cost_usd']) if t.get('observed_cost_usd') is not None else '—',
                     fmt(t.get('duration_ms'), 9)))
        u = run.get('usage') or {}
        print('%-26s %-16s %6s %7s %11s %13s %11s %10s %9s'
              % ('', '  -> run total', '', fmt(u.get('output_tokens'), 7),
                 fmt(u.get('cache_read_tokens'), 11), fmt(u.get('cache_creation_tokens'), 13),
                 fmt(u.get('subagent_tokens'), 11),
                 ('%.4f' % u['observed_cost_usd']) if u.get('observed_cost_usd') is not None else '—',
                 'evaluable=%s unev=%s' % (u.get('cost_evaluable'), u.get('unevaluable_calls'))))
    print()

    # --- Table 8: sitting spacing (candidate 1: quota/throttle) ---------------------------
    print('sitting spacing -- gap since the previous probe_call, and calls per UTC day')
    prev = None
    per_day = Counter()
    import datetime as _dt
    for r in events:
        if r.get('event') != 'probe_call':
            continue
        ts = _dt.datetime.strptime(r['ts'][:19], '%Y-%m-%dT%H:%M:%S')
        per_day[r['ts'][:10]] += 1
        gap = '' if prev is None else '%.2f h' % ((ts - prev).total_seconds() / 3600.0)
        print('%-22s %-8s %-11s  gap since prev call: %s'
              % (r['ts'][:19].replace('T', ' '), r.get('purpose'),
                 r.get('classification'), gap))
        prev = ts
    print()
    print('calls per UTC day (ration is <=2 PROBE ATTEMPTS/day, i.e. <=4 calls):')
    for day in sorted(per_day):
        flag = '   <-- over ration' if per_day[day] > 4 else ''
        print('  %s : %2d calls%s' % (day, per_day[day], flag))


if __name__ == '__main__':
    main()
