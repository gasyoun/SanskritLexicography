#!/usr/bin/env python
r"""Cloud-lane window entry — importable, no headless CLI (H2175 step 14, R2.4).

Lane C (the Anthropic routine) translates IN-SESSION: the routine session itself is
the model, so there is no CLI to spawn and no config-dir fingerprint to bind. This
module gives that lane the SAME shapes the rest of the pipeline speaks:

  * wf_output — ``{meta: {selected_keys, gen_model, lang, execution{...}},
    summary: {usage}, results: [{key, card}]}`` — readable by
    promote_final_cards.collect_cards and judgeable by canary_gate.judge_payload;
  * per-call usage telemetry rows with the cache-token split
    (call_reservation.TOKEN_FIELDS vocabulary), appended to a JSONL ledger.

The translation itself is INJECTED (``translate_fn(item) -> (card, usage)``): in
the routine, that is the session's own generation; in tests, a fixture. This module
never calls a model and is NOT scheduled in Wave 1 (R2.4 wires it in Wave 2).

Route honesty: ``execution_route='anthropic-routine-in-session'`` — deliberately
NOT the headless contract, so execution_contract.validate_profile would refuse it.
Lane C's integrity story is different by design (R3.3): the window lands as a
gated PR; CI re-runs the deterministic gates (ci gates.yml) and requires this
module's usage block; nothing reaches tm/ except through the promoter after that.
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

SCHEMA = 'pwg.cloud_window.v1'
EXECUTION_ROUTE = 'anthropic-routine-in-session'

USAGE_KEYS = ('input_tokens', 'output_tokens', 'cache_creation_input_tokens',
              'cache_read_input_tokens')


def _sum_usage(rows):
    total = {k: 0 for k in USAGE_KEYS}
    cost = 0.0
    evaluable = True
    for r in rows:
        u = r.get('usage') or {}
        for k in USAGE_KEYS:
            total[k] += int(u.get(k) or 0)
        if u.get('observed_cost_usd') is None:
            evaluable = False
        else:
            cost += float(u['observed_cost_usd'])
    total['observed_cost_usd'] = round(cost, 6) if evaluable else None
    total['cost_evaluable'] = evaluable
    return total


def run_cloud_window(window_id, items, translate_fn, *, model_identifier,
                     profile_slot='routine1', lang='ru', gen_model=None,
                     out_dir=None, parked_env=None):
    """Drain ONE window in-session. Returns (wf_output_dict, usage_rows, parked).

    items: [{'key': subcard_key, ...input material...}]. translate_fn(item) ->
    (card_dict, usage_dict) — card in the pwg_ru_final_card shape, usage carrying
    the USAGE_KEYS split (+ observed_cost_usd when known). A translate_fn that
    RAISES parks the item (R4.2) and the window continues — ambiguity never
    blocks the lane."""
    import parked_queue
    results, usage_rows, parked = [], [], []
    for item in items:
        key = item['key']
        t0 = time.time_ns()
        try:
            card, usage = translate_fn(item)
        except Exception as exc:  # noqa: BLE001 — R4.2: park, don't block the lane
            parked.append(parked_queue.park(
                key, 'cloud translate_fn failed: %s' % str(exc).splitlines()[0],
                source='cloud_window', lane='routine', env=parked_env))
            continue
        t1 = time.time_ns()
        results.append({'key': key, 'card': card})
        usage_rows.append({'schema': 'pwg.cloud_call.v1', 'key': key,
                           'reserved_at_ns': t0, 'finalized_at_ns': t1,
                           'duration_ms': (t1 - t0) / 1e6,
                           'usage': dict(usage or {})})
    wf = {
        'schema': SCHEMA,
        'meta': {
            'selected_keys': [i['key'] for i in items],
            'gen_model': gen_model or model_identifier,
            'lang': lang,
            'generator': 'cloud_window.py',
            'schema_version': SCHEMA,
            'root': window_id,
            'execution': {
                'profile_slot': profile_slot,
                'execution_route': EXECUTION_ROUTE,
                'executor_lane': 'cloud-window',
                'validation_method': 'ci-gates+promoter',
                'config_dir_fingerprint': None,     # no CLI config dir exists here
                'model_identifier': model_identifier,
            },
        },
        'summary': {'usage': _sum_usage(usage_rows),
                    'translated': len(results), 'parked': len(parked)},
        'results': results,
    }
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        wf_path = os.path.join(out_dir, 'wf_output.%s.json' % window_id)
        with open(wf_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(wf, f, ensure_ascii=False, indent=1)
        ledger = os.path.join(out_dir, '%s.usage.jsonl' % window_id)
        with open(ledger, 'a', encoding='utf-8', newline='\n') as f:
            for row in usage_rows:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
        wf['_wf_path'], wf['_usage_path'] = wf_path, ledger
    return wf, usage_rows, parked


def selftest():
    import tempfile
    import promote_final_cards as pfc

    def fake_translate(item):
        if item['key'].endswith('boom'):
            raise ValueError('unclassifiable german construction')
        card = {'iast': 'aṃśa', 'records': [
            {'h': item['key'], 'grammar': 'm',
             'senses': [{'tag': 'sense%d' % n, 'german': 'Teil',
                         'russian': 'часть, доля'} for n in (1, 2, 3)]}]}
        usage = {'input_tokens': 100, 'output_tokens': 50,
                 'cache_creation_input_tokens': 10, 'cache_read_input_tokens': 90,
                 'observed_cost_usd': 0.01}
        return card, usage

    with tempfile.TemporaryDirectory() as td:
        items = [{'key': 'r~~a'}, {'key': 'r~~b'}, {'key': 'r~~boom'}]
        wf, rows, parked = run_cloud_window(
            'cw_test', items, fake_translate, model_identifier='claude-sonnet-5',
            out_dir=td, parked_env={'PWG_PARKED_DIR': os.path.join(td, 'parked')})
        # (1) shapes: collect_cards reads the wf file exactly like a CLI window's
        best, conflicts, nulls = pfc.collect_cards([wf['_wf_path']])
        assert set(best) == {'r~~a', 'r~~b'} and not conflicts and not nulls
        assert best['r~~a']['meta']['execution']['execution_route'] == EXECUTION_ROUTE
        # (2) the promoter's row generator yields RU rows from a cloud card
        rows_ru = list(pfc.rows_for('r~~a', best['r~~a'], 'ai_translated',
                                    'claude-sonnet-5'))
        assert len(rows_ru) == 3 and all(r['ru'] for r in rows_ru)
        # (3) usage: cache split summed; cost evaluable
        u = wf['summary']['usage']
        assert u['cache_read_input_tokens'] == 180 and u['observed_cost_usd'] == 0.02
        assert u['cost_evaluable'] is True
        # (4) a raising translate_fn parks (R4.2) and the window completes
        assert len(parked) == 1 and wf['summary']['parked'] == 1
        assert os.path.exists(parked[0])
        # (5) usage ledger rows carry wall stamps for §270 differencing
        lrows = [json.loads(l) for l in open(wf['_usage_path'], encoding='utf-8')]
        assert all(r['finalized_at_ns'] > r['reserved_at_ns'] for r in lrows)
        # (6) a missing cost on ANY call makes the summary UNEVALUABLE, never zero
        def no_cost(item):
            card, usage = fake_translate(item)
            usage.pop('observed_cost_usd')
            return card, usage
        wf2, _r2, _p2 = run_cloud_window('cw2', [{'key': 'r~~c'}], no_cost,
                                         model_identifier='claude-sonnet-5')
        assert wf2['summary']['usage']['observed_cost_usd'] is None
        assert wf2['summary']['usage']['cost_evaluable'] is False
    print('cloud_window selftest: PASS (collect_cards + rows_for compatibility, '
          'cache-split usage, park-on-failure, wall stamps, cost fail-closed)')
    return 0


if __name__ == '__main__':
    sys.exit(selftest())
