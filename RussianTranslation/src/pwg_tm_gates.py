#!/usr/bin/env python
"""Deterministic PWG TM fragment promotion gates (H2684 Track B).

Source anchoring, markup parity, Sanskrit preservation, completeness,
duplication, German residue, GAPS §17 surface-form (German `{%…%}` /
mutated `<ab>`), and provenance. Never a quality self-score.

  python src/pwg_tm_gates.py --selftest
  python src/pwg_tm_gates.py --scan PATH.jsonl
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

import pwg_tm_canonical as C  # noqa: E402
from markup_fidelity_gates import (  # noqa: E402
    SAN_RE, markup_span_flags, markup_wrapper_soft_flags, missing_target_flag,
)

GATE_VERSION = 'pwg.tm.gate.v1'
PROMOTE_STATUSES = ('pass',)
QUARANTINE_TIER = 'uncertain'

CYR_RE = re.compile(r'[А-Яа-яЁё]')
DE_LETTER_RE = re.compile(r'[äöüßÄÖÜ]')
DE_FUNC_RE = re.compile(
    r'\b(?:der|die|das|den|dem|des|ein|eine|einer|einem|einen|und|oder|'
    r'mit|von|für|nicht|auch|wird|sind|dass|wenn|bei|nach|auf|zum|zur)\b',
    re.I,
)
PRESERVE_SPAN_RE = re.compile(
    r'<ls\b[^>]*>.*?</ls>|<ab\b[^>]*>.*?</ab>|<lex\b[^>]*>.*?</lex>|'
    r'<lang\b[^>]*>.*?</lang>|<is\b[^>]*>.*?</is>|\{#.*?#\}',
    re.S,
)
GLOSS_INNER_RE = re.compile(r'\{%(.*?)%\}', re.S)
AB_SPAN_RE = re.compile(r'<ab\b[^>]*>.*?</ab>', re.S)
LATIN_RE = re.compile(r'[A-Za-zÄÖÜäöüß]')

COPY_SAFE = {
    'grammar_label': 'latin-or-tag copy-through is allowed',
    'citation': 'bibliographic <ls> copy-through is allowed',
    'example': 'pure Sanskrit {#…#} copy-through is allowed',
}

REQUIRED_PROVENANCE = (
    'model_id', 'route_id', 'prompt_sha256', 'pipeline_version', 'source_hash',
)


def _strip_preserve(text):
    return PRESERVE_SPAN_RE.sub(' ', text or '')


def _san_spans(text):
    return set(SAN_RE.findall(text or ''))


def source_anchor_flags(fragment):
    src = fragment.get('source_string') or ''
    flags = []
    if not src.strip():
        flags.append('SOURCE-EMPTY')
    got = fragment.get('source_hash')
    want = C.sha256_text(src)
    if got != want:
        flags.append('SOURCE-HASH-MISMATCH')
    return flags


def markup_flags(source, target, fragment_class):
    check_ab = fragment_class not in ('citation', 'example')
    hard = list(markup_span_flags(source, target, check_ab=check_ab))
    soft = list(markup_wrapper_soft_flags(source, target))
    return hard, soft


def sanskrit_flags(source, target):
    missing = _san_spans(source) - _san_spans(target)
    if missing:
        return ['SAN-DROP(%d)' % len(missing)]
    return []


def completeness_flags(fragment):
    klass = fragment.get('fragment_class')
    src = fragment.get('source_string') or ''
    tgt = fragment.get('target_string')
    flags = []
    if tgt is None or not str(tgt).strip():
        miss = missing_target_flag(bool(src.strip()), tgt or '', field='russian')
        flags.append(miss or 'MISSING-RU')
        return flags
    if klass in ('sense', 'definition_gloss'):
        prose = _strip_preserve(src)
        if DE_LETTER_RE.search(prose) or DE_FUNC_RE.search(prose):
            if not CYR_RE.search(_strip_preserve(tgt)):
                flags.append('NO-RUSSIAN')
    return flags


def residue_flags(fragment):
    klass = fragment.get('fragment_class')
    if klass in COPY_SAFE:
        return []
    tgt_prose = _strip_preserve(fragment.get('target_string') or '')
    flags = []
    if DE_LETTER_RE.search(tgt_prose):
        flags.append('DE-RESIDUE-LETTER')
    hits = sorted(set(m.group(0).lower() for m in DE_FUNC_RE.finditer(tgt_prose)))
    if hits:
        flags.append('DE-RESIDUE(%s)' % ','.join(hits[:6]))
    return flags


def german_gloss_flags(target):
    """GAPS §17: a `{%…%}` span whose inner text is still German/Latin, not Russian.

    Promotion requires zero German gloss wrappers in the target. A span with
    Cyrillic and no German letters/function-words is treated as translated.
    """
    for inner in GLOSS_INNER_RE.findall(target or ''):
        if DE_LETTER_RE.search(inner) or DE_FUNC_RE.search(inner):
            return ['GLOSS-DE-RESIDUE']
        if LATIN_RE.search(inner) and not CYR_RE.search(inner):
            return ['GLOSS-DE-RESIDUE']
    return []


def ab_identity_flags(source, target):
    """GAPS §17: every `<ab>…</ab>` in the target must be byte-identical to its source.

    Positional pairing; a count mismatch is also a mutation (AB-LOSS only fires
    on abs-drop ≥ 2, so a single rewritten abbreviation would otherwise pass).
    """
    src_abs = AB_SPAN_RE.findall(source or '')
    tgt_abs = AB_SPAN_RE.findall(target or '')
    if not src_abs and not tgt_abs:
        return []
    if len(src_abs) != len(tgt_abs):
        return ['AB-MUTATED']
    for a, b in zip(src_abs, tgt_abs):
        if a != b:
            return ['AB-MUTATED']
    return []


def surface_form_flags(source, target):
    """Both GAPS §17 predicates. Shared by pwg.tm.gate.v1 and audit_store_gates."""
    return german_gloss_flags(target) + ab_identity_flags(source, target)


def provenance_flags(fragment):
    prov = fragment.get('generation') or fragment.get('provenance') or {}
    if not isinstance(prov, dict):
        return ['PROVENANCE-MISSING']
    flags = []
    for key in REQUIRED_PROVENANCE:
        if not prov.get(key) and not (fragment.get(key)):
            flags.append('PROVENANCE-%s' % key.upper())
    return flags


def duplication_flags(fragments):
    """HARD DUP when two same-class siblings share a target but not a source."""
    by_parent = {}
    for frag in fragments:
        by_parent.setdefault(frag.get('parent_record_id'), []).append(frag)
    flagged = {}
    for rows in by_parent.values():
        seen = {}
        for frag in rows:
            tgt = re.sub(r'\s+', ' ', (frag.get('target_string') or '')).strip().lower()
            src = re.sub(r'\s+', ' ', (frag.get('source_string') or '')).strip().lower()
            if not tgt:
                continue
            klass = frag.get('fragment_class')
            if klass == 'recurring_formula':
                continue
            key = (klass, tgt)
            if key in seen and seen[key] != src:
                flagged[frag.get('fragment_id')] = ['DUP-TARGET']
                flagged.setdefault(seen.get('_id_' + str(key)), ['DUP-TARGET'])
            else:
                seen[key] = src
                seen['_id_' + str(key)] = frag.get('fragment_id')
    return flagged


def gate_fragment(fragment, sibling_dup=None):
    src = fragment.get('source_string') or ''
    tgt = fragment.get('target_string') or ''
    klass = fragment.get('fragment_class')
    hard = []
    soft = []
    hard.extend(source_anchor_flags(fragment))
    m_hard, m_soft = markup_flags(src, tgt, klass)
    hard.extend(m_hard)
    soft.extend(m_soft)
    hard.extend(sanskrit_flags(src, tgt))
    hard.extend(completeness_flags(fragment))
    hard.extend(residue_flags(fragment))
    if klass not in COPY_SAFE:
        hard.extend(german_gloss_flags(tgt))
    hard.extend(ab_identity_flags(src, tgt))
    hard.extend(provenance_flags(fragment))
    if sibling_dup:
        hard.extend(sibling_dup)
    ok = not hard
    return {
        'schema': 'pwg.tm.gate.receipt.v1',
        'gate_version': GATE_VERSION,
        'fragment_id': fragment.get('fragment_id'),
        'fragment_class': klass,
        'ok': ok,
        'gate_status': 'pass' if ok else 'fail',
        'hard': hard,
        'soft': soft,
        'confidence_tier': 'machine_gated' if ok else QUARANTINE_TIER,
        'reuse_policy': 'auto_exact' if ok else 'suggest_only',
        'trust_level': 'machine_exact' if ok else 'suggestion',
    }


def gate_rows(fragments):
    dups = duplication_flags(fragments)
    receipts = []
    for frag in fragments:
        rec = gate_fragment(frag, sibling_dup=dups.get(frag.get('fragment_id')))
        receipts.append(rec)
    return receipts


def apply_gate(fragment, receipt):
    out = dict(fragment)
    out['gate_status'] = receipt['gate_status']
    out['gate_version'] = GATE_VERSION
    out['gate_receipt'] = receipt
    out['confidence_tier'] = receipt['confidence_tier']
    out['reuse_policy'] = receipt['reuse_policy']
    out['trust_level'] = receipt['trust_level']
    if receipt['ok']:
        out['promotion_status'] = 'promoted'
        out['quarantine_reasons'] = []
    else:
        out['promotion_status'] = 'quarantine'
        out['quarantine_reasons'] = list(receipt['hard'])
    return out


def _selftest():
    src = '<lex>m.</lex> {%Feuer.%} <ls>ṚV. 1,1,1</ls> {#agni#}'
    good = {
        'fragment_id': 't-good',
        'fragment_class': 'sense',
        'parent_record_id': 'p1',
        'source_string': src,
        'source_hash': C.sha256_text(src),
        'target_string': '<lex>m.</lex> {%огонь.%} <ls>ṚV. 1,1,1</ls> {#agni#}',
        'generation': {
            'model_id': 'grok-4.6',
            'route_id': 'grok-4.6',
            'prompt_sha256': 'a' * 64,
            'pipeline_version': 'pwg_tm_generate.v1',
            'source_hash': C.sha256_text(src),
        },
    }
    rec = gate_fragment(good)
    assert rec['ok'], rec
    bad_src = dict(good, source_hash='0' * 64)
    assert 'SOURCE-HASH-MISMATCH' in gate_fragment(bad_src)['hard']
    dropped = dict(good, target_string='{%огонь.%}')
    flags = gate_fragment(dropped)['hard']
    assert any(f.startswith('SAN-DROP') or f.startswith('LS-LOSS') or f.startswith('AB-LOSS')
               for f in flags), flags
    residue = dict(good, target_string=good['target_string'] + ' und Feuer')
    assert any(f.startswith('DE-RESIDUE') for f in gate_fragment(residue)['hard'])
    empty = dict(good, target_string='')
    assert 'MISSING-RU' in gate_fragment(empty)['hard']
    no_prov = {
        'fragment_id': 't-np',
        'fragment_class': 'sense',
        'source_string': 'x',
        'source_hash': C.sha256_text('x'),
        'target_string': 'икс',
    }
    assert any(f.startswith('PROVENANCE-') for f in gate_fragment(no_prov)['hard'])
    a = dict(good, fragment_id='d1', target_string='{%огонь%}', source_string='{%Feuer%}',
             source_hash=C.sha256_text('{%Feuer%}'))
    b = dict(good, fragment_id='d2', target_string='{%огонь%}', source_string='{%Brand%}',
             source_hash=C.sha256_text('{%Brand%}'))
    dups = duplication_flags([a, b])
    assert 'd1' in dups and 'd2' in dups
    applied = apply_gate(empty, gate_fragment(empty))
    assert applied['promotion_status'] == 'quarantine'
    assert applied['quarantine_reasons']
    # GAPS §17 canaries (H2684 / 27-08 sidecar): untranslated German gloss + mutated <ab>.
    upakrama = dict(good, fragment_id='t-upakrama',
                    source_string='4〉 {%Antritt, Anfang, Beginn%}',
                    source_hash=C.sha256_text('4〉 {%Antritt, Anfang, Beginn%}'),
                    target_string='4〉 {%Antritt, Anfang, Beginn%}')
    assert 'GLOSS-DE-RESIDUE' in gate_fragment(upakrama)['hard'], gate_fragment(upakrama)
    atmasat = dict(good, fragment_id='t-atmasat',
                   source_string='{%an sich, zu sich, auf sich%} {%thun%}',
                   source_hash=C.sha256_text('{%an sich, zu sich, auf sich%} {%thun%}'),
                   target_string='{%an sich, zu sich, auf sich%} {%класть%}')
    assert 'GLOSS-DE-RESIDUE' in gate_fragment(atmasat)['hard'], gate_fragment(atmasat)
    tarura = dict(good, fragment_id='t-tarura', fragment_class='recurring_formula',
                  source_string='<ab>v. a.</ab>',
                  source_hash=C.sha256_text('<ab>v. a.</ab>'),
                  target_string='<ab>т. е.</ab>')
    assert 'AB-MUTATED' in gate_fragment(tarura)['hard'], gate_fragment(tarura)
    ab_ok = dict(good, fragment_id='t-abok', fragment_class='recurring_formula',
                 source_string='<ab>v. a.</ab>',
                 source_hash=C.sha256_text('<ab>v. a.</ab>'),
                 target_string='<ab>v. a.</ab>')
    assert 'AB-MUTATED' not in gate_fragment(ab_ok)['hard'], gate_fragment(ab_ok)
    print('pwg_tm_gates: PASS')
    return 0


def scan_fragments(path):
    """Census GAPS §17 predicates over a fragment jsonl (promoted dump or sample)."""
    n = 0
    gloss = []
    ab = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            frag = json.loads(line)
            n += 1
            src = frag.get('source_string') or ''
            tgt = frag.get('target_string') or ''
            rec = {
                'key1': ((frag.get('source_locator') or {}).get('key1')
                         or frag.get('entry_id')),
                'fragment_id': frag.get('fragment_id') or frag.get('record_id'),
                'fragment_class': frag.get('fragment_class'),
                'flags': surface_form_flags(src, tgt),
            }
            if 'GLOSS-DE-RESIDUE' in rec['flags']:
                gloss.append(rec)
            if 'AB-MUTATED' in rec['flags']:
                ab.append(rec)
    return {'rows': n, 'gloss_de_residue': gloss, 'ab_mutated': ab}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--scan', metavar='JSONL',
                    help='census GAPS §17 surface-form flags over a fragment jsonl')
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.scan:
        result = scan_fragments(args.scan)
        print('=== pwg.tm.gate.v1 GAPS §17 census: %s' % args.scan)
        print('rows=%d GLOSS-DE-RESIDUE=%d AB-MUTATED=%d' % (
            result['rows'], len(result['gloss_de_residue']), len(result['ab_mutated'])))
        for rec in (result['gloss_de_residue'] + result['ab_mutated'])[:30]:
            print('  %-16s %-22s %s %s' % (
                rec.get('key1') or '', (rec.get('fragment_class') or '')[:22],
                rec.get('fragment_id') or '', ' '.join(rec['flags'])))
        print('CENSUS_JSON: %s' % json.dumps({
            'rows': result['rows'],
            'gloss_de_residue': len(result['gloss_de_residue']),
            'ab_mutated': len(result['ab_mutated']),
            'gloss_keys': sorted({r.get('key1') for r in result['gloss_de_residue']}),
            'ab_keys': sorted({r.get('key1') for r in result['ab_mutated']}),
        }, ensure_ascii=False))
        return 1 if (result['gloss_de_residue'] or result['ab_mutated']) else 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
