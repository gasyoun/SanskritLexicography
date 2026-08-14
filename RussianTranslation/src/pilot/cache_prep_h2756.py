#!/usr/bin/env python
"""H2756 — Flash PREP one-shot vs incremental warm (H2754 residual).

Zero-call CONCLUSIONS replay, then a fresh 50-miss Flash pair sitting.
Does not reuse H2704 IDs. Experimental TM stays under the sealed run root.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import cache_economy_report as report  # noqa: E402
import cache_identity as ident  # noqa: E402
import cache_prep_census as census  # noqa: E402

RT = os.path.dirname(os.path.dirname(HERE))
EXP = os.path.join(RT, 'experiments', 'pwg_cache_economy')
H2704_DIR = os.path.join(EXP, 'h2704_prep')
H2703_DIR = os.path.join(EXP, 'h2703_generation')
H2756_DIR = os.path.join(EXP, 'h2756_flash')
H2675_USD = 0.000873
PREP_SALT = 'h2756-prep-50-v1'
PREP_N = 50
HANDOFF = 'H2756'


class VerifyError(ValueError):
    pass


def load_json(path):
    with open(path, encoding='utf-8') as handle:
        return json.loads(handle.read())


def _near(got, expected, digits, label):
    scale = 10 ** digits
    if round(got * scale) != round(expected * scale):
        raise VerifyError(
            '%s: got %s expected %s (digits=%d)' % (label, got, expected, digits))


def verify_conclusions():
    """Replay CONCLUSIONS headline numbers from sealed H2703/H2704 summaries."""
    prep = load_json(os.path.join(H2704_DIR, 'prep50', 'run', 'summary.json'))
    gen = load_json(os.path.join(H2703_DIR, 'run', 'summary.json'))
    l3_path = os.path.join(H2704_DIR, 'l3', 'run', 'summary.json')
    l3 = load_json(l3_path) if os.path.isfile(l3_path) else None
    deltas = []

    if prep.get('parseable') != 100:
        deltas.append('Flash parseable %s != 100' % prep.get('parseable'))
    _near(float(prep['total_usd']), 0.041929, 6, 'Flash PREP spend')
    _near(float(prep['cold']['total_usd']), 0.022056, 6, 'Flash cold total')
    _near(float(prep['cold']['mean_usd']), 0.000441, 6, 'Flash cold mean')
    _near(float(prep['cold']['mean_cache_hit_tokens']), 87, 0, 'Flash cold hit tokens')
    _near(float(prep['warm']['total_usd']), 0.019872, 6, 'Flash warm total')
    _near(float(prep['warm']['mean_usd']), 0.000397, 6, 'Flash warm mean')
    _near(float(prep['warm']['mean_cache_hit_tokens']), 445, 0, 'Flash warm hit tokens')
    boot = (prep.get('paired_delta_warm_minus_cold') or {}).get('bootstrap') or {}
    _near(float(boot['mean']), -0.0000437, 7, 'Flash paired delta mean')
    _near(float(boot['lo']), -0.000134, 6, 'Flash paired delta lo')
    _near(float(boot['hi']), 0.000040, 6, 'Flash paired delta hi')
    pair_per = float(prep['total_usd']) / 50.0
    _near(pair_per, 0.000839, 6, 'Flash pair USD / card')
    vs_h2675 = pair_per / H2675_USD - 1.0
    _near(vs_h2675, -0.039, 3, 'Flash vs H2675')
    same_card = (-float(boot['mean'])) / float(prep['cold']['mean_usd'])
    _near(same_card, 0.099, 3, 'Flash same-card save')

    if gen.get('parseable') != 42 or gen.get('attempted_slots') != 44:
        deltas.append('Generation parseable %s/%s != 42/44'
                      % (gen.get('parseable'), gen.get('attempted_slots')))
    _near(float(gen['total_usd']), 0.555956, 6, 'Generation spend')
    if gen.get('unique_clean_cards') != 20:
        deltas.append('Generation unique_clean %s != 20'
                      % gen.get('unique_clean_cards'))
    _near(float(gen['usd_per_unique_clean']), 0.02780, 5, 'Generation USD/unique')
    vs_h2676 = float(gen['usd_per_unique_clean']) / 0.01991 - 1.0
    _near(vs_h2676, 0.396, 3, 'Generation vs H2676')
    _near(float(gen['cold']['mean_cache_hit_tokens']), 13585, 0,
          'Generation cold hit tokens')

    if l3 is not None:
        if l3.get('parseable') != 192 or l3.get('attempted_slots') != 200:
            deltas.append('L3 parseable %s/%s != 192/200'
                          % (l3.get('parseable'), l3.get('attempted_slots')))
        _near(float(l3['total_usd']), 0.046207, 6, 'L3 spend')

    if deltas:
        raise VerifyError('CONCLUSIONS replay failed: ' + '; '.join(deltas))
    return {
        'ok': True,
        'flash_parseable': prep['parseable'],
        'flash_total_usd': prep['total_usd'],
        'flash_pair_per_card': pair_per,
        'flash_vs_h2675': vs_h2675,
        'flash_same_card_save': same_card,
        'generation_parseable': '%s/%s' % (gen['parseable'], gen['attempted_slots']),
        'generation_vs_h2676': vs_h2676,
    }


def h2704_keys():
    body = load_json(os.path.join(H2704_DIR, 'prep50.manifest.json'))
    keys = list(body.get('keys') or [])
    if len(keys) != PREP_N:
        raise VerifyError('H2704 prep50 has %d keys, not 50' % len(keys))
    return set(keys)


def select_50():
    census_body = load_json(os.path.join(H2704_DIR, 'census.json'))
    banned = h2704_keys()
    pool = []
    for row in census_body.get('rows') or []:
        if row.get('tier') != 'miss':
            continue
        key1 = row.get('key1')
        if not key1 or key1 in banned:
            continue
        item = dict(row)
        item['selection_hex'] = census.stable_hex(PREP_SALT, key1)
        pool.append(item)
    if len(pool) < PREP_N:
        raise VerifyError('only %d leftover first-200 misses' % len(pool))
    selected = census.allocate_stratified(pool, PREP_N, PREP_SALT)
    keys = [row['key1'] for row in selected]
    if len(keys) != PREP_N:
        raise VerifyError('selected %d != 50' % len(keys))
    if set(keys) & banned:
        raise VerifyError('selection overlaps H2704 keys')
    return selected, pool, banned


def write_manifest(selected):
    os.makedirs(H2756_DIR, exist_ok=True)
    body = {
        'schema': 'pwg.cache_prep_50.v1',
        'handoff': HANDOFF,
        'salt': PREP_SALT,
        'n': PREP_N,
        'max_base_calls': PREP_N * 2,
        'cost_ceiling_usd': 1.0,
        'requested_model': 'deepseek-v4-flash',
        'excluded_h2704_keys': sorted(h2704_keys()),
        'keys': [row['key1'] for row in selected],
        'rows': selected,
    }
    body['manifest_sha256'] = ident.sha256_bytes(ident.canonical_bytes(
        {k: v for k, v in body.items() if k != 'manifest_sha256'}
    ))
    path = os.path.join(H2756_DIR, 'prep50.manifest.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(body))
    return path, body


def bootstrap_ratio_of_means(colds, warms, n=2000, seed=2756):
    """Bootstrap 95% CI for (mean_cold − mean_warm) / mean_cold.

    H2704 CONCLUSIONS 9.9% is this ratio-of-means, not the mean of per-pair
    ratios (small-cold / noisy-warm pairs explode that mean).
    """
    if not colds or not warms or len(colds) != len(warms):
        return None
    nobs = len(colds)
    rng = random.Random(seed)
    draws = []
    for _ in range(n):
        idx = [rng.randrange(nobs) for _ in range(nobs)]
        mc = sum(colds[i] for i in idx) / nobs
        mw = sum(warms[i] for i in idx) / nobs
        if mc <= 0:
            continue
        draws.append((mc - mw) / mc)
    if not draws:
        return None
    draws.sort()
    lo_i = int(0.025 * len(draws))
    hi_i = min(len(draws) - 1, int(0.975 * len(draws)))
    mc = sum(colds) / nobs
    mw = sum(warms) / nobs
    point = (mc - mw) / mc
    return {
        'mean': point,
        'lo': draws[lo_i],
        'hi': draws[hi_i],
        'n': nobs,
        'draws': n,
        'seed': seed,
    }


def paired_save_metrics(summary):
    """Primary metric B: (mean cold − mean warm) / mean cold on complete pairs."""
    colds = []
    warms = []
    for row in summary.get('pairs') or []:
        cold = row.get('cold_cost_usd')
        warm = row.get('warm_cost_usd')
        if cold is None or warm is None:
            continue
        if not row.get('cold_parseable') or not row.get('warm_parseable'):
            continue
        colds.append(float(cold))
        warms.append(float(warm))
    if not colds:
        return {
            'n': 0,
            'point_save': None,
            'ci': None,
            'dollar_mean': None,
            'dollar_ci': None,
            'totals_save': None,
        }
    nobs = len(colds)
    mc = sum(colds) / nobs
    mw = sum(warms) / nobs
    dollar = [c - w for c, w in zip(colds, warms)]
    ci = bootstrap_ratio_of_means(colds, warms, n=2000, seed=2756)
    dollar_ci = report.bootstrap_mean_ci(dollar, n=2000, seed=2756)
    return {
        'n': nobs,
        'point_save': (mc - mw) / mc if mc else None,
        'ci': ci,
        'dollar_mean': sum(dollar) / nobs,
        'dollar_ci': dollar_ci,
        'totals_save': (sum(colds) - sum(warms)) / sum(colds),
        'complete_cold_mean': mc,
        'complete_warm_mean': mw,
    }


def amortized(cold_mean, warm_mean, repeats):
    if cold_mean is None or warm_mean is None or repeats < 1:
        return None
    return (cold_mean + (repeats - 1) * warm_mean) / float(repeats)


def flash_verdict(summary, save, hashes_equal):
    parseable = int(summary.get('parseable') or 0)
    attempted = int(summary.get('attempted_slots') or 0)
    evaluable = int(summary.get('cost_evaluable_slots') or 0)
    retry = summary.get('retry_amplification')
    point = save.get('point_save')
    ci = save.get('ci') or {}
    lo = ci.get('lo')
    hi = ci.get('hi')
    reasons = []
    if attempted < 95 or parseable < 95:
        reasons.append('parseable %s/%s' % (parseable, attempted or 100))
    if evaluable < parseable:
        reasons.append('unevaluable_billing')
    if retry not in (None, 1, 1.0):
        reasons.append('retry_amplification %s' % retry)
    if not hashes_equal:
        reasons.append('canonical_hash_change')
    if summary.get('generation_lane_verdict') == 'FAIL':
        reasons.append('lane_fail')
    if reasons:
        return 'NO-GO', reasons
    if point is None:
        return 'NO-GO', ['no_paired_save']
    if point <= 0:
        return 'NO-GO', ['point_save <= 0']
    if lo is None or hi is None:
        return 'INCONCLUSIVE', ['missing_ci']
    if lo <= 0 <= hi:
        return 'INCONCLUSIVE', ['CI includes 0']
    if lo > 0:
        return 'GO', []
    return 'NO-GO', ['CI entirely <= 0']


def build_denominators(summary, save):
    cold_mean = (summary.get('cold') or {}).get('mean_usd')
    parseable_cards = sum(
        1 for row in summary.get('pairs') or [] if row.get('cold_parseable'))
    pair_per_card = (
        None if not parseable_cards else
        float(summary.get('total_usd') or 0) / parseable_cards
    )
    one_shot = cold_mean
    vs_h2675 = None if one_shot is None else one_shot / H2675_USD - 1.0
    pair_vs = None if pair_per_card is None else pair_per_card / H2675_USD - 1.0
    return {
        'A_pair_per_unique_not_scored': {
            'usd': pair_per_card,
            'vs_h2675': pair_vs,
            'label': 'not scored',
        },
        'B_paired_incremental_primary': {
            'point_save': save.get('point_save'),
            'ci': save.get('ci'),
            'dollar_mean': save.get('dollar_mean'),
            'dollar_ci': save.get('dollar_ci'),
            'totals_save': save.get('totals_save'),
        },
        'C_oneshot_cold_context': {
            'usd': one_shot,
            'vs_h2675': vs_h2675,
            'h2675_usd': H2675_USD,
        },
        'amortized': {
            'R2': amortized(save.get('complete_cold_mean') or cold_mean,
                            save.get('complete_warm_mean'), 2),
            'R5': amortized(save.get('complete_cold_mean') or cold_mean,
                            save.get('complete_warm_mean'), 5),
            'R10': amortized(save.get('complete_cold_mean') or cold_mean,
                             save.get('complete_warm_mean'), 10),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--seal', action='store_true')
    args = ap.parse_args(argv)
    if not args.verify and not args.seal:
        args.verify = True
        args.seal = True
    if args.verify:
        replay = verify_conclusions()
        print('CONCLUSIONS replay OK flash_vs_h2675=%.3f same_card=%.3f'
              % (replay['flash_vs_h2675'], replay['flash_same_card_save']))
    if args.seal:
        selected, pool, banned = select_50()
        path, body = write_manifest(selected)
        print('sealed n=%d leftover_pool=%d excluded=%d path=%s sha=%s'
              % (len(body['keys']), len(pool), len(banned), path,
                 body['manifest_sha256'][:12]))
        overlap = set(body['keys']) & banned
        if overlap:
            raise VerifyError('overlap after write: %s' % sorted(overlap)[:8])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
