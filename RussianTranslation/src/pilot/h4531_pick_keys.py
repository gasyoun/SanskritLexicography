#!/usr/bin/env python
"""H4531: pick the N smallest real d_a sub-cards that have source raw.txt present.

Deliberately tiny and separate from the probe driver: the key list is the one
input a reviewer must be able to re-derive without re-running a paid probe.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))


def pick(root, input_dir, count):
    rootmap = os.path.join(input_dir, root + '.rootmap.json')
    with open(rootmap, encoding='utf-8') as handle:
        cards = json.load(handle)['sub_cards']
    sized = []
    for card in cards:
        raw = os.path.join(input_dir, card['subkey'] + '.raw.txt')
        portrait = os.path.join(input_dir, card['subkey'] + '.portrait.json')
        if os.path.isfile(raw) and os.path.isfile(portrait):
            sized.append((os.path.getsize(raw), card['subkey']))
    sized.sort()
    return [key for _, key in sized[:count]], len(sized), sized[:count]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--root', default='d_a')
    ap.add_argument('--input-dir', required=True)
    ap.add_argument('--count', type=int, default=24)
    args = ap.parse_args(argv)
    keys, total, detail = pick(args.root, args.input_dir, args.count)
    print('eligible sub-cards with raw+portrait: %d' % total)
    print('picked %d (smallest raw bytes): %s' % (len(keys), ','.join(keys)))
    print('bytes: %s' % ' '.join('%s=%d' % (key, size) for size, key in detail))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
