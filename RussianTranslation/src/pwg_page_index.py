#!/usr/bin/env python
"""PWG page/column co-location index — "which words shared a printed column / page".

Böhtlingk-Roth's PWG (7 vols, St. Petersburg 1855-1875) is printed in TWO
columns per page; the canonical citation unit is the column (Spalte). The source
text csl-orig/v02/pwg/pwg.txt records, per entry header, the column an entry
STARTS in:

    <L>8<pc>1-0004<k1>aMSa<k2>aMSa<h>1
         ^^^^^^ volume 1, column 0004

This tool derives three views and (optionally) annotates the Russian cards:

  1. COLUMN mode   -- column (<pc>) -> entries that start in it        (native unit)
  2. PAGE mode     -- physical page (2 columns merged) -> entries       (as in the book)
  3. REVERSE       -- entry/headword -> its column(s), page(s), volume  (lookup)
  4. --annotate    -- add volume/column/page/pc_all to pwg_ru_translated.jsonl
                      IN PLACE, idempotently (only these fields are (re)written),
                      joining cards back to source on (key1, homonym).

Page assumption: page_in_volume = (column + 1) // 2  (2 columns per page, column 1
on page 1). Column numbering is contiguous per volume in the source; the physical
page number is DERIVED, not stored in the source, so verify against scans if the
exact page label matters (a fixed front-matter offset would shift all page numbers
by a constant within a volume).

Idempotent and deterministic (no Date.now / randomness). Follows the in-place
--store enrichment convention of annotate_evidence.py.
"""
import argparse
import collections
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from store_write import locked_store_rewrite  # H2146/H3350 locked writer
from sibling_root import sibling_root
import corpus_gate as cg
from pwg_homonym import AMBIGUOUS, index_by_form_key, resolve_locus, split_subcard

# L-id may be a float (Cologne supplement/Nachtrag records, e.g. 26305.290);
# <h> homonym marker is optional. Mirrors pwg_mask.py HEADER_RE.
HEADER_RE = re.compile(r'^<L>([\d.]+)<pc>(\d+)-(\d+)<k1>(.*?)<k2>(.*?)(?:<h>(\d+))?\s*$')
# internal column-break marker inside a long entry, e.g. [Page1-0002]
PAGEBREAK_RE = re.compile(r'\[Page(\d+)-(\d+)\]')
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(sibling_root(HERE), 'csl-orig', 'v02', 'pwg', 'pwg.txt')
DEFAULT_STORE = 'pwg_ru_translated.jsonl'


class Entry:
    __slots__ = ('L', 'vol', 'col', 'k1', 'k2', 'h', 'spans')

    def __init__(self, L, vol, col, k1, k2, h):
        self.L, self.vol, self.col, self.k1, self.k2, self.h = L, vol, col, k1, k2, h
        self.spans = {(vol, col)}  # every (vol,col) this entry occupies


def page_of(col):
    """Physical page within a volume, 2 columns per page."""
    return (col + 1) // 2


def parse_source(path):
    """Return list[Entry], filling .spans from embedded [PageV-CCCC] markers."""
    entries = []
    cur = None
    with io.open(path, encoding='utf-8') as f:
        for line in f:
            m = HEADER_RE.match(line)
            if m:
                L, vol, col, k1, k2, h = m.groups()
                cur = Entry(L, int(vol), int(col), k1, k2, h)
                entries.append(cur)
                continue
            if cur is not None:
                for pv, pc in PAGEBREAK_RE.findall(line):
                    cur.spans.add((int(pv), int(pc)))
    return entries


def pc_str(vol, col):
    return f'{vol}-{col:04d}'


def write_column_view(entries, out):
    """column -> entries that START there (native PWG citation unit)."""
    by_col = collections.OrderedDict()
    for e in entries:
        by_col.setdefault((e.vol, e.col), []).append(e)
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write('column\tvolume\tpage\tn_entries\tL_ids\theadwords\n')
        for (vol, col), es in by_col.items():
            f.write('\t'.join([
                pc_str(vol, col), str(vol), str(page_of(col)), str(len(es)),
                ','.join('L' + e.L for e in es),
                ', '.join(e.k1 for e in es),
            ]) + '\n')
    return len(by_col)


def write_page_view(entries, out):
    """physical page -> entries whose START column falls on it (2 cols merged)."""
    by_page = collections.OrderedDict()
    for e in entries:
        by_page.setdefault((e.vol, page_of(e.col)), []).append(e)
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write('page\tvolume\tcolumns\tn_entries\tL_ids\theadwords\n')
        for (vol, pg), es in by_page.items():
            cols = sorted({e.col for e in es})
            f.write('\t'.join([
                f'{vol}-p{pg:04d}', str(vol),
                '+'.join(pc_str(vol, c) for c in cols), str(len(es)),
                ','.join('L' + e.L for e in es),
                ', '.join(e.k1 for e in es),
            ]) + '\n')
    return len(by_page)


def write_reverse_view(entries, out):
    """entry -> where it is: start column, all occupied columns, page(s)."""
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write('L_id\theadword\thomonym\tvolume\tstart_column\tpage'
                '\tall_columns\tall_pages\n')
        for e in entries:
            spans = sorted(e.spans)
            pages = sorted({(v, page_of(c)) for v, c in spans})
            f.write('\t'.join([
                'L' + e.L, e.k1, e.h or '', str(e.vol), pc_str(e.vol, e.col),
                f'{e.vol}-p{page_of(e.col):04d}',
                ','.join(pc_str(v, c) for v, c in spans),
                ','.join(f'{v}-p{p:04d}' for v, p in pages),
            ]) + '\n')
    return len(entries)


PC_FIELDS = ('column', 'volume', 'page', 'pc_all', 'page_all')


def compute_annotations(entries, rows):
    """Set volume/column/page/pc_all/page_all on each card IN PLACE (idempotent, pure).

    **The scalar locus is positional, not `<h>`-matched (issue #1801).** A sub-card key's
    `~~h<N>_` is the generator's 0-based `enumerate` index over the headword's PWG records,
    NOT a printed homonym number; `pwg_homonym.resolve_locus` is the only sanctioned
    reading. The former code compared that index against the source's `<h>` (which starts
    at 1), never matched for `~~h0_`, fell through to "every record sharing this key1", and
    took `starts[0]` -- the lowest column across ALL homographs. That put another word's
    printed column on 1,278 of 5,205 mappable rows and shipped it into the DE edition graph
    via `export_de_edition.py`'s `volume`/`page`/`column` allowlist.

    Fields written:
      column      the start column of the card's OWN source record, e.g. '1-0649'
      volume/page derived from that column
      pc_all      every start column of the headword (honest headword-wide superset)
      page_all    every physical page for those columns
    When the index addresses no record (degraded `key1`, source drift) the three SCALAR
    fields are omitted rather than guessed -- `pc_all`/`page_all` stay, because they never
    claimed to name one homograph. Omission is the conservative reading of the issue's
    "what a card's printed page should be when its key1 owns several PWG records"; an
    absent field cannot ship a wrong locus, a guessed one can.
    A re-run overwrites ONLY these five fields.
    """
    by_k1 = collections.defaultdict(list)
    for e in entries:
        by_k1[e.k1].append(e)
    by_fk = index_by_form_key(entries)

    stats = collections.Counter()
    for r in rows:
        cand = by_k1.get(r.get('key1'), [])
        if not cand:
            for fld in PC_FIELDS:
                r.pop(fld, None)
            stats['unmatched'] += 1
            continue
        # headword-wide, homograph-agnostic: unchanged semantics, still honest
        starts = sorted({(e.vol, e.col) for e in cand})
        pages = sorted({(v, page_of(c)) for v, c in starts})
        r['pc_all'] = [pc_str(v, c) for v, c in starts]
        r['page_all'] = [f'{v}-p{p:04d}' for v, p in pages]

        stem, enum_idx = split_subcard(r.get('subcard') or '')
        recs = by_fk.get(cg.form_key(stem)) if stem else None
        locus = resolve_locus(recs or [], enum_idx)
        if locus is AMBIGUOUS:
            for fld in ('column', 'volume', 'page'):
                r.pop(fld, None)
            stats['ambiguous'] += 1
            continue
        r['column'] = pc_str(locus.vol, locus.col)
        r['volume'] = locus.vol
        r['page'] = f'{locus.vol}-p{page_of(locus.col):04d}'
        stats['matched'] += 1
    return stats


def annotate_cards(entries, store):
    """Read `store`, apply :func:`compute_annotations`, write it back under the H2146 lock."""
    with io.open(store, encoding='utf-8') as f:
        rows = [json.loads(l) for l in f if l.strip()]
    stats = compute_annotations(entries, rows)
    # H3350: the in-place pc annotation rewrites the canonical store only
    # through the H2146 lock (PromoteClaim + fsynced backup + atomic replace);
    # ClaimBusy from a concurrent promote/mutator propagates loudly.
    locked_store_rewrite(store, rows, tag='pwgidx')
    return stats['matched'], stats['ambiguous'], stats['unmatched'], len(rows)


# --------------------------------------------------------------------------- selftest
# H3751 / issue #1801 RED-pin. Verified RED against pre-fix master (commit 7435178e0):
# every assertion below fails there with the pooled `starts[0]` locus, i.e. the LOWEST
# column across all homographs of the headword. Re-run the pin against that commit to
# reproduce; do not "fix" it to green by relaxing an expectation.
SELFTEST_SOURCE = '''<L>1000<pc>6-0001<k1>vasa<k2>vasa<h>1
{%Fett%}
<LEND>
<L>1001<pc>6-0500<k1>vasa<k2>vasa<h>2
{%Kleid%}
<LEND>
<L>1002<pc>6-0900<k1>vasa<k2>vasa<h>3
{%Herrschaft%}
<LEND>
<L>1003<pc>7-0100<k1>vasa<k2>vasa
{%Nachtrag, kein <h>%}
<LEND>
<L>2000<pc>1-0009<k1>akArya<k2>akArya
{%Nachtrag ohne Homonymzahl%}
<LEND>
<L>2001<pc>1-0199<k1>akArya<k2>akArya<h>1
{%nicht zu thun%}
<LEND>
<L>2002<pc>5-0943<k1>akArya<k2>akArya
{%zweiter Nachtrag%}
<LEND>
'''


def selftest():
    """Multi-homograph fixture pins (issue #1801). Returns 0 on success."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, 'pwg_fixture.txt')
        with io.open(src, 'w', encoding='utf-8', newline='\n') as f:
            f.write(SELFTEST_SOURCE)
        entries = parse_source(src)
    assert len(entries) == 7, len(entries)

    rows = [
        # vasa class: five printed words behind one key1, each its own sub-card.
        {'key1': 'vasa', 'subcard': 'vasa~~h0_00_pwg00'},
        {'key1': 'vasa', 'subcard': 'vasa~~h1_00_pwg00'},
        {'key1': 'vasa', 'subcard': 'vasa~~h2_00_pwg00'},
        {'key1': 'vasa', 'subcard': 'vasa~~h3_00_pwg00'},   # the <h>-less Nachtrag
        {'key1': 'vasa', 'subcard': 'vasa~~h9_00_pwg00'},   # index addresses nothing
        # the issue's own worked example: `e.h is None` records used to be admitted
        # alongside a matched homonym, so homonym 1 reported 1-0009 instead of 1-0199.
        {'key1': 'akArya', 'subcard': 'ak_arya~~h1_00_pwg00'},
        # whole-card row (gen_card pools every record; position 0 is its MAIN ENTRY)
        {'key1': 'akArya', 'subcard': 'ak_arya'},
        # headword absent from the source -> every pc field is dropped
        {'key1': 'nosuchword', 'subcard': 'nosuchword~~h0_00_pwg00', 'column': '9-9999',
         'volume': 9, 'page': '9-p5000', 'pc_all': ['9-9999'], 'page_all': ['9-p5000']},
    ]
    stats = compute_annotations(entries, rows)

    expect = ['6-0001', '6-0500', '6-0900', '7-0100', None, '1-0199', '1-0009', None]
    got = [r.get('column') for r in rows]
    assert got == expect, 'column: expected %r, got %r' % (expect, got)

    # the out-of-range index keeps the honest headword-wide fields but asserts no scalar
    amb = rows[4]
    assert amb.get('volume') is None and amb.get('page') is None, amb
    assert amb['pc_all'] == ['6-0001', '6-0500', '6-0900', '7-0100'], amb['pc_all']

    # volume/page are derived from the SAME record as column, never from another homograph
    assert rows[2]['volume'] == 6 and rows[2]['page'] == '6-p0450', rows[2]
    assert rows[5]['volume'] == 1 and rows[5]['page'] == '1-p0100', rows[5]

    # an unmatched headword loses all five fields rather than keeping a stale locus
    assert not any(f in rows[7] for f in PC_FIELDS), rows[7]

    # the operator-facing counter no longer folds ambiguous guesses into `matched`
    assert stats['matched'] == 6, stats
    assert stats['ambiguous'] == 1, stats
    assert stats['unmatched'] == 1, stats

    # idempotence: a second pass over the same rows changes nothing
    before = [dict(r) for r in rows]
    compute_annotations(entries, rows)
    assert rows == before, 'annotation is not idempotent'

    print('pwg_page_index selftest OK (8 rows, #1801 positional-locus pins)')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', default=DEFAULT_SRC, help='pwg.txt source path')
    ap.add_argument('--outdir', default='.', help='directory for the .tsv views')
    ap.add_argument('--annotate', metavar='STORE', nargs='?', const=DEFAULT_STORE,
                    help='also add pc fields to this cards jsonl in place')
    ap.add_argument('--no-views', action='store_true',
                    help='skip writing the three .tsv views')
    ap.add_argument('--selftest', action='store_true',
                    help='run the #1801 multi-homograph fixture pins and exit')
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    entries = parse_source(args.src)
    print(f'parsed {len(entries)} PWG entries from {args.src}')

    if not args.no_views:
        col_out = os.path.join(args.outdir, 'pwg_columns.tsv')
        pg_out = os.path.join(args.outdir, 'pwg_pages.tsv')
        rev_out = os.path.join(args.outdir, 'pwg_entry_locations.tsv')
        nc = write_column_view(entries, col_out)
        npg = write_page_view(entries, pg_out)
        write_reverse_view(entries, rev_out)
        print(f'  column view : {nc} columns   -> {col_out}')
        print(f'  page view   : {npg} pages     -> {pg_out}')
        print(f'  reverse view: {len(entries)} entries -> {rev_out}')

    if args.annotate:
        matched, ambiguous, unmatched, total = annotate_cards(entries, args.annotate)
        # #1801: the old single `matched` counter incremented for every homograph-pooled
        # GUESS too, so the operator-facing statistic reported success precisely in the
        # failing case. `ambiguous` is now its own column and is never folded into matched.
        print(f'annotated {args.annotate}: {matched}/{total} cards got a positional locus '
              f'({ambiguous} ambiguous -> scalars omitted, {unmatched} unmatched headwords)')


if __name__ == '__main__':
    sys.exit(main() or 0)
