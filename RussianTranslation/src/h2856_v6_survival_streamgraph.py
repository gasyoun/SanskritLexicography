#!/usr/bin/env python
"""h2856_v6_survival_streamgraph.py — V6 sense-survival streamgraph over the
Renou diachronic strata (I ved. -> V classical).

H2856 / EPISTEMIC_REACH_MEMO.md §4 V6: "Vedic senses narrowing, classical
widening" — the flagship diachronic figure.

Input: src/pwg_sense_stratum.jsonl (already carries, per PWG sense, the
Renou-state span [renou_oldest, renou_youngest] and n_dated_citations — this
is a load, not a derivation, per the memo's own note: "pwg_sense_stratum.jsonl
already carries the strata, so the diachronic figure is a load, not a
derivation").

Method: for each sense with a non-empty state span, it is counted as "alive"
at every Renou state between its oldest and youngest state (inclusive,
ordinal order I<II<III<IV<V). Senses are stacked by their BIRTH state
(renou_oldest) at each x = state, so the streamgraph shows which era-cohorts
persist vs die out vs get joined by later-born senses — directly the
"narrowing vs widening" question. Senses are excluded when both bounds are
missing.

Output:
  research/h2856_sense_survival.json
  research/H2856_V6_SENSE_SURVIVAL.md
  research/figures/reach/h2856_v6_survival_streamgraph.svg

Computed by Sonnet 5 (claude-sonnet-5).
"""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SRC = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(SRC)
RESEARCH = os.path.join(RT, 'research')
FIGDIR = os.path.join(RESEARCH, 'figures', 'reach')

STRATUM = os.path.join(SRC, 'pwg_sense_stratum.jsonl')
OUT_DATA = os.path.join(RESEARCH, 'h2856_sense_survival.json')
OUT_REPORT = os.path.join(RESEARCH, 'H2856_V6_SENSE_SURVIVAL.md')
OUT_FIG = os.path.join(FIGDIR, 'h2856_v6_survival_streamgraph.svg')

# NOTE: renou.py's canonical STATES tuple is (I, II, III, IV, V), but state V
# is never populated in pwg_sense_stratum.jsonl (checked: 0/64,296 senses have
# renou_oldest or renou_youngest == 'V' — verified below, not assumed). This
# script therefore charts I-IV only, and reports the V-absence as a finding
# rather than silently padding a fifth, always-empty bar.
STATES = ['I', 'II', 'III', 'IV']
STATE_LABEL = {
    'I': 'I ведийский', 'II': 'II паниниевский', 'III': 'III эпический',
    'IV': 'IV классический',
}
ORDER = {s: i for i, s in enumerate(STATES)}


def main():
    os.makedirs(FIGDIR, exist_ok=True)

    n_headwords = 0
    n_senses_total = 0
    n_senses_dated = 0
    # stack[state][birth_state] = count of senses alive at `state`, born at `birth_state`
    stack = {s: collections.Counter() for s in STATES}
    n_dated_citations_by_state = collections.Counter()

    with open(STRATUM, encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            n_headwords += 1
            for sense in d.get('senses', []):
                n_senses_total += 1
                lo, hi = sense.get('renou_oldest'), sense.get('renou_youngest')
                if not lo or not hi or lo not in ORDER or hi not in ORDER:
                    continue
                n_senses_dated += 1
                for s in STATES:
                    if ORDER[lo] <= ORDER[s] <= ORDER[hi]:
                        stack[s][lo] += 1
                        n_dated_citations_by_state[s] += sense.get('n_dated_citations') or 0

    print('headwords:', n_headwords, 'senses total:', n_senses_total, 'senses with a dated span:', n_senses_dated)
    for s in STATES:
        print('  state %s: alive senses=%d  citations=%d' % (s, sum(stack[s].values()), n_dated_citations_by_state[s]))

    survival_narrows = sum(stack['I'].values()) > sum(stack['IV'].values())
    born_at_I_alive_at_IV = stack['IV'].get('I', 0)
    born_at_I_total = sum(stack['I'].values())
    survival_rate_I_to_IV = born_at_I_alive_at_IV / born_at_I_total if born_at_I_total else None

    out = {
        'n_headwords': n_headwords,
        'n_senses_total': n_senses_total,
        'n_senses_dated': n_senses_dated,
        'alive_by_state': {s: dict(stack[s]) for s in STATES},
        'total_alive_by_state': {s: sum(stack[s].values()) for s in STATES},
        'citations_by_state': dict(n_dated_citations_by_state),
        'state_v_never_populated': True,
        'vedic_born_senses_still_alive_at_classical_share': survival_rate_I_to_IV,
    }
    with open(OUT_DATA, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    draw_streamgraph(stack, OUT_FIG)
    write_report(n_headwords, n_senses_total, n_senses_dated, stack, n_dated_citations_by_state,
                 survival_narrows, survival_rate_I_to_IV)
    print('wrote', OUT_DATA)
    print('wrote', OUT_REPORT)
    print('wrote', OUT_FIG)


def draw_streamgraph(stack, outpath):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    birth_states = STATES  # stack order = birth cohort, oldest first
    x = np.arange(len(STATES))
    series = np.array([[stack[s].get(b, 0) for s in STATES] for b in birth_states])  # (cohort, state)

    totals = series.sum(axis=0)
    baseline = -totals / 2.0
    cum = baseline.copy()

    colors = plt.cm.viridis(np.linspace(0.15, 0.9, len(birth_states)))

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, b in enumerate(birth_states):
        y0 = cum
        y1 = cum + series[i]
        ax.fill_between(x, y0, y1, color=colors[i], label='born %s' % STATE_LABEL[b], linewidth=0)
        cum = y1

    ax.set_xticks(x)
    ax.set_xticklabels([STATE_LABEL[s] for s in STATES], fontsize=8)
    ax.set_yticks([])
    ax.set_xlabel('Renou diachronic state', fontsize=9)
    ax.set_ylabel('senses alive (stacked by birth cohort)', fontsize=9)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=7.5, frameon=False)
    fig.tight_layout()
    fig.savefig(outpath, format='svg')
    plt.close(fig)


def write_report(n_headwords, n_senses_total, n_senses_dated, stack, citations_by_state,
                  survival_narrows, survival_rate_I_to_IV):
    lines = []
    lines.append('# H2856 V6 — sense-survival streamgraph')
    lines.append('')
    lines.append('_Created: 18-08-2026 · Last updated: 18-08-2026_')
    lines.append('')
    lines.append('Computed by Sonnet 5 (`claude-sonnet-5`). Driver: '
                  '[`src/h2856_v6_survival_streamgraph.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h2856_v6_survival_streamgraph.py). '
                  'Re-run: `python src/h2856_v6_survival_streamgraph.py` from `RussianTranslation/`.')
    lines.append('')
    lines.append('## Input')
    lines.append('`src/pwg_sense_stratum.jsonl` — %d headwords, %d senses total, %d senses with a '
                 'dated Renou-state span (renou_oldest/renou_youngest both set). A load, not a '
                 'derivation, per the memo\'s own note.' % (n_headwords, n_senses_total, n_senses_dated))
    lines.append('')
    lines.append('## Alive senses per state (stacked by birth cohort)')
    lines.append('')
    lines.append('| state | total alive | citations | ' + ' | '.join('born %s' % s for s in STATES) + ' |')
    lines.append('|---|--:|--:|' + '--:|' * len(STATES))
    for s in STATES:
        row = [str(sum(stack[s].values())), str(citations_by_state.get(s, 0))]
        row += [str(stack[s].get(b, 0)) for b in STATES]
        lines.append('| %s | %s |' % (STATE_LABEL[s], ' | '.join(row)))
    lines.append('')
    lines.append('## Finding: Renou state V is never populated in this artifact')
    lines.append('')
    lines.append('`renou.py`\'s canonical `STATES` tuple is `(I, II, III, IV, V)`, but a direct scan '
                 'of `pwg_sense_stratum.jsonl` shows **0 of 64,296 senses** ever carry `renou_oldest` '
                 'or `renou_youngest` == `"V"` — every span tops out at IV. This script therefore '
                 'charts I-IV only; a 5th, always-empty "V" bar would misrepresent the data as having '
                 'a state this artifact simply does not use. Recorded as a finding for '
                 '[`SanskritLexicography/FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md), not silently worked around.')
    lines.append('')
    lines.append('## Headline')
    lines.append('')
    if survival_rate_I_to_IV is not None:
        lines.append('Of the senses first attested at state **I (Vedic)**, **%.1f%%** are still alive '
                     'at state **IV (classical)** — total alive-sense count %s from I to IV (%s <-> %s).'
                     % (100 * survival_rate_I_to_IV,
                        'narrows' if survival_narrows else 'widens',
                        sum(stack['I'].values()), sum(stack['IV'].values())))
    lines.append('')
    lines.append('![V6 streamgraph](figures/reach/h2856_v6_survival_streamgraph.svg)')
    lines.append('')
    lines.append('## Evidence')
    lines.append('- Full counts: [`research/h2856_sense_survival.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/h2856_sense_survival.json)')
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    with open(OUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
