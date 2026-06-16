#!/usr/bin/env python
"""Authoritative PWG <ab> grammatical-abbreviation resolver — from PWG's pwgab table.

PWG's general abbreviations (Interj., ved., Bein., m., Pl., Acc. …) expand from
csl-pywork .../pwgab/pwgab_input.txt (~791 entries: ABBREV<tab><id>..</id>
<disp>German - English</disp>). This gives authoritative grammar / diasystem /
usage labels, replacing the hand DIA map in microstructure.

  python pwg_ab.py lookup <abbrev>
  python pwg_ab.py coverage          <ab> coverage of pwg.txt
"""
import os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
GH = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
AB = os.path.join(GH, 'csl-pywork', 'v02', 'distinctfiles', 'pwg', 'pywork', 'pwgab', 'pwgab_input.txt')
PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
DISP = re.compile(r'<disp>(.*?)</disp>')
ABTAG = re.compile(r'<ab\b([^>]*)>(.*?)</ab>', re.S)
NATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')

# which English labels are diachronic/register (diasystem) vs plain grammar
DIASYSTEM = {'vedic', 'classical', 'epic', 'late'}


def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip())


_AB = None
def table():
    global _AB
    if _AB is None:
        _AB = {}
        for line in open(AB, encoding='utf-8'):
            if '\t' not in line:
                continue
            ab, rest = line.split('\t', 1)
            d = DISP.search(rest)
            disp = d.group(1).strip() if d else ''
            de, en = (disp.split(' - ', 1) + [disp])[:2] if ' - ' in disp else (disp, disp)
            k = norm(ab)
            if k and k not in _AB:
                _AB[k] = {'abbrev': ab.strip(), 'de': de.strip(), 'en': en.strip()}
    return _AB


def resolve(token):
    return table().get(norm(token))


def label(token):
    r = resolve(token)
    return r['en'] if r else None


def is_diasystem(en):
    return any(d in (en or '').lower() for d in DIASYSTEM)


def cmd_lookup(args):
    r = resolve(args[0])
    print('%s = %s / %s' % (r['abbrev'], r['de'], r['en']) if r else '(not in pwgab)')


def cmd_coverage(args):
    freq = collections.Counter()
    data = open(PWG, encoding='utf-8').read()
    for attrs, content in ABTAG.findall(data):
        if NATTR.search(attrs):          # local <ab n="Y"> carries its own expansion
            continue
        k = norm(re.sub(r'<[^>]+>', '', content))
        if k:
            freq[k] += 1
    total = sum(freq.values())
    res = sum(c for k, c in freq.items() if resolve(k))
    print('pwgab entries: %d' % len(table()))
    print('PWG <ab> (global): %d uses, %d distinct' % (total, len(freq)))
    print('resolved: %d/%d distinct (%.1f%%), %d/%d uses (%.1f%%)'
          % (sum(1 for k in freq if resolve(k)), len(freq),
             100.0 * sum(1 for k in freq if resolve(k)) / len(freq), res, total, 100.0 * res / total))
    print('top unresolved:')
    for k, c in [(k, c) for k, c in freq.most_common() if not resolve(k)][:15]:
        print('  %-16s %d' % (k, c))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'lookup': cmd_lookup, 'coverage': cmd_coverage}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
