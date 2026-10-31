"""test_tm_and_fragments — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_tm_and_fragments.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_autosplit_topup_targets_and_reassembles():
    """Item-1 (ka): a partial card's missing_fragments drive a TARGETED top-up, not a full
    re-split. Using ka's real 81-fragment / 41-group plan: mark 2 groups missing (the rest
    resolved via frag_prov), assert topup_fragments targets ONLY those 2 groups' fragments,
    then feed synthetic recoveries and assert stitch_topup reassembles a COMPLETE ka card."""
    import autosplit_requeue as ar
    import translation_memory as tm
    from window_common import input_paths, read_text
    if not os.path.exists(input_paths('ka')[0]):
        return  # ka input not present in this checkout — nothing to assert
    raw = read_text(input_paths('ka')[0])
    groups = ar.frag_groups(raw)
    if len(groups) < 3:
        return
    lang, field = 'ru', 'russian'
    missing_gi = {len(groups) - 1, len(groups) - 2}     # the last 2 groups fail

    def senses_for(text, marker):
        return [{'tag': '1', 'german': text[:16], 'russian': marker,
                 'equivalence_type': 'equivalent', 'source_type': 'attested',
                 'stratum': '', 'differentia': ''}]

    frag_prov, missing_ids = [], []
    for gi, g in enumerate(groups):
        for fi, (si, pi, text) in enumerate(g):
            if gi in missing_gi:
                missing_ids.append('g%d:f%d' % (gi + 1, fi))
            else:
                frag_prov.append({'fsha': tm.frag_address(lang, text),
                                  'senses': senses_for(text, 'resolved')})
    partial_card = {'key1': 'ka', 'iast': 'ka', 'partial': True,
                    'missing_fragments': missing_ids, 'frag_prov': frag_prov,
                    'records': [{'h': '1', 'senses': []}]}
    wf = {'meta': {'root': 'ka', 'lang': lang},
          'results': [{'key': 'ka', 'card': partial_card}]}
    fd, wf_path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    with open(wf_path, 'w', encoding='utf-8') as f:
        json.dump(wf, f, ensure_ascii=False)
    try:
        cards = ar.topup_fragments(wf_path, lang)
    finally:
        os.remove(wf_path)
    if len(cards) != 1:
        fail('topup_fragments did not surface the single partial ka card')
    c = cards[0]
    expected_missing = sum(len(groups[gi]) for gi in missing_gi)
    if len(c['missing']) != expected_missing:
        fail('topup targeted %d fragments, expected %d (the 2 missing groups only)'
             % (len(c['missing']), expected_missing))
    if len(c['missing']) >= len(c['plan']):
        fail('topup did not reduce the fragment set — it re-planned the whole card')

    # feed synthetic recoveries for the missing fragments -> expect a COMPLETE card
    manifest_card = {'orig': c['orig'], 'iast': c['iast'], 'h': c['h'],
                     'plan': [{'s': r['s'], 'p': r['p'], 'fsha': r['fsha'],
                               'fk': r['fk'], 'missing': r['missing']} for r in c['plan']],
                     'resolved': c['resolved']}
    got = {ar.fk_of('ka', si, pi): senses_for(text, 'recovered')
           for (si, pi, text) in c['missing']}
    results, still_missing = ar.stitch_topup([manifest_card], got, field)
    row = results[0]
    if row['partial'] or not row['card']:
        fail('topup-merge left ka partial after every missing fragment was recovered')
    if still_missing:
        fail('no fragments should remain missing after full recovery')
    n_senses = len({r['s'] for r in c['plan']})
    if len(row['card']['records'][0]['senses']) != n_senses:
        fail('reassembled ka is missing senses: %d vs %d source sense-ords'
             % (len(row['card']['records'][0]['senses']), n_senses))

    # a still-failing missing fragment must keep the card partial (never silently complete)
    partial_got = dict(got)
    a_missing = ar.fk_of('ka', c['missing'][0][0], c['missing'][0][1])
    partial_got[a_missing] = None
    presults, pmissing = ar.stitch_topup([manifest_card], partial_got, field)
    if not presults[0]['partial'] or a_missing not in (pmissing.get('ka') or []):
        fail('a still-failing fragment must keep the card partial with its fk recorded')



def test_translation_memory_addressing():
    """TM sidecar: content-addressing rules — only sub-cards with one agreed source SHA and a
    complete translation are cached; SHA-disagreement / missing-translation / no-SHA are
    skipped (never guessed), and reconstruction rebuilds the wf-card sense shape."""
    import translation_memory as tm
    tm.selftest()   # raises AssertionError on any rule violation



def test_tm_pre_resolves_cards():
    """--tm plumbing end-to-end: a card whose source SHA is in the TM is pre-resolved (emitted
    in TM_RESOLVED, excluded from every translate lane), and the total-accounting invariant
    (tm ∪ batched ∪ presplit == selected, disjoint) holds. Uses a real root's on-disk inputs."""
    import gen_opt_harness2 as gh
    from window_common import rootmap_path, input_paths, sha256_file, read_text
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return  # inputs not present in this checkout — nothing to assert
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])][:6]
    if len(keys) < 3:
        return
    cached = keys[:2]
    fd, tmfile = tempfile.mkstemp(suffix='.json'); os.close(fd)
    try:
        entries = {}
        for k in cached:
            raw_path = input_paths(k)[0]
            sha = sha256_file(raw_path)
            entries['ru:%s' % sha] = {'card': {'key1': k, 'iast': None,
                'records': [{'h': None, 'senses': [{'tag': '1', 'german': read_text(raw_path), 'russian': 'р',
                    'equivalence_type': 'equivalent', 'source_type': 'attested',
                    'stratum': '', 'differentia': ''}]}]}, 'src_key': k}
        with open(tmfile, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.translation_memory.v1', 'lang': 'ru',
                       'entries': entries}, f, ensure_ascii=False)
        js, batches = gh.build(root, keys, rootmap, 12000, tm_path=tmfile)
        import re as _re
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        tm_hits = set(meta['tm_hits'])
        if tm_hits != set(cached):
            fail('TM should pre-resolve exactly the cached keys, got %s' % sorted(tm_hits))
        batched = {k for b in meta['batches'] for k in b}
        if tm_hits & batched:
            fail('a TM-resolved card must not also be in a translate batch')
        if tm_hits & set(meta['presplit_keys']):
            fail('a TM-resolved card must not also be in the presplit lane')
        union = tm_hits | batched | set(meta['presplit_keys'])
        if union != set(keys):
            fail('accounting: tm ∪ batched ∪ presplit must equal selected keys')
        inputs = json.loads(_re.search(r'^const INPUTS = (.*)$', js, _re.M).group(1))
        ph = json.loads(_re.search(r'^const PH = (.*)$', js, _re.M).group(1))
        if tm_hits & set(inputs):
            fail('TM-resolved cards must not be inlined in INPUTS: %s' % sorted(tm_hits & set(inputs)))
        if tm_hits & set(ph):
            fail('TM-resolved cards must not be inlined in PH: %s' % sorted(tm_hits & set(ph)))
        if set(inputs) != batched | set(meta['presplit_keys']):
            fail('INPUTS must contain exactly agent-reachable keys')
    finally:
        try:
            os.remove(tmfile)
        except OSError:
            pass



def test_tm_card_sane_rejects_zero_marker_drift():
    """A cached card with zero citations/Sanskrit markers must not satisfy a cited source."""
    import gen_opt_harness2 as gh
    raw = '{#agni#}¦ Feuer <ls>RV. 1</ls>.'
    # Fixtures are schema-complete (iast/notes/h/grammar) so the B03 completeness guard
    # passes and the DRIFT check -- this test's actual claim -- is the one that refuses.
    card = {'key1': 'agni', 'iast': 'agní', 'notes': '', 'records': [
        {'h': 'agni', 'grammar': 'm.', 'senses': [{'tag': '1', 'german': 'Feuer',
                                                   'russian': 'огонь'}]}]}
    ok, why = gh.tm_card_sane(card, 'ru', 'russian', raw)
    if ok or '<ls>' not in why:
        fail('zero-<ls> cached card must be refused for cited source, got ok=%r why=%r' %
             (ok, why))
    raw2 = '{#agni#}¦ Feuer.'
    card2 = {'key1': 'agni', 'iast': 'agní', 'notes': '', 'records': [
        {'h': 'agni', 'grammar': 'm.', 'senses': [{'tag': '1', 'german': 'Feuer',
                                                   'russian': 'огонь'}]}]}
    ok2, why2 = gh.tm_card_sane(card2, 'ru', 'russian', raw2)
    if ok2 or '{#' not in why2:
        fail('zero-{# cached card must be refused for Sanskrit-marked source, got ok=%r why=%r' %
             (ok2, why2))



def test_tm_auto_no_sidecar_metadata():
    """Default CLI semantics are --tm=auto: if the sidecar is missing, generation continues
    normally and records the no-op in META instead of silently changing lanes."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import rootmap_path, input_paths
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])][:3]
    if not keys:
        return
    missing_tm = os.path.join(tempfile.gettempdir(), 'missing_pwg_tm_selftest_%s.json' % os.getpid())
    try:
        os.remove(missing_tm)
    except OSError:
        pass
    js, _batches = gh.build(root, keys, rootmap, 12000, tm_path=missing_tm, tm_auto=True)
    meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
    if not meta.get('tm_auto'):
        fail('META.tm_auto must be true for --tm=auto/default generation')
    if meta.get('tm_available'):
        fail('META.tm_available must be false when the auto sidecar is absent')
    if meta.get('tm_cards') != 0 or meta.get('tm_hits'):
        fail('missing auto TM sidecar must not pre-resolve any cards')
    owed = {k for b in meta['batches'] for k in b} | set(meta['presplit_keys']) | set(meta['degenerate_passthrough_keys'])
    if owed != set(keys):
        fail('missing auto TM sidecar must keep every selected key owed/accounted')



def test_suggest_tm_does_not_skip_agents():
    """Suggestion TM is prompt context only: it must appear in META/SUGGEST_TM but leave
    tm_hits empty and keep the selected key owed by a normal translate lane."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import rootmap_path, input_paths
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])][:1]
    if not keys:
        return
    with tempfile.TemporaryDirectory() as tmp:
        suggest = os.path.join(tmp, 'translation_memory.suggest.ru.jsonl')
        with open(suggest, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': 'pwg.translation_memory.suggest.v1',
                                'lang': 'ru', 'key': keys[0],
                                'score_de_fragment': 0.4,
                                'score_sa_headword': 1.0,
                                'score_semantic_tag': 0.7,
                                'score_combined': 0.88,
                                'trust_level': 'suggestion', 'reuse_policy': 'suggest_only',
                                'source_kind': 'curated_sa_ru_terminology',
                                'provenance_note': 'fixture curated term',
                                'text': 'advisory only'}, ensure_ascii=False) + '\n')
            f.write(json.dumps({'schema': 'pwg.translation_memory.suggest.v1',
                                'lang': 'ru', 'key': keys[0],
                                'trust_level': 'suggestion', 'reuse_policy': 'suggest_only',
                                'source_kind': 'mw_seed',
                                'score_combined': 1.0,
                                'text': 'must be filtered'}, ensure_ascii=False) + '\n')
        js, _batches = gh.build(root, keys, rootmap, 12000, tm_path=None, suggest_tm_path=suggest)
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        suggest_const = json.loads(_re.search(r'^const SUGGEST_TM = (.*)$', js, _re.M).group(1))
        if meta.get('tm_hits') or meta.get('tm_cards') != 0:
            fail('suggestion TM must not create exact TM hits')
        if meta.get('suggest_tm_cards') != keys:
            fail('suggestion TM metadata must list the advisory key')
        if keys[0] not in suggest_const:
            fail('generated harness must emit SUGGEST_TM advisory rows')
        if len(suggest_const[keys[0]]) != 1:
            fail('malformed/raw-MW RU suggestion row must be filtered before prompt injection')
        if suggest_const[keys[0]][0].get('score_de_fragment') != 0.4:
            fail('separate fuzzy evidence scores must survive load/render round-trip')
        for needle in ('score_de_fragment', 'score_sa_headword', 'score_semantic_tag',
                       "'de='", "'sa='", "'tag='"):
            if needle not in js:
                fail('suggestion prompt must render separate evidence-channel scores')
        owed = {k for b in meta['batches'] for k in b} | set(meta['presplit_keys']) | set(meta['degenerate_passthrough_keys'])
        if keys[0] not in owed:
            fail('suggestion TM must not remove the key from agent work lanes')



def test_tm_publication_fixtures_validate():
    """Tracked fixtures pin the publication-grade TM row contract."""
    import translation_memory as tm
    valid = os.path.join(SRC, 'fixtures', 'translation_memory_valid.fixture.jsonl')
    invalid = os.path.join(SRC, 'fixtures', 'translation_memory_invalid.fixture.jsonl')
    rows = [json.loads(line) for line in open(valid, encoding='utf-8') if line.strip()]
    ok, why = tm.validate_suggestion_row(rows[0], lang='ru')
    if not ok:
        fail('valid suggestion fixture rejected: %s' % why)
    ok, why = tm.validate_frag_entry(rows[1], lang='ru')
    if not ok:
        fail('valid fragment fixture rejected: %s' % why)
    bad = [json.loads(line) for line in open(invalid, encoding='utf-8') if line.strip()]
    reasons = []
    for row in bad:
        ok, why = tm.validate_suggestion_row(row, lang='ru')
        if ok:
            fail('invalid suggestion fixture unexpectedly passed')
        reasons.append(why)
    if 'raw MW English seed is forbidden for RU' not in reasons:
        fail('invalid fixture must pin raw MW English rejection')
    if 'score_de_fragment must be a number 0..1' not in reasons:
        fail('invalid fixture must pin score-channel range validation')



def test_degenerate_passthrough_accounted():
    """A safely-degenerate cross-reference stub is emitted as an accounted, SCHEMA-VALID no-LLM row
    and is excluded from translation lanes. N-3/R7 (C-07): the card MUST pass
    validate_final_card_schema (record h + grammar present, not null) so one xref stub can no longer
    make save_and_audit refuse a whole paid window -- and this assertion must never silently skip on
    an absent file fixture."""
    import re as _re
    import gen_opt_harness2 as gh
    import validate_final_card_schema as vs
    # Inline stub -> no filesystem dependency, so the schema assertion below can never be skipped.
    card = gh.degenerate_passthrough_card('ab~~h0_zz_pw', '=== LAYER: PW ===\n\nvgl. {#agni#}',
                                          '[]', 'russian')
    if not card or not card.get('degenerate_passthrough'):
        fail('inline vgl.-stub should qualify for conservative degenerate pass-through')
    vs.validate_card(card)                     # R7/C-07: raises on any schema violation
    rec = card['records'][0]
    if rec.get('h') is None or 'grammar' not in rec:
        fail('degenerate record must carry a non-null h and a grammar field (RECORD_REQUIRED)')
    # File-fixture-dependent accounting -- an EXPLICIT conditional, never a silent top-of-function return.
    from window_common import input_paths, read_text
    rp, pp = input_paths('ab')
    if os.path.exists(rp) and os.path.exists(pp):
        js, batches = gh.build('ab', ['ab'], None, 12000, nominal=True, tm_path=None)
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        if meta.get('degenerate_passthrough_keys') != ['ab']:
            fail('META.degenerate_passthrough_keys must account for the stub key')
        if batches or meta.get('presplit_keys'):
            fail('a degenerate pass-through key must not also enter an agent translation lane')
        if 'const DEGENERATE_RESOLVED' not in js or 'degenerate_passthrough: true' not in js:
            fail('generated harness must emit explicit degenerate pass-through rows')



def test_degenerate_passthrough_no_german_in_target():
    """P3 (H1422) as amended by H3658: a degenerate cross-reference stub must never carry
    verbatim German in the target field ('vgl.', 's.', 'ff.' -- particles the
    german_residue_scan/GERMAN_RESIDUE wordlists do not even cover, so the leak was
    previously undetectable by any existing audit).

    P3 bought that guarantee by leaving the field EMPTY, which then auto-failed every such
    card on empty_russian + dropped_sanskrit_span. H3658 keeps the guarantee and drops the
    emptiness: the RU lane now renders the apparatus (bare closed-vocabulary German -> Russian,
    `{#..#}` spans and whole <ab>/<ls>/<hom> regions verbatim), and falls back to the empty
    field whenever it cannot. The EN lane is unchanged -- an EN vocabulary is not ruled."""
    import gen_opt_harness2 as gh
    raw = '=== LAYER: PW ===\n\nvgl. {#agni#}'

    # EN: unchanged, still the P3 empty field.
    card = gh.degenerate_passthrough_card('ab~~h0_zz_pw', raw, '[]', 'english')
    if not card:
        fail('inline vgl.-stub should qualify for conservative degenerate pass-through')
    sense = card['records'][0]['senses'][0]
    if sense.get('english') != '':
        fail('the EN degenerate lane must still emit an empty target field, got %r'
             % sense.get('english'))

    # RU: rendered, and the German particle is GONE rather than carried.
    card = gh.degenerate_passthrough_card('ab~~h0_zz_pw', raw, '[]', 'russian')
    sense = card['records'][0]['senses'][0]
    ru = sense.get('russian') or ''
    if not ru:
        fail('H3658: the RU degenerate lane must render the apparatus, not leave it empty')
    if 'vgl' in ru.lower():
        fail('verbatim German particle leaked into the russian field: %r' % ru)
    if '\u0441\u0440.' not in ru:
        fail('bare `vgl.` must render as «ср.», got %r' % ru)
    if '{#agni#}' not in ru:
        fail('the {#..#} Sanskrit span must survive into the target field, got %r' % ru)
    if 'vgl' not in sense.get('german', ''):
        fail('the german field must still carry the original source text for editorial reference')

    # An <ab> token stays German ON PURPOSE -- the article site resolves it via
    # pwg_ab_ru.RU_MAP, so rewriting it here would double-translate it.
    tagged = '=== LAYER: PW ===\n\n{#paTin#} <ab>s. u.</ab> {#paT#}.'
    card = gh.degenerate_passthrough_card('paTin~~h0_zz_pw', tagged, '[]', 'russian')
    ru = card['records'][0]['senses'][0]['russian']
    if '<ab>s. u.</ab>' not in ru:
        fail('an <ab> token must be copied verbatim for the site to resolve, got %r' % ru)

    # Fail closed: an unrenderable residue falls back to P3's empty field rather than leaking.
    import xref_vocab
    if xref_vocab.render_xref_ru('Bedeutung {#agni#}') is not None:
        fail('an out-of-vocabulary German word must not be rendered')



def test_degenerate_passthrough_rejects_glosses():
    import gen_opt_harness2 as gh
    import perf_preflight as pp
    raw = """=== LAYER: PWG — MAIN ENTRY ===
{#agni#}¦ {%Feuer%}, <ls>RV.</ls>
"""
    if gh.degenerate_passthrough_card('agni', raw, '{"key1":"agni"}', 'russian'):
        fail('cards with German gloss blocks must not enter deterministic pass-through')
    if pp.near_degenerate_reason('agni', raw, '{"key1":"agni"}', 'russian'):
        fail('cards with German gloss blocks must not be suggested as near-degenerate stubs')
    correction = """=== LAYER: PWG — MAIN ENTRY ===
{#as#}¦ <ab>vgl.</ab> mit {#aBi#} <ab>Z.</ab> 9 <ab>v. u.</ab> lies: {#etattrikam#}.
"""
    if gh.degenerate_passthrough_card('as', correction, '{"key1":"as"}', 'russian'):
        fail('editorial correction prose (lies:) must stay out of deterministic pass-through')
    if 'editorial correction prose' not in (pp.near_degenerate_reason('as', correction, '{"key1":"as"}', 'russian') or ''):
        fail('preflight should explain why correction prose is report-only')
    strike = """=== LAYER: PWG — MAIN ENTRY ===
{#vid#}¦ <ab>Z.</ab> 5 ist ein {#tasya#} zu streichen.
"""
    if gh.degenerate_passthrough_card('vid', strike, '{"key1":"vid"}', 'russian'):
        fail('editorial correction prose (streichen) must stay out of deterministic pass-through')



def test_frag_tm_reuse():
    """Fragment-level --tm: a card that plan()-splits into >=2 fragments, with ONE fragment
    in the fragment sidecar, emits a FRAG_TM group-shape mirroring FRAGS where exactly the
    cached fragment slot is filled (served at runtime with NO agent call) and the rest are
    null. The card itself stays in a translate lane (reuse is inside selfHeal, not card
    removal), so the whole-card accounting invariant is untouched."""
    import re as _re
    import gen_opt_harness2 as gh
    import translation_memory as tm
    from autosplit_requeue import plan as split_plan
    from window_common import rootmap_path, input_paths, read_text
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return  # inputs not present in this checkout — nothing to assert
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])]
    # pick the first card that actually splits into >=2 deterministic fragments
    target, plan0 = None, None
    for k in keys:
        pl = split_plan(read_text(input_paths(k)[0]))
        if len(pl) >= 2:
            target, plan0 = k, pl
            break
    if not target:
        return
    d = tempfile.mkdtemp()
    try:
        # card-level TM: empty (so `target` is NOT a whole-card hit); fragment sidecar caches
        # exactly plan0[0]. The sidecar MUST sit next to the card TM under the exact basename.
        tmfile = os.path.join(d, 'translation_memory.ru.json')
        with open(tmfile, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.translation_memory.v1', 'lang': 'ru', 'entries': {}}, f)
        fsha0 = tm.frag_address('ru', plan0[0][2])
        senses0 = [{'tag': '1', 'german': plan0[0][2][:20], 'russian': 'кэш',
                    'equivalence_type': 'equivalent', 'source_type': 'attested',
                    'stratum': '', 'differentia': ''}]
        # H1386: the fixture must be a VALID frag-TM v2 row (per-sense owners) -- R6 made a
        # v1 ownerless row never-live-served, so the old v1 fixture only ever "passed" when
        # the gam inputs were absent and the test returned early (vacuous in CI; failed on
        # any second suite run in the same checkout, once earlier tests left the fixtures).
        owners0 = [['gam', '']]
        with open(os.path.join(d, 'translation_memory.frag.ru.jsonl'), 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': tm.FRAG_SCHEMA_V2, 'lang': 'ru',
                                'fsha': fsha0, 'src_key': target, 'senses': senses0,
                                'owners': owners0, 'trust_level': tm.TRUST_MACHINE,
                                'gate_status': 'machine_gated', 'reuse_policy': 'auto_exact'},
                               ensure_ascii=False) + '\n')
        js, _batches = gh.build(root, [target], rootmap, 12000, tm_path=tmfile)

        def const(name):
            return json.loads(_re.search(r'^const %s = (.*)$' % name, js, _re.M).group(1))
        meta = const('META')
        frags, frag_tm = const('FRAGS'), const('FRAG_TM')
        if target not in frag_tm:
            fail('the card with a cached fragment must appear in FRAG_TM')
        if target not in meta.get('frag_tm_cards', []):
            fail('meta.frag_tm_cards must list the reusing card')
        if meta.get('frag_tm_fragments') != 1:
            fail('exactly one fragment should be cached, got %r' % meta.get('frag_tm_fragments'))
        # shape mirrors FRAGS exactly
        gv, fv = frags[target], frag_tm[target]
        if [len(g) for g in gv] != [len(g) for g in fv]:
            fail('FRAG_TM group shape must mirror FRAGS')
        filled = [(gi, fi) for gi, g in enumerate(fv) for fi, slot in enumerate(g) if slot]
        if filled != [(0, 0)]:
            fail('only the first fragment (the cached one) must be filled, got %s' % filled)
        # the filled slot carries the cached senses; its FRAGS sibling carries the matching fsha
        # R6 slot shape: {'senses': [...], 'owners': [...]} (never a bare senses list).
        if fv[0][0]['senses'][0]['russian'] != 'кэш':
            fail('cached fragment slot must carry the sidecar senses')
        if fv[0][0]['owners'] != owners0:
            fail('cached fragment slot must carry the v2 per-sense owners')
        if gv[0][0].get('fsha') != fsha0:
            fail('FRAGS fragment must carry the content address used for the cache lookup')
        # whole-card accounting: reuse happens INSIDE selfHeal, so the card is still owed by a
        # translate lane (batch or presplit), never silently dropped.
        batched = {k for b in meta['batches'] for k in b}
        if target not in (batched | set(meta['presplit_keys'])):
            fail('a fragment-reusing card must still be owed by a translate lane')
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_frag_groups_presplit_parity():
    """H304: frag_groups must reconstruct the SAME partition the harness used to mint the
    gN:fM ids. A presplit card groups at PRESPLIT_GROUP_CITE_BUDGET with a sense count_cap
    (H189), not at SELFHEAL_GROUP_BUDGET — reconstructing with the heal budget mis-maps the
    ids for exactly the giant cards topup exists for."""
    import autosplit_requeue as ar
    from gen_opt_harness2 import _group_by_budget
    fixture = [(si, 0, 'sense %d <ls>A</ls> <ls>B</ls>' % si) for si in range(1, 41)]
    old_plan = ar.plan
    ar.plan = lambda raw, ls_budget=None: fixture
    try:
        meta = {'presplit_keys': ['X'], 'presplit_group_cite_budget': 60,
                'presplit_group_sense_cap': 18, 'selfheal_group_budget': 12}
        sizer = lambda f: 1 + f[2].count('<ls')
        want_presplit = _group_by_budget(fixture, sizer, 60, count_cap=18)
        want_heal = _group_by_budget(fixture, sizer, 12)
        if want_presplit == want_heal:
            fail('fixture too small — presplit and heal partitions must differ for the test')
        got_presplit = ar.frag_groups('ignored', meta=meta, key='X')
        if got_presplit != want_presplit:
            fail('frag_groups(presplit key) does not match the harness presplit partition '
                 '(%d vs %d groups)' % (len(got_presplit), len(want_presplit)))
        got_heal = ar.frag_groups('ignored', meta=meta, key='Y')
        if got_heal != want_heal:
            fail('frag_groups(non-presplit key) must keep the heal-budget partition')
        got_legacy = ar.frag_groups('ignored')
        if got_legacy != want_heal:
            fail('frag_groups without meta must keep the pre-H304 heal-budget behavior')
    finally:
        ar.plan = old_plan



def test_defect_fragment_denylist_round_trip():
    """H304 gate-outcome memory: a defect card's frag_prov fshas (requeue.defect.fshas.txt)
    are appended to the TM denylist by requeue_from_audit, card addresses are denylisted from
    their raw input sha, and the runtime loaders then refuse to serve either class — a
    gate-flagged card/fragment is never re-served by --tm=auto."""
    import requeue_from_audit as rfa
    import translation_memory as tm
    tmp = tempfile.mkdtemp()
    inp = os.path.join(tmp, 'input')
    os.makedirs(inp)
    deny_path = os.path.join(tmp, 'denylist.jsonl')
    key = 'h304root~~h0'
    raw_path = os.path.join(inp, key + '.raw.txt')
    with open(raw_path, 'w', encoding='utf-8') as f:
        f.write('flagged raw card')
    card_address = 'ru:%s' % sha256(raw_path)
    fsha_good = tm.frag_address('ru', 'clean fragment')
    fsha_bad = tm.frag_address('ru', 'flagged fragment')
    fsha_file = os.path.join(tmp, 'requeue.defect.fshas.txt')
    with open(fsha_file, 'w', encoding='utf-8') as f:
        f.write(fsha_bad + '\n')
    old_dp = rfa.translation_memory.denylist_path
    old_inp = rfa.INP
    rfa.translation_memory.denylist_path = lambda path=None: deny_path
    rfa.INP = inp
    try:
        n, nf = rfa.append_tm_denylist('h304root', [key], 'defect', lang='ru',
                                       fsha_file=fsha_file, path=deny_path)
    finally:
        rfa.translation_memory.denylist_path = old_dp
        rfa.INP = old_inp
    if (n, nf) != (1, 1):
        fail('append_tm_denylist defect deny count: got %r, want (1, 1)' % ((n, nf),))
    deny = tm.load_denylist(deny_path)
    if card_address not in deny['addresses']:
        fail('defect card address missing from the loaded denylist address set')
    if fsha_bad not in deny['frags']:
        fail('defect fsha missing from the loaded denylist frag set')
    card_tm = os.path.join(tmp, 'translation_memory.ru.json')
    with open(card_tm, 'w', encoding='utf-8') as f:
        json.dump({'schema': tm.CARD_SCHEMA, 'lang': 'ru', 'entries': {
            card_address: {'id': card_address,
                           'card': {'records': [{'senses': [{'russian': 'bad cached card'}]}]},
                           'trust_level': tm.TRUST_MACHINE,
                           'gate_status': 'machine_gated',
                           'reuse_policy': 'auto_exact'}}}, f, ensure_ascii=False)
    if tm.load_tm('ru', card_tm, denylist=deny_path):
        fail('denylisted defect card still served by load_tm')
    senses = [{'tag': '1', 'german': 'x', 'russian': 'y'}]
    sidecar = os.path.join(tmp, 'translation_memory.frag.ru.jsonl')
    with open(sidecar, 'w', encoding='utf-8') as f:
        for fsha in (fsha_good, fsha_bad):
            f.write(json.dumps({'schema': tm.FRAG_SCHEMA_V2, 'fsha': fsha, 'senses': senses,
                                'owners': [['x', '']]}) + '\n')   # R6: v2 (live-reusable)
    cache = tm.load_frag_tm('ru', sidecar, denylist=deny_path)
    if fsha_bad in cache:
        fail('denylisted fragment still served by load_frag_tm')
    if fsha_good not in cache:
        fail('clean fragment wrongly dropped by the denylist')
    # transient requeues must not denylist anything
    n, nf = rfa.append_tm_denylist('h304root', [], 'transient', lang='ru', path=deny_path)
    if (n, nf) != (0, 0):
        fail('transient requeue must never append denylist rows')



def test_opt7_last_audit_tm_refuse_without_no_tm():
    """H2228 / OPT-7 / FINDINGS §31 residual: last-audit defect outcome stamps the denylist
    so a default --tm=auto path (no operator --no-tm) still refuses the failed hash and
    forces real re-translate work. gam-class synthetic fixture:

      * defect key has a TM hit that would otherwise make agent_expected_after_tm=0
      * write_reports(--write-requeue) stamps denylist from requeue_defect
      * load_tm then refuses the failed address; clean held-out key still serves
      * crashed audit does NOT stamp (blast-radius control)
      * false-invalidation: clean key never denylisted
    """
    import translation_memory as tm
    from window_reports import write_reports, _stamp_last_audit_denylist
    tmp = tempfile.mkdtemp(prefix='pwg_audit_ephemeral_opt7_')
    inp = os.path.join(tmp, 'input')
    os.makedirs(inp)
    # gam-class: one defect key + one clean key (held-out clean TM must survive)
    defect_key = 'gam~~h0_zz_pw03'
    clean_key = 'gam~~h0_zz_clean'
    for key, body in ((defect_key, 'gam flagged defect raw COVERAGE-LOW'),
                      (clean_key, 'gam clean held-out raw')):
        with open(os.path.join(inp, key + '.raw.txt'), 'w', encoding='utf-8') as f:
            f.write(body)
    defect_addr = 'ru:%s' % sha256(os.path.join(inp, defect_key + '.raw.txt'))
    clean_addr = 'ru:%s' % sha256(os.path.join(inp, clean_key + '.raw.txt'))
    fsha_bad = tm.frag_address('ru', 'gam defect fragment body')
    fsha_good = tm.frag_address('ru', 'gam clean fragment body')

    # Pre-stamp synthetic TM as if a prior run cached both (the §31 trap: defect is cached)
    card_tm = os.path.join(tmp, 'translation_memory.ru.json')
    with open(card_tm, 'w', encoding='utf-8') as f:
        json.dump({'schema': tm.CARD_SCHEMA, 'lang': 'ru', 'entries': {
            defect_addr: {
                'id': defect_addr,
                'card': {'records': [{'senses': [
                    {'russian': 'cached defect %d' % i} for i in range(47)]}]},
                'trust_level': tm.TRUST_MACHINE,
                'gate_status': 'machine_gated',
                'reuse_policy': 'auto_exact',
            },
            clean_addr: {
                'id': clean_addr,
                'card': {'records': [{'senses': [{'russian': 'cached clean'}]}]},
                'trust_level': tm.TRUST_MACHINE,
                'gate_status': 'machine_gated',
                'reuse_policy': 'auto_exact',
            },
        }}, f, ensure_ascii=False)
    # Without denylist both serve — proves the trap surface exists for this fixture
    before = tm.load_tm('ru', card_tm, denylist=os.path.join(tmp, 'empty_deny.jsonl'))
    if defect_addr not in before or clean_addr not in before:
        fail('fixture TM must serve both addresses before last-audit stamp')

    old_inp = os.environ.get('PWG_INPUT_DIR')
    os.environ['PWG_INPUT_DIR'] = inp
    try:
        report = {
            'workflow': 'wf_output_gam_opt7_fixture.json',
            'root': 'gam',
            'lang': 'ru',
            'keys': [defect_key, clean_key],
            'requeue': [defect_key],
            'requeue_transient': [],
            'requeue_defect': [defect_key],
            'requeue_defect_fshas': [fsha_bad],
            'crashed': [],
            'gates': {},
            'state': 'needs_requeue',
            'null_cards': [],
            'partial_cards': {},
            'failure_reasons': {},
        }
        write_reports(report, True, out_dir=tmp)
        stamp = report.get('tm_denylist_stamped') or {}
        if not stamp.get('stamped'):
            fail('write_reports must stamp last-audit denylist for defect keys: %r' % stamp)
        if stamp.get('cards', 0) < 1:
            fail('expected ≥1 card denylist row from defect raw: %r' % stamp)
        deny_path = stamp.get('denylist')
        if not deny_path or not os.path.exists(deny_path):
            fail('local last-audit denylist missing under ephemeral out_dir')
        after = tm.load_tm('ru', card_tm, denylist=deny_path)
        if defect_addr in after:
            fail('last-audit defect address still served by load_tm (OPT-7 refuse failed)')
        if clean_addr not in after:
            fail('clean held-out TM falsely invalidated by last-audit stamp')
        # Fragment lane: denylisted fsha refused; clean fsha still live
        senses = [{'tag': '1', 'german': 'x', 'russian': 'y'}]
        sidecar = os.path.join(tmp, 'translation_memory.frag.ru.jsonl')
        with open(sidecar, 'w', encoding='utf-8') as f:
            for fsha in (fsha_good, fsha_bad):
                f.write(json.dumps({'schema': tm.FRAG_SCHEMA_V2, 'fsha': fsha,
                                    'senses': senses, 'owners': [['x', '']]}) + '\n')
        frag = tm.load_frag_tm('ru', sidecar, denylist=deny_path)
        if fsha_bad in frag:
            fail('last-audit defect fsha still served by load_frag_tm')
        if fsha_good not in frag:
            fail('clean fragment falsely invalidated')
        # Default requeue path without operator --no-tm still forces real work for the
        # defect key: TM miss on the failed hash means agent_expected cannot be 0 solely
        # from that hit (simulate the gen_opt address lookup).
        hit_after_stamp = after.get(defect_addr)
        if hit_after_stamp is not None:
            fail('default-path TM hit must be None for last-audit-failed hash')
        # agent work residual: 1 defect key refused → non-zero real translate path
        agent_expected_after_tm = 0 if hit_after_stamp else 1
        if agent_expected_after_tm < 1:
            fail('gam-class fixture must prove non-zero real translate path after stamp')
        # Crashed audit must not stamp (false-invalidation / blast-radius control)
        crash_report = {
            'root': 'gam', 'lang': 'ru', 'keys': [clean_key],
            'requeue': [clean_key], 'requeue_defect': [clean_key],
            'requeue_defect_fshas': [], 'crashed': ['coverage'],
            'gates': {}, 'state': 'blocked',
        }
        crash_stamp = _stamp_last_audit_denylist(crash_report, tmp)
        if crash_stamp.get('stamped'):
            fail('crashed audit must not stamp denylist: %r' % crash_stamp)
        if 'false_invalidation_controls' not in (stamp or {}):
            fail('stamp status must document false-invalidation controls')
    finally:
        if old_inp is None:
            os.environ.pop('PWG_INPUT_DIR', None)
        else:
            os.environ['PWG_INPUT_DIR'] = old_inp



def test_frag_tm_fidelity_gate_and_override():
    """H321 item #3b: build_frags must NOT harvest a corrupt/blanked frag_prov
    (first-seen-wins previously let a hand-edited wf_output poison content-addressed
    fragment reuse), load_frag_tm must not SERVE such a row, and a later good harvest
    must be able to override a previously-cached corrupt row."""
    import translation_memory as tm
    # 1) frag_senses_sane: blank/malformed senses are rejected.
    if tm.frag_senses_sane([{'tag': '1', 'russian': 'фу'}], 'ru') is not True:
        fail('a sane ru fragment sense must pass frag_senses_sane')
    if tm.frag_senses_sane([{'tag': '1', 'russian': '  '}], 'ru') is not False:
        fail('a blank-translation fragment sense must fail frag_senses_sane')
    if tm.frag_senses_sane([], 'ru') is not False:
        fail('empty senses must fail frag_senses_sane')

    d = tempfile.mkdtemp()
    old_repo = tm.REPO
    try:
        tm.REPO = d
        good_src = '=== h ===\n1) foo <ls>ṚV.</ls>'
        bad_src = '=== h ===\n1) bar <ls>AV.</ls>'
        good_fsha = tm.frag_address('ru', good_src)
        bad_fsha = tm.frag_address('ru', bad_src)
        good_senses = [{'tag': '1', 'german': 'foo', 'russian': 'фу'}]
        blank_senses = [{'tag': '1', 'german': 'bar', 'russian': ''}]
        wf = {'meta': {'lang': 'ru', 'root': 'zz'}, 'results': [
            {'key': 'zz~~h0', 'card': {'key1': 'zz', 'records': [{'senses': good_senses}],
                                       'frag_prov': [{'fsha': good_fsha, 'senses': good_senses,
                                                      'owners': [['zz', '']]},   # R6: v2 (live-reusable)
                                                     {'fsha': bad_fsha, 'senses': blank_senses,
                                                      'owners': [['zz', '']]}]}}]}
        with open(os.path.join(d, 'wf_output.sc.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False)
        sidecar = os.path.join(d, 'frag.ru.jsonl')
        _p, added, _tot = tm.build_frags('wf_output.sc.*.json', 'ru', out=sidecar)
        served = tm.load_frag_tm('ru', sidecar)
        if good_fsha not in served:
            fail('a sane fragment must be harvested and served')
        if bad_fsha in served:
            fail('a corrupt (blank-sense) fragment must NOT be harvested/served')

        # 2) Later-good override: pre-seed a CORRUPT row for an fsha, then harvest a
        # good one for the same fsha — the good row must win at serve.
        d2 = tempfile.mkdtemp()
        try:
            tm.REPO = d2
            sidecar2 = os.path.join(d2, 'frag.ru.jsonl')
            with open(sidecar2, 'w', encoding='utf-8') as f:
                f.write(json.dumps({'schema': tm.FRAG_SCHEMA, 'lang': 'ru', 'fsha': good_fsha,
                                    'senses': [{'tag': '1', 'russian': ''}],  # corrupt
                                    'trust_level': tm.TRUST_MACHINE,
                                    'harvested_at': '2026-01-01T00:00:00Z'}, ensure_ascii=False) + '\n')
            if tm.load_frag_tm('ru', sidecar2):
                fail('serve-time filter must drop a corrupt historical row (empty served map)')
            with open(os.path.join(d2, 'wf_output.sc.zz.json'), 'w', encoding='utf-8') as f:
                json.dump(wf, f, ensure_ascii=False)
            tm.build_frags('wf_output.sc.*.json', 'ru', out=sidecar2)
            served2 = tm.load_frag_tm('ru', sidecar2)
            if good_fsha not in served2:
                fail('a later GOOD harvest must override a previously-cached corrupt row')
        finally:
            shutil.rmtree(d2, ignore_errors=True)
    finally:
        tm.REPO = old_repo
        shutil.rmtree(d, ignore_errors=True)



def test_denylist_torn_line_fails_loud():
    """P0.1 / H336-H3: translation_memory.load_denylist must FAIL loudly on a torn/
    undecodable JSONL line instead of continuing with a partial deny set — a silently-dropped
    denylist row is a correctness hole (a gate-rejected address quietly becomes TM-reusable
    again), the scariest single entry in the H335 collision matrix."""
    import translation_memory as tm
    d = tempfile.mkdtemp()
    path = os.path.join(d, 'denylist.jsonl')
    good = {'schema': 'pwg.translation_memory.denylist.v1', 'kind': 'card',
            'address': 'ru:deadbeef', 'key': 'x~~h0', 'root': 'x', 'lang': 'ru',
            'reason': 'requeue_defect', 'blocked_at': '2026-07-08T00:00:00Z'}
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(good, ensure_ascii=False) + '\n')
        f.write('{"kind": "card", "address": "ru:TORN_MID_LINE\n')   # deliberately truncated/torn
    proc = subprocess.run(
        [sys.executable, '-c',
         "import sys; sys.path.insert(0, %r); import translation_memory as tm; "
         "tm.load_denylist(%r)" % (HERE, path)],
        capture_output=True, text=True, encoding='utf-8')
    if proc.returncode == 0:
        fail('load_denylist must fail on a torn line, got success:\n%s\n%s'
             % (proc.stdout, proc.stderr))
    if 'DenylistError' not in proc.stderr or 'torn/undecodable denylist line' not in proc.stderr:
        fail('load_denylist must surface a DenylistError for a torn line, got:\n%s' % proc.stderr)



def test_strip_mask_tokens_clears_notes_stranded_anchor():
    # H858: the model sometimes MENTIONS a masking placeholder in its free-text
    # `notes` ("Masked span {T1} is a citation reference…"). Rendered verbatim
    # into the .merged.md blockquote, that mention made stage2_pregate misfire a
    # STRANDED-ANCHOR on an otherwise-clean card (7/15 no_pwg_w09 false positives).
    import _pilot_collect as pc
    if pc.strip_mask_tokens('Masked span {T1} is a citation.') != 'Masked span is a citation.':
        fail('strip_mask_tokens did not strip {T1} + tidy the gap')
    if pc.strip_mask_tokens('echoed {Tn} literal') != 'echoed literal':
        fail('strip_mask_tokens did not strip the literal {Tn} example token')
    if pc.strip_mask_tokens('plain note, no tokens') != 'plain note, no tokens':
        fail('strip_mask_tokens altered clean text')
    # integration: notes mentioning {T1} must not leak a placeholder into the render
    md = pc.render({'key': 'x~~h0_zz_pw', 'card': {
        'key1': 'x', 'iast': 'x', 'notes': 'Masked span {T1} is a citation reference.',
        'records': [{'h': '0', 'grammar': 'm.', 'senses': [
            {'tag': '1', 'german': 'a', 'russian': 'b', 'equivalence_type': 'equivalent',
             'source_type': 'lexicographic', 'stratum': '', 'differentia': ''}]}]}})
    if '{T1}' in md or '{Tn}' in md:
        fail('render() leaked a {Tn} masking token from notes into merged.md')



def test_every_stitch_emits_record_required():
    """C-02: the stitch must emit `h`/`grammar`, and must not collapse distinct homonyms.

    The defect: both stitch lanes built `records: [{senses}]`, discarding record-level h and
    grammar unconditionally, so promote wrote `h: null` -- 468 store rows over 20 sub-cards.
    That also violates schemas/pwg_ru_final_card.schema.json (record.required =
    {h, grammar, senses}), which nothing checked on live output (C-04).
    """
    import headless_worker as hw
    senses = [{'tag': '1'}, {'tag': '2'}, {'tag': '3'}]
    owners = [('1. bhid', 'm.'), ('1. bhid', 'm.'), ('2. bhid', 'f.')]
    records = hw.stitch_records(senses, owners)
    if len(records) != 2:
        fail('two distinct owners must yield two records, got %d' % len(records))
    if records[0]['h'] != '1. bhid' or records[1]['h'] != '2. bhid':
        fail('stitch dropped or reordered the record-level h: %r' % records)
    if records[0]['grammar'] != 'm.' or records[1]['grammar'] != 'f.':
        fail('stitch dropped the record-level grammar: %r' % records)
    for rec in records:
        for key in ('h', 'grammar', 'senses'):
            if key not in rec:
                fail('stitched record missing schema-required %r' % key)
    if [s['tag'] for r in records for s in r['senses']] != ['1', '2', '3']:
        fail('stitch must preserve document order of senses')
    # A single owner stays ONE record -- no gratuitous fragmentation.
    if len(hw.stitch_records(senses, [('h', 'g')] * 3)) != 1:
        fail('one owner must yield exactly one record')

    import autosplit_requeue as ar
    split_records = ar._stitch_owned_senses(senses, owners)
    if [(r['h'], r['grammar']) for r in split_records] != [
            ('1. bhid', 'm.'), ('2. bhid', 'f.')]:
        fail('autosplit stitch lost record owners: %r' % split_records)
    topup_manifest = [{
        'orig': 'bhid', 'iast': 'bhid', 'notes': '',
        'owners_by_tag': {'1': ['1. bhid', 'm.'], '2': ['2. bhid', 'f.']},
        'default_owner': ['1. bhid', 'm.'],
        'plan': [
            {'s': 0, 'p': 0, 'fsha': 'a', 'fk': 'old', 'missing': False},
            {'s': 1, 'p': 0, 'fsha': 'b', 'fk': 'new', 'missing': True}],
        'resolved': {'a': [{'tag': '1', 'german': 'g1', 'russian': 'r1'}]}}]
    new_fragment = {'records': [{'h': '2. bhid', 'grammar': 'f.', 'senses': [
        {'tag': '2', 'german': 'g2', 'russian': 'r2'}]}]}
    rows, missing = ar.stitch_topup(topup_manifest, {'new': new_fragment}, 'russian')
    recs = rows[0]['card']['records']
    if missing or [(r['h'], r['grammar']) for r in recs] != [
            ('1. bhid', 'm.'), ('2. bhid', 'f.')]:
        fail('top-up stitch lost a record boundary/owner: %r %r' % (rows, missing))



def test_unmapped_token_is_counted():
    """C-42: an out-of-range {Tn} is counted, not silently passed through.

    The defect: `restore_text` returned `match.group(0)` for an index the map does not
    address, with no counter, no log and no reject -- so `ban_d~~h0_11_ni` and
    `ban_d~~h0_21_upasam_0` reached the canonical store carrying a raw {T196}/{T235} on cards
    that reported success. Cause is a masking-scope vs restore-scope index mismatch (article
    masked whole, restored per sub-card), not model hallucination.
    """
    import headless_worker as hw
    unmapped = []
    out = hw.restore_text('a {T1} b {T99} c', ['<ls>x</ls>'], unmapped)
    if '<ls>x</ls>' not in out:
        fail('an in-range token must still restore')
    if unmapped != ['{T99}']:
        fail('an out-of-range token must be counted, got %r' % unmapped)
    if '{T99}' not in out:
        fail('behaviour change: the out-of-range token must still pass through verbatim')
    clean = []
    hw.restore_text('a {T1} b', ['x'], clean)
    if clean:
        fail('a fully-mapped text must report no unmapped tokens, got %r' % clean)



def test_validator_has_a_live_caller():
    """C-04 dead-validator canary: the record contract must run on LIVE output.

    `validate_final_card_schema` is the ONLY component encoding record.required =
    {h, grammar, senses}, and its only caller was a CI step feeding it a hand-made PASSING
    fixture. A green check certified a contract no real card was measured against -- which is
    precisely why C-01's 670 placeholder rows and C-02's 468 null-h rows accumulated with no
    signal. This asserts the validator is reachable from the save chain, and that it still
    refuses a record missing `h`.
    """
    from window_common import REPO as repo_root
    save = os.path.join(repo_root, 'save_and_audit.py')
    text = open(save, encoding='utf-8').read()
    if 'validate_final_card_schema' not in text:
        fail('save_and_audit.py has no reference to validate_final_card_schema -- the '
             'validator is dead again (C-04)')
    if 'validate_card(' not in text:
        fail('save_and_audit.py imports the validator but never calls validate_card()')

    audit_path = os.path.join(SRC, 'pilot', 'audit_window.py')
    audit_text = open(audit_path, encoding='utf-8').read()
    if 'run_final_schema_gate' not in audit_text or 'validate_card(' not in audit_text:
        fail('audit_window.py does not validate real workflow cards')

    promote_path = os.path.join(SRC, 'promote_final_cards.py')
    promote_text = open(promote_path, encoding='utf-8').read()
    if 'validate_promotion_entry' not in promote_text or 'validate_card(' not in promote_text:
        fail('promote_final_cards.py lacks independent final-schema validation')

    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import validate_final_card_schema as v
    if v.RECORD_REQUIRED != {'h', 'grammar', 'senses'}:
        fail('RECORD_REQUIRED was relaxed: %r' % (v.RECORD_REQUIRED,))
    # The contract must actually reject the shape C-02 was writing.
    bad = {'key1': 'k', 'iast': 'k', 'notes': '', 'records': [{'senses': [
        {'tag': '1', 'german': 'g', 'russian': 'r', 'equivalence_type': 'equivalent',
         'source_type': 'attested', 'stratum': '', 'differentia': ''}]}]}
    try:
        v.validate_card(bad)
    except ValueError:
        pass
    else:
        fail('validate_card accepted a record with no h/grammar -- the C-02 shape')

    import audit_window
    good = {'key1': 'k', 'iast': 'k', 'notes': '', 'records': [{
        'h': 'k', 'grammar': '', 'senses': [{
            'tag': '1', 'german': 'g', 'russian': 'r',
            'equivalence_type': 'equivalent', 'source_type': 'attested',
            'stratum': '', 'differentia': ''}]}]}
    ok_gate = audit_window.run_final_schema_gate([{'key': 'k', 'card': good}])
    if ok_gate.get('returncode') != 0 or ok_gate.get('requeue'):
        fail('audit final-schema gate rejected a valid card: %r' % ok_gate)
    bad_gate = audit_window.run_final_schema_gate([{'key': 'k', 'card': bad}])
    if bad_gate.get('returncode') != 1 or bad_gate.get('requeue') != ['k']:
        fail('audit final-schema gate did not requeue an invalid live card: %r' % bad_gate)



def test_card_tokens_twins_agree():
    """R2/C-17 (closes N-4): the JS `cardTokens` fidelity collector is DRIVEN by the Python-owned
    card_fields.js_token_fidelity_spec(), so the two twins cannot drift. Proven three ways: the
    generated JS interpolates the exact spec; cardTokens iterates it (not a hard-coded field list);
    and changing the Python-owned spec changes the generated JS collector."""
    import re as _re
    import gen_opt_harness2 as gh
    import card_fields as cf

    def _gen():
        d = tempfile.mkdtemp()
        rp = os.path.join(d, 'agni~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'agni~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#agni#}¦ m. {%a%}\n— 1〉 Feuer.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        try:
            js, _ = gh.build('zz', ['agni~~h0_zz_pw'], None, 12000, nominal=True,
                             grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = saved
        return js

    js = _gen()
    m = _re.search(r'const TOKEN_FIDELITY_SPEC = (\{.*?\})\n', js)
    if not m:
        fail('generated JS does not interpolate TOKEN_FIDELITY_SPEC')
    if m.group(1) != cf.js_token_fidelity_spec():
        fail('JS TOKEN_FIDELITY_SPEC != card_fields.js_token_fidelity_spec(): %s' % m.group(1))
    if 'TOKEN_FIDELITY_SPEC.record' not in js or 'TOKEN_FIDELITY_SPEC.sense' not in js:
        fail('cardTokens is not driven by the interpolated TOKEN_FIDELITY_SPEC')
    saved = cf.TOKEN_FIDELITY_FIELDS
    cf.TOKEN_FIDELITY_FIELDS = (('record', 'grammar'), ('sense', 'german'), ('sense', 'tag'))
    try:
        m2 = _re.search(r'const TOKEN_FIDELITY_SPEC = (\{.*?\})\n', _gen())
        if not m2 or '"tag"' not in m2.group(1) or m2.group(1) == m.group(1):
            fail('JS collector did not follow the Python-owned spec change: %s' % (m2 and m2.group(1)))
    finally:
        cf.TOKEN_FIDELITY_FIELDS = saved
    print('  R2/N-4: JS cardTokens is driven by card_fields.js_token_fidelity_spec() (twins cannot drift)')



def test_frag_tm_v2_supersedes_v1():
    """R6: fragment-TM v2 schema. A v1 (ownerless) row is readable for audit but NEVER live-reusable;
    a valid v2 row with the same fsha supersedes it; and an existing v1 does NOT block a v2 harvest.
    Owners count/shape are validated."""
    import json as _json
    import translation_memory as tm
    d = tempfile.mkdtemp()
    path = os.path.join(d, 'translation_memory.frag.ru.jsonl')
    sense = {'tag': '1', 'german': 'Feuer', 'russian': 'огонь'}
    v1 = {'schema': tm.FRAG_SCHEMA, 'lang': 'ru', 'fsha': 'X', 'n_senses': 1, 'senses': [sense],
          'trust_level': tm.TRUST_MACHINE, 'gate_status': 'machine_gated',
          'reuse_policy': 'auto_exact', 'source_kind': 'frag_prov'}
    with open(path, 'w', encoding='utf-8') as f:
        f.write(_json.dumps(v1) + '\n')
    if tm.load_frag_tm('ru', path) != {}:
        fail('a v1 (ownerless) row must not be live-served')
    if 'X' not in tm.load_frag_tm('ru', path, live_only=False):
        fail('a v1 row must stay readable for historical audit (live_only=False)')
    wf = os.path.join(d, 'wf_output.zz.json')
    card = {'key1': 'agni', 'frag_prov': [{'fsha': 'X', 'senses': [sense],
                                           'owners': [['2. agni', 'm.']]}]}
    with open(wf, 'w', encoding='utf-8') as f:
        _json.dump({'meta': {'lang': 'ru', 'root': 'zz'},
                    'results': [{'key': 'agni', 'card': card}]}, f)
    saved_repo = tm.REPO
    tm.REPO = d
    try:
        _p, added, _total = tm.build_frags(os.path.basename(wf), 'ru', out=path)
    finally:
        tm.REPO = saved_repo
    if added != 1:
        fail('an existing v1 must NOT block a v2 harvest (added=%d)' % added)
    served = tm.load_frag_tm('ru', path)
    if 'X' not in served or served['X'].get('owners') != [['2. agni', 'm.']]:
        fail('the v2 row must be live-served with its owners: %r' % served.get('X'))
    if served['X'].get('schema') != tm.FRAG_SCHEMA_V2:
        fail('served row must be v2')
    if not tm._valid_owners([sense], [['h', 'g']]) or tm._valid_owners([sense], [['h']]) \
            or tm._valid_owners([sense, sense], [['h', 'g']]):
        fail('_valid_owners count/shape validation is wrong')
    # null-owner hardening: BOTH members must be strings ('' valid, None fails). A null-owner row is
    # NOT live-served (so no warm stitch -- JS or headless -- can restore a null owner) but stays
    # audit-readable, exactly like a v1 row.
    if not tm._valid_owners([sense], [['', '']]):
        fail('empty-string owner members must be valid')
    if tm._valid_owners([sense], [[None, 'g']]) or tm._valid_owners([sense], [['h', None]]):
        fail('a null owner member ([None,g] / [h,None]) must be rejected')
    for pair in ([None, 'g'], ['h', None]):
        npath = os.path.join(d, 'nullowner.frag.ru.jsonl')
        with open(npath, 'w', encoding='utf-8') as f:
            f.write(_json.dumps({'schema': tm.FRAG_SCHEMA_V2, 'lang': 'ru', 'fsha': 'N',
                                 'senses': [sense], 'owners': [pair],
                                 'trust_level': tm.TRUST_MACHINE, 'gate_status': 'machine_gated',
                                 'reuse_policy': 'auto_exact'}) + '\n')
        if tm.load_frag_tm('ru', npath) != {}:
            fail('a null-owner row %r must NOT be live-served' % pair)
        if 'N' not in tm.load_frag_tm('ru', npath, live_only=False):
            fail('a null-owner row %r must stay audit-readable' % pair)
    print('  R6: frag-TM v2 supersedes v1; null-owner ([None,g]/[h,None]) rejected from live serve, '
          'audit-readable; owners validated')



def test_degenerate_source_identity():
    """R7: a degenerate card's (h, grammar) is the PROVEN source-record identity, not a schema
    default; an unprovable identity is REJECTED rather than emitted with a fabricated h."""
    import gen_opt_harness2 as gh
    import validate_final_card_schema as vs
    card = gh.degenerate_passthrough_card('ab~~h0_zz_pw', '=== LAYER: PW ===\n\nvgl. {#agni#}',
                                          '[]', 'russian')
    if not card or card['records'][0].get('h') != '' or card['records'][0].get('grammar') != '':
        fail('a clean single-head xref must prove h="" (no source homonym head): %r' % card)
    vs.validate_card(card)
    if gh.degenerate_passthrough_card('ab', '=== LAYER: PW ===\n\nvgl. {#agni#}',
                                      '[]', 'russian') is None:
        fail('a bare-root key with a clean stub is a provable identity -- must NOT be rejected')
    if gh._degenerate_record_identity('ab~~h1_zz_pw', 'vgl. <div n="2"> agni') is not None:
        fail('a residual homonym head must be rejected (ambiguous owning record)')
    if gh._degenerate_record_identity('ab~~h0_zz_pw', 'vgl.') != ('', ''):
        fail('a clean stub must prove ("","")')
    print('  R7: degenerate (h,grammar) is proven source identity; unprovable identity is rejected')



def test_en_card_tm_serves_english_field_c3():
    """C3: `build --lang en` must write each sense's translation under the CARD field name
    'english' (not the store COLUMN 'en'), or the serve-side `tm_card_sane` / final-card schema
    reject every EN card-TM hit ('sense missing english') — 100% of EN whole-card TM silently
    dead, and the EN lane re-translates cards it already has. The RU path stays correct."""
    import translation_memory as tm
    import gen_opt_harness2 as gh
    d = tempfile.mkdtemp()
    try:
        store = os.path.join(d, 'store.en.jsonl')
        row = {'subcard': 'agni~~h0_00_pwg00', 'iast': 'agni', 'h': '1', 'grammar': '',
               'sense_tag': '1', 'de': 'Feuer', 'en': 'fire',
               'provenance': {'input_raw_sha256': 'DEADBEEF'}}
        with open(store, 'w', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
        built_path, count, _skipped = tm.build(store, 'en', os.path.join(d, 'tm.en.json'))
        if count != 1:
            fail('C3: EN card-TM built %d entries from one valid EN store row (expected 1)' % count)
        entry = next(iter(json.load(open(built_path, encoding='utf-8'))['entries'].values()))
        sense = entry['card']['records'][0]['senses'][0]
        if sense.get('english') != 'fire':
            fail("C3: EN card-TM sense must carry 'english'='fire', got keys %r" % sorted(sense))
        if 'en' in sense:
            fail("C3: EN card-TM sense must NOT carry the store-column key 'en': %r" % sense)
        # the serve-side guard the harness runs on every hit must ACCEPT it (was: refuse it)
        ok, why = gh.tm_card_sane(entry['card'], 'en', 'english', 'Feuer')
        if not ok:
            fail('C3: a valid EN card-TM hit must pass tm_card_sane, got refusal: %s' % why)
        # RU parity control: the RU path must still key 'russian'
        rstore = os.path.join(d, 'store.ru.jsonl')
        rrow = dict(row, ru='огонь'); rrow.pop('en')
        with open(rstore, 'w', encoding='utf-8') as f:
            f.write(json.dumps(rrow, ensure_ascii=False) + '\n')
        rpath, rcount, _ = tm.build(rstore, 'ru', os.path.join(d, 'tm.ru.json'))
        rsense = next(iter(json.load(open(rpath, encoding='utf-8'))['entries'].values()))['card']['records'][0]['senses'][0]
        if rsense.get('russian') != 'огонь' or 'ru' in rsense:
            fail("C3: RU card-TM sense must carry 'russian', not 'ru': %r" % rsense)
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_autosplit_stitch_topup_rejects_target_field_drop():
    """H1152 parity (C1): stitch_topup must REJECT a COMPLETE card whose reassembled `german` echo is
    faithful but whose target field dropped an <ls>/{#..#} span (source counts stamped by
    topup_fragments). A faithful card still completes."""
    import autosplit_requeue as ar

    def card(orig, ru_text):
        return {'orig': orig, 'iast': 'zz', 'notes': '', 'owners_by_tag': {},
                'default_owner': ('1', 'm.'), 'src_ls': 1, 'src_sk': 0,
                'resolved': {'F0': [{'tag': '1', 'german': '<ls>RV.</ls> Feuer',
                                     'russian': ru_text}]},
                'plan': [{'s': 0, 'p': 0, 'fsha': 'F0', 'fk': ar.fk_of(orig, 0, 0),
                          'missing': False}]}
    res, _ = ar.stitch_topup([card('zz~~drop', 'огонь')], {}, 'russian')          # target drops <ls>
    if res[0]['card'] is not None or 'fidelity drift' not in (res[0].get('error') or ''):
        fail('stitch_topup must reject a complete card whose target dropped a span: %r' % res[0])
    ok, _ = ar.stitch_topup([card('zz~~keep', '<ls>RV.</ls> огонь')], {}, 'russian')  # faithful
    if not ok[0]['card'] or ok[0].get('partial'):
        fail('stitch_topup must keep a complete faithful card: %r' % ok[0])



def test_autosplit_merge_rejects_target_field_drop():
    """H1152 parity (C1/C5): cmd_merge (the primary autosplit lane) must REJECT a COMPLETE card whose
    target field dropped an <ls>/{#..#} span — it was <ls>-only, german-only, and non-blocking (kept
    the card, only flagged `fidelity_drift`). Behavioral test with a temp manifest/task/source."""
    import autosplit_requeue as ar
    orig = 'zz~~h0_00_pwgm'
    fk = ar.fk_of(orig, 0, 0)
    d = tempfile.mkdtemp()
    saved = (ar.manifest_path, ar.input_paths, ar.REPO)
    try:
        rawp = os.path.join(d, 'src.raw.txt')
        with open(rawp, 'w', encoding='utf-8') as f:
            f.write('<hom>1.</hom> {%Feuer%} <ls>RV. 1,1</ls>.')          # exactly one <ls>, no {#
        mpath = os.path.join(d, 'manifest.json')
        with open(mpath, 'w', encoding='utf-8') as f:
            json.dump({'frags': {fk: {'orig': orig, 's': 0, 'p': 0}}}, f)
        taskp = os.path.join(d, 'task.json')
        drop_card = {'key1': orig, 'iast': 'zz', 'records': [{'h': '1', 'grammar': 'm.', 'senses': [
            {'tag': '1', 'german': '<ls>RV. 1,1</ls> Feuer', 'russian': 'огонь'}]}]}  # ru drops <ls>
        with open(taskp, 'w', encoding='utf-8') as f:
            json.dump({'results': [{'key': fk, 'card': drop_card}]}, f)
        ar.manifest_path = lambda lang, root: mpath
        ar.input_paths = lambda k, input_dir=None: (rawp, os.path.join(d, k + '.portrait.json'))
        ar.REPO = d
        ar.cmd_merge('zzmerge', 'ru', taskp)
        out = json.load(open(os.path.join(d, 'wf_output.sc.zzmerge.autosplit.json'), encoding='utf-8'))
        rows = {r['key']: r for r in out['results']}
        if orig not in rows or rows[orig]['card'] is not None:
            fail('cmd_merge must null a complete card whose target dropped a span: %r' % rows.get(orig))
        if 'fidelity drift' not in (rows[orig].get('error') or ''):
            fail('cmd_merge reject must carry the fidelity-drift error: %r' % rows[orig])
    finally:
        ar.manifest_path, ar.input_paths, ar.REPO = saved
        shutil.rmtree(d, ignore_errors=True)



def test_frag_prov_glob_honors_coordinator_dir_c7():
    """C7: the coordinator's frag_prov detection AND its build-frags call must both derive their
    glob from paths()['artifacts'] (honoring PWG_COORDINATOR_DIR), or a custom coord dir (per-run /
    worktree) detects frag_prov but builds the fragment TM from the empty DEFAULT tree — silently
    dropping the just-promoted window's fragments."""
    import coordinator as c
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as d:
        os.environ['PWG_COORDINATOR_DIR'] = d
        try:
            g = os.path.abspath(c._frag_prov_glob())
            if os.path.abspath(d) not in g:
                fail('C7: build-frags/detection glob must live under PWG_COORDINATOR_DIR, got %r' % g)
            if 'wf_output' not in os.path.basename(g):
                fail('C7: the frag_prov glob must target wf_output*.json, got %r' % g)
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old
    # regression guard: the hardcoded default glob must never come back
    src = open(os.path.join(HERE, 'coordinator.py'), encoding='utf-8').read()
    if "'src/pilot/output/coordinator/artifacts/*/wf_output*.json'" in src:
        fail('C7: build-frags --glob is hardcoded to the default tree again; use _frag_prov_glob()')

