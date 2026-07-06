#!/usr/bin/env python
"""Smoke tests for frequency-window architecture guardrails.

This script intentionally uses ignored runtime files and temporary directories
only. It does not require a fresh Max run.

  python src/pilot/window_selftest.py
"""
import hashlib
import datetime
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
OUT = os.path.join(HERE, 'output')

if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from workflow_payload import workflow_payload
from window_common import harness_meta
from window_provenance import current_root_provenance, stale_check
from prompt_rule_audit import (
    DEFAULT_TEMPLATE,
    audit_card_result,
    audit_cards,
    build_report,
    braced_gloss_risks,
    semantic_risks,
)
from fix_german_connectives import fix_text as fix_german_text
import audit_coverage


def fail(message):
    raise AssertionError(message)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def manifest_files(edition_dir):
    files = {}
    for dirpath, _dirs, names in os.walk(edition_dir):
        for name in names:
            if name == 'release_manifest.json':
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, edition_dir).replace('\\', '/')
            files[rel] = {'sha256': sha256(path), 'bytes': os.path.getsize(path)}
    return dict(sorted(files.items()))


def load_gate_statuses(edition_dir):
    statuses = {}
    path = os.path.join(edition_dir, 'roadmap', 'quality_gates.jsonl')
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                statuses[row.get('id')] = row.get('status')
    return statuses


def write_minimal_edition(edition_dir):
    os.makedirs(edition_dir, exist_ok=True)
    shutil.copytree(os.path.join(ROOT, 'schemas'), os.path.join(edition_dir, 'schemas'))
    shutil.copytree(os.path.join(ROOT, 'roadmap'), os.path.join(edition_dir, 'roadmap'))
    for name in ('CITATION.cff', 'DOI_PLAN.md'):
        shutil.copy2(os.path.join(ROOT, name), os.path.join(edition_dir, name))
    with open(os.path.join(edition_dir, 'assembled_cards.jsonl'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'key1': 'agni', 'records': [{'lossless': True}]}, ensure_ascii=False) + '\n')
    with open(os.path.join(edition_dir, 'reverse_index.jsonl'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'ru': 'огонь', 'key1': 'agni'}, ensure_ascii=False) + '\n')
    with open(os.path.join(edition_dir, 'tei_lex0.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?><TEI><text><body><entry xml:id="agni"/></body></text></TEI>\n')
    ET.parse(os.path.join(edition_dir, 'tei_lex0.xml'))
    with open(os.path.join(edition_dir, 'ontolex.ttl'), 'w', encoding='utf-8') as f:
        f.write('@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .\n')
        f.write('<agni> a ontolex:LexicalEntry .\n')
    manifest = {
        'edition_id': os.path.basename(edition_dir),
        'gate_statuses': load_gate_statuses(edition_dir),
        'files': manifest_files(edition_dir),
    }
    with open(os.path.join(edition_dir, 'release_manifest.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


def run(cmd, expect):
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if proc.returncode != expect:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        fail('%s returned %d, expected %d' % (' '.join(cmd), proc.returncode, expect))
    return proc


def test_workflow_payload_nested():
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'outer': {'meta': {'root': 'sTA'}, 'results': [
            {'key': 'k1', 'card': {'ok': True}},
            {'key': 'k2', 'card': None},
        ]}}, f)
    try:
        _payload, meta, _results, keys, nulls = workflow_payload(path)
    finally:
        os.remove(path)
    if meta.get('root') != 'sTA' or keys != ['k1', 'k2'] or nulls != ['k2']:
        fail('workflow_payload nested extraction failed')


def test_harness_scope_and_tools():
    meta = harness_meta()  # canonical opt2 harness (window_common.OPT_HARNESS)
    if not meta.get('ok'):
        fail('optimized harness missing or invalid: %s' % meta.get('error'))
    is_nominal = bool((meta.get('meta') or {}).get('nominal'))
    current = current_root_provenance(meta.get('root'), meta.get('selected_keys'),
                                      nominal=is_nominal)
    if not current.get('ok'):
        fail('current root provenance unavailable: %s' % current.get('error'))
    if not is_nominal and meta.get('rootmap_sha256') != current.get('rootmap_sha256'):
        fail('optimized harness rootmap hash does not match current rootmap')
    if is_nominal and meta.get('rootmap_sha256') is not None:
        fail('nominal optimized harness must not pretend to have a rootmap hash')
    if meta.get('selected_keys') != current.get('selected_keys'):
        fail('optimized harness selected_keys do not match current rootmap selection')
    text = open(meta['path'], encoding='utf-8').read()
    # Every schema-bearing model call must carry tools: [] (the yuj file-read-blowup guard).
    # Since the kill gate (H155 follow-up) the call sites go through agentKill(prompt, {..}),
    # not a bare agent(prompt, {..}); count both so the guard still holds whichever is used.
    agent_calls = text.count('agentKill(prompt, {') + text.count('agent(prompt, {')
    tool_guards = text.count('tools: []')
    if agent_calls != tool_guards or not tool_guards:
        fail('optimized harness tools guard mismatch: %d agent calls, %d guards' %
             (agent_calls, tool_guards))


def test_stale_check_key_order_independent():
    """stale_check must compare workflow result-key order against meta.selected_keys as a
    SET, not a positional list — the harness assembles results TM-lane-first then
    DEGENERATE-lane then per-batch-completion order, which never matches the rootmap's
    declared order even when every key is present exactly once."""
    meta = harness_meta()
    if not meta.get('ok'):
        fail('optimized harness missing or invalid: %s' % meta.get('error'))
    root = meta.get('root')
    is_nominal = bool((meta.get('meta') or {}).get('nominal'))
    current = current_root_provenance(root, meta.get('selected_keys'), nominal=is_nominal)
    if not current.get('ok'):
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


def test_no_pwg_worklist_runnable_lane():
    """H214: the worklist exposes a no_pwg_runnable lane for PW/SCH/PWKVN-only lemmas and does
    NOT reclassify a true miss (absent from every layer) as runnable, nor mix it into the
    PWG-rooted runnable count."""
    import nominals_worklist as nw
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'sample.slp1.txt')
        store = os.path.join(tmp, 'store.jsonl')      # isolated empty store: the runnable/promoted
        with open(path, 'w', encoding='utf-8') as f:  # split must not depend on the live store
            f.write('Bagavat\nAkulita\nZZzznotaword\n')      # pw-only, sch-only, true miss
        open(store, 'w', encoding='utf-8').close()
        payload = nw.build_worklist(path, store=store)
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


def test_prompt_rule_audit_template():
    report = build_report([DEFAULT_TEMPLATE])
    if report.get('missing_rule_count'):
        missing = []
        for target in report['targets']:
            for rule in target.get('missing') or []:
                missing.append('%s:%s' % (os.path.basename(target['path']), rule['id']))
        fail('prompt-rule audit missing required rules: %s' % ', '.join(missing))
    coverage = set(report.get('live_manual_coverage') or [])
    expected = {'Apresjan', 'Hartmann', 'Gonda/Vogel', 'Tubb',
                'Baalbaki', 'Apte/Gillon/Inglese-Geupel',
                'Mitrenina/Zaliznyak-Paducheva/Ruppel'}
    if not expected.issubset(coverage):
        fail('prompt-rule audit missing manual coverage labels: %s' %
             ', '.join(sorted(expected - coverage)))


def test_prompt_rule_audit_missing_blocks():
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.js', delete=False) as f:
        path = f.name
        f.write('const CHECKS = "Apresjan only";\n')
    try:
        report = build_report([path])
        if not report.get('missing_rule_count'):
            fail('prompt-rule missing fixture did not report missing rules')
    finally:
        os.remove(path)


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


def semantic_card_risk_ids(russian, german='{%nachgehen%}'):
    card = {'card': {'key1': 'x', 'iast': 'x', 'notes': '', 'records': [{
        'h': 'x', 'grammar': 'ind.', 'senses': [{
            'tag': '1', 'german': german, 'russian': russian,
            'equivalence_type': 'explanatory', 'source_type': 'lexicographic',
            'stratum': '', 'differentia': ''}]}]}}
    return {risk['id'] for risk in semantic_risks(card)}


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
                    'german': '<ls>ṚV.</ls> Feuer',
                    'russian': 'мужской Ригведа {#agni',
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


def test_release_manifest_hash_validation():
    with tempfile.TemporaryDirectory() as tmp:
        edition = os.path.join(tmp, 'edition_selftest')
        write_minimal_edition(edition)
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=0)
        with open(os.path.join(edition, 'reverse_index.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({'ru': 'дым', 'key1': 'dhUma'}, ensure_ascii=False) + '\n')
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=1)


def test_lang_parity_ledger_complete():
    """LANG_PARITY.md's ledger must have a verdict for every entry (SHARED /
    INTENTIONAL-DIVERGENCE with a note / GAP with a tracking ref), and no tracked
    file may have drifted since its entry was last verified. See LANG_PARITY.md."""
    import lang_parity_check
    entries, _, _ = lang_parity_check.load_ledger()
    violations = lang_parity_check.check(entries)
    if violations:
        fail('LANG_PARITY.md has %d unresolved parity violation(s):\n  %s'
             % (len(violations), '\n  '.join(violations)))


def test_lang_parity_hash_crlf_independent():
    """file_sha256() must normalize CRLF->LF so verified_sha256 snapshots match the git-blob
    content regardless of core.autocrlf on the checkout OS (Windows disk bytes carry CRLF;
    Linux/CI checkouts and git blobs carry LF) — see LANG_PARITY.md fix, 2026-07-04."""
    import tempfile
    import lang_parity_check
    with tempfile.TemporaryDirectory() as tmp:
        lf_path = os.path.join(tmp, 'lf.txt')
        crlf_path = os.path.join(tmp, 'crlf.txt')
        with open(lf_path, 'wb') as f:
            f.write(b'line one\nline two\n')
        with open(crlf_path, 'wb') as f:
            f.write(b'line one\r\nline two\r\n')
        old_root = lang_parity_check.REPO_ROOT
        lang_parity_check.REPO_ROOT = tmp
        try:
            lf_hash = lang_parity_check.file_sha256('lf.txt')
            crlf_hash = lang_parity_check.file_sha256('crlf.txt')
        finally:
            lang_parity_check.REPO_ROOT = old_root
        if lf_hash != crlf_hash:
            fail('file_sha256 is not CRLF/LF-independent: %s != %s' % (lf_hash, crlf_hash))


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
            n_en = rq.append_tm_denylist('zz', ['k1'], 'defect', lang='en')
            n_ru = rq.append_tm_denylist('zz', ['k1'], 'defect', lang='ru')
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


def test_ru_coverage_denominator_not_silently_exempt():
    """FL3: a corrupt EN denominator must FAIL the coverage gate (not be silently skipped),
    and a RU root with no denominator must be surfaced as UNVERIFIABLE (the gam 6/127 blind
    spot), never exempted."""
    import io
    import contextlib
    import ru_coverage
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'wf_output.en.aa.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps({'meta': {'selected_keys': ['aa~~h0_00_pwg00']}}))
        with open(os.path.join(tmp, 'wf_output.en.bb.json'), 'w', encoding='utf-8') as f:
            f.write('{ broken json')
        store = os.path.join(tmp, 'store.jsonl')
        with open(store, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'key1': 'aa', 'subcard': 'aa~~h0_00_pwg00'}) + '\n')
            f.write(json.dumps({'key1': 'cc', 'subcard': 'cc~~h0_00_pwg00'}) + '\n')
        old_repo, old_store, old_argv = ru_coverage.REPO, ru_coverage.RU_STORE, sys.argv
        ru_coverage.REPO, ru_coverage.RU_STORE = tmp, store
        try:
            intended, corrupt = ru_coverage.intended_by_root()
            if not any(r == 'bb' for r, _ in corrupt):
                fail('corrupt EN denominator not detected')
            if 'aa' not in intended:
                fail('valid EN denominator dropped')
            sys.argv = ['ru_coverage']
            buf = io.StringIO()
            rc = 0
            try:
                with contextlib.redirect_stdout(buf):
                    ru_coverage.main()
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
            out = buf.getvalue()
            if rc != 1:
                fail('ru_coverage did not FAIL on a corrupt EN denominator (silent exemption)')
            if 'UNVERIFIABLE' not in out:
                fail('a RU root with no EN denominator was not surfaced as UNVERIFIABLE')
        finally:
            ru_coverage.REPO, ru_coverage.RU_STORE, sys.argv = old_repo, old_store, old_argv


def test_coverage_gate_multi_layer_and_presplit():
    """audit_coverage.raw_markers() must not mistake <div n="p"> (a STRUCTURAL prefix/
    secondary-conjugation divider elsewhere in this codebase -- root_units.py,
    scale_preflight.py's _DIVP, verify_root_glue.py) for a numbered sense boundary when a
    sub-card bundles several independent '=== LAYER: ... ===' blocks (PW/SCH/PWKVN addenda,
    e.g. gam~~h0_zz_pw04: 3 layers, 5 raw '<div n=' tags, all cross-reference continuations
    -> the correct count is 3, one per layer, not 5). Also: a presplit/fragment-reassembled
    card's granular per-fragment row count must skip the LOW/OVER thresholds entirely (its
    row count is not comparable to a coarse raw marker count)."""
    three_layer_raw = (
        '=== LAYER: PW ===\n\n'
        '√gam mit aByud 1〉 aByudgata aufgegangen (Sonne) <ls>X. 1</ls>.\n\n'
        '=== LAYER: PW ===\n\n'
        '√gam mit aBi Caus. auch zukommen lassen <ls>Y. 2</ls>.\n'
        '<div n="p">— Mit nis Caus. auch verlieren <ls>Z. 3</ls>.\n\n'
        '=== LAYER: PW ===\n\n'
        '√gam mit aBi Caus. II. 5.\n'
        '<div n="p">— Mit A II. Agamya so v. a. fuer <ls>W. 4</ls>.\n'
        '<div n="p">— Mit aByud II. 3.\n'
        '<div n="p">— Mit nis Caus. II. 5.\n'
        '<div n="p">— Mit upanis hinausgehen zu <ls>V. 5</ls>.\n'
    )
    bodies = audit_coverage.layer_bodies(three_layer_raw)
    if len(bodies) != 3:
        fail('expected 3 layer blocks, got %d' % len(bodies))
    counts = [audit_coverage.layer_sense_count(b) for b in bodies]
    if counts != [1, 1, 1]:
        fail('layer_sense_count must floor a pure-cross-reference layer at 1 sense, not count '
             'every <div n="p"> continuation: got %r' % counts)

    with tempfile.TemporaryDirectory() as tmp:
        in_dir = os.path.join(tmp, 'pilot', 'input')
        os.makedirs(in_dir)
        with open(os.path.join(in_dir, 'zz~~h0_zz_pw04.raw.txt'), 'w', encoding='utf-8') as f:
            f.write(three_layer_raw)
        with open(os.path.join(in_dir, 'zz~~presplit_card.raw.txt'), 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n√gam 1〉 aufgegangen <ls>X. 1</ls>.\n')
        old_in = audit_coverage.IN
        audit_coverage.IN = in_dir
        try:
            rm = audit_coverage.raw_markers('zz~~h0_zz_pw04')
            if rm != 3:
                fail('multi-layer raw_markers must count 1 sense per addenda layer (3), got %r'
                     % rm)

            wf = os.path.join(tmp, 'wf_output.json')
            with open(wf, 'w', encoding='utf-8') as f:
                json.dump({'results': [
                    {'key': 'zz~~h0_zz_pw04', 'presplit': False,
                     'card': {'records': [{'senses': [{}, {}, {}]}]}},
                    {'key': 'zz~~presplit_card', 'presplit': True,
                     'card': {'records': [{'senses': [{}] * 20}]}},
                ]}, f)
            import io, contextlib
            old_argv = sys.argv
            sys.argv = ['audit_coverage', wf]
            buf = io.StringIO()
            rc = 0
            try:
                with contextlib.redirect_stdout(buf):
                    audit_coverage.main()
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
            finally:
                sys.argv = old_argv
            out = buf.getvalue()
            if rc != 0:
                fail('multi-layer addenda card + presplit card must both pass: %s' % out)
            if 'COVERAGE-LOW' in out or 'COVERAGE-OVER' in out:
                fail('coverage gate still flagged a multi-layer/presplit card: %s' % out)
            if 'presplit' not in out:
                fail('presplit card must be labeled as such, not silently ok: %s' % out)
        finally:
            audit_coverage.IN = old_in


def test_en_residual_coverage_complete():
    """FL4: en_residual_keys 'done' means coverage-complete, not '>=1 English sense'. A card
    with 1 of 2 senses translated is a residual (its 1 untranslated sense must not be hidden);
    a fully-translated card is done; a null/empty card is never done."""
    from en_residual_keys import card_done, en_coverage
    partial = {'records': [{'senses': [{'german': 'a', 'english': 'x'}, {'german': 'b'}]}]}
    if en_coverage(partial) != (1, 2):
        fail('en_coverage miscounted the partial card')
    if card_done(partial):
        fail('a 1/2-sense card must NOT count as done (the FL4 1/40 bug)')
    full = {'records': [{'senses': [{'german': 'a', 'english': 'x'},
                                    {'german': 'b', 'english': 'y'}]}]}
    if not card_done(full):
        fail('a fully-translated card must count as done')
    if card_done(None) or card_done({'records': []}):
        fail('a null/empty card must never count as done')


def test_en_split_triage_keeps_missing_input():
    """FL4: a residual (null) card whose source input file is absent must stay VISIBLE in
    triage with a missing_input marker, not be silently skipped."""
    import en_split_triage as est
    with tempfile.TemporaryDirectory() as tmp:
        wf = {'meta': {'selected_keys': ['aa~~h0_00', 'bb~~h0_00']},
              'results': [
                  {'key': 'aa~~h0_00', 'card': {'records': [
                      {'senses': [{'german': 'g', 'english': 'e'}]}]}},
                  {'key': 'bb~~h0_00', 'card': None}]}
        with open(os.path.join(tmp, 'wf_output.en.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False)
        aa_raw = os.path.join(tmp, 'aa.raw.txt')
        with open(aa_raw, 'w', encoding='utf-8') as f:
            f.write('<ls>x</ls> Wasser')

        def fake_paths(key):
            if key == 'aa~~h0_00':
                return aa_raw, aa_raw + '.portrait'
            return os.path.join(tmp, 'nope_%s.txt' % key), ''

        old_repo, old_ip = est.REPO, est.input_paths
        est.REPO, est.input_paths = tmp, fake_paths
        try:
            rows = est.scan()
        finally:
            est.REPO, est.input_paths = old_repo, old_ip
    by = {k: f for _r, k, f, _p in rows}
    if 'bb~~h0_00' not in by:
        fail('missing-input null card was dropped from triage (FL4)')
    if not by['bb~~h0_00'].get('missing_input'):
        fail('missing-input residual not marked missing_input')
    if by['aa~~h0_00'].get('missing_input'):
        fail('a present-input card wrongly marked missing_input')


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
    card = {'records': [{'senses': [{'tag': '1', 'german': 'Feuer',
                                     'russian': 'огонь'}]}]}
    ok, why = gh.tm_card_sane(card, 'ru', 'russian', raw)
    if ok or '<ls>' not in why:
        fail('zero-<ls> cached card must be refused for cited source, got ok=%r why=%r' %
             (ok, why))
    raw2 = '{#agni#}¦ Feuer.'
    card2 = {'records': [{'senses': [{'tag': '1', 'german': 'Feuer',
                                      'russian': 'огонь'}]}]}
    ok2, why2 = gh.tm_card_sane(card2, 'ru', 'russian', raw2)
    if ok2 or '{#' not in why2:
        fail('zero-{# cached card must be refused for Sanskrit-marked source, got ok=%r why=%r' %
             (ok2, why2))


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
        if 'const cand = km[k]' not in js:
            fail('full-card lane must use strict key lookup, not positional fallback')
        if 'res.cards[i]' in js or 'res.cards[idx], fi' in js:
            fail('generated harness still has unsafe positional response assignment')
        if 'missing-or-mismatched-key' not in js:
            fail('missing/mismatched full-card keys must get an explicit failure reason')
        if 'missing-or-mismatched-fragment-key' not in js:
            fail('missing/mismatched fragment keys must get an explicit failure reason')
    finally:
        gh.input_paths = saved_ip
        shutil.rmtree(d, ignore_errors=True)


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
    """A safely-degenerate cross-reference stub is emitted as an accounted no-LLM row and is
    excluded from translation lanes; it is never a silent skip."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import input_paths, read_text
    key = 'ab'
    rp, pp = input_paths(key)
    if not (os.path.exists(rp) and os.path.exists(pp)):
        return
    card = gh.degenerate_passthrough_card(key, read_text(rp), read_text(pp), 'russian')
    if not card or not card.get('degenerate_passthrough'):
        fail('ab fixture should qualify for conservative degenerate pass-through')
    js, batches = gh.build(key, [key], None, 12000, nominal=True, tm_path=None)
    meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
    if meta.get('degenerate_passthrough_keys') != [key]:
        fail('META.degenerate_passthrough_keys must account for the stub key')
    if batches or meta.get('presplit_keys'):
        fail('a degenerate pass-through key must not also enter an agent translation lane')
    if 'const DEGENERATE_RESOLVED' not in js or 'degenerate_passthrough: true' not in js:
        fail('generated harness must emit explicit degenerate pass-through rows')


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


def test_perf_preflight_small_tm_and_no_tm():
    key = 'gam~~h0_03_sec_3'
    proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                '--keys=%s' % key, '--json'], 0)
    report = json.loads(proc.stdout)
    if report['selected_keys'] != [key]:
        fail('perf_preflight must preserve the requested fixed key set')
    if report.get('schema') != 'pwg.performance_preflight.v1' or 'reports' in report:
        fail('single-root perf_preflight JSON must remain the plain v1 report shape')
    if 'tm_available' not in report or 'agent_expected_after_tm' not in report:
        fail('perf_preflight JSON missing TM/agent accounting fields')
    proc2 = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                 '--keys=%s' % key, '--no-tm', '--json'], 0)
    no_tm = json.loads(proc2.stdout)
    if no_tm['tm_auto'] or no_tm['tm_cards'] != 0:
        fail('--no-tm preflight must disable TM accounting')
    if no_tm['batch_count'] < 1 or no_tm['agent_expected_after_tm'] < 1:
        fail('small no-TM card should still be owed by a normal agent lane')


def test_perf_preflight_dense_presplit():
    key = 'gam~~h0_00_pwg00'
    proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                '--keys=%s' % key, '--no-tm', '--json'], 0)
    report = json.loads(proc.stdout)
    if key not in report.get('presplit_keys', []):
        fail('dense key must report presplit routing in performance preflight')
    if report.get('agent_expected_after_tm', 0) < 1:
        fail('dense presplit key must report a nonzero expected agent lane')


def test_perf_preflight_presplit_counts_fragments_not_one():
    """agent_expected_after_tm for a presplit giant must be its true fragment-GROUP count,
    not 1 — the old len(presplit) formula underestimated vid's real 102-agent run as 13.
    H189: the group count is now LOWER than the pre-H189 per-12-citation grouping (the
    presplit lane amortizes at PRESPLIT_GROUP_CITE_BUDGET=60), but it must still be >1 (a
    150+-<ls> giant does not collapse to a single call) — that's the invariant this guards."""
    key = 'gam~~h0_00_pwg00'
    proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                '--keys=%s' % key, '--no-tm', '--json'], 0)
    report = json.loads(proc.stdout)
    if key not in report.get('presplit_keys', []):
        fail('fixture card must still route to presplit')
    if report.get('agent_expected_after_tm', 0) < 2:
        fail('a 150+-<ls> presplit giant needs several fragment-group calls, not ~1 — '
             'got agent_expected_after_tm=%r' % report.get('agent_expected_after_tm'))


def test_perf_preflight_degenerate_zero_agent():
    proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'ab',
                '--nominal', '--keys=ab', '--json'], 0)
    report = json.loads(proc.stdout)
    if report.get('degenerate_passthrough_keys') != ['ab']:
        fail('ab must report degenerate pass-through in performance preflight')
    if report.get('agent_expected_after_tm') != 0:
        fail('degenerate pass-through should report zero expected agents')


def test_perf_preflight_multi_root_matrix_and_order():
    tm_sidecar = os.path.join(HERE, 'translation_memory.ru.json')
    if not os.path.exists(tm_sidecar):
        return
    proc = run([sys.executable, 'src/pilot/perf_preflight.py',
                'gam', 'han', 'as', 'vid', '--json'], 0)
    matrix = json.loads(proc.stdout)
    if matrix.get('schema') != 'pwg.performance_preflight.matrix.v1':
        fail('multi-root perf_preflight JSON must use the matrix wrapper')
    reports = {r['root']: r for r in matrix.get('reports', [])}
    for root in ['gam', 'han', 'as', 'vid']:
        if root not in reports:
            fail('multi-root matrix missing %s' % root)
    if reports['han'].get('agent_expected_after_tm') != 0:
        fail('han should be recognized as fully cached / zero-agent in the local TM preflight')
    if 'han' not in matrix.get('recommended_order', {}).get('skip_cached', []):
        fail('fully cached roots must be listed in skip_cached')
    # `as` carries presplit giants and is uncached in the local TM, so its true
    # agent_expected_after_tm must EXCEED its presplit-key count (the pre-fix len(presplit)
    # formula undercounted vid's real 102-agent run as 13) and it defers rather than
    # run_first. H189 note: the per-call count is now lower than pre-H189 (the presplit lane
    # amortizes at PRESPLIT_GROUP_CITE_BUDGET), but the no-undercount invariant still holds.
    # vid is NOT asserted: its classification depends on how much of it the local TM has
    # cached (a mostly-cached vid is legitimately cheap / run-now), same live-state caveat
    # as han's skip-cached above.
    as_r = reports['as']
    if as_r.get('agent_expected_after_tm', 0) <= len(as_r.get('presplit_keys', [])):
        fail('a presplit-giant root must count real fragment-GROUP calls, exceeding its '
             'len(presplit) — got agents=%r presplit=%r'
             % (as_r.get('agent_expected_after_tm'), len(as_r.get('presplit_keys', []))))
    if 'as' not in matrix.get('recommended_order', {}).get('defer', []):
        fail('an uncached presplit-giant root should defer-calibrate, not run_first')


def test_perf_preflight_fragment_tm_empty_warning():
    from window_common import rootmap_path, input_paths
    root = 'gam'
    key = 'gam~~h0_00_pwg00'
    rmpath, _ = rootmap_path(root)
    if not rmpath or not os.path.exists(input_paths(key)[0]):
        return
    with tempfile.TemporaryDirectory() as tmp:
        tm_sidecar = os.path.join(tmp, 'translation_memory.ru.json')
        with open(tm_sidecar, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.translation_memory.v1', 'lang': 'ru', 'entries': {}}, f)
        proc = run([sys.executable, 'src/pilot/perf_preflight.py', root,
                    '--keys=%s' % key, '--tm=%s' % tm_sidecar,
                    '--wf-glob=no_such_frag_prov_fixture_*.json', '--json'], 0)
        report = json.loads(proc.stdout)
        warnings = report.get('warnings') or []
        if key not in report.get('presplit_keys', []):
            fail('dense fixture must route to presplit for fragment-TM warning test')
        joined = '\n'.join(warnings)
        if 'build-frags --lang ru' not in joined:
            fail('empty fragment TM warning must include the build-frags command')
        if 'no fragment provenance available yet' not in joined:
            fail('empty fragment TM warning must state when no frag_prov source exists')


def test_perf_preflight_partitions_mixed_monster_window():
    import gen_opt_harness2 as gh
    import perf_preflight as pp
    import types
    with tempfile.TemporaryDirectory() as tmp:
        cheap, monster = 'h191cheap', 'h191monster'
        raws = {
            cheap: '=== LAYER: PWG — MAIN ENTRY ===\n{%kurzer deutscher Text%} ohne Citate.',
            monster: '=== LAYER: PWG — MAIN ENTRY ===\n{%Monster%} ' +
                     ' '.join('<ls n="T%d">Quelle %d</ls>' % (i, i) for i in range(220)),
        }
        for key, raw in raws.items():
            with open(os.path.join(tmp, key + '.raw.txt'), 'w', encoding='utf-8') as f:
                f.write(raw)
            with open(os.path.join(tmp, key + '.portrait.json'), 'w', encoding='utf-8') as f:
                f.write('{}')

        def fake_input_paths(k, input_dir=None):
            return os.path.join(tmp, k + '.raw.txt'), os.path.join(tmp, k + '.portrait.json')

        old_gh_ip, old_pp_ip = gh.input_paths, pp.input_paths
        gh.input_paths = fake_input_paths
        pp.input_paths = fake_input_paths
        args = types.SimpleNamespace(keys='%s,%s' % (cheap, monster), nominal=True,
                                     tm_auto=False, tm_path=None, lang='ru',
                                     budget=12000, no_grammar=True,
                                     wf_glob='no_such_fixture_*.json',
                                     cost_ceiling_per_card=2.0,
                                     cost_ceiling_window=25.0)
        try:
            report = pp.build_report(args, 'h191mix')
        finally:
            gh.input_paths = old_gh_ip
            pp.input_paths = old_pp_ip
        part = report.get('cost_partition') or {}
        if part.get('run_now') != [cheap]:
            fail('mixed preflight must leave the cheap card runnable, got %r' % part.get('run_now'))
        if part.get('defer_monster') != [monster]:
            fail('mixed preflight must quarantine the monster card, got %r' % part.get('defer_monster'))
        if 'human-budgeted lane' not in (part.get('recommendation') or ''):
            fail('partition recommendation must name the human-budgeted monster lane')


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


def test_coordinator_state_dashboard_and_cap():
    import coordinator
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            state = coordinator.default_state()
            for i in range(3):
                state['leases'].append({
                    'id': 'lease%d' % i,
                    'lane': 'lane%d' % i,
                    'kind': 'verb',
                    'owner': 'selftest',
                    'target': 'root%d' % i,
                    'state': 'prepared',
                    'artifact_dir': os.path.join(tmp, 'artifacts', 'lease%d' % i),
                })
            coordinator.save_state(state)
            loaded = coordinator.load_state()
            if len(coordinator.active_translation_leases(loaded)) != 3:
                fail('coordinator must count exactly three active translation leases')
            dash = json.load(open(os.path.join(tmp, 'dashboard.json'), encoding='utf-8'))
            if dash.get('schema') != coordinator.DASHBOARD_SCHEMA:
                fail('coordinator dashboard schema missing')
            if dash.get('active_translation_leases') != 3 or dash.get('translation_limit') != 3:
                fail('coordinator dashboard must expose cap state')
            state['leases'][0]['state'] = 'promoted'
            coordinator.save_state(state)
            if len(coordinator.active_translation_leases(coordinator.load_state())) != 2:
                fail('promoted leases must not count against the active LLM cap')
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old


def test_coordinator_lock_replaces_stale_dead_owner():
    import coordinator
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, '.state.lock')
        os.mkdir(lock_path)
        old_ts = (datetime.datetime.now(datetime.timezone.utc) -
                  datetime.timedelta(hours=2)).isoformat(timespec='seconds').replace('+00:00', 'Z')
        with open(os.path.join(lock_path, 'owner.json'), 'w', encoding='utf-8') as f:
            json.dump({'pid': 999999999, 'created_at': old_ts}, f)
        with coordinator.DirLock(lock_path, ttl_seconds=1):
            if not os.path.exists(os.path.join(lock_path, 'owner.json')):
                fail('coordinator lock did not recreate owner metadata')


def test_coordinator_defect_requeue_uses_no_tm_and_out():
    import requeue_from_audit as rq

    with tempfile.TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, 'input')
        os.makedirs(inp)
        with open(os.path.join(inp, 'a.raw.txt'), 'w', encoding='utf-8') as f:
            f.write('raw')
        rqfile = os.path.join(tmp, 'requeue.defect.keys.txt')
        with open(rqfile, 'w', encoding='utf-8') as f:
            f.write('a\n')
        out = os.path.join(tmp, 'run_pilot_wf.requeue.js')

        captured = {}

        class FakeProc:
            returncode = 0
            stdout = 'wrote fake harness'
            stderr = ''

        def fake_run(cmd, **_kwargs):
            captured['cmd'] = cmd
            return FakeProc()

        old_inp, old_run = rq.INP, rq.subprocess.run
        old_deny = rq.append_tm_denylist
        old_argv = sys.argv[:]
        rq.INP = inp
        rq.subprocess.run = fake_run
        rq.append_tm_denylist = lambda *_args, **_kwargs: 1
        sys.argv = ['requeue_from_audit.py', 'nominal_selftest', '--defect',
                    '--nominal', '--no-grammar', '--requeue-file=%s' % rqfile,
                    '--out=%s' % out]
        try:
            rq.main()
        finally:
            rq.INP = old_inp
            rq.subprocess.run = old_run
            rq.append_tm_denylist = old_deny
            sys.argv = old_argv
        cmd = captured.get('cmd') or []
        if '--no-tm' not in cmd:
            fail('defect requeue must pass --no-tm')
        if '--nominal' not in cmd or '--no-grammar' not in cmd:
            fail('nominal requeue flags must pass through')
        if '--out=%s' % out not in cmd:
            fail('coordinator requeue must use an explicit harness output path')


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


def test_no_pwg_supplement_chain_cards_render():
    """H214: PWG-missing lemmas with real PW/SCH/PWKVN/NWS records are runnable.

    This uses real dictionary data but writes to a temp input directory, so it proves the
    generator path without touching live pilot/input artifacts.
    """
    import _pilot_gen_merged as pg
    from safe_filename import safe_name
    old_out = pg.OUT
    with tempfile.TemporaryDirectory() as tmp:
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


def test_nominals_worklist_exposes_no_pwg_lane():
    import nominals_worklist as nw
    with tempfile.TemporaryDirectory() as tmp:
        wordlist = os.path.join(tmp, 'sample.slp1.txt')
        store = os.path.join(tmp, 'store.jsonl')
        with open(wordlist, 'w', encoding='utf-8') as f:
            f.write('Bagavat\nAkulita\nnotalocalword\n')
        open(store, 'w', encoding='utf-8').close()
        payload = nw.build_worklist(wordlist, store=store)
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
        with open(os.path.join(d, 'translation_memory.frag.ru.jsonl'), 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': 'pwg.translation_memory.frag.v1', 'lang': 'ru',
                                'fsha': fsha0, 'src_key': target, 'senses': senses0},
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
        if fv[0][0][0]['russian'] != 'кэш':
            fail('cached fragment slot must carry the sidecar senses')
        if gv[0][0].get('fsha') != fsha0:
            fail('FRAGS fragment must carry the content address used for the cache lookup')
        # whole-card accounting: reuse happens INSIDE selfHeal, so the card is still owed by a
        # translate lane (batch or presplit), never silently dropped.
        batched = {k for b in meta['batches'] for k in b}
        if target not in (batched | set(meta['presplit_keys'])):
            fail('a fragment-reusing card must still be owed by a translate lane')
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_no_fallback_batch_isolation():
    """Collateral-null fix (2026-07-04): a card with NO selfheal fallback (split_plan() < 2
    fragments) must never share a batch with a card that DOES have one. Mixed together, a
    whole-batch hard failure (StructuredOutput retry cap) drags the no-fallback card down
    with it even though its own content had nothing to do with the failure — only the
    fallback-having card can be rescued via selfHeal. Verified on real 'gam' fixtures: pick
    one splittable card and one unsplittable card, force them into the same output-budget
    window, and assert build() never puts them in the same batch."""
    import gen_opt_harness2 as gh
    from autosplit_requeue import plan as split_plan
    from window_common import rootmap_path, input_paths, read_text
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return  # inputs not present in this checkout — nothing to assert
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])]
    fallback_key, nofallback_key = None, None
    for k in keys:
        pl = split_plan(read_text(input_paths(k)[0]))
        if len(pl) >= 2 and fallback_key is None:
            fallback_key = k
        elif len(pl) < 2 and nofallback_key is None:
            nofallback_key = k
        if fallback_key and nofallback_key:
            break
    if not (fallback_key and nofallback_key):
        return  # fixture set doesn't offer both shapes — nothing to assert
    # a generous shared OUTPUT_BUDGET so both cards would land in ONE batch under the
    # pre-fix (budget-only) grouping — the isolation must still keep them apart.
    saved_budget = gh.OUTPUT_BUDGET
    gh.OUTPUT_BUDGET = 1000
    try:
        js, batches = gh.build(root, [fallback_key, nofallback_key], rootmap, 100000, tm_path=None)
    finally:
        gh.OUTPUT_BUDGET = saved_budget
    for b in batches:
        if fallback_key in b and nofallback_key in b:
            fail('a no-selfheal-fallback card must never share a batch with a '
                 'fallback-having card — got both in %r' % (b,))
    if not any(nofallback_key in b for b in batches):
        fail('no-fallback key must still be owed by some batch')
    if not any(fallback_key in b for b in batches):
        fail('fallback key must still be owed by some batch')


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


def test_selfheal_fragment_si_threaded_and_tags_normalized():
    """Regression for the 2026-07-04 vid drain SENSE-DUPE false-positive: root vid's
    homonym head h0's giant single-sense part (h0_00_pwg00, source sense '1', 168 <ls>
    citations) was tier-2 split into many citation-batch fragments, all belonging to the
    SAME source sense — but FRAGS[k] (the fragment fallback fed to the JS selfHeal path)
    discarded split_plan()'s sense_ord (previously bound to `_si` and thrown away), so the
    JS heal path had no way to know the fragments shared a parent sense. Translating each
    fragment independently, the model fabricated fresh incrementing tags per fragment
    (2,3,4...) that then collided with a sibling rootmap part's REAL different senses in
    audit_sense_dupes.py's cross-part duplicate check — a deterministic tagging artifact,
    not model stochasticity (reproduced identically across 2 independent live requeue
    rounds). Fixed by threading sense_ord into FRAGS as 'si' (Python side, gen_opt_harness2)
    and normalizing every fragment's tag to its group's first-seen tag per si in JS
    selfHeal() (siTag/applyTag — verified by code inspection; window_selftest has no JS
    runtime). This test exercises the Python-side wiring: a citation-dense single-sense
    fixture card must produce >=2 FRAGS fragments that ALL carry the same si."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import input_paths
    from autosplit_requeue import plan as split_plan
    key = '_selftest_giant~~h0_00_pwgtest'
    lines = ['Uebersicht der Citate zu diesem einzigen Sinn dieses Testkopfes.']
    for i in range(25):
        lines.append('Wort%d <ls n="RV.%d.1">citation text %d</ls> und mehr erlaeuternder Text.'
                     % (i, i, i))
    raw = '\n'.join(lines)
    rp, pp = input_paths(key)
    if os.path.exists(rp) or os.path.exists(pp):
        fail('selftest fixture key collides with a real input file — pick a different key')
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    try:
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('{}')
        pl = split_plan(raw)
        if len(pl) < 2:
            fail('fixture did not produce a multi-fragment plan — adjust the fixture')
        if len({si for si, _pi, _t in pl}) != 1:
            fail('fixture should be ONE giant sense split into citation batches (all si==0)')
        js, _batches = gh.build('_selftest_giant', [key], None, 100000, tm_path=None)
        frags = json.loads(_re.search(r'^const FRAGS = (.*)$', js, _re.M).group(1))
        if key not in frags:
            fail('selfheal fallback was not computed for the fixture card')
        sis = [frag.get('si') for grp in frags[key] for frag in grp]
        if len(sis) < 2:
            fail('fixture did not thread into >=2 FRAGS fragments')
        if any(si is None for si in sis):
            fail('FRAGS fragments are missing the si (sense_ord) field — the '
                 'fragment-tag-collision fix regressed')
        if len(set(sis)) != 1:
            fail('all fragments of one giant sense must share the SAME si, got %r' % sis)
    finally:
        for p in (rp, pp):
            if os.path.exists(p):
                os.remove(p)


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


def test_kill_gate_wired():
    """H155 follow-up (2026-07-04): the wall-clock kill gate must be wired into every
    schema-bearing agent() call so a stalled/doomed call (the ~7-min tyaj~~h0_zz_pw
    retry-cap loop, or any un-characterized future driver) is abandoned at KILL_FACTOR x
    its expected-for-complexity time and routed to the bounded fragment lane — instead of
    burning the full StructuredOutput retry cap. Static regression guard on the generated
    harness: the kill consts render, the budget helper + both call sites use agentKill,
    INPUTS carries the skeleton (the complexity signal), and --no-kill disables it."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_kill'
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
            # consts present with the calibrated defaults
            if 'const KILL = true' not in js:
                fail('kill gate must default ON (const KILL = true) in the generated harness')
            for c in ('KILL_FACTOR', 'KILL_BASE_MS', 'KILL_SLOPE_MS', 'KILL_FLOOR_MS', 'KILL_CEIL_MS'):
                if not _re.search(r'^const %s = [0-9.]+$' % c, js, _re.M):
                    fail('kill const %s missing/malformed in the generated harness' % c)
            # helper + BOTH call sites (resolveGroup main lane + healGroup fragment lane) use it
            n = js.count('agentKill(')
            if n < 3:
                fail('agentKill must appear 3x (definition + main-batch call + heal-group call); '
                     'got %d — a call site is unguarded' % n)
            if 'class KillTimeout' not in js or 'const isKill' not in js:
                fail('KillTimeout/isKill classifier must be present so a kill is distinguished '
                     'from a real hard failure')
            # the complexity signal (skeleton bytes) must be carried per card
            inputs = json.loads(_re.search(r'^const INPUTS = (\{.*?\})\nconst PH', js, _re.S | _re.M).group(1))
            if 'skeleton' not in inputs[key] or 'senses' not in inputs[key]:
                fail('INPUTS must carry skeleton (kill-budget signal) + senses; got keys %r'
                     % sorted(inputs[key]))
            meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
            if not meta.get('kill') or not meta.get('kill_gate'):
                fail('meta must record the kill-gate provenance (kill + kill_gate)')
            # --no-kill disables it
            saved_kill = gh.KILL
            gh.KILL = False
            try:
                js2, _b2 = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            finally:
                gh.KILL = saved_kill
            if 'const KILL = false' not in js2:
                fail('--no-kill / KILL=False must render const KILL = false (disables the gate)')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_group_by_budget_count_cap():
    """H189: _group_by_budget's count_cap closes a group once it holds count_cap items
    regardless of summed size, so a run of many tiny (size-1) fragments can't pack an
    unbounded COUNT (== senses to emit) into one presplit-lane call. Default (no cap)
    keeps the size-only behavior every pre-H189 caller relied on."""
    import gen_opt_harness2 as gh
    items = [{'w': 1}] * 40
    sizer = lambda it: it['w']
    # size-only: 40 weight-1 items at budget 60 = 1 group (nothing caps count)
    if len(gh._group_by_budget(items, sizer, 60)) != 1:
        fail('size-only grouping of 40 size-1 items at budget 60 must be a single group')
    # count_cap=18: 40 -> ceil(40/18) = 3 groups even though total size (40) < budget (60)
    capped = gh._group_by_budget(items, sizer, 60, count_cap=18)
    if len(capped) != 3 or any(len(g) > 18 for g in capped):
        fail('count_cap=18 must yield 3 groups of <=18 for 40 items; got sizes %r'
             % [len(g) for g in capped])


def test_presplit_card_uses_amortized_grouping():
    """H189 core fix: a card routed to the presplit-PRIMARY lane is grouped at
    PRESPLIT_GROUP_CITE_BUDGET/PRESPLIT_GROUP_SENSE_CAP (amortizing the ~27k framework
    across many fragments per call), NOT the conservative SELFHEAL_GROUP_BUDGET. A
    30-sense/1-<ls> card must group by the sense cap (ceil(30/18)=2), not by the old
    per-12-citation budget (ceil(30/12)=3) — proving fewer, larger fragment-lane calls."""
    import re as _re
    import gen_opt_harness2 as gh
    senses = '\n'.join('<div n="1">— %d〉 {%%Bedeutung %d%%}.' % (i, i)
                       for i in range(1, 31))
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n' + senses + '\n')
    key = 'zz~~synthetic_amortize'
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
            frags = json.loads(_re.search(r'^const FRAGS = (\{.*?\})\nconst PHF', js, _re.S | _re.M).group(1))
            groups = frags.get(key) or []
            if not (1 < len(groups) <= 2):
                fail('a 30-sense presplit card must group into 2 amortized fragment calls '
                     '(sense cap 18), not the old ~3 at budget 12; got %d groups' % len(groups))
            if any(len(g) > gh.PRESPLIT_GROUP_SENSE_CAP for g in groups):
                fail('no presplit group may exceed PRESPLIT_GROUP_SENSE_CAP fragments')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_kill_gate_recalibrated_envelope():
    """H189 (MG: '>~60s per subcard suspicious; >3 min unacceptable'): the kill envelope
    must be the tightened one — floor <= 45s, ceil <= 180s (3 min) — never a regression
    back to the 2 min floor / 8 min ceiling that let pril10_w1 fragments run 6.5 min."""
    import gen_opt_harness2 as gh
    if gh.KILL_FLOOR_MS > 45000:
        fail('KILL_FLOOR_MS must be <= 45000 (was 120000) so a tiny subcard is killed '
             'near MG\'s ~60s suspicion line; got %d' % gh.KILL_FLOOR_MS)
    if gh.KILL_CEIL_MS > 180000:
        fail('KILL_CEIL_MS must be <= 180000 (3 min hard ceiling, was 480000); got %d'
             % gh.KILL_CEIL_MS)


def test_budget_kill_switch_wired():
    """H189: the harness must carry a window-level budget kill-switch — count agent()
    calls and abort (requeue remaining) once past MAX_AGENTS — so a runaway retry/binary-
    split cascade self-terminates instead of running to a manual kill (pril10_w1: 230
    agents, 42M tokens, $80 before MG stopped it). MAX_AGENTS is derived from the preflight
    estimate: max(floor, ceil(expected * factor))."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_switch'
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
            for tok in ('const KILL_SWITCH = true', 'const MAX_AGENTS =',
                        'class BudgetExceeded', 'AGENTS_SPENT++', 'BUDGET_TRIPPED'):
                if tok not in js:
                    fail('budget kill-switch token %r missing from the harness' % tok)
            # BudgetExceeded must NOT be treated as a kill (a kill routes to MORE fragment
            # calls — the opposite of a budget stop).
            if _re.search(r'isKill\s*=.*BudgetExceeded', js):
                fail('BudgetExceeded must not be classified as a kill (would spawn more agents)')
            meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
            expected = meta.get('agent_expected_after_tm', 0)
            # H189 follow-up: the ceiling SCALES with word size (ceil(expected*factor)+headroom),
            # NOT a flat floor — a flat floor let a small-word runaway burn 40 agents unchecked.
            want = int(math.ceil(expected * gh.MAX_AGENTS_FACTOR)) + gh.MAX_AGENTS_HEADROOM
            if meta.get('max_agents') != want:
                fail('meta.max_agents must be ceil(expected*factor)+headroom=%d; got %r'
                     % (want, meta.get('max_agents')))
            if hasattr(gh, 'MAX_AGENTS_FLOOR'):
                fail('the flat one-size-fits-all MAX_AGENTS_FLOOR must be gone — the ceiling '
                     'must scale with word size so a small-word runaway is caught, not clamped to 40')
            # summary must expose the trip flag for the requeue path
            if 'budget_kill_switch_tripped' not in js:
                fail('run summary must expose budget_kill_switch_tripped so a self-aborted '
                     'window\'s null cards are requeued, not read as defective')
        finally:
            gh.input_paths = saved_ip
    finally:
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


def test_perf_preflight_cost_gate():
    """H189: the preflight cost gate must FLAG a window whose estimated $ per translated
    card exceeds the ceiling (a window of kAla-class monsters — exactly pril10_w1) and must
    PASS a cheap high-card-count window (e.g. `as`: many cards, low per-card cost). The
    per-card ratio is the load-bearing, model-independent signal."""
    import perf_preflight as pp
    # pril10_w1-shape: 8 cards, ~69 fragment-group agents (post-fix) -> ~$4/card >> ceiling
    monster = {'agent_expected_after_tm': 69, 'selected_keys': ['k%d' % i for i in range(8)],
               'tm_cards': 0, 'degenerate_passthrough_keys': []}
    cg = pp.cost_estimate(monster)
    if not cg['over_ceiling'] or cg['est_cost_per_card_usd'] <= cg['per_card_ceiling_usd']:
        fail('a window of 8 monster cards costing ~$4/card must trip the cost gate; got %r' % cg)
    # cheap high-count window: 98 cards, 24 agents -> pennies/card -> passes
    cheap = {'agent_expected_after_tm': 24, 'selected_keys': ['k%d' % i for i in range(98)],
             'tm_cards': 0, 'degenerate_passthrough_keys': []}
    if pp.cost_estimate(cheap)['over_ceiling']:
        fail('a large but cheap-per-card window must NOT trip the cost gate')
    # fully cached window: 0 agents -> $0 -> never gated
    cached = {'agent_expected_after_tm': 0, 'selected_keys': ['k1'], 'tm_cards': 1,
              'degenerate_passthrough_keys': []}
    if pp.cost_estimate(cached)['over_ceiling']:
        fail('a fully-cached (zero-agent) window must never trip the cost gate')


def main():
    tests = [
        test_translation_memory_addressing,
        test_tm_pre_resolves_cards,
        test_tm_card_sane_rejects_zero_marker_drift,
        test_generated_harness_strict_key_matching,
        test_tm_auto_no_sidecar_metadata,
        test_suggest_tm_does_not_skip_agents,
        test_tm_publication_fixtures_validate,
        test_degenerate_passthrough_accounted,
        test_degenerate_passthrough_rejects_glosses,
        test_perf_preflight_small_tm_and_no_tm,
        test_perf_preflight_dense_presplit,
        test_perf_preflight_presplit_counts_fragments_not_one,
        test_perf_preflight_degenerate_zero_agent,
        test_perf_preflight_multi_root_matrix_and_order,
        test_perf_preflight_fragment_tm_empty_warning,
        test_perf_preflight_partitions_mixed_monster_window,
        test_verb_worklist_excludes_missing_rootmaps,
        test_coordinator_state_dashboard_and_cap,
        test_coordinator_lock_replaces_stale_dead_owner,
        test_coordinator_defect_requeue_uses_no_tm_and_out,
        test_promote_nominal_key1,
        test_build_emits_nominal_keymap,
        test_no_pwg_supplement_chain_cards_render,
        test_nominals_worklist_exposes_no_pwg_lane,
        test_no_pwg_source_profile_promotes,
        test_calibration_arm_set_conservative_emit_only,
        test_frag_tm_reuse,
        test_no_fallback_batch_isolation,
        test_cit_split_never_tears_open_span,
        test_cit_split_caps_single_line_monster_sense,
        test_selfheal_fragment_si_threaded_and_tags_normalized,
        test_sense_dense_card_presplit,
        test_kill_gate_wired,
        test_group_by_budget_count_cap,
        test_presplit_card_uses_amortized_grouping,
        test_kill_gate_recalibrated_envelope,
        test_budget_kill_switch_wired,
        test_harness_size_guard,
        test_perf_preflight_cost_gate,
        test_autosplit_topup_targets_and_reassembles,
        test_workflow_payload_nested,
        test_sense_dupe_batch_override,
        test_sense_dupe_cross_level_exempt,
        test_export_translation_dedup,
        test_requeue_transient_vs_defect_state,
        test_harness_scope_and_tools,
        test_stale_check_key_order_independent,
        test_nominal_provenance_without_rootmap,
        test_no_pwg_card_source_profile_taxonomy,
        test_no_pwg_supplement_card_renders_without_pwg,
        test_no_pwg_worklist_runnable_lane,
        test_no_pwg_layer_and_profile_survive_promotion,
        test_prompt_rule_audit_template,
        test_prompt_rule_audit_missing_blocks,
        test_semantic_risk_checker,
        test_braced_gloss_audit,
        test_german_residue_keeps_retained_markup,
        test_german_connective_fix,
        test_semantic_review_prioritizer,
        test_noisy_source_type_not_requeue,
        test_report_only_risks_never_requeue,
        test_attested_text_signal_redesign,
        test_nws_fp_suppressed,
        test_en_gate_strict_has_teeth,
        test_en_gate_dup_has_teeth,
        test_ru_gate_fails_loud_on_unparseable_child,
        test_pwg_mask_latin_cue_behind_ab_tag,
        test_markup_loss_soft_flag_ru,
        test_markup_loss_soft_flag_en,
        test_en_de_residue_french_guard,
        test_ru_coverage_denominator_not_silently_exempt,
        test_coverage_gate_multi_layer_and_presplit,
        test_en_residual_coverage_complete,
        test_en_split_triage_keeps_missing_input,
        test_whitney_homonym_safety,
        test_stale_refusal_preserves_requeue,
        test_fixture_audit_does_not_clobber_live_status,
        test_release_manifest_hash_validation,
        test_lang_parity_ledger_complete,
        test_lang_parity_hash_crlf_independent,
    ]
    for test in tests:
        test()
        print('PASS:', test.__name__)
    print('window selftest OK')


if __name__ == '__main__':
    main()
