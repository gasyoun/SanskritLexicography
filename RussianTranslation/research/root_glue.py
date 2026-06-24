#-*- coding:utf-8 -*-
"""root_glue.py — SPLIT -> NESTED glue (presentation view), PWG + MW.

The inverse direction of root_segment_proto.py: collect the sub-cards / scattered
records that share a verbal root_key and emit ONE nested root article, ordered by the
existing parse string. Presentation-only and lossy-by-bytes by design (it reorders /
merges whole cards; it does not reproduce any single source byte-region).

Ordering ("by the parse string"): simple verb first, then prefixed forms sorted under
Sanskrit (SLP1 varna) collation on the parse decomposition, so forms group by shared
outer prefix (anu+BU, anu+A+BU, anu+sam+BU ... then aBi+..., ...). This is dict-
independent on purpose: we merge dicts, so we impose one canonical order rather than
any single dictionary's native (Devanagari-alphabetical for PWG/GRA) sequence.

Modes:
  PWG: segment a root <L> record (reuses root_segment_proto) and reorder its sub-cards.
       Parse strings come from PWG/verbs01/pwg_preverb1.txt (already computed); a
       sub-card with no match falls back to a single-prefix parse.
  MW : scan mw.txt, collect the genuineroot/root head + every verb="pre" record whose
       parse is upasarga(s)+root (cvi/denominal forms like kfzRI+BU are excluded), and
       assemble. MW carries parse="..." natively, so no inference.

Usage:
  python root_glue.py pwg ../../../csl-orig/v02/pwg/pwg.txt 55166 [--preverb PATH]
  python root_glue.py mw  ../../../csl-orig/v02/mw/mw.txt  BU
"""
from __future__ import print_function
import sys, re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import root_segment_proto as seg  # reuse read_record(), segment()

# Canonical upasarga / gati set (SLP1) — the classifier that separates true preverbs
# from cvi/denominal parse forms (kfzRI+BU, ekI+BU, a+punar+BU ...).
UPASARGAS = {
    'pra', 'parA', 'apa', 'sam', 'anu', 'ava', 'nis', 'nir', 'dus', 'dur', 'vi', 'A',
    'ni', 'aDi', 'api', 'ati', 'su', 'ud', 'aBi', 'prati', 'pari', 'upa',
    'antaH', 'Avis', 'tiras', 'puras', 'prAdus',
}

# SLP1 varna (alphabetical) order, for collating the parse decomposition.
SLP1_ORDER = "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh"
RANK = {c: i for i, c in enumerate(SLP1_ORDER)}


def slp1_key(s):
    return tuple(RANK.get(c, 99) for c in s)


def parse_sort_key(parse):
    """Simple verb (no parse / no prefix) first, then by outer->inner prefix collation."""
    if not parse:
        return (0,)
    elems = parse.split('+')
    pres = elems[:-1]            # drop the root
    if not pres:
        return (0,)
    return (1,) + tuple(slp1_key(p) for p in pres)


# ---------------------------------------------------------------- PWG ----------
def load_preverb_parses(path, L):
    """(L, surface-upasarga) -> parse string, from pwg_preverb1.txt."""
    d = {}
    curL = None
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                m = re.match(r';; Case \d+: L=(\S+?),', line)
                if m:
                    curL = m.group(1)
                    continue
                # per-upasarga line: "01  ati  BU  atiBU  atiBU yes ati+BU"
                m = re.match(r'\s*\d+\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\s*$', line)
                if m and curL is not None:
                    d[(curL, m.group(1))] = m.group(2)
    except FileNotFoundError:
        print('  (note: %s not found — falling back to single-prefix parses)' % path)
    return {k: v for k, v in d.items() if k[0] == L}


def glue_pwg(path, L, preverb_path):
    rec = seg.read_record(path, L)
    if rec is None:
        print('L=%s not found' % L); return False
    meta, data, lend = rec
    k1 = (re.search(r'<k1>([^<]*)', meta) or [None, '?'])[1]
    cards = seg.segment(data)
    pmap = load_preverb_parses(preverb_path, L)
    head = [c for c in cards if c['kind'] != 'prefix']
    pref = [c for c in cards if c['kind'] == 'prefix']
    for c in pref:
        c['parse'] = pmap.get((L, c['upasarga']), '%s+%s' % (c['upasarga'], k1))
    pref.sort(key=lambda c: parse_sort_key(c['parse']))
    new_data = []
    for c in head:
        new_data.extend(c['lines'])
    for c in pref:
        new_data.extend(c['lines'])
    content_ok = sorted(new_data) == sorted(data)   # same lines, only reordered
    print('PWG glue  L=%s k1=%s : %d sub-cards reordered (1 head + %d prefix)  content-preserving=%s'
          % (L, k1, len(cards), len(pref), content_ok))
    print('  nested order: ' + ' '.join(c['parse'] for c in pref[:18]) + (' ...' if len(pref) > 18 else ''))
    return content_ok


# ----------------------------------------------------------------- MW ----------
def read_all_records(path):
    recs = []
    with open(path, encoding='utf-8') as f:
        lines = [ln.rstrip('\r\n') for ln in f]
    i = 0
    while i < len(lines):
        if lines[i].startswith('<L>'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('<LEND>'):
                j += 1
            meta = lines[i]
            body = '\n'.join(lines[i:j+1])
            k1 = (re.search(r'<k1>([^<]*)', meta) or [None, ''])[1]
            verb = (re.search(r'<info verb="([^"]*)"', body) or [None, ''])[1]
            parse = (re.search(r'parse="([^"]*)"', body) or [None, ''])[1]
            recs.append({'k1': k1, 'verb': verb, 'parse': parse, 'lines': lines[i:j+1]})
            i = j + 1
        else:
            i += 1
    return recs


def glue_mw(path, root):
    recs = read_all_records(path)
    heads = [r for r in recs if r['k1'] == root and r['verb'] in ('genuineroot', 'root')]
    preverbs, skipped_cvi = [], 0
    for r in recs:
        if r['verb'] != 'pre' or not r['parse']:
            continue
        elems = r['parse'].split('+')
        if elems[-1] != root:
            continue
        if all(e in UPASARGAS for e in elems[:-1]) and elems[:-1]:
            preverbs.append(r)
        else:
            skipped_cvi += 1
    preverbs.sort(key=lambda r: parse_sort_key(r['parse']))
    out = ['<NESTED root="%s">' % root]
    for r in heads:
        out.extend(r['lines'])
    for r in preverbs:
        out.extend(r['lines'])
    out.append('</NESTED>')
    print('MW glue   root=%s : %d head + %d preverb records assembled (%d cvi/denominal forms excluded)'
          % (root, len(heads), len(preverbs), skipped_cvi))
    print('  nested order: ' + ' '.join(r['parse'] for r in preverbs[:18]) + (' ...' if len(preverbs) > 18 else ''))
    # write the assembled article for inspection
    fileout = 'glue_mw_%s.txt' % root
    with open(fileout, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('  wrote %d lines to %s' % (len(out), fileout))
    return len(preverbs) > 0


if __name__ == '__main__':
    mode = sys.argv[1]
    path = sys.argv[2]
    if mode == 'pwg':
        L = sys.argv[3]
        pv = '../../../PWG/verbs01/pwg_preverb1.txt'
        if '--preverb' in sys.argv:
            pv = sys.argv[sys.argv.index('--preverb') + 1]
        ok = glue_pwg(path, L, pv)
    elif mode == 'mw':
        ok = glue_mw(path, sys.argv[3])
    else:
        print('mode must be pwg or mw'); sys.exit(2)
    sys.exit(0 if ok else 1)
