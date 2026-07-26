#!/usr/bin/env python
"""bli_eval.py — streaming BLI (P@1 / MRR / coverage) harness for corpus_lexicon.jsonl.

H1521: `corpus_lexicon.jsonl` (the 1.09M-pair Sa->Ru word-alignment lexicon) has never
been quantitatively evaluated. This ranks, per gold Sanskrit lemma, the lexicon's
Russian candidates by raw alignment count (the file carries no per-pair weight -- see
the handoff's "confirm the score field" prerequisite; a one-record `head` showed there
is none), then scores:

  P@1      = fraction of COVERED gold lemmas whose #1-ranked candidate matches gold
  MRR      = mean over COVERED gold lemmas of 1/rank of the first matching candidate
             (0 if no candidate ever matches -- not excluded, per H1521 scope: a
             miss must not be silently folded into an infinite/undefined rank)
  coverage = fraction of ALL gold lemmas that appear at all in corpus_lexicon.jsonl

"Match" = Russian content-word (Cyrillic, len>=4) token overlap between a candidate
and the gold lemma's token set (drawn from an independent dictionary gloss, not from
corpus_lexicon.jsonl itself -- see build_gold_koch.py for why a same-source gold set
would be circular). This is a soft/lenient match by design: BLI gold usually pairs a
lemma with ONE canonical translation, but a dictionary gloss is a free-text definition,
so exact string equality would undercount correct-but-differently-phrased renderings.

The 290 MB corpus is streamed once; only per-gold-lemma Russian-candidate counters are
held in memory (bounded by gold-set size x candidates per lemma, not file size).

Usage:
  python bli_eval.py <gold.tsv> <corpus_lexicon.jsonl>   # real run, prints JSON
  python bli_eval.py selftest                            # fixture selftest (CI)
"""
import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

CONTENT_RE = re.compile(r'[а-яёА-ЯЁ]{4,}')


def content_tokens(text):
    return {t.lower() for t in CONTENT_RE.findall(text or '')}


def load_gold(path):
    """Returns list of {slp1, freq, ru_gold_tokens(set)}, skipping '#' header comments."""
    rows = []
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#') or line.startswith('slp1\t'):
                continue
            parts = line.split('\t')
            if len(parts) != 3:
                continue
            slp1, freq, toks = parts
            rows.append({
                'slp1': slp1,
                'freq': int(freq),
                'ru_gold_tokens': set(toks.split('|')) if toks else set(),
            })
    return rows


def rank_candidates(counter):
    """Deterministic descending rank: count desc, then Russian string asc for ties."""
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))


def collect_candidates(corpus_path, targets):
    """One streaming pass -> {slp1: Counter(ru -> count)} restricted to `targets`."""
    counts = {slp1: collections.Counter() for slp1 in targets}
    with open(corpus_path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            slp1 = d.get('slp1') or ''
            if slp1 not in counts:
                continue
            ru = (d.get('ru') or '').strip()
            if ru:
                counts[slp1][ru] += 1
    return counts


def evaluate(gold_rows, corpus_path):
    targets = {row['slp1'] for row in gold_rows}
    candidates = collect_candidates(corpus_path, targets)

    per_lemma = []
    covered = 0
    hits = 0
    rr_sum = 0.0
    for row in gold_rows:
        counter = candidates[row['slp1']]
        if not counter:
            per_lemma.append({'slp1': row['slp1'], 'covered': False, 'rank': None})
            continue
        covered += 1
        ranked = rank_candidates(counter)
        rank_found = None
        for i, (ru, _cnt) in enumerate(ranked, start=1):
            if content_tokens(ru) & row['ru_gold_tokens']:
                rank_found = i
                break
        if rank_found == 1:
            hits += 1
        if rank_found:
            rr_sum += 1.0 / rank_found
        per_lemma.append({
            'slp1': row['slp1'], 'covered': True, 'rank': rank_found,
            'top_candidate': ranked[0][0],
        })

    n_gold = len(gold_rows)
    return {
        'n_gold': n_gold,
        'covered': covered,
        'coverage': covered / n_gold if n_gold else 0.0,
        'p_at_1': hits / covered if covered else 0.0,
        'mrr': rr_sum / covered if covered else 0.0,
        'per_lemma': per_lemma,
    }


def _selftest():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    gold_path = os.path.join(here, 'fixtures', 'bli_gold.fixture.tsv')
    corpus_path = os.path.join(here, '..', 'fixtures', 'corpus_lexicon.fixture.jsonl')

    gold_rows = load_gold(gold_path)
    assert len(gold_rows) == 4, f'expected 4 fixture gold rows, got {len(gold_rows)}'

    result = evaluate(gold_rows, corpus_path)
    assert result['n_gold'] == 4
    assert result['covered'] == 3, result  # 'agni' is absent from the fixture corpus
    assert abs(result['coverage'] - 0.75) < 1e-9, result
    # karman->action and aDikAra->right both rank-1 hit; yoga's gold token
    # deliberately doesn't overlap the fixture's rendering -> miss.
    assert abs(result['p_at_1'] - (2 / 3)) < 1e-9, result
    assert abs(result['mrr'] - (2 / 3)) < 1e-9, result

    by_slp1 = {r['slp1']: r for r in result['per_lemma']}
    assert by_slp1['karman']['rank'] == 1
    assert by_slp1['aDikAra']['rank'] == 1
    assert by_slp1['yoga']['rank'] is None
    assert by_slp1['agni']['covered'] is False

    print('bli_eval selftest OK:', json.dumps(
        {k: v for k, v in result.items() if k != 'per_lemma'}, ensure_ascii=False))


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'selftest':
        _selftest()
        return
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    gold_path, corpus_path = sys.argv[1], sys.argv[2]
    gold_rows = load_gold(gold_path)
    result = evaluate(gold_rows, corpus_path)
    print(json.dumps({k: v for k, v in result.items() if k != 'per_lemma'},
                      ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
