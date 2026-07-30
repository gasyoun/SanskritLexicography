#!/usr/bin/env python
"""Authoritative PWG <ls> source resolver — from PWG's own bibliography.

PWG ships its Verzeichniss der Abkürzungen as csl-pywork .../pwgauth/pwgbib.txt
(~2.7k entries: <HI code="…" iast="…">CODE = full expansion). This resolves EVERY
<ls> abbreviation to its canonical expansion — replacing the hand-curated 45-source
ls_source_map for the *understanding* layer (the stratum/corpus linkage stays in
ls_source_map for the harvestable subset).

  python pwg_sources.py lookup <abbrev>     resolve one abbreviation
  python pwg_sources.py coverage [topN]      <ls> coverage of pwg.txt vs the bib
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root, require_sibling  # noqa: E402
GH = sibling_root(HERE)
BIB = os.path.join(GH, 'csl-pywork', 'v02', 'distinctfiles', 'pwg', 'pywork', 'pwgauth', 'pwgbib.txt')
PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
HI = re.compile(r'<HI code="([^"]*)" iast="([^"]*)">(.*)')
LS = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)


def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip()).rstrip('. ').strip()


_BIB = None
def bib():
    """The PWG bibliography, or an EMPTY map when the sibling repo is not checked out.

    `BIB` lives in `csl-pywork`, a SIBLING repo that is optional: CI checks out only this
    one, and so does a fresh clone. This used to raise FileNotFoundError, which turned an
    absent *enrichment* source into a hard failure of the promotion path itself --
    `promote_final_cards.rows_for` -> `extract_citation_edges` -> here. Citation edges are
    additive metadata; a missing bibliography must degrade to "no expansions resolved",
    never to "the store cannot be written". Cached either way, so the miss costs one stat.
    `require_sibling` upgrades this back to a raise when CSL_SIBLING_ROOT is explicitly
    set (H1902) — the operator is then asserting the siblings exist.
    """
    global _BIB
    if _BIB is None:
        _BIB = {}
        if not require_sibling(BIB, 'pwg_sources bibliography'):
            return _BIB
        handle = open(BIB, encoding='utf-8')
        for line in handle:
            h = HI.search(line)
            if not h:
                continue
            code, iast, rest = h.group(1), h.group(2), h.group(3)
            rest = re.sub(r'<lb[^>]*>', ' ', rest)
            rest = re.sub(r'\{#.*?#\}', '', rest)
            rest = re.sub(r'<[^>]+>', '', rest)
            rest = re.sub(r'\s+', ' ', rest).strip()
            exp = rest.split(' = ', 1)[1].strip() if ' = ' in rest else rest
            for k in (norm(iast), norm(code)):
                if k and k not in _BIB:
                    _BIB[k] = exp
    return _BIB


def source_key(inner):
    out = []
    for t in re.sub(r'<[^>]+>', '', inner).strip().split():
        if any(c.isdigit() for c in t):
            break
        out.append(t)
        if len(out) >= 4:
            break
    return re.sub(r'\s+', ' ', ' '.join(out)).strip().rstrip('.').strip()


def resolve(token):
    b = bib()
    k = norm(token)
    if k in b:
        return b[k]
    # try progressively shorter prefixes for multi-part abbreviations
    parts = k.split()
    for i in range(len(parts) - 1, 0, -1):
        kk = norm(' '.join(parts[:i]))
        if kk in b:
            return b[kk]
    return None


def cmd_lookup(args):
    print(resolve(args[0]) or '(not in pwgbib)')


def cmd_coverage(args):
    topn = int(args[0]) if args else 30
    freq = collections.Counter()
    data = open(PWG, encoding='utf-8').read()
    for m in LS.finditer(data):
        k = source_key(m.group(1))
        if k:
            freq[k] += 1
    total = sum(freq.values())
    b = bib()
    resolved_keys = sum(1 for k in freq if resolve(k))
    resolved_cit = sum(c for k, c in freq.items() if resolve(k))
    print('pwgbib entries: %d' % len(b))
    print('PWG <ls>: %d citations, %d distinct source keys' % (total, len(freq)))
    print('RESOLVED by pwgbib: %d/%d distinct keys (%.1f%%), %d/%d citations (%.1f%%)'
          % (resolved_keys, len(freq), 100.0 * resolved_keys / len(freq),
             resolved_cit, total, 100.0 * resolved_cit / total))
    unres = [(k, c) for k, c in freq.most_common() if not resolve(k)]
    print('top UNRESOLVED keys (likely mis-parsed multi-part refs or rare/Cologne-added):')
    for k, c in unres[:topn]:
        print('  %-22s %6d' % (k, c))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'lookup': cmd_lookup, 'coverage': cmd_coverage}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
