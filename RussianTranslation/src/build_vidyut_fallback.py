#!/usr/bin/env python
"""build_vidyut_fallback.py — Stage C: lemmatize DCS-missed forms with vidyut.kosha.

DCS (Stage B) resolves ~79% of tokens but only 42% of distinct forms; the long tail of
rare / sandhi-variant / compound forms misses. vidyut's kosha (Paninian FST lexicon) is the
fallback: it lemmatizes an inflected pada to its stem (Subanta) or root/dhatu (Tinanta).

Reads   ../glossary/surface_dcs_misses.tsv   (form_slp1, sa, n, top_ru)
Writes  ../glossary/vidyut_form2lemma.tsv     (form_slp1, lemma_slp1, pos, n_entries)
        pos in {verb, noun, ind}; verb lemma is already the dhatu (= its own root).

Primary lemma per form = the one carried by the most kosha entries (ties -> shortest, to
prefer the root over a longer derived stem). Forms kosha also misses stay unresolved and are
reported in the typology (Stage E).

  python build_vidyut_fallback.py [path/to/vidyut_data/kosha]
"""
import os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from vidyut.kosha import Kosha

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.normpath(os.path.join(HERE, '..', 'glossary'))
# Default: the vidyut kosha data inside the sibling kosha repo
# (GitHub/kosha/data/vidyut/kosha); override with argv[1].
DEFAULT_KOSHA = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'kosha', 'data', 'vidyut', 'kosha'))

def pos_of(entry):
    t = type(entry).__name__
    if 'Tinanta' in t:
        return 'verb'
    if getattr(entry, 'is_avyaya', False):
        return 'ind'
    return 'noun'

def main():
    kpath = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KOSHA
    if not os.path.isdir(kpath):
        sys.exit(f'kosha data not found: {kpath}')
    k = Kosha(kpath)

    inp = os.path.join(G, 'surface_dcs_misses.tsv')
    outp = os.path.join(G, 'vidyut_form2lemma.tsv')
    n = hit = 0
    stats = collections.Counter()
    with open(inp, encoding='utf-8') as f, \
         open(outp, 'w', encoding='utf-8', newline='\n') as out:
        next(f)
        out.write('form_slp1\tlemma_slp1\tpos\tn_entries\n')
        for line in f:
            p = line.rstrip('\n').split('\t')
            if not p or not p[0]:
                continue
            form = p[0]
            n += 1
            try:
                ents = k.get(form)
            except Exception:
                ents = []
            if not ents:
                stats['unresolved'] += 1
                continue
            # tally (lemma, pos) across entries
            lp = collections.Counter()
            for e in ents:
                lem = getattr(e, 'lemma', None)
                if lem:
                    lp[(lem, pos_of(e))] += 1
            if not lp:
                stats['unresolved'] += 1
                continue
            # primary: most entries, then shortest lemma
            (lemma, pos), cnt = max(lp.items(), key=lambda kv: (kv[1], -len(kv[0][0])))
            out.write(f'{form}\t{lemma}\t{pos}\t{cnt}\n')
            hit += 1
            stats[pos] += 1
            if len(lp) > 1:
                stats['ambiguous'] += 1
            if n % 20000 == 0:
                print(f'  ...{n} misses, {hit} recovered', file=sys.stderr)
    print(f'[C] {n} missed forms -> vidyut recovered {hit} '
          f'({100*hit/n:.1f}%); {stats["unresolved"]} still unresolved', file=sys.stderr)
    print(f'[C] pos: verb={stats["verb"]} noun={stats["noun"]} ind={stats["ind"]}; '
          f'ambiguous={stats["ambiguous"]}', file=sys.stderr)
    print(f'[C] -> {outp}', file=sys.stderr)

if __name__ == '__main__':
    main()
