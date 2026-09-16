# -*- coding: utf-8 -*-
"""mw_nachtrag_typology.py — typology + statistics over the MW/PWK Nachtraege
adjudication TSVs (csl-corrections#119 follow-up, MG request 15-09-2026).

Answers (MG 15-09): what typology does the adjudication support, what subgroups
do the near-form matches fall into, what statistics are still missing, and what
fuzzy-typology conclusions suggest themselves. Every number this script prints
is regenerated from the TSVs in this folder — the companion markdown doc
(MW-NACHTRAG-TYPOLOGY-15-09-2026.md) links each claim to a TSV row anchor.

Inputs (read-only):
  MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv    — the canonical sup_7 adjudication (4,151)
  MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv — star-based all-layer sweep (3,353)
  MW72-CLASSES-ADJUDICATION-15-09-2026.tsv   — MW99 vs MW72 cross-check (4,139)
  optional --mine410  PWG/pwk7 410-row trial cut (csl-corrections#119 trial TSV)

Usage:  python mw_nachtrag_typology.py [--mine410 path]
"""
import argparse
import collections
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

SAME_TRADITION = {'sch', 'pwg'}   # Schmidt's Nachtraege + PW gross = the Boehtlingk tradition
VOWELS = 'aeioufAEIOU'


def load(name):
    path = os.path.join(HERE, name)
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def lev(a, b, cap=6):
    la, lb = len(a), len(b)
    if abs(la - lb) > cap:
        return cap + 1
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        for j in range(1, lb + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        if min(cur) > cap:
            return cap + 1
        prev = cur
    return prev[lb]


PAIRS = {
    ('t', 'T'): 'dental/retroflex t-T', ('T', 't'): 'dental/retroflex t-T',
    ('d', 'D'): 'dental/retroflex d-D', ('D', 'd'): 'dental/retroflex d-D',
    ('n', 'N'): 'dental/retroflex n-N', ('N', 'n'): 'dental/retroflex n-N',
    ('s', 'z'): 'sibilant s-z', ('z', 's'): 'sibilant s-z',
    ('s', 'S'): 'sibilant s-S', ('S', 's'): 'sibilant s-S',
    ('z', 'S'): 'sibilant z-S', ('S', 'z'): 'sibilant z-S',
    ('m', 'M'): 'anusvara m-M', ('M', 'm'): 'anusvara m-M',
    ('M', 'n'): 'anusvara/n M-n', ('n', 'M'): 'anusvara/n M-n',
    ('a', 'A'): 'vowel-length a-A', ('A', 'a'): 'vowel-length a-A',
    ('i', 'I'): 'vowel-length i-I', ('I', 'i'): 'vowel-length i-I',
    ('u', 'U'): 'vowel-length u-U', ('U', 'u'): 'vowel-length u-U',
    ('f', 'F'): 'vocalic-r f-F', ('F', 'f'): 'vocalic-r f-F',
    ('i', 'e'): 'grade i-e', ('e', 'i'): 'grade i-e',
    ('u', 'o'): 'grade u-o', ('o', 'u'): 'grade u-o',
    ('l', 'L'): 'l-L', ('L', 'l'): 'l-L', ('r', 'R'): 'r-R', ('R', 'r'): 'r-R',
}
GRADES = {('i', 'e'), ('e', 'i'), ('u', 'o'), ('o', 'u'), ('f', 'a'), ('a', 'f')}
SUFFIX = {
    ('tAr', 'tf'): '-vant/-tar agent -tar/-tR', ('tf', 'tAr'): '-vant/-tar agent -tR/-tar',
    ('tA', 'tva'): 'abstract -tA/-tva', ('tva', 'tA'): 'abstract -tva/-tA',
    ('in', 'a'): 'agent -in/-a', ('a', 'in'): 'agent -a/-in',
    ('aka', 'a'): 'dimin -aka/-a', ('ika', 'a'): 'dimin -ika/-a',
}
AGENT_FAMS = re.compile(r'(vant|vat)$')


def relation(hw, mw):
    """Classify the near-form relation between a candidate and its MW fuzzy target."""
    if hw == mw:
        return 'identity'
    d = lev(hw, mw)
    p = min(len(hw), len(mw))
    if hw[:p] == mw[:p]:
        return 'compound short/long form'
    if AGENT_FAMS.search(hw) or AGENT_FAMS.search(mw):
        if hw.replace('vant', 'vat') == mw or hw.replace('vat', 'vant') == mw:
            return '-vant/-vat alternation'
    cp = 0
    while cp < min(len(hw), len(mw)) and hw[cp] == mw[cp]:
        cp += 1
    if d == 1 and len(hw) == len(mw):
        i = next(k for k in range(len(hw)) if hw[k] != mw[k])
        return 'single-sub ' + PAIRS.get((hw[i], mw[i]), f'other {hw[i]}-{mw[i]}')
    if d <= 2 and cp >= 3:
        st, mt = hw[cp:], mw[cp:]
        if (st, mt) in SUFFIX:
            return 'suffix ' + SUFFIX[(st, mt)]
        if len(st) <= 3 and len(mt) <= 3:
            if st in ('tar', 'tAr', 'ar') or mt in ('tf', 'f'):
                return '-tar/-tR agent alternation'
            return f'suffix other -{st}/-{mt}'
    if d == 2 and len(hw) == len(mw):
        diff = [k for k in range(len(hw)) if hw[k] != mw[k]]
        pairs = {(hw[k], mw[k]) for k in diff}
        if len(pairs) == 2 and all(pp in GRADES for pp in pairs):
            return 'grade guNa/vRddhi'
        names = collections.Counter(PAIRS.get(pp, f'other {pp[0]}-{pp[1]}') for pp in pairs)
        return 'double-sub ' + ' + '.join(n for n, _ in names.most_common(2))
    return f'multi-edit d{d}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mine410', default=None, help='path to the 410-row trial cut TSV')
    args = ap.parse_args()

    rows = load('MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv')
    out = collections.OrderedDict()

    # 1. verdict distribution
    out['verdicts'] = collections.Counter(r['verdict'] for r in rows)

    # 2. fuzzy-score buckets x verdict
    buck = collections.Counter()
    for r in rows:
        m = re.match(r'nearform([0-9.]+)', r['pipeline_tier'])
        if not m:
            continue
        s = float(m.group(1))
        b = '0.8' if s < 0.9 else ('0.9' if s < 0.95 else '0.95+')
        buck[(b, r['verdict'])] += 1
    out['score_buckets'] = buck

    # 3. near-form relation families x verdict
    rel_v = collections.defaultdict(collections.Counter)
    for idx, r in enumerate(rows):
        if not r['pipeline_tier'].startswith('nearform') or not r['mw_fuzzy']:
            continue
        rel_v[relation(r['hw_slp1'], r['mw_fuzzy'])][r['verdict']] += 1
    out['families'] = rel_v

    # 4. corroboration, same-tradition vs outside-PW
    def outside(r):
        return [d for d in (r['corr_dicts'] or '').split(';') if d and d not in SAME_TRADITION]
    out['outside'] = collections.Counter(len(outside(r)) for r in rows)
    out['outside>=2 verdicts'] = collections.Counter(r['verdict'] for r in rows if len(outside(r)) >= 2)
    out['witnesses'] = collections.Counter(d for r in rows for d in (r['corr_dicts'] or '').split(';') if d)
    out['witnesses_outside'] = collections.Counter(d for r in rows for d in outside(r))

    # 5. MAHĀVY / DCS cross-tabs
    out['mahavy'] = collections.Counter(r['verdict'] for r in rows if r['mahavy'] == '1')
    dcs = [r for r in rows if r['dcs_form'] == '1' or r['dcs_lemma'] == '1']
    out['dcs'] = collections.Counter(r['verdict'] for r in dcs)
    out['dcs+outside>=1'] = sum(1 for r in dcs if len(outside(r)) >= 1)
    out['dcs+outside>=2 cm'] = sum(1 for r in dcs if len(outside(r)) >= 2 and r['verdict'] == 'confirmed-missing')

    # 6. MW72 cross-check
    m72 = load('MW72-CLASSES-ADJUDICATION-15-09-2026.tsv')
    out['mw72'] = collections.Counter(r['class'] for r in m72)

    # 7. starred sweep + overlap with the 410-row cut
    star = load('MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv')
    out['starred'] = collections.Counter(r.get('verdict', '') for r in star)
    if args.mine410:
        mine = list(csv.DictReader(open(args.mine410, encoding='utf-8'), delimiter='\t'))
        sidx = {r.get('hw_slp1'): r for r in star}
        mdict = {r['k1'] for r in mine}
        hit = [(k, idx_r) for k in mdict for idx_r in [next((r for r in rows if r['hw_slp1'] == k), None)] if idx_r]
        sh = [(k, sidx[k]) for k in mdict if k in sidx]
        out['mine410'] = {
            'n': len(mine),
            'in_sup7': len(hit),
            'in_sup7_verdicts': collections.Counter(v['verdict'] for _, v in hit),
            'in_starred': len(sh),
            'in_starred_verdicts': collections.Counter(v.get('verdict', '') for _, v in sh),
            'not_in_sup7_sample': [k for k in mdict if k not in {r['hw_slp1'] for r in rows}][:10],
        }

    # ---- print ----
    print(f'rows: {len(rows)}')
    print('\n== verdicts ==')
    for k, n in out['verdicts'].most_common():
        print(f'  {k:32s} {n:5d}')
    print('\n== near-form score buckets x verdict ==')
    fams = ('confirmed-missing', 'near-form-needs-eyes', 'covered-by-fold-twin-flagged')
    for b in ('0.8', '0.9', '0.95+'):
        line = '  ' + b + ': '
        line += ' '.join(f'{v}={buck.get((b, v), 0)}' for v in fams)
        print(line)
    print('\n== near-form relation families (top 14) ==')
    for k, c in sorted(rel_v.items(), key=lambda kv: -sum(kv[1].values()))[:14]:
        tot = sum(c.values())
        print(f'  {tot:5d}  {k:44s} missing={c.get("confirmed-missing",0):4d} eyes={c.get("near-form-needs-eyes",0):4d} fold={c.get("covered-by-fold-twin-flagged",0):4d}')
    ne = sorted(((k, c.get('near-form-needs-eyes', 0)) for k, c in rel_v.items()), key=lambda x: -x[1])
    print('\n== needs-eyes residue: top families ==')
    for k, n in ne[:8]:
        print(f'  {n:5d}  {k}')
    print('\n== corroboration ==')
    print('  witnesses (incl. same tradition):', out['witnesses'].most_common(8))
    print('  outside-PW witnesses:', out['witnesses_outside'].most_common(8))
    print('  outside-corr histogram:', dict(sorted(out['outside'].items())))
    print('  >=2 outside verdicts:', dict(out['outside>=2 verdicts']))
    print('\n== MAHĀVY / DCS ==')
    print('  mahavy=1 verdicts:', dict(out['mahavy']))
    print('  dcs-attested verdicts:', dict(out['dcs']), '| dcs & >=1 outside:', out['dcs+outside>=1'],
          '| dcs & >=2 outside & confirmed-missing:', out['dcs+outside>=2 cm'])
    print('\n== MW72 cross-check ==', dict(out['mw72']))
    print('\n== starred sweep ==', dict(out['starred']))
    if args.mine410:
        m = out['mine410']
        print('\n== 410-row cut overlap ==')
        print(f"  n={m['n']}; in sup_7 pool: {m['in_sup7']} {dict(m['in_sup7_verdicts'])}")
        print(f"  in starred sweep: {m['in_starred']} {dict(m['in_starred_verdicts'])}")
        print('  not in sup_7 pool (Verbesserungen/corrections class):', m['not_in_sup7_sample'])


if __name__ == '__main__':
    main()
