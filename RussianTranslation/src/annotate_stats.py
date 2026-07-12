#!/usr/bin/env python
"""annotate_stats.py — cache per-card derived counts onto the pwg_ru store (H422, H777).

GRAMMAR_LAYER.md § "Counting grammar" design (merged, PR #284): nothing on a card
records "N senses, M government markers, governs {loc, gen}, spans Renou I-IV" —
government_census.py / government_queries.py re-scan/re-aggregate the whole store
on every question. This is the backfill that fixes that, run **last** in the
annotator chain (after annotate_government.py / annotate_renou.py /
annotate_evidence.py) — it reads only fields already on the store row, no new
source parsing.

Three granularities are attached (H777 — MG ruling 12-07-2026, all count families,
finest grain):

  row['sense_stats']   per-row (one sense) — markup density + this sense's own
                       government/QA fields + dcs_freq for this sense's exact form
  row['record_stats']  per homonym group (key1 + subcard ~~h<N>_) — aggregate of
                       its senses; replicated across the record's rows
  row['stats']         per lemma (key1) — the full rollup; replicated across every
                       row sharing that key1 (the flat store has no lemma object to
                       hang a lemma-level block off of, the same convention
                       evidence_summary already uses)

Count families on the lemma block (H777 accepted menu):
  structural   n_records, n_senses
  government   n_government, cases_governed, has_variation          (annotate_government.py)
  chronology   strata_span, n_strata                                (stratum free-text)
  evidence     evidence{provides,supports,contradicts,silent}
  layer/merge  n_layers, layers_present, n_senses_supplement        (5-layer merge: pwg/pw/sch/pwkvn/nws)
  markup       n_ls, n_lex, n_ab, n_xref, n_labels                  (inline <ls>/<lex>/<ab>/vgl. in `de`)
  translation  equivalence_types, source_types, review_statuses, n_differentia, n_null
  frequency    dcs_freq_max {iast, count, band}                     (DCS corpus attestation, exact-iast join)
  grammar      grammar_join, n_whitney_homonyms, n_irregularities, root_class, stem_final
                                                                    (whitney_grammar.py — single-homonym only)

Self-invalidation: `stats.pipeline_version` is the manifest `script` component
version (pipeline_version.py) at compute time. A stats block whose stamped
version is older than the current script version is stale -> recompute;
otherwise trust it without a rescan (mirrors `evidence_summary.evidence_status`).
Bump the `script` component when this file's output shape changes so every lemma
recomputes (H777 bumped script 1.0.0 -> 1.1.0 for the expanded block).

Correct-by-construction joins (never a fuzzy guess — the Renou-classifier lesson):
  * dcs_freq  — EXACT match of a form's `iast` against dcs_freq.json by_lemma, else
                null. Prefixed forms (`nis+vā`) that DCS does not lemmatise stay null
                rather than being force-matched to a different simple lemma.
  * grammar   — whitney_grammar.grammar_for(key1) is joined ONLY when the root has
                exactly ONE Whitney homonym record. Multi-homonym roots need the
                hand PWG-h <-> Whitney-homonym alignment (flagged in GRAMMAR_LAYER.md,
                not guessed here): grammar_join='ambiguous-homonym', counts left null.

  python annotate_stats.py [--store PATH] [--dry-run] [--no-backup] [--limit N]
  python annotate_stats.py --selftest
"""
import argparse, json, os, re, sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pipeline_version as pv

STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DCS_FREQ = os.path.join(HERE, 'dcs_freq.json')

_SUBCARD_H_RE = re.compile(r'~~h(\d+)_')

# Markup-density counters over a sense's `de` (German — the canonical layer text, the
# same field government/dcs key off). Cross-reference marker: `vgl.` (vergleiche) only —
# a deterministic floor; `s.`/`siehe` are omitted deliberately (too ambiguous to count
# without false positives — the same discipline government_census.py applies).
_TAG_LS = re.compile(r'<ls\b')
_TAG_LEX = re.compile(r'<lex>')
_TAG_AB = re.compile(r'<ab>')
_XREF = re.compile(r'\bvgl\.')

# The 5-layer merge chain (pwg_ru_prompts/6_merged_translate.md). PWG is the
# grammatical backbone; the other four are supplements folded in with attribution.
BACKBONE_LAYER = 'pwg'

# Canonical Renou-style era vocabulary, oldest -> youngest. `stratum` is a free-text
# field (not the structured `renou[]` enum) — a row's stratum string is scanned for
# these substrings; unrecognised text (e.g. "general") contributes nothing rather
# than being guessed at.
STRATA_ORDER = ['Vedic', 'Brāhmaṇa', 'Epic', 'Classical', 'Buddhist', 'Medieval']


def strata_in(text):
    """Canonical era labels found in a free-text `stratum` string, in STRATA_ORDER."""
    if not text:
        return []
    return [s for s in STRATA_ORDER if s in text]


def homonym_of(row, idx=0):
    """The homonym-group token for a row, from `subcard`'s `~~h<N>_`. A row with no
    parseable subcard is its own group (via a per-row fallback), so it never silently
    merges into h0."""
    m = _SUBCARD_H_RE.search(row.get('subcard') or '')
    return m.group(1) if m else ('_row%d' % idx)


def n_records_for(rows):
    """Distinct homonym groups for a lemma."""
    return len({homonym_of(r, i) for i, r in enumerate(rows)})


# --- dcs_freq join (exact-iast, lazy, tolerant of a missing gitignored file) --------
_DCS_CACHE = None


def _dcs_by_lemma(path=DCS_FREQ):
    """Load dcs_freq.json's by_lemma once. dcs_freq.json is gitignored bulk data —
    absent in a fresh worktree — so a missing file yields an empty map (no join, no
    crash), logged once."""
    global _DCS_CACHE
    if _DCS_CACHE is None:
        if os.path.exists(path):
            _DCS_CACHE = json.load(open(path, encoding='utf-8')).get('by_lemma', {})
        else:
            print('annotate_stats: %s absent — dcs_freq join skipped (fields left null)'
                  % os.path.basename(path), file=sys.stderr)
            _DCS_CACHE = {}
    return _DCS_CACHE


def dcs_lookup(iast, by_lemma=None):
    """Exact-match dcs frequency for one form's IAST, else None. Never a fuzzy join."""
    if not iast:
        return None
    d = (by_lemma if by_lemma is not None else _dcs_by_lemma()).get(iast)
    if not d:
        return None
    return {'count': d.get('count'), 'band': d.get('band'),
            'hapax': d.get('hapax'), 'core80': d.get('core80')}


# --- grammar join (whitney_grammar, single-homonym only) ----------------------------
_GRAMMAR_FN = None


def _grammar_for():
    """Lazily import whitney_grammar.grammar_for; tolerate its absence (returns a
    stub that yields []) so the annotator still runs where the module/data is missing."""
    global _GRAMMAR_FN
    if _GRAMMAR_FN is None:
        try:
            from whitney_grammar import grammar_for
            _GRAMMAR_FN = grammar_for
        except Exception as e:               # pragma: no cover - defensive
            print('annotate_stats: whitney_grammar unavailable (%s) — grammar join skipped' % e,
                  file=sys.stderr)
            _GRAMMAR_FN = lambda slp1, homonym=None: []
    return _GRAMMAR_FN


def grammar_join(key1, grammar_for=None):
    """Join whitney_grammar for one lemma's SLP1 key. Single Whitney homonym -> full
    join; multiple -> flagged ambiguous, counts null (hand alignment owed, not guessed);
    none -> not a Whitney root (nominal/other). Returns a dict merged into the lemma block."""
    gf = grammar_for or _grammar_for()
    recs = gf(key1) or []
    stem_final = key1[-1] if key1 else None
    if len(recs) == 1:
        r = recs[0]
        return {'grammar_join': 'single', 'n_whitney_homonyms': 1,
                'n_irregularities': len(r.get('irregularities') or []),
                'root_class': r.get('class') or None, 'stem_final': stem_final}
    if len(recs) > 1:
        return {'grammar_join': 'ambiguous-homonym', 'n_whitney_homonyms': len(recs),
                'n_irregularities': None, 'root_class': None, 'stem_final': stem_final}
    return {'grammar_join': 'none', 'n_whitney_homonyms': 0,
            'n_irregularities': None, 'root_class': None, 'stem_final': stem_final}


# --- per-sense (row) block ----------------------------------------------------------
def sense_stats(row, by_lemma=None):
    """Derived counts for ONE sense (row) — markup density + this sense's own
    government / QA fields + dcs_freq for this sense's exact form."""
    de = row.get('de') or ''
    gov = row.get('government') or []
    cases = sorted({c for h in gov for c in (h.get('cases') or [])})
    return {
        'n_ls': len(_TAG_LS.findall(de)),
        'n_lex': len(_TAG_LEX.findall(de)),
        'n_ab': len(_TAG_AB.findall(de)),
        'n_xref': len(_XREF.findall(de)),
        'n_labels': len(row.get('labels') or []),
        'n_government': len(gov),
        'cases': cases,
        'has_differentia': bool((row.get('differentia') or '').strip()),
        'is_null': not (row.get('ru') or '').strip(),
        'layer': row.get('layer'),
        'equivalence_type': row.get('equivalence_type'),
        'source_type': row.get('source_type'),
        'dcs_freq': dcs_lookup(row.get('iast'), by_lemma),
    }


def _aggregate_senses(senses):
    """Shared roll-up used by both record and lemma blocks. `senses` are dicts from
    sense_stats() carrying two extra private keys: `review_status`, `_iast`."""
    agg = {
        'n_senses': len(senses),
        'n_government': sum(1 for s in senses if s['n_government']),
        'cases_governed': sorted({c for s in senses for c in s['cases']}),
        'n_ls': sum(s['n_ls'] for s in senses),
        'n_lex': sum(s['n_lex'] for s in senses),
        'n_ab': sum(s['n_ab'] for s in senses),
        'n_xref': sum(s['n_xref'] for s in senses),
        'n_labels': sum(s['n_labels'] for s in senses),
        'n_differentia': sum(1 for s in senses if s['has_differentia']),
        'n_null': sum(1 for s in senses if s['is_null']),
        'layers_present': sorted({s['layer'] for s in senses if s['layer']}),
        'n_senses_supplement': sum(1 for s in senses
                                   if s['layer'] and s['layer'] != BACKBONE_LAYER),
        'equivalence_types': dict(Counter(s['equivalence_type'] for s in senses
                                          if s['equivalence_type'])),
        'source_types': dict(Counter(s['source_type'] for s in senses if s['source_type'])),
        'review_statuses': dict(Counter(s.get('review_status') for s in senses
                                        if s.get('review_status'))),
    }
    agg['n_layers'] = len(agg['layers_present'])
    # most-attested form for the group (max dcs count over matched senses)
    freqs = [(s['dcs_freq']['count'], s) for s in senses
             if s['dcs_freq'] and s['dcs_freq'].get('count') is not None]
    if freqs:
        cnt, s = max(freqs, key=lambda x: x[0])
        agg['dcs_freq_max'] = {'iast': s.get('_iast'), 'count': cnt,
                               'band': s['dcs_freq'].get('band')}
    else:
        agg['dcs_freq_max'] = None
    return agg


def _senses_of(rows, by_lemma):
    senses = []
    for r in rows:
        s = sense_stats(r, by_lemma)
        s['review_status'] = r.get('review_status')
        s['_iast'] = r.get('iast')
        senses.append(s)
    return senses


def record_stats(rows, by_lemma=None):
    """Per-homonym-record aggregate. `rows` are the raw store rows of ONE record."""
    return _aggregate_senses(_senses_of(rows, by_lemma))


def compute_stats(rows, script_version, key1=None, by_lemma=None, grammar_for=None):
    """Derive the `stats` block for one lemma's (key1-grouped) rows."""
    has_variation = any(h.get('variation') for r in rows for h in (r.get('government') or []))

    agg = _aggregate_senses(_senses_of(rows, by_lemma))

    strata = set()
    for r in rows:
        strata.update(strata_in(r.get('stratum')))
    strata_span = []
    if strata:
        ordered = [s for s in STRATA_ORDER if s in strata]
        strata_span = [ordered[0], ordered[-1]]

    n_provides = n_supports = 0
    for r in rows:
        for ev in (r.get('evidence') or []):
            if ev.get('relation') == 'provides':
                n_provides += 1
            elif ev.get('relation') == 'supports':
                n_supports += 1
    summary = next((r.get('evidence_summary') for r in rows if r.get('evidence_summary')), None)
    n_contradicts = len(summary.get('contradicts', [])) if summary else 0
    n_silent = len(summary.get('silent', [])) if summary else 0

    gj = grammar_join(key1 or (rows[0].get('key1') if rows else ''), grammar_for)

    return {
        'n_records': n_records_for(rows),
        'n_senses': len(rows),
        'n_government': agg['n_government'],
        'cases_governed': agg['cases_governed'],
        'has_variation': has_variation,
        # layer / 5-merge provenance
        'n_layers': agg['n_layers'],
        'layers_present': agg['layers_present'],
        'n_senses_supplement': agg['n_senses_supplement'],
        # markup density
        'n_ls': agg['n_ls'], 'n_lex': agg['n_lex'], 'n_ab': agg['n_ab'],
        'n_xref': agg['n_xref'], 'n_labels': agg['n_labels'],
        # translation / QA
        'equivalence_types': agg['equivalence_types'],
        'source_types': agg['source_types'],
        'review_statuses': agg['review_statuses'],
        'n_differentia': agg['n_differentia'],
        'n_null': agg['n_null'],
        # frequency
        'dcs_freq_max': agg['dcs_freq_max'],
        # grammar (whitney_grammar join)
        'grammar_join': gj['grammar_join'],
        'n_whitney_homonyms': gj['n_whitney_homonyms'],
        'n_irregularities': gj['n_irregularities'],
        'root_class': gj['root_class'],
        'stem_final': gj['stem_final'],
        # chronology
        'strata_span': strata_span,
        'n_strata': len(strata),
        # evidence
        'evidence': {'provides': n_provides, 'supports': n_supports,
                     'contradicts': n_contradicts, 'silent': n_silent},
        'computed_by': 'annotate_stats.py',
        'pipeline_version': script_version,
    }


def is_stale(stats, current_version):
    """True when a cached stats block should be recomputed: missing, or stamped
    below the current script version."""
    if not stats:
        return True
    return pv.semver_lt(stats.get('pipeline_version'), current_version)


def annotate_rows(rows, script_version, force=False, by_lemma=None, grammar_for=None):
    """Mutate store rows in place, attaching `sense_stats` (per row), `record_stats`
    (per homonym group) and `stats` (per lemma). Returns a Counter of corpus-level
    rollup totals."""
    if by_lemma is None:
        by_lemma = _dcs_by_lemma()

    by_key = defaultdict(list)
    for i, r in enumerate(rows):
        by_key[r.get('key1') or ''].append(i)

    totals = Counter()
    lemmas_recomputed = lemmas_cached = 0
    for key1, idxs in sorted(by_key.items()):
        group = [rows[i] for i in idxs]
        existing = group[0].get('stats')
        if not force and not is_stale(existing, script_version):
            stats = existing
            lemmas_cached += 1
            recompute = False
        else:
            stats = compute_stats(group, script_version, key1=key1,
                                  by_lemma=by_lemma, grammar_for=grammar_for)
            lemmas_recomputed += 1
            recompute = True
        for i in idxs:
            rows[i]['stats'] = stats

        # per-sense / per-record blocks follow the lemma block's freshness — recompute
        # them exactly when the lemma block is recomputed, skip when the lemma is cached.
        if recompute:
            by_h = defaultdict(list)
            for i in idxs:
                by_h[homonym_of(rows[i], i)].append(i)
            for hidxs in by_h.values():
                rec = record_stats([rows[i] for i in hidxs], by_lemma)
                for i in hidxs:
                    rows[i]['record_stats'] = rec
            for i in idxs:
                rows[i]['sense_stats'] = sense_stats(rows[i], by_lemma)

        totals['lemmas'] += 1
        totals['records'] += stats['n_records']
        totals['senses'] += stats['n_senses']
        totals['government_markers'] += stats['n_government']
        if stats['has_variation']:
            totals['lemmas_with_variation'] += 1
        if stats.get('grammar_join') == 'single':
            totals['lemmas_grammar_joined'] += 1
            totals['irregularities'] += stats.get('n_irregularities') or 0
        elif stats.get('grammar_join') == 'ambiguous-homonym':
            totals['lemmas_grammar_ambiguous'] += 1
        if stats.get('dcs_freq_max'):
            totals['lemmas_dcs_matched'] += 1
        totals['ls_citations'] += stats['n_ls']
        totals['evidence_provides'] += stats['evidence']['provides']
        totals['evidence_supports'] += stats['evidence']['supports']

    totals['lemmas_recomputed'] = lemmas_recomputed
    totals['lemmas_cached'] = lemmas_cached
    totals['rows'] = len(rows)
    return totals


def report(totals):
    print('=== STATS ANNOTATION ===')
    print('store rows             : %d' % totals['rows'])
    print('lemmas (distinct key1) : %d  (recomputed: %d, cached/fresh: %d)'
          % (totals['lemmas'], totals['lemmas_recomputed'], totals['lemmas_cached']))
    print('total records (homonym groups): %d' % totals['records'])
    print('total senses            : %d' % totals['senses'])
    print('government markers      : %d  (lemmas with case variation: %d)'
          % (totals['government_markers'], totals['lemmas_with_variation']))
    print('grammar-joined lemmas   : %d single (%d irregularities), %d ambiguous-homonym'
          % (totals['lemmas_grammar_joined'], totals['irregularities'],
             totals['lemmas_grammar_ambiguous']))
    print('dcs-matched lemmas      : %d' % totals['lemmas_dcs_matched'])
    print('<ls> citations (total)  : %d' % totals['ls_citations'])
    print('evidence: provides=%d supports=%d'
          % (totals['evidence_provides'], totals['evidence_supports']))


def write_rollup(totals, script_version, model_version, path):
    """Append the corpus-level rollup to RESULTS_LOG.md (persist-tables reflex) —
    a committed snapshot, not a live re-scan target."""
    import datetime
    date = datetime.date.today().strftime('%d-%m-%Y')
    header_needed = not os.path.exists(path)
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        if header_needed:
            f.write('# RussianTranslation — results log\n\n')
            f.write('_Created: %s · Last updated: %s_\n\n' % (date, date))
            f.write('Append-only, reverse-chronological. Each entry: date, context, '
                    'model tier, table.\n\n')
        f.write('## %s — pwg_ru card stats rollup (annotate_stats.py)\n\n' % date)
        f.write('Script v%s · %s\n\n' % (script_version, model_version))
        f.write('| metric | value |\n|---|---|\n')
        f.write('| lemmas | %d |\n' % totals['lemmas'])
        f.write('| records (homonym groups) | %d |\n' % totals['records'])
        f.write('| senses | %d |\n' % totals['senses'])
        f.write('| government markers | %d |\n' % totals['government_markers'])
        f.write('| lemmas with case variation | %d |\n' % totals['lemmas_with_variation'])
        f.write('| grammar-joined lemmas (single homonym) | %d |\n' % totals['lemmas_grammar_joined'])
        f.write('| … whitney irregularities counted | %d |\n' % totals['irregularities'])
        f.write('| grammar ambiguous-homonym (alignment owed) | %d |\n' % totals['lemmas_grammar_ambiguous'])
        f.write('| dcs-matched lemmas | %d |\n' % totals['lemmas_dcs_matched'])
        f.write('| <ls> citations (total) | %d |\n' % totals['ls_citations'])
        f.write('| evidence: provides | %d |\n' % totals['evidence_provides'])
        f.write('| evidence: supports | %d |\n' % totals['evidence_supports'])
        f.write('\n')


# ---- selftest (pure functions only — no store file IO, so it runs in CI) --------
def selftest():
    assert strata_in('Vedic, Epic / early-Classical, Classical') == ['Vedic', 'Epic', 'Classical']
    assert strata_in('general') == []
    assert strata_in('') == [] and strata_in(None) == []

    # dcs join is exact-or-null, never fuzzy
    fake_dcs = {'agni': {'count': 900, 'band': 4, 'hapax': False, 'core80': True}}
    assert dcs_lookup('agni', fake_dcs) == {'count': 900, 'band': 4, 'hapax': False, 'core80': True}
    assert dcs_lookup('nis+vā', fake_dcs) is None      # prefixed form not force-matched
    assert dcs_lookup('', fake_dcs) is None and dcs_lookup(None, fake_dcs) is None

    # grammar join: single -> counts; multi -> ambiguous, null; none -> not a root
    def fake_grammar(slp1, homonym=None):
        table = {
            'gam': [{'class': 'I|II', 'irregularities': ['multi_class', 'root_final_nasal_loss(gam→gatá)']}],
            'as': [{'class': 'II', 'irregularities': []}, {'class': 'IV', 'irregularities': []}],
        }
        return table.get(slp1, [])
    gj = grammar_join('gam', fake_grammar)
    assert gj == {'grammar_join': 'single', 'n_whitney_homonyms': 1, 'n_irregularities': 2,
                  'root_class': 'I|II', 'stem_final': 'm'}, gj
    gj2 = grammar_join('as', fake_grammar)
    assert gj2['grammar_join'] == 'ambiguous-homonym' and gj2['n_irregularities'] is None, gj2
    gj3 = grammar_join('deva', fake_grammar)
    assert gj3 == {'grammar_join': 'none', 'n_whitney_homonyms': 0, 'n_irregularities': None,
                   'root_class': None, 'stem_final': 'a'}, gj3

    rows = [
        {'key1': 'gam', 'subcard': '_gam~~h0_00_pwg01', 'sense_tag': '1', 'layer': 'pwg',
         'iast': 'gam', 'stratum': 'Vedic', 'government': [], 'differentia': 'x',
         'equivalence_type': 'equivalent', 'source_type': 'attested', 'review_status': 'ai_translated',
         'ru': 'идти', 'de': '{%gehen%} <ls>RV. 1,1</ls> <ls>MBH.</ls> vgl. {#i#}.',
         'evidence': [{'relation': 'provides'}],
         'evidence_summary': {'silent': ['smirnov'], 'contradicts': []}},
        {'key1': 'gam', 'subcard': '_gam~~h0_01_pw01', 'sense_tag': '2', 'layer': 'pw',
         'iast': 'gam', 'stratum': 'Classical',
         'government': [{'cases': ['loc', 'gen'], 'variation': True}],
         'equivalence_type': 'explanatory', 'source_type': 'attested', 'review_status': 'ai_translated',
         'ru': '', 'de': '{%treffen%} (<ab>loc.</ab> und <ab>gen.</ab>) <ls>ŚĀK.</ls> <lex>m.</lex>',
         'evidence': [{'relation': 'supports'}],
         'evidence_summary': {'silent': ['smirnov'], 'contradicts': []}},
        {'key1': 'gam', 'subcard': '_gam~~h1_00_nws01', 'sense_tag': '1', 'layer': 'nws',
         'iast': 'saMgam', 'stratum': '', 'government': [],
         'equivalence_type': 'equivalent', 'source_type': 'mixed', 'review_status': 'ai_translated',
         'ru': 'сходиться', 'de': '{%zusammenkommen%}', 'evidence': [], 'evidence_summary': None},
    ]
    dcs = {'gam': {'count': 5000, 'band': 5, 'hapax': False, 'core80': True}}
    rows_copy = [dict(r) for r in rows]
    totals = annotate_rows(rows_copy, '1.1.0', by_lemma=dcs, grammar_for=fake_grammar)
    assert totals['lemmas'] == 1, totals
    assert totals['lemmas_recomputed'] == 1 and totals['lemmas_cached'] == 0, totals

    st = rows_copy[0]['stats']
    assert rows_copy[0]['stats'] is rows_copy[2]['stats'], 'stats is lemma-scoped'
    assert st['n_records'] == 2 and st['n_senses'] == 3, st          # h0, h1
    assert st['n_government'] == 1 and st['cases_governed'] == ['gen', 'loc'], st
    assert st['has_variation'] is True, st
    # layer / merge
    assert st['n_layers'] == 3 and st['layers_present'] == ['nws', 'pw', 'pwg'], st
    assert st['n_senses_supplement'] == 2, st                        # pw + nws (non-pwg)
    # markup density (summed over senses)
    assert st['n_ls'] == 3 and st['n_lex'] == 1 and st['n_ab'] == 2 and st['n_xref'] == 1, st
    # QA
    assert st['equivalence_types'] == {'equivalent': 2, 'explanatory': 1}, st
    assert st['source_types'] == {'attested': 2, 'mixed': 1}, st
    assert st['n_differentia'] == 1 and st['n_null'] == 1, st
    # frequency (exact iast join; 'saMgam' unmatched)
    assert st['dcs_freq_max'] == {'iast': 'gam', 'count': 5000, 'band': 5}, st
    # grammar join
    assert st['grammar_join'] == 'single' and st['n_irregularities'] == 2, st
    assert st['root_class'] == 'I|II' and st['stem_final'] == 'm', st
    # chronology + evidence
    assert st['strata_span'] == ['Vedic', 'Classical'] and st['n_strata'] == 2, st
    assert st['evidence'] == {'provides': 1, 'supports': 1, 'contradicts': 0, 'silent': 1}, st

    # per-sense block
    ss0 = rows_copy[0]['sense_stats']
    assert ss0['n_ls'] == 2 and ss0['n_xref'] == 1 and ss0['is_null'] is False, ss0
    ss1 = rows_copy[1]['sense_stats']
    assert ss1['n_ab'] == 2 and ss1['is_null'] is True and ss1['cases'] == ['gen', 'loc'], ss1
    # per-record block: h0 = senses 0+1, h1 = sense 2
    rec0 = rows_copy[0]['record_stats']
    assert rows_copy[0]['record_stats'] is rows_copy[1]['record_stats'], 'record-scoped'
    assert rec0['n_senses'] == 2 and rec0['n_null'] == 1, rec0
    rec1 = rows_copy[2]['record_stats']
    assert rec1['n_senses'] == 1 and rec1['dcs_freq_max'] is None, rec1  # saMgam unmatched

    # self-invalidation
    assert is_stale(None, '1.1.0') is True
    assert is_stale({'pipeline_version': '1.0.0'}, '1.1.0') is True
    assert is_stale({'pipeline_version': '1.1.0'}, '1.1.0') is False

    rows_copy2 = [dict(r) for r in rows]
    annotate_rows(rows_copy2, '1.1.0', by_lemma=dcs, grammar_for=fake_grammar)
    totals2 = annotate_rows(rows_copy2, '1.1.0', by_lemma=dcs, grammar_for=fake_grammar)
    assert totals2['lemmas_recomputed'] == 0 and totals2['lemmas_cached'] == 1, totals2
    totals3 = annotate_rows(rows_copy2, '2.0.0', by_lemma=dcs, grammar_for=fake_grammar)
    assert totals3['lemmas_recomputed'] == 1, totals3

    print('annotate_stats selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--limit', type=int, default=None, help='annotate only the first N rows (smoke test)')
    ap.add_argument('--force', action='store_true', help='recompute every lemma, ignoring cached stats')
    ap.add_argument('--rollup', default=None,
                     help='append the corpus-level rollup to this RESULTS_LOG.md path')
    ap.add_argument('--model-version', default='n/a',
                     help='model tier+version stamp for the --rollup entry')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    manifest = pv.load_manifest()
    script_version = manifest['components']['script']['version']

    rows = []
    with open(args.store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if args.limit:
        rows = rows[:args.limit]

    totals = annotate_rows(rows, script_version, force=args.force)
    report(totals)

    if args.rollup:
        write_rollup(totals, script_version, args.model_version, args.rollup)
        print('\nrollup appended -> %s' % args.rollup)

    if args.dry_run:
        print('\n(dry run — store not written)')
        return
    if not args.no_backup and args.limit is None:
        os.replace(args.store, args.store + '.pre_stats.bak')
    with open(args.store, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('\nwrote annotated store -> %s' % args.store)


if __name__ == '__main__':
    main()
