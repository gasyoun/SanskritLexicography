#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""build_h1682_abbrev_classification_tsv.py — H1682 step 1: the 100%-coverage
classification tsv over every ab-token, re-grouped from build_h1303_abbrev_sheet.py's
O overlay (see h1682_abbrev_collapse.py for the re-grouping logic; no token is
reclassified, only labeled bulk-rule vs classifier-flagged residue and given a
one-line rule/citation).

Usage (from RussianTranslation/):
    python src/build_h1682_abbrev_classification_tsv.py
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import h1682_abbrev_collapse as coll  # noqa: E402

OUT = os.path.join(RT, 'pwg_ru', 'H1682_ABBREV_RULE_COLLAPSE_CLASSIFICATION_2026-07-26.tsv')

AGENT = 'agent (Sonnet 5, claude-sonnet-5), H1682'


def main():
    r = coll.classify()
    rows = []
    for label in r['order']:
        for tok in r['sections'][label]['bulk'] + r['sections'][label]['residue']:
            row = r['by_token'][tok]
            rows.append(row)
    # stable order: section (source order), then freq desc within section
    order_index = {label: i for i, label in enumerate(r['order'])}
    rows.sort(key=lambda row: (order_index[row['section']], -row['freq']))

    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(['token', 'freq', 'section', 'status', 'bucket', 'cls',
                            'ru_proposed', 'citation', 'note', 'classified_by']) + '\n')
        for row in rows:
            status = 'residue-ambiguous' if row['residue'] else 'rule-bulk'
            citation = r['citation'][row['section']]
            f.write('\t'.join([
                row['token'], str(row['freq']), row['section'], status,
                row['bucket'], row['cls'], row['ru_proposed'] or '',
                citation, row['note'] or '', AGENT,
            ]).replace('\n', ' ') + '\n')

    n_bulk = sum(1 for row in rows if not row['residue'])
    n_residue = sum(1 for row in rows if row['residue'])
    print('wrote %s (%d tokens: %d rule-bulk / %d residue-ambiguous)'
          % (OUT, len(rows), n_bulk, n_residue))
    assert len(rows) == 269, 'H1682 DoD requires 100%% of the 269 ab-tokens classified, got %d' % len(rows)


if __name__ == '__main__':
    main()
