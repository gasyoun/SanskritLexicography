#!/usr/bin/env python
"""H2136: Sonnet independent re-verification of H1702 (D4 boundary wrap), run against
the Grok 4.5 override re-measure (PR #969). Deliberately uses its own seeds (not Grok's
42/11) so the residual and fixed-row samples are a genuinely independent draw, not a
replay of the same rows Grok already read.

  python src/pilot/h2136_sonnet_independent_check.py
"""
import json
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from d4_boundary_wrap import (  # noqa: E402
    GLOSS_SPAN, is_ru_n0_candidate, scan_store, split_by_anchors, try_boundary_wrap,
)
from store_path import canonical_store  # noqa: E402

BRACKET_NORMALIZE = str.maketrans({
    '〉': ')', '）': ')',
    '〈': '(', '（': '(',
})


def load_rows(store):
    rows = []
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    default_local = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store = canonical_store(default_local)
    rows = load_rows(store)
    print('store: %s' % store)
    print('rows : %d' % len(rows))

    eligible, ineligible = scan_store(store)
    total_ineligible = sum(len(v) for v in ineligible.values())
    print('eligible (mechanical fix): %d' % len(eligible))
    print('ineligible total          : %d' % total_ineligible)
    for reason, items in sorted(ineligible.items(), key=lambda x: -len(x[1])):
        print('  %-28s %d' % (reason, len(items)))

    # residual sample, independent seed (not Grok's 42)
    flat = [(reason, ln, label) for reason, items in ineligible.items() for ln, label in items]
    rng = random.Random(7)
    sample = rng.sample(flat, min(30, len(flat)))
    print('\n=== residual sample n=%d seed=7 ===' % len(sample))
    row_by_line = {}
    with open(store, encoding='utf-8') as f:
        for ln, line in enumerate(f):
            row_by_line[ln] = line
    for reason, ln, label in sample:
        row = json.loads(row_by_line[ln])
        de = (row.get('de') or '')[:160]
        ru = (row.get('ru') or '')[:160]
        print('- [%s] %s' % (reason, label))
        print('    DE: %s' % de)
        print('    RU: %s' % ru)

    # fixed-row sample: rows with de_n == ru_n >= 1 (already wrapped, from prior H1702 apply)
    fixed_candidates = []
    for ln, r in enumerate(rows):
        de = r.get('de') or ''
        ru = r.get('ru') or ''
        de_n = len(GLOSS_SPAN.findall(de))
        ru_n = len(GLOSS_SPAN.findall(ru))
        if de_n == ru_n >= 1:
            fixed_candidates.append((ln, r))
    rng2 = random.Random(91)
    fixed_sample = rng2.sample(fixed_candidates, min(25, len(fixed_candidates)))
    print('\n=== fixed-row integrity sample n=%d seed=91 (of %d de_n==ru_n>=1 rows) ===' %
          (len(fixed_sample), len(fixed_candidates)))
    bad = 0
    for ln, r in fixed_sample:
        ru = r.get('ru') or ''
        label = '%s|%s|%s' % (r.get('key1'), r.get('subcard'), r.get('sense_tag'))
        swallowed = False
        for m in GLOSS_SPAN.finditer(ru):
            span = m.group(0)
            if any(tok in span for tok in ('{#', '<ls', '<ab', '<is')):
                swallowed = True
        if swallowed:
            bad += 1
            print('  ANCHOR-SWALLOWED: %s' % label)
    print('  anchor-swallowed-into-gloss: %d / %d' % (bad, len(fixed_sample)))

    # bracket-normalize probe on the ineligible pool
    unlocked = 0
    still_refused = 0
    for reason, items in ineligible.items():
        for ln, label in items:
            row = json.loads(row_by_line[ln])
            de = row.get('de') or ''
            ru = row.get('ru') or ''
            ru_norm = ru.translate(BRACKET_NORMALIZE)
            de_norm = de.translate(BRACKET_NORMALIZE)
            ok, _ = try_boundary_wrap(de_norm, ru_norm)
            if ok:
                unlocked += 1
            else:
                still_refused += 1
    print('\n=== bracket-normalize probe (\\u3009/\\uff09 -> ")" etc.) ===')
    print('  would unlock: %d' % unlocked)
    print('  still refused: %d' % still_refused)


if __name__ == '__main__':
    raise SystemExit(main())
