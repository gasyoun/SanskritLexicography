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
import collections
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
from store_write import locked_store_rewrite  # noqa: E402  H2146/H2153 locked writer

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

# --------------------------------------------------------------------- H1909
# H1809's own census, run over ALL `g5cr._BARE_CIT`-shaped spans in NWS rows
# (not just the Roman-numeral convention above), found 929 matches store-wide
# -- far more than the handful of genuine unlinked citations. This is the
# discriminator that tells them apart, per the module docstring.

#: Full `[NWS: ...]` provenance-note span -- most bracket-interior _BARE_CIT
#: matches are author-name+year fragments the note cites for ITS OWN
#: provenance ('Windisch 1883 : 106'), not a citation the headword makes.
_NWS_BRACKET_SPAN = re.compile(r'\[NWS:[^\]]*\]')

#: A bare 4-digit number with NO internal separator, in a plausible
#: publication-year range -- the shape of an author-name+year provenance
#: fragment ('Dalal 1934', 'Lévi 1925') that lives OUTSIDE the literal
#: `[NWS: ...]` bracket too (the note is sometimes rendered as parenthetical
#: or bare-comma prose instead). A genuine PWG locus is a multi-part
#: comma/period-separated coordinate or a short 1-3 digit page number, never
#: a bare 4-digit run -- measured over the store: 290 of 804 non-bracket
#: matches are exactly this shape and none of the 185 spans this module
#: actually marks would have matched it.
_YEAR_LIKE_LOC = re.compile(r'^(1[4-9]\d\d|20[0-2]\d)$')

#: Leading Roman-numeral mandala in a `_BARE_CIT` `loc` group, either NWS
#: space-form ('I 165, 11') or comma-attached ('I,85,12') -- generalises
#: normalize_nws_locus() above to the shape `_BARE_CIT` actually captures
#: (one string, not a separate roman/loc pair).
_ROMAN_LOC_PREFIX = re.compile(r'^([IVXLC]{1,6})[\s,]+(\d[\d,\s]*)$')

#: 'H.' resolves in PWG's own bibliography (Hemacandra's Abhidhānacintāmaṇi)
#: AND `ls_resolver.generate_href` accepts a bare 1-2 digit locus for it --
#: but EVERY occurrence of this shape in the NWS layer (measured: all 3
#: outside-bracket + the 1 inside-bracket instance, store-wide) is actually
#: "2. H. 12. Jh." = "2nd half, 12th century", a German date fragment, not a
#: citation. A blanket "reject any 1-char siglum" rule was tried and
#: rejected: it also caught 4 genuine 'R I.44.6'-shaped Rāmāyaṇa citations
#: (siglum 'R' legitimately resolves too, and some locus spellings even
#: generate an href -- but Arabic vs. Roman book numbers there route to
#: DIFFERENT editions, Schlegel vs. Gorresio, so guessing one would risk a
#: wrong link; this module correctly leaves 'R'-sigla as `residue_no_href`
#: via the normal gate below instead). Naming just 'H' is the minimal,
#: evidence-backed fix for the one siglum that is both short AND resolves to
#: a valid-but-wrong link for this specific locus shape.
_SPURIOUS_SHORT_SIG = {'H'}


def _normalize_general_loc(loc_raw):
    """`'I,85,12'` / `'I 85, 12'` -> `'1,85,12'`; a plain Arabic locus passes
    through comma-normalised unchanged. Returns None only if a Roman-looking
    prefix does not parse as a real numeral (defensive -- unreachable given
    `_BARE_CIT`'s own shape, kept honest rather than guessed at)."""
    loc_raw = loc_raw.strip()
    m = _ROMAN_LOC_PREFIX.match(loc_raw)
    if m:
        mandala = ls_resolver.roman_int20(m.group(1))
        if not mandala:
            return None
        return '%d,%s' % (mandala, re.sub(r'\s*,\s*', ',', m.group(2).strip()))
    return re.sub(r'\s*,\s*', ',', loc_raw)


def classify_general_bare_citation(ru, m):
    """Does one `g5cr._BARE_CIT` match in an NWS row's `ru` look like a
    genuine bare PWG citation, or a provenance-note author/year fragment?

    Returns `(verdict, payload)`:
      'provenance_bracket'   None            -- lives inside a [NWS: ...] tag
      'provenance_year'      None            -- bare 4-digit year-shaped locus
      'provenance_short_sig' None            -- siglum in `_SPURIOUS_SHORT_SIG`
                                                 (measured false-positive
                                                 source, see that set's
                                                 docstring)
      'residue_no_bib'       sig             -- citation-shaped, siglum not
                                                 in PWG's own bibliography
      'residue_no_href'      n_attr          -- siglum resolves but
                                                 ls_resolver has no pattern
                                                 for this locus shape
      'resolved'             (n_attr, href)  -- genuine citation, validated

    Only 'resolved' is ever marked with `<ls>`; everything else is honest
    residue, matching H1809's "report, don't guess" convention (Scope §3/§5
    of the H1909 handoff)."""
    if any(b.start() <= m.start() and m.end() <= b.end()
           for b in _NWS_BRACKET_SPAN.finditer(ru)):
        return 'provenance_bracket', None
    sig = g5cr._norm(m.group('sig'))
    if sig.rstrip('.') in _SPURIOUS_SHORT_SIG:
        return 'provenance_short_sig', None
    loc_raw = m.group('loc').strip()
    if _YEAR_LIKE_LOC.match(loc_raw):
        return 'provenance_year', None
    loc_norm = _normalize_general_loc(loc_raw)
    if loc_norm is None:
        return 'residue_no_bib', sig
    sig_norm = sig if sig.endswith('.') else sig + '.'
    if not pwg_sources.resolve(sig_norm):
        return 'residue_no_bib', sig
    n_attr = '%s %s' % (sig_norm, loc_norm)
    href = ls_resolver.generate_href('pwg', n_attr, '')
    if not href:
        return 'residue_no_href', n_attr
    return 'resolved', (n_attr, href)


def _general_bare_citation_matches(ru, claimed):
    """`g5cr._BARE_CIT` matches in `ru` not already claimed by the
    Roman-numeral-specific pass (`NWS_ROMAN_CIT`) or an existing store `<ls>`
    span -- both computed by the caller against the SAME `ru` string so
    offsets always agree, even after the Roman pass has mutated it."""
    for m in g5cr._BARE_CIT.finditer(ru):
        if not any(c.start() <= m.start() and m.end() <= c.end() for c in claimed):
            yield m


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
    # H2153 (G7 / #977): the HOUSE serialization — spaced json.dumps, matching
    # promote_final_cards._serialize_rows and every annotate_* writer. This module's
    # old compact separators were the 29-07 "1.29 MB shrink": a full compact rewrite
    # that the next spaced writer reverted, churning ~1.3 MB of pure formatting per
    # flip and breaking cross-writer byte comparability.
    return json.dumps(row, ensure_ascii=False)


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
    general_resolved = []      # (key1, n_attr, href, original_span)
    general_residue = []       # (key1, sig_or_n_attr, original_span)
    general_provenance = collections.Counter()
    for row in rows:
        if not _is_nws_row(row):
            continue
        ru = row.get('ru') or ''
        nws_rows += 1
        roman_spans = list(NWS_ROMAN_CIT.finditer(ru))
        for m in roman_spans:
            span = m.group(0)
            r = resolve_nws_citation(m.group('sig'), m.group('roman'), m.group('loc'))
            if r:
                resolved.append((row.get('key1'), r[0], r[1], span))
            else:
                residue.append((row.get('key1'), g5cr._norm(m.group('sig')), span))
        for m in _BRACKET_TAG_DOMAIN.finditer(ru):
            domain_hits.append((row.get('key1'), m.group(2)))
        general_bare_note += len(g5cr._BARE_CIT.findall(ru))
        claimed = roman_spans + list(_STORE_LS.finditer(ru))
        for m in _general_bare_citation_matches(ru, claimed):
            verdict, payload = classify_general_bare_citation(ru, m)
            if verdict == 'resolved':
                n_attr, href = payload
                general_resolved.append((row.get('key1'), n_attr, href, m.group(0)))
            elif verdict in ('residue_no_bib', 'residue_no_href'):
                general_residue.append((row.get('key1'), payload, m.group(0)))
            else:
                general_provenance[verdict] += 1
    return {
        'store_rows': len(rows),
        'nws_rows': nws_rows,
        'resolved': resolved,
        'residue': residue,
        'domain_migrations': domain_hits,
        'general_bare_citation_note': general_bare_note,
        'general_resolved': general_resolved,
        'general_residue': general_residue,
        'general_provenance': dict(general_provenance),
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
    general_resolved, general_residue = [], []
    general_provenance = collections.Counter()
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

        # H1909 -- general bare-citation discriminator, run AFTER the Roman
        # pass above so `claimed` and the fresh match list share the SAME
        # (possibly just-mutated) `ru` offsets. `claimed` covers both spans
        # the Roman pass just wrapped in <ls> AND ones it left as residue
        # (e.g. 'Harisv XIII 5, 4, 5') so neither is double-reported here.
        claimed = list(NWS_ROMAN_CIT.finditer(ru)) + list(_STORE_LS.finditer(ru))
        general_matches = list(g5cr._BARE_CIT.finditer(ru))
        for m in sorted(general_matches, key=lambda mm: mm.start(), reverse=True):
            if any(c.start() <= m.start() and m.end() <= c.end() for c in claimed):
                continue
            verdict, payload = classify_general_bare_citation(ru, m)
            if verdict == 'resolved':
                n_attr, href = payload
                ru = _wrap_ls(ru, m, n_attr)
                general_resolved.append((row.get('key1'), n_attr, href, m.group(0)))
                changed = True
            elif verdict in ('residue_no_bib', 'residue_no_href'):
                general_residue.append((row.get('key1'), payload, m.group(0)))
            else:
                general_provenance[verdict] += 1

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

    general_stats = {'general_resolved': general_resolved,
                      'general_residue': general_residue,
                      'general_provenance': dict(general_provenance)}

    if dry_run:
        return {'resolved': resolved, 'residue': residue,
                'domain_migrations': domain_hits, 'rows_changed': rows_changed,
                **general_stats}

    # H2146/H2153: locked (PromoteClaim) + unique fsynced backup + atomic replace via
    # the shared writer. The old path was unlocked, and its text-mode backup copy
    # CRLF-translated on Windows — the recovery artifact was not byte-identical.
    locked_store_rewrite(path, rows, tag='h1809nws', no_backup=not backup,
                         serialize=_dump_row)

    return {'resolved': resolved, 'residue': residue,
            'domain_migrations': domain_hits, 'rows_changed': rows_changed,
            **general_stats}


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
    if 'general_resolved' in stats:
        note = (' (out of %d total shaped spans across NWS rows, '
                'Roman-convention matches above excluded)' % stats['general_bare_citation_note']
                if 'general_bare_citation_note' in stats else '')
        print('H1909 general bare-citation discriminator%s:' % note)
        print('  resolved + marked: %d' % len(stats.get('general_resolved', [])))
        for key1, n_attr, href, span in stats.get('general_resolved', []):
            print('    ok   %-14s %-22r -> n=%r  %s' % (key1, span, n_attr, href))
        print('  residue (citation-shaped, does not resolve): %d'
              % len(stats.get('general_residue', [])))
        for key1, detail, span in stats.get('general_residue', []):
            print('    --   %-14s %-30r %r' % (key1, detail, span))
        prov = stats.get('general_provenance', {})
        if prov:
            print('  excluded as provenance-note noise: %s' % dict(prov))


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
