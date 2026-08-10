#!/usr/bin/env python
"""RED→GREEN and mutation matrix for the H2554 canary contract."""
import copy
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gateway_canary_contract as contract  # noqa: E402
from gateway_route import validate_complete_schema  # noqa: E402


def senses(value):
    return value['cards'][0]['records'][0]['senses']


def old_prompt_instance(prompt):
    lines = [line for line in prompt.splitlines()
             if line.startswith('— ') and '{%' in line]
    payload = json.loads(json.dumps(contract.prompt_derived_instance(
        contract.render_prompt())))
    for target, line in zip(senses(payload), lines):
        target['german'] = line
    payload['schema_marker'] = 'pwg_ru.canary_final.v1'
    return payload


def test_h2539_exact_red_then_generated_green():
    root = os.path.join(REPO, 'pwg_ru', 'h2539', 'evidence')
    old_request = json.load(open(os.path.join(root, 't2_request.json'),
                                 encoding='utf-8'))
    old_schema = json.load(open(os.path.join(root, 't2_schema.json'),
                                encoding='utf-8'))
    old_instance = old_prompt_instance(old_request['prompt'])
    assert senses(old_instance)[0]['german'] == '— 1〉 {%eine Schildkröte%}.'
    try:
        validate_complete_schema(old_instance, old_schema)
        raise AssertionError('H2539 contradiction did not reproduce RED')
    except ValueError as exc:
        assert '{%eine Schildkröte%}.' in str(exc)

    request, schema = contract.request_and_schema()
    derived = contract.prompt_derived_instance(request['prompt'])
    validate_complete_schema(derived, schema)
    assert senses(derived)[0]['german'] == '— 1〉 {%eine Schildkröte%}.'


def test_prompt_derived_mutations_fail_closed():
    request, schema = contract.request_and_schema()
    good = contract.prompt_derived_instance(request['prompt'])
    mutations = {
        'sense_number': lambda p: senses(p)[0].update(tag='9'),
        'markup_span': lambda p: senses(p)[0].update(
            german='— 1〉 eine Schildkröte.'),
        'ordering': lambda p: senses(p).insert(0, senses(p).pop()),
        'key': lambda p: p['cards'][0].update(key1='other'),
        'provenance_hash': lambda p: p['provenance'].update(
            raw_sha256='0' * 64),
        'cardinality': lambda p: senses(p).pop(),
    }
    for name, mutate in mutations.items():
        bad = copy.deepcopy(good)
        mutate(bad)
        try:
            validate_complete_schema(bad, schema)
            raise AssertionError('mutation accepted: %s' % name)
        except ValueError:
            pass


def test_prompt_fixture_is_unique_and_schema_has_no_handwritten_copy():
    request, schema = contract.request_and_schema()
    parsed = contract.fixture_from_prompt(request['prompt'])
    assert parsed == contract.CANARY_FIXTURE
    assert json.dumps(schema, ensure_ascii=False).count(
        '— 1〉 {%eine Schildkröte%}.') == 1


TESTS = [
    test_h2539_exact_red_then_generated_green,
    test_prompt_derived_mutations_fail_closed,
    test_prompt_fixture_is_unique_and_schema_has_no_handwritten_copy,
]


def selftest():
    for test in TESTS:
        test()
        print('  PASS: ' + test.__name__)
    print('gateway_canary_contract_selftest: PASS (%d/%d groups)' % (
        len(TESTS), len(TESTS)))
    return True


if __name__ == '__main__':
    sys.exit(0 if selftest() else 1)
