#!/usr/bin/env python
"""H3500 - repair pass for a pwg_ru TM/store JSONL.

Applies exactly three mechanical fixes (everything else found by the scanner
is documented in the H3500 report as renderer-covered or manual-follow-up):

  fix1  drop byte-identical duplicate `ru` rows within one (key1, subcard)
        group, keep-best-ranked copy (human_touched > approved status >
        content mass > first occurrence) and record every dropped row in a
        JSONL ledger;
  fix2  wrap the single free-floating German "vgl." occurrence class into the
        Russian convention directly in `ru` (H2849 precedent: untagged German
        function words are substituted in the ru field; tagged <ab> tokens are
        render-time translated and stay);
  fix3  stamp rows whose `ru` carries beyond-PWG advisory content ([Buddh]/
        BHSD spans) with an additive provenance field
        ``advisory_enrichment: ["bhsd"]`` so no consumer treats ru as pure
        PWG translation (H3456 recommendation).

The de field is NEVER touched. Dry-run by default; --write mutates the store
atomically (tmp file + os.replace). Refuses when the kept-content mass drops
by more than 1% relative to the pre-repair mass unless --allow-mass-drop.

  python src/h3500_store_repair.py [STORE] [--write] [--ledger PATH]
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
DEFAULT_LEDGER = os.path.join(HERE, "h3500_repair_ledger.jsonl")

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t]+")
BARE_VGL_RE = re.compile(r"(?<![A-Za-z])vgl\.(?![A-Za-z])")
ADV_RE = re.compile(r"\[(NWS|Reg|Buddh)\]")
MAX_MASS_DROP = 0.01


def visible(text: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub(" ", text or "")).strip()


def rank(row):
    """Keep-best ranking for one duplicate cluster (higher wins)."""
    pv = row.get("provenance") or {}
    status = row.get("review_status") or ""
    human = bool(row.get("reviewer")) or (
        isinstance(status, str) and bool(status)
        and not status.startswith("ai_"))
    partial = bool(pv.get("partial_card"))
    return (1 if human else 0,
            1 if status == "approved" else 0,
            0 if partial else 1,
            len(row.get("ru") or ""))


def content_mass(rows):
    return sum(len(r.get("ru") or "") + len(r.get("de") or "") for r in rows)


def repair(rows):
    """Return (repaired_rows, ledger_events)."""
    events = []

    # fix1: dedupe byte-identical (sense_tag, ru) rows within (key1, subcard).
    # sense_tag joins the cluster key: identical ru under DIFFERENT tags is
    # zz-key tagger noise, not duplication - those rows are distinct senses
    # and must survive.
    groups = collections.defaultdict(list)
    for i, r in enumerate(rows):
        groups[(r.get("key1"), r.get("subcard"))].append(i)
    drop = set()
    for k, idxs in sorted(groups.items()):
        clusters = collections.defaultdict(list)
        for i in idxs:
            r = rows[i]
            ru = (r.get("ru") or "").strip()
            if len(ru) >= 12:
                clusters[(r.get("sense_tag"), ru)].append(i)
        for tag_ru, members in clusters.items():
            if len(members) < 2:
                continue
            ordered = sorted(members, key=lambda i: rank(rows[i]),
                             reverse=True)
            keep, extras = ordered[0], ordered[1:]
            drop.update(extras)
            for i in extras:
                events.append({
                    "fix": "class1a_dedupe", "key1": k[0], "subcard": k[1],
                    "sense_tag": tag_ru[0],
                    "kept_index": keep, "dropped_index": i,
                    "kept_rank": rank(rows[keep]),
                    "dropped_rank": rank(rows[i]),
                    "ru_sha_prefix": __import__("hashlib").sha256(
                        tag_ru[1].encode("utf-8")).hexdigest()[:16],
                })

    # fix2: free-floating vgl. -> sr. (untagged only; tagged stays Latin)
    vgl_fixed = []
    out = []
    for i, r in enumerate(rows):
        r = dict(r)
        ru = r.get("ru") or ""
        if i not in drop:
            new = _fix_bare_vgl(ru)
            if new != ru:
                r["ru"] = new
                vgl_fixed.append({"index": i, "subcard": r.get("subcard"),
                                  "before": ru[:120], "after": new[:120]})
        out.append(r)
    events.extend({"fix": "class2_bare_vgl", **e} for e in vgl_fixed)

    # fix3: advisory enrichment marker
    adv = []
    for i, r in enumerate(out):
        if i in drop or not ADV_RE.search(r.get("ru") or ""):
            continue
        tags = sorted(set(ADV_RE.findall(r.get("ru") or "")))
        field = {"Buddh": "bhsd"}.get(tags[0], tags[0].lower()) \
            if len(tags) == 1 else [t.lower() for t in tags]
        prev = r.get("advisory_enrichment")
        if prev:
            continue
        r["advisory_enrichment"] = field
        adv.append({"index": i, "subcard": r.get("subcard"),
                    "advisory_enrichment": field})
    events.extend({"fix": "class3_advisory_marker", **e} for e in adv)

    repaired = [r for i, r in enumerate(out) if i not in drop]
    return repaired, events


def _fix_bare_vgl(ru: str) -> str:
    vis_positions = []

    def repl(m):
        start = m.start()
        # skip when inside an <ab>...</ab> span (render-time translated there)
        last_open = ru.rfind("<ab>", 0, start)
        if last_open != -1 and ru.rfind("</ab>", 0, start) < last_open:
            return m.group(0)
        vis_positions.append(start)
        return "ср."

    return BARE_VGL_RE.sub(repl, ru)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("store", nargs="?", default=DEFAULT_STORE)
    ap.add_argument("--write", action="store_true",
                    help="mutate the store (default: dry run)")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--allow-mass-drop", action="store_true")
    args = ap.parse_args()

    with io.open(args.store, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    repaired, events = repair(rows)

    mass_before = content_mass(rows)
    mass_after = content_mass(repaired)
    drop_frac = 1 - mass_after / max(mass_before, 1)
    summary = {
        "store": args.store,
        "rows_before": len(rows),
        "rows_after": len(repaired),
        "dropped_rows": len(rows) - len(repaired),
        "events_by_fix": dict(collections.Counter(e["fix"] for e in events)),
        "content_mass_before": mass_before,
        "content_mass_after": mass_after,
        "mass_drop_fraction": round(drop_frac, 6),
        "mode": "write" if args.write else "dry-run",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if drop_frac > MAX_MASS_DROP and not args.allow_mass_drop:
        print(f"REFUSING: mass drop {drop_frac:.4f} > {MAX_MASS_DROP}; "
              "inspect the ledger before forcing with --allow-mass-drop")
        args.write = False

    if args.write:
        tmp = args.store + ".h3500.tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
            for r in repaired:
                f.write(json.dumps(r, ensure_ascii=False,
                                   sort_keys=True) + "\n")
        os.replace(tmp, args.store)
        with io.open(args.ledger, "w", encoding="utf-8", newline="\n") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"WROTE {args.store} ({len(repaired)} rows); "
              f"ledger -> {args.ledger} ({len(events)} events)")
    else:
        print("dry run: no changes written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
