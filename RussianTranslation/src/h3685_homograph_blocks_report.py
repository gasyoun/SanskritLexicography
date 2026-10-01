#!/usr/bin/env python
"""H3685 - emit the current class1b (cross-subcard homograph) block list from
the live pwg_ru store, for the H3685 close-out report. Reuses
h3500_defect_scan.scan; adds full subcard membership per key1 (the scanner's
class1b_entries only lists the key1, not which subcards collide) and a
schema-validity check on each contributing row (key1/subcard/sense_tag/ru all
present and non-empty - the shape pwg_ru_entry_join.assemble_entry expects).

  python src/h3685_homograph_blocks_report.py [STORE] [--json]
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")

spec = importlib.util.spec_from_file_location(
    "h3500_defect_scan", os.path.join(HERE, "h3500_defect_scan.py"))
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)

REQUIRED_FIELDS = ("key1", "subcard", "sense_tag", "ru")


def build(rows):
    rep = scanner.scan(rows)
    by_key = collections.defaultdict(dict)
    for r in rows:
        ru = (r.get("ru") or "").strip()
        if len(ru) >= 12:
            by_key[r.get("key1")].setdefault(ru, set()).add(r.get("subcard"))

    blocks = []
    invalid_schema = 0
    for k, m in sorted(by_key.items()):
        for ru, cards in m.items():
            if len(cards) <= 1:
                continue
            rows_for_block = [r for r in rows
                               if r.get("key1") == k
                               and (r.get("ru") or "").strip() == ru]
            for r in rows_for_block:
                if not all(r.get(f) not in (None, "") for f in REQUIRED_FIELDS):
                    invalid_schema += 1
            blocks.append({
                "key1": k,
                "subcards": sorted(cards),
                "ru_preview": ru[:80],
            })

    return {
        "rows_in_store": len(rows),
        "class1b_block_count": len(blocks),
        "class1b_schema_invalid_rows": invalid_schema,
        "class1b_class2_leaks_open": len(rep["class2_is_genitive_leaks"]),
        "blocks": blocks,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("store", nargs="?", default=DEFAULT_STORE)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(args.store, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    result = build(rows)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(f"rows_in_store: {result['rows_in_store']}")
        print(f"class1b_block_count: {result['class1b_block_count']}")
        print(f"class1b_schema_invalid_rows: {result['class1b_schema_invalid_rows']}")
        for b in result["blocks"]:
            print(f"  {b['key1']}: subcards={b['subcards']} "
                  f"ru={b['ru_preview']!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
