#!/usr/bin/env python
r"""Annotate the translated store with DCS frequency fields (Macmillan-style band).

Consumes src/dcs_freq.json (build_dcs_freq.py) and adds, to every row of
src/pwg_ru_translated.jsonl, a 'dcs_freq' block:

  "dcs_freq": {
    "band": 1-5 | 0,        # 0 = absent from DCS; 5 = most frequent (>=1000 tokens)
    "count": int,           # raw aggregated DCS token count (0 if absent)
    "hapax": bool,          # exactly one DCS occurrence
    "attested": bool,       # present in DCS at all
    "core80": bool,         # in the ~2.8% of lemmas covering 80% of the corpus
    "matched": "compound" | "root_fallback" | "none",
    "matched_key": "<normalized lemma actually looked up>"
  }

Lookup order (per MG: per preverb-compound form, root fallback):
  1. the row's own 'iast' normalized (e.g. 'anu+vad' -> 'anuvad') = the compound form;
  2. if that misses and the form is a compound, the rightmost element (the bare root;
     Sanskrit preverbs precede the root, so 'anu+vad' -> 'vad');
  3. otherwise absent -> band 0, attested false.

Idempotent and in-place (writes a .bak unless --no-backup). Re-runnable after the bridge.

  python src/annotate_dcs_freq.py                 # annotate the store in place
  python src/annotate_dcs_freq.py --dry-run        # coverage report only
  python src/annotate_dcs_freq.py --selftest
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from build_dcs_freq import norm_lemma, sandhi_key   # canonical normalizer + sandhi joiner

HERE = os.path.dirname(os.path.abspath(__file__))
FREQ = os.path.join(HERE, 'dcs_freq.json')
DIMS = os.path.join(HERE, 'dcs_freq_dims.json')   # genre + POS dimensions (optional)
STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')

_SPLIT = re.compile(r'[+\-\s]+')


def root_tail(iast):
    """Rightmost element of a preverb compound = the bare root. '' if not a compound."""
    if not iast:
        return ''
    head = re.sub(r'\s*\([^)]*\)', '', iast).strip()      # drop parentheticals first
    parts = [p for p in _SPLIT.split(head) if p]
    return parts[-1] if len(parts) > 1 else ''


def lookup(iast, by_lemma):
    """-> (record_or_None, match_kind, matched_key). Tries, in order:
    plain-concat compound -> sandhi-joined compound -> bare-root fallback."""
    key = norm_lemma(iast)
    if key in by_lemma:
        return by_lemma[key], 'compound', key
    sk = sandhi_key(iast)
    if sk and sk in by_lemma:
        return by_lemma[sk], 'compound_sandhi', sk
    tail = norm_lemma(root_tail(iast))
    if tail and tail in by_lemma:
        return by_lemma[tail], 'root_fallback', tail
    return None, 'none', ''


def freq_block(iast, by_lemma):
    rec, kind, mkey = lookup(iast, by_lemma)
    if rec is None:
        return {'band': 0, 'count': 0, 'hapax': False, 'attested': False,
                'core80': False, 'matched': 'none', 'matched_key': ''}
    return {'band': rec['band'], 'count': rec['count'], 'hapax': rec['hapax'],
            'attested': True, 'core80': rec['core80'],
            'matched': kind, 'matched_key': mkey}


def dims_block(iast, by_lemma):
    """Attach POS distribution + genre/era counts (build_dcs_freq_dims). {} if absent."""
    rec, kind, mkey = lookup(iast, by_lemma)
    if not rec:
        return {}
    out = {'matched': kind, 'matched_key': mkey}
    if 'pos' in rec:
        out['pos'] = rec['pos']
    if 'genre' in rec:
        out['genre'] = rec['genre']
    if 'era' in rec:
        out['era'] = rec['era']
    return out


def dcs_registers_for(db):
    """Lane 2 (frequency-weighted, corpus-attested): the sorted register-code vector
    from a dims_block's genre counts, e.g. ['epic', 'kavya']. [] when unmatched or
    register-less. Distinct from and NEVER merged with the citation-derived `genre`
    field (annotate_genres.py, lane 1: 'PWG cites this sense from a kāvya work') —
    the two answer different questions (see W4, PIPELINE_CAPABILITY_AUDIT_2026-07-08.md)."""
    if not db:
        return []
    return sorted((db.get('genre') or {}).get('counts', {}))


def selftest():
    by = {'anuvad': {'count': 5, 'band': 2, 'hapax': False, 'core80': False},
          'vad': {'count': 3918, 'band': 5, 'hapax': False, 'core80': True},
          'prāp': {'count': 2328, 'band': 5, 'hapax': False, 'core80': True},
          'kvip': {'count': 1, 'band': 1, 'hapax': True, 'core80': False}}
    # compound hit
    b = freq_block('anu+vad', by)
    assert b['matched'] == 'compound' and b['band'] == 2 and b['attested']
    # vowel-sandhi compound: pra+āp -> prāp (was a root_fallback before)
    b = freq_block('pra+āp', by)
    assert b['matched'] == 'compound_sandhi' and b['matched_key'] == 'prāp' and b['band'] == 5
    # compound miss -> root fallback to rightmost element
    b = freq_block('pratyabhi+vad', by)
    assert b['matched'] == 'root_fallback' and b['matched_key'] == 'vad' and b['band'] == 5
    # parenthetical + simple
    b = freq_block('kvip (kṣ)', by)
    assert b['matched'] == 'compound' and b['hapax'] is True
    # absent
    b = freq_block('zzz+qqq', by)
    assert b['matched'] == 'none' and b['band'] == 0 and b['attested'] is False
    # dcs_registers: sorted register-code vector from a dims_block, [] when absent
    assert dcs_registers_for({'genre': {'counts': {'kavya': 12, 'epic': 3}}}) == ['epic', 'kavya']
    assert dcs_registers_for({}) == []
    assert dcs_registers_for(None) == []
    print('annotate_dcs_freq selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--freq', default=FREQ)
    ap.add_argument('--dims', default=DIMS)
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    by_lemma = json.load(open(args.freq, encoding='utf-8'))['by_lemma']
    dims = {}
    if os.path.exists(args.dims):
        dims = json.load(open(args.dims, encoding='utf-8'))['by_lemma']
    rows = [json.loads(l) for l in open(args.store, encoding='utf-8') if l.strip()]

    kinds = {'compound': 0, 'compound_sandhi': 0, 'root_fallback': 0, 'none': 0}
    bands = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    hapax = core = pos_n = genre_n = 0
    for r in rows:
        blk = freq_block(r.get('iast'), by_lemma)
        r['dcs_freq'] = blk
        kinds[blk['matched']] += 1
        bands[blk['band']] += 1
        hapax += blk['hapax']
        core += blk['core80']
        if dims:
            db = dims_block(r.get('iast'), dims)
            if db:
                r['dcs_freq']['pos'] = db.get('pos')
                r['dcs_freq']['genre'] = db.get('genre')
                r['dcs_freq']['era'] = db.get('era')
                pos_n += 1 if db.get('pos') else 0
                genre_n += 1 if db.get('genre') else 0
            r['dcs_registers'] = dcs_registers_for(db)   # lane 2, sibling of annotate_genres' `genre`

    n = len(rows)
    print('=== DCS FREQUENCY ANNOTATION ===')
    print('store rows           : %d' % n)
    print('matched compound     : %d (%.1f%%)' % (kinds['compound'], 100 * kinds['compound'] / max(1, n)))
    print('matched sandhi-compound: %d (%.1f%%)' % (kinds['compound_sandhi'], 100 * kinds['compound_sandhi'] / max(1, n)))
    print('matched root-fallback: %d (%.1f%%)' % (kinds['root_fallback'], 100 * kinds['root_fallback'] / max(1, n)))
    print('absent from DCS      : %d (%.1f%%)' % (kinds['none'], 100 * kinds['none'] / max(1, n)))
    print('band distribution    : ' + ', '.join('%d:%d' % (b, bands[b]) for b in range(5, -1, -1)))
    print('hapax rows           : %d' % hapax)
    print('core80 rows          : %d' % core)
    if dims:
        print('rows with POS dist   : %d (%.1f%%)' % (pos_n, 100 * pos_n / max(1, n)))
        print('rows with genre dist : %d (%.1f%%)' % (genre_n, 100 * genre_n / max(1, n)))

    if args.dry_run:
        print('\n(dry run — store not written)')
        return
    if not args.no_backup:
        os.replace(args.store, args.store + '.prefreq.bak')
    with open(args.store, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('\nwrote annotated store -> %s' % args.store)


if __name__ == '__main__':
    main()
