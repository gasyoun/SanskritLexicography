"""Implement the H3169 memo section 7 EWA shape as a no-guess extension (H4726).

EWA (Mayrhofer, Etymologisches Wörterbuch des Altindoarischen, 1986-2001) is
NOT in the crosswalk yet: no EWA heading index exists anywhere in the estate
(probed 15-09-2026, see the acquisition report next to this file's outputs).
The memo prescribed the shape the EWA leg will need when it lands:

1. a `source` column (`KEWA` / `EWA`) beside `lane`,
2. a `supersedes` relation, not a merge - an EWA row for the same headword
   marks the KEWA row superseded and both stay,
3. `vol` stays a string (EWA's three volumes number independently).

This script implements that shape NOW on the KEWA rows only - every row
gains `source=KEWA`, empty `supersedes` and reserved `ewa_volcol`/`ewa_no`
slots - and never rewrites the original crosswalk.  Because zero EWA rows are
emitted, the lane-coverage recount MUST reproduce `etym_lane_coverage.json`
exactly; any drift is a hard failure.

It also measures - as a report statistic only, never as crosswalk rows - how
far the one EWA footprint that DOES exist on disk reaches into PWG key1:
the `ewa_volcol`/`ewa_no` pointer columns of
`dhatup_multisource_crosswalk.json` (H4478, from MG's own Concordance).
Those columns' semantics are UNCONFIRMED (numeric monotonic values vs German
gloss leakage in sibling rows), so no row from them may enter the crosswalk;
the readiness count is honest only as a census of what could be joined.

Usage:
    python ewa_extend.py [--github-root DIR] [--indir DIR] [--outdir DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = "C:/Users/user/Documents/GitHub"
KEWA_CROSSWALK = "kewa_pwg_crosswalk.tsv"
EXTENDED = "kewa_ewa_pwg_crosswalk_extended.tsv"
COVERAGE_BASELINE = "etym_lane_coverage.json"
DHATUP = "SanskritLexicography/RussianTranslation/src/data/dhatup_multisource_crosswalk.json"

LANE = "modern-IE"  # KEWA and EWA are both the modern IE lane, never merged
BASE_COLS = ["lane", "kewa_seq", "vol", "page", "heading_idx", "kewa_slp1",
             "match_basis", "pwg_key1", "witness", "n_candidates",
             "lemma_route", "routes_agree", "flags"]
EXT_COLS = ["lane", "source"] + BASE_COLS[1:] + ["supersedes", "ewa_volcol", "ewa_no"]


def load_pwg(root: str) -> set[str]:
    path = os.path.join(root, "SanskritLexicography/HeadwordLists/now-2026/PWG-unique-key1-106082.txt")
    with open(path, encoding="utf-8") as fh:
        return {line.strip() for line in fh if line.strip()}


def get_transcoder(root: str):
    """The canonical sanskrit-util transcoder from the caller's GitHub root."""
    sys.path.insert(0, os.path.join(root, "sanskrit-util", "py"))
    try:
        from sanskrit_util import to_slp1  # noqa: E402
        return to_slp1
    except ImportError:  # pragma: no cover - layout differs
        return None


def read_crosswalk(indir: str) -> tuple[list[dict], list[str]]:
    path = os.path.join(indir, KEWA_CROSSWALK)
    with open(path, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        rows = [dict(zip(head, line.rstrip("\n").split("\t"))) for line in fh if line.strip()]
    return rows, head


def lane_coverage(root: str, indir: str, crosswalk: str) -> dict:
    """Mirror lane_coverage.py exactly, over an arbitrary crosswalk file."""
    pwg = load_pwg(root)
    traditional: set[str] = set()
    etym_path = os.path.join(root, "csl-orig/v02/pwg/pwg_etymology.tsv")
    with open(etym_path, encoding="utf-8") as fh:
        col = fh.readline().rstrip("\n").split("\t").index("headword_slp1")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > col and parts[col]:
                traditional.add(parts[col])
    modern: set[str] = set()
    with open(os.path.join(indir, crosswalk), encoding="utf-8") as fh:
        ci = fh.readline().rstrip("\n").split("\t").index("pwg_key1")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > ci and parts[ci]:
                modern.update(p for p in parts[ci].split("|") if p)
    return {
        "pwg_key1_headwords": len(pwg),
        "lane_modern_ie_kewa": len(modern),
        "lane_traditional_cologne": len(traditional & pwg),
        "both_lanes": len(modern & traditional),
        "modern_only": len(modern - traditional),
        "traditional_only": len((traditional & pwg) - modern),
        "pwg_with_no_lane": len(pwg - modern - traditional),
    }


def root_slp1(raw: str, to_slp1) -> str | None:
    """Palsule citation root -> SLP1, or None when it will not transcode.

    Leading homonym numerals (`1akṣ`) are not lexical and are dropped;
    Palsule's print convention ç is his ś and is folded before transcoding.
    """
    if to_slp1 is None:
        return None
    body = raw.strip().lstrip("0123456789. ").replace("ç", "ś")
    if not body:
        return None
    try:
        out = to_slp1(body)
    except Exception:
        return None
    return out if out and all(c in "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh" for c in out) else None


def readiness(root: str, to_slp1) -> dict:
    """Census the only on-disk EWA footprint.  Report-only; never rows."""
    path = os.path.join(root, DHATUP)
    data = json.load(open(path, encoding="utf-8"))
    rows = [r for r in data["rows"] if r.get("ewa_volcol") or r.get("ewa_no")]
    with_root = [r for r in rows if r.get("palsule_root")]
    pwg = load_pwg(root)
    buckets = {"exact_in_pwg_key1": [], "transcode_failed": [], "not_in_pwg": []}
    for r in with_root:
        key = root_slp1(r["palsule_root"], to_slp1)
        if key is None:
            buckets["transcode_failed"].append(r["palsule_root"])
        elif key in pwg:
            buckets["exact_in_pwg_key1"].append(key)
        else:
            buckets["not_in_pwg"].append(key)
    return {
        "source": "dhatup_multisource_crosswalk.json (H4478)",
        "caveat": ("Column semantics UNCONFIRMED - ewa_volcol is numeric-monotonic "
                   "(page/column-like), ewa_no mixes entry numbers with German glosses; "
                   "sibling columns (whitney_root, verba_root) carry page numbers. "
                   "READINESS STAT ONLY - none of this may enter the crosswalk until "
                   "the Concordance columns are documented and the real EWA index lands."),
        "rows_with_any_ewa_pointer": len(rows),
        "with_palsule_root": len(with_root),
        "exact_in_pwg_key1": len(buckets["exact_in_pwg_key1"]),
        "transcode_failed": len(buckets["transcode_failed"]),
        "not_in_pwg": len(buckets["not_in_pwg"]),
        "examples_exact": sorted(set(buckets["exact_in_pwg_key1"]))[:10],
        "examples_not_in_pwg": sorted(set(buckets["not_in_pwg"]))[:10],
        "examples_transcode_failed": sorted(set(buckets["transcode_failed"]))[:10],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github-root", default=DEFAULT_ROOT)
    ap.add_argument("--indir", default=os.path.join(HERE, "..", "..", "data", "etym"))
    args = ap.parse_args()
    indir = os.path.abspath(args.indir)
    root = os.path.abspath(args.github_root)

    rows, cols = read_crosswalk(indir)
    assert cols == BASE_COLS, f"unexpected crosswalk schema: {cols}"
    if len(rows) != 11418:
        raise SystemExit(f"FAIL: expected 11,418 KEWA rows, got {len(rows)} "
                         "(an EWA rung may have landed - re-baseline first)")

    # extension: source/supersedes/reserved EWA slots, byte-preserving otherwise
    with open(os.path.join(indir, EXTENDED), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(EXT_COLS) + "\n")
        for r in rows:
            vol = r["vol"]  # string discipline: never coerced to int
            if vol.isdigit():
                raise SystemExit(f"FAIL: vol column carries an integer value {vol!r} - "
                                 "EWA's three volumes number independently, keep strings")
            out = [r["lane"], "KEWA"] + [r[c] for c in BASE_COLS[1:]] + ["", "", ""]
            fh.write("\t".join(out) + "\n")

    # verify: coverage recount must reproduce the committed baseline exactly
    baseline = json.load(open(os.path.join(indir, COVERAGE_BASELINE), encoding="utf-8"))
    base_recount = lane_coverage(root, indir, KEWA_CROSSWALK)
    ext_recount = lane_coverage(root, indir, EXTENDED)
    drift = {}
    for k, v in baseline.items():
        if k in base_recount and base_recount[k] != v:
            drift[f"baseline:{k}"] = (v, base_recount[k])
        if k in ext_recount and ext_recount[k] != v:
            drift[f"extended:{k}"] = (v, ext_recount[k])
    if drift:
        print(json.dumps(drift, indent=2))
        raise SystemExit("FAIL: coverage drift vs etym_lane_coverage.json")

    # verify: KEWA payload untouched - same row count, same pwg_key1 column
    with open(os.path.join(indir, EXTENDED), encoding="utf-8") as fh:
        ext_head = fh.readline().rstrip("\n").split("\t")
        ext_rows = [line.rstrip("\n").split("\t") for line in fh if line.strip()]
    ci, ki = ext_head.index("pwg_key1"), ext_head.index("kewa_slp1")
    if len(ext_rows) != len(rows):
        raise SystemExit("FAIL: extended row count drifted")
    if {r[ci] for r in ext_rows} != {r["pwg_key1"] for r in rows}:
        raise SystemExit("FAIL: pwg_key1 set drifted in the extension")

    report = {
        "handoff": "H4726",
        "built": "2026-09-15",
        "shape": "H3169 memo section 7: source column beside lane, supersedes relation (both stay), vol as string",
        "rows_extended": len(ext_rows),
        "ewa_rows_emitted": 0,
        "why_zero_ewa_rows": ("no EWA heading index exists in the estate (probed 15-09-2026); "
                              "the only on-disk EWA footprint is H4478's Concordance pointer "
                              "columns with unconfirmed semantics - see readiness below and "
                              "EWA_ACQUISITION_REPORT_15-09-2026.md"),
        "coverage_recount_vs_baseline": "PASS (all seven counts identical)",
        "baseline_counts": {k: baseline[k] for k in base_recount},
        "ewa_readiness_census": readiness(root, get_transcoder(root)),
    }
    dst = os.path.join(indir, "ewa_extension_report.json")
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"extended: {EXTENDED} ({len(ext_rows)} rows, source=KEWA, EWA slots reserved)")
    print(f"coverage recount vs baseline: PASS")
    print(json.dumps(report["ewa_readiness_census"], ensure_ascii=False, indent=2)[:400])
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
