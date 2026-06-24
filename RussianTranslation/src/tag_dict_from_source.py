#!/usr/bin/env python
"""tag_dict_from_source.py — Renou I–V tags for any csl-orig dictionary, from source.

Generalises tag_mw_from_source.py to the LS-rich dictionaries. Per entry it derives
both layers — <ls> citations and DCS corpus attestation — keyed by key1 (joins to a
Russian translation later), and writes {code}_renou.jsonl.

Per-dictionary <ls> handling:
  pwg, pw, pwk, sch   Petersburg sigla        → renou.states_for_text(block,'pwg')
  mw                  MW inline sigla         → renou.states_for_text(block,'mw')
  ap, ap90, ben       Apte/Benfey inline      → renou_sigla (curated tables)
  bhs                 Buddhist Hybrid Skt     → renou_sigla default-V + meta blocklist

  python tag_dict_from_source.py CODE [--out PATH] [--index dcs_lemma_renou.json]
                                 [--report]
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou, renou_sigla
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
CSL = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02'))
DEFAULT_INDEX = os.path.join(HERE, 'dcs_lemma_renou.json')
STATES = renou.STATES
_ORDER = {s: i for i, s in enumerate(STATES)}

K1 = re.compile(r'<k1>(.*?)(?:<k2>|<e>|<h>|$)', re.S)
K2 = re.compile(r'<k2>(.*?)(?:<h>|<e>|$)', re.S)
PWG_STYLE = {'pwg', 'pw', 'pwk', 'pwkvn', 'sch'}
INLINE = {'ap', 'ap90', 'ben', 'bhs'}


def entries(data):
    """Yield each dictionary entry block. csl-orig delimits with <L>…<LEND>; some
    files omit <LEND>, so fall back to splitting on <L>."""
    blocks = re.findall(r'<L>(.*?)<LEND>', data, re.S)
    if blocks:
        return blocks
    parts = re.split(r'(?=<L>)', data)
    return [p for p in parts if p.startswith('<L>')]


def to_iast(key1):
    return ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))


def ls_states(code, block):
    """({states}, oldest_state) from the entry's <ls> citations, per dict style."""
    if code in PWG_STYLE:
        r = renou.states_for_text(block, 'pwg')
        return set(r['renou']), r['renou_oldest']
    if code == 'mw':
        r = renou.states_for_text(block, 'mw')
        return set(r['renou']), r['renou_oldest']
    states, oldest = renou_sigla.states_for_block(code, block)
    return states, (oldest[0] if oldest else '')


def merge(ls, dcs):
    enriched = sorted(set(ls) | set(dcs), key=_ORDER.get)
    prov = {}
    for st in enriched:
        src = (['ls'] if st in ls else []) + (['dcs'] if st in dcs else [])
        prov[st] = src
    return enriched, prov


def run(code, out, index_path, report_only, min_support=renou.DCS_MIN_SUPPORT):
    src = os.path.join(CSL, code, code + '.txt')
    if not os.path.exists(src):
        raise SystemExit('no source: %s' % src)
    if code not in PWG_STYLE and code not in INLINE and code != 'mw':
        raise SystemExit('unknown dict code: %s' % code)
    index = json.load(open(index_path, encoding='utf-8'))
    data = open(src, encoding='utf-8').read()
    st = {'entries': 0, 'ls_tagged': 0, 'dcs_hit': 0,
          'ls': collections.Counter(), 'dcs': collections.Counter(),
          'enr': collections.Counter()}
    tmp = (out + '.tmp') if not report_only else None
    sink = open(tmp, 'w', encoding='utf-8', newline='') if tmp else None
    try:
        for block in entries(data):
            k1m = K1.search(block)
            if not k1m:
                continue
            key1 = k1m.group(1).strip()
            ls, ls_oldest = ls_states(code, block)
            iast = to_iast(key1)
            dcs = index.get(iast)
            # apply the DCS over-tag min-support policy (drops thin low-confidence
            # states — homograph/date-fallback noise; see renou.filter_dcs_states)
            dcs_states = renou.filter_dcs_states(dcs, min_support) if dcs else []
            enriched, prov = merge(ls, dcs_states)

            st['entries'] += 1
            if ls:
                st['ls_tagged'] += 1
                for s in ls:
                    st['ls'][s] += 1
            if dcs:
                st['dcs_hit'] += 1
                for s in dcs_states:
                    st['dcs'][s] += 1
            for s in enriched:
                st['enr'][s] += 1

            if sink:
                k2m = K2.search(block)
                rec = {'key1': key1, 'key2': k2m.group(1).strip() if k2m else key1,
                       'iast': iast,
                       'renou_ls': sorted(ls, key=_ORDER.get), 'renou_ls_oldest': ls_oldest,
                       'renou_dcs': dcs_states,
                       'renou_dcs_oldest': dcs['renou_oldest'] if dcs else '',
                       'renou_enriched': enriched, 'renou_provenance': prov}
                sink.write(json.dumps(rec, ensure_ascii=False) + '\n')
    finally:
        if sink:
            sink.close()
    if tmp:
        os.replace(tmp, out)
    report(code, st, out if tmp else None)


def report(code, s, out):
    n = s['entries']
    print('%-5s entries: %d' % (code, n))
    print('  <ls>-tagged: %d (%.1f%%) · DCS-hit: %d (%.1f%%)'
          % (s['ls_tagged'], 100.0 * s['ls_tagged'] / n if n else 0,
             s['dcs_hit'], 100.0 * s['dcs_hit'] / n if n else 0))
    for label, key in (('<ls>', 'ls'), ('DCS', 'dcs'), ('enriched', 'enr')):
        row = ' · '.join('%s %d' % (st, s[key].get(st, 0)) for st in STATES)
        print('  %-9s %s' % (label, row))
    if out:
        print('  → %s' % os.path.basename(out))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    code = args[0]
    out = os.path.join(HERE, code + '_renou.jsonl')
    index_path = DEFAULT_INDEX
    report_only = False
    min_support = renou.DCS_MIN_SUPPORT
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--index':
            index_path = args[i + 1]; i += 2
        elif a == '--report':
            report_only = True; i += 1
        elif a == '--dcs-min-support':
            min_support = int(args[i + 1]); i += 2
        else:
            raise SystemExit('unknown option: %s' % a)
    run(code, out, index_path, report_only, min_support)


if __name__ == '__main__':
    main()
