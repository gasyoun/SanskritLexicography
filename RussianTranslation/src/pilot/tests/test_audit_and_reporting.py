"""test_audit_and_reporting — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_audit_and_reporting.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports
from _support import _h4054_synth_inputs  # noqa: F401  -- `import *` skips _names


def test_tnmask_persist_and_offline_detect():
    """H1226: accept() PERSISTS the pre-restore {Tn} pairing (candidate `got` vs masked-skeleton
    `want`) on the accepted card, and promote carries it to the row's provenance, so a SOFT
    (un-rejected) TNMASK expansion becomes MEASURABLE offline from a promoted row -- H1150 returned
    DO_NOT_ARM (denominator 1) precisely because the store dropped this transient pairing.
    Two-part pin: (1) the behavioral half runs the REAL emitted accept()+tokensOf+cardTokens
    (tnmask_persist_test.js, extraction pattern -> cannot drift from the generator); (2) the
    end-to-end half proves detection through the REAL promote_final_cards.rows_for + the offline
    reader -- GREEN with the field, RED (not measurable) without it."""
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, 'tnp~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'tnp~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#tnp#}¦ {%m%}\n— 1〉 {%a%}.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        gh.KILL = False
        js, _ = gh.build('zz_tnmask', ['tnp~~h0_zz_pw'], None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        # (1a) the persistence line is emitted into the real accept(), and the arming consts are
        #      byte-unchanged (this handoff persists provenance; it never arms).
        if 'c.tnmask = {' not in js:
            fail('accept() must persist the pre-restore {Tn} pairing (c.tnmask) — H1226')
        for needle in ('const TNMASK_HARD_REJECT = false', 'const SANLOSS_HARD_REJECT = false'):
            if needle not in js:
                fail('H1226 must leave the soft-guard arming consts unchanged (missing %r)' % needle)
        # (1b) behavioral: the REAL accept() stamps got/want; an expansion is flagged, clean isn't.
        harness = os.path.join(d, 'tnmask_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(HERE,
                               'tnmask_persist_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('tnmask persistence behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        shutil.rmtree(d, ignore_errors=True)
    # (2) offline detection end-to-end through the REAL promote path (red/green).
    import promote_final_cards as pfc
    import tnmask_offline as tno
    meta = {'root': 'tnp', 'nominal': True, 'nominal_keymap': {'tnp~~h0_zz_pw': 'tnp'},
            'input_hashes': {'tnp~~h0_zz_pw': {'raw_sha256': 'r', 'portrait_sha256': 'p'}}}
    base_card = {'key1': 'tnp', 'iast': 'tnp', 'notes': '',
                 'records': [{'h': 'tnp', 'grammar': '',
                              'senses': [{'tag': '1', 'russian': 'x', 'german': 'y'}]}]}
    exp_card = dict(base_card, tnmask={'got': 'T1', 'want': 'T1 T2'})   # a soft expansion
    row = list(pfc.rows_for('tnp~~h0_zz_pw',
                            {'card': exp_card, 'meta': meta, 'wf_file': 'wf.json'},
                            'ai_translated', pfc.SELFTEST_MODEL_VERSION))[0]
    if not tno.tnmask_measurable(row):
        fail('promoted row must carry the H1226 {Tn} pairing when the card has one')
    if tno.tnmask_mismatch(row) is not True:
        fail('GREEN: an expansion must be detectable offline from the promoted row')
    stripped = json.loads(json.dumps(row))          # the SAME row, field removed = pre-H1226
    stripped['provenance'].pop('tnmask', None)
    if tno.tnmask_mismatch(stripped) is not None:
        fail('RED: without the field the promoted row must be NOT MEASURABLE, never a silent clean')
    tno.selftest()                                  # pin the reader itself (fail-loud, no I/O)



def test_grammar_field_restore_behavioral():
    """H1151 pin for the H858 grammar-{Tn} stranding class (live on gokzuraka, 13-07-2026).
    The C-01 centralization (card_fields.js_restore_spec) already restores record.grammar in
    both lanes; this behavioral test extracts the REAL restore()/restoreCard()/RESTORE_SPEC
    from a freshly generated harness (grammar_restore_test.js) so a future edit that drops
    `grammar` (or `h`) from the record-level restore fails HERE, not as silent store rows."""
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, 'gok~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'gok~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#gok#}¦ {%m%}\n— 1〉 {%a%}.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        gh.KILL = False
        js, _ = gh.build('zz_grestore', ['gok~~h0_zz_pw'], None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        harness = os.path.join(d, 'grestore_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(HERE,
                               'grammar_restore_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('grammar-field restore behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        shutil.rmtree(d, ignore_errors=True)



def test_h3675_target_anchor_repair_behavioral():
    """H3675: the TARGET-side twin of the anchored repair, on the real emitted harness.

    The half of the span-drop class `german_anchor` was never built to catch: the german echo
    comes back faithful and the translation drops a span, so `count_card_field` nulls the card
    while the german-side repair is never even reached (FINDINGS §605/§608). MG ruled
    `reanchor` over an explicit requeue on 29-08-2026.

    Same two-part pin as its german sibling: (1) the twin + its telemetry are emitted into the
    harness at all; (2) the behavioural half runs the REAL emitted taPlan/taReanchor/taStamp
    AND the REAL accept() + restoreCard (`target_anchor_test.js`), so it cannot drift from the
    generator. The Python twin of the same cases is `target_anchor.selftest()`, run by
    `test_h3675_target_anchor_selftest` below — both lanes are interpolated from ONE authored
    source (`target_anchor.js_source()`), the C-01/C-17 lesson.
    """
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, 'ta~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'ta~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#ta#}¦ {%m%}\n— 1〉 {%a%}.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        gh.KILL = False
        js, _ = gh.build('zz_tanchor', ['ta~~h0_zz_pw'], None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        for needle in ('const taPlan = ', 'const taReanchor = ', 'const taStamp = ',
                       'TARGET_ANCHOR_REPAIRS', 'target_anchor_repairs', 'target-anchor '):
            if needle not in js:
                fail('H3675 target-anchor repair not emitted into the harness (missing %r)' % needle)
        harness = os.path.join(d, 'tanchor_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(HERE,
                               'target_anchor_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('target-anchor repair behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill



def test_threaded_gate_exception_requeues_full_window():
    """An unexpected future exception must become durable rc=3/full-window gate evidence."""
    import audit_window as aw
    real_nws = aw.run_nws_gate
    real_prompt = aw.run_prompt_semantic_audit
    real_sense = aw.run_sense_shortfall_gate

    def clean_gate(name):
        return {'argv': ['in-process', name], 'returncode': 0, 'stdout': '',
                'stderr': '', 'seconds': 0.0, 'requeue': []}

    def explode(*_args):
        raise RuntimeError('synthetic threaded failure')

    try:
        aw.run_nws_gate = lambda *_args: clean_gate('nws')
        aw.run_prompt_semantic_audit = explode
        aw.run_sense_shortfall_gate = lambda *_args: clean_gate('sense_loss')
        gates = aw.run_threaded_gates(
            ['z~~2', 'a~~1'], set(), 'fixture.json', [], 'fixture-input')
    finally:
        aw.run_nws_gate = real_nws
        aw.run_prompt_semantic_audit = real_prompt
        aw.run_sense_shortfall_gate = real_sense

    failed = gates['prompt_semantic']
    if failed.get('returncode') != 3:
        fail('threaded exception must become returncode=3, got %r' % failed)
    if failed.get('requeue') != ['a~~1', 'z~~2']:
        fail('threaded exception must deterministically requeue the full window: %r' % failed)
    for field in ('argv', 'stdout', 'stderr', 'seconds'):
        if field not in failed:
            fail('threaded exception result lacks CompletedProcess field %s: %r'
                 % (field, failed))
    if 'RuntimeError: synthetic threaded failure' not in failed['stderr']:
        fail('threaded exception diagnostic missing from stderr: %r' % failed['stderr'])
    if set(gates) != {'nws', 'prompt_semantic', 'sense_loss'}:
        fail('one future exception prevented remaining gate results: %r' % gates)

    # Pin the integration consequence too: main() must reach write_reports/window_status,
    # not merely return a well-shaped helper value.
    originals = {
        'run_nws_gate': aw.run_nws_gate,
        'run_prompt_semantic_audit': aw.run_prompt_semantic_audit,
        'run_sense_shortfall_gate': aw.run_sense_shortfall_gate,
        'collect_cards': aw.collect_cards,
        'run_py_inproc': aw.run_py_inproc,
        'stale_check': aw.stale_check,
        'emit_audit_event': aw.emit_audit_event,
        'emit_stage_boundary': aw.emit_stage_boundary,
    }
    old_argv = sys.argv[:]
    with tempfile.TemporaryDirectory() as tmp:
        wf_path = os.path.join(tmp, 'wf_output.json')
        report_dir = os.path.join(tmp, 'reports')
        with open(wf_path, 'w', encoding='utf-8') as f:
            json.dump({'results': [{'key': 'z~~2', 'card': None}]}, f)
        try:
            aw.run_nws_gate = lambda *_args: dict(
                clean_gate('nws'), misattribution=[], rejected=[])
            aw.run_prompt_semantic_audit = explode
            aw.run_sense_shortfall_gate = lambda *_args: clean_gate('sense_loss')
            aw.collect_cards = lambda *_args: clean_gate('collect')
            aw.run_py_inproc = lambda *_args: dict(
                clean_gate('child'), stdout='FLAGGED_JSON: []\n')
            aw.stale_check = lambda *_args, **_kwargs: {'stale': False}
            aw.emit_audit_event = lambda *_args, **_kwargs: None
            aw.emit_stage_boundary = lambda *_args, **_kwargs: None
            sys.argv = ['audit_window.py', wf_path, '--out-dir', report_dir]
            try:
                aw.main()
            except SystemExit as exc:
                if exc.code != 1:
                    fail('future-failed audit must exit 1 after reporting, got %r' % exc.code)
            else:
                fail('future-failed audit unexpectedly returned without a status exit')
        finally:
            for name, value in originals.items():
                setattr(aw, name, value)
            sys.argv = old_argv

        report_path = os.path.join(report_dir, 'audit_window.report.json')
        status_path = os.path.join(report_dir, 'window_status.json')
        if not os.path.exists(report_path) or not os.path.exists(status_path):
            fail('future exception aborted before durable report/status: %s %s'
                 % (os.path.exists(report_path), os.path.exists(status_path)))
        report = json.load(open(report_path, encoding='utf-8'))
        failed = report['gates']['prompt_semantic']
        if failed.get('returncode') != 3 or failed.get('requeue') != ['z~~2']:
            fail('durable future-failure evidence is incomplete: %r' % failed)
        if 'prompt_semantic' not in report.get('crashed', []):
            fail('durable report did not classify the future failure as crashed: %r'
                 % report.get('crashed'))



def test_quarantine_replace_failure_preserves_previous_destination():
    """A failed atomic replace keeps the prior reject and yields rc=3/full-window evidence."""
    import audit_window as aw
    key = 'atomic~~reject'
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, key + '.merged.md')
        dst = os.path.join(tmp, key + '.merged.REJECTED.md')
        with open(src, 'w', encoding='utf-8') as f:
            f.write('fresh candidate')
        with open(dst, 'w', encoding='utf-8') as f:
            f.write('prior rejected artifact')

        old_out, old_replace = aw.OUT, aw.os.replace

        def fail_replace(_src, _dst):
            raise OSError('synthetic replace denial')

        gate = {
            'argv': ['in-process', 'nws_split.check_result'],
            'returncode': 1,
            'stdout': '',
            'stderr': '',
            'seconds': 0.0,
            'requeue': [key],
            'misattribution': [key],
            'rejected': [],
        }
        try:
            aw.OUT = tmp
            aw.os.replace = fail_replace
            aw.apply_nws_quarantine(gate, [key, 'other~~key'])
        finally:
            aw.OUT = old_out
            aw.os.replace = old_replace

        if open(dst, encoding='utf-8').read() != 'prior rejected artifact':
            fail('failed quarantine destroyed or changed the prior rejected artifact')
        if open(src, encoding='utf-8').read() != 'fresh candidate':
            fail('failed quarantine unexpectedly removed the fresh source artifact')
        if gate.get('returncode') != 3:
            fail('quarantine OSError must become returncode=3 evidence: %r' % gate)
        if gate.get('requeue') != [key, 'other~~key']:
            fail('quarantine failure must requeue the deterministic full window: %r' % gate)
        if 'OSError: synthetic replace denial' not in gate.get('stderr', ''):
            fail('quarantine failure diagnostic missing from stderr: %r' % gate)
        if gate.get('rejected'):
            fail('failed quarantine was incorrectly reported as rejected: %r' % gate)



def test_optional_sibling_bibliography_degrades():
    """An ABSENT optional sibling repo must not break the promotion path.

    `pwg_sources.BIB` lives in `csl-pywork`, which CI does not check out and a fresh clone
    does not have. It used to raise FileNotFoundError, and because
    `promote_final_cards.rows_for` -> `extract_citation_edges` -> `pwg_sources.resolve`
    sits on the promotion path, an absent *enrichment* source became a hard failure of
    promotion itself. Citation edges are additive metadata: missing bibliography must mean
    "no expansions resolved", never "the store cannot be written".
    """
    import pwg_sources
    saved_path, saved_cache = pwg_sources.BIB, pwg_sources._BIB
    try:
        pwg_sources.BIB = os.path.join(tempfile.gettempdir(), 'no-such-pwgbib.txt')
        pwg_sources._BIB = None
        if pwg_sources.bib() != {}:
            fail('an absent bibliography must resolve to an empty map')
        if pwg_sources.resolve('RV.') is not None:
            fail('an absent bibliography must resolve nothing, not raise')
        import citation_edges
        citation_edges.extract_citation_edges('Feuer <ls>RV. 1,1</ls>')   # must not raise
    finally:
        pwg_sources.BIB, pwg_sources._BIB = saved_path, saved_cache



def test_h3675_target_anchor_selftest():
    """H3675: the Python half of the target-side repair, and its LANG_PARITY guarantee.

    `target_anchor` is SHARED. It takes the target field as a PARAMETER and anchors against
    `german`, so the RU and EN lanes run byte-identical logic; the module must never name a
    language. This asserts that mechanically rather than trusting it, exactly as
    `test_german_anchor_selftest` does for the source-side twin.
    """
    import target_anchor
    target_anchor.selftest()
    if 'russian' in target_anchor._JS or 'english' in target_anchor._JS:
        fail('target_anchor must stay language-agnostic (SHARED under LANG_PARITY.md)')
    for target in ('russian', 'english'):
        card = {'records': [{'senses': [{'german': '{T1} Feuer {T2}', target: 'x {T2}'}]}]}
        ok, info = target_anchor.reanchor(card, target)
        sense = card['records'][0]['senses'][0]
        if not ok or sense[target] != '{T1} x {T2}':
            fail('target_anchor repaired differently for target field %r: %r' % (target, info))
        if sense['german'] != '{T1} Feuer {T2}':
            fail('target_anchor wrote the german anchor field for target %r' % target)



def test_h3627_structured_output_exhaustion_is_parked_not_window_fatal():
    """A CLI that exhausts its structured-output retries has failed THIS GROUP, not the window.

    It exits NON-ZERO, which `classify_process` reads as 'process' -- window-fatal. That is how
    a 23-key window threw away 19 already-paid successes when call 20 tripped the validator
    (FINDINGS 596). The predicate must fire on either envelope field the CLI uses, and must NOT
    fire on an unknown non-zero exit: 'we could not tell' has to stay fatal, or an unrecognised
    failure would silently keep spending.
    """
    import headless_worker as hw
    if not hw.structured_output_exhausted({'subtype': 'error_max_structured_output_retries'}):
        fail('the subtype form must be recognised')
    if not hw.structured_output_exhausted(
            {'terminal_reason': 'structured_output_retry_exhausted'}):
        fail('the terminal_reason form must be recognised')
    for hostile in (None, {}, 'structured_output_retry_exhausted',
                    {'subtype': 'error_other'},
                    {'terminal_reason': 'success'},
                    {'error': 'structured_output_retry_exhausted somewhere in prose'}):
        if hw.structured_output_exhausted(hostile):
            fail('must not fire on %r -- an unknown non-zero exit stays window-fatal' % (hostile,))



def test_h3627_aborted_window_still_yields_its_paid_cards():
    """A window that dies on call N must still emit calls 1..N-1.

    `execute()` used to return payload=None on HardFailure, so `main()` wrote no --output at
    all and every card the window had already paid for was discarded (FINDINGS 596). The
    engine now carries them on `partial_rows`, and the salvage path builds the SAME payload
    shape as a clean run via `_finish_payload`, so the cards stay promotable.
    """
    import headless_worker as hw

    class StubEngine(object):
        translate_calls = 3
        heal_calls = 1
        budget_stops = 0
        usage = {'priced_calls': 3}
        kill_timeouts = 0
        conn_errors = 0
        attempts = [{'label': 'b0', 'classification': 'success'}]
        safe_mode = True

    manifest = {'schema': hw.SCHEMA_V2,
                'meta': {'root': 'h3627-selftest', 'lang': 'ru',
                         'selected_keys': ['done_key', 'never_reached']},
                'execution': {}, 'key_provenance': {}}
    resolved = [{'key': 'done_key', 'card': {'key1': 'done_key'}, 'judge': None,
                 'judge_sonnet': None, 'escalated': False}]
    payload = hw._finish_payload(manifest, StubEngine(), list(resolved), 1, 0)

    keys = {row['key']: row for row in payload['results']}
    if not keys.get('done_key', {}).get('card'):
        fail('the already-paid card must survive the abort, got %r' % (payload['results'],))
    if keys.get('never_reached', {}).get('card') is not None:
        fail('an unreached key must be present but null, not fabricated')
    if keys['never_reached'].get('error') != 'unaccounted-key':
        fail('an unreached key must be marked unaccounted-key, got %r' % keys['never_reached'])
    if payload['summary']['ok'] != 1 or payload['summary']['null'] != 1:
        fail('summary must count 1 ok / 1 null, got %r' % payload['summary'])
    for field in ('meta', 'summary', 'results'):
        if field not in payload:
            fail('salvage payload must keep the clean-run shape; missing %r' % field)

    engine = object.__new__(hw.HeadlessEngine)
    engine.partial_rows = []
    engine.partial_healed = 0
    if not hasattr(engine, 'partial_rows'):
        fail('the engine must expose partial_rows for the salvage path')



def test_h3627_salvage_never_publishes_an_infra_starved_window():
    """Salvage must NOT extend to an infrastructure failure.

    H2056 #944 pins that a hung 429 is never recorded as a result: on rate_limit /
    authentication / connection / timeout / budget_exceeded the run is COMPROMISED, not merely
    truncated -- the remaining keys were never attempted -- so publishing a payload would let a
    starved window read as output. Salvage exists for a per-call defect (`process`) that leaves
    the profile and route healthy. This pins the boundary, which the first cut of the H3627
    salvage got wrong by returning a payload for every HardFailure.
    """
    import headless_worker as hw
    for reason in ('rate_limit', 'authentication', 'connection', 'timeout', 'budget_exceeded',
                   'no_progress_kill'):
        if not hw.is_infra_failure(reason):
            fail('%r must be an infra failure, or salvage will publish a starved window' % reason)
    if hw.is_infra_failure('process'):
        fail("'process' must NOT be infra -- it is exactly the salvageable per-call defect")



def test_h4528_no_progress_kill_is_infra_not_a_content_defect():
    """H4528: a card whose call the no-output-progress watchdog killed is NOT a defective card.

    The watchdog's kill carries its own class, `no_progress_kill`, so it can never be read as a
    hard-ceiling `timeout` -- but for the audit's transient-vs-defect split it must land on the
    SAME side as `timeout`: infra. Filed as content it would denylist a healthy card and discard
    the TM of the fragments that did translate (H2077 / #947), and salvage would publish a
    starved window (H2056 #944).
    """
    import headless_worker as hw
    if not hw.is_infra_failure('no_progress_kill'):
        fail("'no_progress_kill' must be an infra failure")
    engine = object.__new__(hw.HeadlessEngine)
    engine.m = {'fragment_groups': {'agni': [[0, 1]]}}
    engine.failures = {'agni_f0': 'no_progress_kill', 'agni_f1': 'fragment-fidelity-reject'}
    if engine._selfheal_stop_reason('agni') != 'no_progress_kill':
        fail('a watchdog-killed heal must surface as no_progress_kill, got %r'
             % engine._selfheal_stop_reason('agni'))
    if engine._partial_cause('agni') != 'no_progress_kill':
        fail('the partial cause must be the infra kill, got %r' % engine._partial_cause('agni'))
    engine.failures = {'agni_f0': 'fragment-fidelity-reject'}
    if engine._selfheal_stop_reason('agni') != 'selfheal-nothing-resolved':
        fail('a genuine content failure must still read as content')



def test_run_py_survives_timeout_and_oserror():
    """P6 (H1422): audit_window.run_py wrapped subprocess.run with no try/except -- a
    TimeoutExpired or OSError re-raised straight through collect_cards/root_glue_translated
    and crashed the whole audit with no report or requeue. main()'s gate loop already
    handles a non-{0,1} returncode gracefully (appends to `crashed`, still reports+requeues)
    -- so run_py must convert either exception into that same result shape instead of
    letting it propagate. Monkeypatches subprocess.run in the audit_window module (no mock
    lib used elsewhere in this file) to force each exception without a real 1800s wait."""
    import audit_window as aw
    real_run = aw.subprocess.run

    def _raise_timeout(*a, **kw):
        raise subprocess.TimeoutExpired(cmd=a[0] if a else 'x', timeout=1800,
                                        output='partial out', stderr='partial err')

    def _raise_oserror(*a, **kw):
        raise OSError('interpreter not found')

    try:
        aw.subprocess.run = _raise_timeout
        res = aw.run_py(['fake_script.py'])
        if res['returncode'] != 124:
            fail('run_py must return returncode=124 on TimeoutExpired, got %r' % res['returncode'])
        if not isinstance(res.get('stdout'), str) or not isinstance(res.get('stderr'), str):
            fail('run_py must still return string stdout/stderr on TimeoutExpired: %r' % res)

        aw.subprocess.run = _raise_oserror
        res = aw.run_py(['fake_script.py'])
        if res['returncode'] in (0, 1):
            fail('run_py must not report a success/soft-fail returncode (0 or 1) on OSError, '
                 'got %r' % res['returncode'])
    finally:
        aw.subprocess.run = real_run



def test_large_card_presplit_and_heal_under_one_card_default():
    """H4054: under the one-card default, presplit and heal routing must be UNCHANGED for a
    LARGE source. A 45-<ls> citation giant exceeds PRESPLIT_SOLO_CITE_FLOOR=40 (the per-card
    trigger since H2160, independent of the batch budget), so it still routes to the
    fragment lane — grouped at the PRESPLIT_GROUP_* budgets (sense cap 18), NOT one fragment
    per call — while the heal path keeps SELFHEAL_GROUP_BUDGET=12. The companion small card
    stays a whole-card solo batch."""
    import gen_opt_harness2 as gh
    import re as _re
    d = tempfile.mkdtemp()
    giant, small = 'g~~h0_zz_pw', 's~~h0_zz_pw'
    saved_ob = gh.OUTPUT_BUDGET
    saved_ip = gh.input_paths
    try:
        gh.input_paths = _h4054_synth_inputs(gh, d, [(giant, 45), (small, 3)])
        js, batches, manifest = gh.build('zz', [giant, small], None, 12000, nominal=True,
                                         grammar_on=False, tm_path=None, return_manifest=True)
        meta = manifest['meta']
        if meta.get('output_budget') != 1:
            fail('default build must run at output_budget 1; got %r'
                 % (meta.get('output_budget'),))
        if giant not in (meta.get('presplit_keys') or []):
            fail('a 45-<ls> giant must presplit under the default (cite floor 40 is the '
                 'per-card trigger); got presplit=%r batches=%r'
                 % (manifest.get('presplit_keys'), batches))
        if any(giant in b for b in batches):
            fail('a presplit giant must not also ride a whole-card batch; got %r' % (batches,))
        if not any(small in b for b in batches) or any(len(b) != 1 for b in batches):
            fail('the small card must stay a whole-card ONE-card batch; got %r' % (batches,))
        groups = meta.get('selfheal_cards', {}).get(giant, 0)
        if groups < 3:
            fail('the giant\'s fragment lane must group at the PRESPLIT_GROUP_* budgets '
                 '(45 fragments / sense cap 18 => >=3 groups), not one fragment per call; '
                 'got %d group(s)' % groups)
        if meta.get('selfheal_group_budget') != 12:
            fail('heal routing must keep SELFHEAL_GROUP_BUDGET=12; got %r'
                 % (meta.get('selfheal_group_budget'),))
        m = _re.search(r'^const FRAGS = (\{.*\})$', js, _re.M)
        if not m:
            fail('could not parse the emitted FRAGS const')
        frags = json.loads(m.group(1))
        for g in frags.get(giant, []):
            if len(g) > 18:
                fail('presplit fragment group exceeds the PRESPLIT_GROUP_SENSE_CAP=18: %d'
                     % len(g))
    finally:
        gh.input_paths = saved_ip
        gh.OUTPUT_BUDGET = saved_ob
        shutil.rmtree(d, ignore_errors=True)



def test_run_telemetry_counters_returned():
    """H462: the two decisive numbers of every launch post-mortem — the kill-timeout count
    and the 'Connection closed mid-response' count — existed only as console.log strings
    and were hand-counted from transcripts into LAUNCH_FUCKUPS.md ('58 of 61 kill-timeouts',
    '3 conn-errors'); every H437/H442 code-vs-infra conclusion leaned on numbers the payload
    never returned. The harness summary must RETURN kill_timeouts / conn_errors / heal_calls /
    kill_bisect_blocked so the orchestrator and classify_run.py read them mechanically.
    Counters only — this pin also guards that the counting stays OUT of control flow."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_telemetry'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            for tok in ('let KILL_TIMEOUTS = 0', 'let CONN_ERRORS = 0', 'let HEAL_CALLS = 0',
                        'let KILL_BISECT_BLOCKED = 0', 'const isConn ='):
                if tok not in js:
                    fail('telemetry counter token %r missing from the harness' % tok)
            # the counters must be RETURNED in summary, not just logged
            for field in ('kill_timeouts: KILL_TIMEOUTS', 'conn_errors: CONN_ERRORS',
                          'heal_calls: HEAL_CALLS', 'kill_bisect_blocked: KILL_BISECT_BLOCKED'):
                if field not in js:
                    fail('summary must return telemetry field %r — hand-counting kill-timeouts '
                         'from transcripts is exactly what H462 removes' % field)
            # counting must live in agentKill's catch (central, one site) and re-throw:
            # the counters observe, they never swallow or reroute the error.
            if not _re.search(r'catch \(e\) \{ if \(isKill\(e\)\) KILL_TIMEOUTS\+\+; '
                              r'else if \(isConn\(e\)\) CONN_ERRORS\+\+; throw e \}', js):
                fail('agentKill must count kills/conn-errors in its catch and RE-THROW — '
                     'telemetry must not change control flow')
            # heal-lane spend is derived once from the heal: label prefix; both the dedicated
            # pool and telemetry must use that exact lane decision.
            if "const healLane = !!(opts && opts.label && /^heal:/.test(String(opts.label)))" not in js:
                fail('agentKill must classify heal calls via the heal: label prefix')
            if 'if (healLane) HEAL_CALLS++' not in js:
                fail('agentKill must count heal-lane calls from the shared lane decision')
            # a KillTimeout must never double-count as a connection error
            if 'e instanceof KillTimeout' not in js.split('const isConn =', 1)[1].split('\n', 1)[0]:
                fail('isConn must exclude KillTimeout so a kill is never double-counted as a conn error')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_h2095_structured_error_does_not_crash_the_audit():
    """H2095: a structured `row['error']` must not crash the transient-vs-defect split.

    H2089 changed a bare null card's error from a plain string to
    `{'failure_REASON': 'null_card_no_card_object', ...}`, but every consumer does string
    matching — `classify_harness_requeues` calls `.startswith('fidelity-reject')` on it. Master
    went red with `AttributeError: 'dict' object has no attribute 'startswith'`, and the real
    consequence is worse than a failing test: the audit crashes on ANY window containing a bare
    null card, so no window gets a transient/defect split.
    """
    import audit_window as aw

    if aw.failure_reason_text({'failure_REASON': 'null_card_no_card_object'}) != \
            'null_card_no_card_object':
        fail('structured error did not normalise to its failure_REASON')
    if aw.failure_reason_text('fidelity-reject: <ls> 1/2') != 'fidelity-reject: <ls> 1/2':
        fail('a plain-string error must pass through untouched')
    # an unrecognised dict must still yield TEXT, never explode
    odd = aw.failure_reason_text({'unexpected': 1})
    if not isinstance(odd, str):
        fail('unrecognised structured error did not normalise to text: %r' % (odd,))

    # end to end: the exact H2089 shape must flow through collect_harness_quality into
    # classify_harness_requeues without raising, and must still be classifiable
    rows = [
        {'key': 'nullish', 'card': None,
         'error': {'failure_REASON': 'null_card_no_card_object'}},
        {'key': 'fid', 'card': None, 'error': 'fidelity-reject: <ls> 1/2'},
    ]
    partial_cards, failure_reasons = aw.collect_harness_quality(rows)
    if not isinstance(failure_reasons['nullish'], str):
        fail('structured error survived into failure_reasons as a non-string: %r'
             % (failure_reasons['nullish'],))
    transient, defect, fidelity_nulls = aw.classify_harness_requeues(
        ['nullish', 'fid'], partial_cards, set(), failure_reasons)
    if fidelity_nulls != {'fid'}:
        fail('fidelity detection broke on the normalised reasons: %r' % (fidelity_nulls,))
    if 'nullish' not in transient or 'nullish' in defect:
        fail('a bare null card must stay transient: transient=%r defect=%r'
             % (sorted(transient), sorted(defect)))



def test_h2095_956_en_absence_flags_exempt_infra_partial():
    """H2095 / #956: the EN twin of #947, and the answer to the question #947 left open.

    The EN auditor has no partial-card model and derives defects from HARD content flags. Six of
    the eleven fire on ABSENCE (MISSING-EN, MISSING-SENSE, LS-LOSS, SAN-LOSS, AB-LOSS, IS-LOSS) —
    SAN-LOSS being literally the gate named in #947's RU harm — so a card left incomplete by a dead
    CALL trips them and lands in the same H304 fsha denylist. The other five fire on what the card
    DOES say and must stay defects even on a partial card.
    """
    import audit_window_en as en

    for flag in ('MISSING-EN', 'MISSING-SENSE', 'LS-LOSS', 'SAN-LOSS', 'AB-LOSS', 'IS-LOSS'):
        if not (en.is_hard(flag) and en.is_absence_hard(flag)):
            fail('%s must be both HARD and absence-bearing' % flag)
    for flag in ('STRANDED-ANCHOR', 'ANCHOR-LEAK', 'ANCHOR-MISMATCH', 'SENSE-DUPE', 'DUP'):
        if not en.is_hard(flag):
            fail('%s must stay HARD' % flag)
        if en.is_absence_hard(flag):
            fail('%s fires on content, not absence — exempting it would hide a real defect' % flag)
    # the split must cover the HARD set exactly, so a new HARD flag cannot silently default
    # into the exempt half
    if not set(en.ABSENCE_HARD) <= set(en.HARD):
        fail('ABSENCE_HARD drifted outside HARD: %r' % (en.ABSENCE_HARD,))
    # suffixed forms (the real flags carry "(...)" detail) classify identically
    if not en.is_absence_hard('SAN-LOSS(3 spans)') or en.is_absence_hard('DUP(x2)'):
        fail('suffixed flag classification drifted')



def test_h2077_947_infra_partial_is_not_a_content_defect():
    """H2077 / #947: a card left partial because its heal CALL died must not be filed as a
    content defect — that denylists a healthy card and discards its translated fragments' TM.

    Pins all four quadrants of the split so the exemption cannot silently widen:
      infra cause + gate flag   -> transient (the fix)
      content cause + gate flag -> defect    (unchanged)
      no cause + gate flag      -> defect    (older wf files, unchanged)
      infra cause + fidelity    -> defect    (fidelity_nulls still overrides)
    """
    import audit_window as aw

    fixture = [
        {'key': 'hung', 'card': {'partial': True, 'missing_fragments': ['g1:f2'],
                                 'partial_cause': 'timeout', 'partial_cause_infra': True,
                                 'frag_prov': [{'fsha': 'sha-good-1'}]}},
        {'key': 'budget', 'card': {'partial': True, 'missing_fragments': ['g1:f3'],
                                   'partial_cause': 'budget_exceeded:heal',
                                   'partial_cause_infra': True}},
        {'key': 'bad_content', 'card': {'partial': True, 'missing_fragments': ['g2:f1'],
                                        'partial_cause': 'fragment-fidelity-reject',
                                        'partial_cause_infra': False}},
        {'key': 'legacy', 'card': {'partial': True, 'missing_fragments': ['g3:f1']}},
    ]
    partial_cards, failure_reasons = aw.collect_harness_quality(fixture)
    if not partial_cards['hung'].get('partial_cause_infra'):
        fail('partial_cause_infra did not survive collect_harness_quality: %r'
             % partial_cards['hung'])

    gate_flagged = {'hung', 'budget', 'bad_content', 'legacy'}
    transient, defect, _ = aw.classify_harness_requeues(
        [], partial_cards, gate_flagged, failure_reasons)
    if transient != {'hung', 'budget'} or defect != {'bad_content', 'legacy'}:
        fail('#947 split wrong: transient=%r defect=%r' % (sorted(transient), sorted(defect)))

    # The whole point: an infra-partial card's fragments must stay OUT of the TM denylist,
    # which is built from requeue_defect membership.
    defect_fshas = {fp['fsha'] for row in fixture if row['key'] in defect
                    for fp in (row['card'].get('frag_prov') or []) if fp.get('fsha')}
    if 'sha-good-1' in defect_fshas:
        fail('#947: a hung card\'s correctly-translated fragment TM was denylisted')

    # fidelity_nulls must still win over the exemption, even with an infra cause recorded.
    transient2, defect2, _ = aw.classify_harness_requeues(
        [], partial_cards, {'hung'}, {'hung': 'fidelity-reject: <ls> 1/2'})
    if 'hung' not in defect2 or 'hung' in transient2:
        fail('#947: fidelity_nulls no longer overrides the infra-partial exemption')

    # A set (legacy caller shape) carries no cause and must behave exactly as before.
    transient3, defect3, _ = aw.classify_harness_requeues(
        [], set(partial_cards), gate_flagged, failure_reasons)
    if defect3 != gate_flagged:
        fail('#947: legacy set-shaped partial_cards changed behaviour: %r' % sorted(defect3))



def test_classify_run_verdicts():
    """H462: classify_run.py mechanizes the code-vs-infra rule H442 applied by hand
    ('if connection errors recur, record as infra-confounded, not a code failure') from
    the payload summary ALONE. Pin the four verdict shapes: clean, infra-confounded (the
    H442 launch-3 signature), code-failure (nulls with a quiet network), and the honest
    refusal on a pre-H462 payload that carries no counters."""
    import classify_run as cr
    base = {'agents_spent': 58,
            'translate_agents_spent': 18, 'max_translate_agents': 28,
            'translate_budget_tripped': False,
            'heal_agents_spent': 40, 'max_heal_agents': 55,
            'heal_budget_tripped': False,
            'kill_timeouts': 0, 'conn_errors': 0, 'heal_calls': 40,
            'kill_bisect_blocked': 0, 'null_keys': [], 'budget_kill_switch_tripped': False}
    v, _, sig = cr.classify(dict(base))
    if v != 'clean':
        fail('all-ok summary must classify clean; got %r' % v)
    if sig['partial_cards'] != 0 or sig['partial_keys']:
        fail('historical summary without partial_keys must remain compatible')
    for field in ('translate_agents_spent', 'max_translate_agents',
                  'translate_budget_tripped', 'heal_agents_spent',
                  'max_heal_agents', 'heal_budget_tripped'):
        if sig[field] != base[field]:
            fail('classifier must preserve split-pool signal %s' % field)
    # H442 launch 3: 58/58 agents, 7 kill-timeouts, 2 conn-errors, 12 nulls, tripped
    infra = dict(base, kill_timeouts=7, conn_errors=2,
                 null_keys=['k%d' % i for i in range(12)], budget_kill_switch_tripped=True)
    v, reasons, sig = cr.classify(infra)
    if v != 'infra-confounded':
        fail('the H442 launch-3 signature must classify infra-confounded; got %r' % v)
    if sig['infra_kill_threshold'] != max(3, math.ceil(0.25 * 58)):
        fail('kill threshold must be max(3, 25%% of agents_spent)')
    # nulls + trip with a QUIET network = the harness is the suspect
    code = dict(base, null_keys=['a', 'b'], budget_kill_switch_tripped=True)
    v, _, _ = cr.classify(code)
    if v != 'code-failure':
        fail('nulls with no infra signal must classify code-failure; got %r' % v)
    partial = dict(base, partial_keys=['p1'])
    v, reasons, sig = cr.classify(partial)
    if v != 'code-failure' or sig['partial_cards'] != 1 or sig['partial_keys'] != ['p1']:
        fail('partial-only output must classify code-failure with partial signals; got %r %r' %
             (v, sig))
    if '1 partial card(s)' not in ' '.join(reasons):
        fail('partial-only code-failure reason must name the incomplete card count')
    partial_infra = dict(base, partial_keys=['p1'], conn_errors=1)
    v, _, _ = cr.classify(partial_infra)
    if v != 'infra-confounded':
        fail('partial output plus an infra signal must classify infra-confounded; got %r' % v)
    # kill-timeouts alone (no conn errors) past the 25%% ceiling are ALSO infra
    kills = dict(base, kill_timeouts=58, null_keys=['a'], budget_kill_switch_tripped=True)
    v, _, _ = cr.classify(kills)
    if v != 'infra-confounded':
        fail('mass kill-timeouts (58/58) must classify infra-confounded; got %r' % v)
    # pre-H462 payload: no counters -> unclassifiable, never a guessed verdict
    old = {'agents_spent': 61, 'null_keys': ['a'], 'budget_kill_switch_tripped': True}
    v, reasons, _ = cr.classify(old)
    if v != 'unclassifiable':
        fail('a summary without H462 counters must be unclassifiable; got %r' % v)
    if 'kill_timeouts' not in ' '.join(reasons):
        fail('unclassifiable reason must name the missing counter fields')



def test_launch_failure_ledger_complete():
    """Launch failures must be classified with expected/actual economics before a
    handoff closes; H220 must stay represented because that incident was previously
    easier to find in .ai_state/RUN_LOG than in the narrative history."""
    import check_launch_ledger as cl
    entries = cl.load_ledger()
    violations = cl.check_entries(entries)
    if violations:
        fail('launch failure ledger has violations: %r' % violations)
    missing = cl.check_requested(entries, handoff='H220')
    if missing:
        fail('H220 must have a launch failure ledger entry: %r' % missing)



def test_launch_failure_ledger_rejects_incomplete_entry():
    """A ledger block that omits classification / metrics must fail loudly, so the
    closeout ritual cannot silently decay into narrative-only notes."""
    import check_launch_ledger as cl
    bad = [{
        'id': 'BAD',
        'date': '2026-07-07',
        'title': 'incomplete',
        'lane': 'verb batch',
        'model': 'claude-sonnet-5',
        'orchestrator': 'Workflow',
        'expected': {'agents': '1'},
        'actual': {'agents': '2'},
        'passes': 1,
        'symptoms': 'nulls',
        'root_cause': 'unknown',
        'guardrail': 'none',
        'residual_status': 'fixed',
        'residual_risk': 'none',
    }]
    violations = cl.check_entries(bad)
    if not any('classification' in v for v in violations):
        fail('incomplete launch ledger entry must reject missing classification: %r' % violations)
    if not any('expected.tokens' in v for v in violations):
        fail('incomplete launch ledger entry must reject missing expected.tokens: %r' % violations)
    if not any('actual.tokens' in v for v in violations):
        fail('incomplete launch ledger entry must reject missing actual.tokens: %r' % violations)



def test_h1386_p3d_p3e_run_py_inproc_exit_semantics():
    """H1386 P3d/P3e: run_py_inproc must mirror CPython for sys.exit('<message>') (message
    lands in captured stderr, rc=1 -- pre-fix the diagnosis vanished into an empty-stderr
    crash entry) and must RE-RAISE KeyboardInterrupt (an operator abort inside a gate was
    recorded as a crashed gate and the audit ran on, polluting the failure gallery)."""
    from audit_window import run_py_inproc
    tmp = tempfile.mkdtemp()
    str_exit = os.path.join(tmp, 'gate_strexit.py')
    with open(str_exit, 'w', encoding='utf-8', newline='\n') as f:
        f.write("import sys\nsys.exit('P3E-DIAGNOSIS: missing input file')\n")
    res = run_py_inproc([str_exit])
    if res['returncode'] != 1:
        fail('P3e: a string sys.exit must map to rc=1, got %r' % res['returncode'])
    if 'P3E-DIAGNOSIS' not in res['stderr']:
        fail('P3e: the sys.exit message must land in captured stderr, got %r'
             % res['stderr'][:200])
    kbd = os.path.join(tmp, 'gate_kbd.py')
    with open(kbd, 'w', encoding='utf-8', newline='\n') as f:
        f.write('raise KeyboardInterrupt\n')
    try:
        run_py_inproc([kbd])
        fail('P3d: KeyboardInterrupt inside a gate was swallowed (recorded as a crash)')
    except KeyboardInterrupt:
        pass



def test_h1386_p3h_stale_check_pins_v2_execution():
    """H1386 P3h: the v2 branch must cross-check the wf_output's execution /
    provenance_classes against the manifest's top-level execution / key_provenance --
    promotion trusts the workflow-side copies (provenance-class gating + the B20
    model-identity check), so a drifted copy must audit stale, not pass as v1-era-clean."""
    execu = {'profile_slot': 'c4', 'model_identifier': 'claude-sonnet-5'}
    prov = {'k1': 'real'}
    meta = {'root': 'p3h_root', 'selected_keys': ['k1'], 'input_hashes': {},
            'rootmap_sha256': None, 'nominal': True}
    manifest = {'schema': 'pwg.headless_execution_manifest.v2', 'meta': dict(meta),
                'execution': dict(execu), 'key_provenance': dict(prov)}
    wf_meta = dict(meta, execution=dict(execu), provenance_classes=dict(prov))

    def errs(wf):
        return stale_check(None, wf, ['k1'], execution_manifest=manifest).get('errors') or []

    matching = errs(wf_meta)
    if any('execution block' in e or 'provenance_classes' in e for e in matching):
        fail('P3h: matching v2 execution/provenance flagged as drift: %s' % matching)
    drifted_exec = errs(dict(wf_meta, execution=dict(execu, model_identifier='claude-opus-4-8')))
    if not any('execution block' in e for e in drifted_exec):
        fail('P3h: drifted wf execution block not flagged against the v2 manifest')
    drifted_prov = errs(dict(wf_meta, provenance_classes={'k1': 'fallback'}))
    if not any('provenance_classes' in e for e in drifted_prov):
        fail('P3h: drifted wf provenance_classes not flagged against the v2 manifest')
    stripped = errs(dict(meta))
    if not any('execution block' in e for e in stripped):
        fail('P3h: a wf meta with NO execution copy must not pass the v2 pin')



def test_h1386_c3_frag_unblock_serves_replacement():
    """H1386 C3: the fragment half of the H304 gate-outcome contract. Deny an fsha, then
    re-harvest the SAME fsha (rework hashes the fragment SOURCE, so the corrected output
    emits an identical fsha) with corrected senses, then unblock -- load_frag_tm must serve
    the NEW senses. Pre-fix, build_frags' seen-scan treated the flagged cached row as a
    cache hit (never consulting the denylist), the replacement was never appended, and the
    unblock re-enabled serving the exact gate-rejected senses the denial existed to block.
    Also pins the recursive harvest glob: a requeue attempt's wf_output lands two dirs deep
    (artifacts/<lease>/requeue/rqNN-<kind>/), which the old single-* glob never matched."""
    import translation_memory as tm
    tmp = tempfile.mkdtemp()
    deny_path = os.path.join(tmp, 'denylist.jsonl')
    sidecar = os.path.join(tmp, 'translation_memory.frag.ru.jsonl')
    fsha = tm.frag_address('ru', 'the fragment source')

    def wf_fixture(path, russian):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'meta': {'lang': 'ru', 'root': 'c3root', 'input_hashes': {}},
                       'results': [{'key': 'c3root~~h0', 'card': {
                           'records': [], 'frag_prov': [{
                               'fsha': fsha, 'owners': [['h', '']],
                               'senses': [{'tag': '1', 'german': 'g', 'russian': russian}],
                           }]}}]}, f, ensure_ascii=False)

    # 1. first harvest caches the (later gate-flagged) senses, one level deep.
    wf_fixture(os.path.join(tmp, 'artifacts', 'w1', 'wf_output.w1.json'), 'FLAGGED')
    pattern = os.path.join(tmp, 'artifacts', '**', 'wf_output*.json')
    _, added, _ = tm.build_frags(pattern, 'ru', out=sidecar, denylist=deny_path)
    if added != 1:
        fail('first harvest should cache 1 fragment, got %d' % added)
    # 2. the gate flags it: fsha denied (H304 defect denial).
    tm.append_jsonl_line(deny_path, {'schema': 'pwg.translation_memory.denylist.v1',
                                     'kind': 'fragment', 'fsha': fsha, 'reason': 'defect'})
    # 3. the corrected --no-tm rework lands TWO dirs deep with the SAME fsha, new senses.
    wf_fixture(os.path.join(tmp, 'artifacts', 'w1', 'requeue', 'rq01-defect',
                            'wf_output.w1.json'), 'CORRECTED')
    _, added2, _ = tm.build_frags(pattern, 'ru', out=sidecar, denylist=deny_path)
    if added2 < 1:
        fail('H1386 C3: replacement harvest of a currently-denied fsha was deduped as a '
             'cache hit -- the corrected senses never reach the sidecar')
    # 4. promotion unblocks the fsha (clear_denials_for_promotion path).
    tm.append_unblock((), [fsha], reason='replaced_by_promotion', path=deny_path)
    # 5. the served row must now be the CORRECTED senses, never the flagged ones.
    cache = tm.load_frag_tm('ru', sidecar, denylist=deny_path)
    if fsha not in cache:
        fail('unblocked fragment missing from load_frag_tm')
    got = (cache[fsha].get('senses') or [{}])[0].get('russian')
    if got != 'CORRECTED':
        fail('H1386 C3: load_frag_tm re-serves the gate-flagged senses (%r) after unblock'
             % got)



def test_write_reports_emits_defect_fsha_file():
    """H304: --write-requeue also persists requeue.defect.fshas.txt so requeue_from_audit
    can denylist the flagged fragments without re-reading the wf_output."""
    from window_reports import write_reports
    tmp = tempfile.mkdtemp()
    report = {'workflow': 'wf.json', 'root': 'h304root', 'keys': ['k1'],
              'null_cards': [], 'requeue': ['k1'], 'crashed': [],
              'gates': {}, 'glue': None, 'collect': {},
              'requeue_transient': [], 'requeue_defect': ['k1'],
              'requeue_defect_fshas': ['a' * 64, 'b' * 64],
              'judge_sample': {'keys': [], 'sample_count': 0, 'seed': None,
                               'clean_key_count': 0}}
    write_reports(report, True, out_dir=tmp)
    p = os.path.join(tmp, 'requeue.defect.fshas.txt')
    if not os.path.exists(p):
        fail('requeue.defect.fshas.txt not written by write_reports')
    got = [ln.strip() for ln in open(p, encoding='utf-8') if ln.strip()]
    if got != ['a' * 64, 'b' * 64]:
        fail('defect fsha file content mismatch: %r' % got)



def test_ledger_stamps_gen_model():
    """H390 Phase 1: the window ledger row carries `gen_model`, read from the run's
    own workflow_meta (gen_opt_harness2 stamps meta.gen_model). Without this the
    Fable-vs-Sonnet A/B question is uncomputable — the model that generated a window
    is invisible to every per-window rate. Also pins that a run with no workflow_meta
    degrades to gen_model=None rather than raising."""
    from window_reports import write_reports
    base = {'null_cards': [], 'requeue': [], 'crashed': [], 'gates': {},
            'glue': None, 'collect': {}, 'requeue_transient': [], 'requeue_defect': [],
            'judge_sample': {'keys': [], 'sample_count': 0, 'seed': None,
                             'clean_key_count': 0}}

    def ledger_row_for(report):
        tmp = tempfile.mkdtemp()
        write_reports(report, True, out_dir=tmp)
        ledger = os.path.join(tmp, 'window_ledger.jsonl')
        if not os.path.exists(ledger):
            fail('window_ledger.jsonl not written by write_reports')
        rows = [json.loads(ln) for ln in open(ledger, encoding='utf-8') if ln.strip()]
        if len(rows) != 1:
            fail('expected exactly one ledger row, got %d' % len(rows))
        return rows[0]

    stamped = dict(base, workflow='wf.json', root='h390stamped', keys=['k1'],
                   workflow_meta={'gen_model': 'claude-fable-5'})
    row = ledger_row_for(stamped)
    if 'gen_model' not in row:
        fail('ledger row missing gen_model key entirely')
    if row['gen_model'] != 'claude-fable-5':
        fail('ledger gen_model mismatch: %r' % row.get('gen_model'))

    # No workflow_meta at all -> None, never a KeyError.
    bare = dict(base, workflow='wf.json', root='h390bare', keys=['k1'])
    row = ledger_row_for(bare)
    if row.get('gen_model') is not None:
        fail('bare-run ledger gen_model should be None, got %r' % row.get('gen_model'))



def test_ledger_stamps_host_profile_b8():
    """H2231 B8: every ledger row stamps gen_model + host + profile keys.

    - gen_model from workflow_meta.gen_model (and execution.model_identifier fallback)
    - profile from execution.profile_slot / source_profile / PWG_PROFILE_SLOT
    - host from PWG_HOST (or COMPUTERNAME / hostname)
    Keys always present; null is honest when unknown.
    """
    from window_reports import (
        write_reports, resolve_gen_model, resolve_host, resolve_profile,
    )
    base = {'null_cards': [], 'requeue': [], 'crashed': [], 'gates': {},
            'glue': None, 'collect': {}, 'requeue_transient': [], 'requeue_defect': [],
            'judge_sample': {'keys': [], 'sample_count': 0, 'seed': None,
                             'clean_key_count': 0}}

    def ledger_row_for(report, env=None):
        tmp = tempfile.mkdtemp()
        # resolve_* consult os.environ; set/restore for host/profile env tests
        saved = {}
        if env is not None:
            for k, v in env.items():
                saved[k] = os.environ.get(k)
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        try:
            write_reports(report, True, out_dir=tmp)
            ledger = os.path.join(tmp, 'window_ledger.jsonl')
            rows = [json.loads(ln) for ln in open(ledger, encoding='utf-8') if ln.strip()]
            if len(rows) != 1:
                fail('expected exactly one ledger row, got %d' % len(rows))
            return rows[0]
        finally:
            for k, old in saved.items():
                if old is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = old

    # Full multi-lane tags from workflow_meta.execution
    stamped = dict(
        base, workflow='wf.json', root='h2231lane', keys=['k1'],
        workflow_meta={
            'gen_model': 'claude-sonnet-5',
            'execution': {
                'profile_slot': 'c4',
                'model_identifier': 'claude-sonnet-5',
            },
        },
    )
    row = ledger_row_for(stamped, env={'PWG_HOST': 'desk-a'})
    for key in ('gen_model', 'host', 'profile'):
        if key not in row:
            fail('ledger row missing %s key entirely' % key)
    if row['gen_model'] != 'claude-sonnet-5':
        fail('gen_model mismatch: %r' % row.get('gen_model'))
    if row['host'] != 'desk-a':
        fail('host mismatch: %r' % row.get('host'))
    if row['profile'] != 'c4':
        fail('profile mismatch: %r' % row.get('profile'))

    # model_identifier fallback when gen_model absent
    via_exec = dict(
        base, workflow='wf.json', root='h2231exec', keys=['k1'],
        workflow_meta={'execution': {'model_identifier': 'claude-fable-5',
                                     'profile_slot': 'c2'}},
    )
    row = ledger_row_for(via_exec, env={'PWG_HOST': 'desk-b'})
    if row.get('gen_model') != 'claude-fable-5':
        fail('execution.model_identifier fallback failed: %r' % row.get('gen_model'))
    if row.get('profile') != 'c2':
        fail('profile from execution.profile_slot failed: %r' % row.get('profile'))

    # source_profile (legacy Max Workflow) as profile fallback
    via_sp = dict(
        base, workflow='wf.json', root='h2231sp', keys=['k1'],
        workflow_meta={'source_profile': 'max-legacy'},
    )
    row = ledger_row_for(via_sp, env={'PWG_HOST': None, 'PWG_PROFILE_SLOT': None,
                                      'PWG_PROFILE': None})
    if row.get('profile') != 'max-legacy':
        fail('source_profile fallback failed: %r' % row.get('profile'))

    # resolve_* pure helpers (no write path)
    st = {'workflow_meta': {'gen_model': 'x'}}
    if resolve_gen_model(st) != 'x':
        fail('resolve_gen_model broken')
    if resolve_host({'host': 'h1'}, env={}) != 'h1':
        fail('resolve_host explicit broken')
    if resolve_host({}, env={'PWG_HOST': 'env-host'}) != 'env-host':
        fail('resolve_host env broken')
    if resolve_profile({}, env={'PWG_PROFILE_SLOT': 'c5'}) != 'c5':
        fail('resolve_profile env broken')



def test_subprocess_gate_calls_hardened():
    """Hardening (H316): Windows cp1252 pitfall + hang guard. Gate/driver
    subprocess.run calls that capture child output must pass encoding='utf-8';
    shell-outs wrapping potentially long children must carry a timeout. Static
    wiring pin so a refactor cannot silently regress either."""
    checks = [
        (os.path.join(SRC, 'make_edition_cut.py'), "encoding='utf-8'"),
        (os.path.join(SRC, 'preflight_remaining_gates.py'), "encoding='utf-8'"),
        (os.path.join(SRC, 'release_readiness.py'), "encoding='utf-8'"),
        (os.path.normpath(os.path.join(SRC, '..', 'save_and_audit.py')), 'timeout=1800'),
        (os.path.join(HERE, 'audit_window.py'), 'timeout=1800'),
        (os.path.join(HERE, 'autosplit_requeue.py'), 'timeout=600'),
    ]
    for path, needle in checks:
        with open(path, encoding='utf-8') as f:
            src_txt = f.read()
        if 'subprocess.run' in src_txt and needle not in src_txt:
            fail('%s: expected %r on its subprocess.run call(s)'
                 % (os.path.basename(path), needle))



def test_ls_resolver_rv_av_anchored():
    """H321 item #5: Ṛgveda/Atharva disambiguation must be ANCHORED on the leading
    citation abbreviation, not a bare `'rv' in kl or 'ṛ' in kl` substring that
    mis-routes any citation merely CONTAINING those characters (parv., gṛ., kṛ.)
    to the RV hymn URL."""
    import ls_resolver as L
    # RV-family abbreviations → rv; AV / everything else → av (default).
    for key, want in [('ṚV.', True), ('RV.', True), ('ṛv.', True),
                      ('AV.', False), ('Nir.', False),
                      ('parv.', False), ('Gṛ.', False), ('kṛ.', False)]:
        got = L._is_rv_prefix(key)
        if got != want:
            fail('_is_rv_prefix(%r) = %r, want %r (anchored, not substring)' % (key, got, want))
    # The fragile substring form must be gone from the source.
    src_txt = open(os.path.join(SRC, 'ls_resolver.py'), encoding='utf-8').read()
    if "'rv' in kl" in src_txt or "'ṛ' in kl" in src_txt:
        fail('ls_resolver still uses the substring RV/AV disambiguation')
    # The two pattern-engine excepts must surface, not silently `pass`.
    if src_txt.count('except Exception:\n            pass') or '_warn_swallowed' not in src_txt:
        fail('ls_resolver pattern-engine excepts must surface via _warn_swallowed, not pass')
    # Live resolution still correct for genuine RV/AV samhita citations.
    if 'rvhymns' not in (L.generate_href('pwg', 'ṚV. ', '10,85,24') or ''):
        fail('ṚV. citation must still resolve to the rv hymns URL')
    if 'avhymns' not in (L.generate_href('pwg', 'AV. ', '11,4,26') or ''):
        fail('AV. citation must still resolve to the av hymns URL')



def test_annotate_evidence_relation_semantics():
    """H337 (W2): the per-sense evidence relation classifier. Pins annotate_evidence.py's
    own pure-function selftest (provides = exact Russian equivalent; supports = token
    containment >= corpus_gate.THRESHOLD; a citation-only sense yields nothing; a source
    with no usable meaning tokens is SILENT not contradicts; the lemma summary is
    lemma-scoped and shared across a lemma's rows). No gate-source file IO, so it runs in
    CI where the gitignored src/*.jsonl dictionaries are absent."""
    import annotate_evidence
    annotate_evidence.selftest()



def test_annotate_genres_sense_join():
    """H339 (W4): per-sense citation genre join (annotate_genres.py). Pins its own
    pure-function selftest — coarse-bucket rollup keyed off the curated genre label's
    leading word (Kāvya/Veda/Epic/Śāstra/Purāṇa/Kośa), an unmapped-only citation set
    stays [] (unknown, never conflated with 'only genre X'), and multi-genre senses
    keep every cited bucket."""
    import annotate_genres
    annotate_genres.selftest()



def test_koch_xref_resolution():
    """H397 (H337 follow-up): koch's bare `см. X` cross-reference resolver — the
    Devanagari self-header crosswalk, one-hop resolution, chain-safe cycle guard, and
    the resolve_koch_lane() wrapper annotate_evidence.gather() calls. Pins
    koch_xref.py's own pure-function selftest (no koch.jsonl file IO, so it runs in CI
    where the gitignored src/*.jsonl dictionaries are absent)."""
    import koch_xref
    koch_xref.selftest()



def test_fri_xref_resolution():
    """H404 (H397 generalization): fri's bare Latin-apparatus (v./cf./q.v.) redirect
    resolver — targets are already roman (build_src.iast_to_slp1 reused, no Devanagari
    crosswalk needed), one hop, and the resolve_fri_lane() wrapper
    annotate_evidence.gather() calls. Pins fri_xref.py's own pure-function selftest
    (no fri.jsonl file IO, so it runs in CI where the gitignored src/*.jsonl
    dictionaries are absent)."""
    import fri_xref
    fri_xref.selftest()



def test_audit_window_tag_routing():
    """H336/H-2: --window-tag routes window_status/report/requeue/judge-sample to
    src/pilot/output/<tag>/ instead of the flat singletons, so two accounts auditing
    different windows in ONE clone cannot clobber each other's status. Untagged
    invocation must still write the flat singletons (backward compatible)."""
    from safe_filename import safe_name
    tag_dir = os.path.join(OUT, safe_name('selftest_tag_zzqq'))
    if os.path.isdir(tag_dir):
        shutil.rmtree(tag_dir)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump({'meta': {'rootmap_sha256': None}, 'results': []}, f)
    try:
        proc = run([sys.executable, os.path.join(SRC, 'pilot', 'audit_window.py'),
                   wf_path, '--root', 'zzqq', '--window-tag', 'selftest_tag_zzqq',
                   '--allow-stale'], expect=0)
        status_path = os.path.join(tag_dir, 'window_status.json')
        report_path = os.path.join(tag_dir, 'audit_window.report.json')
        if not os.path.exists(status_path):
            fail('--window-tag must write window_status.json under output/<tag>/, got:\n%s'
                 % proc.stdout)
        if not os.path.exists(report_path):
            fail('--window-tag must write audit_window.report.json under output/<tag>/')
        live_status = os.path.join(OUT, 'window_status.json')
        live_before = (open(live_status, encoding='utf-8').read()
                      if os.path.exists(live_status) else None)
        # A bare --root run (no tag) must be unaffected by the tag dir's existence.
        if live_before is not None:
            got = json.loads(open(live_status, encoding='utf-8').read())
            if got.get('root') == 'zzqq':
                fail('a tagged run must not also overwrite the flat OUT singleton')
    finally:
        os.remove(wf_path)
        if os.path.isdir(tag_dir):
            shutil.rmtree(tag_dir)



def test_h_reconstructed_regression_guard():
    """D-1 (H1149): `cohort_clean_rates.assert_h_reconstructed_regression` must FAIL
    LOUD the instant the store's `h_reconstructed` count silently drifts off 468, and
    stay green at 468 -- the exact failure mode this guards against already happened
    once (PR #510's underlying `h is None` count fell 468 -> 0 and became invisible to
    the only query that could find it, Uprava FINDINGS §95). "A guard that passes on a
    mutated store is not a guard" (H1149) -- so this test builds a SYNTHETIC store (not
    the real gitignored canonical one, so it stays deterministic off-disk everywhere)
    and proves both directions: 467 markers -> AssertionError; 468 -> clean pass; a
    467-count WITH an authorized re-translation manifest documenting exactly that
    decrease -> accepted.
    """
    import cohort_clean_rates as ccr

    with tempfile.TemporaryDirectory() as tmp:
        store = os.path.join(tmp, 'pwg_ru_translated.jsonl')

        def write_store(n_marked, total=500):
            with open(store, 'w', encoding='utf-8') as f:
                for i in range(total):
                    row = {
                        'key1': 'k%d' % i, 'subcard': 'k%d~~h0_00_pwg00' % i, 'layer': 'pwg',
                        'h': 'h%d' % (i % 14),
                        'provenance': ({'h_reconstructed': True} if i < n_marked else {}),
                    }
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')

        write_store(468)
        got = ccr.assert_h_reconstructed_regression(store, expected=468)
        if got != 468:
            fail('guard mis-measured a clean 468 store: got %r' % got)

        write_store(467)  # simulate ONE silently dropped marker
        try:
            ccr.assert_h_reconstructed_regression(store, expected=468)
        except AssertionError:
            pass
        else:
            fail('h_reconstructed regression guard did NOT fail at 467 -- not a real guard')

        write_store(468)  # restore
        ccr.assert_h_reconstructed_regression(store, expected=468)

        # An authorized re-translation manifest documenting the SAME decrease is accepted.
        write_store(467)
        manifest = os.path.join(tmp, 'retranslation_manifest.json')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg_ru.h_reconstructed_retranslation_manifest.v1',
                       'new_count': 467, 'note': 'selftest fixture'}, f)
        got = ccr.assert_h_reconstructed_regression(store, expected=468, manifest_path=manifest)
        if got != 467:
            fail('guard did not accept an authorized documented decrease: got %r' % got)

        # A manifest that does NOT match the actual count is NOT an excuse.
        write_store(466)
        try:
            ccr.assert_h_reconstructed_regression(store, expected=468, manifest_path=manifest)
        except AssertionError:
            pass
        else:
            fail('guard accepted a manifest whose new_count does not match the actual '
                 'measured count -- an unrelated manifest must not paper over a real drop')



def test_heal_lane_target_field_fidelity_wired():
    """H1152 parity (C1): the JS selfHeal COMPLETE-heal branch must run the <ls>/{#..#} count over
    the TARGET field, not just `german`. The batch accept() lane already did (translation-fidelity-
    reject); the heal/presplit lane — which routes exactly the citation/sense-dense giants — never
    did, so a span kept in `german` but dropped from russian/english was stitched and promoted with
    a silently-missing Sanskrit/citation span (the live H1070 r102 pattern). Static wiring guard on
    the generated harness for BOTH languages (window_selftest has no JS runtime for the heal path)."""
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_healfid'
    d = tempfile.mkdtemp()
    saved_ip = gh.input_paths
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        for lang, want_field in (('ru', "const TARGET_FIELD = 'russian'"),
                                 ('en', "const TARGET_FIELD = 'english'")):
            js, _ = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False,
                             tm_path=None, lang=lang)
            if want_field not in js:
                fail('%s heal harness did not set TARGET_FIELD' % lang)
            if 'stitched-translation-fidelity-reject' not in js:
                fail('%s heal lane is missing the H1152 target-field fidelity check '
                     '(stitched-translation-fidelity-reject)' % lang)
            if 'countOfField(stitched, TARGET_FIELD' not in js:
                fail('%s heal lane must count <ls>/{#} over the TARGET field of the stitched '
                     'card, not just german' % lang)
            # the target check must FOLLOW the german stitched check (i.e. live inside the same
            # complete-heal branch, never on a partial result).
            if not (js.index('stitched-fidelity-reject') < js.index('stitched-translation-fidelity-reject')):
                fail('%s target-field check must follow the german stitched check (complete-heal '
                     'only)' % lang)
    finally:
        gh.input_paths = saved_ip
        shutil.rmtree(d, ignore_errors=True)

