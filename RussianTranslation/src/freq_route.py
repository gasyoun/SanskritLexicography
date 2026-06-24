#!/usr/bin/env python
"""Frequency-first card ordering — DCS hybrid token x breadth x richness.

Ranks PWG headwords so the words readers meet most get translated first (2026-06-23
pivot; supersedes scale_route's alphabetical/coverage order for the bulk). Composite:
  token    = DCS occurrence band 1-5 (log10 orders; ../../../VisualDCS/dcs_lemma_summary.json,
             SLP1-keyed — matches PWG key1 natively)
  breadth  = DCS document frequency n_texts (dcs_lemma_renou.json, IAST-keyed)
  richness = PWG entry content, cheap proxy = record body bytes (no portraits needed)
score = max(band,0.5) * log10(n_texts+2) * log10(bytes+10).  Attested = band>=1 or n_texts>=1.

  python freq_route.py [N]     write pilot/output/scale_manifest.freq.json + show top N (default 50)
"""
import json, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'VisualDCS', 'dcs_lemma_summary.json'))
RENOU = os.path.join(HERE, 'dcs_lemma_renou.json')
OUT = os.path.join(HERE, 'pilot', 'output', 'scale_manifest.freq.json')


def iast(k):
    return ''.join(cg._S2I.get(c, c) for c in k)


def main():
    topn = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 50
    band = {k: v.get('freqBand', 0) for k, v in json.load(open(SUMMARY, encoding='utf-8'))['lemmas'].items()}
    ntexts = {k: v.get('n_texts', 0) for k, v in json.load(open(RENOU, encoding='utf-8')).items()
              if isinstance(v, dict)}   # skip meta keys (e.g. __sources__, whose value is a list)

    agg = {}                                   # form_key -> aggregated headword
    for buf in pwg_mask.records():
        m = pwg_mask.HEADER_RE.match(buf[0])
        if not m:
            continue
        k1 = m.group(3)
        fk = cg.form_key(k1)
        body = sum(len(l.encode('utf-8')) for l in buf[1:])
        b = band.get(k1) or band.get(fk) or 0
        nt = ntexts.get(iast(k1), 0)
        a = agg.get(fk)
        if a is None:
            agg[fk] = {'key1': k1, 'band': b, 'n_texts': nt, 'bytes': body, 'recs': 1}
        else:                                  # merge homonyms: max signal, sum content
            a['band'] = max(a['band'], b); a['n_texts'] = max(a['n_texts'], nt)
            a['bytes'] += body; a['recs'] += 1

    rows = []
    for a in agg.values():
        if a['band'] < 1 and a['n_texts'] < 1:
            continue                           # DCS-attested only (the core)
        score = max(a['band'], 0.5) * math.log10(a['n_texts'] + 2) * math.log10(a['bytes'] + 10)
        rows.append({'key1': a['key1'], 'score': round(score, 3), 'band': a['band'],
                     'n_texts': a['n_texts'], 'bytes': a['bytes'], 'recs': a['recs']})
    rows.sort(key=lambda r: -r['score'])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rows, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total = len(agg)
    print('PWG headwords: %d | DCS-attested (ranked): %d (%.0f%%) -> %s'
          % (total, len(rows), 100 * len(rows) / total, os.path.relpath(OUT, HERE)))
    # band histogram of the attested set
    import collections
    h = collections.Counter(r['band'] for r in rows)
    print('band histogram (attested):', dict(sorted(h.items(), reverse=True)))
    print('\ntop %d by composite score:' % topn)
    print('  %-4s %-14s %-8s %-5s %-8s %s' % ('#', 'key1 (SLP1)', 'score', 'band', 'n_texts', 'iast'))
    for i, r in enumerate(rows[:topn], 1):
        print('  %-4d %-14s %-8.2f %-5d %-8d %s' % (i, r['key1'], r['score'], r['band'], r['n_texts'], iast(r['key1'])))


if __name__ == '__main__':
    main()
