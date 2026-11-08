"""NCC MSS canary -- what a manuscript witness unit is (H7085).

Read-only measurement comparing the two objects the 20-work canary has been
putting in one cell:

* the **parser unit** -- one distinct ``(catalogue, reference)`` pair printed in
  an NCC body, ranges expanded catalogue-wise (``census_ncc_mss.extract_units``);
* the **workbook aggregates** -- the VisualDCS counting sheet's per-row ``mss``
  cell (the current canary's ``exact-row``) and, for the like-for-like check,
  the sum of ``mss`` over every row of the work (``union-of-all-rows``) and the
  distinct ``(catalogue, accession)`` pairs enumerated in its ``Details``
  strings.

The workbook is comparison only.  No ``mss`` cell is used as an answer, no
``--full`` census run is performed, and the workbook total is never quoted as a
census.

Outputs a TSV table and a JSON summary next to this file; nothing in the corpus
or the workbook is written.

Usage:
    python ncc_mss_unit_semantics.py --selftest
    python ncc_mss_unit_semantics.py \
        --ncc ncc.jsonl --workbook "NCC-mss-counting-1 031 077.xlsx" \
        --out-tsv ncc_mss_unit_semantics_2026-10-19.tsv \
        --out-json ncc_mss_unit_semantics_2026-10-19.json
"""
import argparse
import csv
import json
import os
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_ncc_mss as cn  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

CHUNK_RE = re.compile(r'([^:;{}]+?):\s*(\d+)\s*\{([^}]*)\}')
TOKEN_RE = re.compile(r'\d{1,6}(?:\s*[-\u2013]\s*\d{1,6})?[A-Za-z]?')
PAREN_MSS_RE = re.compile(r'\(\s*\d+\s*mss\b', re.I)
PAGE_REF_RE = re.compile(r'\b(?:p{1,2}|pp)\.?\s*\d')
NUM_RANGE_RE = re.compile(r'(?<![\w.])(\d{1,6})\s*[-\u2013]\s*(\d{1,6})(?![\w])')


def _expand_range(start, stop):
    """Expand a range the catalogue way (``1042-48`` -> 1042..1048)."""
    if stop < start:
        width = len(str(stop))
        base = start - (start % (10 ** width))
        stop = base + stop
        if stop < start:
            stop = start
    if 0 <= stop - start <= 1000:
        return [str(n) for n in range(start, stop + 1)]
    return [str(start), str(stop)]


def details_units(details):
    """Distinct ``(catalogue, accession)`` pairs enumerated in a Details cell.

    The workbook's ``mss`` cell and the enumerated list are different
    quantities: a catalogue page range such as ``Bṛhatsūcī, Nepal: 427``
    declares 427 while the brace list enumerates far fewer accession numbers.
    This function reads the enumeration only.
    """
    out = set()
    for cat, _declared, body in CHUNK_RE.findall(details or ''):
        key = cn.cat_key(cn.norm_cat(cat))
        for token in TOKEN_RE.findall(body):
            m = re.match(r'^(\d+)\s*[-\u2013]\s*(\d+)([A-Za-z]?)$', token)
            if m:
                for n in _expand_range(int(m.group(1)), int(m.group(2))):
                    out.add((key, cn.norm_acc(n + m.group(3))))
            else:
                out.add((key, cn.norm_acc(token)))
    return out


def _col_index(ref):
    letters = re.match(r'([A-Z]+)', ref or '')
    if not letters:
        return None
    n = 0
    for ch in letters.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _shared_strings(z):
    strings = []
    with z.open('xl/sharedStrings.xml') as f:
        for _event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag == NS + 'si':
                strings.append(''.join(t.text or '' for t in elem.iter(NS + 't')))
                elem.clear()
    return strings


def iter_workbook_rows(path):
    """Yield workbook rows as dicts keyed by the header labels (streaming)."""
    z = zipfile.ZipFile(path)
    strings = _shared_strings(z)
    header = None
    with z.open('xl/worksheets/sheet1.xml') as f:
        for _event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag != NS + 'row':
                continue
            vals = {}
            for c in elem.findall(NS + 'c'):
                idx = _col_index(c.get('r'))
                if idx is None:
                    continue
                v = c.find(NS + 'v')
                if v is None:
                    continue
                if c.get('t') == 's':
                    vals[idx] = strings[int(v.text)]
                else:
                    vals[idx] = v.text
            elem.clear()
            if header is None:
                width = max(vals) + 1 if vals else 0
                header = [vals.get(i, '') for i in range(width)]
                continue
            row = {}
            for i, name in enumerate(header):
                if name:
                    row[name] = vals.get(i, '')
            yield row


def _workbook_index(rows_path):
    """(title -> [ids in sheet order], id -> mss) from a streaming pass."""
    titles = defaultdict(list)
    mss_of = {}
    for row in iter_workbook_rows(rows_path):
        rid = str(row.get('id', ''))
        title = unicodedata.normalize('NFC', row.get('IAST', '') or '')
        if not rid or not title:
            continue
        titles[title].append(rid)
        try:
            mss_of[rid] = int(float(row.get('mss') or 0))
        except ValueError:
            mss_of[rid] = 0
    return titles, mss_of


def _details_for(rows_path, wanted_ids):
    out = {}
    for row in iter_workbook_rows(rows_path):
        rid = str(row.get('id', ''))
        if rid in wanted_ids:
            out[rid] = row.get('Details', '') or ''
    return out


def _wb_aggregate(ids, mss_of, details):
    first = mss_of.get(ids[0], 0) if ids else None
    total = sum(mss_of.get(i, 0) for i in ids)
    union = set()
    for i in ids:
        union |= details_units(details.get(i, ''))
    return {'rows': len(ids), 'mss_first': first, 'mss_sum': total,
            'details_units': len(union)}


def _body_units(titles, body_by_title, cat_re):
    hits = []
    for t in titles:
        hits.extend(body_by_title.get(unicodedata.normalize('NFC', t), []))
    units = []
    for r in hits:
        u, _stats = cn.extract_units(r['body_html'], cat_re)
        units.extend(u)
    distinct = cn.dedupe(units)
    text = ' '.join(cn.clean_body(r['body_html']) for r in hits)
    shapes = {
        'paren_mss_counts': len(PAREN_MSS_RE.findall(text)),
        'page_refs': len(PAGE_REF_RE.findall(text)),
        'numeric_ranges': len(NUM_RANGE_RE.findall(text)),
    }
    return len(hits), len(distinct), shapes


def _row(label, group, titles, body_by_title, cat_re, wb_titles, mss_of, details):
    entries, body_units, shapes = _body_units(titles, body_by_title, cat_re)
    wb_ids = []
    for t in titles:
        wb_ids.extend(wb_titles.get(unicodedata.normalize('NFC', t), []))
    agg = _wb_aggregate(wb_ids, mss_of, details) if wb_ids else {
        'rows': 0, 'mss_first': None, 'mss_sum': None, 'details_units': None}
    # The committed reader (``read_vdcs_canary``) takes the first row whose
    # IAST equals the label exactly -- not the first alias row.  Keep that
    # exact-row rule for the "current code" column so the comparison is fair.
    exact_ids = wb_titles.get(unicodedata.normalize('NFC', label), [])
    agg['mss_first'] = mss_of.get(exact_ids[0]) if exact_ids else None
    out = {'work': label, 'group': group, 'body_entries': entries,
           'body_units': body_units, 'wb_rows': agg['rows'],
           'wb_mss_first': agg['mss_first'], 'wb_mss_sum': agg['mss_sum'],
           'wb_details_units': agg['details_units']}
    for src in ('mss_first', 'mss_sum', 'details_units'):
        v = agg[src]
        out['delta_' + src] = (body_units - v) if v is not None else None
    out.update(shapes)
    return out


def canary_table(rows_path, ncc_path, top_n=200):
    wb_titles, mss_of = _workbook_index(rows_path)
    ranked = sorted(((sum(mss_of[i] for i in ids), t)
                     for t, ids in wb_titles.items()), reverse=True)
    controls_pool = [t for _s, t in ranked[:top_n]]

    # Selected titles: the 20 canary works (with their aliases) + the head-of-
    # index pool that the control rule is applied to.
    selected = set()
    for _label, title, _fallback in cn.CANARY_WORKS:
        for t in cn.ALIASES.get(_label, {title}):
            selected.add(unicodedata.normalize('NFC', t))
    for t in controls_pool:
        selected.add(t)

    wanted_ids = set()
    for t in selected:
        wanted_ids.update(wb_titles.get(t, []))
    details = _details_for(rows_path, wanted_ids)

    # One streaming pass over the corpus: lexicon witnesses + selected bodies.
    witnesses = []
    body_by_title = defaultdict(list)
    with open(ncc_path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            witnesses.append({'mss_witnesses': r.get('mss_witnesses') or []})
            title = unicodedata.normalize('NFC', r['iast'])
            if title in selected:
                body_by_title[title].append(r)

    lexicon = cn.build_lexicon(witnesses, rows_path)
    cat_re = cn.catalogue_regex(lexicon)

    out = []
    for label, title, _fallback in cn.CANARY_WORKS:
        titles = sorted(cn.ALIASES.get(label, {title}))
        out.append(_row(label, 'canary', titles, body_by_title, cat_re,
                        wb_titles, mss_of, details))

    # Control rule (stated before use): a single workbook row, declared mss
    # >= 500, at least 100 body units -- i.e. works where the row slicing
    # question is moot and only the unit question remains.
    controls = []
    for t in controls_pool:
        ids = wb_titles.get(t, [])
        if len(ids) != 1 or mss_of.get(ids[0], 0) < 500:
            continue
        if t not in body_by_title:
            continue
        row = _row(t, 'control', [t], body_by_title, cat_re, wb_titles,
                   mss_of, details)
        if row['body_units'] < 100:
            continue
        controls.append(row)
    controls.sort(key=lambda r: abs(r['delta_mss_first'] or 0))
    return out, controls


def _write_tsv(rows, path):
    fields = ['work', 'group', 'body_entries', 'body_units', 'wb_rows',
              'wb_mss_first', 'wb_mss_sum', 'wb_details_units',
              'delta_mss_first', 'delta_mss_sum', 'delta_details_units',
              'paren_mss_counts', 'page_refs', 'numeric_ranges']
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t',
                           lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('' if r.get(k) is None else r.get(k))
                        for k in fields})


def _selftest():
    assert _expand_range(1042, 48) == [str(n) for n in range(1042, 1049)]
    assert details_units('Bikaner: 9 {78327 1636 72470 181 73441 5862-63 '
                         '441 1039  }') == {
        ('bikaner', a) for a in ('78327', '1636', '72470', '181', '73441',
                                 '5862', '5863', '441', '1039')}
    u = details_units('Bṛhatsūcī, Nepal: 427 {154 158 178 19 179 2 348 387 '
                      '342-43 83-84}')
    assert len(u) == 12, u
    print('selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ncc', default=os.path.join(HERE, 'ncc.jsonl'))
    ap.add_argument('--workbook',
                    default=os.path.join(
                        '~/Documents/GitHub/VisualDCS/non-derived/NCC/'
                        'Works-Share-NCC/NCC-mss-counting-1 031 077.xlsx'))
    ap.add_argument('--out-tsv',
                    default=os.path.join(
                        HERE, 'ncc_mss_unit_semantics_2026-10-19.tsv'))
    ap.add_argument('--out-json',
                    default=os.path.join(
                        HERE, 'ncc_mss_unit_semantics_2026-10-19.json'))
    ap.add_argument('--top', type=int, default=200,
                    help='head-of-index workbook works used as the control pool')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return 0

    workbook = os.path.expanduser(args.workbook)
    if not os.path.exists(workbook):
        sys.exit('workbook absent: %s' % workbook)

    canary, controls = canary_table(workbook, args.ncc, args.top)
    good = [c for c in controls
            if abs(c['delta_mss_first']) / float(max(c['body_units'],
                                                    c['wb_mss_first'])) <= 0.05]
    summary = {
        'source': 'H7085',
        'canary': canary,
        'controls_pool': len(controls),
        'controls_within_5pct': [c['work'] for c in good],
        'controls': controls,
    }
    _write_tsv(canary + controls, args.out_tsv)
    with open(args.out_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)

    print(f"{'work':24s} {'group':8s} {'body':>6s} {'first':>7s} {'sum':>7s} "
          f"{'union':>6s} {'d/first':>8s} {'d/sum':>7s} {'d/union':>8s}")
    for r in canary + controls:
        print(f"{r['work'][:24]:24s} {r['group']:8s} {r['body_units']:6d} "
              f"{r['wb_mss_first'] if r['wb_mss_first'] is not None else 0:7d} "
              f"{r['wb_mss_sum'] if r['wb_mss_sum'] is not None else 0:7d} "
              f"{r['wb_details_units'] if r['wb_details_units'] is not None else 0:6d} "
              f"{r['delta_mss_first'] if r['delta_mss_first'] is not None else 0:8d} "
              f"{r['delta_mss_sum'] if r['delta_mss_sum'] is not None else 0:7d} "
              f"{r['delta_details_units'] if r['delta_details_units'] is not None else 0:8d}")
    print(f"controls within 5% of the exact-row cell: {len(good)} "
          f"of {len(controls)}")
    print(f"tsv -> {args.out_tsv}")
    print(f"json -> {args.out_json}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
