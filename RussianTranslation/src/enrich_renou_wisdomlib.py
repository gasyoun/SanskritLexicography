#!/usr/bin/env python
"""enrich_renou_wisdomlib.py — tertiary, lower-confidence Renou hint from wisdomlib.

Third signal after <ls> (citation) and DCS (corpus attestation): wisdomlib groups a
word's meanings by TRADITION (Buddhism / Jainism / Ayurveda / Vyakarana / Vedic /
Vedanta / …). Buddhism/Jainism → a **V** hint; the others a weaker era hint. It NEVER
overrides ls/dcs — it only corroborates, and a state supported by `wl` alone is the
weakest evidence (visible in renou_provenance).

Input: word_traditions.jsonl from the wisdomlib `definitions.py` fetcher (in the
SamudraManthanam repo). Join is on a diacritic-free key, since wisdomlib slugs are
ASCII (`akshobhya`) while our headwords are SLP1→IAST (`akṣobhya`).

  python enrich_renou_wisdomlib.py CARDS.jsonl --wl word_traditions.jsonl [--out OUT]

Adds per card: renou_wl (states from wisdomlib), and merges into renou_enriched /
renou_provenance with source tag "wl".
"""
import json, os, re, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou
import corpus_gate as cg

STATES = renou.STATES
_ORDER = {s: i for i, s in enumerate(STATES)}

# wisdomlib tradition tag -> Renou state. Broad/era-less tags contribute nothing.
WL_RENOU = {'buddhism': 'V', 'jainism': 'V', 'ayurveda': 'IV', 'vyakarana': 'II',
            'vedic': 'I', 'vedanta': 'IV', 'hinduism': None, 'sanskrit_dict': None}


def fold_key(s):
    """Diacritic-free lowercase join key. Collapses wisdomlib's 'sh' digraph so the
    ASCII slug (akshobhya) meets the folded IAST (akṣobhya→aksobhya)."""
    nfd = unicodedata.normalize('NFD', s.lower())
    bare = ''.join(c for c in nfd if not unicodedata.combining(c))
    return bare.replace('sh', 's')


def wl_states_from_traditions(trads):
    sts = set()
    for t in trads or []:
        st = WL_RENOU.get(t)
        if st:
            sts.add(st)
    return sts


def load_wl(path):
    """fold_key(word) -> {wl states}."""
    out = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get('error'):
            continue
        out[fold_key(r['word'])] = wl_states_from_traditions(r.get('traditions'))
    return out


def card_of(obj):
    return obj.get('card', obj) if isinstance(obj, dict) else obj


def headword_iast(obj):
    key1 = card_of(obj).get('key1') or obj.get('key1') or ''
    return ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))


def enrich(obj, wl, stats):
    iast = headword_iast(obj)
    wl_sts = wl.get(fold_key(iast), set())
    obj['renou_wl'] = sorted(wl_sts, key=_ORDER.get)

    prov = obj.get('renou_provenance') or {}
    enriched = set(obj.get('renou_enriched') or [])
    enriched |= set(obj.get('renou_ls') or []) | set(obj.get('renou_dcs') or [])
    for st in wl_sts:
        enriched.add(st)
        prov.setdefault(st, [])
        if 'wl' not in prov[st]:
            prov[st].append('wl')
    obj['renou_enriched'] = sorted(enriched, key=_ORDER.get)
    obj['renou_provenance'] = {k: prov[k] for k in sorted(prov, key=_ORDER.get)}

    stats['cards'] += 1
    if wl_sts:
        stats['wl_hit'] += 1
        # a state newly contributed by wl alone (no ls/dcs backing)
        backed = set(obj.get('renou_ls') or []) | set(obj.get('renou_dcs') or [])
        for st in wl_sts:
            stats['wl_state'][st] += 1
            if st not in backed:
                stats['wl_only'][st] += 1


def run(path, wl_path, out, report_only):
    wl = load_wl(wl_path)
    stats = {'cards': 0, 'wl_hit': 0,
             'wl_state': collections.Counter(), 'wl_only': collections.Counter()}
    tmp = (out + '.tmp') if not report_only else None
    sink = open(tmp, 'w', encoding='utf-8', newline='') if tmp else None
    try:
        for line in open(path, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            enrich(obj, wl, stats)
            if sink:
                sink.write(json.dumps(obj, ensure_ascii=False) + '\n')
    finally:
        if sink:
            sink.close()
    if tmp:
        os.replace(tmp, out)
    print('wl words: %d  · cards: %d  · wl-hit: %d'
          % (len(wl), stats['cards'], stats['wl_hit']))
    print('  states hinted by wisdomlib:',
          {s: stats['wl_state'].get(s, 0) for s in STATES})
    print('  states wl contributed ALONE (no ls/dcs):',
          {s: stats['wl_only'].get(s, 0) for s in STATES})
    if tmp:
        print('→ %s' % out)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    path = args[0]
    wl_path = out = None
    report_only = False
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--wl':
            wl_path = args[i + 1]; i += 2
        elif a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--report':
            report_only = True; i += 1
        else:
            raise SystemExit('unknown option: %s' % a)
    if not wl_path:
        raise SystemExit('require --wl word_traditions.jsonl')
    if out is None and not report_only:
        out = path
    run(path, wl_path, out, report_only)


if __name__ == '__main__':
    main()
