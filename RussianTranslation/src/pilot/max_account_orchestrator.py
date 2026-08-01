#!/usr/bin/env python
"""Restartable scheduler for sealed coordinator manifests on authenticated profiles.

Arbitrary argv jobs are refused: only imported coordinator manifests carry the
required run, preflight, reservation, profile, and result bindings.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time

from run_observability import append_event, write_census
from headless_worker import (claude_argv_prefix, run_tree_kill, timeout_output_text,
                             validate_preflight_artifact, windows_hidden_flags)
from window_common import atomic_write_text
from execution_contract import (ActiveCallClaim, config_dir_fingerprint, validate_manifest,
                                validate_profile)
from call_reservation import (CallLimitReached, CallReservationLedger, run_ids,
                              telemetry_from_cli_wrapper, unevaluable_telemetry)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
  name TEXT PRIMARY KEY, config_dir TEXT NOT NULL, parked_until INTEGER NOT NULL DEFAULT 0,
  last_error TEXT, validated INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, external_id TEXT UNIQUE NOT NULL,
  argv_json TEXT NOT NULL DEFAULT '[]', cwd TEXT NOT NULL, output_path TEXT NOT NULL,
  manifest_path TEXT, manifest_sha256 TEXT, profile_slot TEXT,
  preflight_path TEXT, preflight_sha256 TEXT,
  result_sha256 TEXT, attempt_log_path TEXT, run_id TEXT,
  failure_class TEXT, reset_at INTEGER,
  coordinator_recorded INTEGER NOT NULL DEFAULT 0,
  state TEXT NOT NULL DEFAULT 'pending', assigned_acc TEXT, attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 3, started_at TEXT, finished_at TEXT,
  returncode INTEGER, error TEXT
);
CREATE INDEX IF NOT EXISTS jobs_state_id ON jobs(state, id);
"""
RATE_LIMIT = re.compile(r"rate.?limit|usage limit|too many requests|429", re.I)
RESET_EPOCH = re.compile(r"(?:reset(?:s|_at)?|parked_until)[^0-9]{0,20}([0-9]{10})", re.I)


def _profile_slot_from_manifest(manifest_path):
    """Return a validated v2 profile slot, or None for unreadable/invalid legacy input."""
    try:
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        validate_manifest(manifest, require_v2=True)
        return manifest['execution']['profile_slot']
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def is_rate_limited(worker_status, stderr):
    """True only for a genuine provider rate-limit (D-C fix).

    The previous heuristic searched the worker's combined stdout, which prints the
    ``manifest_sha256`` — a hash containing "429" falsely parked a healthy account for
    5 h during the H818 Windows acceptance. Trust the worker's own classification
    (``headless_worker`` exits 21 / classification ``rate_limit`` on a real 429), and
    fall back only to the raw provider stderr. The status JSON / hash is never searched.
    """
    if (worker_status or {}).get('classification') == 'rate_limit':
        return True
    return bool(RATE_LIMIT.search(stderr or ''))


def promotion_classification(lease):
    """Promotion telemetry (D-H). Three distinct outcomes, never conflated:
    * ``success``       -- a positive canonical-store delta.
    * ``not_attempted`` -- nothing was eligible to promote (audit ``needs_requeue`` / zero clean
      cards): the promoter was never invoked for this lease, so it is NOT a conflict.
    * ``conflict``      -- clean cards existed and promotion ran, but produced no positive delta
      (a genuine lock/store/promotion conflict).
    Previously any non-positive delta was reported as ``conflict``, mislabelling the common
    zero-clean requeue case as a conflict and poisoning the census."""
    if (lease.get('store_delta') or 0) > 0:
        return 'success'
    if int(lease.get('clean_count') or 0) == 0:
        return 'not_attempted'
    return 'conflict'


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def required_call_ledger(args, context='paid call'):
    path = getattr(args, 'call_reservation', None)
    run_id = getattr(args, 'run_id', None)
    if not path or not run_id:
        raise SystemExit('%s requires --call-reservation and --run-id' % context)
    try:
        return CallReservationLedger(path, run_id, getattr(args, 'max_calls', None))
    except ValueError as exc:
        raise SystemExit('%s: %s' % (context, exc))


def connect(path):
    # D-G: a real busy_timeout so concurrent claimers (independent connections racing the same
    # BEGIN IMMEDIATE write lock) WAIT for the lock instead of failing with SQLITE_BUSY / "database
    # is locked". `timeout=` sets it at the driver level; the explicit PRAGMA documents + enforces
    # it on the connection so the one-active-job-per-account guard is genuinely serialized.
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA busy_timeout=30000')
    db.executescript(SCHEMA)
    existing = {row[1] for row in db.execute('PRAGMA table_info(jobs)')}
    for name, declaration in (
            ('manifest_path', 'TEXT'), ('manifest_sha256', 'TEXT'),
            ('profile_slot', 'TEXT'),
            ('preflight_path', 'TEXT'), ('preflight_sha256', 'TEXT'),
            ('result_sha256', 'TEXT'), ('attempt_log_path', 'TEXT'),
            ('run_id', 'TEXT'),
            ('failure_class', 'TEXT'), ('reset_at', 'INTEGER'),
            ('coordinator_recorded', 'INTEGER NOT NULL DEFAULT 0')):
        if name not in existing:
            db.execute('ALTER TABLE jobs ADD COLUMN %s %s' % (name, declaration))
    account_cols = {row[1] for row in db.execute('PRAGMA table_info(accounts)')}
    if 'validated' not in account_cols:
        db.execute('ALTER TABLE accounts ADD COLUMN validated INTEGER NOT NULL DEFAULT 0')
    # Existing production databases may predate the profile_slot column. Recheck claim-relevant
    # NULL rows on every connection so a crash after ALTER but before backfill cannot strand them.
    # Historical completed rows are never reopened. Invalid active manifests receive an empty
    # sentinel so an unrelated healthy scope does not reparse them on every connect(). cmd_run_once
    # explicitly retries falsey bindings in its own scope, preserving repair-and-resume recovery.
    for row in db.execute(
            "SELECT id,manifest_path FROM jobs WHERE manifest_path IS NOT NULL "
            "AND profile_slot IS NULL AND state IN ('pending','in_progress')"):
        profile_slot = _profile_slot_from_manifest(row['manifest_path']) or ''
        db.execute('UPDATE jobs SET profile_slot=? WHERE id=?', (profile_slot, row['id']))
    db.commit()
    return db


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path, text):
    atomic_write_text(path, text)


def write_synthetic_preflight(path, root, selected_keys=None):
    """Write explicit zero-work/canary evidence for paid probes without a coordinator lease."""
    payload = {
        'schema': 'pwg.performance_preflight.v1',
        'root': root,
        'selected_keys': list(selected_keys or []),
        'cost_gate': {'over_ceiling': False},
        'synthetic_probe_only': True,
    }
    atomic_write(path, json.dumps(payload, ensure_ascii=False, indent=1) + '\n')
    validate_preflight_artifact(path)
    return os.path.abspath(path)


def coordinator_command(args, command, check=True):
    coordinator = os.path.abspath(getattr(
        args, 'coordinator', os.path.join(os.path.dirname(__file__), 'coordinator.py')))
    env = os.environ.copy()
    coord_dir = getattr(args, 'coord_dir', None)
    if coord_dir:
        env['PWG_COORDINATOR_DIR'] = os.path.abspath(coord_dir)
    proc = subprocess.run(
        [sys.executable, coordinator] + list(command),
        cwd=os.path.abspath(getattr(args, 'cwd', os.path.dirname(os.path.dirname(__file__)))),
        env=env, text=True, encoding='utf-8', capture_output=True)
    if check and proc.returncode:
        raise SystemExit((proc.stderr or proc.stdout or 'coordinator command failed')[-2000:])
    return proc


def release_db_claims(db_path, jobs, error):
    """Undo scheduler claims when the coordinator atomically rejects the dispatch batch."""
    db = connect(db_path)
    with db:
        for job in jobs:
            db.execute(
                "UPDATE jobs SET state='pending', assigned_acc=NULL, attempts=max(attempts-1,0), "
                "started_at=NULL, error=? WHERE id=? AND state='in_progress'",
                (error[-2000:], job['id']))
    db.close()


def bind_jobs_to_run(db_path, jobs, run_id):
    """Seal the run identity before any worker spawn; retries may only reuse that identity."""
    if not run_id:
        raise ValueError('manifest jobs require a run_id before spawn')
    db = connect(db_path)
    try:
        with db:
            for job in jobs:
                row = db.execute('SELECT run_id FROM jobs WHERE id=?', (job['id'],)).fetchone()
                saved = row['run_id'] if row else None
                if saved and saved != run_id:
                    raise ValueError('%s: saved run_id %r refuses resume as %r'
                                     % (job['external_id'], saved, run_id))
                db.execute('UPDATE jobs SET run_id=? WHERE id=? AND run_id IS NULL',
                           (run_id, job['id']))
    finally:
        db.close()


# H1339 A4: a materialised requeue attempt is a NEW job (jobs.external_id is UNIQUE) on the
# SAME coordinator lease -- its external_id is '<lease>::rqNN-<kind>'. Every coordinator
# command that names a lease must map through coordinator_lease_id(); the sqlite layer keeps
# the full external_id. '::' can never appear in a plain lease id (make_lease_id/plan roots).
RQ_ID_SEP = '::rq'


def coordinator_lease_id(external_id):
    """The coordinator lease a job binds to (strips a requeue attempt's '::rqNN-kind')."""
    return (external_id or '').split(RQ_ID_SEP, 1)[0]


def release_runtime(args, lease_id, reason):
    return coordinator_command(
        args, ['release-run', coordinator_lease_id(lease_id), '--confirm-dead',
               '--reason', reason], check=False)


def safe_receipt_name(value):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', value)[:120]


def write_probe_receipt(coord_dir, run_id, lease_ids, probe_latencies):
    receipt_dir = os.path.join(os.path.abspath(coord_dir), 'probe_receipts')
    os.makedirs(receipt_dir, exist_ok=True)
    path = os.path.join(receipt_dir, 'probe_receipt.%s.json' % safe_receipt_name(run_id))
    payload = {
        'schema': PROBE_RECEIPT_SCHEMA,
        'generated_at': now_iso(),
        'run_id': run_id,
        'go': True,
        'lease_ids': sorted(set(lease_ids)),
        'healthy_profiles': sorted(probe_latencies),
        'probe_latency_ms': dict(probe_latencies),
        'model': EXACT_GEN_MODEL,
        'policy': PROBE_POLICY,
    }
    atomic_write(path, json.dumps(payload, ensure_ascii=False, indent=1) + '\n')
    return path


def parse_reset(text, now=None):
    now = int(now or time.time())
    match = RESET_EPOCH.search(text or '')
    return int(match.group(1)) if match else now + 5 * 60 * 60


def _scope_sql(only_external_ids):
    if only_external_ids is None:
        return '', ()
    # H1386 C1 defense-in-depth: iterating a dict yields its keys and a str its characters,
    # silently degrading the scope to a zero-match (the bounded --resume regression). A scope
    # must be a set/list/tuple of external ids -- reject the wrong shape loudly.
    if isinstance(only_external_ids, (dict, str, bytes)):
        raise TypeError('only_external_ids must be a set/list of external ids, got %s'
                        % type(only_external_ids).__name__)
    ids = tuple(sorted(set(only_external_ids)))
    if not ids:
        return ' AND 0', ()
    return ' AND external_id IN (%s)' % ','.join('?' for _ in ids), ids


def scoped_job_count(db, only_external_ids, predicate):
    scope_sql, scope_args = _scope_sql(only_external_ids)
    return db.execute(
        'SELECT count(*) FROM jobs WHERE %s%s' % (predicate, scope_sql),
        scope_args).fetchone()[0]


def scoped_jobs(db, only_external_ids, predicate='1=1'):
    scope_sql, scope_args = _scope_sql(only_external_ids)
    return list(db.execute(
        'SELECT * FROM jobs WHERE %s%s ORDER BY id' % (predicate, scope_sql),
        scope_args))


def _claim_tx(db, account, now, only_external_ids=None):
    """The atomic claim transaction on an ALREADY-OPEN connection. Split out from ``claim`` so the
    concurrency race test can open independent connections BEFORE a barrier and fire both
    transactions at the same instant; production ``claim`` owns its own connection."""
    db.execute('BEGIN IMMEDIATE')
    acc = db.execute('SELECT * FROM accounts WHERE name=?', (account,)).fetchone()
    if not acc or not acc['validated'] or acc['parked_until'] > now:
        db.rollback()
        return None
    # D-G: one active job per account. Inside this BEGIN IMMEDIATE transaction (which holds a
    # write lock, serializing concurrent claimers), refuse the account if it already owns an
    # in_progress job. Two independent claimers racing for the same validated account => only
    # one obtains a job; the other sees the in_progress row (or is blocked until commit) and
    # backs off. Enforces the "one account, strictly sequential" contract atomically.
    if db.execute("SELECT 1 FROM jobs WHERE state='in_progress' AND assigned_acc=? LIMIT 1",
                  (account,)).fetchone():
        db.rollback()
        return None
    scope_sql, scope_args = _scope_sql(only_external_ids)
    job = db.execute(
        "SELECT * FROM jobs WHERE state='pending' AND attempts < max_attempts "
        "AND (manifest_path IS NULL OR profile_slot=?)%s ORDER BY id LIMIT 1"
        % scope_sql, (account,) + scope_args).fetchone()
    if not job:
        db.rollback()
        return None
    changed = db.execute(
        "UPDATE jobs SET state='in_progress', assigned_acc=?, attempts=attempts+1, started_at=?, error=NULL WHERE id=? AND state='pending'",
        (account, now_iso(), job['id']))
    if changed.rowcount != 1:
        db.rollback()
        return None
    db.commit()
    return db.execute('SELECT * FROM jobs WHERE id=?', (job['id'],)).fetchone()


def claim(db_path, account, now=None, only_external_ids=None):
    now = int(now or time.time())
    db = connect(db_path)
    try:
        return _claim_tx(db, account, now, only_external_ids=only_external_ids)
    finally:
        db.close()


def finish(db_path, job_id, state, returncode, error=None, failure_class=None,
           result_sha256=None, attempt_log_path=None, reset_at=None, run_id=None):
    db = connect(db_path)
    with db:
        db.execute('UPDATE jobs SET state=?, returncode=?, error=?, failure_class=?, '
                   'result_sha256=COALESCE(?,result_sha256), attempt_log_path=COALESCE(?,attempt_log_path), '
                   'run_id=COALESCE(?,run_id), reset_at=?, finished_at=? WHERE id=?',
                   (state, returncode, error, failure_class, result_sha256,
                    attempt_log_path, run_id, reset_at, now_iso(), job_id))
    db.close()


def fail_or_retry(db_path, job_id, returncode, error, failure_class=None,
                  attempt_log_path=None):
    db = connect(db_path)
    row = db.execute('SELECT attempts,max_attempts FROM jobs WHERE id=?', (job_id,)).fetchone()
    state = 'pending' if row and row['attempts'] < row['max_attempts'] else 'failed'
    db.close()
    finish(db_path, job_id, state, returncode, error, failure_class=failure_class,
           attempt_log_path=attempt_log_path)
    return state


# H1 (H1940): the classes whose verdict cannot change on a re-run. A malformed manifest, a
# profile/preflight refusal, a drifted seal — nothing about attempt 2 differs from attempt 1,
# so retrying only reproduces the same verdict and consumes the budget a genuinely transient
# failure would have needed.
DETERMINISTIC_FAILURE_CLASSES = frozenset({'configuration', 'manifest_drift'})

# Classes the windows100 readiness report surfaces as hard failures. H1 (H1940) added
# `configuration` when it became TERMINAL: a class that permanently kills a job and never
# appears here is the silent-loss shape the report exists to prevent — the window would
# simply be absent, with nothing saying why. Module-level so a selftest can pin membership
# instead of re-typing the literal.
HARD_FAILURE_CLASSES = frozenset({'authentication', 'configuration', 'manifest_drift',
                                  'malformed_output', 'rate_limit'})


def fail_terminal(db_path, job_id, returncode, error, failure_class,
                  attempt_log_path=None):
    """Fail a job outright, on this attempt, without consulting the retry budget.

    Deliberately a SEPARATE entry point rather than a classification branch inside
    fail_or_retry: transient classes ('process', 'timeout', 'result_drift', a bare
    worker failure) must keep their retry budget exactly as before, and one shared
    function that decided by class is the shape in which that is easy to regress.
    Callers opt in per site; fail_or_retry is unchanged.
    """
    finish(db_path, job_id, 'failed', returncode, error, failure_class=failure_class,
           attempt_log_path=attempt_log_path)
    return 'failed'


def park(db_path, account, until, error):
    db = connect(db_path)
    with db:
        db.execute('UPDATE accounts SET parked_until=?, last_error=?, updated_at=? WHERE name=?',
                   (until, error[-2000:], now_iso(), account))
    db.close()


def requeue_rate_limited(db_path, job_id, returncode, error, reset_at, attempt_log_path=None):
    """C4: a rate-limit (429) is an infra throttle, not a defective translation attempt. Return the
    job to 'pending' AND give back the attempt it consumed at claim time (mirrors
    release_db_claims' `attempts=max(attempts-1,0)`), so it stays claimable once its account
    unparks. Without the decrement, a job rate-limited max_attempts times sits 'pending' with
    attempts==max_attempts — never re-selected by claim (which gates on `attempts < max_attempts`),
    never marked 'failed', permanently stranded — and cmd_staged_run busy-spins on the
    un-drainable pending count."""
    db = connect(db_path)
    with db:
        db.execute("UPDATE jobs SET state='pending', returncode=?, error=?, failure_class='rate_limit', "
                   "attempts=max(attempts-1,0), reset_at=?, "
                   "attempt_log_path=COALESCE(?,attempt_log_path), finished_at=? WHERE id=?",
                   (returncode, error, reset_at, attempt_log_path, now_iso(), job_id))
    db.close()


def emit_call_events(events_path, item, idx, manifest_sha256, base):
    """D-I: telemetry for ONE real model call. Emit exactly one call-level 'model_call' event
    (the single latency sample + classification tally for this call, with a stable call_id and
    key_count), then one 'model_call_key' relation event per key. The per-key events carry no
    elapsed_ms and are excluded from the latency/classification census, so a 5-key call yields
    exactly one latency sample and one classification count (previously it was one per key,
    inflating p50/p95 and the classification totals on large batches)."""
    keys = [k for k in (item.get('keys') or []) if k is not None]
    mhash = (item.get('manifest_sha256') or manifest_sha256 or 'call')[:12]
    # call_id identifies the ACTUAL invocation: manifest # dispatch-attempt # worker label. The
    # worker's label encodes the retry/split path (`.retry1`, per-fragment labels), and the
    # dispatch attempt increments on a recover/re-run — so a genuine re-run gets a NEW call_id,
    # while a crash that re-appends the SAME event to the append-only log reproduces the SAME
    # call_id (the census dedups those and flags any conflicting-data duplicate).
    call_id = '%s#a%s#%s' % (mhash, base.get('attempt', '0'), item.get('label') or idx)
    append_event(events_path, stage='worker', event='model_call', call_id=call_id,
                 key_count=len(keys), elapsed_ms=item.get('elapsed_ms'),
                 classification=item.get('classification'), **base)
    for key in keys:
        append_event(events_path, stage='worker', event='model_call_key', call_id=call_id,
                     key=key, classification=item.get('classification'), **base)


def run_claimed(db_path, account, config_dir, job, timeout, events_path=None, run_id=None,
                claude_bin='claude', call_reservation_path=None, max_calls=None):
    attempt = job['attempts']
    attempt_log = job['output_path'] + '.attempt%d.runner.json' % attempt
    status_path = job['output_path'] + '.attempt%d.status.json' % attempt
    event_base = {'run_id': run_id, 'lease_id': job['external_id'],
                  'window_id': job['external_id'], 'attempt': attempt,
                  'account': account, 'manifest_hash': job['manifest_sha256']}
    if events_path:
        append_event(events_path, stage='dispatch', event='attempt_start', **event_base)
    if job['manifest_path']:
        db = connect(db_path)
        saved_run_id = db.execute(
            'SELECT run_id FROM jobs WHERE id=?', (job['id'],)).fetchone()['run_id']
        db.close()
        if not run_id or saved_run_id != run_id:
            raise RuntimeError('job/run binding mismatch before spawn: saved=%r requested=%r'
                               % (saved_run_id, run_id))
        if not call_reservation_path:
            raise RuntimeError('manifest worker spawn requires a call reservation ledger')
        # H1 (H1940): this pre-launch hash + read was unguarded, so a missing manifest
        # (sha256_path -> FileNotFoundError) or invalid JSON escaped run_claimed entirely
        # and took the orchestrator down with it — the job never even reached a verdict,
        # let alone the worker's own status file. Both are deterministic, so both are
        # terminal here rather than returned to 'pending'.
        try:
            if sha256_path(job['manifest_path']) != job['manifest_sha256']:
                return fail_terminal(db_path, job['id'], 2, 'manifest hash changed',
                                     'manifest_drift', attempt_log)
            manifest = json.load(open(job['manifest_path'], encoding='utf-8'))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return fail_terminal(db_path, job['id'], 2,
                                 'sealed manifest is unreadable: %s' % exc,
                                 'configuration', attempt_log)
        try:
            validate_profile(manifest, config_dir, account)
            validate_preflight_artifact(
                job['preflight_path'], manifest, job['preflight_sha256'])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return fail_terminal(db_path, job['id'], 2,
                                 '%s: %s' % (type(exc).__name__, exc)
                                 if isinstance(exc, (KeyError, TypeError)) else str(exc),
                                 'configuration', attempt_log)
        argv = [sys.executable, os.path.join(os.path.dirname(__file__), 'headless_worker.py'),
                job['manifest_path'], '--output', job['output_path'],
                '--status-out', status_path, '--timeout', str(timeout),
                '--claude-bin', claude_bin, '--only-profile', account,
                '--preflight', job['preflight_path'],
                '--preflight-sha256', job['preflight_sha256'],
                '--manifest-sha256', job['manifest_sha256']]
    else:
        return fail_terminal(
            db_path, job['id'], 2,
            'legacy generic argv jobs are disabled; re-enqueue through a sealed '
            'coordinator manifest',
            'configuration', attempt_log)
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    if call_reservation_path:
        env['PWG_CALL_RESERVATION_PATH'] = os.path.abspath(call_reservation_path)
        env['PWG_CALL_RESERVATION_RUN_ID'] = run_id or ''
        env['PWG_CALL_RESERVATION_MAX_CALLS'] = '' if max_calls is None else str(max_calls)
    try:
        proc = run_tree_kill(argv, cwd=job['cwd'], env=env, text=True, encoding='utf-8',
                             capture_output=True, timeout=timeout)   # D-J: tree-kill on timeout
        payload = json.dumps({'argv': argv, 'returncode': proc.returncode,
                              'stdout': proc.stdout, 'stderr': proc.stderr}, ensure_ascii=False, indent=1)
        atomic_write(attempt_log, payload)
        combined = proc.stdout + '\n' + proc.stderr
        worker_status = {}
        if os.path.exists(status_path):
            try:
                worker_status = json.load(open(status_path, encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                worker_status = {}
        if (job['manifest_path']
                and worker_status.get('manifest_sha256') != job['manifest_sha256']):
            state = fail_terminal(
                db_path, job['id'], 2,
                'worker manifest hash does not match the sealed job manifest',
                'manifest_drift', attempt_log)
            if events_path:
                append_event(
                    events_path, stage='dispatch', event='attempt_end',
                    classification='manifest_drift', **event_base)
            return state
        if events_path:
            for idx, item in enumerate(worker_status.get('attempts') or []):
                emit_call_events(events_path, item, idx,
                                 worker_status.get('manifest_sha256'), event_base)
        failure_class = worker_status.get('classification')
        if is_rate_limited(worker_status, proc.stderr):
            reset_text = (proc.stderr or '') + '\n' + (worker_status.get('error') or '')
            until = parse_reset(reset_text)
            park(db_path, account, until, reset_text)
            requeue_rate_limited(db_path, job['id'], proc.returncode,
                                 'rate-limited; account parked', until,
                                 attempt_log_path=attempt_log)
            if events_path:
                append_event(events_path, stage='dispatch', event='attempt_end',
                             classification='rate_limit', reset_at=until, **event_base)
            return 'parked'
        if proc.returncode == 0:
            result_hash = (
                sha256_path(job['output_path'])
                if os.path.exists(job['output_path']) else None)
            if (job['manifest_path']
                    and (not result_hash
                         or worker_status.get('result_sha256') != result_hash)):
                return fail_or_retry(
                    db_path, job['id'], 2,
                    'worker result hash does not match the sealed status result',
                    'result_drift', attempt_log)
            finish(db_path, job['id'], 'done', 0, failure_class='success',
                   result_sha256=result_hash, attempt_log_path=attempt_log, run_id=run_id)
            if events_path:
                append_event(events_path, stage='dispatch', event='attempt_end',
                             classification='success', result_hash=result_hash, **event_base)
            return 'done'
        # H1 (H1940): the worker's own classification now decides retry-vs-terminal for the
        # deterministic classes. Previously every non-zero worker exit went to fail_or_retry,
        # which keys purely on `attempts < max_attempts` — so a `configuration` verdict (a
        # manifest that will never parse) was retried exactly like a dropped connection.
        # Anything else, including a bare failure with no classification, retries as before.
        failer = (fail_terminal if failure_class in DETERMINISTIC_FAILURE_CLASSES
                  else fail_or_retry)
        state = failer(db_path, job['id'], proc.returncode, combined[-2000:],
                       failure_class or 'process', attempt_log)
        if events_path:
            append_event(events_path, stage='dispatch', event='attempt_end',
                         classification=failure_class or 'process', **event_base)
        return state
    except subprocess.TimeoutExpired:
        state = fail_or_retry(db_path, job['id'], 124, 'timeout after %ss' % timeout,
                              'timeout', attempt_log)
        if events_path:
            append_event(events_path, stage='dispatch', event='attempt_end',
                         classification='timeout', **event_base)
        return state
    except OSError as exc:
        return fail_or_retry(db_path, job['id'], 127, str(exc), 'process', attempt_log)


def profile_status(config_dir, claude='claude', call_reservation=None, account=None,
                   preflight_path=None):
    if not os.path.isdir(config_dir):
        return False, 'profile directory missing'
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    try:
        proc = run_tree_kill(claude_argv_prefix(claude) + ['auth', 'status', '--json'],
                             env=env, text=True,
                             encoding='utf-8', capture_output=True, timeout=30)   # D-J: tree-kill
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, (proc.stderr or proc.stdout)[-500:]
    if proc.returncode or not data.get('loggedIn'):
        return False, data.get('subscriptionType') or 'not logged in'
    if call_reservation is None:
        raise ValueError('paid profile validation requires a call reservation ledger')
    validate_preflight_artifact(preflight_path)
    with ActiveCallClaim(config_dir_fingerprint(config_dir)):
        reservation = call_reservation.reserve('profile:init', profile=account)
        try:
            probe = run_tree_kill(               # D-J: tree-kill on timeout
                claude_argv_prefix(claude) + [
                    '-p', 'Return exactly OK.', '--output-format', 'json',
                    '--model', 'claude-sonnet-5', '--permission-mode', 'plan'],
                env=env, text=True, encoding='utf-8',
                capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            call_reservation.finalize(reservation, unevaluable_telemetry())
            return False, 'timeout'
        except BaseException:
            # The reservation is irreversible once the runner may have
            # spawned. An unexpected runner failure cannot remain pending or
            # masquerade as a zero-cost validation.
            call_reservation.finalize(reservation, unevaluable_telemetry())
            raise
    try:
        wrapper = json.loads(probe.stdout or '')
    except (TypeError, ValueError):
        wrapper = None
    telemetry = telemetry_from_cli_wrapper(wrapper)
    envelope_ok = (
        isinstance(wrapper, dict)
        and wrapper.get('type') == 'result'
        and wrapper.get('subtype') == 'success'
        and wrapper.get('is_error') is not True)
    if not envelope_ok:
        telemetry = dict(telemetry, cost_evaluable=False)
    call_reservation.finalize(reservation, telemetry)
    if probe.returncode:
        return False, ((probe.stderr or '') + '\n' + (probe.stdout or ''))[-500:]
    if not envelope_ok:
        return False, 'paid profile validation probe returned no valid success envelope'
    return True, data.get('subscriptionType') or 'unknown'


def cmd_init(args):
    call_reservation = (None if args.skip_profile_check else
                        required_call_ledger(args, context='init profile probe'))
    preflight = None
    if call_reservation is not None:
        preflight = write_synthetic_preflight(
            call_reservation.path + '.profile-preflight.json',
            'profile-init-' + call_reservation.run_id)
    db = connect(args.db)
    with db:
        for item in args.account:
            name, config_dir = item.split('=', 1)
            config_dir = os.path.abspath(config_dir)
            ok, detail = ((True, 'test override') if args.skip_profile_check else
                          profile_status(
                              config_dir, args.claude_bin, call_reservation, name, preflight))
            if not ok:
                raise SystemExit('%s: profile validation failed: %s' % (name, detail))
            db.execute('INSERT OR REPLACE INTO accounts(name,config_dir,parked_until,last_error,validated,updated_at) VALUES(?,?,0,NULL,1,?)',
                       (name, config_dir, now_iso()))
    db.close()


def cmd_enqueue(args):
    raise SystemExit(
        'generic argv jobs are disabled; import a sealed coordinator manifest '
        'so run/preflight/reservation/profile/result binding is mandatory')


def cmd_import_coordinator(args):
    state_path = os.path.join(os.path.abspath(args.coord_dir), 'state.json')
    with open(state_path, encoding='utf-8') as f:
        state = json.load(f)
    wanted = set(args.lease_id or [])
    leases = [lease for lease in state.get('leases', [])
              if lease.get('state') == 'prepared' and (not wanted or lease.get('id') in wanted)]
    if wanted - {lease.get('id') for lease in leases}:
        raise SystemExit('requested lease is not prepared')
    db = connect(args.db)
    occupied = set()
    for row in db.execute("SELECT manifest_path FROM jobs WHERE state IN ('pending','in_progress') AND manifest_path IS NOT NULL"):
        try:
            occupied.update(json.load(open(row['manifest_path'], encoding='utf-8'))['meta']['selected_keys'])
        except (OSError, KeyError, json.JSONDecodeError):
            pass
    added = 0
    with db:
        for lease in leases:
            manifest_path = lease.get('execution_manifest')
            if not manifest_path or not os.path.exists(manifest_path):
                raise SystemExit('%s: execution manifest missing' % lease.get('id'))
            manifest = json.load(open(manifest_path, encoding='utf-8'))
            try:
                validate_manifest(manifest, require_v2=True)
            except ValueError as exc:
                raise SystemExit('%s: %s' % (lease['id'], exc))
            if manifest['meta'].get('lang') != 'ru':
                raise SystemExit('%s: H818 production default is RU only' % lease['id'])
            profile_slot = manifest['execution']['profile_slot']
            preflight_path = lease.get('preflight_path')
            preflight_hash = lease.get('preflight_sha256')
            if not preflight_path or not preflight_hash or not os.path.exists(preflight_path):
                raise SystemExit('%s: sealed preflight missing' % lease['id'])
            if sha256_path(preflight_path) != preflight_hash:
                raise SystemExit('%s: sealed preflight hash changed' % lease['id'])
            keys = set(manifest['meta']['selected_keys'])
            overlap = keys & occupied
            if overlap:
                raise SystemExit('%s: key overlap with queued/done job: %s' %
                                 (lease['id'], ','.join(sorted(overlap))))
            output = os.path.join(lease['artifact_dir'], 'workflow_result.headless.%s.json' % lease['id'])
            db.execute('INSERT INTO jobs(external_id,cwd,output_path,manifest_path,manifest_sha256,profile_slot,preflight_path,preflight_sha256,max_attempts) VALUES(?,?,?,?,?,?,?,?,?)',
                       (lease['id'], os.path.abspath(args.cwd), output, manifest_path,
                        sha256_path(manifest_path), profile_slot, preflight_path,
                        preflight_hash, args.max_attempts))
            occupied.update(keys)
            added += 1
    db.close()
    print('imported=%d' % added)


def cmd_import_requeue(args):
    """H1339 A4 (the fuller fix): import ONE requeue_prepared lease attempt as a runnable job.

    cmd_import_coordinator imports only state=='prepared' leases, so a coordinator requeue
    attempt (prepare-requeue -> requeue_prepared) was INVISIBLE to the sqlite dispatch
    layer: the unattended loop's rq work-items matched no lease and no job, run_window
    no-op'd, and the rejected keys were silently dropped (checkpointed COMPLETED with zero
    model calls) until the Tier-A fail-loud guard, which stopped the loss but not the work.
    The imported job's external_id is '<lease>::rqNN-<kind>' (UNIQUE per attempt; the
    coordinator commands map back via coordinator_lease_id). Idempotent: an already-present
    attempt job imports nothing, so a crash between import and dispatch resumes cleanly.
    Returns the attempt job's external_id."""
    state_path = os.path.join(os.path.abspath(args.coord_dir), 'state.json')
    with open(state_path, encoding='utf-8') as f:
        state = json.load(f)
    lease = next((l for l in state.get('leases', []) if l.get('id') == args.lease_id), None)
    if lease is None:
        raise SystemExit('%s: unknown coordinator lease' % args.lease_id)
    if lease.get('state') != 'requeue_prepared':
        raise SystemExit('%s: lease state %r is not requeue_prepared -- run '
                         'coordinator prepare-requeue first' % (args.lease_id, lease.get('state')))
    attempt = lease.get('current_attempt') or {}
    number = int(attempt.get('number') or lease.get('requeue_attempt') or 0)
    kind = attempt.get('kind') or lease.get('requeue_kind') or 'requeue'
    manifest_path = attempt.get('execution_manifest') or lease.get('execution_manifest')
    if not manifest_path or not os.path.exists(manifest_path):
        raise SystemExit('%s: requeue execution manifest missing' % args.lease_id)
    manifest = json.load(open(manifest_path, encoding='utf-8'))
    try:
        validate_manifest(manifest, require_v2=True)
    except ValueError as exc:
        raise SystemExit('%s: %s' % (args.lease_id, exc))
    if manifest['meta'].get('lang') != 'ru':
        raise SystemExit('%s: H818 production default is RU only' % args.lease_id)
    profile_slot = manifest['execution']['profile_slot']
    preflight_path = attempt.get('preflight') or lease.get('preflight_path')
    preflight_hash = attempt.get('preflight_sha256') or lease.get('preflight_sha256')
    if not preflight_path or not preflight_hash or not os.path.exists(preflight_path):
        raise SystemExit('%s: requeue sealed preflight missing' % args.lease_id)
    if sha256_path(preflight_path) != preflight_hash:
        raise SystemExit('%s: requeue sealed preflight hash changed' % args.lease_id)
    external_id = '%s%s%02d-%s' % (args.lease_id, RQ_ID_SEP, number, kind)
    db = connect(args.db)
    existing = {row['external_id'] for row in db.execute('SELECT external_id FROM jobs')}
    if external_id in existing:
        db.close()
        print('imported=0 (attempt job exists: %s)' % external_id)
        return external_id
    occupied = set()
    for row in db.execute("SELECT manifest_path FROM jobs WHERE state IN ('pending','in_progress') AND manifest_path IS NOT NULL"):
        try:
            occupied.update(json.load(open(row['manifest_path'], encoding='utf-8'))['meta']['selected_keys'])
        except (OSError, KeyError, json.JSONDecodeError):
            pass
    keys = set(manifest['meta']['selected_keys'])
    overlap = keys & occupied
    if overlap:
        raise SystemExit('%s: requeue key overlap with a queued/running job: %s' %
                         (args.lease_id, ','.join(sorted(overlap))))
    adir = attempt.get('artifact_dir') or lease.get('artifact_dir')
    # NOTE: the OUTPUT filename must stay Windows-legal -- never embed the '::' separator.
    output = os.path.join(adir, 'workflow_result.headless.%s.rq%02d-%s.json'
                          % (args.lease_id, number, kind))
    with db:
        db.execute('INSERT INTO jobs(external_id,cwd,output_path,manifest_path,manifest_sha256,profile_slot,preflight_path,preflight_sha256,max_attempts) VALUES(?,?,?,?,?,?,?,?,?)',
                   (external_id, os.path.abspath(args.cwd), output, manifest_path,
                    sha256_path(manifest_path), profile_slot, preflight_path,
                    preflight_hash, args.max_attempts))
    db.close()
    print('imported=1 %s' % external_id)
    return external_id


def cmd_reset_failed(args):
    """B18 (H1339, P0): the ONLY sanctioned exit from the terminal 'failed' job state.

    A job failing max_attempts times is deliberately terminal and both drain loops fail
    closed on it -- but there was NO recovery command at all, so one twice-failed job was a
    permanent tombstone that fail-closed every future run of its plan. This is the explicit,
    AUDITED recovery: scoped --lease-id (never a blanket reset), mandatory --reason recorded
    on the row and in the events ledger, attempts rezeroed so the job is claimable again.
    Never called automatically -- an unattended loop must stop loudly, a human decides."""
    if not args.reason or not args.reason.strip():
        raise SystemExit('reset-failed requires a non-empty --reason (audited recovery)')
    scope = set(args.lease_id or [])
    if not scope:
        raise SystemExit('reset-failed requires an explicit --lease-id scope')
    db = connect(args.db)
    rows = scoped_jobs(db, scope, "state='failed'")
    if not rows:
        # H1386 P3c: a failed requeue attempt's external_id is '<lease>::rqNN-<kind>' while
        # the fail-closed drain messages name the ORIGIN lease -- so the documented recovery
        # command, pasted with the origin id, found nothing for the exact requeue-tombstone
        # case B18 was built for. Match by origin lease too (still an explicit scope, never
        # a blanket reset).
        all_failed = scoped_jobs(db, None, "state='failed'")
        rows = [j for j in all_failed
                if coordinator_lease_id(j['external_id']) in scope]
    if not rows:
        db.close()
        raise SystemExit('no failed job in scope %s' % sorted(scope))
    with db:
        for job in rows:
            db.execute(
                "UPDATE jobs SET state='pending', assigned_acc=NULL, attempts=0, "
                "started_at=NULL, error=? WHERE id=? AND state='failed'",
                ('reset-failed: %s' % args.reason.strip()[:500], job['id']))
    db.close()
    events_path = getattr(args, 'events', None)
    if events_path:
        for job in rows:
            append_event(events_path, stage='operator', event='reset_failed',
                         lease_id=job['external_id'], window_id=job['external_id'],
                         note=args.reason.strip()[:500])
    print('reset=%d (%s)' % (len(rows), ', '.join(sorted(j['external_id'] for j in rows))))
    return len(rows)


def cmd_recover(args):
    db = connect(args.db)
    abandoned = scoped_jobs(
        db, getattr(args, 'only_external_ids', None),
        "state='in_progress' AND manifest_path IS NOT NULL")
    db.close()
    for job in abandoned:
        proc = release_runtime(args, job['external_id'], 'orchestrator restart recovery')
        if proc.returncode and 'no runtime reservation to release' not in (proc.stderr + proc.stdout):
            raise SystemExit('%s: coordinator recovery failed: %s' %
                             (job['external_id'], proc.stderr or proc.stdout))
    db = connect(args.db)
    scope_sql, scope_args = _scope_sql(getattr(args, 'only_external_ids', None))
    with db:
        changed = db.execute(
            "UPDATE jobs SET state='pending', assigned_acc=NULL, "
            "error='recovered after restart' WHERE state='in_progress'%s" % scope_sql,
            scope_args).rowcount
    db.close()
    print('recovered=%d' % changed)


def cmd_record_done(args):
    db = connect(args.db)
    jobs = scoped_jobs(
        db, getattr(args, 'only_external_ids', None),
        "state='done' AND coordinator_recorded=0")
    db.close()
    recorded = 0
    for job in jobs:
        if not job['manifest_path'] or not os.path.exists(job['output_path']):
            raise SystemExit('%s: completed coordinator job has no result' % job['external_id'])
        if not job['result_sha256']:
            raise SystemExit('%s: completed coordinator job has no saved result hash'
                             % job['external_id'])
        actual_hash = sha256_path(job['output_path'])
        if actual_hash != job['result_sha256']:
            raise SystemExit('%s: result substitution refused (saved=%s actual=%s)'
                             % (job['external_id'], job['result_sha256'], actual_hash))
        if not job['run_id']:
            raise SystemExit('%s: completed coordinator job has no saved run_id'
                             % job['external_id'])
    if len(jobs) > 1:
        lease_ids = [coordinator_lease_id(job['external_id']) for job in jobs]
        if len(lease_ids) != len(set(lease_ids)):
            raise SystemExit('record-done batch refuses duplicate coordinator lease ids')
        command = ['record-output-batch']
        for job, lease_id in zip(jobs, lease_ids):
            command += ['--record', lease_id, job['output_path'], job['run_id'],
                        job['result_sha256']]
        proc = coordinator_command(args, command, check=False)
        progress = None
        prefix = 'RECORD_OUTPUT_BATCH_PROGRESS: '
        for line in ((proc.stdout or '') + '\n' + (proc.stderr or '')).splitlines():
            if line.startswith(prefix):
                try:
                    candidate = json.loads(line[len(prefix):])
                except json.JSONDecodeError:
                    continue
                if candidate.get('schema') == 'pwg.record_output_batch.v1':
                    progress = candidate
        committed = list((progress or {}).get('recorded') or [])
        if committed != lease_ids[:len(committed)]:
            raise SystemExit('record-done batch returned a non-prefix progress receipt')
        if committed:
            committed_set = set(committed)
            db = connect(args.db)
            with db:
                for job, lease_id in zip(jobs, lease_ids):
                    if lease_id in committed_set:
                        db.execute('UPDATE jobs SET coordinator_recorded=1 WHERE id=?',
                                   (job['id'],))
            db.close()
            recorded = len(committed)
        print(proc.stdout, end='')
        print(proc.stderr, end='', file=sys.stderr)
        if proc.returncode or committed != lease_ids:
            raise SystemExit('coordinator record-output-batch committed %d/%d'
                             % (recorded, len(jobs)))
        print('recorded=%d' % recorded)
        return
    for job in jobs:
        proc = coordinator_command(
            args, ['record-output', coordinator_lease_id(job['external_id']),
                   job['output_path'], '--run-id', job['run_id'],
                   '--result-sha256', job['result_sha256']], check=False)
        if proc.returncode:
            print(proc.stdout, end='')
            print(proc.stderr, end='', file=sys.stderr)
            raise SystemExit('%s: coordinator record-output failed' % job['external_id'])
        db = connect(args.db)
        with db:
            db.execute('UPDATE jobs SET coordinator_recorded=1 WHERE id=?', (job['id'],))
        db.close()
        recorded += 1
        print(proc.stdout, end='')
    print('recorded=%d' % recorded)


def cmd_run_once(args):
    db = connect(args.db)
    accounts = list(db.execute('SELECT * FROM accounts ORDER BY name'))
    db.close()
    # GAP #5 (four-profile): optional dispatch allow-list. cmd_staged_run passes the exact set of
    # accounts that PASSED probe_fleet (set(probe_latencies)) so a --max-accounts-capped or
    # --drop-unhealthy-dropped account — which was never health-probed — cannot receive a job. Without
    # it, this re-select-all dispatch would claim jobs for every validated, unparked account,
    # bypassing the mandatory pre-dispatch probe (the cap/drop would apply only to the probe set).
    # Default (attribute absent / None) is unrestricted, so a standalone `run-once` is unchanged.
    only = getattr(args, 'only_accounts', None)
    if getattr(args, 'only_profile', None):
        requested = {args.only_profile}
        only = requested if only is None else set(only) & requested
    if only is not None:
        accounts = [a for a in accounts if a['name'] in only]
    runtime_mode = getattr(args, 'runtime_mode', 'standard')
    db = connect(args.db)
    scope_sql, scope_args = _scope_sql(getattr(args, 'only_external_ids', None))
    manifest_rows = [dict(row) for row in db.execute(
        "SELECT external_id,manifest_path,profile_slot,attempts,max_attempts FROM jobs "
        "WHERE state='pending' AND manifest_path IS NOT NULL%s ORDER BY id" % scope_sql,
        scope_args)]
    # A falsey binding is the durable invalid-legacy sentinel. Retry only the selected scope so a
    # repaired manifest can recover, without making every unrelated connect() reopen the bad file.
    for row in manifest_rows:
        if not row['profile_slot']:
            repaired_slot = _profile_slot_from_manifest(row['manifest_path'])
            if repaired_slot:
                row['profile_slot'] = repaired_slot
                db.execute('UPDATE jobs SET profile_slot=? WHERE external_id=?',
                           (repaired_slot, row['external_id']))
    db.commit()
    db.close()
    if manifest_rows:
        # Do not over-claim scheduler rows that the coordinator must reject. Generic jobs keep
        # their historical account fan-out because they do not consume translation runtime.
        # B16 (H1339): filter to CLAIM-ELIGIBLE accounts (validated + unparked -- the exact
        # _claim_tx predicate) BEFORE the concurrency slice. Slicing the raw name-ordered
        # roster starved dispatch whenever alphabetically-early accounts were parked: the
        # sliced-in parked accounts could claim nothing while healthy later-named accounts
        # were cut off, and the all-parked halt guard (which counts EVERY validated unparked
        # account) never fired -- the bounded drain spun to its iteration ceiling instead.
        now_ts = int(time.time())
        accounts = [a for a in accounts if a['validated'] and a['parked_until'] <= now_ts]
        missing_binding = [row['external_id'] for row in manifest_rows if not row['profile_slot']]
        if missing_binding:
            raise SystemExit('pending manifest job(s) have no valid profile binding: %s'
                             % ','.join(missing_binding))
        exhausted = [row['external_id'] for row in manifest_rows
                     if row['attempts'] >= row['max_attempts']]
        if exhausted:
            raise SystemExit('pending manifest job(s) exhausted attempts: %s'
                             % ','.join(exhausted))
        required_slots = {row['profile_slot'] for row in manifest_rows}
        eligible_slots = {account['name'] for account in accounts}
        unavailable = sorted(required_slots - eligible_slots)
        if unavailable:
            raise SystemExit('pending manifest profile(s) have no eligible/probed account: %s'
                             % ','.join(unavailable))
        placeholders = ','.join('?' for _ in required_slots)
        db = connect(args.db)
        busy_rows = list(db.execute(
            "SELECT assigned_acc,external_id FROM jobs WHERE state='in_progress' "
            "AND assigned_acc IN (%s) ORDER BY id" % placeholders,
            tuple(sorted(required_slots))))
        db.close()
        if busy_rows:
            detail = ','.join('%s:%s' % (row['assigned_acc'], row['external_id'])
                              for row in busy_rows)
            raise SystemExit('pending manifest profile(s) are busy with active job(s): %s' % detail)
        # Filter before the 3/4 concurrency slice. Otherwise alphabetically earlier accounts that
        # own no pending job can cut a required later slot out of the dispatch pass forever.
        accounts = [account for account in accounts if account['name'] in required_slots]
        accounts = accounts[:4 if runtime_mode == 'staged' else 3]
    work = []
    for acc in accounts:
        job = claim(args.db, acc['name'],
                    only_external_ids=getattr(args, 'only_external_ids', None))
        if job:
            work.append((acc, job))
    if not work:
        print('no runnable jobs')
        return
    runtime_jobs = [job for _account, job in work if job['manifest_path']]
    if runtime_jobs:
        try:
            required_call_ledger(args, context='run-once manifest dispatch')
            bind_jobs_to_run(args.db, runtime_jobs, getattr(args, 'run_id', None))
        except (SystemExit, ValueError) as exc:
            release_db_claims(args.db, [job for _account, job in work], str(exc))
            raise SystemExit(str(exc))
        begin = ['begin-run', '--mode', runtime_mode]
        run_id = getattr(args, 'run_id', None)
        receipt = getattr(args, 'probe_receipt', None)
        if run_id:
            begin += ['--run-id', run_id]
        if receipt:
            begin += ['--probe-receipt', receipt]
        for job in runtime_jobs:
            begin += ['--lease-id', coordinator_lease_id(job['external_id'])]
        try:
            coordinator_command(args, begin)
        except SystemExit as exc:
            release_db_claims(args.db, [job for _account, job in work], str(exc))
            raise
    claude_bin = getattr(args, 'claude_bin', 'claude')
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(work)) as pool:
        futures = {}
        for acc, job in work:
            base = (args.db, acc['name'], acc['config_dir'], job, args.timeout,
                    getattr(args, 'events', None), getattr(args, 'run_id', None), claude_bin)
            reservation_path = getattr(args, 'call_reservation', None)
            future = (pool.submit(run_claimed, *base, reservation_path,
                                  getattr(args, 'max_calls', None))
                      if reservation_path else pool.submit(run_claimed, *base))
            futures[future] = (acc['name'], job)
        for future in concurrent.futures.as_completed(futures):
            acc, job = futures[future]
            try:
                outcome = future.result()
            except BaseException as exc:
                outcome = fail_or_retry(args.db, job['id'], 1, str(exc), 'orchestrator')
            if job['manifest_path'] and outcome != 'done':
                release = release_runtime(
                    args, job['external_id'], 'worker outcome %s on profile %s' % (outcome, acc))
                if release.returncode:
                    raise SystemExit('%s: runtime release failed: %s' %
                                     (job['external_id'], release.stderr or release.stdout))
            print('%s %s -> %s' % (acc, job['external_id'], outcome))


def cmd_status(args):
    db = connect(args.db)
    for row in db.execute('SELECT state, count(*) AS n FROM jobs GROUP BY state ORDER BY state'):
        print('jobs %-12s %d' % (row['state'], row['n']))
    for row in db.execute('SELECT name,parked_until,last_error FROM accounts ORDER BY name'):
        print('account %-8s parked_until=%s error=%s' % (row['name'], row['parked_until'], row['last_error'] or '-'))
    db.close()


EXACT_GEN_MODEL = 'claude-sonnet-5'      # D-F: exact generation model under test
PROBE_MIN_PAYLOAD_BYTES = 5000           # D-F: repository >=5 KB load-representative floor
# D-F: health ceiling; a probe reading over this parks the account (probe_fleet) and is NO-GO.
# MG ruling 31-07-2026: 30 000 -> 65 000. This is the PRODUCTION ceiling -- the one that decides
# whether a paid window may dispatch to c4 -- and is deliberately a separate decision from the
# gate probe's, made only after the gate ruling proved insufficient on its own.
#
# Measured basis (c4 gate log, four dated readings): 52 815 (15-07) · 104 870 (16-07) ·
# 31 623 (31-07 12:05) · 47 953 (31-07 13:07). 65 000 clears today's whole observed band with
# ~35 % headroom over its worst reading, where the earlier 33 000 sat BELOW that worst reading
# and so could only flap. It does NOT clear 16-07's 104 870 ms -- stated rather than smoothed
# over: this buys the CURRENT band, not every band c4 has ever shown.
#
# What this does and does not do: it decides whether dispatch is ALLOWED, never how fast the
# route is. At ~32-48 s per call a window still costs roughly that per card; raising the ceiling
# converts a hard block into a throughput cost, which is the trade being made deliberately in
# order to start translating. If readings return to the 16-07 regime this parks c4 again, by
# design.
PROBE_LATENCY_CEILING_MS = 65000
PROBE_POLICY = 'production_v1'
PROBE_LANE = 'claude-cli-headless/readiness-schema'
PROBE_RECEIPT_SCHEMA = 'pwg.runtime_probe_receipt.v1'
# GAP #5 (four-profile): an account dropped by --drop-unhealthy is parked far in the future so the
# dispatch loop's runnable/claim gates exclude it while the fleet proceeds on the healthy subset.
# Only the explicit opt-in ever parks this way; the default STOP-on-any-NO-GO path never drops.
PARKED_FOREVER = 2147483647              # ~2038; a 10-digit epoch, safely "never" vs. any real reset
# (>=5 KB applies to the INPUT payload; the probe validates the OUTPUT by result-envelope structure,
# not by size -- a valid success wrapper with the small {"ok":true} schema result is fine.)


def _probe_err_class(text):
    """Classify an error blob as 'auth' or 'rate_limit' if its text says so, else None. Used for
    BOTH non-zero rc and rc=0 error wrappers — the CLI may report auth/rate-limit with rc=0."""
    if re.search(r'401|authenticat|not logged in|invalid.*credential', text or '', re.I):
        return 'auth'
    if RATE_LIMIT.search(text or ''):
        return 'rate_limit'
    return None


# D-P (H994): the readiness payload is a real, completable task, NOT a degenerate tool-demand.
# The prior probe (``'Return JSON {ok:true}. Preserve this padding as inert input.' + N*'x'``) read
# as a nonsensical "call this tool now, here is meaningless padding" instruction and tripped
# Sonnet-5's ``--permission-mode plan`` refusal — the model answered with prose citing plan-mode's
# "end your turn via AskUserQuestion" rule (structured_output None), a FALSE ``malformed``/``content``/
# over-ceiling NO-GO on a genuinely healthy, fast profile (measured 15-07-2026 on c4: the degenerate
# prompt refused in 54 s, a natural prompt returned {"ok": true} in 12 s). The fix keeps plan mode
# (so the probe matches ``headless_worker.call``'s real generation invocation) and the >=5 KB INPUT
# payload, but frames it as natural, domain-shaped filler with one unambiguous instruction.
_PROBE_FILLER_UNIT = (
    'Reference sample text: the Petersburg Sanskrit dictionary records each headword with '
    'grammatical notes, source citations, and numbered German senses. ')


def _probe_prompt(payload_bytes):
    """A load-representative readiness prompt: one clear task (return {"ok": true}) plus >=payload_bytes
    of inert, domain-shaped filler explicitly framed as ignorable. Deterministic (fixed filler unit)."""
    reps = payload_bytes // len(_PROBE_FILLER_UNIT) + 1
    filler = (_PROBE_FILLER_UNIT * reps)[:payload_bytes]
    return ('You are a readiness probe for an automated translation service. Confirm the service is '
            'responding by replying with exactly the JSON object {"ok": true} and nothing else. The '
            'block below is inert sample text included only to size the request to a realistic payload; '
            'do not analyse, translate, or act on it.\n\n--- inert sample (ignore) ---\n' + filler)


def _probe_call(config_dir, claude, payload_bytes, model, call_reservation=None,
                reservation_purpose='probe', account=None, active_claim=None):
    """One raw >=5 KB exact-model probe call. Returns (latency_ms, classification, output_bytes);
    classification is 'success' | 'auth' | 'rate_limit' | 'malformed' | 'content' | 'process' |
    'timeout'. NEVER raises on a non-zero rc — the two-phase gate (``live_probe``) decides what to
    STOP on. rc 0 alone is NOT enough: the Claude CLI result envelope must indicate success AND
    carry the structured schema result {"ok": true}."""
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    if call_reservation is None:
        raise ValueError('paid probe requires a call reservation ledger')
    fingerprint = config_dir_fingerprint(config_dir)
    if active_claim is None:
        # The raw primitive is safe even when called directly. live_probe passes
        # one outer claim to both calls so nothing can interleave between them.
        with ActiveCallClaim(fingerprint) as claim:
            return _probe_call(
                config_dir, claude, payload_bytes, model, call_reservation,
                reservation_purpose, account, active_claim=claim)
    if (not isinstance(active_claim, ActiveCallClaim)
            or not active_claim.is_live_canonical_for(fingerprint)):
        raise ValueError('probe active-call claim does not bind config directory')
    prompt = _probe_prompt(payload_bytes)
    reservation = call_reservation.reserve(
        reservation_purpose, profile=account)
    started = time.monotonic()
    try:
        proc = run_tree_kill(            # D-J: tree-kill on timeout
            claude_argv_prefix(claude) + ['-p', '--output-format', 'json', '--json-schema',
             '{"type":"object","properties":{"ok":{"type":"boolean"}},"required":["ok"],"additionalProperties":false}',
             '--model', model, '--permission-mode', 'plan'],
            input=prompt, env=env, text=True, encoding='utf-8', capture_output=True, timeout=300)
    except subprocess.TimeoutExpired as exc:
        call_reservation.finalize(reservation, unevaluable_telemetry())
        # H2056 / #944: this was the ONLY exit from _probe_call that skipped _probe_err_class, so a
        # rate-limited profile — which hangs instead of returning 429 (FINDINGS §270) — was reported
        # as a bare 'timeout'. The gate then read that as a connection/process fault and sent the
        # operator down a branch of the exclusion ladder that §266-271 already closed. run_tree_kill
        # attaches the killed child's output (#943), so the provider's message is classifiable here;
        # 'timeout' remains the fall-through when nothing account-level was said.
        return (int((time.monotonic() - started) * 1000),
                (_probe_err_class(timeout_output_text(exc)) or 'timeout'), 0)
    except BaseException:
        call_reservation.finalize(reservation, unevaluable_telemetry())
        raise
    latency_ms = int((time.monotonic() - started) * 1000)
    out = proc.stdout or ''
    combined = out + '\n' + (proc.stderr or '')
    output_bytes = len(out.encode('utf-8'))
    try:
        wrapper = json.loads(out)
    except (ValueError, TypeError):
        wrapper = None
    telemetry = telemetry_from_cli_wrapper(wrapper)
    if proc.returncode:
        call_reservation.finalize(reservation, telemetry)
        return latency_ms, (_probe_err_class(combined) or 'process'), output_bytes
    # rc 0 is NOT sufficient. `claude -p --output-format json` returns the CLI result *envelope*
    # ({"type":"result","subtype":"success","is_error":false,"result":..., "structured_output":...}).
    # Validate it strictly and require the structured schema result {"ok": true}.
    if wrapper is None:
        call_reservation.finalize(
            reservation, dict(telemetry, cost_evaluable=False))
        return latency_ms, 'malformed', output_bytes
    if not isinstance(wrapper, dict) or wrapper.get('type') != 'result':
        call_reservation.finalize(
            reservation, dict(telemetry, cost_evaluable=False))
        return latency_ms, 'malformed', output_bytes            # not the CLI result envelope
    if wrapper.get('subtype') != 'success' or wrapper.get('is_error'):
        # a valid envelope reporting an ERROR (with rc 0) — it may still carry auth/rate-limit text
        call_reservation.finalize(reservation, telemetry)
        return latency_ms, (_probe_err_class(json.dumps(wrapper, ensure_ascii=False)) or 'process'), output_bytes
    # extract the structured schema result: `structured_output`, else `result` when it is a JSON
    # string (or already a dict).
    payload = wrapper.get('structured_output')
    if payload is None:
        res = wrapper.get('result')
        if isinstance(res, str):
            try:
                payload = json.loads(res)
            except (ValueError, TypeError):
                payload = None
        elif isinstance(res, dict):
            payload = res
    if not isinstance(payload, dict) or 'ok' not in payload:
        call_reservation.finalize(
            reservation, dict(telemetry, cost_evaluable=False))
        return latency_ms, 'malformed', output_bytes            # missing / invalid structured result
    if payload.get('ok') is not True:
        call_reservation.finalize(reservation, telemetry)
        return latency_ms, 'content', output_bytes              # {"ok": false} -> content, never success
    call_reservation.finalize(reservation, telemetry)
    return latency_ms, 'success', output_bytes


def live_probe(config_dir, claude='claude', payload_bytes=6491, model=EXACT_GEN_MODEL,
               latency_ceiling_ms=PROBE_LATENCY_CEILING_MS, events_path=None, run_id=None,
               account=None, call_reservation=None):
    """D-K deterministic two-phase probe protocol (ceiling unchanged at 30000 ms). Runs EXACTLY
    one warm-up call (same profile + exact model; its latency is EXCLUDED from the acceptance
    gate — it only stabilizes the cold connection), then IMMEDIATELY EXACTLY one measured >=5 KB
    (INPUT payload) probe that IS gated. PASS only when the measured call has rc 0, its Claude CLI
    result envelope validates (type=result / subtype=success / not is_error) with the structured
    schema result {"ok": true}, the model is exact, and latency <= ceiling. A warm-up failure
    (auth/model/malformed/content/rate-limit/timeout) is an immediate STOP; a failed or over-ceiling
    MEASURED probe is an honest NO-GO with NO retry and no manual pre-warming. Both calls are
    recorded separately in telemetry (purpose warmup / measured), and the warm-up latency never
    enters the census."""
    if payload_bytes < PROBE_MIN_PAYLOAD_BYTES:
        raise SystemExit('probe payload %d B < %d B repository floor' %
                         (payload_bytes, PROBE_MIN_PAYLOAD_BYTES))
    if model != EXACT_GEN_MODEL:
        raise SystemExit('probe model %r is not the exact generation model %r' % (model, EXACT_GEN_MODEL))
    if call_reservation is None:
        raise ValueError('paid probe requires a call reservation ledger')

    def _emit(purpose, latency, cls, obytes):
        if events_path:
            append_event(events_path, run_id=run_id, account=account, stage='probe',
                         event='probe_call', purpose=purpose, elapsed_ms=latency,
                         model=model, output_bytes=obytes, classification=cls,
                         policy=PROBE_POLICY, executor_lane=PROBE_LANE,
                         schema_valid=(cls == 'success'))

    # One profile claim covers the WHOLE pair. Releasing between warmup and measured allowed
    # another paid worker to interleave on the same config directory and invalidated the reading.
    with ActiveCallClaim(config_dir_fingerprint(config_dir)) as active_claim:
        warm_ms, warm_cls, warm_bytes = _probe_call(
            config_dir, claude, payload_bytes, model, call_reservation,
            'probe:warmup', account, active_claim=active_claim)
        _emit('warmup', warm_ms, warm_cls, warm_bytes)
        if warm_cls != 'success':
            raise SystemExit('warm-up probe %s -> STOP (auth/model/output/rate-limit/timeout)' % warm_cls)

        meas_ms, meas_cls, meas_bytes = _probe_call(
            config_dir, claude, payload_bytes, model, call_reservation,
            'probe:measured', account, active_claim=active_claim)
        _emit('measured', meas_ms, meas_cls, meas_bytes)
        if meas_cls != 'success':
            raise SystemExit('measured probe %s -> honest NO-GO (no retry, no re-warm)' % meas_cls)
        if meas_ms >= latency_ceiling_ms:
            raise SystemExit('measured probe latency %d ms is not below %d ms health ceiling — honest NO-GO '
                             '(warm-up already done; no re-roll)' % (meas_ms, latency_ceiling_ms))
    return meas_ms


def probe_fleet(accounts, claude='claude', payload_bytes=6491, model=EXACT_GEN_MODEL,
                latency_ceiling_ms=PROBE_LATENCY_CEILING_MS, events_path=None, run_id=None,
                drop_unhealthy=False, call_reservation=None):
    """GAP #5 (four-profile): probe EACH validated account through the D-K two-phase ``live_probe``
    (exactly one warm-up + one measured >=5 KB call per account, with each account's warm-up latency
    EXCLUDED from the census — a 4-profile fleet therefore yields exactly 4 measured latency samples,
    not 8, so the acceptance census is not inflated). Every call is emitted with ``purpose`` warmup /
    measured and its own ``account`` label. Returns an ordered ``name -> measured_ms`` map for the
    accounts that passed — this map is what ``report['probe_latency_ms']`` is rewired from.

    DEFAULT policy is STOP-on-any-NO-GO: the first account whose probe fails (a warm-up STOP, a
    measured NO-GO, or an over-ceiling reading) aborts the WHOLE fleet by propagating the
    ``live_probe`` ``SystemExit`` — matching acceptance #1 ("four profile probes succeed") and the
    existing honest-NO-GO stance. ``drop_unhealthy=True`` is the explicit opt-in to instead DROP a
    failing account and continue on the healthy subset (still requiring >=1 healthy account); the
    caller parks the dropped accounts so dispatch proceeds only on the survivors.

    N==1 is a pure pass-through: ``probe_fleet([acc])`` returns ``{acc: live_probe(acc.config_dir,
    ...)}`` and the single measured latency is identical to the pre-N-profile
    ``live_probe(accounts[0])`` reading — the Windows-100 single-profile path is unchanged."""
    latencies = {}
    for acc in accounts:
        name = acc['name']
        try:
            latencies[name] = live_probe(acc['config_dir'], claude, payload_bytes=payload_bytes,
                                         model=model, latency_ceiling_ms=latency_ceiling_ms,
                                         events_path=events_path, run_id=run_id, account=name,
                                         call_reservation=call_reservation)
        except SystemExit as exc:
            if not drop_unhealthy:
                # STOP-on-any-NO-GO: one unhealthy profile fails the whole fleet (honest NO-GO).
                raise SystemExit('fleet probe STOP on account %s: %s' % (name, exc))
            # explicit opt-in: drop this account and proceed on the healthy subset.
    if not latencies:
        raise SystemExit('fleet probe: no healthy validated account (probed %d)' % len(accounts))
    return latencies


def staged_plan_scope(plan, requested_lease_ids=None):
    """Return the prepared headless windows that define one staged acceptance run."""
    prepared = [window for window in plan.get('windows', []) if window.get('headless')]
    prepared_ids = [window['root'] for window in prepared]
    if requested_lease_ids and set(requested_lease_ids) != set(prepared_ids):
        raise SystemExit('--lease-id set does not match the staged plan')
    lease_ids = list(requested_lease_ids or prepared_ids)
    lease_scope = set(lease_ids)
    windows = [window for window in prepared if window['root'] in lease_scope]
    return {
        'lease_ids': lease_ids,
        'windows': windows,
        'expected_windows': len(windows),
        'expected_headwords': sum(len(window.get('headwords') or []) for window in windows),
    }


STAGED_RUN_IDLE_POLL_SECONDS = 3   # C4: backoff between no-progress staged-run passes (see loop)


def cmd_staged_run(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    scope = staged_plan_scope(plan, args.lease_id)
    lease_ids = scope['lease_ids']
    expected_windows = scope['expected_windows']
    expected_headwords = scope['expected_headwords']
    if not expected_windows or not expected_headwords:
        raise SystemExit('staged plan has no prepared headless windows')
    db = connect(args.db)
    accounts = list(db.execute('SELECT * FROM accounts WHERE validated=1 ORDER BY name'))
    db.close()
    if getattr(args, 'only_profile', None):
        accounts = [account for account in accounts if account['name'] == args.only_profile]
        if not accounts:
            raise SystemExit('--only-profile is not a validated roster slot')
    # GAP #5 (four-profile): the staged run now fans across N validated profiles instead of hard-
    # capping at one. Require >=1 (a zero-account run has nothing to probe or dispatch); --max-
    # accounts optionally caps the fleet. N==1 remains the exact single-profile Windows-100 path.
    if not accounts:
        raise SystemExit('Windows staged-run requires at least one validated account')
    if getattr(args, 'max_accounts', 0):
        accounts = accounts[:args.max_accounts]
    preflight_cmd = ['validate-preflight']
    for lease_id in sorted(lease_ids):
        preflight_cmd += ['--lease-id', lease_id]
    preflight = coordinator_command(args, preflight_cmd, check=False)
    if preflight.returncode:
        raise SystemExit('staged-run preflight refused before probe: %s'
                         % (preflight.stderr or preflight.stdout)[-2000:])
    reservation_path = getattr(args, 'call_reservation', None)
    if not reservation_path:
        raise SystemExit('staged-run requires --call-reservation')
    run_id = args.run_id
    if getattr(args, 'resume', False):
        if not os.path.exists(reservation_path):
            raise SystemExit('staged-run --resume requires the existing call ledger')
        known = run_ids(reservation_path)
        if run_id and run_id not in known:
            raise SystemExit('staged-run --resume run-id is absent from the call ledger')
        if not run_id and len(known) == 1:
            run_id = known[0]
        elif not run_id:
            raise SystemExit('staged-run --resume requires --run-id for a multi-run ledger')
    run_id = run_id or ('win100-' + now_iso().replace(':', '').replace('-', ''))
    args.run_id = run_id
    call_ledger = required_call_ledger(args, context='staged-run')
    if getattr(args, 'resume', False):
        cmd_recover(argparse.Namespace(
            db=args.db, coordinator=args.coordinator, coord_dir=args.coord_dir,
            cwd=args.cwd, only_external_ids=set(lease_ids)))
    # Probe EVERY validated account (D-K warmup+measured per account; census not inflated). DEFAULT
    # STOP-on-any-NO-GO; --drop-unhealthy opts into proceeding on the healthy subset, parking the
    # dropped accounts so the dispatch loop below claims only survivors.
    probe_latencies = probe_fleet(accounts, args.claude_bin, events_path=args.events,
                                  run_id=run_id,
                                  drop_unhealthy=getattr(args, 'drop_unhealthy', False),
                                  call_reservation=call_ledger)
    probe_receipt = write_probe_receipt(
        args.coord_dir, run_id, lease_ids, probe_latencies)
    if getattr(args, 'drop_unhealthy', False):
        for acc in accounts:
            if acc['name'] not in probe_latencies:
                park(args.db, acc['name'], PARKED_FOREVER,
                     'dropped after probe NO-GO (--drop-unhealthy); healthy subset proceeds')
    db = connect(args.db)
    existing_jobs = {row['external_id'] for row in db.execute('SELECT external_id FROM jobs')}
    db.close()
    coord_state = json.load(open(os.path.join(os.path.abspath(args.coord_dir), 'state.json'),
                                 encoding='utf-8'))
    prepared_ids = {lease['id'] for lease in coord_state.get('leases', [])
                    if lease.get('state') == 'prepared'}
    to_import = [lease_id for lease_id in lease_ids
                 if lease_id not in existing_jobs and lease_id in prepared_ids]
    if to_import:
        import_args = argparse.Namespace(db=args.db, coord_dir=args.coord_dir, cwd=args.cwd,
                                         lease_id=to_import, max_attempts=2)
        cmd_import_coordinator(import_args)
    lease_scope = set(lease_ids)
    db = connect(args.db)
    completed_before = scoped_job_count(db, lease_scope, "state='done'")
    db.close()
    started = time.monotonic()
    # C4 backstop: forward progress = a pending job drained or a done window recorded. If a full
    # pass changes none of (pending, done_unrecorded, completed_before) while accounts are
    # runnable — e.g. a job that no dispatchable account can claim — the loop must poll, not
    # hot-spin. The primary C4 fix (requeue_rate_limited decrements attempts) removes the usual
    # source of an unclaimable-but-pending job; this only guards any residual case.
    prev_progress_sig = None
    while True:
        db = connect(args.db)
        pending = scoped_job_count(db, lease_scope, "state='pending'")
        done_unrecorded = scoped_job_count(
            db, lease_scope, "state='done' AND coordinator_recorded=0")
        failed = scoped_job_count(db, lease_scope, "state='failed'")
        db.close()
        if failed:
            # H1386 P3c: name the failed jobs' FULL external_ids -- the reset-failed
            # recovery needs the exact id (a requeue attempt is '<lease>::rqNN-<kind>').
            db = connect(args.db)
            failed_ids = [j['external_id'] for j in
                          scoped_jobs(db, lease_scope, "state='failed'")]
            db.close()
            raise SystemExit('staged-run stopped: failed jobs=%d (%s) -- recover with '
                             'reset-failed --lease-id <id> --reason "..."'
                             % (failed, ', '.join(sorted(failed_ids))))
        if not pending and not done_unrecorded:
            break
        if pending:
            now_ts = int(time.time())
            db = connect(args.db)
            runnable = db.execute("SELECT count(*) FROM accounts WHERE validated=1 AND parked_until<=?",
                                  (now_ts,)).fetchone()[0]
            earliest = db.execute("SELECT min(parked_until) FROM accounts WHERE validated=1").fetchone()[0]
            db.close()
            if not runnable:
                # D-D: every account is parked while jobs remain pending. The old loop
                # had no sleep/exit here and busy-spun indefinitely (H818 acceptance).
                write_census(args.events, args.census)
                raise SystemExit('staged-run halted: %d job(s) pending but all accounts parked '
                                 'until %s; rerun with --resume after the reset' % (pending, earliest))
            # C4 backstop: runnable accounts exist but the previous pass drained nothing — poll
            # instead of hot-spinning. (`prev_progress_sig` is this pass's entry state; if it
            # equals the previous pass's entry state, that pass made no progress.)
            progress_sig = (pending, done_unrecorded, completed_before)
            if progress_sig == prev_progress_sig:
                time.sleep(STAGED_RUN_IDLE_POLL_SECONDS)
            prev_progress_sig = progress_sig
            cmd_run_once(argparse.Namespace(db=args.db, timeout=args.timeout,
                                             events=args.events, run_id=run_id,
                                             claude_bin=args.claude_bin,
                                             coordinator=args.coordinator,
                                             coord_dir=args.coord_dir,
                                             cwd=args.cwd,
                                             runtime_mode='staged',
                                             probe_receipt=probe_receipt,
                                            # dispatch ONLY to the probed, capped/healthy fleet —
                                            # never to a capped-out or dropped (unprobed) account.
                                            only_accounts=set(probe_latencies),
                                            only_profile=getattr(args, 'only_profile', None),
                                            only_external_ids=lease_scope,
                                            call_reservation=reservation_path,
                                            max_calls=getattr(args, 'max_calls', None)))
        cmd_record_done(argparse.Namespace(db=args.db, coordinator=args.coordinator,
                                           coord_dir=args.coord_dir, cwd=args.cwd,
                                           only_external_ids=lease_scope))
        promote_cmd = ['promote-ready', '--gen-model-version', 'claude-sonnet-5']
        for lease_id in sorted(lease_scope):
            promote_cmd += ['--lease-id', lease_id]
        promote = coordinator_command(args, promote_cmd, check=False)
        if promote.returncode and 'no ready leases to promote' not in (promote.stderr + promote.stdout):
            raise SystemExit('promotion failed: %s' % (promote.stderr or promote.stdout)[-1000:])
        db = connect(args.db)
        done_now = scoped_job_count(db, lease_scope, "state='done'")
        db.close()
        if done_now > completed_before:
            completed_before = done_now
            if args.stop_after and done_now >= args.stop_after:
                print('restart checkpoint reached after %d window(s); rerun with --resume' % done_now)
                return
    db = connect(args.db)
    jobs = scoped_jobs(db, lease_scope)
    db.close()
    outputs = []
    for job in jobs:
        if job['output_path'] and os.path.exists(job['output_path']):
            outputs.append(json.load(open(job['output_path'], encoding='utf-8')))
    cards = sum((payload.get('summary') or {}).get('cards', 0) for payload in outputs)
    clean = sum((payload.get('summary') or {}).get('ok', 0) for payload in outputs)
    failures = {}
    for payload in outputs:
        failures.update((payload.get('summary') or {}).get('failures') or {})
    fidelity = len([v for v in failures.values() if 'fidelity' in str(v)])
    coord_state_path = os.path.join(os.path.abspath(args.coord_dir), 'state.json')
    coord_state = json.load(open(coord_state_path, encoding='utf-8'))
    lease_ids = lease_scope
    audited_clean = sum(int(lease.get('clean_count') or 0)
                        for lease in coord_state.get('leases', [])
                        if lease.get('id') in lease_ids)
    relevant_leases = [lease for lease in coord_state.get('leases', [])
                       if lease.get('id') in lease_ids]
    promotion_deltas = {lease['id']: lease.get('store_delta') for lease in relevant_leases}
    bad_deltas = sorted(lease_id for lease_id, delta in promotion_deltas.items()
                        if delta is None or delta <= 0)
    for lease in relevant_leases:
        append_event(args.events, run_id=run_id, lease_id=lease['id'],
                     window_id=lease['id'], stage='audit', event='audit_end',
                     classification=lease.get('audit_state'), cards=lease.get('workflow_result_count'),
                     clean=lease.get('clean_count'))
        append_event(args.events, run_id=run_id, lease_id=lease['id'],
                     window_id=lease['id'], stage='promotion', event='promotion_end',
                     classification=promotion_classification(lease),
                     store_before=lease.get('store_before'), store_after=lease.get('store_after'))
    selected_keys = []
    headwords = set()
    for job in jobs:
        if job['manifest_path']:
            meta = json.load(open(job['manifest_path'], encoding='utf-8'))['meta']
            selected_keys.extend(meta['selected_keys'])
            keymap = meta.get('nominal_keymap') or {}
            headwords.update(keymap.get(key, key.split('~~', 1)[0]) for key in meta['selected_keys'])
    unique_keys = set(selected_keys)
    result_keys = [row.get('key') for payload in outputs for row in payload.get('results', [])]
    duplicate_results = len(result_keys) - len(set(result_keys))
    unaccounted = sorted(unique_keys - set(result_keys))
    hard_classes = set(HARD_FAILURE_CLASSES)
    hard_failures = sorted({job['failure_class'] for job in jobs if job['failure_class'] in hard_classes})
    for value in failures.values():
        text_value = str(value).lower()
        for classification in hard_classes:
            if classification in text_value or (classification == 'malformed_output' and 'malformed' in text_value):
                hard_failures.append(classification)
    hard_failures = sorted(set(hard_failures))
    model_calls = sum((p.get('summary') or {}).get('translate_agents_spent', 0) +
                      (p.get('summary') or {}).get('heal_agents_spent', 0) for p in outputs)
    model_retries = sum(sum('.retry' in str(item.get('label') or '')
                            for item in ((p.get('summary') or {}).get('headless_attempts') or []))
                        for p in outputs)
    report = {
        'schema': 'pwg.windows100_readiness.v1', 'generated_at': now_iso(),
        'probe_latency_ms': probe_latencies, 'windows': len(outputs),
        'headwords': expected_headwords, 'actual_unique_headwords': len(headwords),
        'subcards': cards, 'expected_subcards': len(selected_keys),
        'model_nonnull': clean, 'audit_clean': audited_clean,
        'residuals': cards - audited_clean,
        'fidelity_rejects': fidelity, 'duplicate_results': duplicate_results,
        'unaccounted_keys': unaccounted, 'hard_failures': hard_failures,
        'model_calls': model_calls, 'model_retries': model_retries,
        'promotion_deltas': promotion_deltas, 'invalid_promotion_deltas': bad_deltas,
        'elapsed_seconds': int(time.monotonic() - started),
        'go': bool(len(outputs) == expected_windows and len(headwords) == expected_headwords and
                   len(unique_keys) == len(selected_keys) and
                   cards == len(selected_keys) and not duplicate_results and not unaccounted and
                   not hard_failures and not bad_deltas and audited_clean / cards >= 0.80 and
                   fidelity / cards < 0.05 and not failed),
    }
    append_event(args.events, run_id=run_id, stage='acceptance', event='run_summary',
                 classification='success' if report['go'] else 'no_go', cards=cards,
                 clean=audited_clean, calls=model_calls, retries=model_retries,
                 fidelity_rejects=fidelity, unaccounted_keys=unaccounted)
    atomic_write(args.report, json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    write_census(args.events, args.census)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if not report['go']:
        raise SystemExit(1)


def cmd_presplit_canary(args):
    try:
        with open(args.manifest, 'rb') as fh:
            manifest_bytes = fh.read()
        manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
        manifest = json.loads(manifest_bytes.decode('utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit('presplit canary manifest is unreadable: %s' % exc)
    try:
        validate_manifest(manifest, require_v2=True)
    except ValueError as exc:
        raise SystemExit('presplit canary preflight: %s' % exc)
    presplit = manifest.get('presplit_keys') or []
    if not presplit:
        raise SystemExit('presplit canary manifest has no presplit_keys')
    db = connect(args.db)
    accounts = list(db.execute('SELECT * FROM accounts WHERE validated=1 ORDER BY name'))
    db.close()
    if len(accounts) != 1:
        raise SystemExit('presplit canary requires exactly one validated account')
    try:
        validate_profile(manifest, accounts[0]['config_dir'], accounts[0]['name'])
    except ValueError as exc:
        raise SystemExit('presplit canary preflight: %s' % exc)
    run_id = args.run_id or ('presplit-' + now_iso().replace(':', '').replace('-', ''))
    args.run_id = run_id
    call_ledger = required_call_ledger(args, context='presplit-canary')
    preflight_path = os.path.abspath(args.preflight)
    validate_preflight_artifact(
        preflight_path, manifest, args.preflight_sha256)
    latency = live_probe(accounts[0]['config_dir'], args.claude_bin,   # D-K: warmup+measured
                         events_path=args.events, run_id=run_id, account=accounts[0]['name'],
                         call_reservation=call_ledger)
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = accounts[0]['config_dir']
    env['PWG_CALL_RESERVATION_PATH'] = os.path.abspath(args.call_reservation)
    env['PWG_CALL_RESERVATION_RUN_ID'] = run_id
    env['PWG_CALL_RESERVATION_MAX_CALLS'] = (
        '' if getattr(args, 'max_calls', None) is None else str(args.max_calls))
    env['PWG_PREFLIGHT_PATH'] = preflight_path
    env['PWG_PREFLIGHT_SHA256'] = args.preflight_sha256
    if sha256_path(args.manifest) != manifest_hash:
        raise SystemExit('presplit canary manifest changed during the health probe')
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'headless_worker.py'),
           os.path.abspath(args.manifest), '--output', os.path.abspath(args.output),
           '--status-out', os.path.abspath(args.status), '--claude-bin', args.claude_bin,
           '--only-profile', accounts[0]['name'],
           '--timeout', str(args.timeout), '--preflight', preflight_path,
           '--preflight-sha256', args.preflight_sha256,
           '--manifest-sha256', manifest_hash]
    proc = run_tree_kill(cmd, env=env, text=True, encoding='utf-8', capture_output=True,
                         timeout=args.timeout)   # D-J: tree-kill on timeout (presplit canary worker)
    status = json.load(open(args.status, encoding='utf-8')) if os.path.exists(args.status) else {}
    canary_base = {'run_id': run_id, 'account': accounts[0]['name'],
                   'manifest_hash': manifest_hash}
    for idx, item in enumerate(status.get('attempts') or []):
        emit_call_events(args.events, item, idx, status.get('manifest_sha256'), canary_base)
    if proc.returncode or status.get('classification') != 'success':
        raise SystemExit('presplit canary NO-GO: %s' %
                         (status.get('classification') or (proc.stderr or proc.stdout)[-500:]))
    if status.get('manifest_sha256') != manifest_hash:
        raise SystemExit('presplit canary NO-GO: worker manifest hash drift')
    try:
        with open(args.output, 'rb') as fh:
            result_bytes = fh.read()
        result_hash = hashlib.sha256(result_bytes).hexdigest()
        payload = json.loads(result_bytes.decode('utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit('presplit canary NO-GO: result is unreadable: %s' % exc)
    if status.get('result_sha256') != result_hash:
        raise SystemExit('presplit canary NO-GO: worker result hash drift')
    if (payload.get('meta') or {}).get(
            'execution_manifest_sha256') != manifest_hash:
        raise SystemExit('presplit canary NO-GO: payload manifest seal is absent/drifted')
    failures = (payload.get('summary') or {}).get('failures') or {}
    if failures or (payload.get('summary') or {}).get('presplit', 0) < 1:
        raise SystemExit('presplit canary NO-GO: residuals or route not exercised')
    append_event(args.events, run_id=run_id, stage='canary', event='run_summary',
                 classification='success', cards=(payload.get('summary') or {}).get('cards'),
                 clean=(payload.get('summary') or {}).get('ok'), calls=
                 (payload.get('summary') or {}).get('heal_agents_spent'))
    print('presplit canary GO: %d key(s)' % len(presplit))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    default_coordinator = os.path.join(os.path.dirname(__file__), 'coordinator.py')
    default_coord_dir = os.path.join(os.path.dirname(__file__), 'output', 'coordinator')
    default_cwd = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    ap.add_argument('--db', default='max_orchestrator.sqlite')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init'); p.add_argument('--account', action='append', required=True); p.add_argument('--claude-bin', default='claude'); p.add_argument('--skip-profile-check', action='store_true', help=argparse.SUPPRESS); p.add_argument('--call-reservation'); p.add_argument('--run-id'); p.add_argument('--max-calls', type=int); p.set_defaults(func=cmd_init)
    p = sub.add_parser('enqueue'); p.add_argument('--external-id', required=True); p.add_argument('--argv-json', required=True); p.add_argument('--cwd', required=True); p.add_argument('--output', required=True); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_enqueue)
    p = sub.add_parser('import-coordinator'); p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True); p.add_argument('--lease-id', action='append'); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_import_coordinator)
    p = sub.add_parser('import-requeue', help='H1339 A4: import one requeue_prepared lease attempt as a runnable job'); p.add_argument('lease_id'); p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True); p.add_argument('--max-attempts', type=int, default=2); p.set_defaults(func=cmd_import_requeue)
    p = sub.add_parser('reset-failed', help='B18: audited scoped recovery of terminal failed jobs (requires --reason)'); p.add_argument('--lease-id', action='append', required=True); p.add_argument('--reason', required=True); p.add_argument('--events'); p.set_defaults(func=cmd_reset_failed)
    p = sub.add_parser('recover'); p.add_argument('--coordinator', default=default_coordinator); p.add_argument('--coord-dir', default=default_coord_dir); p.add_argument('--cwd', default=default_cwd); p.set_defaults(func=cmd_recover)
    p = sub.add_parser('record-done'); p.add_argument('--coordinator', default=default_coordinator); p.add_argument('--coord-dir', default=default_coord_dir); p.add_argument('--cwd', default=default_cwd); p.set_defaults(func=cmd_record_done)
    p = sub.add_parser('run-once'); p.add_argument('--timeout', type=int, default=7200); p.add_argument('--claude-bin', default='claude'); p.add_argument('--only-profile'); p.add_argument('--coordinator', default=default_coordinator); p.add_argument('--coord-dir', default=default_coord_dir); p.add_argument('--cwd', default=default_cwd); p.add_argument('--call-reservation'); p.add_argument('--run-id'); p.add_argument('--max-calls', type=int); p.set_defaults(func=cmd_run_once)
    p = sub.add_parser('status'); p.set_defaults(func=cmd_status)
    p = sub.add_parser('staged-run')
    p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True)
    p.add_argument('--coordinator', required=True); p.add_argument('--lease-id', action='append')
    p.add_argument('--plan', required=True)
    p.add_argument('--claude-bin', default='claude'); p.add_argument('--timeout', type=int, default=7200)
    p.add_argument('--stop-after', type=int, default=0); p.add_argument('--resume', action='store_true')
    p.add_argument('--max-accounts', type=int, default=0)          # GAP #5: cap the validated fleet
    p.add_argument('--only-profile', help='enforce one logical profile slot and its bound directory')
    p.add_argument('--drop-unhealthy', action='store_true')        # GAP #5: proceed on healthy subset
    p.add_argument('--report', required=True)
    p.add_argument('--events', required=True); p.add_argument('--census', required=True)
    p.add_argument('--run-id'); p.add_argument('--call-reservation'); p.add_argument('--max-calls', type=int); p.set_defaults(func=cmd_staged_run)
    p = sub.add_parser('presplit-canary')
    p.add_argument('--manifest', required=True); p.add_argument('--output', required=True)
    p.add_argument('--status', required=True); p.add_argument('--events', required=True)
    p.add_argument('--preflight', required=True)
    p.add_argument('--preflight-sha256', required=True)
    p.add_argument('--run-id'); p.add_argument('--claude-bin', default='claude')
    p.add_argument('--call-reservation'); p.add_argument('--max-calls', type=int)
    p.add_argument('--timeout', type=int, default=7200); p.set_defaults(func=cmd_presplit_canary)
    args = ap.parse_args(argv)
    try:
        args.func(args)
    except CallLimitReached as exc:
        raise SystemExit(str(exc))


if __name__ == '__main__':
    main()
