# -*- coding: utf-8 -*-
r"""Independent verifier recount for `dhatup_multisource_crosswalk.json` (H4478).

Written by the data-class verifier (DeepSeek V4.1 Flash `deepseek/deepseek-v4.1-flash`)
WITHOUT importing the submission's builder: every load-bearing number is re-derived
from the raw workbook with this file's own scanner, then compared against the
committed JSON. Companion of the H4478 `## Verifier` section; H4432's pilot-probe
precedent (a probe that re-derives published numbers without importing the builder).

Checks (18):
  - raw recount: non-blank rows, Palsule entries, per-source filled counts,
    six-witness rows;
  - JSON: row count, Palsule count, counts block, uniform 14-key rows,
    strictly increasing row ids;
  - spot rows: 100/1420/1424 (the doc's) + the 501st/4001st/1001st/3001st
    non-blank rows — every field byte-compared against the raw.

Exit 0 = ALL PASS, 1 = at least one mismatch (printed).

Usage:
  python3 RussianTranslation/src/pilot/dhatup_h4478_verify.py \
      [--xlsx PATH] [--json PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))  # RussianTranslation/
DEFAULT_XLSX = os.path.join(RT, "pwg_ru", "eval", "palsule_yadisk",
                            "Gasuns-Dhātupāṭha-Concordance (Merge_table_Final).xlsm")
DEFAULT_JSON = os.path.join(RT, "src", "data", "dhatup_multisource_crosswalk.json")

SHEET = "Финальная таблица"
FIELDS = ["palsule_root", "palsule_page", "palsule_no",
          "pwg_volcol", "pwg_no", "pwk_volcol", "pwk_no",
          "whitney_root", "whitney_page", "whitney_no",
          "ewa_volcol", "ewa_no", "verba_root"]
WANT = {
    "rows_nonblank": 5183, "palsule_root": 3690, "pwg_volcol": 2390,
    "pwg_no": 1643, "pwk_volcol": 1983, "whitney_root": 1692,
    "whitney_page": 930, "ewa_volcol": 841, "verba_root": 617,
    "six_witness": 178,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--xlsx", default=DEFAULT_XLSX)
    ap.add_argument("--json", dest="json_path", default=DEFAULT_JSON)
    args = ap.parse_args()

    # gitignored corpora may legitimately be absent (H4432 probe precedent:
    # exit 2, never a traceback, so a CI checkout reports the missing input)
    for label, path in (("raw workbook", args.xlsx), ("crosswalk JSON", args.json_path)):
        if not os.path.isfile(path):
            print(f"SKIP: {label} absent — {path}", file=sys.stderr)
            print("exit 2 (corpus absent, not a failure)", file=sys.stderr)
            return 2

    fails = []

    def check(name, got, want):
        ok = got == want
        print(f"{'PASS' if ok else 'FAIL'} {name}: got={got} want={want}")
        if not ok:
            fails.append(name)

    wb = load_workbook(args.xlsx, read_only=True, data_only=True)
    ws = wb[SHEET]
    nonblank = []
    for i, row in enumerate(ws.iter_rows(min_row=4, max_col=len(FIELDS),
                                         values_only=True), start=4):
        vals = [None if v is None else (str(v).strip() or None) for v in row]
        if any(vals):
            nonblank.append((i, vals))
    wb.close()

    def cnt(field):
        idx = FIELDS.index(field)
        return sum(1 for _, v in nonblank if v[idx])

    check("rows_nonblank", len(nonblank), WANT["rows_nonblank"])
    for f in ["palsule_root", "pwg_volcol", "pwg_no", "pwk_volcol",
              "whitney_root", "whitney_page", "ewa_volcol", "verba_root"]:
        check(f, cnt(f), WANT[f])
    six = sum(1 for _, v in nonblank
              if all(v[FIELDS.index(f)] for f in
                     ["palsule_root", "pwg_volcol", "pwk_volcol",
                      "whitney_root", "ewa_volcol", "verba_root"]))
    check("six_witness", six, WANT["six_witness"])

    data = json.load(open(args.json_path, encoding="utf-8"))
    jrows = data["rows"]
    check("json_rows", len(jrows), WANT["rows_nonblank"])
    check("json_palsule_root",
          sum(1 for r in jrows if r["palsule_root"]), WANT["palsule_root"])
    check("json_counts_block",
          data["counts"]["per_source_filled"]["pwg_volcol"], WANT["pwg_volcol"])
    keysets = {tuple(sorted(r.keys())) for r in jrows}
    check("row_keyset_uniform", keysets == {tuple(sorted(["row"] + FIELDS))}, True)
    ids = [r["row"] for r in jrows]
    check("row_ids_increasing",
          ids == sorted(ids) and len(set(ids)) == len(ids), True)

    by_row = {r["row"]: r for r in jrows}
    raw_by_row = dict(nonblank)
    picks = [100, 1420, 1424] + [nonblank[k][0] for k in (500, 4000, 1000, 3000)]
    for rid in picks:
        raw, got = raw_by_row.get(rid), by_row.get(rid)
        if raw is None or got is None:
            check(f"spot_row_{rid}", "missing", "present")
            continue
        mismatch = [f for f, v in zip(FIELDS, raw) if got[f] != v]
        check(f"spot_row_{rid}", mismatch, [])

    print()
    print("VERIFIER RECOUNT:", "ALL PASS" if not fails else f"FAILURES: {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
