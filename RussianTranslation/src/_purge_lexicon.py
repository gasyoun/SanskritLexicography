#!/usr/bin/env python
"""One-off recovery: purge fabricated rows from corpus_lexicon.jsonl.

A row is fabricated if its source verse-group is UNTRANSLATED — i.e. the group's
seg=ru segment carries no Cyrillic (a '…' placeholder). DeepSeek hallucinated
fluent Russian against those non-existent translations (audit 2026-06-16:
12_mahabharata-shantiparva 99.8% placeholder, 13_…-anushasanaparva 100%).

Keep a row iff: its group's source ru has Cyrillic (real translation) AND the
gloss itself has Cyrillic AND ru!=sa AND ru not a refusal string AND no '√' in
the key. Dedup exact (group,slp1,ru,kind). Backs up the original first.
"""
import json, os, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
LEX = os.path.join(HERE, 'corpus_lexicon.jsonl')
CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')
REJECT_RU = {'(no clear counterpart)', 'нет соответствия', '—', '…', '...'}


def has_cyr(s):
    return bool(s) and bool(CYR.search(s))


# 1) which works appear in the lexicon → load only those source files
works = set()
for line in open(LEX, encoding='utf-8'):
    try:
        works.add(json.loads(line)['work'])
    except Exception:
        pass

# 2) set of TRANSLATED groups: source seg=ru has Cyrillic
translated = set()
for w in works:
    f = os.path.join(SM, w + '.jsonl')
    if not os.path.exists(f):
        continue
    for line in open(f, encoding='utf-8'):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('deleted') or e.get('seg') != 'ru':
            continue
        if has_cyr(e.get('text')):
            translated.add(e.get('group'))
print('translated (Cyrillic-ru) groups across these works:', len(translated))

# 3) filter
kept, dropped, seen = 0, 0, set()
drop_by_work = {}
shutil.copyfile(LEX, LEX + '.prepurge')
tmp = LEX + '.clean'
with open(tmp, 'w', encoding='utf-8', newline='') as out:
    for line in open(LEX, encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            dropped += 1; continue
        g, slp1 = r.get('group'), r.get('slp1', '')
        sa = (r.get('sa') or '').strip()
        ru = (r.get('ru') or '').strip()
        ok = (g in translated and has_cyr(ru) and ru != sa
              and ru not in REJECT_RU and '√' not in slp1)
        key = (g, slp1, ru, r.get('kind'))
        if ok and key not in seen:
            seen.add(key)
            out.write(line if line.endswith('\n') else line + '\n')
            kept += 1
        else:
            dropped += 1
            drop_by_work[r.get('work')] = drop_by_work.get(r.get('work'), 0) + 1

os.replace(tmp, LEX)
print('kept=%d  dropped=%d' % (kept, dropped))
print('dropped by work:')
for w, c in sorted(drop_by_work.items(), key=lambda x: -x[1]):
    print('  %7d  %s' % (c, w))
print('backup: corpus_lexicon.jsonl.prepurge')
