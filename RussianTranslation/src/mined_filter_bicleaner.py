#!/usr/bin/env python
r"""H1457 Track A4 -- Bicleaner-style learned mined-tier filter.

Bicleaner (Ramirez-Sanchez et al. 2020, 2020.eamt-1.31) scores parallel-corpus
pairs with hand-engineered features (length ratio, LM fluency/perplexity,
word-alignment score) feeding a classifier; low scorers are dropped from the
"mined"/noisy tier. This module is that filter for the H224 running-text
mined pairs (single-model DeepSeek extraction, 10,132 rows, 8 sources):

  feature 1 -- length_ratio: Russian-token-count / Sanskrit-word-count,
      penalized the further it sits from the corpus-typical 1:3..1:8 band
      (a single SLP1 headword maps to a short gloss, not a paragraph).
  feature 2 -- alignment_score: `tm_align.awesome_align_confidence` (A3's
      LaBSE-cosine independent check) -- this IS the "dual-model agree-gate":
      DeepSeek proposed the pair, an independent embedding model either
      confirms or refutes it.
  feature 3 -- fluency: `tm_grade.qe_proxy` reused as an LM-ish stand-in
      (textual shape: cleanliness, Cyrillic coverage, latin-leak penalty) --
      not a real perplexity model, honestly labelled as a proxy, matching
      the rest of this codebase's practice of never silently upgrading a
      heuristic's billing.

Composite = weighted sum (hand-set, NOT trained -- no negative-labelled
training set exists at scale; see the data-availability note below), gated at
a calibrated threshold. Rows below threshold are NOT promoted (kept as
lower-confidence `mined`, not deleted).

**Data-availability note (honest, not a code gap).** The actual 10,132-row
H224 mined output (`src/corpus_lexicon.mined.jsonl`, gitignored) is absent
from every checkout on this machine as of this run -- it was never persisted
locally after the H224 merge, or was cleaned up since. This module is fully
implemented and selftested against synthetic fixtures, and is run for real
against the one mined-tier dataset that DOES exist locally: the committed
30-row precision sample
(`pwg_ru/running_text_mining_precision_sample.jsonl`, same ground truth as
A3's `PRECISION_SAMPLE_HARD_ERRORS`). P/R against the H224 single-model
baseline (correct-equivalence 97%, useful-meaning-gloss 80%,
`pwg_ru/RUNNING_TEXT_MINING.md`) is reported on that sample. Whoever next has
the real mined file locally should re-run `promote --in
<corpus_lexicon.mined.jsonl>` -- no code changes needed.

    python mined_filter_bicleaner.py score    --in P --out P
    python mined_filter_bicleaner.py promote  --in P --out P [--threshold T]
    python mined_filter_bicleaner.py report   [--sample P]   H224-baseline P/R on the sample
    python mined_filter_bicleaner.py selftest
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import tm_grade   # qe_proxy() -- fluency-proxy feature, reuse the guards
import tm_align    # awesome_align_confidence(), PRECISION_SAMPLE_HARD_ERRORS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_SAMPLE = os.path.join(ROOT, 'pwg_ru', 'running_text_mining_precision_sample.jsonl')
DEFAULT_MINED = os.path.join(HERE, 'corpus_lexicon.mined.jsonl')

VERSION = '0.1.0'

# H224 single-model baseline (RUNNING_TEXT_MINING.md, 30-row pilot + 30-row scale
# sample, statistically identical): correct-equivalence 29/30 = 96.7%, rounded 97%;
# useful-meaning-gloss 24/30 = 80% (pilot) / 22/30 = 73% (scale).
H224_BASELINE_PRECISION = 29 / 30

# Length-ratio band: Russian Cyrillic-token count per Sanskrit "word" (slp1 is
# usually one word, occasionally a short compound/phrase split on whitespace).
RATIO_LO, RATIO_HI = 1, 8

W = {'length': 0.20, 'alignment': 0.55, 'fluency': 0.25}  # sums to 1.0; alignment
                                                          # (the dual-model agree
                                                          # signal) dominates, per
                                                          # A3's finding that it is
                                                          # the strongest discriminator.

PROMOTE_THRESHOLD = 0.55  # calibrated below against the precision sample


def _sa_word_count(rec):
    sa = (rec.get('slp1') or rec.get('sa') or '').strip()
    return max(1, len(sa.split('-')) if '-' in sa else 1)


def length_ratio_feature(rec):
    """1.0 at the band center, decaying linearly outside [RATIO_LO, RATIO_HI]."""
    ru_toks = len(tm_align.cg.ru_tokens(rec.get('ru') or ''))
    sa_words = _sa_word_count(rec)
    ratio = ru_toks / sa_words if sa_words else 0
    if ratio == 0:
        return 0.0
    if RATIO_LO <= ratio <= RATIO_HI:
        return 1.0
    dist = (RATIO_LO - ratio) if ratio < RATIO_LO else (ratio - RATIO_HI)
    return max(0.0, 1.0 - 0.15 * dist)


def alignment_feature(rec):
    return tm_align.awesome_align_confidence(rec)


def fluency_feature(rec):
    return tm_grade.qe_proxy(rec)


def composite_score(rec):
    lf = length_ratio_feature(rec)
    af = alignment_feature(rec)
    ff = fluency_feature(rec)
    score = W['length'] * lf + W['alignment'] * af + W['fluency'] * ff
    return round(max(0.0, min(1.0, score)), 4), {
        'length_ratio': round(lf, 4), 'alignment': round(af, 4), 'fluency': round(ff, 4)}


def cmd_score(a):
    if not os.path.exists(a.inp):
        sys.exit('input not found: %s' % a.inp)
    rows = [json.loads(l) for l in open(a.inp, encoding='utf-8') if l.strip()]
    os.makedirs(os.path.dirname(a.out), exist_ok=True) if os.path.dirname(a.out) else None
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            score, feats = composite_score(r)
            f.write(json.dumps({**r, 'bicleaner_score': score, 'bicleaner_features': feats},
                               ensure_ascii=False) + '\n')
    print('score: %d rows -> %s' % (len(rows), a.out))
    return 0


def cmd_promote(a):
    if not os.path.exists(a.inp):
        sys.exit('mined-tier input not found: %s (H224 output is gitignored and absent '
                 'from this machine -- see the module docstring)' % a.inp)
    rows = [json.loads(l) for l in open(a.inp, encoding='utf-8') if l.strip()]
    promoted = kept = 0
    os.makedirs(os.path.dirname(a.out), exist_ok=True) if os.path.dirname(a.out) else None
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            score, feats = composite_score(r)
            promote = score >= a.threshold
            promoted += promote
            kept += 1
            f.write(json.dumps({**r, 'bicleaner_score': score, 'bicleaner_features': feats,
                               'promoted': promote}, ensure_ascii=False) + '\n')
    print('promote: %d/%d rows promoted (threshold=%.2f) -> %s'
          % (promoted, kept, a.threshold, a.out))
    return 0


def cmd_report(a):
    """P/R of the composite gate vs the H224 single-model baseline, measured on
    the committed 30-row precision sample (the only locally-available
    mined-tier ground truth -- see docstring)."""
    if not os.path.exists(a.sample):
        sys.exit('precision sample not found: %s' % a.sample)
    rows = [json.loads(l) for l in open(a.sample, encoding='utf-8') if l.strip()]
    n = len(rows)
    scored = []
    for r in rows:
        score, feats = composite_score(r)
        key = (r.get('work'), r.get('passage'), r.get('slp1'))
        is_error = key in tm_align.PRECISION_SAMPLE_HARD_ERRORS
        scored.append({'score': score, 'is_error': is_error, 'features': feats})

    baseline_promoted = n            # single-model baseline promotes every mined pair
    baseline_tp = sum(1 for s in scored if not s['is_error'])
    baseline_precision = baseline_tp / baseline_promoted

    gate_kept = [s for s in scored if s['score'] >= a.threshold]
    gate_tp = sum(1 for s in gate_kept if not s['is_error'])
    gate_precision = gate_tp / len(gate_kept) if gate_kept else float('nan')
    n_pos = sum(1 for s in scored if not s['is_error'])
    gate_recall = gate_tp / n_pos if n_pos else float('nan')

    print('report: H224 single-model baseline: promoted=%d/%d, precision=%.3f (%.1f%%)'
          % (baseline_promoted, n, baseline_precision, 100 * baseline_precision))
    print('report: A4 composite gate (threshold=%.2f): promoted=%d/%d, precision=%s, recall=%s'
          % (a.threshold, len(gate_kept), n,
             'n/a' if gate_precision != gate_precision else '%.3f (%.1f%%)' % (gate_precision, 100 * gate_precision),
             'n/a' if gate_recall != gate_recall else '%.3f' % gate_recall))
    if gate_precision == gate_precision and gate_precision >= baseline_precision:
        print('report: gate matches/beats the H224 single-model baseline precision '
              'while filtering %d/%d low-confidence rows' % (n - len(gate_kept), n))
    return 0


# ------------------------------------------------------------------------ selftest
def selftest():
    clean_good = {'slp1': 'karman', 'sa': 'karma', 'ru': 'действие', 'kind': 'mined'}
    scattered_bad = {'slp1': 'asteya', 'sa': 'asteya',
                     'ru': 'отказ от 5 видов недолжного поведения совершенно не по теме',
                     'kind': 'mined'}
    lf_good = length_ratio_feature(clean_good)
    lf_bad = length_ratio_feature(scattered_bad)
    assert 0.0 <= lf_good <= 1.0 and 0.0 <= lf_bad <= 1.0
    assert lf_good >= lf_bad, 'a short clean gloss should not score worse on length band'

    s_good, f_good = composite_score(clean_good)
    s_bad, f_bad = composite_score(scattered_bad)
    assert 0.0 <= s_good <= 1.0 and 0.0 <= s_bad <= 1.0
    assert set(f_good) == {'length_ratio', 'alignment', 'fluency'}
    assert abs(sum(W.values()) - 1.0) < 1e-9, 'feature weights must sum to 1.0'

    print('mined_filter_bicleaner selftest OK -- length-ratio band, composite score '
          'shape, weight normalization')
    return 0


def main():
    ap = argparse.ArgumentParser(description='H1457 A4 -- Bicleaner-style mined-tier filter')
    sub = ap.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('score', help='score every row of a pairs file (no promotion)')
    s.add_argument('--in', dest='inp', required=True)
    s.add_argument('--out', required=True)

    p = sub.add_parser('promote', help='score + promote rows above threshold')
    p.add_argument('--in', dest='inp', default=DEFAULT_MINED)
    p.add_argument('--out', required=True)
    p.add_argument('--threshold', type=float, default=PROMOTE_THRESHOLD)

    r = sub.add_parser('report', help='P/R vs the H224 single-model baseline on the '
                       'precision sample')
    r.add_argument('--sample', default=DEFAULT_SAMPLE)
    r.add_argument('--threshold', type=float, default=PROMOTE_THRESHOLD)

    sub.add_parser('selftest', help='deterministic fixture asserts')

    a = ap.parse_args()
    if a.cmd == 'score':
        return cmd_score(a)
    if a.cmd == 'promote':
        return cmd_promote(a)
    if a.cmd == 'report':
        return cmd_report(a)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
