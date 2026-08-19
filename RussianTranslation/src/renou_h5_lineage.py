#!/usr/bin/env python
"""renou_h5_lineage.py -- H5: does MW inherit the Petersburg citation structure?

Renou hypothesis programme, step 5 (RENOU_HYPOTHESES.md). Joins MW<->PWG (the
hypothesized lineage) and MW<->AP (an independent-lineage baseline, per
FINDINGS #83/#97 -- Apte is not Petersburg-derived) on shared headwords
(key1, homographs collapsed by union), and compares their `<ls>`-provenance
state profiles (`renou_ls`, states in {I..V}):

  (a) exact-match rate       -- set(MW.renou_ls) == set(OTHER.renou_ls)
  (b) mean Jaccard            -- |A n B| / |A u B|
  (c) containment             -- P(MW.renou_ls subseteq OTHER.renou_ls)

Containment is restricted to headwords where MW itself carries at least one
`<ls>` state (renou_ls non-empty) -- an empty MW set is trivially a subset of
anything and would inflate the score without testing inheritance. Bootstrap
95% CIs (2000 resamples) on both containment rates, plus a permutation test
on the containment gap (MW-PWG minus MW-AP).

  python renou_h5_lineage.py [--dir .] [--out-svg ../research/figures/renou/h5_lineage.svg]
"""
import json, os, sys, glob

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
STATES = ('I', 'II', 'III', 'IV', 'V')


def load_ls_profiles(path):
    """key1 -> union of renou_ls states across all lines sharing that key1
    (homographs collapsed, matching the union_headwords.tsv convention)."""
    profiles = {}
    n_lines = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            n_lines += 1
            key1 = e.get('key1', '')
            ls = set(e.get('renou_ls') or [])
            profiles.setdefault(key1, set()).update(ls)
    return profiles, n_lines


def compare(mw, other):
    """Shared headwords with MW.renou_ls non-empty -> (exact, jaccard, contained)."""
    shared = set(mw) & set(other)
    rows = []
    for k in shared:
        a = mw[k]
        if not a:
            continue
        b = other[k]
        exact = 1 if a == b else 0
        union = a | b
        jacc = len(a & b) / len(union) if union else 1.0
        contained = 1 if a <= b else 0
        rows.append((k, exact, jacc, contained))
    return rows, len(shared)


def bootstrap_ci(vals, n_boot=2000, seed=0):
    vals = np.asarray(vals, dtype=float)
    if len(vals) == 0:
        return float('nan'), float('nan'), float('nan')
    rng = np.random.RandomState(seed)
    means = np.empty(n_boot)
    n = len(vals)
    for i in range(n_boot):
        idx = rng.randint(0, n, n)
        means[i] = vals[idx].mean()
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(vals.mean()), float(lo), float(hi)


def permutation_test_gap(contained_pwg, contained_ap, n_perm=5000, seed=0):
    """Two-sample permutation test on the containment-rate gap (unpaired,
    since the PWG-shared and AP-shared headword sets differ)."""
    rng = np.random.RandomState(seed)
    a = np.asarray(contained_pwg, dtype=float)
    b = np.asarray(contained_ap, dtype=float)
    observed = a.mean() - b.mean()
    pooled = np.concatenate([a, b])
    na = len(a)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pooled)
        gap = pooled[:na].mean() - pooled[na:].mean()
        if gap >= observed:
            count += 1
    p = (count + 1) / (n_perm + 1)
    return float(observed), float(p)


def make_figure(stats, out_svg):
    labels = ['MW vs PWG\n(hypothesized lineage)', 'MW vs AP\n(independent baseline)']
    means = [stats['pwg']['containment_mean'], stats['ap']['containment_mean']]
    los = [stats['pwg']['containment_mean'] - stats['pwg']['containment_lo'],
           stats['ap']['containment_mean'] - stats['ap']['containment_lo']]
    his = [stats['pwg']['containment_hi'] - stats['pwg']['containment_mean'],
           stats['ap']['containment_hi'] - stats['ap']['containment_mean']]
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    x = np.arange(2)
    colors = ['#c44e52', '#4c72b0']
    ax.bar(x, means, yerr=[los, his], capsize=6, color=colors, width=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel('P(MW ls-states subseteq OTHER ls-states)', fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.tick_params(labelsize=9)
    for xi, m in zip(x, means):
        ax.text(xi, m + 0.03, '%.3f' % m, ha='center', fontsize=9)
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_svg), exist_ok=True)
    fig.savefig(out_svg, format='svg', dpi=150)
    plt.close(fig)


def main():
    args = sys.argv[1:]
    d = HERE
    out_svg = os.path.join(HERE, '..', 'research', 'figures', 'renou', 'h5_lineage.svg')
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--dir':
            d = args[i + 1]; i += 2
        elif a == '--out-svg':
            out_svg = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    mw_path = os.path.join(d, 'mw.renou.jsonl')
    pwg_path = os.path.join(d, 'pwg.renou.jsonl')
    ap_path = os.path.join(d, 'ap.renou.jsonl')
    for p in (mw_path, pwg_path, ap_path):
        if not os.path.exists(p):
            raise SystemExit('missing input: %s' % p)

    mw, n_mw = load_ls_profiles(mw_path)
    pwg, n_pwg = load_ls_profiles(pwg_path)
    ap, n_ap = load_ls_profiles(ap_path)
    print('lines: MW=%d PWG=%d AP=%d' % (n_mw, n_pwg, n_ap))
    print('distinct key1: MW=%d PWG=%d AP=%d' % (len(mw), len(pwg), len(ap)))

    rows_pwg, n_shared_pwg = compare(mw, pwg)
    rows_ap, n_shared_ap = compare(mw, ap)
    print('\nshared headwords (key1 in both): MW&PWG=%d  MW&AP=%d' % (n_shared_pwg, n_shared_ap))
    print('of those, MW carries a non-empty ls-set: MW&PWG=%d  MW&AP=%d'
          % (len(rows_pwg), len(rows_ap)))

    stats = {}
    for name, rows in (('pwg', rows_pwg), ('ap', rows_ap)):
        exact = [r[1] for r in rows]
        jacc = [r[2] for r in rows]
        contained = [r[3] for r in rows]
        em, elo, ehi = bootstrap_ci(exact)
        jm, jlo, jhi = bootstrap_ci(jacc)
        cm, clo, chi = bootstrap_ci(contained)
        stats[name] = {
            'n': len(rows),
            'exact_mean': em, 'exact_lo': elo, 'exact_hi': ehi,
            'jaccard_mean': jm, 'jaccard_lo': jlo, 'jaccard_hi': jhi,
            'containment_mean': cm, 'containment_lo': clo, 'containment_hi': chi,
        }

    gap, p_perm = permutation_test_gap(
        [r[3] for r in rows_pwg], [r[3] for r in rows_ap])
    stats['containment_gap_pwg_minus_ap'] = gap
    stats['permutation_p_one_sided'] = p_perm

    print('\n%-10s %-8s %-24s %-24s %-24s' % ('baseline', 'n', 'exact-match', 'mean Jaccard', 'containment'))
    for name in ('pwg', 'ap'):
        s = stats[name]
        print('%-10s %-8d %.3f [%.3f, %.3f]     %.3f [%.3f, %.3f]     %.3f [%.3f, %.3f]' % (
            name.upper(), s['n'],
            s['exact_mean'], s['exact_lo'], s['exact_hi'],
            s['jaccard_mean'], s['jaccard_lo'], s['jaccard_hi'],
            s['containment_mean'], s['containment_lo'], s['containment_hi']))

    print('\ncontainment gap (MW-PWG minus MW-AP) = %.4f, one-sided permutation p = %.4f'
          % (gap, p_perm))

    make_figure(stats, out_svg)
    print('\n-> %s' % out_svg)

    result = {
        'n_mw_lines': n_mw, 'n_pwg_lines': n_pwg, 'n_ap_lines': n_ap,
        'n_mw_key1': len(mw), 'n_pwg_key1': len(pwg), 'n_ap_key1': len(ap),
        'n_shared_key1_mw_pwg': n_shared_pwg, 'n_shared_key1_mw_ap': n_shared_ap,
        'stats': stats,
    }
    out_json = os.path.join(HERE, 'renou_h5_lineage_result.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print('-> %s' % out_json)


if __name__ == '__main__':
    main()
