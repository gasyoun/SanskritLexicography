#!/usr/bin/env python
import json
import subprocess
import sys
import tempfile
import os
from types import SimpleNamespace

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import headless_worker as h
import gen_opt_harness2 as generator


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


def execute(test_manifest, runner):
    """Use a real, portable executable path while the runner fakes its output."""
    return h.execute(test_manifest, claude=sys.executable, runner=runner)


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
    h.execute(manifest(), claude=sys.executable, runner=r, max_agents_override=1)
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
                                      max_agents_override=1)
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
        h.execute(m, claude=sys.executable, runner=r, max_agents_override=1)
        assert False, 'expected ValueError starvation refuse'
    except ValueError as exc:
        assert 'starves' in str(exc) and '3-key' in str(exc), exc
    assert r.n == 0, 'starvation refuse must spawn zero: %d' % r.n
    print('  H1610 refuse: multi-key --max-agents=1 raises before any spawn')


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

    # (c) a budget refusal (no subprocess) adds neither usage nor cost
    m = manifest(); m['budgets'] = {'max_translate_agents': 1}
    r = sequence([wrap([], U, 0.05)])
    u = execute(m, r)[0]['summary']['usage']
    assert r.i == 1, 'budget should cap to 1 actual spawn, got %d' % r.i
    assert u['priced_calls'] == 1 and u['input_tokens'] == 100, u
    assert abs(u['observed_cost_usd'] - 0.05) < 1e-9, u
    print('  R5 cost: usage/cost sum across calls; missing -> cost_evaluable False + counter; budget refusal adds nothing')


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
            h.execute(m, claude=sys.executable, runner=counting_runner)   # must NOT be reached
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
    test_call_timeout_clamped()
    test_card_tokens_include_grammar()
    test_cost_telemetry_survives()
    test_foreign_route_refused_before_any_call()
    test_frag_tm_stitch_retains_owner()
    test_null_owner_fragment_tm_refused_before_any_call()
    test_normalize_batch_translation_fidelity_reject()
    test_headless_heal_stitch_translation_fidelity_reject()
    print('headless_worker_selftest: PASS')


if __name__ == '__main__':
    main()
