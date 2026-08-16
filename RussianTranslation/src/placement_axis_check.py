#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""placement_axis_check.py — acceptance gate for the placement axis (H2879).

Re-runnable proof of the criteria in
``docs/VERIFICATION_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md``. Two of
them (A3, A5) are *stop conditions*, not merely checks: if they fail, the
normalisation has attached a supplement to a sense that was never identified,
which is a quieter and worse defect than the one wave 1 removes.

Reads the store and the sidecar; writes nothing.

Run: python src/placement_axis_check.py [--store-sha <sha256>]
"""
import argparse
import collections
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
REL = os.path.join(HERE, "pwg_ru_relationships.jsonl")

from edition_rel import (  # noqa: E402
    build_pwg_sense_index, homonym_of, lead_int, normalize_sense_tag,
    _max_numeric_sense,
)

REASONS = ("found", "no_target_marker", "out_of_range", "not_found")


def sha256_of(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path):
    out = []
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store-sha", default=None,
                    help="expected sha256 of the canonical store (A5)")
    ap.add_argument("--store-rows", type=int, default=None,
                    help="expected row count of the canonical store (A5)")
    args = ap.parse_args()

    store = read_jsonl(STORE)
    rel = read_jsonl(REL)
    senses = build_pwg_sense_index(store)

    failures = []
    notes = []

    def fail(tag, msg):
        failures.append("%s: %s" % (tag, msg))

    # ---- A5 — canonical store untouched --------------------------------
    sha = sha256_of(STORE)
    print("A5  store rows=%d sha256=%s" % (len(store), sha))
    if args.store_rows is not None and len(store) != args.store_rows:
        fail("A5", "store row count %d != expected %d — canonical data was "
                   "touched; STOP" % (len(store), args.store_rows))
    if args.store_sha and sha != args.store_sha:
        fail("A5", "store sha256 changed — canonical data was touched; STOP")

    # ---- A2 — placement=true only on a sense that really exists ---------
    bad_true = []
    for r in rel:
        rr = r["relationship"]
        if not rr.get("placement"):
            continue
        ip = rr.get("insertion_point") or {}
        key = (r.get("key1") or "", ip.get("homonym", "h0"))
        nt = normalize_sense_tag(ip.get("target_sense"))
        if nt not in senses.get(key, set()):
            bad_true.append((r.get("subcard"), r.get("sense_tag"), nt))
    print("A2  placement=true rows whose target is absent from PWG: %d"
          % len(bad_true))
    if bad_true:
        fail("A2", "%d rows claim a target that does not exist, e.g. %r"
                   % (len(bad_true), bad_true[:5]))

    # ---- A3 — normalisation attached nothing that had no target ---------
    # A row whose OWN sense_tag carries no leading number had target '*new'
    # before wave 1 and must still be unplaced. This is the stop condition.
    leaked = []
    for r in rel:
        rr = r["relationship"]
        if not rr.get("placement"):
            continue
        st = str(r.get("sense_tag"))
        if lead_int(st) is None:
            leaked.append((r.get("subcard"), st))
        elif r.get("layer") == "nws" and st.strip().lower().startswith("nws"):
            leaked.append((r.get("subcard"), st))
    print("A3  rows that were '*new' and are now placed: %d" % len(leaked))
    if leaked:
        fail("A3", "STOP — normalisation promoted %d unplaceable rows, e.g. %r"
                   % (len(leaked), leaked[:5]))

    # ---- A4 — out_of_range is stable and correctly derived --------------
    reasons = collections.Counter(
        r["relationship"].get("placement_reason") for r in rel)
    print("A4  placement_reason: " + " · ".join(
        "%s=%d" % (k, reasons[k]) for k in REASONS))
    unknown = set(reasons) - set(REASONS)
    if unknown:
        fail("A4", "placement_reason outside the contract: %r" % sorted(unknown))
    # every out_of_range must really exceed the article's normalised maximum
    bad_oor = []
    for r in rel:
        rr = r["relationship"]
        if rr.get("placement_reason") != "out_of_range":
            continue
        ip = rr.get("insertion_point") or {}
        key = (r.get("key1") or "", ip.get("homonym", "h0"))
        nt = normalize_sense_tag(ip.get("target_sense"))
        mx = _max_numeric_sense(senses.get(key, set()))
        if not (nt.isdigit() and mx is not None and int(nt) > mx):
            bad_oor.append((r.get("subcard"), nt, mx))
    print("A4  out_of_range rows that do NOT exceed the article maximum: %d"
          % len(bad_oor))
    if bad_oor:
        fail("A4", "%d misfiled out_of_range rows, e.g. %r"
                   % (len(bad_oor), bad_oor[:5]))

    # ---- hypothesis must never leak into fact ---------------------------
    leaks = []
    for r in rel:
        rr = r["relationship"]
        hyp = rr.get("placement_hypothesis")
        if not hyp:
            continue
        if rr.get("placement"):
            leaks.append(("placed with a hypothesis", r.get("subcard")))
        ip = rr.get("insertion_point") or {}
        if str(ip.get("target_sense")) == str(hyp.get("target")):
            leaks.append(("hypothesis reached insertion_point", r.get("subcard")))
    n_hyp = sum(1 for r in rel if r["relationship"].get("placement_hypothesis"))
    print("HYP placement_hypothesis rows: %d · leaks into fact: %d"
          % (n_hyp, len(leaks)))
    if leaks:
        fail("HYP", "a guess was promoted to a fact: %r" % leaks[:5])

    # ---- A9 — every sidecar row carries the axis ------------------------
    missing = [r.get("subcard") for r in rel
               if "placement" not in r["relationship"]
               or "placement_reason" not in r["relationship"]]
    print("A9  sidecar rows missing the placement fields: %d" % len(missing))
    if missing:
        fail("A9", "%d rows have no placement axis, e.g. %r"
                   % (len(missing), missing[:5]))

    # ---- A1 — an unplaced row asserts nothing about a sense -------------
    # Structural half: no unplaced row may keep a target that resolves.
    asserting = []
    for r in rel:
        rr = r["relationship"]
        if rr.get("placement"):
            continue
        ip = rr.get("insertion_point") or {}
        nt = normalize_sense_tag(ip.get("target_sense"))
        key = (r.get("key1") or "", ip.get("homonym", "h0"))
        if nt != "*new" and nt in senses.get(key, set()):
            asserting.append((r.get("subcard"), nt))
    print("A1  placement=false rows whose target nonetheless resolves: %d"
          % len(asserting))
    if asserting:
        fail("A1", "%d unplaced rows still point at a real sense, e.g. %r"
                   % (len(asserting), asserting[:5]))

    print()
    if failures:
        for f in failures:
            print("FAIL " + f, file=sys.stderr)
        return 1
    for n in notes:
        print("note: " + n)
    print("placement_axis_check: OK (%d sidecar rows, %d placed)"
          % (len(rel), reasons["found"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
