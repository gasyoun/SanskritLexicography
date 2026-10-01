"""H3500 - regression tests for the pwg_ru TM defect-class fixes.

Covers: entry-join collapse (B090 shape), merge_store_rows incoming-duplicate
guard, repair-pass dedupe/marker/vgl behaviour, and the scanner gate.
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "src")
sys.path.insert(0, SRC)

entry_join = importlib.import_module("pwg_ru_entry_join")
repair = importlib.import_module("h3500_store_repair")
scanner = importlib.import_module("h3500_defect_scan")
promote = importlib.import_module("promote_final_cards")


VASIN_A = "{#vasin#}¦ (от {#vasA#}) <lex>m.</lex> {%выдра%}\n<ls>H. 1350.</ls>"
VASIN_B = "*{#vasin#}¦ <lex>m.</lex> {%выдра%}."


def test_entry_join_collapses_b090_homograph_blocks():
    parts = [VASIN_A, VASIN_B, VASIN_A, VASIN_B]
    text, stats = entry_join.assemble_entry(parts)
    assert stats["blocks_dropped"] == 2
    assert text.count("{%выдра%}") == 2


def test_entry_join_keeps_distinct_senses():
    parts = ["1) {%брать%}", "2) {%брать%} вновь", "<ls>RV. 1,1.</ls>"]
    text, stats = entry_join.assemble_entry(parts)
    assert stats["blocks_dropped"] == 0
    assert text.count("{%брать%}") == 2


def test_scanner_flags_identical_intra_subcard_rows():
    rows = [
        {"key1": "x", "subcard": "x~~h0_00", "sense_tag": "1",
         "ru": "1) {%длинное определение слова для дедупликации%}"},
        {"key1": "x", "subcard": "x~~h0_00", "sense_tag": "1",
         "ru": "1) {%длинное определение слова для дедупликации%}"},
    ]
    rep = scanner.scan(rows)
    assert rep["class1a_duplicate_row_excess"] == 1


def test_repair_drops_duplicates_keep_best_and_marks_advisory(tmp_path):
    rows = [
        {"key1": "x", "subcard": "x~~h0_00", "sense_tag": "1",
         "review_status": "ai_translated", "ru": "{%глосса%} длиннее порога",
         "de": "de-src"},
        {"key1": "x", "subcard": "x~~h0_00", "sense_tag": "1",
         "review_status": "approved", "reviewer": "MG",
         "ru": "{%глосса%} длиннее порога", "de": "de-src"},
        {"key1": "y", "subcard": "pf_tv_i", "sense_tag": "1",
         "ru": "[Buddh] {%просветлённый%} BHSD : 353"},
        {"key1": "z", "subcard": "z~~h0_01", "sense_tag": "1",
         "ru": "Mit {%upa:%}, vgl. <ls>Pischel.</ls>"},
    ]
    repaired, events = repair.repair(rows)
    kinds = {e["fix"] for e in events}
    assert "class1a_dedupe" in kinds
    assert len(repaired) == 3
    kept = [r for r in repaired if r.get("subcard") == "x~~h0_00"]
    assert len(kept) == 1 and kept[0].get("reviewer") == "MG"
    adv = [r for r in repaired if r.get("subcard") == "pf_tv_i"][0]
    assert adv["advisory_enrichment"] == "bhsd"
    fixed = [r for r in repaired if r.get("subcard") == "z~~h0_01"][0]
    assert "vgl." not in repair.visible(fixed["ru"]) or \
        "<ab>vgl.</ab>" in fixed["ru"]


def test_merge_store_rows_collapses_incoming_duplicates():
    dup = {"key1": "k", "subcard": "s~~h0_00", "sense_tag": "1",
           "review_status": "ai_translated", "ru": "1) {%одно и то же%}"}
    existing = []
    merged, downgraded, protected = promote.merge_store_rows(existing, [dup, dict(dup)])
    rows = [r for r in merged if r.get("subcard") == "s~~h0_00"]
    assert len(rows) == 1
    assert downgraded == [] and protected == []


def test_repair_keeps_cross_tag_identical_rows():
    """Identical ru under DIFFERENT sense_tags = zz-tagger noise, not dups."""
    rows = [
        {"key1": "s", "subcard": "s~~h0_zz", "sense_tag": "ud-prefix-3",
         "ru": "{%одно и то же длинное содержание строки%}"},
        {"key1": "s", "subcard": "s~~h0_zz", "sense_tag": "sam-prefix-3",
         "ru": "{%одно и то же длинное содержание строки%}"},
    ]
    repaired, events = repair.repair(rows)
    assert len(repaired) == 2
    assert [e["fix"] for e in events if e["fix"] == "class1a_dedupe"] == []


def test_scanner_vgl_predicate_ignores_tagged_ab():
    rows = [
        {"key1": "a", "subcard": "a1", "sense_tag": "1",
         "ru": "(<ab>vgl.</ab> {#Api#})"},
        {"key1": "b", "subcard": "b1", "sense_tag": "1",
         "ru": "desid. vgl. {#parIpsA#} ."},
    ]
    rep = scanner.scan(rows)
    assert len(rep["class2_bare_vgl"]) == 1
    assert rep["class2_bare_vgl"][0]["subcard"] == "b1"


def test_merge_store_rows_still_protects_human_touched():
    human = {"key1": "k", "subcard": "s~~h0_01", "sense_tag": "1",
             "review_status": "approved", "reviewer": "MG",
             "ru": "{%человеческий перевод%}"}
    incoming = dict(human, review_status="ai_translated", reviewer=None)
    merged, _down, protected = promote.merge_store_rows([human], [incoming])
    assert protected == ["s~~h0_01"]
    assert merged[0].get("reviewer") == "MG"
