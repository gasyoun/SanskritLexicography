#!/usr/bin/env python
"""Restartable outer scheduler for independently authenticated Claude profiles.

This layer owns dispatch only.  A queued job is an argv JSON array; the command
is run with CLAUDE_CONFIG_DIR set to the assigned account.  Translation logic,
auditing, and promotion remain owned by coordinator.py and its existing tools.
"""
import argparse
import concurrent.futures
import datetime
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
  last_error TEXT, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, external_id TEXT UNIQUE NOT NULL,
  argv_json TEXT NOT NULL, cwd TEXT NOT NULL, output_path TEXT NOT NULL,
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
    return db


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
        if not acc or acc['parked_until'] > now:
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


def finish(db_path, job_id, state, returncode, error=None):
    db = connect(db_path)
    with db:
        db.execute('UPDATE jobs SET state=?, returncode=?, error=?, finished_at=? WHERE id=?',
                   (state, returncode, error, now_iso(), job_id))
    db.close()


def fail_or_retry(db_path, job_id, returncode, error):
    db = connect(db_path)
    row = db.execute('SELECT attempts,max_attempts FROM jobs WHERE id=?', (job_id,)).fetchone()
    state = 'pending' if row and row['attempts'] < row['max_attempts'] else 'failed'
    db.close()
    finish(db_path, job_id, state, returncode, error)
    return state


def park(db_path, account, until, error):
    db = connect(db_path)
    with db:
        db.execute('UPDATE accounts SET parked_until=?, last_error=?, updated_at=? WHERE name=?',
                   (until, error[-2000:], now_iso(), account))
    db.close()


def run_claimed(db_path, account, config_dir, job, timeout):
    argv = json.loads(job['argv_json'])
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR'] = config_dir
    try:
        proc = subprocess.run(argv, cwd=job['cwd'], env=env, text=True, encoding='utf-8',
                              capture_output=True, timeout=timeout)
        payload = json.dumps({'argv': argv, 'returncode': proc.returncode,
                              'stdout': proc.stdout, 'stderr': proc.stderr}, ensure_ascii=False, indent=1)
        atomic_write(job['output_path'], payload)
        combined = proc.stdout + '\n' + proc.stderr
        if RATE_LIMIT.search(combined):
            until = parse_reset(combined)
            park(db_path, account, until, combined)
            finish(db_path, job['id'], 'pending', proc.returncode, 'rate-limited; account parked')
            return 'parked'
        if proc.returncode == 0:
            finish(db_path, job['id'], 'done', 0)
            return 'done'
        return fail_or_retry(db_path, job['id'], proc.returncode, combined[-2000:])
    except subprocess.TimeoutExpired as exc:
        return fail_or_retry(db_path, job['id'], 124, 'timeout after %ss' % timeout)
    except OSError as exc:
        return fail_or_retry(db_path, job['id'], 127, str(exc))


def cmd_init(args):
    db = connect(args.db)
    with db:
        for item in args.account:
            name, config_dir = item.split('=', 1)
            db.execute('INSERT OR REPLACE INTO accounts(name,config_dir,parked_until,last_error,updated_at) VALUES(?,?,0,NULL,?)',
                       (name, os.path.abspath(config_dir), now_iso()))
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


def cmd_recover(args):
    db = connect(args.db)
    with db:
        changed = db.execute("UPDATE jobs SET state='pending', assigned_acc=NULL, error='recovered after restart' WHERE state='in_progress'").rowcount
    db.close()
    print('recovered=%d' % changed)


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
    p = sub.add_parser('init'); p.add_argument('--account', action='append', required=True); p.set_defaults(func=cmd_init)
    p = sub.add_parser('enqueue'); p.add_argument('--external-id', required=True); p.add_argument('--argv-json', required=True); p.add_argument('--cwd', required=True); p.add_argument('--output', required=True); p.add_argument('--max-attempts', type=int, default=3); p.set_defaults(func=cmd_enqueue)
    p = sub.add_parser('recover'); p.set_defaults(func=cmd_recover)
    p = sub.add_parser('run-once'); p.add_argument('--timeout', type=int, default=7200); p.set_defaults(func=cmd_run_once)
    p = sub.add_parser('status'); p.set_defaults(func=cmd_status)
    args = ap.parse_args(argv); args.func(args)


if __name__ == '__main__':
    main()
