#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H1809 — normalise NWS-layer bare citations into resolvable `<ls>` markup.

MG (voting `g5_batch1v3_sheet.html`, 28-07-2026): «ṚV(Sā) I 165, 11 is not
clickable? Why? All such entries are long ago clickable even at Cologne».
`g5_card_render.py` (H1808) explained why: the NWS (`Nachträge`) layer cites
sources in its OWN convention -- Roman-numeral maṇḍala, an optional `(Sā)`
recension marker, no period after the siglum -- while PWG's own `<ls>` markup
(and `ls_resolver`, the Python port of Cologne's `ls_service.dart`) expects
Arabic numerals, comma-separated, `Sig. n,n,n`. `ṚV(Sā) I 165, 11` and
`ṚV. 1,165,11` are the SAME locus in two spellings; only the second resolves.

This module finds citations in that convention, normalises them to a form
`ls_resolver` accepts, and -- only when the normalised form both (a) has a
siglum in PWG's own bibliography (`pwg_sources`, gating out ordinary prose
that merely LOOKS citation-shaped) and (b) actually resolves to a URL --
wraps the ORIGINAL, UNCHANGED span in `<ls n="...">`.

Design choices, and why:

* The recension marker is a genuine semantic distinction (Sāyaṇa's redaction
  of the Ṛgveda vs. the base text) -- worth preserving, not stripping. Rather
  than force that call now, the fix sidesteps it: the visible text stays
  byte-identical (`(Sā)` included), and the normalised locus goes ONLY into
  the `n=` attribute that `_ls_href`/`generate_href` already use for
  "prefix a bare continuation ref" (see `build_article_site._ls_href`).
  `generate_href('pwg', n_attr, visible)` concatenates `n_attr + visible`
  and every PWG pattern is `^`-anchored, so a normalised `n_attr` that
  matches on its own resolves correctly regardless of what (unmatched)
  original text follows it. Store round-trips byte-identical except the
  added `<ls n="...">...</ls>` wrapper -- exactly the H1809 stop condition.
* Only NWS-layer rows (`[NWS: ...]` provenance tag present) are touched --
  this is a fix for the NWS convention specifically, not a general bare-
  citation sweep. A broader census over ALL `_BARE_CIT`-shaped spans in NWS
  prose (not just this Roman-numeral shape) surfaced hundreds of matches
  that are mostly author-name+year fragments inside `[NWS: ...]` provenance
  notes, not genuine PWG citations -- see `census_report()`'s
  `general_bare_citation_note`. Marking those needs its own careful pass
  (false-link risk on a shared, gitignored production store); this module
  logs the count and stops rather than guessing at scale.
* The DOMAIN_SLOT_MIGRATIONS half-translation defect (`без уточн.` / `Мед.`
  / `Линг.` / `Лингв.` where `unsp` / `Med` / `Ling` belongs, in the `[X, Y]`
  bracket tag's slot 2) is a distinct but adjacent data defect surfaced by
  the SAME census (H1809's own text: "fix it here"). Migrated in the same
  pass since both are store-level `[diasystem, domain]`/citation markup
  gaps, not renderer gaps -- `g5_card_render`'s `DOMAIN_RU` glosses already
  cover both spellings so no rendering regresses either way.

Entry points:
    python nws_ls_markup.py census [--store PATH]
    python nws_ls_markup.py apply  [--store PATH] [--no-backup]
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import g5_card_render as g5cr           # noqa: E402  reuse _BRACKET_TAG, _norm
import ls_resolver                      # noqa: E402  generate_href, roman_int20
import pwg_sources                      # noqa: E402  the PWG-bibliography gate
import store_path                       # noqa: E402  canonical_store() -- H255 loss-safety

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NWS_TAG = re.compile(r'\[NWS:')


def _is_nws_row(row):
    """True for a genuine NWS-layer row. The authoritative signal is the
    store's own `layer` field (432 rows store-wide) -- NOT the inline
    `[NWS: ...]` provenance marker in `ru` text, which only 244 of those 432
    carry (e.g. the `yaj`/NWS-6 row citing `Harisv. ... zu ṚV. 4,42,8` has no
    inline `[NWS: ...]` at all). Union both so a `[NWS: ...]`-tagged row on a
    non-`nws` layer (a citation copied across layers) is not missed either."""
    return row.get('layer') == 'nws' or bool(NWS_TAG.search(row.get('ru') or ''))

#: siglum + optional `(recension)` marker + Roman-numeral coordinate + a
#: comma-separated numeric locus -- the NWS citation shape MG flagged.
#: `sig` deliberately excludes `(` `)` so it does not swallow the recension
#: parenthetical; `roman` is capped at 6 letters (no real maṇḍala/adhyāya
#: numeral needs more, and this keeps ordinary words from matching).
NWS_ROMAN_CIT = re.compile(
    r'(?P<sig>[A-ZĀĪŪṚṜṆṬḌŚṢḤṂÑṄ][^\s\[\]{}<>()]{0,14}?)'
    r'(?P<rec>\([^)]{1,10}\))?'
    r'\s+(?P<roman>[IVXLC]{1,6})\s+(?P<loc>\d+(?:\s*,\s*\d+)*)'
)

#: half-translated `[diasystem, domain]` slot-2 values -> canonical Latin
#: (H1847's census: measured over the RU store, 13 `без уточн(.)`,
#: 2 `Мед(.)`, 1 `Линг(.)`, 1 `Лингв(.)` of ~11.6k rows). Both dotted and
#: undotted spellings occur in the store; g5_card_render.DOMAIN_RU already
#: glosses both so migrating is presentation-neutral.
DOMAIN_SLOT_MIGRATIONS = {
    'без уточн.': 'unsp', 'без уточн': 'unsp',
    'Мед.': 'Med', 'Мед': 'Med',
    'Линг.': 'Ling', 'Линг': 'Ling',
    'Лингв.': 'Ling', 'Лингв': 'Ling',
}

#: Guards `apply()` against re-wrapping a span the STORE already marks up.
#: NOT `g5_card_render._PROTECTED` -- that regex protects RENDERED-HTML tags
#: (`<a>`, `<abbr>`, `<span class=ls>`, produced by `site_render`), whereas
#: this module edits the raw store, whose citations are wrapped in a literal
#: `<ls ...>...</ls>` tag. The two are easy to conflate (same feature, two
#: different representations) and the whole point of checking at all is to
#: make double-wrapping impossible, so use the store's own tag here.
_STORE_LS = re.compile(r'<ls\b[^>]*>.*?</ls>', re.S)

_BRACKET_TAG_DOMAIN = re.compile(
    r'(\[(?:[A-ZĀŚa-z][\wĀāŚśṢṣṚṛñ.]{0,10})\s*,\s*)'
    r'(без уточн\.?|Мед\.?|Линг\.?|Лингв\.?)'
    r'(\s*(?:\([^)]*\))?\s*\])'
)


def _load_rows(path):
    rows = []
    with io.open(path, encoding='utf-8') as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit('malformed store JSON at %s line %d: %s' % (path, lineno, exc))
    return rows


def _dump_row(row):
    return json.dumps(row, ensure_ascii=False, separators=(',', ':'))


def normalize_nws_locus(sig, roman, loc):
    """`('ṚV', 'I', '165, 11')` -> `'ṚV. 1,165,11'`, PWG's own comma form.

    Returns None when `roman` is not a valid Roman numeral (guards against
    the regex matching an all-caps word like `IX` that is not a coordinate,
    or a mandala too large to be real -- `roman_int20` caps at 20)."""
    mandala = ls_resolver.roman_int20(roman)
    if not mandala:
        return None
    loc_norm = re.sub(r'\s*,\s*', ',', loc.strip())
    sig_norm = sig if sig.endswith('.') else sig + '.'
    return '%s %d,%s' % (sig_norm, mandala, loc_norm)


def resolve_nws_citation(sig, roman, loc):
    """Normalise + validate one NWS citation span. Returns `(n_attr, href)` on
    a genuine, resolvable PWG citation, else None (siglum not in PWG's own
    bibliography, or the normalised locus does not resolve -- both are
    honest "no", not a guess)."""
    n_attr = normalize_nws_locus(sig, roman, loc)
    if n_attr is None:
        return None
    sig_norm = sig if sig.endswith('.') else sig + '.'
    if not pwg_sources.resolve(sig_norm):
        return None
    href = ls_resolver.generate_href('pwg', n_attr, '')
    if not href:
        return None
    return n_attr, href


def census(path):
    """Store-wide (not sample-wide) count of the NWS citation-convention
    defect and the domain half-translation defect. Read-only."""
    rows = _load_rows(path)
    nws_rows = 0
    resolved = []     # (key1, n_attr, href, original_span)
    residue = []       # (key1, sig, span) -- did not resolve
    domain_hits = []   # (key1, value)
    general_bare_note = 0
    for row in rows:
        if not _is_nws_row(row):
            continue
        ru = row.get('ru') or ''
        nws_rows += 1
        for m in NWS_ROMAN_CIT.finditer(ru):
            span = m.group(0)
            r = resolve_nws_citation(m.group('sig'), m.group('roman'), m.group('loc'))
            if r:
                resolved.append((row.get('key1'), r[0], r[1], span))
            else:
                residue.append((row.get('key1'), g5cr._norm(m.group('sig')), span))
        for m in _BRACKET_TAG_DOMAIN.finditer(ru):
            domain_hits.append((row.get('key1'), m.group(2)))
        general_bare_note += len(g5cr._BARE_CIT.findall(ru))
    return {
        'store_rows': len(rows),
        'nws_rows': nws_rows,
        'resolved': resolved,
        'residue': residue,
        'domain_migrations': domain_hits,
        'general_bare_citation_note': general_bare_note,
    }


def _wrap_ls(ru, m, n_attr):
    span = m.group(0)
    return ru[:m.start()] + '<ls n="%s">%s</ls>' % (n_attr.replace('"', '&quot;'), span) + ru[m.end():]


def apply(path, backup=True, dry_run=False):
    """Mutate the store: wrap resolvable NWS citations in `<ls n="...">`,
    migrate half-translated domain-slot values. Returns the same shape as
    `census()` plus `rows_changed`."""
    rows = _load_rows(path)
    resolved, residue, domain_hits = [], [], []
    rows_changed = 0
    for row in rows:
        if not _is_nws_row(row):
            continue
        ru = row.get('ru') or ''
        changed = False

        # citations -- rightmost-match-first so earlier offsets stay valid
        matches = list(NWS_ROMAN_CIT.finditer(ru))
        for m in sorted(matches, key=lambda mm: mm.start(), reverse=True):
            # never re-wrap something already inside a store <ls>...</ls> span
            protected = any(p.start() <= m.start() and m.end() <= p.end()
                            for p in _STORE_LS.finditer(ru))
            if protected:
                continue
            r = resolve_nws_citation(m.group('sig'), m.group('roman'), m.group('loc'))
            if r:
                n_attr, href = r
                ru = _wrap_ls(ru, m, n_attr)
                resolved.append((row.get('key1'), n_attr, href, m.group(0)))
                changed = True
            else:
                residue.append((row.get('key1'), g5cr._norm(m.group('sig')), m.group(0)))

        # domain-slot half-translations -> canonical Latin
        def _migrate(dm):
            domain_hits.append((row.get('key1'), dm.group(2)))
            canon = DOMAIN_SLOT_MIGRATIONS[dm.group(2)]
            return dm.group(1) + canon + dm.group(3)
        new_ru = _BRACKET_TAG_DOMAIN.sub(_migrate, ru)
        if new_ru != ru:
            ru = new_ru
            changed = True

        if changed:
            row['ru'] = ru
            rows_changed += 1

    if dry_run:
        return {'resolved': resolved, 'residue': residue,
                'domain_migrations': domain_hits, 'rows_changed': rows_changed}

    if backup:
        stamp = None
        for i in range(1, 1000):
            cand = path + '.h1809.bak' + ('' if i == 1 else '.%d' % i)
            if not os.path.exists(cand):
                stamp = cand
                break
        if stamp is None:
            raise SystemExit('could not find a free H1809 backup name near %s' % path)
        with io.open(path, encoding='utf-8') as src, io.open(stamp, 'w', encoding='utf-8') as dst:
            dst.write(src.read())

    tmp = path + '.h1809.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        for row in rows:
            fh.write(_dump_row(row) + '\n')
    os.replace(tmp, path)

    return {'resolved': resolved, 'residue': residue,
            'domain_migrations': domain_hits, 'rows_changed': rows_changed}


def _print_census(stats):
    print('store rows: %d   NWS-layer rows: %d' % (stats['store_rows'], stats['nws_rows']))
    print('NWS-convention citations resolved: %d' % len(stats['resolved']))
    for key1, n_attr, href, span in stats['resolved']:
        print('  ok   %-14s %-22r -> n=%r  %s' % (key1, span, n_attr, href))
    print('NWS-convention citations left as residue (siglum not in PWG bib, or unresolved): %d'
          % len(stats['residue']))
    for key1, sig, span in stats['residue']:
        print('  --   %-14s sig=%-10r %r' % (key1, sig, span))
    print('half-translated domain-slot values to migrate: %d' % len(stats['domain_migrations']))
    for key1, val in stats['domain_migrations']:
        print('  --   %-14s %r -> %r' % (key1, val, DOMAIN_SLOT_MIGRATIONS[val]))
    if 'general_bare_citation_note' in stats:
        print('note: %d general bare-citation-shaped spans across NWS rows were NOT touched '
              '(out of scope -- see module docstring); mostly provenance-note author/year '
              'fragments, not genuine PWG citations.' % stats['general_bare_citation_note'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('cmd', choices=['census', 'apply'])
    ap.add_argument('--store', default=None, help='override store path (default: canonical)')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--dry-run', action='store_true', help='(apply) compute but do not write')
    args = ap.parse_args()

    path = args.store or store_path.canonical_store(HERE)
    if not os.path.exists(path):
        raise SystemExit('store not found: %s' % path)

    if args.cmd == 'census':
        _print_census(census(path))
    else:
        result = apply(path, backup=not args.no_backup, dry_run=args.dry_run)
        _print_census(dict(result, store_rows=-1, nws_rows=-1))
        print('rows changed: %d%s' % (result['rows_changed'], ' (dry-run, not written)' if args.dry_run else ''))


if __name__ == '__main__':
    sys.exit(main())
