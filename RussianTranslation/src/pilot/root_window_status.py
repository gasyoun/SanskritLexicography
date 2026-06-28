#!/usr/bin/env python
"""Preflight a root-split window before spending Claude/Max tokens.

  python src/pilot/root_window_status.py sTA
"""
import json
import hashlib
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
INP = os.path.join(HERE, 'input')
OUT = os.path.join(HERE, 'output')

sys.path.insert(0, SRC)
from safe_filename import safe_name
from window_common import harness_meta, latest_status, read_lines_result


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def rootmap_path(root):
    for stem in (safe_name(root), root):
        p = os.path.join(INP, stem + '.rootmap.json')
        if os.path.exists(p):
            return p, stem
    return None, safe_name(root)


def first_headtest_key(subs):
    heads = [s['subkey'] for s in subs
             if s.get('hom') == 0 and s.get('kind') == 'head'
             and (s.get('section') == 'pwg00' or str(s.get('section', '')).startswith('pwg00b'))]
    if not heads:
        heads = [s['subkey'] for s in subs if s.get('hom') == 0 and s.get('kind') == 'head']
    return heads[0] if heads else (subs[0]['subkey'] if subs else '')


def input_digest(subs):
    h = hashlib.sha256()
    missing = []
    for s in subs:
        key = s['subkey']
        for suffix in ('.raw.txt', '.portrait.json'):
            path = os.path.join(INP, key + suffix)
            h.update(key.encode('utf-8'))
            h.update(suffix.encode('ascii'))
            if os.path.exists(path):
                h.update(sha256_file(path).encode('ascii'))
            else:
                missing.append(key + suffix)
    return h.hexdigest(), missing


def latest_state(root):
    status = latest_status(OUT)
    if not status:
        return 'ready'
    if status.get('_error'):
        return 'ready (latest status unreadable)'
    if status.get('root') != root:
        return 'ready (latest status is for %s)' % (status.get('root') or '?')
    return status.get('state') or 'unknown'


def queue_lines(path):
    result = read_lines_result(path)
    return [line for line in result['lines'] if line.strip()], result.get('error')


def harness_matches(root, rootmap_sha):
    meta = harness_meta(os.path.join(HERE, 'run_pilot_wf.opt.js'))
    if not meta.get('ok'):
        return False, meta
    return (meta.get('root') == root
            and meta.get('rootmap_sha256') == rootmap_sha), meta


def next_action(root, failures, rootmap_sha=None):
    if failures:
        return {
            'action': 'Fix root-split input issues before generating a harness.',
            'command': 'python src\\pilot\\root_window_status.py %s' % root,
        }
    status = latest_status(OUT)
    harness = os.path.join(HERE, 'run_pilot_wf.opt.js')
    matches, meta = harness_matches(root, rootmap_sha)
    run_max = {
        'action': 'Run the generated optimized harness in Max Workflow and save fresh wf_output.json.',
        'command': 'python src\\pilot\\audit_window.py wf_output.json --root %s --write-requeue' % root,
        'note': 'Run this command after the Max Workflow finishes.',
        'harness': meta,
    }
    if not status or status.get('_error') or status.get('root') != root:
        if matches:
            return run_max
        return {
            'action': 'Generate the optimized harness for %s, then run Max Workflow.' % root,
            'command': 'python src\\pilot\\gen_opt_harness.py %s' % root,
            'note': meta.get('error') if isinstance(meta, dict) and status and status.get('_error') else '',
        }
    state = status.get('state') or 'unknown'
    requeue, requeue_error = queue_lines(os.path.join(OUT, 'requeue.keys.txt'))
    judge_sample, sample_error = queue_lines(os.path.join(OUT, 'judge_sample.keys.txt'))
    if requeue_error or sample_error:
        return {
            'action': 'Queue files could not be read; inspect file permissions before continuing.',
            'command': 'python src\\pilot\\root_window_status.py %s' % root,
            'note': '; '.join(e for e in (requeue_error, sample_error) if e),
        }
    if state == 'stale_artifact':
        if matches:
            return run_max
        return {
            'action': 'Regenerate optimized harness for %s and rerun Max Workflow.' % root,
            'command': 'python src\\pilot\\gen_opt_harness.py %s' % root,
            'note': meta.get('error') if isinstance(meta, dict) else '',
        }
    if requeue or state == 'needs_requeue':
        return {
            'action': 'Build a requeue-only harness for %s, rerun Max Workflow, then audit again.' % root,
            'command': 'python src\\pilot\\requeue_from_audit.py %s' % root,
        }
    if state == 'partial':
        return {
            'action': 'Run the optimized Max Workflow for pending sub-cards, then audit again.',
            'command': 'After Max: python src\\pilot\\audit_window.py wf_output.json --root %s --write-requeue' % root,
        }
    if judge_sample or int(status.get('judge_sample_count') or 0) > 0:
        return {
            'action': 'Send judge_sample.keys.txt to sampled semantic judging outside Python.',
            'command': 'Get-Content src\\pilot\\output\\judge_sample.keys.txt',
        }
    if not os.path.exists(harness):
        return {
            'action': 'Generate the optimized harness for %s, then run Max Workflow.' % root,
            'command': 'python src\\pilot\\gen_opt_harness.py %s' % root,
        }
    return {
        'action': 'Window is mechanically clean; advance to the next frequency root.',
        'command': 'python src\\pilot\\root_window_status.py <next-root>',
    }


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else ''
    if not root:
        sys.exit('usage: python src/pilot/root_window_status.py <root>')
    rp, stem = rootmap_path(root)
    if not rp:
        sys.exit('FAIL: no rootmap for %r under %s' % (root, INP))
    rm = json.load(open(rp, encoding='utf-8'))
    subs = rm.get('sub_cards') or []
    rootmap_sha = sha256_file(rp)
    digest, digest_missing = input_digest(subs)
    declared = {s['subkey'] for s in subs}
    prefix = stem + '~~'
    raw_files = {fn[:-len('.raw.txt')] for fn in os.listdir(INP)
                 if fn.startswith(prefix) and fn.endswith('.raw.txt')}
    portrait_files = {fn[:-len('.portrait.json')] for fn in os.listdir(INP)
                      if fn.startswith(prefix) and fn.endswith('.portrait.json')}

    missing_raw = sorted(declared - raw_files)
    missing_portrait = sorted(declared - portrait_files)
    stale_raw = sorted(raw_files - declared)
    stale_portrait = sorted(portrait_files - declared)

    budget = int(os.environ.get('HEAD_CIT_BATCH_BUDGET')
                 or os.environ.get('HEAD_CIT_BUDGET') or 18)
    max_ls, over_budget = 0, []
    for s in subs:
        rawp = os.path.join(INP, s['subkey'] + '.raw.txt')
        if not os.path.exists(rawp):
            continue
        nls = open(rawp, encoding='utf-8').read().count('<ls')
        max_ls = max(max_ls, nls)
        if s.get('batch_of') and nls > budget:
            over_budget.append((s['subkey'], nls))

    batch_errors = []
    groups = defaultdict(list)
    for s in subs:
        if s.get('batch_of'):
            groups[(s.get('hom'), s.get('batch_of'))].append(s)
    for (hom, batch_of), group in sorted(groups.items()):
        counts = {g.get('batch_count') for g in group}
        if len(counts) != 1:
            batch_errors.append('hom %s sense %s has inconsistent batch_count %s'
                                % (hom, batch_of, sorted(counts)))
            continue
        count = counts.pop()
        indexes = sorted(g.get('batch_index') for g in group)
        if indexes != list(range(count)):
            batch_errors.append('hom %s sense %s indexes %s != 0..%d'
                                % (hom, batch_of, indexes, count - 1))

    failures = []
    for name, vals in [('missing raw', missing_raw), ('missing portrait', missing_portrait),
                       ('stale raw', stale_raw), ('stale portrait', stale_portrait)]:
        if vals:
            failures.append('%s: %d' % (name, len(vals)))
    if over_budget:
        failures.append('over-budget citation batches: %d' % len(over_budget))
    if batch_errors:
        failures.append('batch metadata errors: %d' % len(batch_errors))

    print('root              : %s (%s)' % (root, stem))
    print('current state     : %s' % latest_state(root))
    print('rootmap           : %s' % rp)
    print('rootmap sha256    : %s' % rootmap_sha)
    print('input digest      : %s' % digest)
    print('sub-cards         : %d' % len(subs))
    print('raw files         : %d declared / %d present / %d stale' %
          (len(declared), len(raw_files), len(stale_raw)))
    print('portrait files    : %d declared / %d present / %d stale' %
          (len(declared), len(portrait_files), len(stale_portrait)))
    print('citation budget   : %d' % budget)
    print('max <ls> in part  : %d' % max_ls)
    print('batch groups      : %d' % len(groups))
    print('headtest key      : %s' % first_headtest_key(subs))
    if over_budget:
        print('over-budget batches:')
        for k, n in over_budget:
            print('  %s: %d <ls>' % (k, n))
    if digest_missing:
        print('input digest missing files:')
        for item in digest_missing[:20]:
            print('  ' + item)
    if batch_errors:
        print('batch metadata errors:')
        for e in batch_errors:
            print('  ' + e)
    if failures:
        print('FAIL:', '; '.join(failures))
        nxt = next_action(root, failures, rootmap_sha=rootmap_sha)
        print('next action       : %s' % nxt['action'])
        print('next command      : %s' % nxt['command'])
        if nxt.get('note'):
            print('next note         : %s' % nxt['note'])
        sys.exit(1)
    nxt = next_action(root, failures, rootmap_sha=rootmap_sha)
    print('next action       : %s' % nxt['action'])
    print('next command      : %s' % nxt['command'])
    if nxt.get('note'):
        print('next note         : %s' % nxt['note'])
    if nxt.get('harness'):
        print('harness generated : %s' % (nxt['harness'].get('generated_at') or nxt['harness'].get('mtime') or 'unknown'))
        print('harness keys      : %s' % (nxt['harness'].get('selected_key_count') or 0))
    print('PASS: root window is structurally ready')


if __name__ == '__main__':
    main()
