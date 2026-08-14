#!/usr/bin/env python
"""Extract the six ruled PWG TM fragment classes (H2683 Track A).

  python src/pwg_tm_fragmentize.py
  python src/pwg_tm_fragmentize.py --verify
  python src/pwg_tm_fragmentize.py --canonical PATH --out-dir DIR

Reuses the markup regexes already owned by markup_fidelity_gates /
microstructure (gloss, <ls>, <lex>, <ab>, {#...#}). Does not invent sense
links: multi-sense publication rows stay sense_alignment=unresolved at the
parent and each extracted sense fragment carries its own ordinal address.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402
from markup_fidelity_gates import GLOSS_RE, SAN_RE  # noqa: E402

LS_FULL = re.compile(r'<ls\b[^>]*>.*?</ls>', re.S)
LEX_FULL = re.compile(r'<lex\b[^>]*>.*?</lex>', re.S)
AB_FULL = re.compile(r'<ab\b([^>]*)>(.*?)</ab>', re.S)
NATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')
SA_FULL = SAN_RE
GLOSS_FULL = GLOSS_RE

GRAMMAR_AB = {
    'adj.', 'adv.', 'm.', 'f.', 'n.', 'm. n.', 'f. n.', 'm. f.', 'm. f. n.',
    'partic.', 'part.', 'caus.', 'desid.', 'intens.', 'pass.', 'med.', 'act.',
    'nom.', 'acc.', 'instr.', 'dat.', 'abl.', 'gen.', 'loc.', 'voc.',
    'sg.', 'du.', 'pl.', 'inf.', 'abs.', 'ger.', 'impf.', 'perf.', 'aor.',
    'opt.', 'impv.', 'fut.', 'cond.', 'ppp.', 'pp.', 'subst.', 'interj.',
    'pron.', 'num.', 'indecl.', 'comp.', 'superl.', 'denomin.', 'desid',
    'partic', 'caus',
}
FORMULA_AB = {
    'vgl.', 's. u.', 's. d.', 's. v.', 's. u. d.', 'fgg.', 'fg.', 'dass.',
    'ebend.', 'u.s.w.', 'desgl.', 'dgl.', 'sc.', 'scil.', 's. u. d. W.',
}
FORMULA_PHRASES = (
    re.compile(r'am Anf(?:ange|\.) eines Comp(?:ositums?|\.)?', re.I),
    re.compile(r'am Ende eines Comp(?:ositums?|\.)?', re.I),
    re.compile(r'in Verbindung mit', re.I),
    re.compile(r's\.\s*u\.\s*d\.\s*W\.', re.I),
)


def _ab_token(attrs, content):
    nm = NATTR.search(attrs or '')
    tok = re.sub(r'<[^>]+>', '', content or '').strip()
    return (nm.group(1) if nm else tok), tok


def _pair(src_spans, tgt_spans):
    """Pair by index when counts match; otherwise leave target unresolved."""
    if len(src_spans) == len(tgt_spans):
        return list(zip(src_spans, tgt_spans))
    out = [(s, None) for s in src_spans]
    return out


def _spans(regex, text):
    return [m.group(0) for m in regex.finditer(text or '')]


def fragment_row(parent, fragment_class, source, target, index, tag, rec_h, mapped):
    parent_id = parent['record_id']
    locator = dict(parent.get('source_locator') or {})
    if rec_h:
        locator = dict(locator)
        locator['homonym'] = rec_h
    entry_id = parent['entry_id']
    sense_id = C.sense_id_of(entry_id, tag, index if fragment_class == 'sense' else index,
                             mapped)
    src = source or ''
    tgt = target
    ctx = '%s|%s|%s' % (locator.get('lemma_slp1') or '', tag or '', rec_h or '')
    frag_id = C.fragment_id_of(fragment_class, parent_id, index, src)
    return {
        'schema': C.SCHEMA,
        'schema_version': C.SCHEMA_VERSION,
        'record_kind': 'fragment',
        'record_id': frag_id,
        'entry_id': entry_id,
        'sense_id': sense_id,
        'fragment_id': frag_id,
        'fragment_class': fragment_class,
        'sense_alignment': 'mapped' if mapped else 'unresolved',
        'lang': parent.get('lang') or 'ru',
        'source_locator': locator,
        'source_string': src,
        'source_hash': C.sha256_text(src),
        'target_string': tgt,
        'target_hash': C.sha256_text(tgt) if tgt is not None else None,
        'reuse_key': C.reuse_key_of(fragment_class, src, ctx),
        'reuse_policy': parent.get('reuse_policy') or 'suggest_only',
        'parent_record_id': parent_id,
        'context': {
            'sense_tag': tag or '',
            'homonym': rec_h or '',
            'local_index': index,
            'parent_tm_record_id': parent.get('tm_record_id'),
        },
        'trust_level': parent.get('trust_level'),
        'gate_status': parent.get('gate_status'),
    }


def extract_from_sense(parent, tag, german, russian, rec_h, ordinal, mapped):
    rows = []
    rows.append(fragment_row(
        parent, 'sense', german, russian, ordinal, tag, rec_h, mapped))
    for i, (src, tgt) in enumerate(_pair(_spans(GLOSS_FULL, german),
                                         _spans(GLOSS_FULL, russian)), 1):
        rows.append(fragment_row(
            parent, 'definition_gloss', src, tgt, ordinal * 1000 + i, tag, rec_h, mapped))
    lex_pairs = _pair(_spans(LEX_FULL, german), _spans(LEX_FULL, russian))
    for i, (src, tgt) in enumerate(lex_pairs, 1):
        rows.append(fragment_row(
            parent, 'grammar_label', src, tgt, ordinal * 1000 + i, tag, rec_h, mapped))
    ab_src = list(AB_FULL.finditer(german or ''))
    ab_tgt = list(AB_FULL.finditer(russian or ''))
    tgt_by_i = {i: m.group(0) for i, m in enumerate(ab_tgt)}
    for i, match in enumerate(ab_src, 1):
        label, visible = _ab_token(match.group(1), match.group(2))
        token = (label or visible or '').strip()
        norm = token.lower() if token.endswith('.') else (token.lower() + '.')
        tgt = tgt_by_i.get(i - 1) if len(ab_src) == len(ab_tgt) else None
        if token in GRAMMAR_AB or norm in GRAMMAR_AB:
            klass = 'grammar_label'
        elif token in FORMULA_AB or norm in FORMULA_AB:
            klass = 'recurring_formula'
        else:
            # Unknown <ab>: keep as grammar_label only when it sits in a <lex>-like
            # POS slot; otherwise treat as formula metalanguage, never a sense.
            klass = 'recurring_formula'
        rows.append(fragment_row(
            parent, klass, match.group(0), tgt, ordinal * 1000 + 200 + i,
            tag, rec_h, mapped))
    for i, (src, tgt) in enumerate(_pair(_spans(LS_FULL, german),
                                         _spans(LS_FULL, russian)), 1):
        rows.append(fragment_row(
            parent, 'citation', src, tgt, ordinal * 1000 + i, tag, rec_h, mapped))
    for i, (src, tgt) in enumerate(_pair(_spans(SA_FULL, german),
                                         _spans(SA_FULL, russian)), 1):
        rows.append(fragment_row(
            parent, 'example', src, tgt, ordinal * 1000 + i, tag, rec_h, mapped))
    for phrase in FORMULA_PHRASES:
        for i, match in enumerate(phrase.finditer(german or ''), 1):
            tgt_m = phrase.search(russian or '')
            rows.append(fragment_row(
                parent, 'recurring_formula', match.group(0),
                tgt_m.group(0) if tgt_m else None,
                ordinal * 1000 + 800 + i, tag, rec_h, mapped))
    return rows


def fragmentize_record(parent):
    pub = parent.get('source_publication') or parent
    units = list(C.sense_units(pub))
    if not units:
        units = [('', parent.get('source_string') or '',
                  parent.get('target_string') or '', '', 1)]
    mapped_parent = parent.get('sense_alignment') == 'mapped' and len(units) == 1
    rows = []
    for tag, de, ru, rec_h, ordinal in units:
        mapped = mapped_parent or (len(units) >= 1 and bool(tag))
        # Multi-sense cards: each sense fragment is mapped to its ordinal/tag;
        # we still do not invent a relation across records.
        if len(units) > 1:
            mapped = bool(tag)
        rows.extend(extract_from_sense(parent, tag, de, ru, rec_h, ordinal, mapped))
    return rows


def fragmentize_rows(canonical_rows):
    out = []
    for parent in canonical_rows:
        out.extend(fragmentize_record(parent))
    return out


def inventory(fragments, parents):
    from collections import Counter
    classes = Counter(f.get('fragment_class') for f in fragments)
    orphan = [f['fragment_id'] for f in fragments
              if f.get('parent_record_id') not in {p['record_id'] for p in parents}]
    ids = [f['fragment_id'] for f in fragments]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    missing = [c for c in C.FRAGMENT_CLASSES if classes.get(c, 0) == 0]
    invalid = []
    for row in fragments:
        ok, why = C.validate_canonical(row)
        if not ok:
            invalid.append({'fragment_id': row.get('fragment_id'), 'why': why})
            if len(invalid) >= 20:
                break
    report = {
        'schema': 'pwg.tm.canonical.fragment_inventory.v1',
        'parent_count': len(parents),
        'fragment_count': len(fragments),
        'by_class': {k: classes.get(k, 0) for k in C.FRAGMENT_CLASSES},
        'orphan_count': len(orphan),
        'duplicate_fragment_ids': len(dupes),
        'missing_classes': missing,
        'invalid_sample': invalid,
        'unresolved_sense_alignment': sum(
            1 for f in fragments if f.get('sense_alignment') == 'unresolved'),
        'ok': (
            not orphan and not dupes and not missing and not invalid
            and set(classes) <= set(C.FRAGMENT_CLASSES)
        ),
    }
    return report


def run(canonical_path, out_dir):
    if canonical_path and os.path.exists(canonical_path):
        parents = C.read_jsonl(canonical_path)
    else:
        pubs = C.read_jsonl(C.DEFAULT_PUBLICATION)
        parents = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z')
                   for p in pubs]
    fragments = fragmentize_rows(parents)
    report = inventory(fragments, parents)
    out_jsonl = os.path.join(out_dir, 'fragments.v1.jsonl')
    C.write_jsonl(out_jsonl, fragments)
    report['artifact'] = os.path.relpath(out_jsonl, C.ROOT).replace('\\', '/')
    report['artifact_sha256'] = C.sha256_file(out_jsonl)
    C.write_json(os.path.join(out_dir, 'fragment_inventory.v1.json'), report)
    return fragments, report, out_jsonl


def verify():
    fix_pub = os.path.join(C.ROOT, 'schemas', 'fixtures',
                           'pwg_tm_canonical.publication.fixture.jsonl')
    pubs = C.read_jsonl(fix_pub)
    parents = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    frags = fragmentize_rows(parents)
    report = inventory(frags, parents)
    if not report['ok']:
        return False, 'fixture inventory failed: %s' % report
    if set(report['by_class']) != set(C.FRAGMENT_CLASSES):
        return False, 'fixture missing class: %s' % report['by_class']
    if any(report['by_class'][c] < 1 for c in C.FRAGMENT_CLASSES):
        return False, 'fixture empty class: %s' % report['by_class']
    schema = C.load_schema()
    for row in frags:
        ok, why = C.validate_canonical(row)
        if not ok:
            return False, 'fixture row: ' + why
        ok, why = C.validate_jsonschema(row, schema)
        if not ok:
            return False, 'fixture schema: ' + why
    again = fragmentize_rows(parents)
    if [f['fragment_id'] for f in again] != [f['fragment_id'] for f in frags]:
        return False, 'fixture fragment IDs not deterministic'
    if not os.path.exists(C.DEFAULT_PUBLICATION):
        return False, 'publication missing'
    with tempfile.TemporaryDirectory() as tmp:
        _frags, live, _out = run(None, tmp)
    if live['parent_count'] != C.EXPECTED_PUBLICATION_COUNT:
        return False, 'live parent count %d' % live['parent_count']
    if not live['ok']:
        return False, 'live inventory failed: %s' % {
            k: live[k] for k in (
                'parent_count', 'fragment_count', 'by_class', 'orphan_count',
                'duplicate_fragment_ids', 'missing_classes', 'invalid_sample',
            )
        }
    return True, 'fixture-ok %d; live-ok %d fragments / %d parents' % (
        len(frags), live['fragment_count'], live['parent_count'])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--canonical', default=os.path.join(C.DEFAULT_OUT_DIR, 'canonical.v1.jsonl'))
    ap.add_argument('--out-dir', default=C.DEFAULT_OUT_DIR)
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args(argv)
    if args.verify:
        ok, msg = verify()
        print(msg)
        return 0 if ok else 1
    src = args.canonical if os.path.exists(args.canonical) else None
    fragments, report, out_jsonl = run(src, args.out_dir)
    print('fragments %d -> %s ok=%s %s' % (
        len(fragments), out_jsonl, report['ok'], report['by_class']))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
