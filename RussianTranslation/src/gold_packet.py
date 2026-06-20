#!/usr/bin/env python
"""Split the human gold-review CSV into deterministic reviewer packets."""
import argparse
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_OUT = os.path.join(ROOT, 'gold', 'reviewer_packets')


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_path')
    ap.add_argument('--batch-size', type=int, default=40)
    ap.add_argument('--out-dir', default=DEFAULT_OUT)
    args = ap.parse_args()
    if args.batch_size < 1:
        raise SystemExit('--batch-size must be positive')
    fields, rows = read_rows(args.csv_path)
    rows = sorted(rows, key=lambda r: (r.get('period') or '', r.get('kind') or '',
                                      int(r.get('id') or 0), r.get('slp1') or ''))
    os.makedirs(args.out_dir, exist_ok=True)
    written = 0
    for start in range(0, len(rows), args.batch_size):
        packet = rows[start:start + args.batch_size]
        path = os.path.join(args.out_dir, 'gold_packet_%03d_%03d.csv'
                            % (start + 1, start + len(packet)))
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            w.writerows(packet)
        written += 1
    print('gold reviewer packets: %d packet(s), %d row(s) -> %s'
          % (written, len(rows), args.out_dir))


if __name__ == '__main__':
    main()
