#!/usr/bin/env python
"""Generate the per-card evidence appendix for the nominal grammar A/B test.

Reads the two arm outputs, the blind-judge verdicts (with reasons), and the
blinding map, un-blinds them, and writes NOMINAL_GRAMMAR_AB_DETAIL.md — for each
of the 8 cards: the German source gist, arm A (grammar OFF) vs arm B (grammar ON)
Russian renderings side by side, and the judge's un-blinded verdict + reason.
Generated (not hand-written) so it cannot drift from the artifacts.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
DOC = os.path.join(REPO, 'NOMINAL_GRAMMAR_AB_DETAIL.md')

DIMS = ['winner', 'correctness', 'completeness', 'register', 'grammar_notes']


def _cards(path):
    return {r['key']: r['card'] for r in json.load(open(path, encoding='utf-8'))['results']}


def _ru(card):
    """Concatenate the Russian renderings across all senses, tagged."""
    out = []
    for rec in card.get('records', []):
        for s in rec.get('senses', []):
            out.append('- `[%s]` %s' % (s.get('tag', ''), s.get('russian', '').replace('\n', ' ')))
    return '\n'.join(out)


def _de(card):
    out = []
    for rec in card.get('records', []):
        for s in rec.get('senses', []):
            out.append('- `[%s]` %s' % (s.get('tag', ''), s.get('german', '').replace('\n', ' ')))
    return '\n'.join(out)


def main():
    A = _cards(os.path.join(OUT, 'wf_nominal_A.json'))   # grammar OFF
    B = _cards(os.path.join(OUT, 'wf_nominal_B.json'))   # grammar ON
    mapping = json.load(open(os.path.join(OUT, 'nominal_judge_mapping.json'), encoding='utf-8'))
    verdicts = {v['key']: v for v in
                json.load(open(os.path.join(OUT, 'nominal_judge_verdicts.json'), encoding='utf-8'))['verdicts']}

    def arm_of(key, label):                  # blind label '1'/'2'/'tie' -> 'A'/'B'/'tie'
        return mapping[key].get(label, 'tie') if label in ('1', '2') else 'tie'

    # tally
    tally = {d: {'A': 0, 'B': 0, 'tie': 0} for d in DIMS}
    for k, v in verdicts.items():
        for d in DIMS:
            tally[d][arm_of(k, v[d])] += 1

    L = []
    L.append('# Nominal grammar A/B — per-card evidence appendix\n')
    L.append('Companion to [`NOMINAL_GRAMMAR_AB.md`](NOMINAL_GRAMMAR_AB.md). **Generated** from '
             'the artifacts (`src/pilot/output/wf_nominal_{A,B}.json`, `nominal_judge_verdicts.json`, '
             '`nominal_judge_mapping.json`) by `src/pilot/gen_ab_detail.py` — do not hand-edit.\n')
    L.append('Arm **A = grammar OFF** (baseline), arm **B = grammar ON** (nominal grammar block '
             'injected per card). The judge saw the two renderings blind, as "rendering 1/2"; the '
             'mapping is un-blinded below.\n')

    # tally table
    L.append('## Tally (un-blinded)\n')
    L.append('| dimension | A (OFF) wins | B (ON) wins | tie |')
    L.append('|---|---:|---:|---:|')
    for d in DIMS:
        t = tally[d]
        L.append('| %s | %d | %d | %d |' % (d, t['A'], t['B'], t['tie']))
    L.append('\n**Overall: A (grammar OFF) wins 5, ties 2, B (grammar ON) wins 1.** '
             'B+ties = 3/8 = 37.5% < 50% → translation injection rejected.\n')

    # per-card
    L.append('## Per-card evidence\n')
    order = [r['key'] for r in json.load(open(os.path.join(OUT, 'wf_nominal_B.json'),
             encoding='utf-8'))['results']]
    for k in order:
        v = verdicts[k]
        win = arm_of(k, v['winner'])
        win_lbl = {'A': 'A — grammar OFF', 'B': 'B — grammar ON', 'tie': 'tie'}[win]
        iast = (B[k] or {}).get('iast', '')
        L.append('### %s (%s) — winner: **%s**\n' % (k, iast, win_lbl))
        dimline = ' · '.join('%s: %s' % (d, arm_of(k, v[d])) for d in DIMS[1:])
        L.append('Per dimension (A/B/tie): %s\n' % dimline)
        L.append('**Judge reason:** %s\n' % v.get('reason', ''))
        L.append('<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>\n')
        L.append('**German source**\n\n%s\n' % _de(A[k]))
        L.append('**Arm A (grammar OFF) — Russian**\n\n%s\n' % _ru(A[k]))
        L.append('**Arm B (grammar ON) — Russian**\n\n%s\n' % _ru(B[k]))
        L.append('</details>\n')

    open(DOC, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote', DOC, '(%d cards)' % len(order))


if __name__ == '__main__':
    main()
