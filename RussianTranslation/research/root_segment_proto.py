#-*- coding:utf-8 -*-
"""root_segment_proto.py — prototype PWG root-record text-slicer (the GAP).

Prior art note: the prefix INVENTORY + sandhi join + MW alignment + Paninian-order
parse are ALREADY computed by Jim Funderburk's PWG/verbs01/preverb1.py
(outputs pwg_preverb1.txt etc.). This prototype builds only the missing piece for the
SanskritLexicography SPLIT/NESTED translation pipeline: cutting the giant PWG <L> record
into translation-ready sub-cards at its <div n="p"> (prefixed-verb) and <div n="m">
(caus/desid/intens) boundaries, then gluing them back LOSSLESSLY.

Cue (confirmed in ROOT_ENTRY_ARCHITECTURE.md RESULTS):
  prefix sub-card  : line starts  <div n="p">    , upasarga in the first {#...#} (or 'Mit {#...#}')
  secondary conj   : line starts  <div n="m">    , label in <ab>Caus./Desid./Intens.</ab>
  everything before the first such boundary = the simple-verb head card (upasarga='').

Usage:
  python root_segment_proto.py ../../../csl-orig/v02/pwg/pwg.txt 55166 21814 72578
  (no L args -> runs the built-in self-test on bhu + both gam homonyms)
"""
from __future__ import print_function
import sys, re, codecs

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

UPA_RE = re.compile(r'^<div n="p">\s*—\s*(?:Mit\s*)?\{#([*]?[a-zA-Z]+)#\}')
SEC_RE = re.compile(r'^<div n="m">.*?<ab>(Caus\.|Desid\.|Intens\.)</ab>')


def read_record(path, L):
    """Return (metaline, datalines, lendline) for the <L>L... record, or None."""
    want = '<L>%s<' % L
    with codecs.open(path, encoding='utf-8') as f:
        lines = [ln.rstrip('\r\n') for ln in f]
    i = 0
    while i < len(lines):
        if lines[i].startswith(want):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('<LEND>'):
                j += 1
            return lines[i], lines[i+1:j], lines[j]
        i += 1
    return None


def segment(datalines):
    """Split datalines into sub-cards on <div n="p"> / <div n="m"> boundaries.
    Returns list of dicts: {kind, upasarga, label, lines:[...]}. Order preserved."""
    cards = []
    cur = {'kind': 'head', 'upasarga': '', 'label': '', 'lines': []}
    for ln in datalines:
        mu, ms = UPA_RE.match(ln), SEC_RE.match(ln)
        if mu:
            cards.append(cur)
            cur = {'kind': 'prefix', 'upasarga': mu.group(1), 'label': '', 'lines': [ln]}
        elif ms:
            cards.append(cur)
            cur = {'kind': 'secondary', 'upasarga': '', 'label': ms.group(1), 'lines': [ln]}
        else:
            cur['lines'].append(ln)
    cards.append(cur)
    return cards


def glue(cards):
    """Inverse of segment(): concatenate sub-card lines in stored order."""
    out = []
    for c in cards:
        out.extend(c['lines'])
    return out


def run(path, L):
    rec = read_record(path, L)
    if rec is None:
        print('  L=%s NOT FOUND' % L); return False
    meta, data, lend = rec
    k1 = re.search(r'<k1>([^<]*)', meta)
    k1 = k1.group(1) if k1 else '?'
    cards = segment(data)
    lossless = glue(cards) == data
    npfx = sum(1 for c in cards if c['kind'] == 'prefix')
    nsec = sum(1 for c in cards if c['kind'] == 'secondary')
    print('  L=%-7s k1=%-5s lines=%-4d sub-cards=%-3d (1 head + %d prefix + %d sec)  round-trip=%s'
          % (L, k1, len(data), len(cards), npfx, nsec, 'LOSSLESS' if lossless else '*** MISMATCH ***'))
    pf = [c['upasarga'] for c in cards if c['kind'] == 'prefix']
    if pf:
        print('     upasargas: ' + ' '.join(pf[:24]) + (' ...' if len(pf) > 24 else ''))
    return lossless


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '../../../csl-orig/v02/pwg/pwg.txt'
    Ls = sys.argv[2:] if len(sys.argv) > 2 else ['55166', '21814', '72578']
    print('PWG root-record segmenter prototype  (source: %s)' % path)
    ok = all([run(path, L) for L in Ls])
    print('ALL ROUND-TRIPS LOSSLESS' if ok else 'SOME ROUND-TRIPS FAILED')
    sys.exit(0 if ok else 1)
