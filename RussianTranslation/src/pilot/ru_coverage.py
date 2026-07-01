#!/usr/bin/env python
r"""RU coverage gate — flag any root whose RU translation is silently partial. No LLM.

The RU catch-up gap (gam sat at 6/127 sub-cards for weeks, invisible) happened because
nothing checked RU completeness per root against the intended card set. This does.

For each root it compares the RU store (src/pwg_ru_translated.jsonl, keyed by sub-card) to
the intended sub-card set = the EN store's meta.selected_keys (the rootmap card list; the EN
run enumerates every sub-card, so it is the authoritative per-root denominator). Prints a
per-root RU% and exits non-zero if any root is below --min (default 90), so it can gate CI /
a pre-promote check.

  python src/pilot/ru_coverage.py               # report; exit 1 if any root < 90% RU
  python src/pilot/ru_coverage.py --min 100     # require full RU coverage
  python src/pilot/ru_coverage.py --keys gam    # list gam's missing RU sub-cards (for a catch-up)
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
RU_STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')


def ru_by_root():
    roots = {}
    if not os.path.exists(RU_STORE):
        return roots
    with open(RU_STORE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            root = (r.get('key1') or r.get('subcard') or '').split('~~')[0]
            roots.setdefault(root, set()).add(r.get('subcard'))
    return roots


def intended_by_root():
    """root -> set(sub-card keys) from each EN store's meta.selected_keys (the rootmap set)."""
    out = {}
    for fp in glob.glob(os.path.join(REPO, 'wf_output.en.*.json')):
        root = os.path.basename(fp).replace('wf_output.en.', '').replace('.json', '')
        try:
            d = json.load(open(fp, encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        out[root] = set(d.get('meta', {}).get('selected_keys') or [])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min', type=float, default=90.0, help='fail if any root RU%% below this')
    ap.add_argument('--keys', metavar='ROOT', help='print the missing RU sub-card keys for ROOT')
    args = ap.parse_args()

    ru = ru_by_root()
    intended = intended_by_root()

    if args.keys:
        root = args.keys
        miss = [k for k in sorted(intended.get(root, set())) if k not in ru.get(root, set())]
        print(','.join(miss))
        return

    roots = sorted(set(ru) | set(intended), key=str.lower)
    print('%-8s %6s %6s %6s  %s' % ('root', 'RU', 'intend', 'RU%', 'flag'))
    worst = 100.0
    partial = []
    for root in roots:
        have = ru.get(root, set())
        want = intended.get(root, set())
        denom = len(want) if want else len(have)
        pct = 100.0 * len(have & (want or have)) / denom if denom else 0.0
        # if no EN store to define 'want', report RU subcard count only (unknown denom)
        if not want:
            print('%-8s %6d %6s %6s  %s' % (root, len(have), '?', '?', '(no EN denom)'))
            continue
        flag = '' if pct >= args.min else 'LOW'
        if pct < 100:
            partial.append((root, pct, len(have), len(want)))
        worst = min(worst, pct)
        print('%-8s %6d %6d %5.0f%%  %s' % (root, len(have), len(want), pct, flag))

    print('\npartial RU roots (<100%%): %d' % len(partial))
    for root, pct, h, w in sorted(partial, key=lambda x: x[1]):
        print('  %-8s %5.0f%%  (%d/%d)  catch-up: python src/pilot/ru_coverage.py --keys %s'
              % (root, pct, h, w, root))
    below = [p for p in partial if p[1] < args.min]
    if below:
        print('\nFAIL: %d root(s) below %.0f%% RU coverage' % (len(below), args.min))
        sys.exit(1)
    print('\nOK: all roots >= %.0f%% RU coverage' % args.min)


if __name__ == '__main__':
    main()
