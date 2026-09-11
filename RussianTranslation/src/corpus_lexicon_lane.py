#!/usr/bin/env python
"""corpus_lexicon_lane.py — the verse-aligned Sa-Ru corpus as a SENSE-SUPPORT lane.

H4119 P1 repair. Until now `corpus` was a NONRU presence-only lane in
`annotate_evidence.gather()`: it answered "does an aligned verse mentioning this
lemma exist?" via `corpus_gate.corpus_examples_with_status`, so it could never
support a single sense — the H4058 review measured 0 senses supported by a
1.09M-row resource whose every row already carries a Russian rendering.

But `corpus_lexicon.jsonl` (built by `build_corpus_lexicon.py`) is SLP1-keyed
Sanskrit -> Russian word alignment: `{"slp1": ..., "ru": ..., "work", "passage",
"kind": "ru"}`. That IS a Russian-glossing authority in exactly the shape the
other RU lanes take, so it belongs in the token-comparable set, not the
presence-only one.

What this module deliberately does NOT do:

* it does not emit `provides`. A corpus rendering is one translator's choice
  inside one verse, not a lexicographic equivalent statement, so the strongest
  relation it can assert is `supports` — the downgrade happens here, once,
  rather than at each call site.
* it never emits `contradicts`. A corpus that renders a lemma differently in one
  verse says nothing against a printed sense of the lemma: the lane is
  ASYMMETRIC by design, and its silence is uninformative.

Classification vocabulary used by the probe (denominators always reported):

  matched     the lane has >=1 Russian rendering for this key1 AND it reaches
              `annotate_evidence.best_relation` at/above corpus_gate.THRESHOLD
  missed      the lane has renderings for this key1 but none reaches threshold
  ambiguous   the lane has renderings but the SENSE asserts no comparable Russian
              meaning (a bare cross-ref / citation sense) — unjudgeable, and never
              silently counted as a miss
  no_lane     the lane holds no rendering for this key1 at all

  python corpus_lexicon_lane.py --selftest
"""
import argparse
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import annotate_evidence as ae                                    # noqa: E402

LEXICON = os.path.join(HERE, 'corpus_lexicon.jsonl')
FIXTURE = os.path.join(HERE, 'fixtures', 'corpus_lexicon.fixture.jsonl')
FIXTURE_KINDS = os.path.join(HERE, 'fixtures', 'corpus_lexicon_kinds.fixture.jsonl')

SOURCE_CODE = 'corpus_lex'
# `kind` values that carry a Russian rendering. The live lexicon writes
# 'translation' (992,265 rows) and 'commentary' (101,126 rows); the committed
# fixture predates that split and writes 'ru'. A row of any OTHER kind is not a
# Russian rendering and is excluded — never defaulted in, because a silently
# widened filter is how a lane starts asserting support it does not have.
RU_KINDS = frozenset(('translation', 'commentary', 'ru'))
# The lane can assert at most `supports` — see the module docstring.
MAX_RELATION = 'supports'
# Per-lemma cap on distinct renderings kept: a common lemma has thousands of verse
# rows and `best_relation` is O(len(glosses)); the cap keeps the probe bounded and
# is recorded in the receipt so the number is never mistaken for the full lane.
MAX_GLOSSES_PER_KEY = 40


def lexicon_path(path=None):
    """Resolve the gitignored lexicon the same way the store is resolved."""
    if path:
        return path
    env = os.environ.get('PWG_RU_CORPUS_LEXICON')
    if env:
        return env
    try:
        import store_path
        return store_path.canonical_store(
            LEXICON, store_rel='RussianTranslation/src/corpus_lexicon.jsonl')
    except Exception:
        return LEXICON


def load_lane(path=None, keys=None, max_glosses=MAX_GLOSSES_PER_KEY):
    """Stream the lexicon into {slp1: [ru rendering, ...]}.

    `keys` (a set of key1) bounds memory: only those lemmas are retained, which is
    what any store-scoped probe wants — the file is ~290 MB / ~1.09M rows.
    Returns (lane, stats) where stats carries the denominators: rows read, rows
    usable (kind == 'ru' with both slp1 and ru), and distinct keys retained.
    """
    p = lexicon_path(path)
    lane = defaultdict(list)
    seen = defaultdict(set)
    stats = {'lexicon_path': p, 'lexicon_present': os.path.exists(p),
             'rows_read': 0, 'rows_usable': 0, 'rows_kept': 0, 'keys_kept': 0,
             'max_glosses_per_key': max_glosses,
             'ru_kinds': sorted(RU_KINDS), 'kinds_seen': {}}
    kinds = defaultdict(int)
    if not stats['lexicon_present']:
        return {}, stats
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            stats['rows_read'] += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = rec.get('kind') or 'ru'
            kinds[kind] += 1
            if kind not in RU_KINDS:
                continue
            k, ru = rec.get('slp1'), (rec.get('ru') or '').strip()
            if not k or not ru:
                continue
            stats['rows_usable'] += 1
            if keys is not None and k not in keys:
                continue
            if len(lane[k]) >= max_glosses or ru in seen[k]:
                continue
            seen[k].add(ru)
            lane[k].append(ru)
            stats['rows_kept'] += 1
    stats['keys_kept'] = len(lane)
    stats['kinds_seen'] = dict(sorted(kinds.items()))
    return dict(lane), stats


def classify(sense_ru, glosses):
    """(class, relation, gloss_ref) for one sense against this lane's renderings.

    class is one of matched / missed / ambiguous / no_lane; relation is
    'supports' or None — `provides` is deliberately unreachable here."""
    if not glosses:
        return 'no_lane', None, ''
    if not ae.ru_tokens_full(sense_ru):
        return 'ambiguous', None, ''
    rel, ref = ae.best_relation(sense_ru, glosses)
    if rel is None:
        return 'missed', None, ''
    return 'matched', MAX_RELATION, ref


def evidence_record(sense_ru, glosses):
    """The `row['evidence']` entry this lane contributes, or None."""
    cls, rel, ref = classify(sense_ru, glosses)
    if cls != 'matched':
        return None
    return {'source': SOURCE_CODE, 'relation': rel, 'gloss_ref': ref,
            'match': 'lemma', 'lane': 'corpus_lexicon'}


def selftest():
    lane, stats = load_lane(FIXTURE)
    assert stats['lexicon_present'], FIXTURE
    assert stats['rows_usable'] == 5, stats
    assert stats['kinds_seen'] == {'ru': 5}, stats
    assert lane['karman'] == ['действие'], lane.get('karman')
    # a non-Russian `kind` is counted in the census but contributes no gloss
    lane_k, st_k = load_lane(FIXTURE_KINDS)
    assert st_k['kinds_seen'] == {'en': 1, 'translation': 1}, st_k
    assert st_k['rows_usable'] == 1 and set(lane_k) == {'agni'}, (st_k, lane_k)

    # matched: the sense's Russian is contained in the corpus rendering
    cls, rel, ref = classify('действие', lane['karman'])
    assert (cls, rel) == ('matched', 'supports'), (cls, rel, ref)
    # a corpus rendering NEVER escalates to `provides`, even on an exact equivalent
    assert rel != 'provides', rel
    # missed: renderings exist, none reaches threshold
    cls, rel, _ = classify('огонь, пламя', lane['karman'])
    assert (cls, rel) == ('missed', None), (cls, rel)
    # ambiguous: a bare citation sense asserts no comparable Russian meaning
    cls, _, _ = classify('<ls>M. 2,109.</ls> {#mAturAptAMSca#}', lane['karman'])
    assert cls == 'ambiguous', cls
    # no_lane: lemma absent from the lexicon
    cls, _, _ = classify('огонь', lane.get('agni') or [])
    assert cls == 'no_lane', cls
    # key-bounded load keeps only the requested lemmas
    lane2, st2 = load_lane(FIXTURE, keys={'yoga'})
    assert set(lane2) == {'yoga'} and st2['rows_read'] == 5, (lane2, st2)
    # evidence_record shape
    er = evidence_record('действие', lane['karman'])
    assert er['source'] == SOURCE_CODE and er['relation'] == 'supports', er
    assert evidence_record('огонь, пламя', lane['karman']) is None
    print('corpus_lexicon_lane selftest OK')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--lexicon')
    ap.add_argument('--key', help='print the lane renderings for one key1')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.key:
        lane, stats = load_lane(a.lexicon, keys={a.key})
        print(json.dumps({'stats': stats, 'glosses': lane.get(a.key, [])},
                         ensure_ascii=False, indent=2))
        return 0
    ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
