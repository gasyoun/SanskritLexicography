#!/usr/bin/env python
r"""build_h1302_requeue_worklist.py -- park the class-(b) German-residue hits for retranslation.

H1302 step 4(b): the German-residue hits that are NOT a deterministic closed-set sub (class 'b'
in german_residue_scan) are ambiguous multi-word German prose that must be RE-TRANSLATED, not
mechanically substituted. This session has no generation channel, so per the handoff the
committed worklist IS the deliverable for this class -- the next generation window feeds these
roots to `requeue_from_audit.py <root>` (which regenerates with --no-tm, mandatory: the TM
re-serves already-flagged content otherwise; PIPELINE_HISTORY 04-07-2026).

Writes, into pwg_ru/ (all derived from the live canonical store, reproducible):
  H1302_GERMAN_RESIDUE_REQUEUE_WORKLIST_2026-07-19.jsonl  -- one line per class-(b) hit
  H1302_GERMAN_RESIDUE_REQUEUE_ROOTS_2026-07-19.txt       -- unique roots (key1), one per line

  python src/pilot/build_h1302_requeue_worklist.py
"""
import json
import os
import sys
from collections import Counter, OrderedDict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (SRC, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
from store_path import canonical_store            # noqa: E402
import german_residue_scan as grs                  # noqa: E402

DATE = '2026-07-19'
PWG_RU = os.path.join(os.path.dirname(SRC), 'pwg_ru')
WORKLIST = os.path.join(PWG_RU, 'H1302_GERMAN_RESIDUE_REQUEUE_WORKLIST_%s.jsonl' % DATE)
ROOTS = os.path.join(PWG_RU, 'H1302_GERMAN_RESIDUE_REQUEUE_ROOTS_%s.txt' % DATE)


def main():
    store = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)
    hits, n_rows = grs.run(store)
    b = [h for h in hits if h['suggested_class'] == 'b']
    roots = OrderedDict()          # key1 -> set(subcard)
    for h in b:
        roots.setdefault(h['key1'], set()).add(h['subcard'])
    with open(WORKLIST, 'w', encoding='utf-8') as f:
        for h in b:
            f.write(json.dumps({
                'key1': h['key1'], 'subcard': h['subcard'], 'sense_tag': h['sense_tag'],
                'token': h['token'], 'context': h['context'],
                'requeue_note': 'retranslate German prose residue; requeue_from_audit.py --no-tm',
            }, ensure_ascii=False) + '\n')
    with open(ROOTS, 'w', encoding='utf-8') as f:
        f.write('# H1302 German-residue class-(b) requeue roots (%s)\n' % DATE)
        f.write('# feed each to: python src/pilot/requeue_from_audit.py <root> --defect  (--no-tm implied)\n')
        f.write('# %d roots, %d subcards, %d hits\n' % (len(roots), sum(len(s) for s in roots.values()), len(b)))
        for k in roots:
            f.write('%s\n' % k)
    tok = Counter(h['token'].lower() for h in b)
    print('rows scanned        : %d' % n_rows)
    print('class-(b) hits      : %d' % len(b))
    print('unique roots        : %d' % len(roots))
    print('unique subcards     : %d' % sum(len(s) for s in roots.values()))
    print('top tokens          : ' + ', '.join('%s=%d' % (t, c) for t, c in tok.most_common(12)))
    print('wrote               : %s' % WORKLIST)
    print('wrote               : %s' % ROOTS)


if __name__ == '__main__':
    main()
