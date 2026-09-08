# -*- coding: utf-8 -*-
"""H4349 independent verification.

Re-derives every published number straight from the shipped JSON and the raw corpora,
without importing the builder — so a bug in the builder's own bookkeeping cannot make
this pass. Deliberately re-counts the denominator (PWG's cited coordinates) with a
freshly written regex rather than reusing the module's.
"""
import ast
import hashlib
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

# Fail CLOSED. Exiting 0 on a missing corpus gives any caller without csl-orig a
# green run that executed zero checks — a second verifier scored exactly that on a
# /tmp worktree. `--skip-if-absent` restores the old behaviour for callers that
# genuinely cannot supply the corpora and say so out loud.
_missing = [x for x in (ART, PWG, PW) if not os.path.exists(x)]
if _missing:
    print('dhatup_h4349_verify: cannot verify — absent: %s' % ', '.join(_missing))
    raise SystemExit(0 if '--skip-if-absent' in sys.argv else 2)

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
# NB: this asserts the CONSTRUCTION exists in pw, NOT that the guard fires on it.
# The guard is order-shadowed by the same-book screen and refuses 0 as shipped.
check('pw contains the Böhtlingk v. l. construction at a DHĀTUP citation (the guard '
      'is standing, not live — it refuses 0 today)',
      any('DHĀTUP. 31,32<' in l and 'v. l.' in l
          for l in open(PW, encoding='utf-8').read().splitlines()))

# --- H4386: the artifact is pinned to the builder that wrote it -------------------
# Re-derived here as well as in ls_enrichment_selftest.py, because the two harnesses
# fail for different callers: the selftest runs corpus-free in CI, this one runs where
# the corpora are and is the file a reviewer runs by hand.
BUILDER = os.path.join(SRC, 'build_dhatup_palsule.py')
_digest = hashlib.sha256(open(BUILDER, 'rb').read()).hexdigest()
check('artifact is stamped with the sha256 of the builder that wrote it',
      st.get('builder_sha256') == _digest,
      'stamped %s… committed %s…' % (str(st.get('builder_sha256'))[:12], _digest[:12]))

# --- H4386: the two sibling screens are mandatory, read off the builder's source ---
# This file's whole premise is that a bug in the builder's own bookkeeping must not be
# able to make it pass, and that applies to the builder's SIGNATURE as much as to its
# counts — a screen that silently defaults is a bookkeeping bug with a wider blast
# radius than a miscount.
# Parsed with `ast`, not grepped: the builder DOCUMENTS the permissive shapes it used
# to have, at length and deliberately, so a substring search cannot tell the warning
# from the thing it warns about — it would force the code to stay undocumented to stay
# green. `ast` sees the syntax tree, and still never imports or executes the builder.
_tree = ast.parse(open(BUILDER, encoding='utf-8').read())
_fn = next((n for n in ast.walk(_tree)
            if isinstance(n, ast.FunctionDef) and n.name == '_sibling_pass'), None)
check('_sibling_pass exists to be checked', _fn is not None)
if _fn is not None:
    _kwonly = [a.arg for a in _fn.args.kwonlyargs]
    _defaults = {a.arg: d for a, d in zip(_fn.args.kwonlyargs, _fn.args.kw_defaults)}
    _positional = [a.arg for a in _fn.args.args]
    check('both screens are keyword-only',
          {'same_book_conflicted', 'pwg_cited'} <= set(_kwonly),
          'kwonly=%r positional=%r' % (_kwonly, _positional))
    check('neither screen has a default — omitting one is a TypeError, not an '
          'unscreened pass',
          all(_defaults.get(k) is None for k in ('same_book_conflicted', 'pwg_cited')),
          repr({k: ast.dump(v) for k, v in _defaults.items() if v is not None}))
    # The membership screen must be a plain `coord not in pwg_cited`, never
    # `pwg_cited and coord not in pwg_cited` — that conjunction is what made an empty
    # set mean "screen off" instead of "screen against nothing".
    _guarded = [n for n in ast.walk(_fn)
                if isinstance(n, ast.If) and isinstance(n.test, ast.BoolOp)
                and any(isinstance(v, ast.Name) and v.id == 'pwg_cited'
                        for v in n.test.values)]
    check('the membership screen is unconditional, not `if pwg_cited and …`',
          not _guarded, '%d conjunction-guarded screens' % len(_guarded))
    # And the empty set — the old default, now reachable only by passing it — is
    # refused at entry rather than honoured as a screen.
    _raises = [n for n in ast.walk(_fn)
               if isinstance(n, ast.If) and isinstance(n.test, ast.UnaryOp)
               and isinstance(n.test.op, ast.Not)
               and isinstance(n.test.operand, ast.Name)
               and n.test.operand.id == 'pwg_cited'
               and any(isinstance(b, ast.Raise) for b in n.body)]
    check('an empty pwg_cited raises instead of admitting every coordinate',
          bool(_raises))

# --- H4386: pw's published refusal split is a partition of its 40 citations --------
# The six terms ABBREVIATIONS_RU.md publishes, plus the two empty buckets, must add to
# the coordinate count re-counted from pw.txt with the pattern written at the top of
# this file — so the doc cannot drift from _stats, and _stats cannot drift from pw.
pw_cited = set()
with open(PW, encoding='utf-8') as f:
    for line in f:
        for rx in (CITE, CONT):
            for m in rx.finditer(line):
                pw_cited.add('%s,%s' % (m.group(1), m.group(2)))
check('pw cites %d coordinates, re-counted from the corpus' % len(pw_cited),
      len(pw_cited) == st['pw_coords_cited'] == 40,
      '_stats says %d' % st['pw_coords_cited'])
_split = {'pw_refused_nominal_head': 12, 'pw_refused_body_only': 4,
          'pw_refused_same_book_conflict': 11, 'pw_refused_not_cited_by_pwg': 3,
          'pw_refused_out_of_coordinate_space': 2,
          'pw_coords_single_verbal_claimant': 8}
check('all six published pw refusal terms hold',
      all(st.get(k) == v for k, v in _split.items()),
      repr({k: st.get(k) for k, v in _split.items() if st.get(k) != v}))
_buckets = sum(st.get(k, 0) for k in list(_split)
               + ['pw_refused_multiple_claimants', 'pw_refused_variant_reading'])
check('the screen chain partitions all 40 citations', _buckets == len(pw_cited),
      'buckets sum to %d' % _buckets)
check('the published sum is the header it is printed under',
      sum(_split.values()) == 40)

print()
print('coverage %d/%d = %s%%  ·  per-source %s'
      % (len(table), len(cited), st['match_rate'], counts))
print('H4349 sibling yield: pw %d, pwg-dotted %d — both classes measured and empty'
      % (st['coords_filled_from_pw'], st['coords_filled_from_pwg-dotted']))
raise SystemExit(1 if fails else 0)
