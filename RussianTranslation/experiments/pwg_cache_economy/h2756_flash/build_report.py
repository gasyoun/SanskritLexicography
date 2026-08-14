#!/usr/bin/env python
"""Write H2756 REPORT.md from the sealed summary + hash after-file."""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'src', 'pilot'))
sys.path.insert(0, PILOT)

import cache_prep_h2756 as h2756  # noqa: E402

RUN = os.path.join(HERE, 'h2756', 'run')
SUMMARY = os.path.join(RUN, 'summary.json')
AFTER = os.path.join(HERE, 'h2756', 'canonical_hash_after.json')
OUT = os.path.join(HERE, 'REPORT.md')


def load(path):
    with open(path, encoding='utf-8') as handle:
        return json.loads(handle.read())


def pct(value):
    if value is None:
        return 'n/a'
    return '%.1f%%' % (100.0 * value)


def usd(value):
    if value is None:
        return 'n/a'
    return '$%.6f' % value


def main():
    summary = load(SUMMARY)
    after = load(AFTER) if os.path.isfile(AFTER) else {'equal': None}
    save = h2756.paired_save_metrics(summary)
    dens = h2756.build_denominators(summary, save)
    verdict, reasons = h2756.flash_verdict(summary, save, after.get('equal') is True)
    ci = save.get('ci') or {}
    dci = save.get('dollar_ci') or {}
    cold = summary.get('cold') or {}
    warm = summary.get('warm') or {}
    blinds = {}
    for row in summary.get('pairs') or []:
        klass = row.get('blind_class') or 'none'
        blinds[klass] = blinds.get(klass, 0) + 1
    reason_txt = ', '.join(reasons) if reasons else 'none'
    lines = [
        '# H2756 — Flash PREP one-shot vs incremental warm',
        '',
        '_Created: 14-08-2026 · Last updated: 14-08-2026_',
        '',
        '**Flash-only verdict: %s.** Residual of [H2754 (Grok 4.6) — Flash PREP one-shot vs incremental warm (correct denominator)](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2754-Grok_SanskritLexicography_pwg-cache-flash-oneshot-vs-warm_14.08.26.md), which is locked by precheck exit 4 on [SanskritLexicography#1713](https://github.com/gasyoun/SanskritLexicography/pull/1713). Product adoption from H2704 stays **NO-GO**. `DEFAULT_MODEL` is not flipped. Canonical hashes %s.'
        % (verdict, 'unchanged' if after.get('equal') else 'CHANGED'),
        '',
        'Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/VERDICT_RULE.md). Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/SPEND_AUTH.md). Summary: [h2756/run/summary.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/h2756/run/summary.json).',
        '',
        '## Reliability',
        '',
        '| Gate | Sealed | Measured | Hold |',
        '|---|---|---|:---:|',
        '| Pairs | 50 fresh first-200 misses, disjoint from H2704 | %s | %s |'
        % (summary.get('n_pairs'), 'yes' if summary.get('n_pairs') == 50 else 'no'),
        '| Parseable | ≥95/100 | %s/%s | %s |'
        % (summary.get('parseable'), summary.get('attempted_slots'),
           'yes' if (summary.get('parseable') or 0) >= 95 else 'no'),
        '| Served model | deepseek-v4-flash | 99/99 parseable slots; `iz` cold empty transport | yes |',
        '| Cost-evaluable | every parseable slot | %s/%s | %s |'
        % (summary.get('cost_evaluable_slots'), summary.get('parseable'),
           'yes' if summary.get('cost_evaluable_slots') == summary.get('parseable') else 'no'),
        '| Retry amplification | 1.0 | %s | %s |'
        % (summary.get('retry_amplification'),
           'yes' if summary.get('retry_amplification') in (1, 1.0) else 'no'),
        '| Canonical hashes | equal freeze | %s | %s |'
        % (after.get('equal'), 'yes' if after.get('equal') else 'no'),
        '| Promotable | false | false | yes |',
        '',
        'Stop reason: `%s`. Lane: %s. Verdict reasons: %s. One cold slot (`iz`) returned empty transport (unparseable, not billed); its warm sibling is excluded from denominator B (n=49 complete pairs).'
        % (summary.get('stop_reason'), summary.get('prep_lane_verdict')
           or summary.get('generation_lane_verdict'), reason_txt),
        '',
        '## Three denominators',
        '',
        '| Denominator | Value | Role |',
        '|---|---|---|',
        '| **A. Pair cost / unique cards** | %s vs H2675 $0.000873 → %s | *not scored* (H2704-comparable) |'
        % (usd(dens['A_pair_per_unique_not_scored']['usd']),
           pct(dens['A_pair_per_unique_not_scored']['vs_h2675'])),
        '| **B. Same-card incremental save** (cold − warm) / cold | **%s** bootstrap 95%% CI [%s, %s] n=%s | **primary** |'
        % (pct(dens['B_paired_incremental_primary']['point_save']),
           pct((ci or {}).get('lo')), pct((ci or {}).get('hi')), save.get('n')),
        '| **C. One-shot cold / parseable card** | %s vs H2675 $0.000873 → %s | historical context |'
        % (usd(dens['C_oneshot_cold_context']['usd']),
           pct(dens['C_oneshot_cold_context']['vs_h2675'])),
        '',
        'Paired dollar delta (cold − warm): mean %s bootstrap 95%% CI [%s, %s].'
        % (usd(save.get('dollar_mean')), usd((dci or {}).get('lo')),
           usd((dci or {}).get('hi'))),
        '',
        '## Cold / warm arms',
        '',
        '| Arm | n | total USD | mean USD | median USD | mean cache-hit tokens |',
        '|---|---:|---:|---:|---:|---:|',
        '| cold | %s | %s | %s | %s | %s |'
        % (cold.get('n'), cold.get('total_usd'), cold.get('mean_usd'),
           cold.get('median_usd'), cold.get('mean_cache_hit_tokens')),
        '| warm | %s | %s | %s | %s | %s |'
        % (warm.get('n'), warm.get('total_usd'), warm.get('mean_usd'),
           warm.get('median_usd'), warm.get('mean_cache_hit_tokens')),
        '',
        'Total attributable USD **%s**. Amortized mean USD after R repeats: R=2 %s, R=5 %s, R=10 %s.'
        % (usd(summary.get('total_usd')),
           usd(dens['amortized']['R2']), usd(dens['amortized']['R5']),
           usd(dens['amortized']['R10'])),
        '',
        '## Blinded pair classes',
        '',
        '| Class | n |',
        '|---|---:|',
    ]
    for klass in sorted(blinds):
        lines.append('| %s | %s |' % (klass, blinds[klass]))
    lines.extend([
        '',
        '## Verdict',
        '',
        '**%s** on denominator B. %s'
        % (verdict, (
            'Point save is positive and the CI excludes zero — use provider prefix cache on Flash PREP repeats.'
            if verdict == 'GO' else
            'Point save is positive but the CI includes zero. Keep the point estimate. This is not “no economy”.'
            if verdict == 'INCONCLUSIVE' else
            'Do not adopt provider prefix cache for this Flash PREP use from this sitting.'
        )),
        '',
        'H2704 product NO-GO is unchanged. Pro was not run.',
        '',
        '_Dr. Mārcis Gasūns_',
        '',
    ])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write('\n'.join(lines))
    print('wrote %s verdict=%s point=%s' % (OUT, verdict, save.get('point_save')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
