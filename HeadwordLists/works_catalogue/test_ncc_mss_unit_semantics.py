"""Tests for ncc_mss_unit_semantics (H7085)."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ncc_mss_unit_semantics as U  # noqa: E402


def test_expand_range_abbreviation():
    assert U._expand_range(1042, 48) == [str(n) for n in range(1042, 1049)]
    assert U._expand_range(132, 150) == [str(n) for n in range(132, 151)]


def test_details_units_matches_declared_when_listed():
    # The workbook declares 9 and enumerates 9 for this chunk.
    units = U.details_units(
        'Bikaner: 9 {78327 1636 72470 181 73441 5862-63 441 1039  }')
    assert units == {('bikaner', a) for a in (
        '78327', '1636', '72470', '181', '73441', '5862', '5863', '441',
        '1039')}


def test_details_units_is_not_the_declared_count():
    # Declared 427, enumerated 12 for this shortened chunk: the two differ.
    units = U.details_units(
        'Bṛhatsūcī, Nepal: 427 {154 158 178 19 179 2 348 387 342-43 83-84}')
    assert len(units) == 12
    assert ('bṛhatsūcī, nepal', '84') in units


def test_aggregate_first_sum_union():
    mss_of = {'a': 100, 'b': 20}
    details = {'a': 'X.: 100 {1 2 3}', 'b': 'Y.: 20 {4 5}'}
    agg = U._wb_aggregate(['a', 'b'], mss_of, details)
    assert agg['rows'] == 2
    assert agg['mss_first'] == 100
    assert agg['mss_sum'] == 120
    assert agg['details_units'] == 5


def test_exact_label_first_row_wins_over_alias():
    # The committed reader takes the first exact-label row, not the first alias
    # row: Bhāgavata must report 2,248, not the Bhāgavatapurāṇa row's 1.
    wb_titles = {'Bhāgavata': ['main'], 'Bhāgavatapurāṇa': ['alias']}
    mss_of = {'main': 2248, 'alias': 1}
    body = {'Bhāgavata': [{'body_html': ''}]}
    row = U._row('Bhāgavata', 'canary', ['Bhāgavata', 'Bhāgavatapurāṇa'],
                 body, re.compile('(?!)'), wb_titles, mss_of, {})
    assert row['wb_mss_first'] == 2248
    assert row['wb_mss_sum'] == 2249
    assert row['body_units'] == 0
