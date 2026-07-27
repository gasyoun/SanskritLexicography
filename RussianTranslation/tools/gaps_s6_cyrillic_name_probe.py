#!/usr/bin/env python3
"""H1746 / SL GAPS §6 — probe Cyrillic name glossaries for recoverable keys.

Does NOT invent reverse-transliteration rules. Surveys available name-index
artifacts for: (a) inline IAST already present, (b) fully-Cyrillic-only,
(c) whether a small validated lookup seed can be built from (a) as onomasticon.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SL = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "gaps_s6_cyrillic_name_probe.json"

# Candidate roots from FINDINGS §60 / H184 survey
SEARCH_ROOTS = [
    Path(r"C:\Users\user\Documents\GitHub\SamudraManthanam"),
    SL / "RussianTranslation",
]

IAST_INLINE = re.compile(
    r"\(([A-Za-zĀāĪīŪūṚṛṜḹḶḷṂṃḤḥÑñṄṅṬṭḌḍṆṇŚśṢṣ\-\s]+)\)"
)


def scan_file(path: Path, max_lines: int = 5000) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"path": str(path), "error": str(e)}
    lines = text.splitlines()[:max_lines]
    cyr = 0
    iast_paren = 0
    samples = []
    for ln in lines:
        if re.search(r"[А-Яа-яЁё]", ln):
            cyr += 1
            m = IAST_INLINE.search(ln)
            if m:
                iast_paren += 1
                if len(samples) < 8:
                    samples.append(ln[:160])
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "lines_scanned": len(lines),
        "cyrillic_lines": cyr,
        "iast_paren_hits": iast_paren,
        "samples": samples,
    }


def main() -> None:
    hits = []
    name_tokens = (
        "potap",
        "erman",
        "temkin",
        "bady",
        "kadambar",
        "grincer",
        "grinzer",
        "рамаян",
        "имя",
        "imena",
        "names",
        "onomast",
        "glossary",
        "index",
    )
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".md", ".txt", ".tsv", ".csv", ".json", ".jsonl", ".html"}:
                continue
            low = p.name.lower()
            if not any(t in low for t in name_tokens):
                # also check path parts for Russian names
                pl = str(p).lower()
                if not any(t in pl for t in ("имя", "imena", "names", "onomast", "potap", "erman", "grincer", "кадамб")):
                    continue
            if p.stat().st_size > 50_000_000:
                continue
            hits.append(scan_file(p))

    with_iast = [h for h in hits if h.get("iast_paren_hits", 0) > 0]
    pure_cyr = [
        h
        for h in hits
        if h.get("cyrillic_lines", 0) > 20 and h.get("iast_paren_hits", 0) == 0
    ]
    report = {
        "handoff": "H1746",
        "gap": "SanskritLexicography/GAPS.md §6",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "model": "Grok 4.5 (grok-4.5)",
        "files_scanned": len(hits),
        "files_with_inline_iast": len(with_iast),
        "files_cyrillic_heavy_no_iast": len(pure_cyr),
        "verdict": (
            "FINDINGS §60 stands: reverse-transcription rules remain unsafe. "
            "Recoverable path is a validated proper-noun LOOKUP table seeded from "
            "IAST-bearing indices (Гринцер / Rāmāyaṇa), not character rules. "
            "This probe inventories seed candidates; full table build needs human "
            "spot-check against an onomasticon for the 3 fully-Cyrillic glossaries."
        ),
        "with_iast_top": sorted(with_iast, key=lambda h: -h.get("iast_paren_hits", 0))[:15],
        "pure_cyr_top": sorted(pure_cyr, key=lambda h: -h.get("cyrillic_lines", 0))[:15],
        "all_hits": hits[:80],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "files_scanned": report["files_scanned"],
                "with_iast": report["files_with_inline_iast"],
                "pure_cyr": report["files_cyrillic_heavy_no_iast"],
                "out": str(OUT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
