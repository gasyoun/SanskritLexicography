#!/usr/bin/env python3
"""Audit every Repo cell of FEATURES_INDEX.md §II against the live GitHub orgs.

Why this exists (H1722, 27-07-2026): the H1475 consolidation spike found three
wrong cells -- PUI and IEG marked "csl-orig only" though both repos exist, and
PD linking a Cologne scan where a repo link belongs. That column is not
decorative: the "csl-orig only" marker is what the count of repo-less
dictionaries is derived from, so a wrong cell silently moves a published figure.

Two checks per row:
  * a cell linking github.com/<org>/<repo> -> that repo must exist;
  * a cell claiming "csl-orig only"        -> no repo named for that code may exist.

Exit 0 when every cell is consistent, 1 otherwise (usable as a CI gate).
Requires the `gh` CLI, authenticated with read access to both orgs.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ORGS = ("sanskrit-lexicon", "gasyoun")
INDEX = Path(__file__).resolve().parent.parent / "FEATURES_INDEX.md"
HEADER = "| Code | Dictionary |"
REPO_COL = 6


def live_repos():
    """Full name set across both orgs. Fails loudly -- an empty listing would
    otherwise read as 'every repo is missing' and flag all 44 rows."""
    names = set()
    for org in ORGS:
        proc = subprocess.run(
            ["gh", "repo", "list", org, "--limit", "300", "--json", "name"],
            capture_output=True, text=True, encoding="utf-8",
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            raise SystemExit(
                f"gh repo list {org} returned nothing (rc={proc.returncode}): "
                f"{proc.stderr.strip()[:200]}"
            )
        names |= {f"{org}/{r['name']}" for r in json.loads(proc.stdout)}
    return {n.lower(): n for n in names}


def rows(text):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(HEADER))
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            return
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) > REPO_COL:
            yield cells[0], cells[REPO_COL]


def main():
    repos = live_repos()
    defects = []
    checked = 0

    for code, cell in rows(INDEX.read_text(encoding="utf-8")):
        checked += 1
        linked = re.search(r"github\.com/([\w.-]+/[\w.-]+)", cell)
        if linked:
            if linked.group(1).lower() not in repos:
                defects.append(f"{code}: links {linked.group(1)}, which does not exist")
        elif "csl-orig only" in cell:
            hit = repos.get(f"sanskrit-lexicon/{code.lower()}")
            if hit:
                defects.append(f'{code}: says "csl-orig only" but {hit} exists')
        else:
            hit = repos.get(f"sanskrit-lexicon/{code.lower()}")
            if hit:
                defects.append(f"{code}: no repo link, but {hit} exists")

    for defect in defects:
        print(f"DEFECT  {defect}")
    print(f"{checked} Repo cells checked, {len(defects)} defective")
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())
