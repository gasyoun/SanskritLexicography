"""test_senses_and_glosses — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_senses_and_glosses.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_h920_sense_count_top_level_ordinals():
    """H920: count_source_senses counts DISTINCT top-level source senses (N〉 close-glyph and
    line-anchored N) markers), never citation numbers or lettered sub-senses. Calibrated on
    the real darvI (3-sense PW source), aklizwa (single keyed supplement sense), and a_sakta
    (unnumbered adjective) evidence."""
    darvi = ('=== LAYER: PW ===\n\n{T1} und {T2}¦ {T3}\n'
             '{T6}— 1〉 {%Löffel%}.\n{T7}— 2〉 {%die Haube einer Schlange%}.\n'
             '{T8}— 3〉 {T4} {T5} eines Landes.')
    cases = [
        (darvi, 3),                                             # darvI: 3 top-level senses
        ('{#aklizwa#}¦ 3〉 {%keine Pein verursachend%} <ls>KAP. 2,33</ls>.', 1),  # single keyed sense
        ('{#aSakta#}¦ <lex>Adj.</lex> {%nicht könnend%} <ls n="Chr.">94,27</ls>.', 0),  # unnumbered
        ('<ls>MBH. 5,163,4</ls>. 2,33 1,5', 0),                # citation numbers are NOT senses
        ('1) a\n2) b\n3) c', 3),                               # line-anchored N) form
        ('— 2〉 x\n— 2〉 x (batch repeat)', 1),                  # a repeated ordinal counts once
    ]
    for text, want in cases:
        got = count_source_senses(text)
        if got != want:
            fail('count_source_senses(%r) = %d, expected %d' % (text[:40], got, want))



def test_h920_sense_shortfall_gate_flags_dropped_sense():
    """H920: the audit_window SAN-LOSS gate flags a card whose OUTPUT sense count falls short
    of its input portrait's declared source_senses (the darvI 2/3 shape), passes a complete
    card, and is CONSERVATIVE — it skips null cards and portraits that predate the source_senses
    stamp (never a false positive)."""
    import audit_window
    with tempfile.TemporaryDirectory() as tmp:
        def portrait(name, **extra):
            json.dump([dict({'portrait_kind': 'no_pwg_supplement_chain', 'senses': []}, **extra)],
                      open(os.path.join(tmp, name + '.portrait.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False)
        portrait('darv_i~~h0_zz_pw', key1='darvI', source_senses=3)   # 3 source senses
        portrait('ok~~h0_zz_pw', key1='ok', source_senses=2)          # complete
        portrait('legacy~~h0_zz_pw', key1='legacy')                   # pre-H920, no count
        results = [
            {'key': 'darv_i~~h0_zz_pw',                               # 2 of 3 -> SAN-LOSS
             'card': {'key1': 'darvI', 'records': [{'senses': [{'tag': '2'}, {'tag': '3'}]}]}},
            {'key': 'ok~~h0_zz_pw',                                   # 2 of 2 -> clean
             'card': {'records': [{'senses': [{'tag': '1'}, {'tag': '2'}]}]}},
            {'key': 'legacy~~h0_zz_pw',                               # no expected count -> skipped
             'card': {'records': [{'senses': [{'tag': '1'}]}]}},
            {'key': 'null~~h0_zz_pw', 'card': None, 'error': 'kill-timeout'},  # null -> skipped
        ]
        # pure scan
        short = scan_sense_shortfall(results, tmp)
        if [s['key'] for s in short] != ['darv_i~~h0_zz_pw']:
            fail('scan_sense_shortfall should flag ONLY darvI, got %r' % short)
        if short[0]['expected'] != 3 or short[0]['actual'] != 2 or short[0]['dropped'] != 1:
            fail('darvI shortfall math wrong: %r' % short[0])
        # the wired audit gate
        gate = audit_window.run_sense_shortfall_gate(results, tmp, set())
        if gate['returncode'] != 1 or gate['requeue'] != ['darv_i~~h0_zz_pw']:
            fail('SAN-LOSS gate must FAIL and requeue only darvI, got %r' % gate)
        if 'SAN-LOSS' not in gate['stdout'] or 'dropped 1' not in gate['stdout']:
            fail('SAN-LOSS gate stdout must report the drop: %r' % gate['stdout'])
        # protected keys are never requeued
        if audit_window.run_sense_shortfall_gate(results, tmp, {'darv_i~~h0_zz_pw'})['requeue']:
            fail('a protected key must not be requeued by the SAN-LOSS gate')
        # a fully-clean window passes
        clean = audit_window.run_sense_shortfall_gate(results[1:], tmp, set())
        if clean['returncode'] != 0 or clean['requeue']:
            fail('SAN-LOSS gate must PASS a window with no shortfall, got %r' % clean)



def test_h920_no_pwg_portrait_stamps_source_senses():
    """H920: gen_no_pwg_card stamps a deterministic source_senses count into each sub-card's
    portrait (matching count_source_senses on that sub-card's raw), while still fabricating NO
    sense tree (senses stays []). A source with >=2 numbered senses also carries the explicit
    sense-completeness rule so the model is told to render every sense."""
    import _pilot_gen_merged as pg
    import dict_merge as dm
    # unit: the sense-completeness rule fires only for multi-sense sources and never inflates
    # the deterministic count (the rule text carries no 〉 / leading-digit lines).
    multi = '=== LAYER: PW ===\n\n{#x#}¦\n— 1〉 {%a%}.\n— 2〉 {%b%}.\n— 3〉 {%c%}.'
    ruled = pg._with_sense_rule(multi, count_source_senses(multi))
    if 'SENSE-COMPLETENESS RULE' not in ruled or 'all 3' not in ruled:
        fail('multi-sense supplement must carry the H920 sense-completeness rule')
    if count_source_senses(ruled) != 3:
        fail('the sense-completeness rule must not inflate the deterministic count')
    if pg._with_sense_rule('=== LAYER: PW ===\n\nsingle sense, no marker', 0) \
            != '=== LAYER: PW ===\n\nsingle sense, no marker':
        fail('a source with <2 senses must NOT get the sense-completeness rule')
    # end-to-end: render a real no-PWG card and assert the portrait is enriched + consistent.
    old_out = pg.OUT
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        pg.OUT = tmp
        try:
            pwg_idx = dm.index('pwg')
            for key, layer in (('Bagavat', 'pw'), ('Akulita', 'sch')):
                if not pg.gen_no_pwg_card(key, pwg_idx, verbose=False):
                    fail('gen_no_pwg_card(%s) produced no sub-cards' % key)
                sub = '%s~~h0_zz_%s' % (pg.safe_name(key), layer)
                raw = open(os.path.join(pg.OUT, sub + '.raw.txt'), encoding='utf-8').read()
                p0 = json.loads(open(os.path.join(pg.OUT, sub + '.portrait.json'), encoding='utf-8').read())[0]
                if 'source_senses' not in p0:
                    fail('%s portrait must carry the H920 source_senses count' % sub)
                if p0['source_senses'] != count_source_senses(raw):
                    fail('%s portrait source_senses (%r) must equal count_source_senses(raw) (%d)'
                         % (sub, p0['source_senses'], count_source_senses(raw)))
                if p0.get('senses') != []:
                    fail('%s no-PWG portrait must still fabricate no sense tree' % sub)
        finally:
            pg.OUT = old_out



def test_h920_en_missing_sense_hard_flag():
    """H920: the EN auditor emits a HARD MISSING-SENSE flag when an output card falls short of
    its portrait's source_senses (SHARED with the RU gate via sense_count.py), distinct from the
    per-sense SAN-LOSS gloss-token flag; a complete card carries no such flag."""
    import audit_window_en as en
    with tempfile.TemporaryDirectory() as tmp:
        json.dump([{'source_senses': 3}],
                  open(os.path.join(tmp, 'darv_i~~h0_zz_pw.portrait.json'), 'w', encoding='utf-8'))
        json.dump([{'source_senses': 2}],
                  open(os.path.join(tmp, 'ok~~h0_zz_pw.portrait.json'), 'w', encoding='utf-8'))
        old_dir = en.INPUT_DIR
        en.INPUT_DIR = tmp
        try:
            short = en.audit_card(
                {'key': 'darv_i~~h0_zz_pw',
                 'card': {'records': [{'h': 'darvī', 'senses': [
                     {'tag': '2', 'german': '2〉 x', 'english': 'the hood of a snake'},
                     {'tag': '3', 'german': '3〉 y', 'english': 'name of a country'}]}]}},
                None, False)
            flags = [f for _, f in short['flags']]
            if not any(f.startswith('MISSING-SENSE') for f in flags):
                fail('EN auditor must emit MISSING-SENSE on a 2/3 card, got %r' % flags)
            if not any(en.is_hard(f) for f in flags if f.startswith('MISSING-SENSE')):
                fail('MISSING-SENSE must be a HARD flag')
            ok = en.audit_card(
                {'key': 'ok~~h0_zz_pw',
                 'card': {'records': [{'h': 'ok', 'senses': [
                     {'tag': '1', 'german': '1〉 a', 'english': 'first'},
                     {'tag': '2', 'german': '2〉 b', 'english': 'second'}]}]}},
                None, False)
            if any(f.startswith('MISSING-SENSE') for _, f in ok['flags']):
                fail('a complete 2/2 card must NOT get MISSING-SENSE')
        finally:
            en.INPUT_DIR = old_dir



def test_en_dup_gate_preserves_sanskrit_referent_c2():
    """C2: the EN within-card DUP hard-gate must key on the RAW english, not prose() — prose()
    strips {#..#} Sanskrit and <ls>, so two senses distinguished ONLY by their referent
    ('N. of a serpent-demon {#vAsuki#}' vs '…{#takzaka#}') collapsed to one string and the second
    was wrongly HARD-DUP'd, failing --strict on faithful output (the verifier found 310 such real
    within-record cases). A TRUE duplicate (identical english) must still be flagged HARD."""
    import audit_window_en as en
    with tempfile.TemporaryDirectory() as tmp:
        old_dir = en.INPUT_DIR
        en.INPUT_DIR = tmp   # no portraits -> source_senses absent -> MISSING-SENSE gate skipped
        try:
            distinct = en.audit_card(
                {'key': 'zz~~h0_00_pwg00',
                 'card': {'records': [{'h': 'zz', 'senses': [
                     {'tag': '1', 'german': '1〉 N. eines Schlangendämons {#vAsuki#}',
                      'english': 'N. of a serpent-demon {#vAsuki#}'},
                     {'tag': '2', 'german': '2〉 N. eines Schlangendämons {#takzaka#}',
                      'english': 'N. of a serpent-demon {#takzaka#}'}]}]}},
                None, False)
            if any(f.startswith('DUP') for _, f in distinct['flags']):
                fail('C2: senses distinguished by their {#..#} referent must NOT be flagged DUP: %r'
                     % [f for _, f in distinct['flags']])
            same = en.audit_card(
                {'key': 'zz~~h1_00_pwg00',
                 'card': {'records': [{'h': 'zz', 'senses': [
                     {'tag': '1', 'german': '1〉 N. eines Schlangendämons {#vAsuki#}',
                      'english': 'N. of a serpent-demon {#vAsuki#}'},
                     {'tag': '2', 'german': '2〉 N. eines Schlangendämons {#vAsuki#}',
                      'english': 'N. of a serpent-demon {#vAsuki#}'}]}]}},
                None, False)
            dup_flags = [f for _, f in same['flags'] if f.startswith('DUP')]
            if not dup_flags:
                fail('C2: two senses with the EXACT same english must still be flagged DUP')
            if not any(en.is_hard(f) for f in dup_flags):
                fail('C2: DUP must remain a HARD flag')
        finally:
            en.INPUT_DIR = old_dir



def test_h960_accept_sanloss_soft_gate():
    """H960: the harness stamps the deterministic (cross-reference-hardened) source_senses into
    each input, and accept() carries the SAN-LOSS shortfall guard — H920's deferred deepest fix.
    SOFT by default (SANLOSS_HARD_REJECT=false): a whole-dropped sense is COUNTED as telemetry but
    the card is kept; the owner-gated flip rejects+requeues it. The behavioral half runs the REAL
    emitted accept()+countOf (see accept_sensecount_test.js), so it can't drift from the generator."""
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        # darv_i: 3 line-opening senses -> source_senses 3. xref: only cross-reference ordinals
        # ("zu {#ASraya#} 1〉 und 6〉") -> hardened source_senses 0 (the FP-regression shape).
        raws = {
            'darv_i~~h0_zz_pw': '=== LAYER: PW ===\n\n{#darvI#}¦\n— 1〉 {%a%}.\n— 2〉 {%b%}.\n— 3〉 {%c%}.',
            'xref~~h0_zz_pw': '=== LAYER: PW ===\n\nNom. abstr. zu {#ASraya#} 1〉 und 6〉.',
        }
        keys = list(raws)
        paths = {}
        for k, raw in raws.items():
            rp = os.path.join(d, k + '.raw.txt')
            pp = os.path.join(d, k + '.portrait.json')
            with open(rp, 'w', encoding='utf-8') as f:
                f.write(raw)
            with open(pp, 'w', encoding='utf-8') as f:
                f.write('[]')
            paths[k] = (rp, pp)
        gh.input_paths = lambda k, input_dir=None: paths[k]
        gh.KILL = False
        js, _ = gh.build('zz_sanloss', keys, None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        # (1) the soft gates (sanloss + grammar-{Tn}) + owner-gated hard paths + telemetry are emitted
        for needle in ('const SANLOSS_HARD_REJECT = false', 'SANLOSS_SHORTFALLS',
                       'sanloss-reject', 'sanloss_shortfalls',
                       'const TNMASK_HARD_REJECT = false', 'TNMASK_MISMATCHES',
                       'tnmask-reject', 'tnmask_mismatches'):
            if needle not in js:
                fail('accept() SAN-LOSS / {Tn} soft gate not emitted (missing %r)' % needle)
        # (2) the deterministic source_senses count is stamped into the runtime INPUTS
        if '"source_senses": 3' not in js:
            fail('darv_i source_senses (3) must be stamped into the emitted INPUTS')
        if '"source_senses": 0' not in js:
            fail('cross-reference xref source_senses must harden to 0 in the emitted INPUTS')
        # (3) behavioral: the REAL accept() rejects/keeps a shortfall exactly as specified
        harness = os.path.join(d, 'sanloss_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(HERE,
                               'accept_sensecount_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('accept() SAN-LOSS behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        shutil.rmtree(d, ignore_errors=True)



def test_h960_dropped_sanskrit_span():
    """H960 (H911 backlog #3): a {#..#} Sanskrit span present in the German source but dropped from
    the Russian translation is flagged (dropped_sanskrit_span). The harness/tm fidelity gates count
    {#..#} only in the german echo, never the translation field, so an intra-sense span that
    survives the echo but vanishes from the Russian passes clean. LOW / report-only (never in
    HIGH_CONFIDENCE_RISKS -> never requeues). Structural HEAD labels (headword/preverb/root) are
    excluded — the measured 95%-false-positive class — so only a genuine intra-sense drop fires."""
    import prompt_rule_audit as pr
    def ids(ru, de):
        return [r['id'] for r in pr.markup_sigla_risks({}, ru, de, '', '3')]
    # POSITIVE: a genuine mid-sense span drop fires.
    if 'dropped_sanskrit_span' not in ids('делает что-то несмотря', 'делает что-то {#kar#} несмотря'):
        fail('dropped_sanskrit_span must fire on a genuine mid-sense {#..#} drop')
    # CONTROL: span retained -> silent.
    if 'dropped_sanskrit_span' in ids('делает {#kar#} несмотря', 'делает {#kar#} несмотря'):
        fail('dropped_sanskrit_span must NOT fire when the span is retained')
    # CONTROL: a headword-label drop (the darvI FP class) is excluded.
    if 'dropped_sanskrit_span' in ids('имя собственное страны', '{#darvI#} <ab>N. pr.</ab> eines Landes'):
        fail('a headword-label {#..#} drop must be excluded (95% FP class)')
    # CONTROL: a √-root label drop is excluded.
    if 'dropped_sanskrit_span' in ids('мерить', '√{#mA#} messen'):
        fail('a root-label {#..#} drop must be excluded')
    # report-only: never high-confidence (never drives a requeue), and LOW severity.
    if 'dropped_sanskrit_span' in pr.HIGH_CONFIDENCE_RISKS:
        fail('dropped_sanskrit_span must stay out of HIGH_CONFIDENCE_RISKS (report-only)')
    row = [r for r in pr.markup_sigla_risks({}, 'делает что-то несмотря', 'делает что-то {#kar#} несмотря', '', '3')
           if r['id'] == 'dropped_sanskrit_span'][0]
    if row['level'] != 'low' or row.get('high_confidence'):
        fail('dropped_sanskrit_span must be LOW / non-high-confidence, got %r' % row)



def test_gloss_wrapper_prompt_preservation_h4270():
    """H4015 residual (H4270): the generation prompt must order {%…%} wrapper preservation.

    Two independent c1 windows lost the German {%…%} gloss wrappers in the Russian output on
    _apta (8 wrappers in, 1 kept, zero «») while every {Tn}-masked span survived — because
    pwg_mask.mask keeps DE {%…%} spans INLINE (unmasked), so nothing told the model the
    wrapper is markup it must reproduce. H3658 Lane B ruled the class not deterministically
    repairable post-hoc and PR #789 forbids guessing gloss boundaries, so the prompt is the
    fix: an explicit preservation rule + a worked example, pinned here on MASK_PREAMBLE (the
    shared source of the manifest-v2 preamble and the generated JS) and end-to-end on a mini
    manifest whose golden output requires {%…%} spans.
    """
    import gen_opt_harness2 as gh
    from gen_opt_harness2 import MASK_PREAMBLE as preamble

    # 1) The rule, on the shared source text.
    for needle in ('{%…%}', 'GLOSS-DE-RESIDUE', 'MUST reappear',
                   'Never drop the wrapper', 'never replace it with «…»',
                   'never leave the'):
        if needle not in preamble:
            fail('MASK_PREAMBLE lost the gloss-wrapper clause %r — the model will keep '
                 'stripping {%…%} wrappers and every window re-defects (H4015, twice)' % needle)
    # 1b) H4277 (a′): the tightening clause — the H4270 window over-applied the rule to a
    #     MASKED English span ({%equation of a degree%} -> {%уравнение степени%}, sense 4b,
    #     high-confidence foreign_gloss_translated) instead of echoing {Tn} for restore.
    for needle in ('applies ONLY to {%…%} spans you can SEE in your masked source',
                   'stays {Tn} VERBATIM in both fields', 'never translate it',
                   'never wrap it in {%…%}'):
        if needle not in preamble:
            fail('MASK_PREAMBLE lost the {Tn}-verbatim tightening clause %r — the model will '
                 'over-apply the wrapper rule to masked spans again (H4270 sense 4b)' % needle)
    # 2) The worked example, spans verbatim.
    for needle in ('a〉 {%ein%} <is>Arhant</is> <ls>H. 25</ls>.',
                   'а) {%некий%} <is>Arhant</is> <ls>H. 25</ls>.'):
        if needle not in preamble:
            fail('MASK_PREAMBLE lost the gloss-wrapper worked example %r' % needle)
    # 2b) #2109: the EN lane must see the demonstration in the language it produces. The rule
    #     itself was always shared (`.replace('`russian`', field)` reaches both lanes), but the
    #     worked example stayed RU-illustrated, so an `--lang en` window read a Russian target
    #     string as the model for its own English output. Both renderings are pinned here.
    en_preamble = gh.mask_preamble('english')
    for needle in ('a〉 {%ein%} <is>Arhant</is> <ls>H. 25</ls>.',
                   'EN `a) {%a certain%} <is>Arhant</is> <ls>H. 25</ls>.`',
                   'must read `a) {%a certain%} {T1} {T2}.`',
                   '`english` field'):
        if needle not in en_preamble:
            fail('the EN-lane preamble lost %r — an --lang en window is back to being shown a '
                 'Russian worked example for its own English output (#2109)' % needle)
    if 'некий' in en_preamble:
        fail('the EN-lane preamble still carries the Russian worked example (#2109) — the '
             'example must be keyed to `field`, not copied from the RU rendering')
    if 'a certain' in preamble:
        fail('the RU-lane preamble picked up the English worked example (#2109)')
    # The rule text itself stays byte-identical across lanes apart from the field name and the
    # example, so the shared-verdict half of the ledger pair keeps holding.
    for needle in ('GLOSS-DE-RESIDUE', 'MUST reappear', 'Never drop the wrapper',
                   'applies ONLY to {%…%} spans you can SEE in your masked source',
                   'stays {Tn} VERBATIM in both fields'):
        if needle not in en_preamble:
            fail('the EN-lane preamble lost the shared wrapper rule %r' % needle)

    # 3) End-to-end mini manifest: the DE {%…%} span stays inline in the masked skeleton AND
    #    the generated JS prompt carries the rule (ensure_ascii escapes the Cyrillic example;
    #    the ASCII skeleton of the clause survives verbatim).
    raw = '<L>1<pc>1<k1>a<k2>a<h>1\n{#a#}¦ a) {%eins%} <is>Arhant</is> <ls>H. 25</ls>.\n'
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
        import re as _re
        if 'GLOSS WRAPPERS' not in js or '{%ein%}' not in js:
            fail('generated JS prompt lost the gloss-wrapper rule/example — the paid lane '
                 'would translate bare prose again (H4015 class)')
        inputs = json.loads(_re.search(r'^const INPUTS = (.*)$', js, _re.M).group(1))
        for k in keys:
            skel = inputs[k]['skeleton']
            if '{%eins%}' not in skel:
                fail('masked skeleton dropped the DE gloss wrapper for %s: %r — golden output '
                     'cannot carry {%…%} spans the input no longer shows' % (k, skel))
            if '{T' not in skel:
                fail('masked skeleton lost its {Tn} spans for %s: %r' % (k, skel))
    finally:
        gh.input_paths = saved_ip
        shutil.rmtree(d, ignore_errors=True)



def test_h1152_guard1_en_polyseme_checklist():
    """H1152 guard 1 (H1070 finding #1: r155 'braut'->betroth, r119 'Vergleich'->comparison):
    a German-homograph/polyseme checklist under term-mistranslation in the EN fidelity judge
    rubric, plus a matching HARD RULE in tr_en.txt telling the generator to pick the sense the
    Sanskrit lemma licenses, never the frequent German sense. Markup stays intact and the
    English reads fluently for this error class, so no deterministic gate can catch it --
    this guard is judge-rubric + generation-prompt only, pinned here as a content check."""
    import gen_fidelity_judge_en as jen
    for term in ('Vergleich', 'braut', 'Braut', 'gelten', 'Zug', 'anführen'):
        if term not in jen.RUBRIC:
            fail('EN judge RUBRIC missing German-polyseme checklist term %r' % term)
    if 'term-mistranslation' not in jen.RUBRIC or 'polysem' not in jen.RUBRIC.lower():
        fail('EN judge RUBRIC term-mistranslation line is missing the polyseme checklist')
    tr = open(os.path.join(HERE, 'tr_en.txt'), encoding='utf-8').read()
    if 'sense the sanskrit lemma licenses' not in tr.lower():
        fail('tr_en.txt is missing the polyseme prompt rule (pick the sense the Sanskrit '
             'lemma licenses, never the frequent sense)')
    if 'polysemous german gloss' not in tr.lower():
        fail('tr_en.txt is missing the POLYSEMOUS GERMAN GLOSSES hard rule')



def test_braced_gloss_audit():
    untranslated = braced_gloss_risks('{%Schulter%}', '{%Schulter%}', '1')
    ids = {risk['id'] for risk in untranslated}
    if 'untranslated_braced_german_gloss' not in ids:
        fail('braced gloss audit missed untranslated German gloss')
    kept_latin = braced_gloss_risks('das lat. {%ansa%}', 'лат. {%ansa%}', '1')
    kept_binomial = braced_gloss_risks('{%Trapa bispinosa%}', '{%Trapa bispinosa%}', '1')
    if kept_latin or kept_binomial:
        fail('braced gloss audit flagged literal Latin/binomial preservation')
    translated_latin = braced_gloss_risks(
        'das lat. {%ansa%}', 'лат. {%ручка%}', '1')
    translated_english = braced_gloss_risks(
        'Wils. übersetzt durch {%leaving, abandoning%}',
        'Уилсон переводит как {%оставление, покидание%}', '1')
    ids = {risk['id'] for risk in translated_latin + translated_english}
    if 'foreign_gloss_translated' not in ids:
        fail('braced gloss audit missed translated Latin/English literal gloss')

    # B&R Latin euphemisms / French / Sanskrit-token braces must NOT be flagged as
    # untranslated German (the convention keeps them verbatim).
    for ger in ('{%inire feminam%}', '{%legere%}', '{%inveteratus%}',
                "{%un homme de l'extraction la plus basse%}", '{%abhi%}',
                '{%upanis%}', '{%āgamya%}', '{%sequi, obsequi%}'):
        leftover = {r['id'] for r in braced_gloss_risks(ger, ger, '1')}
        if 'untranslated_braced_german_gloss' in leftover:
            fail('braced gloss audit wrongly flagged non-German literal: %s' % ger)
    # Side-by-side: German kept in {%...%} BESIDE its Russian rendering is required.
    side = braced_gloss_risks('{%herfallen über%}', 'нападать на ({%herfallen über%})', '1')
    if {r['id'] for r in side} & {'untranslated_braced_german_gloss'}:
        fail('braced gloss audit flagged required side-by-side German echo')

    # gam~~h0_20_ava / gam~~h0_38_sam_a (2026-07-03): short/colloquial German that collides
    # with a FRENCH_WORDS entry ("du") or matches LATIN_BINOMIAL's over-permissive
    # Capitalized-word+lowercase-word shape ("Jmd zusammenkommen", "Jmd" being the common B&R
    # abbreviation for "jemand") must be recognized as German and NOT flagged
    # foreign_gloss_translated merely for being correctly translated into Russian.
    colloquial = braced_gloss_risks(
        '{%wie kommst du darauf? woraus schliessest du dieses?%}',
        '{%как ты до этого дошёл? из чего ты это заключаешь?%}', '1')
    if {r['id'] for r in colloquial} & {'foreign_gloss_translated'}:
        fail('braced gloss audit misclassified colloquial German (du) as foreign literal')
    abbrev = braced_gloss_risks('{%Jmd zusammenkommen%}', '{%встречаться с кем-л.%}', '1')
    if {r['id'] for r in abbrev} & {'foreign_gloss_translated'}:
        fail('braced gloss audit misclassified "Jmd ..." (LATIN_BINOMIAL shape) as Latin')

    # gam~~h0_38_sam_a (2026-07-03): a correctly-translated short gloss ({%mit%} -> {%с%})
    # was flagged untranslated because the "leaked" check did a raw substring search across
    # the WHOLE Russian text, including verbatim {#Sanskrit#} citation spans -- "mit" is a
    # literal substring of the unrelated SLP1 citation token "miTunO" (lowercased "mituno").
    sanskrit_collision = braced_gloss_risks(
        '{%mit%} (<ab>instr.</ab>) {#yadA vE miTunO samAgacCataH#} (fleischlich)',
        '{%с%} (<ab>instr.</ab>) {#yadA vE miTunO samAgacCataH#} (плотски)', '1')
    if {r['id'] for r in sanskrit_collision} & {'untranslated_braced_german_gloss'}:
        fail('braced gloss audit flagged a gloss that only collided with an embedded '
             'Sanskrit citation substring, not a real leak')

    # H4527 (23-09-2026, kast_ur_i~~h0_zz_pw): a Latin binomial wrapped in PWG markup
    # ({%<bot>Hibiscus abelmoschus</bot>%}) and kept verbatim in the Russian is the
    # convention, not an untranslated German gloss -- the anchored LATIN_BINOMIAL used to be
    # defeated by the leading tag. The other direction must still fire: a bare German
    # {%Moschus%} echoed with no Cyrillic rendering is a genuine miss, tagged or not.
    for bot in ('{%<bot>Hibiscus abelmoschus</bot>%}', '{%<bot>Amaryllis zeylanica</bot>%}'):
        bot_ids = {r['id'] for r in braced_gloss_risks(bot, bot, '1')}
        if bot_ids & {'untranslated_braced_german_gloss', 'foreign_gloss_translated'}:
            fail('braced gloss audit flagged a verbatim <bot> Latin binomial: %s' % bot)
    for ger in ('{%Moschus%}', '{%<bot>Moschus</bot>%}'):
        ger_ids = {r['id'] for r in braced_gloss_risks(ger, ger, '1')}
        if 'untranslated_braced_german_gloss' not in ger_ids:
            fail('braced gloss audit missed a bare untranslated German echo: %s' % ger)



def test_sense_dupe_norm_strips_trailing_period():
    """P5 (H1422): norm() stripped a trailing ')'/'〉' but not '.', so tag '1.' and plain
    '1' hashed to different buckets and a real cross-part duplicate with mismatched
    locator punctuation ('1.' vs '1)' vs '1') was missed by the dupe check. An INTERIOR
    period ('caus. 2') must stay distinct from plain '2' -- only trailing punctuation is
    normalized away."""
    from audit_sense_dupes import norm
    for variant in ('1', '1.', '1)', '1 ', '1.)', '1).'):
        if norm(variant) != '1':
            fail('norm(%r) = %r, expected \'1\' -- trailing punctuation must normalize '
                 'identically' % (variant, norm(variant)))
    if norm('caus. 2') == norm('2'):
        fail('norm() must keep \'caus. 2\' distinct from plain \'2\' -- an interior period '
             'is meaningful, only trailing punctuation should be stripped')



def test_sense_dupe_batch_override():
    """The cross-part sense-duplicate exemption must be reproducible from the committed
    rootmap_overrides.json, NOT from a gitignored hand-edited rootmap (PROCESS_AUDIT rec 15)."""
    from audit_sense_dupes import allowed_batch_duplicate, rootmap_meta
    keys = ['x~~h0_00_pwg00', 'x~~h0_00_pwg01']
    declared = {k: {'batch_of': '1c'} for k in keys}
    if not allowed_batch_duplicate('1c', keys, declared):
        fail('a declared citation-split duplicate must be permitted')
    if allowed_batch_duplicate('1c', keys, {}):
        fail('an undeclared cross-part duplicate must NOT be permitted')
    # The committed override file must actually reach rootmap_meta() (jan 1c), independent
    # of whatever the gitignored jan.rootmap.json currently holds.
    entry = rootmap_meta().get('jan~~h0_00_pwg00') or {}
    if entry.get('batch_of') != '1c':
        fail('committed rootmap_overrides.json (jan 1c) not merged into rootmap_meta')



def test_sense_dupe_cross_level_exempt():
    """A flagged cross-part duplicate is legitimate when the root declares the (homonym, tag) as
    known cross-LEVEL sense-number reuse (verb vs derived-noun vs prefix-participle). siD h1 is
    the committed case (SIDH_DUPE_INVESTIGATION.md)."""
    from audit_sense_dupes import is_dupe_exempt, dupe_exempt_map
    exempt = dupe_exempt_map()
    keys = {'si_d~~h1_00_pwg00', 'si_d~~h1_00_pwg02'}
    if not is_dupe_exempt('h1', '3', keys, exempt):
        fail('declared siD cross-level reuse (h1 sense 3) must be exempt')
    if is_dupe_exempt('h1', '5', keys, exempt):
        fail('an undeclared tag must NOT be exempt')
    if is_dupe_exempt('h1', '3', {'si_d~~h1_00_pwg00', 'jan~~h1_00_pwg00'}, exempt):
        fail('a cross-root collision must never be exempt')



def test_pwg_mask_latin_cue_behind_ab_tag():
    """Regression (review 2026-07-04): a Latin/Greek cue inside an <ab> span
    (e.g. `<ab>lat.</ab> {%ignis%}`) is masked to a {Tn} placeholder in mask()
    step 1, so classify_pct used to see "{T5}" instead of "lat." and misread the
    following {%...%} cognate as German — leaking Latin verbatim into the
    translator prompt. The cue must be recovered from the placeholder so the
    Latin gloss is masked, while a genuine German gloss stays inline. SHARED
    (masking runs before any --lang branch; identical for RU and EN)."""
    import pwg_mask
    body = 'Feuer <ab>lat.</ab> {%ignis%} und Wasser'
    sk, ph, st = pwg_mask.mask(body)
    if st['pct_la'] != 1 or st['pct_de'] != 0:
        fail('Latin cue behind <ab> not caught: %r' % st)
    if '{%ignis%}' in sk:
        fail('Latin gloss leaked into skeleton unmasked: %r' % sk)
    if pwg_mask.restore(sk, ph) != body:
        fail('mask round-trip not lossless after Latin-cue fix')
    # a genuine German gloss (no Latin cue) must still be kept inline for translation
    sk2, ph2, st2 = pwg_mask.mask('das <ab>Subst.</ab> {%Feuer%}')
    if st2['pct_de'] != 1 or st2['pct_la'] != 0:
        fail('German gloss wrongly masked as Latin: %r' % st2)



def test_h1152_guard3_xref_only_and_nws_de_locked():
    """H1152 guard 3 (H1070 finding #3, 12/170 FU1 rows): two deterministic "nothing was
    really translated here" shapes, flagged SOFT so a coverage consumer stops counting them
    as ordinary translated prose. Neither is a fidelity defect (markup/meaning stay intact),
    so neither may ever become a HARD flag."""
    from audit_window_en import audit_sense
    # XREF-ONLY: no {%..%} gloss wrapper -> only the cross-reference apparatus survives.
    hard_xref, soft_xref = audit_sense('Vgl. {#foo#} fgg.', 'Cf. {#foo#} and foll.')
    if 'XREF-ONLY' not in soft_xref:
        fail('XREF-ONLY did not fire on a pure cross-reference row (Vgl. ... fgg.)')
    if hard_xref:
        fail('a pure cross-reference row must never produce a HARD flag: %r' % hard_xref)
    # CONTROL: a real {%..%} gloss beside a cross-ref word must NOT fire XREF-ONLY.
    _, soft_real = audit_sense('{%to speak%} Vgl. {#foo#}', 'to speak; cf. {#foo#}')
    if 'XREF-ONLY' in soft_real:
        fail('XREF-ONLY wrongly fired on a row carrying real gloss prose')
    # NWS-DE-LOCKED: German trapped inside a {#..#} span never reached the translator.
    hard_locked, soft_locked = audit_sense('{#der Bote kommt#}', '{#der Bote kommt#}')
    if 'NWS-DE-LOCKED' not in soft_locked:
        fail('NWS-DE-LOCKED did not fire on German text trapped inside a {#..#} span')
    if hard_locked:
        fail('NWS-DE-LOCKED shape must never produce a HARD flag: %r' % hard_locked)
    # CONTROL: genuine Sanskrit/IAST inside {#..#} must NOT fire NWS-DE-LOCKED.
    _, soft_san = audit_sense('{%to speak%} {#vac#}', 'to speak {#vac#}')
    if 'NWS-DE-LOCKED' in soft_san:
        fail('NWS-DE-LOCKED wrongly fired on genuine Sanskrit inside a {#..#} span')



def test_whitney_homonym_safety():
    """FL1: requesting a Whitney homonym a root lacks must return EMPTY, never fall back to
    ALL homonyms — attaching a different homonym's grammar is a silent wrong-root error."""
    from whitney_grammar import grammar_for
    all_vas = grammar_for('vas')
    if len(all_vas) < 2:
        return  # whitney_grammar.json unbuilt in this env — nothing to assert
    first = all_vas[0]['homonym']
    exact = grammar_for('vas', first)
    if len(exact) != 1 or exact[0]['homonym'] != first:
        fail('an exact homonym request must return only that homonym')
    if grammar_for('vas', '999') != []:
        fail('a nonexistent homonym must return empty, not fall back to all homonyms')
    if grammar_for('zzqqx_no_such_root', '1') != []:
        fail('an unknown root must return empty')



def test_cit_split_never_tears_open_span():
    """SAN-LOSS hypothesis (2026-07-04 vid drain): autosplit_requeue._cit_parts split a
    (sub)sense purely on running <ls> counts per line, with NO awareness of {#...#} span
    state. A well-formed <ls>...</ls> span can never straddle a cut (a NEW <ls> can only
    open once the PREVIOUS one has closed, and the algorithm never lets the running count
    exceed budget), but a {#...#} span never contributes to that count at all — so a
    {#...#} block that is still open when a LATER, unrelated <ls> tag pushes the running
    <ls> count over budget got torn across the cut. A torn {#...#} span can no longer be
    matched by pwg_mask's PAIRED regex (needs a complete open+close pair), so its Sanskrit
    content passed through UNMASKED as ordinary translatable prose — the model then
    paraphrases or drops it, producing SAN-LOSS on exactly the citation-dense giant heads
    that need tier-2 splitting. Fixed via _span_open(): defer the cut until the accumulated
    fragment text is <ls>/{#..#} balanced. This constructs the vulnerable shape (a
    {#...#} span straddling what would otherwise be the cut point) and asserts every
    returned fragment is internally balanced."""
    from autosplit_requeue import plan as split_plan
    raw = (
        '<ls n="1">a</ls>\n'
        '{#Sanskrit quote start\n'
        '<ls n="2">b</ls>\n'
        'quote end#}\n'
        '<ls n="3">c</ls>\n'
    )
    parts = split_plan(raw, ls_budget=1)
    if len(parts) < 2:
        fail('fixture did not force a split — adjust ls_budget/fixture')
    for _si, _pi, text in parts:
        if text.count('<ls') != text.count('</ls>'):
            fail('a returned fragment has an unbalanced <ls>/</ls> pair — span torn across '
                 'a cut: %r' % text)
        if text.count('{#') != text.count('#}'):
            fail('a returned fragment has an unbalanced {#/#} pair — Sanskrit span torn '
                 'across a cut: %r' % text)



def test_sense_split_never_tears_open_span():
    """P4 (H1422): autosplit_requeue._blocks detects sense boundaries purely from lines
    matching _SENSE ("1)", "2)", ...), with no awareness of an open <ls>/{#...#} span --
    unlike _cit_parts (H155, see test_cit_split_never_tears_open_span above), which already
    defers a citation-batch cut until the accumulated text is span-balanced. A citation that
    spans several lines can contain an interior line shaped like "2)" (a locator INSIDE the
    span, not a real second sense), which _blocks used to accept as a genuine boundary and
    tear the span across two (sub)sense blocks. Fixed by applying the same _span_open
    deferral to sense-boundary detection: a candidate boundary is skipped (merged into the
    current block) while the text since the last accepted boundary is still open."""
    import autosplit_requeue as ar
    raw = (
        '1) first sense <ls n="a">start of citation\n'
        '2) middle of citation still open</ls> end of first sense really\n'
        '3) second real sense\n'
    )
    b = ar._blocks(raw)
    if b is None:
        fail('fixture should detect 2 real sense boundaries (1+3), got none')
    header, blocks = b
    if len(blocks) != 2:
        fail('interior "2)" locator inside an open <ls> span must not be treated as a real '
             'sense boundary -- expected 2 blocks, got %d: %r' % (len(blocks), blocks))
    for blk in blocks:
        if blk.count('<ls') != blk.count('</ls>'):
            fail('a sense block has an unbalanced <ls>/</ls> pair — span torn across a '
                 'sense-tier cut: %r' % blk)
    if '3) second real sense' not in blocks[-1]:
        fail('the genuine third sense must survive as its own block: %r' % blocks[-1])



def test_cit_split_caps_single_line_monster_sense():
    """H191/B2: a single physical line with many complete citations must still be
    sub-split; line-boundary splitting alone emitted >90-citation fragments."""
    import autosplit_requeue as ar
    raw = 'Ein einziger Sinn. ' + ' '.join(
        '<ls n="SRC.%d">citation %d</ls>' % (i, i) for i in range(150))
    parts = ar.plan(raw, ls_budget=18)
    if len(parts) < 2:
        fail('150-citation one-line fixture must split into multiple fragments')
    for _si, _pi, text in parts:
        if text.count('<ls') > 18:
            fail('fragment exceeds citation budget: %d <ls>' % text.count('<ls'))
        if text.count('<ls') != text.count('</ls>'):
            fail('line-level splitter tore an <ls> span')



def test_sense_dense_card_presplit():
    """H155 (2026-07-04): a SENSE-dense card must presplit even when its CITATION weight
    (1+<ls>) is FAR below the output budget. A PW addenda card compresses a whole root article
    (base verb + Caus/Desid + every prefix combination) into dozens of terse senses carrying
    few citations, so the citation metric (1+<ls>) ranks it as one of the LIGHTEST cards while
    its real output surface (dozens of {tag,german,russian} sense objects) is the HEAVIEST — it
    deterministically blows the whole-card StructuredOutput retry cap (tyaj~~h0_zz_pw: 35 senses
    in 11 <ls>, weight 12, stalled ~7 min retrying the identical call). The fragment-count
    trigger (frag count > SENSE_PRESPLIT_BUDGET) routes it straight to the proven fragment lane,
    same as the citation giants — independent of the citation trigger and of byte/citation
    batching mode. Uses a synthetic card (30 senses, 1 <ls>) so it never depends on a specific
    corpus fixture."""
    import gen_opt_harness2 as gh
    senses = '\n'.join('<div n="1">— %d〉 {%%Bedeutung %d%%}.' % (i, i)
                       for i in range(1, 31))
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n' + senses + '\n')
    key = 'zz~~synthetic_sense_dense'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')  # empty portrait — exactly the real tyaj~~h0_zz_pw shape
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            # citation weight 1+<ls>=2 is far below OUTPUT_BUDGET(90): only the SENSE trigger
            # can route this card. nominal mode makes the key its own card (no rootmap needed).
            js, batches = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            import re as _re
            presplit = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js, _re.M).group(1))
            batched = {k for b in batches for k in b}
            if key not in presplit:
                fail('a sense-dense card (30 senses, 1 <ls>) must be routed to presplit by the '
                     'fragment-count trigger; got PRESPLIT=%r batches=%r' % (presplit, batches))
            if key in batched:
                fail('a presplit card must be pulled OUT of the whole-card batch lane, got it in '
                     '%r' % (batches,))
            # the citation trigger alone must NOT explain it (proves the sense trigger is load-
            # bearing): with the sense trigger disabled, the card falls back to a batch.
            saved_sb = gh.SENSE_PRESPLIT_BUDGET
            gh.SENSE_PRESPLIT_BUDGET = None
            try:
                js2, batches2 = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
                presplit2 = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js2, _re.M).group(1))
            finally:
                gh.SENSE_PRESPLIT_BUDGET = saved_sb
            if key in presplit2:
                fail('with --sense-presplit-budget=off the citation-light card must NOT presplit '
                     '(only the sense trigger should route it); got PRESPLIT=%r' % presplit2)
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_pwg_mask_bom_source_keeps_first_record():
    """Hardening (H316; FL6 / CODE_REVIEW 2026-07-04): a UTF-8 BOM on the PWG
    source used to leave the first line as BOM+'<L>...', which
    startswith('<L>') misses -- the FIRST record of the dictionary was silently
    dropped. records() now reads utf-8-sig (a no-op on BOM-less files).
    SHARED (stage-0 masking, before any --lang branch)."""
    import tempfile
    import pwg_mask
    body = ('<L>1<pc>1,1<k1>agni<k2>agni\nFeuer\n<LEND>\n'
            '<L>2<pc>1,1<k1>ap<k2>ap\nWasser\n<LEND>\n')
    for bom, label in ((b'\xef\xbb\xbf', 'BOM'), (b'', 'no-BOM')):
        tf = tempfile.NamedTemporaryFile('wb', suffix='.txt', delete=False)
        tf.write(bom + body.encode('utf-8'))
        tf.close()
        old = pwg_mask.PWG
        pwg_mask.PWG = tf.name
        try:
            recs = list(pwg_mask.records())
        finally:
            pwg_mask.PWG = old
            os.unlink(tf.name)
        if len(recs) != 2:
            fail('%s source: expected 2 records, got %d' % (label, len(recs)))
        if not recs[0][0].startswith('<L>1'):
            fail('%s source: first record dropped/mangled: %r' % (label, recs[0][0]))



def test_pwg_mask_truncated_final_record_not_silent():
    """Hardening (H316): a final record opened with <L> but never closed by
    <LEND> (truncated source) must not be yielded downstream -- but it must not
    vanish silently either: records() warns on stderr."""
    import contextlib
    import io
    import tempfile
    import pwg_mask
    body = ('<L>1<pc>1,1<k1>agni<k2>agni\nFeuer\n<LEND>\n'
            '<L>2<pc>1,1<k1>ap<k2>ap\nWasser\n')  # no closing <LEND>
    tf = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8')
    tf.write(body)
    tf.close()
    old = pwg_mask.PWG
    pwg_mask.PWG = tf.name
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            recs = list(pwg_mask.records())
    finally:
        pwg_mask.PWG = old
        os.unlink(tf.name)
    if len(recs) != 1:
        fail('truncated source: expected 1 complete record, got %d' % len(recs))
    if 'truncated final record' not in err.getvalue():
        fail('truncated final record dropped SILENTLY -- warning missing')



def test_degenerate_xref_vocab_single_source():
    """H1425 W2: the cross-reference / degenerate-passthrough vocabulary is ONE shared frozenset,
    consumed by both the RU generation lane (gen_opt_harness2.degenerate_passthrough_card) and the
    EN auditor (audit_window_en.xref_only) — it used to be two independently-authored copies (the
    C-01 drift class). Assert both reference the same object (can't drift), and that xref_vocab is
    dependency-free so the EN auditor can import it without the heavy harness stack."""
    import gen_opt_harness2 as gh
    import audit_window_en as en
    import xref_vocab
    if gh._DEGENERATE_WORDS is not xref_vocab.DEGENERATE_XREF_WORDS:
        fail('gen_opt_harness2._DEGENERATE_WORDS must BE the shared xref_vocab set, not a copy')
    if en._XREF_WORDS is not xref_vocab.DEGENERATE_XREF_WORDS:
        fail('audit_window_en._XREF_WORDS must BE the shared xref_vocab set, not a copy')
    # behaviour intact through the shared set (cross-ref residue -> True; a real gloss -> False)
    if not en.xref_only('s. {#foo#} fgg.') or en.xref_only('{%real gloss%}'):
        fail('xref_only behaviour changed after the vocab extraction')



def test_card_coverage_lang_symmetric():
    """H1425 W1: the FL4 coverage-complete rule lives in ONE --lang-parameterized kernel
    (`card_coverage`), so a fix reaches both languages instead of an EN-only reimplementation.
    card_done = >=1 slot AND every German-bearing slot carries the target field; identical for
    'russian'/'english', and the OTHER language's field must not count toward this one's coverage."""
    from card_coverage import card_done, slot_coverage
    for field, other in (('english', 'russian'), ('russian', 'english')):
        full = {'records': [{'senses': [{'german': 'a', field: 'x'}, {'german': 'b', field: 'y'}]}]}
        part = {'records': [{'senses': [{'german': 'a', field: 'x'}, {'german': 'b'}]}]}
        empty = {'records': [{'senses': [{'tag': '1'}]}]}   # no german/target -> 0 slots
        cross = {'records': [{'senses': [{'german': 'a', other: 'z'}]}]}
        if slot_coverage(full, field) != (2, 2) or not card_done(full, field):
            fail('%s: a fully-translated card must be done' % field)
        if slot_coverage(part, field) != (1, 2) or card_done(part, field):
            fail('%s: FL4 — a 1/2 card must NOT be done (the ">=1" blindspot)' % field)
        if card_done(empty, field) or card_done(None, field) or card_done({}, field):
            fail('%s: a null / empty / no-slot card must not be done' % field)
        if card_done(cross, field):
            fail('%s coverage must not be satisfied by the %s field' % (field, other))



def test_pwg_mask_german_homograph_not_latin_c8():
    """C8: In/Ab/Ex/Sub/Pro are German-capitalized homographs of Latin prepositions, so a German
    {%..%} gloss like 'In der Regel' / 'In den Schlusssatz einfallen' matched LATIN_PHRASE and was
    masked-and-dropped (never translated), invisibly (restore reinserts the identical German, so the
    round-trip selftest still reads 100% lossless). A German function word now keeps such a gloss
    inline ('de'); a genuine Latin phrase ('De accentu comp.', 'In usum Delphini') stays 'la'."""
    import pwg_mask as pm
    de_cases = ['In den Schlusssatz einfallen', 'In der Regel', 'In Verbindung mit etwas',
                'Ab dem dritten Tag']
    for c in de_cases:
        if pm.classify_pct(c, '') != 'de':
            fail("C8: German gloss %r must classify 'de' (kept inline), got %r"
                 % (c, pm.classify_pct(c, '')))
    la_cases = ['De accentu comp.', 'In usum Delphini', 'Ab ovo', 'Ex professo']
    for c in la_cases:
        if pm.classify_pct(c, '') != 'la':
            fail("C8: genuine Latin phrase %r must stay 'la', got %r" % (c, pm.classify_pct(c, '')))
    # the LATIN_CUE path (an explicit 'lat.'/'griech.' before the span) is unchanged
    if pm.classify_pct('in aqua', 'das lat.') != 'la':
        fail('C8: an explicit Latin cue must still force la')



def test_pwg_mask_gloss_lang_g1():
    """H1624 G1: durable gloss_lang on {%…%} — DE translate / LA+EN leave.

    Classifier emits {span, gloss_lang, rule_id, offsets}; mask treats la+en as
    {Tn} so Wilson English and botanical binomials never enter the translate
    prompt. Residue audit (braced_gloss_risks) shares the same classifier via
    looks_foreign_literal.
    """
    import pwg_mask as pm

    # --- classify vectors ---
    vectors = [
        # content, preceding, following, expect_lang, expect_rule_prefix
        ('das Nichthandeln', '', '', 'de', pm.RULE_DEFAULT_DE),
        ('Gabe, Geschenk', '', '', 'de', pm.RULE_DEFAULT_DE),
        ('ignis', 'das lat. ', '', 'la', pm.RULE_LATIN_CUE),
        ('De accentu comp.', '', '', 'la', pm.RULE_LATIN_PHRASE),
        ('Trapa bispinosa', '', '', 'la', pm.RULE_BOTANY_BINOMIAL),
        ('Galedupa arborea', '', '', 'la', pm.RULE_BOTANY_BINOMIAL),
        ('leaving, abandoning', 'WILS. übersetzt durch ', '', 'en', pm.RULE_WILSON_EN),
        ('terrestrial latitude', '', ', WILS.', 'en', pm.RULE_WILSON_EN),
        # Wilson + German content stays DE (must not mask German after WILS.)
        ('Honig', 'WILS. übersetzt durch ', '', 'de', pm.RULE_DEFAULT_DE),
        # German Capitalized+lowercase is NOT a binomial
        ('Name eines Baumes', '', '', 'de', pm.RULE_DEFAULT_DE),
    ]
    for content, prec, foll, exp_lang, exp_rule in vectors:
        d = pm.classify_pct_detail(content, prec, foll)
        if d['gloss_lang'] != exp_lang:
            fail('G1 classify %r: expected lang %r got %r (%r)'
                 % (content, exp_lang, d['gloss_lang'], d))
        if d['rule_id'] != exp_rule:
            fail('G1 classify %r: expected rule %r got %r'
                 % (content, exp_rule, d['rule_id']))
        if (exp_lang in pm.NON_TRANSLATE_LANGS) == d['translate']:
            fail('G1 classify %r: translate flag wrong for %r: %r'
                 % (content, exp_lang, d))

    # --- gloss_lang_spans on raw body (cues inside tags) ---
    body = (
        'Feuer <ab>lat.</ab> {%ignis%} und {%Trapa bispinosa%} '
        '(<ls>WILS.</ls> übersetzt durch {%leaving, abandoning%}) '
        'sowie {%Gabe, Geschenk%}.'
    )
    spans = pm.gloss_lang_spans(body)
    by = {s['span']: s for s in spans}
    for span, exp in (
        ('ignis', 'la'),
        ('Trapa bispinosa', 'la'),
        ('leaving, abandoning', 'en'),
        ('Gabe, Geschenk', 'de'),
    ):
        if by.get(span, {}).get('gloss_lang') != exp:
            fail('G1 spans %r: expected %r got %r' % (span, exp, by.get(span)))
        s = by[span]
        chunk = body[s['start']:s['end']]
        if not (chunk.startswith('{%') and chunk.endswith('%}')):
            fail('G1 spans offset broken for %r: %r' % (span, chunk))

    # --- mask: LA+EN as {Tn}, DE inline, lossless restore ---
    sk, ph, st = pm.mask(body)
    if st.get('pct_la', 0) < 2:
        fail('G1 mask expected >=2 LA placeholders, got %r' % st)
    if st.get('pct_en', 0) < 1:
        fail('G1 mask expected >=1 EN placeholder, got %r' % st)
    if st.get('pct_de', 0) < 1:
        fail('G1 mask expected >=1 DE inline, got %r' % st)
    if '{%ignis%}' in sk or '{%Trapa bispinosa%}' in sk:
        fail('G1 LA leaked into skeleton: %r' % sk)
    if '{%leaving, abandoning%}' in sk:
        fail('G1 EN leaked into skeleton: %r' % sk)
    if '{%Gabe, Geschenk%}' not in sk:
        fail('G1 DE not kept inline: %r' % sk)
    if pm.restore(sk, ph) != body:
        fail('G1 mask round-trip not lossless')

    # --- residue gate shares classifier (Latin/Wilson stay untranslated OK;
    # translating them fires foreign_gloss_translated) ---
    from prompt_rule_audit import braced_gloss_risks
    kept = braced_gloss_risks(
        'das lat. {%ansa%} und {%Trapa bispinosa%}; '
        'Wils. übersetzt durch {%leaving, abandoning%}',
        'лат. {%ansa%} und {%Trapa bispinosa%}; '
        'Уилсон: {%leaving, abandoning%}',
        '1')
    if kept:
        fail('G1 residue flagged faithful LA/EN preservation: %r' % kept)
    translated = braced_gloss_risks(
        'Wils. übersetzt durch {%leaving, abandoning%}',
        'Уилсон: {%оставление%}',
        '1')
    if 'foreign_gloss_translated' not in {r['id'] for r in translated}:
        fail('G1 residue missed translated Wilson EN: %r' % translated)

