#!/usr/bin/env python
"""Pilot input — the FULL layered card (PWG + PW + SCH + PWKVN + NWS net-new).

Extends _pilot_gen.py from PWG-only to the whole supplement chain, so the translator
produces ONE Russian entry that is the union of all layers. Per card key:
  • PWG base record(s) + their Nachträge   → microstructure portrait + labeled raw
  • PW (revision) / SCH (Schmidt) / PWKVN   → raw, layer-labeled (from dict_merge)
  • NWS net-new fragment                    → the ~2013 cumulative addendum (if any)

Output: src/pilot/input/<key>.portrait.json + <key>.raw.txt (gitignored).

  python _pilot_gen_merged.py [key ...]      default: a small NWS-exercising batch
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import microstructure as M
import dict_merge as dm
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'input')

DEFAULT = ['arTa', 'agni', 'amfta', 'aMSa', 'anna', 'akzara']

ROLE = {'pw': 'PW — Böhtlingk kürzere Fassung (revision of PWG; may correct gender/sense)',
        'sch': 'SCH — Schmidt Nachträge 1928 (pure addenda to PW; °=new vs pw, *=first attestation)',
        'pwkvn': 'PWKVN — PWK variant supplement (keyed to PW sense numbers)',
        'nws': 'NWS — Nachtragswörterbuch (Halle, cumulative addendum; condensed "Kleines Zitat" '
               '— render the new lemma/sense/grammar + keep its sigla)'}


def main():
    keys = sys.argv[1:] or DEFAULT
    os.makedirs(OUT, exist_ok=True)
    pwg_idx = dm.index('pwg')
    for key in keys:
        fk = cg.form_key(key)
        pwg_bufs = pwg_idx.get(fk, [])
        if not pwg_bufs:
            print('  MISSING in PWG: %s' % key); continue

        # 1) PWG portrait (corpus evidence) + labeled raw records (main + Nachträge)
        portraits = [M.portrait(buf) for buf in pwg_bufs]
        json.dump(portraits, open(os.path.join(OUT, key + '.portrait.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        sections = []
        for i, buf in enumerate(pwg_bufs):
            role = ('PWG — MAIN ENTRY (Böhtlingk-Roth, large)' if i == 0 else
                    'PWG — NACHTRÄGE/ADDENDA #%d — patches keyed to the main sense numbers; '
                    'render in full' % i)
            sections.append('=== LAYER: %s ===\n\n%s' % (role, '\n'.join(buf[1:])))

        # 2) PW / SCH / PWKVN + NWS net-new layers (all from the merge), each labeled.
        #    dm.merged() now owns the NWS fold — it appends the external addendum last
        #    when (and only when) it adds beyond pw/Schmidt (has_nws_extra).
        layer_counts = {}
        for L in dm.merged(key):
            code = L['layer']
            if code == 'pwg':
                continue
            layer_counts[code] = len(L['records'])
            for r in L['records']:
                sections.append('=== LAYER: %s ===\n\n%s' % (ROLE.get(code, code.upper()), r))

        open(os.path.join(OUT, key + '.raw.txt'), 'w', encoding='utf-8').write('\n\n'.join(sections))
        ns = sum(len([s for s in p['senses'] if s['n'] != '0']) for p in portraits)
        print('  %-10s PWG rec=%d senses=%d | PW=%d SCH=%d PWKVN=%d | NWS-extra=%s'
              % (key, len(pwg_bufs), ns, layer_counts.get('pw', 0), layer_counts.get('sch', 0),
                 layer_counts.get('pwkvn', 0), 'yes' if layer_counts.get('nws') else 'no'))
    print('wrote merged pilot inputs → %s' % OUT)


if __name__ == '__main__':
    main()
