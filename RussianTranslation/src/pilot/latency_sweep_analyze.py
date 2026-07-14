#!/usr/bin/env python3
"""Analyze the exact-model latency probe JSONL.

Default (legacy) view: per-size stats, input-bytes vs latency correlation + OLS
slope, and the >30000 ms ceiling-breach rate over ALL measured calls.

``--decision-rule`` view (sol.md #1/#3): group MEASURED calls by route+window and
evaluate, as two SEPARATE conclusions:
  * Foreign operational readiness -- foreign independently satisfies the latency
    rule: per window median <= ceiling AND breaches <= 1/5 (rate <= 0.20), n>=5;
    aggregate across >=2 foreign windows breaches/total <= 0.10.
  * Route causality -- foreign is consistently materially faster than the paired
    home window (foreign median <= --causality-ratio x home median in every
    paired window).
Warm-up rows (``warmup=true``) are excluded from every statistic. Diagnostic PASS
is NOT a production GO.
"""
import argparse
import json
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')

CEILING = 30000


def load(paths, include_warmups=False):
    rows = []
    for p in paths:
        try:
            with open(p, encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line.startswith('{'):
                        continue
                    r = json.loads(line)
                    if r.get('warmup') and not include_warmups:
                        continue                       # exclude warm-ups (sol.md #5)
                    rows.append(r)
        except FileNotFoundError:
            pass
    return rows


def _bytes(r):
    return r.get('total_input_bytes', r.get('actual_prompt_bytes'))


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return float('nan')
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return num / (dx * dy) if dx and dy else float('nan')


def ols(xs, ys):
    n = len(xs)
    if n < 2:
        return float('nan'), float('nan'), float('nan')
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx if sxx else float('nan')
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot else float('nan')
    return slope, intercept, r2


def legacy_report(rows):
    rows.sort(key=lambda r: r['ts_utc'])
    print('N measured calls = %d   window %s .. %s' %
          (len(rows), rows[0]['ts_utc'], rows[-1]['ts_utc']))
    by = {}
    for r in rows:
        by.setdefault(_bytes(r), []).append(r)
    print('\nper input-size band (measured calls; latency_ms):')
    print('%8s %3s %7s %7s %7s %7s %7s  %s' %
          ('bytes', 'n', 'min', 'median', 'mean', 'max', 'stdev', 'classes'))
    for tib in sorted(by):
        lat = [r['latency_ms'] for r in by[tib]]
        cls = {}
        for r in by[tib]:
            cls[r['classification']] = cls.get(r['classification'], 0) + 1
        sd = int(st.pstdev(lat)) if len(lat) > 1 else 0
        print('%8s %3d %7d %7d %7d %7d %7d  %s' %
              (tib, len(lat), min(lat), int(st.median(lat)), int(st.mean(lat)),
               max(lat), sd, cls))
    xs = [_bytes(r) for r in rows]
    ys = [r['latency_ms'] for r in rows]
    r = pearson(xs, ys)
    slope, intercept, r2 = ols(xs, ys)
    over = [x for x in rows if x['latency_ms'] > CEILING]
    allv = sorted(ys)

    def pct(p):
        return int(allv[int((len(allv) - 1) * p)])
    print('\noverall (all %d calls): min=%d  p50=%d  p90=%d  max=%d  mean=%d  stdev=%d'
          % (len(ys), min(ys), pct(0.5), pct(0.9), max(ys), int(st.mean(ys)), int(st.pstdev(ys))))
    print('input-bytes vs latency:  Pearson r=%.3f   OLS slope=%.3f ms/byte   R^2=%.3f'
          % (r, slope, r2))
    print('ceiling breach (>%d ms): %d/%d = %.0f%% of calls'
          % (CEILING, len(over), len(rows), 100 * len(over) / len(rows)))


def _group(rows):
    g = {}
    for r in rows:
        g.setdefault((r.get('route', '?'), r.get('window', '?')), []).append(r)
    return g


def decision_report(rows, ceiling, foreign_route, home_route, causality_ratio):
    g = _group(rows)
    routes = sorted({k[0] for k in g})
    print('=== per route x window (measured, warm-ups excluded) ===')
    print('%-16s %-6s %4s %9s %9s %s' % ('route', 'window', 'n', 'median', 'breach', 'verdict'))
    stats = {}   # (route,window) -> dict
    for (route, window) in sorted(g):
        rs = g[(route, window)]
        lat = [r['latency_ms'] for r in rs]
        med = int(st.median(lat))
        breach = sum(1 for v in lat if v > ceiling)
        n = len(rs)
        win_pass = (n >= 5) and (med <= ceiling) and (breach / n <= 0.20)
        stats[(route, window)] = dict(n=n, median=med, breach=breach, rate=breach / n, win_pass=win_pass)
        note = 'PASS' if win_pass else ('n<5' if n < 5 else 'FAIL')
        print('%-16s %-6s %4d %9d %6d/%d  %s' % (route, window, n, med, breach, n, note))

    # (A) Foreign operational readiness -- foreign alone satisfies the rule
    fwins = sorted(w for (r, w) in stats if r == foreign_route)
    print('\n=== (A) FOREIGN OPERATIONAL READINESS (foreign satisfies the latency rule) ===')
    if not fwins:
        print('  no foreign-route (%r) windows found -- cannot evaluate.' % foreign_route)
        readiness = None
    else:
        tot = sum(stats[(foreign_route, w)]['n'] for w in fwins)
        tot_breach = sum(stats[(foreign_route, w)]['breach'] for w in fwins)
        agg = tot_breach / tot if tot else 1.0
        all_win_pass = all(stats[(foreign_route, w)]['win_pass'] for w in fwins)
        enough = len(fwins) >= 2
        readiness = all_win_pass and enough and agg <= 0.10
        for w in fwins:
            s = stats[(foreign_route, w)]
            print('  window %s: n=%d median=%d ms breach=%d/%d (%.0f%%) -> %s'
                  % (w, s['n'], s['median'], s['breach'], s['n'], 100 * s['rate'],
                     'ok' if s['win_pass'] else 'fail'))
        print('  aggregate: %d/%d breaches = %.1f%% (need <=10%%); windows=%d (need >=2); every-window-pass=%s'
              % (tot_breach, tot, 100 * agg, len(fwins), all_win_pass))
        print('  --> FOREIGN READINESS: %s' % ('PASS (diagnostic)' if readiness else 'FAIL'))

    # (B) Route causality -- foreign consistently materially faster than paired home
    print('\n=== (B) ROUTE CAUSALITY (foreign consistently materially faster than paired home) ===')
    paired = sorted(w for (r, w) in stats if r == foreign_route
                    and (home_route, w) in stats)
    if not paired:
        print('  no paired foreign+home windows -- causality not evaluable (need same-window pairs).')
    else:
        faster_all = True
        for w in paired:
            fm = stats[(foreign_route, w)]['median']
            hm = stats[(home_route, w)]['median']
            ratio = fm / hm if hm else float('inf')
            materially = ratio <= causality_ratio
            faster_all = faster_all and materially
            print('  window %s: foreign median=%d ms vs home median=%d ms  ratio=%.2f  delta=%d ms  %s'
                  % (w, fm, hm, ratio, hm - fm,
                     'materially faster' if materially else 'not materially faster'))
        print('  --> ROUTE CAUSALITY: %s (threshold ratio <= %.2f in every window)'
              % ('SUGGESTED' if faster_all else 'INCONCLUSIVE', causality_ratio))

    print('\nNOTE: a diagnostic PASS is NOT a production GO -- provisioning 4 profiles and the '
          'bounded arvant + 1->10->20->100 acceptance is a SEPARATE gate.')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='*', default=None,
                    help='JSONL probe files (default: the H898 home sweep files)')
    ap.add_argument('--decision-rule', action='store_true',
                    help='evaluate the foreign-route readiness + causality rule (sol.md #1/#3)')
    ap.add_argument('--ceiling', type=int, default=CEILING)
    ap.add_argument('--foreign-route', default='foreign-linux')
    ap.add_argument('--home-route', default='home-windows')
    ap.add_argument('--causality-ratio', type=float, default=0.70,
                    help='foreign median <= ratio x home median counts as "materially faster"')
    args = ap.parse_args()
    files = args.files or ['h898_sweep.jsonl', 'h898_interleaved.jsonl']
    rows = load(files)
    if not rows:
        print('no measured rows')
        return
    if args.decision_rule:
        decision_report(rows, args.ceiling, args.foreign_route, args.home_route, args.causality_ratio)
    else:
        legacy_report(rows)


if __name__ == '__main__':
    main()
