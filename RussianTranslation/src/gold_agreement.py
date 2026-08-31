#!/usr/bin/env python
"""Compute human gold precision and double-review agreement.

  python gold_agreement.py [human_gold_labels.jsonl] [out_dir]
  python gold_agreement.py fixture.jsonl tmp/reports --fixture
"""
import argparse
import collections, json, math, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.join(HERE, 'pilot') not in sys.path:
    sys.path.insert(0, os.path.join(HERE, 'pilot'))
import gate_evidence as ge                                          # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, '..'))
INP = os.path.join(ROOT, 'gold', 'human_gold_labels.jsonl')
PRECISION = os.path.join(ROOT, 'gold', 'human_precision_report.md')
AGREEMENT = os.path.join(ROOT, 'gold', 'double_review_agreement.md')
GOOD = {'correct', 'lemma-variant', 'proper-name'}
ERR = {'wrong-sense', 'hallucinated'}
LABELS = ['correct', 'lemma-variant', 'proper-name', 'partial',
          'wrong-sense', 'hallucinated']


def wilson(x, n):
    if not n:
        return 0.0, 0.0, 0.0
    z = 1.96
    p = x / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p, max(0.0, c - h), min(1.0, c + h)


def load(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def item_labels(rows):
    by_id = collections.defaultdict(list)
    meta = {}
    for r in rows:
        by_id[str(r['id'])].append(r['human_label'])
        meta[str(r['id'])] = r
    final = {}
    for rid, labels in by_id.items():
        counts = collections.Counter(labels)
        final[rid] = counts.most_common(1)[0][0]
    return final, meta, by_id


def kappa(by_id):
    pairs = [labs[:2] for labs in by_id.values() if len(labs) >= 2]
    if not pairs:
        return None, 0, 0.0
    agree = sum(1 for a, b in pairs if a == b)
    marg1 = collections.Counter(a for a, _ in pairs)
    marg2 = collections.Counter(b for _, b in pairs)
    n = len(pairs)
    po = agree / n
    pe = sum((marg1[l] / n) * (marg2[l] / n) for l in LABELS)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0, n, po


def stats(final, meta, filt):
    labs = collections.Counter(label for rid, label in final.items() if filt(meta[rid]))
    n = sum(labs.values())
    good = sum(labs[l] for l in GOOD)
    err = sum(labs[l] for l in ERR)
    p, lo, hi = wilson(good, n)
    return n, good, labs['partial'], err, p, lo, hi


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('jsonl_path', nargs='?', default=INP)
    ap.add_argument('out_dir', nargs='?', default=os.path.join(ROOT, 'gold'))
    ap.add_argument('--fixture', action='store_true',
                    help='allow tiny fixture data; release mode requires double review')
    ap.add_argument('--evidence', default=None, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    path = args.jsonl_path
    out_dir = args.out_dir
    release_mode = not args.fixture and os.path.abspath(path) == os.path.abspath(INP)
    # W1 (H3748, #1803 C6-01). The release-mode expression above is unchanged, and so is
    # its defect: `release_mode` is False for ANY non-default input path, so a run over a
    # non-default path silently drops the >=1-kappa-pair guard while still writing into
    # the watched gold/ directory. The evidence record makes that state legible — it says
    # which file was read, its sha256, whether the guard was armed, and (below) warns when
    # a non-fixture run disarmed it.
    ev = ge.GateEvidence('gold_agreement',
                         'human gold precision + double-review agreement (C6-01)')
    precision_path = os.path.join(out_dir, 'human_precision_report.md')
    agreement_path = os.path.join(out_dir, 'double_review_agreement.md')
    rows = load(path)
    if not rows:
        sys.exit('human gold labels are empty: %s' % path)
    final, meta, by_id = item_labels(rows)
    os.makedirs(out_dir, exist_ok=True)
    n, good, part, err, p, lo, hi = stats(final, meta, lambda _: True)
    lines = ['# Human gold precision', '',
             '| metric | value |', '|---|---|',
             '| unique items | %d |' % len(final),
             '| reviewer rows | %d |' % len(rows),
             '| precision | %.1f%% (95%% CI %.1f-%.1f) |' % (100*p, 100*lo, 100*hi),
             '| partial | %.1f%% |' % (100 * part / max(n, 1)),
             '| errors | %.1f%% |' % (100 * err / max(n, 1)), '',
             '## By period', '',
             '| period | n | precision | 95% CI |', '|---|---|---|---|']
    for per in sorted({m.get('period') for m in meta.values()}):
        sn, _, _, _, sp, slo, shi = stats(final, meta, lambda m, per=per: m.get('period') == per)
        if sn:
            lines.append('| %s | %d | %.1f%% | %.1f-%.1f |' % (per, sn, 100*sp, 100*slo, 100*shi))
    lines += ['', '## By kind', '', '| kind | n | precision | 95% CI |', '|---|---|---|---|']
    for kind in sorted({m.get('kind') for m in meta.values()}):
        sn, _, _, _, sp, slo, shi = stats(final, meta, lambda m, kind=kind: m.get('kind') == kind)
        if sn:
            lines.append('| %s | %d | %.1f%% | %.1f-%.1f |' % (kind, sn, 100*sp, 100*slo, 100*shi))
    open(precision_path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    kap, pair_n, po = kappa(by_id)
    if release_mode and (pair_n == 0 or kap is None):
        sys.exit('release agreement requires at least one double-reviewed item with Cohen kappa')
    alines = ['# Double-review agreement', '',
              '| metric | value |', '|---|---|',
              '| double-reviewed items | %d |' % pair_n,
              '| percent agreement | %.1f%% |' % (100 * po),
              '| Cohen kappa | %s |' % ('n/a' if kap is None else '%.3f' % kap)]
    open(agreement_path, 'w', encoding='utf-8').write('\n'.join(alines) + '\n')

    ev.add_input('labels', path=path, units=len(rows))
    ev.add_predicate('precision', evaluations=n, hits=err)
    ev.add_predicate('kappa_pairs', evaluations=pair_n, hits=0)
    ev.note('unique_items', len(final))
    ev.note('release_mode', release_mode)
    ev.note('cohen_kappa', None if kap is None else round(kap, 3))
    ev.note('written', [os.path.basename(precision_path), os.path.basename(agreement_path)])
    if not args.fixture and not release_mode:
        ev.warnings.append(
            'C6-01: --fixture was not passed and the input is not the default gold path, '
            'so the >=1-kappa-pair release guard is DISARMED for this run (%s)' % path)
    ev.set_verdict('pass')
    if not pair_n:
        ev.declare_expected_empty(
            'no_double_reviewed_items',
            'single-review corpus: there is no pair to compute Cohen kappa over, and the '
            'precision half is still fully measured over %d item(s)' % len(final))
    ev.assert_nonvacuous()
    ev.emit(args.evidence or ge.sidecar_for(agreement_path))

    print('human precision report → %s' % precision_path)
    print('double-review agreement → %s' % agreement_path)
    print(ev.summary())


if __name__ == '__main__':
    main()
