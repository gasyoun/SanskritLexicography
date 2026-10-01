#!/usr/bin/env python3
"""H4475 — derive TSVs from the Sanskrityatina 04_Reverse coding legend.

Source: yadisk:Sanskrityatina/04_Reverse/187992 headwords.txt (ASCII, CRLF,
1,706 bytes) — the coding LEGEND of MG's 187,992-headword reverse-dictionary
stock (Schwarz-based, sources IEG/PD/BHS/MW/SCH), NOT the headword list
itself: 1 total/class-0 line + 23 subclass lines + 3 attested example
headwords in an ASCII fence.

Outputs (beside this file's parent, LF, UTF-8, idempotent):
  - sanskrityatina_reverse_index_coding_classes.tsv
      class_code <TAB> headwords <TAB> description <TAB> is_stock_total
  - sanskrityatina_reverse_index_examples.tsv
      headword_slp1 <TAB> headword_iast <TAB> form_key <TAB> cdsl_key
      <TAB> exact_key <TAB> sources <TAB> rev_class <TAB> source_page_ref
      (source_page_ref is EMPTY by construction — the legend carries no
      page/column refs; the SCH XML research cases do, and are a separate
      census line, per the H4475 mission)
  - provenance.json (fetch facts, sha256, counts, arithmetic checks)

The raw txt stays gitignored (raw/.gitignore); this script + the committed
derived outputs + provenance.json are the auditable record.

Usage:
  python3 tools/h4475_build_reverse_index.py [--raw PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # .../sanskrityatina/
SANSKRIT_UTIL_CANDIDATES = [
    HERE / ".." / ".." / ".." / "sanskrit-util" / "py",   # sibling-clone default
    Path.home() / "Documents" / "GitHub" / "sanskrit-util" / "py",
]

_CLASS_RE = re.compile(r"^(\d+)\s+headwords coded as (\S+):\s*(.+?)\s*$")
_EXAMPLE_RE = re.compile(r"^([A-Za-z0-9]+):([A-Za-z][A-Za-z,]*)$")


def _import_sanskrit_util():
    try:
        import sanskrit_util  # noqa: F401
        return sanskrit_util
    except ImportError:
        pass
    for cand in SANSKRIT_UTIL_CANDIDATES:
        cand = cand.resolve()
        if cand.is_dir():
            sys.path.insert(0, str(cand))
            try:
                import sanskrit_util  # noqa: F401
                return sanskrit_util
            except ImportError:
                sys.path.pop(0)
    raise SystemExit(
        "Could not import sanskrit_util — clone https://github.com/gasyoun/sanskrit-util "
        "to ~/Documents/GitHub/sanskrit-util (H3222 sibling-clone layout).")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(HERE / "raw" / "187992 headwords.txt"))
    args = ap.parse_args()

    su = _import_sanskrit_util()
    raw = Path(args.raw)
    if not raw.is_file():
        raise SystemExit(f"raw legend not found: {raw}\n"
                         "refetch: rclone copy 'yadisk:Sanskrityatina/04_Reverse/"
                         "187992 headwords.txt' raw/")
    text = raw.read_text(encoding="ascii")            # ASCII, CRLF — decode is exact
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # -- parse class lines ---------------------------------------------------
    classes: list[dict] = []
    examples: list[tuple[str, str]] = []
    in_fence = False
    for ln in lines:
        if ln.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            m = _EXAMPLE_RE.match(ln)
            if m:
                examples.append((m.group(1), m.group(2)))
            continue
        m = _CLASS_RE.match(ln)
        if m:
            classes.append({"headwords": int(m.group(1)),
                            "class_code": m.group(2),
                            "description": m.group(3)})

    if not classes:
        raise SystemExit("no 'N headwords coded as X:' lines parsed — format drift?")
    stock_total = classes[0]["headwords"]              # line 1: '187992 ... as 0'
    subclass_sum = sum(c["headwords"] for c in classes[1:])
    if classes[0]["class_code"] != "0" or classes[0]["headwords"] != stock_total:
        raise SystemExit("first class line is not the stock-total class-0 line")

    # -- transcode the example headwords via sanskrit-util --------------------
    ex_rows = []
    for slp1, sources in examples:
        iast = su.from_slp1(slp1)                      # SLP1 -> IAST (raises on bad input)
        ex_rows.append({
            "headword_slp1": slp1,
            "headword_iast": iast,
            "form_key": su.slp1_form_key(slp1),        # form_key ∘ from_slp1 (house key)
            "cdsl_key": su.slp1_norm(slp1),            # CDSL headword key
            "exact_key": su.norm(iast),                # diacritic-insensitive lookup key
            "sources": sources,
            "rev_class": "0",                          # legend examples are stock examples
            "source_page_ref": "",                     # ABSENT in the legend by construction
        })

    # -- write outputs (LF, deterministic) ------------------------------------
    cls_tsv = HERE / "sanskrityatina_reverse_index_coding_classes.tsv"
    with cls_tsv.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("class_code\theadwords\tdescription\tis_stock_total\n")
        for i, c in enumerate(classes):
            fh.write(f"{c['class_code']}\t{c['headwords']}\t{c['description']}\t"
                     f"{1 if i == 0 else 0}\n")

    ex_tsv = HERE / "sanskrityatina_reverse_index_examples.tsv"
    with ex_tsv.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("headword_slp1\theadword_iast\tform_key\tcdsl_key\texact_key\t"
                 "sources\trev_class\tsource_page_ref\n")
        for r in ex_rows:
            fh.write("\t".join(r[k] for k in
                               ("headword_slp1", "headword_iast", "form_key",
                                "cdsl_key", "exact_key", "sources", "rev_class",
                                "source_page_ref")) + "\n")

    sha = hashlib.sha256(raw.read_bytes()).hexdigest()
    prov = {
        "dataset": "sanskrityatina-reverse-index",
        "source_file": "yadisk:Sanskrityatina/04_Reverse/187992 headwords.txt",
        "source_size_bytes": raw.stat().st_size,
        "source_mtime_utc": "2017-05-16T06:59:05Z",    # rclone lsjson ModTime (UTC) at fetch time
        "source_sha256": sha,
        "source_encoding": "ASCII, CRLF line terminators",
        "fetched_at_utc": "2026-09-10T20:25Z",   # constant: keeps provenance.json idempotent
        "fetched_by": "H4475 (OxAlpha, opencode glm-5.3-flash), rclone yadisk:",
        "builder": "ReverseDictionary/sanskrityatina/tools/h4475_build_reverse_index.py",
        "sanskrit_util_version": getattr(su, "__version__", "unknown"),
        "counts": {
            "stock_total_class0": stock_total,
            "class_lines_total": len(classes),
            "class_lines_excl_total": len(classes) - 1,
            "subclass_headword_sum": subclass_sum,
            "subclass_sum_minus_stock": subclass_sum - stock_total,
            "example_headwords": len(ex_rows),
        },
        "notes": [
            "The file is the CODING LEGEND of the 187,992-headword stock, not the "
            "stock itself: class 0 ('in two or more dictionaries') carries the whole "
            "stock; the 23 subclass lines sum to more than the stock, i.e. classes "
            "OVERLAP (delta recorded in counts.subclass_sum_minus_stock).",
            "source_page_ref is empty by construction — page/column refs exist only "
            "in the sibling SCH XML research cases (separate census line, mission).",
        ],
    }
    (HERE / "provenance.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # -- verify ---------------------------------------------------------------
    for name in (cls_tsv, ex_tsv, HERE / "provenance.json"):
        if not name.is_file() or name.stat().st_size == 0:
            raise SystemExit(f"output missing/empty: {name}")
    print(f"classes parsed      : {len(classes)} (1 stock-total + {len(classes)-1} subclasses)")
    print(f"stock total (code 0): {stock_total}")
    print(f"subclass sum        : {subclass_sum} (overlap delta {subclass_sum - stock_total})")
    print(f"examples transcoded : {len(ex_rows)} via sanskrit-util "
          f"from_slp1/slp1_form_key/slp1_norm/norm")
    print(f"source sha256       : {sha[:16]}…")
    print("OK: 2 TSVs + provenance.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
