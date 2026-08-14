#!/usr/bin/env python
"""Build the immutable H2685 four-format release pack.

  python src/pwg_tm_release.py
  python src/pwg_tm_release.py --limit 20
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402
import pwg_tm_export_core as X  # noqa: E402
import pwg_tm_export_loss as L  # noqa: E402

CREATED = '2026-08-14T12:00:00Z'
RELEASE_ID = 'pwg-tm-canonical-v1.0.0'
WAVE1_RECEIPT = os.path.join(
    C.DEFAULT_OUT_DIR, 'wave1_b_receipt', 'quality_report.json')
WAVE1_RECON = os.path.join(
    C.DEFAULT_OUT_DIR, 'wave1_b_receipt', 'reconciliation.json')
PRIORITY = os.path.join(C.DEFAULT_OUT_DIR, 'priority_5000.denominators.json')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def coverage_block():
    cov = {
        'publication_green': {
            'records': C.EXPECTED_PUBLICATION_COUNT,
            'exact_card': C.EXPECTED_EXACT_CARD,
            'exact_fragment': C.EXPECTED_EXACT_FRAGMENT,
            'quality': 'canonical_migrated_lossless',
            'independent_gate': 'not_applicable_legacy_publication',
        },
        'wave1_5000': {
            'published_as': 'coverage_denominator_only_not_green_export',
            'reason': (
                'H2684 independent n=400 failed the serious-error floor '
                '(2.5% > 1%) after one repair. Wave-1 promoted fragments '
                'are not in the four-format green release.'
            ),
        },
    }
    if os.path.exists(PRIORITY):
        with open(PRIORITY, encoding='utf-8') as f:
            cov['priority'] = json.load(f)
    if os.path.exists(WAVE1_RECON):
        with open(WAVE1_RECON, encoding='utf-8') as f:
            recon = json.load(f)
        cov['wave1_5000'].update({
            'keys': recon.get('processed_keys') or recon.get('queue_keys') or 5000,
            'fragments_accounted': recon.get('accounted_fragments')
            or recon.get('extracted_fragments'),
            'promoted': recon.get('promoted_fragments'),
            'quarantine': recon.get('quarantine_fragments'),
            'silent_drops': recon.get('silent_drops'),
            'manifest_sha256': recon.get('manifest_sha256'),
        })
    if os.path.exists(WAVE1_RECEIPT):
        with open(WAVE1_RECEIPT, encoding='utf-8') as f:
            q = json.load(f)
        cov['wave1_5000']['independent_gate'] = q.get('independent_gate')
        cov['wave1_5000']['floors'] = q.get('floors')
        cov['wave1_5000']['reasons'] = q.get('reasons')
    return cov


def rights_facts():
    return {
        'policy': 'STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026',
        'source_status': 'public_domain',
        'translation_status': 'own_machine_translation_of_pd_source',
        'block_class': None,
        'facts': list(C.RIGHTS_FACTS),
        'license_data': 'CC-BY-4.0',
        'license_source_pwg': 'Public Domain Mark 1.0',
        'secrets_private_data': False,
        'restricted_designation': False,
        'publish_safety': 'GO',
    }


def build(out_dir, canonical, limit=None):
    os.makedirs(out_dir, exist_ok=True)
    rows = X.load_canonical(canonical, limit=limit)
    stamp = CREATED
    tmx = os.path.join(out_dir, 'pwg_tm.de-ru.tmx')
    tei = os.path.join(out_dir, 'pwg_tm.tei.lex0.xml')
    ttl = os.path.join(out_dir, 'pwg_tm.ontolex.ttl')
    jsonl = os.path.join(out_dir, 'canonical.v1.jsonl')
    if os.path.abspath(canonical) != os.path.abspath(jsonl):
        shutil.copyfile(canonical, jsonl)
    X.write_text(tmx, X.build_tmx(rows, canonical, stamp))
    X.write_text(tei, X.build_tei(rows, stamp, canonical))
    X.write_text(ttl, X.build_ontolex(rows, stamp))

    ledger_path = os.path.join(out_dir, 'loss_ledger.json')
    report = L.run(jsonl, tmx, tei, ttl, ledger_path, limit=limit)

    files = [
        'canonical.v1.jsonl', 'pwg_tm.de-ru.tmx',
        'pwg_tm.tei.lex0.xml', 'pwg_tm.ontolex.ttl',
        'loss_ledger.json',
    ]
    checksums = {}
    for name in files:
        checksums[name] = sha256_file(os.path.join(out_dir, name))

    sums_path = os.path.join(out_dir, 'SHA256SUMS')
    with open(sums_path, 'w', encoding='utf-8', newline='\n') as f:
        for name in files:
            f.write('%s  %s\n' % (checksums[name], name))
    checksums['SHA256SUMS'] = sha256_file(sums_path)

    cov = coverage_block()
    C.write_json(os.path.join(out_dir, 'coverage.json'), cov)
    checksums['coverage.json'] = sha256_file(os.path.join(out_dir, 'coverage.json'))

    manifest = {
        'schema': 'pwg.tm.release.v1',
        'release_id': RELEASE_ID,
        'created': stamp,
        'pipeline_version': X.PIPELINE_VERSION,
        'canonical_schema': C.SCHEMA,
        'record_count': len(rows),
        'expected_publication_count': C.EXPECTED_PUBLICATION_COUNT,
        'limit': limit,
        'formats': ['jsonl', 'tmx-1.4b', 'tei-lex0', 'ontolex-lemon'],
        'loss_ok': report['ok'],
        'lost_count': report['lost_count'],
        'checksums_sha256': checksums,
        'coverage': cov,
        'rights': rights_facts(),
        'doi': {
            'concept': 'pending',
            'version': 'pending',
            'note': 'Zenodo mint when credentials permit; hashes frozen first.',
        },
        'github_release': 'pending',
        'supersedes': [],
    }
    C.write_json(os.path.join(out_dir, 'manifest.json'), manifest)
    return manifest, report


def main():
    ap = argparse.ArgumentParser(description='H2685 immutable four-format release pack')
    ap.add_argument('--out-dir', default=X.DEFAULT_RELEASE)
    ap.add_argument('--canonical', default=X.DEFAULT_CANONICAL)
    ap.add_argument('--limit', type=int, default=None)
    a = ap.parse_args()
    if not os.path.exists(a.canonical):
        sys.exit('canonical JSONL not found: %s' % a.canonical)
    manifest, report = build(a.out_dir, a.canonical, limit=a.limit)
    print('pwg_tm_release: %s records=%d loss_ok=%s -> %s' % (
        manifest['release_id'], manifest['record_count'],
        report['ok'], a.out_dir))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
