#!/usr/bin/env python3
"""H5468 — seed the sheet-assignment ledger with the batch 1 that was already published.

Sheet 1 (https://gasyoun.github.io/vote/sheets/pwg_ru_nkrya_flags_b01_24-09-2026.html)
was built by H5262 from the 54-flag H5262_flags.json at commit cdaba35cd — the first ten
rows of that file, in its order. The drain has since raised the flag list to 136, and
because new flags interleave by severity the positional slice no longer reproduces those
ten lemmas. Seeding from the committed artifact, not from today's list, is the only way
to keep the published sheet's card set true.

Run once; `build_h5262_nkrya_flag_sheet.py` maintains the ledger from then on.

  python src/h5468_seed_sheet_assignments.py [--rev cdaba35cd]
"""

import argparse
import io
import json
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_h5262_nkrya_flag_sheet as B  # noqa: E402

PUBLISHED_REV = "cdaba35cd"
PER_SHEET = 10


def sheet1_lemmas(rev=PUBLISHED_REV, repo=None):
    """The ten lemmas the published sheet 1 actually carries."""
    out = subprocess.run(
        ["git", "show", "%s:RussianTranslation/reports/H5262_flags.json" % rev],
        capture_output=True, cwd=repo or os.path.dirname(HERE), check=True)
    old = json.loads(out.stdout.decode("utf-8"))
    return [r["lemma"] for r in old["flagged"][:PER_SHEET]]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rev", default=PUBLISHED_REV)
    ap.add_argument("--assignments", default=B.ASSIGNMENTS)
    a = ap.parse_args(argv)

    if os.path.exists(a.assignments):
        raise SystemExit("%s already exists — seeding is a one-time step, refusing to "
                         "overwrite an append-only ledger." % a.assignments)

    lemmas = sheet1_lemmas(a.rev)
    doc = {"handoff": "H5468", "per_sheet": PER_SHEET, "note": B.ASSIGN_NOTE,
           "seeded_from": "%s:RussianTranslation/reports/H5262_flags.json" % a.rev,
           "assigned": {lemma: 1 for lemma in lemmas}}
    doc["lemmas_assigned"] = len(doc["assigned"])
    doc["batches"] = 1
    B.save_assignments(doc, a.assignments)
    print("seeded batch 1 with %d published lemmas -> %s" % (len(lemmas), a.assignments))
    for lemma in lemmas:
        print("  %s" % lemma)
    return 0


if __name__ == "__main__":
    sys.exit(main())
