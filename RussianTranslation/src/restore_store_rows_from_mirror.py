#!/usr/bin/env python
r"""restore_store_rows_from_mirror.py — H3591: put the mirror's `ru` back on src rows that drifted.

MG ruling 27-08-2026 (GAPS §16): `Instr.` stays canonical. Every src-store row whose `ru`
differs from the same row in `pwg-ru-data/tm/` gets the mirror's `ru`; rows only in src
(the H3361 window) are kept; then the mirror is refreshed from src. Backup + ledger always.

H4040 (04-09-2026): the posture flips from write-by-default (``--dry-run`` opt-in) to
the house dry-run-default convention — the store is only touched with an explicit
``--write``. The in-place ``io.open(src, 'w')`` truncate-then-write rewrite is replaced
by ``store_write.locked_store_rewrite`` (the H2146 lock: PromoteClaim across the
read-guard-write window, unique fsynced backup, atomic LF-only replace), which also
supplies the backup the ledger records.

  python src/restore_store_rows_from_mirror.py [--src PATH] [--mirror PATH] [--write]
"""
import argparse
import hashlib
import io
import json
import os
import shutil
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root  # noqa: E402
from store_write import locked_store_rewrite  # noqa: E402
GITHUB = sibling_root(HERE)
DATA = os.path.normpath(os.path.join(GITHUB, 'pwg-ru-data'))
DEFAULT_SRC = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DEFAULT_MIRROR = os.path.join(DATA, 'tm', 'pwg_ru_translated.jsonl')
LEDGER = os.path.join(DATA, 'tm', 'h3591_restore_ledger.jsonl')


def rid(r):
    return (r.get('key1') or '', r.get('subcard') or '', r.get('sense_tag') or '', (r.get('de') or '')[:80])


def load(path):
    with io.open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--mirror', default=DEFAULT_MIRROR)
    ap.add_argument('--write', action='store_true',
                    help='mutate the store (default: dry run)')
    a = ap.parse_args()
    src, mir = load(a.src), load(a.mirror)
    mir_by = {}
    for r in mir:
        mir_by.setdefault(rid(r), r)
    restored, only_src, entries = 0, 0, []
    for r in src:
        m = mir_by.get(rid(r))
        if m is None:
            only_src += 1
            continue
        if (r.get('ru') or '') != (m.get('ru') or ''):
            entries.append({'key1': r.get('key1'), 'subcard': r.get('subcard'), 'sense_tag': r.get('sense_tag'),
                            'ru_before_sha': hashlib.sha256((r.get('ru') or '').encode('utf-8')).hexdigest()[:12],
                            'ru_after_sha': hashlib.sha256((m.get('ru') or '').encode('utf-8')).hexdigest()[:12]})
            r['ru'] = m.get('ru')
            restored += 1
    print('src rows=%d mirror rows=%d restored=%d only_src(kept)=%d' % (len(src), len(mir), restored, only_src))
    if not a.write:
        print('dry run: no changes written (pass --write to mutate)')
        return
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    # H4040: locked rewrite (PromoteClaim + unique fsynced backup + atomic
    # replace) replaces the in-place truncate-then-write; its unique backup is
    # the one the ledger records.
    bak = locked_store_rewrite(a.src, src, tag='h3591')
    shutil.copy2(a.src, a.mirror)
    with io.open(LEDGER, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps({'handoff': 'H3591', 'ts': stamp, 'ruling': 'MG 27-08-2026 keep Instr. (GAPS §16)',
                            'restored_rows': restored, 'kept_only_src_rows': only_src, 'src_rows': len(src),
                            'backup': os.path.basename(bak) if bak else None, 'src_sha256': sha(a.src),
                            'mirror_sha256': sha(a.mirror),
                            'rows': entries}, ensure_ascii=False) + '\n')
    print('backup=%s  src_sha=%s  mirror refreshed (identical=%s)' % (os.path.basename(bak) if bak else '(fresh store)',
                                                                      sha(a.src)[:12], sha(a.src) == sha(a.mirror)))


if __name__ == '__main__':
    main()
