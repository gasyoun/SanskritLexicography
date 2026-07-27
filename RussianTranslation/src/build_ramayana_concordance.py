#!/usr/bin/env python
r"""Rāmāyaṇa recension concordances — Southern↔Critical (verse level) and
Gorresio↔Southern (sarga level, structural DRAFT) (H1656).

MG ruled (weekly @DECIDE sheet 20-07-2026, applied 21-07-2026): option (а) —
commission the Gorresio↔Southern concordance; «NEVER propose to skip» citation
reuse. This module builds the two maps the R./R. GORR. citation-reuse path
needs, WITHOUT flipping the resolver: per the H1656 title, **R. GORR. stays
`unmapped_locus_scheme` in `citation_tm.py` until the map validates** (content-
level validation gate documented in `pwg_ru/COVERED_TEXTS_RU.md` § R. GORR.).

THREE recensions, three keyings:

  Southern  — the Leonov/Gryntser translation-of-record keying: SamudraManthanam
              corpus `0X_ramayana-*kanda.jsonl`, vulgate sarga.verse numbering
              (kāṇḍa 4 kiṣkindhā not ingested).
  Critical  — Baroda Critical Edition numbering as carried by the DCS
              (`dcs_full.sqlite`, text_id 143, refs `Rām, <Kāṇḍa>, <sarga>`).
  Gorresio  — Gauḍīya (Bengal) recension, ed. Gorresio 1843–1867; NO clean
              e-text exists (scans + rough OCR only). Its complete structural
              inventory (kāṇḍa → sarga → verse count → volume/page) is
              recovered from the Cologne scan-viewer page index
              (sanskrit-lexicon-scans/ramayanagorr `ksverse.js`,
              commit 609a2866, 2022-03-18) — the same index that already powers
              the per-verse page links `ls_resolver.py` emits for R. GORR.

Outputs (committed, metadata only — loci, counts, scores; never translation text):

  src/ramayana_southern_critical_concordance.tsv
      verse-level, CONTENT-BASED: char-n-gram similarity + per-kāṇḍa monotonic
      anchoring (LIS). Columns: s_kanda s_sarga s_verse c_kanda c_sarga c_verse
      score class;  class ∈ matched | fuzzy | moved | southern_only.
  src/ramayana_gorresio_inventory.tsv
      Gorresio structural inventory: kanda sarga n_verses volume page_first
      page_last (from ksverse.js; no OCR involved).
  src/gorresio_etext.jsonl
      the Gorresio e-text (IAST). Vols 1/3/5 (Bāla, Ayodhyā sargas 1–9,
      Āraṇya, Kiṣkindhā-part, Yuddha): recovered 26-07-2026 from the Cologne
      page PDFs' embedded Google text layer — the "no OCR exists" premise was
      wrong. Vols 2/4/uk (Ayodhyā 10–127, Kiṣkindhā-tail + Sundara, Uttara):
      image-only scans, OCRed 26-07-2026 with tesseract 5.5 `san` at full
      embedded-image resolution (H1689) — same accuracy class as the Google
      layer for the n-gram consumer here.
  src/ramayana_gorresio_southern_verse_map.tsv
      verse-level, CONTENT-BASED Gorresio↔Southern concordance over the
      e-text. class ∈ matched | fuzzy | moved | gorresio_only |
      no_southern_corpus. `matched`/`fuzzy` key citation reuse in
      citation_tm (reuse ON per MG 26-07-2026); `moved` deliberately does
      not (formulaic-repeat error class per the H783 cross-validation).
  src/ramayana_gorresio_southern_sarga_map.tsv
      sarga-level majority roll-up of the verse map (CONTENT-BASED; owned by
      `build-gorresio`). The original content-blind DTW draft was superseded
      26-07-2026 — scan-anchor checks showed ±1–3-sarga drift.
  src/ramayana_bombay_inventory.tsv
      Bombay (Gujarātī Printing Press, 1859) structural inventory — the
      edition PWG's plain `R.` cites for book 7: kāṇḍa → sarga → verse count →
      volume/page span, read off the ramayanabom scan-viewer per-page index
      (NO OCR involved, same shape as the Gorresio inventory). Built by
      `build-bombay`, which also emits the Bombay↔corpus numbering study that
      decided H1705.

Build (needs the LOCAL-ONLY stores; absent in CI by design):

  python src/build_ramayana_concordance.py build \
      [--corpus-dir <SamudraManthanam>/web/corpus_builder/jsonl] \
      [--dcs-sqlite <VisualDCS>/src/DCS-data-2026/dcs_full.sqlite] \
      [--ksverse <path to ksverse.js>]
  python src/build_ramayana_concordance.py build-gorresio \
      --pdf-dir <ramayanagorr clone>/pdfpages --ksverse <ksverse.js> \
      [--corpus-dir ...] [--cache <page_texts.jsonl>]
  python src/build_ramayana_concordance.py build-bombay \
      --index-dir <ramayanabom clone>/app1/pywork [--corpus-dir ...]

Selftest (CI gate — validates the COMMITTED TSVs only, no stores, no network):

  python src/build_ramayana_concordance.py selftest
"""
import argparse
import bisect
import csv
import json
import os
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CORPUS_DIR = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'SamudraManthanam', 'web', 'corpus_builder', 'jsonl'))
DEFAULT_DCS_SQLITE = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'VisualDCS', 'src', 'DCS-data-2026', 'dcs_full.sqlite'))

OUT_SC = os.path.join(HERE, 'ramayana_southern_critical_concordance.tsv')
OUT_GINV = os.path.join(HERE, 'ramayana_gorresio_inventory.tsv')
OUT_GS = os.path.join(HERE, 'ramayana_gorresio_southern_sarga_map.tsv')
OUT_GETEXT = os.path.join(HERE, 'gorresio_etext.jsonl')
OUT_GSV = os.path.join(HERE, 'ramayana_gorresio_southern_verse_map.tsv')
OUT_BINV = os.path.join(HERE, 'ramayana_bombay_inventory.tsv')

# Southern corpus file → kāṇḍa number; kāṇḍa 4 (kiṣkindhā) is not ingested.
SOUTHERN_FILES = {
    1: '01_ramayana-balakanda.jsonl',
    2: '02_ramayana-ayodhyakanda.jsonl',
    3: '03_ramayana-aranyakanda.jsonl',
    5: '05_ramayana-sundarakanda.jsonl',
    6: '06_ramayana-yuddhakanda.jsonl',
    7: '07_ramayana-uttarakanda.jsonl',
}
# DCS chapter-ref kāṇḍa token → kāṇḍa number.
DCS_KANDA = {'Bā': 1, 'Ay': 2, 'Ār': 3, 'Ki': 4, 'Su': 5, 'Yu': 6, 'Utt': 7}

KSVERSE_COMMIT = '609a28669e3d8f4648a153c7af0105f3dca03ead'  # provenance pin
# sanskrit-lexicon-scans/ramayanabom @ app1/pywork/indexv{1,2,3}.txt — the
# hand-made per-page index for the Bombay ed. (PWG's `R.` book 7). Pin the
# commit that last touched those files, not HEAD.
BOMINDEX_COMMIT = '841764ad48e13ed3db998b32f1a8dcc1b1787750'
# `app1/pywork/index.txt` in that repo is NOT the Rāmāyaṇa index — it is
# Śatapatha-brāhmaṇa template residue (14 kāṇḍas, brāhmaṇa/kaṇḍikā columns)
# left over from the app it was cloned from. Read indexv1/2/3 only.
BOMINDEX_FILES = ('indexv1.txt', 'indexv2.txt', 'indexv3.txt')

# Verse-map pairs voted OFF in the 26-07-2026 human audit sheet
# (review/sanskritlexicography-gorresio-southern-map_audit-26-07-26_decisions.json,
# 4 half-verse-shift pairs). build-gorresio re-applies them so a rebuild never
# silently resurrects a rejected pair; keyed by the FULL pair — if a rebuild
# maps the Gorresio verse to a different Southern verse, the old veto does not
# apply and the new pair goes back to a human sheet instead.
AUDIT_REJECTED_PAIRS = {
    (1, 12, 28, 1, 13, 33),
    (1, 48, 11, 1, 47, 8),
    (1, 62, 8, 1, 60, 7),
    (2, 4, 7, 2, 5, 7),
}

MATCH_HI = 0.50   # class 'matched' (same verse, minor recension variance)
MATCH_LO = 0.35   # class 'fuzzy' floor


def norm(text):
    """Diacritic-folded lowercase letter string for cross-recension matching."""
    text = unicodedata.normalize('NFD', text.lower())
    return ''.join(c for c in text if 'a' <= c <= 'z')


def grams(s, n=4):
    return {s[i:i + n] for i in range(len(s) - n + 1)}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_southern(corpus_dir):
    """{kanda: [(sarga, verse, normtext), ...]} in corpus order."""
    out = {}
    for kanda, fname in SOUTHERN_FILES.items():
        path = os.path.join(corpus_dir, fname)
        rows = []
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                r = json.loads(line)
                if r.get('seg') != 'sa' or r.get('deleted'):
                    continue
                m = re.match(r'^(\d+)\.(\d+)$', r['passage'])
                if not m:
                    continue
                rows.append((int(m.group(1)), int(m.group(2)), norm(r['text'])))
        rows.sort(key=lambda t: (t[0], t[1]))
        out[kanda] = rows
    return out


def load_critical(dcs_sqlite):
    """{kanda: [(sarga, verse, normtext), ...]} from DCS text_id=143."""
    con = sqlite3.connect(dcs_sqlite)
    cur = con.cursor()
    cur.execute("SELECT chapter_id, ref FROM chapter WHERE text_id=143")
    chapters = {}
    for chap_id, ref in cur.fetchall():
        m = re.match(r'^Rām, ([^,]+), (\d+)$', ref)
        if m and m.group(1) in DCS_KANDA:
            chapters[chap_id] = (DCS_KANDA[m.group(1)], int(m.group(2)))
    verses = defaultdict(list)  # (kanda, sarga, verse) -> [text parts]
    cur.execute(
        "SELECT chapter_id, sent_counter, sent_subcounter, text_sandhied "
        "FROM sentence WHERE chapter_id IN (%s) "
        "ORDER BY chapter_id, sent_counter, sent_subcounter"
        % ','.join(str(c) for c in chapters))
    for chap_id, counter, sub, text in cur.fetchall():
        if counter is None:        # unnumbered line (colophon etc.) — no locus
            continue
        kanda, sarga = chapters[chap_id]
        verses[(kanda, sarga, int(counter))].append(text or '')
    con.close()
    out = defaultdict(list)
    for (kanda, sarga, verse), parts in sorted(verses.items()):
        out[kanda].append((sarga, verse, norm(' '.join(parts))))
    return dict(out)


def load_gorresio_inventory(ksverse_path):
    """[(kanda, sarga, n_verses, volume, page_first, page_last), ...]"""
    src = open(ksverse_path, encoding='utf-8').read()
    src = src.split('=', 1)[1].strip().rstrip(';')
    src = re.sub(r'([{,]\s*)(\d+)(\s*):', r'\1"\2"\3:', src)   # quote int keys
    src = re.sub(r',(\s*[}\]])', r'\1', src)                   # trailing commas
    data = json.loads(src)
    rows = []
    for kanda, sargas in data.items():
        for sarga, blocks in sargas.items():
            n = max(b['v2'] for b in blocks)
            vol = blocks[0]['v']
            pages = [b['page'] for b in blocks]
            rows.append((int(kanda), int(sarga), n, vol, min(pages), max(pages)))
    rows.sort(key=lambda t: (t[0], t[1]))
    return rows


# ---------------------------------------------------------------------------
# Bombay (1859) structural inventory — from the scan-viewer per-page index
# ---------------------------------------------------------------------------

# The uttarakāṇḍa's LAST sarga is typed `11` in indexv3.txt where 111 is meant:
# it follows sarga 110, restarts its verse numbering at 1, and sits at pages
# 810-812 — while the real sarga 11 sits ~280 pages earlier. Page 810's colophon
# reads `इत्यार्षे … दशाधिकशततमः सर्गः ॥ ११० ॥` and the mūla under it restarts at
# ॥१॥, so the block below it is the 111th and last. Repaired here EXPLICITLY (the
# TSV marks the row `index_typo_111`) rather than silently, and asserted in
# selftest: a duplicate sarga id with a disjoint page span is the detector.
# (kāṇḍa, typed sarga, page_lo, page_hi) -> (corrected sarga, flag)
BOM_INDEX_REPAIRS = {(7, '11', 800, 899): ('111', 'index_typo_111')}


def _bom_repair(kanda, sarga, page):
    for (k, s, lo, hi), fix in BOM_INDEX_REPAIRS.items():
        if (k, s) == (kanda, sarga) and lo <= page <= hi:
            return fix
    return None


def _bom_int(tok):
    m = re.match(r'^(\d+)', (tok or '').strip())
    return int(m.group(1)) if m else None


def load_bombay_inventory(index_dir):
    """[(kanda, sarga, n_verses, volume, page_first, page_last, ipage_first,
        ipage_last, flags), ...] from ramayanabom's indexv{1,2,3}.txt.

    Columns are `vol page kāṇḍa sarga from-v. to-v. ipage remark(s)`; `---`
    marks an unnumbered/missing page. `sarga` is a STRING because the Bombay ed.
    prints interpolated sargas as `23.1 … 23.5`, `37.1 … 37.5`, `59.1 … 59.3` —
    numbering PWG's `R. 7,<sarga>,<verse>` cannot address at all.
    """
    per = {}
    for fname in BOMINDEX_FILES:
        path = os.path.join(index_dir, fname)
        if not os.path.exists(path):
            sys.exit('%s not found in %s (ramayanabom clone @ %s)'
                     % (fname, index_dir, BOMINDEX_COMMIT[:8]))
        with open(path, encoding='utf-8') as fh:
            next(fh)                                   # header
            for line in fh:
                p = line.rstrip('\n').split('\t')
                if len(p) < 7 or not p[2].strip().isdigit():
                    continue                           # front matter / blank pages
                vol, page = p[0].strip(), _bom_int(p[1])
                kanda, sarga = int(p[2]), p[3].strip()
                if page is None or not sarga or sarga == '---':
                    continue
                repaired = _bom_repair(kanda, sarga, page)
                if repaired:
                    sarga = repaired[0]
                d = per.setdefault((kanda, sarga), {
                    'vol': vol, 'n': 0, 'pages': [], 'ipages': [],
                    'flags': set()})
                for v in (_bom_int(p[4]), _bom_int(p[5])):
                    if v and v > d['n']:
                        d['n'] = v
                d['pages'].append(page)
                if p[6].strip() and p[6].strip() != '---':
                    d['ipages'].append(p[6].strip())
                if '.' in sarga:
                    d['flags'].add('interpolated')
                if repaired:
                    d['flags'].add(repaired[1])
    rows = []
    for (kanda, sarga), d in per.items():
        rows.append((kanda, sarga, d['n'], d['vol'],
                     min(d['pages']), max(d['pages']),
                     d['ipages'][0] if d['ipages'] else '',
                     d['ipages'][-1] if d['ipages'] else '',
                     ','.join(sorted(d['flags']))))
    rows.sort(key=lambda t: (t[0], [int(x) for x in t[1].split('.')]))
    return rows


def cmd_build_bombay(args):
    """Bombay inventory + the Bombay↔corpus numbering study (H1705).

    NO OCR: the whole verdict rests on the hand-made per-page index and the
    corpus's own verse numbering. The e-text route is deliberately NOT taken —
    see pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md for why
    (no Russian uttarakāṇḍa exists to reuse, so a concordance has no consumer).
    """
    rows = load_bombay_inventory(args.index_dir)
    with open(OUT_BINV, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(['kanda', 'sarga', 'n_verses', 'volume',
                    'page_first', 'page_last', 'ipage_first', 'ipage_last',
                    'flags'])
        w.writerows(rows)
    per_kanda = defaultdict(int)
    for r in rows:
        per_kanda[r[0]] += 1
    print('bombay inventory: %d sargas -> %s' % (len(rows), OUT_BINV))
    print('  sargas per kāṇḍa: %s' % dict(sorted(per_kanda.items())))

    if not os.path.exists(args.corpus_dir):
        print('corpus dir absent — numbering study skipped')
        return
    corpus = load_southern(args.corpus_dir)
    bom7 = {r[1]: r[2] for r in rows if r[0] == 7 and 'interpolated' not in r[8]}
    cor7 = defaultdict(int)
    for sarga, verse, _ in corpus.get(7, []):
        cor7[sarga] = max(cor7[sarga], verse)
    bom_int = {int(s): n for s, n in bom7.items()}
    both = sorted(set(bom_int) & set(cor7))
    same = [s for s in both if bom_int[s] == cor7[s]]
    print()
    print('=== Bombay ↔ corpus numbering study, kāṇḍa 7 ===')
    print('bombay sargas      : %d (+%d interpolated)'
          % (len(bom_int), sum(1 for r in rows
                               if r[0] == 7 and 'interpolated' in r[8])))
    print('corpus sargas      : %d' % len(cor7))
    print('bombay-only sargas : %s' % sorted(set(bom_int) - set(cor7)))
    print('identical verse count: %d/%d (%.1f%%)'
          % (len(same), len(both), 100.0 * len(same) / len(both) if both else 0))
    deltas = [bom_int[s] - cor7[s] for s in both]
    if deltas:
        print('delta bombay-corpus : min %+d  max %+d  mean %+.1f'
              % (min(deltas), max(deltas), sum(deltas) / len(deltas)))
    print('VERDICT: the two numberings are NOT ≈1:1 — a direct-with-offset '
          'scheme would be dishonest (H1705).')


# ---------------------------------------------------------------------------
# Southern ↔ Critical verse alignment
# ---------------------------------------------------------------------------

def align_kanda(southern, critical, shingle=12, step=4,
                match_lo=MATCH_LO, match_hi=MATCH_HI):
    """Content-based monotonic alignment inside one kāṇḍa. `shingle`/`step`
    control candidate retrieval — use shorter shingles (8/2) when one side is
    OCR-derived, where long exact runs are rarer."""
    index = defaultdict(set)
    cgrams = []
    for ci, (_, _, text) in enumerate(critical):
        cgrams.append(grams(text))
        # index EVERY offset (step 1): a strided index misses shared runs whose
        # relative shift between the two texts is off-phase with the stride
        for i in range(0, max(1, len(text) - shingle + 1)):
            index[text[i:i + shingle]].add(ci)
    pairs = []  # (si, ci, score)
    for si, (_, _, text) in enumerate(southern):
        hits = defaultdict(int)
        for i in range(0, max(1, len(text) - shingle + 1), step):
            for ci in index.get(text[i:i + shingle], ()):
                hits[ci] += 1
        if not hits:
            continue
        sg = grams(text)
        best_ci, best_score = -1, 0.0
        for ci in sorted(hits, key=hits.get, reverse=True)[:8]:
            inter = len(sg & cgrams[ci])
            union = len(sg | cgrams[ci])
            score = inter / union if union else 0.0
            if score > best_score:
                best_ci, best_score = ci, score
        if best_score >= match_lo:
            pairs.append((si, best_ci, best_score))
    # Monotonic backbone: LIS on ci over pairs sorted by si (strict order).
    tails, tails_idx, parent = [], [], [-1] * len(pairs)
    for pi, (si, ci, score) in enumerate(pairs):
        pos = bisect.bisect_left(tails, ci)
        if pos == len(tails):
            tails.append(ci); tails_idx.append(pi)
        else:
            tails[pos] = ci; tails_idx[pos] = pi
        parent[pi] = tails_idx[pos - 1] if pos > 0 else -1
    on_lis = set()
    pi = tails_idx[-1] if tails_idx else -1
    while pi != -1:
        on_lis.add(pi); pi = parent[pi]
    rows = []
    matched_si = {}
    for pi, (si, ci, score) in enumerate(pairs):
        if pi in on_lis:
            cls = 'matched' if score >= match_hi else 'fuzzy'
        elif score >= match_hi:
            cls = 'moved'
        else:
            continue
        matched_si[si] = (ci, score, cls)
    for si, (s_sarga, s_verse, _) in enumerate(southern):
        if si in matched_si:
            ci, score, cls = matched_si[si]
            c_sarga, c_verse, _ = critical[ci]
            rows.append((s_sarga, s_verse, c_sarga, c_verse, round(score, 3), cls))
        else:
            rows.append((s_sarga, s_verse, '', '', '', 'southern_only'))
    return rows


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_build(args):
    ksverse = args.ksverse
    if not ksverse or not os.path.exists(ksverse):
        sys.exit('ksverse.js not found — pass --ksverse (fetch from '
                 'sanskrit-lexicon-scans/ramayanagorr @ %s)' % KSVERSE_COMMIT[:8])
    for path, what in [(args.corpus_dir, 'SamudraManthanam corpus dir'),
                       (args.dcs_sqlite, 'DCS sqlite')]:
        if not os.path.exists(path):
            sys.exit('%s not found at %s (local-only store)' % (what, path))

    ginv = load_gorresio_inventory(ksverse)
    with open(OUT_GINV, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(['kanda', 'sarga', 'n_verses', 'volume', 'page_first', 'page_last'])
        w.writerows(ginv)
    print('gorresio inventory: %d sargas -> %s' % (len(ginv), OUT_GINV))

    southern = load_southern(args.corpus_dir)
    critical = load_critical(args.dcs_sqlite)

    with open(OUT_SC, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(['s_kanda', 's_sarga', 's_verse',
                    'c_kanda', 'c_sarga', 'c_verse', 'score', 'class'])
        stats = defaultdict(int)
        for kanda in sorted(southern):
            rows = align_kanda(southern[kanda], critical.get(kanda, []))
            for s_sarga, s_verse, c_sarga, c_verse, score, cls in rows:
                w.writerow([kanda, s_sarga, s_verse,
                            kanda if c_sarga != '' else '', c_sarga, c_verse,
                            score, cls])
                stats[cls] += 1
            print('kanda %d: %d southern verses aligned' % (kanda, len(rows)))
        print('southern<->critical classes:', dict(stats))

    # The Gorresio<->Southern sarga map is owned by `build-gorresio` (CONTENT-
    # BASED, from the e-text). The original content-blind DTW draft this
    # command used to emit here was superseded 26-07-2026 — anchor checks
    # showed it drifted ±1–3 sargas — and must not clobber the content map.
    print('gorresio<->southern sarga map: owned by build-gorresio (not touched)')


def _segment_sarga(blocks):
    """Split a sarga's page texts into verses by ॥N॥ markers, anchored to the
    hand-made per-page verse ranges from ksverse.js (`blocks` =
    [(text, v1, v2), ...] in page order). OCR drops digits often enough
    (॥91॥ read as ॥1॥) that the parsed number is only trusted INSIDE the
    page's known range; otherwise the running counter wins. Later pages
    overwrite front-matter pollution on kāṇḍa-opening pages."""
    digits = str.maketrans('०१२३४५६७८९', '0123456789')
    verses = {}
    carry = ''
    last = 0
    for text, v1, v2 in blocks:
        # tesseract renders the double daṇḍa ॥ as two single daṇḍas often
        # enough to lose whole verses — normalize before splitting
        text = text.replace('।।', '॥')
        txt = (carry + '\n' + text).translate(digits)
        chunks = re.split('॥\\s*(\\d{1,3})\\s*॥?', txt)
        carry = chunks[-1]
        expect = max(v1, last + 1)
        for j in range(1, len(chunks), 2):
            parsed = int(chunks[j])
            if v1 <= parsed <= v2:
                num = parsed
            elif expect <= v2 + 1:
                num = expect
            else:
                continue
            verses[num] = re.sub(r'\s+', ' ', chunks[j - 1]).strip()[-400:]
            last = max(last, num)
            expect = num + 1
    return verses


def cmd_build_gorresio(args):
    """Extract the Gorresio e-text from the Cologne page PDFs' embedded Google
    text layer (discovered 26-07-2026 — the 'no OCR exists' premise was wrong:
    every pdfpages/rgorr_*.pdf carries clean digitized Devanagari) and align it
    verse-level against the Southern corpus. This supersedes the DTW sarga
    draft with a CONTENT-BASED map."""
    from indic_transliteration import sanscript      # lazy: not needed in CI
    try:
        import fitz                                  # PyMuPDF: ~100x faster

        def _page_text(path):
            doc = fitz.open(path)
            try:
                return doc[0].get_text() or ''
            finally:
                doc.close()
    except ImportError:
        from pypdf import PdfReader

        def _page_text(path):
            return PdfReader(path).pages[0].extract_text() or ''

    ksdata = _load_ksverse(args.ksverse)

    cache = args.cache or os.path.join(args.pdf_dir, '..', 'page_texts.jsonl')
    texts = {}
    if os.path.exists(cache):
        for line in open(cache, encoding='utf-8'):
            r = json.loads(line)
            texts[(r['vol'], r['page'])] = r['text']
    else:
        wanted = sorted({(b['v'], b['page']) for sg in ksdata.values()
                         for bl in sg.values() for b in bl})
        with open(cache, 'w', encoding='utf-8') as out:
            for i, (vol, page) in enumerate(wanted):
                # text-volume 6 (uttarakāṇḍa) is filed as 'uk' in pdfpages/
                fvol = 'uk' if str(vol) == '6' else vol
                path = os.path.join(args.pdf_dir, 'rgorr_%s.%03d.pdf' % (fvol, page))
                text = ''
                if os.path.exists(path):
                    try:
                        text = _page_text(path)
                    except Exception:
                        text = ''
                texts[(vol, page)] = text
                out.write(json.dumps({'vol': vol, 'page': page, 'text': text},
                                     ensure_ascii=False) + '\n')
                if i % 250 == 0:
                    print('  extracting %d/%d' % (i, len(wanted)), flush=True)
    print('page texts: %d (empty: %d)'
          % (len(texts), sum(1 for t in texts.values() if not t)))

    etext = {}
    for kanda, sargas in ksdata.items():
        for sarga, blocks in sargas.items():
            page_blocks = [(texts.get((b['v'], b['page']), ''), b['v1'], b['v2'])
                           for b in blocks]
            etext[(int(kanda), int(sarga))] = _segment_sarga(page_blocks)

    with open(OUT_GETEXT, 'w', encoding='utf-8') as fh:
        for (k, s), verses in sorted(etext.items()):
            for v, deva in sorted(verses.items()):
                iast = sanscript.transliterate(deva, sanscript.DEVANAGARI,
                                               sanscript.IAST)
                fh.write(json.dumps({'k': k, 's': s, 'v': v, 'iast': iast},
                                    ensure_ascii=False) + '\n')
    n = sum(len(v) for v in etext.values())
    print('gorresio e-text: %d verses -> %s' % (n, OUT_GETEXT))

    southern = load_southern(args.corpus_dir)

    sarga_rows = []
    with open(OUT_GSV, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(['g_kanda', 'g_sarga', 'g_verse',
                    's_kanda', 's_sarga', 's_verse', 'score', 'class'])
        for k in sorted({kk for kk, _ in etext}):
            grows = []
            for (kk, s), verses in sorted(etext.items()):
                if kk != k:
                    continue
                for v, deva in sorted(verses.items()):
                    iast = sanscript.transliterate(deva, sanscript.DEVANAGARI,
                                                   sanscript.IAST)
                    grows.append((s, v, norm(iast)))
            if k not in southern:
                for s, v, _ in grows:
                    w.writerow([k, s, v, '', '', '', '', 'no_southern_corpus'])
                continue
            rows = align_kanda(grows, southern[k], shingle=8, step=2,
                               match_lo=0.25, match_hi=0.45)
            stats = defaultdict(int)
            for g_sarga, g_verse, s_sarga, s_verse, score, cls in rows:
                if cls == 'southern_only':
                    cls = 'gorresio_only'
                if (cls in ('matched', 'fuzzy') and s_sarga != '' and
                        (k, g_sarga, g_verse,
                         k, s_sarga, s_verse) in AUDIT_REJECTED_PAIRS):
                    cls = 'audit-rejected'
                w.writerow([k, g_sarga, g_verse,
                            k if s_sarga != '' else '', s_sarga, s_verse,
                            score, cls])
                stats[cls] += 1
                if cls in ('matched', 'fuzzy'):
                    sarga_rows.append((k, g_sarga, s_sarga))
            print('kanda %d: %s' % (k, dict(stats)))
    print('verse map -> %s' % OUT_GSV)

    # Regenerate the sarga-level map CONTENT-BASED (supersedes the DTW draft).
    per_sarga = defaultdict(lambda: defaultdict(int))
    for k, gs, ss in sarga_rows:
        per_sarga[(k, gs)][ss] += 1
    g_verse_count = {(k, s): len(v) for (k, s), v in etext.items()}
    with open(OUT_GS, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(['g_kanda', 'g_sarga', 'g_verses',
                    's_kanda', 's_sarga', 'n_matched', 'share',
                    'confidence', 'status'])
        for (k, gs) in sorted(g_verse_count):
            nv = g_verse_count[(k, gs)]
            cands = per_sarga.get((k, gs))
            if not cands:
                w.writerow([k, gs, nv, '', '', 0, '', 'none', 'CONTENT-BASED'])
                continue
            ss, cnt = max(cands.items(), key=lambda t: t[1])
            share = round(cnt / max(1, nv), 3)
            conf = ('high' if share >= 0.6 and cnt >= 5 else
                    'medium' if share >= 0.3 else 'low')
            w.writerow([k, gs, nv, k, ss, cnt, share, conf, 'CONTENT-BASED'])
    print('sarga map regenerated CONTENT-BASED -> %s' % OUT_GS)


def _load_ksverse(path):
    src = open(path, encoding='utf-8').read()
    src = src.split('=', 1)[1].strip().rstrip(';')
    src = re.sub(r'([{,]\s*)(\d+)(\s*):', r'\1"\2"\3:', src)
    src = re.sub(r',(\s*[}\]])', r'\1', src)
    return json.loads(src)


def cmd_selftest(_args):
    """CI gate over the COMMITTED TSVs — no local stores, no network."""
    fails = []

    def check(cond, msg):
        (print('  ok  - %s' % msg) if cond else fails.append(msg))

    inv = list(csv.DictReader(open(OUT_GINV, encoding='utf-8'), delimiter='\t'))
    check(len(inv) > 500, 'gorresio inventory has %d sargas (>500)' % len(inv))
    check({int(r['kanda']) for r in inv} == {1, 2, 3, 4, 5, 6, 7},
          'gorresio inventory covers all 7 kandas')
    fix = [r for r in inv if r['kanda'] == '2' and r['sarga'] == '16']
    check(fix and int(fix[0]['n_verses']) >= 46,
          'fixture R. GORR. 2,16,46 inside inventory (2,16 has %s verses)'
          % (fix[0]['n_verses'] if fix else '-'))
    for r in inv:
        if int(r['page_first']) > int(r['page_last']):
            fails.append('inventory page range inverted at %s,%s'
                         % (r['kanda'], r['sarga']))
            break

    binv = list(csv.DictReader(open(OUT_BINV, encoding='utf-8'), delimiter='\t'))
    check({int(r['kanda']) for r in binv} == {1, 2, 3, 4, 5, 6, 7},
          'bombay inventory covers all 7 kandas')
    b7 = [r for r in binv if r['kanda'] == '7']
    b7_int = sorted(int(r['sarga']) for r in b7 if '.' not in r['sarga'])
    check(b7_int == list(range(1, 112)),
          'bombay uttarakanda = 111 consecutive sargas (got %d, max %s)'
          % (len(b7_int), b7_int[-1] if b7_int else '-'))
    # The whole H1705 verdict rests on this: the Bombay ed. PWG cites for book 7
    # runs 11 sargas PAST the 100-sarga corpus text, so no offset scheme is honest.
    check(len(b7_int) - 100 == 11,
          'bombay uttarakanda exceeds the corpus 100 sargas by 11')
    interp7 = sorted(r['sarga'] for r in b7 if 'interpolated' in r['flags'])
    check(interp7 == ['23.1', '23.2', '23.3', '23.4', '23.5',
                      '37.1', '37.2', '37.3', '37.4', '37.5',
                      '59.1', '59.2', '59.3'],
          'bombay uttarakanda interpolated sargas intact (%d)' % len(interp7))
    fix111 = [r for r in b7 if 'index_typo_111' in r['flags']]
    check(len(fix111) == 1 and fix111[0]['sarga'] == '111'
          and int(fix111[0]['page_first']) > 800,
          'indexv3 sarga-11/111 typo repaired at the tail, not at the real 11')
    real11 = [r for r in b7 if r['sarga'] == '11']
    check(real11 and int(real11[0]['page_last']) < 600,
          'the genuine uttarakanda sarga 11 kept its own page span')
    for r in binv:
        if int(r['page_first']) > int(r['page_last']):
            fails.append('bombay inventory page range inverted at %s,%s'
                         % (r['kanda'], r['sarga']))
            break

    sc = list(csv.DictReader(open(OUT_SC, encoding='utf-8'), delimiter='\t'))
    check(len(sc) > 15000, 'southern<->critical has %d verse rows (>15000)' % len(sc))
    matched = [r for r in sc if r['class'] in ('matched', 'fuzzy')]
    share = len(matched) / len(sc)
    check(share >= 0.5,
          'aligned share %.1f%% >= 50%%' % (100 * share))
    check(any(r['s_kanda'] == '2' and r['s_sarga'] == '91' for r in sc),
          'fixture R. 2,91 (southern) present')
    check(not any(r['s_kanda'] == '4' for r in sc),
          'kanda 4 (kiskindha) correctly absent from southern side')
    last = {}
    mono_ok = True
    for r in sc:
        if r['class'] != 'matched':
            continue
        k = r['s_kanda']
        key = (int(r['c_sarga']), int(r['c_verse']))
        if k in last and key < last[k]:
            mono_ok = False
            break
        last[k] = key
    check(mono_ok, 'matched rows monotonic per kanda')

    gs = list(csv.DictReader(open(OUT_GS, encoding='utf-8'), delimiter='\t'))
    check(all(r['status'] == 'CONTENT-BASED' for r in gs),
          'every gorresio<->southern sarga row is CONTENT-BASED')
    k4 = [r for r in gs if r['g_kanda'] == '4']
    check(k4 and all(r['s_sarga'] == '' for r in k4),
          'kanda 4 gorresio rows carry no southern mapping')

    gsv = list(csv.DictReader(open(OUT_GSV, encoding='utf-8'), delimiter='\t'))
    check(len(gsv) > 19000, 'gorresio verse map has %d rows (>19000)' % len(gsv))
    et_kandas = {r['g_kanda'] for r in gsv}
    check(et_kandas == {'1', '2', '3', '4', '5', '6', '7'},
          'e-text covers all 7 kandas (H1689 closed vols 2/4/uk)')
    k2_sargas = {int(r['g_sarga']) for r in gsv if r['g_kanda'] == '2'}
    check(min(k2_sargas) == 1 and max(k2_sargas) == 127 and len(k2_sargas) == 127,
          'kanda 2 covers sargas 1-127 (%d sargas)' % len(k2_sargas))
    for kk in ('5', '7'):
        n = sum(1 for r in gsv
                if r['g_kanda'] == kk and r['class'] in ('matched', 'fuzzy'))
        check(n > 300, 'kanda %s has %d mapped verses (>300)' % (kk, n))
    # 'audit-rejected' = row switched off by a voted review sheet (the 26-07-2026
    # audit killed 4 half-verse-shift pairs); the citation_tm loader only reads
    # matched/fuzzy, so these are inert by construction — keep them for the trail.
    ok_cls = {'matched', 'fuzzy', 'moved', 'gorresio_only', 'no_southern_corpus',
              'audit-rejected'}
    check({r['class'] for r in gsv} <= ok_cls, 'verse-map classes are typed')
    rej = [r for r in gsv if r['class'] == 'audit-rejected']
    check(len(rej) == 4 and all(r['g_kanda'] in ('1', '2') for r in rej),
          '4 audit-rejected rows from the 26-07-2026 sheet stay switched off')
    anchor = [r for r in gsv if (r['g_kanda'], r['g_sarga'], r['g_verse'])
              == ('1', '22', '1')]
    check(anchor and anchor[0]['s_sarga'] == '19' and anchor[0]['class'] == 'matched',
          'gold anchor G 1,22,1 -> S 19,1 matched (scan-verified 26-07-2026)')

    # Resolver contract (reuse ON, MG 26-07-2026): mapped verses resolve,
    # gaps stay HONEST typed misses — never an invented offset.
    sys.path.insert(0, HERE)
    import citation_tm
    res = citation_tm.lookup('R. GORR.', '1,22,1')
    check(res.get('canonical_id') == '01_ramayana-balakanda:19.1',
          'citation_tm R. GORR. 1,22,1 resolves via concordance (got %r)'
          % res.get('canonical_id'))
    res = citation_tm.lookup('R.', '3,79,10')
    check(res.get('status') == 'miss'
          and res.get('reason') == 'no-southern-counterpart',
          'R. 3,79,10 -> honest no-southern-counterpart miss (got %r/%r)'
          % (res.get('status'), res.get('reason')))
    res = citation_tm.lookup('R. GORR.', '2,16,46')
    check(res.get('status') == 'miss'
          and res.get('reason') == 'no-southern-counterpart',
          'R. GORR. 2,16,46 -> honest no-southern-counterpart (H1689: the '
          'vol-2 e-text gap is closed; this verse is Bengal-only, best '
          'Southern score 0.109)')
    res = citation_tm.lookup('R. GORR.', '5,10,1')
    check(res.get('canonical_id') == '05_ramayana-sundarakanda:2.51',
          'citation_tm R. GORR. 5,10,1 resolves (Sundara live, got %r)'
          % res.get('canonical_id'))

    if fails:
        for msg in fails:
            print('  FAIL - %s' % msg)
        sys.exit('selftest: %d failure(s)' % len(fails))
    print('selftest: all green')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build', help='build all three TSVs (needs local stores)')
    b.add_argument('--corpus-dir', default=DEFAULT_CORPUS_DIR)
    b.add_argument('--dcs-sqlite', default=DEFAULT_DCS_SQLITE)
    b.add_argument('--ksverse', default=None)
    b.set_defaults(func=cmd_build)
    g = sub.add_parser('build-gorresio',
                       help='e-text from page-PDF text layer + verse-level map')
    g.add_argument('--pdf-dir', required=True,
                   help='local ramayanagorr pdfpages/ (per-page PDFs)')
    g.add_argument('--ksverse', required=True)
    g.add_argument('--corpus-dir', default=DEFAULT_CORPUS_DIR)
    g.add_argument('--cache', default=None,
                   help='page-text cache jsonl (reused across runs)')
    g.set_defaults(func=cmd_build_gorresio)
    bo = sub.add_parser('build-bombay',
                        help='Bombay structural inventory + numbering study')
    bo.add_argument('--index-dir', required=True,
                    help='local ramayanabom app1/pywork/ (indexv1-3.txt)')
    bo.add_argument('--corpus-dir', default=DEFAULT_CORPUS_DIR)
    bo.set_defaults(func=cmd_build_bombay)
    s = sub.add_parser('selftest', help='CI gate over committed TSVs')
    s.set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
