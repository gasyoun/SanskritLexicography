#!/usr/bin/env python
"""Smoke tests for frequency-window architecture guardrails.

This script intentionally uses ignored runtime files and temporary directories
only. It does not require a fresh Max run.

  python src/pilot/window_selftest.py
"""
import hashlib
import json
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
from window_provenance import current_root_provenance
from prompt_rule_audit import (
    DEFAULT_TEMPLATE,
    audit_card_result,
    audit_cards,
    build_report,
    braced_gloss_risks,
    semantic_risks,
)
from fix_german_connectives import fix_text as fix_german_text


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
    current = current_root_provenance(meta.get('root'), meta.get('selected_keys'))
    if not current.get('ok'):
        fail('current root provenance unavailable: %s' % current.get('error'))
    if meta.get('rootmap_sha256') != current.get('rootmap_sha256'):
        fail('optimized harness rootmap hash does not match current rootmap')
    if meta.get('selected_keys') != current.get('selected_keys'):
        fail('optimized harness selected_keys do not match current rootmap selection')
    text = open(meta['path'], encoding='utf-8').read()
    agent_calls = text.count('agent(prompt, {')
    tool_guards = text.count('tools: []')
    if agent_calls != tool_guards or not tool_guards:
        fail('optimized harness tools guard mismatch: %d agent calls, %d guards' %
             (agent_calls, tool_guards))


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
                '{%upanis%}', '{%āgamya%}'):
        leftover = {r['id'] for r in braced_gloss_risks(ger, ger, '1')}
        if 'untranslated_braced_german_gloss' in leftover:
            fail('braced gloss audit wrongly flagged non-German literal: %s' % ger)
    # Side-by-side: German kept in {%...%} BESIDE its Russian rendering is required.
    side = braced_gloss_risks('{%herfallen über%}', 'нападать на ({%herfallen über%})', '1')
    if {r['id'] for r in side} & {'untranslated_braced_german_gloss'}:
        fail('braced gloss audit flagged required side-by-side German echo')


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


def test_release_manifest_hash_validation():
    with tempfile.TemporaryDirectory() as tmp:
        edition = os.path.join(tmp, 'edition_selftest')
        write_minimal_edition(edition)
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=0)
        with open(os.path.join(edition, 'reverse_index.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({'ru': 'дым', 'key1': 'dhUma'}, ensure_ascii=False) + '\n')
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=1)


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
    from window_common import rootmap_path, input_paths, sha256_file
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
            sha = sha256_file(input_paths(k)[0])
            entries['ru:%s' % sha] = {'card': {'key1': k, 'iast': None,
                'records': [{'h': None, 'senses': [{'tag': '1', 'german': 'g', 'russian': 'р',
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
    finally:
        try:
            os.remove(tmfile)
        except OSError:
            pass


def main():
    tests = [
        test_translation_memory_addressing,
        test_tm_pre_resolves_cards,
        test_workflow_payload_nested,
        test_sense_dupe_batch_override,
        test_sense_dupe_cross_level_exempt,
        test_export_translation_dedup,
        test_requeue_transient_vs_defect_state,
        test_harness_scope_and_tools,
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
        test_markup_loss_soft_flag_ru,
        test_markup_loss_soft_flag_en,
        test_ru_coverage_denominator_not_silently_exempt,
        test_whitney_homonym_safety,
        test_stale_refusal_preserves_requeue,
        test_release_manifest_hash_validation,
    ]
    for test in tests:
        test()
        print('PASS:', test.__name__)
    print('window selftest OK')


if __name__ == '__main__':
    main()
