#!/usr/bin/env python
"""Validate the TM question boundary and modality coverage catalog."""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CATALOG = os.path.join(ROOT, 'docs', 'tm_question_catalog.v1.json')


def main() -> int:
    with open(CATALOG, encoding='utf-8') as handle:
        value = json.load(handle)
    assert value.get('schema') == 'pwg.tm_question_catalog.v1'
    rows = value.get('questions') or []
    ids = [row.get('id') for row in rows]
    assert len(ids) == len(set(ids)), 'question IDs must be unique'
    expected = {
        'will_answer': {'Q%d' % n for n in range(1, 8)},
        'will_not_answer': {'N%d' % n for n in range(1, 12)},
        'could_answer_later': {'F%d' % n for n in range(1, 9)},
    }
    for status, wanted in expected.items():
        found = {row['id'] for row in rows if row.get('status') == status}
        assert found == wanted, '%s coverage drift: %r' % (status, sorted(wanted ^ found))
    coverage = value.get('coverage') or {}
    assert coverage.get('written_pwg_exact_fragment') == 'live'
    assert coverage.get('oral_transcript_units') == 'planned'
    assert coverage.get('raw_audio_asr') == 'out_of_scope'
    invariants = value.get('invariants') or {}
    assert invariants == {
        'flash_may_read_and_rank_tm': True,
        'flash_may_write_tm': False,
        'flash_may_sole_judge_promotion': False,
        'fuzzy_may_auto_reuse': False,
        'promoter_is_only_writer': True,
    }
    print('tm_question_catalog_selftest: PASS (7 will / 11 will-not / 8 future)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
