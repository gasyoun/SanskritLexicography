#!/usr/bin/env python
"""tag_mw_from_source.py — Renou I–V tags for Monier-Williams, from the source.

The MW *Russian* cards live in a separate working repo, but the Renou tag is
language-independent: it comes from the Sanskrit headword and its <ls> citations,
both present in the MW source csl-orig/v02/mw/mw.txt. This emits a per-entry,
key1-keyed Renou index that attaches to the Russian cards later (join on key1).

Per entry it writes both layers:
  renou_ls            <ls>-derived states (via ls_source_map_mw.json), multi-label
  renou_ls_oldest     state of the entry's earliest dated citation
  renou_dcs           DCS corpus attestation states for the headword lemma
  renou_dcs_oldest    earliest DCS attestation state
  renou_enriched      union(ls, dcs), ordered I→V
  renou_provenance    {state: ["ls","dcs"], …}

  python tag_mw_from_source.py [--out mw_renou.jsonl] [--index dcs_lemma_renou.json]
                               [--report]
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
MW = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'mw', 'mw.txt'))
DEFAULT_INDEX = os.path.join(HERE, 'dcs_lemma_renou.json')
OUT = os.path.join(HERE, 'mw_renou.jsonl')
STATES = renou.STATES
_ORDER = {s: i for i, s in enumerate(STATES)}

ENTRY = re.compile(r'<L>(.*?)<LEND>', re.S)
K1 = re.compile(r'<k1>(.*?)<k2>', re.S)
K2 = re.compile(r'<k2>(.*?)(?:<h>|<e>|$)', re.S)
HOM = re.compile(r'<h>(\d+)')


def to_iast(key1):
    return ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))


def merge(ls_states, dcs_states):
    enriched = sorted(set(ls_states) | set(dcs_states), key=_ORDER.get)
    prov = {}
    for st in enriched:
        src = []
        if st in ls_states:
            src.append('ls')
        if st in dcs_states:
            src.append('dcs')
        prov[st] = src
    return enriched, prov


def run(out, index_path, report_only):
    index = json.load(open(index_path, encoding='utf-8'))
    data = open(MW, encoding='utf-8').read()
    stats = {'entries': 0, 'ls_tagged': 0, 'dcs_hit': 0,
             'ls_state': collections.Counter(), 'dcs_state': collections.Counter(),
             'enr_state': collections.Counter()}
    tmp = (out + '.tmp') if not report_only else None
    sink = open(tmp, 'w', encoding='utf-8', newline='') if tmp else None
    try:
        for m in ENTRY.finditer(data):
            block = m.group(1)
            k1m = K1.search(block)
            if not k1m:
                continue
            key1 = k1m.group(1).strip()
            k2m = K2.search(block)
            homm = HOM.search(block)

            ls = renou.states_for_text(block, 'mw')
            iast = to_iast(key1)
            dcs = index.get(iast)
            dcs_states = renou.filter_dcs_states(dcs) if dcs else []
            enriched, prov = merge(ls['renou'], dcs_states)
            registers = renou.filter_dcs_registers(dcs) if dcs else []
            reg_prov = {r: ['dcs'] for r in registers}

            stats['entries'] += 1
            if ls['renou']:
                stats['ls_tagged'] += 1
                for s in ls['renou']:
                    stats['ls_state'][s] += 1
            if dcs:
                stats['dcs_hit'] += 1
                for s in dcs_states:
                    stats['dcs_state'][s] += 1
            for s in enriched:
                stats['enr_state'][s] += 1

            if sink:
                rec = {'key1': key1, 'key2': k2m.group(1).strip() if k2m else key1,
                       'iast': iast, 'hom': homm.group(1) if homm else None,
                       'renou_ls': ls['renou'], 'renou_ls_oldest': ls['renou_oldest'],
                       'renou_dcs': dcs_states,
                       'renou_dcs_oldest': renou.dcs_oldest(dcs, dcs_states),
                       'renou_enriched': enriched, 'renou_provenance': prov,
                       'renou_register': registers, 'renou_register_provenance': reg_prov}
                sink.write(json.dumps(rec, ensure_ascii=False) + '\n')
    finally:
        if sink:
            sink.close()
    if tmp:
        os.replace(tmp, out)
    report(stats, out if tmp else None)


def report(s, out):
    n = s['entries']
    print('MW entries: %d' % n)
    print('  <ls>-tagged: %d (%.1f%%) · DCS-hit: %d (%.1f%%)'
          % (s['ls_tagged'], 100.0 * s['ls_tagged'] / n if n else 0,
             s['dcs_hit'], 100.0 * s['dcs_hit'] / n if n else 0))
    for label, key in (('<ls> citations', 'ls_state'), ('DCS attestation', 'dcs_state'),
                       ('enriched (ls ∪ dcs)', 'enr_state')):
        print('  %s — entries carrying each state:' % label)
        for st in STATES:
            print('    %-3s %-15s %d' % (st, renou.RENOU_NAME[st], s[key].get(st, 0)))
    if out:
        print('→ %s' % out)


def main():
    args = sys.argv[1:]
    out, index_path, report_only = OUT, DEFAULT_INDEX, False
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--index':
            index_path = args[i + 1]; i += 2
        elif a == '--report':
            report_only = True; i += 1
        else:
            raise SystemExit('unknown option: %s' % a)
    run(out, index_path, report_only)


if __name__ == '__main__':
    main()
