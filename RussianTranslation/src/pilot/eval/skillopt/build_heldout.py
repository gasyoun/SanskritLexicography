"""Build the FROZEN SkillOpt B-arm held-out benchmark for the PWG->RU pilot (H388).

A held-out benchmark must be reproducible and stable, so this script embeds a
DATED SNAPSHOT of the runnable-root universe (from `verb_worklist.py --top`,
08-07-2026) rather than reading live worklist state -- a frozen exam must not
drift when the queue changes. It emits `heldout_v1.json`: N roots split 2:1:7
into train / selection / test, stratified by size band, deterministically.

Honest constraints (surfaced, not padded -- see README):
  * Only 17 roots are RUNNABLE (have rootmaps); 684 remain rootmap-less. A larger
    exam REQUIRES generating more rootmaps first -- that is a prerequisite task,
    not something this fixture can conjure.
  * `sTA` is a 241-agent defer-monster (own budgeted session per /pwg-drain
    guardrails); it is held aside as a cost-deferred control, NOT in the scored
    16-root benchmark, so a single monster can't dominate B-arm cost.
  * Unit = root here (coarse). Card-level scoring (denser signal) is a later
    refinement once the loop proves out at root granularity.

Split contract (SkillOpt §3.1): train supplies experience, selection GATES every
edit, test is touched ONLY for the final report. Assignment is size-stratified so
each split spans small/medium/large roots -- an edit that only helps big roots
can't hide behind a size-skewed selection split.
"""
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SNAPSHOT_DATE = "08-07-2026"
SNAPSHOT_SOURCE = "verb_worklist.py --top 40 (runnable=17)"

# Frozen snapshot: (root, source_bytes, worklist_score). From the 08-07-2026 run.
RUNNABLE = [
    ("sTA", 184881, 61.6), ("BU", 102570, 60.2), ("yuj", 106851, 58.2),
    ("as", 59006, 57.5), ("i", 146340, 57.4), ("tap", 39184, 49.4),
    ("ram", 35782, 48.1), ("Baj", 34013, 47.4), ("kzip", 37869, 46.7),
    ("aS", 21710, 46.1), ("SaMs", 26005, 45.2), ("tyaj", 17387, 45.0),
    ("muh", 21894, 44.5), ("nu", 20679, 44.4), ("hu", 16988, 44.0),
    ("sev", 20037, 43.4), ("pU", 14411, 43.3),
]

# sTA: 241 expected agents on live preflight (defer-calibrate). Excluded from the
# scored benchmark; kept as a documented cost-deferred control.
DEFER_MONSTERS = {"sTA"}


def size_band(byts: int) -> str:
    if byts >= 80_000:
        return "large"
    if byts >= 30_000:
        return "medium"
    return "small"


def build():
    active = [(r, b, s) for (r, b, s) in RUNNABLE if r not in DEFER_MONSTERS]
    buckets: dict[str, list] = {"large": [], "medium": [], "small": []}
    for r, b, s in active:
        buckets[size_band(b)].append((r, b, s))
    for band in buckets:
        buckets[band].sort(key=lambda t: -t[1])

    n = len(active)
    want = {"train": round(0.2 * n), "sel": max(1, round(0.1 * n))}
    want["test"] = n - want["train"] - want["sel"]

    # Stratified allocation: draw WITHIN each size band so every split spans sizes.
    # train takes the top of each band (one per band) -> train is size-balanced;
    # sel takes the 2nd of the two largest bands -> sel spans two sizes; test gets
    # the rest -> test spans all sizes. Requires large>=1, medium>=2, small>=2.
    splits: dict[str, list] = {"train": [], "sel": [], "test": []}
    assigned = set()

    # train: one per band (top by bytes)
    for band in ("large", "medium", "small"):
        if buckets[band]:
            pick = buckets[band][0]
            splits["train"].append(pick)
            assigned.add(pick[0])

    # sel: 2nd member of the two most-populous bands (small, medium here)
    for band in sorted(buckets, key=lambda b: -len(buckets[b]))[:want["sel"]]:
        for item in buckets[band]:
            if item[0] not in assigned:
                splits["sel"].append(item)
                assigned.add(item[0])
                break

    # test: everything not yet assigned, size-interleaved for readability
    for band in ("large", "medium", "small"):
        for item in buckets[band]:
            if item[0] not in assigned:
                splits["test"].append(item)
                assigned.add(item[0])

    want = {k: len(v) for k, v in splits.items()}  # actual counts after strat
    return active, buckets, splits, want


def main():
    active, buckets, splits, want = build()
    here = os.path.dirname(os.path.abspath(__file__))

    def rows(items):
        return [{"root": r, "source_bytes": b, "worklist_score": s,
                 "size_band": size_band(b)} for (r, b, s) in items]

    fixture = {
        "schema": "pwg.skillopt.heldout.v1",
        "created": SNAPSHOT_DATE,
        "handoff": "H388",
        "snapshot_source": SNAPSHOT_SOURCE,
        "split_ratio": "2:1:7 (train:selection:test)",
        "unit": "root",
        "n_active": len(active),
        "notes": [
            "Only 17 roots were runnable (had rootmaps) on the snapshot date; a "
            "larger exam requires generating more rootmaps first (prerequisite).",
            "sTA (241 expected agents, defer-calibrate) held aside as a "
            "cost-deferred control, NOT scored in this benchmark.",
            "selection split GATES every edit; test split is report-only.",
        ],
        "size_band_counts": {b: len(v) for b, v in buckets.items()},
        "splits": {k: rows(v) for k, v in splits.items()},
        "deferred_controls": [
            {"root": "sTA", "source_bytes": 184881, "reason":
             "241 expected agents (defer-calibrate) — own budgeted session"}
        ],
    }
    out = os.path.join(here, "heldout_v1.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(fixture, f, ensure_ascii=False, indent=2)

    print(f"SkillOpt held-out fixture (H388) — {len(active)} active roots, 2:1:7")
    print(f"  size bands: {fixture['size_band_counts']}")
    for split in ("train", "sel", "test"):
        items = splits[split]
        bands = {}
        for (r, b, s) in items:
            bands[size_band(b)] = bands.get(size_band(b), 0) + 1
        roots = ", ".join(r for (r, _, _) in items)
        print(f"  {split:5} ({len(items):2}) [{bands}]: {roots}")
    print("  deferred control: sTA (241 agents)")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
