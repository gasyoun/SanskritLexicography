#!/usr/bin/env python
"""Build an optimized (gen_opt_harness2) rerun harness from the latest audit_window requeue.

  python src/pilot/requeue_from_audit.py sTA               # all requeue keys (requeue.keys.txt)
  python src/pilot/requeue_from_audit.py sTA --transient   # only null cards (cheap re-run)
  python src/pilot/requeue_from_audit.py sTA --defect      # only real content failures (rework)
  python src/pilot/requeue_from_audit.py sTA --lang=en     # EN requeue / EN TM denylist

A defect/all requeue always regenerates with --no-tm: a gate-flagged key's TM entry
addresses on the input SHA, not on whether the cached translation passed the gates, so a
plain --tm=auto rerun would silently re-serve the exact already-flagged content (see
Uprava/FINDINGS.md, the gam requeue trap). --transient (null cards, nothing was ever
cached) keeps --tm=auto since there is no flagged content to re-serve.
"""
import json
import os
import subprocess
import sys
import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'output')
INP = os.path.join(HERE, 'input')
REQUEUE = os.path.join(OUT, 'requeue.keys.txt')

sys.path.insert(0, SRC)
from safe_filename import safe_name
from window_common import sha256_file

sys.path.insert(0, HERE)
import translation_memory


def rootmap_path(root):
    for stem in (safe_name(root), root):
        p = os.path.join(INP, stem + '.rootmap.json')
        if os.path.exists(p):
            return p
    return None


def requeue_file(which):
    return os.path.join(OUT, {
        'transient': 'requeue.transient.keys.txt',   # null cards only — cheap re-run
        'defect': 'requeue.defect.keys.txt',         # real content failures — rework
    }.get(which, 'requeue.keys.txt'))


def read_requeue(path):
    if not os.path.exists(path):
        sys.exit('no %s — run audit_window.py --write-requeue first' % path)
    keys = [ln.strip() for ln in open(path, encoding='utf-8') if ln.strip()]
    if not keys:
        sys.exit('empty requeue file: %s' % path)
    return keys


def append_tm_denylist(root, keys, which, lang='ru'):
    """Invalidate exact card-TM addresses for defect/all requeues. Append-only and local-only."""
    if which == 'transient':
        return 0
    path = translation_memory.denylist_path()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')
    n = 0
    with open(path, 'a', encoding='utf-8') as f:
        for k in keys:
            raw = os.path.join(INP, k + '.raw.txt')
            if not os.path.exists(raw):
                continue
            address = '%s:%s' % (lang, sha256_file(raw))
            f.write(json.dumps({'schema': 'pwg.translation_memory.denylist.v1',
                                'kind': 'card', 'address': address, 'key': k,
                                'root': root, 'lang': lang, 'reason': 'requeue_%s' % which,
                                'blocked_at': now}, ensure_ascii=False) + '\n')
            n += 1
    return n


def main():
    argv = sys.argv[1:]
    which = ('transient' if '--transient' in argv else
             'defect' if '--defect' in argv else 'all')
    lang = 'ru'
    for a in argv:
        if a.startswith('--lang='):
            lang = a.split('=', 1)[1]
    if lang not in ('ru', 'en'):
        sys.exit('unknown --lang %r (ru|en)' % lang)
    positional = [a for a in argv if not a.startswith('--')]
    root = positional[0] if positional else ''
    if not root:
        sys.exit('usage: python src/pilot/requeue_from_audit.py <root> [--transient|--defect] [--lang=ru|en]')
    rp = rootmap_path(root)
    if not rp:
        sys.exit('no rootmap for %r under %s' % (root, INP))
    rm = json.load(open(rp, encoding='utf-8'))
    declared = {s['subkey'] for s in rm.get('sub_cards', [])}
    suffixes = {k.split('~~')[-1]: k for k in declared}
    keys = read_requeue(requeue_file(which))
    resolved, invalid = [], []
    for k in keys:
        full = k if k in declared else suffixes.get(k)
        if full and os.path.exists(os.path.join(INP, full + '.raw.txt')):
            resolved.append(full)
        else:
            invalid.append(k)
    if invalid:
        print('invalid/stale requeue keys:')
        for k in invalid:
            print('  ' + k)
        sys.exit(1)
    denied = append_tm_denylist(root, resolved, which, lang=lang)

    cmd = [sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'),
           root, '--keys=' + ','.join(resolved)]
    if lang != 'ru':
        cmd.append('--lang=%s' % lang)
    if which != 'transient':
        cmd.append('--no-tm')
    p = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(HERE)),
                       text=True, encoding='utf-8', capture_output=True)
    if p.stdout.strip():
        print(p.stdout.rstrip())
    if p.stderr.strip():
        print(p.stderr.rstrip(), file=sys.stderr)
    if p.returncode:
        sys.exit(p.returncode)

    harness = os.path.join(HERE, 'run_pilot_wf.opt2.js')
    print('requeue root      : %s' % root)
    print('requeue source    : %s' % which)
    print('requeue keys      : %d' % len(resolved))
    if denied:
        print('tm denylist       : +%d card address(es)' % denied)
    print('generated harness : %s' % harness)
    print('keys:')
    for k in resolved:
        print('  ' + k)


if __name__ == '__main__':
    main()
