#!/usr/bin/env python
"""Derive cache-economy totals from a sealed run manifest + event ledger (H2703).

Summaries are derived, never a second source of truth. A provider cache hit is
explanatory evidence, not an accepted artifact.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import cache_event_ledger as ledger  # noqa: E402
import cache_identity as ident  # noqa: E402

H2676_USD_PER_CLEAN = 0.01991
H2676_DET_CLEAN = 21
PARSEABLE_MIN = 42
PARSEABLE_DENOM = 44
N_PAIRS = 22


class ReportError(ValueError):
    pass


def _median(values):
    if not values:
        return None
    return float(statistics.median(values))


def _mean(values):
    if not values:
        return None
    return float(sum(values) / len(values))


def bootstrap_mean_ci(values, n=2000, seed=2703):
    if not values:
        return None
    rng = random.Random(seed)
    nobs = len(values)
    means = []
    for _ in range(n):
        sample = [values[rng.randrange(nobs)] for _ in range(nobs)]
        means.append(sum(sample) / nobs)
    means.sort()
    lo_i = int(0.025 * n)
    hi_i = min(n - 1, int(0.975 * n))
    return {
        'mean': _mean(values),
        'lo': means[lo_i],
        'hi': means[hi_i],
        'n': nobs,
        'draws': n,
        'seed': seed,
    }


def slot_events(events):
    rows = []
    for event in events:
        if event.get('kind') != 'terminal_response':
            continue
        if event.get('cold_warm') not in ('cold', 'warm'):
            continue
        if not event.get('request_id'):
            continue
        rows.append(event)
    return rows


def is_parseable(event):
    detail = event.get('detail') or {}
    return bool(detail.get('parseable'))


def is_det_clean(event):
    detail = event.get('detail') or {}
    return bool(detail.get('det_clean'))


def usage_cost_usd(event):
    if event.get('cost_evaluable') and event.get('observed_cost_usd') is not None:
        return float(event['observed_cost_usd'])
    return None


def _lane_floors(manifest):
    acceptance = manifest.get('acceptance') or {}
    n_pairs = int(acceptance.get('n_pairs') or manifest.get('n') or N_PAIRS)
    denom = int(acceptance.get('parseable_denom') or manifest.get('call_ceiling') or PARSEABLE_DENOM)
    parse_min = int(acceptance.get('parseable_min') or PARSEABLE_MIN)
    return n_pairs, denom, parse_min


def derive(manifest, events):
    if not isinstance(manifest, dict) or not manifest.get('sealed'):
        raise ReportError('manifest is not sealed')
    n_pairs, parseable_denom, parseable_min = _lane_floors(manifest)
    terminals = slot_events(events)
    parseable = [e for e in terminals if is_parseable(e)]
    unevaluable = [
        e for e in terminals
        if is_parseable(e) and (e.get('cost_evaluable') is False or e.get('usage') is None)
    ]
    model_mismatch = [
        e for e in terminals
        if e.get('served_model') and e.get('requested_model')
        and e.get('served_model') != e.get('requested_model')
    ]
    pairs = {}
    for event in terminals:
        rid = event['request_id']
        pairs.setdefault(rid, {'cold': None, 'warm': None, 'source_ordinal': event.get('source_ordinal')})
        pairs[rid][event['cold_warm']] = event

    pair_rows = []
    cold_costs = []
    warm_costs = []
    deltas = []
    cold_hits = []
    warm_hits = []
    unique_clean = set()
    for rid, members in sorted(pairs.items(), key=lambda kv: (kv[1].get('source_ordinal') is None, kv[1].get('source_ordinal'), kv[0])):
        cold = members['cold']
        warm = members['warm']
        cold_cost = usage_cost_usd(cold) if cold else None
        warm_cost = usage_cost_usd(warm) if warm else None
        cold_hit = None
        warm_hit = None
        if cold and isinstance(cold.get('usage'), dict):
            cold_hit = cold['usage'].get('cache_hit_tokens')
        if warm and isinstance(warm.get('usage'), dict):
            warm_hit = warm['usage'].get('cache_hit_tokens')
        if cold_cost is not None:
            cold_costs.append(cold_cost)
        if warm_cost is not None:
            warm_costs.append(warm_cost)
        if cold_cost is not None and warm_cost is not None:
            deltas.append(warm_cost - cold_cost)
        if cold_hit is not None:
            cold_hits.append(cold_hit)
        if warm_hit is not None:
            warm_hits.append(warm_hit)
        if (cold and is_det_clean(cold)) or (warm and is_det_clean(warm)):
            unique_clean.add(rid)
        pair_rows.append({
            'request_id': rid,
            'source_ordinal': members.get('source_ordinal'),
            'cold_parseable': bool(cold and is_parseable(cold)),
            'warm_parseable': bool(warm and is_parseable(warm)),
            'cold_det_clean': bool(cold and is_det_clean(cold)),
            'warm_det_clean': bool(warm and is_det_clean(warm)),
            'cold_cost_usd': cold_cost,
            'warm_cost_usd': warm_cost,
            'delta_warm_minus_cold_usd': (
                None if cold_cost is None or warm_cost is None
                else warm_cost - cold_cost
            ),
            'cold_cache_hit_tokens': cold_hit,
            'warm_cache_hit_tokens': warm_hit,
            'blind_class': ((cold or {}).get('detail') or {}).get('blind_class')
            or ((warm or {}).get('detail') or {}).get('blind_class'),
        })

    total_usd = 0.0
    cost_evaluable_n = 0
    for event in terminals:
        cost = usage_cost_usd(event)
        if cost is not None:
            total_usd += cost
            cost_evaluable_n += 1

    attempted_slots = len(terminals)
    parseable_n = len(parseable)
    clean_slots = sum(1 for e in terminals if is_det_clean(e))
    unique_clean_n = len(unique_clean)
    retry_events = [
        e for e in events
        if e.get('kind') == 'retry' or (
            e.get('kind') == 'dispatch' and (e.get('attempt') or 1) > 1
        )
    ]
    dispatch_n = sum(1 for e in events if e.get('kind') == 'dispatch')
    retry_amplification = (
        None if attempted_slots == 0 else dispatch_n / float(attempted_slots)
    )

    parseable_rate = (
        None if parseable_denom == 0 else parseable_n / float(parseable_denom)
    )
    usd_per_unique_clean = (
        None if unique_clean_n == 0 else total_usd / unique_clean_n
    )
    usd_per_clean_slot = (
        None if clean_slots == 0 else total_usd / clean_slots
    )

    stop_reason = None
    for event in events:
        if event.get('kind') == 'stop':
            stop_reason = (event.get('detail') or {}).get('reason') or 'stop'
            break

    pairs_attempted = sum(
        1 for row in pair_rows if row['cold_parseable'] or row['warm_parseable']
        or any(pairs[row['request_id']].values())
    )
    # Count pairs that have both slots terminal.
    pairs_complete = sum(
        1 for members in pairs.values()
        if members['cold'] is not None and members['warm'] is not None
    )

    generation_lane = 'INCONCLUSIVE'
    fail_reasons = []
    if stop_reason:
        fail_reasons.append('stop:%s' % stop_reason)
    if parseable_n < parseable_min:
        fail_reasons.append('parseable %d/%d' % (parseable_n, parseable_denom))
    if model_mismatch:
        fail_reasons.append('served_model_mismatch')
    if unevaluable:
        fail_reasons.append('unevaluable_billing')
    if pairs_complete < n_pairs and not stop_reason:
        fail_reasons.append('pairs_incomplete %d/%d' % (pairs_complete, n_pairs))
    if manifest.get('promotable') is not False:
        fail_reasons.append('promotable_not_false')
    if attempted_slots == 0:
        generation_lane = 'INCONCLUSIVE'
        fail_reasons.append('no_terminal_slots')
    elif fail_reasons:
        generation_lane = 'FAIL'
    elif (
        pairs_complete == n_pairs
        and parseable_n >= parseable_min
        and not model_mismatch
        and not unevaluable
        and not stop_reason
    ):
        generation_lane = 'PASS'

    return {
        'schema': 'pwg.cache_economy_report.v1',
        'handoff': (manifest.get('acceptance') or {}).get('handoff') or manifest.get('handoff') or 'H2703',
        'run_id': manifest.get('run_id'),
        'manifest_sha256': manifest.get('manifest_sha256'),
        'n_pairs': n_pairs,
        'max_base_calls': parseable_denom,
        'attempted_slots': attempted_slots,
        'pairs_complete': pairs_complete,
        'pairs_attempted': pairs_attempted,
        'parseable': parseable_n,
        'parseable_rate_of_44': parseable_rate,
        'det_clean_slots': clean_slots,
        'unique_clean_cards': unique_clean_n,
        'h2676_det_clean': H2676_DET_CLEAN,
        'h2676_usd_per_clean': H2676_USD_PER_CLEAN,
        'total_usd': round(total_usd, 6),
        'cost_evaluable_slots': cost_evaluable_n,
        'usd_per_unique_clean': (
            None if usd_per_unique_clean is None else round(usd_per_unique_clean, 6)
        ),
        'usd_per_clean_slot': (
            None if usd_per_clean_slot is None else round(usd_per_clean_slot, 6)
        ),
        'cold': {
            'n': len(cold_costs),
            'total_usd': round(sum(cold_costs), 6) if cold_costs else 0.0,
            'mean_usd': _mean(cold_costs),
            'median_usd': _median(cold_costs),
            'mean_cache_hit_tokens': _mean(cold_hits),
        },
        'warm': {
            'n': len(warm_costs),
            'total_usd': round(sum(warm_costs), 6) if warm_costs else 0.0,
            'mean_usd': _mean(warm_costs),
            'median_usd': _median(warm_costs),
            'mean_cache_hit_tokens': _mean(warm_hits),
        },
        'paired_delta_warm_minus_cold': {
            'n': len(deltas),
            'mean_usd': _mean(deltas),
            'median_usd': _median(deltas),
            'bootstrap': bootstrap_mean_ci(deltas),
        },
        'retry_amplification': retry_amplification,
        'dispatch_events': dispatch_n,
        'cache_hit_is_not_accepted_artifact': True,
        'accepted_artifact_rule': (
            'det_gate_clean parseable card; unique by request_id; '
            'provider cache hit is explanatory only'
        ),
        'generation_lane_verdict': generation_lane,
        'fail_reasons': fail_reasons,
        'stop_reason': stop_reason,
        'pairs': pair_rows,
        'adoption': 'deferred_to_H2704',
    }


def load_and_derive(manifest_path, ledger_path):
    with open(manifest_path, encoding='utf-8') as handle:
        manifest = json.loads(handle.read())
    events = ledger.read_events(ledger_path)
    return derive(manifest, events)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--ledger', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args(argv)
    report = load_and_derive(args.manifest, args.ledger)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(report))
    print('generation_lane=%s parseable=%s/%s unique_clean=%s total_usd=%s'
          % (report['generation_lane_verdict'], report['parseable'],
             PARSEABLE_DENOM, report['unique_clean_cards'], report['total_usd']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
