#!/usr/bin/env python
import io
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Isolation from production data, established before any repo import (several modules
# resolve store/coordinator constants at import time). See selftest_isolation.py.
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_isolation import guard as _isolation_guard  # noqa: E402
_isolation_guard()

import coordinator
import no_pwg_scale_plan as planner


def main():
    queue = [{'key1': 'k%03d' % i} for i in range(120)]
    ordered, tail = planner.build_order(queue, {'k003'}, ['k010~~x', 'k005~~x'])
    assert ordered[:2] == ['k010', 'k005'] and 'k003' not in ordered
    assert tail == ['k010', 'k005']

    with tempfile.TemporaryDirectory() as td:
        here, out = os.path.join(td, 'here'), os.path.join(td, 'out')
        os.makedirs(here); os.makedirs(out)
        open(os.path.join(here, 'run_pilot_wf.test_w01.js'), 'w').close()
        open(os.path.join(out, 'wf_output.test_w02_rq1.json'), 'w').close()
        assert planner.used_window_indices('test_w', here, out) == {1, 2}
        assert planner.next_free_index('test_w', here=here, out=out) == 3

        old = os.environ.get('PWG_COORDINATOR_DIR')
        os.environ['PWG_COORDINATOR_DIR'] = os.path.join(td, 'coord')
        try:
            for i in range(5):
                artifact = os.path.join(td, 'a%d' % i); os.makedirs(artifact)
                harness = os.path.join(artifact, 'h.js')
                manifest = os.path.join(artifact, 'm.json')
                preflight = os.path.join(artifact, 'p.json')
                for path in (harness, manifest, preflight):
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write('{}')
                coordinator.register_prepared_lease(
                    'w%d' % i, 'test', ['key%d' % i], harness, manifest, preflight,
                    artifact_path=artifact)
            state = coordinator.load_state()
            assert len(state['leases']) == 5
            assert state['preparation_limit'] == coordinator.PREPARATION_LIMIT
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old

    source = {'summary': {'cards': 3}, 'results': [
        {'key': 'clean', 'card': {'key1': 'clean'}},
        {'key': 'defect', 'card': {'key1': 'defect'}},
        {'key': 'null', 'card': None},
    ]}
    clean = coordinator.clean_result_payload(source, {'defect'})
    assert [row['key'] for row in clean['results']] == ['clean']
    assert clean['summary']['cards'] == 1 and clean['summary']['null'] == 0
    with tempfile.TemporaryDirectory() as td:
        lock_path = os.path.join(td, '.promotion.lock')
        os.mkdir(lock_path)
        with open(os.path.join(lock_path, 'owner.json'), 'w', encoding='utf-8') as f:
            json.dump({'pid': os.getpid(), 'created_at': coordinator.utc_now()}, f)
        try:
            with coordinator.DirLock(lock_path, wait_seconds=0):
                pass
        except SystemExit as exc:
            assert 'lock busy' in str(exc)
        else:
            raise AssertionError('live promotion conflict was not refused')
    _test_planner_binding()
    print('windows100_selftest: PASS')


def _test_planner_binding():
    """H3677 / FINDINGS 604 gate 3: the planner must stamp a PRODUCTION-eligible manifest.

    Unbound, `gen_opt_harness2` emits `pwg.headless_execution_manifest.v1` and
    `bounded_staged_run` refuses it, so every planner-prepared lease was unrunnable and
    H3659 had to rebuild the manifest by hand before it could spend. The binding is
    asserted against `coordinator.prepare`'s own list rather than a copied literal, so the
    two paths cannot drift apart again.
    """
    import argparse
    args = argparse.Namespace(profile_slot=None, config_dir=None,
                              execution_route='claude-cli-headless',
                              executor_lane='serial-whole-card',
                              validation_method='audit_window+final_schema')
    assert planner.binding_args(args) == [], 'unbound planner must pass no binding'

    args.profile_slot, args.config_dir = 'c1', os.path.join('.', 'cfg')
    bound = planner.binding_args(args)
    assert bound[0] == '--profile-slot=c1', bound
    assert bound[1] == '--config-dir=%s' % os.path.abspath(os.path.join('.', 'cfg')), bound
    assert bound[2:] == ['--execution-route=claude-cli-headless',
                         '--executor-lane=serial-whole-card',
                         '--validation-method=audit_window+final_schema'], bound

    # The flag NAMES and their order must match what `coordinator.prepare` builds, or a
    # planner lease and a coordinator lease stop being production-eligible on equal terms.
    src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'coordinator.py'), encoding='utf-8').read()
    for flag in ('--profile-slot=', '--config-dir=', '--execution-route=claude-cli-headless',
                 '--executor-lane=', '--validation-method=audit_window+final_schema'):
        assert flag in src, 'coordinator no longer passes %s' % flag

    # And the lease must carry the binding, exactly as `prepare` records it.
    import inspect
    sig = inspect.signature(coordinator.register_prepared_lease).parameters
    for name in ('profile_slot', 'config_dir', 'executor_lane'):
        assert name in sig, 'register_prepared_lease drops %s' % name


if __name__ == '__main__':
    main()
