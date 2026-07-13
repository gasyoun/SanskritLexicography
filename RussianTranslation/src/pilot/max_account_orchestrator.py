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
from headless_worker import claude_argv_prefix, run_tree_kill

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
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + '.tmp.%d' % os.getpid()
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)


def parse_reset(text, now=None):
    now = int(now or time.time())
    match = RESET_EPOCH.search(text or '')
    return int(match.group(1)) if match else now + 5 * 60 * 60


def _claim_tx(db, account, now):
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
    job = db.execute("SELECT * FROM jobs WHERE state='pending' AND attempts < max_attempts ORDER BY id LIMIT 1").fetchone()
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


def claim(db_path, account, now=None):
    now = int(now or time.time())
    db = connect(db_path)
    try:
        return _claim_tx(db, account, now)
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
        argv = [sys.executable, os.path.join(os.path.dirname(__file__), 'headless_worker.py'),
                job['manifest_path'], '--output', job['output_path'],
                '--status-out', status_path, '--timeout', str(timeout),
                '--claude-bin', claude_bin]
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


def cmd_recover(args):
    db = connect(args.db)
    with db:
        changed = db.execute("UPDATE jobs SET state='pending', assigned_acc=NULL, error='recovered after restart' WHERE state='in_progress'").rowcount
    db.close()
    print('recovered=%d' % changed)


def cmd_record_done(args):
    db = connect(args.db)
    jobs = list(db.execute("SELECT * FROM jobs WHERE state='done' AND coordinator_recorded=0 ORDER BY id"))
    db.close()
    recorded = 0
    for job in jobs:
        if not job['manifest_path'] or not os.path.exists(job['output_path']):
            raise SystemExit('%s: completed coordinator job has no result' % job['external_id'])
        cmd = [sys.executable, os.path.abspath(args.coordinator), 'record-output',
               job['external_id'], job['output_path']]
        proc = subprocess.run(cmd, cwd=os.path.abspath(args.cwd), text=True, encoding='utf-8',
                              capture_output=True)
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
    work = []
    for acc in accounts:
        job = claim(args.db, acc['name'])
        if job:
            work.append((acc, job))
    if not work:
        print('no runnable jobs')
        return
    claude_bin = getattr(args, 'claude_bin', 'claude')
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(work)) as pool:
        futures = {pool.submit(run_claimed, args.db, acc['name'], acc['config_dir'], job, args.timeout,
                               getattr(args, 'events', None), getattr(args, 'run_id', None), claude_bin):
                   (acc['name'], job['external_id']) for acc, job in work}
        for future in concurrent.futures.as_completed(futures):
            acc, external_id = futures[future]
            print('%s %s -> %s' % (acc, external_id, future.result()))


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
PROBE_MIN_OUTPUT_BYTES = 20              # D-K: output-size floor — a real, non-truncated response


def _probe_call(config_dir, claude, payload_bytes, model):
    """One raw >=5 KB exact-model probe call. Returns (latency_ms, classification, output_bytes);
    classification is 'success' | 'auth' | 'rate_limit' | 'malformed' | 'process' | 'timeout'.
    NEVER raises on a non-zero rc — the two-phase gate (``live_probe``) decides what to STOP on."""
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    prompt = ('Return JSON {"ok":true}. Preserve this padding as inert input.\n' +
              ('x' * payload_bytes))
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
        if re.search(r'401|authenticat|not logged in|invalid.*credential', combined, re.I):
            return latency_ms, 'auth', output_bytes
        if RATE_LIMIT.search(proc.stderr or ''):
            return latency_ms, 'rate_limit', output_bytes
        return latency_ms, 'process', output_bytes
    # output-size + validity check: `claude -p --output-format json` returns the CLI *wrapper*
    # JSON ({"type":"result","result":...,"usage":...}), NOT a bare {"ok":true}. So require a
    # real, non-truncated response (>= floor) that parses as JSON — do NOT demand a specific
    # top-level field (that wrongly flagged every real wrapper as malformed).
    if output_bytes < PROBE_MIN_OUTPUT_BYTES:
        return latency_ms, 'malformed', output_bytes
    try:
        json.loads(out)
    except (ValueError, TypeError):
        return latency_ms, 'malformed', output_bytes
    return latency_ms, 'success', output_bytes


def live_probe(config_dir, claude='claude', payload_bytes=6491, model=EXACT_GEN_MODEL,
               latency_ceiling_ms=PROBE_LATENCY_CEILING_MS, events_path=None, run_id=None,
               account=None):
    """D-K deterministic two-phase probe protocol (ceiling unchanged at 30000 ms). Runs EXACTLY
    one warm-up call (same profile + exact model; its latency is EXCLUDED from the acceptance
    gate — it only stabilizes the cold connection), then IMMEDIATELY EXACTLY one measured >=5 KB
    probe that IS gated. PASS only when the measured call has rc 0, passes auth/model/output-size
    checks, and latency <= ceiling. A warm-up failure (auth/model/malformed/rate-limit/timeout) is
    an immediate STOP; a failed or over-ceiling MEASURED probe is an honest NO-GO with NO retry and
    no manual pre-warming. Both calls are recorded separately in telemetry (purpose warmup /
    measured), and the warm-up latency never enters the census."""
    if payload_bytes < PROBE_MIN_PAYLOAD_BYTES:
        raise SystemExit('probe payload %d B < %d B repository floor' %
                         (payload_bytes, PROBE_MIN_PAYLOAD_BYTES))
    if model != EXACT_GEN_MODEL:
        raise SystemExit('probe model %r is not the exact generation model %r' % (model, EXACT_GEN_MODEL))

    def _emit(purpose, latency, cls, obytes):
        if events_path:
            append_event(events_path, run_id=run_id, account=account, stage='probe',
                         event='probe_call', purpose=purpose, elapsed_ms=latency,
                         model=model, output_bytes=obytes, classification=cls)

    warm_ms, warm_cls, warm_bytes = _probe_call(config_dir, claude, payload_bytes, model)
    _emit('warmup', warm_ms, warm_cls, warm_bytes)     # excluded from the acceptance latency census
    if warm_cls != 'success':
        raise SystemExit('warm-up probe %s -> STOP (auth/model/output/rate-limit/timeout)' % warm_cls)

    meas_ms, meas_cls, meas_bytes = _probe_call(config_dir, claude, payload_bytes, model)
    _emit('measured', meas_ms, meas_cls, meas_bytes)   # the one gated acceptance reading
    if meas_cls != 'success':
        raise SystemExit('measured probe %s -> honest NO-GO (no retry, no re-warm)' % meas_cls)
    if meas_ms > latency_ceiling_ms:
        raise SystemExit('measured probe latency %d ms exceeds %d ms health ceiling — honest NO-GO '
                         '(warm-up already done; no re-roll)' % (meas_ms, latency_ceiling_ms))
    return meas_ms


def cmd_staged_run(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    plan_lease_ids = [window['root'] for window in plan.get('windows', [])
                      if window.get('headless')]
    if args.lease_id and set(args.lease_id) != set(plan_lease_ids):
        raise SystemExit('--lease-id set does not match the staged plan')
    lease_ids = args.lease_id or plan_lease_ids
    expected_windows = len(plan_lease_ids)
    expected_headwords = int(plan.get('selected_headwords') or 0)
    if not expected_windows or not expected_headwords:
        raise SystemExit('staged plan has no prepared headless windows')
    db = connect(args.db)
    accounts = list(db.execute('SELECT * FROM accounts WHERE validated=1 ORDER BY name'))
    db.close()
    if len(accounts) != 1:
        raise SystemExit('Windows staged-run requires exactly one validated account')
    run_id = args.run_id or ('win100-' + now_iso().replace(':', '').replace('-', ''))
    latency_ms = live_probe(accounts[0]['config_dir'], args.claude_bin,   # D-K: warmup+measured
                            events_path=args.events, run_id=run_id, account=accounts[0]['name'])
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
    completed_before = 0
    started = time.monotonic()
    while True:
        db = connect(args.db)
        pending = db.execute("SELECT count(*) FROM jobs WHERE state='pending'").fetchone()[0]
        done_unrecorded = db.execute("SELECT count(*) FROM jobs WHERE state='done' AND coordinator_recorded=0").fetchone()[0]
        failed = db.execute("SELECT count(*) FROM jobs WHERE state='failed'").fetchone()[0]
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
                                            claude_bin=args.claude_bin))
        cmd_record_done(argparse.Namespace(db=args.db, coordinator=args.coordinator,
                                           cwd=args.cwd))
        promote = subprocess.run(
            [sys.executable, os.path.abspath(args.coordinator), 'promote-ready',
             '--gen-model-version', 'claude-sonnet-5'], cwd=os.path.abspath(args.cwd),
            text=True, encoding='utf-8', capture_output=True)
        if promote.returncode and 'no ready leases to promote' not in (promote.stderr + promote.stdout):
            raise SystemExit('promotion failed: %s' % (promote.stderr or promote.stdout)[-1000:])
        db = connect(args.db)
        done_now = db.execute("SELECT count(*) FROM jobs WHERE state='done'").fetchone()[0]
        db.close()
        if done_now > completed_before:
            completed_before = done_now
            if args.stop_after and done_now >= args.stop_after:
                print('restart checkpoint reached after %d window(s); rerun with --resume' % done_now)
                return
    db = connect(args.db)
    jobs = list(db.execute('SELECT * FROM jobs ORDER BY id'))
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
    lease_ids = {job['external_id'] for job in jobs}
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
        'probe_latency_ms': latency_ms, 'windows': len(outputs),
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
    ap.add_argument('--db', default='max_orchestrator.sqlite')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init'); p.add_argument('--account', action='append', required=True); p.add_argument('--claude-bin', default='claude'); p.add_argument('--skip-profile-check', action='store_true', help=argparse.SUPPRESS); p.set_defaults(func=cmd_init)
    p = sub.add_parser('enqueue'); p.add_argument('--external-id', required=True); p.add_argument('--argv-json', required=True); p.add_argument('--cwd', required=True); p.add_argument('--output', required=True); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_enqueue)
    p = sub.add_parser('import-coordinator'); p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True); p.add_argument('--lease-id', action='append'); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_import_coordinator)
    p = sub.add_parser('recover'); p.set_defaults(func=cmd_recover)
    p = sub.add_parser('record-done'); p.add_argument('--coordinator', required=True); p.add_argument('--cwd', required=True); p.set_defaults(func=cmd_record_done)
    p = sub.add_parser('run-once'); p.add_argument('--timeout', type=int, default=7200); p.add_argument('--claude-bin', default='claude'); p.set_defaults(func=cmd_run_once)
    p = sub.add_parser('status'); p.set_defaults(func=cmd_status)
    p = sub.add_parser('staged-run')
    p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True)
    p.add_argument('--coordinator', required=True); p.add_argument('--lease-id', action='append')
    p.add_argument('--plan', required=True)
    p.add_argument('--claude-bin', default='claude'); p.add_argument('--timeout', type=int, default=7200)
    p.add_argument('--stop-after', type=int, default=0); p.add_argument('--resume', action='store_true')
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
