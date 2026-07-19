# -*- coding: utf-8 -*-
"""Indische Sprüche (2nd ed.) full-text lookup for <ls> Spr. (II) enrichment.

H1307 (MG's N3(b) vote): a PWG `<ls>Spr. (II) N</ls>` citation should not only
link to the boesp2 scan viewer but also expose the saying's own recognized full
text on hover. This module resolves N -> the 2nd-edition saying record from the
tracked, public-domain corpus
    ../../IndischeSprueche/data/indische_sprueche.jsonl
(7,537 sayings: num, deva, iast, translation_de, ...), registered in the kosha
manifest as `indische-sprueche` with declared consumer "PWG <ls> citation links".

EDITION GUARD (load-bearing — README + PWG#87): only the 2nd-edition citation
form `Spr. (II) N` is resolved here. Plain `Spr. N` is 1st-edition numbering
(a DIFFERENT 5,419-saying edition) and MUST NEVER be looked up against this
2nd-ed JSONL — `second_ed_num()` returns None for it, so the enrichment layer
never mis-resolves a 1st-ed citation against 2nd-ed text.

The layer is render-time and language-independent (the saying is the same in the
DE/RU/EN editions), so it is SHARED per LANG_PARITY.md — build_article_site's
_render() calls it for every language, and the H1301 review-sheet emitter can
import the same functions.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))                 # RussianTranslation/src
_JSONL = os.path.normpath(os.path.join(
    HERE, '..', '..', 'IndischeSprueche', 'data', 'indische_sprueche.jsonl'))

# 2nd-edition citation form only. n= attribute + visible text are combined the
# way ls_resolver.generate_href does (a normalizing space is added between them);
# we only need the edition marker + number, so a liberal single-space join is safe.
_SPR_II = re.compile(r'^Spr\.\s*\(II\)\s*([0-9]+)')

_BY_NUM = None


def _load():
    global _BY_NUM
    if _BY_NUM is not None:
        return _BY_NUM
    _BY_NUM = {}
    if not os.path.exists(_JSONL):
        # Absent (e.g. a sparse checkout) -> lookups degrade to None, never raise.
        sys.stderr.write('spr_fulltext: corpus not found at %s — enrichment disabled\n' % _JSONL)
        return _BY_NUM
    with open(_JSONL, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            n = r.get('num')
            if isinstance(n, int):
                _BY_NUM[n] = r
    return _BY_NUM


def available():
    """True iff the full-text corpus is present on this machine."""
    return bool(_load())


def saying(n):
    """The 2nd-ed saying record for number `n`, or None."""
    try:
        return _load().get(int(n))
    except (TypeError, ValueError):
        return None


def second_ed_num(n_attr, visible):
    """Return the 2nd-edition saying number for a `Spr. (II) N` citation, or None.

    EDITION GUARD: matches ONLY the `Spr. (II)` form. Plain `Spr. N` (1st ed) and
    `Spr. (I) N` return None, so a 1st-edition citation is never resolved against
    the 2nd-edition full text."""
    combined = re.sub(r'\s+', ' ', ('%s %s' % (n_attr or '', visible or '')).strip())
    combined = re.sub(r'<[^>]+>', '', combined)      # drop any stray inner markup
    m = _SPR_II.match(combined)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _oneline(s, limit):
    """Collapse a verse/prose field to one tooltip-safe line, truncated."""
    s = (s or '')
    s = re.sub(r'^\s*[0-9]+[.)]\s*', '', s)          # strip a leading saying number
    s = s.replace('/', ' ')                           # record-internal line breaks
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > limit:
        s = s[:limit].rstrip() + '…'
    return s


def tooltip(n_attr, visible):
    """Enriched hover text for a `Spr. (II) N` citation, or None when it is not a
    2nd-ed citation or the saying is absent. Combines the IAST verse and the
    German translation from the recognized full text.

    Language-independent: the saying text is the same across the DE/RU/EN editions
    (SHARED per LANG_PARITY.md)."""
    n = second_ed_num(n_attr, visible)
    if n is None:
        return None
    rec = saying(n)
    if not rec:
        return None
    iast = _oneline(rec.get('iast'), 150)
    de = _oneline(rec.get('translation_de'), 220)
    parts = ['Spr. (II) %d' % n]
    body = ' — '.join(p for p in (iast, de) if p)
    if body:
        parts.append(body)
    return ': '.join(parts)


if __name__ == '__main__':
    for na, vi in [('', 'Spr. (II) 6145'), ('Spr. (II)', '6145.'),
                   ('', 'Spr. 1415'), ('', 'Spr. (I) 200'), ('', 'Spr. (II) 5712')]:
        print('%r %r -> num=%s' % (na, vi, second_ed_num(na, vi)))
        print('   tooltip: %s' % tooltip(na, vi))
    print('corpus available:', available(), '| entries:', len(_load()))
