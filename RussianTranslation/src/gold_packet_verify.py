#!/usr/bin/env python
"""Verify reviewer packet CSVs cover the gold scaffold exactly once."""
import argparse
import csv
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def key(row):
    return (row.get('id') or '', row.get('slp1') or '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('gold_csv')
    ap.add_argument('packet_dir')
    args = ap.parse_args()
    source = read_rows(args.gold_csv)
    expected = [key(r) for r in source]
    source_duplicates = sorted(k for k in set(expected) if expected.count(k) > 1)
    if source_duplicates:
        print('source duplicates:', source_duplicates[:20])
        raise SystemExit('gold scaffold contains duplicate id/slp1 keys')
    packet_paths = sorted(glob.glob(os.path.join(args.packet_dir, '*.csv')))
    if not packet_paths:
        raise SystemExit('no packet CSVs found in %s' % args.packet_dir)
    seen = []
    for path in packet_paths:
        seen.extend(key(r) for r in read_rows(path))
    missing = sorted(set(expected) - set(seen))
    extra = sorted(set(seen) - set(expected))
    duplicates = sorted(k for k in set(seen) if seen.count(k) > 1)
    if missing or extra or duplicates or len(seen) != len(expected):
        if missing:
            print('missing:', missing[:20])
        if extra:
            print('extra:', extra[:20])
        if duplicates:
            print('duplicates:', duplicates[:20])
        raise SystemExit('packet verification failed')
    print('packet verification OK: %d packet(s), %d row(s)' %
          (len(packet_paths), len(seen)))


if __name__ == '__main__':
    main()
