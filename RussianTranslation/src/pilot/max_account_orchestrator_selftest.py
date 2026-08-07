#!/usr/bin/env python
import builtins
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import types

import run_observability as ro

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Isolation from production data, established before any repo import (several modules
# resolve store/coordinator constants at import time). See selftest_isolation.py.
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_isolation import guard as _isolation_guard  # noqa: E402
_isolation_guard()

import max_account_orchestrator as m
import headless_worker as hw          # H2299: the paid lane's own bare-cwd helper
from execution_contract import config_dir_fingerprint


class MemoryCallLedger:
    """Selftest-only reservation authority for fake probe runners."""

    def __init__(self):
        self.next_id = 0
        self.finalized = {}

    def reserve(self, *_args, **_kwargs):
        self.next_id += 1
        return 'test-probe-%d' % self.next_id

    def finalize(self, reservation, telemetry):
        self.finalized[reservation] = dict(telemetry)


def enqueue_fixture(db_path, external_id, cwd, output_path, max_attempts=3):
    """Insert an inert legacy row for scheduler-state tests without a CLI escape."""
    con = m.connect(db_path)
    with con:
        con.execute(
            'INSERT INTO jobs(external_id,argv_json,cwd,output_path,max_attempts) '
            'VALUES(?,?,?,?,?)',
            (external_id, '[]', os.path.abspath(cwd),
             os.path.abspath(output_path), max_attempts))
    con.close()


def finish_fixture_worker(db_path, account, config_dir, job, timeout, *_args, **_kwargs):
    """Exercise scheduler fan-out without retaining an arbitrary subprocess path."""
    m.finish(db_path, job['id'], 'done', 0)
    return 'done'


def main():
    # H2154 (H2025 census S1-1/S1-2): the occupied-keys guard FAILS CLOSED — an
    # unreadable manifest on a queued/running job aborts the import instead of
    # contributing zero keys (which let the same headwords dispatch into a second
    # paid window). Terminal jobs with lost manifests stay ignorable.
    with tempfile.TemporaryDirectory() as okd:
        okdb = os.path.join(okd, 'jobs.sqlite')
        good = os.path.join(okd, 'good.json')
        with open(good, 'w', encoding='utf-8') as fh:
            json.dump({'meta': {'selected_keys': ['agni~~h0']}}, fh)
        torn = os.path.join(okd, 'torn.json')
        with open(torn, 'w', encoding='utf-8') as fh:
            fh.write('{"meta": {"selected_keys": ["bhU~~')
        con = m.connect(okdb)
        with con:
            con.execute("INSERT INTO jobs(external_id,cwd,output_path,manifest_path,state) "
                        "VALUES('j-good','.','o1',?, 'pending')", (good,))
            con.execute("INSERT INTO jobs(external_id,cwd,output_path,manifest_path,state) "
                        "VALUES('j-done-lost','.','o2',?, 'done')",
                        (os.path.join(okd, 'gone.json'),))
        assert m.occupied_keys(con) == {'agni~~h0'}, \
            'a terminal job with a lost manifest must stay ignorable'
        with con:
            con.execute("INSERT INTO jobs(external_id,cwd,output_path,manifest_path,state) "
                        "VALUES('j-live-lost','.','o3',?, 'pending')",
                        (os.path.join(okd, 'gone.json'),))
        try:
            m.occupied_keys(con)
            raise AssertionError('a LIVE job with an unreadable manifest must abort, '
                                 'not contribute zero keys (duplicate paid window)')
        except SystemExit as exc:
            assert 'j-live-lost' in str(exc) and 'H2154' in str(exc)
        with con:
            con.execute("UPDATE jobs SET manifest_path=? WHERE external_id='j-live-lost'",
                        (torn,))
        try:
            m.occupied_keys(con)
            raise AssertionError('a torn live manifest must abort the import')
        except SystemExit as exc:
            assert 'j-live-lost' in str(exc)
        con.close()
    print('PASS: test_occupied_keys_guard_fails_closed_h2154')

    staged_plan = {
        'selected_headwords': 2,
        'prepared_headwords': 1,
        'windows': [
            {'root': 'prepared', 'headwords': ['a'], 'headless': {'manifest_sha256': 'x'}},
            {'root': 'future', 'headwords': ['b'], 'headless': None},
        ],
    }
    scope = m.staged_plan_scope(staged_plan)
    assert scope['lease_ids'] == ['prepared']
    assert scope['expected_windows'] == 1
    assert scope['expected_headwords'] == 1
    assert m.staged_plan_scope(staged_plan, ['prepared']) == scope
    try:
        m.staged_plan_scope(staged_plan, ['future'])
        assert False, 'unprepared lease id must not enter staged acceptance'
    except SystemExit as exc:
        assert 'does not match' in str(exc)
    assert scope['expected_windows'] == 1 and scope['expected_headwords'] == 1
    print('  staged plan scope: prepared lease alone supplies the GO denominators')

    # Schema migration reads historical manifests once, when profile_slot is added. Corrupt
    # legacy rows stay NULL/unclaimable but must not be reopened on every scheduler connection.
    with tempfile.TemporaryDirectory() as td:
        legacy_db = os.path.join(td, 'legacy.sqlite')
        legacy_schema = m.SCHEMA.replace(
            'manifest_path TEXT, manifest_sha256 TEXT, profile_slot TEXT,',
            'manifest_path TEXT, manifest_sha256 TEXT,')
        assert legacy_schema != m.SCHEMA
        con = sqlite3.connect(legacy_db)
        con.executescript(legacy_schema)
        valid_path = os.path.join(td, 'valid-manifest.json')
        corrupt_path = os.path.join(td, 'corrupt-manifest.json')
        with open(valid_path, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v2',
                       'model': 'claude-sonnet-5',
                       'meta': {'lang': 'ru', 'selected_keys': ['legacy-key']},
                       'execution': {'profile_slot': 'acc1',
                                     'config_dir_fingerprint': config_dir_fingerprint(td),
                                     'execution_route': 'claude-cli-headless',
                                     'executor_lane': 'serial-whole-card',
                                     'validation_method': 'audit_window+final_schema',
                                     'model_identifier': 'claude-sonnet-5'},
                       'key_provenance': {'legacy-key': 'real'}}, f)
        with open(corrupt_path, 'w', encoding='utf-8') as f:
            f.write('{')
        for external_id, manifest_path in (
                ('legacy-valid', valid_path), ('legacy-corrupt', corrupt_path)):
            con.execute(
                'INSERT INTO jobs(external_id,cwd,output_path,manifest_path) VALUES(?,?,?,?)',
                (external_id, td, os.path.join(td, external_id + '.json'), manifest_path))
        con.commit()
        con.close()
        migrated = m.connect(legacy_db)
        assert migrated.execute(
            "SELECT profile_slot FROM jobs WHERE external_id='legacy-valid'").fetchone()[0] == 'acc1'
        assert migrated.execute(
            "SELECT profile_slot FROM jobs WHERE external_id='legacy-corrupt'").fetchone()[0] == ''
        now = m.now_iso()
        for account in ('acc1', 'acc2'):
            migrated.execute(
                'INSERT INTO accounts(name,config_dir,validated,updated_at) VALUES(?,?,1,?)',
                (account, os.path.join(td, account), now))
        migrated.commit()
        migrated.close()
        # A healthy scoped run must not reopen the unrelated corrupt sentinel.
        original_open = builtins.open
        original_claim = m.claim
        attempted = []
        try:
            def reject_corrupt_cross_scope(path, *args, **kwargs):
                if os.path.abspath(os.fspath(path)) == os.path.abspath(corrupt_path):
                    raise AssertionError('unrelated corrupt manifest was reparsed')
                return original_open(path, *args, **kwargs)

            def observe_claim(db_path, account, only_external_ids=None):
                attempted.append((account, frozenset(only_external_ids or ())))
                return None

            builtins.open = reject_corrupt_cross_scope
            m.claim = observe_claim
            m.cmd_run_once(types.SimpleNamespace(
                db=legacy_db, timeout=30, runtime_mode='standard', only_accounts=None,
                only_external_ids={'legacy-valid'}))
        finally:
            builtins.open = original_open
            m.claim = original_claim
        assert attempted == [('acc1', frozenset({'legacy-valid'}))], attempted
        with open(corrupt_path, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v2',
                       'model': 'claude-sonnet-5',
                       'meta': {'lang': 'ru', 'selected_keys': ['restored-key']},
                       'execution': {'profile_slot': 'acc2',
                                     'config_dir_fingerprint': config_dir_fingerprint(td),
                                     'execution_route': 'claude-cli-headless',
                                     'executor_lane': 'serial-whole-card',
                                     'validation_method': 'audit_window+final_schema',
                                     'model_identifier': 'claude-sonnet-5'},
                       'key_provenance': {'restored-key': 'real'}}, f)
        original_claim = m.claim
        try:
            m.claim = lambda db_path, account, only_external_ids=None: None
            m.cmd_run_once(types.SimpleNamespace(
                db=legacy_db, timeout=30, runtime_mode='standard', only_accounts=None,
                only_external_ids={'legacy-corrupt'}))
        finally:
            m.claim = original_claim
        reopened = sqlite3.connect(legacy_db)
        assert reopened.execute(
            "SELECT profile_slot FROM jobs WHERE external_id='legacy-corrupt'").fetchone()[0] == 'acc2'
        reopened.close()
    print('  profile-slot migration: bad cross-scope sentinel stays cold; scoped repair revalidates')

    with tempfile.TemporaryDirectory() as td:
        scoped_db = os.path.join(td, 'scope.sqlite')
        m.main(['--db', scoped_db, 'init', '--account', 'acc=' + os.path.join(td, 'acc'),
                '--skip-profile-check'])
        for external_id in ('historic-failed', 'current'):
            enqueue_fixture(
                scoped_db, external_id, td,
                os.path.join(td, external_id + '.json'))
        con = m.connect(scoped_db)
        with con:
            con.execute("UPDATE jobs SET state='failed' WHERE external_id='historic-failed'")
        con.close()
        claimed = m.claim(scoped_db, 'acc', only_external_ids={'current'})
        assert claimed and claimed['external_id'] == 'current'
        m.finish(scoped_db, claimed['id'], 'done', 0)
        con = m.connect(scoped_db)
        assert m.scoped_job_count(con, {'current'}, "state='failed'") == 0
        assert [row['external_id'] for row in m.scoped_jobs(
            con, {'current'}, "state='done' AND coordinator_recorded=0")] == ['current']
        con.close()
    print('  staged scope: unrelated failed/history jobs excluded from claims and counts')

    # A profile-bound v2 manifest is a scheduler constraint, not merely a worker-time check.
    # Register accounts in the opposite order from the manifest owner and ask the wrong account
    # first: it must not reserve the paid job.
    with tempfile.TemporaryDirectory() as td:
        bound_db = os.path.join(td, 'profile-bound.sqlite')
        acc1_dir = os.path.join(td, 'acc1')
        acc2_dir = os.path.join(td, 'acc2')
        m.main(['--db', bound_db, 'init',
                '--account', 'acc2=' + acc2_dir, '--account', 'acc1=' + acc1_dir,
                '--skip-profile-check'])
        coord = os.path.join(td, 'coord')
        artifacts = os.path.join(coord, 'artifacts', 'bound-acc1')
        os.makedirs(artifacts)
        manifest_path = os.path.join(artifacts, 'execution_manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v2',
                       'model': 'claude-sonnet-5',
                       'meta': {'lang': 'ru', 'selected_keys': ['bound-key']},
                       'execution': {'profile_slot': 'acc1',
                                     'config_dir_fingerprint': config_dir_fingerprint(acc1_dir),
                                     'execution_route': 'claude-cli-headless',
                                     'executor_lane': 'serial-whole-card',
                                     'validation_method': 'audit_window+final_schema',
                                     'model_identifier': 'claude-sonnet-5'},
                       'key_provenance': {'bound-key': 'real'}}, f)
        bound_preflight = os.path.join(artifacts, 'preflight.json')
        with open(bound_preflight, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.performance_preflight.v1',
                       'selected_keys': ['bound-key'],
                       'cost_gate': {'over_ceiling': False}}, f)
        with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
            json.dump({'leases': [{'id': 'bound-acc1', 'state': 'prepared',
                                   'artifact_dir': artifacts,
                                   'execution_manifest': manifest_path,
                                   'preflight_path': bound_preflight,
                                   'preflight_sha256':
                                       m.sha256_path(bound_preflight)}]}, f)
        m.main(['--db', bound_db, 'import-coordinator', '--coord-dir', coord,
                '--cwd', td, '--lease-id', 'bound-acc1'])
        con = sqlite3.connect(bound_db)
        assert con.execute(
            "select profile_slot from jobs where external_id='bound-acc1'").fetchone()[0] == 'acc1'
        con.close()
        assert m.claim(bound_db, 'acc2') is None, 'wrong account claimed an acc1-bound manifest'
        try:
            m.cmd_run_once(types.SimpleNamespace(
                db=bound_db, timeout=30, runtime_mode='standard',
                only_accounts={'acc2'}, only_external_ids={'bound-acc1'}))
            raise AssertionError('missing eligible owner must fail before a dispatch poll loop')
        except SystemExit as exc:
            assert 'no eligible/probed account: acc1' in str(exc), exc

        bound = m.claim(bound_db, 'acc1')
        assert bound is not None and bound['external_id'] == 'bound-acc1'
    print('  profile-bound claims: wrong/missing owner refused loudly')

    # Arbitrary argv is not a securable paid-call boundary: a neutral wrapper can invoke
    # anything. Refuse every generic enqueue and every legacy generic row before spawn.
    with tempfile.TemporaryDirectory() as td:
        guard_db = os.path.join(td, 'generic-guard.sqlite')
        m.main(['--db', guard_db, 'init',
                '--account', 'acc=' + os.path.join(td, 'acc'), '--skip-profile-check'])
        generic_argvs = [
            ['Claude', '-p', 'forbidden'],
            ['claude-code', '-p', 'forbidden'],
            [sys.executable, os.path.join(td, 'headless_worker.py')],
            [sys.executable, os.path.join(td, 'latency_payload_sweep.py')],
            [sys.executable, os.path.join(td, 'H963_c4_gate0_probe.py')],
            [sys.executable, os.path.join(td, 'model_wrapper.py')],
            ['node', os.path.join(td, 'model_wrapper.js')],
            [os.path.join(td, 'renamed.exe'), '-p', 'request'],
            [sys.executable, '-c', 'print("harmless")'],
        ]
        for index, argv in enumerate(generic_argvs):
            try:
                m.main(['--db', guard_db, 'enqueue',
                        '--external-id', 'enqueue-generic-%d' % index,
                        '--argv-json', json.dumps(argv), '--cwd', td,
                        '--output', os.path.join(td, 'enqueue-generic-%d.json' % index)])
                raise AssertionError('generic argv reached enqueue: %r' % argv)
            except SystemExit as exc:
                assert 'generic argv jobs are disabled' in str(exc), (argv, exc)
        con = m.connect(guard_db)
        assert con.execute(
            "SELECT count(*) FROM jobs WHERE external_id LIKE "
            "'enqueue-generic-%'").fetchone()[0] == 0
        with con:
            for index, argv in enumerate(generic_argvs):
                con.execute(
                    'INSERT INTO jobs(external_id,argv_json,cwd,output_path,max_attempts) '
                    'VALUES(?,?,?,?,1)',
                    ('legacy-generic-%d' % index, json.dumps(argv), td,
                     os.path.join(td, 'legacy-generic-%d.json' % index)))
        con.close()
        original_runner = m.run_tree_kill
        spawned = []

        def reject_spawn(*args, **kwargs):
            spawned.append((args, kwargs))
            raise AssertionError('forbidden generic argv was spawned')

        m.run_tree_kill = reject_spawn
        try:
            for index in range(len(generic_argvs)):
                job = m.claim(guard_db, 'acc')
                assert job and job['external_id'] == 'legacy-generic-%d' % index, job
                assert m.run_claimed(
                    guard_db, 'acc', os.path.join(td, 'acc'), job, 5) == 'failed'
        finally:
            m.run_tree_kill = original_runner
        assert not spawned
        con = m.connect(guard_db)
        assert con.execute(
            "SELECT count(*) FROM jobs WHERE external_id LIKE 'legacy-generic-%' "
            "AND state='failed' AND failure_class='configuration'").fetchone()[0] == len(
                generic_argvs)
        con.close()
    print('  generic argv guard: all arbitrary enqueues + legacy rows refuse before spawn')

    # H1 (H1940): a DETERMINISTIC defect must be terminal on the first attempt.
    # fail_or_retry keys purely on `attempts < max_attempts`, so a configuration verdict —
    # a manifest that will never parse — used to go back to 'pending' and burn the whole
    # budget re-deriving it. Two of these shapes never even reached a verdict: the
    # pre-launch hash + json.load were unguarded, so they escaped run_claimed entirely.
    # Every job below carries max_attempts=3 and fails on attempt 1, so 'failed' proves
    # the CLASS ended it, not exhaustion.
    with tempfile.TemporaryDirectory() as td:
        h1_db = os.path.join(td, 'h1-terminal.sqlite')
        acc_dir = os.path.join(td, 'acc1')
        os.makedirs(acc_dir)
        m.main(['--db', h1_db, 'init', '--account', 'acc1=' + acc_dir,
                '--skip-profile-check'])
        h1_ledger = os.path.join(td, 'h1.calls.json')

        def h1_manifest(keys):
            return {'schema': 'pwg.headless_execution_manifest.v2',
                    'model': 'claude-sonnet-5',
                    'meta': {'lang': 'ru', 'selected_keys': keys},
                    'execution': {'profile_slot': 'acc1',
                                  'config_dir_fingerprint': config_dir_fingerprint(acc_dir),
                                  'execution_route': 'claude-cli-headless',
                                  'executor_lane': 'serial-whole-card',
                                  'validation_method': 'audit_window+final_schema',
                                  'model_identifier': 'claude-sonnet-5'},
                    'key_provenance': {key: 'real' for key in keys}}

        h1_preflight = os.path.join(td, 'h1.preflight.json')
        with open(h1_preflight, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.performance_preflight.v1',
                       'selected_keys': ['h1key'],
                       'cost_gate': {'over_ceiling': False}}, f)
        h1_preflight_sha = m.sha256_path(h1_preflight)

        def h1_seed(external_id, manifest_path, manifest_sha):
            con = m.connect(h1_db)
            with con:
                con.execute(
                    'INSERT INTO jobs(external_id,cwd,output_path,manifest_path,'
                    'manifest_sha256,profile_slot,preflight_path,preflight_sha256,'
                    'max_attempts,run_id) VALUES(?,?,?,?,?,?,?,?,3,?)',
                    (external_id, td, os.path.join(td, external_id + '.out.json'),
                     manifest_path, manifest_sha, 'acc1', h1_preflight,
                     h1_preflight_sha, 'h1run'))
            con.close()
            job = m.claim(h1_db, 'acc1', only_external_ids=[external_id])
            assert job and job['external_id'] == external_id, (external_id, job)
            assert job['attempts'] == 1 < job['max_attempts'], dict(job)
            return job

        def h1_row(external_id):
            con = m.connect(h1_db)
            row = con.execute(
                'SELECT state,failure_class,error,attempts,max_attempts FROM jobs '
                'WHERE external_id=?', (external_id,)).fetchone()
            con.close()
            return dict(row)

        original_runner = m.run_tree_kill
        h1_spawns = []

        def h1_worker(status_payload, returncode):
            def runner(argv, **_kwargs):
                h1_spawns.append(argv)
                with open(argv[argv.index('--status-out') + 1], 'w',
                          encoding='utf-8') as fh:
                    json.dump(status_payload, fh)
                return types.SimpleNamespace(returncode=returncode, stdout='', stderr='')
            return runner

        try:
            # (1) The sealed manifest is missing. Pre-H1 sha256_path raised
            # FileNotFoundError straight out of run_claimed — no verdict at all.
            m.run_tree_kill = lambda *_a, **_k: h1_spawns.append('SPAWNED')
            job = h1_seed('h1-missing', os.path.join(td, 'gone.json'), 'f' * 64)
            state = m.run_claimed(h1_db, 'acc1', acc_dir, job, 5, run_id='h1run',
                                  call_reservation_path=h1_ledger)
            row = h1_row('h1-missing')
            assert state == 'failed', ('missing manifest retried', state, row)
            assert row['state'] == 'failed' and row['failure_class'] == 'configuration', row
            assert row['attempts'] < row['max_attempts'], ('terminal by exhaustion, '
                                                           'not by class', row)
            assert 'unreadable' in (row['error'] or ''), row
            assert not h1_spawns, h1_spawns

            # (2) Bytes read fine, JSON invalid. The seal matches, so the drift branch
            # is passed and the decode is what fails.
            bad_path = os.path.join(td, 'invalid.json')
            with open(bad_path, 'wb') as f:
                f.write(b'{"schema": "pwg.headless_execution_manifest.v2", ')
            job = h1_seed('h1-badjson', bad_path, m.sha256_path(bad_path))
            state = m.run_claimed(h1_db, 'acc1', acc_dir, job, 5, run_id='h1run',
                                  call_reservation_path=h1_ledger)
            row = h1_row('h1-badjson')
            assert state == 'failed', ('invalid JSON retried', state, row)
            assert row['state'] == 'failed' and row['failure_class'] == 'configuration', row
            assert row['attempts'] < row['max_attempts'], row
            assert not h1_spawns, h1_spawns

            # (3) The manifest is fine here; the WORKER returns a configuration verdict
            # (its own H1 status path). Pre-H1 this went to fail_or_retry -> 'pending'.
            good_path = os.path.join(td, 'good.json')
            with open(good_path, 'w', encoding='utf-8') as f:
                json.dump(h1_manifest(['h1key']), f)
            good_sha = m.sha256_path(good_path)
            m.run_tree_kill = h1_worker(
                {'classification': 'configuration', 'error': "KeyError: 'inputs'",
                 'manifest_sha256': good_sha}, 2)
            job = h1_seed('h1-worker-config', good_path, good_sha)
            state = m.run_claimed(h1_db, 'acc1', acc_dir, job, 5, run_id='h1run',
                                  call_reservation_path=h1_ledger)
            row = h1_row('h1-worker-config')
            assert state == 'failed', ('worker configuration verdict retried', state, row)
            assert row['state'] == 'failed' and row['failure_class'] == 'configuration', row
            assert row['attempts'] < row['max_attempts'], row
            assert len(h1_spawns) == 1, h1_spawns

            # (4) REGRESSION GUARD, not a defect pin: an ordinary process failure must
            # still consume an attempt and return to 'pending'. This one is GREEN on
            # pre-H1 master by construction — it exists to prove the terminal path did
            # not globally disable retry.
            h1_spawns.clear()
            m.run_tree_kill = h1_worker(
                {'classification': 'process', 'error': 'transient boom',
                 'manifest_sha256': good_sha}, 1)
            job = h1_seed('h1-transient', good_path, good_sha)
            state = m.run_claimed(h1_db, 'acc1', acc_dir, job, 5, run_id='h1run',
                                  call_reservation_path=h1_ledger)
            row = h1_row('h1-transient')
            assert state == 'pending', ('transient failure lost its retry', state, row)
            assert row['state'] == 'pending' and row['failure_class'] == 'process', row
        finally:
            m.run_tree_kill = original_runner
    # A class that permanently kills a job must be visible in the readiness report, or the
    # window simply goes missing from it with nothing saying why.
    assert 'configuration' in m.HARD_FAILURE_CLASSES, m.HARD_FAILURE_CLASSES
    assert m.DETERMINISTIC_FAILURE_CLASSES <= m.HARD_FAILURE_CLASSES, (
        'a class terminal enough to kill a job must also be reported as a hard failure')
    print('  H1 terminal config: unreadable/invalid manifest + worker configuration verdict '
          'fail terminally on attempt 1 (max_attempts=3, zero pre-launch spawns); '
          'process failure still retries')

    # Required profile selection happens before the standard three-account concurrency slice.
    # Otherwise acc4 is permanently hidden behind three alphabetically earlier idle accounts.
    with tempfile.TemporaryDirectory() as td:
        slice_db = os.path.join(td, 'profile-slice.sqlite')
        m.main(['--db', slice_db, 'init'] + [
            part for n in range(1, 5)
            for part in ('--account', 'acc%d=%s' % (n, os.path.join(td, 'a%d' % n)))
        ] + ['--skip-profile-check'])
        con = m.connect(slice_db)
        with con:
            con.execute(
                'INSERT INTO jobs(external_id,cwd,output_path,manifest_path,profile_slot) '
                'VALUES(?,?,?,?,?)', ('late-slot', td, os.path.join(td, 'late.json'),
                                     os.path.join(td, 'manifest.json'), 'acc4'))
        con.close()
        original_claim = m.claim
        attempted = []
        try:
            def observe_claim(db_path, account, only_external_ids=None):
                attempted.append(account)
                return None

            m.claim = observe_claim
            m.cmd_run_once(types.SimpleNamespace(
                db=slice_db, timeout=30, runtime_mode='standard', only_accounts=None,
                only_external_ids={'late-slot'}))
        finally:
            m.claim = original_claim
        assert attempted == ['acc4'], attempted
        con = m.connect(slice_db)
        with con:
            con.execute(
                "INSERT INTO jobs(external_id,cwd,output_path,state,assigned_acc) "
                "VALUES(?,?,?,'in_progress','acc4')",
                ('unrelated-active', td, os.path.join(td, 'busy.json')))
        con.close()
        try:
            m.cmd_run_once(types.SimpleNamespace(
                db=slice_db, timeout=30, runtime_mode='standard', only_accounts=None,
                only_external_ids={'late-slot'}))
            raise AssertionError('busy required profile must fail before a bounded poll loop')
        except SystemExit as exc:
            assert 'acc4:unrelated-active' in str(exc), exc
    print('  profile-bound dispatch: late slot selected before slice; busy owner fails loudly')

    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'q.sqlite')
        m.main(['--db', db, 'init', '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'), '--skip-profile-check'])
        for n in range(2):
            enqueue_fixture(
                db, 'j%d' % n, td, os.path.join(td, 'out%d.json' % n))
        for account in ('acc1', 'acc2'):
            job = m.claim(db, account)
            assert job is not None
            m.finish(db, job['id'], 'done', 0)
        con = sqlite3.connect(db)
        assert con.execute("select count(*) from jobs where state='done'").fetchone()[0] == 2
        con.execute("insert into jobs(external_id,argv_json,cwd,output_path,state) values('stale','[]',?,?,'in_progress')", (td, os.path.join(td, 'x')))
        con.commit(); con.close()
        m.main(['--db', db, 'recover'])
        con = sqlite3.connect(db)
        assert con.execute("select state from jobs where external_id='stale'").fetchone()[0] == 'pending'
        con.execute("delete from jobs where external_id='stale'")
        con.commit()
        con.close()
        assert m.parse_reset('rate limit reset_at=1999999999', now=1) == 1999999999
        assert m.parse_reset('429 too many requests', now=100) == 18100

        coord = os.path.join(td, 'coord'); artifacts = os.path.join(coord, 'artifacts', 'lease1')
        os.makedirs(artifacts)
        manifest = os.path.join(artifacts, 'manifest.json')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v2',
                       'model': 'claude-sonnet-5',
                       'meta': {'lang': 'ru', 'selected_keys': ['unique']},
                       'execution': {'profile_slot': 'acc1',
                                     'config_dir_fingerprint': config_dir_fingerprint(
                                         os.path.join(td, 'a1')),
                                     'execution_route': 'claude-cli-headless',
                                     'executor_lane': 'serial-whole-card',
                                     'validation_method': 'audit_window+final_schema',
                                     'model_identifier': 'claude-sonnet-5'},
                       'key_provenance': {'unique': 'real'}}, f)
        preflight = os.path.join(artifacts, 'preflight.json')
        with open(preflight, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.performance_preflight.v1',
                       'selected_keys': ['unique'],
                       'cost_gate': {'over_ceiling': False}}, f)
        with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
            json.dump({'leases': [{'id': 'lease1', 'state': 'prepared',
                                   'artifact_dir': artifacts,
                                   'execution_manifest': manifest,
                                   'preflight_path': preflight,
                                   'preflight_sha256': m.sha256_path(preflight)}]}, f)
        m.main(['--db', db, 'import-coordinator', '--coord-dir', coord, '--cwd', td,
                '--lease-id', 'lease1'])
        con = sqlite3.connect(db)
        row = con.execute("select manifest_sha256,state from jobs where external_id='lease1'").fetchone()
        assert row == (m.sha256_path(manifest), 'pending')
        con.close()

        # H1339 A4: import-requeue materialises a requeue_prepared attempt as the UNIQUE
        # job '<lease>::rqNN-<kind>'; idempotent on re-run; loud on a wrong lease state.
        rq_dir = os.path.join(artifacts, 'requeue', 'rq01-transient')
        os.makedirs(rq_dir)
        rq_manifest = os.path.join(rq_dir, 'execution_manifest.lease1.rq01-transient.json')
        with open(rq_manifest, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v2',
                       'model': 'claude-sonnet-5',
                       'meta': {'lang': 'ru', 'selected_keys': ['rqkey']},
                       'execution': {'profile_slot': 'acc1',
                                     'config_dir_fingerprint': config_dir_fingerprint(
                                         os.path.join(td, 'a1')),
                                     'execution_route': 'claude-cli-headless',
                                     'executor_lane': 'serial-whole-card',
                                     'validation_method': 'audit_window+final_schema',
                                     'model_identifier': 'claude-sonnet-5'},
                       'key_provenance': {'rqkey': 'real'}}, f)
        rq_preflight = os.path.join(rq_dir, 'preflight.json')
        with open(rq_preflight, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.performance_preflight.v1',
                       'selected_keys': ['rqkey'],
                       'cost_gate': {'over_ceiling': False}}, f)
        with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
            json.dump({'leases': [{'id': 'lease1', 'state': 'requeue_prepared',
                                   'artifact_dir': artifacts,
                                   'requeue_attempt': 1, 'requeue_kind': 'transient',
                                   'execution_manifest': rq_manifest,
                                   'preflight_path': rq_preflight,
                                   'preflight_sha256': m.sha256_path(rq_preflight),
                                   'current_attempt': {'number': 1, 'kind': 'transient',
                                                       'artifact_dir': rq_dir,
                                                       'execution_manifest': rq_manifest,
                                                       'preflight': rq_preflight,
                                                       'preflight_sha256':
                                                           m.sha256_path(rq_preflight)}}]}, f)
        ns = types.SimpleNamespace(db=db, coord_dir=coord, cwd=td,
                                   lease_id='lease1', max_attempts=2)
        rq_id = m.cmd_import_requeue(ns)
        assert rq_id == 'lease1::rq01-transient', rq_id
        assert m.coordinator_lease_id(rq_id) == 'lease1'
        assert m.coordinator_lease_id('lease1') == 'lease1'
        con = sqlite3.connect(db)
        row = con.execute('select manifest_sha256,state,max_attempts from jobs '
                          'where external_id=?', (rq_id,)).fetchone()
        assert row == (m.sha256_path(rq_manifest), 'pending', 2), row
        con.close()
        assert m.cmd_import_requeue(ns) == rq_id            # idempotent re-import
        con = sqlite3.connect(db)
        assert con.execute('select count(*) from jobs where external_id=?',
                           (rq_id,)).fetchone()[0] == 1
        con.close()
        with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
            json.dump({'leases': [{'id': 'lease1', 'state': 'promoted'}]}, f)
        try:
            m.cmd_import_requeue(ns)
            raise AssertionError('import-requeue accepted a non-requeue_prepared lease')
        except SystemExit as e:
            assert 'requeue_prepared' in str(e)
        print('  H1339 A4: import-requeue -> unique ::rqNN job, idempotent, fail-closed on state')

        # H1339 B18: reset-failed is the ONLY (audited) exit from the terminal failed state.
        con = sqlite3.connect(db)
        con.execute("update jobs set state='failed', attempts=2, error='boom' "
                    'where external_id=?', (rq_id,))
        con.commit(); con.close()
        try:
            m.cmd_reset_failed(types.SimpleNamespace(db=db, lease_id=[rq_id], reason='  ',
                                                     events=None))
            raise AssertionError('reset-failed accepted an empty reason')
        except SystemExit:
            pass
        ev = os.path.join(td, 'reset_events.jsonl')
        n = m.cmd_reset_failed(types.SimpleNamespace(
            db=db, lease_id=[rq_id], reason='operator verified transient outage', events=ev))
        assert n == 1
        con = sqlite3.connect(db)
        state_, attempts_, err_ = con.execute(
            'select state,attempts,error from jobs where external_id=?', (rq_id,)).fetchone()
        con.close()
        assert (state_, attempts_) == ('pending', 0) and 'reset-failed' in err_
        assert 'reset_failed' in open(ev, encoding='utf-8').read()
        try:
            m.cmd_reset_failed(types.SimpleNamespace(db=db, lease_id=['absent'],
                                                     reason='x', events=None))
            raise AssertionError('reset-failed on an empty scope must be loud')
        except SystemExit:
            pass
        con = sqlite3.connect(db)
        con.execute('delete from jobs where external_id=?', (rq_id,))
        con.commit(); con.close()
        print('  H1339 B18: reset-failed audited (reason + events row), scoped, loud on empty scope')

    # D-C (H818 Windows acceptance): a manifest_sha256 containing "429" must NOT be read
    # as a rate-limit; only the worker's own classification or a real provider 429 in
    # stderr must. This prevents the false 5 h account park observed on Windows.
    assert m.is_rate_limited({'classification': 'configuration',
                              'manifest_sha256': '80179429d4f8e6'}, '') is False
    assert m.is_rate_limited({'classification': 'rate_limit'}, '') is True
    assert m.is_rate_limited({}, 'HTTP 429 Too Many Requests') is True
    assert m.is_rate_limited({}, '') is False
    print('  D-C is_rate_limited: hash-429 ignored; worker-class / real-429 detected')

    # D-F/D-K: the two-phase probe protocol. payload<5KB / non-exact model raise before any call.
    # Then EXACTLY one warm-up call (latency excluded) + one measured call (gated): policy is
    # strictly below the ceiling; the ceiling value itself is an honest NO-GO.
    # Boundary values are DERIVED from m.PROBE_LATENCY_CEILING_MS, never hard-coded: this
    # pin asserted 29999/30000 literally, so raising the ceiling to 65 000 (MG 31-07-2026)
    # silently turned it into a false pass. Deriving them tests the strictly-below POLICY.
    _ceil = m.PROBE_LATENCY_CEILING_MS
    _under, _at = _ceil - 1, _ceil
    try:
        m.live_probe('cfg', payload_bytes=100); assert False, 'payload floor not enforced'
    except SystemExit as e:
        assert 'floor' in str(e)
    try:
        m.live_probe('cfg', model='claude-haiku-4-5'); assert False, 'exact-model gate missing'
    except SystemExit as e:
        assert 'exact generation model' in str(e)
    try:
        m.live_probe('cfg')
        assert False, 'paid live probe accepted no reservation ledger'
    except ValueError as e:
        assert 'call reservation ledger' in str(e)
    _pc = m._probe_call
    try:
        seen = []

        def fake(seq):
            it = iter(seq)

            def _mock(config_dir, claude, payload_bytes, model, *_args, **_kwargs):
                v = next(it)
                seen.append(v)
                return v
            return _mock

        # warm-up 99999 ms (EXCLUDED) + measured 29999 ms -> PASS
        seen.clear(); m._probe_call = fake([(99999, 'success', 120), (_under, 'success', 120)])
        with tempfile.TemporaryDirectory() as td:
            ev = os.path.join(td, 'e.jsonl')
            assert m.live_probe(
                'cfg', events_path=ev, run_id='r', account='a',
                call_reservation=MemoryCallLedger()) == _under
            rows = ro.read_events(ev)
            assert len([r for r in rows if r.get('purpose') == 'warmup']) == 1
            assert len([r for r in rows if r.get('purpose') == 'measured']) == 1
            assert len(seen) == 2                       # exactly one warm-up + one measured
            cen = ro.build_census(rows)
            assert cen['latency_ms']['max'] == _under   # the warm-up is NOT in the latency census
            assert len(cen['probe']['warmup']) == 1 and len(cen['probe']['measured']) == 1
        # measured AT the ceiling -> honest NO-GO (no retry)
        seen.clear(); m._probe_call = fake([(9000, 'success', 120), (_at, 'success', 120)])
        try:
            m.live_probe('cfg', call_reservation=MemoryCallLedger()); assert False, 'a measured reading AT the ceiling must NO-GO'
        except SystemExit as e:
            assert 'health ceiling' in str(e)
        assert len(seen) == 2
        # warm-up auth failure -> immediate STOP, measured NEVER starts
        seen.clear(); m._probe_call = fake([(9000, 'auth', 0)])
        try:
            m.live_probe('cfg', call_reservation=MemoryCallLedger()); assert False, 'warm-up auth must STOP'
        except SystemExit as e:
            assert 'warm-up' in str(e)
        assert len(seen) == 1                           # measured never started
        # measured malformed (output-size/validity) -> honest NO-GO
        seen.clear(); m._probe_call = fake([(9000, 'success', 120), (9000, 'malformed', 3)])
        try:
            m.live_probe('cfg', call_reservation=MemoryCallLedger()); assert False, 'malformed measured must NO-GO'
        except SystemExit:
            pass
        assert len(seen) == 2
    finally:
        m._probe_call = _pc
    print('  D-F/D-K probe protocol: 1 warm-up (excluded) + 1 measured; %d pass / %d NO-GO (derived from PROBE_LATENCY_CEILING_MS); warm-up fail STOPs before measured' % (_under, _at))

    # D-K _probe_call: rc 0 is NOT enough. The Claude CLI result envelope must indicate success
    # (type=result, subtype=success, not is_error) AND carry the structured schema result
    # {"ok": true}. Six fixtures + edge cases. output_bytes is ENCODED UTF-8 bytes, not char count.
    assert len('да') == 2 and len('да'.encode('utf-8')) == 4
    _rtk = m.run_tree_kill

    def _out(stdout='', rc=0, stderr=''):
        m.run_tree_kill = lambda *a, **k: types.SimpleNamespace(returncode=rc, stdout=stdout, stderr=stderr)

    def _cls(stdout='', rc=0, stderr=''):
        _out(stdout, rc, stderr)
        return m._probe_call(
            'cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
            call_reservation=MemoryCallLedger())[1]

    try:
        # (1) observed successful result-STRING wrapper (result is a JSON string) + Cyrillic body
        w1 = '{"type":"result","subtype":"success","is_error":false,"result":"{\\"ok\\":true}","usage":{"n":"да"}}'
        _out(w1)
        lat, cls, ob = m._probe_call(
            'cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
            call_reservation=MemoryCallLedger())
        assert cls == 'success', cls
        assert ob == len(w1.encode('utf-8')) and ob > len(w1)     # encoded bytes, not char count
        # (2) successful structured_output wrapper
        assert _cls('{"type":"result","subtype":"success","is_error":false,"structured_output":{"ok":true}}') == 'success'
        # (3) rc=0 ERROR wrapper (subtype != success) -> process
        assert _cls('{"type":"result","subtype":"error_during_execution","is_error":false}') == 'process'
        # (4) is_error=true -> process (never success)
        assert _cls('{"type":"result","subtype":"success","is_error":true,"result":"boom"}') == 'process'
        # (5) {"ok": false} -> content (never success)
        assert _cls('{"type":"result","subtype":"success","is_error":false,"result":"{\\"ok\\":false}"}') == 'content'
        # (6) rate-limit / auth error wrapper reported with rc 0 -> detected inside
        assert _cls('{"type":"result","subtype":"error","is_error":true,"result":"429 Too Many Requests rate limit"}') == 'rate_limit'
        assert _cls('{"type":"result","subtype":"error","is_error":true,"result":"401 Invalid authentication credentials"}') == 'auth'
        # edges: non-envelope / non-JSON / missing structured result -> malformed; 401 rc!=0 -> auth
        assert _cls('<html>not json</html>') == 'malformed'
        assert _cls('{"foo":"bar"}') == 'malformed'                       # type != result
        assert _cls('{"type":"result","subtype":"success","is_error":false}') == 'malformed'  # no structured result
        assert _cls('', rc=1, stderr='401 Invalid authentication credentials') == 'auth'
    finally:
        m.run_tree_kill = _rtk
    print('  D-K _probe_call envelope: result-string + structured_output => success; error/is_error => process; {ok:false} => content; rc0 rate/auth wrapper detected; non-envelope => malformed')

    # D-P (H994): the readiness prompt must be a completable, natural task — NOT the degenerate
    # "Return JSON {ok:true} + N*'x' padding" that tripped Sonnet-5's --permission-mode plan refusal
    # (prose citing AskUserQuestion; a FALSE NO-GO on a healthy fast profile). It must keep
    # >=payload_bytes of inert filler (load-representative), keep plan mode (matches
    # headless_worker.call's real generation invocation), and carry ONE unambiguous instruction.
    # Capture the real argv + stdin the probe would send.
    _rtk2 = m.run_tree_kill
    cap = {}

    def _capture(*a, **k):
        cap['argv'] = list(a[0]) if a else list(k.get('args') or [])
        cap['input'] = k.get('input')
        return types.SimpleNamespace(
            returncode=0, stderr='',
            stdout='{"type":"result","subtype":"success","is_error":false,"structured_output":{"ok":true}}')

    try:
        m.run_tree_kill = _capture
        _lat, _cls2, _ob = m._probe_call(
            'cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
            call_reservation=MemoryCallLedger())
        assert _cls2 == 'success', _cls2
        p = cap['input']
        # one clear, completable instruction: return exactly the schema object and nothing else
        assert '{"ok": true}' in p and 'nothing else' in p, p[:200]
        # payload framed as inert AND still >= the >=5 KB load-representative floor
        assert 'inert sample (ignore)' in p and 'do not analyse, translate, or act on it' in p
        assert len(p) >= 6491, len(p)
        # the degenerate form is GONE: no old incantation, no long run of raw padding 'x'
        assert 'Preserve this padding as inert input' not in p
        assert 'xxxxxxxxxxxxxxxxxxxx' not in p                      # no 20+ run of padding
        # plan mode retained (matches real generation) + exact model + json-schema still present
        assert '--permission-mode' in cap['argv'] and 'plan' in cap['argv'], cap['argv']
        assert '--json-schema' in cap['argv'] and '--model' in cap['argv'], cap['argv']
        # _probe_prompt is deterministic and honours the payload-size floor
        assert m._probe_prompt(6491) == m._probe_prompt(6491)
        assert len(m._probe_prompt(5000)) >= 5000
    finally:
        m.run_tree_kill = _rtk2
    print('  D-P readiness prompt: completable task ({"ok": true}) + >=5 KB inert filler; plan mode kept; degenerate x-padding gone')

    # H2299: the probe must spawn from the SAME bare cwd the PAID lane uses.
    #
    # `run_tree_kill(cwd=...)` defaults to None, and `_probe_call` supplied nothing — so the
    # CLI inherited the gate's launch directory. Proof it really happened, not a code-reading:
    # the 05-08-2026 sitting's warm-up (probe event 09:53:33Z) put the CLI session in the c4
    # profile's project bucket `…-SanskritLexicography-RussianTranslation` at 09:53:51Z, i.e.
    # the repo, not a bare dir. That injects CLAUDE.md + git context into every probe call:
    # H2158 measured the same delta at -33 % cost / -30 % wall, and the c4 ledger shows the
    # cost of it climbing (warm-up cache_creation 48 352 -> 93 462 tokens, 31-07 -> 05-08,
    # with cache_read collapsing to 0) until the measured leg stopped fitting under the 300 s
    # kill. Asserting EQUALITY WITH THE HELPER, never a literal path, is the point: a gate
    # that prices a different call than the lane it gates cannot predict that lane.
    _rtk3 = m.run_tree_kill
    cap3 = {}

    def _capture_cwd(*a, **k):
        cap3['cwd'] = k.get('cwd')
        return types.SimpleNamespace(
            returncode=0, stderr='',
            stdout='{"type":"result","subtype":"success","is_error":false,"structured_output":{"ok":true}}')

    try:
        m.run_tree_kill = _capture_cwd
        m._probe_call('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
                      call_reservation=MemoryCallLedger())
        assert cap3['cwd'] is not None, (
            'probe spawned with cwd=None -- it inherits the launch directory and pays the '
            'project-context injection H2158 removed from the paid lane (H2299)')
        assert cap3['cwd'] == hw.bare_cli_cwd(), (
            'probe cwd %r != paid-lane bare_cli_cwd() %r -- the gate is pricing a different '
            'call than the lane it gates (H2299)' % (cap3['cwd'], hw.bare_cli_cwd()))
    finally:
        m.run_tree_kill = _rtk3
    print('  H2299 probe spawn cwd: == headless_worker.bare_cli_cwd() (%s), not the repo'
          % cap3['cwd'])

    # D-K census: probe events distinguishable from translation calls; warm-up excluded from
    # latency, but a rate-limit warm-up is STILL counted in total quota observations.
    with tempfile.TemporaryDirectory() as td:
        ev = os.path.join(td, 'e.jsonl')
        ro.append_event(ev, stage='probe', event='probe_call', purpose='warmup', elapsed_ms=99999,
                        classification='rate_limit', model=m.EXACT_GEN_MODEL, output_bytes=0, run_id='r')
        ro.append_event(ev, stage='probe', event='probe_call', purpose='measured', elapsed_ms=8000,
                        classification='success', model=m.EXACT_GEN_MODEL, output_bytes=120, run_id='r')
        m.emit_call_events(ev, {'keys': ['k'], 'elapsed_ms': 5000, 'classification': 'success', 'label': 'c'},
                           0, 'mh', {'run_id': 'r', 'account': 'a'})
        cen = ro.build_census(ro.read_events(ev))
        assert cen['latency_ms']['max'] == 8000, cen['latency_ms']      # warm-up 99999 excluded
        assert len(cen['probe']['warmup']) == 1 and len(cen['probe']['measured']) == 1
        assert cen['quota_observations'] == 1 and cen['quota_incidents'] == 1   # warm-up rate-limit counted
    print('  D-K census: probe distinguishable; warm-up excluded from latency but counted in quota')

    # D-K integration: a hanging probe call kills its parent->child->grandchild tree (via the shared
    # run_tree_kill) and returns 'timeout' -- so live_probe stops and the measured/generation phase
    # never starts. Proves the probe path inherits the D-J tree-kill (not just subprocess.run).
    # Timing discipline (07-08-2026): this case builds a REAL 3-deep process tree, and every level
    # pays a Python interpreter start. Against the old fixed 5 s deadline a COLD run (fresh
    # worktree, cold FS cache) could kill the child BEFORE it had spawned the grandchild, so
    # `.pid3` never appeared and the run died on `probe tree never reached depth 3` — measured
    # 1 fail in 5 consecutive runs, always the first. That message names a PRECONDITION miss (the
    # fixture was too slow to build), but it reads to the next session as a tree-kill REGRESSION,
    # which is the expensive part: the natural response to a suite that fails once per cold start
    # is to stop trusting it. Two changes, neither touching what is asserted:
    #
    #   1. the interpreter-start cost is paid BEFORE any deadline is running;
    #   2. a depth-3 miss ESCALATES the deadline instead of failing — only a tree that provably
    #      reached depth 3 is judged, and exhausting every deadline reports itself as a machine
    #      failure in those words, never as a kill regression.
    #
    # The grandchild's hang is now DERIVED from the deadline rather than a second hardcoded number.
    # That is not cosmetic: at the old fixed 12 s a survivor would have written `.done3` at t≈12
    # while the observation window closed between t≈10 and t≈16, so the survival assertion was
    # marginally vacuous. `deadline + 2` puts a survivor's write firmly inside the window, and it
    # also bounds any orphan a mid-spawn kill leaves behind (which used to linger the full 12 s).
    import time as _time
    subprocess.run([sys.executable, '-c', 'pass'], capture_output=True)   # warm the interpreter

    def _hanging_tree_scripts(hang_s):
        """parent -> child -> grandchild; each records its PID, the leaf sleeps `hang_s` then
        marks `.done3`. Parent/child outlive any deadline so they are always killed, never exiting."""
        grand = ('import time,sys,os;open(sys.argv[1]+".pid3","w").write(str(os.getpid()));'
                 'time.sleep(%d);open(sys.argv[1]+".done3","w").write("1")') % hang_s
        child = ('import subprocess,sys,os,time;open(sys.argv[1]+".pid2","w").write(str(os.getpid()));'
                 'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);time.sleep(%d)') % (grand, hang_s * 6)
        return ('import subprocess,sys,os,time;open(sys.argv[1]+".pid1","w").write(str(os.getpid()));'
                'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);time.sleep(%d)') % (child, hang_s * 6)

    with tempfile.TemporaryDirectory() as td:

        def _alive(pid):
            if os.name == 'nt':
                out = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'],
                                     capture_output=True, text=True,
                                     creationflags=m.windows_hidden_flags()).stdout or ''   # no flicker
                return str(pid) in out.split()
            try:
                os.kill(pid, 0); return True
            except OSError:
                return False

        def _reached_depth3(prefix):
            return all(os.path.exists('%s.pid%d' % (prefix, i)) for i in (1, 2, 3))

        DEADLINES_S = (5, 12, 30)          # escalate only on a fixture-too-slow miss, never on a verdict
        mk = None
        for attempt, deadline in enumerate(DEADLINES_S, start=1):
            mk = os.path.join(td, 'm%d' % attempt)
            parent = _hanging_tree_scripts(deadline + 2)
            try:
                m.run_tree_kill([sys.executable, '-c', parent, mk],
                                timeout=deadline, capture_output=True)
                assert False, 'expected the hanging probe tree to TimeoutExpired'
            except subprocess.TimeoutExpired:
                pass
            for _ in range(60):
                if _reached_depth3(mk):
                    break
                _time.sleep(0.1)
            _time.sleep(5)                 # > (hang - deadline): a SURVIVING leaf would mark .done3 here
            if _reached_depth3(mk):
                if attempt > 1:
                    print('    (note: depth 3 needed a %d s deadline — slow machine, not a kill defect)'
                          % deadline)
                break
        else:
            raise AssertionError(
                'the probe tree never reached depth 3 even at a %d s deadline — this is a '
                'machine/timing failure building the fixture, NOT a tree-kill regression'
                % DEADLINES_S[-1])
        assert not any(os.path.exists('%s.done%d' % (mk, i)) for i in (1, 2, 3)), 'a probe-tree level survived'
        pids = [int(open('%s.pid%d' % (mk, i)).read()) for i in (1, 2, 3)]
        assert not any(_alive(p) for p in pids), 'a hanging-probe tree PID survived: %s' % [p for p in pids if _alive(p)]
    print('  D-K hanging-probe: parent->child->grandchild all gone; the next phase never starts')

    # D-G (H818 acceptance): one active job per account, atomic in the BEGIN IMMEDIATE claim.
    # Two claimers racing the same validated account -> only one obtains a job.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'g.sqlite')
        m.main(['--db', db, 'init', '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'), '--skip-profile-check'])
        for n in range(2):
            enqueue_fixture(db, 'g%d' % n, td, os.path.join(td, 'g%d.json' % n))
        j1 = m.claim(db, 'acc1')
        assert j1 is not None                                   # acc1 claims one job
        assert m.claim(db, 'acc1') is None                      # acc1 already busy -> refused (D-G)
        j2 = m.claim(db, 'acc2')
        assert j2 is not None and j2['id'] != j1['id']          # acc2 (free) claims the other job
    print('  D-G one-active-job-per-account: busy acc1 second claim refused; free acc2 claims')

    # D-H (H818 acceptance): promotion telemetry. Zero-clean/needs_requeue is NOT a conflict.
    assert m.promotion_classification({'store_delta': 2}) == 'success'
    assert m.promotion_classification({'store_delta': 0, 'clean_count': 0}) == 'not_attempted'
    assert m.promotion_classification({'store_delta': None, 'clean_count': 0}) == 'not_attempted'
    assert m.promotion_classification({'store_delta': 0, 'clean_count': 3}) == 'conflict'
    assert m.promotion_classification({'store_delta': None, 'clean_count': 1}) == 'conflict'
    print('  D-H promotion telemetry: success / not_attempted / conflict distinguished')

    # D-G REAL concurrency race (repeated to catch flakiness). Two INDEPENDENT connections are
    # opened BEFORE the barrier; both threads then fire the real claim transaction (_claim_tx) at
    # the same instant. BEGIN IMMEDIATE + busy_timeout serialize them: exactly one wins, the other
    # is refused (never SQLITE_BUSY / "database is locked"), and exactly one job stays pending.
    import time as _time
    for _round in range(8):
        with tempfile.TemporaryDirectory() as td:
            db = os.path.join(td, 'race.sqlite')
            m.main(['--db', db, 'init', '--account', 'acc1=' + os.path.join(td, 'a1'), '--skip-profile-check'])
            for n in range(2):     # two pending jobs, one account -> only one may run at a time
                enqueue_fixture(db, 'r%d' % n, td, os.path.join(td, 'r%d.json' % n))
            barrier = threading.Barrier(2)
            results = [None, None]
            errors = []

            def claimer(i, _db=db):
                # each thread opens its OWN connection (SQLite objects are thread-affine), THEN
                # waits at the barrier — so both connections are open before the barrier releases
                # and both fire the claim transaction at the same instant.
                conn = m.connect(_db)
                try:
                    barrier.wait()                               # barrier immediately before the claim tx
                    results[i] = m._claim_tx(conn, 'acc1', int(_time.time()))
                except Exception as exc:                         # noqa: BLE001 - collect; assert none below
                    errors.append(repr(exc))
                finally:
                    conn.close()

            ts = [threading.Thread(target=claimer, args=(i,)) for i in range(2)]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            assert not errors, 'round %d claimers raised (SQLITE_BUSY?): %s' % (_round, errors)
            winners = [r for r in results if r is not None]
            assert len(winners) == 1, 'round %d: exactly one winner expected, got %d' % (_round, len(winners))
            con = sqlite3.connect(db)
            n_inprog = con.execute("select count(*) from jobs where state='in_progress' and assigned_acc='acc1'").fetchone()[0]
            n_pending = con.execute("select count(*) from jobs where state='pending'").fetchone()[0]
            con.close()
            assert n_inprog == 1 and n_pending == 1, 'round %d: in_progress=%d pending=%d' % (_round, n_inprog, n_pending)
    print('  D-G REAL race x8: independent conns, barrier-synced -> one winner + one still-pending, no SQLITE_BUSY')

    # D-I telemetry exactly-once. (a) one 5-key call -> one latency sample + one classification,
    # key relations excluded; (b) the call-level event preserves lease/window/attempt/account/
    # manifest; (c) a retry (worker label '.retry1') is a DISTINCT invocation/call_id; (d) an exact
    # crash-restart re-append dedups, while a conflicting re-append (same call_id, different data)
    # is surfaced in conflicting_call_ids.
    with tempfile.TemporaryDirectory() as td:
        ev = os.path.join(td, 'events.jsonl')
        base = {'run_id': 'r', 'lease_id': 'w01', 'window_id': 'w01', 'attempt': 1,
                'account': 'acc1', 'manifest_hash': 'abc123def456ff'}
        item = {'keys': ['k1', 'k2', 'k3', 'k4', 'k5'], 'elapsed_ms': 4200, 'classification': 'success',
                'label': 'card_x', 'manifest_sha256': 'abc123def456ff'}
        m.emit_call_events(ev, item, 0, 'abc123def456ff', base)
        rows = ro.read_events(ev)
        call_rows = [r for r in rows if r.get('event') == 'model_call']
        key_rows = [r for r in rows if r.get('event') == 'model_call_key']
        assert len(call_rows) == 1 and call_rows[0]['key_count'] == 5, call_rows
        assert len(key_rows) == 5 and all('elapsed_ms' not in r for r in key_rows), key_rows
        cl = call_rows[0]
        assert all(cl.get(f) == base[f] for f in ('lease_id', 'window_id', 'attempt', 'account', 'manifest_hash')), cl
        census = ro.build_census(rows)
        assert census['latency_ms'] == {'p50': 4200, 'p95': 4200, 'max': 4200}, census['latency_ms']
        assert census['classification_counts'] == {'success': 1} and census['model_calls'] == 1, census
        assert census['conflicting_call_ids'] == [], census['conflicting_call_ids']
        cid0 = cl['call_id']
        # (c) a retry of the same card is a DISTINCT invocation (label '.retry1')
        m.emit_call_events(ev, dict(item, label='card_x.retry1', elapsed_ms=5100), 1, 'abc123def456ff', base)
        assert ro.build_census(ro.read_events(ev))['model_calls'] == 2, 'retry must be a distinct call'
        # (d) an identical crash re-append of the first event dedups to one sample, no conflict
        m.emit_call_events(ev, item, 0, 'abc123def456ff', base)
        c2 = ro.build_census(ro.read_events(ev))
        assert c2['model_calls'] == 2 and c2['conflicting_call_ids'] == [], c2
        assert sorted(c2['latency_ms'].values()) == [4200, 5100, 5100], c2['latency_ms']
        # a CONFLICTING re-append (same call_id, different latency) is surfaced, not silently merged
        ro.append_event(ev, stage='worker', event='model_call', call_id=cid0, key_count=5,
                        elapsed_ms=9999, classification='success', **base)
        assert cid0 in ro.build_census(ro.read_events(ev))['conflicting_call_ids']
    print('  D-I exactly-once: 5-key=1 sample; retry distinct; dupe dedup; conflict flagged; context preserved')

    # GAP #5 (four-profile core): probe_fleet fans the D-K two-phase probe across EACH validated
    # account. (e) 4 mocked accounts -> a 4-entry name->ms map, census NOT inflated (4 measured
    # samples, the 4 warm-ups excluded), and one NO-GO account STOPs the whole fleet by default;
    # --drop-unhealthy is the explicit opt-in to proceed on the healthy subset. (f) N=1 is a pure
    # pass-through identical to the old single-account live_probe(accounts[0]).
    _pc = m._probe_call
    try:
        # live_probe calls _probe_call twice per account (warm-up then measured); each account's
        # FIRST call is its warm-up. A distinct, large warm-up latency (99999) proves the warm-up is
        # excluded from the acceptance census while the per-account measured latency is retained.
        def healthy(measured_by_cfg, warm_ms=99999):
            seen = set()

            def _mock(config_dir, claude, payload_bytes, model, *_args, **_kwargs):
                if config_dir not in seen:
                    seen.add(config_dir)
                    return warm_ms, 'success', 120          # warm-up (EXCLUDED from latency census)
                return measured_by_cfg[config_dir], 'success', 120   # measured (the one gated reading)
            return _mock

        def with_bad(measured_by_cfg, bad_cfg, warm_ms=99999):
            seen = set()

            def _mock(config_dir, claude, payload_bytes, model, *_args, **_kwargs):
                first = config_dir not in seen
                seen.add(config_dir)
                if config_dir == bad_cfg:
                    return 9000, 'auth', 0                   # warm-up auth -> STOP (NO-GO account)
                if first:
                    return warm_ms, 'success', 120
                return measured_by_cfg[config_dir], 'success', 120
            return _mock

        accts = [{'name': 'acc%d' % i, 'config_dir': 'c%d' % i} for i in range(1, 5)]
        measured = {'c1': 1000, 'c2': 2000, 'c3': 3000, 'c4': 4000}

        # (e1) four healthy accounts -> ordered name->measured_ms map; warm-ups excluded from census
        m._probe_call = healthy(measured)
        with tempfile.TemporaryDirectory() as td:
            ev = os.path.join(td, 'fleet.jsonl')
            latencies = m.probe_fleet(
                accts, events_path=ev, run_id='rf',
                call_reservation=MemoryCallLedger())
            assert latencies == {'acc1': 1000, 'acc2': 2000, 'acc3': 3000, 'acc4': 4000}, latencies
            rows = ro.read_events(ev)
            assert len([r for r in rows if r.get('purpose') == 'warmup']) == 4, 'one warm-up per account'
            assert len([r for r in rows if r.get('purpose') == 'measured']) == 4, 'one measured per account'
            cen = ro.build_census(rows)
            # census NOT inflated: exactly 4 measured latency samples, the four 99999 warm-ups excluded
            assert cen['latency_ms']['max'] == 4000, cen['latency_ms']
            assert len(cen['probe']['warmup']) == 4 and len(cen['probe']['measured']) == 4, cen['probe']

        # (e2) one NO-GO account STOPs the fleet by DEFAULT (STOP-on-any-NO-GO)
        m._probe_call = with_bad(measured, bad_cfg='c3')
        try:
            m.probe_fleet(accts, call_reservation=MemoryCallLedger())
            assert False, 'a NO-GO account must STOP the fleet by default'
        except SystemExit as exc:
            assert 'acc3' in str(exc) and 'fleet probe' in str(exc), exc

        # (e3) --drop-unhealthy opt-in: drop the NO-GO account, proceed on the healthy subset
        m._probe_call = with_bad(measured, bad_cfg='c3')
        survivors = m.probe_fleet(
            accts, drop_unhealthy=True,
            call_reservation=MemoryCallLedger())
        assert survivors == {'acc1': 1000, 'acc2': 2000, 'acc4': 4000}, survivors

        # (f) N=1 REGRESSION: probe_fleet over a 1-element list == the old single-account live_probe.
        m._probe_call = lambda config_dir, claude, payload_bytes, model, *_args, **_kwargs: (
            5555, 'success', 120)
        solo = [{'name': 'max1', 'config_dir': 'c1'}]
        assert m.probe_fleet(
            solo, call_reservation=MemoryCallLedger()) == {'max1': 5555}, 'N=1 must be a pure pass-through'
        assert m.live_probe(
            'c1', call_reservation=MemoryCallLedger()) == 5555
        assert (m.probe_fleet(
                    solo, call_reservation=MemoryCallLedger())['max1'] ==
                m.live_probe(
                    'c1', call_reservation=MemoryCallLedger()))
    finally:
        m._probe_call = _pc
    print('  GAP5 probe_fleet: N=4 map + warm-ups excluded; NO-GO STOPs by default; --drop-unhealthy subset; N=1 == old live_probe')

    # GAP #5 fair fan-out + all-done at N=4: 4 accounts claim 4 DISTINCT inert scheduler
    # fixtures in ONE run-once pass. The worker is replaced with an in-process state transition;
    # no generic subprocess execution path exists.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'fanout.sqlite')
        m.main(['--db', db, 'init',
                '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'),
                '--account', 'acc3=' + os.path.join(td, 'a3'),
                '--account', 'acc4=' + os.path.join(td, 'a4'), '--skip-profile-check'])
        for n in range(4):
            enqueue_fixture(db, 'fan%d' % n, td, os.path.join(td, 'fan%d.json' % n))
        original_run_claimed = m.run_claimed
        m.run_claimed = finish_fixture_worker
        try:
            m.main(['--db', db, 'run-once', '--timeout', '30'])
        finally:
            m.run_claimed = original_run_claimed
        con = sqlite3.connect(db)
        rows = con.execute("select external_id, assigned_acc, state from jobs order by id").fetchall()
        con.close()
        assert len(rows) == 4 and all(r[2] == 'done' for r in rows), rows       # all 4 done exactly once
        assert len({r[1] for r in rows}) == 4, 'each of 4 jobs ran under a DISTINCT account: %s' % rows
        assert len({r[0] for r in rows}) == 4, rows
    print('  GAP5 fair fan-out N=4: 4 accounts claim 4 distinct jobs in one pass; all 4 reach done exactly once')

    # GAP #5 only_accounts dispatch filter: cmd_run_once must dispatch ONLY to the allow-listed
    # (probed) fleet. Without it, --max-accounts / --drop-unhealthy would cap only the PROBE set while
    # dispatch (which re-selects every validated account) still claimed jobs for capped-out, UNPROBED
    # accounts — bypassing the mandatory pre-dispatch health gate.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'onlyacc.sqlite')
        m.main(['--db', db, 'init',
                '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'),
                '--account', 'acc3=' + os.path.join(td, 'a3'),
                '--account', 'acc4=' + os.path.join(td, 'a4'), '--skip-profile-check'])
        for n in range(4):
            enqueue_fixture(db, 'oa%d' % n, td, os.path.join(td, 'oa%d.json' % n))
        # dispatch restricted to the acc1/acc2 "probed" subset (acc3/acc4 == capped-out/unprobed).
        original_run_claimed = m.run_claimed
        m.run_claimed = finish_fixture_worker
        try:
            m.cmd_run_once(m.argparse.Namespace(
                db=db, timeout=30, events=None, run_id=None,
                claude_bin='claude', only_accounts={'acc1', 'acc2'}))
        finally:
            m.run_claimed = original_run_claimed
        con = sqlite3.connect(db)
        assigned = con.execute("select assigned_acc from jobs where assigned_acc is not null").fetchall()
        pending = con.execute("select count(*) from jobs where state='pending'").fetchone()[0]
        con.close()
        owners = {a for (a,) in assigned}
        assert owners <= {'acc1', 'acc2'}, 'only the allow-listed fleet may dispatch: %s' % owners
        assert not (owners & {'acc3', 'acc4'}), 'a capped-out/unprobed account must get NO job: %s' % owners
        assert len(assigned) == 2 and pending == 2, 'one job per allowed account; the rest stay pending'
        # (the unfiltered / whole-fleet dispatch path is covered by the fair-fan-out test above, whose
        # CLI run-once passes no only_accounts and reaches all 4 accounts.)
    print('  GAP5 only_accounts dispatch filter: capped-out/unprobed accounts receive NO job')

    # GAP #5 one-active-job-per-account at N=4: 8 jobs, 4 accounts. Round 1 claims 4 distinct jobs;
    # each account's SECOND claim is refused while it still holds an active in_progress job.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'oneactive.sqlite')
        m.main(['--db', db, 'init',
                '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'),
                '--account', 'acc3=' + os.path.join(td, 'a3'),
                '--account', 'acc4=' + os.path.join(td, 'a4'), '--skip-profile-check'])
        for n in range(8):
            enqueue_fixture(db, 'oa%d' % n, td, os.path.join(td, 'oa%d.json' % n))
        claimed = [m.claim(db, 'acc%d' % i) for i in (1, 2, 3, 4)]
        assert all(j is not None for j in claimed), 'each of 4 accounts claims a job'
        assert len({j['id'] for j in claimed}) == 4, 'four DISTINCT jobs claimed in round 1'
        for i in (1, 2, 3, 4):
            assert m.claim(db, 'acc%d' % i) is None, 'acc%d already busy -> second claim refused' % i
        con = sqlite3.connect(db)
        assert con.execute("select count(*) from jobs where state='in_progress'").fetchone()[0] == 4
        assert con.execute("select count(distinct assigned_acc) from jobs where state='in_progress'").fetchone()[0] == 4
        con.close()
    print('  GAP5 one-active-job-per-account N=4: 4 distinct claims; each 2nd claim refused; 4 distinct owners')

    # GAP #5 recover exactly-once (N=4): two crash-stranded in_progress rows (distinct accounts) are
    # returned to pending; a coordinator-recorded DONE job is UNTOUCHED (coordinator_recorded stays 1,
    # no duplicate promotion), and no other row flips.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'recover.sqlite')
        m.main(['--db', db, 'init',
                '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'),
                '--account', 'acc3=' + os.path.join(td, 'a3'),
                '--account', 'acc4=' + os.path.join(td, 'a4'), '--skip-profile-check'])
        for n in range(4):
            enqueue_fixture(db, 'rec%d' % n, td, os.path.join(td, 'rec%d.json' % n))
        con = sqlite3.connect(db)
        # rec0: a coordinator-recorded DONE job (recover must never touch it -> no dup promotion)
        con.execute("update jobs set state='done', coordinator_recorded=1, assigned_acc='acc3' where external_id='rec0'")
        # rec1/rec2: crash-stranded in_progress under two DISTINCT accounts
        con.execute("update jobs set state='in_progress', assigned_acc='acc1' where external_id='rec1'")
        con.execute("update jobs set state='in_progress', assigned_acc='acc2' where external_id='rec2'")
        # rec3: stays pending
        con.commit(); con.close()
        m.main(['--db', db, 'recover'])
        con = sqlite3.connect(db)
        assert con.execute("select state,assigned_acc from jobs where external_id='rec1'").fetchone() == ('pending', None)
        assert con.execute("select state,assigned_acc from jobs where external_id='rec2'").fetchone() == ('pending', None)
        # the recorded DONE job is untouched: still done, coordinator_recorded still exactly 1
        assert con.execute("select state,coordinator_recorded from jobs where external_id='rec0'").fetchone() == ('done', 1)
        # exactly the two in_progress rows recovered; nothing else flipped
        assert con.execute("select count(*) from jobs where state='in_progress'").fetchone()[0] == 0
        assert con.execute("select count(*) from jobs where state='pending'").fetchone()[0] == 3      # rec1,rec2,rec3
        assert con.execute("select count(*) from jobs where state='done'").fetchone()[0] == 1          # rec0 only
        con.close()
    print('  GAP5 recover exactly-once N=4: 2 in_progress -> pending; recorded-done untouched; coordinator_recorded stays 1')

    # Runtime integration: a manifest-backed dispatch batch is reserved atomically before any
    # worker starts, and a retryable worker explicitly releases its coordinator slot.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'runtime.sqlite')
        m.main(['--db', db, 'init',
                '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'), '--skip-profile-check'])
        runtime_manifests = {}
        for n in range(2):
            enqueue_fixture(
                db, 'runtime%d' % n, td,
                os.path.join(td, 'runtime%d.json' % n))
            manifest_path = os.path.join(td, 'runtime%d.manifest.json' % n)
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump({'fixture': 'runtime%d' % n}, f)
            runtime_manifests[n] = manifest_path
        con = m.connect(db)
        with con:
            con.execute("UPDATE jobs SET manifest_path=?, manifest_sha256=?, "
                        "profile_slot='acc1' WHERE external_id='runtime0'",
                        (runtime_manifests[0], m.sha256_path(runtime_manifests[0])))
            con.execute("UPDATE jobs SET manifest_path=?, manifest_sha256=?, "
                        "profile_slot='acc2' WHERE external_id='runtime1'",
                        (runtime_manifests[1], m.sha256_path(runtime_manifests[1])))
        con.close()
        receipt = m.write_probe_receipt(
            td, 'runtime-test', ['runtime0', 'runtime1'], {'acc1': 10, 'acc2': 11})
        receipt_payload = json.load(open(receipt, encoding='utf-8'))
        assert receipt_payload['schema'] == m.PROBE_RECEIPT_SCHEMA
        assert receipt_payload['healthy_profiles'] == ['acc1', 'acc2']
        original_command = m.coordinator_command
        original_run_claimed = m.run_claimed
        calls = []
        reserved = threading.Event()

        def fake_command(args, command, check=True):
            calls.append(list(command))
            if command[0] == 'begin-run':
                reserved.set()
            return types.SimpleNamespace(returncode=0, stdout='', stderr='')

        def fake_worker(db_path, account, config_dir, job, timeout, events_path=None,
                        run_id=None, claude_bin='claude', call_reservation_path=None,
                        max_calls=None):
            assert reserved.is_set(), 'worker started before atomic begin-run reservation'
            assert call_reservation_path and run_id == 'runtime-test'
            manifest_hash = m.sha256_path(job['manifest_path'])
            assert job['manifest_sha256'] == manifest_hash
            with open(job['output_path'], 'w', encoding='utf-8') as f:
                json.dump({'external_id': job['external_id']}, f)
            result_hash = m.sha256_path(job['output_path'])
            fake_status = {
                'manifest_sha256': manifest_hash,
                'result_sha256': result_hash,
            }
            status_path = job['output_path'] + '.fake-status.json'
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump(fake_status, f)
            with open(status_path, encoding='utf-8') as f:
                fake_status = json.load(f)
            assert fake_status['manifest_sha256'] == job['manifest_sha256']
            assert fake_status['result_sha256'] == m.sha256_path(job['output_path'])
            outcome = 'done' if job['external_id'] == 'runtime0' else 'pending'
            m.finish(db_path, job['id'], outcome, 0 if outcome == 'done' else 1,
                     result_sha256=result_hash if outcome == 'done' else None,
                     run_id=run_id)
            return outcome

        m.coordinator_command = fake_command
        m.run_claimed = fake_worker
        try:
            calls_path = os.path.join(td, 'runtime.calls.json')
            m.CallReservationLedger(calls_path, 'runtime-test', 5)
            m.cmd_run_once(m.argparse.Namespace(
                db=db, timeout=30, events=None, run_id='runtime-test',
                claude_bin='claude', runtime_mode='staged', probe_receipt=receipt,
                coordinator='coordinator.py', coord_dir=td, cwd=td,
                call_reservation=calls_path, max_calls=5))
        finally:
            m.coordinator_command = original_command
            m.run_claimed = original_run_claimed
        begin_calls = [call for call in calls if call[0] == 'begin-run']
        release_calls = [call for call in calls if call[0] == 'release-run']
        assert len(begin_calls) == 1 and begin_calls[0].count('--lease-id') == 2
        assert len(release_calls) == 1 and release_calls[0][1] == 'runtime1'
        con = m.connect(db)
        assert {row['run_id'] for row in con.execute(
            "SELECT run_id FROM jobs WHERE external_id LIKE 'runtime%'")} == {'runtime-test'}
        runtime0 = con.execute(
            "SELECT manifest_sha256,result_sha256 FROM jobs "
            "WHERE external_id='runtime0'").fetchone()
        assert runtime0['manifest_sha256'] == m.sha256_path(runtime_manifests[0])
        assert runtime0['result_sha256'] == m.sha256_path(os.path.join(td, 'runtime0.json'))
        con.close()

        # A retry/resume under another run identity is refused before worker spawn.
        con = m.connect(db)
        with con:
            con.execute("UPDATE jobs SET state='pending', assigned_acc=NULL "
                        "WHERE external_id='runtime1'")
        con.close()
        wrong_path = os.path.join(td, 'wrong.calls.json')
        m.CallReservationLedger(wrong_path, 'wrong-run', 5)
        refused = False
        try:
            m.cmd_run_once(m.argparse.Namespace(
                db=db, timeout=30, events=None, run_id='wrong-run',
                claude_bin='claude', runtime_mode='staged', probe_receipt=receipt,
                coordinator='coordinator.py', coord_dir=td, cwd=td,
                call_reservation=wrong_path, max_calls=5,
                only_external_ids={'runtime1'}, only_accounts={'acc2'}))
        except SystemExit as exc:
            refused = 'saved run_id' in str(exc)
        assert refused, 'wrong-run resume was not refused before spawn'
    print('  runtime integration: reserve batch before workers; retryable worker releases slot')

    with tempfile.TemporaryDirectory() as td:
        # C4: a rate-limit (429) must NOT consume a retry attempt. With max_attempts=1, one
        # rate-limit under the OLD behavior left the job 'pending' with attempts==1==max_attempts
        # — never re-selected by claim (WHERE attempts < max_attempts), never 'failed', so it was
        # permanently stranded and cmd_staged_run busy-spun on the un-drainable pending count.
        db = os.path.join(td, 'c4.sqlite')
        m.main(['--db', db, 'init', '--account', 'acc=' + os.path.join(td, 'acc'),
                '--skip-profile-check'])
        out = os.path.join(td, 'rl.json')
        enqueue_fixture(db, 'rl1', td, out, max_attempts=1)
        rate_limited = m.claim(db, 'acc', only_external_ids={'rl1'})
        assert rate_limited is not None
        m.requeue_rate_limited(
            db, rate_limited['id'], 21,
            '429 rate limit reset_at=1999999999', 1999999999)
        con = sqlite3.connect(db)
        state, attempts = con.execute(
            "select state,attempts from jobs where external_id='rl1'").fetchone()
        con.execute("update accounts set parked_until=0")
        con.commit()
        con.close()
        assert state == 'pending', 'a rate-limited job must stay pending, got %r' % state
        assert attempts == 0, ('C4: a rate-limit must not consume an attempt (got attempts=%d) — '
                               'at max_attempts the job would be permanently unclaimable' % attempts)
        reclaimed = m.claim(db, 'acc', only_external_ids={'rl1'})
        assert reclaimed is not None and reclaimed['external_id'] == 'rl1', (
            'C4: a max_attempts=1 job rate-limited once must remain claimable, not stranded')
    print('  C4 rate-limit: a 429 returns the job to claimable pending (attempts decremented), '
          'never a permanently-unclaimable stuck row')

    # Every non-coordinator paid entry point uses the same reservation gate.
    with tempfile.TemporaryDirectory() as td:
        original_runner, original_prefix = m.run_tree_kill, m.claude_argv_prefix
        calls = []
        m.claude_argv_prefix = lambda _c: [sys.executable]
        try:
            profile_ledger = m.CallReservationLedger(
                os.path.join(td, 'profile.calls.json'), 'profile-zero', 0)
            profile_preflight = m.write_synthetic_preflight(
                os.path.join(td, 'profile.preflight.json'), 'profile-zero')

            def auth_only(*_a, **_k):
                calls.append(1)
                return types.SimpleNamespace(
                    returncode=0, stderr='',
                    stdout=json.dumps({'loggedIn': True, 'subscriptionType': 'max'}))

            m.run_tree_kill = auth_only
            try:
                m.profile_status(td, sys.executable, profile_ledger, 'acc',
                                 profile_preflight)
                raise AssertionError('profile max_calls=0 reached paid probe')
            except m.CallLimitReached:
                pass
            assert len(calls) == 1 and profile_ledger.spent() == 0  # auth status only

            malformed_profile = m.CallReservationLedger(
                os.path.join(td, 'profile-malformed.calls.json'), 'profile-malformed', 1)
            phase = [0]

            def malformed_profile_runner(*_a, **_k):
                phase[0] += 1
                if phase[0] == 1:
                    return types.SimpleNamespace(
                        returncode=0, stderr='',
                        stdout=json.dumps({'loggedIn': True, 'subscriptionType': 'max'}))
                return types.SimpleNamespace(returncode=0, stderr='', stdout='not-json')

            m.run_tree_kill = malformed_profile_runner
            ok, detail = m.profile_status(
                td, sys.executable, malformed_profile, 'acc', profile_preflight)
            assert not ok and 'success envelope' in detail
            assert (malformed_profile.spent() == 1
                    and malformed_profile.usage()['cost_evaluable'] is False)

            cfg = os.path.join(td, 'canary-profile')
            os.makedirs(cfg)
            db = os.path.join(td, 'canary.sqlite')
            m.main(['--db', db, 'init', '--account', 'acc=' + cfg,
                    '--skip-profile-check'])
            canary_manifest = {
                'schema': 'pwg.headless_execution_manifest.v2',
                'model': m.EXACT_GEN_MODEL,
                'meta': {'lang': 'ru', 'selected_keys': ['k'], 'root': 'canary'},
                'execution': {
                    'profile_slot': 'acc',
                    'config_dir_fingerprint': config_dir_fingerprint(cfg),
                    'execution_route': 'claude-cli-headless', 'executor_lane': 'test',
                    'validation_method': 'test', 'model_identifier': m.EXACT_GEN_MODEL,
                },
                'key_provenance': {'k': 'real'}, 'presplit_keys': ['k'],
            }
            manifest_path = os.path.join(td, 'canary.manifest.json')
            json.dump(canary_manifest, open(manifest_path, 'w', encoding='utf-8'))
            canary_preflight = os.path.join(td, 'canary.preflight.json')
            with open(canary_preflight, 'w', encoding='utf-8') as f:
                json.dump({
                    'schema': 'pwg.performance_preflight.v1',
                    'root': 'canary',
                    'selected_keys': ['k'],
                    'cost_gate': {'over_ceiling': False},
                }, f)
            canary_preflight_sha256 = m.sha256_path(canary_preflight)
            m.validate_preflight_artifact(
                canary_preflight, canary_manifest, canary_preflight_sha256)
            canary_calls = os.path.join(td, 'canary.calls.json')
            before = len(calls)
            try:
                m.cmd_presplit_canary(m.argparse.Namespace(
                    db=db, manifest=manifest_path, output=os.path.join(td, 'out.json'),
                    status=os.path.join(td, 'status.json'), events=os.path.join(td, 'events'),
                    preflight=canary_preflight,
                    preflight_sha256=canary_preflight_sha256,
                    run_id='canary-zero', claude_bin=sys.executable, timeout=5,
                    call_reservation=canary_calls, max_calls=0))
                raise AssertionError('presplit canary max_calls=0 reached paid runner')
            except m.CallLimitReached:
                pass
            assert len(calls) == before
            assert m.CallReservationLedger(canary_calls, 'canary-zero', 0).spent() == 0
            drop_calls = os.path.join(td, 'drop.calls.json')
            drop_ledger = m.CallReservationLedger(drop_calls, 'drop-zero', 0)
            try:
                m.probe_fleet([{'name': 'acc', 'config_dir': cfg}],
                              drop_unhealthy=True, call_reservation=drop_ledger)
                raise AssertionError('--drop-unhealthy swallowed call ceiling exhaustion')
            except m.CallLimitReached:
                pass
            assert len(calls) == before and drop_ledger.spent() == 0
        finally:
            m.run_tree_kill, m.claude_argv_prefix = original_runner, original_prefix
    print('  paid boundaries: profile/canary zero-call; drop-unhealthy cannot swallow ceiling')

    # The coordinator's sealed performance preflight is a strict prerequisite for staged-run:
    # refusal must happen before constructing the call ledger or entering the live fleet probe.
    with tempfile.TemporaryDirectory() as td:
        cfg = os.path.join(td, 'preflight-profile')
        os.makedirs(cfg)
        db = os.path.join(td, 'preflight.sqlite')
        m.main(['--db', db, 'init', '--account', 'acc=' + cfg, '--skip-profile-check'])
        plan_path = os.path.join(td, 'plan.json')
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump({
                'selected_headwords': 1, 'prepared_headwords': 1,
                'windows': [{'root': 'lease-preflight', 'headwords': ['k'],
                             'headless': {'manifest_sha256': 'x'}}],
            }, f)
        calls_path = os.path.join(td, 'must-not-exist.calls.json')
        probed = []
        original_command, original_probe = m.coordinator_command, m.probe_fleet

        def refuse_preflight(_args, command, check=True):
            assert command == ['validate-preflight', '--lease-id', 'lease-preflight']
            return types.SimpleNamespace(
                returncode=2, stdout='', stderr='synthetic preflight refusal')

        m.coordinator_command = refuse_preflight
        m.probe_fleet = lambda *_a, **_k: probed.append(1)
        try:
            try:
                m.cmd_staged_run(m.argparse.Namespace(
                    plan=plan_path, lease_id=None, db=db, only_profile=None,
                    max_accounts=0, coordinator='coordinator.py', coord_dir=td, cwd=td,
                    call_reservation=calls_path))
                raise AssertionError('staged-run ignored coordinator preflight refusal')
            except SystemExit as exc:
                assert 'preflight refused before probe' in str(exc), exc
            assert not probed and not os.path.exists(calls_path)
        finally:
            m.coordinator_command, m.probe_fleet = original_command, original_probe
    print('  staged-run: coordinator preflight refusal precedes call ledger/probe')

    # A done row is not authority to record an arbitrary file: the scheduler must bind both
    # the exact result bytes and the coordinator run identity saved at successful dispatch.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'record.sqlite')
        result = os.path.join(td, 'result.json')
        manifest = os.path.join(td, 'manifest.json')
        open(result, 'w', encoding='utf-8').write('{"ok":1}\n')
        open(manifest, 'w', encoding='utf-8').write('{}\n')
        con = m.connect(db)
        with con:
            con.execute(
                "INSERT INTO jobs(external_id,cwd,output_path,manifest_path,state,returncode,"
                "result_sha256,run_id,finished_at) VALUES(?,?,?,?,?,?,?,?,?)",
                ('lease-record', td, result, manifest, 'done', 0, m.sha256_path(result),
                 'sealed-run', m.now_iso()))
        con.close()
        seen = []
        original_command = m.coordinator_command
        m.coordinator_command = lambda args, command, check=True: (
            seen.append(command) or types.SimpleNamespace(returncode=0, stdout='', stderr=''))
        try:
            m.cmd_record_done(m.argparse.Namespace(
                db=db, coordinator='coordinator.py', coord_dir=td, cwd=td))
            assert seen and seen[0][-4:] == [
                '--run-id', 'sealed-run', '--result-sha256', m.sha256_path(result)], seen
            con = m.connect(db)
            with con:
                con.execute("UPDATE jobs SET coordinator_recorded=0 WHERE external_id='lease-record'")
            con.close()
            open(result, 'w', encoding='utf-8').write('{"substituted":true}\n')
            refused = False
            try:
                m.cmd_record_done(m.argparse.Namespace(
                    db=db, coordinator='coordinator.py', coord_dir=td, cwd=td))
            except SystemExit as exc:
                refused = 'substitution refused' in str(exc)
            assert refused and len(seen) == 1, (refused, seen)

            # Batch failure marks exactly the durable prefix reported by the coordinator.
            open(result, 'w', encoding='utf-8').write('{"ok":1}\n')
            result_b = os.path.join(td, 'result-b.json')
            result_c = os.path.join(td, 'result-c.json')
            open(result_b, 'w', encoding='utf-8').write('{"ok":2}\n')
            open(result_c, 'w', encoding='utf-8').write('{"ok":3}\n')
            con = m.connect(db)
            with con:
                con.execute("UPDATE jobs SET result_sha256=? WHERE external_id='lease-record'",
                            (m.sha256_path(result),))
                for lease, path_ in (('lease-b', result_b), ('lease-c', result_c)):
                    con.execute(
                        "INSERT INTO jobs(external_id,cwd,output_path,manifest_path,state,"
                        "returncode,result_sha256,run_id,finished_at) VALUES(?,?,?,?,?,?,?,?,?)",
                        (lease, td, path_, manifest, 'done', 0, m.sha256_path(path_),
                         'sealed-run', m.now_iso()))
            con.close()
            progress = {
                'schema': 'pwg.record_output_batch.v1',
                'recorded': ['lease-record', 'lease-b'],
                'remaining': ['lease-c'],
                'failed': {'lease_id': 'lease-c'},
            }

            def partial_command(args, command, check=True):
                seen.append(command)
                return types.SimpleNamespace(
                    returncode=1,
                    stdout='RECORD_OUTPUT_BATCH_PROGRESS: ' +
                           json.dumps(progress, separators=(',', ':')) + '\n',
                    stderr='synthetic batch failure')

            m.coordinator_command = partial_command
            try:
                m.cmd_record_done(m.argparse.Namespace(
                    db=db, coordinator='coordinator.py', coord_dir=td, cwd=td))
                raise AssertionError('partial record batch reported success')
            except SystemExit as exc:
                assert '2/3' in str(exc), exc
            con = m.connect(db)
            states = list(con.execute(
                'SELECT external_id,coordinator_recorded FROM jobs ORDER BY id'))
            con.close()
            assert [(r['external_id'], r['coordinator_recorded']) for r in states] == [
                ('lease-record', 1), ('lease-b', 1), ('lease-c', 0)], states
            batch_cmd = seen[-1]
            assert batch_cmd[0] == 'record-output-batch' and batch_cmd.count('--record') == 3
            assert m.sha256_path(result_c) in batch_cmd
        finally:
            m.coordinator_command = original_command
    print('  record-done: hash+run forwarded; substitution refused; batch partial prefix exact')

    _test_h2079_945_probe_emits_api_time()
    _test_h2326_1172_probe_raw_envelope_capture()
    print('max_account_orchestrator_selftest: PASS')


def _test_h2079_945_probe_emits_api_time():
    """H2079 / #945: the probe records API time and the wall-minus-API gap beside the wall reading.

    The gate still decides on `elapsed_ms` — nothing here changes what passes. The point is that a
    reading becomes DECOMPOSABLE after the fact: a 78 s wall reading that spent 13 s at the API was
    measuring in-CLI backoff, not the route, and the whole c4 series lacked the field that says so.
    """
    import max_account_orchestrator as m
    import run_observability as obs

    _rtk = m.run_tree_kill
    _pc = m._probe_call
    try:
        # An envelope reporting a large wall/API divergence — the §270 shape.
        wrapper = ('{"type":"result","subtype":"success","is_error":false,'
                   '"structured_output":{"ok":true},"total_cost_usd":0.29,'
                   '"duration_ms":78415,"duration_api_ms":12987}')
        m.run_tree_kill = lambda *a, **k: types.SimpleNamespace(
            returncode=0, stdout=wrapper, stderr='')
        timing = {}
        _lat, cls, _ob = m._probe_call(
            'cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
            call_reservation=MemoryCallLedger(), timing_out=timing)
        assert cls == 'success', cls
        assert timing == {'duration_ms': 78415, 'duration_api_ms': 12987}, timing

        # end to end through live_probe's event emission
        with tempfile.TemporaryDirectory() as td:
            ev = os.path.join(td, 'e.jsonl')

            def _mock(config_dir, claude, payload_bytes, model, *_args, **_kwargs):
                out = _kwargs.get('timing_out')
                if out is not None:
                    out.update({'duration_ms': 40000, 'duration_api_ms': 12987})
                return 40000, 'success', 120
            m._probe_call = _mock
            m.live_probe('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
                         latency_ceiling_ms=65000, events_path=ev, run_id='h2079',
                         account='c4', call_reservation=MemoryCallLedger())
            rows = [json.loads(line) for line in open(ev, encoding='utf-8') if line.strip()]
            measured = [r for r in rows if r.get('purpose') == 'measured']
            assert len(measured) == 1, rows
            row = measured[0]
            assert row['elapsed_ms'] == 40000, row          # the gated number is UNCHANGED
            assert row['duration_api_ms'] == 12987, row
            assert row['api_gap_ms'] == 27013, row          # 40000 - 12987
            assert {'duration_api_ms', 'api_gap_ms'} <= obs.ALLOWED
            # H2095 (#946): the row records the ceiling THAT JUDGED IT, so it can be read
            # standalone. H2118 (#946) then made `policy` sufficient on its own too, by giving
            # each ceiling value its own token instead of re-pointing one name across
            # 30000 -> 33000 -> 65000. The two gates can no longer drift apart: both derive.
            assert row['latency_ceiling_ms'] == 65000, row
            assert 'latency_ceiling_ms' in obs.ALLOWED
            import probe_log
            import coordinator
            # H2118 replaces H2095's divergence pin (which asserted the two ceilings DISAGREE
            # and fired the moment they were reconciled — it had done its job). The invariant
            # now worth pinning is the derivation itself: one table, no second copy.
            assert m.PROBE_LATENCY_CEILING_MS == probe_log.ceiling_for(m.PROBE_POLICY), (
                'max_account_orchestrator stopped deriving its ceiling from probe_log.POLICIES '
                '— re-derive it rather than restating the number')
            assert coordinator.PROBE_LATENCY_CEILING_MS == m.PROBE_LATENCY_CEILING_MS, (
                'coordinator and max_account_orchestrator disagree on the dispatch ceiling; '
                'both must derive from probe_log.POLICIES[probe_log.CURRENT_POLICY]')
            assert coordinator.PROBE_POLICY == m.PROBE_POLICY, (
                'the two gates stamp rows with different policy tokens')
            # ONE POLICY NAME PER CEILING VALUE. A future ceiling change adds a new token; it
            # must never re-point an existing one, or rows judged differently claim one policy
            # again — the exact defect #946 was opened for.
            assert probe_log.POLICIES['production_v1']['latency_ceil_ms'] == 30_000, (
                'production_v1 is frozen at its historical 30 000 — rows stamped with it were '
                'judged at that ceiling, and moving it falsifies them retroactively')
            _ceilings = [spec['latency_ceil_ms'] for spec in probe_log.POLICIES.values()]
            assert len(_ceilings) == len(set(_ceilings)), (
                'two policy names share one ceiling value: %r' % (probe_log.POLICIES,))

            # a probe that yields no envelope must emit NEITHER key (not an explicit null)
            ev2 = os.path.join(td, 'e2.jsonl')
            m._probe_call = lambda *a, **k: (30000, 'success', 120)   # populates no timing_out
            m.live_probe('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
                         latency_ceiling_ms=65000, events_path=ev2, run_id='h2079',
                         account='c4', call_reservation=MemoryCallLedger())
            bare = [json.loads(line) for line in open(ev2, encoding='utf-8') if line.strip()]
            assert all('duration_api_ms' not in r and 'api_gap_ms' not in r for r in bare), bare
    finally:
        m.run_tree_kill = _rtk
        m._probe_call = _pc
    print('  H2079 #945: probe emits duration_api_ms + api_gap_ms; ceiling still gates elapsed_ms')


def _test_h2326_1172_probe_raw_envelope_capture():
    """H2326 / #1172: a NON-SUCCESS probe classification leaves the provider's own text on disk.

    On 06-08-2026 a c4 gate-0 warm-up returned 830 bytes in 18 574 ms classified `rate_limit`, and
    the 830 bytes were thrown away — so nobody could tell an account weekly cap from a per-model
    capacity refusal, or read the reset time that decides whether the next sitting is worth an
    attempt. The classification was CORRECT (H2263); the evidence behind it was unrecoverable, on a
    gate that is no-reroll and rationed to two attempts a UTC day.

    Pinned here: both non-success exits write, `err_pattern` says WHICH alternative fired, the
    file lands beside the event row, the row carries the pointer — and the `success` lane still
    writes nothing at all.
    """
    import max_account_orchestrator as m
    import run_observability as obs

    assert {'err_pattern', 'raw_envelope_path'} <= obs.ALLOWED, (
        'append_event refuses the H2326 diagnostic fields; the probe row cannot carry them')

    _rtk, _pc, _raw_dir = m.run_tree_kill, m._probe_call, m.PROBE_RAW_DIR
    with tempfile.TemporaryDirectory() as td:
        m.PROBE_RAW_DIR = os.path.join(td, 'output')

        def _raw(run_id):
            return os.path.join(m.PROBE_RAW_DIR, 'h963_c4_gate0_probe_raw_%s.txt' % run_id)

        def _envelope(stdout, rc=0, stderr=''):
            m.run_tree_kill = lambda *a, **k: types.SimpleNamespace(
                returncode=rc, stdout=stdout, stderr=stderr)

        def _call(run_id, purpose='probe'):
            detail = {}
            _lat, cls, _ob = m._probe_call(
                'cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
                reservation_purpose=purpose, call_reservation=MemoryCallLedger(),
                run_id=run_id, detail_out=detail)
            return cls, detail

        try:
            # (1) The 06-08 shape itself: an rc-0 error envelope carrying an account usage limit
            # AND its reset time. Pre-fix this returned 'rate_limit' and nothing else survived.
            _envelope('{"type":"result","subtype":"error","is_error":true,"result":'
                      '"Claude usage limit reached. Your limit will reset at 2026-08-07T01:02:53Z."}')
            cls, detail = _call('h2326')
            assert cls == 'rate_limit', cls
            assert detail['err_pattern'] == 'usage limit', detail
            assert detail['raw_envelope_path'] == os.path.basename(_raw('h2326')), detail
            body = open(_raw('h2326'), encoding='utf-8').read()
            assert '2026-08-07T01:02:53Z' in body, body      # the reset time SURVIVES — the point
            assert 'classification=rate_limit' in body and 'matched=usage limit' in body, body

            # (2) The distinction the class alone erased: a per-model 429 is the SAME verdict and a
            # DIFFERENT decision. `err_pattern` now separates them without reading the file.
            _envelope('', rc=1, stderr='429 Too Many Requests (model capacity)')
            cls, detail = _call('h2326-429')
            assert cls == 'rate_limit' and detail['err_pattern'] == '429', (cls, detail)
            assert '429 Too Many Requests' in open(_raw('h2326-429'), encoding='utf-8').read()

            # (3) The killed-child exit writes too — a rate-limited CLI hangs rather than
            # answering 429 (FINDINGS §270), which is exactly when the text is worth most.
            def _timeout(*_a, **_k):
                raise subprocess.TimeoutExpired(
                    'claude', 300, output='rate limit exceeded, retrying',
                    stderr='killed after 300 s')
            m.run_tree_kill = _timeout
            cls, detail = _call('h2326-kill')
            assert cls == 'rate_limit' and detail['err_pattern'] == 'rate limit', (cls, detail)
            assert 'killed after 300 s' in open(_raw('h2326-kill'), encoding='utf-8').read()

            # (4) A classification with no account-level text still parks the envelope — 'process'
            # and 'malformed' are the hardest to diagnose from a bare class.
            _envelope('<html>503 upstream</html>')
            cls, detail = _call('h2326-bad')
            assert cls == 'malformed' and 'err_pattern' not in detail, (cls, detail)
            assert '503 upstream' in open(_raw('h2326-bad'), encoding='utf-8').read()

            # (5) BOUNDED: only the tail is kept, and the header says it was cut.
            _envelope('{"type":"result","subtype":"error","is_error":true,"result":"'
                      + 'A' * (m.PROBE_RAW_TAIL_BYTES + 5000) + 'TAILMARKER 429"}')
            _call('h2326-big')
            big = open(_raw('h2326-big'), encoding='utf-8').read()
            assert 'TAILMARKER' in big and 'TRUNCATED' in big, big[:200]
            assert len(big.encode('utf-8')) < m.PROBE_RAW_TAIL_BYTES + 600, len(big)

            # (6) THE HEALTHY LANE IS UNTOUCHED: a success writes no file and adds no row fields.
            _envelope('{"type":"result","subtype":"success","is_error":false,'
                      '"structured_output":{"ok":true}}')
            cls, detail = _call('h2326-ok')
            assert cls == 'success' and detail == {}, (cls, detail)
            assert not os.path.exists(_raw('h2326-ok')), 'success wrote a raw-envelope file'

            # (7) Two calls of one run APPEND — live_probe makes two per account, and the last
            # failure must not erase the first.
            _envelope('', rc=1, stderr='429 first')
            _call('h2326-pair', purpose='probe:warmup')
            _envelope('', rc=1, stderr='429 second')
            _call('h2326-pair', purpose='probe:measured')
            pair = open(_raw('h2326-pair'), encoding='utf-8').read()
            assert '429 first' in pair and '429 second' in pair, pair
            assert 'purpose=probe:warmup' in pair and 'purpose=probe:measured' in pair, pair

            # (8) End to end through live_probe's emission: the warm-up STOP row carries both
            # fields, so the event log alone points at the evidence.
            ev = os.path.join(td, 'e.jsonl')
            _envelope('{"type":"result","subtype":"error","is_error":true,'
                      '"result":"Claude usage limit reached"}')
            try:
                m.live_probe('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
                             latency_ceiling_ms=65000, events_path=ev, run_id='h2326-live',
                             account='c4', call_reservation=MemoryCallLedger())
                raise AssertionError('a rate-limited warm-up did not STOP')
            except SystemExit as exc:
                assert 'rate_limit' in str(exc), exc
            rows = [json.loads(line) for line in open(ev, encoding='utf-8') if line.strip()]
            warm = [r for r in rows if r.get('purpose') == 'warmup']
            assert len(warm) == 1, rows
            assert warm[0]['classification'] == 'rate_limit', warm
            assert warm[0]['err_pattern'] == 'usage limit', warm
            assert warm[0]['raw_envelope_path'] == os.path.basename(_raw('h2326-live')), warm
            assert 'Claude usage limit reached' in open(_raw('h2326-live'), encoding='utf-8').read()

            # a healthy live_probe leaves neither key on the row (append_event drops None)
            ev2 = os.path.join(td, 'e2.jsonl')
            _envelope('{"type":"result","subtype":"success","is_error":false,'
                      '"structured_output":{"ok":true}}')
            m.live_probe('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL,
                         latency_ceiling_ms=65000, events_path=ev2, run_id='h2326-live-ok',
                         account='c4', call_reservation=MemoryCallLedger())
            ok_rows = [json.loads(line) for line in open(ev2, encoding='utf-8') if line.strip()]
            assert ok_rows and all(
                'err_pattern' not in r and 'raw_envelope_path' not in r for r in ok_rows), ok_rows
            assert not os.path.exists(_raw('h2326-live-ok')), 'healthy live_probe wrote a raw file'
        finally:
            m.run_tree_kill, m._probe_call, m.PROBE_RAW_DIR = _rtk, _pc, _raw_dir
    print('  H2326 #1172: non-success probe parks the raw envelope + matched pattern; '
          'success lane writes nothing')


if __name__ == '__main__':
    main()
