#!/usr/bin/env python
"""Hermetic regression tests for truthful PWG usage accounting."""
import json
import os
import tempfile

import call_reservation as cr
import usage_accounting as ua


TOKENS = {
    'input_tokens': 41_320,
    'output_tokens': 4_263,
    'cache_creation_tokens': 116_439,
    'cache_read_tokens': 974_856,
}
HERE = os.path.dirname(os.path.abspath(__file__))


def test_counterfactuals():
    standard = ua.build(TOKENS, billing_mode=ua.API_STANDARD)
    batch = ua.build(TOKENS, billing_mode=ua.API_BATCH)
    assert standard['list_equivalent_usd'] == 1.964993
    assert standard['observed_cash_usd'] == 1.964993
    assert batch['list_equivalent_usd'] == 1.964993
    assert batch['observed_cash_usd'] == 0.9824965


def test_max_credit_classification():
    wrapper = {
        'usage': {
            'input_tokens': TOKENS['input_tokens'],
            'output_tokens': TOKENS['output_tokens'],
            'cache_creation_input_tokens': TOKENS['cache_creation_tokens'],
            'cache_read_input_tokens': TOKENS['cache_read_tokens'],
        },
        'total_cost_usd': 1.965,
    }
    claimed = cr.telemetry_from_cli_wrapper(
        wrapper, max_agent_sdk_credit=True, credit_claimed=True,
        credit_claim_evidence='support-credit-claim:2026-08')
    accounting = claimed['accounting']
    assert accounting['usage_evaluable'] is True
    assert accounting['billing_mode'] == ua.MAX_AGENT_SDK_CREDIT
    assert accounting['observed_cash_usd'] is None
    assert accounting['list_equivalent_usd'] == 1.965
    assert accounting['credit_equivalent_usd'] == 1.965
    assert claimed['cost_evaluable'] is False and claimed['observed_cost_usd'] == 0

    unknown = cr.telemetry_from_cli_wrapper(
        wrapper, max_agent_sdk_credit=True, credit_claimed=True)
    assert unknown['accounting']['billing_mode'] == ua.UNKNOWN_GATEWAY
    assert unknown['accounting']['list_equivalent_usd'] is None
    assert unknown['accounting']['credit_equivalent_usd'] is None


def test_router_tokens_and_bad_usage():
    router = ua.build(TOKENS, billing_mode=ua.UNKNOWN_GATEWAY)
    assert router['usage_evaluable'] is True
    assert router['observed_cash_usd'] is None
    assert router['list_equivalent_usd'] is None
    for bad in (None, {}, {'input_tokens': 1}, dict(TOKENS, output_tokens=-1)):
        value = ua.build(bad, billing_mode=ua.UNKNOWN_GATEWAY)
        assert value['usage_evaluable'] is False


def test_legacy_ledger_bytes_unchanged():
    usage = {
        'input_tokens': 1, 'output_tokens': 2, 'cache_read_tokens': 3,
        'cache_creation_tokens': 4, 'subagent_tokens': 10,
        'observed_cost_usd': 0.5, 'cost_evaluable': True,
        'finalized_calls': 1, 'unevaluable_calls': 0, 'pending_calls': 0,
    }
    value = {'schema': cr.SCHEMA, 'runs': {'legacy': {
        'max_calls': 1, 'calls_spent': 1, 'next_ordinal': 2,
        'reservations': [{
            'reservation_id': 'legacy-id', 'ordinal': 1, 'purpose': 'legacy',
            'finalized': True, 'telemetry': {
                'cost_evaluable': True, 'input_tokens': 1, 'output_tokens': 2,
                'cache_read_tokens': 3, 'cache_creation_tokens': 4,
                'subagent_tokens': 10, 'observed_cost_usd': 0.5,
            },
        }], 'usage': usage,
    }}}
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'ledger.json')
        original = (json.dumps(value, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
        with open(path, 'wb') as handle:
            handle.write(original)
        cr.CallReservationLedger.open_existing(path, 'legacy').snapshot()
        with open(path, 'rb') as handle:
            assert handle.read() == original


def test_new_finalization_only_emits_accounting():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = cr.CallReservationLedger(os.path.join(tmp, 'ledger.json'), 'mixed', 2)
        legacy = ledger.reserve('legacy')
        ledger.finalize(legacy, {
            'cost_evaluable': True, 'observed_cost_usd': 0.1,
            'input_tokens': 1, 'output_tokens': 1,
        })
        modern = ledger.reserve('modern')
        ledger.finalize(modern, ua.legacy_telemetry(
            ua.build(TOKENS, billing_mode=ua.API_BATCH)))
        rows = ledger.snapshot()['reservations']
        assert 'accounting' not in rows[0]['telemetry']
        assert rows[1]['telemetry']['accounting']['billing_mode'] == ua.API_BATCH
        ledger.finalize(modern, rows[1]['telemetry'])  # exact-once replay


def test_h2539_derived_receipt_binds_immutable_envelopes():
    root = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'pwg_ru', 'h2539')
    with open(os.path.join(root, 'GATEWAY_USAGE_ACCOUNTING_11-08-2026.json'),
              encoding='utf-8') as handle:
        receipt = json.load(handle)
    totals = {name: 0 for name in TOKENS}
    aliases = {
        'input_tokens': 'input_tokens', 'output_tokens': 'output_tokens',
        'cache_creation_tokens': 'cache_creation_input_tokens',
        'cache_read_tokens': 'cache_read_input_tokens',
    }
    for source in receipt['source_envelopes']:
        with open(os.path.join(root, source['path']), encoding='utf-8') as handle:
            envelope = json.load(handle)
        assert envelope['saved_envelope_sha256'] == source['saved_envelope_sha256']
        usage = envelope['attested_usage_totals']
        for target, raw in aliases.items():
            totals[target] += usage[raw]
    assert totals == TOKENS
    assert ua.validate(receipt['accounting'])['usage_evaluable'] is True
    assert receipt['cost_evaluable'] is False and receipt['observed_cash_usd'] is None


TESTS = (
    test_counterfactuals,
    test_max_credit_classification,
    test_router_tokens_and_bad_usage,
    test_legacy_ledger_bytes_unchanged,
    test_new_finalization_only_emits_accounting,
    test_h2539_derived_receipt_binds_immutable_envelopes,
)


def main():
    for test in TESTS:
        test()
    print('usage_accounting_selftest: PASS (%d/%d)' % (len(TESTS), len(TESTS)))


if __name__ == '__main__':
    main()
