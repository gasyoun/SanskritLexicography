"""One-source contract for the offline router.cheap PWG canary (H2554).

The canonical fixture below is the only authored copy of semantic literals.
Both the operator prompt and the complete Draft 2020-12 schema are rendered
from it.  Test instances are reconstructed from the rendered prompt, never
from schema constants, so prompt/schema divergence is observable offline.
"""
from __future__ import annotations

import copy
import json
import re


CONTRACT_SCHEMA = 'pwg.router_cheap_canary_contract.v2'
PROMPT_FIXTURE_BEGIN = '=== CANONICAL CANARY FIXTURE JSON ==='
PROMPT_FIXTURE_END = '=== END CANONICAL CANARY FIXTURE JSON ==='

CANARY_FIXTURE = {
    'schema': CONTRACT_SCHEMA,
    'schema_marker': 'pwg_ru.canary_final.v2',
    'key1': 'dq_canary_puregloss',
    'model': 'claude-opus-5',
    'raw_sha256': '152a3eec0b6b9c167a91950d649a10d1f2d413f96c076e17f01859a2eaa9058d',
    'portrait_sha256': 'a43235e366573182884922f7fd42a2072c3148cef27de234d24c92fc75cbc4c7',
    'senses': [
        {'tag': '1', 'german': '— 1〉 {%eine Schildkröte%}.',
         'russian': 'черепаха', 'equivalence_type': 'equivalent'},
        {'tag': '2', 'german': '— 2〉 {%ein kleiner Fisch%}.',
         'russian': 'небольшая рыба', 'equivalence_type': 'explanatory'},
        {'tag': '3', 'german': '— 3〉 {%eine Wasserpflanze%}.',
         'russian': 'водное растение', 'equivalence_type': 'explanatory'},
    ],
}


def canonical_fixture(fixture=None):
    value = copy.deepcopy(fixture or CANARY_FIXTURE)
    if value.get('schema') != CONTRACT_SCHEMA:
        raise ValueError('canary fixture schema mismatch')
    senses = value.get('senses')
    if not isinstance(senses, list) or not senses:
        raise ValueError('canary fixture requires senses')
    for index, sense in enumerate(senses, start=1):
        if sense.get('tag') != str(index):
            raise ValueError('canary sense tags must be ordered and contiguous')
        if not re.fullmatch(r'— %s〉 \{%%.+%%\}\.' % index,
                            sense.get('german', '')):
            raise ValueError('canary german must preserve the full skeleton line')
    return value


def render_prompt(fixture=None):
    value = canonical_fixture(fixture)
    fixture_json = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    return (
        'Return one JSON object only. Translate every canonical sense into '
        'Russian and preserve every non-Russian field exactly.\n\n'
        + PROMPT_FIXTURE_BEGIN + '\n' + fixture_json + '\n'
        + PROMPT_FIXTURE_END + '\n\n'
        'The response german field means the complete skeleton line, including '
        'the leading sense marker (for example "— 1〉 "). Do not strip it.\n'
        'Emit exactly one card, one record, and the same ordered sense count. '
        'Use source_type="lexicographic", government=[], iast="", notes="", '
        'h="0", provenance_class="synthetic_control", '
        'route="router-cheap-agent", promotable=false.')


def fixture_from_prompt(prompt):
    if not isinstance(prompt, str):
        raise ValueError('prompt must be text')
    start = prompt.count(PROMPT_FIXTURE_BEGIN)
    end = prompt.count(PROMPT_FIXTURE_END)
    if start != 1 or end != 1:
        raise ValueError('prompt must contain exactly one canonical fixture block')
    body = prompt.split(PROMPT_FIXTURE_BEGIN, 1)[1].split(
        PROMPT_FIXTURE_END, 1)[0].strip()
    try:
        return canonical_fixture(json.loads(body))
    except json.JSONDecodeError as exc:
        raise ValueError('prompt fixture JSON is malformed') from exc


def prompt_derived_instance(prompt):
    value = fixture_from_prompt(prompt)
    senses = [{
        'tag': sense['tag'],
        'german': sense['german'],
        'russian': sense['russian'],
        'equivalence_type': sense['equivalence_type'],
        'source_type': 'lexicographic',
        'government': [],
    } for sense in value['senses']]
    return {
        'schema_marker': value['schema_marker'],
        'provenance': {
            'provenance_class': 'synthetic_control',
            'route': 'router-cheap-agent',
            'model': value['model'],
            'raw_sha256': value['raw_sha256'],
            'portrait_sha256': value['portrait_sha256'],
            'source_senses': len(senses),
            'promotable': False,
        },
        'cards': [{
            'key1': value['key1'], 'iast': '', 'notes': '',
            'records': [{'h': '0', 'grammar': '', 'senses': senses}],
        }],
    }


def build_schema(fixture=None):
    value = canonical_fixture(fixture)
    sense_defs = {}
    for index, sense in enumerate(value['senses'], start=1):
        sense_defs['sense%d' % index] = {
            'type': 'object', 'additionalProperties': False,
            'required': ['tag', 'german', 'russian', 'equivalence_type',
                         'source_type', 'government'],
            'properties': {
                'tag': {'const': sense['tag']},
                'german': {'const': sense['german']},
                'russian': {'$ref': '#/$defs/russian'},
                'equivalence_type': {'enum': ['equivalent', 'explanatory']},
                'source_type': {'const': 'lexicographic'},
                'government': {'type': 'array', 'maxItems': 0},
            },
        }
    count = len(value['senses'])
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'canary_pwg_ru_record_v2.schema.json',
        'type': 'object', 'additionalProperties': False,
        'required': ['schema_marker', 'provenance', 'cards'],
        'properties': {
            'schema_marker': {'const': value['schema_marker']},
            'provenance': {
                'type': 'object', 'additionalProperties': False,
                'required': ['provenance_class', 'route', 'model', 'raw_sha256',
                             'portrait_sha256', 'source_senses', 'promotable'],
                'properties': {
                    'provenance_class': {'const': 'synthetic_control'},
                    'route': {'const': 'router-cheap-agent'},
                    'model': {'const': value['model']},
                    'raw_sha256': {'const': value['raw_sha256']},
                    'portrait_sha256': {'const': value['portrait_sha256']},
                    'source_senses': {'const': count},
                    'promotable': {'const': False},
                },
            },
            'cards': {
                'type': 'array', 'minItems': 1, 'maxItems': 1,
                'prefixItems': [{
                    'type': 'object', 'additionalProperties': False,
                    'required': ['key1', 'iast', 'notes', 'records'],
                    'properties': {
                        'key1': {'const': value['key1']},
                        'iast': {'const': ''}, 'notes': {'const': ''},
                        'records': {
                            'type': 'array', 'minItems': 1, 'maxItems': 1,
                            'prefixItems': [{
                                'type': 'object', 'additionalProperties': False,
                                'required': ['h', 'grammar', 'senses'],
                                'properties': {
                                    'h': {'const': '0'}, 'grammar': {'const': ''},
                                    'senses': {
                                        'type': 'array', 'minItems': count,
                                        'maxItems': count,
                                        'prefixItems': [
                                            {'$ref': '#/$defs/sense%d' % i}
                                            for i in range(1, count + 1)],
                                        'items': False,
                                    },
                                },
                            }], 'items': False,
                        },
                    },
                }], 'items': False,
            },
        },
        '$defs': {
            'russian': {
                'type': 'string', 'minLength': 3,
                'allOf': [{'pattern': '[\\u0430-\\u044F]'},
                          {'pattern': '^[^A-Za-z]*$'}],
            },
            **sense_defs,
        },
    }


def request_and_schema(fixture=None):
    value = canonical_fixture(fixture)
    return {'prompt': render_prompt(value)}, build_schema(value)
