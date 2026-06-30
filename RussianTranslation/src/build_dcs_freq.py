#!/usr/bin/env python
r"""Build the DCS frequency table consumed by annotate_dcs_freq.py.

Reads the DCS token corpus (VisualDCS/src/DCS-data-2026/dcs_full.sqlite) and emits a
per-lemma frequency record keyed by a normalized IAST lemma form, so the translated
store can be annotated with a Macmillan-style 1-5 band plus hapax/absent/Pareto flags.

Design decisions (per MG, 2026-06-30):
  - GRANULARITY: per preverb-compound lemma (DCS stores e.g. 'atikram' with preverbs
    'ati'); the simple root is also indexed so annotation can fall back to it.
  - SCALE: re-derived from RAW token counts (not the pre-bucketed dcs_lemma_summary
    freqBand). Bands are decimal (log10) orders, documented in BAND_EDGES below.
  - HAPAX/ABSENT: carried as explicit flags, not folded into the band — band stays a
    magnitude, hapax=(count==1), absent=(lemma not in DCS at all; handled at annotate
    time by a missing lookup).
  - PARETO: 'core80' marks the smallest set of most-frequent lemmas whose cumulative
    token count covers >=80% of the whole DCS corpus (the ~20% of words that carry
    ~80% of running text).

Homonyms (several lemma_id rows sharing one lemma string) are SUMMED — the question is
"how often is this word met in DCS", not "which sense". Output is IAST-keyed because the
store rows carry an IAST 'iast' field; SLP1 cards are matched at annotate time via the
same normalizer.

  python src/build_dcs_freq.py                  # -> src/dcs_freq.json
  python src/build_dcs_freq.py --selftest
"""
import argparse
import collections
import json
import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DCS_SQLITE = os.path.normpath(os.path.join(REPO, '..', '..', 'VisualDCS', 'src',
                                           'DCS-data-2026', 'dcs_full.sqlite'))
OUT = os.path.join(HERE, 'dcs_freq.json')

# Band edges on RAW aggregated token count. band = number of the highest edge the count
# clears. 0 is reserved for "absent" (assigned at annotate time, never stored here).
# 5: >=1000  4: >=100  3: >=10  2: >=2  1: ==1 (== hapax). Tune here; documented in store.
BAND_EDGES = [(1000, 5), (100, 4), (10, 3), (2, 2), (1, 1)]
PARETO_COVERAGE = 0.80


def band_for(count):
    for edge, band in BAND_EDGES:
        if count >= edge:
            return band
    return 0


# SLP1 capital-letter aspirates/retroflex that can leak into an otherwise-IAST 'iast'
# field (observed: 'aBisam+vas'). Mapped to their IAST digraphs so matching is robust.
_SLP1_LEAK = {'B': 'bh', 'K': 'kh', 'G': 'gh', 'C': 'ch', 'J': 'jh', 'D': 'dh',
              'T': 'th', 'P': 'ph', 'q': 'ṭ', 'Q': 'ṭh', 'R': 'ṇ', 'S': 'ś',
              'z': 'ṣ', 'M': 'ṃ', 'H': 'ḥ', 'Y': 'ñ', 'N': 'ṅ', 'w': 'ṭ', 'W': 'ṭh',
              'x': 'ḷ', 'f': 'ṛ'}


_VSET = set('aāiīuūṛṝḷeo')


def _vowel_combine(L, R):
    """External vowel sandhi for one junction: last vowel L + first vowel R -> joined.
    Covers the preverb+root cases that plain concatenation misses (pra+āp -> prāp,
    vi+āp -> vyāp, anu+ā -> anvā, upa+i -> upe). Returns the replacement for 'L'+'R'."""
    if L in 'aā':
        return {'a': 'ā', 'ā': 'ā', 'i': 'e', 'ī': 'e', 'u': 'o', 'ū': 'o',
                'ṛ': 'ar', 'ṝ': 'ar', 'ḷ': 'al', 'e': 'ai', 'o': 'au'}.get(R, 'ā' + R)
    if L in 'iī':
        return 'ī' + R if R in 'iī' else 'y' + R
    if L in 'uū':
        return 'ū' + R if R in 'uū' else 'v' + R
    if L in 'ṛṝ':
        return 'ṝ' + R if R in 'ṛṝ' else 'r' + R
    return L + R                                    # e/o: leave (rare in preverbs)


def sandhi_join(parts):
    """Fold ['pra','āp'] -> 'prāp' applying vowel sandhi at each junction; a
    consonant-initial right part (pra+vad) or consonant-final left just concatenates."""
    parts = [p for p in parts if p]
    if not parts:
        return ''
    out = parts[0]
    for nxt in parts[1:]:
        if out and nxt and out[-1] in _VSET and nxt[0] in _VSET:
            out = out[:-1] + _vowel_combine(out[-1], nxt[0]) + nxt[1:]
        else:
            out += nxt
    return out


def sandhi_key(iast):
    """Normalized DCS-comparable key for a compound 'iast' via sandhi (not plain concat).
    'pra+āp' -> 'prāp'; 'dhā (vyā+dhā)' -> drops the parenthetical first."""
    if not iast:
        return ''
    head = re.sub(r'\s*\([^)]*\)', '', iast).strip()
    head = ''.join(_SLP1_LEAK.get(c, c) for c in head)      # repair leak before sandhi
    parts = [p for p in re.split(r'[+\-\s]+', head) if p]
    if len(parts) < 2:
        return ''
    return norm_lemma(sandhi_join(parts))


def norm_lemma(s):
    """Normalize an IAST lemma / store 'iast' form to a DCS-comparable key.

    Strips parentheticals ('dhā (vyā+dhā)' keeps the leading head only), removes the
    '+'/'-'/space compound joiners so 'anusam+āp' -> 'anusamāp', and repairs stray SLP1
    capital leakage. Lowercased. Returns '' for empty input.
    """
    if not s:
        return ''
    s = re.sub(r'\s*\([^)]*\)', '', s).strip()      # drop parenthetical variants
    s = ''.join(_SLP1_LEAK.get(c, c) for c in s)    # repair SLP1 leak BEFORE lowering
    s = s.replace('+', '').replace('-', '').replace(' ', '')
    return s.lower()


def build(sqlite_path):
    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()
    # Sum token rows per lemma_id, then aggregate homonyms by normalized lemma string.
    counts = collections.Counter()
    raw_q = ('select l.lemma, count(*) n from token t '
             'join lemma l on t.lemma_id = l.lemma_id group by l.lemma_id')
    for lemma, n in cur.execute(raw_q):
        key = norm_lemma(lemma)
        if key:
            counts[key] += n
    con.close()
    return finalize(counts)


def finalize(counts):
    """counts: Counter(norm_lemma -> total tokens) -> the full freq table dict."""
    total = sum(counts.values())
    # Pareto: walk lemmas most-frequent first, mark until cumulative >= 80% of corpus.
    core = set()
    cum = 0
    target = total * PARETO_COVERAGE
    for key, n in counts.most_common():
        core.add(key)
        cum += n
        if cum >= target:
            break
    by_lemma = {}
    for key, n in counts.items():
        by_lemma[key] = {
            'count': n,
            'band': band_for(n),
            'hapax': n == 1,
            'core80': key in core,
        }
    return {
        'meta': {
            'source': 'VisualDCS dcs_full.sqlite token table',
            'total_tokens': total,
            'distinct_lemmas': len(counts),
            'band_edges': BAND_EDGES,
            'pareto_coverage': PARETO_COVERAGE,
            'core80_lemma_count': len(core),
            'core80_share_of_lemmas': round(len(core) / max(1, len(counts)), 4),
            'hapax_count': sum(1 for v in by_lemma.values() if v['hapax']),
            'generator': 'build_dcs_freq.py',
        },
        'by_lemma': by_lemma,
    }


def selftest():
    # norm_lemma: joiners, parentheticals, SLP1 leak
    assert norm_lemma('anusam+āp') == 'anusamāp'
    assert norm_lemma('prā-yā') == 'prāyā'
    assert norm_lemma('dhā (vyā+dhā)') == 'dhā'
    assert norm_lemma('aBisam+vas') == 'abhisamvas', norm_lemma('aBisam+vas')
    # sandhi join: vowel-initial roots that plain concat misses
    assert sandhi_join(['pra', 'āp']) == 'prāp', sandhi_join(['pra', 'āp'])
    assert sandhi_join(['vi', 'āp']) == 'vyāp'
    assert sandhi_join(['anu', 'ā']) == 'anvā'
    assert sandhi_join(['upa', 'i']) == 'upe'
    assert sandhi_join(['pra', 'vad']) == 'pravad'          # consonant-initial: concat
    assert sandhi_key('pra+āp') == 'prāp' and sandhi_key('vad') == ''
    # banding + pareto on a tiny synthetic corpus
    c = collections.Counter({'a': 1000, 'b': 50, 'c': 5, 'd': 1})
    t = finalize(c)
    bl = t['by_lemma']
    assert bl['a']['band'] == 5 and bl['b']['band'] == 3 and bl['c']['band'] == 2
    assert bl['d']['band'] == 1 and bl['d']['hapax'] is True
    assert bl['a']['hapax'] is False
    # a=1000 alone is 94.6% > 80% of 1056 -> only 'a' is core80
    assert bl['a']['core80'] is True and bl['b']['core80'] is False
    assert t['meta']['total_tokens'] == 1056 and t['meta']['hapax_count'] == 1
    print('build_dcs_freq selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sqlite', default=DCS_SQLITE)
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not os.path.exists(args.sqlite):
        sys.exit('DCS sqlite not found: %s' % args.sqlite)
    table = build(args.sqlite)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(table, f, ensure_ascii=False)
    m = table['meta']
    print('wrote %s' % args.out)
    print('  total tokens      : %d' % m['total_tokens'])
    print('  distinct lemmas   : %d' % m['distinct_lemmas'])
    print('  hapax lemmas      : %d' % m['hapax_count'])
    print('  core80 lemmas     : %d (%.1f%% of lemmas cover %d%% of tokens)'
          % (m['core80_lemma_count'], 100 * m['core80_share_of_lemmas'],
             int(100 * m['pareto_coverage'])))


if __name__ == '__main__':
    main()
