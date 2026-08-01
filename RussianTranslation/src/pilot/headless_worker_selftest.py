#!/usr/bin/env python
import contextlib
import hashlib
import json
import subprocess
import sys
import tempfile
import os
from types import SimpleNamespace

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Isolation from production data, established before any repo import (several modules
# resolve store/coordinator constants at import time). See selftest_isolation.py.
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_isolation import guard as _isolation_guard  # noqa: E402
_isolation_guard()

import headless_worker as h
import gen_opt_harness2 as generator
import proc_tree
from call_reservation import CallReservationLedger
from execution_contract import ActiveCallClaim, config_dir_fingerprint


class MemoryCallLedger:
    """Selftest-only reservation authority; fake runners never reach a provider."""

    def __init__(self):
        self.next_id = 0
        self.finalized = {}

    def reserve(self, *_args, **_kwargs):
        self.next_id += 1
        return 'test-call-%d' % self.next_id

    def finalize(self, reservation, telemetry):
        self.finalized[reservation] = dict(telemetry)


def manifest():
    return {
        'schema': 'pwg.headless_execution_manifest.v1',
        'meta': {'root': 'fixture', 'lang': 'ru', 'selected_keys': ['agni'],
                 'nominal_keymap': None, 'gen_model': 'claude-sonnet-5'},
        'field': 'russian', 'model': 'claude-sonnet-5',
        'prompt': {'preamble': 'P', 'grammar': 'G', 'grammars': {},
                   'translation': 'T', 'nws_rule': ''},
        'output_schema': {'type': 'object'}, 'batches': [['agni']],
        'inputs': {'agni': {'skeleton': '{T1} Feuer', 'portrait': '{}',
                            'ls': 1, 'sk': 0, 'nws': 0}},
        'placeholder_maps': {'agni': ['<ls>RV.</ls>']},
        'fragment_groups': {}, 'fragment_placeholder_maps': {}, 'fragment_tm': {},
        'runtime': {'binary_split': True, 'per_card_heal_budget': True,
                    'per_card_heal_factor': 1.5, 'per_card_heal_headroom': 3,
                    'kill_timeout_no_bisect': True, 'whole_attempts': 2,
                    'fragment_attempts': 3},
        'tm_resolved': {}, 'degenerate_resolved': {}, 'suggestions': {},
        'presplit_keys': [],
    }


def proc(returncode=0, stdout='', stderr=''):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


_FIXTURE_CONFIG_DIR = tempfile.mkdtemp(prefix='hw-selftest-cfg-')


def execute(test_manifest, runner, config_dir=None):
    """Use a real, portable executable path while the runner fakes its output.

    `config_dir` is REQUIRED by h.execute (the paid-boundary guard: no
    CLAUDE_CONFIG_DIR, no execution). Every test routed through this helper runs a
    FAKE runner against a v1 fixture manifest, so it needs a config dir that exists
    but must never be a real profile -- a scratch dir is exactly right, and passing
    it explicitly beats mutating os.environ for the whole process. Without this the
    suite aborted on its first `execute()` call (found on rebase onto master,
    26-07-2026; the guard and this helper are both from the hardening branch, so the
    breakage is in the branch as delivered, not in the rebase).
    """
    return h.execute(
        test_manifest, claude=sys.executable, runner=runner,
        call_reservation=MemoryCallLedger(),
        config_dir=config_dir or _FIXTURE_CONFIG_DIR)


def success_runner(argv, **kwargs):
    assert '--json-schema' in argv and '--model' in argv
    card = {'key1': 'agni', 'records': [{'grammar': '{T1} m.', 'senses': [
        {'tag': '1', 'german': '{T1} Feuer', 'russian': '{T1} огонь'}]}]}
    wrapper = {'structured_output': {'cards': [card]}}
    return proc(stdout=json.dumps(wrapper))


def _soft_nonresolve_runner():
    """A runner that always returns a well-formed-but-empty result, so the engine keeps
    trying to spawn (retries/bisect/heal) -- maximum spawn pressure, no HardFailure."""
    def runner(argv, **kwargs):
        runner.n += 1
        return proc(stdout=json.dumps({'structured_output': {'cards': []}}))
    runner.n = 0
    return runner


def test_translate_budget_binds():
    """R3 (C-12/C-13): the manifest agent budget and the --max-agents override cap the ACTUAL
    spawn count. The 1-key fixture would spawn `whole_attempts`=2 unbounded; a ceiling of 1
    must cut it to 1, consuming no extra call."""
    r = _soft_nonresolve_runner()
    execute(manifest(), r)
    assert r.n == 2, 'expected 2 unbounded spawns (whole_attempts), got %d' % r.n
    r = _soft_nonresolve_runner()
    m = manifest(); m['budgets'] = {'max_translate_agents': 1}
    execute(m, r)
    assert r.n == 1, 'manifest budget=1 did not bind: %d spawns' % r.n
    r = _soft_nonresolve_runner()
    h.execute(
        manifest(), claude=sys.executable, runner=r, max_agents_override=1,
        call_reservation=MemoryCallLedger(), config_dir=_FIXTURE_CONFIG_DIR)
    assert r.n == 1, '--max-agents=1 did not bind: %d spawns' % r.n
    print('  R3 budget: unbounded=2; manifest ceiling and --max-agents both cap actual spawns to 1')


def test_h1610_preserve_budget_exceeded_over_selfheal_stamp():
    """H1610: when --max-agents=1 starves heal after the first translate refuse-path,
    failures must retain budget_exceeded* (not selfheal-nothing-resolved). Multi-key
    starvation is refused before any call — so this pin uses 1 key + override=1 so the
    whole-card attempt spends the budget and self_heal cannot spawn."""
    r = _soft_nonresolve_runner()
    m = manifest()
    # Give the key a fragment group so self_heal runs (and would stamp selfheal-nothing
    # if note() overwrote). With max_agents_override=1 the whole-card attempt(s) spend
    # the budget; heal path then budget_exceeds without overwriting the first note.
    m['fragment_groups'] = {'agni': [[{'skeleton': '{T1} x', 'si': 0, 'fsha': 'f0'}]]}
    m['fragment_placeholder_maps'] = {'agni': [['<ls>RV.</ls>']]}
    m['fragment_tm'] = {'agni': [[]]}
    m['runtime'] = dict(m['runtime'], whole_attempts=1, fragment_attempts=1)
    payload, status, code = h.execute(m, claude=sys.executable, runner=r,
                                      max_agents_override=1,
                                      call_reservation=MemoryCallLedger(),
                                      config_dir=_FIXTURE_CONFIG_DIR)
    assert code == 0 and payload is not None
    failures = payload['summary']['failures']
    assert 'agni' in failures, failures
    err = failures['agni']
    assert 'budget_exceeded' in err or err.startswith('timeout') or 'unresolved' in err or err != 'selfheal-nothing-resolved', (
        'selfheal stamp clobbered the real stop reason: %r (budget_stops=%s)'
        % (err, payload['summary'].get('budget_stops')))
    # The smoking-gun triad must still be readable when budget starved the heal lane.
    if payload['summary'].get('budget_stops', 0) > 0:
        assert err != 'selfheal-nothing-resolved', failures
    print('  H1610 preserve: failures[agni]=%r budget_stops=%s'
          % (err, payload['summary'].get('budget_stops')))


def test_h1610_refuse_max_agents_starves_multikey():
    """H1610: --max-agents N with N < selected_keys is a hard refuse (no paid call)."""
    r = _soft_nonresolve_runner()
    m = manifest()
    m['meta'] = dict(m['meta'], selected_keys=['a', 'b', 'c'])
    m['batches'] = [['a'], ['b'], ['c']]
    for k in ('a', 'b', 'c'):
        m['inputs'][k] = m['inputs']['agni']
        m['placeholder_maps'][k] = m['placeholder_maps']['agni']
    try:
        h.execute(
            m, claude=sys.executable, runner=r, max_agents_override=1,
            call_reservation=MemoryCallLedger(), config_dir=_FIXTURE_CONFIG_DIR)
        assert False, 'expected ValueError starvation refuse'
    except ValueError as exc:
        assert 'starves' in str(exc) and '3-key' in str(exc), exc
    assert r.n == 0, 'starvation refuse must spawn zero: %d' % r.n
    print('  H1610 refuse: multi-key --max-agents=1 raises before any spawn')


def test_h2b_translate_budget_preserves_attempt_content_note():
    """H2b: a retry refused by the translate budget must not erase attempt 1's
    per-key content diagnosis with the batch-wide budget stop."""
    m = manifest()
    m['budgets'] = {'max_translate_agents': 1}
    m['runtime'] = dict(m['runtime'], whole_attempts=2, binary_split=False)
    dropped = {'key1': 'agni', 'records': [{'grammar': '', 'senses': [
        {'tag': '1', 'german': '{T1} Feuer', 'russian': 'огонь'}]}]}

    def content_reject_runner(argv, **kwargs):
        return proc(stdout=json.dumps({'structured_output': {'cards': [dropped]}}))

    payload, status, code = execute(m, content_reject_runner)
    assert code == 0 and payload is not None, (code, status)
    assert payload['summary']['budget_stops'] == 1, payload['summary']
    assert payload['summary']['failures']['agni'] == 'translation-fidelity-reject', (
        'retry budget clobbered attempt-1 content diagnosis: %r'
        % payload['summary']['failures']['agni'])
    print('  H2b preserve: retry budget leaves attempt-1 translation-fidelity-reject observable')


def test_call_timeout_clamped():
    """R4 (C-15): the timeout handed to subprocess is min(operator, budgets.timeout_ceil_ms, HARD)."""
    seen = {}
    def capture_runner(argv, **kwargs):
        seen['timeout'] = kwargs.get('timeout')
        return success_runner(argv, **kwargs)
    execute(manifest(), capture_runner)   # operator default 7200 s -> clamp to HARD (180 s)
    assert seen['timeout'] == h.HARD_TIMEOUT_MS / 1000.0, 'not clamped to HARD: %r' % seen['timeout']
    seen.clear()
    m = manifest(); m['budgets'] = {'timeout_ceil_ms': 45000}
    execute(m, capture_runner)
    assert seen['timeout'] == 45.0, 'timeout_ceil_ms not honoured: %r' % seen['timeout']
    print('  R4 timeout: clamped to min(operator,ceil,180000ms) -> 180.0s then 45.0s')


def test_durable_call_reservation():
    """The durable ceiling is consumed before the runner, including malformed results."""
    with tempfile.TemporaryDirectory() as td:
        original_prefix = h.claude_argv_prefix
        h.claude_argv_prefix = lambda _claude: ['claude']
        try:
            spawned = []

            def runner(_argv, **_kwargs):
                spawned.append(1)
                if len(spawned) == 1:
                    return SimpleNamespace(returncode=0, stdout='not-json', stderr='')
                return SimpleNamespace(returncode=0, stderr='', stdout=json.dumps({
                    'structured_output': {'cards': []},
                    'usage': {'input_tokens': 4, 'output_tokens': 1},
                    'total_cost_usd': 0.10,
                }))

            # HeadlessEngine.call refuses to spawn without the live canonical profile
            # claim -- the same lock execute() takes. Constructing the engine directly
            # (as this test does, to drive .call() one reservation at a time) must
            # therefore hold that claim too, or the test never reaches the ledger
            # behaviour it exists to prove.
            fingerprint = config_dir_fingerprint(_FIXTURE_CONFIG_DIR)
            zero = CallReservationLedger(os.path.join(td, 'zero.json'), 'r0', 0)
            with ActiveCallClaim(fingerprint) as claim:
                eng = h.HeadlessEngine(manifest(), 'claude', 30, runner, call_reservation=zero,
                                       config_dir=_FIXTURE_CONFIG_DIR, active_claim=claim)
                value, error = eng.call('p', 'zero', ['agni'])
                assert value is None and error == 'budget_exceeded:max_calls' and not spawned

            one = CallReservationLedger(os.path.join(td, 'one.json'), 'r1', 2)
            with ActiveCallClaim(fingerprint) as claim:
                eng = h.HeadlessEngine(manifest(), 'claude', 30, runner, call_reservation=one,
                                       config_dir=_FIXTURE_CONFIG_DIR, active_claim=claim)
                _value, error = eng.call('p', 'malformed', ['agni'])
                assert error.startswith('malformed_output') and one.spent() == 1
                value, error = eng.call('p', 'success', ['agni'])
                assert error is None and value == {'cards': []}
                usage = one.usage()
                assert usage['cost_evaluable'] is False and usage['observed_cost_usd'] == 0.10
                _value, error = eng.call('p', 'refused', ['agni'])
                assert error == 'budget_exceeded:max_calls' and len(spawned) == 2
        finally:
            h.claude_argv_prefix = original_prefix
    print('  call ledger: zero spawn; malformed+success cumulative cost stays unevaluable; cap refused')


def test_cli_reservation_and_preflight_gates():
    with tempfile.TemporaryDirectory() as td:
        original_runner = h.run_tree_kill
        original_prefix = h.claude_argv_prefix
        original_config_dir = os.environ.get('CLAUDE_CONFIG_DIR')
        spawned = []
        h.run_tree_kill = lambda *_a, **_k: spawned.append(1)
        h.claude_argv_prefix = lambda _c: [sys.executable]
        try:
            # The paid-boundary guard is checked BEFORE --max-calls is consulted, so the
            # max_calls=0 case below needs a config dir too -- this test only set one later,
            # for its v2 half, and so exited 2 (configuration) instead of the 0 it asserts.
            os.environ['CLAUDE_CONFIG_DIR'] = os.path.join(td, 'cli-profile')
            os.makedirs(os.environ['CLAUDE_CONFIG_DIR'], exist_ok=True)
            # CLI max_calls=0: the Python worker runs, but no paid CLI runner is entered.
            v1_path = os.path.join(td, 'v1.json')
            json.dump(manifest(), open(v1_path, 'w', encoding='utf-8'))
            ledger_path = os.path.join(td, 'zero.calls.json')
            out = os.path.join(td, 'out.json')
            status = os.path.join(td, 'status.json')
            try:
                h.main([v1_path, '--output', out, '--status-out', status,
                        '--allow-historical-v1', '--claude-bin', sys.executable,
                        '--call-reservation', ledger_path, '--run-id', 'zero',
                        '--max-calls', '0'])
            except SystemExit as exc:
                assert exc.code == 0, exc
            assert not spawned and CallReservationLedger(ledger_path, 'zero', 0).spent() == 0

            # Missing/malformed/hash-drift v2 preflight refuses before reservation/spawn.
            v2 = manifest()
            v2['schema'] = h.SCHEMA_V2
            config_dir = os.path.join(td, 'profile')
            os.makedirs(config_dir)
            os.environ['CLAUDE_CONFIG_DIR'] = config_dir
            v2['execution'] = {
                'profile_slot': 'acc',
                'config_dir_fingerprint': config_dir_fingerprint(config_dir),
                'execution_route': 'claude-cli-headless', 'executor_lane': 'test',
                'validation_method': 'test', 'model_identifier': v2['model'],
            }
            v2['key_provenance'] = {'agni': 'real'}
            v2_path = os.path.join(td, 'v2.json')
            json.dump(v2, open(v2_path, 'w', encoding='utf-8'))
            manifest_sha = h.sha256_path(v2_path)
            gate_ledger = os.path.join(td, 'gate.calls.json')
            malformed = os.path.join(td, 'bad.preflight.json')
            open(malformed, 'w', encoding='utf-8').write('{}')
            good = os.path.join(td, 'good.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'selected_keys': ['agni'],
                'cost_gate': {'over_ceiling': False},
            }, open(good, 'w', encoding='utf-8'))
            over = os.path.join(td, 'over.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'selected_keys': ['agni'],
                'cost_gate': {'over_ceiling': True},
            }, open(over, 'w', encoding='utf-8'))
            wrong_scope = os.path.join(td, 'wrong-scope.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'selected_keys': ['soma'],
                'cost_gate': {'over_ceiling': False},
            }, open(wrong_scope, 'w', encoding='utf-8'))
            empty_scope = os.path.join(td, 'empty-scope.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'selected_keys': [],
                'cost_gate': {'over_ceiling': False},
            }, open(empty_scope, 'w', encoding='utf-8'))
            duplicate_scope = os.path.join(td, 'duplicate-scope.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'selected_keys': ['agni', 'agni'],
                'cost_gate': {'over_ceiling': False},
            }, open(duplicate_scope, 'w', encoding='utf-8'))
            missing_scope = os.path.join(td, 'missing-scope.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'cost_gate': {'over_ceiling': False},
            }, open(missing_scope, 'w', encoding='utf-8'))
            synthetic = os.path.join(td, 'synthetic.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'selected_keys': ['agni'],
                'synthetic_probe_only': True,
                'cost_gate': {'over_ceiling': False},
            }, open(synthetic, 'w', encoding='utf-8'))
            non_boolean_gate = os.path.join(td, 'non-boolean.preflight.json')
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'selected_keys': ['agni'],
                'cost_gate': {'over_ceiling': 0},
            }, open(non_boolean_gate, 'w', encoding='utf-8'))
            base = [v2_path, '--output', out, '--claude-bin', sys.executable,
                    '--call-reservation', gate_ledger, '--run-id', 'gate',
                    '--max-calls', '2']
            # Each case reaches the intended gate: only the first two omit/corrupt the
            # manifest seal; all preflight cases carry the exact seal over manifest bytes.
            refused = (
                [],
                ['--manifest-sha256', 'f' * 64],
                ['--manifest-sha256', manifest_sha],
                ['--manifest-sha256', manifest_sha, '--preflight', malformed],
                ['--manifest-sha256', manifest_sha, '--preflight', good,
                 '--preflight-sha256', 'f' * 64],
                ['--manifest-sha256', manifest_sha, '--preflight', over],
                ['--manifest-sha256', manifest_sha, '--preflight', wrong_scope],
                ['--manifest-sha256', manifest_sha, '--preflight', empty_scope],
                ['--manifest-sha256', manifest_sha, '--preflight', duplicate_scope],
                ['--manifest-sha256', manifest_sha, '--preflight', missing_scope],
                ['--manifest-sha256', manifest_sha, '--preflight', synthetic],
                ['--manifest-sha256', manifest_sha, '--preflight', non_boolean_gate],
            )
            for index, extra in enumerate(refused):
                status_i = os.path.join(td, 'status%d.json' % index)
                try:
                    h.main(base + ['--status-out', status_i] + extra)
                except SystemExit as exc:
                    assert exc.code == 2, (index, exc)
            assert CallReservationLedger(gate_ledger, 'gate', 2).spent() == 0
            assert not spawned
            try:
                h.main([v2_path, '--output', out,
                        '--status-out', os.path.join(td, 'no-ledger.status.json'),
                        '--claude-bin', sys.executable,
                        '--manifest-sha256', manifest_sha, '--preflight', good])
            except SystemExit as exc:
                assert exc.code == 2, exc
            assert not spawned

            # A fully sealed v2 invocation can complete offline with max_calls=0.
            # It must bind both artifacts to the exact manifest bytes, while the
            # durable reservation prevents the fake runner from ever being entered.
            valid_out = os.path.join(td, 'valid.out.json')
            valid_status = os.path.join(td, 'valid.status.json')
            valid_ledger = os.path.join(td, 'valid.calls.json')
            try:
                h.main([
                    v2_path, '--output', valid_out, '--status-out', valid_status,
                    '--claude-bin', sys.executable,
                    '--manifest-sha256', manifest_sha,
                    '--preflight', good, '--preflight-sha256', h.sha256_path(good),
                    '--call-reservation', valid_ledger, '--run-id', 'valid',
                    '--max-calls', '0',
                ])
            except SystemExit as exc:
                assert exc.code == 0, exc
            result = json.load(open(valid_out, encoding='utf-8'))
            completed = json.load(open(valid_status, encoding='utf-8'))
            assert result['meta']['execution_manifest_sha256'] == manifest_sha, result['meta']
            assert completed['manifest_sha256'] == manifest_sha, completed
            assert completed['result_sha256'] == h.sha256_path(valid_out), completed
            assert CallReservationLedger(valid_ledger, 'valid', 0).spent() == 0
            assert not spawned
        finally:
            h.run_tree_kill = original_runner
            h.claude_argv_prefix = original_prefix
            if original_config_dir is None:
                os.environ.pop('CLAUDE_CONFIG_DIR', None)
            else:
                os.environ['CLAUDE_CONFIG_DIR'] = original_config_dir
    print('  CLI gates: exact manifest seal + real-scope preflight required; malformed, '
          'synthetic, duplicate/wrong/empty scope spawn zero; result/status hashes bound')


@contextlib.contextmanager
def _h1_worker_env():
    """Scratch dir + CLAUDE_CONFIG_DIR + a spawn tracker, all restored on exit.

    Every H1 pin must prove **zero** model spawns, so the runner is replaced and counted
    rather than trusted to be unreachable.
    """
    original_runner = h.run_tree_kill
    original_prefix = h.claude_argv_prefix
    original_config_dir = os.environ.get('CLAUDE_CONFIG_DIR')
    spawned = []
    h.run_tree_kill = lambda *_a, **_k: spawned.append(1)
    h.claude_argv_prefix = lambda _c: [sys.executable]
    try:
        with tempfile.TemporaryDirectory() as td:
            os.environ['CLAUDE_CONFIG_DIR'] = os.path.join(td, 'h1-profile')
            os.makedirs(os.environ['CLAUDE_CONFIG_DIR'], exist_ok=True)
            yield td, spawned
    finally:
        h.run_tree_kill = original_runner
        h.claude_argv_prefix = original_prefix
        if original_config_dir is None:
            os.environ.pop('CLAUDE_CONFIG_DIR', None)
        else:
            os.environ['CLAUDE_CONFIG_DIR'] = original_config_dir


def _h1_drive_main(td, manifest_path, tag):
    """Run main() over `manifest_path` as a historical-v1 invocation with a zero-call
    budget. Returns (exit_code, status_or_None, output_exists).

    Pre-H1 the exception escapes main() instead of becoming a SystemExit, so on master
    this call RAISES rather than returning — which is precisely the defect, and is what
    makes every pin below red there.
    """
    out = os.path.join(td, '%s.out.json' % tag)
    status_path = os.path.join(td, '%s.status.json' % tag)
    code = None
    try:
        h.main([manifest_path, '--output', out, '--status-out', status_path,
                '--allow-historical-v1', '--claude-bin', sys.executable,
                '--call-reservation', os.path.join(td, '%s.calls.json' % tag),
                '--run-id', tag, '--max-calls', '0'])
    except SystemExit as exc:
        code = exc.code
    status = (json.load(open(status_path, encoding='utf-8'))
              if os.path.exists(status_path) else None)
    return code, status, os.path.exists(out)


def _h1_assert_configuration(code, status, produced_output, spawned, tag):
    if code != 2:
        raise AssertionError('%s: expected exit 2, got %r' % (tag, code))
    if status is None:
        raise AssertionError('%s: no status file was written' % tag)
    if status.get('classification') != 'configuration':
        raise AssertionError('%s: classification %r, expected configuration'
                             % (tag, status.get('classification')))
    if not (status.get('error') or '').strip():
        raise AssertionError('%s: status carries no error detail' % tag)
    if produced_output:
        raise AssertionError('%s: a result output was written for a configuration failure' % tag)
    if spawned:
        raise AssertionError('%s: %d model spawn(s) on a configuration failure'
                             % (tag, len(spawned)))


def test_h1_unreadable_manifest_is_configuration_status():
    """H1 (H1940) pin 1 of 4 — the manifest cannot be read at all.

    `open()`/`read()` sat outside main()'s try, so OSError escaped with no status file
    and the orchestrator retried a permanent defect. The hash must stay null: nothing was
    read, so nothing may be attested.
    """
    with _h1_worker_env() as (td, spawned):
        missing = os.path.join(td, 'does-not-exist.json')
        code, status, produced = _h1_drive_main(td, missing, 'missing')
        _h1_assert_configuration(code, status, produced, spawned, 'missing manifest')
        if 'manifest_sha256' not in status:
            raise AssertionError('status dropped the manifest_sha256 key entirely')
        if status['manifest_sha256'] is not None:
            raise AssertionError('a manifest that was never read was attested with hash %r'
                                 % status['manifest_sha256'])
    print('  H1 unreadable manifest: exit 2, configuration status, no output/spawn, '
          'hash null (not fabricated)')


def test_h1_invalid_json_manifest_keeps_real_byte_hash():
    """H1 (H1940) pin 2 of 4 — bytes read fine, JSON decoding fails.

    Distinct from pin 1: the bytes DID arrive, so their hash is real evidence of exactly
    what was rejected and must survive into the status unchanged. Expected hash is
    computed from the literal bytes written here, never from the code under test.
    """
    with _h1_worker_env() as (td, spawned):
        bad_bytes = b'{"schema": "pwg.headless_execution_manifest.v1", "meta": '
        bad_path = os.path.join(td, 'truncated.json')
        with open(bad_path, 'wb') as f:
            f.write(bad_bytes)
        expected = hashlib.sha256(bad_bytes).hexdigest()
        code, status, produced = _h1_drive_main(td, bad_path, 'badjson')
        _h1_assert_configuration(code, status, produced, spawned, 'invalid JSON manifest')
        if status.get('manifest_sha256') != expected:
            raise AssertionError('status hash %r != sha256 of the malformed bytes %r'
                                 % (status.get('manifest_sha256'), expected))
    print('  H1 invalid JSON: exit 2, configuration status, hash of the ACTUAL '
          'malformed bytes retained')


def test_h1_structural_key_error_is_configuration_status():
    """H1 (H1940) pin 3 of 4 — structurally malformed manifest raising KeyError.

    A manifest that decodes and passes `validate_manifest` can still be missing a section
    the executor subscripts directly: `build_prompt` does `manifest['inputs'][k]`. That
    KeyError was absent from the except tuple, so it escaped. It is raised while building
    the prompt — an argument to `HeadlessEngine.call` — so it precedes any reservation or
    spawn, which is why this pin can also assert zero calls.
    """
    with _h1_worker_env() as (td, spawned):
        broken = manifest()
        del broken['inputs']
        path = os.path.join(td, 'no-inputs.json')
        json.dump(broken, open(path, 'w', encoding='utf-8'))
        code, status, produced = _h1_drive_main(td, path, 'keyerror')
        _h1_assert_configuration(code, status, produced, spawned, 'KeyError manifest')
        if 'KeyError' not in (status.get('error') or ''):
            raise AssertionError('KeyError stringifies to a bare key; the status must name '
                                 'the type, got %r' % status.get('error'))
    print('  H1 structural KeyError: exit 2, configuration status, type named in the error')


def test_h1_structural_type_error_is_configuration_status():
    """H1 (H1940) pin 4 of 4 — structurally malformed manifest raising TypeError.

    `_validate_fragment_tm` iterates `for group in groups or []`; a scalar where the
    generator always emits a list makes that `for` a TypeError. It runs inside `execute`
    before the config-dir check, the profile claim and the engine, so this is the earliest
    of the four failures and likewise reaches no paid call.
    """
    with _h1_worker_env() as (td, spawned):
        broken = manifest()
        broken['fragment_tm'] = {'agni': 7}
        path = os.path.join(td, 'scalar-fragment-tm.json')
        json.dump(broken, open(path, 'w', encoding='utf-8'))
        code, status, produced = _h1_drive_main(td, path, 'typeerror')
        _h1_assert_configuration(code, status, produced, spawned, 'TypeError manifest')
        if 'TypeError' not in (status.get('error') or ''):
            raise AssertionError('TypeError stringifies without naming its type; the status '
                                 'must name it, got %r' % status.get('error'))
    print('  H1 structural TypeError: exit 2, configuration status, type named in the error')


def test_non_timeout_communicate_cleanup():
    original_popen = proc_tree.subprocess.Popen
    original_terminate = proc_tree.terminate_tree
    original_job = getattr(proc_tree, '_WindowsKillJob', None)
    seen = []

    class FakeProc:
        def __init__(self, *_a, **_k):
            self.returncode = None
            self._tree_job = None
            self._tree_setup_trouble = None
            self.calls = 0

        def communicate(self, **_kwargs):
            self.calls += 1
            if self.calls == 1:
                raise UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'synthetic')
            return '', ''

        def poll(self):
            return self.returncode

        def kill(self):
            self.returncode = -9

        def wait(self, timeout=None):
            self.returncode = -9
            return -9

    fake = [None]

    def popen(*args, **kwargs):
        fake[0] = FakeProc(*args, **kwargs)
        return fake[0]

    def terminate(proc, deadline):
        seen.append((proc, deadline))
        proc.returncode = -9
        return None

    proc_tree.subprocess.Popen = popen
    proc_tree.terminate_tree = terminate
    if original_job is not None:
        class FakeJob:
            def create(self): pass
            def assign(self, proc): pass
            def resume(self, proc): pass
            def close(self): return None
        proc_tree._WindowsKillJob = FakeJob
    try:
        try:
            proc_tree.run_tree_kill(['synthetic'], capture_output=True)
            raise AssertionError('communicate decode failure was swallowed')
        except UnicodeDecodeError:
            pass
        assert seen and fake[0].calls == 2 and fake[0].returncode == -9
    finally:
        proc_tree.subprocess.Popen = original_popen
        proc_tree.terminate_tree = original_terminate
        if original_job is not None:
            proc_tree._WindowsKillJob = original_job
    print('  process tree: non-timeout communicate exception terminates and reaps child tree')


def test_card_tokens_include_grammar():
    """R2/C-17: card_token_multiset counts {Tn} in record.grammar (not german-only), matching the
    JS cardTokens, so a grammar-{Tn} card is not falsely fragment-fidelity-rejected. Driven by the
    one card_fields.TOKEN_FIDELITY_FIELDS tuple the two twins share."""
    import card_fields as cf
    card = {'records': [{'grammar': '{T3} {T4}', 'senses': [{'german': '{T1} Feuer'}]}]}
    ms = dict(h.card_token_multiset(card))
    assert ms == {'{T1}': 1, '{T3}': 1, '{T4}': 1}, 'grammar tokens missing: %r' % ms
    assert ('record', 'grammar') in cf.TOKEN_FIDELITY_FIELDS and ('sense', 'german') in cf.TOKEN_FIDELITY_FIELDS
    print('  R2 tokens: card_token_multiset counts grammar+german via card_fields.TOKEN_FIDELITY_FIELDS')


def test_cost_telemetry_survives():
    """R5 (C-25): the CLI wrapper's usage/cost survive into summary['usage']:
      * a resolving call surfaces its usage/cost (schema-valid card, record `h` present — the test
        must not embed the C-02 missing-h defect);
      * multiple calls (retry/split/heal) SUM, never overwrite by the last response;
      * a measured call + a call missing usage -> known telemetry retained, cost_evaluable False,
        missing_usage_calls incremented, observed_cost_usd authoritative (accumulated, not recomputed);
      * a budget refusal (no subprocess) adds neither usage nor cost."""
    U = {'input_tokens': 100, 'output_tokens': 50,
         'cache_read_input_tokens': 10, 'cache_creation_input_tokens': 5}   # disjoint fields

    def wrap(cards, usage=U, cost=0.01):
        w = {'structured_output': {'cards': cards}}
        if usage is not None:
            w['usage'] = usage
        if cost is not None:
            w['total_cost_usd'] = cost
        return proc(stdout=json.dumps(w))

    def sequence(seq):
        def runner(argv, **k):
            runner.i += 1
            return seq[min(runner.i - 1, len(seq) - 1)]
        runner.i = 0
        return runner

    valid_card = {'key1': 'agni', 'iast': 'agni', 'notes': '',
                  'records': [{'h': '', 'grammar': '{T1} m.', 'senses': [
                      {'tag': '1', 'german': '{T1} Feuer', 'russian': '{T1} огонь'}]}]}

    # resolving call surfaces usage/cost (schema-valid card)
    payload = execute(manifest(), lambda argv, **k: wrap([valid_card], U, 0.0123))[0]
    assert payload['results'][0]['card'], 'schema-valid card should resolve'
    u = payload['summary']['usage']
    assert (u['input_tokens'], u['output_tokens'], u['cache_read_tokens'],
            u['cache_creation_tokens']) == (100, 50, 10, 5), u
    assert u['subagent_tokens'] == 165 and u['cost_evaluable'] is True and u['priced_calls'] == 1, u
    assert abs(u['observed_cost_usd'] - 0.0123) < 1e-9, u

    # (a) two calls SUM, not overwrite (empty cards -> retry to whole_attempts=2)
    u = execute(manifest(), sequence([wrap([], U, 0.01), wrap([], U, 0.02)]))[0]['summary']['usage']
    assert u['priced_calls'] == 2 and u['input_tokens'] == 200 and u['subagent_tokens'] == 330, u
    assert abs(u['observed_cost_usd'] - 0.03) < 1e-9 and u['cost_evaluable'] is True, u

    # (b) measured + missing-usage -> retain telemetry, cost_evaluable False, counter, authoritative cost
    u = execute(manifest(), sequence([wrap([], U, 0.01), wrap([], usage=None, cost=None)]))[0]['summary']['usage']
    assert u['input_tokens'] == 100 and u['subagent_tokens'] == 165, u
    assert u['cost_evaluable'] is False and u['missing_usage_calls'] == 1, u
    assert abs(u['observed_cost_usd'] - 0.01) < 1e-9, u

    # (c) a PAID, schema-malformed wrapper is still accounted before cards[] validation/retry.
    malformed = proc(stdout=json.dumps({
        'structured_output': {'not_cards': []}, 'usage': U, 'total_cost_usd': 0.25}))
    u = execute(manifest(), sequence([malformed, malformed]))[0]['summary']['usage']
    assert u['priced_calls'] == 2 and u['input_tokens'] == 200, u
    assert u['cost_evaluable'] is False and abs(u['observed_cost_usd'] - 0.50) < 1e-9, u

    # An unreadable envelope is also a spawned call; its unknown spend fails closed.
    unreadable = proc(stdout='not-json')
    u = execute(manifest(), sequence([unreadable, unreadable]))[0]['summary']['usage']
    assert u['priced_calls'] == 2 and u['missing_usage_calls'] == 2, u
    assert u['cost_evaluable'] is False, u

    # (d) a budget refusal (no subprocess) adds neither usage nor cost
    m = manifest(); m['budgets'] = {'max_translate_agents': 1}
    r = sequence([wrap([], U, 0.05)])
    u = execute(m, r)[0]['summary']['usage']
    assert r.i == 1, 'budget should cap to 1 actual spawn, got %d' % r.i
    assert u['priced_calls'] == 1 and u['input_tokens'] == 100, u
    assert abs(u['observed_cost_usd'] - 0.05) < 1e-9, u
    print('  R5 cost: every spawn accounted before result validation; malformed/missing fails closed')


def test_foreign_route_refused_before_any_call():
    """P-3: in the execution flow (validate_profile gates execute), a v2 manifest declaring a
    foreign route is refused BEFORE execute runs, so the injected model runner is NEVER invoked --
    not merely that validate_profile() raises in isolation."""
    import execution_contract as ec
    called = {'n': 0}
    def counting_runner(argv, **kwargs):
        called['n'] += 1
        return success_runner(argv, **kwargs)
    with tempfile.TemporaryDirectory() as cfgroot:
        cfg = os.path.join(cfgroot, 'p'); os.makedirs(cfg)
        m = manifest()
        m['schema'] = ec.SCHEMA_V2
        m['execution'] = {'profile_slot': 'c4',
                          'config_dir_fingerprint': ec.config_dir_fingerprint(cfg),
                          'execution_route': 'workflow', 'executor_lane': 'serial',
                          'validation_method': 'audit', 'model_identifier': m['model']}
        m['key_provenance'] = {'agni': 'real'}
        try:                       # replicate headless_worker.main()'s v2 order
            ec.validate_profile(m, cfg)
            h.execute(
                m, claude=sys.executable, runner=counting_runner,
                call_reservation=MemoryCallLedger(),
                config_dir=_FIXTURE_CONFIG_DIR)   # must NOT be reached
        except ValueError as e:
            assert 'execution_route' in str(e), e
        else:
            raise AssertionError('P-3: foreign route reached execute')
    assert called['n'] == 0, 'P-3: runner was called despite a foreign route'
    print('  P-3 route: foreign execution_route refused before any runner call (runner uncalled)')


def test_frag_tm_stitch_retains_owner():
    """R6 (C-02 residual): a warm frag-TM (v2) stitch restores each sense's (h, grammar) owner
    instead of a null owner, and heals a fully-cached fragment with ZERO model calls."""
    m = manifest()
    key = 'agni'
    sense = {'tag': '1', 'german': 'Feuer', 'russian': 'огонь'}   # already restored, no {Tn}
    m['fragment_groups'] = {key: [[{'skeleton': 'Feuer', 'fsha': 'FSHA0', 'si': 0}]]}
    m['fragment_placeholder_maps'] = {key: [[[]]]}
    m['fragment_tm'] = {key: [[{'senses': [sense], 'owners': [['2. agni', 'm.']]}]]}
    m['inputs'] = {key: {'skeleton': 'Feuer', 'portrait': '{}', 'ls': 0, 'sk': 0, 'nws': 0}}
    m['batches'] = []
    m['presplit_keys'] = [key]

    def never_runner(argv, **kwargs):
        raise AssertionError('R6: a fully-cached fragment must NOT call the model')

    payload, _status, _code = execute(m, never_runner)
    card = payload['results'][0]['card']
    assert card, 'a fully-cached fragment should stitch a card'
    rec = card['records'][0]
    assert rec.get('h') == '2. agni' and rec.get('grammar') == 'm.', rec   # owner restored, not null
    print('  R6 frag-TM: a v2-served warm stitch retains each sense owner (h/grammar), zero calls')


def test_null_owner_fragment_tm_refused_before_any_call():
    """R6 execution-time gate: a DIRECT manifest whose fragment_tm slot carries a null owner
    ([None,'m.'] / ['2. agni',None]) -- or is ownerless (legacy shape) -- is refused BEFORE any paid
    call, with the runner PROVEN uncalled. The generator's gview drops such rows, but a hand-edited /
    direct manifest bypasses it, so the executor validates every slot before stitching."""
    def never_runner(argv, **kwargs):
        raise AssertionError('runner was called despite a null/ownerless fragment_tm slot')
    sense = {'tag': '1', 'german': 'Feuer', 'russian': 'огонь'}

    def _mk(owners_or_missing):
        m = manifest()
        key = 'agni'
        slot = {'senses': [sense]}
        if owners_or_missing is not None:
            slot['owners'] = owners_or_missing
        m['fragment_groups'] = {key: [[{'skeleton': 'Feuer', 'fsha': 'F', 'si': 0}]]}
        m['fragment_placeholder_maps'] = {key: [[[]]]}
        m['fragment_tm'] = {key: [[slot]]}
        m['inputs'] = {key: {'skeleton': 'Feuer', 'portrait': '{}', 'ls': 0, 'sk': 0, 'nws': 0}}
        m['batches'] = []
        m['presplit_keys'] = [key]
        return m

    for bad in ([[None, 'm.']], [['2. agni', None]], None):   # null-h, null-grammar, ownerless
        try:
            execute(_mk(bad), never_runner)
        except ValueError as e:
            assert 'owner' in str(e).lower(), e
        else:
            raise AssertionError('a null/ownerless fragment_tm slot (%r) must be refused before any call' % bad)
    print('  R6 exec-gate: a direct manifest with a null/ownerless fragment_tm slot is refused before '
          'any call (runner uncalled)')


def test_normalize_batch_translation_fidelity_reject():
    """H1152 parity (C1): normalize_batch must reject a card whose `german` echo is faithful but
    whose TARGET field dropped an <ls>/{#..#} span. Was german-only (count_card), so a
    translation-column span drop reached the store on the headless production route (the
    live H1070 r102 pattern: german 33/33, english 32/33). A faithful card still passes."""
    m = manifest()   # inputs.agni ls=1 sk=0; placeholder_maps.agni=['<ls>RV.</ls>']; field=russian
    faithful = {'key1': 'agni', 'records': [{'grammar': '', 'senses': [
        {'tag': '1', 'german': '{T1} Feuer', 'russian': '{T1} огонь'}]}]}
    dropped = {'key1': 'agni', 'records': [{'grammar': '', 'senses': [
        {'tag': '1', 'german': '{T1} Feuer', 'russian': 'огонь'}]}]}   # <ls> kept in de, dropped in ru
    ok = h.normalize_batch(m, ['agni'], {'cards': [faithful]})
    assert ok[0].get('error') is None and ok[0]['card'], ok
    bad = h.normalize_batch(m, ['agni'], {'cards': [dropped]})
    assert bad[0].get('error') == 'translation-fidelity-reject' and bad[0]['card'] is None, bad
    print('  C1 normalize_batch: german-faithful but target-dropped card -> translation-fidelity-reject')


def test_normalize_batch_german_anchor_repair():
    """H858 Part B: a card whose `german` echo DROPPED a masked span is repaired from the source
    skeleton instead of nulled — the dominant retry-RESISTANT null class (6 of 7 residual nulls in
    no_pwg_w10, H1283: a requeue reproduces the drop, because it is a property of the echo, not of
    transport). Four properties, all on the REAL production route:

      1. the drop is repaired and the card survives, carrying the genuine restored span;
      2. the repair is STAMPED (`german_anchor`) — a machine-patched german is never
         indistinguishable in the store from one the model echoed correctly;
      3. a faithful card is byte-untouched and unstamped (the repair can only reach cards that
         were already being thrown away, so the clean yield cannot regress);
      4. a german that is NOT a pure drop (duplicate/foreign/reordered span) is refused repair
         and rejects exactly as before, with the refusal reason recorded for diagnosis.
    """
    m = manifest()   # inputs.agni skeleton='{T1} Feuer' ls=1 sk=0; PH=['<ls>RV.</ls>']
    def card(german, russian):
        return {'key1': 'agni', 'records': [{'grammar': '', 'senses': [
            {'tag': '1', 'german': german, 'russian': russian}]}]}

    repaired = h.normalize_batch(m, ['agni'], {'cards': [card('Feuer', '{T1} огонь')]})
    row = repaired[0]
    assert row.get('error') is None and row['card'], row
    assert row['card']['records'][0]['senses'][0]['german'] == '<ls>RV.</ls> Feuer', row['card']
    assert row['card']['german_anchor'] == {'reinjected': ['T1'], 'head': ['T1']}, row['card']

    clean = h.normalize_batch(m, ['agni'], {'cards': [card('{T1} Feuer', '{T1} огонь')]})
    assert clean[0].get('error') is None and clean[0]['card'], clean
    assert 'german_anchor' not in clean[0]['card'], clean[0]['card']

    # Not a pure drop -> refused, rejected, reason recorded (and never silently repaired).
    dup = h.normalize_batch(m, ['agni'], {'cards': [card('{T1} {T1} Feuer', '{T1} огонь')]})
    assert dup[0]['card'] is None and 'german-anchor duplicate-token' in dup[0].get('error', ''), dup

    # The repair must not launder a TRANSLATION-side drop (H1152 C1 still owns that class).
    ru_drop = h.normalize_batch(m, ['agni'], {'cards': [card('Feuer', 'огонь')]})
    assert ru_drop[0]['card'] is None, ru_drop
    assert ru_drop[0].get('error') == 'translation-fidelity-reject', ru_drop
    print('  H858 normalize_batch: dropped german span repaired+stamped; clean card untouched; '
          'non-drop refused; translation-side drop still rejected')


def test_headless_heal_stitch_translation_fidelity_reject():
    """H1152 parity (C1): the headless selfheal stitch (twin of the JS selfHeal check) must reject
    a COMPLETE stitched card whose german echo is faithful but whose TARGET field dropped a span.
    Driven via a warm frag-TM slot (already-restored senses), so no model call is made."""
    m = manifest()
    key = 'agni'
    sense = {'tag': '1', 'german': '<ls>RV.</ls> Feuer', 'russian': 'огонь'}   # de has <ls>, ru drops it
    m['fragment_groups'] = {key: [[{'skeleton': '<ls>RV.</ls> Feuer', 'fsha': 'FSHA0', 'si': 0}]]}
    m['fragment_placeholder_maps'] = {key: [[[]]]}
    m['fragment_tm'] = {key: [[{'senses': [sense], 'owners': [['2. agni', 'm.']]}]]}
    m['inputs'] = {key: {'skeleton': '<ls>RV.</ls> Feuer', 'portrait': '{}', 'ls': 1, 'sk': 0, 'nws': 0}}
    m['batches'] = []
    m['presplit_keys'] = [key]

    def never_runner(argv, **kwargs):
        raise AssertionError('a fully-cached fragment must NOT call the model')

    payload, _status, _code = execute(m, never_runner)
    assert payload['results'][0]['card'] is None, payload['results'][0]
    print('  C1 headless heal: german-faithful, target-dropped complete stitch -> rejected (card None)')


def _h2a_engine(test_manifest):
    """A bare HeadlessEngine for the H2a classification pins.

    `self_heal`'s zero-sense classification is pure bookkeeping over `self.failures` and
    `fragment_groups`, so the pins that need EXACT control of which fragment keys carry
    which error drive the engine directly instead of through a paid `execute()` run.
    """
    return h.HeadlessEngine(
        test_manifest, claude=sys.executable, timeout=1,
        runner=lambda argv, **kwargs: proc(
            stdout=json.dumps({'structured_output': {'cards': []}})),
        call_reservation=MemoryCallLedger(), config_dir=_FIXTURE_CONFIG_DIR)


def _h2a_presplit_manifest(key='agni', fragments=2, served_empty=False):
    m = manifest()
    m['batches'] = []
    m['presplit_keys'] = [key]
    m['meta'] = dict(m['meta'], selected_keys=[key])
    m['inputs'][key] = {'skeleton': '{T1}', 'portrait': '{}', 'ls': 1, 'sk': 0, 'nws': 0}
    m['placeholder_maps'][key] = ['<ls>A</ls>']
    m['fragment_groups'] = {key: [[{'skeleton': '{T1}', 'ls': 1, 'sk': 0,
                                    'fsha': 'f%d' % i, 'si': i + 1}
                                   for i in range(fragments)]]}
    m['fragment_placeholder_maps'] = {key: [[['<ls>A</ls>'] for _ in range(fragments)]]}
    # served_empty: every fragment is a WARM frag-TM slot carrying zero senses, so
    # self_heal reaches its zero-sense branch having spawned nothing at all. That lets a
    # pin drive the real `self_heal` (not just its private helper) with no paid-call
    # machinery, and with `failures` seeded to exactly the shape under test.
    m['fragment_tm'] = {key: [[{'senses': [], 'owners': []} for _ in range(fragments)]]
                        if served_empty else []}
    return m


def test_h2a_heal_budget_stop_is_not_a_content_defect():
    """H2a: a presplit base key whose OWN fragments hit the heal ceiling must report the
    typed `budget_exceeded:heal`, not `selfheal-nothing-resolved`.

    Before H2a the typed reason landed only on the fragment keys and the base key was
    stamped with the soft content-defect note, routing a transient infrastructure stop
    into the C-49 content lane. `preserve=True` could not save it: a presplit key runs no
    whole-card translate attempt, so there is no earlier base note to preserve.
    """
    m = _h2a_presplit_manifest()
    m['budgets'] = {'max_heal_agents': 0}      # every heal spawn refuses, typed
    r = _soft_nonresolve_runner()
    payload, status, code = execute(m, r)
    assert code == 0 and payload is not None, (code, status)
    failures = payload['summary']['failures']
    assert 'agni' in failures, failures
    err = failures['agni']
    assert 'budget_exceeded' in err, (
        'a heal-budget stop was reported as a content defect: failures[agni]=%r '
        '(budget_stops=%s)' % (err, payload['summary'].get('budget_stops')))
    assert err != 'selfheal-nothing-resolved', failures
    assert r.n == 0, 'a refused heal call must spawn nothing: %d' % r.n
    print('  H2a budget: presplit base failures[agni]=%r (was selfheal-nothing-resolved)' % err)


def test_h2a_fragment_key_match_is_exact_not_prefix():
    """H2a req 1: `ab_f` must not capture `ab_foo`.

    Fragment keys are `<key>_f<index>`, so `startswith('ab_f')` also matches `ab_foo_f0`
    — a different card's fragment. Here ONLY the foreign card's fragment carries a budget
    stop; the audited card's own fragment fails on content. A prefix-matching classifier
    steals the foreign reason and misreports this card as budget-stopped.
    """
    m = _h2a_presplit_manifest(key='ab', fragments=1, served_empty=True)
    m['fragment_groups']['ab_foo'] = [[{'skeleton': '{T1}', 'ls': 1, 'sk': 0,
                                        'fsha': 'x', 'si': 1}]]
    engine = _h2a_engine(m)
    engine.failures['ab_foo_f0'] = 'budget_exceeded:heal'     # a DIFFERENT card's stop
    engine.failures['ab_f0'] = 'fragment-fidelity-reject'     # this card: content defect

    assert engine._fragment_keys('ab') == {'ab_f0'}, engine._fragment_keys('ab')
    assert 'ab_foo_f0' not in engine._fragment_keys('ab'), (
        'ab_foo_f0 leaked into the exact fragment set for ab')
    assert engine.self_heal('ab') is None
    assert engine.failures['ab'] == 'selfheal-nothing-resolved', (
        "a prefix match stole ab_foo_f0's budget stop for card ab: %r"
        % engine.failures['ab'])
    print('  H2a exact: ab_foo_f0 ignored for base ab -> %r' % engine.failures['ab'])


def test_h2a_content_failure_without_budget_stop_unchanged():
    """H2a req 4: with no budget stop anywhere, the historical classification stands."""
    m = _h2a_presplit_manifest(key='agni', fragments=2, served_empty=True)
    engine = _h2a_engine(m)
    engine.failures['agni_f0'] = 'fragment-fidelity-reject'
    engine.failures['agni_f1'] = 'missing-or-mismatched-fragment-key'
    assert engine.self_heal('agni') is None
    assert engine.failures['agni'] == 'selfheal-nothing-resolved', engine.failures['agni']
    # ... and with no fragment failures recorded at all.
    engine2 = _h2a_engine(_h2a_presplit_manifest(key='agni', fragments=2,
                                                 served_empty=True))
    assert engine2.self_heal('agni') is None
    assert engine2.failures['agni'] == 'selfheal-nothing-resolved', engine2.failures['agni']
    print('  H2a unchanged: genuine zero-resolution still selfheal-nothing-resolved')


def test_h2a_precedence_is_deterministic_and_budget_stays_observable():
    """H2a req 5: mixed fragment errors resolve deterministically, budget stop observable.

    Fragments are examined in ascending NUMERIC index, so the answer cannot depend on set
    iteration order — and `_f10` must not be read before `_f2`.
    """
    m = _h2a_presplit_manifest(key='agni', fragments=12, served_empty=True)
    engine = _h2a_engine(m)
    engine.failures['agni_f0'] = 'fragment-fidelity-reject'
    engine.failures['agni_f2'] = 'budget_exceeded:heal'
    engine.failures['agni_f10'] = 'budget_exceeded:max_calls'
    assert engine.self_heal('agni') is None
    first = engine.failures['agni']
    assert first == 'budget_exceeded:heal', (
        'precedence must take the lowest-numbered budget stop (_f2 before _f10): %r' % first)
    for _ in range(25):                       # order-independence, not luck
        probe = _h2a_engine(_h2a_presplit_manifest(key='agni', fragments=12,
                                                   served_empty=True))
        probe.failures.update({'agni_f0': 'fragment-fidelity-reject',
                               'agni_f2': 'budget_exceeded:heal',
                               'agni_f10': 'budget_exceeded:max_calls'})
        probe.self_heal('agni')
        assert probe.failures['agni'] == first, probe.failures['agni']
    # A non-budget error on a LOWER index must not mask the budget stop.
    masked = _h2a_engine(_h2a_presplit_manifest(key='agni', fragments=12,
                                                served_empty=True))
    masked.failures.update({'agni_f1': 'timeout', 'agni_f2': 'budget_exceeded:heal'})
    masked.self_heal('agni')
    assert masked.failures['agni'] == 'budget_exceeded:heal', masked.failures['agni']
    # The typed reason also stays readable on the fragment key itself.
    assert masked.failures['agni_f2'] == 'budget_exceeded:heal'
    print('  H2a precedence: lowest-index budget stop wins deterministically (%r)' % first)


def h3_fsync_order_probe(write_call):
    """Run `write_call` with os.fsync/os.replace instrumented; return the ordered log.

    Each entry is ('fsync', size_of_that_fd) or ('replace', basename). `os.fstat` inside the
    fake fsync is the load-bearing part: it raises if the descriptor is already closed, so a
    pin built on this cannot pass against an implementation that fsyncs a stale fd. Shared by
    the three H3 pins (headless_worker / bounded_supervisor / cohort_engine)."""
    calls = []
    real_fsync, real_replace = os.fsync, os.replace

    def fake_fsync(fd):
        calls.append(('fsync', os.fstat(fd).st_size))
        return real_fsync(fd)

    def fake_replace(src, dst):
        calls.append(('replace', os.path.basename(dst)))
        return real_replace(src, dst)

    os.fsync, os.replace = fake_fsync, fake_replace
    try:
        write_call()
    finally:
        os.fsync, os.replace = real_fsync, real_replace
    return calls


def test_h3_atomic_json_fsyncs_before_replace():
    """H3 (H1940 Phase 2) — atomic_json must flush to DISK before the atomic rename.

    os.replace is atomic but not durable: pre-H3 a power loss between the write and the
    flush left a valid-looking truncated/empty status file, and the orchestrator re-audited
    the whole window. RED on master, where no fsync happens at all.

    Also pins that the fix is BYTE-IDENTICAL — the deliberate reason H3 landed inline
    instead of routing through window_common.atomic_write_json (which would have emitted
    CRLF and dropped the trailing newline; see src/pilot/h3_byte_probe.py).
    """
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'window_status.json')
        payload = {'schema': 'pwg.window_status.v1', 'cards': 3, 'unicode': 'ā ī ū'}
        calls = h3_fsync_order_probe(lambda: h.atomic_json(path, payload))

    kinds = [kind for kind, _ in calls]
    if kinds != ['fsync', 'replace']:
        raise AssertionError('expected exactly fsync-then-replace, got %r' % calls)
    if calls[0][1] <= 0:
        raise AssertionError('fsynced an empty descriptor: %r' % calls)

    # Re-write uninstrumented to assert the on-disk bytes are unchanged by H3.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'window_status.json')
        h.atomic_json(path, payload)
        raw = open(path, 'rb').read()
    if b'\r\n' in raw:
        raise AssertionError('atomic_json emitted CRLF — the newline pin was lost')
    if not raw.endswith(b'\n'):
        raise AssertionError('atomic_json lost its trailing newline')
    print('  H3: atomic_json fsyncs the live fd before os.replace; bytes unchanged '
          '(LF, trailing newline)')


def test_h2056_943_tree_kill_attaches_drained_output():
    """H2056 #943: run_tree_kill must ATTACH the output it drains from a tree-killed child.

    Before the fix it bound `out`/`err` to locals and bare-`raise`d, so the only copy of what the
    killed CLI said died with the frame — which is why every caller hardcoded 'timeout'. Pins that
    a 429 printed before the hang survives on the exception."""
    original_popen = proc_tree.subprocess.Popen
    original_terminate = proc_tree.terminate_tree
    original_job = getattr(proc_tree, '_WindowsKillJob', None)

    class FakeProc:
        def __init__(self, *_a, **_k):
            self.returncode = None
            self._tree_job = None
            self._tree_setup_trouble = None
            self.calls = 0

        def communicate(self, **_kwargs):
            self.calls += 1
            if self.calls == 1:                       # the call that blows the wall ceiling
                raise subprocess.TimeoutExpired('synthetic', 1)
            return 'partial stdout', 'Claude API error: 429 rate limit exceeded'

        def poll(self):
            return self.returncode

        def kill(self):
            self.returncode = -9

        def wait(self, timeout=None):
            self.returncode = -9
            return -9

    def popen(*args, **kwargs):
        return FakeProc(*args, **kwargs)

    def terminate(proc, deadline):
        proc.returncode = -9
        return None

    proc_tree.subprocess.Popen = popen
    proc_tree.terminate_tree = terminate
    if original_job is not None:
        class FakeJob:
            def create(self): pass
            def assign(self, proc): pass
            def resume(self, proc): pass
            def close(self): return None
        proc_tree._WindowsKillJob = FakeJob
    try:
        try:
            proc_tree.run_tree_kill(['synthetic'], capture_output=True, timeout=1)
            raise AssertionError('timeout was swallowed')
        except subprocess.TimeoutExpired as exc:
            assert exc.stdout == 'partial stdout', 'drained stdout not attached: %r' % (exc.stdout,)
            assert '429' in (exc.stderr or ''), 'drained stderr not attached: %r' % (exc.stderr,)
            # .stdout is TimeoutExpired's alias for .output — both must see it.
            assert exc.output == exc.stdout
            assert h.classify_timeout(exc) == ('rate_limit', h.EXIT_RATE_LIMIT)
    finally:
        proc_tree.subprocess.Popen = original_popen
        proc_tree.terminate_tree = original_terminate
        if original_job is not None:
            proc_tree._WindowsKillJob = original_job
    print('  H2056 #943: tree-kill attaches drained child output; a hung 429 is classifiable')


def test_h2056_944_hung_rate_limit_is_not_recorded_as_success():
    """H2056 #944: a rate-limited CLI hangs instead of returning 429 (FINDINGS §270).

    The hang must reach the SAME HardFailure path a non-hanging 429 takes — worker classification
    `rate_limit` + exit 21 — because that is what the orchestrator's is_rate_limited() reads to
    park the account. Before the fix the run continued, produced null cards and exited 0, so the
    job row was written `state='done', failure_class='success'` for a window that made nothing."""
    def hung_rate_limited_runner(argv, **kwargs):
        hung_rate_limited_runner.n += 1
        exc = subprocess.TimeoutExpired(argv, 180)
        exc.output = ''
        exc.stderr = 'Claude API error: 429 usage limit reached; resets at 2026-08-01T12:00:00Z'
        raise exc
    hung_rate_limited_runner.n = 0

    payload, status, code = execute(manifest(), hung_rate_limited_runner)
    assert code == h.EXIT_RATE_LIMIT, 'expected exit 21, got %r' % (code,)
    assert status['classification'] == 'rate_limit', status['classification']
    assert payload is None, 'a rate-limited run must not publish a result payload'
    assert hung_rate_limited_runner.n == 1, (
        'run continued spending against a locked account: %d spawns' % hung_rate_limited_runner.n)
    # The orchestrator gate that parks the account keys off exactly this field.
    import max_account_orchestrator as mao
    assert mao.is_rate_limited(status, ''), 'is_rate_limited() would not park this account'
    attempt = status['attempts'][-1]
    assert attempt['classification'] == 'rate_limit', attempt
    print('  H2056 #944: a hung 429 exits 21 as rate_limit, stops the run, and would park the account')


def test_h2056_944_plain_hang_still_classifies_as_timeout():
    """Regression guard for the #944 fix: only ACCOUNT-level causes are promoted.

    A genuine slow-call timeout — nothing said about 429/401 — must keep its historical 'timeout'
    classification and must NOT raise HardFailure, or every slow window would be misreported as a
    quota stall and parked. Also covers a runner that raises a bare TimeoutExpired with no attached
    output at all (older runners, stubs)."""
    for label, build in (
            ('silent hang', lambda argv: subprocess.TimeoutExpired(argv, 180)),
            ('chatty non-account hang', None)):
        def runner(argv, **kwargs):
            runner.n += 1
            if build is not None:
                raise build(argv)
            exc = subprocess.TimeoutExpired(argv, 180)
            exc.output = 'thinking...'
            exc.stderr = 'socket hang up'      # connection-ish, deliberately NOT promoted
            raise exc
        runner.n = 0
        payload, status, code = execute(manifest(), runner)
        assert code == 0, '%s: expected exit 0, got %r' % (label, code)
        assert status['classification'] != 'rate_limit', label
        assert runner.n >= 1
        assert all(a['classification'] == 'timeout' for a in status['attempts']), (
            '%s: %r' % (label, status['attempts']))
    print('  H2056 #944: a non-account hang stays a plain timeout (no false park)')


def main():
    payload, status, code = execute(manifest(), success_runner)
    assert code == 0 and status['classification'] == 'success'
    assert payload['results'][0]['card']['records'][0]['senses'][0]['german'].startswith('<ls>')
    assert payload['results'][0]['card']['records'][0]['grammar'].startswith('<ls>')
    assert payload['meta']['gen_model'] == 'claude-sonnet-5'

    def auth_runner(argv, **kwargs):
        return proc(1, stderr='API Error: 401 Invalid authentication credentials')
    assert execute(manifest(), auth_runner)[2] == h.EXIT_AUTH

    def rate_runner(argv, **kwargs):
        return proc(1, stderr='429 rate limit reset_at=1999999999')
    assert execute(manifest(), rate_runner)[2] == h.EXIT_RATE_LIMIT

    def malformed_runner(argv, **kwargs):
        return proc(stdout='not json')
    payload, status, code = execute(manifest(), malformed_runner)
    assert code == 0 and status['classification'] == 'completed_with_residuals'

    def missing_runner(argv, **kwargs):
        return proc(stdout=json.dumps({'structured_output': {'cards': []}}))
    payload, status, code = execute(manifest(), missing_runner)
    assert code == 0 and payload['summary']['null_keys'] == ['agni']

    def timeout_runner(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 1)
    payload, status, code = execute(manifest(), timeout_runner)
    assert code == 0 and payload['summary']['kill_timeouts'] == 1

    presplit = manifest()
    presplit['batches'] = []
    presplit['presplit_keys'] = ['agni']
    presplit['inputs']['agni'].update({'skeleton': '{T1}{T2}', 'ls': 2})
    presplit['fragment_groups'] = {'agni': [[
        {'skeleton': '{T1}', 'ls': 1, 'sk': 0, 'fsha': 'a', 'si': 1},
        {'skeleton': '{T1}', 'ls': 1, 'sk': 0, 'fsha': 'b', 'si': 2},
    ]]}
    presplit['fragment_placeholder_maps'] = {
        'agni': [[['<ls>A</ls>'], ['<ls>B</ls>']]]}
    presplit['placeholder_maps']['agni'] = ['<ls>A</ls>', '<ls>B</ls>']

    def fragment_runner(argv, **kwargs):
        cards = []
        for index in (0, 1):
            key = 'agni_f%d' % index
            if key in kwargs['input']:
                cards.append({'key1': key, 'records': [{'senses': [{
                    'tag': str(index + 1), 'german': '{T1}',
                    'russian': '{T1}'}]}]})
        return proc(stdout=json.dumps({'structured_output': {'cards': cards}}))

    payload, status, code = execute(presplit, fragment_runner)
    assert code == 0 and status['classification'] == 'success'
    card = payload['results'][0]['card']
    assert payload['summary']['presplit'] == 1 and payload['summary']['healed'] == 1
    assert not card.get('partial') and len(card['records'][0]['senses']) == 2

    calls = {'n': 0}
    def partial_runner(argv, **kwargs):
        calls['n'] += 1
        card = {'key1': 'agni_f0', 'records': [{'senses': [
            {'tag': '1', 'german': '{T1}', 'russian': '{T1}'}]}]}
        return proc(stdout=json.dumps({'structured_output': {'cards': [card]}}))
    payload, _status, code = execute(presplit, partial_runner)
    assert code == 0 and payload['results'][0]['card']['partial']
    assert payload['results'][0]['card']['missing_fragments']

    def fragment_timeout(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 1)
    payload, _status, code = execute(presplit, fragment_timeout)
    assert code == 0 and payload['summary']['null'] == 1
    assert payload['summary']['heal_agents_spent'] == 1  # timeout-no-bisect

    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, 'fixture.raw.txt')
        portrait = os.path.join(td, 'fixture.portrait.json')
        with open(raw, 'w', encoding='utf-8') as f:
            f.write('Feuer')
        with open(portrait, 'w', encoding='utf-8') as f:
            json.dump({'key1': 'agni'}, f)
        original = generator.input_paths
        generator.input_paths = lambda key: (raw, portrait)
        try:
            js, batches, built = generator.build(
                'fixture', ['agni'], None, 12000, nominal=True, grammar_on=False,
                tm_path=None, suggest_tm_path=None, return_manifest=True)
            js_v2, _batches_v2, built_v2 = generator.build(
                'fixture', ['agni'], None, 12000, nominal=True, grammar_on=False,
                tm_path=None, suggest_tm_path=None, return_manifest=True,
                profile_slot='c4', config_dir=td,
                execution_route='claude-cli-headless')
            try:
                generator.build(
                    'fixture', ['agni'], None, 12000, nominal=True, grammar_on=False,
                    tm_path=None, suggest_tm_path=None, return_manifest=True,
                    profile_slot='c4', config_dir=td,
                    execution_route='claude-workflow')
            except ValueError:
                pass
            else:
                raise AssertionError('profile-bound Workflow route was admitted')
        finally:
            generator.input_paths = original
        assert built['schema'] == 'pwg.headless_execution_manifest.v1'
        assert built['batches'] == batches and built['model'] == 'claude-sonnet-5'
        assert json.dumps(built['inputs'], ensure_ascii=True) in js
        assert built_v2['schema'] == 'pwg.headless_execution_manifest.v2'
        assert built_v2['meta']['execution_manifest_schema'] == built_v2['schema']
        assert "manifest-v2 production is CLI/headless-only" in js_v2
        start = js.index('function restoreCard(card, k)')
        end = js.index('// Per-card grammar', start)
        restore_card_js = js[start:end]
        # RESTORE_SPEC is injected from the same constant the harness interpolates (C-01), not
        # re-typed here: the whole point of the constant is that no second list exists. The
        # slice above starts at `function restoreCard`, so the const declared above it is not
        # carried in -- supply it exactly as the real harness would.
        import card_fields
        node_script = r"""
const PH = {agni: ['<lex>m.</lex>']}
const restore = (t, ph) => (t || '').replace(/\{T(\d+)\}/g, (_m, n) => ph[Number(n)-1])
const RESTORE_SPEC = %s
%s
const card = {iast: '{T1}', records: [{h: '{T1}', grammar: '{T1}', senses: [
  {tag: '{T1}', german: '{T1}', russian: '{T1}', differentia: '{T1}'}]}]}
console.log(JSON.stringify(restoreCard(card, 'agni')))
""" % (card_fields.js_restore_spec('russian'), restore_card_js)
        node = subprocess.run(['node', '-e', node_script], capture_output=True,
                              text=True, encoding='utf-8')
        assert node.returncode == 0, node.stderr
        restored = json.loads(node.stdout)
        rec = restored['records'][0]
        sense = rec['senses'][0]
        assert rec['grammar'] == '<lex>m.</lex>'
        assert sense['german'] == '<lex>m.</lex>'
        # C-01: the JS lane must unmask EVERY field the promote path reads, not just three.
        # card.iast / record.h / sense.tag / sense.differentia used to survive as raw {Tn} and
        # were promoted verbatim -- 670 store rows, 223 of them a {Tn} headword.
        for where, value in (('card.iast', restored['iast']), ('record.h', rec['h']),
                             ('sense.tag', sense['tag']),
                             ('sense.differentia', sense['differentia']),
                             ('sense.russian', sense['russian'])):
            assert value == '<lex>m.</lex>', '%s left unrestored by the JS lane: %r' % (where, value)

    # D-A (H818 Windows acceptance): the launcher resolver must bypass the Windows .cmd
    # batch shim (cmd.exe corrupts the --json-schema arg) and pass native/POSIX through.
    _name, _which, _glob = h.os.name, h.shutil.which, h.glob.glob
    try:
        h.os.name = 'posix'
        assert h.claude_argv_prefix('/usr/bin/claude') == ['/usr/bin/claude']
        h.os.name = 'nt'
        # Forward slashes are accepted by Windows and keep this simulated-nt branch
        # meaningful when the selftest itself runs with POSIX os.path semantics in CI.
        assert h.claude_argv_prefix('/p/claude.exe') == ['/p/claude.exe']
        h.shutil.which = lambda _n: '/node.exe'
        h.glob.glob = lambda pat: (['/p/node_modules/@anthropic-ai/claude-code/cli-wrapper.cjs']
                                   if 'cli*.cjs' in pat else [])
        assert h.claude_argv_prefix('/p/claude.cmd') == [
            '/node.exe', '/p/node_modules/@anthropic-ai/claude-code/cli-wrapper.cjs']
        h.shutil.which = lambda _n: None
        try:
            h.claude_argv_prefix('/p/claude.cmd')
        except FileNotFoundError:
            pass
        else:
            raise AssertionError('unresolved .cmd shim must fail closed')
    finally:
        h.os.name, h.shutil.which, h.glob.glob = _name, _which, _glob
    print('  D-A claude_argv_prefix: posix/.exe passthrough, .cmd->node-direct, unresolved shim refused')

    # D-J: a timeout must terminate the ENTIRE process tree, not just the immediate child. The
    # Windows claude launcher (node cli-wrapper.cjs) spawnSync's the native binary as a CHILD, so
    # killing only the node process orphans it (the multi-minute 'hang'). Mirror the real
    # python -> node(wrapper) -> native-binary depth with parent -> child -> GRANDCHILD: each level
    # records its PID and writes a '.done<n>' marker ONLY if it survives its sleep. A correct
    # tree-kill leaves NONE of the three PIDs alive and NONE of the three markers written.
    import time as _time

    def _alive(pid):
        if os.name == 'nt':
            out = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'],
                                  capture_output=True, text=True,
                                  creationflags=h.windows_hidden_flags()).stdout or ''   # no flicker
            return str(pid) in out.split()
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    with tempfile.TemporaryDirectory() as td:
        mk = os.path.join(td, 'm')
        grand = ('import time,sys,os;'
                 'open(sys.argv[1]+".pid3","w").write(str(os.getpid()));'
                 'time.sleep(6);open(sys.argv[1]+".done3","w").write("1")')
        child = ('import subprocess,sys,os,time;'
                 'open(sys.argv[1]+".pid2","w").write(str(os.getpid()));'
                 'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);'
                 'time.sleep(30)') % grand
        parent = ('import subprocess,sys,os,time;'
                  'open(sys.argv[1]+".pid1","w").write(str(os.getpid()));'
                  'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);'
                  'time.sleep(30)') % child
        t0 = _time.monotonic()
        try:
            h.run_tree_kill([sys.executable, '-c', parent, mk], timeout=3, capture_output=True)
            assert False, 'expected TimeoutExpired'
        except subprocess.TimeoutExpired:
            pass
        assert _time.monotonic() - t0 < 25, 'tree kill did not bound the timeout'
        for _ in range(60):     # wait for the full 3-level tree to have recorded its PIDs
            if all(os.path.exists('%s.pid%d' % (mk, i)) for i in (1, 2, 3)):
                break
            _time.sleep(0.1)
        _time.sleep(5)          # > the grandchild's 6 s sleep offset: an orphan would have written .done3
        for i in (1, 2, 3):
            assert os.path.exists('%s.pid%d' % (mk, i)), 'level %d never started (test setup broken)' % i
        pids = [int(open('%s.pid%d' % (mk, i)).read()) for i in (1, 2, 3)]
        survived_marker = [i for i in (1, 2, 3) if os.path.exists('%s.done%d' % (mk, i))]
        assert not survived_marker, 'level(s) %s SURVIVED the tree kill (orphaned)' % survived_marker
        still_alive = [p for p in pids if _alive(p)]
        assert not still_alive, 'tree PID(s) still alive after kill (orphaned): %s' % still_alive
    print('  D-J tree-kill: parent->child->grandchild all gone (no orphan); timeout bounded + raised once')
    test_translate_budget_binds()
    test_h1610_preserve_budget_exceeded_over_selfheal_stamp()
    test_h1610_refuse_max_agents_starves_multikey()
    test_h2b_translate_budget_preserves_attempt_content_note()
    test_call_timeout_clamped()
    test_durable_call_reservation()
    test_cli_reservation_and_preflight_gates()
    test_h1_unreadable_manifest_is_configuration_status()
    test_h1_invalid_json_manifest_keeps_real_byte_hash()
    test_h1_structural_key_error_is_configuration_status()
    test_h1_structural_type_error_is_configuration_status()
    test_non_timeout_communicate_cleanup()
    test_card_tokens_include_grammar()
    test_cost_telemetry_survives()
    test_foreign_route_refused_before_any_call()
    test_frag_tm_stitch_retains_owner()
    test_null_owner_fragment_tm_refused_before_any_call()
    test_normalize_batch_translation_fidelity_reject()
    test_normalize_batch_german_anchor_repair()
    test_headless_heal_stitch_translation_fidelity_reject()
    test_h2a_heal_budget_stop_is_not_a_content_defect()
    test_h2a_fragment_key_match_is_exact_not_prefix()
    test_h2a_content_failure_without_budget_stop_unchanged()
    test_h2a_precedence_is_deterministic_and_budget_stays_observable()
    test_h3_atomic_json_fsyncs_before_replace()
    test_h2056_943_tree_kill_attaches_drained_output()
    test_h2056_944_hung_rate_limit_is_not_recorded_as_success()
    test_h2056_944_plain_hang_still_classifies_as_timeout()
    print('headless_worker_selftest: PASS')


if __name__ == '__main__':
    main()
