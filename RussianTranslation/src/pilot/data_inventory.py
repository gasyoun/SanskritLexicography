#!/usr/bin/env python
r"""Inventory the PWG->RU local-only working set for migration (H2175 step 1, R2.2).

Walks the RussianTranslation data surfaces in a MAIN checkout and emits
``data_inventory.json``: one row per item (path, size, sha256, class, target bucket
in gasyoun/pwg-ru-data, rights note). No moves, no writes outside --out.

Classes:
  migrate           local-only + load-bearing -> goes to the private data repo
  exclude-regen     regenerable derived cache/backup -> stays local (writer recorded)
  exclude-tracked   already tracked in a git repo (this one or csl-orig)
  exclude-secret    credentials/profile material -> NEVER in any repo (fence R4.3d)
  defer             local-only but outside the wave-1 pipeline scope (review sheets,
                    research chains) -> revisit deliberately, never by accident

Buckets mirror data_root.py's layout (+ corpus/ for the corpus-gate dictionaries,
a documented wave-1 addition): layers/ tm/ manifests/ raws/ telemetry/ gatelogs/
parked/ corpus/.

The NWS layer (~168k small JSON files, 35.5 MB) is inventoried as ONE aggregate
row and migrated as a packed tar.gz — 168k blobs is the worst shape for git/LFS,
and layer_versions.py already treats the file count as the cost driver.
"""
import argparse
import fnmatch
import glob
import hashlib
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

SCHEMA = 'pwg.data_inventory.v1'

# (relative-to-RussianTranslation glob, bucket, class, rights, note)
# Rights vocabulary: 'own' (project-authored), 'pd' (public domain source),
# 'mixed-copyright' (modern in-copyright material present -> PRIVATE repo only),
# 'secret' (never in git).
CLASS_MAP = [
    # --- tm/ : the crown jewel + hand-curated sidecar -------------------------
    ('src/pwg_ru_translated.jsonl', 'tm', 'migrate', 'own',
     'THE canonical store; promoter-only writes; LFS'),
    ('src/pilot/translation_memory.denylist.jsonl', 'tm', 'migrate', 'own',
     'hand-curated denylist — NOT derivable'),
    ('src/pilot/translation_memory.*.json', None, 'exclude-regen', 'own',
     'rebuild: translation_memory.py build'),
    ('src/pilot/translation_memory.frag.*.jsonl', None, 'exclude-regen', 'own',
     'rebuild: translation_memory.py build-frags'),
    ('src/pwg_ru_translated.jsonl.*.bak', None, 'exclude-regen', 'own',
     '995 MB of pre-merge safety snapshots; never a deliverable'),
    ('src/pwg_ru_translated.jsonl.*.keep', None, 'exclude-regen', 'own', 'ditto'),
    # --- layers/ : NWS is the only local-only layer ---------------------------
    ('src/pilot/nws', 'layers', 'migrate-packed', 'pd',
     'Halle NWS scrape, ~168k files -> pack as layers/nws.tar.gz + keys manifest'),
    # PW/SCH/PWKVN/PWG are tracked in the sibling csl-orig repo (read live).
    ('../csl-orig/v02/pwg/pwg.txt', None, 'exclude-tracked', 'pd', 'csl-orig upstream'),
    # --- raws/ : the literal window input payloads ----------------------------
    ('src/pilot/input/*.raw.txt', 'raws', 'migrate', 'mixed-copyright',
     'window prompt payloads (PWG German)'),
    ('src/pilot/input/*.portrait.json', 'raws', 'migrate', 'mixed-copyright', ''),
    ('src/pilot/input/*.rootmap.json', 'raws', 'migrate', 'own', ''),
    # --- manifests/ : coordinator state + window plans ------------------------
    ('src/pilot/output/coordinator/state.json', 'manifests', 'migrate', 'own',
     'live lease state (DirLock-owned)'),
    ('src/pilot/output/coordinator/artifact_registry.jsonl', 'manifests', 'migrate',
     'own', 'artifact provenance'),
    ('src/pilot/output/coordinator/promotions*', 'manifests', 'migrate', 'own', ''),
    ('src/pilot/output/coordinator/artifacts/**', 'manifests', 'migrate', 'own',
     'per-lease manifests, hash-bound to promotions'),
    ('src/pilot/output/scale_manifest.*.json', 'manifests', 'migrate', 'own',
     'the window-plan universe (18 MB)'),
    ('src/pilot/output/coordinator/dashboard.json', None, 'exclude-regen', 'own',
     'rebuild: coordinator.py status'),
    # --- gatelogs/ : receipts, ledgers, queues --------------------------------
    ('src/pilot/output/h963_*_gate0_*', 'gatelogs', 'migrate', 'own',
     'append-only live-gate history, cited by H1110/H1447/H858'),
    ('src/pilot/output/h858_partb_gate0_*', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/gate0_*_probe_events.jsonl', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/window_ledger.jsonl', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/audit_window.report.json', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/audit_window.report.md', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/window_status.json', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/window_status.md', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/requeue*.keys.txt', 'gatelogs', 'migrate', 'own',
     'requeue queues'),
    ('src/pilot/output/requeue.defect.fshas.txt', 'gatelogs', 'migrate', 'own', ''),
    ('src/pilot/output/ru_cleanup_queues/**', 'gatelogs', 'migrate', 'own', ''),
    ('failures/auto_failures.jsonl', 'gatelogs', 'migrate', 'own',
     'auto-captured live incidents'),
    ('src/pilot/output/dashboard_events.jsonl', None, 'exclude-regen', 'own',
     'regenerable telemetry stream'),
    ('src/pilot/output/*.merged.md', None, 'exclude-regen', 'own',
     'rendered wf_output (3k files)'),
    ('src/pilot/output/*.NESTED.md', None, 'exclude-regen', 'own', ''),
    # --- telemetry/ -----------------------------------------------------------
    ('src/pilot/generation_api_probe_log.jsonl', 'telemetry', 'migrate', 'own',
     'tracked-in-git today; the ONE tracked->data-repo move (append-only)'),
    # --- corpus/ : corpus-gate inputs (wave-1 layout addition) ----------------
    ('src/assembled_cards.jsonl', 'corpus', 'migrate', 'mixed-copyright',
     'the ~120k-headword German card set; coordinator.nominal_candidates reads it; LFS'),
    ('src/assembled_cards.quarantine.jsonl', 'corpus', 'migrate', 'own', ''),
    ('src/corpus_lexicon.jsonl', 'corpus', 'migrate', 'mixed-copyright',
     'corpus gate; regenerable only where SamudraManthanam exists; LFS'),
    ('src/kosha_syn.jsonl', 'corpus', 'migrate', 'mixed-copyright', 'LFS'),
    ('src/snap.jsonl', 'corpus', 'migrate', 'mixed-copyright', 'LFS'),
    ('src/apte_hi.jsonl', 'corpus', 'migrate', 'mixed-copyright', 'LFS'),
    ('src/koch.jsonl', 'corpus', 'migrate', 'mixed-copyright', ''),
    ('src/kow.jsonl', 'corpus', 'migrate', 'mixed-copyright', ''),
    ('src/fri.jsonl', 'corpus', 'migrate', 'pd', ''),
    ('src/smirnov.jsonl', 'corpus', 'migrate', 'mixed-copyright', ''),
    ('src/kna.jsonl', 'corpus', 'migrate', 'mixed-copyright', ''),
    ('src/vedic_rituals_hi.jsonl', 'corpus', 'migrate', 'mixed-copyright', ''),
    ('src/grin*.jsonl', 'corpus', 'migrate', 'mixed-copyright', ''),
    ('src/meulenbeld_plants.jsonl', 'corpus', 'migrate', 'mixed-copyright', ''),
    # --- secrets: named so the scan is explicit, never silent -----------------
    ('src/.env', None, 'exclude-secret', 'secret',
     'API keys — NEVER in git; lanes read env/.secrets (R2.2/R4.3d)'),
    # --- deliberate deferrals (outside wave-1 pipeline scope) -----------------
    ('review/*_sheet.html', None, 'defer', 'mixed-copyright',
     'embed unpublished store text; personal voting artifacts'),
    ('pwg_ru/eval/**', None, 'defer', 'mixed-copyright', ''),
    ('gold/reviewer_packets/**', None, 'defer', 'mixed-copyright', ''),
    ('src/*.renou.jsonl', None, 'defer', 'mixed-copyright',
     'Renou research chain (536 MB), not the window pipeline'),
    ('src/assembled_cards.renou.bhs.wl.jsonl', None, 'defer', 'mixed-copyright', ''),
    ('glossary/**', None, 'defer', 'mixed-copyright',
     'belongs to gasyoun/SanskritRussian'),
    ('src/pilot/translate/**', None, 'exclude-regen', 'own',
     'superseded per-key route (Jun-2026), forensics only'),
]


def sha256_file(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def dir_stats(root):
    """(file_count, total_bytes) for an aggregate directory row — no per-file hashing."""
    count = total = 0
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
                count += 1
            except OSError:
                pass
    return count, total


def expand(rt_root, pattern):
    base = os.path.normpath(os.path.join(rt_root, pattern))
    if os.path.isdir(base):
        return [base]
    return sorted(glob.glob(base, recursive=True))


def build_inventory(rt_root, do_hash=True):
    rows, seen = [], set()
    for pattern, bucket, cls, rights, note in CLASS_MAP:
        matches = expand(rt_root, pattern)
        if not matches:
            rows.append({'pattern': pattern, 'bucket': bucket, 'class': cls,
                         'rights': rights, 'note': note, 'status': 'ABSENT'})
            continue
        for path in matches:
            key = os.path.normcase(os.path.abspath(path))
            if key in seen:
                continue
            seen.add(key)
            rel = os.path.relpath(path, rt_root).replace('\\', '/')
            row = {'pattern': pattern, 'path': rel, 'bucket': bucket, 'class': cls,
                   'rights': rights, 'note': note, 'status': 'present'}
            if os.path.isdir(path):
                count, total = dir_stats(path)
                row.update({'file_count': count, 'size': total, 'sha256': None,
                            'aggregate': True})
            else:
                row['size'] = os.path.getsize(path)
                row['sha256'] = (sha256_file(path)
                                 if do_hash and cls.startswith('migrate') else None)
            rows.append(row)
    migrate_rows = [r for r in rows if r.get('class', '').startswith('migrate')
                    and r.get('status') == 'present']
    summary = {
        'migrate_files': sum(r.get('file_count', 1) for r in migrate_rows),
        'migrate_bytes': sum(r.get('size', 0) for r in migrate_rows),
        'by_class': {},
        'by_bucket': {},
    }
    for r in rows:
        if r.get('status') != 'present':
            continue
        summary['by_class'].setdefault(r['class'], [0, 0])
        summary['by_class'][r['class']][0] += r.get('file_count', 1)
        summary['by_class'][r['class']][1] += r.get('size', 0)
        if r.get('bucket'):
            summary['by_bucket'].setdefault(r['bucket'], [0, 0])
            summary['by_bucket'][r['bucket']][0] += r.get('file_count', 1)
            summary['by_bucket'][r['bucket']][1] += r.get('size', 0)
    return {'schema': SCHEMA, 'generated_at': int(time.time()),
            'rt_root': os.path.abspath(rt_root), 'hashed': do_hash,
            'summary': summary, 'rows': rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rt-root', default=None,
                    help='RussianTranslation dir of the MAIN tree (default: resolve '
                         'the main checkout from this file via store_path)')
    ap.add_argument('--out', default='data_inventory.json')
    ap.add_argument('--no-hash', action='store_true',
                    help='skip sha256 (fast census mode)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    rt_root = args.rt_root
    if not rt_root:
        sys.path.insert(0, os.path.dirname(HERE))
        from store_path import main_worktree_root
        main = main_worktree_root(HERE)
        rt_root = (os.path.join(main, 'RussianTranslation') if main
                   else os.path.normpath(os.path.join(HERE, '..', '..')))
    inv = build_inventory(rt_root, do_hash=not args.no_hash)
    tmp = args.out + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(inv, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, args.out)
    s = inv['summary']
    print('inventory: %d files / %.1f MB to migrate -> %s'
          % (s['migrate_files'], s['migrate_bytes'] / 1e6, args.out))
    for bucket, (n, b) in sorted(s['by_bucket'].items()):
        print('  %-10s %6d files %10.1f MB' % (bucket, n, b / 1e6))
    return 0


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # synthetic RT tree exercising file, dir-aggregate, absent, and secret rows
        os.makedirs(os.path.join(td, 'src', 'pilot', 'nws'))
        os.makedirs(os.path.join(td, 'src', 'pilot', 'input'))
        with open(os.path.join(td, 'src', 'pwg_ru_translated.jsonl'), 'w',
                  encoding='utf-8') as f:
            f.write('{"subcard":"a"}\n')
        for i in range(3):
            with open(os.path.join(td, 'src', 'pilot', 'nws', 'k%d.json' % i), 'w',
                      encoding='utf-8') as f:
                f.write('{}')
        with open(os.path.join(td, 'src', 'pilot', 'input', 'a.raw.txt'), 'w',
                  encoding='utf-8') as f:
            f.write('raw')
        with open(os.path.join(td, 'src', '.env'), 'w', encoding='utf-8') as f:
            f.write('DEEPSEEK_API_KEY=sk-secret\n')
        inv = build_inventory(td)
        by_pattern = {}
        for r in inv['rows']:
            by_pattern.setdefault(r['pattern'], []).append(r)
        store = by_pattern['src/pwg_ru_translated.jsonl'][0]
        assert store['class'] == 'migrate' and store['sha256'] and store['bucket'] == 'tm'
        nws = by_pattern['src/pilot/nws'][0]
        assert nws['aggregate'] and nws['file_count'] == 3 and nws['sha256'] is None
        assert nws['class'] == 'migrate-packed'
        env = by_pattern['src/.env'][0]
        assert env['class'] == 'exclude-secret' and env['sha256'] is None, \
            'secret file must never be hashed into a manifest'
        raw = by_pattern['src/pilot/input/*.raw.txt'][0]
        assert raw['class'] == 'migrate' and raw['bucket'] == 'raws'
        absent = [r for r in inv['rows'] if r.get('status') == 'ABSENT']
        assert absent, 'absent patterns must be recorded, not dropped'
        assert inv['summary']['migrate_bytes'] > 0
        assert 'tm' in inv['summary']['by_bucket']
    print('data_inventory selftest: PASS (classes, aggregate NWS row, secret never '
          'hashed, absent recorded, bucket summary)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
