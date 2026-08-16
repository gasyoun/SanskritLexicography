#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_relationships.py — Deliverable 1 of H180 (ADDENDA_TYPOLOGY.md).

Populate the `provenance.relationship` typology for every non-`pwg` sub-card in
the layered translated store, and roll it up by (subtype, layer).

Design choices (honour H180 guardrails):
  * NO re-translation, NO workflow/translate call — pure metadata over the
    already-translated store.
  * NON-DESTRUCTIVE: the canonical store `pwg_ru_translated.jsonl` is left
    byte-identical. Relationships are emitted to a *separate sidecar*
    `src/pwg_ru_relationships.jsonl`, keyed by (subcard, sense_tag), which
    REGLUE_SPEC's build_reglue.py consumes. (The typology's "write the sidecar
    back per sub-card" is realised as an external sidecar so the layered store
    stays canonical — the store is the single source of truth for `ru`.)
  * Every instance is `confidence: "llm"` (first-pass, LLM/heuristic-proposed);
    the human gold standard is a separate, later deliverable — never overwrite
    an llm verdict in place.

Inputs  : src/pwg_ru_translated.jsonl
Outputs : src/pwg_ru_relationships.jsonl   (one row per sub-card sense that
          asserts a relationship: every non-`pwg` sense, plus — since H2880
          wave 2 — the `pwg` rows that are corrections to another PWG sense
          rather than senses themselves)
          pwg_ru/relationships_rollup.tsv   (aggregate by subtype/op/direction/layer)

Run: python src/build_relationships.py
"""
import sys, os, io, json, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # RussianTranslation/
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
OUT_JSONL = os.path.join(HERE, "pwg_ru_relationships.jsonl")
OUT_TSV = os.path.join(ROOT, "pwg_ru", "relationships_rollup.tsv")

# H1624 G4: single classifier shared with promote / annotate_edition_rel.
from edition_rel import (
    edition_rel_for_row, build_pwg_gender_index, build_pwg_sense_index,
    pwg_correction_marker, lead_int, homonym_of,
)


def main():
    recs = []
    with io.open(STORE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))

    pwg_gender = build_pwg_gender_index(recs)
    pwg_senses = build_pwg_sense_index(recs)   # H2879: the placement axis

    out = []
    roll = collections.Counter()
    lang_counter = collections.Counter()
    placement_roll = collections.Counter()
    for d in recs:
        layer = d.get("layer")
        if layer == "pwg" and not pwg_correction_marker(d.get("sense_tag")):
            # An ordinary PWG sense asserts no relationship, so it gets no
            # sidecar row — as before. H2880 admits exactly one exception: a row
            # sitting in the skeleton that is really an edit *to* a sense.
            continue
        # confidence "llm" preserved for H180 sheet continuity (heuristic first pass).
        er = edition_rel_for_row(d, pwg_gender, pwg_senses)
        er = dict(er)
        er["confidence"] = "llm"
        # sidecar shape expected by build_reglue / review sheets
        ip = er.get("insertion_point") or {}
        rel = {
            "op": er["op"],
            "target": "grammar" if (ip.get("anchor") == "grammar") else "sense",
            "direction": er["direction"],
            "subtype": er["subtype"],
            # H2879: whether this supplement has an identified target, kept
            # apart from *what kind* of supplement it is. Read `subtype` only
            # together with `placement`.
            "placement": er["placement"],
            "placement_reason": er["placement_reason"],
            "placement_hypothesis": er["placement_hypothesis"],
            "insertion_point": ip,
            "confidence": "llm",
            "evidence": er.get("evidence") or "",
        }
        # H2881: `contains_correction_clause` marks an additive SCH row whose
        # non-leading section carries a correction clause — the residue of the
        # conservative default, kept measurable rather than dropped.
        for k in ("source_lang", "correction_marker",
                  "contains_correction_clause"):
            if k in er:
                rel[k] = er[k]
        if er.get("subtype") == "pwg_internal_correction":
            # H2880: which layer the amending material came from — `pwg` for a
            # Nachtrag, `pwg`+`pw` for a `1 (PW)` row.
            rel["source_layers"] = er.get("source_layers", ["pwg"])
        for k, v in er.items():
            if k.startswith("needs_ru_from_"):
                rel[k] = v
        if er.get("subtype") == "foreign_fragment" and er.get("source_lang"):
            lang_counter[er["source_lang"]] += 1
        out.append({
            "subcard": d["subcard"], "key1": d["key1"],
            "sense_tag": str(d.get("sense_tag")),
            "layer": layer, "relationship": rel,
        })
        roll[(er["subtype"], er["op"], er["direction"], layer)] += 1
        placement_roll[er["placement_reason"]] += 1

    with io.open(OUT_JSONL, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    with io.open(OUT_TSV, "w", encoding="utf-8") as fh:
        fh.write("subtype\top\tdirection\tlayer\tcount\n")
        for (subtype, op, direction, layer), n in sorted(
                roll.items(), key=lambda kv: (-kv[1], kv[0][0])):
            fh.write(f"{subtype}\t{op}\t{direction}\t{layer}\t{n}\n")

    print(f"non-pwg sub-card senses classified : {len(out)}")
    print(f"foreign-fragment languages         : {dict(lang_counter)}")
    print(f"wrote {OUT_JSONL}")
    print(f"wrote {OUT_TSV}")
    placed = placement_roll["found"]
    print(f"placement=true (target identified)  : {placed} "
          f"of {len(out)} ({100.0 * placed / max(len(out), 1):.1f}%)")
    print("placement_reason:")
    for k in ("found", "no_target_marker", "out_of_range", "not_found"):
        print(f"  {k:18s} {placement_roll[k]}")

    print("\nrollup:")
    for (subtype, op, direction, layer), n in sorted(
            roll.items(), key=lambda kv: (-kv[1], kv[0][0])):
        print(f"  {subtype:16s} {op:9s} {direction:9s} {layer:6s} {n}")


if __name__ == "__main__":
    main()