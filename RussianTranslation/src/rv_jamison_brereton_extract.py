#!/usr/bin/env python
r"""rv_jamison_brereton_extract.py -- the Jamison-Brereton 2014 English RV layer (H1910).

Emits pwg_ru/jamison_brereton_en_2014.json in the SAME envelope shape as the three
VedaWeb translation files and as pwg_ru/griffith_en_1896.json (H1843 step 1), so the
spine builder takes it as a fifth translator with no reshape:

    {meta, contents: [{createdAt, archived, text, location}]}

Source: the archive.org OCR of all three volumes,
`the-rigveda-the-earliest-poetry-of-india-all-3-volume-sets`. It is an INPUT, not an
artifact -- it is never committed. Fetch it with (note `/download/`, NOT `/stream/`,
which returns the viewer page with HTML and an analytics <script> wrapped around the text):

    curl -sL "https://archive.org/download/the-rigveda-the-earliest-poetry-of-india-all-3-volume-sets/The%20Rigveda%20-%20The%20Earliest%20Poetry%20of%20India%20all%203%20Volume%20Sets%20_djvu.txt" \
        -o RussianTranslation/pwg_ru/sources/jb2014_djvu.txt

Why the parser is built the way it is -- three traps, all measured, two of them paid for
in wrong probes before this script existed (H1910):

  1. Hymn headings CANNOT be found by matching roman-numeral patterns. `^[IVX]+\.\d+`
     matches 2,303 lines and they are overwhelmingly cross-references inside running
     prose ("V.84 could be a later composition..."). A parser built on that reconstructs
     767 hymns and 6,986 loci, all of it garbage assembled from citations.
  2. The heading form is not even constant across the three volumes. Mandalas I-II use
     `I.l Agni` (and the OCR renders the digit 1 as lowercase `l`); from III.8 on the
     headings carry the continuous hymn serial, `IV.44(340) Asvins`. That serial runs
     1..1017, not 1..1028, because J-B number the eleven Valakhilya hymns (VIII.49-59)
     separately -- so the serial is recorded, never trusted as a key.
  3. Page furniture is interleaved mid-stanza: a bare page number, and a running head
     that is sometimes arabic (`1.40`), sometimes roman with a page number
     (`VII.79 981`), sometimes a hymn range (`V.72-73 753`).

So segmentation is POSITIONAL and anchored on the canonical hymn sequence, not on the
numbers printed in the book:

  * the canonical hymn order and each hymn's stanza numbers come from the read-only
    VedaWeb lemmatization.json -- the same source of truth the spine uses;
  * a heading only counts if it resolves to a hymn at or after the current position in
    that canonical sequence;
  * within a hymn's line range, stanza markers are matched in REVERSE (n, n-1, ..., 1),
    taking the LAST candidate for each. This is what keeps J-B's per-hymn introductions
    out of the translation column (requirement 3): an introduction sits BEFORE stanza 1,
    so a line-initial "1." inside it is never the last candidate for stanza 1. Forward
    greedy would silently swallow the introduction as the text of stanza 1.

    python rv_jamison_brereton_extract.py                 # build
    python rv_jamison_brereton_extract.py --report-only    # diagnostics, no write
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))


if HERE not in sys.path:
    sys.path.insert(0, HERE)
from rv_org_root import vedaweb_dir  # noqa: E402

LEMMATIZATION = os.path.join(vedaweb_dir(HERE), 'lemmatization.json')
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')
SOURCES_DIR = os.path.join(PWG_RU_DIR, 'sources')
DEFAULT_SOURCE = os.path.join(SOURCES_DIR, 'jb2014_djvu.txt')
OUT_PATH = os.path.join(PWG_RU_DIR, 'jamison_brereton_en_2014.json')
RUN_LOG_DIR = os.path.join(PWG_RU_DIR, 'h1910')
RUN_LOG_PATH = os.path.join(RUN_LOG_DIR, 'jb_extract_run_log.md')

ARCHIVE_IDENT = 'the-rigveda-the-earliest-poetry-of-india-all-3-volume-sets'
ARCHIVE_FILE = 'The Rigveda - The Earliest Poetry of India all 3 Volume Sets _djvu.txt'

ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6,
         'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}

# The OCR confuses the digit 1 with lowercase l inside numbers ("I.l Agni" is I.1).
# Deliberately narrow: only `l`, and only in a slot already known to be a number. A wider
# map (I/i/O/o/S) makes stanza openings like "4. O Indra and Vayu" parse as a locus.
DIGIT_FIX = {'l': '1'}

# A heading is: mandala (roman OR arabic -- the OCR renders `I.2` as `1.2` about as often
# as not), separator, hymn number, an OPTIONAL parenthesised group (the continuous hymn
# serial in vols 2-3, a stanza range in vol 1 -- recorded, never trusted, trap 2), then
# deity/title text that must not be bare digits (that would be a running head with a page
# number, trap 3).
HEAD_RE = re.compile(
    r'^\s*([IVXivxl0-9]{1,4})\s*[\.,]\s*([0-9l]{1,3})\s*'
    r'(?:\(([^)]{1,24})\))?\s*(.*?)\s*$')
STANZA_RE = re.compile(r'^\s*([0-9l]{1,3})\s*\.\s+(\S.*)$')
BACKMATTER_RE = re.compile(
    r'^\s*(BIBLIOGRAPHY|INDEX|ABBREVIATIONS|GLOSSARY|APPENDIX)\b')
# Between the last hymn of a mandala and the first hymn of the next sits a multi-page
# mandala introduction, opening with a lone roman numeral and a `Mandala VIII` header.
MANDALA_HDR_RE = re.compile(r'^\s*Mandala\s*[IVX]{1,4}\s*$')
LONE_ROMAN_RE = re.compile(r'^\s*[IVX]{1,4}\s*$')
# Furniture: a bare page number, or a running head. A running head is recognised by
# whether the WHOLE line denotes a real hymn (see runhead_hymns) rather than by a fixed
# numeral shape -- the OCR mangles these as badly as it mangles headings (`V111.78` is
# VIII.78, `VI.43^4` is VI.43 plus a page number), and 16 stanzas kept a mangled one
# glued to their last word before this was tolerant enough to catch them.
PAGE_RE = re.compile(r'^\s*\d{1,4}\s*$')
RUNHEAD_PARSE_RE = re.compile(
    r'^\s*([IVXivxl0-9]{1,4})\s*[\.,]\s*(\d{1,3})'
    r'(?:\s*[-–—]\s*(\d{1,3}))?'
    r'(?:\s*\^?\s*\d{1,4})?\s*$')
RUNHEAD_TITLE_RE = re.compile(r'^\s*(?:The Rigveda|\d{1,4}\s+The Rigveda)\s*$', re.I)
VERSES_RE = re.compile(r'^\s*([0-9lIiOoS]{1,3})\s+verses?\s*[:;]', re.I)
TERMINAL_PUNCT_RE = re.compile('[.!?;:”’"\'\\)\\]—–-]\\s*$')

# Requirement 3 is CHECKED, not assumed. J-B's editorial register is recognisable by
# scholarly apparatus that never occurs inside a translated stanza: a bibliographic year,
# a named modern scholar, the metre/attribution vocabulary of a heading block, the
# `Mandala N` section header, or the "The next N hymns..." formula that opens a hymn-group
# introduction. This is a DETECTOR for measurement, not a parser -- its count is reported
# honestly rather than used to trim text.
COMMENTARY_RE = re.compile(
    r'\(1[89]\d\d[a-z]?(?::\s*\d)|'
    r'\b(?:Oldenberg|Geldner|Renou|Witzel|Anukraman|Sayana|Bergaigne|Hillebrandt)\b|'
    r'\bMandala\s*[IVX]{1,4}\b|'
    r'\b\d{1,3}\s+verses?\s*[:;]|'
    r'\b(?:attributed to|are ascribed to)\b|'
    r'\bThe next \w+ hymns?\b',
    re.I)


def fix_digits(s):
    return ''.join(DIGIT_FIX.get(ch, ch) for ch in s)


def as_int(s):
    try:
        return int(fix_digits(s))
    except ValueError:
        return None


ROMAN_CANON = {v: k for k, v in ROMAN.items()}


def mandala_readings(token):
    """Every mandala number `token` could denote, 1-10. Trap 2, third form.

    The OCR does not render roman numerals consistently: Mandala I appears as `I` and as
    `1`, and Mandala II appears as `II` and as `11` (`11.1(192) Agni` is II.1). So a token
    is interpreted BOTH ways and the caller -- which knows the next canonical hymn -- picks.
    `11` has only one valid reading (II; there is no Mandala 11), and `10` only one (arabic
    X), so this widens the candidate set without making it ambiguous in practice.
    """
    out = set()
    n = as_int(token)
    if n is not None and 1 <= n <= 10:
        out.add(n)
    roman = token.upper().replace('L', 'I').replace('1', 'I')
    if roman in ROMAN:
        out.add(ROMAN[roman])
    return out


# --------------------------------------------------------------------- canonical
def load_canonical():
    """-> (ordered hymn keys, {(m,h): [stanza numbers in feed order]})."""
    with open(LEMMATIZATION, encoding='utf-8') as f:
        doc = json.load(f)
    hymns = collections.OrderedDict()
    for rec in doc['contents']:
        m, h, s = (int(x) for x in rec['location'].split('.'))
        hymns.setdefault((m, h), []).append(s)
    return list(hymns.keys()), hymns


# ------------------------------------------------------------------- segmentation
HEAD_MAX_LEN = 130
# How far ahead in the canonical sequence a heading may jump. A jump of more than one
# means a heading was missed (OCR damage); allowing it unconditionally is what let prose
# cross-references hijack the walk, so a jump REQUIRES the `N verses: metre` confirmation.
MAX_JUMP = 4
VERSES_LOOKAHEAD = 8


def heading_candidate(lines, i):
    """-> (keys, serial, has_verses_line) if lines[i] can be a hymn heading, else None.

    `keys` is the SET of (mandala, hymn) pairs the line could denote -- see
    mandala_readings() for why more than one reading exists.
    """
    raw = lines[i]
    if len(raw) > HEAD_MAX_LEN or is_furniture(raw):
        return None
    m = HEAD_RE.match(raw)
    if not m:
        return None
    mand_s, hymn_s, serial, rest = m.groups()
    hymn = as_int(hymn_s)
    if hymn is None or not (1 <= hymn <= 191):
        return None
    keys = {(m_, hymn) for m_ in mandala_readings(mand_s)}
    if not keys:
        return None
    rest = rest.strip()
    # Title text is mandatory and must not be a bare page number (a running head, trap 3).
    if not rest or rest.isdigit():
        return None
    # A heading's title opens a word or a bracket -- never punctuation continuing prose.
    # Relaxed when the parenthesised group is a plausible hymn serial: that shape is
    # itself heading-only, and it rescues titles whose first letter the OCR destroyed
    # (`X.151(977) ^raddha` is Sraddha).
    serial_n = as_int(serial) if serial else None
    looks_serial = serial_n is not None and 1 <= serial_n <= 1100
    if not looks_serial and not re.match(r'^[A-Z(\[“"]', rest):
        return None
    has_verses = any(VERSES_RE.match(lines[j])
                     for j in range(i + 1, min(i + 1 + VERSES_LOOKAHEAD, len(lines))))
    return keys, serial, has_verses


def find_headings(lines, hymn_order):
    """Strict next-hymn walk. Returns ([(line_index, (m, h), serial)], diagnostics).

    Anchoring on "at or after the current position" is NOT enough: a forward-pointing
    prose cross-reference ("...as in I.164...") then hijacks the pointer and every hymn
    it skipped is lost. Measured: that reading found 358 of 1,028 headings, because the
    general introduction cites hymns before Mandala I even begins.

    So a candidate is accepted only if it is the NEXT canonical hymn, or -- when a
    heading was genuinely lost to OCR damage -- at most MAX_JUMP ahead AND carrying the
    `N verses: metre` line that only a real heading block has.
    """
    pos_of = {k: i for i, k in enumerate(hymn_order)}
    # Body start: the first heading block for the first canonical hymn that is confirmed
    # by its `N verses:` line. Everything above it is front matter and general
    # introduction -- the region densest in the cross-reference trap.
    start = None
    for i in range(len(lines)):
        cand = heading_candidate(lines, i)
        if cand and hymn_order[0] in cand[0] and cand[2]:
            start = i
            break
    if start is None:
        return [], {'body_start': None, 'rejected': 0, 'jumps': 0}

    out = []
    cur = -1
    rejected = 0
    jumps = 0
    for i in range(start, len(lines)):
        cand = heading_candidate(lines, i)
        if not cand:
            continue
        keys, serial, has_verses = cand
        # Of the readings this line admits, take the one that advances least -- the next
        # hymn if it is among them. A reading may only skip ahead (a heading lost to OCR
        # damage) when the `N verses: metre` line confirms a real heading block.
        best = None
        for key in keys:
            j = pos_of.get(key)
            if j is None:
                continue
            d = j - cur
            if d == 1 or (2 <= d <= MAX_JUMP and has_verses):
                if best is None or d < best[1]:
                    best = (key, d, j)
        if best is None:
            rejected += 1
            continue
        key, d, j = best
        if d > 1:
            jumps += 1
        out.append((i, key, serial))
        cur = j
    return out, {'body_start': start, 'rejected': rejected, 'jumps': jumps}


def segments(headings, body_end, hymn_order):
    """Group the canonical hymns under the heading that opens their line range.

    A heading lost to OCR damage (measured: 9 of 1,028, e.g. `V.IO (364) Agni`,
    `mil (527) Agni`, `m103(619) Frogs`) leaves its hymn with no anchor of its own, so its
    stanzas sit inside the PREVIOUS heading's range. Yields (hymns, start, end, serial)
    with `hymns` in canonical order -- the caller resolves them from the end backwards.

    Widening the heading regex to catch `mil` and `m103` instead is the trap this whole
    parser is built to avoid: those tokens are indistinguishable from running prose, and
    the loosening buys 9 hymns at the cost of an unknown number of false anchors.
    """
    pos_of = {k: i for i, k in enumerate(hymn_order)}
    for k, (i, key, serial) in enumerate(headings):
        end = headings[k + 1][0] if k + 1 < len(headings) else body_end
        lo = pos_of[key]
        hi = pos_of[headings[k + 1][1]] if k + 1 < len(headings) else lo + 1
        yield hymn_order[lo:hi], i, end, serial


def match_stanzas(lines, start, end, expected):
    """Reverse-greedy stanza-marker match over lines[start:end].

    `expected` is the hymn's canonical stanza numbers ascending. Walking backward and
    taking the LAST candidate for each number is what excludes J-B's per-hymn
    introduction (requirement 3) -- see the module docstring.
    """
    cands = []
    for i in range(start, end):
        raw = lines[i]
        if is_furniture(raw):
            continue
        m = STANZA_RE.match(raw)
        if not m:
            continue
        n = as_int(m.group(1))
        if n is not None:
            cands.append((i, n, m.group(2)))

    found = {}
    limit = end
    for n in reversed(expected):
        hit = None
        for i, num, tail in reversed(cands):
            if i >= limit:
                continue
            if num == n:
                hit = (i, tail)
                break
        if hit is None:
            continue
        found[n] = hit
        limit = hit[0]
    return found, len(cands)


# ------------------------------------------------------------------- text cleanup
SOFT_HYPHEN_RE = re.compile(r'[¬-‐‑]\s*$')


def clean_text(chunks, drop_furniture=True):
    """Join OCR lines into one paragraph, repairing end-of-line hyphenation.

    Page furniture is dropped HERE, not only where markers are detected. A stanza that
    spans a page break has the page number and the running head sitting in the middle of
    its own text, and filtering them during detection while joining the raw lines leaves
    them embedded: 1.4.8 ended `... You helped the prizewinner to the prizes. 94 1.5`.
    Measured before the fix: 9.77 %% of stanzas ended without terminal punctuation against
    1.87 %% for the independently-extracted Griffith layer -- the gap was all furniture.
    Filtering before the join also means a word hyphenated across a page break rejoins.

    J-B's printed pada line breaks are NOT recoverable from this OCR: it inserts blank
    lines inside a single printed line as often as between them. So the layer stores one
    normalised paragraph per stanza rather than inventing a line structure. Recorded as a
    known limitation rather than papered over.
    """
    out = []
    for ln in chunks:
        if drop_furniture and is_furniture(ln):
            continue
        ln = ln.strip()
        if not ln:
            continue
        if out and SOFT_HYPHEN_RE.search(out[-1]):
            out[-1] = SOFT_HYPHEN_RE.sub('', out[-1]) + ln
        else:
            out.append(ln)
    text = ' '.join(out)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_furniture(line):
    return bool(PAGE_RE.match(line) or RUNHEAD_TITLE_RE.match(line)
                or runhead_hymns(line))


def runhead_hymns(line):
    """The hymn(s) a running head names, e.g. `1.40` -> {(1,40)}, `V.72-73` -> {(5,72),(5,73)}.

    A running head states which hymn the page is showing. That makes it the one reliable
    signal for the residual case the blank-run rule cannot see: a page break falling
    immediately AFTER a hymn's last stanza, where the furniture is followed by editorial
    prose rather than by more of the stanza. Measured on 3 stanzas (1.57.6, 1.93.12,
    10.70.11) -- e.g. 1.57.6 ran on `... entirely. 174 1.58 The next seven hymns (1.58-64)
    are attributed to Nodhas Gautama...`. The running head says `1.58` while the hymn being
    read is 1.57, so the page has already turned and the hymn's text is over.
    """
    m = RUNHEAD_PARSE_RE.match(line)
    if not m:
        return set()
    lo = as_int(m.group(2))
    hi = as_int(m.group(3)) if m.group(3) else lo
    if lo is None or hi is None or hi < lo:
        return set()
    return {(mand, h) for mand in mandala_readings(m.group(1))
            for h in range(lo, min(hi, 191) + 1)}


def structure_stop(lines, lo, hi, key=None):
    """First line in [lo, hi) that is structural material rather than stanza text.

    Only the LAST stanza of a hymn needs this. Its text would otherwise run to the next
    anchor, swallowing everything between the hymn's end and that anchor. Three kinds of
    trailing material were measured doing exactly that, all of them requirement-3
    violations (J-B commentary inside the translation column) and all of them invisible to
    a locus count -- 10,552/10,552 held while every one of them was present:

      * the next hymn's whole heading block, whenever that heading was the one the OCR
        destroyed (8 hymns; 7.102.3 ended `... 1012 V11.103 m103(619) Frogs Vasistha ...`);
      * the multi-page `Mandala VIII` section introduction at a mandala boundary
        (9 stanzas; 7.104.25 ended `... VIII MandalaVIII Mandala`);
      * a hymn-GROUP introduction, which carries no heading and no metre line at all
        (1.11.8 ended `... 1.12-23 are attributed to Medhatithi Kanva, ...`).

    The third kind has no keyword that reliably marks it, so the cut is typographic, and
    the typography was measured rather than assumed: J-B pada lines within a stanza are
    separated by exactly ONE blank line, while every block boundary -- stanza to editorial
    paragraph, paragraph to heading -- is TWO. The sole within-stanza exception is a page
    break, whose blank region always contains a page number or a running head, so it is
    identifiable and skipped instead of being treated as a boundary.
    """
    i = lo
    while i < hi:
        raw = lines[i]
        if (VERSES_RE.match(raw) or BACKMATTER_RE.match(raw)
                or MANDALA_HDR_RE.match(raw) or LONE_ROMAN_RE.match(raw)):
            return i
        if heading_candidate(lines, i):
            return i
        if raw.strip() and not is_furniture(raw):
            i += 1
            continue
        # A maximal blank/furniture region: two or more blank lines with no page furniture
        # in them is a block boundary; anything containing furniture is a page break.
        j = i
        blanks = 0
        has_furniture = False
        page_turned = False
        while j < hi and (not lines[j].strip() or is_furniture(lines[j])):
            if lines[j].strip():
                has_furniture = True
                named = runhead_hymns(lines[j])
                if key is not None and named and key not in named:
                    page_turned = True
            else:
                blanks += 1
            j += 1
        if page_turned or (blanks >= 2 and not has_furniture):
            return i
        i = max(j, i + 1)
    return hi


# ------------------------------------------------------------------------- build
def build(lines, hymn_order, hymn_stanzas):
    headings, diag = find_headings(lines, hymn_order)
    skipped_back = diag['rejected']
    body_end = len(lines)
    if headings:
        # The back matter (bibliography, then an index of hymns whose entries look exactly
        # like `V.5 Aprl` headings) follows the last hymn. Bound the last hymn on the first
        # back-matter header, or the whole tail is swallowed into 10.191's last stanza.
        for i in range(headings[-1][0], len(lines)):
            if BACKMATTER_RE.match(lines[i]):
                body_end = i
                break

    records = []
    per_hymn = {}
    gap_filled = []
    for hymns, start, end, serial in segments(headings, body_end, hymn_order):
        # Resolve the hymns sharing this range from the LAST one backwards, each bounded
        # above by the first marker of the hymn after it. Same reverse-greedy discipline
        # as within a hymn, one level up.
        limit = end
        resolved = []
        for key in reversed(hymns):
            expected = sorted(hymn_stanzas[key])
            found, n_cands = match_stanzas(lines, start, limit, expected)
            resolved.append((key, found, n_cands, limit))
            if found:
                limit = min(v[0] for v in found.values())
        for key, found, n_cands, hi in reversed(resolved):
            per_hymn[key] = {
                'serial': serial if key == hymns[0] else None,
                'expected': len(sorted(hymn_stanzas[key])), 'found': len(found),
                'candidates': n_cands, 'start': start, 'end': hi,
                'gap_filled': key != hymns[0],
            }
            if key != hymns[0]:
                gap_filled.append(key)
            marks = sorted(found.items(), key=lambda kv: kv[1][0])
            for idx, (n, (line_i, tail)) in enumerate(marks):
                if idx + 1 < len(marks):
                    stop = marks[idx + 1][1][0]
                else:
                    stop = structure_stop(lines, line_i + 1, hi, key)
                body = [ln for ln in lines[line_i + 1:stop] if not is_furniture(ln)]
                # `tail` is what followed the stanza marker on its own line, so it is
                # stanza text by construction and is never furniture-filtered.
                text = clean_text([tail] + body, drop_furniture=False)
                if not text:
                    continue
                records.append({
                    'createdAt': '0001-01-01 00:00:00+00:00',
                    'archived': False,
                    'text': text,
                    'location': '%d.%d.%d' % (key[0], key[1], n),
                })
    records.sort(key=lambda r: [int(p) for p in r['location'].split('.')])
    stats = {
        'headings': len(headings),
        'heading_candidates_rejected_backward': skipped_back,
        'hymns_seen': len(per_hymn),
        'body_end': body_end,
        'gap_filled_hymns': gap_filled,
    }
    return records, per_hymn, stats


def report(records, per_hymn, stats, hymn_order, hymn_stanzas):
    canonical = {'%d.%d.%d' % (m, h, s)
                 for (m, h), ss in hymn_stanzas.items() for s in ss}
    got = {r['location'] for r in records}
    missing = sorted(canonical - got, key=lambda x: [int(p) for p in x.split('.')])
    extra = sorted(got - canonical, key=lambda x: [int(p) for p in x.split('.')])
    missing_hymns = [k for k in hymn_order if k not in per_hymn]
    short = {k: v for k, v in per_hymn.items() if v['found'] != v['expected']}

    print('headings anchored:            %d / %d canonical hymns' % (
        stats['headings'], len(hymn_order)))
    print('heading candidates rejected (backward/out of sequence): %d'
          % stats['heading_candidates_rejected_backward'])
    print('hymns with no heading of their own, resolved positionally inside the '
          'previous heading\'s range: %d %s'
          % (len(stats['gap_filled_hymns']), stats['gap_filled_hymns'][:12]))
    print('hymns not placed at all:      %d %s' % (
        len(missing_hymns), missing_hymns[:12]))
    print('hymns short of their canonical stanza count: %d' % len(short))
    for k in sorted(short)[:15]:
        v = short[k]
        print('    %2d.%-3d expected %3d found %3d (%d candidates, L%d-%d)'
              % (k[0], k[1], v['expected'], v['found'], v['candidates'],
                 v['start'], v['end']))
    print('stanzas extracted:            %d / %d canonical loci'
          % (len(records), len(canonical)))
    print('unmatched (missing) loci:     %d' % len(missing))
    print('  first 20: %s' % missing[:20])
    print('loci outside the canonical set: %d %s' % (len(extra), extra[:10]))
    dupes = [loc for loc, c in collections.Counter(
        r['location'] for r in records).items() if c > 1]
    print('duplicate loci:               %d %s' % (len(dupes), sorted(dupes)[:10]))
    empties = [r['location'] for r in records if not r['text'].strip()]
    print('empty texts:                  %d' % len(empties))
    lens = sorted(len(r['text']) for r in records)
    if lens:
        print('text length: min %d  p05 %d  median %d  p95 %d  max %d'
              % (lens[0], lens[len(lens) // 20], lens[len(lens) // 2],
                 lens[len(lens) * 19 // 20], lens[-1]))
    leaks = [r['location'] for r in records if COMMENTARY_RE.search(r['text'])]
    print('commentary leaks (requirement 3): %d %s' % (len(leaks), leaks[:12]))
    # Embedded page furniture is invisible to every count above -- it neither adds nor
    # removes a locus. It shows up as text that stops without terminal punctuation, so
    # that rate is reported next to the independently-extracted Griffith layer as control
    # (Griffith: 1.87 %). A J-B rate far above it means furniture is still in the text.
    open_ended = [r['location'] for r in records
                  if r['text'] and not TERMINAL_PUNCT_RE.search(r['text'])]
    print('no terminal punctuation: %d (%.2f%%) -- griffith control 1.87%%'
          % (len(open_ended), 100.0 * len(open_ended) / max(1, len(records))))
    furniture_tail = [r['location'] for r in records
                      if re.search(r'\b\d{2,4}\s+\d{1,2}\.\d{1,3}\s*$', r['text'])
                      or re.search(r'\b\d{1,2}\.\d{1,3}\s+\d{2,4}\s*$', r['text'])]
    print('text ending in page/running-head furniture: %d %s'
          % (len(furniture_tail), furniture_tail[:8]))
    return missing, extra, dupes, short, missing_hymns, leaks, furniture_tail


def main():
    ap = argparse.ArgumentParser(description='J-B 2014 RV English layer (H1910)')
    ap.add_argument('--source', default=os.environ.get('JB2014_OCR') or DEFAULT_SOURCE)
    ap.add_argument('--report-only', action='store_true')
    ap.add_argument('--dump-missing', action='store_true',
                    help='print the locus-looking lines in the range where each '
                         'undetected hymn heading should be')
    a = ap.parse_args()

    if not os.path.exists(a.source):
        sys.exit(
            'source OCR not found: %s\nIt is an input, never committed. Fetch it with the '
            'curl command in this script\'s docstring (use /download/, not /stream/).'
            % a.source)

    with open(a.source, encoding='utf-8') as f:
        lines = f.read().split('\n')

    hymn_order, hymn_stanzas = load_canonical()
    total_canonical = sum(len(v) for v in hymn_stanzas.values())
    print('canonical: %d hymns, %d stanzas' % (len(hymn_order), total_canonical))
    print('source: %s (%d lines)' % (a.source, len(lines)))

    records, per_hymn, stats = build(lines, hymn_order, hymn_stanzas)
    missing, extra, dupes, short, missing_hymns, leaks, furniture_tail = report(
        records, per_hymn, stats, hymn_order, hymn_stanzas)
    gates_ok = not (missing or extra or dupes or leaks or furniture_tail)

    if a.dump_missing:
        loc_like = re.compile(r'\d\s*[\.,]\s*\d')
        for key in missing_hymns:
            prev = [k for k in hymn_order if k in per_hymn
                    and hymn_order.index(k) < hymn_order.index(key)]
            if not prev:
                continue
            lo = per_hymn[prev[-1]]['start']
            hi = per_hymn[prev[-1]]['end']
            print('\n=== %d.%d missing; scanning L%d-%d (range of %d.%d) ===' % (
                key[0], key[1], lo, hi, prev[-1][0], prev[-1][1]))
            shown = 0
            for i in range(lo, hi):
                s = lines[i].strip()
                if not s or len(s) > 62 or STANZA_RE.match(lines[i]):
                    continue
                if PAGE_RE.match(lines[i]):
                    continue
                print('  L%-7d %r' % (i, s[:90]))
                shown += 1
                if shown >= 26:
                    break
        return 0

    if a.report_only:
        return 0 if gates_ok else 1

    envelope = {
        'meta': {
            'author': 'Stephanie W. Jamison and Joel P. Brereton',
            'year': '2014',
            'language': 'en',
            'title': 'The Rigveda: The Earliest Religious Poetry of India',
            'publisher': 'Oxford University Press',
            'provenance': (
                'extracted by rv_jamison_brereton_extract.py (H1910) from the archive.org '
                'OCR %s, file %r; stanza segmentation anchored on the VedaWeb canonical '
                'hymn sequence, per-hymn introductions and notes excluded'
                % (ARCHIVE_IDENT, ARCHIVE_FILE)),
            'known_limitations': (
                "printed pada line breaks are not recoverable from this OCR (it inserts "
                "blank lines within a printed line as often as between them), so each "
                "stanza is stored as one normalised paragraph"),
        },
        'contents': records,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('wrote %s' % OUT_PATH)

    os.makedirs(RUN_LOG_DIR, exist_ok=True)
    with open(RUN_LOG_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Jamison-Brereton 2014 extraction run log (H1910)\n\n')
        f.write('_Created: 30-07-2026 · Last updated: 30-07-2026_\n\n')
        f.write('- source: archive.org `%s`, `%s`\n' % (ARCHIVE_IDENT, ARCHIVE_FILE))
        f.write('- source lines: %d\n' % len(lines))
        f.write('- canonical hymns / stanzas: %d / %d\n'
                % (len(hymn_order), total_canonical))
        f.write('- headings anchored: %d\n' % stats['headings'])
        f.write('- heading candidates rejected as backward/out-of-sequence '
                '(the prose cross-reference trap): %d\n'
                % stats['heading_candidates_rejected_backward'])
        f.write('- stanzas extracted: %d\n' % len(records))
        f.write('- unmatched loci: %d\n' % len(missing))
        f.write('- loci outside the canonical set: %d\n' % len(extra))
        f.write('- duplicate loci: %d\n' % len(dupes))
        f.write('- hymns short of their canonical stanza count: %d\n' % len(short))
        gap = stats['gap_filled_hymns']
        f.write('- hymns with no heading of their own, resolved positionally inside the '
                'previous heading\'s range: %d%s\n'
                % (len(gap),
                   ' (%s)' % ', '.join('%d.%d' % k for k in gap) if gap else ''))
        f.write('- commentary leaks (requirement 3, J-B introductions/notes inside a '
                'stanza): %d\n' % len(leaks))
        f.write('- stanzas ending in page/running-head furniture: %d\n'
                % len(furniture_tail))
        if missing:
            f.write('\n## Unmatched loci\n\n')
            for loc in missing[:200]:
                f.write('- %s\n' % loc)
            if len(missing) > 200:
                f.write('- ... %d more\n' % (len(missing) - 200))
        f.write('\n_Dr. Mārcis Gasūns_\n')
    print('wrote %s' % RUN_LOG_PATH)
    return 0 if gates_ok else 1


if __name__ == '__main__':
    sys.exit(main())
