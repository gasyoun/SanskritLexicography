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

Source is the committed join sidecar src/pwg_derivation_layer.tsv (built by
src/pwg_derivation_layer.py from the three SanskritGrammar PWG layers). Homonyms: the
sidecar keys on k1 only (no L_id↔hom map committed upstream), so the block is attached
to every homonym entry of a k1 and `homonym_ambiguous` is carried through — the same
attach-all-and-flag policy as enrich_portrait_grammar.py.

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
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))                 # src/pilot
SRC = os.path.dirname(HERE)                                       # src
SIDECAR = os.path.join(SRC, 'pwg_derivation_layer.tsv')


def load_blocks(path=SIDECAR):
    """k1 -> derivation block dict (built from the join sidecar)."""
    blocks = {}
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            k1 = r['k1']
            if k1 in blocks:
                continue          # first homonym row wins; block is per-k1
            b = {'source': 'pwg_derivation_layer.tsv',
                 'homonym_ambiguous': bool(r.get('homonym_ambiguous'))}
            if r.get('deriv_suffix'):
                b['derivation'] = {'base': r['deriv_base'], 'suffix': r['deriv_suffix'],
                                   'class': r['deriv_class'], 'citation': r['deriv_citation']}
            if r.get('panini_sutras'):
                b['panini'] = r['panini_sutras'].split('|')
            if r.get('compound_members_pwg'):
                b['compound'] = {'members': r['compound_members_pwg'],
                                 'vs_index': r['compound_status']}
            blocks[k1] = b
    return blocks


def enrich_portrait_obj(port, block):
    """Attach `derivation` block to each homonym entry of a portrait object. In place."""
    for entry in (port if isinstance(port, list) else [port]):
        entry['derivation'] = block
    return port


def run_key(key, apply):
    from window_common import INP
    blocks = load_blocks()
    block = blocks.get(key)
    if not block:
        sys.exit('no PWG derivation layer for %r — nothing to attach' % key)
    paths = sorted(glob.glob(os.path.join(INP, '%s~~*.portrait.json' % key)))
    if not paths:
        sys.exit('no portraits for %r under %s (local-only store)' % (key, INP))
    changed = 0
    sample = None
    for p in paths:
        port = json.load(open(p, encoding='utf-8'))
        enrich_portrait_obj(port, block)
        if apply:
            json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        changed += 1
        if sample is None:
            sample = (os.path.basename(p), port)
    print('key %s: portraits %s: %d%s'
          % (key, 'written' if apply else 'would enrich', changed,
             ' (homonym-ambiguous — attached to all)' if block['homonym_ambiguous'] else ''))
    if not apply and sample:
        name, port = sample
        print('\n=== enriched portrait sample: %s ===' % name)
        print(json.dumps(port, ensure_ascii=False, indent=2)[:2200])


def selftest():
    """Prove the attach logic on a synthetic portrait (real store is local-only)."""
    block = {'source': 'x', 'homonym_ambiguous': True,
             'derivation': {'base': 'aMSa', 'suffix': 'ka', 'class': 'уменьш.', 'citation': 'AK.'},
             'panini': ['P.5.2.69'], 'compound': {'members': 'a + b', 'vs_index': 'agrees'}}
    port = [{'key1': 'aMSaka1', 'senses': []}, {'key1': 'aMSaka2', 'senses': []}]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'aMSaka~~x.portrait.json')
        json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        loaded = json.load(open(p, encoding='utf-8'))
        enrich_portrait_obj(loaded, block)
        json.dump(loaded, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        back = json.load(open(p, encoding='utf-8'))
    assert all(e['derivation'] == block for e in back), 'block not attached to every homonym'
    assert back[0]['senses'] == [], 'existing fields must be preserved'
    # sidecar sanity: the committed join exists and parses
    blocks = load_blocks()
    assert 'aMSaka' in blocks and blocks['aMSaka'].get('derivation', {}).get('suffix') == 'ka', \
        'sidecar join missing expected aMSaka derivation'
    print('selftest OK — block attaches to every homonym, preserves fields; sidecar join parses (%d k1)' % len(blocks))


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        selftest()
        return
    if not args:
        sys.exit('usage: enrich_portrait_derivation.py <k1> [--apply] | --selftest')
    run_key(args[0], '--apply' in args)


if __name__ == '__main__':
    main()
