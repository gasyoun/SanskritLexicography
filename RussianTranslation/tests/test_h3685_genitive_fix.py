"""H3685 - regression tests for the akshara close-out tail: the 3 genitive
rewordings and the 42-vs-live homograph block report.
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "src")
sys.path.insert(0, SRC)

genitive_fix = importlib.import_module("h3685_genitive_fix")
blocks_report = importlib.import_module("h3685_homograph_blocks_report")
scanner = importlib.import_module("h3500_defect_scan")


def _row(key1, subcard, sense_tag, ru):
    return {"key1": key1, "subcard": subcard, "sense_tag": sense_tag, "ru": ru}


def test_genitive_fix_repairs_all_three_and_clears_scanner_class2():
    rows = [
        _row("diS", "di_s~~h0_22_samud", "2",
             "она стала невесткой\n<is>Arjuna's</is> 489."),
        _row("su", "su~~h1_00_pwg00", "3.",
             "(о <is>Savitar's</is> воздействии)"),
        _row("vad", "vad~~h0_08_anu", "1",
             "{%звучал подобно%} <is>Indra's</is> {%городу%}"),
    ]
    before_leaks = scanner.scan(rows)["class2_is_genitive_leaks"]
    assert len(before_leaks) == 3

    repaired, events = genitive_fix.repair([dict(r) for r in rows])
    assert len(events) == 3
    after_leaks = scanner.scan(repaired)["class2_is_genitive_leaks"]
    assert after_leaks == []
    # Russian genitive form present, English possessive gone
    ru_by_key1 = {r["key1"]: r["ru"] for r in repaired}
    assert "Арджуны" in ru_by_key1["diS"] and "Arjuna" not in ru_by_key1["diS"]
    assert "Савитара" in ru_by_key1["su"] and "Savitar" not in ru_by_key1["su"]
    assert "Индры" in ru_by_key1["vad"] and "Indra" not in ru_by_key1["vad"]


def test_genitive_fix_refuses_on_missing_row():
    rows = [_row("other", "x", "1", "no leak here")]
    with pytest.raises(SystemExit):
        genitive_fix.repair([dict(r) for r in rows])


def test_genitive_fix_refuses_on_drifted_before_text():
    rows = [_row("diS", "di_s~~h0_22_samud", "2", "already fixed, no leak")]
    with pytest.raises(SystemExit):
        genitive_fix.repair([dict(r) for r in rows])


def test_homograph_block_report_schema_and_counts():
    rows = [
        # same key1, two homograph subcards (h0_80/h6_23-style anusam pair)
        _row("vasin", "s0", "1", "{%выдра%} длинный текст блока один"),
        _row("vasin", "s1", "1", "{%выдра%} длинный текст блока один"),
        _row("vasin", "s2", "1", "не повторяющийся блок"),
        {"key1": "bad", "subcard": "s3", "sense_tag": "1", "ru": ""},
    ]
    result = blocks_report.build(rows)
    assert result["class1b_block_count"] == 1
    block = result["blocks"][0]
    assert set(block["subcards"]) == {"s0", "s1"}
    # the empty-ru row never enters a block (too short to collapse), so the
    # schema-invalid counter stays 0 for this fixture
    assert result["class1b_schema_invalid_rows"] == 0
