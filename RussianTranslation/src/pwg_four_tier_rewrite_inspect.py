#!/usr/bin/env python
"""H3948 option-2: print the printed source behind each of the 12 rewrite candidates.

MG's ruling authorises rewriting only the rows "где ярус читается однозначно".
Deciding that requires looking at the PWG text, not at counters. For every key1
that owns a candidate row this prints:

  * the sense-id set before and after H3948 (what appeared / disappeared);
  * for the row's own sense_tag, the pre- and post-H3948 gloss text;
  * the store row's German span and its paid Russian translation.

Read-only. Nothing is written anywhere.

    python pwg_four_tier_rewrite_inspect.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import microstructure as ms                 # noqa: E402
import pwg_mask                             # noqa: E402
import pwg_four_tier_store_impact as impact  # noqa: E402

REPORTS_DIR = os.path.join(HERE, '..', 'reports')
CANDIDATES = os.path.join(REPORTS_DIR, 'H3948_four_tier_rewrite_candidates.json')


def texts(buf, pre):
    """{sense_id: text} for one record under one parser."""
    saved = (ms.MARK, ms.ADJACENT_MARKERS)
    if pre:
        ms.MARK, ms.ADJACENT_MARKERS = impact.PRE_H3948_MARK, impact.PRE_H3948_ADJACENT
    try:
        out = {}
        body = ms.ADJACENT_MARKERS.sub(r'\1 ', '\n'.join(buf[1:]))
        for seg in ms.split_senses(body):
            if seg['n'] == '0':
                continue
            out.setdefault(ms.sense_path(seg), []).append(ms.clean_de(seg['text']))
        return out
    finally:
        ms.MARK, ms.ADJACENT_MARKERS = saved


def short(s, n=180):
    s = ' '.join((s or '').split())
    return s if len(s) <= n else s[:n] + ' …'


def main():
    cand = json.load(open(CANDIDATES, encoding='utf-8'))
    rows = cand['rows']
    wanted = {}
    for r in rows:
        wanted.setdefault(r['key1'], []).append(r)

    records = {}
    for buf in pwg_mask.records():
        k1, _k2, _h = ms.header(buf)
        if k1 in wanted:
            records.setdefault(k1, []).append(buf)

    for k1 in sorted(wanted):
        bufs = records.get(k1, [])
        print('=' * 78)
        print('key1 %s   (%d homograph record(s) in pwg.txt)' % (k1, len(bufs)))
        old_all, new_all = {}, {}
        for i, buf in enumerate(bufs):
            for sid, ts in texts(buf, True).items():
                old_all.setdefault(sid, []).extend((i, t) for t in ts)
            for sid, ts in texts(buf, False).items():
                new_all.setdefault(sid, []).extend((i, t) for t in ts)
        gone = sorted(set(old_all) - set(new_all))
        born = sorted(set(new_all) - set(old_all))
        print('  ids disappeared : %s' % (', '.join(gone) or '(none)'))
        print('  ids appeared    : %s' % (', '.join(born) or '(none)'))
        for r in wanted[k1]:
            tag = r['sense_tag']
            print('  -- row %s  sense_tag=%r  review=%s/%s'
                  % (r['subcard'], tag, r['review_status'], r['reviewer']))
            print('     tag still exists after H3948: %s' % (tag in new_all))
            for label, src in (('PRE ', old_all), ('POST', new_all)):
                for rec_i, t in src.get(tag, []):
                    print('     %s [rec %d] %s' % (label, rec_i, short(t)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
