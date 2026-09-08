"""H4342 (e): requeue the three stuck SAN-LOSS store rows so the daily spotcheck
stops re-freezing the pc lane. Surgical, single-purpose, one-shot script (models
lane_guard.py's revert_windows(), scoped to named subcards instead of a promotion
day). Backs up the store, quarantines the offending rows, atomic-writes the rest,
and appends a requeue worklist -- exactly the ledgered shape lane_guard already uses.
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SRC = r"C:\Users\user\Documents\GitHub\SanskritLexicography-h4342-27494\RussianTranslation\src"
PILOT = os.path.join(SRC, "pilot")
for p in (SRC, PILOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import markup_fidelity_gates as mfg          # noqa: E402
import promote_final_cards as pfc            # noqa: E402
from promote_lock import PromoteClaim        # noqa: E402

STORE = r"C:\Users\user\Documents\GitHub\pwg-ru-data\tm\pwg_ru_translated.jsonl"
GATELOGS = r"C:\Users\user\Documents\GitHub\pwg-ru-data\gatelogs"
DATE_TAG = "h4342-20260908"

TARGET_SUBCARDS = {"m_a~~h0_zz_pw03", "pat~~h0_zz_pw00", "asvatantra~~h0_zz_pw"}

EXECUTE = "--execute" in sys.argv


def find_sanloss_hits(rows):
    hits = []
    for i, row in enumerate(rows):
        sub = row.get("subcard")
        if sub not in TARGET_SUBCARDS:
            continue
        de, ru = row.get("de") or "", row.get("ru") or ""
        flags = [fl for fl in mfg.markup_span_flags(de, ru, check_ab=False)
                 if fl.startswith("SAN-LOSS")]
        if flags:
            hits.append((i, row, flags))
    return hits


def main():
    with open(STORE, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    hits = find_sanloss_hits(rows)
    print("found %d SAN-LOSS hits among target subcards" % len(hits))
    for i, row, flags in hits:
        touched = pfc.human_touched(row)
        print("  idx=%d subcard=%s sense_tag=%r flags=%s human_touched=%s"
              % (i, row.get("subcard"), row.get("sense_tag"), flags, touched))
        if touched:
            raise SystemExit("REFUSE: row %s is human-touched -- do not remove" % row.get("subcard"))

    if not hits:
        print("nothing to do")
        return 0

    remove_idx = {i for i, _row, _flags in hits}
    removed = [row for i, row in enumerate(rows) if i in remove_idx]
    kept = [row for i, row in enumerate(rows) if i not in remove_idx]

    quarantine_path = os.path.join(GATELOGS, "h4342_sanloss_requeue_%s.quarantine.jsonl" % DATE_TAG)
    requeue_path = os.path.join(GATELOGS, "h4342_sanloss_requeue_%s.requeue.keys.txt" % DATE_TAG)

    if not EXECUTE:
        print("DRY-RUN: would remove %d rows, quarantine -> %s, requeue -> %s"
              % (len(removed), quarantine_path, requeue_path))
        return 0

    with PromoteClaim(STORE):
        backup = pfc._backup_path(STORE, merge=True)
        pfc._fsynced_backup(STORE, backup)
        os.makedirs(GATELOGS, exist_ok=True)
        with open(quarantine_path, "w", encoding="utf-8", newline="\n") as f:
            for row in removed:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        with open(requeue_path, "w", encoding="utf-8", newline="\n") as f:
            for row in removed:
                f.write(row.get("subcard") + "\n")
        pfc._atomic_write_rows(STORE, kept)

    print("EXECUTED: removed %d rows (backup=%s, quarantine=%s, requeue=%s), store now %d rows"
          % (len(removed), backup, quarantine_path, requeue_path, len(kept)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
