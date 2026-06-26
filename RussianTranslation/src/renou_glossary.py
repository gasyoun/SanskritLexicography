#!/usr/bin/env python
"""renou_glossary.py — extract a register (or state) glossary from the Renou tags.

Realises the register-axis use cases (RENOU.md §Use cases): filter the canonical
`{code}.renou.jsonl` by register / state / provenance and emit a deduplicated headword
glossary — e.g. the épigraphique inscriptional vocabulary, a bhāṣya commentary glossary,
a kāvya poetic lexicon. Headwords are aggregated by IAST across dictionaries and senses;
each row records the states it spans, which dictionaries attest it, and the register's
provenance (ls = lexicographer cited it, dcs = corpus attestation).

  python renou_glossary.py REGISTER [--state S] [--exclude-state S,S] [--prov ls|dcs]
        [--dicts pwg,mw,…] [--min-dicts N] [--format md|tsv] [--out FILE] [--title "…"]

`--state S` keeps only words also attested in state S; `--exclude-state S,S` drops
words attested in any listed state — together they carve cross-axis slices, e.g.
`kavya --exclude-state I` = poetic words with no Vedic attestation ("born in kāvya"),
or `I --state-only --exclude-state II,III,IV,V` = words attested *only* in Vedic.

REGISTER is a renou_register code (renou_register.REGISTERS) — or pass --state-only to
glossary a *state* (I–V) instead. Examples:
  python renou_glossary.py epig  --format md  --out ../glossaries/epigraphic_vocabulary.md
  python renou_glossary.py bhasya --format tsv --out ../glossaries/bhasya_glossary.tsv
"""
import json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou
import renou_register

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = ('pwg', 'mw', 'pw', 'ap', 'ap90', 'ben', 'sch', 'bhs')
_SORD = {s: i for i, s in enumerate(renou.STATES)}


def collect(code_filter, dicts, state_filter, prov_filter, state_only, exclude_states):
    """iast -> {dicts:set, states:set, prov:set, key2:str, n:int}."""
    agg = {}
    exclude_states = set(exclude_states or ())
    for code in dicts:
        path = os.path.join(HERE, code + '.renou.jsonl')
        if not os.path.exists(path):
            continue
        for line in open(path, encoding='utf-8'):
            e = json.loads(line)
            states = e.get('renou_enriched') or []
            if state_only:
                if code_filter not in states:
                    continue
                srcs = (e.get('renou_provenance') or {}).get(code_filter, [])
            else:
                if code_filter not in (e.get('renou_register') or []):
                    continue
                srcs = (e.get('renou_register_provenance') or {}).get(code_filter, [])
            if state_filter and state_filter not in states:
                continue
            if exclude_states and exclude_states & set(states):
                continue  # drop entries attested in any excluded state
            if prov_filter and prov_filter not in srcs:
                continue
            ia = e.get('iast') or ''
            a = agg.get(ia)
            if a is None:
                a = agg[ia] = {'dicts': set(), 'states': set(), 'prov': set(),
                               'key2': e.get('key2') or ia, 'n': 0}
            a['dicts'].add(code.upper())
            a['states'].update(e.get('renou_enriched') or [])
            a['prov'].update(srcs)
            a['n'] += 1
    return agg


def render(agg, reg, title, fmt, min_dicts, meta):
    rows = sorted((ia for ia, a in agg.items() if len(a['dicts']) >= min_dicts),
                  key=lambda s: s.lower())
    states_of = lambda a: '·'.join(sorted(a['states'], key=_SORD.get))
    prov_of = lambda a: '+'.join(sorted(a['prov']))
    if fmt == 'tsv':
        L = ['# %s' % title, '# %s' % meta, 'headword\tstates\tprovenance\tdicts\tsenses']
        for ia in rows:
            a = agg[ia]
            L.append('%s\t%s\t%s\t%s\t%d' % (ia, states_of(a), prov_of(a),
                                             ','.join(sorted(a['dicts'])), a['n']))
        return '\n'.join(L) + '\n'
    L = ['# %s' % title, '', meta, '',
         '%d headwords%s. Columns: states it spans · register provenance '
         '(ls=cited, dcs=corpus) · dictionaries · senses.'
         % (len(rows), '' if min_dicts < 2 else ' (in ≥%d dictionaries)' % min_dicts),
         '', '| headword | states | prov | dicts | n |', '|---|---|---|---|--:|']
    for ia in rows:
        a = agg[ia]
        L.append('| %s | %s | %s | %s | %d |' % (ia, states_of(a), prov_of(a),
                 ','.join(sorted(a['dicts'])), a['n']))
    return '\n'.join(L) + '\n'


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    reg = args[0]
    dicts = list(CANON)
    state_filter = prov_filter = out = title = None
    exclude_states = []
    fmt = 'md'
    min_dicts = 1
    state_only = False
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--dicts':
            dicts = args[i + 1].split(','); i += 2
        elif a == '--state':
            state_filter = args[i + 1]; i += 2
        elif a == '--exclude-state':
            exclude_states = args[i + 1].split(','); i += 2
        elif a == '--prov':
            prov_filter = args[i + 1]; i += 2
        elif a == '--min-dicts':
            min_dicts = int(args[i + 1]); i += 2
        elif a == '--format':
            fmt = args[i + 1]; i += 2
        elif a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--title':
            title = args[i + 1]; i += 2
        elif a == '--state-only':
            state_only = True; i += 1
        else:
            raise SystemExit('unknown option: %s' % a)

    if not state_only and reg not in renou_register.REGISTERS:
        raise SystemExit('unknown register %r (see renou_register.REGISTERS)' % reg)
    agg = collect(reg, dicts, state_filter, prov_filter, state_only, exclude_states)
    if not title:
        kind = 'state' if state_only else 'register'
        title = 'Renou %s glossary: %s' % (kind, reg)
    meta = ('Generated by `renou_glossary.py %s` from the Renou-tagged dictionaries '
            '(%s). Derived data — regenerate, do not hand-edit.'
            % (' '.join(args), ', '.join(d.upper() for d in dicts)))
    text = render(agg, reg, title, fmt, min_dicts, meta)
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8', newline='\n').write(text)
        print('%d headwords → %s' % (sum(1 for a in agg.values()
              if len(a['dicts']) >= min_dicts), out))
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
