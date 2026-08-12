#!/usr/bin/env python
"""bli_score_stratified.py -- per-stratum P@1 / P@5 / MRR scorer for the H2401
BLI gold frame (docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md), against
corpus_lexicon.jsonl. H2402.

Reuses bli_eval.py's candidate ranking and content-token matching (H1521) --
this script differs only in what it does with the result, per §6 of the
protocol:

  1. Report per (band x pos) cell, not one number. A single frame-wide P@1 is
     FRAME-WEIGHTED (25 equal cells), never corpus-weighted -- see the
     protocol's §7 pool sizes for re-weighting.
  2. A lemma absent from corpus_lexicon.jsonl has no rank. It counts against
     that cell's coverage and is EXCLUDED from P@1/P@5/MRR -- never folded in
     as rank-infinity. Per-stratum presence in the shipped frame runs from
     1.00 (band 5, several POS) down to 0.00 (band 1 VERB), so mixing the two
     would make thin bands look like retrieval failures when they are
     absence.

Gold input is the H2401 frame (slp1, band, pos, koch_gloss, ...) with a
`gold_ru` column appended by the annotation pass (pipe-separated acceptable
Russian translations; the literal token SKIP marks an unannotatable row,
excluded from every metric -- protocol §5). The 500-row frame as shipped by
H2401 carries no gold column yet (annotation is pass-1/pass-2 work, not this
script's); this scorer is exercised against a fixture until that lands.

P@5 (new here; bli_eval.py only reports P@1): a covered gold lemma counts as
a P@5 hit iff the first content-token-matching candidate ranks <= 5.

  python bli_score_stratified.py <gold.tsv> <corpus_lexicon.jsonl> [--min-reportable N]
  python bli_score_stratified.py selftest
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bli_eval  # noqa: E402  (content_tokens / rank_candidates / collect_candidates)

DEFAULT_MIN_REPORTABLE = 5
SKIP = 'SKIP'


def load_stratified_gold(path):
    """Returns (rows, n_skipped). Each row: {slp1, band, pos, ru_gold_tokens}.
    Skipped (gold_ru == SKIP) rows are excluded from `rows` and counted."""
    rows = []
    n_skipped = 0
    with open(path, encoding='utf-8-sig') as f:
        header = None
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if header is None:
                header = parts
                continue
            rec = dict(zip(header, parts))
            gold_ru = (rec.get('gold_ru') or '').strip()
            if gold_ru == SKIP:
                n_skipped += 1
                continue
            tokens = set()
            for variant in gold_ru.split('|'):
                tokens |= bli_eval.content_tokens(variant)
            rows.append({
                'slp1': rec['slp1'],
                'band': rec['band'],
                'pos': rec['pos'],
                'ru_gold_tokens': tokens,
            })
    return rows, n_skipped


def _score_rows(rows, candidates_by_slp1):
    """Shared scoring core for one cell or the whole frame."""
    n_gold = len(rows)
    covered = 0
    hits1 = 0
    hits5 = 0
    rr_sum = 0.0
    per_lemma = []
    for row in rows:
        counter = candidates_by_slp1.get(row['slp1'])
        if not counter:
            per_lemma.append({'slp1': row['slp1'], 'covered': False, 'rank': None})
            continue
        covered += 1
        ranked = bli_eval.rank_candidates(counter)
        rank_found = None
        for i, (ru, _cnt) in enumerate(ranked, start=1):
            if bli_eval.content_tokens(ru) & row['ru_gold_tokens']:
                rank_found = i
                break
        if rank_found == 1:
            hits1 += 1
        if rank_found is not None and rank_found <= 5:
            hits5 += 1
        if rank_found:
            rr_sum += 1.0 / rank_found
        per_lemma.append({'slp1': row['slp1'], 'covered': True, 'rank': rank_found})
    return {
        'n_gold': n_gold,
        'covered': covered,
        'coverage': covered / n_gold if n_gold else 0.0,
        'p_at_1': hits1 / covered if covered else 0.0,
        'p_at_5': hits5 / covered if covered else 0.0,
        'mrr': rr_sum / covered if covered else 0.0,
        'per_lemma': per_lemma,
    }


def evaluate_stratified(gold_rows, n_skipped, corpus_path, min_reportable):
    targets = {row['slp1'] for row in gold_rows}
    candidates = bli_eval.collect_candidates(corpus_path, targets)

    cells = {}
    for row in gold_rows:
        cells.setdefault((row['band'], row['pos']), []).append(row)

    cell_results = {}
    for (band, pos), rows in sorted(cells.items()):
        result = _score_rows(rows, candidates)
        result['reportable'] = result['covered'] >= min_reportable
        del result['per_lemma']
        cell_results['%s|%s' % (band, pos)] = result

    overall = _score_rows(gold_rows, candidates)
    del overall['per_lemma']
    overall['weighting'] = 'frame_weighted_not_corpus_weighted'

    return {
        'n_skipped': n_skipped,
        'min_reportable': min_reportable,
        'overall': overall,
        'cells': cell_results,
    }


def _selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    gold_path = os.path.join(here, 'fixtures', 'bli_gold_stratified.fixture.tsv')
    corpus_path = os.path.join(here, '..', 'fixtures', 'corpus_lexicon_stratified.fixture.jsonl')

    gold_rows, n_skipped = load_stratified_gold(gold_path)
    assert n_skipped == 1, n_skipped  # 'iti' is SKIP
    assert len(gold_rows) == 5, len(gold_rows)  # karman, aDikAra, uru, gam, kzip

    result = evaluate_stratified(gold_rows, n_skipped, corpus_path, DEFAULT_MIN_REPORTABLE)
    assert result['n_skipped'] == 1
    assert set(result['cells']) == {'5|NOUN', '5|VERB'}, result['cells']

    noun = result['cells']['5|NOUN']
    assert noun['n_gold'] == 3, noun  # karman, aDikAra, uru
    assert noun['covered'] == 2, noun  # uru absent
    assert abs(noun['coverage'] - (2 / 3)) < 1e-9, noun
    # karman -> rank 1 (hit both P@1/P@5); aDikAra -> rank 3 (P@5 hit, P@1 miss)
    assert abs(noun['p_at_1'] - 0.5) < 1e-9, noun
    assert abs(noun['p_at_5'] - 1.0) < 1e-9, noun
    assert abs(noun['mrr'] - ((1.0 + 1 / 3) / 2)) < 1e-9, noun

    verb = result['cells']['5|VERB']
    assert verb['n_gold'] == 2, verb  # gam, kzip
    assert verb['covered'] == 1, verb  # kzip absent
    assert abs(verb['coverage'] - 0.5) < 1e-9, verb
    assert abs(verb['p_at_1'] - 1.0) < 1e-9, verb
    assert abs(verb['p_at_5'] - 1.0) < 1e-9, verb
    assert abs(verb['mrr'] - 1.0) < 1e-9, verb

    overall = result['overall']
    assert overall['n_gold'] == 5, overall
    assert overall['covered'] == 3, overall
    assert overall['weighting'] == 'frame_weighted_not_corpus_weighted'

    # min_reportable gate: 2 rows covered per cell here, so a threshold of 5
    # (the default) marks both cells not-yet-reportable -- this is the
    # protocol's "coverage evidence but no usable P@1" case (§6), not a bug.
    assert noun['reportable'] is False, noun
    assert verb['reportable'] is False, verb
    result_low_bar = evaluate_stratified(gold_rows, n_skipped, corpus_path, min_reportable=2)
    assert result_low_bar['cells']['5|NOUN']['reportable'] is True

    print('bli_score_stratified selftest OK:', json.dumps(
        {'n_skipped': result['n_skipped'], 'cells': result['cells'],
         'overall': result['overall']}, ensure_ascii=False))


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'selftest':
        _selftest()
        return

    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('gold_tsv')
    ap.add_argument('corpus_jsonl')
    ap.add_argument('--min-reportable', type=int, default=DEFAULT_MIN_REPORTABLE,
                     help='minimum covered lemmas for a cell rate to be marked reportable '
                          '(default %(default)s)')
    args = ap.parse_args()

    gold_rows, n_skipped = load_stratified_gold(args.gold_tsv)
    result = evaluate_stratified(gold_rows, n_skipped, args.corpus_jsonl, args.min_reportable)
    for cell in result['cells'].values():
        cell.pop('per_lemma', None)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
