#!/usr/bin/env python
"""Attach the nominal grammar block to a headword's pwg_ru portrait (non-root layer).

Parallel to enrich_portrait_grammar.py for verb roots. Attaches stem-class,
Whitney §§, compound members, and irregularity flags to the portrait JSON so the
harness can inline the data during the DE→RU pass.

  python src/pilot/enrich_portrait_nominal_grammar.py agni m.             dry-run
  python src/pilot/enrich_portrait_nominal_grammar.py agni m. --apply     write
  python src/pilot/enrich_portrait_nominal_grammar.py --all --lex-from-portrait  # batch mode

The <lex> tag is required because the same k1 may have multiple lex variants.
Batch mode reads the `lex` field from existing portrait JSON if present.
"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))   # RussianTranslation/src
from nominal_grammar import nominal_grammar_for
from window_common import INP


def _lex_from_portrait(port):
    """Best-effort lex extraction from an existing portrait JSON."""
    if isinstance(port, list) and port:
        port = port[0]
    return (port.get('lex') or port.get('gender') or
            port.get('pos') or '')


def enrich_one(slp1, lex, apply=False):
    """Enrich all portrait files for the given SLP1 headword."""
    rec = nominal_grammar_for(slp1, lex)
    grammar = {
        'stem_class': rec['stem_class'],
        'gender': rec['gender'],
        'declension_sections': rec['declension_sections'],
        'paradigm_section': rec.get('paradigm_section'),
        'compound_members': rec['compound_members'],
        'compound_sections': rec['compound_sections'],
        'irregularities': rec['irregularities'],
        'source': rec['source'],
    }
    paths = sorted(glob.glob(os.path.join(INP, '%s~~*.portrait.json' % slp1)))
    if not paths:
        print('no portraits for %r under %s' % (slp1, INP))
        return 0
    changed = 0
    sample = None
    for p in paths:
        port = json.load(open(p, encoding='utf-8'))
        entries = port if isinstance(port, list) else [port]
        for entry in entries:
            entry['nominal_grammar'] = grammar
        if apply:
            json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        changed += 1
        if sample is None:
            sample = (os.path.basename(p), port)
    print('%s [%s]: %s (%s)%s | portraits %s: %d'
          % (slp1, lex, rec['stem_class'], rec['declension_sections'],
             ' compound:%s' % '+'.join(rec['compound_members']) if rec['compound_members'] else '',
             'written' if apply else 'would enrich', changed))
    if not apply and sample:
        name, port = sample
        print('\n=== enriched portrait sample: %s ===' % name)
        print(json.dumps(port, ensure_ascii=False, indent=2)[:2000])
    return changed


def main():
    args = sys.argv[1:]
    if not args or '--help' in args or '-h' in args:
        print(__doc__)
        return
    apply = '--apply' in args
    args = [a for a in args if a not in ('--apply',)]

    if args[0] == '--all':
        # batch mode: enrich every portrait whose lex can be read
        lex_from_portrait = '--lex-from-portrait' in args
        paths = sorted(glob.glob(os.path.join(INP, '*.portrait.json')))
        total = 0
        for p in paths:
            slp1 = os.path.basename(p).split('~~')[0]
            try:
                port = json.load(open(p, encoding='utf-8'))
            except Exception:
                continue
            lex = _lex_from_portrait(port) if lex_from_portrait else ''
            if not lex:
                continue
            total += enrich_one(slp1, lex, apply=apply)
        print('batch done: %d portraits enriched' % total)
        return

    # single headword mode
    if len(args) < 2:
        sys.exit('usage: enrich_portrait_nominal_grammar.py <SLP1> <lex> [--apply]')
    slp1, lex = args[0], args[1]
    enrich_one(slp1, lex, apply=apply)


if __name__ == '__main__':
    main()
