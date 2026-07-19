#!/usr/bin/env python
"""Restartable outer scheduler for independently authenticated Claude profiles.

This layer owns dispatch only.  A queued job is an argv JSON array; the command
is run with CLAUDE_CONFIG_DIR set to the assigned account.  Translation logic,
auditing, and promotion remain owned by coordinator.py and its existing tools.
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
from headless_worker import claude_argv_prefix, run_tree_kill, windows_hidden_flags
from window_common import atomic_write_text
from execution_contract import validate_manifest, validate_profile

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
  manifest_path TEXT, manifest_sha256 TEXT, result_sha256 TEXT, attempt_log_path TEXT,
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
            ('result_sha256', 'TEXT'), ('attempt_log_path', 'TEXT'),
            ('failure_class', 'TEXT'), ('reset_at', 'INTEGER'),
            ('coordinator_recorded', 'INTEGER NOT NULL DEFAULT 0')):
        if name not in existing:
            db.execute('ALTER TABLE jobs ADD COLUMN %s %s' % (name, declaration))
    account_cols = {row[1] for row in db.execute('PRAGMA table_info(accounts)')}
    if 'validated' not in account_cols:
        db.execute('ALTER TABLE accounts ADD COLUMN validated INTEGER NOT NULL DEFAULT 0')
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
        "SELECT * FROM jobs WHERE state='pending' AND attempts < max_attempts%s "
        "ORDER BY id LIMIT 1" % scope_sql, scope_args).fetchone()
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
           result_sha256=None, attempt_log_path=None, reset_at=None):
    db = connect(db_path)
    with db:
        db.execute('UPDATE jobs SET state=?, returncode=?, error=?, failure_class=?, '
                   'result_sha256=COALESCE(?,result_sha256), attempt_log_path=COALESCE(?,attempt_log_path), '
                   'reset_at=?, finished_at=? WHERE id=?',
                   (state, returncode, error, failure_class, result_sha256,
                    attempt_log_path, reset_at, now_iso(), job_id))
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


def park(db_path, account, until, error):
    db = connect(db_path)
    with db:
        db.execute('UPDATE accounts SET parked_until=?, last_error=?, updated_at=? WHERE name=?',
                   (until, error[-2000:], now_iso(), account))
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
                claude_bin='claude'):
    attempt = job['attempts']
    attempt_log = job['output_path'] + '.attempt%d.runner.json' % attempt
    status_path = job['output_path'] + '.attempt%d.status.json' % attempt
    event_base = {'run_id': run_id, 'lease_id': job['external_id'],
                  'window_id': job['external_id'], 'attempt': attempt,
                  'account': account, 'manifest_hash': job['manifest_sha256']}
    if events_path:
        append_event(events_path, stage='dispatch', event='attempt_start', **event_base)
    if job['manifest_path']:
        if sha256_path(job['manifest_path']) != job['manifest_sha256']:
            return fail_or_retry(db_path, job['id'], 2, 'manifest hash changed',
                                 'manifest_drift', attempt_log)
        manifest = json.load(open(job['manifest_path'], encoding='utf-8'))
        try:
            validate_profile(manifest, config_dir, account)
        except ValueError as exc:
            return fail_or_retry(db_path, job['id'], 2, str(exc), 'configuration', attempt_log)
        argv = [sys.executable, os.path.join(os.path.dirname(__file__), 'headless_worker.py'),
                job['manifest_path'], '--output', job['output_path'],
                '--status-out', status_path, '--timeout', str(timeout),
                '--claude-bin', claude_bin, '--only-profile', account]
    else:
        argv = json.loads(job['argv_json'])
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
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
        if events_path:
            for idx, item in enumerate(worker_status.get('attempts') or []):
                emit_call_events(events_path, item, idx,
                                 worker_status.get('manifest_sha256'), event_base)
        failure_class = worker_status.get('classification')
        if is_rate_limited(worker_status, proc.stderr):
            reset_text = (proc.stderr or '') + '\n' + (worker_status.get('error') or '')
            until = parse_reset(reset_text)
            park(db_path, account, until, reset_text)
            finish(db_path, job['id'], 'pending', proc.returncode,
                   'rate-limited; account parked', 'rate_limit',
                   attempt_log_path=attempt_log, reset_at=until)
            if events_path:
                append_event(events_path, stage='dispatch', event='attempt_end',
                             classification='rate_limit', reset_at=until, **event_base)
            return 'parked'
        if proc.returncode == 0:
            result_hash = sha256_path(job['output_path']) if os.path.exists(job['output_path']) else None
            finish(db_path, job['id'], 'done', 0, failure_class='success',
                   result_sha256=result_hash, attempt_log_path=attempt_log)
            if events_path:
                append_event(events_path, stage='dispatch', event='attempt_end',
                             classification='success', result_hash=result_hash, **event_base)
            return 'done'
        state = fail_or_retry(db_path, job['id'], proc.returncode, combined[-2000:],
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


def profile_status(config_dir, claude='claude'):
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
    probe = run_tree_kill(               # D-J: tree-kill on timeout
        claude_argv_prefix(claude) + ['-p', 'Return exactly OK.', '--output-format', 'json',
         '--model', 'claude-sonnet-5', '--permission-mode', 'plan'],
        env=env, text=True, encoding='utf-8', capture_output=True, timeout=60)
    if probe.returncode:
        return False, ((probe.stderr or '') + '\n' + (probe.stdout or ''))[-500:]
    return True, data.get('subscriptionType') or 'unknown'


def cmd_init(args):
    db = connect(args.db)
    with db:
        for item in args.account:
            name, config_dir = item.split('=', 1)
            config_dir = os.path.abspath(config_dir)
            ok, detail = (True, 'test override') if args.skip_profile_check else profile_status(config_dir, args.claude_bin)
            if not ok:
                raise SystemExit('%s: profile validation failed: %s' % (name, detail))
            db.execute('INSERT OR REPLACE INTO accounts(name,config_dir,parked_until,last_error,validated,updated_at) VALUES(?,?,0,NULL,1,?)',
                       (name, config_dir, now_iso()))
    db.close()


def cmd_enqueue(args):
    argv = json.loads(args.argv_json)
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
        raise SystemExit('--argv-json must be a non-empty JSON string array')
    db = connect(args.db)
    with db:
        db.execute('INSERT INTO jobs(external_id,argv_json,cwd,output_path,max_attempts) VALUES(?,?,?,?,?)',
                   (args.external_id, json.dumps(argv), os.path.abspath(args.cwd),
                    os.path.abspath(args.output), args.max_attempts))
    db.close()


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
            keys = set(manifest['meta']['selected_keys'])
            overlap = keys & occupied
            if overlap:
                raise SystemExit('%s: key overlap with queued/done job: %s' %
                                 (lease['id'], ','.join(sorted(overlap))))
            output = os.path.join(lease['artifact_dir'], 'workflow_result.headless.%s.json' % lease['id'])
            db.execute('INSERT INTO jobs(external_id,cwd,output_path,manifest_path,manifest_sha256,max_attempts) VALUES(?,?,?,?,?,?)',
                       (lease['id'], os.path.abspath(args.cwd), output, manifest_path,
                        sha256_path(manifest_path), args.max_attempts))
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
        db.execute('INSERT INTO jobs(external_id,cwd,output_path,manifest_path,manifest_sha256,max_attempts) VALUES(?,?,?,?,?,?)',
                   (external_id, os.path.abspath(args.cwd), output, manifest_path,
                    sha256_path(manifest_path), args.max_attempts))
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
        proc = coordinator_command(
            args, ['record-output', coordinator_lease_id(job['external_id']),
                   job['output_path']], check=False)
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
    manifest_pending = scoped_job_count(
        db, getattr(args, 'only_external_ids', None),
        "state='pending' AND manifest_path IS NOT NULL")
    db.close()
    if manifest_pending:
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
        futures = {pool.submit(run_claimed, args.db, acc['name'], acc['config_dir'], job, args.timeout,
                               getattr(args, 'events', None), getattr(args, 'run_id', None), claude_bin):
                   (acc['name'], job) for acc, job in work}
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
PROBE_LATENCY_CEILING_MS = 30000         # D-F: health ceiling; a reading over this is NO-GO
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


def _probe_call(config_dir, claude, payload_bytes, model):
    """One raw >=5 KB exact-model probe call. Returns (latency_ms, classification, output_bytes);
    classification is 'success' | 'auth' | 'rate_limit' | 'malformed' | 'content' | 'process' |
    'timeout'. NEVER raises on a non-zero rc — the two-phase gate (``live_probe``) decides what to
    STOP on. rc 0 alone is NOT enough: the Claude CLI result envelope must indicate success AND
    carry the structured schema result {"ok": true}."""
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    prompt = _probe_prompt(payload_bytes)
    started = time.monotonic()
    try:
        proc = run_tree_kill(            # D-J: tree-kill on timeout
            claude_argv_prefix(claude) + ['-p', '--output-format', 'json', '--json-schema',
             '{"type":"object","properties":{"ok":{"type":"boolean"}},"required":["ok"],"additionalProperties":false}',
             '--model', model, '--permission-mode', 'plan'],
            input=prompt, env=env, text=True, encoding='utf-8', capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return int((time.monotonic() - started) * 1000), 'timeout', 0
    latency_ms = int((time.monotonic() - started) * 1000)
    out = proc.stdout or ''
    combined = out + '\n' + (proc.stderr or '')
    output_bytes = len(out.encode('utf-8'))
    if proc.returncode:
        return latency_ms, (_probe_err_class(combined) or 'process'), output_bytes
    # rc 0 is NOT sufficient. `claude -p --output-format json` returns the CLI result *envelope*
    # ({"type":"result","subtype":"success","is_error":false,"result":..., "structured_output":...}).
    # Validate it strictly and require the structured schema result {"ok": true}.
    try:
        wrapper = json.loads(out)
    except (ValueError, TypeError):
        return latency_ms, 'malformed', output_bytes
    if not isinstance(wrapper, dict) or wrapper.get('type') != 'result':
        return latency_ms, 'malformed', output_bytes            # not the CLI result envelope
    if wrapper.get('subtype') != 'success' or wrapper.get('is_error'):
        # a valid envelope reporting an ERROR (with rc 0) — it may still carry auth/rate-limit text
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
        return latency_ms, 'malformed', output_bytes            # missing / invalid structured result
    if payload.get('ok') is not True:
        return latency_ms, 'content', output_bytes              # {"ok": false} -> content, never success
    return latency_ms, 'success', output_bytes


def live_probe(config_dir, claude='claude', payload_bytes=6491, model=EXACT_GEN_MODEL,
               latency_ceiling_ms=PROBE_LATENCY_CEILING_MS, events_path=None, run_id=None,
               account=None):
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

    def _emit(purpose, latency, cls, obytes):
        if events_path:
            append_event(events_path, run_id=run_id, account=account, stage='probe',
                         event='probe_call', purpose=purpose, elapsed_ms=latency,
                         model=model, output_bytes=obytes, classification=cls,
                         policy=PROBE_POLICY, executor_lane=PROBE_LANE,
                         schema_valid=(cls == 'success'))

    warm_ms, warm_cls, warm_bytes = _probe_call(config_dir, claude, payload_bytes, model)
    _emit('warmup', warm_ms, warm_cls, warm_bytes)     # excluded from the acceptance latency census
    if warm_cls != 'success':
        raise SystemExit('warm-up probe %s -> STOP (auth/model/output/rate-limit/timeout)' % warm_cls)

    meas_ms, meas_cls, meas_bytes = _probe_call(config_dir, claude, payload_bytes, model)
    _emit('measured', meas_ms, meas_cls, meas_bytes)   # the one gated acceptance reading
    if meas_cls != 'success':
        raise SystemExit('measured probe %s -> honest NO-GO (no retry, no re-warm)' % meas_cls)
    if meas_ms >= latency_ceiling_ms:
        raise SystemExit('measured probe latency %d ms is not below %d ms health ceiling — honest NO-GO '
                         '(warm-up already done; no re-roll)' % (meas_ms, latency_ceiling_ms))
    return meas_ms


def probe_fleet(accounts, claude='claude', payload_bytes=6491, model=EXACT_GEN_MODEL,
                latency_ceiling_ms=PROBE_LATENCY_CEILING_MS, events_path=None, run_id=None,
                drop_unhealthy=False):
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
                                         events_path=events_path, run_id=run_id, account=name)
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
    run_id = args.run_id or ('win100-' + now_iso().replace(':', '').replace('-', ''))
    if getattr(args, 'resume', False):
        cmd_recover(argparse.Namespace(
            db=args.db, coordinator=args.coordinator, coord_dir=args.coord_dir,
            cwd=args.cwd, only_external_ids=set(lease_ids)))
    # Probe EVERY validated account (D-K warmup+measured per account; census not inflated). DEFAULT
    # STOP-on-any-NO-GO; --drop-unhealthy opts into proceeding on the healthy subset, parking the
    # dropped accounts so the dispatch loop below claims only survivors.
    probe_latencies = probe_fleet(accounts, args.claude_bin, events_path=args.events,
                                  run_id=run_id, drop_unhealthy=getattr(args, 'drop_unhealthy', False))
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
    while True:
        db = connect(args.db)
        pending = scoped_job_count(db, lease_scope, "state='pending'")
        done_unrecorded = scoped_job_count(
            db, lease_scope, "state='done' AND coordinator_recorded=0")
        failed = scoped_job_count(db, lease_scope, "state='failed'")
        db.close()
        if failed:
            raise SystemExit('staged-run stopped: failed jobs=%d' % failed)
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
                                            only_external_ids=lease_scope))
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
    hard_classes = {'authentication', 'manifest_drift', 'malformed_output', 'rate_limit'}
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
    manifest = json.load(open(args.manifest, encoding='utf-8'))
    presplit = manifest.get('presplit_keys') or []
    if not presplit:
        raise SystemExit('presplit canary manifest has no presplit_keys')
    db = connect(args.db)
    accounts = list(db.execute('SELECT * FROM accounts WHERE validated=1 ORDER BY name'))
    db.close()
    if len(accounts) != 1:
        raise SystemExit('presplit canary requires exactly one validated account')
    run_id = args.run_id or ('presplit-' + now_iso().replace(':', '').replace('-', ''))
    latency = live_probe(accounts[0]['config_dir'], args.claude_bin,   # D-K: warmup+measured
                         events_path=args.events, run_id=run_id, account=accounts[0]['name'])
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = accounts[0]['config_dir']
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'headless_worker.py'),
           os.path.abspath(args.manifest), '--output', os.path.abspath(args.output),
           '--status-out', os.path.abspath(args.status), '--claude-bin', args.claude_bin,
           '--timeout', str(args.timeout)]
    proc = run_tree_kill(cmd, env=env, text=True, encoding='utf-8', capture_output=True,
                         timeout=args.timeout)   # D-J: tree-kill on timeout (presplit canary worker)
    status = json.load(open(args.status, encoding='utf-8')) if os.path.exists(args.status) else {}
    canary_base = {'run_id': run_id, 'account': accounts[0]['name'],
                   'manifest_hash': status.get('manifest_sha256')}
    for idx, item in enumerate(status.get('attempts') or []):
        emit_call_events(args.events, item, idx, status.get('manifest_sha256'), canary_base)
    if proc.returncode or status.get('classification') != 'success':
        raise SystemExit('presplit canary NO-GO: %s' %
                         (status.get('classification') or (proc.stderr or proc.stdout)[-500:]))
    payload = json.load(open(args.output, encoding='utf-8'))
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
    p = sub.add_parser('init'); p.add_argument('--account', action='append', required=True); p.add_argument('--claude-bin', default='claude'); p.add_argument('--skip-profile-check', action='store_true', help=argparse.SUPPRESS); p.set_defaults(func=cmd_init)
    p = sub.add_parser('enqueue'); p.add_argument('--external-id', required=True); p.add_argument('--argv-json', required=True); p.add_argument('--cwd', required=True); p.add_argument('--output', required=True); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_enqueue)
    p = sub.add_parser('import-coordinator'); p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True); p.add_argument('--lease-id', action='append'); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_import_coordinator)
    p = sub.add_parser('import-requeue', help='H1339 A4: import one requeue_prepared lease attempt as a runnable job'); p.add_argument('lease_id'); p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True); p.add_argument('--max-attempts', type=int, default=2); p.set_defaults(func=cmd_import_requeue)
    p = sub.add_parser('reset-failed', help='B18: audited scoped recovery of terminal failed jobs (requires --reason)'); p.add_argument('--lease-id', action='append', required=True); p.add_argument('--reason', required=True); p.add_argument('--events'); p.set_defaults(func=cmd_reset_failed)
    p = sub.add_parser('recover'); p.add_argument('--coordinator', default=default_coordinator); p.add_argument('--coord-dir', default=default_coord_dir); p.add_argument('--cwd', default=default_cwd); p.set_defaults(func=cmd_recover)
    p = sub.add_parser('record-done'); p.add_argument('--coordinator', default=default_coordinator); p.add_argument('--coord-dir', default=default_coord_dir); p.add_argument('--cwd', default=default_cwd); p.set_defaults(func=cmd_record_done)
    p = sub.add_parser('run-once'); p.add_argument('--timeout', type=int, default=7200); p.add_argument('--claude-bin', default='claude'); p.add_argument('--only-profile'); p.add_argument('--coordinator', default=default_coordinator); p.add_argument('--coord-dir', default=default_coord_dir); p.add_argument('--cwd', default=default_cwd); p.set_defaults(func=cmd_run_once)
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
    p.add_argument('--run-id'); p.set_defaults(func=cmd_staged_run)
    p = sub.add_parser('presplit-canary')
    p.add_argument('--manifest', required=True); p.add_argument('--output', required=True)
    p.add_argument('--status', required=True); p.add_argument('--events', required=True)
    p.add_argument('--run-id'); p.add_argument('--claude-bin', default='claude')
    p.add_argument('--timeout', type=int, default=7200); p.set_defaults(func=cmd_presplit_canary)
    args = ap.parse_args(argv); args.func(args)


if __name__ == '__main__':
    main()
