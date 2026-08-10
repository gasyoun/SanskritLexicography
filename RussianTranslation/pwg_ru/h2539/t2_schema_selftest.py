"""Selftest the H2539 Ticket 2 final-output schema BEFORE it is frozen into a ticket.

An invalid or too-loose schema discovered after `prepare-external` would waste the
only remaining reservation, so every accept/reject case is proven offline first.
Run: python pwg_ru/h2539/t2_schema_selftest.py
"""
import copy
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / 'evidence' / 't2_schema.json'
sys.path.insert(0, str(HERE.parents[1] / 'src' / 'pilot'))

from gateway_route import validate_complete_schema  # noqa: E402

SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))

GOOD = {
    "schema_marker": "pwg_ru.canary_final.v1",
    "provenance": {
        "provenance_class": "synthetic_control",
        "route": "router-cheap-agent",
        "model": "claude-opus-5",
        "raw_sha256": "152a3eec0b6b9c167a91950d649a10d1f2d413f96c076e17f01859a2eaa9058d",
        "portrait_sha256": "a43235e366573182884922f7fd42a2072c3148cef27de234d24c92fc75cbc4c7",
        "source_senses": 3,
        "promotable": False,
    },
    "cards": [{
        "key1": "dq_canary_puregloss",
        "iast": "",
        "notes": "",
        "records": [{
            "h": "0",
            "grammar": "",
            "senses": [
                {"tag": "1", "german": "{%eine Schildkröte%}.",
                 "russian": "черепаха", "equivalence_type": "equivalent",
                 "source_type": "lexicographic", "government": []},
                {"tag": "2", "german": "{%ein kleiner Fisch%}.",
                 "russian": "небольшая рыба", "equivalence_type": "explanatory",
                 "source_type": "lexicographic", "government": []},
                {"tag": "3", "german": "{%eine Wasserpflanze%}.",
                 "russian": "водное растение", "equivalence_type": "explanatory",
                 "source_type": "lexicographic", "government": []},
            ],
        }],
    }],
}


def mutate(fn):
    payload = copy.deepcopy(GOOD)
    fn(payload)
    return payload


def senses(payload):
    return payload['cards'][0]['records'][0]['senses']


BAD_CASES = {
    'dropped_sense': lambda p: senses(p).pop(1),
    'merged_senses': lambda p: (senses(p).pop(2), senses(p)[1].update(
        russian='небольшая рыба; водное растение')),
    'extra_sense': lambda p: senses(p).append(copy.deepcopy(senses(p)[2])),
    'untranslated_german': lambda p: senses(p)[0].update(russian='eine Schildkröte'),
    'latin_leak_in_russian': lambda p: senses(p)[0].update(russian='черепаха (Testudo)'),
    'empty_russian': lambda p: senses(p)[0].update(russian=''),
    'placeholder_leak': lambda p: senses(p)[0].update(russian='{T1} черепаха'),
    'german_markup_stripped': lambda p: senses(p)[0].update(german='eine Schildkröte.'),
    'sense_order_swapped': lambda p: senses(p).insert(0, senses(p).pop(2)),
    'key_drift': lambda p: p['cards'][0].update(key1='dq_canary_puregloss~~h0_zz_pw'),
    'promotion_claim': lambda p: p['provenance'].update(promotable=True),
    'provenance_class_drift': lambda p: p['provenance'].update(provenance_class='real'),
    'model_drift': lambda p: p['provenance'].update(model='claude-sonnet-5'),
    'raw_hash_drift': lambda p: p['provenance'].update(raw_sha256='0' * 64),
    'source_senses_drift': lambda p: p['provenance'].update(source_senses=2),
    'extra_toplevel_field': lambda p: p.update(thinking='hidden'),
    'extra_sense_field': lambda p: senses(p)[0].update(comment='x'),
    'missing_provenance': lambda p: p.pop('provenance'),
    'invented_government': lambda p: senses(p)[0].update(government=['loc.']),
    'second_card': lambda p: p['cards'].append(copy.deepcopy(p['cards'][0])),
    'second_record': lambda p: p['cards'][0]['records'].append(
        copy.deepcopy(p['cards'][0]['records'][0])),
    'bad_equivalence_enum': lambda p: senses(p)[0].update(equivalence_type='gloss'),
    'wrong_marker': lambda p: p.update(schema_marker='pwg_ru.final.v1'),
}


def main():
    failures = []
    try:
        validate_complete_schema(GOOD, SCHEMA)
        print('PASS  accepts the golden 3/3 instance')
    except ValueError as exc:
        failures.append('golden instance REJECTED: %s' % exc)
        print('FAIL  golden instance rejected: %s' % exc)

    for name, fn in BAD_CASES.items():
        payload = mutate(fn)
        try:
            validate_complete_schema(payload, SCHEMA)
        except ValueError as exc:
            print('PASS  rejects %-24s (%s)' % (name, str(exc)[:70]))
        else:
            failures.append('defect NOT caught: %s' % name)
            print('FAIL  accepted defective instance: %s' % name)

    print('\n%d/%d checks passed' % (
        1 + len(BAD_CASES) - len(failures), 1 + len(BAD_CASES)))
    if failures:
        print('SELFTEST FAILED')
        return 1
    print('SELFTEST OK — schema safe to freeze into a ticket')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
