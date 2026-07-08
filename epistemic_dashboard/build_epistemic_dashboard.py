#!/usr/bin/env python3
"""build_epistemic_dashboard.py — parse the seven epistemic sibling registries in a directory
into one `epistemic.json` for the dashboard (H356 Wave 4).

Reads whichever of ASSUMPTIONS / CONTRADICTIONS / GAPS / DEAD_ENDS / RECIPES / STALENESS /
GLOSSARY exist in `--dir`, and emits per-layer counts (rows, importance 🔴🟠🟡, origin
⚙️ auto / ✍️ human) plus a STALENESS flag summary and grand totals. The dashboard `index.html`
renders this file; the same generator serves both the Sanskrit-data side (public) and the
infra side (local-only), so the two dashboards are byte-for-byte the same code.

No `Date.now()` in any derived count — the generation timestamp is the only clock read, and it
is stamped, not computed-against, so re-runs over unchanged registries diff cleanly.

Usage:
    python build_epistemic_dashboard.py --dir <registries-dir> --side {sanskrit|infra} \
        --repo-url <blob-base> --out <epistemic.json>
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

IMPORTANCE = {"🔴": 3, "🟠": 2, "🟡": 1}
# layer key -> (the epistemic act it holds)
LAYERS = [
    ("ASSUMPTIONS", "relying on an unproven premise"),
    ("CONTRADICTIONS", "≥2 sources disagree, no verdict"),
    ("GAPS", "not-yet-knowing (the frontier)"),
    ("DEAD_ENDS", "abandoning an approach"),
    ("RECIPES", "reproducing a fact"),
    ("STALENESS", "decaying — confidence over time"),
    ("GLOSSARY", "defining canonical terms"),
]
ENTRY = re.compile(r"^### (.+?)\s*$")
DOT = re.compile(r"(🔴|🟠|🟡)")
ORIGIN = re.compile(r"(⚙️|✍️)")
STALE_ROW = re.compile(r"^\|\s*\[§(\d+)\]")
STALE_FLAG = re.compile(r"(🔴|🟡|🟢|⬜)")


def gh_slug(heading):
    out = []
    for ch in heading.strip().lower():
        if ch in " -":
            out.append(ch)
        elif ch.isalnum():
            out.append(ch)
    return "".join(out).replace(" ", "-")


def parse_entry_layer(text, file_url):
    """Layers whose rows are `### …` entries (all but STALENESS)."""
    lines = text.split("\n")
    entries = []
    i = 0
    while i < len(lines):
        m = ENTRY.match(lines[i])
        if m:
            heading = m.group(1)
            # look at the next few non-blank lines for the dot + origin
            imp = origin = None
            for k in range(i + 1, min(i + 4, len(lines))):
                if imp is None:
                    dm = DOT.search(lines[k])
                    if dm:
                        imp = IMPORTANCE[dm.group(1)]
                if origin is None:
                    om = ORIGIN.search(lines[k])
                    if om:
                        origin = "auto" if om.group(1) == "⚙️" else "human"
                if imp and origin:
                    break
            entries.append({
                "title": heading,
                "importance": imp,
                "origin": origin or "human",  # glossary/plain entries default human
                "url": f"{file_url}#{gh_slug(heading)}",
            })
        i += 1
    return entries


def parse_staleness(text):
    flags = {"red": 0, "yellow": 0, "green": 0, "unknown": 0}
    total = 0
    for line in text.split("\n"):
        if not STALE_ROW.match(line):
            continue
        total += 1
        cells = line.split("|")
        # the Flag column is the 6th cell (idx 5) in | § | disc | last | age | flag | recipe |
        flagcell = cells[5] if len(cells) > 5 else ""
        fm = STALE_FLAG.search(flagcell)
        g = fm.group(1) if fm else "⬜"
        flags[{"🔴": "red", "🟡": "yellow", "🟢": "green", "⬜": "unknown"}[g]] += 1
    return total, flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--side", choices=["sanskrit", "infra"], required=True)
    ap.add_argument("--repo-url", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    from pathlib import Path
    root = Path(args.dir)
    side_name = "Sanskrit-data" if args.side == "sanskrit" else "infra / process"

    layers = []
    staleness = None
    tot_rows = tot_auto = tot_human = 0
    tot_entry = tot_cand = tot_cats = tot_ilinks = 0
    tot_imp = {"3": 0, "2": 0, "1": 0}
    cat_re = re.compile(r"^## (?:[A-Z]\.|⚙️)", re.M)   # thematic category headers (not Conclusions)
    ilink_re = re.compile(r"^↔ Interlinks:", re.M)

    for key, act in LAYERS:
        p = root / f"{key}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        file_url = f"{args.repo_url}/{key}.md"
        if key == "STALENESS":
            total, flags = parse_staleness(text)
            layers.append({"key": key, "act": act, "url": file_url,
                           "total": total, "by_importance": None,
                           "by_origin": {"auto": total, "human": 0},
                           "flags": flags, "entries": []})
            staleness = {"total": total, **flags}
            tot_rows += total
            tot_auto += total
            continue
        entries = parse_entry_layer(text, file_url)
        by_imp = {"3": 0, "2": 0, "1": 0}
        by_org = {"auto": 0, "human": 0}
        for e in entries:
            if e["importance"] in (3, 2, 1):
                by_imp[str(e["importance"])] += 1
                tot_imp[str(e["importance"])] += 1
            by_org[e["origin"]] += 1
        cats = len(cat_re.findall(text))
        ilinks = len(ilink_re.findall(text))
        layers.append({"key": key, "act": act, "url": file_url,
                       "total": len(entries), "by_importance": by_imp,
                       "by_origin": by_org, "categories": cats,
                       "interlinks": ilinks, "entries": entries})
        tot_rows += len(entries)
        tot_auto += by_org["auto"]
        tot_human += by_org["human"]
        tot_entry += len(entries)
        tot_cand += by_org["auto"]
        tot_cats += cats
        tot_ilinks += ilinks

    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "side": side_name,
        "repo_url": args.repo_url,
        "layers": layers,
        "staleness": staleness,
        "totals": {"rows": tot_rows, "auto": tot_auto, "human": tot_human,
                   "by_importance": tot_imp, "layers": len(layers),
                   "entry_rows": tot_entry, "candidates": tot_cand,
                   "categories": tot_cats, "interlinks": tot_ilinks},
    }
    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=1),
                              encoding="utf-8")
    print(f"wrote {args.out}: {len(layers)} layers, {tot_rows} rows "
          f"(⚙️{tot_auto}/✍️{tot_human}); staleness={staleness}")


if __name__ == "__main__":
    main()
