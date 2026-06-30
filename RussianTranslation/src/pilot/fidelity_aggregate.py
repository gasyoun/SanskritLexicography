#!/usr/bin/env python
r"""Aggregate Opus fidelity verdicts into precision + 95% Wilson CI (overall + by stratum).

  python src/pilot/fidelity_aggregate.py <verdicts.json|.jsonl> [--sample fidelity_sample.jsonl]

A verdict is BAD when ok=false OR severity>=3 (the judge_ab_score convention). Precision =
fraction of cards that are NOT bad. Wilson score interval (z=1.96) gives the CI a small sample
warrants. Joins verdicts to the sample (by key) for stratum breakdown + reports the issue mix.
"""
import argparse
import collections
import json
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
Z = 1.96


def load_any(path):
    txt = open(path, encoding='utf-8').read().strip()
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            obj = obj.get('verdicts') or obj.get('results') or []
        return obj
    except json.JSONDecodeError:
        return [json.loads(l) for l in txt.splitlines() if l.strip()]


def is_bad(v):
    return (not v.get('ok', True)) or int(v.get('severity', 0)) >= 3


def wilson(good, n):
    if not n:
        return (0.0, 0.0, 0.0)
    p = good / n
    denom = 1 + Z * Z / n
    center = (p + Z * Z / (2 * n)) / denom
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / denom
    return (p, max(0.0, center - half), min(1.0, center + half))


def coarse(stratum):
    s = (stratum or '').lower()
    for k in ('vedic', 'epic', 'classical', 'medieval', 'buddhist'):
        if k in s:
            return k.capitalize()
    return 'unspecified'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('verdicts')
    ap.add_argument('--sample', default=os.path.join(OUT, 'fidelity_sample.jsonl'))
    ap.add_argument('--out', default=os.path.join(OUT, 'fidelity_aggregate.json'))
    args = ap.parse_args()

    verdicts = load_any(args.verdicts)
    stratum_of = {}
    if os.path.exists(args.sample):
        for line in open(args.sample, encoding='utf-8'):
            if line.strip():
                r = json.loads(line)
                stratum_of[r['key']] = coarse(r.get('stratum'))

    n = len(verdicts)
    good = sum(1 for v in verdicts if not is_bad(v))
    p, lo, hi = wilson(good, n)
    issues = collections.Counter(i for v in verdicts if is_bad(v) for i in (v.get('issues') or []))
    sev = collections.Counter(int(v.get('severity', 0)) for v in verdicts)

    per = {}
    by = collections.defaultdict(list)
    for v in verdicts:
        by[stratum_of.get(v.get('key'), 'unspecified')].append(v)
    for st, vs in sorted(by.items()):
        g = sum(1 for v in vs if not is_bad(v))
        per[st] = {'n': len(vs), 'good': g, 'precision': round(wilson(g, len(vs))[0], 3),
                   'ci95': [round(x, 3) for x in wilson(g, len(vs))[1:]]}

    report = {'n': n, 'good': good, 'bad': n - good, 'precision': round(p, 3),
              'ci95_wilson': [round(lo, 3), round(hi, 3)],
              'severity_hist': dict(sorted(sev.items())),
              'bad_issue_hist': dict(issues.most_common()),
              'by_stratum': per}
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    print('=== FIDELITY (Opus judge, DE->RU) ===')
    print('cards judged : %d' % n)
    print('precision    : %.1f%%  (good=%d, bad=%d)' % (100 * p, good, n - good))
    print('95%% CI       : [%.1f%%, %.1f%%]  (Wilson)' % (100 * lo, 100 * hi))
    print('severity hist: %s' % dict(sorted(sev.items())))
    print('bad issues   : %s' % dict(issues.most_common()))
    print('by stratum:')
    for st, d in per.items():
        print('  %-12s n=%-3d precision=%.0f%% CI=[%.0f%%,%.0f%%]'
              % (st, d['n'], 100 * d['precision'], 100 * d['ci95'][0], 100 * d['ci95'][1]))
    print('wrote %s' % args.out)


if __name__ == '__main__':
    main()
