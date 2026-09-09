#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H4438. Re-derive the three scope corrections and the citation-form ruling from the
raw corpora — WITHOUT importing `build_dhatup_palsule.py`.

WHY IT DOES NOT IMPORT THE BUILDER. Same reason as the H4432 probe beside it: every
number below was published by the code this handoff changed, so a re-derivation that
imports that code reproduces the builder's reading of PWG rather than PWG. The citation
forms, the head-line weighting, the `<lex>` nominal flag, the Böhtlingk `v. l.` marker,
the clause test and H1333's multi-claimant resolution are all restated here from the
published prose. The only non-corpus file it reads is the SHIPPED ARTIFACT, as data.

WHAT IT MEASURES, in the order the adjudication argues it.

  1  The `<lex>` nominal head test, line-scoped against scoped-to-before-the-citation:
     128 flags, 73 of them with no tag anywhere before the citation.
  2  The Böhtlingk trailing `v. l.` note: 1999 head-line claimant pairs, 331 carrying a
     note somewhere later on the line, 148 governing under the strict reading, 165 once
     punctuation-only separation is admitted, 166 left not governing.
  3  What the note WOULD do if it were applied to H1333's own pass — measured, never
     applied, because H4386 and H4432 both declined that re-baseline: 93 gains and 18
     reattributions line-scoped, 74 gains and exactly 8 reattributions clause-scoped.
  4  The head/body discriminator widened, the residue-5 defect: to `<div n="p">`
     continuations, and to the whole article. Both measured, both declined.
  5  The third citation form `<ls n="DHĀTUP.">4,13</ls>`: 320 occurrences, 270 distinct
     coordinates, 141 cited by no other form, 281 of the 320 on the citing article's own
     head line, 93 of the 141 independently cited by Monier-Williams, 3 above the
     attested ceiling of their gaṇa.
  6  The shipped artifact after the ruling: 1575 rows over 1892 cited coordinates, and
     the six coordinates whose lone head-line claimant was a noun article.

`--dump <coord>…` prints every PWG line claiming those coordinates, in all three
citation forms, so an adjudication quotes Böhtlingk rather than paraphrasing him.

Exit codes: 0 every published figure reproduced · 1 a figure did not reproduce ·
2 the corpora are absent (checked nothing — never a silent pass).
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))          # RussianTranslation/
GH = os.path.dirname(os.path.dirname(REPO))            # …/GitHub

DEFAULT_PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
DEFAULT_MW = os.path.join(GH, 'csl-orig', 'v02', 'mw', 'mw.txt')
DEFAULT_ART = os.path.join(REPO, 'src', 'data', 'dhatup_palsule.json')

# --- the markup, restated from the published prose (never imported) ----------------
_L = re.compile(r'^<L>(\d+)<pc>[^<]*<k1>([^<]*)<k2>')
_DHATUP = re.compile(r'<ls\b[^>]*>\s*DH[ĀA]TUP\.\s*(\d+)\s*,\s*(\d+)')
_DHATUP_N = re.compile(r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\.\s*(\d+)\s*,\s*"[^>]*>\s*(\d+)')
_DHATUP_N_FULL = re.compile(r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\."[^>]*>\s*(\d+)\s*,\s*(\d+)')
_AB = (_DHATUP, _DHATUP_N)                       # what the builder read before H4438
_ABC = (_DHATUP, _DHATUP_N, _DHATUP_N_FULL)      # what it reads after
_HEAD_LEX = re.compile(r'<lex\b')
_VL = re.compile(r'<ab>\s*(?:v\.\s*l\.|w\.\s*r\.)\s*</ab>')
_LS_OPEN = re.compile(r'<ls\b')
_MARKUP_SPAN = re.compile(r'<[^>]*>|\{#.*?#\}|\{%.*?%\}|\{@.*?@\}')
_WORDLIKE = re.compile(r'[^\W_]', re.UNICODE)
_DIV = re.compile(r'^<div n="([^"]*)"')

_MW_DHATUP = re.compile(r'<ls\b[^>]*>\s*Dh[āaĀA]tup\.\s*([ivxlcIVXLC]+)\s*,\s*(\d+)')
_MW_N_FULL = re.compile(
    r'<ls\b[^>]*\bn\s*=\s*"Dh[āaĀA]tup\."[^>]*>\s*([ivxlcIVXLC]+)\s*,\s*(\d+)')
_MW_N_GANA = re.compile(
    r'<ls\b[^>]*\bn\s*=\s*"Dh[āaĀA]tup\.\s*([ivxlcIVXLC]+)\s*,\s*"[^>]*>\s*(\d+)')
_ROMAN = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}


def roman(s):
    s = (s or '').lower()
    total = 0
    for i, ch in enumerate(s):
        v = _ROMAN.get(ch)
        if v is None:
            return None
        nxt = _ROMAN.get(s[i + 1]) if i + 1 < len(s) else 0
        total += -v if (nxt or 0) > v else v
    return total or None


def coord_key(c):
    return [int(x) for x in c.split(',')]


def blank_markup(s):
    """`s` with tag and `{#…#}` / `{%…%}` spans replaced by spaces of equal length, so
    the `.` inside `<ab>caus.</ab>` cannot be read as the full stop ending a clause."""
    if '<' not in s and '{' not in s:
        return s
    out = list(s)
    for m in _MARKUP_SPAN.finditer(s):
        for i in range(m.start(), m.end()):
            out[i] = ' '
    return ''.join(out)


def vl_governs(line, at, strict=False):
    """Does the FIRST trailing `v. l.` note after the citation ending at `at` govern it?

    `strict=True` is the reading that refuses any `.` at parenthesis depth zero (148
    governing pairs); the shipped reading additionally admits a note separated from the
    citation by punctuation alone with no parenthesis between — Böhtlingk's ordinary
    `</ls>. <ab>v. l.</ab> für {#X#}` (165 governing pairs, same eight reattributions)."""
    note = _VL.search(line, at)
    if note is None:
        return False
    raw = line[at:note.start()]
    if _LS_OPEN.search(raw):
        return False
    between = blank_markup(raw)
    depth = dots = 0
    for ch in between:
        if ch == '(':
            depth += 1
        elif ch == ')':
            if depth == 0:
                return False
            depth -= 1
        elif depth == 0:
            if ch == ';':
                return False
            if ch == '.':
                dots += 1
    if depth > 0:
        return False
    if not dots:
        return True
    if strict or '(' in between or ')' in between:
        return False
    return not _WORDLIKE.search(between)


def scan(pwg, forms=_ABC, lex_scope='before', head_scope='line', strict_vl=False):
    """coord -> {root: [head, body, head_nominal, head_governing_note]}, plus the raw
    per-firing records the shape census needs."""
    coords = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
    firings = []          # (coord, root, line_scoped_note, governing_note)
    lex_flags = []        # (coord, root, tag_anywhere_on_line, tag_before_citation)
    key = None
    first = False
    entries = 0
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                key = m.group(2)
                first = True
                entries += 1
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            d = _DIV.match(line)
            if head_scope == 'line':
                at_head = first
            elif head_scope == 'para':
                at_head = first or (d is not None and d.group(1) == 'p')
            else:
                at_head = True
            lex_line = bool(_HEAD_LEX.search(line))
            for rx in forms:
                for mm in rx.finditer(line):
                    coord = '%s,%s' % (mm.group(1), mm.group(2))
                    c = coords[coord][key]
                    c[0 if at_head else 1] += 1
                    if not at_head:
                        continue
                    lex_before = bool(_HEAD_LEX.search(line, 0, mm.start()))
                    if lex_line or lex_before:
                        lex_flags.append((coord, key, lex_line, lex_before))
                    if (lex_line if lex_scope == 'line' else lex_before):
                        c[2] += 1
                    noted = bool(_VL.search(line, mm.end()))
                    gov = vl_governs(line, mm.end(), strict=strict_vl)
                    if noted or gov:
                        firings.append((coord, key, noted, gov))
                    if gov:
                        c[3] += 1
            first = False
    return coords, firings, lex_flags, entries


def resolve(coords, guard=False, sole_nominal=False):
    """H1333's rule, restated. `guard` is the NARROW variant-reading reading (drop noted
    claimants only where others remain); `sole_nominal` is H4438's refusal of a lone
    `<lex>` head claimant."""
    out = {}
    for coord, roots in coords.items():
        roots = dict(roots)
        if guard and len(roots) > 1:
            kept = {r: c for r, c in roots.items() if not c[3]}
            if kept:
                roots = kept
        head = [r for r, c in roots.items() if c[0]]
        if sole_nominal and len(roots) > 1 and len(head) == 1 and roots[head[0]][2]:
            roots = {r: c for r, c in roots.items() if r != head[0]}
            head = []
        if len(roots) > 1:
            if len(head) > 1:
                verbal = [r for r in head if not roots[r][2]]
                if verbal:
                    head = verbal
            if len(head) != 1:
                continue
            out[coord] = head[0]
        else:
            out[coord] = next(iter(roots))
    return out


def mw_cited(mw):
    out = set()
    with open(mw, encoding='utf-8') as f:
        for line in f:
            for rx in (_MW_DHATUP, _MW_N_FULL, _MW_N_GANA):
                for mm in rx.finditer(line):
                    g = roman(mm.group(1))
                    if g:
                        out.add('%d,%s' % (g, mm.group(2)))
    return out


class Checks(object):
    def __init__(self):
        self.fails = []
        self.n = 0

    def eq(self, label, got, want):
        self.n += 1
        ok = got == want
        if not ok:
            self.fails.append('%s: got %r, expected %r' % (label, got, want))
        print('  %-58s %-22s %s' % (label, got, 'OK' if ok else 'FAIL (want %r)' % (want,)))


def dump(pwg, wanted):
    want = set(wanted)
    key = None
    first = False
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                key = m.group(2)
                first = True
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            for rx, tag in ((_DHATUP, 'A'), (_DHATUP_N, 'B'), (_DHATUP_N_FULL, 'C')):
                for mm in rx.finditer(line):
                    c = '%s,%s' % (mm.group(1), mm.group(2))
                    if c in want:
                        lo = max(0, mm.start() - 110)
                        print('%-9s %-14s form=%s %-4s %s' % (
                            c, key, tag, 'HEAD' if first else 'body',
                            line[lo:mm.end() + 90].replace('\n', ' ')))
            first = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pwg', default=DEFAULT_PWG)
    ap.add_argument('--mw', default=DEFAULT_MW)
    ap.add_argument('--artifact', default=DEFAULT_ART)
    ap.add_argument('--dump', nargs='*', default=None,
                    help='print every PWG line claiming these coordinates and stop')
    a = ap.parse_args()

    for p in (a.pwg, a.mw):
        if not os.path.exists(p):
            print('corpus absent: %s' % p)
            print('CHECKED NOTHING — exit 2, never a silent pass.')
            return 2

    if a.dump is not None:
        dump(a.pwg, a.dump)
        return 0

    c = Checks()

    print('1  the <lex> nominal head test (residue 2)')
    coords_ab, firings_ab, lex_ab, entries = scan(a.pwg, forms=_AB, lex_scope='line')
    flags = {(x[0], x[1]) for x in lex_ab if x[2]}
    before = {(x[0], x[1]) for x in lex_ab if x[2] and x[3]}
    c.eq('PWG all-digit articles seen', entries, 122730)
    c.eq('head-line (coord, root) pairs flagged nominal, line-scoped', len(flags), 128)
    c.eq('of those, with NO <lex> before the citation', len(flags - before), 73)

    print('2  the Böhtlingk trailing v.l. note (residue 1)')
    pairs = {(coord, r) for coord, rr in coords_ab.items() for r in rr}
    head_pairs = {(coord, r) for coord, rr in coords_ab.items()
                  for r, x in rr.items() if x[0]}
    lined = {(x[0], x[1]) for x in firings_ab if x[2]}
    gov = {(x[0], x[1]) for x in firings_ab if x[3]}
    c.eq('head-line claimant pairs', len(head_pairs), 1999)
    c.eq('carrying a note anywhere later on the line', len(lined), 331)
    c.eq('of those, governing under the shipped clause rule', len(gov), 165)
    c.eq('left NOT governing (the detector misfires)', len(lined - gov), 166)
    _, firings_strict, _, _ = scan(a.pwg, forms=_AB, lex_scope='line', strict_vl=True)
    c.eq('governing under the strict `.` reading', len({(x[0], x[1]) for x in
                                                        firings_strict if x[3]}), 148)

    print('3  what the note would do to H1333 — measured, NOT applied')
    base_ab = resolve(coords_ab)
    coords_line = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
    for coord, rr in coords_ab.items():
        for r, x in rr.items():
            coords_line[coord][r] = list(x)
    for coord, r in lined:
        coords_line[coord][r][3] = 1
    g_line = resolve(coords_line, guard=True)
    g_clause = resolve(coords_ab, guard=True)
    c.eq('line-scoped: gains', len(set(g_line) - set(base_ab)), 93)
    c.eq('line-scoped: coordinates lost', len(set(base_ab) - set(g_line)), 0)
    c.eq('line-scoped: reattributions', len([x for x in set(base_ab) & set(g_line)
                                             if base_ab[x] != g_line[x]]), 18)
    c.eq('clause-scoped: gains', len(set(g_clause) - set(base_ab)), 74)
    c.eq('clause-scoped: coordinates lost', len(set(base_ab) - set(g_clause)), 0)
    flips = sorted([x for x in set(base_ab) & set(g_clause)
                    if base_ab[x] != g_clause[x]], key=coord_key)
    c.eq('clause-scoped: reattributions', len(flips), 8)
    c.eq('clause-scoped: the flip set', ','.join(flips),
         '15,33,17,13,32,30,32,68,32,119,33,5,33,55,35,11')

    print('4  the head/body discriminator widened (residue 5) — measured, DECLINED')
    base_now = resolve(scan(a.pwg, forms=_AB)[0])
    for mode, want in (('para', (9, 1, 1)), ('article', (55, 0, 4))):
        r = resolve(scan(a.pwg, forms=_AB, head_scope=mode)[0])
        got = (len(set(base_now) - set(r)), len(set(r) - set(base_now)),
               len([x for x in set(base_now) & set(r) if base_now[x] != r[x]]))
        c.eq('head scope=%-7s (lost, gained, root-changed)' % mode, got, want)

    print('5  the third citation form (residue 6) — ADMITTED after adjudication')
    occ = 0
    formc = defaultdict(int)
    on_head = 0
    key = None
    first = False
    with open(a.pwg, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                key = m.group(2)
                first = True
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            for mm in _DHATUP_N_FULL.finditer(line):
                occ += 1
                on_head += 1 if first else 0
                formc['%s,%s' % (mm.group(1), mm.group(2))] += 1
            first = False
    seen_ab = set(coords_ab)
    new = [x for x in formc if x not in seen_ab]
    c.eq('form-C occurrences', occ, 320)
    c.eq('form-C distinct coordinates', len(formc), 270)
    c.eq('of those, cited by no other form', len(new), 141)
    c.eq('form-C occurrences on the article\'s own head line', on_head, 281)
    mw = mw_cited(a.mw)
    c.eq('new coordinates Monier-Williams cites independently',
         sum(1 for x in new if x in mw), 93)
    # The ceiling is built from forms A and B only. Form C spells `DHĀTUP.` in an
    # ATTRIBUTE, and an attribute is inheritable — so a form-C coordinate may not
    # certify its own gaṇa.
    ceil = defaultdict(int)
    for x in seen_ab:
        g, s = coord_key(x)
        ceil[g] = max(ceil[g], s)
    over = sorted([x for x in new if coord_key(x)[1] > ceil[coord_key(x)[0]]],
                  key=coord_key)
    c.eq('new coordinates above the attested ceiling of their gaṇa', ','.join(over),
         '6,113,27,71,32,133')
    c.eq('gaṇa 6 stops at (kṣip claims a 113th root)', ceil[6], 25)
    c.eq('gaṇa 27 stops at (rādh claims a 71st root)', ceil[27], 33)
    c.eq('gaṇa 32 stops at (stūp claims the 133rd, one past)', ceil[32], 132)
    # MW is the one witness allowed to break a Böhtlingk tie here, and it splits the
    # three cleanly: it prints `xxxii, 133` for stūp, prints `xxvi, 71` — not xxvii —
    # where PWG has 27,71, and gives kṣip no such coordinate at all.
    c.eq('of the three, the ones MW independently names',
         ','.join(x for x in over if x in mw), '32,133')

    print('6  the shipped artifact')
    if not os.path.exists(a.artifact):
        print('  artifact absent: %s' % a.artifact)
        c.fails.append('artifact absent')
    else:
        with open(a.artifact, encoding='utf-8') as f:
            art = json.load(f)
        st = art['_stats']
        c.eq('rows', len(art['table']), 1573)
        c.eq('coords_cited (1892 cited, 2 refused out of space)',
             st['coords_cited'], 1890)
        c.eq('coords_refused_form_c_out_of_space',
             st['coords_refused_form_c_out_of_space'], 2)
        c.eq('the two refused', ','.join(
            r['coord'] for r in art['_refused_form_c_out_of_space']), '6,113,27,71')
        c.eq('match_rate', st['match_rate'], 83.2)
        c.eq('coords_conflicted', st['coords_conflicted'], 346)
        c.eq('coords_linked_pwg', st['coords_linked_pwg'], 1302)
        c.eq('coords_sole_nominal_head_dropped',
             st['coords_sole_nominal_head_dropped'], 6)
        c.eq('the six refused nominal head claimants',
             ','.join(r['coord'] for r in art['_dropped_sole_nominal_head']),
             '7,3,19,54,20,27,23,39,32,109,33,73')
        c.eq('MW cross-agreement rate (rose from 77.7 pre-H4438)',
             st['cross_agreement_rate'], 80.1)
        # The guard ported in this handoff is a STANDING screen, not a live one: it
        # refuses nothing in either sibling pass today, and that is the claim.
        c.eq('pw_refused_variant_reading', st['pw_refused_variant_reading'], 0)
        c.eq('pwg-dotted_refused_variant_reading',
             st['pwg-dotted_refused_variant_reading'], 0)

    print('\n%d checks, %d failed' % (c.n, len(c.fails)))
    for f in c.fails:
        print('  FAIL %s' % f)
    return 1 if c.fails else 0


if __name__ == '__main__':
    sys.exit(main())
