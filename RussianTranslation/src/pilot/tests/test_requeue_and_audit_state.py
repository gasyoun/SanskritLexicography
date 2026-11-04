"""test_requeue_and_audit_state — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_requeue_and_audit_state.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_semantic_risk_checker():
    clean_card = {
        'key': 'ap',
        'card': {
            'key1': 'ap',
            'iast': 'ap',
            'records': [{
                'h': '2',
                'grammar': 'f.',
                'senses': [{
                    'tag': '1',
                    'german': 'Wasser, Gewässer',
                    'russian': 'вода, воды',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': 'Vedic',
                    'differentia': 'вода — основной корпусный перевод; воды — pluralia tantum.',
                }, {
                    'tag': '2',
                    'german': 'Amarakośa: Stern',
                    'russian': 'звезда',
                    'equivalence_type': 'equivalent',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    clean = audit_card_result(clean_card)
    if clean['risk_count']:
        fail('clean semantic-risk fixture produced risks: %s' %
             ', '.join(r['id'] for r in clean['risks']))

    bad_card = {
        'card': {
            'key1': 'agni',
            'iast': 'agni',
            'corpus_synonyms': {'candidates': ['огонь', 'пламя']},
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': 'Feuer, Brand',
                    'russian': 'agni der',
                    'stratum': '',
                }],
            }, {
                'h': '2',
                'grammar': 'm.',
                'senses': [{
                    'tag': '2',
                    'german': 'Glanz',
                    'russian': 'agni der',
                    'equivalence_type': 'equivalent',
                    'source_type': 'lexicographic',
                    'stratum': 'Epic',
                    'differentia': '',
                }, {
                    'tag': '3',
                    'german': '{%Schein%}',
                    'russian': 'agni der',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    ids = {risk['id'] for risk in semantic_risks(bad_card)}
    expected = {
        'missing_required_sense_field',
        'missing_equivalence_type',
        'missing_source_type',
        'untranslated_german_residue',
        'collapsed_synonym_string',
        'likely_circular_gloss',
        'identical_russian_glosses',
        'missing_apresjan_discrimination',
        'suspicious_attested_without_text_signal',
        'suspicious_lexicographic_with_text_signal',
    }
    if not expected.issubset(ids):
        fail('semantic-risk checker missed: %s' % ', '.join(sorted(expected - ids)))

    formula_card = {
        'card': {
            'key1': 'iti',
            'iast': 'iti',
            'records': [{
                'h': '1',
                'grammar': 'ind.',
                'senses': [{
                    'tag': '1',
                    'german': 'iti arthaḥ',
                    'russian': 'смысл',
                    'equivalence_type': 'explanatory',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }, {
                    'tag': '2',
                    'german': 'iti śeṣaḥ',
                    'russian': 'остаток',
                    'equivalence_type': 'explanatory',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    formula_ids = {risk['id'] for risk in semantic_risks(formula_card)}
    if not {'formula_iti_arthah', 'formula_iti_sesah'}.issubset(formula_ids):
        fail('formula semantic-risk fixture missed fixed-rendering findings')



def test_semantic_review_prioritizer():
    high = {
        'key': 'high',
        'card': {
            'key1': 'high',
            'iast': 'high',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    # B13 (H1339): the siglum-leak fixture is CITATION-SHAPED («Ригведа 1,1»
                    # -- work name + numeric locator), matching the narrowed trigger; a bare
                    # prose «Ригведа» with no locator is now legitimate prose, not a leak.
                    'german': '<ls>ṚV.</ls> 1,1 Feuer',
                    'russian': 'мужской Ригведа 1,1 {#agni',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': 'Vedic',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    medium = {
        'key': 'medium',
        'card': {
            'key1': 'medium',
            'iast': 'medium',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': 'Glanz, Schimmer',
                    'russian': 'блеск',
                    'equivalence_type': 'equivalent',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    low = {
        'key': 'low',
        'card': {
            'key1': 'low',
            'iast': 'low',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': 'Schein',
                    'russian': 'свет',
                    'equivalence_type': '',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    formula = {
        'key': 'formula',
        'card': {
            'key1': 'formula',
            'iast': 'formula',
            'records': [{
                'h': '1',
                'grammar': 'ind.',
                'senses': [{
                    'tag': '1',
                    'german': 'iti arthaḥ',
                    'russian': 'смысл',
                    'equivalence_type': 'explanatory',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'results': [medium, low, high, formula]}, f, ensure_ascii=False)
    try:
        report = audit_cards(path, review_limit=3)
        queue = report['review_queue']['items']
        queued_keys = [item['key'] for item in queue]
        if queued_keys[0] != 'high' or 'low' in queued_keys:
            fail('review queue did not prioritize high/medium risk before low risk')
        high_ids = {risk['id'] for card in report['cards'] if card['key'] == 'high'
                    for risk in card['risks']}
        expected_high = {
            'translated_grammar_siglum',
            'translated_source_siglum',
            'unbalanced_sanskrit_delimiters',
        }
        if not expected_high.issubset(high_ids):
            fail('markup/sigla leakage fixture missed: %s' %
                 ', '.join(sorted(expected_high - high_ids)))
        inv = {row['id']: row for row in report['formula_inventory']}
        if inv['formula_iti_arthah']['occurrences'] != 1 or inv['formula_iti_arthah']['missing_rendering'] != 1:
            fail('formula inventory did not count missing iti arthaḥ rendering')
        run([sys.executable, os.path.join(SRC, 'pilot', 'prompt_rule_audit.py'),
             '--cards', path, '--fail-on-high-risk'], expect=1)
    finally:
        os.remove(path)



def test_noisy_source_type_not_requeue():
    # A sense that DOES assert a meaning ({%..%} gloss span) but is marked attested with no
    # citation/stratum/lexicographic signal is the genuine review target — it must produce
    # the hint yet never enter the requeue set (REPORT_ONLY_RISKS, F-gate-nws-fp).
    noisy = {
        'key': 'noisy',
        'card': {
            'key1': 'noisy',
            'iast': 'noisy',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': '{%Glanz%}',
                    'russian': 'блеск',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'results': [noisy]}, f, ensure_ascii=False)
    try:
        report = audit_cards(path, review_limit=3)
        ids = {risk['id'] for card in report['cards'] for risk in card['risks']}
        if 'suspicious_attested_without_text_signal' not in ids:
            fail('noisy source-type fixture did not produce expected review hint')
        if report.get('high_confidence_count') or report.get('requeue_keys'):
            fail('source-type review hint became high-confidence/requeue')
    finally:
        os.remove(path)



def test_report_only_risks_never_requeue():
    """The report-only semantic hints must be structurally barred from the requeue set:
    disjoint from HIGH_CONFIDENCE_RISKS (the only thing requeue_keys is built from)."""
    from prompt_rule_audit import HIGH_CONFIDENCE_RISKS, REPORT_ONLY_RISKS
    overlap = REPORT_ONLY_RISKS & HIGH_CONFIDENCE_RISKS
    if overlap:
        fail('REPORT_ONLY_RISKS leaked into the requeue-driving set: %s'
             % ', '.join(sorted(overlap)))
    if 'suspicious_attested_without_text_signal' not in REPORT_ONLY_RISKS:
        fail('suspicious_attested_without_text_signal must be report-only')



def test_attested_text_signal_redesign():
    """FL5 redesign of suspicious_attested_without_text_signal:
    - a pure cross-reference / erratum sense (no {%..%} gloss span) never fires, even with
      no card-level signal (it asserts no meaning to attest);
    - a lexicographic citation counts as a text signal for an attested meaning;
    - a real meaning gloss ({%..%}) marked attested with zero signal still fires (kept)."""
    def ids_for(sense):
        card = {'key': 'x', 'card': {'key1': 'x', 'iast': 'x', 'records': [
            {'h': '1', 'grammar': 'verb', 'senses': [sense]}]}}
        return {r['id'] for r in semantic_risks(card)}

    FLAG = 'suspicious_attested_without_text_signal'

    # 1) Cross-reference sense: {#paryanu#} <ab>s.</ab> {#paryanubanDa#} — no gloss span.
    crossref = {'tag': '1', 'german': '<div n="p">— {#paryanu#} <ab>s.</ab> {#paryanubanDa#} .',
                'russian': '<div n="p">— {#paryanu#} <ab>s.</ab> {#paryanubanDa#} .',
                'equivalence_type': 'explanatory', 'source_type': 'attested',
                'stratum': '', 'differentia': ''}
    if FLAG in ids_for(crossref):
        fail('cross-reference sense (no meaning claim) wrongly flagged as attested-without-signal')

    # 2) Erratum sense: <ab>Z.</ab> 3 lies ... — no gloss span, editorial correction.
    erratum = {'tag': 'corr', 'german': '<hom>1.</hom> {#nI#}¦ <ab>Z.</ab> 19. Lies: 3 <ab>st.</ab> 8.<info n="rev"/>',
               'russian': 'читай: 3 вместо 8', 'equivalence_type': 'explanatory',
               'source_type': 'attested', 'stratum': '', 'differentia': ''}
    if FLAG in ids_for(erratum):
        fail('erratum sense (no meaning claim) wrongly flagged as attested-without-signal')

    # 3) Lexicographic citation grounds an attested meaning gloss -> no flag.
    lexcite = {'tag': '1', 'german': 'Amarakośa: {%Stern%}', 'russian': 'звезда',
               'equivalence_type': 'equivalent', 'source_type': 'attested',
               'stratum': '', 'differentia': ''}
    if FLAG in ids_for(lexcite):
        fail('attested meaning with a lexicographic citation wrongly flagged')

    # 4) Genuine target survives: a {%..%} meaning gloss, attested, with no signal at all.
    genuine = {'tag': '1', 'german': '<lex>adj.</lex> {%sich rasch bewegend, eilend%}',
               'russian': '<lex>adj.</lex> {%быстро движущийся%}', 'equivalence_type': 'equivalent',
               'source_type': 'attested', 'stratum': '', 'differentia': ''}
    if FLAG not in ids_for(genuine):
        fail('a genuine attested meaning gloss without any signal must still surface the hint')



def test_stale_refusal_preserves_requeue():
    os.makedirs(OUT, exist_ok=True)
    requeue_path = os.path.join(OUT, 'requeue.keys.txt')
    old = open(requeue_path, encoding='utf-8').read() if os.path.exists(requeue_path) else None
    sentinel = 'SELFTEST_SENTINEL\n'
    with open(requeue_path, 'w', encoding='utf-8') as f:
        f.write(sentinel)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump({'results': [{'key': 'not-current', 'card': {'ok': True}}]}, f)
    try:
        run([sys.executable, os.path.join(SRC, 'pilot', 'audit_window.py'),
             wf_path, '--root', 'sTA', '--write-requeue'], expect=2)
        got = open(requeue_path, encoding='utf-8').read()
        if got != sentinel:
            fail('stale audit overwrote requeue.keys.txt')
    finally:
        os.remove(wf_path)
        if old is None:
            try:
                os.remove(requeue_path)
            except FileNotFoundError:
                pass
        else:
            with open(requeue_path, 'w', encoding='utf-8') as f:
                f.write(old)



def test_fixture_audit_does_not_clobber_live_status():
    """FL8: a fixture/self-test audit run must NEVER overwrite the live singleton status files
    (window_status.json / audit_window.report.json). A temp-file wf auto-enables the guard, and
    --ephemeral forces it; either way the live OUT singletons are byte-identical afterward."""
    live = [os.path.join(OUT, 'window_status.json'),
            os.path.join(OUT, 'audit_window.report.json'),
            os.path.join(OUT, 'window_ledger.jsonl')]

    def snap(p):
        return open(p, 'rb').read() if os.path.exists(p) else None

    before = {p: snap(p) for p in live}
    fixture = {'meta': {'root': 'zzfixture'}, 'results': [
        {'key': 'zzfixture~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': '1', 'senses': [{'tag': '1', 'german': '{%Wasser%}', 'russian': 'вода',
             'equivalence_type': 'equivalent', 'source_type': 'attested',
             'stratum': '', 'differentia': ''}]}]}}]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    try:
        # No expect() — a fixture may audit clean/blocked/stale; the guarantee under test is
        # only that the live singletons are not touched, whatever the exit code.
        subprocess.run([sys.executable, os.path.join(SRC, 'pilot', 'audit_window.py'),
                        wf_path, '--ephemeral'],
                       cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        after = {p: snap(p) for p in live}
        for p in live:
            if before[p] != after[p]:
                fail('ephemeral audit clobbered the live status file %s' % os.path.basename(p))
    finally:
        os.remove(wf_path)



def test_requeue_transient_vs_defect_state():
    """Null cards (transient) must classify transient_only; a gate defect -> needs_requeue;
    a pre-split report (no requeue_defect key) must stay needs_requeue (PROCESS_AUDIT rec 3/10)."""
    from window_reports import audit_state
    base = {'root': 'zztest', 'keys': ['k1'], 'crashed': [], 'glue': {}}
    transient = dict(base, requeue=['k1'], requeue_transient=['k1'], requeue_defect=[])
    if audit_state(transient) != 'transient_only':
        fail('all-null requeue must classify as transient_only')
    defect = dict(base, requeue=['k1', 'k2'], requeue_transient=['k1'], requeue_defect=['k2'])
    if audit_state(defect) != 'needs_requeue':
        fail('a gate-defect requeue must classify as needs_requeue')
    legacy = dict(base, requeue=['k1'])  # pre-split report: no requeue_defect key
    if audit_state(legacy) != 'needs_requeue':
        fail('pre-split reports must remain needs_requeue (no silent transient downgrade)')
    import requeue_from_audit as rq
    with tempfile.TemporaryDirectory() as tmp:
        old_inp = rq.INP
        old_deny = rq.translation_memory.denylist_path
        try:
            rq.INP = tmp
            raw = os.path.join(tmp, 'k1.raw.txt')
            with open(raw, 'w', encoding='utf-8') as f:
                f.write('source')
            deny = os.path.join(tmp, 'deny.jsonl')
            rq.translation_memory.denylist_path = lambda out=None: deny
            no_fshas = os.path.join(tmp, 'no_fshas.txt')   # keep the frag channel out of scope
            n_en, _ = rq.append_tm_denylist('zz', ['k1'], 'defect', lang='en',
                                            fsha_file=no_fshas)
            n_ru, _ = rq.append_tm_denylist('zz', ['k1'], 'defect', lang='ru',
                                            fsha_file=no_fshas)
            if (n_en, n_ru) != (1, 1):
                fail('denylist should append one row per lang')
            rows = [json.loads(line) for line in open(deny, encoding='utf-8')]
            if rows[0]['lang'] != 'en' or not rows[0]['address'].startswith('en:'):
                fail('EN denylist address must carry en:<sha>')
            if rows[1]['lang'] != 'ru' or not rows[1]['address'].startswith('ru:'):
                fail('RU denylist address must carry ru:<sha>')
        finally:
            rq.INP = old_inp
            rq.translation_memory.denylist_path = old_deny



def test_export_translation_dedup():
    """Homograph fix: translations attach ONCE per key1, labelled by store homonym; a second
    same-key1 (homograph) entry must NOT repeat them (was the preview multiplication)."""
    from export_interop import card_glosses
    translations = {'dA': [{'ru': 'давать', 'subcard': 'dA~~h0_00_pwg00'},
                           {'ru': 'резать', 'subcard': 'dA~~h3_00_pwg00'}]}
    card = {'key1': 'dA', 'attested_senses': {}, 'records': []}
    emitted = set()
    t1 = [r for r in card_glosses(card, translations, emitted) if r[0] == 'approved_translation']
    t2 = [r for r in card_glosses(card, translations, emitted) if r[0] == 'approved_translation']
    if len(t1) != 2:
        fail('first homograph entry must carry both translations')
    if t2:
        fail('a second same-key1 entry must NOT repeat translations (homograph dedup)')
    if not (t1[0][1].startswith('h0-') and t1[1][1].startswith('h3-')):
        fail('each translation sense must be labelled by its store homonym')



def test_transient_requeue_no_tm_flag_h4527():
    """H4527: a transient requeue stays TM-on by default; `--no-tm` (passed by the coordinator
    for a defect-repair lease, whose card is in the TM) forces TM-off."""
    import requeue_from_audit as rq

    for extra, want in (([], False), (['--no-tm'], True)):
        with tempfile.TemporaryDirectory() as tmp:
            inp = os.path.join(tmp, 'input')
            os.makedirs(inp)
            with open(os.path.join(inp, 'a.raw.txt'), 'w', encoding='utf-8') as f:
                f.write('raw')
            rqfile = os.path.join(tmp, 'requeue.transient.keys.txt')
            with open(rqfile, 'w', encoding='utf-8') as f:
                f.write('a\n')
            captured = {}

            class FakeProc:
                returncode = 0
                stdout = ''
                stderr = ''

            def fake_run(cmd, **_kwargs):
                captured['cmd'] = cmd
                return FakeProc()

            old_inp, old_run, old_argv = rq.INP, rq.subprocess.run, sys.argv[:]
            rq.INP = inp
            rq.subprocess.run = fake_run
            sys.argv = ['requeue_from_audit.py', 'nominal_selftest', '--transient', '--nominal',
                        '--requeue-file=%s' % rqfile,
                        '--out=%s' % os.path.join(tmp, 'h.js')] + extra
            try:
                rq.main()
            finally:
                rq.INP, rq.subprocess.run, sys.argv = old_inp, old_run, old_argv
        if ('--no-tm' in (captured.get('cmd') or [])) != want:
            fail('transient requeue %r: --no-tm should be %s' % (extra, want))



def test_partial_cards_requeue_and_stay_out_of_clean_sample():
    """Partial-only output is transient; an independent content defect wins."""
    import audit_window as aw
    import window_reports as wr

    fixture = [
        {'key': 'partial_only', 'card': {'partial': True,
                                         'missing_fragments': ['g1:f9']}},
        {'key': 'partial_defect', 'card': {'partial': True,
                                           'missing_fragments': ['g2:f3']}},
    ]
    partial_cards, failure_reasons = aw.collect_harness_quality(fixture)
    transient, defect, _ = aw.classify_harness_requeues(
        [], partial_cards, {'partial_defect'}, failure_reasons)
    if transient != {'partial_only'} or defect != {'partial_defect'}:
        fail('partial requeue precedence drifted: transient=%r defect=%r' %
             (transient, defect))

    report = {'root': 'zz', 'keys': ['clean', 'partial_only', 'partial_defect'],
              'null_cards': [], 'requeue': sorted(transient | defect)}
    saved_merged_exists = wr.merged_exists
    try:
        wr.merged_exists = lambda key: True
        sample = wr.build_judge_sample(report, rate=1.0, minimum=0, seed='partial-test')
    finally:
        wr.merged_exists = saved_merged_exists
    if sample['clean_sample_keys'] != ['clean']:
        fail('partial keys leaked into clean judge candidates: %r' %
             sample['clean_sample_keys'])

