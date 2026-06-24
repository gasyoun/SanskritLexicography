#-*- coding:utf-8 -*-
"""affix_pedagogy.py — build the teaching dataset for Sanskrit affixation from affix_map.tsv.

One enriched JSON feeds every teaching artifact (explorer / charts / poster / quiz):
each affix gets its function GROUP, kṛt/taddhita/strī kind, surface + Pāṇinian forms,
anubandha-stripping steps (why घञ् → -a), Apte productivity (# distinct roots), the MW
surface-suffix count, and a few REAL example derivatives mined from Apte S–H.

  python affix_pedagogy.py            # -> affix_pedagogy.json (+ console summary)
"""
from __future__ import print_function
import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apte_parse as AP                     # records(), etym_chain(), slp1(), deva_to_iast

MAP = os.path.join(HERE, 'affix_map.tsv')

# function text -> teaching group (what the affix MAKES)
def group_of(fn, kind):
    f = fn.lower()
    if 'agent' in f:            return 'Agent — the doer'
    if 'participle' in f:       return 'Participle'
    if 'gerundive' in f:        return 'Gerundive — “to-be-Xed”'
    if 'action' in f or 'result' in f: return 'Action / result noun'
    if 'abstract' in f:         return 'Abstract quality — “-ness”'
    if kind == 'strī':          return 'Feminine stem'
    if 'possessive' in f:       return 'Possessive — “having X”'
    if 'comparative' in f or 'superlative' in f: return 'Comparison'
    if 'adverb' in f:           return 'Adverb'
    if 'temporal' in f:         return 'Temporal'
    if 'relational' in f or 'patronymic' in f: return 'Relational / patronymic'
    if 'diminutive' in f:       return 'Diminutive / self-sense'
    return 'Other'

# anubandha-stripping steps: pratyaya_iast -> [steps] (it-markers P.1.3.2-1.3.9 + substitutions)
ANUBANDHA = {
    'kta':   ['k = it (P.1.3.8)', '→ surface -ta'],
    'lyuṭ':  ['l = it', 'ṭ = it', 'yu → ana (P.7.1.1)', '→ -ana'],
    'ṇvul':  ['ṇ = it (→ vṛddhi)', 'l = it', 'vu → aka (P.7.1.1)', '→ -aka'],
    'tṛc':   ['c = it (P.1.3.3)', '→ -tṛ'],
    'ghañ':  ['gh = it (initial)', 'ñ = it (→ vṛddhi)', '→ -a'],
    'ac':    ['c = it', '→ -a'],
    'ktin':  ['k = it', 'n = it', '→ -ti'],
    'yat':   ['t = it', '→ -ya'],
    'aṇ':    ['ṇ = it (→ vṛddhi)', '→ -a'],
    'ṭhak':  ['ṭha → ika (P.7.3.50)', 'k = it (→ vṛddhi)', '→ -ika'],
    'ṣyañ':  ['ṣ = it (initial)', 'ñ = it (→ vṛddhi)', '→ -ya'],
    'ini':   ['final i = it', '→ -in'],
    'tva':   ['(no it-marker)', '→ -tva'],
    'tal':   ['l = it', '→ -tā (fem.)'],
    'matup': ['u, p = it', 'm → v after a/ā (P.8.2.9)', '→ -mat / -vat'],
    'tarap': ['p = it', '→ -tara'],
    'tamap': ['p = it', '→ -tama'],
    'tasil': ['l = it', '→ -tas'],
    'śas':   ['(adverbial)', '→ -śas'],
    'vini':  ['final i = it', '→ -vin'],
    'valac': ['c = it', '→ -vala'],
    'ṭyu':   ['ṭ = it', 'yu → ana → -tana', '→ -tana'],
    'kan':   ['k = it', 'n = it', '→ -ka'],
    'ka':    ['→ -ka'],
    'ṭāp':   ['ṭ = it', 'p = it', '→ -ā (fem.)'],
    'ṅīp':   ['ṅ = it', 'p = it', '→ -ī (fem.)'],
    'ṅīṣ':   ['ṅ = it', 'ṣ = it (→ vṛddhi)', '→ -ī (fem.)'],
}


def load_map():
    rows = []
    with open(MAP, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            c = line.rstrip('\n').split('\t')
            if len(c) >= 7:
                rows.append(dict(surface=c[0], surface_deva=c[1], pratyaya=c[2],
                                 pratyaya_deva=c[3], mw_wsfx=c[4], kind=c[5], function=c[6]))
    return rows


def mine(rows):
    """Apte productivity counts + example derivatives per pratyaya_deva."""
    wanted = set()
    for r in rows:
        wanted.update(r['pratyaya_deva'].split('|'))
    roots = {p: set() for p in wanted}
    examples = {p: [] for p in wanted}
    for rec in AP.records(AP.BABYLON):
        parts = AP.etym_chain(rec['etym'])
        if not parts or len(parts) < 2:
            continue
        aff = parts[-1]
        if aff not in wanted:
            continue
        root_slp = AP.slp1(parts[0])
        roots[aff].add(root_slp)
        if len(examples[aff]) < 3000 and 1 <= len(rec['hw_dev']) <= 14:
            try:
                examples[aff].append({'root': AP.deva_to_iast(parts[0]),
                                      'word': rec['hw_dev'], 'word_iast': AP.deva_to_iast(rec['hw_dev'])})
            except Exception:
                pass
    return roots, examples


def pick_examples(cands):
    """Prefer short, root-diverse, non-negated (skip leading a-/an-) example derivatives."""
    cands = sorted(cands, key=lambda e: (e['word_iast'].startswith(('a', 'an')), len(e['word_iast'])))
    out, seen_root = [], set()
    for e in cands:
        if e['root'] in seen_root:
            continue
        seen_root.add(e['root']); out.append(e)
        if len(out) >= 6:
            break
    return out or cands[:6]


def mw_counts():
    d = {}
    try:
        import mw_deriv
        for recs in mw_deriv.load().values():
            b = mw_deriv.best(recs)
            if b and b['method'].startswith('wsfx'):
                s = b['method'].split(':')[1] if ':' in b['method'] else b['method']
                d[s] = d.get(s, 0) + 1
    except Exception as e:
        print('  (MW counts unavailable: %s)' % e)
    return d


def main():
    if not os.path.exists(AP.BABYLON):
        print('missing %s' % AP.BABYLON); return
    rows = load_map()
    roots, examples = mine(rows)
    mw = mw_counts()
    affixes = []
    for r in rows:
        ps = r['pratyaya_deva'].split('|')
        apte = len(set().union(*[roots.get(p, set()) for p in ps])) if ps else 0
        ex = []
        for p in ps:
            ex += examples.get(p, [])
        seen, exu = set(), []
        for e in ex:
            if e['word'] not in seen:
                seen.add(e['word']); exu.append(e)
        exu = pick_examples(exu)
        mwc = sum(mw.get(k, 0) for k in r['mw_wsfx'].split('|') if k != '-')
        affixes.append({
            'surface': r['surface'], 'surface_deva': r['surface_deva'],
            'pratyaya': r['pratyaya'], 'pratyaya_deva': ps[0],
            'kind': r['kind'], 'function': r['function'],
            'group': group_of(r['function'], r['kind']),
            'anubandha': ANUBANDHA.get(r['pratyaya'], ['→ -' + r['surface']]),
            'apte_roots': apte, 'mw_count': mwc,
            'examples': exu[:6],
        })
    affixes.sort(key=lambda a: -a['apte_roots'])
    groups = {}
    for a in affixes:
        groups.setdefault(a['group'], []).append(a['pratyaya'])
    out = {'affixes': affixes, 'groups': groups,
           'note': 'Apte S–H affix productivity (apte_roots = # distinct roots) + MW wsfx '
                   'surface-suffix counts (mw_count = # headwords). Built by affix_pedagogy.py.'}
    json.dump(out, open(os.path.join(HERE, 'affix_pedagogy.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('affix_pedagogy.json: %d affixes in %d function groups' % (len(affixes), len(groups)))
    for g, aff in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print('  %-26s %s' % (g, ', '.join(aff)))
    print('  example (top affix):', affixes[0]['pratyaya'], '→',
          [e['word_iast'] for e in affixes[0]['examples'][:4]])


if __name__ == '__main__':
    main()
