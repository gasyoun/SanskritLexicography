#!/usr/bin/env python
"""H1702 store repair: apply d4_boundary_wrap.try_boundary_wrap to every eligible
`ru_n==0` row (see d4_boundary_wrap.py module docstring for the method and its
precision discipline). Ineligible rows are left untouched and reported.

  python src/pilot/fix_d4_boundary_wrap.py --store [--dry-run]
"""
import argparse
import json
import os
import shutil
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


def run_store(dry=False):
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

    fixed, ineligible = [], {}
    for r in rows:
        de = r.get('de') or ''
        ru = r.get('ru') or ''
        if not is_ru_n0_candidate(de, ru):
            continue
        label = '%s|%s|%s' % (r.get('key1'), r.get('subcard'), r.get('sense_tag'))
        ok, result = try_boundary_wrap(de, ru)
        if ok:
            fixed.append(label)
            if not dry:
                r['ru'] = result
        else:
            ineligible.setdefault(result, []).append(label)

    total_ineligible = sum(len(v) for v in ineligible.values())
    print('D4 BOUNDARY WRAP %s' % ('(DRY RUN)' if dry else ''))
    print('store                          : %s' % store)
    print('rows                           : %d' % len(rows))
    print('rows fixed                     : %d' % len(fixed))
    print('rows left (manual review)      : %d' % total_ineligible)
    for reason, labels in sorted(ineligible.items(), key=lambda x: -len(x[1])):
        print('  %-25s %d' % (reason, len(labels)))

    if not dry and fixed:
        bak = store + '.h1702.bak'
        if not os.path.exists(bak):
            shutil.copyfile(store, bak)
            print('backup                         : %s' % bak)
        tmp = store + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        os.replace(tmp, store)
        print('wrote                          : %s' % store)

    return {
        'rows_fixed': len(fixed),
        'rows_ineligible': total_ineligible,
        'ineligible_breakdown': {k: len(v) for k, v in ineligible.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', action='store_true', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    run_store(dry=args.dry_run)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
