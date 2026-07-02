#!/usr/bin/env python
"""Deterministic audit for prompt/manual-rule wiring and cheap semantic risks.

No model calls are made. The prompt-rule audit checks whether the live template
and generated optimized harness still carry the manual-derived translation and
judge rules. The semantic-risk helpers are intentionally heuristic and cheap:
they flag likely review targets, not final editorial verdicts.

  python src/pilot/prompt_rule_audit.py
  python src/pilot/prompt_rule_audit.py --fail-on-missing
  python src/pilot/prompt_rule_audit.py --cards wf_output.json
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
OUT = os.path.join(HERE, 'output')

DEFAULT_TEMPLATE = os.path.join(HERE, 'run_pilot_wf.js')
# The missing-required-rule check is the BUILD-TIME contract on the canonical template;
# it must not point at a generated harness. The masked opt2 harness legitimately omits the
# SOFT judge-7 guidance rules (samasa/correlatives/sastric-formula/anti-circular), so rule-
# checking it would hard-fail the prompt_semantic gate on every root (false positive).
DEFAULT_HARNESS = os.path.join(HERE, 'run_pilot_wf.opt.js')

if HERE not in sys.path:
    sys.path.insert(0, HERE)

from workflow_payload import workflow_payload

GERMAN_RESIDUE = re.compile(
    r'\b(?:der|die|das|den|dem|des|und|oder|mit|ohne|von|für|nicht|eine|einer|'
    r'eines|einem|einen|auch|wohl|vielleicht|beim|bezeichnet|bedeutung|'
    r'gewässer|wasser|gabe|geschenk|schulter|strahl|sonne)\b',
    re.I)
CYR_WORD = re.compile(r'[А-Яа-яЁё]{2,}')
TAG_TOKEN = re.compile(r'</?(?:ls|ab|lex|is)\b[^>]*>', re.I)
BROKEN_TAG_TOKEN = re.compile(r'<(?:ls|ab|lex|is)\b[^>]*(?:$|<)', re.I)
TRANSLATED_GRAMMAR_SIGLUM = re.compile(
    r'\b(?:мужской|женский|средний|множественное|двойственное|единственное)\b',
    re.I)
TRANSLATED_SOURCE_SIGLUM = re.compile(
    r'\b(?:ригвед|атхарвавед|махабхарат|рамаян|ману)\w*',
    re.I)
BRACED_GLOSS = re.compile(r'\{%(.*?)%\}', re.S)
LATIN_FLAG_CONTEXT = re.compile(
    r'(?:das\s+lat\.|lat\.|latin|latein|griech\.|greek|engl\.|english|Wils\.\s+übersetzt)',
    re.I)
LATIN_BINOMIAL = re.compile(r'^[A-Z][a-z]+(?:\s+[a-z][a-z.-]+){1,2}$')
ENGLISH_GLOSS_WORDS = re.compile(
    r'\b(?:leaving|abandoning|water|fire|sun|moon|king|sacrifice|rice|wind|'
    r'knowledge|law|right|wrong|place|time|body|mind)\b',
    re.I)
GERMAN_GLOSS_WORDS = re.compile(
    r'\b(?:der|die|das|den|dem|des|und|oder|mit|ohne|von|für|nicht|eine|einer|'
    r'eines|einem|einen|auch|wohl|vielleicht|beim|Name|Art|Theil|Teil|'
    r'Bedeutung|Schulter|Strahl|Sonne|Wasser|Gewässer|Gabe|Geschenk|Glanz|'
    r'Schimmer|Pracht|Feuer|Brand|Schein|Ort|Zeit|Grund|Handeln|Zeug|'
    r'Pflanze|Gefäss|Gefäß|Handhaben|Henkeln|Schulden)\b',
    re.I)
TEXT_CITATION = re.compile(
    r'(?:<ls\b|ṚV|RV|Atharv|AV\.|MBH|Mahābh|Rām|R\.|M\.|BhP|ŚBr|TS\.|VS\.|'
    r'Kāty|Pañcat|Hit\.|Suśr|Car\.|Manu|Yājñ)',
    re.I)
# NWS (Nachtragswörterbuch) owner citation: [NWS: OWNER] pattern produced by the
# NWS layer cards. These citations appear in equivalence_type (a field skipped by
# citation_blob), so we scan all sense values for them separately in has_text_signal.
NWS_OWNER_CITATION = re.compile(r'\[NWS:\s')
LEXICOGRAPHIC_CITATION = re.compile(
    r'(?:Amarakośa|Amara|AK\b|Hemacandra|H\.\b|Pāṇini|P\.\b|Medinī|Med\.|'
    r'kośa|lexicographic)',
    re.I)

# Latin and Romance glosses B&R deliberately leave untranslated (esp. indelicate
# euphemisms written in Latin, e.g. "inire feminam"). These must NOT be flagged as
# untranslated German — the convention keeps them verbatim.
LATIN_WORDS = re.compile(
    r'\b(?:inire|feminam?|legere|inveteratus|convenire|coitus|coire|coeundi|'
    r'membrum|virile|penis|pudenda|futuere|mingere|venus|venere|in\s+coitu|'
    r'cum|quasi|scilicet|sic|idem|vide)\b', re.I)
FRENCH_WORDS = re.compile(
    r"(?:\bl['’]|\b(?:une?|les?|des|du|aux?|plus|tr[eè]s|homme|femme|basse|"
    r"extraction|chose|terre|qui|dans|pour|avec|sans)\b)", re.I)
# Sanskrit preverbs / transliterated tokens that appear braced on messy layer cards
# (e.g. SCH) and are not German glosses.
SANSKRIT_PREVERBS = {
    'abhi', 'adhi', 'anu', 'antar', 'apa', 'api', 'ava', 'ati', 'ud', 'upa',
    'ni', 'nis', 'nir', 'pari', 'pra', 'prati', 'vi', 'sam', 'su', 'parā',
    'abhyud', 'abhyudgata', 'upanis', 'samud', 'samupa', 'āgamya',
}
IAST_DIACRITIC = re.compile(r'[āīūṛṝḷḹṅñṭḍṇśṣ]')
# Markup spans the side-by-side convention REQUIRES kept verbatim inside the Russian
# field: {%German%} kept beside the Russian, {#Sanskrit#}, and <ab>/<ls>/<is> tags.
RETAINED_SPAN = re.compile(r'\{%.*?%\}|\{#.*?#\}|<(?:ab|ls|is)\b[^>]*>.*?</(?:ab|ls|is)>'
                           r'|<(?:ab|ls|is)\b[^>]*>', re.S | re.I)

SENSE_REQUIRED = (
    'tag', 'german', 'russian', 'equivalence_type', 'source_type', 'stratum',
    'differentia',
)

HIGH_RISKS = {
    'empty_russian',
    'missing_required_sense_field',
    'likely_circular_gloss',
    'untranslated_german_residue',
    'missing_source_type',
    'bad_card_shape',
    'missing_senses',
    'broken_markup_token',
    'unbalanced_sanskrit_delimiters',
    'translated_grammar_siglum',
    'translated_source_siglum',
    'untranslated_braced_german_gloss',
    'foreign_gloss_translated',
}

MEDIUM_RISKS = {
    'collapsed_synonym_string',
    'identical_russian_glosses',
    'missing_apresjan_discrimination',
    'formula_iti_arthah',
    'formula_iti_sesah',
    'suspicious_attested_without_text_signal',
    'suspicious_lexicographic_with_text_signal',
    'possible_sense_compression',
}

SEVERITY_WEIGHT = {'high': 100, 'medium': 10, 'low': 1}

HIGH_CONFIDENCE_RISKS = {
    'empty_russian',
    'broken_markup_token',
    'unbalanced_sanskrit_delimiters',
    'translated_grammar_siglum',
    'translated_source_siglum',
    'untranslated_german_residue',
    'untranslated_braced_german_gloss',
    'foreign_gloss_translated',
}

LIVE_MANUAL_COVERAGE = [
    'Apresjan',
    'Hartmann',
    'Gonda/Vogel',
    'Tubb',
    'Baalbaki',
    'Apte/Gillon/Inglese-Geupel',
    'Mitrenina/Zaliznyak-Paducheva/Ruppel',
]

METHODOLOGY_ONLY_MANUALS = [
    'Riemer',
    'Klosa',
]

FORMULA_RENDERINGS = [
    {
        'id': 'formula_iti_arthah',
        'patterns': ['iti arthaḥ', 'ity arthaḥ', 'iti arthaH', 'ity arthaH'],
        'renderings': ['то есть', 'таков смысл', 'это означает'],
    },
    {
        'id': 'formula_iti_sesah',
        'patterns': ['iti śeṣaḥ', 'ity śeṣaḥ', 'iti zezaH', 'ity zezaH'],
        'renderings': ['подразумевается', 'следует дополнить'],
    },
]

RULES = [
    {
        'id': 'apresjan_near_synonym',
        'category': 'Apresjan',
        'severity': 'required',
        'phrases': ['DISCRIMINATE', 'Apresjan', 'differentia'],
    },
    {
        'id': 'apresjan_manner_position',
        'category': 'Apresjan',
        'severity': 'required',
        'phrases': ['MANNER/POSITION', 'grammatical-but-false'],
    },
    {
        'id': 'apresjan_register',
        'category': 'Apresjan',
        'severity': 'required',
        'phrases': ['scholarly-philological', 'register'],
    },
    {
        'id': 'apresjan_anti_circular',
        'category': 'Apresjan',
        'severity': 'required',
        'phrases': ['non-circular', 'cryptographic'],
    },
    {
        'id': 'hartmann_equivalence_type',
        'category': 'Hartmann',
        'severity': 'required',
        'phrases': ['equivalence_type', 'explanatory'],
    },
    {
        'id': 'hartmann_punctuation_grouping',
        'category': 'Hartmann',
        'severity': 'required',
        'phrases': ['PUNCTUATION carries sense-grouping', 'semicolon'],
    },
    {
        'id': 'gonda_vogel_two_source',
        'category': 'Gonda/Vogel',
        'severity': 'required',
        'phrases': ['TWO-SOURCE PRINCIPLE', 'source_type=lexicographic'],
    },
    {
        'id': 'tubb_sastric_formulas',
        'category': 'Tubb',
        'severity': 'required',
        'phrases': ['ŚĀSTRIC FORMULAS', 'iti arthaḥ'],
    },
    {
        'id': 'baalbaki_synonym_cardinality',
        'category': 'Baalbaki/Apresjan',
        'severity': 'required',
        'phrases': ['SYNONYM CARDINALITY', 'EQUAL cardinality'],
    },
    {
        'id': 'compound_samasa',
        'category': 'Apte/Gillon/Inglese-Geupel',
        'severity': 'required',
        'phrases': ['COMPOUNDS (samāsa)', 'right-headed', 'bahuvrīhi', 'ādi'],
    },
    {
        'id': 'correlatives_yad_tad',
        'category': 'Mitrenina/Zaliznyak-Paducheva/Ruppel',
        'severity': 'required',
        'phrases': ['CORRELATIVES', 'yad…tad', 'кто…тот'],
    },
]


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from all_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_strings(child)


def iter_senses(card_like):
    if isinstance(card_like, dict) and isinstance(card_like.get('card'), dict):
        card_like = card_like['card']
    if not isinstance(card_like, dict):
        return
    for record in card_like.get('records') or []:
        for sense in record.get('senses') or []:
            if isinstance(sense, dict):
                yield sense


def corpus_candidate_count(card_like):
    counts = []
    for node in walk_dicts(card_like):
        corpus = node.get('corpus_synonyms')
        if isinstance(corpus, dict):
            candidates = corpus.get('candidates') or []
            counts.append(len(candidates))
        candidates = node.get('candidates')
        if isinstance(candidates, list) and node.get('by_stratum') is not None:
            counts.append(len(candidates))
    return max(counts or [0])


def walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def likely_circular(key1, iast, russian):
    low = (russian or '').lower()
    latin = re.findall(r'[A-Za-zĀ-ỿā-ỿ]{3,}', low)
    for token in (key1 or '', iast or ''):
        if token and len(token) >= 3 and token.lower() in latin:
            return True
    words = [w.lower() for w in CYR_WORD.findall(russian or '')]
    return len(words) >= 2 and len(set(words)) == 1


def add_risk(risks, risk_id, detail, tag=None, key=None):
    row = {'id': risk_id, 'level': risk_level(risk_id), 'detail': detail}
    row['high_confidence'] = risk_id in HIGH_CONFIDENCE_RISKS
    if tag is not None:
        row['tag'] = tag
    if key is not None:
        row['key'] = key
    risks.append(row)


def risk_level(risk_id):
    if risk_id in HIGH_RISKS:
        return 'high'
    if risk_id in MEDIUM_RISKS:
        return 'medium'
    return 'low'


def risk_score(risks):
    return sum(SEVERITY_WEIGHT.get(risk.get('level') or risk_level(risk.get('id')), 1)
               for risk in risks)


def norm_text(value):
    return ' '.join((value or '').lower().split())


def citation_blob(sense):
    skip = {'russian', 'equivalence_type', 'source_type', 'differentia', 'tag', 'stratum'}

    def values(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for key, child in value.items():
                if key not in skip:
                    yield from values(child)
        elif isinstance(value, list):
            for child in value:
                yield from values(child)

    return ' '.join(values(sense))


def has_text_signal(sense):
    blob = citation_blob(sense)
    if TEXT_CITATION.search(blob) or (sense.get('stratum') or '').strip():
        return True
    # NWS owner citations (e.g. [NWS: Graßmann 1873 (1996) : 168]) land in
    # equivalence_type which citation_blob skips.  Scan all string values.
    all_vals = ' '.join(v for v in sense.values() if isinstance(v, str))
    return bool(NWS_OWNER_CITATION.search(all_vals))


def has_lexicographic_signal(sense):
    return bool(LEXICOGRAPHIC_CITATION.search(citation_blob(sense)))


def formula_missing(german, russian):
    joined = norm_text(german)
    ru = norm_text(russian)
    missing = []
    for formula in FORMULA_RENDERINGS:
        if any(pattern.lower() in joined for pattern in formula['patterns']):
            if not any(rendering in ru for rendering in formula['renderings']):
                missing.append(formula['id'])
    return missing


def formula_hits(german):
    joined = norm_text(german)
    hits = []
    for formula in FORMULA_RENDERINGS:
        if any(pattern.lower() in joined for pattern in formula['patterns']):
            hits.append(formula['id'])
    return hits


def braced_glosses(text):
    return [m.group(1).strip() for m in BRACED_GLOSS.finditer(text or '')]


def gloss_context(text, index):
    matches = list(BRACED_GLOSS.finditer(text or ''))
    if index >= len(matches):
        return ''
    start = max(0, matches[index].start() - 80)
    return (text or '')[start:matches[index].start()]


def is_sanskrit_token(value):
    """A braced gloss that is a Sanskrit preverb / transliterated token, not German."""
    v = (value or '').strip().strip('˚°').lower()
    if not v or ' ' in v or ',' in v:
        return False
    if v in SANSKRIT_PREVERBS:
        return True
    return bool(IAST_DIACRITIC.search(v))


def looks_foreign_literal(gloss, context):
    value = (gloss or '').strip()
    if not value:
        return False
    if LATIN_FLAG_CONTEXT.search(context or ''):
        return True
    if LATIN_BINOMIAL.match(value):
        return True
    if LATIN_WORDS.search(value) and not GERMAN_GLOSS_WORDS.search(value):
        return True
    if FRENCH_WORDS.search(value) and not GERMAN_GLOSS_WORDS.search(value):
        return True
    if ENGLISH_GLOSS_WORDS.search(value) and not GERMAN_GLOSS_WORDS.search(value):
        return True
    return False


def looks_german_gloss(gloss, context):
    value = (gloss or '').strip()
    if not value or looks_foreign_literal(value, context):
        return False
    if is_sanskrit_token(value):
        return False
    if GERMAN_GLOSS_WORDS.search(value):
        return True
    return bool(re.search(r'[A-Za-zÄÖÜäöüß]{3,}', value) and not CYR_WORD.search(value))


def braced_gloss_risks(german, russian, tag):
    risks = []
    src = braced_glosses(german)
    dst = braced_glosses(russian)
    russian_norm = norm_text(russian)
    for i, gloss in enumerate(src):
        context = gloss_context(german, i)
        rendered = dst[i].strip() if i < len(dst) else ''
        if looks_foreign_literal(gloss, context):
            if rendered and norm_text(rendered) != norm_text(gloss):
                add_risk(risks, 'foreign_gloss_translated',
                         'literal non-German gloss changed: {%s} -> {%s}' %
                         (gloss[:80], rendered[:80]), tag=tag)
        elif looks_german_gloss(gloss, context):
            gloss_norm = norm_text(gloss)
            # Side-by-side convention: the German is kept verbatim in {%...%} in the
            # Russian field BESIDE its Russian rendering (e.g. "нападать на
            # ({%herfallen über%})"). That retained echo is required, not a leak —
            # but only when an actual Russian rendering sits next to it. A bare
            # {%German%} echo with no adjacent Cyrillic is a genuine miss.
            m = re.search(r'\{%\s*' + re.escape(gloss.strip()) + r'\s*%\}', russian)
            side_by_side = False
            if m:
                window = russian[max(0, m.start() - 40):m.end() + 40]
                side_by_side = CYR_WORD.search(window) is not None
            leaked = bool(gloss_norm and gloss_norm in russian_norm) and not side_by_side
            rendered_echo = bool(rendered and norm_text(rendered) == gloss_norm) and not side_by_side
            if rendered_echo or leaked:
                add_risk(risks, 'untranslated_braced_german_gloss',
                         'German braced gloss appears untranslated: {%s}' %
                         gloss[:100], tag=tag)
    return risks


def markup_sigla_risks(sense, russian, german, grammar, tag):
    risks = []
    if BROKEN_TAG_TOKEN.search(russian):
        add_risk(risks, 'broken_markup_token',
                 'Russian field contains a malformed markup token', tag=tag)
    if russian.count('{#') != russian.count('#}'):
        add_risk(risks, 'unbalanced_sanskrit_delimiters',
                 'Russian field has unbalanced {#...#} delimiters', tag=tag)
    if grammar and re.search(r'\b(?:m|f|n|Pl|Du|Sg)\.', grammar) and TRANSLATED_GRAMMAR_SIGLUM.search(russian):
        add_risk(risks, 'translated_grammar_siglum',
                 'grammar abbreviation appears translated rather than kept verbatim', tag=tag)
    if TEXT_CITATION.search(german) and TRANSLATED_SOURCE_SIGLUM.search(russian):
        add_risk(risks, 'translated_source_siglum',
                 'source siglum appears translated in the Russian field', tag=tag)
    if TAG_TOKEN.search(russian) and russian.count('<') != russian.count('>'):
        add_risk(risks, 'broken_markup_token',
                 'Russian field has unbalanced angle brackets around markup', tag=tag)
    # markup-loss (pwg_ru/DharmaMitra crosswalk, FU1_PLAN.md): the {%..%} gloss-wrapper pair
    # itself gets dropped while the underlying prose is still translated correctly — distinct
    # from untranslated_braced_german_gloss above (which fires when the wrapper survives but
    # its content wasn't rendered). Soft/low severity: meaning is intact, only the wrapper is
    # gone, so it never blocks the gate.
    sgloss, dgloss = len(BRACED_GLOSS.findall(german or '')), len(BRACED_GLOSS.findall(russian or ''))
    if sgloss > 0 and dgloss < sgloss:
        add_risk(risks, 'markup_wrapper_dropped',
                 'braced gloss wrapper {%%..%%} dropped: %d source vs %d target' % (sgloss, dgloss),
                 tag=tag)
    return risks


def semantic_risks(card_like):
    """Return cheap deterministic semantic-risk findings for a translated card."""
    card = card_like.get('card') if isinstance(card_like, dict) and isinstance(card_like.get('card'), dict) else card_like
    if not isinstance(card, dict):
        return [{'id': 'bad_card_shape', 'level': risk_level('bad_card_shape'),
                 'detail': 'card is not an object'}]
    key1 = card.get('key1') or ''
    iast = card.get('iast') or key1
    risks = []
    senses = list(iter_senses(card))
    if not senses:
        add_risk(risks, 'missing_senses', 'no translated senses found')
        return risks
    multi_candidate = corpus_candidate_count(card_like) > 1
    has_differentia = False
    russian_values = []
    # Card-level text-signal: if any ATTESTED sense in the card has a text
    # citation or NWS owner citation, individual PW senses that list a verb
    # meaning without an inline <ls> are false positives for
    # suspicious_attested_without_text_signal (e.g. _zz_pw* cards where the
    # head sense proves attestation but numbered senses carry no inline cite).
    all_card_senses = [s for rec in (card.get('records') or [])
                       for s in (rec.get('senses') or []) if isinstance(s, dict)]
    card_has_text_signal = any(
        s.get('source_type') == 'attested' and has_text_signal(s)
        for s in all_card_senses
    )
    for record in card.get('records') or []:
        grammar = record.get('grammar') or ''
        rec_senses = [sense for sense in record.get('senses') or [] if isinstance(sense, dict)]
        if len(rec_senses) <= 1:
            german_blob = ' '.join((sense.get('german') or '') for sense in rec_senses)
            if ';' in german_blob or re.search(r'(?:^|\s)\d+[.)]', german_blob):
                add_risk(risks, 'possible_sense_compression',
                         'German sense separators/numbering appear inside a single output sense')
        for sense in rec_senses:
            tag = sense.get('tag') or '?'
            german = sense.get('german') or ''
            russian = sense.get('russian') or ''
            russian_clean = russian.strip()
            russian_values.append(russian_clean)
            differentia = (sense.get('differentia') or '').strip()
            if differentia:
                has_differentia = True
            for field in SENSE_REQUIRED:
                if field not in sense:
                    add_risk(risks, 'missing_required_sense_field',
                             'sense lacks required field %s' % field, tag=tag)
            if not russian_clean:
                add_risk(risks, 'empty_russian', 'sense has empty russian gloss', tag=tag)
            if not sense.get('equivalence_type'):
                add_risk(risks, 'missing_equivalence_type',
                         'sense lacks equivalence_type', tag=tag)
            if not sense.get('source_type'):
                add_risk(risks, 'missing_source_type',
                         'sense lacks source_type', tag=tag)
            # Strip the markup spans the convention keeps verbatim ({%German%}
            # side-by-side, {#Sanskrit#}, <ab>/<ls>/<is>) before hunting German
            # residue, so retained-by-design German is not mistaken for a leak.
            russian_outside = RETAINED_SPAN.sub(' ', russian)
            if GERMAN_RESIDUE.search(russian_outside):
                add_risk(risks, 'untranslated_german_residue',
                         russian[:120], tag=tag)
            if ',' in german and ',' not in russian:
                add_risk(risks, 'collapsed_synonym_string',
                         'German comma-separated synonym string has no Russian comma', tag=tag)
            if likely_circular(key1, iast, russian):
                add_risk(risks, 'likely_circular_gloss', russian[:120], tag=tag)
            for markup_risk in markup_sigla_risks(sense, russian, german, grammar, tag):
                risks.append(markup_risk)
            for gloss_risk in braced_gloss_risks(german, russian, tag):
                risks.append(gloss_risk)
            for formula_id in formula_missing(german, russian):
                add_risk(risks, formula_id,
                         'fixed śāstric formula appears without expected Russian rendering',
                         tag=tag)
            source_type = sense.get('source_type')
            if source_type == 'attested' and not has_text_signal(sense) and not card_has_text_signal:
                add_risk(risks, 'suspicious_attested_without_text_signal',
                         'source_type=attested but no text citation or stratum signal found',
                         tag=tag)
            if source_type == 'lexicographic' and has_text_signal(sense) and not has_lexicographic_signal(sense):
                add_risk(risks, 'suspicious_lexicographic_with_text_signal',
                         'source_type=lexicographic but only text/stratum evidence is visible',
                         tag=tag)
    unique_russian = {value for value in russian_values if value}
    if len(russian_values) > 1 and len(unique_russian) == 1:
        add_risk(risks, 'identical_russian_glosses',
                 'all senses have the same Russian gloss')
    if multi_candidate and not has_differentia:
        add_risk(risks, 'missing_apresjan_discrimination',
                 'multiple corpus candidates present but all differentia fields are empty')
    return risks


def audit_card_result(result, index=0):
    key = result.get('key') if isinstance(result, dict) else None
    card = result.get('card') if isinstance(result, dict) else None
    if isinstance(card, dict):
        key = key or card.get('key1')
    risks = semantic_risks(result)
    for risk in risks:
        risk.setdefault('key', key or 'result[%d]' % index)
        risk.setdefault('level', risk_level(risk.get('id')))
    levels = {'high': 0, 'medium': 0, 'low': 0}
    high_confidence_count = 0
    for risk in risks:
        levels[risk.get('level') or 'low'] = levels.get(risk.get('level') or 'low', 0) + 1
        if risk.get('high_confidence'):
            high_confidence_count += 1
    return {
        'key': key or 'result[%d]' % index,
        'risk_count': len(risks),
        'risk_score': risk_score(risks),
        'high_count': levels.get('high', 0),
        'medium_count': levels.get('medium', 0),
        'low_count': levels.get('low', 0),
        'high_confidence_count': high_confidence_count,
        'risks': risks,
    }


def formula_inventory(results):
    inventory = {
        formula['id']: {'id': formula['id'], 'occurrences': 0, 'missing_rendering': 0}
        for formula in FORMULA_RENDERINGS
    }
    for result in results:
        card = result.get('card') if isinstance(result, dict) else None
        if not isinstance(card, dict):
            continue
        for sense in iter_senses(card):
            german = sense.get('german') or ''
            russian = sense.get('russian') or ''
            for formula_id in formula_hits(german):
                inventory[formula_id]['occurrences'] += 1
            for formula_id in formula_missing(german, russian):
                inventory[formula_id]['missing_rendering'] += 1
    return list(inventory.values())


def build_review_queue(cards, limit):
    ranked = sorted(
        (card for card in cards if card['risk_count']),
        key=lambda card: (-card['risk_score'], -card['high_count'],
                          -card['medium_count'], card['key']))
    return {
        'limit': limit,
        'total': len(ranked),
        'keys': [card['key'] for card in ranked[:limit]],
        'items': [{
            'key': card['key'],
            'risk_score': card['risk_score'],
            'high_count': card['high_count'],
            'medium_count': card['medium_count'],
            'low_count': card['low_count'],
            'high_confidence_count': card.get('high_confidence_count', 0),
            'top_risks': [risk['id'] for risk in card['risks'][:5]],
        } for card in ranked[:limit]],
    }


def audit_cards(path, review_limit=25):
    _payload, meta, results, keys, nulls = workflow_payload(path)
    cards = []
    for i, result in enumerate(results):
        cards.append(audit_card_result(result, i))
    risky = [card for card in cards if card['risk_count']]
    high_risk_count = sum(card['high_count'] for card in cards)
    high_confidence_count = sum(card.get('high_confidence_count', 0) for card in cards)
    high_confidence_keys = sorted(
        card['key'] for card in cards if card.get('high_confidence_count', 0))
    return {
        'path': os.path.abspath(path),
        'meta': meta,
        'result_count': len(results),
        'key_count': len(keys),
        'null_card_count': len(nulls),
        'risk_count': sum(card['risk_count'] for card in cards),
        'high_risk_count': high_risk_count,
        'high_confidence_count': high_confidence_count,
        'risky_key_count': len(risky),
        'risky_keys': [card['key'] for card in risky],
        'high_confidence_keys': high_confidence_keys,
        'requeue_keys': high_confidence_keys,
        'review_queue': build_review_queue(cards, review_limit),
        'formula_inventory': formula_inventory(results),
        'cards': cards,
    }


def audit_text(path):
    if not os.path.exists(path):
        return {'path': path, 'exists': False, 'rules': [], 'missing': []}
    text = read_text(path)
    rules = []
    missing = []
    for rule in RULES:
        absent = [phrase for phrase in rule['phrases'] if phrase not in text]
        status = 'pass' if not absent else 'missing'
        row = {k: rule[k] for k in ('id', 'category', 'severity')}
        row.update({'status': status, 'missing_phrases': absent})
        rules.append(row)
        if absent:
            missing.append(row)
    return {'path': path, 'exists': True, 'rules': rules, 'missing': missing}


def write_reports(report):
    os.makedirs(OUT, exist_ok=True)
    json_path = os.path.join(OUT, 'prompt_rule_audit.json')
    md_path = os.path.join(OUT, 'prompt_rule_audit.md')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    prompt = report.get('prompt_rules') or report
    card_risks = report.get('card_risks')
    lines = [
        '# Prompt Rule Audit',
        '',
        '| target | status | missing |',
        '|---|---|---:|',
    ]
    for target in prompt['targets']:
        status = 'missing-file' if not target['exists'] else ('fail' if target['missing'] else 'pass')
        lines.append('| `%s` | %s | %d |' % (
            os.path.relpath(target['path'], ROOT), status, len(target['missing'])))
    lines += [
        '',
        'Live manual coverage: %s.' % ', '.join(prompt.get('live_manual_coverage') or []),
        'Methodology/design only: %s.' % ', '.join(prompt.get('methodology_only_manuals') or []),
    ]
    lines += ['', '## Rules', '', '| target | category | rule | status | missing phrases |',
              '|---|---|---|---|---|']
    for target in prompt['targets']:
        rel = os.path.relpath(target['path'], ROOT)
        for rule in target['rules']:
            lines.append('| `%s` | %s | `%s` | %s | %s |' % (
                rel, rule['category'], rule['id'], rule['status'],
                ', '.join('`%s`' % p for p in rule['missing_phrases']) or ''))
    if card_risks:
        lines += [
            '',
            '## Card Risks',
            '',
            '| source | results | risky keys | risks | high risks | high-confidence |',
            '|---|---:|---:|---:|---:|---:|',
            '| `%s` | %d | %d | %d | %d | %d |' % (
                os.path.relpath(card_risks['path'], ROOT),
                card_risks['result_count'],
                card_risks['risky_key_count'],
                card_risks['risk_count'],
                card_risks.get('high_risk_count', 0),
                card_risks.get('high_confidence_count', 0)),
            '',
            '### Review Queue',
            '',
            '| rank | key | score | high-confidence | high | medium | low | top risks |',
            '|---:|---|---:|---:|---:|---:|---:|---|',
        ]
        for rank, item in enumerate((card_risks.get('review_queue') or {}).get('items') or [], 1):
            lines.append('| %d | `%s` | %d | %d | %d | %d | %d | %s |' % (
                rank, item['key'], item['risk_score'],
                item.get('high_confidence_count', 0), item['high_count'],
                item['medium_count'], item['low_count'],
                ', '.join('`%s`' % risk for risk in item['top_risks'])))
        lines += [
            '',
            '### Formula Inventory',
            '',
            '| formula | occurrences | missing rendering |',
            '|---|---:|---:|',
        ]
        for row in card_risks.get('formula_inventory') or []:
            lines.append('| `%s` | %d | %d |' % (
                row['id'], row['occurrences'], row['missing_rendering']))
        lines += [
            '',
            '### All Findings',
            '',
            '| key | risk | tag | detail |',
            '|---|---|---|---|',
        ]
        for card in card_risks['cards']:
            for risk in card['risks']:
                lines.append('| `%s` | `%s` | %s | %s |' % (
                    card['key'],
                    risk['id'],
                    risk.get('tag') or '',
                    (risk.get('detail') or '').replace('|', '/')))
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return json_path, md_path


def build_report(paths):
    targets = [audit_text(path) for path in paths]
    scanned = [target for target in targets if target['exists']]
    missing_rules = sum(len(target['missing']) for target in scanned)
    missing_files = [target['path'] for target in targets if not target['exists']]
    return {
        'rule_count': len(RULES),
        'target_count': len(targets),
        'scanned_target_count': len(scanned),
        'missing_rule_count': missing_rules,
        'missing_files': missing_files,
        'live_manual_coverage': LIVE_MANUAL_COVERAGE,
        'methodology_only_manuals': METHODOLOGY_ONLY_MANUALS,
        'targets': targets,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', default=DEFAULT_TEMPLATE,
                        help='committed workflow template to audit')
    parser.add_argument('--harness', default=DEFAULT_HARNESS,
                        help='generated optimized harness to audit when present')
    parser.add_argument('--cards',
                        help='workflow/card JSON file to scan for deterministic semantic risks')
    parser.add_argument('--review-limit', type=int, default=25,
                        help='number of ranked review-queue keys to print/report')
    parser.add_argument('--fail-on-missing', action='store_true',
                        help='exit non-zero when any scanned target is missing required phrases')
    parser.add_argument('--fail-on-risk', action='store_true',
                        help='exit non-zero when --cards finds any semantic risk')
    parser.add_argument('--fail-on-high-risk', action='store_true',
                        help='exit non-zero when --cards finds any high-confidence mechanical risk')
    args = parser.parse_args()
    paths = [os.path.abspath(args.template)]
    if args.harness:
        harness = os.path.abspath(args.harness)
        if os.path.exists(harness):
            paths.append(harness)
    prompt_report = build_report(paths)
    report = dict(prompt_report)
    report['prompt_rules'] = prompt_report
    if args.cards:
        report['card_risks'] = audit_cards(args.cards, max(args.review_limit, 0))
    json_path, md_path = write_reports(report)
    for target in prompt_report['targets']:
        status = 'MISSING FILE' if not target['exists'] else ('FAIL' if target['missing'] else 'PASS')
        print('%-12s %s' % (status, os.path.relpath(target['path'], ROOT)))
        for rule in target.get('missing') or []:
            print('  missing %-34s %s' % (
                rule['id'], ', '.join(rule['missing_phrases'])))
    if args.cards:
        risks = report['card_risks']
        status = 'PASS' if not risks['risk_count'] else 'RISK'
        print('%-12s %s (%d risks across %d keys)' % (
            status, os.path.relpath(risks['path'], ROOT),
            risks['risk_count'], risks['risky_key_count']))
        queue = risks.get('review_queue') or {}
        for item in queue.get('items') or []:
            print('  %-34s score=%d high=%d medium=%d risks=%s' % (
                item['key'], item['risk_score'], item['high_count'],
                item['medium_count'], ', '.join(item['top_risks'])))
    print('report json  : %s' % os.path.relpath(json_path, ROOT))
    print('report md    : %s' % os.path.relpath(md_path, ROOT))
    if args.fail_on_missing and prompt_report['missing_rule_count']:
        sys.exit(1)
    if args.fail_on_risk and args.cards and report['card_risks']['risk_count']:
        sys.exit(1)
    if args.fail_on_high_risk and args.cards and report['card_risks'].get('high_confidence_count', 0):
        sys.exit(1)


if __name__ == '__main__':
    main()
