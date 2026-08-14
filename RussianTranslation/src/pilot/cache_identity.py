#!/usr/bin/env python
"""Provider-neutral request identity for the PWG cache-economy contract (H2702).

Canonical JSON is UTF-8 without BOM, LF, sorted keys. The request ID is the
SHA-256 of that serialization of the answer-affecting fields only.

Excluded from identity: timestamps, secrets, filesystem paths, run IDs,
connection IDs, retry ordinals. A Windows path representation therefore cannot
change the ID. Semantic headword labels are metadata, never identity.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

COMPILER_VERSION = 'pwg.prompt_compiler.v1'
REQUEST_SCHEMA = 'pwg.cache_request.v1'
BUNDLE_SCHEMA = 'pwg.prompt_bundle.v1'
EVENT_SCHEMA = 'pwg.cache_event.v1'
RUN_MANIFEST_SCHEMA = 'pwg.cache_run_manifest.v1'
CONVERTER_VERSION = 'pwg.cache_migrate.v1'

IDENTITY_KEYS = (
    'provider',
    'requested_model',
    'generation_parameters',
    'compiler_version',
    'response_schema_sha256',
    'stable_prefix_sha256',
    'volatile_tail_sha256',
    'source_card_sha256',
    'source_fragment_sha256',
    'dependency_hashes',
    'parent_request_id',
    'repair_variant',
)

# Names that must never leak into the identity object.
EXCLUDED_IDENTITY_NAMES = frozenset({
    'timestamp', 'created_at', 'sealed_at', 'ts', 'produced_at',
    'secret', 'api_key', 'authorization', 'token',
    'path', 'cwd', 'file_path', 'abspath', 'locator',
    'run_id', 'connection_id', 'retry_ordinal', 'attempt',
    'pid', 'hostname',
})


def canonical_dumps(obj):
    """UTF-8-ready JSON text: sorted keys, compact, LF terminator, no BOM."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'


def canonical_bytes(obj):
    return canonical_dumps(obj).encode('utf-8')


def sha256_bytes(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    if not path or not os.path.isfile(path):
        return None
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def token_estimate(stable, volatile):
    """Rough token stand-in: UTF-8 bytes / 4, never used as billing."""
    n = len(stable.encode('utf-8')) + len(volatile.encode('utf-8'))
    return (n + 3) // 4


def _strip_excluded(obj):
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if key in EXCLUDED_IDENTITY_NAMES:
                continue
            out[key] = _strip_excluded(value)
        return out
    if isinstance(obj, list):
        return [_strip_excluded(item) for item in obj]
    return obj


def identity_payload(fields):
    """Return the sealed identity object (no request_id yet)."""
    cleaned = _strip_excluded(fields)
    payload = {}
    for key in IDENTITY_KEYS:
        payload[key] = cleaned.get(key)
    payload['compiler_version'] = payload.get('compiler_version') or COMPILER_VERSION
    deps = payload.get('dependency_hashes') or {}
    if not isinstance(deps, dict):
        raise ValueError('dependency_hashes must be an object')
    payload['dependency_hashes'] = {
        name: deps[name] for name in sorted(deps)
    }
    return payload


def request_id_for(fields):
    return sha256_bytes(canonical_bytes(identity_payload(fields)))


def build_request_record(fields):
    payload = identity_payload(fields)
    rid = sha256_bytes(canonical_bytes(payload))
    record = {
        'schema': REQUEST_SCHEMA,
        'compiler_version': payload['compiler_version'],
        'provider': payload['provider'],
        'requested_model': payload['requested_model'],
        'generation_parameters': payload.get('generation_parameters') or {},
        'stable_prefix_sha256': payload['stable_prefix_sha256'],
        'volatile_tail_sha256': payload['volatile_tail_sha256'],
        'response_schema_sha256': payload['response_schema_sha256'],
        'source_card_sha256': payload.get('source_card_sha256'),
        'source_fragment_sha256': payload.get('source_fragment_sha256'),
        'dependency_hashes': payload.get('dependency_hashes') or {},
        'parent_request_id': payload.get('parent_request_id'),
        'repair_variant': payload.get('repair_variant'),
        'request_id': rid,
        'promotable': False,
    }
    compat = fields.get('compatibility')
    if compat is not None:
        record['compatibility'] = compat
    return record


def mutate_and_id(fields, **changes):
    merged = dict(fields)
    merged.update(changes)
    return request_id_for(merged)


def selftest():
    base = {
        'provider': 'deepseek',
        'requested_model': 'deepseek-v4-pro',
        'generation_parameters': {'temperature': 0.2, 'max_tokens': 32768},
        'compiler_version': COMPILER_VERSION,
        'response_schema_sha256': sha256_bytes('{"type":"object"}'),
        'stable_prefix_sha256': sha256_bytes('stable'),
        'volatile_tail_sha256': sha256_bytes('tail'),
        'source_card_sha256': sha256_bytes('card'),
        'source_fragment_sha256': None,
        'dependency_hashes': {'tm': sha256_bytes('tm'), 'prep': sha256_bytes('prep')},
        'parent_request_id': None,
        'repair_variant': None,
    }
    a = request_id_for(base)
    b = request_id_for(dict(base, timestamp='2026-08-14T00:00:00Z',
                            run_id='run-1', path=r'C:\\Users\\x\\card.json',
                            attempt=3, api_key='sk-secret'))
    if a != b:
        raise AssertionError('excluded fields changed identity')
    c = request_id_for(dict(base, requested_model='deepseek-v4-flash'))
    if c == a:
        raise AssertionError('model change must change identity')
    d = request_id_for(dict(base, stable_prefix_sha256=sha256_bytes('other')))
    if d == a:
        raise AssertionError('prefix change must change identity')
    # Path-shaped strings inside excluded names stay out; a path used AS content
    # is hashed by the caller, never stored as a path field.
    dumped = canonical_bytes({'b': 1, 'a': 2})
    if dumped[:3] == b'\xef\xbb\xbf':
        raise AssertionError('BOM leaked into canonical bytes')
    if dumped != b'{"a":2,"b":1}\n':
        raise AssertionError('canonical JSON is not sorted compact LF: %r' % dumped)
    rec = build_request_record(base)
    if rec['promotable'] is not False:
        raise AssertionError('request records are never promotable')
    if rec['request_id'] != a:
        raise AssertionError('record id drifted from payload hash')
    print('cache_identity selftest: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(selftest())
