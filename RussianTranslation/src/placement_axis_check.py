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

# H3300: both inputs live in the MAIN checkout (gitignored); resolving them
# relative to HERE made this gate unrunnable — and the sheet unverifiable — in
# any linked worktree, i.e. exactly the sanctioned workflow.
from store_path import canonical_store, main_worktree_root          # noqa: E402

STORE = canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))
_MAIN = main_worktree_root(HERE)
REL = (os.path.join(_MAIN, "RussianTranslation", "src",
                    "pwg_ru_relationships.jsonl") if _MAIN
       else os.path.join(HERE, "pwg_ru_relationships.jsonl"))

from edition_rel import (  # noqa: E402
    build_pwg_sense_index, homonym_of, lead_int, normalize_sense_tag,
    pwg_correction_marker, sch_correction_marker, _max_numeric_sense,
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

    # ---- W2 — PWG-internal corrections (H2880) --------------------------
    w2 = [r for r in rel
          if r["relationship"].get("subtype") == "pwg_internal_correction"]
    w2_reasons = collections.Counter(
        r["relationship"].get("placement_reason") for r in w2)
    w2_placed = sum(1 for r in w2 if r["relationship"].get("placement"))
    print("W2  pwg_internal_correction rows: %d · placed %d (%.1f%%) · %s"
          % (len(w2), w2_placed, 100.0 * w2_placed / max(len(w2), 1),
             " ".join("%s=%d" % (k, w2_reasons[k]) for k in REASONS)))

    # W2a — every such row really sits on the pwg layer and really carries a
    # marker. A row pulled out of the skeleton without a named printed cue
    # would be an invented relationship, not a recorded one.
    bad_w2 = [r.get("subcard") for r in w2
              if r.get("layer") != "pwg"
              or not pwg_correction_marker(r.get("sense_tag"))]
    print("W2a corrections with no marker or wrong layer: %d" % len(bad_w2))
    if bad_w2:
        fail("W2a", "%d rows classified as PWG-internal without a marker, e.g. %r"
                    % (len(bad_w2), bad_w2[:5]))

    # W2b — STOP: a correction must never be its own target, nor the target of
    # another correction. The skeleton index excludes them; this proves it.
    self_ref = []
    for r in w2:
        rr = r["relationship"]
        if not rr.get("placement"):
            continue
        ip = rr.get("insertion_point") or {}
        nt = normalize_sense_tag(ip.get("target_sense"))
        if pwg_correction_marker(nt):
            self_ref.append((r.get("subcard"), r.get("sense_tag"), nt))
    print("W2b corrections placed onto another correction: %d" % len(self_ref))
    if self_ref:
        fail("W2b", "STOP — %d corrections target a correction, e.g. %r"
                    % (len(self_ref), self_ref[:5]))

    # W2c — no correction tag may survive in the skeleton index, or it would
    # still be offered to supplements as an ordinary PWG sense.
    stray = sorted({t for tags in senses.values() for t in tags
                    if pwg_correction_marker(t)})
    print("W2c correction tags still in the skeleton index: %d" % len(stray))
    if stray:
        fail("W2c", "%d correction tags are still senses, e.g. %r"
                    % (len(stray), stray[:5]))

    # W2d — an `op` of correct/delete renders as a struck-through cancellation
    # in build_reglue. A Nachtrag amends its sense; it does not withdraw it.
    miscast = [r.get("subcard") for r in w2
               if r["relationship"].get("op") in ("correct", "delete")]
    print("W2d corrections that would render as cancellations: %d" % len(miscast))
    if miscast:
        fail("W2d", "%d corrections would be struck through as cancelled, e.g. %r"
                    % (len(miscast), miscast[:5]))

    # ---- W3 — SCH corrections and cancellations (H2881) ------------------
    sch = [r for r in rel if r.get("layer") == "sch"]
    w3 = [r for r in sch if r["relationship"].get("subtype")
          in ("sch_correct", "sch_cancel")]
    w3_kinds = collections.Counter(
        r["relationship"].get("subtype") for r in w3)
    print("W3  sch rows: %d · corrective %d (%.1f%%) · %s"
          % (len(sch), len(w3), 100.0 * len(w3) / max(len(sch), 1),
             " ".join("%s=%d" % (k, w3_kinds[k])
                      for k in ("sch_correct", "sch_cancel"))))

    # W3a — the layer must be ABLE to be corrective. This is the whole point of
    # wave 3: before it, `sch` could only come out additive, so "SCH only
    # supplements" was a property of the classifier, not a measurement. If this
    # ever returns to zero, the claim has silently become unfalsifiable again.
    if not w3:
        fail("W3a", "no SCH row is corrective — the layer is structurally "
                    "additive again, so the claim is unmeasured, not measured")

    # W3b — every corrective SCH row must name the printed cue that convicted
    # it, and that cue must still be findable in the row's DE. A row pulled out
    # of the additive class without a reproducible printed instruction is an
    # invented relationship, not a recorded one.
    # H3300: DE fetched by the pair's occurrence ordinal, not bare pair —
    # duplicated pairs must not show each other's body to this gate.
    de_by_key = {}
    _seen = collections.Counter()
    for d in store:
        if (d.get("layer") or "") == "sch":
            k = (d.get("subcard"), str(d.get("sense_tag")))
            de_by_key[k + (_seen[k],)] = d.get("de")
            de_by_key[k] = d.get("de")          # legacy fallback view
            _seen[k] += 1
    bad_w3 = []
    for r in w3:
        marker = r["relationship"].get("correction_marker")
        de = de_by_key.get((r.get("subcard"), str(r.get("sense_tag")),
                            r.get("dup_ordinal")))
        if de is None:
            de = de_by_key.get((r.get("subcard"), str(r.get("sense_tag"))))
        if not marker or sch_correction_marker(de) is None:
            bad_w3.append((r.get("subcard"), marker))
    print("W3a corrective SCH rows with no reproducible printed cue: %d"
          % len(bad_w3))
    if bad_w3:
        fail("W3b", "%d corrective rows cite no cue, e.g. %r"
                    % (len(bad_w3), bad_w3[:5]))

    # W3c — STOP: the criterion is a speech act, not a keyword. These strings
    # are real additive SCH text ('Ind. St.' = Indische Studien; 'metrisch
    # statt'; 'vgl.'). A cue set that fires on them would convict ~11 rows that
    # add material of withdrawing it — a louder lie than the one wave 3 fixes.
    decoys = (
        "Mit {%vi, vyāpta%} 4. in allem enthalten, <ls>Ind. St. 9,137.</ls>",
        "{%mā gantum arhasi%} metrisch statt {%na gan˚%},2,116,5.",
        "Statt dessen {%vipācayati%} 281,158.",
        "Mit {%upapra%}, vgl. <ls>Pischel, Ved. Stud. I,72.</ls>",
    )
    fired = [d for d in decoys if sch_correction_marker(d) is not None]
    print("W3c look-alike additive strings wrongly convicted: %d" % len(fired))
    if fired:
        fail("W3c", "STOP — the cue set matches descriptive text: %r" % fired)

    # W3d — an SCH edit renders as a cancellation, deliberately unlike wave 2's
    # `amend`: 'lies X' and 'streiche Y' really do withdraw the printed reading.
    miscast = [r.get("subcard") for r in w3
               if r["relationship"].get("op") not in ("correct", "delete")]
    print("W3d SCH edits that would NOT render as a cancellation: %d"
          % len(miscast))
    if miscast:
        fail("W3d", "%d SCH edits render as ordinary additions, e.g. %r"
                    % (len(miscast), miscast[:5]))

    # W3e — the conservative residue: rows kept additive although a non-leading
    # section carries a correction clause. Reported, never silently dropped.
    residue = [r.get("subcard") for r in sch
               if r["relationship"].get("contains_correction_clause")]
    print("W3e additive SCH rows carrying a non-leading correction clause: %d"
          % len(residue))
    if residue:
        notes.append("W3e %d SCH rows keep a correction clause in a "
                     "non-leading section and stay additive by the "
                     "conservative default: %r" % (len(residue), residue))

    # ---- W7 — sidecar key uniqueness (H3300, FINDINGS §551) --------------
    # §551: 133 `(subcard, sense_tag)` pairs repeated in the sidecar, so every
    # consumer that built a dict on the bare pair silently dropped all but the
    # last row (468 of 6,009 rows on the wave-1 baseline; worst case 25:1).
    # The fix is writer-side: every row now carries `row_key` (unique) +
    # `dup_ordinal` (the pair's occurrence index in store order), and readers
    # join on it. Pairs still repeat — that is a fact of the untouched store;
    # what must never come back is a row without its own key.
    pair_counts = collections.Counter(
        (r.get("subcard"), str(r.get("sense_tag"))) for r in rel)
    dup_pairs = {k: v for k, v in pair_counts.items() if v > 1}
    rows_under_dups = sum(dup_pairs.values())
    print("W7  sidecar rows=%d · duplicate pairs=%d · rows under them=%d"
          % (len(rel), len(dup_pairs), rows_under_dups))

    no_key = [r for r in rel if "row_key" not in r or "dup_ordinal" not in r]
    print("W7a rows missing row_key/dup_ordinal: %d" % len(no_key))
    if no_key:
        fail("W7a", "%d rows carry no unique key (pre-H3300 sidecar? "
                    "regenerate with src/build_relationships.py), e.g. %r"
             % (len(no_key), [r.get("subcard") for r in no_key[:5]]))
    else:
        keys = collections.Counter(r["row_key"] for r in rel)
        colliding = {k: v for k, v in keys.items() if v > 1}
        print("W7a colliding row_keys: %d" % len(colliding))
        if colliding:
            fail("W7a", "%d row_keys are not unique, e.g. %r"
                 % (len(colliding), list(colliding)[:5]))
        malformed = [
            r["row_key"] for r in rel
            if r["row_key"] != "%s::%s#%d" % (r.get("subcard"),
                                              r.get("sense_tag"),
                                              r["dup_ordinal"])]
        print("W7a malformed row_keys: %d" % len(malformed))
        if malformed:
            fail("W7a", "%d row_keys disagree with (subcard, sense_tag, "
                        "dup_ordinal), e.g. %r" % (len(malformed),
                                                   malformed[:5]))

    # W7b — the ordinals must be exactly the file-order occurrence counts of
    # each pair: that is the whole join contract readers rely on.
    bad_ord = []
    seen_ord = collections.Counter()
    for r in rel:
        k = (r.get("subcard"), str(r.get("sense_tag")))
        if r.get("dup_ordinal") != seen_ord[k]:
            bad_ord.append((r["row_key"] if "row_key" in r else k,
                            r.get("dup_ordinal"), seen_ord[k]))
        seen_ord[k] += 1
    print("W7b ordinals out of sequence: %d" % len(bad_ord))
    if bad_ord:
        fail("W7b", "%d dup_ordinals do not count occurrences in file order, "
                    "e.g. %r" % (len(bad_ord), bad_ord[:5]))

    # W7c — the shadow census, restated against consumers: with unique keys in
    # place nothing is unreachable, but the number stays printed so the
    # published before/after (§551: 468 shadowed on the wave-1 baseline → 0)
    # keeps reconciling on every future run.
    by_layer = collections.Counter()
    for r in rel:
        k = (r.get("subcard"), str(r.get("sense_tag")))
        if dup_pairs.get(k):
            by_layer[r.get("layer")] += 1
    print("W7c rows under duplicate pairs by layer: "
          + (" ".join("%s=%d" % kv for kv in sorted(by_layer.items()))
             or "(none)"))

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
