#!/usr/bin/env python
r"""audit_store_gates.py — deterministic, zero-token markup audit of the LIVE pwg_ru store.

H3590 (27-08-2026). `audit_translation.py` audits a window's <stem>.raw.txt vs .merged.md
and `spot_check_daily.py` audits one day's auto-promoted cards; nothing re-ran the HARD
gates over every row that actually landed in `pwg_ru_translated.jsonl`. This does, with
the exact thresholds the RU path uses (`markup_fidelity_gates`, check_ab=False), and diffs
the src store against the `pwg-ru-data/tm/` mirror so silent drift is visible.

  python src/audit_store_gates.py [--store PATH] [--mirror PATH] [--no-mirror] [--json OUT]

Exit 1 on any hard flag (LS-LOSS / SAN-LOSS / NO-RUSSIAN) in the src store; 0 otherwise.
Read-only: never writes the store.
"""
import argparse
import collections
import difflib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from markup_fidelity_gates import (  # noqa: E402
    GLOSS_RE,
    dup_key,
    markup_span_flags,
    markup_wrapper_soft_flags,
    missing_target_flag,
)
from pwg_tm_gates import surface_form_flags  # noqa: E402

DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DEFAULT_MIRROR = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'pwg-ru-data', 'tm', 'pwg_ru_translated.jsonl'))
FLAG_NAME = re.compile(r'[(:]')


def load_rows(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            row['_line'] = lineno
            rows.append(row)
    return rows


def row_id(row):
    """Stable identity for diffing. sense_tag alone is degenerate (homograph blocks share
    'main'), so the head of `de` is folded in."""
    return (row.get('key1') or '', row.get('subcard') or '',
            row.get('sense_tag') or '', (row.get('de') or '')[:80])


def gate_rows(rows):
    hard = collections.Counter()
    soft = collections.Counter()
    flagged = []
    surface = []
    dups = collections.defaultdict(list)
    for row in rows:
        de = row.get('de') or ''
        ru = row.get('ru') or ''
        flags = list(markup_span_flags(de, ru, check_ab=False))
        missing = missing_target_flag(bool(GLOSS_RE.search(de)), ru, field='russian')
        if missing:
            flags.append(missing)
        for flag in flags:
            hard[FLAG_NAME.split(flag)[0]] += 1
        for flag in markup_wrapper_soft_flags(de, ru):
            soft[FLAG_NAME.split(flag)[0]] += 1
        if flags:
            flagged.append({'key1': row.get('key1'), 'subcard': row.get('subcard'),
                            'sense_tag': row.get('sense_tag'), 'line': row['_line'],
                            'review_status': row.get('review_status'), 'flags': flags})
        sflags = surface_form_flags(de, ru)
        if sflags:
            surface.append({'key1': row.get('key1'), 'subcard': row.get('subcard'),
                            'sense_tag': row.get('sense_tag'), 'line': row['_line'],
                            'flags': sflags})
        if ru:
            dups[dup_key(ru)].append(row_id(row))
    clusters = {k: v for k, v in dups.items() if len(v) > 1}
    byte_identical = sum(1 for v in clusters.values() if len(set(v)) < len(v))
    return {'rows': len(rows), 'hard': dict(hard), 'soft': dict(soft), 'flagged': flagged,
            'surface': surface,
            'identical_ru_clusters': len(clusters), 'byte_identical_id_dups': byte_identical}


def diff_stores(src_rows, mirror_rows):
    src = {row_id(r): r for r in src_rows}
    mir = {row_id(r): r for r in mirror_rows}
    only_src = [k for k in src if k not in mir]
    only_mirror = [k for k in mir if k not in src]
    changed = []
    for k, r in src.items():
        if k in mir and (r.get('ru') or '') != (mir[k].get('ru') or ''):
            old, new = mir[k].get('ru') or '', r.get('ru') or ''
            sm = difflib.SequenceMatcher(None, old, new)
            ops = [(t, old[i1:i2][:40], new[j1:j2][:40])
                   for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']
            changed.append({'id': k[:3], 'ops': ops[:4]})
    return {'only_src': [k[:3] for k in only_src], 'only_mirror': [k[:3] for k in only_mirror],
            'changed_ru': changed}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--mirror', default=DEFAULT_MIRROR)
    ap.add_argument('--no-mirror', action='store_true')
    ap.add_argument('--json', default=None, help='write the full machine-readable result here')
    args = ap.parse_args()

    src_rows = load_rows(args.store)
    result = {'store': args.store, 'gates': gate_rows(src_rows)}
    g = result['gates']
    print('=== store gate audit: %s' % args.store)
    print('rows=%d hard_flagged_rows=%d hard=%s soft=%s' % (g['rows'], len(g['flagged']), g['hard'], g['soft']))
    print('identical-ru clusters=%d byte-identical id dups=%d' % (g['identical_ru_clusters'], g['byte_identical_id_dups']))
    for f in g['flagged']:
        print('  %-14s %-28s %-10s L%-6d %s' % (f['key1'], f['subcard'], (f['sense_tag'] or '')[:10], f['line'], ' '.join(f['flags'])))
    surf = g.get('surface') or []
    print('=== GAPS §17 surface-form (does not change exit; TM gate owns promotion)')
    print('surface_rows=%d GLOSS-DE-RESIDUE=%d AB-MUTATED=%d' % (
        len(surf),
        sum(1 for r in surf if 'GLOSS-DE-RESIDUE' in r['flags']),
        sum(1 for r in surf if 'AB-MUTATED' in r['flags'])))
    for f in surf[:12]:
        print('  %-14s %-28s %-10s L%-6d %s' % (
            f['key1'], f['subcard'], (f['sense_tag'] or '')[:10], f['line'],
            ' '.join(f['flags'])))
    if len(surf) > 12:
        print('   ... %d more (see --json)' % (len(surf) - 12))

    if not args.no_mirror and os.path.exists(args.mirror):
        mirror_rows = load_rows(args.mirror)
        d = diff_stores(src_rows, mirror_rows)
        result['mirror'] = {'path': args.mirror, 'rows': len(mirror_rows),
                            'only_src': len(d['only_src']), 'only_mirror': len(d['only_mirror']),
                            'changed_ru': len(d['changed_ru']), 'detail': d}
        print('=== mirror diff vs %s (rows=%d)' % (args.mirror, len(mirror_rows)))
        print('only_src=%d only_mirror=%d changed_ru=%d' % (len(d['only_src']), len(d['only_mirror']), len(d['changed_ru'])))
        for c in d['changed_ru'][:10]:
            print('  ', c['id'], c['ops'])
        if len(d['changed_ru']) > 10:
            print('   ... %d more (see --json)' % (len(d['changed_ru']) - 10))
    elif not args.no_mirror:
        print('=== mirror not found: %s' % args.mirror)

    if args.json:
        with open(args.json, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
    print('FLAGGED_JSON: %s' % json.dumps([[f['key1'], f['subcard'], f['sense_tag']] for f in g['flagged']], ensure_ascii=False))
    sys.exit(1 if g['flagged'] else 0)


if __name__ == '__main__':
    main()
