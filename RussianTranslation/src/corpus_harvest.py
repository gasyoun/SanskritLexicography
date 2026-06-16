#!/usr/bin/env python
"""Harvest reader — corpus_lexicon.jsonl → attested Russian senses per headword.

Turns the raw word-alignment rows into the reuse signal the pwg_ru harvest
consumes: given a Sanskrit headword (SLP1 key) it returns the Russian renderings
ACTUALLY ATTESTED in the parallel corpus, grouped by stratum (period/genre),
counted, and split translation-vs-commentary. When the PWG sense's <ls> citation
is known, ls_source_map.json resolves it to a stratum so that stratum's
renderings surface first (a Ṛgvedic citation → the Vedic Russian).

  python corpus_harvest.py top [N]            most-attested keys
  python corpus_harvest.py <slp1> [LS_KEY]    attested Russian for a headword
"""
import json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, 'corpus_lexicon.jsonl')
LSMAP = os.path.join(HERE, 'ls_source_map.json')
LS_SOURCES = json.load(open(LSMAP, encoding='utf-8')) if os.path.exists(LSMAP) else {}

# period ordering oldest→newest for stable stratum sort
PERIOD_ORDER = {'Ṛgvedic': 0, 'Vedic (Brāhmaṇa–Upaniṣad)': 1,
                'Epic / early-Classical': 2, 'Classical': 3, 'Medieval': 4}


def index():
    idx = collections.defaultdict(list)
    if os.path.exists(LEX):
        for line in open(LEX, encoding='utf-8'):
            try:
                r = json.loads(line)
            except Exception:
                continue
            idx[r['slp1']].append(r)
    return idx


def harvest(rows, prefer_period=None):
    """rows for one slp1 key → strata, each with counted Russian renderings."""
    by_stratum = collections.defaultdict(lambda: collections.defaultdict(
        lambda: {'n': 0, 'kinds': set(), 'works': set()}))
    for r in rows:
        key = (r.get('period') or '?', r.get('genre') or '?')
        ru = (r.get('ru') or '').strip()
        cell = by_stratum[key][ru]
        cell['n'] += 1
        cell['kinds'].add(r.get('kind'))
        cell['works'].add(r.get('work'))
    out = []
    for (period, genre), rends in by_stratum.items():
        renderings = sorted(
            ({'ru': ru, 'count': c['n'], 'kinds': sorted(c['kinds']),
              'works': len(c['works'])} for ru, c in rends.items()),
            key=lambda x: -x['count'])
        out.append({'period': period, 'genre': genre,
                    'total': sum(r['count'] for r in renderings),
                    'renderings': renderings})
    out.sort(key=lambda s: (s['period'] != prefer_period,
                            PERIOD_ORDER.get(s['period'], 9)))
    return out


def resolve_period(ls_key):
    rec = LS_SOURCES.get(ls_key)
    return rec.get('period') if rec else None


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    idx = index()
    if sys.argv[1] == 'top':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        rank = sorted(((k, len(v)) for k, v in idx.items()), key=lambda x: -x[1])
        print('%d distinct SLP1 keys; top %d by attestation count:' % (len(idx), n))
        for k, c in rank[:n]:
            print('  %-18s %5d' % (k, c))
        return
    slp1 = sys.argv[1]
    ls_key = sys.argv[2] if len(sys.argv) > 2 else None
    pref = resolve_period(ls_key)
    rows = idx.get(slp1, [])
    if not rows:
        print('no corpus attestation for key %r' % slp1); return
    print('=== %s : %d attestations across the corpus%s ==='
          % (slp1, len(rows), (' | <ls>=%s → prefer %s' % (ls_key, pref)) if ls_key else ''))
    for s in harvest(rows, pref):
        star = ' ◀ cited stratum' if s['period'] == pref else ''
        print('· %s · %s (%d)%s' % (s['period'], s['genre'], s['total'], star))
        for r in s['renderings'][:8]:
            tag = '+comm' if 'commentary' in r['kinds'] else ''
            print('     %4d  %s  %s' % (r['count'], r['ru'], tag))


if __name__ == '__main__':
    main()
