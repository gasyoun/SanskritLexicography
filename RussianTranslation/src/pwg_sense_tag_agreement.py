#!/usr/bin/env python
"""Does a store row's sense_tag describe the row's OWN German text?

The option-2 evidence pass turned up rows whose `sense_tag` contradicts the marker
their `de` field opens with (tagged `1a`, text starts `d>`; tagged `2d`, text starts
`1)`). If that disagreement is store-wide, `sense_tag` is not a sense path at all and
no H3948 retag can be computed from it -- which decides whether the 12 candidates are
rewritable. This measures the agreement rate over every row.

Leading marker = the first enumeration marker the `de` span opens with, after the
`<div n="N">`, dash and whitespace furniture. Compared against the LAST component of
`sense_tag` (`4a` -> `a`, `3calpha` -> the greek letter, `12` -> `12`).

Read-only; the store sha256 is asserted unchanged.

    python pwg_sense_tag_agreement.py
"""
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_four_tier_store_impact as impact  # noqa: E402

LEAD = re.compile(r'^(?:\s|—|-|<div\s+n="[^"]*">|</div>)*'
                  r'(?P<t>[α-ω]|[a-z]|\d{1,2}|[ivxl]{1,5})[)〉]')
TAIL = re.compile(r'([α-ω]|[a-z]|\d{1,2})$')


def lead_marker(de):
    m = LEAD.match(de or '')
    return m.group('t') if m else None


def tag_tail(tag):
    m = TAIL.search(tag or '')
    return m.group(1) if m else None


def main():
    store = impact.find_store(None)
    sha_before = impact.sha256_of(store)
    tot = collections.Counter()
    examples = collections.defaultdict(list)
    with open(store, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            tot['rows'] += 1
            tag = str(row.get('sense_tag') or '')
            de = row.get('de') or ''
            lm, tt = lead_marker(de), tag_tail(tag)
            if not tag:
                tot['no_sense_tag'] += 1
                continue
            if lm is None:
                tot['de_opens_with_no_marker'] += 1
                continue
            tot['comparable'] += 1
            if tt is None:
                tot['tag_has_no_tail'] += 1
            elif lm == tt:
                tot['agree'] += 1
            else:
                tot['disagree'] += 1
                if len(examples['d']) < 8:
                    examples['d'].append((row.get('subcard'), tag, lm,
                                          ' '.join(de.split())[:70]))
            if any(g in tag for g in 'αβγδεζηθ'):
                tot['tag_carries_greek'] += 1
    assert sha_before == impact.sha256_of(store), \
        'FENCE VIOLATION: RU store hash changed during a read-only pass'

    for k in ('rows', 'no_sense_tag', 'de_opens_with_no_marker', 'comparable',
              'agree', 'disagree', 'tag_has_no_tail', 'tag_carries_greek'):
        print('%-26s %6d' % (k, tot[k]))
    if tot['comparable']:
        print('%-26s %6.1f%%' % ('agreement rate',
                                 100.0 * tot['agree'] / tot['comparable']))
    print()
    print('sample disagreements (subcard | sense_tag | de opens with | de):')
    for sc, tag, lm, de in examples['d']:
        print('  %-22s %-6s %-3s %s' % (sc, tag, lm, de))
    return 0


if __name__ == '__main__':
    sys.exit(main())
