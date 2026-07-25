#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Attach the PWG derivation block to a headword's pwg_ru portraits (a grammar layer,
sibling of `grammar` / `corpus_synonyms`) — H1282, the 4th of the cheap PWG layers.

Baking it into the portrait means the translator sees the derivation during the DE→RU
pass (the portrait is inlined by the harness), the same rationale as
enrich_portrait_grammar.py (Whitney root grammar). The block carries, per headword:
  - derivation : denominal base + suffix + class + <ls> citation (taddhita)
  - panini     : the Aṣṭādhyāyī sūtra(s) PWG cites for the form
  - compound   : PWG's member split + how it compares to the index's compound_members
  - gana       : the Pāṇinian gaṇa(s) the word belongs to (external Gaṇapāṭha), + a
                 `corroborated` flag when PWG cites the gaṇa's governing sūtra

Source is the committed join sidecar src/pwg_derivation_layer.tsv (built by
src/pwg_derivation_layer.py from the SanskritGrammar PWG layers + the L_id↔hom map).
Homonyms: the sidecar is now keyed by (k1, hom), so each portrait's block is matched to
its homonym via the `~~h<N>` token in the portrait filename — derivation/compound pin to
the EXACT homonym (`homonym_precise`); Pāṇini is k1-level (aggregated upstream). A portrait
whose homonym has no exact sidecar row falls back to the k1-level block.

  python src/pilot/enrich_portrait_derivation.py aMSaka           dry-run: report + show one enriched portrait
  python src/pilot/enrich_portrait_derivation.py aMSaka --apply    write the block into the portraits
  python src/pilot/enrich_portrait_derivation.py --selftest        verify attach logic on a synthetic portrait

Note: the portrait store (pilot/input/) is local-only/gitignored, so --apply runs on
the maintainer's local portraits; --selftest proves the block-attachment logic here.
"""
import csv
import glob
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))                 # src/pilot
SRC = os.path.dirname(HERE)                                       # src
SIDECAR = os.path.join(SRC, 'pwg_derivation_layer.tsv')


# Compound statuses that mean layers disagree or need a human eye (H1624 G6).
# ``differs`` = PWG split ≠ index compound_members (~4.2k) — never auto-fixed.
# ``index-only`` = index has members but PWG layer has none (optional review).
CONFLICT_STATUSES = frozenset({'differs'})
NEEDS_HUMAN_STATUSES = frozenset({'differs', 'index-only'})


def _flags_for_compound_status(status: str) -> dict:
    """Machine-safe conflict flags — never adjudicates the split."""
    st = (status or '').strip()
    return {
        'conflict': st in CONFLICT_STATUSES,
        'needs_human': st in NEEDS_HUMAN_STATUSES,
        'conflict_kind': 'compound_split' if st in CONFLICT_STATUSES else (
            'compound_index_only' if st == 'index-only' else None),
    }


def row_to_block(r: dict) -> dict:
    """Build one derivation block from a sidecar TSV row (shared by load + store path)."""
    b = {'source': 'pwg_derivation_layer.tsv',
         'homonym_precise': bool(r.get('homonym_precise'))}
    if r.get('deriv_suffix'):
        b['derivation'] = {'base': r.get('deriv_base') or '',
                           'suffix': r['deriv_suffix'],
                           'class': r.get('deriv_class') or '',
                           'citation': r.get('deriv_citation') or ''}
    if r.get('panini_sutras'):
        b['panini'] = [s for s in r['panini_sutras'].split('|') if s]
    status = (r.get('compound_status') or '').strip()
    if r.get('compound_members_pwg') or status:
        members = r.get('compound_members_pwg') or ''
        b['compound'] = {
            'members': members,
            'vs_index': status,
        }
        b['compound'].update(_flags_for_compound_status(status))
    # Top-level flags for portrait consumers that do not dig into compound
    flags = _flags_for_compound_status(status)
    b['conflict'] = flags['conflict']
    b['needs_human'] = flags['needs_human']
    if flags['conflict_kind']:
        b['conflict_kind'] = flags['conflict_kind']
    if r.get('ganas'):
        b['gana'] = {'ganas': r['ganas'].split('|'),
                     'sutras': [s for s in r.get('gana_sutras', '').split('|') if s],
                     'corroborated': bool(r.get('gana_corroborated'))}
    return b


def load_blocks(path=SIDECAR):
    """Return (blocks_kh, blocks_k1): (k1,hom)->block (homonym-precise) and k1->block
    (fallback / k1-level, first row per k1) built from the join sidecar."""
    blocks_kh, blocks_k1 = {}, {}
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            k1, hom = r['k1'], r['hom']
            b = row_to_block(r)
            blocks_kh[(k1, hom)] = b
            blocks_k1.setdefault(k1, b)
    return blocks_kh, blocks_k1


def derivation_for_key(key1: str, hom: str = '', path=SIDECAR) -> dict | None:
    """Lookup one derivation block by k1 (+ optional hom). Public API for promote/store."""
    blocks_kh, blocks_k1 = load_blocks(path)
    if hom != '' and (key1, str(hom)) in blocks_kh:
        return blocks_kh[(key1, str(hom))]
    return blocks_k1.get(key1)


def conflict_rate_report(path=SIDECAR) -> dict:
    """Honest census of compound conflict / needs_human over the committed sidecar."""
    from collections import Counter
    status = Counter()
    n = n_conflict = n_needs = 0
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            n += 1
            st = (r.get('compound_status') or '').strip()
            status[st or '(empty)'] += 1
            flags = _flags_for_compound_status(st)
            if flags['conflict']:
                n_conflict += 1
            if flags['needs_human']:
                n_needs += 1
    return {
        'rows': n,
        'conflict': n_conflict,
        'conflict_pct': round(100.0 * n_conflict / n, 2) if n else 0.0,
        'needs_human': n_needs,
        'needs_human_pct': round(100.0 * n_needs / n, 2) if n else 0.0,
        'by_status': dict(status.most_common()),
        'note': ('differs rows are a human review queue (~4.2k) — never auto-adjudicated '
                 '(H1282 / H1624 G6). Point at /review-sheet for a sample, not bulk close.'),
    }


def enrich_portrait_obj(port, block):
    """Attach `derivation` block to each homonym entry of a portrait object. In place.

    Never overwrites a human-reviewed derivation overlay: if an entry already has
    ``derivation.human_reviewed`` truthy, leave it untouched (H1624 G6).
    """
    for entry in (port if isinstance(port, list) else [port]):
        existing = entry.get('derivation')
        if isinstance(existing, dict) and existing.get('human_reviewed'):
            continue
        entry['derivation'] = block
    return port


def hom_from_filename(name):
    """`aMSaka~~h2_00_x.portrait.json` -> '2' (index hom is the bare number; the subcard
    token is `h<N>`). Returns '' if not determinable."""
    m = re.search(r'~~h?(\d+)_', name)
    return m.group(1) if m else ''


def run_key(key, apply):
    from window_common import INP
    blocks_kh, blocks_k1 = load_blocks()
    if key not in blocks_k1:
        sys.exit('no PWG derivation layer for %r — nothing to attach' % key)
    paths = sorted(glob.glob(os.path.join(INP, '%s~~*.portrait.json' % key)))
    if not paths:
        sys.exit('no portraits for %r under %s (local-only store)' % (key, INP))
    changed = pinned = 0
    sample = None
    for p in paths:
        hom = hom_from_filename(os.path.basename(p))
        block = blocks_kh.get((key, hom))
        if block is not None:
            pinned += 1
        else:
            block = blocks_k1[key]              # k1-level fallback (singleton / unmatched hom)
        port = json.load(open(p, encoding='utf-8'))
        enrich_portrait_obj(port, block)
        if apply:
            json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        changed += 1
        if sample is None:
            sample = (os.path.basename(p), port)
    print('key %s: portraits %s: %d (homonym-pinned via map: %d)'
          % (key, 'written' if apply else 'would enrich', changed, pinned))
    if not apply and sample:
        name, port = sample
        print('\n=== enriched portrait sample: %s ===' % name)
        print(json.dumps(port, ensure_ascii=False, indent=2)[:2200])


def selftest():
    """Prove the attach + homonym-match + conflict flags (real store is local-only)."""
    block = {'source': 'x', 'homonym_precise': True,
             'derivation': {'base': 'aMSa', 'suffix': 'ka', 'class': 'уменьш.', 'citation': 'AK.'},
             'panini': ['P.5.2.69'],
             'compound': {'members': 'a + b', 'vs_index': 'agrees',
                          'conflict': False, 'needs_human': False, 'conflict_kind': None},
             'conflict': False, 'needs_human': False,
             'gana': {'ganas': ['saNkASAdiH'], 'sutras': ['4.2.80'], 'corroborated': True}}
    port = [{'key1': 'aMSaka', 'senses': []}, {'key1': 'aMSaka', 'senses': []}]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'aMSaka~~h2_00_x.portrait.json')
        json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        loaded = json.load(open(p, encoding='utf-8'))
        enrich_portrait_obj(loaded, block)
        json.dump(loaded, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        back = json.load(open(p, encoding='utf-8'))
    assert all(e['derivation'] == block for e in back), 'block not attached to every entry'
    assert back[0]['senses'] == [], 'existing fields must be preserved'
    assert hom_from_filename('aMSaka~~h2_00_x.portrait.json') == '2', 'filename homonym parse'
    assert hom_from_filename('foo~~h0_zz_y.portrait.json') == '0', 'singleton homonym parse'
    # human_reviewed overlay must not be overwritten
    human = {'key1': 'x', 'derivation': {'human_reviewed': True, 'note': 'keep-me'},
             'senses': []}
    enrich_portrait_obj(human, block)
    assert human['derivation']['note'] == 'keep-me', 'must not wipe human_reviewed overlay'
    # conflict flags from compound_status
    flags = _flags_for_compound_status('differs')
    assert flags['conflict'] and flags['needs_human'] and flags['conflict_kind'] == 'compound_split'
    flags2 = _flags_for_compound_status('agrees')
    assert not flags2['conflict'] and not flags2['needs_human']
    flags3 = _flags_for_compound_status('index-only')
    assert not flags3['conflict'] and flags3['needs_human']
    # row_to_block surfaces flags
    b = row_to_block({'k1': 'x', 'hom': '0', 'homonym_precise': '1',
                      'compound_members_pwg': 'a + b', 'compound_status': 'differs'})
    assert b['conflict'] is True and b['needs_human'] is True, b
    assert b['compound']['vs_index'] == 'differs', b
    # sidecar sanity
    blocks_kh, blocks_k1 = load_blocks()
    assert 'aMSaka' in blocks_k1 and blocks_k1['aMSaka'].get('derivation', {}).get('suffix') == 'ka', \
        'sidecar join missing expected aMSaka derivation'
    # conflict rate (committed sidecar) — report, never adjudicate
    rep = conflict_rate_report()
    assert rep['rows'] > 0 and 'differs' in str(rep['by_status']), rep
    assert rep['conflict'] >= 4000, 'expected ~4.2k differs queue, got %s' % rep['conflict']
    print('selftest OK — attaches + preserves fields; human_reviewed guard; conflict flags; '
          'sidecar parses (%d k1, %d (k1,hom)); conflict_rate=%s/%s (%.2f%%)'
          % (len(blocks_k1), len(blocks_kh), rep['conflict'], rep['rows'], rep['conflict_pct']))


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        selftest()
        return
    if '--conflict-rate' in args:
        print(json.dumps(conflict_rate_report(), ensure_ascii=False, indent=2))
        return
    if not args:
        sys.exit('usage: enrich_portrait_derivation.py <k1> [--apply] | --selftest | --conflict-rate')
    run_key(args[0], '--apply' in args)


if __name__ == '__main__':
    main()
