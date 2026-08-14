#!/usr/bin/env python
"""Provider-neutral prompt compiler (H2702).

Wraps the existing Claude (headless_worker) and DeepSeek (deepseek_arm /
prep_slice) builders. Reconstructs their payload bytes before a migrated
mode is eligible. Provider adapters may add transport headers but must not
reinterpret content.

v0 base = current production assembly. No paid calls.
"""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
H1210 = os.path.join(HERE, 'h1210')
if H1210 not in sys.path:
    sys.path.insert(0, H1210)
H1209 = os.path.join(HERE, 'h1209')
if H1209 not in sys.path:
    sys.path.insert(0, H1209)

import cache_identity as ident  # noqa: E402
import deepseek_arm as ds_arm  # noqa: E402
import headless_worker as hw  # noqa: E402
import prep_slice  # noqa: E402

FIXTURE_DIR = os.path.join(HERE, 'fixtures', 'pwg_cache_economy')


def _dep_hashes(extra):
    extra = extra or {}
    deps = dict(extra.get('dependency_hashes') or {})
    for name in ('tm', 'denylist', 'retrieved_evidence', 'grammar', 'nws',
                 'prep', 'corpus'):
        if name in extra and name not in deps:
            deps[name] = extra[name]
    return deps


def _gen_params(extra, defaults):
    extra = extra or {}
    params = dict(defaults)
    params.update(extra.get('generation_parameters') or {})
    return params


def compile_claude_v0(manifest, keys, extra=None):
    """Compile a Claude/headless request using production prompt_blocks."""
    extra = extra or {}
    stable, volatile = hw.prompt_blocks(manifest, keys)
    schema_obj = extra.get('response_schema') or {'type': 'object'}
    schema_hash = ident.sha256_bytes(ident.canonical_bytes(schema_obj))
    source = ''.join((manifest.get('inputs') or {}).get(k, {}).get('skeleton', '')
                     for k in keys)
    fields = {
        'provider': extra.get('provider') or 'anthropic',
        'requested_model': extra.get('requested_model') or 'claude-opus-5',
        'generation_parameters': _gen_params(extra, {'max_tokens': 32768}),
        'compiler_version': ident.COMPILER_VERSION,
        'response_schema_sha256': schema_hash,
        'stable_prefix_sha256': ident.sha256_bytes(stable),
        'volatile_tail_sha256': ident.sha256_bytes(volatile),
        'source_card_sha256': ident.sha256_bytes(source) if source else None,
        'source_fragment_sha256': extra.get('source_fragment_sha256'),
        'dependency_hashes': _dep_hashes(extra),
        'parent_request_id': extra.get('parent_request_id'),
        'repair_variant': extra.get('repair_variant'),
    }
    request = ident.build_request_record(fields)
    bundle = {
        'schema': ident.BUNDLE_SCHEMA,
        'compiler_version': ident.COMPILER_VERSION,
        'provider': fields['provider'],
        'requested_model': fields['requested_model'],
        'stable_prefix_sha256': fields['stable_prefix_sha256'],
        'volatile_tail_sha256': fields['volatile_tail_sha256'],
        'response_schema_sha256': schema_hash,
        'generation_parameters': fields['generation_parameters'],
        'token_estimate': ident.token_estimate(stable, volatile),
        'lineage': {
            'parent_request_id': fields.get('parent_request_id'),
            'repair_variant': fields.get('repair_variant'),
        },
        'request_id': request['request_id'],
        'provider_envelope': {
            'kind': 'claude_prompt',
            'prompt': stable + volatile,
        },
        'promotable': False,
    }
    return {
        'bundle': bundle,
        'request': request,
        'stable_prefix': stable,
        'volatile_tail': volatile,
    }


def compile_deepseek_v0(card, common, schema, extra=None):
    """Compile a DeepSeek request using production SYSTEM_TMPL + common + card."""
    extra = extra or {}
    schema_text = json.dumps(schema, ensure_ascii=False)
    system = ds_arm.SYSTEM_TMPL % schema_text
    card_block = card['card_block']
    feedback = extra.get('feedback')
    user_volatile = card_block
    if feedback:
        user_volatile = (
            card_block
            + '\n\n=== CONTROLLER FEEDBACK (fix ONLY these, keep everything else verbatim) ===\n'
            + feedback
        )
    # Shared system + slice common is the cacheable prefix; card (+ repair) is the tail.
    stable = system + '\n' + common
    volatile = user_volatile
    schema_hash = ident.sha256_bytes(ident.canonical_bytes(schema))
    fields = {
        'provider': extra.get('provider') or 'deepseek',
        'requested_model': extra.get('requested_model') or ds_arm.DEFAULT_MODEL,
        'generation_parameters': _gen_params(extra, {
            'temperature': 0.2,
            'max_tokens': extra.get('max_tokens') or ds_arm.DEFAULT_MAX_TOKENS,
            'response_format': {'type': 'json_object'},
        }),
        'compiler_version': ident.COMPILER_VERSION,
        'response_schema_sha256': schema_hash,
        'stable_prefix_sha256': ident.sha256_bytes(stable),
        'volatile_tail_sha256': ident.sha256_bytes(volatile),
        'source_card_sha256': ident.sha256_bytes(card_block),
        'source_fragment_sha256': extra.get('source_fragment_sha256'),
        'dependency_hashes': _dep_hashes(extra),
        'parent_request_id': extra.get('parent_request_id'),
        'repair_variant': extra.get('repair_variant'),
    }
    request = ident.build_request_record(fields)
    bundle = {
        'schema': ident.BUNDLE_SCHEMA,
        'compiler_version': ident.COMPILER_VERSION,
        'provider': fields['provider'],
        'requested_model': fields['requested_model'],
        'stable_prefix_sha256': fields['stable_prefix_sha256'],
        'volatile_tail_sha256': fields['volatile_tail_sha256'],
        'response_schema_sha256': schema_hash,
        'generation_parameters': fields['generation_parameters'],
        'token_estimate': ident.token_estimate(stable, volatile),
        'lineage': {
            'parent_request_id': fields.get('parent_request_id'),
            'repair_variant': fields.get('repair_variant'),
        },
        'request_id': request['request_id'],
        'provider_envelope': {
            'kind': 'openai_chat',
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': common + user_volatile},
            ],
        },
        'promotable': False,
    }
    return {
        'bundle': bundle,
        'request': request,
        'stable_prefix': stable,
        'volatile_tail': volatile,
        'system': system,
        'user': common + user_volatile,
    }


def reconstruct_legacy_claude(fixture):
    compiled = compile_claude_v0(fixture['manifest'], fixture['keys'],
                                 extra=fixture.get('extra'))
    prompt = compiled['stable_prefix'] + compiled['volatile_tail']
    expected = fixture['expected_prompt']
    if prompt != expected:
        raise AssertionError('Claude legacy reconstruction drifted')
    return compiled


def reconstruct_legacy_deepseek(fixture):
    compiled = compile_deepseek_v0(
        fixture['card'], fixture['common'], fixture['schema'],
        extra=fixture.get('extra'),
    )
    if compiled['system'] != fixture['expected_system']:
        raise AssertionError('DeepSeek system reconstruction drifted')
    if compiled['user'] != fixture['expected_user']:
        raise AssertionError('DeepSeek user reconstruction drifted')
    return compiled


def load_json(name):
    path = name if os.path.dirname(name) else os.path.join(FIXTURE_DIR, name)
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def write_golden_fixtures(directory=None):
    """Regenerate committed goldens from the live builders (offline)."""
    directory = directory or FIXTURE_DIR
    os.makedirs(directory, exist_ok=True)
    claude = {
        'kind': 'legacy_claude_v0',
        'keys': ['demo'],
        'manifest': {
            'prompt': {
                'preamble': 'PREAMBLE\n',
                'translation': 'TRANSLATION RULES\n',
                'grammar': 'GRAMMAR\n',
                'nws_rule': 'NWS RULE',
                'grammars': {'demo': 'CARD-GRAMMAR'},
            },
            'inputs': {
                'demo': {
                    'skeleton': 'ein {%Gloss%}. {T1}',
                    'portrait': 'portrait-bytes',
                    'nws': True,
                },
            },
            'suggestions': {},
        },
    }
    compiled = compile_claude_v0(claude['manifest'], claude['keys'])
    claude['expected_prompt'] = compiled['stable_prefix'] + compiled['volatile_tail']
    claude['expected_stable_sha256'] = compiled['request']['stable_prefix_sha256']
    claude['expected_volatile_sha256'] = compiled['request']['volatile_tail_sha256']
    claude['expected_request_id'] = compiled['request']['request_id']

    schema = {
        'type': 'object',
        'required': ['card', 'self_report'],
        'properties': {
            'card': {'type': 'object'},
            'self_report': {'type': 'object'},
        },
    }
    common = prep_slice.prompt_common(claude['manifest'])
    card = {
        'key1': 'demo',
        'card_block': prep_slice.card_block(claude['manifest'], 'demo'),
        'complexity': {'complex': False},
    }
    deep = {
        'kind': 'legacy_deepseek_v0',
        'card': card,
        'common': common,
        'schema': schema,
        'extra': {'requested_model': 'deepseek-v4-pro'},
    }
    dcomp = compile_deepseek_v0(card, common, schema, extra=deep['extra'])
    deep['expected_system'] = dcomp['system']
    deep['expected_user'] = dcomp['user']
    deep['expected_request_id'] = dcomp['request']['request_id']

    for name, payload in (
        ('legacy_claude_prompt.json', claude),
        ('legacy_deepseek_payload.json', deep),
    ):
        path = os.path.join(directory, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    return directory


def selftest():
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    write_golden_fixtures(FIXTURE_DIR)
    claude = load_json('legacy_claude_prompt.json')
    deep = load_json('legacy_deepseek_payload.json')
    rec_c = reconstruct_legacy_claude(claude)
    rec_d = reconstruct_legacy_deepseek(deep)
    if rec_c['request']['request_id'] != claude['expected_request_id']:
        raise AssertionError('Claude request id drifted from golden')
    if rec_d['request']['request_id'] != deep['expected_request_id']:
        raise AssertionError('DeepSeek request id drifted from golden')
    # Identity mutation: one answer-affecting change, one excluded change.
    mutated = compile_claude_v0(
        claude['manifest'], claude['keys'],
        extra={'requested_model': 'claude-sonnet-5'},
    )
    if mutated['request']['request_id'] == rec_c['request']['request_id']:
        raise AssertionError('model mutation did not change request id')
    ignored = compile_claude_v0(
        claude['manifest'], claude['keys'],
        extra={'run_id': 'other-run', 'path': r'D:\\tmp\\x.json'},
    )
    if ignored['request']['request_id'] != rec_c['request']['request_id']:
        raise AssertionError('path/run extras leaked into identity')
    # Oracle: compiler bytes == live production builders.
    live = hw.build_prompt(claude['manifest'], claude['keys'])
    if rec_c['stable_prefix'] + rec_c['volatile_tail'] != live:
        raise AssertionError('compiler diverged from headless_worker.build_prompt')
    live_user = deep['common'] + deep['card']['card_block']
    if rec_d['user'] != live_user:
        raise AssertionError('compiler diverged from DeepSeek user assembly')
    print('prompt_compiler selftest: PASS')
    return 0


if __name__ == '__main__':
    if '--write-goldens' in sys.argv:
        write_golden_fixtures()
        print('wrote goldens under', FIXTURE_DIR)
        raise SystemExit(0)
    raise SystemExit(selftest())
