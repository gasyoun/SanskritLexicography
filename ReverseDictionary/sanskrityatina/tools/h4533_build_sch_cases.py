#!/usr/bin/env python3
"""H4533 -- derive a keyed TSV from the Sanskrityatina 04_Reverse/Experimental
SCH-experimental XML research cases (census: H4475 SS4).

Source: yadisk:Sanskrityatina/04_Reverse/Experimental/ -- six UTF-16LE
(BOM) files, one csl-orig-style entry per line:
  <H1><h><key1>SLP1</key1><key2>accented</key2>[<hom>N</hom>]</h>
      <body>German</body><tail><L>n</L><pc>page-col</pc></tail></H1>

`<hom>` (homonym index) appears on ~10% of rows and is not part of the
mission's output schema -- left unread on purpose.

Output (beside this file's parent, LF, UTF-8, idempotent):
  sanskrityatina_sch_cases.tsv
    key1_slp1 <TAB> key2_accented <TAB> iast <TAB> form_key <TAB>
    case_class <TAB> L <TAB> pc <TAB> source_xml
  sanskrityatina_sch_cases_provenance.json (fetch facts, sha256 per source
  file, counts, the filename-count-vs-parsed-count mismatch this run measured)

The raw XML stays gitignored (raw/.gitignore); this script + the committed
TSV + provenance JSON are the auditable record.

Usage:
  python3 tools/h4533_build_sch_cases.py [--raw-dir PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent.parent          # .../sanskrityatina/
SANSKRIT_UTIL_CANDIDATES = [
    HERE / ".." / ".." / ".." / "sanskrit-util" / "py",   # sibling-clone default
    Path.home() / "Documents" / "GitHub" / "sanskrit-util" / "py",
]

# filename -> (case_class, filename-embedded case count -- the mission's
# claimed acceptance denominator, checked against the actual parsed count
# below rather than trusted blindly)
CASE_FILES = {
    "SCH-fiction-3147_cases.xml": ("fiction", 3147),
    "SCH-gedruckt_86_cases.xml": ("gedruckt", 86),
    "SCH-grade-12427_cases.xml": ("grade", 12427),
    "SCH-pw-comparison_319_cases.xml": ("pw-comparison", 319),
    "SCH-zu betonen-83_cases.xml": ("zu-betonen", 83),
    "SCH-zu-lesen_181_cases.xml": ("zu-lesen", 181),
}

_ROW_RE = re.compile(
    r"^<H1><h><key1>(?P<key1>[^<]*)</key1><key2>(?P<key2>[^<]*)</key2>"
    r"(?:<hom>\d+</hom>)?</h><body>(?P<body>.*)</body>"
    r"<tail><L>(?P<L>\d+)</L><pc>(?P<pc>[^<]*)</pc></tail></H1>$"
)


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
        "Could not import sanskrit_util -- clone https://github.com/gasyoun/sanskrit-util "
        "to ~/Documents/GitHub/sanskrit-util (H3222 sibling-clone layout).")


def _parse_file(path: Path, case_class: str):
    """Yields parsed row dicts; returns (rows, skipped_lines) via the list args."""
    raw_bytes = path.read_bytes()
    text = raw_bytes.decode("utf-16-le")
    if text.startswith("﻿"):
        text = text[1:]
    rows = []
    junk = []       # non-<H1> stray lines (blank-ish separators) -- expected, non-fatal
    malformed = []  # starts with <H1> but the full-line regex fails -- format drift, fatal
    for lineno, line in enumerate(text.split("\n"), start=1):
        line = line.strip("\r\n").strip()
        if not line:
            continue
        if not line.startswith("<H1>"):
            junk.append((lineno, line[:60]))
            continue
        m = _ROW_RE.match(line)
        if not m:
            malformed.append((lineno, line[:60]))
            continue
        rows.append({
            "key1_slp1": m.group("key1"),
            "key2_accented": m.group("key2"),
            "case_class": case_class,
            "L": m.group("L"),
            "pc": m.group("pc"),
            "source_xml": path.name,
        })
    return rows, junk, malformed, hashlib.sha256(raw_bytes).hexdigest(), len(raw_bytes)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default=str(HERE / "raw" / "Experimental"))
    args = ap.parse_args()

    su = _import_sanskrit_util()
    raw_dir = Path(args.raw_dir)

    all_rows = []
    per_file = {}
    for fname, (case_class, claimed_count) in CASE_FILES.items():
        fpath = raw_dir / fname
        if not fpath.is_file():
            raise SystemExit(
                f"raw file not found: {fpath}\n"
                f"refetch: rclone copy 'yadisk:Sanskrityatina/04_Reverse/Experimental/{fname}' "
                f"raw/Experimental/")
        rows, junk, malformed, sha, size = _parse_file(fpath, case_class)
        if malformed:
            raise SystemExit(
                f"{fname}: {len(malformed)} line(s) start with <H1> but fail the row "
                f"regex, e.g. {malformed[:3]} -- format drift?")
        per_file[fname] = {
            "case_class": case_class,
            "filename_claimed_count": claimed_count,
            "parsed_count": len(rows),
            "junk_lines_skipped": len(junk),
            "size_bytes": size,
            "sha256": sha,
        }
        all_rows.extend(rows)

    # -- transcode key1 via sanskrit-util (mandated pipeline) -----------------
    for r in all_rows:
        r["iast"] = su.from_slp1(r["key1_slp1"])
        r["form_key"] = su.slp1_form_key(r["key1_slp1"])

    # -- write TSV (LF, deterministic -- input order is file dict order, then
    #    on-disk line order within each file, so re-running is byte-stable) --
    out_tsv = HERE / "sanskrityatina_sch_cases.tsv"
    cols = ("key1_slp1", "key2_accented", "iast", "form_key", "case_class",
            "L", "pc", "source_xml")
    with out_tsv.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in all_rows:
            fh.write("\t".join(r[c] for c in cols) + "\n")

    claimed_total = sum(v["filename_claimed_count"] for v in per_file.values())
    parsed_total = len(all_rows)
    prov = {
        "dataset": "sanskrityatina-sch-cases",
        "source_dir": "yadisk:Sanskrityatina/04_Reverse/Experimental/",
        "fetched_by": "H4533 (OxAlpha, opencode glm-5.3-flash), rclone yadisk: (WebDAV backend)",
        "builder": "ReverseDictionary/sanskrityatina/tools/h4533_build_sch_cases.py",
        "sanskrit_util_version": getattr(su, "__version__", "unknown"),
        "per_file": per_file,
        "counts": {
            "filename_claimed_total": claimed_total,
            "parsed_total": parsed_total,
            "claimed_vs_parsed_delta": parsed_total - claimed_total,
        },
        "notes": [
            "The mint-time acceptance denominator (16,243 = sum of the six "
            "filename-embedded counts) does NOT match the actual number of "
            "<H1> entries on contact -- parsed_total is the real count, "
            "verified per-file against a direct '<H1>' occurrence grep.",
            "SCH-fiction-3147_cases.xml carries 3148 entries, one more than "
            "its filename claims -- unexplained single-row drift, not a "
            "parser artifact (open/close <H1> tag counts balance).",
            "SCH-zu betonen-83_cases.xml carries 143 entries, not 83: the "
            "file unions two accent-correction phrasings, 83x 'zu betonen' "
            "+ 60x 'zu akzentuieren' ('so to be accented' / 'to be "
            "accentuated') -- the filename names only the first phrasing.",
            "<hom> (homonym index, present on ~10% of rows) is read past "
            "but not emitted -- not part of the mission's TSV schema.",
            "One key1 in the zu-betonen file ('ja|u', L=13803, pc=190-3) "
            "carries a literal source-data '|' -- passed through verbatim; "
            "from_slp1 maps unmapped characters to themselves so iast/"
            "form_key for that row inherit the glitch rather than raising.",
            "SCH-zu betonen-83_cases.xml's raw file ends with 2 blank lines "
            "and 1 stray line containing only '+' -- source-file noise "
            "after the last real entry, skipped (blank lines silently, "
            "the '+' line counted in junk_lines_skipped), not counted as "
            "rows or as format drift.",
        ],
    }
    (HERE / "sanskrityatina_sch_cases_provenance.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    for name in (out_tsv, HERE / "sanskrityatina_sch_cases_provenance.json"):
        if not name.is_file() or name.stat().st_size == 0:
            raise SystemExit(f"output missing/empty: {name}")

    print(f"files parsed        : {len(per_file)}")
    for fname, v in per_file.items():
        print(f"  {fname}: claimed={v['filename_claimed_count']} parsed={v['parsed_count']}")
    print(f"claimed total        : {claimed_total}")
    print(f"parsed total         : {parsed_total} (delta {parsed_total - claimed_total})")
    print(f"rows transcoded      : {parsed_total} via sanskrit-util from_slp1/slp1_form_key")
    print("OK: 1 TSV + sanskrityatina_sch_cases_provenance.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
