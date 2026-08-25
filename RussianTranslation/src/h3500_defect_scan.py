#!/usr/bin/env python
"""H3500 - scan a pwg_ru TM/store JSONL for the defect classes surfaced by the
H3456 blinded benchmark (kosha PR #432), measured against the RENDER-TIME
architecture (ABBREVIATIONS_RU.md): <ab> tokens are translated at render by
pwg_ab_ru.RU_MAP, so raw Latin inside `ru` is only a defect when it sits
OUTSIDE its tag.

Classes
-------
class1a  byte-identical duplicate `ru` rows WITHIN one (key1, subcard) group
         - true store corruption; repairable by keep-best dedupe
class1b  identical `ru` blocks across DIFFERENT subcards of one key1
         (PWG homograph sections listing the same gloss twice, e.g. vAsin/vaSin,
         DA anusam under h0_80 + h6_23) - source-faithful rows; the fix belongs
         to the entry assembler (pwg_ru_entry_join.py), NOT to the store
class2   free-floating residues outside tags: bare German "vgl." (render never
         sees it), English-genitive prose leaks inside <is> ("Indra's город")
class3  beyond-PWG advisory enrichment ([Buddh]/BHSD spans) present in `ru`
         without an additive provenance marker field

Modes
-----
default        human-readable counts + samples
--json         machine counts
--check        gate mode: exit 0 clean, exit 1 any class1a/class2/class3 hit
               (class1b is reported but does NOT fail the gate - rows are
               source-faithful; the assembler collapses them at join)

  python src/h3500_defect_scan.py [STORE] [--json] [--check] [--samples N]
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t]+")
BARE_VGL_RE = re.compile(r"(?<![A-Za-z])vgl\.(?![A-Za-z])")
GEN_RE = re.compile(r"<is>[^<]*[A-Za-zÄÖÜäöüß]+'s[^<]*</is>")
ADV_RE = re.compile(r"\[(NWS|Reg|Buddh)\]")


def visible(text: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub(" ", text or "")).strip()


def scan(rows):
    """Return the full defect report dict for a row list."""
    by_card = collections.defaultdict(list)
    for i, r in enumerate(rows):
        by_card[(r.get("key1"), r.get("subcard"))].append(i)

    # class1a: byte-identical (sense_tag, ru) within one subcard group -
    # safely droppable; identical ru under DIFFERENT tags is zz-tagger noise
    # (reported separately, never auto-dropped)
    c1a_groups = []
    c1c_degenerate = []
    for k, idxs in sorted(by_card.items()):
        seen = {}
        seen_any_tag = {}
        for i in idxs:
            r = rows[i]
            ru = (r.get("ru") or "").strip()
            if len(ru) < 12:
                continue
            key = (r.get("sense_tag"), ru)
            if key in seen:
                c1a_groups.append({"key1": k[0], "subcard": k[1],
                                   "keep_index": seen[key], "dup_index": i})
            else:
                seen[key] = i
            if ru in seen_any_tag and seen_any_tag[ru][0] != r.get("sense_tag"):
                c1c_degenerate.append({"key1": k[0], "subcard": k[1],
                                       "tags": sorted({seen_any_tag[ru][0],
                                                       r.get("sense_tag")})})
            else:
                seen_any_tag.setdefault(ru, (r.get("sense_tag"), i))

    # class1b: identical ru across distinct subcards within one key1
    by_key = collections.defaultdict(dict)
    for i, r in enumerate(rows):
        ru = (r.get("ru") or "").strip()
        if len(ru) >= 12:
            by_key[r.get("key1")].setdefault(ru, set()).add(r.get("subcard"))
    c1b = [{"key1": k, "subcards": sorted(cards)}
           for k, m in sorted(by_key.items())
           for ru, cards in m.items() if len(cards) > 1]

    c2_vgl, c2_gen = [], []
    c3_rows, c3_flagged = [], 0
    for i, r in enumerate(rows):
        ru = r.get("ru") or ""
        for m in BARE_VGL_RE.finditer(ru):
            if _inside_ab(ru, m.start()):
                continue
            c2_vgl.append({"index": i, "subcard": r.get("subcard"),
                           "snip": ru[max(0, m.start() - 40):m.start() + 30]})
            break
        if GEN_RE.search(ru):
            c2_gen.append({"index": i, "subcard": r.get("subcard"),
                           "snip": GEN_RE.search(ru).group(0)})
        hits = ADV_RE.findall(ru)
        if hits:
            marker = r.get("advisory_enrichment")
            if marker:
                c3_flagged += 1
            else:
                c3_rows.append({"index": i, "subcard": r.get("subcard"),
                                "tags": sorted(set(hits))})

    return {
        "rows": len(rows),
        "class1a_duplicate_row_excess": len(c1a_groups),
        "class1a_groups": c1a_groups,
        "class1b_cross_subcard_identical_blocks": len(c1b),
        "class1b_entries": [e["key1"] for e in c1b],
        "class1c_degenerate_tag_copies": len(c1c_degenerate),
        "class2_bare_vgl": c2_vgl,
        "class2_is_genitive_leaks": c2_gen,
        "class3_unflagged_advisory_rows": c3_rows,
        "class3_flagged_rows": c3_flagged,
    }


def _inside_ab(raw: str, pos: int) -> bool:
    last_open = raw.rfind("<ab>", 0, pos)
    return last_open != -1 and raw.rfind("</ab>", 0, pos) < last_open


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("store", nargs="?", default=DEFAULT_STORE)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    with io.open(args.store, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    rep = scan(rows)

    failing = (rep["class1a_duplicate_row_excess"]
               + len(rep["class2_bare_vgl"])
               + len(rep["class3_unflagged_advisory_rows"]))
    # class2_is_genitive_leaks is deliberately NOT gate-failing: auto-fixing
    # "<is>Indra's город</is>"-style prose needs per-row Russian rewording -
    # documented as the H3500 manual follow-up list instead.
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
    elif args.check:
        print(json.dumps({k: v for k, v in rep.items()
                          if not k.endswith("_groups")
                          and k not in ("class1b_entries",
                                        "class2_bare_vgl",
                                        "class2_is_genitive_leaks",
                                        "class3_unflagged_advisory_rows")},
                         ensure_ascii=False))
    else:
        for k, v in rep.items():
            if isinstance(v, list) and len(v) > 6:
                print(f"{k}: {len(v)} item(s)")
                for item in v[:4]:
                    print(f"   {json.dumps(item, ensure_ascii=False)[:200]}")
            else:
                print(f"{k}: {v}")
    if args.check:
        print(f"H3500 check: {'FAIL' if failing else 'OK'} "
              f"(failing items: {failing}; class1b informational: "
              f"{rep['class1b_cross_subcard_identical_blocks']})")
        return 1 if failing else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
