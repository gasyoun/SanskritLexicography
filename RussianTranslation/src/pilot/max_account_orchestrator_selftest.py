#!/usr/bin/env python
import json
import os
import sqlite3
import sys
import tempfile
import types

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import max_account_orchestrator as m


def main():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'q.sqlite')
        m.main(['--db', db, 'init', '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'), '--skip-profile-check'])
        for n in range(2):
            out = os.path.join(td, 'out%d.json' % n)
            argv = [sys.executable, '-c', 'import os; print(os.environ["CLAUDE_CONFIG_DIR"])']
            m.main(['--db', db, 'enqueue', '--external-id', 'j%d' % n,
                    '--argv-json', json.dumps(argv), '--cwd', td, '--output', out])
        m.main(['--db', db, 'run-once', '--timeout', '10'])
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

        timeout_out = os.path.join(td, 'timeout.json')
        m.main(['--db', db, 'enqueue', '--external-id', 'timeout', '--argv-json',
                json.dumps([sys.executable, '-c', 'import time;time.sleep(2)']),
                '--cwd', td, '--output', timeout_out, '--max-attempts', '1'])
        m.main(['--db', db, 'run-once', '--timeout', '1'])
        con = sqlite3.connect(db)
        assert con.execute("select state,failure_class from jobs where external_id='timeout'").fetchone() == ('failed', 'timeout')
        con.close()

        fail_out = os.path.join(td, 'fail.json')
        m.main(['--db', db, 'enqueue', '--external-id', 'retry', '--argv-json',
                json.dumps([sys.executable, '-c', 'raise SystemExit(7)']),
                '--cwd', td, '--output', fail_out, '--max-attempts', '2'])
        m.main(['--db', db, 'run-once', '--timeout', '10'])
        m.main(['--db', db, 'run-once', '--timeout', '10'])
        con = sqlite3.connect(db)
        state, attempts = con.execute("select state,attempts from jobs where external_id='retry'").fetchone()
        assert (state, attempts) == ('failed', 2)
        con.close()

        crash_out = os.path.join(td, 'crash-after-output.json')
        code = ('import pathlib,sys;pathlib.Path(sys.argv[1]).write_text("{}",encoding="utf-8");'
                'raise SystemExit(7)')
        m.main(['--db', db, 'enqueue', '--external-id', 'crash-after-output', '--argv-json',
                json.dumps([sys.executable, '-c', code, crash_out]), '--cwd', td,
                '--output', crash_out, '--max-attempts', '1'])
        m.main(['--db', db, 'run-once', '--timeout', '10'])
        assert os.path.exists(crash_out)
        con = sqlite3.connect(db)
        assert con.execute("select state from jobs where external_id='crash-after-output'").fetchone()[0] == 'failed'
        con.close()

        rate_out = os.path.join(td, 'rate.json')
        m.main(['--db', db, 'enqueue', '--external-id', 'limited', '--argv-json',
                json.dumps([sys.executable, '-c',
                            'import sys;sys.stderr.write("429 rate limit reset_at=1999999999");sys.exit(21)']),
                '--cwd', td, '--output', rate_out])
        m.main(['--db', db, 'run-once', '--timeout', '10'])
        con = sqlite3.connect(db)
        state, failure = con.execute("select state,failure_class from jobs where external_id='limited'").fetchone()
        assert (state, failure) == ('pending', 'rate_limit')
        assert con.execute("select count(*) from accounts where parked_until=1999999999").fetchone()[0] == 1
        con.execute("delete from jobs where external_id='limited'")
        con.execute("update accounts set parked_until=0")
        con.commit(); con.close()

        coord = os.path.join(td, 'coord'); artifacts = os.path.join(coord, 'artifacts', 'lease1')
        os.makedirs(artifacts)
        manifest = os.path.join(artifacts, 'manifest.json')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                       'meta': {'lang': 'ru', 'selected_keys': ['unique']}}, f)
        with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
            json.dump({'leases': [{'id': 'lease1', 'state': 'prepared',
                                   'artifact_dir': artifacts,
                                   'execution_manifest': manifest}]}, f)
        m.main(['--db', db, 'import-coordinator', '--coord-dir', coord, '--cwd', td,
                '--lease-id', 'lease1'])
        con = sqlite3.connect(db)
        row = con.execute("select manifest_sha256,state from jobs where external_id='lease1'").fetchone()
        assert row == (m.sha256_path(manifest), 'pending')
        con.close()

    # D-C (H818 Windows acceptance): a manifest_sha256 containing "429" must NOT be read
    # as a rate-limit; only the worker's own classification or a real provider 429 in
    # stderr must. This prevents the false 5 h account park observed on Windows.
    assert m.is_rate_limited({'classification': 'configuration',
                              'manifest_sha256': '80179429d4f8e6'}, '') is False
    assert m.is_rate_limited({'classification': 'rate_limit'}, '') is True
    assert m.is_rate_limited({}, 'HTTP 429 Too Many Requests') is True
    assert m.is_rate_limited({}, '') is False
    print('  D-C is_rate_limited: hash-429 ignored; worker-class / real-429 detected')

    # D-F (H818 acceptance): the repository probe gate. payload<5KB and a non-exact model raise
    # before any subprocess call; a latency over the 30 s ceiling is a NO-GO (the observed
    # 50,991 ms / 36,684 ms probes must stop the run). A healthy <=30 s rc-0 reading returns.
    try:
        m.live_probe('cfg', payload_bytes=100); assert False, 'payload floor not enforced'
    except SystemExit as e:
        assert 'floor' in str(e)
    try:
        m.live_probe('cfg', model='claude-haiku-4-5'); assert False, 'exact-model gate missing'
    except SystemExit as e:
        assert 'exact generation model' in str(e)
    _run, _mono = m.subprocess.run, m.time.monotonic
    try:
        m.subprocess.run = lambda *a, **k: types.SimpleNamespace(returncode=0, stdout='{"ok":true}', stderr='')
        over = iter([1000.0, 1031.0])            # 31,000 ms elapsed -> over the 30 s ceiling
        m.time.monotonic = lambda: next(over)
        try:
            m.live_probe('cfg'); assert False, 'latency ceiling not enforced'
        except SystemExit as e:
            assert 'health ceiling' in str(e)
        good = iter([1000.0, 1010.0])            # 10,000 ms -> healthy
        m.time.monotonic = lambda: next(good)
        assert m.live_probe('cfg') == 10000
    finally:
        m.subprocess.run, m.time.monotonic = _run, _mono
    print('  D-F probe gate: <5KB/non-exact-model raise; >30s NO-GO; healthy <=30s passes')

    # D-G (H818 acceptance): one active job per account, atomic in the BEGIN IMMEDIATE claim.
    # Two claimers racing the same validated account -> only one obtains a job.
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'g.sqlite')
        m.main(['--db', db, 'init', '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'), '--skip-profile-check'])
        for n in range(2):
            m.main(['--db', db, 'enqueue', '--external-id', 'g%d' % n,
                    '--argv-json', json.dumps(['x']), '--cwd', td,
                    '--output', os.path.join(td, 'g%d.json' % n)])
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

    print('max_account_orchestrator_selftest: PASS')


if __name__ == '__main__':
    main()
