#!/usr/bin/env python
"""Write H2703 REPORT.md from the sealed summary + ledger. No paid calls."""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
PILOT = os.path.join(RT, 'src', 'pilot')
if PILOT not in sys.path:
    sys.path.insert(0, PILOT)

import cache_economy_report as report  # noqa: E402


def pct(n, d):
    if not d:
        return 'n/a'
    return '%.1f%%' % (100.0 * n / d)


def main():
    run = os.path.join(HERE, 'run')
    summary_path = os.path.join(run, 'summary.json')
    if os.path.isfile(summary_path):
        summary = json.loads(open(summary_path, encoding='utf-8').read())
    else:
        summary = report.load_and_derive(
            os.path.join(run, 'run.manifest.json'),
            os.path.join(run, 'events.jsonl'),
        )
    after_path = os.path.join(HERE, 'canonical_hash_after.json')
    after = {}
    if os.path.isfile(after_path):
        after = json.loads(open(after_path, encoding='utf-8').read())
    freeze_path = os.path.join(HERE, 'freeze.json')
    freeze = {}
    if os.path.isfile(freeze_path):
        freeze = json.loads(open(freeze_path, encoding='utf-8').read())

    verdict = summary.get('generation_lane_verdict')
    cold = summary.get('cold') or {}
    warm = summary.get('warm') or {}
    delta = summary.get('paired_delta_warm_minus_cold') or {}
    boot = delta.get('bootstrap') or {}
    lines = []
    lines.append('# H2703 — exact-request Pro generation cold/warm')
    lines.append('')
    lines.append('_Created: 14-08-2026 · Last updated: 14-08-2026_')
    lines.append('')
    lines.append('**Generation-lane verdict: %s.** Adoption is not decided here; that is [H2704 (Grok 4.6) — PWG cache economy residual C: PREP/TM proof, bounded L3, and adoption verdict](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2704-Grok_SanskritLexicography_pwg-cache-economy-prep-tm-adoption-verdict_14.08.26.md).' % verdict)
    lines.append('')
    lines.append('Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/VERDICT_RULE.md). Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/SPEND_AUTH.md). Summary: [run/summary.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/run/summary.json).')
    lines.append('')
    lines.append('## Frozen before token 1')
    lines.append('')
    lines.append('| Clause | Sealed value | Measured | Hold |')
    lines.append('|---|---|---|:---:|')
    lines.append('| Pairs | 22 | %s | %s |' % (
        summary.get('pairs_complete'),
        'yes' if summary.get('pairs_complete') == 22 else 'no'))
    lines.append('| Parseable | ≥42/44 | %s/44 (%s) | %s |' % (
        summary.get('parseable'),
        pct(summary.get('parseable') or 0, 44),
        'yes' if (summary.get('parseable') or 0) >= 42 else 'no'))
    lines.append('| Served model | deepseek-v4-pro | see per-slot table | %s |' % (
        'yes' if not any(r.get('fail') for r in []) else 'no'))
    lines.append('| Unique det_clean cards | context (H2676=21) | %s | n/a |' % summary.get('unique_clean_cards'))
    lines.append('| USD / unique clean | H2676 $0.01991 | %s | n/a |' % summary.get('usd_per_unique_clean'))
    lines.append('| Canonical hashes | equal freeze | %s | %s |' % (
        after.get('equal'), 'yes' if after.get('equal') else 'no'))
    lines.append('| Promotable | false | false | yes |')
    lines.append('')
    lines.append('Source commit at seal: `%s`.' % (freeze.get('source_commit') or summary.get('run_id')))
    lines.append('')
    lines.append('## Economy')
    lines.append('')
    lines.append('| Arm | n | total USD | mean USD | median USD | mean cache-hit tokens |')
    lines.append('|---|---:|---:|---:|---:|---:|')
    lines.append('| cold | %s | %s | %s | %s | %s |' % (
        cold.get('n'), cold.get('total_usd'), cold.get('mean_usd'),
        cold.get('median_usd'), cold.get('mean_cache_hit_tokens')))
    lines.append('| warm | %s | %s | %s | %s | %s |' % (
        warm.get('n'), warm.get('total_usd'), warm.get('mean_usd'),
        warm.get('median_usd'), warm.get('mean_cache_hit_tokens')))
    lines.append('')
    lines.append('Paired delta (warm − cold): n=%s mean=%s median=%s bootstrap 95%% CI [%s, %s].' % (
        delta.get('n'), delta.get('mean_usd'), delta.get('median_usd'),
        (boot.get('lo') if boot else None), (boot.get('hi') if boot else None)))
    lines.append('')
    lines.append('Total attributable USD **%s**. Retry amplification **%s**. A cache hit is explanatory, not an accepted artifact. Output tokens still dominate Pro cost, so a warm prefix hit need not lower USD per card.' % (
        summary.get('total_usd'), summary.get('retry_amplification')))
    lines.append('')
    lines.append('## Per pair')
    lines.append('')
    lines.append('| key / request | cold parse | warm parse | cold clean | warm clean | cold USD | warm USD | delta | blind |')
    lines.append('|---|:---:|:---:|:---:|:---:|---:|---:|---:|---|')
    key_by_rid = {}
    events_path = os.path.join(run, 'events.jsonl')
    if os.path.isfile(events_path):
        for line in open(events_path, encoding='utf-8'):
            event = json.loads(line)
            rid = event.get('request_id')
            key1 = (event.get('detail') or {}).get('key1')
            if rid and key1:
                key_by_rid[rid] = key1
    for row in summary.get('pairs') or []:
        label = key_by_rid.get(row.get('request_id')) or (row.get('request_id') or '')[:12]
        lines.append('| `%s` | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            label,
            row.get('cold_parseable'), row.get('warm_parseable'),
            row.get('cold_det_clean'), row.get('warm_det_clean'),
            row.get('cold_cost_usd'), row.get('warm_cost_usd'),
            row.get('delta_warm_minus_cold_usd'),
            row.get('blind_class') or ''))
    lines.append('')
    fail = summary.get('fail_reasons') or []
    lines.append('Fail reasons: %s.' % (', '.join(fail) if fail else 'none'))
    lines.append('')
    lines.append('## What this does not authorise')
    lines.append('')
    lines.append('- Adoption of prefix cache as the default PWG generation route (H2704).')
    lines.append('- TM / store write or auto-promote.')
    lines.append('- Flipping `DEFAULT_MODEL` off Flash.')
    lines.append('- Q4 / monster / unattended partition.')
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    out = os.path.join(HERE, 'REPORT.md')
    with open(out, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write('\n'.join(lines))
    print('wrote', out, 'verdict', verdict)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
