#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the PWG derivation layer for pwg_ru — join the SanskritGrammar PWG data layers
onto the pwg_ru headword index, HOMONYM-PRECISE via the PWG L_id↔(k1,hom) map.

Consumes (canonical, read-only; the sibling SanskritGrammar repo — like the pipeline
already reads csl-orig / WhitneyRoots):
  - L_id↔hom map        : data/pwg_lid_hom_map/pwg_lid_hom_map.tsv   (L_id → k1, hom)
  - taddhita derivations : sangram/articles/taddhita-overview/data/pwg_taddhita_derivations.tsv
  - Pāṇini crosswalk     : data/pwg_panini_crosswalk/pwg_panini_word2sutra.tsv
  - compound splits      : data/pwg_compound_split/pwg_compound_splits.tsv
  - gaṇa membership      : data/pwg_gana_membership/pwg_gana_membership.tsv (external Gaṇapāṭha × crosswalk)

Homonym alignment (upgraded from the k1-only attach-all-and-flag first version):
  - **derivation** and **compound** carry a per-occurrence PWG `L_id`, so each is pinned to
    the EXACT `(k1, hom)` its L_id maps to. `homonym_precise=1` marks such rows.
  - **Pāṇini** `word2sutra` is headword-AGGREGATED (sūtras merged across a word's homonyms
    into one row), so it stays k1-level — attached to every homonym of the k1, which is the
    correct scope for aggregated data. `homonym_precise` does not apply to it.
  A layer occurrence whose L_id is absent from the map falls back to k1-level (rare; the map
  resolves 100 % of the index's (k1,hom) pairs).

Compound is a CROSS-CHECK, not a primary field: the index already fills `compound_members`
~47%; this records whether PWG agrees / differs / fills a gap.

Emits src/pwg_derivation_layer.tsv (committed, grammar-FAIR) + a coverage report. The
sidecar is consumed by src/pilot/enrich_portrait_derivation.py. Deterministic.

    python src/pwg_derivation_layer.py
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


def load_lid_hom(sg):
    """L_id -> (k1, hom)."""
    p = os.path.join(sg, 'data', 'pwg_lid_hom_map', 'pwg_lid_hom_map.tsv')
    out = {}
    for r in read_tsv(p):
        out[r['L_id']] = (r['k1'], r['hom'])
    return out


def load_taddhita(sg, lid_hom):
    """(k1, hom) -> {base, suffix, class, citation}; k1 -> same (k1-level fallback)."""
    p = os.path.join(sg, 'sangram', 'articles', 'taddhita-overview', 'data',
                     'pwg_taddhita_derivations.tsv')
    precise, byk1 = {}, {}
    for r in read_tsv(p):
        rec = {'base': r['base_slp1'], 'suffix': r['suffix'], 'class': r['suffix_class'],
               'citation': (r.get('citations', '') or '').split(';')[0].strip()}
        kh = lid_hom.get(r.get('L_id', ''))
        if kh:
            precise.setdefault(kh, rec)
        byk1.setdefault(r['headword_slp1'], rec)
    return precise, byk1


def load_compound(sg, lid_hom):
    """(k1, hom) -> members; k1 -> members (fallback)."""
    p = os.path.join(sg, 'data', 'pwg_compound_split', 'pwg_compound_splits.tsv')
    precise, byk1 = {}, {}
    for r in read_tsv(p):
        members = [m.strip() for m in r['members_slp1'].split('+') if m.strip()]
        kh = lid_hom.get(r.get('L_id', ''))
        if kh:
            precise.setdefault(kh, members)
        byk1.setdefault(r['headword_slp1'], members)
    return precise, byk1


def load_panini(sg):
    """k1 -> sūtra list (headword-aggregated → k1-level by design)."""
    p = os.path.join(sg, 'data', 'pwg_panini_crosswalk', 'pwg_panini_word2sutra.tsv')
    out = {}
    for r in read_tsv(p):
        out[r['headword_slp1']] = [s.strip() for s in r['sutras'].split('|') if s.strip()]
    return out


def load_gana(sg):
    """k1 -> {ganas, gana_sutras, corroborated} from the external Gaṇapāṭha join.
    Only PWG-attested members; k1-level (gaṇa membership is lexical, not per-homonym)."""
    p = os.path.join(sg, 'data', 'pwg_gana_membership', 'pwg_gana_membership.tsv')
    out = {}
    for r in read_tsv(p):
        if r.get('attested_in_pwg') != '1':
            continue
        out[r['member_slp1']] = {'ganas': r['ganas'], 'gana_sutras': r['gana_sutras'],
                                 'corroborated': r.get('corroborated', '')}
    return out


def compound_status(pwg_members, index_members):
    if not pwg_members:
        return 'index-only' if index_members else ''
    if not index_members:
        return 'pwg-new-fill'
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

    lid_hom = load_lid_hom(args.sg_root)
    tad_precise, tad_k1 = load_taddhita(args.sg_root, lid_hom)
    cmp_precise, cmp_k1 = load_compound(args.sg_root, lid_hom)
    panini = load_panini(args.sg_root)
    gana = load_gana(args.sg_root)

    cols = ['k1', 'hom', 'homonym_precise', 'deriv_base', 'deriv_suffix', 'deriv_class',
            'deriv_citation', 'panini_sutras', 'compound_members_pwg', 'compound_status',
            'ganas', 'gana_sutras', 'gana_corroborated']
    cov = Counter()
    comp_status_ctr = Counter()
    n = precise_rows = 0
    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(cols)
        for r in read_tsv(args.index):
            k1, hom = r['k1'], r['hom']
            kh = (k1, hom)
            # derivation + compound: exact homonym via map, else k1-level fallback
            tad = tad_precise.get(kh)
            cmp_pwg = cmp_precise.get(kh)
            pinned = tad is not None or cmp_pwg is not None
            if tad is None:
                tad = tad_k1.get(k1)
            if cmp_pwg is None:
                cmp_pwg = cmp_k1.get(k1)
            sut = panini.get(k1, [])                     # k1-level (aggregated)
            gan = gana.get(k1)                            # k1-level (lexical membership)
            if not (tad or sut or cmp_pwg or gan):
                continue
            status = compound_status(cmp_pwg or [],
                                     [m for m in r.get('compound_members', '').split('+') if m.strip()])
            n += 1
            if pinned:
                precise_rows += 1
            if tad:
                cov['derivation'] += 1
            if sut:
                cov['panini'] += 1
            if cmp_pwg:
                cov['compound'] += 1
            if gan:
                cov['gana'] += 1
            comp_status_ctr[status] += 1
            tad = tad or {}
            gan = gan or {}
            w.writerow([
                k1, hom, '1' if pinned else '',
                tad.get('base', ''), tad.get('suffix', ''), tad.get('class', ''),
                tad.get('citation', ''),
                '|'.join(sut),
                ' + '.join(cmp_pwg or []),
                status,
                gan.get('ganas', ''), gan.get('gana_sutras', ''), gan.get('corroborated', ''),
            ])

    print('wrote %s' % args.out, file=sys.stderr)
    print('rows with >=1 PWG layer: %d (homonym-pinned via map: %d)' % (n, precise_rows), file=sys.stderr)
    print('  derivation (taddhita) : %d' % cov['derivation'], file=sys.stderr)
    print('  panini sutra (k1-level): %d' % cov['panini'], file=sys.stderr)
    print('  compound (pwg)        : %d' % cov['compound'], file=sys.stderr)
    print('  gaṇa membership       : %d' % cov['gana'], file=sys.stderr)
    print('compound cross-check vs index: %s' % dict(comp_status_ctr.most_common()), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
