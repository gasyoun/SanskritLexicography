#!/usr/bin/env python
"""Deterministic PWG TM fragment promotion gates (H2684 Track B).

Source anchoring, markup parity, Sanskrit preservation, completeness,
duplication, German residue, and provenance. Never a quality self-score.

  python src/pwg_tm_gates.py --selftest
"""
from __future__ import annotations

import argparse
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
    print('pwg_tm_gates: PASS')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
