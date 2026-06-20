#!/usr/bin/env python
"""Create an immutable release edition directory with a manifest.

  python make_edition_cut.py edition_v1
  python make_edition_cut.py edition_fixture --cards src/fixtures/assembled_fixture.jsonl --release-root C:/tmp/pwg_release
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_RELEASE = os.path.join(ROOT, 'release')
DEFAULT_CARDS = os.path.join(HERE, 'assembled_cards.jsonl')
INTEROP = ('tei_lex0.xml', 'ontolex.ttl', 'reverse_index.jsonl')


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError('%s\n%s' % (' '.join(cmd), r.stderr.strip() or r.stdout.strip()))
    return r.stdout.strip()


def git_value(args, default='unknown'):
    try:
        out = run(['git'] + args)
        return out or default
    except Exception:
        return default


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def copy_file(src, dst):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src, dst):
    if not os.path.isdir(src):
        raise FileNotFoundError(src)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def ensure_interop(args):
    missing = [name for name in INTEROP if not os.path.exists(os.path.join(args.source_release, name))]
    if missing:
        cmd = [sys.executable, os.path.join(HERE, 'export_interop.py'), 'all',
               '--cards', args.cards, '--out-dir', args.source_release]
        if args.limit:
            cmd += ['--limit', str(args.limit)]
        run(cmd)


def manifest_files(edition_dir):
    files = {}
    for dirpath, _, filenames in os.walk(edition_dir):
        for name in filenames:
            if name == 'release_manifest.json':
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, edition_dir).replace('\\', '/')
            files[rel] = {'sha256': sha256(path), 'bytes': os.path.getsize(path)}
    return dict(sorted(files.items()))


def load_gate_statuses():
    path = os.path.join(ROOT, 'roadmap', 'quality_gates.jsonl')
    statuses = {}
    if not os.path.exists(path):
        return statuses
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                statuses[r.get('id')] = r.get('status')
    return statuses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('edition_id')
    ap.add_argument('--cards', default=DEFAULT_CARDS)
    ap.add_argument('--release-root', default=DEFAULT_RELEASE)
    ap.add_argument('--source-release', default=DEFAULT_RELEASE)
    ap.add_argument('--limit', type=int, default=None,
                    help='fixture mode: generate interop from only the first N cards')
    args = ap.parse_args()
    if not args.edition_id.startswith('edition_'):
        raise SystemExit('edition id should look like edition_v1')

    ensure_interop(args)
    edition_dir = os.path.join(args.release_root, args.edition_id)
    if os.path.exists(edition_dir):
        raise SystemExit('edition already exists: %s' % edition_dir)
    os.makedirs(edition_dir)

    copy_file(args.cards, os.path.join(edition_dir, 'assembled_cards.jsonl'))
    for name in INTEROP:
        copy_file(os.path.join(args.source_release, name), os.path.join(edition_dir, name))
    copy_tree(os.path.join(ROOT, 'schemas'), os.path.join(edition_dir, 'schemas'))
    copy_tree(os.path.join(ROOT, 'roadmap'), os.path.join(edition_dir, 'roadmap'))
    for name in ('CITATION.cff', 'DOI_PLAN.md', 'CHANGELOG.md'):
        copy_file(os.path.join(ROOT, name), os.path.join(edition_dir, name))

    manifest = {
        'edition_id': args.edition_id,
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'source_git_commit': git_value(['rev-parse', 'HEAD']),
        'source_git_dirty': bool(git_value(['status', '--porcelain'], default='')),
        'prompt_hash': 'see per-card provenance and schemas',
        'model_ids': ['claude-sonnet-4-6', 'claude-opus-4-8'],
        'schema_ids': ['pwg_ru.card.v1', 'pwg_ru.final_card.v1'],
        'command_log': [
            'python src/validate_assembled_export.py',
            'python src/export_interop.py all',
            'python src/make_edition_cut.py %s' % args.edition_id,
        ],
        'gate_statuses': load_gate_statuses(),
        'files': manifest_files(edition_dir),
    }
    manifest_path = os.path.join(edition_dir, 'release_manifest.json')
    open(manifest_path, 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('edition cut -> %s' % edition_dir)
    print('manifest files: %d' % len(manifest['files']))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('EDITION CUT FAILED: %s' % e, file=sys.stderr)
        raise SystemExit(1)
