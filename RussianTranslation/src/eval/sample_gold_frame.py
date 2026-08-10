#!/usr/bin/env python
"""sample_gold_frame.py — draw the H2401 stratified BLI gold frame (candidates only).

This emits the ANNOTATION FRAME for the B1 gold set: the sampled lemmas, their
stratum, and the Kochergina gloss an annotator reads. It deliberately does NOT
emit gold labels -- the labels are what MG (pass 1) and the frozen model (pass 2)
produce; a script inventing them is the H070 "rule-based arm" trap that invalidates
a dual-annotation design (see /gold-adjudicate Phase 0).

Design (measured, not assumed -- see probe_gold_strata.py output and
docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md):

  * Frame = Kochergina standalone lemmas x an independent DCS frequency signal,
    with >= 1 extractable Russian content token: 12,939 candidates.
  * Strata = DCS freqBand (1..5) x dominant POS (NOUN/VERB/ADJ/ADV), the four POS
    that clear 20 glossable candidates in every band. Rarer POS (PART, PRON, NUM,
    INTJ, CONJ, SCONJ, ADP -- 23 cells, 108 lemmas total) cannot support a stable
    per-cell rate and are pooled into one reported `OTHER` cell, never silently
    dropped.
  * Allocation = equal-ish per cell rather than proportional, because the research
    question is per-stratum behaviour (where does the lexicon fail?), and a
    proportional draw would spend the whole budget on band 2-3 NOUNs and leave
    band-5 VERB with too few items to report a rate for.

Sampling is seeded and the seed is written into the output header, so the frame is
reproducible: same inputs + same seed = byte-identical frame.

Usage:
  python sample_gold_frame.py --koch <koch.jsonl> --dcs <dcs_lemma_summary.json> \
      --dims <dcs_freq_dims.json> --out <frame.tsv> [--per-cell 25] [--seed 20260810]
  python sample_gold_frame.py selftest
"""
import argparse
import collections
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_gold_strata import (  # noqa: E402  (local module, path set above)
    content_tokens, gloss_text, lemma_key, load_dcs, merge_dcs,
    polysemy_bucket, sense_count,
)

# The four POS with >= 20 glossable candidates in every frequency band.
CORE_POS = ('NOUN', 'VERB', 'ADJ', 'ADV')
BANDS = (5, 4, 3, 2, 1)


def build_frame(koch_path, dcs_path, dims_path, per_cell, seed):
    dcs = merge_dcs(load_dcs(dcs_path), load_dcs(dims_path) if dims_path else None)

    # Pass 1: count entries per SLP1 key. 711 Kochergina keys (2.52%) carry more
    # than one entry -- `vas` I "shine" vs `vas` II "wear clothes" -- and
    # corpus_lexicon.jsonl is keyed by bare surface SLP1 with no homograph index.
    # "The gold Russian gloss for `vas`" is therefore ill-posed, and POOLING the
    # homographs' glosses would make the match leniently accept any homograph's
    # translation, inflating P@1. So homograph keys are EXCLUDED from the frame and
    # the excluded count is reported (see probe_homographs.py).
    entries_per_key = collections.Counter()
    with open(koch_path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                k = lemma_key(rec)
                if k and not k.startswith('-'):
                    entries_per_key[k] += 1

    by_cell = collections.defaultdict(list)
    excluded_homographs = set()
    with open(koch_path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            lemma = lemma_key(rec)
            if not lemma or lemma.startswith('-'):
                continue
            dim = dcs.get(lemma)
            if not dim:
                continue
            gloss = gloss_text(rec)
            toks = content_tokens(gloss)
            if not toks:
                continue
            band = dim['band']
            if band not in BANDS:
                continue
            if entries_per_key[lemma] > 1:
                excluded_homographs.add(lemma)
                continue
            pos = dim['pos'] if dim['pos'] in CORE_POS else 'OTHER'
            nsense = sense_count(rec, gloss)
            by_cell[(band, pos)].append({
                'slp1': lemma,
                'band': band,
                'pos': pos,
                'polysemy': polysemy_bucket(nsense),
                'n_senses': nsense,
                'gloss': ' '.join(gloss.split()),
            })

    rng = random.Random(seed)
    rows, shortfalls = [], []
    for band in BANDS:
        for pos in CORE_POS + ('OTHER',):
            pool = sorted(by_cell.get((band, pos), []), key=lambda r: r['slp1'])
            if not pool:
                shortfalls.append((band, pos, 0, per_cell))
                continue
            if len(pool) <= per_cell:
                picked = pool
                if len(pool) < per_cell:
                    shortfalls.append((band, pos, len(pool), per_cell))
            else:
                picked = rng.sample(pool, per_cell)
            rows.extend(sorted(picked, key=lambda r: r['slp1']))

    stats = {'pools': {k: len(v) for k, v in by_cell.items()},
             'excluded_homograph_keys': len(excluded_homographs)}
    return rows, shortfalls, stats


def write_frame(rows, shortfalls, stats, out_path, per_cell, seed, inputs):
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# H2401 stratified BLI gold ANNOTATION FRAME (candidates, NOT labels).\n')
        f.write('# Labels are produced by MG (pass 1) and the frozen model (pass 2);\n')
        f.write('# this file deliberately carries no gold column -- see the protocol at\n')
        f.write('# docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md.\n')
        f.write(f'# Seed: {seed} (reproducible: same inputs + seed = same frame)\n')
        f.write(f'# Per-cell target: {per_cell}; rows: {len(rows)}\n')
        f.write('# Homograph SLP1 keys excluded (>1 Kochergina entry, ill-posed as\n')
        f.write('# a single gold gloss and lenient-match inflating): '
                f'{stats.get("excluded_homograph_keys", 0)}\n')
        for label, path in inputs:
            f.write(f'# Input {label}: {path}\n')
        if shortfalls:
            f.write('# Shortfall cells (pool < target, sampled exhaustively):\n')
            for band, pos, have, want in shortfalls:
                f.write(f'#   band{band} {pos}: {have} available, {want} requested\n')
        f.write('slp1\tband\tpos\tpolysemy\tn_senses\tkoch_gloss\n')
        for r in rows:
            f.write(f'{r["slp1"]}\t{r["band"]}\t{r["pos"]}\t{r["polysemy"]}\t'
                    f'{r["n_senses"]}\t{r["gloss"]}\n')
    return out_path


def selftest():
    import tempfile

    koch_rows = []
    # 3 bands x 2 POS x 4 lemmas: enough to prove per-cell capping and shortfall.
    for band, pos_lemmas in ((5, ('gaja', 'nara', 'vIra', 'mitra')),
                             (4, ('aSva', 'go', 'jala', 'vana'))):
        for i, lem in enumerate(pos_lemmas):
            koch_rows.append({'slp1': lem, 'ru': f'1) значение{i} 2) второе'})
    koch_rows.append({'slp1': 'solo', 'ru': 'одинокий'})   # band 3, shortfall cell
    koch_rows.append({'slp1': '-bound', 'ru': 'делающий'})  # skipped
    # Homograph: two entries under one SLP1 key -> must be excluded entirely,
    # not drawn twice and not pooled into one lenient gold set.
    koch_rows.append({'slp1': 'homo', 'ru': 'I) сиять, сверкать'})
    koch_rows.append({'slp1': 'homo', 'ru': 'II) носить одежду'})

    summary = {'lemmas': {}}
    for lem in ('gaja', 'nara', 'vIra', 'mitra'):
        summary['lemmas'][lem] = {'freqBand': 5, 'count': 50}
    for lem in ('aSva', 'go', 'jala', 'vana'):
        summary['lemmas'][lem] = {'freqBand': 4, 'count': 30}
    summary['lemmas']['solo'] = {'freqBand': 3, 'count': 10}
    summary['lemmas']['-bound'] = {'freqBand': 3, 'count': 5}
    summary['lemmas']['homo'] = {'freqBand': 5, 'count': 60}

    dims = {'by_lemma': {lem: {'pos': {'dominant': 'NOUN', 'band': {'NOUN': 5},
                                       'total': 50}}
                         for lem in ('gaja', 'nara', 'vIra', 'mitra',
                                     'aśva', 'go', 'jala', 'vana', 'solo')}}

    tmp = tempfile.mkdtemp()
    kp, dp, xp = (os.path.join(tmp, n) for n in
                  ('koch.jsonl', 'summary.json', 'dims.json'))
    with open(kp, 'w', encoding='utf-8') as f:
        for r in koch_rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(dp, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False)
    with open(xp, 'w', encoding='utf-8') as f:
        json.dump(dims, f, ensure_ascii=False)

    failures = []

    def check(label, got, want):
        if got != want:
            failures.append(f'{label}: got {got!r}, want {want!r}')

    rows, shortfalls, stats = build_frame(kp, dp, xp, per_cell=2, seed=7)
    check('rows (2 per cell x band5/band4 NOUN + 1 shortfall)', len(rows), 5)
    check('band5 rows', sum(1 for r in rows if r['band'] == 5), 2)
    check('band3 shortfall recorded',
          any(s[0] == 3 and s[2] == 1 for s in shortfalls), True)
    check('bound lemma excluded', any(r['slp1'] == '-bound' for r in rows), False)
    check('polysemy labelled', rows[0]['polysemy'], '2-3')

    # Homographs: excluded entirely, counted, and never duplicated into the frame.
    check('homograph excluded from rows', any(r['slp1'] == 'homo' for r in rows), False)
    check('homograph counted', stats['excluded_homograph_keys'], 1)
    check('no duplicate lemmas', len({r['slp1'] for r in rows}), len(rows))

    # Determinism: same seed -> same frame; different seed -> (very likely) different.
    rows_again, _, _ = build_frame(kp, dp, xp, per_cell=2, seed=7)
    check('seed reproducible', [r['slp1'] for r in rows],
          [r['slp1'] for r in rows_again])

    out = os.path.join(tmp, 'frame.tsv')
    write_frame(rows, shortfalls, stats, out, 2, 7, [('koch', kp)])
    with open(out, encoding='utf-8') as f:
        text = f.read()
    check('no gold column emitted', 'gold' in text.split('slp1\tband')[1].split('\n')[0],
          False)
    check('header carries seed', '# Seed: 7' in text, True)
    check('header reports homograph exclusion',
          'Homograph SLP1 keys excluded' in text, True)

    if failures:
        print('SELFTEST FAIL')
        for f_ in failures:
            print('  -', f_)
        return 1
    print('SELFTEST PASS (per-cell cap, shortfall report, seed determinism, no gold column)')
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--koch', required=True)
    ap.add_argument('--dcs', required=True, help='dcs_lemma_summary.json (SLP1-keyed)')
    ap.add_argument('--dims', default=None, help='dcs_freq_dims.json (IAST-keyed, POS)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--per-cell', type=int, default=25)
    ap.add_argument('--seed', type=int, default=20260810)
    args = ap.parse_args()

    rows, shortfalls, stats = build_frame(args.koch, args.dcs, args.dims,
                                          args.per_cell, args.seed)
    write_frame(rows, shortfalls, stats, args.out, args.per_cell, args.seed,
                [('koch', args.koch), ('dcs', args.dcs), ('dims', args.dims or '-')])
    print(f'frame rows: {len(rows)} -> {args.out}')
    print(f'homograph keys excluded: {stats["excluded_homograph_keys"]}')
    if shortfalls:
        print(f'shortfall cells: {len(shortfalls)}')
        for band, pos, have, want in shortfalls:
            print(f'  band{band} {pos}: {have}/{want}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
