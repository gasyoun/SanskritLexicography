#!/usr/bin/env python
"""renou_portrait.py — turn the Renou signals into editor-facing output.

Two editorial uses of the tags:

1. `portrait(entry)` — a compact, human-readable Renou label for a headword, for
   display in the dictionary entry: the era span, the first attestation, and a
   confidence note from `renou_provenance` (a V supported only by `bhs` is flagged
   register-only). Runs on a canonical `{code}.renou.jsonl`.

2. `order_senses_oldest_first(card)` — reorder a structured card's senses so the
   earliest-attested meaning comes first (uses the per-sense `renou_oldest` +
   `renou_oldest_sense` that annotate_renou writes). Ready for the structured
   per-sense store; a no-op on cards without senses.

  python renou_portrait.py label mw.renou.jsonl [--out OUT]   # add renou_label to each entry
  python renou_portrait.py demo mw.renou.jsonl agni buddha akṣobhya
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou
NAME = {'I': 'ведийское', 'II': 'паниниевское', 'III': 'эпическое',
        'IV': 'классическое', 'V': 'буддийско-джайнское'}
EN = {'I': 'Vedic', 'II': 'Pāṇinian', 'III': 'Epic', 'IV': 'Classical', 'V': 'Buddhist/Jaina'}
_ORDER = {s: i for i, s in enumerate(renou.STATES)}


def portrait(e):
    """-> {renou_label, renou_first, renou_note} or None when untagged."""
    states = e.get('renou_enriched') or []
    if not states:
        return None
    prov = e.get('renou_provenance') or {}
    first = e.get('renou_dcs_oldest') or e.get('renou_ls_oldest') or ''
    # weak-V flag: V attested only via the BHS register membership (no ls/dcs/wl)
    notes = []
    if 'V' in states and set(prov.get('V', [])) <= {'bhs'}:
        notes.append('V: только регистр (BHS)')
    label = ' · '.join(NAME[s] for s in states)
    return {
        'renou_label': label,
        'renou_first': NAME.get(first, ''),
        'renou_note': '; '.join(notes),
    }


def order_senses_oldest_first(card):
    """Reorder records' senses by earliest attestation. Senses with a dated
    `renou_oldest` lead (by state order = rough chronology), undated keep order.
    Mutates and returns the card; safe on cards lacking senses."""
    for rec in card.get('records', []):
        senses = rec.get('senses')
        if not senses:
            continue
        rec['senses'] = sorted(
            senses,
            key=lambda s: (_ORDER.get(s.get('renou_oldest', ''), 99),
                           senses.index(s)))
    return card


def cmd_label(path, out):
    n = labelled = 0
    sink = open(out + '.tmp', 'w', encoding='utf-8', newline='')
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        o = json.loads(line)
        p = portrait(o)
        if p:
            o.update(p); labelled += 1
        sink.write(json.dumps(o, ensure_ascii=False) + '\n')
        n += 1
    sink.close()
    os.replace(out + '.tmp', out)
    print('%d entries · %d labelled → %s' % (n, labelled, os.path.basename(out)))


def cmd_demo(path, words):
    want = set(words)
    for line in open(path, encoding='utf-8'):
        o = json.loads(line)
        if o.get('iast') in want:
            p = portrait(o)
            print('%-14s %s' % (o['iast'], o.get('renou_enriched')))
            print('   label: %s' % (p['renou_label'] if p else '—'))
            print('   первое свидетельство: %s%s' % (p['renou_first'] or '—',
                  ('  · ' + p['renou_note']) if p and p['renou_note'] else '') if p else '—')
            print('   provenance: %s' % o.get('renou_provenance'))
            want.discard(o['iast'])
            if not want:
                break


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__); return
    cmd, path = args[0], args[1]
    rest = args[2:]
    if cmd == 'label':
        out = path
        if '--out' in rest:
            out = rest[rest.index('--out') + 1]
        cmd_label(path, out)
    elif cmd == 'demo':
        cmd_demo(path, rest)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
