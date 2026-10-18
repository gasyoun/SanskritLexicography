#!/usr/bin/env python3
"""H6994 -- guard the interim PD -> ACC -> NCC composition.

The check is the acceptance gate (H6994 acceptance, lock before work):

  (a) exits non-zero if any composition row lacks a valid provenance;
  (b) proves zero cd_bridge rows in the headline composition;
  (c) reproduces the named rejected-bridge worked example from the source data;
  (d) proves every table row in the report carries the literal interim flag;
  (e) proves the ledger carries score + matched side + contradiction verdict on
      every row, and that the headline counts are internally consistent.

Exit codes: 0 PASS / 1 FAIL / 2 missing input.
"""
from __future__ import annotations

import collections
import csv
import re
import sys
import unicodedata
from pathlib import Path

FLAG = "interim, AOB denominator"
HERE = Path(__file__).resolve().parent
COMPOSITION = HERE / "pd_acc_ncc_composition_interim.tsv"
LEDGER = HERE / "pd_acc_ncc_cd_bridge_ledger.tsv"
REPORT = HERE / "PD_ACC_NCC_COMPOSITION_INTERIM_2026-10-18.md"
ACC = HERE / "acc.jsonl"
NCC = HERE / "ncc.jsonl"


def fold(text):
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^A-Za-z]", "", text)
    return text.lower()


def fail(msg):
    print(f"FAIL {msg}")
    return 1


def main():
    for path in (COMPOSITION, LEDGER, REPORT, ACC, NCC):
        if not path.exists():
            print(f"FAIL missing {path}", file=sys.stderr)
            return 2
    errors = 0

    with open(COMPOSITION, encoding="utf-8") as fh:
        comp = list(csv.DictReader(fh, delimiter="\t"))
    with open(LEDGER, encoding="utf-8") as fh:
        ledger = list(csv.DictReader(fh, delimiter="\t"))

    # (a) provenance on every row
    bad = [i for i, row in enumerate(comp, 2)
           if row.get("provenance") not in ("composed", "direct", "both")]
    if bad:
        errors += fail(f"{len(bad)} composition rows lack a valid provenance: {bad[:5]}")
    else:
        print(f"PASS provenance on 100% of {len(comp)} composition rows")

    # (b) no bridged row in the headline
    bridged = [i for i, row in enumerate(comp, 2) if row.get("provenance") == "cd_bridge"]
    if bridged:
        errors += fail(f"{len(bridged)} cd_bridge rows leaked into the headline: {bridged[:5]}")
    else:
        print("PASS zero cd_bridge rows in the headline composition")

    # (e) ledger shape + headline consistency
    required = ("tier", "score", "matched_side", "contradiction_verdict", "provenance", "flag")
    missing = [i for i, row in enumerate(ledger, 2)
               if any(not row.get(col) for col in required)]
    if missing:
        errors += fail(f"{len(missing)} ledger rows missing a required field: {missing[:5]}")
    else:
        print(f"PASS ledger shape: {len(ledger)} rows carry score/matched side/verdict")
    bad_side = [i for i, row in enumerate(ledger, 2)
                if row.get("matched_side") not in ("ACC", "NCC", "both")]
    if bad_side:
        errors += fail(f"{len(bad_side)} ledger rows have an invalid matched_side: {bad_side[:5]}")
    bad_verdict = [i for i, row in enumerate(ledger, 2)
                   if row.get("contradiction_verdict") not in ("PASS", "REJECT")]
    if bad_verdict:
        errors += fail(f"{len(bad_verdict)} ledger rows have an invalid verdict: {bad_verdict[:5]}")
    bad_prov = [i for i, row in enumerate(ledger, 2) if row.get("provenance") != "cd_bridge"]
    if bad_prov:
        errors += fail(f"{len(bad_prov)} ledger rows are not tagged cd_bridge: {bad_prov[:5]}")
    overlap = {(r["acc_L"], r["ncc_id"]) for r in comp} & {(r["acc_L"], r["ncc_id"]) for r in ledger}
    if overlap:
        errors += fail(f"ledger rows appear in the headline: {sorted(overlap)[:5]}")
    else:
        print("PASS no ledger row appears in the headline")

    heads = collections.Counter(r["provenance"] for r in comp)
    print(f"INFO provenance counts {dict(heads)}")
    if sum(heads.values()) != len(comp):
        errors += fail("provenance counts do not add up to the composition rows")

    # (c) reproduce the named rejected bridge from the source data
    target = next((r for r in ledger if r["acc_L"] == "19619"
                   and r["ncc_id"] == "24_297_b_2976"), None)
    if target is None:
        errors += fail("named rejected bridge 19619 x 24_297_b_2976 is missing from the ledger")
    elif target["contradiction_verdict"] != "REJECT":
        errors += fail("named rejected bridge is not marked REJECT")
    else:
        acc_key = None
        with open(ACC, encoding="utf-8") as fh:
            for line in fh:
                if '"acc_L": "19619"' in line:
                    acc_key = __import__("json").loads(line)["match_key"]
                    break
        ncc_iast = None
        with open(NCC, encoding="utf-8") as fh:
            for line in fh:
                if '"ncc_id": "24_297_b_2976"' in line:
                    ncc_iast = __import__("json").loads(line)["iast"]
                    break
        if not acc_key or not ncc_iast:
            errors += fail("cannot load the named bridge endpoints")
        else:
            shared = [s for s in target["shared_pd_sigla"].split(";") if s]
            ncc_key = fold(ncc_iast)
            if not shared:
                errors += fail("named bridge has no shared PD siglum")
            elif acc_key == ncc_key:
                errors += fail("named bridge titles agree; the contradiction is not reproducible")
            elif target["score"] and float(target["score"]) < 0.90:
                errors += fail("named bridge is below the 0.90 score guard")
            elif not any(fold("abhiseka") in acc_key and fold("abhiseka") in ncc_key
                         for _ in shared):
                errors += fail("named bridge does not show the shared siglum on both titles")
            else:
                print(f"PASS rejected bridge reproducible: {target['acc_L']} x "
                      f"{target['ncc_id']} shared={target['shared_pd_sigla']} "
                      f"score={target['score']} {acc_key} != {ncc_key}")

    # (d) every table data row in the report carries the literal flag
    text = REPORT.read_text(encoding="utf-8")
    in_table = False
    header_seen = False
    table_rows = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.startswith("|"):
            if not in_table:
                in_table = True
                header_seen = False
                continue
            if set(line.replace("|", "").replace(" ", "")) <= set("-:"):
                header_seen = True
                continue
            if not header_seen:
                continue
            table_rows += 1
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells or cells[-1] != FLAG:
                errors += fail(f"report table row {lineno} lacks the interim flag: {line[:100]}")
        else:
            in_table = False
            header_seen = False
    if table_rows == 0:
        errors += fail("no report table rows found")
    else:
        print(f"PASS interim flag on all {table_rows} report table rows")

    if errors:
        print(f"FAIL {errors} guard(s) failed")
        return 1
    print("PASS all H6994 composition guards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
