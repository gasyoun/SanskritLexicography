#!/usr/bin/env python
"""Selftests for promote_final_cards (PR-C: extracted from the production module).

The test body is byte-identical to the former inline `selftest()`; every
production name it exercises is imported explicitly below so drift between
the suite and the module fails loudly at import time.

  python src/promote_final_cards_selftest.py
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from promote_final_cards import (  # noqa: E402,F401
    ClaimBusy,
    PromoteClaim,
    PromotionContractError,
    SELFTEST_MODEL_VERSION,
    _atomic_write_rows,
    _backup_path,
    _fsynced_backup,
    batch_promote,
    collect_cards,
    content_mass,
    explicit_glob_supplied,
    human_touched,
    json,
    load_defect_keys,
    merge_store_rows,
    os,
    promote_ready_partial_clean,
    promotion_journal,
    refuse_content_mass_shrink,
    refuse_defect_keys,
    rows_for,
    shutil,
    tempfile,
    validate_promotion_entry,
    validate_store_target,
)


def selftest():
    import tempfile
    meta = {'root': 'pA', 'safe_root': 'p_a', 'generator': 'gen_opt_harness2.batched-masked',
            'schema_version': 'v1', 'rootmap_sha256': 'abc', 'generated_at': '2026-06-29T00:00:00Z',
            'selected_keys': ['p_a~~h5_00_pwg00'],
            'execution_manifest_schema': 'pwg.headless_execution_manifest.v2',
            'execution': {'profile_slot': 'c4', 'config_dir_fingerprint': 'f' * 64,
                          'execution_route': 'claude-cli-headless',
                          'executor_lane': 'serial-whole-card',
                          'validation_method': 'audit_window+final_schema',
                          'model_identifier': 'claude-sonnet-5'},
            'provenance_classes': {'p_a~~h5_00_pwg00': 'real'},
            'input_hashes': {'p_a~~h5_00_pwg00': {
                'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}}
    entry = {'card': {'key1': 'p_a~~h5_00_pwg00', 'iast': 'pā', 'notes': '', 'records': [
        {'h': 'pā', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'пить', 'german': 'trinken', 'equivalence_type': 'equivalent',
             'source_type': 'attested', 'stratum': 'Vedic', 'differentia': ''},
            {'tag': '2', 'russian': '', 'german': 'x'},          # no russian -> skipped
        ]}]}, 'meta': meta, 'wf_file': 'wf_output.sc.pA.json'}
    rows = list(rows_for('p_a~~h5_00_pwg00', entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))
    assert len(rows) == 1, 'a sense without russian must be skipped'
    r = rows[0]
    assert r['key1'] == 'pA', 'key1 must be the HEADWORD meta.root, not the sub-card key'
    assert r['subcard'] == 'p_a~~h5_00_pwg00' and r['ru'] == 'пить' and r['de'] == 'trinken'
    assert r['layer'] == 'pwg', 'base sub-card must carry an explicit layer=pwg'
    assert r.get('government') == [], 'plain DE with no Rektion must stamp government=[]'
    assert r.get('form_labels') == [], 'plain DE with no form labels must stamp form_labels=[]'
    assert r.get('form_notes') == [], 'plain DE with no nom/voc must stamp form_notes=[]'
    assert r.get('citation_edges') == [], 'plain DE with no <ls> must stamp citation_edges=[]'
    assert r.get('edition_rel', {}).get('subtype') == 'base', r.get('edition_rel')
    # H1624 G2: PW capitalized (Instr.) must be stamped at promote time from DE only
    gov_entry = {'card': {'key1': 'vas~~h0_zz_pw00', 'iast': 'vas', 'notes': '', 'records': [
        {'h': 'vas', 'grammar': '', 'senses': [
            {'tag': 'samava', 'russian': 'обёрнутый',
             'german': '<div n="m">— <ab>Caus.</ab> {#prativAsita#} {%gehüllt in%} '
                       '(<ab>Instr.</ab>).',
             'equivalence_type': 'explanatory', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='vas', selected_keys=['vas~~h0_zz_pw00'],
                           provenance_classes={'vas~~h0_zz_pw00': 'real'},
                           input_hashes={'vas~~h0_zz_pw00': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    grow = list(rows_for('vas~~h0_zz_pw00', gov_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    assert grow['government'] and grow['government'][0]['cases'] == ['instr'], grow
    assert grow['government'][0]['span'] == '(<ab>Instr.</ab>)', grow
    # H1624 form-layer: gender + number + voc on one DE sense
    form_entry = {'card': {'key1': 'deva~~h0_00_pwg00', 'iast': 'deva', 'notes': '', 'records': [
        {'h': 'deva', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'бог',
             'german': '<lex>m.</lex> {%Gott%} (<ab>pl.</ab>) <ls>ṚV. 1,1,1</ls>. '
                       '(<ab>voc.</ab>) auch so.',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='deva', selected_keys=['deva~~h0_00_pwg00'],
                           provenance_classes={'deva~~h0_00_pwg00': 'real'},
                           input_hashes={'deva~~h0_00_pwg00': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    frow = list(rows_for('deva~~h0_00_pwg00', form_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    axes = {(h['axis'], h['value']) for h in frow['form_labels']}
    assert ('gender', 'm') in axes and ('number', 'pl') in axes and ('case_form', 'voc') in axes, frow
    # Dedicated form_notes field for nom/voc
    assert frow['form_notes'] and frow['form_notes'][0]['case'] == 'voc', frow
    assert frow['form_notes'][0]['span'] == '(<ab>voc.</ab>)', frow
    # Rektion loc must NOT land in form_labels or form_notes
    assert not any(h.get('value') == 'loc' for h in frow['form_labels']), frow
    assert not any(n.get('case') in ('loc', 'instr', 'acc') for n in frow['form_notes']), frow
    # H1624 G3: citation_edges from DE <ls>
    cite_entry = {'card': {'key1': 'agni~~h0_00_pwg00', 'iast': 'agni', 'notes': '', 'records': [
        {'h': 'agni', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'огонь',
             'german': '{%Feuer%} <ls>ṚV. 1,1,1</ls>; <ls n="MBH.">3,50</ls>.',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='agni', selected_keys=['agni~~h0_00_pwg00'],
                           provenance_classes={'agni~~h0_00_pwg00': 'real'},
                           input_hashes={'agni~~h0_00_pwg00': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    crow = list(rows_for('agni~~h0_00_pwg00', cite_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    assert len(crow['citation_edges']) == 2, crow
    assert crow['citation_edges'][0]['siglum'] == 'ṚV', crow
    assert crow['citation_edges'][0]['resolver_status'] == 'map', crow
    assert crow['citation_edges'][0]['page'] == '1,1,1', crow
    # raw DE still holds the markup
    assert '<ls>ṚV. 1,1,1</ls>' in crow['de'], crow
    # H1624 G4: edition_rel on overlay layers
    sch_entry = {'card': {'key1': 'ap~~h0_zz_sch', 'iast': 'ap', 'notes': '', 'records': [
        {'h': 'ap', 'grammar': '', 'senses': [
            {'tag': 'anu_desid', 'russian': 'соглашаться',
             'german': '{%einstimmen%}',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='Ap', selected_keys=['ap~~h0_zz_sch'],
                           provenance_classes={'ap~~h0_zz_sch': 'real'},
                           input_hashes={'ap~~h0_zz_sch': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    srow = list(rows_for('ap~~h0_zz_sch', sch_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    assert srow['layer'] == 'sch', srow
    assert srow['edition_rel']['subtype'] == 'derived_sense', srow['edition_rel']
    assert srow['edition_rel']['source_layers'] == ['sch'], srow['edition_rel']
    pw_entry = {'card': {'key1': 'g~~h0_zz_pw01', 'iast': 'g', 'notes': '', 'records': [
        {'h': 'g', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'идти', 'german': '{%gehen%}',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='gA', selected_keys=['g~~h0_zz_pw01'],
                           provenance_classes={'g~~h0_zz_pw01': 'real'},
                           input_hashes={'g~~h0_zz_pw01': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    prow = list(rows_for('g~~h0_zz_pw01', pw_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    # H3752: promotion sees one card and has no peer rows, so no PWG sense can be
    # identified here and the provisional stamp is the unplaced twin — agreeing
    # with the `placement: False` this row already carried. `direction` is the
    # layer's property and survives, which is what keeps the stamp useful.
    assert prow['edition_rel']['subtype'] == 'restate_unplaced', prow['edition_rel']
    assert prow['edition_rel']['placement'] is False, prow['edition_rel']
    assert prow['edition_rel']['direction'] == 'abridging', prow['edition_rel']
    assert list(rows_for('x~~h0_zz_pw01', dict(entry, meta=meta), 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]['layer'] == 'pw', 'addenda sub-card -> layer=pw'
    assert r['review_status'] == 'ai_translated', 'must not auto-approve (G5 gate)'
    p = r['provenance']
    assert p['model'] == 'sonnet' and p['rootmap_sha256'] == 'abc'
    assert p['model_version'] == SELFTEST_MODEL_VERSION, 'model VERSION recorded, not just the tier alias'
    assert p['input_raw_sha256'] == '1' * 64 and p['generated_at'], 'provenance must be complete'
    validate_promotion_entry('p_a~~h5_00_pwg00', entry)
    historical = {'card': entry['card'], 'wf_file': entry['wf_file'],
                  'meta': dict(meta, execution_manifest_schema=
                               'pwg.headless_execution_manifest.v1')}
    try:
        validate_promotion_entry('p_a~~h5_00_pwg00', historical)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('historical v1 output passed new production promotion')
    synthetic = {'card': entry['card'], 'wf_file': entry['wf_file'],
                 'meta': dict(meta, provenance_classes={
                     'p_a~~h5_00_pwg00': 'synthetic_control'})}
    try:
        validate_promotion_entry('p_a~~h5_00_pwg00', synthetic)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('synthetic control passed promotion validation')
    foreign = {'card': entry['card'], 'wf_file': entry['wf_file'],
               'meta': dict(meta, selected_keys=['some_other_key'])}
    try:
        validate_promotion_entry('p_a~~h5_00_pwg00', foreign)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('foreign key passed promotion validation')
    # NOMINAL mode: meta.root is a window LABEL; the row must key to the true SLP1 headword
    # recovered from nominal_keymap[stem], NOT to the label (regression guard, H179 drain).
    nmeta = {'root': 'pril10_w1', 'nominal': True, 'nominal_keymap': {'k_ala': 'kAla'},
             'input_hashes': {'k_ala': {'raw_sha256': 'r', 'portrait_sha256': 'p'}}}
    ncard = {'key1': 'kAla', 'iast': 'kāla', 'notes': '',
             'records': [{'h': 'kāla', 'grammar': '',
                          'senses': [{'tag': '1', 'russian': 'время', 'german': 'Zeit'}]}]}
    nrow = list(rows_for('k_ala', {'card': ncard, 'meta': nmeta, 'wf_file': 'wf_output.json'},
                         'ai_translated', SELFTEST_MODEL_VERSION))[0]
    assert nrow['key1'] == 'kAla', 'nominal card must key to true SLP1 headword, not the window label'
    assert nrow['subcard'] == 'k_ala' and nrow['layer'] == 'pwg'
    assert 'partial_card' not in p, 'complete card carries no partial marker'
    # a partial (selfheal) card must be marked on every row it yields
    pentry = dict(entry)
    pentry['card'] = dict(entry['card'], partial=True, missing_fragments=['g2:f1'],
                          missing_groups=1, total_groups=3)
    pr = list(rows_for('p_a~~h5_00_pwg00', pentry, 'ai_translated',
                       SELFTEST_MODEL_VERSION))[0]['provenance']
    assert pr['partial_card'] is True and pr['missing_fragments'] == ['g2:f1'], \
        'partial cards must be distinguishable in the store'
    # H1226: the pre-restore {Tn} pairing rides on provenance when the card carries it, is absent
    # (never fabricated) for pre-H1226 cards, and a malformed pairing is dropped rather than stored.
    assert 'tnmask' not in p, 'a card without tnmask must not fabricate one in provenance'
    tnentry = dict(entry, card=dict(entry['card'], tnmask={'got': 'T1 T2', 'want': 'T1 T2 T3'}))
    tp = list(rows_for('p_a~~h5_00_pwg00', tnentry, 'ai_translated',
                       SELFTEST_MODEL_VERSION))[0]['provenance']
    assert tp['tnmask'] == {'got': 'T1 T2', 'want': 'T1 T2 T3'}, \
        'the pre-restore {Tn} pairing must ride on the promoted row provenance'
    badentry = dict(entry, card=dict(entry['card'], tnmask={'got': 'T1'}))   # missing `want`
    bp = list(rows_for('p_a~~h5_00_pwg00', badentry, 'ai_translated',
                       SELFTEST_MODEL_VERSION))[0]['provenance']
    assert 'tnmask' not in bp, 'a malformed tnmask pairing must not be promoted'
    # H858 Part B: a card repaired by the german-anchor lane must SAY SO on every row it yields --
    # otherwise a machine-re-injected citation is indistinguishable in the store from one the model
    # echoed correctly, and the repair's real-world precision is unauditable after the fact. Same
    # discipline as tnmask above: never fabricated, and a malformed stamp is dropped.
    assert 'german_anchor' not in p, 'an unrepaired card must not fabricate a german_anchor stamp'
    garow = list(rows_for('p_a~~h5_00_pwg00',
                          dict(entry, card=dict(entry['card'],
                                                german_anchor={'reinjected': ['T4'], 'head': []})),
                          'ai_translated', SELFTEST_MODEL_VERSION))[0]['provenance']
    assert garow['german_anchor'] == {'reinjected': ['T4'], 'head': []}, \
        'a german-anchor repair must ride on the promoted row provenance'
    gabad = list(rows_for('p_a~~h5_00_pwg00',
                          dict(entry, card=dict(entry['card'], german_anchor={'head': []})),
                          'ai_translated', SELFTEST_MODEL_VERSION))[0]['provenance']
    assert 'german_anchor' not in gabad, 'a malformed german_anchor stamp must not be promoted'
    # collect_cards: a non-null card wins over a null for the same sub-card key.
    d = tempfile.mkdtemp()
    nullf = os.path.join(d, 'wf_output.sc.x.json')
    fullf = os.path.join(d, 'wf_output.x.json')
    with open(nullf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': None}]}, f)
    with open(fullf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': entry['card']}]}, f)
    best, _conf, nulls = collect_cards([nullf, fullf])
    assert 'p_a~~h5_00_pwg00' in best, 'non-null must win over null for the same key'
    assert nulls == [], 'a key non-null in any file is not a null'
    # Byte-equivalent recovered artifacts collapse; divergent cards/provenance fail closed.
    dupf = os.path.join(d, 'wf_output.duplicate.x.json')
    with open(dupf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [
            {'key': 'p_a~~h5_00_pwg00', 'card': entry['card']}]}, f)
    best, duplicate_conflicts, _nulls = collect_cards([fullf, dupf])
    assert len(best) == 1 and duplicate_conflicts == [], \
        'byte-equivalent workflow cards must deduplicate without a conflict'
    divergent = os.path.join(d, 'wf_output.divergent.x.json')
    changed_card = json.loads(json.dumps(entry['card']))
    changed_card['records'][0]['senses'][0]['russian'] = 'выпить'
    with open(divergent, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [
            {'key': 'p_a~~h5_00_pwg00', 'card': changed_card}]}, f)
    _best, divergent_conflicts, _nulls = collect_cards([fullf, divergent])
    assert divergent_conflicts == ['p_a~~h5_00_pwg00'], \
        'different non-null translations for one key must conflict'
    # EN wf files must NOT shadow RU cards: 'wf_output.en.*' sorts before 'wf_output.sc.*',
    # and its cards carry 'english' not 'russian' -> zero rows -> silent RU loss on rebuild.
    enf = os.path.join(d, 'wf_output.en.x.json')
    en_meta = dict(meta, lang='en')
    en_card = {'key1': 'p_a~~h5_00_pwg00', 'records': [
        {'h': 'pā', 'senses': [{'tag': '1', 'english': 'to drink', 'german': 'trinken'}]}]}
    with open(enf, 'w', encoding='utf-8') as f:
        json.dump({'meta': en_meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': en_card}]}, f)
    best, _conf, _nulls = collect_cards(sorted([enf, fullf, nullf]))
    got = best['p_a~~h5_00_pwg00']
    assert got['meta'].get('lang') != 'en', 'EN wf file must be excluded from the RU bridge'
    assert list(rows_for('p_a~~h5_00_pwg00', got, 'ai_translated',
                         SELFTEST_MODEL_VERSION)), 'RU rows survive the EN sibling'
    assert explicit_glob_supplied(['--merge', '--glob', 'src/pilot/output/wf_output.w01.json'])
    assert explicit_glob_supplied(['--glob=src/pilot/output/wf_output.w01.json', '--merge'])
    assert not explicit_glob_supplied(['--merge'])
    # Missing stores fail closed; explicit first-run init is accepted only while absent.
    missing = os.path.join(d, 'missing-store.jsonl')
    try:
        validate_store_target(missing)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('missing store passed without --init-store')
    validate_store_target(missing, init_store=True)
    with open(missing, 'w', encoding='utf-8') as f:
        f.write('')
    try:
        validate_store_target(missing, init_store=True)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('--init-store overwrote an existing store')
    # Exact-subcard merge is idempotent; a second promotion replaces rather than duplicates.
    old = [{'key1': 'x', 'subcard': 'x~~a'}, {'key1': 'y', 'subcard': 'y~~a'}]
    new = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'new'}]
    once, dg1, pr1 = merge_store_rows(old, new)
    twice, dg2, pr2 = merge_store_rows(once, new)
    assert once == twice and len(once) == 2 and dg1 == [] and dg2 == []
    assert pr1 == [] and pr2 == [], 'unreviewed rows must not be protected'
    # B08 (H1339): the store merge is better-attempt-wins, the H304 rule ported to the
    # store level. A partial incoming attempt must NOT downgrade complete existing rows;
    # a complete incoming attempt replaces a partial; fewer missing fragments win among
    # partials; equal quality -> incoming wins (deliberate retranslation).
    complete_old = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'old-good', 'provenance': {}}]
    partial_new = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'new-partial',
                    'provenance': {'partial_card': True, 'missing_fragments': ['g1:f0']}}]
    merged, downgraded, _pr = merge_store_rows(complete_old, partial_new)
    assert merged == complete_old and downgraded == ['x~~a'], \
        'a partial attempt silently downgraded a complete store row'
    merged, downgraded, _pr = merge_store_rows(partial_new, complete_old)
    assert merged == complete_old and downgraded == [], \
        'a complete attempt must replace a partial store row'
    worse = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'p3',
              'provenance': {'partial_card': True,
                             'missing_fragments': ['g1:f0', 'g1:f1', 'g2:f0']}}]
    better = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'p1',
               'provenance': {'partial_card': True, 'missing_fragments': ['g1:f0']}}]
    merged, downgraded, _pr = merge_store_rows(worse, better)
    assert merged == better and downgraded == [], 'fewer missing fragments must win'
    merged, downgraded, _pr = merge_store_rows(better, worse)
    assert merged == better and downgraded == ['x~~a'], 'more missing fragments must lose'

    # H2146 (FINDINGS §513): human-touched store rows are PROTECTED from machine
    # replacement -- reviewer stamp, non-ai_* review_status, or editorial_decision*
    # each protect independently; --override-reviewed restores the old behaviour.
    machine_new = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'machine-redo',
                    'review_status': 'ai_translated', 'reviewer': None,
                    'provenance': {}}]
    for label, human_row in (
            ('approved+reviewer', {'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                                   'review_status': 'approved', 'reviewer': 'MG',
                                   'provenance': {}}),
            ('needs_review', {'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                              'review_status': 'needs_review', 'reviewer': None,
                              'provenance': {}}),
            ('editorial stamp', {'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                                 'review_status': 'ai_translated', 'reviewer': None,
                                 'editorial_decision_id': 'D42', 'provenance': {}})):
        merged, downgraded, protected = merge_store_rows([human_row], machine_new)
        assert merged == [human_row] and protected == ['x~~a'] and downgraded == [], \
            'human overlay (%s) must survive a machine re-promote' % label
        assert merged[0]['review_status'] == human_row['review_status'] \
            and merged[0].get('reviewer') == human_row.get('reviewer'), \
            'overlay fields must come back intact (%s)' % label
    # Explicit override lands the machine attempt (deliberate re-translation).
    approved = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                 'review_status': 'approved', 'reviewer': 'MG', 'provenance': {}}]
    merged, downgraded, protected = merge_store_rows(
        approved, machine_new, override_reviewed=True)
    assert merged == machine_new and protected == [] and downgraded == [], \
        '--override-reviewed must land the machine attempt'
    # Unrelated subcards still merge normally next to a protected one.
    mixed_store = approved + [{'key1': 'y', 'subcard': 'y~~a', 'ru': 'old',
                               'review_status': 'ai_translated', 'provenance': {}}]
    incoming2 = machine_new + [{'key1': 'y', 'subcard': 'y~~a', 'ru': 'new',
                                'review_status': 'ai_translated', 'reviewer': None,
                                'provenance': {}}]
    merged, downgraded, protected = merge_store_rows(mixed_store, incoming2)
    assert protected == ['x~~a'] and downgraded == []
    assert any(r['subcard'] == 'y~~a' and r['ru'] == 'new' for r in merged), \
        'unprotected sibling subcards must still land'
    assert any(r['subcard'] == 'x~~a' and r['ru'] == 'human-kept' for r in merged)
    assert not human_touched({'review_status': 'ai_translated', 'reviewer': None}), \
        'machine rows must never self-protect'

    # H2146: store_write.locked_store_rewrite -- the shared mutator writer -- refuses
    # to write under a live PromoteClaim (lock serializes mutators against promotes).
    import store_write
    sw_store = os.path.join(d, 'sw-store.jsonl')
    store_write.locked_store_rewrite(sw_store, [{'subcard': 's1'}], tag='selftest')
    with PromoteClaim(sw_store):
        try:
            store_write.locked_store_rewrite(sw_store, [{'subcard': 's2'}], tag='selftest')
            raise AssertionError('locked_store_rewrite must raise ClaimBusy under a claim')
        except ClaimBusy:
            pass
    swb = store_write.locked_store_rewrite(sw_store, [{'subcard': 's3'}], tag='selftest')
    assert swb and os.path.isfile(swb), 'mutator rewrite must leave a unique backup'

    # H2153 (G7 / #977): the content-mass gate sees what the row-count guard cannot —
    # a same-row-count content wipe — and ignores what fooled the byte size: formatting.
    fat = [{'subcard': 'm~~%d' % i, 'ru': 'x' * 100, 'de': 'y' * 50, 'provenance': {}}
           for i in range(10)]
    thin = [dict(r, ru='x' * 5) for r in fat]
    try:
        refuse_content_mass_shrink(fat, thin)
        raise AssertionError('a same-row-count content wipe must be refused')
    except PromotionContractError:
        pass
    refuse_content_mass_shrink(fat, list(reversed(fat)))     # reorder/format-only: passes
    refuse_content_mass_shrink(fat, thin, force=True)        # deliberate reduction: --force
    grown = fat + [{'subcard': 'm~~new', 'ru': 'z' * 40, 'provenance': {}}]
    refuse_content_mass_shrink(fat, grown)                   # growth always passes
    mild = [dict(r, ru='x' * 95) for r in fat]
    refuse_content_mass_shrink(fat, mild)                    # <10% shed passes
    assert content_mass([{'ru': 'ab', 'de': None, 'h': 'c'}]) == 3, \
        'content_mass counts only string content fields'
    # Atomic failure leaves the old store intact and removes the temporary file.
    atomic = os.path.join(d, 'atomic.jsonl')
    with open(atomic, 'w', encoding='utf-8') as f:
        f.write('old\n')
    real_replace = promotion_journal.durable_replace
    try:
        promotion_journal.durable_replace = (
            lambda _src, _dst: (_ for _ in ()).throw(OSError('synthetic crash')))
        try:
            _atomic_write_rows(atomic, new)
        except OSError:
            pass
        else:
            raise AssertionError('atomic replace failure was swallowed')
    finally:
        promotion_journal.durable_replace = real_replace
    assert open(atomic, encoding='utf-8').read() == 'old\n'
    assert not [n for n in os.listdir(d) if n.endswith('.tmp')]
    # Backups are exclusive, collision-resistant copies. A failed copy leaves both the live
    # store and any earlier backup untouched and removes its incomplete destination.
    backup1 = _backup_path(atomic, True)
    backup2 = _backup_path(atomic, True)
    assert backup1 != backup2, 'two promotions must never share a backup name'
    _fsynced_backup(atomic, backup1)
    _fsynced_backup(atomic, backup2)
    assert open(backup1, encoding='utf-8').read() == 'old\n'
    assert open(backup2, encoding='utf-8').read() == 'old\n'
    try:
        _fsynced_backup(atomic, backup1)
    except FileExistsError:
        pass
    else:
        raise AssertionError('backup creation overwrote an existing recovery artifact')
    real_copyfileobj = shutil.copyfileobj
    failed_backup = _backup_path(atomic, False)
    try:
        shutil.copyfileobj = lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OSError('synthetic backup failure'))
        try:
            _fsynced_backup(atomic, failed_backup)
        except OSError:
            pass
        else:
            raise AssertionError('backup copy failure was swallowed')
    finally:
        shutil.copyfileobj = real_copyfileobj
    assert open(atomic, encoding='utf-8').read() == 'old\n'
    assert not os.path.exists(failed_backup), 'partial backup survived a failed copy'
    # H1339 Phase 3: the batched multi-lease transaction — one claim/read/backup/write,
    # per-lease validation + attribution, all-or-nothing, idempotent, byte-stable.
    bd = tempfile.mkdtemp()
    bstore = os.path.join(bd, 'store.jsonl')
    keep_row = {'key1': 'y', 'subcard': 'y~~keep', 'h': 'y', 'sense_tag': '1',
                'de': 'x', 'ru': 'у', 'provenance': {}}
    with open(bstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps(keep_row, ensure_ascii=False) + '\n')
    k2 = 'x~~h0_zz_pw01'
    meta2 = dict(meta, selected_keys=[k2],
                 provenance_classes={k2: 'real'},
                 input_hashes={k2: {'raw_sha256': '3' * 64, 'portrait_sha256': '4' * 64}})
    lease_files = {}
    for lease_id, key, m in (('L1', 'p_a~~h5_00_pwg00', meta), ('L2', k2, meta2)):
        d2 = os.path.join(bd, lease_id)
        os.makedirs(d2)
        fp = os.path.join(d2, 'wf_output.clean.%s.json' % lease_id)
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump({'meta': m, 'results': [{'key': key, 'card': entry['card']}]}, f)
        lease_files[lease_id] = (fp, key)
    batch = [{'lease_id': lid, 'run_id': 'run-' + lid,
              'attempt_id': 'attempt-' + lid,
              'glob': fp, 'expected_subcards': [key]}
             for lid, (fp, key) in lease_files.items()]
    unjournaled_before = open(bstore, 'rb').read()
    try:
        batch_promote(batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION)
        raise AssertionError('unjournaled mutating batch was accepted')
    except PromotionContractError as exc:
        assert 'requires --journal' in str(exc)
    assert open(bstore, 'rb').read() == unjournaled_before
    batch_journal = os.path.join(bd, 'batch.journal.json')
    batch_report = os.path.join(bd, 'batch.report.json')
    rep = batch_promote(
        batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=batch_journal, promotion_id='batch-selftest',
        report_path=batch_report)
    assert rep['leases']['L1']['subcards'] == 1 and rep['leases']['L2']['subcards'] == 1
    # H1386 D3: PER-LEASE delta figures, not the bundle-wide before/after stamped N times.
    for lid in ('L1', 'L2'):
        row = rep['leases'][lid]
        assert row['rows_added'] == row['rows'] and row['rows_replaced'] == 0, row
        assert row['store_delta'] == row['rows'], row
    bytes1 = open(bstore, 'rb').read()
    report_bytes1 = open(batch_report, 'rb').read()
    assert b'y~~keep' in bytes1, 'unrelated store row must survive the batch'
    rep2 = batch_promote(
        batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=batch_journal, promotion_id='batch-selftest',
        report_path=batch_report)
    assert open(bstore, 'rb').read() == bytes1, 'batch rerun must be byte-stable/idempotent'
    assert rep2 == rep, 'journal retry must return the sealed report'
    assert open(batch_report, 'rb').read() == report_bytes1, (
        'journal retry report must be byte-idempotent')
    # PREPARED and report-replace death points are independently recoverable.
    pstore = os.path.join(bd, 'prepared-store.jsonl')
    with open(pstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps(keep_row, ensure_ascii=False) + '\n')
    pbefore = open(pstore, 'rb').read()
    pjournal = os.path.join(bd, 'prepared.journal.json')
    preport = os.path.join(bd, 'prepared.report.json')
    def _die_prepared(point):
        if point == 'prepared':
            raise RuntimeError('synthetic prepared death')
    try:
        batch_promote(
            batch, pstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=pjournal, promotion_id='prepared-selftest',
            report_path=preport, fault_hook=_die_prepared)
        raise AssertionError('prepared fault hook did not fire')
    except RuntimeError as exc:
        assert 'prepared death' in str(exc)
    assert open(pstore, 'rb').read() == pbefore
    assert promotion_journal.load(pjournal)['phase'] == 'prepared'
    def _die_report_replace(point):
        if point == 'report_replace':
            raise RuntimeError('synthetic report replace death')
    try:
        batch_promote(
            batch, pstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=pjournal, promotion_id='prepared-selftest',
            report_path=preport, fault_hook=_die_report_replace)
        raise AssertionError('report_replace fault hook did not fire')
    except RuntimeError as exc:
        assert 'report replace death' in str(exc)
    assert promotion_journal.load(pjournal)['phase'] == 'store_committed'
    preport_bytes = open(preport, 'rb').read()
    batch_promote(
        batch, pstore, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=pjournal, promotion_id='prepared-selftest',
        report_path=preport)
    assert open(preport, 'rb').read() == preport_bytes
    # Recover the exact death window: store replace succeeded, PREPARED ->
    # STORE_COMMITTED phase write did not. Re-entry adopts only the sealed after hash.
    jstore = os.path.join(bd, 'journal-store.jsonl')
    with open(jstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps(keep_row, ensure_ascii=False) + '\n')
    jpath = os.path.join(bd, 'promotion.journal.json')
    rpath = os.path.join(bd, 'promotion.report.json')
    old_tm_dir = os.environ.get('PWG_RU_TM_DIR')
    os.environ['PWG_RU_TM_DIR'] = bd
    def _die_after_replace(point):
        if point == 'store_replace':
            raise RuntimeError('synthetic death after replace')
    try:
        try:
            batch_promote(
                batch, jstore, 'ai_translated', SELFTEST_MODEL_VERSION,
                journal_path=jpath, promotion_id='selftest-promotion',
                report_path=rpath, fault_hook=_die_after_replace)
            raise AssertionError('after-replace fault hook did not fire')
        except RuntimeError as exc:
            assert 'synthetic death' in str(exc)
        assert promotion_journal.load(jpath)['phase'] == 'prepared'
        assert promotion_journal.reconcile(jpath, adopt_after=False)[
            'action'] == 'adopt_store_commit'
        recovered = batch_promote(
            batch, jstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=jpath, promotion_id='selftest-promotion',
            report_path=rpath)
        assert recovered['promotion_id'] == 'selftest-promotion', recovered
        assert promotion_journal.load(jpath)['phase'] == 'store_committed'
        assert os.path.isfile(rpath), 'batch report must be atomic and present after retry'
    finally:
        if old_tm_dir is None:
            os.environ.pop('PWG_RU_TM_DIR', None)
        else:
            os.environ['PWG_RU_TM_DIR'] = old_tm_dir
    # all-or-nothing: a lease whose clean output diverges from its expectation fails the
    # WHOLE bundle with the store byte-identical.
    bad = [dict(batch[0]), dict(batch[1], expected_subcards=['not~~this'])]
    try:
        batch_promote(
            bad, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=os.path.join(bd, 'bad.journal.json'),
            promotion_id='bad-selftest')
        raise AssertionError('divergent lease expectation did not fail the bundle')
    except PromotionContractError:
        pass
    assert open(bstore, 'rb').read() == bytes1, 'failed bundle must leave the store unchanged'
    # Multi-sense replacement is one atomic subcard replacement: no stale old
    # sense may survive and no new sense may be dropped.
    multi_key = 'multi~~h0_00_pwg00'
    multi_meta = dict(
        meta, root='multi', selected_keys=[multi_key],
        provenance_classes={multi_key: 'real'},
        input_hashes={multi_key: {
            'raw_sha256': '7' * 64, 'portrait_sha256': '8' * 64}})
    multi_card = {
        'key1': multi_key, 'iast': 'multi', 'notes': '', 'records': [{
            'h': 'multi', 'grammar': '', 'senses': [
                {'tag': '1', 'russian': 'новый один', 'german': 'neu eins',
                 'equivalence_type': 'equivalent', 'source_type': 'attested',
                 'stratum': '', 'differentia': ''},
                {'tag': '2', 'russian': 'новый два', 'german': 'neu zwei',
                 'equivalence_type': 'equivalent', 'source_type': 'attested',
                 'stratum': '', 'differentia': ''},
            ],
        }],
    }
    multi_wf = os.path.join(bd, 'wf_output.multi.json')
    with open(multi_wf, 'w', encoding='utf-8') as f:
        json.dump({'meta': multi_meta, 'results': [
            {'key': multi_key, 'card': multi_card}]}, f)
    multi_store = os.path.join(bd, 'multi.store.jsonl')
    with open(multi_store, 'w', encoding='utf-8') as f:
        for tag, ru in (('1', 'старый один'), ('2', 'старый два')):
            f.write(json.dumps({
                'key1': 'multi', 'subcard': multi_key, 'h': 'multi',
                'sense_tag': tag, 'de': 'alt ' + tag, 'ru': ru,
                'provenance': {},
            }, ensure_ascii=False) + '\n')
    batch_promote(
        [{'lease_id': 'LM', 'run_id': 'run-LM', 'attempt_id': 'attempt-LM',
          'glob': multi_wf, 'expected_subcards': [multi_key]}],
        multi_store, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=os.path.join(bd, 'multi.journal.json'),
        promotion_id='multi-selftest')
    with open(multi_store, encoding='utf-8') as f:
        multi_rows = [json.loads(line) for line in f if line.strip()]
    assert len(multi_rows) == 2, multi_rows
    assert [row['ru'] for row in multi_rows] == ['новый один', 'новый два']
    # bundle-fails when the store already holds a strictly better attempt (a freshly
    # audited lease should never lose better-attempt-wins).
    partial_card = dict(entry['card'], partial=True, missing_fragments=['g1:f0'])
    fp1, key1 = lease_files['L1']
    with open(fp1, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': key1, 'card': partial_card}]}, f)
    try:
        batch_promote(
            batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=os.path.join(bd, 'downgrade.journal.json'),
            promotion_id='downgrade-selftest')
        raise AssertionError('a partial attempt over a complete store row did not fail the bundle')
    except PromotionContractError as exc:
        assert 'better attempt' in str(exc)
    assert open(bstore, 'rb').read() == bytes1, 'downgrade bundle must leave the store unchanged'
    print('batch promotion: 2-lease transaction, idempotent+byte-stable, all-or-nothing OK')

    # H1553 / H1403 A3: defect-key refusal + ready_partial clean-subset (temp store only).
    ddef = tempfile.mkdtemp()
    defect_list = os.path.join(ddef, 'requeue.defect.keys.txt')
    with open(defect_list, 'w', encoding='utf-8') as f:
        f.write('bad~~key\n')
        f.write('p_a~~h5_00_pwg00\n')
    assert load_defect_keys(defect_list) == ['bad~~key', 'p_a~~h5_00_pwg00']
    blocked = refuse_defect_keys(
        ['p_a~~h5_00_pwg00', 'ok~~key'], ['p_a~~h5_00_pwg00', 'other'], force=False)
    assert blocked == ['p_a~~h5_00_pwg00'], blocked
    assert refuse_defect_keys(['p_a~~h5_00_pwg00'], ['p_a~~h5_00_pwg00'], force=True) == []
    assert refuse_defect_keys(['ok~~key'], ['p_a~~h5_00_pwg00'], force=False) == []
    assert refuse_defect_keys(['ok~~key'], [], force=False) == []

    tstore = os.path.join(ddef, 'store.jsonl')
    # seed one row so apply has a merge target
    with open(tstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps({
            'key1': 'keep', 'subcard': 'y~~keep', 'h': 'y', 'sense_tag': '1',
            'de': 'x', 'ru': 'y', 'review_status': 'ai_translated',
            'layer': 'pwg', 'provenance': {},
        }, ensure_ascii=False) + '\n')
    clean_report = {
        'keys': ['p_a~~h5_00_pwg00', 'bad~~key'],
        'requeue': ['bad~~key'],
        'requeue_defect': ['bad~~key'],
        'null_cards': [],
        'requeue_transient': [],
    }
    dry = promote_ready_partial_clean(clean_report, dry_run=True, store=tstore)
    assert dry['status'] == 'dry_run_ok' and dry['clean_keys'] == ['p_a~~h5_00_pwg00'], dry
    assert dry['promoted_keys'] == ['p_a~~h5_00_pwg00']
    # refuse when clean somehow intersects defect
    dirty_report = {
        'keys': ['p_a~~h5_00_pwg00'],
        'requeue': [],
        'requeue_defect': ['p_a~~h5_00_pwg00'],
        'null_cards': [],
    }
    # clean_keys_from_report excludes defect → no_clean_keys
    empty = promote_ready_partial_clean(dirty_report, dry_run=True, store=tstore)
    assert empty['status'] == 'no_clean_keys', empty
    # force path still dry-runs without writing
    force_dry = promote_ready_partial_clean(
        clean_report, dry_run=True, store=tstore, force=True)
    assert force_dry['status'] == 'dry_run_ok'
    before = open(tstore, 'rb').read()
    # apply with a real wf file for the clean key only
    wf_clean = os.path.join(ddef, 'wf_output.clean.json')
    with open(wf_clean, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [
            {'key': 'p_a~~h5_00_pwg00', 'card': entry['card']}]}, f)
    applied = promote_ready_partial_clean(
        clean_report, dry_run=False, store=tstore,
        gen_model_version=SELFTEST_MODEL_VERSION, wf_glob=wf_clean)
    assert applied['status'] == 'applied', applied
    assert 'p_a~~h5_00_pwg00' in applied['promoted_keys']
    after = open(tstore, 'rb').read()
    assert after != before and b'pA' in after or b'p_a' in after or b'\xd0' in after, \
        'applied promote must land rows in the temp store'
    # dry-run must not have been the writer for the earlier check — re-assert fence
    dry2 = promote_ready_partial_clean(clean_report, dry_run=True, store=tstore)
    assert dry2['status'] == 'dry_run_ok'
    print('H1553 defect refusal + ready_partial clean-subset (temp store) OK')
    print('promote_final_cards selftest OK')




if __name__ == "__main__":
    sys.exit(selftest())
