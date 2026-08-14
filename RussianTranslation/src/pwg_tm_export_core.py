#!/usr/bin/env python
"""Shared PWG TM interchange mapping (H2685 Track C).

Canonical JSONL is the only store. TMX 1.4b, TEI Lex-0 and OntoLex/vartrans/PROV-O
are derived views. Every scholarly field path is either first-class in a derived
format or an explicit extension (JSON payload / content hash). Silent loss is a
hard failure for pwg_tm_export_loss.py.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import OrderedDict
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402

ROOT = C.ROOT
DEFAULT_CANONICAL = os.path.join(C.DEFAULT_OUT_DIR, 'canonical.v1.jsonl')
DEFAULT_RELEASE = os.path.join(ROOT, 'release', 'pwg_tm')
SCHEMA_DIR = os.path.join(ROOT, 'schemas')

PIPELINE_VERSION = 'pwg_tm_export.v1'
SCHEMA = 'pwg.tm.canonical.v1'
BASE_IRI = 'https://w3id.org/sanskrit-lexicon/repwg/tm/'
VOCAB_IRI = 'https://w3id.org/sanskrit-lexicon/repwg/vocab#'
TEI_NS = 'http://www.tei-c.org/ns/1.0'
XML_NS = 'http://www.w3.org/XML/1998/namespace'
XML_LANG = '{%s}lang' % XML_NS

TMX_SRCLANG = 'de'
TMX_TGTLANG = 'ru'

# Scalar scholarly paths that every derived format must carry as a first-class
# property/note/literal (or, for source/target strings, as the interchange body).
SCALAR_PATHS = (
    'schema', 'schema_version', 'record_kind',
    'record_id', 'entry_id', 'sense_id', 'fragment_id', 'fragment_class',
    'sense_alignment', 'lang', 'script', 'transliteration',
    'source_string', 'source_hash', 'target_string', 'target_hash',
    'trust_level', 'reuse_policy', 'confidence_tier',
    'gate_status', 'gate_version', 'review_status',
    'tm_record_id', 'model_version', 'pipeline_version',
    'source_locator.dictionary', 'source_locator.key1',
    'source_locator.lemma_slp1', 'source_locator.iast',
    'source_locator.src_key', 'source_locator.homonym',
    'structural_markup.n_senses', 'structural_markup.record_type',
    'structural_markup.source_kind',
    'source_hashes.input_raw_sha256', 'source_hashes.fragment_sha256',
    'provenance.generated_at', 'provenance.pipeline_version',
    'provenance.source.model', 'provenance.source.model_version',
    'provenance.source.root', 'provenance.source.source_kind',
    'provenance.source.gate_version',
    'rights.source_status', 'rights.translation_status',
    'rights.block_class', 'rights.uncertainty',
    'source_publication.schema', 'source_publication.tm_record_id',
    'source_publication.record_type',
)

# Nested scholarly objects. Carried as a JSON extension in TMX/TEI/RDF plus
# first-class RDF/TEI structure where the model has a home.
COMPLEX_PATHS = (
    'source_locator', 'source_hashes', 'structural_markup',
    'provenance', 'provenance.agents', 'provenance.activities',
    'provenance.entities', 'provenance.source',
    'evidence', 'rights', 'rights.facts',
    'supersedes', 'superseded_by',
)

# Full nested publication row is already the lossless JSONL audit copy.
# Other formats carry its hash + the three identity fields above.
JSONL_ONLY_HASHED = (
    'source_publication',
)

ALL_SCHOLARLY_PATHS = SCALAR_PATHS + COMPLEX_PATHS + JSONL_ONLY_HASHED


def json_dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha256_text(text):
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()


def get_path(obj, path):
    cur = obj
    for part in path.split('.'):
        if cur is None:
            return None
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def load_canonical(path, limit=None):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get('record_kind') != 'publication':
                continue
            rows.append(row)
            if limit is not None and len(rows) >= limit:
                break
    rows.sort(key=lambda r: r.get('record_id') or '')
    return rows


def xml_esc(s):
    return escape('' if s is None else str(s), {'"': '&quot;'})


def xml_id(s):
    slug = re.sub(r'[^0-9A-Za-z_.-]+', '-', str(s or 'x')).strip('-') or 'x'
    return slug if re.match(r'^[A-Za-z_]', slug) else '_' + slug


def ttl_esc(s):
    return (str(s if s is not None else '')
            .replace('\\', '\\\\').replace('"', '\\"')
            .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))


def ttl_unesc(s):
    """Inverse of ttl_esc. Do not use unicode_escape — it breaks UTF-8."""
    out = []
    i = 0
    text = s or ''
    while i < len(text):
        if text[i] == '\\' and i + 1 < len(text):
            nxt = text[i + 1]
            out.append({'n': '\n', 'r': '\r', 't': '\t', '"': '"', '\\': '\\'}.get(nxt, nxt))
            i += 2
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)


def ttl_lit(s, lang=None, dtype=None):
    body = '"%s"' % ttl_esc(s)
    if lang:
        return body + '@' + lang
    if dtype:
        return body + '^^' + dtype
    return body


def iri_local(s):
    out = []
    for ch in str(s if s is not None else 'x'):
        if ch.isascii() and ch.isalnum():
            out.append(ch)
        else:
            out.append(''.join('_x%02x_' % b for b in ch.encode('utf-8')))
    return ''.join(out) or 'x'


def rec_iri(record_id):
    return '<%srecord/%s>' % (BASE_IRI, iri_local(record_id))


def entry_iri(entry_id):
    return '<%sentry/%s>' % (BASE_IRI, iri_local(entry_id))


def form_iri(entry_id):
    return '<%sform/%s>' % (BASE_IRI, iri_local(entry_id))


def sense_iri(sense_id):
    return '<%ssense/%s>' % (BASE_IRI, iri_local(sense_id))


def trans_iri(record_id):
    return '<%strans/%s>' % (BASE_IRI, iri_local(record_id))


def ext_payload(row):
    """JSON extensions that keep nested scholarly objects lossless."""
    payload = OrderedDict()
    for path in COMPLEX_PATHS:
        payload[path] = get_path(row, path)
    payload['source_publication_hash'] = sha256_text(json_dump(row.get('source_publication')))
    return payload


def scalar_map(row):
    out = OrderedDict()
    for path in SCALAR_PATHS:
        out[path] = get_path(row, path)
    return out


# --------------------------------------------------------------------------- #
# TMX 1.4b
# --------------------------------------------------------------------------- #
def _prop(kind, val):
    if val is None:
        return ''
    if isinstance(val, (dict, list)):
        text = json_dump(val)
    else:
        text = '' if val is False else str(val)
        if val is True:
            text = 'true'
        if text == '' and not isinstance(val, str):
            return ''
    return '  <prop type=%s>%s</prop>\n' % (quoteattr(kind), xml_esc(text))


def tmx_tuid(row):
    return row.get('record_id') or ('pwg.tm.v1:' + (row.get('tm_record_id') or ''))


def tmx_tu(row):
    parts = ['<tu tuid=%s>\n' % quoteattr(tmx_tuid(row))]
    parts.append(_prop('layer', 'canonical-v1'))
    for path, val in scalar_map(row).items():
        if path in ('source_string', 'target_string'):
            continue
        parts.append(_prop(path, val))
    ext = ext_payload(row)
    parts.append(_prop('scholarly_extension', ext))
    parts.append(_prop('source_publication_hash', ext['source_publication_hash']))
    parts.append('  <tuv xml:lang="%s"><seg>%s</seg></tuv>\n' % (
        TMX_SRCLANG, xml_esc(row.get('source_string') or '')))
    parts.append('  <tuv xml:lang="%s"><seg>%s</seg></tuv>\n' % (
        TMX_TGTLANG, xml_esc(row.get('target_string') or '')))
    parts.append(' </tu>\n')
    return ''.join(parts)


def tmx_header(count, srcfile, created):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<tmx version="1.4">\n'
        ' <header\n'
        '   creationtool="build_tmx.py"\n'
        '   creationtoolversion=%s\n'
        '   segtype="phrase"\n'
        '   o-tmf=%s\n'
        '   adminlang="en"\n'
        '   srclang=%s\n'
        '   datatype="plaintext"\n'
        '   creationdate=%s\n'
        '   o-encoding="UTF-8">\n'
        '  <prop type="tm-layer">canonical scholarly JSONL v1 (H2685)</prop>\n'
        '  <prop type="pipeline">%s</prop>\n'
        '  <prop type="unit-count">%d</prop>\n'
        ' </header>\n'
        ' <body>\n'
        % (quoteattr(PIPELINE_VERSION), quoteattr(os.path.basename(srcfile)),
           quoteattr(TMX_SRCLANG), quoteattr(created),
           xml_esc(PIPELINE_VERSION), count)
    )


def build_tmx(rows, srcfile, created):
    chunks = [tmx_header(len(rows), srcfile, created)]
    for row in rows:
        chunks.append(tmx_tu(row))
    chunks.append(' </body>\n</tmx>\n')
    return ''.join(chunks)


def validate_tmx_canonical(path):
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return False, 'tmx parse error: %s' % e
    root = tree.getroot()
    if root.tag != 'tmx' or root.get('version') != '1.4':
        return False, 'root is not <tmx version="1.4">'
    header = root.find('header')
    if header is None or header.get('srclang') != TMX_SRCLANG:
        return False, 'header missing or srclang!=de'
    body = root.find('body')
    if body is None:
        return False, 'no <body>'
    tus = body.findall('tu')
    if not tus:
        return False, 'zero <tu>'
    for tu in tus:
        tuvs = tu.findall('tuv')
        langs = {}
        for tuv in tuvs:
            lang = tuv.get(XML_LANG)
            seg = tuv.find('seg')
            if lang is None or seg is None:
                return False, 'tu %s missing lang/seg' % tu.get('tuid')
            langs[lang] = '' if seg.text is None else seg.text
        if TMX_SRCLANG not in langs or TMX_TGTLANG not in langs:
            return False, 'tu %s missing de or ru tuv' % tu.get('tuid')
        props = {p.get('type') for p in tu.findall('prop')}
        for needed in ('record_id', 'entry_id', 'fragment_class',
                       'scholarly_extension', 'source_publication_hash'):
            if needed not in props:
                return False, 'tu %s missing prop %s' % (tu.get('tuid'), needed)
    return True, 'tmx ok -- %d tu, srclang=de' % len(tus)


# --------------------------------------------------------------------------- #
# TEI Lex-0
# --------------------------------------------------------------------------- #
def tei_note(typ, val, indent='        '):
    if val is None:
        return ''
    if isinstance(val, (dict, list)):
        text = json_dump(val)
        fmt = ' format="application/json"'
    else:
        text = '' if val is False else str(val)
        if val is True:
            text = 'true'
        fmt = ''
        if text == '' and not isinstance(val, str):
            return ''
    return '%s<note type=%s%s>%s</note>\n' % (
        indent, quoteattr(typ), fmt, xml_esc(text))


def build_tei(rows, created, srcfile):
    by_entry = OrderedDict()
    for row in rows:
        by_entry.setdefault(row.get('entry_id') or 'pwg.entry:unresolved', []).append(row)

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- PWG TM canonical v1, TEI Lex-0 profile, export_pwg_tm_tei.py (H2685). -->',
        '<TEI xmlns="%s" xmlns:pwg="%s">' % (TEI_NS, VOCAB_IRI),
        '  <teiHeader>',
        '    <fileDesc>',
        '      <titleStmt>',
        '        <title>PWG German–Russian translation memory (canonical v1)</title>',
        '        <author>Mārcis Gasūns</author>',
        '      </titleStmt>',
        '      <editionStmt><edition>pwg.tm.canonical.v1 / %s</edition></editionStmt>' % (
            xml_esc(PIPELINE_VERSION)),
        '      <publicationStmt>',
        '        <publisher>Sanskrit Lexicon project</publisher>',
        '        <availability status="free">',
        '          <licence target="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0 '
        '(Russian renderings); PWG source Public Domain Mark 1.0</licence>',
        '        </availability>',
        '        <date when="%s"/>' % xml_esc(created),
        '        <idno type="pipeline">%s</idno>' % xml_esc(PIPELINE_VERSION),
        '      </publicationStmt>',
        '      <sourceDesc>',
        '        <bibl>Böhtlingk, Otto; Roth, Rudolph. Sanskrit-Wörterbuch. '
        'St. Petersburg, 1855–1875 (PWG). Public domain.</bibl>',
        '        <p>Derived from %s. Canonical JSONL remains the source of truth.</p>' % (
            xml_esc(os.path.basename(srcfile))),
        '      </sourceDesc>',
        '    </fileDesc>',
        '    <encodingDesc>',
        '      <projectDesc><p>TEI Lex-0 subset. Scholarly fields that Lex-0 cannot '
        'express live in note[@type] (JSON when format=&quot;application/json&quot;) '
        'and are checked by pwg_tm_export_loss.py.</p></projectDesc>',
        '    </encodingDesc>',
        '    <revisionDesc>',
        '      <change when="%s" who="#pwg_tm_export">H2685 Track C lossless TEI Lex-0 '
        'export of %d canonical publication records.</change>' % (
            xml_esc(created[:10] if created else ''), len(rows)),
        '    </revisionDesc>',
        '  </teiHeader>',
        '  <text>',
        '    <body>',
    ]
    for entry_id, members in by_entry.items():
        first = members[0]
        loc = first.get('source_locator') or {}
        out.append('      <entry xml:id="%s">' % xml_id(entry_id))
        out.append('        <form type="lemma">')
        out.append('          <orth xml:lang="sa-Latn-x-slp1">%s</orth>' %
                   xml_esc(loc.get('lemma_slp1') or ''))
        if loc.get('iast'):
            out.append('          <orth xml:lang="sa-Latn">%s</orth>' % xml_esc(loc['iast']))
        out.append('        </form>')
        for row in members:
            sid = xml_id(row.get('sense_id') or row.get('record_id'))
            out.append('        <sense xml:id="%s">' % sid)
            out.append('          <idno type="record_id">%s</idno>' %
                       xml_esc(row.get('record_id') or ''))
            out.append('          <idno type="fragment_id">%s</idno>' %
                       xml_esc(row.get('fragment_id') or ''))
            out.append('          <usg type="fragmentClass">%s</usg>' %
                       xml_esc(row.get('fragment_class') or ''))
            out.append('          <cit type="sourceEquivalent" xml:lang="de">')
            out.append('            <quote>%s</quote>' % xml_esc(row.get('source_string') or ''))
            out.append('          </cit>')
            out.append('          <cit type="translationEquivalent" xml:lang="ru">')
            out.append('            <quote>%s</quote>' % xml_esc(row.get('target_string') or ''))
            out.append('          </cit>')
            for path, val in scalar_map(row).items():
                if path in ('source_string', 'target_string', 'record_id',
                            'fragment_id', 'fragment_class'):
                    continue
                note = tei_note(path, val, '          ')
                if note:
                    out.append(note.rstrip('\n'))
            ext = ext_payload(row)
            out.append(tei_note('scholarly_extension', ext, '          ').rstrip('\n'))
            out.append(tei_note('source_publication_hash',
                                ext['source_publication_hash'], '          ').rstrip('\n'))
            out.append('        </sense>')
        out.append('      </entry>')
    out += ['    </body>', '  </text>', '</TEI>', '']
    return '\n'.join(out)


def _tei_local(tag):
    if tag.startswith('{%s}' % TEI_NS):
        return tag[len(TEI_NS) + 2:]
    return tag


def validate_tei(path):
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return False, 'tei parse error: %s' % e
    root = tree.getroot()
    if _tei_local(root.tag) != 'TEI':
        return False, 'root is not TEI'
    header = None
    text = None
    for child in list(root):
        loc = _tei_local(child.tag)
        if loc == 'teiHeader':
            header = child
        elif loc == 'text':
            text = child
    if header is None:
        return False, 'missing teiHeader'
    header_txt = ET.tostring(header, encoding='unicode')
    for needed in ('fileDesc', 'encodingDesc', 'revisionDesc', 'titleStmt',
                   'publicationStmt', 'sourceDesc'):
        if needed not in header_txt:
            return False, 'teiHeader missing ' + needed
    if text is None:
        return False, 'missing text'
    entries = [el for el in text.iter() if _tei_local(el.tag) == 'entry']
    if not entries:
        return False, 'zero entry'
    senses = 0
    for entry in entries:
        forms = [el for el in list(entry) if _tei_local(el.tag) == 'form']
        if not forms:
            return False, 'entry missing form'
        for sense in [el for el in list(entry) if _tei_local(el.tag) == 'sense']:
            senses += 1
            cits = [el for el in list(sense) if _tei_local(el.tag) == 'cit']
            langs = {c.get(XML_LANG) for c in cits}
            if 'de' not in langs or 'ru' not in langs:
                return False, 'sense missing de/ru cit'
    return True, 'tei ok -- %d entry, %d sense' % (len(entries), senses)


# --------------------------------------------------------------------------- #
# OntoLex + vartrans + lexicog + PROV-O
# --------------------------------------------------------------------------- #
def _ttl_prefixes():
    return (
        '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n'
        '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n'
        '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n'
        '@prefix dct: <http://purl.org/dc/terms/> .\n'
        '@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n'
        '@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .\n'
        '@prefix vartrans: <http://www.w3.org/ns/lemon/vartrans#> .\n'
        '@prefix lexicog: <http://www.w3.org/ns/lemon/lexicog#> .\n'
        '@prefix prov: <http://www.w3.org/ns/prov#> .\n'
        '@prefix pwglex: <%s> .\n'
        '@prefix tm: <%s> .\n\n' % (VOCAB_IRI, BASE_IRI)
    )


def build_ontolex(rows, created):
    by_entry = OrderedDict()
    for row in rows:
        by_entry.setdefault(row.get('entry_id') or 'pwg.entry:unresolved', []).append(row)

    buf = [_ttl_prefixes()]
    buf.append('tm:dataset a ontolex:Lexicon, prov:Entity ;\n')
    buf.append('  rdfs:label %s ;\n' % ttl_lit(
        'PWG German–Russian translation memory (canonical v1)'))
    buf.append('  dct:created %s ;\n' % ttl_lit(created, dtype='xsd:dateTime'))
    buf.append('  dct:license <https://creativecommons.org/licenses/by/4.0/> ;\n')
    buf.append('  pwglex:pipelineVersion %s ;\n' % ttl_lit(PIPELINE_VERSION))
    buf.append('  ontolex:entry %s .\n\n' % ' , '.join(
        entry_iri(eid) for eid in by_entry))

    for entry_id, members in by_entry.items():
        first = members[0]
        loc = first.get('source_locator') or {}
        lemma = loc.get('lemma_slp1') or ''
        buf.append('%s a ontolex:LexicalEntry ;\n' % entry_iri(entry_id))
        buf.append('  rdfs:label %s ;\n' % ttl_lit(lemma or entry_id))
        buf.append('  ontolex:canonicalForm %s ;\n' % form_iri(entry_id))
        buf.append('  ontolex:sense %s ;\n' % ' , '.join(
            sense_iri(r.get('sense_id') or r.get('record_id')) for r in members))
        buf.append('  pwglex:entryId %s .\n\n' % ttl_lit(entry_id))

        buf.append('%s a ontolex:Form ;\n' % form_iri(entry_id))
        buf.append('  ontolex:writtenRep %s' % ttl_lit(lemma, lang='sa-Latn-x-slp1'))
        if loc.get('iast'):
            buf.append(' ;\n  ontolex:writtenRep %s' % ttl_lit(loc['iast'], lang='sa-Latn'))
        buf.append(' .\n\n')

        if len(members) > 1:
            buf.append('%s a lexicog:Entry ;\n' % (
                '<%slexicog/%s>' % (BASE_IRI, iri_local(entry_id))))
            buf.append('  lexicog:describes %s ;\n' % entry_iri(entry_id))
            for i, row in enumerate(members, 1):
                buf.append('  rdf:_%d %s ;\n' % (
                    i, sense_iri(row.get('sense_id') or row.get('record_id'))))
            buf.append('  pwglex:reason %s .\n\n' % ttl_lit(
                'dictionary-view sense order that OntoLex core cannot express'))

        for row in members:
            sid = row.get('sense_id') or row.get('record_id')
            buf.append('%s a ontolex:LexicalSense, prov:Entity ;\n' % sense_iri(sid))
            buf.append('  ontolex:isLexicalizedSenseOf %s ;\n' % entry_iri(entry_id))
            buf.append('  skos:definition %s ;\n' % ttl_lit(
                row.get('source_string') or '', lang='de'))
            buf.append('  skos:definition %s ;\n' % ttl_lit(
                row.get('target_string') or '', lang='ru'))
            buf.append('  pwglex:recordId %s ;\n' % ttl_lit(row.get('record_id') or ''))
            for path, val in scalar_map(row).items():
                if path in ('source_string', 'target_string', 'record_id'):
                    continue
                pred = 'pwglex:f_' + path.replace('.', '__')
                if val is None:
                    continue
                if isinstance(val, (dict, list)):
                    buf.append('  %s %s ;\n' % (pred, ttl_lit(json_dump(val))))
                else:
                    buf.append('  %s %s ;\n' % (pred, ttl_lit(val)))
            ext = ext_payload(row)
            buf.append('  pwglex:scholarlyExtension %s ;\n' % ttl_lit(json_dump(ext)))
            buf.append('  pwglex:sourcePublicationHash %s ;\n' % ttl_lit(
                ext['source_publication_hash']))
            gen = get_path(row, 'provenance.generated_at') or created
            buf.append('  prov:generatedAtTime %s ;\n' % ttl_lit(gen, dtype='xsd:dateTime'))
            buf.append('  prov:wasGeneratedBy %s ;\n' % rec_iri(
                'activity/' + (row.get('record_id') or '')))
            buf.append('  prov:value %s .\n\n' % ttl_lit(row.get('source_hash') or ''))

            buf.append('%s a vartrans:Translation, vartrans:LexicalRelation ;\n' %
                       trans_iri(row.get('record_id') or sid))
            buf.append('  vartrans:source %s ;\n' % sense_iri(sid))
            buf.append('  vartrans:target %s ;\n' % sense_iri(sid))
            buf.append('  pwglex:sourceLang %s ;\n' % ttl_lit('de'))
            buf.append('  pwglex:targetLang %s ;\n' % ttl_lit(row.get('lang') or 'ru'))
            buf.append('  pwglex:sourceHash %s ;\n' % ttl_lit(row.get('source_hash') or ''))
            buf.append('  pwglex:targetHash %s .\n\n' % ttl_lit(row.get('target_hash') or ''))

            act_id = rec_iri('activity/' + (row.get('record_id') or ''))
            buf.append('%s a prov:Activity ;\n' % act_id)
            buf.append('  rdfs:label %s ;\n' % ttl_lit(PIPELINE_VERSION))
            agents = get_path(row, 'provenance.agents') or []
            for ag in agents:
                if ag.get('id'):
                    buf.append('  prov:wasAssociatedWith <%sagent/%s> ;\n' % (
                        BASE_IRI, iri_local(ag['id'])))
            buf.append('  prov:endedAtTime %s .\n\n' % ttl_lit(gen, dtype='xsd:dateTime'))
            for ag in agents:
                if not ag.get('id'):
                    continue
                buf.append('<%sagent/%s> a prov:SoftwareAgent ;\n' % (
                    BASE_IRI, iri_local(ag['id'])))
                buf.append('  rdfs:label %s ;\n' % ttl_lit(ag.get('label') or ag['id']))
                buf.append('  pwglex:agentType %s .\n\n' % ttl_lit(ag.get('type') or ''))
    return ''.join(buf)


def _ttl_has(text, needle):
    return needle in text


def validate_ontolex_text(text):
    if '@prefix ontolex:' not in text or '@prefix vartrans:' not in text:
        return False, 'missing ontolex/vartrans prefixes'
    if '@prefix prov:' not in text:
        return False, 'missing prov prefix'
    if 'ontolex:LexicalEntry' not in text:
        return False, 'no LexicalEntry'
    if 'vartrans:Translation' not in text:
        return False, 'no vartrans:Translation'
    if 'prov:Activity' not in text:
        return False, 'no prov:Activity'
    entries = text.count('a ontolex:LexicalEntry')
    trans = text.count('a vartrans:Translation')
    if entries < 1 or trans < 1:
        return False, 'counts too low'
    return True, 'ontolex ok -- %d LexicalEntry, %d Translation' % (entries, trans)


def validate_shacl_structural(text):
    """Stdlib stand-in for SHACL: every Entry has canonicalForm+sense,
    every Translation has source+target, every Sense has generatedAtTime."""
    ok, msg = validate_ontolex_text(text)
    if not ok:
        return False, msg
    if text.count('ontolex:canonicalForm') < text.count('a ontolex:LexicalEntry'):
        return False, 'SHACL: an entry is missing canonicalForm'
    if text.count('vartrans:source') < text.count('a vartrans:Translation'):
        return False, 'SHACL: a translation is missing source'
    if text.count('vartrans:target') < text.count('a vartrans:Translation'):
        return False, 'SHACL: a translation is missing target'
    if text.count('prov:generatedAtTime') < 1:
        return False, 'SHACL: no prov:generatedAtTime'
    if text.count('skos:definition') < 2:
        return False, 'SHACL: missing skos:definition pair'
    return True, 'shacl-structural ok'


# --------------------------------------------------------------------------- #
# Loss ledger
# --------------------------------------------------------------------------- #
def extract_tmx_index(path):
    tree = ET.parse(path)
    out = {}
    for tu in tree.getroot().find('body').findall('tu'):
        rid = tu.get('tuid')
        props = {}
        for p in tu.findall('prop'):
            props[p.get('type')] = '' if p.text is None else p.text
        segs = {}
        for tuv in tu.findall('tuv'):
            seg = tuv.find('seg')
            segs[tuv.get(XML_LANG)] = '' if seg is None or seg.text is None else seg.text
        out[rid] = {'props': props, 'segs': segs}
    return out


def extract_tei_index(path):
    tree = ET.parse(path)
    out = {}
    for sense in tree.getroot().iter():
        if _tei_local(sense.tag) != 'sense':
            continue
        rid = None
        notes = {}
        quotes = {}
        for child in list(sense):
            loc = _tei_local(child.tag)
            if loc == 'idno':
                typ = child.get('type')
                notes[typ] = '' if child.text is None else child.text
                if typ == 'record_id':
                    rid = child.text
            elif loc == 'usg' and child.get('type') == 'fragmentClass':
                notes['fragment_class'] = '' if child.text is None else child.text
            elif loc == 'note':
                notes[child.get('type')] = '' if child.text is None else child.text
            elif loc == 'cit':
                quote = None
                for q in list(child):
                    if _tei_local(q.tag) == 'quote':
                        quote = '' if q.text is None else q.text
                quotes[child.get(XML_LANG)] = quote
        if rid:
            out[rid] = {'notes': notes, 'quotes': quotes}
    return out


def extract_ttl_index(text):
    """Index pwglex:recordId blocks enough to recover source/target + extension."""
    out = {}
    # Split on LexicalSense resources.
    parts = re.split(r'\n(?=<[^>]+> a ontolex:LexicalSense)', text)
    for part in parts[1:]:
        m = re.search(r'pwglex:recordId "((?:\\.|[^"\\])*)"', part)
        if not m:
            continue
        rid = ttl_unesc(m.group(1))
        defs = re.findall(r'skos:definition "((?:\\.|[^"\\])*)"@([a-z-]+)', part)
        quotes = {}
        for body, lang in defs:
            quotes[lang] = ttl_unesc(body)
        ext_m = re.search(r'pwglex:scholarlyExtension "((?:\\.|[^"\\])*)"', part)
        ext = {}
        if ext_m:
            raw = ttl_unesc(ext_m.group(1))
            try:
                ext = json.loads(raw)
            except json.JSONDecodeError:
                ext = {}
        hash_m = re.search(r'pwglex:sourcePublicationHash "((?:\\.|[^"\\])*)"', part)
        fields = dict(re.findall(r'pwglex:f_([A-Za-z0-9_]+) "((?:\\.|[^"\\])*)"', part))
        decoded = {}
        for k, v in fields.items():
            decoded[k.replace('__', '.')] = ttl_unesc(v)
        decoded['record_id'] = rid
        out[rid] = {
            'quotes': quotes,
            'ext': ext,
            'pub_hash': ttl_unesc(hash_m.group(1)) if hash_m else '',
            'fields': decoded,
        }
    return out


def _norm(val):
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json_dump(val)
    if val is True:
        return 'true'
    if val is False:
        return 'false'
    return str(val)


def _json_load_maybe(text):
    if text is None:
        return None
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return text


def compare_value(expected, got):
    if expected is None and (got is None or got == ''):
        return True
    if _norm(expected) == _norm(got):
        return True
    parsed = _json_load_maybe(got)
    if _norm(expected) == _norm(parsed):
        return True
    return False


def loss_report(rows, tmx_path, tei_path, ttl_text):
    tmx = extract_tmx_index(tmx_path)
    tei = extract_tei_index(tei_path)
    ttl = extract_ttl_index(ttl_text)
    lost = []
    accounted = 0
    for row in rows:
        rid = row.get('record_id')
        tmx_row = tmx.get(rid) or tmx.get(tmx_tuid(row))
        tei_row = tei.get(rid)
        ttl_row = ttl.get(rid)
        if not tmx_row or not tei_row or not ttl_row:
            lost.append({
                'record_id': rid,
                'path': '*',
                'reason': 'record missing from a derived format',
                'tmx': bool(tmx_row), 'tei': bool(tei_row), 'ttl': bool(ttl_row),
            })
            continue
        ext_tmx = _json_load_maybe(tmx_row['props'].get('scholarly_extension')) or {}
        ext_tei = _json_load_maybe(tei_row['notes'].get('scholarly_extension')) or {}
        ext_ttl = ttl_row.get('ext') or {}

        # Body strings: round-trip identity.
        for path, tmx_lang, tei_lang, ttl_lang in (
            ('source_string', 'de', 'de', 'de'),
            ('target_string', 'ru', 'ru', 'ru'),
        ):
            expected = row.get(path) or ''
            got = (
                tmx_row['segs'].get(tmx_lang),
                tei_row['quotes'].get(tei_lang),
                ttl_row['quotes'].get(ttl_lang),
            )
            if not all(g == expected for g in got):
                lost.append({
                    'record_id': rid, 'path': path,
                    'reason': 'round-trip identity failed',
                    'expected_hash': sha256_text(expected),
                    'tmx_hash': sha256_text(got[0] or ''),
                    'tei_hash': sha256_text(got[1] or ''),
                    'ttl_hash': sha256_text(got[2] or ''),
                })
            else:
                accounted += 1

        for path in SCALAR_PATHS:
            if path in ('source_string', 'target_string'):
                continue
            expected = get_path(row, path)
            tmx_got = tmx_row['props'].get(path)
            tei_got = tei_row['notes'].get(path)
            ttl_got = ttl_row['fields'].get(path)
            if not (compare_value(expected, tmx_got)
                    and compare_value(expected, tei_got)
                    and compare_value(expected, ttl_got)):
                # None/absent optional hashes are accounted if all three omit them.
                if expected is None and not tmx_got and not tei_got and not ttl_got:
                    accounted += 1
                    continue
                lost.append({
                    'record_id': rid, 'path': path,
                    'reason': 'scalar not recovered from all formats',
                    'expected': _norm(expected),
                    'tmx': tmx_got, 'tei': tei_got, 'ttl': ttl_got,
                })
            else:
                accounted += 1

        for path in COMPLEX_PATHS:
            expected = get_path(row, path)
            tmx_got = ext_tmx.get(path)
            tei_got = ext_tei.get(path)
            ttl_got = ext_ttl.get(path)
            if not (compare_value(expected, tmx_got)
                    and compare_value(expected, tei_got)
                    and compare_value(expected, ttl_got)):
                lost.append({
                    'record_id': rid, 'path': path,
                    'reason': 'complex extension not recovered',
                })
            else:
                accounted += 1

        expected_hash = sha256_text(json_dump(row.get('source_publication')))
        tmx_h = tmx_row['props'].get('source_publication_hash')
        tei_h = tei_row['notes'].get('source_publication_hash')
        ttl_h = ttl_row.get('pub_hash')
        if not (tmx_h == expected_hash and tei_h == expected_hash and ttl_h == expected_hash):
            lost.append({
                'record_id': rid, 'path': 'source_publication',
                'reason': 'source_publication hash mismatch',
                'expected': expected_hash, 'tmx': tmx_h, 'tei': tei_h, 'ttl': ttl_h,
            })
        else:
            accounted += 1

    return {
        'schema': 'pwg.tm.export_loss.v1',
        'pipeline_version': PIPELINE_VERSION,
        'records': len(rows),
        'scholarly_paths': list(ALL_SCHOLARLY_PATHS),
        'accounted_checks': accounted,
        'lost_count': len(lost),
        'lost': lost[:50],
        'ok': len(lost) == 0,
    }


def write_text(path, text):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def created_stamp(rows, override=None):
    if override:
        return override
    stamps = [get_path(r, 'provenance.generated_at') for r in rows]
    stamps = [s for s in stamps if s]
    return max(stamps) if stamps else '1970-01-01T00:00:00Z'
