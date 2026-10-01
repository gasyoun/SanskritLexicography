"""H3644 — GAPS §17 surface-form gates + coordinator --kind defect-repair."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
PILOT = os.path.join(SRC, 'pilot')
sys.path.insert(0, SRC)

import pwg_tm_canonical as C  # noqa: E402
import pwg_tm_gates as G  # noqa: E402


def _frag(src, tgt, klass='sense', fid='t'):
    return {
        'fragment_id': fid,
        'fragment_class': klass,
        'parent_record_id': 'p',
        'source_string': src,
        'source_hash': C.sha256_text(src),
        'target_string': tgt,
        'generation': {
            'model_id': 'grok-4.6',
            'route_id': 'grok-4.6',
            'prompt_sha256': 'a' * 64,
            'pipeline_version': 'pwg_tm_generate.v1',
            'source_hash': C.sha256_text(src),
        },
    }


def test_gaps17_upakrama_german_gloss_fails():
    rec = G.gate_fragment(_frag(
        '4〉 {%Antritt, Anfang, Beginn%}',
        '4〉 {%Antritt, Anfang, Beginn%}',
        fid='upakrama'))
    assert rec['gate_status'] == 'fail'
    assert 'GLOSS-DE-RESIDUE' in rec['hard']


def test_gaps17_atmasat_german_gloss_fails():
    rec = G.gate_fragment(_frag(
        '{#AtmasAt#} {%an sich, zu sich, auf sich%} {%thun%}',
        '{#AtmasAt#} {%an sich, zu sich, auf sich%} {%класть%}',
        fid='AtmasAt'))
    assert 'GLOSS-DE-RESIDUE' in rec['hard']


def test_gaps17_tarura_ab_mutated_fails():
    rec = G.gate_fragment(_frag(
        '<ab>v. a.</ab>', '<ab>т. е.</ab>',
        klass='recurring_formula', fid='taruRa'))
    assert 'AB-MUTATED' in rec['hard']


def test_gaps17_ab_copy_through_passes_ab_identity():
    rec = G.gate_fragment(_frag(
        '<ab>v. a.</ab>', '<ab>v. a.</ab>',
        klass='recurring_formula', fid='taruRa-ok'))
    assert 'AB-MUTATED' not in rec['hard']


def test_gaps17_translated_gloss_is_not_residue():
    rec = G.gate_fragment(_frag('{%Feuer.%}', '{%огонь.%}'))
    assert 'GLOSS-DE-RESIDUE' not in rec['hard']


def test_selftest_includes_gaps17():
    assert G.main(['--selftest']) == 0


def test_coordinator_claim_help_lists_defect_repair():
    proc = subprocess.run(
        [sys.executable, os.path.join(PILOT, 'coordinator.py'), 'claim', '--help'],
        capture_output=True, text=True, encoding='utf-8')
    assert proc.returncode == 0, proc.stderr
    assert 'defect-repair' in proc.stdout


def test_coordinator_claim_defect_repair_requires_keys_and_root():
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, os.path.join(PILOT, 'coordinator.py'),
             '--data-root', tmp,
             'claim', '--kind', 'defect-repair', '--lane', 'pc',
             '--owner', 'h3644-test'],
            capture_output=True, text=True, encoding='utf-8')
        assert proc.returncode != 0
        blob = (proc.stderr or '') + (proc.stdout or '')
        assert 'defect-repair requires --keys' in blob


def test_coordinator_claim_defect_repair_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, os.path.join(PILOT, 'coordinator.py'),
             '--data-root', tmp,
             'claim', '--kind', 'defect-repair', '--lane', 'pc',
             '--owner', 'h3644-test',
             '--root', 'dA',
             '--keys', 'd_a~~h0_02_sec_2,d_a~~h0_05_anu',
             '--lease-id', 'defect-repair-h3644-test'],
            capture_output=True, text=True, encoding='utf-8')
        assert proc.returncode == 0, proc.stderr + proc.stdout
        lease = json.loads(proc.stdout)
        assert lease['kind'] == 'defect-repair'
        assert lease['target'] == 'defect-repair:dA'
        assert lease['details']['no_tm'] is True
        assert lease['details']['keys'] == ['d_a~~h0_02_sec_2', 'd_a~~h0_05_anu']
        assert lease['reserved_keys'] == ['d_a~~h0_02_sec_2', 'd_a~~h0_05_anu']
