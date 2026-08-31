#!/usr/bin/env python
"""Validate minimal TEI/OntoLex/reverse-index release artifacts (G9).

[#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798): both shipped interop
artifacts carry **12,374 duplicated entry ids** (120,173 ids, 106,082 distinct) and this
gate reported both as validating. It could not have caught them:

* ``validate_tei`` called ``ET.parse`` and counted ``<entry>`` elements. ElementTree is a
  non-validating parser with no ``xml:id`` awareness, so a duplicate ID — invalid per the
  XML ID rule — sails through.
* ``validate_ontolex`` never parsed Turtle at all: it was ``text.count('ontolex:LexicalEntry')``,
  which would pass on a file consisting solely of that literal string. The RDF half is the
  worse of the two, because duplicate RDF subjects are perfectly legal and simply **merge** —
  14,091 entries' senses silently unioned onto the wrong lexical entry, with no error anywhere.

W1 (H3748) closes step 1 of that issue's fix list, and only step 1: **harden the gate
first**. TEI ids are collected and asserted unique; OntoLex is parsed with `rdflib` (already
in [`requirements.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/requirements.txt),
already used for exactly this in `src/lod_acceptance.py`) and its distinct
``ontolex:LexicalEntry`` subjects counted for real.

Deliberately **not** done here:

* **Re-cutting the artifacts** (step 2). They are published against a Zenodo DOI, so
  whether to re-cut in place or supersede with a new version plus a public erratum is a
  publication decision. Re-cutting before the gate had teeth would have put clean bytes
  behind a blind gate and made the next drift equally invisible — which is why the issue
  orders it this way.
* **The ``safe_id``/``idn`` counter fix** (step 3, one genuine collapse: ``pwg-U``).

So this gate is expected to be **RED on the currently shipped
[`release/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release)
artifacts**. That is the finding, not a regression.

    python src/validate_interop.py --dir release
"""
import argparse
import collections
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.join(HERE, 'pilot') not in sys.path:
    sys.path.insert(0, os.path.join(HERE, 'pilot'))
import gate_evidence as ge                                          # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_RELEASE = os.path.join(ROOT, 'release')

TEI_NS = 'http://www.tei-c.org/ns/1.0'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
ONTOLEX_ENTRY = 'http://www.w3.org/ns/lemon/ontolex#LexicalEntry'

#: How many duplicated ids to name in a failure message before eliding.
MAX_NAMED_DUPES = 10


def fail(msg):
    raise ValueError(msg)


def _dupe_report(counter, label):
    dupes = {value: n for value, n in counter.items() if n > 1}
    if not dupes:
        return None
    worst = sorted(dupes.items(), key=lambda kv: (-kv[1], kv[0]))
    named = ', '.join('%s x%d' % (v, n) for v, n in worst[:MAX_NAMED_DUPES])
    return ('%s: %d duplicated value(s) across %d occurrence(s) — %s%s'
            % (label, len(dupes), sum(dupes.values()), named,
               ' …' if len(worst) > MAX_NAMED_DUPES else ''))


def measure_tei(path):
    """(entry_count, distinct_ids, error_or_None) — measure without raising.

    Split out from :func:`validate_tei` so the evidence record carries REAL counts on a
    failing artifact too. A gate that reports 0/0 when it found 12,374 duplicates is the
    same shape of blindness the duplicates got in through.
    """
    if not os.path.exists(path):
        return 0, 0, 'missing TEI file: %s' % path
    root = ET.parse(path).getroot()
    if not root.tag.endswith('TEI'):
        return 0, 0, 'TEI root is not TEI: %s' % root.tag
    entries = root.findall('.//{%s}entry' % TEI_NS)
    if not entries:
        return 0, 0, 'TEI contains no entries'
    ids = collections.Counter(e.get(XML_ID) for e in entries if e.get(XML_ID) is not None)
    missing = len(entries) - sum(ids.values())
    if missing:
        return len(entries), len(ids), ('TEI has %d <entry> element(s) with no xml:id'
                                        % missing)
    return len(entries), len(ids), _dupe_report(ids, 'TEI xml:id')


def validate_tei(path):
    """(entry_count, distinct_ids, duplicate_id_count). Raises on any duplicate.

    #1798: a duplicate ``xml:id`` is invalid per the XML ID rule, but ElementTree has no
    ID awareness, so counting ``<entry>`` elements can never see one.
    """
    entries, distinct, error = measure_tei(path)
    if error:
        fail(error)
    return entries, distinct, 0


def measure_ontolex(path):
    """(declared_entries, distinct_subjects, error_or_None) — measure without raising."""
    if not os.path.exists(path):
        return 0, 0, 'missing OntoLex file: %s' % path
    try:
        import rdflib
    except ImportError:                                   # pragma: no cover - env guard
        return 0, 0, ('rdflib is required to validate OntoLex Turtle (it is in '
                      'requirements.txt). Refusing to fall back to a substring count — '
                      'that fallback IS the #1798 defect, not a degraded mode.')
    graph = rdflib.Graph()
    graph.parse(path, format='turtle')
    distinct = len(set(graph.subjects(rdflib.RDF.type, rdflib.URIRef(ONTOLEX_ENTRY))))
    # The serialization's own count of the type triple: rdflib de-duplicates identical
    # triples, so repeated blocks for one subject collapse and must be counted in text.
    declared = open(path, encoding='utf-8').read().count('ontolex:LexicalEntry')
    if not distinct:
        return declared, 0, 'OntoLex Turtle contains no ontolex:LexicalEntry subjects'
    if declared > distinct:
        return declared, distinct, (
            'OntoLex: %d ontolex:LexicalEntry declaration(s) in the serialization but only '
            '%d distinct subject(s) — %d entr(y/ies) silently MERGED onto another lexical '
            'entry (duplicate RDF subjects are legal and simply union, so nothing else in '
            'the stack can report this)' % (declared, distinct, declared - distinct))
    return declared, distinct, None


def validate_ontolex(path):
    """(entry_count, distinct_subjects, duplicate_count). Raises on any duplicate.

    Parsed with `rdflib`, not counted as a substring. Duplicate RDF subjects are legal and
    simply merge, so a *parsed* graph cannot report them either — the count that matters is
    the graph's distinct ``ontolex:LexicalEntry`` subjects against the serialization's
    occurrences of the same type triple. A gap between the two is the silent union #1798
    measured.
    """
    declared, distinct, error = measure_ontolex(path)
    if error:
        fail(error)
    return declared, distinct, 0


def validate_reverse(path):
    if not os.path.exists(path):
        fail('missing reverse index: %s' % path)
    n = 0
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            for field in ('ru', 'key1'):
                if not row.get(field):
                    fail('reverse index line %d missing %s' % (i, field))
            if 'source' not in row or 'ref' not in row:
                fail('reverse index line %d missing source/ref' % i)
            n += 1
    if not n:
        fail('reverse index is empty')
    return n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=DEFAULT_RELEASE)
    ap.add_argument('--evidence', default=None, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    ev = ge.GateEvidence('interop_validity',
                         'released TEI/OntoLex/reverse-index validity (G9, #1798)')
    tei_path = os.path.join(args.dir, 'tei_lex0.xml')
    ttl_path = os.path.join(args.dir, 'ontolex.ttl')
    rev_path = os.path.join(args.dir, 'reverse_index.jsonl')
    failures = []

    tei, tei_ids, tei_error = measure_tei(tei_path)
    if tei_error:
        failures.append(tei_error)
    ttl, ttl_ids, ttl_error = measure_ontolex(ttl_path)
    if ttl_error:
        failures.append(ttl_error)
    try:
        rev = validate_reverse(rev_path)
    except ValueError as exc:
        rev = 0
        failures.append(str(exc))

    ev.add_input('tei', path=tei_path, units=tei)
    ev.add_input('ontolex', path=ttl_path, units=ttl)
    ev.add_input('reverse_index', path=rev_path, units=rev)
    ev.add_predicate('tei_entry_id_uniqueness', evaluations=tei,
                     hits=max(tei - tei_ids, 0))
    ev.add_predicate('ontolex_subject_uniqueness', evaluations=ttl,
                     hits=max(ttl - ttl_ids, 0))
    ev.add_predicate('reverse_row_fields', evaluations=rev, hits=0)
    ev.note('tei_distinct_ids', tei_ids)
    ev.note('ontolex_distinct_subjects', ttl_ids)
    ev.set_verdict('fail' if failures else 'pass')
    try:
        ev.assert_nonvacuous()
    except ge.VacuousGateError as exc:
        ev.set_verdict('fail')
        failures.append(str(exc))
    ev.emit(args.evidence or ge.sidecar_for(os.path.join(args.dir, 'interop_validation')))

    if failures:
        for line in failures:
            print('INTEROP CHECK FAILED: %s' % line, file=sys.stderr)
        return 1
    print('interop validation OK: TEI entries=%d (%d distinct ids) | OntoLex entries=%d '
          '(%d distinct subjects) | reverse rows=%d' % (tei, tei_ids, ttl, ttl_ids, rev))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
