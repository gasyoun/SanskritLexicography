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
import hashlib
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
RESIDUALS = os.path.join(HERE, 'no_pwg_residuals.jsonl')

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from safe_filename import decode_safe_name, safe_name  # noqa: E402
from store_path import canonical_store  # noqa: E402
import coordinator  # noqa: E402
from window_common import atomic_write_json  # noqa: E402

# One logical store shared across worktrees: dedup must read the SAME store a worktree drain
# promotes into, or the planner re-offers already-promoted headwords (H255 w06 loss / H805).
STORE = canonical_store(STORE)


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_store_keys(path=STORE):
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, encoding='utf-8') as f:
        for line in f:
            try:
                key = json.loads(line).get('key1') if line.strip() else None
            except json.JSONDecodeError:
                key = None
            if key:
                keys.add(key)
    return keys


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


def read_residuals(path=RESIDUALS):
    """Return the latest durable residual decision for each exact subcard key."""
    latest = {}
    if not path or not os.path.exists(path):
        return latest
    with open(path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit('FAIL: malformed residual registry %s:%d: %s' %
                                 (path, lineno, e))
            if row.get('schema') != 'pwg.no_pwg_residual.v1':
                raise SystemExit('FAIL: unsupported residual registry schema at %s:%d' %
                                 (path, lineno))
            if not row.get('key') or row.get('status') not in ('blocked', 'retry', 'resolved'):
                raise SystemExit('FAIL: invalid residual row at %s:%d' % (path, lineno))
            latest[row['key']] = row
    return latest


def residual_summary(rows):
    return [{'key': row['key'], 'reason': row.get('reason'),
             'source_window': row.get('source_window')}
            for row in rows]


def filter_residual_subcards(subcards, blocked):
    skipped = [blocked[key] for key in subcards if key in blocked]
    return [key for key in subcards if key not in blocked], skipped


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


def promotion_command(workflow_output, gen_model_version):
    """Return the single-window, merge-safe promotion command for a plan row."""
    if not gen_model_version or gen_model_version in ('sonnet', 'claude-sonnet'):
        raise ValueError('an exact generation model id is required')
    return (
        'python src/promote_final_cards.py --merge --glob "%s" '
        '--gen-model-version %s' % (workflow_output, gen_model_version)
    )


def audit_command(workflow_output, root, execution_manifest=None):
    command = (
        'python src/pilot/audit_window.py "%s" --root "%s" '
        '--write-requeue --window-tag "%s"' % (workflow_output, root, root)
    )
    if execution_manifest:
        command += ' --execution-manifest "%s"' % execution_manifest
    return command


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
    promoted_keys = read_store_keys()
    subcards = [k for k in subcards if k not in promoted_keys]
    blocked = getattr(args, 'blocked_residuals', {})
    subcards, skipped_rows = filter_residual_subcards(subcards, blocked)
    if not subcards:
        if skipped_rows:
            print('omitting %s: every unpromoted subcard is a blocked residual' % root)
            return {
                'omitted': True, 'root': root, 'headwords': heads,
                'residual_skipped': residual_summary(skipped_rows),
            }
        raise SystemExit('FAIL: %s produced no no-PWG subcards' % root)

    if args.headless or args.dry_run:
        base = (os.path.join(os.path.abspath(args.coordinator_dir), 'artifacts', root)
                if args.headless else os.path.join(OUT, 'headless_dryrun', root))
        os.makedirs(base, exist_ok=True)
        harness = os.path.join(base, 'run_pilot_wf.%s.js' % root)
        execution_manifest = os.path.join(base, 'execution_manifest.%s.json' % root)
        preflight_path = os.path.join(base, 'preflight.json')
        if os.path.exists(execution_manifest) and not args.force_index:
            raise SystemExit('FAIL: headless window id already exists: %s' % root)
    else:
        harness = os.path.join(HERE, 'run_pilot_wf.%s.js' % root)
        execution_manifest = None
        preflight_path = None
    gen_cmd = [
        sys.executable, 'src/pilot/gen_opt_harness2.py', root,
        '--nominal',
        '--keys=' + ','.join(subcards),
        '--output-budget=1',
        '--out=' + harness,
        '--refuse-oversize',
    ]
    if execution_manifest:
        gen_cmd.append('--manifest-out=' + execution_manifest)
    run_cmd(gen_cmd)
    preflight = preflight_json(root, subcards)
    if preflight_path:
        atomic_write_json(preflight_path, preflight, indent=1)
    headless_meta = None
    if execution_manifest:
        with open(execution_manifest, encoding='utf-8') as f:
            execution = json.load(f)
        if execution.get('meta', {}).get('selected_keys') != subcards:
            raise SystemExit('FAIL: %s manifest key drift' % root)
        headless_meta = {
            'execution_manifest': os.path.relpath(execution_manifest, RT).replace('\\', '/'),
            'manifest_sha256': sha256_path(execution_manifest),
            'harness_sha256': sha256_path(harness),
            'presplit_keys': execution.get('presplit_keys') or [],
            'projected_calls': preflight.get('agent_expected_after_tm'),
        }
        if args.headless:
            coordinator.register_prepared_lease(
                root, 'no_pwg_windows100', subcards, harness, execution_manifest,
                preflight_path, artifact_path=os.path.dirname(execution_manifest))
    wf_out = os.path.join(OUT, 'wf_output.%s.json' % root)
    wf_out_rel = os.path.relpath(wf_out, RT).replace('\\', '/')
    manifest_rel = (os.path.relpath(execution_manifest, RT).replace('\\', '/')
                    if execution_manifest else None)
    return {
        'root': root,
        'mode': 'still_null_tail' if tail_mode else 'queue',
        'headwords': heads,
        'subcards': subcards,
        'harness': os.path.relpath(harness, RT).replace('\\', '/'),
        'workflow_output': wf_out_rel,
        'audit_command': audit_command(wf_out_rel, root, manifest_rel),
        'promote_command': promotion_command(wf_out_rel, args.gen_model_version),
        'residual_skipped': residual_summary(skipped_rows),
        'preflight': {
            'selected_keys': len(preflight.get('selected_keys') or []),
            'batches': preflight.get('batch_count'),
            'agent_expected_after_tm': preflight.get('agent_expected_after_tm'),
            'cost_gate': preflight.get('cost_gate'),
            'warnings': preflight.get('warnings') or [],
        },
        'headless': headless_meta,
    }


def used_window_indices(prefix, here=HERE, out=OUT):
    """Return the set of numeric window indices already used for `prefix`.

    Scans HERE for `run_pilot_wf.<prefix>NN.js` harnesses and OUT for
    `wf_output.<prefix>NN.json` outputs. A `_rq1`/`_rq2` requeue sibling counts as
    its BASE index (the regex stops at the first run of digits after the prefix), so
    `run_pilot_wf.no_pwg_w06_rq1.js` registers index 6 — a requeue is not a new window.
    H809 W3: `--start-index` was a pure label knob whose stale `.ai_state` value (4)
    silently collided with already-run w04/w05; deriving the used set from disk removes
    the guesswork.
    """
    pat = re.compile(re.escape(prefix) + r'0*([0-9]+)')
    used = set()
    for base, prefix, suffix in (
        (here, 'run_pilot_wf.', '.js'),
        (out, 'wf_output.', '.json'),
    ):
        try:
            names = os.listdir(base)
        except OSError:
            continue
        for name in names:
            if not (name.startswith(prefix) and name.endswith(suffix)):
                continue
            m = pat.search(name)
            if m:
                used.add(int(m.group(1)))
    return used


def next_free_index(prefix, minimum=2, here=HERE, out=OUT):
    """Lowest unused index >= minimum for `prefix` (max(used)+1, floored at minimum)."""
    used = used_window_indices(prefix, here, out)
    return max([minimum - 1] + sorted(used)) + 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='Plan/prepare H255 no-PWG scale windows.')
    ap.add_argument('--window-size', type=int, default=20,
                    help='headwords per prepared queue window (default %(default)s; keep <=30)')
    ap.add_argument('--prefix', default='no_pwg_w',
                    help='window root prefix (default %(default)s)')
    ap.add_argument('--start-index', type=int, default=None,
                    help='first numeric suffix. Default: auto = max(used-on-disk)+1 '
                         '(min 2; w1 was the pilot). An explicit value that collides with an '
                         'index already used on disk is refused unless --force-index.')
    ap.add_argument('--force-index', action='store_true',
                    help='allow an explicit --start-index that reuses an index already on disk '
                         '(the pre-H809 behaviour). Never needed for a normal forward drain.')
    ap.add_argument('--limit-windows', type=int, default=1,
                    help='prepare only this many windows now; 0 means plan all without preparing')
    ap.add_argument('--plan-only', action='store_true',
                    help='write the manifest without generating sidecars/harnesses')
    ap.add_argument('--manifest', default=os.path.join(OUT, 'no_pwg_scale_plan.json'),
                    help='manifest output path')
    ap.add_argument('--headwords', type=int, default=0,
                    help='limit the deterministic queue to N headwords (100 for H818)')
    ap.add_argument('--headless', action='store_true',
                    help='generate execution manifests and register prepared coordinator leases')
    ap.add_argument('--dry-run', action='store_true',
                    help='generate headless artifacts/report without registering leases or calling Claude')
    ap.add_argument('--coordinator-dir', default=coordinator.DEFAULT_COORD_DIR,
                    help='coordinator state/artifact directory for --headless')
    ap.add_argument('--gen-model-version', default='claude-sonnet-5',
                    help='exact generation model id written into the promotion command '
                         '(default %(default)s)')
    ap.add_argument('--residual-file', default=RESIDUALS,
                    help='durable pwg.no_pwg_residual.v1 JSONL registry')
    ap.add_argument('--include-residuals', action='store_true',
                    help='explicitly retry keys whose latest residual status is blocked')
    args = ap.parse_args(argv)

    if args.headless:
        os.environ['PWG_COORDINATOR_DIR'] = os.path.abspath(args.coordinator_dir)

    if args.window_size < 1 or args.window_size > 30:
        raise SystemExit('FAIL: --window-size must be between 1 and 30 for H255')
    if args.gen_model_version in ('sonnet', 'claude-sonnet'):
        raise SystemExit('FAIL: --gen-model-version must be an exact model id')

    # H809 W3: resolve the window index from disk unless the caller pins one.
    # `--plan-only` prepares nothing, so a stale/colliding label is harmless there and
    # never blocks a dry-run plan.
    preparing = (not args.plan_only) and args.limit_windows > 0
    if args.start_index is None:
        args.start_index = next_free_index(args.prefix)
    elif preparing and not args.force_index:
        used = used_window_indices(args.prefix)
        if args.start_index in used:
            free = next_free_index(args.prefix)
            raise SystemExit(
                'FAIL: --start-index %d collides with an index already used on disk for '
                'prefix %r (used: %s). Next free index is %d. Omit --start-index to '
                'auto-select, or pass --force-index to reuse deliberately.'
                % (args.start_index, args.prefix, sorted(used), free))

    queue = read_queue()
    promoted = read_store_heads()
    still_null = read_still_null()
    residuals = read_residuals(args.residual_file)
    args.blocked_residuals = ({
        key: row for key, row in residuals.items() if row.get('status') == 'blocked'
    } if not args.include_residuals else {})
    initially_skipped = [args.blocked_residuals[key] for key in still_null
                         if key in args.blocked_residuals]
    eligible_still_null = [key for key in still_null if key not in args.blocked_residuals]
    ordered, tail_heads = build_order(queue, promoted, eligible_still_null)
    if args.headwords:
        ordered = ordered[:args.headwords]
        tail_heads = [head for head in tail_heads if head in set(ordered)]
    windows = []
    omitted = []
    tail_set = set(tail_heads)
    tail_order = [h for h in ordered if h in tail_set]
    rest_order = [h for h in ordered if h not in tail_set]
    window_heads = list(chunked(tail_order, args.window_size)) + list(chunked(rest_order, args.window_size))

    to_prepare = 0 if args.plan_only else args.limit_windows
    seen_subcards = set()
    for offset, heads in enumerate(window_heads):
        idx = args.start_index + offset
        tail_mode = all(h in tail_set for h in heads)
        if to_prepare and offset < to_prepare:
            window = prepare_window(args, idx, heads, eligible_still_null, tail_mode)
            if window.get('omitted'):
                omitted.append(window)
                continue
            overlap = seen_subcards & set(window['subcards'])
            if overlap:
                raise SystemExit('FAIL: duplicate subcards across windows: %s' % ','.join(sorted(overlap)))
            seen_subcards.update(window['subcards'])
            windows.append(window)
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
        'residual_registry': os.path.relpath(args.residual_file, RT).replace('\\', '/'),
        'include_residuals': args.include_residuals,
        'residual_skipped': residual_summary({
            row['key']: row for row in initially_skipped + [
                residuals[item['key']] for window in windows + omitted
                for item in (window.get('residual_skipped') or [])
            ]
        }.values()),
        'omitted_windows': omitted,
        'remaining_headwords': len(ordered),
        'tail_headwords_first': tail_heads,
        'window_size': args.window_size,
        'prepared_windows': len([w for w in windows if w.get('harness')]),
        'selected_headwords': sum(len(w['headwords']) for w in windows),
        'selected_subcards': sum(len(w.get('subcards') or []) for w in windows),
        'presplit_subcards': sum(len((w.get('headless') or {}).get('presplit_keys') or []) for w in windows),
        'projected_calls': sum(((w.get('headless') or {}).get('projected_calls') or 0) for w in windows),
        'windows': windows,
    }
    os.makedirs(os.path.dirname(args.manifest), exist_ok=True)
    atomic_write_json(args.manifest, payload, indent=2)
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
