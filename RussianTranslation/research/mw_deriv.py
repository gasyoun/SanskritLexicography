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


def resolve_chain(key1, D, seen=None):
    """Follow the head member (parts[-1]) to the ultimate root. -> {root, depth, lwc, chain}.
    This is the MW analogue of lex_noun_link's chain, but sourced from the authoritative
    MWderivations analysis instead of parsed prose."""
    seen = seen or set()
    if key1 in seen or len(seen) > 12:
        return None
    seen = seen | {key1}
    b = best(D.get(key1, []))
    if not b:
        return None
    if b['klass'] == 'primary' or not b['parts']:
        return {'root': key1, 'depth': 0, 'lwc': False, 'chain': [key1]}
    head = b['parts'][-1]
    sub = resolve_chain(head, D, seen)
    if sub:
        return {'root': sub['root'], 'depth': sub['depth'] + 1,
                'lwc': (b['klass'] == 'compound') or sub['lwc'], 'chain': [key1] + sub['chain']}
    return {'root': head, 'depth': 1, 'lwc': b['klass'] == 'compound', 'chain': [key1, head]}


def write_link_table(D):
    """Emit mw_noun_link.tsv — the MW side of lex_noun_link, from the authoritative source."""
    rows = 0
    out = os.path.join(HERE, 'mw_noun_link.tsv')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('headword\troot_key\tklass\tdepth\tis_leading_word_compound\tchain\n')
        for key1, recs in D.items():
            b = best(recs)
            if not b or b['klass'] not in ('compound', 'preverb', 'suffix'):
                continue
            ch = resolve_chain(key1, D)
            if not ch:
                continue
            f.write('%s\t%s\t%s\t%d\t%s\t%s\n' % (key1, ch['root'], b['klass'],
                    ch['depth'], ch['lwc'], '>'.join(ch['chain'])))
            rows += 1
    print('  wrote %d MW link rows -> %s' % (rows, os.path.basename(out)))
    return rows


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    if not os.path.exists(ANALYSIS):
        print('missing %s — fetch from github.com/funderburkjim/MWderivations' % ANALYSIS)
        return
    D = load()
    if cmd == 'link':
        write_link_table(D)
    elif cmd == 'split':
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
