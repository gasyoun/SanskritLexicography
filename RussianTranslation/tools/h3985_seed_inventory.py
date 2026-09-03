#!/usr/bin/env python3
"""H3985 / SL GAPS §6 stage A — portable re-derivation of the H1746 seed inventory.

Reproduces the FINDINGS §495 split (IAST-bearing vs pure-Cyrillic name-index
files) on whatever box runs it: the H1746 probe hardcoded Windows roots and only
persisted the first 80 of 152 hits, so the actual 61-file seed list was never
committed. Same filters, same regexes as
`gaps_s6_cyrillic_name_probe.py`; only the roots and the output are new.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SL = Path(__file__).resolve().parents[2]
GITHUB = SL.parent
OUT = Path(__file__).resolve().parent / "h3985_seed_inventory.json"

SEARCH_ROOTS = [GITHUB / "SamudraManthanam", SL / "RussianTranslation"]

IAST_INLINE = re.compile(
    r"\(([A-Za-zĀāĪīŪūṚṛṜḹḶḷṂṃḤḥÑñṄṅṬṭḌḍṆṇŚśṢṣ\-\s]+)\)"
)
CYR = re.compile(r"[А-Яа-яЁё]")

NAME_TOKENS = (
    "potap", "erman", "temkin", "bady", "kadambar", "grincer", "grinzer",
    "рамаян", "имя", "imena", "names", "onomast", "glossary", "index",
)
PATH_TOKENS = ("имя", "imena", "names", "onomast", "potap", "erman", "grincer", "кадамб")
EXTS = {".md", ".txt", ".tsv", ".csv", ".json", ".jsonl", ".html"}


def scan_file(path: Path, max_lines: int = 5000) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:  # unreadable candidate is a hit with an error field
        return {"path": str(path), "error": str(e)}
    lines = text.splitlines()[:max_lines]
    cyr = 0
    iast_paren = 0
    for ln in lines:
        if CYR.search(ln):
            cyr += 1
            if IAST_INLINE.search(ln):
                iast_paren += 1
    return {
        "path": str(path),
        "rel": os.path.relpath(str(path), str(GITHUB)),
        "bytes": path.stat().st_size,
        "lines_scanned": len(lines),
        "cyrillic_lines": cyr,
        "iast_paren_hits": iast_paren,
    }


def main() -> None:
    hits = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in EXTS:
                continue
            low = p.name.lower()
            if not any(t in low for t in NAME_TOKENS):
                if not any(t in str(p).lower() for t in PATH_TOKENS):
                    continue
            if p.stat().st_size > 50_000_000:
                continue
            hits.append(scan_file(p))

    with_iast = [h for h in hits if h.get("iast_paren_hits", 0) > 0]
    pure_cyr = [h for h in hits
                if h.get("cyrillic_lines", 0) > 20 and h.get("iast_paren_hits", 0) == 0]
    report = {
        "handoff": "H3985",
        "reproduces": "H1746 / FINDINGS §495",
        "gap": "SanskritLexicography/GAPS.md §6",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "model": "Opus 5 (claude-opus-5)",
        "roots": [str(r) for r in SEARCH_ROOTS if r.exists()],
        "files_scanned": len(hits),
        "files_with_inline_iast": len(with_iast),
        "files_cyrillic_heavy_no_iast": len(pure_cyr),
        "h1746_reference": {"files_scanned": 152, "with_iast": 61, "pure_cyr": 47},
        "seeds_with_iast": sorted(with_iast, key=lambda h: -h.get("iast_paren_hits", 0)),
        "seeds_pure_cyrillic": sorted(pure_cyr, key=lambda h: -h.get("cyrillic_lines", 0)),
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("files_scanned", "files_with_inline_iast",
                       "files_cyrillic_heavy_no_iast")}, indent=2))
    print("out:", OUT)


if __name__ == "__main__":
    main()
