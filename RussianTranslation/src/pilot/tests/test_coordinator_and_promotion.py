"""test_coordinator_and_promotion — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_coordinator_and_promotion.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports
from _support import _sealed_preflight  # noqa: F401  -- `import *` skips _names


def test_selftest_isolation_guard():
    """The isolation guard itself: production data must be unreachable BY CONSTRUCTION.

    Three defects in two days shared one shape -- a test reached production data because
    the thing keeping it away was incidental (a subprocess boundary in the live-store case,
    a missing `--no-residual` flag in #726, a default filename). This pins both halves of
    the fix: every redirectable path is pinned to scratch, and a run that writes a watched
    production file is reported even when every assertion passed.
    """
    import selftest_isolation as iso
    iso.selftest()
    for env, _kind, _base in iso.REDIRECTABLE:
        value = os.environ.get(env)
        if not value:
            fail('isolation guard did not pin %s' % env)
        if iso._inside_repo(value):
            fail('%s still points inside the checkout: %s' % (env, value))
    # the tripwire must actually notice a changed watched file -- a guard that cannot fail
    # is not a guard. (Digest-level, so this never writes to the real path.)
    before = iso.tripwire()
    if iso.verify_tripwire(before) != []:
        fail('tripwire reported a violation on an unchanged tree')
    forged = dict(before, **{iso.WATCHED[0]: 'not-the-real-digest'})
    if iso.verify_tripwire(forged) != [iso.WATCHED[0]]:
        fail('tripwire did not report a changed watched production file')



def test_c4_gate0_probe_run_scope():
    """#729: the c4 health gate must read only the readings ITS OWN run wrote.

    `h963_c4_gate0_probe.py` used to pin a CONSTANT `RUN_ID`, append to that one bucket
    and re-read it, keeping the last row per purpose — so a run could pair its own
    warm-up with a **stale** `measured` from days earlier. The 25-07-2026 gate run cited
    a 23-07 reading of 168 352 ms as a NO-GO reason for a measured call it never made.

    That direction was harmless. The inverse is not: a stale *passing* measured plus a
    passing warm-up empties the fail list and prints `GATE-0 VERDICT: PASS`, which
    `/pwg-live-gate` Step 3 turns into `LIVE_GO` and which authorizes `/pwg-bounded-run`
    to SPEND — a paid window opened off a two-day-old number, from inside the gate whose
    entire job is "a stale GO never authorizes a window".

    The module's own `selftest()` builds exactly that log and proves both halves (the
    scoped read is NO-GO; the contaminated pairing is demonstrably PASS-shaped). Run it
    here so the gate cannot regress silently. Pure — no live call, nothing spent.
    """
    import h963_c4_gate0_probe as probe
    probe.selftest()
    if probe.CAMPAIGN != 'h963-c4-single-profile-gate0-2026-07-16':
        fail('the campaign label is cited verbatim by the H1110/H1447 gate reports — '
             'changing it silently orphans them from their own telemetry rows')
    # The label must never again BE the run id: two invocations must not collide.
    if probe.new_run_id(now=0, pid=1) == probe.new_run_id(now=0, pid=2):
        fail('#729 regression: run ids collide, so one run can read another run\'s readings')



def test_h3659_input_sidecars_parked_beside_manifest():
    """FINDINGS 612: a window's INPUT sidecars are parked with its manifest, fail-closed.

    The evidence root kept everything a paid window PRODUCED and nothing it CONSUMED, so
    once the planning worktree died `audit_window.py` could not re-derive the inputs it
    hashes -- and `no_pwg_w09`'s two audit-clean cards were unpromotable after 8 priced
    calls. Two guarantees are pinned here because both failure modes are silent:

      1. present sidecars are COPIED (content-identical, sha recorded), so the window
         stays auditable after its checkout is gone;
      2. a MISSING sidecar raises at plan time -- before any spend. Discovering it after
         the window ran is the unrecoverable case, so this must never degrade to a warn.
    """
    import no_pwg_scale_plan as nps
    tmp = tempfile.mkdtemp(prefix='h3659_sidecars_')
    try:
        gen_dir = os.path.join(nps.SRC, 'pilot', 'input')
        os.makedirs(gen_dir, exist_ok=True)
        keys = ['zz~~h0_zz_selftest_a', 'zz~~h0_zz_selftest_b']
        written = []
        try:
            for i, key in enumerate(keys):
                raw = os.path.join(gen_dir, key + '.raw.txt')
                por = os.path.join(gen_dir, key + '.portrait.json')
                with open(raw, 'w', encoding='utf-8') as fh:
                    fh.write('raw body %d\n' % i)
                with open(por, 'w', encoding='utf-8') as fh:
                    fh.write('[{"portrait_kind": "selftest", "n": %d}]' % i)
                written += [raw, por]

            parked = nps.park_input_sidecars(keys, tmp)
            for key in keys:
                for suffix in nps.INPUT_SIDECAR_SUFFIXES:
                    src_p = os.path.join(gen_dir, key + suffix)
                    dst_p = os.path.join(tmp, 'input', key + suffix)
                    if not os.path.isfile(dst_p):
                        fail('sidecar %s was not parked beside the manifest' % (key + suffix))
                    with open(src_p, 'rb') as a, open(dst_p, 'rb') as b:
                        if a.read() != b.read():
                            fail('parked %s differs from its source' % (key + suffix))
                if sorted(parked.get(key, {})) != ['portrait', 'raw']:
                    fail('parked record for %s lacks both sha entries: %r'
                         % (key, parked.get(key)))

            # 2. fail-closed on a missing sidecar -- at plan time, before any spend.
            os.remove(os.path.join(gen_dir, keys[0] + '.portrait.json'))
            written.remove(os.path.join(gen_dir, keys[0] + '.portrait.json'))
            try:
                nps.park_input_sidecars(keys, tmp)
            except SystemExit as exc:
                if 'FINDINGS 612' not in str(exc):
                    fail('missing-sidecar refusal does not cite its finding: %s' % exc)
            else:
                fail('a missing input sidecar did not refuse -- the window would run '
                     'and then be unpromotable, which is the unrecoverable case')
        finally:
            for path in written:
                if os.path.isfile(path):
                    os.remove(path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('  H3659/612: input sidecars parked beside the manifest; missing one refuses')



def test_coordinator_state_dashboard_and_cap():
    import coordinator
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            state = coordinator.default_state()
            for i in range(3):
                state['leases'].append({
                    'id': 'lease%d' % i,
                    'lane': 'lane%d' % i,
                    'kind': 'verb',
                    'owner': 'selftest',
                    'target': 'root%d' % i,
                    'state': 'prepared',
                    'artifact_dir': os.path.join(tmp, 'artifacts', 'lease%d' % i),
                })
            coordinator.save_state(state)
            loaded = coordinator.load_state()
            if len(coordinator.reserved_translation_leases(loaded)) != 3:
                fail('coordinator must count exactly three reserved translation leases')
            if coordinator.running_translation_leases(loaded):
                fail('prepared leases must not consume runtime slots')
            dash = json.load(open(os.path.join(tmp, 'dashboard.json'), encoding='utf-8'))
            if dash.get('schema') != coordinator.DASHBOARD_SCHEMA:
                fail('coordinator dashboard schema missing')
            if (dash.get('reserved_translation_leases') != 3
                    or dash.get('running_translation_leases') != 0
                    or dash.get('active_translation_leases') != 0
                    or dash.get('runtime_limit') != 3
                    or dash.get('runtime_mode') != 'standard'):
                fail('coordinator dashboard must distinguish reserved and running state')
            coordinator.begin_run_leases(loaded, ['lease0', 'lease1', 'lease2'])
            if len(coordinator.active_translation_leases(loaded)) != 3:
                fail('deprecated active alias must equal the running count')
            state['leases'][0]['state'] = 'promoted'
            coordinator.save_state(state)
            if len(coordinator.reserved_translation_leases(coordinator.load_state())) != 2:
                fail('promoted leases must not count against reserved work')
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old



def test_coordinator_nominal_reservations():
    """Nominal batches own every canonical key, including migrated legacy leases."""
    import coordinator
    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    old_here = coordinator.HERE
    old_store = coordinator.promote_final_cards.DEFAULT_STORE
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = os.path.join(tmp, 'coord')
        coordinator.HERE = os.path.join(tmp, 'pilot')
        os.makedirs(os.path.join(coordinator.HERE, 'input'))
        store = os.path.join(tmp, 'store.jsonl')
        open(store, 'w', encoding='utf-8').close()
        coordinator.promote_final_cards.DEFAULT_STORE = store
        manifest = os.path.join(tmp, 'manifest.json')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                       'meta': {'selected_keys': ['c_safe'],
                                'nominal_keymap': {'c_safe': 'c'}}}, f)
        try:
            state = coordinator.default_state()
            state['leases'] = [
                {'id': 'details-legacy', 'kind': 'nominal', 'state': 'prepared',
                 'details': {'keys': ['a', 'b']}},
                {'id': 'manifest-legacy', 'kind': 'nominal', 'state': 'prepared',
                 'execution_manifest': manifest},
            ]
            coordinator.save_state(state)
            migrated = coordinator.load_state()
            if migrated['leases'][0].get('reserved_keys') != ['a', 'b']:
                fail('legacy details.keys reservation was not migrated')
            if migrated['leases'][1].get('reserved_keys') != ['c']:
                fail('legacy manifest nominal_keymap reservation was not migrated')
            if coordinator.active_reserved_nominal_keys(migrated) != {'a', 'b', 'c'}:
                fail('active nominal reservations did not include every batch key')

            cards = os.path.join(tmp, 'cards.jsonl')
            with open(cards, 'w', encoding='utf-8') as f:
                for key in ('b', 'd'):
                    f.write(json.dumps({'key1': key}) + '\n')
                    stem = coordinator.safe_name(key)
                    open(os.path.join(coordinator.HERE, 'input', stem + '.raw.txt'),
                         'w', encoding='utf-8').close()
                    open(os.path.join(coordinator.HERE, 'input', stem + '.portrait.json'),
                         'w', encoding='utf-8').close()
            if coordinator.nominal_candidates(migrated, batch_size=5, cards_path=cards) != ['d']:
                fail('nominal candidate selection reused a non-first reserved batch key')

            try:
                coordinator.register_prepared_lease(
                    'overlap', 'test', ['b', 'd'], 'harness.js', manifest,
                    _sealed_preflight(tmp, 'test', ['b', 'd']))
            except SystemExit as exc:
                if 'already active' not in str(exc):
                    raise
            else:
                fail('overlapping prepared nominal lease was accepted')

            # An unresolved active legacy lease blocks every new nominal claim; terminal history
            # is harmless and must not freeze the queue forever.
            state = coordinator.load_state()
            state['leases'].append({'id': 'unknown', 'kind': 'nominal', 'state': 'prepared'})
            coordinator.save_state(state)
            try:
                coordinator.active_reserved_nominal_keys(coordinator.load_state())
            except SystemExit as exc:
                if 'unresolved reservations' not in str(exc):
                    raise
            else:
                fail('unresolved active legacy lease did not fail closed')
            state = coordinator.load_state()
            state['leases'][-1]['state'] = 'blocked'
            coordinator.save_state(state)
            if coordinator.active_reserved_nominal_keys(coordinator.load_state()) != {'a', 'b', 'c'}:
                fail('terminal unresolved legacy lease incorrectly blocked reservations')

            barrier = threading.Barrier(2)
            outcomes = []

            # Built ONCE, outside the threads: two racers writing the same artifact would
            # collide in os.replace on Windows and neither would reach the reservation
            # logic this test is about. The shared path is also the realistic shape --
            # both registrations reference already-sealed preflight evidence.
            race_preflight = _sealed_preflight(tmp, 'test', ['e', 'f'])

            def register_race(lease_id):
                barrier.wait()
                try:
                    coordinator.register_prepared_lease(
                        lease_id, 'test', ['e', 'f'], 'harness.js', manifest,
                        race_preflight)
                    outcomes.append('accepted')
                except SystemExit:
                    outcomes.append('rejected')

            racers = [threading.Thread(target=register_race, args=('race%d' % i,))
                      for i in range(2)]
            for racer in racers:
                racer.start()
            for racer in racers:
                racer.join(5)
            if sorted(outcomes) != ['accepted', 'rejected']:
                fail('simultaneous overlapping nominal reservations were not serialized')
        finally:
            coordinator.HERE = old_here
            coordinator.promote_final_cards.DEFAULT_STORE = old_store
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord



def test_coordinator_runtime_state_machine_and_cas():
    """Runtime caps, probe authorization, lock responsiveness, and stale completions."""
    import coordinator
    from types import SimpleNamespace

    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    original_run = coordinator.run_cmd
    original_audit = coordinator.run_audit
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            state = coordinator.default_state()
            for i in range(5):
                state['leases'].append({
                    'id': 'run%d' % i, 'kind': 'verb', 'target': 'root%d' % i,
                    'state': 'prepared', 'artifact_dir': os.path.join(tmp, 'a%d' % i),
                })
            coordinator.begin_run_leases(state, ['run0', 'run1', 'run2'])
            try:
                coordinator.begin_run_leases(state, ['run3'])
            except SystemExit as exc:
                if 'runtime cap' not in str(exc):
                    raise
            else:
                fail('standard runtime accepted a fourth lease')

            state = coordinator.default_state()
            for i in range(5):
                state['leases'].append({
                    'id': 'stage%d' % i, 'kind': 'verb', 'target': 'root%d' % i,
                    'state': 'prepared', 'artifact_dir': os.path.join(tmp, 's%d' % i),
                })
            receipt = os.path.join(tmp, 'receipt.json')
            with open(receipt, 'w', encoding='utf-8') as f:
                json.dump({
                    'schema': coordinator.PROBE_RECEIPT_SCHEMA,
                    'generated_at': coordinator.utc_now(), 'run_id': 'acceptance-1',
                    'model': coordinator.PROBE_MODEL, 'policy': coordinator.PROBE_POLICY,
                    'go': True, 'lease_ids': ['stage%d' % i for i in range(5)],
                    'healthy_profiles': ['c1', 'c2', 'c3', 'c4'],
                    'probe_latency_ms': {'c1': 10, 'c2': 11, 'c3': 12, 'c4': 13},
                }, f)
            coordinator.begin_run_leases(
                state, ['stage0', 'stage1', 'stage2', 'stage3'], mode='staged',
                run_id='acceptance-1', probe_receipt=receipt)
            try:
                coordinator.begin_run_leases(
                    state, ['stage4'], mode='staged', run_id='acceptance-1',
                    probe_receipt=receipt)
            except SystemExit as exc:
                if 'runtime cap' not in str(exc):
                    raise
            else:
                fail('staged runtime accepted a fifth lease')
            if len(coordinator.running_translation_leases(state)) != 4:
                fail('fresh four-profile receipt did not authorize four runtime slots')
            coordinator.save_state(state)
            coordinator.release_run(SimpleNamespace(
                lease_id='stage0', confirm_dead=True, reason='selftest worker died'))
            released = coordinator.load_state()['leases'][0]
            if released['state'] != 'prepared' or not released.get('run_attempts'):
                fail('release-run did not restore and record the prepared lease')
            stale_receipt = os.path.join(tmp, 'stale-receipt.json')
            stale_payload = json.load(open(receipt, encoding='utf-8'))
            stale_payload['generated_at'] = (
                datetime.datetime.now(datetime.timezone.utc) -
                datetime.timedelta(hours=7)).isoformat(
                    timespec='seconds').replace('+00:00', 'Z')
            with open(stale_receipt, 'w', encoding='utf-8') as f:
                json.dump(stale_payload, f)
            try:
                coordinator.validate_probe_receipt(
                    stale_receipt, ['stage0'], 'acceptance-1')
            except SystemExit as exc:
                if 'stale' not in str(exc):
                    raise
            else:
                fail('stale staged probe evidence did not fail closed')

            # Two independent dispatchers racing disjoint batches may both validate against an
            # empty snapshot, but the state lock must serialize the commit and keep the cap <=3.
            state = coordinator.default_state()
            # begin_run now calls validate_lease_preflight, so a hand-built 'prepared' lease
            # needs the sealed evidence a real preparation would have left: an existing
            # preflight artifact and its hash. Without it BOTH racers SystemExit on
            # "no sealed preflight evidence", and the cap assertion below then reads as a
            # concurrency failure when it is a fixture gap.
            race_pf = _sealed_preflight(tmp, 'race')
            race_pf_sha = coordinator.sha256_file(race_pf)
            for i in range(5):
                state['leases'].append({
                    'id': 'race%d' % i, 'kind': 'verb', 'target': 'root%d' % i,
                    'state': 'prepared', 'artifact_dir': os.path.join(tmp, 'r%d' % i),
                    'preflight_path': race_pf, 'preflight_sha256': race_pf_sha,
                })
            coordinator.save_state(state)
            barrier = threading.Barrier(2)
            race_results = []

            def begin_race(lease_ids):
                barrier.wait()
                try:
                    coordinator.begin_run(SimpleNamespace(
                        lease_id=lease_ids, mode='standard', run_id=None,
                        probe_receipt=None))
                    race_results.append('accepted')
                except SystemExit:
                    race_results.append('rejected')

            racers = [threading.Thread(target=begin_race, args=(['race0', 'race1', 'race2'],)),
                      threading.Thread(target=begin_race, args=(['race3', 'race4'],))]
            for racer in racers:
                racer.start()
            for racer in racers:
                racer.join(5)
            running = coordinator.running_translation_leases(coordinator.load_state())
            if len(running) > 3 or sorted(race_results) != ['accepted', 'rejected']:
                fail('simultaneous begin-run batches exceeded the standard runtime cap')

            # A blocked preparation must not hold the coordinator lock. Recovering it while
            # the fake subprocess is still alive makes its later completion stale; CAS must
            # refuse that completion rather than overwrite the recovered lease.
            state = coordinator.default_state()
            state['leases'] = [{
                'id': 'prep', 'kind': 'verb', 'target': 'gam', 'state': 'claimed',
                'artifact_dir': os.path.join(tmp, 'prep'),
            }]
            coordinator.save_state(state)
            entered = threading.Event()
            release = threading.Event()
            errors = []

            def blocking_run(cmd, cwd=coordinator.REPO, check=True, timeout=None):
                if not 0 < timeout <= coordinator.PREPARE_TIMEOUT_SECONDS:
                    fail('prepare subprocess did not receive the explicit 10-minute timeout')
                script = os.path.basename(cmd[1])
                if script == 'perf_preflight.py':
                    entered.set()
                    release.wait(5)
                    return SimpleNamespace(returncode=0, stdout=PREFLIGHT_STDOUT, stderr='')
                harness = next(value.split('=', 1)[1] for value in cmd if value.startswith('--out='))
                manifest = next(value.split('=', 1)[1] for value in cmd
                                if value.startswith('--manifest-out='))
                os.makedirs(os.path.dirname(harness), exist_ok=True)
                open(harness, 'w', encoding='utf-8').close()
                with open(manifest, 'w', encoding='utf-8') as f:
                    json.dump({'schema': 'pwg.headless_execution_manifest.v1', 'meta': {}}, f)
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            coordinator.run_cmd = blocking_run

            def do_prepare():
                try:
                    coordinator.prepare(SimpleNamespace(
                        lease_id='prep', allow_over_cost=False, profile_slot=None,
                        config_dir=None, executor_lane='serial-whole-card'))
                except BaseException as exc:
                    errors.append(exc)

            worker = threading.Thread(target=do_prepare)
            worker.start()
            if not entered.wait(5):
                fail('blocking preparation fixture did not start')
            with coordinator.DirLock(coordinator.paths()['lock'], wait_seconds=1):
                if coordinator.load_state()['leases'][0]['state'] != 'preparing':
                    fail('preparing operation token was not persisted before subprocess launch')
            coordinator.recover_operation(SimpleNamespace(
                lease_id='prep', confirm_dead=True))
            release.set()
            worker.join(5)
            if worker.is_alive():
                fail('blocking preparation fixture did not finish')
            if not errors or 'stale preparing completion' not in str(errors[0]):
                fail('stale preparation completion did not fail compare-and-swap')
            if coordinator.load_state()['leases'][0]['state'] != 'claimed':
                fail('stale preparation completion overwrote recovered lease state')

            # The same lock/CAS contract applies to the 30-minute audit phase.
            audit_dir = os.path.join(tmp, 'audit')
            os.makedirs(audit_dir)
            audit_manifest = os.path.join(audit_dir, 'manifest.json')
            with open(audit_manifest, 'w', encoding='utf-8') as f:
                json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                           'meta': {'selected_keys': ['k'], 'input_hashes': {}}}, f)
            result_path = os.path.join(audit_dir, 'result.json')
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump({'results': [{'key': 'k', 'card': {'key1': 'k'}}]}, f)
            state = coordinator.default_state()
            state['leases'] = [{
                'id': 'audit', 'kind': 'verb', 'target': 'gam', 'state': 'prepared',
                'artifact_dir': audit_dir, 'execution_manifest': audit_manifest,
            }]
            coordinator.begin_run_leases(state, ['audit'])
            coordinator.save_state(state)
            audit_entered = threading.Event()
            audit_release = threading.Event()
            audit_errors = []

            def blocking_audit(argv):
                # H1811 S1: the audit step's seam moved from run_cmd (subprocess) to
                # run_audit (in-proc, argv form) -- this fixture substitutes THAT seam.
                adir = argv[argv.index('--out-dir') + 1]
                audit_entered.set()
                audit_release.wait(5)
                with open(os.path.join(adir, 'window_status.json'), 'w', encoding='utf-8') as f:
                    json.dump({'state': 'blocked'}, f)
                with open(os.path.join(adir, 'audit_window.report.json'),
                          'w', encoding='utf-8') as f:
                    json.dump({}, f)
                return SimpleNamespace(returncode=2, stdout='', stderr='')

            coordinator.run_audit = blocking_audit

            def do_audit():
                try:
                    coordinator.record_output(SimpleNamespace(
                        lease_id='audit', workflow_result=result_path,
                        allow_stale=False, transcript_dir=None))
                except BaseException as exc:
                    audit_errors.append(exc)

            audit_worker = threading.Thread(target=do_audit)
            audit_worker.start()
            if not audit_entered.wait(5):
                fail('blocking audit fixture did not start')
            with coordinator.DirLock(coordinator.paths()['lock'], wait_seconds=1):
                if coordinator.load_state()['leases'][0]['state'] != 'auditing':
                    fail('auditing operation token was not persisted before subprocess launch')
            coordinator.recover_operation(SimpleNamespace(
                lease_id='audit', confirm_dead=True))
            audit_release.set()
            audit_worker.join(5)
            if audit_worker.is_alive():
                fail('blocking audit fixture did not finish')
            if not audit_errors or 'stale auditing completion' not in str(audit_errors[0]):
                fail('stale audit completion did not fail compare-and-swap')
            if coordinator.load_state()['leases'][0]['state'] != 'running':
                fail('stale audit completion overwrote recovered runtime state')
        finally:
            coordinator.run_cmd = original_run
            coordinator.run_audit = original_audit
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord



def test_h1957_audit_timeout_actually_kills_the_child():
    """H1957: run_audit's timeout must CANCEL the audit, not merely stop waiting for it.

    H1811 S1 ran audit_window in-process on a daemon thread, so a timeout returned
    rc=124 while the audit kept running -- still writing window_status.json / the
    report / requeue files the caller reads next, and still holding the process-global
    sys.argv, cwd and stdout/stderr that run_py_inproc mutates (its own docstring
    forbids exactly this concurrency). The old test monkeypatched run_py_inproc and
    asserted only the rc=124 mapping, so it passed either way; nothing pinned the part
    that matters.

    This drives a REAL child that sleeps and then writes a sentinel. After the timeout
    we wait past the child's write moment: if the sentinel appears, the work outlived
    its own timeout."""
    import os
    import sys
    import tempfile
    import threading
    import time

    import coordinator

    child_sleep = 2.5
    d = tempfile.mkdtemp(prefix='h1957_')
    sentinel = os.path.join(d, 'sentinel.txt')
    child = os.path.join(d, 'slow_audit.py')
    with open(child, 'w', encoding='utf-8') as fh:
        fh.write(
            'import time\n'
            'time.sleep(%r)\n'
            'open(%r, "w", encoding="utf-8").write("the audit outlived its timeout")\n'
            % (child_sleep, sentinel))

    before_cwd = os.getcwd()
    before_argv = list(sys.argv)
    before_stdout, before_stderr = sys.stdout, sys.stderr
    before_threads = threading.active_count()

    t0 = time.monotonic()
    wedged = coordinator.run_audit([child], timeout=0.4)
    if wedged.returncode != 124:
        fail('run_audit did not map a timed-out audit to rc=124 (got %r)' % wedged.returncode)
    if 'timed out' not in wedged.stderr:
        fail('run_audit timeout did not explain itself in stderr: %r' % wedged.stderr)

    # Wait past the moment the child would have written, plus margin.
    remaining = (t0 + child_sleep + 1.0) - time.monotonic()
    if remaining > 0:
        time.sleep(remaining)
    if os.path.exists(sentinel):
        fail('the audit child survived its timeout and wrote %s -- the timeout did not '
             'cancel the work, it only stopped waiting for it' % sentinel)

    # run_py_inproc mutates all four of these; a survivor would leave them wrong.
    if os.getcwd() != before_cwd:
        fail('run_audit left the process cwd at %r, expected %r' % (os.getcwd(), before_cwd))
    if sys.argv != before_argv:
        fail('run_audit mutated sys.argv: %r' % (sys.argv,))
    if sys.stdout is not before_stdout or sys.stderr is not before_stderr:
        fail('run_audit left stdout/stderr redirected')
    if threading.active_count() != before_threads:
        fail('run_audit leaked a background thread (%d -> %d)'
             % (before_threads, threading.active_count()))

    # The pass-through contract, driven through a real child rather than a stub.
    talker = os.path.join(d, 'talker.py')
    with open(talker, 'w', encoding='utf-8') as fh:
        fh.write('import sys\n'
                 'sys.stdout.write("out")\n'
                 'sys.stderr.write("err")\n'
                 'sys.exit(1)\n')
    ok = coordinator.run_audit([talker], timeout=60)
    if (ok.returncode, ok.stdout.strip(), ok.stderr.strip()) != (1, 'out', 'err'):
        fail('run_audit broke the returncode/stdout/stderr contract: %r'
             % ((ok.returncode, ok.stdout, ok.stderr),))



def test_coordinator_fail_closed_audit_states():
    import coordinator
    card = {'key': 'k', 'card': {'key1': 'k'}}
    cases = {
        'clean': ('ready', True),
        'needs_requeue': ('ready_partial', True),
        'transient_only': ('ready_partial', True),
        'blocked': ('blocked', False),
        'stale_artifact': ('stale_artifact', False),
        'partial': ('partial', False),
        'unknown': ('unknown', False),
    }
    for state_name, expected in cases.items():
        got = coordinator.recorded_lease_state(state_name, [], [card])
        if got != expected:
            fail('coordinator audit state %s mapped to %r, expected %r' %
                 (state_name, got, expected))
    if coordinator.recorded_lease_state('clean', ['bad provenance'], [card]) != (
            'blocked', False):
        fail('a nominally clean audit with validation errors must fail closed')
    if coordinator.recorded_lease_state('clean', [], []) != ('blocked', False):
        fail('an empty clean audit must fail closed')
    if coordinator.recorded_lease_state('needs_requeue', [], []) != (
            'needs_requeue', False):
        fail('an all-requeue audit must remain requeueable but non-promotable')



def test_coordinator_promotion_revalidates_artifacts():
    import coordinator
    from types import SimpleNamespace
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            adir = os.path.join(tmp, 'artifacts', 'lease')
            os.makedirs(adir)
            wf = os.path.join(adir, 'wf.json')
            clean = os.path.join(adir, 'clean.json')
            status_path = os.path.join(adir, 'window_status.json')
            report_path = os.path.join(adir, 'audit_window.report.json')
            payload = {'results': [{'key': 'k', 'card': {'key1': 'k'}}]}
            for path, value in ((wf, payload), (clean, payload),
                                (status_path, {'state': 'clean', 'requeue_keys': []}),
                                (report_path, {'workflow': wf, 'requeue': [], 'crashed': [],
                                               'stale_check': {'ok': True}})):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(value, f)
            state = coordinator.default_state()
            state['leases'] = [{
                'id': 'lease', 'kind': 'nominal', 'target': 'n', 'state': 'ready',
                'artifact_dir': adir, 'wf_output': wf, 'clean_output': clean,
                'clean_output_sha256': 'tampered', 'clean_count': 1,
                'audit_state': 'clean', 'audit_returncode': 0,
                'status_path': status_path, 'audit_report': report_path,
            }]
            coordinator.save_state(state)
            try:
                coordinator.promote_ready(SimpleNamespace(
                    gen_model_version='claude-sonnet-5'))
                fail('promotion accepted a clean artifact whose hash was tampered')
            except SystemExit as e:
                if 'clean output hash' not in str(e):
                    raise
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old



def test_atomic_control_writes_preserve_previous_file():
    import window_common
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'control.json')
        window_common.atomic_write_json(path, {'version': 1})
        original_replace = window_common.os.replace
        window_common.os.replace = lambda *_args: (_ for _ in ()).throw(
            OSError('injected replace failure'))
        try:
            try:
                window_common.atomic_write_json(path, {'version': 2})
                fail('atomic writer did not surface an injected replace failure')
            except OSError:
                pass
        finally:
            window_common.os.replace = original_replace
        if json.load(open(path, encoding='utf-8')) != {'version': 1}:
            fail('failed atomic replacement damaged the previous control artifact')
        leftovers = [name for name in os.listdir(tmp) if name != 'control.json']
        if leftovers:
            fail('failed atomic replacement left temporary files: %r' % leftovers)
        window_common.atomic_write_json(path, {'version': 2})
        if json.load(open(path, encoding='utf-8')) != {'version': 2}:
            fail('successful atomic replacement did not publish the new artifact')



def test_coordinator_expired_leases_release_cap():
    """A killed/offline pre-prepare claim must not hold one global translation lane
    forever, while an already-prepared harness remains a durable operator artifact."""
    import coordinator
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            expired_at = (datetime.datetime.now(datetime.timezone.utc) -
                          datetime.timedelta(seconds=1)).isoformat(
                              timespec='seconds').replace('+00:00', 'Z')
            future_at = (datetime.datetime.now(datetime.timezone.utc) +
                         datetime.timedelta(hours=1)).isoformat(
                             timespec='seconds').replace('+00:00', 'Z')
            state = coordinator.default_state()
            state['leases'] = [
                {'id': 'old-claim', 'lane': 'a', 'kind': 'verb', 'owner': 'selftest',
                 'target': 'gam', 'state': 'claimed', 'expires_at': expired_at},
                {'id': 'old-prepared', 'lane': 'b', 'kind': 'verb', 'owner': 'selftest',
                 'target': 'tyaj', 'state': 'prepared', 'expires_at': expired_at},
                {'id': 'live', 'lane': 'b', 'kind': 'verb', 'owner': 'selftest',
                 'target': 'dah', 'state': 'prepared', 'expires_at': future_at},
            ]
            coordinator.save_state(state)
            loaded = coordinator.load_state()
            reserved = coordinator.reserved_translation_leases(loaded)
            if [l.get('id') for l in reserved] != ['old-prepared', 'live']:
                fail('only expired pre-prepare coordinator claims must release reservations')
            if coordinator.running_translation_leases(loaded):
                fail('durable prepared leases must not consume runtime')
            if loaded['leases'][0].get('state') != 'expired':
                fail('expired coordinator claim must be marked terminal')
            if loaded['leases'][1].get('state') != 'prepared':
                fail('prepared coordinator leases must not expire just because the TTL passed')
            if coordinator.active_targets(loaded) != {'tyaj', 'dah'}:
                fail('only the expired claim target must be reclaimable')
            coordinator.save_state(loaded)
            persisted = coordinator.load_state()
            if persisted['leases'][0].get('state') != 'expired':
                fail('expired coordinator claim state must persist to disk')
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old



def test_coordinator_lock_replaces_stale_dead_owner():
    import coordinator
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, '.state.lock')
        os.mkdir(lock_path)
        old_ts = (datetime.datetime.now(datetime.timezone.utc) -
                  datetime.timedelta(hours=2)).isoformat(timespec='seconds').replace('+00:00', 'Z')
        with open(os.path.join(lock_path, 'owner.json'), 'w', encoding='utf-8') as f:
            json.dump({'pid': 999999999, 'created_at': old_ts}, f)
        with coordinator.DirLock(lock_path, ttl_seconds=1):
            if not os.path.exists(os.path.join(lock_path, 'owner.json')):
                fail('coordinator lock did not recreate owner metadata')



def test_coordinator_lock_creates_parent_dir():
    import coordinator
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, 'missing', 'coordinator', '.state.lock')
        with coordinator.DirLock(lock_path, ttl_seconds=1):
            if not os.path.exists(os.path.join(lock_path, 'owner.json')):
                fail('coordinator lock must create its parent directory before locking')



def test_coordinator_defect_requeue_uses_no_tm_and_out():
    import requeue_from_audit as rq

    with tempfile.TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, 'input')
        os.makedirs(inp)
        with open(os.path.join(inp, 'a.raw.txt'), 'w', encoding='utf-8') as f:
            f.write('raw')
        rqfile = os.path.join(tmp, 'requeue.defect.keys.txt')
        with open(rqfile, 'w', encoding='utf-8') as f:
            f.write('a\n')
        out = os.path.join(tmp, 'run_pilot_wf.requeue.js')
        manifest_out = os.path.join(tmp, 'execution_manifest.requeue.json')

        captured = {}

        class FakeProc:
            returncode = 0
            stdout = 'wrote fake harness'
            stderr = ''

        def fake_run(cmd, **_kwargs):
            captured['cmd'] = cmd
            return FakeProc()

        old_inp, old_run = rq.INP, rq.subprocess.run
        old_deny = rq.append_tm_denylist
        old_argv = sys.argv[:]
        rq.INP = inp
        rq.subprocess.run = fake_run
        rq.append_tm_denylist = lambda *_args, **_kwargs: (1, 0)
        # `--no-residual` (H1618) is NOT decoration: without it this test's `--defect` run
        # reaches requeue_from_audit's C-49 residual stamp, which writes to the REAL tracked
        # `no_pwg_residuals.jsonl` — so every selftest run appended a junk
        # `{"key": "a", "source_window": "nominal_selftest"}` row to the registry that decides
        # which keys are BLOCKED from requeue. The test stubs INP / subprocess.run /
        # append_tm_denylist but never that path. Found 25-07-2026 while running this suite for
        # H858; the assertions below (coordinator flag pass-through) are unaffected by the flag.
        sys.argv = ['requeue_from_audit.py', 'nominal_selftest', '--defect', '--no-residual',
                    '--nominal', '--no-grammar', '--requeue-file=%s' % rqfile,
                    '--out=%s' % out, '--manifest-out=%s' % manifest_out]
        try:
            rq.main()
        finally:
            rq.INP = old_inp
            rq.subprocess.run = old_run
            rq.append_tm_denylist = old_deny
            sys.argv = old_argv
        cmd = captured.get('cmd') or []
        if '--no-tm' not in cmd:
            fail('defect requeue must pass --no-tm')
        if '--nominal' not in cmd or '--no-grammar' not in cmd:
            fail('nominal requeue flags must pass through')
        if '--out=%s' % out not in cmd:
            fail('coordinator requeue must use an explicit harness output path')
        if '--manifest-out=%s' % manifest_out not in cmd:
            fail('coordinator requeue must bind the harness to its exact manifest')



def test_coordinator_requeue_attempt_manifests():
    import coordinator
    import window_provenance
    from types import SimpleNamespace
    from window_common import input_paths

    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    original_run = coordinator.run_cmd
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        artifacts = os.path.join(tmp, 'artifacts', 'lease')
        os.makedirs(artifacts)
        input_dir = os.path.join(tmp, 'input')
        os.makedirs(input_dir)
        input_hashes = {}
        for key in ('a~~x', 'b~~x'):
            raw_path, portrait_path = input_paths(key, input_dir=input_dir)
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write('raw ' + key)
            with open(portrait_path, 'w', encoding='utf-8') as f:
                json.dump({'key': key}, f)
            input_hashes[key] = {
                'raw_sha256': coordinator.sha256_file(raw_path),
                'portrait_sha256': coordinator.sha256_file(portrait_path),
            }
        initial_manifest = os.path.join(artifacts, 'execution_manifest.lease.json')
        # Promotion is a sealed contract now: v1/unbound output is historical-only and is
        # refused, so a lane fixture that ends in a promotion needs manifest-v2 meta with the
        # execution block and per-key provenance. The REAL input hashes computed above are
        # kept -- only the sealing is added.
        original = {
            'schema': 'pwg.headless_execution_manifest.v2',
            'meta': dict(sealed_wf_meta(['a~~x', 'b~~x'], root='no_pwg_fixture', nominal=True),
                         input_hashes=input_hashes),
        }
        with open(initial_manifest, 'w', encoding='utf-8') as f:
            json.dump(original, f)
        original_bytes = open(initial_manifest, 'rb').read()
        audit_report = os.path.join(artifacts, 'audit_window.report.json')
        report = {
            'keys': ['a~~x', 'b~~x'], 'requeue': ['a~~x', 'b~~x'],
            'requeue_transient': ['a~~x'], 'requeue_defect': ['b~~x'],
            'requeue_defect_fshas': ['frag-b'],
        }
        with open(audit_report, 'w', encoding='utf-8') as f:
            json.dump(report, f)
        pending = coordinator.pending_from_report(
            report, audit_report, original['meta']['selected_keys'])
        orphan = os.path.join(artifacts, 'requeue', 'rq01-defect')
        os.makedirs(orphan)
        state = coordinator.default_state()
        state['leases'] = [{
            'id': 'lease', 'kind': 'nominal', 'target': 'a',
            'state': 'promoted_partial', 'artifact_dir': artifacts,
            'execution_manifest': initial_manifest,
            'origin_execution_manifest': initial_manifest,
            'origin_execution_manifest_sha256': coordinator.sha256_file(initial_manifest),
            'pending_requeue': pending,
        }]
        coordinator.save_state(state)

        class FakeProc:
            stdout = 'generated requeue harness\n'

        fail_once = [True]

        def fake_run(cmd, **_kwargs):
            # prepare_requeue now runs perf_preflight.py for the attempt and cost-gates its
            # stdout, so the fake has to answer that command FIRST: it carries no --out=, and
            # the unconditional next(...) below raised StopIteration on it.
            if any(str(arg).endswith('perf_preflight.py') for arg in cmd):
                return SimpleNamespace(returncode=0, stdout=PREFLIGHT_STDOUT, stderr='')
            out = next(arg.split('=', 1)[1] for arg in cmd if arg.startswith('--out='))
            manifest = next(arg.split('=', 1)[1] for arg in cmd
                            if arg.startswith('--manifest-out='))
            rqfile = next(arg.split('=', 1)[1] for arg in cmd
                          if arg.startswith('--requeue-file='))
            keys = [line.strip() for line in open(rqfile, encoding='utf-8') if line.strip()]
            if fail_once[0]:
                fail_once[0] = False
                raise SystemExit('synthetic generation failure')
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'w', encoding='utf-8') as f:
                f.write('// generated\n')
            with open(manifest, 'w', encoding='utf-8') as f:
                json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                           'meta': {'root': 'no_pwg_fixture', 'nominal': True,
                                    'selected_keys': keys,
                                    'input_hashes': {key: input_hashes[key] for key in keys}}}, f)
            return FakeProc()

        coordinator.run_cmd = fake_run
        try:
            try:
                coordinator.prepare_requeue(SimpleNamespace(
                    lease_id='lease', transient=True, defect=False))
                fail('synthetic requeue generation failure was not propagated')
            except SystemExit as exc:
                if 'synthetic' not in str(exc):
                    raise
            lease = coordinator.load_state()['leases'][0]
            failed_dir = os.path.join(artifacts, 'requeue', 'rq02-transient')
            if os.path.exists(failed_dir) or lease.get('requeue_attempt'):
                fail('caught generation failure consumed an attempt or left its directory')
            if lease.get('state') != 'blocked' or 'synthetic generation failure' not in (
                    lease.get('operation_error') or ''):
                fail('unexpected requeue generation failure was not recorded as blocked')
            if set(coordinator.pending_key_set(lease['pending_requeue'])) != {'a~~x', 'b~~x'}:
                fail('caught generation failure changed the pending backlog')

            # Continue the artifact-sequencing half of this selftest from an explicit operator
            # reset; production blocked states are never retried silently.
            state = coordinator.load_state()
            state['leases'][0]['state'] = 'promoted_partial'
            state['leases'][0].pop('operation_error', None)
            coordinator.save_state(state)

            coordinator.prepare_requeue(SimpleNamespace(
                lease_id='lease', transient=True, defect=False))
            lease = coordinator.load_state()['leases'][0]
            if lease['requeue_attempt'] != 2 or 'rq02-transient' not in lease['current_artifact_dir']:
                fail('requeue did not advance past the preserved orphan directory')
            if not os.path.isdir(orphan) or not lease.get('orphaned_requeue_attempts'):
                fail('orphaned requeue attempt was deleted or not recorded')
            if json.load(open(lease['execution_manifest'], encoding='utf-8'))[
                    'meta']['selected_keys'] != ['a~~x']:
                fail('requeue attempt manifest was not narrowed to its exact keys')
            if open(initial_manifest, 'rb').read() != original_bytes:
                fail('requeue preparation modified the original execution manifest')
            if len(lease['execution_manifest_history']) != 2:
                fail('initial and first-attempt manifests were not retained in history')
            remaining = lease['current_attempt']['remaining_pending']
            if remaining['transient'] or remaining['defect'] != ['b~~x']:
                fail('unselected defect lane was not carried into the attempt')
            attempt_manifest = json.load(open(lease['execution_manifest'], encoding='utf-8'))
            old_inp = window_provenance.INP
            window_provenance.INP = input_dir
            try:
                if not window_provenance.stale_check(
                        None, attempt_manifest['meta'], ['a~~x'],
                        execution_manifest=attempt_manifest)['ok']:
                    fail('one-key requeue did not validate against its attempt manifest')
                if window_provenance.stale_check(
                        None, attempt_manifest['meta'], ['a~~x'],
                        execution_manifest=original)['ok']:
                    fail('one-key requeue unexpectedly validated against the two-key original')
            finally:
                window_provenance.INP = old_inp

            latest_dir = lease['current_artifact_dir']
            latest_report_path = os.path.join(latest_dir, 'audit_window.report.json')
            latest_report = {
                'keys': ['a~~x'], 'requeue': [],
                'requeue_transient': [], 'requeue_defect': [],
                'requeue_defect_fshas': [],
            }
            with open(latest_report_path, 'w', encoding='utf-8') as f:
                json.dump(latest_report, f)
            latest_pending = coordinator.pending_from_report(
                latest_report, latest_report_path, ['a~~x'])
            carried = coordinator.merge_pending_requeue(
                lease, remaining, latest_pending,
                coordinator.ensure_origin_manifest(lease))
            if coordinator.recorded_lease_state('clean', [], [{'card': {}}], carried) != (
                    'ready_partial', True):
                fail('a clean transient retry with carried defect work must stay ready_partial')
            state = coordinator.load_state()
            state['leases'][0]['state'] = 'promoted_partial'
            state['leases'][0]['pending_requeue'] = carried
            coordinator.save_state(state)
            coordinator.prepare_requeue(SimpleNamespace(
                lease_id='lease', transient=False, defect=True))
            lease = coordinator.load_state()['leases'][0]
            if lease['requeue_attempt'] != 3 or 'rq03-defect' not in lease['current_artifact_dir']:
                fail('carried defect lane did not receive the next attempt')
            if lease['current_attempt']['selected_keys'] != ['b~~x']:
                fail('carried defect key was not selected after transient recovery')
            if coordinator.pending_key_set(lease['current_attempt']['remaining_pending']):
                fail('final defect attempt retained a phantom pending sibling')
            fsha_path = os.path.join(lease['current_artifact_dir'],
                                     'requeue.defect.fshas.txt')
            if open(fsha_path, encoding='utf-8').read().strip() != 'frag-b':
                fail('defect fragment denylist evidence was not materialized per attempt')
            if len(lease['execution_manifest_history']) != 3:
                fail('repeated requeue did not preserve every prior manifest')

            reverse = coordinator.pending_without_kind(pending, 'defect')
            if reverse['transient'] != ['a~~x'] or reverse['defect']:
                fail('defect-first recovery did not preserve the transient sibling')
            unresolved_report_path = os.path.join(tmp, 'unresolved.json')
            unresolved_report = {
                'keys': ['a~~x'], 'requeue': ['a~~x'],
                'requeue_transient': ['a~~x'], 'requeue_defect': [],
            }
            with open(unresolved_report_path, 'w', encoding='utf-8') as f:
                json.dump(unresolved_report, f)
            unresolved = coordinator.pending_from_report(
                unresolved_report, unresolved_report_path, ['a~~x'])
            mixed_unresolved = coordinator.merge_pending_requeue(
                lease, remaining, unresolved, coordinator.ensure_origin_manifest(lease))
            if coordinator.recorded_lease_state(
                    'transient_only', [], [], mixed_unresolved) != ('needs_requeue', False):
                fail('an unresolved transient retry hid its carried defect sibling')

            foreign_report_path = os.path.join(tmp, 'foreign.json')
            foreign_report = {
                'keys': ['foreign'], 'requeue': ['foreign'],
                'requeue_transient': ['foreign'], 'requeue_defect': [],
            }
            with open(foreign_report_path, 'w', encoding='utf-8') as f:
                json.dump(foreign_report, f)
            foreign = coordinator.pending_from_report(
                foreign_report, foreign_report_path, ['foreign'])
            try:
                coordinator.validate_pending_requeue(
                    lease, foreign, coordinator.ensure_origin_manifest(lease))
                fail('foreign pending key escaped the origin manifest')
            except SystemExit as exc:
                if 'escapes origin' not in str(exc):
                    raise

            tampered_report_path = os.path.join(tmp, 'tampered.json')
            with open(tampered_report_path, 'w', encoding='utf-8') as f:
                json.dump(unresolved_report, f)
            tampered = coordinator.pending_from_report(
                unresolved_report, tampered_report_path, ['a~~x'])
            with open(tampered_report_path, 'w', encoding='utf-8') as f:
                json.dump(dict(unresolved_report, marker='changed'), f)
            try:
                coordinator.validate_pending_requeue(
                    lease, tampered, coordinator.ensure_origin_manifest(lease))
                fail('changed pending source report was accepted')
            except SystemExit as exc:
                if 'hash changed' not in str(exc):
                    raise

            invalid_reports = [
                ({'keys': ['a~~x'], 'requeue': ['a~~x', 'a~~x'],
                  'requeue_transient': ['a~~x', 'a~~x'], 'requeue_defect': []},
                 'duplicate'),
                ({'keys': ['a~~x'], 'requeue': ['a~~x'],
                  'requeue_transient': ['a~~x'], 'requeue_defect': ['a~~x']},
                 'overlap'),
                ({'keys': ['a~~x', 'b~~x'], 'requeue': ['a~~x', 'b~~x'],
                  'requeue_transient': ['a~~x'], 'requeue_defect': []},
                 'do not equal'),
            ]
            for invalid, expected in invalid_reports:
                try:
                    coordinator.report_requeue_parts(invalid, invalid['keys'])
                    fail('invalid split requeue report was accepted')
                except SystemExit as exc:
                    if expected not in str(exc):
                        raise

            history_only = {'execution_manifest_history': [
                {'attempt': 7, 'artifact_dir': os.path.join(tmp, 'gone-rq07')}]}
            if coordinator.next_requeue_attempt(history_only, os.path.join(tmp, 'empty'))[0] != 8:
                fail('attempt allocation ignored the maximum recorded historical attempt')

            state = coordinator.load_state()
            state['leases'][0]['state'] = 'ready_partial'
            coordinator.save_state(state)
            try:
                coordinator.prepare_requeue(SimpleNamespace(
                    lease_id='lease', transient=True, defect=False))
                fail('unpromoted ready_partial lease was allowed to prepare a requeue')
            except SystemExit as exc:
                if 'promote' not in str(exc):
                    fail('ready_partial refusal did not explain the promotion prerequisite')
        finally:
            coordinator.run_cmd = original_run
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord



def test_coordinator_mixed_lane_public_state_sequence():
    import coordinator
    from types import SimpleNamespace

    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    old_store_env = os.environ.get('PWG_RU_STORE')
    old_tm_dir_env = os.environ.get('PWG_RU_TM_DIR')
    original_run = coordinator.run_cmd
    original_audit = coordinator.run_audit
    original_store = coordinator.promote_final_cards.DEFAULT_STORE
    original_count = coordinator.nonempty_line_count
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        store = os.path.join(tmp, 'store.jsonl')
        open(store, 'w', encoding='utf-8').close()
        coordinator.promote_final_cards.DEFAULT_STORE = store
        # H5948: the promotion's derived-TM rebuild calls translation_memory.build() with
        # out=None, and since 9b1936cd that refuses any non-canonical source store. This
        # fixture's scratch store IS this test's whole universe, so make it canonical via
        # the sanctioned env seams (store file + sidecar dir) instead of letting the build
        # resolve the real main-worktree sidecar.
        tm_dir = os.path.join(tmp, 'tm')
        os.makedirs(tm_dir)
        os.environ['PWG_RU_STORE'] = store
        os.environ['PWG_RU_TM_DIR'] = tm_dir
        initial_dir = os.path.join(tmp, 'artifacts', 'lease')
        os.makedirs(initial_dir)
        origin_manifest = os.path.join(initial_dir, 'execution_manifest.lease.json')
        origin = {
            'schema': 'pwg.headless_execution_manifest.v1',
            'meta': {'root': 'nominal_mixed', 'nominal': True,
                     'selected_keys': ['a~~x', 'b~~x'], 'input_hashes': {}},
        }
        with open(origin_manifest, 'w', encoding='utf-8') as f:
            json.dump(origin, f)
        state = coordinator.default_state()
        state['leases'] = [{
            'id': 'lease', 'kind': 'nominal', 'target': 'mixed', 'state': 'prepared',
            'artifact_dir': initial_dir, 'current_artifact_dir': initial_dir,
            'execution_manifest': origin_manifest,
            'origin_execution_manifest': origin_manifest,
            'origin_execution_manifest_sha256': coordinator.sha256_file(origin_manifest),
        }]
        coordinator.save_state(state)

        audit_specs = [{
            'state': 'needs_requeue', 'returncode': 1,
            'requeue': ['a~~x', 'b~~x'],
            'transient': ['a~~x'], 'defect': ['b~~x'],
        }, {
            'state': 'clean', 'returncode': 0, 'requeue': [],
            'transient': [], 'defect': [],
        }, {
            'state': 'clean', 'returncode': 0, 'requeue': [],
            'transient': [], 'defect': [],
        }]

        def fake_audit(argv):
            # H1811 S1: the audit step's seam is run_audit (in-proc, argv form);
            # this fixture substitutes THAT seam with the same scripted specs.
            spec = audit_specs.pop(0)
            wf = argv[1]
            adir = argv[argv.index('--out-dir') + 1]
            status = {'state': spec['state'], 'requeue_keys': spec['requeue']}
            report = {
                'workflow': wf, 'keys': json.load(open(
                    argv[argv.index('--execution-manifest') + 1], encoding='utf-8'))[
                        'meta']['selected_keys'],
                'requeue': spec['requeue'],
                'requeue_transient': spec['transient'],
                'requeue_defect': spec['defect'],
                'requeue_defect_fshas': ['frag-b'] if spec['defect'] else [],
                'crashed': [], 'stale_check': {'ok': True},
            }
            with open(os.path.join(adir, 'window_status.json'), 'w', encoding='utf-8') as f:
                json.dump(status, f)
            with open(os.path.join(adir, 'audit_window.report.json'),
                      'w', encoding='utf-8') as f:
                json.dump(report, f)
            return SimpleNamespace(returncode=spec['returncode'], stdout='', stderr='')

        def fake_run(cmd, cwd=coordinator.REPO, check=True, timeout=None):
            script = os.path.basename(cmd[1]) if len(cmd) > 1 else ''
            if script == 'promote_final_cards.py':
                # H1339 Phase 3: promote-ready now invokes ONE batched transaction
                # (--batch-manifest + --report) instead of one subprocess per lease; the
                # fake must honour that contract (write the per-lease report + rows).
                batch_arg = cmd[cmd.index('--batch-manifest') + 1]
                report_arg = cmd[cmd.index('--report') + 1]
                batch_spec = json.load(open(batch_arg, encoding='utf-8'))
                leases_out = {}
                with open(store, encoding='utf-8') as f:
                    before = sum(1 for line in f if line.strip())
                with open(store, 'a', encoding='utf-8') as f:
                    for item in batch_spec:
                        subs = item.get('expected_subcards') or []
                        for sub in subs:
                            f.write(json.dumps({'promoted': True, 'subcard': sub}) + '\n')
                        leases_out[item['lease_id']] = {'subcards': len(subs),
                                                        'rows': len(subs)}
                with open(report_arg, 'w', encoding='utf-8') as f:
                    json.dump({'schema': 'pwg.batch_promotion.v1',
                               'store_rows_before': before,
                               'store_rows_after': before + sum(
                                   row['rows'] for row in leases_out.values()),
                               'leases': leases_out}, f)
            return SimpleNamespace(returncode=0, stdout='', stderr='')

        def result_file(name, keys):
            path = os.path.join(tmp, name)
            # The workflow output -- not the manifest -- is what promotion validates, so the
            # sealed meta and a schema-complete card have to live HERE. The real per-key input
            # hashes are carried over; only the sealing is added.
            payload = {
                'meta': dict(sealed_wf_meta(list(keys), root='no_pwg_fixture', nominal=True),
                             nominal_keymap={k: k for k in keys}),
                'results': [{'key': key, 'card': sealed_card(key)} for key in keys],
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(payload, f)
            return path

        def record(path):
            state = coordinator.load_state()
            coordinator.begin_run_leases(state, ['lease'])
            coordinator.save_state(state)
            coordinator.record_output(SimpleNamespace(
                lease_id='lease', workflow_result=path, allow_stale=False,
                transcript_dir=None))

        def set_attempt(number, kind, key, remaining):
            adir = os.path.join(initial_dir, 'requeue', 'rq%02d-%s' % (number, kind))
            os.makedirs(adir)
            manifest = os.path.join(adir, 'execution_manifest.json')
            attempt = dict(origin)
            attempt['meta'] = dict(origin['meta'], selected_keys=[key])
            with open(manifest, 'w', encoding='utf-8') as f:
                json.dump(attempt, f)
            state = coordinator.load_state()
            lease = state['leases'][0]
            lease.update({
                'state': 'requeue_prepared', 'current_artifact_dir': adir,
                'execution_manifest': manifest, 'requeue_attempt': number,
                'current_attempt': {
                    'number': number, 'kind': kind, 'artifact_dir': adir,
                    'execution_manifest': manifest, 'selected_keys': [key],
                    'remaining_pending': remaining,
                },
            })
            coordinator.save_state(state)

        coordinator.run_cmd = fake_run
        coordinator.run_audit = fake_audit
        coordinator.nonempty_line_count = lambda _path: (_ for _ in ()).throw(
            AssertionError('coordinator must use transaction report counts, not rescan store'))
        try:
            record(result_file('initial.json', ['a~~x', 'b~~x']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'needs_requeue':
                fail('mixed initial audit did not enter needs_requeue')
            pending = lease['pending_requeue']
            if pending['transient'] != ['a~~x'] or pending['defect'] != ['b~~x']:
                fail('record-output did not persist both provenance-bound retry lanes')

            carried_b = coordinator.pending_without_kind(pending, 'transient')
            set_attempt(1, 'transient', 'a~~x', carried_b)
            record(result_file('retry-a.json', ['a~~x']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'ready_partial' or lease['pending_requeue']['defect'] != ['b~~x']:
                fail('clean transient retry did not retain the defect backlog')
            coordinator.promote_ready(SimpleNamespace(
                gen_model_version='claude-sonnet-5', lease_id=['lease']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'promoted_partial':
                fail('mixed backlog promotion did not remain promoted_partial')
            if (lease.get('store_before'), lease.get('store_after'), lease.get('store_delta')) != (0, 1, 1):
                fail('promotion did not persist transaction-reported store counts')

            set_attempt(2, 'defect', 'b~~x', coordinator.empty_pending_requeue())
            record(result_file('retry-b.json', ['b~~x']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'ready' or coordinator.pending_key_set(
                    lease['pending_requeue']):
                fail('final clean defect retry did not drain the pending backlog')
            coordinator.promote_ready(SimpleNamespace(
                gen_model_version='claude-sonnet-5', lease_id=['lease']))
            final_lease = coordinator.load_state()['leases'][0]
            if final_lease['state'] != 'promoted':
                fail('drained mixed retry sequence did not finish promoted')
            if (final_lease.get('store_before'), final_lease.get('store_after'),
                    final_lease.get('store_delta')) != (1, 2, 1):
                fail('second promotion did not use transaction-reported store counts')
            if audit_specs:
                fail('mixed-lane integration did not consume every planned audit')
        finally:
            coordinator.run_cmd = original_run
            coordinator.run_audit = original_audit
            coordinator.nonempty_line_count = original_count
            coordinator.promote_final_cards.DEFAULT_STORE = original_store
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord
            if old_store_env is None:
                os.environ.pop('PWG_RU_STORE', None)
            else:
                os.environ['PWG_RU_STORE'] = old_store_env
            if old_tm_dir_env is None:
                os.environ.pop('PWG_RU_TM_DIR', None)
            else:
                os.environ['PWG_RU_TM_DIR'] = old_tm_dir_env



def test_h1553_wall_clock_auto_derive():
    """H1553 / H1403 A2: wall_clock auto-derive + wall_clock_source stamping.

    - explicit CLI wins over mtime derive
    - derive from fixture mtimes when CLI omitted
    - unavailable → null + source tag (no crash)
    """
    import types
    from window_reports import derive_wall_clock_minutes, build_production_metrics

    # CLI wins
    minutes, source = derive_wall_clock_minutes(
        None, {'generated_at': '2026-07-01T00:00:00Z'}, 12.5)
    if source != 'cli' or minutes != 12.5:
        fail('CLI wall-clock must win: got minutes=%r source=%r' % (minutes, source))

    # derive from mtime - generated_at
    tmp = tempfile.mkdtemp()
    wf = os.path.join(tmp, 'wf_output.json')
    with open(wf, 'w', encoding='utf-8') as f:
        f.write('{}')
    # set mtime to a known epoch and generated_at 10 minutes earlier
    end = 1_700_000_600  # fixed epoch seconds
    os.utime(wf, (end, end))
    gen_at = datetime.datetime.fromtimestamp(
        end - 600, tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    minutes, source = derive_wall_clock_minutes(wf, {'generated_at': gen_at}, None)
    if source != 'derived_mtime':
        fail('expected derived_mtime, got %r (minutes=%r)' % (source, minutes))
    if minutes is None or abs(minutes - 10.0) > 0.05:
        fail('derived minutes expected ~10, got %r' % minutes)

    # unavailable: no meta, no crash
    minutes, source = derive_wall_clock_minutes(wf, {}, None)
    if source != 'unavailable' or minutes is not None:
        fail('missing generated_at must be unavailable: minutes=%r source=%r'
             % (minutes, source))

    # unavailable: negative / zero delta
    gen_future = datetime.datetime.fromtimestamp(
        end + 60, tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    minutes, source = derive_wall_clock_minutes(wf, {'generated_at': gen_future}, None)
    if source != 'unavailable' or minutes is not None:
        fail('future generated_at must be unavailable: minutes=%r source=%r'
             % (minutes, source))

    # build_production_metrics stamps wall_clock_source
    args = types.SimpleNamespace(
        wall_clock_minutes=None, max_input_tokens=None, max_output_tokens=None,
        max_cache_read_tokens=None, max_cache_create_tokens=None,
        max_total_tokens=None, weekly_cap_fired=False,
        weekly_cap_cumulative_tokens=None, metrics_note=None)
    metrics = build_production_metrics(args, wf_path=wf, workflow_meta={'generated_at': gen_at})
    if metrics.get('wall_clock_source') != 'derived_mtime':
        fail('metrics missing derived source: %r' % metrics)
    if metrics.get('wall_clock_minutes') is None:
        fail('metrics must carry derived wall_clock_minutes: %r' % metrics)

    args.wall_clock_minutes = 3.0
    metrics = build_production_metrics(args, wf_path=wf, workflow_meta={'generated_at': gen_at})
    if metrics.get('wall_clock_source') != 'cli' or metrics.get('wall_clock_minutes') != 3.0:
        fail('CLI must stamp wall_clock_source=cli: %r' % metrics)

    args.wall_clock_minutes = None
    metrics = build_production_metrics(args, wf_path=wf, workflow_meta={})
    if metrics.get('wall_clock_source') != 'unavailable':
        fail('unavailable must stamp source: %r' % metrics)
    if 'wall_clock_minutes' not in metrics or metrics['wall_clock_minutes'] is not None:
        fail('unavailable must keep null wall_clock_minutes: %r' % metrics)

    # ledger fixture shows wall_clock_source
    from window_reports import write_reports
    base = {'null_cards': [], 'requeue': [], 'crashed': [], 'gates': {},
            'glue': None, 'collect': {}, 'requeue_transient': [], 'requeue_defect': [],
            'judge_sample': {'keys': [], 'sample_count': 0, 'seed': None,
                             'clean_key_count': 0}}
    report = dict(base, workflow=wf, root='h1553wc', keys=['k1'],
                  workflow_meta={'gen_model': 'claude-sonnet-5', 'generated_at': gen_at},
                  production_metrics=metrics)
    # re-build with available path for a non-null stamp
    args.wall_clock_minutes = 7.0
    report['production_metrics'] = build_production_metrics(args)
    out = tempfile.mkdtemp()
    write_reports(report, True, out_dir=out)
    ledger = os.path.join(out, 'window_ledger.jsonl')
    rows = [json.loads(ln) for ln in open(ledger, encoding='utf-8') if ln.strip()]
    pm = (rows[0].get('production_metrics') or {})
    if pm.get('wall_clock_source') != 'cli' or pm.get('wall_clock_minutes') != 7.0:
        fail('ledger production_metrics missing wall_clock_source: %r' % pm)



def test_h1553_stage_boundary_emit():
    """H1553 / H1403 A2: stage_boundary emit path exists and writes one JSONL event."""
    from dashboard_events import emit_stage_boundary
    tmp = tempfile.mkdtemp()
    log = os.path.join(tmp, 'dashboard_events.jsonl')
    rec = emit_stage_boundary(
        'audit_start', window_tag='h1553', root='testRoot',
        data={'cards': 2}, log_path=log)
    if rec.get('type') != 'stage_boundary':
        fail('event type must be stage_boundary, got %r' % rec.get('type'))
    if rec.get('state') != 'audit_start':
        fail('stage must land in state, got %r' % rec.get('state'))
    if not os.path.exists(log):
        fail('stage_boundary must append to the event log')
    lines = [ln for ln in open(log, encoding='utf-8') if ln.strip()]
    if len(lines) != 1:
        fail('expected 1 event line, got %d' % len(lines))
    loaded = json.loads(lines[0])
    if loaded.get('type') != 'stage_boundary' or loaded.get('data', {}).get('window_tag') != 'h1553':
        fail('logged event mismatch: %r' % loaded)
    # second boundary does not raise
    emit_stage_boundary('audit_end', window_tag='h1553', root='testRoot', log_path=log)
    lines = [ln for ln in open(log, encoding='utf-8') if ln.strip()]
    if len(lines) != 2:
        fail('expected 2 stage_boundary lines, got %d' % len(lines))



def test_save_merge_better_attempt_wins():
    """H304: 'latest requeue wins' is WRONG — a requeue can regress a card (gam h0_63_sam_0
    went 2->3->7 missing fragments). --merge must keep the better prior attempt: complete
    beats partial, fewer missing fragments beat more; a complete fresh card still replaces."""
    from window_common import REPO as repo_root
    save = os.path.join(repo_root, 'save_and_audit.py')
    root, tag = 'h304tmp', 'sftest'
    out_path = os.path.join(repo_root, 'wf_output.%s.%s.json' % (tag, root))
    tmp = tempfile.mkdtemp()

    def wf(card):
        return {'result': {'meta': {'root': root},
                           'results': [{'key': 'k1', 'card': card}]}}

    def save_run(name, card, *extra):
        p = os.path.join(tmp, name)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(wf(card), f)
        run([sys.executable, save, root, p, tag, '--no-audit'] + list(extra), expect=0)

    def valid_card(marker, **extra):
        card = {'key1': 'k1', 'iast': 'k1', 'notes': '', 'senses_marker': marker,
                'records': [{'h': 'k1', 'grammar': '', 'senses': [
                    {'tag': '1', 'german': 'Deutsch', 'russian': 'русский'}]}]}
        card.update(extra)
        return card

    try:
        complete = valid_card('first-complete')
        save_run('a.json', complete)
        worse = valid_card('regression', partial=True,
                           missing_fragments=['g1:f0', 'g1:f1'])
        save_run('b.json', worse, '--merge')
        got = json.load(open(out_path, encoding='utf-8'))
        card = got['results'][0]['card']
        if card.get('partial') or card.get('senses_marker') != 'first-complete':
            fail('--merge let a partial attempt regress a complete card')
        fresh = valid_card('second-complete')
        save_run('c.json', fresh, '--merge')
        got = json.load(open(out_path, encoding='utf-8'))
        if got['results'][0]['card'].get('senses_marker') != 'second-complete':
            fail('an equal-quality fresh card must still replace (ties go to new)')
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)



def test_defer_monster_ledger_dedupes():
    """H304 cap-and-defer: the deferred-monsters ledger is append-only and deduped on
    (target, reason, UTC day) so a daily coordinator sweep cannot flood it."""
    from window_common import defer_monster
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, 'deferred_monsters.jsonl')
    row = defer_monster('kAla', 'cost_gate_over_ceiling',
                        estimate={'est_cost_usd': 79.83}, keys=['kAla~~h0_00'], path=p)
    if not row or row.get('schema') != 'pwg.deferred_monsters.v1':
        fail('first defer_monster call must write a schema-stamped row')
    if defer_monster('kAla', 'cost_gate_over_ceiling', path=p) is not None:
        fail('same (target, reason, day) must dedupe to None')
    if defer_monster('kAla', 'defer-calibrate', path=p) is None:
        fail('a different reason for the same target must append')
    lines = [ln for ln in open(p, encoding='utf-8') if ln.strip()]
    if len(lines) != 2:
        fail('ledger must hold exactly 2 rows, got %d' % len(lines))



def test_promote_claim_contention():
    """H336/H-1: the O_EXCL promotion claim file — a second claimant on a live claim
    must retry/error cleanly (not silently proceed to race the read-guard-write window),
    a stale (TTL-expired) claim is reclaimed with NO PID-liveness check (meaningless
    across clones/machines — the whole point of this claim over coordinator.DirLock),
    and --steal-lock bypasses even a fresh claim. Pins promote_lock.py's own selftest
    into the aggregate suite rather than re-deriving the contention scenario here."""
    import promote_lock
    promote_lock.selftest()



def test_restore_covers_every_promoted_field():
    """C-01: restore's field set and promote's read set are ONE constant, not two lists.

    The defect: `restore_card` unmasked 3 fields while `rows_for` promoted 6, so card.iast /
    record.h / sense.tag / sense.differentia reached the canonical store with their {Tn}
    intact -- 670 rows, 223 of them a raw {Tn} in the HEADWORD field. Two independently
    hand-maintained lists could drift; one constant cannot.
    """
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import card_fields
    # Both language lanes: every field the promoter reads must have been unmasked first.
    for field in ('russian', 'english'):
        promoted = set(card_fields.promoted_pairs(field))
        restored = set(card_fields.restored_pairs(field))
        missing = promoted - restored
        if missing:
            fail('fields promoted but never restored (%s): %s' % (field, sorted(missing)))
    # The JS lane cannot import Python, so its list is interpolated from the same constant.
    spec = json.loads(card_fields.js_restore_spec('russian'))
    if set(spec['record']) != set(card_fields.RECORD_MASKED):
        fail('js_restore_spec record set drifted from RECORD_MASKED')
    if 'h' not in spec['record']:
        fail('the JS lane must restore record.h -- it is promoted verbatim')

    # And the restore actually reaches those fields, end to end.
    card = {'iast': '{T1}', 'records': [{'h': '{T1}', 'grammar': '{T1}', 'senses': [
        {'tag': '{T1}', 'german': '{T1}', 'russian': '{T1}', 'differentia': '{T1}'}]}]}
    card_fields.restore_card_fields(card, 'russian', lambda t: t.replace('{T1}', 'X'))
    rec, sense = card['records'][0], card['records'][0]['senses'][0]
    for where, value in (('card.iast', card['iast']), ('record.h', rec['h']),
                         ('record.grammar', rec['grammar']), ('sense.tag', sense['tag']),
                         ('sense.german', sense['german']), ('sense.russian', sense['russian']),
                         ('sense.differentia', sense['differentia'])):
        if value != 'X':
            fail('%s was not restored (still %r)' % (where, value))



def test_h1339_b21_promoted_pairs_cover_store_write_set():
    """H1339 B21 (the H1283 card_fields.py:64 conflict, resolved): every MASKED field
    `rows_for` writes into a store row must be in PROMOTED_PAIRS, or `tn_residue` (the
    promote-time loud-failure backstop) and `backfill_tn_residue` (the repair tool) are
    blind to it. The defect: `record.grammar` is store-written (rows_for) and is BY DESIGN
    a {Tn}-bearing field pre-restore (TOKEN_FIDELITY_FIELDS), yet PROMOTED_COMMON omitted
    it -- so a future restore gap in grammar would promote raw {Tn} silently, exactly the
    C-01 class the module exists to prevent (670 rows last time).
    """
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import card_fields
    import promote_final_cards as pfc
    # Structural half: every masked field the store write-set contains is residue-checked.
    # The store write-set of masked fields, stated here independently of PROMOTED_COMMON
    # (comparing two separately-authored facts, per this module's own design rule):
    # rows_for writes iast (card), h + grammar (record), tag/german/differentia/russian (sense).
    store_written_masked = {('card', 'iast'), ('record', 'h'), ('record', 'grammar'),
                            ('sense', 'tag'), ('sense', 'german'), ('sense', 'differentia'),
                            ('sense', 'russian')}
    missing = store_written_masked - set(card_fields.promoted_pairs('russian'))
    if missing:
        fail('store-written masked fields invisible to tn_residue/backfill: %s'
             % sorted(missing))
    # Behavioral half: a raw {Tn} in record.grammar must be reported as residue.
    card = {'key1': 'x', 'iast': 'x', 'notes': '', 'records': [
        {'h': 'x', 'grammar': 'm. {T9} du.', 'senses': [
            {'tag': '1', 'german': 'a', 'russian': 'b'}]}]}
    rec = card['records'][0]
    residue = pfc.tn_residue(card, rec, rec['senses'][0])
    if not any('grammar' in r for r in residue):
        fail('tn_residue is blind to a raw {Tn} in record.grammar: %r' % (residue,))
    # And the repair tool's store-field set sees the grammar column too.
    import backfill_tn_residue as btr
    if 'grammar' not in btr.STORE_FIELDS:
        fail('backfill_tn_residue.STORE_FIELDS lacks grammar -- repair tool blind')



def test_h1339_b02_stitched_card_schema_complete():
    """H1339 B02: a heal/presplit STITCHED card must be schema-complete at construction.

    The defect: both stitch twins built `{key1, records}` only, omitting CARD_REQUIRED
    `iast`/`notes` (validate_final_card_schema:26) -- so any window containing a healed or
    presplit card was refused WHOLE by the save gate (save_and_audit) or per-key by the
    audit's final-schema gate + promotion contract, losing the window's paid agent calls.
    """
    import headless_worker as hw
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import validate_final_card_schema as vfs
    senses = [{'tag': '1', 'german': 'Feuer', 'russian': 'огонь'}]
    owners = [('agni', 'm.')]
    # Python twin: the construction helper itself must emit a schema-complete card.
    card = hw.stitched_card('agni', 'agní', senses, owners)
    try:
        vfs.validate_card(card)
    except ValueError as exc:
        fail('Python stitched card is schema-incomplete: %s' % exc)
    if card['iast'] != 'agní' or card['notes'] != '':
        fail('stitched card iast/notes wrong: %r/%r' % (card['iast'], card['notes']))
    if hw.stitched_card('k', None, senses, owners)['iast'] != 'k':
        fail('a missing portrait iast must fall back to the key, not None')
    # JS twin (static wiring): the template's stitched construction carries the same two
    # fields, fed from the interpolated IASTS map (the JS cannot import Python).
    src_text = open(os.path.join(HERE, 'gen_opt_harness2.py'), encoding='utf-8').read()
    if 'const IASTS = %(iasts)s' not in src_text:
        fail('JS template does not interpolate the IASTS map')
    if "const stitched = { key1: k, iast: IASTS[k] || k, notes: '', records:" not in src_text:
        fail('JS stitched construction does not carry schema-required iast/notes')



def test_h1339_b03_tm_cards_schema_complete():
    """H1339 B03 (P0): a TM-served whole card must be schema-complete, at BUILD and at SERVE.

    The defect: `reconstruct_cards` emitted `{key1, iast, records:[{h, senses}]}` -- no
    card.notes, no record.grammar, and sense-level optional fields present with None values
    (all of which `validate_final_card_schema` refuses) -- so ONE TM hit poisoned the whole
    window at the save gate. The serve-time guard `tm_card_sane` accepted such cards.
    """
    import tempfile
    import translation_memory as tm
    import gen_opt_harness2 as gh
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import validate_final_card_schema as vfs
    prov = {'input_raw_sha256': 'a' * 64, 'model': 'sonnet', 'model_version': 'claude-sonnet-5'}
    rows = [
        {'key1': 'x', 'subcard': 'x~~h0_00_pwg00', 'iast': 'xā', 'h': 'x', 'grammar': 'm.',
         'sense_tag': '1', 'ru': 'смысл', 'de': 'Sinn {T1}', 'equivalence_type': 'equivalent',
         'source_type': None, 'stratum': None, 'differentia': None,
         'review_status': 'ai_translated', 'provenance': prov},
        {'key1': 'x', 'subcard': 'x~~h0_00_pwg00', 'iast': 'xā', 'h': 'x', 'grammar': 'm.',
         'sense_tag': '2', 'ru': 'иной', 'de': 'ander', 'equivalence_type': None,
         'source_type': None, 'stratum': None, 'differentia': None,
         'review_status': 'ai_translated', 'provenance': prov},
    ]
    d = tempfile.mkdtemp()
    store = os.path.join(d, 'store.jsonl')
    with open(store, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    entries, skipped = tm.reconstruct_cards(store, 'ru')
    if len(entries) != 1:
        fail('expected 1 reconstructed TM card, got %d (skipped: %r)' % (len(entries), skipped))
    card = next(iter(entries.values()))['card']
    try:
        vfs.validate_card(card)
    except ValueError as exc:
        fail('reconstructed TM card is schema-incomplete: %s' % exc)
    # Serve-time guard: a legacy sidecar card (built pre-fix) must be REFUSED, not served.
    legacy = {'key1': 'x', 'iast': 'xā', 'records': [
        {'h': 'x', 'senses': [{'tag': '1', 'german': 'Sinn {T1}', 'russian': 'смысл'},
                              {'tag': '2', 'german': 'ander', 'russian': 'иной'}]}]}
    raw = 'Sinn {T1} ander'
    ok, why = gh.tm_card_sane(legacy, 'ru', 'russian', raw)
    if ok:
        fail('tm_card_sane served a schema-incomplete legacy TM card')
    ok, why = gh.tm_card_sane(card, 'ru', 'russian', raw)
    if not ok:
        fail('tm_card_sane refused a schema-complete reconstructed card: %s' % why)



def test_h1339_b04_b09_worktree_safe_resolution():
    """H1339 B04/B09: TM sidecars and the coverage gate resolve worktree-safely.

    B04: the four TM sidecar resolvers defaulted to THIS checkout's src/pilot -- gitignored
    files absent in every fresh worktree, so the sanctioned worktree workflow silently got
    0 TM hits. B09: ru_coverage read the worktree-local store, so the anti-silent-partial
    gate measured an EMPTY store. Both now route through store_path's canonical resolvers.
    """
    import translation_memory as tm
    import ru_coverage as rc
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    from store_path import canonical_sidecar, canonical_store
    here = os.path.dirname(os.path.abspath(tm.__file__))
    for got, name in ((tm.tm_path('ru'), 'translation_memory.ru.json'),
                      (tm.suggest_tm_path('ru'), 'translation_memory.suggest.ru.jsonl'),
                      (tm.denylist_path(), 'translation_memory.denylist.jsonl'),
                      (tm.frag_tm_path('ru'), 'translation_memory.frag.ru.jsonl')):
        want = canonical_sidecar(os.path.join(here, name))
        if got != want:
            fail('%s resolves to %r, not the canonical sidecar %r' % (name, got, want))
    explicit = os.path.join('explicit', 'x.json')
    if tm.tm_path('ru', explicit) != explicit:
        fail('an explicit tm path must always win over canonical resolution')
    want_store = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
    if os.path.normpath(rc.RU_STORE) != os.path.normpath(want_store):
        fail('ru_coverage.RU_STORE is not the canonical store: %r' % rc.RU_STORE)
    want_repo = os.path.dirname(os.path.dirname(os.path.abspath(rc.RU_STORE)))
    if os.path.normpath(rc.REPO) != os.path.normpath(want_repo):
        fail("ru_coverage.REPO must be the RESOLVED store's checkout (denominators beside "
             'the numerator), got %r' % rc.REPO)



def test_h1339_b10_b19_audit_chain_routing():
    """H1339 B10 + B19: the factory audit chain routes its artifacts correctly.

    B10: save_and_audit's audit invocation must pass --write-requeue, or the requeue
    singletons silently describe the PREVIOUS window. B19: stage2_pregate/audit_translation
    resolved merged output by a verbatim join while the collector writes safe_name(stem) --
    safe_name is not idempotent ('k_ala' -> 'k~005fala'), so every already-safe nominal stem
    was hard-flagged NO-OUTPUT: a translated card requeued at full paid cost.
    """
    import tempfile
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import audit_translation as at
    from safe_filename import safe_name
    # B19 behavioral: the double-encoded file is found; the verbatim file is found; absent -> None.
    d = tempfile.mkdtemp()
    stem = 'k_ala'
    assert safe_name(stem) != stem, 'fixture stem must be non-idempotent under safe_name'
    with open(os.path.join(d, safe_name(stem) + '.merged.md'), 'w', encoding='utf-8') as f:
        f.write('перевод')
    got = at.merged_output_path(stem, out_dir=d)
    if not got or not got.endswith(safe_name(stem) + '.merged.md'):
        fail('dual lookup missed the collector-written double-encoded output: %r' % got)
    with open(os.path.join(d, 'mitra.merged.md'), 'w', encoding='utf-8') as f:
        f.write('x')
    if not at.merged_output_path('mitra', out_dir=d):
        fail('dual lookup must still find the verbatim form')
    if at.merged_output_path('absent', out_dir=d) is not None:
        fail('a genuinely missing output must resolve to None')
    # H1430: one per-audit name snapshot preserves exact-case behavior and is not global/stale.
    snap = at._directory_names(d)
    if at.merged_output_path('MITRA', out_dir=d, exact_names=snap) is not None:
        fail('snapshot lookup accepted the wrong filename case')
    with open(os.path.join(d, 'fresh.merged.md'), 'w', encoding='utf-8') as f:
        f.write('x')
    if at.merged_output_path('fresh', out_dir=d, exact_names=snap) is not None:
        fail('an existing per-audit snapshot unexpectedly changed after collection')
    if not at.merged_output_path('fresh', out_dir=d, exact_names=at._directory_names(d)):
        fail('a fresh audit snapshot missed a file created by collection')
    # B19 wiring: both defect sites route through the shared resolver.
    for fname in ('audit_translation.py', 'stage2_pregate.py'):
        text = open(os.path.join(SRC, fname), encoding='utf-8').read()
        if 'merged_output_path(' not in text:
            fail('%s does not use the shared dual-lookup resolver' % fname)
    # B10 wiring: the factory save path refreshes the requeue singletons.
    sa = open(os.path.join(os.path.dirname(SRC), 'save_and_audit.py'), encoding='utf-8').read()
    if '"--write-requeue"' not in sa and "'--write-requeue'" not in sa:
        fail('save_and_audit audit invocation lacks --write-requeue (B10)')



def test_h1339_b11_b12_denylist_lifecycle_and_crash_refusal():
    """H1339 B11 + B12: the TM denylist gets a supersede lifecycle, and a crashed audit's
    blast-radius requeue list is refused, never consumed mechanically.

    B12: the denylist was append-forever and keyed on the INPUT address, so one defect
    requeue disabled TM reuse of that card permanently even after a passing replacement
    was promoted. B11: an unparseable child auditor requeues EVERY window key (fail-loud
    artifact); requeue_from_audit consumed that list mechanically, denylisting the window.
    """
    import tempfile
    import translation_memory as tm
    import requeue_from_audit as rfa
    import promote_final_cards as pfc
    d = tempfile.mkdtemp()
    dl = os.path.join(d, 'denylist.jsonl')
    from window_common import append_jsonl_line
    row = {'schema': 'pwg.translation_memory.denylist.v1', 'blocked_at': 'T'}
    append_jsonl_line(dl, dict(row, kind='card', address='ru:aaa'))
    append_jsonl_line(dl, dict(row, kind='card', address='ru:bbb'))
    append_jsonl_line(dl, dict(row, kind='frag', fsha='f1'))
    denied = tm.load_denylist(dl)
    if denied['addresses'] != {'ru:aaa', 'ru:bbb'} or denied['frags'] != {'f1'}:
        fail('denylist seed did not load: %r' % denied)
    # An unblock clears ONLY the exact match; a later re-denial re-blocks it.
    tm.append_unblock(['ru:aaa'], ['f1'], reason='replaced_by_promotion', path=dl)
    denied = tm.load_denylist(dl)
    if denied['addresses'] != {'ru:bbb'} or denied['frags'] != set():
        fail('unblock did not clear exactly the matching denials: %r' % denied)
    append_jsonl_line(dl, dict(row, kind='card', address='ru:aaa'))
    if 'ru:aaa' not in tm.load_denylist(dl)['addresses']:
        fail('a re-denial after an unblock must re-block (append order is chronology)')
    # Promote-side clearing: only LANDED subcards' currently-denied state is cleared.
    append_jsonl_line(dl, dict(row, kind='frag', fsha='f2'))
    best = {
        'x~~a': {'meta': {'input_hashes': {'x~~a': {'raw_sha256': 'aaa'}}},
                 'card': {'frag_prov': [{'fsha': 'f2'}]}},
        'y~~a': {'meta': {'input_hashes': {'y~~a': {'raw_sha256': 'bbb'}}}, 'card': {}},
        'z~~a': {'meta': {'input_hashes': {'z~~a': {'raw_sha256': 'zzz'}}}, 'card': {}},
    }
    addrs, frags = pfc.clear_denials_for_promotion(best, blocked_subs=['y~~a'], denylist=dl)
    if addrs != ['ru:aaa'] or frags != ['f2']:
        fail('promotion cleared the wrong denial set: %r %r' % (addrs, frags))
    denied = tm.load_denylist(dl)
    if denied['addresses'] != {'ru:bbb'} or denied['frags'] != set():
        fail('post-promotion denylist wrong (blocked subcard must stay denied): %r' % denied)
    # B11: a crashed audit report beside the requeue files refuses the mechanical consume.
    crash_dir = os.path.join(d, 'crash')
    os.makedirs(crash_dir)
    rq = os.path.join(crash_dir, 'requeue.keys.txt')
    with open(rq, 'w', encoding='utf-8') as f:
        f.write('k1\nk2\n')
    with open(os.path.join(crash_dir, 'audit_window.report.json'), 'w', encoding='utf-8') as f:
        json.dump({'crashed': ['sense_dupes-unparseable-verdict'], 'requeue': ['k1', 'k2']}, f)
    try:
        rfa.refuse_crashed_audit(rq, None)
        fail('a crashed audit requeue list was not refused')
    except SystemExit as e:
        if 'CRASHED' not in str(e):
            fail('crash refusal message wrong: %s' % e)
    with open(os.path.join(crash_dir, 'audit_window.report.json'), 'w', encoding='utf-8') as f:
        json.dump({'crashed': [], 'requeue': ['k1']}, f)
    rfa.refuse_crashed_audit(rq, None)          # clean report -> no refusal



def test_h1339_b13_b15_telemetry_and_siglum_precision():
    """H1339 B13 + B15: the siglum trigger fires only on citation-shaped Russian, and an
    outcome telemetry row can never be appended all-null.

    B13: TRANSLATED_SOURCE_SIGLUM's open `ману\\w*` fired HIGH_CONFIDENCE on legitimate
    prose («эпитет Ману», «манускрипт») -- unclearable requeue churn. B15: probe_log
    cmd_outcome appended rows with every structured field null, corrupting scripted rate
    math over the log.
    """
    import tempfile
    from types import SimpleNamespace
    import prompt_rule_audit as pra
    import probe_log as pl
    R = pra.TRANSLATED_SOURCE_SIGLUM
    for prose in ('эпитет Ману', 'в манускрипте написано', 'манускрипт 4'):
        if R.search(prose):
            fail('siglum trigger fired on legitimate prose: %r' % prose)
    for cite in ('Ману 4,126', 'Ригведа 9,67,30', 'Махабхарата 1,1816'):
        if not R.search(cite):
            fail('siglum trigger missed a genuinely translated citation: %r' % cite)
    d = tempfile.mkdtemp()
    old_jsonl = pl.JSONL
    try:
        pl.JSONL = os.path.join(d, 'probe.jsonl')
        with open(pl.JSONL, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'run_id': 'r1', 'kind': 'launch'}) + '\n')

        def ns(**kw):
            base = dict(run_id='r1', cards=None, clean=None, agents=None, tokens=None,
                        kill_timeouts=None, conn_errors=None, tripped=None, note='')
            base.update(kw)
            return SimpleNamespace(**base)
        try:
            pl.cmd_outcome(ns(note='ran fine'))
            fail('an all-null outcome row was appended')
        except SystemExit as e:
            if 'REFUSED' not in str(e):
                fail('all-null outcome refusal message wrong: %s' % e)
        pl.cmd_outcome(ns(note='ok=11 cards=20 tokens=123456'))
        out = [json.loads(ln) for ln in open(pl.JSONL, encoding='utf-8')][-1]['outcome']
        if (out['cards'], out['audit_clean'], out['subagent_tokens']) != (20, 11, 123456):
            fail('note-kv recovery did not populate the structured fields: %r' % out)
    finally:
        pl.JSONL = old_jsonl



def test_h1283_a1_pid_alive_and_dirlock_owner():
    """A1 (H1283): pid_alive is a real liveness probe (os.kill(pid,0) is broken on win32);
    DirLock.__exit__ spares a lock that has been re-owned by another pid."""
    import coordinator as coord
    import json as _json
    import tempfile as _tf
    import shutil as _sh
    if not coord.pid_alive(os.getpid()):
        fail('A1: pid_alive(own pid) must be True')
    if coord.pid_alive(2 ** 31 - 1):
        fail('A1: pid_alive(impossible pid) must be False')
    if coord.pid_alive(0) or coord.pid_alive(None) or coord.pid_alive('nope'):
        fail('A1: pid_alive of 0/None/non-numeric must be False')
    d = _tf.mkdtemp()
    try:
        lockpath = os.path.join(d, 'L')
        with coord.DirLock(lockpath, ttl_seconds=9999, wait_seconds=1):
            with open(os.path.join(lockpath, 'owner.json'), 'w', encoding='utf-8') as f:
                _json.dump({'pid': os.getpid() + 1, 'created_at': coord.utc_now()}, f)
        if not os.path.isdir(lockpath):
            fail('A1: DirLock.__exit__ deleted a lock owned by a different pid')
    finally:
        _sh.rmtree(d, ignore_errors=True)
    print('  A1: pid_alive is a real liveness probe; DirLock spares a foreign-owned lock')



def test_h1420_p2_win32_openprocess_error_leans_alive():
    """P2 (H1420): _win32_alive_on_openprocess_error leans ALIVE on every OpenProcess error except
    ERROR_INVALID_PARAMETER (87 = no such pid). The prior `err == ERROR_ACCESS_DENIED` reported
    DEAD for every error but 5, so any transient probe error falsely reclaimed a LIVE lock into two
    writers (the A1 double-writer window, H1283)."""
    import coordinator as coord
    if not coord._win32_alive_on_openprocess_error(5):
        fail('P2: ERROR_ACCESS_DENIED (5) is a live process we lack rights to open -> ALIVE')
    if coord._win32_alive_on_openprocess_error(coord.ERROR_INVALID_PARAMETER):
        fail('P2: ERROR_INVALID_PARAMETER (87) is the only definitively-dead error -> DEAD')
    for err in (0, 6, 8, 998, 1450):  # success/handle/memory/transient codes -> must lean ALIVE
        if not coord._win32_alive_on_openprocess_error(err):
            fail('P2: OpenProcess error %d must lean ALIVE (never falsely reclaim a live lock)' % err)
    print('  P2: OpenProcess error classification leans alive except no-such-pid (87)')



def test_h1420_p11_record_output_binds_run_id():
    """P11 (H1420): record-output refuses a workflow_result whose --run-id does not match the
    running lease's sealed run_id (a stale/zombie run recording against a re-leased run), and the
    on-disk lease stays 'running' for a correct retry. A matching --run-id proceeds."""
    import coordinator
    from types import SimpleNamespace
    old = os.environ.get('PWG_COORDINATOR_DIR')
    original_run = coordinator.run_cmd
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            adir = os.path.join(tmp, 'run')
            os.makedirs(adir)
            manifest = os.path.join(adir, 'manifest.json')
            with open(manifest, 'w', encoding='utf-8') as f:
                json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                           'meta': {'selected_keys': ['k'], 'input_hashes': {}}}, f)
            result_path = os.path.join(adir, 'result.json')
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump({'results': [{'key': 'k', 'card': {'key1': 'k'}}]}, f)

            def fresh_running_state():
                state = coordinator.default_state()
                state['leases'] = [{
                    'id': 'run', 'kind': 'verb', 'target': 'gam', 'state': 'running',
                    'artifact_dir': adir, 'execution_manifest': manifest,
                    'run_operation_id': 'op-X', 'run_id': 'run-X',
                }]
                coordinator.save_state(state)

            # A record-output carrying the WRONG run identity is refused before any subprocess runs.
            fresh_running_state()

            def must_not_run(*a, **k):
                fail('P11: mismatched --run-id must be refused before the audit subprocess runs')
            coordinator.run_cmd = must_not_run
            try:
                coordinator.record_output(SimpleNamespace(
                    lease_id='run', workflow_result=result_path, allow_stale=False,
                    transcript_dir=None, run_id='run-Y',
                    # A sealed run now binds the RESULT BYTES too: record-output refuses when
                    # --result-sha256 is absent. Supplied here so this case still fails for the
                    # run-id reason it is about, not for a missing hash it never meant to test.
                    result_sha256=coordinator.sha256_file(result_path)))
                fail('P11: record-output accepted a stale run-id')
            except SystemExit as e:
                if 'run-id' not in str(e):
                    raise
            if coordinator.load_state()['leases'][0]['state'] != 'running':
                fail('P11: a refused record-output must leave the on-disk lease running')

            # The matching run identity proceeds (the lease leaves 'running').
            fresh_running_state()

            def fake_audit(cmd, cwd=coordinator.REPO, check=True, timeout=None):
                adir_ = cmd[cmd.index('--out-dir') + 1]
                with open(os.path.join(adir_, 'window_status.json'), 'w', encoding='utf-8') as f:
                    json.dump({'state': 'blocked'}, f)
                with open(os.path.join(adir_, 'audit_window.report.json'), 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                return SimpleNamespace(returncode=2, stdout='', stderr='')
            coordinator.run_cmd = fake_audit
            coordinator.record_output(SimpleNamespace(
                lease_id='run', workflow_result=result_path, allow_stale=False,
                transcript_dir=None, run_id='run-X',
                result_sha256=coordinator.sha256_file(result_path)))
            if coordinator.load_state()['leases'][0]['state'] == 'running':
                fail('P11: a matching --run-id must let record-output proceed')
            print('  P11: record-output binds a supplied --run-id to the running lease run_id')
        finally:
            coordinator.run_cmd = original_run
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old



def test_h1420_p10_promote_rebuilds_tm_in_finally():
    """P10 (H1420): a post-store-commit failure must NOT cost the RU TM rebuild.

    The invariant is unchanged; the shape that carries it is not. `promote_ready` used to
    rebuild the TM in a `finally` around a per-lease loop, and this test drove that by
    faking the `--batch-manifest` subprocess. Promotion is now in-process and journal-phased:
    `build_promotion_derived` runs `translation_memory.build`/`build_frags` BEFORE the `try:`
    whose failure re-raises, so the TM is rebuilt by construction rather than by a `finally`.

    So this pins the guarantee against the current architecture: with the store already
    committed, make the step AFTER the TM build fail, and require that the rebuild still
    happened and the failure still propagates. Testing the old `finally` would now be
    testing a shape the code no longer has.
    """
    import promotion_journal_selftest as pjs
    import promotion_journal
    import coordinator
    import translation_memory
    import promote_final_cards as pfc
    saved = (translation_memory.build, translation_memory.build_frags, pfc.collect_cards)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            store, journal_path, _before, after, _kwargs = pjs.make_prepared(tmp)
            with open(store, 'wb') as f:            # the store IS committed at this point
                f.write(after)
            promotion_journal.mark_store_committed(journal_path, store_claim_held=True)

            tm_builds = []
            translation_memory.build = lambda *a, **k: (
                tm_builds.append('card'), (os.path.join(tmp, 'card.tm'), 1, 0))[1]
            translation_memory.build_frags = lambda *a, **k: (
                tm_builds.append('frag'), (os.path.join(tmp, 'frag.tm'), 1, 1))[1]

            def exploding_collect(_files):
                raise RuntimeError('synthetic post-TM derived failure')
            pfc.collect_cards = exploding_collect

            try:
                coordinator.build_promotion_derived(journal_path, store_claim_held=True)
                fail('P10: a failing derived step must propagate, not be swallowed')
            except RuntimeError as exc:
                if 'synthetic post-TM derived failure' not in str(exc):
                    raise
            if tm_builds != ['card', 'frag']:
                fail('P10: the RU TM rebuild must survive a post-store-commit failure '
                     '(ran %r)' % tm_builds)
            print('  P10: a post-commit derived failure still leaves the RU TM rebuilt')
        finally:
            translation_memory.build, translation_memory.build_frags, pfc.collect_cards = saved



def test_h2173_g5_malformed_result_rows_are_accounted():
    """G5 (H2173, audit S1-3): a result row that is not a dict, or that carries no usable
    `key`, used to hit a bare `continue` — counted in NEITHER `keys` NOR `nulls`. The window
    was billed for that call and the card was invisible to every accounting surface. Pin
    that such rows now land as FAILURES with a synthetic REASON, that the original row
    survives as evidence, and that well-formed rows are untouched."""
    import workflow_payload as wp
    payload = {'meta': {'root': 'h2173'}, 'results': [
        {'key': 'good', 'card': {'senses': [1]}},      # clean
        {'key': 'nullcard', 'card': None},             # H2089 null-card class
        {'card': {'senses': [1]}},                     # G5: keyed nowhere, but PAID
        {'key': '', 'card': None},                     # G5: falsy key
        'not-a-dict',                                  # G5: not an object at all
    ]}
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'wf.json')
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh)
        _p, _meta, results, keys, nulls = wp.workflow_payload(path)

    if len(keys) != 5:
        fail('G5: every billed row must be accounted in `keys` (got %d of 5: %r)'
             % (len(keys), keys))
    if len(nulls) != 4:
        fail('G5: the three malformed rows + the null card must all be failures '
             '(got %d of 4: %r)' % (len(nulls), nulls))
    if 'good' in nulls:
        fail('G5: a clean keyed card must NOT be dragged into nulls')
    malformed = [k for k in keys if wp.is_malformed_row_key(k)]
    if len(malformed) != 3:
        fail('G5: expected 3 synthetic malformed keys, got %r' % malformed)
    if len(set(keys)) != len(keys):
        fail('G5: synthetic keys must be unique per row index (got %r)' % keys)
    for key in malformed:
        if key not in nulls:
            fail('G5: malformed row %s must also be a null/failure' % key)
    # The rewritten rows carry a reason AND the original evidence.
    stamped = [r for r in results if isinstance(r, dict) and r.get('malformed_result_row')]
    if len(stamped) != 3:
        fail('G5: `results` must carry the 3 rewritten rows (got %d)' % len(stamped))
    reasons = {r['failure_REASON'] for r in stamped}
    if reasons != {wp.MALFORMED_MISSING_KEY, wp.MALFORMED_NOT_A_DICT}:
        fail('G5: both malformed classes need distinct REASONs (got %r)' % reasons)
    for row in stamped:
        if not row.get('malformed_row_raw'):
            fail('G5: the original row must survive as evidence (malformed_row_raw)')
        if not (row.get('error') or {}).get('failure_REASON'):
            fail('G5: a malformed row needs the structured error shape audits already read')
    if results[0].get('malformed_result_row'):
        fail('G5: a well-formed row must not be rewritten')
    print('  G5: 3 unaccountable rows now bill as failures (keys 5/5, nulls 4/4)')



def test_h2173_g8_promote_refuses_route_foreign_artifact():
    """G8 (H2173, audit F-1): promotion checked `execution_route` for is-a-nonblank-string
    only, so a v2-SHAPED artifact from any other route (the retired Max-Workflow lane, a
    hand-built envelope) could enter the canonical store. Pin that the value itself is now
    compared against execution_contract.HEADLESS_ROUTE — and that a correct route still gets
    PAST this gate, so the check cannot be passing by refusing everything."""
    sys.path.insert(0, os.path.dirname(HERE))
    import promote_final_cards as pfc
    import execution_contract

    def entry(route):
        return {'card': {}, 'meta': {
            'execution_manifest_schema': 'pwg.headless_execution_manifest.v2',
            'execution': {'profile_slot': 'c4', 'config_dir_fingerprint': 'abc',
                          'execution_route': route, 'executor_lane': 'headless',
                          'validation_method': 'schema', 'model_identifier': 'claude-sonnet-5'}}}

    for foreign in ('workflow', 'max-workflow', 'CLAUDE-CLI-HEADLESS', ' '.join(
            [execution_contract.HEADLESS_ROUTE, 'x'])):
        try:
            pfc.validate_promotion_entry('k1', entry(foreign))
        except pfc.PromotionContractError as exc:
            if 'execution_route' not in str(exc):
                fail('G8: a route refusal must name execution_route (got %s)' % exc)
        else:
            fail('G8: route %r must not be promotable' % foreign)
    # Positive control: the real route passes the ROUTE gate and dies later, on card schema.
    try:
        pfc.validate_promotion_entry('k1', entry(execution_contract.HEADLESS_ROUTE))
    except pfc.PromotionContractError as exc:
        if 'execution_route' in str(exc):
            fail('G8: the headless route must not be refused by the route gate (%s)' % exc)
    else:
        fail('G8: an empty card should still fail promotion on schema grounds')
    print('  G8: promote compares execution_route to the contract, not just its type')



def test_h2173_g10_classify_run_reads_the_live_lane():
    """G10 (H2173, audit F-B7): classify_run was written against the JS harness summary and
    never re-read after the live route became the headless CLI. `heal_calls`, `agents_spent`
    and `budget_kill_switch_tripped` do not exist in headless_worker's summary, so EVERY live
    window answered 'unclassifiable' and the budget trip always read False. Pin that both
    lane vocabularies now classify, and that the headless trip is actually seen."""
    import classify_run as cr
    # Exactly the shape headless_worker.py builds (no heal_calls, no agents_spent, no boolean).
    headless = {'cards': 4, 'ok': 4, 'null': 0, 'null_keys': [], 'partial_keys': [],
                'translate_agents_spent': 6, 'heal_agents_spent': 2, 'budget_stops': 0,
                'kill_timeouts': 0, 'conn_errors': 0}
    verdict, _reasons, signals = cr.classify(dict(headless))
    if verdict == 'unclassifiable':
        fail('G10: a live headless summary must be classifiable, not refused')
    if verdict != 'clean':
        fail('G10: an all-ok headless window must classify clean; got %r' % verdict)
    if signals['agents_spent'] != 8:
        fail('G10: agents_spent must sum the two headless pools (got %r)'
             % signals['agents_spent'])
    if signals['infra_kill_threshold'] != max(3, math.ceil(0.25 * 8)):
        fail('G10: the kill threshold must derive from the REAL agent count, not 0')
    # A headless budget stop IS the kill switch firing.
    tripped = dict(headless, budget_stops=3, null_keys=['a'])
    verdict, _reasons, signals = cr.classify(tripped)
    if not signals['budget_kill_switch_tripped']:
        fail('G10: budget_stops>0 must read as a budget trip on the headless lane')
    if verdict != 'code-failure':
        fail('G10: a quiet-network trip with nulls is a code-failure; got %r' % verdict)
    # The JS vocabulary must keep winning when it is present — no silent overwrite.
    js = dict(headless, heal_calls=99, agents_spent=42, budget_kill_switch_tripped=False,
              budget_stops=7)
    _v, _r, signals = cr.classify(js)
    if signals['agents_spent'] != 42 or signals['budget_kill_switch_tripped']:
        fail('G10: an explicit JS-lane value must never be overwritten by a derived one')
    print('  G10: classify_run adjudicates the headless lane (and still the JS lane)')



def test_h2173_g10_probe_gate_defaults_and_live_boundary():
    """G10 (H2173, audit F-B4): `verdict_for`'s default policy and the CLI `--policy` default
    were frozen at production_v1 while CURRENT_POLICY advanced to v2 and then v3 — the live
    lane produced receipts naming a retired gate, and v3's api ceiling could never fire
    because nothing passed api_ms. Pin the defaults to CURRENT_POLICY and put a boundary test
    on the LIVE ceilings, derived from the policy table so a future bump cannot leave this
    test asserting a dead number."""
    import probe_log
    import inspect
    spec = inspect.signature(probe_log.verdict_for)
    if spec.parameters['policy'].default != probe_log.CURRENT_POLICY:
        fail('G10: verdict_for must default to CURRENT_POLICY (got %r)'
             % spec.parameters['policy'].default)
    live = probe_log.POLICIES[probe_log.CURRENT_POLICY]
    ceil_ms = live['latency_ceil_ms']
    floor = live['payload_floor_bytes']
    ok = dict(conn_errors=0, payload_bytes=floor, kind='warmup', schema_valid=True)
    # Boundary: strictly under the live ceiling is GO, exactly at it is NO-GO.
    verdict, reason = probe_log.verdict_for(ceil_ms - 1, **ok)
    if verdict != 'GO':
        fail('G10: %d ms must pass the live ceiling %d (%s)' % (ceil_ms - 1, ceil_ms, reason))
    verdict, _reason = probe_log.verdict_for(ceil_ms, **ok)
    if verdict != 'NO-GO':
        fail('G10: %d ms must NOT pass a ceiling of %d' % (ceil_ms, ceil_ms))
    # The api ceiling is a SECOND, independent fail condition when the policy declares one.
    api_ceil = live.get('api_ceil_ms')
    if api_ceil is not None:
        verdict, reason = probe_log.verdict_for(ceil_ms - 1, api_ms=api_ceil, **ok)
        if verdict != 'NO-GO' or 'duration_api_ms' not in reason:
            fail('G10: a route-time breach must fail even when wall is within ceiling')
        verdict, _r = probe_log.verdict_for(ceil_ms - 1, api_ms=api_ceil - 1, **ok)
        if verdict != 'GO':
            fail('G10: a healthy route under both ceilings must pass')
    # The CLI must be able to supply api_ms at all — the gate was unreachable without it.
    parser_src = inspect.getsource(probe_log)
    if "'--api-ms'" not in parser_src:
        fail('G10: probe_log CLI must expose --api-ms or the v3 route guard cannot fire')
    print('  G10: probe defaults track %s; boundary pinned at %d ms wall / %s ms api'
          % (probe_log.CURRENT_POLICY, ceil_ms, api_ceil))



def test_h2173_g10_declared_budgets_are_read_or_labelled():
    """G10 (H2173, audit F-B7/F-B5): two halves of the same defect class — a budget the
    executor READS that the emitter never wrote (`budgets.max_agents`, so `max_total_agents`
    was None on every live window), and a state field the operator SETS that enforcement
    ignored (`state['translation_limit']`, while `preparation_limit` two frames down already
    honoured state)."""
    import gen_opt_harness2  # noqa: F401 -- import guard only; the manifest block is source-pinned
    import coordinator
    src = open(os.path.join(HERE,
                            'gen_opt_harness2.py'), encoding='utf-8').read()
    budgets_block = src.split("'budgets': {", 1)[1].split('},', 1)[0]
    for key in ('max_agents', 'max_translate_agents', 'max_heal_agents', 'timeout_ceil_ms'):
        if "'%s'" % key not in budgets_block:
            fail('G10: the execution manifest budgets block must carry %r — headless_worker '
                 'reads it' % key)
    # F-B5: the standard-mode runtime cap must honour state, exactly as preparation does.
    leases = [{'id': 'l1', 'kind': 'verb', 'state': 'prepared'},
              {'id': 'l2', 'kind': 'verb', 'state': 'prepared'}]
    state = {'leases': leases, 'translation_limit': 1, 'runtime_mode': 'standard'}
    try:
        coordinator.begin_run_leases(state, ['l1', 'l2'], mode='standard')
    except SystemExit as exc:
        if 'runtime cap reached (1)' not in str(exc):
            fail('G10: the cap must report the STATE limit, not the constant (got %s)' % exc)
    else:
        fail('G10: state["translation_limit"]=1 must refuse a 2-lease standard run')
    print('  G10: manifest budgets feed the executor; translation_limit binds from state')

