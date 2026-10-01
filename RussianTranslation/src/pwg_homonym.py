#!/usr/bin/env python
r"""The one place that knows what `~~h<N>` in a pwg_ru sub-card key MEANS (issue #1801).

`~~h<N>_` is **not** a homonym number. It is the 0-based `enumerate` index over the PWG
source records of a headword, assigned in `_pilot_gen_merged.gen_root_split`:

    for hom, (dl, cards, npfx) in enumerate(segmented):
        sub = '%s~~h%d_00_%s' % (root, hom, label)

PWG's printed `<h>` values start at 1 and are not contiguous across a headword's record
list (Nachtrag records carry no `<h>` at all), so comparing the two is a type confusion.
H2889 measured the damage: `~~h0_` maps to printed `<h>1` 113x, `<h>2` 48x, `<h>3` 33x --
and never to `<h>0`. Consumers that treated the index as an `<h>` value silently fell back
to "the lowest column across every homograph of this headword", i.e. another word's
printed locus (1,278 of 5,211 mappable store rows, 24.5 %).

The only evidence-decidable reading is **positional**: index `N` addresses the `N`-th
source record of that headword, in source order -- exactly the list the generator
enumerated. `resolve_locus()` is that reading, and it is what every consumer must use.

The subkey text itself is deliberately left alone: it is the identity of 11k+ already
promoted store rows, and re-spelling it would fork the join rather than fix it. What is
fixed is the *interpretation* -- plus, at the generation end, the printed homonym is now
carried explicitly (`hom_printed` in the rootmap, and the translator-facing header) so no
downstream reader has to guess again.
"""
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_gate as cg                      # noqa: E402
import pwg_mask                               # noqa: E402
from safe_filename import decode_safe_name    # noqa: E402

# `<stem>~~h<N>_<rest>` -- the generated sub-card key shape.
SUBCARD_RE = re.compile(r'^(?P<stem>.*?)~~h(?P<idx>\d+)_')

#: returned by :func:`resolve_locus` when the index addresses no source record.
AMBIGUOUS = object()

Locus = collections.namedtuple('Locus', 'h vol col record_index n_records')


def split_subcard(subcard):
    """Return ``(generation_stem_decoded, enumerate_index_or_None)``.

    The stem is the ``safe_name()`` encoding of the key the generator was invoked with,
    which is a better witness of the intended lemma than the row's own (sometimes
    degraded, issue #1767) ``key1``.
    """
    if not subcard:
        return '', None
    m = SUBCARD_RE.match(subcard)
    if m:
        return decode_safe_name(m.group('stem')), int(m.group('idx'))
    return decode_safe_name(subcard), None


def index_by_form_key(entries):
    """``form_key(k1) -> [entry, ...]`` in SOURCE ORDER.

    Mirrors `dict_merge.index('pwg')` -- same file, same order, same key function -- so the
    list positions are the ones `gen_root_split`'s `enumerate` walked.
    """
    idx = collections.defaultdict(list)
    for e in entries:
        idx[cg.form_key(e.k1)].append(e)
    return idx


def resolve_locus(records, enum_index):
    """The record an enumerate index addresses, or :data:`AMBIGUOUS`.

    ``enum_index is None`` means a whole-card row: `gen_card` pools every record of the
    headword into one card whose MAIN ENTRY is `records[0]` (later positions are labelled
    Nachträge/addenda), so position 0 is that card's own printed locus.
    """
    if not records:
        return AMBIGUOUS
    pos = 0 if enum_index is None else enum_index
    if pos >= len(records):
        return AMBIGUOUS
    e = records[pos]
    return Locus(h=e.h, vol=e.vol, col=e.col, record_index=pos, n_records=len(records))


def header_locus(header_line):
    """``(printed_h_or_None, '<pc>' string or None)`` from a raw PWG ``<L>`` header line.

    Lets the *generator* stamp the printed homonym and column it actually read, instead of
    leaving every downstream consumer to re-derive them from a positional index.
    """
    m = pwg_mask.HEADER_RE.match(header_line or '')
    if not m:
        return None, None
    return m.group(5), (m.group(2) or None)
