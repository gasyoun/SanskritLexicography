#!/usr/bin/env python3
"""H7299: additive PD/chronology extension of the E47 witness map.

Consumes the committed 16-dictionary union as-is; never rebuilds it. The
15-dictionary H1363 policies remain the regression baseline. PD is a separate
family at every rung, while DCS/Dharmamitra are registered as one chronology
lineage outside the dictionary-witness count.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from witness_independence_reaudit import (
    ALL_DICTS16,
    PD_E47_EXTENSION,
    build_policies,
    cumulative_ge,
    distribution,
    load_union,
)

HERE = Path(__file__).resolve().parent
DEFAULT_UNION = HERE.parent / "HeadwordLists/union-16dicts/union_headwords_16.tsv"
OUT_TSV = HERE / "witness_independence_pd_extension.tsv"
OUT_CLUSTERS = HERE / "witness_independence_pd_clusters.tsv"
OUT_JSON = HERE / "witness_independence_pd_extension.json"
CONTRACT = HERE / "witness_corroboration_contract.json"


def policies16():
    """The H1363 ladder plus independent PD, with accurate 16-dict labels."""
    result = []
    for pid, _label, note, cmap in build_policies(ALL_DICTS16):
        n = len(set(cmap.values()))
        labels = {
            "P0": f"published ({n} dictionary inventories)",
            "P1": f"same-work collapse ({n} clusters)",
            "P2": f"editorial-lineage collapse ({n} clusters)",
            "P3": f"FINDINGS §83/§97 ruling + independent PD ({n} clusters)",
            "P4": f"strict + MD; PD remains independent ({n} clusters)",
        }
        result.append((pid, labels[pid], note, cmap))
    return result


def claim_families(claim, policy="P3"):
    """Map a consumer claim's dictionary codes to independent family IDs."""
    cmap = next(item[3] for item in build_policies(ALL_DICTS16) if item[0] == policy)
    unknown = sorted(set(claim.get("dictionaries", [])) - set(cmap))
    if unknown:
        raise ValueError(f"unknown dictionaries: {','.join(unknown)}")
    return {cmap[d] for d in claim.get("dictionaries", [])}


def validate_claim(claim, policy="P3"):
    """Enforce the machine consumer contract; return the derived family count.

    Dictionary count is never accepted as independent-witness count. Inventory
    claims describe listings only; replication requires one family; confirmation
    requires at least two. A mismatch is a canary failure, not a warning.
    """
    evidence_class = claim.get("evidence_class")
    if evidence_class not in {
        "inventory", "within-family-replication", "cross-family-confirmation"
    }:
        raise ValueError("STOP_CANARY_MISMATCH: missing/invalid evidence_class")
    families = claim_families(claim, policy)
    dictionaries = claim.get("dictionaries", [])
    if evidence_class == "inventory":
        if "independent_witnesses" in claim:
            raise ValueError("STOP_CANARY_MISMATCH: inventory is not attestation")
        return len(families)
    if evidence_class == "within-family-replication" and (
        len(dictionaries) < 2 or len(families) != 1
    ):
        raise ValueError("STOP_CANARY_MISMATCH: invalid within-family replication")
    if evidence_class == "cross-family-confirmation" and len(families) < 2:
        raise ValueError("STOP_CANARY_MISMATCH: no cross-family confirmation")
    if claim.get("independent_witnesses") != len(families):
        raise ValueError("STOP_CANARY_MISMATCH: dictionaries != independent witnesses")
    return len(families)


def recompute(union_path=DEFAULT_UNION):
    rows = list(load_union(union_path))
    policies = policies16()
    dists = {pid: distribution(rows, cmap) for pid, _l, _n, cmap in policies}
    p0_hist = Counter(n for _s, _codes, n in rows)
    if dict(dists["P0"]) != dict(p0_hist):
        raise ValueError("STOP_CANARY_MISMATCH: 16-dict P0 differs from n_dicts")

    pd_rows = [codes for _s, codes, _n in rows if "PD" in codes]
    pd_unique = sum(set(codes) == {"PD"} for codes in pd_rows)
    pd_total = len(pd_rows)
    inventory = PD_E47_EXTENSION["pd_inventory"]
    if (pd_total, pd_unique) != (
        inventory["headwords"], inventory["single_dictionary_unique"]
    ):
        raise ValueError("STOP_CANARY_MISMATCH: PD inventory fact drift")

    total = len(rows)
    summaries = {}
    for pid, label, _note, cmap in policies:
        dist = dists[pid]
        singles = dist.get(1, 0)
        corroborated = total - singles - dist.get(0, 0)
        summaries[pid] = {
            "label": label,
            "clusters": len(set(cmap.values())),
            "single_witness": singles,
            "corroborated": corroborated,
            "corroborated_share": round(corroborated / total, 6),
            "newly_single_vs_p0": singles - dists["P0"].get(1, 0),
            "map": cmap,
        }
    return rows, policies, dists, {
        "schema_version": "e47-pd-extension.v1",
        "handoff": "H7299",
        "union": {"headwords": total, "dictionaries": 16, "p0_matches_n_dicts": True},
        "baseline_15_preserved": {
            "p0_corroborated_share": 0.559,
            "p3_corroborated_share": 0.347,
            "apte_family": "AP",
            "petersburg": ["PWG", "PWK", "SCH", "MW", "MD"],
        },
        "policies": summaries,
        "delta_p0_to_p3": {
            "corroborated": summaries["P3"]["corroborated"] - summaries["P0"]["corroborated"],
            "corroborated_share": round(
                summaries["P3"]["corroborated_share"] - summaries["P0"]["corroborated_share"], 6
            ),
            "newly_single": summaries["P3"]["newly_single_vs_p0"],
        },
        "pd_inventory": {**inventory, "single_dictionary_unique_share": round(pd_unique / pd_total, 6)},
        "chronology_lineages": PD_E47_EXTENSION["chronology_lineages"],
    }


def write_outputs(rows, policies, dists, summary):
    with OUT_CLUSTERS.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(["policy", "dict", "cluster"])
        for pid, _label, _note, cmap in policies:
            for dictionary in ALL_DICTS16:
                writer.writerow([pid, dictionary, cmap[dictionary]])
    with OUT_TSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(["policy", "n_clusters_max", "n_witnesses", "headwords", "cum_ge", "cum_ge_share"])
        for pid, _label, _note, cmap in policies:
            dist = dists[pid]
            cum, total = cumulative_ge(dist)
            for n in sorted(dist):
                writer.writerow([pid, len(set(cmap.values())), n, dist[n], cum[n], f"{cum[n]/total:.4f}"])
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--union", type=Path, default=DEFAULT_UNION)
    args = parser.parse_args()
    rows, policies, dists, summary = recompute(args.union)
    write_outputs(rows, policies, dists, summary)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for canary in contract["canaries"]:
        try:
            validate_claim(canary["claim"])
        except ValueError:
            if canary["expect"] == "reject":
                continue
            raise
        if canary["expect"] == "reject":
            raise ValueError(f"STOP_CANARY_MISMATCH: accepted {canary['id']}")
    print(f"PASS: {summary['union']['headwords']} union rows; P0 matches n_dicts")
    for pid in ("P0", "P3"):
        row = summary["policies"][pid]
        print(f"{pid}: corroborated={row['corroborated']} share={row['corroborated_share']:.1%}")
    print(f"PD inventory-only unique: {summary['pd_inventory']['single_dictionary_unique']} "
          f"({summary['pd_inventory']['single_dictionary_unique_share']:.1%})")
    print(f"wrote {OUT_TSV.name}, {OUT_CLUSTERS.name}, {OUT_JSON.name}")


if __name__ == "__main__":
    main()
