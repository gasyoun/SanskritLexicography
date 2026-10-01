#!/usr/bin/env python3
"""H4800 — Sanskrityatina reverse index vs union headwords (16-dict, H4797).

Two-stage, read-only over committed/landed inputs:

 1. STOCK EXTRACTION (resolves metadoc backlog item 2): the per-headword
    carrier of the 187,992-headword Schwarz-based reverse-dictionary stock is
    yadisk:Sanskrityatina/04_Reverse/.doc.pdf/reverse-index-full.doc (OLE2
    Word 97, 13,846,528 B). Its WordDocument stream is uniformly UTF-16LE;
    one paragraph per entry, `SOURCE_CODE<TAB|SP>headword` or a bare
    headword. This builder extracts every word-line (binary junk filtered by
    charset) — ~230k+ entries — and keys it via sanskrit-util form_key().
    The doc is the FULL working reverse index (mtime 2014), a superset of the
    legend's 187,992 stock; see the report for the count reconciliation.
 2. UNION JOIN: stock form_key -> HeadwordLists/union-16dicts/
    union_headwords_16.tsv (417,184 keys, H4797) keyed slp1_form_key(slp1).
    Measures coverage, per-dict overlap, and the union-absent residue
    (Russian-school-only forms).

Outputs (beside this file's parent, LF, UTF-8, idempotent):
  - sanskrityatina_reverse_full_stock.tsv
      headword_iast <TAB> source_code <TAB> form_key   (doc order preserved)
  - sanskrityatina_reverse_union16_join.tsv
      headword_iast <TAB> source_code <TAB> form_key <TAB> in_union
      <TAB> union_dicts                                (doc order preserved)
  - h4800_provenance.json

Raw stays gitignored (raw/.gitignore). Usage:
  python3 tools/h4800_union_join.py [--raw PATH] [--union PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent.parent          # .../sanskrityatina/
REPO = HERE.parent.parent                              # repo root
SANSKRIT_UTIL_CANDIDATES = [
    REPO.parent / "sanskrit-util" / "py",               # sibling-clone default
    Path.home() / "Documents" / "GitHub" / "sanskrit-util" / "py",
]

DOC_REMOTE = "yadisk:Sanskrityatina/04_Reverse/.doc.pdf/reverse-index-full.doc"

# IAST word alphabet (precomposed) + ASCII letters, hyphen, avagraha.
_WORD_CHARS = set(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "āīūṛṝḷḹēōṅñṭḍṇśṣḥṃṁḻṹṵ"
    "-''"
)
_WORD_RE = re.compile(r"^[A-Za-zāīūṛṝḷḹēōṅñṭḍṇśṣḥṃṁḻṹṵ\-']+$")
_CODED_RE = re.compile(r"^([A-Z])[\t \xa0]+(\S+)$")

# Legend anchor examples (H4475) for extraction cross-validation.
_LEGEND_ANCHORS = ("aṃśagaṇa", "paryantīkṛta", "paryavadāpayitar")


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


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_stock(doc_path: Path):
    """Word 97 UTF-16LE WordDocument stream -> [(headword_iast, source_code)]."""
    import olefile
    ole = olefile.OleFileIO(str(doc_path))
    wd = ole.openstream("WordDocument").read()
    text = wd.decode("utf-16-le", errors="ignore")
    entries, junk = [], 0
    for ln in text.split("\r"):
        s = ln.strip()
        if not s:
            continue
        if not (set(s) <= _WORD_CHARS | {" ", "\t", "\xa0"}):
            junk += 1                       # binary/formatting block — not an entry
            continue
        m = _CODED_RE.match(s)
        if m and _WORD_RE.match(m.group(2)):
            entries.append((m.group(2), m.group(1)))
        elif _WORD_RE.match(s):
            entries.append((s, ""))
        else:
            junk += 1
    return entries, junk, len(wd)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(HERE / "raw" / "reverse-index-full.doc"))
    ap.add_argument("--union", default=str(
        REPO / "HeadwordLists" / "union-16dicts" / "union_headwords_16.tsv"))
    args = ap.parse_args()

    su = _import_sanskrit_util()

    raw = Path(args.raw)
    if not raw.is_file():
        raise SystemExit(f"raw doc not found: {raw}\n"
                         f"refetch: rclone copy '{DOC_REMOTE}' raw/")

    entries, junk_lines, wd_bytes = extract_stock(raw)

    # ---- dedupe census (doc order preserved for the TSV) ----
    seen = set()
    dupes = 0
    unique_entries = []
    for w, c in entries:
        if w in seen:
            dupes += 1
            continue
        seen.add(w)
        unique_entries.append((w, c))

    coded = [(w, c) for w, c in unique_entries if c]
    code_dist = Counter(c for _, c in coded)

    # ---- legend anchors ----
    anchors = {a: (a in seen) for a in _LEGEND_ANCHORS}

    # ---- union index ----
    union_path = Path(args.union)
    union = {}                              # form_key -> dicts string
    n_union_rows = 0
    with open(union_path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        assert header[:3] == ["slp1", "n_dicts", "dicts"], header
        for ln in f:
            cols = ln.rstrip("\n").split("\t")
            if len(cols) < 3:
                continue
            n_union_rows += 1
            fk = su.slp1_form_key(cols[0])
            if fk and fk not in union:
                union[fk] = cols[2]

    # ---- join ----
    join_rows = []
    in_union = 0
    per_dict = Counter()
    residue_codes = Counter()
    residue = []
    for w, c in unique_entries:
        fk = su.form_key(w)
        hit = union.get(fk)
        join_rows.append((w, c, fk, "1" if hit else "0", hit or ""))
        if hit:
            in_union += 1
            for d in hit.split(" "):
                per_dict[d] += 1
        else:
            residue_codes[c or "(none)"] += 1
            residue.append(w)

    # ---- write outputs ----
    stock_tsv = HERE / "sanskrityatina_reverse_full_stock.tsv"
    with open(stock_tsv, "w", encoding="utf-8", newline="\n") as f:
        f.write("headword_iast\tsource_code\tform_key\n")
        for w, c in unique_entries:
            f.write(f"{w}\t{c}\t{su.form_key(w)}\n")

    join_tsv = HERE / "sanskrityatina_reverse_union16_join.tsv"
    with open(join_tsv, "w", encoding="utf-8", newline="\n") as f:
        f.write("headword_iast\tsource_code\tform_key\tin_union\tunion_dicts\n")
        for w, c, fk, flag, dicts in join_rows:
            f.write(f"{w}\t{c}\t{fk}\t{flag}\t{dicts}\n")

    cov = in_union / len(unique_entries)
    prov = {
        "dataset": "sanskrityatina-reverse-vs-union16",
        "handoff": "H4800",
        "generated": "2026-09-19",
        "executor": "OxAlpha (opencode/z-ai/glm-5.3-flash), drain worker on Claude/c4",
        "stock_source": {
            "path": DOC_REMOTE,
            "local_size_bytes": raw.stat().st_size,
            "sha256": _sha256(raw),
            "worddocument_stream_bytes": wd_bytes,
            "extraction": "WordDocument stream decoded UTF-16LE, split on \\r; "
                          "entries = lines entirely within the IAST word alphabet; "
                          "coded lines 'SOURCE_CODE<TAB|SP>word' (single capital letter); "
                          "binary junk lines excluded",
        },
        "union_source": {
            "path": "HeadwordLists/union-16dicts/union_headwords_16.tsv (H4797)",
            "rows": n_union_rows,
            "join_key": "sanskrit-util slp1_form_key(union slp1) == form_key(headword_iast)",
        },
        "counts": {
            "raw_entries_extracted": len(entries),
            "junk_nonentry_lines": junk_lines,
            "duplicate_headwords": dupes,
            "unique_headwords": len(unique_entries),
            "coded": len(coded),
            "uncoded": len(unique_entries) - len(coded),
            "source_code_distribution": dict(sorted(code_dist.items())),
            "legend_stock_total_for_reference": 187992,
            "legend_anchor_examples_present": anchors,
            "in_union": in_union,
            "residue_not_in_union": len(unique_entries) - in_union,
            "coverage_pct": round(cov * 100, 2),
            "per_dict_overlapping_stock_headwords": dict(
                sorted(per_dict.items(), key=lambda kv: -kv[1])),
            "residue_by_source_code": dict(sorted(residue_codes.items(),
                                                  key=lambda kv: -kv[1])),
        },
        "notes": [
            "The doc is the FULL working reverse index (superset of the legend's "
            "187,992 'class 0' stock); single-letter source codes are carried verbatim, "
            "semantics NOT adjudicated here (H4475 legend names IEG/PD/BHS/MW/SCH as the "
            "coding's source-dict universe).",
            "Residue (in_union=0) = forms attested in MG's Schwarz-based reverse stock "
            "but absent from ALL 16 Cologne dictionaries of the H4797 union — the "
            "Russian-school-only slice.",
        ],
    }
    with open(HERE / "h4800_provenance.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(prov, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(json.dumps(prov["counts"], ensure_ascii=False, indent=2))
    print(f"residue sample (first 25): {residue[:25]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
