#!/usr/bin/env python
r"""h4055_store_lineage_evidence.py — H4055 evidence builder (offline, zero provider calls).

Produces, under RussianTranslation/reports/:

  H4055_receipt_content_only.json  scratch-store refresh whose row-set counters are ALL
                                   zero while `changed_ru=1` — proof a content-only sync
                                   is no longer byte-shaped like a no-op;
  H4055_receipt_noop.json          scratch-store refresh of byte-identical src/mirror:
                                   `changed_ru=0`, `noop=true`, sha unmoved;
  H4055_store_mirror_box_matrix.json / .md
                                   src/mirror/box evidence matrix: timestamp, sha256,
                                   row count, producing commit and availability for each
                                   surface. A missing-box observation stays MISSING —
                                   equality is never asserted across unobserved boxes,
                                   and a local Git LFS POINTER is never equated with the
                                   hydrated file bytes (the pointer's oid is recorded
                                   beside the hydrated sha instead).

Live state is only ever READ. The canonical store is not written, the real mirror is not
refreshed (the 02-09 refresh already synchronized it; "no refresh required if already
equal"), no ledger row is appended to the real ledger — the fixtures run in temp dirs with
a scratch ledger.

  python tools/h4055_store_lineage_evidence.py            # build all four artifacts
  python tools/h4055_store_lineage_evidence.py --fixtures-only
"""
import argparse
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'src'))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import refresh_tm_mirror as rtm  # noqa: E402

REPORTS = os.path.normpath(os.path.join(HERE, '..', 'reports'))
HANDOFF = 'H4055'
EXECUTOR_MODEL = 'glm-5.3-flash'
EXECUTOR_ROUTE = 'opencode/z-ai (OxAlpha pool)'


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _write_json(path, obj):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('wrote %s' % path)


def run_fixtures(reports):
    """The two acceptance fixtures. Raises on any failed acceptance condition."""
    failures = []
    checks_run = [0]

    def check(name, cond):
        checks_run[0] += 1
        print('  %-52s %s' % (name, 'ok' if cond else 'FAIL'))
        if not cond:
            failures.append(name)

    rows = [
        {'key1': 'k1', 'subcard': 's', 'sense_tag': '1', 'de': 'de1', 'ru': 'один',
         'review_status': 'ai_translated', 'reviewer': None},
        {'key1': 'k2', 'subcard': 's', 'sense_tag': '1', 'de': 'de2', 'ru': 'два',
         'review_status': 'ai_translated', 'reviewer': None},
        {'key1': 'k3', 'subcard': 's', 'sense_tag': '1', 'de': 'de3', 'ru': 'три',
         'review_status': 'ai_translated', 'reviewer': None},
    ]

    def dump(path, rs):
        with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

    with tempfile.TemporaryDirectory(prefix='h4055_') as td:
        led = os.path.join(td, 'scratch_ledger.jsonl')

        # Fixture A: byte-identical no-op.
        src_a = os.path.join(td, 'src_noop.jsonl')
        mir_a = os.path.join(td, 'mirror_noop.jsonl')
        dump(src_a, rows)
        shutil.copy2(src_a, mir_a)
        e_a = rtm.run_refresh(src_a, mir_a, led, HANDOFF, apply=True,
                              receipt=os.path.join(reports, 'H4055_receipt_noop.json'))
        check('noop: changed_ru == 0', e_a['changed_ru'] == 0)
        check('noop: noop is True', e_a['noop'] is True)
        check('noop: row-set counters all zero',
              e_a['only_src_added'] == 0 and e_a['only_mirror_dropped'] == 0)
        check('noop: sha unmoved', e_a['mirror_sha_after'] == e_a['mirror_sha_before'])

        # Fixture B: content-only update — same rid set (all row-set counters stay
        # zero), one ru differs. Pre-H4055 this looked exactly like a no-op.
        src_b = os.path.join(td, 'src_content.jsonl')
        mir_b = os.path.join(td, 'mirror_content.jsonl')
        dump(src_b, rows)
        stale = [dict(r) for r in rows]
        stale[1]['ru'] = 'два (устаревшая правка)'
        dump(mir_b, stale)
        e_b = rtm.run_refresh(src_b, mir_b, led, HANDOFF, apply=True,
                              receipt=os.path.join(reports, 'H4055_receipt_content_only.json'))
        check('content-only: changed_ru == 1 (nonzero)', e_b['changed_ru'] == 1)
        check('content-only: noop is False', e_b['noop'] is False)
        check('content-only: row-set counters all zero',
              e_b['only_src_added'] == 0 and e_b['only_mirror_dropped'] == 0)
        check('content-only: sha moved',
              e_b['mirror_sha_after'] != e_b['mirror_sha_before'])
        check('content-only: stale key carried into receipt',
              e_b['changed_ru_keys'] == [['k2', 's', '1', 'de2']])
        check('content-only: mirror still a BYTE-exact copy of src',
              open(mir_b, 'rb').read() == open(src_b, 'rb').read())
        real_lines = [l for l in io.open(rtm.DEFAULT_LEDGER, encoding='utf-8')
                      if l.strip()]
        check('real ledger untouched by fixtures',
              '"handoff": "H4055"' not in real_lines[-1])

    if failures:
        raise SystemExit('acceptance FAILED: %s' % ', '.join(failures))
    print('acceptance fixtures: PASS (%d checks)' % checks_run[0])
    return e_a, e_b


def _git(datarepo, *args):
    p = subprocess.run(['git', '-C', datarepo, *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       encoding='utf-8', errors='replace')
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


def _lfs_pointer(blob_text):
    out = {}
    for line in blob_text.splitlines():
        if line.startswith('oid sha256:'):
            out['oid_sha256'] = line.split('oid sha256:', 1)[1].strip()
        elif line.startswith('size '):
            out['size'] = int(line.split('size ', 1)[1].strip())
        elif line.startswith('version '):
            out['version'] = line.split('version ', 1)[1].strip()
    return out


def build_matrix():
    mirror = rtm.DEFAULT_MIRROR
    store = rtm.DEFAULT_SRC
    datarepo = os.path.dirname(os.path.dirname(mirror))  # .../pwg-ru-data
    rel_mirror = os.path.relpath(mirror, datarepo)

    m = {
        'handoff': HANDOFF,
        'generated_at': utcnow(),
        'executor': {'model': EXECUTOR_MODEL, 'route': EXECUTOR_ROUTE},
        'box': {'platform': platform.platform(), 'node': platform.node()},
        'provider_calls': 0,
        'live_mutations': 'none — read-only observation; fixtures ran in temp dirs',
        'surfaces': [],
        'lineage_chain': {},
        'cross_box_equality': 'NOT ASSERTED — each unobserved box stays unavailable; '
                              'row counts (11,462 quarantine-era / 11,519 current-ledger) '
                              'are historical sizes, never lineage',
    }

    # 1. canonical src store on THIS box
    m['surfaces'].append({
        'surface': 'src store (canonical pwg_ru_translated.jsonl)', 'box': m['box']['node'],
        'path': store,
        'timestamp': None, 'sha256': None, 'rows': None, 'producing_commit': None,
        'availability': 'MISSING on this box' if not os.path.exists(store)
                        else 'present',
        'note': 'the store is gitignored and lives per-box; its absence here is the '
                'explicit missing-box state, not an error',
    })

    # 2. hydrated mirror working tree on THIS box
    surf = {'surface': 'mirror working tree (hydrated bytes)', 'box': m['box']['node'],
            'path': mirror}
    if os.path.exists(mirror):
        with open(mirror, 'rb') as f:
            head = f.read(64)
        surf.update({
            'timestamp': datetime.datetime.fromtimestamp(
                os.path.getmtime(mirror), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'sha256': rtm.sha256_file(mirror),
            'rows': sum(1 for l in io.open(mirror, encoding='utf-8') if l.strip()),
            'bytes': os.path.getsize(mirror),
            'availability': 'present',
            'hydrated': not head.startswith(b'version https://git-lfs'),
        })
    else:
        surf['availability'] = 'MISSING on this box'
    m['surfaces'].append(surf)

    # 3. mirror git blob: the LFS POINTER is not the bytes
    rc, out, err = _git(datarepo, 'cat-file', 'blob', 'HEAD:%s' % rel_mirror)
    pointer = _lfs_pointer(out) if rc == 0 else {}
    rc2, head_sha, _ = _git(datarepo, 'rev-parse', 'HEAD')
    rc3, subj, _ = _git(datarepo, 'log', '-1', '--format=%s', '--', rel_mirror)
    rc4, date, _ = _git(datarepo, 'log', '-1', '--format=%cI', '--', rel_mirror)
    m['surfaces'].append({
        'surface': 'mirror git blob (LFS pointer — never equated with bytes)',
        'box': '%s @ %s' % (m['box']['node'], datarepo),
        'path': '%s (git blob at HEAD)' % rel_mirror,
        'timestamp': date or None, 'sha256': pointer.get('oid_sha256'),
        'rows': None, 'producing_commit': head_sha or None,
        'producing_commit_subject': subj or None,
        'availability': 'present' if rc == 0 else 'unreadable: %s' % err,
        'lfs_pointer': pointer,
        'pointer_oid_equals_hydrated_sha': bool(
            pointer.get('oid_sha256') and surf.get('sha256')
            and pointer['oid_sha256'] == surf['sha256']),
    })

    # 4. refresh ledger, last entry (the provenance chain anchor)
    last = None
    if os.path.exists(rtm.DEFAULT_LEDGER):
        lines = [l for l in io.open(rtm.DEFAULT_LEDGER, encoding='utf-8') if l.strip()]
        if lines:
            last = json.loads(lines[-1])
    m['surfaces'].append({
        'surface': 'mirror_refresh_ledger.jsonl (last entry)', 'box': m['box']['node'],
        'path': rtm.DEFAULT_LEDGER,
        'timestamp': last['ts'] if last else None,
        'sha256': last.get('mirror_sha_after') if last else None,
        'rows': last.get('mirror_rows_after') if last else None,
        'producing_commit': head_sha or None,
        'availability': 'present' if last else 'MISSING',
        'last_entry': {k: last.get(k) for k in (
            'handoff', 'ts', 'src_rows', 'only_src_added', 'only_mirror_dropped',
            'mirror_sha_before', 'mirror_sha_after')} if last else None,
    })

    # 5-6. the other box: explicitly unavailable
    m['surfaces'].append({
        'surface': 'src store (canonical)', 'box': 'Windows build box',
        'path': 'unknown from this box', 'timestamp': None, 'sha256': None,
        'rows': None, 'producing_commit': None,
        'availability': 'UNAVAILABLE — this box cannot observe it; any equality claim '
                        'would be fabricated',
    })
    m['surfaces'].append({
        'surface': 'mirror working tree', 'box': 'Windows build box',
        'path': 'unknown from this box', 'timestamp': None, 'sha256': None,
        'rows': None, 'producing_commit': None,
        'availability': 'UNAVAILABLE — this box cannot observe it',
    })

    # lineage chain: sha-based, not row-count-based
    mir_sha = surf.get('sha256')
    m['lineage_chain'] = {
        'mirror_hydrated_sha256': mir_sha,
        'ledger_last_mirror_sha_after': last.get('mirror_sha_after') if last else None,
        'lfs_pointer_oid_sha256': pointer.get('oid_sha256'),
        'all_three_agree': bool(mir_sha and last and pointer.get('oid_sha256')
                                and mir_sha == last.get('mirror_sha_after')
                                == pointer.get('oid_sha256')),
        'origin': {},
    }
    rc5, _f, ferr = _git(datarepo, 'fetch', 'origin')
    for ref in ('origin/master', 'origin/main'):
        rc6, oref, _ = _git(datarepo, 'rev-parse', '--verify', ref)
        if rc6 == 0:
            m['lineage_chain']['origin'] = {
                'ref': ref, 'head': oref,
                'availability': 'fetch %s' % ('ok' if rc5 == 0 else 'FAILED: %s' % ferr.strip())}
            break
    else:
        m['lineage_chain']['origin'] = {'availability': 'no origin ref resolvable'}
    return m


def matrix_md(m):
    lines = ['# H4055 — src/mirror/box evidence matrix',
             '',
             '_Generated: %s · executor: %s (%s) · zero provider calls · live state read-only_' % (
                 m['generated_at'], m['executor']['model'], m['executor']['route']),
             '',
             '| surface | box | timestamp | sha256 | rows | producing commit | availability |',
             '|---|---|---|---|---|---|---|']
    for s in m['surfaces']:
        lines.append('| %s | %s | %s | `%s` | %s | %s | %s |' % (
            s['surface'], s['box'], s.get('timestamp') or '—',
            (s.get('sha256') or '—')[:12] + ('…' if s.get('sha256') else ''),
            s.get('rows') if s.get('rows') is not None else '—',
            (s.get('producing_commit') or '—')[:12] + ('…' if s.get('producing_commit') else ''),
            s['availability']))
    lc = m['lineage_chain']
    lines += ['',
              '## Lineage (hash-based — row counts alone are never lineage)',
              '',
              '- mirror hydrated sha256 `%s`' % (lc['mirror_hydrated_sha256'] or '—'),
              '- ledger last `mirror_sha_after` `%s`' % (lc['ledger_last_mirror_sha_after'] or '—'),
              '- LFS pointer oid `%s` (pointer ≠ bytes; oid recorded beside the sha)' % (
                  lc['lfs_pointer_oid_sha256'] or '—'),
              '- all three agree: **%s**' % ('yes' if lc['all_three_agree'] else 'NO'),
              '- origin: %s' % json.dumps(lc['origin'], ensure_ascii=False),
              '',
              '## Cross-box equality',
              '',
              m['cross_box_equality'],
              '']
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--fixtures-only', action='store_true')
    args = ap.parse_args()
    os.makedirs(REPORTS, exist_ok=True)
    run_fixtures(REPORTS)
    if args.fixtures_only:
        return 0
    m = build_matrix()
    _write_json(os.path.join(REPORTS, 'H4055_store_mirror_box_matrix.json'), m)
    with io.open(os.path.join(REPORTS, 'H4055_store_mirror_box_matrix.md'), 'w',
                 encoding='utf-8', newline='\n') as f:
        f.write(matrix_md(m))
    print('wrote %s' % os.path.join(REPORTS, 'H4055_store_mirror_box_matrix.md'))
    print('lineage chain all-three-agree: %s' % m['lineage_chain']['all_three_agree'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
