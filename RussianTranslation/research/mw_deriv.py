#-*- coding:utf-8 -*-
"""mw_deriv.py — authoritative MW derivation oracle (Funderburk's MWderivations).

Replaces the FAKED derivation parser in lex_noun_link.py for the MW side. Source:
funderburkjim/MWderivations step4/analysis2.txt (220k MW headwords, ~95% resolved),
same author as PWG/verbs01 — so it dovetails with the preverb work and needs no
re-derivation.

Each row (tab-separated): Hcode, L, key1, key2(hyphenated), gender, parse, status, method.
The METHOD column already classifies the derivation:
  pfx1:/pfx2:<upa>  -> prefixed verb (preverb split)         anuBU  -> anu-BU
  cpd1..5 / srs2..  -> compound (samasa)                      aMSaBU -> aMSa-BU
  wsfx:<suffix>     -> word + krt/taddhita suffix             X-tva, X-tA, X-vat
  noparts           -> primary stem (a root / unanalysable)   BU
  init/NTD/SEE/...   -> unresolved or auxiliary

Data is vendored (gitignored) under external/; re-fetch from
https://github.com/funderburkjim/MWderivations  (step4/analysis2.txt).

  python mw_deriv.py demo            # classify the BU family + class distribution
  python mw_deriv.py split <key1>    # show one headword's derivation
"""
from __future__ import print_function
import os, sys, re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.join(HERE, 'external', 'mwderiv_analysis2.txt')


def classify(method):
    if method.startswith('pfx'):
        return 'preverb'
    if method.startswith(('cpd', 'srs')):
        return 'compound'
    if method.startswith('wsfx'):
        return 'suffix'
    if method == 'noparts':
        return 'primary'
    return 'unresolved'


def parts(parse):
    """Split the parse field (anu-BU, aMSa+avataraRa, aMSa-BU) into members."""
    p = [x for x in re.split(r'[-+~@]', parse) if x]
    return p


def load(path=ANALYSIS):
    """key1 -> list of {gender, parse, method, klass, parts, status}."""
    d = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            c = line.rstrip('\n').split('\t')
            if len(c) < 8:
                continue
            key1, key2, gender, parse, status, method = c[2], c[3], c[4], c[5], c[6], c[7]
            rec = {'key2': key2, 'gender': gender, 'parse': parse, 'status': status,
                   'method': method, 'klass': classify(method),
                   'parts': parts(parse) if parse else []}
            d.setdefault(key1, []).append(rec)
    return d


def best(recs):
    """Pick the resolved nominal derivation (skip VERB/SEE/init aux rows)."""
    done = [r for r in recs if r['status'] == 'DONE' and r['klass'] != 'unresolved']
    return done[0] if done else (recs[0] if recs else None)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    if not os.path.exists(ANALYSIS):
        print('missing %s — fetch from github.com/funderburkjim/MWderivations' % ANALYSIS)
        return
    D = load()
    if cmd == 'split':
        for r in D.get(sys.argv[2], []):
            print('  %-10s %-8s %-12s %-7s parts=%s'
                  % (r['method'], r['klass'], r['parse'], r['gender'], r['parts']))
    else:
        from collections import Counter
        cl = Counter()
        for recs in D.values():
            b = best(recs)
            if b:
                cl[b['klass']] += 1
        print('MW derivation oracle: %d distinct headwords' % len(D))
        print('  class distribution (best resolved per headword):')
        for k, n in cl.most_common():
            print('    %-11s %6d' % (k, n))
        print('  BU-family sample:')
        for kw in ('BU', 'anuBU', 'aBiBU', 'praBU', 'aMSaBU', 'aMSaBUta', 'aBiBava'):
            b = best(D.get(kw, []))
            if b:
                print('    %-10s -> %-9s %-10s parts=%s' % (kw, b['klass'], b['parse'], b['parts']))


if __name__ == '__main__':
    main()
