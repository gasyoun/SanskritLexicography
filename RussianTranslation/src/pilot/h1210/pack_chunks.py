#!/usr/bin/env python
r"""H1210 — repack a prep_slice v3 payload into SIZE-BOUNDED chunks.

`prep_slice.py --chunk N` splits contiguously into N equal-COUNT groups. On the H1210
100-card selection that is unusable: card_block sizes span 0.4 KB .. 46 KB (the selection
is deliberately stratified by length), so equal-count chunks came out 40 KB .. 950 KB and
four of twelve blew the 512 KB Workflow scriptPath ceiling that `inject_payload.py`
refuses at.

This packs greedily by MEASURED emitted size instead: each chunk carries the shared
`prompt_common` once plus as many cards as fit under `--cap` bytes of compact JSON
(the form `inject_payload.py` embeds), preserving the payload's card order. A single card
larger than the cap is emitted alone with a loud warning — never silently dropped.

Usage:
  python src/pilot/h1210/pack_chunks.py <slice_payload.json> <out_prefix> [--cap 400000]
Writes: <out_prefix>.chunkNN.json  (same schema prep_slice emits; feed to build_args.py)
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def emitted_size(header, cards):
    return len(json.dumps(dict(header, cards=cards), ensure_ascii=False).encode('utf-8'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('payload')
    ap.add_argument('out_prefix')
    ap.add_argument('--cap', type=int, default=400000,
                    help='max compact-JSON bytes per chunk (Workflow scriptPath cap is 512 KB; '
                         'the template and the derived worker_schema also consume budget)')
    a = ap.parse_args()

    payload = json.load(open(a.payload, encoding='utf-8'))
    header = {k: v for k, v in payload.items() if k != 'cards'}
    cards = payload['cards']

    groups, cur = [], []
    for c in cards:
        trial = cur + [c]
        if cur and emitted_size(header, trial) > a.cap:
            groups.append(cur)
            cur = [c]
        else:
            cur = trial
    if cur:
        groups.append(cur)

    paths = []
    for i, g in enumerate(groups, 1):
        size = emitted_size(header, g)
        if size > a.cap:
            print('WARNING: chunk %02d is %d bytes > cap %d (single oversized card %s) — '
                  'emitted anyway, inject_payload.py will refuse it if it also exceeds the '
                  'hard 512 KB ceiling' % (i, size, a.cap, g[0]['key1']))
        p = '%s.chunk%02d.json' % (a.out_prefix, i)
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(dict(header, chunk={'index': i, 'of': len(groups)}, cards=g),
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        paths.append(p)
        print('chunk %02d: %2d cards, %7d B compact -> %s'
              % (i, len(g), size, os.path.basename(p)))
    print('packed %d cards into %d chunks (cap %d B)' % (len(cards), len(groups), a.cap))


if __name__ == '__main__':
    main()
