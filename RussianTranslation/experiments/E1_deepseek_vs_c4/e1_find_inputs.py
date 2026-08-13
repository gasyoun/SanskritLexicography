#!/usr/bin/env python
"""H2488 — locate raw/portrait for the frozen 40 keys across known input roots."""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_PILOT = os.path.normpath(os.path.join(HERE, '..', '..', 'src', 'pilot'))
ids_path = os.path.join(SRC_PILOT, 'h1210', 'card_ids.txt')
card_ids = [ln.strip() for ln in open(ids_path, encoding='utf-8') if ln.strip()][:40]

roots = [
    os.path.join(r'C:\Users\user\Documents\GitHub\SanskritLexicography',
                 'RussianTranslation', 'src', 'pilot', 'input'),
    os.path.join(r'C:\Users\user\Documents\GitHub\SanskritLexicography',
                 'RussianTranslation', 'src', 'pilot', 'output'),
    os.path.join(r'D:\pwg-ru-data', 'input'),
    os.path.join(r'D:\pwg-ru-data', 'src', 'pilot', 'input'),
    os.path.join(r'C:\Users\user\Documents\GitHub', 'pwg-ru-data', 'input'),
    os.environ.get('PWG_INPUT_DIR') or '',
    os.environ.get('PWG_DATA_ROOT') or '',
]
roots = [r for r in roots if r]
print('searching', len(card_ids), 'ids in', len(roots), 'roots')
for root in roots:
    exists = os.path.isdir(root)
    print('ROOT', root, 'exists' if exists else 'absent')
    if not exists:
        continue
    hits = 0
    sample = None
    for cid in card_ids:
        for name in (cid + '.raw.txt', cid + '.portrait.json'):
            p = os.path.join(root, name)
            if os.path.exists(p):
                hits += 1
                sample = p
    print('  hits', hits, 'sample', sample)
