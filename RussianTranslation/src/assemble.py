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
  python assemble.py build  [N] [--offset K] [--out PATH] [--quarantine PATH]
                                      emit assembled_cards.jsonl (gitignored)
"""
import json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg
import corpus_harvest as ch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assembled_cards.jsonl')
QUARANTINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assembled_cards.quarantine.jsonl')
OUT_TMP = OUT + '.tmp'
QUARANTINE_TMP = QUARANTINE + '.tmp'

_CHIDX = None


def replace_output(tmp, dest):
    try:
        os.replace(tmp, dest)
    except PermissionError as e:
        raise RuntimeError(
            'could not replace %s; existing export left untouched, temp output kept at %s'
            % (dest, tmp)
        ) from e


def ch_index():
    """The SLP1→alignments index over the whole corpus lexicon (built once)."""
    global _CHIDX
    if _CHIDX is None:
        _CHIDX = ch.index()
    return _CHIDX


def _corpus_lexicon_senses_from_rows(rows, prefer_period=None):
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


def corpus_lexicon_senses(key1, prefer_period=None):
    """Stratified, lemma-grouped, content-filtered Russian attested in the
    parallel corpus for this headword, plus the near-synonym candidate set
    (distinct content lemmas, freq-ranked) to be DISCRIMINATED per Apresjan."""
    return _corpus_lexicon_senses_from_rows(
        ch_index().get(cg.form_key(key1), []), prefer_period)


def corpus_examples_from_rows(rows, limit=3):
    """Cheap build-time corpus examples from corpus_lexicon rows.

    Interactive lookup still uses corpus_gate.corpus_examples(), whose SQLite FTS
    result is fuller. The assembled export only requires stable {work, passage,
    ru} evidence, so build can avoid per-card FTS queries.
    """
    out, seen = [], set()
    for r in rows:
        if r.get('kind') != 'translation':
            continue
        ru = (r.get('ru') or '').strip()
        work = r.get('work')
        passage = r.get('passage')
        if not (ru and work and passage):
            continue
        key = (work, passage)
        if key in seen:
            continue
        seen.add(key)
        out.append({'work': work, 'passage': passage, 'ru': ru})
        if len(out) >= limit:
            break
    return out


def precompute_corpus_lexicon_cache(raw_idx):
    cache = {}
    for key, rows in raw_idx.items():
        senses = _corpus_lexicon_senses_from_rows(rows)
        if senses:
            cache[key] = senses
    return cache


def precompute_corpus_examples_cache(raw_idx):
    return {key: examples for key, rows in raw_idx.items()
            for examples in [corpus_examples_from_rows(rows)] if examples}


def build_context():
    raw_idx = ch_index()
    print('  precomputing corpus lexicon cache for %d attested key(s)'
          % len(raw_idx), file=sys.stderr)
    return {
        'corpus_lexicon': precompute_corpus_lexicon_cache(raw_idx),
        'corpus_examples': precompute_corpus_examples_cache(raw_idx),
    }


def iast(key1):
    return ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))


def harvest(idx, key1, key2, ctx=None):
    indep, kow = cg.lookup(idx, key1, key2)
    if ctx is None:
        corpus = cg.corpus_examples(key1, limit=3)
    else:
        corpus = ctx['corpus_examples'].get(cg.form_key(key1), [])
    return indep, kow, corpus


def assemble(idx, key1, key2, records, ctx=None):
    """records = list of masked record bodies (one per homonym)."""
    indep, kow, corpus = harvest(idx, key1, key2, ctx)
    recs = []
    quarantined = []
    for record_no, body in enumerate(records, 1):
        sk, ph, st = pwg_mask.mask(body)
        if pwg_mask.restore(sk, ph) != body:
            quarantined.append({'key1': key1, 'key2': key2, 'record_no': record_no,
                                'reason': 'pwg_mask round-trip failed',
                                'body_excerpt': _clean(body)[:240],
                                'placeholder_count': len(ph)})
            continue
        recs.append({'de_skeleton': sk,
                     'placeholders': ph,
                     'lossless': True})
    pub_dict = sum(1 for g in indep if g.get('publishable'))
    if ctx is None:
        clex = corpus_lexicon_senses(key1)    # lazy interactive path
    else:
        clex = ctx['corpus_lexicon'].get(cg.form_key(key1))
    return {
        'key1': key1, 'key2': key2, 'iast': iast(key1),
        'records': recs,
        'quarantined_records': len(quarantined),
        '_quarantine': quarantined,
        'attested_senses': {
            'dict': [{'source': g['source'], 'code': g['code'], 'gloss': g['gloss'],
                      'publishable': g.get('publishable', False)} for g in indep],
            'kow_reference': kow,            # Kossowich d.1883 = public domain, citable as reference
            'corpus': corpus,                # verse examples (FTS)
            'corpus_lexicon': clex,          # stratified, discriminated attested renderings
        },
        # Rights for the PRINTED edition: modern Sanskrit-Russian sources are
        # approved for extensive use. Keep provenance/attribution; do not strip
        # approved modern-source text from the card body.
        'rights': {
            'publishable_dict_senses': pub_dict,
            'restricted_dict_senses': 0,
            'corpus_rights': 'approved-for-project-use',
            'note': 'Modern Sanskrit-Russian sources are approved for publication use; '
                    'preserve source attribution and provenance.',
        },
        'reuse': {'n_dict': len(indep), 'n_kow': len(kow), 'n_corpus': len(corpus),
                  'n_corpus_lex': clex['n_attestations'] if clex else 0,
                  'covered': bool(indep or kow or corpus or clex)},
    }


def grouped_records(limit_scan=None, offset=0, limit=None):
    """Yield (key1, key2, [bodies]) grouping consecutive same-key1 records."""
    cur_k1 = cur_k2 = None
    bodies = []
    seen = emitted = 0

    def maybe_emit(k1, k2, recs):
        nonlocal seen, emitted
        if seen >= offset and (limit is None or emitted < limit):
            emitted += 1
            return k1, k2, recs
        seen += 1
        return None

    for buf in pwg_mask.records(limit_scan):
        k1, k2, body = pwg_mask.parse(buf)
        if k1 != cur_k1:
            if cur_k1 is not None:
                row = maybe_emit(cur_k1, cur_k2, bodies)
                if row:
                    yield row
                if limit is not None and emitted >= limit:
                    return
            cur_k1, cur_k2, bodies = k1, k2, []
        bodies.append(body)
    if cur_k1 is not None:
        row = maybe_emit(cur_k1, cur_k2, bodies)
        if row:
            yield row


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
    if card.get('quarantined_records'):
        print('  quarantined lossy record(s): %d → %s'
              % (card['quarantined_records'], os.path.basename(QUARANTINE)))
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


def build_tmp_path(path):
    return path + '.tmp'


def parse_build_args(args):
    n = offset = None
    out, quarantine = OUT, QUARANTINE
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--offset':
            offset = int(args[i + 1]); i += 2
        elif a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--quarantine':
            quarantine = args[i + 1]; i += 2
        elif a.startswith('--'):
            raise SystemExit('unknown build option: %s' % a)
        elif n is None:
            n = int(a); i += 1
        else:
            raise SystemExit('unexpected build argument: %s' % a)
    return n, (offset or 0), out, quarantine


def cmd_build(idx, args):
    n, offset, out, quarantine = parse_build_args(args)
    out_tmp = build_tmp_path(out)
    quarantine_tmp = build_tmp_path(quarantine)
    ctx = build_context()
    tot = cov = qn = 0
    with open(out_tmp, 'w', encoding='utf-8', newline='') as o, \
         open(quarantine_tmp, 'w', encoding='utf-8', newline='') as q:
        for k1, k2, bodies in grouped_records(offset=offset, limit=n):
            card = assemble(idx, k1, k2, bodies, ctx)
            for qr in card.pop('_quarantine', []):
                q.write(json.dumps(qr, ensure_ascii=False) + '\n')
                qn += 1
            o.write(json.dumps(card, ensure_ascii=False) + '\n')
            tot += 1
            cov += 1 if card['reuse']['covered'] else 0
            if tot % 5000 == 0:
                print('  assembled %d card(s), covered %d, quarantined %d'
                      % (tot, cov, qn), file=sys.stderr)
    replace_output(out_tmp, out)
    replace_output(quarantine_tmp, quarantine)
    print('wrote %d assembled cards to %s (%d with reuse, %.1f%%; quarantined %d lossy record(s) → %s)'
          % (tot, os.path.basename(out), cov, 100.0 * cov / max(tot, 1),
             qn, os.path.basename(quarantine)))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    idx = cg.load_index()
    cmd, args = sys.argv[1], sys.argv[2:]
    {'card': cmd_card, 'sample': cmd_sample, 'build': cmd_build}.get(
        cmd, lambda *_: print(__doc__))(idx, args)


if __name__ == '__main__':
    main()
