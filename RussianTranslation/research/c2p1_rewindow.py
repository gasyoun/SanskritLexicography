"""Ceiling C2 — re-window phase-1 ls_source_map.json on the corrected work dates (H4728).

Executes the re-window that H3790 (C2 phase 2) measured but deliberately did NOT perform:
the 7 map-date conflicts (AMAR, GĪT. GOV, KATHĀS, RĀJAN, SĀH. D, VOP, Spr) recorded in
work_dating_table.json are applied to a DERIVED re-windowed map, and the committed
phase-1 windows are recomputed under the curated ranges to produce a delta report with
a date-range recount.

Consumes (never rewrites — the H3790 fence stands):
    src/ls_source_map.json                  phase-1 point-date map (45 sigla)
    src/work_dating_table.json              curated ranges + scholarly sources (H3790)
    src/pwg_sense_attestation_window.jsonl  phase-1 per-sense windows (committed store)

Emits (both idempotent):
    src/ls_source_map_rewindowed.json       re-windowed map: original entries verbatim
                                            + curated dating block per siglum
    research/C2P1_REWINDOW_DELTA.md         delta report: corrections table + recount

Method: research/c2p2_dating_table.py::rewindow — a window's bounds are the union of
the cited works' curated RANGES (earliest=min, latest=max) over works with
dating_valid=true; dating-invalid sigla (Spr, ŚKDR) are dropped, not clamped. Dropping
them here follows the curated table's own committed semantics («invalid … must not set
a window bound», H3790); the STORE-WIDE convention remains the open human decision
C2P2-D10 — this artifact changes no vote and rewrites no store.

The honesty contract carries over unchanged: every window is «per Böhtlingk–Roth's
citations» — a fact about the dictionary, never a claim about when a sense emerged.

Usage:
    python c2p1_rewindow.py --selftest   # fixture tests (validator + delta arithmetic)
    python c2p1_rewindow.py --check      # gate: recompute + invariants, exit 1 on drift
    python c2p1_rewindow.py              # emit re-windowed map + delta report

H4728 · interlinks self-edge row 221 (SanskritLexicography → itself) flips to live on push · 15-09-2026
"""

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from c2p2_dating_table import (   # noqa: E402  (prior art: proven re-window maths)
    MAP_PATH,
    TABLE_PATH,
    WINDOW_PATH,
    load_json,
    rewindow,
    validate,
)

RT = os.path.dirname(HERE)
SRC = os.path.join(RT, "src")

OUT_MAP_PATH = os.path.join(SRC, "ls_source_map_rewindowed.json")
OUT_REPORT_PATH = os.path.join(HERE, "C2P1_REWINDOW_DELTA.md")

HANDOFF = "H4728"
TODAY = "15-09-2026"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def n(x):
    return "{:,}".format(x)


def fmt_year(y):
    return "%d BCE" % (-y) if y < 0 else "%d CE" % y


# ----------------------------------------------------------------------- delta


def new_stats():
    return {
        "windows": 0,
        "unchanged": 0,
        "moved_any": 0,
        "earliest_moved": 0,
        "latest_moved": 0,
        "widened": 0,
        "tightened": 0,
        "vanished": 0,
        "still_windowed": 0,
        "earliest_earlier": 0,
        "earliest_later": 0,
        "latest_later": 0,
        "latest_earlier": 0,
        "per_siglum": {},
    }


def delta_one(row, table):
    """Old bounds -> (new_lo, new_hi, new_n) under the curated table."""
    return rewindow(row.get("dated_works") or [], table)


def fold_row(stats, row, table):
    """Fold one window row into the running stats (shared by compute_delta and the
    selftest so the fixture exercises the exact production fold)."""
    stats["windows"] += 1
    old_lo, old_hi = row.get("earliest"), row.get("latest")
    lo, hi, _nn = delta_one(row, table)

    hit = [s for s in (row.get("dated_works") or []) if s in stats["per_siglum"]]
    for s in hit:
        stats["per_siglum"][s]["citing"] += 1

    if lo is None:
        if old_lo is not None:
            stats["vanished"] += 1
            for s in hit:
                stats["per_siglum"][s]["vanished"] += 1
        return
    stats["still_windowed"] += 1

    e_moved = lo != old_lo
    l_moved = hi != old_hi
    if e_moved:
        stats["earliest_moved"] += 1
        if lo < old_lo:
            stats["earliest_earlier"] += 1
        else:
            stats["earliest_later"] += 1
    if l_moved:
        stats["latest_moved"] += 1
        if hi > old_hi:
            stats["latest_later"] += 1
        else:
            stats["latest_earlier"] += 1
    if e_moved or l_moved:
        stats["moved_any"] += 1
        for s in hit:
            if e_moved:
                stats["per_siglum"][s]["earliest_moved"] += 1
            if l_moved:
                stats["per_siglum"][s]["latest_moved"] += 1
        if lo < old_lo or hi > old_hi:
            stats["widened"] += 1
        if lo > old_lo or hi < old_hi:
            stats["tightened"] += 1
    else:
        stats["unchanged"] += 1


def compute_delta(table, window_path):
    """Recount every committed window under the curated ranges.

    Partition: windows = unchanged + moved_any + vanished (moved_any windows may move
    both ends; earliest/latest_moved overlap freely). per-siglum attribution is
    co-citation-overlapping on purpose.
    """
    stats = new_stats()
    conflicts = sorted(s for s, r in table["works"].items() if r.get("map_date_conflict"))
    for s in conflicts:
        stats["per_siglum"][s] = {"citing": 0, "earliest_moved": 0, "latest_moved": 0,
                                  "vanished": 0}
    with open(window_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not row.get("dated_works"):
                continue
            fold_row(stats, row, table)
    return stats


# ------------------------------------------------------------ re-windowed map


def build_rewindowed_map(source_map, table):
    """Original entries verbatim + curated dating block. `date_corrected` marks the
    map-date conflicts; `dating_valid` is the curated usability flag (false on Spr
    and ŚKDR regardless of conflict)."""
    out = {
        "_meta": {
            "title": "Re-windowed ls_source_map on the corrected work dates",
            "handoff": HANDOFF,
            "created": TODAY,
            "derived_from": {
                "ls_source_map.json": {"sha256": sha256_file(MAP_PATH)},
                "work_dating_table.json": {
                    "sha256": sha256_file(TABLE_PATH),
                    "handoff": "H3790 (C2 phase 2, curated per-work dating table)",
                },
            },
            "method": "per-siglum curated range (earliest/latest) from "
                      "work_dating_table.json; window arithmetic = "
                      "research/c2p2_dating_table.py::rewindow (dating-invalid sigla "
                      "dropped, not clamped). The phase-1 map and window store are "
                      "read-only inputs and remain the committed record.",
            "corrected_sigla": sorted(s for s, r in table["works"].items()
                                      if r.get("map_date_conflict")),
            "open_decisions": "C2P2-D1…D11 remain open human decisions; the dating-"
                              "invalid drop convention is C2P2-D10 and is NOT closed "
                              "by this artifact.",
            "honesty_contract": "A range is when a WORK was composed per a named "
                                "scholar; never a claim about when a SENSE emerged.",
        }
    }
    for siglum in sorted(source_map):
        entry = dict(source_map[siglum])
        row = table["works"][siglum]
        entry["date_earliest"] = row["earliest"]
        entry["date_latest"] = row["latest"]
        entry["dating_valid"] = row["dating_valid"]
        entry["date_confidence"] = row["confidence"]
        entry["date_corrected"] = bool(row.get("map_date_conflict"))
        out[siglum] = entry
    return out


# --------------------------------------------------------------------- report


def render_report(source_map, table, stats):
    works = table["works"]
    conflicts = sorted((s for s, r in works.items() if r.get("map_date_conflict")),
                       key=lambda s: works[s]["earliest"])
    L = []
    L.append("# C2 — re-window delta report on the corrected work dates")
    L.append("")
    L.append("_Created: %s · Handoff [H4728](https://github.com/gasyoun/Uprava/blob/main/"
             "handoffs/%s-OxAlpha_SanskritLexicography_xwalk-b9-work-dating-rewindow_"
             "14.09.26.md) · Table [C2P2_WORK_DATING_TABLE.md](C2P2_WORK_DATING_TABLE.md) "
             "· Phase 1 [C2P1_ATTESTATION_WINDOW.md](C2P1_ATTESTATION_WINDOW.md)_" % (TODAY, HANDOFF))
    L.append("")
    L.append("_Dr. Mārcis Gasūns_")
    L.append("")
    L.append("**What this is.** H3790 curated 45 sourced date ranges and measured what a "
             "re-window would move — without performing it. This report performs it on a "
             "DERIVED artifact: [ls_source_map_rewindowed.json](../src/ls_source_map_rewindowed.json) "
             "carries the corrected datings beside the untouched phase-1 entries, and every "
             "committed window in "
             "[pwg_sense_attestation_window.jsonl](../src/pwg_sense_attestation_window.jsonl) "
             "is recounted under the curated ranges below. The phase-1 map and window store "
             "are read-only inputs; nothing is rewritten.")
    L.append("")
    L.append("**Method.** Window bounds under the curated table = `min(earliest)` / "
             "`max(latest)` over the sense's cited works with `dating_valid: true` "
             "(`c2p2_dating_table.py::rewindow`, selftest-proven). Dating-invalid sigla "
             "(`Spr`, `ŚKDR`) are dropped, not clamped — the curated table's own committed "
             "semantics. The store-wide drop convention is the open human decision "
             "**C2P2-D10**: nothing here closes it, and no window store is rewritten.")
    L.append("")
    L.append("## The seven corrections")
    L.append("")
    L.append("| Siglum | Work | Phase-1 point | Curated range | Confidence | Effect |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for s in conflicts:
        r = works[s]
        effect = ("dropped (dating-invalid)" if not r["dating_valid"]
                  else "repointed into the sourced range")
        L.append("| `%s` | %s | %s | %s – %s | %s | %s |" % (
            s, r["name"], fmt_year(r["map_date"]), fmt_year(r["earliest"]),
            fmt_year(r["latest"]), r["confidence"], effect))
    L.append("")
    L.append("## Date-range recount (%s windows with ≥1 dated work)" % n(stats["windows"]))
    L.append("")
    L.append("| Measure | Windows |")
    L.append("| --- | --- |")
    L.append("| windows recounted | %s |" % n(stats["windows"]))
    L.append("| bounds unchanged | %s |" % n(stats["unchanged"]))
    L.append("| any bound moved | %s |" % n(stats["moved_any"]))
    L.append("| `earliest` moved | %s (earlier %s · later %s) |"
             % (n(stats["earliest_moved"]), n(stats["earliest_earlier"]),
                n(stats["earliest_later"])))
    L.append("| `latest` moved | %s (later %s · earlier %s) |"
             % (n(stats["latest_moved"]), n(stats["latest_later"]),
                n(stats["latest_earlier"])))
    L.append("| any bound widened | %s |" % n(stats["widened"]))
    L.append("| any bound tightened | %s |" % n(stats["tightened"]))
    L.append("| window VANISHED (only dated works were dating-invalid) | %s |"
             % n(stats["vanished"]))
    L.append("")
    L.append("Most movement is the point→range change itself (a work that was one number "
             "is now a bracket, so bounds widen by construction) plus the seven real "
             "corrections; `Spr`'s drop also TIGHTENS bounds it had falsely set and "
             "vanishes windows whose only dated works were invalid. A window may count "
             "as widened AND tightened when different cited works pull its two ends "
             "opposite ways.")
    L.append("")
    L.append("## Per-siglum attribution (windows citing each corrected siglum)")
    L.append("")
    L.append("Co-citation overlaps allowed — one window can move for two corrections.")
    L.append("")
    L.append("| Siglum | windows citing | `earliest` moved | `latest` moved | vanished |")
    L.append("| --- | --- | --- | --- | --- |")
    for s in conflicts:
        p = stats["per_siglum"][s]
        L.append("| `%s` | %s | %s | %s | %s |" % (
            s, n(p["citing"]), n(p["earliest_moved"]), n(p["latest_moved"]),
            n(p["vanished"])))
    L.append("")
    L.append("## Carried, unchanged")
    L.append("")
    L.append("- **C7 residue:** 115,354 citation instances across 2,607 distinct sigla "
             "still resolve to no work in the map; every window remains a conservative "
             "lower bound. This re-window widens nothing about C7.")
    L.append("- **Open decisions:** C2P2-D1…D11 (eleven contested datings) remain open; "
             "the vote sheet "
             "[pwg_c2p2_work_dating_11.html](https://gasyoun.github.io/vote/sheets/pwg_c2p2_work_dating_11.html) "
             "is unvoted. This artifact changes no vote.")
    L.append("- **Phase-1 store:** [pwg_sense_attestation_window.jsonl](../src/pwg_sense_attestation_window.jsonl) "
             "and [ls_source_map.json](../src/ls_source_map.json) are byte-identical to "
             "phase 1. A re-windowed window store is deliberately NOT written until the "
             "D-decisions settle the convention.")
    L.append("")
    L.append("## Reproduce")
    L.append("")
    L.append("```sh")
    L.append("cd RussianTranslation/research")
    L.append("python c2p1_rewindow.py --selftest   # fixture tests")
    L.append("python c2p1_rewindow.py --check      # gate: recompute + invariants")
    L.append("python c2p1_rewindow.py              # regenerate both artifacts")
    L.append("```")
    L.append("")
    return "\n".join(L) + "\n"


# -------------------------------------------------------------------- checking


def check(source_map, table, stats):
    fails = list(validate(source_map, table))
    if set(source_map) != set(table["works"]):
        fails.append("map/table siglum sets differ")
    if stats["unchanged"] + stats["moved_any"] + stats["vanished"] != stats["windows"]:
        fails.append("recount does not sum: unchanged %d + moved_any %d + "
                     "vanished %d != windows %d"
                     % (stats["unchanged"], stats["moved_any"], stats["vanished"],
                        stats["windows"]))
    if stats["still_windowed"] + stats["vanished"] != stats["windows"]:
        fails.append("still-windowed %d + vanished %d != windows %d"
                     % (stats["still_windowed"], stats["vanished"], stats["windows"]))
    if stats["unchanged"] + stats["moved_any"] != stats["still_windowed"]:
        fails.append("unchanged %d + moved_any %d != still_windowed %d"
                     % (stats["unchanged"], stats["moved_any"],
                        stats["still_windowed"]))
    if stats["earliest_earlier"] + stats["earliest_later"] != stats["earliest_moved"]:
        fails.append("earliest direction counts do not sum")
    if stats["latest_later"] + stats["latest_earlier"] != stats["latest_moved"]:
        fails.append("latest direction counts do not sum")
    for s, p in stats["per_siglum"].items():
        if p["citing"] > stats["windows"]:
            fails.append("per-siglum citing %d > windows %d for %s"
                         % (p["citing"], stats["windows"], s))
    return fails


# --------------------------------------------------------------------- selftest


def selftest():
    fx = {
        "sources": {"r": {"citation": "X"}},
        "decisions": {"D": "drop or keep"},
        "works": {
            "GOOD": {"name": "G", "map_date": 100, "earliest": 50, "latest": 150,
                     "confidence": "consensus", "dating_valid": True,
                     "map_date_conflict": False,
                     "sources": [{"ref": "r", "claim": "c", "verified": "reference-only"}]},
            "FIXED": {"name": "F", "map_date": 450, "earliest": 650, "latest": 800,
                      "confidence": "consensus", "dating_valid": True,
                      "map_date_conflict": True,
                      "sources": [{"ref": "r", "claim": "c", "verified": "reference-only"}]},
            "BAD": {"name": "B", "map_date": 600, "earliest": 1863, "latest": 1873,
                    "confidence": "invalid", "dating_valid": False,
                    "map_date_conflict": True, "decide": "D",
                    "sources": [{"ref": "r", "claim": "c", "verified": "reference-only"}]},
        },
    }
    smap = {"GOOD": {"date": 100}, "FIXED": {"date": 450}, "BAD": {"date": 600}}

    # prior-art maths still green through the import
    assert rewindow(["GOOD", "BAD"], fx) == (50, 150, 1)
    assert rewindow(["BAD"], fx) == (None, None, 0)

    # delta arithmetic on fixtures, folded by the PRODUCTION fold_row
    st = new_stats()
    st["per_siglum"] = {s: {"citing": 0, "earliest_moved": 0, "latest_moved": 0,
                            "vanished": 0} for s in fx["works"]}
    rows = [
        {"dated_works": ["GOOD"], "earliest": 100, "latest": 100},         # widens
        {"dated_works": ["FIXED"], "earliest": 450, "latest": 450},        # widened+tightened
        {"dated_works": ["BAD"], "earliest": 600, "latest": 600},          # vanishes
        {"dated_works": ["GOOD", "BAD"], "earliest": 100, "latest": 600},  # tightened hi
    ]
    for row in rows:
        fold_row(st, row, fx)

    # row1 (100,100)->(50,150): e earlier, l later, widened
    # row2 (450,450)->(650,800): e later, l later, widened AND tightened
    # row3 (600,600)-> vanished
    # row4 (100,600)->(50,150): e earlier, l earlier, widened+tightened
    assert st == dict(st, unchanged=0, moved_any=3, earliest_moved=3, latest_moved=3,
                      widened=3, tightened=2, vanished=1, still_windowed=3,
                      earliest_earlier=2, earliest_later=1, latest_later=2,
                      latest_earlier=1), st
    assert st["per_siglum"]["BAD"] == {"citing": 2, "earliest_moved": 1,
                                       "latest_moved": 1, "vanished": 1}, st["per_siglum"]
    assert st["per_siglum"]["GOOD"] == {"citing": 2, "earliest_moved": 2,
                                        "latest_moved": 2, "vanished": 0}
    assert st["per_siglum"]["FIXED"] == {"citing": 1, "earliest_moved": 1,
                                         "latest_moved": 1, "vanished": 0}
    assert check(smap, fx, st) == [], check(smap, fx, st)

    # recount gate actually fails on a corrupted partition
    bad = dict(st, unchanged=5)
    assert any("does not sum" in f for f in check(smap, fx, bad))

    # re-windowed map: originals verbatim + dating block + corrected flag only on conflicts
    rmap = build_rewindowed_map(smap, fx)
    assert "_meta" in rmap and rmap["FIXED"]["date"] == 450  # original untouched
    assert rmap["FIXED"]["date_earliest"] == 650 and rmap["FIXED"]["date_corrected"] is True
    assert rmap["GOOD"]["date_corrected"] is False
    assert rmap["BAD"]["dating_valid"] is False and rmap["BAD"]["date_corrected"] is True
    assert set(rmap["GOOD"]) == {"date", "date_earliest", "date_latest", "dating_valid",
                                 "date_confidence", "date_corrected"}

    print("selftest OK")
    return 0


# ------------------------------------------------------------------------ main


def main():
    ap = argparse.ArgumentParser(
        description=(__doc__ or "c2p1_rewindow").splitlines()[0])
    ap.add_argument("--selftest", action="store_true", help="run the fixture tests")
    ap.add_argument("--check", action="store_true",
                    help="recompute + invariants; exit 1 on drift; no writes")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    source_map = load_json(MAP_PATH)
    table = load_json(TABLE_PATH)
    stats = compute_delta(table, WINDOW_PATH)
    fails = check(source_map, table, stats)

    if args.check:
        for f in fails:
            print("FAIL %s" % f)
        print("%s — %s windows recounted, %d failures"
              % ("PASS" if not fails else "FAIL", n(stats["windows"]), len(fails)))
        return 1 if fails else 0

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        print("refusing to emit over %d invariant failures" % len(fails))
        return 1

    rmap = build_rewindowed_map(source_map, table)
    map_text = json.dumps(rmap, ensure_ascii=False, indent=1, sort_keys=False) + "\n"
    with open(OUT_MAP_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(map_text)
    report_text = render_report(source_map, table, stats)
    with open(OUT_REPORT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report_text)

    print("windows recounted: %s | unchanged %s | moved_any %s | earliest moved %s | "
          "latest moved %s | widened %s | tightened %s | vanished %s"
          % (n(stats["windows"]), n(stats["unchanged"]), n(stats["moved_any"]),
             n(stats["earliest_moved"]), n(stats["latest_moved"]),
             n(stats["widened"]), n(stats["tightened"]), n(stats["vanished"])))
    print("wrote %s" % OUT_MAP_PATH)
    print("wrote %s" % OUT_REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
