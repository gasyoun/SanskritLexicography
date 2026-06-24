#-*- coding:utf-8 -*-
"""root_merge.py — build B: PWG <-> MW merged comparative nested article.

Aligns the PWG root sub-cards (NESTED in one record) with the MW prefixed-verb records
(SPLIT across the file) on the canonical PARSE key (anu+BU, prati+anu+BU, ...), and emits
one comparative article: per prefix, the PWG German gloss beside the MW English gloss,
plus presence flags. This is the cross-dict view the translation correctness gate wants.

Reuses (no reinvention):
  root_segment_proto  -> PWG record slicer
  root_glue           -> load_preverb_parses (PWG surface->parse), collect_mw_preverbs,
                         parse_sort_key (canonical ordering)

  python root_merge.py BU [pwg.txt] [mw.txt]
"""
from __future__ import print_function
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import root_segment_proto as RS                              # noqa: E402
import root_glue as G                                        # noqa: E402

PWG = os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt')
MW = os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'mw', 'mw.txt')
PREVERB = os.path.join(HERE, '..', '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt')
PCT = re.compile(r'\{%(.*?)%\}', re.S)


def pwg_by_parse(pwg, L):
    """parse-key -> (upasarga, German gloss snippet) for each PWG prefix sub-card."""
    rec = RS.read_record(pwg, L)
    if not rec:
        return '?', {}
    meta, data, lend = rec
    k1 = (re.search(r'<k1>([^<]*)', meta) or [None, '?'])[1]
    pmap = G.load_preverb_parses(PREVERB, L)
    out = {}
    for c in RS.segment(data):
        if c['kind'] != 'prefix':
            continue
        parse = pmap.get((L, c['upasarga']), '%s+%s' % (c['upasarga'], k1))
        m = PCT.search('\n'.join(c['lines']))
        out[parse] = (c['upasarga'], (m.group(1).strip()[:46] if m else ''))
    return k1, out


def mw_by_parse(mw, root):
    """parse-key -> English gloss snippet for each MW preverb record."""
    _, preverbs, _ = G.collect_mw_preverbs(mw, root)
    out = {}
    for r in preverbs:
        body = '\n'.join(r['lines'][1:])               # skip the <L> meta line
        txt = re.sub(r'<[^>]+>', ' ', body)            # drop tags (incl <s>Sanskrit</s>)
        txt = re.sub(r'\{[#%@][^}]*\}', ' ', txt)
        txt = re.sub(r'\s+', ' ', txt).strip(' .,;')
        out[r['parse']] = txt[:46]
    return out


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'BU'
    pwg = sys.argv[2] if len(sys.argv) > 2 else PWG
    mw = sys.argv[3] if len(sys.argv) > 3 else MW
    # PWG root record L: find by scanning for the verb root headword
    L = None
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            if line.startswith('<L>') and ('<k1>%s<' % root) in line:
                m = re.search(r'<L>(\S+?)<', line)
                L = m.group(1)
                break
    if L is None:
        print('PWG root %s not found' % root); return
    k1, pwg_map = pwg_by_parse(pwg, L)
    mw_map = mw_by_parse(mw, root)
    keys = sorted(set(pwg_map) | set(mw_map), key=G.parse_sort_key)
    both = [k for k in keys if k in pwg_map and k in mw_map]
    pwg_only = [k for k in keys if k in pwg_map and k not in mw_map]
    mw_only = [k for k in keys if k in mw_map and k not in pwg_map]
    out = ['# %s — PWG <-> MW merged root article (L=%s)' % (root, L), '',
           '%d prefixes total: **%d in both**, %d PWG-only, %d MW-only.'
           % (len(keys), len(both), len(pwg_only), len(mw_only)), '',
           '| parse | PWG (de) | MW (en) |', '|---|---|---|']
    for k in keys:
        pg = pwg_map.get(k, ('', ''))[1]
        mg = mw_map.get(k, '')
        flag = '' if k in both else (' ⟂PWG' if k in pwg_only else ' ⟂MW')
        out.append('| `%s`%s | %s | %s |' % (k, flag, pg.replace('|', '/'), mg.replace('|', '/')))
    fileout = os.path.join(HERE, 'merge_%s.md' % root)
    open(fileout, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('PWG<->MW merge  %s (L=%s): %d prefixes  both=%d  PWG-only=%d  MW-only=%d -> %s'
          % (root, L, len(keys), len(both), len(pwg_only), len(mw_only),
             os.path.basename(fileout)))
    print('  both (first 12):', ' '.join(both[:12]))
    if pwg_only:
        print('  PWG-only (first 10):', ' '.join(pwg_only[:10]))
    if mw_only:
        print('  MW-only (first 10):', ' '.join(mw_only[:10]))


if __name__ == '__main__':
    main()
