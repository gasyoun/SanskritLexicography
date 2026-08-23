#!/usr/bin/env python3
"""H3171 — verify the hand-classification map covers exactly the missed cells."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from h3171_classify import CLASSES  # noqa: E402

GOLD_DIR = Path(__file__).resolve().parents[1]
rows = [json.loads(l) for l in (GOLD_DIR / "h3171_results.jsonl").read_text(encoding="utf-8").splitlines()]
by_id = {r["id"]: r for r in rows}

for wit, flag in [("H", "vs_gold_heritage"), ("D", "vs_gold_dm")]:
    missing = []
    extra = []
    for r in rows:
        if r["panel_lemma"] != "correct":
            continue
        missed = not r.get(flag)
        classified = any(w == wit for w, _c, _n in CLASSES.get(r["id"], []))
        if missed and not classified:
            missing.append(r["id"])
        if not missed and classified:
            extra.append(r["id"])
    print(f"{wit}: unclassified_misses={missing} classifications_on_hits={extra}")
