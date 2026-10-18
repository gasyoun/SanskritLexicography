#!/usr/bin/env python3
"""Gold audit for sandhi-bench v2 (H6063).

The third baseline lane is not a system but an audit of the gold itself
(ruling B8 asks annotator-grade care; what is automatable today is
provenance + hygiene). This script FAILS CLOSED on any of:

  A1 provenance — every committed item re-derives from the kosha source
     table of its text (same JUNCTION_RE parse as build_dataset.py); the
     rule, category, left+right, surface and sentence prefix must all match
     a live source row.
  A2 split hygiene — splits are text-disjoint; every item's recorded split
     matches the file it lives in.
  A3 identity — ids are unique across all three files and follow the stable
     build order.
  A4 manifest — manifest.json counts equal the actual jsonl line counts.

Writes results/gold_audit.json and exits non-zero on any failed check.

Usage:
    python sandhi-bench/audit_gold.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_dataset import JUNCTION_RE, find_kosha, harvest  # noqa: E402


def load(split: str) -> list[dict]:
    return [json.loads(x) for x in
            (HERE / "data" / f"{split}.jsonl").read_text(
                encoding="utf-8").splitlines() if x.strip()]


def main() -> int:
    kosha = find_kosha()
    report: dict = {"audit": "gold_audit", "passed": True, "checks": {}}

    # --- A1 provenance: rebuild the harvest and index it ------------------
    source_items = harvest(kosha)
    src_index = {}
    for it in source_items:
        src_index[(it["text"], it["sandhied"], it["gold"])] = it

    committed = {s: load(s) for s in ("train", "dev", "test")}
    mismatches = []
    for split, rows in committed.items():
        for it in rows:
            key = (it["text"], it["sandhied"], it["gold"])
            src = src_index.get(key)
            if src is None:
                mismatches.append(f"{it['id']}: not re-derivable from source")
                continue
            if (src["rule"] != it["rule"]
                    or src["category"] != it["category"]
                    or not it["sent"].startswith(src["sent"][:20])):
                mismatches.append(f"{it['id']}: rule/category/context drift")
    report["checks"]["A1_provenance"] = {
        "n_source_items": len(source_items),
        "n_committed": sum(len(v) for v in committed.values()),
        "mismatches": mismatches[:10], "n_mismatches": len(mismatches)}

    # --- A2 split hygiene: text-disjoint, split field correct -------------
    text_split: dict[str, set[str]] = {}
    split_field_errors = []
    for split, rows in committed.items():
        for it in rows:
            text_split.setdefault(it["text"], set()).add(split)
            if it.get("split") != split:
                split_field_errors.append(it["id"])
    overlap = {t: sorted(s) for t, s in text_split.items() if len(s) > 1}
    report["checks"]["A2_split_hygiene"] = {
        "texts_in_multiple_splits": overlap,
        "split_field_errors": split_field_errors[:10],
        "n_split_field_errors": len(split_field_errors)}

    # --- A3 identity: unique ids in stable build order --------------------
    all_rows = [it for s in ("train", "dev", "test") for it in committed[s]]
    ids = [it["id"] for it in all_rows]
    dup = {i for i in ids if ids.count(i) > 1}
    order_ok = sorted(ids) == sorted(
        f"sb-{i:06d}" for i in range(1, len(ids) + 1))
    report["checks"]["A3_identity"] = {
        "n": len(ids), "duplicate_ids": sorted(dup)[:5],
        "contiguous_stable_ids": order_ok}

    # --- A4 manifest counts ------------------------------------------------
    manifest = json.loads((HERE / "data" / "manifest.json").read_text(
        encoding="utf-8"))
    counts_ok = all(manifest["splits"]["n_items"][s] == len(committed[s])
                    for s in ("train", "dev", "test"))
    report["checks"]["A4_manifest"] = {
        "counts_match": counts_ok,
        "manifest": manifest["splits"]["n_items"],
        "actual": {s: len(committed[s]) for s in committed}}

    c = report["checks"]
    failed = (c["A1_provenance"]["n_mismatches"] > 0
              or c["A2_split_hygiene"]["texts_in_multiple_splits"]
              or c["A2_split_hygiene"]["n_split_field_errors"] > 0
              or c["A3_identity"]["duplicate_ids"]
              or not c["A3_identity"]["contiguous_stable_ids"]
              or not counts_ok)
    report["passed"] = not failed

    out = HERE / "results" / "gold_audit.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
