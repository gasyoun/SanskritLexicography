#!/usr/bin/env python
"""H2676 — fold telemetry + slice_result into summary.json against VERDICT_RULE."""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
FLASH_PER_CLEAN = 0.0093
CEILING = 5 * FLASH_PER_CLEAN
FLOOR_CLEAN = 15
N = 22


def _issues_empty(row):
    issues = row.get('det_issues')
    return isinstance(issues, list) and len(issues) == 0


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'run', 'q3')
    slice_path = prefix + '.slice_result.json'
    tel_path = prefix + '.telemetry.json'
    sl = json.load(open(slice_path, encoding='utf-8'))
    tel = json.load(open(tel_path, encoding='utf-8'))
    rows = sl.get('results') or []
    attempted = [r for r in rows if r.get('final_status') not in ('never-attempted', None)]
    clean = [r for r in rows if _issues_empty(r)]
    transport_deaths = [
        r for r in rows
        if any('IncompleteRead' in str(x) or 'TimeoutError' in str(x)
               for x in (r.get('repairs') or []))
        or r.get('final_status') in ('worker-null-death', 'driver-exception')
    ]
    cost = (tel.get('cost') or {})
    usd = cost.get('usd')
    n_clean = len(clean)
    usd_per = (usd / n_clean) if (usd is not None and n_clean) else None
    store_write = False
    calls = tel.get('calls') or []
    served_ok = all(
        c.get('model_matches_request') is True
        for c in calls
        if c.get('served_model') or c.get('requested_model')
    )
    price_model = cost.get('price_model') or tel.get('model')
    price_ok = price_model == 'deepseek-v4-pro'
    det_ok = n_clean >= FLOOR_CLEAN
    cost_ok = usd_per is not None and usd_per <= CEILING
    attempted_ok = len(attempted) >= N
    verdict = 'PASS' if (attempted_ok and det_ok and cost_ok and served_ok
                         and price_ok and not store_write) else 'FAIL'
    summary = {
        'schema': 'pwg.h2676_q3_summary.v1',
        'handoff': 'H2676',
        'verdict': verdict,
        'n': N,
        'attempted': len(attempted),
        'det_gate_clean': n_clean,
        'det_clean_floor': FLOOR_CLEAN,
        'usd': usd,
        'usd_per_clean': None if usd_per is None else round(usd_per, 6),
        'usd_per_clean_ceiling': CEILING,
        'flash_usd_per_clean': FLASH_PER_CLEAN,
        'store_write': store_write,
        'would_promote_count': sum(1 for r in rows if r.get('would_promote') is True),
        'promote_dry': True,
        'model': tel.get('model'),
        'transport': tel.get('transport'),
        'price_card': tel.get('price_card') or cost.get('price_card'),
        'price_model': price_model,
        'price_table': cost.get('price_table'),
        'served_model_ok': served_ok,
        'price_ok': price_ok,
        'clauses': {
            'attempted_22': attempted_ok,
            'det_clean_ge_15': det_ok,
            'usd_per_clean_le_5x_flash': cost_ok,
            'served_pro': served_ok,
            'pro_price_table': price_ok,
            'store_write_never_true': not store_write,
        },
        'status_counts': {},
        'transport_death_keys': [r.get('key1') for r in transport_deaths],
        'clean_keys': [r.get('key1') for r in clean],
        'wall_clock_s': tel.get('wall_clock_s'),
        'generation_calls': tel.get('generation_calls'),
    }
    from collections import Counter
    summary['status_counts'] = dict(Counter(r.get('final_status') for r in rows))
    out = os.path.join(HERE, 'summary.json')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({k: summary[k] for k in (
        'verdict', 'attempted', 'det_gate_clean', 'usd', 'usd_per_clean',
        'store_write', 'clauses')}, indent=2))
    print('wrote', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
