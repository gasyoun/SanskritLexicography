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

DATA HONESTY. The concordance covers 1,226 of the 1,751 `DHĀTUP. x,y` coordinates
PWG actually cites (70.0%). The rest are either coordinates Böhtlingk lists under two
root spellings (`skand`/`skund`) — dropped rather than guessed — or roots absent from
Palsule's artha index. A miss returns None and the citation renders exactly as before.

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

    Shape: `DHĀTUP. 26,91 — Palsule √snih (P175, P186, …): snehane, prītau, …`.
    The page siglum is Palsule's own printed page, which is the citable address in
    the absence of an online edition."""
    c = coord(n_attr, visible)
    if c is None:
        return None
    rec = _load().get(c)
    if not rec:
        return None
    parts = ['DHĀTUP. %s' % c, 'Palsule √%s' % rec.get('palsule_root', '')]
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
