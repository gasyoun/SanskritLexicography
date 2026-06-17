#!/usr/bin/env python
"""Layered multi-dictionary merge — the spine of the complete pwg_ru.

Per the architecture: PWG is the base; PW (revision) + SCH/PWKVN (supplements) +
NWS (external, later) overlay it. This module indexes the local Cologne layers by
SLP1 headword and assembles, for any key, the union across dictionaries — each
record tagged with its source + role, so the translator/editor sees the fullest
picture and the conflicts (e.g. PWG gender vs PW gender).

  python dict_merge.py stats                 records + headword coverage per layer
  python dict_merge.py merge <key1>          the layered view of one headword
"""
import os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
V02 = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02'))

# layer code → (role, blurb). NWS added once scraped.
LAYERS = [
    ('pwg',   'base',       'PWG — Böhtlingk-Roth, large (1855-75)'),
    ('pw',    'revision',   'PW/PWK — Böhtlingk, kürzere Fassung (1879-89)'),
    ('sch',   'supplement', 'SCH — Schmidt, Nachträge (1928)'),
    ('pwkvn', 'supplement', 'PWKVN — PWK variant supplement'),
]


def records_of(code):
    path = os.path.join(V02, code, code + '.txt')
    if not os.path.exists(path):
        return
    buf = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('<L>'):
            buf = [line]
        elif line.startswith('<LEND>'):
            if buf:
                yield buf
            buf = []
        elif buf:
            buf.append(line)


_IDX = {}
def index(code):
    if code in _IDX:
        return _IDX[code]
    idx = collections.defaultdict(list)
    for buf in records_of(code):
        m = pwg_mask.HEADER_RE.match(buf[0])
        if m:
            idx[cg.form_key(m.group(3))].append(buf)
    _IDX[code] = idx
    return idx


def merged(key1):
    fk = cg.form_key(key1)
    out = []
    for code, role, blurb in LAYERS:
        recs = index(code).get(fk, [])
        if recs:
            out.append({'layer': code, 'role': role, 'blurb': blurb,
                        'records': ['\n'.join(b[1:]) for b in recs]})
    return out


def cmd_stats(args):
    print('%-7s %-11s %9s %9s' % ('layer', 'role', 'records', 'headwords'))
    for code, role, blurb in LAYERS:
        idx = index(code)
        print('%-7s %-11s %9d %9d   %s'
              % (code, role, sum(len(v) for v in idx.values()), len(idx), blurb))
    # how many PWG headwords gain extra material from a later layer
    pwg = set(index('pwg'))
    for code, role, _ in LAYERS[1:]:
        k = set(index(code))
        print('  %s: %d headwords; %d NOT in PWG (net-new), %d also in PWG (overlay)'
              % (code, len(k), len(k - pwg), len(k & pwg)))


def cmd_merge(args):
    key1 = args[0]
    layers = merged(key1)
    if not layers:
        print('no entry for %r in any layer' % key1); return
    print('=== %s — %d layer(s) ===' % (key1, len(layers)))
    for L in layers:
        print('\n## [%s · %s] %s  (%d record(s))' % (L['layer'].upper(), L['role'], L['blurb'], len(L['records'])))
        for r in L['records']:
            print('  ' + re.sub(r'\s+', ' ', r)[:600])


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'stats': cmd_stats, 'merge': cmd_merge}.get(sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
