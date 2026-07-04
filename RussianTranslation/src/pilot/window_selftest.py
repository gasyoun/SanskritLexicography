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
    run_first = matrix.get('recommended_order', {}).get('run_first', [])
    if 'vid' not in run_first or 'as' not in run_first:
        fail('low-agent roots should appear in recommended run order')


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


def main():
    tests = [
        test_translation_memory_addressing,
        test_tm_pre_resolves_cards,
        test_tm_auto_no_sidecar_metadata,
        test_degenerate_passthrough_accounted,
        test_degenerate_passthrough_rejects_glosses,
        test_perf_preflight_small_tm_and_no_tm,
        test_perf_preflight_dense_presplit,
        test_perf_preflight_degenerate_zero_agent,
        test_perf_preflight_multi_root_matrix_and_order,
        test_perf_preflight_fragment_tm_empty_warning,
        test_calibration_arm_set_conservative_emit_only,
        test_frag_tm_reuse,
        test_autosplit_topup_targets_and_reassembles,
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
        test_coverage_gate_multi_layer_and_presplit,
        test_en_residual_coverage_complete,
        test_en_split_triage_keeps_missing_input,
        test_whitney_homonym_safety,
        test_stale_refusal_preserves_requeue,
        test_fixture_audit_does_not_clobber_live_status,
        test_release_manifest_hash_validation,
        test_lang_parity_ledger_complete,
    ]
    for test in tests:
        test()
        print('PASS:', test.__name__)
    print('window selftest OK')


if __name__ == '__main__':
    main()
