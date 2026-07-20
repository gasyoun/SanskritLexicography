#!/usr/bin/env python
"""saru_gloss_sample.py — freeze a tier x frequency stratified sample of the
Sa->Ru gloss layer for a precision panel (H1349 wave 2, D5).

Reads the rollup's per-form resolution trace (glossary/surface_resolution.tsv,
emitted by build_rollup_glossaries.py) and draws a fixed-seed stratified sample
balanced across **tier** (dcs / vidyut / marker — which heuristic resolved the
form) x **frequency band** (hapax / low / mid / high). Each sampled item is the
unit a panel judges on two independent axes (D6):

  * lemmatization — is `lemma`/`root` a correct reduction of surface form `slp1`?
  * gloss         — is `top_ru` a correct Russian rendering of that lemma?

Because the glossary AGGREGATES over occurrences, an item is judged from the
(form, lemma, gloss) triple itself, not a single source verse (unlike the
per-alignment gold_set). Writes gold/saru_gloss_sample.jsonl (gitignored working
sample); the committed labels + report are produced by the panel + aggregator.

  python saru_gloss_sample.py [K_per_cell]   # default 10
"""
import collections
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.normpath(os.path.join(HERE, '..', 'glossary'))
RES = os.path.join(G, 'surface_resolution.tsv')
OUT = os.path.join(HERE, '..', 'gold', 'saru_gloss_sample.jsonl')
SEED = 42
TIERS = ('dcs', 'vidyut', 'marker')


def freq_band(n):
    if n <= 1:
        return 'hapax(1)'
    if n <= 9:
        return 'low(2-9)'
    if n <= 99:
        return 'mid(10-99)'
    return 'high(100+)'


def load_rows(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        next(f)  # header
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) < 8:
                continue
            slp1, sa, n, tier, lemma, upos, root, top_ru = p[:8]
            if not top_ru:
                continue  # nothing to judge on the gloss axis
            rows.append({'slp1': slp1, 'sa': sa, 'n': int(n), 'tier': tier,
                         'lemma': lemma, 'upos': upos, 'root': root, 'top_ru': top_ru})
    return rows


def stratified(rows, k_per_cell, seed=SEED):
    cells = collections.defaultdict(list)
    for r in rows:
        cells[(r['tier'], freq_band(r['n']))].append(r)
    rng = random.Random(seed)
    sample = []
    for cell in sorted(cells):
        lst = cells[cell]
        sample += rng.sample(lst, min(k_per_cell, len(lst)))
    rng.shuffle(sample)
    return sample, cells


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    rows = load_rows(RES)
    sample, cells = stratified(rows, k)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as o:
        for i, r in enumerate(sample):
            o.write(json.dumps({
                'id': i, 'slp1': r['slp1'], 'sa': r['sa'], 'n': r['n'],
                'tier': r['tier'], 'band': freq_band(r['n']),
                'lemma': r['lemma'], 'upos': r['upos'], 'root': r['root'],
                'top_ru': r['top_ru'],
            }, ensure_ascii=False) + '\n')
    comp = collections.Counter((r['tier'], freq_band(r['n'])) for r in sample)
    print(f'sample: {len(sample)} items (k={k}/cell, seed={SEED}) -> {os.path.basename(OUT)}',
          file=sys.stderr)
    for cell in sorted(comp):
        print(f'  {cell[0]:7} {cell[1]:11} {comp[cell]:3}  (of {len(cells[cell])})',
              file=sys.stderr)


if __name__ == '__main__':
    main()
