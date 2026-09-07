#!/usr/bin/env python
"""h3979_ledger_backfill.py — H3979: compute changed_ru for the two ledger rows written
before H4055 added content-sensitive receipts (H3751, H3947), so the H3969 question
("did the 02-09 refresh actually carry the German->Latin sweep?") is answerable from the
ledger alone, without re-deriving it from local-only .bak files that only this box holds.

Reuses refresh_tm_mirror.load/rid/semantic_diff — no reimplementation. Each historical
refresh's mirror-before and mirror-after states are recovered from the LOCAL .bak chain
(tm/*.bak, gitignored) plus the current mirror file, keyed on the sha256 values the ledger
itself already recorded — verified against those recorded shas before any diff is trusted.

  python h3979_ledger_backfill.py --tm-dir <path-to-pwg-ru-data>/tm
      [--ledger PATH] [--apply]

  Dry-run by default: prints the computed annotation for both rows, writes nothing.
"""
import argparse
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from refresh_tm_mirror import load, sha256_file, semantic_diff  # noqa: E402

# (handoff, mirror_before_file, mirror_after_file, expected_sha_before, expected_sha_after)
TRANSITIONS = [
    ('H3751', 'pwg_ru_translated.jsonl.h3751.20260831T025926Z.bak',
     'pwg_ru_translated.jsonl.h3947.20260902T202344Z.bak',
     '3022239c63ac5fbf8788276aa8bc893b5433a01b92e4e2984a3e24982ce99818',
     '58c2172607c34928b417178d50ee80823956c4ccdde5f4d49ab8b0407e06faf0'),
    ('H3947', 'pwg_ru_translated.jsonl.h3947.20260902T202344Z.bak',
     'pwg_ru_translated.jsonl',
     '58c2172607c34928b417178d50ee80823956c4ccdde5f4d49ab8b0407e06faf0',
     '79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65'),
]


def compute(tm_dir, receipt_max_keys=100):
    out = {}
    for handoff, before_name, after_name, exp_before, exp_after in TRANSITIONS:
        before_path = os.path.join(tm_dir, before_name)
        after_path = os.path.join(tm_dir, after_name)
        for p in (before_path, after_path):
            if not os.path.exists(p):
                raise SystemExit('missing local file (only present on the box that ran the '
                                  'refresh): %s' % p)
        got_before = sha256_file(before_path)
        got_after = sha256_file(after_path)
        if got_before != exp_before:
            raise SystemExit('%s mirror-before sha mismatch: got %s expected %s (%s)' % (
                handoff, got_before[:12], exp_before[:12], before_path))
        if got_after != exp_after:
            raise SystemExit('%s mirror-after sha mismatch: got %s expected %s (%s)' % (
                handoff, got_after[:12], exp_after[:12], after_path))
        mirror_rows = load(before_path)
        src_rows = load(after_path)
        sem = semantic_diff(src_rows, mirror_rows)
        out[handoff] = {
            'backfilled': True,
            'backfilled_by': 'H3979',
            'shared_ids': sem['shared_ids'],
            'ru_equal': sem['ru_equal'],
            'changed_ru': sem['changed_ru'],
            'changed_ru_keys': sem['changed_keys'][:receipt_max_keys],
            'changed_ru_keys_truncated': len(sem['changed_keys']) > receipt_max_keys,
        }
    return out


def apply(ledger_path, annotations):
    rows = [json.loads(l) for l in io.open(ledger_path, encoding='utf-8') if l.strip()]
    touched = 0
    for row in rows:
        ann = annotations.get(row.get('handoff'))
        if ann and 'changed_ru' not in row:
            row.update(ann)
            touched += 1
    with io.open(ledger_path, 'w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return touched


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--tm-dir', required=True,
                     help='pwg-ru-data/tm directory holding the .bak chain and current mirror')
    ap.add_argument('--ledger', default=None,
                     help='ledger jsonl to annotate (default: <tm-dir>/mirror_refresh_ledger.jsonl)')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    ledger = args.ledger or os.path.join(args.tm_dir, 'mirror_refresh_ledger.jsonl')
    ann = compute(args.tm_dir)
    for handoff, entry in ann.items():
        print('%s: changed_ru=%d shared_ids=%d ru_equal=%d' % (
            handoff, entry['changed_ru'], entry['shared_ids'], entry['ru_equal']))

    if not args.apply:
        print('\nDRY RUN — nothing written. Re-run with --apply to annotate %s.' % ledger)
        return 0

    if not os.path.exists(ledger):
        raise SystemExit('ledger not found: %s' % ledger)
    touched = apply(ledger, ann)
    print('\nannotated %d row(s) in %s' % (touched, ledger))
    return 0


if __name__ == '__main__':
    sys.exit(main())
