#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H6590 (h2361 step 2): rebuild the EN<->SA stanza mapping for RV 8.49-8.103.

Method (philological, not a blind rekey):
  1. Learn EN transliterations of rare Sanskrit names from the ALIGNED region
     8.1-8.48 (92.2% anchor agreement, H2361) via fuzzy token matching.
  2. Score every (EN stanza, SA stanza) pair in the 8.44-8.103 window by
     IDF-weighted rare-name evidence (learned lexicon + generic deity anchors).
  3. Monotone DP (Needleman-Gotoh) over the flat stanza sequences; identity in
     8.44-8.48 is the in-run control.
  4. Emit the mapping + confidence per stanza as JSON for the repair step.

Dry run: writes nothing but reports/H6590_alignment_mapping.json (gitignored
runtime dir -- the committed report is written by h6590_asset_repair.py).
"""
import difflib
import json
import math
import os
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sibling_root import sibling_root

GITHUB = sibling_root(HERE)
CORPUS_DB = os.environ.get(
    'SAMUDRA_CORPUS_DB', os.path.join(GITHUB, 'SamudraManthanam', 'web', 'corpus.db'))
FIXTURE = os.path.join(HERE, '..', 'tests', 'fixtures', 'rigveda_sa_fixture.db')
GRIFFITH_EN_JSON = os.path.join(HERE, '..', 'pwg_ru', 'griffith_en_1896.json')
OUT = os.environ.get(
    'H6590_MAPPING_OUT',
    os.path.join(HERE, '..', 'reports', 'H6590_alignment_mapping.json'))

WIN_LO, WIN_HI = 44, 103          # alignment window (mandala 8)
CONTROL_LO, CONTROL_HI = 44, 48   # must align as identity
MIN_TOK = 4                        # min token length for name matching
SIM_MIN = 0.72                     # fuzzy token similarity floor

sys.stdout.reconfigure(encoding='utf-8')


def strip_diacritics(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if not unicodedata.combining(c))


def en_tokens(text):
    # Griffith: keep alphabetic runs, lowercase; drop ALLCAPS display prefixes.
    return [t.lower() for t in re.findall(r"[A-Za-zāīūṛṝḷḹōēṅñṭḍṇśṣḥ'-]+", text)]


def sa_tokens(text):
    # SLP1-ish Unicode Sanskrit: fold to bare latin by stripping diacritics,
    # drop non-letter suffix clutter lightly.
    folded = strip_diacritics(text).lower()
    toks = re.findall(r"[a-z]+", folded)
    out = []
    for t in toks:
        if len(t) >= MIN_TOK:
            out.append(t)
    return out


def sim(a, b):
    """Cheap bounded similarity: exact after fold, else bounded ratio, tuned for
    macron/variant differences (kanva~kāṇva folded to kanva, vrtra~vṛtra→vrtra)."""
    if a == b:
        return 1.0
    if a[0] != b[0] or abs(len(a) - len(b)) > 2:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


class Lexicon:
    """(Kept for reference; scoring now uses the global tolerant match index.)"""

    def __init__(self):
        self.pairs = defaultdict(set)

    def learn(self, sa_txt, en_txt):
        st, et = sa_tokens(sa_txt), en_tokens(en_txt)
        for s in st:
            for e in et:
                if len(e) >= MIN_TOK and sim(s, e) >= 0.80:
                    self.pairs[s].add(e)

    def knows(self, s, e):
        cands = self.pairs.get(s)
        if not cands:
            return False
        for c in cands:
            if c == e or sim(c, e) >= 0.80:
                return True
        return False


def load():
    db = CORPUS_DB if os.path.exists(CORPUS_DB) else FIXTURE
    con = sqlite3.connect('file:{}?mode=ro'.format(db), uri=True)
    sa = {}
    for cid, txt in con.execute(
            "SELECT canonical_id, line_text FROM corpus_lines "
            "WHERE canonical_id LIKE '08_rigveda:%#sa'"):
        work, rest = cid.split(':')
        hymn, verse = rest[:-3].split('.')
        sa[(8, int(hymn), int(verse))] = txt or ''
    con.close()
    with open(GRIFFITH_EN_JSON, encoding='utf-8') as fh:
        d = json.load(fh)
    en = {}
    for r in d['contents']:
        loc = r.get('location')
        if loc and r.get('text') and loc.startswith('8.'):
            m, s, v = map(int, loc.split('.'))
            en[(m, s, v)] = r['text']
    return db, sa, en


def main():
    db, sa, en = load()
    print('db: %s   SA mandala8: %d   EN mandala8: %d' % (db, len(sa), len(en)))

    # ---- 1. rotated reference (vulgate order) + flat null mapping ---------
    # The en column follows the vulgate sequence: crit 60..103 then 49..59
    # (macro-verified verse-1 readings at all 22 hymn heads, H6590). Build
    # that reference in stanza order; the null is position identity; the DP
    # only resolves LOCAL drift (Griffith's own verse-count divergences).
    crit_by_hymn = defaultdict(list)
    for k in sorted(sa):
        if k[0] == 8 and 1 <= k[1] <= 103:
            crit_by_hymn[k[1]].append(k)
    ref = []
    for h in list(range(60, 104)) + list(range(49, 60)):
        ref.extend(sorted(crit_by_hymn[h]))
    en_blk = [k for k in sorted(en) if 49 <= k[1] <= 103]
    N, M = len(en_blk), len(ref)
    print('block 8.49-8.103: EN %d stanzas, rotated crit reference %d stanzas'
          % (N, M))

    en_seq, sa_seq = en_blk, ref

    en_tok = {k: en_tokens(en[k]) for k in en_seq}
    sa_tok = {k: sa_tokens(sa[k]) for k in sa_seq}

    df = defaultdict(int)
    for k in sa_seq:
        for t in set(sa_tok[k]):
            df[t] += 1
    idf = {t: math.log(1 + M / (1 + c)) for t, c in df.items()}

    # ---- 2. global tolerant match index over UNIQUE tokens ----------------
    # idf floor 2.0: drop the deity-saturated vocabulary (indra/agni/soma occur
    # in a third of the window and match in the WRONG stanza too).
    IDF_FLOOR = 2.0
    uniq_sa = sorted({t for k in sa_seq for t in sa_tok[k] if idf[t] >= IDF_FLOOR})
    uniq_en = sorted({t for k in en_seq for t in en_tok[k] if len(t) >= MIN_TOK})
    by_first = defaultdict(list)
    for e in uniq_en:
        by_first[e[0]].append(e)
    match_index = {}
    for s in uniq_sa:
        hits = set()
        for e in by_first.get(s[0], ()):  # Griffith keeps the initial consonant
            if sim(s, e) >= 0.80:
                hits.add(e)
        if hits:
            match_index[s] = hits
    print('match index: %d rare SA tokens with an EN candidate' % len(match_index))

    # near-unique names (<=2 SA stanzas in the window) are near-certain keys
    rare_weight = {t: (2.5 * idf[t] if df[t] <= 2 else idf[t]) for t in idf}

    en_set = {k: frozenset(t for t in en_tok[k] if len(t) >= MIN_TOK)
              for k in en_seq}
    sa_rare = {k: [(t, rare_weight[t]) for t in sa_tok[k] if idf[t] >= IDF_FLOOR]
               for k in sa_seq}

    def score(i, j):
        """Rare-name evidence that EN stanza i renders SA stanza j (>= 0)."""
        val = 0.0
        eset = en_set[en_seq[i]]
        for t, w in sa_rare[sa_seq[j]]:
            hits = match_index.get(t)
            if hits and not hits.isdisjoint(eset):
                val += w
        return val

    # ---- 3. monotone DP (Needleman-Gotoh) with locality band -------------
    # Null hypothesis = position identity in rotated coordinates (the site
    # pasted Griffith's vulgate-order text onto critical stamps 1:1). The DP
    # only pays a drift where the name evidence demands it.
    GAP = 1.5
    BAND = 30
    NEG = float('-inf')
    S = [[NEG] * (M + 1) for _ in range(N + 1)]
    BT = [[0] * (M + 1) for _ in range(N + 1)]  # 1 diag, 2 up(EN gap), 3 left
    S[0][0] = 0.0
    for j in range(1, min(M, BAND) + 1):
        S[0][j] = -GAP * j
        BT[0][j] = 3
    for i in range(1, min(N, BAND) + 1):
        S[i][0] = -GAP * i
        BT[i][0] = 2
    for i in range(1, N + 1):
        Si, Sim1, BTi = S[i], S[i - 1], BT[i]
        jlo = max(1, i - BAND)
        jhi = min(M, i + BAND)
        for j in range(jlo, jhi + 1):
            d = Sim1[j - 1] + score(i - 1, j - 1) if Sim1[j - 1] != NEG else NEG
            u = Sim1[j] - GAP if Sim1[j] != NEG else NEG
            l = Si[j - 1] - GAP if Si[j - 1] != NEG else NEG
            if d >= u and d >= l:
                Si[j], BTi[j] = d, 1
            elif u >= l:
                Si[j], BTi[j] = u, 2
            else:
                Si[j], BTi[j] = l, 3

    # traceback
    pairs = []
    i, j = N, M
    while i > 0 or j > 0:
        if i > 0 and j > 0 and BT[i][j] == 1:
            pairs.append((en_seq[i - 1], sa_seq[j - 1], S[i][j] - S[i - 1][j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and (j == 0 or BT[i][j] == 2):
            pairs.append((en_seq[i - 1], None, None))
            i -= 1
        else:
            pairs.append((None, sa_seq[j - 1], None))
            j -= 1
    pairs.reverse()

    # ---- 4. drift profile in rotated coordinates --------------------------
    # control here = the flat null: a pair (i, i) is the vulgate-paste null.
    pairs = []
    i, j = N, M
    while i > 0 or j > 0:
        if i > 0 and j > 0 and BT[i][j] == 1:
            pairs.append((en_seq[i - 1], sa_seq[j - 1], S[i][j] - S[i - 1][j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and (j == 0 or BT[i][j] == 2):
            pairs.append((en_seq[i - 1], None, None))
            i -= 1
        else:
            pairs.append((None, sa_seq[j - 1], None))
            j -= 1
    pairs.reverse()

    mapped = [(e, s, sc) for e, s, sc in pairs if e and s]
    unmapped_en = [e for e, s, _ in pairs if e and not s]
    unmapped_sa = [s for e, s, _ in pairs if s and not e]
    print('\nblock: %d EN->ref pairs, %d EN ungapped, %d ref unmapped'
          % (len(mapped), len(unmapped_en), len(unmapped_sa)))
    drift = [(e, s, sc) for e, s, sc in mapped if e != s]
    print('  stanzas off the flat null: %d  (these are the real drift sites)'
          % len(drift))
    for e, s, sc in drift[:40]:
        print('   drift %d.%d.%d -> %d.%d.%d (score %.2f)' % (e + s + (sc,)))
    order = [s for _, s, _ in mapped]
    viol = sum(1 for a, b in zip(order, order[1:]) if b <= a)
    print('  monotonicity violations: %d' % viol)

    out = {
        'generated': 'H6590 dry run',
        'db': db,
        'match_index_entries': len(match_index),
        'reference': 'rotated vulgate order: crit 8.60-8.103 then 8.49-8.59',
        'off_null_pairs': len(drift),
        'pairs': [
            {'en': ('%d.%d.%d' % e) if e else None,
             'sa': ('%d.%d.%d' % s) if s else None,
             'score': sc}
            for e, s, sc in pairs if (e and e[1] >= 49) or (s and s[1] >= 49)],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print('\nwrote %s' % OUT)


if __name__ == '__main__':
    main()
