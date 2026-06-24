#!/usr/bin/env python
"""renou_pipeline.py — one canonical Renou index per dictionary, all four signals.

Chains the per-signal steps into a single reproducible artifact, keyed by key1:

  <ls> citation + DCS corpus   (tag_dict_from_source)
    -> + BHS register V transfer (enrich_renou_bhs)
    -> + wisdomlib tradition     (enrich_renou_wisdomlib, if word_traditions.jsonl given)
  = {code}.renou.jsonl  with renou_enriched + renou_provenance
    (provenance sources: "ls", "dcs", "bhs", "wl")

Prereqs built once: ls_source_map{,_mw}.json (build_ls_map*.py) and the DCS index
dcs_lemma_renou.json (build_dcs_renou.py). bhs_renou.jsonl (the BHS-vocab source for
the transfer) is built automatically if missing.

  python renou_pipeline.py mw [--wl word_traditions.jsonl]
  python renou_pipeline.py --all [--wl ...]
"""
import json, os, sys, tempfile, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import tag_dict_from_source as tag
import enrich_renou_bhs as bhs
import enrich_renou_wisdomlib as wl
import renou

HERE = os.path.dirname(os.path.abspath(__file__))
DCS = os.path.join(HERE, 'dcs_lemma_renou.json')
BHS_SRC = os.path.join(HERE, 'bhs_renou.jsonl')
DICTS = ['pwg', 'mw', 'pw', 'ap', 'ap90', 'ben', 'sch', 'bhs']


def ensure_bhs():
    if not os.path.exists(BHS_SRC):
        print('building bhs_renou.jsonl (BHS vocab source) …', file=sys.stderr)
        tag.run('bhs', BHS_SRC, DCS, False)


def build(code, wl_path):
    if not os.path.exists(DCS):
        raise SystemExit('missing %s — run build_dcs_renou.py first' % os.path.basename(DCS))
    ensure_bhs()
    final = os.path.join(HERE, code + '.renou.jsonl')
    with tempfile.TemporaryDirectory() as td:
        t1 = os.path.join(td, 't1.jsonl')
        t2 = os.path.join(td, 't2.jsonl')
        tag.run(code, t1, DCS, False)                 # <ls> + DCS
        if code == 'bhs':
            t2 = t1                                    # BHS is the transfer source — skip self-transfer
        else:
            bhs.run(t1, t2, BHS_SRC, False)            # + BHS V
        if wl_path and os.path.exists(wl_path):
            wl.run(t2, wl_path, final, False)          # + wisdomlib
        else:
            os.replace(t2, final) if t2 != t1 else _copy(t2, final)
    return final


def _copy(src, dst):
    with open(src, encoding='utf-8') as i, open(dst, 'w', encoding='utf-8', newline='') as o:
        o.write(i.read())


def report(code, path):
    st = collections.Counter()
    prov = collections.Counter()
    n = 0
    for line in open(path, encoding='utf-8'):
        o = json.loads(line)
        n += 1
        for s in (o.get('renou_enriched') or []):
            st[s] += 1
        for s, srcs in (o.get('renou_provenance') or {}).items():
            for src in srcs:
                prov[(s, src)] += 1
    print('== %-5s %7d entries  →  %s' % (code, n, os.path.basename(path)))
    print('   states   ' + ' · '.join('%s %d' % (s, st.get(s, 0)) for s in renou.STATES))
    print('   V by src ' + ' · '.join('%s %d' % (src, prov.get(('V', src), 0))
                                       for src in ('ls', 'dcs', 'bhs', 'wl')))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    wl_path = None
    codes = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--all':
            codes = list(DICTS); i += 1
        elif a == '--wl':
            wl_path = args[i + 1]; i += 2
        else:
            codes.append(a); i += 1
    for code in codes:
        final = build(code, wl_path)
        report(code, final)


if __name__ == '__main__':
    main()
