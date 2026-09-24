#!/usr/bin/env python3
"""check_prose_number_drift.py — refuse a stale hand-copied number in prose (H5421).

_Created: 24-09-2026 · Last updated: 24-09-2026_

Self-contained per-repo twin of Uprava's central checker
(https://github.com/gasyoun/Uprava/blob/main/tools/prose_number_drift.py, which
is the actual fix/log engine and the one that reads/writes
data/prose_drift_log.tsv). This script exists only so pre-commit and this
repo's own CI can catch a *new* stale copy of a pinned number landing in a
living doc, without needing network access to Uprava (a private repo) at
hook/CI time. Claims: scripts/prose_number_drift_claims.json (id, current
display value, retired stale forms, paths this repo never auto-corrects —
CHANGELOG.md and any file under changelog_queue/, matching Uprava's MG Q2
ruling that changelogs are frozen narrative, drift only logged centrally).

Usage:
    python scripts/check_prose_number_drift.py --check [PATH ...]
    python scripts/check_prose_number_drift.py --fix   [PATH ...]

No PATH given -> scans the whole repo (CI use). PATHs given (pre-commit passes
staged *.md files) -> scans only those.

Exit 0 = no stale value found (or all fixed) · 1 = stale value(s) found in --check · 2 = usage/IO error.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CLAIMS_PATH = ROOT / "scripts" / "prose_number_drift_claims.json"
SCAN_EXTS = {".md", ".txt", ".tex"}
SKIP_DIR_NAMES = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "vendor"}


def load_claims() -> list[dict]:
    return json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))["claims"]


def build_regex(claim: dict) -> re.Pattern:
    values = sorted({*claim["stale_values"], claim["display"]}, key=len, reverse=True)
    alts = "|".join(re.escape(v) for v in values)
    return re.compile(rf"(?<![\d,])(?:{alts})(?![\d,])")


def is_allowed(rel_posix: str, allow_globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel_posix, pat) for pat in allow_globs)


def candidate_files(explicit: list[str]) -> list[Path]:
    if explicit:
        return [Path(p) for p in explicit if Path(p).suffix.lower() in SCAN_EXTS]
    out = []
    for p in ROOT.rglob("*"):
        if p.is_dir() or p.suffix.lower() not in SCAN_EXTS:
            continue
        if any(part in SKIP_DIR_NAMES for part in p.relative_to(ROOT).parts[:-1]):
            continue
        out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args(argv)
    if not args.check and not args.fix:
        args.check = True

    try:
        claims = load_claims()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read {CLAIMS_PATH}: {exc}", file=sys.stderr)
        return 2

    hits = []
    for path in candidate_files(args.paths):
        if not path.exists():
            continue
        try:
            rel_posix = path.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        changed = False
        for claim in claims:
            if is_allowed(rel_posix, claim.get("allow_paths", [])):
                continue
            regex = build_regex(claim)
            for i, line in enumerate(text.split("\n"), start=1):
                for m in regex.finditer(line):
                    old = m.group(0)
                    if old == claim["display"]:
                        continue
                    hits.append((rel_posix, i, old, claim["display"]))
            if args.fix:
                new_text = regex.sub(claim["display"], text)
                if new_text != text:
                    text = new_text
                    changed = True
        if changed:
            path.write_text(text, encoding="utf-8")

    if hits:
        for rel_posix, i, old, display in hits:
            verb = "fixed" if args.fix else "STALE"
            print(f"{verb}: {rel_posix}:{i}  {old!r} -> {display!r}")
    if args.check and hits:
        print(f"\n{len(hits)} stale prose-number hit(s). Fix with --fix, or see H5421.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
