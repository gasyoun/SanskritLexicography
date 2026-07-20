#!/usr/bin/env python
"""build_compound_split.py — Stage C2: recover DCS+Vidyut+marker-unresolved forms
by compound segmentation with vidyut.cheda (H1349 wave 3, D7 — reuse, don't build).

The 78,842 forms no tier resolved (`surface_unresolved.tsv`) are dominated by long
samāsa and sandhi-fused simplexes. vidyut.cheda (the offline Paninian segmenter,
v0.4.0, reused via the kosha `compare_sandhi_methods.py` method-B pattern) splits a
form into member tokens, each carrying a lemma.

**Precision gate (the load-bearing choice).** cheda on *isolated* OOV forms is
low-precision — it happily emits spurious splits (`bax`→`ba`+`x`). A spike (H1349
W3.2, n=2000) measured: "any segment is glossable" recovers 47% but at low
precision; **"≥2 tokens AND *every* member lemma is already glossable"** recovers
~35% and only accepts a compound fully decomposed into known, glossable members.
This module ships the strict gate; a recovered-but-wrong form counts as a
regression (wave-3 acceptance), so precision is bought with coverage.

Where the corpus already carries a `+`/`-` morpheme marker (handled upstream by the
rollup's marker tier), that form never reaches here — so cheda is used ONLY where no
marker exists (the plan's precedence rule).

Reads   glossary/surface_unresolved.tsv, glossary/lemma_glossary.jsonl
Writes  glossary/cheda_recovered.tsv  (form_slp1, n, n_tokens, segmentation,
                                       head_lemma, head_gloss, chain_gloss)

  python build_compound_split.py [kosha_vidyut_dir]
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.normpath(os.path.join(HERE, '..', 'glossary'))
DEFAULT_VIDYUT = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'kosha', 'data', 'vidyut'))


def load_gloss_map(path):
    """lemma_slp1 -> top Russian gloss (translations[0]); only glossable lemmas."""
    g = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            tr = r.get('translations') or []
            if tr:
                g[r['lemma_slp1']] = tr[0]['ru']
    return g


def gate(tokens, gloss_map):
    """Accept a segmentation only if it has >=2 tokens and EVERY member lemma is
    glossable. Returns the lemma list on accept, else None."""
    if len(tokens) < 2:
        return None
    lemmas = [t.lemma for t in tokens]
    if not all(l and l in gloss_map for l in lemmas):
        return None
    return lemmas


def main():
    vidyut_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VIDYUT
    from vidyut.cheda import Chedaka        # lazy: keeps the module importable for tests
    ch = Chedaka(vidyut_dir)
    gloss_map = load_gloss_map(os.path.join(G, 'lemma_glossary.jsonl'))
    print(f'[C2] {len(gloss_map)} glossable lemmas', file=sys.stderr)

    inp = os.path.join(G, 'surface_unresolved.tsv')
    outp = os.path.join(G, 'cheda_recovered.tsv')
    n = rec = rec_tokens = 0
    with open(inp, encoding='utf-8') as f, \
         open(outp, 'w', encoding='utf-8', newline='\n') as out:
        next(f)
        out.write('form_slp1\tn\tn_tokens\tsegmentation\thead_lemma\thead_gloss\tchain_gloss\n')
        for line in f:
            p = line.rstrip('\n').split('\t')
            if not p or not p[0]:
                continue
            form, freq = p[0], int(p[2]) if len(p) > 2 and p[2].isdigit() else 1
            n += 1
            try:
                tokens = ch.run(form)
            except Exception:
                tokens = []
            lemmas = gate(tokens, gloss_map)
            if not lemmas:
                continue
            head = lemmas[-1]                       # Sanskrit compound head = last member
            seg = '+'.join(lemmas)
            chain = ' + '.join(gloss_map[l] for l in lemmas)
            out.write(f'{form}\t{freq}\t{len(lemmas)}\t{seg}\t{head}\t'
                      f'{gloss_map[head]}\t{chain}\n')
            rec += 1
            rec_tokens += freq
            if n % 20000 == 0:
                print(f'  ...{n} unresolved, {rec} recovered', file=sys.stderr)
    print(f'[C2] {n} unresolved -> cheda gated-recovered {rec} forms '
          f'({100*rec/n:.1f}%), {rec_tokens} tokens -> {outp}', file=sys.stderr)


if __name__ == '__main__':
    main()
