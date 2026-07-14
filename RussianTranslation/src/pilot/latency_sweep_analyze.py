#!/usr/bin/env python3
"""Analyze the H898 payload-size sweep JSONL: per-size stats, input-bytes vs
latency correlation + OLS slope, and the >30000 ms ceiling-breach rate.
Latency is valid for every completed call regardless of envelope classification
(the call round-tripped), so stats are over ALL calls; a success-only view is
also printed for the gated-latency comparison."""
import json
import sys
import statistics as st

sys.stdout.reconfigure(encoding='utf-8')

CEILING = 30000


def load(paths):
    rows = []
    for p in paths:
        try:
            with open(p, encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith('{'):
                        rows.append(json.loads(line))
        except FileNotFoundError:
            pass
    return rows


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
    """Return (slope_per_byte, intercept, r2)."""
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx if sxx else float('nan')
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot else float('nan')
    return slope, intercept, r2


def main():
    rows = load(sys.argv[1:] or ['h898_sweep.jsonl'])
    if not rows:
        print('no rows')
        return
    rows.sort(key=lambda r: r['ts_utc'])
    print('N calls = %d   window %s .. %s' %
          (len(rows), rows[0]['ts_utc'], rows[-1]['ts_utc']))
    by = {}
    for r in rows:
        by.setdefault(r['total_input_bytes'], []).append(r)
    print('\nper input-size band (ALL completed calls; latency_ms):')
    print('%8s %3s %7s %7s %7s %7s %7s  %s' %
          ('bytes', 'n', 'min', 'median', 'mean', 'max', 'stdev', 'classes'))
    for tib in sorted(by):
        lat = [r['latency_ms'] for r in by[tib]]
        cls = {}
        for r in by[tib]:
            cls[r['classification']] = cls.get(r['classification'], 0) + 1
        sd = int(st.pstdev(lat)) if len(lat) > 1 else 0
        print('%8d %3d %7d %7d %7d %7d %7d  %s' %
              (tib, len(lat), min(lat), int(st.median(lat)), int(st.mean(lat)),
               max(lat), sd, cls))
    xs = [r['total_input_bytes'] for r in rows]
    ys = [r['latency_ms'] for r in rows]
    r = pearson(xs, ys)
    slope, intercept, r2 = ols(xs, ys)
    over = [r for r in rows if r['latency_ms'] > CEILING]
    allv = sorted(ys)

    def pct(p):
        k = (len(allv) - 1) * p
        return int(allv[int(k)])
    print('\noverall (all %d calls): min=%d  p50=%d  p90=%d  max=%d  mean=%d  stdev=%d'
          % (len(ys), min(ys), pct(0.5), pct(0.9), max(ys), int(st.mean(ys)),
             int(st.pstdev(ys))))
    print('input-bytes vs latency:  Pearson r=%.3f   OLS slope=%.3f ms/byte '
          '(=%.1f ms per +1KB)   intercept=%d ms   R^2=%.3f'
          % (r, slope, slope * 1024, int(intercept), r2))
    print('ceiling breach (>%d ms): %d/%d = %.0f%% of calls'
          % (CEILING, len(over), len(rows), 100 * len(over) / len(rows)))
    succ = [r['latency_ms'] for r in rows if r['classification'] == 'success']
    if succ:
        print("success-only (n=%d): min=%d  median=%d  max=%d  >ceiling=%d"
              % (len(succ), min(succ), int(st.median(succ)), max(succ),
                 sum(1 for v in succ if v > CEILING)))


if __name__ == '__main__':
    main()
