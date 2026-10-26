#!/usr/bin/env python3
"""Fail-closed canaries for the H7299 E47 PD/chronology extension."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from witness_independence_pd_extension import (
    ALL_DICTS16,
    CONTRACT,
    OUT_JSON,
    PD_E47_EXTENSION,
    recompute,
    validate_claim,
)
from witness_independence_reaudit import ALL_DICTS, build_policies

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(f"STOP_CANARY_MISMATCH: {message}")


def main():
    tiers = json.loads((HERE / "witness_tiers.json").read_text(encoding="utf-8"))
    for pid, _label, _note, cmap in build_policies():
        require(tiers["policies"][pid]["map"] == cmap, f"baseline {pid} partition changed")
    require(tiers["policies"]["P0"]["map"] == {d: d for d in ALL_DICTS}, "P0 is not identity")
    require(tiers["policies"]["P3"]["map"]["AP"] == "AP", "Apte was folded")
    require(all(tiers["policies"]["P3"]["map"][d] == "PETERSBURG" for d in ("PWG", "PWK", "MW")), "Petersburg ruling changed")

    extension = tiers["extensions"]["H7299"]
    require(extension == PD_E47_EXTENSION, "map and generator extension metadata differ")
    relation = extension["dictionary_relations"][0]
    require(relation["family_id"] == "DECCAN_PD" and relation["collapse_at"] is None, "PD is not independent")
    require(relation["source"] and relation["confidence"], "PD relation lacks source/confidence")
    lineage = extension["chronology_lineages"][0]
    require(lineage["members"] == ["DCS", "Dharmamitra"], "chronology members changed")
    require(lineage["independent_confirmations"] == 1, "second chronology confirmation claimed")
    require((lineage["spearman_rho"], lineage["shared_works"]) == (0.94, 56), "chronology evidence changed")

    _rows, policies, _dists, computed = recompute()
    committed = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    require(computed == committed, "committed extension output is stale")
    require(computed["union"]["p0_matches_n_dicts"], "16-dict P0 mismatch")
    require(computed["baseline_15_preserved"]["p0_corroborated_share"] == 0.559, "55.9% baseline lost")
    require(computed["baseline_15_preserved"]["p3_corroborated_share"] == 0.347, "34.7% baseline lost")
    for pid, _label, _note, cmap in policies:
        require(cmap["PD"] == "PD", f"PD folded at {pid}")
        require(len(cmap) == 16, f"PD absent at {pid}")

    inventory = computed["pd_inventory"]
    require(inventory["headwords"] == 104962, "PD denominator changed")
    require(inventory["single_dictionary_unique"] == 93462, "PD unique inventory changed")
    require(inventory["evidence_scope"] == "inventory-only", "PD inventory promoted to attestation")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for canary in contract["canaries"]:
        try:
            validate_claim(canary["claim"])
        except ValueError:
            require(canary["expect"] == "reject", f"valid canary rejected: {canary['id']}")
        else:
            require(canary["expect"] == "accept", f"invalid canary accepted: {canary['id']}")

    with (HERE / "witness_independence_pd_clusters.tsv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    require(len(rows) == 5 * len(ALL_DICTS16), "cluster output incomplete")
    print("PASS: baseline P0/P1/P2/P3/P4 maps preserved; PD independent at every rung")
    print("PASS: DCS/Dharmamitra = one chronology lineage (rho=0.94, 56 works)")
    print("PASS: PD 93,462/104,962 unique = inventory-only; consumer canaries reject N dicts = N witnesses")


if __name__ == "__main__":
    main()
