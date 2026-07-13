#!/usr/bin/env python
import json
import os
import sqlite3
import sys
import tempfile
import threading
import types

import run_observability as ro

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
                m.main(['--db', db, 'enqueue', '--external-id', 'r%d' % n, '--argv-json', json.dumps(['x']),
                        '--cwd', td, '--output', os.path.join(td, 'r%d.json' % n)])
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

    print('max_account_orchestrator_selftest: PASS')


if __name__ == '__main__':
    main()
