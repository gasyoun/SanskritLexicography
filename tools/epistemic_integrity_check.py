#!/usr/bin/env python3
"""epistemic_integrity_check.py — structural integrity gate for the FINDINGS core
and its seven epistemic sibling registries (H1361).

Checks, over `--dir` (default `.`):

  1. duplicate §-numbers   — no two `### §N.` headings in one registry share N
  2. heading ↔ Index parity — in FINDINGS.md, every `### §N.` heading has exactly
                              one Index entry `[§N. …]`, and every Index entry has
                              a heading (no dangling index rows)
  3. dangling §N reference  — an Index `[§N.]` row pointing at a non-existent heading
  4. next-free marker       — FINDINGS' "currently §N" marker equals max(heading)+1
  5. dashboard ↔ file parity— findings_dashboard/data.json and
                              epistemic_dashboard/epistemic.json report a findings
                              total equal to the distinct-heading count, and carry
                              no null/None importance (every finding is classified)

Import-free beyond the stdlib. stdout/stderr reconfigured to utf-8. Exits 1 with a
per-defect report if any check fails, 0 if all hold. Designed to run in CI before the
dashboard builders and as a pre-commit hook.

    python tools/epistemic_integrity_check.py --dir .
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REGISTRIES = ["FINDINGS.md", "CONTRADICTIONS.md", "DEAD_ENDS.md", "GAPS.md",
              "ASSUMPTIONS.md", "RECIPES.md", "STALENESS.md", "GLOSSARY.md"]

HEADING = re.compile(r"^#{2,4}\s*§\s*(\d+)([a-z]?)\.", re.M)
INDEX_ENTRY = re.compile(r"\[§\s*(\d+)([a-z]?)\.")
MARKER = re.compile(r"currently\s*§\s*(\d+)")


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def headings(text):
    """Ordered list of (number, suffix) heading keys."""
    return [(int(n), suf) for n, suf in HEADING.findall(text)]


def check_duplicates(defects, name, text):
    seen = {}
    for n, suf in headings(text):
        seen.setdefault((n, suf), 0)
        seen[(n, suf)] += 1
    dups = {f"§{n}{suf}": c for (n, suf), c in seen.items() if c > 1}
    if dups:
        for key, c in sorted(dups.items()):
            defects.append(f"{name}: duplicate heading {key} ({c} headings share it)")


def index_block(text):
    """The lines of FINDINGS.md's `## Index` section (up to the next `## `)."""
    m = re.search(r"^##\s+Index\s*$", text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"^##\s+(?!Index)", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def check_findings_index(defects, text):
    idx = index_block(text)
    if idx is None:
        defects.append("FINDINGS.md: no `## Index` section found")
        return
    head_nums = {n for n, suf in headings(text) if suf == ""}
    idx_nums = {int(n) for n, suf in INDEX_ENTRY.findall(idx) if suf == ""}
    missing = sorted(head_nums - idx_nums)
    dangling = sorted(idx_nums - head_nums)
    if missing:
        defects.append(f"FINDINGS.md: {len(missing)} heading(s) missing from Index: "
                       + ", ".join(f"§{n}" for n in missing))
    if dangling:
        defects.append(f"FINDINGS.md: {len(dangling)} Index row(s) with no heading "
                       f"(dangling): " + ", ".join(f"§{n}" for n in dangling))


def check_marker(defects, text):
    m = MARKER.search(text)
    nums = [n for n, suf in headings(text)]
    if not nums:
        return
    want = max(nums) + 1
    if not m:
        defects.append(f"FINDINGS.md: no 'currently §N' next-free marker found "
                       f"(expected §{want})")
    elif int(m.group(1)) != want:
        defects.append(f"FINDINGS.md: next-free marker says §{m.group(1)}, "
                       f"expected §{want} (max heading §{max(nums)} + 1)")


def check_dashboard_parity(defects, root, distinct_findings):
    fd = root / "findings_dashboard" / "data.json"
    ed = root / "epistemic_dashboard" / "epistemic.json"
    fdt = read(fd)
    if fdt is not None:
        try:
            d = json.loads(fdt)
            total = d.get("counts", {}).get("total")
            if total != distinct_findings:
                defects.append(f"findings_dashboard/data.json total={total} != "
                               f"{distinct_findings} distinct FINDINGS headings "
                               f"(stale — regenerate)")
            nulls = [f.get("n") for f in d.get("findings", [])
                     if f.get("importance") in (None, "None")]
            if nulls:
                defects.append(f"findings_dashboard/data.json: {len(nulls)} finding(s) "
                               f"with null importance (unclassified): "
                               + ", ".join(f"§{n}" for n in nulls[:20])
                               + (" …" if len(nulls) > 20 else ""))
        except json.JSONDecodeError:
            defects.append("findings_dashboard/data.json: invalid JSON")
    edt = read(ed)
    if edt is not None:
        try:
            d = json.loads(edt)
            core = d.get("core") or {}
            total = core.get("total")
            if total != distinct_findings:
                defects.append(f"epistemic_dashboard/epistemic.json core.total={total} "
                               f"!= {distinct_findings} distinct FINDINGS headings "
                               f"(stale — regenerate)")
            bi = core.get("by_importance") or {}
            s = sum(v for v in bi.values() if isinstance(v, int))
            if total is not None and s != total:
                defects.append(f"epistemic_dashboard/epistemic.json core.by_importance "
                               f"sums to {s} but core.total={total} "
                               f"({total - s} finding(s) unclassified)")
        except json.JSONDecodeError:
            defects.append("epistemic_dashboard/epistemic.json: invalid JSON")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=".", help="repo root (default: .)")
    ap.add_argument("--structural-only", action="store_true",
                    help="skip the dashboard↔file parity check (use before the "
                         "dashboard builders regenerate the JSON; the full check "
                         "runs after the build and in pre-commit)")
    args = ap.parse_args()
    root = Path(args.dir).resolve()

    defects = []
    findings_text = None
    for fname in REGISTRIES:
        text = read(root / fname)
        if text is None:
            continue
        check_duplicates(defects, fname, text)
        if fname == "FINDINGS.md":
            findings_text = text

    distinct = 0
    if findings_text is not None:
        distinct = len({n for n, suf in headings(findings_text) if suf == ""})
        check_findings_index(defects, findings_text)
        check_marker(defects, findings_text)
        if not args.structural_only:
            check_dashboard_parity(defects, root, distinct)
    else:
        defects.append(f"FINDINGS.md not found under {root}")

    if defects:
        print(f"EPISTEMIC INTEGRITY: FAIL — {len(defects)} defect(s)\n", file=sys.stderr)
        for d in defects:
            print(f"  ✗ {d}", file=sys.stderr)
        print(f"\n({distinct} distinct FINDINGS headings scanned)", file=sys.stderr)
        return 1
    print(f"EPISTEMIC INTEGRITY: OK — {distinct} distinct FINDINGS headings, "
          f"Index parity holds, no duplicate §-numbers, dashboards in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
