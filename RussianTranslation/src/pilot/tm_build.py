#!/usr/bin/env python
r"""Harvest a sense-level translation memory from all wf_output.<lang>.*.json stores.

Every successfully-translated sense is a (German source -> target) pair the pipeline
already paid for. This scans the stores and records each pair in the content-addressed
TM (translation_memory.TM), so an identical German gloss that recurs — a root's sense
reappearing in a derived noun, a shared cross-reference block — is REUSED next time
instead of being re-translated. It also reports how much exact-duplicate source there
is (the concrete reuse headroom).

Key scoping is by the active translation prompt (prompt_sha), so a prompt change starts
a fresh TM generation rather than reusing translations the new prompt would change.

  python src/pilot/tm_build.py en          # harvest EN stores -> src/pilot/tm/tm.en.jsonl
  python src/pilot/tm_build.py ru           # harvest RU stores
  python src/pilot/tm_build.py en --dry     # report duplicate headroom, write nothing
"""
import glob
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot
SRC = os.path.dirname(HERE)                                # .../src
REPO = os.path.dirname(SRC)

sys.path.insert(0, HERE)
from translation_memory import TM

# The target field differs by language; the source is always `german`.
FIELD = {'en': 'english', 'ru': 'russian'}
# The translation prompt whose hash scopes the TM generation (reuse only if unchanged).
PROMPT_FILE = {'en': os.path.join(HERE, 'tr_en.txt'), 'ru': os.path.join(HERE, 'tr.txt')}


def prompt_sha(lang):
    p = PROMPT_FILE.get(lang)
    if p and os.path.exists(p):
        with open(p, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    return 'noprompt'


def iter_senses(lang):
    """Yield (german, target) for every non-null translated sense across the stores."""
    field = FIELD[lang]
    for path in sorted(glob.glob(os.path.join(REPO, 'wf_output.%s.*.json' % lang))):
        try:
            d = json.load(open(path, encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        for e in d.get('results', []):
            c = e.get('card')
            if not c:
                continue
            for rec in c.get('records', []):
                for s in rec.get('senses', []):
                    g, t = s.get('german'), s.get(field)
                    if g and t:
                        yield g, t


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}
    lang = args[0] if args else 'en'
    if lang not in FIELD:
        sys.exit('usage: tm_build.py <en|ru> [--dry]')

    psha = prompt_sha(lang)
    tm = TM(lang, psha)
    before = len(tm)

    total = 0
    uniq_src = set()
    dup_pairs = 0            # identical (src,target) seen more than once
    for g, t in iter_senses(lang):
        total += 1
        k = hashlib.sha256(g.encode('utf-8')).hexdigest()
        if k in uniq_src:
            dup_pairs += 1
        uniq_src.add(k)
        if '--dry' not in flags:
            tm.put(g, t)

    print('lang=%s prompt_sha=%s' % (lang, psha))
    print('senses scanned      : %d' % total)
    print('unique German sources: %d' % len(uniq_src))
    print('exact-duplicate srcs : %d  (%.1f%% reuse headroom on repeats)'
          % (dup_pairs, 100.0 * dup_pairs / total if total else 0.0))
    if '--dry' in flags:
        print('(dry run — TM not written)')
        return
    tm.save()
    print('TM %s: %d -> %d entries  (+%d)  %s'
          % (os.path.basename(tm.path), before, len(tm), len(tm) - before, tm.path))


if __name__ == '__main__':
    main()
