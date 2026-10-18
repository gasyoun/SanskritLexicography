#!/usr/bin/env python
r"""Render the built PWG->RU LOD graph as the static per-resource Pages surface.

Consumes ``release/pwg_ru_lod.ttl`` (the full lexical graph from
``export_lod.py``) and emits, per resource document:

  - ``entry/<ekey>.ttl``            — the entry chunk + its sense chunks
  - ``entry/<ekey>.html``           — minimal HTML rendering with the
                                      machine-preview non-citable banner
  - ``lemma/<key1>.ttl``            — shared lemma-bank node
  - ``citation/<slug>.ttl``         — per-<ls> citation resource
  - ``index.html`` / ``grades.ttl`` / ``vocab.ttl`` / ``dataset.ttl``

Chunking is line-based: the exporter writes one resource block per contiguous
run of lines ending at a blank line, so a chunk's subject is its first line's
IRI. Sense IRIs (``sense/<ekey>/<dict>/<no>``) are assigned to their owning
entry document (``<ekey>``), which the w3id .htaccess mirrors with a 303.

  python src/render_static_lod.py --graph release/pwg_ru_lod.ttl --out-dir release/site

Known preview limitation (documented in PROVENANCE.md): lemma/citation/grade
documents are Turtle-only; per-entry documents carry the full Turtle/HTML
content negotiation.
"""
import argparse
import html
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE = 'https://w3id.org/sanskrit-lexicon/repwg/'

BANNER = (
    '<div role="alert" style="border:2px solid #b00;background:#fdd;padding:.8em 1em;'
    'margin:0 0 1em 0;font-family:sans-serif">'
    '<strong>&#9888; Machine translation — not yet human-reviewed — NOT CITABLE.</strong><br>'
    'Every sense below is graded <code>gr:machine-preview</code> or '
    '<code>gr:dict-attested</code> (machine-assisted). No human-approved '
    '(<code>gr:approved</code>/<code>gr:human-reviewed</code>) senses exist yet; the '
    'citable subset is the SPARQL filter '
    '<code>?s pwglex:evidenceGrade ?g . FILTER(?g IN (gr:approved, gr:human-reviewed))</code> '
    'and is currently empty. Technical preview of the graph shape; do not cite the '
    'translations. See <a href="/pwg-ru-lod/">the dataset landing page</a>.</div>'
)

LABEL_RE = re.compile(r'rdfs:label "([^"]*)"')
WRITTEN_RE = re.compile(r'ontolex:writtenRep "([^"]*)"@([^\s;]*)')
DEF_RE = re.compile(r'skos:definition "([^"]*)"@(ru|de|en)')
GRADE_RE = re.compile(r'pwglex:evidenceGrade gr:([a-z-]+)')
SOURCE_RE = re.compile(r'dct:source "([^"]*)"')
REFS_RE = re.compile(r'dct:references <([^>]*)>')


def turtle_escape_to_text(s):
    # unescape the common turtle escapes the exporter emits
    return (s.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
             .replace('\\t', '\t'))


def read_chunks(path):
    """Yield (subject_iri, chunk_text); a chunk starts at every resource-subject
    line (the exporter writes one complete turtle statement per resource) and at
    the ``# base IRI:`` header comment."""
    buf, subject = [], None
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if line.startswith('# base IRI:'):
                if buf and subject:
                    yield subject, ''.join(buf)
                buf, subject = [line], '__header__'
                continue
            if line.startswith('<' + BASE):
                if buf and subject:
                    yield subject, ''.join(buf)
                buf = [line]
                subject = line[1:line.index('>')]
            elif buf is not None:
                buf.append(line)
            elif line.strip():
                buf, subject = [line], None
    if buf and subject:
        yield subject, ''.join(buf)


def owner_entry(subject):
    """sense/<ekey>/... -> entry/<ekey>; else None."""
    if subject.startswith(BASE + 'sense/'):
        rest = subject[len(BASE) + len('sense/'):]
        seg = rest.split('/')
        if len(seg) >= 2:
            return '%s/%s' % (seg[0], seg[1])
    return None


def doc_of(subject):
    """Map a chunk subject to its output document stem (no extension)."""
    if subject.startswith(BASE + 'entry/'):
        return subject[len(BASE):].rstrip('/')
    o = owner_entry(subject)
    if o:
        return o
    if subject.startswith(BASE + 'lemma/'):
        return subject[len(BASE):].rstrip('/')
    if subject.startswith(BASE + 'citation/'):
        return subject[len(BASE):].rstrip('/')
    return None  # meta (header/lexicon/prov/grade/vocab) -> index docs


def parse_entry_doc(stem, chunks):
    """Extract the fields the HTML template needs from one document's chunks."""
    doc = {'stem': stem, 'label': '', 'written': [], 'senses': [], 'canonical': ''}
    for subj, text in chunks:
        if subj.endswith('/grade/scheme') or 'grade/' in subj.split(BASE)[-1][:6]:
            continue
        if '/sense/' in subj:
            m = DEF_RE.search(text)
            g = GRADE_RE.search(text)
            s = SOURCE_RE.search(text)
            refs = [r[len(BASE):] if r.startswith(BASE) else r
                    for r in REFS_RE.findall(text)]
            doc['senses'].append({
                'iri': subj, 'def': turtle_escape_to_text(m.group(1)) if m else '',
                'grade': g.group(1) if g else '', 'source': s.group(1) if s else '',
                'refs': refs,
            })
            continue
        m = LABEL_RE.search(text)
        if m and not doc['label']:
            doc['label'] = m.group(1)
        for wm in WRITTEN_RE.finditer(text):
            form = turtle_escape_to_text(wm.group(1))
            if (form, wm.group(2)) not in doc['written']:
                doc['written'].append((form, wm.group(2)))
        if subj.startswith(BASE + 'lemma/') and not doc['canonical']:
            doc['canonical'] = subj
    return doc


def render_html(doc, generated):
    esc = html.escape
    title = esc(doc['label'] or (doc['written'][0][0] if doc['written'] else doc['stem']))
    parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<title>%s — PWG→RU LOD (technical preview)</title>' % title,
        '<style>body{font-family:Georgia,serif;max-width:52em;margin:2em auto;padding:0 1em;'
        'line-height:1.45}dl dt{font-weight:bold;margin-top:.9em}dd{margin-left:1.4em}'
        'code{background:#f4f4f4}</style></head><body>',
        BANNER,
        '<h1>%s</h1>' % title,
        '<p>IRI: <code>%s%s</code><br>' % (esc(BASE), esc(doc['stem'])),
    ]
    if doc['written']:
        parts.append('Written representations: %s<br>' % esc(', '.join(
            '%s@%s' % (f, l) for f, l in doc['written'])))
    if doc['canonical']:
        parts.append('Canonical form: <a href="%s%s.ttl">%s</a><br>'
                     % (esc(BASE), esc(doc['canonical'][len(BASE):]), esc(doc['canonical'])))
    parts.append('Machine-readable: <a href="%s%s.ttl">Turtle</a></p>'
                 % (esc(BASE), esc(doc['stem'])))
    if doc['senses']:
        parts.append('<h2>Senses (%d)</h2><dl>' % len(doc['senses']))
        for i, s in enumerate(doc['senses'], 1):
            parts.append('<dt>%d. <code>gr:%s</code>%s</dt><dd>%s%s</dd>' % (
                i, esc(s['grade'] or 'ungraded'),
                (' (source: <em>%s</em>)' % esc(s['source'])) if s['source'] else '',
                esc(s['def']),
                ('<br>References: %s' % ', '.join(
                    '<a href="%s">%s</a>' % (esc(r if r.startswith('http') else BASE + r),
                                             esc(r.split('/')[-1]))
                    for r in s['refs'])) if s['refs'] else ''))
        parts.append('</dl>')
    parts.append('<p style="color:#666;font-size:.9em">PWG→RU LOD graph, generated %s. '
                 'License: <a href="https://creativecommons.org/licenses/by-sa/4.0/">'
                 'CC BY-SA 4.0</a> (see dataset landing page for third-party credits).'
                 '</p>' % esc(generated))
    parts.append('</body></html>')
    return '\n'.join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--graph', default=os.path.join('release', 'pwg_ru_lod.ttl'))
    ap.add_argument('--out-dir', default=os.path.join('release', 'site'))
    ap.add_argument('--generated-at', default=None)
    args = ap.parse_args()
    if args.generated_at is None:
        import datetime
        args.generated_at = datetime.date.today().isoformat()

    os.makedirs(args.out_dir, exist_ok=True)
    for sub in ('entry', 'lemma', 'citation'):
        os.makedirs(os.path.join(args.out_dir, sub), exist_ok=True)

    docs = {}          # stem -> [chunks]
    meta = []          # (subject, chunk)
    prefixed = []      # chunks whose subject uses a QName (pwglex:/gr: vocab terms)
    n = 0
    for subject, chunk in read_chunks(args.graph):
        n += 1
        if subject == '__header__':
            meta.append((subject, chunk))
            continue
        if subject is None:
            prefixed.append(chunk)
            continue
        stem = doc_of(subject)
        if stem is None:
            meta.append((subject, chunk))
        else:
            docs.setdefault(stem, []).append((subject, chunk))
    print('chunks: %d, docs: %d, meta chunks: %d' % (n, len(docs), len(meta)))

    # meta docs: index turtle (lexicon/prov/grade/vocab blocks + header)
    header = next((c for s, c in meta if s == '__header__'), '')
    idx_path = os.path.join(args.out_dir, 'dataset.ttl')
    with open(idx_path, 'w', encoding='utf-8') as fh:
        fh.write(header)
        for subject, chunk in meta:
            if subject != '__header__':
                fh.write('\n' + chunk)
    # grades.ttl: grade/ meta blocks + the gr:/pwglex: QName definitions
    grades = [c for s, c in meta if s.startswith(BASE + 'grade/')]
    with open(os.path.join(args.out_dir, 'grades.ttl'), 'w', encoding='utf-8') as fh:
        fh.write(header)
        for c in grades + prefixed:
            fh.write('\n' + c)
    # vocab.ttl: the pwglex:/gr: prefix block + QName term definitions
    with open(os.path.join(args.out_dir, 'vocab.ttl'), 'w', encoding='utf-8') as fh:
        fh.write(header)
        for c in prefixed:
            fh.write('\n' + c)

    counts = {'entry': 0, 'lemma': 0, 'citation': 0}
    for stem, chunks in docs.items():
        kind = stem.split('/', 1)[0]
        with open(os.path.join(args.out_dir, stem + '.ttl'), 'w', encoding='utf-8') as fh:
            fh.write(header)
            for subject, chunk in chunks:
                fh.write('\n' + chunk)
        if kind == 'entry':
            doc = parse_entry_doc(stem, chunks)
            with open(os.path.join(args.out_dir, stem + '.html'), 'w', encoding='utf-8') as fh:
                fh.write(render_html(doc, args.generated_at))
        counts[kind] = counts.get(kind, 0) + 1
    print('written: %s' % counts)

    landing = os.path.join(args.out_dir, 'index.html')
    if not os.path.exists(landing):
        with open(landing, 'w', encoding='utf-8') as fh:
            fh.write(LANDING_TEMPLATE % (html.escape(args.generated_at), len(docs)))


LANDING_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>PWG→RU LOD graph — machine-preview technical release</title>
<style>body{font-family:Georgia,serif;max-width:52em;margin:2em auto;padding:0 1em;
line-height:1.5}code{background:#f4f4f4}</style></head><body>
<div role="alert" style="border:2px solid #b00;background:#fdd;padding:.8em 1em;margin:0 0 1em 0">
<strong>&#9888; Machine translation — not yet human-reviewed — NOT CITABLE.</strong><br>
This dataset publishes the graph <em>shape</em> of the Petersburg Dictionary → Russian
Linked-Open-Data edition as a technical preview. Every translated sense is graded
<code>gr:machine-preview</code> (machine translation, no human review); dictionary-layer
senses are <code>gr:dict-attested</code>. The citable subset
(<code>pwglex:citable true</code>) is documented but currently empty — it will fill only
after human sense approvals. Do not cite the translations.</div>
<h1>PWG→RU LOD graph</h1>
<p>Permanent namespace: <code>https://w3id.org/sanskrit-lexicon/repwg/</code> (w3id.org
303 content negotiation: Turtle to machines, HTML to browsers).</p>
<ul>
<li>Dataset description (VoID/DCAT): <a href="void.ttl">void.ttl</a></li>
<li>Full lexical graph (gzip — Turtle gzips ~10:1, staying under GitHub's
100 MB file cap): <a href="pwg_ru_lod.ttl.gz">pwg_ru_lod.ttl.gz</a></li>
<li>DCS lemma-frequency graph: <a href="dcs_freq.ttl">dcs_freq.ttl</a></li>
<li>SHACL shapes: <a href="shapes.ttl">shapes.ttl</a> · grades: <a href="grades.ttl">grades.ttl</a>
· vocabulary: <a href="vocab.ttl">vocab.ttl</a></li>
<li>SPARQL acceptance query: <a href="sense_citation_dcsfreq.rq">sense_citation_dcsfreq.rq</a></li>
<li>Small-class register (SKOS, v1.6.1): <a href="small-class-register.ttl">small-class-register.ttl</a></li>
</ul>
<p>Example resource: <a href="https://w3id.org/sanskrit-lexicon/repwg/entry/rakz">
https://w3id.org/sanskrit-lexicon/repwg/entry/rakz</a></p>
<p>License: CC BY-SA 4.0 for the project's own work; PWG (Böhtlingk–Roth) is public
domain; DCS frequency data is CC BY 4.0 (Hellwig, <em>Digital Corpus of Sanskrit</em>,
2010–2024); Kochergina/Frisch/Smirnov gloss layers are used under recorded copyright
approvals with per-sense attribution (<code>dct:source</code>).</p>
<p style="color:#666">Generated %s · %d resource documents · a
<a href="https://github.com/sanskrit-lexicon/csl-standards">csl-standards</a> publication.</p>
</body></html>
"""


if __name__ == '__main__':
    main()
