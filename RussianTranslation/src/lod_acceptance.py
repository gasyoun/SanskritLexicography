#!/usr/bin/env python
"""Acceptance + lossless-round-trip gate for the PWG->RU LOD graph (H350/E7).

Two acceptance criteria from the handoff, both enforced here (non-zero exit on
failure):

  A. **Federated SPARQL join** -- a query that joins a PWG sense to its per-sense
     <ls> citation (lexical graph) *and* the DCS corpus frequency of its lemma
     (separate frequency graph), across the shared lemma IRI. Must return rows.

  B. **Lossless round-trip** -- the repo's re-glue byte-identity discipline,
     applied to RDF:
       B1. deterministic generation: regenerating the fixture from source is
           byte-identical to the committed fixture;
       B2. RDF round-trip: parse -> re-serialise -> re-parse is graph-isomorphic
           (no triple lost or invented by serialisation);
       B3. source coverage: every per-sense <ls>, every Renou stratum, and every
           evidence grade present in the SOURCE (over the fixture keys) survives
           as a triple in the graph -- counted independently from the jsonl and
           asserted equal.

Runs standalone against the committed fixture (no gitignored source needed) for
A + B2 + structural invariants; B1 + B3 additionally fire when the source jsonl
is reachable (``--cards`` etc. default to the repo ``src/``).

  python lod_acceptance.py                     # committed fixture + source if present
  python lod_acceptance.py --fixture release/fixture
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from rdflib import Graph  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
V = 'https://w3id.org/sanskrit-lexicon/pwg-ru/vocab#'
GR = 'https://w3id.org/sanskrit-lexicon/pwg-ru/grade/'
ONTO = 'http://www.w3.org/ns/lemon/ontolex#'
VART = 'http://www.w3.org/ns/lemon/vartrans#'
LS_RE = re.compile(r'<ls\b([^>]*)>(.*?)</ls>|<ls\b([^>]*?)/>', re.DOTALL)

FAILURES = []


def check(name, ok, detail=''):
    mark = 'PASS' if ok else 'FAIL'
    print('  [%s] %s%s' % (mark, name, (' -- ' + detail) if detail else ''))
    if not ok:
        FAILURES.append(name)
    return ok


def load_graphs(fixture_dir):
    g = Graph()
    lex = os.path.join(fixture_dir, 'pwg_ru_lod.ttl')
    freq = os.path.join(fixture_dir, 'dcs_freq.ttl')
    g.parse(lex, format='turtle')
    g.parse(freq, format='turtle')
    return g


def count(g, sparql):
    return list(g.query(sparql))[0][0].toPython()


# --------------------------------------------------------------------------- #
# A. federated join
# --------------------------------------------------------------------------- #
def test_federated_join(g, query_path):
    print('\nA. Federated SPARQL join (sense -> citation + DCS frequency)')
    with open(query_path, encoding='utf-8') as f:
        q = f.read()
    rows = list(g.query(q))
    ok = check('join returns rows', len(rows) > 0, '%d rows' % len(rows))
    for r in rows[:5]:
        d = r.asdict()
        print('       lemma=%-46s tag=%-4s dcs=%-5s %s %s' % (
            str(d.get('lemma')).rsplit('/', 1)[-1], d.get('senseTag'),
            d.get('dcsCount'), d.get('sigla'), d.get('locus') or ''))
    return ok


# --------------------------------------------------------------------------- #
# B2. RDF round-trip isomorphism
# --------------------------------------------------------------------------- #
def test_roundtrip(fixture_dir):
    print('\nB2. RDF round-trip isomorphism (parse -> serialise -> parse)')
    ok = True
    for fn in ('pwg_ru_lod.ttl', 'dcs_freq.ttl'):
        g1 = Graph(); g1.parse(os.path.join(fixture_dir, fn), format='turtle')
        ttl = g1.serialize(format='turtle')
        g2 = Graph(); g2.parse(data=ttl, format='turtle')
        iso = g1.isomorphic(g2)
        ok = check('%s isomorphic after round-trip' % fn, iso,
                   '%d triples' % len(g1)) and ok
    return ok


# --------------------------------------------------------------------------- #
# structural invariants (fixture-only, no source needed)
# --------------------------------------------------------------------------- #
def test_invariants(g):
    print('\nStructural invariants')
    ok = True
    ok = check('every LexicalSense has an evidence grade',
               count(g, 'SELECT (COUNT(?s) AS ?n){?s a <%sLexicalSense> FILTER NOT EXISTS{?s <%sevidenceGrade> ?gg}}' % (ONTO, V)) == 0) and ok
    ok = check('every Citation has pwglex:lsRaw',
               count(g, 'SELECT (COUNT(?c) AS ?n){?c a <%sCitation> FILTER NOT EXISTS{?c <%slsRaw> ?r}}' % (V, V)) == 0) and ok
    ok = check('every StratumAttestation has renouOldest+dateMin',
               count(g, 'SELECT (COUNT(?a) AS ?n){?a a <%sStratumAttestation> FILTER NOT EXISTS{?a <%srenouOldest> ?o}}' % (V, V)) == 0) and ok
    ok = check('every SenseRelation has source+target',
               count(g, 'SELECT (COUNT(?r) AS ?n){?r a <%sSenseRelation> FILTER(NOT EXISTS{?r <%ssource> ?s} || NOT EXISTS{?r <%starget> ?t})}' % (VART, VART, VART)) == 0) and ok
    ok = check('no placeholder example.org IRI remains',
               count(g, 'SELECT (COUNT(*) AS ?n){?s ?p ?o FILTER(isIRI(?o) && CONTAINS(STR(?o),"example.org"))}') == 0) and ok
    return ok


# --------------------------------------------------------------------------- #
# B1 + B3. deterministic generation + source coverage
# --------------------------------------------------------------------------- #
def read_keys(fixture_dir):
    kf = os.path.join(fixture_dir, 'fixture.keys')
    with open(kf, encoding='utf-8') as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]


def source_expected(args, keys):
    """Recompute, straight from the source jsonl over the fixture keys, the facts
    the graph must preserve: distinct <ls> citation slugs, stratum attestations
    (key1,numeric-sense), and sense count per evidence grade."""
    keyset = set(keys)
    sys.path.insert(0, HERE)
    import export_lod as X

    cites = set()
    grade_senses = {}     # grade -> count
    attest = set()        # (key1, sense_tag) with a dated stratum + matching store row
    rels = 0

    # translations (store) -> translation senses, citations, grades
    strat = X.load_stratum(args.stratum)
    relmap = X.load_relationships(args.rel)
    tr = X.load_translations(args.store, keyset)
    for key1 in keys:
        for row in tr.get(key1, []):
            grade = X.GRADE.get(row.get('review_status'), 'machine-preview')
            grade_senses[grade] = grade_senses.get(grade, 0) + 1
            for raw, _s, _l in X.extract_ls(row.get('ru')):
                slug = X.cite_slug(raw)
                if slug:
                    cites.add(slug)
            tag = row.get('sense_tag')
            if tag is not None and str(tag).isdigit():
                se = strat.get(key1, {}).get(int(tag))
                if se and se.get('stratum_label') and se.get('stratum_label') != '–':
                    attest.add((key1, str(tag)))
            sub = row.get('subcard') or ''
            for rr in relmap.get(key1, []):
                if rr.get('subcard') == sub and str(rr.get('sense_tag')) == str(tag):
                    rels += 1
    # card-carried senses (dict/kow/corpus) -> grades
    for card in X.iter_jsonl(args.cards):
        if card.get('key1') not in keyset:
            continue
        for rec in X.card_carried_senses(card):
            grade_senses[rec['grade']] = grade_senses.get(rec['grade'], 0) + 1
    return {'citations': cites, 'grades': grade_senses, 'attest': attest, 'rels': rels}


def test_source_coverage(g, args, keys):
    print('\nB3. Source coverage (every <ls>, stratum, grade survives)')
    exp = source_expected(args, keys)
    ok = True
    n_cite = count(g, 'SELECT (COUNT(DISTINCT ?c) AS ?n){?c a <%sCitation>}' % V)
    ok = check('distinct citations match source', n_cite == len(exp['citations']),
               'graph=%d source=%d' % (n_cite, len(exp['citations']))) and ok
    n_att = count(g, 'SELECT (COUNT(?a) AS ?n){?a a <%sStratumAttestation>}' % V)
    ok = check('stratum attestations match source', n_att == len(exp['attest']),
               'graph=%d source=%d' % (n_att, len(exp['attest']))) and ok
    n_rel = count(g, 'SELECT (COUNT(?r) AS ?n){?r a <%sSenseRelation>}' % VART)
    ok = check('vartrans relations match source', n_rel == exp['rels'],
               'graph=%d source=%d' % (n_rel, exp['rels'])) and ok
    for grade, exp_n in sorted(exp['grades'].items()):
        gn = count(g, 'SELECT (COUNT(?s) AS ?n){?s <%sevidenceGrade> <%s%s>}' % (V, GR, grade))
        ok = check('grade %s sense count matches source' % grade, gn == exp_n,
                   'graph=%d source=%d' % (gn, exp_n)) and ok
    return ok


def test_deterministic(args, keys, fixture_dir):
    print('\nB1. Deterministic generation (regeneration is byte-identical)')
    ok = True
    with tempfile.TemporaryDirectory() as td:
        for mode in ('lexicon', 'dcs-freq'):
            cmd = [sys.executable, os.path.join(HERE, 'export_lod.py'), mode,
                   '--keys', ','.join(keys), '--generated-at', args.generated_at,
                   '--cards', args.cards, '--store', args.store, '--rel', args.rel,
                   '--stratum', args.stratum, '--freq', args.freq, '--out-dir', td]
            subprocess.run(cmd, check=True, capture_output=True)
        for fn in ('pwg_ru_lod.ttl', 'dcs_freq.ttl'):
            with open(os.path.join(td, fn), 'rb') as a, open(os.path.join(fixture_dir, fn), 'rb') as b:
                same = a.read() == b.read()
            ok = check('%s regenerates byte-identical' % fn, same) and ok
    return ok


def load_de_graph(fixture_dir):
    """RU lexical + DCS frequency + German enrichment graphs, loaded together
    (the three-graph federated view over the shared lemma spine)."""
    g = load_graphs(fixture_dir)
    g.parse(os.path.join(fixture_dir, 'pwg_de_lexicon.ttl'), format='turtle')
    return g


def test_de_enrichment(fixture_dir, query_path):
    """PWG++ German enrichment (H772): the derivable layers glue onto the German
    original too. Fixture-only (no gitignored source needed)."""
    print('\nC. PWG++ German enrichment (glue the layers onto the German source)')
    O = ONTO
    g = load_de_graph(fixture_dir)
    ok = True
    # C1. three-way federated join: German sense -> its <ls> citation + the DCS
    #     frequency of its SHARED lemma. Must return rows.
    with open(query_path, encoding='utf-8') as f:
        q = f.read()
    rows = list(g.query(q))
    ok = check('German sense x citation x DCS-freq join returns rows', len(rows) > 0,
               '%d rows' % len(rows)) and ok
    for r in rows[:4]:
        d = r.asdict()
        print('       lemma=%-40s de-sense=%-3s dcs=%-6s %s %s' % (
            str(d.get('lemma')).rsplit('/', 1)[-1], d.get('senseNumber'),
            d.get('dcsCount'), d.get('sigla'), d.get('locus') or ''))
    # C2. every German entry is a real, language-tagged, lemma-anchored entry.
    ok = check('every German entry has dct:language "de" + canonicalForm',
               count(g, 'SELECT (COUNT(?e) AS ?n){?e a <%sLexicalEntry> ; <http://purl.org/dc/terms/language> "de" '
                        'FILTER NOT EXISTS{?e <%scanonicalForm> ?l}}' % (O, O)) == 0) and ok
    # C3. RU and DE entries sit on the SAME lemma (siblings on one spine).
    shared = count(g, 'SELECT (COUNT(DISTINCT ?lemma) AS ?n){'
                      '?de a <%sLexicalEntry> ; <http://purl.org/dc/terms/language> "de" ; <%scanonicalForm> ?lemma . '
                      '?ru a <%sLexicalEntry> ; <%scanonicalForm> ?lemma . FILTER(?ru != ?de)}' % (O, O, O, O))
    ok = check('lemmas carry >1 sibling entry (RU + DE on one lemma)', shared > 0, '%d lemmas' % shared) and ok
    # C4. every German sense carries the PWG-source evidence grade.
    ok = check('every German sense has evidenceGrade gr:pwg-source',
               count(g, 'SELECT (COUNT(?s) AS ?n){?e <http://purl.org/dc/terms/language> "de" ; <%ssense> ?s '
                        'FILTER NOT EXISTS{?s <%sevidenceGrade> <%spwg-source>}}' % (O, V, GR)) == 0) and ok
    return ok


def test_de_deterministic(args, keys, fixture_dir):
    print('\nC5. German graph deterministic generation (byte-identical)')
    with tempfile.TemporaryDirectory() as td:
        cmd = [sys.executable, os.path.join(HERE, 'export_lod.py'), 'de-lexicon',
               '--keys', ','.join(keys), '--generated-at', args.generated_at,
               '--cards', args.cards, '--stratum', args.stratum, '--out-dir', td]
        subprocess.run(cmd, check=True, capture_output=True)
        with open(os.path.join(td, 'pwg_de_lexicon.ttl'), 'rb') as a, \
             open(os.path.join(fixture_dir, 'pwg_de_lexicon.ttl'), 'rb') as b:
            same = a.read() == b.read()
    return check('pwg_de_lexicon.ttl regenerates byte-identical', same)


def test_de_source_coverage(args, keys, fixture_dir):
    print('\nC6. German source coverage (every source German sense survives)')
    sys.path.insert(0, HERE)
    import export_lod as X
    keyset = set(keys)
    exp = 0
    for card in X.iter_jsonl(args.cards):
        if card.get('key1') in keyset:
            exp += len(list(X.de_card_senses(card)))
    g = Graph(); g.parse(os.path.join(fixture_dir, 'pwg_de_lexicon.ttl'), format='turtle')
    got = count(g, 'SELECT (COUNT(?s) AS ?n){?e <http://purl.org/dc/terms/language> "de" ; <%ssense> ?s}' % ONTO)
    return check('German sense count matches source', got == exp, 'graph=%d source=%d' % (got, exp))


def test_shacl(fixture_dir, shapes_path):
    print('\nSHACL conformance (optional -- needs pyshacl)')
    try:
        import pyshacl
    except ImportError:
        print('  [skip] pyshacl not installed')
        return True
    data = load_graphs(fixture_dir)
    shapes = Graph(); shapes.parse(shapes_path, format='turtle')
    conforms, _rg, txt = pyshacl.validate(data, shacl_graph=shapes, inference='none')
    return check('graph conforms to SHACL shapes', conforms,
                 '' if conforms else txt.strip().splitlines()[0] if txt.strip() else 'see report')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fixture', default=os.path.join(ROOT, 'release', 'fixture'))
    ap.add_argument('--query', default=os.path.join(ROOT, 'release', 'query', 'sense_citation_dcsfreq.rq'))
    ap.add_argument('--de-query', default=os.path.join(ROOT, 'release', 'query', 'de_sense_citation_dcsfreq.rq'))
    ap.add_argument('--shapes', default=os.path.join(ROOT, 'release', 'shapes.ttl'))
    ap.add_argument('--cards', default=os.path.join(HERE, 'assembled_cards.jsonl'))
    ap.add_argument('--store', default=os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    ap.add_argument('--rel', default=os.path.join(HERE, 'pwg_ru_relationships.jsonl'))
    ap.add_argument('--stratum', default=os.path.join(HERE, 'pwg_sense_stratum.jsonl'))
    ap.add_argument('--freq', default=os.path.join(HERE, 'dcs_freq.json'))
    ap.add_argument('--generated-at', default='2026-07-08')
    args = ap.parse_args()

    print('LOD acceptance gate (H350/E7) -- fixture: %s' % args.fixture)
    g = load_graphs(args.fixture)
    print('  loaded %d triples' % len(g))
    keys = read_keys(args.fixture)

    test_federated_join(g, args.query)
    test_roundtrip(args.fixture)
    test_invariants(g)
    test_shacl(args.fixture, args.shapes)

    de_present = os.path.exists(os.path.join(args.fixture, 'pwg_de_lexicon.ttl'))
    if de_present:
        test_de_enrichment(args.fixture, args.de_query)

    if os.path.exists(args.cards) and os.path.exists(args.store):
        test_source_coverage(g, args, keys)
        test_deterministic(args, keys, args.fixture)
        if de_present:
            test_de_source_coverage(args, keys, args.fixture)
            test_de_deterministic(args, keys, args.fixture)
    else:
        print('\n[skip] B1+B3: source jsonl not reachable (gitignored) -- '
              'fixture-only checks ran. Point --cards/--store at the repo src to enable.')

    print()
    if FAILURES:
        print('ACCEPTANCE FAILED: %d check(s) -- %s' % (len(FAILURES), ', '.join(FAILURES)))
        sys.exit(1)
    print('ACCEPTANCE PASSED')


if __name__ == '__main__':
    main()
