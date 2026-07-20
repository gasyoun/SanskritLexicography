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


def pick_primary_and_alts(lp):
    """Choose the primary (lemma, pos) for a form and list its competitors.

    lp: Counter mapping (lemma, pos) -> n_entries. Primary = most entries, then
    SHORTEST lemma (prefer the root over a longer derived stem) — identical to
    the original max(..., key=(cnt, -len)). Returns
    (primary_lemma, primary_pos, primary_n, alts), where
    alts = [(lemma, pos, n)] for every non-primary candidate (W1.3 ambiguity
    trail — the same competitors that only bumped a bare `ambiguous` counter
    before), or None when lp is empty."""
    if not lp:
        return None
    ranked = sorted(lp.items(), key=lambda kv: (-kv[1], len(kv[0][0])))
    (plem, ppos), pn = ranked[0]
    alts = [(lem, pos, n) for (lem, pos), n in ranked[1:]]
    return plem, ppos, pn, alts

def main():
    kpath = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KOSHA
    if not os.path.isdir(kpath):
        sys.exit(f'kosha data not found: {kpath}')
    from vidyut.kosha import Kosha       # lazy: keeps the module importable for unit tests
    k = Kosha(kpath)

    inp = os.path.join(G, 'surface_dcs_misses.tsv')
    outp = os.path.join(G, 'vidyut_form2lemma.tsv')
    ambp = os.path.join(G, 'vidyut_ambiguity.tsv')
    n = hit = 0
    stats = collections.Counter()
    with open(inp, encoding='utf-8') as f, \
         open(outp, 'w', encoding='utf-8', newline='\n') as out, \
         open(ambp, 'w', encoding='utf-8', newline='\n') as amb:
        next(f)
        out.write('form_slp1\tlemma_slp1\tpos\tn_entries\n')
        # W1.3: mirror the DCS ambiguity_homographs.tsv schema so the two tiers'
        # ambiguity trails are directly comparable.
        amb.write('form_slp1\tprimary_lemma\tprimary_pos\tprimary_n\t'
                  'alt_lemma\talt_pos\talt_n\n')
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
            picked = pick_primary_and_alts(lp)
            if picked is None:
                stats['unresolved'] += 1
                continue
            lemma, pos, cnt, alts = picked
            out.write(f'{form}\t{lemma}\t{pos}\t{cnt}\n')
            hit += 1
            stats[pos] += 1
            if alts:                       # more than one candidate lemma/pos
                stats['ambiguous'] += 1
                for alt_lem, alt_pos, alt_n in alts:
                    amb.write(f'{form}\t{lemma}\t{pos}\t{cnt}\t'
                              f'{alt_lem}\t{alt_pos}\t{alt_n}\n')
            if n % 20000 == 0:
                print(f'  ...{n} misses, {hit} recovered', file=sys.stderr)
    print(f'[C] {n} missed forms -> vidyut recovered {hit} '
          f'({100*hit/n:.1f}%); {stats["unresolved"]} still unresolved', file=sys.stderr)
    print(f'[C] pos: verb={stats["verb"]} noun={stats["noun"]} ind={stats["ind"]}; '
          f'ambiguous={stats["ambiguous"]}', file=sys.stderr)
    print(f'[C] -> {outp}', file=sys.stderr)
    print(f'[C] ambiguity trail -> {ambp}', file=sys.stderr)

if __name__ == '__main__':
    main()
