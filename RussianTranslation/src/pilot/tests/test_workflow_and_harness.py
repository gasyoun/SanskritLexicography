"""test_workflow_and_harness — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_workflow_and_harness.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports
from _support import _h4054_synth_inputs  # noqa: F401  -- `import *` skips _names


def test_workflow_payload_nested():
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'outer': {'meta': {'root': 'sTA'}, 'results': [
            {'key': 'k1', 'card': {'ok': True}},
            {'key': 'k2', 'card': None},
        ]}}, f)
    try:
        _payload, meta, results, keys, nulls = workflow_payload(path)
    finally:
        os.remove(path)
    if meta.get('root') != 'sTA' or keys != ['k1', 'k2'] or nulls != ['k2']:
        fail('workflow_payload nested extraction failed')
    # H2089: null card must carry synthetic failure_REASON
    null_row = next(r for r in results if r.get('key') == 'k2')
    if null_row.get('failure_REASON') != 'null_card_no_card_object':
        fail('null card missing synthetic failure_REASON: %r' % null_row)



def test_workflow_payload_missing_results_hard_fail():
    """H2089: no results list must not become a clean empty window."""
    from workflow_payload import WorkflowPayloadError
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'meta': {'root': 'x'}, 'status': 'ok'}, f)
    try:
        try:
            workflow_payload(path)
            fail('missing results did not raise WorkflowPayloadError')
        except WorkflowPayloadError as exc:
            if 'silent-empty' not in str(exc) and 'no results' not in str(exc):
                fail('wrong error: %r' % exc)
        # opt-in soft path for diagnostics
        _p, _m, results, keys, nulls = workflow_payload(path, allow_missing_results=True)
        if results != [] or keys != [] or nulls != []:
            fail('allow_missing_results soft path not empty')
    finally:
        os.remove(path)



def test_harness_scope_and_tools():
    meta = harness_meta()  # canonical opt2 harness (window_common.OPT_HARNESS)
    if not meta.get('ok'):
        if meta.get('error') == 'missing harness':
            return  # ignored runtime artifact absent in a fresh worktree
        fail('optimized harness missing or invalid: %s' % meta.get('error'))
    text = open(meta['path'], encoding='utf-8').read()
    # Every schema-bearing model call must carry tools: [] (the yuj file-read-blowup guard).
    # Since the kill gate (H155 follow-up) the call sites go through agentKill(prompt, {..}),
    # not a bare agent(prompt, {..}); count both so the guard still holds whichever is used.
    agent_calls = text.count('agentKill(prompt, {') + text.count('agent(prompt, {')
    tool_guards = text.count('tools: []')
    if agent_calls != tool_guards or not tool_guards:
        fail('optimized harness tools guard mismatch: %d agent calls, %d guards' %
             (agent_calls, tool_guards))
    is_nominal = bool((meta.get('meta') or {}).get('nominal'))
    current = current_root_provenance(meta.get('root'), meta.get('selected_keys'),
                                      nominal=is_nominal)
    if not current.get('ok'):
        if 'no rootmap' in (current.get('error') or ''):
            return  # live ignored input/rootmap artifacts are absent in this checkout
        fail('current root provenance unavailable: %s' % current.get('error'))
    if not is_nominal and meta.get('rootmap_sha256') != current.get('rootmap_sha256'):
        fail('optimized harness rootmap hash does not match current rootmap')
    if is_nominal and meta.get('rootmap_sha256') is not None:
        fail('nominal optimized harness must not pretend to have a rootmap hash')
    if meta.get('selected_keys') != current.get('selected_keys'):
        fail('optimized harness selected_keys do not match current rootmap selection')



def test_stale_check_key_order_independent():
    """stale_check must compare workflow result-key order against meta.selected_keys as a
    SET, not a positional list — the harness assembles results TM-lane-first then
    DEGENERATE-lane then per-batch-completion order, which never matches the rootmap's
    declared order even when every key is present exactly once."""
    meta = harness_meta()
    if not meta.get('ok'):
        if meta.get('error') == 'missing harness':
            return  # ignored runtime artifact absent in a fresh worktree
        fail('optimized harness missing or invalid: %s' % meta.get('error'))
    root = meta.get('root')
    is_nominal = bool((meta.get('meta') or {}).get('nominal'))
    current = current_root_provenance(root, meta.get('selected_keys'), nominal=is_nominal)
    if not current.get('ok'):
        if 'no rootmap' in (current.get('error') or ''):
            return  # live ignored input/rootmap artifacts are absent in this checkout
        fail('current root provenance unavailable: %s' % current.get('error'))
    workflow_meta = {
        'root': root,
        'safe_root': current['safe_root'],
        'rootmap_sha256': current['rootmap_sha256'],
        'selected_keys': current['selected_keys'],
        'input_hashes': current['input_hashes'],
        'nominal': is_nominal,
    }
    reordered_keys = list(reversed(current['selected_keys']))
    check = stale_check(root, workflow_meta, reordered_keys)
    if any('do not match' in err for err in check.get('errors') or []):
        fail('stale_check flagged reordered-but-identical key set as a mismatch')
    if check['stale']:
        fail('stale_check treated an order-only difference as stale: %s' % check.get('errors'))



def test_nominal_provenance_without_rootmap():
    """Nominal windows use selected headword keys directly; lack of a rootmap is expected."""
    import gen_opt_harness2 as gh
    from window_common import input_paths
    keys = ['_selftest_nominal_prov']
    rp, pp = input_paths(keys[0])
    old_raw = open(rp, encoding='utf-8').read() if os.path.exists(rp) else None
    old_portrait = open(pp, encoding='utf-8').read() if os.path.exists(pp) else None
    try:
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('<L>1<pc>1<k1>a<k2>a<h>1\n<body>{#a#} x</body>\n')
        with open(pp, 'w', encoding='utf-8') as f:
            json.dump({'key1': 'a', 'lex': 'm.'}, f)
        current = current_root_provenance('nominal_selftest', keys, nominal=True)
        if not current.get('ok') or current.get('rootmap_sha256') is not None:
            fail('nominal provenance must succeed without a rootmap')
        workflow_meta = {
            'root': 'nominal_selftest',
            'safe_root': current['safe_root'],
            'rootmap_sha256': None,
            'selected_keys': keys,
            'input_hashes': current['input_hashes'],
            'nominal': True,
        }
        check = stale_check('nominal_selftest', workflow_meta, list(reversed(keys)))
        if check['stale']:
            fail('nominal stale_check must not require a rootmap: %s' % check.get('errors'))
        manifest = {'schema': 'pwg.headless_execution_manifest.v1',
                    'meta': dict(workflow_meta)}
        check = stale_check(None, workflow_meta, keys, execution_manifest=manifest)
        if check['stale']:
            fail('manifest-bound nominal provenance must pass without a rootmap: %s'
                 % check.get('errors'))
        duplicate = stale_check(
            None, workflow_meta, keys + keys, execution_manifest=manifest)
        if not duplicate['stale'] or duplicate.get('duplicate_keys') != {keys[0]: 2}:
            fail('manifest provenance must reject duplicate result keys exactly')
        missing = stale_check(None, workflow_meta, [], execution_manifest=manifest)
        if not missing['stale'] or keys[0] not in (missing.get('missing_keys') or []):
            fail('manifest provenance must reject missing result keys')
        foreign = stale_check(
            None, workflow_meta, keys + ['foreign'], execution_manifest=manifest)
        if not foreign['stale'] or 'foreign' not in (foreign.get('unexpected_keys') or []):
            fail('manifest provenance must reject foreign result keys')
        wrong_root_meta = dict(workflow_meta, root='wrong')
        wrong_root = stale_check(
            None, wrong_root_meta, keys, execution_manifest=manifest)
        if not wrong_root['stale'] or not any(
                'execution manifest root' in err for err in wrong_root.get('errors') or []):
            fail('manifest provenance must reject workflow root drift')
        drifted_manifest = {'schema': manifest['schema'],
                            'meta': json.loads(json.dumps(workflow_meta))}
        drifted_manifest['meta']['input_hashes'][keys[0]]['raw_sha256'] = 'drift'
        hash_drift = stale_check(
            None, workflow_meta, keys, execution_manifest=drifted_manifest)
        if not hash_drift['stale'] or not any(
                'input hashes' in err for err in hash_drift.get('errors') or []):
            fail('manifest provenance must reject input-hash drift')
    finally:
        for path, old in ((rp, old_raw), (pp, old_portrait)):
            if old is None:
                try:
                    os.remove(path)
                except OSError:
                    pass
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(old)



def test_release_manifest_hash_validation():
    with tempfile.TemporaryDirectory() as tmp:
        edition = os.path.join(tmp, 'edition_selftest')
        write_minimal_edition(edition)
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=0)
        with open(os.path.join(edition, 'reverse_index.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({'ru': 'дым', 'key1': 'dhUma'}, ensure_ascii=False) + '\n')
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=1)



def test_generated_harness_strict_key_matching():
    """Generated JS must not positionally assign a returned full card to another key."""
    import gen_opt_harness2 as gh
    raw = '<L>1<pc>1<k1>a<k2>a<h>1\n{#a#}¦ {%eins%}.\n'
    d = tempfile.mkdtemp()
    keys = ['zz_key_a', 'zz_key_b']
    saved_ip = gh.input_paths
    try:
        for k in keys:
            with open(os.path.join(d, k + '.raw.txt'), 'w', encoding='utf-8') as f:
                f.write(raw)
            with open(os.path.join(d, k + '.portrait.json'), 'w', encoding='utf-8') as f:
                f.write('{}')
        gh.input_paths = lambda k, input_dir=None: (
            os.path.join(d, k + '.raw.txt'), os.path.join(d, k + '.portrait.json'))
        js, _batches = gh.build('zz', keys, None, 12000, nominal=True,
                                grammar_on=False, tm_path=None)
        # km[k] (the exact expected key) is always the PRIMARY match. H220 added a
        # nominal-only SLP1-echo fallback (re-key via nominal_keymap), so the binding is
        # `let cand = km[k]` now — still key-based, never positional.
        if 'let cand = km[k]' not in js:
            fail('full-card lane must use strict key lookup (km[k]), not positional fallback')
        if 'res.cards[i]' in js or 'res.cards[idx], fi' in js:
            fail('generated harness still has unsafe positional response assignment')
        if 'missing-or-mismatched-key' not in js:
            fail('missing/mismatched full-card keys must get an explicit failure reason')
        if 'missing-or-mismatched-fragment-key' not in js:
            fail('missing/mismatched fragment keys must get an explicit failure reason')
    finally:
        gh.input_paths = saved_ip
        shutil.rmtree(d, ignore_errors=True)



def test_build_emits_nominal_keymap():
    """Producer-side twin of test_promote_nominal_key1: build(nominal=True) MUST emit
    meta.nominal + meta.nominal_keymap. Without them promote_final_cards.rows_for falls
    back to meta.root (the window LABEL, e.g. pril10_w1) and mis-keys every nominal card.
    The consumer test hand-builds its meta, so it cannot catch build() dropping the fields;
    this test does (guards PR #155 against a silent regression)."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import input_paths
    key = 'ab'
    rp, pp = input_paths(key)
    if not (os.path.exists(rp) and os.path.exists(pp)):
        return  # fixture-gated, same as the sibling nominal build() tests
    js, _batches = gh.build(key, [key], None, 12000, nominal=True, tm_path=None)
    meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
    if meta.get('nominal') is not True:
        fail('build(nominal=True) must set meta.nominal=True (else promote falls back to the window label)')
    keymap = meta.get('nominal_keymap')
    if not isinstance(keymap, dict) or key not in keymap:
        fail('build(nominal=True) must emit meta.nominal_keymap mapping each safe key to its SLP1 headword')
    slp1 = gh._slp1_lex_for_key(key)[0] or key
    if keymap[key] != slp1:
        fail('nominal_keymap must map the safe key to the portrait SLP1 (%r), got %r' % (slp1, keymap[key]))
    # Negative: a non-nominal (batched) build must NOT carry the nominal routing fields.
    js2, _b2 = gh.build(key, [key], None, 12000, nominal=False, tm_path=None)
    meta2 = json.loads(_re.search(r'const META = (\{.*?\})\n', js2, _re.S).group(1))
    if meta2.get('nominal'):
        fail('batched (non-nominal) build must not set meta.nominal')
    if meta2.get('nominal_keymap') is not None:
        fail('batched (non-nominal) build must leave meta.nominal_keymap null')



def test_generation_schema_carries_no_post_generation_field():
    """H428: the per-call StructuredOutput schema (build()'s batch_schema) must never carry
    a field that a deterministic annotator adds AFTER generation (government, labels, renou,
    renou_oldest, evidence, evidence_summary, stats, renou_oldest_sense) -- those fields
    pushed the full reachable schema to 10,940 chars, over the Workflow tool's safety-
    classifier size threshold, blocking every agent() call pre-generation at 0 tokens
    (Uprava/FINDINGS.md §30). Pins the fix so a future annotator field added to
    schemas/pwg_ru_final_card.schema.json cannot silently regress this without also being
    added to _POST_GENERATION_*_FIELDS."""
    import gen_opt_harness2 as gh
    schema = gh.load_json(os.path.join(gh.REPO, 'schemas', 'pwg_ru_final_card.schema.json'))
    schema['$defs']['sense']['required'] = ['tag', 'german', 'russian']
    defs = gh._strip_post_generation_fields(schema['$defs'])
    reachable = gh._reachable_defs(defs, 'card')
    banned = (gh._POST_GENERATION_CARD_FIELDS + gh._POST_GENERATION_RECORD_FIELDS
              + gh._POST_GENERATION_SENSE_FIELDS)
    for def_name in ('card', 'record', 'sense'):
        props = reachable.get(def_name, {}).get('properties', {})
        for f in banned:
            if f in props:
                fail('generation schema $defs[%r] still carries post-generation field %r' % (def_name, f))
    # evidence_item/evidence_summary/stats become unreachable once sense.evidence and
    # card.evidence_summary/stats are stripped -- pin that they actually drop out, since a
    # dangling $defs entry is exactly the H130 orphan-defs dead weight this fix removes.
    for orphan in ('evidence_item', 'evidence_summary', 'stats'):
        if orphan in reachable:
            fail('%r should be unreachable from card once post-generation fields are stripped' % orphan)
    size = len(json.dumps({
        'type': 'object', 'additionalProperties': False, 'required': ['cards'],
        'properties': {'cards': {'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/card'}}},
        '$defs': reachable,
    }))
    if size > 5000:
        fail('slimmed generation schema grew to %d chars (was 1,698 at H428) -- '
             're-measure against the Workflow tool safety-classifier threshold' % size)



def test_nominals_worklist_exposes_no_pwg_lane():
    import nominals_worklist as nw
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        wordlist = os.path.join(tmp, 'sample.slp1.txt')
        manifest = os.path.join(tmp, 'scale_manifest.freq.json')
        store = os.path.join(tmp, 'store.jsonl')
        with open(wordlist, 'w', encoding='utf-8') as f:
            f.write('Bagavat\nAkulita\nnotalocalword\n')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump([
                {'key1': 'Bagavat', 'score': 3, 'band': 1},
                {'key1': 'Akulita', 'score': 2, 'band': 1},
                {'key1': 'notalocalword', 'score': 1, 'band': 1},
            ], f)
        open(store, 'w', encoding='utf-8').close()
        payload = nw.build_worklist(wordlist, manifest=manifest, store=store)
    got = set(payload.get('no_pwg_runnable') or [])
    if not {'Bagavat', 'Akulita'}.issubset(got):
        fail('PW/SCH-only misses must enter no_pwg_runnable, got %s' % sorted(got))
    if 'notalocalword' not in payload.get('true_miss_keys', []):
        fail('true misses must remain misses, not no-PWG runnable')
    for field in ('no_pwg_runnable_count', 'no_pwg_promoted_count', 'no_pwg_runnable_detail'):
        if field not in payload:
            fail('nominals_worklist payload missing %s' % field)
    if any(k in payload.get('runnable_remaining', []) for k in got):
        fail('no-PWG runnable keys must stay separate from PWG-rooted runnable_remaining')



def test_calibration_arm_set_conservative_emit_only():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = os.path.join(tmp, 'perf_smoke_preflight')
        proc = run([sys.executable, 'src/pilot/calibrate_perf_harness.py', 'gam',
                    '--keys=gam~~h0_03_sec_3', '--arm-set', 'conservative',
                    '--emit-only', '--out-dir=%s' % out_dir], 0)
        manifest_path = os.path.join(out_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            fail('calibration emit-only must write manifest.json')
        manifest = json.load(open(manifest_path, encoding='utf-8'))
        arms = {(a['output_budget'], a['selfheal_budget'], a['tm_mode'])
                for a in manifest.get('arms', [])}
        expected = {(90, 12, 'auto'), (90, 12, 'off'), (110, 12, 'auto'), (110, 12, 'off')}
        if arms != expected:
            fail('conservative arm set mismatch: %s' % sorted(arms))
        if 'cache cooldown' not in manifest.get('cache_warning', ''):
            fail('calibration manifest must keep the cache-cooldown warning')
        if any(name.endswith('.js') for name in os.listdir(out_dir)):
            fail('emit-only calibration must not generate harness JS files')
        if 'cache cooldown' not in proc.stdout:
            fail('calibration CLI must print the cache-cooldown warning')



def test_default_call_shape_is_one_card_per_call():
    """H4054: the NO-FLAG production preparation must emit ONE ORIGINAL CARD PER TRANSLATE
    CALL. The ruled shape (H2152, 02-08-2026; RUN_FREQ_MAX § call shape; AGENTS.md one-card
    policy) used to live only in whoever typed the command while the generator default was
    OUTPUT_BUDGET=90 — the structural default is now 1. Proves (a) the module default is
    literally 1 on a fresh import, (b) a default-budget multi-key build produces exactly one
    card per batch, and (c) the explicit experiment lane still packs: --output-budget=90
    puts the same small cards into ONE batch."""
    import gen_opt_harness2 as gh
    d = tempfile.mkdtemp()
    keys = ['a~~h0_zz_pw', 'b~~h0_zz_pw', 'c~~h0_zz_pw']
    saved_ob = gh.OUTPUT_BUDGET
    saved_ip = gh.input_paths
    try:
        # (a) structural default, proven outside this process (monkeypatch-proof).
        out = subprocess.run(
            [sys.executable, '-c', 'import gen_opt_harness2 as g; print(g.OUTPUT_BUDGET)'],
            cwd=os.path.dirname(os.path.abspath(gh.__file__)),
            capture_output=True, text=True, encoding='utf-8')
        if out.returncode or out.stdout.strip() != '1':
            fail('fresh-import gen_opt_harness2.OUTPUT_BUDGET must be 1 (one card per call); '
                 'got rc=%s stdout=%r stderr=%r' % (out.returncode, out.stdout, out.stderr))
        if gh.OUTPUT_BUDGET != 1:
            fail('in-process OUTPUT_BUDGET is %r, not the import default 1' % (gh.OUTPUT_BUDGET,))
        gh.input_paths = _h4054_synth_inputs(gh, d, list(zip(keys, (2, 0, 5))))
        # (b) no-flag build: one original card per batch.
        js, batches, manifest = gh.build('zz', keys, None, 12000, nominal=True,
                                         grammar_on=False, tm_path=None, return_manifest=True)
        meta = manifest['meta']
        if meta.get('output_budget') != 1:
            fail('meta.output_budget must record the structural default 1; got %r'
                 % (meta.get('output_budget'),))
        owed = [k for b in batches for k in b]
        if sorted(owed) != sorted(keys):
            fail('every original card must stay owed by the batch lane; got %r' % (batches,))
        if any(len(b) != 1 for b in batches):
            fail('no-flag production preparation must emit ONE card per translate call; '
                 'got batches=%r' % (batches,))
        if meta.get('batch_count') != len(keys):
            fail('batch_count must equal the card count under the one-card default; got %r'
                 % (meta.get('batch_count'),))
        if meta.get('presplit_keys'):
            fail('small cards (max 5 <ls>) must NOT presplit under the default '
                 '(PRESPLIT_SOLO_CITE_FLOOR governs, not the batch budget); got %r'
                 % (meta['presplit_keys'],))
        # (c) explicit experiment batching still packs the same small cards.
        gh.OUTPUT_BUDGET = 90
        js2, batches2, manifest2 = gh.build('zz', keys, None, 12000, nominal=True,
                                            grammar_on=False, tm_path=None, return_manifest=True)
        if manifest2['meta'].get('output_budget') != 90:
            fail('explicit --output-budget=90 must be honoured verbatim; got %r'
                 % (manifest2['meta'].get('output_budget'),))
        if not any(len(b) > 1 for b in batches2):
            fail('explicit batching must pack >1 small card per batch; got %r' % (batches2,))
        if sorted(k for b in batches2 for k in b) != sorted(keys):
            fail('explicit batching must still owe every card; got %r' % (batches2,))
    finally:
        gh.input_paths = saved_ip
        gh.OUTPUT_BUDGET = saved_ob
        shutil.rmtree(d, ignore_errors=True)



def test_harness_size_guard():
    """H189 / F-harness-size-limit: the generator must surface an oversize harness at
    generation with a concrete key-disjoint split, so the Workflow scriptPath cap is not
    discovered at launch (pril10_w1: 1.03 MB, unlaunchable). Small harness -> no split."""
    import gen_opt_harness2 as gh
    keys = ['k%d' % i for i in range(9)]
    over, lines = gh.harness_size_report('kAla', keys, True, 1_030_000, 480_000)
    if not over or not lines:
        fail('a 1.03 MB harness over the 480 KB cap must report oversize with a split')
    split_cmds = [ln for ln in lines if '--keys=' in ln]
    if len(split_cmds) < 2:
        fail('oversize report must suggest >=2 key-disjoint sub-windows; got %d' % len(split_cmds))
    # every original key must appear in exactly one sub-window (disjoint, complete)
    seen = []
    for ln in split_cmds:
        seen += ln.split('--keys=')[1].split(' --out=')[0].split(',')
    if sorted(seen) != sorted(keys):
        fail('the suggested split must partition the keys exactly once each; got %r' % seen)
    under, lines2 = gh.harness_size_report('kAla', keys, True, 100_000, 480_000)
    if under or lines2:
        fail('a harness under the cap must not report oversize')



def test_h2591_prep_context_compare_matrix():
    """H2591: the baseline-vs-PREP comparison driver's hermetic matrix, in-window.

    The driver spends real Claude calls, so every fence it enforces has to be provable
    without one. `prep_context_compare_selftest.py` drives it through an injected caller
    across prompt identity, context-hash replay, the TM fence, reservation exhaustion,
    crash/resume, model substitution, missing usage, exact-once finalization and the
    receipt's GO/NO-GO/INCONCLUSIVE arithmetic. Running it here means a later change to
    `build_prompt`, `prep_pack.compact_context` or `call_reservation` that silently breaks
    the qualification rig goes red in the full window, not on the money contour.
    """
    sys.path.insert(0, os.path.join(HERE, 'h1210'))
    import prep_context_compare_selftest as pcc_selftest
    if pcc_selftest.selftest() != 0:
        fail('H2591 prep_context_compare hermetic matrix failed')



def test_h2245_canary_manifest_builder():
    """H2245: the canary manifest builder's output shape is PINNED, offline.

    `canary_manifest_build.py` (H2174) made the canary re-runnable, but nothing pinned what
    it emits — and the canary's diagnostic value lives entirely in properties a schema change
    could rot silently (ls==0/sk==0 with 3 senses; provenance synthetic_control; a
    live-computed config_dir_fingerprint). Note `validate_manifest` alone does NOT catch a
    provenance flip to `real` — 'real' is a legal class — so that guard has to live here.

    Delegated to the sibling selftest, which builds against a scratch profile dir and diffs
    the result against the committed golden artifact. Spends nothing.
    """
    import canary_manifest_build_selftest
    canary_manifest_build_selftest.selftest()

