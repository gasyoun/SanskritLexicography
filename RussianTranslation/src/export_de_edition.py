#!/usr/bin/env python
"""DE edition-graph export profile — OntoLex-Lemon + TEI Lex-0 (H1629).

The **German** side of the PWG edition graph, serialized for FAIR reuse. Where
``export_lod.py de-lexicon`` (H772) emits German senses re-parsed straight from
``assembled_cards.jsonl`` and carries only gloss + citation + Renou stratum,
this profile exports the *edition graph* built by H1624 G1–G6 — one entry per
(key1, homonym) whose senses come from several **editions** (PWG, PW, SCH,
PWKVN, NWS), each sense carrying the five structured DE layers:

  =====================  =========================  ==============================
  layer (H1624)          producer module            carried as
  =====================  =========================  ==============================
  G1 gloss_lang spans    ``pwg_mask.gloss_lang_spans``   pwglex:glossSpan / <gloss>
  G2 government          ``government_census.extract_government``  pwglex:Government / <gramGrp>
  -- form_notes          ``form_labels.extract_form_notes``        pwglex:FormNote / <gram type="case">
  G3 citation_edges      ``citation_edges.extract_citation_edges`` pwglex:Citation / <cit><bibl>
  G4 edition_rel         ``edition_rel.classify_edition_rel``      vartrans:SenseRelation / <xr>
  =====================  =========================  ==============================

Every layer is **recomputed from the German string** by the shipped extractor
(reuse, not reimplementation), and a precomputed field on the input row is used
only when present and structurally valid — so the export does not depend on a
particular store-annotation vintage.

**Rights fence (N9).** This export is DE-only. Input rows pass a hard field
allowlist (:data:`DE_FIELDS`) at read time — ``ru``/``en``/``review_status``/
``reviewer``/``provenance``/``evidence`` are dropped before any emitter sees a
row, and :func:`assert_rights_safe` re-checks the serialized bytes. A row whose
German-bearing fields contain Cyrillic is **quarantined**, not emitted: the store
has real RU-into-DE contamination (11 ``de`` rows / 110 ``sense_tag`` rows as of
26-07-2026 — see FINDINGS), and a corrupted German source must never reach a
public artifact.

  python export_de_edition.py --selftest
  python export_de_edition.py export --out-dir release/fixture/de_edition
  python export_de_edition.py export --rows src/fixtures/pwg_de_edition.fixture.jsonl
  python export_de_edition.py export --store src/pwg_ru_translated.jsonl --limit 500
  python export_de_edition.py export --strict     # fail instead of quarantining

Field-by-field mapping + provenance:
``DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md``.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import export_lod as EL                                    # noqa: E402 IRI/Turtle helpers
import microstructure as MS                                # noqa: E402 clean_de + PCT/SA regexes
import pwg_mask                                            # noqa: E402 G1 gloss_lang
from government_census import extract_government           # noqa: E402 G2
from form_labels import extract_form_notes                 # noqa: E402 form layer
from citation_edges import extract_citation_edges          # noqa: E402 G3
from edition_rel import (  # noqa: E402 G4
    base_subtype, classify_edition_rel, homonym_of,
)

DEFAULT_ROWS = os.path.join(HERE, 'fixtures', 'pwg_de_edition.fixture.jsonl')
DEFAULT_OUT = os.path.join(HERE, '..', 'release', 'fixture', 'de_edition')

#: Hard allowlist — the ONLY input fields this profile ever reads. Everything
#: else on a store row (ru, review_status, reviewer, provenance, evidence, …)
#: is dropped before any emitter sees the row.
#:
#: The store's ``h`` field is deliberately NOT here: the homonym is derived from
#: ``subcard`` (:func:`edition_rel.homonym_of`), and ``h`` is free text that in
#: practice carries Russian disambiguation prose (e.g. ``PW 3 (с sam, …)``), so
#: reading it would import a contaminated field for no gain.
DE_FIELDS = ('key1', 'iast', 'subcard', 'sense_tag', 'layer',
             'volume', 'page', 'column', 'de')

#: Fields whose presence in the output would be a rights breach (N9).
FORBIDDEN_FIELDS = ('ru', 'en', 'review_status', 'reviewer', 'provenance',
                    'evidence', 'evidence_summary', 'corpus_gate', 'differentia')

CYRILLIC = re.compile('[Ѐ-ӿ]')
#: Run form, so a scrubbed label carries ONE marker per contiguous Russian run
#: rather than one per character.
CYRILLIC_RUN = re.compile('[Ѐ-ӿ]+(?:[\\s‐-―-]+[Ѐ-ӿ]+)*')

#: Edition layer -> human label + licence posture. PWG/PW/SCH/PWKVN are the
#: 19th–early-20th-c. German editions (public domain); NWS is the Cologne
#: Nachtragswörterbuch working layer.
LAYERS = {
    'pwg':   ('PWG — Böhtlingk-Roth, Sanskrit-Wörterbuch (1855–1875)', 'pd'),
    'pw':    ('PW — Böhtlingk, kürzere Fassung (1879–1889)', 'pd'),
    'sch':   ('SCH — Schmidt, Nachträge (1928)', 'pd'),
    'pwkvn': ('PWKVN — Nachträge to the kürzere Fassung', 'pd'),
    'nws':   ('NWS — Nachtragswörterbuch (Cologne working layer)', 'project'),
}

#: case slug -> lexinfo individual (OntoLex side) / TEI @norm value.
LEXINFO_CASE = {
    'acc': 'lexinfo:accusativeCase', 'gen': 'lexinfo:genitiveCase',
    'dat': 'lexinfo:dativeCase', 'instr': 'lexinfo:instrumentalCase',
    'loc': 'lexinfo:locativeCase', 'abl': 'lexinfo:ablativeCase',
    'nom': 'lexinfo:nominativeCase', 'voc': 'lexinfo:vocativeCase',
}

DE_EDITION_GRADE = ('pwg-de-edition',
                    'German edition text + machine-derived DE structure '
                    '(no translation, no review score)', True)


# --------------------------------------------------------------------------- #
# Input adapters + rights fence
# --------------------------------------------------------------------------- #
def de_only(row: dict) -> dict:
    """Project a raw input row onto the DE allowlist. The single choke point
    through which store data enters this profile."""
    return {k: row.get(k) for k in DE_FIELDS}


#: Cyrillic in one of these fields means the German text itself is corrupted —
#: the row is quarantined, never published.
BLOCKING_DE_FIELDS = ('de', 'iast')
#: Cyrillic here is a structural-label defect only; :func:`sense_tag_slug`
#: already reduces the tag to its ASCII skeleton, so the German survives.
SANITIZABLE_DE_FIELDS = ('sense_tag',)


def de_impurity(row: dict) -> list[str]:
    """Names of German-bearing fields on ``row`` that contain Cyrillic.

    Returns field names (not just a count) so the manifest can name the defect.
    Callers split the result with :data:`BLOCKING_DE_FIELDS` /
    :data:`SANITIZABLE_DE_FIELDS`.
    """
    return sorted(k for k in BLOCKING_DE_FIELDS + SANITIZABLE_DE_FIELDS
                  if isinstance(row.get(k), str) and CYRILLIC.search(row[k]))


#: Marker left where a Cyrillic run was scrubbed out of a structural label, so
#: the defect stays visible in the artifact instead of silently vanishing.
RU_ELIDED = '[ru elided]'


def scrub_cyrillic(text):
    """Replace Cyrillic runs in a structural label with :data:`RU_ELIDED`.

    ``edition_rel.classify_edition_rel`` builds its ``evidence`` string by
    interpolating the RAW ``sense_tag`` (``"PW abridging restatement;
    sense_tag=%r"``), and that string is emitted verbatim as ``rdfs:comment``
    (Turtle) and ``@relEvidence`` (TEI). ``sense_tag`` is
    :data:`SANITIZABLE_DE_FIELDS` — ~1% of store rows carry Russian free text
    there — but the slug sanitizer only guards IRIs/``xml:id``s, so the raw tag
    reached the serializer through the evidence string and tripped
    :func:`assert_rights_safe` on a full-store export (H1635).
    """
    if not isinstance(text, str):
        return text
    return CYRILLIC_RUN.sub(RU_ELIDED, text)


def iter_rows(path: str, limit: int | None = None, keys: set | None = None):
    """Stream DE-projected rows from a JSONL source (fixture or store)."""
    with open(path, encoding='utf-8') as f:
        n = 0
        for line in f:
            if not line.strip():
                continue
            raw = json.loads(line)
            if keys is not None and raw.get('key1') not in keys:
                continue
            yield de_only(raw)
            n += 1
            if limit and n >= limit:
                break


def assert_rights_safe(text: str, what: str) -> None:
    """Post-serialization guard: no forbidden field name, no Cyrillic."""
    # Match a forbidden field only where a field NAME can occur — a JSON key, a
    # Turtle predicate, or an XML element. Never a literal value: `"en"` is a
    # legitimate gloss-language value and `pwglex:evidenceGrade` a legitimate
    # DE-side predicate, and neither is a leak.
    bad = []
    for f in FORBIDDEN_FIELDS:
        e = re.escape(f)
        if re.search(r'"%s"\s*:|(?<![\w:-])pwglex:%s(?![\w-])|<%s[\s/>]' % (e, e, e), text):
            bad.append(f)
    if bad:
        raise SystemExit('RIGHTS BREACH in %s: forbidden field(s) %s' % (what, bad))
    m = CYRILLIC.search(text)
    if m:
        i = max(0, m.start() - 60)
        raise SystemExit('RIGHTS/PURITY BREACH in %s: Cyrillic at %d: %r'
                         % (what, m.start(), text[i:m.start() + 60]))


# --------------------------------------------------------------------------- #
# Layer computation (reuse the shipped extractors; trust a valid precomputed
# field when the caller already has one)
# --------------------------------------------------------------------------- #
def _use_precomputed(row, field, required_keys):
    val = row.get(field)
    if not isinstance(val, list):
        return None
    for item in val:
        if not isinstance(item, dict) or not required_keys <= set(item):
            return None
    return val


def sense_layers(row: dict, pwg_genders: dict | None = None) -> dict:
    """The five H1624 DE layers for one edition sense row."""
    de = row.get('de') or ''
    government = (_use_precomputed(row, 'government', {'cases', 'kind'})
                  or extract_government(de))
    form_notes = (_use_precomputed(row, 'form_notes', {'case', 'kind'})
                  or extract_form_notes(de))
    citations = (_use_precomputed(row, 'citation_edges', {'raw_ls', 'resolver_status'})
                 or extract_citation_edges(de))
    rel = row.get('edition_rel')
    if not isinstance(rel, dict) or 'subtype' not in rel:
        rel = classify_edition_rel(
            row.get('layer'), sense_tag=row.get('sense_tag'), de=de,
            key1=row.get('key1'), subcard=row.get('subcard'),
            pwg_genders=(pwg_genders or {}).get(row.get('key1')))
    # The classifier interpolates the RAW sense_tag into `evidence`, and both
    # emitters write that string out verbatim. Scrub it here — the one place
    # both the precomputed and the freshly-classified `rel` pass through.
    if isinstance(rel, dict) and rel.get('evidence'):
        rel = dict(rel, evidence=scrub_cyrillic(rel['evidence']))
    # G1: keep only the spans whose language is NOT German — those are the
    # editorially interesting ones (Latin cue, botany binomial, Wilson English)
    # and the ones a consumer must not read as German.
    spans = [s for s in pwg_mask.gloss_lang_spans(de)
             if s.get('gloss_lang') != 'de']
    return {'government': government, 'form_notes': form_notes,
            'citation_edges': citations, 'edition_rel': rel, 'gloss_spans': spans}


def sense_text(de: str) -> tuple[str, list[str], list[str]]:
    """(definition, braced German equivalents, Sanskrit example forms)."""
    equivalents, seen = [], set()
    for m in MS.PCT.finditer(de or ''):
        g = MS.clean_de(m.group(1))
        if g and g not in seen:
            seen.add(g)
            equivalents.append(g)
    examples = [e.strip() for e in MS.SA.findall(de or '') if e.strip()][:4]
    definition = '; '.join(equivalents) if equivalents else MS.clean_de(de or '')
    return definition, equivalents, examples


def sense_tag_slug(tag) -> str:
    """Structural sense id. Never carries prose — a sense_tag can be free text
    (and, in ~1% of store rows, Russian free text), so only the ASCII structural
    skeleton survives into an IRI / xml:id."""
    s = re.sub(r'[^0-9A-Za-z_.-]+', '-', str(tag if tag is not None else 'x'))
    s = re.sub(r'-{2,}', '-', s).strip('-.')
    return s[:48] or 'x'


def numbered_senses(entry: dict):
    """Yield ``(row, layers, sense_id)`` for one entry.

    Single source of truth for sense-id assignment, so the Turtle and the TEI
    can never drift apart on identifiers (they cross-reference each other).
    """
    used = set()
    for row in entry['senses']:
        sid = sense_tag_slug(row.get('sense_tag'))
        base, k = sid, 2
        while (row.get('layer'), sid) in used:
            sid = '%s-%d' % (base, k)
            k += 1
        used.add((row.get('layer'), sid))
        yield row, sense_layers(row), sid


def group_entries(rows) -> list[dict]:
    """Group DE rows into edition entries keyed on (key1, homonym).

    One entry, many editions: this is what makes the artifact an *edition graph*
    rather than five parallel dictionaries.
    """
    order, entries = [], {}
    for row in rows:
        key1 = row.get('key1') or ''
        hom = homonym_of(row.get('subcard') or '') or 'h0'
        k = (key1, hom)
        if k not in entries:
            order.append(k)
            entries[k] = {'key1': key1, 'hom': hom, 'iast': row.get('iast') or '',
                          'senses': []}
        if row.get('iast') and not entries[k]['iast']:
            entries[k]['iast'] = row['iast']
        entries[k]['senses'].append(row)
    return [entries[k] for k in order]


# --------------------------------------------------------------------------- #
# OntoLex-Lemon (Turtle)
# --------------------------------------------------------------------------- #
def _ttl_vocab(f, R, args):
    f.write('# --- DE edition lexicon (H1629) ------------------------------\n')
    f.write('%s a lime:Lexicon ;\n' % R('lexicon/pwg-de-edition'))
    f.write('  rdfs:label "PWG German edition graph (PWG/PW/SCH/PWKVN/NWS)"@en ;\n')
    f.write('  dct:language "de" ; lime:language "de" ;\n')
    f.write('  dct:source <https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/> ;\n')
    f.write('  dct:license <https://creativecommons.org/publicdomain/mark/1.0/> ;\n')
    f.write('  prov:wasGeneratedBy %s ;\n' % R('prov/export-de-edition'))
    f.write('  dct:created "%s"^^xsd:date .\n\n' % EL.esc(args.generated_at))
    f.write('%s a prov:Activity ;\n' % R('prov/export-de-edition'))
    f.write('  rdfs:label "DE edition-graph export (export_de_edition.py, H1629)" ;\n')
    f.write('  prov:endedAtTime "%s"^^xsd:date .\n\n' % EL.esc(args.generated_at))
    slug, label, citable = DE_EDITION_GRADE
    f.write('gr:%s a skos:Concept ; skos:inScheme %s ; skos:prefLabel "%s"@en ; pwglex:citable %s .\n\n'
            % (slug, R('grade/scheme'), EL.esc(label), 'true' if citable else 'false'))
    for layer, (label, posture) in sorted(LAYERS.items()):
        f.write('%s a pwglex:Edition ; rdfs:label "%s"@en ; pwglex:rightsPosture "%s" .\n'
                % (R('edition/%s' % layer), EL.esc(label), posture))
    f.write('\n')


def _ttl_sense(f, R, entry, row, lay, sid):
    key1, hom = entry['key1'], entry['hom']
    layer = row.get('layer') or 'unknown'
    siri = R('sense/%s/%s/%s/%s' % (EL.iri_local(key1), hom, EL.iri_local(layer), sid))
    definition, equivalents, examples = sense_text(row.get('de'))
    f.write('%s a ontolex:LexicalSense ;\n' % siri)
    f.write('  skos:definition %s ;\n' % EL.lit(definition, lang='de'))
    for g in equivalents:
        f.write('  pwglex:germanEquivalent %s ;\n' % EL.lit(g, lang='de'))
    for ex in examples:
        f.write('  pwglex:exampleForm %s ;\n' % EL.lit(ex, lang='sa-Latn-x-slp1'))
    f.write('  pwglex:senseTag %s ;\n' % EL.lit(sid))
    f.write('  pwglex:homonym %s ;\n' % EL.lit(hom))
    f.write('  pwglex:edition %s ;\n' % R('edition/%s' % EL.iri_local(layer)))
    if row.get('page'):
        f.write('  pwglex:page %s ;\n' % EL.lit(row.get('page')))
    if row.get('volume'):
        f.write('  pwglex:volume %s ;\n' % EL.lit(row.get('volume')))

    for i, g in enumerate(lay['government'], 1):
        f.write('  pwglex:government %s ;\n'
                % R('government/%s/%s/%s/%d' % (EL.iri_local(key1), hom, sid, i)))
    for i, n in enumerate(lay['form_notes'], 1):
        f.write('  pwglex:formNote %s ;\n'
                % R('formnote/%s/%s/%s/%d' % (EL.iri_local(key1), hom, sid, i)))
    refs = sorted({R('citation/%s' % EL.cite_slug(e['raw_ls']))
                   for e in lay['citation_edges'] if EL.cite_slug(e.get('raw_ls') or '')})
    if refs:
        f.write('  dct:references %s ;\n' % ', '.join(refs))
    for i, s in enumerate(lay['gloss_spans'], 1):
        f.write('  pwglex:glossSpan %s ;\n'
                % R('glossspan/%s/%s/%s/%d' % (EL.iri_local(key1), hom, sid, i)))
    f.write('  pwglex:evidenceGrade gr:%s .\n' % DE_EDITION_GRADE[0])

    for i, g in enumerate(lay['government'], 1):
        giri = R('government/%s/%s/%s/%d' % (EL.iri_local(key1), hom, sid, i))
        f.write('%s a pwglex:Government ;\n' % giri)
        for c in g.get('cases') or []:
            f.write('  pwglex:case %s ;\n' % EL.lit(c))
            if c in LEXINFO_CASE:
                f.write('  lexinfo:case %s ;\n' % LEXINFO_CASE[c])
        f.write('  pwglex:variation %s ;\n' % ('true' if g.get('variation') else 'false'))
        if g.get('connector'):
            f.write('  pwglex:connector %s ;\n' % EL.lit(g.get('connector')))
        f.write('  pwglex:governmentKind %s ;\n' % EL.lit(g.get('kind')))
        f.write('  pwglex:span %s .\n' % EL.lit(g.get('span') or ''))

    for i, n in enumerate(lay['form_notes'], 1):
        niri = R('formnote/%s/%s/%s/%d' % (EL.iri_local(key1), hom, sid, i))
        f.write('%s a pwglex:FormNote ;\n' % niri)
        f.write('  pwglex:case %s ;\n' % EL.lit(n.get('case')))
        if n.get('case') in LEXINFO_CASE:
            f.write('  lexinfo:case %s ;\n' % LEXINFO_CASE[n['case']])
        f.write('  pwglex:formNoteKind %s ;\n' % EL.lit(n.get('kind')))
        f.write('  pwglex:span %s .\n' % EL.lit(n.get('span') or ''))

    for i, s in enumerate(lay['gloss_spans'], 1):
        giri = R('glossspan/%s/%s/%s/%d' % (EL.iri_local(key1), hom, sid, i))
        f.write('%s a pwglex:GlossSpan ;\n' % giri)
        f.write('  rdfs:label %s ;\n' % EL.lit(s.get('span') or '',
                                               lang=s.get('gloss_lang') or 'und'))
        f.write('  pwglex:glossLang %s ;\n' % EL.lit(s.get('gloss_lang')))
        f.write('  pwglex:ruleId %s .\n' % EL.lit(s.get('rule_id')))

    rel = lay['edition_rel'] or {}
    if rel.get('subtype') and rel.get('subtype') != 'base':
        riri = R('editionrel/%s/%s/%s' % (EL.iri_local(key1), hom, sid))
        f.write('%s a vartrans:SenseRelation ;\n' % riri)
        f.write('  vartrans:source %s ;\n' % siri)
        f.write('  vartrans:target %s ;\n' % R('entry/%s/%s/de' % (EL.iri_local(key1), hom)))
        f.write('  vartrans:category %s ;\n' % EL.lit(rel.get('subtype')))
        f.write('  pwglex:relOp %s ;\n' % EL.lit(rel.get('op')))
        f.write('  pwglex:relDirection %s ;\n' % EL.lit(rel.get('direction')))
        f.write('  pwglex:editionLayer %s ;\n' % R('edition/%s' % EL.iri_local(layer)))
        f.write('  pwglex:confidence %s ;\n' % EL.lit(rel.get('confidence') or 'rule'))
        f.write('  rdfs:comment %s .\n' % EL.lit(rel.get('evidence') or ''))
    return siri, lay['citation_edges']


def emit_ttl(entries, args) -> str:
    R = EL.IRI(args.base)
    buf: list[str] = []

    class W:
        def write(self, s):
            buf.append(s)
    f = W()
    f.write('# PWG DE edition graph -- export_de_edition.py (H1629)\n')
    f.write('# base IRI: %s   generated: %s\n' % (args.base, args.generated_at))
    f.write('# DE-only: no Russian text, no review status, no evidence grades '
            'beyond the DE-edition grade.\n\n')
    f.write(EL.prefixes(args.base))
    _ttl_vocab(f, R, args)

    citations: dict[str, dict] = {}
    lemma_seen: set = set()
    for entry in entries:
        key1, hom = entry['key1'], entry['hom']
        lemma_iri = R('lemma/%s' % EL.iri_local(key1))
        entry_iri = R('entry/%s/%s/de' % (EL.iri_local(key1), hom))
        if key1 not in lemma_seen:
            lemma_seen.add(key1)
            f.write('%s a ontolex:Form, lila:Lemma ;\n' % lemma_iri)
            f.write('  ontolex:writtenRep %s ;\n' % EL.lit(key1, lang='sa-Latn-x-slp1'))
            if entry['iast']:
                f.write('  ontolex:writtenRep %s ;\n' % EL.lit(entry['iast'], lang='sa-Latn'))
            f.write('  pwglex:slp1 %s ;\n' % EL.lit(key1))
            f.write('  rdfs:label %s .\n' % EL.lit(entry['iast'] or key1, lang='sa-Latn'))

        blocks = list(numbered_senses(entry))
        sense_iris = [R('sense/%s/%s/%s/%s' % (
            EL.iri_local(key1), hom, EL.iri_local(row.get('layer') or 'unknown'), sid))
            for row, _, sid in blocks]

        f.write('%s a ontolex:LexicalEntry ;\n' % entry_iri)
        f.write('  rdfs:label %s ;\n' % EL.lit(entry['iast'] or key1, lang='sa-Latn'))
        f.write('  dct:language "de" ;\n')
        f.write('  dct:isPartOf %s ;\n' % R('lexicon/pwg-de-edition'))
        f.write('  ontolex:canonicalForm %s ;\n' % lemma_iri)
        f.write('  pwglex:homonym %s ;\n' % EL.lit(hom))
        f.write('  ontolex:sense %s .\n' % ', '.join(sense_iris))

        for row, lay, sid in blocks:
            _, edges = _ttl_sense(f, R, entry, row, lay, sid)
            for e in edges:
                slug = EL.cite_slug(e.get('raw_ls') or '')
                if slug:
                    citations[slug] = e
        f.write('\n')

    f.write('# --- citations ------------------------------------------------\n')
    for slug in sorted(citations):
        e = citations[slug]
        f.write('%s a pwglex:Citation, prov:Entity ;\n' % R('citation/%s' % slug))
        f.write('  rdfs:label %s ;\n' % EL.lit(e.get('raw_ls') or ''))
        if e.get('siglum'):
            f.write('  pwglex:sourceSigla %s ;\n' % EL.lit(e.get('siglum')))
        if e.get('page'):
            f.write('  pwglex:locus %s ;\n' % EL.lit(e.get('page')))
        if e.get('work_id'):
            f.write('  pwglex:workId %s ;\n' % EL.lit(e.get('work_id')))
        if e.get('work_name'):
            f.write('  pwglex:workName %s ;\n' % EL.lit(e.get('work_name')))
        if e.get('renou'):
            f.write('  pwglex:renouStratum %s ;\n' % EL.lit(e.get('renou')))
        f.write('  pwglex:bibOk %s ;\n' % ('true' if e.get('bib_ok') else 'false'))
        f.write('  pwglex:resolverStatus %s .\n' % EL.lit(e.get('resolver_status')))
    return ''.join(buf)


# --------------------------------------------------------------------------- #
# TEI Lex-0 (XML)
# --------------------------------------------------------------------------- #
def xesc(s) -> str:
    return (str(s if s is not None else '')
            .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def xml_id(s) -> str:
    """xml:id must be an XML Name: start with a letter/underscore, no colons."""
    s = re.sub(r'[^0-9A-Za-z_.-]+', '-', str(s or 'x')).strip('-') or 'x'
    return s if re.match(r'^[A-Za-z_]', s) else '_' + s


def plain(s) -> str:
    """Markup-free rendering of a source span, for TEI element content.

    The raw span (tags and all) stays in the Turtle ``pwglex:span`` as
    provenance; TEI element *content* is what a reader sees, so it carries the
    stripped form and the machine value lives in ``@norm``.
    """
    s = re.sub(r'<[^>]+>', '', str(s or ''))
    return re.sub(r'\s+', ' ', s).strip()


def _tei_sense(out, entry, row, lay, sid, bibl_ids, indent='      '):
    key1, hom = entry['key1'], entry['hom']
    layer = row.get('layer') or 'unknown'
    definition, equivalents, examples = sense_text(row.get('de'))
    sense_id = xml_id('sense-%s-%s-%s-%s' % (key1, hom, layer, sid))
    i, i2 = indent, indent + '  '
    out.append('%s<sense xml:id="%s" n="%s" source="#edition-%s">'
               % (i, sense_id, xesc(sid), xesc(layer)))
    out.append('%s<def xml:lang="de">%s</def>' % (i2, xesc(definition)))
    for g in equivalents:
        out.append('%s<gloss xml:lang="de">%s</gloss>' % (i2, xesc(g)))
    for s in lay['gloss_spans']:
        out.append('%s<gloss xml:lang="%s" type="sourceGloss" subtype="%s">%s</gloss>'
                   % (i2, xesc(s.get('gloss_lang') or 'und'), xesc(s.get('rule_id')),
                      xesc(plain(s.get('span')))))

    gram = []
    for g in lay['government']:
        for c in g.get('cases') or []:
            gram.append('%s  <gram type="government" subtype="%s" norm="%s">%s</gram>'
                        % (i2, xesc(g.get('kind')), xesc(c),
                           xesc(plain(g.get('span')) or c)))
        if g.get('variation'):
            gram.append('%s  <note type="governmentVariation">%s</note>'
                        % (i2, xesc(g.get('connector') or 'variation')))
    for n in lay['form_notes']:
        gram.append('%s  <gram type="case" norm="%s">%s</gram>'
                    % (i2, xesc(n.get('case')),
                       xesc(plain(n.get('span')) or n.get('case'))))
    if gram:
        out.append('%s<gramGrp>' % i2)
        out.extend(gram)
        out.append('%s</gramGrp>' % i2)

    for ex in examples:
        out.append('%s<cit type="example" xml:lang="sa-Latn-x-slp1">'
                   '<quote>%s</quote></cit>' % (i2, xesc(ex)))
    for e in lay['citation_edges']:
        slug = EL.cite_slug(e.get('raw_ls') or '')
        if not slug:
            continue
        out.append('%s<cit type="citation">' % i2)
        out.append('%s  <bibl corresp="#%s" ana="%s">'
                   % (i2, bibl_ids[slug], xesc(e.get('resolver_status'))))
        if e.get('siglum'):
            out.append('%s    <abbr type="siglum">%s</abbr>' % (i2, xesc(e.get('siglum'))))
        if e.get('page'):
            out.append('%s    <biblScope unit="locus">%s</biblScope>' % (i2, xesc(e.get('page'))))
        out.append('%s  </bibl>' % i2)
        out.append('%s</cit>' % i2)

    rel = lay['edition_rel'] or {}
    if rel.get('subtype') and rel.get('subtype') != 'base':
        out.append('%s<xr type="editionRel" subtype="%s">' % (i2, xesc(rel.get('subtype'))))
        out.append('%s  <ref target="#%s">%s</ref>'
                   % (i2, xml_id('entry-%s-%s' % (key1, hom)), xesc(rel.get('direction'))))
        if rel.get('evidence'):
            # `relEvidence`, not `evidence`: the bare name is a store field
            # carrying RU-side judge evidence and is on the forbidden list.
            out.append('%s  <note type="relEvidence">%s</note>'
                       % (i2, xesc(rel.get('evidence'))))
        out.append('%s</xr>' % i2)
    out.append('%s</sense>' % i)


def collect_citations(entries) -> dict:
    """slug -> citation edge, across every sense of every entry (dedup, sorted)."""
    cites: dict[str, dict] = {}
    for entry in entries:
        for _, lay, _ in numbered_senses(entry):
            for e in lay['citation_edges']:
                slug = EL.cite_slug(e.get('raw_ls') or '')
                if slug:
                    cites[slug] = e
    return cites


def emit_tei(entries, args) -> str:
    # Bibliography first: every <bibl @corresp> in the body must resolve to a
    # real xml:id, so the ids are assigned up front over the sorted slug set
    # (short sequential ids, not the hex-escaped IRI slug).
    citations = collect_citations(entries)
    bibl_ids = {slug: 'bibl-%03d' % i
                for i, slug in enumerate(sorted(citations), 1)}

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<!-- PWG DE edition graph, TEI Lex-0 profile, export_de_edition.py (H1629). '
           'DE-only; no Russian text. -->',
           '<TEI xmlns="http://www.tei-c.org/ns/1.0">',
           '  <teiHeader>',
           '    <fileDesc>',
           '      <titleStmt><title>PWG German edition graph (PWG/PW/SCH/PWKVN/NWS)</title></titleStmt>',
           '      <publicationStmt>',
           '        <availability status="free"><licence '
           'target="https://creativecommons.org/publicdomain/mark/1.0/">'
           'Public Domain Mark 1.0 (19th-c. German editions)</licence></availability>',
           '        <date when="%s"/>' % xesc(args.generated_at),
           '      </publicationStmt>',
           '      <sourceDesc>',
           '        <p>German edition text from the Cologne PWG family; structural layers '
           'derived by RussianTranslation/src (H1624 G1-G6).</p>',
           '        <listBibl>']
    for layer, (label, posture) in sorted(LAYERS.items()):
        out.append('          <bibl xml:id="edition-%s" ana="%s">%s</bibl>'
                   % (xesc(layer), xesc(posture), xesc(label)))
    out += ['        </listBibl>',
            '      </sourceDesc>',
            '    </fileDesc>',
            '    <encodingDesc>',
            '      <projectDesc><p>TEI Lex-0 export profile; @type values '
            'government/case/editionRel/sourceGloss are project extensions documented in '
            'DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md.</p></projectDesc>',
            '    </encodingDesc>',
            '  </teiHeader>',
            '  <text>',
            '  <body>']

    for entry in entries:
        key1, hom = entry['key1'], entry['hom']
        out.append('    <entry xml:id="%s">' % xml_id('entry-%s-%s' % (key1, hom)))
        out.append('      <form type="lemma">')
        out.append('        <orth xml:lang="sa-Latn-x-slp1">%s</orth>' % xesc(key1))
        if entry['iast']:
            out.append('        <orth xml:lang="sa-Latn">%s</orth>' % xesc(entry['iast']))
        out.append('      </form>')
        for row, lay, sid in numbered_senses(entry):
            _tei_sense(out, entry, row, lay, sid, bibl_ids)
        out.append('    </entry>')
    out.append('  </body>')

    out.append('  <back>')
    out.append('    <div type="bibliography">')
    out.append('      <listBibl xml:id="cited-works">')
    for slug in sorted(citations):
        e = citations[slug]
        bits = []
        if e.get('siglum'):
            bits.append('<abbr type="siglum">%s</abbr>' % xesc(e['siglum']))
        if e.get('work_name'):
            bits.append('<title>%s</title>' % xesc(e['work_name']))
        if e.get('renou'):
            bits.append('<note type="renouStratum">%s</note>' % xesc(e['renou']))
        out.append('        <bibl xml:id="%s" ana="%s">%s</bibl>'
                   % (bibl_ids[slug], xesc(e.get('resolver_status')),
                      ''.join(bits) or xesc(e.get('raw_ls') or '')))
    out += ['      </listBibl>', '    </div>', '  </back>', '  </text>', '</TEI>', '']
    return '\n'.join(out)


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def build(args):
    rows_in = list(iter_rows(args.rows, limit=args.limit, keys=args.keyset))
    clean, quarantined, sanitized = [], [], []
    for r in rows_in:
        bad = de_impurity(r)
        blocking = [b for b in bad if b in BLOCKING_DE_FIELDS]
        if blocking:
            quarantined.append({'key1': r.get('key1'), 'subcard': r.get('subcard'),
                                'fields': blocking})
            continue
        if bad:
            # sense_tag only: the German is intact, the structural label is not.
            sanitized.append({'key1': r.get('key1'), 'subcard': r.get('subcard'),
                              'fields': bad, 'slug': sense_tag_slug(r.get('sense_tag'))})
        clean.append(r)
    if (quarantined or sanitized) and args.strict:
        raise SystemExit(
            'PURITY: %d quarantined + %d sanitized row(s) and --strict set: %s'
            % (len(quarantined), len(sanitized),
               json.dumps({'quarantined': quarantined, 'sanitized': sanitized},
                          ensure_ascii=False)))
    entries = group_entries(clean)
    ttl = emit_ttl(entries, args)
    tei = emit_tei(entries, args)
    assert_rights_safe(ttl, 'pwg_de_edition.ttl')
    assert_rights_safe(tei, 'pwg_de_edition.tei.xml')

    counts = {'government': 0, 'form_notes': 0, 'citation_edges': 0,
              'gloss_spans': 0, 'edition_rel': 0}
    layers_seen: dict[str, int] = {}
    for e in entries:
        for row, lay, _ in numbered_senses(e):
            counts['government'] += len(lay['government'])
            counts['form_notes'] += len(lay['form_notes'])
            counts['citation_edges'] += len(lay['citation_edges'])
            counts['gloss_spans'] += len(lay['gloss_spans'])
            if (lay['edition_rel'] or {}).get('subtype') not in (None, 'base'):
                counts['edition_rel'] += 1
            lyr = row.get('layer') or 'unknown'
            layers_seen[lyr] = layers_seen.get(lyr, 0) + 1
    manifest = {
        'profile': 'pwg_de_edition.v1',
        'handoff': 'H1629',
        'generated_at': args.generated_at,
        'base_iri': args.base,
        'source_rows': len(rows_in),
        'exported_rows': sum(len(e['senses']) for e in entries),
        'entries': len(entries),
        'quarantined_rows': len(quarantined),
        'quarantined': quarantined,
        'sanitized_tag_rows': len(sanitized),
        'sanitized_tags': sanitized,
        'layer_rows': dict(sorted(layers_seen.items())),
        'layer_counts': counts,
        'rights': {'de_only': True, 'allowlist': list(DE_FIELDS),
                   'forbidden': list(FORBIDDEN_FIELDS)},
    }
    return ttl, tei, manifest


def cmd_export(args):
    ttl, tei, manifest = build(args)
    os.makedirs(args.out_dir, exist_ok=True)
    paths = {
        'ttl': os.path.join(args.out_dir, 'pwg_de_edition.ttl'),
        'tei': os.path.join(args.out_dir, 'pwg_de_edition.tei.xml'),
        'manifest': os.path.join(args.out_dir, 'pwg_de_edition.manifest.json'),
    }
    with open(paths['ttl'], 'w', encoding='utf-8', newline='\n') as f:
        f.write(ttl)
    with open(paths['tei'], 'w', encoding='utf-8', newline='\n') as f:
        f.write(tei)
    with open(paths['manifest'], 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    print('DE edition graph: %d entries / %d senses (%d quarantined)'
          % (manifest['entries'], manifest['exported_rows'], manifest['quarantined_rows']))
    print('  OntoLex  -> %s' % paths['ttl'])
    print('  TEI Lex-0-> %s' % paths['tei'])
    print('  manifest -> %s' % paths['manifest'])
    return manifest


# --------------------------------------------------------------------------- #
# Selftest
# --------------------------------------------------------------------------- #
def selftest():
    import xml.etree.ElementTree as ET
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    class A:
        pass
    args = A()
    args.rows = DEFAULT_ROWS
    args.base = EL.DEFAULT_BASE
    args.generated_at = '2026-07-26'
    args.limit = None
    args.keyset = None
    args.strict = False

    # ---- 1. rights allowlist drops everything non-DE -----------------------
    dirty = {'key1': 'jIv', 'de': 'leben', 'ru': 'жить', 'review_status': 'approved',
             'reviewer': 'MG', 'provenance': {'model_version': 'x'}, 'layer': 'pwg',
             'subcard': 'j_iv~~h0_00_pwg00', 'sense_tag': '1'}
    proj = de_only(dirty)
    check(set(proj) == set(DE_FIELDS), 'allowlist keys: %r' % sorted(proj))
    for bad in FORBIDDEN_FIELDS:
        check(bad not in proj, 'forbidden field leaked: %s' % bad)

    # ---- 2. purity guard fires on real contamination -----------------------
    check(de_impurity({'de': '{%Opfer%} in {#sarva#} и {#havirhuti#}'}) == ['de'],
          'Cyrillic in de must be flagged')
    check(de_impurity({'sense_tag': 'c) с dat.'}) == ['sense_tag'],
          'Cyrillic in sense_tag must be flagged')
    check(de_impurity({'de': '{%Opfer%} in {#sarva#} und {#havirhuti#}'}) == [],
          'clean German must pass')

    # ---- 3. layer extraction on a synthetic DE sense -----------------------
    row = {'key1': 'jIv', 'iast': 'jīv', 'subcard': 'j_iv~~h0_zz_pw',
           'sense_tag': '1', 'layer': 'pw',
           'de': '<div n="1">— 1) {%sich freuen%} (<ab>Instr.</ab>) und '
                 '{%erquicken%} (<ab>Nom.</ab>) <ls>ṚV. 1,1,1</ls>: '
                 '{#jIvati#} <ls n="MBH.">3,50</ls>.'}
    lay = sense_layers(row)
    check(len(lay['government']) == 1 and lay['government'][0]['cases'] == ['instr'],
          'government: %r' % lay['government'])
    check([n['case'] for n in lay['form_notes']] == ['nom'],
          'form_notes: %r' % lay['form_notes'])
    check([e['siglum'] for e in lay['citation_edges']] == ['ṚV', 'MBH'],
          'citation_edges: %r' % lay['citation_edges'])
    # H3752: compared on the BASE label. This fixture is a lone PW row with no
    # PWG skeleton beside it, so nothing can be placed and the fallback classify
    # returns `restate_unplaced` — correctly. What this check is about is the
    # KIND of relation, and `base_subtype` is exactly the seam for that.
    check(base_subtype(lay['edition_rel'].get('subtype'))
          in ('restate', 'pw_correct', 'derived_sense', 'unknown'),
          'edition_rel subtype: %r' % lay['edition_rel'])
    definition, equivalents, examples = sense_text(row['de'])
    check(equivalents == ['sich freuen', 'erquicken'], 'equivalents: %r' % equivalents)
    check(examples == ['jIvati'], 'examples: %r' % examples)

    # ---- 4. sense_tag slug never carries prose / Cyrillic ------------------
    slug = sense_tag_slug('c) с dat. лица')
    check(not CYRILLIC.search(slug), 'slug must strip Cyrillic: %r' % slug)
    check(re.fullmatch(r'[0-9A-Za-z_.-]+', slug), 'slug charset: %r' % slug)
    check(sense_tag_slug('sam- 1') == 'sam-1', 'slug: %r' % sense_tag_slug('sam- 1'))
    check(sense_tag_slug('NWS-1') == 'NWS-1', 'slug: %r' % sense_tag_slug('NWS-1'))
    check(xml_id('1') == '_1', 'xml:id must start with a letter/underscore')

    # ---- 4b. edition_rel `evidence` is scrubbed (H1635) --------------------
    # The classifier interpolates the RAW sense_tag into `evidence`, which both
    # emitters write verbatim. The fixture's sanitizable-tag row happens not to
    # take an evidence-bearing classification branch, so the leak survived the
    # fixture round-trip and only surfaced on a full-store export. Reproduce it
    # directly rather than relying on the fixture to wander onto the branch.
    check(scrub_cyrillic('sense_tag=%r' % 'Mit <div n="p"> — корригенда')
          == 'sense_tag=\'Mit <div n="p"> — %s\'' % RU_ELIDED,
          'scrub_cyrillic collapses a run to one marker: %r'
          % scrub_cyrillic('sense_tag=%r' % 'Mit <div n="p"> — корригенда'))
    check(scrub_cyrillic('плохой тег') == RU_ELIDED,
          'multi-word Cyrillic run collapses to a single marker: %r'
          % scrub_cyrillic('плохой тег'))
    leaky = {'key1': 'test', 'layer': 'pw', 'subcard': 'PW 1',
             'sense_tag': 'Mit <div n="p"> — корригенда',
             'de': 'ein deutscher Text {%Gloss%}'}
    ev = sense_layers(leaky)['edition_rel'].get('evidence') or ''
    check('sense_tag' in ev,
          'guard row must reach the evidence-bearing branch, got %r' % ev)
    check(not CYRILLIC.search(ev),
          'edition_rel evidence must carry no Cyrillic: %r' % ev)

    # ---- 5. fixture round-trip: both serializations -----------------------
    check(os.path.exists(args.rows), 'fixture present: %s' % args.rows)
    ttl, tei, manifest = build(args)
    check(manifest['entries'] >= 4, 'entries: %r' % manifest['entries'])
    check(manifest['quarantined_rows'] == 2,
          'fixture must carry exactly 2 Cyrillic-in-`de` guard rows, got %r'
          % manifest['quarantined_rows'])
    check(manifest['sanitized_tag_rows'] == 1,
          'fixture must carry exactly 1 Cyrillic-sense_tag guard row, got %r'
          % manifest['sanitized_tag_rows'])
    # every layer this profile claims to export must be exercised by the fixture,
    # else a regression in one extractor would ship silently
    for layer in ('government', 'form_notes', 'citation_edges', 'gloss_spans',
                  'edition_rel'):
        check(manifest['layer_counts'][layer] > 0,
              'fixture exercises no %s -- layer would regress undetected' % layer)
    # and every edition layer must be represented
    check(set(manifest['layer_rows']) == set(LAYERS),
          'fixture edition layers: %r' % sorted(manifest['layer_rows']))

    # quarantined rows are really absent from both artifacts; the sanitized-tag
    # row's German IS present (only its label was reduced to an ASCII skeleton)
    check('havirhuti' not in ttl and 'havirhuti' not in tei,
          'quarantined row leaked into an artifact')
    check('parihAra' not in ttl and 'parihAra' not in tei,
          'second quarantined row leaked into an artifact')

    # ---- 6. OntoLex shape --------------------------------------------------
    for needed in ('ontolex:LexicalEntry', 'ontolex:LexicalSense', 'lime:Lexicon',
                   'pwglex:Government', 'pwglex:Citation', 'vartrans:SenseRelation',
                   'lexinfo:case', 'prov:Activity'):
        check(needed in ttl, 'TTL missing %s' % needed)
    check(ttl.count('a ontolex:LexicalEntry') == manifest['entries'],
          'TTL entry count mismatch')

    # ---- 7. TEI Lex-0 shape + well-formedness ------------------------------
    root = ET.fromstring(tei.encode('utf-8'))   # bytes: the XML decl names an encoding
    ns = {'t': 'http://www.tei-c.org/ns/1.0'}
    entries = root.findall('.//t:entry', ns)
    check(len(entries) == manifest['entries'], 'TEI entry count: %d' % len(entries))
    check(root.find('.//t:form[@type="lemma"]/t:orth', ns) is not None, 'TEI lemma orth')
    check(root.find('.//t:sense/t:def', ns) is not None, 'TEI sense def')
    check(root.find('.//t:gramGrp/t:gram[@type="government"]', ns) is not None,
          'TEI government gram')
    check(root.find('.//t:cit[@type="citation"]/t:bibl', ns) is not None, 'TEI bibl')
    check(root.find('.//t:xr[@type="editionRel"]', ns) is not None, 'TEI editionRel xr')
    ids = [e.get('{http://www.w3.org/XML/1998/namespace}id') for e in root.iter()]
    ids = [i for i in ids if i]
    check(len(ids) == len(set(ids)), 'duplicate xml:id in TEI')
    # every pointer resolves: no dangling @corresp / @source / @target
    idset = set(ids)
    dangling = []
    for el in root.iter():
        for att in ('corresp', 'source', 'target'):
            v = el.get(att)
            if v and v.startswith('#') and v[1:] not in idset:
                dangling.append((att, v))
    check(not dangling, 'dangling TEI pointers: %r' % dangling[:5])
    check(root.find('.//t:back//t:listBibl/t:bibl', ns) is not None,
          'TEI back matter must carry the cited-works listBibl')

    # ---- 8. determinism ----------------------------------------------------
    ttl2, tei2, _ = build(args)
    check(ttl == ttl2 and tei == tei2, 'export is not byte-deterministic')

    # ---- 9. rights guard: fires on real leaks, not on lookalikes -----------
    for leak in ('skos:definition "жить"@ru',            # Cyrillic
                 '  "review_status": "approved",',        # JSON key
                 '  pwglex:ru "..." ;',                   # Turtle predicate
                 '<ru>...</ru>'):                         # XML element
        try:
            assert_rights_safe(leak, 'probe')
            fails.append('assert_rights_safe did not fire on %r' % leak)
        except SystemExit:
            pass
    for ok in ('pwglex:glossLang "en" ;',                 # legitimate value
               'pwglex:evidenceGrade gr:pwg-de-edition .',
               '<gloss xml:lang="en">light</gloss>'):
        try:
            assert_rights_safe(ok, 'probe')
        except SystemExit as exc:
            fails.append('assert_rights_safe false positive on %r: %s' % (ok, exc))

    if fails:
        for m in fails:
            print('FAIL:', m, file=sys.stderr)
        sys.exit(1)
    print('export_de_edition --selftest: OK (%d entries, %d senses, %d quarantined)'
          % (manifest['entries'], manifest['exported_rows'], manifest['quarantined_rows']))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', nargs='?', default='export', choices=['export'])
    ap.add_argument('--rows', default=DEFAULT_ROWS,
                    help='JSONL of DE sense rows (fixture by default)')
    ap.add_argument('--store', default=None,
                    help='read the translated store instead (DE allowlist applied)')
    ap.add_argument('--out-dir', default=DEFAULT_OUT)
    ap.add_argument('--base-iri', dest='base', default=EL.DEFAULT_BASE)
    ap.add_argument('--generated-at', default=None,
                    help='ISO date stamped into provenance (fixed value => byte-stable)')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--keys', default=None, help='comma-separated key1 whitelist')
    ap.add_argument('--strict', action='store_true',
                    help='fail on a contaminated row instead of quarantining it')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.store:
        args.rows = args.store
    if not args.base.endswith('/'):
        args.base += '/'
    args.keyset = ({k.strip() for k in args.keys.split(',') if k.strip()}
                   if args.keys else None)
    if args.generated_at is None:
        import datetime
        args.generated_at = datetime.date.today().isoformat()
    cmd_export(args)


if __name__ == '__main__':
    main()
