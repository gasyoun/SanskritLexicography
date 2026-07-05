#!/usr/bin/env python
"""Evolution / timelapse statistics for the RussianTranslation dashboard.

Reads the local, append-only operational logs and derives day-bucketed trend
series that tell the maturation story of the pwg_ru pipeline: throughput,
coverage, cost/efficiency, quality, an "academic rigor" proxy, and a failure
typology over time. Consumed by the dashboard's `/api/evolution` endpoint (which
caches on source mtimes) and writeable to `output/evolution_stats.json` via the
CLI for offline inspection.

All inputs are best-effort: a missing/partial file degrades that series to
nulls rather than raising, because this is observability, not a gate.
"""
import datetime
import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))

# Coverage denominators (PWG unique headwords / DCS-attested subset). See
# RUN_FREQ_MAX.md: 43,968 / 106,082 PWG headwords are DCS-attested.
PWG_HEADWORDS = 106082
DCS_ATTESTED = 43968


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def source_paths(root):
    out = os.path.join(root, 'src', 'pilot', 'output')
    return {
        'cards': os.path.join(root, 'src', 'pwg_ru_translated.jsonl'),
        'ledger': os.path.join(out, 'window_ledger.jsonl'),
        'events': os.path.join(out, 'dashboard_events.jsonl'),
        'failures': os.path.join(root, 'failures', 'failures.jsonl'),
        'failures_auto': os.path.join(root, 'failures', 'auto_failures.jsonl'),
    }


def newest_mtime(paths):
    mt = 0.0
    for p in paths.values():
        try:
            mt = max(mt, os.path.getmtime(p))
        except OSError:
            continue
    return mt


def _iter_jsonl(path):
    if not os.path.exists(path):
        return
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _day(ts):
    """First 10 chars of an ISO-8601 timestamp -> YYYY-MM-DD, or None."""
    if not ts or not isinstance(ts, str) or len(ts) < 10:
        return None
    return ts[:10]


def _daterange(start, end):
    d0 = datetime.date.fromisoformat(start)
    d1 = datetime.date.fromisoformat(end)
    days = []
    cur = d0
    while cur <= d1:
        days.append(cur.isoformat())
        cur += datetime.timedelta(days=1)
    return days


def _pct(n, d):
    return round(100.0 * n / d, 3) if d else 0.0


def build_evolution_stats(root=REPO):
    paths = source_paths(root)

    # ---- cards: per-day new cards, first-seen roots, provenance completeness ----
    cards_by_day = {}          # day -> card count
    roots_first_day = {}       # key1 -> first day seen
    prov_full_by_day = {}      # day -> cards with model_version AND pipeline
    seen_days = set()
    total_cards = 0
    for c in _iter_jsonl(paths['cards']):
        prov = c.get('provenance') or {}
        day = _day(prov.get('generated_at'))
        if not day:
            continue
        total_cards += 1
        seen_days.add(day)
        cards_by_day[day] = cards_by_day.get(day, 0) + 1
        key1 = c.get('key1') or prov.get('root')
        if key1 and (key1 not in roots_first_day or day < roots_first_day[key1]):
            roots_first_day[key1] = day
        has_prov = bool(prov.get('model_version')) and bool(prov.get('pipeline'))
        if has_prov:
            prov_full_by_day[day] = prov_full_by_day.get(day, 0) + 1

    roots_by_day = {}
    for key1, day in roots_first_day.items():
        roots_by_day[day] = roots_by_day.get(day, 0) + 1

    # ---- ledger: per-audit quality + efficiency, bucketed by day ----
    led_requeue = {}   # day -> [requeue_rate, ...]
    led_tokens = {}    # day -> [max_output_tokens, ...]
    led_minutes = {}   # day -> [wall_clock_minutes, ...]
    for r in _iter_jsonl(paths['ledger']):
        day = _day(r.get('recorded_at'))
        if not day:
            continue
        seen_days.add(day)
        wk = r.get('workflow_keys') or 0
        rq = r.get('requeue_count') or 0
        if wk:
            led_requeue.setdefault(day, []).append(rq / wk)
        pm = r.get('production_metrics') or {}
        tok = pm.get('max_output_tokens')
        if isinstance(tok, (int, float)) and tok > 0:
            led_tokens.setdefault(day, []).append(float(tok))
        mins = pm.get('wall_clock_minutes')
        if isinstance(mins, (int, float)) and mins > 0:
            led_minutes.setdefault(day, []).append(float(mins))

    # ---- events: gate-failure counts (all-time + per day) ----
    gate_fail_total = {}   # gate -> count
    gate_fail_day = {}     # day -> {gate -> count}
    for e in _iter_jsonl(paths['events']):
        if e.get('type') != 'gate_summary':
            continue
        data = e.get('data') or {}
        gate = data.get('gate') or e.get('source') or 'gate'
        failed = (data.get('requeue_count') or 0) > 0 or \
                 str(e.get('level')) in ('warn', 'error') or \
                 str(data.get('status')).lower() in ('fail', 'failed')
        if not failed:
            continue
        gate_fail_total[gate] = gate_fail_total.get(gate, 0) + 1
        day = _day(e.get('ts'))
        if day:
            seen_days.add(day)
            gate_fail_day.setdefault(day, {})[gate] = \
                gate_fail_day.setdefault(day, {}).get(gate, 0) + 1

    # ---- failures.jsonl: typology (modes x severity) + timeline ----
    mode_counts = {}
    sev_counts = {}
    fail_timeline = {}   # day -> count
    fail_records = []
    for src_key in ('failures', 'failures_auto'):
        origin = 'auto' if src_key == 'failures_auto' else 'curated'
        for fr in _iter_jsonl(paths.get(src_key, '')):
            mode = fr.get('mode') or 'unknown'
            sev = fr.get('severity') or 'unknown'
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
            day = fr.get('date') or None
            if day:
                fail_timeline[day] = fail_timeline.get(day, 0) + 1
            fail_records.append({'id': fr.get('id'), 'date': day, 'mode': mode,
                                 'severity': sev, 'origin': fr.get('source') or origin,
                                 'symptom': (fr.get('symptom') or '')[:200]})

    # ---- assemble the day axis + cumulative series ----
    all_days = sorted(seen_days | set(fail_timeline))
    if not all_days:
        return {'generated_at': utc_now(), 'empty': True,
                'note': 'no timestamped data found yet'}
    days = _daterange(all_days[0], all_days[-1])

    def cum(daily):
        run, out = 0, []
        for d in days:
            run += daily.get(d, 0)
            out.append(run)
        return out

    def avg_series(bucket):
        return [round(sum(bucket[d]) / len(bucket[d]), 4) if bucket.get(d) else None
                for d in days]

    cards_daily = [cards_by_day.get(d, 0) for d in days]
    cards_cum = cum(cards_by_day)
    roots_cum = cum(roots_by_day)
    prov_cum = cum(prov_full_by_day)
    rigor_index = [_pct(prov_cum[i], cards_cum[i]) for i in range(len(days))]
    coverage_pwg = [_pct(roots_cum[i], PWG_HEADWORDS) for i in range(len(days))]
    coverage_dcs = [_pct(roots_cum[i], DCS_ATTESTED) for i in range(len(days))]

    tokens_avg = avg_series(led_tokens)
    minutes_avg = avg_series(led_minutes)
    requeue_avg = [round(100.0 * sum(led_requeue[d]) / len(led_requeue[d]), 2)
                   if led_requeue.get(d) else None for d in days]

    series = {
        'cards_daily': cards_daily,
        'cards_cumulative': cards_cum,
        'roots_cumulative': roots_cum,
        'coverage_pwg_pct': coverage_pwg,
        'coverage_dcs_pct': coverage_dcs,
        'rigor_index_pct': rigor_index,
        'requeue_rate_pct': requeue_avg,
        'tokens_per_window': tokens_avg,
        'minutes_per_window': minutes_avg,
    }

    return {
        'generated_at': utc_now(),
        'span': {'start': days[0], 'end': days[-1], 'days': len(days)},
        'days': days,
        'series': series,
        'headline': _headline(total_cards, roots_cum, coverage_pwg, coverage_dcs,
                              rigor_index, requeue_avg, tokens_avg, minutes_avg),
        'failure_typology': {
            'modes': sorted(({'mode': m, 'count': c} for m, c in mode_counts.items()),
                            key=lambda x: -x['count']),
            'severity': sorted(({'severity': s, 'count': c} for s, c in sev_counts.items()),
                               key=lambda x: -x['count']),
            'timeline': [{'date': d, 'count': fail_timeline.get(d, 0)} for d in days],
            'records': fail_records,
        },
        'gate_failures': sorted(({'gate': g, 'count': c} for g, c in gate_fail_total.items()),
                                key=lambda x: -x['count']),
        'trends': _trends(days, cards_cum, coverage_pwg, rigor_index, requeue_avg,
                          tokens_avg, minutes_avg, mode_counts, fail_timeline),
    }


def _first_last(vals):
    """First and last non-null values of a series."""
    nn = [v for v in vals if v is not None]
    if not nn:
        return None, None
    return nn[0], nn[-1]


def _headline(total_cards, roots_cum, cov_pwg, cov_dcs, rigor, requeue, tokens, minutes):
    return {
        'total_cards': total_cards,
        'total_roots': roots_cum[-1] if roots_cum else 0,
        'coverage_pwg_pct': cov_pwg[-1] if cov_pwg else 0.0,
        'coverage_dcs_pct': cov_dcs[-1] if cov_dcs else 0.0,
        'rigor_index_pct': rigor[-1] if rigor else 0.0,
        'requeue_rate_pct': _first_last(requeue)[1],
    }


def _delta_pct(first, last):
    if first in (None, 0) or last is None:
        return None
    return round(100.0 * (last - first) / first, 1)


def _trends(days, cards_cum, cov_pwg, rigor, requeue, tokens, minutes,
            mode_counts, fail_timeline):
    """Human-readable trend insights ('find trends')."""
    out = []
    if len(days) >= 2:
        out.append('Grew from %d to %d translated cards over %d days.'
                   % (cards_cum[0], cards_cum[-1], len(days)))
    tok_f, tok_l = _first_last(tokens)
    d = _delta_pct(tok_f, tok_l)
    if d is not None:
        if abs(d) < 1:
            out.append('Per-window output tokens held ~flat at %.0f.' % tok_l)
        else:
            out.append('Per-window output tokens %s %.0f%% (%.0f→%.0f) — cost %s.'
                       % ('fell' if d < 0 else 'rose', abs(d), tok_f, tok_l,
                          'down' if d < 0 else 'up'))
    min_f, min_l = _first_last(minutes)
    d = _delta_pct(min_f, min_l)
    if d is not None and abs(d) >= 1:
        out.append('Per-window wall-clock %s %.0f%% (%.1f→%.1f min) — %s.'
                   % ('fell' if d < 0 else 'rose', abs(d), min_f, min_l,
                      'faster' if d < 0 else 'slower'))
    rq_f, rq_l = _first_last(requeue)
    if rq_f is not None and rq_l is not None:
        out.append('Requeue rate moved %.1f%%→%.1f%% (a rise can reflect stricter gates, not worse output).'
                   % (rq_f, rq_l))
    if rigor:
        out.append('Academic-rigor index (cards with full model+pipeline provenance) at %.0f%%.'
                   % rigor[-1])
    if cov_pwg:
        out.append('Coverage of PWG headwords at %.2f%% (DCS-attested share higher).' % cov_pwg[-1])
    if mode_counts:
        top = max(mode_counts.items(), key=lambda x: x[1])
        out.append('Dominant recorded failure mode: "%s" (%d of %d gallery entries).'
                   % (top[0], top[1], sum(mode_counts.values())))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default=REPO)
    ap.add_argument('--out', default=None,
                    help='write JSON here (default: <root>/src/pilot/output/evolution_stats.json)')
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    stats = build_evolution_stats(root)
    out = args.out or os.path.join(root, 'src', 'pilot', 'output', 'evolution_stats.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
    hl = stats.get('headline', {})
    print('evolution_stats -> %s' % out)
    print('  span   : %s' % (stats.get('span') or 'empty'))
    print('  cards  : %s  roots: %s' % (hl.get('total_cards'), hl.get('total_roots')))
    for t in stats.get('trends', []):
        print('  trend  : %s' % t)


if __name__ == '__main__':
    main()
