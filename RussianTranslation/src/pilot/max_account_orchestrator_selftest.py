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
from execution_contract import config_dir_fingerprint


def main():
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

    with tempfile.TemporaryDirectory() as td:
        scoped_db = os.path.join(td, 'scope.sqlite')
        m.main(['--db', scoped_db, 'init', '--account', 'acc=' + os.path.join(td, 'acc'),
                '--skip-profile-check'])
        for external_id in ('historic-failed', 'current'):
            m.main(['--db', scoped_db, 'enqueue', '--external-id', external_id,
                    '--argv-json', json.dumps([sys.executable, '-c', 'print(1)']), '--cwd', td,
                    '--output', os.path.join(td, external_id + '.json')])
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
        with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
            json.dump({'leases': [{'id': 'lease1', 'state': 'requeue_prepared',
                                   'artifact_dir': artifacts,
                                   'requeue_attempt': 1, 'requeue_kind': 'transient',
                                   'execution_manifest': rq_manifest,
                                   'current_attempt': {'number': 1, 'kind': 'transient',
                                                       'artifact_dir': rq_dir,
                                                       'execution_manifest': rq_manifest}}]}, f)
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
    # strictly below 30000; 30000 is an honest NO-GO.
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

        # warm-up 99999 ms (EXCLUDED) + measured 29999 ms -> PASS
        seen.clear(); m._probe_call = fake([(99999, 'success', 120), (29999, 'success', 120)])
        with tempfile.TemporaryDirectory() as td:
            ev = os.path.join(td, 'e.jsonl')
            assert m.live_probe('cfg', events_path=ev, run_id='r', account='a') == 29999
            rows = ro.read_events(ev)
            assert len([r for r in rows if r.get('purpose') == 'warmup']) == 1
            assert len([r for r in rows if r.get('purpose') == 'measured']) == 1
            assert len(seen) == 2                       # exactly one warm-up + one measured
            cen = ro.build_census(rows)
            assert cen['latency_ms']['max'] == 29999    # the 99999 warm-up is NOT in the latency census
            assert len(cen['probe']['warmup']) == 1 and len(cen['probe']['measured']) == 1
        # measured 30000 -> honest NO-GO (no retry)
        seen.clear(); m._probe_call = fake([(9000, 'success', 120), (30000, 'success', 120)])
        try:
            m.live_probe('cfg'); assert False, '30000 ms measured must NO-GO'
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
    print('  D-F/D-K probe protocol: 1 warm-up (excluded) + 1 measured; 29999 pass / 30000 NO-GO; warm-up fail STOPs before measured')

    # D-K _probe_call: rc 0 is NOT enough. The Claude CLI result envelope must indicate success
    # (type=result, subtype=success, not is_error) AND carry the structured schema result
    # {"ok": true}. Six fixtures + edge cases. output_bytes is ENCODED UTF-8 bytes, not char count.
    assert len('да') == 2 and len('да'.encode('utf-8')) == 4
    _rtk = m.run_tree_kill

    def _out(stdout='', rc=0, stderr=''):
        m.run_tree_kill = lambda *a, **k: types.SimpleNamespace(returncode=rc, stdout=stdout, stderr=stderr)

    def _cls(stdout='', rc=0, stderr=''):
        _out(stdout, rc, stderr)
        return m._probe_call('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL)[1]

    try:
        # (1) observed successful result-STRING wrapper (result is a JSON string) + Cyrillic body
        w1 = '{"type":"result","subtype":"success","is_error":false,"result":"{\\"ok\\":true}","usage":{"n":"да"}}'
        _out(w1)
        lat, cls, ob = m._probe_call('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL)
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
        _lat, _cls2, _ob = m._probe_call('cfg', sys.executable, 6491, m.EXACT_GEN_MODEL)
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
                                     capture_output=True, text=True,
                                     creationflags=m.windows_hidden_flags()).stdout or ''   # no flicker
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

            def _mock(config_dir, claude, payload_bytes, model):
                if config_dir not in seen:
                    seen.add(config_dir)
                    return warm_ms, 'success', 120          # warm-up (EXCLUDED from latency census)
                return measured_by_cfg[config_dir], 'success', 120   # measured (the one gated reading)
            return _mock

        def with_bad(measured_by_cfg, bad_cfg, warm_ms=99999):
            seen = set()

            def _mock(config_dir, claude, payload_bytes, model):
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
            latencies = m.probe_fleet(accts, events_path=ev, run_id='rf')
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
            m.probe_fleet(accts)
            assert False, 'a NO-GO account must STOP the fleet by default'
        except SystemExit as exc:
            assert 'acc3' in str(exc) and 'fleet probe' in str(exc), exc

        # (e3) --drop-unhealthy opt-in: drop the NO-GO account, proceed on the healthy subset
        m._probe_call = with_bad(measured, bad_cfg='c3')
        survivors = m.probe_fleet(accts, drop_unhealthy=True)
        assert survivors == {'acc1': 1000, 'acc2': 2000, 'acc4': 4000}, survivors

        # (f) N=1 REGRESSION: probe_fleet over a 1-element list == the old single-account live_probe.
        m._probe_call = lambda config_dir, claude, payload_bytes, model: (5555, 'success', 120)
        solo = [{'name': 'max1', 'config_dir': 'c1'}]
        assert m.probe_fleet(solo) == {'max1': 5555}, 'N=1 must be a pure pass-through'
        assert m.live_probe('c1') == 5555                 # the pre-N-profile single-account reading
        assert m.probe_fleet(solo)['max1'] == m.live_probe('c1')   # value report['probe_latency_ms'] carries
    finally:
        m._probe_call = _pc
    print('  GAP5 probe_fleet: N=4 map + warm-ups excluded; NO-GO STOPs by default; --drop-unhealthy subset; N=1 == old live_probe')

    # GAP #5 fair fan-out + all-done at N=4: 4 accounts claim 4 DISTINCT jobs in ONE run-once pass
    # and every job reaches 'done' exactly once (echo jobs; --skip-profile-check; never credentials).
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'fanout.sqlite')
        m.main(['--db', db, 'init',
                '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2'),
                '--account', 'acc3=' + os.path.join(td, 'a3'),
                '--account', 'acc4=' + os.path.join(td, 'a4'), '--skip-profile-check'])
        argv = [sys.executable, '-c', 'import os; print(os.environ["CLAUDE_CONFIG_DIR"])']
        for n in range(4):
            m.main(['--db', db, 'enqueue', '--external-id', 'fan%d' % n,
                    '--argv-json', json.dumps(argv), '--cwd', td,
                    '--output', os.path.join(td, 'fan%d.json' % n)])
        m.main(['--db', db, 'run-once', '--timeout', '30'])
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
        argv = [sys.executable, '-c', 'import os; print(os.environ["CLAUDE_CONFIG_DIR"])']
        for n in range(4):
            m.main(['--db', db, 'enqueue', '--external-id', 'oa%d' % n,
                    '--argv-json', json.dumps(argv), '--cwd', td,
                    '--output', os.path.join(td, 'oa%d.json' % n)])
        # dispatch restricted to the acc1/acc2 "probed" subset (acc3/acc4 == capped-out/unprobed).
        m.cmd_run_once(m.argparse.Namespace(db=db, timeout=30, events=None, run_id=None,
                                            claude_bin='claude', only_accounts={'acc1', 'acc2'}))
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
            m.main(['--db', db, 'enqueue', '--external-id', 'oa%d' % n,
                    '--argv-json', json.dumps(['x']), '--cwd', td,
                    '--output', os.path.join(td, 'oa%d.json' % n)])
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
            m.main(['--db', db, 'enqueue', '--external-id', 'rec%d' % n,
                    '--argv-json', json.dumps(['x']), '--cwd', td,
                    '--output', os.path.join(td, 'rec%d.json' % n)])
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
        for n in range(2):
            m.main(['--db', db, 'enqueue', '--external-id', 'runtime%d' % n,
                    '--argv-json', json.dumps(['x']), '--cwd', td,
                    '--output', os.path.join(td, 'runtime%d.json' % n)])
        con = m.connect(db)
        with con:
            con.execute("UPDATE jobs SET manifest_path='fixture.json', manifest_sha256='fixture'")
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
                        run_id=None, claude_bin='claude'):
            assert reserved.is_set(), 'worker started before atomic begin-run reservation'
            outcome = 'done' if job['external_id'] == 'runtime0' else 'pending'
            m.finish(db_path, job['id'], outcome, 0 if outcome == 'done' else 1)
            return outcome

        m.coordinator_command = fake_command
        m.run_claimed = fake_worker
        try:
            m.cmd_run_once(m.argparse.Namespace(
                db=db, timeout=30, events=None, run_id='runtime-test',
                claude_bin='claude', runtime_mode='staged', probe_receipt=receipt,
                coordinator='coordinator.py', coord_dir=td, cwd=td))
        finally:
            m.coordinator_command = original_command
            m.run_claimed = original_run_claimed
        begin_calls = [call for call in calls if call[0] == 'begin-run']
        release_calls = [call for call in calls if call[0] == 'release-run']
        assert len(begin_calls) == 1 and begin_calls[0].count('--lease-id') == 2
        assert len(release_calls) == 1 and release_calls[0][1] == 'runtime1'
    print('  runtime integration: reserve batch before workers; retryable worker releases slot')

    print('max_account_orchestrator_selftest: PASS')


if __name__ == '__main__':
    main()
