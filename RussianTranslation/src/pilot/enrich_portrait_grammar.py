#!/usr/bin/env python
"""Attach the Whitney grammar block to a root's pwg_ru portraits (the 3rd layer).

A root's sub-cards (anugam, abhigam, … for gam) share the root's conjugation, so each
sub-card portrait gets the same root-level `grammar` block (sibling of `corpus_synonyms`)
— class, PPP, period tags, corpus-attested forms, Whitney §§ per form-category, and a
derived `irregularities` exception list. Baking it into the portrait means the translator
sees grammar during the DE→RU pass (the portrait is inlined by the harness), so the data
is enriched once, not bolted on later.

  python src/pilot/enrich_portrait_grammar.py gam              dry-run: report + show one enriched portrait
  python src/pilot/enrich_portrait_grammar.py gam --apply      write the grammar block into the portraits

Homonym note: multi-Whitney-record roots (as, i, vid) need PWG-homonym↔Whitney-homonym
alignment first; this prototype attaches all matching records and flags it.
"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))     # RussianTranslation/src
from whitney_grammar import grammar_for
from window_common import INP


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit('usage: enrich_portrait_grammar.py <root> [--apply]')
    root = args[0]
    apply = '--apply' in args
    recs = grammar_for(root)
    if not recs:
        sys.exit('no Whitney grammar record for root %r — nothing to attach' % root)
    ambiguous = len(recs) > 1
    grammar = {'records': recs, 'join': 'pwg_root_slp1==whitney_root_slp1',
               'homonym_aligned': not ambiguous}

    paths = sorted(glob.glob(os.path.join(INP, '%s~~*.portrait.json' % root)))
    if not paths:
        sys.exit('no portraits for root %r under %s' % (root, INP))

    changed = 0
    sample = None
    for p in paths:
        port = json.load(open(p, encoding='utf-8'))
        # portrait is a list of homonym dicts; attach the root grammar to each
        for entry in (port if isinstance(port, list) else [port]):
            entry['grammar'] = grammar
        if apply:
            json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        changed += 1
        if sample is None:
            sample = (os.path.basename(p), port)

    print('root %s: %d Whitney record(s)%s | portraits %s: %d'
          % (root, len(recs), ' (AMBIGUOUS — homonym alignment needed)' if ambiguous else '',
             'written' if apply else 'would enrich', changed))
    if not apply and sample:
        name, port = sample
        print('\n=== enriched portrait sample: %s ===' % name)
        print(json.dumps(port, ensure_ascii=False, indent=2)[:2600])


if __name__ == '__main__':
    main()
