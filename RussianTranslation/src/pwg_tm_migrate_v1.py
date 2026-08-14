#!/usr/bin/env python
"""Migrate publication-grade TM rows into canonical scholarly JSONL v1.

  python src/pwg_tm_migrate_v1.py
  python src/pwg_tm_migrate_v1.py --verify
  python src/pwg_tm_migrate_v1.py --publication PATH --out-dir DIR
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402


def migrate_path(publication, out_dir, generated_at=None):
    rows = C.read_jsonl(publication)
    wrapped = [C.migrate_publication(row, generated_at=generated_at) for row in rows]
    receipt = C.reconcile(rows, wrapped)
    receipt['source_path'] = os.path.relpath(publication, C.ROOT).replace('\\', '/')
    receipt['source_sha256'] = C.sha256_file(publication)
    out_jsonl = os.path.join(out_dir, 'canonical.v1.jsonl')
    C.write_jsonl(out_jsonl, wrapped)
    receipt['artifact'] = os.path.relpath(out_jsonl, C.ROOT).replace('\\', '/')
    receipt['artifact_sha256'] = C.sha256_file(out_jsonl)
    receipt['expected_count'] = C.EXPECTED_PUBLICATION_COUNT
    C.write_json(os.path.join(out_dir, 'reconciliation.v1.json'), receipt)
    return wrapped, receipt, out_jsonl


def fixture_path():
    return os.path.join(C.ROOT, 'schemas', 'fixtures',
                        'pwg_tm_canonical.publication.fixture.jsonl')


def verify_fixture():
    path = fixture_path()
    if not os.path.exists(path):
        return False, 'missing fixture ' + path
    with tempfile.TemporaryDirectory() as tmp:
        wrapped, receipt, _out = migrate_path(path, tmp, generated_at='1970-01-01T00:00:00Z')
    if not receipt['ok']:
        return False, 'fixture reconcile failed: %s' % receipt
    if len(wrapped) != 2:
        return False, 'fixture expected 2 rows, got %d' % len(wrapped)
    ids = [row['record_id'] for row in wrapped]
    if len(set(ids)) != 2:
        return False, 'fixture record_id not unique'
    again = [C.migrate_publication(row, generated_at='1970-01-01T00:00:00Z')
             for row in C.read_jsonl(path)]
    if [r['record_id'] for r in again] != ids:
        return False, 'fixture IDs not deterministic'
    schema = C.load_schema()
    for row in wrapped:
        ok, why = C.validate_jsonschema(row, schema)
        if not ok:
            return False, 'fixture schema: ' + why
    return True, 'fixture-ok %d' % len(wrapped)


def verify_live(publication):
    if not os.path.exists(publication):
        return False, 'publication missing: ' + publication
    with tempfile.TemporaryDirectory() as tmp:
        wrapped, receipt, _out = migrate_path(
            publication, tmp, generated_at='1970-01-01T00:00:00Z')
    if receipt['in_count'] != C.EXPECTED_PUBLICATION_COUNT:
        return False, 'expected %d publication rows, got %d (source drift/corruption)' % (
            C.EXPECTED_PUBLICATION_COUNT, receipt['in_count'])
    if receipt['in_types'].get('exact_card') != C.EXPECTED_EXACT_CARD:
        return False, 'exact_card count drifted: %s' % receipt['in_types']
    if receipt['in_types'].get('exact_fragment') != C.EXPECTED_EXACT_FRAGMENT:
        return False, 'exact_fragment count drifted: %s' % receipt['in_types']
    if not receipt['ok']:
        return False, 'live reconcile failed: %s' % {
            k: receipt[k] for k in (
                'in_count', 'out_count', 'orphan_source_ids', 'orphan_canonical_ids',
                'duplicate_record_ids', 'lost_field_records', 'invalid',
            )
        }
    schema = C.load_schema()
    for row in wrapped[:3] + wrapped[-3:]:
        ok, why = C.validate_jsonschema(row, schema)
        if not ok:
            return False, 'live schema: ' + why
    return True, 'live-ok %d/%d' % (receipt['out_count'], receipt['in_count'])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--publication', default=C.DEFAULT_PUBLICATION)
    ap.add_argument('--out-dir', default=C.DEFAULT_OUT_DIR)
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args(argv)
    if args.verify:
        ok_f, msg_f = verify_fixture()
        print('fixture:', msg_f)
        ok_l, msg_l = verify_live(args.publication)
        print('live:', msg_l)
        if not (ok_f and ok_l):
            return 1
        return 0
    wrapped, receipt, out_jsonl = migrate_path(args.publication, args.out_dir)
    print('migrated %d -> %s ok=%s' % (len(wrapped), out_jsonl, receipt['ok']))
    if not receipt['ok']:
        return 1
    if receipt['in_count'] != C.EXPECTED_PUBLICATION_COUNT:
        print('WARN: expected %d rows, got %d' % (
            C.EXPECTED_PUBLICATION_COUNT, receipt['in_count']), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
