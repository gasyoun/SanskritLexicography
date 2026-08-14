#!/usr/bin/env python
"""Split a blind 400-packet into independent-judge shards (non-Grok-4.6)."""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--packet', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--shards', type=int, default=8)
    args = ap.parse_args(argv)
    rows = C.read_jsonl(args.packet)
    n = max(1, args.shards)
    os.makedirs(args.out_dir, exist_ok=True)
    size = (len(rows) + n - 1) // n
    written = []
    for i in range(n):
        chunk = rows[i * size:(i + 1) * size]
        if not chunk:
            continue
        path = os.path.join(args.out_dir, 'shard_%02d.jsonl' % i)
        C.write_jsonl(path, chunk)
        written.append({'path': path, 'n': len(chunk)})
    print(json.dumps({'shards': written, 'total': len(rows)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
