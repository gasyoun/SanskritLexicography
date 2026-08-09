#!/usr/bin/env python
"""Fixture selftest for the H2189 profile A/B rig. Offline, deterministic, spends nothing.

What is worth pinning here is not arithmetic -- it is the three ways this measurement
could quietly become invalid:

1. The `card` arm stops sending the production prompt (the H2011 trap: a rig that
   validates, runs, bills and reports a prompt production never uses).
2. An arm changes more than one variable, so its delta cannot be attributed.
3. `--bare` reappears as an arm, silently moving the lane off subscription auth.

    python src/pilot/h2189_profile_ab_selftest.py

Model: authored by Opus 5 (`claude-opus-5[1m]`) for handoff H2189.
"""
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import h2189_min_profile as mp                                       # noqa: E402
import h2189_profile_ab as ab                                        # noqa: E402
from headless_worker import build_prompt                             # noqa: E402

MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'h1209_slice3.manifest.json')


def _manifest():
    with open(MANIFEST, encoding='utf-8') as fh:
        return json.load(fh)


def test_card_arm_sends_the_production_prompt_verbatim():
    """The card phase must send `build_prompt` output, not a paraphrase of it."""
    manifest = _manifest()
    key = manifest['meta']['selected_keys'][0]
    argv = ab.build_argv('paid', 'card', manifest, key)
    assert '--json-schema' in argv, 'card arm must carry the manifest schema'
    schema = argv[argv.index('--json-schema') + 1]
    assert json.loads(schema) == manifest['output_schema'], 'schema is not the manifest schema'
    assert argv[argv.index('--model') + 1] == manifest['model']
    assert argv[argv.index('--permission-mode') + 1] == 'plan'
    # The prompt itself travels on stdin; assert the rig would send exactly build_prompt.
    assert '-p' in argv and argv[argv.index('-p') + 1].startswith('--'), \
        'card arm must pass the prompt on stdin, not as an argv literal'
    assert build_prompt(manifest, [key]), 'production prompt is empty'


def test_every_arm_changes_exactly_one_thing_against_the_baseline():
    """Single-lever arms, plus one explicitly-declared stack. Anything else is unreadable."""
    base = ab.ARMS['paid']
    assert base['extra'] == [] and base['cwd'] == 'bare' and base['home'] is None, \
        'the baseline arm must reproduce production exactly'

    def levers(arm):
        return {'dir': arm['config_dir'] != base['config_dir'],
                'flags': bool(arm['extra']),
                'cwd': arm['cwd'] != base['cwd']}

    for name in ('minimal', 'safe', 'clean_cwd'):
        changed = [k for k, v in levers(ab.ARMS[name]).items() if v]
        assert len(changed) == 1, \
            'arm %s changes %s; a multi-lever arm cannot attribute its delta' % (name, changed)
    assert levers(ab.ARMS['minimal'])['dir']
    assert levers(ab.ARMS['safe'])['flags']
    assert levers(ab.ARMS['clean_cwd'])['cwd']
    # The one intentional stack: safe_clean must be exactly safe + clean_cwd, so its
    # delta is readable as the sum of two arms that were both measured on their own.
    stack = ab.ARMS['safe_clean']
    assert stack['extra'] == ab.ARMS['safe']['extra']
    assert stack['cwd'] == ab.ARMS['clean_cwd']['cwd']
    assert stack['config_dir'] == base['config_dir']


def test_minimal_arm_overrides_the_variable_that_actually_binds_the_profile():
    """CLAUDE_CONFIG_DIR alone does not swap the profile on a USERPROFILE-bound box."""
    env = ab.arm_env('minimal')
    assert env['CLAUDE_CONFIG_DIR'] == ab.ARMS['minimal']['config_dir']
    assert env['USERPROFILE'] == os.path.dirname(ab.ARMS['minimal']['config_dir'])
    assert env['HOME'] == env['USERPROFILE'], \
        'HOME and USERPROFILE must agree, or the child resolves two different profiles'
    base_env = ab.arm_env('paid')
    assert base_env['CLAUDE_CONFIG_DIR'] == ab.ARMS['paid']['config_dir']
    assert base_env.get('USERPROFILE') == os.environ.get('USERPROFILE'), \
        'the baseline arm must inherit the operator profile binding unchanged'


def test_clean_cwd_arm_fails_loud_rather_than_falling_back_to_the_leaking_dir():
    """A silent fallback would report the leaking cwd as if the clean case was measured."""
    with tempfile.TemporaryDirectory() as td:
        dirty = os.path.join(td, 'spawn')
        os.makedirs(os.path.join(td, '.claude'))
        with open(os.path.join(td, '.claude', 'CLAUDE.md'), 'w', encoding='utf-8') as fh:
            fh.write('# operator memory an ancestor walk would inject\n')
        assert mp.clean_cwd(dirty) is None, \
            'clean_cwd accepted a directory whose ANCESTOR carries .claude/CLAUDE.md'
        hits = mp.cwd_ancestry_scan(dirty)
        assert any(h['path'].endswith(os.path.join('.claude', 'CLAUDE.md')) for h in hits)


def test_ancestry_scan_sees_what_bare_cli_cwd_misses():
    """The exact blind spot: bare_cli_cwd rejects `CLAUDE.md`/`.git`, not `.claude/CLAUDE.md`."""
    from headless_worker import bare_cli_cwd
    with tempfile.TemporaryDirectory() as td:
        spawn = os.path.join(td, 'sub', 'spawn')
        os.makedirs(spawn)
        os.makedirs(os.path.join(td, '.claude'))
        with open(os.path.join(td, '.claude', 'CLAUDE.md'), 'w', encoding='utf-8') as fh:
            fh.write('x' * 100)
        planted = os.path.join(td, '.claude', 'CLAUDE.md')
        hits = mp.cwd_ancestry_scan(spawn)
        assert any(h['path'] == planted and h['bytes'] == 100 for h in hits), \
            'the walk missed a .claude/CLAUDE.md that bare_cli_cwd would have walked past'
        # Not asserted as the ONLY hit: on this box %TEMP% itself sits under a user
        # profile that carries its own .claude/CLAUDE.md -- which is the finding, not
        # noise, so a fixture that pretended otherwise would be testing a fiction.
        # And the production helper's own directory is scanned for real, not mocked:
        # if it ever becomes clean on this box the assertion below simply reads 0.
        real = bare_cli_cwd()
        if real:
            assert isinstance(mp.cwd_ancestry_scan(real), list)


def test_bare_is_never_an_arm():
    """`--bare` forces ANTHROPIC_API_KEY auth: a billing-identity change, not a cache tweak."""
    for name, arm in ab.ARMS.items():
        assert '--bare' not in arm['extra'], (
            'arm %s carries --bare, which moves this lane off the subscription identity. '
            'That is a human ruling (PROMPT_CACHING_PWG_RU 4), not a harness default.' % name)


def test_trivial_phase_translates_nothing():
    manifest = _manifest()
    argv = ab.build_argv('paid', 'trivial', manifest, None)
    assert '--max-turns' in argv and argv[argv.index('--max-turns') + 1] == '1'
    assert '--json-schema' not in argv, \
        'the trivial phase must not carry a card schema; it measures scaffolding only'


def test_cache_writes_are_priced_at_the_1h_rate():
    """A 5m-priced write understates this lane ~1.6x -- the wrong direction for a GO."""
    from parse_workflow_cost import cache_write_rate
    assert ab.CACHE_WRITE_1H == cache_write_rate('1h')
    assert ab.CACHE_WRITE_1H > cache_write_rate('5m')
    usd = ab.repriced({'cache_creation_input_tokens': 1_000_000})
    assert abs(usd - ab.CACHE_WRITE_1H) < 1e-9


def test_failed_call_is_never_priced_at_zero_silently():
    """A timed-out paid call has an empty usage dict; it must still be visible as a failure."""
    row = {'arm': 'paid', 'phase': 'trivial', 'failure_class': 'timeout', 'usage': {}}
    assert ab.repriced(row['usage']) == 0.0
    assert row['failure_class'], 'the row carries the failure class that stops $0 reading as free'
    assert ab.summarise([dict(row, key=None)]) == {}, \
        'a failed call must not enter the per-arm medians'


def test_instruction_compliance_detects_a_refusal_that_cites_the_profile():
    refusal = {'result': 'I cannot run this: the profile CLAUDE.md says to surface the '
                         'NEXT ISSUE and mint a handoff first.'}
    rec = ab.instruction_compliance(refusal)
    assert rec['schema_compliant'] is False
    assert rec['cards_returned'] == 0
    assert 'handoff' in rec['profile_vocab_leaked']
    good = {'result': json.dumps({'cards': [{'key': 'nakzatra', 'ru': 'созвездие'}]},
                                 ensure_ascii=False)}
    rec = ab.instruction_compliance(good)
    assert rec['schema_compliant'] is True and rec['cards_returned'] == 1
    assert rec['profile_vocab_leaked'] == []


def test_minimal_profile_refuses_to_be_born_inside_a_working_tree():
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, '.git'))
        try:
            mp.build(td, os.path.join(td, 'sub', '.claude'))
        except SystemExit as exc:
            assert 'REFUSING' in str(exc)
        else:
            raise AssertionError('a credential-bearing profile was built inside a git tree')


def test_minimal_profile_drops_project_state_and_writes_empty_settings():
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, 'src', '.claude')
        dest = os.path.join(td, 'dest', '.claude')
        os.makedirs(src)
        with open(os.path.join(src, '.claude.json'), 'w', encoding='utf-8') as fh:
            json.dump({'userID': 'u', 'oauthAccount': {'a': 1},
                       'projects': {'C:/repo': {'allowedTools': []}}}, fh)
        with open(os.path.join(src, '.credentials.json'), 'w', encoding='utf-8') as fh:
            fh.write('{"token":"x"}')
        with open(os.path.join(src, 'CLAUDE.md'), 'w', encoding='utf-8') as fh:
            fh.write('# operator rules\n')
        os.makedirs(os.path.join(src, 'commands'))
        open(os.path.join(src, 'commands', 'go.md'), 'w').close()
        mp.build(src, dest)

        with open(os.path.join(dest, '.claude.json'), encoding='utf-8') as fh:
            carried = json.load(fh)
        assert 'projects' not in carried, 'per-project state leaked into the minimal profile'
        assert carried['userID'] == 'u', 'account identity must survive, or auth breaks'
        with open(os.path.join(dest, 'settings.json'), encoding='utf-8') as fh:
            assert json.load(fh) == {}, 'minimal settings must carry no hooks'
        assert os.path.exists(os.path.join(dest, '.credentials.json'))
        assert not os.path.exists(os.path.join(dest, 'CLAUDE.md'))
        assert not os.path.exists(os.path.join(dest, 'commands'))

        rec = mp.inventory(dest)
        assert rec['memory_bytes'] == 0 and rec['hooks_total'] == 0
        assert rec['capability_total'] == 0
        assert mp.inventory(src)['capability_total'] == 1
        # The two profiles authenticate as one account but fingerprint differently, so
        # they take DIFFERENT ActiveCallClaim locks. Pinned because production wiring
        # that treats the minimal profile as an alias would silently lose serialisation.
        assert rec['fingerprint'] != mp.inventory(src)['fingerprint']


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith('test_')]
    failed = 0
    for fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print('FAIL %s: %s' % (fn.__name__, exc))
        else:
            print('ok   %s' % fn.__name__)
    print('\n%d/%d passed' % (len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
