#!/usr/bin/env python
"""Export the PWG->RU lexicon as a real Linked-Open-Data graph (E7 / H350).

This is the LOD upgrade of the flat one-way string export in
``export_interop.py``.  Where that emitter produced ``ontolex:LexicalEntry`` /
``ontolex:LexicalSense`` with a *placeholder* IRI namespace
(``https://example.org/pwg/ru/``), string-only ``ontolex:usage`` and no query
surface, this emitter adds the five things a real LOD graph needs:

  1. a real, dereferenceable, **configurable** IRI namespace (``--base-iri``;
     ships defaulting to a documented w3id PURL placeholder pending the
     publication-domain @DECIDE -- IRIs are forever, so the domain is a human
     ruling, not a guess baked into code);
  2. ``vartrans`` sense<->sense relations, fed from ``pwg_ru_relationships.jsonl``
     (restate / add / relocate / correct, abridging vs additive, per layer);
  3. PROV-O evidence grades on every sense (approved / human-reviewed /
     machine-preview / dict-attested / kow / corpus), so the citable subset is a
     SPARQL filter rather than a separate build;
  4. every per-sense ``<ls>`` citation as a first-class ``pwglex:Citation``
     (``prov:Entity``) resource linked ``dct:references`` from the sense;
  5. the Renou stratum per sense (from ``pwg_sense_stratum.jsonl``) as a dated
     ``pwglex:StratumAttestation``.

The SLP1 lemma (``key1``) is the spine: one shared ``ontolex:Form`` / ``lila:Lemma``
node per ``key1`` (a LiLa-style lemma bank), so every homograph entry and the
separate DCS-frequency graph join on the *same* lemma IRI.  DCS frequency is
emitted into a **separate** graph (``dcs_freq.ttl``, ``export_lod.py dcs-freq``)
keyed by that lemma IRI, so the acceptance query in ``lod_acceptance.py`` performs
a genuine cross-dataset (federated-shape) join.

  python export_lod.py lexicon --limit 200 --out-dir release/fixture
  python export_lod.py dcs-freq --out-dir release/fixture
  python export_lod.py all --out-dir release           # full graph (large)

Design notes and known modelling boundaries are in ``LOD_GRAPH.md``.  Ownership:
the *generator* and its input data stay in ``RussianTranslation``; the *published*
graph + SPARQL surface land in ``csl-standards`` per the 2026-06-03 boundary
rules (see ``ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`` G2).
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_CARDS = os.path.join(HERE, 'assembled_cards.jsonl')
DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DEFAULT_REL = os.path.join(HERE, 'pwg_ru_relationships.jsonl')
DEFAULT_STRATUM = os.path.join(HERE, 'pwg_sense_stratum.jsonl')
DEFAULT_FREQ = os.path.join(HERE, 'dcs_freq.json')
DEFAULT_RELEASE = os.path.join(ROOT, 'release')

# Placeholder publication domain. w3id.org is the community PURL redirector; the
# real registration/DNS target is an open @DECIDE (see LOD_GRAPH.md). Overridable
# with --base-iri so nothing downstream hard-codes a domain we do not yet own.
DEFAULT_BASE = 'https://w3id.org/sanskrit-lexicon/pwg-ru/'

APPROVED_STATUSES = {'approved', 'human_reviewed'}

# review_status / source -> evidence-grade skos concept slug (clean PN_LOCAL).
GRADE = {
    'approved': 'approved',
    'human_reviewed': 'human-reviewed',
    'ai_translated': 'machine-preview',
    'machine_gated': 'machine-preview',
    'machine_exact': 'machine-preview',
    'legacy_promoted': 'machine-preview',
}

LS_RE = re.compile(r'<ls\b([^>]*)>(.*?)</ls>|<ls\b([^>]*?)/>', re.DOTALL)
N_ATTR_RE = re.compile(r'\bn\s*=\s*"([^"]*)"')
# leading run of capitalised siglum tokens (Latin + IAST diacritic capitals + . -)
SIGLA_LEAD_RE = re.compile(r'^\s*([A-ZĀĪŪṚṜḶḸṄÑṆṬḌŚṢḤṂ][A-ZĀĪŪṚṜḶḸṄÑṆṬḌŚṢḤṂ.\- ]*?)(?=\d|$)')


# --------------------------------------------------------------------------- #
# IRI / Turtle helpers
# --------------------------------------------------------------------------- #
def iri_local(s):
    """Injective segment encoder: keep [A-Za-z0-9], escape everything else as
    ``_xHH_`` (hex of the UTF-8 bytes). Reversible enough that two distinct keys
    never collapse to the same IRI segment (the old ``safe_id`` merged them)."""
    out = []
    for ch in str(s if s is not None else 'x'):
        if ch.isascii() and ch.isalnum():
            out.append(ch)
        else:
            out.append(''.join('_x%02x_' % b for b in ch.encode('utf-8')))
    return ''.join(out) or 'x'


def esc(s):
    """Escape a Turtle string-literal body (for \"...\")."""
    return (str(s if s is not None else '')
            .replace('\\', '\\\\').replace('"', '\\"')
            .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))


def lit(s, lang=None, dtype=None):
    body = '"%s"' % esc(s)
    if lang:
        return body + '@' + lang
    if dtype:
        return body + '^^' + dtype
    return body


class IRI:
    """Mint absolute <base+path> IRIs for instance resources (path may contain
    '/', which is legal in an IRIREF but not in a Turtle prefixed name)."""
    def __init__(self, base):
        self.base = base

    def __call__(self, path):
        return '<%s%s>' % (self.base, path)


def extract_ls(text):
    """Yield (raw, sigla, locus) for every <ls> in a card/gloss text."""
    for m in LS_RE.finditer(text or ''):
        attrs = m.group(1) if m.group(1) is not None else (m.group(3) or '')
        content = re.sub(r'\s+', ' ', (m.group(2) or '')).strip()
        na = N_ATTR_RE.search(attrs or '')
        if na and na.group(1).strip():
            sigla = na.group(1).strip()
            locus = content
            raw = (sigla + ' ' + content).strip()
        else:
            lead = SIGLA_LEAD_RE.match(content)
            sigla = lead.group(1).strip() if lead else content
            locus = content[lead.end():].strip() if lead else ''
            raw = content
        yield raw, sigla, locus


def cite_slug(raw):
    return iri_local(re.sub(r'\s+', '-', (raw or '').strip()))[:160]


def iter_jsonl(path, limit=None):
    if not path or not os.path.exists(path):
        return
    n = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
            n += 1
            if limit and n >= limit:
                break


def iter_cards(args):
    """Cards honouring --keys (curated fixture set) or --limit (first N)."""
    keys = getattr(args, 'keyset', None)
    for card in iter_jsonl(args.cards, None if keys else args.limit):
        if keys is None or card.get('key1') in keys:
            yield card


# --------------------------------------------------------------------------- #
# Sidecar loaders
# --------------------------------------------------------------------------- #
def load_relationships(path):
    out = {}
    for r in iter_jsonl(path):
        out.setdefault(r.get('key1'), []).append(r)
    return out


def load_stratum(path):
    """key1 -> {sense_no(int) -> best stratum entry} (prefer the dated row)."""
    out = {}
    for r in iter_jsonl(path):
        d = out.setdefault(r.get('key1'), {})
        for s in r.get('senses') or []:
            no = s.get('sense_no')
            if no is None:
                continue
            prev = d.get(no)
            if prev is None or (s.get('n_dated_citations') or 0) > (prev.get('n_dated_citations') or 0):
                d[no] = s
    return out


def load_translations(path, limit_keys=None):
    out = {}
    for r in iter_jsonl(path):
        k = r.get('key1')
        if limit_keys is not None and k not in limit_keys:
            continue
        if r.get('ru'):
            out.setdefault(k, []).append(r)
    return out


def store_homonym(row):
    sub = row.get('subcard') or ''
    return sub.split('~~')[1].split('_')[0] if '~~' in sub else 'h?'


# --------------------------------------------------------------------------- #
# Prefix + header blocks
# --------------------------------------------------------------------------- #
def prefixes(base):
    return '\n'.join([
        '@prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
        '@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .',
        '@prefix owl:      <http://www.w3.org/2002/07/owl#> .',
        '@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .',
        '@prefix dct:      <http://purl.org/dc/terms/> .',
        '@prefix skos:     <http://www.w3.org/2004/02/skos/core#> .',
        '@prefix prov:     <http://www.w3.org/ns/prov#> .',
        '@prefix ontolex:  <http://www.w3.org/ns/lemon/ontolex#> .',
        '@prefix vartrans: <http://www.w3.org/ns/lemon/vartrans#> .',
        '@prefix lime:     <http://www.w3.org/ns/lemon/lime#> .',
        '@prefix lexinfo:  <http://www.lexinfo.net/ontology/3.0/lexinfo#> .',
        '@prefix lila:     <http://lila-erc.eu/ontologies/lila/> .',
        '@prefix pwglex:   <%svocab#> .' % base,
        '@prefix gr:       <%sgrade/> .' % base,
        '',
    ]) + '\n'


GRADES = [
    ('approved', 'human-approved (G5)', True),
    ('human-reviewed', 'human-reviewed (G5)', True),
    ('machine-preview', 'machine translation, not yet human-reviewed (non-citable)', False),
    ('dict-attested', 'attested in a modern Sanskrit-Russian dictionary', True),
    ('kow', 'Kossowich reference gloss', True),
    ('corpus', 'induced from the corpus alignment lexicon', False),
]


def emit_vocab_and_lexicon(f, R, args):
    f.write('# --- lexicon + provenance ------------------------------------\n')
    f.write('%s a lime:Lexicon ;\n' % R('lexicon/pwg-ru'))
    f.write('  rdfs:label "PWG->Russian lexicon (Petersburg Dictionary)"@en ;\n')
    f.write('  dct:language "sa" ;\n')
    f.write('  dct:source <https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/> ;\n')
    f.write('  lime:language "sa" ; lime:language "ru" ;\n')
    f.write('  dct:license <https://creativecommons.org/licenses/by-sa/4.0/> ;\n')
    f.write('  prov:wasGeneratedBy %s ;\n' % R('prov/export-lod'))
    f.write('  dct:created "%s"^^xsd:date .\n\n' % esc(args.generated_at))
    f.write('%s a prov:Activity ;\n' % R('prov/export-lod'))
    f.write('  rdfs:label "PWG->RU LOD export (export_lod.py)" ;\n')
    f.write('  prov:endedAtTime "%s"^^xsd:date .\n\n' % esc(args.generated_at))
    f.write('%s a skos:ConceptScheme ; rdfs:label "PWG->RU evidence grades" .\n' % R('grade/scheme'))
    for slug, label, citable in GRADES:
        f.write('gr:%s a skos:Concept ; skos:inScheme %s ; skos:prefLabel "%s"@en ; pwglex:citable %s .\n'
                % (slug, R('grade/scheme'), esc(label), 'true' if citable else 'false'))
    f.write('\n')


# --------------------------------------------------------------------------- #
# Per-card emission
# --------------------------------------------------------------------------- #
def card_carried_senses(card):
    """dict / kow / corpus senses carried by the assembled card."""
    out = []
    for i, d in enumerate((card.get('attested_senses', {}) or {}).get('dict') or [], 1):
        if d.get('gloss'):
            code = d.get('code') or d.get('source') or 'dict'
            out.append({'frag': 'dict/%s/%d' % (iri_local(code), i), 'gloss': d.get('gloss'),
                        'lang': 'ru', 'grade': 'dict-attested', 'src': code})
    for i, s in enumerate(card.get('kow_reference') or [], 1):
        out.append({'frag': 'kow/%d' % i, 'gloss': s, 'lang': 'ru', 'grade': 'kow', 'src': 'kow'})
    for st in (card.get('corpus_lexicon') or {}).get('strata') or []:
        for j, r in enumerate(st.get('renderings') or [], 1):
            if r.get('lemma'):
                out.append({'frag': 'corpus/%s/%d' % (iri_local(st.get('period') or 'x'), j),
                            'gloss': r.get('lemma'), 'lang': 'ru', 'grade': 'corpus',
                            'src': st.get('period') or 'corpus'})
    return out


def emit_card(f, R, card, eloc, lemma_seen, translations, stratum, rels, args, emitted_tr):
    key1 = card.get('key1')
    lemma_iri = R('lemma/%s' % iri_local(key1))
    entry_iri = R(eloc)

    if key1 not in lemma_seen:
        lemma_seen.add(key1)
        f.write('%s a ontolex:Form, lila:Lemma ;\n' % lemma_iri)
        f.write('  ontolex:writtenRep %s ;\n' % lit(key1, lang='sa-Latn-x-slp1'))
        if card.get('iast'):
            f.write('  ontolex:writtenRep %s ;\n' % lit(card.get('iast'), lang='sa-Latn'))
        f.write('  pwglex:slp1 %s ;\n' % lit(key1))
        f.write('  rdfs:label %s .\n' % lit(card.get('iast') or key1, lang='sa-Latn'))

    f.write('%s a ontolex:LexicalEntry ;\n' % entry_iri)
    f.write('  rdfs:label %s ;\n' % lit(card.get('iast') or key1, lang='sa-Latn'))
    f.write('  dct:isPartOf %s ;\n' % R('lexicon/pwg-ru'))
    f.write('  ontolex:canonicalForm %s ;\n' % lemma_iri)
    if card.get('key2') and card.get('key2') != key1:
        f.write('  pwglex:key2 %s ;\n' % lit(card.get('key2')))

    # 1) card-carried senses
    carried = card_carried_senses(card)
    carried_iris = [(R('sense/%s/%s' % (eloc, rec['frag'])), rec) for rec in carried]

    # 2) translation store senses -- attach ONCE per key1 (homograph discipline:
    #    the assembled side carries no homonym key, so all store rows for a key1
    #    hang under its first entry, exactly as export_interop.py does).
    tr_rows = []
    if key1 not in emitted_tr:
        emitted_tr.add(key1)
        tr_rows = translations.get(key1, [])
    key_rels = rels.get(key1, [])
    key_strat = stratum.get(key1, {})

    tr_iris = []
    cite_blocks = {}
    attest_blocks = {}
    rel_blocks = []
    for row in tr_rows:
        sub = row.get('subcard') or ''
        tag = row.get('sense_tag')
        frag = 'tr/%s/%s' % (iri_local(sub), iri_local(tag if tag is not None else 'x'))
        siri = R('sense/%s/%s' % (eloc, frag))
        tr_iris.append((siri, row))
        for raw, sigla, locus in extract_ls(row.get('ru')):
            slug = cite_slug(raw)
            if slug:
                cite_blocks[slug] = (sigla, locus, raw)
        if tag is not None and str(tag).isdigit():
            se = key_strat.get(int(tag))
            if se and se.get('stratum_label') and se.get('stratum_label') != '–':
                attest_blocks[str(tag)] = se
        for rr in key_rels:
            if rr.get('subcard') == sub and str(rr.get('sense_tag')) == str(tag):
                rel_blocks.append((siri, rr))

    all_senses = [s for s, _ in carried_iris] + [s for s, _ in tr_iris]
    if all_senses:
        f.write('  ontolex:sense %s .\n' % ', '.join(all_senses))
    else:
        f.write('  rdfs:comment "no senses"@en .\n')

    for siri, rec in carried_iris:
        f.write('%s a ontolex:LexicalSense ;\n' % siri)
        f.write('  skos:definition %s ;\n' % lit(rec['gloss'], lang=rec['lang']))
        f.write('  pwglex:evidenceGrade gr:%s ;\n' % rec['grade'])
        f.write('  dct:source %s .\n' % lit(rec['src']))

    for siri, row in tr_iris:
        grade = GRADE.get(row.get('review_status'), 'machine-preview')
        f.write('%s a ontolex:LexicalSense ;\n' % siri)
        f.write('  skos:definition %s ;\n' % lit(row.get('ru'), lang='ru'))
        if row.get('de'):
            f.write('  pwglex:sourceGloss %s ;\n' % lit(row.get('de'), lang='de'))
        f.write('  pwglex:senseTag %s ;\n' % lit(row.get('sense_tag')))
        f.write('  pwglex:homonym %s ;\n' % lit(store_homonym(row)))
        if row.get('equivalence_type'):
            f.write('  pwglex:equivalenceType %s ;\n' % lit(row.get('equivalence_type')))
        if row.get('source_type'):
            f.write('  pwglex:sourceType %s ;\n' % lit(row.get('source_type')))
        if row.get('differentia'):
            f.write('  pwglex:differentia %s ;\n' % lit(row.get('differentia'), lang='ru'))
        f.write('  pwglex:evidenceGrade gr:%s ;\n' % grade)
        prov = row.get('provenance') or {}
        if prov.get('model_version'):
            f.write('  pwglex:model %s ;\n' % lit(prov.get('model_version')))
        if prov.get('generated_at'):
            f.write('  prov:generatedAtTime %s ;\n' % lit(prov.get('generated_at'), dtype='xsd:dateTime'))
        refs = sorted({R('citation/%s' % cite_slug(raw)) for raw, _, _ in extract_ls(row.get('ru')) if cite_slug(raw)})
        if refs:
            f.write('  dct:references %s ;\n' % ', '.join(refs))
        tag = row.get('sense_tag')
        if tag is not None and str(tag) in attest_blocks:
            f.write('  pwglex:attestation %s ;\n' % R('attestation/%s/%s' % (iri_local(key1), iri_local(str(tag)))))
        f.write('  prov:wasAttributedTo %s .\n' % R('prov/export-lod'))

    for slug, (sigla, locus, raw) in cite_blocks.items():
        f.write('%s a pwglex:Citation, prov:Entity ;\n' % R('citation/%s' % slug))
        f.write('  rdfs:label %s ;\n' % lit(raw))
        if sigla:
            f.write('  pwglex:sourceSigla %s ;\n' % lit(sigla))
        if locus:
            f.write('  pwglex:locus %s ;\n' % lit(locus))
        f.write('  pwglex:lsRaw %s .\n' % lit(raw))

    for tag, se in attest_blocks.items():
        airi = R('attestation/%s/%s' % (iri_local(key1), iri_local(tag)))
        f.write('%s a pwglex:StratumAttestation, prov:Entity ;\n' % airi)
        if se.get('stratum_label'):
            f.write('  skos:prefLabel %s ;\n' % lit(se.get('stratum_label'), lang='ru'))
        if se.get('renou_oldest'):
            f.write('  pwglex:renouOldest %s ;\n' % lit(se.get('renou_oldest')))
        if se.get('renou_youngest'):
            f.write('  pwglex:renouYoungest %s ;\n' % lit(se.get('renou_youngest')))
        if se.get('date_min') is not None:
            f.write('  pwglex:dateMin %s ;\n' % lit(se.get('date_min'), dtype='xsd:integer'))
        if se.get('date_max') is not None:
            f.write('  pwglex:dateMax %s ;\n' % lit(se.get('date_max'), dtype='xsd:integer'))
        f.write('  pwglex:datedCitations %s .\n' % lit(se.get('n_dated_citations') or 0, dtype='xsd:integer'))

    for idx, (siri, rr) in enumerate(rel_blocks, 1):
        rel = rr.get('relationship') or {}
        ins = rel.get('insertion_point') or {}
        riri = R('rel/%s/%s/%d' % (iri_local(key1), iri_local(str(rr.get('sense_tag'))), idx))
        tgt_key1 = ins.get('key1') or key1
        f.write('%s a vartrans:SenseRelation ;\n' % riri)
        f.write('  vartrans:source %s ;\n' % siri)
        f.write('  vartrans:target %s ;\n' % R('entry/%s' % iri_local(tgt_key1)))
        f.write('  vartrans:category %s ;\n' % lit('%s/%s' % (rel.get('op'), rel.get('direction'))))
        f.write('  pwglex:relOp %s ;\n' % lit(rel.get('op')))
        f.write('  pwglex:relDirection %s ;\n' % lit(rel.get('direction')))
        if rel.get('subtype'):
            f.write('  pwglex:relSubtype %s ;\n' % lit(rel.get('subtype')))
        if rr.get('layer'):
            f.write('  pwglex:layer %s ;\n' % lit(rr.get('layer')))
        if ins.get('homonym'):
            f.write('  pwglex:targetHomonym %s ;\n' % lit(ins.get('homonym')))
        if ins.get('target_sense'):
            f.write('  pwglex:targetSenseTag %s ;\n' % lit(ins.get('target_sense')))
        if rel.get('confidence'):
            f.write('  pwglex:confidence %s ;\n' % lit(rel.get('confidence')))
        f.write('  rdfs:comment %s .\n' % lit(rel.get('evidence') or ''))

    f.write('\n')


def entry_local_for(key1, counts):
    counts[key1] = counts.get(key1, 0) + 1
    n = counts[key1]
    return 'entry/%s' % iri_local(key1) + ('' if n == 1 else '-%d' % n)


def export_lexicon(args):
    os.makedirs(args.out_dir, exist_ok=True)
    R = IRI(args.base)
    limit_keys = getattr(args, 'keyset', None)
    if limit_keys is None and args.limit:
        limit_keys = {c.get('key1') for c in iter_jsonl(args.cards, args.limit)}
    sys.stderr.write('loading sidecars...\n')
    translations = load_translations(args.store, limit_keys)
    stratum = load_stratum(args.stratum)
    rels = load_relationships(args.rel)
    out = os.path.join(args.out_dir, 'pwg_ru_lod.ttl')
    counts, lemma_seen, emitted_tr = {}, set(), set()
    n = 0
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write('# PWG->RU LOD graph -- generated by export_lod.py (H350/E7)\n')
        f.write('# base IRI: %s   generated: %s\n\n' % (args.base, args.generated_at))
        f.write(prefixes(args.base))
        emit_vocab_and_lexicon(f, R, args)
        for card in iter_cards(args):
            el = entry_local_for(card.get('key1'), counts)
            emit_card(f, R, card, el, lemma_seen, translations, stratum, rels, args, emitted_tr)
            n += 1
    sys.stderr.write('lexical graph: %d entries -> %s\n' % (n, out))
    print('OntoLex/vartrans/PROV LOD graph -> %s' % out)


def export_dcs_freq(args):
    """Separate DCS-frequency graph keyed by the shared lemma IRI (join spine)."""
    os.makedirs(args.out_dir, exist_ok=True)
    R = IRI(args.base)
    with open(args.freq, encoding='utf-8') as fh:
        freq = json.load(fh)
    by_lemma = freq.get('by_lemma', {})
    iast2key = {}
    for c in iter_cards(args):
        if c.get('iast') and c.get('key1'):
            iast2key.setdefault(c.get('iast'), c.get('key1'))
    out = os.path.join(args.out_dir, 'dcs_freq.ttl')
    n = 0
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write('# DCS frequency graph -- join by shared lemma IRI (export_lod.py dcs-freq)\n\n')
        f.write(prefixes(args.base))
        meta = freq.get('meta', {})
        f.write('%s a prov:Entity ; rdfs:label "VisualDCS token frequency" ;\n' % R('dcs/dataset'))
        f.write('  pwglex:totalTokens %s ; pwglex:distinctLemmas %s .\n\n'
                % (lit(meta.get('total_tokens', 0), dtype='xsd:integer'),
                   lit(meta.get('distinct_lemmas', 0), dtype='xsd:integer')))
        for iast, key1 in iast2key.items():
            fr = by_lemma.get(iast)
            if not fr:
                continue
            f.write('%s pwglex:dcsCount %s ; pwglex:dcsBand %s ; pwglex:dcsHapax %s ; pwglex:dcsCore80 %s .\n'
                    % (R('lemma/%s' % iri_local(key1)),
                       lit(fr.get('count', 0), dtype='xsd:integer'),
                       lit(fr.get('band', 0), dtype='xsd:integer'),
                       'true' if fr.get('hapax') else 'false',
                       'true' if fr.get('core80') else 'false'))
            n += 1
    sys.stderr.write('dcs-freq graph: %d lemmas -> %s\n' % (n, out))
    print('DCS frequency graph -> %s' % out)


# --------------------------------------------------------------------------- #
# German enrichment graph (PWG++)
# --------------------------------------------------------------------------- #
# A first-class ``ontolex:LexicalEntry`` **in German** per lemma, sourced from the
# German source cards (``assembled_cards.jsonl``, the full ~120k headword set) via
# the deterministic masker + microstructure reuse -- NO translation call. Emitted
# as a SEPARATE graph that federates on the *same* ``lemma/<key1>`` IRI as the RU
# lexical graph and the DCS-frequency graph (the shared-lemma spine). This is the
# "glue the derivable layers onto the German original too" deliverable (H772): the
# German entry is enriched by its own <ls> citations + Renou dated strata + the
# shared-lemma DCS frequency, in parallel with and decoupled from the Russian tail.
DE_GRADE = ('pwg-source', 'PWG source gloss (Boehtlingk-Roth), public domain', True)


def de_card_senses(card):
    """Yield German senses for a card straight from its source skeleton.

    Reuses ``pwg_mask.restore`` (placeholder round-trip) + ``microstructure``
    ``split_senses``/``sense_node`` -- the SAME deterministic parse the portrait
    uses, so PWG sense structure is not re-implemented. Each yielded sense carries
    the German equivalents, POS, <ls> citations and Renou strata."""
    import pwg_mask as _pm
    import microstructure as _ms
    for ri, rec in enumerate(card.get('records') or []):
        skel = rec.get('de_skeleton')
        if not skel:
            continue
        try:
            body = _pm.restore(skel, rec.get('placeholders') or [])
        except Exception:
            continue
        for seg in _ms.split_senses(body):
            node = _ms.sense_node(seg)
            glosses = [g for g in (node.get('equivalents_de') or []) if g]
            # n=='0' is the pre-sense head (grammar/general run before sense 1); keep
            # it only when it actually carries a German equivalent, else it is header
            # noise ("¦ m. 4,51") -- entry-level POS is preserved on the real senses.
            if str(node.get('n')) == '0' and not glosses:
                continue
            definition = '; '.join(glosses) if glosses else (node.get('gloss_de') or '')
            if not definition.strip():
                continue
            yield {
                'record': ri, 'n': node.get('n'), 'sub': node.get('sub'),
                'glosses': glosses, 'definition': definition,
                'eqtype': node.get('equivalence_type'),
                'grammar': list(dict.fromkeys(node.get('grammar') or [])),
                'diasystem': node.get('diasystem') or [],
                'strata': sorted(node.get('strata') or []),
                'seg_text': seg.get('text') or '',
            }


def emit_de_vocab(f, R, args):
    f.write('# --- German enrichment lexicon (PWG++) -----------------------\n')
    f.write('%s a lime:Lexicon ;\n' % R('lexicon/pwg-de'))
    f.write('  rdfs:label "PWG German lexicon (Petersburg Dictionary, enriched)"@en ;\n')
    f.write('  dct:language "de" ; lime:language "de" ;\n')
    f.write('  dct:source <https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/> ;\n')
    f.write('  dct:license <https://creativecommons.org/publicdomain/mark/1.0/> ;\n')
    f.write('  prov:wasGeneratedBy %s ;\n' % R('prov/export-lod-de'))
    f.write('  dct:created "%s"^^xsd:date .\n\n' % esc(args.generated_at))
    f.write('%s a prov:Activity ;\n' % R('prov/export-lod-de'))
    f.write('  rdfs:label "PWG++ German enrichment export (export_lod.py de-lexicon)" ;\n')
    f.write('  prov:endedAtTime "%s"^^xsd:date .\n\n' % esc(args.generated_at))
    slug, label, citable = DE_GRADE
    f.write('gr:%s a skos:Concept ; skos:inScheme %s ; skos:prefLabel "%s"@en ; pwglex:citable %s .\n\n'
            % (slug, R('grade/scheme'), esc(label), 'true' if citable else 'false'))


def emit_de_card(f, R, card, suffix, lemma_seen, stratum, args):
    """Emit the German LexicalEntry + its senses + citations + stratum for one
    card. ``suffix`` disambiguates homograph cards sharing a key1 (mirrors the RU
    graph's entry/<key1>-N). Returns the number of senses emitted (0 -> nothing)."""
    key1 = card.get('key1')
    senses = list(de_card_senses(card))
    if not senses:
        return 0
    ekey = iri_local(key1) + suffix
    lemma_iri = R('lemma/%s' % iri_local(key1))
    entry_iri = R('entry/%s/de' % ekey)

    if key1 not in lemma_seen:
        lemma_seen.add(key1)
        f.write('%s a ontolex:Form, lila:Lemma ;\n' % lemma_iri)
        f.write('  ontolex:writtenRep %s ;\n' % lit(key1, lang='sa-Latn-x-slp1'))
        if card.get('iast'):
            f.write('  ontolex:writtenRep %s ;\n' % lit(card.get('iast'), lang='sa-Latn'))
        f.write('  pwglex:slp1 %s ;\n' % lit(key1))
        f.write('  rdfs:label %s .\n' % lit(card.get('iast') or key1, lang='sa-Latn'))

    f.write('%s a ontolex:LexicalEntry ;\n' % entry_iri)
    f.write('  rdfs:label %s ;\n' % lit(card.get('iast') or key1, lang='sa-Latn'))
    f.write('  dct:language "de" ;\n')
    f.write('  dct:isPartOf %s ;\n' % R('lexicon/pwg-de'))
    f.write('  ontolex:canonicalForm %s ;\n' % lemma_iri)

    sense_iris, cite_blocks, attest_used = [], {}, {}
    key_strat = stratum.get(key1, {})
    # leading running index si guarantees a unique sense IRI even when two source
    # segments share (record, n, sub); n/sub stay queryable via senseNumber/senseSub.
    for si, s in enumerate(senses, 1):
        frag = 'de/%d/%s%s' % (si, iri_local(str(s['n'])),
                               ('-' + iri_local(str(s['sub']))) if s['sub'] else '')
        siri = R('sense/%s/%s' % (ekey, frag))
        sense_iris.append((siri, s))
        for raw, sigla, locus in extract_ls(s['seg_text']):
            slug = cite_slug(raw)
            if slug:
                cite_blocks[slug] = (sigla, locus, raw)
        if str(s['n']).isdigit():
            se = key_strat.get(int(s['n']))
            if se and se.get('stratum_label') and se.get('stratum_label') != '–':
                attest_used[str(s['n'])] = se
    f.write('  ontolex:sense %s .\n' % ', '.join(i for i, _ in sense_iris))

    for siri, s in sense_iris:
        f.write('%s a ontolex:LexicalSense ;\n' % siri)
        f.write('  skos:definition %s ;\n' % lit(s['definition'], lang='de'))
        for g in s['glosses']:
            f.write('  pwglex:germanEquivalent %s ;\n' % lit(g, lang='de'))
        f.write('  pwglex:senseNumber %s ;\n' % lit(str(s['n'])))
        if s['sub']:
            f.write('  pwglex:senseSub %s ;\n' % lit(str(s['sub'])))
        f.write('  pwglex:equivalenceType %s ;\n' % lit(s['eqtype']))
        for pos in s['grammar']:
            f.write('  pwglex:grammar %s ;\n' % lit(pos))
        for d in s['diasystem']:
            f.write('  pwglex:diasystem %s ;\n' % lit(d))
        for st in s['strata']:
            f.write('  pwglex:renouStratum %s ;\n' % lit(st))
        refs = sorted({R('citation/%s' % cite_slug(raw))
                       for raw, _, _ in extract_ls(s['seg_text']) if cite_slug(raw)})
        if refs:
            f.write('  dct:references %s ;\n' % ', '.join(refs))
        if str(s['n']) in attest_used:
            f.write('  pwglex:attestation %s ;\n'
                    % R('attestation/%s/%s' % (iri_local(key1), iri_local(str(s['n'])))))
        f.write('  pwglex:evidenceGrade gr:%s .\n' % DE_GRADE[0])

    for slug, (sigla, locus, raw) in cite_blocks.items():
        f.write('%s a pwglex:Citation, prov:Entity ;\n' % R('citation/%s' % slug))
        f.write('  rdfs:label %s ;\n' % lit(raw))
        if sigla:
            f.write('  pwglex:sourceSigla %s ;\n' % lit(sigla))
        if locus:
            f.write('  pwglex:locus %s ;\n' % lit(locus))
        f.write('  pwglex:lsRaw %s .\n' % lit(raw))

    for tag, se in attest_used.items():
        airi = R('attestation/%s/%s' % (iri_local(key1), iri_local(tag)))
        f.write('%s a pwglex:StratumAttestation, prov:Entity ;\n' % airi)
        if se.get('stratum_label'):
            f.write('  skos:prefLabel %s ;\n' % lit(se.get('stratum_label'), lang='ru'))
        if se.get('renou_oldest'):
            f.write('  pwglex:renouOldest %s ;\n' % lit(se.get('renou_oldest')))
        if se.get('renou_youngest'):
            f.write('  pwglex:renouYoungest %s ;\n' % lit(se.get('renou_youngest')))
        if se.get('date_min') is not None:
            f.write('  pwglex:dateMin %s ;\n' % lit(se.get('date_min'), dtype='xsd:integer'))
        if se.get('date_max') is not None:
            f.write('  pwglex:dateMax %s ;\n' % lit(se.get('date_max'), dtype='xsd:integer'))
        f.write('  pwglex:datedCitations %s .\n' % lit(se.get('n_dated_citations') or 0, dtype='xsd:integer'))

    f.write('\n')
    return len(sense_iris)


def export_de_lexicon(args):
    os.makedirs(args.out_dir, exist_ok=True)
    R = IRI(args.base)
    sys.stderr.write('loading stratum sidecar...\n')
    stratum = load_stratum(args.stratum)
    out = os.path.join(args.out_dir, 'pwg_de_lexicon.ttl')
    lemma_seen = set()
    counts = {}
    n_entry = n_sense = 0
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write('# PWG++ German enrichment graph -- export_lod.py de-lexicon (H772)\n')
        f.write('# base IRI: %s   generated: %s\n\n' % (args.base, args.generated_at))
        f.write(prefixes(args.base))
        emit_de_vocab(f, R, args)
        for card in iter_cards(args):
            key1 = card.get('key1')
            counts[key1] = counts.get(key1, 0) + 1
            suffix = '' if counts[key1] == 1 else '-%d' % counts[key1]
            k = emit_de_card(f, R, card, suffix, lemma_seen, stratum, args)
            if k:
                n_entry += 1
                n_sense += k
    sys.stderr.write('de-lexicon graph: %d entries / %d senses -> %s\n' % (n_entry, n_sense, out))
    print('PWG++ German enrichment graph -> %s' % out)


# --------------------------------------------------------------------------- #
# Grammar layer graph (Whitney root / nominal) -- H781
# --------------------------------------------------------------------------- #
# The THIRD derivable layer glued onto the shared lemma/<key1> spine (after
# dcs-freq and de-lexicon): the Whitney root grammar (class/ppp/§§/exceptions,
# whitney_grammar.py) or, for non-root headwords, the nominal-grammar block
# (stem class/§§/paradigm/compounds/Zaliznyak index, nominal_grammar.py). One
# block per key1 -- NOT per homonym entry, since both source functions are
# already keyed purely on the SLP1 string. Emitted as its own SEPARATE graph
# (grammar.ttl) so lexicon/dcs-freq/de-lexicon stay byte-identical.
GRAMMAR_GRADE = ('grammar-derived',
                  'derived from the WhitneyRoots crosswalk + nominal_grammar.py '
                  'concordance (structured data, not a translation)', True)

# Mirrors pilot/enrich_portrait_nominal_grammar.py's _GENDER_PRIORITY -- prefer a
# concrete noun gender over an adj./adv. use when a card's senses carry several
# <lex> tags, so the stem-class/Zaliznyak-index join reflects the substantive.
_GENDER_PRIORITY = ('m.', 'f.', 'n.', 'm.n.', 'm.f.', 'f.n.', 'm.f.n.')

_LEXINFO_GENDER = {'m.': 'lexinfo:masculine', 'f.': 'lexinfo:feminine', 'n.': 'lexinfo:neuter'}


def _aggregate_lex(senses):
    """One <lex> tag for a non-root card: dedupe grammar tags across ALL its
    PWG senses (first-seen order, via de_card_senses' deterministic parse),
    then apply the concrete-noun-gender priority pick."""
    tags, seen = [], set()
    for s in senses:
        for t in (s.get('grammar') or []):
            if t not in seen:
                seen.add(t)
                tags.append(t)
    for g in _GENDER_PRIORITY:
        if g in tags:
            return g
    return tags[0] if tags else ''


def emit_grammar_vocab(f, R, args):
    f.write('# --- Grammar layer (Whitney root / nominal concordance) -------\n')
    f.write('%s a lime:Lexicon ;\n' % R('lexicon/pwg-grammar'))
    f.write('  rdfs:label "PWG grammar layer (Whitney root + nominal concordance)"@en ;\n')
    f.write('  dct:source <https://github.com/gasyoun/WhitneyRoots> ;\n')
    f.write('  dct:license <https://creativecommons.org/licenses/by-sa/4.0/> ;\n')
    f.write('  prov:wasGeneratedBy %s ;\n' % R('prov/export-lod-grammar'))
    f.write('  dct:created "%s"^^xsd:date .\n\n' % esc(args.generated_at))
    f.write('%s a prov:Activity ;\n' % R('prov/export-lod-grammar'))
    f.write('  rdfs:label "Grammar layer export (export_lod.py grammar, H781)" ;\n')
    f.write('  prov:endedAtTime "%s"^^xsd:date .\n\n' % esc(args.generated_at))
    slug, label, citable = GRAMMAR_GRADE
    f.write('gr:%s a skos:Concept ; skos:inScheme %s ; skos:prefLabel "%s"@en ; pwglex:citable %s .\n\n'
            % (slug, R('grade/scheme'), esc(label), 'true' if citable else 'false'))


def _emit_lemma_node(f, R, card, lemma_seen):
    """Idempotent shared lemma node -- byte-identical to emit_card's/emit_de_card's
    block, reused verbatim so the lemma serialization never diverges."""
    key1 = card.get('key1')
    lemma_iri = R('lemma/%s' % iri_local(key1))
    if key1 not in lemma_seen:
        lemma_seen.add(key1)
        f.write('%s a ontolex:Form, lila:Lemma ;\n' % lemma_iri)
        f.write('  ontolex:writtenRep %s ;\n' % lit(key1, lang='sa-Latn-x-slp1'))
        if card.get('iast'):
            f.write('  ontolex:writtenRep %s ;\n' % lit(card.get('iast'), lang='sa-Latn'))
        f.write('  pwglex:slp1 %s ;\n' % lit(key1))
        f.write('  rdfs:label %s .\n' % lit(card.get('iast') or key1, lang='sa-Latn'))
    return lemma_iri


def emit_grammar_card(f, R, card, lemma_seen, seen_keys, args):
    """Emit the grammar block for one lemma (key1). Three cases:

    1. exactly one Whitney root record  -> the ROOT branch (class/ppp/§§/
       irregularities), an unambiguous PWG-homonym<->Whitney-homonym join.
    2. >1 Whitney root record (as/i/vid-style homonym-keyed roots)          -> a
       ``pwglex:homonymAmbiguous`` marker ONLY -- never guess which homonym's
       class/ppp to attach (GRAMMAR_LAYER.md's homonym-alignment guardrail).
    3. no Whitney root record          -> the NOMINAL branch (stem class/§§/
       paradigm/compounds/Zaliznyak index), sourced via nominal_grammar_for()
       with a single aggregated <lex> tag (see _aggregate_lex).

    Grammar facts are a function of key1 alone, so this fires ONCE per key1
    regardless of how many homonym sub-cards share it (``seen_keys``) --
    distinct from ``lemma_seen``, which only guards the shared lemma NODE.
    """
    import whitney_grammar as WG
    import nominal_grammar as NG

    key1 = card.get('key1')
    if key1 in seen_keys:
        return 0
    seen_keys.add(key1)

    lemma_iri = _emit_lemma_node(f, R, card, lemma_seen)
    wg_recs = WG.grammar_for(key1)
    sections = []   # (sec_iri, label, category, range) -> pwglex:GrammarSection resources

    if len(wg_recs) == 1:
        rec = wg_recs[0]
        for cat, rng in sorted((rec.get('section_refs') or {}).items()):
            sec_iri = R('section/%s/%s' % (iri_local(key1), iri_local(cat)))
            sections.append((sec_iri, '%s §%s' % (cat, rng), cat, rng))
        lines = ['  pwglex:grammarBranch "root" ;']
        if rec.get('class'):
            lines.append('  pwglex:whitneyClass %s ;' % lit(rec.get('class')))
            lines.append('  lexinfo:conjugationClass %s ;' % lit(rec.get('class')))
        if rec.get('ppp'):
            lines.append('  pwglex:ppp %s ;' % lit(rec.get('ppp')))
        if sections:
            lines.append('  pwglex:sectionRef %s ;' % ', '.join(s[0] for s in sections))
        for irr in rec.get('irregularities') or []:
            lines.append('  pwglex:irregularity %s ;' % lit(irr))
        lines.append('  pwglex:evidenceGrade gr:%s .' % GRAMMAR_GRADE[0])
        f.write('%s\n' % lemma_iri)
        f.write('\n'.join(lines) + '\n\n')
    elif len(wg_recs) > 1:
        # Homonym-keyed root (as/i/vid...): the PWG-homonym<->Whitney-homonym
        # alignment is unresolved -- flag, don't guess (GRAMMAR_LAYER.md).
        f.write('%s pwglex:grammarBranch "root-ambiguous" ;\n' % lemma_iri)
        f.write('  pwglex:homonymAmbiguous true ;\n')
        f.write('  rdfs:comment %s ;\n' % lit(
            '%d Whitney homonyms for this SLP1 root -- PWG<->Whitney homonym '
            'alignment not resolved, no class/ppp attached' % len(wg_recs)))
        f.write('  pwglex:evidenceGrade gr:%s .\n\n' % GRAMMAR_GRADE[0])
    else:
        senses = list(de_card_senses(card))
        lex = _aggregate_lex(senses)
        ng = NG.nominal_grammar_for(key1, lex, accented=card.get('key2'))
        if ng.get('declension_sections'):
            sections.append((R('section/%s/declension' % iri_local(key1)),
                             'declension %s' % ng['declension_sections'], 'declension', ng['declension_sections']))
        if ng.get('paradigm_section'):
            sections.append((R('section/%s/paradigm' % iri_local(key1)),
                             'paradigm %s' % ng['paradigm_section'], 'paradigm', ng['paradigm_section']))
        if ng.get('compound_sections'):
            sections.append((R('section/%s/compound' % iri_local(key1)),
                             'compound %s' % ng['compound_sections'], 'compound', ng['compound_sections']))
        if ng.get('derivation_sections'):
            sections.append((R('section/%s/derivation' % iri_local(key1)),
                             'derivation %s' % ng['derivation_sections'], 'derivation', ng['derivation_sections']))
        lines = ['  pwglex:grammarBranch "nominal" ;']
        lines.append('  pwglex:stemClass %s ;' % lit(ng['stem_class']))
        gender_iri = _LEXINFO_GENDER.get(ng.get('gender'))
        if gender_iri:
            lines.append('  lexinfo:gender %s ;' % gender_iri)
        for member in ng.get('compound_members') or []:
            lines.append('  pwglex:compoundMember %s ;' % lit(member))
        for irr in ng.get('irregularities') or []:
            lines.append('  pwglex:irregularity %s ;' % lit(irr))
        lines.append('  pwglex:zaliznyakIndex %s ;' % lit(ng['zaliznyak_index']))
        if sections:
            lines.append('  pwglex:sectionRef %s ;' % ', '.join(s[0] for s in sections))
        lines.append('  pwglex:evidenceGrade gr:%s .' % GRAMMAR_GRADE[0])
        f.write('%s\n' % lemma_iri)
        f.write('\n'.join(lines) + '\n\n')

    for sec_iri, label, cat, rng in sections:
        f.write('%s a pwglex:GrammarSection ;\n' % sec_iri)
        f.write('  rdfs:label %s ;\n' % lit(label))
        f.write('  pwglex:sectionCategory %s ;\n' % lit(cat))
        f.write('  pwglex:sectionRange %s .\n' % lit(rng))
    if sections:
        f.write('\n')
    return 1


def export_grammar(args):
    os.makedirs(args.out_dir, exist_ok=True)
    R = IRI(args.base)
    out = os.path.join(args.out_dir, 'grammar.ttl')
    lemma_seen, seen_keys = set(), set()
    n = 0
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write('# Grammar layer graph -- export_lod.py grammar (H781)\n')
        f.write('# base IRI: %s   generated: %s\n\n' % (args.base, args.generated_at))
        f.write(prefixes(args.base))
        emit_grammar_vocab(f, R, args)
        for card in iter_cards(args):
            n += emit_grammar_card(f, R, card, lemma_seen, seen_keys, args)
    sys.stderr.write('grammar graph: %d lemmas -> %s\n' % (n, out))
    print('Grammar layer LOD graph -> %s' % out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', choices=['lexicon', 'dcs-freq', 'de-lexicon', 'grammar', 'all'])
    ap.add_argument('--cards', default=DEFAULT_CARDS)
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--rel', default=DEFAULT_REL)
    ap.add_argument('--stratum', default=DEFAULT_STRATUM)
    ap.add_argument('--freq', default=DEFAULT_FREQ)
    ap.add_argument('--out-dir', default=DEFAULT_RELEASE)
    ap.add_argument('--base-iri', dest='base', default=DEFAULT_BASE,
                    help='dereferenceable base IRI namespace (default: w3id placeholder pending domain @DECIDE)')
    ap.add_argument('--generated-at', default=None,
                    help='ISO date stamped into provenance (default: today; pass a fixed value for byte-stable fixtures)')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--keys', default=None,
                    help='comma-separated key1 whitelist for a curated fixture (overrides --limit)')
    ap.add_argument('--keys-file', default=None,
                    help='file with one key1 per line for a curated fixture (overrides --limit)')
    args = ap.parse_args()
    if not args.base.endswith('/'):
        args.base += '/'
    args.keyset = None
    if args.keys:
        args.keyset = {k.strip() for k in args.keys.split(',') if k.strip()}
    elif args.keys_file:
        with open(args.keys_file, encoding='utf-8') as fh:
            args.keyset = {ln.strip() for ln in fh if ln.strip() and not ln.startswith('#')}
    if args.generated_at is None:
        import datetime
        args.generated_at = datetime.date.today().isoformat()
    if args.mode in ('lexicon', 'all'):
        export_lexicon(args)
    if args.mode in ('dcs-freq', 'all'):
        export_dcs_freq(args)
    if args.mode in ('de-lexicon', 'all'):
        export_de_lexicon(args)
    if args.mode in ('grammar', 'all'):
        export_grammar(args)


if __name__ == '__main__':
    main()
