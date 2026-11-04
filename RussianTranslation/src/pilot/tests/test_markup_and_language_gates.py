"""test_markup_and_language_gates — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_markup_and_language_gates.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_german_anchor_repair_behavioral():
    """H858 Part B: the anchored repair of a masked span dropped from the model's `german` echo.

    The `{#…#}`-span drop was the clean-rate ceiling on the no_pwg windows — 6 of 7 residual
    nulls in `no_pwg_w10` (H1283), and provably NOT fixable by a `--max-wide` requeue: the drop
    is a property of the echo, not of transport. `accept()` now re-injects the dropped spans
    from the source skeleton and re-runs the SAME `<ls>`/`{#` count as the verifier, so a repair
    lands only when it makes the card exactly source-faithful, and a card that already passed
    never enters the branch at all.

    Two-part pin, matching the H960/H1226 pattern: (1) the repair twin + its telemetry are
    emitted into the harness at all; (2) the behavioural half runs the REAL emitted
    gaPlan/gaReanchor/gaStamp AND the REAL accept() + restoreCard (german_anchor_test.js), so
    it cannot drift from the generator. The Python twin of the same cases is
    `german_anchor.selftest()`, run by `test_german_anchor_selftest` below — the two lanes are
    interpolated from ONE authored source (`german_anchor.js_source()`), the C-01/C-17 lesson.
    """
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, 'ga~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'ga~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#ga#}¦ {%m%}\n— 1〉 {%a%}.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        gh.KILL = False
        js, _ = gh.build('zz_ganchor', ['ga~~h0_zz_pw'], None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        for needle in ('const gaPlan = ', 'const gaReanchor = ', 'const gaStamp = ',
                       'GERMAN_ANCHOR_REPAIRS', 'german_anchor_repairs', 'german-anchor '):
            if needle not in js:
                fail('H858 german-anchor repair not emitted into the harness (missing %r)' % needle)
        harness = os.path.join(d, 'ganchor_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(HERE,
                               'german_anchor_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('german-anchor repair behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        shutil.rmtree(d, ignore_errors=True)



def test_german_anchor_selftest():
    """H858 Part B: the Python half of the repair, and the LANG_PARITY guarantee.

    `german_anchor` is SHARED (not language-specific): it repairs the `german` SOURCE echo,
    which is identical on the RU and EN lanes, and never touches the target-language field. So
    one selftest covers both languages by construction — the divergence LANG_PARITY.md exists
    to catch cannot arise here, and this test asserts that the module is genuinely
    field-agnostic rather than merely believed to be.
    """
    import german_anchor
    german_anchor.selftest()
    if 'russian' in german_anchor._JS or 'english' in german_anchor._JS:
        fail('german_anchor must stay language-agnostic (SHARED under LANG_PARITY.md)')
    for target in ('russian', 'english'):
        card = {'records': [{'senses': [{'german': 'Feuer', target: 'x'}]}]}
        ok, info = german_anchor.reanchor(card, '{T1} Feuer')
        if not ok or card['records'][0]['senses'][0]['german'] != '{T1} Feuer':
            fail('german_anchor repaired differently for target field %r: %r' % (target, info))
        if card['records'][0]['senses'][0][target] != 'x':
            fail('german_anchor must never touch the target field %r' % target)



def test_german_residue_keeps_retained_markup():
    # German inside retained {%...%} / <ab> spans with a Russian rendering beside it
    # is side-by-side, not residue; bare German connectives outside markup still flag.
    clean = semantic_card_risk_ids(
        'подражать ({%den Umständen gemäss%}: сообразно обстоятельствам)')
    if 'untranslated_german_residue' in clean:
        fail('residue audit flagged required side-by-side German')
    leak = semantic_card_risk_ids('— Vgl. upAgama und gam mit upa')
    if 'untranslated_german_residue' not in leak:
        fail('residue audit missed genuine untranslated German connectives')



def test_german_connective_fix():
    # safe lone connectives / fixed phrase in free text are substituted
    assert fix_german_text('{#X#} und {#Y#} mit {#Z#}')[0] == '{#X#} и {#Y#} с {#Z#}'
    assert fix_german_text('(<ab>s.</ab> auch d.)')[0] == '(<ab>s.</ab> также d.)'
    assert fix_german_text('fehlerhaft für {#aDijagAma#}')[0] == 'ошибочно вместо {#aDijagAma#}'
    # protected spans are NEVER touched: retained {%..%} markup and «..» German quotes
    if fix_german_text('{%und%}')[1] or fix_german_text('«Von Sternen und Mond»')[1]:
        fail('connective fix touched a protected span ({%..%} or «..»)')
    # ambiguous multi-word German phrase is left for review (no lone-connective match)
    if fix_german_text('aber nur in der Saṃhitā')[1]:
        fail('connective fix wrongly altered an ambiguous German phrase')



def test_h1302_german_prose_residue_scan():
    # H1302: the store-wide German-prose-residue detector + deterministic --store fixer.
    from german_residue_scan import scan_text
    from fix_german_connectives import fix_ru_store

    def classes(text):
        return {(tok, cls) for tok, _ctx, cls in scan_text(text)}

    # prose `zu` in a citation (Schol. zu <ls>) is flagged and deterministically fixable (class a)
    zu = classes('5) {%извлекать%}: {#tApasA#}\n<ab>Schol.</ab> zu <ls>ŚĀK. 14.</ls>')
    if ('zu', 'a') not in zu:
        fail('H1302: citation `zu` not flagged as class-a residue')
    # `mit Ergänzung von` outside markup is flagged class a
    if not any('Erg' in t and c == 'a' for t, c in classes('{%примирить%} mit Ergänzung von {#saha grIveRa#})')):
        fail('H1302: `mit Ergänzung von` not flagged as class-a residue')
    # a protected German gloss {%…%} and a «…» verbatim quote are NEVER flagged
    if classes('{%родственник, друг%} «nahe stehend» <ab>vgl.</ab> {#Api#}'):
        fail('H1302: detector flagged a protected {%…%} / «…» span')
    # grammatical German prose "mit dem <ab>acc.</ab>" is class-b (needs retranslation, not a sub)
    if not any(c == 'b' for _, c in classes('{%думать о%}; mit dem <ab>acc.</ab>: {#aBi#}')):
        fail('H1302: "mit dem <ab>acc.</ab>" not flagged as class-b retranslate')
    # author proper names with German orthography are whitelisted (class c), never residue
    if not any(c == 'c' for _, c in classes('Кауз.: оживлять. [NWS: Graßmann 1873 (1996) : 491]') or [(None, 'x')]):
        # [NWS:…] is masked entirely; a bare "Böhtlingk 1840" still whitelists to c
        if not any(c == 'c' for _, c in classes('первоначальном состоянии. Böhtlingk 1840 : 548')):
            fail('H1302: proper-name author not whitelisted (class c)')
    # the deterministic --store fixer repairs the two rejected-card patterns exactly
    if fix_ru_store('<ab>Schol.</ab> zu <ls>ŚĀK. 14.</ls>')[0] != '<ab>Schol.</ab> к <ls>ŚĀK. 14.</ls>':
        fail('H1302: --store fixer did not turn citation `zu` into «к»')
    if fix_ru_store('{%примирить%} mit Ergänzung von {#saha#}')[0] != '{%примирить%} с восполнением {#saha#}':
        fail('H1302: --store fixer did not turn `mit Ergänzung von` into «с восполнением»')
    # the fixer NEVER touches a protected span
    if fix_ru_store('{%mit und ohne%} «und»')[1]:
        fail('H1302: --store fixer touched a protected {%…%} / «…» span')



def test_h1305_ru_style_mechanical():
    # H1305 + review fix: hard style rules inspect structured Russian senses only;
    # ambiguous narrative R2/R3 prose warns but never enters FLAGGED_JSON.
    from ru_style_sweep import audit_workflow_results, scan_violations, style_diagnostics, sweep_text

    # ё-word flagged (R1)
    if 'R1_yo' not in scan_violations('пришёл поздно'):
        fail('H1305: ё-carrying word not flagged R1_yo')
    # standalone «всё» passes clean (whitelisted)
    if scan_violations('всё хорошо, Всё в порядке'):
        fail('H1305: whitelisted «всё»/«Всё» incorrectly flagged')
    # the «всё-таки» edge case is NOT whitelisted -- defaults to е, so IS flagged
    if 'R1_yo' not in scan_violations('он всё-таки пришёл'):
        fail('H1305: «всё-таки» edge case incorrectly treated as whitelisted')
    # metalanguage «вместо» flagged (R2)
    if 'R2_vmesto' not in scan_violations('ошибочно вместо {#X#}'):
        fail('H1305: metalanguage «вместо» not flagged R2_vmesto')
    # metalanguage «в значении» flagged (R3)
    if 'R3_vznach' not in scan_violations('употребляется в значении «зуб»'):
        fail('H1305: metalanguage «в значении» not flagged R3_vznach')
    # Ordinary prose stays natural and is diagnostic-only, not a hard violation.
    for prose, rule in (
            ('Он выступил вместо брата.', 'R2_vmesto'),
            ('«в отдельные случаи [вместо того чтобы быть непрерывным]»', 'R2_vmesto'),
            ('при māraṇa вместо abhra', 'R2_vmesto'),
            ('Он понял знак в значении обещания.', 'R3_vznach')):
        diagnostic = style_diagnostics(prose)
        if rule in diagnostic['violations'] or rule not in diagnostic['ambiguous_rules']:
            fail('H1305 review: narrative prose was not classified ambiguous: %s' % prose)
    # `ed. Bomb.` INSIDE <ls>...</ls> (standalone or embedded) is NEVER a violation --
    # rewriting it would break src/pwg_sources.py's citation-key resolution.
    if scan_violations('(так <ls>ed. Bomb.</ls>)'):
        fail('H1305: in-<ls> standalone `ed. Bomb.` incorrectly flagged')
    if scan_violations('<ls>R. ed. Bomb. 3,69,4</ls>'):
        fail('H1305: in-<ls> embedded `ed. Bomb.` citation incorrectly flagged')
    # a genuine free-prose `ed. Bomb.` OUTSIDE any <ls> tag IS flagged (R4)
    if 'R4_bomb' not in scan_violations('<ls>Mālatīm.</ls> (ed. Bomb.) 304,1.'):
        fail('H1305: free-prose `ed. Bomb.` not flagged R4_bomb')
    # a clean row (no violations of any kind) scans empty
    if scan_violations('обычный чистый русский текст без нарушений'):
        fail('H1305: clean text incorrectly flagged')
    # sweep_text actually applies the fix a flagged violation predicts
    fixed, counts = sweep_text('ошибочно вместо {#X#}, читает <ls>ed. Bomb.</ls>')
    if 'вм.' not in fixed or 'ed. Bomb.' not in fixed:
        fail('H1305: sweep_text did not apply the terse form / kept in-<ls> siglum verbatim')
    if counts.get('R2_vmesto') != 1 or counts.get('R4_bomb') != 0:
        fail('H1305: sweep_text per-rule counts do not match the expected split')

    # The workflow gate consumes card.records[].senses[].russian directly. Notes,
    # differentia and German text cannot false-flag an otherwise-clean translation.
    results = [{
        'key': 'clean-notes',
        'card': {'notes': 'Переводчик пришёл.', 'records': [{'senses': [{
            'german': 'вместо', 'russian': 'чистый текст', 'differentia': 'пришёл',
        }]}]},
    }, {
        'key': 'multi-hard',
        'card': {'records': [{'senses': [
            {'russian': 'пришёл'},
            {'russian': 'ошибочно вместо {#X#}'},
        ]}]},
    }, {
        'key': 'narrative',
        'card': {'records': [{'senses': [{'russian': 'Он выступил вместо брата.'}]}]},
    }]
    _, flagged, warned = audit_workflow_results(results)
    if flagged != ['multi-hard']:
        fail('H1305 review: structured workflow flags wrong keys: %r' % flagged)
    if warned != ['narrative']:
        fail('H1305 review: ambiguous workflow warning wrong keys: %r' % warned)



def test_h1651_wrapper_defect_gate():
    """H1651: Cyrillic is never valid inside {#...#} (the SLP1/Sanskrit wrapper) --
    a planted violation must fire, and the fix must be found deterministically."""
    from wrapper_defect_scan import find_d1, find_d3
    from fix_wrapper_defects import fix_d1, fix_d3

    # POSITIVE: a planted Cyrillic-in-{#...#} violation fires.
    if not find_d1('текст {#полагать#} далее'):
        fail('H1651: Cyrillic inside {#...#} must be detected by find_d1')
    # CONTROL: genuine SLP1 content never fires.
    if find_d1("текст {#mfto 'yamiti na vetti#} далее"):
        fail('H1651: genuine SLP1 inside {#...#} must NOT be flagged')
    # CONTROL: a Cyrillic gloss correctly wrapped in {%...%} never fires (it is not
    # inside a {#...#} span at all).
    if find_d1('текст {%полагать%} далее'):
        fail('H1651: a correctly-wrapped {%...%} gloss must NOT be flagged by find_d1')

    # fix_d1 rewraps the violation to {%...%}, content unchanged.
    fixed, n = fix_d1('до {#полагать, думать#} после')
    if n != 1 or fixed != 'до {%полагать, думать%} после':
        fail('H1651: fix_d1 did not rewrap the Cyrillic span cleanly: %r' % fixed)
    if find_d1(fixed):
        fail('H1651: fix_d1 output must be clean under find_d1')

    # D3: DE {%...%} rendered as RU «...» at matching slot count is drift.
    if not find_d3('{%glauben%}', 'text «полагать» text'):
        fail('H1651: gloss-wrapper drift (DE {%...%} -> RU «...») must be detected')
    # CONTROL: a row whose RU already uses {%...%} for the gloss is clean.
    if find_d3('{%glauben%}', 'text {%полагать%} text'):
        fail('H1651: a row already using {%...%} in ru must NOT be flagged as drift')
    fixed3, n3, eligible = fix_d3('a {%X%} b {%Y%} c', 'a «X» b «Y» c')
    if not eligible or n3 != 2 or fixed3 != 'a {%X%} b {%Y%} c':
        fail('H1651: fix_d3 did not rewrap a count-matched row cleanly: %r' % fixed3)
    # count mismatch -> left untouched, not eligible (needs manual review).
    fixed3b, n3b, eligible_b = fix_d3('a {%X%} b {%Y%} c', 'a «X» b c')
    if eligible_b or n3b or fixed3b != 'a «X» b c':
        fail('H1651: fix_d3 must refuse a count-mismatched row rather than guess')



def test_h1651_live_gate_cyrillic_and_guillemet():
    """H1651 follow-up: wrapper_defect_scan.py/fix_wrapper_defects.py (PR #789) detect and
    repair D1/D3 in a periodic store scan, but neither is wired into the live per-card
    generation-time audit (prompt_rule_audit.markup_sigla_risks) -- so a future generation run
    could still reintroduce Cyrillic-in-{#..#} (or grow the guillemet-drift residual)
    undetected by the pipeline itself. This tests that live gate, distinct from
    test_h1651_wrapper_defect_gate above (which tests the standalone scan/fix tools)."""
    import prompt_rule_audit as pr

    def ids(ru, de=''):
        return [r['id'] for r in pr.markup_sigla_risks({}, ru, de, '', '3')]

    # D1: Cyrillic wrapped in {#..#} fires HIGH_CONFIDENCE.
    if 'cyrillic_in_sanskrit_wrapper' not in ids('{#полагать, думать#}: {#mfto vetti#}'):
        fail('cyrillic_in_sanskrit_wrapper must fire on a Cyrillic {#..#} span')
    if 'cyrillic_in_sanskrit_wrapper' in ids('{#mfto vetti#} значит "знать"'):
        fail('cyrillic_in_sanskrit_wrapper must NOT fire on a genuine Sanskrit span')
    if 'cyrillic_in_sanskrit_wrapper' not in pr.HIGH_CONFIDENCE_RISKS:
        fail('cyrillic_in_sanskrit_wrapper must be HIGH_CONFIDENCE (unambiguous, always wrong)')

    # D3: a {%..%} gloss dropped AND rendered as a guillemet fires the soft companion risk
    # alongside the pre-existing markup_wrapper_dropped.
    found = ids('«полагать»', de='{%glauben%}')
    if 'markup_wrapper_dropped' not in found or 'gloss_wrapper_became_guillemet' not in found:
        fail('gloss_wrapper_became_guillemet must fire alongside markup_wrapper_dropped')
    if {'markup_wrapper_dropped', 'gloss_wrapper_became_guillemet'} & set(ids('{%полагать%}', de='{%glauben%}')):
        fail('neither D3 risk should fire when the {%..%} wrapper survives')
    plain = ids('полагать', de='{%glauben%}')
    if 'markup_wrapper_dropped' not in plain:
        fail('markup_wrapper_dropped must still fire on a bare unwrapped drop')
    if 'gloss_wrapper_became_guillemet' in plain:
        fail('gloss_wrapper_became_guillemet must NOT fire without a guillemet span')
    if 'gloss_wrapper_became_guillemet' in pr.HIGH_CONFIDENCE_RISKS:
        fail('gloss_wrapper_became_guillemet must stay report-only (never requeue)')



def test_h1702_boundary_wrap_gate():
    """H1702: boundary-anchored auto-wrap for the H1651 D4 ru_n==0 sub-pattern (de carries
    a {%...%} gloss, ru carries the translated content but never wraps it). The fixer must
    place {%...%} in ru only when de's exact affixes around the gloss (numbering markers,
    trailing punctuation) are found verbatim in ru at the same anchor-delimited position --
    never guess a boundary it cannot verify byte-for-byte."""
    from d4_boundary_wrap import is_ru_n0_candidate, try_boundary_wrap

    # POSITIVE: a clean single-gloss row with a numbering prefix and trailing separator,
    # matching the H1651 report's row-4553 worked example.
    de = '<div n="2">— e〉 {%zum Vorschein gekommen%}.'
    ru = '<div n="2">— e〉 появившийся.'
    if not is_ru_n0_candidate(de, ru):
        fail('H1702: de-has-gloss/ru-has-none must be detected as a candidate')
    ok, result = try_boundary_wrap(de, ru)
    want = '<div n="2">— e〉 {%появившийся%}.'
    if not ok or result != want:
        fail('H1702: boundary wrap did not reproduce the expected wrap: %r' % (result,))
    if is_ru_n0_candidate(de, result):
        fail('H1702: a freshly-wrapped row must no longer read as a ru_n==0 candidate')

    # CONTROL: a row that already carries a {%...%} gloss in ru is not a candidate at all.
    if is_ru_n0_candidate('{%glauben%}', '{%полагать%}'):
        fail('H1702: a row already wrapped in ru must NOT be a ru_n==0 candidate')

    # BOUNDARY-SAFETY (H1651 row-811 corruption-risk shape): the gloss covers only the
    # clause before a colon, followed by a {#...#} citation. Affixes match exactly here,
    # so the fixer must place the wrap at the colon, NOT swallow the citation into the gloss.
    de2 = '{%Etwas einräumen, zugeben%}: {#na samADatte#} als <ab>Erkl.</ab> von'
    ru2 = 'допустить, признать: {#na samADatte#} как <ab>Erkl.</ab> от'
    ok2, result2 = try_boundary_wrap(de2, ru2)
    if not ok2 or '{%' not in result2 or result2.index('%}') > result2.index('{#'):
        fail('H1702: the gloss wrap must close before the {#...#} citation, not swallow it: %r' % (result2,))

    # NEGATIVE: ru dropped the leading <div>/numbering marker present in de -- the anchor
    # set deliberately excludes <div>, so this must fail the exact-prefix check rather than
    # guess where the marker would have been.
    de3 = '<div n="1">— 2〉 {%an sich nehmen%}.'
    ru3 = 'принимать на себя.'
    ok3, reason3 = try_boundary_wrap(de3, ru3)
    if ok3:
        fail('H1702: a dropped-<div>-prefix row must be refused, not wrapped by guesswork: %r' % (reason3,))

    # NEGATIVE: two gloss spans inside the same anchor-delimited gap -- refuse rather than
    # guess an interior boundary.
    de4 = '{%first%} und {%second%}: {#x#}'
    ru4 = 'первый и второй: {#x#}'
    ok4, reason4 = try_boundary_wrap(de4, ru4)
    if ok4:
        fail('H1702: multiple gloss spans in one gap must be refused, not partially guessed')
    if reason4 != 'multi-gloss-in-gap':
        fail('H1702: expected multi-gloss-in-gap, got %r' % (reason4,))

    # NEGATIVE: a row with an unrelated, still-open H1651 D3 guillemet elsewhere in ru
    # must be refused wholesale, even though this particular gloss slot's affixes match --
    # wrapping only this slot would hide the still-open D3 defect from find_d3's own
    # `not ru_gloss` heuristic without actually resolving it.
    de5 = '{%first%}: {#x#} «second»'
    ru5 = 'первый: {#x#} «second»'
    ok5, reason5 = try_boundary_wrap(de5, ru5)
    if ok5:
        fail('H1702: a row with a residual D3 guillemet must be refused, not partially fixed')
    if reason5 != 'residual-d3-guillemet-present':
        fail('H1702: expected residual-d3-guillemet-present, got %r' % (reason5,))

    # REGRESSION: an anchor (<ab>...</ab>) nested INSIDE a {%...%} gloss span (a real PWG
    # pattern, e.g. "gekocht <ab>u. s. w.</ab>") splits that gloss across the anchor
    # boundary under naive anchor-tokenization -- it must not silently fall through while
    # another, cleanly-anchored gloss slot in the same row gets wrapped (a partial fix
    # that breaks the all-or-nothing guarantee; found live in the store, 4 rows).
    de6 = '{%clean%}: {#x#} {%gekocht <ab>u. s. w.</ab>%}'
    ru6 = 'чистый: {#x#} сваренный <ab>u. s. w.</ab>'
    ok6, reason6 = try_boundary_wrap(de6, ru6)
    if ok6:
        fail('H1702: a gloss span split by a nested anchor must be refused, not partially wrapped: %r' % (reason6,))
    if reason6 != 'gloss-span-crosses-anchor':
        fail('H1702: expected gloss-span-crosses-anchor, got %r' % (reason6,))



def test_h2144_d4b_bracket_normalize():
    """H2144: D4b bracket-normalize unlock. de's fullwidth/CJK corner-bracket numbering
    marker (e.g. `〉`) and ru's plain ASCII equivalent (`)`) must be treated as the same
    affix boundary when normalize_brackets=True, WITHOUT rewriting ru's own bracket
    character into de's form and WITHOUT changing default (normalize_brackets=False)
    behavior at all."""
    from d4_boundary_wrap import try_boundary_wrap

    # POSITIVE: de uses the fullwidth corner bracket, ru already uses plain ASCII ")" --
    # refused by default (exact-affix), unlocked under normalize_brackets=True, and ru's
    # own ")" is preserved verbatim in the result (not rewritten to de's "〉").
    de = '<div n="2">— e〉 {%zum Vorschein gekommen%}.'
    ru = '<div n="2">— e) появившийся.'
    ok_default, reason_default = try_boundary_wrap(de, ru)
    if ok_default:
        fail('H2144: bracket-mismatched affix must be refused by default (normalize_brackets=False)')
    if reason_default != 'prefix-no-match':
        fail('H2144: expected prefix-no-match by default, got %r' % (reason_default,))
    ok_norm, result_norm = try_boundary_wrap(de, ru, normalize_brackets=True)
    want = '<div n="2">— e) {%появившийся%}.'
    if not ok_norm or result_norm != want:
        fail('H2144: bracket-normalize wrap did not reproduce the expected wrap (ru bracket must survive verbatim): %r' % (result_norm,))

    # POSITIVE (reverse pairing): de uses ASCII, ru uses the fullwidth bracket -- ru's own
    # fullwidth bracket must survive the wrap untouched.
    de_rev = '<div n="2">— e) {%zum Vorschein gekommen%}.'
    ru_rev = '<div n="2">— e〉 появившийся.'
    ok_rev, result_rev = try_boundary_wrap(de_rev, ru_rev, normalize_brackets=True)
    want_rev = '<div n="2">— e〉 {%появившийся%}.'
    if not ok_rev or result_rev != want_rev:
        fail('H2144: reverse bracket-normalize wrap must preserve ru\'s fullwidth bracket verbatim: %r' % (result_rev,))

    # CONTROL: an already-exact-match row must produce an IDENTICAL result under
    # normalize_brackets=True as under the default -- the flag must never change behavior
    # for rows that did not need it.
    de_exact = '<div n="2">— 2〉 {%an sich nehmen%}.'
    ru_exact = '<div n="2">— 2〉 принимать на себя.'
    ok_a, result_a = try_boundary_wrap(de_exact, ru_exact)
    ok_b, result_b = try_boundary_wrap(de_exact, ru_exact, normalize_brackets=True)
    if not (ok_a and ok_b and result_a == result_b):
        fail('H2144: normalize_brackets=True must not change the outcome for an already-exact-match row')

    # NEGATIVE: a genuine (non-bracket) affix mismatch stays refused even with
    # normalize_brackets=True -- the flag only widens bracket equivalence, nothing else.
    de_bad = '<div n="1">— 2〉 {%an sich nehmen%}.'
    ru_bad = 'принимать на себя.'
    ok_bad, reason_bad = try_boundary_wrap(de_bad, ru_bad, normalize_brackets=True)
    if ok_bad:
        fail('H2144: a dropped-<div>-prefix row must still be refused under normalize_brackets=True: %r' % (reason_bad,))



def test_nws_fp_suppressed():
    """Card-level text signal (head sense has <ls>) suppresses per-sense FP.
    Also: [NWS: OWNER] in equivalence_type counts as text signal."""
    # Case A: _zz_pw*-style card — head has <ls>, simple senses do not.
    pw_card = {
        'key': 'han~~h0_zz_pw00',
        'card': {
            'key1': 'han~~h0_zz_pw00',
            'iast': 'han',
            'records': [{
                'h': '1',
                'grammar': 'verb',
                'senses': [
                    {'tag': 'head', 'german': '<ls>R. ed. Bomb. 4,24,33</ls>',
                     'russian': 'введение', 'equivalence_type': 'explanatory',
                     'source_type': 'attested', 'stratum': '', 'differentia': ''},
                    {'tag': '1', 'german': '{%schlagen%}',
                     'russian': 'бить', 'equivalence_type': 'equivalent',
                     'source_type': 'attested', 'stratum': '', 'differentia': ''},
                    {'tag': '2', 'german': '{%abschlagen%}',
                     'russian': 'отбивать', 'equivalence_type': 'equivalent',
                     'source_type': 'attested', 'stratum': '', 'differentia': ''},
                ],
            }],
        },
    }
    # Case B: NWS sense — [NWS: OWNER] in equivalence_type only.
    nws_card = {
        'key': 'a~~h0_zz_nws00',
        'card': {
            'key1': 'a~~h0_zz_nws00',
            'iast': 'a',
            'records': [{
                'h': '1',
                'grammar': '',
                'senses': [{
                    'tag': 'NWS',
                    'german': '{#a#} [Gen , unsp] ohne Band',
                    'russian': 'без оков',
                    'equivalence_type': '[NWS: Graßmann 1873 (1996) : 81]',
                    'source_type': 'attested',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'results': [pw_card, nws_card]}, f, ensure_ascii=False)
    try:
        report = audit_cards(path, review_limit=5)
        ids = {risk['id'] for card in report['cards'] for risk in card['risks']}
        if 'suspicious_attested_without_text_signal' in ids:
            fail('F-gate-nws-fp: suspicious_attested_without_text_signal fired on '
                 'a card with card-level text signal or NWS owner citation')
    finally:
        os.remove(path)



def test_en_gate_strict_has_teeth():
    """FL2: the EN gate's --strict must FAIL on a null card (missing EN) and write a report;
    report-only (no --strict) must still exit 0. A null card used to slide through clean."""
    fixture = {'meta': {'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': '1', 'senses': [{'tag': '1', 'german': '{%Wasser%}', 'english': 'water'}]}]}},
        {'key': 'zz~~h0_01_pwg01', 'card': None},
    ]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    report_path = wf_path + '.report.json'
    en_audit = os.path.join(HERE, 'audit_window_en.py')
    try:
        # report-only: exit 0 even with a null card
        run([sys.executable, en_audit, wf_path, '--no-mw'], expect=0)
        # strict: null card must fail, and the report must record it
        run([sys.executable, en_audit, wf_path, '--no-mw', '--strict', '--report', report_path],
            expect=1)
        rep = json.load(open(report_path, encoding='utf-8'))
        if 'zz~~h0_01_pwg01' not in (rep.get('null_keys') or []):
            fail('EN gate report did not record the null key')
        if not rep.get('strict_reasons'):
            fail('EN gate report did not record a strict failure reason')
    finally:
        os.remove(wf_path)
        if os.path.exists(report_path):
            os.remove(report_path)



def test_en_gate_dup_has_teeth():
    """H169 defect 1: two senses in one record sharing identical english used to slide
    through clean — the only within-record duplicate signal was the soft SAME-GLOSS flag,
    gated on >=3 content words, so a short duplicate ("to go" / "to go") produced zero flags
    and --strict passed. DUP must fire HARD regardless of gloss length."""
    fixture = {'meta': {'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': 'zz', 'senses': [
                {'tag': '1', 'german': '{%gehen%}', 'english': 'to go'},
                {'tag': '2', 'german': '{%gehen%}', 'english': 'to go'}]}]}},
    ]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    report_path = wf_path + '.report.json'
    en_audit = os.path.join(HERE, 'audit_window_en.py')
    try:
        # report-only: still exits 0 even with the hard DUP flag present
        run([sys.executable, en_audit, wf_path, '--no-mw'], expect=0)
        run([sys.executable, en_audit, wf_path, '--no-mw', '--strict', '--report', report_path],
            expect=1)
        rep = json.load(open(report_path, encoding='utf-8'))
        if not any(fl['flag'].startswith('DUP') for ff in rep['files'] for fl in ff['flags']):
            fail('EN gate did not emit a DUP flag for two identical-english senses')
        if not any('hard flag' in r for r in rep.get('strict_reasons') or []):
            fail('EN gate report did not record a strict failure reason for the DUP hard flag')
    finally:
        os.remove(wf_path)
        if os.path.exists(report_path):
            os.remove(report_path)



def test_ru_gate_fails_loud_on_unparseable_child():
    """H169 defect 2: the RU gate used to recover child-auditor verdicts by regex-scraping
    prose stdout (`| flagged: ...`) — any wording drift in audit_translation.py /
    audit_coverage.py / audit_sense_dupes.py made the parser return [] and silently drop
    flagged cards from the requeue while the gate reported clean. The fixed parser must
    return None (never []) when the strict `FLAGGED_JSON:` verdict line is missing or
    malformed, so the caller can fail loud instead of passing silently."""
    from audit_window import parse_flagged_json
    drifted_stdout = 'FAIL: 2/5 units clean | flagged: root_a, root_b\n'
    if parse_flagged_json(drifted_stdout) is not None:
        fail('parser must return None (unparseable) when the child emits no FLAGGED_JSON '
             'line, not silently treat wording drift as a clean pass')
    malformed = 'FLAGGED_JSON: {not valid json\n'
    if parse_flagged_json(malformed) is not None:
        fail('parser must return None on malformed JSON, not crash or silently drop flags')
    clean_line = 'PASS: 5/5 units clean\nFLAGGED_JSON: []\n'
    if parse_flagged_json(clean_line) != []:
        fail('parser did not parse a genuinely clean FLAGGED_JSON: [] line')
    flagged_line = 'FAIL: 3/5 units clean | flagged: root_a, root_b\nFLAGGED_JSON: ["root_a", "root_b"]\n'
    if parse_flagged_json(flagged_line) != ['root_a', 'root_b']:
        fail('parser did not parse a well-formed FLAGGED_JSON line correctly')



def test_markup_loss_soft_flag_ru():
    """S7 rec 1 (RU): a dropped {%..%} gloss wrapper is a SOFT, report-only signal —
    markup_wrapper_dropped fires at low severity and is NEVER a requeue trigger; a retained
    side-by-side {%German%} echo (required by the side-by-side convention) must NOT fire it."""
    from prompt_rule_audit import HIGH_CONFIDENCE_RISKS, semantic_risks

    def risks(german, russian):
        card = {'card': {'key1': 'x', 'iast': 'x', 'notes': '', 'records': [{
            'h': 'x', 'grammar': 'ind.', 'senses': [{
                'tag': '1', 'german': german, 'russian': russian,
                'equivalence_type': 'explanatory', 'source_type': 'lexicographic',
                'stratum': '', 'differentia': ''}]}]}}
        return semantic_risks(card)

    if 'markup_wrapper_dropped' in HIGH_CONFIDENCE_RISKS:
        fail('markup_wrapper_dropped must stay out of the requeue set (report-only)')
    dropped = [r for r in risks('{%nachgehen%}', 'следовать за')
               if r['id'] == 'markup_wrapper_dropped']
    if not dropped:
        fail('markup_wrapper_dropped did not fire on a dropped {%..%} wrapper')
    if dropped[0].get('level') != 'low' or dropped[0].get('high_confidence'):
        fail('markup_wrapper_dropped must be soft (low, non-high-confidence)')
    kept = risks('{%herfallen über%}', 'нападать на ({%herfallen über%})')
    if any(r['id'] == 'markup_wrapper_dropped' for r in kept):
        fail('markup_wrapper_dropped wrongly fired on a retained side-by-side {%..%} echo')



def test_p8_markup_loss_not_masked_by_unrelated_div():
    """P8 (H1422): MARKUP-LOSS used to sum {%..%} gloss-wrapper and <div> counts into ONE
    combined number before comparing, so a genuinely dropped gloss wrapper could be masked
    by an unrelated <div> gained in the english (net count unchanged: source 2 gloss/0 div
    vs output 0 gloss/2 div -> 2 == 2, no flag). Counting each marker class separately
    catches this; test_markup_loss_soft_flag_en (below) covers the un-masked ordinary case
    end-to-end through the CLI."""
    from audit_window_en import audit_sense
    _, soft = audit_sense('{%to fall upon%} {%to attack%}',
                          '<div n="1">to fall upon</div><div n="2">to attack</div>')
    if not any(f.startswith('MARKUP-LOSS') for f in soft):
        fail('MARKUP-LOSS must fire when both {%..%} wrappers are dropped, even though an '
             'unrelated <div> count masks the OLD combined-sum comparison: %r' % soft)



def test_markup_loss_soft_flag_en():
    """S7 rec 1 (EN): dropped {%..%} gloss wrappers are the dominant EN residual; the EN gate
    must flag them as SOFT MARKUP-LOSS — counted in the report but never hard, so --strict
    still exits 0 when MARKUP-LOSS is the only issue on a non-null card."""
    from audit_window_en import is_hard
    if is_hard('MARKUP-LOSS'):
        fail('MARKUP-LOSS must be a SOFT flag, never hard')
    fixture = {'meta': {'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': '1', 'senses': [{'tag': '1',
             'german': '{%to fall upon%} {%to attack%}',
             'english': 'to fall upon, to attack'}]}]}},
    ]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    report_path = wf_path + '.report.json'
    en_audit = os.path.join(HERE, 'audit_window_en.py')
    try:
        run([sys.executable, en_audit, wf_path, '--no-mw', '--strict', '--report', report_path],
            expect=0)
        rep = json.load(open(report_path, encoding='utf-8'))
        if rep.get('flag_counts', {}).get('MARKUP-LOSS', 0) < 1:
            fail('EN gate did not count the dropped {%..%} wrappers as MARKUP-LOSS')
        if rep.get('strict_reasons'):
            fail('a soft MARKUP-LOSS must not produce a strict failure reason')
    finally:
        os.remove(wf_path)
        if os.path.exists(report_path):
            os.remove(report_path)



def test_en_de_residue_french_guard():
    """EN analogue of the 2026-07-03 RU 'du'-vs-French collision fix (prompt_rule_audit.py):
    'des' is both a German article ("des Todes") and a French partitive article (as in "de
    basse extraction", a stock B&R euphemism for "of low birth"). gen_fidelity_judge_en.py's
    prompt explicitly preserves French literals verbatim, so a bare 'des' hit alongside
    another confirming French word must NOT fire DE-RESIDUE; genuine German residue ('des
    Todes', no other French markers) still must."""
    from audit_window_en import audit_sense
    _, soft_french = audit_sense('{%des basse extraction%}', 'des basse extraction')
    if any(s.startswith('DE-RESIDUE') for s in soft_french):
        fail('DE-RESIDUE wrongly fired on a preserved French literal ("des basse extraction")')
    _, soft_german = audit_sense('{%Todesangst%}', 'fear of des Todes')
    if not any(s.startswith('DE-RESIDUE') for s in soft_german):
        fail('DE-RESIDUE did not fire on genuine German residue ("des Todes")')



def test_p7_missing_en_not_fired_on_xref_only_residue():
    """P7 (H1422): has_gloss used to fire on ANY non-empty prose residue, so a genuinely
    non-target sense whose German is only a cross-reference apparatus ('Vgl. {#foo#} fgg.')
    hard-failed MISSING-EN the moment its english field was correctly left empty (there was
    nothing to translate). The neighboring test above only ever exercises xref rows WITH a
    non-empty english, which can never trigger MISSING-EN regardless of has_gloss -- this
    test is the one that actually reproduces the defect."""
    from audit_window_en import audit_sense
    hard, soft = audit_sense('Vgl. {#foo#} fgg.', '')
    if 'MISSING-EN' in hard:
        fail('MISSING-EN must not fire on a pure cross-reference row with empty english '
             '(nothing was ever a translation target here): %r' % hard)
    if 'XREF-ONLY' not in soft:
        fail('XREF-ONLY should still fire on this row')
    # CONTROL: a real gloss with empty english IS a genuine MISSING-EN.
    hard_real, _ = audit_sense('{%to speak%}', '')
    if 'MISSING-EN' not in hard_real:
        fail('MISSING-EN must still fire when real gloss prose exists and english is empty')

