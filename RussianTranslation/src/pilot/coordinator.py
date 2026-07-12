#!/usr/bin/env python
"""Deterministic coordinator for the PWG->RU 30-day SLA lanes.

The coordinator owns leases and artifact paths only. It does not run the
Max/Workflow surface; operators still run the generated harness from the coding
session and feed the full result back through record-output.
"""
import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
OUT = os.path.join(HERE, 'output')
DEFAULT_COORD_DIR = os.path.join(OUT, 'coordinator')
ARTIFACT_DIRNAME = 'artifacts'
STATE_SCHEMA = 'pwg.sla_coordinator.state.v1'
DASHBOARD_SCHEMA = 'pwg.sla_coordinator.dashboard.v1'
REGISTRY_SCHEMA = 'pwg.sla_coordinator.artifact.v1'
DAILY_SCHEMA = 'pwg.sla_coordinator.daily.v1'
TRANSLATION_LIMIT = 3
LEASE_TTL_SECONDS = 6 * 60 * 60
LOCK_TTL_SECONDS = 10 * 60

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import promote_final_cards  # noqa: E402
from safe_filename import safe_name  # noqa: E402
import translation_memory  # noqa: E402
import verb_worklist  # noqa: E402
from window_common import append_jsonl_line, defer_monster  # noqa: E402


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def parse_ts(value):
    if not value:
        return None
    return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))


def coord_dir():
    return os.path.abspath(os.environ.get('PWG_COORDINATOR_DIR', DEFAULT_COORD_DIR))


def paths():
    base = coord_dir()
    return {
        'base': base,
        'state': os.path.join(base, 'state.json'),
        'lock': os.path.join(base, '.state.lock'),
        'promotion_lock': os.path.join(base, '.promotion.lock'),
        'registry': os.path.join(base, 'artifact_registry.jsonl'),
        'daily': os.path.join(base, 'daily_metrics.jsonl'),
        'dashboard': os.path.join(base, 'dashboard.json'),
        'artifacts': os.path.join(base, ARTIFACT_DIRNAME),
    }


def ensure_dirs():
    p = paths()
    os.makedirs(p['base'], exist_ok=True)
    os.makedirs(p['artifacts'], exist_ok=True)
    return p


def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


class DirLock:
    def __init__(self, path, ttl_seconds=LOCK_TTL_SECONDS):
        self.path = path
        self.ttl_seconds = ttl_seconds

    def __enter__(self):
        deadline = time.time() + 30
        while True:
            try:
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                os.mkdir(self.path)
                self.write_meta()
                return self
            except FileExistsError:
                if self.stale():
                    shutil.rmtree(self.path, ignore_errors=True)
                    continue
                if time.time() > deadline:
                    raise SystemExit('lock busy: %s' % self.path)
                time.sleep(0.2)

    def __exit__(self, exc_type, exc, tb):
        shutil.rmtree(self.path, ignore_errors=True)

    def write_meta(self):
        with open(os.path.join(self.path, 'owner.json'), 'w', encoding='utf-8') as f:
            json.dump({'pid': os.getpid(), 'created_at': utc_now()}, f, indent=1)

    def stale(self):
        meta_path = os.path.join(self.path, 'owner.json')
        try:
            meta = json.load(open(meta_path, encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return True
        created = parse_ts(meta.get('created_at'))
        if not created:
            return True
        age = (datetime.datetime.now(datetime.timezone.utc) - created).total_seconds()
        return age > self.ttl_seconds and not pid_alive(meta.get('pid'))


def default_state():
    return {
        'schema': STATE_SCHEMA,
        'created_at': utc_now(),
        'updated_at': utc_now(),
        'translation_limit': TRANSLATION_LIMIT,
        'leases': [],
        'cap': {'weekly_cap_fired': False, 'weekly_cap_cumulative_tokens': None},
    }


def load_state():
    p = ensure_dirs()
    if not os.path.exists(p['state']):
        return default_state()
    try:
        state = json.load(open(p['state'], encoding='utf-8'))
    except json.JSONDecodeError as e:
        raise SystemExit('invalid coordinator state: %s' % e)
    state.setdefault('schema', STATE_SCHEMA)
    state.setdefault('leases', [])
    state.setdefault('translation_limit', TRANSLATION_LIMIT)
    state.setdefault('cap', {})
    return state


def save_state(state):
    p = ensure_dirs()
    expire_stale_leases(state)
    state['updated_at'] = utc_now()
    tmp = p['state'] + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p['state'])
    write_dashboard(state)


def terminal_state(state):
    return state in ('released', 'promoted', 'abandoned', 'blocked', 'expired')


def lease_expired(lease, now=None):
    if terminal_state(lease.get('state')):
        return False
    if lease.get('state') != 'claimed':
        return False
    expires = parse_ts(lease.get('expires_at'))
    if not expires:
        return False
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return expires <= now


def expire_stale_leases(state):
    """Turn TTL-expired non-terminal leases into terminal expired leases.

    The coordinator's global <=3 translation cap is only useful if dead
    pre-prepare claims eventually release their slots. Prepared leases are
    durable operator artifacts: they may wait for a human Workflow run and should
    not be invalidated merely because the handoff spans days.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    changed = []
    for lease in state.get('leases', []):
        if lease_expired(lease, now=now):
            lease['previous_state'] = lease.get('state')
            lease['state'] = 'expired'
            lease['expired_at'] = utc_now()
            changed.append(lease)
    return changed


def translation_lease(lease):
    return lease.get('kind') in ('verb', 'nominal')


def active_translation_leases(state):
    expire_stale_leases(state)
    return [
        lease for lease in state.get('leases', [])
        if translation_lease(lease) and not terminal_state(lease.get('state'))
    ]


def lease_by_id(state, lease_id):
    for lease in state.get('leases', []):
        if lease.get('id') == lease_id:
            return lease
    raise SystemExit('unknown lease: %s' % lease_id)


def artifact_dir(lease_id):
    return os.path.join(paths()['artifacts'], lease_id)


def append_jsonl(path, rec):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    append_jsonl_line(path, rec)


def registry_event(lease, event_type, data=None):
    rec = {
        'schema': REGISTRY_SCHEMA,
        'ts': utc_now(),
        'lease_id': lease.get('id'),
        'event': event_type,
        'kind': lease.get('kind'),
        'target': lease.get('target'),
        'state': lease.get('state'),
        'artifact_dir': lease.get('artifact_dir'),
        'data': data or {},
    }
    append_jsonl(paths()['registry'], rec)


def run_cmd(cmd, cwd=REPO, check=True):
    p = subprocess.run(cmd, cwd=cwd, text=True, encoding='utf-8',
                       capture_output=True)
    if check and p.returncode:
        if p.stdout.strip():
            print(p.stdout.rstrip())
        if p.stderr.strip():
            print(p.stderr.rstrip(), file=sys.stderr)
        raise SystemExit(p.returncode)
    return p


def load_store_key1s(store=None):
    store = store or promote_final_cards.DEFAULT_STORE
    done = set()
    if not os.path.exists(store):
        return done
    with open(store, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    done.add(json.loads(line).get('key1'))
                except json.JSONDecodeError:
                    continue
    return {k for k in done if k}


def active_targets(state):
    expire_stale_leases(state)
    return {lease.get('target') for lease in state.get('leases', [])
            if not terminal_state(lease.get('state'))}


def verb_candidates(state, limit=20):
    payload = verb_worklist.build_worklist()
    leased = active_targets(state)
    roots = [root for root in payload.get('runnable_remaining', []) if root not in leased]
    roots = roots[:limit]
    if not roots:
        return [], payload
    p = run_cmd([sys.executable, os.path.join(HERE, 'perf_preflight.py')] +
                roots + ['--json'], check=False)
    reports = []
    if p.returncode == 0:
        try:
            data = json.loads(p.stdout)
            reports = data.get('reports') or [data]
        except json.JSONDecodeError:
            reports = []
    by_root = {r.get('root'): r for r in reports}
    ordered = []
    for root in roots:
        report = by_root.get(root) or {'root': root, 'agent_expected_after_tm': 9999}
        action = report.get('recommended_action')
        cost_gate = report.get('cost_gate') or {}
        # Cap-and-defer (H304, MG ruling 07-07-2026): a window the cost gate flags is
        # never claimable as bulk — it goes to the deferred-monsters ledger and waits
        # for a dedicated human-budgeted session (see deferred_monsters.jsonl).
        if action == 'defer-calibrate' or cost_gate.get('over_ceiling'):
            reason = ('cost_gate_over_ceiling' if cost_gate.get('over_ceiling')
                      else 'defer-calibrate')
            defer_monster(root, reason, source='coordinator.claim',
                          estimate={k: cost_gate.get(k) for k in
                                    ('est_tokens', 'est_cost_usd', 'est_cost_per_card_usd')
                                    if cost_gate.get(k) is not None} or None,
                          keys=(report.get('cost_partition') or {}).get('defer_monster'))
            continue
        ordered.append(report)
    ordered.sort(key=lambda r: (r.get('agent_expected_after_tm', 9999),
                                len(r.get('selected_keys') or []),
                                r.get('root') or ''))
    return ordered, payload


def nominal_candidates(state, batch_size=12, cards_path=None):
    cards_path = cards_path or os.path.join(SRC, 'assembled_cards.jsonl')
    done = load_store_key1s()
    leased = active_targets(state)
    keys = []
    if not os.path.exists(cards_path):
        return keys
    with open(cards_path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            key = row.get('key1')
            stem = safe_name(key) if key else ''
            target = 'nominal:%s' % key
            if (key and key not in done and target not in leased
                    and not row.get('quarantined_records')
                    and os.path.exists(os.path.join(HERE, 'input', stem + '.raw.txt'))
                    and os.path.exists(os.path.join(HERE, 'input', stem + '.portrait.json'))):
                keys.append(key)
            if len(keys) >= batch_size:
                break
    return keys


def make_lease_id(kind, lane, target):
    safe = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in target)[:40]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return '%s-%s-%s-%d' % (kind, lane, stamp, os.getpid()) if not safe else (
        '%s-%s-%s-%s-%d' % (kind, lane, safe, stamp, os.getpid()))


def claim(args):
    p = ensure_dirs()
    with DirLock(p['lock']):
        state = load_state()
        if translation_lease({'kind': args.kind}) and len(active_translation_leases(state)) >= state.get('translation_limit', TRANSLATION_LIMIT):
            raise SystemExit('translation lease cap reached (%d)' % state.get('translation_limit', TRANSLATION_LIMIT))
        if args.kind == 'verb':
            candidates, worklist = verb_candidates(state)
            if not candidates:
                blocked = len(worklist.get('blocked_missing_rootmap') or []) if isinstance(worklist, dict) else 0
                raise SystemExit('no runnable verb candidate; missing rootmaps=%d' % blocked)
            chosen = candidates[0]
            target = chosen['root']
            details = {'preflight': chosen}
        elif args.kind == 'nominal':
            keys = nominal_candidates(state, batch_size=args.batch_size)
            if not keys:
                raise SystemExit('no nominal/non-root candidate')
            target = 'nominal:%s' % keys[0]
            run_keys = [safe_name(k) for k in keys]
            details = {'keys': keys, 'run_keys': run_keys,
                       'keymap': dict(zip(run_keys, keys))}
        elif args.kind == 'rootmap':
            payload = verb_worklist.build_worklist()
            blocked = [root for root in payload.get('blocked_missing_rootmap', [])
                       if root not in active_targets(state)]
            if not blocked:
                raise SystemExit('no missing-rootmap candidate')
            target = blocked[0]
            details = {'blocked_missing_rootmap_count': len(blocked)}
        else:
            raise SystemExit('unknown kind: %s' % args.kind)

        lease_id = args.lease_id or make_lease_id(args.kind, args.lane, target)
        adir = artifact_dir(lease_id)
        lease = {
            'id': lease_id,
            'lane': args.lane,
            'kind': args.kind,
            'owner': args.owner,
            'target': target,
            'state': 'claimed',
            'claimed_at': utc_now(),
            'expires_at': (datetime.datetime.now(datetime.timezone.utc) +
                           datetime.timedelta(seconds=args.ttl_seconds)).isoformat(
                               timespec='seconds').replace('+00:00', 'Z'),
            'artifact_dir': adir,
            'details': details,
        }
        os.makedirs(adir, exist_ok=True)
        state['leases'].append(lease)
        save_state(state)
        registry_event(lease, 'claimed', details)
    print(json.dumps(lease, ensure_ascii=False, indent=1))


def enforce_cost_gate(preflight_path, target, allow_over_cost=False):
    """Cap-and-defer at prepare time (H304): a lease whose preflight trips the H189/H191
    cost gate is parked in the deferred-monsters ledger and refused, instead of handing the
    operator a harness that repeats the pril10_w1 blow-up ($79.83/3 cards). Pass
    --allow-over-cost only inside an explicitly human-budgeted monster session."""
    try:
        with open(preflight_path, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    for rep in (data.get('reports') or [data]):
        cg = rep.get('cost_gate') or {}
        if not cg.get('over_ceiling'):
            continue
        part = rep.get('cost_partition') or {}
        defer_monster(target or rep.get('root'), 'cost_gate_over_ceiling',
                      source='coordinator.prepare',
                      estimate={k: cg.get(k) for k in
                                ('est_tokens', 'est_cost_usd', 'est_cost_per_card_usd')
                                if cg.get(k) is not None} or None,
                      keys=part.get('defer_monster'))
        if not allow_over_cost:
            raise SystemExit(
                'COST-GATE: %s over ceiling (est ~$%.2f window, ~$%.2f/card) — parked in '
                'deferred_monsters.jsonl. Re-claim with only cost_partition.run_now keys '
                '(%d run-now / %d monster), or re-run prepare with --allow-over-cost in a '
                'dedicated human-budgeted session.'
                % (target or rep.get('root'), cg.get('est_cost_usd') or 0.0,
                   cg.get('est_cost_per_card_usd') or 0.0,
                   len(part.get('run_now') or []), len(part.get('defer_monster') or [])))


def prepare(args):
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
        os.makedirs(adir, exist_ok=True)
        if lease['kind'] == 'verb':
            root = lease['target']
            preflight_path = os.path.join(adir, 'preflight.json')
            p = run_cmd([sys.executable, os.path.join(HERE, 'perf_preflight.py'),
                         root, '--json'])
            with open(preflight_path, 'w', encoding='utf-8') as f:
                f.write(p.stdout)
            enforce_cost_gate(preflight_path, lease.get('target'),
                              allow_over_cost=getattr(args, 'allow_over_cost', False))
            harness = os.path.join(adir, 'run_pilot_wf.%s.js' % lease['id'])
            manifest = os.path.join(adir, 'execution_manifest.%s.json' % lease['id'])
            run_cmd([sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'),
                     root, '--out=%s' % harness, '--manifest-out=%s' % manifest])
        elif lease['kind'] == 'nominal':
            keys = lease.get('details', {}).get('run_keys') or lease.get('details', {}).get('keys') or []
            if not keys:
                raise SystemExit('nominal lease has no keys')
            preflight_path = os.path.join(adir, 'preflight.json')
            root = 'nominal_%s' % lease['id']
            key_arg = ','.join(keys)
            p = run_cmd([sys.executable, os.path.join(HERE, 'perf_preflight.py'),
                         root, '--nominal', '--no-grammar', '--keys=%s' % key_arg, '--json'])
            with open(preflight_path, 'w', encoding='utf-8') as f:
                f.write(p.stdout)
            enforce_cost_gate(preflight_path, lease.get('target'),
                              allow_over_cost=getattr(args, 'allow_over_cost', False))
            harness = os.path.join(adir, 'run_pilot_wf.%s.js' % lease['id'])
            manifest = os.path.join(adir, 'execution_manifest.%s.json' % lease['id'])
            run_cmd([sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'),
                     root, '--nominal', '--no-grammar', '--keys=%s' % key_arg,
                     '--out=%s' % harness, '--manifest-out=%s' % manifest])
        else:
            raise SystemExit('prepare is only for verb/nominal translation leases')
        lease['state'] = 'prepared'
        lease['harness'] = harness
        lease['execution_manifest'] = manifest
        lease['preflight_path'] = preflight_path
        save_state(state)
        registry_event(lease, 'prepared', {'harness': harness, 'manifest': manifest,
                                           'preflight': preflight_path})
    print('harness: %s' % harness)


def normalize_workflow_result(src_path, dst_path):
    with open(src_path, encoding='utf-8') as f:
        wrapper = json.load(f)
    result = wrapper.get('result')
    if isinstance(result, str):
        result = json.loads(result)
    if result is None:
        result = wrapper
    if not isinstance(result, dict):
        raise SystemExit('workflow result is not an object')
    with open(dst_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
    return result


def cost_from_transcript(path):
    if not path:
        return None
    try:
        import parse_workflow_cost
        return parse_workflow_cost.tally(path)
    except Exception as e:
        return {'error': str(e)}


def record_output(args):
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
        os.makedirs(adir, exist_ok=True)
        wf = os.path.join(adir, 'wf_output.%s.json' % lease['id'])
        result = normalize_workflow_result(args.workflow_result, wf)
        if lease.get('kind') == 'nominal':
            result.setdefault('meta', {})['nominal_keymap'] = lease.get('details', {}).get('keymap') or {}
            with open(wf, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False)
        cmd = [sys.executable, os.path.join(HERE, 'audit_window.py'), wf,
               '--write-requeue', '--out-dir', adir]
        if lease.get('kind') == 'verb':
            cmd += ['--root', lease['target']]
        if args.allow_stale:
            cmd.append('--allow-stale')
        audit = run_cmd(cmd, check=False)
        status_path = os.path.join(adir, 'window_status.json')
        report_path = os.path.join(adir, 'audit_window.report.json')
        status = json.load(open(status_path, encoding='utf-8')) if os.path.exists(status_path) else {}
        state_name = status.get('state') or ('blocked' if audit.returncode not in (0, 1) else 'unknown')
        if state_name == 'clean':
            lease['state'] = 'ready'
        elif state_name in ('needs_requeue', 'transient_only'):
            lease['state'] = state_name
        else:
            lease['state'] = state_name
        lease['wf_output'] = wf
        lease['audit_report'] = report_path
        lease['status_path'] = status_path
        lease['recorded_at'] = utc_now()
        lease['workflow_result_count'] = len(result.get('results') or [])
        lease['cost'] = cost_from_transcript(args.transcript_dir)
        save_state(state)
        registry_event(lease, 'recorded', {
            'wf_output': wf,
            'status': state_name,
            'audit_returncode': audit.returncode,
            'cost': lease.get('cost'),
        })
    if audit.stdout.strip():
        print(audit.stdout.rstrip())
    if audit.stderr.strip():
        print(audit.stderr.rstrip(), file=sys.stderr)
    print('lease %s -> %s' % (lease['id'], lease['state']))


def prepare_requeue(args):
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
        which = 'transient' if args.transient else 'defect'
        rq = os.path.join(adir, 'requeue.%s.keys.txt' % which)
        legacy = os.path.join(adir, {
            'transient': 'requeue.transient.keys.txt',
            'defect': 'requeue.defect.keys.txt',
        }[which])
        if not os.path.exists(rq) and os.path.exists(legacy):
            rq = legacy
        harness = os.path.join(adir, 'run_pilot_wf.%s.requeue.%s.js' % (lease['id'], which))
        root = 'nominal_%s' % lease['id'] if lease.get('kind') == 'nominal' else lease['target']
        cmd = [sys.executable, os.path.join(HERE, 'requeue_from_audit.py'),
               root, '--%s' % which, '--requeue-file=%s' % rq, '--out=%s' % harness]
        if lease.get('kind') == 'nominal':
            cmd += ['--nominal', '--no-grammar']
        p = run_cmd(cmd)
        lease['state'] = 'requeue_prepared'
        lease['requeue_harness'] = harness
        lease['requeue_kind'] = which
        save_state(state)
        registry_event(lease, 'requeue_prepared', {'harness': harness, 'kind': which})
    if p.stdout.strip():
        print(p.stdout.rstrip())
    print('harness: %s' % harness)


def promote_ready(args):
    if not args.gen_model_version or args.gen_model_version in ('sonnet', 'claude-sonnet'):
        raise SystemExit('exact --gen-model-version is required')
    with DirLock(paths()['promotion_lock']):
        with DirLock(paths()['lock']):
            state = load_state()
            ready = [lease for lease in state.get('leases', [])
                     if lease.get('state') == 'ready' and lease.get('wf_output')]
            if not ready:
                raise SystemExit('no ready leases to promote')
        for lease in ready:
            rel_glob = os.path.relpath(
                os.path.join(lease['artifact_dir'], 'wf_output*.json'), REPO)
            run_cmd([sys.executable, os.path.join(SRC, 'promote_final_cards.py'),
                     '--merge', '--glob', rel_glob,
                     '--gen-model-version', args.gen_model_version])
            with DirLock(paths()['lock']):
                state = load_state()
                fresh = lease_by_id(state, lease['id'])
                fresh['state'] = 'promoted'
                fresh['promoted_at'] = utc_now()
                fresh['model_version'] = args.gen_model_version
                save_state(state)
                registry_event(fresh, 'promoted', {'glob': rel_glob})
        run_cmd([sys.executable, os.path.join(HERE, 'translation_memory.py'), 'build', '--lang', 'ru'])
        if any('"frag_prov"' in open(fp, encoding='utf-8').read()
               for fp in glob.glob(os.path.join(paths()['artifacts'], '*', 'wf_output*.json'))):
            run_cmd([sys.executable, os.path.join(HERE, 'translation_memory.py'), 'build-frags',
                     '--lang', 'ru', '--glob', 'src/pilot/output/coordinator/artifacts/*/wf_output*.json'])
        run_cmd([sys.executable, os.path.join(HERE, 'translation_memory.py'), 'validate', '--lang', 'ru'])
    print('promoted %d lease(s)' % len(ready))


def daily_close(args):
    with DirLock(paths()['lock']):
        state = load_state()
    checks = []
    commands = [
        ['translation_memory.py', 'build', '--lang', 'ru'],
        ['translation_memory.py', 'validate', '--lang', 'ru'],
        ['translation_memory.py', 'export-publication', '--lang', 'ru'],
        ['translation_memory.py', 'validate', '--lang', 'ru', '--publication',
         os.path.join(REPO, 'release', 'translation_memory', 'translation_memory.ru.publication.jsonl')],
        ['window_selftest.py'],
    ]
    for cmd in commands:
        script = os.path.join(HERE, cmd[0])
        full = [sys.executable, script] + cmd[1:]
        p = run_cmd(full, check=False)
        checks.append({'cmd': ' '.join(cmd), 'returncode': p.returncode,
                       'stdout_tail': p.stdout[-1000:], 'stderr_tail': p.stderr[-1000:]})
    promoted_today = 0
    today = utc_now()[:10]
    for lease in state.get('leases', []):
        if (lease.get('promoted_at') or '').startswith(today):
            promoted_today += 1
    rec = {
        'schema': DAILY_SCHEMA,
        'ts': utc_now(),
        'date': today,
        'promoted_leases_today': promoted_today,
        'active_translation_leases': len(active_translation_leases(state)),
        'blocked_leases': len([l for l in state.get('leases', []) if l.get('state') == 'blocked']),
        'checks': checks,
        'validation_clean': all(c['returncode'] == 0 for c in checks),
    }
    append_jsonl(paths()['daily'], rec)
    write_dashboard(state, daily=rec)
    print(json.dumps(rec, ensure_ascii=False, indent=1))
    if not rec['validation_clean']:
        raise SystemExit(1)


def write_dashboard(state, daily=None):
    p = ensure_dirs()
    leases = state.get('leases', [])
    payload = {
        'schema': DASHBOARD_SCHEMA,
        'generated_at': utc_now(),
        'translation_limit': state.get('translation_limit', TRANSLATION_LIMIT),
        'active_translation_leases': len(active_translation_leases(state)),
        'leases': leases[-30:],
        'ready': [l.get('id') for l in leases if l.get('state') == 'ready'],
        'blocked': [l.get('id') for l in leases if l.get('state') == 'blocked'],
        'cap': state.get('cap') or {},
        'daily': daily,
    }
    tmp = p['dashboard'] + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p['dashboard'])


def status(args):
    with DirLock(paths()['lock']):
        state = load_state()
        save_state(state)
    leases = state.get('leases', [])
    print('PWG RU SLA coordinator')
    print('state       : %s' % paths()['state'])
    print('leases      : %d' % len(leases))
    print('active LLM  : %d/%d' % (len(active_translation_leases(state)),
                                  state.get('translation_limit', TRANSLATION_LIMIT)))
    for lease in leases[-20:]:
        print('  {id} [{kind}/{lane}] {state} target={target}'.format(**lease))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('status')
    s.set_defaults(func=status)
    c = sub.add_parser('claim')
    c.add_argument('--lane', required=True)
    c.add_argument('--kind', required=True, choices=('verb', 'nominal', 'rootmap'))
    c.add_argument('--owner', required=True)
    c.add_argument('--lease-id')
    c.add_argument('--batch-size', type=int, default=12)
    c.add_argument('--ttl-seconds', type=int, default=LEASE_TTL_SECONDS)
    c.set_defaults(func=claim)
    p = sub.add_parser('prepare')
    p.add_argument('lease_id')
    p.add_argument('--allow-over-cost', action='store_true',
                   help='H304 cap-and-defer override: prepare a cost-gate-flagged window '
                        'anyway (dedicated human-budgeted monster session only)')
    p.set_defaults(func=prepare)
    r = sub.add_parser('record-output')
    r.add_argument('lease_id')
    r.add_argument('workflow_result')
    r.add_argument('--transcript-dir')
    r.add_argument('--allow-stale', action='store_true')
    r.set_defaults(func=record_output)
    rq = sub.add_parser('prepare-requeue')
    rq.add_argument('lease_id')
    g = rq.add_mutually_exclusive_group(required=True)
    g.add_argument('--transient', action='store_true')
    g.add_argument('--defect', action='store_true')
    rq.set_defaults(func=prepare_requeue)
    pr = sub.add_parser('promote-ready')
    pr.add_argument('--gen-model-version', required=True)
    pr.set_defaults(func=promote_ready)
    d = sub.add_parser('daily-close')
    d.set_defaults(func=daily_close)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
