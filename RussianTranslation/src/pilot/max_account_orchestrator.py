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


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def connect(path):
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
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


def claim(db_path, account, now=None):
    now = int(now or time.time())
    db = connect(db_path)
    try:
        db.execute('BEGIN IMMEDIATE')
        acc = db.execute('SELECT * FROM accounts WHERE name=?', (account,)).fetchone()
        if not acc or not acc['validated'] or acc['parked_until'] > now:
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


def run_claimed(db_path, account, config_dir, job, timeout):
    attempt = job['attempts']
    attempt_log = job['output_path'] + '.attempt%d.runner.json' % attempt
    status_path = job['output_path'] + '.attempt%d.status.json' % attempt
    if job['manifest_path']:
        if sha256_path(job['manifest_path']) != job['manifest_sha256']:
            return fail_or_retry(db_path, job['id'], 2, 'manifest hash changed',
                                 'manifest_drift', attempt_log)
        argv = [sys.executable, os.path.join(os.path.dirname(__file__), 'headless_worker.py'),
                job['manifest_path'], '--output', job['output_path'],
                '--status-out', status_path, '--timeout', str(timeout)]
    else:
        argv = json.loads(job['argv_json'])
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    try:
        proc = subprocess.run(argv, cwd=job['cwd'], env=env, text=True, encoding='utf-8',
                              capture_output=True, timeout=timeout)
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
        failure_class = worker_status.get('classification')
        if RATE_LIMIT.search(combined):
            until = parse_reset(combined)
            park(db_path, account, until, combined)
            finish(db_path, job['id'], 'pending', proc.returncode,
                   'rate-limited; account parked', 'rate_limit',
                   attempt_log_path=attempt_log, reset_at=until)
            return 'parked'
        if proc.returncode == 0:
            result_hash = sha256_path(job['output_path']) if os.path.exists(job['output_path']) else None
            finish(db_path, job['id'], 'done', 0, failure_class='success',
                   result_sha256=result_hash, attempt_log_path=attempt_log)
            return 'done'
        return fail_or_retry(db_path, job['id'], proc.returncode, combined[-2000:],
                             failure_class or 'process', attempt_log)
    except subprocess.TimeoutExpired as exc:
        return fail_or_retry(db_path, job['id'], 124, 'timeout after %ss' % timeout,
                             'timeout', attempt_log)
    except OSError as exc:
        return fail_or_retry(db_path, job['id'], 127, str(exc), 'process', attempt_log)


def profile_status(config_dir, claude='claude'):
    if not os.path.isdir(config_dir):
        return False, 'profile directory missing'
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    try:
        proc = subprocess.run([claude, 'auth', 'status', '--json'], env=env, text=True,
                              encoding='utf-8', capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, (proc.stderr or proc.stdout)[-500:]
    if proc.returncode or not data.get('loggedIn'):
        return False, data.get('subscriptionType') or 'not logged in'
    probe = subprocess.run(
        [claude, '-p', 'Return exactly OK.', '--output-format', 'json',
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(work)) as pool:
        futures = {pool.submit(run_claimed, args.db, acc['name'], acc['config_dir'], job, args.timeout):
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db', default='max_orchestrator.sqlite')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init'); p.add_argument('--account', action='append', required=True); p.add_argument('--claude-bin', default='claude'); p.add_argument('--skip-profile-check', action='store_true', help=argparse.SUPPRESS); p.set_defaults(func=cmd_init)
    p = sub.add_parser('enqueue'); p.add_argument('--external-id', required=True); p.add_argument('--argv-json', required=True); p.add_argument('--cwd', required=True); p.add_argument('--output', required=True); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_enqueue)
    p = sub.add_parser('import-coordinator'); p.add_argument('--coord-dir', required=True); p.add_argument('--cwd', required=True); p.add_argument('--lease-id', action='append'); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_import_coordinator)
    p = sub.add_parser('recover'); p.set_defaults(func=cmd_recover)
    p = sub.add_parser('record-done'); p.add_argument('--coordinator', required=True); p.add_argument('--cwd', required=True); p.set_defaults(func=cmd_record_done)
    p = sub.add_parser('run-once'); p.add_argument('--timeout', type=int, default=7200); p.set_defaults(func=cmd_run_once)
    p = sub.add_parser('status'); p.set_defaults(func=cmd_status)
    args = ap.parse_args(argv); args.func(args)


if __name__ == '__main__':
    main()
