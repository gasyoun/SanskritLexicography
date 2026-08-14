#!/usr/bin/env python
"""H2686 Track D driver: QE liveness + gold calibration + live two-arm retrieval.

    python src/pwg_tm_w2_run.py --probe
    python src/pwg_tm_w2_run.py --all --gold-limit 80 --n-per-class 3
"""
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

import nn_api  # noqa: E402
import tm_grade  # noqa: E402
import tm_retrieval_eval as ev  # noqa: E402

RECEIPT = os.path.join(HERE, 'QE_BACKEND_RECEIPT.json')


def write_receipt(extra=None):
    rec = {
        'schema': 'pwg.tm.qe.receipt.v1',
        'labse': nn_api.qe_backend_receipt('labse'),
        'comet': nn_api.qe_backend_receipt('comet'),
        'proxy_rho_preliminary': tm_grade.PROXY_RHO_PRELIMINARY,
        'repair': None,
    }
    if extra:
        rec.update(extra)
    with open(RECEIPT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return rec


def probe_deepseek():
    key, src = ev.load_deepseek_key()
    if not key:
        return {'available': False, 'reason': 'no DEEPSEEK_API_KEY', 'key_src': None}
    _tr, judge, ledger = ev.make_deepseek_fns(key)
    judged = judge({
        'source_string': 'Feuer, Gott des Feuers',
        'qe_reference_free': True,
        'fragment_id': 'probe',
    }, {'text': 'огонь, бог огня'})
    return {
        'available': judged.get('quality') is not None,
        'key_src': 'environ' if src == 'environ' else 'file',
        'model': ev.DEEPSEEK_MODEL,
        'probe_quality': judged.get('quality'),
        'probe_equivalence': judged.get('equivalence'),
        'ledger_calls': len(ledger),
        'cost_usd': sum(float(r.get('cost_usd') or 0) for r in ledger),
        'error': ledger[-1].get('error') if ledger else None,
    }


def cmd_probe(_a):
    rec = write_receipt()
    ds = probe_deepseek()
    rec['deepseek'] = ds
    rec['repair'] = None
    if rec['labse']['available']:
        rec['active_backend'] = 'labse'
    elif ds.get('available'):
        rec['active_backend'] = 'deepseek'
        rec['repair'] = 'labse failed (process-local load); deepseek-v4-flash judge serves'
    else:
        rec['active_backend'] = None
        rec['repair'] = 'labse failed and deepseek probe failed'
    write_receipt({'deepseek': ds, 'repair': rec['repair'],
                   'active_backend': rec.get('active_backend')})
    print(json.dumps({
        'labse': rec['labse']['available'],
        'comet': rec['comet']['available'],
        'deepseek': ds.get('available'),
        'active_backend': rec.get('active_backend'),
        'repair': rec.get('repair'),
        'probe_quality': ds.get('probe_quality'),
        'error': ds.get('error'),
    }, ensure_ascii=False, indent=2))
    return 0 if rec.get('active_backend') else 2


def cmd_all(a):
    rc = cmd_probe(a)
    rec = json.load(open(RECEIPT, encoding='utf-8'))
    if not rec.get('active_backend'):
        print('no genuine QE backend; stopping after one repair')
        return rc

    freeze = argparse.Namespace(
        sample=ev.DEFAULT_SAMPLE,
        adjudication=ev.DEFAULT_ADJ,
        n_per_class=a.n_per_class,
        out=ev.DEFAULT_BATCH,
        manifest=ev.DEFAULT_MANIFEST,
    )
    ev.cmd_freeze(freeze)

    qe_backend = rec['active_backend']
    gold = ev.DEFAULT_GRADE_GOLD
    if a.gold_limit:
        rows = ev.load_jsonl(gold)
        # deterministic: first N by id, preserving grade mix by taking
        # round-robin from A/B/C after id sort
        by = {'A': [], 'B': [], 'C': []}
        for r in sorted(rows, key=lambda x: x.get('id', 0)):
            g = r.get('grade')
            if g in by:
                by[g].append(r)
        picked = []
        i = 0
        while len(picked) < a.gold_limit and any(by.values()):
            bucket = ['A', 'B', 'C'][i % 3]
            if by[bucket]:
                picked.append(by[bucket].pop(0))
            i += 1
        gold = os.path.join(HERE, 'GRADE_GOLD_CALIB_SLICE.jsonl')
        ev.write_jsonl(gold, picked)
        print('gold slice n=%d -> %s' % (len(picked), gold))

    cal = argparse.Namespace(gold=gold, qe=qe_backend, out=tm_grade.DEFAULT_CALIBRATION_MD)
    tm_grade.cmd_calibrate_gold(cal)

    run = argparse.Namespace(
        batch=ev.DEFAULT_BATCH,
        engine=ev.ENGINE_DEEPSEEK,
        model=ev.DEEPSEEK_MODEL,
        sample=ev.DEFAULT_SAMPLE,
        publication=ev.DEFAULT_PUBLICATION,
        out=ev.DEFAULT_OUT,
        live_json=ev.DEFAULT_LIVE_JSON,
        ledger=ev.DEFAULT_LEDGER,
    )
    return ev.cmd_run(run)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--all', dest='do_all', action='store_true')
    ap.add_argument('--gold-limit', dest='gold_limit', type=int, default=0)
    ap.add_argument('--n-per-class', dest='n_per_class', type=int, default=3)
    a = ap.parse_args()
    if a.do_all:
        return cmd_all(a)
    return cmd_probe(a)


if __name__ == '__main__':
    sys.exit(main())
