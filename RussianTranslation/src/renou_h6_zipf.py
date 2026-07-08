#!/usr/bin/env python
"""renou_h6_zipf.py — H6: does ls-dcs exact agreement fall with lemma corpus frequency?

Renou hypothesis programme, step 3 (RENOU_HYPOTHESES.md). Reuses the ls/dcs
trichotomy from renou_audit.py (exact / dcs_adds / dcs_misses / conflict) and the
already-built per-lemma DCS text frequency in dcs_lemma_renou.json (`n_texts`,
keyed by `iast` — the same join renou_audit.py uses for its suspect ranking) as
the canonical frequency signal, instead of re-deriving frequency from the raw
1.09M-line corpus_lexicon.jsonl.

Among entries in the 8 canonical {code}.renou.jsonl dicts carrying BOTH `ls`
and `dcs`: bin by log10(n_texts), compute per-bin exact/dcs_adds/dcs_misses
rate, fit a logistic curve P(exact) ~ log10(freq), and report the frequency at
which P(exact) crosses 50%.

  python renou_h6_zipf.py [--dir .] [--index dcs_lemma_renou.json]
                          [--out-svg ../research/figures/renou/h6_zipf_agreement.svg]
"""
import json, os, sys, glob, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = ('pwg', 'mw', 'pw', 'ap', 'ap90', 'ben', 'sch', 'bhs')


def load_dcs_index(path):
    d = json.load(open(path, encoding='utf-8'))
    d.pop('__sources__', None)
    return d


def relation(ls, dcs):
    if ls == dcs:
        return 'exact'
    if ls < dcs:
        return 'dcs_adds'
    if dcs < ls:
        return 'dcs_misses'
    return 'conflict'


def collect_samples(paths, dcs_index):
    """One row per (dict, entry) with both ls and dcs: (code, log10_freq, relation)."""
    rows = []
    per_dict = collections.Counter()
    no_freq = 0
    for p in paths:
        code = os.path.basename(p).split('.')[0]
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            ls = set(e.get('renou_ls') or [])
            dcs = set(e.get('renou_dcs') or [])
            if not (ls and dcs):
                continue
            info = dcs_index.get(e.get('iast', ''))
            n_texts = info['n_texts'] if info else 0
            if n_texts <= 0:
                no_freq += 1
                continue
            rel = relation(ls, dcs)
            rows.append((code, np.log10(n_texts), rel))
            per_dict[code] += 1
    return rows, per_dict, no_freq


def bin_rows(rows, bin_width=0.5):
    """Fixed-width log10-frequency bins -> per-bin trichotomy rates."""
    if not rows:
        return []
    xs = [r[1] for r in rows]
    lo, hi = min(xs), max(xs)
    n_bins = max(1, int(np.ceil((hi - lo) / bin_width)))
    edges = [lo + i * bin_width for i in range(n_bins + 1)]
    edges[-1] = hi + 1e-9
    buckets = [collections.Counter() for _ in range(n_bins)]
    for _, x, rel in rows:
        i = min(n_bins - 1, int((x - lo) / bin_width))
        buckets[i][rel] += 1
    out = []
    for i, b in enumerate(buckets):
        total = sum(b.values())
        if total == 0:
            continue
        mid = (edges[i] + edges[i + 1]) / 2
        out.append({
            'lo': edges[i], 'hi': edges[i + 1], 'mid': mid, 'n': total,
            'exact': b['exact'] / total, 'dcs_adds': b['dcs_adds'] / total,
            'dcs_misses': b['dcs_misses'] / total, 'conflict': b['conflict'] / total,
        })
    return out


def fit_logistic(rows):
    """P(exact) ~ sigmoid(a*log10freq + b) over the raw (unbinned) samples."""
    X = np.array([[r[1]] for r in rows])
    y = np.array([1 if r[2] == 'exact' else 0 for r in rows])
    clf = LogisticRegression()
    clf.fit(X, y)
    a = clf.coef_[0][0]
    b = clf.intercept_[0]
    x50 = -b / a if a != 0 else float('nan')
    return clf, a, b, x50


def make_figure(rows, bins, clf, x50, out_svg):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    xs = [r[1] for r in rows]
    ys = [1 if r[2] == 'exact' else 0 for r in rows]
    rng = np.random.RandomState(0)
    jitter = rng.uniform(-0.03, 0.03, size=len(ys))
    ax.scatter(xs, np.array(ys) + jitter, s=4, alpha=0.06, color='#4c72b0',
               linewidths=0, label='entries (jittered)', rasterized=True)

    bx = [bb['mid'] for bb in bins]
    by = [bb['exact'] for bb in bins]
    bn = [bb['n'] for bb in bins]
    sizes = [max(10, min(140, n / 20)) for n in bn]
    ax.scatter(bx, by, s=sizes, color='#c44e52', zorder=5,
               label='per-bin exact-agreement rate')

    xgrid = np.linspace(min(xs), max(xs), 200)
    pgrid = clf.predict_proba(xgrid.reshape(-1, 1))[:, 1]
    ax.plot(xgrid, pgrid, color='#333333', lw=1.8, label='fitted logistic curve')

    if np.isfinite(x50):
        ax.axvline(x50, color='#888888', lw=1, ls='--')
        ax.axhline(0.5, color='#888888', lw=1, ls='--')

    ax.set_xlabel('log10(DCS lemma text frequency)', fontsize=9)
    ax.set_ylabel('P(ls = dcs exact agreement)', fontsize=9)
    ax.tick_params(labelsize=9)
    ax.set_ylim(-0.08, 1.08)
    ax.legend(fontsize=8, loc='center left')
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_svg), exist_ok=True)
    fig.savefig(out_svg, format='svg', dpi=150)
    plt.close(fig)


def main():
    args = sys.argv[1:]
    d = HERE
    index_path = os.path.join(HERE, 'dcs_lemma_renou.json')
    out_svg = os.path.join(HERE, '..', 'research', 'figures', 'renou', 'h6_zipf_agreement.svg')
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--dir':
            d = args[i + 1]; i += 2
        elif a == '--index':
            index_path = args[i + 1]; i += 2
        elif a == '--out-svg':
            out_svg = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    dcs_index = load_dcs_index(index_path)
    paths = [p for p in sorted(glob.glob(os.path.join(d, '*.renou.jsonl')))
             if os.path.basename(p).split('.')[0] in CANON]
    if not paths:
        raise SystemExit('no canonical {code}.renou.jsonl in %s' % d)

    rows, per_dict, no_freq = collect_samples(paths, dcs_index)
    print('samples with both ls & dcs, freq>0: %d (dropped %d with no/zero freq)'
          % (len(rows), no_freq))
    for code in CANON:
        print('  %-5s %d' % (code.upper(), per_dict.get(code, 0)))

    bins = bin_rows(rows, bin_width=0.5)
    clf, a, b, x50 = fit_logistic(rows)
    freq50 = 10 ** x50 if np.isfinite(x50) else float('nan')

    print('\nlogistic fit: P(exact) = sigmoid(%.4f * log10(freq) + %.4f)' % (a, b))
    print('P(exact) crosses 50%% at log10(freq)=%.3f  ->  freq ≈ %.1f DCS texts' % (x50, freq50))
    print('\nper-bin table (log10freq_mid, n, exact, dcs_adds, dcs_misses, conflict):')
    for bb in bins:
        print('  %.2f  n=%-6d exact=%.3f dcs_adds=%.3f dcs_misses=%.3f conflict=%.3f'
              % (bb['mid'], bb['n'], bb['exact'], bb['dcs_adds'], bb['dcs_misses'], bb['conflict']))

    make_figure(rows, bins, clf, x50, out_svg)
    print('\n-> %s' % out_svg)

    result = {
        'n_samples': len(rows), 'dropped_no_freq': no_freq, 'per_dict': dict(per_dict),
        'logistic_a': float(a), 'logistic_b': float(b),
        'log10_freq_at_p50': float(x50), 'freq_at_p50': float(freq50),
        'bins': bins,
    }
    out_json = os.path.join(HERE, 'renou_h6_zipf_result.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print('-> %s' % out_json)


if __name__ == '__main__':
    main()
