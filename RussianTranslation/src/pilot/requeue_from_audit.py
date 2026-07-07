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
import argparse

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


def append_tm_denylist(root, keys, which, lang='ru', fsha_file=None):
    """Invalidate exact card-TM addresses for defect/all requeues. Append-only and local-only.

    H304: also invalidate the flagged cards' FRAGMENT addresses. build_frags harvests
    frag_prov from raw wf_output before any gate runs, so without this a defect card's
    fragments stay reusable in the sidecar and --tm=auto re-serves the flagged content on
    the next window that shares a fragment. audit_window writes the fshas to
    requeue.defect.fshas.txt next to the requeue key files."""
    if which == 'transient':
        return 0, 0
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
    nf = 0
    fp = fsha_file or os.path.join(OUT, 'requeue.defect.fshas.txt')
    if os.path.exists(fp):
        fshas = [ln.strip() for ln in open(fp, encoding='utf-8') if ln.strip()]
        with open(path, 'a', encoding='utf-8') as f:
            for fsha in fshas:
                f.write(json.dumps({'schema': 'pwg.translation_memory.denylist.v1',
                                    'kind': 'frag', 'fsha': fsha,
                                    'root': root, 'lang': lang,
                                    'reason': 'requeue_%s_fragment' % which,
                                    'blocked_at': now}, ensure_ascii=False) + '\n')
                nf += 1
    return n, nf


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('root')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--transient', action='store_true')
    group.add_argument('--defect', action='store_true')
    ap.add_argument('--lang', default='ru', choices=('ru', 'en'))
    ap.add_argument('--requeue-file',
                    help='explicit requeue key file; default uses src/pilot/output singleton files')
    ap.add_argument('--out',
                    help='explicit generated harness path; default is src/pilot/run_pilot_wf.opt2.js')
    ap.add_argument('--nominal', action='store_true',
                    help='resolve keys directly as nominal cards instead of requiring a rootmap')
    ap.add_argument('--no-grammar', action='store_true',
                    help='pass --no-grammar through for nominal requeues')
    args = ap.parse_args()
    which = 'transient' if args.transient else 'defect' if args.defect else 'all'
    lang = args.lang
    if lang not in ('ru', 'en'):
        sys.exit('unknown --lang %r (ru|en)' % lang)
    root = args.root
    rp = rootmap_path(root)
    if not rp and not args.nominal:
        sys.exit('no rootmap for %r under %s' % (root, INP))
    declared, suffixes = set(), {}
    if rp:
        rm = json.load(open(rp, encoding='utf-8'))
        declared = {s['subkey'] for s in rm.get('sub_cards', [])}
        suffixes = {k.split('~~')[-1]: k for k in declared}
    keys = read_requeue(args.requeue_file or requeue_file(which))
    resolved, invalid = [], []
    for k in keys:
        full = k if (args.nominal or k in declared) else suffixes.get(k)
        if full and os.path.exists(os.path.join(INP, full + '.raw.txt')):
            resolved.append(full)
        else:
            invalid.append(k)
    if invalid:
        print('invalid/stale requeue keys:')
        for k in invalid:
            print('  ' + k)
        sys.exit(1)
    fsha_file = None
    if args.requeue_file:
        cand = os.path.join(os.path.dirname(os.path.abspath(args.requeue_file)),
                            'requeue.defect.fshas.txt')
        fsha_file = cand if os.path.exists(cand) else None
    denied, denied_frags = append_tm_denylist(root, resolved, which, lang=lang,
                                              fsha_file=fsha_file)

    cmd = [sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'),
           root, '--keys=' + ','.join(resolved)]
    if args.out:
        cmd.append('--out=%s' % args.out)
    if args.nominal:
        cmd.append('--nominal')
    if args.no_grammar:
        cmd.append('--no-grammar')
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

    harness = os.path.abspath(args.out) if args.out else os.path.join(HERE, 'run_pilot_wf.opt2.js')
    print('requeue root      : %s' % root)
    print('requeue source    : %s' % which)
    print('requeue keys      : %d' % len(resolved))
    if denied:
        print('tm denylist       : +%d card address(es)' % denied)
    if denied_frags:
        print('tm denylist       : +%d fragment fsha(s)' % denied_frags)
    print('generated harness : %s' % harness)
    print('keys:')
    for k in resolved:
        print('  ' + k)


if __name__ == '__main__':
    main()
