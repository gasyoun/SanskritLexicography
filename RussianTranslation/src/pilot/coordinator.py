#!/usr/bin/env python
"""Deterministic coordinator for the PWG->RU 30-day SLA lanes.

The coordinator owns leases and artifact paths only. It does not run the
Max/Workflow surface; operators still run the generated harness from the coding
session and feed the full result back through record-output.
"""
import argparse
from collections import Counter
import copy
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)

from dashboard_events import emit_collision  # noqa: E402

def input_dir():
    """H1386 P3f: PWG_INPUT_DIR points a hermetic harness at a sandbox input dir.
    Resolved PER CALL (never a module constant): callers that rebind HERE (the
    selftest seam) and env changes must both take effect."""
    return os.environ.get('PWG_INPUT_DIR') or os.path.join(HERE, 'input')
OUT = os.path.join(HERE, 'output')
DEFAULT_COORD_DIR = os.path.join(OUT, 'coordinator')
ARTIFACT_DIRNAME = 'artifacts'
STATE_SCHEMA = 'pwg.sla_coordinator.state.v1'
DASHBOARD_SCHEMA = 'pwg.sla_coordinator.dashboard.v1'
REGISTRY_SCHEMA = 'pwg.sla_coordinator.artifact.v1'
DAILY_SCHEMA = 'pwg.sla_coordinator.daily.v1'
TRANSLATION_LIMIT = 3
STAGED_TRANSLATION_LIMIT = 4
PREPARATION_LIMIT = 100
LEASE_TTL_SECONDS = 6 * 60 * 60
LOCK_TTL_SECONDS = 10 * 60
LOCK_META_GRACE_SECONDS = 2
PREPARE_TIMEOUT_SECONDS = 10 * 60
AUDIT_TIMEOUT_SECONDS = 30 * 60
# A single probe authorizes one bounded staged run, whose successive four-window batches can
# legitimately span hours. It still expires fail-closed before a later operator session.
PROBE_RECEIPT_MAX_AGE_SECONDS = 6 * 60 * 60
PROBE_RECEIPT_SCHEMA = 'pwg.runtime_probe_receipt.v1'
PROBE_MODEL = 'claude-sonnet-5'
# PROBE_POLICY / PROBE_LATENCY_CEILING_MS are DERIVED from probe_log below, once sys.path is
# set up -- they cannot be defined here because the import has to follow that setup.

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import probe_log  # noqa: E402
# H2118 (#946): DERIVED from the one source of truth, never restated. This was previously a
# third hard-coded `65000` held in lockstep with max_account_orchestrator by a comment; the
# comment's own rationale conceded that duplication is what let the production ceiling sit at
# 30 000 and silently keep translation blocked after the gate probe's ceiling was raised.
# The old objection -- "coordinator must not take an import dependency on the orchestrator" --
# is satisfied: this imports `probe_log`, a stdlib-only leaf module, not the orchestrator.
PROBE_POLICY = probe_log.CURRENT_POLICY
PROBE_LATENCY_CEILING_MS = probe_log.ceiling_for(PROBE_POLICY)

import promote_final_cards  # noqa: E402
import promotion_journal  # noqa: E402
from safe_filename import safe_name  # noqa: E402
import translation_memory  # noqa: E402
import verb_worklist  # noqa: E402
from window_common import (  # noqa: E402
    append_jsonl_line,
    atomic_write_json,
    atomic_write_text,
    defer_monster,
    fsync_existing_path,
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
        'promotions': os.path.join(base, 'promotions'),
        'registry': os.path.join(base, 'artifact_registry.jsonl'),
        'daily': os.path.join(base, 'daily_metrics.jsonl'),
        'dashboard': os.path.join(base, 'dashboard.json'),
        'artifacts': os.path.join(base, ARTIFACT_DIRNAME),
    }


def _frag_prov_glob():
    """C7: the ONE glob both the frag_prov detection and the build-frags call use — derived from
    paths()['artifacts'], so a custom PWG_COORDINATOR_DIR (per-run / worktree coordinator dir) is
    honored on both sides. Previously detection honored it but build-frags hardcoded the default
    tree, so a custom dir detected frag_prov here yet built the fragment TM from the empty default
    tree, silently dropping the just-promoted window's fragments."""
    # H1386 C3: '**' (recursive) -- a requeue attempt's corrected wf_output lands two dirs
    # deep at artifacts/<lease>/requeue/rqNN-<kind>/, which the old single-'*' never
    # matched, so a rework's fragments were never harvested at all.
    return os.path.join(paths()['artifacts'], '**', 'wf_output*.json')


def ensure_dirs():
    p = paths()
    os.makedirs(p['base'], exist_ok=True)
    os.makedirs(p['artifacts'], exist_ok=True)
    os.makedirs(p['promotions'], exist_ok=True)
    return p


ERROR_INVALID_PARAMETER = 87  # OpenProcess for a nonexistent pid -> definitively dead


def _win32_alive_on_openprocess_error(err):
    # P2 (H1420): OpenProcess failed, so the pid must be ruled alive-or-dead from the error alone.
    # The ONLY error that definitively proves the pid is gone is ERROR_INVALID_PARAMETER (87 = no
    # such pid). Everything else -- ERROR_ACCESS_DENIED (5, a live process we merely lack rights to
    # open), a transient handle/-memory error, or any unexpected code -- must lean ALIVE, so a live
    # lock-holder is never falsely reported dead and reclaimed into two writers (the A1
    # double-writer window, H1283). The prior `err == ERROR_ACCESS_DENIED` inverted this: it
    # reported DEAD for every error except 5 -- the unsafe direction on any transient probe error.
    return err != ERROR_INVALID_PARAMETER


def _win32_pid_alive(pid):
    # A1 (H1283): os.kill(pid, 0) on win32 is GenerateConsoleCtrlEvent(CTRL_C_EVENT), NOT a
    # liveness probe -- it reported a LIVE >600 s promotion-lock holder (whose TM rebuild
    # legitimately runs >10 min) as dead, so DirLock.stale() reclaimed the lock into two
    # concurrent state.json / canonical-store writers. Probe correctly via OpenProcess +
    # GetExitCodeProcess == STILL_ACTIVE.
    import ctypes
    from ctypes import wintypes
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return _win32_alive_on_openprocess_error(ctypes.get_last_error())
    try:
        code = wintypes.DWORD()
        k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        if not k32.GetExitCodeProcess(h, ctypes.byref(code)):
            return True  # handle opened but exit code unreadable -> treat as alive
        return code.value == STILL_ACTIVE
    finally:
        k32.CloseHandle(h)


def pid_alive(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if sys.platform == 'win32':
        try:
            return _win32_pid_alive(pid)
        except Exception:
            return True  # never falsely reclaim a lock on a probe error (A1 direction)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
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
        # A1 (H1283): only remove the lock if WE still own it. If this lock was reclaimed and
        # re-created by another process (e.g. after a stale() ruling), its owner.json now
        # carries a different pid; a blind rmtree here would destroy the NEW owner's live lock.
        try:
            meta = json.load(open(os.path.join(self.path, 'owner.json'), encoding='utf-8'))
            if meta.get('pid') != os.getpid():
                return
        except (OSError, json.JSONDecodeError):
            pass  # no readable owner.json -> our own incomplete lock dir; clean it up
        shutil.rmtree(self.path, ignore_errors=True)

    def write_meta(self):
        with open(os.path.join(self.path, 'owner.json'), 'w', encoding='utf-8') as f:
            json.dump({'pid': os.getpid(), 'created_at': utc_now()}, f, indent=1)

    def stale(self):
        meta_path = os.path.join(self.path, 'owner.json')
        try:
            meta = json.load(open(meta_path, encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            # os.mkdir() and owner.json creation are separate operations. A contender can
            # legitimately observe the directory in that tiny gap; never delete that live lock.
            try:
                return time.time() - os.path.getmtime(self.path) > LOCK_META_GRACE_SECONDS
            except OSError:
                return False
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
        'runtime_limit': TRANSLATION_LIMIT,
        'runtime_mode': 'standard',
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
    state.setdefault('runtime_limit', state.get('translation_limit', TRANSLATION_LIMIT))
    state.setdefault('runtime_mode', 'standard')
    state.setdefault('preparation_limit', PREPARATION_LIMIT)
    state.setdefault('cap', {})
    normalize_lease_reservations(state)
    return state


def prepare_state_for_save(state, updated_at=None):
    """Normalize state exactly once so promotion can seal the bytes before replacement."""
    p = ensure_dirs()
    expire_stale_leases(state)
    normalize_lease_reservations(state)
    running = running_translation_leases(state)
    state['runtime_mode'] = ('staged-probed' if any(
        lease.get('runtime_mode') == 'staged-probed' for lease in running) else 'standard')
    state['runtime_limit'] = (max(
        (int(lease.get('runtime_limit') or TRANSLATION_LIMIT) for lease in running),
        default=TRANSLATION_LIMIT) if state['runtime_mode'] == 'staged-probed'
                              else TRANSLATION_LIMIT)
    state['updated_at'] = updated_at or utc_now()
    return p


def serialized_state(state):
    return json.dumps(state, ensure_ascii=False, indent=1).encode('utf-8')


def save_state(state, updated_at=None):
    p = prepare_state_for_save(state, updated_at=updated_at)
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


def _validate_reserved_keys(value):
    if not isinstance(value, list) or not value:
        return None, 'reserved_keys must be a non-empty list'
    if any(not isinstance(key, str) or not key for key in value):
        return None, 'reserved_keys contains an invalid key'
    if len(value) != len(set(value)):
        return None, 'reserved_keys contains duplicate keys'
    return list(value), None


def derive_lease_reserved_keys(lease):
    """Return canonical nominal keys for new and legacy leases, or an explicit error.

    Runtime/safe keys are not sufficient for collision detection because a later candidate is
    selected by its canonical assembled-card key1. Prefer the persisted reservation, then the
    claim details, and finally a prepared execution manifest's nominal keymap.
    """
    if lease.get('kind') != 'nominal':
        return [], None
    if 'reserved_keys' in lease:
        return _validate_reserved_keys(lease.get('reserved_keys'))
    details = lease.get('details') or {}
    if details.get('keys') is not None:
        return _validate_reserved_keys(details.get('keys'))
    keymap = details.get('keymap')
    if isinstance(keymap, dict) and keymap:
        return _validate_reserved_keys(list(keymap.values()))
    manifest_path = lease.get('execution_manifest') or lease.get('origin_execution_manifest')
    if manifest_path:
        try:
            with open(manifest_path, encoding='utf-8') as f:
                manifest = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            return None, 'execution manifest is unreadable: %s' % exc
        meta = manifest.get('meta') or {}
        selected = meta.get('selected_keys')
        keymap = meta.get('nominal_keymap')
        if isinstance(selected, list) and isinstance(keymap, dict):
            if any(key not in keymap for key in selected):
                return None, 'execution manifest nominal_keymap does not cover selected_keys'
            return _validate_reserved_keys([keymap[key] for key in selected])
    return None, 'canonical nominal keys cannot be derived from lease details or manifest'


def normalize_lease_reservations(state):
    """Backfill additive reservation state without making read-only status unusable."""
    for lease in state.get('leases', []):
        if lease.get('kind') != 'nominal':
            continue
        keys, error = derive_lease_reserved_keys(lease)
        if error:
            lease['reservation_error'] = error
        else:
            lease['reserved_keys'] = keys
            lease.pop('reservation_error', None)


def active_reserved_nominal_keys(state, exclude_lease_id=None, strict=True):
    """Canonical keys owned by nonterminal nominal leases.

    A new claim must fail closed if any active legacy lease cannot prove its full reservation;
    otherwise a partially-known batch could overlap silently.
    """
    expire_stale_leases(state)
    normalize_lease_reservations(state)
    reserved = set()
    for lease in state.get('leases', []):
        if (lease.get('kind') != 'nominal' or terminal_state(lease.get('state'))
                or lease.get('id') == exclude_lease_id):
            continue
        error = lease.get('reservation_error')
        if error:
            if strict:
                raise SystemExit('active nominal lease %s has unresolved reservations: %s'
                                 % (lease.get('id'), error))
            continue
        reserved.update(lease.get('reserved_keys') or [])
    return reserved


def reserved_translation_leases(state):
    expire_stale_leases(state)
    return [
        lease for lease in state.get('leases', [])
        if translation_lease(lease) and not terminal_state(lease.get('state'))
    ]


def running_translation_leases(state):
    expire_stale_leases(state)
    return [
        lease for lease in state.get('leases', [])
        if translation_lease(lease) and lease.get('state') in ('running', 'auditing')
    ]


def active_translation_leases(state):
    """Deprecated compatibility alias: active now means consuming runtime."""
    return running_translation_leases(state)


def lease_by_id(state, lease_id):
    for lease in state.get('leases', []):
        if lease.get('id') == lease_id:
            return lease
    raise SystemExit('unknown lease: %s' % lease_id)


def artifact_dir(lease_id):
    return os.path.join(paths()['artifacts'], lease_id)


def append_jsonl(path, rec):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    append_jsonl_line(path, rec, durable=True)


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


def promotion_registry_record(lease, promotion_id, data=None, event_ts=None):
    """Build the deterministic registry projection sealed into the journal."""
    payload = dict(data or {})
    payload['promotion_id'] = promotion_id
    return {
        'schema': REGISTRY_SCHEMA,
        'ts': event_ts or utc_now(),
        'lease_id': lease.get('id'),
        'event': 'promoted',
        'kind': lease.get('kind'),
        'target': lease.get('target'),
        'state': lease.get('state'),
        'artifact_dir': lease.get('artifact_dir'),
        'data': payload,
    }


def append_promotion_registry_record(expected):
    """Durably append or re-adopt one exact promotion registry projection."""
    registry = paths()['registry']
    if os.path.exists(registry):
        raw = open(registry, 'rb').read()
        if raw and not raw.endswith(b'\n'):
            raise promotion_journal.JournalError(
                'artifact registry is not newline-terminated; refusing a '
                'possibly short/non-durable append')
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise promotion_journal.JournalError(
                'artifact registry is not valid UTF-8: %s' % exc) from exc
        for line_number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise promotion_journal.JournalError(
                    'artifact registry has malformed JSONL at line %d: %s'
                    % (line_number, exc)) from exc
            if not isinstance(row, dict):
                raise promotion_journal.JournalError(
                    'artifact registry line %d is not an object'
                    % line_number)
            if (row.get('lease_id') == expected.get('lease_id')
                    and row.get('event') == 'promoted'
                    and (row.get('data') or {}).get(
                        'promotion_id') == (
                            expected.get('data') or {}).get('promotion_id')):
                if row != expected:
                    raise promotion_journal.JournalError(
                        'artifact registry promotion identity exists with '
                        'different payload')
                # A prior append may have written every byte but failed its
                # fsync.  Retry adoption only after durability succeeds now.
                fsync_existing_path(registry)
                return False
    append_jsonl(registry, expected)
    return True


def registry_promotion_event(lease, promotion_id, data=None, event_ts=None):
    """Append exactly one promoted event for a lease/promotion pair."""
    return append_promotion_registry_record(promotion_registry_record(
        lease, promotion_id, data, event_ts))


def run_cmd(cmd, cwd=REPO, check=True, timeout=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, encoding='utf-8',
                       capture_output=True, timeout=timeout)
    if check and p.returncode:
        if p.stdout.strip():
            print(p.stdout.rstrip())
        if p.stderr.strip():
            print(p.stderr.rstrip(), file=sys.stderr)
        raise SystemExit(p.returncode)
    return p


def operation_id():
    return uuid.uuid4().hex


def remaining_operation_timeout(deadline, command):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired(command, 0)
    return remaining


def begin_operation(lease, expected_states, operation_state, operation_kind):
    if lease.get('state') not in expected_states:
        raise SystemExit('%s: cannot begin %s from lease state %r' %
                         (lease.get('id'), operation_kind, lease.get('state')))
    token = operation_id()
    lease['operation_id'] = token
    lease['operation_kind'] = operation_kind
    lease['operation_started_at'] = utc_now()
    lease['operation_previous_state'] = lease.get('state')
    lease['state'] = operation_state
    return token


def require_operation(lease, token, operation_state):
    if lease.get('state') != operation_state or lease.get('operation_id') != token:
        raise SystemExit('%s: stale %s completion refused' %
                         (lease.get('id'), operation_state))


def clear_operation(lease):
    for key in ('operation_id', 'operation_kind', 'operation_started_at',
                'operation_previous_state'):
        lease.pop(key, None)


def block_operation(lease_id, token, operation_state, exc):
    """Record an unexpected long-operation failure if its CAS token still owns the lease."""
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, lease_id)
        if lease.get('state') == operation_state and lease.get('operation_id') == token:
            if operation_state == 'auditing':
                lease.setdefault('run_attempts', []).append({
                    'run_operation_id': lease.get('run_operation_id'),
                    'run_id': lease.get('run_id'),
                    'runtime_mode': lease.get('runtime_mode'),
                    'started_at': lease.get('run_started_at'),
                    'blocked_at': utc_now(),
                    'outcome': 'blocked',
                })
                for key in ('run_operation_id', 'run_started_at', 'runtime_mode', 'runtime_limit',
                            'run_id',
                            'probe_receipt', 'pre_run_state'):
                    lease.pop(key, None)
            lease['previous_state'] = operation_state
            lease['state'] = 'blocked'
            lease['blocked_at'] = utc_now()
            lease['operation_error'] = '%s: %s' % (type(exc).__name__, exc)
            clear_operation(lease)
            save_state(state)
            registry_event(lease, 'operation_blocked', {
                'operation_state': operation_state,
                'error': lease['operation_error'],
            })


def validate_probe_receipt(receipt_path, lease_ids, run_id, now=None):
    if not receipt_path:
        raise SystemExit('staged begin-run requires --probe-receipt')
    try:
        with open(receipt_path, encoding='utf-8') as f:
            receipt = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit('probe receipt is unreadable: %s' % exc)
    if receipt.get('schema') != PROBE_RECEIPT_SCHEMA or receipt.get('go') is not True:
        raise SystemExit('probe receipt is missing successful staged evidence')
    if (receipt.get('model') != PROBE_MODEL
            or receipt.get('policy') != PROBE_POLICY):
        raise SystemExit('probe receipt model or policy mismatch')
    if not run_id or receipt.get('run_id') != run_id:
        raise SystemExit('probe receipt run ID mismatch')
    generated = parse_ts(receipt.get('generated_at'))
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if not generated:
        raise SystemExit('probe receipt timestamp is missing')
    age = (now - generated).total_seconds()
    if age < -60 or age > PROBE_RECEIPT_MAX_AGE_SECONDS:
        raise SystemExit('probe receipt is stale or future-dated')
    allowed = set(receipt.get('lease_ids') or [])
    if not set(lease_ids).issubset(allowed):
        raise SystemExit('probe receipt lease scope mismatch')
    healthy = receipt.get('healthy_profiles') or []
    latencies = receipt.get('probe_latency_ms') or {}
    if (not healthy or len(set(healthy)) != len(healthy)
            or set(healthy) != set(latencies)):
        raise SystemExit('probe receipt profile evidence is incomplete')
    if any(not isinstance(latencies.get(profile), (int, float))
           or latencies[profile] < 0
           or latencies[profile] >= PROBE_LATENCY_CEILING_MS for profile in healthy):
        raise SystemExit('probe receipt latency evidence is invalid')
    return receipt


def begin_run_leases(state, lease_ids, mode='standard', run_id=None,
                     probe_receipt=None):
    lease_ids = list(lease_ids or [])
    if not lease_ids or len(set(lease_ids)) != len(lease_ids):
        raise SystemExit('begin-run requires unique lease IDs')
    leases = [lease_by_id(state, lease_id) for lease_id in lease_ids]
    if any(lease.get('state') not in ('prepared', 'requeue_prepared') for lease in leases):
        raise SystemExit('begin-run requires prepared leases')
    running = running_translation_leases(state)
    if mode == 'standard':
        limit = TRANSLATION_LIMIT
        runtime_mode = 'standard'
    elif mode == 'staged':
        receipt = validate_probe_receipt(probe_receipt, lease_ids, run_id)
        limit = min(STAGED_TRANSLATION_LIMIT, len(receipt['healthy_profiles']))
        runtime_mode = 'staged-probed'
    else:
        raise SystemExit('unknown runtime mode: %s' % mode)
    if len(running) + len(leases) > limit:
        raise SystemExit('runtime cap reached (%d)' % limit)
    started_at = utc_now()
    for lease in leases:
        lease['pre_run_state'] = lease['state']
        lease['state'] = 'running'
        lease['run_operation_id'] = operation_id()
        lease['run_started_at'] = started_at
        lease['runtime_mode'] = runtime_mode
        lease['runtime_limit'] = limit
        lease['run_id'] = run_id
        lease['probe_receipt'] = os.path.abspath(probe_receipt) if probe_receipt else None
    state['runtime_mode'] = runtime_mode
    state['runtime_limit'] = limit
    return leases


def begin_run(args):
    with DirLock(paths()['lock']):
        state = load_state()
        for lease_id in args.lease_id:
            validate_lease_preflight(lease_by_id(state, lease_id))
        leases = begin_run_leases(
            state, args.lease_id, mode=args.mode, run_id=args.run_id,
            probe_receipt=args.probe_receipt)
        save_state(state)
        for lease in leases:
            registry_event(lease, 'run_started', {
                'run_id': lease.get('run_id'),
                'runtime_mode': lease.get('runtime_mode'),
                'run_operation_id': lease.get('run_operation_id'),
            })
    print('running=%s' % ','.join(lease['id'] for lease in leases))


def release_run(args):
    if not args.confirm_dead or not (args.reason or '').strip():
        raise SystemExit('release-run requires --confirm-dead and a non-empty --reason')
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        if lease.get('state') not in ('running', 'auditing'):
            raise SystemExit('%s: no runtime reservation to release' % lease['id'])
        attempt = {
            'run_operation_id': lease.get('run_operation_id'),
            'run_id': lease.get('run_id'),
            'runtime_mode': lease.get('runtime_mode'),
            'started_at': lease.get('run_started_at'),
            'released_at': utc_now(),
            'reason': args.reason.strip(),
        }
        lease.setdefault('run_attempts', []).append(attempt)
        lease['state'] = lease.get('pre_run_state') or 'prepared'
        for key in ('run_operation_id', 'run_started_at', 'runtime_mode', 'runtime_limit', 'run_id',
                    'probe_receipt', 'pre_run_state'):
            lease.pop(key, None)
        clear_operation(lease)
        save_state(state)
        registry_event(lease, 'run_released', attempt)
    print('lease %s -> %s' % (lease['id'], lease['state']))


def recover_operation(args):
    if not args.confirm_dead:
        raise SystemExit('recover-operation requires --confirm-dead')
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        current = lease.get('state')
        if current not in ('preparing', 'auditing'):
            raise SystemExit('%s: no recoverable operation' % lease['id'])
        if current == 'auditing':
            restored = 'running'
        else:
            restored = lease.get('operation_previous_state') or 'claimed'
        recovery = {
            'operation_id': lease.get('operation_id'),
            'operation_kind': lease.get('operation_kind'),
            'operation_started_at': lease.get('operation_started_at'),
            'recovered_at': utc_now(),
            'from_state': current,
            'to_state': restored,
        }
        lease.setdefault('operation_recoveries', []).append(recovery)
        lease['state'] = restored
        clear_operation(lease)
        save_state(state)
        registry_event(lease, 'operation_recovered', recovery)
    print('lease %s -> %s' % (lease['id'], lease['state']))


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
    # H8 (H1940): the only caller, claim(), holds the global state DirLock across this
    # call, so a hung preflight wedged EVERY coordinator operation until the lock TTL.
    # Bound it with the same PREPARE_TIMEOUT_SECONDS the other preflight call sites use
    # (:1901, :1918). subprocess.run kills and reaps the child before raising (see the
    # run_audit note at :1576), and raising here unwinds ahead of the artifact-dir
    # makedirs / leases.append / save_state below, so the DirLock is released with no
    # lease, no artifact directory and no partial state. Moving the candidate scan out
    # of the lock is the larger refactor and stays deferred.
    try:
        p = run_cmd([sys.executable, os.path.join(HERE, 'perf_preflight.py')] +
                    roots + ['--json'], check=False,
                    timeout=PREPARE_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        raise SystemExit(
            'claim: perf_preflight timed out after %ss while scanning %d candidate '
            'root(s); the preflight child was killed and no lease was created' %
            (PREPARE_TIMEOUT_SECONDS, len(roots)))
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
    leased = active_reserved_nominal_keys(state)
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
            if (key and key not in done and key not in leased
                    and not row.get('quarantined_records')
                    and os.path.exists(os.path.join(input_dir(), stem + '.raw.txt'))
                    and os.path.exists(os.path.join(input_dir(), stem + '.portrait.json'))):
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
        if (translation_lease({'kind': args.kind})
                and len(reserved_translation_leases(state)) >=
                state.get('preparation_limit', PREPARATION_LIMIT)):
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
        # H4 (H1940 Phase 2): register_prepared_lease has refused a duplicate id since it was
        # written; claim did not, so `--lease-id <existing>` appended a SECOND lease under the
        # same id. Every later lookup goes through lease_by_id, which returns the FIRST match,
        # so the second lease was unreachable-but-persisted: it consumed a preparation slot,
        # showed up in active_targets/reserved-key scans, and broke the single-id CAS
        # assumption the rest of the coordinator is built on. Placed before the artifact-dir
        # makedirs / leases.append / save_state, so a refused claim leaves no directory, no
        # lease, no saved state and no registry event -- the unwind is clean by construction
        # (the H8 pattern), and `with DirLock(...)` releases on the way out.
        #
        # This also covers the auto-generated id, not just an explicit --lease-id: make_lease_id
        # embeds a second-resolution UTC stamp AND os.getpid(), so a collision there requires
        # the same kind+lane+target within the same second from the same pid -- which is itself
        # a genuine duplicate and equally worth refusing. Two claims for the same TARGET remain
        # legal; they get distinct ids and this guard never sees them.
        if any(existing.get('id') == lease_id for existing in state.get('leases', [])):
            raise SystemExit('lease already exists: %s' % lease_id)
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
        if args.kind == 'nominal':
            lease['reserved_keys'] = list(keys)
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
        keys, key_error = _validate_reserved_keys(list(keys))
        if key_error:
            raise SystemExit('invalid nominal reservation: %s' % key_error)
        active = active_reserved_nominal_keys(state)
        target = 'nominal:%s' % keys[0]
        overlap = sorted(set(keys) & active)
        if overlap:
            sample = ','.join(overlap[:12])
            msg = 'nominal lease keys already active: %s' % sample
            # OPT-8 / H2229 — surface lease collision on the kitchen, not only stderr.
            emit_collision(
                'nominal_keys_active',
                root=lease_id,
                summary=msg,
                source='coordinator',
                data={
                    'lease_id': lease_id,
                    'overlap_count': len(overlap),
                    'overlap_sample': overlap[:20],
                })
            raise SystemExit('nominal lease keys already active: %s' % ','.join(overlap))
        run_keys = [safe_name(k) for k in keys]
        lease = {
            'id': lease_id, 'lane': lane, 'kind': 'nominal', 'owner': owner,
            'target': target, 'state': 'prepared', 'claimed_at': utc_now(),
            'prepared_at': utc_now(), 'artifact_dir': artifact_path or os.path.dirname(manifest),
            'reserved_keys': list(keys),
            'details': {'keys': keys, 'run_keys': run_keys,
                        'keymap': dict(zip(run_keys, keys))},
            'harness': os.path.abspath(harness),
            'execution_manifest': os.path.abspath(manifest),
            'origin_execution_manifest': os.path.abspath(manifest),
            'origin_execution_manifest_sha256': sha256_file(manifest),
            'preflight_path': os.path.abspath(preflight_path),
            'preflight_sha256': sha256_file(preflight_path),
            'preflight_allow_over_cost': False,
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
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            'COST-GATE: required preflight is unreadable (%s): %s'
            % (preflight_path, exc))
    if not isinstance(data, dict):
        raise SystemExit('COST-GATE: required preflight top level is not an object: %s'
                         % preflight_path)
    schema = data.get('schema')
    if schema == 'pwg.performance_preflight.v1':
        reports = [data]
    elif schema == 'pwg.performance_preflight.matrix.v1':
        reports = data.get('reports')
    else:
        raise SystemExit(
            'COST-GATE: required preflight has unsupported schema %r: %s'
            % (schema, preflight_path))
    if not isinstance(reports, list) or not reports:
        raise SystemExit('COST-GATE: required preflight has no reports: %s'
                         % preflight_path)
    for index, rep in enumerate(reports):
        if not isinstance(rep, dict):
            raise SystemExit(
                'COST-GATE: preflight report %d is not an object: %s'
                % (index, preflight_path))
        cg = rep.get('cost_gate')
        if not isinstance(cg, dict) or not isinstance(cg.get('over_ceiling'), bool):
            raise SystemExit(
                'COST-GATE: preflight report %d has no boolean cost verdict: %s'
                % (index, preflight_path))
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


def validate_lease_preflight(lease):
    """Recheck the sealed cost estimate immediately before a lease can consume runtime."""
    path = lease.get('preflight_path')
    expected = lease.get('preflight_sha256')
    if not path or not expected:
        raise SystemExit(
            '%s: prepared lease has no sealed preflight evidence; reprepare it'
            % lease.get('id'))
    try:
        actual = sha256_file(path)
    except OSError as exc:
        raise SystemExit('%s: sealed preflight is unreadable: %s'
                         % (lease.get('id'), exc))
    if actual != expected:
        raise SystemExit(
            '%s: sealed preflight hash changed (expected %s, actual %s)'
            % (lease.get('id'), expected, actual))
    enforce_cost_gate(
        path, lease.get('target'),
        allow_over_cost=bool(lease.get('preflight_allow_over_cost')))
    return path


def validate_preflight_command(args):
    lease_ids = list(args.lease_id or [])
    if not lease_ids or len(lease_ids) != len(set(lease_ids)):
        raise SystemExit('validate-preflight requires unique lease IDs')
    with DirLock(paths()['lock']):
        state = load_state()
        validated = [
            {'lease_id': lease_id,
             'preflight': validate_lease_preflight(lease_by_id(state, lease_id))}
            for lease_id in lease_ids
        ]
    print(json.dumps({
        'schema': 'pwg.coordinator.preflight_validation.v1',
        'ok': True,
        'leases': validated,
    }, ensure_ascii=False, indent=1))


def _run_child_inproc(argv, timeout=None):
    """H1386 OPT: run a prepare child (perf_preflight / gen_opt_harness2) IN-PROCESS via
    audit_window.run_py_inproc -- the H1339 runpy-gates pattern applied to the prepare
    stage, which H1339's own closeout named as the remaining dominant per-lease
    interpreter-spawn cost. Returns a CompletedProcess-shaped object; mirrors run_cmd's
    loud failure. `timeout` is accepted for signature parity but not enforceable in-proc
    -- the caller's between-children operation deadline still applies."""
    from audit_window import run_py_inproc
    # run_py_inproc takes [script, *args] -- strip the interpreter that the subprocess
    # form (run_cmd) needs but runpy must not see.
    if argv and os.path.normcase(argv[0]) == os.path.normcase(sys.executable):
        argv = argv[1:]
    res = run_py_inproc(argv)
    if res['returncode']:
        if (res['stdout'] or '').strip():
            print(res['stdout'].rstrip())
        if (res['stderr'] or '').strip():
            print(res['stderr'].rstrip(), file=sys.stderr)
        raise SystemExit(res['returncode'])
    return subprocess.CompletedProcess(argv, res['returncode'],
                                       stdout=res['stdout'], stderr=res['stderr'])


def prepare_batch(args):
    """H1386 OPT: prepare N claimed leases in ONE coordinator process, with the two
    per-lease children (perf_preflight cost gate + gen_opt_harness2 harness/manifest
    generation) run in-process -- 3 interpreter spawns per lease become 0 marginal spawns
    per lease. Per-lease semantics are IDENTICAL to `prepare` (same operation tokens,
    same cost gate, same artifacts, same state transitions), proven by the
    h1339_offline_bench deterministic output signature."""
    for lease_id in args.lease_id:
        one = argparse.Namespace(
            lease_id=lease_id, allow_over_cost=getattr(args, 'allow_over_cost', False),
            profile_slot=args.profile_slot, config_dir=args.config_dir,
            executor_lane=args.executor_lane)
        prepare(one, run_child=_run_child_inproc)


def prepare(args, run_child=None):
    run_child = run_child or run_cmd
    if bool(args.profile_slot) != bool(args.config_dir):
        raise SystemExit('--profile-slot and --config-dir must be supplied together')
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        token = begin_operation(lease, ('claimed',), 'preparing', 'prepare')
        save_state(state)
        working = copy.deepcopy(lease)
    deadline = time.monotonic() + PREPARE_TIMEOUT_SECONDS
    try:
        lease = working
        adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
        os.makedirs(adir, exist_ok=True)
        binding = []
        if args.profile_slot:
            binding = ['--profile-slot=%s' % args.profile_slot,
                       '--config-dir=%s' % os.path.abspath(args.config_dir),
                       '--execution-route=claude-cli-headless',
                       '--executor-lane=%s' % args.executor_lane,
                       '--validation-method=audit_window+final_schema']
        if lease['kind'] == 'verb':
            root = lease['target']
            preflight_path = os.path.join(adir, 'preflight.json')
            p = run_child([sys.executable, os.path.join(HERE, 'perf_preflight.py'),
                           root, '--json'],
                          timeout=remaining_operation_timeout(deadline, 'prepare'))
            atomic_write_text(preflight_path, p.stdout)
            enforce_cost_gate(preflight_path, lease.get('target'),
                              allow_over_cost=getattr(args, 'allow_over_cost', False))
            harness = os.path.join(adir, 'run_pilot_wf.%s.js' % lease['id'])
            manifest = os.path.join(adir, 'execution_manifest.%s.json' % lease['id'])
            run_child([sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'),
                       root, '--out=%s' % harness, '--manifest-out=%s' % manifest] + binding,
                      timeout=remaining_operation_timeout(deadline, 'prepare'))
        elif lease['kind'] == 'nominal':
            keys = lease.get('details', {}).get('run_keys') or lease.get('details', {}).get('keys') or []
            if not keys:
                raise SystemExit('nominal lease has no keys')
            preflight_path = os.path.join(adir, 'preflight.json')
            root = 'nominal_%s' % lease['id']
            key_arg = ','.join(keys)
            p = run_child([sys.executable, os.path.join(HERE, 'perf_preflight.py'),
                           root, '--nominal', '--no-grammar', '--keys=%s' % key_arg, '--json'],
                          timeout=remaining_operation_timeout(deadline, 'prepare'))
            atomic_write_text(preflight_path, p.stdout)
            enforce_cost_gate(preflight_path, lease.get('target'),
                              allow_over_cost=getattr(args, 'allow_over_cost', False))
            harness = os.path.join(adir, 'run_pilot_wf.%s.js' % lease['id'])
            manifest = os.path.join(adir, 'execution_manifest.%s.json' % lease['id'])
            run_child([sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'),
                       root, '--nominal', '--no-grammar', '--keys=%s' % key_arg,
                       '--out=%s' % harness, '--manifest-out=%s' % manifest] + binding,
                      timeout=remaining_operation_timeout(deadline, 'prepare'))
        else:
            raise SystemExit('prepare is only for verb/nominal translation leases')
    except BaseException as exc:
        block_operation(args.lease_id, token, 'preparing', exc)
        raise
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        require_operation(lease, token, 'preparing')
        lease['state'] = 'prepared'
        lease['prepared_at'] = utc_now()
        lease['harness'] = harness
        lease['execution_manifest'] = manifest
        lease['origin_execution_manifest'] = os.path.abspath(manifest)
        lease['origin_execution_manifest_sha256'] = sha256_file(manifest)
        lease['profile_slot'] = args.profile_slot
        lease['config_dir'] = os.path.abspath(args.config_dir) if args.config_dir else None
        lease['executor_lane'] = args.executor_lane
        lease['preflight_path'] = preflight_path
        lease['preflight_sha256'] = sha256_file(preflight_path)
        lease['preflight_allow_over_cost'] = bool(
            getattr(args, 'allow_over_cost', False))
        clear_operation(lease)
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


def seal_workflow_submission(src_path, artifact_path, expected_sha256):
    """Copy once, hash the copied bytes, and audit only that immutable submission."""
    if not expected_sha256 or not re.fullmatch(r'[0-9a-fA-F]{64}', expected_sha256):
        raise SystemExit('record-output requires a valid --result-sha256')
    expected_sha256 = expected_sha256.lower()
    os.makedirs(artifact_path, exist_ok=True)
    destination = os.path.join(
        artifact_path, 'submitted_result.%s.json' % expected_sha256[:16])
    if os.path.exists(destination):
        if sha256_file(destination) != expected_sha256:
            raise SystemExit('sealed result destination has unexpected bytes: %s'
                             % destination)
        return destination
    tmp = '%s.tmp.%s' % (destination, uuid.uuid4().hex)
    digest = hashlib.sha256()
    try:
        with open(src_path, 'rb') as source, open(tmp, 'wb') as target:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(chunk)
                target.write(chunk)
            target.flush()
            os.fsync(target.fileno())
        actual = digest.hexdigest()
        if actual != expected_sha256:
            raise SystemExit(
                'result substitution refused (expected %s, copied %s)'
                % (expected_sha256, actual))
        os.replace(tmp, destination)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    return destination


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
    # B23 (H1339): accept BOTH manifest generations -- profile-bound production prepare
    # emits v2 (execution_contract.SCHEMA_V2); v1-only here made every v2 lease's requeue
    # hydration and prepare-requeue fail on the manifest the coordinator itself prepared.
    if manifest.get('schema') not in ('pwg.headless_execution_manifest.v1',
                                      'pwg.headless_execution_manifest.v2'):
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


def ensure_origin_manifest(lease):
    path = lease.get('origin_execution_manifest')
    recorded_hash = lease.get('origin_execution_manifest_sha256')
    if not path:
        history = [row for row in (lease.get('execution_manifest_history') or [])
                   if int(row.get('attempt') or 0) == 0 and row.get('path')]
        if history:
            path = history[0]['path']
            recorded_hash = history[0].get('sha256')
        elif int(lease.get('requeue_attempt') or 0) == 0:
            path = lease.get('execution_manifest')
        else:
            raise SystemExit(
                '%s: attempted legacy lease has no verifiable origin manifest' % lease['id'])
    manifest = read_execution_manifest(path)
    actual_hash = sha256_file(path)
    if recorded_hash and actual_hash != recorded_hash:
        raise SystemExit('%s: origin execution manifest hash changed' % lease['id'])
    lease['origin_execution_manifest'] = os.path.abspath(path)
    lease['origin_execution_manifest_sha256'] = actual_hash
    return manifest


def empty_pending_requeue():
    return {'transient': [], 'defect': [], 'sources': {}, 'updated_at': utc_now()}


def pending_key_set(pending):
    pending = pending or {}
    return set(pending.get('transient') or []) | set(pending.get('defect') or [])


def report_requeue_parts(report, selected_keys):
    if 'requeue_transient' not in report or 'requeue_defect' not in report:
        raise SystemExit('audit report has no split requeue classification')
    transient = report.get('requeue_transient')
    defect = report.get('requeue_defect')
    requeue = report.get('requeue')
    if not all(isinstance(value, list) for value in (transient, defect, requeue)):
        raise SystemExit('audit requeue fields must be lists')
    for label, values in (('transient', transient), ('defect', defect), ('all', requeue)):
        if any(not isinstance(key, str) or not key for key in values):
            raise SystemExit('audit %s requeue contains an invalid key' % label)
        if len(values) != len(set(values)):
            raise SystemExit('audit %s requeue contains duplicate keys' % label)
    if set(transient) & set(defect):
        raise SystemExit('audit requeue classifications overlap')
    if Counter(transient + defect) != Counter(requeue):
        raise SystemExit('audit split requeue classifications do not equal the requeue set')
    selected = Counter(selected_keys or [])
    if any(count != 1 for count in selected.values()):
        raise SystemExit('execution manifest selected keys are not unique')
    foreign = list((Counter(requeue) - selected).elements())
    if foreign:
        raise SystemExit('audit requeue contains foreign keys: %s' % ','.join(sorted(foreign)))
    return list(transient), list(defect)


def pending_from_report(report, report_path, selected_keys):
    transient, defect = report_requeue_parts(report, selected_keys)
    report_path = os.path.abspath(report_path)
    report_hash = sha256_file(report_path)
    sources = {
        key: {'kind': kind, 'audit_report': report_path,
              'audit_report_sha256': report_hash}
        for kind, keys in (('transient', transient), ('defect', defect))
        for key in keys
    }
    return {'transient': transient, 'defect': defect, 'sources': sources,
            'updated_at': utc_now()}


def validate_pending_requeue(lease, pending, origin_manifest=None):
    pending = pending or empty_pending_requeue()
    transient = pending.get('transient')
    defect = pending.get('defect')
    sources = pending.get('sources')
    if not isinstance(transient, list) or not isinstance(defect, list) or not isinstance(sources, dict):
        raise SystemExit('%s: pending requeue structure is invalid' % lease['id'])
    for label, values in (('transient', transient), ('defect', defect)):
        if any(not isinstance(key, str) or not key for key in values):
            raise SystemExit('%s: pending %s requeue contains an invalid key' %
                             (lease['id'], label))
        if len(values) != len(set(values)):
            raise SystemExit('%s: pending %s requeue contains duplicate keys' %
                             (lease['id'], label))
    all_keys = transient + defect
    if set(transient) & set(defect):
        raise SystemExit('%s: pending requeue classifications overlap' % lease['id'])
    if set(sources) != set(all_keys):
        raise SystemExit('%s: pending requeue sources do not match keys' % lease['id'])
    origin_manifest = origin_manifest or ensure_origin_manifest(lease)
    origin_keys = origin_manifest['meta'].get('selected_keys') or []
    if any(count != 1 for count in Counter(origin_keys).values()):
        raise SystemExit('%s: origin execution manifest keys are not unique' % lease['id'])
    foreign = list((Counter(all_keys) - Counter(origin_keys)).elements())
    if foreign:
        raise SystemExit('%s: pending requeue escapes origin manifest: %s' %
                         (lease['id'], ','.join(sorted(foreign))))
    reports = {}
    for kind, keys in (('transient', transient), ('defect', defect)):
        for key in keys:
            source = sources.get(key) or {}
            if source.get('kind') != kind:
                raise SystemExit('%s: pending requeue source kind drift for %s' %
                                 (lease['id'], key))
            path = source.get('audit_report')
            expected_hash = source.get('audit_report_sha256')
            if not path or not expected_hash:
                raise SystemExit('%s: pending requeue source is incomplete for %s' %
                                 (lease['id'], key))
            if path not in reports:
                try:
                    with open(path, encoding='utf-8') as f:
                        report = json.load(f)
                except (OSError, json.JSONDecodeError) as e:
                    raise SystemExit('%s: pending audit report is unreadable: %s' %
                                     (lease['id'], e))
                if sha256_file(path) != expected_hash:
                    raise SystemExit('%s: pending audit report hash changed' % lease['id'])
                report_requeue_parts(report, report.get('keys') or [])
                reports[path] = report
            if key not in (reports[path].get('requeue_%s' % kind) or []):
                raise SystemExit('%s: pending key %s is not bound to its source audit' %
                                 (lease['id'], key))
    return pending


def pending_without_kind(pending, selected_kind):
    remaining = empty_pending_requeue()
    keep_kind = 'defect' if selected_kind == 'transient' else 'transient'
    remaining[keep_kind] = list(pending.get(keep_kind) or [])
    remaining['sources'] = {
        key: dict((pending.get('sources') or {})[key]) for key in remaining[keep_kind]
    }
    return remaining


def merge_pending_requeue(lease, carried, latest, origin_manifest):
    carried = validate_pending_requeue(lease, carried, origin_manifest)
    latest = validate_pending_requeue(lease, latest, origin_manifest)
    if pending_key_set(carried) & pending_key_set(latest):
        raise SystemExit('%s: carried and current requeue keys overlap' % lease['id'])
    merged = empty_pending_requeue()
    for kind in ('transient', 'defect'):
        merged[kind] = sorted((carried.get(kind) or []) + (latest.get(kind) or []))
    merged['sources'] = dict(carried.get('sources') or {})
    merged['sources'].update(latest.get('sources') or {})
    return validate_pending_requeue(lease, merged, origin_manifest)


ATTEMPT_DIR_RE = re.compile(r'^rq([0-9]+)-(transient|defect)$')


def next_requeue_attempt(lease, artifact_path):
    root = os.path.join(artifact_path, 'requeue')
    found = []
    if os.path.isdir(root):
        for name in os.listdir(root):
            match = ATTEMPT_DIR_RE.match(name)
            path = os.path.abspath(os.path.join(root, name))
            if match and os.path.isdir(path):
                found.append((int(match.group(1)), match.group(2), path))
    referenced = {
        os.path.abspath(row.get('artifact_dir'))
        for row in (lease.get('execution_manifest_history') or []) if row.get('artifact_dir')
    }
    current = (lease.get('current_attempt') or {}).get('artifact_dir')
    if current:
        referenced.add(os.path.abspath(current))
    orphans = [
        {'number': number, 'kind': kind, 'artifact_dir': path,
         'discovered_at': utc_now(), 'reason': 'unreferenced_attempt_directory'}
        for number, kind, path in found if path not in referenced
    ]
    recorded = [int(row.get('attempt') or 0)
                for row in (lease.get('execution_manifest_history') or [])]
    highest = max([int(lease.get('requeue_attempt') or 0)] + recorded +
                  [number for number, _kind, _path in found])
    return highest + 1, orphans


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


def recorded_lease_state(state_name, audit_errors, clean_rows, pending=None):
    if state_name not in PROMOTABLE_AUDIT_EXITS:
        return state_name, False
    if audit_errors:
        return 'blocked', False
    if pending is None:
        if clean_rows:
            return ('ready' if state_name == 'clean' else 'ready_partial'), True
        if state_name in ('needs_requeue', 'transient_only'):
            return state_name, False
        return 'blocked', False
    has_pending = bool(pending_key_set(pending))
    if clean_rows:
        return ('ready_partial' if has_pending else 'ready'), True
    if pending.get('defect'):
        return 'needs_requeue', False
    if pending.get('transient'):
        return 'transient_only', False
    return 'blocked', False


def run_audit(argv, timeout=AUDIT_TIMEOUT_SECONDS):
    """Run audit_window in a KILLABLE SUBPROCESS under the audit timeout.

    H1957 correction of H1811 S1, which ran audit_window in-process (runpy via
    audit_window.run_py_inproc) on a daemon worker thread. That broke
    run_py_inproc's OWN documented contract -- "callers must not run two of these
    concurrently (sys.argv/stdout are process-global)" -- because on timeout the
    worker was left running alongside the caller. Three consequences, none of them
    covered by the deterministic gates:

      1. The abandoned thread keeps executing audit code that WRITES the very
         window_status.json / audit_window.report.json / requeue files the caller
         reads immediately after receiving rc=124.
      2. While it runs, the coordinator's own sys.argv, cwd (run_py_inproc chdirs
         to SRC) and stdout/stderr remain hijacked -- so coordinator output goes
         into a dead capture buffer and relative paths resolve against the wrong
         directory.
      3. run_py_inproc's `finally` restores argv/cwd whenever the thread finally
         ends, clobbering whatever the main thread had set in the meantime.

    A separate process is the only boundary where the timeout can actually cancel
    the work: subprocess.run kills the child, so nothing survives to race the
    caller. The cost is one interpreter spawn per lease.

    H1811 S2 is deliberately RETAINED -- _pilot_collect still runs in-process
    INSIDE audit_window -- so this restores one spawn, not the five H1339 removed.

    Semantics preserved from the in-proc form: a crash still surfaces the child's
    own returncode + stderr (the fail-loud path of H169 defect 2), and a timeout
    is still reported as rc=124 (the conventional timeout code) rather than raising
    TimeoutExpired, so process_record_output's H5 corrupt-status handling -- which
    keys on rc not in {0, 1} -- is unchanged.

    This function remains the ONE audit seam: tests substitute it (never run_cmd)
    to fixture the audit step."""
    import types

    def _text(chunk):
        if chunk is None:
            return ''
        if isinstance(chunk, bytes):
            return chunk.decode('utf-8', 'replace')
        return chunk

    cmd = [sys.executable] + list(argv)
    try:
        p = subprocess.run(cmd, cwd=REPO, text=True, encoding='utf-8',
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        # subprocess.run has already killed the child and reaped it before raising.
        return types.SimpleNamespace(
            returncode=124,
            stdout=_text(exc.stdout),
            stderr=(_text(exc.stderr) +
                    'run_audit: audit_window timed out after %ss; the child process '
                    'was killed, so no audit output can still be written.\n' % timeout))
    return types.SimpleNamespace(returncode=p.returncode, stdout=p.stdout,
                                 stderr=p.stderr)


def process_record_output(lease, args):
    """Normalize and audit a detached lease snapshot without holding the state lock."""
    base_adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
    adir = lease.get('current_artifact_dir') or base_adir
    os.makedirs(adir, exist_ok=True)
    wf = os.path.join(adir, 'wf_output.%s.json' % lease['id'])
    result = normalize_workflow_result(args.workflow_result, wf)
    if lease.get('kind') == 'nominal':
        result.setdefault('meta', {})['nominal_keymap'] = lease.get('details', {}).get('keymap') or {}
        atomic_write_json(wf, result, indent=None)
    argv = [os.path.join(HERE, 'audit_window.py'), wf,
            '--write-requeue', '--out-dir', adir]
    manifest = lease.get('execution_manifest') or os.path.join(
        adir, '__missing_execution_manifest__.json')
    argv += ['--execution-manifest', manifest]
    if lease.get('kind') == 'verb':
        argv += ['--root', lease['target']]
    if args.allow_stale:
        argv.append('--allow-stale')
    audit = run_audit(argv)
    status_path = os.path.join(adir, 'window_status.json')
    report_path = os.path.join(adir, 'audit_window.report.json')
    status_corrupt = report_corrupt = False
    try:
        status = json.load(open(status_path, encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        status = {}
        status_corrupt = True
    try:
        report = json.load(open(report_path, encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        report = {}
        report_corrupt = True
    state_name = status.get('state') or ('blocked' if audit.returncode not in (0, 1) else 'unknown')
    rejected = set(report.get('requeue') or status.get('requeue_keys') or [])
    clean_payload = clean_result_payload(result, rejected)
    clean_rows = clean_payload['results']
    audit_errors = validate_promotable_audit(
        wf, status, report, state_name, audit.returncode)
    # H1811 H5: a truncated/missing status or report with a clean-looking rc used to
    # record a meaningless 'unknown' state silently -- surface it as an audit error.
    if audit.returncode in (0, 1):
        if status_corrupt:
            audit_errors.append('window_status.json unreadable despite audit rc=%d'
                                % audit.returncode)
        if report_corrupt:
            audit_errors.append('audit_window.report.json unreadable despite audit rc=%d'
                                % audit.returncode)
    pending = lease.get('pending_requeue') or empty_pending_requeue()
    if not audit_errors:
        try:
            origin_manifest = ensure_origin_manifest(lease)
            current_manifest = read_execution_manifest(manifest)
            latest_pending = pending_from_report(
                report, report_path, current_manifest['meta'].get('selected_keys') or [])
            carried = ((lease.get('current_attempt') or {}).get('remaining_pending') or
                       empty_pending_requeue())
            if pending_key_set(carried) & set(
                    current_manifest['meta'].get('selected_keys') or []):
                raise SystemExit('%s: carried requeue overlaps the current attempt' % lease['id'])
            pending = merge_pending_requeue(
                lease, carried, latest_pending, origin_manifest)
            lease['pending_requeue'] = pending
        except SystemExit as exc:
            audit_errors.append(str(exc))
    lease_state, promotable = recorded_lease_state(
        state_name, audit_errors, clean_rows, pending)
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
    if lease.get('current_attempt'):
        lease['current_attempt']['audit_report'] = report_path
        lease['current_attempt']['audit_report_sha256'] = (
            sha256_file(report_path) if os.path.exists(report_path) else None)
        lease['current_attempt']['recorded_at'] = lease['recorded_at']
    return audit, manifest, adir, pending


def record_output(args):
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        token = begin_operation(lease, ('running',), 'auditing', 'record-output')
        # P11 (H1420): record-output gates only on state=='running', so after a run is
        # released/recovered and the lease re-run, a STALE workflow_result from the prior run would
        # be recorded against the NEW run (silent misattribution -> a zombie run's output promoted).
        # When the operator carries the run identity (--run-id, sealed at begin-run), require it
        # match the running lease's run_id; a mismatch is a stale/zombie submission -> refuse before
        # any state is persisted. Raising here discards begin_operation's in-memory mutation (state
        # is not saved yet), leaving the on-disk lease 'running' for a correct retry.
        supplied_run_id = getattr(args, 'run_id', None)
        expected_run_id = lease.get('run_id')
        if expected_run_id and supplied_run_id is None:
            raise SystemExit(
                '%s: record-output --run-id is required for running lease run-id %r '
                '(unbound result submission refused)' % (args.lease_id, expected_run_id))
        if supplied_run_id is not None and supplied_run_id != lease.get('run_id'):
            raise SystemExit(
                '%s: record-output --run-id %r does not match the running lease run-id %r '
                '(stale/zombie run submission refused)' %
                (args.lease_id, supplied_run_id, lease.get('run_id')))
        supplied_result_sha256 = getattr(args, 'result_sha256', None)
        if expected_run_id and supplied_result_sha256 is None:
            raise SystemExit(
                '%s: record-output --result-sha256 is required for a sealed run '
                '(unbound result bytes refused)' % args.lease_id)
        processing_args = copy.copy(args)
        if supplied_result_sha256 is not None:
            result_artifact_dir = (
                lease.get('current_artifact_dir')
                or lease.get('artifact_dir')
                or artifact_dir(args.lease_id))
            sealed_result = seal_workflow_submission(
                args.workflow_result, result_artifact_dir, supplied_result_sha256)
            processing_args.workflow_result = sealed_result
            lease['submitted_result_path'] = sealed_result
            lease['submitted_result_sha256'] = supplied_result_sha256.lower()
        save_state(state)
        working = copy.deepcopy(lease)
    try:
        audit, manifest, adir, pending = process_record_output(working, processing_args)
    except BaseException as exc:
        block_operation(args.lease_id, token, 'auditing', exc)
        raise
    with DirLock(paths()['lock']):
        state = load_state()
        lease = lease_by_id(state, args.lease_id)
        require_operation(lease, token, 'auditing')
        completed_attempt = {
            'run_operation_id': working.get('run_operation_id'),
            'run_id': working.get('run_id'),
            'runtime_mode': working.get('runtime_mode'),
            'started_at': working.get('run_started_at'),
            'recorded_at': working.get('recorded_at'),
            'outcome': working.get('state'),
        }
        working.setdefault('run_attempts', []).append(completed_attempt)
        for key in ('run_operation_id', 'run_started_at', 'runtime_mode', 'runtime_limit',
                    'run_id', 'probe_receipt', 'pre_run_state'):
            working.pop(key, None)
        clear_operation(working)
        lease.clear()
        lease.update(working)
        save_state(state)
        registry_event(lease, 'recorded', {
            'wf_output': lease['wf_output'],
            'execution_manifest': manifest,
            'artifact_dir': adir,
            'status': lease['audit_state'],
            'audit_returncode': audit.returncode,
            'pending_requeue': {
                'transient': list((pending or {}).get('transient') or []),
                'defect': list((pending or {}).get('defect') or []),
            },
            'cost': lease.get('cost'),
        })
    if audit.stdout.strip():
        print(audit.stdout.rstrip())
    if audit.stderr.strip():
        print(audit.stderr.rstrip(), file=sys.stderr)
    print('lease %s -> %s' % (lease['id'], lease['state']))


RECORD_BATCH_SCHEMA = 'pwg.record_output_batch.v1'


def _record_batch_progress(recorded, records, failed=None):
    payload = {
        'schema': RECORD_BATCH_SCHEMA,
        'recorded': list(recorded),
        'remaining': [row[0] for row in records[len(recorded):]],
        'failed': failed,
    }
    print('RECORD_OUTPUT_BATCH_PROGRESS: ' +
          json.dumps(payload, ensure_ascii=False, separators=(',', ':')))


def record_output_batch(args):
    """Record N completed leases in one coordinator parent process.

    Each item still executes the existing :func:`record_output` unit with its own operation token,
    locks, isolated ``audit_window`` child/timeout, report, and state commit. The batch is
    deliberately sequential and fail-fast: earlier commits remain durable, the failing item and
    later leases remain retryable. A machine-readable progress line after every commit (and on
    failure) lets the outer SQLite scheduler mark exactly the completed prefix.
    """
    records = [tuple(row) for row in (getattr(args, 'record', None) or [])]
    if not records:
        raise SystemExit(
            'record-output-batch requires at least one '
            '--record LEASE RESULT RUN_ID RESULT_SHA256')
    lease_ids = [row[0] for row in records]
    if len(lease_ids) != len(set(lease_ids)):
        raise SystemExit('record-output-batch refuses duplicate lease ids')
    recorded = []
    for lease_id, workflow_result, run_id, result_sha256 in records:
        one = argparse.Namespace(
            lease_id=lease_id,
            workflow_result=workflow_result,
            transcript_dir=None,
            allow_stale=getattr(args, 'allow_stale', False),
            run_id=None if run_id == '-' else run_id,
            result_sha256=None if result_sha256 == '-' else result_sha256,
        )
        try:
            record_output(one)
        except BaseException as exc:
            _record_batch_progress(
                recorded, records,
                failed={'lease_id': lease_id, 'type': type(exc).__name__, 'message': str(exc)})
            raise
        recorded.append(lease_id)
        _record_batch_progress(recorded, records)


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
        token = begin_operation(lease, allowed, 'preparing', 'prepare-requeue')
        save_state(state)
        lease = copy.deepcopy(lease)
    try:
        adir = lease.get('artifact_dir') or artifact_dir(args.lease_id)
        which = 'transient' if args.transient else 'defect'
        origin_manifest = ensure_origin_manifest(lease)
        current_manifest_path = lease.get('execution_manifest')
        current_manifest = read_execution_manifest(current_manifest_path)
        current_meta = current_manifest['meta']
        root = current_meta.get('root')
        if not root:
            raise SystemExit('%s: execution manifest has no root' % lease['id'])
        nominal = bool(current_meta.get('nominal'))

        pending = lease.get('pending_requeue')
        if not pending:
            if int(lease.get('requeue_attempt') or 0):
                raise SystemExit(
                    '%s: attempted legacy lease has no provenance-bound pending backlog' %
                    lease['id'])
            try:
                status = json.load(open(lease['status_path'], encoding='utf-8'))
                report = json.load(open(lease['audit_report'], encoding='utf-8'))
            except (KeyError, OSError, json.JSONDecodeError) as e:
                raise SystemExit('%s: cannot hydrate pending requeue: %s' % (lease['id'], e))
            errors = validate_promotable_audit(
                lease['wf_output'], status, report, lease.get('audit_state'),
                lease.get('audit_returncode'))
            if errors:
                raise SystemExit('%s: cannot hydrate pending requeue: %s' %
                                 (lease['id'], '; '.join(errors)))
            pending = pending_from_report(
                report, lease['audit_report'], current_meta.get('selected_keys') or [])
            lease['pending_requeue'] = pending
        pending = validate_pending_requeue(lease, pending, origin_manifest)
        requeue_keys = list(pending.get(which) or [])
        if not requeue_keys:
            raise SystemExit('%s: pending %s requeue is empty' % (lease['id'], which))
        remaining_pending = pending_without_kind(pending, which)

        attempt, orphans = next_requeue_attempt(lease, adir)
        attempt_tag = 'rq%02d-%s' % (attempt, which)
        attempt_dir = os.path.join(adir, 'requeue', attempt_tag)
        harness = os.path.join(attempt_dir, 'run_pilot_wf.%s.%s.js' %
                               (lease['id'], attempt_tag))
        manifest = os.path.join(attempt_dir, 'execution_manifest.%s.%s.json' %
                                (lease['id'], attempt_tag))
        rq = os.path.join(attempt_dir, 'requeue.%s.keys.txt' % which)
        old_manifest_sha256 = sha256_file(current_manifest_path)
        cmd = [sys.executable, os.path.join(HERE, 'requeue_from_audit.py'),
               root, '--%s' % which, '--requeue-file=%s' % rq, '--out=%s' % harness,
               '--manifest-out=%s' % manifest]
        if lease.get('profile_slot') and lease.get('config_dir'):
            cmd += ['--profile-slot=%s' % lease['profile_slot'],
                    '--config-dir=%s' % lease['config_dir'],
                    '--executor-lane=%s' % (lease.get('executor_lane') or 'serial-whole-card')]
        if nominal:
            cmd += ['--nominal', '--no-grammar']
        created = False
        try:
            os.makedirs(attempt_dir, exist_ok=False)
            created = True
            atomic_write_text(rq, '\n'.join(requeue_keys) + '\n')
            preflight_path = os.path.join(attempt_dir, 'preflight.json')
            preflight_cmd = [
                sys.executable, os.path.join(HERE, 'perf_preflight.py'),
                ('nominal_%s' % lease['id']) if nominal else root,
                '--keys=%s' % ','.join(requeue_keys), '--json',
            ]
            if nominal:
                preflight_cmd += ['--nominal', '--no-grammar']
            preflight = run_cmd(preflight_cmd, timeout=PREPARE_TIMEOUT_SECONDS)
            atomic_write_text(preflight_path, preflight.stdout)
            enforce_cost_gate(
                preflight_path, lease.get('target'),
                allow_over_cost=bool(lease.get('preflight_allow_over_cost')))
            if which == 'defect':
                fshas = set()
                source_paths = {
                    pending['sources'][key]['audit_report'] for key in requeue_keys
                }
                for source_path in source_paths:
                    with open(source_path, encoding='utf-8') as f:
                        source_report = json.load(f)
                    fshas.update(source_report.get('requeue_defect_fshas') or [])
                atomic_write_text(
                    os.path.join(attempt_dir, 'requeue.defect.fshas.txt'),
                    '\n'.join(sorted(fshas)) + ('\n' if fshas else ''))
            p = run_cmd(cmd, timeout=PREPARE_TIMEOUT_SECONDS)
            if sha256_file(current_manifest_path) != old_manifest_sha256:
                raise SystemExit(
                    '%s: previous execution manifest changed during requeue preparation' %
                    lease['id'])
            prepared_manifest = read_execution_manifest(manifest)
            if (prepared_manifest['meta'].get('selected_keys') or []) != requeue_keys:
                raise SystemExit('%s: requeue execution manifest key drift' % lease['id'])
        except BaseException:
            if created:
                shutil.rmtree(attempt_dir, ignore_errors=True)
            raise
        history = lease.setdefault('execution_manifest_history', [])
        origin_path = lease['origin_execution_manifest']
        origin_abs = os.path.abspath(origin_path)
        if not any(os.path.abspath(row.get('path') or '') == origin_abs for row in history):
            history.append(manifest_history_entry(
                origin_path, 0, 'initial', adir,
                lease.get('prepared_at') or lease.get('recorded_at')))
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
        lease['preflight_path'] = preflight_path
        lease['preflight_sha256'] = sha256_file(preflight_path)
        lease['current_artifact_dir'] = attempt_dir
        known_orphans = {
            os.path.abspath(row.get('artifact_dir'))
            for row in (lease.get('orphaned_requeue_attempts') or [])
            if row.get('artifact_dir')
        }
        lease.setdefault('orphaned_requeue_attempts', []).extend(
            row for row in orphans if os.path.abspath(row['artifact_dir']) not in known_orphans)
        lease['current_attempt'] = {
            'number': attempt,
            'kind': which,
            'artifact_dir': attempt_dir,
            'harness': harness,
            'execution_manifest': manifest,
            'preflight': preflight_path,
            'preflight_sha256': lease['preflight_sha256'],
            'prepared_at': prepared_at,
            'selected_keys': requeue_keys,
            'remaining_pending': remaining_pending,
        }
    except BaseException as exc:
        block_operation(args.lease_id, token, 'preparing', exc)
        raise
    with DirLock(paths()['lock']):
        state = load_state()
        fresh = lease_by_id(state, args.lease_id)
        require_operation(fresh, token, 'preparing')
        clear_operation(lease)
        fresh.clear()
        fresh.update(lease)
        save_state(state)
        registry_event(fresh, 'requeue_prepared', {
            'attempt': attempt, 'artifact_dir': attempt_dir,
            'harness': harness, 'manifest': manifest, 'kind': which,
            'selected_keys': requeue_keys,
        })
    if p.stdout.strip():
        print(p.stdout.rstrip())
    print('harness: %s' % harness)


def completed_run_binding(lease):
    """Return the durable run/attempt identity that produced a recorded lease.

    ``record-output`` releases the live runtime reservation, so the current
    ``run_id`` is deliberately removed from the lease.  The completed attempt is
    the immutable source of promotion attribution.
    """
    attempts = lease.get('run_attempts') or []
    if not attempts:
        return {'run_id': None, 'attempt_id': None}
    attempt = attempts[-1]
    return {
        'run_id': attempt.get('run_id'),
        'attempt_id': attempt.get('run_operation_id'),
    }


def promotion_identity(ready, model_identifier):
    """Content-address one exact promotion intent for stable crash retries."""
    intent = {
        'schema': 'pwg.coordinator.promotion_intent.v1',
        'model_identifier': model_identifier,
        'review_status': 'ai_translated',
        'leases': [{
            'lease_id': lease['id'],
            'run': completed_run_binding(lease),
            'clean_output_sha256': lease.get('clean_output_sha256'),
        } for lease in sorted(ready, key=lambda row: row['id'])],
    }
    payload = json.dumps(
        intent, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode('utf-8')
    return 'pwg-prom-' + hashlib.sha256(payload).hexdigest()[:24]


def journal_paths(promotion_id):
    base = os.path.join(paths()['promotions'], promotion_id)
    return {
        'journal': base + '.journal.json',
        'manifest': base + '.manifest.json',
        'report': base + '.report.json',
    }


def batch_from_journal(journal):
    """Reconstruct the exact clean-output bundle sealed in a journal."""
    batch = []
    for lease_id in journal['lease_ids']:
        metrics = journal['leases'][lease_id]
        files = (metrics.get('clean_output') or {}).get('files') or []
        if len(files) != 1 or not files[0].get('path'):
            raise promotion_journal.JournalError(
                '%s: coordinator recovery requires exactly one sealed clean output'
                % lease_id)
        binding = journal['bindings'][lease_id]
        batch.append({
            'lease_id': lease_id,
            'run_id': binding.get('run_id'),
            'attempt_id': binding.get('attempt_id'),
            'glob': files[0]['path'],
            'expected_subcards': list(metrics['subcard_keys']),
        })
    return batch


def build_promotion_derived(journal_path, store_claim_held=False):
    """Build, validate, and seal the store-derived RU artifacts idempotently."""
    journal = promotion_journal.load(journal_path)
    if journal['phase'] != 'store_committed':
        return journal
    if not store_claim_held:
        with promote_final_cards.PromoteClaim(journal['store']['path']):
            return build_promotion_derived(
                journal_path, store_claim_held=True)
    promotion_journal.reconcile(
        journal_path, adopt_after=False, store_claim_held=True)
    store = journal['store']['path']
    clean_files = [
        row['path']
        for lease_id in journal['lease_ids']
        for row in journal['leases'][lease_id]['clean_output']['files']
    ]
    card_path, _count, _skipped = translation_memory.build(
        store, 'ru', journal_path=journal_path)
    frag_path, _added, _total = translation_memory.build_frags(
        clean_files, 'ru', journal_path=journal_path)
    try:
        best, conflicts, null_keys = promote_final_cards.collect_cards(clean_files)
        if conflicts or null_keys or sorted(best) != sorted(
                key for lease_id in journal['lease_ids']
                for key in journal['leases'][lease_id]['subcard_keys']):
            raise promotion_journal.JournalError(
                'clean-output membership changed before denylist unblock')
        cleared_addr, cleared_frag = promote_final_cards.clear_denials_for_promotion(
            best, timestamp=journal['artifact_timestamp'])
        if cleared_addr or cleared_frag:
            print('TM denylist: cleared %d card address(es) + %d fragment sha(s)'
                  % (len(cleared_addr), len(cleared_frag)))
    except Exception as exc:
        promotion_journal.record_derived_observation(
            journal_path, 'denylist',
            artifact_path=translation_memory.denylist_path(),
            error=str(exc))
        raise
    promotion_journal.record_derived_observation(
        journal_path, 'denylist',
        artifact_path=translation_memory.denylist_path(),
        error=None)
    return promotion_journal.mark_derived_validated(
        journal_path,
        denylist_path=translation_memory.denylist_path(),
        card_tm_path=card_path,
        fragment_tm_path=frag_path,
    )


def apply_journal_outcomes(state, journal):
    """Apply one journal's complete lease metrics to an in-memory state."""
    intent = (journal.get('coordinator') or {}).get('intent') or {}
    sealed_outcomes = intent.get('lease_outcomes')
    outcomes = {}
    promoted_at = journal['artifact_timestamp']
    report = journal['report']
    store_before = report['store_rows_before']
    store_after = report['store_rows_after']
    for lease_id in journal['lease_ids']:
        lease = lease_by_id(state, lease_id)
        if sealed_outcomes:
            outcome = sealed_outcomes[lease_id]
        elif lease.get('promotion_id') == journal['promotion_id']:
            outcome = lease.get('state')
        elif lease.get('state') == 'ready_partial':
            outcome = 'promoted_partial'
        elif lease.get('state') == 'ready':
            outcome = 'promoted'
        else:
            raise promotion_journal.JournalError(
                '%s: coordinator lease is %r, expected ready/ready_partial or '
                'this promotion marker' % (lease_id, lease.get('state')))
        if outcome not in ('promoted', 'promoted_partial'):
            raise promotion_journal.JournalError(
                '%s: invalid sealed promotion outcome %r' % (lease_id, outcome))
        per = journal['leases'][lease_id]
        lease.update({
            'state': outcome,
            'promoted_at': promoted_at,
            'promotion_id': journal['promotion_id'],
            'promotion_journal': os.path.abspath(
                journal_paths(journal['promotion_id'])['journal']),
            'model_version': journal['model_identifier'],
            'store_before': store_before,
            'store_after': store_after,
            'store_delta': per['store_delta'],
            'bundle_store_delta': store_after - store_before,
            'promoted_subcards': per['subcards'],
            'promoted_rows': per['rows'],
            'rows_added': per['rows_added'],
            'rows_replaced': per['rows_replaced'],
        })
        outcomes[lease_id] = outcome
    state['last_promotion'] = {
        'promotion_id': journal['promotion_id'],
        'journal': os.path.abspath(
            journal_paths(journal['promotion_id'])['journal']),
        'lease_outcomes': outcomes,
        'model_identifier': journal['model_identifier'],
        'store_sha256': journal['store']['expected_after_sha256'],
        'committed_at': promoted_at,
    }
    # A fixed journal timestamp makes a retry reconstruct byte-identical state.
    state['updated_at'] = promoted_at
    return outcomes


def promotion_registry_rows(state, journal, journal_path):
    """Return the exact per-lease registry projection for one promotion."""
    rows = []
    for lease_id in journal['lease_ids']:
        lease = lease_by_id(state, lease_id)
        per = journal['leases'][lease_id]
        rows.append(promotion_registry_record(
            lease, journal['promotion_id'], {
                'glob': ((per.get('clean_output') or {}).get(
                    'files') or [{}])[0].get('path'),
                'journal': os.path.abspath(journal_path),
                'store_before': journal['report']['store_rows_before'],
                'store_after': journal['report']['store_rows_after'],
                'store_delta': per['store_delta'],
                'bundle_store_delta': (
                    journal['report']['store_rows_after']
                    - journal['report']['store_rows_before']),
                'rows_added': per['rows_added'],
                'rows_replaced': per['rows_replaced'],
                'batch_subcards': per['subcards'],
                'batch_rows': per['rows'],
            }, event_ts=journal['artifact_timestamp']))
    return rows


def commit_journal_coordinator(journal_path, store_claim_held=False):
    """Seal/commit every lease update in one coordinator-state replacement."""
    journal = promotion_journal.load(journal_path)
    if journal['phase'] == 'complete':
        return journal
    if not store_claim_held:
        with promote_final_cards.PromoteClaim(journal['store']['path']):
            return commit_journal_coordinator(
                journal_path, store_claim_held=True)
    if journal['phase'] not in ('derived_validated', 'coordinator_committed'):
        raise promotion_journal.JournalError(
            'coordinator commit requires derived_validated, got %s'
            % journal['phase'])
    promotion_journal.reconcile(
        journal_path, adopt_after=False, store_claim_held=True)
    with DirLock(paths()['lock']):
        state_path = paths()['state']
        state = load_state()
        outcomes = apply_journal_outcomes(state, journal)
        expected_state_bytes = promotion_journal.stable_json_bytes(state)
        registry_rows = promotion_registry_rows(state, journal, journal_path)
        if journal['phase'] == 'derived_validated':
            promotion_journal.prepare_coordinator_commit(
                journal_path,
                state_path=state_path,
                expected_state_bytes=expected_state_bytes,
                lease_outcomes=outcomes,
                promotion_marker=journal['promotion_id'],
                registry_path=paths()['registry'],
                registry_events=registry_rows,
                store_claim_held=True,
            )
            journal = promotion_journal.load(journal_path)
            reconciled = promotion_journal.reconcile_coordinator(
                journal_path, adopt_after=False, store_claim_held=True)
            if reconciled['action'] == 'adopt_coordinator_commit':
                promotion_journal.reconcile_coordinator(
                    journal_path, adopt_after=True, store_claim_held=True)
            elif reconciled['action'] == 'write_coordinator_state':
                promotion_journal.commit_coordinator_state(
                    journal_path, expected_state_bytes,
                    store_claim_held=True)
            elif reconciled['action'] != 'already_coordinator_committed':
                raise promotion_journal.JournalError(
                    'unexpected coordinator reconciliation action %r'
                    % reconciled['action'])
        else:
            promotion_journal.reconcile_coordinator(
                journal_path, adopt_after=False, store_claim_held=True)
        # Dashboard and registry are replayable projections.  Registry events are
        # deduplicated by promotion ID, so a crash at any line below converges.
        write_dashboard(state)
        sealed_registry = (
            promotion_journal.load(journal_path)['coordinator']['intent']['registry'])
        for expected in sealed_registry['events']:
            append_promotion_registry_record(expected)
        return promotion_journal.mark_complete(
            journal_path, store_claim_held=True)


def finish_promotion_journal(journal_path, store_claim_held=False):
    """Drive one incomplete journal forward while holding the canonical-store claim."""
    journal = promotion_journal.load(journal_path)
    if journal['phase'] == 'complete':
        return journal
    if not store_claim_held:
        # The store hash checks and the coordinator/journal replacements are one
        # transaction boundary.  Releasing the writer claim after only the store
        # replace permits a second canonical writer to land between verification
        # and COMPLETE.
        with promote_final_cards.PromoteClaim(journal['store']['path']):
            return finish_promotion_journal(
                journal_path, store_claim_held=True)
    if journal['phase'] in ('prepared', 'store_committed'):
        batch = batch_from_journal(journal)
        promote_final_cards.batch_promote(
            batch,
            journal['store']['path'],
            journal['review_status'],
            journal['model_identifier'],
            report_path=journal['report'].get('report_path'),
            journal_path=journal_path,
            promotion_id=journal['promotion_id'],
            store_claim_held=True,
        )
        journal = promotion_journal.load(journal_path)
    if journal['phase'] == 'store_committed':
        journal = build_promotion_derived(
            journal_path, store_claim_held=True)
    if journal['phase'] in ('derived_validated', 'coordinator_committed'):
        journal = commit_journal_coordinator(
            journal_path, store_claim_held=True)
    if journal['phase'] != 'complete':
        raise promotion_journal.JournalError(
            'promotion recovery stopped unexpectedly at %s' % journal['phase'])
    return journal


def reconcile_promotion_journals():
    """Automatically converge the single active promotion before any command."""
    promotion_dir = paths()['promotions']
    os.makedirs(promotion_dir, exist_ok=True)
    active = []
    for journal_path in sorted(glob.glob(os.path.join(
            promotion_dir, '*.journal.json'))):
        journal = promotion_journal.load(journal_path)
        if journal['phase'] != 'complete':
            active.append(journal_path)
    if len(active) > 1:
        raise promotion_journal.JournalError(
            'multiple incomplete promotion journals require manual ordering: %s'
            % ', '.join(active))
    if active:
        with DirLock(paths()['promotion_lock']):
            finish_promotion_journal(active[0])


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
        # H1339 Phase 3: validate every lease first (identical checks), then promote the
        # WHOLE bundle in ONE store transaction (promote_final_cards --batch-manifest):
        # one claim, one full-store read, one better-attempt merge, one backup, one atomic
        # replacement -- instead of a full store read/copy/rewrite + interpreter startup
        # PER LEASE. All-or-nothing: any diverging lease fails the bundle with the store
        # byte-identical; per-lease attribution comes back in the batch report.
        batch = []
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
            pending = lease.get('pending_requeue') or empty_pending_requeue()
            try:
                origin_manifest = ensure_origin_manifest(lease)
                pending = validate_pending_requeue(lease, pending, origin_manifest)
            except SystemExit as e:
                errors.append(str(e))
            has_pending = bool(pending_key_set(pending))
            expected_lease_state = 'ready_partial' if has_pending else 'ready'
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
            binding = completed_run_binding(lease)
            batch.append({
                'lease_id': lease['id'],
                'run_id': binding['run_id'],
                'attempt_id': binding['attempt_id'],
                'glob': os.path.abspath(source),
                'expected_subcards': sorted({row.get('key') for row in clean_rows}),
            })
        promotion_id = promotion_identity(ready, args.gen_model_version)
        promotion_files = journal_paths(promotion_id)
        batch_manifest = promotion_files['manifest']
        batch_report = promotion_files['report']
        journal_path = promotion_files['journal']
        atomic_write_json(batch_manifest, batch, indent=1)
        # Hold the same canonical-store claim from PREPARED through COMPLETE.
        # All later store-hash checks therefore remain atomic with the batched
        # coordinator state update and durable registry projection.
        with promote_final_cards.PromoteClaim(
                promote_final_cards.DEFAULT_STORE):
            promote_final_cards.batch_promote(
                batch,
                promote_final_cards.DEFAULT_STORE,
                'ai_translated',
                args.gen_model_version,
                report_path=batch_report,
                journal_path=journal_path,
                promotion_id=promotion_id,
                store_claim_held=True,
            )
            finish_promotion_journal(
                journal_path, store_claim_held=True)
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
        'reserved_translation_leases': len(reserved_translation_leases(state)),
        'running_translation_leases': len(running_translation_leases(state)),
        'active_translation_leases': len(running_translation_leases(state)),
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
    running = running_translation_leases(state)
    runtime_mode = ('staged-probed' if any(
        lease.get('runtime_mode') == 'staged-probed' for lease in running) else 'standard')
    runtime_limit = (state.get('runtime_limit', STAGED_TRANSLATION_LIMIT)
                     if runtime_mode == 'staged-probed'
                     else TRANSLATION_LIMIT)
    payload = {
        'schema': DASHBOARD_SCHEMA,
        'generated_at': utc_now(),
        'translation_limit': state.get('translation_limit', TRANSLATION_LIMIT),
        'reserved_translation_leases': len(reserved_translation_leases(state)),
        'running_translation_leases': len(running),
        'runtime_limit': runtime_limit,
        'runtime_mode': runtime_mode,
        # Deprecated compatibility alias for one dashboard cycle.
        'active_translation_leases': len(running),
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
    print('reserved    : %d' % len(reserved_translation_leases(state)))
    print('running LLM : %d/%d (%s)' % (
        len(running_translation_leases(state)), state.get('runtime_limit', TRANSLATION_LIMIT),
        state.get('runtime_mode', 'standard')))
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
    p.add_argument('--profile-slot', help='logical profile slot (for example c4; not billing proof)')
    p.add_argument('--config-dir', help='canonical CLAUDE_CONFIG_DIR bound into manifest v2')
    p.add_argument('--executor-lane', default='serial-whole-card')
    p.set_defaults(func=prepare)
    pb = sub.add_parser('prepare-batch')
    pb.add_argument('lease_id', nargs='+')
    pb.add_argument('--allow-over-cost', action='store_true',
                    help='H304 cap-and-defer override: prepare cost-gate-flagged windows '
                         'anyway (dedicated human-budgeted monster session only)')
    pb.add_argument('--profile-slot', help='logical profile slot (for example c4; not billing proof)')
    pb.add_argument('--config-dir', help='canonical CLAUDE_CONFIG_DIR bound into manifest v2')
    pb.add_argument('--executor-lane', default='serial-whole-card')
    pb.set_defaults(func=prepare_batch)
    vp = sub.add_parser(
        'validate-preflight',
        help='revalidate sealed preparation evidence before any live probe or worker')
    vp.add_argument('--lease-id', action='append', required=True)
    vp.set_defaults(func=validate_preflight_command)
    br = sub.add_parser('begin-run')
    br.add_argument('--lease-id', action='append', required=True)
    br.add_argument('--mode', choices=('standard', 'staged'), default='standard')
    br.add_argument('--run-id')
    br.add_argument('--probe-receipt')
    br.set_defaults(func=begin_run)
    rr = sub.add_parser('release-run')
    rr.add_argument('lease_id')
    rr.add_argument('--confirm-dead', action='store_true')
    rr.add_argument('--reason', required=True)
    rr.set_defaults(func=release_run)
    ro = sub.add_parser('recover-operation')
    ro.add_argument('lease_id')
    ro.add_argument('--confirm-dead', action='store_true')
    ro.set_defaults(func=recover_operation)
    r = sub.add_parser('record-output')
    r.add_argument('lease_id')
    r.add_argument('workflow_result')
    r.add_argument('--transcript-dir')
    r.add_argument('--allow-stale', action='store_true')
    r.add_argument('--run-id',
                   help='if set, must match the running lease run_id sealed at begin-run '
                        '(P11: refuses a stale/zombie run recording against a re-leased run)')
    r.add_argument('--result-sha256',
                   help='sealed SHA-256 of the exact submitted result; required with a run ID')
    r.set_defaults(func=record_output)
    rb = sub.add_parser('record-output-batch')
    rb.add_argument(
        '--record', action='append', nargs=4, required=True,
        metavar=('LEASE_ID', 'WORKFLOW_RESULT', 'RUN_ID', 'RESULT_SHA256'),
        help='repeatable record tuple; use - sentinels only for a legacy unsealed lease')
    rb.add_argument('--allow-stale', action='store_true')
    rb.set_defaults(func=record_output_batch)
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
    try:
        reconcile_promotion_journals()
    except (promotion_journal.JournalError,
            promote_final_cards.PromotionContractError) as exc:
        raise SystemExit('promotion reconciliation blocked: %s' % exc) from exc
    args.func(args)


if __name__ == '__main__':
    main()
