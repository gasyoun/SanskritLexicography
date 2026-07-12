#!/usr/bin/env python
"""Plan and prepare no-PWG supplement-chain drain windows.

This is the deterministic wrapper for the H255 no-PWG scale run. It does not run
Workflow generation locally. Instead it:

* reads the 232-lemma backfill queue;
* skips headwords already present in the translated store;
* drains the no_pwg_w1 still-null sub-card tail first;
* generates the exact input sidecars through _pilot_gen_merged.py;
* emits a per-window harness with --output-budget=1 and a unique --out path;
* runs perf_preflight.py and writes a manifest the Workflow-capable session can
  follow without hand-picking stale lists.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(RT, 'src')
OUT = os.path.join(HERE, 'output')
QUEUE = os.path.join(HERE, 'lexical_cores', 'pwg_miss_backfill_queue.md')
STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
STILL_NULL = os.path.join(OUT, 'no_pwg_w1.still_null.txt')

if SRC not in sys.path:
    sys.path.insert(0, SRC)

from safe_filename import decode_safe_name, safe_name  # noqa: E402
from store_path import canonical_store  # noqa: E402

# One logical store shared across worktrees: dedup must read the SAME store a worktree drain
# promotes into, or the planner re-offers already-promoted headwords (H255 w06 loss / H805).
STORE = canonical_store(STORE)


def read_store_heads(path=STORE):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                key = json.loads(line).get('key1')
            except json.JSONDecodeError:
                continue
            if key:
                done.add(key)
    return done


def read_queue(path=QUEUE):
    rows, seen = [], set()
    row_re = re.compile(r'^\|\s*([^|`\s][^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = row_re.match(line)
            if not m:
                continue
            key = m.group(1).strip()
            if key in ('key1', '---') or key.startswith('-'):
                continue
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                'key1': key,
                'iast': m.group(2).strip(),
                'layers': [x for x in m.group(3).strip().split('/') if x],
            })
    if not rows:
        raise SystemExit('FAIL: no queue rows parsed from %s' % path)
    return rows


def subcard_head(subcard):
    stem = subcard.split('~~', 1)[0]
    try:
        return decode_safe_name(stem)
    except Exception:
        return stem


def read_still_null(path=STILL_NULL):
    if not os.path.exists(path):
        return []
    out, seen = [], set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            key = line.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(key)
    return out


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def existing_subcards(head):
    prefix = safe_name(head) + '~~h0_zz_'
    keys = []
    gen_dir = os.path.join(SRC, 'pilot', 'input')  # _pilot_gen_merged.py's OUT, not this module's
    if not os.path.isdir(gen_dir):
        return keys
    for name in sorted(os.listdir(gen_dir)):
        if name.startswith(prefix) and name.endswith('.raw.txt'):
            keys.append(name[:-len('.raw.txt')])
    return keys


def run_cmd(cmd, capture=False):
    kwargs = {
        'cwd': RT,
        'encoding': 'utf-8',
        'errors': 'replace',
    }
    if capture:
        kwargs.update({'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT})
    p = subprocess.run(cmd, **kwargs)
    if p.returncode:
        if capture and p.stdout:
            sys.stderr.write(p.stdout)
        raise SystemExit('FAIL: command exited %d: %s' % (p.returncode, ' '.join(cmd)))
    return p.stdout if capture else ''


def build_order(queue_rows, promoted, still_null):
    queued = [r['key1'] for r in queue_rows if r['key1'] not in promoted]
    queued_set = set(queued)
    tail_heads = []
    for key in still_null:
        head = subcard_head(key)
        if head in queued_set and head not in tail_heads:
            tail_heads.append(head)
    rest = [k for k in queued if k not in set(tail_heads)]
    return tail_heads + rest, tail_heads


def preflight_json(root, keys):
    cmd = [
        sys.executable, 'src/pilot/perf_preflight.py', root,
        '--nominal',
        '--keys=' + ','.join(keys),
        '--output-budget=1',
        '--json',
        '--cost-ceiling-window=25',
        '--cost-ceiling-per-card=2',
    ]
    return json.loads(run_cmd(cmd, capture=True))


def prepare_window(args, index, heads, still_null_keys, tail_mode):
    root = '%s%02d' % (args.prefix, index)
    print('preparing %s: %d headword(s)%s' %
          (root, len(heads), ' [still-null tail]' if tail_mode else ''))
    run_cmd([sys.executable, 'src/_pilot_gen_merged.py'] + heads)

    if tail_mode:
        head_set = set(heads)
        subcards = [k for k in still_null_keys if subcard_head(k) in head_set]
    else:
        subcards = []
        for head in heads:
            subcards.extend(existing_subcards(head))

    subcards = [k for i, k in enumerate(subcards) if k and k not in set(subcards[:i])]
    if not subcards:
        raise SystemExit('FAIL: %s produced no no-PWG subcards' % root)

    harness = os.path.join(HERE, 'run_pilot_wf.%s.js' % root)
    gen_cmd = [
        sys.executable, 'src/pilot/gen_opt_harness2.py', root,
        '--nominal',
        '--keys=' + ','.join(subcards),
        '--output-budget=1',
        '--out=' + harness,
        '--refuse-oversize',
    ]
    run_cmd(gen_cmd)
    preflight = preflight_json(root, subcards)
    wf_out = os.path.join(OUT, 'wf_output.%s.json' % root)
    return {
        'root': root,
        'mode': 'still_null_tail' if tail_mode else 'queue',
        'headwords': heads,
        'subcards': subcards,
        'harness': os.path.relpath(harness, RT).replace('\\', '/'),
        'workflow_output': os.path.relpath(wf_out, RT).replace('\\', '/'),
        'audit_command': 'python src/pilot/audit_window.py %s' % root,
        'promote_command': 'python src/promote_final_cards.py --merge',
        'preflight': {
            'selected_keys': len(preflight.get('selected_keys') or []),
            'batches': preflight.get('batch_count'),
            'agent_expected_after_tm': preflight.get('agent_expected_after_tm'),
            'cost_gate': preflight.get('cost_gate'),
            'warnings': preflight.get('warnings') or [],
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description='Plan/prepare H255 no-PWG scale windows.')
    ap.add_argument('--window-size', type=int, default=20,
                    help='headwords per prepared queue window (default %(default)s; keep <=30)')
    ap.add_argument('--prefix', default='no_pwg_w',
                    help='window root prefix (default %(default)s)')
    ap.add_argument('--start-index', type=int, default=2,
                    help='first numeric suffix; w1 was the pilot (default %(default)s)')
    ap.add_argument('--limit-windows', type=int, default=1,
                    help='prepare only this many windows now; 0 means plan all without preparing')
    ap.add_argument('--plan-only', action='store_true',
                    help='write the manifest without generating sidecars/harnesses')
    ap.add_argument('--manifest', default=os.path.join(OUT, 'no_pwg_scale_plan.json'),
                    help='manifest output path')
    args = ap.parse_args(argv)

    if args.window_size < 1 or args.window_size > 30:
        raise SystemExit('FAIL: --window-size must be between 1 and 30 for H255')

    queue = read_queue()
    promoted = read_store_heads()
    still_null = read_still_null()
    ordered, tail_heads = build_order(queue, promoted, still_null)
    windows = []
    tail_set = set(tail_heads)
    tail_order = [h for h in ordered if h in tail_set]
    rest_order = [h for h in ordered if h not in tail_set]
    window_heads = list(chunked(tail_order, args.window_size)) + list(chunked(rest_order, args.window_size))

    to_prepare = 0 if args.plan_only else args.limit_windows
    for offset, heads in enumerate(window_heads):
        idx = args.start_index + offset
        tail_mode = all(h in tail_set for h in heads)
        if to_prepare and offset < to_prepare:
            windows.append(prepare_window(args, idx, heads, still_null, tail_mode))
        else:
            windows.append({
                'root': '%s%02d' % (args.prefix, idx),
                'mode': 'still_null_tail' if tail_mode else 'queue',
                'headwords': heads,
                'subcards': None,
                'harness': None,
                'workflow_output': None,
                'preflight': None,
            })

    payload = {
        'schema': 'pwg.no_pwg_scale_plan.v1',
        'queue_rows': len(queue),
        'store_path': os.path.relpath(STORE, RT).replace('\\', '/'),
        'store_present': os.path.exists(STORE),
        'promoted_headwords_seen': len(promoted),
        'still_null_subcards_seen': len(still_null),
        'remaining_headwords': len(ordered),
        'tail_headwords_first': tail_heads,
        'window_size': args.window_size,
        'prepared_windows': len([w for w in windows if w.get('harness')]),
        'windows': windows,
    }
    os.makedirs(os.path.dirname(args.manifest), exist_ok=True)
    with open(args.manifest, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('wrote %s' % args.manifest)
    if not os.path.exists(STORE):
        print('WARNING: promoted store not found at %s; dedup will become exact when the '
              'gitignored local store is restored/present' % os.path.relpath(STORE, RT))
    print('remaining headwords: %d | windows: %d | prepared: %d'
          % (payload['remaining_headwords'], len(windows), payload['prepared_windows']))
    if windows:
        first = windows[0]
        print('next window: %s (%s) %d headword(s)' %
              (first['root'], first['mode'], len(first['headwords'])))


if __name__ == '__main__':
    main()
