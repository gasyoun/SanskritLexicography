#!/usr/bin/env python3
"""H5468 — rewrite reports/H5262_sheets.json from the sheets actually on disk.

One row per built sheet: batch, card count, the hub URL it will carry, and the local
HTML the hub commit copies. Derived from review/locks/ (the review-binding lock is what
proves a sheet was really built) joined with the assignment ledger, so the index can
never claim a sheet that does not exist.

  python src/h5468_update_sheets_index.py
"""

import argparse
import glob
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REVIEW = os.path.join(REPO, "review")
LOCKS = os.path.join(REVIEW, "locks")
SHEETS = os.path.join(REPO, "reports", "H5262_sheets.json")
ASSIGNMENTS = os.path.join(REPO, "reports", "H5262_sheet_assignments.json")

LOCK_RE = re.compile(r"^h5262-nkrya-flags-b(\d{2})-(\d{4}-\d{2}-\d{2})\.lock\.json$")
# The hub filename convention sheet 1 established (DD-MM-YYYY, not the sheet_id's ISO).
HUB = "https://gasyoun.github.io/vote/sheets/pwg_ru_nkrya_flags_b%02d_%s.html"

NOTE = (
    "Sheet 1 is committed on gasyoun.github.io branch h5262-nkrya-flags-b01 (b589c33) on the "
    "Mac with its vote-hub index row; sheets 2-14 are prepared by H5468 in this repo's "
    "review/ and still need their hub commit. The hub's pre-push guard reserves the "
    "publishing push to a human (ALLOW_PUBLISH_PUSH), so every URL below goes live only "
    "when MG pushes. Publish-safety: PWG-RU glosses are this project's own translation "
    "output, PWG German is 19th-century public domain, NKRYa concordance sentences are "
    "deliberately omitted, and a scan found no e-mails, keys or local paths."
)


def hub_date(iso):
    y, m, d = iso.split("-")
    return "%s-%s-%s" % (d, m, y)


def rows():
    assigned = {}
    if os.path.exists(ASSIGNMENTS):
        with io.open(ASSIGNMENTS, encoding="utf-8") as fh:
            assigned = json.load(fh).get("assigned", {})
    per_batch = {}
    for lemma, batch in assigned.items():
        per_batch.setdefault(batch, []).append(lemma)

    out = []
    for path in sorted(glob.glob(os.path.join(LOCKS, "h5262-nkrya-flags-b*.lock.json"))):
        m = LOCK_RE.match(os.path.basename(path))
        if not m:
            continue
        batch, iso = int(m.group(1)), m.group(2)
        with io.open(path, encoding="utf-8") as fh:
            lock = json.load(fh)
        ids = lock.get("card_ids") or lock.get("ids") or []
        html = glob.glob(os.path.join(
            REVIEW, "sanskritlexicography-h5262-nkrya-flags-b%02d_*.html" % batch))
        out.append({
            "batch": batch,
            "cards": len(ids) or len(per_batch.get(batch, [])),
            "url": HUB % (batch, hub_date(iso)),
            "local_html": ("RussianTranslation/review/" + os.path.basename(html[0]))
                          if html else None,
            "sheet_id": lock.get("sheet_id") or os.path.basename(path)[:-len(".lock.json")],
            "published": batch == 1,
        })
    out.sort(key=lambda r: (r["batch"], r["sheet_id"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=SHEETS)
    a = ap.parse_args(argv)

    sheets = rows()
    doc = {"handoff": "H5468", "sheets": sheets,
           "sheets_total": len(sheets),
           "cards_total": sum(r["cards"] for r in sheets),
           "note": NOTE}
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("wrote %d sheet row(s), %d cards -> %s"
          % (len(sheets), doc["cards_total"], a.out))
    for r in sheets:
        print("  b%02d  %2d cards  %s%s"
              % (r["batch"], r["cards"], r["url"],
                 "" if r["published"] else "   (hub commit pending)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
