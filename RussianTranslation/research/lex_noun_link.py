#-*- coding:utf-8 -*-
"""lex_noun_link.py — lexicalised-noun -> root_key link table (PWG), the GAP piece.

verbs01 is verbs-only. The separate <k1>aDiBU / anuBUti / anuBUtiprakASa nominal
headwords are NOT linked there. This builds the non-destructive sidecar link table that
joins every PWG nominal to its verbal root, per the locked spec:

  root_key       = CHAIN: immediate base AND ultimate verbal root (anuBUtiprakASa ->
                   anuBUti -> anuBU -> BU)
  source         = the dict's OWN derivation field first, morphology only as fallback:
                     PWG '(von [N.] {#ROOT#} ... mit {#UPA#})'  -> prefix_root
                     PWG '(von {#X#})' / 's. u. {#X#}'           -> derived / xref
                     PWG '({#A + B#})'                           -> compound
                     PWG '(wie eben)'                            -> inherit previous
                     none stated -> strip-upasarga + root-set match (source=morph)
  scope          = full derivative family (prefix-nominals + suffix-derivs + compounds)
  output         = sidecar TSV; never edits csl-orig
  depth + is_leading_word_compound = so root_glue.py can CAP nesting (e.g. prefix-verb +
                   direct derivative only) while the table still records the full chain.

Usage:
  python lex_noun_link.py ../../../csl-orig/v02/pwg/pwg.txt \
         --roots ../../../PWG/verbs01/pwg_verb_filter_map.txt
"""
from __future__ import print_function
import sys, re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

UPASARGAS = ['saMpra', 'sam', 'pra', 'parA', 'apa', 'anu', 'ava', 'nis', 'nir', 'dus',
             'dur', 'vi', 'aDi', 'api', 'ati', 'su', 'ud', 'aBi', 'prati', 'pari', 'upa',
             'ni', 'A', 'antaH', 'Avis']   # longest-first within reason for stripping


def first_dataline(path):
    """Yield (L, k1, first non-meta line) for each record."""
    L = k1 = None
    waiting = False
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if line.startswith('<L>'):
                m = re.search(r'<L>(\S+?)<.*?<k1>([^<]*)', line)
                L, k1 = (m.group(1), m.group(2)) if m else (None, None)
                waiting = True
            elif waiting and line and not line.startswith('<LEND>'):
                yield L, k1, line
                waiting = False


def parse_derivation(line):
    """Return dict {type, base?, upa?, members?} from a PWG first-dataline, or None."""
    # strip the leading "{#headword#}¦"
    body = re.sub(r'^\{#[^#]*#\}¦', '', line).strip()
    # first top-level parenthetical
    mp = re.search(r'\(([^()]*)\)', body)
    paren = mp.group(1) if mp else ''
    # prefix_root: "von [N.] {#ROOT#} ... mit {#UPA#}"  (in paren OR after 's. u.')
    for scope in (paren, body):
        m = re.search(r'von\s+(?:\d+\.\s*)?\{#([^#]+)#\}.*?mit\s+\{#([^#]+)#\}', scope)
        if m:
            return {'type': 'prefix_root', 'base': m.group(1), 'upa': m.group(2)}
        m = re.search(r'\{#([^#]+)#\}\s*mit\s+\{#([^#]+)#\}', scope)   # 's. u. {#BU#} mit {#pra#}'
        if m:
            return {'type': 'prefix_root', 'base': m.group(1), 'upa': m.group(2)}
    # compound: "{#A + B#}" or "{#A#} + {#B#}"
    m = re.search(r'\{#\s*([^#+]+?)\s*\+\s*([^#]+?)\s*#\}', paren) or \
        re.search(r'\{#([^#]+)#\}\s*\+\s*\{#([^#]+)#\}', paren)
    if m:
        return {'type': 'compound', 'members': [m.group(1).strip(), m.group(2).strip()]}
    # wie eben / wie oben -> inherit previous
    if re.search(r'wie\s+(eben|oben)', paren):
        return {'type': 'inherit'}
    # derived: "(von {#X#})"  or  "s. u. {#X#}"
    m = re.search(r'von\s+(?:\d+\.\s*)?\{#([^#]+)#\}', paren)
    if m:
        return {'type': 'derived', 'base': m.group(1)}
    m = re.search(r's\.\s*u\.\s*\{#([^#]+)#\}', body)
    if m:
        return {'type': 'xref', 'base': m.group(1)}
    return None


def clean(s):
    """Keep only SLP1 letters (+ the * variant marker); kills stray ')' / digits / spaces
    that leak from imperfect derivation parentheses (the aDi)+BU mis-parse class)."""
    return re.sub(r'[^A-Za-z*]', '', s or '')


def strip_upasarga(k1, rootset):
    for u in UPASARGAS:
        if k1.startswith(u) and len(k1) > len(u):
            res = k1[len(u):]
            if res in rootset:
                return u, res
    return None, None


def main(path, rootspath):
    rootset = set()
    try:
        with open(rootspath, encoding='utf-8') as f:
            for line in f:
                m = re.search(r'k1=([^,]+),', line)
                if m:
                    rootset.add(m.group(1))
    except FileNotFoundError:
        print('warning: roots file not found:', rootspath)

    # pass 1: derivations, in file order (for 'inherit')
    deriv = {}          # k1 -> derivation dict (first occurrence wins)
    order = []          # (L, k1)
    prev = None
    for L, k1, line in first_dataline(path):
        if k1 is None:
            continue
        d = parse_derivation(line)
        if d and d['type'] == 'inherit':
            d = dict(prev) if prev else None
        if d:
            prev = d
        order.append((L, k1))
        if k1 not in deriv and d:
            deriv[k1] = d

    # pass 2: resolve chains (memoised, cycle-guarded)
    memo = {}

    def resolve(k1, seen):
        if k1 in memo:
            return memo[k1]
        if k1 in seen or len(seen) > 12:
            return None
        seen = seen | {k1}
        d = deriv.get(k1)
        res = None
        if d is None:
            u, r = strip_upasarga(k1, rootset)
            if r:
                res = {'root': r, 'base': '%s+%s' % (u, r), 'upa': u,
                       'dtype': 'prefix_root', 'src': 'morph', 'depth': 2,
                       'lwc': False, 'chain': [k1, '%s+%s' % (u, r), r]}
        elif d['type'] == 'prefix_root':
            r, u = clean(d['base']), clean(d['upa'])
            if not r or not u:
                memo[k1] = None
                return None
            res = {'root': r, 'base': '%s+%s' % (u, r), 'upa': u,
                   'dtype': 'prefix_root', 'src': 'pwg', 'depth': 2,
                   'lwc': False, 'chain': [k1, '%s+%s' % (u, r), r]}
        elif d['type'] in ('derived', 'xref'):
            X = clean(d['base'])
            sub = resolve(X, seen) if X else None
            if sub:
                res = {'root': sub['root'], 'base': X, 'upa': sub['upa'],
                       'dtype': d['type'], 'src': 'pwg', 'depth': sub['depth'] + 1,
                       'lwc': sub['lwc'], 'chain': [k1] + sub['chain']}
            elif X in rootset:
                res = {'root': X, 'base': X, 'upa': '', 'dtype': d['type'],
                       'src': 'pwg', 'depth': 1, 'lwc': False, 'chain': [k1, X]}
        elif d['type'] == 'compound':
            for mem in [clean(m) for m in d['members']]:
                sub = resolve(mem, seen) if mem else None
                if sub:
                    res = {'root': sub['root'], 'base': mem, 'upa': sub['upa'],
                           'dtype': 'compound', 'src': 'pwg', 'depth': sub['depth'] + 1,
                           'lwc': True, 'chain': [k1] + sub['chain']}
                    break
        memo[k1] = res
        return res

    rows = []
    for L, k1 in order:
        res = resolve(k1, set())
        if res:
            rows.append((k1, L, res['root'], res['base'], res['upa'], res['dtype'],
                         res['src'], res['depth'], res['lwc'], '>'.join(res['chain'])))

    fileout = 'lex_noun_link_pwg.tsv'
    with open(fileout, 'w', encoding='utf-8') as f:
        f.write('headword\tL\troot_key\timmediate_base\tupasarga\tderivation_type\t'
                'source\tdepth\tis_leading_word_compound\tchain\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')

    nrec = len(order)
    bysrc = {}
    for r in rows:
        bysrc[r[6]] = bysrc.get(r[6], 0) + 1
    print('%d records scanned; %d linked (%.1f%%) -> %s'
          % (nrec, len(rows), 100.0 * len(rows) / max(nrec, 1), fileout))
    print('  by source:', bysrc)
    print('  BU-family sample:')
    for r in rows:
        if r[2] == 'BU' and r[0] in ('aDiBU', 'aDiBUta', 'anuBU', 'anuBUti',
                                     'anuBUtiprakASa', 'praBAva', 'praBUta', 'saMBava'):
            print('   %-16s root=%-4s base=%-10s upa=%-5s %-11s %-5s depth=%d lwc=%s  %s'
                  % (r[0], r[2], r[3], r[4] or '-', r[5], r[6], r[7], r[8], r[9]))


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '../../../csl-orig/v02/pwg/pwg.txt'
    roots = '../../../PWG/verbs01/pwg_verb_filter_map.txt'
    if '--roots' in sys.argv:
        roots = sys.argv[sys.argv.index('--roots') + 1]
    main(path, roots)
