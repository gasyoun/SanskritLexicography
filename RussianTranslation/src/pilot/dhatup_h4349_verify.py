# -*- coding: utf-8 -*-
"""H4349 independent verification.

Re-derives every published number straight from the shipped JSON and the raw corpora,
without importing the builder — so a bug in the builder's own bookkeeping cannot make
this pass. Deliberately re-counts the denominator (PWG's cited coordinates) with a
freshly written regex rather than reusing the module's.
"""
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, SRC)
from sibling_root import sibling_root  # noqa: E402
GH = sibling_root(SRC)

ART = os.path.join(SRC, 'data', 'dhatup_palsule.json')
PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
PW = os.path.join(GH, 'csl-orig', 'v02', 'pw', 'pw.txt')

if not all(os.path.exists(x) for x in (ART, PWG, PW)):
    print('dhatup_h4349_verify: artifact or csl-orig corpus absent — skipped')
    raise SystemExit(0)

d = json.load(open(ART, encoding='utf-8'))
table, st = d['table'], d['_stats']
fails = []


def check(name, ok, detail=''):
    print('%-4s %s%s' % ('PASS' if ok else 'FAIL', name, ('  — ' + detail) if detail else ''))
    if not ok:
        fails.append(name)


# --- denominator, re-counted from the corpus with an independently written pattern ---
CITE = re.compile(r'<ls\b[^>]*>\s*DH[ĀA]TUP\.\s*(\d+)\s*,\s*(\d+)')
CONT = re.compile(r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\.\s*(\d+)\s*,\s*"[^>]*>\s*(\d+)')
DOT = re.compile(r'^<L>\d+\.[\d.]*<pc>')
INT = re.compile(r'^<L>\d+<pc>')

cited = set()
dotted_articles = 0
with open(PWG, encoding='utf-8') as f:
    for line in f:
        if line.startswith('<L>'):
            if DOT.match(line):
                dotted_articles += 1
            continue
        for rx in (CITE, CONT):
            for m in rx.finditer(line):
                cited.add('%s,%s' % (m.group(1), m.group(2)))

check('denominator: PWG cites %d gaṇa,serial coordinates' % len(cited),
      len(cited) == st['coords_cited'] == 1751, '_stats says %d' % st['coords_cited'])
check('PWG dotted-id article count', dotted_articles == 636 == st['pwg-dotted_articles'],
      're-counted %d' % dotted_articles)

# --- coverage, re-derived from the table ------------------------------------------
counts = {}
for r in table.values():
    counts[r['source']] = counts.get(r['source'], 0) + 1
check('coverage 1465 = 1226 pwg + 140 mw + 99 mw-respell + 0 pw + 0 pwg-dotted',
      len(table) == 1465 and counts == {'pwg': 1226, 'mw': 140, 'mw-respell': 99},
      repr(counts))
# THE INVARIANT THIS FILE ORIGINALLY MISSED, and the reason an independent verifier
# refuted the first cut. `ceil` below is derived from `cited`, so testing only
# `serial <= ceil[gana]` cannot notice a coordinate that is absent from `cited`
# altogether: `33,67` cleared gaṇa 33's ceiling of 130 and PWG never cites it at all.
# `match_rate` divides by `cited`, so a row outside it was counted against a
# denominator that excluded it. Assert membership directly.
check('every shipped coordinate is one PWG actually cites',
      set(table) <= cited, repr(sorted(set(table) - cited)[:5]))
check('match_rate is the ratio it claims to be',
      round(100.0 * len(table) / len(cited), 1) == st['match_rate'] == 83.7,
      '%s%%' % st['match_rate'])
check('H1333 rate still 70.0%% off the same denominator',
      round(100.0 * counts['pwg'] / len(cited), 1) == st['match_rate_pwg'] == 70.0)

# --- every shipped row is in the attested space -----------------------------------
ceil = {}
for c in cited:
    g, s = (int(x) for x in c.split(','))
    ceil[g] = max(ceil.get(g, 0), s)
bad = [c for c in table if (lambda g, s: s > ceil.get(g, 0))(*(int(x) for x in c.split(',')))]
check('no shipped row lies outside the attested coordinate space', not bad, repr(bad[:5]))
check('gaṇa 1 ceiling is 1, which is what refuses 1,840 and 1,960',
      ceil[1] == 1, 'ceiling %d' % ceil[1])
refused = {x['coord'] for x in d['_out_of_coordinate_space']}
check('both artifacts refused and published', refused == {'1,840', '1,960'}, repr(sorted(refused)))
check('neither refused coordinate is in the table', not (refused & set(table)))

# --- the two rows the first cut shipped, and why neither may come back -------------
# Both were refuted by an independent verifier. They are pinned as ABSENT, with the
# source evidence that condemns each, so a future loosening of the screens fails here.
for coord in ('32,56', '33,67'):
    check('%s is not shipped' % coord, coord not in table,
          repr(table.get(coord, {}).get('root_slp1')))
src = open(PWG, encoding='utf-8').read().splitlines()
ev = {
    # PWG splits 32,56 between `cakk` and a `v. l.` `cikk`, and puts `cukk` at 34,21.
    '32,56': ('cakk', 'cikk'),
    # PWG never cites 33,67; the identical `2. tras` article is its 33,88.
    '33,88': ('tras',),
}
for coord, roots in ev.items():
    lines = [l for l in src if 'DHĀTUP. %s<' % coord in l]
    for root in roots:
        check('PWG evidence: %s is cited in a %s article' % (coord, root),
              any('{#%s#}' % root in l for l in lines),
              '%d citing lines' % len(lines))
check('PWG never cites 33,67', '33,67' not in cited)
check('pw uses the Böhtlingk v. l. construction at a DHĀTUP citation, so the guard '
      'is not hypothetical',
      any('DHĀTUP. 31,32<' in l and 'v. l.' in l
          for l in open(PW, encoding='utf-8').read().splitlines()))

print()
print('coverage %d/%d = %s%%  ·  per-source %s'
      % (len(table), len(cited), st['match_rate'], counts))
print('H4349 sibling yield: pw %d, pwg-dotted %d — both classes measured and empty'
      % (st['coords_filled_from_pw'], st['coords_filled_from_pwg-dotted']))
raise SystemExit(1 if fails else 0)
