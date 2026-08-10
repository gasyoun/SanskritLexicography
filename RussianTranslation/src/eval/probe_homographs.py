#!/usr/bin/env python
"""probe_homographs.py — how many Kochergina SLP1 keys carry multiple entries?

check_gold_frame.py flagged 6 duplicate lemmas in the H2401 frame. The cause
matters for the protocol: if one SLP1 key has several Kochergina entries (`vas` I
"dwell" vs `vas` II "wear"), then

  * the sampler can draw the same key more than once (a duplicate row), and
  * more importantly, "the gold Russian gloss for `vas`" is ill-posed -- the
    annotator would be asked to gloss a key that names two different words.

`corpus_lexicon.jsonl` is keyed by surface SLP1 with no homograph index, so the
BLI task genuinely cannot distinguish them: the protocol must therefore say what
it does with homographs (pool the senses, or exclude the key), and that ruling
needs this count behind it.

Read-only diagnostic.

Usage: python probe_homographs.py --koch <koch.jsonl> [--show 15]
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_gold_strata import gloss_text, lemma_key  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--koch', required=True)
    ap.add_argument('--show', type=int, default=15)
    args = ap.parse_args()

    by_key = collections.defaultdict(list)
    total = 0
    with open(args.koch, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            k = lemma_key(rec)
            if not k or k.startswith('-'):
                continue
            total += 1
            by_key[k].append(gloss_text(rec))

    multi = {k: v for k, v in by_key.items() if len(v) > 1}
    dist = collections.Counter(len(v) for v in by_key.values())
    print(f'standalone entries      : {total}')
    print(f'distinct SLP1 keys      : {len(by_key)}')
    print(f'keys with >1 entry      : {len(multi)} '
          f'({len(multi) / len(by_key):.2%} of keys)')
    print(f'entries inside them     : {sum(len(v) for v in multi.values())}')
    print(f'entries-per-key distribution: {dict(sorted(dist.items()))}')

    print(f'\n--- {args.show} widest homograph keys ---')
    for k, v in sorted(multi.items(), key=lambda kv: -len(kv[1]))[:args.show]:
        print(f'{k} ({len(v)} entries)')
        for g in v[:2]:
            print('   ', ' '.join(g.split())[:110])
    return 0


if __name__ == '__main__':
    sys.exit(main())
