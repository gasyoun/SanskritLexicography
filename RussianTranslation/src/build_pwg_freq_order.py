#!/usr/bin/env python
r"""Order the PWG->RU/EN slice worklist by corpus frequency (Bridge 1).

Consumes the kosha frequency sidecar feed
(kosha/data/frequency/lemma_frequency.tsv, built by build_frequency_layer.py from
VisualDCS archive.sqlite M9) as the SINGLE source of frequency truth, joins it onto
the PWG headword set (SLP1 `k1` from headword_index.tsv), and emits
`pwg_freq_order.tsv` so the /pwg-slice worklist translates high-frequency roots first
(more corpus coverage per translated token).

Also CROSS-CHECKS the archive `count_all` ranking against the frequency gate the
pwg_ru kit already uses (dcs_freq.json, built from dcs_full.sqlite by
build_dcs_freq.py) — the two are independent DCS extractions, so agreement on the
shared lemma set validates the archive layer. dcs_freq.json is IAST-keyed; archive is
SLP1, transcoded with sanskrit_util.from_slp1 for the comparison only (the emitted
join key stays SLP1).

  python build_pwg_freq_order.py                 # -> pwg_freq_order.tsv (+ report)
  python build_pwg_freq_order.py --feed PATH     # override lemma_frequency.tsv
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FEED = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'kosha', 'data', 'frequency', 'lemma_frequency.tsv'))
HEADWORDS = os.path.join(HERE, 'headword_index.tsv')
DCS_FREQ = os.path.join(HERE, 'dcs_freq.json')
OUT_TSV = os.path.join(HERE, 'pwg_freq_order.tsv')
OUT_REPORT = os.path.join(HERE, 'pwg_freq_order.report.json')

# sanskrit_util is the canonical transcoder (SHARED_CODE §; SLP1-native CDSL keys).
sys.path.insert(0, os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'sanskrit-util', 'py')))
from sanskrit_util import from_slp1  # noqa: E402


def load_feed(path):
    """lemma_slp1 -> (count_all|None, rank_all, periods_sum, coverage_pct|None)."""
    feed = {}
    with open(path, encoding='utf-8') as f:
        header = f.readline().rstrip('\n').split('\t')
        idx = {c: i for i, c in enumerate(header)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            lemma = p[idx['lemma_slp1']]
            ca = p[idx['count_all']]
            feed[lemma] = {
                'count_all': int(ca) if ca else None,
                'rank_all': int(p[idx['rank_all']]),
                'periods_sum': int(p[idx['periods_sum']] or 0),
                'coverage_pct': p[idx['coverage_pct']] or '',
            }
    return feed


def load_pwg_headwords(path):
    """Distinct SLP1 `k1` headwords from the PWG headword index."""
    hw = []
    seen = set()
    with open(path, encoding='utf-8') as f:
        next(f)
        for line in f:
            k = line.split('\t', 1)[0]
            if k and k not in seen:
                seen.add(k)
                hw.append(k)
    return hw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feed', default=DEFAULT_FEED)
    args = ap.parse_args()

    if not os.path.exists(args.feed):
        sys.exit(f"frequency feed not found: {args.feed}\n"
                 "Build it first: python kosha/data/frequency/build_frequency_layer.py")

    feed = load_feed(args.feed)
    pwg = load_pwg_headwords(HEADWORDS)

    # Join PWG headwords to the feed. Rank a headword by count_all (fallback
    # periods_sum). Headwords with no signal sort last, in stable header order.
    rows = []
    matched = 0
    for k1 in pwg:
        e = feed.get(k1)
        if e:
            matched += 1
            primary = e['count_all'] if e['count_all'] is not None else e['periods_sum']
            rows.append((k1, e['count_all'], e['periods_sum'],
                         e['coverage_pct'], primary, e['count_all'] is not None))
        else:
            rows.append((k1, None, 0, '', 0, False))

    rows.sort(key=lambda r: (0 if r[5] else 1, -(r[4] or 0), r[0]))

    with open(OUT_TSV, 'w', encoding='utf-8', newline='\n') as f:
        f.write('slice_order\tk1_slp1\tcount_all\tperiods_sum\tcoverage_pct\n')
        for i, (k1, ca, ps, cov, _, _) in enumerate(rows, 1):
            f.write(f"{i}\t{k1}\t{'' if ca is None else ca}\t{ps}\t{cov}\n")

    # ---- cross-check vs the existing dcs_freq.json gate (IAST-keyed) ----
    dcs = json.load(open(DCS_FREQ, encoding='utf-8'))['by_lemma']
    both = 0
    agree_dir = 0  # of adjacent-in-archive pwg pairs, how many keep order in dcs
    ranked = [k1 for (k1, _, _, _, _, has) in rows if has]  # archive-ranked pwg headwords
    dcs_counts = []
    for k1 in ranked:
        c = dcs.get(from_slp1(k1))
        if c:
            both += 1
            dcs_counts.append(c['count'])
        else:
            dcs_counts.append(None)
    # Kendall-lite: over consecutive archive-ranked pairs both present in dcs,
    # fraction where dcs count is non-increasing (same direction as archive rank).
    pairs = 0
    for a, b in zip(dcs_counts, dcs_counts[1:]):
        if a is not None and b is not None:
            pairs += 1
            if a >= b:
                agree_dir += 1
    concordance = round(agree_dir / pairs, 3) if pairs else None

    report = {
        'generator': 'build_pwg_freq_order.py',
        'feed': os.path.relpath(args.feed, HERE),
        'pwg_headwords': len(pwg),
        'matched_in_freq_feed': matched,
        'matched_pct': round(100 * matched / len(pwg), 1),
        'crosscheck_vs_dcs_freq': {
            'archive_ranked_pwg_headwords': len(ranked),
            'also_in_dcs_freq': both,
            'also_in_dcs_freq_pct': round(100 * both / len(ranked), 1) if ranked else None,
            'adjacent_pair_concordance': concordance,
            'note': ('concordance = fraction of consecutive archive-ranked PWG '
                     'headword pairs whose dcs_freq counts are non-increasing; '
                     '~1.0 means the two independent DCS extractions rank PWG '
                     'headwords the same way.'),
        },
    }
    json.dump(report, open(OUT_REPORT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    open(OUT_REPORT, 'a', encoding='utf-8').write('\n')

    print(f"wrote {os.path.basename(OUT_TSV)}: {len(rows)} PWG headwords "
          f"({matched} = {report['matched_pct']}% with a freq signal)")
    print(f"cross-check vs dcs_freq.json: {both}/{len(ranked)} shared, "
          f"adjacent-pair concordance {concordance}")


if __name__ == '__main__':
    main()
