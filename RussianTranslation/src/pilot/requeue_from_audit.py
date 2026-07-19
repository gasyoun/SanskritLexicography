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
from window_common import sha256_file, append_jsonl_line

sys.path.insert(0, HERE)
import translation_memory


def rootmap_path(root):
    for stem in (safe_name(root), root):
        p = os.path.join(INP, stem + '.rootmap.json')
        if os.path.exists(p):
            return p
    return None


def tag_out_dir(tag):
    """H336/H-2: the same per-window namespacing audit_window.py --window-tag writes to.
    None (untagged / legacy) resolves to the flat OUT singleton dir — unchanged default
    behavior so an untagged invocation keeps reading the old singletons."""
    return os.path.join(OUT, safe_name(tag)) if tag else OUT


def requeue_file(which, tag=None):
    return os.path.join(tag_out_dir(tag), {
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


def refuse_crashed_audit(requeue_file, tag):
    """B11 (H1339): a crashed/unparseable child auditor deliberately requeues EVERY window
    key (the H169 fail-loud artifact). Consuming that list mechanically would TM-denylist
    and re-run the whole window off ONE gate crash — blast radius, not rework. Refuse to
    build a rerun harness or denylist rows from a crashed audit; the audit must be re-run
    first. When no report sits beside the key files (explicit --requeue-file workflows),
    legacy behavior is kept — there is nothing bound to check against."""
    d = (os.path.dirname(os.path.abspath(requeue_file)) if requeue_file
         else tag_out_dir(tag))
    report_path = os.path.join(d, 'audit_window.report.json')
    try:
        report = json.load(open(report_path, encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return
    crashed = report.get('crashed') or []
    if crashed:
        sys.exit('REFUSED: the audit that wrote this requeue list CRASHED (%s) — its '
                 'requeue set is the fail-loud blast-radius artifact (every window key), '
                 'not a work list. Re-run audit_window.py, then requeue from the fresh '
                 'report.' % ', '.join(str(c) for c in crashed[:5]))


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
    for k in keys:
        raw = os.path.join(INP, k + '.raw.txt')
        if not os.path.exists(raw):
            continue
        address = '%s:%s' % (lang, sha256_file(raw))
        # H336/H-3: one os.write() per row (window_common.append_jsonl_line) — a bare
        # buffered 'a' handle can split one line across writes, and a concurrent
        # appender (another account's requeue) can then tear it.
        append_jsonl_line(path, {'schema': 'pwg.translation_memory.denylist.v1',
                                 'kind': 'card', 'address': address, 'key': k,
                                 'root': root, 'lang': lang, 'reason': 'requeue_%s' % which,
                                 'blocked_at': now})
        n += 1
    nf = 0
    fp = fsha_file or os.path.join(OUT, 'requeue.defect.fshas.txt')
    if os.path.exists(fp):
        fshas = [ln.strip() for ln in open(fp, encoding='utf-8') if ln.strip()]
        for fsha in fshas:
            append_jsonl_line(path, {'schema': 'pwg.translation_memory.denylist.v1',
                                     'kind': 'frag', 'fsha': fsha,
                                     'root': root, 'lang': lang,
                                     'reason': 'requeue_%s_fragment' % which,
                                     'blocked_at': now})
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
                    help='explicit requeue key file; default uses src/pilot/output singleton files, '
                         'or src/pilot/output/<window-tag>/ if --window-tag is given')
    ap.add_argument('--window-tag',
                    help='H336/H-2: read requeue/fsha files from src/pilot/output/<tag>/ — the same '
                         'tag audit_window.py --window-tag wrote them to. Closes the same-clone '
                         'requeue TOCTOU: an untagged run reads whichever window last rewrote the '
                         'singleton, possibly not this one.')
    ap.add_argument('--out',
                    help='explicit generated harness path; default is src/pilot/run_pilot_wf.opt2.js')
    ap.add_argument('--manifest-out',
                    help='optional execution-manifest path bound to this exact requeue key set')
    ap.add_argument('--nominal', action='store_true',
                    help='resolve keys directly as nominal cards instead of requiring a rootmap')
    ap.add_argument('--no-grammar', action='store_true',
                    help='pass --no-grammar through for nominal requeues')
    ap.add_argument('--profile-slot')
    ap.add_argument('--config-dir')
    ap.add_argument('--executor-lane', default='serial-whole-card')
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
    refuse_crashed_audit(args.requeue_file, args.window_tag)     # B11: never consume a crash
    keys = read_requeue(args.requeue_file or requeue_file(which, tag=args.window_tag))
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
    fsha_dir = (os.path.dirname(os.path.abspath(args.requeue_file)) if args.requeue_file
                else tag_out_dir(args.window_tag))
    cand = os.path.join(fsha_dir, 'requeue.defect.fshas.txt')
    fsha_file = cand if os.path.exists(cand) else None
    denied, denied_frags = append_tm_denylist(root, resolved, which, lang=lang,
                                              fsha_file=fsha_file)

    cmd = [sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'),
           root, '--keys=' + ','.join(resolved)]
    if args.out:
        cmd.append('--out=%s' % args.out)
    if args.manifest_out:
        cmd.append('--manifest-out=%s' % args.manifest_out)
    if bool(args.profile_slot) != bool(args.config_dir):
        sys.exit('--profile-slot and --config-dir must be supplied together')
    if args.profile_slot:
        cmd += ['--profile-slot=%s' % args.profile_slot,
                '--config-dir=%s' % args.config_dir,
                '--execution-route=claude-cli-headless',
                '--executor-lane=%s' % args.executor_lane,
                '--validation-method=audit_window+final_schema']
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
    if args.manifest_out:
        print('execution manifest: %s' % os.path.abspath(args.manifest_out))
    print('keys:')
    for k in resolved:
        print('  ' + k)


if __name__ == '__main__':
    main()
