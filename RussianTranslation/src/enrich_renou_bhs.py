#!/usr/bin/env python
"""enrich_renou_bhs.py — deterministic V transfer from BHS to PWG/MW/AP.

Edgerton's Buddhist Hybrid Sanskrit dictionary IS the state-**V** register: every
BHS headword is, by definition, attested in Buddhist Sanskrit. So a headword that
appears in BHS but lacks V in a mainstream dictionary (PWG/MW/AP) is simply a
missed attestation — fillable deterministically, no fetching.

This adds V (provenance source `"bhs"`) to any target entry whose headword is a
BHS headword: a NEW V where the dict had none, or a corroborating `"bhs"` on an
existing V. It is an attestation claim ("this word occurs in Edgerton's BHS"),
not a semantic one — so common words used in Buddhist texts (e.g. viṣṇu) correctly
gain a V-register attestation, distinguishable in `renou_provenance` from
`ls`/`dcs`/`wl`.

Join is on a diacritic-free key (sh-folded), matching the wisdomlib consumer.

  python enrich_renou_bhs.py IN.jsonl [--out OUT] [--bhs bhs_renou.jsonl] [--report]
"""
import json, os, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou

STATES = renou.STATES
_ORDER = {s: i for i, s in enumerate(STATES)}
HERE = os.path.dirname(os.path.abspath(__file__))


def fold(s):
    bare = ''.join(c for c in unicodedata.normalize('NFD', s.lower())
                   if not unicodedata.combining(c))
    return bare.replace('sh', 's')


def load_bhs(path):
    """Fold-keys of every BHS headword = the Buddhist-Sanskrit-attested vocabulary."""
    keys = set()
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line:
            keys.add(fold(json.loads(line)['iast']))
    return keys


def enrich(obj, bhs, stats):
    stats['cards'] += 1
    if fold(obj.get('iast', '')) not in bhs:
        return
    stats['bhs_hit'] += 1
    enriched = set(obj.get('renou_enriched') or [])
    had_v = 'V' in enriched
    enriched.add('V')
    obj['renou_enriched'] = sorted(enriched, key=_ORDER.get)
    prov = obj.get('renou_provenance') or {}
    prov.setdefault('V', [])
    if 'bhs' not in prov['V']:
        prov['V'].append('bhs')
    obj['renou_provenance'] = {k: prov[k] for k in sorted(prov, key=_ORDER.get)}
    obj['renou_bhs'] = True
    if had_v:
        stats['corroborated'] += 1
    else:
        stats['new_v'] += 1


def run(path, out, bhs_path, report_only):
    bhs = load_bhs(bhs_path)
    stats = collections.Counter()
    tmp = (out + '.tmp') if not report_only else None
    sink = open(tmp, 'w', encoding='utf-8', newline='') if tmp else None
    try:
        for line in open(path, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            enrich(obj, bhs, stats)
            if sink:
                sink.write(json.dumps(obj, ensure_ascii=False) + '\n')
    finally:
        if sink:
            sink.close()
    if tmp:
        os.replace(tmp, out)
    print('BHS vocab: %d  · %s' % (len(bhs), os.path.basename(path)))
    print('  cards: %d · BHS-matched: %d' % (stats['cards'], stats['bhs_hit']))
    print('  V ADDED (was missing): %d · V corroborated (already had it): %d'
          % (stats['new_v'], stats['corroborated']))
    if tmp:
        print('→ %s' % out)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    path = args[0]
    out = None
    bhs_path = os.path.join(HERE, 'bhs_renou.jsonl')
    report_only = False
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--bhs':
            bhs_path = args[i + 1]; i += 2
        elif a == '--report':
            report_only = True; i += 1
        else:
            raise SystemExit('unknown option: %s' % a)
    if out is None and not report_only:
        out = path
    run(path, out, bhs_path, report_only)


if __name__ == '__main__':
    main()
