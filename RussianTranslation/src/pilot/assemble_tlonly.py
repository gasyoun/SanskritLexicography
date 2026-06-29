#!/usr/bin/env python
"""PROTOTYPE — weld the translation-only model output back into a full card.

The tlonly model returned ONLY Russian-per-sense (with {Tn} placeholder tokens
where it referenced masked spans). This restores the {Tn} tokens deterministically
(pwg_mask) and welds the german field back from the source, producing a card in
the production schema so it can be audited identically and compared to the echo run.

  python src/pilot/assemble_tlonly.py <tlonly_result.json> [--ref wf_output.json]

<tlonly_result.json> is the Workflow result object ({meta, results}) OR the raw
task-output wrapper ({result: {...}}). --ref is the production run that supplies
the per-sense german (default: wf_output.json).
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from window_common import OUT
import pwg_mask
import prompt_rule_audit as P


def load_result(path):
    d = json.load(open(path, encoding='utf-8'))
    if 'results' in d:
        return d
    r = d.get('result')
    if isinstance(r, str):
        r = json.loads(r)
    if isinstance(r, dict) and 'results' in r:
        return r
    sys.exit('no {results} found in %s' % path)


def german_index(ref_path):
    """(key, rec_idx, tag) -> source german, from the production run."""
    idx = {}
    if not os.path.exists(ref_path):
        return idx
    ref = json.load(open(ref_path, encoding='utf-8'))
    for r in ref.get('results', []):
        c = r.get('card') or {}
        for ri, rec in enumerate(c.get('records', [])):
            for s in rec.get('senses', []):
                idx[(r['key'], ri, s.get('tag'))] = s.get('german', '')
    return idx


def risk_ids(card_like):
    return [rk['id'] for rk in P.semantic_risks(card_like)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ref_path = 'wf_output.json'
    if '--ref' in sys.argv:
        ref_path = sys.argv[sys.argv.index('--ref') + 1]
    if not args:
        sys.exit('usage: assemble_tlonly.py <tlonly_result.json> [--ref wf_output.json]')
    data = load_result(args[0])
    phmaps = json.load(open(os.path.join(OUT, 'tlonly_phmaps.json'), encoding='utf-8'))
    gidx = german_index(ref_path)

    assembled = {'meta': data.get('meta', {}), 'results': []}
    unresolved_tokens = welded = missing_german = 0
    for r in data['results']:
        key = r['key']
        ph = phmaps.get(key, [])
        c = r.get('card') or {}
        out_records = []
        for ri, rec in enumerate(c.get('records', [])):
            senses = []
            for s in rec.get('senses', []):
                tag = s.get('tag')
                russian = pwg_mask.restore(s.get('russian', ''), ph)
                if '{T' in russian:
                    unresolved_tokens += 1
                german = gidx.get((key, ri, tag), '')
                if german:
                    welded += 1
                else:
                    missing_german += 1
                senses.append({
                    'tag': tag, 'german': german, 'russian': russian,
                    'equivalence_type': s.get('equivalence_type', ''),
                    'source_type': s.get('source_type', ''),
                    'stratum': s.get('stratum', ''),
                    'differentia': s.get('differentia', ''),
                })
            out_records.append({'h': rec.get('h', ''),
                                'grammar': rec.get('grammar', ''),
                                'senses': senses})
        assembled['results'].append({
            'key': key,
            'card': {'key1': c.get('key1', ''), 'iast': c.get('key1', ''),
                     'records': out_records, 'notes': ''},
            'judge': None, 'judge_sonnet': None, 'escalated': False})

    out_path = os.path.join(os.path.dirname(OUT), '..', '..', 'wf_output.tlonly_assembled.json')
    out_path = os.path.normpath(out_path)
    json.dump(assembled, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
    print('assembled %d cards -> %s' % (len(assembled['results']), out_path))
    print('senses welded with source german: %d | missing german: %d | unresolved {T tokens: %d'
          % (welded, missing_german, unresolved_tokens))

    # Quality comparison: semantic-risk counts, tlonly-assembled vs production ref.
    ref = json.load(open(ref_path, encoding='utf-8'))
    refmap = {r['key']: r for r in ref.get('results', [])}
    print('\n%-26s %10s %10s' % ('card', 'ref_risks', 'tlonly_risks'))
    tot_ref = tot_tl = 0
    for r in assembled['results']:
        tl = len(risk_ids(r))
        rf = len(risk_ids(refmap.get(r['key'], {}))) if r['key'] in refmap else -1
        tot_tl += tl
        tot_ref += max(0, rf)
        print('%-26s %10s %10d' % (r['key'], rf if rf >= 0 else 'n/a', tl))
    print('%-26s %10d %10d' % ('TOTAL', tot_ref, tot_tl))


if __name__ == '__main__':
    main()
