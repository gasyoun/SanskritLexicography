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
PREPARATION_LIMIT = 100
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
from window_common import (  # noqa: E402
    append_jsonl_line,
    atomic_write_json,
    atomic_write_text,
    defer_monster,
    sha256_file,
)


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def nonempty_line_count(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding='utf-8') as f:
        return sum(bool(line.strip()) for line in f)


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
    def __init__(self, path, ttl_seconds=LOCK_TTL_SECONDS, wait_seconds=30):
        self.path = path
        self.ttl_seconds = ttl_seconds
        self.wait_seconds = wait_seconds

    def __enter__(self):
        deadline = time.time() + self.wait_seconds
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
        'preparation_limit': PREPARATION_LIMIT,
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
    state.setdefault('preparation_limit', PREPARATION_LIMIT)
    state.setdefault('cap', {})
    return state


def save_state(state):
    p = ensure_dirs()
    expire_stale_leases(state)
    state['updated_at'] = utc_now()
    atomic_write_json(p['state'], state, indent=1)
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
        if translation_lease({'kind': args.kind}) and len(active_translation_leases(state)) >= state.get('preparation_limit', PREPARATION_LIMIT):
            raise SystemExit('translation preparation cap reached (%d)' % state.get('preparation_limit', PREPARATION_LIMIT))
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


def register_prepared_lease(lease_id, lane, keys, harness, manifest, preflight_path,
                            artifact_path=None, owner='no_pwg_scale_plan'):
    """Register an already-generated deterministic nominal window without consuming a runtime slot."""
    with DirLock(paths()['lock']):
        state = load_state()
        if any(lease.get('id') == lease_id for lease in state.get('leases', [])):
            raise SystemExit('lease already exists: %s' % lease_id)
        active = active_targets(state)
        target = 'nominal:%s' % keys[0]
        if target in active:
            raise SystemExit('lease target already active: %s' % target)
        run_keys = [safe_name(k) for k in keys]
        lease = {
            'id': lease_id, 'lane': lane, 'kind': 'nominal', 'owner': owner,
            'target': target, 'state': 'prepared', 'claimed_at': utc_now(),
            'prepared_at': utc_now(), 'artifact_dir': artifact_path or os.path.dirname(manifest),
            'details': {'keys': keys, 'run_keys': run_keys,
                        'keymap': dict(zip(run_keys, keys))},
            'harness': os.path.abspath(harness),
            'execution_manifest': os.path.abspath(manifest),
            'preflight_path': os.path.abspath(preflight_path),
        }
        state['leases'].append(lease)
        save_state(state)
        registry_event(lease, 'prepared', {'harness': lease['harness'],
                                           'manifest': lease['execution_manifest'],
                                           'preflight': lease['preflight_path']})
    return lease


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
            atomic_write_text(preflight_path, p.stdout)
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
            atomic_write_text(preflight_path, p.stdout)
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
    atomic_write_json(dst_path, result, indent=None)
    return result


def clean_result_payload(result, rejected):
    rejected = set(rejected or [])
    rows = [row for row in (result.get('results') or [])
            if row.get('card') and row.get('key') not in rejected]
    payload = dict(result)
    payload['results'] = rows
    payload['summary'] = dict(result.get('summary') or {}, cards=len(rows), ok=len(rows),
                              null=0, null_keys=[], failures={})
    return payload


def read_execution_manifest(path):
    if not path:
        raise SystemExit('execution manifest path is missing')
    try:
        with open(path, encoding='utf-8') as f:
            manifest = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit('execution manifest is unreadable: %s' % e)
    if manifest.get('schema') != 'pwg.headless_execution_manifest.v1':
        raise SystemExit('unsupported execution manifest schema: %r' % manifest.get('schema'))
    if not isinstance(manifest.get('meta'), dict):
        raise SystemExit('execution manifest meta is missing or invalid')
    return manifest


def manifest_history_entry(path, attempt, kind, artifact_path, prepared_at=None):
    manifest = read_execution_manifest(path)
    meta = manifest['meta']
    return {
        'attempt': int(attempt),
        'kind': kind,
        'path': os.path.abspath(path),
        'sha256': sha256_file(path),
        'artifact_dir': os.path.abspath(artifact_path),
        'root': meta.get('root'),
        'nominal': bool(meta.get('nominal')),
        'selected_keys': list(meta.get('selected_keys') or []),
        'prepared_at': prepared_at or utc_now(),
    }


def cost_from_transcript(path):
    if not path:
        return None
    try:
        import parse_workflow_cost
        return parse_workflow_cost.tally(path)
    except Exception as e:
        return {'error': str(e)}


PROMOTABLE_AUDIT_EXITS = {'clean': 0, 'needs_requeue': 1, 'transient_only': 1}


def validate_promotable_audit(wf, status, report, state_name, returncode):
    errors = []
    expected_exit = PROMOTABLE_AUDIT_EXITS.get(state_name)
    if expected_exit is None:
        errors.append('audit state %r is not promotable' % state_name)
    elif returncode != expected_exit:
        errors.append('audit exit %r does not match %s' % (returncode, state_name))
    if not isinstance(status, dict) or status.get('state') != state_name:
        errors.append('window status is missing or disagrees with audit state')
    if not isinstance(report, dict):
        errors.append('audit report is missing or invalid')
        return errors
    report_wf = report.get('workflow')
    if not report_wf or os.path.abspath(report_wf) != os.path.abspath(wf):
        errors.append('audit report is not bound to the recorded workflow output')
    if report.get('crashed'):
        errors.append('audit report contains crashed gates')
    if not (report.get('stale_check') or {}).get('ok'):
        errors.append('audit provenance did not pass')
    requeue = set(report.get('requeue') or [])
    status_requeue = set(status.get('requeue_keys') or [])
    if requeue != status_requeue:
        errors.append('audit report and status requeue sets disagree')
    if state_name == 'clean' and requeue:
        errors.append('clean audit unexpectedly contains requeue keys')
    if state_name in ('needs_requeue', 'transient_only') and not requeue:
        errors.append('partial audit has no explicit requeue keys')
    return errors


def recorded_lease_state(state_name, audit_errors, clean_rows):
    if state_name not in PROMOTABLE_AUDIT_EXITS:
        return state_name, False
    if audit_errors:
        return 'blocked', False
    if clean_rows:
        return ('ready' if state_name == 'clean' else 'ready_partial'), True
    if state_name in ('needs_requeue', 'transient_only'):
        return state_name, False
    return 'blocked', False


def record_output(args):
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        base_adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
        adir = lease.get('current_artifact_dir') or base_adir
        os.makedirs(adir, exist_ok=True)
        wf = os.path.join(adir, 'wf_output.%s.json' % lease['id'])
        result = normalize_workflow_result(args.workflow_result, wf)
        if lease.get('kind') == 'nominal':
            result.setdefault('meta', {})['nominal_keymap'] = lease.get('details', {}).get('keymap') or {}
            atomic_write_json(wf, result, indent=None)
        cmd = [sys.executable, os.path.join(HERE, 'audit_window.py'), wf,
               '--write-requeue', '--out-dir', adir]
        manifest = lease.get('execution_manifest') or os.path.join(
            adir, '__missing_execution_manifest__.json')
        cmd += ['--execution-manifest', manifest]
        if lease.get('kind') == 'verb':
            cmd += ['--root', lease['target']]
        if args.allow_stale:
            cmd.append('--allow-stale')
        audit = run_cmd(cmd, check=False)
        status_path = os.path.join(adir, 'window_status.json')
        report_path = os.path.join(adir, 'audit_window.report.json')
        try:
            status = json.load(open(status_path, encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            status = {}
        try:
            report = json.load(open(report_path, encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            report = {}
        state_name = status.get('state') or ('blocked' if audit.returncode not in (0, 1) else 'unknown')
        rejected = set(report.get('requeue') or status.get('requeue_keys') or [])
        clean_payload = clean_result_payload(result, rejected)
        clean_rows = clean_payload['results']
        audit_errors = validate_promotable_audit(
            wf, status, report, state_name, audit.returncode)
        lease_state, promotable = recorded_lease_state(state_name, audit_errors, clean_rows)
        clean_output = None
        if promotable:
            clean_output = os.path.join(adir, 'wf_output.clean.%s.json' % lease['id'])
            atomic_write_json(clean_output, clean_payload, indent=None)
        lease['audit_state'] = state_name
        lease['state'] = lease_state
        lease['wf_output'] = wf
        lease['clean_output'] = clean_output
        lease['clean_count'] = len(clean_rows) if promotable else 0
        lease['clean_output_sha256'] = sha256_file(clean_output) if clean_output else None
        lease['audit_report'] = report_path
        lease['status_path'] = status_path
        lease['audit_returncode'] = audit.returncode
        lease['audit_errors'] = audit_errors
        lease['recorded_at'] = utc_now()
        lease['workflow_result_count'] = len(result.get('results') or [])
        lease['cost'] = cost_from_transcript(args.transcript_dir)
        lease['current_artifact_dir'] = adir
        save_state(state)
        registry_event(lease, 'recorded', {
            'wf_output': wf,
            'execution_manifest': manifest,
            'artifact_dir': adir,
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
        lease_state = lease.get('state')
        if lease_state == 'ready_partial':
            raise SystemExit(
                '%s: promote the verified clean subset before preparing its requeue' % lease['id'])
        allowed = ('promoted_partial', 'needs_requeue', 'transient_only')
        if lease_state not in allowed:
            raise SystemExit('%s: cannot prepare requeue from lease state %r' %
                             (lease['id'], lease_state))
        adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
        source_dir = os.path.dirname(lease.get('status_path') or '') or adir
        which = 'transient' if args.transient else 'defect'
        rq = os.path.join(source_dir, 'requeue.%s.keys.txt' % which)
        legacy = os.path.join(source_dir, {
            'transient': 'requeue.transient.keys.txt',
            'defect': 'requeue.defect.keys.txt',
        }[which])
        if not os.path.exists(rq) and os.path.exists(legacy):
            rq = legacy
        if not os.path.exists(rq):
            raise SystemExit('%s: requeue file is missing: %s' % (lease['id'], rq))
        with open(rq, encoding='utf-8') as f:
            requeue_keys = [line.strip() for line in f if line.strip()]
        if not requeue_keys:
            raise SystemExit('%s: requeue file is empty: %s' % (lease['id'], rq))

        current_manifest_path = lease.get('execution_manifest')
        current_manifest = read_execution_manifest(current_manifest_path)
        current_meta = current_manifest['meta']
        root = current_meta.get('root')
        if not root:
            raise SystemExit('%s: execution manifest has no root' % lease['id'])
        nominal = bool(current_meta.get('nominal'))
        attempt = int(lease.get('requeue_attempt') or 0) + 1
        attempt_tag = 'rq%02d-%s' % (attempt, which)
        attempt_dir = os.path.join(adir, 'requeue', attempt_tag)
        os.makedirs(attempt_dir, exist_ok=False)
        harness = os.path.join(attempt_dir, 'run_pilot_wf.%s.%s.js' %
                               (lease['id'], attempt_tag))
        manifest = os.path.join(attempt_dir, 'execution_manifest.%s.%s.json' %
                                (lease['id'], attempt_tag))
        old_manifest_sha256 = sha256_file(current_manifest_path)
        cmd = [sys.executable, os.path.join(HERE, 'requeue_from_audit.py'),
               root, '--%s' % which, '--requeue-file=%s' % rq, '--out=%s' % harness,
               '--manifest-out=%s' % manifest]
        if nominal:
            cmd += ['--nominal', '--no-grammar']
        try:
            p = run_cmd(cmd)
            if sha256_file(current_manifest_path) != old_manifest_sha256:
                raise SystemExit(
                    '%s: previous execution manifest changed during requeue preparation' %
                    lease['id'])
            prepared_manifest = read_execution_manifest(manifest)
            if (prepared_manifest['meta'].get('selected_keys') or []) != requeue_keys:
                raise SystemExit('%s: requeue execution manifest key drift' % lease['id'])
        except BaseException:
            shutil.rmtree(attempt_dir, ignore_errors=True)
            raise
        history = lease.setdefault('execution_manifest_history', [])
        current_abs = os.path.abspath(current_manifest_path)
        if not any(os.path.abspath(row.get('path') or '') == current_abs for row in history):
            history.append(manifest_history_entry(
                current_manifest_path, lease.get('requeue_attempt') or 0,
                'initial' if not history else lease.get('requeue_kind') or 'requeue',
                lease.get('current_artifact_dir') or adir,
                lease.get('prepared_at') or lease.get('recorded_at')))
        prepared_at = utc_now()
        history.append(manifest_history_entry(
            manifest, attempt, which, attempt_dir, prepared_at))
        lease['state'] = 'requeue_prepared'
        lease['requeue_harness'] = harness
        lease['requeue_kind'] = which
        lease['requeue_attempt'] = attempt
        lease['execution_manifest'] = manifest
        lease['current_artifact_dir'] = attempt_dir
        lease['current_attempt'] = {
            'number': attempt,
            'kind': which,
            'artifact_dir': attempt_dir,
            'harness': harness,
            'execution_manifest': manifest,
            'prepared_at': prepared_at,
            'selected_keys': requeue_keys,
        }
        save_state(state)
        registry_event(lease, 'requeue_prepared', {
            'attempt': attempt, 'artifact_dir': attempt_dir,
            'harness': harness, 'manifest': manifest, 'kind': which,
            'selected_keys': requeue_keys,
        })
    if p.stdout.strip():
        print(p.stdout.rstrip())
    print('harness: %s' % harness)


def promote_ready(args):
    if not args.gen_model_version or args.gen_model_version in ('sonnet', 'claude-sonnet'):
        raise SystemExit('exact --gen-model-version is required')
    with DirLock(paths()['promotion_lock']):
        with DirLock(paths()['lock']):
            state = load_state()
            lease_scope = set(getattr(args, 'lease_id', None) or [])
            ready = [lease for lease in state.get('leases', [])
                     if lease.get('state') in ('ready', 'ready_partial')
                     and lease.get('clean_output')
                     and (not lease_scope or lease.get('id') in lease_scope)]
            if not ready:
                raise SystemExit('no ready leases to promote')
        for lease in ready:
            source = lease['clean_output']
            try:
                status = json.load(open(lease['status_path'], encoding='utf-8'))
                report = json.load(open(lease['audit_report'], encoding='utf-8'))
                clean_payload = json.load(open(source, encoding='utf-8'))
            except (KeyError, OSError, json.JSONDecodeError) as e:
                raise SystemExit('%s: promotion artifacts are unreadable: %s' % (lease['id'], e))
            errors = validate_promotable_audit(
                lease['wf_output'], status, report, lease.get('audit_state'),
                lease.get('audit_returncode'))
            expected_lease_state = ('ready' if lease.get('audit_state') == 'clean'
                                    else 'ready_partial')
            if lease.get('state') != expected_lease_state:
                errors.append('lease state does not match audited promotion class')
            clean_rows = clean_payload.get('results') or []
            if not clean_rows or any(not row.get('card') for row in clean_rows):
                errors.append('clean output is empty or contains null cards')
            if len(clean_rows) != lease.get('clean_count'):
                errors.append('clean output count does not match lease')
            if sha256_file(source) != lease.get('clean_output_sha256'):
                errors.append('clean output hash does not match recorded artifact')
            if errors:
                raise SystemExit('%s: promotion refused: %s' %
                                 (lease['id'], '; '.join(errors)))
            rel_glob = os.path.relpath(source, REPO)
            store_before = nonempty_line_count(promote_final_cards.DEFAULT_STORE)
            run_cmd([sys.executable, os.path.join(SRC, 'promote_final_cards.py'),
                     '--merge', '--glob', rel_glob,
                     '--gen-model-version', args.gen_model_version])
            store_after = nonempty_line_count(promote_final_cards.DEFAULT_STORE)
            if lease.get('clean_count') and store_after <= store_before:
                raise SystemExit('%s: promotion produced no positive canonical-store delta' % lease['id'])
            with DirLock(paths()['lock']):
                state = load_state()
                fresh = lease_by_id(state, lease['id'])
                fresh['state'] = ('promoted_partial' if fresh.get('audit_state') != 'clean'
                                  else 'promoted')
                fresh['promoted_at'] = utc_now()
                fresh['model_version'] = args.gen_model_version
                fresh['store_before'] = store_before
                fresh['store_after'] = store_after
                fresh['store_delta'] = store_after - store_before
                save_state(state)
                registry_event(fresh, 'promoted', {'glob': rel_glob,
                                                   'store_before': store_before,
                                                   'store_after': store_after,
                                                   'store_delta': store_after - store_before})
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
    atomic_write_json(p['dashboard'], payload, indent=1)


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
    pr.add_argument('--lease-id', action='append',
                    help='promote only these ready lease IDs (repeatable)')
    pr.set_defaults(func=promote_ready)
    d = sub.add_parser('daily-close')
    d.set_defaults(func=daily_close)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
