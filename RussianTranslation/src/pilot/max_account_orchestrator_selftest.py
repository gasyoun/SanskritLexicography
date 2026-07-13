#!/usr/bin/env python
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

    # D-F/D-K: the two-phase probe protocol. payload<5KB / non-exact model raise before any call.
    # Then EXACTLY one warm-up call (latency excluded) + one measured call (gated): 30000 passes,
    # 30001 is an honest NO-GO, and a warm-up failure STOPs before the measured call ever starts.
    try:
        m.live_probe('cfg', payload_bytes=100); assert False, 'payload floor not enforced'
    except SystemExit as e:
        assert 'floor' in str(e)
    try:
        m.live_probe('cfg', model='claude-haiku-4-5'); assert False, 'exact-model gate missing'
    except SystemExit as e:
        assert 'exact generation model' in str(e)
    _pc = m._probe_call
    try:
        seen = []

        def fake(seq):
            it = iter(seq)

            def _mock(config_dir, claude, payload_bytes, model):
                v = next(it)
                seen.append(v)
                return v
            return _mock

        # warm-up 99999 ms (EXCLUDED) + measured exactly 30000 ms -> PASS (ceiling inclusive)
        seen.clear(); m._probe_call = fake([(99999, 'success', 120), (30000, 'success', 120)])
        with tempfile.TemporaryDirectory() as td:
            ev = os.path.join(td, 'e.jsonl')
            assert m.live_probe('cfg', events_path=ev, run_id='r', account='a') == 30000
            rows = ro.read_events(ev)
            assert len([r for r in rows if r.get('purpose') == 'warmup']) == 1
            assert len([r for r in rows if r.get('purpose') == 'measured']) == 1
            assert len(seen) == 2                       # exactly one warm-up + one measured
            cen = ro.build_census(rows)
            assert cen['latency_ms']['max'] == 30000    # the 99999 warm-up is NOT in the latency census
            assert len(cen['probe']['warmup']) == 1 and len(cen['probe']['measured']) == 1
        # measured 30001 -> honest NO-GO (no retry)
        seen.clear(); m._probe_call = fake([(9000, 'success', 120), (30001, 'success', 120)])
        try:
            m.live_probe('cfg'); assert False, '30001 ms measured must NO-GO'
        except SystemExit as e:
            assert 'health ceiling' in str(e)
        assert len(seen) == 2
        # warm-up auth failure -> immediate STOP, measured NEVER starts
        seen.clear(); m._probe_call = fake([(9000, 'auth', 0)])
        try:
            m.live_probe('cfg'); assert False, 'warm-up auth must STOP'
        except SystemExit as e:
            assert 'warm-up' in str(e)
        assert len(seen) == 1                           # measured never started
        # measured malformed (output-size/validity) -> honest NO-GO
        seen.clear(); m._probe_call = fake([(9000, 'success', 120), (9000, 'malformed', 3)])
        try:
            m.live_probe('cfg'); assert False, 'malformed measured must NO-GO'
        except SystemExit:
            pass
        assert len(seen) == 2
    finally:
        m._probe_call = _pc
    print('  D-F/D-K probe protocol: 1 warm-up (excluded) + 1 measured; 30000 pass / 30001 NO-GO; warm-up fail STOPs before measured')

    # D-K output_bytes is measured from ENCODED UTF-8 bytes, not character count.
    assert len('да') == 2 and len('да'.encode('utf-8')) == 4
    _rtk = m.run_tree_kill
    try:
        body = '{"ok":true,"n":"да"}'
        m.run_tree_kill = lambda *a, **k: types.SimpleNamespace(returncode=0, stdout=body, stderr='')
        lat, cls, obytes = m._probe_call('cfg', 'claude', 6491, m.EXACT_GEN_MODEL)
        assert cls == 'success' and obytes == len(body.encode('utf-8')) and obytes > len(body)
    finally:
        m.run_tree_kill = _rtk
    print('  D-K output_bytes: encoded UTF-8 bytes, not character count')

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
    import time as _time
    with tempfile.TemporaryDirectory() as td:
        mk = os.path.join(td, 'm')
        grand = ('import time,sys,os;open(sys.argv[1]+".pid3","w").write(str(os.getpid()));'
                 'time.sleep(6);open(sys.argv[1]+".done3","w").write("1")')
        child = ('import subprocess,sys,os,time;open(sys.argv[1]+".pid2","w").write(str(os.getpid()));'
                 'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);time.sleep(30)') % grand
        parent = ('import subprocess,sys,os,time;open(sys.argv[1]+".pid1","w").write(str(os.getpid()));'
                  'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);time.sleep(30)') % child

        def _alive(pid):
            if os.name == 'nt':
                out = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'],
                                     capture_output=True, text=True).stdout or ''
                return str(pid) in out.split()
            try:
                os.kill(pid, 0); return True
            except OSError:
                return False

        try:
            m.run_tree_kill([sys.executable, '-c', parent, mk], timeout=3, capture_output=True)
            assert False, 'expected the hanging probe tree to TimeoutExpired'
        except subprocess.TimeoutExpired:
            pass
        for _ in range(60):
            if all(os.path.exists('%s.pid%d' % (mk, i)) for i in (1, 2, 3)):
                break
            _time.sleep(0.1)
        _time.sleep(5)
        assert all(os.path.exists('%s.pid%d' % (mk, i)) for i in (1, 2, 3)), 'probe tree never reached depth 3'
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
