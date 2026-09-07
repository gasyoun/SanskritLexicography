# -*- coding: utf-8 -*-
r"""`DHĀTUP. x,y` -> Palsule artha-index enrichment for <ls> citations (H1333).

H1307 shipped the `<ls>` link layer for Pāṇini and `Spr. (II)` but had to leave its
third arm — `DHĀTUP.` -> Palsule — as an acquisition spec, because no machine-readable
Palsule-numbered dhātupāṭha existed in the org. H1333 closes that arm from MG's
supplied XLS (G.B. Palsule's artha index; rights cleared by MG 07-09-2026).

WHAT THIS ADDS, AND WHAT IT DOES NOT REPLACE. The resolver already links every
`DHĀTUP. x,y` to the csl-westergaard scan viewer at gaṇa level; that href STAYS.
This module only enriches the *hover text* with what Palsule records for the root
at that coordinate: its artha (meaning) glosses and its Palsule page(s).

NO FABRICATED LINK (H1333 step 3). Palsule's *Concordance* has no online edition, so
the Palsule datum ships as tooltip text carrying the page siglum (`P167`), never as
an href to a page that does not exist.

WHAT A RECORD ACTUALLY IS (read before trusting one). It is keyed by coordinate, but its
content is everything Palsule records for that ROOT SPELLING. Palsule's artha index is
keyed on the root, not on a gaṇa,serial pair, so it cannot separate the homonyms
Böhtlingk numbers apart: `DHĀTUP. 26,91` is the divādi `snih`, and its record carries the
arthas of every `snih` in Palsule. The tooltip therefore answers "what does Palsule
record for this root", not "what does Palsule record at exactly this coordinate".

SECOND WITNESS (H4339). Monier-Williams cites the same Böhtlingk coordinates and states
many of them in a structured field of its own (`<info westergaard="dIDIN,24.68,…"/>`).
Where Böhtlingk left a coordinate ambiguous and MW claims it for exactly one root, the
row is filled from MW and MARKED as such — `[MW]` in the tooltip, `source` in the data.
Where both dictionaries name a single root, they can be compared: 633 of 814 agree
outright (77.8%), 696 (85.5%) once the regular guṇa alternation `arj`/`ṛj` is counted as
the citation-form variation it is. The 181 remaining are LISTED in the concordance's
`_mw_disagreements` and nothing is auto-resolved: a row Böhtlingk attributed keeps HIS
root, and the only rows carrying MW's spelling (`mw-respell`) are ones where Palsule has
no entry under Böhtlingk's spelling, so there was never a PWG row there to displace.

A PROSE CITATION IS NOT ALWAYS AN ATTRIBUTION (adjudication, 07-09-2026). MW's `kzal`
article cites `Dhātup. xx, 21` inside `<ab>v.l.</ab> for √ kzar` — a sentence that gives
the coordinate to `kṣar` and names `kṣal` as the rejected reading. Harvested raw it put
`kṣal` on 20,21 (and `taṭ` on 32,43, the same shape). BUT WHICH SIDE OF THE CITATION THE
NOTE SITS ON DECIDES WHAT IT MEANS: `juq`'s `<ls>…xxviii, 37</ls> (<ab>v.l.</ab> √ jun)`
puts the note AFTER, so 28,37 is the headword's and `jun` is the variant. So the guard is
clause-scoped, not line-scoped, and those two coordinates are DROPPED rather than
re-attributed: MW assigns them in words this parser does not read, and inventing that
attribution would be the fabrication this pipeline exists to refuse.

DATA HONESTY — COVERAGE AND ACCURACY ARE DIFFERENT NUMBERS.
  Coverage: 1,465 of the 1,751 `DHĀTUP. x,y` coordinates PWG cites (83.7%) — 1,226
  (70.0%) attributed by Böhtlingk himself, 239 added by the MW witness above (220 of them
  backed by MW's structured field, 19 by running prose alone — a weaker class, counted
  apart as `_stats.coords_filled_from_mw_prose_only`). The remaining 286 are coordinates
  neither dictionary resolves unambiguously, or roots
  absent from Palsule's artha index. Filter `source == 'pwg'` for the H1333 table.
  Accuracy: measured, not asserted. Böhtlingk often prints the dhātupāṭha's own artha in
  parentheses beside the citation, which is an independent witness; over the 232
  coordinates where he does, the artha he names is in our record 139 times exactly
  (59.9%) and 174 times allowing for citation-form variation (75.0%, a deliberately weak
  test — `ched`/`chede`, `mandāyāṃ gatau`/`mandāyāṁ gatau`). Re-derive with
  `python src/build_dhatup_palsule.py` (see `_stats.inline_artha_*`).

A miss returns None and the citation renders exactly as before.

Language-independent (the dhātu and its artha are the same in the DE/RU/EN editions),
so this is SHARED per LANG_PARITY.md and the H1301 review-sheet emitter inherits it
through the same `build_article_site._ls_tooltip`.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
_JSON = os.path.join(HERE, 'data', 'dhatup_palsule.json')

#: The citation form, combined from n= attribute + visible text the way
#: ls_resolver.generate_href joins them. Both `DHĀTUP. 26,91` in one element and the
#: continuation split `n="DHĀTUP. 26," / visible "91"` normalize to the same coord.
_COORD = re.compile(r'^DH[ĀA]TUP\.\s*([0-9]+)\s*,\s*([0-9]+)')

#: Provenance marks rendered into the tooltip (H4339). Deliberately sigla, not prose:
#: this module is SHARED across the RU/DE/EN editions per LANG_PARITY.md, so the text
#: must not be in one of them. `[MW]` = Böhtlingk left the coordinate ambiguous and
#: Monier-Williams claims it for exactly one root; `[MW sp.]` = Böhtlingk's own root is
#: absent from Palsule's index and MW's spelling of it is the one Palsule glosses.
#: A PWG-attributed row (H1333's rule) carries no mark — it is the unmarked default.
_SOURCE_MARK = {'pwg': '', 'mw': '[MW]', 'mw-respell': '[MW sp.]'}

_TABLE = None
_STATS = None


def _load():
    global _TABLE, _STATS
    if _TABLE is not None:
        return _TABLE
    _TABLE, _STATS = {}, {}
    if not os.path.exists(_JSON):
        sys.stderr.write('dhatup_palsule: concordance not found at %s — '
                         'enrichment disabled\n' % _JSON)
        return _TABLE
    with open(_JSON, encoding='utf-8') as f:
        payload = json.load(f)
    _TABLE = payload.get('table') or {}
    _STATS = payload.get('_stats') or {}
    return _TABLE


def available():
    """True iff the committed concordance is present on this machine."""
    return bool(_load())


def stats():
    """The build stats recorded in the concordance header."""
    _load()
    return dict(_STATS)


def coord(n_attr, visible):
    """`DHĀTUP. x,y` -> the canonical `"x,y"` coordinate key, or None.

    A gaṇa-only citation (`DHĀTUP. 26`, no serial) returns None: Palsule is keyed on
    the root, and without the serial there is no root to key on. Those citations keep
    their gaṇa-level Westergaard link and their plain source tooltip."""
    combined = re.sub(r'\s+', ' ', ('%s %s' % (n_attr or '', visible or '')).strip())
    combined = re.sub(r'<[^>]+>', '', combined)
    m = _COORD.match(combined)
    if not m:
        return None
    return '%s,%s' % (m.group(1), m.group(2))


def record(n_attr, visible):
    """The Palsule record for a `DHĀTUP. x,y` citation, or None."""
    c = coord(n_attr, visible)
    if c is None:
        return None
    return _load().get(c)


def palsule_for(n_attr, visible, artha_limit=4):
    """Tooltip text for a `DHĀTUP. x,y` citation, or None when it is not one / is
    not in the concordance.

    Shape: `DHĀTUP. 26,91 — Palsule √snih (P175, P186, …): gatau, prītau, snehane, …`.
    The page siglum is Palsule's own printed page, which is the citable address in
    the absence of an online edition.

    PROVENANCE IS SHOWN, NOT HIDDEN (H4339). A row Böhtlingk himself attributes reads
    as above. A row that exists only because Monier-Williams broke a tie Böhtlingk left
    open says so — `Palsule √skand [MW]` — because the reader is then looking at a
    second dictionary's attribution, and that is a different epistemic claim."""
    c = coord(n_attr, visible)
    if c is None:
        return None
    rec = _load().get(c)
    if not rec:
        return None
    root = 'Palsule √%s' % rec.get('palsule_root', '')
    mark = _SOURCE_MARK.get(rec.get('source') or 'pwg')
    if mark:
        root += ' %s' % mark
    parts = ['DHĀTUP. %s' % c, root]
    pages = rec.get('pages') or []
    if pages:
        parts[-1] += ' (%s)' % ', '.join(pages[:6])
    arthas = rec.get('arthas') or []
    head = ' — '.join(parts)
    if not arthas:
        return head
    shown = ', '.join(arthas[:artha_limit])
    more = rec.get('artha_count', len(arthas)) - min(artha_limit, len(arthas))
    if more > 0:
        shown += ', +%d' % more
    return '%s: %s' % (head, shown)


if __name__ == '__main__':
    for na, vi in [('', 'DHĀTUP. 26,91'), ('DHĀTUP. 22,', '30.'),
                   ('', 'DHĀTUP. 1,1'), ('', 'DHĀTUP.'), ('', 'P. 7,4,71')]:
        print('%r %r -> coord=%s' % (na, vi, coord(na, vi)))
        print('   tooltip: %s' % palsule_for(na, vi))
    print('concordance available:', available(), '| coords:', len(_load()))
    print('stats:', json.dumps(stats(), ensure_ascii=False))
