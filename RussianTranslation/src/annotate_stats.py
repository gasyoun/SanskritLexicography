#!/usr/bin/env python
"""annotate_stats.py — cache per-card derived counts onto the pwg_ru store (H422).

GRAMMAR_LAYER.md § "Counting grammar" design (merged, PR #284): nothing on a card
records "N senses, M government markers, governs {loc, gen}, spans Renou I-IV" —
government_census.py / government_queries.py re-scan/re-aggregate the whole store
on every question. This is the backfill that fixes that, run **last** in the
annotator chain (after annotate_government.py / annotate_renou.py /
annotate_evidence.py) — it reads only fields already on the store row, no new
source parsing:

  row['stats']  {n_records, n_senses, n_government, cases_governed, has_variation,
                 n_irregularities, strata_span, n_strata, evidence, computed_by,
                 pipeline_version}

Grouped and attached per lemma (`key1`), identically to every store row sharing
that key1 — the same convention `evidence_summary` already uses (the flat store
has no lemma object to hang a lemma-level block off of).

Self-invalidation: `stats.pipeline_version` is the manifest `script` component
version (pipeline_version.py) at compute time. A stats block whose stamped
version is older than the current script version is stale -> recompute;
otherwise trust it without a rescan (mirrors `evidence_summary.evidence_status`).

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

_SUBCARD_H_RE = re.compile(r'~~h(\d+)_')

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


def n_records_for(rows):
    """Distinct homonym groups for a lemma, from `subcard`'s `~~h<N>_` token.
    A row with no parseable subcard counts as its own (unknown) group of one,
    via a per-row fallback key so it never silently merges into h0."""
    groups = set()
    for i, r in enumerate(rows):
        m = _SUBCARD_H_RE.search(r.get('subcard') or '')
        groups.add(m.group(1) if m else ('_row%d' % i))
    return len(groups)


def compute_stats(rows, script_version):
    """Derive the `stats` block for one lemma's (key1-grouped) rows."""
    n_government = 0
    cases_governed = set()
    has_variation = False
    for r in rows:
        hits = r.get('government') or []
        if hits:
            n_government += 1
        for hit in hits:
            cases_governed.update(hit.get('cases') or [])
            if hit.get('variation'):
                has_variation = True

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

    return {
        'n_records': n_records_for(rows),
        'n_senses': len(rows),
        'n_government': n_government,
        'cases_governed': sorted(cases_governed),
        'has_variation': has_variation,
        'n_irregularities': 0,     # not yet joined onto card rows — see GRAMMAR_LAYER.md
        'strata_span': strata_span,
        'n_strata': len(strata),
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


def annotate_rows(rows, script_version, force=False):
    """Mutate store rows in place, attaching `stats` per lemma. Returns a
    Counter of corpus-level rollup totals."""
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
        else:
            stats = compute_stats(group, script_version)
            lemmas_recomputed += 1
        for i in idxs:
            rows[i]['stats'] = stats

        totals['lemmas'] += 1
        totals['records'] += stats['n_records']
        totals['senses'] += stats['n_senses']
        totals['government_markers'] += stats['n_government']
        if stats['has_variation']:
            totals['lemmas_with_variation'] += 1
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
        f.write('| evidence: provides | %d |\n' % totals['evidence_provides'])
        f.write('| evidence: supports | %d |\n' % totals['evidence_supports'])
        f.write('\n')


# ---- selftest (pure functions only — no store file IO, so it runs in CI) --------
def selftest():
    assert strata_in('Vedic, Epic / early-Classical, Classical') == ['Vedic', 'Epic', 'Classical']
    assert strata_in('general') == []
    assert strata_in('') == [] and strata_in(None) == []

    rows = [
        {'key1': 'agni', 'subcard': '_agni~~h0_00_pwg01', 'sense_tag': '1',
         'stratum': 'Vedic', 'government': [], 'evidence': [{'relation': 'provides'}],
         'evidence_summary': {'silent': ['smirnov'], 'contradicts': []}},
        {'key1': 'agni', 'subcard': '_agni~~h0_01_pwg01', 'sense_tag': '2',
         'stratum': 'Classical',
         'government': [{'cases': ['loc', 'gen'], 'variation': True}],
         'evidence': [{'relation': 'supports'}],
         'evidence_summary': {'silent': ['smirnov'], 'contradicts': []}},
        {'key1': 'agni', 'subcard': '_agni~~h1_00_pwg01', 'sense_tag': '1',
         'stratum': '', 'government': [], 'evidence': [], 'evidence_summary': None},
        {'key1': 'deva', 'subcard': '_deva~~h0_00_pwg01', 'sense_tag': '1',
         'stratum': '', 'government': [], 'evidence': [], 'evidence_summary': None},
    ]
    rows_copy = [dict(r) for r in rows]
    totals = annotate_rows(rows_copy, '1.0.0')
    assert totals['lemmas'] == 2, totals
    assert totals['lemmas_recomputed'] == 2 and totals['lemmas_cached'] == 0, totals

    agni_stats = rows_copy[0]['stats']
    assert agni_stats is rows_copy[1]['stats'] is rows_copy[2]['stats'], 'stats is lemma-scoped'
    assert agni_stats['n_records'] == 2, agni_stats            # h0, h1
    assert agni_stats['n_senses'] == 3, agni_stats
    assert agni_stats['n_government'] == 1, agni_stats
    assert agni_stats['cases_governed'] == ['gen', 'loc'], agni_stats
    assert agni_stats['has_variation'] is True, agni_stats
    assert agni_stats['strata_span'] == ['Vedic', 'Classical'], agni_stats
    assert agni_stats['n_strata'] == 2, agni_stats
    assert agni_stats['evidence'] == {'provides': 1, 'supports': 1, 'contradicts': 0, 'silent': 1}, agni_stats
    assert agni_stats['computed_by'] == 'annotate_stats.py'
    assert agni_stats['pipeline_version'] == '1.0.0'

    deva_stats = rows_copy[3]['stats']
    assert deva_stats['n_records'] == 1 and deva_stats['n_senses'] == 1, deva_stats
    assert deva_stats['strata_span'] == [] and deva_stats['n_strata'] == 0, deva_stats

    # self-invalidation: a stale-versioned cached block is recomputed; a fresh one is trusted
    assert is_stale(None, '1.0.0') is True
    assert is_stale({'pipeline_version': '0.9.0'}, '1.0.0') is True
    assert is_stale({'pipeline_version': '1.0.0'}, '1.0.0') is False
    assert is_stale({'pipeline_version': '1.1.0'}, '1.0.0') is False

    rows_copy2 = [dict(r) for r in rows]
    annotate_rows(rows_copy2, '1.0.0')
    totals2 = annotate_rows(rows_copy2, '1.0.0')     # re-run at the same version: no recompute
    assert totals2['lemmas_recomputed'] == 0 and totals2['lemmas_cached'] == 2, totals2
    totals3 = annotate_rows(rows_copy2, '2.0.0')     # bump: every lemma recomputes
    assert totals3['lemmas_recomputed'] == 2, totals3

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
