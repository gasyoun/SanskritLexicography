#!/usr/bin/env python
"""H1702 -- boundary-anchored auto-wrap for the H1651 D4 `ru_n==0` sub-pattern.

H1651 found 2,539 rows (21.9% of the store) where `de` carries >=1 `{%...%}` gloss slot
but `ru` carries zero -- not content omission (spot-checked, translation present and
correct) but a markup-fidelity gap: the Russian gloss text is simply never wrapped. H1651
declined to auto-fix this class because a naive "wrap the rest of the row" heuristic risks
swallowing following `{#...#}`/`<ab>`/`<ls>` citation content into the gloss span (see the
H1651 report's row-811 worked example). This module builds the boundary-anchored fix that
report called for.

Method -- exact-affix positional anchoring, never guessing:

1. Split `de` and `ru` on a fixed set of anchors that are NEVER translated and so are
   byte-identical between the two fields when the row is clean: `{#...#}` (Sanskrit/SLP1),
   `<ls>...</ls>` (citations), `<ab>...</ab>` (grammatical abbreviations -- per
   ABBREVIATIONS_RU.md these stay international Latin), `<is>...</is>` (transliterated
   foreign terms). `<div n="...">` tags are deliberately EXCLUDED from the anchor set: some
   rows drop the leading `<div>`/numbering marker on the RU side (a separate, pre-existing
   defect class), and requiring it to match would either misfire on those rows or need
   special-casing; leaving it out of the anchor set means such rows simply fail the
   affix-match check below and are safely skipped, not silently mishandled.
2. If the anchor sequence extracted from `de` (excluding `{%...%}` gloss spans, which are
   never literal in `ru`) is not IDENTICAL to the one extracted from `ru` -- same anchors,
   same order, same content -- the row is not eligible. This is the coarse safety gate.
3. Anchors partition both fields into the same number of "gaps" (plain text with no
   anchors in it). For each gap in `de` that contains exactly one `{%...%}` span, split it
   into (prefix, gloss, suffix). A gap with >=2 gloss spans is left ineligible -- locating
   multiple gloss boundaries in one run of free text is exactly the guessing this pass
   refuses to do.
4. The gloss boundary in the CORRESPONDING `ru` gap is placed only if that gap's text
   starts with `prefix` and ends with `suffix` EXACTLY (byte-for-byte) -- numbering markers
   like "-- 2)" and trailing separators like ": " are themselves untranslated, so an exact
   affix match on both ends is required, not merely available. If either affix doesn't
   match verbatim, the row is left untouched and reported as ineligible.
5. A row that still carries an unresolved H1651 D3 guillemet (`\xab...\xbb`) anywhere in
   `ru` is refused outright (`residual-d3-guillemet-present`), even if its OTHER gloss
   slots would otherwise pass steps 1-4. Wrapping only the unrelated slots would add a
   `{%...%}` span that makes `wrapper_defect_scan.find_d3`'s `not ru_gloss` heuristic stop
   flagging the row, hiding the still-open D3 defect from its own detector without
   resolving it -- discovered mid-pass (6 rows) and fixed by keeping the two defect
   classes disjoint rather than patching find_d3, which is out of this handoff's scope.
6. Before any gap is processed, the total `{%...%}` count in `de` is compared against the
   sum of per-gap counts after anchor-splitting; a mismatch (`gloss-span-crosses-anchor`)
   means an anchor -- typically `<ab>...</ab>` -- sits INSIDE a gloss span (a real PWG
   pattern, e.g. "{%gekocht <ab>u. s. w.</ab>%}") and split it across the anchor boundary,
   so it would read as gloss-free to the per-gap loop while other, cleanly-anchored slots
   in the same row still got wrapped -- a partial fix that breaks the all-or-nothing
   guarantee. Discovered mid-pass (4 rows: a diff between the applied fix and de/ru gloss
   counts caught it, not the sample review) and closed by refusing the whole row.

On a spot-check-scale sample (n=25, seed 11, and an earlier independent n=10 sample) every
resulting wrap reproduced the correct Russian gloss content with no boundary corruption,
including a source row where the DE `{%...%}` span itself already had an off-by-one
bracket (a pre-existing PWG markup quirk, not introduced by this pass) -- the fixer
faithfully mirrors whatever boundary DE actually encodes rather than second-guessing it.

  python src/pilot/d4_boundary_wrap.py [--store PATH]
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import re  # noqa: E402
from wrapper_defect_scan import GLOSS_SPAN, GUILLEMET_SPAN  # noqa: E402

ANCHOR_RE = re.compile(
    r'(\{#.*?#\})|(<ls\b[^>]*>.*?</ls>)|(<ab\b[^>]*>.*?</ab>)|(<is\b[^>]*>.*?</is>)',
    re.S,
)
BAD_CHARS = set('{}<>')

# H2144: fullwidth/CJK corner-bracket numbering markers that PWG's DE column uses where
# RU carries the plain ASCII equivalent (or vice versa). A one-to-one, length-preserving
# char map -- used ONLY to decide whether an affix matches; the actual prefix/suffix text
# written back to `ru` is always sliced from the ORIGINAL (non-normalized) string, so a
# fullwidth bracket already present in `ru` is never silently rewritten to ASCII.
BRACKET_NORMALIZE = str.maketrans({
    '〉': ')', '）': ')',  # 〉 ）
    '〈': '(', '（': '(',  # 〈 （
})


def split_by_anchors(text):
    """Return (gaps, anchors): len(gaps) == len(anchors) + 1."""
    anchors = []
    gaps = []
    pos = 0
    for m in ANCHOR_RE.finditer(text):
        gaps.append(text[pos:m.start()])
        anchors.append(m.group(0))
        pos = m.end()
    gaps.append(text[pos:])
    return gaps, anchors


def is_ru_n0_candidate(de_text, ru_text):
    """H1651 D4 ru_n==0 sub-pattern: de carries >=1 gloss slot, ru carries none."""
    if not de_text:
        return False
    de_n = len(GLOSS_SPAN.findall(de_text))
    ru_n = len(GLOSS_SPAN.findall(ru_text or ''))
    return de_n > 0 and ru_n == 0


def try_boundary_wrap(de_text, ru_text, normalize_brackets=False):
    """Attempt the boundary-anchored wrap. Returns (ok: bool, result: str).

    On success, result is the repaired ru text. On failure, result is a short reason code
    (residual-d3-guillemet-present, gloss-span-crosses-anchor, anchor-mismatch,
    multi-gloss-in-gap, prefix-no-match, suffix-no-match, overlap, empty-candidate,
    bad-chars-in-candidate, no-gloss-found) -- never a guess.

    H2144: when `normalize_brackets` is True, the prefix/suffix affix comparison treats
    the fullwidth/CJK corner-bracket numbering markers in BRACKET_NORMALIZE as equivalent
    to their ASCII counterparts on BOTH sides -- e.g. de's `e〉` matches ru's `e)`. This is
    comparison-only: BRACKET_NORMALIZE is a 1:1, length-preserving char map, so the actual
    prefix/suffix/candidate text spliced into the result is always sliced from the
    ORIGINAL (non-normalized) `de_text`/`ru_text` -- a fullwidth bracket already present in
    the stored gloss is never silently rewritten to ASCII. Default False keeps the H1702
    fixer's existing exact-affix behavior (and its already-passing rows) unchanged.
    """
    de_text = de_text or ''
    ru_text = ru_text or ''
    if GUILLEMET_SPAN.search(ru_text):
        # A row still carrying an unresolved H1651 D3 guillemet defect is left entirely
        # to the D3 manual-review track. Fixing this row's OTHER, unrelated gloss slots
        # would add a {%...%} span that makes find_d3's `not ru_gloss` heuristic stop
        # flagging the row -- masking the still-open D3 defect from its own detector
        # without actually resolving it. Keep the two defect classes cleanly separable.
        return False, 'residual-d3-guillemet-present'
    total_de_gloss = len(GLOSS_SPAN.findall(de_text))
    gaps_de, anchors_de = split_by_anchors(de_text)
    gaps_ru, anchors_ru = split_by_anchors(ru_text)
    if anchors_de != anchors_ru:
        return False, 'anchor-mismatch'

    gap_gloss_counts = [len(GLOSS_SPAN.findall(g)) for g in gaps_de]
    if sum(gap_gloss_counts) != total_de_gloss:
        # An anchor (e.g. a <ab>...</ab> abbreviation) sits INSIDE a {%...%} gloss span
        # (a real PWG pattern, e.g. "{%gekocht <ab>u. s. w.</ab>%}") and split it in two
        # across the anchor boundary -- each half then looks gloss-free to the per-gap
        # scan below, so that gloss slot would silently fall through untouched while
        # OTHER, cleanly-anchored slots in the same row got wrapped: a partial fix that
        # breaks the all-or-nothing guarantee. Refuse the whole row instead.
        return False, 'gloss-span-crosses-anchor'

    new_gaps_ru = list(gaps_ru)
    any_gloss = False
    for i, gap_de in enumerate(gaps_de):
        n_gloss = gap_gloss_counts[i]
        if n_gloss == 0:
            continue
        any_gloss = True
        if n_gloss >= 2:
            return False, 'multi-gloss-in-gap'
        prefix, _gloss_de, suffix = GLOSS_SPAN.split(gap_de)
        gap_ru = gaps_ru[i]
        if normalize_brackets:
            prefix_cmp = prefix.translate(BRACKET_NORMALIZE)
            suffix_cmp = suffix.translate(BRACKET_NORMALIZE)
            gap_ru_cmp = gap_ru.translate(BRACKET_NORMALIZE)
        else:
            prefix_cmp, suffix_cmp, gap_ru_cmp = prefix, suffix, gap_ru
        if not gap_ru_cmp.startswith(prefix_cmp):
            return False, 'prefix-no-match'
        if not gap_ru_cmp.endswith(suffix_cmp):
            return False, 'suffix-no-match'
        if len(gap_ru) < len(prefix) + len(suffix):
            return False, 'overlap'
        candidate = gap_ru[len(prefix):len(gap_ru) - len(suffix)] if suffix else gap_ru[len(prefix):]
        if not candidate.strip():
            return False, 'empty-candidate'
        if BAD_CHARS & set(candidate):
            return False, 'bad-chars-in-candidate'
        # Splice using RU's OWN prefix/suffix bytes, not DE's. Under exact-affix matching
        # (normalize_brackets=False) the two are guaranteed byte-identical, so this is a
        # no-op for existing rows. Under bracket-normalize matching they may differ only in
        # bracket form (e.g. de `e〉` / ru `e)`) -- using ru's own slice keeps ru's native
        # bracket character untouched, so only the added {%...%} markers are new content.
        ru_prefix = gap_ru[:len(prefix)]
        ru_suffix = gap_ru[len(gap_ru) - len(suffix):] if suffix else ''
        new_gaps_ru[i] = ru_prefix + '{%' + candidate + '%}' + ru_suffix

    if not any_gloss:
        return False, 'no-gloss-found'

    out = []
    for i, gap in enumerate(new_gaps_ru):
        out.append(gap)
        if i < len(anchors_ru):
            out.append(anchors_ru[i])
    return True, ''.join(out)


def scan_store(store_path):
    eligible, ineligible = [], {}
    with open(store_path, encoding='utf-8') as stream:
        for line_number, line in enumerate(stream):
            if not line.strip():
                continue
            row = json.loads(line)
            de = row.get('de') or ''
            ru = row.get('ru') or ''
            if not is_ru_n0_candidate(de, ru):
                continue
            label = '%s|%s|%s' % (row.get('key1'), row.get('subcard'), row.get('sense_tag'))
            ok, result = try_boundary_wrap(de, ru)
            if ok:
                eligible.append((line_number, label))
            else:
                ineligible.setdefault(result, []).append((line_number, label))
    return eligible, ineligible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store')
    args = parser.parse_args()

    from store_path import canonical_store
    default_local = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store = args.store or canonical_store(default_local)
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)

    eligible, ineligible = scan_store(store)
    total_ineligible = sum(len(v) for v in ineligible.values())
    print('store                          : %s' % store)
    print('D4 ru_n==0 rows total          : %d' % (len(eligible) + total_ineligible))
    print('  mechanically eligible        : %d' % len(eligible))
    print('  ineligible (manual review)   : %d' % total_ineligible)
    for reason, rows in sorted(ineligible.items(), key=lambda x: -len(x[1])):
        print('    %-25s %d' % (reason, len(rows)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
