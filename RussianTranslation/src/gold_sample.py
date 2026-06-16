#!/usr/bin/env python
"""Freeze a stratified random sample of the corpus lexicon for precision review.

Draws N alignments balanced across period × kind (fixed seed → reproducible),
attaches each row's SOURCE verse + the segment it was aligned from, and writes a
gitignored working sample for judging (gold_sample.jsonl). The committed,
minimal gold set (keys + labels, no bulk text) is produced after judging.

  python gold_sample.py [N]
"""
import json, os, random, collections, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import corpus_harvest as ch

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
LEX = os.path.join(HERE, 'corpus_lexicon.jsonl')
OUT = os.path.join(HERE, 'gold_sample.jsonl')
SEED = 42

_src = {}
def load_src(work):
    if work in _src:
        return _src[work]
    d = collections.defaultdict(dict)
    f = os.path.join(SM, work + '.jsonl')
    if os.path.exists(f):
        for line in open(f, encoding='utf-8'):
            try:
                e = json.loads(line)
            except Exception:
                continue
            g = e.get('group'); seg = e.get('seg', '')
            if seg == 'sa':
                d[g]['sa'] = e.get('text')
            elif seg == 'ru':
                d[g]['ru'] = e.get('text')
            elif seg.startswith('comm'):
                d[g].setdefault('comm', []).append(e.get('text'))
    _src[work] = d
    return d


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    cells = collections.defaultdict(list)
    for line in open(LEX, encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            continue
        cells[(ch.norm_period(r.get('period')), r.get('kind'))].append(r)
    random.seed(SEED)
    per = max(1, n // len(cells))
    sample = []
    for cell, lst in sorted(cells.items()):
        sample += random.sample(lst, min(per, len(lst)))
    random.shuffle(sample)
    with open(OUT, 'w', encoding='utf-8', newline='') as o:
        for i, r in enumerate(sample):
            s = load_src(r['work']).get(r['group'], {})
            o.write(json.dumps({
                'id': i, 'slp1': r['slp1'], 'sa': r['sa'], 'ru': r['ru'],
                'kind': r['kind'], 'work': r['work'], 'group': r['group'],
                'period': ch.norm_period(r.get('period')), 'genre': r.get('genre'),
                'src_sa': s.get('sa'), 'src_ru': s.get('ru'),
                'src_comm': (s.get('comm') or [])[:2],
            }, ensure_ascii=False) + '\n')
    comp = collections.Counter((ch.norm_period(r.get('period')), r['kind']) for r in sample)
    print('sample: %d rows → %s' % (len(sample), os.path.basename(OUT)))
    for cell, c in sorted(comp.items()):
        print('  %-30s %s : %d' % (cell[0], cell[1], c))


if __name__ == '__main__':
    main()
