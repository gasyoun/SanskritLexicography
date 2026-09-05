#!/usr/bin/env python
"""H4058 — independent linguistic / corpus-evidence probe over the frozen PWG store.

Read-only over the canonical store and corpus assets; the only writes are a
JSON report under RussianTranslation/reports/ and scratch TM files under the
system temp dir (hold-out replay). Zero provider calls.

Usage:
    python tools/h4058_evidence_probe.py [--store PATH] [--out PATH]
"""
import argparse
import collections
import hashlib
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(RT, 'src', 'pilot'))
import translation_memory as tm  # noqa: E402

DATA = os.path.normpath(os.path.join(RT, '..', '..', 'pwg-ru-data'))
STORE = os.path.join(DATA, 'tm', 'pwg_ru_translated.jsonl')
MANIFEST = os.path.join(RT, 'reports', 'H4056_evidence_packet_manifest.json')

SKT = re.compile(r'\{#(.*?)#\}')
LS = re.compile(r'<ls[^>]*>')
LATIN_GLOSS = re.compile(r'\{%(.*?)%\}')
# teaching-corpus family per REUSE_MAP: kna = Knauer 1908 textbook glossary is the
# only textbook-derived INDEP source; lecture transcripts are not wired anywhere.
TEACHING = {'kna'}
PARALLEL = {'corpus'}          # build_corpus_lexicon verse-aligned Sa<->Ru lexicon
DICT_INDEP = {'koch', 'fri', 'smirnov', 'kna'}
DICT_REF = {'kow'}
SPECIALIST = {'grin12', 'grin3'}
ADVISORY = {'apte_hi', 'vedic_rituals_hi', 'kosha_syn', 'meulenbeld'}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def review_id_of(r):
    return None  # filled from manifest side; we key on (subcard, sense_tag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--out', default=os.path.join(RT, 'reports', 'H4058_evidence_probe.json'))
    a = ap.parse_args()

    rows = load(a.store)
    rep = {'schema': 'h4058-evidence-probe/v1', 'store': a.store,
           'store_sha256': sha256(a.store), 'rows': len(rows)}

    keys = collections.Counter()
    for r in rows:
        keys.update(r.keys())
    rep['store_keys'] = dict(keys)
    rep['has_en_column'] = any(k in keys for k in ('en', 'en_text', 'english'))

    # ---- evidence census ------------------------------------------------
    supp = collections.Counter(); pres = collections.Counter(); sil = collections.Counter()
    contra = collections.Counter(); ev_status = collections.Counter(); c_status = collections.Counter()
    eq_type = collections.Counter(); rev = collections.Counter(); hr = collections.Counter()
    n_no_summary = n_zero_supports = n_parallel_present = n_parallel_supports = 0
    n_teaching_supports = n_teaching_only = n_any_indep = 0
    n_evidence_rows = 0; ev_match = collections.Counter(); ev_rel = collections.Counter()
    skt_drop = skt_add = ls_mismatch = 0; skt_rows = 0
    latin_gloss_de = 0
    for r in rows:
        es = r.get('evidence_summary')
        if not es:
            n_no_summary += 1
        else:
            s = set(es.get('supports_senses') or [])
            p = {x.get('source') for x in (es.get('present') or []) if isinstance(x, dict)}
            supp.update(s); pres.update(p); sil.update(es.get('silent') or [])
            contra.update([str(len(es.get('contradicts') or []))])
            ev_status[es.get('evidence_status')] += 1
            c_status[es.get('corpus_status')] += 1
            if not s:
                n_zero_supports += 1
            if p & PARALLEL:
                n_parallel_present += 1
            if s & PARALLEL:
                n_parallel_supports += 1
            if s & TEACHING:
                n_teaching_supports += 1
                if not (s - TEACHING):
                    n_teaching_only += 1
            if s & (DICT_INDEP | DICT_REF):
                n_any_indep += 1
        eq_type[r.get('equivalence_type')] += 1
        rev[r.get('review_status')] += 1
        hr[((r.get('human_review') or {}).get('decision'))] += 1
        ev = r.get('evidence') or []
        if ev:
            n_evidence_rows += 1
            for e in ev:
                ev_match[e.get('match')] += 1; ev_rel[e.get('relation')] += 1
        de = r.get('de') or ''; ru = r.get('ru') or ''
        sd = SKT.findall(de); sr = SKT.findall(ru)
        if sd:
            skt_rows += 1
            if set(sd) - set(sr):
                skt_drop += 1
        if set(sr) - set(sd):
            skt_add += 1
        if len(LS.findall(de)) != len(LS.findall(ru)):
            ls_mismatch += 1
        if LATIN_GLOSS.search(de):
            latin_gloss_de += 1
    rep['evidence_census'] = {
        'rows_without_evidence_summary': n_no_summary,
        'rows_zero_supports_senses': n_zero_supports,
        'rows_with_any_dictionary_support(koch/kna/fri/smirnov/kow)': n_any_indep,
        'rows_parallel_corpus_present': n_parallel_present,
        'rows_parallel_corpus_supports_sense': n_parallel_supports,
        'rows_teaching_corpus_supports(kna)': n_teaching_supports,
        'rows_teaching_corpus_only_support': n_teaching_only,
        'rows_with_evidence_array': n_evidence_rows,
        'supports_senses_by_source': dict(supp.most_common()),
        'present_by_source': dict(pres.most_common()),
        'silent_by_source': dict(sil.most_common()),
        'contradicts_count_hist': dict(contra),
        'evidence_status': dict(ev_status), 'corpus_status': dict(c_status),
        'evidence_match_kind': dict(ev_match), 'evidence_relation': dict(ev_rel),
        'equivalence_type': dict(eq_type), 'review_status': dict(rev),
        'human_review_decision': dict(hr),
    }
    rep['sanskrit_preservation'] = {
        'rows_with_{#skt#}_in_de': skt_rows,
        'rows_dropping_a_de_sanskrit_token_in_ru': skt_drop,
        'rows_adding_sanskrit_token_absent_in_de': skt_add,
        'rows_ls_citation_count_mismatch_de_vs_ru': ls_mismatch,
        'rows_de_has_{%gloss%}': latin_gloss_de,
    }

    # ---- corpus assets --------------------------------------------------
    assets = {}
    for code in ['koch', 'kna', 'fri', 'smirnov', 'kow', 'grin12', 'grin3', 'apte_hi',
                 'kosha_syn', 'vedic_rituals_hi', 'meulenbeld_plants']:
        p = os.path.join(DATA, 'corpus', code + '.jsonl')
        if os.path.exists(p):
            with open(p, 'rb') as f:
                n = sum(1 for _ in f)
            assets[code] = {'rows': n, 'bytes': os.path.getsize(p)}
        else:
            assets[code] = None
    cl = os.path.join(DATA, 'corpus', 'corpus_lexicon.jsonl')
    tiers = collections.Counter(); texts = collections.Counter(); n_cl = 0; n_ru = 0
    if os.path.exists(cl):
        with open(cl, encoding='utf-8') as f:
            for line in f:
                n_cl += 1
                if n_cl <= 200000:
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    tiers[o.get('tier', '<none>')] += 1
                    texts[(o.get('text') or o.get('source') or o.get('work') or '<none>')] += 1
                    if o.get('ru'):
                        n_ru += 1
        assets['corpus_lexicon'] = {'rows': n_cl, 'bytes': os.path.getsize(cl),
                                    'sample_first_200k_tier': dict(tiers),
                                    'sample_first_200k_top_texts': dict(texts.most_common(12)),
                                    'sample_first_200k_with_ru': n_ru,
                                    'sample_first_line_keys': sorted(o.keys()) if n_cl else []}
    mined = os.path.join(RT, 'src', 'corpus_lexicon.mined.jsonl')
    assets['corpus_lexicon.mined'] = ({'rows': sum(1 for _ in open(mined, 'rb'))}
                                      if os.path.exists(mined) else None)
    assets['en_store'] = [p for p in os.listdir(os.path.join(DATA, 'tm'))
                          if 'en' in p.lower() and p.endswith('.jsonl')]
    rep['corpus_assets'] = assets

    # ---- the ten H4056 cards: independent trace -------------------------
    man = json.load(open(MANIFEST, encoding='utf-8'))
    idx = {(r.get('subcard'), r.get('sense_tag')): r for r in rows}
    cards = []
    chosen = []
    for c in man['cards']:
        r = idx.get((c['subcard'], c['sense_tag']))
        if r is None:
            cards.append({'review_id': c['review_id'], 'found': False}); continue
        chosen.append(r)
        es = r.get('evidence_summary') or {}
        cards.append({
            'review_id': c['review_id'], 'key1': r.get('key1'), 'iast': r.get('iast'),
            'h': r.get('h'), 'equivalence_type': r.get('equivalence_type'),
            'de': (r.get('de') or '')[:220], 'ru': (r.get('ru') or '')[:220],
            'supports_senses': es.get('supports_senses'),
            'present': [x.get('source') for x in es.get('present') or [] if isinstance(x, dict)],
            'silent': es.get('silent'),
            'evidence_n': len(r.get('evidence') or []),
            'evidence_first': ((r.get('evidence') or [{}])[0].get('gloss_ref') or '')[:160],
            'skt_de': SKT.findall(r.get('de') or ''), 'skt_ru': SKT.findall(r.get('ru') or ''),
            'ls_de': len(LS.findall(r.get('de') or '')), 'ls_ru': len(LS.findall(r.get('ru') or '')),
            'input_raw_sha256': (r.get('provenance') or {}).get('input_raw_sha256'),
            'model_version': (r.get('provenance') or {}).get('model_version'),
        })
    rep['h4056_cards'] = cards

    # ---- TM circularity: hold-out replay --------------------------------
    # H4056 built the TM FROM the store and looked the same store rows up (10/10
    # hit by construction). Rebuild the TM with the ten card rows held out: a
    # hit here would mean genuine reuse from OTHER rows; a miss shows the
    # packet's 10/10 measured self-identity, not reuse.
    scratch = tempfile.mkdtemp(prefix='h4058_tm_')
    held = {(r.get('subcard'), r.get('sense_tag')) for r in chosen}
    hold_store = os.path.join(scratch, 'store_minus_cards.jsonl')
    with open(hold_store, 'w', encoding='utf-8') as f:
        for r in rows:
            if (r.get('subcard'), r.get('sense_tag')) not in held:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    full_tm = os.path.join(scratch, 'tm.full.ru.json')
    hold_tm = os.path.join(scratch, 'tm.holdout.ru.json')
    tm.build(a.store, 'ru', out=full_tm)
    tm.build(hold_store, 'ru', out=hold_tm)
    full_hits = hold_hits = 0; per = []
    for r in chosen:
        raw = (r.get('provenance') or {}).get('input_raw_sha256')
        fh = bool(tm.lookup('ru', raw, tm=full_tm)) if raw else False
        hh = bool(tm.lookup('ru', raw, tm=hold_tm)) if raw else False
        full_hits += fh; hold_hits += hh
        per.append({'key1': r.get('key1'), 'full_tm': 'hit' if fh else 'miss',
                    'holdout_tm': 'hit' if hh else 'miss'})
    # duplicate-address rate across the whole store = the real reuse ceiling
    addr = collections.Counter((r.get('provenance') or {}).get('input_raw_sha256') for r in rows)
    addr.pop(None, None)
    dup_addr = sum(1 for k, v in addr.items() if v > 1)
    rep['tm_holdout_replay'] = {
        'cards': len(chosen), 'full_tm_hits': full_hits, 'holdout_tm_hits': hold_hits,
        'per_card': per, 'scratch_dir': scratch,
        'store_distinct_input_addresses': len(addr),
        'store_rows_with_address': sum(addr.values()),
        'addresses_shared_by_2plus_rows': dup_addr,
        'denylist_addresses': len(tm.load_denylist()['addresses']),
    }

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k not in ('h4056_cards', 'store_keys')},
                     ensure_ascii=False, indent=1))
    print('cards:')
    for c in cards:
        print(json.dumps(c, ensure_ascii=False)[:900])
    print('wrote', a.out)


if __name__ == '__main__':
    main()
