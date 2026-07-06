#!/usr/bin/env python
r"""H215 Slice 1 — TMX 1.4b exporter over the corpus Sa->Ru translation memory.

Turns the word-aligned corpus lexicon (`corpus_lexicon.jsonl`, DeepSeek L1 units:
one SLP1 Sanskrit key <-> one Russian rendering, stratified by work/genre/period)
into a TMX 1.4b interchange/publication artifact -- the cheapest publication-grade
representation of the TM. One <tu> per L1 unit for now; the segment-level L0 layer
(verse <-> verse) arrives with H215 Slice 3, and the real A/B/C composite grade with
Slice 2 (this exporter stamps grade=C on every unit until then, per the handoff).

  python build_tmx.py build                 corpus_lexicon.jsonl -> release TMX
  python build_tmx.py build --sample 500    first 500 L1 units (reviewable slice)
  python build_tmx.py build --grades PATH   stamp real A/B/C from a tm_grade.py sidecar
  python build_tmx.py build --in PATH --out PATH
  python build_tmx.py validate <file.tmx>   round-trip parse + structural checks
  python build_tmx.py selftest              fixture -> export -> re-parse, assert

RIGHTS: the corpus mixes public-domain and in-copyright named modern Russian
translations, so the emitted TMX is gitignored (release/corpus_tm/) exactly like
`corpus_lexicon.jsonl` itself. Only this generator + its README are committed. No
public release before per-translator clearance (H215 Slice 5, /publish-safety-check).

Model provenance: deterministic exporter, no LLM call. The upstream alignments in
corpus_lexicon.jsonl were produced by DeepSeek (build_corpus_lexicon.py).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_IN = os.path.join(HERE, 'corpus_lexicon.jsonl')
DEFAULT_OUT = os.path.join(ROOT, 'release', 'corpus_tm', 'corpus_tm.sa-ru.tmx')
STRATA_PATH = os.path.join(HERE, 'corpus_strata.json')

VERSION = '0.1.0'
SRCLANG = 'sa-slp1'
TGTLANG = 'ru'
# Slice 1 stamps every unit C ("usage/citation only") until the composite grader
# (Slice 2, src/tm_grade.py) assigns real A/B/C. Do NOT hand-promote here.
DEFAULT_GRADE = 'C'
# corpus_lexicon.jsonl is entirely written scholarly translations; oral units
# (modality=oral) enter via Slice 4 with their own lowered base grade.
DEFAULT_MODALITY = 'written'

CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')


def has_cyr(s):
    return bool(s) and bool(CYR.search(s))


def q(s):
    """Escape text for an XML element body."""
    return escape('' if s is None else str(s))


def tuid(rec):
    """Stable, content-derived tuid -- deterministic (no clock/random), so the
    same lexicon always yields byte-identical TMX (reproducible release)."""
    basis = '\x1f'.join(str(rec.get(k, '')) for k in
                        ('work', 'group', 'passage', 'slp1', 'ru', 'kind'))
    return 'cl-' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:16]


def _prop(kind, val):
    if val is None or val == '':
        return ''
    return '  <prop type=%s>%s</prop>\n' % (quoteattr(str(kind)), q(val))


def tu_xml(rec, grade=DEFAULT_GRADE, modality=DEFAULT_MODALITY):
    """One TMX <tu> for one L1 unit. Source seg = the SLP1 key (matches
    srclang="sa-slp1"); the printed surface Sanskrit is kept as a <prop>."""
    slp1 = (rec.get('slp1') or '').strip()
    ru = (rec.get('ru') or '').strip()
    parts = ['<tu tuid=%s>\n' % quoteattr(tuid(rec))]
    parts.append(_prop('layer', 'L1'))
    parts.append(_prop('grade', grade))
    parts.append(_prop('modality', modality))
    parts.append(_prop('kind', rec.get('kind')))
    parts.append(_prop('surface', rec.get('sa')))
    parts.append(_prop('work', rec.get('work')))
    parts.append(_prop('passage', rec.get('passage')))
    parts.append(_prop('group', rec.get('group')))
    parts.append(_prop('genre', rec.get('genre')))
    parts.append(_prop('period', rec.get('period')))
    parts.append(_prop('date', rec.get('date')))
    parts.append('  <tuv xml:lang="%s"><seg>%s</seg></tuv>\n' % (SRCLANG, q(slp1)))
    parts.append('  <tuv xml:lang="%s"><seg>%s</seg></tuv>\n' % (TGTLANG, q(ru)))
    parts.append(' </tu>\n')
    return ''.join(parts)


def iter_units(path):
    """Yield well-formed L1 records, skipping any that fail the never-invent
    guards (non-Cyrillic ru, empty key, ru==sa) -- the same invariants _audit.py
    enforces, applied again at export so a contaminated row can never reach a
    published TMX (FAILURE_GALLERY F1, the 166k-hallucination lesson)."""
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            slp1 = (r.get('slp1') or '').strip()
            ru = (r.get('ru') or '').strip()
            sa = (r.get('sa') or '').strip()
            if not slp1 or not has_cyr(ru) or ru == sa:
                continue
            yield r


def header_xml(count, srcfile):
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
        '  <prop type="tm-layer">L1 (word/phrase; corpus_lexicon.jsonl)</prop>\n'
        '  <prop type="grade-scheme">A/B/C composite (H215); this export defaults grade=C pending tm_grade.py</prop>\n'
        '  <prop type="unit-count">%d</prop>\n'
        ' </header>\n'
        ' <body>\n'
        % (quoteattr(VERSION), quoteattr(os.path.basename(srcfile)),
           quoteattr(SRCLANG),
           quoteattr(time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())),
           count))


def load_grades(path):
    """tuid -> grade from a tm_grade.py sidecar (JSONL: {tuid, grade, ...}). Absent
    path -> empty map -> every unit keeps DEFAULT_GRADE (Slice-1 behaviour)."""
    grades = {}
    if not path:
        return grades
    if not os.path.exists(path):
        sys.exit('grades sidecar not found: %s (run tm_grade.py grade first)' % path)
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get('tuid') and r.get('grade'):
                grades[r['tuid']] = r['grade']
    return grades


def build(in_path, out_path, sample=None, grade=DEFAULT_GRADE,
          modality=DEFAULT_MODALITY, grades_path=None):
    if not os.path.exists(in_path):
        sys.exit('input not found: %s\n(corpus_lexicon.jsonl is gitignored; build it '
                 'first with build_corpus_lexicon.py)' % in_path)
    grades = load_grades(grades_path)
    units = list(iter_units(in_path))
    if sample is not None:
        units = units[:sample]
    dist = {}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as out:
        out.write(header_xml(len(units), in_path))
        for r in units:
            g = grades.get(tuid(r), grade)   # sidecar wins; else the default stamp
            dist[g] = dist.get(g, 0) + 1
            out.write(tu_xml(r, grade=g, modality=modality))
        out.write(' </body>\n</tmx>\n')
    gsrc = 'sidecar %s' % os.path.basename(grades_path) if grades else 'default=%s' % grade
    print('build_tmx: %d L1 units -> %s  (grade: %s; dist %s)'
          % (len(units), out_path, gsrc, dist))
    ok, msg = validate(out_path)
    print(msg)
    return 0 if ok else 1


XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


def validate(path):
    """Round-trip: parse the emitted TMX and structurally verify it. Returns
    (ok, message). Catches malformed XML (bad escaping) and shape drift."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return False, 'validate: XML PARSE ERROR: %s' % e
    root = tree.getroot()
    if root.tag != 'tmx' or root.get('version') != '1.4':
        return False, 'validate: root is not <tmx version="1.4">'
    header = root.find('header')
    if header is None or header.get('srclang') != SRCLANG:
        return False, 'validate: missing/blank header or wrong srclang'
    body = root.find('body')
    if body is None:
        return False, 'validate: no <body>'
    tus = body.findall('tu')
    n = 0
    langs_seen = set()
    for tu in tus:
        tuvs = tu.findall('tuv')
        if len(tuvs) != 2:
            return False, 'validate: <tu> %s has %d tuv (expected 2)' % (
                tu.get('tuid'), len(tuvs))
        segs = {}
        for tuv in tuvs:
            lang = tuv.get(XML_LANG)
            seg = tuv.find('seg')
            if lang is None or seg is None or not (seg.text or '').strip():
                return False, 'validate: <tu> %s has a tuv with no lang or empty seg' % tu.get('tuid')
            segs[lang] = seg.text
            langs_seen.add(lang)
        if SRCLANG not in segs or TGTLANG not in segs:
            return False, 'validate: <tu> %s missing %s or %s tuv' % (
                tu.get('tuid'), SRCLANG, TGTLANG)
        if not has_cyr(segs[TGTLANG]):
            return False, 'validate: <tu> %s target seg has no Cyrillic' % tu.get('tuid')
        n += 1
    if n == 0:
        return False, 'validate: zero <tu> units'
    return True, 'validate: OK -- %d <tu>, langs=%s, well-formed TMX 1.4b' % (
        n, '+'.join(sorted(langs_seen)))


FIXTURE = [
    {'group': 'g1', 'work': '05_bhagavadgita', 'passage': '2.47', 'slp1': 'karman',
     'sa': 'karmaR', 'ru': 'действие', 'kind': 'ru', 'genre': 'Epic',
     'period': 'Classical', 'date': -300},
    {'group': 'g1', 'work': '05_bhagavadgita', 'passage': '2.47', 'slp1': 'aDikAra',
     'sa': 'aDikAras', 'ru': 'право', 'kind': 'ru', 'genre': 'Epic',
     'period': 'Classical', 'date': -300},
    # must survive escaping: ampersand, angle brackets, quotes in the Russian.
    {'group': 'g2', 'work': '05_bhagavadgita', 'passage': '2.48', 'slp1': 'yoga',
     'sa': 'yogaH', 'ru': 'йога <и> «связь» & равновесие', 'kind': 'ru',
     'genre': 'Epic', 'period': 'Classical', 'date': -300},
    # contamination rows the exporter MUST drop (never-invent guards):
    {'group': 'g3', 'work': 'x', 'passage': '1', 'slp1': 'ban', 'sa': 'ban',
     'ru': 'ban', 'kind': 'ru'},          # ru == sa
    {'group': 'g3', 'work': 'x', 'passage': '1', 'slp1': 'deva', 'sa': 'devaH',
     'ru': 'deva', 'kind': 'ru'},         # non-Cyrillic ru
    {'group': 'g3', 'work': 'x', 'passage': '1', 'slp1': '', 'sa': 'agni',
     'ru': 'огонь', 'kind': 'ru'},        # empty key
]


def selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix='tmx_selftest_')
    src = os.path.join(d, 'corpus_lexicon.jsonl')
    out = os.path.join(d, 'corpus_tm.sa-ru.tmx')
    with open(src, 'w', encoding='utf-8') as f:
        for r in FIXTURE:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    kept = list(iter_units(src))
    assert len(kept) == 3, 'guards should keep 3 of 6 fixture rows, kept %d' % len(kept)

    with open(out, 'w', encoding='utf-8', newline='\n') as o:
        o.write(header_xml(len(kept), src))
        for r in kept:
            o.write(tu_xml(r))
        o.write(' </body>\n</tmx>\n')

    ok, msg = validate(out)
    assert ok, 'round-trip validation failed: ' + msg

    tree = ET.parse(out)
    tus = tree.getroot().find('body').findall('tu')
    assert len(tus) == 3, 'expected 3 <tu>, got %d' % len(tus)

    # the escaping fixture must survive round-trip byte-for-byte in content.
    yoga = [t for t in tus if t.get('tuid') == tuid(FIXTURE[2])][0]
    ru = [tv.find('seg').text for tv in yoga.findall('tuv')
          if tv.get(XML_LANG) == TGTLANG][0]
    assert ru == 'йога <и> «связь» & равновесие', 'escaping round-trip lost data: %r' % ru
    props = {p.get('type'): p.text for p in yoga.findall('prop')}
    assert props.get('grade') == 'C', 'grade default should be C'
    assert props.get('layer') == 'L1'
    assert props.get('modality') == 'written'
    assert props.get('surface') == 'yogaH'

    # tuid is deterministic.
    assert tuid(FIXTURE[0]) == tuid(dict(FIXTURE[0])), 'tuid not deterministic'
    print('build_tmx selftest OK -- 3/6 rows kept, escaping + props + validation clean')
    return 0


def main():
    ap = argparse.ArgumentParser(description='TMX 1.4b exporter for the corpus Sa->Ru TM (H215 Slice 1)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('build', help='corpus_lexicon.jsonl -> TMX')
    b.add_argument('--in', dest='inp', default=DEFAULT_IN)
    b.add_argument('--out', dest='out', default=DEFAULT_OUT)
    b.add_argument('--sample', type=int, default=None, help='export only the first N L1 units')
    b.add_argument('--grade', default=DEFAULT_GRADE, help='fallback grade stamp when no sidecar (default C)')
    b.add_argument('--grades', dest='grades', default=None, help='tm_grade.py sidecar JSONL -> real A/B/C per unit')
    b.add_argument('--modality', default=DEFAULT_MODALITY)

    v = sub.add_parser('validate', help='round-trip validate an existing TMX')
    v.add_argument('path')

    sub.add_parser('selftest', help='fixture -> export -> re-parse, assert')

    a = ap.parse_args()
    if a.cmd == 'build':
        return build(a.inp, a.out, sample=a.sample, grade=a.grade,
                     modality=a.modality, grades_path=a.grades)
    if a.cmd == 'validate':
        ok, msg = validate(a.path)
        print(msg)
        return 0 if ok else 1
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
