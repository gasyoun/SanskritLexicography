#!/usr/bin/env python
r"""h4342_requeue_sanloss.py — H4342 (e) / H4530: requeue the stuck SAN-LOSS store rows so
the daily spotcheck stops re-freezing the pc lane.

Surgical, single-purpose script (models `lane_guard.py`'s `revert_windows()`, scoped to
named subcards instead of a promotion day). Quarantines the offending rows with a full
backup, rewrites the rest through the house locked/atomic store writer, and appends a
requeue worklist — the ledgered shape `lane_guard` already uses.

  python src/pilot/h4342_fixes/h4342_requeue_sanloss.py              # dry-run (default)
  python src/pilot/h4342_fixes/h4342_requeue_sanloss.py --execute    # writes the store

H4530 (11-09-2026) fixed three defects in the H4342 draft, all of the H255/H3658 class:

1. ``SRC`` was hardcoded to the H4342 session's own worktree
   (``SanskritLexicography-h4342-27494``), which no longer exists — the script could not
   import at all from any other checkout. Paths now resolve from ``__file__``.
2. ``STORE`` was hardcoded to ``pwg-ru-data/tm/pwg_ru_translated.jsonl`` — the **mirror**,
   not the canonical store. A pre-H4530 run on 08-09 removed the three rows from the mirror
   while the canonical ``RussianTranslation/src/pwg_ru_translated.jsonl`` kept them, so
   ``audit_store_gates.py`` still reported ``hard_flagged_rows=3`` and the spotcheck kept
   re-freezing. Resolution is now ``store_path.canonical_store`` / ``canonical_data_repo``,
   exactly what ``promote_final_cards.py`` and ``audit_store_gates.py`` use.
3. The quarantine/requeue filenames carried a frozen ``DATE_TAG``, so a second run silently
   overwrote the first run's evidence. The tag now defaults to today, is overridable, and an
   existing quarantine file is refused rather than clobbered.

Restore (documented, reversible) — the quarantine file is a plain JSONL of the removed rows:

  python src/pilot/h4342_fixes/h4342_requeue_sanloss.py --restore <quarantine.jsonl> --execute
"""
import argparse
import datetime
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(HERE)
SRC = os.path.dirname(PILOT)
for _p in (SRC, PILOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import markup_fidelity_gates as mfg                                  # noqa: E402
import promote_final_cards as pfc                                    # noqa: E402
from store_path import canonical_data_repo, canonical_store          # noqa: E402
from store_write import locked_store_rewrite                         # noqa: E402

DEFAULT_STORE = canonical_store(os.path.join(SRC, "pwg_ru_translated.jsonl"))
DEFAULT_GATELOGS = os.path.join(canonical_data_repo(SRC), "gatelogs")

TARGET_SUBCARDS = {"m_a~~h0_zz_pw03", "pat~~h0_zz_pw00", "asvatantra~~h0_zz_pw"}


def read_rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def find_sanloss_hits(rows, targets):
    """(index, row, flags) for every target subcard whose real span gate fires SAN-LOSS.

    Same gate + thresholds as `audit_store_gates.py` and
    `spot_check_daily.store_san_loss_scan` (`markup_span_flags(..., check_ab=False)`),
    never a marker grep — FINDINGS §589.
    """
    hits = []
    for i, row in enumerate(rows):
        if row.get("subcard") not in targets:
            continue
        de, ru = row.get("de") or "", row.get("ru") or ""
        flags = [fl for fl in mfg.markup_span_flags(de, ru, check_ab=False)
                 if fl.startswith("SAN-LOSS")]
        if flags:
            hits.append((i, row, flags))
    return hits


def do_restore(args):
    quarantined = read_rows(args.restore)
    rows = read_rows(args.store)
    have = {(r.get("subcard"), r.get("sense_tag")) for r in rows}
    back = [r for r in quarantined if (r.get("subcard"), r.get("sense_tag")) not in have]
    print("restore: quarantine holds %d row(s), %d not currently in the store"
          % (len(quarantined), len(back)))
    for row in back:
        print("  + %s / %r" % (row.get("subcard"), row.get("sense_tag")))
    if not back:
        print("nothing to restore")
        return 0
    if not args.execute:
        print("DRY-RUN: would append %d row(s) to %s" % (len(back), args.store))
        return 0
    backup = locked_store_rewrite(args.store, rows + back, tag="h4342restore")
    print("RESTORED: %d row(s) (backup=%s, store now %d rows)"
          % (len(back), backup, len(rows) + len(back)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="requeue the stuck SAN-LOSS store rows (H4342 item e / H4530)")
    ap.add_argument("--store", default=DEFAULT_STORE,
                    help="canonical store to repair (default: %(default)s)")
    ap.add_argument("--gatelogs", default=DEFAULT_GATELOGS,
                    help="gatelogs dir for the quarantine + requeue worklist")
    ap.add_argument("--date-tag",
                    default="h4342-" + datetime.date.today().strftime("%Y%m%d"),
                    help="tag stamped into the quarantine/requeue filenames "
                         "(default: %(default)s)")
    ap.add_argument("--subcards", default=",".join(sorted(TARGET_SUBCARDS)),
                    help="comma-separated target subcards (default: the three H4342 rows)")
    ap.add_argument("--restore", metavar="QUARANTINE_JSONL",
                    help="put a quarantine file's rows back into the store (reversal path)")
    ap.add_argument("--execute", action="store_true",
                    help="actually write the store (default is dry-run)")
    args = ap.parse_args(argv)

    print("store:    %s" % args.store)
    print("gatelogs: %s" % args.gatelogs)
    if args.restore:
        return do_restore(args)

    targets = {s.strip() for s in args.subcards.split(",") if s.strip()}
    rows = read_rows(args.store)
    hits = find_sanloss_hits(rows, targets)
    print("found %d SAN-LOSS hit(s) among %d target subcard(s) in %d store rows"
          % (len(hits), len(targets), len(rows)))
    for i, row, flags in hits:
        touched = pfc.human_touched(row)
        print("  idx=%d subcard=%s sense_tag=%r flags=%s human_touched=%s"
              % (i, row.get("subcard"), row.get("sense_tag"), flags, touched))
        if touched:
            raise SystemExit("REFUSE: row %s is human-touched -- do not remove"
                             % row.get("subcard"))
    if not hits:
        print("nothing to do")
        return 0

    remove_idx = {i for i, _row, _flags in hits}
    removed = [row for i, row in enumerate(rows) if i in remove_idx]
    kept = [row for i, row in enumerate(rows) if i not in remove_idx]

    quarantine_path = os.path.join(
        args.gatelogs, "h4342_sanloss_requeue_%s.quarantine.jsonl" % args.date_tag)
    requeue_path = os.path.join(
        args.gatelogs, "h4342_sanloss_requeue_%s.requeue.keys.txt" % args.date_tag)

    if not args.execute:
        print("DRY-RUN: would remove %d row(s) (%d -> %d), quarantine -> %s, requeue -> %s"
              % (len(removed), len(rows), len(kept), quarantine_path, requeue_path))
        return 0
    if os.path.exists(quarantine_path):
        raise SystemExit("REFUSE: %s already exists -- pass a fresh --date-tag rather than "
                         "overwriting an earlier run's evidence" % quarantine_path)

    os.makedirs(args.gatelogs, exist_ok=True)
    with open(quarantine_path, "w", encoding="utf-8", newline="\n") as f:
        for row in removed:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(requeue_path, "w", encoding="utf-8", newline="\n") as f:
        for row in removed:
            f.write(row.get("subcard") + "\n")
    backup = locked_store_rewrite(args.store, kept, tag="h4342sanloss")

    print("EXECUTED: removed %d row(s) (backup=%s, quarantine=%s, requeue=%s), "
          "store now %d rows"
          % (len(removed), backup, quarantine_path, requeue_path, len(kept)))
    print("REVERSIBLE: python src/pilot/h4342_fixes/h4342_requeue_sanloss.py "
          "--restore %s --execute" % quarantine_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
