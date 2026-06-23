#!/usr/bin/env python
"""enrich_renou_dcs.py — add DCS-attested Renou states to dictionary cards.

The <ls>-derived tag (annotate_renou.py) is authoritative but narrow: only what
the lexicographer chose to cite. This adds a second, provenance-tagged signal —
where the *headword lemma* is actually attested across the Digital Corpus of
Sanskrit (DCS) — from the index built by build_dcs_renou.py.

DCS attestation is per-LEMMA, so it cannot tell senses apart; it is merged at the
card/record level as `renou_dcs` and never overwrites the per-sense `<ls>` tag.
The reconciled view is `renou_enriched` (union of ls + dcs) with `renou_provenance`
naming, per state, which signal(s) support it ("ls", "dcs"):

  obj['renou_dcs']         states the lemma is attested in across DCS (I–V)
  obj['renou_dcs_oldest']  state of the earliest-dated DCS text for the lemma
  obj['renou_dcs_texts']   number of DCS texts the lemma occurs in
  obj['renou_enriched']    sorted union of ls-states and dcs-states
  obj['renou_provenance']  {state: ["ls","dcs"], …}

Idempotent, BOM-free, temp-swap. Join is on the headword: key1 (SLP1) → IAST lemma.

  python enrich_renou_dcs.py IN.jsonl [--out OUT] [--dict pwg|mw]
                             [--index dcs_lemma_renou.json] [--report]
"""
import json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou
import corpus_gate as cg   # _S2I + form_key for the SLP1→IAST headword join

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INDEX = os.path.join(HERE, 'dcs_lemma_renou.json')
STATES = renou.STATES
_ORDER = {s: i for i, s in enumerate(STATES)}


def to_iast(key1):
    return ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))


def card_of(obj):
    return obj.get('card', obj) if isinstance(obj, dict) else obj


def ls_states(obj):
    """Union of <ls>-derived states already on the line (flat 'renou', or every
    sense's 'renou' in the structured store)."""
    card = card_of(obj)
    if 'records' in card:
        s = set()
        for rec in card.get('records', []):
            for sense in rec.get('senses', []):
                s.update(sense.get('renou', []))
        return s
    return set(obj.get('renou', []))


def headword_key(obj):
    card = card_of(obj)
    return card.get('key1') or obj.get('key1')


def enrich(obj, index, stats):
    key1 = headword_key(obj)
    iast = to_iast(key1) if key1 else ''
    dcs = index.get(iast)
    dcs_states = dcs['renou'] if dcs else []
    ls = ls_states(obj)

    enriched = sorted(set(ls) | set(dcs_states), key=_ORDER.get)
    prov = {}
    for st in enriched:
        src = []
        if st in ls:
            src.append('ls')
        if st in dcs_states:
            src.append('dcs')
        prov[st] = src

    obj['renou_dcs'] = dcs_states
    obj['renou_dcs_oldest'] = dcs['renou_oldest'] if dcs else ''
    obj['renou_dcs_texts'] = dcs['n_texts'] if dcs else 0
    obj['renou_enriched'] = enriched
    obj['renou_provenance'] = prov

    stats['cards'] += 1
    if dcs:
        stats['dcs_hit'] += 1
    added = [st for st in dcs_states if st not in ls]
    if added:
        stats['cards_gained'] += 1
        for st in added:
            stats['added_by_state'][st] += 1
    for st in enriched:
        stats['enriched_by_state'][st] += 1


def run(path, out, index_path, report_only):
    index = json.load(open(index_path, encoding='utf-8'))
    stats = {'cards': 0, 'dcs_hit': 0, 'cards_gained': 0,
             'added_by_state': collections.Counter(),
             'enriched_by_state': collections.Counter()}
    tmp = (out + '.tmp') if not report_only else None
    sink = open(tmp, 'w', encoding='utf-8', newline='') if tmp else None
    try:
        with open(path, encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                enrich(obj, index, stats)
                if sink:
                    sink.write(json.dumps(obj, ensure_ascii=False) + '\n')
    finally:
        if sink:
            sink.close()
    if tmp:
        os.replace(tmp, out)
    report(stats, index_path, out if tmp else None)


def report(s, index_path, out):
    n = s['cards']
    print('index=%s  cards=%d' % (os.path.basename(index_path), n))
    print('  cards with a DCS lemma hit: %d (%.1f%%)'
          % (s['dcs_hit'], 100.0 * s['dcs_hit'] / n if n else 0))
    print('  cards that GAINED >=1 state from DCS (beyond <ls>): %d' % s['cards_gained'])
    print('  states added by DCS (not in <ls>):')
    for st in STATES:
        print('    %-3s %-15s %d' % (st, renou.RENOU_NAME[st], s['added_by_state'].get(st, 0)))
    print('  enriched coverage (ls ∪ dcs), cards carrying each state:')
    for st in STATES:
        print('    %-3s %-15s %d' % (st, renou.RENOU_NAME[st], s['enriched_by_state'].get(st, 0)))
    if out:
        print('→ %s' % out)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    path = args[0]
    out, index_path, report_only = None, DEFAULT_INDEX, False
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--index':
            index_path = args[i + 1]; i += 2
        elif a == '--dict':
            i += 2  # accepted for symmetry; join is dict-agnostic (key1→IAST)
        elif a == '--report':
            report_only = True; i += 1
        else:
            raise SystemExit('unknown option: %s' % a)
    if not report_only and out is None:
        out = path
    run(path, out, index_path, report_only)


if __name__ == '__main__':
    main()
