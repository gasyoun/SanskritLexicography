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

H3300: every row also carries a UNIQUE `row_key` (`"<subcard>::<sense_tag>#<n>"`)
plus its `dup_ordinal` — the 0-based occurrence of that `(subcard, sense_tag)`
pair in store order. The store itself repeats pairs (149 pairs, 722 rows today),
and until H3300 every consumer that built a dict keyed on the bare pair silently
dropped all but the last row (FINDINGS §551: 133 pairs, 468 of 6,009 rows
shadowed on the wave-1 baseline). Readers join on `row_key`/`dup_ordinal` when
present and stay tolerant of legacy rows without them.

Run: python src/build_relationships.py
"""
import sys, os, io, json, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # RussianTranslation/
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")

# H3300: the sidecar is gitignored, local-only runtime data belonging to the MAIN
# checkout — exactly like the canonical store (store_path.py, the H255 class of
# loss). A linked-worktree run must refresh the persistent copy, not vanish with
# the worktree; readers resolve the same way, so writer and readers agree.
from store_path import canonical_store, main_worktree_root          # noqa: E402

_MAIN = main_worktree_root(HERE)
STORE = canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))
OUT_JSONL = (os.path.join(_MAIN, "RussianTranslation", "src",
                          "pwg_ru_relationships.jsonl") if _MAIN
             else os.path.join(HERE, "pwg_ru_relationships.jsonl"))
OUT_TSV = ((os.path.join(_MAIN, "RussianTranslation", "pwg_ru",
                         "relationships_rollup.tsv")) if _MAIN
           else os.path.join(ROOT, "pwg_ru", "relationships_rollup.tsv"))

# H1624 G4: single classifier shared with promote / annotate_edition_rel.
from edition_rel import (
    edition_rel_for_row, build_pwg_gender_index, build_pwg_sense_index,
    pwg_correction_marker, lead_int, homonym_of,
)


def row_key(subcard, sense_tag, ordinal):
    """The unique H3300 key for one sidecar row."""
    return "%s::%s#%d" % (subcard, sense_tag, ordinal)


def classify_store(recs):
    """Classify every qualifying store row -> (out, roll, placement_roll, dup_pairs).

    The single writer loop, extracted so the H3300 selftest exercises exactly
    what `main()` writes and nothing else.
    """
    pwg_gender = build_pwg_gender_index(recs)
    pwg_senses = build_pwg_sense_index(recs)   # H2879: the placement axis

    out = []
    roll = collections.Counter()
    lang_counter = collections.Counter()
    placement_roll = collections.Counter()
    # H3300: occurrence ordinal per (subcard, sense_tag) pair, in store order —
    # the disambiguator readers join back on. Counted over ALL qualifying rows
    # so writer and every reader compute the same number from the same file.
    pair_seen = collections.Counter()
    dup_pairs = collections.Counter()
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
        pair = (d["subcard"], str(d.get("sense_tag")))
        ordinal = pair_seen[pair]
        pair_seen[pair] += 1
        if ordinal:                       # not the first occurrence
            dup_pairs[pair] = pair_seen[pair]
        out.append({
            "subcard": d["subcard"], "key1": d["key1"],
            "sense_tag": str(d.get("sense_tag")),
            # H3300: unique row identity + the join disambiguator.
            "row_key": row_key(pair[0], pair[1], ordinal),
            "dup_ordinal": ordinal,
            "layer": layer, "relationship": rel,
        })
        roll[(er["subtype"], er["op"], er["direction"], layer)] += 1
        placement_roll[er["placement_reason"]] += 1
    return out, roll, placement_roll, dup_pairs, lang_counter


def main():
    recs = []
    with io.open(STORE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))

    out, roll, placement_roll, dup_pairs, lang_counter = classify_store(recs)

    with io.open(OUT_JSONL, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    with io.open(OUT_TSV, "w", encoding="utf-8") as fh:
        fh.write("subtype\top\tdirection\tlayer\tcount\n")
        for (subtype, op, direction, layer), n in sorted(
                roll.items(), key=lambda kv: (-kv[1], kv[0][0])):
            fh.write(f"{subtype}\t{op}\t{direction}\t{layer}\t{n}\n")

    print(f"non-pwg sub-card senses classified : {len(out)}")
    # H3300 shadow census: pairs are still allowed to repeat (that is a fact of
    # the store, which stays untouched); what must go to zero is rows being
    # UNREACHABLE in consumers — every row now carries its unique `row_key`.
    n_dup_rows = sum(v for v in dup_pairs.values())
    print(f"(subcard, sense_tag) duplicate pairs : {len(dup_pairs)} "
          f"({n_dup_rows} rows live under them; each carries a unique row_key)")
    print(f"unique row_keys                      : {len(set(r['row_key'] for r in out))} of {len(out)}")
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


# --------------------------------------------------------------------- selftest
def selftest():
    """H3300: the writer's key contract over a synthetic duplicated-pair store."""
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # A store whose PW sub-card repeats one (subcard, sense_tag) pair 3x — the
    # FINDINGS §551 shape (worst real case was 25 rows under one pair).
    recs = [
        {"key1": "x", "subcard": "x~~h0_00_pwg00", "layer": "pwg",
         "sense_tag": "1", "de": "<lex>m.</lex> {%x%}"},
        {"key1": "x", "subcard": "x~~h0_zz_pw01", "layer": "pw",
         "sense_tag": "1", "de": "{%erstes%}"},
        {"key1": "x", "subcard": "x~~h0_zz_pw01", "layer": "pw",
         "sense_tag": "1", "de": "{%zweites%}"},
        {"key1": "x", "subcard": "x~~h0_zz_pw01", "layer": "pw",
         "sense_tag": "1", "de": "{%drittes%}"},
        {"key1": "x", "subcard": "x~~h0_zz_sch01", "layer": "sch",
         "sense_tag": "2", "de": "{%neu%}"},
    ]
    out, _roll, _placement_roll, dup_pairs, _lang = classify_store(recs)

    check(len(out) == 4, "one sidecar row per qualifying store row (%d)" % len(out))
    keys = [r["row_key"] for r in out]
    check(len(set(keys)) == len(keys), "row_keys are unique across the sidecar")
    dup = [r for r in out if r["subcard"] == "x~~h0_zz_pw01"
           and r["sense_tag"] == "1"]
    check([r["dup_ordinal"] for r in dup] == [0, 1, 2],
          "dup_ordinal counts occurrences in store order: %r"
          % [r["dup_ordinal"] for r in dup])
    check(all(r["row_key"] == row_key(r["subcard"], r["sense_tag"],
                                      r["dup_ordinal"]) for r in out),
          "row_key is exactly row_key(subcard, sense_tag, dup_ordinal)")
    check(list(dup_pairs) == [("x~~h0_zz_pw01", "1")],
          "the repeated pair is reported: %r" % dict(dup_pairs))
    # a single-occurrence pair still gets ordinal 0 — uniform shape, no special case
    solo = [r for r in out if r["layer"] == "sch"][0]
    check(solo["dup_ordinal"] == 0 and solo["row_key"].endswith("#0"),
          "first occurrence of every pair carries ordinal 0")
    print("build_relationships selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())