#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a role-tagged census of RussianTranslation pipeline scripts.

Emits SCRIPT_CENSUS.md next to this file (committed optional; deep manual
points at the generator + last emit). Stdlib only.

Usage (from RussianTranslation/):
  python src/pilot/script_census.py
  python src/pilot/script_census.py --check   # exit 1 if on-disk census drifts
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
RT_ROOT = HERE.parent.parent  # RussianTranslation/
SRC = RT_ROOT / "src"
OUT = HERE / "SCRIPT_CENSUS.md"

# Role → (description, path/name predicates). First match wins.
ROLE_RULES: list[tuple[str, str, list[re.Pattern[str]]]] = [
    (
        "Preflight / live-gate",
        "worklist, cost gate, root status, probes",
        [
            re.compile(r"(verb_worklist|nominals_worklist|root_window_status|perf_preflight|freq_route|prompt_rule_audit|probe_log|h963_c4_gate0)"),
            re.compile(r"_pilot_gen_merged"),
        ],
    ),
    (
        "Harness + headless execution",
        "manifest v2, coordinator, headless worker, requeue harness",
        [
            re.compile(r"(gen_opt_harness2|headless_worker|bounded_staged_run|bounded_supervisor|coordinator|max_account_orchestrator|requeue_from_audit|autosplit_requeue|execution_contract|cohort_engine)"),
        ],
    ),
    (
        "Audit gates",
        "deterministic acceptance",
        [
            re.compile(r"(audit_window|stage2_pregate|audit_coverage|audit_sense|audit_root|nws_split|ru_coverage|tnmask|german_residue|layer_presence|validate_)"),
        ],
    ),
    (
        "Promote / store",
        "store write + lock",
        [
            re.compile(r"(promote_final|promote_en|promote_lock|promotion_receipt|save_and_audit)"),
        ],
    ),
    (
        "Translation memory",
        "TM build/grade/export",
        [
            re.compile(r"(translation_memory|tm_grade|tm_align|build_tmx|build_l0|ingest_oral|build_oral)"),
        ],
    ),
    (
        "Instrumentation",
        "ledgers, dashboard, parity, harvest",
        [
            re.compile(r"(check_launch_ledger|harvest_launch|classify_run|parse_workflow|dashboard|lang_parity|pipeline_version|layer_versions|watch_upstream|failure_capture|economy_ledger|run_observability|script_census|evolution_stats)"),
        ],
    ),
    (
        "Selftests",
        "fixture / unit gates",
        [
            re.compile(r"selftest|_test\.py$"),
            re.compile(r"window_selftest|windows100_selftest"),
        ],
    ),
    (
        "Release / edition / site",
        "print gates, reglue, article site, export",
        [
            re.compile(r"(preflight_remaining|release_readiness|make_edition|build_reglue|build_article_site|export_interop|export_lod|export_mdf)"),
        ],
    ),
    (
        "Gold / human review",
        "gold samples, review sheets, editorial apply",
        [
            re.compile(r"(gold_|fidelity_sample|build_h180|apply_editorial|review_sheet|trilingual_sample)"),
        ],
    ),
    (
        "Source / corpus builders",
        "harvest, mask, lexicon, relationships",
        [
            re.compile(r"(build_src|build_corpus|mine_running|build_glossar|corpus_gate|pwg_mask|dict_merge|build_dcs|build_learner|build_relationships|government_census)"),
        ],
    ),
    (
        "Renou / grammar layers",
        "annotation + grammar data",
        [
            re.compile(r"(renou|annotate_|whitney_grammar|nominal_grammar|reverse_index|mw_compounds)"),
        ],
    ),
    (
        "Fan-out guard",
        "sanctioned multi-agent dispatch only",
        [re.compile(r"synth_dispatch")],
    ),
]

SKIP_DIR_PARTS = {
    "archive",
    "nws",
    "fixtures",
    "input",
    "output",
    "lexical_cores",
    "dashboard",
    "eval",
    "h1209",
    "h1447",
    "__pycache__",
    "translate",
    "root_translate",
    "upstream_changes",
}


def classify(rel: str) -> str:
    name = Path(rel).name
    for role, _desc, pats in ROLE_RULES:
        for p in pats:
            if p.search(name) or p.search(rel.replace("\\", "/")):
                return role
    if name.startswith("_") or re.search(r"h\d{3,4}", name, re.I):
        return "One-offs / dated helpers"
    return "Other / untagged"


def collect() -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    roots = [SRC]
    root_save = RT_ROOT / "save_and_audit.py"
    if root_save.is_file():
        buckets[classify("save_and_audit.py")].append("save_and_audit.py")

    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.py")):
            rel = path.relative_to(RT_ROOT).as_posix()
            parts = set(Path(rel).parts)
            if parts & SKIP_DIR_PARTS:
                continue
            if "archive" in Path(rel).parts:
                continue
            buckets[classify(rel)].append(rel)
    return buckets


def render(buckets: dict[str, list[str]]) -> str:
    today = dt.date.today().strftime("%d-%m-%Y")
    total = sum(len(v) for v in buckets.values())
    lines = [
        "# RussianTranslation script census (generated)",
        "",
        f"_Created: {today} · Last updated: {today}_",
        "",
        "Auto-generated by [`script_census.py`](script_census.py). "
        "Do not hand-edit — re-run the generator. Role tags are "
        "heuristic (first-match); entry points for production stay bold "
        "in the deep manual, not here.",
        "",
        f"**As of {today}: {total} Python files** under `src/` (+ root "
        "`save_and_audit.py`), excluding archive/fixtures/nws bulk trees.",
        "",
        "```powershell",
        "python src\\pilot\\script_census.py",
        "python src\\pilot\\script_census.py --check",
        "```",
        "",
    ]
    # Stable role order from ROLE_RULES then leftovers
    order = [r[0] for r in ROLE_RULES] + ["One-offs / dated helpers", "Other / untagged"]
    seen = set()
    for role in order:
        if role not in buckets or role in seen:
            continue
        seen.add(role)
        files = sorted(buckets[role])
        desc = next((d for r, d, _ in ROLE_RULES if r == role), "")
        lines.append(f"## {role} ({len(files)})")
        if desc:
            lines.append("")
            lines.append(desc)
        lines.append("")
        for f in files:
            lines.append(f"- `{f}`")
        lines.append("")
    for role, files in sorted(buckets.items()):
        if role in seen:
            continue
        lines.append(f"## {role} ({len(files)})")
        lines.append("")
        for f in sorted(files):
            lines.append(f"- `{f}`")
        lines.append("")
    lines.append("_Auto-generated by script_census.py._")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if SCRIPT_CENSUS.md differs from a fresh emit",
    )
    ap.add_argument(
        "--stdout",
        action="store_true",
        help="print markdown to stdout instead of writing",
    )
    args = ap.parse_args()
    text = render(collect())
    if args.stdout:
        sys.stdout.write(text)
        return 0
    if args.check:
        if not OUT.is_file():
            print(f"MISSING {OUT}", file=sys.stderr)
            return 1
        old = OUT.read_text(encoding="utf-8")
        # Compare body without the date lines so --check is day-stable
        def strip_dates(s: str) -> str:
            return re.sub(
                r"_Created: .*? · Last updated: .*?_",
                "_Created: DATE · Last updated: DATE_",
                s,
            ).replace(
                re.search(r"\*\*As of \d{2}-\d{2}-\d{4}:", s).group(0)
                if re.search(r"\*\*As of \d{2}-\d{2}-\d{4}:", s)
                else "",
                "**As of DATE:",
            ) if False else re.sub(
                r"\*\*As of \d{2}-\d{2}-\d{4}:",
                "**As of DATE:",
                re.sub(
                    r"_Created: .*? · Last updated: .*?_",
                    "_Created: DATE · Last updated: DATE_",
                    s,
                ),
            )

        if strip_dates(old) != strip_dates(text):
            print(f"DRIFT {OUT} — re-run: python src/pilot/script_census.py", file=sys.stderr)
            return 1
        print(f"OK {OUT} matches generator (dates ignored)")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
