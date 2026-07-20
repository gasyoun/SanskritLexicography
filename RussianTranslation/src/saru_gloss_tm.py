#!/usr/bin/env python
r"""saru_gloss_tm.py — read-only Sa->Ru gloss lookup layer for the pwg_ru/mw_ru
translation-memory path (H1349 wave 4, downstream).

Exposes the aggregated lemma + root gloss layers (built by
build_rollup_glossaries.py) as a lookup: given a Sanskrit lemma or root (SLP1),
return ranked candidate Russian renderings. The pwg_ru / mw_ru card path can
consult this as a TM *suggestion* source when translating a headword.

**Read-only, additive, no coordinator touch.** This is a consumer of the committed
glossary artifacts; it does NOT read or write the harness TM
(`pilot/translation_memory.py`), the store, or anything the safety-plan PRs
#547/#550 touch (the wave-4 risk fence). It opens no network and mutates nothing.

  from saru_gloss_tm import GlossTM
  tm = GlossTM.from_glossary_dir('glossary')          # or point at the SanskritRussian clone
  hit = tm.lookup('gam')                               # {'key','layer','candidates':[{'ru','n'}]}

  python saru_gloss_tm.py <lemma-or-root> [--glossary-dir DIR]
  python saru_gloss_tm.py --selftest
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

_ava = re.compile(r"^['’‘]+")


def _norm(k):
    return _ava.sub('', k or '')


def _load(path, key_field):
    """{key: [(ru, n), ...] ranked} from a *_glossary.jsonl, or {} if absent."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cands = [(t['ru'], t['n']) for t in (r.get('translations') or [])]
            out[_norm(r[key_field])] = cands
    return out


class GlossTM:
    """Read-only lemma+root gloss lookup."""

    def __init__(self, lemma_path=None, root_path=None):
        self.lemma = _load(lemma_path, 'lemma_slp1')
        self.root = _load(root_path, 'root_slp1')

    @classmethod
    def from_glossary_dir(cls, d):
        return cls(os.path.join(d, 'lemma_glossary.jsonl'),
                   os.path.join(d, 'root_glossary.jsonl'))

    def lookup(self, key, prefer='lemma', top=None):
        """Return {'key', 'layer', 'candidates':[{'ru','n'}]} for a lemma/root key.

        `prefer` picks which layer wins when both carry the key ('lemma' is more
        specific, 'root' aggregates over a whole verb family). Falls back to the
        other layer. layer is None when the key is unknown to both.
        """
        k = _norm(key)
        order = ('lemma', 'root') if prefer == 'lemma' else ('root', 'lemma')
        for layer in order:
            cands = getattr(self, layer).get(k)
            if cands:
                ranked = sorted(cands, key=lambda c: -c[1])
                if top:
                    ranked = ranked[:top]
                return {'key': k, 'layer': layer,
                        'candidates': [{'ru': ru, 'n': n} for ru, n in ranked]}
        return {'key': k, 'layer': None, 'candidates': []}

    def __len__(self):
        return len(self.lemma) + len(self.root)


HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, 'fixtures')


def selftest():
    tm = GlossTM(os.path.join(FIX, 'saru_gloss_lemma.fixture.jsonl'),
                 os.path.join(FIX, 'saru_gloss_root.fixture.jsonl'))
    # known lemma resolves, ranked
    hit = tm.lookup('gam')
    assert hit['layer'] == 'lemma', hit
    assert hit['candidates'][0]['ru'] == 'идти', hit          # highest-n first
    assert [c['ru'] for c in hit['candidates']] == ['идти', 'пришёл'], hit
    # prefer=root reaches the root layer's aggregate
    rhit = tm.lookup('gam', prefer='root')
    assert rhit['layer'] == 'root' and rhit['candidates'][0]['ru'] == 'пришел', rhit
    # avagraha normalized on the query
    assert tm.lookup("'gam")['layer'] == 'lemma'
    # root-only key falls back
    assert tm.lookup('BU')['layer'] == 'root'
    # unknown key -> empty, no raise
    assert tm.lookup('zzznotalemma') == {'key': 'zzznotalemma', 'layer': None, 'candidates': []}
    # top-k
    assert len(tm.lookup('gam', top=1)['candidates']) == 1
    print('saru_gloss_tm selftest OK')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('key', nargs='?', help='lemma or root (SLP1) to look up')
    ap.add_argument('--glossary-dir', default=os.path.join(HERE, '..', 'glossary'))
    ap.add_argument('--prefer', choices=('lemma', 'root'), default='lemma')
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    if not args.key:
        ap.error('a key is required (or use --selftest)')
    tm = GlossTM.from_glossary_dir(args.glossary_dir)
    hit = tm.lookup(args.key, prefer=args.prefer, top=args.top)
    print(json.dumps(hit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
