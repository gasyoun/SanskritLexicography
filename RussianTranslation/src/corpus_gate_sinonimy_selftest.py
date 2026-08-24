#!/usr/bin/env python
"""H2410 regression tests: sinonimy.jsonl wiring into corpus_gate.py.

Covers the two behaviors the raw data does NOT provide upstream (verified by
direct inspection of a real row, e.g. the `agni` synonym_group_lemma group
whose members[] include the lemma itself twice):
  - self-exclusion (a member never lists itself as its own synonym)
  - de-duplication of repeated members within one group
  - homonym-disambiguation suffix ("aṁśa 2") stripped before the IAST->SLP1 join
  - sense_inventory rows feed a separate soft SENSE index, never the synonym one
Plus a live-data smoke test against the real sinonimy.jsonl (47k rows) proving
a known headword (agni) surfaces non-empty evidence end-to-end via build_card().
"""
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_gate as cg  # noqa: E402
from rt_io import write_jsonl  # noqa: E402


def _reset_index():
    cg._SINONIMY_SYN_IDX = None
    cg._SINONIMY_SENSE_IDX = None


def test_self_exclusion_and_dedup():
    """Mirrors the real `agni` group (lemma appears twice in its own members[])."""
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'sinonimy.jsonl')
        write_jsonl(path, [
            {'type': 'synonym_group_lemma', 'lemma': 'agni', 'depth': 14,
             'gloss_anchor': 'plumbago zeylanica',
             'members': ['tanūnapāt', 'agni', 'agni', 'agnimukha', 'anala', 'anala']},
        ])
        old_path = cg._SINONIMY_PATH
        cg._SINONIMY_PATH = path
        _reset_index()
        try:
            syn_idx, _ = cg.load_sinonimy_index()
            agni_syn = syn_idx[cg._sinonimy_key('agni')]
            assert 'agni' not in agni_syn, 'lemma must not list itself as its own synonym'
            assert agni_syn == {'tanūnapāt', 'agnimukha', 'anala'}, agni_syn
            anala_syn = syn_idx[cg._sinonimy_key('anala')]
            assert 'anala' not in anala_syn
            assert 'agni' in anala_syn
        finally:
            cg._SINONIMY_PATH = old_path
            _reset_index()
    print('  self-exclusion + dedup on synonym_group_lemma: PASS')


def test_disambiguation_suffix_stripped():
    """A lemma like 'aṁśa 2' (homonym disambiguation) must still join correctly."""
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'sinonimy.jsonl')
        write_jsonl(path, [
            {'type': 'sense_inventory', 'lemma': 'aṁśa 2',
             'n_senses': 2, 'senses': ['share', 'part']},
            {'type': 'synonym_group_gloss', 'pos': 'm', 'gloss': 'part',
             'n_members': 2, 'members': ['aṁśa 2', 'bhāga']},
        ])
        old_path = cg._SINONIMY_PATH
        cg._SINONIMY_PATH = path
        _reset_index()
        try:
            key = cg._sinonimy_key('aṁśa 2')
            assert key == cg._sinonimy_key('aṁśa'), (key, cg._sinonimy_key('aṁśa'))
            syn_idx, sense_idx = cg.load_sinonimy_index()
            assert sense_idx[key] == ['share', 'part']
            assert 'bhāga' in syn_idx[key]
        finally:
            cg._SINONIMY_PATH = old_path
            _reset_index()
    print('  homonym-disambiguation suffix strip + IAST join: PASS')


def test_sense_inventory_separate_from_synonyms():
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'sinonimy.jsonl')
        write_jsonl(path, [
            {'type': 'sense_inventory', 'lemma': 'kara', 'n_senses': 1, 'senses': ['hand']},
        ])
        old_path = cg._SINONIMY_PATH
        cg._SINONIMY_PATH = path
        _reset_index()
        try:
            syn_idx, sense_idx = cg.load_sinonimy_index()
            key = cg._sinonimy_key('kara')
            assert key not in syn_idx or not syn_idx[key]
            assert sense_idx[key] == ['hand']
            assert cg.lookup_sinonimy_senses('kara') == ['hand']
            assert cg.lookup_sinonimy_synonyms('kara') == []
        finally:
            cg._SINONIMY_PATH = old_path
            _reset_index()
    print('  sense_inventory rows never enter the synonym index: PASS')


def test_missing_file_degrades_to_empty():
    old_path = cg._SINONIMY_PATH
    cg._SINONIMY_PATH = os.path.join(tempfile.gettempdir(), 'does-not-exist-h2410.jsonl')
    _reset_index()
    try:
        assert cg.lookup_sinonimy_synonyms('agni') == []
        assert cg.lookup_sinonimy_senses('agni') == []
    finally:
        cg._SINONIMY_PATH = old_path
        _reset_index()
    print('  absent sinonimy.jsonl degrades to empty (no crash): PASS')


def test_live_data_smoke():
    """Proves the wiring against the real 47k-row sinonimy.jsonl, not a fixture."""
    real_path = os.path.join(HERE, '..', 'research', 'sinonimy', 'sinonimy.jsonl')
    if not os.path.exists(real_path):
        print('  live-data smoke (agni via build_card): SKIPPED (sinonimy.jsonl not present)')
        return
    _reset_index()
    syn = cg.lookup_sinonimy_synonyms('agni')
    senses = cg.lookup_sinonimy_senses('agni')
    assert syn, 'expected non-empty sinonimy synonyms for agni on real data'
    assert 'agni' not in syn, 'self-exclusion must hold on real data too'
    assert senses, 'expected non-empty sinonimy senses for agni on real data'
    card = cg.build_card(cg.load_index(), 'agni', None, 'огонь')
    assert card['sinonimy_synonyms'], card
    assert card['sinonimy_senses'], card
    print('  live-data smoke (agni via build_card): PASS (%d syn, %d senses)'
          % (len(syn), len(senses)))


def main():
    test_self_exclusion_and_dedup()
    test_disambiguation_suffix_stripped()
    test_sense_inventory_separate_from_synonyms()
    test_missing_file_degrades_to_empty()
    test_live_data_smoke()
    print('corpus_gate sinonimy selftest: PASS')


if __name__ == '__main__':
    main()
