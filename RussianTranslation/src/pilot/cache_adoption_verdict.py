#!/usr/bin/env python
"""H2704 — two-lane ADOPT / NO-GO from sealed summaries. No paid calls."""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
RT = os.path.dirname(os.path.dirname(HERE))

import cache_identity as ident  # noqa: E402

EXP_DIR = os.path.join(RT, 'experiments', 'pwg_cache_economy')
H2676_USD = 0.01991
H2675_USD = 0.000873
ADOPT_FRACTION = 0.80  # at least 20% lower than baseline


def load_json(path):
    with open(path, encoding='utf-8') as handle:
        return json.loads(handle.read())


def lane_ok(summary, parseable_min, denom):
    parseable = int(summary.get('parseable') or 0)
    verdict = summary.get('prep_lane_verdict') or summary.get('generation_lane_verdict')
    return {
        'verdict': verdict,
        'parseable': parseable,
        'parseable_min': parseable_min,
        'denom': denom,
        'parseable_ok': parseable >= parseable_min,
        'usd_per_unique_clean': summary.get('usd_per_unique_clean'),
        'total_usd': summary.get('total_usd'),
        'unique_clean': summary.get('unique_clean_cards'),
    }


def economy_pass(observed, baseline):
    if observed is None or baseline is None or baseline <= 0:
        return False, None
    ratio = observed / baseline
    return ratio <= ADOPT_FRACTION, ratio


def decide(gen, prep, hashes_equal, l3_status):
    gen_econ, gen_ratio = economy_pass(gen['usd_per_unique_clean'], H2676_USD)
    prep_econ, prep_ratio = economy_pass(prep['usd_per_unique_clean'], H2675_USD)
    reasons = []
    if gen['verdict'] != 'PASS':
        reasons.append('generation_lane_not_pass')
    if prep['verdict'] != 'PASS':
        reasons.append('prep_lane_not_pass')
    if not gen['parseable_ok']:
        reasons.append('generation_parseable')
    if not prep['parseable_ok']:
        reasons.append('prep_parseable')
    if not gen_econ:
        reasons.append('generation_economy_lt_20pct')
    if not prep_econ:
        reasons.append('prep_economy_lt_20pct')
    if not hashes_equal:
        reasons.append('canonical_hash_change')
    verdict = 'ADOPT' if not reasons else 'NO-GO'
    return {
        'schema': 'pwg.cache_adoption_verdict.v1',
        'handoff': 'H2704',
        'verdict': verdict,
        'reasons': reasons,
        'generation': dict(gen, economy_pass=gen_econ, vs_baseline=gen_ratio,
                           baseline_usd=H2676_USD),
        'prep': dict(prep, economy_pass=prep_econ, vs_baseline=prep_ratio,
                     baseline_usd=H2675_USD),
        'canonical_hashes_equal': hashes_equal,
        'l3': l3_status,
        'default_model_unchanged': True,
        'canonical_promotion': False,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--gen-summary', default=os.path.join(
        EXP_DIR, 'h2703_generation', 'run', 'summary.json'))
    ap.add_argument('--prep-summary', default=os.path.join(
        EXP_DIR, 'h2704_prep', 'prep50', 'run', 'summary.json'))
    ap.add_argument('--l3-summary', default=os.path.join(
        EXP_DIR, 'h2704_prep', 'l3', 'run', 'summary.json'))
    ap.add_argument('--prep-hash', default=os.path.join(
        EXP_DIR, 'h2704_prep', 'prep50', 'canonical_hash_after.json'))
    ap.add_argument('--out', default=os.path.join(
        EXP_DIR, 'h2704_prep', 'ADOPTION.json'))
    args = ap.parse_args(argv)

    gen = lane_ok(load_json(args.gen_summary), 42, 44)
    prep = lane_ok(load_json(args.prep_summary), 95, 100)
    hashes = {'equal': False}
    if os.path.isfile(args.prep_hash):
        hashes = load_json(args.prep_hash)
    l3_status = {'ran': False, 'reason': 'not_present'}
    if os.path.isfile(args.l3_summary):
        l3 = load_json(args.l3_summary)
        l3_status = {
            'ran': True,
            'verdict': l3.get('prep_lane_verdict') or l3.get('generation_lane_verdict'),
            'parseable': l3.get('parseable'),
            'total_usd': l3.get('total_usd'),
        }
    elif os.path.isfile(os.path.join(EXP_DIR, 'h2704_prep', 'L3_SKIP.json')):
        l3_status = load_json(os.path.join(EXP_DIR, 'h2704_prep', 'L3_SKIP.json'))
    body = decide(gen, prep, bool(hashes.get('equal')), l3_status)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(body))
    print('verdict=%s reasons=%s' % (body['verdict'], ','.join(body['reasons']) or 'none'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
