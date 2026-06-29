#!/usr/bin/env python
"""Attach the nominal grammar block to a headword's pwg_ru portrait (non-root layer).

Parallel to enrich_portrait_grammar.py for verb roots. Attaches stem-class,
Whitney §§, compound members, and irregularity flags to the portrait JSON so the
harness can inline the data during the DE→RU pass.

  python src/pilot/enrich_portrait_nominal_grammar.py agni m.             dry-run
  python src/pilot/enrich_portrait_nominal_grammar.py agni m. --apply     write
  python src/pilot/enrich_portrait_nominal_grammar.py --all               batch (lex from portrait pos)

Portrait facts (csl-orig PWG portraits): the SLP1 key is the `key1` field, the
filename stem is safe_name(key1), and POS is the `pos` list (e.g. ['n.']). Batch
mode reads key1 + pos[0] from each non-root portrait directly.
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
from safe_filename import safe_name, candidate_names
from window_common import INP


# Concrete substantive genders, preferred over adj./adv. when a portrait lists
# several POS tags (a noun's paradigm keys off its gender, not its adj. use).
_GENDER_PRIORITY = ('m.', 'f.', 'n.', 'm.n.', 'm.f.', 'f.n.', 'm.f.n.')


def _lex_of(entry):
    """Normalize a portrait POS/lex field (list or string) to a single lex tag.
    When several tags are present, prefer a concrete noun gender so the stem-class
    paradigm and irregularity flags reflect the substantive, not its adj./adv. use."""
    val = entry.get('lex') or entry.get('pos') or entry.get('gender') or ''
    if isinstance(val, (list, tuple)):
        tags = [str(t).strip() for t in val if str(t).strip()]
        if not tags:
            return ''
        for g in _GENDER_PRIORITY:
            if g in tags:
                return g
        return tags[0]
    return str(val).strip()


def _slp1_of(entry, fallback_stem=''):
    """SLP1 headword key from a portrait entry; key1 is canonical."""
    return entry.get('key1') or entry.get('slp1') or fallback_stem


def _portrait_path(slp1):
    """Locate the portrait file for an SLP1 key via safe_name (and legacy stem)."""
    for stem in candidate_names(slp1):
        p = os.path.join(INP, stem + '.portrait.json')
        if os.path.exists(p):
            return p
    return None


def _grammar_block(slp1, lex):
    rec = nominal_grammar_for(slp1, lex)
    return {
        'stem_class': rec['stem_class'],
        'gender': rec['gender'],
        'declension_sections': rec['declension_sections'],
        'paradigm_section': rec.get('paradigm_section'),
        'compound_members': rec['compound_members'],
        'compound_sections': rec['compound_sections'],
        'irregularities': rec['irregularities'],
        'source': rec['source'],
    }


def enrich_path(p, slp1, lex, apply=False):
    """Enrich a single portrait FILE in place; returns the loaded port (for sampling)."""
    grammar = _grammar_block(slp1, lex)
    port = json.load(open(p, encoding='utf-8'))
    for entry in (port if isinstance(port, list) else [port]):
        entry['nominal_grammar'] = grammar
    if apply:
        json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return port, grammar


def enrich_one(slp1, lex, apply=False):
    p = _portrait_path(slp1)
    if not p:
        print('no portrait for %r (tried %s) under %s'
              % (slp1, candidate_names(slp1), INP))
        return 0
    port, grammar = enrich_path(p, slp1, lex, apply=apply)
    print('%s [%s]: %s (%s)%s | %s: %s'
          % (slp1, lex, grammar['stem_class'], grammar['declension_sections'],
             ' compound:%s' % '+'.join(grammar['compound_members']) if grammar['compound_members'] else '',
             'written' if apply else 'would enrich', os.path.basename(p)))
    if not apply:
        print('\n=== enriched portrait sample ===')
        print(json.dumps(port, ensure_ascii=False, indent=2)[:2000])
    return 1


def enrich_all(apply=False, limit=None):
    """Batch: enrich every NON-root portrait, reading key1 + pos from each file."""
    paths = sorted(glob.glob(os.path.join(INP, '*.portrait.json')))
    n = skipped = 0
    for p in paths:
        if '~~' in os.path.basename(p):
            continue                                   # root sub-cards use the root layer
        try:
            port = json.load(open(p, encoding='utf-8'))
        except Exception:
            skipped += 1
            continue
        entry0 = port[0] if isinstance(port, list) else port
        slp1 = _slp1_of(entry0)
        lex = _lex_of(entry0)
        if not slp1 or not lex:
            skipped += 1
            continue
        enrich_path(p, slp1, lex, apply=apply)
        n += 1
        if limit and n >= limit:
            break
    print('batch %s: %d portraits enriched, %d skipped (no key1/pos)'
          % ('written' if apply else 'dry-run', n, skipped))
    return n


def main():
    args = sys.argv[1:]
    if not args or '--help' in args or '-h' in args:
        print(__doc__)
        return
    apply = '--apply' in args
    limit = None
    for a in args:
        if a.startswith('--limit='):
            limit = int(a.split('=', 1)[1])
    args = [a for a in args if not a.startswith('--')]

    if '--all' in sys.argv[1:]:
        enrich_all(apply=apply, limit=limit)
        return

    if len(args) < 2:
        sys.exit('usage: enrich_portrait_nominal_grammar.py <SLP1> <lex> [--apply]')
    enrich_one(args[0], args[1], apply=apply)


if __name__ == '__main__':
    main()
