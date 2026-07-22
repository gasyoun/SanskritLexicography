#!/usr/bin/env python
"""Rootmap/input provenance checks for optimized Max workflow output."""
from collections import Counter
import os

from window_common import HERE, INP, sha256_file, load_json, rootmap_for, input_paths, harness_meta

import sys
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from safe_filename import safe_name


def current_root_provenance(root, selected_keys=None, nominal=False):
    if nominal:
        keys = selected_keys or []
        if not keys:
            return {'ok': False, 'rootmap_path': None,
                    'error': 'nominal window %r has no selected_keys' % root}
        input_hashes = {}
        missing = []
        for key in keys:
            raw_path, portrait_path = input_paths(key, input_dir=INP)
            rec = {}
            if os.path.exists(raw_path):
                rec['raw_sha256'] = sha256_file(raw_path)
            else:
                missing.append(key + '.raw.txt')
            if os.path.exists(portrait_path):
                rec['portrait_sha256'] = sha256_file(portrait_path)
            else:
                missing.append(key + '.portrait.json')
            input_hashes[key] = rec
        return {
            'ok': True,
            'root': root,
            'safe_root': safe_name(root),
            'nominal': True,
            'rootmap_path': None,
            'rootmap_sha256': None,
            'root_keys': keys,
            'selected_keys': keys,
            'input_hashes': input_hashes,
            'missing_inputs': missing,
        }
    rootmap = rootmap_for(root)
    if not rootmap:
        return {'ok': False, 'rootmap_path': None, 'error': 'no rootmap for %r' % root}
    rootmap_json = load_json(rootmap)
    root_keys = [row['subkey'] for row in rootmap_json.get('sub_cards', [])]
    keys = selected_keys or root_keys
    input_hashes = {}
    missing = []
    for key in keys:
        raw_path, portrait_path = input_paths(key, input_dir=INP)
        rec = {}
        if os.path.exists(raw_path):
            rec['raw_sha256'] = sha256_file(raw_path)
        else:
            missing.append(key + '.raw.txt')
        if os.path.exists(portrait_path):
            rec['portrait_sha256'] = sha256_file(portrait_path)
        else:
            missing.append(key + '.portrait.json')
        input_hashes[key] = rec
    return {
        'ok': True,
        'root': root,
        'safe_root': safe_name(root),
        'rootmap_path': rootmap,
        'rootmap_sha256': sha256_file(rootmap),
        'root_keys': root_keys,
        'selected_keys': keys,
        'input_hashes': input_hashes,
        'missing_inputs': missing,
    }


def _key_coverage(check, workflow_keys, expected_keys, label):
    got = Counter(workflow_keys)
    expected = Counter(expected_keys)
    duplicates = {key: count for key, count in got.items() if count > 1}
    expected_duplicates = {key: count for key, count in expected.items() if count > 1}
    if got == expected and not duplicates and not expected_duplicates:
        return
    missing = sorted((expected - got).elements())
    unexpected = sorted((got - expected).elements())
    check['errors'].append(
        '%s keys do not match exactly once (workflow=%d expected=%d missing=%d '
        'unexpected=%d duplicates=%d)' %
        (label, len(workflow_keys), len(expected_keys), len(missing), len(unexpected),
         len(duplicates)))
    check['missing_keys'] = missing
    check['unexpected_keys'] = unexpected
    check['duplicate_keys'] = duplicates
    check['expected_duplicate_keys'] = expected_duplicates


def stale_check(root, workflow_meta, workflow_keys, execution_manifest=None):
    requested_root = root
    check = {'ok': True, 'stale': False, 'warnings': [], 'errors': [],
             'workflow_meta': workflow_meta or {}, 'current': None,
             'execution_manifest': None}
    manifest_meta = None
    if execution_manifest is not None:
        if execution_manifest.get('_load_error'):
            check['errors'].append('execution manifest could not be loaded: %s' %
                                   execution_manifest['_load_error'])
        elif execution_manifest.get('schema') not in (
                'pwg.headless_execution_manifest.v1',
                'pwg.headless_execution_manifest.v2'):
            # B23 (H1339, found by the offline bench's first end-to-end run): production
            # profile-bound prepare emits manifest v2, but this check accepted ONLY v1 --
            # so every v2 lease audited as stale_artifact and the whole headless factory
            # chain could never pass its own audit. v2 is a superset at the meta level
            # (adds top-level execution/key_provenance, which the import gate validates).
            check['errors'].append('unsupported execution manifest schema: %r' %
                                   execution_manifest.get('schema'))
        elif not isinstance(execution_manifest.get('meta'), dict):
            check['errors'].append('execution manifest meta is missing or invalid')
        else:
            manifest_meta = execution_manifest['meta']
            check['execution_manifest'] = {
                'schema': execution_manifest['schema'],
                'root': manifest_meta.get('root'),
                'nominal': bool(manifest_meta.get('nominal')),
                'selected_keys': manifest_meta.get('selected_keys') or [],
            }
            if requested_root and requested_root != manifest_meta.get('root'):
                check['errors'].append('requested root %r != execution manifest root %r' %
                                       (requested_root, manifest_meta.get('root')))
            root = root or manifest_meta.get('root')

    if not root and manifest_meta is None:
        if check['errors']:
            check['ok'] = False
            check['stale'] = True
        else:
            check['warnings'].append('no --root supplied; rootmap/input staleness was not checked')
        return check
    if not workflow_meta:
        check['ok'] = False
        check['stale'] = True
        check['errors'].append('workflow meta missing from wf_output; fresh Max output is required')
        selected_keys = None
    else:
        selected_keys = ((manifest_meta or {}).get('selected_keys')
                         or workflow_meta.get('selected_keys') or None)
    nominal = bool((manifest_meta or workflow_meta or {}).get('nominal'))

    if manifest_meta is not None and workflow_meta:
        manifest_keys = manifest_meta.get('selected_keys') or []
        workflow_selected = workflow_meta.get('selected_keys') or []
        if Counter(workflow_selected) != Counter(manifest_keys):
            check['errors'].append('workflow selected_keys do not match execution manifest')
        if workflow_meta.get('root') != manifest_meta.get('root'):
            check['errors'].append('workflow root %r != execution manifest root %r' %
                                   (workflow_meta.get('root'), manifest_meta.get('root')))
        if bool(workflow_meta.get('nominal')) != bool(manifest_meta.get('nominal')):
            check['errors'].append('workflow nominal mode does not match execution manifest')
        if workflow_meta.get('rootmap_sha256') != manifest_meta.get('rootmap_sha256'):
            check['errors'].append('workflow rootmap hash does not match execution manifest')
        if workflow_meta.get('input_hashes') != manifest_meta.get('input_hashes'):
            check['errors'].append('workflow input hashes do not match execution manifest')
        # H1386 P3h: B23 admitted v2 manifests but still verified only v1-era meta. A v2
        # manifest also binds top-level execution + key_provenance, and PROMOTION trusts
        # the wf_output-side copies (provenance-class gating + the B20 model-identity
        # check) -- headless_worker/execution_contract stamp them verbatim from the
        # manifest, so any drift means a stale/foreign/tampered wf_output.
        if (execution_manifest or {}).get('schema') == 'pwg.headless_execution_manifest.v2':
            if workflow_meta.get('execution') != execution_manifest.get('execution'):
                check['errors'].append(
                    'workflow execution block does not match execution manifest')
            if workflow_meta.get('provenance_classes') != execution_manifest.get('key_provenance'):
                check['errors'].append(
                    'workflow provenance_classes do not match execution manifest key_provenance')

    if manifest_meta is not None:
        _key_coverage(check, workflow_keys, manifest_meta.get('selected_keys') or [],
                      'execution manifest')

    current = current_root_provenance(root, selected_keys, nominal=nominal)
    check['current'] = current
    if not current.get('ok'):
        check['ok'] = False
        check['stale'] = True
        check['errors'].append(current.get('error') or 'root provenance unavailable')
        return check

    root_keys = current['root_keys']
    expected_keys = current['selected_keys']
    if selected_keys and not nominal:
        invalid = sorted(set(selected_keys) - set(root_keys))
        if invalid:
            check['errors'].append('workflow selected keys not in current rootmap: %s' %
                                   ', '.join(invalid[:12]))
    _key_coverage(check, workflow_keys, expected_keys, 'current selected rootmap')
    if current['missing_inputs']:
        check['errors'].append('current raw/portrait inputs missing: %s' %
                               ', '.join(current['missing_inputs'][:12]))

    if workflow_meta:
        if workflow_meta.get('root') and workflow_meta.get('root') != root:
            check['errors'].append('workflow root %r != requested root %r' %
                                   (workflow_meta.get('root'), root))
        if workflow_meta.get('safe_root') and workflow_meta.get('safe_root') != safe_name(root):
            check['errors'].append('workflow safe_root %r != current safe_root %r' %
                                   (workflow_meta.get('safe_root'), safe_name(root)))
        if not nominal and workflow_meta.get('rootmap_sha256') != current['rootmap_sha256']:
            check['errors'].append('rootmap hash mismatch')
        workflow_hashes = workflow_meta.get('input_hashes') or {}
        for key in expected_keys:
            got = workflow_hashes.get(key)
            cur = current['input_hashes'].get(key) or {}
            if not got:
                check['errors'].append('missing workflow input hash for %s' % key)
                continue
            if got.get('raw_sha256') != cur.get('raw_sha256'):
                check['errors'].append('raw hash mismatch for %s' % key)
            if got.get('portrait_sha256') != cur.get('portrait_sha256'):
                check['errors'].append('portrait hash mismatch for %s' % key)

    if check['errors']:
        check['ok'] = False
        check['stale'] = True
    return check


def harness_matches_current_root(report):
    root = report.get('root')
    stale = report.get('stale_check') or {}
    current = stale.get('current') or {}
    expected = current.get('selected_keys') or []
    meta = harness_meta()
    nominal = bool((report.get('workflow_meta') or {}).get('nominal') or
                   (stale.get('workflow_meta') or {}).get('nominal') or current.get('nominal'))
    if not root or not expected:
        return False, meta
    if not nominal and not current.get('rootmap_sha256'):
        return False, meta
    if not meta.get('ok'):
        return False, meta
    ok = (meta.get('root') == root and (meta.get('selected_keys') or []) == expected)
    if nominal:
        ok = ok and bool((meta.get('meta') or {}).get('nominal'))
    else:
        ok = ok and meta.get('rootmap_sha256') == current.get('rootmap_sha256')
    if not ok:
        meta['scope_error'] = 'harness scope does not match current rootmap selection'
    return ok, meta
