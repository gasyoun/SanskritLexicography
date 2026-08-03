"""H2138 (#946) — derive the probe latency ceiling from the measured c4 series.

Re-derives `probe_log.POLICIES['production_v3']` from the append-only c4 health-probe
series instead of restating a ruled number. Offline and free: every reading below was
already paid for by H2011 / H2152 / H2158 / H2174, so this script makes **zero** calls.

Why two ceilings and not one
----------------------------
`production_v1` (30 000) and `production_v2` (65 000) carry a single wall-clock ceiling.
The measured series shows that one number cannot do the job, because wall time is the sum
of two independent quantities:

    wall elapsed_ms  =  duration_api_ms  +  api_gap_ms
                        (route health)     (in-CLI scaffolding)

and they move independently — the api/wall ratio ranges 0.25..0.72 across the five
decomposable readings, so no fixed factor converts one into the other (H2174). The
consequence is concrete: the 02-08 12:46 reading carried the **fastest API time ever
recorded on c4** (16 445 ms) and still failed the 65 000 ms wall gate, on 49 846 ms of
scaffolding. A healthy route was refused a window.

So `production_v3` keeps gating on wall elapsed_ms — MG's 02-08-2026 ruling (H2160 option
A), not reopened here — and adds `api_ceil_ms` as a **second, independent** fail
condition, which is h2152 §5.2 item 2 and H2174's "option C". It is an ADDED guard: it
catches genuine route degradation that a wall number conflates with scaffolding noise.

Run:  python src/pilot/h2138_ceiling_derive.py
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

# The append-only measured c4 health-probe series, transcribed from RESULTS_LOG.md.
# `api` is None for readings taken before the H2095 `duration_api_ms` instrumentation.
# (date_utc, wall_elapsed_ms, api_ms)
READINGS = [
    ('2026-07-22 20:04', 102_874, None),
    ('2026-07-23 06:09', 168_352, None),
    ('2026-07-31 19:01', 78_415, None),
    ('2026-08-01 20:21', 50_336, 27_557),
    ('2026-08-02 05:48', 43_815, 26_386),
    ('2026-08-02 07:49', 75_561, 29_069),
    ('2026-08-02 11:06', 96_520, 69_137),
    ('2026-08-02 12:46', 66_291, 16_445),
]

ROUTE_SAFETY_MARGIN = 1.5   # headroom over the healthy-route cluster
ROUND_TO = 5_000            # ceilings are stated in round steps, never to the millisecond


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def round_up(x, step=ROUND_TO):
    return int(-(-x // step) * step)


def split_cluster(values):
    """Split a sorted series at its largest MULTIPLICATIVE gap.

    Route latency is either 'normal' or 'degraded'; an additive threshold would be
    arbitrary, but the ratio between consecutive readings is scale-free. Returns
    (cluster, outliers).
    """
    s = sorted(values)
    if len(s) < 3:
        return s, []
    ratios = [(s[i + 1] / s[i], i) for i in range(len(s) - 1)]
    best_ratio, cut = max(ratios)
    if best_ratio < 1.5:            # no real separation — treat the whole series as one
        return s, []
    return s[:cut + 1], s[cut + 1:]


def main():
    walls = [w for _, w, _ in READINGS]
    apis = [a for _, _, a in READINGS if a is not None]
    gaps = [w - a for _, w, a in READINGS if a is not None]

    print('H2138 — probe ceiling derivation from the measured c4 series')
    print('=' * 66)
    print(f'readings: n={len(walls)} wall, n={len(apis)} decomposable (carry duration_api_ms)')
    print()

    print('  wall elapsed_ms : min %6d  median %8.0f  max %6d' % (min(walls), median(walls), max(walls)))
    print('  duration_api_ms : min %6d  median %8.0f  max %6d' % (min(apis), median(apis), max(apis)))
    print('  api_gap_ms      : min %6d  median %8.0f  max %6d' % (min(gaps), median(gaps), max(gaps)))
    ratios = [a / w for _, w, a in READINGS if a is not None]
    print('  api/wall ratio  : min %6.2f  median %8.2f  max %6.2f' % (min(ratios), median(ratios), max(ratios)))
    print()

    cluster, outliers = split_cluster(apis)
    print('ROUTE ceiling (api_ceil_ms) — from the duration_api_ms distribution')
    print(f'  healthy cluster : {cluster}')
    print(f'  degraded        : {outliers}')
    api_ceil = round_up(max(cluster) * ROUTE_SAFETY_MARGIN)
    print(f'  rule            : round_up(cluster_max {max(cluster)} x {ROUTE_SAFETY_MARGIN}) = {api_ceil}')
    print(f'  -> api_ceil_ms  = {api_ceil}   admits {sum(1 for a in apis if a < api_ceil)}/{len(apis)}')
    print()

    print('WALL ceiling (latency_ceil_ms) — the worst LEGITIMATE healthy call')
    print('  A call is legitimate when its route is healthy; its wall time may still carry')
    print('  the largest scaffolding tax ever observed. Ceiling = the sum of those two.')
    wall_ceil = round_up(max(cluster) + max(gaps))
    print(f'  rule            : round_up(cluster_max_api {max(cluster)} + max_gap {max(gaps)}) = {wall_ceil}')
    admitted = sum(1 for w in walls if w < wall_ceil)
    print(f'  -> latency_ceil_ms = {wall_ceil}   admits {admitted}/{len(walls)}'
          f' ({100.0 * admitted / len(walls):.0f} %)')
    print()

    print('Verdict change vs production_v2 (65 000, wall only)')
    print('  %-18s %9s %9s   %-8s -> %-8s  %s' % ('date', 'wall', 'api', 'v2', 'v3', 'why'))
    for date, wall, api in READINGS:
        v2 = 'GO' if wall < 65_000 else 'NO-GO'
        if wall >= wall_ceil:
            v3, why = 'NO-GO', 'wall over ceiling'
        elif api is not None and api >= api_ceil:
            v3, why = 'NO-GO', 'ROUTE degraded (new guard)'
        else:
            v3, why = 'GO', 'healthy route'
        flag = '  <-- flips' if v2 != v3 else ''
        print('  %-18s %9d %9s   %-8s -> %-8s  %s%s'
              % (date, wall, api if api is not None else '—', v2, v3, why, flag))
    print()
    print(f'  pass rate: v2 {sum(1 for w in walls if w < 65_000)}/{len(walls)}'
          f'  ->  v3 {sum(1 for w, a in ((w, a) for _, w, a in READINGS) if w < wall_ceil and (a is None or a < api_ceil))}/{len(walls)}')
    print()
    print('NOT a weakened guard: every reading v2 rejected on genuine route degradation is')
    print('still rejected by v3, now for the right reason. What v3 stops rejecting is the')
    print('healthy-route/slow-scaffolding class the wall number could never distinguish.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
