#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the PWG collocate layer for pwg_ru — join the DCS syntagmatic table
(kosha dataset `dcs-sintagmatic-appendix7`, Приложение 7) onto the pwg_ru
headword index, H4708.

Consumes (canonical, read-only):
  - DCS_Sintagmatic.csv  : sibling VisualDCS clone
    (derived-data/Lexical-Cores/Prilozhenie-7.-«Sintagmaticheskaya-tablica-
     dlya-vseh-lemm-korpusa»v/DCS_Sintagmatic.csv — semicolon-delimited UTF-8
     no BOM; `lemma; total occurrences; co-occurrence count; ranked
     collocate freq; ...`). Registered in kosha datasets.json
     (`dcs-sintagmatic-appendix7`, 82,799 rows).
  - headword_index.tsv   : this repo's k1 index (SLP1).

Join: DCS lemmas are IAST → transcode via the vendored sanskrit-util
`to_slp1` (_sanskrit_util_vendored.py, reused — no new transcoder) and match
headword_index `k1` exactly. DCS aggregates the whole corpus lemma, which
cannot distinguish PWG homonyms, so the profile is attached to EVERY homonym
of a covered k1 (same k1-level policy as pwg_derivation_layer.py's aggregated
Pāṇini field; homonym_precise stays empty). This layer NEVER overwrites
reviewed overlay/portrait data — it is a sidecar only; --apply on local
portraits is the maintainer's step and is deliberately NOT implemented here.

Emits src/pwg_collocate_layer.tsv (committed, grammar-FAIR):
  k1  hom  lemma_iast  total_occ  cooccur  collocates (top-N `iast:freq|...`)
Deterministic. Selftest: python src/pwg_collocate_layer.py --selftest
Spot check:  python src/pwg_collocate_layer.py --spot-check 10
"""
import argparse
import csv
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _sanskrit_util_vendored import to_slp1  # noqa: E402

DEFAULT_CSV = os.path.join(
    HERE, '..', '..', '..', 'VisualDCS', 'derived-data', 'Lexical-Cores',
    'Prilozhenie-7.-«Sintagmaticheskaya-tablica-dlya-vseh-lemm-korpusa»v',
    'DCS_Sintagmatic.csv')
OUT_PATH = os.path.join(HERE, 'pwg_collocate_layer.tsv')
INDEX_PATH = os.path.join(HERE, 'headword_index.tsv')

FIXTURE_CSV = (
    "akāra;57;81;ādi 10;ukāra 6;akṣara 4;nāman 2;rūpa 2;hakāra 1;mṛtyu 1\n"
    "vid;900;1400;mantra 120;veda 80;jānāti 40\n"
    "go;1200;2100;gavām 90;goṣtha 30\n"
    "zombie;5;5; phantom 5\n"          # never joins the index (negative control)
    "garbageline\n"                     # malformed: no counts -> skipped+counted
    ";5;5;x 1\n"                        # empty lemma -> skipped+counted
)
FIXTURE_INDEX = [
    {'k1': 'akAra', 'hom': '1'},
    {'k1': 'akAra', 'hom': '2'},   # homonym pair — profile attached to both
    {'k1': 'vid', 'hom': '1'},
    {'k1': 'gam', 'hom': '1'},     # in index, absent from CSV (negative control)
]
FIXTURE_CSV_PATH = os.path.join(HERE, '..', 'tests', 'fixtures',
                                'H4708_collocate_fixture.csv')


def read_lemma_profiles(csv_path):
    """lemma(IAST) -> dict(total, cooccur, collocates=[(iast, freq), ...]).

    Verbatim token preservation: corrupted source tokens (e.g. U+FFB1 mojibake
    in the pre-2026 dump) are carried through untouched — cleaning is a
    human/editorial call, never a silent rewrite of a derived layer.
    Rows with <4 fields or an empty lemma are skipped (blank separators,
    truncated lines — counted, reported by caller).
    """
    profiles, skipped = {}, 0
    with open(csv_path, encoding='utf-8', newline='') as f:
        if f.read(1) == '\ufeff':
            raise SystemExit('FATAL: appendix7 CSV unexpectedly has a BOM '
                             '(kosha notes say none) — stop, re-check source')
        f.seek(0)
        for line in f:
            parts = line.rstrip('\n').rstrip('\r').split(';')
            if len(parts) < 4 or not parts[0]:
                skipped += 1
                continue
            try:
                total, cooccur = int(parts[1]), int(parts[2])
            except ValueError:
                skipped += 1
                continue
            cands = []
            for tok in parts[3:]:
                if not tok:
                    continue
                head, _, tail = tok.rpartition(' ')
                try:
                    freq = int(tail)
                except ValueError:
                    skipped += 1
                    continue
                cands.append((head, freq))
            profiles[parts[0]] = {'total': total, 'cooccur': cooccur,
                                  'collocates': cands}
    return profiles, skipped


def build(csv_path, index_path, top_n):
    profiles, skipped = read_lemma_profiles(csv_path)
    by_slp1 = {}
    for lem, prof in profiles.items():
        by_slp1.setdefault(to_slp1(lem), []).append((lem, prof))
    rows_out, covered_k1 = [], set()
    with open(index_path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            hit = by_slp1.get(r['k1'])
            if not hit:
                continue
            covered_k1.add(r['k1'])
            lem, prof = hit[0]
            top = prof['collocates'][:top_n]
            rows_out.append({
                'k1': r['k1'], 'hom': r['hom'], 'lemma_iast': lem,
                'total_occ': prof['total'], 'cooccur': prof['cooccur'],
                'collocates': '|'.join('%s:%d' % c for c in top),
            })
    stats = {
        'csv_lemmas': len(profiles), 'csv_skipped_lines': skipped,
        'index_k1_unique': None, 'k1_covered': len(covered_k1),
        'rows_emitted': len(rows_out),
    }
    return rows_out, stats


def write_tsv(rows, out_path):
    cols = ['k1', 'hom', 'lemma_iast', 'total_occ', 'cooccur', 'collocates']
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')


def selftest(tmp_dir):
    """Positive + negative: join hits, homonym fan-out, ordering, freq
    preservation, non-join of an unindexed lemma, BOM guard, skipped-line
    accounting. Returns list of (name, ok)."""
    import io
    os.makedirs(tmp_dir, exist_ok=True)
    fx = os.path.join(tmp_dir, 'fixture.csv')
    with open(fx, 'w', encoding='utf-8') as f:
        f.write(FIXTURE_CSV)
    fx_idx = os.path.join(tmp_dir, 'fixture_index.tsv')
    with open(fx_idx, 'w', encoding='utf-8', newline='') as f:
        f.write('k1\thom\n')
        for r in FIXTURE_INDEX:
            f.write('%s\t%s\n' % (r['k1'], r['hom']))
    rows, stats = build(fx, fx_idx, top_n=12)
    by = {(r['k1'], r['hom']): r for r in rows}
    checks = [
        ('akAra joins with lemma preserved',
         by.get(('akAra', '1'), {}).get('lemma_iast') == 'akāra'),
        ('homonym fan-out: profile on both homs',
         ('akAra', '2') in by and
         by[('akAra', '1')]['collocates'] == by[('akAra', '2')]['collocates']),
        ('top-N order keeps source ranking + freqs',
         by[('akAra', '1')]['collocates'].startswith('ādi:10|ukāra:6|akṣara:4')
         and 'hakāra:1' in by[('akAra', '1')]['collocates']),
        ('counts preserved (total 57 / cooccur 81)',
         by[('akAra', '1')]['total_occ'] == 57
         and by[('akAra', '1')]['cooccur'] == 81),
        ('vid joins', by.get(('vid', '1'), {}).get('lemma_iast') == 'vid'),
        ('negative: unindexed lemma not emitted',
         all(r['k1'] != 'zombie' for r in rows)),
        ('negative: indexed-but-unattested k1 absent',
         ('gam', '1') not in by),
        ('skipped-line accounting counts the malformed row',
         stats['csv_skipped_lines'] >= 1),
        ('fixture profile count == 3 emitted rows',
         stats['rows_emitted'] == 3),
    ]
    # BOM guard fires on a BOM'd copy
    fx_bom = os.path.join(tmp_dir, 'bom.csv')
    with open(fx_bom, 'w', encoding='utf-8-sig') as f:
        f.write(FIXTURE_CSV)
    try:
        build(fx_bom, fx_idx, 12)
        checks.append(('BOM guard refuses BOM\u2019d source', False))
    except SystemExit:
        checks.append(('BOM guard refuses BOM\u2019d source', True))
    return checks


def spot_check(tsv_path, csv_path, n, seed=4708):
    """Re-derive n sampled rows straight from the raw CSV and compare —
    the H4708 '10-portrait spot check'. Deterministic (seeded)."""
    profiles, _ = read_lemma_profiles(csv_path)
    with open(tsv_path, encoding='utf-8', newline='') as f:
        rows = [r for r in csv.DictReader(f, delimiter='\t')]
    rng = random.Random(seed)
    sample = rng.sample(rows, min(n, len(rows)))
    fails = []
    print('spot-check %d rows (seed=%d):' % (len(sample), seed))
    print('k1\thom\tlemma\ttotal\tcooccur\ttop3\tverdict')
    for r in sample:
        prof = profiles.get(r['lemma_iast'])
        if prof is None:
            fails.append(r['k1'])
            print('%s\t%s\t%s\t-\t-\t-\tFAIL(lemma gone)' %
                  (r['k1'], r['hom'], r['lemma_iast']))
            continue
        top3 = '|'.join('%s:%d' % c for c in prof['collocates'][:3])
        ok = (str(prof['total']) == r['total_occ']
              and str(prof['cooccur']) == r['cooccur']
              and r['collocates'].startswith(
                  '|'.join('%s:%d' % c for c in prof['collocates'][:3]).split(
                      '|')[0]))
        ok = ok and all(tok in r['collocates']
                        for tok in [t for t, _ in prof['collocates'][:3]])
        if not ok:
            fails.append(r['k1'])
        print('%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
            r['k1'], r['hom'], r['lemma_iast'], prof['total'], prof['cooccur'],
            top3, 'PASS' if ok else 'FAIL'))
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--csv', default=DEFAULT_CSV)
    ap.add_argument('--index', default=INDEX_PATH)
    ap.add_argument('--out', default=OUT_PATH)
    ap.add_argument('--top-n', type=int, default=12)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--spot-check', type=int, metavar='N')
    args = ap.parse_args()

    if args.selftest:
        import tempfile
        checks = selftest(os.path.join(tempfile.gettempdir(), 'h4708_selftest'))
        for name, ok in checks:
            print('%s  %s' % ('PASS' if ok else 'FAIL', name))
        if not all(ok for _, ok in checks):
            sys.exit(1)
        print('selftest: %d/%d PASS' % (sum(ok for _, ok in checks),
                                        len(checks)))
        return
    if args.spot_check:
        fails = spot_check(args.out, args.csv, args.spot_check)
        sys.exit(1 if fails else 0)

    rows, stats = build(args.csv, args.index, args.top_n)
    with open(args.index, encoding='utf-8', newline='') as f:
        stats['index_k1_unique'] = len({r['k1'] for r in
                                        csv.DictReader(f, delimiter='\t')})
    write_tsv(rows, args.out)
    stats['out'] = args.out
    stats['out_bytes'] = os.path.getsize(args.out)
    print('coverage: %s' % stats)


if __name__ == '__main__':
    main()
