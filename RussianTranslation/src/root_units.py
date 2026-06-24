#!/usr/bin/env python
"""root_units.py — segment a PWG root mega-record into per-prefix translation units.

Problem: a root like BU is ONE headword card (1315 lines, ~40 prefixed verbs packed
into <div n="p"> divisions). Sending that as a single card overwhelms the translator and
QA. This bridge splits it into one translation unit per prefix sub-card, in the SAME
manifest shape compile_translatable.py emits ({layer,ref,lang,text,keep}), with the added
root_key / upasarga / seg_index so downstream batching, translation and QA can group and
order by sub-card.

Reuses (no reinvention):
  - research/root_segment_proto.py  -> read_record(), segment()   (the <div n=p> slicer)
  - compile_translatable.py         -> PCT / INLINE_SA regexes     (the German-gloss mask)

  python root_units.py one   BU [pwg.txt]        # print the segmented manifest (md)
  python root_units.py write BU [BU2 ...]        # -> pilot/root_translate/<safe>.json+md
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.join(HERE, '..', 'research')
sys.path.insert(0, RESEARCH)
sys.path.insert(0, HERE)

import root_segment_proto as RS                       # noqa: E402
from compile_translatable import PCT, INLINE_SA       # noqa: E402  ({%..%}, {#..#}/<is>)
from safe_filename import safe_name                    # noqa: E402

PWG = os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt')
OUT = os.path.join(HERE, 'pilot', 'root_translate')
SIGLA = re.compile(r'<ls\b[^>]*>.*?</ls>|<ab\b[^>]*>.*?</ab>|<lex\b[^>]*>.*?</lex>')


def card_units(text, root_key, upasarga, seg_index, kind):
    """One sub-card's lines (joined) -> list of translation units (one per German gloss)."""
    keep = INLINE_SA.findall(text) + SIGLA.findall(text)
    glosses = [g.strip().rstrip(':').strip() for g in PCT.findall(text)]
    glosses = [g for g in glosses if g and not g.startswith('{')]
    ref = upasarga + '+' + root_key if kind == 'prefix' else root_key
    if not glosses:                                    # form-only card (no German to translate)
        return [{'layer': 'PWG-root', 'ref': ref, 'root_key': root_key,
                 'upasarga': upasarga, 'seg_index': seg_index, 'kind': kind,
                 'lang': ['none'], 'text': '', 'keep': keep[:12]}]
    out = []
    for j, g in enumerate(glosses):
        out.append({'layer': 'PWG-root', 'ref': ref + (':%d' % j if len(glosses) > 1 else ''),
                    'root_key': root_key, 'upasarga': upasarga, 'seg_index': seg_index,
                    'kind': kind, 'lang': ['de'], 'text': g, 'keep': keep[:12]})
    return out


def manifest(L, pwg=PWG):
    rec = RS.read_record(pwg, L)
    if rec is None:
        return None
    meta, data, lend = rec
    k1 = (re.search(r'<k1>([^<]*)', meta) or [None, '?'])[1]
    cards = RS.segment(data)
    units, seg = [], 0
    for c in cards:
        units += card_units('\n'.join(c['lines']), k1, c['upasarga'], seg, c['kind'])
        seg += 1
    return {'key': k1, 'L': L, 'safe': safe_name(k1), 'sub_cards': len(cards),
            'units': units}


def to_md(man):
    de = sum(1 for u in man['units'] if u['lang'] == ['de'])
    L = ['# %s (L=%s) — segmented root manifest' % (man['key'], man['L']), '',
         '%d sub-cards -> %d translation units (%d German to translate). '
         'root_key/upasarga/seg_index group + order the sub-cards.'
         % (man['sub_cards'], len(man['units']), de), '',
         '| seg | ref | kind | lang | to translate | keep |',
         '|---|---|---|---|---|---|']
    for u in man['units']:
        L.append('| %d | %s | %s | %s | %s | %s |' % (
            u['seg_index'], u['ref'][:22], u['kind'], ','.join(u['lang']),
            u['text'].replace('|', '\\|')[:70], (' · '.join(u['keep']))[:40].replace('|', '\\|')))
    return '\n'.join(L) + '\n'


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'one'
    if cmd == 'one':
        L = sys.argv[2] if len(sys.argv) > 2 else '55166'
        pwg = sys.argv[3] if len(sys.argv) > 3 else PWG
        man = manifest(L, pwg)
        print(to_md(man) if man else 'L=%s not found' % L)
    elif cmd == 'write':
        os.makedirs(OUT, exist_ok=True)
        for L in sys.argv[2:]:
            man = manifest(L)
            if not man:
                print('  L=%s not found' % L); continue
            base = os.path.join(OUT, '%s_%s' % (man['safe'], L))
            json.dump(man, open(base + '.json', 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            open(base + '.md', 'w', encoding='utf-8').write(to_md(man))
            print('  %-6s L=%s : %d sub-cards -> %d units -> %s.{json,md}'
                  % (man['key'], L, man['sub_cards'], len(man['units']),
                     os.path.relpath(base, HERE)))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
