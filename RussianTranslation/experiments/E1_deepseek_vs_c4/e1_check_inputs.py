#!/usr/bin/env python
"""H2488 — report which E1 frozen keys have raw+portrait inputs."""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_PILOT = os.path.normpath(os.path.join(HERE, '..', '..', 'src', 'pilot'))
if SRC_PILOT not in sys.path:
    sys.path.insert(0, SRC_PILOT)
from window_common import input_paths  # noqa: E402

MAIN_INPUT = os.environ.get('PWG_INPUT_DIR') or os.path.join(
    r'C:\Users\user\Documents\GitHub\SanskritLexicography',
    'RussianTranslation', 'src', 'pilot', 'input')

def main():
    man = json.load(open(os.path.join(HERE, 'sample_manifest.json'), encoding='utf-8'))
    ids_path = os.path.join(SRC_PILOT, 'h1210', 'card_ids.txt')
    card_ids = [ln.strip() for ln in open(ids_path, encoding='utf-8') if ln.strip()][:40]
    slp = man['keys']
    print('keys', len(slp), 'card_ids', len(card_ids), 'input_dir', MAIN_INPUT)
    print('dir_exists', os.path.isdir(MAIN_INPUT))
    present, missing = [], []
    for slp1, cid in zip(slp, card_ids):
        hits = []
        for stem in (cid, slp1):
            rp, pp = input_paths(stem, input_dir=MAIN_INPUT)
            if os.path.exists(rp) and os.path.exists(pp):
                hits.append(stem)
        ok = bool(hits)
        (present if ok else missing).append((slp1, cid, hits))
        print(('OK' if ok else 'MISSING'), slp1, cid, 'stems=' + ','.join(hits) if hits else '')
    print('present', len(present), 'missing', len(missing))
    return 0 if not missing else 2

if __name__ == '__main__':
    sys.exit(main())
