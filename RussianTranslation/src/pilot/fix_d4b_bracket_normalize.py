#!/usr/bin/env python
"""H2144: D4b bracket-normalize unlock for the D4 `ru_n==0` residual subclass.

H2136's bracket-normalize probe found 63 of the 1,109 residual `ru_n==0` rows refused by
d4_boundary_wrap.try_boundary_wrap ONLY because DE uses a fullwidth/CJK corner-bracket
numbering marker (`〉`/`）`) where RU carries the plain ASCII `)` equivalent (or
the reverse pairing) -- a punctuation-only affix mismatch, not a genuine boundary
ambiguity. This script scans the SAME ineligible pool that plain (non-normalized)
try_boundary_wrap refuses, re-tries each with normalize_brackets=True, and reports (or
applies) only the newly-unlocked subset -- it never touches a row that plain
try_boundary_wrap already accepts or that bracket-normalize still refuses.

  python src/pilot/fix_d4b_bracket_normalize.py            # dry-run report (default)
  python src/pilot/fix_d4b_bracket_normalize.py --store    # apply to the live store
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from d4_boundary_wrap import is_ru_n0_candidate, try_boundary_wrap  # noqa: E402


def run_store(dry=True):
    from store_path import canonical_store
    default_local = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store = canonical_store(default_local)
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)

    rows = []
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line:
                rows.append(json.loads(line))

    newly_unlocked = []
    still_refused = {}
    for r in rows:
        de = r.get('de') or ''
        ru = r.get('ru') or ''
        if not is_ru_n0_candidate(de, ru):
            continue
        label = '%s|%s|%s' % (r.get('key1'), r.get('subcard'), r.get('sense_tag'))
        ok_plain, _ = try_boundary_wrap(de, ru)
        if ok_plain:
            # Already handled by the H1702 exact-affix fixer -- out of scope here.
            continue
        ok_norm, result_norm = try_boundary_wrap(de, ru, normalize_brackets=True)
        if ok_norm:
            newly_unlocked.append((r, label, result_norm))
            if not dry:
                r['ru'] = result_norm
        else:
            still_refused.setdefault(result_norm, []).append(label)

    print('D4B BRACKET NORMALIZE %s' % ('(DRY RUN)' if dry else ''))
    print('store                          : %s' % store)
    print('rows                           : %d' % len(rows))
    print('newly unlocked                 : %d' % len(newly_unlocked))
    print('still refused                  : %d' % sum(len(v) for v in still_refused.values()))
    for reason, labels in sorted(still_refused.items(), key=lambda x: -len(x[1])):
        print('  %-25s %d' % (reason, len(labels)))
    for _r, label, result in newly_unlocked:
        print('  UNLOCKED: %s -> %s' % (label, result[:120]))

    if not dry and newly_unlocked:
        # H2146: locked (PromoteClaim) + unique per-run backup + atomic replace, same
        # convention as fix_d4_boundary_wrap.py -- an unlocked '.tmp' rewrite here would
        # be the same last-writer-wins hazard FINDINGS §513 fixed for the sibling fixer.
        from store_write import locked_store_rewrite
        locked_store_rewrite(store, rows, tag='h2144fix')
        print('wrote                          : %s' % store)

    return {
        'rows_unlocked': len(newly_unlocked),
        'rows_still_refused': sum(len(v) for v in still_refused.values()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', action='store_true', help='apply to the live store (default: dry-run)')
    args = parser.parse_args()
    run_store(dry=not args.store)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
