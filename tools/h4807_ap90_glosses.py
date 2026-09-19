#!/usr/bin/env python3
"""H4807 — AP90 (Apte 1890) English-gloss extractor, Cologne <L> records.

Reuses the sanctioned MW cleaner approach (mw_en_tm.py) adapted to AP90 markup:
Sanskrit sits in {#...#} spans; English prose may sit in {%...%}; residual
<ab>/<lbinfo>/<ls>/{@..@} tags stripped.

Output: { slp1_headword: "english gloss; english gloss; ..." } JSON.
Selftest: python3 h4807_ap90_glosses.py --selftest
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AP90 = os.environ.get('AP90_TXT', os.path.normpath(
    os.path.join(HERE, '..', '..', 'csl-orig', 'v02', 'ap90', 'ap90.txt')))
OUT = os.path.join(HERE, 'h4807_ap90_glosses.json')
CAP = 700

_K1 = re.compile(r'<k1>(.*?)<')
_SKT = re.compile(r'\{#.*?#\}', re.S)          # Devanagari/SLP1 spans (drop)
_LAT = re.compile(r'\{%([^%]*?)%\}')           # keep Latin/English italics content
_TAG = re.compile(r'</?(?:ab|b|lbinfo|ls|lex|s|lang|etym)[^>]*/?>')
_TAGPAIR = re.compile(r'<(ab|lex)>(.*?)</\1>', re.S)
_CURLY = re.compile(r'\{@[^@]*@\}')            # number markers


def clean_body(body):
    t = _TAGPAIR.sub(' ', body)
    t = _SKT.sub(' ', t)
    t = _LAT.sub(r' \1 ', t)
    t = _TAG.sub(' ', t)
    t = _CURLY.sub(' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'[ \t]*\n[ \t]*', ' ', t)
    t = re.sub(r'\([\s;,.&c]*\)', ' ', t)
    t = re.sub(r'\s*([;,])(\s*[;,])+', r'\1 ', t)
    t = re.sub(r'^[\s\d.;,()]+', '', t)
    t = re.sub(r'\s{2,}', ' ', t).strip(' ;,.|')
    return t


def records(path):
    k1 = None
    body = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('<L>'):
                if k1 is not None:
                    yield k1, '\n'.join(body)
                k1 = None
                body = []
                m = _K1.search(line)
                if m:
                    k1 = m.group(1)
                continue
            if k1 is not None:
                body.append(line.rstrip('\n'))
    if k1 is not None:
        yield k1, '\n'.join(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--out', default=OUT)
    args = ap.parse_args()
    if not os.path.exists(AP90):
        sys.exit('FATAL: %s missing' % AP90)
    out = {}
    n = 0
    for k1, body in records(AP90):
        n += 1
        t = clean_body(body)
        if t:
            out[k1] = t[:CAP]
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)
    if args.selftest:
        assert n > 30000, 'too few records: %d' % n
        probe = out.get('aha')
        assert probe and 'particle' in probe.lower(), 'aha probe failed: %r' % probe
        print('AP90 selftest OK records=%d glossed=%d' % (n, len(out)))
        return
    print('wrote %s records=%d glossed=%d' % (args.out, n, len(out)))


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
    except AttributeError:
        pass
    main()
