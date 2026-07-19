#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the PWG derivation layer for pwg_ru — join the three SanskritGrammar PWG
data layers onto the pwg_ru headword index, keyed by headword (k1).

Consumes (canonical, read-only; the sibling SanskritGrammar repo — like the pipeline
already reads csl-orig / WhitneyRoots):
  - taddhita derivations : sangram/articles/taddhita-overview/data/pwg_taddhita_derivations.tsv
                           (denominal base + suffix + class + <ls> citation)
  - Pāṇini crosswalk     : data/pwg_panini_crosswalk/pwg_panini_word2sutra.tsv
                           (headword → licensing sūtra(s))
  - compound splits      : data/pwg_compound_split/pwg_compound_splits.tsv
                           (headword → ordered members)

Joins each onto RussianTranslation/src/headword_index.tsv on `k1` (SLP1 headword).
Homonyms: the SanskritGrammar layers key on headword + PWG L_id, the index keys on
k1 + hom; there is no committed L_id↔hom map, so a layer value is attached to every
homonym row of that k1 and `homonym_ambiguous` is set when the k1 has >1 index row —
the same attach-all-and-flag policy as enrich_portrait_grammar.py.

Compound is a CROSS-CHECK, not a primary field: the index already fills
`compound_members` ~47%; this records whether PWG agrees / differs / fills a gap.

Emits src/pwg_derivation_layer.tsv (committed, grammar-FAIR) + a coverage report to
stderr. Deterministic; no LLM, no network. This sidecar is the input consumed by
src/pilot/enrich_portrait_derivation.py (which bakes it into the local portraits).

    python src/pwg_derivation_layer.py                 # default paths
    python src/pwg_derivation_layer.py --sg-root ../../SanskritGrammar-data
"""
import argparse
import csv
import os
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))                 # RussianTranslation/src
RT = os.path.dirname(HERE)                                        # RussianTranslation
DEFAULT_SG = os.path.normpath(os.path.join(RT, '..', '..', 'SanskritGrammar'))
DEFAULT_INDEX = os.path.join(HERE, 'headword_index.tsv')
DEFAULT_OUT = os.path.join(HERE, 'pwg_derivation_layer.tsv')


def read_tsv(path):
    with open(path, encoding='utf-8') as f:
        yield from csv.DictReader(f, delimiter='\t')


def load_taddhita(sg):
    """k1(slp1) -> list of {base, suffix, class, citation}."""
    p = os.path.join(sg, 'sangram', 'articles', 'taddhita-overview', 'data',
                     'pwg_taddhita_derivations.tsv')
    out = defaultdict(list)
    for r in read_tsv(p):
        out[r['headword_slp1']].append({
            'base': r['base_slp1'], 'suffix': r['suffix'],
            'class': r['suffix_class'],
            'citation': (r.get('citations', '') or '').split(';')[0].strip(),
        })
    return out


def load_panini(sg):
    """k1(slp1) -> list of sūtra strings."""
    p = os.path.join(sg, 'data', 'pwg_panini_crosswalk', 'pwg_panini_word2sutra.tsv')
    out = {}
    for r in read_tsv(p):
        out[r['headword_slp1']] = [s.strip() for s in r['sutras'].split('|') if s.strip()]
    return out


def load_compound(sg):
    """k1(slp1) -> members list (SLP1)."""
    p = os.path.join(sg, 'data', 'pwg_compound_split', 'pwg_compound_splits.tsv')
    out = {}
    for r in read_tsv(p):
        out[r['headword_slp1']] = [m.strip() for m in r['members_slp1'].split('+') if m.strip()]
    return out


def compound_status(pwg_members, index_members):
    if not pwg_members:
        return 'index-only' if index_members else ''
    if not index_members:
        return 'pwg-new-fill'
    # normalise both to a comparable member-token set
    norm = lambda xs: [x.replace('˚', '').strip() for x in xs]
    return 'agrees' if norm(pwg_members) == norm(index_members) else 'differs'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sg-root', default=DEFAULT_SG)
    ap.add_argument('--index', default=DEFAULT_INDEX)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()
    for p, lbl in ((args.sg_root, 'SanskritGrammar root'), (args.index, 'headword index')):
        if not os.path.exists(p):
            print('ERROR: %s not found: %s' % (lbl, p), file=sys.stderr)
            return 1

    taddhita = load_taddhita(args.sg_root)
    panini = load_panini(args.sg_root)
    compound = load_compound(args.sg_root)

    # how many index rows share each k1 (for homonym-ambiguity flag)
    k1_rows = Counter(r['k1'] for r in read_tsv(args.index))

    cols = ['k1', 'hom', 'homonym_ambiguous', 'deriv_base', 'deriv_suffix', 'deriv_class',
            'deriv_citation', 'panini_sutras', 'compound_members_pwg', 'compound_status']
    cov = Counter()
    comp_status_ctr = Counter()
    n = 0
    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(cols)
        for r in read_tsv(args.index):
            k1 = r['k1']
            tad = taddhita.get(k1, [])
            sut = panini.get(k1, [])
            cmp_pwg = compound.get(k1, [])
            status = compound_status(cmp_pwg, [m for m in r.get('compound_members', '').split('+') if m.strip()])
            if not (tad or sut or cmp_pwg):
                continue
            n += 1
            if tad:
                cov['derivation'] += 1
            if sut:
                cov['panini'] += 1
            if cmp_pwg:
                cov['compound'] += 1
            comp_status_ctr[status] += 1
            first = tad[0] if tad else {}
            w.writerow([
                k1, r['hom'], '1' if k1_rows[k1] > 1 else '',
                first.get('base', ''), first.get('suffix', ''), first.get('class', ''),
                first.get('citation', ''),
                '|'.join(sut),
                ' + '.join(cmp_pwg),
                status,
            ])

    print('wrote %s' % args.out, file=sys.stderr)
    print('rows with >=1 PWG layer: %d' % n, file=sys.stderr)
    print('  derivation (taddhita) : %d' % cov['derivation'], file=sys.stderr)
    print('  panini sutra          : %d' % cov['panini'], file=sys.stderr)
    print('  compound (pwg)        : %d' % cov['compound'], file=sys.stderr)
    print('compound cross-check vs index: %s' % dict(comp_status_ctr.most_common()), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
