"""NCC manuscript census from bodies -- strict witness unit (H6995).

The shipped ``ncc.jsonl`` ``mss_witnesses`` field is a narrow citation-shape
heuristic (``MSS_WITNESS_RE`` in ``parse_ncc.py``): it only fires on
"Abbrev. 123" and silently drops prose witnesses such as "Bikaner 1042-48",
"Adyar D. XIII. 899. 902." or "Bodl. Sup. 39-41".  It therefore cannot be the
basis of a census.  This tool re-reads ``body_html`` and extracts the strict
witness unit:

    (catalogue siglum, accession number)

from every body, expands simple accession ranges, dedupes on the normalised
pair, and emits per-entry and per-work counts.  Catalogue sigla come from a
lexicon built out of (a) the catalogue prefixes already visible in
``mss_witnesses`` and (b) the catalogue keys of the VisualDCS counting sheet,
which is only used as an abbreviation table -- all counts are recomputed from
the NCC bodies.

Never publish 1,032,077 as a census: that is the sum of the ``mss`` column
over all 140,848 rows of the VisualDCS counting spreadsheet, including
Author/Commentary rows and catalogue range serials.  It is a workbook total,
not a distinct-manuscript count.

Usage:
    python census_ncc_mss.py --ncc ncc.jsonl --pilot 500
    python census_ncc_mss.py --ncc ncc.jsonl --canary
    python census_ncc_mss.py --ncc ncc.jsonl --full   # only after the canary
"""
import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

TAG_RE = re.compile(r'<[^>]+>')
LITERAL_NEWLINE_RE = re.compile(r'\\n')
PAREN_RE = re.compile(r'\([^)]*\)')
SPACE_RE = re.compile(r'\s+')
ROMAN_RE = re.compile(r'^(?=[IVXLCDM]+\.?$)[IVXLCDM]+\.?$')
RANGE_RE = re.compile(r'(?<![\w.])(\d{1,6})\s*[-\u2013]\s*(\d{1,6})(?![\w])')
NUMBER_RE = re.compile(r'(?<![\w.])(\d{1,6}[A-Za-z]?)(?![\w])')
PAGE_RE = re.compile(
    r'\b(?:p{1,2}|pp?)[.]{0,2}\s*\d+(?:\s*[-\u2013]\s*\d+)?[A-Za-z]?'
    r'|\bvol\.?\s*[IVXLCDM]+\.?|\bno\.?\s*\d+', re.I)
YEAR_CONTEXT_RE = re.compile(r'(?:\b(?:A\.?\s?D\.?|C\.?\s?E\.?|ed\.|pub\.|cent\.|c\.)\s*)$', re.I)

# 18 Mahapurana + the two epics = the 20-work canary named in the handoff.
CANARY_WORKS = [
    ('Mahābhārata', 'Mahābhārata', 21),
    ('Rāmāyaṇa', 'Rāmāyaṇa', 2762),
    ('Skandapurāṇa', 'Skandapurāṇa', 17),
    ('Bhāgavata', 'Bhāgavata', 2248),
    ('Viṣṇupurāṇa', 'Viṣṇupurāṇa', None),
    ('Nāradapurāṇa', 'Nāradapurāṇa', None),
    ('Garuḍapurāṇa', 'Garuḍapurāṇa', None),
    ('Padmapurāṇa', 'Padmapurāṇa', None),
    ('Varāhapurāṇa', 'Varāhapurāṇa', None),
    ('Matsyapurāṇa', 'Matsyapurāṇa', None),
    ('Kūrmapurāṇa', 'Kūrmapurāṇa', None),
    ('Liṅgapurāṇa', 'Liṅgapurāṇa', None),
    ('Śivapurāṇa', 'Śivapurāṇa', None),
    ('Agnipurāṇa', 'Agnipurāṇa', None),
    ('Bhaviṣyapurāṇa', 'Bhaviṣyapurāṇa', None),
    ('Brahmavaivartapurāṇa', 'Brahmavaivartapurāṇa', None),
    ('Mārkaṇḍeyapurāṇa', 'Mārkaṇḍeyapurāṇa', None),
    ('Vāmanapurāṇa', 'Vāmanapurāṇa', None),
    ('Brahmāṇḍapurāṇa', 'Brahmāṇḍapurāṇa', None),
    ('Vāyupurāṇa', 'Vāyupurāṇa', None),
]

ALIASES = {
    'Mahābhārata': {'Mahābhārata'},
    'Rāmāyaṇa': {'Rāmāyaṇa'},
    'Skandapurāṇa': {'Skandapurāṇa', 'Skandamahāpurāṇa'},
    'Bhāgavata': {'Bhāgavata', 'Bhāgavatapurāṇa', '(śrī)bhagavatpurāṇa'},
    'Viṣṇupurāṇa': {'Viṣṇupurāṇa'},
    'Nāradapurāṇa': {'Nāradapurāṇa', 'Nāradīyapurāṇa'},
    'Garuḍapurāṇa': {'Garuḍapurāṇa'},
    'Padmapurāṇa': {'Padmapurāṇa'},
    'Varāhapurāṇa': {'Varāhapurāṇa'},
    'Matsyapurāṇa': {'Matsyapurāṇa'},
    'Kūrmapurāṇa': {'Kūrmapurāṇa'},
    'Liṅgapurāṇa': {'Liṅgapurāṇa'},
    'Śivapurāṇa': {'Śivapurāṇa', 'Śivamahāpurāṇa'},
    'Agnipurāṇa': {'Agnipurāṇa', 'Agneyapurāṇa'},
    'Bhaviṣyapurāṇa': {'Bhaviṣyapurāṇa', 'Bhaviṣyatpurāṇa'},
    'Brahmavaivartapurāṇa': {'Brahmavaivartapurāṇa'},
    'Mārkaṇḍeyapurāṇa': {'Mārkaṇḍeyapurāṇa'},
    'Vāmanapurāṇa': {'Vāmanapurāṇa'},
    'Brahmāṇḍapurāṇa': {'Brahmāṇḍapurāṇa'},
    'Vāyupurāṇa': {'Vāyupurāṇa'},
}


def clean_body(raw_html):
    text = LITERAL_NEWLINE_RE.sub(' ', raw_html or '')
    text = TAG_RE.sub(' ', text)
    text = SPACE_RE.sub(' ', text).strip()
    return text


def norm_cat(cat):
    cat = unicodedata.normalize('NFC', cat).strip(' .,')
    cat = SPACE_RE.sub(' ', cat)
    return cat


def cat_key(cat):
    return norm_cat(cat).casefold()


def norm_acc(num):
    m = re.match(r'^(\d+)([A-Za-z]?)$', num)
    if not m:
        return num.lower()
    return str(int(m.group(1))) + m.group(2).lower()


def build_lexicon(rows, vdcs_details_path=None):
    """Catalogue sigla seen in the shipped witness field + VisualDCS keys.

    VisualDCS ``Details`` strings have the shape ``Cat.: 123 { ... }``; only
    the key is used, as an abbreviation table.  No count is copied.
    """
    cats = Counter()
    for r in rows:
        for w in r.get('mss_witnesses') or []:
            m = re.match(r'^(.*?)[\s.]*\d', w)
            if m:
                c = norm_cat(m.group(1))
                if c:
                    cats[c] += 1
    if vdcs_details_path and os.path.exists(vdcs_details_path):
        for key in read_vdcs_detail_keys(vdcs_details_path):
            cats[key] += 1
    # Longest first so "Adyar D." wins over "Adyar".
    return sorted({c for c in cats if 1 < len(c) <= 40}, key=len, reverse=True)


def read_vdcs_detail_keys(xlsx_path):
    """Yield catalogue keys from the Details column of the VisualDCS sheet.

    Deliberately does not read the mss counts -- the workbook is an
    abbreviation source only.
    """
    import zipfile
    import xml.etree.ElementTree as ET
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z = zipfile.ZipFile(xlsx_path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall('m:si', ns):
            ss.append(''.join(t.text or '' for t in si.iter(
                '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')))
    root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    header = None
    for row in root.findall('.//m:row', ns):
        vals = []
        for c in row.findall('m:c', ns):
            v = c.find('m:v', ns)
            if v is None:
                vals.append('')
            elif c.get('t') == 's':
                vals.append(ss[int(v.text)])
            else:
                vals.append(v.text)
        if header is None:
            header = {h: i for i, h in enumerate(vals)}
            continue
        i = header.get('Details')
        if i is None or i >= len(vals):
            continue
        for key in re.findall(r'([^:;{}]+?):\s*\d', vals[i]):
            key = norm_cat(key)
            if 1 < len(key) <= 40:
                yield key


def catalogue_regex(lexicon):
    alts = '|'.join(re.escape(c) for c in lexicon)
    return re.compile(r'(?<![A-Za-zĀ-ſ])(?:' + alts + r')(?![A-Za-zĀ-ſ])')


def _expand_range(start, stop):
    """Expand "1042-48" the catalogue way (stop is an abbreviation)."""
    if stop < start:
        width = len(str(stop))
        base = start - (start % (10 ** width))
        stop = base + stop
        if stop < start:
            stop = start
    if 0 <= stop - start <= 1000:
        return [str(n) for n in range(start, stop + 1)]
    return [str(start), str(stop)]


PREFIX_TOKEN_RE = re.compile(
    r'(?:\s+'
    r'|(?P<roman>[IVXLCDM]+\.)'
    r'|(?P<range>\d{1,6}\s*[-\u2013]\s*\d{1,6})'
    r'|(?P<page>(?:p{1,2}|pp?)[.]{0,2}\s*\d+(?:\s*[-\u2013]\s*\d+)?[A-Za-z]?)'
    r'|(?P<num>\d{1,6}[A-Za-z]?)'
    r'|(?P<punct>[.,;]))'
)


def extract_units(body, cat_re):
    """Extract (catalogue, accession) pairs from one body.

    Only the *prefix* of the text after a catalogue mention is harvested:
    consecutive roman volume markers, accession numbers, ranges, page refs and
    punctuation.  The first ordinary word ends the list, which keeps
    bibliographic prose ("New Delhi, 1991", "ed. by ...") out.
    """
    text = PAREN_RE.sub(' ', clean_body(body))
    matches = list(cat_re.finditer(text))
    units = []
    bare = 0
    if not matches:
        return units, {'mentions': 0, 'no_number_segments': 0}
    for i, m in enumerate(matches):
        before = text[max(0, m.start() - 6):m.start()].strip().lower()
        if before.endswith(('new', 'old')):
            continue
        cat = norm_cat(m.group(0))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        seg = text[m.end():end]
        stripped = seg.lstrip()
        if not stripped or stripped[0] in ',;:':
            bare += 1
            continue
        pos = 0
        got = 0
        while pos < len(seg):
            mm = PREFIX_TOKEN_RE.match(seg, pos)
            if not mm:
                break
            pos = mm.end()
            if mm.group('range'):
                a, b = re.split(r'\s*[-\u2013]\s*', mm.group('range'))
                for n in _expand_range(int(a), int(b)):
                    units.append((cat, n))
                    got += 1
            elif mm.group('num'):
                units.append((cat, mm.group('num')))
                got += 1
        if not got and stripped:
            bare += 1
    stats = {'mentions': len(matches), 'no_number_segments': bare}
    return units, stats


def dedupe(units):
    out = []
    seen = set()
    for cat, acc in units:
        key = (cat_key(cat), norm_acc(acc))
        if key in seen:
            continue
        seen.add(key)
        out.append((norm_cat(cat), norm_acc(acc)))
    return out


def load_rows(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def volume_of(row):
    return row['ncc_id'].split('_')[0]


def pilot_sample(rows, n):
    """Systematic sample over rows sorted by (volume, ncc_id)."""
    ordered = sorted(rows, key=lambda r: (int(volume_of(r)) if volume_of(r).isdigit() else 999,
                                          r['ncc_id']))
    if n >= len(ordered):
        return ordered
    step = len(ordered) / float(n)
    return [ordered[int(i * step)] for i in range(n)]


def run_pilot(rows, cat_re, n, out_path):
    sample = pilot_sample(rows, n)
    stats = Counter()
    per_vol = Counter()
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['ncc_id', 'volume', 'iast', 'mentions', 'raw_units',
                    'distinct_units', 'no_number_segments'])
        for r in sample:
            units, st = extract_units(r['body_html'], cat_re)
            d = dedupe(units)
            per_vol[volume_of(r)] += 1
            stats['entries'] += 1
            stats['mentions'] += st['mentions']
            stats['raw_units'] += len(units)
            stats['distinct_units'] += len(d)
            if not d:
                stats['entries_without_units'] += 1
            w.writerow([r['ncc_id'], volume_of(r), r['iast'], st['mentions'],
                        len(units), len(d), st.get('no_number_segments', 0)])
    stats['volumes'] = len(per_vol)
    stats['sample'] = len(sample)
    return stats


def run_canary(rows, cat_re, out_path, vdcs_path=None):
    by_title = defaultdict(list)
    for r in rows:
        by_title[unicodedata.normalize('NFC', r['iast'])].append(r)
    vdcs = {}
    if vdcs_path and os.path.exists(vdcs_path):
        vdcs = read_vdcs_canary(vdcs_path)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['work', 'entries', 'raw_units', 'distinct_units',
                    'visualdcs_mss', 'delta', 'status'])
        results = []
        for label, title, fallback in CANARY_WORKS:
            titles = ALIASES.get(label, {title})
            hits = []
            for t in titles:
                hits.extend(by_title.get(unicodedata.normalize('NFC', t), []))
            units = []
            for r in hits:
                u, _ = extract_units(r['body_html'], cat_re)
                units.extend(u)
            d = dedupe(units)
            v = vdcs.get(label, fallback)
            if not hits:
                status = 'INCONCLUSIVE (absent from bodies)'
                delta = ''
            elif v is None:
                status = 'COMPARED (no VisualDCS canary)'
                delta = ''
            else:
                delta = len(d) - v
                status = 'DIFF'
            results.append((label, len(hits), len(units), len(d), v, delta, status))
            w.writerow(results[-1])
    return results


def read_vdcs_canary(xlsx_path):
    """Exact-row mss values for the three named VisualDCS canaries."""
    import zipfile
    import xml.etree.ElementTree as ET
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z = zipfile.ZipFile(xlsx_path)
    ss = []
    root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.findall('m:si', ns):
        ss.append(''.join(t.text or '' for t in si.iter(
            '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')))
    root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    header = None
    out = {}
    wanted = {'Mahābhārata': 'Mahābhārata', 'Skandapurāṇa': 'Skandapurāṇa',
              'Rāmāyaṇa': 'Rāmāyaṇa', 'Bhāgavata': 'Bhāgavata'}
    for row in root.findall('.//m:row', ns):
        vals = []
        for c in row.findall('m:c', ns):
            v = c.find('m:v', ns)
            if v is None:
                vals.append('')
            elif c.get('t') == 's':
                vals.append(ss[int(v.text)])
            else:
                vals.append(v.text)
        if header is None:
            header = {h: i for i, h in enumerate(vals)}
            continue
        ti = header.get('IAST')
        mi = header.get('mss')
        if ti is None or mi is None or ti >= len(vals) or mi >= len(vals):
            continue
        label = wanted.get(vals[ti])
        if label and label not in out:
            try:
                out[label] = int(float(vals[mi] or 0))
            except ValueError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ncc', default=os.path.join(HERE, 'ncc.jsonl'))
    ap.add_argument('--vdcs-details',
                    help='VisualDCS counting .xlsx (abbreviation keys only)')
    ap.add_argument('--pilot', type=int, default=0)
    ap.add_argument('--canary', action='store_true')
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--out-dir', default=HERE)
    args = ap.parse_args()

    rows = load_rows(args.ncc)
    lexicon = build_lexicon(rows, args.vdcs_details)
    cat_re = catalogue_regex(lexicon)
    print(f'rows={len(rows)} catalogue_sigla={len(lexicon)}', file=sys.stderr)

    if args.pilot:
        p = os.path.join(args.out_dir, f'ncc_mss_census_pilot_{args.pilot}.tsv')
        st = run_pilot(rows, cat_re, args.pilot, p)
        print(json.dumps(st, ensure_ascii=False), file=sys.stderr)
        print(f'pilot -> {p}', file=sys.stderr)
    if args.canary:
        p = os.path.join(args.out_dir, 'ncc_mss_canary_20.tsv')
        res = run_canary(rows, cat_re, p, args.vdcs_details)
        for r in res:
            print('\t'.join(str(x) for x in r), file=sys.stderr)
        print(f'canary -> {p}', file=sys.stderr)
    if args.full:
        p = os.path.join(args.out_dir, 'ncc_mss_census_full.tsv')
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            w = csv.writer(f, delimiter='\t', lineterminator='\n')
            w.writerow(['ncc_id', 'volume', 'iast', 'distinct_units'])
            for r in rows:
                u, _ = extract_units(r['body_html'], cat_re)
                w.writerow([r['ncc_id'], volume_of(r), r['iast'], len(dedupe(u))])
        print(f'full -> {p}', file=sys.stderr)


if __name__ == '__main__':
    main()
