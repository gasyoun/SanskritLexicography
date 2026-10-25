"""test_no_pwg_lane — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_no_pwg_lane.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_no_pwg_card_source_profile_taxonomy():
    """H214: the per-card source-material classifier. The portrait's explicit no-PWG flag wins,
    so a root-split supplement sub-card (empty portrait) is NOT mis-tagged as no-PWG; and the
    supplement PW matcher must not fire on 'PWG'."""
    import gen_opt_harness2 as gh
    no_pwg_portrait = json.dumps([{'portrait_kind': 'no_pwg_supplement_chain',
                                   'source_profile': 'no_pwg_supplement_chain', 'key1': 'k'}])
    cases = [
        ('=== LAYER: PW — Böhtlingk ===\n\nfoo', no_pwg_portrait, 'no_pwg_supplement_chain'),
        ('=== LAYER: PW — Böhtlingk ===\n\nfoo', '[]', 'pwg_supplement_subcard'),
        ('=== LAYER: NWS — Halle ===\n\nfoo', '[]', 'pwg_supplement_subcard'),
        ('=== LAYER: PWG — MAIN ENTRY ===\n\nx\n\n=== LAYER: PW — y ===\n\nz', '[]', 'pwg_with_supplements'),
        ('=== LAYER: PWG — MAIN ENTRY ===\n\nx', '[]', 'pwg_only'),
        ('=== LAYER: PWG-ROOT HEAD — root=gam ===\n\nx', None, 'pwg_only'),
        ('no layer markers here', None, None),
    ]
    for raw, port, want in cases:
        got = gh.card_source_profile(raw, port)
        if got != want:
            fail('card_source_profile(%r) = %r, expected %r' % (raw[:30], got, want))



def test_no_pwg_supplement_card_renders_without_pwg():
    """H214: a PW-only lemma (Bagavat) and a SCH-only lemma (Akulita) render standalone
    supplement-chain sub-cards (raw + portrait) with NO fabricated PWG layer; a PWG key
    (agni) is left to the normal path (gen_no_pwg_card returns None)."""
    import _pilot_gen_merged as pg
    import gen_opt_harness2 as gh
    import dict_merge as dm
    old_out = pg.OUT
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        pg.OUT = tmp
        try:
            pwg_idx = dm.index('pwg')
            if pg.gen_no_pwg_card('agni', pwg_idx, verbose=False) is not None:
                fail('gen_no_pwg_card must return None for a PWG-present key (agni)')
            for key, want_layer in (('Bagavat', 'pw'), ('Akulita', 'sch')):
                n = pg.gen_no_pwg_card(key, pwg_idx, verbose=False)
                if not n:
                    fail('gen_no_pwg_card(%s) produced no sub-cards' % key)
                sub = '%s~~h0_zz_%s' % (pg.safe_name(key), want_layer)
                rp = os.path.join(pg.OUT, sub + '.raw.txt')
                pp = os.path.join(pg.OUT, sub + '.portrait.json')
                if not (os.path.exists(rp) and os.path.exists(pp)):
                    fail('expected no-PWG sub-card files for %s (%s)' % (key, sub))
                raw = open(rp, encoding='utf-8').read()
                port = open(pp, encoding='utf-8').read()
                if '=== LAYER: PWG' in raw:
                    fail('%s no-PWG card must NOT contain a PWG layer' % key)
                if '=== LAYER:' not in raw:
                    fail('%s no-PWG card missing a LAYER marker' % key)
                p0 = json.loads(port)[0]
                if p0.get('portrait_kind') != 'no_pwg_supplement_chain' or p0.get('key1') != key:
                    fail('%s portrait must be a no_pwg_supplement_chain sidecar keyed to the headword' % key)
                if p0.get('senses') != []:
                    fail('%s no-PWG portrait must not fabricate a sense tree' % key)
                if gh.card_source_profile(raw, port) != 'no_pwg_supplement_chain':
                    fail('%s sub-card must classify as no_pwg_supplement_chain' % key)
                if dm.layer_of(sub) != want_layer:
                    fail('%s sub-card id must encode layer %s' % (key, want_layer))
        finally:
            pg.OUT = old_out



def test_no_pwg_worklist_runnable_lane():
    """H214: the worklist exposes a no_pwg_runnable lane for PW/SCH/PWKVN-only lemmas and does
    NOT reclassify a true miss (absent from every layer) as runnable, nor mix it into the
    PWG-rooted runnable count."""
    import nominals_worklist as nw
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'sample.slp1.txt')
        manifest = os.path.join(tmp, 'scale_manifest.freq.json')
        store = os.path.join(tmp, 'store.jsonl')      # isolated empty store: the runnable/promoted
        with open(path, 'w', encoding='utf-8') as f:  # split must not depend on the live store
            f.write('Bagavat\nAkulita\nZZzznotaword\n')      # pw-only, sch-only, true miss
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump([
                {'key1': 'Bagavat', 'score': 3, 'band': 1},
                {'key1': 'Akulita', 'score': 2, 'band': 1},
                {'key1': 'ZZzznotaword', 'score': 1, 'band': 1},
            ], f)
        open(store, 'w', encoding='utf-8').close()
        payload = nw.build_worklist(path, manifest=manifest, store=store)
    runnable = set(payload['no_pwg_runnable'])
    if 'Bagavat' not in runnable or 'Akulita' not in runnable:
        fail('no_pwg_runnable must contain the PW/SCH-only lemmas: %s' % sorted(runnable))
    if 'ZZzznotaword' in runnable or 'ZZzznotaword' not in set(payload['true_miss_keys']):
        fail('a true miss must stay a true miss, never runnable')
    if runnable & set(payload['runnable_remaining']):
        fail('no-PWG runnable must stay separate from the PWG-rooted runnable lane')



def test_no_pwg_layer_and_profile_survive_promotion():
    """H214: layer label + source_profile survive sub-card id -> provenance -> promoted rows,
    for a no-PWG card AND a mixed (pwg_with_supplements) card, in one nominal window."""
    import promote_final_cards as pf
    meta = {
        'root': 'no_pwg_selftest', 'safe_root': 'no_pwg_selftest', 'generator': 'g',
        'schema_version': 'v', 'rootmap_sha256': None, 'generated_at': '2026-07-06T00:00:00Z',
        'nominal': True,
        'nominal_keymap': {'_bagavat~~h0_zz_pw00': 'Bagavat', 'x~~h0_00_pwg00': 'x'},
        'source_profiles': {'_bagavat~~h0_zz_pw00': 'no_pwg_supplement_chain',
                            'x~~h0_00_pwg00': 'pwg_with_supplements'},
        'input_hashes': {'_bagavat~~h0_zz_pw00': {'raw_sha256': 'r', 'portrait_sha256': 'p'},
                         'x~~h0_00_pwg00': {'raw_sha256': 'r2', 'portrait_sha256': 'p2'}},
    }

    def one(subkey, key1, ru):
        card = {'key1': key1, 'iast': key1,
                'records': [{'h': '1', 'senses': [{'tag': '1', 'russian': ru, 'german': 'x'}]}]}
        entry = {'card': card, 'meta': meta, 'wf_file': 't'}
        return list(pf.rows_for(subkey, entry, 'ai_translated', pf.SELFTEST_MODEL_VERSION))[0]

    r = one('_bagavat~~h0_zz_pw00', 'Bagavat', 'блаженный')
    if r['key1'] != 'Bagavat' or r['layer'] != 'pw':
        fail('no-PWG row must key to the headword and carry layer=pw: %r' % r)
    if r['provenance'].get('source_profile') != 'no_pwg_supplement_chain':
        fail('no-PWG provenance marker did not reach the promoted row')
    m = one('x~~h0_00_pwg00', 'x', 'слово')
    if m['layer'] != 'pwg' or m['provenance'].get('source_profile') != 'pwg_with_supplements':
        fail('mixed card must carry layer=pwg + source_profile=pwg_with_supplements: %r' % m)



def test_verb_worklist_excludes_missing_rootmaps():
    import verb_worklist as vw
    with tempfile.TemporaryDirectory() as tmp:
        preverb = os.path.join(tmp, 'pwg_preverb1.txt')
        manifest = os.path.join(tmp, 'scale_manifest.freq.json')
        store = os.path.join(tmp, 'pwg_ru_translated.jsonl')
        rootmaps = os.path.join(tmp, 'input')
        os.makedirs(rootmaps, exist_ok=True)
        with open(preverb, 'w', encoding='utf-8') as f:
            f.write(';; Case 1: L=1, k1=SrI, k2=x, code=x,\n')
            f.write(';; Case 2: L=2, k1=dah, k2=x, code=x,\n')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump([
                {'key1': 'SrI', 'score': 99.0, 'band': 5, 'bytes': 900},
                {'key1': 'dah', 'score': 10.0, 'band': 5, 'bytes': 100},
            ], f)
        with open(store, 'w', encoding='utf-8') as f:
            f.write('')
        with open(os.path.join(rootmaps, 'dah.rootmap.json'), 'w', encoding='utf-8') as f:
            json.dump({'meta': {'root': 'dah'}, 'items': []}, f)

        payload = vw.build_worklist(preverb=preverb, manifest=manifest,
                                    store=store, rootmap_dir=rootmaps)
        if payload.get('remaining') != ['SrI', 'dah']:
            fail('verb_worklist must preserve the raw score-ranked backlog')
        if payload.get('runnable_remaining') != ['dah']:
            fail('verb_worklist --top must be backed by runnable roots only')
        if payload.get('blocked_missing_rootmap') != ['SrI']:
            fail('missing-rootmap roots must remain visible in blocked_missing_rootmap')
        if payload.get('remaining_count') != 2 or payload.get('runnable_count') != 1:
            fail('verb_worklist count fields must distinguish backlog from runnable queue')
        if payload.get('remaining_bytes') != 1000 or payload.get('runnable_bytes') != 100:
            fail('verb_worklist byte fields must distinguish backlog from runnable queue')



def test_no_pwg_residual_registry_and_audit_command():
    import no_pwg_scale_plan as plan
    from types import SimpleNamespace
    with tempfile.TemporaryDirectory() as tmp:
        registry = os.path.join(tmp, 'residuals.jsonl')
        rows = [
            {'schema': 'pwg.no_pwg_residual.v1', 'key': 'a~~h0_zz_pw',
             'status': 'blocked', 'reason': 'repeat', 'source_window': 'w1',
             'updated_at': '2026-07-15T00:00:00Z'},
            {'schema': 'pwg.no_pwg_residual.v1', 'key': 'a~~h0_zz_pw',
             'status': 'resolved', 'reason': 'fixed', 'source_window': 'w2',
             'updated_at': '2026-07-15T01:00:00Z'},
            {'schema': 'pwg.no_pwg_residual.v1', 'key': 'b~~h0_zz_pw',
             'status': 'blocked', 'reason': 'repeat', 'source_window': 'w1',
             'updated_at': '2026-07-15T00:00:00Z'},
        ]
        with open(registry, 'w', encoding='utf-8') as f:
            for row in rows:
                f.write(json.dumps(row) + '\n')
        latest = plan.read_residuals(registry)
        if latest['a~~h0_zz_pw']['status'] != 'resolved':
            fail('latest residual registry row must win')
        eligible, skipped = plan.filter_residual_subcards(
            ['a~~h0_zz_pw', 'b~~h0_zz_pw'],
            {'b~~h0_zz_pw': latest['b~~h0_zz_pw']})
        if eligible != ['a~~h0_zz_pw'] or [r['key'] for r in skipped] != ['b~~h0_zz_pw']:
            fail('blocked residual filtering or explicit retry eligibility is wrong')
        command = plan.audit_command(
            'src/pilot/output/wf_output.no_pwg_w11.json', 'no_pwg_w11',
            'src/pilot/output/manifest.json')
        required = ('wf_output.no_pwg_w11.json', '--root "no_pwg_w11"',
                    '--write-requeue', '--window-tag "no_pwg_w11"',
                    '--execution-manifest')
        if any(piece not in command for piece in required):
            fail('no-PWG audit command is incomplete: %s' % command)

        original_run = plan.run_cmd
        original_existing = plan.existing_subcards
        original_store = plan.read_store_keys
        plan.run_cmd = lambda *_args, **_kwargs: ''
        plan.existing_subcards = lambda _head: ['b~~h0_zz_pw']
        plan.read_store_keys = lambda: set()
        try:
            omitted = plan.prepare_window(
                SimpleNamespace(prefix='fixture_w', blocked_residuals={
                    'b~~h0_zz_pw': latest['b~~h0_zz_pw']}),
                1, ['b'], [], False)
        finally:
            plan.run_cmd = original_run
            plan.existing_subcards = original_existing
            plan.read_store_keys = original_store
        if not omitted.get('omitted') or omitted.get('subcards'):
            fail('a no-PWG head with only blocked residuals must be omitted')



def test_no_pwg_require_senses_gate():
    """H4527: --require-senses must prove a repair lane before a paid call is spent.

    `agent_budget` derives the per-card self-heal pool from sense groups, so a
    zero-sense sub-card runs with `max_heal_agents: 0` — one shot, no repair. The
    16-09-2026 acceptance window paid for exactly that topology and came back null.
    """
    import no_pwg_scale_plan as plan
    from types import SimpleNamespace

    with tempfile.TemporaryDirectory() as tmp:
        rich = 'darv_i~~h0_zz_pw'
        poor = 'darv_i~~h0_zz_nws00'
        with open(os.path.join(tmp, rich + '.portrait.json'), 'w', encoding='utf-8') as f:
            json.dump({'key': rich, 'source_senses': 3}, f)
        with open(os.path.join(tmp, rich + '.raw.txt'), 'w', encoding='utf-8') as f:
            f.write('1\u3009 first sense\n2\u3009 second sense\n')
        with open(os.path.join(tmp, poor + '.raw.txt'), 'w', encoding='utf-8') as f:
            f.write('an unnumbered supplement gloss\n')

        # the stamped portrait count wins over a recount of the raw blob
        if plan.subcard_source_senses(rich, tmp) != 3:
            fail('--require-senses must read the portrait sidecar stamp first')
        # no portrait -> deterministic recount, not a guess
        if plan.subcard_source_senses(poor, tmp) != 0:
            fail('a sense-poor sub-card without a portrait must recount to 0')
        # neither sidecar -> unprovable, and unprovable is never zero
        if plan.subcard_source_senses('absent~~h0_zz_pw', tmp) is not None:
            fail('a missing sidecar pair must read as None (unprovable), never 0')

        kept, skipped = plan.filter_sense_poor_subcards(
            [rich, poor, 'absent~~h0_zz_pw'], 1, tmp)
        if kept != [rich]:
            fail('--require-senses kept a sub-card that cannot prove the minimum: %r' % kept)
        if [row['key'] for row in skipped] != [poor, 'absent~~h0_zz_pw']:
            fail('--require-senses did not report every skipped sub-card')
        if skipped[0]['source_senses'] != 0 or skipped[1]['source_senses'] is not None:
            fail('skipped rows must carry the measured count, unknown as None')
        if plan.filter_sense_poor_subcards([rich], 4, tmp)[0]:
            fail('--require-senses must refuse a count below the requested minimum')

        # a head whose eligible sub-cards are ALL sense-poor is omitted, like a
        # fully-blocked head -- and nothing is written to the residual registry
        originals = {name: getattr(plan, name) for name in
                     ('run_cmd', 'existing_subcards', 'read_store_keys',
                      'subcard_source_senses', 'filter_sense_poor_subcards')}
        plan.run_cmd = lambda *_args, **_kwargs: ''
        plan.existing_subcards = lambda _head: [poor]
        plan.read_store_keys = lambda: set()
        plan.subcard_source_senses = lambda key, input_dir=None: (
            originals['subcard_source_senses'](key, tmp))
        try:
            omitted = plan.prepare_window(
                SimpleNamespace(prefix='fixture_w', blocked_residuals={},
                                require_senses=1),
                1, ['darv_i'], [], False)
            if not omitted.get('omitted') or omitted.get('subcards'):
                fail('a head with only sense-poor sub-cards must be omitted')
            if [row['key'] for row in omitted['sense_skipped']] != [poor]:
                fail('the omitted window must name the sense-poor sub-cards it skipped')
            if omitted['residual_skipped']:
                fail('the sense gate must not invent residual-registry rows')

            # off by default: an args object without the attribute never reaches the gate
            def refuse(*_args, **_kwargs):
                fail('--require-senses gate ran while the flag was off')
            plan.filter_sense_poor_subcards = refuse
            try:
                blocked = {poor: {'key': poor, 'reason': 'repeat failure',
                                  'source_window': 'old'}}
                legacy = plan.prepare_window(
                    SimpleNamespace(prefix='fixture_w', blocked_residuals=blocked),
                    2, ['darv_i'], [], False)
            finally:
                plan.filter_sense_poor_subcards = originals['filter_sense_poor_subcards']
            if not legacy.get('omitted') or legacy.get('sense_skipped'):
                fail('the historical (flag-off) path must be byte-identical')
        finally:
            for name, value in originals.items():
                setattr(plan, name, value)

        # the manifest records the gate and everything it skipped
        planner_originals = {name: getattr(plan, name) for name in
                             ('read_queue', 'read_store_heads', 'read_still_null',
                              'read_residuals', 'prepare_window')}
        manifest = os.path.join(tmp, 'plan.json')
        plan.read_queue = lambda: [{'key1': 'darv_i'}, {'key1': 'gl_ana'}]
        plan.read_store_heads = lambda: set()
        plan.read_still_null = lambda: []
        plan.read_residuals = lambda _path: {}

        def prepare_stub(args, index, heads, _still_null, _tail_mode):
            if args.require_senses != 2:
                fail('--require-senses did not reach prepare_window: %r' % args.require_senses)
            if heads[0] == 'darv_i':
                return {'omitted': True, 'root': 'sense_w%02d' % index,
                        'headwords': heads, 'residual_skipped': [],
                        'sense_skipped': [{'key': poor, 'source_senses': 0,
                                           'reason': 'source senses 0 < --require-senses 2'}]}
            return {'root': 'sense_w%02d' % index, 'mode': 'queue', 'headwords': heads,
                    'subcards': ['gl_ana~~h0_zz_pw'], 'harness': 'run.js',
                    'workflow_output': 'wf.json', 'preflight': {},
                    'headless': {'projected_calls': 1},
                    'residual_skipped': [], 'sense_skipped': []}

        try:
            plan.prepare_window = prepare_stub
            plan.main(['--window-size', '1', '--limit-windows', '1',
                       '--start-index', '920', '--force-index',
                       '--prefix', 'sense_w', '--manifest', manifest,
                       '--require-senses', '2'])
            payload = json.load(open(manifest, encoding='utf-8'))
            if payload.get('require_senses') != 2:
                fail('the plan manifest must record the sense gate it ran under')
            if [row['key'] for row in payload.get('sense_skipped') or []] != [poor]:
                fail('the plan manifest must carry every sense-skipped sub-card')
            if payload['prepared_windows'] != 1 or payload['windows'][0]['root'] != 'sense_w921':
                fail('a sense-omitted head must not consume the preparation quota')
        finally:
            for name, value in planner_originals.items():
                setattr(plan, name, value)

    try:
        plan.main(['--plan-only', '--require-senses', '-1'])
    except SystemExit as exc:
        if '--require-senses must be >= 0' not in str(exc):
            fail('a negative --require-senses must be refused by name: %s' % exc)
    else:
        fail('a negative --require-senses was accepted')



def test_no_pwg_preparation_advances_past_omitted_chunks():
    import no_pwg_scale_plan as plan

    def residual(key):
        return {'schema': 'pwg.no_pwg_residual.v1', 'key': key,
                'status': 'blocked', 'reason': 'repeat failure',
                'source_window': 'old', 'updated_at': '2026-07-15T00:00:00Z'}

    originals = {name: getattr(plan, name) for name in
                 ('read_queue', 'read_store_heads', 'read_still_null',
                  'read_residuals', 'prepare_window')}
    with tempfile.TemporaryDirectory() as tmp:
        registry = os.path.join(tmp, 'residuals.jsonl')
        manifest = os.path.join(tmp, 'plan.json')
        blocked = {'a~~x': residual('a~~x'), 'b~~x': residual('b~~x')}
        plan.read_queue = lambda: [
            {'key1': 'a'}, {'key1': 'b'}, {'key1': 'c'}]
        plan.read_store_heads = lambda: set()
        plan.read_still_null = lambda: []
        plan.read_residuals = lambda _path: blocked

        def prepare_some(args, index, heads, _still_null, _tail_mode):
            head = heads[0]
            if head == 'a':
                return {'omitted': True, 'root': 'fixture_w%02d' % index,
                        'headwords': heads,
                        'residual_skipped': plan.residual_summary([blocked['a~~x']])}
            return {'root': 'fixture_w%02d' % index, 'mode': 'queue',
                    'headwords': heads, 'subcards': [head + '~~x'],
                    'harness': 'run.js', 'workflow_output': 'wf.json',
                    'preflight': {}, 'headless': {'projected_calls': 1},
                    'residual_skipped': []}

        try:
            plan.prepare_window = prepare_some
            plan.main(['--window-size', '1', '--limit-windows', '1',
                       '--start-index', '900', '--force-index',
                       '--prefix', 'fixture_w', '--manifest', manifest,
                       '--residual-file', registry])
            payload = json.load(open(manifest, encoding='utf-8'))
            if payload['prepared_windows'] != 1 or payload['prepared_headwords'] != 1:
                fail('an omitted chunk consumed the requested preparation quota')
            if payload['windows'][0]['root'] != 'fixture_w901':
                fail('planner did not advance to the first eligible deterministic index')
            if [row['root'] for row in payload['omitted_windows']] != ['fixture_w900']:
                fail('omitted chunk was not reported completely')
            if payload['residual_skipped'][0]['reason'] != 'repeat failure':
                fail('omitted residual reason was lost from the plan manifest')

            def prepare_none(args, index, heads, _still_null, _tail_mode):
                key = heads[0] + '~~x'
                row = blocked.get(key) or residual(key)
                blocked[key] = row
                return {'omitted': True, 'root': 'blocked_w%02d' % index,
                        'headwords': heads,
                        'residual_skipped': plan.residual_summary([row])}

            plan.prepare_window = prepare_none
            blocked_manifest = os.path.join(tmp, 'blocked-plan.json')
            plan.main(['--window-size', '1', '--limit-windows', '1',
                       '--start-index', '910', '--force-index',
                       '--prefix', 'blocked_w', '--manifest', blocked_manifest,
                       '--residual-file', registry])
            payload = json.load(open(blocked_manifest, encoding='utf-8'))
            if payload['prepared_windows'] != 0 or payload['windows']:
                fail('an entirely blocked queue must prepare zero windows')
            if len(payload['omitted_windows']) != 3:
                fail('an entirely blocked queue must report every omitted chunk')
        finally:
            for name, value in originals.items():
                setattr(plan, name, value)



def test_promote_nominal_key1():
    import promote_final_cards as pfc
    entry = {
        'card': {'key1': 'agni', 'iast': 'agni', 'records': [
            {'h': 'agni', 'senses': [{'tag': '1', 'russian': 'огонь', 'german': 'Feuer'}]},
        ]},
        'meta': {'nominal': True, 'root': 'nominal_batch',
                 'input_hashes': {'agni': {'raw_sha256': 'r', 'portrait_sha256': 'p'}}},
        'wf_file': 'wf_output.nominal.json',
    }
    rows = list(pfc.rows_for('agni', entry, 'ai_translated', pfc.SELFTEST_MODEL_VERSION))
    if not rows or rows[0]['key1'] != 'agni':
        fail('nominal promotion must preserve the assembled-card key1')
    mapped = {
        'card': {'key1': 'af_rin', 'records': [
            {'h': 'afRin', 'senses': [{'tag': '1', 'russian': 'свободный', 'german': 'frei'}]},
        ]},
        'meta': {'nominal': True, 'root': 'nominal_batch',
                 'nominal_keymap': {'af_rin': 'afRin'}},
        'wf_file': 'wf_output.nominal.json',
    }
    rows = list(pfc.rows_for('af_rin', mapped, 'ai_translated', pfc.SELFTEST_MODEL_VERSION))
    if not rows or rows[0]['key1'] != 'afRin':
        fail('nominal promotion must map safe runtime keys back to assembled key1')



def test_no_pwg_supplement_chain_cards_render():
    """H214: PWG-missing lemmas with PW/SCH/PWKVN/NWS records are runnable.

    Synthetic indexes and a temp input directory prove the generator path without
    requiring csl-orig or touching live pilot/input artifacts.
    """
    import _pilot_gen_merged as pg
    from safe_filename import safe_name
    old_out = pg.OUT
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        pg.OUT = tmp
        try:
            bagavat_n = pg.gen_no_pwg_card('Bagavat', {}, verbose=False)
            akulita_n = pg.gen_no_pwg_card('Akulita', {}, verbose=False)
            if not bagavat_n:
                fail('Bagavat should render as a no-PWG supplement-chain card')
            if not akulita_n:
                fail('Akulita should render as a SCH-only no-PWG supplement-chain card')
            bagavat_stem = safe_name('Bagavat')
            akulita_stem = safe_name('Akulita')
            bagavat_files = [n for n in os.listdir(tmp) if n.startswith(bagavat_stem + '~~h0_zz_')]
            akulita_files = [n for n in os.listdir(tmp) if n.startswith(akulita_stem + '~~h0_zz_')]
            if not any('_zz_pw' in n and n.endswith('.raw.txt') for n in bagavat_files):
                fail('Bagavat must emit a PW-labeled no-PWG sub-card')
            if not any('_zz_sch' in n and n.endswith('.raw.txt') for n in akulita_files):
                fail('Akulita must emit a SCH-labeled no-PWG sub-card')
            for stem in (bagavat_stem + '~~h0_zz_pw', akulita_stem + '~~h0_zz_sch'):
                raw_path = os.path.join(tmp, stem + '.raw.txt')
                portrait_path = os.path.join(tmp, stem + '.portrait.json')
                if not os.path.exists(raw_path) or not os.path.exists(portrait_path):
                    fail('missing no-PWG generated files for %s' % stem)
                raw = open(raw_path, encoding='utf-8').read()
                portrait = json.load(open(portrait_path, encoding='utf-8'))
                if '=== LAYER: PWG' in raw:
                    fail('%s must not fabricate a PWG layer' % stem)
                if not portrait or portrait[0].get('source_profile') != 'no_pwg_supplement_chain':
                    fail('%s portrait must carry source_profile=no_pwg_supplement_chain' % stem)
                if portrait[0].get('senses') != []:
                    fail('%s portrait must not fabricate a PWG sense tree' % stem)
        finally:
            pg.OUT = old_out



def test_no_pwg_source_profile_promotes():
    import gen_opt_harness2 as gh
    import promote_final_cards as pfc
    old_input_paths = gh.input_paths
    with tempfile.TemporaryDirectory() as tmp:
        key = 'bagavat~~h0_zz_pw'
        raw_path = os.path.join(tmp, key + '.raw.txt')
        portrait_path = os.path.join(tmp, key + '.portrait.json')
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n{#Bagavat#}¦ selig.\n')
        with open(portrait_path, 'w', encoding='utf-8') as f:
            json.dump([{'portrait_kind': 'no_pwg_supplement_chain',
                        'source_profile': 'no_pwg_supplement_chain',
                        'key1': 'Bagavat', 'iast': 'bhagavat', 'layers': ['pw'],
                        'senses': []}], f)
        gh.input_paths = lambda k, input_dir=None: (
            os.path.join(tmp, k + '.raw.txt'), os.path.join(tmp, k + '.portrait.json'))
        try:
            js, _batches = gh.build('no_pwg_sample', [key], None, 12000, nominal=True,
                                    grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = old_input_paths
        import re as _re
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        if meta.get('source_profile') != 'no_pwg_supplement_chain':
            fail('all-no-PWG harness must stamp window source_profile')
        if (meta.get('source_profiles') or {}).get(key) != 'no_pwg_supplement_chain':
            fail('harness must stamp per-card no-PWG source profile')
        entry = {
            'card': {'key1': key, 'iast': 'bhagavat', 'records': [
                {'senses': [{'tag': '1', 'russian': 'бхагават', 'german': '{#Bagavat#}¦ selig.'}]},
            ]},
            'meta': meta,
            'wf_file': 'wf_output.no_pwg.json',
        }
        rows = list(pfc.rows_for(key, entry, 'ai_translated', pfc.SELFTEST_MODEL_VERSION))
        if not rows:
            fail('no-PWG promotion fixture yielded no rows')
        row = rows[0]
        if row['key1'] != 'Bagavat':
            fail('no-PWG nominal promotion must map runtime key back to true key1')
        if row['layer'] != 'pw':
            fail('no-PWG promoted row must preserve layer=pw')
        if row['provenance'].get('source_profile') != 'no_pwg_supplement_chain':
            fail('promoted provenance must preserve source_profile=no_pwg_supplement_chain')



def test_nominal_key_echo_tolerance_scoped():
    """H220: nominal / no-PWG windows must tolerate the model echoing the CLEAN SLP1 headword
    (nominal_keymap[stem], e.g. 'CAyA') instead of the mangled sub-card stem
    (_c_ay_a~~h0_zz_pw) in key1 — recovering the card by re-keying it to the stem, but ONLY
    when the SLP1 maps to exactly one pending stem (unambiguous). This must be GATED on
    META.nominal so PWG root windows keep strict key matching (paired with
    test_generated_harness_strict_key_matching). Static guard on the generated harness."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '{#CAya#}¦ {%Schatten%}.\n')
    key = '_c_ay_a~~h0_zz_pw'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[{"portrait_kind":"no_pwg_supplement_chain","key1":"CAyA","iast":"chāyā","senses":[]}]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = saved_ip
        # the recovery is gated on META.nominal + nominal_keymap (inert for root windows)
        if 'META.nominal && META.nominal_keymap' not in js:
            fail('nominal key-echo tolerance must be gated on META.nominal so root windows stay strict')
        # unambiguous rival check (never re-key a SLP1 that maps to >1 pending stem) + re-key to stem
        if 'const rivals = cur.filter(x => NKM[x] === slp1)' not in js:
            fail('key-echo recovery must guard on an UNAMBIGUOUS SLP1->stem mapping within the batch')
        if 'rivals.length === 1' not in js or 'cand.key1 = k' not in js:
            fail('recovery must require exactly one rival stem and re-key the card to the stem')
        # H255/H834: also accept the SLP1 headword with the sub-card suffix kept
        # ('avyAhata~~h0_zz_pw' for the stem 'avy_ahata~~h0_zz_pw'), still gated + unambiguous.
        if 'km[slp1 + sfx]' not in js:
            fail('key-echo recovery must also accept the SLP1 headword carrying the ~~<layer> '
                 'suffix (the H255 avy_ahata failure), not only the bare SLP1')
        # strict key lookup (km[k]) is still the FIRST attempt — tolerance is a fallback, not positional
        if 'let cand = km[k]' not in js:
            fail('strict key lookup km[k] must remain the primary match; tolerance is a fallback only')
        meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
        if not meta.get('nominal') or meta.get('nominal_keymap', {}).get(key) != 'CAyA':
            fail('nominal harness must carry nominal_keymap[stem]=SLP1 for the re-key (got %r)'
                 % meta.get('nominal_keymap'))
    finally:
        shutil.rmtree(d, ignore_errors=True)

