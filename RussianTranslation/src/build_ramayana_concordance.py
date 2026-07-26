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
  src/ramayana_gorresio_southern_sarga_map.tsv
      sarga-level, STRUCTURE-ONLY DRAFT: DTW over verse-count profiles.
      Columns: g_kanda g_sarga g_verses s_kanda s_sarga s_verses ratio
      confidence status;  status is always DRAFT-STRUCTURAL — this map is
      content-blind evidence and MUST NOT drive citation reuse until the
      validation gate passes (see COVERED_TEXTS_RU.md).

Build (needs the two LOCAL-ONLY stores; absent in CI by design):

  python src/build_ramayana_concordance.py build \
      [--corpus-dir <SamudraManthanam>/web/corpus_builder/jsonl] \
      [--dcs-sqlite <VisualDCS>/src/DCS-data-2026/dcs_full.sqlite] \
      [--ksverse <path to ksverse.js>]

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
# Southern ↔ Critical verse alignment
# ---------------------------------------------------------------------------

def align_kanda(southern, critical):
    """Content-based monotonic alignment inside one kāṇḍa."""
    # Shingle index over critical verses (12-char shingles, step 4).
    index = defaultdict(set)
    cgrams = []
    for ci, (_, _, text) in enumerate(critical):
        cgrams.append(grams(text))
        for i in range(0, max(1, len(text) - 11), 4):
            index[text[i:i + 12]].add(ci)
    pairs = []  # (si, ci, score)
    for si, (_, _, text) in enumerate(southern):
        hits = defaultdict(int)
        for i in range(0, max(1, len(text) - 11), 4):
            for ci in index.get(text[i:i + 12], ()):
                hits[ci] += 1
        if not hits:
            continue
        sg = grams(text)
        best_ci, best_score = -1, 0.0
        for ci in sorted(hits, key=hits.get, reverse=True)[:5]:
            inter = len(sg & cgrams[ci])
            union = len(sg | cgrams[ci])
            score = inter / union if union else 0.0
            if score > best_score:
                best_ci, best_score = ci, score
        if best_score >= MATCH_LO:
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
            cls = 'matched' if score >= MATCH_HI else 'fuzzy'
        elif score >= MATCH_HI:
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
# Gorresio ↔ Southern sarga-level structural DTW
# ---------------------------------------------------------------------------

def sarga_profile(rows_by_kanda):
    """{kanda: [(sarga, n_verses), ...]} from verse-level rows."""
    out = {}
    for kanda, rows in rows_by_kanda.items():
        counts = defaultdict(int)
        for sarga, verse, _ in rows:
            counts[sarga] = max(counts[sarga], verse)
        out[kanda] = sorted(counts.items())
    return out


def dtw_sargas(gor, sou):
    """Monotonic DTW over two (sarga, n_verses) sequences; gaps allowed."""
    G, S = len(gor), len(sou)
    GAP = 0.6
    INF = float('inf')
    cost = [[INF] * (S + 1) for _ in range(G + 1)]
    move = [[None] * (S + 1) for _ in range(G + 1)]
    cost[0][0] = 0.0
    for gi in range(G + 1):
        for sj in range(S + 1):
            if cost[gi][sj] is INF:
                continue
            base = cost[gi][sj]
            if gi < G and sj < S:
                ng, ns = gor[gi][1], sou[sj][1]
                c = abs(ng - ns) / max(ng, ns)
                if base + c < cost[gi + 1][sj + 1]:
                    cost[gi + 1][sj + 1] = base + c
                    move[gi + 1][sj + 1] = 'm'
            if gi < G and base + GAP < cost[gi + 1][sj]:
                cost[gi + 1][sj] = base + GAP
                move[gi + 1][sj] = 'g'
            if sj < S and base + GAP < cost[gi][sj + 1]:
                cost[gi][sj + 1] = base + GAP
                move[gi][sj + 1] = 's'
    out, gi, sj = [], G, S
    while gi or sj:
        mv = move[gi][sj]
        if mv == 'm':
            gi, sj = gi - 1, sj - 1
            out.append((gor[gi], sou[sj]))
        elif mv == 'g':
            gi -= 1
            out.append((gor[gi], None))
        else:
            sj -= 1
            out.append((None, sou[sj]))
    return list(reversed(out))


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

    gprof = defaultdict(list)
    for kanda, sarga, n, _, _, _ in ginv:
        gprof[kanda].append((sarga, n))
    sprof = sarga_profile(southern)
    with open(OUT_GS, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(['g_kanda', 'g_sarga', 'g_verses',
                    's_kanda', 's_sarga', 's_verses',
                    'ratio', 'confidence', 'status'])
        for kanda in sorted(gprof):
            if kanda not in sprof:      # kiṣkindhā: no southern corpus side
                for sarga, n in gprof[kanda]:
                    w.writerow([kanda, sarga, n, '', '', '', '',
                                'none', 'DRAFT-STRUCTURAL'])
                continue
            for gside, sside in dtw_sargas(gprof[kanda], sprof[kanda]):
                if gside and sside:
                    (gs, gn), (ss, sn) = gside, sside
                    ratio = round(min(gn, sn) / max(gn, sn), 3)
                    conf = 'plausible' if ratio >= 0.85 else 'weak'
                    w.writerow([kanda, gs, gn, kanda, ss, sn, ratio, conf,
                                'DRAFT-STRUCTURAL'])
                elif gside:
                    w.writerow([kanda, gside[0], gside[1], '', '', '', '',
                                'none', 'DRAFT-STRUCTURAL'])
                else:
                    w.writerow(['', '', '', kanda, sside[0], sside[1], '',
                                'none', 'DRAFT-STRUCTURAL'])
    print('gorresio<->southern sarga map -> %s' % OUT_GS)


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
    check(all(r['status'] == 'DRAFT-STRUCTURAL' for r in gs),
          'every gorresio<->southern row is DRAFT-STRUCTURAL')
    k4 = [r for r in gs if r['g_kanda'] == '4']
    check(k4 and all(r['s_sarga'] == '' for r in k4),
          'kanda 4 gorresio rows carry no southern mapping')

    # The resolver contract: R. GORR. must STILL be unmapped in citation_tm.
    sys.path.insert(0, HERE)
    import citation_tm
    res = citation_tm.lookup('R. GORR.', '2,16,46')
    status = res.get('status') if isinstance(res, dict) else getattr(res, 'status', None)
    check(status == 'unmapped_locus_scheme',
          'citation_tm R. GORR. stays unmapped_locus_scheme (got %r)' % status)

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
    s = sub.add_parser('selftest', help='CI gate over committed TSVs')
    s.set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
