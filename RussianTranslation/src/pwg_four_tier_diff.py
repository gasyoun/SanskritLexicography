#!/usr/bin/env python
"""Before/after segmentation diff for H3948 (FINDINGS §453) — READ-ONLY.

Shows, for named PWG headwords, how `microstructure.leaf_senses()` segmented a
record under the pre-H3948 two-tier parser (§447: digit + latin only) versus the
four-tier parser (roman division + digit + latin + greek). Nothing is written:
no store row is opened, no file is produced.

  python pwg_four_tier_diff.py                 # the three default entries
  python pwg_four_tier_diff.py ati upa gam     # any key1 values
  python pwg_four_tier_diff.py --width 90
"""
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import microstructure as ms          # noqa: E402
import pwg_mask                      # noqa: E402

# The §447 two-tier forms, exactly as they stood before H3948.
PRE_H3948_MARK = re.compile(r'(?<![^\s—])(?P<t>\d{1,2}|[a-z])[)〉]')
PRE_H3948_ADJACENT = re.compile(r'([)〉])(?=(?:\d{1,2}|[a-z])[)〉])')

DEFAULT_KEYS = ['Gana', 'akzara', 'ati']


def segment(buf):
    """(sense_id, gloss) pairs exactly as leaf_senses() would emit them."""
    out = []
    body = ms.ADJACENT_MARKERS.sub(r'\1 ', '\n'.join(buf[1:]))
    for seg in ms.split_senses(body):
        if seg['n'] == '0':
            continue
        out.append((ms.sense_path(seg), ms.clean_de(seg['text'])))
    return out


def with_pre_h3948(fn, *a):
    """Run `fn` with microstructure reverted to the two-tier parser."""
    mark, adj = ms.MARK, ms.ADJACENT_MARKERS
    ms.MARK, ms.ADJACENT_MARKERS = PRE_H3948_MARK, PRE_H3948_ADJACENT
    try:
        return fn(*a)
    finally:
        ms.MARK, ms.ADJACENT_MARKERS = mark, adj


def records_for(keys):
    """One buffer per requested key1, in corpus order (first record wins)."""
    want, found = set(keys), {}
    for buf in pwg_mask.records():
        k1, _k2, _h = ms.header(buf)
        if k1 in want and k1 not in found:
            found[k1] = buf
            if len(found) == len(want):
                break
    return found


def block(label, segs, width):
    print('%s (%d leaf senses): %s' % (
        label, len(segs), ' '.join(i for i, _ in segs) or '(none)'))
    for sense_id, gloss in segs:
        print('    %-10s %s' % (sense_id, gloss[:width]))


def report(k1, buf, width):
    """Both segmentations in full.

    Sense ids are NOT comparable across the two parsers — a roman division
    restarts digit numbering, so the old parser's '1' and the new parser's
    'I1'/'II1' are different senses that happen to share a label. Printing the
    two lists whole is the only honest diff; a merged +/- listing would invent
    an identity relation the data does not have.
    """
    old = with_pre_h3948(segment, buf)
    new = segment(buf)
    print('=' * (width + 16))
    print('%s  —  leaf senses %d → %d' % (k1, len(old), len(new)))
    print('-' * (width + 16))
    block('  BEFORE  §447 two-tier ', old, width)
    print()
    block('  AFTER   H3948 four-tier', new, width)
    print()


def main(argv):
    width = 100
    keys = []
    i = 0
    while i < len(argv):
        if argv[i] == '--width':
            width = int(argv[i + 1])
            i += 2
        else:
            keys.append(argv[i])
            i += 1
    keys = keys or DEFAULT_KEYS
    found = records_for(keys)
    print('H3948 before/after segmentation diff (READ-ONLY)')
    print('corpus: %s' % pwg_mask.PWG)
    print('each entry is printed twice, in full: as the pre-H3948 parser '
          'segmented it and as it segments now\n')
    missing = [k for k in keys if k not in found]
    for k in keys:
        if k in found:
            report(k, found[k], width)
    if missing:
        print('not found in the corpus: %s' % ', '.join(missing))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
