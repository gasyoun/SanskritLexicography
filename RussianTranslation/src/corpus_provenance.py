#!/usr/bin/env python
"""Trace a Russian meaning back to the exact corpus text it comes from.

The portrait's corpus_synonyms (the Russian candidates the translator leans on)
are mined from corpus_lexicon.jsonl — a word-aligned Sanskrit→Russian corpus. Each
aligned pair there carries FULL provenance: `work` (source text), `passage` (verse),
`period`/`date` (stratum). The portrait keeps only the bare Russian word, dropping
that link. This tool restores it: given a Sanskrit form (or root, or a Russian word),
it shows every Russian rendering and the exact text:passage(s) attesting it — so an
editor can see WHY a given Russian gloss is there before changing it.

  python src/corpus_provenance.py <slp1form>          exact SLP1 form (e.g. gamemahi)
  python src/corpus_provenance.py --root gam          all SLP1 forms containing 'gam'
  python src/corpus_provenance.py --ru соединимся      reverse: which forms/texts gave it
  python src/corpus_provenance.py <form> --limit 8     cap attestations shown per rendering
"""
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

LEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus_lexicon.jsonl')


def scan(match):
    """Yield records where match(record) is True."""
    with open(LEX, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if match(r):
                yield r


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    limit = 6
    if '--limit' in args:
        i = args.index('--limit'); limit = int(args[i + 1]); del args[i:i + 2]

    if args[0] == '--root':
        needle = args[1]
        match = lambda r: needle in (r.get('slp1') or '')
        title = "SLP1 forms containing %r" % needle
        group_key = lambda r: (r.get('slp1'), r.get('ru'))
    elif args[0] == '--ru':
        needle = args[1]
        match = lambda r: needle.lower() in (r.get('ru') or '').lower()
        title = "Russian renderings matching %r" % needle
        group_key = lambda r: (r.get('ru'), r.get('slp1'))
    else:
        form = args[0]
        match = lambda r: (r.get('slp1') or '') == form
        title = "SLP1 form %r" % form
        group_key = lambda r: (r.get('slp1'), r.get('ru'))

    groups = defaultdict(list)
    for r in scan(match):
        groups[group_key(r)].append(r)

    if not groups:
        print('no corpus attestations found.'); return

    print('=== provenance: %s ===' % title)
    print('(each rendering -> count, period span, and the texts:passages attesting it)\n')
    for key in sorted(groups, key=lambda k: -len(groups[k])):
        recs = groups[key]
        works = sorted({'%s:%s' % (x.get('work'), x.get('passage')) for x in recs})
        periods = sorted({x.get('period') for x in recs if x.get('period')})
        a, b = key
        print('%-22s -> %-26s  (n=%d)' % (a, b, len(recs)))
        print('    period(s): %s' % '; '.join(periods))
        shown = works[:limit]
        print('    source(s): %s%s' % (', '.join(shown),
              '  …+%d more' % (len(works) - limit) if len(works) > limit else ''))
        print()


if __name__ == '__main__':
    main()
