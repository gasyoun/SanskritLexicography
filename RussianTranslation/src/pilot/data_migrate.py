#!/usr/bin/env python
r"""Migrate the inventoried working set into a pwg-ru-data checkout (H2175 step 3).

Consumes ``data_inventory.json`` (data_inventory.py, hashed run), copies every
``migrate`` row into the target clone's bucket, packs the NWS layer as ONE
``layers/nws.tar.gz`` (168k blobs would poison git/LFS), re-hashes everything on
the destination, and writes a byte-parity report to
``<target>/telemetry/migration_parity_<date>.json``. Refuses to finish dirty:

  * any copy whose destination hash differs from the recorded source hash FAILS
    the run (a live writer raced us — re-run after pausing the lane);
  * the SECRETS SCAN walks the migrated tree for credential shapes (.env bodies,
    api keys, OAuth/refresh tokens, Claude profile dirs) and a hit is FATAL
    (fence R4.3d: profile dirs and creds move by scp only, never through git).

``--verify`` mode re-hashes an existing clone against the parity report — the
acceptance check for "100% byte-parity between local set and fresh clone".
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

SCHEMA = 'pwg.migration_parity.v1'

SECRET_PATTERNS = [
    (re.compile(r'\bsk-[A-Za-z0-9]{20,}'), 'api key (sk-...)'),
    (re.compile(r'\b(api[_-]?key|secret|token|password)\s*[=:]\s*[\'"]?[A-Za-z0-9_\-/+]{16,}',
                re.IGNORECASE), 'key=value credential shape'),
    (re.compile(r'oauth[^\n]{0,40}(token|refresh)', re.IGNORECASE), 'oauth token'),
]
SECRET_NAME_PATTERNS = ('.env', 'credentials', '.claude.json', 'oauth')
# migrated payloads legitimately containing the word "token"/dictionary text: only
# scan text-ish files below this size cap; bulk corpus rows are dictionary content.
SECRET_SCAN_MAX_BYTES = 5 * 1024 * 1024


def sha256_file(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def dest_for(row, target):
    rel = row['path']
    name = os.path.basename(rel)
    sub = ''
    # keep the artifacts/ and queue subtree shapes; flat-copy plain files
    for keep in ('output/coordinator/artifacts/', 'ru_cleanup_queues/'):
        if keep in rel.replace('\\', '/'):
            sub = rel.replace('\\', '/').split(keep, 1)[1]
            sub = os.path.dirname(os.path.join(keep.rstrip('/').split('/')[-1], sub))
            break
    return os.path.join(target, row['bucket'], sub, name)


def pack_nws(src_dir, target):
    """Pack the NWS layer -> layers/nws.tar.gz (+ sidecar keys manifest copy)."""
    out = os.path.join(target, 'layers', 'nws.tar.gz')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with tarfile.open(out, 'w:gz') as tf:
        tf.add(src_dir, arcname='nws')
    return out


def secrets_scan(target):
    """Credential shapes anywhere in the migrated tree -> list of findings."""
    findings = []
    for dirpath, dirs, files in os.walk(target):
        if '.git' in dirs:
            dirs.remove('.git')
        for name in files:
            path = os.path.join(dirpath, name)
            lower = name.lower()
            if any(p in lower for p in SECRET_NAME_PATTERNS):
                findings.append({'path': path, 'kind': 'suspicious filename'})
                continue
            try:
                if os.path.getsize(path) > SECRET_SCAN_MAX_BYTES:
                    continue
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            except OSError:
                continue
            for rex, kind in SECRET_PATTERNS:
                m = rex.search(text)
                if m:
                    findings.append({'path': path, 'kind': kind,
                                     'excerpt': m.group(0)[:12] + '…'})
                    break
    return findings


def migrate(inventory, target, rt_root=None):
    rt_root = rt_root or inventory['rt_root']
    copied, mismatches, packed = [], [], []
    for row in inventory['rows']:
        cls = row.get('class', '')
        if row.get('status') != 'present' or not cls.startswith('migrate'):
            continue
        src = os.path.join(rt_root, row['path'])
        if cls == 'migrate-packed':
            out = pack_nws(src, target)
            packed.append({'src': row['path'], 'dest': os.path.relpath(out, target),
                           'sha256': sha256_file(out),
                           'source_file_count': row.get('file_count')})
            continue
        if os.path.isdir(src):
            # aggregate directory row (e.g. coordinator artifacts/**): copy the tree,
            # per-file parity (source hashed at copy time — the inventory's aggregate
            # row carries no per-file hashes by design)
            for dirpath, _dirs, files in os.walk(src):
                for name in files:
                    fsrc = os.path.join(dirpath, name)
                    rel = os.path.relpath(fsrc, src).replace('\\', '/')
                    dest = os.path.join(target, row['bucket'],
                                        os.path.basename(src.rstrip('/\\')), rel)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    want = sha256_file(fsrc)
                    shutil.copyfile(fsrc, dest)
                    got = sha256_file(dest)
                    entry = {'src': row['path'] + '/' + rel,
                             'dest': os.path.relpath(dest, target),
                             'sha256': want, 'size': os.path.getsize(dest)}
                    (copied if got == want else mismatches).append(entry)
            continue
        dest = dest_for(row, target)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(src, dest)
        got = sha256_file(dest)
        want = row.get('sha256') or sha256_file(src)
        entry = {'src': row['path'], 'dest': os.path.relpath(dest, target),
                 'sha256': want, 'size': row.get('size')}
        if got != want:
            entry['dest_sha256'] = got
            mismatches.append(entry)
        else:
            copied.append(entry)
    return copied, mismatches, packed


def write_report(target, copied, mismatches, packed, secrets):
    date = time.strftime('%Y-%m-%d', time.gmtime())
    report = {'schema': SCHEMA, 'generated_at': int(time.time()), 'date': date,
              'copied': len(copied), 'mismatches': mismatches,
              'packed': packed, 'secrets_findings': secrets,
              'parity_ok': not mismatches, 'secrets_ok': not secrets,
              'files': copied}
    out = os.path.join(target, 'telemetry', 'migration_parity_%s.json' % date)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, out)
    return out, report


def verify(target, report_path):
    """Re-hash an existing clone against a parity report -> (ok, bad_list)."""
    report = json.load(open(report_path, encoding='utf-8'))
    bad = []
    for entry in report['files'] + report.get('packed', []):
        dest = os.path.join(target, entry['dest'])
        if not os.path.exists(dest):
            bad.append({'dest': entry['dest'], 'problem': 'MISSING'})
        elif sha256_file(dest) != entry['sha256']:
            bad.append({'dest': entry['dest'], 'problem': 'HASH MISMATCH'})
    return not bad, bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory', help='data_inventory.json (hashed run)')
    ap.add_argument('--target', help='pwg-ru-data checkout root')
    ap.add_argument('--rt-root', default=None,
                    help='override the inventory\'s recorded RussianTranslation root')
    ap.add_argument('--verify', metavar='PARITY_REPORT',
                    help='verify an existing clone against a parity report; no copies')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.target:
        ap.error('--target is required')
    if args.verify:
        ok, bad = verify(args.target, args.verify)
        print(json.dumps({'verify_ok': ok, 'bad': bad}, ensure_ascii=False, indent=1))
        return 0 if ok else 1
    if not args.inventory:
        ap.error('--inventory is required (run data_inventory.py first)')
    inventory = json.load(open(args.inventory, encoding='utf-8'))
    copied, mismatches, packed = migrate(inventory, args.target, rt_root=args.rt_root)
    secrets = secrets_scan(args.target)
    out, report = write_report(args.target, copied, mismatches, packed, secrets)
    print('migrated %d files + %d packed archives -> %s' % (len(copied), len(packed),
                                                            args.target))
    print('parity: %s   secrets: %s   report: %s'
          % ('OK' if report['parity_ok'] else 'FAIL (%d mismatches)' % len(mismatches),
             'CLEAN' if report['secrets_ok'] else 'FINDINGS — DO NOT PUSH', out))
    if not report['parity_ok'] or not report['secrets_ok']:
        return 1
    return 0


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rt = os.path.join(td, 'rt')
        os.makedirs(os.path.join(rt, 'src', 'pilot', 'nws'))
        os.makedirs(os.path.join(rt, 'src', 'pilot', 'input'))
        store = os.path.join(rt, 'src', 'pwg_ru_translated.jsonl')
        with open(store, 'w', encoding='utf-8', newline='\n') as f:
            f.write('{"subcard":"a","ru":"x"}\n')
        with open(os.path.join(rt, 'src', 'pilot', 'input', 'a.raw.txt'), 'w',
                  encoding='utf-8') as f:
            f.write('raw payload')
        for i in range(4):
            with open(os.path.join(rt, 'src', 'pilot', 'nws', 'k%d.json' % i), 'w',
                      encoding='utf-8') as f:
                f.write('{"n":%d}' % i)
        inv = {'schema': 'pwg.data_inventory.v1', 'rt_root': rt, 'rows': [
            {'path': 'src/pwg_ru_translated.jsonl', 'bucket': 'tm', 'class': 'migrate',
             'status': 'present', 'sha256': sha256_file(store), 'size': 24},
            {'path': 'src/pilot/input/a.raw.txt', 'bucket': 'raws', 'class': 'migrate',
             'status': 'present', 'sha256': None, 'size': 11},
            {'path': 'src/pilot/nws', 'bucket': 'layers', 'class': 'migrate-packed',
             'status': 'present', 'file_count': 4, 'aggregate': True},
            {'path': 'src/pilot/output/coordinator/artifacts', 'bucket': 'manifests',
             'class': 'migrate', 'status': 'present', 'aggregate': True},
        ]}
        adir = os.path.join(rt, 'src', 'pilot', 'output', 'coordinator', 'artifacts',
                            'lease1')
        os.makedirs(adir)
        with open(os.path.join(adir, 'execution_manifest.lease1.json'), 'w',
                  encoding='utf-8', newline='\n') as f:
            f.write('{"schema":"v2"}')
        target = os.path.join(td, 'clone')
        copied, mismatches, packed = migrate(inv, target)
        assert len(copied) == 3 and not mismatches and len(packed) == 1
        assert os.path.exists(os.path.join(
            target, 'manifests', 'artifacts', 'lease1',
            'execution_manifest.lease1.json')), 'aggregate dir tree not copied'
        assert os.path.exists(os.path.join(target, 'tm', 'pwg_ru_translated.jsonl'))
        assert os.path.exists(os.path.join(target, 'layers', 'nws.tar.gz'))
        with tarfile.open(os.path.join(target, 'layers', 'nws.tar.gz')) as tf:
            assert len([m for m in tf.getmembers() if m.isfile()]) == 4
        # clean tree -> clean scan; report written; verify OK
        secrets = secrets_scan(target)
        assert not secrets, secrets
        out, report = write_report(target, copied, mismatches, packed, secrets)
        assert report['parity_ok'] and report['secrets_ok']
        ok, bad = verify(target, out)
        assert ok, bad
        # verify catches a mutated clone
        with open(os.path.join(target, 'tm', 'pwg_ru_translated.jsonl'), 'a',
                  encoding='utf-8') as f:
            f.write('tampered\n')
        ok2, bad2 = verify(target, out)
        assert not ok2 and bad2[0]['problem'] == 'HASH MISMATCH'
        # a planted credential is FATAL
        with open(os.path.join(target, 'raws', 'oops.txt'), 'w', encoding='utf-8') as f:
            f.write('DEEPSEEK_API_KEY=sk-abcdefghijklmnopqrstuvwx123456\n')
        findings = secrets_scan(target)
        assert findings, 'planted credential must be found'
        # a live-writer race surfaces as a mismatch, not a silent pass
        with open(store, 'a', encoding='utf-8') as f:
            f.write('{"subcard":"b","ru":"y"}\n')      # source changed after hashing
        _c2, mism2, _p2 = migrate(inv, os.path.join(td, 'clone2'))
        assert mism2 and mism2[0]['src'] == 'src/pwg_ru_translated.jsonl'
    print('data_migrate selftest: PASS (copy+parity, NWS packing, verify catches '
          'tamper, secrets scan catches creds, racing writer surfaces as mismatch)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
