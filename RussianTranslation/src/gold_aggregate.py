#!/usr/bin/env python
"""Aggregate the precision-judging workflow output → precision + Wilson 95% CI by
stratum and kind. Writes the committed precision report + minimal gold set.

  python gold_aggregate.py <workflow-output.json>
"""
import json, os, math, collections, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = os.path.join(HERE, 'gold_sample.jsonl')
GOLD_DIR = os.path.normpath(os.path.join(HERE, '..', 'gold'))
GOOD = {'correct', 'lemma-variant', 'proper-name'}
ERR = {'wrong-sense', 'hallucinated'}


def find_judgments(o):
    if isinstance(o, dict):
        if isinstance(o.get('judgments'), list):
            return o['judgments']
        for v in o.values():
            r = find_judgments(v)
            if r:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_judgments(v)
            if r:
                return r
    return None


def wilson(x, n):
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.96
    p = x / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p, max(0.0, c - h), min(1.0, c + h)


def main():
    wf = sys.argv[1]
    J = find_judgments(json.loads(open(wf, encoding='utf-8').read())) or []
    meta = {}
    for line in open(GOLD, encoding='utf-8'):
        r = json.loads(line)
        meta[r['id']] = r
    labof = {j['id']: j['label'] for j in J}

    def stats(filt):
        labs = collections.Counter()
        for jid, lab in labof.items():
            m = meta.get(jid)
            if m and filt(m):
                labs[lab] += 1
        n = sum(labs.values())
        good = sum(labs[l] for l in GOOD)
        err = sum(labs[l] for l in ERR)
        p, lo, hi = wilson(good, n)
        return n, good, labs['partial'], err, p, lo, hi

    os.makedirs(GOLD_DIR, exist_ok=True)
    lines = ['# Harvest precision — gold-standard measurement (2026-06-16)', '',
             'A stratified random sample of %d corpus-lexicon alignments (seed=42, balanced '
             'across period × kind), each judged against its source verse, errors adversarially '
             'verified. "Precision" = correct + lemma-variant + proper-name (accurate renderings); '
             'partial = marginal; errors = wrong-sense + hallucinated.' % len(labof), '',
             '> NOTE: this is an **LLM-judged** estimate (38-agent panel + adversarial verification '
             'of every flagged error). The frozen sample (`gold_set.jsonl`) is the scaffold for a '
             'human spot-check, which would confirm/adjust these numbers.', '',
             '## Overall', '']
    n, good, part, err, p, lo, hi = stats(lambda m: True)
    lines += ['| metric | value |', '|---|---|',
              '| sample size | %d |' % n,
              '| **precision (good)** | **%.1f%%**  (95%% CI %.1f–%.1f) |' % (100 * p, 100 * lo, 100 * hi),
              '| partial (marginal) | %.1f%% |' % (100 * part / n),
              '| errors (wrong-sense + hallucinated) | %.1f%% |' % (100 * err / n),
              '| good + partial | %.1f%% |' % (100 * (good + part) / n), '',
              '## By stratum (period)', '',
              '| stratum | n | precision | 95% CI | partial | errors |', '|---|---|---|---|---|---|']
    for per in ['Vedic', 'Epic / early-Classical', 'Classical', 'Medieval']:
        n, good, part, err, p, lo, hi = stats(lambda m: m['period'] == per)
        if n:
            lines.append('| %s | %d | %.1f%% | %.1f–%.1f | %.1f%% | %.1f%% |'
                         % (per, n, 100 * p, 100 * lo, 100 * hi, 100 * part / n, 100 * err / n))
    lines += ['', '## By kind', '', '| kind | n | precision | 95% CI | partial | errors |',
              '|---|---|---|---|---|---|']
    for kind in ['translation', 'commentary']:
        n, good, part, err, p, lo, hi = stats(lambda m: m['kind'] == kind)
        if n:
            lines.append('| %s | %d | %.1f%% | %.1f–%.1f | %.1f%% | %.1f%% |'
                         % (kind, n, 100 * p, 100 * lo, 100 * hi, 100 * part / n, 100 * err / n))
    alllabs = collections.Counter(labof.values())
    lines += ['', '## Label distribution', '',
              ' · '.join('%s: %d' % (k, alllabs[k]) for k in
                         ['correct', 'lemma-variant', 'proper-name', 'partial', 'wrong-sense', 'hallucinated'])]
    open(os.path.join(GOLD_DIR, 'precision_report.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    # minimal committed gold set (keys + labels + provenance; word-level glosses only)
    with open(os.path.join(GOLD_DIR, 'gold_set.jsonl'), 'w', encoding='utf-8', newline='') as o:
        for jid in sorted(labof):
            m = meta.get(jid, {})
            o.write(json.dumps({'id': jid, 'slp1': m.get('slp1'), 'sa': m.get('sa'),
                                'ru': m.get('ru'), 'kind': m.get('kind'),
                                'period': m.get('period'), 'work': m.get('work'),
                                'label': labof[jid]}, ensure_ascii=False) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
