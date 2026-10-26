"""Focused H7299 canaries for E47 PD and consumer corroboration labels."""
from __future__ import annotations

import json

import pytest

from conftest import REPO, load_module

reaudit = load_module("data/witness_independence_reaudit.py")
extension = load_module("data/witness_independence_pd_extension.py")


def test_baseline_partitions_and_apte_are_unchanged():
    policies = {pid: cmap for pid, _l, _n, cmap in reaudit.build_policies()}
    assert policies["P0"] == {d: d for d in reaudit.ALL_DICTS}
    assert policies["P3"]["AP"] == "AP"
    assert all(policies["P3"][d] == "PETERSBURG" for d in ("PWG", "PWK", "MW"))
    assert policies["P4"]["MD"] == "PETERSBURG"
    assert policies["P2"]["SKD"] != policies["P2"]["VCP"]


def test_pd_is_a_separate_family_at_every_rung():
    policies = extension.policies16()
    assert [len(set(cmap.values())) for _p, _l, _n, cmap in policies] == [16, 15, 13, 12, 11]
    for _pid, _label, _note, cmap in policies:
        assert cmap["PD"] == "PD"
        assert cmap["AP"] == "AP"


def test_distribution_distinguishes_replication_from_confirmation():
    rows = [("x", ["PWG", "PWK", "MW"], 3), ("y", ["PWG", "AP"], 2)]
    p0 = reaudit.distribution(rows, reaudit.build_policies()[0][3])
    p3 = reaudit.distribution(rows, reaudit.build_policies()[3][3])
    assert p0 == {2: 1, 3: 1}
    assert p3 == {1: 1, 2: 1}


def test_n_dictionaries_is_not_n_independent_witnesses():
    with pytest.raises(ValueError, match="STOP_CANARY_MISMATCH"):
        extension.validate_claim({
            "evidence_class": "cross-family-confirmation",
            "dictionaries": ["PWG", "PWK", "MW"],
            "independent_witnesses": 3,
        })
    assert extension.validate_claim({
        "evidence_class": "within-family-replication",
        "dictionaries": ["PWG", "PWK", "MW"],
        "independent_witnesses": 1,
    }) == 1


def test_pd_and_apte_cross_family_confirmation():
    assert extension.validate_claim({
        "evidence_class": "cross-family-confirmation",
        "dictionaries": ["PD", "PWG", "AP"],
        "independent_witnesses": 3,
    }) == 3


def test_inventory_cannot_claim_textual_attestation():
    with pytest.raises(ValueError, match="STOP_CANARY_MISMATCH"):
        extension.validate_claim({
            "evidence_class": "inventory",
            "dictionaries": ["PD"],
            "independent_witnesses": 1,
        })


def test_chronology_is_one_lineage_and_committed_canaries_hold():
    metadata = extension.PD_E47_EXTENSION
    lineage = metadata["chronology_lineages"][0]
    assert lineage["independent_confirmations"] == 1
    assert lineage["spearman_rho"] == 0.94 and lineage["shared_works"] == 56
    contract = json.loads(extension.CONTRACT.read_text(encoding="utf-8"))
    for canary in contract["canaries"]:
        if canary["expect"] == "accept":
            extension.validate_claim(canary["claim"])
        else:
            with pytest.raises(ValueError):
                extension.validate_claim(canary["claim"])


def test_real_extension_output_is_current():
    _rows, _policies, _dists, computed = extension.recompute()
    committed = json.loads(extension.OUT_JSON.read_text(encoding="utf-8"))
    assert computed == committed
    assert computed["pd_inventory"]["evidence_scope"] == "inventory-only"
    assert computed["pd_inventory"]["single_dictionary_unique"] == 93462
