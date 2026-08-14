#!/usr/bin/env python
"""Freeze source-commit + SHA-256 baselines for the cache-economy contract (H2702).

Writes experiments/pwg_cache_economy/baseline/manifest.json with hashes only
(no secrets, no store contents). Canonical store/TM hashes are resolved through
store_path helpers. Missing local files are recorded as null + reason.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
RT = os.path.dirname(SRC)
REPO = os.path.dirname(RT)

import cache_identity as ident  # noqa: E402
from store_path import canonical_sidecar, canonical_store  # noqa: E402

OUT = os.path.join(RT, 'experiments', 'pwg_cache_economy', 'baseline', 'manifest.json')

TRACKED = (
    'RussianTranslation/experiments/H2676_v4pro_q3_rematch/sample_keys.json',
    'RussianTranslation/experiments/H2676_v4pro_q3_rematch/h2676.manifest.json',
    'RussianTranslation/experiments/H2676_v4pro_q3_rematch/slice_payload.json',
    'RussianTranslation/experiments/H2675_w1_prep/REPORT.md',
    'RussianTranslation/src/pilot/h1210/deepseek_arm.py',
    'RussianTranslation/src/pilot/h1210/det_gate.py',
    'RussianTranslation/src/pilot/h1210/prep_pack.py',
    'RussianTranslation/src/pilot/h1210/prep_pack.schema.json',
    'RussianTranslation/src/pilot/h1210/prep_context.schema.json',
    'RussianTranslation/src/pilot/h1209/prep_slice.py',
    'RussianTranslation/src/pilot/headless_worker.py',
    'RussianTranslation/src/pilot/translation_memory.py',
    'RussianTranslation/schemas/pwg_ru_final_card.schema.json',
    'RussianTranslation/schemas/pwg_transport_envelope.schema.json',
    'RussianTranslation/schemas/translation_memory.schema.json',
)


def git_commit():
    proc = subprocess.run(
        ['git', '-C', REPO, 'rev-parse', 'HEAD'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        encoding='utf-8',
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def hash_rel(rel):
    path = os.path.join(REPO, *rel.split('/'))
    digest = ident.sha256_file(path)
    if digest is None:
        return {'path': rel, 'sha256': None, 'reason': 'missing'}
    return {'path': rel, 'sha256': digest, 'bytes': os.path.getsize(path)}


def hash_resolved(label, path):
    digest = ident.sha256_file(path)
    if digest is None:
        return {
            'label': label,
            'resolved': path,
            'sha256': None,
            'reason': 'absent_local',
        }
    return {
        'label': label,
        'resolved': path,
        'sha256': digest,
        'bytes': os.path.getsize(path),
    }


def build_manifest():
    store_default = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    tm_default = os.path.join(HERE, 'translation_memory.ru.json')
    frag_default = os.path.join(HERE, 'translation_memory.frag.ru.jsonl')
    deny_default = os.path.join(HERE, 'translation_memory.denylist.jsonl')
    rows = {
        'schema': 'pwg.cache_economy_baseline.v1',
        'handoff': 'H2702',
        'source_commit': git_commit(),
        'tracked': [hash_rel(rel) for rel in TRACKED],
        'canonical': [
            hash_resolved('store', canonical_store(store_default)),
            hash_resolved('tm_card', canonical_sidecar(tm_default)),
            hash_resolved('tm_frag', canonical_sidecar(frag_default)),
            hash_resolved('tm_denylist', canonical_sidecar(deny_default)),
        ],
        'notes': (
            'Hashes only. Paths recorded for resolution audit; they are not '
            'identity inputs. Missing gitignored files stay null.'
        ),
    }
    return rows


def write_manifest(path=None):
    path = path or OUT
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = build_manifest()
    payload['manifest_sha256'] = ident.sha256_bytes(ident.canonical_bytes(
        {k: v for k, v in payload.items() if k != 'manifest_sha256'}
    ))
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    return payload


def selftest():
    import tempfile
    payload = build_manifest()
    if not payload['source_commit']:
        raise AssertionError('source commit missing')
    missing_required = [
        row['path'] for row in payload['tracked']
        if row['sha256'] is None and 'H2676' in row['path']
    ]
    if missing_required:
        raise AssertionError('H2676 cohort files missing: %s' % missing_required)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'manifest.json')
        written = write_manifest(path)
        again = ident.sha256_file(path)
        if again is None or written.get('manifest_sha256') is None:
            raise AssertionError('baseline manifest not written')
    print('cache_baseline_freeze: PASS commit=%s files=%d' % (
        payload['source_commit'][:12], len(payload['tracked'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(selftest() if '--selftest' in sys.argv or len(sys.argv) == 1
                     else write_manifest() or 0)
