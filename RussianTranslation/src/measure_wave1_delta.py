#!/usr/bin/env python
"""measure_wave1_delta.py — before/after counts for the H1349 wave-1 defect fixes.

Reproducible delta table (D9): replays the OLD and NEW behaviour of each fix over
the SAME regenerated glossary inputs, so every row isolates the code change alone.
Reuses the pipeline's own helpers — no logic is re-implemented here.

  W1.1 pseudo-root split : root inventory with vs without the self-mapped pseudo-roots.
  W1.2 homograph trail   : ambiguity rows the old (cands[1]-only) vs new (all cands[1:]) rule emit.
  W1.3 vidyut ambiguity  : competitor rows recorded (was a bare counter -> 0 rows).

Run from RussianTranslation/ AFTER a two-pass bootstrap:
  python src/measure_wave1_delta.py
Prints a Markdown table to stdout; the numbers feed RESULTS_LOG.md.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_rollup_glossaries as R

G = R.G


def count_rows(path):
    """Data rows in a TSV (excluding the header); 0 if absent."""
    if not os.path.exists(path):
        return 0
    with open(path, encoding='utf-8') as f:
        return max(0, sum(1 for _ in f) - 1)


def main():
    f2l, l2r, roots_set, lemmas_set, dcs_keys = R.load_maps()

    # --- W1.1: pseudo-root inventory delta -----------------------------------
    unres_path = os.path.join(G, 'dcs_lemma2root_unresolved.tsv')
    pseudo = []
    if os.path.exists(unres_path):
        with open(unres_path, encoding='utf-8') as f:
            next(f, None)
            pseudo = [line.split('\t')[0] for line in f if line.strip()]
    roots_after = set(l2r.values())                 # unresolved already excluded by load_maps
    roots_before = roots_after | set(pseudo)         # old behaviour kept the self-maps
    n_pseudo = len(pseudo)

    # --- W1.2: homograph rows, old rule vs new rule (identical stream) --------
    old_amb_rows = new_amb_rows = new_amb_forms = 0
    with open(os.path.join(G, 'surface_glossary.jsonl'), encoding='utf-8') as f:
        for line in f:
            nk = R.norm(json.loads(line)['slp1'])
            cands = f2l.get(nk)
            if not cands or len(cands) < 2:
                continue
            # OLD: inspected only the single runner-up cands[1]
            _l1, u1, c1, _s1 = cands[0]
            _l2, u2, c2, _s2 = cands[1]
            if u2 != u1 or c2 >= 0.5 * c1:
                old_amb_rows += 1
            # NEW: every qualifying candidate in cands[1:]
            alts = R.homograph_alts(cands)
            if alts:
                new_amb_rows += len(alts)
                new_amb_forms += 1

    # --- W1.3: vidyut ambiguity rows -----------------------------------------
    vidyut_amb_after = count_rows(os.path.join(G, 'vidyut_ambiguity.tsv'))

    # root-glossary layer size (headline context for W1.1)
    root_gloss = 0
    rg_path = os.path.join(G, 'root_glossary.jsonl')
    if os.path.exists(rg_path):
        with open(rg_path, encoding='utf-8') as f:
            root_gloss = sum(1 for line in f if line.strip())

    d_inv = len(roots_before) - len(roots_after)
    rows = [
        ('W1.1 distinct root keys in lemma->root map', len(roots_before), len(roots_after),
         f'{n_pseudo} pseudo-root rows split out (net -{d_inv} distinct keys); '
         f'root_glossary layer now {root_gloss:,}'),
        ('W1.2 homograph alternate rows', old_amb_rows, new_amb_rows,
         f'+{new_amb_rows - old_amb_rows} rows; full trail over {new_amb_forms:,} forms'),
        ('W1.3 vidyut ambiguity rows recorded', 0, vidyut_amb_after,
         'was a bare counter; now a competitor trail'),
    ]
    print('| Defect | Before | After | Note |')
    print('|---|--:|--:|---|')
    for name, before, after, note in rows:
        print(f'| {name} | {before:,} | {after:,} | {note} |')

    # machine-readable echo for the commit body / CI
    print('\n' + json.dumps({name: {'before': b, 'after': a}
                             for name, b, a, _ in rows}, ensure_ascii=False))


if __name__ == '__main__':
    main()
