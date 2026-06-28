#!/usr/bin/env python
"""Validate an immutable edition directory and manifest hashes.

  python validate_release.py release/edition_v1

The argument is an edition subdirectory created by make_edition_cut.py, not the
staging release/ directory that holds generated interop artifacts.
"""
import argparse
import json
import os
import sys
import hashlib
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REQUIRED = {
    'assembled_cards.jsonl',
    'tei_lex0.xml',
    'ontolex.ttl',
    'reverse_index.jsonl',
    'CITATION.cff',
    'DOI_PLAN.md',
    'schemas/pwg_ru_final_card.schema.json',
    'roadmap/quality_gates.jsonl',
    'roadmap/scientific_hardening.json',
}
REQUIRED_GATES = {'G%d_' % i for i in range(1, 11)}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def fail(msg):
    raise ValueError(msg)


def count_jsonl(path, required):
    n = 0
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            for field in required:
                if not row.get(field):
                    fail('%s line %d missing %s' % (path, i, field))
            n += 1
    if not n:
        fail('%s is empty' % path)
    return n


def load_gate_statuses(path):
    statuses = {}
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            gid = row.get('id')
            if not gid:
                fail('quality_gates.jsonl line %d missing id' % i)
            statuses[gid] = row.get('status')
    return statuses


def validate_gate_statuses(edition_dir, manifest):
    got = manifest.get('gate_statuses')
    if not isinstance(got, dict) or not got:
        fail('manifest gate_statuses must be a non-empty object')
    bad_keys = [k for k in got if not k or k == 'null']
    if bad_keys:
        fail('manifest gate_statuses contains empty/null key(s)')
    expected = load_gate_statuses(os.path.join(edition_dir, 'roadmap', 'quality_gates.jsonl'))
    missing_prefixes = sorted(p for p in REQUIRED_GATES if not any(k.startswith(p) for k in got))
    if missing_prefixes:
        fail('manifest gate_statuses missing gates: %s' % ', '.join(missing_prefixes))
    if got != expected:
        fail('manifest gate_statuses do not match edition roadmap/quality_gates.jsonl')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('edition_dir')
    args = ap.parse_args()
    manifest_path = os.path.join(args.edition_dir, 'release_manifest.json')
    if not os.path.exists(manifest_path):
        editions = []
        if os.path.isdir(args.edition_dir):
            editions = sorted(name for name in os.listdir(args.edition_dir)
                              if name.startswith('edition_')
                              and os.path.isdir(os.path.join(args.edition_dir, name)))
        hint = ('; validate an edition subdirectory created by make_edition_cut.py, '
                'for example release/edition_v1')
        if editions:
            hint += '; found edition candidate(s): %s' % ', '.join(editions)
        fail('missing release_manifest.json%s' % hint)
    manifest = json.load(open(manifest_path, encoding='utf-8'))
    validate_gate_statuses(args.edition_dir, manifest)
    files = manifest.get('files') or {}
    missing = sorted(REQUIRED - set(files))
    if missing:
        fail('manifest missing required files: %s' % ', '.join(missing))
    for rel, meta in files.items():
        path = os.path.join(args.edition_dir, rel.replace('/', os.sep))
        if not os.path.exists(path):
            fail('manifest file missing on disk: %s' % rel)
        got = sha256(path)
        if got != meta.get('sha256'):
            fail('hash mismatch for %s' % rel)

    ET.parse(os.path.join(args.edition_dir, 'tei_lex0.xml'))
    ttl = open(os.path.join(args.edition_dir, 'ontolex.ttl'), encoding='utf-8').read()
    if 'ontolex:LexicalEntry' not in ttl:
        fail('OntoLex file contains no lexical entries')
    cards = count_jsonl(os.path.join(args.edition_dir, 'assembled_cards.jsonl'), ('key1', 'records'))
    reverse = count_jsonl(os.path.join(args.edition_dir, 'reverse_index.jsonl'), ('ru', 'key1'))
    print('release validation OK: edition=%s | files=%d | cards=%d | reverse rows=%d'
          % (manifest.get('edition_id'), len(files), cards, reverse))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('RELEASE CHECK FAILED: %s' % e, file=sys.stderr)
        raise SystemExit(1)
