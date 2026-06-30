#!/usr/bin/env python
r"""gold_sample_en.py — stratified human-gold sample of the tri-lingual store's EN layer.

FU1 locked decision 4: the citable bar is FU2 audit + Opus judge + a HUMAN-validated gold sample
with documented inter-annotator agreement (Cohen kappa) and error rate. This draws that sample.

Population = store rows that carry `en`. Strata = DCS freq band x source_type x stratum, fixed
seed, proportional with a per-cell floor (deterministic). Emits:

  1. a gitignored WORKING sample (gold_sample_en.jsonl) — id + headword + de + en + the strata, plus
     `period`/`kind` ALIASES (period = "band<N>", kind = source_type) so the existing kappa/precision
     scorer gold_agreement.py consumes the ingested labels UNCHANGED (it breaks down by period+kind).
  2. a BLANK reviewer sheet (gold/reviewer_sheet_en.csv) showing ONLY headword + de + en + a
     human_label column. Monier-Williams is DELIBERATELY ABSENT — ground truth is faithful-to-German
     (decision 6); showing MW would anchor the annotator to a different dictionary.
  3. a METHODS note (gold/METHODS_en.md) for the citable layer.

Reviewer labels (gold_agreement.py vocabulary): correct | lemma-variant | proper-name | partial |
wrong-sense | hallucinated. GOOD = {correct, lemma-variant, proper-name}; ERR = {wrong-sense,
hallucinated}. Two annotators -> gold_agreement.py reports precision + Cohen kappa.

  python src/gold_sample_en.py --n 300 [--seed 42]
  python src/gold_sample_en.py --dry-run        # report composition, write nothing
  python src/gold_sample_en.py --selftest
Downstream: python src/gold_packet.py gold/reviewer_sheet_en.csv   # split into reviewer packets
            python src/gold_agreement.py gold/human_gold_labels_en.jsonl
"""
import argparse
import collections
import csv
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
GOLD = os.path.join(ROOT, 'gold')
SAMPLE = os.path.join(HERE, 'gold_sample_en.jsonl')
SHEET = os.path.join(GOLD, 'reviewer_sheet_en.csv')
METHODS = os.path.join(GOLD, 'METHODS_en.md')
LABELS = ['correct', 'lemma-variant', 'proper-name', 'partial', 'wrong-sense', 'hallucinated']
SHEET_FIELDS = ['id', 'headword', 'de', 'en', 'human_label', 'notes']


def band_label(row):
    f = row.get('dcs_freq') or {}
    b = f.get('band')
    return 'band%s' % b if b is not None else 'band_na'


def cell_of(row):
    return (band_label(row), row.get('source_type') or 'na', row.get('stratum') or 'unspecified')


def stratified(rows, n, seed):
    cells = collections.defaultdict(list)
    for r in rows:
        cells[cell_of(r)].append(r)
    rng = random.Random(seed)
    total = len(rows)
    picked = []
    for cell, group in sorted(cells.items()):
        group = sorted(group, key=lambda r: (r.get('subcard') or '', r.get('sense_tag') or ''))
        rng.shuffle(group)
        want = max(min(3, len(group)), round(n * len(group) / total)) if total else 0
        picked.extend(group[:min(want, len(group))])
    rng.shuffle(picked)
    return picked[:n] if len(picked) > n else picked


def to_record(i, r):
    band, src, stratum = cell_of(r)
    return {
        'id': i,
        'headword': r.get('iast'),
        'key1': r.get('key1'), 'subcard': r.get('subcard'), 'sense_tag': r.get('sense_tag'),
        'de': r.get('de'), 'en': r.get('en'),
        'freq_band': band, 'source_type': src, 'stratum': stratum,
        'period': band, 'kind': src,           # ALIASES for gold_agreement.py breakdowns
    }


def write_outputs(picked):
    os.makedirs(GOLD, exist_ok=True)
    recs = [to_record(i, r) for i, r in enumerate(picked)]
    with open(SAMPLE, 'w', encoding='utf-8') as f:
        for rec in recs:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    with open(SHEET, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=SHEET_FIELDS, extrasaction='ignore')
        w.writeheader()
        for rec in recs:
            w.writerow({'id': rec['id'], 'headword': rec['headword'],
                        'de': rec['de'], 'en': rec['en'], 'human_label': '', 'notes': ''})
    comp = collections.Counter((rec['freq_band'], rec['source_type']) for rec in recs)
    methods = [
        '# EN gold sample — METHODS', '',
        'Ground truth: **faithful to the PWG German** sense (FU1 decision 6). Monier-Williams is a',
        'cross-check only and is **withheld from the reviewer sheet** to avoid anchoring.', '',
        '- Population: tri-lingual store rows carrying `en` (%d sampled).' % len(recs),
        '- Strata: DCS freq band x source_type x stratum, fixed seed, proportional with a per-cell floor.',
        '- Reviewer sheet shows headword + German (de) + English (en) only; label vocabulary: '
        + ', '.join('`%s`' % l for l in LABELS) + '.',
        '- GOOD = {correct, lemma-variant, proper-name}; ERR = {wrong-sense, hallucinated}.',
        '- Two annotators -> `gold_agreement.py` reports precision (Wilson 95%% CI) + Cohen kappa.',
        '  The working sample aliases `period`=freq-band and `kind`=source_type so that scorer is',
        '  reused unchanged.', '',
        '## Sample composition (freq_band x source_type)', '',
        '| freq_band | source_type | n |', '|---|---|---:|',
    ]
    for (band, src), c in sorted(comp.items()):
        methods.append('| %s | %s | %d |' % (band, src, c))
    open(METHODS, 'w', encoding='utf-8').write('\n'.join(methods) + '\n')
    return recs, comp


def selftest():
    rows = []
    for i in range(60):
        rows.append({'iast': 'hw%d' % i, 'key1': 'k%d' % i, 'subcard': 's%d' % i,
                     'sense_tag': '1', 'de': 'deutsch %d' % i, 'en': 'english %d' % i,
                     'source_type': 'attested' if i % 2 else 'lexicographic',
                     'stratum': 'Vedic' if i % 3 else 'Classical',
                     'dcs_freq': {'band': i % 6}})
    picked = stratified(rows, 20, 42)
    assert 0 < len(picked) <= 20, 'sample is non-empty and never exceeds n'
    assert [r['key1'] for r in stratified(rows, 20, 42)] == [r['key1'] for r in picked], \
        'deterministic for a fixed seed'
    rec = to_record(0, picked[0])
    assert set(SHEET_FIELDS) - {'human_label', 'notes'} <= set(['id'] + list(rec)), 'sheet cols present'
    assert 'mw' not in rec and 'monier' not in str(rec).lower(), 'MW must be absent from the sample'
    assert rec['period'] == rec['freq_band'] and rec['kind'] == rec['source_type'], 'aliases set'
    print('gold_sample_en selftest OK (%d rows, deterministic, MW-free, aliased)' % len(picked))


def main():
    if '--selftest' in sys.argv[1:]:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=300)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if not os.path.exists(args.store):
        sys.exit('no store at %s' % args.store)
    rows = [json.loads(l) for l in open(args.store, encoding='utf-8') if l.strip()]
    en_rows = [r for r in rows if r.get('en')]
    if not en_rows:
        sys.exit('no rows carry `en` yet — run promote_en.py first')
    picked = stratified(en_rows, args.n, args.seed)
    comp = collections.Counter((band_label(r), r.get('source_type') or 'na') for r in picked)
    print('population (rows with en): %d | sampled: %d (seed %d, target %d)'
          % (len(en_rows), len(picked), args.seed, args.n))
    for cell, c in sorted(comp.items()):
        print('  %-10s %-14s : %d' % (cell[0], cell[1], c))
    if args.dry_run:
        print('\n(dry run — nothing written)')
        return
    recs, _ = write_outputs(picked)
    print('\nwrote working sample  -> %s (%d rows)' % (os.path.relpath(SAMPLE, ROOT), len(recs)))
    print('wrote reviewer sheet  -> %s (MW hidden)' % os.path.relpath(SHEET, ROOT))
    print('wrote METHODS note    -> %s' % os.path.relpath(METHODS, ROOT))
    print('NEXT: src/gold_packet.py %s  (split into reviewer packets)' % os.path.relpath(SHEET, ROOT))


if __name__ == '__main__':
    main()
