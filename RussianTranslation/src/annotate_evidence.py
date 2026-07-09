#!/usr/bin/env python
"""annotate_evidence.py — retrofit per-sense evidence provenance onto the pwg_ru store.

For every store sense row it re-assembles corpus_gate's deterministic evidence lanes
for the row's `key1` (a pure offline join — H335 W2 verified the assembly is LLM-free
and reproducible from `key1` alone) and records, per sense:

  row['evidence']  list of {source, relation, gloss_ref, match} for the Russian-
                   glossing authorities — INDEP (koch/kna/fri/smirnov), REF (kow),
                   SPECIALIST (grin12/grin3) — that PROVIDE or SUPPORT this sense's
                   Russian gloss. Only token-comparable (Russian) lanes go here; a
                   source that supports no sense contributes nothing to that sense's
                   list (its lemma-level standing is in evidence_summary).

and, per lemma (D1 ruling 08-07-2026, DECISIONS_PIPELINE_CAPABILITY_H335.md: in-store,
no sidecar — so it is attached identically to every store row sharing that `key1`,
the flat store having no lemma object):

  row['evidence_summary']  {silent, contradicts, present, supports_senses,
                            evidence_status, corpus_status} — the lemma-level roll-up:
                            which sources are SILENT (absent, or carry no usable
                            Russian meaning gloss — e.g. Smirnov citation-lists,
                            Kossovich bare transliteration), which CONTRADICT (have a
                            usable Russian gloss that overlaps no sense of the lemma),
                            which non-Russian lanes are PRESENT as corroboration
                            (apte_hi/vedic_rituals_hi/kosha_syn/meulenbeld/corpus),
                            and which Russian sources supported >=1 sense.

Relation semantics (all deterministic; the supports/contradicts split IS a token-
overlap heuristic — labelled as such, per the W2 spec):
  provides     a source gloss states this sense's exact Russian equivalent
  supports     token containment with the sense's `ru` at/above corpus_gate.THRESHOLD
  contradicts  (lemma-level) source has a usable Russian gloss but overlaps no sense
  silent       (lemma-level) source absent, or its entry carries no usable Russian
               meaning tokens

The LLM-judged relation upgrade is exactly what the never-run 4_korpus gate would add;
it slots into the same field without a schema change.

`leonov` is a RESERVED source value (777-note Sundarakāṇḍa apparatus, org memory
project_sundara_commentary_apparatus) — NOT assembled here; reserved so the schema
enum is stable when that apparatus ships as a machine-usable glossary.

Deterministic, idempotent (a re-run overwrites only `evidence`/`evidence_summary`,
preserving renou/dcs_freq/etc.), BOM-free, in-place with a `.pre_evidence.bak` backup
unless --no-backup.

  python annotate_evidence.py [--store PATH] [--dry-run] [--no-backup] [--limit N]
  python annotate_evidence.py --selftest
"""
import argparse, json, os, re, sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_gate as cg
import koch_xref
import fri_xref

STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')

# H397: resolve koch's bare `см. X` cross-refs to their target's real gloss before
# best_relation/source_meaning_tokens run, so a resolvable redirect counts as
# provides/supports evidence instead of silence. --no-resolve-xref reproduces H337 exactly.
RESOLVE_KOCH_XREF = True
# H404: same idea for fri's bare v./cf./q.v. Latin-apparatus redirects (kna/smirnov/kow
# measured below H397's ~2% materiality bar — not touched). --no-resolve-xref disables both.
RESOLVE_FRI_XREF = True

# Russian-glossing, token-comparable authorities (relation = provides/supports/contradicts/silent).
RU_SOURCES = ['koch', 'kna', 'fri', 'smirnov', 'kow', 'grin12', 'grin3']
# Non-Russian corroboration lanes (presence-only: present/silent, never a correctness verdict).
NONRU_LANES = ['apte_hi', 'vedic_rituals_hi', 'kosha_syn', 'meulenbeld', 'corpus']
# Reserved, not built — see module docstring.
RESERVED_SOURCES = ['leonov']

# Mirrors corpus_gate.ru_tokens' stemming/content regex, WITHOUT the HEAD_SENSE_ONLY
# ';'-truncation: here we compare one already-split sense (or a source gloss that may
# itself list several senses), so the full text must be tokenised, not just sense 1.
_RU_END = cg._RU_END
_TAG_RE = re.compile(r'<[^>]+>')
_SANSKRIT_RE = re.compile(r'\{#.*?#\}')              # {#SLP1 citation#} — drop (not a meaning)
_MEANING_DELIM_RE = re.compile(r'\{%|%\}')           # {%…%} meaning delimiters — strip, KEEP the gloss inside
_PLACEHOLDER_RE = re.compile(r'\{T\d+\}')
_SENSE_NUM_RE = re.compile(r'^\s*\d+[\)\.]\s*')      # leading "6)" / "1." sense number


def ru_tokens_full(text):
    """Stemmed Russian content tokens over the WHOLE text (cf. corpus_gate.ru_tokens,
    which keeps only the head sense)."""
    if not text:
        return set()
    text = _PLACEHOLDER_RE.sub(' ', text)
    text = _TAG_RE.sub(' ', text)
    toks = re.findall(r'[а-яёА-ЯЁ]{2,}', text.lower())
    return {_RU_END.sub('', t) for t in toks if len(_RU_END.sub('', t)) >= 3}


def phrase_equivalents(text):
    """Normalised full-phrase equivalents of a Russian gloss/sense — for exact-equivalent
    (`provides`) detection. Strips markup, {#..#}/{%..%} spans, a leading sense number,
    then splits on ; , / and dashes; keeps phrases with a Cyrillic letter and length>=3."""
    if not text:
        return set()
    t = _TAG_RE.sub(' ', text)
    t = _SANSKRIT_RE.sub(' ', t)
    t = _MEANING_DELIM_RE.sub(' ', t)
    t = _PLACEHOLDER_RE.sub(' ', t)
    t = _SENSE_NUM_RE.sub(' ', t)
    out = set()
    for p in re.split(r'[;,/]|\s[—–-]\s', t):
        p = p.lower()
        m = re.search(r'[а-яё]', p)                     # drop a Devanagari/translit/POS/"1)" prefix:
        if not m:                                       # keep the Russian core of the equivalent only
            continue
        p = re.sub(r'\s+', ' ', p[m.start():]).strip().strip('.()[]{}·- ')
        if len(p) >= 3 and re.search(r'[а-яё]', p):
            out.add(p)
    return out


def gloss_ref(text, limit=160):
    """A readable snippet of the matched gloss for the evidence record."""
    t = _TAG_RE.sub(' ', text or '')
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:limit]


def source_meaning_tokens(glosses):
    """Union of usable Russian meaning tokens across a source's glosses. Empty ⇒ the
    source carries no usable meaning here (a citation-list / bare translit), so its
    silence is UNINFORMATIVE, never a `contradicts`."""
    toks = set()
    for g in glosses:
        toks |= ru_tokens_full(g)
    return toks


def best_relation(sense_ru, glosses):
    """(relation, gloss_ref) for one Russian source vs one sense's `ru`:
    'provides' (exact equivalent), 'supports' (containment >= THRESHOLD), or (None,'')."""
    a_tok = ru_tokens_full(sense_ru)
    if not a_tok:
        return None, ''                     # a pure cross-ref / citation sense asserts no meaning
    a_phr = phrase_equivalents(sense_ru)
    best_ov, best_g = 0.0, ''
    for g in glosses:
        if a_phr and (a_phr & phrase_equivalents(g)):
            return 'provides', gloss_ref(g)
        b = ru_tokens_full(g)
        if not b:
            continue
        ov = len(a_tok & b) / len(a_tok)
        if ov > best_ov:
            best_ov, best_g = ov, g
    if best_ov >= cg.THRESHOLD:
        return 'supports', gloss_ref(best_g)
    return None, ''


# ---- lane assembly (needs the gate source jsonls; NOT exercised by --selftest) --------
def gather(idx, key1):
    """Assemble the evidence lanes for one lemma. RU lanes -> {code: [glosses]};
    non-RU lanes -> {code: {present, match}}."""
    indep, kow = cg.lookup(idx, key1, None)
    ru = defaultdict(list)
    for g in indep:
        ru[g['code']].append(g['gloss'])
    for g in kow:
        ru['kow'].append(g)
    for g in cg.lookup_specialist(key1, None):
        ru[g['code']].append(g['gloss'])

    if RESOLVE_KOCH_XREF and ru.get('koch'):
        ru['koch'], _n_resolved = koch_xref.resolve_koch_lane(ru['koch'])
    if RESOLVE_FRI_XREF and ru.get('fri'):
        ru['fri'], _n_resolved = fri_xref.resolve_fri_lane(ru['fri'])

    sense_codes = {s['code'] for s in cg.lookup_sense(key1, None)}
    nonru = {
        'apte_hi': {'present': 'apte_hi' in sense_codes, 'match': 'stem'},
        'vedic_rituals_hi': {'present': 'vedic_rituals_hi' in sense_codes, 'match': 'stem'},
        'kosha_syn': {'present': bool(cg.lookup_synonyms(key1, None)), 'match': 'lemma'},
        'meulenbeld': {'present': bool(cg.lookup_binomials(key1, None)), 'match': 'stem'},
    }
    ex, cstat = cg.corpus_examples_with_status(key1)
    nonru['corpus'] = {'present': bool(ex), 'match': 'lemma'}
    return {'ru': ru, 'nonru': nonru, 'evidence_status': cg.evidence_status(), 'corpus_status': cstat}


def annotate_rows(rows, idx, tally):
    """Mutate store rows in place, adding `evidence` (per sense) and `evidence_summary`
    (per lemma). `tally` accumulates per-source relation counts for the report."""
    by_key = defaultdict(list)
    for i, r in enumerate(rows):
        by_key[r.get('key1') or ''].append(i)

    stats = Counter()
    for key1, idxs in sorted(by_key.items()):
        if not key1:
            for i in idxs:
                rows[i]['evidence'] = []
                rows[i]['evidence_summary'] = {'silent': [], 'contradicts': [], 'present': [],
                                               'supports_senses': [], 'evidence_status': 'no_key1',
                                               'corpus_status': 'skipped_short_term'}
                stats['rows'] += 1
            continue

        lanes = gather(idx, key1)
        ru_supported = set()
        for i in idxs:
            r = rows[i]
            ev = []
            for code in RU_SOURCES:
                glosses = lanes['ru'].get(code) or []
                if not glosses:
                    continue
                rel, ref = best_relation(r.get('ru') or '', glosses)
                if rel:
                    ev.append({'source': code, 'relation': rel, 'gloss_ref': ref, 'match': 'lemma'})
                    ru_supported.add(code)
                    tally[code][rel] += 1
            r['evidence'] = ev
            stats['rows'] += 1
            if ev:
                stats['rows_with_evidence'] += 1

        silent, contradicts, present = [], [], []
        for code in RU_SOURCES:
            glosses = lanes['ru'].get(code) or []
            if not glosses or not source_meaning_tokens(glosses):
                silent.append(code)
            elif code in ru_supported:
                pass                                 # positive standing recorded per sense
            else:
                contradicts.append(code)
        for code in NONRU_LANES:
            info = lanes['nonru'][code]
            (present.append({'source': code, 'match': info['match']}) if info['present']
             else silent.append(code))

        summary = {'silent': silent, 'contradicts': contradicts, 'present': present,
                   'supports_senses': sorted(ru_supported),
                   'evidence_status': lanes['evidence_status'], 'corpus_status': lanes['corpus_status']}
        for i in idxs:
            rows[i]['evidence_summary'] = summary

        stats['lemmas'] += 1
        for c in contradicts:
            tally[c]['contradicts'] += 1
        for c in silent:
            tally[c]['silent'] += 1
        for p in present:
            tally[p['source']]['present'] += 1
    return stats


def report(stats, tally):
    print('=== EVIDENCE ANNOTATION ===')
    print('store rows            : %d' % stats['rows'])
    print('lemmas (distinct key1): %d' % stats['lemmas'])
    print('rows with >=1 evidence: %d (%.1f%%)'
          % (stats['rows_with_evidence'], 100.0 * stats['rows_with_evidence'] / max(1, stats['rows'])))
    print('\nper-source tallies (provides/supports = sense-level; contradicts/silent/present = lemma-level):')
    print('  %-18s %8s %8s %11s %8s %8s' % ('source', 'provides', 'supports', 'contradicts', 'silent', 'present'))
    for code in RU_SOURCES + NONRU_LANES:
        t = tally.get(code, {})
        print('  %-18s %8d %8d %11d %8d %8d'
              % (code, t.get('provides', 0), t.get('supports', 0),
                 t.get('contradicts', 0), t.get('silent', 0), t.get('present', 0)))


# ---- selftest (pure functions only — no gate-source file IO, so it runs in CI) --------
def selftest():
    # provides: exact equivalent phrase intersection
    rel, ref = best_relation('огонь', ['अग्नि /agni/ m. 1) огонь, пламя; бог огня'])
    assert rel == 'provides', ('provides expected', rel, ref)
    # supports: token containment >= THRESHOLD but no exact-phrase equivalent
    rel, _ = best_relation('лотос дневной', ['padma m. n. лотос (водяной)'])
    assert rel == 'supports', ('supports expected', rel)
    # no relation: disjoint meaning
    rel, _ = best_relation('огонь', ['время, срок, эпоха'])
    assert rel is None, ('no relation expected', rel)
    # a pure citation/cross-ref sense (no Russian meaning tokens) never yields evidence
    rel, _ = best_relation('<ls>M. 2,109.</ls> {#mAturAptAMSca#}', ['огонь, пламя'])
    assert rel is None, ('citation-only sense must not match', rel)
    # source with no usable meaning tokens (Smirnov citation-list) -> uninformative, not contradicts
    assert source_meaning_tokens(['(II-2) IV, 19, 24, 25; VIII,']) == set(), 'citation-list must have no meaning tokens'
    assert source_meaning_tokens(['огонь, бог огня']), 'a real gloss must have meaning tokens'
    # phrase_equivalents strips a leading sense number and markup
    assert 'близкий' in phrase_equivalents('6) {%близкий, родственный%}; <lex>m.</lex>')
    # gloss_ref collapses markup/whitespace and truncates
    assert '<' not in gloss_ref('<ls>M.</ls>  огонь\n  пламя')
    # idempotency of the per-lemma summary shape: build a fake two-sense lemma without file IO
    _lanes = {'ru': {'koch': ['agni m. огонь'], 'smirnov': ['(II-2) IV, 19']},
              'nonru': {'apte_hi': {'present': True, 'match': 'stem'},
                        'vedic_rituals_hi': {'present': False, 'match': 'stem'},
                        'kosha_syn': {'present': True, 'match': 'lemma'},
                        'meulenbeld': {'present': False, 'match': 'stem'},
                        'corpus': {'present': True, 'match': 'lemma'}},
              'evidence_status': 'ok', 'corpus_status': 'ok'}
    rows = [{'key1': 'agni', 'ru': 'огонь'}, {'key1': 'agni', 'ru': 'молния, вспышка'}]
    tally = defaultdict(Counter)

    def _fake_gather(_idx, _k):
        return _lanes
    global gather
    real_gather, gather = gather, _fake_gather
    try:
        st = annotate_rows(rows, None, tally)
    finally:
        gather = real_gather
    assert rows[0]['evidence'] and rows[0]['evidence'][0]['source'] == 'koch', 'koch must support огонь'
    assert rows[1]['evidence'] == [], 'молния has no supporting gloss here'
    summ = rows[0]['evidence_summary']
    assert 'koch' in summ['supports_senses'], summ
    assert 'smirnov' in summ['silent'], ('smirnov citation-list is silent, not contradicts', summ)
    assert {'source': 'kosha_syn', 'match': 'lemma'} in summ['present'], summ
    assert 'vedic_rituals_hi' in summ['silent'] and 'meulenbeld' in summ['silent'], summ
    assert rows[0]['evidence_summary'] is rows[1]['evidence_summary'], 'summary is lemma-scoped'
    print('annotate_evidence selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--limit', type=int, default=None, help='annotate only the first N rows (smoke test)')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--no-resolve-xref', dest='resolve_xref', action='store_false', default=True,
                     help='disable H397/H404 koch+fri xref resolution (reproduces H337 exactly)')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    global RESOLVE_KOCH_XREF, RESOLVE_FRI_XREF
    RESOLVE_KOCH_XREF = args.resolve_xref
    RESOLVE_FRI_XREF = args.resolve_xref

    idx = cg.load_index()
    if cg.evidence_status() != 'ok':
        sys.stderr.write('REFUSING: no independent Sanskrit-Russian authority (INDEP) loaded — '
                         'gate sources not built; every lane would read "silent" falsely. '
                         'Build src/*.jsonl (build_src.py) first.\n')
        raise SystemExit(2)

    rows = []
    with open(args.store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if args.limit:
        rows = rows[:args.limit]

    tally = defaultdict(Counter)
    stats = annotate_rows(rows, idx, tally)
    report(stats, tally)

    if args.dry_run:
        print('\n(dry run — store not written)')
        return
    if not args.no_backup and args.limit is None:
        os.replace(args.store, args.store + '.pre_evidence.bak')
    with open(args.store, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('\nwrote annotated store -> %s' % args.store)


if __name__ == '__main__':
    main()
