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
# H4438. The third form. `n="DHĀTUP."` carries the source in an ATTRIBUTE and the whole
# coordinate in the body. It is a real citation — 320 occurrences, 281 of them on the
# citing article's own head line — and the reader was blind to every one of them. It is
# kept in its own pattern here, not folded into CITE, because the ceiling screen below
# depends on knowing which coordinates the visible text spells out and which only an
# attribute attributes.
FULL = re.compile(r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\."[^>]*>\s*(\d+)\s*,\s*(\d+)')
DOT = re.compile(r'^<L>\d+\.[\d.]*<pc>')
INT = re.compile(r'^<L>\d+<pc>')

cited = set()
spelled_out = set()
dotted_articles = 0
with open(PWG, encoding='utf-8') as f:
    for line in f:
        if line.startswith('<L>'):
            if DOT.match(line):
                dotted_articles += 1
            continue
        for rx in (CITE, CONT, FULL):
            for m in rx.finditer(line):
                coord = '%s,%s' % (m.group(1), m.group(2))
                cited.add(coord)
                if rx is not FULL:
                    spelled_out.add(coord)

# The denominator is what PWG cites MINUS what the ceiling screen refused, so this one
# check re-derives both halves: a refusal the builder invented would show up as surplus
# here, and a refusal it forgot would show up as deficit.
refused_c = {r['coord'] for r in d.get('_refused_form_c_out_of_space', [])}
check('denominator: PWG cites %d coordinates, %d refused out of space'
      % (len(cited), len(refused_c)),
      len(cited) == 1892 and len(cited) - len(refused_c) == st['coords_cited'] == 1890,
      '_stats says %d' % st['coords_cited'])
check('the citation forms that spell the gaṇa out attest 1751 of them',
      len(spelled_out) == 1751, 're-counted %d' % len(spelled_out))
check('PWG dotted-id article count', dotted_articles == 636 == st['pwg-dotted_articles'],
      're-counted %d' % dotted_articles)

# --- coverage, re-derived from the table ------------------------------------------
counts = {}
for r in table.values():
    counts[r['source']] = counts.get(r['source'], 0) + 1
check('coverage 1573 = 1302 pwg + 178 mw + 93 mw-respell + 0 pw + 0 pwg-dotted',
      len(table) == 1573 and counts == {'pwg': 1302, 'mw': 178, 'mw-respell': 93},
      repr(counts))
# THE INVARIANT THIS FILE ORIGINALLY MISSED, and the reason an independent verifier
# refuted the first cut. `ceil` below is derived from `cited`, so testing only
# `serial <= ceil[gana]` cannot notice a coordinate that is absent from `cited`
# altogether: `33,67` cleared gaṇa 33's ceiling of 130 and PWG never cites it at all.
# `match_rate` divides by `cited`, so a row outside it was counted against a
# denominator that excluded it. Assert membership directly.
check('every shipped coordinate is one PWG actually cites',
      set(table) <= cited, repr(sorted(set(table) - cited)[:5]))
# H4438 RETIRED 83.7%. It was 1465/1751 against a denominator two of PWG's three
# citation forms could reach; 83.2% is 1573/1890 against all three. The two are not
# comparable and the smaller number is the better table — agreement with MW rose from
# 77.7% to 80.1% across the same change. Quoting 83.7% again is a regression claim
# about a coverage improvement.
check('match_rate is the ratio it claims to be',
      round(100.0 * len(table) / (len(cited) - len(refused_c)), 1)
      == st['match_rate'] == 83.2, '%s%%' % st['match_rate'])
check('H1333 rate is 68.9%% off the same denominator',
      round(100.0 * counts['pwg'] / (len(cited) - len(refused_c)), 1)
      == st['match_rate_pwg'] == 68.9, '%s%%' % st['match_rate_pwg'])

# --- every shipped row is in the attested space -----------------------------------
# H4438. The ceiling is built from `spelled_out`, NOT from `cited`. A form-C citation
# names its source in an attribute, and an attribute is inheritable: PWG's
# `<ls n="DHĀTUP.">27,71</ls>` is MW's `xxvi, 71` — the gaṇa carried forward from the
# `27,16` one clause earlier. Build the ceiling from the form that can carry a gaṇa and
# it certifies itself; gaṇa 27, attested by 32 coordinates ending at 33, would have
# acquired a ceiling of 71 and handed the sibling passes 38 serials PWG never attests.
ceil = {}
for c in spelled_out:
    g, sr = (int(x) for x in c.split(','))
    ceil[g] = max(ceil.get(g, 0), sr)
bad = [c for c in table if (lambda g, sr: sr > ceil.get(g, 0))(*(int(x) for x in c.split(',')))]
# Exactly one shipped row stands above that ceiling, and it is there because MW — a
# different author, the only witness allowed to break a Böhtlingk tie here — prints the
# identical pair: `Dhātup. xxvi, 127; <ls n="Dhātup.">xxxii, 133</ls>` for stūp. It is
# the last root of a gaṇa 108 coordinates attest up to 132.
check('the only shipped row above the spelled-out ceiling is the one MW confirms',
      bad == ['32,133'], repr(sorted(bad)))
check('the two the screen refused are the two the adjudication named',
      refused_c == {'6,113', '27,71'}, repr(sorted(refused_c)))
check('neither refused coordinate is in the table', not (refused_c & set(table)))
for _r in d.get('_refused_form_c_out_of_space', []):
    check('%s is published with the ceiling it failed' % _r['coord'],
          isinstance(_r.get('spelled_out_ceiling'), int) and _r.get('claimants'),
          'ceiling %s, claimants %r' % (_r.get('spelled_out_ceiling'), _r.get('claimants')))
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
    # refused at entry rather than honoured as a screen. Checked below as a loop over
    # BOTH screen names, which is what the first cut got wrong: it refused an empty
    # `pwg_cited` and let an empty `same_book_conflicted` through, and the same-book
    # side is the one that shipped 32,56.

# THE CALL SITES, not just the signature — an adversarial verifier's refutation of the
# first H4386 cut. The shipped H4349 defect was never a missing argument; it was a call
# site passing the permissive value, and a signature check cannot see that. Every call
# to `_sibling_pass` must name both screens, and neither may be an empty literal.
_calls = [n for n in ast.walk(_tree) if isinstance(n, ast.Call)
          and isinstance(n.func, ast.Name) and n.func.id == '_sibling_pass']
check('every _sibling_pass call site names both screens',
      all({'same_book_conflicted', 'pwg_cited'} <= {k.arg for k in c.keywords if k.arg}
          for c in _calls),
      '%d call sites' % len(_calls))


def _is_empty_literal(node):
    """`frozenset()` / `set()` with no arguments — the shape that shipped 32,56."""
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ('frozenset', 'set')
            and not node.args and not node.keywords)


_empty_at_call = [(c.lineno, k.arg) for c in _calls for k in c.keywords
                  if k.arg in ('same_book_conflicted', 'pwg_cited')
                  and _is_empty_literal(k.value)]
check('no call site passes an empty screen literal', not _empty_at_call,
      repr(_empty_at_call))
# And the empty/type refusal must cover BOTH screens. The first cut checked `pwg_cited`
# alone, so `same_book_conflicted=frozenset()` still shipped 32,56 → cukk against the
# hardened code — the same defect, one screen over. Found structurally: the validation
# must be a loop over both screen names whose body raises.
if _fn is not None:
    _validating = [n for n in ast.walk(_fn) if isinstance(n, ast.For)
                   and any(isinstance(b, ast.Raise) for b in ast.walk(n))]
    _covered = set()
    for _loop in _validating:
        for _c in ast.walk(_loop.iter):
            if isinstance(_c, ast.Constant) and _c.value in ('same_book_conflicted',
                                                             'pwg_cited'):
                _covered.add(_c.value)
    check('the screen validation covers BOTH screens, not pwg_cited alone',
          _covered == {'same_book_conflicted', 'pwg_cited'},
          'covered %r — the H4349 defect was on the same-book side' % sorted(_covered))

# --- H4386: pw's published refusal split is a partition of its 40 citations --------
# The six terms ABBREVIATIONS_RU.md publishes, plus the two empty buckets, must add to
# the coordinate count re-counted from pw.txt with the pattern written at the top of
# this file — so the doc cannot drift from _stats, and _stats cannot drift from pw.
pw_cited = set()
with open(PW, encoding='utf-8') as f:
    for line in f:
        for rx in (CITE, CONT, FULL):
            for m in rx.finditer(line):
                pw_cited.add('%s,%s' % (m.group(1), m.group(2)))
check('pw cites %d coordinates, re-counted from the corpus' % len(pw_cited),
      len(pw_cited) == st['pw_coords_cited'] == 41,
      '_stats says %d' % st['pw_coords_cited'])
# H4438 moved this split without moving the verdict. pw's 41st citation arrives with
# the third form, and the same-book screen absorbs five coordinates that used to be
# refused one screen later or to pass as single verbal claimants — because PWG now
# resolves more of the coordinates pw also cites, so more of them are same-book
# conflicts. The sibling yield is still 0, which is the claim this file protects.
_split = {'pw_refused_nominal_head': 11, 'pw_refused_body_only': 3,
          'pw_refused_same_book_conflict': 16, 'pw_refused_not_cited_by_pwg': 3,
          'pw_refused_out_of_coordinate_space': 2,
          'pw_coords_single_verbal_claimant': 6}
check('all six published pw refusal terms hold',
      all(st.get(k) == v for k, v in _split.items()),
      repr({k: st.get(k) for k, v in _split.items() if st.get(k) != v}))
_buckets = sum(st.get(k, 0) for k in list(_split)
               + ['pw_refused_multiple_claimants', 'pw_refused_variant_reading'])
check('the screen chain partitions all 41 citations', _buckets == len(pw_cited),
      'buckets sum to %d' % _buckets)
check('the published sum is the header it is printed under',
      sum(_split.values()) == 41)
check('the sibling yield is still zero — both classes measured and empty',
      st['coords_filled_from_pw'] == 0 and st['coords_filled_from_pwg-dotted'] == 0)

print()
print('coverage %d/%d = %s%%  ·  per-source %s'
      % (len(table), st['coords_cited'], st['match_rate'], counts))
print('H4438: 3 citation forms, %d coordinates cited, %d refused out of space '
      '(83.7%% was 1465/1751 over two forms and is retired)'
      % (len(cited), len(refused_c)))
print('H4349 sibling yield: pw %d, pwg-dotted %d — both classes measured and empty'
      % (st['coords_filled_from_pw'], st['coords_filled_from_pwg-dotted']))
raise SystemExit(1 if fails else 0)
