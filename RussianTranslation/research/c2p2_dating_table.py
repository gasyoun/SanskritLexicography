"""Ceiling C2 phase 2 — validate the curated per-work dating table and report its impact.

Consumes (never rewrites):
  RussianTranslation/src/ls_source_map.json                 — phase 1's 45 dated works
  RussianTranslation/src/work_dating_table.json             — this handoff's curated table
  RussianTranslation/src/pwg_sense_attestation_window.jsonl — phase 1's per-sense windows

Emits:
  --check     gate: every siglum covered, every date sourced, every contested row routed
  --report    regenerates the generated block of research/C2P2_WORK_DATING_TABLE.md
  --selftest  fixture tests for the validator and the re-window arithmetic

The re-window figures under --report are a MEASUREMENT of what the curated table would
change. Nothing here writes a second window store: phase 1's jsonl is read-only input,
per H3790's "consume, do not re-derive" fence.

H3790 · roadmap item C2 · 01-09-2026
"""

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
SRC = os.path.join(RT, "src")

MAP_PATH = os.path.join(SRC, "ls_source_map.json")
TABLE_PATH = os.path.join(SRC, "work_dating_table.json")
WINDOW_PATH = os.path.join(SRC, "pwg_sense_attestation_window.jsonl")
MEMO_PATH = os.path.join(HERE, "C2P2_WORK_DATING_TABLE.md")

START = "<!-- c2p2:generated:start -->"
END = "<!-- c2p2:generated:end -->"

CONFIDENCE = ("anchored", "consensus", "contested", "invalid")
VERIFIED = ("on-disk-quote", "reference-only")


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- check


def validate(source_map, table):
    """Return a list of failure strings. Empty list == the gate passes."""
    fails = []
    works = table["works"]
    sources = table["sources"]

    missing = sorted(set(source_map) - set(works))
    extra = sorted(set(works) - set(source_map))
    if missing:
        fails.append("sigla in ls_source_map.json with no curated row: %s" % ", ".join(missing))
    if extra:
        fails.append("curated rows for sigla absent from ls_source_map.json: %s" % ", ".join(extra))

    for siglum in sorted(works):
        row = works[siglum]
        where = "[%s]" % siglum

        for field in ("name", "map_date", "earliest", "latest", "confidence", "dating_valid", "sources"):
            if field not in row:
                fails.append("%s missing field %r" % (where, field))
        if fails and any(where in f for f in fails[-1:]):
            continue

        if row["confidence"] not in CONFIDENCE:
            fails.append("%s confidence %r not one of %s" % (where, row["confidence"], CONFIDENCE))
        if row["earliest"] > row["latest"]:
            fails.append("%s earliest %d > latest %d" % (where, row["earliest"], row["latest"]))

        # Every date carries a citation. A date without one is a gap, not a guess.
        if not row["sources"]:
            fails.append("%s has a date with no source — that is a gap, not a guess" % where)
        for i, src in enumerate(row["sources"]):
            if src.get("ref") not in sources:
                fails.append("%s source[%d] ref %r not in the sources block" % (where, i, src.get("ref")))
            if not src.get("claim"):
                fails.append("%s source[%d] has no claim text" % (where, i))
            if src.get("verified") not in VERIFIED:
                fails.append("%s source[%d] verified %r not one of %s" % (where, i, src.get("verified"), VERIFIED))
            if src.get("verified") == "on-disk-quote":
                ref = sources.get(src.get("ref"), {})
                if not ref.get("on_disk"):
                    fails.append("%s source[%d] claims an on-disk quote but %r has no on_disk path"
                                 % (where, i, src.get("ref")))
                if not src.get("locus"):
                    fails.append("%s source[%d] is an on-disk quote with no printed locus" % (where, i))

        # Contested datings are routed to a decision, never self-ruled.
        if row["confidence"] == "contested" and not row.get("decide"):
            fails.append("%s is contested but carries no @DECIDE id" % where)
        if row.get("decide") and row["decide"] not in table["decisions"]:
            fails.append("%s decide %r is not in the decisions block" % (where, row["decide"]))

        # A siglum that cannot date anything must say so in the machine field too.
        if row["confidence"] == "invalid" and row["dating_valid"]:
            fails.append("%s confidence invalid but dating_valid true" % where)

        # map_date_conflict must agree with the arithmetic, so it cannot drift.
        conflict = not (row["earliest"] <= row["map_date"] <= row["latest"])
        if bool(row.get("map_date_conflict")) != conflict:
            fails.append("%s map_date_conflict is %r but map_date %d vs range %d..%d says %r"
                         % (where, row.get("map_date_conflict"), row["map_date"],
                            row["earliest"], row["latest"], conflict))
        if row["map_date"] != source_map[siglum]["date"]:
            fails.append("%s map_date %d does not match ls_source_map.json's %d"
                         % (where, row["map_date"], source_map[siglum]["date"]))

    for did in sorted(table["decisions"]):
        if not any(w.get("decide") == did for w in works.values()):
            fails.append("decision %s is declared but no work routes to it" % did)

    return fails


# --------------------------------------------------------------------- measurement


def rewindow(dated_works, table):
    """Bounds a window would take under the curated table, dropping dating-invalid sigla.

    Returns (earliest, latest, n_valid_works). (None, None, 0) when nothing datable is left.
    """
    works = table["works"]
    lo = hi = None
    n = 0
    for siglum in dated_works:
        row = works.get(siglum)
        if row is None or not row["dating_valid"]:
            continue
        n += 1
        lo = row["earliest"] if lo is None else min(lo, row["earliest"])
        hi = row["latest"] if hi is None else max(hi, row["latest"])
    return lo, hi, n


def measure(table, window_path):
    works = table["works"]
    invalid = {s for s, r in works.items() if not r["dating_valid"]}
    stats = {
        "windows": 0,
        "touching_invalid": 0,
        "only_invalid": 0,
        "latest_set_by_invalid": 0,
        "earliest_moves": 0,
        "latest_moves": 0,
        "per_invalid_siglum": {s: 0 for s in sorted(invalid)},
    }
    with open(window_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            dw = row.get("dated_works") or []
            if not dw:
                continue
            stats["windows"] += 1
            hit = [s for s in dw if s in invalid]
            if hit:
                stats["touching_invalid"] += 1
                for s in hit:
                    stats["per_invalid_siglum"][s] += 1
                if len(hit) == len(dw):
                    stats["only_invalid"] += 1
            lo, hi, _n = rewindow(dw, table)
            if hit and (hi is None or (row.get("latest") is not None and row["latest"] > hi)):
                stats["latest_set_by_invalid"] += 1
            if lo is not None and row.get("earliest") is not None and lo != row["earliest"]:
                stats["earliest_moves"] += 1
            if hi is not None and row.get("latest") is not None and hi != row["latest"]:
                stats["latest_moves"] += 1
    return stats


# ------------------------------------------------------------------------- report


def fmt_year(y):
    return "%d BCE" % (-y) if y < 0 else "%d CE" % y


def decide_sort(did):
    """C2P2-D2 before C2P2-D10 — lexicographic order puts D10 second and reads as a defect."""
    tail = did.rsplit("-D", 1)[-1]
    return (int(tail) if tail.isdigit() else 0, did)


def n(x):
    """Thousands separators; the window counts run to five digits."""
    return "{:,}".format(x)


def fmt_range(row):
    if row["earliest"] == row["latest"]:
        return fmt_year(row["earliest"])
    return "%s – %s" % (fmt_year(row["earliest"]), fmt_year(row["latest"]))


CONF_MARK = {
    "anchored": "⚓ anchored",
    "consensus": "○ consensus",
    "contested": "⚖ contested",
    "invalid": "✖ dating-invalid",
}


def render(source_map, table, stats):
    works = table["works"]
    sources = table["sources"]
    out = []

    out.append("")
    out.append("## The table — 45 sigla, every date sourced")
    out.append("")
    out.append("Sorted by the curated `earliest`. `map` is the point date phase 1 used; a **bold**")
    out.append("map value falls outside the sourced range and is an evidence-decidable correction.")
    out.append("")
    out.append("| Siglum | Work | Curated range | map | Confidence | Source(s) | Decision |")
    out.append("| --- | --- | --- | --- | --- | --- | --- |")
    for siglum in sorted(works, key=lambda s: (works[s]["earliest"], works[s]["latest"], s)):
        row = works[siglum]
        mapv = "**%s**" % fmt_year(row["map_date"]) if row.get("map_date_conflict") else fmt_year(row["map_date"])
        refs = ", ".join(sorted({s["ref"] for s in row["sources"]}))
        out.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (
            siglum, row["name"], fmt_range(row), mapv, CONF_MARK[row["confidence"]],
            refs, row.get("decide") or "—"))
    out.append("")

    counts = {c: sum(1 for r in works.values() if r["confidence"] == c) for c in CONFIDENCE}
    on_disk = sum(1 for r in works.values()
                  for s in r["sources"] if s.get("verified") == "on-disk-quote")
    conflicts = sorted(s for s, r in works.items() if r.get("map_date_conflict"))
    out.append("**Shape:** %d anchored · %d consensus · %d contested · %d dating-invalid. "
               "%d of the citations are quoted from a source held in this repository "
               "(Vogel 1979, with printed page); the rest name the standard reference and are "
               "marked `reference-only` — page-level verification is an open residual, not a claim."
               % (counts["anchored"], counts["consensus"], counts["contested"],
                  counts["invalid"], on_disk))
    out.append("")
    out.append("**Map-date conflicts (%d):** %s — recorded here, **not** written back into "
               "`ls_source_map.json`, which phase 1's committed store consumed."
               % (len(conflicts), ", ".join("`%s`" % s for s in conflicts)))
    out.append("")

    out.append("## Dating-invalid sigla — what phase 1's windows are actually reporting")
    out.append("")
    out.append("Two sigla in the map are not datable Sanskrit works. `Spr.` is Böhtlingk's own")
    out.append("anthology (St. Petersburg, 1863–1873) and `ŚKDR.` a Calcutta compilation of")
    out.append("1821–1858. Both were given ordinary point dates in phase 1 and both therefore")
    out.append("set window bounds that mean nothing about the language.")
    out.append("")
    out.append("| Measure | Windows |")
    out.append("| --- | --- |")
    out.append("| windows with at least one dated work | %s |" % n(stats["windows"]))
    out.append("| … containing a dating-invalid siglum | %s (%.1f%%) |"
               % (n(stats["touching_invalid"]), 100.0 * stats["touching_invalid"] / max(stats["windows"], 1)))
    for siglum, cnt in sorted(stats["per_invalid_siglum"].items(), key=lambda kv: -kv[1]):
        out.append("| … of which cite `%s` | %s |" % (siglum, n(cnt)))
    out.append("| … whose ONLY dated works are invalid (window would vanish) | %s |" % n(stats["only_invalid"]))
    out.append("| windows whose `latest` is set by an invalid siglum | %s |" % n(stats["latest_set_by_invalid"]))
    out.append("")
    out.append("**If the curated table replaced the point dates:** `earliest` would move on %s "
               "windows and `latest` on %s, out of %s. Most of that is not error correction but "
               "the point→range change itself: a work that was one number is now a bracket, so "
               "almost every bound shifts by construction. The %d map-date conflicts and the two "
               "dating-invalid sigla are the part that is a correction. The re-window is "
               "deliberately NOT performed here — phase 1's store is consumed, not re-derived "
               "(H3790), and which convention to use for growth-span works is itself an open "
               "decision (C2P2-D2)."
               % (n(stats["earliest_moves"]), n(stats["latest_moves"]), n(stats["windows"]),
                  sum(1 for r in works.values() if r.get("map_date_conflict"))))
    out.append("")

    out.append("## Contested datings — %d decisions, none self-ruled" % len(table["decisions"]))
    out.append("")
    for did in sorted(table["decisions"], key=decide_sort):
        rows = sorted(s for s, r in works.items() if r.get("decide") == did)
        out.append("- **%s** — %s _(sigla: %s)_" % (did, table["decisions"][did],
                                                    ", ".join("`%s`" % s for s in rows)))
    out.append("")

    out.append("## Bibliography")
    out.append("")
    for key in sorted(sources):
        s = sources[key]
        line = "- **`%s`** — %s" % (key, s["citation"])
        if s.get("on_disk"):
            line += " _(held in this repository: [%s](%s))_" % (s["on_disk"], s["on_disk"])
        if s.get("note"):
            line += " %s" % s["note"]
        out.append(line)
    out.append("")
    return "\n".join(out)


def write_block(memo_path, block):
    with open(memo_path, encoding="utf-8") as fh:
        text = fh.read()
    i, j = text.find(START), text.find(END)
    if i < 0 or j < 0:
        raise SystemExit("generated markers not found in %s" % memo_path)
    new = text[: i + len(START)] + "\n" + block + text[j:]
    if new != text:
        with open(memo_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new)
        return True
    return False


# ----------------------------------------------------------------------- selftest


def selftest():
    table = {
        "sources": {
            "ok": {"citation": "X", "on_disk": "some/file.md"},
            "ref": {"citation": "Y"},
        },
        "decisions": {"D1": "a fork"},
        "works": {
            "A": {"name": "A", "map_date": 100, "earliest": 50, "latest": 150,
                  "confidence": "consensus", "dating_valid": True, "map_date_conflict": False,
                  "sources": [{"ref": "ref", "claim": "c", "verified": "reference-only"}]},
            "B": {"name": "B", "map_date": 900, "earliest": 800, "latest": 850,
                  "confidence": "invalid", "dating_valid": False, "map_date_conflict": True,
                  "decide": "D1",
                  "sources": [{"ref": "ok", "locus": "12", "claim": "c", "verified": "on-disk-quote"}]},
        },
    }
    smap = {"A": {"date": 100}, "B": {"date": 900}}
    fails = validate(smap, table)
    assert fails == [], fails

    # a contested row with no decision must fail
    bad = json.loads(json.dumps(table))
    bad["works"]["A"]["confidence"] = "contested"
    assert any("contested but carries no @DECIDE" in f for f in validate(smap, bad))

    # a date with no source must fail
    bad = json.loads(json.dumps(table))
    bad["works"]["A"]["sources"] = []
    assert any("gap, not a guess" in f for f in validate(smap, bad))

    # a drifted map_date_conflict flag must fail
    bad = json.loads(json.dumps(table))
    bad["works"]["B"]["map_date_conflict"] = False
    assert any("map_date_conflict" in f for f in validate(smap, bad))

    # an uncovered siglum must fail
    assert any("no curated row" in f for f in validate({"A": {"date": 100}, "B": {"date": 900},
                                                        "C": {"date": 1}}, table))

    # re-window drops the invalid siglum, and vanishes when only invalid sigla remain
    assert rewindow(["A", "B"], table) == (50, 150, 1)
    assert rewindow(["B"], table) == (None, None, 0)
    assert rewindow([], table) == (None, None, 0)

    print("selftest OK")
    return 0


# --------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="validate the table; exit 1 on any failure")
    ap.add_argument("--report", action="store_true", help="regenerate the memo's generated block")
    ap.add_argument("--selftest", action="store_true", help="run the fixture tests")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    source_map = load_json(MAP_PATH)
    table = load_json(TABLE_PATH)
    fails = validate(source_map, table)

    if args.check or not args.report:
        for f in fails:
            print("FAIL %s" % f)
        print("%s — %d sigla, %d curated rows, %d failures"
              % ("PASS" if not fails else "FAIL", len(source_map), len(table["works"]), len(fails)))
        if fails:
            return 1
        if not args.report:
            return 0

    if fails:
        print("refusing to render a report over an invalid table (%d failures)" % len(fails))
        return 1

    stats = measure(table, WINDOW_PATH)
    changed = write_block(MEMO_PATH, render(source_map, table, stats))
    print("%s %s" % ("rewrote" if changed else "unchanged", MEMO_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
