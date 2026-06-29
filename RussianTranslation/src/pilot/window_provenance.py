#!/usr/bin/env python
"""Rootmap/input provenance checks for optimized Max workflow output."""
import os

from window_common import HERE, INP, sha256_file, load_json, rootmap_for, input_paths, harness_meta

import sys
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from safe_filename import safe_name


def current_root_provenance(root, selected_keys=None):
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


def stale_check(root, workflow_meta, workflow_keys):
    check = {'ok': True, 'stale': False, 'warnings': [], 'errors': [],
             'workflow_meta': workflow_meta or {}, 'current': None}
    if not root:
        check['warnings'].append('no --root supplied; rootmap/input staleness was not checked')
        return check
    if not workflow_meta:
        check['ok'] = False
        check['stale'] = True
        check['errors'].append('workflow meta missing from wf_output; fresh Max output is required')
        selected_keys = None
    else:
        selected_keys = workflow_meta.get('selected_keys') or None
    current = current_root_provenance(root, selected_keys)
    check['current'] = current
    if not current.get('ok'):
        check['ok'] = False
        check['stale'] = True
        check['errors'].append(current.get('error') or 'root provenance unavailable')
        return check

    root_keys = current['root_keys']
    expected_keys = current['selected_keys']
    if selected_keys:
        invalid = sorted(set(selected_keys) - set(root_keys))
        if invalid:
            check['errors'].append('workflow selected keys not in current rootmap: %s' %
                                   ', '.join(invalid[:12]))
    if workflow_keys != expected_keys:
        missing = sorted(set(expected_keys) - set(workflow_keys))
        unexpected = sorted(set(workflow_keys) - set(expected_keys))
        check['errors'].append('workflow keys do not match current selected rootmap keys '
                               '(workflow=%d expected=%d missing=%d unexpected=%d)' %
                               (len(workflow_keys), len(expected_keys), len(missing), len(unexpected)))
        check['missing_keys'] = missing
        check['unexpected_keys'] = unexpected
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
        if workflow_meta.get('rootmap_sha256') != current['rootmap_sha256']:
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
    meta = harness_meta(os.path.join(HERE, 'run_pilot_wf.opt.js'))
    if not root or not current.get('rootmap_sha256') or not expected:
        return False, meta
    if not meta.get('ok'):
        return False, meta
    ok = (
        meta.get('root') == root and
        meta.get('rootmap_sha256') == current.get('rootmap_sha256') and
        (meta.get('selected_keys') or []) == expected
    )
    if not ok:
        meta['scope_error'] = 'harness scope does not match current rootmap selection'
    return ok, meta
