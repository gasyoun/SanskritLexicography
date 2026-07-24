#!/usr/bin/env python
r"""H1457 Track A6 -- retrieval measurement (does the graded TM, retrieved as
fuzzy context, improve translation quality/speed vs no-TM?).

Neural Fuzzy Repair framing (Bulte & Tezcan 2019, P19-1175): translate a fixed
card batch twice -- (a) no-TM, (b) with the best-matching graded TM segment(s)
retrieved as in-context fuzzy match -- and report the quality delta (judge
severity) and wall-clock/token delta. MEASUREMENT ONLY: this never wires
retrieval into the production decode loop (that is the plan's explicit W2
non-goal).

Both `translate_fn` (the engine under test) and `judge_fn` (the quality
scorer) are pluggable so this harness is independently testable (selftest
uses deterministic mock functions) and immediately usable the moment a real
engine is wired in -- no code changes needed, only supplying the two
callables.

**Data-availability note (honest, not a code gap).** Both the no-TM and
with-TM arms need a LIVE translation-engine call (DeepSeek or an Anthropic
model). Per `research/nn_api_smoketest.md` (S1) and `GRADE_CALIBRATION.md`
(A2), this environment has no `DEEPSEEK_API_KEY` (no repo-local `.env`) and no
Anthropic API key. So the live measurement is BLOCKED here exactly like A2 --
the harness is fully built, selftested against mock engines, and ready to run
the real batch the moment either key is available; no fabricated quality
numbers are reported.

    python tm_retrieval_eval.py batch   [--grade-gold P] [--n N] [--out P]   fixed eval batch -> jsonl
    python tm_retrieval_eval.py run     --batch P [--engine none] [--out P]  the real measurement
    python tm_retrieval_eval.py selftest
"""
import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_GRADE_GOLD = os.path.join(ROOT, 'gold', 'grade_gold.jsonl')
DEFAULT_BATCH = os.path.join(HERE, 'RETRIEVAL_EVAL_BATCH.jsonl')
DEFAULT_OUT = os.path.join(HERE, 'RETRIEVAL_EVAL.md')

VERSION = '0.1.0'


def cmd_batch(a):
    """A fixed, reproducible eval batch: the first N grade-A rows of the frozen
    gold (highest-confidence references, so a quality delta isn't confounded
    by disputed segments), sorted deterministically by id."""
    if not os.path.exists(a.grade_gold):
        sys.exit('frozen gold not found: %s (run build_grade_gold.py build first)'
                 % a.grade_gold)
    rows = [json.loads(l) for l in open(a.grade_gold, encoding='utf-8') if l.strip()]
    a_rows = sorted((r for r in rows if r.get('grade') == 'A'), key=lambda r: r.get('id', 0))
    batch = a_rows[:a.n]
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        for r in batch:
            f.write(json.dumps({'slp1': r.get('slp1'), 'sa': r.get('sa'),
                               'ru_reference': r.get('ru'), 'kind': r.get('kind'),
                               'period': r.get('period')}, ensure_ascii=False) + '\n')
    print('batch: %d grade-A rows -> %s' % (len(batch), a.out))
    return 0


def fuzzy_context(card, tm_index, k=1):
    """Retrieve the k best-matching graded TM segments for `card` by exact
    slp1 match first, else empty (this is a MEASUREMENT harness, not a
    retrieval-quality contribution -- A5's LaBSE aligner is the real
    candidate-scoring method; here any reasonable retrieval suffices since
    the thing being measured is the DOWNSTREAM translation delta, not the
    retriever itself)."""
    hit = tm_index.get(card.get('slp1'))
    return [hit] if hit else []


def run_arm(cards, translate_fn, judge_fn, tm_index=None):
    """Translate every card with `translate_fn` (optionally handed fuzzy
    context from tm_index), score with `judge_fn`, and return per-card + total
    wall-clock/token/quality stats."""
    rows = []
    t0 = time.perf_counter()
    total_tokens = 0
    for card in cards:
        context = fuzzy_context(card, tm_index) if tm_index is not None else []
        t1 = time.perf_counter()
        out = translate_fn(card, context)
        dt = time.perf_counter() - t1
        quality = judge_fn(card, out)
        total_tokens += out.get('tokens', 0)
        rows.append({'slp1': card.get('slp1'), 'output': out.get('text'),
                    'wall_clock_s': round(dt, 4), 'tokens': out.get('tokens', 0),
                    'quality': quality})
    return {'rows': rows, 'total_wall_clock_s': round(time.perf_counter() - t0, 4),
           'total_tokens': total_tokens,
           'mean_quality': (sum(r['quality'] for r in rows) / len(rows)) if rows else float('nan')}


def cmd_run(a):
    if not os.path.exists(a.batch):
        sys.exit('eval batch not found: %s (run `batch` first)' % a.batch)
    cards = [json.loads(l) for l in open(a.batch, encoding='utf-8') if l.strip()]

    if a.engine == 'none':
        md = _render_blocked_md(len(cards))
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(md)
        print('run: --engine none -> no live translation call made; see %s for the '
              'documented block (no DEEPSEEK_API_KEY/.env or Anthropic key in this env)'
              % a.out)
        return 0

    sys.exit('run: --engine %s not implemented in this environment (only "none" is '
             'available -- see the module docstring)' % a.engine)


def _render_blocked_md(n_cards):
    lines = []
    lines.append('# RETRIEVAL_EVAL — H1457 A6 retrieval measurement')
    lines.append('')
    lines.append('_Created: 22-07-2026 · Last updated: 22-07-2026_')
    lines.append('')
    lines.append('Harness: `tm_retrieval_eval.py` (Sonnet 5, `claude-sonnet-5`), H1457 Track A6. '
                 'Fixed eval batch: %d grade-A rows from `gold/grade_gold.jsonl` '
                 '(`RETRIEVAL_EVAL_BATCH.jsonl`).' % n_cards)
    lines.append('')
    lines.append('## Status: BLOCKED — no live translation engine available in this environment')
    lines.append('')
    lines.append('A6 needs a LIVE translation-engine call for both arms (no-TM baseline vs '
                 'graded-TMX-as-fuzzy-context). Per '
                 '[`research/nn_api_smoketest.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/nn_api_smoketest.md) '
                 '(spike S1) and '
                 '[`src/GRADE_CALIBRATION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/GRADE_CALIBRATION.md) '
                 '(A2), this environment has no `DEEPSEEK_API_KEY` (`build_corpus_lexicon.py` '
                 'expects one in a repo-local `.env`; none exists in this worktree or the main '
                 'checkout) and no Anthropic API key. No fabricated quality/wall-clock numbers '
                 'are reported here — that would misrepresent a measurement that never ran.')
    lines.append('')
    lines.append('## What IS built and tested')
    lines.append('')
    lines.append('- `cmd_batch`: reproducible eval-batch construction from the frozen gold '
                 '(deterministic, id-sorted, grade-A only).')
    lines.append('- `run_arm` / `fuzzy_context`: the measurement loop (wall-clock per card, '
                 'token accounting, mean quality), engine-agnostic via a pluggable '
                 '`translate_fn`/`judge_fn` pair.')
    lines.append('- `selftest` exercises the full loop with deterministic MOCK engines '
                 '(a fixed-latency mock translator + a mock judge that scores context-aided '
                 'output higher), proving the harness correctly computes the deltas it is '
                 'designed to report.')
    lines.append('')
    lines.append('## To activate')
    lines.append('')
    lines.append('Supply a real `translate_fn(card, context) -> {text, tokens}` and '
                 '`judge_fn(card, output) -> float` (e.g. wrapping the existing '
                 '`build_corpus_lexicon.py` DeepSeek client once a key is configured, or an '
                 'Anthropic client), then '
                 '`run_arm(cards, translate_fn, judge_fn)` for the no-TM arm and '
                 '`run_arm(cards, translate_fn, judge_fn, tm_index)` for the with-TM arm — '
                 'no other code changes needed.')
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    return '\n'.join(lines)


# ------------------------------------------------------------------------ selftest
def _mock_translate_no_context(card, context):
    time.sleep(0.001)
    return {'text': card.get('slp1', '') + '_baseline', 'tokens': 10}


def _mock_translate_with_context(card, context):
    time.sleep(0.001)
    suffix = '_ctx' if context else '_baseline'
    return {'text': card.get('slp1', '') + suffix, 'tokens': 12 if context else 10}


def _mock_judge(card, out):
    return 0.9 if out['text'].endswith('_ctx') else 0.6


def selftest():
    cards = [{'slp1': 'karman', 'ru_reference': 'действие'},
             {'slp1': 'yoga', 'ru_reference': 'йога'}]
    tm_index = {'karman': 'действие (TM match)'}  # only one card has a fuzzy hit

    no_tm = run_arm(cards, _mock_translate_no_context, _mock_judge)
    with_tm = run_arm(cards, _mock_translate_with_context, _mock_judge, tm_index=tm_index)

    assert no_tm['mean_quality'] < with_tm['mean_quality'], \
        'the mock context-aided arm must score higher, got %s vs %s' % (no_tm, with_tm)
    assert with_tm['total_tokens'] >= no_tm['total_tokens'], \
        'context arm should not use fewer tokens than baseline in this mock'
    assert all('wall_clock_s' in r for r in no_tm['rows'])
    assert len(fuzzy_context({'slp1': 'karman'}, tm_index)) == 1
    assert len(fuzzy_context({'slp1': 'nonexistent'}, tm_index)) == 0

    print('tm_retrieval_eval selftest OK -- run_arm computes quality/token deltas, '
          'fuzzy_context retrieves only known keys')
    return 0


def main():
    ap = argparse.ArgumentParser(description='H1457 A6 -- retrieval measurement (TM as fuzzy context)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('batch', help='build the fixed eval batch from frozen gold')
    b.add_argument('--grade-gold', dest='grade_gold', default=DEFAULT_GRADE_GOLD)
    b.add_argument('--n', type=int, default=20)
    b.add_argument('--out', default=DEFAULT_BATCH)

    r = sub.add_parser('run', help='run the no-TM vs with-TM measurement')
    r.add_argument('--batch', default=DEFAULT_BATCH)
    r.add_argument('--engine', choices=['none'], default='none',
                   help='"none" documents the block; no other engine is available in '
                        'this environment (see module docstring)')
    r.add_argument('--out', default=DEFAULT_OUT)

    sub.add_parser('selftest', help='deterministic mock-engine asserts')

    a = ap.parse_args()
    if a.cmd == 'batch':
        return cmd_batch(a)
    if a.cmd == 'run':
        return cmd_run(a)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
