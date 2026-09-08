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
Where both dictionaries name a single root, they can be compared: 633 of 815 agree
outright (77.7%), 696 (85.4%) once the regular guṇa alternation `arj`/`ṛj` is counted as
the citation-form variation it is. The 182 remaining are LISTED in the concordance's
`_mw_disagreements` and nothing is auto-resolved: a row Böhtlingk attributed keeps HIS
root, and the only rows carrying MW's spelling (`mw-respell`) are ones where Palsule has
no entry under Böhtlingk's spelling, so there was never a PWG row there to displace.

A PROSE CITATION IS NOT ALWAYS AN ATTRIBUTION (adjudication, 07-09-2026). MW's `kzal`
article cites `Dhātup. xx, 21` inside `<ab>v.l.</ab> for √ kzar` — a sentence that gives
the coordinate to `kṣar` and names `kṣal` as the rejected reading. Harvested raw it put
`kṣal` on 20,21 (and `taṭ` on 32,43, the same shape). BUT WHICH SIDE OF THE CITATION THE
NOTE SITS ON DECIDES WHAT IT MEANS: `juq`'s `<ls>…xxviii, 37</ls> (<ab>v.l.</ab> √ jun)`
puts the note AFTER, so 28,37 is the headword's and `jun` is the variant — and a `)` that
merely closes the note's OWN parenthesis ends nothing (`paRq` at 32,130, which both
dictionaries give to `piṇḍ`). So the guard is clause-scoped with parenthesis depth, not
line-scoped, and those three coordinates are DROPPED rather than
re-attributed: MW assigns them in words this parser does not read, and inventing that
attribution would be the fabrication this pipeline exists to refuse.

DATA HONESTY — COVERAGE AND ACCURACY ARE DIFFERENT NUMBERS.
  Coverage: 1,465 of the 1,751 `DHĀTUP. x,y` coordinates PWG cites (83.7%) — 1,226
  (70.0%) attributed by Böhtlingk himself and 239 added by the MW witness above (220 of
  them backed by MW's structured field, 19 by running prose alone — a weaker class,
  counted apart as `_stats.coords_filled_from_mw_prose_only`). The remaining 286 are
  coordinates no dictionary resolves unambiguously, or roots
  absent from Palsule's artha index. Filter `source == 'pwg'` for the H1333 table.

  WHY pw ADDS NOTHING (H4349), and why that is the finding rather than a failure. pw is
  the *Sanskrit-Wörterbuch in kürzerer Fassung* — Böhtlingk's own abridgement — so it
  looked like the strongest untapped source after pwg itself. It cites 40 `DHĀTUP.`
  coordinates and contributes **none**, because the same authorship that makes it strong
  evidence is what disqualifies almost every candidate:
    · 12 state the coordinate on the head line of the *artha* noun rather than the root
      (`{#uttrAsana#}¦ <lex>n.</lex> … <ls>DHĀTUP. 9,15</ls>`) — pw abridges and moves
      its citations, and it often omits `<lex>` while doing so, which is why the pass
      turns on Böhtlingk's positive `√` marker instead of on the absence of a tag;
    · 4 are body quotations, not attributions;
    · 11 name a coordinate PWG's own multi-claimant filter refused. **A same-author
      source may not break Böhtlingk's tie by adding one of Böhtlingk's votes** — the
      first cut of this pass omitted that screen and shipped `32,56 → cukk`, a
      coordinate pwg splits between `cakk` and a `v. l.` `cikk`, and whose `cukk` pwg
      places at `34,21`;
    · 3 name a coordinate pwg never cites at all. Böhtlingk renumbered between editions:
      pw's `2. √tras, trāsayati (dhāraṇe, grahaṇe, vāraṇe)` at `33,67` is pwg's
      `2. tras, trāsayati "halten"` at `33,88` — one article, three matching glosses,
      two serials. The first cut shipped that too, and since `match_rate` divides by the
      set pwg cites, it counted a row its own denominator excluded;
    · 2 — `1,840` and `1,960` — name a serial in a gaṇa whose attested serials stop at 1;
    · of the 8 that survive every screen, all 8 are coordinates the table already had.
  Every refusal is published rather than netted out (`_stats.pw_refused_*`,
  `_out_of_coordinate_space`), because a source that yields nothing is only a useful
  finding if the reasons are inspectable.
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

#: Provenance marks rendered into the tooltip (H4339, extended H4349). Deliberately
#: sigla, not prose: this module is SHARED across the RU/DE/EN editions per
#: LANG_PARITY.md, so the text must not be in one of them.
#:   `[MW]`     Böhtlingk left the coordinate ambiguous and Monier-Williams claims it
#:              for exactly one root.
#:   `[MW sp.]` Böhtlingk's own root is absent from Palsule's index and MW's spelling
#:              of it is the one Palsule glosses.
#:   `[pw]`     the coordinate comes from Böhtlingk's own abridgement, the
#:              Sanskrit-Wörterbuch in kürzerer Fassung — the same author, not a second
#:              opinion, which is why the siglum is the dictionary's own short name.
#:   `[pwg°]`   the coordinate is cited only by one of PWG's dotted-id articles, which
#:              the H1333 scan cannot see. Reserved and rendered, but EMPTY in the
#:              shipped table: those 636 articles cite one coordinate between them and
#:              it is one PWG itself leaves contested (see build_dhatup_palsule.py,
#:              `read_pwg_dotted_coords`). The mark exists so that a corpus update
#:              which puts real coordinates into that id space renders correctly on
#:              arrival rather than falling back to the unmarked PWG default.
#: A PWG-attributed row (H1333's rule) carries no mark — it is the unmarked default.
_SOURCE_MARK = {'pwg': '', 'mw': '[MW]', 'mw-respell': '[MW sp.]',
                'pw': '[pw]', 'pwg-dotted': '[pwg°]'}

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
