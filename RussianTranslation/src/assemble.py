#!/usr/bin/env python
"""pwg_ru P2 — harvest + assemble (De→Ru, no API).

Ties stage-0 (pwg_mask: the masked German skeleton + card identity) to the
harvest sources (corpus_gate: the 5 dictionaries + the SamudraManthanam
parallel corpus) into an assembled pwg_ru card. The card shows what we ALREADY
have — the source-tagged, attested Russian senses — alongside the German gloss
that still needs translating (stage 3). For a covered headword this is already a
usable Russian entry before any LLM touches it; harvested meanings are ADDITIVE
senses, not just anchors.

No model is called. The dictionary data (src/*.jsonl) is gitignored; the corpus
is queried in place from SamudraManthanam.

Modes:
  python assemble.py card   <key1>     show one assembled card (pretty)
  python assemble.py sample [N]        show N covered cards (richest reuse first)
  python assemble.py build  [N]        emit assembled_cards.jsonl (gitignored)
"""
import json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg
import corpus_harvest as ch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assembled_cards.jsonl')

_CHIDX = None


def ch_index():
    """The SLP1→alignments index over the whole corpus lexicon (built once)."""
    global _CHIDX
    if _CHIDX is None:
        _CHIDX = ch.index()
    return _CHIDX


def corpus_lexicon_senses(key1, prefer_period=None):
    """Stratified, lemma-grouped, content-filtered Russian attested in the
    parallel corpus for this headword, plus the near-synonym candidate set
    (distinct content lemmas, freq-ranked) to be DISCRIMINATED per Apresjan."""
    rows = ch_index().get(cg.form_key(key1), [])
    if not rows:
        return None
    strata = ch.harvest(rows, prefer_period)
    cand = collections.Counter()
    for s in strata:
        for r in s['renderings']:
            if r.get('pos') != 'func':
                cand[r['lemma']] += r['count']
    return {
        'n_attestations': len(rows),
        'strata': [{'period': s['period'], 'genre': s['genre'], 'total': s['total'],
                    'renderings': [{'lemma': r['lemma'], 'count': r['count'],
                                    'kinds': r['kinds'], 'pos': r.get('pos'),
                                    'forms': r['forms'][:4]} for r in s['renderings'][:6]]}
                   for s in strata],
        'synonym_candidates': [w for w, _ in cand.most_common(12)],
    }


def iast(key1):
    return ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))


def harvest(idx, key1, key2):
    indep, kow = cg.lookup(idx, key1, key2)
    corpus = cg.corpus_examples(key1, limit=3)
    return indep, kow, corpus


def assemble(idx, key1, key2, records):
    """records = list of masked record bodies (one per homonym)."""
    indep, kow, corpus = harvest(idx, key1, key2)
    recs = []
    for body in records:
        sk, ph, st = pwg_mask.mask(body)
        recs.append({'de_skeleton': sk,
                     'placeholders': ph,
                     'lossless': pwg_mask.restore(sk, ph) == body})
    pub_dict = sum(1 for g in indep if g.get('publishable'))
    clex = corpus_lexicon_senses(key1)        # stratified corpus reuse (the 190k-key lexicon)
    return {
        'key1': key1, 'key2': key2, 'iast': iast(key1),
        'records': recs,
        'attested_senses': {
            'dict': [{'source': g['source'], 'code': g['code'], 'gloss': g['gloss'],
                      'publishable': g.get('publishable', False)} for g in indep],
            'kow_reference': kow,            # Kossowich d.1883 = public domain, citable as reference
            'corpus': corpus,                # verse examples (FTS)
            'corpus_lexicon': clex,          # stratified, discriminated attested renderings
        },
        # rights for the PRINTED edition: only PD senses may be quoted verbatim;
        # modern dicts + corpus translations are correctness signals for a fresh
        # translation, not copy sources. The exporter gates the card BODY on this.
        'rights': {
            'publishable_dict_senses': pub_dict,
            'restricted_dict_senses': len(indep) - pub_dict,
            'corpus_rights': 'unverified',   # corpus translations may be in-copyright → evidence-only by default
            'note': 'Quote verbatim only Knauer/Kossowich (PD); Kochergina/Smirnov/Frisch '
                    'and corpus glosses inform a fresh translation but are not copied.',
        },
        'reuse': {'n_dict': len(indep), 'n_kow': len(kow), 'n_corpus': len(corpus),
                  'n_corpus_lex': clex['n_attestations'] if clex else 0,
                  'covered': bool(indep or kow or corpus or clex)},
    }


def grouped_records(limit_scan=None):
    """Yield (key1, key2, [bodies]) grouping consecutive same-key1 records."""
    cur_k1 = cur_k2 = None
    bodies = []
    for buf in pwg_mask.records(limit_scan):
        k1, k2, body = pwg_mask.parse(buf)
        if k1 != cur_k1:
            if cur_k1 is not None:
                yield cur_k1, cur_k2, bodies
            cur_k1, cur_k2, bodies = k1, k2, []
        bodies.append(body)
    if cur_k1 is not None:
        yield cur_k1, cur_k2, bodies


def pretty(card):
    print('=' * 74)
    print('%s  (key2 %s · IAST %s)  — %d record(s)'
          % (card['key1'], card['key2'], card['iast'], len(card['records'])))
    a = card['attested_senses']
    print('\n  ATTESTED RUSSIAN SENSES (reuse — already exist):')
    if a['dict']:
        for g in a['dict']:
            print('    · [%s] %s' % (g['source'], _clean(g['gloss'])[:150]))
    if a['kow_reference']:
        for g in a['kow_reference']:
            print('    · [KOW · reference] %s' % _clean(g)[:150])
    if a['corpus']:
        for e in a['corpus']:
            print('    · [corpus %s %s] %s' % (e['work'], e['passage'], e['ru'][:120]))
    cl = a.get('corpus_lexicon')
    if cl:
        print('  CORPUS-ATTESTED RUSSIAN by stratum (%d attestations):' % cl['n_attestations'])
        for s in cl['strata']:
            rends = ', '.join('%s(%d)' % (r['lemma'], r['count'])
                              for r in s['renderings'] if r.get('pos') != 'func')
            print('    · %-26s %s' % (s['period'], rends))
        print('    → near-synonym set to DISCRIMINATE (Apresjan): %s'
              % ' · '.join(cl['synonym_candidates']))
    if not (a['dict'] or a['kow_reference'] or a['corpus'] or cl):
        print('    (none — long-tail headword; full German translation needed)')
    print('\n  GERMAN GLOSS — pending translation (stage 3):')
    for r in card['records']:
        print('    %s' % r['de_skeleton'].replace('\n', ' ')[:200])
    print('  reuse: %d dict · %d KOW · %d corpus-ex · %d corpus-lex  | round-trip ok: %s'
          % (card['reuse']['n_dict'], card['reuse']['n_kow'], card['reuse']['n_corpus'],
             card['reuse'].get('n_corpus_lex', 0),
             all(r['lossless'] for r in card['records'])))


def _clean(s):
    import re
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def cmd_card(idx, args):
    target = args[0]
    for k1, k2, bodies in grouped_records():
        if k1 == target:
            pretty(assemble(idx, k1, k2, bodies))
            return
    print('not found:', target)


def cmd_sample(idx, args):
    n = int(args[0]) if args else 5
    shown = 0
    for k1, k2, bodies in grouped_records(8000):
        # fast dict check before the slower corpus query
        if not (cg.lookup(idx, k1, k2)[0] or cg.lookup(idx, k1, k2)[1]):
            continue
        card = assemble(idx, k1, k2, bodies)
        pretty(card)
        shown += 1
        if shown >= n:
            break


def cmd_build(idx, args):
    n = int(args[0]) if args else None
    tot = cov = 0
    with open(OUT, 'w', encoding='utf-8', newline='') as o:
        for k1, k2, bodies in grouped_records(n):
            card = assemble(idx, k1, k2, bodies)
            o.write(json.dumps(card, ensure_ascii=False) + '\n')
            tot += 1
            cov += 1 if card['reuse']['covered'] else 0
    print('wrote %d assembled cards to %s (%d with reuse, %.1f%%)'
          % (tot, os.path.basename(OUT), cov, 100.0 * cov / max(tot, 1)))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    idx = cg.load_index()
    cmd, args = sys.argv[1], sys.argv[2:]
    {'card': cmd_card, 'sample': cmd_sample, 'build': cmd_build}.get(
        cmd, lambda *_: print(__doc__))(idx, args)


if __name__ == '__main__':
    main()
