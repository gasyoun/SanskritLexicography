#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H4432. Re-derive H4386's declined re-baseline from the raw corpora — WITHOUT
importing `build_dhatup_palsule.py`.

WHY IT DOES NOT IMPORT THE BUILDER. The numbers under adjudication (93 / 130 / 18 and
74 → 43 → 31) were published by the very code that would be changed if the verdict were
APPLY. A re-derivation that imports that code cannot refute it: it would reproduce the
builder's reading of the corpus, not the corpus. So the citation scan, the head-line
weighting, the `<lex>` nominal flag, the Böhtlingk `v. l.` marker and H1333's own
multi-claimant resolution are all restated here from the published prose, and the only
file this script reads besides the corpora is the SHIPPED ARTIFACT — as data, to learn
which coordinates the MW pass already fills. FINDINGS §637 is the reason: a number
nobody can re-derive is a number nobody should trust, and H4386 published one (`12 of
the 18`) that reproduced under no mechanical definition.

WHAT IT MEASURES. Four resolutions of the same coordinate set:

  baseline  H1333 as shipped — head-line claimants outrank body ones, `<lex>`-tagged
            head claimants lose to verbal ones, anything still tied is DROPPED.
  blunt     H4349's sibling-pass variant-reading guard applied to PWG's own claimants:
            a claimant whose citation is followed by `<ab>v. l.</ab>` is removed
            outright, sole claimant or not.
  narrow    the same note used only among MULTI-claimant coordinates, never erasing a
            sole claimant (H4386's counterfactual B).
  ordered   H4432's question: the tie-break runs LAST, on the claimants that survive
            H1333's own verbal-beats-nominal filter and only while they are still tied.
            Nothing that already resolves can move.

`--dump-flips` prints, for every coordinate the narrow reading reattributes, the raw
corpus lines of both articles, so the adjudication quotes Böhtlingk rather than
paraphrasing him.

Exit codes: 0 all published figures reproduced · 1 a figure did not reproduce ·
2 the corpora are absent (checked nothing — never a silent pass).
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))          # RussianTranslation/
GH = os.path.dirname(os.path.dirname(REPO))            # …/GitHub

DEFAULT_XLS = os.path.join(REPO, 'pwg_ru', 'eval', 'Palsule_Artha_24_01_2014.xlsx')
DEFAULT_PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
DEFAULT_ART = os.path.join(REPO, 'src', 'data', 'dhatup_palsule.json')

# --- the markup, restated from the published prose (never imported) ----------------
_L = re.compile(r'^<L>(\d+)<pc>[^<]*<k1>([^<]*)<k2>')
_DHATUP = re.compile(r'<ls\b[^>]*>\s*DH[ĀA]TUP\.\s*(\d+)\s*,\s*(\d+)')
_DHATUP_N = re.compile(r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\.\s*(\d+)\s*,\s*"[^>]*>\s*(\d+)')
_HEAD_LEX = re.compile(r'<lex\b')
_HEAD_RADICAL = re.compile('√')
_VL = re.compile(r'<ab>\s*(?:v\.\s*l\.|w\.\s*r\.)\s*</ab>')

_S2I = {
    'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ',
    'E': 'ai', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ',
    'K': 'kh', 'G': 'gh', 'N': 'ṅ', 'C': 'ch', 'J': 'jh', 'Y': 'ñ',
    'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ',
    'T': 'th', 'D': 'dh', 'P': 'ph', 'B': 'bh',
    'S': 'ś', 'z': 'ṣ',
}
_XLS_ROOT_TYPOS = {'bhu': 'bhū', 'dhu': 'dhū'}
_EDGE_PUNCT = re.compile(r'^[\s.,;:]+|[\s.,;:]+$')

# Slots per (coordinate, root) — head, body, head_nominal, head_radical, and the
# `v. l.` note counted SEPARATELY for a head-line and a body citation. The separation
# is load-bearing, not tidiness: H4386's counterfactual drops "any head-line claimant
# whose citation is followed by `<ab>v. l.</ab>`", and a claimant whose HEAD citation is
# plain while some body quotation of the same coordinate carries the note is not one.
# Conflating the two moves 18 extra coordinates and was the first thing this probe got
# wrong.
HEAD, BODY, NOMINAL, RADICAL, VL_HEAD, VL_BODY, VL_HEAD_CLAUSE = range(7)
_SLOTS = 7

#: Markup and Böhtlingk's two brace languages. Stripped before the clause test so that
#: the `.` of `<ls>P. 6,1,16</ls>` or of `{#u. s. w.#}` cannot be mistaken for the full
#: stop that ends a clause.
_TAG = re.compile(r'<[^>]*>')
_BRACES = re.compile(r'\{[#%].*?[#%]\}')
_LS_OPEN = re.compile(r'<ls\b')


def vl_governs_after(line, at):
    """Does the first `<ab>v. l.</ab>` after the citation ending at `at` govern IT?

    THE WHOLE ADJUDICATION TURNS ON THIS FUNCTION. The builder's Böhtlingk-family
    guard asks only whether such a note appears anywhere later on the same physical
    line — and a Cologne article is one physical line, so a note attached to the
    article's fourth citation is read as disowning its first. MW's side of the same
    problem was already corrected on 07-09-2026: `_vl_governs` there is clause-scoped
    with parenthesis depth, because `paRq` at 32,130 shipped a root both dictionaries
    disown when the paren was counted blindly. This is that rule, mirrored for a note
    that stands AFTER its citation instead of before it:

      governs      `<ls>DHĀTUP. 15,33</ls>, <ab>v. l.</ab>`            — nothing between
      governs      `<ls>DHĀTUP. 32,68</ls>, <ab>v. l.</ab> für {#bal#}` — names the root
      does not    `<ls>DHĀTUP. 9,76</ls>. {#laqayati#} ({#jihvonmaTane#}, <ab>v. l.</ab>`
                   — a full stop, a new finite form and an open paren stand between: the
                     note belongs to 19,53, cited later on the same line
      does not    `<ls>DHĀTUP. 19,2</ls> ({#BayasaMcalanayoH#} <ab>v. l.</ab> …)`
                   — the note sits inside a parenthesis opened AFTER the citation, so it
                     offers variants of the ARTHA, not of the headword
      does not    `<ls>DHĀTUP. 17,80</ls>. <ls n="DHĀTUP.">32,82</ls> (<ab>v. l.</ab> …)`
                   — another citation intervenes; the note is that one's
    """
    m = _VL.search(line, at)
    if not m:
        return False
    between = line[at:m.start()]
    if _LS_OPEN.search(between):
        return False
    plain = _BRACES.sub(' ', _TAG.sub(' ', between))
    depth = 0
    for ch in plain:
        if ch == '(':
            depth += 1
        elif ch == ')':
            if depth == 0:
                return False          # closes a parenthesis opened before the citation
            depth -= 1
        elif ch in '.;' and depth == 0:
            return False
    return depth == 0                 # a note deeper than the citation governs the paren


def iast(slp1):
    return ''.join(_S2I.get(c, c) for c in slp1)


def norm(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFC', s)
    s = s.replace('⎷', '').replace('√', '')
    s = _EDGE_PUNCT.sub('', s)
    s = re.sub(r'[\s\-·]', '', s)
    s = re.sub(r'\d+$', '', s).lower()
    return _XLS_ROOT_TYPOS.get(s, s)


def coord_key(c):
    g, s = c.split(',')
    return int(g), int(s)


def scan_pwg(path):
    """pwg.txt -> {coord: {root_slp1: [head, body, nominal, radical, vl]}}.

    H1333's own id space (all-digit `<L>`), its head-line weighting and its `<lex>`
    flag, plus the two slots this probe adds: the `√` marker and a `v. l.` note
    standing AFTER the citation on the citation's own line.
    """
    coords = defaultdict(lambda: defaultdict(lambda: [0] * _SLOTS))
    key, at_head, entries = None, False, 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                key, at_head = m.group(2), True
                entries += 1
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            slot = HEAD if at_head else BODY
            nominal = bool(at_head and _HEAD_LEX.search(line))
            radical = bool(at_head and _HEAD_RADICAL.search(line))
            for rx in (_DHATUP, _DHATUP_N):
                for mm in rx.finditer(line):
                    coord = '%s,%s' % (mm.group(1), mm.group(2))
                    cell = coords[coord][key]
                    cell[slot] += 1
                    if nominal:
                        cell[NOMINAL] += 1
                    if radical:
                        cell[RADICAL] += 1
                    if _VL.search(line, mm.end()):
                        cell[VL_HEAD if at_head else VL_BODY] += 1
                    if at_head and vl_governs_after(line, mm.end()):
                        cell[VL_HEAD_CLAUSE] += 1
            at_head = False
    return coords, entries


def read_palsule_roots(xls):
    """The Palsule artha index's join keys — {norm_root} only; this probe never needs
    the glosses, so it does not carry them."""
    import openpyxl
    wb = openpyxl.load_workbook(xls, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    keys = set()
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0 or not row or len(row) < 7:
            continue
        root = row[5]
        if not root:
            continue
        k = norm(str(root))
        if k:
            keys.add(k)
    wb.close()
    return keys


#: Which `v. l.` slot each reading believes. The `-clause` readings are the same
#: algorithms run against the clause-scoped note instead of the line-scoped one.
_VL_SLOT = {'blunt': VL_HEAD, 'narrow': VL_HEAD, 'ordered': VL_HEAD,
            'narrow-clause': VL_HEAD_CLAUSE, 'ordered-clause': VL_HEAD_CLAUSE,
            'blunt-clause': VL_HEAD_CLAUSE}


def resolve(coords, mode):
    """{coord: root_slp1} for the coordinates this reading attributes, by H1333's rule.

    `mode` selects where — if anywhere — the `v. l.` note is allowed to act.
    """
    out = {}
    vl = _VL_SLOT.get(mode, VL_HEAD)
    base_mode = mode.split('-')[0]
    for coord, roots in coords.items():
        roots = dict(roots)
        if base_mode == 'blunt':
            kept = {r: c for r, c in roots.items() if not c[vl]}
            roots = kept                                  # sole claimants included
        elif base_mode == 'narrow' and len(roots) > 1:
            kept = {r: c for r, c in roots.items() if not c[vl]}
            if kept:
                roots = kept
        if not roots:
            continue
        if len(roots) > 1:
            head = [r for r, c in roots.items() if c[HEAD]]
            if len(head) > 1:
                verbal = [r for r in head if not roots[r][NOMINAL]]
                if verbal:
                    head = verbal
            if base_mode == 'ordered' and len(head) > 1:
                # THE ORDERING UNDER ADJUDICATION. The note breaks a tie among the
                # claimants H1333's own filter left standing — it never removes a
                # claimant from the pool, so no coordinate that already resolves can
                # move, and no sole claimant can be erased.
                plain = [r for r in head if not roots[r][vl]]
                if plain:
                    head = plain
            if len(head) != 1:
                continue
            out[coord] = head[0]
        else:
            out[coord] = next(iter(roots))
    return out


def movement(base, other):
    gained = sorted(set(other) - set(base), key=coord_key)
    lost = sorted(set(base) - set(other), key=coord_key)
    moved = sorted((c for c in set(base) & set(other) if base[c] != other[c]),
                   key=coord_key)
    return gained, lost, moved


def article_head_lines(path, wanted_keys):
    """{<k1> key: [each article's FIRST content line]} — the head lines, where Böhtlingk
    states a root's own coordinate.

    A LIST, not one line: `<k1>` is not unique. `laYj` and `cal` are homonym sets
    (`<hom>2.</hom>`, `<hom>3.</hom>`), the coordinate under adjudication is stated by
    the third article of its key, and a reader that takes the first head line reports
    "citation not on the head line" for a citation that is plainly on one.
    """
    out, want = defaultdict(list), None
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                want = m.group(2) if m.group(2) in wanted_keys else None
                continue
            if want:
                out[want].append(line.rstrip('\n'))
                want = None
    return out


def article_lines(path, wanted_keys):
    """{<k1> key: [raw lines]} for the articles named, read in one pass."""
    out = defaultdict(list)
    key = None
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                key = m.group(2) if m.group(2) in wanted_keys else None
                if key:
                    out[key].append(line.rstrip('\n'))
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key:
                out[key].append(line.rstrip('\n'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pwg', default=DEFAULT_PWG)
    ap.add_argument('--xls', default=DEFAULT_XLS)
    ap.add_argument('--artifact', default=DEFAULT_ART)
    ap.add_argument('--dump-flips', action='store_true',
                    help='print the corpus lines of both articles for every '
                         'reattributed coordinate (the adjudication evidence)')
    a = ap.parse_args()

    missing = [p for p in (a.pwg, a.xls, a.artifact) if not os.path.exists(p)]
    if missing:
        sys.stderr.write('dhatup_h4432_rebaseline_probe: absent, checked NOTHING: %s\n'
                         % ', '.join(missing))
        return 2

    coords, entries = scan_pwg(a.pwg)
    palsule = read_palsule_roots(a.xls)
    shipped = json.load(open(a.artifact, encoding='utf-8'))
    table = shipped['table']
    mw_filled = {c for c, r in table.items() if r['source'] in ('mw', 'mw-respell')}

    base = resolve(coords, 'baseline')
    checks, failed = [], []

    def check(label, got, want):
        if want is None:                     # a measurement, not a published figure
            checks.append((label, got, '(measured)', True))
            return True
        ok = got == want
        checks.append((label, got, want, ok))
        if not ok:
            failed.append(label)
        return ok

    check('coords_cited', len(coords), 1751)
    check('coords_resolved_by_pwg', len(base), 1480)
    check('coords_conflicted', len(coords) - len(base), 271)
    check('vl_head_claimants',
          sum(1 for roots in coords.values()
              for c in roots.values() if c[VL_HEAD]), 331)

    check('vl_head_claimants_clause_scoped',
          sum(1 for roots in coords.values()
              for c in roots.values() if c[VL_HEAD_CLAUSE]), None)

    results = {}
    for mode in ('blunt', 'narrow', 'ordered', 'narrow-clause', 'ordered-clause'):
        alt = resolve(coords, mode)
        gained, lost, moved = movement(base, alt)
        results[mode] = (alt, gained, lost, moved)

    _, g_b, l_b, m_b = results['blunt']
    check('blunt: newly resolved', len(g_b), 93)
    check('blunt: lost outright', len(l_b), 130)
    check('blunt: reattributed', len(m_b), 18)
    check('blunt: total moved', len(g_b) + len(l_b) + len(m_b), 241)

    alt_n, g_n, l_n, m_n = results['narrow']
    check('narrow: newly resolved', len(g_n), 93)
    check('narrow: lost outright', len(l_n), 0)
    check('narrow: reattributed', len(m_n), 18)
    check('narrow: 32,56 resolves to cakk', alt_n.get('32,56'), 'cakk')

    # The funnel, on the narrow reading's 93 gains.
    with_row = [c for c in g_n if norm(iast(alt_n[c])) in palsule]
    already_mw = [c for c in with_row if c in mw_filled]
    net_new = [c for c in with_row if c not in mw_filled]
    check('narrow gains with a Palsule row', len(with_row), 74)
    check('narrow gains the MW pass already fills', len(already_mw), 43)
    check('narrow gains that are net new', len(net_new), 31)
    check('re-baselined coverage', len(table) + len(net_new), 1496)

    # The 18 reattributions against the SHIPPED table: how many published rows flip.
    flips_shipped = [c for c in m_n if c in table]
    check('reattributions already in the shipped table', len(flips_shipped), 17)

    # The shape of the 18, mechanically — the split H4386 had to correct.
    nominal_head = [c for c in m_n if coords[c][alt_n[c]][NOMINAL]]
    no_head = [c for c in m_n if not coords[c][alt_n[c]][HEAD]]
    check('reattributions to a <lex> nominal head line', len(nominal_head), 8)
    check('reattributions to an article with no head-line citation', len(no_head), 10)
    check('nominal + no-head is a partition of the 18',
          len(nominal_head) + len(no_head), len(m_n))
    check('reattributions to a verbal (√, no <lex>) head line',
          sum(1 for c in m_n
              if coords[c][alt_n[c]][HEAD] and not coords[c][alt_n[c]][NOMINAL]), 0)

    _, g_o, l_o, m_o = results['ordered']
    check('ordered: lost outright', len(l_o), 0)
    check('ordered: reattributed', len(m_o), 0)
    check('ordered: 32,56 resolves to cakk', results['ordered'][0].get('32,56'), 'cakk')

    print('pwg entries scanned            %d' % entries)
    for label, got, want, ok in checks:
        print('%-52s %-10s %-14s %s'
              % (label, got, want if want == '(measured)' else 'want=%s' % want,
                 '' if want == '(measured)' else ('OK' if ok else 'MISMATCH')))
    print('\nordered reading: newly resolved %d -> with a Palsule row %d, '
          'MW already fills %d, net new %d'
          % (len(g_o),
             len([c for c in g_o if norm(iast(results['ordered'][0][c])) in palsule]),
             len([c for c in g_o if c in mw_filled
                  and norm(iast(results['ordered'][0][c])) in palsule]),
             len([c for c in g_o if c not in mw_filled
                  and norm(iast(results['ordered'][0][c])) in palsule])))

    for mode in ('narrow-clause', 'ordered-clause'):
        alt_c, g_c, l_c, m_c = results[mode]
        net = [c for c in g_c
               if norm(iast(alt_c[c])) in palsule and c not in mw_filled]
        print('\n%-15s gained %3d  lost %3d  reattributed %3d  '
              '(shipped rows flipped %2d)  net new %3d -> %d/1751'
              % (mode, len(g_c), len(l_c), len(m_c),
                 len([c for c in m_c if c in table]), len(net), len(table) + len(net)))
        for c in m_c:
            cell = alt_c[c]
            print('    %-9s %-12s -> %-14s %s'
                  % (c, iast(base[c]) if c in base else '-', iast(cell),
                     'SHIPPED as %s' % table[c]['source'] if c in table
                     else 'not shipped'))

    print('\nthe 18 reattributions of the narrow reading '
          '(coord · shipped root · proposed root · shape · in shipped table):')
    for c in m_n:
        cell = coords[c][alt_n[c]]
        shape = ('nominal head line' if cell[NOMINAL] else
                 'no head-line citation' if not cell[HEAD] else 'verbal head line')
        print('  %-9s %-12s -> %-14s %-22s %s'
              % (c, iast(base[c]), iast(alt_n[c]), shape,
                 'SHIPPED as %s' % table[c]['source'] if c in table else 'not shipped'))

    # The scope evidence, one line per reattribution: what actually stands between the
    # coordinate's citation and the note the line-scoped test attributes to it.
    print('\nwhat stands between the citation and the `v. l.` note '
          '(shipped article, line-scoped test says "disowned" for all 18):')
    heads = article_head_lines(a.pwg, {base[c] for c in m_n})
    for c in m_n:
        pat = re.compile(r'DH[\u0100A]TUP\.\s*%s\s*,\s*%s\b' % tuple(c.split(',')))
        line, mm = '', None
        for cand in heads.get(base[c], []):
            mm = pat.search(cand)
            if mm:
                line = cand
                break
        between, verdict = '(citation not on the head line)', '?'
        if mm:
            note = _VL.search(line, mm.end())
            between = (line[mm.end():note.start()] if note else '(no note after)')
            if len(between) > 96:
                between = between[:93] + '...'
            verdict = 'GOVERNS' if vl_governs_after(line, mm.end()) else 'belongs elsewhere'
        print('  %-9s %-11s %-18s %s' % (c, iast(base[c]), verdict, between))

    if a.dump_flips:
        wanted = set()
        for c in m_n:
            wanted.add(base[c])
            wanted.add(alt_n[c])
        arts = article_lines(a.pwg, wanted)
        for c in m_n:
            print('\n=== %s : %s (shipped) -> %s (proposed) ==='
                  % (c, iast(base[c]), iast(alt_n[c])))
            for role, k in (('SHIPPED', base[c]), ('PROPOSED', alt_n[c])):
                print('--- %s article <k1>%s' % (role, k))
                pat = re.compile(r'DH[ĀA]TUP\.\s*%s\s*,\s*%s\b'
                                 % tuple(c.split(',')))
                for i, line in enumerate(arts.get(k, [])):
                    if pat.search(line) or i == 0:
                        print('    %s' % line)

    print('\n%d checks, %d mismatched' % (len(checks), len(failed)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
