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
check('coverage 1467 = 1226 pwg + 140 mw + 99 mw-respell + 2 pw + 0 pwg-dotted',
      len(table) == 1467 and counts == {'pwg': 1226, 'mw': 140, 'mw-respell': 99, 'pw': 2},
      repr(counts))
check('match_rate is the ratio it claims to be',
      round(100.0 * len(table) / len(cited), 1) == st['match_rate'] == 83.8,
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

# --- the two pw rows are what the source actually says ----------------------------
want = {'32,56': 'cukk', '33,67': 'tras'}
for coord, root in want.items():
    row = table.get(coord)
    ok = row and row['source'] == 'pw' and row['root_slp1'] == root and row['arthas']
    check('pw row %s is √%s with Palsule arthas' % (coord, root), bool(ok),
          repr((row or {}).get('root_slp1')))
src = open(PW, encoding='utf-8').read()
for coord, root in want.items():
    line = [l for l in src.splitlines() if 'DHĀTUP. %s<' % coord in l]
    ok = line and ('√{#%s#}' % root) in line[0]
    check('pw states %s on a √-marked %s head line' % (coord, root), bool(ok),
          (line[0][:70] if line else 'no line'))

print()
print('coverage %d/%d = %s%%  ·  per-source %s'
      % (len(table), len(cited), st['match_rate'], counts))
raise SystemExit(1 if fails else 0)
