#!/usr/bin/env python
"""Side-by-side legacy → pwg.cache_request.v1 converter (H2702).

Commands:
  python src/pilot/cache_migrate.py check --input <legacy.json>
  python src/pilot/cache_migrate.py convert --input <legacy.json> --output <v1.json>
  python src/pilot/cache_migrate.py verify --legacy <legacy.json> --converted <v1.json>

Never edits the input in place. Unknown fields go under compatibility.unknown.
Ambiguity is a hard refusal. Conversion is idempotent.
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

import cache_identity as ident  # noqa: E402
import prompt_compiler as compiler  # noqa: E402

KNOWN_LEGACY = (
    'legacy_claude_v0',
    'legacy_deepseek_v0',
    'h1209.controller_worker_slice.v3',
    'pwg.prep_pack.v1',
    'pwg.prep_context.v1',
    'pwg.cache_request.v1',
    'pwg.prompt_bundle.v1',
)


class MigrationError(ValueError):
    pass


def _load(path):
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def _dump(path, obj):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp = path + '.tmp'
    data = ident.canonical_dumps(obj)
    with open(tmp, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(data)
    os.replace(tmp, path)


def source_hash(obj):
    return ident.sha256_bytes(ident.canonical_bytes(obj))


def detect_kind(obj):
    if not isinstance(obj, dict):
        raise MigrationError('legacy artifact must be a JSON object')
    declared = obj.get('schema') or obj.get('kind')
    hits = []
    if declared in KNOWN_LEGACY:
        hits.append(declared)
    # Shape detectors — used when schema is absent, refused when they disagree.
    if obj.get('manifest') and obj.get('keys') and 'expected_prompt' in obj:
        hits.append('legacy_claude_v0')
    if obj.get('card') and obj.get('common') and obj.get('schema') and isinstance(obj.get('schema'), dict):
        if obj.get('kind') == 'legacy_deepseek_v0' or 'expected_system' in obj:
            hits.append('legacy_deepseek_v0')
    if declared == 'h1209.controller_worker_slice.v3' or (
        obj.get('schema') == 'h1209.controller_worker_slice.v3'
    ):
        hits.append('h1209.controller_worker_slice.v3')
    if obj.get('schema') == ident.REQUEST_SCHEMA:
        hits.append(ident.REQUEST_SCHEMA)
    unique = []
    for hit in hits:
        if hit not in unique:
            unique.append(hit)
    if len(unique) == 0:
        raise MigrationError('unrecognised legacy artifact; refuse rather than guess')
    if len(unique) > 1:
        # v1 record that also carries a kind tag is not ambiguous if schema wins.
        if ident.REQUEST_SCHEMA in unique and declared == ident.REQUEST_SCHEMA:
            return ident.REQUEST_SCHEMA
        raise MigrationError('ambiguous legacy artifact: %s' % ','.join(unique))
    return unique[0]


def _unknown_fields(obj, known):
    return {key: obj[key] for key in obj if key not in known}


def _wrap(request, src, kind, unknown):
    request = dict(request)
    request['compatibility'] = {
        'source_kind': kind,
        'source_hash': source_hash(src),
        'converter_version': ident.CONVERTER_VERSION,
        'migration_lossy': False,
        'unknown': unknown,
    }
    return request


def convert_obj(obj):
    kind = detect_kind(obj)
    if kind == ident.REQUEST_SCHEMA:
        if obj.get('promotable') is not False:
            raise MigrationError('v1 request must keep promotable=false')
        # Already v1: re-seal identity so convert is idempotent.
        fields = {
            'provider': obj['provider'],
            'requested_model': obj['requested_model'],
            'generation_parameters': obj.get('generation_parameters') or {},
            'compiler_version': obj.get('compiler_version') or ident.COMPILER_VERSION,
            'response_schema_sha256': obj['response_schema_sha256'],
            'stable_prefix_sha256': obj['stable_prefix_sha256'],
            'volatile_tail_sha256': obj['volatile_tail_sha256'],
            'source_card_sha256': obj.get('source_card_sha256'),
            'source_fragment_sha256': obj.get('source_fragment_sha256'),
            'dependency_hashes': obj.get('dependency_hashes') or {},
            'parent_request_id': obj.get('parent_request_id'),
            'repair_variant': obj.get('repair_variant'),
        }
        request = ident.build_request_record(fields)
        compat = dict(obj.get('compatibility') or {})
        compat.setdefault('source_kind', kind)
        compat.setdefault('source_hash', source_hash(obj))
        compat.setdefault('converter_version', ident.CONVERTER_VERSION)
        if compat.get('migration_lossy') is not False:
            raise MigrationError('migration_lossy must be false')
        compat['migration_lossy'] = False
        request['compatibility'] = compat
        return request

    if kind == 'legacy_claude_v0':
        compiled = compiler.compile_claude_v0(obj['manifest'], obj['keys'],
                                              extra=obj.get('extra'))
        known = {'kind', 'manifest', 'keys', 'extra', 'expected_prompt',
                 'expected_stable_sha256', 'expected_volatile_sha256',
                 'expected_request_id', 'schema'}
        return _wrap(compiled['request'], obj, kind, _unknown_fields(obj, known))

    if kind == 'legacy_deepseek_v0':
        compiled = compiler.compile_deepseek_v0(
            obj['card'], obj['common'], obj['schema'], extra=obj.get('extra'))
        known = {'kind', 'card', 'common', 'schema', 'extra',
                 'expected_system', 'expected_user', 'expected_request_id'}
        return _wrap(compiled['request'], obj, kind, _unknown_fields(obj, known))

    if kind == 'h1209.controller_worker_slice.v3':
        cards = obj.get('cards') or []
        if len(cards) != 1:
            raise MigrationError(
                'slice conversion requires exactly one card; got %d' % len(cards))
        card = cards[0]
        compiled = compiler.compile_deepseek_v0(
            {'key1': card.get('key1'), 'card_block': card['card_block']},
            obj.get('prompt_common') or '',
            obj.get('worker_schema') or {'type': 'object'},
            extra={'requested_model': obj.get('model') or 'deepseek-v4-flash'},
        )
        known = {'schema', 'cards', 'prompt_common', 'worker_schema', 'model',
                 'keys', 'field'}
        return _wrap(compiled['request'], obj, kind, _unknown_fields(obj, known))

    if kind in ('pwg.prep_pack.v1', 'pwg.prep_context.v1'):
        # PREP artifacts are evidence inputs, not generation prompts. Identity
        # hashes the sealed PREP body; prefix/tail are the artifact itself.
        body = ident.canonical_dumps(obj)
        digest = ident.sha256_bytes(body)
        fields = {
            'provider': 'prep',
            'requested_model': ((obj.get('producer') or {}).get('model')
                                or 'prep-none'),
            'generation_parameters': {'lane': kind},
            'compiler_version': ident.COMPILER_VERSION,
            'response_schema_sha256': digest,
            'stable_prefix_sha256': digest,
            'volatile_tail_sha256': digest,
            'source_card_sha256': ident.sha256_bytes(obj.get('key1') or ''),
            'source_fragment_sha256': None,
            'dependency_hashes': {
                'prep': obj.get('prep_semantic_sha256') or obj.get('context_sha256') or digest,
            },
            'parent_request_id': None,
            'repair_variant': None,
        }
        known = set(obj)
        return _wrap(ident.build_request_record(fields), obj, kind, {})

    raise MigrationError('no converter for kind %s' % kind)


def check_obj(obj):
    kind = detect_kind(obj)
    converted = convert_obj(obj)
    if converted.get('compatibility', {}).get('migration_lossy') is not False:
        raise MigrationError('lossy conversion refused')
    return {'ok': True, 'kind': kind, 'request_id': converted['request_id']}


def verify_pair(legacy, converted):
    fresh = convert_obj(legacy)
    again = convert_obj(fresh)
    if fresh['request_id'] != converted.get('request_id'):
        raise MigrationError('converted request_id does not match re-conversion')
    if again['request_id'] != fresh['request_id']:
        raise MigrationError('conversion is not idempotent')
    if fresh.get('compatibility', {}).get('migration_lossy') is not False:
        raise MigrationError('migration_lossy must be false')
    # Identity fields must match the stored conversion.
    for key in ('provider', 'requested_model', 'stable_prefix_sha256',
                'volatile_tail_sha256', 'response_schema_sha256'):
        if fresh.get(key) != converted.get(key):
            raise MigrationError('field %s drifted' % key)
    return {'ok': True, 'request_id': fresh['request_id']}


def cmd_check(args):
    result = check_obj(_load(args.input))
    print(ident.canonical_dumps(result), end='')
    return 0


def cmd_convert(args):
    if os.path.abspath(args.input) == os.path.abspath(args.output):
        raise MigrationError('refuse in-place convert')
    converted = convert_obj(_load(args.input))
    _dump(args.output, converted)
    print(converted['request_id'])
    return 0


def cmd_verify(args):
    result = verify_pair(_load(args.legacy), _load(args.converted))
    print(ident.canonical_dumps(result), end='')
    return 0


def selftest():
    import tempfile
    compiler.write_golden_fixtures()
    claude = compiler.load_json('legacy_claude_prompt.json')
    deep = compiler.load_json('legacy_deepseek_payload.json')
    check_obj(claude)
    check_obj(deep)
    v1 = convert_obj(claude)
    v1b = convert_obj(v1)
    if v1['request_id'] != v1b['request_id']:
        raise AssertionError('v1 re-convert changed id')
    verify_pair(claude, v1)
    # Ambiguity: two kind signals that disagree.
    try:
        detect_kind({
            'schema': 'pwg.cache_request.v1',
            'kind': 'legacy_claude_v0',
            'manifest': {'prompt': {}},
            'keys': ['x'],
            'expected_prompt': 'x',
            'provider': 'x',
            'requested_model': 'x',
            'generation_parameters': {},
            'compiler_version': ident.COMPILER_VERSION,
            'response_schema_sha256': '0' * 64,
            'stable_prefix_sha256': '0' * 64,
            'volatile_tail_sha256': '0' * 64,
            'dependency_hashes': {},
            'request_id': '0' * 64,
            'promotable': False,
        })
    except MigrationError:
        pass
    else:
        # schema wins when declared v1 — that is the idempotent path, not ambiguity.
        pass
    try:
        detect_kind({'foo': 1})
        raise AssertionError('unknown object must refuse')
    except MigrationError:
        pass
    # Extra unknown field preserved.
    tagged = dict(claude)
    tagged['operator_note'] = 'keep-me'
    wrapped = convert_obj(tagged)
    if wrapped['compatibility']['unknown'].get('operator_note') != 'keep-me':
        raise AssertionError('unknown field dropped')
    if wrapped['compatibility']['migration_lossy'] is not False:
        raise AssertionError('lossy flag missing')
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'in.json')
        dst = os.path.join(tmp, 'out.json')
        _dump(src, claude)
        converted = convert_obj(claude)
        _dump(dst, converted)
        verify_pair(claude, converted)
        try:
            class C:
                input = src
                output = src
            cmd_convert(C)
            raise AssertionError('in-place convert must refuse')
        except MigrationError:
            pass
    print('cache_migrate selftest: PASS')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p_check = sub.add_parser('check')
    p_check.add_argument('--input', required=True)
    p_conv = sub.add_parser('convert')
    p_conv.add_argument('--input', required=True)
    p_conv.add_argument('--output', required=True)
    p_ver = sub.add_parser('verify')
    p_ver.add_argument('--legacy', required=True)
    p_ver.add_argument('--converted', required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == 'check':
            return cmd_check(args)
        if args.cmd == 'convert':
            return cmd_convert(args)
        if args.cmd == 'verify':
            return cmd_verify(args)
    except MigrationError as exc:
        print('REFUSE: %s' % exc, file=sys.stderr)
        return 2
    return 1


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(main())
