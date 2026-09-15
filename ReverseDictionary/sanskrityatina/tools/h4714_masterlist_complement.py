#!/usr/bin/env python3
"""H4714 -- Sanskrityatina reverse stock as ReverseDictionary master-list
complement (census A9, xwalk lane).

Join the keyed sanskrityatina-sch-cases slice (16,304 SCH-experimental
cases, H4533 -- the only per-headword sanskrityatina data that exists; the
reverse-index legend is a 24-line class SUMMARY whose 187,992-headword
stock has no per-headword list, reverse-index meta backlog item 2)
against the canonical ReverseDictionary master list
(`266820-reverse-Gasuns.txt`, 266,820 data lines, IAST,
`SOURCE<TAB>word`, local-only -- H736 durable copy under pwg-ru-data).

Join key, identical pipeline both sides via sanskrit-util:
  sch-cases : form_key column as committed (= slp1_form_key(key1_slp1))
  master    : slp1_form_key(to_slp1(word))          (word = LAST TSV field,
                                                     source column may be empty)

Outputs (beside the datasets, LF, UTF-8, deterministic/idempotent):
  sanskrityatina_sch_cases_masterlist_join.tsv
      all sch-case rows + `in_master` (1/0), committed input order
  sanskrityatina_sch_cases_masterlist_complement.tsv
      the complement -- in_master=0 rows only (candidates the master list
      is missing within this slice)
  H4714_HAND_SAMPLE_20.tsv
      deterministic stratified 20-row hand-verification sample
      (10 in-master + 10 complement, stride-sampled across case classes)
  sanskrityatina_masterlist_complement_provenance.json
      inputs + sha256, counts, per-case_class coverage, caveats

Usage:
  python3 tools/h4714_masterlist_complement.py [--master PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent.parent          # .../sanskrityatina/
SANSKRIT_UTIL_CANDIDATES = [
    HERE / ".." / ".." / ".." / "sanskrit-util" / "py",   # sibling-clone default
    Path.home() / "Documents" / "GitHub" / "sanskrit-util" / "py",
]
DEFAULT_MASTER = (
    Path.home() / "Documents" / "GitHub" / "pwg-ru-data" / "durable"
    / "reverse-dictionary" / "266820-reverse-Gasuns.txt"
)

JOIN_TSV = HERE / "sanskrityatina_sch_cases_masterlist_join.tsv"
COMPLEMENT_TSV = HERE / "sanskrityatina_sch_cases_masterlist_complement.tsv"
SAMPLE_TSV = HERE / "H4714_HAND_SAMPLE_20.tsv"
PROVENANCE = HERE / "sanskrityatina_masterlist_complement_provenance.json"

SCH_COLS = ("key1_slp1", "key2_accented", "iast", "form_key", "case_class",
            "L", "pc", "source_xml")
OUT_COLS = SCH_COLS + ("in_master",)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_master_keys(master_path: Path):
    """word = LAST tab field (source column may be empty). Returns
    (set_of_form_keys, total_data_lines, key_dupes, unmapped_words)."""
    from sanskrit_util import SLP1_ALPHABET, slp1_form_key, to_slp1  # noqa: PLC0415

    keys: set[str] = set()
    key_counts: Counter = Counter()
    n_lines = 0
    unmapped = Counter()
    allowed = set(SLP1_ALPHABET)  # uppercase IS legitimate SLP1 (z=ṣ, S=ś, T=th)
    with master_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if not line:
                continue
            n_lines += 1
            word = line.split("\t")[-1].strip()
            if not word:
                continue
            slp1 = to_slp1(word)
            # to_slp1 maps unmapped characters to themselves; a survivor
            # outside the SLP1 alphabet (c-cedilla scheme variants etc.)
            # cannot key-match a clean sch-case form_key -- counted, not
            # silently dropped.
            if any(c not in allowed for c in slp1):
                unmapped[word] += 1
            k = slp1_form_key(slp1)
            keys.add(k)
            key_counts[k] += 1
    dupes = sum(1 for v in key_counts.values() if v > 1)
    return keys, n_lines, dupes, unmapped


def stride_pick(rows: list[dict], want: int) -> list[dict]:
    if len(rows) <= want:
        return list(rows)
    step = len(rows) / want
    return [rows[min(int(i * step), len(rows) - 1)] for i in range(want)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", type=Path, default=DEFAULT_MASTER,
                    help="canonical 266820 master list (default: H736 "
                         "durable copy under pwg-ru-data)")
    args = ap.parse_args()

    for cand in SANSKRIT_UTIL_CANDIDATES:
        if cand.is_dir():
            sys.path.insert(0, str(cand))
            break
    else:
        print("FATAL: sanskrit-util sibling clone not found", file=sys.stderr)
        return 2

    if not args.master.is_file():
        print(f"FATAL: master list not found: {args.master}", file=sys.stderr)
        return 2

    # -- inputs ------------------------------------------------------------
    sch_path = HERE / "sanskrityatina_sch_cases.tsv"
    legend_path = HERE / "sanskrityatina_reverse_index_coding_classes.tsv"
    legend: dict[str, int] = {}
    with legend_path.open(encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3 and p[0]:
                legend[p[0]] = int(p[1].replace(",", ""))

    master_keys, n_master_lines, master_dupe_keys, master_unmapped = \
        load_master_keys(args.master)

    rows: list[dict] = []
    with sch_path.open(encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        assert tuple(header) == SCH_COLS, f"unexpected sch TSV header: {header}"
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != len(SCH_COLS):
                continue
            rows.append(dict(zip(SCH_COLS, parts)))

    for r in rows:
        r["in_master"] = "1" if r["form_key"] in master_keys else "0"

    # -- write join + complement (input order, byte-stable) ----------------
    for out in (JOIN_TSV, COMPLEMENT_TSV, SAMPLE_TSV, PROVENANCE):
        tmp = out.with_suffix(out.suffix + ".tmp")
        tmp.write_text("", encoding="utf-8")  # truncate now, stream later
        tmp.unlink()

    with JOIN_TSV.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(OUT_COLS) + "\n")
        for r in rows:
            fh.write("\t".join(r[c] for c in OUT_COLS) + "\n")

    complement = [r for r in rows if r["in_master"] == "0"]
    with COMPLEMENT_TSV.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(OUT_COLS) + "\n")
        for r in complement:
            fh.write("\t".join(r[c] for c in OUT_COLS) + "\n")

    # -- deterministic stratified 20-row hand sample ------------------------
    hit = [r for r in rows if r["in_master"] == "1"]
    sample = stride_pick(hit, 10) + stride_pick(complement, 10)
    with SAMPLE_TSV.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(OUT_COLS) + "\n")
        for r in sample:
            fh.write("\t".join(r[c] for c in OUT_COLS) + "\n")

    # -- coverage -----------------------------------------------------------
    by_class: Counter = Counter(r["case_class"] for r in rows)
    by_class_hit: Counter = Counter(r["case_class"] for r in rows
                                    if r["in_master"] == "1")
    coverage_by_class = {
        c: {"cases": by_class[c], "in_master": by_class_hit[c],
            "complement": by_class[c] - by_class_hit[c],
            "coverage_pct": round(100.0 * by_class_hit[c] / by_class[c], 2)
            if by_class[c] else 0.0}
        for c in sorted(by_class)
    }
    stock = legend.get("0", 0)

    prov = {
        "handoff": "H4714",
        "generated": "15-09-2026",
        "executor": "OxAlpha (opencode/z-ai/glm-5.3-flash)",
        "join_key": "sanskrit-util slp1_form_key (sch-cases committed column "
                    "= slp1_form_key(key1_slp1); master = "
                    "slp1_form_key(to_slp1(last TSV field)))",
        "inputs": {
            "master_list": {
                "path": str(args.master),
                "sha256": sha256(args.master),
                "data_lines": n_master_lines,
                "unique_form_keys": len(master_keys),
                "form_keys_with_multiple_raw_words": master_dupe_keys,
                "words_with_unmapped_characters": dict(master_unmapped) or {},
            },
            "sch_cases_tsv": {
                "path": str(sch_path),
                "sha256": sha256(sch_path),
                "rows": len(rows),
            },
            "legend_coding_classes_tsv": {
                "path": str(legend_path),
                "stock_class_0_headwords": stock,
            },
        },
        "results": {
            "sch_cases_total": len(rows),
            "in_master": len(rows) - len(complement),
            "complement": len(complement),
            "coverage_pct": round(
                100.0 * (len(rows) - len(complement)) / len(rows), 2)
            if rows else 0.0,
            "coverage_by_case_class": coverage_by_class,
        },
        "caveats": [
            "The legend's 187,992-headword stock (class 0) has NO "
            "per-headword list in the registered dataset (reverse-index "
            "meta backlog item 2) -- row-level complement is measured on "
            "the 16,304-case SCH-experimental slice only; the legend "
            "contributes class-level context, not join rows.",
            "master words carrying unmapped characters (c-cedilla scheme "
            "variants etc.) are counted, not matched.",
            "Empty first field in the master list (131,916 lines have no "
            "source code) -- word is always the LAST tab field.",
        ],
    }
    PROVENANCE.write_text(json.dumps(prov, ensure_ascii=False, indent=2,
                                     sort_keys=False) + "\n",
                          encoding="utf-8")

    # -- summary ------------------------------------------------------------
    print(f"master lines           : {n_master_lines}")
    print(f"master unique form_keys: {len(master_keys)} "
          f"({master_dupe_keys} keys from >1 raw word)")
    print(f"sch cases              : {len(rows)}")
    print(f"  in master            : {len(rows) - len(complement)} "
          f"({prov['results']['coverage_pct']}%)")
    print(f"  complement           : {len(complement)}")
    print(f"legend stock (class 0) : {stock}")
    for c, v in coverage_by_class.items():
        print(f"  {c:<14} {v['in_master']:>6}/{v['cases']:<6} "
              f"complement {v['complement']}")
    if master_unmapped:
        total_unmapped = sum(master_unmapped.values())
        print(f"master unmapped-char words: {total_unmapped} "
              f"(counted, not matched)")
    print("OK: join + complement + hand sample + provenance written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
