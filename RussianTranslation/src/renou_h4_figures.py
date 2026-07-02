#!/usr/bin/env python
"""renou_h4_figures.py — H4 dumbbell figures: citation-share vs usage-share by
register, one SVG per dictionary.

Reads the intermediate produced by renou_h4_citation_bias.py
(h4_citation_bias.json, gitignored — regenerate with that script) and renders
a publication-grade dumbbell chart per dict (both-route registers only, sorted
by |log2 bias| descending): usage-share dot, citation-share dot, connecting
line, register on the y-axis. No baked-in titles (captions live in the write-up
MD); axis labels + legend only. Font >= 9pt.

  python renou_h4_figures.py [--in h4_citation_bias.json] [--outdir ../research/figures/renou]

Computed by Sonnet 5 (claude-sonnet-5).
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

HERE = os.path.dirname(os.path.abspath(__file__))

REGISTER_LABEL = {
    'rgveda': 'ṛgveda', 'atharva': 'atharva', 'yajus': 'yajus', 'brahmana': 'brāhmaṇa',
    'upanisad': 'upaniṣad', 'sutra': 'sūtra', 'vyakarana': 'vyākaraṇa', 'epig': 'epig',
    'epic': 'epic', 'purana': 'purāṇa', 'tantra': 'tantra', 'smrti': 'smṛti',
    'karika': 'kārikā', 'bhasya': 'bhāṣya', 'katha': 'kathā', 'natya': 'nāṭya',
    'kavya': 'kāvya', 'bauddha': 'bauddha', 'jaina': 'jaina', 'hors_inde': 'hors inde',
}


def draw_dict(code, data, outdir):
    both = data['both_route_registers']
    if not both:
        print('  %s: no both-route registers, skipping figure' % code)
        return
    rows = sorted(both.items(), key=lambda kv: abs(kv[1]['log2_bias'] or 0), reverse=True)
    regs = [REGISTER_LABEL.get(r, r) for r, _ in rows]
    usage = [v['usage_share'] * 100 for _, v in rows]
    citation = [v['citation_share'] * 100 for _, v in rows]

    n = len(rows)
    fig_h = max(2.2, 0.38 * n + 1.0)
    fig, ax = plt.subplots(figsize=(7.2, fig_h))
    y = list(range(n))

    for yi, u, c in zip(y, usage, citation):
        ax.plot([u, c], [yi, yi], color='#9aa0aa', linewidth=1.4, zorder=1)
    ax.scatter(usage, y, s=46, color='#4c72b0', label='usage share (corpus)', zorder=2)
    ax.scatter(citation, y, s=46, color='#c44e52', label='citation share (ls)', zorder=2,
               marker='D')

    ax.set_yticks(y)
    ax.set_yticklabels(regs, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('share (%)', fontsize=9)
    ax.tick_params(axis='x', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='lower right', fontsize=8, frameon=False)
    ax.set_xlim(left=0)
    fig.tight_layout()

    out = os.path.join(outdir, 'h4_citation_vs_usage_%s.svg' % code)
    fig.savefig(out, format='svg')
    plt.close(fig)
    print('  %s -> %s (%d registers)' % (code, os.path.basename(out), n))


def main():
    args = sys.argv[1:]
    in_path = os.path.join(HERE, 'h4_citation_bias.json')
    outdir = os.path.normpath(os.path.join(HERE, '..', 'research', 'figures', 'renou'))
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--in':
            in_path = args[i + 1]; i += 2
        elif a == '--outdir':
            outdir = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    os.makedirs(outdir, exist_ok=True)
    data = json.load(open(in_path, encoding='utf-8'))
    for code, d in data['dicts'].items():
        draw_dict(code, d, outdir)


if __name__ == '__main__':
    main()
