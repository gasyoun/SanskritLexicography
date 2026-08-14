#!/usr/bin/env python
"""Blinded cold/warm semantic compare (H2703).

The comparator never receives cold/warm labels. Both outputs are retained
even when they disagree. No paid judge.
"""
from __future__ import annotations

import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import os

HERE = os.path.dirname(os.path.abspath(__file__))
H1210 = os.path.join(HERE, 'h1210')
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if H1210 not in sys.path:
    sys.path.insert(0, H1210)

import cache_identity as ident  # noqa: E402
import det_gate  # noqa: E402


def _canonical(obj):
    return ident.canonical_dumps(obj)


def _sense_count(card):
    if not isinstance(card, dict):
        return 0
    return det_gate.output_sense_count(card)


def _placeholders(card):
    if not isinstance(card, dict):
        return []
    return det_gate.fidelity_tokens(card) + det_gate.translation_tokens(card)


def compare_blind(output_a, output_b):
    """Compare two parsed card objects without cold/warm labels.

    Order is fixed by SHA-256 of the canonical form so the function is
    deterministic and label-blind.
    """
    dump_a = _canonical(output_a)
    dump_b = _canonical(output_b)
    hash_a = ident.sha256_bytes(dump_a)
    hash_b = ident.sha256_bytes(dump_b)
    if hash_a <= hash_b:
        left, right = output_a, output_b
        left_hash, right_hash = hash_a, hash_b
    else:
        left, right = output_b, output_a
        left_hash, right_hash = hash_b, hash_a
    identical = left_hash == right_hash
    left_senses = _sense_count(left)
    right_senses = _sense_count(right)
    left_ph = _placeholders(left)
    right_ph = _placeholders(right)
    return {
        'identical': identical,
        'left_sha256': left_hash,
        'right_sha256': right_hash,
        'sense_count_equal': left_senses == right_senses,
        'placeholder_equal': left_ph == right_ph,
        'left_sense_count': left_senses,
        'right_sense_count': right_senses,
        'class': (
            'identical' if identical
            else 'equivalent_structure' if (
                left_senses == right_senses and left_ph == right_ph)
            else 'disagree'
        ),
    }


def compare_prep_blind(output_a, output_b):
    """Compare two PREP terminal objects (ru_skeleton + route_hint) label-blind."""
    slim_a = {
        'ru_skeleton': (output_a or {}).get('ru_skeleton'),
        'route_hint': (output_a or {}).get('route_hint'),
    }
    slim_b = {
        'ru_skeleton': (output_b or {}).get('ru_skeleton'),
        'route_hint': (output_b or {}).get('route_hint'),
    }
    dump_a = _canonical(slim_a)
    dump_b = _canonical(slim_b)
    hash_a = ident.sha256_bytes(dump_a)
    hash_b = ident.sha256_bytes(dump_b)
    identical = hash_a == hash_b
    route_equal = slim_a['route_hint'] == slim_b['route_hint']
    n_a = len(slim_a['ru_skeleton'] or []) if isinstance(slim_a['ru_skeleton'], list) else 0
    n_b = len(slim_b['ru_skeleton'] or []) if isinstance(slim_b['ru_skeleton'], list) else 0
    return {
        'identical': identical,
        'left_sha256': hash_a if hash_a <= hash_b else hash_b,
        'right_sha256': hash_b if hash_a <= hash_b else hash_a,
        'route_equal': route_equal,
        'skeleton_len_equal': n_a == n_b,
        'left_skeleton_len': n_a if hash_a <= hash_b else n_b,
        'right_skeleton_len': n_b if hash_a <= hash_b else n_a,
        'class': (
            'identical' if identical
            else 'equivalent_structure' if route_equal and n_a == n_b
            else 'disagree'
        ),
    }
